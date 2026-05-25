---
doc_id: indigenomics.jam.overnight-research-findings
doc_kind: research-synthesis
status: v0
date: 2026-05-25
audience: jam organizers, Carol Anne (post-event), future jam organizers
---

# Overnight Research Findings — Creator Jam Kit, 2026-05-25

What was learned in ~6 hours of overnight preparation before Day 1 of the IndigenomicsAI Creator Jam. This document synthesizes results from: 3 sample submission pairs, 14 spec preflights through the TELUS build lane, 5 adversarial harness stress tests, 4 mentor helper tools shipped, a participant-agent knowledge bundle, and a kit UX walkthrough.

## Headline findings

1. **Every ready-to-jam spec is buildable** — across 14 spec preflights + 3 sample submission pairs, ~36 model build attempts, every single spec had at least one model produce a clean (or fixed-after-repair) build. The kit's menu is real.

2. **Zero boundary leaks across all attempts** — the build packet's `excluded_inputs` content is stripped structurally by the exporter; the model never sees it. Reviewer-findings leak-checks were clean on every run. Teams worried about protected material leaking through can be reassured by this data.

3. **Spec ↔ acceptance-test alignment is the single most common failure mode** — accounts for more failed test cases than any other category. Walk teams through their spec ↔ test alignment before freeze.

4. **Text-format / markdown outputs are noticeably harder than numeric/tabular** — Gemma usually repairs; Qwen sometimes doesn't. Numeric rollups built clean first try ~half the time; markdown specs needed at least one repair cycle on every attempt observed.

5. **Optional CLI arguments are a real failure mode** — 4 of 5 partial-pass specs failed because the model didn't wire up an optional `argv[2]`. Three mitigations: make it required, write a test that exercises it, or default to a fixed value not data-derived.

6. **The harness validation gate works for the obvious cases** — frozen=false and missing-required-field were both refused. But it does NOT check structural validity of `excluded_inputs` entries, content quality of `allowed_inputs`, or sensible authorization vs build-path combinations. Team-side over-clearing of `allowed_inputs` would not be caught.

7. **Two models (Gemma 4 31B, Qwen 3.6 35B) give complementary coverage** — Gemma usually repairs better; Qwen sometimes catches what Gemma misses. Recommending "the lane" rather than "this model" is the right framing.

## Methodology

### Sample submission pairs (3)

Each pair: a fictional team writes a `team-submission-v0`, freezes, exports an `agentic-build-packet-v0`, and runs through the TELUS lane on both Gemma + Qwen. Different output shapes deliberately.

- **Kelp Watch** — numeric rollup (means + counts) at `examples/sample-submission-pair/`
- **Story Receipts Wall** — markdown text aggregation with consent gates at `examples/sample-submission-receipt-wall/`
- **Pool Routing Diagnostic** — per-kind routing diagnostic at `examples/sample-submission-commitment-pool/`

### Spec preflights (14)

For each of the 14 ready-to-jam specs in the kit, write a minimal CLI-subset packet and run through Gemma + Qwen. Index at `specs/preflights/README.md`.

### Harness stress tests (5)

Adversarial packets sent to the lane to map the harness's discipline-boundary. Report at `specs/preflights/stress-tests/README.md`.

## Per-spec data

| Spec | Both clean? | Notes |
|---|---|---|
| Sensor To Receipt Pipeline | ✅ both 6/6 | spot-checked good; sensitive_location_flag honored |
| Untracked Allocation Ledger | ✅ both 6/6 | anti-surveillance discipline preserved |
| Flow Funding Frontier Map | ✅ both 4/4 | edge-walk + status filtering correct |
| Spec Composer Bundle Board | ✅ both 4/4 | interface-intersection logic |
| Dream To Fulfillment Board | ✅ both 4/4 | state-machine kanban |
| Living Atlas Coherence Packet | ✅ both 4/4 | coherence flagging works |
| Private Learning Ledger | ✅ both 4/4 | private_notes never leaked (specifically verified) |
| Bioregional Mapping Layer Board | ✅ both 3/3 | consent-tier filtering |
| Bioregional Insights Briefing | ✅ both 3/3 | markdown template generation |
| Participant Gateway | ✅ both 4/4 | decision tree (ROUTE/HOLD/REFUSE) |
| Graph Chat Witness Sidecar | ✅ both 4/4 | citation coverage diagnostics |
| Claims Evidence Coherence Report | ⚠️ Qwen 8/8, Gemma 7/8 | optional `as_of` CLI arg, Gemma missed |
| Risk and Insurance Coherence Map | ⚠️ Qwen 3/3 (fixed), Gemma 2/3 | "do not rank" discipline tripped Gemma |
| Witness Record Interop Profile | ❌ both 6/7 | optional `as_of` CLI arg, both models missed |

## Failure-mode catalog

Ranked by frequency across observed builds (see `docs/troubleshooting-and-failure-modes.md` for full):

1. **Spec ↔ acceptance-test misalignment** — most common. Easy fix when caught early.
2. **Optional CLI arguments not wired up** — second most common.
3. **Text-format / markdown whitespace rules** — third most common.
4. **Discipline-as-NOT-doing** — Risk Coherence Map's "do not rank" tripped Gemma. The model defaults to aggregating; specs that require NOT aggregating need explicit refusal language in the spec text.
5. **Structural shape (numeric / tabular / status-enum)** — strongest. ~50% first-try success on both models.

## Things expected to be failure modes but weren't

- **Boundary leaks** — zero observed across all attempts. The exporter strips `excluded_inputs` content structurally.
- **Network / credential access in generated code** — zero observed. Models reliably follow the "stdlib only" constraint.
- **Hardcoded fixture data** — zero observed. Generated tools are data-driven.
- **Infinite loops / timeouts** — zero observed (90s test timeout never hit).
- **Culturally insensitive output** — zero observed. Salish-Sea-ecological framings produced no concerning content.
- **Cleared-text leaks where the team mis-cleared** — model didn't echo leaky content in the one stress test, **but the harness has no automated check for this**. Team-side discipline is the only protection.

## Tools shipped

Four standard-library Python utilities in `tools/`:

- `witness-record-validator.py` — catches overclaim language in Tuesday records (disclaimer-context-aware)
- `withdrawal-propagation.py` — surfaces/summaries to update when a record is withdrawn
- `composition-merger.py` — merge two team submissions into a candidate bundle with conflicts surfaced
- `spec-linter.py` — flag 5+ common failure modes before freeze (grounded in this overnight data)

## Knowledge bundle for participant agents

Shipped to `participant-agent-context/`:

- 64 direct Carol Anne quotes from Books 1 + 2, attributed
- 25-themes summary with anchoring quotes + sample spec ideas per theme
- Plain-language primers on Ruddick's CPP, Johar's metacognition discipline, the compositional-field architecture
- JSON-LD knowledge bundle with 118 entities (Theme / Quote / Concept / Boundary / Discipline / Principle)
- Three sample system prompts for LLMs helping a team (spec drafting / boundary checking / witness record drafting)

Public-safe. Any LLM a participant brings can ingest this. Solves the "participant-agent KB" question independent of Shawn's gateway.

## Discipline observations

Across the night, three discipline-preserving patterns held in 100% of attempts:

1. **The freeze gate is real.** Unfrozen packets refused.
2. **Excluded inputs are stripped structurally.** Model never sees them.
3. **The receipt-statement boilerplate works as a counter-weight.** Witness records include "this does not establish authority/approval/certification/reuse" by default, and the validator catches when teams accidentally embed overclaim language alongside.

One discipline gap surfaced:

- **The harness assumes team-side discipline on `allowed_inputs`.** If a team incorrectly clears private content, the model sees it and could echo it. Not observed in any actual run, but the structural assumption is real. Mitigation: `spec-linter.py` warnings + facilitator review of `cleared_text` fields before freeze.

## Mentor takeaways

1. **Recommend the lane, not a specific model.** Gemma usually repairs cleanly; Qwen sometimes catches what Gemma misses. Both should be tried.
2. **Walk teams through their spec ↔ test alignment before freeze.** Single highest-leverage intervention.
3. **Expect at least one repair cycle on markdown / text-format outputs.** Don't treat first-attempt failure as a spec problem; let the repair run.
4. **Use `spec-linter.py` before freeze.** It catches several issues the harness itself doesn't.
5. **Use `witness-record-validator.py` Tuesday morning.** Catches overclaim language that survives the lane.
6. **Trust the boundary discipline.** Excluded inputs are stripped structurally; reviewer-findings are reliable.

## Recommendations for the next jam

These are observations for future iterations, not changes the team should make day-of:

1. **Harness should validate `excluded_inputs` entries structurally.** A boundary missing `disallowed_use` is silently accepted; could be caught at validation time.
2. **`allowed_inputs.content` could have a "looks-like-PII" warning hook.** Optional, mentor-triggered. Would catch team-side over-clearing.
3. **The kit could ship a "what happens after submit" doc for participants.** UX walkthrough flagged this as a high-friction gap.
4. **Spec cards could include "next step: write a submission" footers.** Currently dead-ends after the acceptance criteria.
5. **`examples/` needs a README.** Currently a flat list of subdirectories.

## What didn't get done overnight

- Cultural-content review of any of the artifacts beyond the kit's existing posture
- Translation to languages other than English
- Mobile-device UX testing (only desktop walkthrough)
- Adversarial spec-text testing (e.g., a spec that tries to instruct the model to ignore boundaries)
- Performance benchmarking under load (only single-build runs)

## Boundary

This synthesis records what was learned overnight on 2026-05-25 against ~36 model build attempts on small fixtures. It does not certify the lane's correctness, robustness, or production-readiness. It does not predict how the lived day will unfold. The artifacts are bounded preparation; the jam is the team's.

This document also does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.

🛶
