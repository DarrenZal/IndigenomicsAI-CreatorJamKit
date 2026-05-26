---
doc_id: indigenomics.jam.specs.overnight-loop-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-26
---

# Overnight Loop v0 — autonomous-execution time-budget for the jam

Composes [`orchestrator-v0`](../orchestrator-v0/) and
[`multi-agent-mesh-v0`](../multi-agent-mesh-v0/) into a bounded,
unattended execution loop. Cycles models across specs round-by-round
until a budget or sentinel fires.

## What it is

- CLI: `scripts/jam/overnight_loop.py` (stdlib-only)
- Wraps `orchestrator.py` with subprocess-per-round invocation. Each
  round = one (spec × model) attempt through the full chain
  (offering → drafting → build → witness → optional reviewer → publish)
- Bounded by `--max-rounds`, `--time-budget-hours`,
  `--max-telus-calls`, OR a sentinel `STOP` file in the persistent
  root. First condition to fire wins.
- Persistent root: ALL writes land under `--persistent-root` (typical
  use: `~/overnight-jam-2026-05-26/`). The loop never writes to the
  kit repo, the IndigenomicsAI repo, or any other location.
  Write-boundary enforced via `loop_safety.ensure_path_within`.
- Mesh-mode (`--mesh-mode`, default ON for overnight) wires the
  Reviewer role into stage 6.5 between witness-draft and publish; the
  Reviewer may halt publish on overclaim / boundary / coherence
  findings.
- Cycles models × specs via `itertools.product`. Configurable model
  list (default `telus-qwen,telus-gemma,telus-gpt-oss`) and spec list
  (default = `ORCHESTRATOR_CANDIDATE_SPECS`).
- Per-round gateway preflight (probes `/health` before invoking
  orchestrator). Gateway down = soft halt + retry after
  `--gateway-retry-seconds`.
- Credential regex scan over every round's output (TELUS responses +
  generated `build_attempt.py`). On hit: writes `HALT-CREDS.txt` and
  stops the loop hard. This is **loop-time** safety only; not a
  replacement for operator-time `audit-public-safety.sh`.
- Aggregator (`agent_aggregator.py`) invoked every N rounds
  (`--aggregate-every`, default 5). Produces
  `aggregator/recommendations-after-round-NNNN.md` — prose-only
  recommendations; no machine-applicable diffs in v0.
- Master log: `<persistent_root>/overnight-master-log.jsonl` —
  append-only JSONL of every round + safety event.
- Wall: cumulative across rounds at `<persistent_root>/wall/`. Every
  round shares the same `--wall-root`.
- Sentinel-stop: drop a file named `STOP` or `STOP.txt` into the
  persistent root; the loop checks at every round boundary and exits
  gracefully.
- HALT-on-stale-halts: if a prior `HALT-*.txt` exists at startup, the
  loop refuses to start. Pass `--ignore-stale-halts` to override
  (operator must have inspected the prior halt).

## What it is not

- Not safe autonomous internet code execution. Generated
  `build_attempt.py` files run with a stripped env (no creds) and a
  30s timeout, but Python stdlib retains network access in principle.
  Operator should monitor gateway logs during overnight runs for
  unexpected request patterns; Docker / network-namespace sandboxing
  is a v0.2 hardening item.
- Not git-aware. The loop process never runs `git`. Outputs that look
  ready to promote should be moved by the operator deliberately in
  the morning, not by the loop.
- Not a Planner. Round-robin model picker substitutes for a Planner in
  v0. The Planner role is deferred to v0.2.
- Not authoritative. Wall records and aggregator recommendations carry
  the standard receipt statement implicitly; nothing the loop emits
  certifies anything.

## Try it (60 sec)

Smoke-test against a local gateway:

```bash
source ~/projects/indigenomics-ai-gateway/.env.telus
mkdir -p ~/overnight-jam-2026-05-26/smoke
python3 scripts/jam/overnight_loop.py run \
  --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \
  --gateway http://localhost:8000 --team-key "$DOGFOOD_TEAM_KEY" \
  --persistent-root ~/overnight-jam-2026-05-26/smoke \
  --models telus-gemma \
  --specs flow-funding-frontier-map \
  --max-rounds 2 \
  --time-budget-hours 0.1 \
  --aggregate-every 1 \
  --inter-round-pause-seconds 1 \
  --builder-mode telus
```

A real overnight invocation (full 6-hour budget):

```bash
source ~/projects/indigenomics-ai-gateway/.env.telus
python3 scripts/jam/overnight_loop.py run \
  --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \
  --gateway http://localhost:8000 --team-key "$DOGFOOD_TEAM_KEY" \
  --persistent-root ~/overnight-jam-2026-05-26 \
  --models telus-qwen,telus-gemma,telus-gpt-oss \
  --max-rounds 100 \
  --time-budget-hours 6 \
  --max-telus-calls 600 \
  --aggregate-every 5 \
  --builder-mode telus
```

## Discipline

Loop-time invariants:

- All writes land under `--persistent-root` (enforced via
  `ensure_path_within`).
- No git mutations from inside the loop process.
- Credential regex scan after every round; first hit halts hard.
- HALT files are tombstones; the loop refuses to restart with stale
  halts present unless `--ignore-stale-halts` is passed.
- Sentinel `STOP` is checked at every round boundary AND before round
  1 (refuses to start if pre-set).

## Refusal-as-record

- Reviewer can halt publish at stage 6.5 (mesh-mode). Recorded as
  "doesn't fit yet," not failure.
- Model refusal at the drafting stage (`{"refusal": "..."}`) is
  recorded; no retry-past-rejection.
- Gateway 5xx during a round → that round records its outcome and the
  loop continues to the next.

## Observable surface

What the operator sees in the morning:

- `overnight-master-log.jsonl` — append-only log of every round +
  safety event
- `aggregator/recommendations-after-round-NNNN.md` — patterns across
  rounds
- `wall/witness-records/*.md` — what got published
- `rounds/round-NNNN-HHMMSS/<spec-id>/<run-id>/result.json` +
  `reviewer-findings.json` — per-round per-spec detail
- Any `HALT-*.txt` files — tombstones from halts (none = clean run)

## Files

- `../../scripts/jam/overnight_loop.py` — main CLI
- `../../scripts/jam/loop_safety.py` — write-boundary + credential
  scan helpers
- `spec-v0.md` — formal spec (TODO)

## Boundary

Validated lane = bounded autonomous orchestration across (spec × model)
rounds, with loop-time safety rails (write-boundary, credential scan,
sentinel STOP, stale-halt refusal) and mesh-mode reviewer gating. NOT
sandboxed code execution, NOT git-aware, NOT a Planner, NOT
authoritative. The persistent root records what the loop attempted and
what each layer refused.
