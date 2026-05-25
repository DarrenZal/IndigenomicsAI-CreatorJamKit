#!/usr/bin/env python3
import sys
import json
from datetime import date, datetime, timedelta

def parse_date(s):
    try:
        return date.fromisoformat(s)
    except Exception:
        return None

def main():
    if len(sys.argv) < 2:
        print("error:")
        return

    json_path = sys.argv[1]
    as_of_str = sys.argv[2] if len(sys.argv) > 2 else None

    # Load JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error:")
        return

    records = data.get("records", [])
    # Determine as_of date
    if as_of_str:
        as_of = parse_date(as_of_str)
        if not as_of:
            as_of = date(2026, 5, 26)
    else:
        max_created = None
        for rec in records:
            d = parse_date(rec.get("created_at", ""))
            if d and (max_created is None or d > max_created):
                max_created = d
        as_of = max_created if max_created else date(2026, 5, 26)

    # Prepare output
    header = f"WITNESS RECORD VALIDATION (as_of {as_of.isoformat()})"
    print(header)
    print()  # blank line after header

    ok_count = 0
    fail_count = 0
    total_findings = 0

    for rec in records:
        rec_id = rec.get("record_id", "")
        findings = []

        # 1. missing_consent
        if rec.get("visibility_tier") == "public" and rec.get("permission_state") != "granted":
            findings.append("missing_consent")

        # 2. stale_evidence
        stale = False
        for ev in rec.get("evidence_pointers", []):
            ev_date = parse_date(ev.get("created_at", ""))
            if ev_date and (as_of - ev_date).days > 365:
                stale = True
                break
        if stale:
            findings.append("stale_evidence")

        # 3. overbroad_public_claim
        if rec.get("record_type") in {"claim", "attestation", "promise"} \
                and rec.get("visibility_tier") == "public" \
                and len(rec.get("statement", "")) > 240:
            findings.append("overbroad_public_claim")

        # 4. unsupported_authority_language
        stmt = rec.get("statement", "").lower()
        authority_terms = ["certified", "authorized", "legitimate", "official"]
        if any(term in stmt for term in authority_terms) and rec.get("review_state") != "reviewed":
            findings.append("unsupported_authority_language")

        if findings:
            findings.sort()
            line = f"{rec_id}: {', '.join(findings)}"
            fail_count += 1
            total_findings += len(findings)
        else:
            line = f"{rec_id}: OK"
            ok_count += 1

        print(line)

    print()  # blank line before summary
    summary = f"SUMMARY: {ok_count} ok, {fail_count} with findings of {total_findings} total"
    print(summary)

if __name__ == "__main__":
    main()