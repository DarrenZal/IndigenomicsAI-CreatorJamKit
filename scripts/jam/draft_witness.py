#!/usr/bin/env python3
"""draft_witness.py — stage 6 of the spec-drafting-loop chain.

After a team has frozen a build packet (via spec_drafting_loop.py) and
attempted a build (manually or via TELUS lane), this CLI takes:
  - The frozen build packet
  - A build-attempt result (what actually happened — finding + outcome)
  - Optional reviewer findings (per-check pass/fail)

...and produces a witness-record draft via Prompt 3 (witness-drafter)
through gateway OR stub adapter. The draft must include the standard
receipt statement and avoid overclaim language (the kit's
tools/witness-record-validator.py is invoked as a final gate).

This is NOT autonomous publication — the output is a DRAFT. The team
edits + reviews before running scripts/jam/witness_append.py.

Composition:
  offering -> spec_drafting_loop -> frozen build packet
                                       |
                                       v
                              (build attempt, external)
                                       |
                                       v
  build outputs -> draft_witness.py -> witness record DRAFT
                                       |
                                       v
                            (team review + edits)
                                       |
                                       v
                    witness_append.py --confirm-publish -> wall

Usage:
  python3 scripts/jam/draft_witness.py draft <build-packet.json> \\
      [--build-attempt <build-attempt.json>] \\
      [--reviewer-findings <findings.json>] \\
      [--finding built-clean|fixed|improved|no-change|regressed|failed|refusal] \\
      [--model-source stub|gateway] \\
      [--gateway URL --team-key KEY --model MODEL] \\
      [--out <witness-record.md>]

  python3 scripts/jam/draft_witness.py validate <witness-record.md>

Discipline:
  - Output is a DRAFT. Team review remains the authoritative voice.
  - Validator (overclaim + receipt-statement) is the final gate.
  - "Refusal-as-record" is a first-class finding (--finding refusal).
  - Stub mode is offline + deterministic for tests + offline use.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Make `jam.stub_model` importable when running from kit root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.stub_model import StubModelAdapter  # noqa: E402
from jam.spec_drafting_loop import (  # noqa: E402
    GatewayModelAdapter,
    make_adapter,
    _try_parse_json,
)


KIT_ROOT = Path(__file__).resolve().parents[2]


VALID_FINDINGS = {
    "built-clean",
    "fixed",
    "improved",
    "no-change",
    "regressed",
    "failed",
    "refusal",  # refusal-as-record path
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


# --------------------------------------------------------------------- #
# Witness-record markdown rendering                                     #
# --------------------------------------------------------------------- #

RECEIPT_STATEMENT = (
    "This record states what happened. It does not establish authority, "
    "approval, certification, legitimacy, community consent, or readiness "
    "for reuse."
)


def render_witness_record_md(
    *,
    team_name: str,
    team_id: str,
    site: str,
    finding: str,
    build_packet: Dict[str, Any],
    build_attempt: Optional[Dict[str, Any]],
    reviewer_findings: Optional[Dict[str, Any]],
    drafted_fields: Dict[str, str],
) -> str:
    """Render the witness-record markdown.

    drafted_fields: dict with keys 'what_we_brought', 'what_we_attempted',
    'what_worked', 'what_did_not_work', 'what_we_learned',
    'boundaries_that_remain' — usually populated by Prompt 3, but if the
    model output is missing fields we fall back to packet-derived
    defaults so the output is never null."""
    spec = build_packet.get("team_spec", {})
    target_name = spec.get("build_target") or "build target"
    excluded = build_packet.get("excluded_inputs", [])

    def field(k: str, default: str) -> str:
        v = drafted_fields.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        return default

    boundaries_that_remain = field(
        "boundaries_that_remain",
        (
            "The boundaries named in the team's submission as marker-only / "
            "not-for-AI / not-for-reuse / private / protected were not "
            "given to the build attempt and were not computed on."
        )
        if excluded
        else "No marker-only or protected content was named for this build attempt.",
    )

    lines = [
        f"# Canoe Landing / Witness Record — {team_name}",
        "",
        f"- team-id: {team_id}",
        f"- date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        f"- finding: **{finding}**",
        "",
        "## What we brought",
        "",
        field("what_we_brought", spec.get("vision") or "(team vision not specified)"),
        "",
        "## What we attempted",
        "",
        field(
            "what_we_attempted",
            f"A build attempt on the frozen build packet. Build target: {target_name}.",
        ),
        "",
        "## What worked",
        "",
        field(
            "what_worked",
            "(team to fill — what passed acceptance, what behaved as designed)",
        ),
        "",
        "## What did not work / what broke",
        "",
        field(
            "what_did_not_work",
            "(team to fill — what failed, what surprised)",
        ),
        "",
        "## What we learned",
        "",
        field(
            "what_we_learned",
            "(team to fill — what the attempt taught us)",
        ),
        "",
        "## Boundaries that remain",
        "",
        boundaries_that_remain,
        "",
        "## Receipt",
        "",
        RECEIPT_STATEMENT,
        "",
    ]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------- #
# Prompt 3 call + result hoisting                                       #
# --------------------------------------------------------------------- #

def call_prompt3(
    adapter,
    build_packet: Dict[str, Any],
    build_attempt: Optional[Dict[str, Any]],
    reviewer_findings: Optional[Dict[str, Any]],
    finding: str,
) -> Dict[str, Any]:
    """Call Prompt 3 (witness-drafter) and return parsed fields.

    For stub adapter: returns dict directly with witness_record_draft.
    For gateway adapter: structured-parses raw_content.

    Returns a dict with these string fields (some may be empty):
        what_we_brought, what_we_attempted, what_worked,
        what_did_not_work, what_we_learned, boundaries_that_remain.
    """
    spec = build_packet.get("team_spec", {})
    payload = {
        "team": {"name": spec.get("team_name", "unknown")},
        "build_outcome": finding,
        "build_packet_summary": {
            "vision": spec.get("vision"),
            "spec": spec.get("spec"),
            "build_target": spec.get("build_target"),
            "acceptance_criteria": build_packet.get(
                "acceptance_criteria", {}
            ).get("description", []),
            "excluded_inputs_count": len(build_packet.get("excluded_inputs", [])),
        },
        "build_attempt": build_attempt or {"finding": finding},
        "reviewer_findings": reviewer_findings or {},
    }

    raw = adapter.complete("witness-drafter", payload)

    # Stub adapter: returns dict with `witness_record_draft` key directly.
    if raw.get("model_source") == "stub":
        wrd = raw.get("witness_record_draft", {})
        return {
            "what_we_brought": wrd.get("what_we_brought", ""),
            "what_we_attempted": wrd.get("what_we_attempted", ""),
            "what_worked": "",  # stub doesn't split worked/did-not-work
            "what_did_not_work": "",
            "what_we_learned": wrd.get("what_happened", ""),
            "boundaries_that_remain": "",
            "model_source": "stub",
            "_raw": raw,
        }

    # Gateway adapter: also already structured-parsed in v0.1, but
    # double-check the witness_record_draft key.
    wrd = raw.get("witness_record_draft")
    if isinstance(wrd, dict):
        return {
            "what_we_brought": wrd.get("what_we_brought", ""),
            "what_we_attempted": wrd.get("what_we_attempted", ""),
            "what_worked": wrd.get("what_worked", ""),
            "what_did_not_work": wrd.get("what_did_not_work", ""),
            "what_we_learned": wrd.get("what_we_learned", ""),
            "boundaries_that_remain": wrd.get("boundaries_that_remain", ""),
            "model_source": raw.get("model_source", "gateway"),
            "_raw": raw,
        }

    # Fallback: try parsing raw_content directly
    raw_content = raw.get("raw_content", "")
    parsed = _try_parse_json(raw_content) or {}
    return {
        "what_we_brought": parsed.get("what_we_brought", ""),
        "what_we_attempted": parsed.get("what_we_attempted", ""),
        "what_worked": parsed.get("what_worked", ""),
        "what_did_not_work": parsed.get("what_did_not_work", ""),
        "what_we_learned": parsed.get("what_we_learned", ""),
        "boundaries_that_remain": parsed.get("boundaries_that_remain", ""),
        "model_source": raw.get("model_source", "gateway"),
        "_raw": raw,
    }


# --------------------------------------------------------------------- #
# Validator wrap                                                         #
# --------------------------------------------------------------------- #

def run_validator(record_path: Path) -> Dict[str, Any]:
    """Call tools/witness-record-validator.py on the draft."""
    validator = KIT_ROOT / "tools" / "witness-record-validator.py"
    if not validator.exists():
        return {"ok": False, "output": f"validator missing at {validator}", "returncode": 2}
    try:
        result = subprocess.run(
            ["python3", str(validator), str(record_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "ok": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "validator timed out", "returncode": 2}


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_draft(args):
    packet_path = Path(args.build_packet)
    if not packet_path.exists():
        print(f"error: build packet not found: {packet_path}", file=sys.stderr)
        sys.exit(2)
    build_packet = load_json(packet_path)

    build_attempt = None
    if args.build_attempt:
        build_attempt = load_json(Path(args.build_attempt))

    reviewer_findings = None
    if args.reviewer_findings:
        reviewer_findings = load_json(Path(args.reviewer_findings))

    finding = args.finding
    if finding not in VALID_FINDINGS:
        print(
            f"error: --finding must be one of {sorted(VALID_FINDINGS)}",
            file=sys.stderr,
        )
        sys.exit(2)

    adapter = make_adapter(args.model_source, args.gateway, args.team_key, args.model)

    drafted = call_prompt3(adapter, build_packet, build_attempt, reviewer_findings, finding)

    # Resolve team-name + team-id from packet
    spec = build_packet.get("team_spec", {})
    team_name = spec.get("team_name", args.team_name or "unknown-team")
    team_id = args.team_id or "team-" + re.sub(r"[^a-z0-9]+", "-", team_name.lower()).strip("-")
    site = spec.get("site", "other")

    md = render_witness_record_md(
        team_name=team_name,
        team_id=team_id,
        site=site,
        finding=finding,
        build_packet=build_packet,
        build_attempt=build_attempt,
        reviewer_findings=reviewer_findings,
        drafted_fields=drafted,
    )

    out_path = Path(args.out) if args.out else Path(
        f"witness-record-draft-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.md"
    )
    out_path.write_text(md)

    # Run the validator immediately so the team sees overclaim issues
    # before they hand-edit.
    validation = run_validator(out_path)

    print(json.dumps({
        "drafted": True,
        "out_path": str(out_path),
        "model_source": drafted.get("model_source"),
        "validator_ok": validation["ok"],
        "validator_output": validation["output"][:500],
        "next_step": (
            f"Open {out_path}, fill any 'team to fill' placeholders, "
            "review for accuracy + voice, then publish via "
            "scripts/jam/witness_append.py append <path> --confirm-publish"
        ),
    }, indent=2))


def cmd_validate(args):
    result = run_validator(Path(args.record))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["ok"] else 1)


def main():
    ap = argparse.ArgumentParser(prog="draft_witness.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_draft = sub.add_parser("draft", help="draft a witness record from build outputs")
    ap_draft.add_argument("build_packet", help="path to frozen agentic-build-packet-v0.json")
    ap_draft.add_argument("--build-attempt", help="path to build-attempt.json (optional)")
    ap_draft.add_argument("--reviewer-findings", help="path to reviewer-findings.json (optional)")
    ap_draft.add_argument(
        "--finding",
        choices=sorted(VALID_FINDINGS),
        default="built-clean",
        help="overall build finding",
    )
    ap_draft.add_argument("--model-source", choices=["stub", "gateway"], default="stub")
    ap_draft.add_argument("--gateway", help="gateway base URL")
    ap_draft.add_argument("--team-key", help="gateway team API key")
    ap_draft.add_argument("--model", help="gateway model id")
    ap_draft.add_argument("--team-name", help="override team name (otherwise from packet)")
    ap_draft.add_argument("--team-id", help="override team id (otherwise derived)")
    ap_draft.add_argument("--out", help="output path for the draft markdown")
    ap_draft.set_defaults(func=cmd_draft)

    ap_val = sub.add_parser("validate", help="validate a witness record draft")
    ap_val.add_argument("record")
    ap_val.set_defaults(func=cmd_validate)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
