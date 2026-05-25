import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        print("error: invalid input")
        sys.exit(0)
    
    try:
        response_text = data["response_text"]
        cited_claim_ids = data["cited_claim_ids"]
        available_claims = data["available_claims"]
    except KeyError:
        print("error: missing required fields")
        sys.exit(0)
    
    # Compute metrics
    cited_count = len(cited_claim_ids)
    
    # Create a set of available claim IDs for quick lookup
    available_claim_ids = set()
    for claim in available_claims:
        available_claim_ids.add(claim["claim_id"])
    
    # valid_cited: number of cited_claim_ids present in available_claims
    valid_cited = sum(1 for cid in cited_claim_ids if cid in available_claim_ids)
    
    # uncited_with_evidence: number of available_claims whose claim_id NOT in cited_claim_ids
    cited_set = set(cited_claim_ids)
    uncited_with_evidence = sum(1 for claim in available_claims if claim["claim_id"] not in cited_set)
    
    # unreviewed_cited: number of cited claims whose reviewer is null
    # We need to find cited claims that are in available_claims and have reviewer null
    unreviewed_cited = 0
    for claim in available_claims:
        if claim["claim_id"] in cited_set and claim.get("reviewer") is None:
            unreviewed_cited += 1
    
    # Print output
    print("CITATION COVERAGE SIDECAR")
    print()
    print(f"- cited: {cited_count}")
    print(f"- valid_cited: {valid_cited}")
    print(f"- uncited_with_evidence: {uncited_with_evidence}")
    print(f"- unreviewed_cited: {unreviewed_cited}")
    print()
    
    if unreviewed_cited > 0:
        print(f"WARNING: {unreviewed_cited} cited claims have no named reviewer.")

if __name__ == "__main__":
    main()