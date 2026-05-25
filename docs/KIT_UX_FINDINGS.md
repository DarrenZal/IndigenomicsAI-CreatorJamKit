---
doc_id: indigenomics.jam.kit-ux-findings
doc_kind: ux-walkthrough
status: v0
date: 2026-05-25
walked_by: Claude (overnight, simulating a fresh participant)
---

# Kit UX Findings — Walking Through As a Fresh Participant

A walkthrough of the public kit as a participant arriving cold would experience it. Findings ranked by severity (high = friction during the jam; medium = inefficiency; low = polish).

**Method**: I started at the public kit URL (`https://github.com/DarrenZal/IndigenomicsAI-CreatorJamKit`), read the README first, then tried to write a team-submission from scratch using only the kit's own docs and templates. I recorded every moment of "wait, where is X?" or "what does this term mean?" friction.

---

## Walkthrough trace

### Step 1 — Landing on the repo

I read the README top-to-bottom. Tone: clear, plain-language, sets expectations well.

**Finding (low)**: The README has 11 sections and ~75 lines of content before the Boundaries section, which is one of the most important things to read. A first-time participant might miss it. **Fix**: pull a 2-line "What this is" paragraph to the very top, then jump straight to "Quick start" + "Boundaries."

**Finding (medium)**: The "Fast Path" lists 7 steps but doesn't say how long they take or which require facilitator help. A new participant doesn't know whether step 2 is "5 minutes" or "an hour." **Fix**: add rough time estimates ("5 min", "facilitator-led") and which can be done alone.

### Step 2 — Reading `docs/participant-handout.md`

This is the actual entry-point per the README. Read in full.

**Finding (high)**: The handout never tells me what a "spec" is, even though it's the next concept I hit (the README says step 3 is "wrap with templates/spec-fragment.md"). I had to flip back to specs/README.md to even understand what a "spec" was in this context. **Fix**: add a one-paragraph "What is a spec?" definition to the participant handout.

**Finding (medium)**: The handout says "build attempt instructions" but doesn't explicitly distinguish that from "spec." A participant might think these are the same thing. **Fix**: explicit comparison: "A spec is what you want; build attempt instructions are how someone (human or AI) tries to make it."

**Finding (low)**: The five-questions are buried mid-document under "## The Quick Card." For a participant skimming, they're the highest-value content but visually low-priority. **Fix**: pull the five questions to the top of the doc, even before "The Big Idea."

### Step 3 — Trying to write a team-submission

I open `templates/team-submission-v0.md`. It's the schema doc — dense, ~340 lines, more reference than tutorial.

**Finding (high)**: There's no "filled-in example" link at the top of the schema doc. A new participant looking at 340 lines of schema has no idea what an actual submission looks like. **Fix**: header line: "See `examples/sample-submission-pair/sample-team-submission-v0.md` for a worked example. This file is the schema reference."

**Finding (medium)**: The YAML schema starts at line 41 with fields like `submission_id`, `surface`, `team.id` — none of which a participant would know they need. Are they required? Auto-generated? **Fix**: split into "things you fill in" vs "things the gateway/exporter fills in." Or: a "minimum viable submission" mini-schema with just the must-fill fields.

**Finding (high)**: The schema mentions `boundary_type: marker-only | not-for-AI | not-for-reuse | private | protected` as if these were known terms. A participant who hasn't read `docs/MENTOR_FIELD_GUIDE.md` (which lives in `docs/` and isn't linked from `templates/`) has no idea what these mean. **Fix**: either inline the definitions next to the field, or add a "See `docs/MENTOR_FIELD_GUIDE.md` §2 for the full boundary vocabulary" pointer at the top of the boundaries section.

### Step 4 — Wanting a sample to look at

I navigate to `examples/`. There are now 5+ subdirectories with samples. Good.

**Finding (medium)**: `examples/` has no README — just a flat list. A participant doesn't know which example to look at first. **Fix**: write `examples/README.md` with a 1-line description of each example + which to look at when.

**Finding (medium)**: `examples/sample-submission-pair/` (Kelp Watch) is one of three sample-submission-* dirs. The others are `sample-submission-receipt-wall/` and `sample-submission-commitment-pool/`. The naming is inconsistent — one has no descriptor, the other two do. **Fix**: rename the original to `examples/sample-submission-kelp-watch/` for parallel structure, or add an explicit description at the top of its README.

### Step 5 — Looking at the spec menu

I open `specs/README.md`. The new tagged table is excellent — difficulty, boundary, preflight columns clear.

**Finding (low)**: The tag legend is at the top but the table uses emoji symbols. On a phone, the legend ↔ table mapping requires scrolling back. **Fix**: repeat the legend below the table for phone readers, or use text codes (GFB / INT / COMP / DOC) instead of emoji.

**Finding (medium)**: After picking a spec from the menu, I have no obvious next step. The individual spec card (e.g., `witness-record-interop-profile.md`) has Invitation / What Could Be Built / Inputs / Outputs / Acceptance Criteria — but no "now write your submission" instruction. **Fix**: at the bottom of each spec card, add a "Next: write a team-submission using `templates/team-submission-v0.md`. See `examples/sample-submission-pair/` for a worked example."

### Step 6 — Trying to understand the freeze step

The schema mentions `freeze.status: draft | frozen | needs-review` with a `facilitator_confirmed` block. As a participant, "facilitator-confirmed" is opaque.

**Finding (medium)**: The freeze checklist lives in `docs/facilitator-quick-card.md`. Participants don't naturally read facilitator docs. **Fix**: include the freeze checklist (or a participant-facing version) in `templates/team-submission-v0.md` itself, under the `freeze` field documentation.

### Step 7 — What happens after freeze?

I've written a submission. I think I'm done. What happens next?

**Finding (high)**: There's no "what happens after I submit" doc visible. A participant doesn't know: who freezes? where does the build attempt run? when do I see the result? do I have to do anything during the build? **Fix**: add a short "After You Submit" section to the participant handout (or a `docs/what-happens-next.md`). Walks through: facilitator-freezes → exporter-runs → TELUS-lane-attempts → reviewer-checks → witness-record. Estimated timeline.

### Step 8 — Looking for the participant agent

The README mentions "participant-agent-context/" — I navigate there.

**Finding (low)**: The README's `participant-agent-context/` section says "for any LLM helping you draft a spec" but doesn't tell the participant HOW to give the bundle to their LLM. **Fix**: add a 3-line example: "Paste the contents of `PROMPTS_FOR_AGENTS.md` into your LLM along with the `knowledge-bundle.jsonld`. The agent will know how to help."

### Step 9 — Tuesday morning panic

Tomorrow I have to write a witness record. Where do I look?

**Finding (medium)**: There's no obvious "Tuesday morning checklist" anywhere. The participant handout doesn't tell me how to write a witness record. **Fix**: short `docs/tuesday-morning-checklist.md` for participants, separate from the canoe-landing-runbook (which is facilitator-facing).

### Step 10 — Tone / register

Across all docs, the kit is consistently warm, plain-language, and care-full. The tone is the right tone.

**Finding (low — positive)**: The kit's voice is the kit's biggest UX strength. Don't lose it as future iterations add structure.

---

## Top 5 fixes a mentor could flag day-of (most leverage)

These are the fixes that don't require editing docs — mentors can address them verbally during the first-5-minutes flow:

1. **Show participants the sample pair early.** "Don't read the schema doc cold — open `examples/sample-submission-pair/sample-team-submission-v0.md` first. It's a worked example. Then come back to the schema if you need detail."

2. **Walk through the five offering questions before any template.** Mentors already do this per the facilitator-quick-card; emphasize it.

3. **Define the boundary vocabulary on first contact.** Use the table in `docs/MENTOR_FIELD_GUIDE.md` §2. The schema doc assumes these terms.

4. **Explain the freeze step verbally.** Don't let participants try to interpret the `facilitator_confirmed` field cold.

5. **Tell participants what happens after submit.** Walk through the post-submit timeline so the team isn't anxious about "is my thing being looked at right now?"

---

## Top 5 fixes that need doc edits (medium-term)

For future iterations of the kit, before the next jam:

1. **Add `docs/what-happens-next.md`** — post-submit walkthrough for participants
2. **Add `docs/tuesday-morning-checklist.md`** — participant-facing pre-canoe-landing prep
3. **Write `examples/README.md`** — flat list with descriptions, which-when-to-show guidance
4. **Add boundary vocabulary glossary** to the top of `templates/team-submission-v0.md`
5. **Add "next steps" footer** to every spec card in `specs/`

---

## What this walkthrough did NOT do

- I did not actually try to run the gateway (would require Shawn's live URL + login)
- I did not test the kit on a phone — only desktop
- I did not test the kit with a participant who has zero programming background — I made participant-shaped guesses, but a real fresh participant might have different friction
- I did not test the kit in a non-English context

A more thorough UX test would walk a real fresh participant through the kit live, recording their actual stumbles. This is a simulation.

---

## Boundary

These findings are observations from one walkthrough on 2026-05-25 by an LLM simulating a fresh participant. They are not a UX audit, a usability study, or a verdict on the kit's quality. The kit is in active use and the team adjusts as the day unfolds.
