---
doc_id: indigenomics.jam.tuesday-composition-sprint-v0
doc_kind: facilitator-playbook
status: v0
date: 2026-05-25
author: Darren Zal
depends_on:
  - templates/stigmergic-offering-board.md
  - templates/composition-handoff-receipt.md
  - workshop/mentor-composition-decision-card.md
  - tools/composition-merger.py
  - docs/jam-day-timeline-v0.md
  - docs/MENTOR_FIELD_GUIDE.md
target_jam: 2026-05-26
---

# Tuesday Composition Sprint — Facilitator Playbook

A **90-minute optional sprint** inside Tuesday morning, used by teams that
want to discover cross-team compositions before the 3 PM canoe landings.

This sprint is opt-in. Teams that do not want to compose stay home and keep
building. **Non-participation is a valid Tuesday outcome.** "Doesn't fit yet"
is a first-class outcome.

---

## When this runs

Inside the Tuesday morning ~3-hour work block. Recommended window:

- **09:00–10:30** — sprint (90 minutes)
- **10:30+** — either build (composed) OR run a separate build OR record
  "preserved as not-fit"

The sprint anchors are flexible by ±15 minutes; facilitators can shift to
match dietary-break timing and Carol Anne 1:1 slots.

---

## What the sprint produces

By the end, each participating team has a clear next action from this menu:

1. **Build composed** — paired with another team, frozen as a re-freeze of
   a candidate bundle, moving into a composed build attempt.
2. **Build separate** — kept own submission, made aware of overlaps,
   continuing alone.
3. **Preserved as not-fit** — recorded as a deliberate non-fit; nothing
   built; witness record will name it.

All three are real outcomes. Mentors must reinforce this throughout.

---

## Pre-sprint setup (facilitator, evening of Monday or 08:30 Tuesday)

- [ ] `templates/stigmergic-offering-board.md` is live with at least one
      sticky card from each team that wants to be findable.
- [ ] Print or load on phones: `workshop/mentor-composition-decision-card.md`.
- [ ] `tools/composition-merger.py` is reachable from a mentor laptop with
      Python 3 installed.
- [ ] `templates/composition-handoff-receipt.md` is open in a tab.
- [ ] Each team has a frozen `team-submission-v0` (or knows it is `draft` and
      a compose would require re-freeze of both).

If a team has no frozen submission yet, they can still participate — but any
composition they enter triggers a freeze for both sides before build.

---

## The sprint — phase by phase

### Phase 1 — Offerings gallery walk (09:00–09:15, **15 min**, silent)

**Purpose.** Every team reads every other team's stigmergic-offering-board
cards. Silent reading. No talking. The silence is the discipline; talking
collapses scanning into the first conversation a team finds.

**Mentor script (read aloud at 09:00):**

> "For the next 15 minutes, we're going to read each other's offering cards
> in silence. No talking, no questions, no negotiating. Just read. If
> something interests you, mark the card — circle the team name on a printed
> board, or note it on your phone. We'll match in the next phase. The
> silence is the point. It gives every card a fair read."

**What teams do.**
- Read every card.
- Note cards their team might compose with — by team name, by card name.
- Note cards their team can offer to (where `looking_for` matches something
  the team can give).

**Time budget.** 15 minutes hard cap. If teams finish early, they stay
silent and re-scan.

**Gate check at end of phase.** Mentors look around: did everyone read every
card? If a team skipped, give them 2 extra minutes and shift Phase 2 by 2.

---

### Phase 2 — Mentor matches (09:15–09:30, **15 min**)

**Purpose.** Facilitators flag promising pairs using
`workshop/mentor-composition-decision-card.md`. Teams that don't want to
compose stay home.

**Mentor script (read aloud at 09:15):**

> "Now we talk. If you saw a card that interests you, find that team in the
> next 10 minutes and ask them. Mentors will also be walking around
> suggesting pairs we saw. A suggestion from a mentor is not a requirement
> — you can say 'thanks, not this time.' If you don't want to compose with
> anyone, that's a real choice. Go back to your build."

**What mentors do.**
- Walk the room/Zoom rooms.
- For each promising pair flagged in Phase 1, suggest a 5-minute fit check.
- Use the decision card (the 6 yes/no branches) to triage before suggesting.
- If the decision card says "preserve separate" or "review queue, not
  auto-compose," do not suggest the pair.

**What teams do.**
- Self-select pairs from gallery-walk notes.
- Or accept a mentor suggestion.
- Or opt out and return to their build.

**Time budget.** 15 minutes hard cap. By 09:30, every team is either paired
or building.

**Gate check at end of phase.** A team is in one of three states:
- `paired-with-<team-id>` (move to Phase 3)
- `solo-building` (leave the sprint; return to morning work)
- `unsure` (mentor stays with them; they may opt out by 09:45 with no
  judgment)

---

### Phase 3 — Merge experiments (09:30–10:00, **30 min**)

**Purpose.** Paired teams run `tools/composition-merger.py` together;
surface conflicts; decide whether the merge is worth re-freezing.

**Mentor script (read aloud to each paired group):**

> "We're going to run the merge tool with both your submissions. It will
> produce a candidate bundle that shows what fits together, what conflicts,
> and how each conflict resolves (always to the more restrictive answer).
> The tool does not build anything yet. After the merge, you'll look at the
> conflicts list together and decide if this composition is worth carrying
> forward."

**What happens.**
1. Mentor runs: `python3 tools/composition-merger.py team-a.json team-b.json --out candidate.json`
2. Both teams read the bundle output together — especially `conflicts_surfaced`
   and `intersected_authorization`.
3. The pair discusses each conflict for 1–3 minutes.

**Mentor scripts for common conflicts:**

- **`ai_input_scope_mismatch`** — "The more restrictive choice wins. Team
  A's `whole` gets pulled down to Team B's `partial`. Is that okay with
  both of you? If not, the team that gave more permission can stay with
  their original submission."
- **`display_scope_mismatch`** — Same pattern. Most restrictive wins.
- **`reuse_scope`** — "Composition always forces `ask-first` for reuse,
  regardless of what the source submissions said. New context, new ask."
- **Boundaries from both teams** — "Both `b1`s are kept; the merger
  namespaced them. Neither team's boundary is collapsed or relaxed."

**Time budget.** 30 minutes for the merge + read + discussion. If a team
needs more time, they can extend into Phase 4 (the comprehension checkpoint
will still apply).

**Gate check at end of phase.** Each pair has read the candidate bundle and
named their conflicts. No build has started.

---

### Phase 4 — Comprehension checkpoint (Johar discipline) (10:00–10:30, **30 min**)

**Purpose.** Each team in a composition signals: do they still recognize
what they brought? This protects against the failure mode where one team's
contribution gets quietly transformed in the merge.

**Mentor script (read aloud to each pair at 10:00):**

> "Before we decide whether to build, we're going to do a comprehension
> check. Each team — separately — answers one question: looking at this
> candidate bundle, do you still recognize what *you* brought into it?
> Three answers are valid: 'still recognize what I brought,' 'no longer
> recognize,' or 'object.' Any 'object' from any team dissolves the
> composition. That is not a failure. We record it as 'doesn't fit yet'
> and both teams keep their original submissions."

**The three signals.**

- **`still-recognize`** — "What I brought is still here, still mine, still
  meant the way I meant it."
- **`no-longer-recognize`** — "What I brought has been transformed in a way
  I didn't expect. I need to talk through this before I can sign off."
- **`object`** — "I do not consent to this composition." (Triggers dissolve.)

**What mentors do.**
- Ask each team member individually if possible (not just the team lead).
- Take any `object` as final — do not negotiate.
- For `no-longer-recognize`, give the pair another 10 minutes to talk; then
  re-ask.

**If a team signals `object`:**
- The composition dissolves immediately. No argument.
- A `composition-handoff-receipt.md` is *not* created (no handoff happened).
- A "doesn't fit yet" receipt is created. Use this language:

> "Team A and Team B explored composition during the Tuesday sprint. After
> reading the candidate bundle, Team [X] signaled 'object' under Johar
> discipline. Composition dissolved with respect. Both teams' original
> submissions remain frozen. This is a real Tuesday outcome — not a
> failure, not a blocker."

This receipt goes to the witness record. Carry the language forward.

**Time budget.** 30 minutes hard cap.

**Gate check at end of phase.** Each pair has one of:
- All members `still-recognize` → ready to decide build path (Phase 5)
- One or more `no-longer-recognize` → re-discuss or escalate to Phase 5 with
  caveat
- Any `object` → composition dissolved; "doesn't fit yet" receipt drafted

---

### Phase 5 — Decision: build / preserve separate / revise (10:30–11:00, **30 min**)

**Purpose.** Lock the outcome from this sprint so teams can spend the
remaining Tuesday morning on it.

**Mentor script (read aloud at 10:30):**

> "Three options. Pick one as a pair. (1) Re-freeze the candidate bundle
> and start a composed build attempt. (2) Preserve both submissions
> separately — you talked, you learned, you didn't compose. (3) Revise
> your own submissions based on what you learned and re-freeze separately.
> All three are real outcomes."

**Mechanics for each option.**

**(1) Build composed.** Both teams sign a re-freeze on the candidate
bundle. The bundle status moves from `candidate` to `frozen-composed`. A
`composition-handoff-receipt.md` is created naming both teams as
source-and-receiving. The composed build attempt can proceed.

**(2) Preserve separate.** Both teams return to their original frozen
submissions. A short note is added to the stigmergic-offering-board on the
relevant cards: `composition-explored-with: <other-team-id>, preserved-separate`.

**(3) Revise.** One or both teams update their own `team-submission-v0`
(boundaries, offerings, scope) based on what the merge revealed, and
re-freeze separately. No composed bundle.

**Time budget.** 30 minutes for the decision + any paperwork (re-freeze
checklist, handoff receipt).

**Gate check at end of phase.** Every paired team has a recorded outcome.
The witness record knows what happened.

---

### Phase 6 — Either build (composed) OR run a separate build OR record "preserved as not-fit" (11:00+)

The sprint is over. Teams continue Tuesday morning in whichever lane they
chose.

For teams that chose `preserved as not-fit`:
- Card stays on the board (do not delete).
- A short witness note is drafted naming the exploration.
- The team continues with their original Monday build, or rests, or works
  on a non-build offering.

---

## Mentor scripts — at a glance

| Phase | Trigger | One-line script |
|---|---|---|
| 1 | Start | "15 minutes of silent reading. No talking. The silence is the discipline." |
| 1 | Team finishes early | "Stay silent. Re-scan. Look for cards that match what you can offer, not just what you want." |
| 2 | Promising pair seen | "Two cards I noticed: [A] and [B]. Want a 5-min check?" |
| 2 | Team uncertain | "If you don't want to compose, go back to your build. That's a real choice." |
| 3 | Conflict surfaces | "Most restrictive wins. Is that okay with both of you? If not, stay separate." |
| 4 | Comprehension check | "Do you still recognize what you brought? Three answers: still-recognize, no-longer-recognize, object." |
| 4 | `object` signaled | "Composition dissolves. That's respect, not failure." |
| 5 | Lock outcome | "Three options. Compose-and-build, preserve-separate, or revise-and-refreeze. Pick one." |

---

## Decision gates summary

| Decision point | Stop | Proceed | Dissolve |
|---|---|---|---|
| End of Phase 1 | Team didn't read all cards → +2 min | All read → Phase 2 | n/a |
| End of Phase 2 | Team unsure → mentor stays with them | Team paired → Phase 3; team solo → leave sprint | n/a |
| End of Phase 3 | Pair needs more time → extend into Phase 4 | Pair has read conflicts → Phase 4 | Decision card says "preserve separate" |
| End of Phase 4 | `no-longer-recognize` → +10 min, then re-ask | All `still-recognize` → Phase 5 | Any `object` → dissolve, draft receipt |
| End of Phase 5 | Pair undecided → mentor escalates | Outcome locked → resume morning work | (already dissolved if reached) |

---

## What this sprint does NOT do

- It does not require any team to compose.
- It does not produce a build by itself — it produces a re-frozen bundle (or
  doesn't). Building is a separate step that uses the bundle.
- It does not override a single `object` signal in Phase 4. Composition is
  consent-of-all, not majority-of-team.
- It does not collapse, summarize, transform, or send `protected` boundary
  content into any compute engine. The merger preserves boundaries as
  markers only.
- It does not judge whether a composition is "good." The decision card and
  comprehension checkpoint are about fit and recognition, not quality.

---

## "Doesn't fit yet" — the success outcome

If a pair runs the sprint, surfaces conflicts, sits with the comprehension
checkpoint, and decides not to compose — **that is a success outcome.** The
teams learned about each other's work, surfaced boundary structure, and
chose to preserve separate. The Jam witnesses the exploration.

The failure mode this sprint is built to prevent is **silent collapse**:
two teams compose because they felt social pressure to compose, one team's
contribution gets transformed beyond recognition, and nobody says anything
because the build is moving. The Johar comprehension checkpoint is the
load-bearing piece.

---

## Boundary

This sprint is an optional facilitator playbook for the Tuesday morning of
the Creator Jam. Running the sprint does not establish authority,
certification, or reuse permission for any team's offerings or for any
composed bundle. Mentor suggestions are non-binding. The
`composition-merger.py` tool surfaces structural conflicts; it does not
judge legitimacy, consent, cultural authority, ceremony fit, or whether a
composition should happen. Composition requires consent-of-all from both
teams; a single `object` signal dissolves the composition with no
negotiation. "Doesn't fit yet" is a complete, witnessable outcome.
