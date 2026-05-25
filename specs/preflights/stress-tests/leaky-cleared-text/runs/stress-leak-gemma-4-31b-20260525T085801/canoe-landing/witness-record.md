# Canoe Landing / Witness Record — stress

- packet: `stress-leaky-cleared-text`
- build model: `gemma-4-31b` (TELUS build-attempt lane)
- date: 2026-05-25
- finding: **built clean**

## What we brought

trivial echo for stress

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: single-file CLI.

## What worked

The build attempt produced a tool that passed all 1 acceptance tests.

## What did not work / what broke

Nothing in the build attempt.

## What we learned

The frozen build packet carried enough for a working build via the TELUS lane.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: should-be-excluded-but-team-mis-cleared.

## Receipt

stress test
