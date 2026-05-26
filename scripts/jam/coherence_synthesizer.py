#!/usr/bin/env python3
"""coherence_synthesizer.py — cross-spec coherence synthesis from an
overnight_loop persistent_root.

Reads all published wall witness records, per-round reviewer findings,
and build-packet metadata, then asks the gateway model to synthesize a
short paragraph about what the body of work says TOGETHER. Output is a
single markdown file the operator reviews + promotes; nothing is
published autonomously.

Discipline:
  - Output carries the standard closing boundary (no authority /
    certification / reuse claim).
  - Synthesis runs ONLY against the gateway model (TELUS), one-shot
    retry, temperature=0.2.
  - If the gateway fails, write a fallback markdown that lists records
    + clusters but omits the LLM synthesis section; exit 0.
  - If no wall records exist, write a "no published records to
    synthesize" note + exit 0.
  - Cluster names are descriptive operator labels, not authority claims.

Usage:
  python3 scripts/jam/coherence_synthesizer.py synthesize \\
      --persistent-root <path> \\
      --gateway http://localhost:8000 \\
      --model telus-gemma \\
      [--team-key KEY] \\
      --out <out.md>
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.spec_drafting_loop import GatewayModelAdapter, _try_parse_json  # noqa: E402,F401


# Per-record body cap when building the model payload.
PER_RECORD_BODY_CAP = 1500
# Maximum number of wall records to include in the model payload.
MAX_RECORDS_IN_PAYLOAD = 30

# Standard closing boundary text (mirrors closing_readout.py phrasing
# so the two artifacts read as one operator-facing voice).
CLOSING_BOUNDARY = (
    "This synthesis records what the published witness records say "
    "together. It does not establish legitimacy, authority, "
    "certification, community consent, or readiness for reuse. The "
    "wall records themselves are DRAFTS produced by the autonomous "
    "chain; operator review before external sharing is the human "
    "authority that ratifies any closing artifact."
)


# Sharpened synthesis system prompt. Anti-overclaim vocabulary mirrors
# Prompt 3 (witness-drafter) in spec_drafting_loop.py.
SYNTHESIZER_SYSTEM = (
    "You are a Cross-Spec Coherence Synthesizer for an IndigenomicsAI "
    "Creator Jam autonomous overnight run. You read a JSON payload "
    "listing the published wall witness records (each record is a "
    "short markdown body capped at 1500 characters). Your task is to "
    "produce a SHORT FLAT-MARKDOWN PROSE SYNTHESIS that surfaces what "
    "the body of work says TOGETHER.\n\n"
    "OUTPUT FORMAT — STRICT:\n"
    "Reply with flat markdown prose only. No JSON. No code fence. No "
    "headings. No bullet list. 200-400 words MAX.\n\n"
    "DISCIPLINE (load-bearing):\n"
    "- Lead with what the records HAVE IN COMMON across specs, not "
    "  what they differ on.\n"
    "- Use kit verb discipline: 'observed', 'witnessed', 'recorded', "
    "  'surfaced', 'held'.\n"
    "- NEVER use these words in any context: 'certified', "
    "  'certification', 'approved', 'approval', 'authorized', "
    "  'authorization', 'validated', 'validation', 'legitimate', "
    "  'legitimacy', 'successful', 'official'. They trigger overclaim "
    "  validation and block publication.\n"
    "- Do NOT recommend external action, downstream reuse, or "
    "  publication beyond operator review.\n"
    "- Do NOT include the input payload in your output.\n"
    "- Do NOT invent witness records that are not in the payload.\n"
    "- If the records share too little to synthesize, say so plainly "
    "  in one sentence — that is a valid outcome.\n"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Clustering                                                            #
# --------------------------------------------------------------------- #

# Cluster keyword map. Order matters: first match wins per record.
CLUSTER_KEYWORDS: List[Tuple[str, List[str]]] = [
    ("WITNESSING", ["witness", "receipt"]),
    ("ECONOMIC-FLOWS", ["commitment", "pool", "flow"]),
    ("CLAIMS", ["claim", "evidence", "coherence"]),
    ("ASPIRATIONS", ["dream", "fulfillment"]),
    ("BIOREGIONAL", ["bioregion", "ecological", "atlas"]),
]
UNCATEGORIZED = "UNCATEGORIZED"


def cluster_for_vision(vision: str) -> str:
    """Return cluster label for a vision string using keyword heuristic.
    First-match-wins across CLUSTER_KEYWORDS in declaration order.
    """
    if not isinstance(vision, str):
        return UNCATEGORIZED
    low = vision.lower()
    for label, keywords in CLUSTER_KEYWORDS:
        for kw in keywords:
            if kw in low:
                return label
    return UNCATEGORIZED


# --------------------------------------------------------------------- #
# Persistent-root readers                                               #
# --------------------------------------------------------------------- #

def collect_wall_records(persistent_root: Path) -> List[Dict[str, Any]]:
    """Walk <persistent_root>/wall/ for witness record markdown files.
    Returns list of {file, name, body, size_bytes}, sorted by filename.
    """
    wall_root = persistent_root / "wall"
    out: List[Dict[str, Any]] = []
    if not wall_root.exists():
        return out
    for p in sorted(wall_root.rglob("*.md")):
        try:
            body = p.read_text()
        except Exception:
            body = ""
        out.append({
            "file": str(p),
            "name": p.name,
            "body": body,
            "size_bytes": p.stat().st_size,
        })
    return out


def collect_build_packets(persistent_root: Path) -> List[Dict[str, Any]]:
    """Walk persistent_root/rounds/**/5-agentic-build-packet-v0.json
    via rglob. Returns list of {file, spec_id, vision, build_target,
    title}. Tolerates malformed JSON (skips).
    """
    rounds_root = persistent_root / "rounds"
    out: List[Dict[str, Any]] = []
    if not rounds_root.exists():
        return out
    for p in sorted(rounds_root.rglob("5-agentic-build-packet-v0.json")):
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        spec = data.get("team_spec") if isinstance(data, dict) else None
        if not isinstance(spec, dict):
            spec = {}
        # Best-effort spec_id: prefer explicit field, fall back to dir
        # name two levels up (rounds/round-NNNN/<spec-id>/<run-id>/...)
        spec_id = (
            spec.get("spec_id")
            or data.get("spec_id")
            or _infer_spec_id_from_path(p, rounds_root)
        )
        out.append({
            "file": str(p),
            "spec_id": spec_id or "unknown",
            "title": spec.get("title", ""),
            "vision": spec.get("vision", ""),
            "build_target": spec.get("build_target", ""),
        })
    return out


def _infer_spec_id_from_path(packet_path: Path, rounds_root: Path) -> str:
    """Walk up from the packet file looking for the <spec-id> dir, which
    sits immediately under rounds/round-NNNN/. Returns empty string if
    the layout doesn't match.
    """
    try:
        rel = packet_path.relative_to(rounds_root).parts
    except ValueError:
        return ""
    # Expect: <round-NNNN>, <spec-id>, <run-id>, ..., 5-agentic-build-packet-v0.json
    if len(rel) >= 2:
        return rel[1]
    return ""


def collect_reviewer_findings(persistent_root: Path) -> List[Dict[str, Any]]:
    """Walk rounds/**/reviewer-findings.json. Returns list of
    {file, halt_publish, review_passed, halts, flags}. Tolerates
    malformed JSON.
    """
    rounds_root = persistent_root / "rounds"
    out: List[Dict[str, Any]] = []
    if not rounds_root.exists():
        return out
    for p in sorted(rounds_root.rglob("reviewer-findings.json")):
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        findings = data.get("findings") if isinstance(data, dict) else None
        if not isinstance(findings, dict):
            findings = {}
        checks = findings.get("checks") if isinstance(findings.get("checks"), list) else []
        halts = sum(1 for c in checks if isinstance(c, dict) and c.get("status") == "halt")
        flags = sum(1 for c in checks if isinstance(c, dict) and c.get("status") == "flag")
        out.append({
            "file": str(p),
            "halt_publish": bool(findings.get("halt_publish", False)),
            "review_passed": bool(findings.get("review_passed", False)),
            "halts": halts,
            "flags": flags,
        })
    return out


# --------------------------------------------------------------------- #
# Spec clustering                                                       #
# --------------------------------------------------------------------- #

def cluster_specs(
    build_packets: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    """Deduplicate build packets by spec_id (keep first), then group
    into clusters using vision-keyword heuristic. Returns dict mapping
    cluster_label -> list of dedup'd spec entries.
    """
    by_spec: Dict[str, Dict[str, Any]] = {}
    for bp in build_packets:
        sid = bp.get("spec_id") or "unknown"
        if sid not in by_spec:
            by_spec[sid] = bp
    clusters: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for sid, bp in by_spec.items():
        label = cluster_for_vision(bp.get("vision", ""))
        clusters[label].append(bp)
    return dict(clusters)


# --------------------------------------------------------------------- #
# Gateway synthesis call                                                #
# --------------------------------------------------------------------- #

def call_synthesizer_gateway(
    base_url: str,
    team_key: str,
    model: str,
    payload: Dict[str, Any],
    timeout: int = 120,
) -> str:
    """Raw chat-completions call. Returns the synthesis prose string.
    One-shot retry on transient upstream failures. Raises on definitive
    failure — caller handles fallback rendering.
    """
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYNTHESIZER_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "temperature": 0.2,
    }).encode()

    data = None
    last_err: Optional[Exception] = None
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
            last_err = e
            if attempt == 2:
                raise RuntimeError(
                    f"synthesizer gateway request failed after retry: {e}"
                )
            time.sleep(2)

    content = data["choices"][0]["message"]["content"] or ""
    # If the model echoed a JSON fence anyway, strip it. We do NOT
    # require JSON shape — the prompt asks for flat prose.
    return _strip_markdown_fence(content).strip()


def _strip_markdown_fence(text: str) -> str:
    """Remove a leading/trailing ```<lang> fence if present."""
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].rstrip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def build_synthesis_payload(
    wall_records: List[Dict[str, Any]],
    clusters: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """Bound the payload: cap per-record body + cap record count."""
    bounded_records = []
    for w in wall_records[:MAX_RECORDS_IN_PAYLOAD]:
        bounded_records.append({
            "name": w.get("name", ""),
            "body": (w.get("body") or "")[:PER_RECORD_BODY_CAP],
        })
    cluster_summary = []
    for label, specs in clusters.items():
        cluster_summary.append({
            "cluster": label,
            "specs": [
                {
                    "spec_id": s.get("spec_id", ""),
                    "build_target": s.get("build_target", ""),
                    "vision": (s.get("vision") or "")[:400],
                }
                for s in specs
            ],
        })
    return {
        "wall_records": bounded_records,
        "clusters": cluster_summary,
    }


# --------------------------------------------------------------------- #
# Markdown rendering                                                    #
# --------------------------------------------------------------------- #

NO_RECORDS_NOTE = (
    "No published witness records were found under "
    "`<persistent_root>/wall/witness-records/`. There is nothing to "
    "synthesize across."
)


def render_clusters_section(
    clusters: Dict[str, List[Dict[str, Any]]],
) -> List[str]:
    lines: List[str] = []
    if not clusters:
        lines.append("(no build packets found under "
                     "`<persistent_root>/rounds/`)")
        return lines
    # Stable order: declared clusters first, UNCATEGORIZED last.
    order = [label for label, _ in CLUSTER_KEYWORDS] + [UNCATEGORIZED]
    for label in order:
        specs = clusters.get(label)
        if not specs:
            continue
        lines.append(f"### {label}")
        lines.append("")
        for s in specs:
            sid = s.get("spec_id", "unknown")
            target = s.get("build_target", "") or "(no build_target)"
            vision = (s.get("vision") or "").strip().replace("\n", " ")
            if not vision:
                vision = "(no vision recorded)"
            # One sentence: cap roughly at first 240 chars.
            if len(vision) > 240:
                vision = vision[:237].rstrip() + "..."
            lines.append(f"- `{sid}` — *{target}* — {vision}")
        lines.append("")
    return lines


def render_synthesis_document(
    persistent_root: Path,
    wall_records: List[Dict[str, Any]],
    reviewer_findings: List[Dict[str, Any]],
    clusters: Dict[str, List[Dict[str, Any]]],
    synthesis_prose: Optional[str],
    synthesis_skipped_reason: Optional[str] = None,
) -> str:
    """Render the final markdown document.

    synthesis_prose=None + synthesis_skipped_reason set → fallback mode
    (no LLM synthesis section, reason recorded).
    synthesis_prose=str → normal mode.
    Empty wall_records → short "no records" note + exit 0 path.
    """
    lines: List[str] = [
        "# Coherence Synthesis — Autonomous Overnight Run",
        "",
        f"- generated: {now_iso()}",
        f"- persistent_root: `{persistent_root}`",
        f"- wall records read: {len(wall_records)}",
        f"- reviewer findings consulted: {len(reviewer_findings)}",
        "",
    ]

    if not wall_records:
        lines += [
            "## What these specs say together",
            "",
            NO_RECORDS_NOTE,
            "",
            "## Closing Boundary",
            "",
            CLOSING_BOUNDARY,
            "",
        ]
        return "\n".join(lines) + "\n"

    lines += [
        "## Spec themes observed",
        "",
        "Each cluster below groups specs by a keyword heuristic against "
        "the build packet's vision field. Cluster names are descriptive "
        "operator labels, not authority claims.",
        "",
    ]
    lines += render_clusters_section(clusters)

    lines += [
        "## What these specs say together",
        "",
    ]
    if synthesis_prose:
        lines.append(synthesis_prose.strip())
        lines.append("")
    else:
        reason = synthesis_skipped_reason or "synthesis was not run"
        lines += [
            "_LLM synthesis was not produced for this run "
            f"({reason}). The cluster listing above is the only "
            "cross-spec view in this document._",
            "",
        ]

    lines += [
        "## Open coherence questions",
        "",
        "The following questions are surfaced by the cluster layout + "
        "record count; they are flagged for operator/human review and "
        "are NOT answered here:",
        "",
        "- Do the records inside each cluster cohere on vocabulary, "
        "discipline, and outcome framing — or did each spec drift?",
        "- Are there cross-cluster echoes (e.g. WITNESSING ↔ CLAIMS) "
        "that imply a composite picture beyond any single spec?",
        "- Which UNCATEGORIZED specs should have their own cluster "
        "label in a future revision of the heuristic?",
        "- Which reviewer-findings halts/flags did the records carry "
        "into publication, and do they cluster?",
        "",
        "## Closing Boundary",
        "",
        CLOSING_BOUNDARY,
        "",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# Top-level synthesize entrypoint                                       #
# --------------------------------------------------------------------- #

def synthesize(
    persistent_root: Path,
    gateway: str,
    model: str,
    team_key: Optional[str],
) -> str:
    """Read persistent_root, optionally call gateway, return markdown."""
    wall_records = collect_wall_records(persistent_root)
    reviewer_findings = collect_reviewer_findings(persistent_root)
    build_packets = collect_build_packets(persistent_root)
    clusters = cluster_specs(build_packets)

    if not wall_records:
        return render_synthesis_document(
            persistent_root=persistent_root,
            wall_records=wall_records,
            reviewer_findings=reviewer_findings,
            clusters=clusters,
            synthesis_prose=None,
            synthesis_skipped_reason="no published records to synthesize",
        )

    payload = build_synthesis_payload(wall_records, clusters)

    # Gateway call — fail soft.
    synthesis_prose: Optional[str] = None
    skipped_reason: Optional[str] = None
    if not team_key:
        skipped_reason = (
            "team key not provided via --team-key or TELUS_TEAM_KEY env"
        )
    else:
        try:
            synthesis_prose = call_synthesizer_gateway(
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

    return render_synthesis_document(
        persistent_root=persistent_root,
        wall_records=wall_records,
        reviewer_findings=reviewer_findings,
        clusters=clusters,
        synthesis_prose=synthesis_prose,
        synthesis_skipped_reason=skipped_reason,
    )


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_synthesize(args):
    pr = Path(args.persistent_root).expanduser().resolve()
    if not pr.exists():
        raise SystemExit(f"persistent_root does not exist: {pr}")
    # Prefer env var over argv to avoid argv leak (matches kit
    # convention in draft_witness.py / overnight_loop.py).
    team_key = os.environ.get("TELUS_TEAM_KEY") or args.team_key
    if args.team_key and not os.environ.get("TELUS_TEAM_KEY"):
        print("warning: --team-key passed via argv; prefer "
              "'export TELUS_TEAM_KEY=...'", file=sys.stderr)

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    md = synthesize(
        persistent_root=pr,
        gateway=args.gateway,
        model=args.model,
        team_key=team_key,
    )
    out_path.write_text(md)
    print(f"coherence-synthesis → {out_path}")
    print(f"  size: {len(md)} bytes")


def main():
    ap = argparse.ArgumentParser(prog="coherence_synthesizer.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    aps = sub.add_parser("synthesize")
    aps.add_argument("--persistent-root", required=True)
    aps.add_argument("--gateway", required=True)
    aps.add_argument("--model", required=True)
    aps.add_argument("--team-key", default=None,
                     help="STRONGLY PREFER env var TELUS_TEAM_KEY. "
                          "--team-key passes the key via argv which "
                          "is visible via /proc; only use for one-off "
                          "tests.")
    aps.add_argument("--out", required=True)
    aps.set_defaults(func=cmd_synthesize)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
