#!/usr/bin/env python3
"""agent_aggregator.py — multi-agent-mesh-v0 Aggregator role.

After N rounds of overnight orchestrator runs, the Aggregator reads:
  - the cumulative wall (witness records, one per round)
  - per-round reviewer findings (reviewer-findings.json files)
  - per-round result.json files (stage outcomes, refusal reasons)

...and produces aggregator-recommendations.md — a single markdown
document with prose-only recommendations. NO diffs in v0. v0.2 may
add machine-applicable diff generation.

The aggregator's purpose: surface PATTERNS across rounds — repeated
refusal reasons, repeated overclaim hits, repeated stage failures,
repeated reviewer flags — so the operator (or a future Planner role)
can sharpen prompts / boundaries / spec menu before the next overnight
run.

Discipline:
  - Output is recommendations, NOT decisions. Operator decides.
  - Markdown only. No diffs (defer to v0.2).
  - "No patterns observed" is a valid output. Do not invent findings.

Usage:
  python3 scripts/jam/agent_aggregator.py aggregate \\
      --rounds-dir <dir-containing-round-subdirs> \\
      --wall-root <wall-dir> \\
      --out <aggregator-recommendations.md>

Round dir layout expected:
  <rounds-dir>/
    round-001/
      orchestrator-summary-*.json
      <spec-id>/<run-id>/
        result.json
        reviewer-findings.json   (if reviewer ran)
        witness-record-draft.md
        ...
    round-002/
      ...
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Round-level collection                                                #
# --------------------------------------------------------------------- #

def collect_rounds(rounds_dir: Path) -> List[Dict[str, Any]]:
    """Walk rounds_dir, return per-round summary list."""
    rounds = []
    if not rounds_dir.exists():
        return rounds
    for round_path in sorted(rounds_dir.iterdir()):
        if not round_path.is_dir():
            continue
        round_id = round_path.name
        summaries = sorted(round_path.glob("orchestrator-summary-*.json"))
        summary = None
        if summaries:
            try:
                summary = json.loads(summaries[-1].read_text())
            except Exception:
                summary = None
        per_spec_results = []
        # Also walk per-spec dirs for result.json + reviewer-findings.json
        for spec_dir in sorted(round_path.iterdir()):
            if not spec_dir.is_dir() or spec_dir.name in (
                "wall", "build-queue", "build-sandbox"
            ):
                continue
            for run_dir in sorted(spec_dir.iterdir()):
                if not run_dir.is_dir():
                    continue
                rj = run_dir / "result.json"
                rf = run_dir / "reviewer-findings.json"
                wd = run_dir / "witness-record-draft.md"
                entry = {
                    "spec_id": spec_dir.name,
                    "run_id": run_dir.name,
                    "result": None,
                    "reviewer_findings": None,
                    "witness_draft_present": wd.exists(),
                }
                if rj.exists():
                    try:
                        entry["result"] = json.loads(rj.read_text())
                    except Exception:
                        pass
                if rf.exists():
                    try:
                        entry["reviewer_findings"] = json.loads(rf.read_text())
                    except Exception:
                        pass
                per_spec_results.append(entry)
        rounds.append({
            "round_id": round_id,
            "summary": summary,
            "per_spec": per_spec_results,
        })
    return rounds


# --------------------------------------------------------------------- #
# Pattern analysis                                                      #
# --------------------------------------------------------------------- #

def analyze_outcomes(rounds: List[Dict[str, Any]]) -> Dict[str, Counter]:
    """Count outcomes across all rounds + per-spec."""
    overall = Counter()
    per_spec_outcomes = defaultdict(Counter)
    per_model_outcomes = defaultdict(Counter)
    refusal_reasons = Counter()
    for r in rounds:
        for entry in r["per_spec"]:
            res = entry.get("result") or {}
            outcome = res.get("outcome", "unknown")
            overall[outcome] += 1
            per_spec_outcomes[entry["spec_id"]][outcome] += 1
            model = res.get("model", "unknown")
            per_model_outcomes[model][outcome] += 1
            if outcome and ("refused" in outcome or "doesnt-fit" in outcome):
                # Extract the reason tail
                reason = outcome
                refusal_reasons[reason[:200]] += 1
    return {
        "overall": overall,
        "per_spec": dict(per_spec_outcomes),
        "per_model": dict(per_model_outcomes),
        "refusal_reasons": refusal_reasons,
    }


def analyze_reviewer_findings(rounds: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate reviewer findings across rounds."""
    check_status_counts = defaultdict(Counter)  # check_name -> Counter(status)
    flagged_notes = defaultdict(list)            # check_name -> [notes]
    halted_count = 0
    reviewed_count = 0
    for r in rounds:
        for entry in r["per_spec"]:
            rf = entry.get("reviewer_findings")
            if not rf:
                continue
            findings = rf.get("findings", {})
            if not isinstance(findings, dict):
                continue
            reviewed_count += 1
            if findings.get("halt_publish"):
                halted_count += 1
            for c in findings.get("checks", []):
                if not isinstance(c, dict):
                    continue
                name = c.get("name", "unnamed")
                status = c.get("status", "ok")
                check_status_counts[name][status] += 1
                if status in ("flag", "halt"):
                    note = c.get("note", "")
                    if note:
                        flagged_notes[name].append({
                            "spec_id": entry["spec_id"],
                            "status": status,
                            "note": note[:300],
                        })
    return {
        "reviewed_count": reviewed_count,
        "halted_count": halted_count,
        "check_status_counts": {k: dict(v) for k, v in check_status_counts.items()},
        "flagged_notes": dict(flagged_notes),
    }


def derive_recommendations(
    outcomes: Dict[str, Any],
    reviewer: Dict[str, Any],
    rounds: List[Dict[str, Any]],
) -> List[str]:
    """Prose-only recommendations. No diffs in v0."""
    recs = []
    overall = outcomes["overall"]
    total = sum(overall.values()) or 1
    published = overall.get("frozen-and-published", 0)

    # 1. Refusal pattern
    refusals = outcomes["refusal_reasons"]
    if refusals:
        top_refusal, top_count = refusals.most_common(1)[0]
        if top_count >= 2:
            recs.append(
                f"Refusal pattern observed: `{top_refusal}` fired in "
                f"{top_count} round(s). If this is by-design, consider "
                f"removing those specs from `ORCHESTRATOR_CANDIDATE_SPECS`. "
                f"If unintended, consider sharpening the relevant prompt "
                f"to make the refusal-trigger more explicit OR adding the "
                f"spec to the kit's documented refusal-cases."
            )

    # 2. Reviewer-flagged overclaim vocabulary
    overclaim_flags = reviewer["check_status_counts"].get(
        "overclaim-vocabulary", {}
    )
    overclaim_total = overclaim_flags.get("halt", 0) + overclaim_flags.get("flag", 0)
    if overclaim_total >= 2:
        notes = reviewer["flagged_notes"].get("overclaim-vocabulary", [])
        # Extract specific terms named in notes
        terms_seen = set()
        for n in notes:
            note_text = n["note"].lower()
            # Look for quoted or comma-listed terms
            for term in ["certified", "approved", "authorized", "validated",
                         "legitimate", "official", "successful"]:
                if term in note_text:
                    terms_seen.add(term)
        if terms_seen:
            recs.append(
                f"Overclaim vocabulary flagged in {overclaim_total} witness "
                f"draft(s) — repeat terms: {', '.join(sorted(terms_seen))}. "
                f"Consider sharpening Prompt 3 (witness-drafter) by adding "
                f"these to the forbidden-words list with alternative "
                f"vocabulary examples."
            )
        else:
            recs.append(
                f"Overclaim vocabulary flagged in {overclaim_total} witness "
                f"draft(s). Consider sharpening Prompt 3 with explicit "
                f"forbidden-words examples."
            )

    # 3. Reviewer-flagged boundary-honored
    boundary_flags = reviewer["check_status_counts"].get(
        "boundary-honored-in-draft", {}
    )
    boundary_total = boundary_flags.get("halt", 0) + boundary_flags.get("flag", 0)
    if boundary_total >= 2:
        recs.append(
            f"Boundary-honored-in-draft flagged in {boundary_total} witness "
            f"draft(s). The boundaries-that-remain section may be generic "
            f"or empty across multiple rounds. Consider strengthening Prompt 3's "
            f"explicit instruction to enumerate excluded_inputs in the draft."
        )

    # 4. Model-specific patterns
    for model, model_outcomes in outcomes["per_model"].items():
        model_total = sum(model_outcomes.values())
        if model_total < 2:
            continue
        model_published = model_outcomes.get("frozen-and-published", 0)
        if model_published == 0 and model_total >= 3:
            recs.append(
                f"Model `{model}` published 0 of {model_total} round(s). "
                f"Outcomes: {dict(model_outcomes)}. Consider whether this "
                f"model is mismatched to the spec menu, OR whether the "
                f"sharpened prompts need a model-specific variant."
            )

    # 5. Spec-specific patterns
    for spec_id, spec_outcomes in outcomes["per_spec"].items():
        spec_total = sum(spec_outcomes.values())
        if spec_total >= 3:
            spec_published = spec_outcomes.get("frozen-and-published", 0)
            if spec_published == 0:
                recs.append(
                    f"Spec `{spec_id}` ran {spec_total} time(s) and never "
                    f"reached publish. Outcomes: {dict(spec_outcomes)}. "
                    f"Consider whether the spec body is structured in a way "
                    f"that consistently trips a refusal layer OR is "
                    f"insufficient for the drafting loop."
                )

    # 6. Reviewer never ran case
    if reviewer["reviewed_count"] == 0 and total >= 2:
        recs.append(
            f"Reviewer findings were not present for any round across "
            f"{total} attempt(s). Verify orchestrator stage 6.5 (reviewer) "
            f"is wired into the active orchestrator invocation."
        )

    # 7. Halt rate
    if reviewer["reviewed_count"] > 0:
        halt_rate = reviewer["halted_count"] / reviewer["reviewed_count"]
        if halt_rate >= 0.5:
            recs.append(
                f"Reviewer halted publish on {reviewer['halted_count']} of "
                f"{reviewer['reviewed_count']} draft(s) (halt rate "
                f"{halt_rate:.0%}). High halt-rate suggests Prompt 3 needs "
                f"sharpening, OR reviewer threshold needs calibration."
            )

    if not recs:
        recs.append(
            "No multi-round patterns detected at the threshold for "
            "recommendation. The substrate held steady across this run."
        )

    return recs


# --------------------------------------------------------------------- #
# Markdown rendering                                                    #
# --------------------------------------------------------------------- #

def render_markdown(
    rounds: List[Dict[str, Any]],
    outcomes: Dict[str, Any],
    reviewer: Dict[str, Any],
    recommendations: List[str],
    wall_root: Path,
) -> str:
    n_rounds = len(rounds)
    n_attempts = sum(len(r["per_spec"]) for r in rounds)
    overall = outcomes["overall"]
    n_published = overall.get("frozen-and-published", 0)
    wall_count = 0
    if wall_root.exists():
        wall_count = sum(1 for _ in wall_root.glob("*.md"))

    lines = [
        f"# Aggregator Recommendations — Overnight Run",
        "",
        f"- generated: {now_iso()}",
        f"- rounds analyzed: {n_rounds}",
        f"- attempts total: {n_attempts}",
        f"- published to wall: {n_published}",
        f"- wall record count: {wall_count}",
        f"- reviewer findings present: {reviewer['reviewed_count']} of "
        f"{n_attempts}",
        f"- reviewer halt-publish fired: {reviewer['halted_count']}",
        "",
        "## Outcome distribution",
        "",
    ]
    for outcome, count in overall.most_common():
        lines.append(f"- {outcome}: {count}")
    lines.append("")

    # Per-model
    lines.append("## Per-model outcomes")
    lines.append("")
    for model, model_outcomes in outcomes["per_model"].items():
        lines.append(f"- **{model}**: {dict(model_outcomes)}")
    lines.append("")

    # Reviewer check summary
    if reviewer["check_status_counts"]:
        lines.append("## Reviewer check status counts")
        lines.append("")
        for name, counts in reviewer["check_status_counts"].items():
            lines.append(f"- **{name}**: {dict(counts)}")
        lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    lines.append(
        "_Prose-only recommendations. No machine-applicable diffs in v0. "
        "Operator decides whether to apply._"
    )
    lines.append("")
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")
        lines.append("")

    # Flagged-note examples (bounded)
    flagged_notes = reviewer.get("flagged_notes", {})
    if flagged_notes:
        lines.append("## Flagged-note examples")
        lines.append("")
        for name, notes in flagged_notes.items():
            if not notes:
                continue
            lines.append(f"### {name}")
            lines.append("")
            for n in notes[:3]:
                lines.append(f"- ({n['spec_id']}, {n['status']}) "
                              f"{n['note']}")
            if len(notes) > 3:
                lines.append(f"- ...and {len(notes) - 3} more")
            lines.append("")

    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_aggregate(args):
    rounds_dir = Path(args.rounds_dir).expanduser()
    wall_root = Path(args.wall_root).expanduser() if args.wall_root else (
        rounds_dir / "wall"
    )
    out_path = Path(args.out).expanduser()

    rounds = collect_rounds(rounds_dir)
    outcomes = analyze_outcomes(rounds)
    reviewer = analyze_reviewer_findings(rounds)
    recs = derive_recommendations(outcomes, reviewer, rounds)
    md = render_markdown(rounds, outcomes, reviewer, recs, wall_root)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"aggregator-recommendations → {out_path}")
    print(f"  rounds analyzed: {len(rounds)}")
    print(f"  recommendations: {len(recs)}")


def main():
    ap = argparse.ArgumentParser(prog="agent_aggregator.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_agg = sub.add_parser("aggregate")
    ap_agg.add_argument("--rounds-dir", required=True)
    ap_agg.add_argument("--wall-root")
    ap_agg.add_argument("--out", required=True)
    ap_agg.set_defaults(func=cmd_aggregate)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
