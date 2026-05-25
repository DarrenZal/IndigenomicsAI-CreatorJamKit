---
doc_id: indigenomics.jam.morning-additions-mentor-brief
doc_kind: mentor-brief
status: v0
date: 2026-05-25
audience: jam mentors arriving today
---

# What's new in the kit since Friday — mentor brief

The Mentor Field Guide ([`docs/MENTOR_FIELD_GUIDE.md`](MENTOR_FIELD_GUIDE.md)) is the main reference. This brief covers **what was added Saturday–Sunday–Monday morning** that mentors should know about.

## TL;DR (60 seconds)

1. **Environmental impact** is now a buildable thread — two specs ready, Justin Yang (TELUS) can mentor.
2. **Cross-team coordination** has tooling now — stigmergic offering board, sprint guide, handoff receipts, mentor decision card.
3. **Multi-agent coordination** has a design + protocol + worked example — for teams curious how their LLM helpers can collaborate within and across teams.

If a team asks "what's the menu?", point them at [`specs/README.md`](../specs/README.md). The three additions below are sub-menus inside that.

---

## 1. Environmental impact accounting (energy / TELUS / Justin Yang)

**For**: any team curious about energy use, carbon ledgering, or the relationship between compute and accountability.

**Two specs ready** (both TELUS-preflighted):

- [`specs/preflights/energy-receipt/`](../specs/preflights/energy-receipt/) — per-team CLI. Reads a log of compute events (intention + model + tokens + estimated kWh + outcome) and produces a markdown receipt with a Carol-Anne-framed reflection block. Mentor brief for Justin: [`justin-mentor-brief.md`](../specs/preflights/energy-receipt/justin-mentor-brief.md) (5 day-of questions).
- [`specs/preflights/compute-covenant/`](../specs/preflights/compute-covenant/) — cross-team rollup CLI. Reads multiple team energy-receipts and produces a jam-wide energy picture with a covenant statement. No scoring. Just witnessing.

**Framing**: "compute as ceremony" — runs carry intention, care-taking, and reciprocity. Not a carbon-offset commodity. The TELUS Rimouski H200 runs on Quebec hydro (~99% renewable) — that's *evidence of a sovereignty-first choice*, not permission to be wasteful.

**Who to involve**: Justin Yang (TELUS) is on-site and is the natural mentor. The first energy-receipt folder includes 5 day-of questions you can use to open conversation with him (metrics API coverage, water-impact data, per-event granularity, embodied carbon, Scope 1/2/3 alignment).

---

## 2. Cross-team coordination

**For**: the Tuesday morning composition sprint + any teams that realize mid-Monday their work overlaps with another team's.

**Four new artifacts** (all linked from MFG §11):

- [`templates/stigmergic-offering-board.md`](../templates/stigmergic-offering-board.md) — sticky-card schema for teams to post live "we're making X, who needs it?" cards. Gallery-walk pacing built in. Default is **share-only-if-the-team-chose-to**.
- [`workshop/tuesday-composition-sprint-v0.md`](../workshop/tuesday-composition-sprint-v0.md) — 90-minute facilitator playbook for Tuesday morning. 6 phases including a Johar comprehension checkpoint ("still recognize what I brought / no longer / object"). **"Doesn't fit yet" is a success outcome**, not a failure.
- [`templates/composition-handoff-receipt.md`](../templates/composition-handoff-receipt.md) — when Team A's output becomes Team B's input. Source team's permissions travel; handoff is preservation, not new consent.
- [`workshop/mentor-composition-decision-card.md`](../workshop/mentor-composition-decision-card.md) — 90-second mentor flowchart for "can these two offerings compose?" with concrete next-action per NO branch.

**Plus**: [`tools/composition-merger.py`](../tools/composition-merger.py) does the mechanical merge with conflicts surfaced. Run it live with paired teams during the Tuesday sprint.

**Mentor rule of thumb**: the sprint is OPTIONAL. Teams that don't want to compose don't have to. Composition that's forced loses the relational signal.

---

## 3. Multi-agent coordination (how agents help within and across teams)

**For**: teams using LLMs to draft their specs who want their agent to also handle in-team coordination and cross-team sharing.

**The design + protocol** (for anyone going deep):

- [`docs/multi-agent-coordination-design.md`](multi-agent-coordination-design.md) — 4 architectural routes, 3 membrane operations (person→team / team→team / agent→witness), UX layers (settings + inline prompts), composes onto Shawn's existing gateway. Has open questions for Shawn at the end.
- [`specs/coordination-protocol-v0.md`](../specs/coordination-protocol-v0.md) — 7 message types (share_request / share_grant / share_refuse / withdraw_notice / boundary_marker / composition_propose / witness_observe). For teams building agent-to-agent tools.

**The discipline** (for any LLM helping a team):

- [`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../participant-agent-context/PROMPTS_FOR_AGENTS.md) **Prompt 4 (Collaboration Facilitator)** — system prompt that establishes the three-membrane discipline + asks consent at every share moment. Pair with the rest of the bundle (Carol Anne's voice, 25-themes summary, etc).

**The worked example**:

- [`examples/claude-darren-demo/agent-coordination-transcript.md`](../examples/claude-darren-demo/agent-coordination-transcript.md) — 7-scene screenplay showing two team agents discovering each other through the offering board, hitting consent moments, a real refusal, a mentor moment when a protected boundary surfaces, and a joint witness record at the end.

**Mentor rule of thumb**: agents serve the team. The team's judgment is the deciding voice. Consent is asked at every membrane crossing. Refusal is a complete outcome.

---

## What stayed the same

The kit's discipline is unchanged: boundaries before sharing, consent before disclosure, refusal as a complete offering, "doesn't fit yet" as a success outcome, AI as execution helper not judgment authority. All five boundary types (marker-only / not-for-AI / not-for-reuse / private / protected) and three authorization scopes (display / ai-input / reuse) are preserved.

## Open coordination items (mentors should know)

- **Team-key onboarding email** for the gateway didn't land in everyone's inbox; if teams are stuck on access, route them to Shawn directly via Lets JAM Signal.
- **Yvonne Coady asked Sunday** whether the Space Center planetarium can do 3D flythroughs (she has Unity 3D experience from a Maritime Museum diatoms project). Worth pairing her with Pravin during setup if 3D is in scope.
- **Justin Yang on TELUS metrics API**: Qwen is live; other 4 models still need per-event tracking enabled. He's the contact.

---

## Afternoon additions (Day 1 afternoon)

Three **meta-specs** shipped after the morning push — runnable substrate
that the jam dogfoods itself with. Each is ~20-min walkable for an
arriving mentor:

### 4. `specs/agent-coordination-bus-v0/` — file-based bus implementing the 7 wire types

The 7 wire types from `coordination-protocol-v0.md` are now runnable as
JSON files via `scripts/jam/bus.py`. Per-team append-only logs, per-type
validators, audit invariant. 13-message worked demo with 3 simulated
teams.

### 5. `specs/agentic-spec-drafting-loop-v0/` — 5-stage orchestrator

Takes a loose offering, drafts a spec (Prompt 1), boundary-checks
(Prompt 2), optionally composes (Prompt 4), and freezes to
`agentic-build-packet-v0.json`. Stub mode is offline + deterministic;
gateway mode hits the local indigenomics-ai-gateway smoke stack.

### 6. `specs/witness-record-append-v0/` — public witness wall

Tuesday's canoe-landing publication surface. `--confirm-publish` gate,
overclaim validator wrap, refusal-as-record support. 3 sample records
demonstrating clean / refusal / partial outcomes.

### Tuesday-sprint walkthrough

[`workshop/tuesday-meta-spec-walkthrough.md`](../workshop/tuesday-meta-spec-walkthrough.md)
is a 30-min mentor playbook for introducing teams to these three specs
during Tuesday morning's composition sprint. Each spec has clear
extension paths.

### Bugs caught + fixed at source today

1. `tools/witness-record-validator.py` was rejecting every well-formed
   witness record (multi-line receipt-statement wrap broke the
   disclaimer-context check). Patched. **Without the fix, Tuesday's
   witness wall would have refused every record.**
2. `IndigenomicsAI/scripts/mirror-to-public.sh` (newly written) used
   `--first-parent` which hid second-parent commits. Patched +
   documented.

### Tests

```bash
python3 -m unittest discover -s scripts/jam/tests
```

Expected: 43/43 OK across the 3 meta-specs.

## Boundary

This brief synthesizes additions to the public kit. It does not certify, approve, or authorize anything. Mentors observe, ask, surface — and the team's judgment remains the deciding voice.

🛶
