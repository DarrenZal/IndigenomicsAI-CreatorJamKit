import sys
import json
from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    as_of_arg = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except Exception:
        print("error: unreadable file or invalid JSON")
        sys.exit(0)

    if not isinstance(data, dict) or "records" not in data:
        # Handle cases where JSON is valid but doesn't match expected schema
        # though the spec implies records will be present.
        records = []
    else:
        records = data.get("records", [])
    
    # Determine as_of date
    if as_of_arg:
        try:
            as_of_date = parse_date(as_of_arg)
        except ValueError:
            # Fallback if provided date is malformed
            as_of_date = parse_date("2026-05-26")
    else:
        created_dates = []
        for r in records:
            if isinstance(r, dict) and "created_at" in r:
                try:
                    created_dates.append(parse_date(r["created_at"]))
                except (ValueError, TypeError):
                    pass
        if created_dates:
            as_of_date = max(created_dates)
        else:
            as_of_date = parse_date("2026-05-26")

    as_of_str = as_of_date.strftime("%Y-%m-%d")
    
    results = []
    ok_count = 0
    fail_count = 0
    total_findings = 0

    authority_keywords = {"certified", "authorized", "legitimate", "official"}

    for r in records:
        if not isinstance(r, dict):
            continue
            
        findings = set()
        rid = r.get("record_id", "unknown")
        statement = r.get("statement", "")
        visibility = r.get("visibility_tier", "")
        permission = r.get("permission_state", "")
        rtype = r.get("record_type", "")
        review_state = r.get("review_state", "")
        evidence = r.get("evidence_pointers", [])

        # 1. missing_consent
        if visibility == "public" and permission != "granted":
            findings.add("missing_consent")

        # 2. stale_evidence
        if isinstance(evidence, list):
            for ptr in evidence:
                if isinstance(ptr, dict):
                    ptr_date_str = ptr.get("created_at")
                    if ptr_date_str:
                        try:
                            ptr_date = parse_date(ptr_date_str)
                            if (as_of_date - ptr_date).days > 365:
                                findings.add("stale_evidence")
                                break
                        except (ValueError, TypeError):
                            pass

        # 3. overbroad_public_claim
        if rtype in {"claim", "attestation", "promise"} and visibility == "public" and len(statement) > 240:
            findings.add("overbroad_public_claim")

        # 4. unsupported_authority_language
        stmt_lower = statement.lower() if isinstance(statement, str) else ""
        if any(kw in stmt_lower for kw in authority_keywords) and review_state != "reviewed":
            findings.add("unsupported_authority_language")

        if not findings:
            results.append(f"{rid}: OK")
            ok_count += 1
        else:
            sorted_findings = sorted(list(findings))
            results.append(f"{rid}: {', '.join(sorted_findings)}")
            fail_count += 1
            total_findings += len(sorted_findings)

    # Output
    print(f"WITNESS RECORD VALIDATION (as_of {as_of_str})")
    print()
    for res in results:
        print(res)
    print()
    print(f"SUMMARY: {ok_count} ok, {fail_count} with findings of {total_findings} total")

if __name__ == "__main__":
    main()