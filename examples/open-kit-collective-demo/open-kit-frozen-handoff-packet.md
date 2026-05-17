---
type: frozen-handoff-packet
status: frozen-for-sample-dry-run
created: 2026-05-16
author: Darren Zal
drafting_partner: AI coding partner
bundle_id: bundle:open-kit-commitments-receipts
handoff_packet_id: handoff:open-kit-commitments-receipts-v0
---

# Open Kit Frozen Handoff Packet - v0

## Packet Identity

```yaml
handoff_packet_id: handoff:open-kit-commitments-receipts-v0
bundle_id: bundle:open-kit-commitments-receipts
title: Open Kit Commitments + Receipts Internal Dry Run
status: frozen-for-sample-dry-run
default_demo_path: manual/static HTML walkthrough
optional_showcase_path: TELUS/Jupyter receipt display or schema check if already ready
```

## Purpose

Test whether a narrow Offering Integration flow can produce instructions clear enough for an agent-assisted execution attempt.

The run should show one public ecological commitment entering a simple demonstration pool, becoming visible as a commitment tuple, and mapping to a v0.2 receipt record.

This is not a production pool, not ceremony, not a certification process, and not an authority decision.

## Authorized Inputs

Use only these inputs unless a human operator explicitly adds another cleared public input:

| Input ID | Path | Purpose |
|---|---|---|
| `input:facilitator-script` | `docs/specs/open-kit-facilitator-script-v0.md` | Spoken demo boundaries and steps. |
| `input:commitment-pool-primer` | `docs/specs/commitment-pool-primer-v0.1.md` | Open Kit primer and acceptance/refusal context. |
| `input:commitment-pool-html` | `examples/commitment-pool/salish-sea-ecological-v0.1.html` | Manual/static demo artifact. |
| `input:receipt-schema-v02` | `docs/specs/witnessing-receipt-schema-v0.2.md` | Receipt schema reference. |
| `input:sample-receipt-v02` | `examples/witnessing/sample-receipt-v0.2.json` | Schema-shaped sample receipt. |
| `input:receipt-json-schema-v02` | `examples/witnessing/witnessing-receipt-v0.2.schema.json` | Optional validation reference. |

## Non-Inputs

Do not use or request:

- cultural, linguistic, ceremonial, Nation-specific, participant-private, or protected research material
- authority-bound content that requires steward, community, Nation, or ceremony review
- participant private prompts, private files, or unreviewed participant data
- production pool credentials or deployment secrets
- TELUS/Jupyter access as a required condition
- gateway/token UI, Waka bridge, Knowledge commons backend, or full multi-witness runtime

If any protected or authority-bound content appears, stop the run and record `review_required`. Do not send it into AI for checking.

## Builder Agent Task

The builder agent should attempt the frozen packet using the authorized inputs.

Expected builder behavior:

1. Read the authorized inputs.
2. Confirm the default manual/static path is understandable.
3. If opening or rendering is available, attempt the HTML demo path.
4. Identify the visible commitment tuple and receipt-related fields.
5. Compare the visible receipt-related fields to the v0.2 sample/schema at a practical field level.
6. Record what passed, what was partial, what failed, what was refused, and what was not run.
7. Do not expand the demo scope.
8. Do not build a new agent framework.
9. Do not process protected or authority-bound content.
10. Do not repair schema mismatches, hashes, validation flags, or HTML behavior during this dry run. Record them as findings only.

Unless a human operator explicitly asks for code changes, this run should produce notes, not edits.

## Reviewer / Evaluator Task

The reviewer/evaluator checks the builder output against acceptance criteria and refusal boundaries.

The reviewer should not judge cultural legitimacy, community authority, or ceremony fit. If such review is needed, route it to the appropriate human or steward review path.

## Witness / Receipt Task

The witness/receipt step records what happened:

- packet frozen
- builder attempt started
- builder attempt outcome
- reviewer/evaluator outcome
- refusal or stop condition, if any
- final rollup

The receipt records the run. It does not establish legitimacy, authority, certification, or readiness for reuse.

## Acceptance Criteria

| ID | Criterion | Check Method |
|---|---|---|
| `AC1` | The authorized files are enough to understand and run the manual/static Open Kit demo. | file and instruction review |
| `AC2` | The commitment-pool demo can show a public commitment tuple. | HTML/manual observation, or documented fallback if not run |
| `AC3` | The receipt display or sample receipt maps clearly enough to v0.2 fields for a demo. Field checks may be `partial` if HTML is v0.2-style but not validated against JSON Schema. | manual field check or schema validation |
| `AC4` | The run clearly states that receipts do not establish legitimacy, authority, certification, or readiness for reuse. | text check |
| `AC5` | TELUS/Jupyter is framed as optional, and manual witnessing remains valid. | text check |
| `AC6` | The final output names pass, partial, fail, refused, and not-run states honestly. | reviewer check |

## Refusal Boundaries

| ID | Boundary | Required Action |
|---|---|---|
| `RF1` | Protected or authority-bound material appears. | Stop and record `review_required`; do not process with AI. |
| `RF2` | The run is framed as legitimacy, authority, certification, or readiness for reuse. | Stop and repair language. |
| `RF3` | The demo is framed as a production pool, monitoring program, or economic deployment. | Stop and repair language. |
| `RF4` | TELUS/Jupyter availability is treated as a condition for success. | Stop and return to the manual/static path. |
| `RF5` | The task expands into framework selection, gateway design, Waka bridge, or full multi-agent architecture. | Stop and defer to a later offering review. |

## Expected Output From Agent Dry Run

Use this shape for the builder or reviewer notes:

Use evidence from existing files only. If a mapping is inferred rather than directly shown, list that part as `partial`, not `pass`.

```yaml
packet_id: handoff:open-kit-commitments-receipts-v0
role: builder | reviewer_evaluator | witness_receipt
run_date:
artifact_refs_used:
  - docs/specs/open-kit-facilitator-script-v0.md
  - docs/specs/commitment-pool-primer-v0.1.md
  - examples/commitment-pool/salish-sea-ecological-v0.1.html
  - docs/specs/witnessing-receipt-schema-v0.2.md
  - examples/witnessing/sample-receipt-v0.2.json
acceptance_matrix:
  AC1:
    status: pass | partial | fail | refused | not_run
    evidence:
  AC2:
    status:
    evidence:
  AC3:
    status:
    evidence:
  AC4:
    status:
    evidence:
  AC5:
    status:
    evidence:
  AC6:
    status:
    evidence:
refusal_matrix:
  RF1:
    status: honored | triggered | unclear
    evidence:
  RF2:
    status:
    evidence:
  RF3:
    status:
    evidence:
  RF4:
    status:
    evidence:
  RF5:
    status:
    evidence:
receipt_event_log:
  - event_id:
    event_type: packet_frozen | builder_attempt | reviewer_evaluation | witness_rollup | stop_condition
    summary:
    status:
open_questions:
recommended_repairs:
```

## Receipt Events

| Event ID | Event Type | Trigger | Minimum Body |
|---|---|---|---|
| `receipt:packet-frozen-open-kit-v0` | `packet_frozen` | This packet is selected for the dry run. | packet id, bundle id, authorized inputs, refusal boundaries |
| `receipt:builder-attempt-open-kit-v0` | `builder_attempt` | Builder agent attempts the packet. | inputs used, actions attempted, outcome |
| `receipt:reviewer-evaluation-open-kit-v0` | `reviewer_evaluation` | Reviewer checks acceptance/refusal matrix. | AC/RF statuses and evidence |
| `receipt:witness-rollup-open-kit-v0` | `witness_rollup` | Final rehearsal readout. | what happened, what fit, what was partial, what was refused/not run, repairs |

## Final Boundary

AI execution is a witnessed rendering attempt. It is not proof that the bundle is legitimate, authoritative, complete, or ready for reuse.
