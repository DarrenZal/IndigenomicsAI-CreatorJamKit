---
doc_id: kit.docs.multi-agent-coordination-design
doc_kind: design-doc
status: v0
date: 2026-05-25
audience: kit authors, gateway developers, mentors thinking about agent tooling
---

# Multi-Agent Coordination — Design Doc (v0)

> First articulation. Design exploration, not implementation. Not approval or
> certification of any architecture. Iterates.

## 1. The question

The kit already ships three system prompts for participant-helping LLMs
([`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../participant-agent-context/PROMPTS_FOR_AGENTS.md):
spec-drafting / boundary-checker / witness-drafter), and two tools that
implement cross-team mechanics
([`tools/composition-merger.py`](../tools/composition-merger.py),
[`tools/withdrawal-propagation.py`](../tools/withdrawal-propagation.py)).
What is missing is the **agent-coordination layer** — how agents helping
*different* participants talk to each other (or refuse to) while honouring
the kit's boundary, authorization, and consent discipline
([`templates/team-submission-v0.md`](../templates/team-submission-v0.md),
[`docs/MENTOR_FIELD_GUIDE.md`](MENTOR_FIELD_GUIDE.md) §2 + §11).

Two sub-questions:

- **Within a team** — how do per-person agents help a team converge on one
  `team-submission-v0` without flattening divergence into false agreement?
- **Across teams** — how do agents help discover composable offerings
  (per [`tools/composition-merger.py`](../tools/composition-merger.py)) without
  silently leaking marker-only or protected content across membranes?

This doc is design-only. It does not specify code; it scopes the surface.

## 2. Four architectural routes

| Route | What it is | Pros | Cons |
|---|---|---|---|
| **Per-team agent** | One agent shared by a team | Fewer agents to coordinate; team divergence stays in the room | Erases per-person stake; one teammate's silence reads as consent |
| **Per-person agent** | Each participant runs their own agent | Each person keeps their own voice + memory; per-person consent decisions are first-class | N×N coordination cost; risk of fragmenting team discussion |
| **Hybrid (person + team)** | Each person has an agent; team has a thin coordinating agent that *only* mediates surfaces the team has authorized as shared | Honours per-person stake + gives the team a shared draft surface; team agent has no authority the team didn't lend it | Two layers to reason about; clear scoping required |
| **Multi-agent network** | Person agents + team agent + cross-team mediator agent(s) | Composes with multi-team discovery; supports the composition-merger pattern at agent layer | Coordination overhead; central-coordinator anti-pattern risk if mediator becomes authority |

**Recommendation: hybrid (person + team) as the primitive.** Person agents are
the *holders of stake*; the team agent is a *facilitation surface*, not an
authority. Multi-agent-network is the extension when a Jam team explicitly
opts into cross-team composition (Tuesday morning playbook,
[`workshop/tuesday-composition-sprint-v0.md`](../workshop/tuesday-composition-sprint-v0.md)).

Two non-negotiables make this work:

1. The team agent's memory **strictly composes from**, and never overwrites,
   what each person agent has authorized it to receive. (Wise legibility,
   per [`compositional-field-orientation.md`](../participant-agent-context/compositional-field-orientation.md).)
2. The cross-team mediator (if used) **never sees marker-only or protected
   content**. It sees only marker records (the existence of a boundary), in
   the same shape `team-submission-v0` exports them.

## 3. The three membrane operations

| Operation | Direction | What flows | Consent moment | Default |
|---|---|---|---|---|
| **Lift** | person → team | A contribution moves from a participant's private notes into the team-submission draft | Inline prompt: "Lift this to team? (whole / paraphrased / marker-only)" | Off — content stays with the person until explicitly lifted |
| **Cross-membrane** | team → team | An offering, boundary, or composition proposal crosses to another team | Inline prompt mirroring `composition-merger`: "Share with Team B? (cleared text / marker-only / refuse)" | Off — composition is opt-in per the May 24 UX walk |
| **Vertical** | agent → witness / operator surface | An observation about what happened (divergence, refusal, untracked allocation) reaches the witness record or mentor surface | Inline prompt: "Surface as observation to witness layer? (with-attribution / anonymized / refuse)" | Off; never auto — agent observations are flagged as observation, not authority |

For every membrane operation, the agent layer uses the same authorization
vocabulary the kit already publishes — `display_scope`, `ai_input_scope`,
`reuse_scope`, and the boundary types `marker-only`, `not-for-AI`,
`not-for-reuse`, `private`, `protected` ([template](../templates/team-submission-v0.md)).
No new vocabulary is invented; the agent layer is a *user* of the kit's
boundary language.

## 4. UX layers

Two distinct surfaces. The first absorbs defaults; the second enforces
discipline in the moment.

### 4a. Web-app settings (per Jam, per participant)

```
Defaults for my agent:
  Lift to team       : ask-each-time  / always-ask / on-explicit-only [default: on-explicit-only]
  Cross-team share   : refuse  / ask-each-time / on-named-team-only   [default: refuse]
  Surface to witness : ask-each-time / on-divergence-only / refuse    [default: ask-each-time]

Per-cross-team rules (override the default for one named team):
  + Team Kelp Watch  : ask-each-time  (Jam day 1, expires day 2 EOD)
  + Team Tide Tally  : refuse         (cultural protocol mismatch flagged by mentor)

Specific permissions:
  My agent may quote Carol Anne sources from the bundle.
  My agent may NOT speak in Carol Anne's voice on questions of standing.
  My agent may share boundary markers but never marker-only content.
  My agent may send observations to mentors but not to other teams' agents.
```

### 4b. Inline consent prompts (the discipline moments)

Concrete agent-to-participant prompts, one per membrane:

**Lift (person → team):**
> "You wrote: *'salmon timing in this estuary is shifting'*. The team is
> drafting its vision section. Lift this to the team draft? Options:
> (a) lift the whole sentence with your name, (b) lift paraphrased without
> name, (c) lift as a marker-only ('one teammate brought ecological-timing
> observation; content stays with contributor'), (d) keep private."

**Cross-membrane (team → team):**
> "Team Kelp Watch's agent is asking whether your team's `untracked
> allocation` ledger fragment could compose with their `sensor-to-receipt`
> pipeline. They have NOT seen the content; their agent saw the marker only.
> Options: (a) share cleared text labelled in the spec, (b) share marker-only
> (composition continues but content stays with us), (c) refuse with no
> reason, (d) refuse and ask facilitator to log the refusal as a learning."

**Vertical (agent → witness / mentor):**
> "I observed a divergence: two teammates wrote different framings of the
> refusal log. The spec-drafting partner prompt asks me to surface divergence
> rather than summarise it away. Send to the witness drafter as observation?
> Options: (a) yes with both framings preserved, (b) yes anonymized, (c) hold
> until end of session, (d) refuse."

## 5. How this composes with existing kit infrastructure

| Kit primitive | How the agent layer uses it |
|---|---|
| Boundary vocabulary ([Mentor Field Guide §2](MENTOR_FIELD_GUIDE.md)) | Agent prompts reuse the published terms; no synonyms |
| Authorization scopes (`display_scope`, `ai_input_scope`, `reuse_scope`) | Per-cross-team rules are stored as scope overrides; the team agent never exceeds the most-restrictive setting of its members |
| `composition-merger.py` | When two team agents agree to compose, they invoke the merger on their respective frozen submissions; the merger's `conflicts_surfaced` becomes the next mediator prompt |
| `withdrawal-propagation.py` | When a person withdraws a lifted contribution, the team agent runs the manifest against the propagation tool to show which surfaces (including cross-team bundles) need to update |
| `team-submission-v0` freeze | The team agent CANNOT push to the build packet directly; freeze is human + facilitator, per [template](../templates/team-submission-v0.md) §4 |
| `witness-record` (Tuesday) | Agent observations enter the witness layer as draft observations (Prompt 3), never as final witness statements; situated stake holders write the record |

The discipline is **already in the kit**. The agent layer's job is to honour
it at run-time, not to redefine it.

## 6. Implementation routes

### 6a. What Shawn's gateway already has (baseline)

Per the May 20 Shawn + Darren planning sync (operator-facing planning notes:
`docs/operations/2026-05-20-gateway-agentic-system-north-star.md` and the
companion action plan in the main IndigenomicsAI repo; see also the shared
vault note `Shared/IndigenomicsAI/Plans/shared-task-and-spec-coordination.md`)
— **not in this kit**, referenced for context — the gateway has a designed
spine and is partially built:

```
Participant Gateway      → access / identity / consent / model entry point
Spec Composer            → collects offerings, composes team vision/spec,
                           captures boundaries
Freeze Record            → confirms one team spec ready for build attempt
Agentic Build Harness    → runs TELUS attempt, emits build attempt record
Reviewer / Witness       → records what happened, no authority claims
Canoe Landing            → public surface for what was witnessed
```

Other concrete gateway facts:

- **Three-dropdown interface**: *specs* / *models* (TELUS Qwen / Gemma /
  gpt-oss, Opus, GPT-5.5) / *harnesses* (Claude Code, Codex, Hermes, Pi —
  Hermes preferred because it cleanly swaps in TELUS models as backend).
- **Token-based access**: team-key redeem at `/jam/redeem` → `/jam` →
  `/api/jam/*`. Consent gate (agreement + retention / follow-up choices)
  renders before token redemption.
- **Telemetry**: Grafana + TELUS metrics API (Qwen exposes it) live for
  token-usage tracking — useful for Jam + impact/emissions accounting.
- **Codex agent team building it**: PO/PM + feature-dev + deployment, with
  a 4th writing-dedicated agent being added.
- **For Jam-week itself**: the gateway runs in **access / chat only**
  mode. Spec submission goes through the fallback surface (Notion / shared
  doc / operator file), per the Jam-day plan.

Shawn has already named multi-agent coordination as a direction —
> "AI agents act as both coding agents and coordination agents — helping
> teams form coherent specs and surfacing cross-team themes, tensions, and
> dependencies."

— and has named a *universal, subjective prioritization function*
`priority(agent, object) → score` over knowledge objects in the KOI network
as a long-running interest. The agent-coordination membrane this design
describes is one path that interest can grow along.

### 6b. Where the agent-coordination layer slots in

| Route | Where it runs | What's possible today | What it needs |
|---|---|---|---|
| **Additive on the gateway, post-Jam** | Gateway frontend + per-team scratchpad | Settings UI; inline prompts at lift / share / surface moments; per-cross-team override rules | Per-participant agent context store; per-team scratchpad surface |
| **Gateway-side roadmap** | Gateway backend | Agent-to-agent messaging routed through gateway with full audit trail (a natural KOI use case if mediated through KOI-resolved knowledge objects); token scoping per team; metrics visibility into cross-team flows | The open questions in §8 |
| **Local Claude + bundle (standalone)** | Participant's laptop | Per-person agent loads bundle + [`specs/coordination-protocol-v0.md`](../specs/coordination-protocol-v0.md); team and cross-team coordination simulated via shared markdown + manual paste | Nothing new; works today with any agent that can read the bundle |

For the 2026-05-25 Jam: the gateway is access/chat only, so the
agent-coordination layer described here is **not live for Jam-week**. The
standalone route is the resilient floor; the hybrid + gateway routes
describe the trajectory after Jam. None of them touches the build-attempt
lane.

## 7. Failure modes to avoid

- **Consent fatigue.** If every micro-action triggers a prompt, participants
  habituate to "yes." Mitigation: defaults that default to *refuse* on
  cross-membrane operations; settings absorb the routine cases; prompts fire
  only when defaults don't cover.
- **Default-to-share creep.** The hardest drift. Each Jam, defaults are
  re-confirmed; no implicit carry-over between events.
- **Agent-as-authority.** An agent that "declares" composition compatibility
  is doing what only mentors and stewards may do. Mitigation: agent output
  is always framed as *observation* or *option*, never *judgment*. Mirrors
  Prompt 2's "you are NOT a gate."
- **Performative sharing without substance.** Teams check the share box
  because composition feels good; nothing real flows. Mitigation: the
  composition-handoff-receipt ([template](../templates/composition-handoff-receipt.md))
  requires a concrete "new use intent" — vague intents fail the receipt.
- **Central coordinator pattern.** A mediator agent that becomes the bus
  through which all teams talk. Mitigation: mediators are *short-lived*
  (per composition, per Tuesday morning sprint), and visible to all teams
  they touch. No persistent mediator across Jam events.

## 8. Open questions for Shawn (gateway)

Given the gateway baseline in §6a, the questions narrow:

1. **Per-team or per-person agent context?** Token redemption appears to
   land at the *team* level. The hybrid recommendation needs per-person
   agent context within a team — does the gateway already model
   participants individually inside a team record, or only as team-members
   under a single team token?
2. **Token scoping for cross-team messaging.** Can the existing token
   scheme (`/api/jam/*`) be extended with per-cross-team allow-lists, or
   does cross-team messaging need a separate scope?
3. **Agent-to-agent channel.** Once submission flow goes live post-Jam,
   does the gateway plan to route agent traffic, or should agent-to-agent
   messaging run beside the gateway (with the gateway as identity + token
   authority only)?
4. **KOI as substrate.** Given the `priority(agent, object)` interest, do
   cross-team message payloads resolve to KOI knowledge-object IDs (so
   the same offering can be referenced by both teams' agents without
   duplicating content), or stay file-local for now?
5. **Metrics visibility into cross-team flows.** The Grafana + TELUS
   metrics path covers token usage. Could it extend to surface
   `share_request` / `share_refuse` / `withdraw_notice` counts to
   facilitators? Refusals are data; mentors need to see them.
6. **Withdrawal propagation at gateway layer.** Today
   [`tools/withdrawal-propagation.py`](../tools/withdrawal-propagation.py) is
   manual + manifest-driven. Could the gateway maintain the manifest
   automatically (manifest as a side-effect of every accepted
   `share_grant`) so withdrawal surfaces the propagation set without
   manual curation?
7. **Harness integration.** Where the three-dropdown picker lets a team
   pick a harness (Claude Code / Codex / Hermes / Pi), is the coordination
   layer a harness-independent service, or does each harness wrap the
   protocol differently?

## 9. Boundary footer

This is a design exploration produced 2026-05-25 in conversation with the
kit. It is **not** approval, certification, authority, or reuse permission
for any specific implementation. The agent layer it describes does not yet
exist in the kit beyond the three sample prompts. Treat as a working
articulation; iterate. v0.
