import sys
import json
from datetime import datetime, date

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("error: usage: python3 tool.py <claims_json_path> [as_of YYYY-MM-DD]")
        sys.exit(0)

    claims_path = sys.argv[1]
    as_of_str = None
    if len(sys.argv) == 3:
        as_of_str = sys.argv[2]

    # Parse as_of
    as_of_date = None
    if as_of_str:
        try:
            as_of_date = datetime.strptime(as_of_str, "%Y-%m-%d").date()
        except ValueError:
            print("error: invalid as_of date format")
            sys.exit(0)

    # Read input
    try:
        with open(claims_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print("error: failed to read or parse input file")
        sys.exit(0)

    if not isinstance(data, dict) or "claims" not in data:
        print("error: invalid input structure")
        sys.exit(0)

    claims = data["claims"]
    if not isinstance(claims, list):
        print("error: claims must be a list")
        sys.exit(0)

    # Determine as_of date
    if as_of_date is None:
        latest_date = None
        for claim in claims:
            if "evidence_pointers" in claim and isinstance(claim["evidence_pointers"], list):
                for ep in claim["evidence_pointers"]:
                    if "created_at" in ep:
                        try:
                            d = datetime.strptime(ep["created_at"], "%Y-%m-%d").date()
                            if latest_date is None or d > latest_date:
                                latest_date = d
                        except ValueError:
                            pass
        if latest_date is not None:
            as_of_date = latest_date
        else:
            as_of_date = date(2026, 5, 26)

    # Freshness windows
    freshness_windows = {
        "descriptive": 730,
        "commitment_status": 180,
        "outcome": 365,
        "impact": 365,
        "risk": 180,
        "eligibility": 180
    }

    # Process claims
    results = []
    for claim in claims:
        claim_id = claim.get("claim_id", "unknown")
        claim_type = claim.get("claim_type", "descriptive")
        intended_use = claim.get("intended_use", "internal")
        visibility_tier = claim.get("visibility_tier", "private")
        evidence_pointers = claim.get("evidence_pointers", [])
        reviewer = claim.get("reviewer", None)
        contested = claim.get("contested", False)

        # Determine status
        status = None
        repair_path = None

        # 1. do_not_compute
        if visibility_tier == "not-for-computation":
            status = "do_not_compute"
            repair_path = "preserve as marker-only; do not compute"
        # 2. visibility_blocked
        elif visibility_tier in ("private", "local-only") and intended_use == "public_share":
            status = "visibility_blocked"
            repair_path = "choose: lower intended_use, or raise visibility (requires consent)"
        # 3. missing_evidence
        elif not evidence_pointers or (intended_use == "public_share" and reviewer is None and visibility_tier == "public"):
            status = "missing_evidence"
            repair_path = "attach evidence and named reviewer"
        # 4. contested
        elif contested:
            status = "contested"
            repair_path = "invite contesting party to review"
        # 5. stale_evidence
        else:
            days = freshness_windows.get(claim_type, 180)
            all_stale = True
            if evidence_pointers:
                for ep in evidence_pointers:
                    if "created_at" in ep:
                        try:
                            ep_date = datetime.strptime(ep["created_at"], "%Y-%m-%d").date()
                            if (as_of_date - ep_date).days <= days:
                                all_stale = False
                                break
                        except ValueError:
                            pass
            else:
                # No evidence pointers, but we already checked missing_evidence above
                # This case should not be reached if missing_evidence is checked first
                all_stale = True
            
            if all_stale:
                status = "stale_evidence"
                repair_path = f"refresh evidence within freshness window for {claim_type}"
        # 6. needs_review
        if status is None:
            needs_review = False
            if evidence_pointers:
                for ep in evidence_pointers:
                    if ep.get("reviewer") is None and visibility_tier == "public":
                        needs_review = True
                        break
            if needs_review:
                status = "needs_review"
                repair_path = "assign a named reviewer"
        
        # 7. ready_for_use
        if status is None:
            status = "ready_for_use"
            repair_path = None

        results.append({
            "claim_id": claim_id,
            "claim_type": claim_type,
            "status": status,
            "repair_path": repair_path
        })

    # Count summary
    ok_count = sum(1 for r in results if r["status"] == "ready_for_use")
    fail_count = len(results) - ok_count
    total_count = len(results)

    # Output
    print(f"CLAIMS COHERENCE REPORT (as_of {as_of_date.strftime('%Y-%m-%d')})")
    print()
    for r in results:
        print(f"{r['claim_id']} [{r['claim_type']}]: {r['status']}")
        if r['repair_path']:
            print(f"repair_path: {r['repair_path']}")
    print()
    print(f"SUMMARY: {ok_count} ready / {fail_count} needing work of {total_count} total")

if __name__ == "__main__":
    main()