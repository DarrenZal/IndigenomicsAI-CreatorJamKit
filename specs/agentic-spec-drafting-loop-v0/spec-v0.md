---
doc_id: indigenomics.jam.specs.agentic-spec-drafting-loop-v0.spec
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
area: agentic-pipeline
last_updated: 2026-05-25
---

# Agentic Spec Drafting Loop — Spec v0

## Invitation

Wire Prompts 1, 2, 4 from
[`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../../participant-agent-context/PROMPTS_FOR_AGENTS.md)
+ the local boundary leak check + (optional) the
[`scripts/composition_engine.py`](../../scripts/composition_engine.py)
into a 5-stage loop that takes loose offerings and emits a frozen
`agentic-build-packet-v0.json` ready for a TELUS lane build attempt.

## Schema reality check

The plan that motivated this work assumed three things that diverge from
the existing kit reality:

1. **Schema location**: plan said `team-submission-v0.md` and
   `agentic-build-packet-v0.md` live in
   `~/projects/IndigenomicsAI/docs/jam/`. **Reality**: they live in the
   kit at `templates/team-submission-v0.md` +
   `templates/agentic-build-packet-v0.md`. Implementation references the
   real locations.

2. **`run-build-packet.py` already exists**: plan said it did.
   **Reality**: no such CLI exists in the kit. Stage 5 of this loop ends
   at "produce frozen build packet"; the actual build attempt lives in
   the TELUS lane preflight pipeline (see `specs/preflights/`), not in
   this loop. Stage 6 (witness drafting via Prompt 3) is downstream of
   build execution and is a separate, future CLI.

3. **Python toolchain**: plan suggested `uv` + `pyproject.toml` +
   `pytest`. **Reality**: existing kit tools are stdlib-only python3
   with no dependency manifest. To compose cleanly, this loop is
   stdlib-only Python and uses `unittest`, not `pytest`.

## Stages

| # | Stage | Adapter call | Output file |
|---|---|---|---|
| 1 | Offering ingestion | (parse only) | `1-offering.json` |
| 2 | Spec drafting (Prompt 1) | `spec-drafter` | `2-draft-spec.json` |
| 3 | Boundary checking (Prompt 2) | `boundary-checker` | `3-annotated-spec.json` |
| 3.5 | Local boundary leak check | (regex on annotated spec) | (failure logged in `run.json`) |
| 4 | Composition + facilitation (Prompt 4) | `collaboration-facilitator` | `4-collaboration-assessment.json` (only if `--composes`) |
| 5 | Freeze to build packet | (renderer) | `5-team-submission-v0.md` + `5-agentic-build-packet-v0.json` + `5-freeze-record.json` |

## Model sources

- `--model-source stub` — `StubModelAdapter` returns deterministic canned
  responses keyed by prompt name. Offline. Useful for tests + acceptance.
- `--model-source gateway` — `GatewayModelAdapter` POSTs to
  `{gateway}/v1/chat/completions` with team-scoped Bearer auth. Used
  against local `indigenomics-ai-gateway` smoke stack (or production
  with real team keys, not exercised in this v0).

Both adapters return a dict shape that the loop's stage handlers
serialize to JSON.

## Acceptance criteria

- Loop runs end-to-end with `--model-source stub` and `--confirm-freeze`
  on a markdown-with-frontmatter offering, producing all expected
  artifacts.
- Without `--confirm-freeze`, the loop stops after stage 4 and records
  `outcome: draft-only` in the audit log.
- Boundary leak check rejects annotated specs where a protected-content
  marker (e.g. `[PROTECTED]`) appears outside the `boundaries[]` array.
- Build packet output validates against `templates/agentic-build-packet-v0.md`
  schema (required fields: `schema_version`, `packet_id`, `team_spec`,
  `freeze_record`, `allowed_inputs`, `excluded_inputs`,
  `build_instructions`, `acceptance_criteria`, `review_checks`,
  `witness_record_seed`).
- Freeze record explicitly marks `frozen_by` as autonomous-loop (not
  facilitator), and the note explains this is for stub/demo only.

## What is NOT in v0

- **Stage 6 — witness drafting.** Runs downstream of build execution.
  Separate CLI: `scripts/jam/draft_witness.py` (future).
- **Build attempt execution.** Lives in the TELUS lane preflight
  pipeline, not in this loop.
- **Real facilitator freeze flow.** The `--confirm-freeze` flag is
  explicitly auto-freeze for demo purposes; a real freeze involves a
  human facilitator checklist.
- **Structured-parse of gateway responses.** v0 captures the gateway's
  raw text content; downstream parsing is the caller's responsibility.
  Stub adapter returns dicts directly.
- **Resume from a partial run.** Each `run` is a fresh run-id; no
  reverse-engineering of prior runs.

## Refusal boundaries

This loop MUST NOT:

- Auto-freeze without `--confirm-freeze`. Default is draft-only.
- Pass marker-only / protected content through the boundary leak check
  silently. Failure is a complete outcome ("doesn't fit yet") recorded
  in `run.json`, not a crash.
- Claim facilitator authority for the freeze. The freeze record's
  `frozen_by` says it's autonomous.
- Hide model source: every stage records `model_source` (stub | gateway)
  and `model_label` (e.g. `telus-qwen`) so the witness record can carry
  this provenance forward.

## Composition prompts

- The bus emits `witness_observe` messages; this loop emits build
  artifacts. Together they cover the dataflow: agents coordinate via
  bus → drafting loop produces frozen packet → TELUS lane attempts a
  build → witness record captured (separate CLI) → optionally appended
  to witness wall (Phase 3, witness-record-append-v0).
- The loop's stage 5 output (build packet) is exactly the shape the
  existing `specs/preflights/<spec>/runs/` preflight pipeline consumes.

## Refusal as complete outcome

If at any stage the loop returns a refusal-shaped output ("doesn't fit
yet"), it is recorded in `run.json` and the loop exits cleanly with
`outcome` set to a descriptive string. The loop does NOT retry, does
NOT escalate, and does NOT request additional input.

## Boundary

Validated lane = orchestration of an offering through Prompts 1, 2, 4 +
local boundary check + (optional) composition into a frozen build
packet. NOT autonomous authoring authority. NOT a substitute for human
facilitator freeze. Stub mode is offline + deterministic (not real
inference). Witness drafting is downstream of build execution.

🛶
