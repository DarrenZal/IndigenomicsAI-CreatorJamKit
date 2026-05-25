# Claude + Darren — Two Teams That Learned How To Compose

A worked end-to-end example: two simulated jam teams arrive Monday with
separate visions, discover at Monday-afternoon gallery walk that their work
composes, run the merger, sit with the conflicts, jointly re-freeze, run the
build through TELUS, and write one joint witness record.

This is a "we ate our own dog food" reference. Both teams, the conflicts, and
the conversation are fictional. The composition pattern, the merger, the
TELUS lane, the boundaries that survived composition, and the witness record
are real.

> If you only have five minutes before canoe landings, read **The moment they
> realized their work composed** and **The conversation that resolved the
> conflicts** below. Skip the rest.

## The two starting points

**Team Kelp Bed Observers** (Vancouver — `team-claude-submission.json`).
They've been logging bull-kelp surface canopy at Boundary Bay and Lighthouse
Park since last August. Each observation is a date, a site, a canopy
percentage, and an observer alias. They want a CLI that turns a season of
observations into a simple, plain-language condition report a community group
could read at a Saturday work-party.

Their authorization: `display_scope: whole`, `ai_input_scope: whole`,
`reuse_scope: ask-first`. Their one boundary is observer real names — those
live in a roster spreadsheet, not in the cleared dataset. Everything else is
public-shoreline framing.

**Team Steward Calendar** (Victoria — `team-darren-submission.json`).
They've been tracking *what stewardship work has been happening* across the
season — work-parties, beach clean-ups, eelgrass surveys, kelp counts,
plantings — across multiple bioregions. They want a CLI that produces a
per-bioregion calendar showing seasonal patterns so a new volunteer can see
where they fit.

Their authorization: `display_scope: partial`, `ai_input_scope: partial`,
`reuse_scope: ask-first`. They hold a host-Nation stewardship-cycle reference
document that shapes their private thinking but is **never** in the dataset,
the AI input, or any display. They named it as a `protected` boundary in
their submission.

Two teams, two domains, two datasets, two different shapes of authorization.
Neither team thought of the other as a collaborator on Monday morning.

## The moment they realized their work composed

Monday 2:30pm. Gallery walk.

A Steward Calendar member walks past the Kelp Bed Observers' Notion page and
stops at the example output line: *"Boundary Bay: declining (mean canopy
45%)"*. She says, out loud, "you know we had three work-parties at Boundary
Bay this season." A Kelp Bed Observers member, three feet away, looks up.

The realization isn't "we have the same project." It's quieter: **each team's
output is the other team's missing column**. Kelp Bed Observers know which
beds are stressed; they don't know what work is happening around those beds.
Steward Calendar knows where the work is; they don't know whether the work is
landing on stressed beds or healthy ones.

The mentor on shift suggests they try the composition merger.

## Running the merger

```bash
python3 tools/composition-merger.py \
  examples/claude-darren-demo/team-claude-submission.json \
  examples/claude-darren-demo/team-darren-submission.json \
  --out examples/claude-darren-demo/candidate-bundle.json
```

Output:

```
wrote candidate bundle: examples/claude-darren-demo/candidate-bundle.json
  status: candidate
  conflicts surfaced: 2
```

Both teams sit with `candidate-bundle.json`. Three things show up:

1. **Both teams' offerings are in the bundle.** Kelp Bed Observers'
   Boundary-Bay-and-Lighthouse-Park canopy log. Steward Calendar's public
   stewardship action log. *And* — preserved, not cleared, marked
   `included_in_build: false` — Steward Calendar's protected host-Nation
   reference, named only as a boundary.

2. **Both teams' boundaries are namespaced and preserved.** The bundle holds
   `team-kelp-bed-observers::b1` (observer real names — not-for-AI) and
   `team-steward-calendar::b1` (host-Nation reference — protected) and
   `team-steward-calendar::b2` (volunteer real names — not-for-AI). Composition
   adds boundaries; it never subtracts.

3. **Two conflicts surfaced**, both authorization mismatches:

   ```json
   {
     "kind": "ai_input_scope_mismatch",
     "team_a_value": "whole",
     "team_b_value": "partial",
     "resolution": "intersected to most restrictive: partial"
   },
   {
     "kind": "display_scope_mismatch",
     "team_a_value": "whole",
     "team_b_value": "partial",
     "resolution": "intersected to most restrictive: partial"
   }
   ```

   The merger does not silently relax. Where Kelp Bed Observers said
   `whole` and Steward Calendar said `partial`, the composed bundle is
   `partial`. The intersected `authorization_notes` reads: *"composed: both
   teams must re-confirm before any build attempt or display"*.

## The conversation that resolved the conflicts

This is the part the merger can't do.

Kelp Bed Observers' first reaction, honest: *"wait, we said `whole` because
our dataset is fully cleared — why is the composed bundle `partial`?"*

The mentor pulls up Steward Calendar's submission and reads the boundary
aloud: *"Host-Nation stewardship cycle reference. Subject to ongoing
partner-organization review. Disallowed use: summarize, tag, embed,
transform, send-to-ai, quoted-in-output."*

Kelp Bed Observers re-reads. *"Ah. So `partial` here doesn't mean partial
*for our data* — it means the **composed authorization** is the most
restrictive across both teams, and your team has a part of your stack that
isn't AI-cleared. Even though that part isn't in the build input, the
composed bundle still inherits the partial framing because composition is
one stack."*

That's the right read. Steward Calendar's `partial` reflects a posture
their team holds about their dataset as a whole; that posture survives
composition. The fact that the protected reference is *not* in the input
fixtures does not let the composed bundle relax to `whole`.

Steward Calendar adds: *"And we want to keep it that way. If we ever
add the host-Nation reference back in, it'd be a fresh authorization
conversation with them — not something the composed framing should
auto-cover."*

Joint decision (~12 minutes of conversation):

- Accept the intersected `partial / partial / ask-first` authorization.
- Re-freeze in the composed context (both teams' facilitators confirm).
- Carry both teams' marker-only boundaries forward into the build packet as
  `excluded_inputs`, namespaced by team. Neither boundary dissolves.
- Add an `intersected_authorization_accepted_by_both_teams: true` field to
  the joint freeze record so the lineage shows up.

## Joint re-freeze and the composed build packet

`composed-build-packet.json` was written from the candidate bundle with the
joint freeze record above. Its build target combines both teams' shapes:

- Read kelp observations + stewardship actions (two cleared fixtures, one per
  team).
- Group by bioregion.
- Per bioregion: a `KELP:` block (per-site condition from the canopy mean)
  and an `ACTIONS:` block (per-action-type counts).
- Summary line: total healthy / declining / stressed sites, total stewardship
  actions.

Steward Calendar's original calendar-by-month shape is collapsed to
season-totals in this v0 composition (named in the spec — *"the calendar
shape is collapsed to seasonal totals in this v0"*). Both teams noted that's
a real loss and a thing to revisit if the joint tool ever becomes a v1.

The build instructions and the acceptance test are at
`build-instructions.md` and `acceptance-test.py`. Eight acceptance tests
cover the worked example, three conditions across two bioregions, an
actions-only bioregion, the both-empty case, unknown action types being
dropped, malformed JSON, missing CLI args, and round-half-away-from-zero on
the canopy mean.

## Running the build through TELUS

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/examples/claude-darren-demo/composed-build-packet.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/examples/claude-darren-demo/runs \
  --run-prefix claude-darren-composed --models gemma-4-31b,qwen-3.6-35b
```

What the TELUS lane returned (real run, 2026-05-25 15:44 UTC):

| Model | Attempt 1 | After repair | Finding |
|---|---|---|---|
| Gemma 4 31B | 7/8 | **8/8** | **fixed** |
| Qwen 3.6 35B | 0/8 | 2/8 | improved |

Gemma's attempt-1 missed one rounding edge (test_8 — half-away-from-zero on
59.5); the single repair pass, fed only the failing test names and
counts, produced an 8/8 solution. Qwen's attempt-1 produced code that
failed all 8 tests (it misread the output shape and produced a calendar by
month instead of the joint per-bioregion sections); its repair pass got
the malformed-JSON and missing-arg cases right but did not converge on
the joint shape.

Honest finding: this packet is harder than the M2.5 single-team example.
The composition introduces a two-input shape, a more elaborate output
structure, and a rounding edge. Gemma handles it with one repair; Qwen
needs more passes than v0 allows.

Run artifacts are in `runs/` — each model's directory has
`build-attempt.json` (the model, the attempts, the final code, the
finding), `reviewer-findings.json` (each review check + the leak check
for excluded-input content), and `canoe-landing/witness-record.md`
(the per-run witness record the adapter generated).

## Joint witness record

`joint-witness-record.md` is the canoe-landing record written
collaboratively as if from both teams. It uses the witness-rollup section
headers and adds an `untracked-allocation` section that captures the
12-minute conversation that resolved the authorization conflict (the
conversation isn't in the spec; it's the kind of thing the receipt
statement points to when it says *"this does not establish authority"*).

The receipt statement is verbatim from the witness-rollup template:

> This record states what happened. It does not establish authority,
> approval, certification, legitimacy, community consent, or readiness for
> reuse.

Both teams' boundaries remain. The host-Nation reference is still
marker-only. Observer and volunteer real names are still not in the AI
input or any output. Composition added two teams' work together; it
didn't dissolve what either team was holding.

## What this teaches that the existing sample doesn't

The existing `sample-multi-team-composition/` shows the **mechanics** of
the merge (boundaries namespaced, authorization intersected, conflicts
surfaced). This demo shows the **arc** — gallery walk → realization →
merger → conflict conversation → joint re-freeze → joint build → joint
witness — and what reciprocity actually feels like when two teams find
that their separate offerings make something neither team could have
alone.

The relational read: **composition is not a feature of the spec system.
It's a thing two teams choose to do, once, after looking each other in
the face. The spec system just makes sure neither team's boundaries get
quietly stepped on along the way.**

## Files in this directory

- `team-claude-submission.json` — Kelp Bed Observers' frozen submission
- `team-darren-submission.json` — Steward Calendar's frozen submission
- `candidate-bundle.json` — output of `composition-merger.py`
- `composed-build-packet.json` — joint re-frozen `agentic-build-packet-v0`
- `build-instructions.md` — frozen spec for the composed tool
- `acceptance-test.py` — 8 acceptance tests against the composed spec
- `runs/` — TELUS lane outputs (Gemma + Qwen)
- `joint-witness-record.md` — Tuesday canoe-landing record from both teams
- `README.md` — this file

## Boundary

These are fictional teams and fictional offerings. The composition pattern,
the merger output, the build-packet adapter run, the Gemma + Qwen
findings, and the witness record are real. No real host-Nation
stewardship-cycle reference is named or used. The condition thresholds in
the build spec are illustrative for the jam and do not constitute
ecological certification.
