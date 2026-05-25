---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: sensors
last_updated: 2026-05-17
---

# Sensor To Receipt Pipeline

## Invitation

Build a small pipeline that turns sensor readings or field observations into reviewable evidence packets and witness receipts.

## What Could Be Built

- A sensor reading schema.
- A citizen observation form.
- A packet builder that links observations to claims or commitments.
- A reviewer step for calibration, context, permission, and uncertainty.
- A receipt that records what was observed and how it was reviewed.

## Inputs

- `observation_id`
- `observation_type`: sensor_reading, field_note, photo, audio, manual_count, repair_event
- `source_device_or_person`
- `location_precision`
- `time_window`
- `measurement`
- `unit`
- `calibration_state`
- `evidence_pointer`
- `visibility_tier`
- `review_state`
- `sensitive_location_flag`

## Outputs

- Sensor or observation evidence packet.
- Review diagnostics.
- Claim or commitment link.
- Witness receipt.
- Public-safe summary.

## Acceptance Criteria

- Sensor readings and human observations can share one packet model.
- Location precision can be reduced for sensitive places.
- Calibration and uncertainty are visible.
- Public receipts do not expose protected locations or identities.
- Records can be withdrawn, corrected, or marked not-for-computation.

## Refusal Boundaries

- Do not treat a raw sensor reading as a verified claim.
- Do not publish sensitive ecological or cultural locations.
- Do not infer compliance, enforcement, or eligibility without a separate reviewed spec.
- Do not assume a device owner has authority to publish place-based knowledge.

## First Build Step

Create three sample packets: one temperature sensor reading, one field note, and one restoration repair event, then produce a witness receipt for each.

## Source Notes

Synthesized from bioregional ecological monitoring notes, RegenAI sensor-to-claim patterns, and Creator Jam witness receipt templates.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
