#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: missing input file path")
        sys.exit(0)

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"error: {e}")
        sys.exit(0)

    cited_claim_ids = data.get("cited_claim_ids", [])
    available_claims = data.get("available_claims", [])

    # Build a mapping from claim_id to reviewer (may be None)
    claim_to_reviewer = {}
    for claim in available_claims:
        cid = claim.get("claim_id")
        if cid is not None:
            claim_to_reviewer[cid] = claim.get("reviewer")

    cited_set = set(cited_claim_ids)

    cited_count = len(cited_claim_ids)
    valid_cited = sum(1 for cid in cited_claim_ids if cid in claim_to_reviewer)
    uncited_with_evidence = sum(1 for cid in claim_to_reviewer if cid not in cited_set)
    unreviewed_cited = sum(1 for cid in cited_claim_ids if claim_to_reviewer.get(cid) is None)

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