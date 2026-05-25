---
doc_id: indigenomics.jam.mentor-field-guide
doc_kind: facilitator-reference
status: v0
date: 2026-05-25
audience: mentors carrying this on their phones
---

# Mentor Field Guide — Creator Jam 2026-05-25 + 2026-05-26

One reference page. Open this on your phone when working with a team.

If you have 10 seconds: **start with the five questions** (section 1). Do not start with a spec.

If you have 2 minutes: **read sections 1, 5, and 6** — questions, first-five-minutes flow, common stumbles.

If a team asks "what does the kit have?" or "what could we build?" — point them at `specs/README.md` first, then this guide.

---

## 1. The Five Questions

Use these before any template. These come from `docs/facilitator-quick-card.md`:

1. **What are you offering?**
2. **What do you hope it helps with?**
3. **What should it not be used for?**
4. **Is anything private, protected, or review-required?**
5. **Who should be credited or asked?**

You are listening, not prescribing. Take notes.

---

## 2. Boundary Vocabulary — Quick Reference

| Term | Meaning | Reach for when |
|---|---|---|
| **marker-only** | Acknowledged as present; content stays protected | Indigenous / ceremonial / steward-held / Nation-specific material |
| **not-for-AI** | Can be discussed/shared/displayed, but never sent to a compute engine | Sensitive locations, unvetted claims, observer contact details |
| **not-for-reuse** | Useful for the Jam; do not build products with it | Experimental protocols, one-time prompts, internal learnings |
| **private** | Only for the contributor or named stewards | Personal notes, relationship details, private commitments |
| **protected** | Requires explicit authority to use; do not disclose to ask permission | Cultural, linguistic, ceremonial, treaty-bound, credential-bound |
| **review-required** | Cannot move forward until the right authority clears it | Anything that might be cultural, governance, legal, steward-held |
| **do-not-compute** | Hard boundary: exclude from indexing, embedding, routing, summarization, AI | Protected material, sensitive observations, unvetted claims |
| **visibility_tier** | T1–T4 (public, local-only, private, not-for-computation) | Governs who can see the record; used in witness schema |
| **display-approval** | Separate from creation consent. Yes to build ≠ yes to public display | Before any receipt wall item, story, screenshot, public readout |
| **ai_input_scope** | Does the AI lane touch this offering? whole / partial / none | Recorded in team-submission-v0; governs what's sent to TELUS |

**Mentor script when naming a boundary:**
> "You don't have to disclose what's protected to say it exists. I can write: 'This team brought cultural material that needs [authority name]'s review before any use.' That's it. The content stays safe. The Jam record shows respect."

---

## 3. Specs Menu — What to Recommend for Which Team-Shape

The full menu lives at `specs/README.md`. Recommend by team-shape:

| Spec | Best for teams interested in… | Single-file CLI buildable in 2 days? |
|---|---|---|
| **Witness Record Interop Profile** | Portability of attestation/review records across tools | Yes ✅ — preflight ran on Gemma + Qwen |
| **Claims Evidence Coherence Report** | Public claims needing evidence/freshness audit; steward-facing | Yes ✅ — preflight ran on Gemma + Qwen |
| **Sensor To Receipt Pipeline** | Citizen science, monitoring, observation → reviewable evidence | Yes ✅ — preflight ran on Gemma + Qwen |
| **Untracked Allocation Ledger** | Acknowledging support without surveillance pressure | Yes ✅ — preflight ran on Gemma + Qwen |
| **Commitment Pool Route Diagnostic** | Offers + needs + commitments routing into a shared pool | Partial — needs more context; better with composition |
| **Flow Funding Frontier Map** | Mapping edges: dreams → commitments → witnessed work → support | Composition-required (works with Commitment Pool + Allocation Ledger) |
| **Bioregional Mapping Layer Board** | Multi-layer place maps (ecological + cultural + economic) | Composition-required (works with Living Atlas + Sensor Pipeline) |
| **Living Atlas Coherence Packet** | Workshop contributions → atlas records with consent preservation | Composition-required |
| **Bioregional Insights Briefing** | Steward-reviewed briefs from claims/sensor/evidence | Composition-required (needs upstream specs) |
| **Risk and Insurance Coherence Map** | Resilience signals without becoming underwriting | Composition-required (needs claims + sensor + observation data) |
| **Participant Gateway** | Improving invite/consent/entry flow; app UX | Doc-shaped (mock or static HTML) |
| **Graph Chat Witness Sidecar** | Chat answers ↔ claims ↔ evidence ↔ source coherence | Doc-shaped (UI-heavy, integrate later) |
| **Receipt Wall Story Gallery** | Displaying what happened with consent gates | See `examples/sample-submission-receipt-wall/` for a worked CLI version |
| **Private Learning Ledger** | Learning from steward actions without exposing data | Composition-required (needs upstream action records) |
| **Dream To Fulfillment Board** | Vision → promise → witnessed delivery tracking | Composition-required (needs witness + commitment) |
| **Spec Composer Bundle Board** | Composing fragments into candidate bundles | Doc-shaped (markdown kanban; facilitator board) |

**Sample worked examples to show:**
- `examples/sample-submission-pair/` — Kelp Watch (numeric rollup, 6/6 both models)
- `examples/sample-submission-receipt-wall/` — Story Receipts (markdown wall, Gemma fixed, Qwen partial)
- `examples/sample-submission-commitment-pool/` — Pool Route Diagnostic (per-kind diagnostic, Gemma 7/7, Qwen 6/7)
- `examples/jam-dogfood-m2-6/` (in main IndigenomicsAI repo) — Tide Tally tag-counter (the M2.6 dogfood reference)

---

## 4. The First 5 Minutes With a Team

### Minute 1–2: Orient with the five questions
Pull up `docs/facilitator-quick-card.md`. Listen.

### Minute 2–3: Validate with the handout
If they hesitate on Q3 or Q4, show them `docs/participant-handout.md`:
- "What Can I Bring?" — yes, these kinds of things are valued
- "What Does 'Fits' Or 'Does Not Fit Yet' Mean?" — non-fit is not failure

Say: **"Doesn't-fit-yet is a real outcome. We will witness that together."**

### Minute 3–5: Map only if they're ready
One clarifying question:
> "Is this more like a **small tool** (you'd write code and ship in 4 hours) or more like a **composition** (multiple people's offerings, fit-checked)?"

**Small tool path** → `specs/README.md` + point to Witness / Claims / Sensor / Untracked Allocation as preflighted-good single-file CLIs.

**Composition path** → `examples/composition-v0/README.md` + `workshop/spec-composition-matrix.md`. Map their offerings first; bundle suggests itself.

---

## 5. "Doesn't Fit Yet" / Refusal — How to Reinforce

This is counter-intuitive to most participants. Every participant's default is "make it work or we failed." Mentors reinforce repeatedly that **non-fit and refusal are first-class Jam outcomes.**

### Key phrasings (memorize one):

- *"Does not fit yet is not a failure. It may need more time, clearer permission, a different bundle, human review, or protection."* (participant-handout)
- *"A refusal can be a complete offering."* (facilitator-quick-card)
- *"Preserve separate: the material can only be represented as present, protected, or review-required. Do not simulate protected content."* (spec-composition-matrix)

### When a team is blocked or forcing a fit:

> "Your offering did not fit the bundles we're testing in the Jam. That's not failure — it's real information. We can record it as 'not-fit-yet' and preserve it. It might fit a different bundle later, or it might need more time. Either way, the Jam witnesses that it happened and you contributed."

---

## 6. Common Participant Stumbles + Mentor Lines

### "We built it, so can we show it publicly?"
**No.** Display is separate from build. Display approval may need additional review.
> "Saying yes to the build is not the same as saying yes to the receipt wall. Those are separate choices."

### "What if our offering is too weird / small / not finished?"
The handout says you can bring anything; teams will doubt.
> "Finished is not a requirement. Unfinished, exploratory, reflective, relational — those are all valid offerings. What matters is clarity about what it is and what you don't want it used for."

### "Can AI tell us if our idea is good?"
**No.** AI helps with execution, not judgment.
> "AI can help with execution, not judgment. Judgment is humans and stewards."

### "We have protected material to contribute. Can we?"
**Yes.** Marker-only is valid.
> "Marker-only is valid. You name what's there, what it is, who needs to review it — but you don't disclose it. We record that it's here and that it's protected. That's a real contribution."

### "Our build attempt failed. Is that bad?"
**No — it's data.**
> "Build attempts that fail are as valuable as ones that succeed — if we witness what happened and learn from it. That's the receipt."

### "What if I change my mind about something we recorded?"
**Withdrawal is built-in.**
> "We can mark it withdrawn. The ledger keeps the entry, marks the change, and the public summary updates."

---

## 7. The Freeze Step — Load-Bearing

Once a team commits to a build attempt and freezes, new ideas need re-freeze before they enter the build lane.

### Freeze checklist (from facilitator-quick-card):

- [ ] Team has reviewed the final vision/spec text
- [ ] Team has confirmed which offerings are included in the build attempt
- [ ] Included offerings have cleared text
- [ ] Private, protected, marker-only, not-for-AI, and not-for-reuse records are **named only as boundaries**
- [ ] Tuesday sharing scope is explicit (whole / partial / spoken-only / none)
- [ ] AI/TELUS input scope is explicit (whole / partial / none)
- [ ] Build path is confirmed (hand / own-AI / TELUS lane / mixed)
- [ ] "Witnessed working" is understandable to a reviewer
- [ ] Any disagreement or unclear consent → `needs-review`, not frozen

### Confirmation statement (read aloud to the team):

> "This submission is frozen for a build attempt. It is not approval, certification, authority, or reuse permission. New ideas require re-freeze before they enter the build lane."

---

## 8. Cross-References — Which Doc/Spec to Pull Up

| If a team asks… | Open |
|---|---|
| "What's the menu of things we could build?" | `specs/README.md` |
| "What does a finished submission look like?" | `examples/sample-submission-pair/` |
| "What does the AI lane actually do?" | `examples/sample-submission-pair/preflight-findings.md` + `runs/` |
| "What does the Tuesday witness record look like?" | `examples/sample-submission-pair/sample-witness-record.md` |
| "How do offerings become a bundle?" | `examples/composition-v0/` + `workshop/spec-composition-matrix.md` |
| "What can I bring? Is X valid?" | `docs/participant-handout.md` |
| "Can I refuse to put X in the build?" | `docs/participant-handout.md` (refusal section) + this guide §5 |
| "What does AI not do?" | `docs/participant-handout.md` → "What Will AI Not Do?" |
| "What's the schema for our submission?" | `templates/team-submission-v0.md` |
| "What's the runtime packet that goes to TELUS?" | `templates/agentic-build-packet-v0.md` |
| "What's the schedule? Where's lunch?" | `docs/jam-day-timeline-v0.md` |
| "How do I write a witness record on Tuesday?" | `examples/sample-submission-pair/sample-witness-record.md` + `templates/witness-rollup.md` |

---

## 9. Likely Tripping Points (Subtle Vocabulary)

### "Coordination Canoe" is an English working metaphor — not a cultural claim.
> "This is our local working name for the pattern. It is not a cultural, language, or protocol claim."

### "Waka" refers to Austin Wade Smith / RiverComputer's project, not the Creator Jam pattern.
Do not conflate. Glossary explicit.

### "Freeze" ≠ "Consent."
Freeze is "spec locked, build can start." Consent was set in the boundary fields. They're different moments.

### "Witness record" ≠ ceremonial witnessing.
The schema is structured attestation. Ceremonial witnessing requires different authority.
> "When we say 'witness record,' we mean a documented observation. That is different from Knowledge Keeper witnessing or ceremonial witnessing, which requires different authority."

### "Acceptance criteria" / "witnessed working" / "expected outputs"
These are used near-interchangeably in different docs. They all mean the same thing: **how we know it worked**. Clarify when teams encounter both terms.

---

## 10. Carol Anne 1:1 Check-Ins

Carol Anne offers 15–20 min 1:1 check-ins as an Indigenous-mentorship resource.

Pull her in for:
- Any team wrestling with cultural-framing questions
- The Victoria-cohort participant who self-identified as Indigenous
- Teams uncertain about how to name or honor a Nation-specific or protected element

Eve has the scheduler. Bill Edmunds is the broader floater mentor.

---

## 11. Cross-Team Coordination

Four artifacts close the cross-team gaps surfaced in the May 24 UX walk. Open these when teams want to coordinate, compose, or hand offerings to each other:

- **`templates/stigmergic-offering-board.md`** — a shared sticky-card board where teams post what they're making, who might use it, and what they're looking for; the surface other teams scan in a gallery walk.
- **`workshop/tuesday-composition-sprint-v0.md`** — a 90-minute opt-in Tuesday-morning playbook (gallery walk → mentor matches → merge experiments → comprehension checkpoint → decision) for teams that want to discover cross-team compositions before the 3 PM canoe landings.
- **`templates/composition-handoff-receipt.md`** — when Team A's output becomes Team B's input, this receipt preserves the source team's original permission state, names the receiving team's new use intent, and records the rollback path if the source team later withdraws.
- **`workshop/mentor-composition-decision-card.md`** — a 90-second 6-question mentor flowchart (shared interface? compatible permissions? AI boundaries? fresh evidence? no protected material? → "candidate for compose") for triaging promising pairs without making value judgments.

---

## What to leave out

This guide intentionally does **not** include all 14 specs in detail, all templates, or all workshop docs. Those live in the kit. Open the kit on a laptop when detail is needed.

## What's pre-loaded for you

- The kit repo is public: https://github.com/DarrenZal/IndigenomicsAI-CreatorJamKit
- The sample pairs are clickable from your phone
- The preflight findings show real model behavior on each sample/spec
- The timeline is canonical-as-of-May-22

Good Jam. 🛶
