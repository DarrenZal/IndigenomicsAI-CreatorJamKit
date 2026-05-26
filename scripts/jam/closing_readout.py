#!/usr/bin/env python3
"""closing_readout.py — render the kit's closing-witness-readout from
an overnight_loop persistent_root.

The kit already has a template at workshop/closing-witness-readout.md
with sections that map 1:1 to autonomous round outcomes:

  What Was Selected       → spec list (input)
  What Was Attempted      → rounds attempted (spec × model pairs)
  What Passed             → frozen-and-published outcomes
  What Was Partial        → review-halted + doesnt-fit-yet
  What Failed             → loop-error + subprocess-timeout
  What Was Refused        → refused-by-gatekeeper + refused-by-model
  What Was Not Run        → Planner-demoted pairs never attempted
  What Remains For Review → wall records + flagged checks

This script reads an overnight_loop persistent_root and produces the
populated readout. Output is operator-facing, not autonomous-published —
the operator reviews + edits before showing at the closing ceremony.

Usage:
  python3 scripts/jam/closing_readout.py render \\
      --persistent-root ~/overnight-jam-2026-05-26 \\
      --out ~/overnight-jam-2026-05-26/closing-witness-readout.md

Discipline:
  - Output carries the standard closing boundary (no legitimacy /
    authority / certification claim).
  - Reads from the loop's existing artifacts; does not invoke any LLM.
  - "What Was Not Run" lists Planner-demoted pairs from planner-events.json
    if present; otherwise marks the section as not-applicable.
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Persistent-root readers                                               #
# --------------------------------------------------------------------- #

def read_master_log(persistent_root: Path) -> List[Dict[str, Any]]:
    log_path = persistent_root / "overnight-master-log.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return entries


def read_planner_status(persistent_root: Path) -> Optional[Dict[str, Any]]:
    p = persistent_root / "planner-events.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError:
        return None


def collect_wall_records(persistent_root: Path) -> List[Dict[str, Any]]:
    """Walk <persistent_root>/wall/ for witness record files.
    Returns list of {file, spec_hint, timestamp_hint}."""
    wall_root = persistent_root / "wall"
    out = []
    if not wall_root.exists():
        return out
    for p in sorted(wall_root.rglob("*.md")):
        name = p.name
        # filename format from witness_append.py:
        # <YYYYMMDDTHHMMSS>-<team-id>-<hash>.md
        parts = name.split("-", 2)
        ts_hint = parts[0] if parts else ""
        spec_hint = ""
        # spec id usually appears in team-id (orchestrator-<spec>) +
        # in the filename tail
        for stem in [
            "witness-record-interop-profile",
            "claims-evidence-coherence-report",
            "commitment-pool-route-diagnostic",
            "dream-to-fulfillment-board",
            "receipt-wall-story-gallery",
            "flow-funding-frontier-map",
            "bioregional-mapping-layer-board",
            "spec-composer-bundle-board",
        ]:
            if stem in name:
                spec_hint = stem
                break
        out.append({
            "file": str(p),
            "spec_hint": spec_hint,
            "timestamp_hint": ts_hint,
            "size_bytes": p.stat().st_size,
        })
    return out


# --------------------------------------------------------------------- #
# Round classification                                                  #
# --------------------------------------------------------------------- #

OUTCOME_BUCKETS = {
    "passed": {"frozen-and-published"},
    "partial": {"review-halted", "doesnt-fit-yet-no-packet"},
    "failed": {"loop-error", "subprocess-timeout", "drafting-timeout",
               "witness-draft-failed", "witness-timeout", "publish-failed",
               "publish-timeout", "offering-generation-failed",
               "unknown", "no-results"},
    "refused": set(),  # any outcome starting with refused-by-* or
                       # offering-generation-failed prefix
}


def bucket_for(outcome: str) -> str:
    if not isinstance(outcome, str):
        return "failed"
    if outcome.startswith("refused-by-"):
        return "refused"
    if outcome.startswith("offering-generation-failed"):
        return "refused"
    for bucket, members in OUTCOME_BUCKETS.items():
        if outcome in members:
            return bucket
    # Catch-all for unknown outcome strings
    return "failed"


# --------------------------------------------------------------------- #
# Readout rendering                                                     #
# --------------------------------------------------------------------- #

def render_readout(persistent_root: Path) -> str:
    entries = read_master_log(persistent_root)
    round_entries = [e for e in entries if e.get("kind") == "round"]
    loop_start = next((e for e in entries if e.get("kind") == "loop_start"), {})
    loop_finish = next((e for e in entries if e.get("kind") == "loop_finish"), {})
    planner_status = read_planner_status(persistent_root)
    wall_records = collect_wall_records(persistent_root)

    # Group by spec
    selected_specs = loop_start.get("specs", [])
    selected_models = loop_start.get("models", [])
    by_spec = defaultdict(list)
    for r in round_entries:
        by_spec[r.get("spec_id", "unknown")].append(r)

    # Bucket counts
    buckets = defaultdict(list)  # bucket -> list of (spec, model, outcome)
    for r in round_entries:
        spec = r.get("spec_id", "?")
        model = r.get("model", "?")
        outcome = r.get("outcome", "?")
        buckets[bucket_for(outcome)].append((spec, model, outcome))

    # Planner-demoted pairs (= What Was Not Run, if Planner was used)
    demoted_pairs = []
    if planner_status:
        fs = planner_status.get("final_status", {})
        for pair in fs.get("demoted_pairs", []):
            if isinstance(pair, list) and len(pair) == 2:
                demoted_pairs.append(tuple(pair))

    halt_reason = loop_finish.get("halt_reason", "unknown")
    rounds_completed = loop_finish.get("rounds_completed", len(round_entries))
    wall_seconds = loop_finish.get("wall_seconds", 0)
    cumulative_calls = loop_finish.get("cumulative_telus_calls", 0)

    lines = [
        "# Closing Witness Readout — Autonomous Overnight Run",
        "",
        "_This readout records what happened. It does not establish "
        "legitimacy, authority, certification, or readiness for reuse._",
        "",
        "## Run metadata",
        "",
        f"- generated: {now_iso()}",
        f"- persistent_root: `{persistent_root}`",
        f"- rounds attempted: {len(round_entries)}",
        f"- rounds completed: {rounds_completed}",
        f"- wall time: {wall_seconds}s "
        f"({round(wall_seconds / 3600, 2)} hr)",
        f"- cumulative TELUS calls: {cumulative_calls}",
        f"- halt reason: {halt_reason}",
        "",
        "## What Was Selected",
        "",
        "The autonomous orchestrator was given the following spec menu "
        "and model fleet to attempt:",
        "",
        "### Specs",
        "",
    ]
    for s in selected_specs:
        lines.append(f"- `{s}`")
    lines += [
        "",
        "### Models",
        "",
    ]
    for m in selected_models:
        lines.append(f"- `{m}`")
    lines += [
        "",
        "## What Was Attempted",
        "",
        f"The loop attempted {len(round_entries)} round(s), each round "
        "being one (spec × model) pair through the full chain (offering → "
        "drafting → build → witness-draft → reviewer → publish):",
        "",
    ]
    # Group by spec for readability
    for spec in selected_specs:
        rounds_for_spec = by_spec.get(spec, [])
        if not rounds_for_spec:
            lines.append(f"- `{spec}`: not attempted in this run")
            continue
        attempts = [
            f"{r.get('model','?')}→{r.get('outcome','?')[:40]}"
            for r in rounds_for_spec
        ]
        lines.append(f"- `{spec}`: {len(rounds_for_spec)} attempt(s) — "
                      + "; ".join(attempts))
    lines += [
        "",
        "## What Passed",
        "",
        f"Rounds that produced a frozen build packet + a published "
        f"witness record: **{len(buckets['passed'])}**.",
        "",
    ]
    for spec, model, _ in buckets["passed"]:
        lines.append(f"- `{spec}` × `{model}`")
    if not buckets["passed"]:
        lines.append("(none)")

    lines += [
        "",
        "## What Was Partial",
        "",
        "Rounds where the chain proceeded but did not reach publish — "
        "Reviewer halted (mesh-mode caught a coherence concern) OR the "
        "spec did not fit yet (no frozen packet emitted). Honoring "
        "\"doesn't fit yet\" as a valid outcome.",
        "",
    ]
    for spec, model, outcome in buckets["partial"]:
        lines.append(f"- `{spec}` × `{model}` — {outcome}")
    if not buckets["partial"]:
        lines.append("(none)")

    lines += [
        "",
        "## What Failed",
        "",
        "Rounds where a stage errored unexpectedly (subprocess timeout, "
        "model gateway error, parse failure). These are operator-review "
        "cases, not authority claims about the spec.",
        "",
    ]
    for spec, model, outcome in buckets["failed"]:
        lines.append(f"- `{spec}` × `{model}` — {outcome}")
    if not buckets["failed"]:
        lines.append("(none)")

    lines += [
        "",
        "## What Was Refused",
        "",
        "Rounds where the orchestrator's refusal gatekeeper, OR the "
        "model itself, refused to proceed. Refusal-as-record: these "
        "are first-class outcomes, not failures.",
        "",
    ]
    for spec, model, outcome in buckets["refused"]:
        lines.append(f"- `{spec}` × `{model}` — {outcome}")
    if not buckets["refused"]:
        lines.append("(none)")

    lines += [
        "",
        "## What Was Not Run",
        "",
    ]
    if planner_status is None:
        lines.append("Planner-mode was not enabled for this run; the "
                      "round-robin cycler attempted every (spec, model) "
                      "pair until budgets were reached.")
    elif not demoted_pairs:
        lines.append("Planner was enabled; no (spec, model) pairs were "
                      "demoted during this run.")
    else:
        lines.append("Planner adaptively demoted the following pairs "
                      "after consecutive non-publish outcomes; subsequent "
                      "rounds skipped them:")
        lines.append("")
        for spec, model in demoted_pairs:
            lines.append(f"- `{spec}` × `{model}`")

    lines += [
        "",
        "## What Remains For Review",
        "",
        f"The wall contains {len(wall_records)} witness record(s) ready "
        "for operator review before any external sharing. Reviewer "
        "findings sit alongside each round's `result.json`. The "
        "aggregator's recommendations file surfaces patterns across "
        "rounds.",
        "",
        "### Wall records",
        "",
    ]
    for w in wall_records:
        rel = Path(w["file"]).relative_to(persistent_root) \
            if Path(w["file"]).is_relative_to(persistent_root) \
            else Path(w["file"]).name
        lines.append(f"- `{rel}` ({w['size_bytes']} bytes)"
                      + (f" — {w['spec_hint']}" if w["spec_hint"] else ""))
    if not wall_records:
        lines.append("(none)")

    # Aggregator pointer
    agg_dir = persistent_root / "aggregator"
    if agg_dir.exists():
        latest_agg = sorted(agg_dir.glob("recommendations-after-round-*.md"))
        if latest_agg:
            lines += [
                "",
                "### Aggregator recommendations (latest)",
                "",
                f"- `{latest_agg[-1].relative_to(persistent_root)}`",
            ]

    lines += [
        "",
        "## Closing Boundary",
        "",
        "This readout records what happened during an autonomous "
        "experimental build attempt. It does not establish legitimacy, "
        "authority, certification, community consent, or readiness for "
        "reuse. The witness records on the wall are DRAFTS produced by "
        "the autonomous chain; operator review before external sharing "
        "is the human authority that ratifies the closing artifact.",
        "",
    ]

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_render(args):
    pr = Path(args.persistent_root).expanduser().resolve()
    if not pr.exists():
        raise SystemExit(f"persistent_root does not exist: {pr}")
    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = render_readout(pr)
    out_path.write_text(md)
    print(f"closing-witness-readout → {out_path}")
    print(f"  size: {len(md)} bytes")


def main():
    ap = argparse.ArgumentParser(prog="closing_readout.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    apr = sub.add_parser("render")
    apr.add_argument("--persistent-root", required=True)
    apr.add_argument("--out", required=True)
    apr.set_defaults(func=cmd_render)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
