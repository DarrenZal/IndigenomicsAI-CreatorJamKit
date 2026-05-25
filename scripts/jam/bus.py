#!/usr/bin/env python3
"""agent-coordination-bus — file-based JSONL bus for the 7 wire types
defined in specs/coordination-protocol-v0.md.

A jam-day mentor + participant tool. Provides:
  - validated message envelope + per-type payloads
  - append-only JSONL log per team (bus/teams/<team-id>.jsonl)
  - append-only global log (bus/global.jsonl)
  - validator that rejects refusal-boundary violations
  - audit subcommand verifying append-only invariant

Discipline:
  - Refusal is a complete outcome (share_refuse with no reason is valid).
  - Boundary markers cannot be transitively shared via share_grant. Even
    if Team B grants a share_request, marker-only / protected content is
    rejected by validation before storage.
  - Aggregated consent is rejected: each share_request is its own decision.
  - Withdrawals require explicit acknowledgement from every receiving team
    before the propagation chain is closed.
  - witness_observe MUST set not_an_authority_claim: true (observations
    are observations; the bus does not certify or authorize anything).

Usage:
  python3 scripts/jam/bus.py init <bus-root> --team <team-id>
  python3 scripts/jam/bus.py post <bus-root> <message-json-file>
  python3 scripts/jam/bus.py read <bus-root> [--team <team-id>] [--global]
  python3 scripts/jam/bus.py audit <bus-root> [--team <team-id>]
  python3 scripts/jam/bus.py validate <message-json-file>
  python3 scripts/jam/bus.py replay <bus-root> <demo-dir>

Storage layout under <bus-root>:
  bus/teams/<team-id>.jsonl
  bus/global.jsonl
  bus/meta.json   # bus-level metadata (created_at, version)

Boundary on claims:
  This is a coordination substrate that records what was said between
  agents. It does not certify, authorize, or grant authority to any
  message. Refusal-boundary checks reject obvious leaks; downstream
  human stewards remain the deciding voice.
"""

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


VALID_MESSAGE_TYPES = {
    "share_request",
    "share_grant",
    "share_refuse",
    "withdraw_notice",
    "boundary_marker",
    "composition_propose",
    "witness_observe",
}

VALID_AGENT_ROLES = {
    "spec-drafting",
    "boundary-checker",
    "witness-drafter",
    "mediator",
    "other",
}

VALID_CONTENT_KINDS = {
    "offering",
    "spec_fragment",
    "boundary_marker",
    "acceptance_criterion",
    "refusal_log_entry",
    "other",
}

VALID_BOUNDARY_TYPES = {
    "marker-only",
    "not-for-AI",
    "not-for-reuse",
    "private",
    "protected",
    "review-required",
}

# Heuristic markers that suggest content is protected / marker-only.
# Used to reject share_request payloads that attempt to leak protected
# content through non-boundary_marker channels.
PROTECTED_LEAK_MARKERS = {
    "[PROTECTED]",
    "[MARKER_ONLY]",
    "[NOT_FOR_AI]",
    "[NOT_FOR_REUSE]",
    "[PRIVATE]",
}


# --------------------------------------------------------------------- #
# Validation                                                            #
# --------------------------------------------------------------------- #

class ValidationError(Exception):
    """Raised when a message violates the protocol."""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _require_keys(d, keys, ctx):
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValidationError(f"{ctx}: missing required keys: {missing}")


def validate_envelope(msg):
    _require_keys(
        msg,
        ["message_id", "created_at", "from_agent", "to_agent",
         "message_type", "references", "signature"],
        "envelope",
    )
    if msg["message_type"] not in VALID_MESSAGE_TYPES:
        raise ValidationError(
            f"envelope: unknown message_type {msg['message_type']!r}; "
            f"must be one of {sorted(VALID_MESSAGE_TYPES)}"
        )

    for who in ("from_agent", "to_agent"):
        sub = msg[who]
        if not isinstance(sub, dict):
            raise ValidationError(f"envelope: {who} must be an object")
        _require_keys(sub, ["team_id"], f"envelope.{who}")
        if "agent_role" in sub and sub["agent_role"] not in VALID_AGENT_ROLES:
            raise ValidationError(
                f"envelope.{who}.agent_role: {sub['agent_role']!r} not in {sorted(VALID_AGENT_ROLES)}"
            )

    if not isinstance(msg["references"], list):
        raise ValidationError("envelope: references must be a list")


def _check_protected_leak(text, ctx):
    if not isinstance(text, str):
        return
    upper = text.upper()
    for marker in PROTECTED_LEAK_MARKERS:
        if marker in upper:
            raise ValidationError(
                f"{ctx}: contains protected-content leak marker {marker!r}; "
                "protected content cannot travel in this payload type. "
                "Use a boundary_marker message instead."
            )


def validate_share_request(payload):
    _require_keys(payload, ["what", "why", "consent_terms"], "share_request")
    what = payload["what"]
    _require_keys(what, ["content_kind", "preview"], "share_request.what")
    if what["content_kind"] not in VALID_CONTENT_KINDS:
        raise ValidationError(
            f"share_request.what.content_kind: {what['content_kind']!r} not in {sorted(VALID_CONTENT_KINDS)}"
        )
    preview = what["preview"]
    _require_keys(preview, ["mode", "body"], "share_request.what.preview")
    if preview["mode"] not in {"cleared_text", "paraphrased", "marker_only"}:
        raise ValidationError(
            f"share_request.what.preview.mode: {preview['mode']!r} "
            "must be cleared_text | paraphrased | marker_only"
        )
    # If marker-only, body MUST NOT contain protected content (heuristic).
    if preview["mode"] == "marker_only":
        _check_protected_leak(preview["body"], "share_request.what.preview.body (marker_only)")

    why = payload["why"]
    _require_keys(why, ["intent"], "share_request.why")
    if not isinstance(why["intent"], str) or len(why["intent"].strip()) < 5:
        raise ValidationError(
            "share_request.why.intent: must be a concrete intent (>=5 chars); "
            "vague intents fail validation"
        )

    consent = payload["consent_terms"]
    _require_keys(consent, ["display_scope", "ai_input_scope", "reuse_scope"], "share_request.consent_terms")
    if consent["display_scope"] not in {"whole", "partial", "spoken-only", "none"}:
        raise ValidationError(f"share_request.consent_terms.display_scope invalid")
    if consent["ai_input_scope"] not in {"whole", "partial", "none"}:
        raise ValidationError(f"share_request.consent_terms.ai_input_scope invalid")
    if consent["reuse_scope"] not in {"not-granted", "ask-first", "team-only", "public-ok"}:
        raise ValidationError(f"share_request.consent_terms.reuse_scope invalid")


def validate_share_grant(msg, payload):
    if not msg["references"]:
        raise ValidationError("share_grant: references must include the share_request message_id")
    _require_keys(payload, ["granted"], "share_grant")
    if payload["granted"] is not True:
        raise ValidationError("share_grant: granted must be True; use share_refuse to decline")


def validate_share_refuse(msg, payload):
    if not msg["references"]:
        raise ValidationError("share_refuse: references must include the share_request message_id")
    _require_keys(payload, ["granted"], "share_refuse")
    if payload["granted"] is not False:
        raise ValidationError("share_refuse: granted must be False")
    # reason is OPTIONAL — refusals do not require justification.


def validate_withdraw_notice(msg, payload):
    if not msg["references"]:
        raise ValidationError("withdraw_notice: references must include prior share_request / share_grant message_ids")
    _require_keys(
        payload,
        ["withdrawn_record_ids", "acknowledgment_required_from"],
        "withdraw_notice",
    )
    if not payload["withdrawn_record_ids"]:
        raise ValidationError("withdraw_notice.withdrawn_record_ids: must not be empty")
    if not payload["acknowledgment_required_from"]:
        raise ValidationError(
            "withdraw_notice.acknowledgment_required_from: must list every "
            "receiving team; withdrawals cannot be silently absorbed"
        )


def validate_boundary_marker(payload):
    _require_keys(
        payload,
        ["label", "boundary_type", "marker_text", "disallowed_use"],
        "boundary_marker",
    )
    if payload["boundary_type"] not in VALID_BOUNDARY_TYPES:
        raise ValidationError(
            f"boundary_marker.boundary_type: {payload['boundary_type']!r} "
            f"not in {sorted(VALID_BOUNDARY_TYPES)}"
        )
    # marker_text MUST NOT contain protected content.
    _check_protected_leak(payload["marker_text"], "boundary_marker.marker_text")


def validate_composition_propose(payload):
    _require_keys(
        payload,
        ["proposed_bundle_id", "composes", "acceptance_required_from"],
        "composition_propose",
    )
    if len(payload["composes"]) < 2:
        raise ValidationError(
            "composition_propose.composes: must list at least 2 teams' submissions"
        )
    if not payload["acceptance_required_from"]:
        raise ValidationError(
            "composition_propose.acceptance_required_from: must list every team "
            "whose submission is being composed; aggregated consent is rejected"
        )


def validate_witness_observe(payload):
    _require_keys(payload, ["observed", "not_an_authority_claim", "routing"], "witness_observe")
    if payload["not_an_authority_claim"] is not True:
        raise ValidationError(
            "witness_observe: not_an_authority_claim must be True; observations "
            "are not authority claims"
        )
    observed = payload["observed"]
    _require_keys(observed, ["kind", "body"], "witness_observe.observed")


PAYLOAD_VALIDATORS = {
    "share_request": lambda m, p: validate_share_request(p),
    "share_grant": validate_share_grant,
    "share_refuse": validate_share_refuse,
    "withdraw_notice": validate_withdraw_notice,
    "boundary_marker": lambda m, p: validate_boundary_marker(p),
    "composition_propose": lambda m, p: validate_composition_propose(p),
    "witness_observe": lambda m, p: validate_witness_observe(p),
}


def validate_message(msg):
    """Validate a complete message. Raises ValidationError on any violation."""
    if not isinstance(msg, dict):
        raise ValidationError("message must be a JSON object")
    validate_envelope(msg)
    payload = msg.get("payload")
    if not isinstance(payload, dict):
        raise ValidationError("message: missing or non-object payload")
    PAYLOAD_VALIDATORS[msg["message_type"]](msg, payload)


# --------------------------------------------------------------------- #
# Storage                                                               #
# --------------------------------------------------------------------- #

def bus_paths(bus_root: Path):
    return {
        "root": bus_root,
        "bus_dir": bus_root / "bus",
        "teams_dir": bus_root / "bus" / "teams",
        "global_log": bus_root / "bus" / "global.jsonl",
        "meta": bus_root / "bus" / "meta.json",
    }


def init_bus(bus_root: Path, team_id: Optional[str] = None):
    paths = bus_paths(bus_root)
    paths["bus_dir"].mkdir(parents=True, exist_ok=True)
    paths["teams_dir"].mkdir(parents=True, exist_ok=True)
    if not paths["meta"].exists():
        paths["meta"].write_text(json.dumps({
            "version": "v0",
            "created_at": now_iso(),
        }, indent=2) + "\n")
    paths["global_log"].touch(exist_ok=True)
    if team_id:
        team_log = paths["teams_dir"] / f"{team_id}.jsonl"
        team_log.touch(exist_ok=True)
    return paths


def append_message(bus_root: Path, msg: dict):
    validate_message(msg)
    paths = bus_paths(bus_root)
    if not paths["bus_dir"].exists():
        raise FileNotFoundError(
            f"bus not initialized at {bus_root}; run `bus.py init {bus_root}` first"
        )
    line = json.dumps(msg, sort_keys=True) + "\n"
    # Append to from_agent's team log + to_agent's team log + global.
    for team in {msg["from_agent"]["team_id"], msg["to_agent"]["team_id"]}:
        team_log = paths["teams_dir"] / f"{team}.jsonl"
        with team_log.open("a") as f:
            f.write(line)
    with paths["global_log"].open("a") as f:
        f.write(line)


def read_log(path: Path):
    if not path.exists():
        return []
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        out.append(json.loads(ln))
    return out


def audit_append_only(path: Path):
    """Sanity-check append-only invariant: every line is a valid JSON object
    and message_ids are unique. We can't fully prove never-modified from
    the file alone, but we surface obvious tampering signals."""
    if not path.exists():
        return {"ok": True, "lines": 0, "unique_message_ids": 0}
    seen_ids = set()
    line_count = 0
    duplicates = []
    for i, ln in enumerate(path.read_text().splitlines(), start=1):
        ln = ln.strip()
        if not ln:
            continue
        line_count += 1
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError as e:
            return {"ok": False, "lines": line_count, "error": f"line {i}: invalid json: {e}"}
        mid = obj.get("message_id")
        if mid in seen_ids:
            duplicates.append(mid)
        seen_ids.add(mid)
    return {
        "ok": len(duplicates) == 0,
        "lines": line_count,
        "unique_message_ids": len(seen_ids),
        "duplicates": duplicates,
    }


# --------------------------------------------------------------------- #
# Message construction helpers                                          #
# --------------------------------------------------------------------- #

def make_envelope(from_team, to_team, message_type, references=None,
                   from_role="spec-drafting", to_role=None, signature_seed=None):
    """Convenience helper for tests + demos."""
    msg_id = str(uuid.uuid4())
    sig = hashlib.sha256(
        (signature_seed or f"{from_team}:{msg_id}").encode()
    ).hexdigest()[:32]
    env = {
        "message_id": msg_id,
        "created_at": now_iso(),
        "from_agent": {"team_id": from_team, "agent_role": from_role},
        "to_agent": {"team_id": to_team},
        "message_type": message_type,
        "references": references or [],
        "signature": sig,
    }
    if to_role:
        env["to_agent"]["agent_role"] = to_role
    return env


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_init(args):
    paths = init_bus(Path(args.bus_root), team_id=args.team)
    print(f"initialized bus at {paths['bus_dir']}")
    if args.team:
        print(f"  team log: {paths['teams_dir'] / (args.team + '.jsonl')}")


def cmd_post(args):
    msg = json.loads(Path(args.message_file).read_text())
    append_message(Path(args.bus_root), msg)
    print(f"posted {msg['message_id']} ({msg['message_type']})")


def cmd_read(args):
    paths = bus_paths(Path(args.bus_root))
    if args.team:
        log = paths["teams_dir"] / f"{args.team}.jsonl"
    elif args.global_log:
        log = paths["global_log"]
    else:
        print("usage: read <bus-root> --team <id> | --global", file=sys.stderr)
        sys.exit(2)
    msgs = read_log(log)
    if args.summary:
        for m in msgs:
            print(f"{m['created_at']}  {m['message_type']:22s}  "
                  f"{m['from_agent']['team_id']} → {m['to_agent']['team_id']}")
    else:
        for m in msgs:
            print(json.dumps(m, indent=2))
            print("---")


def cmd_audit(args):
    paths = bus_paths(Path(args.bus_root))
    if args.team:
        log = paths["teams_dir"] / f"{args.team}.jsonl"
    else:
        log = paths["global_log"]
    result = audit_append_only(log)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["ok"] else 1)


def cmd_validate(args):
    msg = json.loads(Path(args.message_file).read_text())
    try:
        validate_message(msg)
        print(f"ok: {msg['message_id']} ({msg['message_type']})")
    except ValidationError as e:
        print(f"REJECTED: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_replay(args):
    """Replay a demo directory: post every *.json message file in
    sorted order (filenames typically prefix with order, e.g. 01-...)."""
    bus_root = Path(args.bus_root)
    demo_dir = Path(args.demo_dir)
    if not demo_dir.exists():
        print(f"ERROR: demo directory not found: {demo_dir}", file=sys.stderr)
        sys.exit(2)
    init_bus(bus_root)
    files = sorted(demo_dir.glob("*.json"))
    if not files:
        print(f"no .json files under {demo_dir}", file=sys.stderr)
        sys.exit(2)
    posted = 0
    rejected = 0
    for f in files:
        try:
            msg = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            print(f"  {f.name}: bad json: {e}", file=sys.stderr)
            rejected += 1
            continue
        try:
            append_message(bus_root, msg)
            print(f"  {f.name:50s} → posted ({msg['message_type']})")
            posted += 1
        except ValidationError as e:
            # Some demo messages are intentional failure cases.
            expected_fail = "expected-fail" in f.name or "should-reject" in f.name
            tag = "expected REJECT" if expected_fail else "UNEXPECTED REJECT"
            print(f"  {f.name:50s} → {tag}: {e}", file=sys.stderr)
            if not expected_fail:
                rejected += 1
    print(f"\nposted: {posted}, rejected: {rejected}")
    sys.exit(0 if rejected == 0 else 1)


def main():
    ap = argparse.ArgumentParser(prog="bus.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_init = sub.add_parser("init", help="initialize a bus root")
    ap_init.add_argument("bus_root")
    ap_init.add_argument("--team", help="optional team_id to create team log")
    ap_init.set_defaults(func=cmd_init)

    ap_post = sub.add_parser("post", help="post a message")
    ap_post.add_argument("bus_root")
    ap_post.add_argument("message_file")
    ap_post.set_defaults(func=cmd_post)

    ap_read = sub.add_parser("read", help="read team or global log")
    ap_read.add_argument("bus_root")
    ap_read.add_argument("--team")
    ap_read.add_argument("--global", dest="global_log", action="store_true")
    ap_read.add_argument("--summary", action="store_true",
                          help="one-line per message")
    ap_read.set_defaults(func=cmd_read)

    ap_audit = sub.add_parser("audit", help="verify append-only invariant")
    ap_audit.add_argument("bus_root")
    ap_audit.add_argument("--team")
    ap_audit.set_defaults(func=cmd_audit)

    ap_valid = sub.add_parser("validate", help="validate a message file")
    ap_valid.add_argument("message_file")
    ap_valid.set_defaults(func=cmd_validate)

    ap_replay = sub.add_parser("replay", help="replay a demo directory")
    ap_replay.add_argument("bus_root")
    ap_replay.add_argument("demo_dir")
    ap_replay.set_defaults(func=cmd_replay)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
