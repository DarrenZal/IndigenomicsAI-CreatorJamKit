import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        print("error:")
        sys.exit(0)

    # Extract fields with defaults to avoid KeyErrors
    cited_claim_ids = data.get("cited_claim_ids", [])
    available_claims = data.get("available_claims", [])

    # Compute metrics
    cited_count = len(cited_claim_ids)
    
    # Create a map of available claims for O(1) lookup
    available_map = {claim.get("claim_id"): claim for claim in available_claims if "claim_id" in claim}
    
    valid_cited = 0
    for cid in cited_claim_ids:
        if cid in available_map:
            valid_cited += 1
            
    uncited_with_evidence = 0
    for cid in available_map:
        if cid not in cited_claim_ids:
            uncited_with_evidence += 1
            
    unreviewed_cited = 0
    for cid in cited_claim_ids:
        if cid in available_map:
            if available_map[cid].get("reviewer") is None:
                unreviewed_cited += 1

    # Output formatting
    print("CITATION COVERAGE SIDECAR")
    print("")
    print(f"- cited: {cited_count}")
    print(f"- valid_cited: {valid_cited}")
    print(f"- uncited_with_evidence: {uncited_with_evidence}")
    print(f"- unreviewed_cited: {unreviewed_cited}")
    print("")
    
    if unreviewed_cited > 0:
        print(f"WARNING: {unreviewed_cited} cited claims have no named reviewer.")

if __name__ == "__main__":
    main()