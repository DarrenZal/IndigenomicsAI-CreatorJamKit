---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: flow_funding
last_updated: 2026-05-17
---

# Flow Funding Frontier Map

## Invitation

Build a map of the next fundable edges between dreams, commitments, pools, witnessed work, and retroactive support.

## What Could Be Built

- A graph view of dreams, needs, offers, commitments, receipts, pools, and funding openings.
- A "frontier queue" that shows where a small contribution could unlock more flow.
- A pool brief that explains what is ready, what is blocked, and what needs witness or evidence.
- A demo flow from dream to commitment to receipt to retroactive support.

## Inputs

- `node_id`
- `node_type`: dream, need, offer, commitment, pool, receipt, retro_certificate, funding_opening
- `relationship_type`: supports, depends_on, fulfills, witnesses, requests, unlocks
- `amount_or_quantity`
- `currency_or_unit`
- `timeframe`
- `evidence_pointers`
- `witness_records`
- `visibility_tier`
- `review_state`

## Outputs

- Flow Funding Frontier Map.
- Candidate funding edges.
- Pool readiness summary.
- Witness and receipt gaps.
- Optional public sample story.

## Acceptance Criteria

- The map can show both prospective commitments and completed witnessed work.
- A pool cannot be marked ready if review, evidence, consent, or capacity is missing.
- The system distinguishes tracked funding from untracked or relational support.
- Public exports do not expose protected participant details.
- The map makes uncertainty visible instead of filling gaps with speculation.

## Refusal Boundaries

- Do not rank people by fundability.
- Do not imply investment advice.
- Do not treat a graph edge as consent.
- Do not publish private commitments or refusals.

## First Build Step

Create a ten-node fixture and render a static map with three frontier edges and their blockers.

## Source Notes

Synthesized from RegenAI flow-funding essays, commitment pool notes, and Creator Jam candidate bundle work.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
