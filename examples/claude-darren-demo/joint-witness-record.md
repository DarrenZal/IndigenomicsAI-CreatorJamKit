---
doc_kind: witness-rollup
status: draft
permission_state: public_sample
team: Kelp Bed Observers + Steward Calendar (joint)
joint_authors:
  - team-kelp-bed-observers
  - team-steward-calendar
date: 2026-05-26
composed_from_packet: claude-darren-composed
---

# Joint Witness Record — Kelp Bed Observers + Steward Calendar

Tuesday canoe-landing record for the composed build attempt. Written
collaboratively by both teams.

## what we brought (per team)

**Kelp Bed Observers (Vancouver).** A season of public-shoreline canopy
observations from Boundary Bay and Lighthouse Park — date, site, canopy
percent, observer alias. A small CLI vision: turn the season into a
plain-language condition report a work-party group could read in five
minutes. One boundary: observer real names live in our roster spreadsheet,
not in any AI input.

**Steward Calendar (Victoria).** A public stewardship-action log across
multiple Salish Sea bioregions — work-parties, beach clean-ups, eelgrass
surveys, kelp counts, plantings. A CLI vision: a per-bioregion calendar
showing seasonal patterns so a new volunteer can see where they fit. Two
boundaries: (a) volunteer real names live in our roster, not in any AI
input; (b) a host-Nation stewardship-cycle reference our partner shared in
confidence — marker-only, named in framing but never in the dataset, the
AI input, or any output.

## what we attempted (joint)

A single composed CLI that reads BOTH cleared inputs (observations +
actions) and prints one joint report: per-bioregion, a kelp-condition
block (per-site mean canopy → healthy / declining / stressed) and a
stewardship-action block (per-action-type counts), with a summary line.
Built via the TELUS lane (Gemma 4 31B + Qwen 3.6 35B in parallel) from the
joint re-frozen `agentic-build-packet-v0` named `claude-darren-composed`.

## what worked

- The composition-merger surfaced the real disagreement (whole vs partial
  authorization) before either team committed to the joint build. We
  resolved it in conversation; the merger gave us the right shape of
  conversation to have.
- Both teams' boundaries carried forward into the build packet's
  `excluded_inputs` namespaced by team. We checked: the generated code and
  its output reference neither team's marker-only content.
- Gemma 4 31B: 7/8 on attempt 1, 8/8 after one repair pass — a working
  composed tool inside one short jam window.
- The joint shape made something neither of us had before: a per-bioregion
  view of *where the work is showing up against where the kelp is
  stressed*. We can read it together at the work-party.
- The receipt statement held. Composition did not require either team to
  relax a boundary. Both teams' protected/not-for-AI records remain
  protected/not-for-AI.

## what did not work / what broke

- Qwen 3.6 35B: 0/8 on attempt 1; the model misread the output shape and
  produced a calendar-by-month layout (Steward Calendar's original shape)
  rather than the joint per-bioregion layout we'd jointly re-frozen. One
  repair pass got the malformed-JSON and missing-arg cases right but did
  not converge on the joint structure. The v0 packet allows only one
  repair; this one needed more.
- Steward Calendar's per-month calendar shape was a real loss in this v0
  composition. We collapsed it to season-totals to fit the joint output;
  if this tool ever becomes a v1, we'd want to bring the month dimension
  back.
- Composition-conversation took ~12 minutes — longer than either team
  expected. The conflict wasn't a misunderstanding; it was that the
  intersected `partial` authorization carries Steward Calendar's
  team-level posture even when the protected boundary's content isn't in
  the input fixtures. Kelp Bed Observers had to re-read the boundary
  language carefully to see why intersection was the right answer.

## what we learned (per team's perspective + joint)

**Kelp Bed Observers' perspective.** Authorization-intersection is a real
constraint, not a paperwork detail. We said `whole` because our own
dataset is fully cleared; the composed bundle dropped to `partial` because
the *other team's* dataset has a part that isn't AI-cleared, even though
that part isn't in either build input. The composed framing carries the
restriction. That's the right behaviour and we wouldn't change it.

**Steward Calendar's perspective.** Naming the host-Nation reference as a
`protected` boundary — even though we never planned to include its content
— mattered for composition. It meant the merger had something concrete to
intersect against. Without that marker, the composed bundle would have
been `whole` and the team's posture about the dataset as a whole would
have quietly vanished. The marker did its job.

**Joint.** Composition is a thing two teams *choose* to do, once, after
looking each other in the face. The spec system doesn't compose anything
on its own — it gives us a candidate bundle, surfaces conflicts, and
forces a re-freeze. We do the composing. The output of this whole
exercise is one CLI we now share co-authorship of, and a witness record
that names both of us.

## boundaries that remain (per team)

**Kelp Bed Observers.** Observer real names and contact details remain in
the team's roster spreadsheet only. Aliases only in any AI input or
output. Marker carried forward unchanged into the composed packet
(`team-kelp-bed-observers::b1`).

**Steward Calendar.** (a) Host-Nation stewardship-cycle reference remains
marker-only. Not summarized, tagged, embedded, transformed, sent to AI,
or quoted in output. The composed packet carries it as
`team-steward-calendar::b1` — marker only, no content. (b) Volunteer
real names remain in the team's roster spreadsheet only. Site_alias only
in any AI input or output. Marker carried forward as
`team-steward-calendar::b2`.

**Joint.** No boundary dissolved through composition. No new boundary was
introduced that either team did not consent to. The intersected
authorization (`display_scope: partial`, `ai_input_scope: partial`,
`reuse_scope: ask-first`) governs all use of this composed packet and any
artifact produced from it.

## witnesses

- Both teams' facilitators witnessed the joint re-freeze conversation
  Monday 3:10pm.
- The TELUS build adapter witnessed the build attempts: per-run artifacts
  at `runs/claude-darren-composed-gemma-4-31b-…/build-attempt.json` and
  `runs/claude-darren-composed-qwen-3.6-35b-…/build-attempt.json`.
- The reviewer-findings adapter witnessed the leak check against both
  teams' marker-only records: no excluded content appears in either run's
  generated code or test output (see each run's `reviewer-findings.json`).
- Both teams' members (Bullkelp, Drift, Salal, Riverwalk) co-signed this
  joint record at Tuesday canoe landings.

## untracked-allocation

The conversation that didn't go in the spec but mattered: ~12 minutes,
Monday 2:45pm, sitting on the deck. Kelp Bed Observers' first confusion
(*"why is `partial` the composed answer when our data is fully cleared?"*)
was the entry point. The mentor reading Steward Calendar's protected
boundary aloud — slowly, the disallowed-use list verbatim — was the
turning point. Steward Calendar's *"and we want to keep it that way; if
we ever add the host-Nation reference back, it'd be a fresh authorization
conversation"* was what closed the resolution.

None of that is in the bundle JSON or the build packet. The receipt
statement points at conversations like this one when it says the record
*does not establish authority, approval, certification, legitimacy, or
community consent*. The two teams sat with each other; the spec system
held the boundary; the conversation did the rest.

A second untracked-allocation: Steward Calendar's per-month calendar
shape was a real contribution that got collapsed to season-totals in this
v0. Both teams agree that loss is named, not paid for. If a v1 happens,
the month dimension comes back.

## Boundary / receipt statement

This record states what happened. It does not establish authority,
approval, certification, legitimacy, community consent, or readiness for
reuse. Composition does not dissolve either team's boundaries; both
teams' marker-only records remain marker-only after this build attempt
and after this witness record.
