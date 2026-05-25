# Build instructions — Witness Record Validator (preflight sample)

Build `tool.py`. Run as:

```
python3 tool.py <records_json_path> [as_of YYYY-MM-DD]
```

Reads a JSON object:

```json
{ "records": [ {
    "record_id": "...",
    "statement": "...",
    "record_type": "claim" | "witness" | "attestation" | "promise" | "refusal" | "review" | "receipt",
    "actor_or_issuer": "...",
    "witnesses": ["..."],
    "evidence_pointers": [{"id":"...","created_at":"YYYY-MM-DD"}, ...],
    "visibility_tier": "public" | "local-only" | "private" | "not-for-computation",
    "permission_state": "granted" | "pending" | "refused" | "not-applicable",
    "review_state": "reviewed" | "contested" | "withdrawn" | "pending" | "not-applicable",
    "created_at": "YYYY-MM-DD"
}, ... ] }
```

`as_of`: optional second CLI arg in `YYYY-MM-DD` form. If absent, default to the latest `created_at` in the file (else `2026-05-26`).

For each record, evaluate four findings:

1. **missing_consent** — if `visibility_tier == "public"` AND `permission_state != "granted"`.
2. **stale_evidence** — if any `evidence_pointers[].created_at` is more than **365 days** before `as_of`.
3. **overbroad_public_claim** — if `record_type` ∈ {`claim`, `attestation`, `promise`} AND `visibility_tier == "public"` AND `len(statement) > 240`.
4. **unsupported_authority_language** — if `statement` contains any of (case-insensitive) `certified`, `authorized`, `legitimate`, `official` AND `review_state != "reviewed"`.

## Output

```
WITNESS RECORD VALIDATION (as_of <as_of>)

<record_id>: OK
<record_id>: missing_consent, stale_evidence
...

SUMMARY: <OK> ok, <FAIL> with findings of <N> total
```

- One blank line between header and first record line.
- One blank line between last record line and SUMMARY.
- Findings joined by `, ` alphabetically. `OK` if no findings.

## Errors

On unreadable file or invalid JSON, print a single line starting with `error:` and exit 0.

## Constraints

Stdlib only; no network; no credentials.
