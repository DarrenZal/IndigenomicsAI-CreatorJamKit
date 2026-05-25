# Canoe Landing / Witness Record — Pool Routing

- packet: `sample-commitment-pool-route`
- build model: `gpt-oss-120b` (TELUS build-attempt lane)
- date: 2026-05-26
- finding: **fixed**

## What we brought

A tool that tells a team whether their offers, needs, and commitments can route into a small shared pool, or what's blocking it.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: one single-file command-line tool, standard library only, routing diagnostic output.

## What worked

The build attempt produced a tool that passed all 7 acceptance tests.

## What did not work / what broke

Attempt 1 failed some tests; the repair attempt corrected them.

## What we learned

The frozen build packet carried enough for a working build via the TELUS lane.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: boundary-withheld-offers, boundary-contributor-contact.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
