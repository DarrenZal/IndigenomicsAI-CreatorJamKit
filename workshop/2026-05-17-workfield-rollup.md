---
doc_kind: workshop-rollup
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# 2026-05-17 Workfield Rollup

This rollup closes the Sunday workfield after the Creator Jam kit moved from spec menu into fixture-backed composition, executable diagnostics, deliberation support, and lightweight play.

## What Landed

| Area | Result |
| --- | --- |
| Claims, witness, receipt | A worked composition reference shows evidence -> claim and witness record -> story candidate with display gates, excluded evidence, AI-use receipts, and non-ceremonial witness boundaries. |
| Non-composability | Commitment Pool + Untracked Allocation records a blocked route where deliberate non-legibility stays protected instead of being treated as missing data. |
| Commitment pooling | Dream, offer, promise, refusal, withdrawal, pool capacity, and witness receipts now compose in a fixture only through explicit authority and transition records. |
| Display review | `templates/display-review-checklist.md` and the story-card walkthrough make display approval a separate review step. |
| Speech-act transitions | `templates/speech-act-transition.md` is now the category-drift checkpoint for citation -> claim, dream -> commitment, witness -> story, allocation -> route diagnostic, and related moves. |
| Composition engine | `scripts/composition_engine.py` v0.1.1 generates diagnostic reports and JSON traces across the three main fixtures. |
| Coherence vs goodness | `workshop/coherence-vs-goodness.md` separates composability, coherence, and desirability/health. |
| Trade-off surfaces | `templates/trade-off-surface.md` plus two worked examples test deliberation support for both approved-for-fixture and non-composable cases. |
| Waka / Claims Engine bridge | `workshop/waka-claims-engine-primitive-comparison.md` frames Waka, RegenAI Claims Engine, and Creator Jam Coordination Canoe as adjacent surfaces without treating mapping as adoption. |
| Play | Speech-act bingo gives the jam a lightweight way to notice category drift in real time. |

## Fixture Status

| Fixture | Engine Records | Transitions | Hard Checks | Boundary Result |
| --- | ---:| ---:| --- | --- |
| `claims-witness-receipt-composition` | 7 | 2 | all `ok` | Story candidate remains fixture-only with display gates and excluded evidence. |
| `commitment-pool-dream-witness-composition` | 7 | 4 | all `ok` | One contributor-authorized commitment enters; one offer returns for capacity; refusals stay excluded. |
| `commitment-pool-untracked-allocation-blocked` | 1 | 1 | all `ok` | Private relational support remains summary-only and non-routeable. |

## Core Discipline

The kit's working rule is now:

```text
LLMs can propose compositions.
Schemas and constraints can detect shape.
The composition engine can produce diagnostic traces.
Humans with standing authorize, refuse, narrow, defer, or preserve separate.
Receipts record what happened and what was not established.
```

Composition is not consent. Coherence is not goodness. A blocked composition can be a successful discovery.

## New Closure From The Afternoon

- Older fixtures were normalized to the newer discipline:
  - `explicit_or_inferred` is now present on claims/witness/receipt source records.
  - the blocked allocation transition now carries an AI-use receipt.
  - the blocked allocation record is explicitly represented in `excluded_records`.
- The composition matrix now includes rows for:
  - Waka / Claims Engine primitive comparison
  - Trade-Off Surface as a deliberation-support artifact
- The workshop lab now points directly to the executable composition engine command.
- The midday workfield note is preserved but marked superseded by this rollup.

## Queued Threads

| Thread | Suggested Next Artifact | Why It Matters |
| --- | --- | --- |
| CAT-style receipts | `workshop/transition-receipt-spec-v0.2.md` | Adapts content-addressable transformation receipt fields to human-authorized speech-act transitions. Useful for Claims Engine and Waka bridge work. |
| Conversation -> records | `workshop/conversation-to-records-hazard-map.md` | Names how transcripts can over-extract jokes, dreams, questions, refusals, and tentative offers into claims or commitments. |
| Indigenomics AI app | App gateway sidecar fixture | Connects participant entry, offering card, composition suggestion, AI-use receipt, review, and display gates. |
| Risk / sensors / claims | Fixture-backed boundary stress test | Tests whether sensor evidence can inform resilience without becoming underwriting, eligibility, or actuarial language. |
| Coordination map layers | Spec or fixture | Maps offers, needs, commitments, refusals, issues, places, evidence, and pathways with visibility and authority boundaries. |
| Deeper play | Commitment pool simulator or card game | Makes returned, refused, withdrawn, pending, and accepted states playable before real deployment. |
| More deliberation support | Value-lens view, adjacent-possible map, future-horizon review | Extends the trade-off surface only when a concrete fixture needs the next deliberation tool. |

## External Threads

- Austin / Waka: watch for reply. Do not write an interop spec until posture is known. The current comparison doc is analysis, not a claim about Waka adoption.
- Carol Anne: optional language/canoe-naming conversation can be queued gently; current `Coordination Canoe` use is a provisional English working metaphor.
- Eve / Shawn: refresh the team review note before sending, because the kit now has more artifacts than the earlier review note described.

## Successor Session Start

Start from the latest pushed `main` branch. First run:

```bash
git status --short
python3 scripts/validate-frontmatter.py
python3 scripts/validate-bundle-links.py
python3 scripts/composition_engine.py examples/spec-experiments/claims-witness-receipt-composition --write
python3 scripts/composition_engine.py examples/spec-experiments/commitment-pool-dream-witness-composition --write
python3 scripts/composition_engine.py examples/spec-experiments/commitment-pool-untracked-allocation-blocked --write
```

Best first decision for the next session: choose between CAT-style transition receipts, conversation-to-records hazard mapping, or the Indigenomics AI app gateway sidecar fixture.
