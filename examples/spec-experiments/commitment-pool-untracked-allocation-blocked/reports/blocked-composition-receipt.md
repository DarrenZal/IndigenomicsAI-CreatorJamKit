# Blocked Composition Receipt: Commitment Pool + Untracked Allocation

Fixture: `commitment-pool-untracked-allocation-blocked-public-sample-v0.1`  
Date: 2026-05-17  
Disposition: `non_composable`

## Participant Safety

This receipt uses fictional public-sample content only. It contains no real allocation, funder, recipient, financial record, private note, protected cultural material, or authority-bound material.

## Composition Attempt

| Field | Value |
| --- | --- |
| Source specs | `commitment-pool-route-diagnostic`, `untracked-allocation-ledger` |
| Question | Can an untracked allocation become a routeable commitment pool record? |
| Composition shape | `partial_overlap` |
| Composition disposition | `non_composable` |
| Allowed projection | summary-only receipt |
| Blocked projection | routeable commitment, fundable edge, pool capacity update |

## Why It Does Not Compose

The commitment pool route diagnostic needs structured fields such as issuer, beneficiary, quantity, unit, timeframe, routing tags, bioregion, share policy, and evidence pointers.

The untracked allocation record deliberately withholds or refuses several of those fields:

| Route Need | Allocation State | Result |
| --- | --- | --- |
| Beneficiary or recipient | hidden | blocked |
| Quantity or amount | not tracked | blocked |
| Route permission | `do_not_route: true` | blocked |
| Computation permission | `do_not_compute: true` | blocked |
| Evidence pointer | private notes pointer redacted | blocked |
| Receipt policy | private receipt | blocked |

## Speech Act Transition Review

| Field | Value |
| --- | --- |
| Transition | `allocation_record` -> `route_diagnostic` |
| Transition ID | `transition:allocation-to-route-diagnostic-blocked-001` |
| Reviewer | Public Sample Composition Reviewer |
| Review date | 2026-05-17 |
| Transition result | blocked |

The transition is blocked because converting the private introduction into a routeable pool contribution would change relational support into a structured commitment. That would violate the not-tracked reason and create surveillance pressure.

## What This Receipt Does Not Establish

- It does not say the allocation failed.
- It does not say the allocation lacked value.
- It does not create a routeable commitment.
- It does not update pool capacity.
- It does not create a funding edge.
- It does not authorize public display of private details.
- It does not establish legitimacy, authority, certification, eligibility, or investment relevance.

## Allowed Public Summary

Support was offered in a way that should remain private and not routable. The public composition result is a blocked, summary-only receipt.

## Acceptance Checks

| Check | Status | Evidence |
| --- | --- | --- |
| Non-composability is recorded as a valid result. | pass | `composition_disposition: non_composable` |
| Private allocation details are not exposed. | pass | recipient, amount, and private notes are omitted. |
| The route diagnostic does not infer missing route fields. | pass | blocked codes include `not_tracked_by_design` and `missing_route_quantity_by_design`. |
| The allocation is not treated as failure or lower value. | pass | receipt states that non-legibility is preserved. |
| Withdrawal path is named. | pass | fixture identifies affected surfaces and action if withdrawn. |

## Repair Path

No repair is recommended for direct routing.

If the contributor later wants to make a separate public offer or commitment, create a new record with explicit consent. Do not backfill from this private allocation or infer hidden details.

## Boundary

This receipt records a blocked composition. It does not establish legitimacy, authority, certification, eligibility, financial value, pool readiness, or permission for reuse.
