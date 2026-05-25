# Withdrawal Flow — Worked Example

What it looks like when a contributor changes their mind about something they recorded — and how the kit's tooling helps the operator team figure out what needs to update.

## The scenario

A team called **Kelp Watch** ran a build attempt Monday afternoon. The team has:

- A build-attempt record (`r1`) — published on the `receipt-wall`
- A witness record (`r2`) — published on the `receipt-wall`
- An offering (`r3`) — A. Tidesmith's eelgrass observations — listed as a cleared input on the `agentic-build-packet-kelp-watch`

A different team called **Story Receipts** also has a build-attempt record (`r4`) on `story-receipts-wall` + aggregate.

Tuesday morning, **A. Tidesmith decides to withdraw offering r3**. She doesn't want her observations carried in the public build packet on Tuesday's reading. She's not refusing the offering itself — she's withdrawing it from this specific build context.

## The propagation question

> "If A. Tidesmith withdraws r3, what surfaces and downstream summaries reference it and need to update?"

The naive answer ("just remove it from the build packet") misses the propagation. The systematic answer comes from running the tool.

## Running the propagation tool

```bash
python3 tools/withdrawal-propagation.py \
  examples/sample-withdrawal-flow/manifest.json \
  r3
```

Output:

```
WITHDRAWAL PROPAGATION (manifest: manifest.json)

Withdrawn record: r3
  surfaces to update (1):
    - agentic-build-packet-kelp-watch

BOUNDARY: this propagation lists which surfaces reference the withdrawn
record(s) based on the manifest. It does not auto-update anything.
Humans execute the updates.
```

## What this tells the operator team

1. **One surface needs update**: the `agentic-build-packet-kelp-watch` lists r3 as a `cleared_records` input. The team should re-export the build packet without r3, or hold the build packet for re-freeze.

2. **No downstream summaries are affected** — because r3 doesn't directly appear in `receipt-wall`, `aggregate-jam-summary`, or `story-receipts-wall`. The receipt wall shows the team's build-attempt records (r1, r2), not the underlying offerings. The withdrawal doesn't ripple unless the team's witness record (r2) needs to be revised to acknowledge that the build attempt now used a smaller offering set.

3. **The tool does NOT execute the updates.** It surfaces what's affected. Humans:
   - Re-export the build packet (operator's job)
   - Decide whether the build attempt needs to be re-run with the smaller offering set
   - Update the witness record (r2) if the team's account of what happened changed

## What if multiple records are withdrawn?

The tool accepts multiple record IDs:

```bash
python3 tools/withdrawal-propagation.py manifest.json r1 r3
```

Each withdrawn record gets its own propagation list. Some withdrawals propagate to many surfaces; some propagate to one.

## Pattern: withdrawal is structural, not procedural

The kit treats withdrawal as a structural concept (you can withdraw something), not just an apology mechanism (asking for forgiveness after the fact). Building withdrawal into the schema, the manifest, and the tooling means:

- Contributors can change their minds without negotiating an awkward removal
- Operators can systematically execute the propagation
- Downstream summaries can be re-rolled-up with the correct subset
- The receipt of the withdrawal itself becomes part of the witness record (boundaries that remain)

## When to use this pattern jam-day

Any of:

- A contributor reconsiders an offering they cleared
- A team realizes mid-build that they don't want a particular offering carried in the public packet
- A reviewer flags content that needs to be held rather than displayed
- Someone explicitly says "I changed my mind"

In any of those cases, run the propagation tool first to see scope, then execute the updates with humans in the loop.

## Files in this directory

- `manifest.json` — small fictional dependency manifest (records + surfaces + summaries)
- `README.md` — this file

## Boundary

This is a fictional manifest. No real withdrawal is recorded here. The pattern is real and the tooling works as shown.
