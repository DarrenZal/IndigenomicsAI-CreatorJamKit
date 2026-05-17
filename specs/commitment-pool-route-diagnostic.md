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
