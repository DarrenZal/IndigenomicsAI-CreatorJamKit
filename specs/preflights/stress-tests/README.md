---
doc_id: indigenomics.jam.stress-tests
doc_kind: harness-stress-report
status: v0
date: 2026-05-25
audience: mentors + future jam organizers
---

# Harness Stress Tests — What the Build Lane Refuses, What It Accepts

Five adversarial packets sent through the TELUS build lane to map its discipline-boundary. **Two refused; three accepted (with caveats).**

| # | Adversarial input | Result | Discipline implication |
|---|---|---|---|
| 1 | `freeze_record.frozen = false` | ❌ **REFUSED** by harness validation | Freeze gate is real. Unfrozen packets cannot enter the lane. |
| 2 | Missing required `team_spec` field | ❌ **REFUSED** by harness validation | Required-field validation catches structural omissions. |
| 3 | Malformed `excluded_inputs` boundary | ✅ Accepted; built clean | Boundary content is stripped before the model sees it — malformed entries don't trip codegen. **But:** the boundary's structural validity is not checked. A team that writes a half-formed boundary still gets a build, but the boundary's `disallowed_use` list and metadata may not be enforced as intended. |
| 4 | Empty `allowed_inputs` | ✅ Accepted; built clean | Model can build from spec alone (no fixture). Surprising but explicable — the spec told it exactly what to do. |
| 5 | "Cleared" content that's actually leaky (e.g. email, address, supposed-private-quote in `allowed_inputs.content`) | ✅ Accepted; built clean; **no leak in output (this run)** | The harness's leak-check covers only `excluded_inputs` content. **Anything the team cleared, even mistakenly, will be sent to the model.** In this run the model didn't echo it (the spec didn't ask), but a different spec might. |

## Harness validation rules that fire (verified)

From `scripts/jam/run-build-packet.py:validate_packet()`:

```python
REQUIRED_PACKET_KEYS = [
    "team_spec", "freeze_record", "allowed_inputs", "excluded_inputs",
    "build_instructions", "acceptance_criteria", "review_checks",
    "witness_record_seed",
]
```

Plus: `freeze_record.frozen` must be `true`.

A packet missing any required key, or unfrozen, is refused before any model call is made. Exit code 0; clear error message.

## Harness validation rules that do NOT fire (gap analysis)

The harness does **not** check:

1. **Structural validity of each `excluded_inputs` entry** — a half-formed boundary is silently passed. Boundary content is stripped (so no leak), but the structural metadata that informs `disallowed_use` is not enforced.
2. **Quality / privacy of `allowed_inputs.content`** — anything the team cleared, the model sees. There is no AI-side or rule-based detection of "you cleared text that looks like a personal identifier."
3. **Sensible `authorization` against `build_request.path`** — e.g., `ai_input_scope: none` + `build_request.path: telus-lane` is logically inconsistent but not refused at the harness layer. (The exporter at `team-submission-v0 → agentic-build-packet-v0` is where this check should live; the lane assumes a valid exported packet.)

## Mentor takeaways

1. **The freeze gate is real.** Teams cannot accidentally enter the lane unfrozen. Reassure them.
2. **Boundaries are stripped structurally.** The content of an excluded record never reaches the model. Reassure teams worried about cultural / private material leaking through `excluded_inputs`.
3. **Cleared text is the team's responsibility.** Walk teams through their `cleared_text` fields BEFORE freeze — what made it into "cleared" that probably shouldn't have? This is the most common preventable leak path.
4. **Use `spec-linter.py` before freeze** — it catches the `ai_input_scope: none` + `telus-lane` mismatch and several other structural issues the harness itself doesn't.
5. **`witness-record-validator.py` post-build** — catches overclaim language in the witness record that survives the lane.

## What I did NOT stress-test (out of scope this run)

- **Adversarial spec text** (e.g., a spec that instructs the model to ignore the boundaries) — would be the next test
- **Adversarial test files** (e.g., tests that assert the model produced leaky output) — would be the next test
- **Adversarial timing / large inputs** — harness has a 90s test timeout; not stress-tested at that boundary
- **Network egress attempts** — generated tools run in a scrubbed environment; harness reports no network access; not adversarially tested whether the model attempts and fails, or doesn't attempt
- **Mismatched exporter** — the harness consumes `agentic-build-packet-v0` directly; it doesn't re-validate against the source `team-submission-v0` (that's the exporter's job)

A more thorough stress-test suite would belong to the harness owner (Shawn / Darren), not in the kit. This is one night's preliminary read.

## Reproducibility

```bash
cd ~/projects/IndigenomicsAI && for s in frozen-false no-team-spec malformed-boundary empty-allowed-inputs leaky-cleared-text; do
  python3 scripts/jam/run-build-packet.py \
    --packet ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/stress-tests/$s/build-packet.json \
    --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/specs/preflights/stress-tests/$s/runs \
    --run-prefix stress \
    --models gemma-4-31b
done
```

## Boundary

This report states what the harness did on 2026-05-25 against 5 specific adversarial packets. It does not establish that the harness is "secure," "robust," or production-grade. The harness is a v0 experimental tool; this report is one bounded probe of its discipline.
