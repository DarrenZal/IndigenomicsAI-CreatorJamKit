---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: indigenomics_ai_app
last_updated: 2026-05-17
---

# Indigenomics AI Graph Chat Witness Sidecar

## Invitation

Build a sidecar that connects graph nodes, chat answers, citations, claims, evidence, and witness records so users can see what an answer is grounded in.

## What Could Be Built

- A node sidecar that lists source documents, claims, evidence, and witness records.
- A chat citation panel that separates answer text from source status.
- A "needs review" state for unsupported or stale claims.
- A receipt for AI-assisted summaries.

## Inputs

- `node_id`
- `chat_turn_id`
- `answer_text`
- `source_documents`
- `citation_links`
- `claims`
- `evidence_pointers`
- `witness_records`
- `review_state`
- `ai_use_receipt`

## Outputs

- Graph/chat witness sidecar.
- Citation and evidence table.
- Claim review diagnostics.
- AI-assisted answer receipt.
- Follow-up repair tasks.

## Acceptance Criteria

- Users can inspect which sources support an answer.
- Claims are separate from citations and can have their own review status.
- Stale, missing, contested, or local-only sources are visible.
- AI-assisted answers include a receipt of source material and reviewer status.
- Protected source content does not leak through citations or summaries.

## Refusal Boundaries

- Do not present chat answers as authoritative because they have citations.
- Do not expose private source content in snippets.
- Do not auto-upgrade a citation into a verified claim.
- Do not hide contested or missing evidence.

## First Build Step

Create a static sidecar fixture for one graph node, one chat answer, three citations, two claims, and one reviewer diagnostic.

## Source Notes

Synthesized from IndigenomicsAI graph/chat app surfaces, claims evidence specs, and witness receipt patterns.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
