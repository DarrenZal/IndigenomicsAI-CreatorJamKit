---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: spec_driven_development
last_updated: 2026-05-17
---

# Spec Composer Bundle Board

## Invitation

Build a tool that helps facilitators and participants compose spec fragments into candidate collective builds, select one bundle, and freeze build instructions.

## What Could Be Built

- A spec fragment intake board.
- A candidate bundle composer.
- A dependency and boundary checker.
- A selected bundle freeze step.
- An export to build attempt instructions.

## Inputs

- `spec_fragment_id`
- `offering_id`
- `capability`
- `needed_inputs`
- `expected_outputs`
- `acceptance_criteria`
- `refusal_boundaries`
- `dependencies`
- `permission_state`
- `candidate_bundle_id`

## Outputs

- Candidate bundle board.
- Bundle fit diagnostics.
- Selected bundle receipt.
- Build attempt instructions.
- Reviewer checklist.

## Acceptance Criteria

- Fragments can be grouped without losing their original refusal boundaries.
- Candidate bundles show dependencies and unresolved questions.
- A selected bundle is frozen before build attempts start.
- Build instructions include acceptance criteria and reviewer checks.
- The composer can reject a bundle that requires protected data or unclear consent.

## Refusal Boundaries

- Do not treat composition as consent.
- Do not merge fragments in a way that changes participant intent.
- Do not hide dependency gaps to make a bundle look build-ready.
- Do not ask AI to resolve cultural, governance, or consent questions.

## First Build Step

Create a board fixture with six spec fragments, three candidate bundles, one selected bundle, and one rejected bundle.

## Source Notes

Synthesized from Creator Jam composition v0 materials, offering quick cards, bundle templates, and selected build instruction flows.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
