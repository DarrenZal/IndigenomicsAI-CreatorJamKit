---
doc_id: kit.participant-agent-context.readme
doc_kind: orientation
status: v0
date: 2026-05-25
audience: participants + their LLM agents
---

# Participant Agent Knowledge Bundle

A focused context bundle for the IndigenomicsAI Creator Jam (2026-05-25 / 2026-05-26). It is meant to be loaded by any LLM that is helping a participant team draft a `team-submission-v0`, review a draft for boundary discipline, or compose a Tuesday witness record.

## What this is

A small, self-contained snapshot of:

- Carol Anne Hilton's direct voice (quoted from her two books with attribution).
- The 25-theme Indigenomics ontology that frames "where value creation is happening."
- A plain-language primer on Will Ruddick's commitment-pool primitive (CVLE × RVLFHG × the commitment tuple) and how it maps to the Jam's work.
- A plain-language summary of Indy Johar's metacognition / shifting-cost-of-strategy work and what it says about the Jam's discipline.
- A plain-language orientation to the broader compositional-field architecture the Jam sits inside.
- A JSON-LD bundle that ingests in one shot for retrieval-augmented agents.
- Sample agent system prompts that explicitly reference this bundle.

## Who it is for

- **Participants** drafting team submissions and reviewing their own work.
- **Mentors and floaters** helping teams stay close to Carol Anne's voice and the Jam's boundary discipline.
- **LLM agents** (Shawn's gateway agent, but also any model a team brings in for help — Claude, Gemma on TELUS, Qwen, ChatGPT, local models, etc.).

## How to use

1. **For a chat agent.** Load `knowledge-bundle.jsonld` once at the start of the session. Use one of the prompts in `PROMPTS_FOR_AGENTS.md` as the system prompt. The agent will be able to answer "what does Carol Anne say about land?" with attributed quotes, and to flag drafts that drift into territory the Jam refuses.
2. **For a participant reading by hand.** Start at `carol-anne-voice.md` — it is the most important document in the bundle. Then read `25-themes-summary.md` to see which themes your team's idea touches. Skim `compositional-field-orientation.md` for the broader architecture; `ruddick-cpp-primer.md` and `johar-discipline.md` are supporting context.
3. **For a mentor reviewing a draft.** Use the "Boundary discipline checker" prompt in `PROMPTS_FOR_AGENTS.md` plus the bundle. The agent will surface places where a draft puts words in Carol Anne's mouth, claims authority it does not hold, or asks the system to do something it should not.

## What NOT to use it for

- **Do not use this bundle to invent new Carol Anne quotes.** If something is not in `carol-anne-voice.md` or the worldview JSONs, it is not in her voice. Agents should refuse to fabricate.
- **Do not use this bundle to make Indigenous cultural claims.** Only the worldview content already extracted by Carol Anne and her team into the published books is included here. Anything beyond that requires Indigenous-led authorization that does not happen at the Jam.
- **Do not treat this bundle as authority for downstream decisions.** It supports drafting; it does not certify, approve, or license. Final calls on Indigenous content, language, and direction sit with Carol Anne and the Indigenomics Institute, not with an agent or a participant draft.
- **Do not assume the bundle is complete.** It is a v0 snapshot. The compositional-field synthesis is mid-evolution; the ontology is v1.0 with a v1.1 extension proposed; Ruddick's paper is being read through. Treat omissions as omissions, not as exclusions.

## Files

| File | What it holds |
|------|---------------|
| `README.md` | This document |
| `carol-anne-voice.md` | ~60 direct attributed quotes from Carol Anne Hilton's two books, grouped by theme |
| `25-themes-summary.md` | The 25 ontology themes with definitions, anchoring quotes, and sample spec ideas |
| `ruddick-cpp-primer.md` | Plain-language primer on Will Ruddick's commitment-pool primitive |
| `johar-discipline.md` | Plain-language summary of Indy Johar's four-position frame and what it asks of the Jam |
| `compositional-field-orientation.md` | Plain-language orientation to the broader compositional-field architecture |
| `knowledge-bundle.jsonld` | Structured JSON-LD bundle — load once, query inline |
| `PROMPTS_FOR_AGENTS.md` | Three sample system prompts (spec drafting / boundary check / witness record) |

## Sources

- `book1-worldview.json` and `book2-worldview.json` in the IndigenomicsAI repo at `v2/packages/knowledge/data/` — extracted from Carol Anne Hilton's *Indigenomics: Taking a Seat at the Economic Table* (2021) and *The Rise of Indigenous Economic Power* (2024).
- `indigenomics-ontology-v1.json` — the 25-theme ontology extracted from Book 2, Chapter 8.
- `docs/methodology/ruddick-commitment-pool-bridge.md` in the IndigenomicsAI repo — Darren Zal's bridge from Ruddick's formalism to the Indigenomics work.
- `docs/specs/jam-witness-ceremony-v0-johar-enhancements.md` and `docs/synthesis/johar-shifting-cost-of-strategy-connection.md` in the IndigenomicsAI repo — Johar discipline synthesis.
- `docs/research/synthesis/compositional-field-architecture.md` in the Spore repo — the cross-project architectural recognition.

## Boundary

This is a public-facing artifact. Salish-Sea-ecological framings (kelp, herring, eelgrass, salmon, eelgrass meadows, etc.) are public-safe and may be used freely. Indigenous-cultural content is included **only** as Carol Anne and her team have already published it in the books. No new synthetic framings of her voice are introduced; no Indigenous-cultural content beyond the books is added. If a team needs cultural framing beyond what is here, that is a question for Carol Anne, not for the bundle or an agent reading it.
