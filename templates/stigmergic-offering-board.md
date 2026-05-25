---
doc_id: indigenomics.jam.stigmergic-offering-board
doc_kind: template
status: v0
date: 2026-05-25
author: Darren Zal
depends_on:
  - templates/team-submission-v0.md
  - docs/MENTOR_FIELD_GUIDE.md
  - docs/glossary.md
target_jam: 2026-05-25
---

# Stigmergic Offering Board

> A shared board for live, low-friction sharing of what your team is making
> that other teams might use. Each entry is a "sticky card" — small, scannable,
> updatable. Other teams read; mentors match; nothing is forced.

This board is a **coordination affordance, not a marketplace**. Teams keep
their full submissions in `team-submission-v0`. The board is just the surface
that other teams can scan in a gallery walk.

If a card never gets picked up, that's not failure. **"Doesn't fit yet" is a
first-class outcome.**

---

## What goes on the board

One sticky card per offering. A team can have multiple cards if they're making
multiple distinct things. Keep each card short enough to read on a phone in
under 30 seconds.

## Sticky card schema

```yaml
offering_name: string             # short, memorable; one phrase
from_team: string                 # team name or team_id
what_i_make: string               # noun phrase — the artifact, output, or capability
intended_use: string              # verb phrase — what this is FOR
who_might_use_it: string          # role or team-shape
integration_cost: 1 | 2 | 3 | 4 | 5  # how much work to receive it (1 = drop-in, 5 = co-build needed)
consent_gate: open | review-required | protected
current_status: drafting | built | witnessed | withdrawn
looking_for: optional string      # what the offering team needs from others
where_to_find: string             # file path / URL / "ask in person"
last_updated: ISO date-time
```

### Field definitions

- **`offering_name`** — A short handle teams will remember in a hallway
  conversation. Not the formal spec title.
- **`from_team`** — The team that made the offering. Use the team's chosen
  name; mentor can also note the `team_id` from `team-submission-v0`.
- **`what_i_make`** — The artifact itself, named as a noun phrase. ("A
  per-site rollup of kelp observations.") Avoid verbs here; verbs go in
  `intended_use`.
- **`intended_use`** — What the offering is *for*, as a verb phrase. ("To let
  stewards share at a community meeting without re-keying spreadsheets.") This
  is the most-read field by other teams.
- **`who_might_use_it`** — A role or team-shape, not specific team names. ("Any
  team producing per-site ecological observations." Or "A team building a
  steward-facing readout.") Keeps the board scannable.
- **`integration_cost`** — A 1–5 estimate, posted by the offering team.
  - 1: drop-in (paste this into your build, runs as-is)
  - 2: light wrap (rename a field, point at a file)
  - 3: small bridge (a few lines of glue code or a translation table)
  - 4: structural fit-check (likely needs a composition merge)
  - 5: co-build needed (the two teams have to sit together)
- **`consent_gate`** — Mirrors `team-submission-v0` vocabulary:
  - `open` — public-ok or team-only-with-ask-first; receiving teams can pick it up under named conditions
  - `review-required` — needs a named authority to clear it before reuse
  - `protected` — held by team; only the boundary is recorded, not the content
  - (No `open` card implies "no consent needed"; the offering team still names
    attribution and reuse expectations in their `team-submission-v0`.)
- **`current_status`** —
  - `drafting` — being shaped; expect change
  - `built` — exists in some runnable or readable form
  - `witnessed` — has a witness record from a build attempt
  - `withdrawn` — team retired this card (see "retiring" below)
- **`looking_for`** — Optional. The offering team can name what *they* need —
  a reviewer, a domain check, a sample dataset, a co-builder. Composition is
  bidirectional; this field is how a team signals receiving-side interest.
- **`where_to_find`** — A path or pointer. `examples/.../...md`, a GitHub URL,
  a Notion link, or `"ask in person"` for things that aren't artifact-shaped yet.
- **`last_updated`** — Roughly when the team last touched the card.

---

## Three example sticky cards

### Card 1 — Eelgrass per-site rollup

```yaml
offering_name: Eelgrass per-site rollup
from_team: Eelgrass Observers
what_i_make: A Python script that reads observation JSON and prints a per-site mean rollup with date range.
intended_use: To let a steward share Boundary Bay canopy data at a community meeting without re-keying the spreadsheet.
who_might_use_it: Any team needing site-grouped numeric rollups from ecological observation logs.
integration_cost: 1
consent_gate: open
current_status: built
looking_for: A second observation log from another bay to test the rollup generalizes.
where_to_find: examples/sample-submission-pair/build-instructions.md
last_updated: 2026-05-25T11:00:00-07:00
```

### Card 2 — Herring forage-fish witness sketches

```yaml
offering_name: Herring forage-fish witness sketches
from_team: Forage Stories
what_i_make: A small markdown wall of forage-fish observation stories with attribution and consent flags.
intended_use: To show how unstructured observation stories can sit next to structured rollups without losing voice.
who_might_use_it: A team building a public readout that wants narrative alongside numeric panels.
integration_cost: 2
consent_gate: review-required
current_status: drafting
looking_for: A reviewer who can sanity-check that the public-display gate is wired correctly.
where_to_find: ask in person
last_updated: 2026-05-25T10:20:00-07:00
```

### Card 3 — Kelp survey 2026 dataset

```yaml
offering_name: Kelp survey 2026 dataset
from_team: Kelp Monitors
what_i_make: A held survey dataset (named only as a boundary; content stays with the team and named stewards).
intended_use: To make visible that the team is carrying restricted-release material so other teams can plan around it.
who_might_use_it: No receiver yet. Posted so coordination can route around, not toward.
integration_cost: 5
consent_gate: protected
current_status: built
looking_for: Nothing right now. Posting the boundary is the offering.
where_to_find: see team-submission boundary record (id team-kelp-monitors::b1)
last_updated: 2026-05-25T09:45:00-07:00
```

---

## How to use the board

### Pacing — the gallery walk

The board is best read together, in silence, at a known time. The Tuesday
Composition Sprint (`workshop/tuesday-composition-sprint-v0.md`) opens with a
**15-minute silent gallery walk**: every team reads every other team's cards.

Outside the sprint window, the board lives as a always-on shared markdown
file. Teams can update their own cards any time.

### Mentor matching

Mentors carry `workshop/mentor-composition-decision-card.md`. After the
gallery walk, mentors flag promising pairs by writing alongside a card:

> *"@MentorName: Card 1 (Eelgrass) and Card 7 (Sensor pipeline) look like
> they share an interface field. Worth a 5-min check?"*

No team is required to follow up. Mentor suggestions are non-binding.

### When to update a card

- Status changes (`drafting` → `built`, etc.)
- `looking_for` resolves or shifts
- `integration_cost` becomes clearer after a first compose attempt
- The offering changes shape enough that the existing card description is wrong

If a team wants to add a *new* offering, they post a *new* card; do not
overwrite a card with a different offering.

### When to retire a card

A card is retired by setting `current_status: withdrawn`. Do not delete the
card — keep it on the board with the withdrawn flag, so the trail of "this
was here, then went away" is visible.

Retirement reasons (optional, add as a `withdrawal_note`):

- offering no longer matches what the team is making
- team decided not to put this on offer after all
- offering was rolled into a composition, see `<bundle-id>`
- "doesn't fit yet" was the right answer (this is fine)

### "Doesn't fit yet" — honored explicitly

If your card sits on the board for the whole Jam and no team picks it up:
**that is a real outcome, not a failure.** The Jam witnesses the offering;
the witness record can name the card; nothing about your team or the
offering is diminished by non-fit.

The mentor scripts in `docs/MENTOR_FIELD_GUIDE.md` §5 cover the language for
reinforcing this with participants.

---

## Vocabulary alignment

This board uses the same vocabulary as `templates/team-submission-v0.md` and
`docs/MENTOR_FIELD_GUIDE.md`:

| Board field | Where it's defined |
|---|---|
| `consent_gate: open / review-required / protected` | `templates/team-submission-v0.md` §boundary-vocabulary + `docs/MENTOR_FIELD_GUIDE.md` §2 |
| `current_status: drafting / built / witnessed / withdrawn` | `docs/witnessing-receipts.md`, `tools/withdrawal-propagation.py` |
| Composition flow that this board feeds into | `tools/composition-merger.py` and `examples/sample-multi-team-composition/` |

If a card's `consent_gate` is `protected`, the **content stays with the team**.
The board only records that the offering exists. Mentors carrying this on
their phones: do not screenshot, transcribe, or send `protected` card content
to any compute engine.

---

## Boundary

This board is a coordination affordance for the Creator Jam. Posting an
offering here is not a grant of consent, not a transfer of authority, not a
claim of certification, and not a promise to integrate. Picking up an
offering is not a guarantee of reuse permission — the receiving team must
honor the source team's `team-submission-v0` and use the
`composition-handoff-receipt.md` template when an offering moves between
teams. "Doesn't fit yet" is a complete outcome. Refusal is a complete
offering.
