# Canoe Landing / Witness Record — Energy Receipt preflight

- packet: `preflight-energy-receipt`
- build model: `qwen-3.6-35b` (TELUS build-attempt lane)
- date: 2026-05-25
- finding: **fixed**

## What we brought

Turn a team's compute events on TELUS Rimouski hydro into a per-team energy receipt with intention + outcome + reflection — receipt, not offset.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: single-file CLI.

## What worked

The build attempt produced a tool that passed all 6 acceptance tests.

## What did not work / what broke

Attempt 1 failed some tests; the repair attempt corrected them.

## What we learned

The frozen build packet carried enough for a working build via the TELUS lane.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: raw-prompts-and-completions.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, carbon neutrality, or readiness for reuse.
