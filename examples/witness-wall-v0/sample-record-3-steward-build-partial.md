# Canoe Landing / Witness Record — Restoration Site Picker

- team-id: team-steward-calendar
- date: 2026-05-26
- finding: **built, partial — 2/3 acceptance criteria met**

## What we brought

A specification for a small tool that helps pick restoration sites by
reading a JSON manifest of candidate sites + a JSON manifest of
constraint windows (e.g. tides, salmon spawning windows that should
not be disturbed).

## What we attempted

A single-file CLI build attempt via the TELUS build-attempt lane,
using Gemma 4 31B as the build model.

## What worked

- The CLI reads both JSON inputs without crashing.
- The CLI emits a ranked list of candidate sites.
- The output references the constraint windows verbatim.

## What did not work / what broke

The third acceptance criterion — "the CLI rejects sites whose
constraint windows overlap with the current week" — was not fully
met. The build attempt produced output where the constraint check
ran but only against the FIRST constraint window in the manifest,
not all of them. The build was attempted with one repair against
concrete test feedback; the repair improved the situation but did
not fully resolve it.

## What we learned

For acceptance criteria that reference iteration ("ALL constraint
windows", "EVERY..."), the test file needs to be explicit about
iteration — a single-row passing test is not enough.

## Boundaries that remain

The team's own draft of cultural sensitivity around site selection
(boundary marker id `b-steward-cultural-internal`) was named only;
the build attempt was not given that content and did not compute on
it.

## Receipt

This record states what happened. It does not establish authority,
approval, certification, legitimacy, community consent, or readiness
for reuse. The tool is not production-ready; one build attempt with
one repair surfaced one bug class for further work.
