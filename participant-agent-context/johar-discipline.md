---
doc_id: kit.participant-agent-context.johar-discipline
doc_kind: primer
status: v0
date: 2026-05-25
audience: participants + their LLM agents
---

# Johar's Discipline — Plain-Language Summary

## Who is Indy Johar and why does it matter at the Jam?

Indy Johar is a designer and architect who writes about the conditions for legitimate strategy at planetary scale. His May 2026 essay *The Shifting Cost of Strategy* names a failure mode that the Jam was already designed to prevent but had not yet named: **strategic epistemic inflation** — an abundance of coherent, compelling, plausible AI-generated strategies that reproduce inherited categories rather than discover emergent ones.

Translated for the Jam: machine intelligence is now extremely good at producing fluent strategic conjecture (specs, plans, theories of change, summaries). It is not good at producing collective comprehension, situated ground truth, or trustworthy data. If we mistake one for the other, we get accelerated delusion. Johar's discipline is what keeps the Jam honest under exactly that pressure.

## The four-position frame

Johar names four positions that any serious strategic work has to hold in tension:

1. **Conjecture** — fluent, cheap, abundant, dangerous if mistaken for grounded understanding. This is what the AI agents in the Jam will produce when we let them rip.
2. **Comprehension** — scarce, slow, legitimacy-conferring. Comprehension is **part of the production of strategy**, not a communications layer added afterwards. A strategy that cannot be collectively understood cannot become power.
3. **Ground truth** — situated, lived, often held at the edge of legibility. Frequently held by *those least formally authorised to define strategy but most exposed to whether it is true*. In the Jam: Carol Anne on overall ceremony shape; survey respondents on instrument fitness; specific contributors on the parts of the spec they authored; the bioregion itself on what its conditions actually are.
4. **Data** — relevant, manipulable, gameable, must be cross-correlated with ground truth.

Johar's strongest claim: *"Great strategic organising is the capacity to hold conjecture, comprehension, ground truth, and data in productive tension as a single living system — not to privilege any one position."*

## Five process moves the Jam takes from this

The Jam architecture (see `docs/specs/jam-witness-ceremony-v0.md` and `docs/specs/jam-design-principles-v0.md` in the IndigenomicsAI repo) implements five concrete moves drawn from Johar's discipline:

### 1. Capture comprehension state upstream, not just downstream

Every contribution carries not only **content** but three additional fields: **intent** (what the contributor was trying to make possible), **partial understanding** (what they don't yet fully understand), and **refusals** (what they would not want their contribution used to authorise). This makes the comprehension visible at the moment it is produced, so the composition step has material to preserve.

### 2. Compose with a divergence ledger as first-class output

When N contributors say slightly different things, the default move is to summarise toward coherence — which throws away the most strategically valuable signal in the room. Instead, composition produces **two** artefacts: the composed spec (what goes to execution) AND a **divergence ledger** that names what did not merge, what partially overlaps, and what contradicts. The divergence is the signal, not noise.

### 3. Comprehension checkpoint between composition and execution

After composition is done, before execution starts, there is a facilitated round where contributors re-encounter the composed spec and signal one of three: *still recognise / no longer recognise / actively object*. "No longer recognise" gets a brief moment to articulate what got lost. The checkpoint has three possible outcomes: proceed, brief-repair, or pause-and-re-author. This catches naive composition damage before it becomes execution damage.

### 4. Route witnessing by situated stake, not by uniform crowd

Different parts of a spec have different ground-truth holders. A floater mentor does not have ground truth about a specific contributor's intent; the contributor does. Carol Anne does not have ground truth about every team's domain; the team does. The witnessing-receipt schema includes a `witness_routing` field family that names who holds ground truth for each section, so the witnessing phase gives them first voice on the parts they hold.

### 5. Pace AI execution to human witness cadence

The sovereign-stack agents can execute faster than humans can witness. Optimising for raw throughput is the wrong call. The Jam orchestrator caps agent execution at a witnessing-tick (typically 1–5 minutes per unit), and the facilitator can adjust live based on observed absorption. Carol Anne's framing: *"the rigour is witnessing."* If witnessing cannot keep up, the execution slows down.

## The refusal-log reframe

The handoff packet has always included a **refusal log** — what the team collectively cannot permit the agents to do. The discipline question is whether the log is facilitated as **veto-collection at the end** ("OK, what should the agents not do?") or as **comprehension-building from the start** ("Before we begin, what is the smallest thing we can collectively articulate that we cannot permit?").

Johar's frame says: the refusal log is the externalised form of collective comprehension as constraint on conjecture. It is the most concentrated comprehension artefact the Jam produces. Facilitating it from the start makes it Principle 1 made operational. Leaving it to the end makes it residual gatekeeping. Choose the start.

## Lifecycle bracketing — Spehr upstream, compost discipline downstream

A more recent enhancement, drawn from the P2P / Free Cooperation tradition: every record produced at the Jam is bracketed from both ends.

**Upstream (Spehr's three qualifiers):** a refusal only counts if it passes three tests — is it **a priori** (not retrofitted to a later position), **significant enough to bargain with** (not decorative), and **bearable** (the holder can live with insisting on it)? Refusals that fail these tests are recorded as opinions, not as refusals.

**Downstream (compost discipline):** every record has a compost path. At session-close, contributors lead an explicit compost moment per record they produced. Four lifecycle states: *withdrawn / composted / retained-as-boundary-marker / transformed-to-teaching*. Without catabolic primitives, the Jam's epistemic-hygiene moves quietly become a reputation system. Compost is anti-reputation infrastructure.

## What this asks of your team and your agent

- **Do not let your agent smooth contradictions away.** If two teammates disagree, the agent should surface the disagreement, not LLM it into apparent consensus.
- **Do not let your agent claim authority it does not hold.** It can draft; it cannot certify. The witness is human. The ground truth is held by the person who is exposed to it.
- **Do not let your agent pace you.** You pace the agent. If you cannot keep up with what it is producing, slow it down.
- **Hold the four positions.** Conjecture, comprehension, ground truth, data — all four, in tension, all the time. If you find your team has collapsed onto one (usually conjecture, because that is what AI is fastest at), name it and rebalance.
