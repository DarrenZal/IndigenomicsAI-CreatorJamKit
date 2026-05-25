---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: commitments
last_updated: 2026-05-17
---

# Dream To Fulfillment Board

## Invitation

Build a board that tracks the movement from dream to vision, care, offer, need, promise, witnessed commitment, fulfilled work, and receipt.

## What Could Be Built

- A kanban-style board for commitment speech acts.
- A record model for dreams, offers, needs, promises, refusals, commitments, and fulfillment.
- A transition validator.
- A witness receipt rollup for completed work.

## Inputs

- `item_id`
- `speech_act`: dream, vision, care, offer, need, promise, refusal, witnessed_commitment, fulfilled, receipt
- `summary`
- `issuer`
- `beneficiary`
- `timeframe`
- `dependencies`
- `witness_records`
- `evidence_pointers`
- `visibility_tier`
- `review_state`

## Outputs

- Dream to Fulfillment Board.
- Transition diagnostics.
- Commitment bundle candidates.
- Fulfillment receipt rollup.

## Acceptance Criteria

- A dream can remain a dream without being forced into delivery logic.
- Refusals and constraints are visible and respected.
- A promise cannot become a witnessed commitment without witness context.
- Fulfillment requires review or evidence appropriate to the intended use.
- Public board exports use sample-safe summaries.

## Refusal Boundaries

- Do not pressure participants to turn care, story, or dreams into commitments.
- Do not treat a promise as fulfilled because it moved columns.
- Do not publish private relational commitments.
- Do not convert refusals into backlog items.

## First Build Step

Create a board fixture with eight items and two transition diagnostics, then render it as markdown or a small web view.

## Source Notes

Synthesized from stewardship-of-commitments essays, commitment pool notes, and Creator Jam bundle workflows.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
