# Canoe Landing / Witness Record — Story Receipts

- packet: `sample-story-receipts`
- build model: `gpt-oss-120b` (TELUS build-attempt lane)
- date: 2026-05-26
- finding: **fixed**

## What we brought

A tool that turns a small set of public-safe story-receipts into a markdown wall the room can read on Tuesday — each entry only appearing if the contributor cleared it for display.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: one single-file command-line tool, standard library only, markdown output.

## What worked

The build attempt produced a tool that passed all 7 acceptance tests.

## What did not work / what broke

Attempt 1 failed some tests; the repair attempt corrected them.

## What we learned

The frozen build packet carried enough for a working build via the TELUS lane.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: boundary-non-public-scopes, boundary-contributor-contact.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
