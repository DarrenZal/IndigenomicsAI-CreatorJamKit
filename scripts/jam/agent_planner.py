#!/usr/bin/env python3
"""agent_planner.py — multi-agent-mesh-v0 Planner role (v0 scope).

The Planner consumes round outcomes + aggregator recommendations and
demotes (spec, model) pairs that consistently fail to publish. The
overnight_loop calls `planner.next_pair(...)` instead of raw cycling,
giving the loop adaptive scheduling instead of dumb round-robin.

v0 scope (per ~/.claude/plans/planner-role-v0-design.md):

  P1: spec×model affinity routing — after K consecutive non-publish
      outcomes for a pair, demote it. Pure state machine; no LLM call.

  P2: aggregator-recommendation consumption — parse the aggregator's
      "spec X has 0 publishes after N rounds" and "model Y published
      0 of N round(s)" patterns; demote globally.

v0.2 (deferred):
  - Composition-aware scheduling (P3) — prefer successor specs after
    a publish, per coordination-protocol composition_propose hints.
  - Cross-run persistence — v0 starts fresh each loop launch.
  - LLM-in-the-loop planning — v0 is pure state machine; v0.2 could
    add a model call to interpret aggregator output more flexibly.

Discipline:
  - Planner emits decisions, never executes external actions itself.
  - Demoted state lives in-process; no disk persistence in v0.
  - Operator can always override by restarting the loop with edited
    --specs / --models flags.
  - Refusals are not penalties — a refusal counts as non-publish but
    the Planner does NOT treat "doesn't fit yet" as a moral failing.
    It just observes that the (spec, model) pair didn't produce a
    publishable artifact tonight.
"""

import re
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple


# --------------------------------------------------------------------- #
# Outcome classification                                                #
# --------------------------------------------------------------------- #

PUBLISH_OUTCOMES = {"frozen-and-published"}
NON_PUBLISH_BUT_RECOVERABLE = {
    "doesnt-fit-yet-no-packet",
    "drafting-timeout",
    "witness-draft-failed",
    "witness-timeout",
    "publish-failed",
    "publish-timeout",
    "loop-error",
    "subprocess-timeout",
    "review-halted",
    "unknown",
    "no-results",
}
# Refusals are non-publish and meaningful — a Planner that just demotes
# refusing pairs effectively learns "this spec needs another model" or
# "this model refuses this kind of content".
REFUSAL_OUTCOME_PREFIXES = (
    "refused-by-gatekeeper",
    "refused-by-model",
    "offering-generation-failed",
)


def classify_outcome(outcome: str) -> str:
    """Return 'publish' | 'refusal' | 'non-publish'."""
    if not isinstance(outcome, str):
        return "non-publish"
    if outcome in PUBLISH_OUTCOMES:
        return "publish"
    for prefix in REFUSAL_OUTCOME_PREFIXES:
        if outcome.startswith(prefix):
            return "refusal"
    return "non-publish"


# --------------------------------------------------------------------- #
# Planner state machine                                                 #
# --------------------------------------------------------------------- #

class Planner:
    """Stateful scheduler. Consumes round records + aggregator output;
    decides which (spec, model) pair to attempt next.

    Constructor takes the full spec list + full model list; the Planner
    tracks which pairs have been demoted. A pair stays demoted for the
    rest of the run (in-process state).
    """

    def __init__(self, specs: List[str], models: List[str],
                  consecutive_threshold: int = 2):
        self.specs = list(specs)
        self.models = list(models)
        self.consecutive_threshold = consecutive_threshold

        # State
        self.demoted_pairs: Set[Tuple[str, str]] = set()
        self.demoted_specs: Set[str] = set()
        self.demoted_models: Set[str] = set()
        # (spec, model) -> int consecutive non-publish count
        self.consecutive_non_publish: Dict[Tuple[str, str], int] = defaultdict(int)

        # Audit trail — humans + aggregator can read this
        self.events: List[Dict[str, Any]] = []

        # Round-robin cursor across (spec × model) pairs
        self._cursor = 0

    # ----- audit ----- #

    def _record(self, event_type: str, **kwargs):
        self.events.append({
            "event": event_type,
            "demoted_pairs": [list(p) for p in sorted(self.demoted_pairs)],
            "demoted_specs": sorted(self.demoted_specs),
            "demoted_models": sorted(self.demoted_models),
            **kwargs,
        })

    # ----- state update ----- #

    def update(self, round_record: Dict[str, Any]) -> None:
        """Consume a finished-round record. Updates the consecutive
        non-publish counter; demotes the pair if threshold hit.
        """
        spec_id = round_record.get("spec_id")
        model = round_record.get("model")
        outcome = round_record.get("outcome", "")
        if not spec_id or not model:
            return
        pair = (spec_id, model)
        kind = classify_outcome(outcome)
        if kind == "publish":
            # Reset counter — a publish proves the pair is viable.
            if self.consecutive_non_publish[pair] > 0:
                self._record("counter_reset", pair=list(pair),
                              outcome=outcome)
            self.consecutive_non_publish[pair] = 0
            return

        # Both refusal AND non-publish bump the counter.
        self.consecutive_non_publish[pair] += 1
        n = self.consecutive_non_publish[pair]
        if n >= self.consecutive_threshold and pair not in self.demoted_pairs:
            self.demoted_pairs.add(pair)
            self._record("pair_demoted", pair=list(pair),
                          consecutive_count=n,
                          last_outcome=outcome)

    # ----- aggregator consumption (P2) ----- #

    # Patterns mirror what agent_aggregator.derive_recommendations emits.
    SPEC_ZERO_PATTERN = re.compile(
        r"Spec `([a-z0-9\-]+)` ran (\d+) time\(s\) and never reached publish",
    )
    MODEL_ZERO_PATTERN = re.compile(
        r"Model `([a-z0-9\-\.]+)` published 0 of (\d+) round\(s\)",
    )

    def consume_aggregator(self, recs_md_text: str) -> int:
        """Read the aggregator-recommendations.md text; extract
        machine-actionable items and apply them. Returns count of
        actions taken this call.
        """
        actions = 0
        if not isinstance(recs_md_text, str):
            return 0
        for m in self.SPEC_ZERO_PATTERN.finditer(recs_md_text):
            spec_id = m.group(1)
            attempts = int(m.group(2))
            if spec_id in self.specs and spec_id not in self.demoted_specs:
                self.demoted_specs.add(spec_id)
                self._record("spec_demoted_via_aggregator",
                              spec_id=spec_id, attempts=attempts)
                actions += 1
        for m in self.MODEL_ZERO_PATTERN.finditer(recs_md_text):
            model = m.group(1)
            attempts = int(m.group(2))
            if model in self.models and model not in self.demoted_models:
                self.demoted_models.add(model)
                self._record("model_demoted_via_aggregator",
                              model=model, attempts=attempts)
                actions += 1
        return actions

    # ----- scheduling ----- #

    def is_pair_active(self, pair: Tuple[str, str]) -> bool:
        spec_id, model = pair
        if spec_id in self.demoted_specs:
            return False
        if model in self.demoted_models:
            return False
        if pair in self.demoted_pairs:
            return False
        return True

    def active_pairs(self) -> List[Tuple[str, str]]:
        out = []
        for spec_id in self.specs:
            if spec_id in self.demoted_specs:
                continue
            for model in self.models:
                if model in self.demoted_models:
                    continue
                pair = (spec_id, model)
                if pair in self.demoted_pairs:
                    continue
                out.append(pair)
        return out

    def next_pair(self) -> Optional[Tuple[str, str]]:
        """Return the next (spec, model) to attempt, or None if no
        active pairs remain (loop should halt or pause).

        Uses a stable cursor across the active-pair list so picks
        cycle through diversity rather than always picking the first
        active pair.
        """
        active = self.active_pairs()
        if not active:
            return None
        pair = active[self._cursor % len(active)]
        self._cursor += 1
        return pair

    def status(self) -> Dict[str, Any]:
        return {
            "specs_total": len(self.specs),
            "specs_demoted": len(self.demoted_specs),
            "models_total": len(self.models),
            "models_demoted": len(self.demoted_models),
            "pairs_total": len(self.specs) * len(self.models),
            "pairs_demoted": len(self.demoted_pairs),
            "pairs_active": len(self.active_pairs()),
            "demoted_pairs": sorted([list(p) for p in self.demoted_pairs]),
            "demoted_specs": sorted(self.demoted_specs),
            "demoted_models": sorted(self.demoted_models),
        }


# --------------------------------------------------------------------- #
# Self-test                                                             #
# --------------------------------------------------------------------- #

if __name__ == "__main__":
    p = Planner(
        specs=["spec-a", "spec-b"],
        models=["model-x", "model-y"],
        consecutive_threshold=2,
    )
    print("initial:", p.status()["pairs_active"], "pairs active")

    p.update({"spec_id": "spec-a", "model": "model-x",
               "outcome": "refused-by-model: cultural"})
    p.update({"spec_id": "spec-a", "model": "model-x",
               "outcome": "refused-by-model: cultural"})
    print("after 2 consec refusals on (spec-a, model-x):",
           p.status()["pairs_active"], "pairs active; demoted:",
           p.status()["demoted_pairs"])

    p.update({"spec_id": "spec-a", "model": "model-y",
               "outcome": "frozen-and-published"})
    print("publish on (spec-a, model-y); cursor still rotates:")
    for _ in range(4):
        print("  next_pair:", p.next_pair())

    # Aggregator consumption test
    agg_text = (
        "1. Spec `spec-b` ran 3 time(s) and never reached publish. "
        "Outcomes: {'refused-by-model': 3}. Consider whether the spec body "
        "is structured in a way that consistently trips a refusal layer."
    )
    actions = p.consume_aggregator(agg_text)
    print(f"\naggregator consumption: {actions} action(s); status:")
    print(" ", p.status())
