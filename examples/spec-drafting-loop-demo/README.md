---
doc_id: indigenomics.jam.examples.spec-drafting-loop-demo
doc_kind: worked-example
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Spec Drafting Loop — worked example

A worked example of [`specs/agentic-spec-drafting-loop-v0/`](../../specs/agentic-spec-drafting-loop-v0/),
showing one offering flowing through stages 1–5 of the loop to produce a
frozen `team-submission-v0.md` + `agentic-build-packet-v0.json`.

## What's here

- [`offering-kelp-cover-map.md`](offering-kelp-cover-map.md) — a sample
  participant offering (Salish-Sea-ecological framing, no Indigenous-
  cultural content).

## Try it (stub mode — offline)

From the kit root:

```bash
# Run loop end-to-end with deterministic stub model
python3 scripts/jam/spec_drafting_loop.py run \
  examples/spec-drafting-loop-demo/offering-kelp-cover-map.md \
  --model-source stub \
  --confirm-freeze \
  --team-name "Kelp Bed Observers" \
  --team-site Victoria \
  --out-dir /tmp/spec-drafting-runs

# Inspect the produced artifacts
ls /tmp/spec-drafting-runs/<run-id>/
# 1-offering.json
# 2-draft-spec.json
# 3-annotated-spec.json
# 5-team-submission-v0.md
# 5-agentic-build-packet-v0.json
# 5-freeze-record.json
# run.json
```

Output: `FROZEN — run <id>`, with paths to the three frozen artifacts +
audit log.

## Try it (gateway mode — local TELUS stub)

First, boot the local gateway (in another terminal):

```bash
cd ~/projects/indigenomics-ai-gateway
make smoke-local  # validates stack, then exits
# OR keep services running with:
# make dev
```

Then run the loop pointing at the gateway:

```bash
python3 scripts/jam/spec_drafting_loop.py run \
  examples/spec-drafting-loop-demo/offering-kelp-cover-map.md \
  --model-source gateway \
  --gateway http://localhost:8000 \
  --team-key iai_dev_victoria \
  --confirm-freeze \
  --team-name "Kelp Bed Observers" \
  --team-site Victoria \
  --out-dir /tmp/spec-drafting-runs
```

In gateway mode, each prompt's response is captured as raw text (the
gateway returns OpenAI-shape chat completions; the loop records the
content verbatim in `2-draft-spec.json`, `3-annotated-spec.json`, etc.).

## Stages exercised

| Stage | What | Adapter call | Output file |
|---|---|---|---|
| 1 | Offering ingestion | (parse only) | `1-offering.json` |
| 2 | Spec drafting (Prompt 1) | `spec-drafter` | `2-draft-spec.json` |
| 3 | Boundary checking (Prompt 2) | `boundary-checker` | `3-annotated-spec.json` |
| 3.5 | Boundary leak check (local) | (regex check) | (no file; logged in run.json) |
| 4 | Composition + facilitation (Prompt 4) | `collaboration-facilitator` | `4-collaboration-assessment.json` (only if `--composes`) |
| 5 | Freeze | (renderer) | `5-team-submission-v0.md` + `5-agentic-build-packet-v0.json` + `5-freeze-record.json` |

Stage 6 (witness drafting via Prompt 3) runs downstream after a real
build attempt against the frozen packet; that's a separate CLI
(`scripts/jam/draft_witness.py`) and not part of this loop's v0.

## What this demo proves

- ✅ A loose offering flows cleanly through Prompts 1 + 2 + 4 (via stub
  or gateway) into a frozen `agentic-build-packet-v0.json`.
- ✅ Boundary leak check rejects protected-content markers leaking
  outside the boundaries[] list.
- ✅ Without `--confirm-freeze`, the loop stops after stage 4 — the
  freeze decision belongs to a human facilitator.
- ✅ With `--confirm-freeze`, the auto-freeze is explicit in the
  freeze_record's `frozen_by` field — it does NOT pretend to be a
  facilitator confirmation.

## Compose with other meta-specs

- The build packet emitted at stage 5 is the input to a real TELUS lane
  build attempt (see `specs/preflights/` for the existing preflight
  pipeline).
- The witness record draft produced by stage 6 (separate CLI) lands at
  [`specs/witness-record-append-v0/`](../../specs/witness-record-append-v0/)
  (Tuesday).
- The agent-coordination-bus carries the witness_observe message that
  this loop emits at the end of a real run.

## Boundary

Validated lane = orchestration of an offering through Prompts 1+2+4 +
local boundary check to produce a frozen build packet. NOT autonomous
authoring authority, NOT certification, NOT a substitute for facilitator
freeze. Stub mode is offline + deterministic — useful for tests, not
real inference.
