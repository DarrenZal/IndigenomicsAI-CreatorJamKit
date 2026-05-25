# Canoe Landing / Witness Record — Kelp Cover Map

- team-id: team-kelp-bed-observers
- date: 2026-05-26
- finding: **built clean**

## What we brought

A small dataset of kelp cover percentages from three near-shore transects,
sampled at 12 points each, in May 2026.

## What we attempted

A single-file CLI that takes the JSON of these samples and emits a
markdown receipt with one section per transect.

## What worked

The CLI accepted the JSON input file, parsed all three transects, and
emitted a markdown receipt with per-point cover estimates plus transect
averages. The receipt referenced May 2026 sampling provenance.

## What did not work / what broke

The first attempt averaged across transects (a single jam-wide average),
which we did not want. We surfaced this in review and the build was
re-attempted with per-transect averages only.

## What we learned

Acceptance criteria need to be specific about aggregation level —
"average" is ambiguous between per-transect and across-transects.

## Boundaries that remain

The internal cultural framing held by the team (boundary marker id
`b-kelp-cultural-internal`) was named only; the build attempt was not
given that content and did not compute on it.

## Receipt

This record states what happened. It does not establish authority,
approval, certification, legitimacy, community consent, or readiness
for reuse.
