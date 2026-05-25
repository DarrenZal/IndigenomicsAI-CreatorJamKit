# Canoe Landing / Witness Record — Claims Coherence preflight

- packet: `preflight-claims-evidence-coherence`
- build model: `gpt-oss-120b` (TELUS build-attempt lane)
- date: 2026-05-25
- finding: **no change**

## What we brought

Help a steward see whether a public claim is supported, stale, contested, or ready for a specific use.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: single-file CLI.

## What worked

The build attempt passed 7 of 8 tests.

## What did not work / what broke

Acceptance tests still failing: __main__.ClaimsCoherenceTest.test_4_stale.

## What we learned

This packet needs another repair round or a human builder.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: none.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
