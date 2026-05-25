---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: commitment_pooling
last_updated: 2026-05-17
---

# Commitment Pool Route Diagnostic

## Invitation

Build a diagnostic that checks whether offers, needs, commitments, refusals, and constraints can route into a candidate commitment pool.

## What Could Be Built

- A small commitment pool schema.
- A fixture with offers, needs, commitments, refusals, and pool rules.
- A diagnostic runner that explains why a record is route-ready, needs review, or must stop.
- A repair-path view for missing fields and governance gaps.

## Inputs

- `candidate_id`
- `declaration_type`: offer, need, commitment, refusal, constraint
- `issuer`
- `beneficiary`
- `quantity`
- `unit`
- `estimated_value`
- `timeframe`
- `routing_tags`
- `bioregion_uri`
- `evidence_pointers`
- `share_policy`
- `target_pool`
- `pool_capacity`
- `pool_rules`

## Outputs

- Route status: route_ready, needs_review, hard_stop, not_computable.
- Diagnostic list.
- Pool capacity summary.
- Repair path recommendations.

## Acceptance Criteria

- Missing bioregion, timeframe, routing tags, or evidence are reported clearly.
- Capacity constraints can block routing.
- Share policies can block routing without exposing protected content.
- Refusals and `do_not_compute` records are honored.
- Governance gaps are surfaced as review needs, not auto-resolved.

## Refusal Boundaries

- Do not automatically route money, commitments, or authority.
- Do not compute legitimacy.
- Do not route around a refusal.
- Do not search protected records to complete a pool.

## First Build Step

Create a replay fixture with three candidate declarations and two pools, including one zero-capacity pool and one share-policy block.

## Source Notes

Synthesized from local commitment bundle route diagnostic specs, commitment pool research, and Creator Jam bundle templates.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
