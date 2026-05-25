#!/usr/bin/env python3
import sys
import json
import datetime

FRESHNESS_WINDOWS = {
    "descriptive": 730,
    "commitment_status": 180,
    "outcome": 365,
    "impact": 365,
    "risk": 180,
    "eligibility": 180,
}

REPAIR_PATHS = {
    "do_not_compute": "preserve as marker-only; do not compute",
    "visibility_blocked": "choose: lower intended_use, or raise visibility (requires consent)",
    "missing_evidence": "attach evidence and named reviewer",
    "contested": "invite contesting party to review",
    "stale_evidence": "refresh evidence within freshness window for {claim_type}",
    "needs_review": "assign a named reviewer",
}

def parse_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        raise ValueError(f"invalid date format: {s}")

def error(msg):
    print(f"error: {msg}")
    sys.exit(0)

def validate_claim(claim, idx):
    required_fields = [
        "claim_id", "claim_text", "claim_type", "intended_use",
        "visibility_tier", "evidence_pointers", "reviewer", "contested"
    ]
    for f in required_fields:
        if f not in claim:
            error(f"claim at index {idx} missing required field '{f}'")
    if not isinstance(claim["claim_id"], str):
        error(f"claim_id must be string at index {idx}")
    if claim["claim_type"] not in FRESHNESS_WINDOWS:
        error(f"unknown claim_type '{claim['claim_type']}' at index {idx}")
    if claim["intended_use"] not in {"public_share", "steward_review", "internal"}:
        error(f"invalid intended_use at index {idx}")
    if claim["visibility_tier"] not in {"public", "local-only", "private", "not-for-computation"}:
        error(f"invalid visibility_tier at index {idx}")
    if not isinstance(claim["evidence_pointers"], list):
        error(f"evidence_pointers must be list at index {idx}")
    for ep_idx, ep in enumerate(claim["evidence_pointers"]):
        if not isinstance(ep, dict):
            error(f"evidence pointer at claim {idx} index {ep_idx} not an object")
        for subf in ("id", "created_at", "reviewer"):
            if subf not in ep:
                error(f"evidence pointer missing '{subf}' at claim {idx} index {ep_idx}")
        if not isinstance(ep["id"], str):
            error(f"evidence id must be string at claim {idx} index {ep_idx}")
        try:
            parse_date(ep["created_at"])
        except ValueError:
            error(f"invalid created_at date at claim {idx} index {ep_idx}")
        # reviewer may be null or string; no further check
    if claim["reviewer"] is not None and not isinstance(claim["reviewer"], str):
        error(f"reviewer must be string or null at index {idx}")
    if not isinstance(claim["contested"], bool):
        error(f"contested must be boolean at index {idx}")

def compute_as_of(claims, provided):
    if provided:
        try:
            return parse_date(provided)
        except ValueError:
            error(f"provided as_of date '{provided}' is invalid")
    latest = None
    for claim in claims:
        for ep in claim["evidence_pointers"]:
            d = parse_date(ep["created_at"])
            if latest is None or d > latest:
                latest = d
    if latest is None:
        return datetime.date(2026, 5, 26)
    return latest

def status_for_claim(claim, as_of):
    vt = claim["visibility_tier"]
    iu = claim["intended_use"]
    ct = claim["claim_type"]
    reviewer = claim["reviewer"]
    contested = claim["contested"]
    eps = claim["evidence_pointers"]

    # 1. do_not_compute
    if vt == "not-for-computation":
        return "do_not_compute"
    # 2. visibility_blocked
    if vt in {"private", "local-only"} and iu == "public_share":
        return "visibility_blocked"
    # 3. missing_evidence
    if not eps or (iu == "public_share" and reviewer is None and vt == "public"):
        return "missing_evidence"
    # 4. contested
    if contested:
        return "contested"
    # 5. stale_evidence
    window_days = FRESHNESS_WINDOWS[ct]
    all_stale = True
    for ep in eps:
        ep_date = parse_date(ep["created_at"])
        age = (as_of - ep_date).days
        if age <= window_days:
            all_stale = False
            break
    if all_stale:
        return "stale_evidence"
    # 6. needs_review
    if vt == "public":
        for ep in eps:
            if ep["reviewer"] is None:
                return "needs_review"
    # 7. ready_for_use
    return "ready_for_use"

def main():
    if len(sys.argv) < 2:
        error("no input file provided")
    input_path = sys.argv[1]
    as_of_provided = None
    if len(sys.argv) >= 4 and sys.argv[2] == "as_of":
        as_of_provided = sys.argv[3]

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        error(f"cannot read JSON: {e}")

    if not isinstance(data, dict) or "claims" not in data:
        error("JSON must contain top-level 'claims' list")
    claims = data["claims"]
    if not isinstance(claims, list):
        error("'claims' must be a list")

    for idx, claim in enumerate(claims):
        if not isinstance(claim, dict):
            error(f"claim at index {idx} is not an object")
        validate_claim(claim, idx)

    as_of_date = compute_as_of(claims, as_of_provided)

    # Prepare report
    lines = []
    header = f"CLAIMS COHERENCE REPORT (as_of {as_of_date.isoformat()})"
    lines.append(header)
    lines.append("")  # blank line

    ready_cnt = 0
    fail_cnt = 0

    for claim in claims:
        status = status_for_claim(claim, as_of_date)
        if status == "ready_for_use":
            ready_cnt += 1
        else:
            fail_cnt += 1
        line1 = f"{claim['claim_id']} [{claim['claim_type']}]: {status}"
        lines.append(line1)
        if status != "ready_for_use":
            suggestion = REPAIR_PATHS[status]
            if status == "stale_evidence":
                suggestion = suggestion.format(claim_type=claim["claim_type"])
            lines.append(f"repair_path: {suggestion}")

    lines.append("")  # blank line before summary
    total = len(claims)
    summary = f"SUMMARY: {ready_cnt} ready / {fail_cnt} needing work of {total} total"
    lines.append(summary)

    print("\n".join(lines))

if __name__ == "__main__":
    main()