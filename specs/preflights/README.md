---
doc_id: indigenomics.jam.specs.preflights
doc_kind: preflight-index
status: complete
date: 2026-05-25
---

# Spec Preflights — TELUS Lane Build Status

Four single-file-CLI-shaped specs from the kit menu, each run through the TELUS build lane (Gemma 4 31B + Qwen 3.6 35B) overnight. This index tells mentors which specs are **spot-checked good for Monday** and what to watch for on the others.

## Results

| Spec | Gemma | Qwen | Status | Notes |
|---|---|---|---|---|
| **Sensor-To-Receipt Pipeline** | ✅ 6/6 clean | ✅ 6/6 clean | **spot-checked good** | Both models built clean first try. Honors `sensitive_location_flag` redaction. |
| **Untracked Allocation Ledger** | ✅ 6/6 clean | ✅ 6/6 clean | **spot-checked good** | Both clean. Anti-surveillance discipline preserved (never sums amounts). |
| **Claims Evidence Coherence Report** | ⚠️ 7/8 partial | ✅ 8/8 clean | **partial — recommend Qwen** | Gemma stuck on optional `as_of` CLI arg. Qwen got it. |
| **Witness Record Interop Profile** | ⚠️ 6/7 partial | ⚠️ 6/7 partial | **needs sharpening — both models stuck on as_of arg** | Same `as_of`-handling issue. The spec mentions the arg; both models defaulted instead. |

Total: 2 specs both-clean; 1 spec Qwen-clean (recommend specifying model in build path); 1 spec partial on both (mentor warning before recommending).

## What "spot-checked good" means

The spec's core mechanic builds cleanly under the TELUS lane in at least one model attempt, with no repair needed, against a small but realistic fixture. Mentors can recommend the spec to a team with confidence that the spec itself is buildable.

**It does NOT mean:**
- The spec is "correct" (correctness depends on the team's interpretation and use)
- The spec is production-ready
- Future builds with different fixtures will also pass
- Any reuse permission is granted

## Files per preflight

Each `specs/preflights/<spec-name>/` contains:
- `build-packet.json` — minimal team-submission → frozen runtime packet for the preflight
- `build-instructions.md` — frozen build spec
- `acceptance-test.py` — unittest cases (6–8 tests per spec)
- `runs/<run-id>/` — committed artifacts: `attempt-1.py`, `build-attempt.json`, `reviewer-findings.json`, `canoe-landing/witness-record.md`

## Common failure mode observed

**Optional CLI arguments are at risk** — both partial-pass specs had an optional `as_of YYYY-MM-DD` arg that the model didn't wire up. This is the single most common failure mode across these preflights. Teams using optional args should write at least one acceptance test that explicitly exercises the arg, and consider making the arg required if mentor-side risk is low.

See `docs/troubleshooting-and-failure-modes.md` for the full catalog.

## Reproducibility

For any preflight:

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/<spec-name>/build-packet.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/<spec-name>/runs \
  --run-prefix <prefix> \
  --models gemma-4-31b,qwen-3.6-35b
```

## What's not preflighted (and why)

The other 10 specs in `specs/README.md` are **composition-required** or **doc-shaped** — they don't fit a single-file CLI 2-day build path:

- **Composition-required**: Commitment Pool Route Diagnostic, Flow Funding Frontier Map, Dream To Fulfillment Board, Bioregional Mapping Layer Board, Living Atlas Coherence Packet, Bioregional Insights Briefing, Risk and Insurance Coherence Map, Private Learning Ledger
- **Doc-shaped**: Participant Gateway, Graph Chat Witness Sidecar, Receipt Wall Story Gallery, Spec Composer Bundle Board

For composition-required specs, mentors should group them: "X + Y + Z work together as a small composition." See `examples/composition-v0/` for a worked composition example.

Note: a **routing-diagnostic CLI variant** of Commitment Pool Route Diagnostic is preflighted as a sample at `examples/sample-submission-commitment-pool/` — Gemma 7/7 fixed-after-repair, Qwen 6/7 improved. Mentors can show that as evidence that *part* of a composition spec is buildable standalone.

A **CLI variant** of Receipt Wall Story Gallery is also preflighted as a sample at `examples/sample-submission-receipt-wall/` — Gemma 7/7 fixed-after-repair, Qwen 5/7 no-change.

## Boundary

This index states what the lane did on 2026-05-25 against four specific small fixtures. It does not certify spec correctness, completeness, fit, or reuse readiness. Mentors recommend specs with confidence informed by this data; teams build with their own discipline.
