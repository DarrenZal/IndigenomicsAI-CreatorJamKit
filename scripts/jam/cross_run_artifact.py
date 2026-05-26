#!/usr/bin/env python3
"""cross_run_artifact.py — cross-run weaver for autonomous overnight runs.

Reads N persistent_roots (each one a completed overnight_loop run with
its own configuration) and produces ONE comparative narrative
document. Surfaces:
  - Where the runs AGREED (consistent vocabulary / discipline / themes
    across configurations)
  - Where they DIVERGED (config-dependent patterns)
  - Cross-run aggregate stats (totals, refusal rates per model)
  - The top composition proposals across the runs
  - A single closing boundary at the end

Discipline:
  - Output carries ONE closing boundary at the very end (not three).
  - Cross-run synthesis prose runs ONLY against the gateway model
    (TELUS); one-shot retry; temperature=0.2; verb discipline mirrors
    coherence_synthesizer.SYNTHESIZER_SYSTEM.
  - If the gateway fails, write a fallback markdown with statistics +
    composition highlights but no LLM synthesis section (exit 0).
  - If 0 runs are passed, write a graceful stub + exit 0.
  - Bound the model payload: only the synthesis prose from each run's
    coherence-synthesis.md is sent, not the wall records themselves.

Usage:
  python3 scripts/jam/cross_run_artifact.py weave \\
      --persistent-roots <root1>,<root2>,<root3> \\
      --gateway http://localhost:8000 \\
      --model telus-gemma \\
      [--team-key KEY | env TELUS_TEAM_KEY] \\
      --out <cross-run-artifact.md>
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.spec_drafting_loop import _try_parse_json  # noqa: E402,F401
from jam import coherence_synthesizer as cs  # noqa: E402
from jam import ceremony_artifact as ca  # noqa: E402
from jam import closing_readout as cr  # noqa: E402


# Bound the synthesis prose sent to the model from each run.
PER_RUN_SYNTHESIS_CAP = 3000
# Maximum composition highlights to surface.
MAX_COMPOSITION_HIGHLIGHTS = 5


CROSS_RUN_CLOSING_BOUNDARY = (
    "This document records what happened across {n} experimental "
    "autonomous overnight runs. It does not establish legitimacy, "
    "authority, certification, community consent, or readiness for "
    "reuse. The wall records on each run are DRAFTS produced by the "
    "autonomous chain; operator review before external sharing is the "
    "human authority that ratifies the closing presentation."
)


# Anti-overclaim prompt mirrored from coherence_synthesizer.SYNTHESIZER_SYSTEM,
# adapted for cross-run scope (agreement vs divergence across configs).
CROSS_RUN_SYNTHESIZER_SYSTEM = (
    "You are a Cross-Run Coherence Synthesizer for an IndigenomicsAI "
    "Creator Jam autonomous overnight experiment. You read a JSON "
    "payload listing N completed runs, each with a different "
    "configuration (planner threshold, mesh mode, DAG strictness). "
    "Each run includes (a) its synthesis prose written by the in-run "
    "coherence synthesizer and (b) its top outcomes. Your task is to "
    "produce a SHORT FLAT-MARKDOWN PROSE comparative synthesis with "
    "THREE labeled passages.\n\n"
    "OUTPUT FORMAT — STRICT:\n"
    "Reply with flat markdown prose only. No JSON. No code fence. No "
    "headings (## etc). 200-400 words MAX total. Use exactly three "
    "bold inline labels — **Where the runs agreed**, **Where they "
    "diverged**, **What the substrate collectively observed** — each "
    "followed by a paragraph.\n\n"
    "DISCIPLINE (load-bearing):\n"
    "- Use kit verb discipline: 'observed', 'witnessed', 'recorded', "
    "  'surfaced', 'held'.\n"
    "- NEVER use these words in any context: 'certified', "
    "  'certification', 'approved', 'approval', 'authorized', "
    "  'authorization', 'validated', 'validation', 'legitimate', "
    "  'legitimacy', 'official'. Descriptive use of outcome words "
    "  like 'refused', 'halted', 'frozen' is OK.\n"
    "- Do NOT recommend external action, downstream reuse, or "
    "  publication beyond operator review.\n"
    "- Do NOT include the input payload in your output.\n"
    "- Do NOT invent runs that are not in the payload.\n"
    "- If two runs share too little to compare, say so plainly under "
    "  the relevant label — that is a valid outcome.\n"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Run discovery + config extraction                                     #
# --------------------------------------------------------------------- #

def label_from_root(persistent_root: Path) -> str:
    """Derive a short run label from the persistent_root path basename."""
    return persistent_root.name or str(persistent_root)


def extract_config_from_loop_start(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Pull the configuration-relevant fields from a loop_start entry.
    Returns {planner_threshold, mesh_mode, dag_mode, max_rounds,
    time_budget_hours, models, specs}. Missing fields default to None
    or sensible falsy values.
    """
    if not isinstance(entry, dict):
        return {
            "planner_threshold": None,
            "mesh_mode": None,
            "dag_mode": None,
            "max_rounds": None,
            "time_budget_hours": None,
            "models": [],
            "specs": [],
        }
    return {
        # These three may not be present in loop_start (they're often
        # passed as CLI flags to overnight_loop.py rather than logged);
        # we surface them when available, otherwise None.
        "planner_threshold": entry.get("planner_threshold"),
        "mesh_mode": entry.get("mesh_mode"),
        "dag_mode": entry.get("dag_mode") or entry.get("dag"),
        "max_rounds": entry.get("max_rounds"),
        "time_budget_hours": entry.get("time_budget_hours"),
        "models": entry.get("models", []) or [],
        "specs": entry.get("specs", []) or [],
    }


def collect_round_entries(persistent_root: Path) -> List[Dict[str, Any]]:
    return [
        e for e in cr.read_master_log(persistent_root)
        if isinstance(e, dict) and e.get("kind") == "round"
    ]


def bucket_outcome_counts(
    round_entries: List[Dict[str, Any]],
) -> Dict[str, int]:
    """Use closing_readout.bucket_for to bucket outcomes. Also record
    'no-publish' = anything that did not end in frozen-and-published.
    """
    counts: Dict[str, int] = defaultdict(int)
    for r in round_entries:
        outcome = r.get("outcome", "?")
        bucket = cr.bucket_for(outcome)
        counts[bucket] += 1
        if bucket != "passed":
            counts["no-publish"] += 1
    return dict(counts)


def refusal_rates_per_model(
    round_entries: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """For each model, return {total, refused, refusal_rate}."""
    by_model_total: Counter = Counter()
    by_model_refused: Counter = Counter()
    for r in round_entries:
        model = r.get("model", "?")
        outcome = r.get("outcome", "?")
        by_model_total[model] += 1
        if cr.bucket_for(outcome) == "refused":
            by_model_refused[model] += 1
    out: Dict[str, Dict[str, Any]] = {}
    for model, total in by_model_total.items():
        refused = by_model_refused[model]
        rate = round(refused / total, 3) if total else 0.0
        out[model] = {
            "total": total,
            "refused": refused,
            "refusal_rate": rate,
        }
    return out


def top_specs_by_publish(
    round_entries: List[Dict[str, Any]],
    n: int = 3,
) -> List[Tuple[str, int]]:
    """Return top-N specs by frozen-and-published count."""
    counts: Counter = Counter()
    for r in round_entries:
        if r.get("outcome") == "frozen-and-published":
            counts[r.get("spec_id", "?")] += 1
    return counts.most_common(n)


def extract_synthesis_prose(persistent_root: Path) -> str:
    """Read coherence-synthesis.md and extract the prose under
    '## What these specs say together'. Returns empty string if
    missing or section absent.
    """
    p = persistent_root / "coherence-synthesis.md"
    if not p.exists():
        return ""
    try:
        text = p.read_text()
    except Exception:
        return ""
    # Slice between "## What these specs say together" and the next "## "
    m = re.search(
        r"^##\s+What these specs say together\s*\n(.*?)(?=^##\s)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not m:
        return ""
    body = m.group(1).strip()
    # Drop "no records to synthesize" stub
    if body.startswith("No published witness records"):
        return ""
    # Drop the "_LLM synthesis was not produced..._" fallback note
    if body.startswith("_LLM synthesis was not produced"):
        return ""
    return body[:PER_RUN_SYNTHESIS_CAP]


def discover_runs(
    persistent_roots: List[Path],
) -> List[Dict[str, Any]]:
    """Walk each persistent_root and build a run-summary dict.
    Returns list of {label, persistent_root, config, outcome_counts,
    refusal_rates, top_specs, wall_record_count, synthesis_prose}.
    """
    runs: List[Dict[str, Any]] = []
    for pr in persistent_roots:
        entries = cr.read_master_log(pr)
        loop_start = next(
            (e for e in entries if isinstance(e, dict)
             and e.get("kind") == "loop_start"),
            {},
        )
        round_entries = [
            e for e in entries
            if isinstance(e, dict) and e.get("kind") == "round"
        ]
        config = extract_config_from_loop_start(loop_start)
        outcome_counts = bucket_outcome_counts(round_entries)
        wall_records = cs.collect_wall_records(pr)
        runs.append({
            "label": label_from_root(pr),
            "persistent_root": str(pr),
            "config": config,
            "outcome_counts": outcome_counts,
            "rounds_total": len(round_entries),
            "refusal_rates": refusal_rates_per_model(round_entries),
            "top_specs": top_specs_by_publish(round_entries, n=3),
            "wall_record_count": len(wall_records),
            "synthesis_prose": extract_synthesis_prose(pr),
        })
    return runs


# --------------------------------------------------------------------- #
# Composition highlights                                                #
# --------------------------------------------------------------------- #

# Capture (refused.*)? as honesty signal in caveats / refusals.
REFUSAL_PATTERN = re.compile(r"\brefus", re.IGNORECASE)
CAVEATS_HEADING_RE = re.compile(
    r"^###?\s+Composition\s+caveats\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _read_proposal_specs_touched(body: str) -> List[str]:
    """Extract spec ids from a proposal body (the '### `<spec-id>`'
    lines under '## Components composed').
    """
    out: List[str] = []
    for m in re.finditer(r"^###\s+`([^`]+)`", body, re.MULTILINE):
        sid = m.group(1)
        # Skip the proposal-title backticks if any (those are inside
        # bullet lines, not under ### headings, but safe).
        out.append(sid)
    return out


def _proposal_section(body: str, heading: str) -> str:
    """Slice the body under a heading until the next heading of the
    same or higher level. Returns empty string if not found.
    """
    pattern = re.compile(
        rf"^(#{{1,6}})\s+{re.escape(heading)}\s*\n(.*?)(?=^#{{1,6}}\s|\Z)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(body)
    if not m:
        return ""
    return m.group(2).strip()


def _proposal_title(body: str) -> str:
    """Extract proposal title — either from '### Title' section or
    from the first '# ' line."""
    title = _proposal_section(body, "Title")
    if title:
        return title.splitlines()[0].strip()
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def _proposal_vision(body: str) -> str:
    return _proposal_section(body, "Vision")


def _proposal_seams(body: str) -> str:
    return _proposal_section(body, "Composition seams")


def _proposal_caveats(body: str) -> str:
    return _proposal_section(body, "Composition caveats")


def _proposal_intent(body: str) -> str:
    """Extract the '- intent: ...' frontmatter line."""
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("- intent:"):
            return s[len("- intent:"):].strip()
    return ""


def _proposal_is_refusal(body: str) -> bool:
    """A proposal is a refusal-as-record if the title or vision
    surfaces refusal language and there's no Composition seams /
    composed spec block.
    """
    title = _proposal_title(body).lower()
    if REFUSAL_PATTERN.search(title):
        return True
    # Heuristic: if vision starts with "Refused" or "The composer
    # refused", treat as refusal record.
    vision = _proposal_vision(body).lower()
    if vision.startswith("refused") or "refused to compose" in vision:
        return True
    return False


def collect_compositions(run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Read all proposal-*.md files for a run and structure them."""
    pr = Path(run["persistent_root"])
    comp_dir = pr / "compositions"
    out: List[Dict[str, Any]] = []
    if not comp_dir.exists():
        return out
    for p in sorted(comp_dir.glob("proposal-*.md")):
        try:
            body = p.read_text()
        except Exception:
            continue
        specs = _read_proposal_specs_touched(body)
        caveats = _proposal_caveats(body)
        out.append({
            "run_label": run["label"],
            "filename": p.name,
            "file": str(p),
            "title": _proposal_title(body),
            "intent": _proposal_intent(body),
            "vision": _proposal_vision(body),
            "seams": _proposal_seams(body),
            "caveats": caveats,
            "specs_touched": specs,
            "is_refusal": _proposal_is_refusal(body),
            "has_caveats": bool(caveats.strip()),
            "body": body,
        })
    return out


def pick_diverse_highlights(
    all_proposals: List[Dict[str, Any]],
    max_n: int = MAX_COMPOSITION_HIGHLIGHTS,
) -> List[Dict[str, Any]]:
    """Score and pick diverse compositions across runs.

    Scoring:
      + spec diversity (count of unique specs touched)
      + explicit composition_caveats present (honesty signal)
      + refusal-as-record (first-class)
    Diversity guard: prefer proposals that touch DIFFERENT spec sets
    from already-picked ones.
    """
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for prop in all_proposals:
        n_specs = len(set(prop.get("specs_touched") or []))
        score = float(n_specs)
        if prop.get("has_caveats"):
            score += 1.0
        if prop.get("is_refusal"):
            score += 1.5
        scored.append((score, prop))
    scored.sort(key=lambda t: t[0], reverse=True)

    picked: List[Dict[str, Any]] = []
    picked_spec_sets: List[set] = []
    for score, prop in scored:
        spec_set = set(prop.get("specs_touched") or [])
        # Skip if exact same spec set already picked (encourages
        # diversity); allow if it's a refusal (first-class regardless).
        if spec_set and any(spec_set == s for s in picked_spec_sets) \
                and not prop.get("is_refusal"):
            continue
        picked.append(prop)
        picked_spec_sets.append(spec_set)
        if len(picked) >= max_n:
            break
    return picked


# --------------------------------------------------------------------- #
# Gateway synthesis call                                                #
# --------------------------------------------------------------------- #

def build_cross_run_payload(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Bound the payload — only synthesis prose + outcome summary."""
    bounded: List[Dict[str, Any]] = []
    for r in runs:
        bounded.append({
            "label": r["label"],
            "config": {
                "planner_threshold": r["config"].get("planner_threshold"),
                "mesh_mode": r["config"].get("mesh_mode"),
                "dag_mode": r["config"].get("dag_mode"),
                "max_rounds": r["config"].get("max_rounds"),
                "time_budget_hours": r["config"].get("time_budget_hours"),
            },
            "outcome_counts": r.get("outcome_counts", {}),
            "rounds_total": r.get("rounds_total", 0),
            "wall_record_count": r.get("wall_record_count", 0),
            "top_specs": [
                {"spec_id": s, "publishes": n}
                for s, n in r.get("top_specs", [])
            ],
            "synthesis_prose": (r.get("synthesis_prose") or "")[
                :PER_RUN_SYNTHESIS_CAP
            ],
        })
    return {"runs": bounded}


def call_cross_run_gateway(
    base_url: str,
    team_key: str,
    model: str,
    payload: Dict[str, Any],
    timeout: int = 180,
) -> str:
    """Raw chat-completions call. One-shot retry on transient failure.
    Raises RuntimeError on definitive failure — caller handles fallback.
    """
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": CROSS_RUN_SYNTHESIZER_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "temperature": 0.2,
    }).encode()

    data = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(
                f"{base_url.rstrip('/')}/v1/chat/completions",
                data=body,
                headers={
                    "Authorization": f"Bearer {team_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            break
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(
                    f"cross-run gateway request failed after retry: {e}"
                )
            time.sleep(2)

    content = data["choices"][0]["message"]["content"] or ""
    return cs._strip_markdown_fence(content).strip()


# --------------------------------------------------------------------- #
# Markdown rendering                                                    #
# --------------------------------------------------------------------- #

def _format_config(cfg: Dict[str, Any]) -> str:
    parts = []
    if cfg.get("planner_threshold") is not None:
        parts.append(f"planner_threshold={cfg['planner_threshold']}")
    if cfg.get("mesh_mode") is not None:
        parts.append(f"mesh_mode={cfg['mesh_mode']}")
    if cfg.get("dag_mode") is not None:
        parts.append(f"dag_mode={cfg['dag_mode']}")
    if cfg.get("max_rounds") is not None:
        parts.append(f"max_rounds={cfg['max_rounds']}")
    if cfg.get("time_budget_hours") is not None:
        parts.append(f"time_budget_hours={cfg['time_budget_hours']}")
    if not parts:
        return "(no configuration fields recorded in loop_start)"
    return ", ".join(parts)


def render_run_inventory(runs: List[Dict[str, Any]]) -> List[str]:
    lines: List[str] = []
    for r in runs:
        lines.append(f"### `{r['label']}`")
        lines.append("")
        lines.append(f"- persistent_root: `{r['persistent_root']}`")
        lines.append(f"- configuration: {_format_config(r['config'])}")
        lines.append(f"- rounds total: {r.get('rounds_total', 0)}")
        lines.append(f"- wall records: {r.get('wall_record_count', 0)}")
        oc = r.get("outcome_counts", {})
        bucket_summary = ", ".join(
            f"{b}={n}" for b, n in sorted(oc.items())
        ) or "(none)"
        lines.append(f"- outcomes: {bucket_summary}")
        top = r.get("top_specs", [])
        if top:
            lines.append("- top published specs:")
            for sid, n in top:
                lines.append(f"  - `{sid}` ({n})")
        else:
            lines.append("- top published specs: (none)")
        rr = r.get("refusal_rates", {})
        if rr:
            lines.append("- refusal rate per model:")
            for model in sorted(rr.keys()):
                m = rr[model]
                lines.append(
                    f"  - `{model}`: {m['refused']}/{m['total']} "
                    f"({m['refusal_rate'] * 100:.1f}%)"
                )
        lines.append("")
    return lines


def render_composition_highlight(prop: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    lines.append(
        f"### `{prop['run_label']}` / `{prop['filename']}`"
    )
    lines.append("")
    if prop.get("intent"):
        lines.append(f"- intent: {prop['intent']}")
    if prop.get("specs_touched"):
        specs = ", ".join(f"`{s}`" for s in prop["specs_touched"])
        lines.append(f"- specs touched: {specs}")
    if prop.get("is_refusal"):
        lines.append("- refusal-as-record: yes")
    if prop.get("has_caveats"):
        lines.append("- carries explicit composition caveats: yes")
    lines.append("")
    if prop.get("title"):
        lines.append(f"**Title**: {prop['title']}")
        lines.append("")
    if prop.get("vision"):
        lines.append("**Vision**")
        lines.append("")
        lines.append(prop["vision"])
        lines.append("")
    if prop.get("seams"):
        lines.append("**Composition seams**")
        lines.append("")
        lines.append(prop["seams"])
        lines.append("")
    if prop.get("caveats"):
        lines.append("**Composition caveats**")
        lines.append("")
        lines.append(prop["caveats"])
        lines.append("")
    return lines


def render_cross_run_document(
    runs: List[Dict[str, Any]],
    highlights: List[Dict[str, Any]],
    synthesis_prose: Optional[str],
    synthesis_skipped_reason: Optional[str] = None,
) -> str:
    """Render the unified cross-run artifact."""
    n = len(runs)
    if n == 0:
        return (
            "# Cross-Run Closing Ceremony Artifact\n\n"
            "_No persistent_roots were supplied (or none existed). "
            "There is nothing to weave across._\n\n"
            "## Closing Boundary\n\n"
            + CROSS_RUN_CLOSING_BOUNDARY.format(n=0)
            + "\n"
        )

    lines: List[str] = [
        "# Cross-Run Closing Ceremony Artifact",
        "",
        f"_Weaves {n} autonomous overnight runs into ONE comparative "
        "narrative. Each run had different configuration (planner "
        "threshold, mesh mode, DAG flag); this document surfaces what "
        "they agreed on and where they diverged._",
        "",
        f"- generated: {now_iso()}",
        f"- runs woven: {n}",
        "",
        "---",
        "",
        "## Run inventory",
        "",
    ]
    lines += render_run_inventory(runs)
    lines.append("---")
    lines.append("")

    # Cross-run aggregate stats
    total_rounds = sum(r.get("rounds_total", 0) for r in runs)
    total_wall = sum(r.get("wall_record_count", 0) for r in runs)
    total_compositions = sum(
        len(collect_compositions(r)) for r in runs
    )
    # Per-model refusal across all runs
    cross_model_total: Counter = Counter()
    cross_model_refused: Counter = Counter()
    for r in runs:
        for model, m in (r.get("refusal_rates") or {}).items():
            cross_model_total[model] += m["total"]
            cross_model_refused[model] += m["refused"]

    lines += [
        "## Cross-run aggregate",
        "",
        f"- total rounds across runs: {total_rounds}",
        f"- total wall records across runs: {total_wall}",
        f"- total composition proposals across runs: {total_compositions}",
        "",
        "### Refusal rate per model (across runs)",
        "",
    ]
    if cross_model_total:
        for model in sorted(cross_model_total.keys()):
            total = cross_model_total[model]
            refused = cross_model_refused[model]
            rate = (refused / total) if total else 0.0
            lines.append(
                f"- `{model}`: {refused}/{total} ({rate * 100:.1f}%)"
            )
    else:
        lines.append("(no per-model outcome data found)")
    lines += ["", "---", ""]

    # Cross-run pattern (LLM synthesis)
    lines += [
        "## Cross-run pattern (substrate synthesis)",
        "",
    ]
    if synthesis_prose:
        lines.append(synthesis_prose.strip())
        lines.append("")
    else:
        reason = synthesis_skipped_reason or "synthesis was not run"
        lines += [
            f"_LLM cross-run synthesis was not produced for this "
            f"weave ({reason}). The run inventory and composition "
            "highlights above/below remain the substrate's own voice._",
            "",
        ]
    lines += ["---", ""]

    # Composition highlights
    lines += [
        "## Cross-run composition highlights",
        "",
        "Composition proposals selected for diversity (specs touched + "
        "honesty signals like explicit composition caveats and "
        "refusal-as-record). Each proposal speaks in the substrate's "
        "voice; the closing boundaries on the individual proposal files "
        "have been stripped — ONE unified boundary appears at the end "
        "of this document.",
        "",
    ]
    if highlights:
        for prop in highlights:
            lines += render_composition_highlight(prop)
    else:
        lines.append("_No composition proposals were found across the "
                     "weaved runs._")
        lines.append("")
    lines.append("---")
    lines.append("")

    # Single unified closing boundary
    lines += [
        "## Closing Boundary",
        "",
        CROSS_RUN_CLOSING_BOUNDARY.format(n=n),
        "",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# Top-level weave entrypoint                                            #
# --------------------------------------------------------------------- #

def weave(
    persistent_roots: List[Path],
    gateway: str,
    model: str,
    team_key: Optional[str],
) -> str:
    """Top-level: discover runs, gather highlights, call gateway (soft),
    render the unified markdown."""
    runs = discover_runs(persistent_roots)
    if not runs:
        return render_cross_run_document(
            runs=[], highlights=[],
            synthesis_prose=None,
            synthesis_skipped_reason="no runs supplied",
        )

    # Gather + score composition highlights across runs
    all_props: List[Dict[str, Any]] = []
    for r in runs:
        all_props.extend(collect_compositions(r))
    highlights = pick_diverse_highlights(all_props)

    # Gateway call — fail soft.
    synthesis_prose: Optional[str] = None
    skipped_reason: Optional[str] = None
    payload = build_cross_run_payload(runs)
    if not team_key:
        skipped_reason = (
            "team key not provided via --team-key or TELUS_TEAM_KEY env"
        )
    else:
        try:
            synthesis_prose = call_cross_run_gateway(
                base_url=gateway,
                team_key=team_key,
                model=model,
                payload=payload,
            )
            if not synthesis_prose.strip():
                synthesis_prose = None
                skipped_reason = "gateway returned empty content"
        except Exception as e:
            synthesis_prose = None
            skipped_reason = f"gateway error: {e}"

    return render_cross_run_document(
        runs=runs,
        highlights=highlights,
        synthesis_prose=synthesis_prose,
        synthesis_skipped_reason=skipped_reason,
    )


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def _parse_roots_arg(raw: str) -> List[Path]:
    out: List[Path] = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece:
            continue
        out.append(Path(piece).expanduser().resolve())
    return out


def cmd_weave(args):
    roots = _parse_roots_arg(args.persistent_roots)
    # Filter to those that exist; warn for missing.
    existing: List[Path] = []
    for r in roots:
        if r.exists():
            existing.append(r)
        else:
            print(f"warning: persistent_root does not exist: {r}",
                  file=sys.stderr)

    team_key = os.environ.get("TELUS_TEAM_KEY") or args.team_key
    if args.team_key and not os.environ.get("TELUS_TEAM_KEY"):
        print("warning: --team-key passed via argv; prefer "
              "'export TELUS_TEAM_KEY=...'", file=sys.stderr)

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    md = weave(
        persistent_roots=existing,
        gateway=args.gateway,
        model=args.model,
        team_key=team_key,
    )
    out_path.write_text(md)
    print(f"cross-run-artifact → {out_path}")
    print(f"  runs woven: {len(existing)}")
    print(f"  size: {len(md)} bytes")


def main():
    ap = argparse.ArgumentParser(prog="cross_run_artifact.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    apw = sub.add_parser("weave")
    apw.add_argument(
        "--persistent-roots", required=True,
        help="Comma-separated list of persistent_root directories.",
    )
    apw.add_argument("--gateway", required=True)
    apw.add_argument("--model", required=True)
    apw.add_argument(
        "--team-key", default=None,
        help="STRONGLY PREFER env var TELUS_TEAM_KEY. "
             "--team-key passes the key via argv which is visible "
             "via /proc; only use for one-off tests.",
    )
    apw.add_argument("--out", required=True)
    apw.set_defaults(func=cmd_weave)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
