---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: private_learning
last_updated: 2026-05-17
---

# Private Learning Ledger

## Invitation

Build a ledger that lets a system learn from reviewed steward actions and outcomes without training on raw protected data or exposing private context.

## What Could Be Built

- A steward action log.
- A learning summary that only uses approved projections.
- A withdrawal propagation report.
- A public/private boundary checker.

## Inputs

- `record_id`
- `record_class`
- `visibility_tier`
- `do_not_compute`
- `action_type`: review, approve, reject, withdraw, correct, publish, hide, route, do_not_route
- `actor`
- `timestamp`
- `rationale`
- `source_diagnostic`
- `raw_content_pointer`
- `external_surface`

## Outputs

- Private Learning Ledger.
- Approved learning summary.
- Withdrawal propagation report.
- Boundary diagnostics.

## Acceptance Criteria

- Raw workshop or protected data is not used for model training.
- `do_not_compute` records are not embedded, indexed, routed, summarized, or entity-resolved.
- Public learning summaries use reviewed projections only.
- Withdrawals and corrections identify affected surfaces.
- The ledger records who reviewed the learning step and why.

## Refusal Boundaries

- Do not claim cryptographic privacy or private machine learning unless actually implemented and reviewed.
- Do not use private material to improve public models by default.
- Do not hide that a public summary came from reviewed projections rather than raw data.
- Do not keep using withdrawn data.

## First Build Step

Create a fixture with five steward actions and generate a learning summary plus one withdrawal propagation report.

## Source Notes

Synthesized from private learning and data sovereignty specs, Creator Jam consent review examples, and local-first AI use boundaries.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
