# Canoe Landing / Witness Record — Pool Routing

- packet: `sample-commitment-pool-route`
- build model: `qwen-3.6-35b` (TELUS build-attempt lane)
- date: 2026-05-26
- finding: **improved**

## What we brought

A tool that tells a team whether their offers, needs, and commitments can route into a small shared pool, or what's blocking it.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: one single-file command-line tool, standard library only, routing diagnostic output.

## What worked

The build attempt passed 6 of 7 tests.

## What did not work / what broke

Acceptance tests still failing: __main__.PoolRouteTest.test_6_idle_and_no_supply.

## What we learned

This packet needs another repair round or a human builder.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: boundary-withheld-offers, boundary-contributor-contact.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
