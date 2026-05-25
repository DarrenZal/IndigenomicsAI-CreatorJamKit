# Canoe Landing / Witness Record — preflight

- packet: `preflight-risk-coherence`
- build model: `gemma-4-31b` (TELUS build-attempt lane)
- date: 2026-05-25
- finding: **no change**

## What we brought

Show resilience signals without becoming an underwriting or actuarial model.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: single-file CLI.

## What worked

The build attempt passed 2 of 3 tests.

## What did not work / what broke

Acceptance tests still failing: __main__.PreflightTest.test_t2_no_ranking.

## What we learned

This packet needs another repair round or a human builder.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: none.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
