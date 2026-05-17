# Commitment Pool Route Diagnostic

Fixture: `commitment-pool-route-public-sample-v0.1`  
Diagnostic date: 2026-05-17  
Diagnostic use: public workshop replay that explains route readiness, review needs, and hard stops for fictional declarations.

## Participant Safety

This diagnostic uses fictional public-sample content only. It contains no participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material. The share-policy block is marker-only and does not reveal, infer, or search for protected content.

## Pool Capacity Summary

| Pool | Unit | Total | Committed | Remaining | Route Boundary |
|---|---|---:|---:|---:|---|
| `pool:cedar-care-sprint` | volunteer_hours | 20 | 12 | 8 | Public-sample replay only; no real commitments are created. |
| `pool:harbor-microgrant-zero` | usd | 0 | 0 | 0 | Zero-capacity sample pool; cannot accept new route candidates. |

## Candidate Route Summary

| Candidate | Type | Target Pool | Status | Primary Reasons |
|---|---|---|---|---|
| `candidate:CPR-001` | offer | `pool:cedar-care-sprint` | `route_ready` | Required fields present, capacity available, share policy allowed, evidence present. |
| `candidate:CPR-002` | commitment | `pool:harbor-microgrant-zero` | `hard_stop` | Zero capacity, missing `bioregion_uri`, missing evidence. |
| `candidate:CPR-003` | need | `pool:cedar-care-sprint` | `not_computable` | Protected share-policy block, `do_not_compute`, active standing refusal. |

## Field Completeness

| Candidate | Bioregion | Timeframe | Routing Tags | Evidence | Result |
|---|---|---|---|---|---|
| `candidate:CPR-001` | present | present | present | present | Complete enough for route-readiness review. |
| `candidate:CPR-002` | missing | present | present | missing | Missing fields reported; route remains blocked. |
| `candidate:CPR-003` | marker only | redacted | present | marker only | Not computable; do not complete from protected records. |

## Diagnostic List

| Candidate | Diagnostic Codes | Capacity Effect | Repair Path |
|---|---|---|---|
| `candidate:CPR-001` | `required_fields_present`, `capacity_available`, `share_policy_allowed`, `evidence_present` | Hypothetical route would leave 2 of 8 volunteer hours remaining. | No repair required for diagnostic readiness; human review is still required before any real-world commitment. |
| `candidate:CPR-002` | `capacity_block`, `missing_bioregion_uri`, `missing_evidence` | No route possible; target pool has 0 USD remaining. | Do not route. A steward would need a new pool with capacity, a bioregion URI, evidence pointers, and governance review. |
| `candidate:CPR-003` | `share_policy_block`, `do_not_compute`, `standing_refusal_active`, `protected_marker_only` | No capacity calculation is performed. | Preserve the refusal and do not inspect or complete the protected declaration. |

## Refusals And Constraints

| Record | Applies To | Status | Handling |
|---|---|---|---|
| `standing_refusal:CPR-RF-001` | `candidate:CPR-003`, protected private share policy | active | Honored as marker-only; no routing, summary, inference, or search. |
| `constraint:CPR-001` | `pool:harbor-microgrant-zero` | active | Blocks `candidate:CPR-002` because the pool has zero remaining capacity. |

## Acceptance Checks

| ID | Status | Evidence |
|---|---|---|
| `AC1` | pass | `candidate:CPR-002` reports missing `bioregion_uri` and missing evidence. |
| `AC2` | pass | `candidate:CPR-002` receives `hard_stop` because the target pool has zero capacity. |
| `AC3` | pass | `candidate:CPR-003` is blocked by share policy without exposing protected content. |
| `AC4` | pass | `standing_refusal:CPR-RF-001` and `candidate:CPR-003` are honored as non-routable. |
| `AC5` | pass | Missing capacity, bioregion, and evidence are surfaced as steward review needs, not auto-resolved. |

## Refusal Boundaries

| Boundary | Status | Evidence |
|---|---|---|
| Do not automatically route money, commitments, or authority. | honored | The route-ready candidate is diagnostic-only and still requires human review. |
| Do not compute legitimacy. | honored | No legitimacy score, rank, or certification appears. |
| Do not route around a refusal. | honored | The standing refusal blocks `candidate:CPR-003`. |
| Do not search protected records to complete a pool. | honored | The share-policy marker remains redacted and not computable. |

## Not Run

- No real pool update.
- No payment, grant, or commitment execution.
- No participant outreach.
- No search over private or protected records.
