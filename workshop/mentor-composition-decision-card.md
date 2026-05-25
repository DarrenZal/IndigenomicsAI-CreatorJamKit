---
doc_id: indigenomics.jam.mentor-composition-decision-card
doc_kind: mentor-aid
status: v0
date: 2026-05-25
author: Darren Zal
depends_on:
  - templates/team-submission-v0.md
  - templates/stigmergic-offering-board.md
  - workshop/tuesday-composition-sprint-v0.md
  - tools/composition-merger.py
target_jam: 2026-05-25
---

# Mentor Composition Decision Card

A 90-second triage tool for mentors during the Tuesday Composition Sprint
(or any time two teams ask "could we compose?").

**This card is a mentor aid. It is not authority.** It does not decide
whether a composition should happen. It surfaces structural fit so the
teams can decide for themselves. The teams' Phase 4 comprehension
checkpoint (Johar discipline) is where actual consent lives.

---

## The 90-second flow

```
  ┌─────────────────────────────────────────────────────┐
  │  Q1. Do the two offerings share at least one        │
  │      interface field? (an input shape, an output    │
  │      shape, a witness criterion they both produce)  │
  └─────────────────────────────────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
       NO              YES
        │               │
        ▼               ▼
  preserve         ┌─────────────────────────────────────┐
  separate         │  Q2. Are the permission states      │
                   │      (display_scope, ai_input_scope,│
                   │      reuse_scope) compatible? (i.e. │
                   │      a "most-restrictive wins"      │
                   │      resolution is acceptable to    │
                   │      both teams)                    │
                   └─────────────────────────────────────┘
                                │
                        ┌───────┴───────┐
                        │               │
                       NO              YES
                        │               │
                        ▼               ▼
                  needs re-freeze  ┌─────────────────────────────────────┐
                  with both teams  │  Q3. Are the AI-use boundaries      │
                  (one or both     │      compatible? (if either team    │
                  may need to      │      has `ai_input_scope: none`, a  │
                  adjust before    │      composed build with AI in the  │
                  compose can      │      loop is blocked)               │
                  proceed)         └─────────────────────────────────────┘
                                                │
                                        ┌───────┴───────┐
                                        │               │
                                       NO              YES
                                        │               │
                                        ▼               ▼
                                  preserve         ┌─────────────────────────────────────┐
                                  separate (or     │  Q4. Is the evidence / cleared text │
                                  compose-without- │      on either side stale,          │
                                  AI lane)         │      unverified, or known-changing? │
                                                   └─────────────────────────────────────┘
                                                                │
                                                        ┌───────┴───────┐
                                                        │               │
                                                       YES             NO
                                                        │               │
                                                        ▼               ▼
                                                  refresh           ┌─────────────────────────────────────┐
                                                  before            │  Q5. Is there protected /           │
                                                  compose           │      review-required / cultural     │
                                                                    │      material on either side?       │
                                                                    └─────────────────────────────────────┘
                                                                                │
                                                                        ┌───────┴───────┐
                                                                        │               │
                                                                       YES             NO
                                                                        │               │
                                                                        ▼               ▼
                                                                  review queue,    ┌─────────────────────┐
                                                                  not auto-        │  ✅ Candidate for   │
                                                                  compose          │     compose.        │
                                                                                   │  Run                │
                                                                                   │  composition-       │
                                                                                   │  merger.py and      │
                                                                                   │  proceed to         │
                                                                                   │  Phase 3 of the     │
                                                                                   │  Tuesday sprint.    │
                                                                                   └─────────────────────┘
```

---

## Each NO branch — concrete next action (no value judgment)

| Branch | Concrete next action | Suggested mentor line |
|---|---|---|
| Q1 NO — no shared interface | **Preserve separate.** Note both cards on the stigmergic board: `composition-explored, no shared interface`. Teams continue separately. | "I don't see a shared interface field between these two. That's not a flaw — it just means a compose would be a co-build, not a merge. Want to stay separate for now?" |
| Q2 NO — permission states incompatible | **Needs re-freeze with both teams.** One or both teams may want to adjust their `team-submission-v0.authorization` before compose can proceed. Or stay separate. | "Your permission states don't sit comfortably together yet. You can either adjust your own submission and re-freeze, or you can stay separate. Either is fine." |
| Q3 NO — AI-use boundaries incompatible | **Preserve separate.** Or compose-without-AI-lane: the bundle can still produce a hand-built outcome, just not a TELUS build attempt. | "One of you has `ai_input_scope: none`, so a composed AI build is blocked. You can still compose for a hand-built outcome, or stay separate. Your call." |
| Q4 YES (stale evidence) | **Refresh before compose.** The team with stale evidence updates their `cleared_text` or `acceptance_criteria`; re-freeze; then revisit compose. | "The evidence on [side] is stale enough that a compose would carry the staleness forward. Quick refresh first?" |
| Q5 YES (protected material) | **Review queue, not auto-compose.** The protected material stays with its team. The compose can only proceed if the team holding the protected material confirms that the compose does not require the protected content (i.e. it remains as a marker-only boundary). If the compose *needs* the protected content, this becomes a review-required item — not a Jam-day decision. | "There's protected material on [side]. That doesn't kill the compose, but the protected content can't enter the merged bundle. Can the compose work with the protected piece staying as a marker-only boundary? If not, this is a review-required item — beyond what we can decide today." |
| All clear | **Candidate for compose.** Run `python3 tools/composition-merger.py team-a.json team-b.json --out candidate.json` and move into Phase 3 of the Tuesday Composition Sprint. | "Looks like a candidate. Want to run the merger and read the conflicts together?" |

---

## 5 common scenarios — verdict at a glance

| # | Scenario | Verdict | Why |
|---|---|---|---|
| 1 | Team A built a per-site rollup tool; Team B has matching per-site observation data | **Candidate for compose** | Shared interface (observation JSON in, site rollup out); permissions likely compatible; data is fresh; no protected material |
| 2 | Team A's offering uses `ai_input_scope: none`; Team B's build sends every input to TELUS | **Q3 NO — preserve separate (or compose-without-AI-lane)** | Boundary mismatch on AI use; compose can still happen for a hand-built outcome |
| 3 | Team A has a sketch of a steward-facing readout; Team B has a tag-counter CLI | **Q1 NO — preserve separate** | Both useful, but no shared interface field; would be co-build, not merge |
| 4 | Team A holds restricted-release survey data as a `protected` boundary; Team B wants to use it as input to their rollup | **Q5 YES — review queue, not auto-compose** | Protected material cannot move into a merged bundle without authority; not a Jam-day decision |
| 5 | Team A's cleared text was finalized Friday from a survey that has since been updated by the source community | **Q4 YES — refresh before compose** | Stale evidence will carry forward; quick refresh first, then revisit |

---

## How to use this card during the sprint

- **Phase 1 (gallery walk)** — Don't use this card yet. Let teams scan.
- **Phase 2 (mentor matches)** — Carry this card. For each promising pair
  you flag, run the 6 questions in your head (or with the pair, if they
  want to see the structure) before suggesting they go to Phase 3.
- **Phase 3 (merge experiments)** — If the card's verdict is "candidate
  for compose," run `composition-merger.py`. If the verdict is anything
  else, suggest the corresponding next action and do not run the merger.
- **Phase 4 (comprehension checkpoint)** — This card is not used. Phase 4
  is consent-of-all from each team; structural fit (this card) is not
  consent.

---

## What this card does NOT do

- It does not certify that a compose will succeed.
- It does not override a team's `object` signal in Phase 4. Even if all 6
  questions pass, any team member's `object` dissolves the composition.
- It does not judge whether an offering is "good." It looks at structural
  fit only.
- It does not decide consent for protected, cultural, or review-required
  material. Those are escalations, not decisions.
- It does not require teams to compose. A "candidate for compose" verdict
  is a suggestion to *consider* compose, not an instruction to do it.

---

## Reminders for the mentor

- A NO answer at any branch is **not a failure**. It is a routing decision.
- "Preserve separate" is a real outcome.
- "Doesn't fit yet" is a real outcome.
- Refusal is a complete offering.
- If a team says "we don't want to compose," stop. Do not push.

---

## Boundary

This card is a mentor aid for surfacing structural composition fit. It is
not authority. It does not decide consent, cultural permission, ceremony
fit, or whether a composition should proceed. The 6 questions surface
structure; the teams themselves (via the Phase 4 comprehension checkpoint)
hold consent. A "candidate for compose" verdict is a suggestion to consider
running `composition-merger.py`; it is not a requirement, a certification,
or a guarantee that the composition will work or be witnessed favorably.
