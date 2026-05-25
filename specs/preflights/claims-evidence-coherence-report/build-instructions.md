# Build instructions — Claims Evidence Coherence Report (preflight)

Build `tool.py`. Run:

```
python3 tool.py <claims_json_path> [as_of YYYY-MM-DD]
```

Reads:

```json
{ "claims": [ {
  "claim_id": "...", "claim_text": "...",
  "claim_type": "descriptive" | "commitment_status" | "outcome" | "impact" | "risk" | "eligibility",
  "intended_use": "public_share" | "steward_review" | "internal",
  "visibility_tier": "public" | "local-only" | "private" | "not-for-computation",
  "evidence_pointers": [{"id":"...","created_at":"YYYY-MM-DD","reviewer":"..." | null}, ...],
  "reviewer": "..." | null,
  "contested": <boolean>
}, ... ] }
```

`as_of` defaults to the latest `evidence_pointers[].created_at` across all claims, else `2026-05-26`.

## Freshness windows (days)

| claim_type | days |
|---|---|
| descriptive | 730 |
| commitment_status | 180 |
| outcome | 365 |
| impact | 365 |
| risk | 180 |
| eligibility | 180 |

## Status rules (apply in priority order, stop at first match)

1. `do_not_compute` — `visibility_tier == "not-for-computation"`
2. `visibility_blocked` — `visibility_tier ∈ {private, local-only}` AND `intended_use == "public_share"`
3. `missing_evidence` — no `evidence_pointers` OR (`intended_use == "public_share"` AND `reviewer is null` AND `visibility_tier == "public"`)
4. `contested` — `contested == true`
5. `stale_evidence` — **all** evidence pointers have `created_at` older than the freshness window for this `claim_type` (measured against `as_of`)
6. `needs_review` — any evidence pointer has `reviewer is null` AND `visibility_tier == "public"`
7. `ready_for_use` — otherwise

## Repair path suggestions (per status)

| status | repair_path |
|---|---|
| do_not_compute | `preserve as marker-only; do not compute` |
| visibility_blocked | `choose: lower intended_use, or raise visibility (requires consent)` |
| missing_evidence | `attach evidence and named reviewer` |
| contested | `invite contesting party to review` |
| stale_evidence | `refresh evidence within freshness window for <claim_type>` |
| needs_review | `assign a named reviewer` |

For `stale_evidence`, substitute the actual claim_type into the repair_path string.

## Output

```
CLAIMS COHERENCE REPORT (as_of <as_of>)

<claim_id> [<claim_type>]: <status>
repair_path: <suggestion>     ← only if status != ready_for_use
<claim_id> [<claim_type>]: <status>
...

SUMMARY: <ok> ready / <fail> needing work of <N> total
```

- One blank line between header and first claim.
- No blank lines between claim entries.
- One blank line before SUMMARY.

## Errors

Single `error:` line on bad input, exit 0.

## Constraints

Stdlib only; no network; no credentials.
