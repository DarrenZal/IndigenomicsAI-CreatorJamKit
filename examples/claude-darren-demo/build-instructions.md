# Build Instructions — Kelp-Bed Stewardship Intelligence Report

A single-file Python tool composed from two team submissions for the Creator
Jam. It reads two JSON files — kelp-canopy observations and stewardship-action
entries — and prints a joint report that pairs each site's kelp-bed condition
with the stewardship actions that happened in that bioregion over the season.

These build instructions are **frozen**: they are the exact, complete
description the build works from. Every behaviour below is intended and
testable.

## Invocation

    python3 tool.py <observations_json_path> <actions_json_path>

Read each JSON file at its given command-line argument path. Print all results
to stdout. Exit with status 0 on success. Both arguments are required; with
fewer arguments, print a single line beginning with `error:` and exit 0.

## Input 1 — kelp-canopy observations

A JSON object:

    { "observations": [
        { "date": "2025-08-01", "site": "Boundary Bay",
          "canopy_percent": 64, "observer_alias": "obs-a",
          "bioregion": "Strait of Georgia" },
        ...
    ] }

- `observations` is a list. It may be empty.
- Each entry has `date` (ISO string), `site` (string),
  `canopy_percent` (number 0-100), `observer_alias` (string), and
  `bioregion` (string).
- Entries with malformed `canopy_percent` (not a number, or outside 0-100)
  are dropped silently.

## Input 2 — stewardship actions

A JSON object:

    { "actions": [
        { "date": "2025-09-15", "bioregion": "Strait of Georgia",
          "action_type": "kelp-count", "site_alias": "site-a" },
        ...
    ] }

- `actions` is a list. It may be empty.
- Each entry has `date` (ISO string), `bioregion` (string),
  `action_type` (string), `site_alias` (string).
- `action_type` is one of: `work-party`, `beach-cleanup`, `eelgrass-survey`,
  `kelp-count`, `planting`. Other values are dropped silently.

## Output

Print exactly these parts, in order:

1. a header line;
2. one section per **bioregion** that appears in EITHER input (sorted
   alphabetically ascending), each containing:
   - a bioregion sub-header;
   - a `KELP:` block of per-site condition lines for sites in that bioregion;
   - an `ACTIONS:` block of per-action-type counts in that bioregion;
3. one blank line;
4. a summary line.

### 1. Header line

    KELP-BED STEWARDSHIP REPORT (<B> bioregions)

`<B>` is the number of distinct bioregions across both inputs combined. Always
use the word `bioregions` — do not change it to `bioregion` when `B` is 0 or 1.

### 2. Per-bioregion sections

For each bioregion, print:

    == <bioregion> ==
    KELP:
      <site>: <condition> (mean canopy <X>%)
      ...
    ACTIONS:
      <action_type>: <count>
      ...

#### KELP block rules

- One line per site that has at least one valid observation in this bioregion.
- `<condition>` is assigned from the per-site mean of `canopy_percent`:
  - mean >= 60 -> `healthy`
  - 30 <= mean < 60 -> `declining`
  - mean < 30 -> `stressed`
- `<X>` is the per-site mean rounded to the nearest integer (round half away
  from zero — i.e. 59.5 -> 60).
- Sort site lines alphabetically ascending by site name.
- If this bioregion has no kelp observations, print a single line `  none`
  under `KELP:`.

#### ACTIONS block rules

- One line per distinct `action_type` recorded in this bioregion.
- Sort by count descending, then action_type alphabetically ascending.
- If this bioregion has no actions, print a single line `  none` under
  `ACTIONS:`.

### 3. Blank line

Print exactly one empty line between the last bioregion section and the
summary line.

### 4. Summary line

    SUMMARY: <H> healthy / <D> declining / <S> stressed sites, <A> stewardship actions

- `<H>`, `<D>`, `<S>` are total counts of sites in each condition across all
  bioregions.
- `<A>` is the total count of valid stewardship actions across all bioregions.
- Always use the word forms unchanged, whatever the numbers are.

The summary line is always printed — including when both inputs are empty
(`SUMMARY: 0 healthy / 0 declining / 0 stressed sites, 0 stewardship actions`).

## Malformed input

If either file cannot be read or does not contain valid JSON, print to stdout
a single line beginning with `error:` (for example `error: invalid JSON in
observations`) and exit with status 0. Do not print a Python traceback or any
partial report.

## Worked example

`observations.json`:

    { "observations": [
        {"date":"2025-08-01","site":"Boundary Bay","canopy_percent":70,
         "observer_alias":"obs-a","bioregion":"Strait of Georgia"},
        {"date":"2025-09-01","site":"Boundary Bay","canopy_percent":50,
         "observer_alias":"obs-b","bioregion":"Strait of Georgia"}
    ] }

`actions.json`:

    { "actions": [
        {"date":"2025-09-15","bioregion":"Strait of Georgia",
         "action_type":"kelp-count","site_alias":"site-a"},
        {"date":"2025-10-01","bioregion":"Strait of Georgia",
         "action_type":"kelp-count","site_alias":"site-a"},
        {"date":"2025-10-15","bioregion":"Strait of Georgia",
         "action_type":"beach-cleanup","site_alias":"site-a"}
    ] }

Output:

    KELP-BED STEWARDSHIP REPORT (1 bioregions)
    == Strait of Georgia ==
    KELP:
      Boundary Bay: healthy (mean canopy 60%)
    ACTIONS:
      kelp-count: 2
      beach-cleanup: 1

    SUMMARY: 1 healthy / 0 declining / 0 stressed sites, 3 stewardship actions

## Constraints

- Python standard library only. No third-party packages.
- No network access. Do not prompt for input. Read only the two file paths
  given on the command line; write only to stdout.
- The tool must never reference, summarize, or print any "host-Nation
  stewardship cycle reference" content — that boundary is marker-only and its
  content is not in either input.
