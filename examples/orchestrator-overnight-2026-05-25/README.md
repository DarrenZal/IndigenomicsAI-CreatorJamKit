---
doc_id: indigenomics.jam.examples.orchestrator-overnight-2026-05-25
doc_kind: worked-example
status: v0.2
visibility: public_sample
date: 2026-05-25
last_updated: 2026-05-26
---

# Orchestrator overnight run — autonomous wall records

5 witness records produced autonomously by `scripts/jam/orchestrator.py`
running v0.2 against real TELUS models (Qwen + Gemma) via the local
indigenomics-ai-gateway in TELUS mode. Wall-clock: 6 min for 7 specs.
Total TELUS calls: 33.

## What this demonstrates

The 5 meta-specs (bus / drafting-loop / draft-witness / wall /
orchestrator) compose into an autonomous network that:

1. **Honors refusal at multiple layers.** 1 spec was refused-by-model
   (sharpened Prompt 1's `{"refusal": "requires cultural authorization"}`
   path); 1 spec was rejected at pre-freeze-sanity (model produced
   empty vision/spec). Neither shipped null content to the wall.

2. **Publishes discipline-clean records.** All 5 published records
   passed the witness validator (no overclaim language, receipt
   statement present). Prompt 3 v0.2 — with explicit forbidden-words
   list ("approved", "approval", etc.) — eliminated the 2 publish
   failures from v0.1's run.

3. **Surfaces model-judgment diversity.** Different models judge the
   same spec offerings differently:
   - v0.1 (Qwen): witness-record-interop-profile refused; bioregional-mapping published
   - v0.2 (Gemma + Qwen mix): witness-record-interop-profile published; bioregional-mapping refused
   
   This is genuine model-judgment variation, not a bug. Both judgments
   honored cultural-authorization caution; the diversity is useful
   Tuesday-sprint material.

## Per-spec outcomes (v0.2)

| Spec | Model | Outcome |
|---|---|---|
| witness-record-interop-profile | Qwen | published |
| claims-evidence-coherence-report | Gemma | published |
| commitment-pool-route-diagnostic | Qwen | doesnt-fit-yet (pre-freeze-sanity caught empty content) |
| dream-to-fulfillment-board | Gemma | published |
| receipt-wall-story-gallery | Qwen | published |
| flow-funding-frontier-map | Gemma | published |
| bioregional-mapping-layer-board | Qwen | refused-by-model: requires cultural authorization |

## Wall records

5 files under `wall/`. Each contains a witness record drafted by
TELUS via Prompt 3 v0.2 + the standard receipt-statement footer.
All validated clean before publication.

Note: finding is `no-change` on every record because builder-wait-seconds=0
in v0 of the orchestrator. The orchestrator's TELUS-reasoning layer
emits witness drafts; the building step is a Tuesday-sprint extension
target (TELUS-builder mode or Claude-Code-subagent builder).

## How to reproduce

```bash
cd ~/projects/IndigenomicsAI-CreatorJamKit
source ~/projects/indigenomics-ai-gateway/.env.telus
python3 scripts/jam/orchestrator.py run \
  --kit-root . \
  --gateway http://localhost:8000 --team-key "$DOGFOOD_TEAM_KEY" \
  --models telus-qwen,telus-gemma \
  --max-specs 7 --max-telus-calls 80 --time-budget-min 30 \
  --bus-root /tmp/my-orch-bus \
  --out-dir /tmp/my-orch-runs

# Report:
python3 scripts/jam/orchestrator.py report /tmp/my-orch-runs
```

Expected: 5-6 of 7 publish (with model-judgment diversity), 1-2
refused-or-doesnt-fit, in under 10 min wall-clock with under 50 TELUS calls.

## Boundary

These records were produced AUTONOMOUSLY by the orchestrator + TELUS
models. They state what happened: the orchestrator drafted them; the
validator passed them; the wall accepted them. They do NOT establish
authority, certification, legitimacy, or reuse permission. Tuesday
participants extending the orchestrator decide whether to extend or
contest any of this.

🛶
