---
doc_id: indigenomics.jam.specs.agentic-spec-drafting-loop-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Agentic Spec Drafting Loop — v0

The loop that wires Prompts 1, 2, 4 (from
[`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../../participant-agent-context/PROMPTS_FOR_AGENTS.md))
into a pipeline that takes loose offerings and produces a frozen
`agentic-build-packet-v0.json` ready for a TELUS lane attempt.

This is the second meta-spec for the jam (after
[`agent-coordination-bus-v0/`](../agent-coordination-bus-v0/)). The two
compose: agents collaborating across teams via the bus can use this
loop to draft and freeze the team's own build packet.

## What it is

- Stdlib Python CLI: `scripts/jam/spec_drafting_loop.py`
- Stub model adapter (deterministic, offline) for tests + acceptance
- Gateway adapter (HTTP POST to `indigenomics-ai-gateway`)
- 5 stages: ingest offering → draft → boundary check → (optionally compose) → freeze
- Output: `team-submission-v0.md` + `agentic-build-packet-v0.json` + `freeze-record.json`

## What it is not

- Not stage 6 (witness drafting). That happens AFTER a real build attempt and is a separate CLI.
- Not autonomous freeze authority. The auto-freeze flag is explicit in the freeze record; human facilitator confirmation is still the canonical authority.
- Not a replacement for the team's own deliberation. The loop is a draft assistant, not a judgment.

## Try it (60 seconds)

```bash
# Stub mode (offline, deterministic)
python3 scripts/jam/spec_drafting_loop.py run \
  examples/spec-drafting-loop-demo/offering-kelp-cover-map.md \
  --model-source stub --confirm-freeze \
  --team-name "Kelp Bed Observers" --team-site Victoria \
  --out-dir /tmp/runs

# Gateway mode (against local indigenomics-ai-gateway)
python3 scripts/jam/spec_drafting_loop.py run \
  examples/spec-drafting-loop-demo/offering-kelp-cover-map.md \
  --model-source gateway --gateway http://localhost:8000 \
  --team-key iai_dev_victoria --confirm-freeze \
  --team-name "Kelp Bed Observers" --team-site Victoria \
  --out-dir /tmp/runs
```

## Composition

- [`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../../participant-agent-context/PROMPTS_FOR_AGENTS.md) — the 4 prompts this loop wires together (1 spec drafter / 2 boundary checker / 3 witness drafter [not in v0] / 4 collaboration facilitator)
- [`templates/team-submission-v0.md`](../../templates/team-submission-v0.md) + [`templates/agentic-build-packet-v0.md`](../../templates/agentic-build-packet-v0.md) — the schemas this loop outputs
- [`scripts/composition_engine.py`](../../scripts/composition_engine.py) — the multi-team composition engine the loop's stage 4 calls
- [`specs/agent-coordination-bus-v0/`](../agent-coordination-bus-v0/) — the bus that carries this loop's stage 6 `witness_observe` output (downstream)

## Tests

```bash
python3 -m unittest scripts.jam.tests.test_spec_drafting_loop -v
```

Expected: 12 tests OK. Combined with `test_bus.py`: 32 tests across both meta-specs.

## Files

- `spec-v0.md` — formal spec
- `../../scripts/jam/spec_drafting_loop.py` — main orchestrator
- `../../scripts/jam/stub_model.py` — deterministic stub adapter
- `../../scripts/jam/tests/test_spec_drafting_loop.py` — 12 unittest cases
- `../../examples/spec-drafting-loop-demo/` — worked example

## Boundary

Validated lane = orchestration of an offering through Prompts 1, 2, 4
+ local boundary check + (optional) composition into a frozen build
packet. NOT autonomous authoring authority. NOT a substitute for human
facilitator freeze. Stub mode is offline + deterministic (not real
inference). Witness drafting (Prompt 3) is downstream of build
execution and lives in a separate CLI.
