#!/usr/bin/env python3
"""witness_append — append a validated witness record to the public
witness wall, and render the wall as markdown.

The third meta-spec for the jam (Tuesday-friendly). After a team's build
attempt + reviewer findings, a witness record draft (produced by
spec_drafting_loop's stage 6 or by hand) is validated and explicitly
published to the wall by the team via --confirm-publish.

Composition:
- Wraps tools/witness-record-validator.py (existing overclaim detector)
- Reads/writes to wall/witness-records/<timestamp>-<team-id>.md
- "Refusal as record" path: a team can publish a record that says
  "we chose not to surface our offering publicly" — that's a witness
  record too, and it lands on the wall like any other.

Discipline:
- No record reaches the wall without --confirm-publish (one explicit flag
  per publication, no batch mode)
- Every record runs through the overclaim validator first; high-severity
  findings reject the publish, medium/low surface as warnings (publishable
  with operator review)
- Wall rendering is deterministic: alphabetical by timestamp; refused-as-
  records appear with explicit ⟂ marker
- No retroactive edits: once on the wall, corrections happen via NEW
  records that reference the prior record-id

Usage:
  python3 scripts/jam/witness_append.py append <record-file.md> [--confirm-publish] [--wall-root <path>]
  python3 scripts/jam/witness_append.py wall [--wall-root <path>] [--out <wall.md>]
  python3 scripts/jam/witness_append.py audit [--wall-root <path>]
  python3 scripts/jam/witness_append.py validate <record-file.md>

Default wall-root: <kit-root>/wall/

Boundary:
  This is a publication surface for witness records. The wall does not
  certify, approve, authorize, or grant authority. Each record's
  receipt-statement reiterates this discipline.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


KIT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WALL_ROOT = KIT_ROOT / "wall"


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def now_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


# --------------------------------------------------------------------- #
# Validator wrapper                                                     #
# --------------------------------------------------------------------- #

def run_validator(record_path: Path) -> dict:
    """Call tools/witness-record-validator.py on the record. Returns
    {ok, output, returncode}. The existing validator exits 1 on high-
    severity findings, 0 otherwise (medium/low surface but don't reject).

    We re-classify here: exit 1 → reject publish; exit 0 → proceed but
    surface warnings if any."""
    validator = KIT_ROOT / "tools" / "witness-record-validator.py"
    if not validator.exists():
        return {"ok": False, "output": f"validator missing at {validator}", "returncode": 2}
    try:
        result = subprocess.run(
            ["python3", str(validator), str(record_path)],
            capture_output=True, text=True, timeout=30,
        )
        return {
            "ok": result.returncode == 0,
            "output": result.stdout + result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "validator timed out", "returncode": 2}


# --------------------------------------------------------------------- #
# Record parsing                                                        #
# --------------------------------------------------------------------- #

REQUIRED_RECEIPT_PATTERNS = [
    r"this record states what happened",
    r"does not establish.*(authority|approval|certification)",
]


def parse_record(path: Path) -> dict:
    """Parse a witness record markdown file. Returns a dict with
    metadata + body sections. Validates presence of receipt statement."""
    text = path.read_text()

    # Extract any front-matter or bullet metadata
    team_id = None
    date_field = None
    finding = None
    # Common patterns:
    m = re.search(r"^[-*]\s*(team[_\- ]?id|team)\s*:\s*[`']?([\w\-]+)", text, re.M | re.I)
    if m:
        team_id = m.group(2)
    m = re.search(r"^[-*]\s*date\s*:\s*([^\n]+)", text, re.M | re.I)
    if m:
        date_field = m.group(1).strip()
    m = re.search(r"^[-*]\s*finding\s*:\s*([^\n]+)", text, re.M | re.I)
    if m:
        finding = m.group(1).strip().strip("*`")

    # Receipt-statement check (defense in depth — validator catches
    # overclaim language; we additionally require an explicit receipt
    # statement so the wall can't accidentally publish a record without
    # the discipline-affirming closing).
    receipt_present = False
    lower = text.lower()
    if all(re.search(p, lower) for p in REQUIRED_RECEIPT_PATTERNS):
        receipt_present = True

    # Detect refusal-as-record marker
    refusal = bool(re.search(r"\b(we (chose not|declined|refused) to|refusal[- ]as[- ]record|⟂)\b", lower))

    return {
        "team_id": team_id,
        "date": date_field,
        "finding": finding,
        "receipt_present": receipt_present,
        "refusal": refusal,
        "raw_text": text,
        "source_path": str(path),
    }


# --------------------------------------------------------------------- #
# Append + wall operations                                              #
# --------------------------------------------------------------------- #

def append_record(record_path: Path, wall_root: Path, confirm_publish: bool) -> dict:
    record_path = Path(record_path)
    wall_dir = wall_root / "witness-records"
    wall_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_record(record_path)

    # 1. Validator
    validation = run_validator(record_path)

    # 2. Receipt-statement gate
    if not parsed["receipt_present"]:
        return {
            "published": False,
            "reason": ("record is missing the standard receipt statement "
                       "('This record states what happened. It does not "
                       "establish authority, approval, certification, "
                       "legitimacy...'). Add it before publishing."),
            "validator": validation,
        }

    # 3. Validator rejection (high-severity overclaim) blocks publish
    if not validation["ok"]:
        return {
            "published": False,
            "reason": ("validator surfaced high-severity overclaim language; "
                       "see validator output. Edit record + retry."),
            "validator": validation,
        }

    # 4. --confirm-publish required
    if not confirm_publish:
        return {
            "published": False,
            "reason": ("validator clean + receipt statement present; "
                       "re-run with --confirm-publish to actually publish."),
            "validator": validation,
            "parsed": parsed,
        }

    # 5. Compute wall filename: <timestamp>-<team-id>-<short-hash>.md
    ts = now_timestamp()
    team_id = parsed["team_id"] or "unattributed"
    short = hashlib.sha256(parsed["raw_text"].encode()).hexdigest()[:6]
    fname = f"{ts}-{team_id}-{short}.md"
    target = wall_dir / fname

    # 6. Write with metadata footer
    record_with_meta = parsed["raw_text"].rstrip()
    if not record_with_meta.endswith("\n"):
        record_with_meta += "\n"
    record_with_meta += (
        "\n---\n\n"
        f"**Wall metadata** (added by witness_append.py)\n"
        f"- record_id: `{ts}-{team_id}-{short}`\n"
        f"- appended_at: {now_iso()}\n"
        f"- source: `{record_path}`\n"
        f"- refusal_as_record: {parsed['refusal']}\n"
    )
    target.write_text(record_with_meta)

    return {
        "published": True,
        "record_id": f"{ts}-{team_id}-{short}",
        "wall_file": str(target),
        "validator": validation,
        "parsed": parsed,
    }


def render_wall(wall_root: Path, out_path: Path = None) -> str:
    """Render all records under wall/witness-records/ as a single
    markdown wall. Records appear in alphabetical filename order
    (which sorts by timestamp).

    Returns the rendered text. If out_path given, also writes it."""
    wall_dir = wall_root / "witness-records"
    if not wall_dir.exists():
        return "# Witness Wall\n\n(No records yet.)\n"

    files = sorted(wall_dir.glob("*.md"))
    parts = [
        "# Witness Wall",
        "",
        ("> This wall publishes witness records from the Creator Jam. Each "
         "record states what happened. Display does not establish authority, "
         "approval, certification, legitimacy, or reuse permission. Refusal "
         "records appear alongside other records and are honored equally."),
        "",
        f"**Records published**: {len(files)} (rendered {now_iso()})",
        "",
    ]
    if not files:
        parts.append("(No records yet.)")
    for f in files:
        parsed = parse_record(f)
        marker = "⟂" if parsed["refusal"] else "🛶"
        parts.append("---")
        parts.append("")
        parts.append(f"### {marker} `{f.stem}`")
        if parsed["team_id"]:
            parts.append(f"- team: `{parsed['team_id']}`")
        if parsed["date"]:
            parts.append(f"- date: {parsed['date']}")
        if parsed["finding"]:
            parts.append(f"- finding: **{parsed['finding']}**")
        parts.append("")
        parts.append(parsed["raw_text"].rstrip())
        parts.append("")

    rendered = "\n".join(parts) + "\n"
    if out_path:
        out_path.write_text(rendered)
    return rendered


def audit_wall(wall_root: Path) -> dict:
    """Audit every record on the wall. Returns per-file findings."""
    wall_dir = wall_root / "witness-records"
    if not wall_dir.exists():
        return {"ok": True, "records": 0, "findings": []}
    files = sorted(wall_dir.glob("*.md"))
    findings = []
    for f in files:
        parsed = parse_record(f)
        validation = run_validator(f)
        findings.append({
            "file": f.name,
            "receipt_present": parsed["receipt_present"],
            "validator_ok": validation["ok"],
            "refusal_as_record": parsed["refusal"],
        })
    all_ok = all(x["receipt_present"] and x["validator_ok"] for x in findings)
    return {"ok": all_ok, "records": len(files), "findings": findings}


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_append(args):
    result = append_record(
        Path(args.record),
        Path(args.wall_root),
        confirm_publish=args.confirm_publish,
    )
    print(json.dumps(result, indent=2))
    if not result["published"]:
        sys.exit(1)


def cmd_wall(args):
    rendered = render_wall(Path(args.wall_root),
                            out_path=Path(args.out) if args.out else None)
    if args.out:
        print(f"Wrote wall to {args.out}")
    else:
        print(rendered)


def cmd_audit(args):
    result = audit_wall(Path(args.wall_root))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["ok"] else 1)


def cmd_validate(args):
    parsed = parse_record(Path(args.record))
    validation = run_validator(Path(args.record))
    out = {
        "receipt_present": parsed["receipt_present"],
        "refusal_as_record": parsed["refusal"],
        "validator_ok": validation["ok"],
        "validator_output": validation["output"],
    }
    print(json.dumps(out, indent=2))
    sys.exit(0 if (validation["ok"] and parsed["receipt_present"]) else 1)


def main():
    ap = argparse.ArgumentParser(prog="witness_append.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_app = sub.add_parser("append", help="append a record to the wall")
    ap_app.add_argument("record", help="path to the witness record markdown")
    ap_app.add_argument("--confirm-publish", action="store_true",
                        help="REQUIRED to actually publish — without it, "
                             "the record is only validated, not appended")
    ap_app.add_argument("--wall-root", default=str(DEFAULT_WALL_ROOT))
    ap_app.set_defaults(func=cmd_append)

    ap_wall = sub.add_parser("wall", help="render the wall as markdown")
    ap_wall.add_argument("--wall-root", default=str(DEFAULT_WALL_ROOT))
    ap_wall.add_argument("--out", help="write rendered wall to this path "
                                        "(default: print to stdout)")
    ap_wall.set_defaults(func=cmd_wall)

    ap_aud = sub.add_parser("audit", help="audit all records on the wall")
    ap_aud.add_argument("--wall-root", default=str(DEFAULT_WALL_ROOT))
    ap_aud.set_defaults(func=cmd_audit)

    ap_val = sub.add_parser("validate", help="validate a record without "
                                              "appending")
    ap_val.add_argument("record")
    ap_val.set_defaults(func=cmd_validate)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
