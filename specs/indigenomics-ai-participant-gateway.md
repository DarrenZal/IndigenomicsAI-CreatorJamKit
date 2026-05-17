---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: indigenomics_ai_app
last_updated: 2026-05-17
---

# Indigenomics AI Participant Gateway

## Invitation

Build the entry path for a participant who receives an invite, understands the boundaries, redeems access, and starts a jam offering without confusion.

## What Could Be Built

- Invite token issue and redeem flow.
- Gateway agreement screen.
- Participant profile with visibility defaults.
- First offering quick-card flow.
- Receipt showing what the participant agreed to and what remains private.

## Inputs

- `invite_token`
- `participant_display_name`
- `role`
- `agreement_version`
- `accepted_boundaries`
- `default_visibility`
- `ai_use_preference`
- `offering_start`
- `receipt_policy`

## Outputs

- Gateway access record.
- Participant agreement receipt.
- First offering draft.
- Review-needed flags.
- Facilitator handoff note.

## Acceptance Criteria

- Tokens can be redeemed once or according to an explicit policy.
- The participant sees boundaries before submitting material.
- Default visibility is conservative.
- AI use preferences are recorded separately from public display consent.
- A facilitator can see which participant records need follow-up.

## Refusal Boundaries

- Do not treat token redemption as consent to publish.
- Do not require a participant to disclose private identity details to make an offering.
- Do not feed submitted material to AI unless that use is explicitly approved.
- Do not bury withdrawal, refusal, or local-only options.

## First Build Step

Create a mock gateway flow with token redeem, agreement receipt, and one offering quick-card draft.

## Source Notes

Synthesized from IndigenomicsAI gateway/token surfaces, gateway agreement specs, and Creator Jam participant handout work.
