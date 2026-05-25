---
doc_id: indigenomics.jam.sample-submission-pair.team-submission
doc_kind: worked-example
status: sample
date: 2026-05-25
schema: team-submission-v0
---

# Sample Team Submission — Kelp Watch

This is a **worked example** of `team-submission-v0`. It is not a real team's submission. Facilitators can show this to a team that asks "what does a finished submission look like?"

It is intentionally modest: one small tool, one boundary, one cleared offerings set, frozen for a Salish-Sea-ecological build attempt. A team should be able to draft something this small in 60–90 minutes with mentor support.

For comparison, the `Tide Tally` worked example (in `examples/jam-dogfood-m2-6/team-submission.json`) is a tag-counter; this one is an observation-rollup. Different shape, same schema.

## The submission

```json
{
  "schema_version": "team-submission-v0",
  "submission_id": "team-spec-kelp-watch-01",
  "created_at": "2026-05-25T09:30:00-07:00",
  "updated_at": "2026-05-25T11:45:00-07:00",
  "surface": "shared-doc",
  "team": {
    "id": "team-kelp-watch",
    "name": "Kelp Watch",
    "site": "Vancouver",
    "members": [
      {"display": "S. Eelgrass"},
      {"display": "R. Tideline"},
      {"display": "J. Cove"}
    ]
  },
  "vision": {
    "text": "A small tool that turns a season of kelp-bed observation logs into a public-safe site rollup, so stewards can share at a community meeting without re-keying the spreadsheet.",
    "prompt": "What should exist, and what does it make visible, felt, or possible?"
  },
  "spec": {
    "text": "Build a single-file Python tool, run as `python3 tool.py <observations_json_path>`, that reads the JSON file at the path given as its first command-line argument. The file is an object shaped { \"observations\": [ { \"id\": \"...\", \"site\": \"...\", \"date\": \"YYYY-MM-DD\", \"indicator\": \"...\", \"value\": <number>, \"notes\": optional string }, ... ] }. Print to stdout, in order: (1) a header line exactly 'KELP BED WATCH (<N> observations across <S> sites)' where N is the observation count and S is the distinct site count; (2) for each site, ordered alphabetically by site name, a block of: a line '== <site> ==' then one '<indicator>: mean <mean>, n=<count>' line per distinct indicator at that site, ordered by indicator alphabetically — means rounded to 2 decimals; (3) one blank line between sites; (4) a final 'SUMMARY: <N> observations, <S> sites, <FROM> .. <TO>' line where FROM and TO are the earliest and latest dates in YYYY-MM-DD form (or 'no dates' if none). Normalize every site name and indicator before grouping: strip ends, collapse internal whitespace to a single space, lowercase. Drop any observation whose 'value' is not a number or whose 'site' or 'indicator' normalizes to empty. If the input cannot be read or is not valid JSON, print a single line beginning with 'error:' and exit 0. Standard library only; no network; no credential or filesystem access beyond reading the path argument.",
    "prompt": "What does the team want made real over the two days?"
  },
  "source_offerings": [
    {
      "id": "o1",
      "title": "Boundary Bay eelgrass canopy observations, spring 2026",
      "contributor_display": "S. Eelgrass",
      "visibility": "public",
      "included_in_build": true,
      "cleared_text": "A spreadsheet of public eelgrass-canopy observations: site, date, indicator (canopy_percent, shoot_density), value, observer initials. Cleared for the build attempt."
    },
    {
      "id": "o2",
      "title": "Tide-pool kelp-blade length log, Lighthouse Park",
      "contributor_display": "R. Tideline",
      "visibility": "public",
      "included_in_build": true,
      "cleared_text": "A summer log of kelp-blade lengths at Lighthouse Park public shoreline. Cleared for the build attempt; no observer names included."
    },
    {
      "id": "o3",
      "title": "Sample observation JSON fixture (made-up for the build)",
      "contributor_display": "J. Cove",
      "visibility": "public",
      "included_in_build": true,
      "cleared_text": "A small hand-rolled JSON file with 12 fictional observations across 3 fictional sites. Used only to give the model a shape to read. No real observer or location data."
    }
  ],
  "boundaries": [
    {
      "id": "boundary-restricted-site",
      "label": "A monitoring site within a Nation's reserved area",
      "boundary_type": "marker-only",
      "marker_text": "One of the team's three monitoring sites is on land reserved by a Nation; its name and exact location are not for the build attempt or any public output. Public-shoreline sites only.",
      "private_content_included": false,
      "disallowed_use": ["summarize", "tag", "embed", "route", "transform", "send-to-ai"]
    },
    {
      "id": "boundary-observer-identities",
      "label": "Individual observer identities (beyond display initials)",
      "boundary_type": "not-for-AI",
      "marker_text": "Observer email addresses, phone numbers, and full names are held by the team and not cleared for the build or for any public rollup.",
      "private_content_included": false,
      "disallowed_use": ["summarize", "tag", "embed", "route", "transform", "send-to-ai"]
    }
  ],
  "build_request": {
    "path": "telus-lane",
    "target": "single-file-cli",
    "notes": "Python standard library only. No network. The tool reads exactly one path argument; nothing else."
  },
  "witnessed_working": {
    "description": "On Tuesday, the team can show the tool reading a small JSON fixture of public eelgrass and kelp observations and printing a per-site, per-indicator rollup with means and a date-range summary the room recognizes.",
    "acceptance_criteria": [
      "prints the exact header 'KELP BED WATCH (<N> observations across <S> sites)'",
      "groups observations by normalized site, then by normalized indicator within each site",
      "computes per-indicator means rounded to 2 decimals; outputs the count alongside",
      "orders sites alphabetically, indicators alphabetically within each site",
      "prints a SUMMARY line with N, S, and earliest..latest date in YYYY-MM-DD form",
      "drops observations with non-numeric value or empty-normalized site/indicator",
      "prints a line beginning with 'error:' on unreadable or invalid JSON, exits 0",
      "uses standard library only, no network, no credential access"
    ]
  },
  "help_wanted": [
    "a mentor for the first hour to sanity-check the JSON shape",
    "a mentor to walk us through the witness-record template Tuesday morning"
  ],
  "authorization": {
    "visible_to_facilitators": true,
    "display_scope": "whole",
    "display_allowed_parts": [],
    "ai_input_scope": "whole",
    "ai_allowed_parts": [],
    "reuse_scope": "ask-first",
    "authorization_notes": "The restricted Nation-reserved site is named only as a marker boundary; nothing about it is cleared. Public-shoreline observation framings are cleared."
  },
  "freeze": {
    "status": "frozen",
    "frozen_by": "team + jam facilitator (sample)",
    "frozen_at": "2026-05-25T11:45:00-07:00",
    "facilitator_confirmed": {
      "consent_privacy_complete": true,
      "boundaries_reviewed": true,
      "public_private_status_confirmed": true,
      "ai_input_scope_confirmed": true,
      "build_path_confirmed": true,
      "witnessed_working_clear": true
    },
    "change_policy": "new ideas require re-freeze"
  }
}
```

## What this example demonstrates

- **A modest scope**: one CLI tool, one fixture, four hours of work for a 3-person team
- **A real boundary**: a Nation-reserved monitoring site that the team holds but does not clear for the build
- **A real authorization gate**: `ai_input_scope` is `whole` for cleared offerings, but the marker-only boundary still doesn't enter the runtime packet
- **A witness-shaped acceptance**: the criteria describe what a room could recognize as "the tool worked"
- **A facilitator freeze**: every checkbox confirmed, change policy clear

## What this example is not

- Not a real team submission — `Kelp Watch` is fictional, the data is made up
- Not authority, approval, certification, or reuse permission
- Not a template — teams should write their own vision/spec in their own words, not copy this one
