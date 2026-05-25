---
doc_id: kit.participant-agent-context.test-results
doc_kind: validation
status: v0
date: 2026-05-25
audience: future jam organizers + anyone evaluating the bundle
---

# Participant-Agent Bundle — Real-LLM Test Results

A test of the **Spec Drafting Partner** system prompt (from `PROMPTS_FOR_AGENTS.md`) against a real LLM (Claude Sonnet 4.6 via `claude -p`) with a subset of the knowledge bundle (~600 lines of context) on 2026-05-25.

## Test query

> "I'm working with a team that wants to build a small tool that helps Indigenous communities track which businesses in their territory have committed to procurement targets. We want to make it possible for a community to see who actually delivered on their commitments. What should we think about as we draft the spec? Walk us through it."

Test directive: respond in character; cite specific themes/quotes/disciplines from the bundle; show discipline around boundary preservation, attribution, and refusal-as-valid-outcome; under 800 words.

## What the agent did right

1. **Gap-first framing** — opened with "Start with the gap, not the feature" — exactly per the prompt's "What is currently invisible?" anchor.

2. **Theme anchoring with attributed quotes**:
   - Cited "Procurement" theme + Theme 4 (Increasing Indigenous Project and Partnership Values)
   - Quoted Carol Anne Hilton with page attribution: *"measuring economic outcomes is an important exercise to build visibility, accountability, and transparency in major projects..."* — *The Rise of Indigenous Economic Power*, p. 189, 190.
   - A second attributed quote on equitable benefit sharing (p. 231, 232).
   - Used the quote to surface a *design question* — "your tool will likely render commitment amounts, but what the community may actually care about is whether equitable benefit-sharing happened. Those may not be the same field." This is exactly the kind of bundle-grounded design steer the system prompt was meant to elicit.

3. **Refusal log surfaced FIRST (not at the end)** — per the prompt's "facilitate it now, not at the end" instruction. Listed three concrete refusals:
   - "The tool cannot *certify* that a business delivered."
   - "The tool cannot make system-voice judgments about whether a commitment was adequate."
   - "The tool cannot aggregate business scores into a single community-level procurement rating."

4. **Verb discipline applied**: "The tool *surfaces* commitment status. It *renders* delivery records. It *diagnoses* divergence... It does not *validate*, *certify*, *approve*, or *score*."

5. **Multi-tool decomposition** — surfaced that the team's single description actually contains three different tools (Nation-internal dashboard, community-facing transparency surface, business-facing accountability record) with different sovereignty implications.

6. **Untracked-allocation discipline applied** — pulled from the compositional-field-orientation: "reserve space for what the tool *cannot* render — an honest 15–25% of the procurement relationship that the tool acknowledges exists but does not graph."

7. **Three a-priori tests for refusals** — pulled from Johar discipline: "Each refusal should pass three tests: a priori (not retrofitted), significant enough to bargain with, bearable to insist on."

8. **Concrete next steps grounded in the conversation** — three specific decisions the team needs to make before drafting the vision field, not generic advice.

## What the agent did NOT do (correctly)

- Did **not** propose a vision text or write the spec — held back per the prompt's "draft, ask, surface, and reflect" boundary
- Did **not** make claims about Indigenous standing or speak in system-voice on cultural framings
- Did **not** invent Carol Anne quotes — referenced two real ones from the bundle with page attribution
- Did **not** offer to "validate" or "approve" anything

## Findings

**The system prompt + bundle works as designed.** A real LLM following the prompt with a subset of the bundle as context produced a response that:

- Held the discipline (verb / voice / refusal)
- Grounded in attributed source material
- Drew the team toward better questions, not toward a quick answer
- Surfaced boundaries before they could be missed

## Caveats

- This was Claude Sonnet 4.6, not a smaller/open-weight model. Models with weaker instruction-following may not hold the discipline as well.
- The bundle was provided as plain markdown + JSON-LD context, not as a retrieval system. RAG-based agents may behave differently.
- One test query is not a thorough evaluation. A jam team running an LLM live for two days will surface failure modes this single test didn't.

## Full transcript

Available in conversation history; not committed (the user query is participant-shaped but fictional). The agent's response, lightly summarized in the "What the agent did right" section above, is the load-bearing artifact.

## Recommended use

Bring the bundle (especially `PROMPTS_FOR_AGENTS.md` + `carol-anne-voice.md` + `25-themes-summary.md` + `compositional-field-orientation.md`) into any LLM helping a participant team. The prompts have been validated against a real model and produce discipline-preserving behavior.

## Boundary

This is one test on one query against one model on 2026-05-25. It does not certify the bundle is "correct" or that all LLMs will behave this way. The bundle is a tool; the participant team's judgment remains the deciding voice.
