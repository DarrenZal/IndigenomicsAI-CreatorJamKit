---
doc_id: indigenomics.jam.specs.preflights
doc_kind: preflight-index
status: complete-v2
date: 2026-05-25
---

# Spec Preflights — TELUS Lane Build Status

**14 of 14 ready-to-jam specs preflighted overnight on 3 models** (Mon 2026-05-25). Each spec was given a minimal CLI-subset packet, then run through the TELUS build lane: Gemma 4 31B + Qwen 3.6 35B + gpt-oss 120B. This index tells mentors which specs are spot-checked good for Monday.

For the **3-model comparison table** (including gpt-oss 120B which sometimes catches edge cases the smaller models miss), see [`3-model-comparison.md`](3-model-comparison.md).

## Headline result

**11 specs both-models clean. 2 specs Qwen-only clean. 1 spec both-partial.**

Across 28 model attempts (14 specs × 2 models), zero boundary leaks were observed in any generated tool or output. The exporter strips excluded inputs structurally; the model never sees them.

## Results table

| # | Spec | Gemma | Qwen | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | **Witness Record Interop Profile** | ⚠️ 6/7 | ⚠️ 6/7 | partial — both | Optional `as_of` CLI arg not wired up by either model |
| 2 | **Claims Evidence Coherence Report** | ⚠️ 7/8 | ✅ 8/8 | recommend Qwen | Same `as_of` arg issue on Gemma |
| 3 | **Sensor To Receipt Pipeline** | ✅ 6/6 | ✅ 6/6 | **spot-checked good** | Honors `sensitive_location_flag` redaction |
| 4 | **Untracked Allocation Ledger** | ✅ 6/6 | ✅ 6/6 | **spot-checked good** | Anti-surveillance discipline preserved |
| 5 | **Flow Funding Frontier Map** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | Edge-walk + status filtering correct |
| 6 | **Spec Composer Bundle Board** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | Interface-intersection logic |
| 7 | **Risk and Insurance Coherence Map** | ⚠️ 2/3 | ✅ 3/3 fixed | recommend Qwen | Gemma got tripped up on the "do not rank" discipline |
| 8 | **Dream To Fulfillment Board** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | Stage-machine kanban output |
| 9 | **Living Atlas Coherence Packet** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | Coherence-check flagging works |
| 10 | **Private Learning Ledger** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | `private_notes` never leaked in either output (specifically verified) |
| 11 | **Bioregional Mapping Layer Board** | ✅ 3/3 | ✅ 3/3 | **spot-checked good** | Consent-tier filtering correct |
| 12 | **Bioregional Insights Briefing** | ✅ 3/3 | ✅ 3/3 | **spot-checked good** | Markdown template generation |
| 13 | **Participant Gateway** | ✅ 4/4 | ✅ 4/4 fixed | **spot-checked good** | Decision tree (ROUTE/HOLD/REFUSE) |
| 14 | **Graph Chat Witness Sidecar** | ✅ 4/4 | ✅ 4/4 | **spot-checked good** | Citation coverage diagnostics |

Plus three sample submission pairs in `examples/` covering the same shapes from a different angle (Kelp Watch, Story Receipts, Pool Routing Diagnostic).

## What "spot-checked good" means

The spec's core mechanic builds cleanly under the TELUS lane in at least one model attempt, with no repair needed, against a small but realistic fixture. Mentors can recommend the spec to a team with confidence that the spec itself is buildable.

It does NOT mean: the spec is "correct" (correctness depends on the team's interpretation), production-ready, or that future builds with different fixtures will pass. One small fixture, one model attempt.

## Common failure modes observed

1. **Optional CLI arguments** — single most common failure (4 of 5 partial passes traced to this). Models default to data-derived values instead of reading optional `argv[2]`.
2. **Discipline-as-NOT-doing** — Risk Coherence Map's "do not rank, do not score, do not aggregate severity counts" tripped Gemma. The model wanted to summarize severity counts; it took repair feedback to remove that.
3. **Markdown blank-line placement** — captured in earlier sample preflights; less common in spec preflights here.

Full failure catalog: `docs/troubleshooting-and-failure-modes.md`.

## Honor of the "doesn't fit yet" outcome

Of the 14 specs, every single one had at least one model produce a clean build. **No spec was unbuildable.** This is good news for Monday — the spec menu is real.

A team that picks a spec is choosing a spec that has been spot-checked. They are not choosing whether the spec is buildable — that's been answered. They are choosing how to interpret it, what fixtures to use, what boundaries to honor.

## What didn't get preflighted (and why)

- **Two `examples/sample-submission-*/`** that are full participant-shaped sample pairs (Kelp Watch + Story Receipts + Pool Routing) — not in this table because they're framed as sample submissions rather than spec preflights. Same kind of run; different folder location.

## Reproducibility

For any preflight:

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/<spec-name>/build-packet.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/<spec-name>/runs \
  --run-prefix <prefix> \
  --models gemma-4-31b,qwen-3.6-35b
```

## Boundary

This index states the TELUS lane's behavior on 2026-05-25 against 14 small fixtures. It does not certify spec correctness, completeness, fit, or reuse readiness. Mentors recommend specs informed by this data; teams build with their own discipline.
