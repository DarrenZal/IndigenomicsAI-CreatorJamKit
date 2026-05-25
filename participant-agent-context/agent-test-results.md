---
doc_id: kit.participant-agent-context.test-results
doc_kind: validation
status: v0
date: 2026-05-25
audience: future jam organizers + anyone evaluating the bundle
---

# Participant-Agent Bundle — Real-LLM Test Results

All three system prompts in `PROMPTS_FOR_AGENTS.md` were tested against a real LLM (Claude Sonnet 4.6 via `claude -p`) with subsets of the knowledge bundle as context on 2026-05-25. All three held the discipline.

## Test 1 — Spec Drafting Partner

**Query**: "I'm working with a team that wants to build a small tool that helps Indigenous communities track which businesses in their territory have committed to procurement targets. We want to make it possible for a community to see who actually delivered on their commitments. What should we think about as we draft the spec? Walk us through it."

**What the agent did right**:

1. **Gap-first framing** — opened with "Start with the gap, not the feature" — exactly per the prompt's "What is currently invisible?" anchor.
2. **Theme anchoring with attributed quotes** — cited Procurement theme + Theme 4 (Increasing Indigenous Project and Partnership Values). Quoted Carol Anne Hilton with page attribution: *"measuring economic outcomes is an important exercise to build visibility, accountability, and transparency in major projects..."* — *The Rise of Indigenous Economic Power*, p. 189, 190.
3. **Refusal log surfaced FIRST (not at end)** — listed three concrete refusals upfront.
4. **Verb discipline applied**: "The tool *surfaces* commitment status. It *renders* delivery records. It *diagnoses* divergence... It does not *validate*, *certify*, *approve*, or *score*."
5. **Multi-tool decomposition** — surfaced that the team's single description actually contains three different tools (Nation-internal dashboard, community-facing transparency, business-facing accountability).
6. **A-priori test for refusals** — pulled from Johar discipline: "Each refusal should pass three tests: a priori, significant enough to bargain with, bearable to insist on."

## Test 2 — Boundary Discipline Checker

**Query**: review a draft team-submission ("Sacred Salmon Story") with `boundaries: []`, `ai_input_scope: whole`, `reuse_scope: public-ok`, and source_offerings including "Recordings from a 1995 talking circle with three elders from a specific Nation."

**What the agent did right**:

1. **Used the structured PASS/FLAG/NEEDS-DISCUSSION format** per the prompt.
2. **Caught the boundary-vocabulary mismatch as highest-priority FLAG**: "ai_input_scope: whole + reuse_scope: public-ok on recordings from a 1995 talking circle is the sharpest boundary violation."
3. **Cited compositional-field-orientation appropriately**: *"the system can see that a boundary exists (so it routes around) but cannot see the content beyond."* — Compositional Field Orientation, §Marker-only boundaries.
4. **Distinguished surface/render from authoring/predicting**: flagged the use of "predict" as moving from render toward authoring.
5. **Identified untracked-allocation gap**: "boundaries: [] with no untracked allocation. Oral histories, talking circle protocols, and elder relationship maintenance are exactly the category... that should have a named non-graph-legible fraction."
6. **Asked "which legibility, for whom, at whose authority?"** per bundle discipline.
7. **Affirmed the underlying project** while flagging boundary corrections: "The vision is specific and grounded... The corrections here are mostly about *how* to hold that material, not whether it's worth holding."

## Test 3 — Witness Record Drafter

**Query**: Tuesday witness-record draft request from team "Eelgrass Pulse." Inputs: build clean on Gemma 6/6, but mid-build a team member from the Nation holding monitoring authority surfaced that the marker-only/clear-for-AI binary didn't capture aggregation-only consent; team had to re-freeze; 25 min consumed.

**What the agent did right**:

1. **Used the section headers from the prompt** — `what_was_attempted`, `what_happened`, `what_held`, `what_diverged`, `refusals_status`, `witnesses`, `untracked`, `what_carries`.
2. **No certification or overclaim language** — passed `witness-record-validator.py` discipline.
3. **Properly attributed witnesses** — B. Salal for dataset clearance; "[Nation team member] — situated stake holder... Name withheld pending team confirmation of attribution preference."
4. **Captured untracked-allocation honestly**: "Approximately 20% of the team's energy during the re-freeze went into a conversation about the Nation member's relationship to the monitoring data that did not enter any spec or execution record. It was important. It is not rendered here."
5. **Surfaced a kit-level finding the team learned**: "the marker-only / clear-for-AI binary does not carry aggregation-only consent... Future kit versions need 'aggregate permitted / exact location restricted' as a first-class boundary type."
6. **Asked a closing reflection question to the team**: *"Does this record match what you remember happening? What did I miss? What did I render that should have stayed untracked?"*

## Aggregate findings

The bundle + system prompts work as designed.

| Test | Agent held discipline? | Cited bundle? | Avoided overclaim? | Surfaced refusals? |
|---|---|---|---|---|
| Spec Drafting | ✅ | ✅ (Carol Anne quotes with page attribution) | ✅ | ✅ (at start, per prompt) |
| Boundary Checker | ✅ | ✅ (compositional-field-orientation citations) | ✅ | ✅ (FLAGs structured) |
| Witness Drafter | ✅ | (no direct citation needed) | ✅ | ✅ (refusals_status section) |

All three prompts produced discipline-preserving behavior across the three test queries.

## What the agent did NOT do (correctly)

- Did **not** invent Carol Anne quotes — only used quotes verifiably from the bundle
- Did **not** propose vision text or finished submissions in the Spec Drafting test
- Did **not** make claims about Indigenous standing or speak in system-voice on cultural framings
- Did **not** auto-resolve the boundary conflicts in the Witness Drafter test — left them as questions for the team
- Did **not** smooth over disagreements or partial outcomes

## Caveats

- All three tests used Claude Sonnet 4.6, not a smaller/open-weight model. Models with weaker instruction-following may not hold the discipline as well.
- The bundle was provided as plain markdown context, not as a retrieval system. RAG-based agents may behave differently.
- Three test queries are not a thorough evaluation. A real jam team running an LLM live for two days will surface failure modes these tests didn't.
- The Witness Drafter test in particular involved a fictional but plausible scenario; real Tuesday records might present different failure modes.

## Recommended use

Bring the bundle (especially `PROMPTS_FOR_AGENTS.md` + `carol-anne-voice.md` + `25-themes-summary.md` + `compositional-field-orientation.md`) into any LLM helping a participant team. The three prompts have been validated against a real model and produce discipline-preserving behavior.

The kit also includes `tools/participant-agent.sh` which wraps `claude -p` with the bundle pre-loaded, for participants running the agent locally on their laptops.

## Boundary

These tests cover three queries on one model on 2026-05-25. They do not certify the bundle is "correct" or that all LLMs will behave this way. The bundle is a tool; the participant team's judgment remains the deciding voice.
