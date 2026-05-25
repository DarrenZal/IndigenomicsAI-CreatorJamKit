# Refusal-Only — Worked Example

The most counter-intuitive pattern in the kit: **a team-submission that does NOT lead to a build attempt**.

## The pattern

A team comes to the Jam, works through the offering-integration session, and concludes that **the thing they originally wanted to build should not be built**. The kit's discipline says this is a complete Jam contribution — not a failure.

Mechanically:
- `ai_input_scope: none` — no AI/TELUS runtime packet can be exported
- `build_request.path: note-only` — no tool to build
- `display_scope: spoken-only` (or whatever the team prefers) — Tuesday share is a verbal account of the refusal
- `reuse_scope: not-granted` — the refusal does not consent to anyone else building the inverse

The submission IS the deliverable. The witness record on Tuesday holds the refusal in front of the room.

## When to show this pattern

A team comes to a mentor saying:
- "We came in wanting to build X but now we don't think we should"
- "We've identified a boundary that means our build can't proceed"
- "We want our refusal to be a witnessed Jam contribution"

The mentor's job in that moment: **affirm that this is real**, walk them through the schema fields, and frame the Tuesday share as a refusal-as-contribution rather than a withdrawal.

## What's in this directory

- `sample-team-submission-v0.md` — fictional sample showing the schema filled in for a refusal-only submission

## Files explicitly not in this directory

- An `agentic-build-packet-v0.json` — there isn't one. The exporter refuses (correctly).
- A `runs/` directory — no TELUS lane attempt.
- A separate `witness-record.md` file — the team would draft one Tuesday morning per `docs/tuesday-morning-checklist.md`.

## Mentor script when a team is heading toward refusal

> "What you're surfacing is a real Jam contribution. The kit calls it a refusal, and refusals can be complete offerings. We can write your submission with `build_request.path: note-only`. Your team's Tuesday share will hold the refusal in front of the room. That's not a failure — it's a different shape of success."

## What the discipline asks of a refusal-only submission

The same discipline applies as for any other submission:

- Boundaries named (the refusal itself is often a boundary; name it explicitly)
- Consent fields filled (what may be shared aloud? what stays held?)
- Witnessed working description ("what would success look like" → for a refusal: "the room holds this refusal as a real Jam contribution")
- Facilitator freeze checklist completed

The freeze step matters: **the team is choosing to be witnessed making this refusal**. That's the moment to be sure.

## Boundary

This is a fictional sample. No real team chose this refusal in the 2026-05-25 Jam. The pattern is real; the team and content are illustrative.
