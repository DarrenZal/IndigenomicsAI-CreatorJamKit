# Build instructions — Sidecar (preflight)

Build `python3 tool.py <response_json_path>`. Reads { "response_text":"...","cited_claim_ids":["..."],"available_claims":[{"claim_id":"...","reviewer":"..."|null}] }. Compute: cited_count=len(cited_claim_ids); valid_cited=number of cited_claim_ids present in available_claims; uncited_with_evidence=number of available_claims whose claim_id NOT in cited_claim_ids; unreviewed_cited=number of cited claims whose reviewer is null. Print header 'CITATION COVERAGE SIDECAR'; blank; '- cited: <cited_count>'; '- valid_cited: <valid_cited>'; '- uncited_with_evidence: <uncited_with_evidence>'; '- unreviewed_cited: <unreviewed_cited>'; blank; if unreviewed_cited > 0: 'WARNING: <unreviewed_cited> cited claims have no named reviewer.'. On invalid JSON: 'error:' line, exit 0. Stdlib only.

Stdlib only; no network; no credentials.
