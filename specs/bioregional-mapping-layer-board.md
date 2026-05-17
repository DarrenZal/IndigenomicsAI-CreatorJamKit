---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: bioregional_mapping
last_updated: 2026-05-17
---

# Bioregional Mapping Layer Board

## Invitation

Build a board that helps a group compose ecological, cultural, economic, governance, and geospatial layers without flattening place into a single map.

## What Could Be Built

- A layer catalog for a sample bioregion.
- A map or board that shows which layers are public, local-only, restricted, or absent.
- A consent-gated layer switcher.
- A review queue for layers that need steward approval.

## Inputs

- `layer_id`
- `layer_type`: ecological, cultural, economic, governance, geospatial, relational, story, sensor
- `area_of_interest`
- `source`
- `source_authority`
- `visibility_tier`
- `sensitivity_level`
- `review_state`
- `freshness`
- `use_limitations`

## Outputs

- Bioregional layer board.
- Public layer manifest.
- Restricted layer manifest.
- Missing layer list.
- Review queue.

## Acceptance Criteria

- Layers have explicit visibility and use limitations.
- Cultural or Indigenous layers can be represented as present without exposing protected content.
- The board can show missing, stale, and contested layers.
- Public map exports include only approved layers.
- The system supports multiple scales, such as watershed, neighborhood, corridor, and region.

## Refusal Boundaries

- Do not publish sensitive cultural, ecological, or governance locations.
- Do not treat geospatial precision as more true than relational knowledge.
- Do not merge layers with incompatible permissions.
- Do not use Indigenous names or protocol context without approval from the right authority.

## First Build Step

Create a sample layer catalog with ten fictional layers and render a layer board with visibility filters.

## Source Notes

Synthesized from bioregional-mapping project vision, bioregional-coordination mapping notes, and Creator Jam consent review patterns.
