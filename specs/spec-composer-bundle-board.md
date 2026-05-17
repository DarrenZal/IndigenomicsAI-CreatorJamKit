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
