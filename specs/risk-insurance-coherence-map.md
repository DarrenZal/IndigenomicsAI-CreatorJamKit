---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: insurance_risk
last_updated: 2026-05-17
---

# Risk and Insurance Coherence Map

## Invitation

Build a resilience risk map that helps a group see known signals, stale evidence, missing context, and candidate investments without becoming a premium model or underwriting tool.

## What Could Be Built

- A watershed-scale risk coherence map.
- A diagnostic packet for hazards such as drought, fire weather, flood watch, or recovery.
- A resilience investment shortlist.
- A reviewer checklist for sensitive sites, stale layers, and unsupported claims.

## Inputs

- `area_of_interest`
- `hazard_family`
- `regime`: baseline, drought, fire_weather, flood_watch, recovery
- `public_layers`
- `sensor_or_weather_signals`
- `local_observations`
- `infrastructure_or_livelihood_records`
- `restoration_commitments`
- `evidence_pointers`
- `freshness`
- `visibility_tier`
- `sensitive_location_flag`

## Outputs

- Risk Coherence Map.
- Risk Diagnostic Packet.
- Resilience Investment Shortlist.
- Missing evidence and stale layer list.
- Sensitive boundary report.

## Acceptance Criteria

- The map states what is known, stale, missing, sensitive, and review-required.
- The map can show resilience actions ready for steward review.
- Sensitive sites can be masked or excluded.
- The packet distinguishes public signals from local-only observations.
- No output suggests pricing, underwriting, eligibility, or actuarial confidence.

## Refusal Boundaries

- Do not create premium, underwriting, eligibility, or actuarial models.
- Do not expose sensitive cultural, ecological, or infrastructure locations.
- Do not infer risk for a person, household, or specific private property.
- Do not present climate or hazard signals as certainty.

## First Build Step

Create a one-page risk coherence packet for one fictional watershed with three public layers, two local observations, one stale signal, and two candidate resilience actions.

## Source Notes

Synthesized from bioregional-coordination risk coherence and insurance notes, with Creator Jam permission boundaries.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
