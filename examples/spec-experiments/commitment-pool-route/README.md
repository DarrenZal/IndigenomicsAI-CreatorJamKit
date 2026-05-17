# Commitment Pool Route Spec Experiment

This experiment instantiates `specs/commitment-pool-route-diagnostic.md` with public-sample material only.

## Files

- `fixtures/commitment-pool-route-fixture.json` contains three candidate declarations, two pools, one standing refusal marker, one constraint, and expected route diagnostics.
- `reports/commitment-pool-route-diagnostic.md` is the generated sample diagnostic for the fixture.

## Participant Safety

- All names, places, organizations, pools, declarations, and evidence references are fictional public-sample content.
- The fixture does not contain participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material.
- The share-policy block uses a marker only. It does not reveal protected content and does not search for missing details.
- The diagnostic does not route money, commitments, obligations, authority, or access.

## Acceptance Checks

| Check | Fixture Coverage |
|---|---|
| Missing bioregion, timeframe, routing tags, or evidence are reported clearly. | `candidate:CPR-002` reports missing `bioregion_uri` and missing evidence. |
| Capacity constraints can block routing. | `candidate:CPR-002` targets a zero-capacity pool and receives `hard_stop`. |
| Share policies can block routing without exposing protected content. | `candidate:CPR-003` is blocked by `protected_private_no_ai_no_public_route` and remains redacted. |
| Refusals and `do_not_compute` records are honored. | `standing_refusal:CPR-RF-001` and `candidate:CPR-003` are excluded from route computation. |
| Governance gaps are surfaced as review needs, not auto-resolved. | The report names missing governance review for the zero-capacity/missing-field case. |

## Refusal Boundaries

- Do not automatically route money, commitments, obligations, authority, or access.
- Do not compute legitimacy.
- Do not route around a refusal.
- Do not search protected records to complete a pool.
- Do not infer missing private details from a share-policy marker.
