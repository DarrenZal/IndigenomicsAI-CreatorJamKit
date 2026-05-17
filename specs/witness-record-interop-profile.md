---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: witnessing
last_updated: 2026-05-17
---

# Witness Record Interop Profile

## Invitation

Build a small record format that can carry a claim, evidence pointer, witness event, attestation, promise, or receipt across different tools without pretending to certify authority.

## What Could Be Built

- A JSON schema for a portable witness record.
- A fixture set with one claim, one evidence pointer, one commitment, one review, and one receipt.
- A validator that catches missing consent, stale evidence, overbroad public claims, and unsupported authority language.
- A simple timeline view showing how multiple witnesses relate to one statement or commitment.

## Inputs

- `record_id`
- `statement`
- `record_type`: claim, witness, attestation, promise, refusal, review, receipt
- `subject`
- `actor_or_issuer`
- `witnesses`
- `evidence_pointers`
- `visibility_tier`
- `permission_state`
- `review_state`
- `created_at`
- Optional: `anchor_pointer`, `supersedes`, `related_records`

## Outputs

- Portable witness record JSON.
- Human-readable witness card.
- Review diagnostics.
- Optional anchor payload that exposes only approved fields.

## Acceptance Criteria

- The same profile can represent past witness events, present attestations, and future promises.
- Multiple witnesses can be attached without collapsing them into one score.
- A record can say "reviewed", "contested", "withdrawn", "private", or "not for computation".
- Public export excludes protected content and private evidence.
- The validator rejects records that imply certification, legitimacy, or cultural authority without explicit review authority.

## Refusal Boundaries

- Do not compute a trust score.
- Do not treat a witness record as proof of cultural authority.
- Do not publish private evidence to make a public receipt look stronger.
- Do not require blockchain anchoring for a record to be meaningful.

## First Build Step

Create five fixture records and a `validate-witness-record` script that prints diagnostics for each one.

## Source Notes

Synthesized from the RegenAI claims engine notes, Waka/Regen interop notes, multi-witness inference sketches, and Creator Jam receipt work.
