# Canoe Landing / Witness Record — Kelp Bed Observers + Steward Calendar (joint)

- packet: `claude-darren-composed`
- build model: `qwen-3.6-35b` (TELUS build-attempt lane)
- date: 2026-05-26
- finding: **improved**

## What we brought

A small CLI that pairs a season's kelp-bed condition assessments with the stewardship actions that happened in each bioregion, so a community group can read which beds are stressed AND what work has been showing up around them.

## What we attempted

A build attempt on the frozen build packet via the TELUS build-attempt lane. Build target: one single-file Python tool, standard library only.

## What worked

The build attempt passed 2 of 8 tests.

## What did not work / what broke

Acceptance tests still failing: __main__.StewardshipReportTest.test_1_worked_example, __main__.StewardshipReportTest.test_2_three_conditions_two_bioregions, __main__.StewardshipReportTest.test_3_actions_only_bioregion, __main__.StewardshipReportTest.test_4_both_empty, __main__.StewardshipReportTest.test_5_unknown_action_type_dropped, __main__.StewardshipReportTest.test_8_canopy_rounding_half_away_from_zero.

## What we learned

This packet needs another repair round or a human builder.

## Boundaries that remain

Marker-only records named in the packet were not given to the build attempt and were not computed on: team-kelp-bed-observers::b1, team-steward-calendar::b1, team-steward-calendar::b2.

## Receipt

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse. Composition does not dissolve either team's boundaries; both teams' marker-only records remain marker-only after this build attempt and after this witness record.
