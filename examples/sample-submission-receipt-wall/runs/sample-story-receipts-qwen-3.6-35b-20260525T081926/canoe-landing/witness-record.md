# Canoe Landing / Witness Record — Story Receipts

- packet: `sample-story-receipts`
- build model: `qwen-3.6-35b` (TELUS build-attempt lane)
- date: 2026-05-26
- finding: **no change**

## What we brought

A tool that turns a small set of public-safe story-receipts into a markdown wall the room can read on Tuesday — each entry only appearing if the contributor cleared it for display.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: one single-file command-line tool, standard library only, markdown output.

## What worked

The build attempt passed 5 of 7 tests.

## What did not work / what broke

Acceptance tests still failing: __main__.StoryReceiptsTest.test_1_happy_path_two_public_one_withheld, __main__.StoryReceiptsTest.test_2_multi_line_receipt_each_line_quoted.

## What we learned

This packet needs another repair round or a human builder.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: boundary-non-public-scopes, boundary-contributor-contact.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
