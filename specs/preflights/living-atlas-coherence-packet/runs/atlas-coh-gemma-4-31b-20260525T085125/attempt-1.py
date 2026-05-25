import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        print("error:")
        sys.exit(0)

    contributions = data.get("contributions", [])
    total_n = len(contributions)
    
    results = []
    clean_count = 0
    flagged_count = 0

    for item in contributions:
        cid = item.get("id", "unknown")
        layer = item.get("layer", "unknown")
        consent = item.get("consent")
        sources = item.get("cited_sources", [])
        
        findings = []
        
        # (1) missing_consent
        if consent not in {"public", "steward-review", "private"}:
            findings.append("missing_consent")
            
        # (2) needs_steward_review
        if consent == "steward-review":
            findings.append("needs_steward_review")
            
        # (3) uncited_public
        if consent == "public" and not sources:
            findings.append("uncited_public")
            
        if not findings:
            status = "clean"
            clean_count += 1
        else:
            # Alphabetical comma-joined
            findings.sort()
            status = ", ".join(findings)
            flagged_count += 1
            
        results.append(f"{cid} [{layer}]: {status}")

    # Header
    print(f"ATLAS COHERENCE PACKET ({clean_count} clean / {flagged_count} flagged of {total_n} contributions)")
    print()

    # Body
    for res in results:
        print(res)
        print()

    # Footer
    print("BOUNDARY: this packet flags coherence; it does not force fit, replace steward review, or grant any visibility upgrade.")

if __name__ == "__main__":
    main()