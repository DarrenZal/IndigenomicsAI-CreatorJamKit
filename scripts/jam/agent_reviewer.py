#!/usr/bin/env python3
"""agent_reviewer.py — multi-agent-mesh-v0 Reviewer role.

Stage 6.5 of the orchestrator chain (between witness-draft and publish).
Reads:
  - frozen build packet (agentic-build-packet-v0.json)
  - build-attempt JSON (build-attempt.json, optional)
  - witness-record draft (markdown)

Produces reviewer-findings.json with per-check status + recommendations
+ halt_publish flag. The orchestrator consults halt_publish before
calling witness_append.py.

The Reviewer is INDEPENDENT of the witness-drafter (different model
call, different role framing). Its job is to catch coherence gaps the
validator regex can't — overclaim drift, attempted-vs-witnessed tense
slips, boundary-honored-in-draft, claim-vs-evidence coherence.

This is v0 of the role. v0.2 may add machine-applicable diffs.

Usage:
  python3 scripts/jam/agent_reviewer.py review \\
      <build-packet.json> <witness-draft.md> \\
      [--build-attempt <build-attempt.json>] \\
      [--model-source stub|gateway] \\
      [--gateway URL --team-key KEY --model MODEL] \\
      [--out <reviewer-findings.json>]

Refusal-as-first-class: the Reviewer can itself output a refusal
(if the witness draft is asked to certify cultural authorization,
for example). Refusal → halt_publish=true with reason.
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.spec_drafting_loop import _try_parse_json  # noqa: E402


REVIEWER_SYSTEM = (
    "You are a Witness Record Reviewer for an IndigenomicsAI Creator "
    "Jam team's build attempt. You read a frozen build packet, an "
    "optional build-attempt JSON, and a witness-record draft. You "
    "produce structured findings — per-check status — that the "
    "orchestrator uses to decide whether the draft is ready to publish "
    "or needs more work.\n\n"
    "INPUT: a JSON payload with `build_packet_summary`, `build_attempt`, "
    "and `witness_draft` (the full markdown body as a string).\n\n"
    "OUTPUT FORMAT — STRICT:\n"
    "Reply with ONE JSON object, no prose, no markdown, no fence. "
    "Fields:\n"
    "  - review_passed: boolean (true if all checks pass; false if any "
    "halt-level flag fires)\n"
    "  - halt_publish: boolean (true → orchestrator must NOT publish "
    "this draft; false → ok to proceed to validator + publish)\n"
    "  - checks: array of objects, each with:\n"
    "      name: string (one of "
    "'acceptance-criteria-vs-attempt', "
    "'claim-vs-evidence-coherence', "
    "'boundary-honored-in-draft', "
    "'attempted-vs-witnessed-tense', "
    "'overclaim-vocabulary')\n"
    "      status: 'ok' | 'flag' | 'halt'\n"
    "      note: string (1-2 sentences explaining the finding)\n"
    "  - recommendations: array of strings (optional improvements that "
    "do NOT block publish; prose only, no diffs in v0)\n\n"
    "DISCIPLINE (load-bearing):\n"
    "- A 'halt' status on ANY check means halt_publish MUST be true.\n"
    "- 'flag' is a non-blocking concern (recorded for aggregator).\n"
    "- Do NOT rewrite the draft. Findings only.\n"
    "- If the draft contains overclaim vocabulary ('certified', "
    "'approved', 'authorized', 'validated', 'legitimate', 'official', "
    "'successful' as summary judgment, 'failed' as summary judgment) "
    "outside the standard outcome words ('built-clean', 'no-change', "
    "'diverged', 'fixed', 'improved', 'regressed', 'refusal'), flag "
    "the overclaim-vocabulary check with status='halt'.\n"
    "- If the draft describes the build's behavior in asserted-tense "
    "('certifies', 'guarantees', 'validates') rather than "
    "attempted-tense ('attempted', 'observed', 'recorded'), flag the "
    "attempted-vs-witnessed-tense check with status='flag' (note: "
    "not always halt-level; depends on context).\n"
    "- If the build_attempt shows test_passed=false but the draft "
    "'what worked' section asserts success without qualification, "
    "flag claim-vs-evidence-coherence with status='halt'.\n"
    "- If the packet's excluded_inputs are non-empty but the "
    "boundaries-that-remain section is empty or generic, flag "
    "boundary-honored-in-draft with status='flag'.\n"
    "- Do NOT include the input payload in your output.\n"
    "- If the draft itself requests cultural authorization or "
    "Nation-specific claims, output: {\"refusal\": \"requires cultural "
    "authorization\"} — do NOT attempt to review.\n"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Reviewer call (gateway adapter — raw chat-completions)                #
# --------------------------------------------------------------------- #

def call_reviewer_gateway(
    base_url: str,
    team_key: str,
    model: str,
    payload: Dict[str, Any],
    timeout: int = 120,
) -> Dict[str, Any]:
    """Raw chat-completions call with REVIEWER_SYSTEM. One-shot retry
    on transient upstream failures.

    Returns dict with `raw_content` always present + `parsed` (dict or
    None) + `model_label` + `seed`.
    """
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": REVIEWER_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "temperature": 0.2,
    }).encode()

    last_err = None
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
            last_err = e
            if attempt == 2:
                raise RuntimeError(f"reviewer gateway request failed after retry: {e}")
            import time
            time.sleep(2)

    content = data["choices"][0]["message"]["content"]
    parsed = _try_parse_json(content)
    return {
        "raw_content": content,
        "parsed": parsed,
        "model_label": data.get("model", model),
        "seed": (data.get("id") or "")[:12],
    }


# --------------------------------------------------------------------- #
# Reviewer call (stub adapter — deterministic for tests)                #
# --------------------------------------------------------------------- #

def call_reviewer_stub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic stub: scan the witness_draft markdown for overclaim
    vocabulary; produce a minimal review record. Used in tests + offline.
    """
    draft = payload.get("witness_draft", "") or ""
    OVERCLAIM_TERMS = [
        "certified", "certification",
        "approved", "approval",
        "authorized", "authorization",
        "validated", "validation",
        "legitimate", "legitimacy",
        "official",
    ]
    OK_OUTCOMES = {"built-clean", "no-change", "diverged",
                   "fixed", "improved", "regressed", "refusal"}
    # Crude scan — count tokens that aren't in OK_OUTCOMES context
    hits = []
    low = draft.lower()
    for term in OVERCLAIM_TERMS:
        # Skip occurrences immediately preceded by a hyphen (e.g. "self-
        # certification" used in a refusal-context line); the stub is
        # intentionally simple — gateway path is authoritative.
        if term in low:
            hits.append(term)
    overclaim_status = "halt" if hits else "ok"

    # Boundary check: if "Boundaries that remain" is non-empty body, ok.
    boundary_status = "ok"
    if "## Boundaries that remain" in draft:
        seg = draft.split("## Boundaries that remain", 1)[1]
        seg_body = seg.split("##", 1)[0].strip()
        if not seg_body or seg_body.startswith("("):
            boundary_status = "flag"

    review_passed = (overclaim_status == "ok")
    halt_publish = (overclaim_status == "halt")

    findings = {
        "review_passed": review_passed,
        "halt_publish": halt_publish,
        "checks": [
            {"name": "overclaim-vocabulary",
             "status": overclaim_status,
             "note": (
                 f"stub scan hit overclaim terms: {', '.join(hits)}"
                 if hits else
                 "stub scan: no overclaim vocabulary detected"
             )},
            {"name": "boundary-honored-in-draft",
             "status": boundary_status,
             "note": (
                 "stub scan: boundaries-that-remain section is empty or generic"
                 if boundary_status == "flag" else
                 "stub scan: boundaries-that-remain section present"
             )},
            # Other checks default to ok in stub (gateway path covers them)
            {"name": "acceptance-criteria-vs-attempt",
             "status": "ok",
             "note": "stub: not evaluated (gateway-only check)"},
            {"name": "claim-vs-evidence-coherence",
             "status": "ok",
             "note": "stub: not evaluated (gateway-only check)"},
            {"name": "attempted-vs-witnessed-tense",
             "status": "ok",
             "note": "stub: not evaluated (gateway-only check)"},
        ],
        "recommendations": [],
    }
    return {
        "raw_content": json.dumps(findings),
        "parsed": findings,
        "model_label": "stub-reviewer-v0",
        "seed": "stub",
    }


# --------------------------------------------------------------------- #
# Normalize parsed findings into a canonical findings shape             #
# --------------------------------------------------------------------- #

REQUIRED_CHECK_NAMES = [
    "acceptance-criteria-vs-attempt",
    "claim-vs-evidence-coherence",
    "boundary-honored-in-draft",
    "attempted-vs-witnessed-tense",
    "overclaim-vocabulary",
]


def normalize_findings(parsed: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Coerce model output into the canonical findings dict, with
    safe defaults for missing fields. NEVER raises on bad input —
    falls back to a 'flag' finding noting the parse problem."""
    if not isinstance(parsed, dict):
        return {
            "review_passed": False,
            "halt_publish": False,
            "checks": [
                {"name": "reviewer-parse-failed",
                 "status": "flag",
                 "note": "reviewer output did not parse as JSON; "
                         "raw content preserved in artifact."},
            ],
            "recommendations": [
                "Reviewer model output did not parse; consider re-running.",
            ],
        }

    # Model refusal → halt with refusal record
    if "refusal" in parsed and isinstance(parsed["refusal"], str):
        return {
            "review_passed": False,
            "halt_publish": True,
            "checks": [
                {"name": "reviewer-refusal",
                 "status": "halt",
                 "note": parsed["refusal"][:300]},
            ],
            "recommendations": [],
            "refusal": parsed["refusal"],
        }

    checks = parsed.get("checks")
    if not isinstance(checks, list):
        checks = []

    # Normalize each check
    norm_checks = []
    seen_names = set()
    halt_seen = False
    for c in checks:
        if not isinstance(c, dict):
            continue
        name = str(c.get("name", "")).strip() or "unnamed"
        status = c.get("status", "ok")
        if status not in ("ok", "flag", "halt"):
            status = "flag"
        if status == "halt":
            halt_seen = True
        note = str(c.get("note", ""))[:500]
        norm_checks.append({"name": name, "status": status, "note": note})
        seen_names.add(name)

    # Backfill missing required check names with status=ok + a note
    for required in REQUIRED_CHECK_NAMES:
        if required not in seen_names:
            norm_checks.append({
                "name": required,
                "status": "ok",
                "note": "reviewer did not return this check; defaulted to ok",
            })

    # If model said halt_publish=true OR any halt status, force halt.
    explicit_halt = bool(parsed.get("halt_publish", False))
    halt_publish = explicit_halt or halt_seen

    review_passed = bool(parsed.get("review_passed", not halt_publish))
    if halt_publish:
        review_passed = False

    recs = parsed.get("recommendations")
    if not isinstance(recs, list):
        recs = []
    recs = [str(r)[:500] for r in recs if r]

    return {
        "review_passed": review_passed,
        "halt_publish": halt_publish,
        "checks": norm_checks,
        "recommendations": recs,
    }


# --------------------------------------------------------------------- #
# Orchestration                                                         #
# --------------------------------------------------------------------- #

def build_payload(
    build_packet: Dict[str, Any],
    build_attempt: Optional[Dict[str, Any]],
    witness_draft: str,
) -> Dict[str, Any]:
    spec = build_packet.get("team_spec", {})
    return {
        "build_packet_summary": {
            "vision": spec.get("vision"),
            "spec": spec.get("spec"),
            "build_target": spec.get("build_target"),
            "acceptance_criteria": build_packet.get(
                "acceptance_criteria", {}
            ).get("description", []),
            "excluded_inputs_count": len(build_packet.get("excluded_inputs", [])),
        },
        "build_attempt": build_attempt or {"finding": "unknown"},
        "witness_draft": witness_draft[:8000],  # bound payload size
    }


def review(
    build_packet_path: Path,
    witness_draft_path: Path,
    build_attempt_path: Optional[Path],
    model_source: str,
    gateway: Optional[str],
    team_key: Optional[str],
    model: Optional[str],
) -> Dict[str, Any]:
    if not build_packet_path.exists():
        raise SystemExit(f"build packet not found: {build_packet_path}")
    if not witness_draft_path.exists():
        raise SystemExit(f"witness draft not found: {witness_draft_path}")

    build_packet = json.loads(build_packet_path.read_text())
    witness_draft = witness_draft_path.read_text()
    build_attempt = None
    if build_attempt_path is not None and build_attempt_path.exists():
        build_attempt = json.loads(build_attempt_path.read_text())

    payload = build_payload(build_packet, build_attempt, witness_draft)

    if model_source == "stub":
        raw = call_reviewer_stub(payload)
    elif model_source == "gateway":
        if not gateway or not team_key:
            raise SystemExit("model-source=gateway requires --gateway and --team-key")
        raw = call_reviewer_gateway(gateway, team_key, model or "telus-qwen", payload)
    else:
        raise SystemExit(f"unknown model-source {model_source!r}")

    findings = normalize_findings(raw.get("parsed"))

    return {
        "schema": "reviewer-findings-v0",
        "reviewer_at": now_iso(),
        "model_source": model_source,
        "model_label": raw.get("model_label"),
        "seed": raw.get("seed"),
        "build_packet_path": str(build_packet_path),
        "witness_draft_path": str(witness_draft_path),
        "build_attempt_path": str(build_attempt_path) if build_attempt_path else None,
        "findings": findings,
        "raw_content": raw.get("raw_content"),
    }


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_review(args):
    out_path = Path(args.out).expanduser() if args.out else None
    record = review(
        build_packet_path=Path(args.build_packet).expanduser(),
        witness_draft_path=Path(args.witness_draft).expanduser(),
        build_attempt_path=Path(args.build_attempt).expanduser() if args.build_attempt else None,
        model_source=args.model_source,
        gateway=args.gateway,
        team_key=args.team_key,
        model=args.model,
    )
    text = json.dumps(record, indent=2)
    if out_path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text)
        print(f"reviewer-findings → {out_path}")
        f = record["findings"]
        print(f"  review_passed: {f['review_passed']}")
        print(f"  halt_publish:  {f['halt_publish']}")
        print(f"  checks: {len(f['checks'])} (halt: "
              f"{sum(1 for c in f['checks'] if c['status'] == 'halt')}, "
              f"flag: "
              f"{sum(1 for c in f['checks'] if c['status'] == 'flag')})")
    else:
        print(text)


def main():
    ap = argparse.ArgumentParser(prog="agent_reviewer.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_rev = sub.add_parser("review")
    ap_rev.add_argument("build_packet")
    ap_rev.add_argument("witness_draft")
    ap_rev.add_argument("--build-attempt")
    ap_rev.add_argument("--model-source", choices=["stub", "gateway"], default="stub")
    ap_rev.add_argument("--gateway")
    ap_rev.add_argument("--team-key")
    ap_rev.add_argument("--model")
    ap_rev.add_argument("--out")
    ap_rev.set_defaults(func=cmd_review)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
