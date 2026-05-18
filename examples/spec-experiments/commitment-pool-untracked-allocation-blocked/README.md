---
doc_kind: spec-experiment
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Commitment Pool + Untracked Allocation Blocked Experiment

This experiment tests a non-composable pair:

- `specs/commitment-pool-route-diagnostic.md`
- `specs/untracked-allocation-ledger.md`

The result is intentionally blocked. That is the point of the experiment.

## Question

Can a commitment pool route diagnostic consume an untracked allocation record?

## Finding

Not directly. The route diagnostic wants structured routing fields, capacity, amount or quantity, pool fit, evidence, and consent to route. The untracked allocation ledger can deliberately preserve non-legibility: hidden amount, hidden recipient, hidden funder, private notes pointer, and a reason not to track.

The compatible projection is a summary-only receipt saying that support occurred or was intentionally not tracked. It must not become a routeable commitment, funding edge, or pool capacity update.

## Files

- `fixtures/blocked-composition-fixture.json`
- `reports/blocked-composition-receipt.md`
- `reports/composition-engine-report.md`
- `reports/trade-off-surface.md`
- `traces/composition-trace.json`

## Participant-Safe Scope

All content is fictional and public-sample. No real allocation, funder, recipient, financial record, private note, participant identity, cultural material, or authority-bound content is included.

## Composition Result

| Field | Value |
| --- | --- |
| Composition shape | `partial_overlap` |
| Composition disposition | `non_composable` |
| Allowed projection | summary-only receipt |
| Blocked projection | routeable pool commitment, fundable edge, capacity update |

## Boundary

This experiment records why two specs should not compose directly. It does not say the allocation was invalid, incomplete, failed, or less valuable. It says the allocation's non-legibility is the point to preserve.
