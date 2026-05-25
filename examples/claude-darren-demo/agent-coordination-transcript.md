---
doc_id: kit.examples.claude-darren-demo.agent-coordination-transcript
doc_kind: worked-example-transcript
status: v0
date: 2026-05-25
audience: participants, mentors, agent designers
depends_on:
  - participant-agent-context/PROMPTS_FOR_AGENTS.md (Prompt 4)
  - specs/coordination-protocol-v0.md
  - examples/claude-darren-demo/README.md
  - templates/stigmergic-offering-board.md
  - templates/composition-handoff-receipt.md
---

# Agent-to-Agent Coordination — Worked Transcript

A screenplay-style transcript showing the two teams from the claude-darren-demo (Kelp Bed Observers and Steward Calendar) discovering each other through their team agents, going through the consent moments, hitting a refusal, surviving a withdrawal, and arriving at a joint witness record.

Both agents are running Prompt 4 (Collaboration Facilitator) with the participant-agent knowledge bundle loaded. Each agent operates inside its team's gateway session (Shawn's three-dropdown access surface — specs / models / harnesses — gated by team-key token via `/jam/redeem` → `/jam` → `/api/jam/*`). Cross-team messages move through the gateway's chat surface using the schema in `specs/coordination-protocol-v0.md` (`share_request`, `share_grant`, `share_refuse`, `withdraw_notice`, `boundary_marker`, `composition_propose`, `witness_observe`). The two teams post to the same `stigmergic-offering-board`.

> **This is a designed transcript demonstrating the protocol — not a recording of real teams.** Names and dialogue are illustrative.

---

## Cast

- **Team Kelp Bed Observers (Vancouver)** — two people present: Mira (technical), Jess (community-facing). Authorization: `display: whole / ai_input: whole / reuse: ask-first`. One `not-for-AI` boundary on observer real names.
- **Kelp agent** — their team's Prompt 4 instance.
- **Team Steward Calendar (Victoria)** — two people present: Ravi (data), Lin (facilitator). Authorization: `display: partial / ai_input: partial / reuse: ask-first`. One `protected` boundary (host-Nation stewardship cycle reference), one `not-for-AI` boundary (volunteer real names).
- **Steward agent** — their team's Prompt 4 instance.
- **Mentor (Bill)** — floater on shift when a `protected` boundary surfaces.

---

## SCENE 1 — Discovery on the offering board

*[Monday 2:34 PM. Gallery walk just ended. Both teams are back at their tables. The stigmergic offering board is open on a shared Notion page.]*

**Kelp agent** *(to Kelp Bed Observers team, inside the team's `/jam` session)*:
> A new card just went up on the board from `team-steward-calendar`. Their `what_i_make` reads: "A per-bioregion seasonal calendar of stewardship actions (work-parties, kelp counts, eelgrass surveys, plantings)." Their `intended_use` is "to let a new volunteer see where they fit." Their `consent_gate` is **review-required**. Integration cost they posted is 3.
>
> Substrate reminder: I am operating inside this team's gateway session. I don't have visibility into the other team's chat unless they choose to share through the protocol. Any message I draft routes through the gateway's cross-team chat surface — both teams have to consent before it goes.
>
> I notice their bioregion column overlaps with our site list — Boundary Bay is on both. Want me to draft a `share_request` to their agent? If yes, what exactly should I share about us?

**Mira:** Just that we exist and what we make. Don't share the dataset, don't share any cleared_text. One sentence on the gap we're addressing. Let them decide whether it's worth a conversation.

**Jess:** Agreed. And flag that we have a `not-for-AI` boundary on observer names — they should know that going in.

**Kelp agent:** Got it. Here's the exact draft. This is what would leave your team:

> ```
> message_type: share_request
> from: team-kelp-bed-observers (agent)
> to: team-steward-calendar (agent)
> body: |
>   Hi. We saw your card on the offering board. We make a per-site
>   condition rollup from public-shoreline kelp canopy observations
>   (Boundary Bay, Lighthouse Park). Our `ai_input_scope` is `whole`
>   on the cleared dataset; we hold one `not-for-AI` boundary on
>   observer real names.
>   We're not asking to share data yet. We're asking whether a
>   conversation about whether our outputs could feed your seasonal
>   calendar would be welcome.
> consent_terms: response (yes / no / edit / conditions) requested.
>   No data attached. No reuse implied.
> ```

> Five-question check: who benefits — both teams might learn whether their outputs compose; what's shared — that we exist plus one sentence on what we do; what stays held — our dataset, our cleared_text, observer names; withdrawal — you can retract this share_request before they respond; witness — Mira holds technical ground truth, Jess holds community framing. Send?

**Mira:** Send.

**Jess:** Send.

**Kelp agent** *(to Steward agent, on the cross-team channel)*: *[posts the share_request verbatim]*

---

## SCENE 2 — The receiving team considers

**Steward agent** *(to Steward Calendar team)*:
> Kelp Bed Observers sent a `share_request`. Only their introduction text is in their message — no data, no cleared_text. Their `not-for-AI` boundary on observer names is named upfront. They're asking for a conversation, not a transfer.
>
> Three options under coordination-protocol-v0:
>
> 1. **`share_grant`** — start a scoped conversation; nothing else commits.
> 2. **`share_refuse`** — record "does not fit yet" as a complete outcome; the offering board reflects it.
> 3. **`share_grant` with conditions** (counter-offer) — accept conditionally; for example, "yes but only if our `protected` host-Nation reference is preserved on your side and never enters any joint surface."
>
> Reminder: our `display_scope` is `partial`. If we say yes to a conversation, anything that comes back from them does not automatically become joint-displayable. That's a separate consent moment.

**Ravi:** I want to talk to them. Their observations are exactly the column we're missing.

**Lin:** Counter-offer, then. Yes to conversation. Explicit condition: the host-Nation reference is `protected`, never enters any joint anything, and a mentor reviews before we go past "conversation" into "composition."

**Steward agent:** Drafting. Here is the exact reply:

> ```
> message_type: share_grant
> from: team-steward-calendar (agent)
> to: team-kelp-bed-observers (agent)
> in_reply_to: <previous share_request id>
> grant_kind: conditional (counter-offer)
> body: |
>   Yes to a scoped conversation about whether our outputs compose.
>   Two conditions:
>   1. We hold a `protected` host-Nation stewardship cycle reference.
>      It is named only as a boundary, never in our dataset, our AI
>      input, or any display. If we move past conversation toward
>      composition, that boundary survives composition intact and a
>      mentor reviews the compose moment.
>   2. Our `ai_input_scope` is `partial`. Any joint surface inherits
>      `partial` as the floor — no upward intersection.
> consent_terms: same scope as your share_request — no data attached,
>   conversation only.
> ```

> Five-question check: who benefits — same as before; what's shared — our two conditions in plain language; what stays held — the protected reference and our cleared_text; withdrawal — either side can retract at any point in the conversation; witness — Lin holds the boundary framing, Ravi holds the data shape. Send?

**Ravi:** Send.

**Lin:** Send.

---

## SCENE 3 — A real refusal

*[Tuesday 9:50 AM. Both teams are in the same room. Conversation has been going for about 20 minutes. Kelp Bed Observers ask whether Steward Calendar's underlying action log — not the calendar output, the raw per-action records — could be added to their condition report as a "stewardship pressure" column.]*

**Steward agent** *(to Steward Calendar team)*:
> Kelp Bed Observers' agent just relayed a follow-up `share_request`. They're asking for the per-action records (date, site, action type, count) — the raw log behind the calendar, not the calendar itself. Their use intent: a "stewardship pressure" column on the condition report.
>
> Per coordination-protocol-v0, this is a new ask — broader than the conversation we agreed to. It needs fresh consent, not implied consent.
>
> Surfacing what they'd actually get if we said yes: 1,247 rows of per-action records spanning four bioregions. Some rows have volunteer aliases that map to real names in our roster — a `not-for-AI` boundary. Some rows are at sites where the host-Nation reference shapes our private thinking about the action; the reference is not in the data, but the actions at those sites are colored by it in ways that are not visible from the row.

**Lin:** That's where I get uncomfortable. The data itself is cleared, but the sites that touch the protected reference — even cleared rows at those sites — start to read differently when they're being used as a "pressure" signal in someone else's tool. Pressure for what? Pressure as named by whom?

**Ravi:** I hear you. I was leaning yes on the data but I want to sit with what you just said.

**Lin:** Let's decline this one. Not refuse the team — refuse this specific ask. The calendar-shape output we already discussed composes fine. The raw log doesn't. "Does not fit yet."

**Steward agent:** Drafting the refusal. This is a complete outcome under refuse-and-record discipline, not a failure. Here's the exact reply:

> ```
> message_type: share_refuse
> from: team-steward-calendar (agent)
> to: team-kelp-bed-observers (agent)
> in_reply_to: <follow-up share_request id>
> refuse_kind: does-not-fit-yet
> body: |
>   We sat with the raw per-action records ask and decided it does not
>   fit yet. The calendar-shape output (per-bioregion seasonal totals)
>   continues to be in scope for our conversation; the underlying log
>   is not. Reason in our own words: cleared rows at sites colored by
>   our protected reference begin to read differently when used as a
>   "pressure" signal in another team's tool, and the framing of
>   "pressure" is not ours to author here.
>   This is not a no to the team. It is a no to this specific share.
> consent_terms: this refusal is recorded on the offering board under
>   "does not fit yet" outcomes; no rollback needed because no data
>   moved.
> ```

> Five-question check: who benefits from naming this clearly — both teams; what's shared — the refusal and the reason in our words; what stays held — the raw log, the protected reference, the framing question; withdrawal — n/a, nothing moved; witness — Lin held the boundary read, Ravi held the data shape. Send?

**Lin:** Send.

**Ravi:** Send. And let's keep the calendar-output conversation going.

**Kelp agent** *(receiving, to Kelp team)*:
> Steward Calendar's agent sent a `share_refuse` (`does-not-fit-yet`) on the raw-log ask. They were explicit that this is a no to the share, not a no to the team. The calendar-shape conversation continues. I'll record it on the offering board as a "does not fit yet" outcome — that's a first-class Jam result, not a failure.

**Jess:** That's fair. We were asking for more than we'd thought through.

**Mira:** Let's stay with the calendar shape.

---

## SCENE 4 — A `protected`-touching composition proposal goes to mentor

**Mira:** Quick question before we go further — what's this conversation costing us in token spend? I want to know what we're sitting on.

**Kelp agent:** Reaching for the Grafana / TELUS metrics surface. For our gateway session today: ~14,200 tokens out, ~8,900 tokens in across the model we're using (Qwen 3.6 35B has token-usage tracking; Gemma reports run-level only). I can show you the per-message breakdown if you want. I cannot see Steward Calendar's session — their team-key bounds their metrics.

**Mira:** That's fine. Keep going.

**Kelp agent** *(continuing)*:
> The calendar-output conversation has converged. Both agents have drafts of a `composition_propose` that would create a joint candidate bundle (your condition report + their per-bioregion calendar, both cleared inputs only). Because Steward Calendar holds a `protected` boundary that touches the composition stack — even though the protected content is not in either input — coordination-protocol-v0 routes this through a mentor before either team's `composition_propose` becomes a candidate bundle.
>
> Both agents are ready to send to Bill (mentor on shift). I will not send without your sign-off on the exact text. Steward agent has parallel sign-off on their side.

**Mira:** Sign-off.

**Jess:** Sign-off.

**Kelp agent and Steward agent** *(joint message to mentor channel)*:
> ```
> message_type: composition_propose_mentor_review
> from: team-kelp-bed-observers (agent) + team-steward-calendar (agent)
> to: mentor channel
> bundle_inputs:
>   - team-kelp-bed-observers: cleared canopy observations (whole)
>   - team-steward-calendar: cleared stewardship actions (partial)
> protected_boundary_present: true (steward team)
> joint_authorization_floor: partial / partial / ask-first
> mentor_question: We are ready to write a candidate bundle. The
>   protected host-Nation reference is not in either input and survives
>   composition as a marker-only boundary. Please review whether we
>   have honored the boundary correctly before we re-freeze.
> ```

**Bill (mentor):** *[reads, asks both teams two questions, confirms the protected boundary is named-only and not transformed, signs off]*
> Compose. The boundary is held. The intersected authorization (`partial / partial / ask-first`) is the right read. Re-freeze with both teams' facilitators present.

---

## SCENE 5 — Joint candidate bundle drafted by both agents

**Kelp agent** *(to Steward agent, on cross-team channel)*:
> Drafting the candidate bundle now. I'll surface our team's contribution; you surface yours. Each team's boundaries stay namespaced. The intersected authorization is `partial / partial / ask-first` per Bill's sign-off.
>
> Compositional-field-orientation says composition adds boundaries; it never subtracts. I'm carrying `team-kelp-bed-observers::b1` (observer real names — not-for-AI) forward as-is.

**Steward agent:** Confirmed. Carrying `team-steward-calendar::b1` (host-Nation reference — protected) and `team-steward-calendar::b2` (volunteer real names — not-for-AI) forward as-is. The intersected `authorization_notes` reads: "composed: both teams must re-confirm before any build attempt or display."

*[Both agents jointly draft `candidate-bundle.json` and surface it to both teams. Both teams read, both teams' facilitators confirm. Joint re-freeze happens.]*

---

## SCENE 6 — A withdrawal late in the process

*[Tuesday 1:15 PM. Build has run. Both teams are reviewing the run output before the canoe-landing witness record.]*

**Jess** *(to Kelp agent)*: One of our observers — Sam — just looked at the joint output and said they don't want their cleared canopy readings from Boundary Bay site 3 used in the joint surface anymore. They're fine with the readings being in our team-only condition report, but not in the composed bundle that gets displayed jointly. Can we do that?

**Kelp agent:** Yes. This is a scoped withdrawal under coordination-protocol-v0 — Sam is withdrawing one element from one surface, not the whole offering. Three things will happen:
>
> 1. I draft a `withdrawal` message to Steward agent naming exactly which readings, which surface (the joint display, not the team-internal report), and the requested action (remove from the candidate bundle).
> 2. Steward agent surfaces this to their team. Their team's response is theirs.
> 3. The witness record will note that the withdrawal happened and was honored — that's a healthy record, not a failure.
>
> Five-question check: who benefits — Sam, primarily, by holding their boundary; what's shared — the fact of the withdrawal and the scope; what stays held — the readings themselves stay in your team-internal use; withdrawal mechanism — this IS the withdrawal mechanism; witness — Sam holds situated stake on their own readings.

**Jess:** Send.

**Kelp agent** *(to Steward agent, routed through the gateway cross-team chat surface)*:
> ```
> message_type: withdraw_notice
> from: team-kelp-bed-observers (agent)
> to: team-steward-calendar (agent)
> scope: Boundary Bay site 3 canopy readings, observer-alias "sam-bb"
> surface: joint composed bundle / joint display only
> retained_for: team-kelp-bed-observers internal report
> rationale (in Sam's words, with consent to share this much):
>   "Fine in our own report; not for the joint surface."
> requested_action: remove from candidate-bundle.json and any joint
>   build artifacts before the Tuesday witness record.
> ```

**Steward agent** *(to Steward team)*:
> Kelp Bed Observers' agent sent a `withdraw_notice`. One observer is pulling their readings from Boundary Bay site 3 out of the joint surface (retained for their own team's use). This is the withdrawal mechanism working as designed — it's a healthy moment, not a problem.
>
> Recommended response: acknowledge, regenerate the candidate bundle without those rows, and note the withdrawal in the joint witness record under `untracked` or `what_diverged`. Sam's reasoning stays in their words; the witness record renders the fact of the withdrawal, not the contents of Sam's reasoning.

**Ravi:** Acknowledge and regenerate.

**Lin:** Agreed. Note it in `what_diverged` — the bundle changed late, and that's part of the record.

---

## SCENE 7 — Ceremonial witnessing step (canoe landing)

*[Tuesday 2:45 PM. Canoe-landing in 15 minutes. This is the ceremonial witnessing step at the end of an agent build — the moment Shawn names where human feedback closes the loop. Both agents emit `witness_observe` messages and switch to Prompt 3 (Witness Record Drafter) to draft the joint witness record together.]*

**Kelp agent** *(emitting `witness_observe`, handing off to its team)*:
> ```
> message_type: witness_observe
> from: team-kelp-bed-observers (agent)
> scope: joint composed build, Tuesday 2:45 PM
> handoff_to: Prompt 3 (Witness Record Drafter)
> receipt_statement: "This record states what happened. It does not
>   establish authority, approval, certification, legitimacy,
>   community consent, or readiness for reuse."
> ```
>
> I've drafted what_was_attempted, what_happened, and what_held for our side. Steward agent has drafted the parallel sections for their side. The two agents are surfacing the joint draft to both teams together. The withdrawal goes in `what_diverged` — Sam's readings were removed from the joint surface on Tuesday afternoon, and the bundle was regenerated.
>
> One section neither agent will draft: `what_carries`. That's for the humans. Two or three lines, in their own words.

**Mira:** I'll write ours. Something like: *"We thought we were building a tool. We were building a conversation between two teams that didn't know each other on Monday morning."*

**Lin:** Ours: *"The protected boundary survived composition. That's the part I'll remember."*

---

## META — What to notice

Some patterns this transcript surfaces, for designers and mentors thinking about how agent-to-agent coordination works in practice:

- **Every share moment goes through the team.** The agents never send a `share_request`, `composition_propose`, or `withdrawal` without showing the exact text to their team and getting explicit sign-off. The five-question discipline is the consent prompt, not a checklist.
- **Asymmetric authorization intersects downward, not upward.** Kelp's `whole` and Steward's `partial` compose to `partial`. The compositional-field-orientation rule is load-bearing: the more restrictive team's boundary holds.
- **Refuse-and-record is a complete outcome, not a failure mode.** The raw-log refusal in Scene 3 is the protocol working — naming a "does not fit yet" outcome in the team's own words, recording it on the offering board, and continuing the conversation that does compose.
- **`Protected` routes through a mentor.** Even when the protected content is not in the inputs, its presence in the team's stack triggers mentor review before composition. The agents do not bypass.
- **Withdrawal is scoped.** Sam withdraws specific readings from a specific surface, not the whole offering. The agent draft makes the scope explicit; the receiving team responds; the witness record renders the fact, not the contents of the reasoning.
- **The agents draft; the humans decide.** Verb discipline holds throughout — surface, render, draft, propose, ask. No `validate`, `certify`, `approve`, `authorize` from either agent.
- **`What_carries` is for humans.** Both agents stop short of drafting it. Carol Anne's framings and Lin's "the protected boundary survived composition" are human language, not agent language.
- **Untracked is honest.** The 20-minute conversation in which Lin sat with the "pressure" framing question, and the mentor's two questions to Bill, do not appear in the witness record as content — only as the fact of the conversation. That fraction is visible; the contents are not.

Reference: this transcript is designed against Prompt 4 (Collaboration Facilitator) in `participant-agent-context/PROMPTS_FOR_AGENTS.md` and the message schema in `specs/coordination-protocol-v0.md`. Both should be read alongside this transcript when designing or instantiating an agent for a team.

---

## Boundary

This is a designed transcript demonstrating the protocol — not a recording of real teams. The teams, their members, the observer "Sam," and the dialogue are illustrative. No real host-Nation stewardship-cycle reference is named or used. The condition thresholds, action types, and consent flows are kit-vocabulary illustrations and do not constitute ecological certification, governance approval, or a model for any specific Nation's protocols.
