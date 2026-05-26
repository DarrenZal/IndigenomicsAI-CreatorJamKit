---
doc_id: indigenomics.jam.specs.orchestrator-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-26
---

# Orchestrator v0 — autonomous spec-execution network

The fifth meta-spec, composing all the others. Given a set of jam
specs, attempts each through the chain (offering → drafting →
build-queue → witness → publish), honoring refusals at every step.

## What it is

- CLI: `scripts/jam/orchestrator.py` (stdlib-only)
- Reads the kit's spec menu, filters by refusal-gatekeeper (cultural /
  Nation-specific framings → auto-refuse)
- Generates a participant-shape offering per spec via TELUS
- Runs `spec_drafting_loop.py` to produce a frozen build packet OR
  refusal-as-outcome
- Emits a build-queue entry so a builder (Claude Code subagent or
  human operator) can pick up the packet + write the CLI
- Optionally waits for builder result with `--builder-wait-seconds`
- Drafts a witness record via `draft_witness.py`
- Validates + publishes to wall via `witness_append.py`
- Posts `witness_observe` to bus at key steps for cross-team
  coordination visibility

## What it is not

- Not autonomous code generation. v0 ships orchestration only; the
  builder step uses Claude Code subagents OR operator-manual builds.
  v0.2 may add TELUS-builder support.
- Not authority. Witness records published autonomously carry the
  standard receipt statement; they don't certify anything.
- Not a substitute for facilitator review. Operator should review the
  wall before any external sharing.

## Try it (60 sec)

```bash
source ~/projects/indigenomics-ai-gateway/.env.telus
python3 scripts/jam/orchestrator.py run \
  --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \
  --gateway http://localhost:8000 --team-key "$DOGFOOD_TEAM_KEY" \
  --models telus-qwen,telus-gemma \
  --max-specs 5 \
  --max-telus-calls 60 \
  --time-budget-min 60 \
  --bus-root /tmp/orchestrator-bus \
  --out-dir /tmp/orchestrator-runs

# After run completes:
python3 scripts/jam/orchestrator.py report /tmp/orchestrator-runs
```

## Refusal gatekeeper

A spec is auto-refused-by-design if its body contains ANY of these
terms (case-insensitive): cultural authorization, Carol Anne,
Ahousaht, Hesquiaht, Tla-o-qui-aht, Nuu-chah-nulth, Indigenous data
sovereignty, Nation-specific, Nation authority, elder, ceremonial,
traditional knowledge, OCAP, FPIC, potlatch, longhouse.

This is **deliberately conservative**. False-positives (e.g., a spec
that QUOTES the discipline against these terms in its Refusal
Boundaries section) refuse-by-default — the operator can override
manually.

## Refusal layers at runtime

| Layer | Refusal trigger | Outcome |
|---|---|---|
| Gatekeeper | Cultural/Nation terms in spec body | `refused-by-gatekeeper` |
| Drafting model | Sharpened prompt detects cultural framing in offering | `refused-by-model: <reason>` |
| Drafting loop | annotated_spec not dict / vision+spec empty | `doesnt-fit-yet-no-packet` |
| Builder (future) | Acceptance tests fail after revision | `built-failed` |
| Witness validator | Overclaim language detected | `witness-draft-failed` |
| Publisher | --confirm-publish required per record | (implicit via flag) |

Every refusal lands as `witness_observe` on the bus + a row in the
orchestrator run summary.

## Budget caps

- `--max-specs N` (default 5)
- `--max-telus-calls N` (default 60)
- `--time-budget-min N` (default 60 min)
- Builder wait: `--builder-wait-seconds 0` (default — skip building)

## Composition

- Uses [`agent-coordination-bus-v0`](../agent-coordination-bus-v0/) for cross-step audit trail
- Drives [`agentic-spec-drafting-loop-v0`](../agentic-spec-drafting-loop-v0/) per spec
- Drives [`draft-witness-v0`](../draft-witness-v0/) post-build
- Drives [`witness-record-append-v0`](../witness-record-append-v0/) for publication

The orchestrator IS the jam dogfooding itself — five meta-specs
composing into one autonomous network.

## Files

- `../../scripts/jam/orchestrator.py` — main CLI
- `spec-v0.md` — formal spec (TODO)
- (no tests yet — integration tested via smoke runs against local
  TELUS-mode gateway)

## Boundary

Validated lane = autonomous orchestration of an offering through the
chain primitives, honoring refusal at every step. NOT certification,
NOT authority, NOT a substitute for facilitator review. The wall
records what happened; the orchestrator records what it attempted +
what refused.

🛶
