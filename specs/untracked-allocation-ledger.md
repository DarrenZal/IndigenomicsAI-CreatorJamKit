---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: flow_funding
last_updated: 2026-05-17
---

# Untracked Allocation Ledger

## Invitation

Build a ledger for recording that support was allocated without turning every gift, favor, or relational act into surveillance.

## What Could Be Built

- A simple allocation record format.
- A privacy-preserving summary view.
- A receipt that says what was recorded and what was deliberately left untracked.
- A facilitator checklist for deciding when not to record.

## Inputs

- `allocation_id`
- `allocation_type`: money, time, material, introduction, care, knowledge, infrastructure
- `public_summary`
- `private_notes_pointer`
- `recipient_visibility`
- `funder_visibility`
- `amount_visibility`
- `reviewer`
- `receipt_policy`
- `not_tracked_reason`

## Outputs

- Allocation receipt.
- Public aggregate summary.
- Private steward note pointer.
- Not-tracked register.

## Acceptance Criteria

- An allocation can be acknowledged without exposing amount, recipient, or funder identity.
- The ledger can record "not tracked by design" as a first-class outcome.
- Public summaries separate aggregate support from identifiable records.
- Reviewers can flag extractive accounting pressure.
- Withdrawal or correction can update public summaries.

## Refusal Boundaries

- Do not make relational generosity legible just because software can.
- Do not expose participant finances without explicit approval.
- Do not infer hidden allocations.
- Do not use this ledger for tax, compliance, or investment reporting without a separate reviewed spec.

## First Build Step

Create six allocation fixtures: two public, two private-summary-only, and two deliberately untracked.

## Source Notes

Synthesized from flow-funding notes about wise legibility, Creator Jam receipt practices, and commitment pool review boundaries.
