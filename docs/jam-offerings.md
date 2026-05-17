# Jam Offerings — Open Kit + Pathways

**For:** Indigenomics Creator Jam (May 25-26, 2026)
**From:** Darren Zal (Cascadia Systems Inc, working alongside Shawn Anderson on Indigenomics AI)
**Status:** v0.1 — Draft sketches, not finished products. Things will land + sharpen across the next 12 days.

## What this is

A set of things I'm building toward the Jam. They're meant to be useful for other Jam participants — take what's useful, integrate, remix, take inspiration, or just ignore them and build your own thing. None of these are required. They're offerings, not gates.

I'm also bringing them as my own Jam contribution — I want to participate AND offer infrastructure others can plug into, not pick one or the other.

The Jam is a place to learn together and build together. People bring offerings: ideas, sketches, prompts, code, practices, commitments, refusals, and questions. Some offerings will fit together into shared bundles; some will not fit yet and should be preserved with care. The goal is not to force one system, but to make contribution, consent, attribution, reciprocity, repair, and next commitments more visible.

## What this is not

- Not a "platform" you have to use
- Not a "menu" of fixed choices — these are starting points, remix freely
- Not finished — most are v0.1; expect rough edges
- Not authoritative on Indigenous-cultural framings — worked examples use **Salish Sea ecological** content (kelp, herring, salmon, eelgrass) which is openly accessible. Cultural / linguistic / ceremonial content requires Nation-specific authorization that's separate from this kit.

## Participant-facing offerings

These are the invitations participants should see first. They are about learning together, building together, making offerings visible, and preserving boundaries.

### 1. Open Kit: Commitments + Receipts

**Invitation.** Try a narrow public ecological demo where one commitment becomes visible, enters a small local pool, and produces a receipt record.

Open Kit is a guided public example, not software participants need to install or adopt.

**What participants experience.** A facilitator opens the commitment-pool primer, enters one public ecological commitment, shows the commitment tuple, and shows the v0.2-style receipt fields.

**What this helps with.** Contribution, attribution, permission, refusal, repair, and reciprocity become visible without needing a production system.

**What this is not.** Not a production pool, not a monitoring program, not a claim of legitimacy or authority, and not a place for protected content.

**Current scope.** This is the first public vertical slice. Keep it narrow: commitment-pool primer, v0.2 receipts, sample receipt, and manual/static witnessing.

### 2. Offering Integration Session

**Invitation.** Bring an offering into a facilitated session and find out what it can connect with, what needs review, and what should be protected or preserved for later.

**What participants experience.** The facilitator asks the live quick card questions below. Participants do not need to fill YAML or learn the operator template.

**What this helps with.** The room can see what fits, what does not fit yet, what needs consent or review, and what can move toward a shared bundle.

**What this is not.** Not a platform requirement, not a forced merge, and not a way to process protected material with AI.

### 3. Handoff Packet Studio

**Invitation.** Turn a selected bundle into plain build attempt instructions that a person or agent can try later.

**What participants experience.** A facilitator/operator summarizes the selected offering bundle, what inputs are allowed, how we know it worked, and what must not happen.

**What this helps with.** The final witnessing surface can show an honest attempt: what passed, what was partial, what failed, what was refused, and what was not run.

**What this is not.** Not the first place where offerings are merged, and not a decision about legitimacy or authority.

### 4. Receipt Wall / Witnessing Surface

**Invitation.** See selected receipts and decisions displayed as a readable "what happened" surface.

**What participants experience.** Receipt Wall uses sample receipts or receipts that people have explicitly approved for display. It can also show selected bundle decisions, review-required notes, and unresolved offerings.

**What this helps with.** The room can witness contributions, decisions, refusals, and repair paths without relying on memory.

**Current status.** Deferred unless explicitly used in the narrow Open Kit rehearsal with public sample receipts only. Real participant receipts require display consent.

### 5. Consent / Refusal / Review Desk

**Invitation.** Name what should not be used, what needs review, who should be asked, and what should be protected and preserved.

**What participants experience.** The facilitator records refusals, review routes, withdrawals, and decisions about what does not fit yet without exposing protected material.

**What this helps with.** Refusal and non-use become visible Jam outputs, not hidden blockers.

**What this is not.** Not a computation of legitimacy, not a substitute for steward/community/Nation authority, and not a request to disclose protected content.

## Live facilitator quick card

Use these five questions in the room before any operator template:

1. What are you offering?
2. What do you hope it helps with?
3. What should it not be used for?
4. Is anything private, protected, or review-required?
5. Who should be credited or asked?

## Appendix: Operator And Deferred Tracks

These tracks support the Jam, but they should not be presented as participant requirements.

| Track | Purpose | Jam posture |
|---|---|---|
| Schema maintenance | Keep receipt schema v0.2 usable and document future schema changes. | Operator/internal. |
| Receipt validation / field checks | Check that receipts are field-shaped enough for the demo. `validates: true` means schema-shaped, not legitimate or authorized. | Operator/internal. |
| Frozen build-attempt packet | Preserve the selected Open Kit bundle as build attempt instructions. | Operator/internal; used only after the Offering Integration Session. |
| Partner/runtime integration | Coordinate model endpoints, notebooks, deployment, access, and logging. | Operator/internal. |
| TELUS/Jupyter optional showcase path | Show TELUS/Jupyter with public sample receipts if ready. | Deferred/operator track unless explicitly used in the narrow Open Kit rehearsal. |
| Waka / claims bridge | Explore cross-system anchoring with Austin Wade Smith / RiverComputer's Waka project without exporting protected content. | Deferred/operator track. |
| Full multi-witness runtime | Explore deeper AI review and evaluator patterns. | Deferred/operator track; not a blocker for Open Kit. |
| Knowledge Commons backend | Explore entity linking, contribution maps, and shared memory infrastructure. | Deferred/operator track; not a blocker for Open Kit. |

## Integration patterns

If you're building something for the Jam and want to connect with these:

- **Easiest:** answer the live quick card, then let the facilitator/operator wrap the offering if needed.
- **Open Kit path:** use the commitment-pool primer as a public ecological example of commitments + receipts.
- **Build attempt path:** after the group selects a bundle, help turn it into build attempt instructions.
- **Witnessing path:** use receipts when useful, but remember they record what happened; they do not establish legitimacy or authority.
- **Just inspiration:** take the ideas, remix them, or build your own version. No integration required.

## Sovereignty + IP discipline

- All ecological content uses CARE + CC-BY-SA + signed-attribution
- Cultural / linguistic / ceremonial content NOT included without Nation-specific authorization
- Full multi-witness runtime is an operator/internal track for now, not a participant-facing requirement.
- Witnessing receipts include sovereignty flags + IP framework slots so participants can declare their own posture
- Protected or authority-bound material should not be sent into AI for checking. The kit can record that review is required; it cannot compute legitimacy.
- Where agent execution is shown later, the preferred public demonstration path may use TELUS-hosted model resources and, where useful, TELUS/Jupyter notebook deployment. TELUS/Jupyter remains optional for the first Open Kit rehearsal path.

## How to get involved

- Q&A info-session next week (date TBC with Georgia) — happy to walk through any offering live
- Draft kit lands in this private participant repo as sample specs, templates, and build examples.
- Questions / collaboration / "I want to integrate" — get in touch via Indigenomics AI Devs Telegram / Indigenomics Creator Jam WhatsApp group

## Status + iteration plan

- **May 13:** witnessing-receipt schema v0.1 + commitment-pool primer v0.1 committed
- **May 16:** manual-first offering integration docs + Open Kit rehearsal path drafted
- **Week 2 (May 19-23):** test the quick card and narrow Open Kit flow with real people; keep RiverComputer Waka interop, full multi-witness runtime, TELUS/Jupyter, and Knowledge Commons backend as operator/deferred tracks unless explicitly cleared
- **Jam (May 25-26):** live Open Kit demo + Offering Integration Session support for participants who want it

See `2026-05-13-jam-build-sprint.md` for the day-by-day schedule.
