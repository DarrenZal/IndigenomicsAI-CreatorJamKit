---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: claims
last_updated: 2026-05-26
depends_on:
  - witness-record-interop-profile
---

# Claims Evidence Coherence Report

## Invitation

Build a report that helps stewards see whether a public claim is supported, stale, overbroad, contested, blocked by permissions, or ready for a specific use.

## What Could Be Built

- A claim intake form.
- A small evidence pointer registry.
- A deterministic report generator.
- A reviewer screen for marking gaps and repair paths.

## Inputs

- `claim_id`
- `claim_text`
- `claim_subject`
- `claim_type`: descriptive, commitment_status, outcome, impact, risk, eligibility
- `intended_use`
- `visibility_tier`
- `evidence_pointers`
- `evidence_type`
- `evidence_date`
- `reviewer`
- `review_date`
- `restrictions`
- `confidence`
- `related_claims`

## Outputs

- Claims Evidence Coherence Report.
- Claim status: ready_for_use, missing_evidence, stale_evidence, needs_review, contested, overbroad, visibility_blocked, do_not_compute.
- Evidence freshness table.
- Repair path list.

## Acceptance Criteria

- Public claims require evidence and reviewer context.
- Stale evidence is surfaced using claim-type freshness windows.
- Conflicting claims remain visible and are not silently merged.
- `do_not_compute` records are excluded from summarization, routing, and public display.
- The report states the specific intended use it supports or blocks.

## Refusal Boundaries

- Do not adjudicate ultimate truth.
- Do not produce a legitimacy score.
- Do not launder weak evidence into strong public language.
- Do not train on raw private evidence.

## First Build Step

Create a fixture with five claims and six evidence pointers, then generate one markdown report.

## Source Notes

Synthesized from local claims evidence coherence specs, claims engine implementation notes, and the Creator Jam reviewer and witness templates.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
