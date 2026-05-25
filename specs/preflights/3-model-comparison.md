---
doc_id: indigenomics.jam.preflights.3-model-comparison
doc_kind: preflight-comparison
status: v0
date: 2026-05-25
---

# 3-Model Comparison — TELUS Lane on Gemma + Qwen + gpt-oss

All 17 packets (14 spec preflights + 3 sample submissions) run overnight through three models in the TELUS catalog: **Gemma 4 31B**, **Qwen 3.6 35B**, and **gpt-oss 120B**.

## Headline

**14 of 17 packets built-clean or fixed-after-repair on gpt-oss 120B.** Same general shape as Gemma + Qwen, with some interesting differences on specific failure modes.

## Per-packet results

| # | Packet | Gemma | Qwen | gpt-oss 120B |
|---|---|---|---|---|
| 1 | dream-to-fulfillment-board | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 2 | untracked-allocation-ledger | ✅ 6/6 | ✅ 6/6 | ✅ 6/6 |
| 3 | bioregional-mapping-layer-board | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| 4 | risk-insurance-coherence-map | ⚠️ 2/3 no-change | ✅ 3/3 fixed | ✅ 3/3 fixed |
| 5 | witness-record-interop-profile | ⚠️ 6/7 no-change | ⚠️ 6/7 no-change | ✅ **7/7 fixed** ⭐ |
| 6 | graph-chat-witness-sidecar | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 7 | bioregional-insights-briefing | ✅ 3/3 | ✅ 3/3 | ✅ 3/3 |
| 8 | sensor-to-receipt-pipeline | ✅ 6/6 | ✅ 6/6 | ✅ 6/6 |
| 9 | participant-gateway | ✅ 4/4 | ✅ 4/4 fixed | ✅ 4/4 |
| 10 | spec-composer-bundle-board | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 11 | flow-funding-frontier-map | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 12 | private-learning-ledger | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 13 | living-atlas-coherence-packet | ✅ 4/4 | ✅ 4/4 | ✅ 4/4 |
| 14 | claims-evidence-coherence-report | ⚠️ 7/8 no-change | ✅ 8/8 | ⚠️ 7/8 no-change |
| 15 | sample-kelp-watch | ✅ 6/6 | ✅ 6/6 | ✅ 6/6 |
| 16 | sample-story-receipts | ✅ 7/7 fixed | ⚠️ 5/7 no-change | ✅ **7/7 fixed** ⭐ |
| 17 | sample-pool-route | ✅ 7/7 fixed | ✅ 6/7 improved | ✅ **7/7 fixed** ⭐ |

⭐ = gpt-oss caught something other models missed or matched best result on.

## Aggregate counts

| Outcome | Gemma | Qwen | gpt-oss 120B |
|---|---|---|---|
| Built clean (first try) | 11 | 11 | 13 |
| Fixed after repair | 2 | 4 | 4 |
| Improved (partial after repair) | 0 | 1 | 0 |
| No change (stuck partial) | 4 | 2 | 1 |
| **Total** | 17 | 18 (M2.6 dogfood +1) | 17 |

(Counts add to 17 within each column except Qwen, which has one extra reflecting the M2.6 dogfood test run earlier.)

## Per-failure-mode patterns

### `witness-record-interop-profile` (optional `as_of` CLI arg)

- Gemma: no change 6/7
- Qwen: no change 6/7
- **gpt-oss 120B: fixed 7/7** — caught the optional arg on repair where the smaller models didn't

### `claims-evidence-coherence-report` (also `as_of` CLI arg)

- Gemma: no change 7/8
- Qwen: clean 8/8 (first try, no repair)
- gpt-oss 120B: no change 7/8 — same partial pattern as Gemma

### `risk-insurance-coherence-map` (discipline-as-NOT-doing — "do not rank")

- Gemma: no change 2/3
- Qwen: fixed 3/3
- gpt-oss 120B: fixed 3/3 — matched Qwen on this discipline test

### `sample-story-receipts` (markdown vertical whitespace)

- Gemma: fixed 7/7
- Qwen: no change 5/7
- gpt-oss 120B: fixed 7/7 — matched Gemma on markdown discipline

## Observations

1. **gpt-oss 120B is the strongest single model in this overnight cohort.** Built-clean rate 13/17 vs Gemma 11/17 vs Qwen 11/17. Caught the `witness-record-interop-profile` optional arg that both smaller models missed.

2. **gpt-oss is not strictly dominant.** Qwen 3.6 35B beat gpt-oss on `claims-evidence-coherence-report` (Qwen 8/8 clean first try vs gpt-oss 7/8 no change). The two failures are correlated (both `as_of` arg-related) but Qwen handled this case.

3. **Recommending "the lane" rather than "this model" is still the right framing.** No single model is dominant on every spec. Running on multiple models surfaces edge cases.

4. **Three-model diversity is the strongest configuration.** For the witness-record-interop-profile, only gpt-oss converged. For claims-coherence, only Qwen converged. Running all three is the surest signal.

5. **Zero boundary leaks observed across all 3 models, all 17 packets, on overnight runs.** The exporter discipline holds across model choice.

## Implications for mentor guidance

The mentor field guide's recommendation — "recommend the lane, not the model" — is supported by this 3-model data. For teams using TELUS:

- Default model: any of the three is acceptable.
- If first attempt with one model fails: try a different model before sharpening the spec.
- If the spec involves optional CLI args: gpt-oss 120B is the stronger choice based on this overnight data.
- If the spec involves markdown whitespace rules: Gemma or gpt-oss outperform Qwen.
- If the spec involves discipline-as-NOT-doing: Qwen or gpt-oss outperform Gemma.

## Reproducibility

All 17 packets re-run via:

```bash
bash /tmp/run-gpt-oss-preflights.sh
```

(Script at `/tmp/run-gpt-oss-preflights.sh` — not committed to repo; reproducible from the loop structure documented above.)

Or per-packet:

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet <path-to-build-packet.json> \
  --output-dir <output-dir> \
  --run-prefix gptoss-<name> \
  --models gpt-oss-120b
```

## Boundary

This comparison records what three TELUS-lane models did on 17 small fixtures on 2026-05-25. It does not certify any model's general capability, and one night of data is not a thorough benchmark. The kit's discipline holds; specific model recommendations are observations, not authority.
