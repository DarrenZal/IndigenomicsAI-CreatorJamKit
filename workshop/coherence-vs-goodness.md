---
doc_kind: workshop-analysis
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Coherence Vs Goodness

This note separates three questions that are easy to collapse:

1. Can these records compose?
2. Does the composed whole remain coherent?
3. Is this composition good, healthy, desirable, or worth doing?

The Creator Jam kit currently handles the first two better than the third. This note names the gap.

## Three Checks

| Check | Question | Good Use | Who Or What Can Help | Boundary |
| --- | --- | --- | --- | --- |
| Composability | Can the records, fields, purposes, permissions, and transitions fit? | Candidate bundle discovery, interface testing, blocked/non-composable receipts. | Schemas, hard constraints, LLM relation suggestions, reviewers. | Technical fit does not create consent or authority. |
| Coherence | Does the composed whole preserve meaning, evidence, authority, time, and boundaries? | Coherence vector, speech-act transition review, obstruction markers. | LLM critique, reviewer checklists, provenance graph, time-aware checks. | Coherence is necessary but not sufficient for goodness. |
| Desirability / health | Is this a good next move under the values, relationships, and time horizons that matter? | Deliberation, adjacent-possible exploration, value-lens review, future consequence mapping. | Human reviewers, affected people, stewards, AI as deliberation support. | AI can surface possibilities and tradeoffs; it does not authorize value judgments. |

All three need to hold before a composition becomes a good next move.

## Combination Table

| Composable | Coherent | Desirable / Healthy | Reading |
| --- | --- | --- | --- |
| yes | yes | yes | Good candidate to proceed, subject to authority and review. |
| yes | yes | no | We could do this, and it would hold together, but we should not. |
| yes | no | yes | The parts fit, and the aim may be good, but the whole loses meaning or boundary discipline. |
| yes | no | no | Seductive trap: technically possible, incoherent, and not worth doing. |
| no | any | any | Record the obstruction. Non-composability can be a valid discovery. |

This table should appear before any score, rank, or recommendation.

## Why Coherence Is Not Goodness

Coherence is a diagnostic. It asks whether the parts hold together without contradiction, evidence drift, authority drift, time drift, or boundary collapse.

Goodness and health ask a different kind of question:

- good for whom?
- over what time horizon?
- under which value frame?
- with whose authority?
- at what cost to refusal, dignity, privacy, care, or future optionality?
- what does this make possible next?
- what does it foreclose?

A harmful system can be coherent. An extractive funding machine can be internally consistent. A public story can be polished and coherent while violating consent. Therefore coherence must support deliberation, not replace it.

## Desirability Is Also A Vector

The kit should not collapse desirability into one number. At minimum, deliberation may ask:

| Dimension | Question |
| --- | --- |
| Participant dignity | Does this preserve the contributor's agency, refusal, and context? |
| Relational health | Does this strengthen relationships or create surveillance, pressure, or extraction? |
| Bioregional grounding | Does this attend to place, material reality, and ecological constraints? |
| Future optionality | Does this widen or narrow legitimate future paths? |
| Repair capacity | If harm, error, withdrawal, or conflict appears, can the system repair? |
| Generativity | Does this open adjacent possible work without forcing premature closure? |
| Beauty / elegance | Does the composition feel clear, fitting, alive, or ceremonially appropriate for the context? |

These dimensions are prompts for human deliberation. They are not automatic verdicts.

## AI's Bounded Role

AI can help humans deliberate. It should not decide what is good.

| AI Role | Useful For | Not For |
| --- | --- | --- |
| Surface tradeoffs | Naming what is gained, lost, or made fragile. | Deciding the tradeoff is acceptable. |
| Identify missing perspectives | Asking who is not represented. | Speaking for absent people. |
| Generate alternatives | Mapping adjacent possible options. | Choosing the destination. |
| Stress-test values | Comparing a proposal against stated values. | Defining the values. |
| Map time horizons | Looking at near-term, seasonal, annual, and long-horizon consequences. | Authorizing on behalf of future people. |
| Speak through lenses | Showing how a composition appears from different frames. | Declaring the correct lens. |
| Expose hidden assumptions | Naming what the proposal treats as obvious. | Validating those assumptions. |

The pattern is:

```text
AI proposes possibilities and tradeoffs
  -> humans deliberate with standing
  -> AI helps compare revised options
  -> humans authorize, refuse, narrow, or defer
  -> receipt records what happened
```

## Deliberation-Support Artifacts

The kit has templates for composition checks, transition checks, display review, and receipts. It also needs artifacts that support deciding whether a coherent composition is worth doing.

Candidate artifacts:

| Artifact | Purpose |
| --- | --- |
| `templates/trade-off-surface.md` | Names what the composition gains, loses, and makes fragile. |
| `value-lens-view` | Shows the same composition through Indigenomics, commons, gift-economy, bioregional, legal, technical, and participant lenses. |
| `adjacent-possible-map` | Lists near options that become possible if this proceeds. |
| `adjacent-impossible-map` | Lists options that may be foreclosed if this proceeds. |
| `stakeholder-reflection-prompts` | Asks who is affected, missing, overburdened, or under-authorized. |
| `future-horizon-review` | Looks at immediate, jam-scale, seasonal, annual, and long-horizon effects. |
| `repair-and-withdrawal-readiness` | Checks whether the composition can repair, narrow, or unwind later. |

These are not substitutes for review. They help reviewers and participants see the field.

## Working Rule

For now, a Creator Jam composition should not be called a good next move unless:

- it is technically composable or has a clear adapter
- it remains coherent under the current coherence vector
- hard constraints are satisfied
- the right authority is present
- refusal and withdrawal paths are explicit
- a desirability / health deliberation has named what the composition serves, what it risks, and what it forecloses

The last point is the gap that `templates/trade-off-surface.md` starts to address. Future iterations should add more deliberation-support artifacts only when concrete fixtures show the need.
