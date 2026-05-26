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
from collections import defaultdict, deque
from pathlib import Path
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
# Spec DAG + topological scheduling                                     #
# --------------------------------------------------------------------- #

def read_spec_dependencies(specs_root: Path,
                            candidate_specs: List[str]) -> Dict[str, List[str]]:
    """Read `depends_on:` from YAML frontmatter of each candidate spec
    file. Returns {spec_id: [dependency_spec_ids]}.

    Specs without `depends_on:` get an empty dependency list. Missing
    spec files are skipped silently (the caller's candidate list is
    authoritative).

    Format expected in spec frontmatter:
      ---
      doc_kind: jam-spec
      depends_on:
        - other-spec-id
        - another-spec-id
      ---
    """
    deps: Dict[str, List[str]] = {}
    for spec_id in candidate_specs:
        path = specs_root / f"{spec_id}.md"
        if not path.exists():
            deps[spec_id] = []
            continue
        text = path.read_text()
        if not text.startswith("---"):
            deps[spec_id] = []
            continue
        # Extract the frontmatter block — between first --- and second ---
        parts = text.split("---", 2)
        if len(parts) < 3:
            deps[spec_id] = []
            continue
        frontmatter = parts[1]
        # Naive YAML parsing for the depends_on: array.
        # We don't want to add a PyYAML dependency.
        dep_list: List[str] = []
        in_depends_block = False
        for line in frontmatter.splitlines():
            stripped = line.strip()
            if stripped.startswith("depends_on:"):
                # Inline array: depends_on: [a, b]
                inline = stripped[len("depends_on:"):].strip()
                if inline.startswith("["):
                    inner = inline.strip("[]")
                    for item in inner.split(","):
                        item = item.strip().strip("'\"")
                        if item:
                            dep_list.append(item)
                else:
                    in_depends_block = True
                continue
            if in_depends_block:
                if stripped.startswith("- "):
                    dep_list.append(stripped[2:].strip().strip("'\""))
                elif stripped and not line.startswith(" "):
                    # Frontmatter key with no leading space → end of block
                    in_depends_block = False
        deps[spec_id] = dep_list
    return deps


def topological_levels(deps: Dict[str, List[str]]) -> List[List[str]]:
    """Kahn's algorithm. Returns a list of "levels" — specs at level 0
    have no deps inside the candidate set; level 1 specs depend only on
    level 0; etc. Cycles are detected and the remaining specs are
    appended as a final "ungated" level (with a warning recorded by
    the caller via the returned cycle_specs set in detail mode).

    Round-robin within each level is the caller's responsibility.
    """
    in_degree = {s: 0 for s in deps}
    edges_in: Dict[str, Set[str]] = defaultdict(set)
    edges_out: Dict[str, Set[str]] = defaultdict(set)
    for spec, dep_list in deps.items():
        for dep in dep_list:
            if dep in in_degree:  # only count deps that are in candidates
                edges_out[dep].add(spec)
                edges_in[spec].add(dep)
                in_degree[spec] += 1
    levels: List[List[str]] = []
    remaining = set(deps.keys())
    current_level = sorted(s for s in remaining if in_degree[s] == 0)
    while current_level:
        levels.append(current_level)
        next_level_set = set()
        for s in current_level:
            remaining.discard(s)
            for downstream in edges_out.get(s, []):
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    next_level_set.add(downstream)
        current_level = sorted(next_level_set)
    if remaining:
        # Cycle (or dep on something outside candidates). Append the
        # rest as a final level so they still get attempted.
        levels.append(sorted(remaining))
    return levels


class DAGScheduler:
    """Wraps a topological ordering of specs across the (spec × model)
    schedule. When a spec's deps haven't all been published yet, the
    scheduler defers attempting it.

    "Published" status tracked via the Planner's update mechanism:
    when a (spec, _) round produces frozen-and-published, the spec is
    marked published; downstream specs unlock for the next round.
    """

    def __init__(self, specs: List[str], models: List[str],
                  deps: Dict[str, List[str]]):
        self.specs = list(specs)
        self.models = list(models)
        self.deps = {s: list(deps.get(s, [])) for s in specs}
        self.published: Set[str] = set()
        # Stable cursor for round-robin within an unlocked subset
        self._cursor = 0

    def mark_published(self, spec_id: str) -> None:
        self.published.add(spec_id)

    def is_unlocked(self, spec_id: str) -> bool:
        for dep in self.deps.get(spec_id, []):
            if dep in self.specs and dep not in self.published:
                return False
        return True

    def unlocked_pairs(self,
                        demoted_pairs: Set[Tuple[str, str]],
                        demoted_specs: Set[str],
                        demoted_models: Set[str]) -> List[Tuple[str, str]]:
        out = []
        for spec_id in self.specs:
            if spec_id in demoted_specs:
                continue
            if not self.is_unlocked(spec_id):
                continue
            for model in self.models:
                if model in demoted_models:
                    continue
                pair = (spec_id, model)
                if pair in demoted_pairs:
                    continue
                out.append(pair)
        return out


# Add factory + DAG-aware next_pair to Planner via monkey-patch — keeps
# the existing v0 unchanged + opt-in via constructor flag.

def _planner_init_with_dag(self, specs, models, consecutive_threshold=2,
                            dag_deps: Optional[Dict[str, List[str]]] = None):
    self.specs = list(specs)
    self.models = list(models)
    self.consecutive_threshold = consecutive_threshold
    self.demoted_pairs = set()
    self.demoted_specs = set()
    self.demoted_models = set()
    self.consecutive_non_publish = defaultdict(int)
    self.events = []
    self._cursor = 0
    # DAG support (opt-in; None preserves v0 behavior)
    self.dag = (
        DAGScheduler(specs, models, dag_deps) if dag_deps is not None
        else None
    )

Planner.__init__ = _planner_init_with_dag


def _planner_update_with_dag(self, round_record):
    spec_id = round_record.get("spec_id")
    model = round_record.get("model")
    outcome = round_record.get("outcome", "")
    if not spec_id or not model:
        return
    pair = (spec_id, model)
    kind = classify_outcome(outcome)
    if kind == "publish":
        if self.consecutive_non_publish[pair] > 0:
            self._record("counter_reset", pair=list(pair), outcome=outcome)
        self.consecutive_non_publish[pair] = 0
        # NEW: notify the DAG that this spec has produced a publishable
        # artifact — unlocks any downstream specs whose deps included
        # this spec.
        if self.dag is not None:
            was_already = spec_id in self.dag.published
            self.dag.mark_published(spec_id)
            if not was_already:
                self._record("dag_spec_published", spec_id=spec_id)
        return
    self.consecutive_non_publish[pair] += 1
    n = self.consecutive_non_publish[pair]
    if n >= self.consecutive_threshold and pair not in self.demoted_pairs:
        self.demoted_pairs.add(pair)
        self._record("pair_demoted", pair=list(pair),
                      consecutive_count=n, last_outcome=outcome)

Planner.update = _planner_update_with_dag


def _planner_next_pair_with_dag(self):
    """Pick next active pair. When DAG is enabled, picks from
    unlocked-only pool. When DAG is None, picks from full active pool
    (v0 behavior preserved).
    """
    if self.dag is not None:
        active = self.dag.unlocked_pairs(
            self.demoted_pairs, self.demoted_specs, self.demoted_models)
    else:
        active = self.active_pairs()
    if not active:
        return None
    pair = active[self._cursor % len(active)]
    self._cursor += 1
    return pair

Planner.next_pair = _planner_next_pair_with_dag


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
