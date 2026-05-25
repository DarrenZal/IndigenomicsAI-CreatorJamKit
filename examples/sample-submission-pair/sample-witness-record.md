---
doc_id: indigenomics.jam.sample-submission-pair.witness-record
doc_kind: worked-example
status: sample
date: 2026-05-26
team: Kelp Watch
---

# Sample Witness Record — Kelp Watch (Tuesday canoe landing)

This is a **worked example** of what a Tuesday witness record looks like for the Kelp Watch sample submission. It is not a real team's record. Facilitators can show this to a team that asks "what does the Tuesday witness record look like?"

The record states only what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.

---

## Team

Kelp Watch (Vancouver site — S. Eelgrass, R. Tideline, J. Cove)

## Date

2026-05-26

## Receipt statement

This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.

## What we brought

- A spreadsheet of public eelgrass-canopy observations from Boundary Bay (spring 2026)
- A summer log of kelp-blade lengths from Lighthouse Park (public shoreline)
- A small hand-rolled JSON fixture of 13 fictional observations across 3 fictional sites for the build attempt
- One marker-only boundary: a monitoring site within a Nation's reserved area (named only; not cleared for the build)
- One not-for-AI boundary: individual observer identities (held by the team; not cleared)

## What we attempted

A single-file Python CLI that reads a JSON file of observations and prints a per-site, per-indicator rollup with means and a date-range summary. Targeted the TELUS build lane; Python standard library only.

## What worked

- The build lane returned a single-file tool on the first attempt
- All six acceptance-test cases passed:
  - happy path with two sites and two indicators
  - normalization collapsing case + whitespace variants to one bucket
  - drop rules excluding bad-value, empty-site, and empty-indicator rows
  - empty-observations case
  - invalid JSON producing `error:` line + exit 0
  - alphabetical indicator ordering within site
- No excluded-input record appeared in the generated tool or its output (leak check passed)
- No observer names or Nation-reserved site names appeared anywhere in the output

## What did not work / what broke

- The first generation rounded means to 1 decimal instead of 2; the model self-corrected after one repair round when given the failing acceptance-test feedback
- We had to clarify the SUMMARY line wording mid-build; reviewer caught that the model had pluralized "sites" inconsistently when count was 1

## What we learned

- The freeze step was load-bearing — when we tried to add a fourth indicator after freezing, the facilitator made us re-freeze. That felt slow at the moment but kept the build coherent.
- Salish-Sea-ecological framings (eelgrass, kelp-blade length, shoot density, canopy percent) gave us a worked example we could share publicly without crossing into anything that required Nation-specific authorization.
- We learned to keep the marker-only boundary as a one-line label, not a paragraph. That made the leak-check easier to read.

## Boundaries that remain

- The Nation-reserved monitoring site stays held by the team. The build did not see it; the rollup does not display it. We named it; we did not include it.
- Individual observer identities (emails, phone numbers, full names) stay with the team. The rollup uses no observer-identifying information.
- This tool is shared with `reuse_scope: ask-first`. Anyone who wants to reuse it should ask the team again, not assume the witness record grants reuse.

## Closing line

This is not a finished product. It is one team's two-day attempt, witnessed by the room. The next version, if there is one, is the team's call.
