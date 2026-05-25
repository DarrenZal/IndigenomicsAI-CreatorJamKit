---
doc_id: indigenomics.jam.agentic-build-packet
doc_kind: spec
status: draft
date: 2026-05-20
author: Darren Zal
depends_on:
  - docs/operations/2026-05-20-gateway-agentic-system-action-plan.md
  - docs/jam/operational-kit/team-vision-spec-submission-template.md
  - docs/jam/operational-kit/tuesday-witness-record-form.md
target_jam: 2026-05-25
---

# Agentic Build Packet — v0

## Purpose

A **build packet** is the self-contained, frozen unit that an agentic build
attempt consumes. It replaces the loose, one-off micro-spec folder used by the
M1 / M1.5 / M2-lite dogfoods (a spec file, a test file, and a fixture passed as
separate command-line flags).

One packet carries everything a build attempt, a review, and a witness record
need. The same packet can be handed to the TELUS build-attempt lane, to a human
builder, or — later — to the gateway, and produce comparable results.

## Where it sits in the flow

The Creator Jam system contract is:

    offerings -> candidate team spec -> frozen build spec -> build attempt
    -> review / witness check -> canoe landing record

The build packet **is** the frozen-build-spec stage. It is produced once, from a
team's frozen submission, and then consumed unchanged by everything downstream.

## Packet contents

A packet is a JSON manifest (`build-packet.json`) plus any files it references,
together in one directory. It has eight fields.

### `team_spec`

The team's vision and what they want built — `team_name`, `site`, `vision`,
`spec`, `build_target`. Sourced from the team's submission (see
`team-vision-spec-submission-template.md`).

### `freeze_record`

Who froze the packet and when: `frozen`, `frozen_at`, `frozen_by`, and a
`facilitator_confirmed` block (boundaries reviewed, public/private status
confirmed, consent complete). A build attempt **must refuse to run** on a packet
whose `freeze_record.frozen` is not true.

### `allowed_inputs`

Data the build attempt is cleared to use — each entry has `name`, `kind`,
`note`, and inline `content`. For example, a sample of the data the tool will
process, so the model can see its shape.

### `excluded_inputs`

Marker-only records — each has `id`, `visibility: "marker-only"`, `boundary`,
and `disallowed_use`. These are named only. Their content is **not** in the
packet and is **never** passed to a build attempt. The adapter honors this and
leak-checks the build artifacts against it.

### `build_instructions`

The frozen build spec — the exact description the build works from. May be an
inline string, or `{ "path": "..." }` resolved relative to the packet directory.

### `acceptance_criteria`

`description` — a human-readable list of acceptance criteria. `test_file` — an
executable check (`name`, `language`, and either inline `content` or a `path`
relative to the packet). The test file is the smoke/acceptance run.

### `review_checks`

The checklist a reviewer — human or agent — applies to a build attempt. Plain
strings; the adapter auto-evaluates the ones it can and marks the rest
`needs-human-review`.

### `witness_record_seed`

The skeleton for the canoe-landing / witness record — `team`, `date`, the
`fields` to fill, and the `receipt_statement`. The adapter fills it from what
the build attempt actually did.

## Run flow

    build-packet.json
      -> TELUS model attempt (one single-file tool)
      -> tests / smoke run (the acceptance test, isolated)
      -> optional one repair (only if the attempt fails; concrete test feedback)
      -> build-attempt.json
      -> reviewer-findings.json
      -> canoe-landing/witness-record.md

The build attempt and the repair run in a temp directory with a scrubbed
environment and a timeout. No network, credential, or database access reaches
generated code.

## Output contract

Per build attempt (per model), in a run directory:

- `build-attempt.json` — model, attempt(s), test outcomes, the final code, and
  the finding (built clean / fixed / improved / no change / regressed / failed).
- `reviewer-findings.json` — each `review_check` evaluated (`pass` /
  `needs-human-review` / `fail`), plus the `excluded_inputs` leak check.
- `canoe-landing/witness-record.md` — the witness record, filled from
  `witness_record_seed`.

## Boundary

A build packet, a build attempt, and a witness record state what happened. They
do not establish authority, approval, certification, legitimacy, or reuse
permission. `excluded_inputs` are honored by the adapter — their content never
enters a build attempt.

## Exporting from a team submission

There are two schemas, with two jobs:

- **`team-submission-v0`** — the rich gateway / fallback submission schema,
  defined in `team-submission-v0.md`. It captures the team's words, offerings,
  boundaries, build path, authorization, and facilitator freeze.
- **`agentic-build-packet-v0`** — the lean runtime packet defined above,
  consumed by `run-build-packet.py`.

`scripts/jam/create-build-packet-from-submission.py` is the exporter
(`team-submission-v0` → `agentic-build-packet-v0`). The field-by-field mapping
and the facilitator-freeze rules are owned by `team-submission-v0.md` (its §3
mapping summary and §2 transformation boundary). The exporter refuses to
export — producing no packet — when the submission is not frozen, any
facilitator-freeze confirmation is missing, or `authorization.ai_input_scope`
does not permit an AI / TELUS runtime packet. Marker boundaries become
`excluded_inputs` — named only, marker metadata preserved, content never carried.

## v0 scope

- One tiny single-file build target; Gemma + Qwen only.
- `build_instructions` and `acceptance_criteria.test_file` may be inline content
  or a path reference.
- Adapter: `scripts/jam/run-build-packet.py`.
- Submission exporter: `scripts/jam/create-build-packet-from-submission.py`
  (`team-submission-v0` → `agentic-build-packet-v0`).
- Worked examples: `examples/jam-dogfood-m2-5/` (packet) and
  `examples/jam-dogfood-m2-6/` (submission → exported packet).

## Status

- v0 — drafted 2026-05-20.
