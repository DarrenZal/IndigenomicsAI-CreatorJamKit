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

Synthesized from the RegenAI claims engine notes, Waka/Regen interop notes where Waka refers to Austin Wade Smith / RiverComputer's project, multi-witness inference sketches, and Creator Jam receipt work.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
