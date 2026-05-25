import json
import sys
from datetime import datetime, timedelta

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    as_of_arg = None
    if len(sys.argv) >= 4 and sys.argv[2] == "as_of":
        as_of_arg = sys.argv[3]

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except Exception:
        print("error: invalid input file")
        sys.exit(0)

    if not isinstance(data, dict) or "claims" not in data:
        print("error: invalid input format")
        sys.exit(0)

    claims = data["claims"]
    
    # Determine as_of date
    all_dates = []
    for c in claims:
        if not isinstance(c, dict): continue
        eps = c.get("evidence_pointers", [])
        if not isinstance(eps, list): continue
        for ep in eps:
            if not isinstance(ep, dict): continue
            date_str = ep.get("created_at")
            if date_str:
                try:
                    all_dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                except ValueError:
                    pass
    
    if as_of_arg:
        try:
            as_of_date = datetime.strptime(as_of_arg, "%Y-%m-%d")
        except ValueError:
            print("error: invalid as_of date format")
            sys.exit(0)
    elif all_dates:
        as_of_date = max(all_dates)
    else:
        as_of_date = datetime.strptime("2026-05-26", "%Y-%m-%d")

    as_of_str = as_of_date.strftime("%Y-%m-%d")

    freshness_windows = {
        "descriptive": 730,
        "commitment_status": 180,
        "outcome": 365,
        "impact": 365,
        "risk": 180,
        "eligibility": 180
    }

    repair_paths = {
        "do_not_compute": "preserve as marker-only; do not compute",
        "visibility_blocked": "choose: lower intended_use, or raise visibility (requires consent)",
        "missing_evidence": "attach evidence and named reviewer",
        "contested": "invite contesting party to review",
        "stale_evidence": "refresh evidence within freshness window for {type}",
        "needs_review": "assign a named reviewer",
        "ready_for_use": None
    }

    results = []
    ready_count = 0

    for c in claims:
        cid = c.get("claim_id", "unknown")
        ctype = c.get("claim_type", "unknown")
        iuse = c.get("intended_use")
        vtier = c.get("visibility_tier")
        eps = c.get("evidence_pointers", [])
        rev = c.get("reviewer")
        contested = c.get("contested", False)

        status = "ready_for_use"

        # 1. do_not_compute
        if vtier == "not-for-computation":
            status = "do_not_compute"
        # 2. visibility_blocked
        elif vtier in ["private", "local-only"] and iuse == "public_share":
            status = "visibility_blocked"
        # 3. missing_evidence
        elif not eps or (iuse == "public_share" and rev is None and vtier == "public"):
            status = "missing_evidence"
        # 4. contested
        elif contested is True:
            status = "contested"
        # 5. stale_evidence
        else:
            window_days = freshness_windows.get(ctype, 0)
            all_stale = True
            if not eps:
                all_stale = True
            else:
                for ep in eps:
                    date_str = ep.get("created_at")
                    if date_str:
                        try:
                            ep_date = datetime.strptime(date_str, "%Y-%m-%d")
                            # Freshness: (as_of - ep_date).days <= window_days
                            # If any evidence is within window, it is NOT stale.
                            if (as_of_date - ep_date).days <= window_days:
                                all_stale = False
                                break
                        except ValueError:
                            pass
            
            if all_stale:
                status = "stale_evidence"
            # 6. needs_review
            else:
                needs_rev = False
                for ep in eps:
                    if ep.get("reviewer") is None and vtier == "public":
                        needs_rev = True
                        break
                if needs_rev:
                    status = "needs_review"
                else:
                    status = "ready_for_use"

        if status == "ready_for_use":
            ready_count += 1

        results.append((cid, ctype, status))

    # Output
    print(f"CLAIMS COHERENCE REPORT (as_of {as_of_str})")
    print()
    for cid, ctype, status in results:
        print(f"{cid} [{ctype}]: {status}")
        if status != "ready_for_use":
            path = repair_paths[status]
            if status == "stale_evidence":
                path = path.format(type=ctype)
            print(f"repair_path: {path}")

    print()
    print(f"SUMMARY: {ready_count} ready / {len(claims) - ready_count} needing work of {len(claims)} total")

if __name__ == "__main__":
    main()