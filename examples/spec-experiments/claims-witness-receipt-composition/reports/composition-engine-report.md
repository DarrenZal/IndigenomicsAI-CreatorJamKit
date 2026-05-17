---
doc_kind: composition-engine-report
status: generated
visibility: public_sample
last_updated: 2026-05-17
---

# Composition Engine Diagnostic Report

Fixture: `claims-witness-receipt-composition-public-sample-v0.1`
Engine: `Creator Jam Composition Engine Prototype` `0.1.1`

This report is diagnostic output for human review. It is not a verdict, score, approval, authority grant, or display approval.

## Composition Attempt


## Source Records

| Record | Speech Act | Explicit Or Inferred | Visibility | Permission | do_not_compute |
| --- | --- | --- | --- | --- | --- |
| `evidence:CWRC-001` | `evidence_pointer` | `` | `public_sample` | `approved_for_review` | `false` |
| `evidence:CWRC-002` | `evidence_pointer` | `` | `local_only` | `approved_for_review` | `false` |
| `evidence:CWRC-003` | `evidence_pointer` | `` | `do_not_display` | `refused` | `true` |
| `claim:CWRC-001` | `claim` | `` | `public_sample` | `approved_for_review` | `false` |
| `witness:CWRC-001` | `witness` | `` | `public_sample` | `approved_for_review` | `` |
| `witness:CWRC-002` | `witness` | `` | `public_sample` | `approved_for_review` | `` |
| `receipt:CWRC-001` | `reviewer_evaluation` | `` | `public_sample` | `approved_for_review` | `` |

## Speech-Act Transitions

| Transition | From | To | Disposition | Result | AI Receipt | Authority Record | Contributor Consent | Explicit Contributor Authority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `transition:CWRC-001` | `evidence_pointer` | `claim` | `approved_for_fixture` | `transitioned_with_limits` | `true` | `false` | `false` | `false` |
| `transition:CWRC-002` | `witness_record` | `story_candidate` | `review_required` | `review_required` | `true` | `false` | `false` | `false` |

## Hard Checks

| Check | Status | Detail |
| --- | --- | --- |
| `source_records_explicit_or_inferred` | `warn` | Missing explicit_or_inferred. |
| `transition_ai_use_receipts` | `ok` | All transitions include AI-use receipts. |
| `derived_from_transitions` | `ok` | Composed outputs point to known transition IDs. |
| `do_not_compute_exclusions` | `ok` | do_not_compute source records are represented as excluded records. |
| `speech_act_authority_markers` | `ok` | Load-bearing speech-act transitions carry authority markers. |

## Blocked Or Returned Items

| Transition | Reason | Next Action |
| --- | --- | --- |
| `transition:CWRC-002` | display_approval is pending; do_not_show_externally is true; witness records are reviewer/software receipts only; evidence:CWRC-003 is excluded and cannot be used as story support | Display reviewer must explicitly approve or return the candidate before any external display. |

## Excluded Records

| Record | Reason | Prohibited Actions |
| --- | --- | --- |
| `evidence:CWRC-003` | permission_state refused, do_not_compute true, evidence_visibility private, and no display approval |  |

## Coherence Vector

These states are preserved from the fixture. The v0.1.x engine does not independently validate coherence-vector claims.

| Dimension | State | Note |
| --- | --- | --- |
|  |  | No fixture-authored coherence vector was found. |

## Not Established


## Not Run


## Human Review Prompt

Review the trace for authority gaps, boundary laundering, category drift, missing excluded records, and whether blocked outputs are explained as clearly as composed outputs.
