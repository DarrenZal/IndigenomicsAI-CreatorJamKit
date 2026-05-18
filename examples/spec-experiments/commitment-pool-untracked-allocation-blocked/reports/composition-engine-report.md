---
doc_kind: composition-engine-report
status: generated
visibility: public_sample
last_updated: 2026-05-17
---

# Composition Engine Diagnostic Report

Fixture: `commitment-pool-untracked-allocation-blocked-public-sample-v0.1`
Engine: `Creator Jam Composition Engine Prototype` `0.1.1`

This report is diagnostic output for human review. It is not a verdict, score, approval, authority grant, or display approval.

## Composition Attempt

- `attempt_id`: composition:commitment-pool-untracked-allocation-blocked-001
- `purpose`: Test whether an untracked allocation can become a routeable commitment pool record.
- `composition_shape`: partial_overlap
- `composition_disposition`: non_composable
- `review_date`: 2026-05-17

## Source Records

| Record | Speech Act | Explicit Or Inferred | Visibility | Permission | do_not_compute |
| --- | --- | --- | --- | --- | --- |
| `allocation:care-introduction-001` | `introduction` | `explicit` | `` | `approved_for_private_receipt` | `true` |

## Speech-Act Transitions

| Transition | From | To | Disposition | Result | AI Receipt | Authority Record | Contributor Consent | Explicit Contributor Authority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `transition:allocation-to-route-diagnostic-blocked-001` | `allocation_record` | `route_diagnostic` | `non_composable` | `blocked` | `true` | `false` | `false` | `false` |

## Hard Checks

| Check | Status | Detail |
| --- | --- | --- |
| `source_records_explicit_or_inferred` | `ok` | All source records carry explicit_or_inferred. |
| `transition_ai_use_receipts` | `ok` | All transitions include AI-use receipts. |
| `derived_from_transitions` | `ok` | No composed outputs were found to check. |
| `do_not_compute_exclusions` | `ok` | do_not_compute source records are represented as excluded records. |
| `speech_act_authority_markers` | `ok` | Load-bearing speech-act transitions carry authority markers. |

## Blocked Or Returned Items

| Transition | Reason | Next Action |
| --- | --- | --- |
| `transition:allocation-to-route-diagnostic-blocked-001` | recipient hidden; amount not tracked; private notes pointer redacted; private receipt policy; do_not_route true; do_not_compute true; no consent to convert relational support into a pool commitment | Preserve as summary-only receipt. Do not route, value, infer, or search private notes. |

## Excluded Records

| Record | Reason | Prohibited Actions |
| --- | --- | --- |
| `allocation:care-introduction-001` | do_not_compute true; do_not_route true; recipient hidden; amount not tracked; private receipt policy | route into commitment pool; infer amount; infer recipient; summarize private notes; embed or index private notes; display private details |

## Coherence Vector

These states are preserved from the fixture. The v0.1.x engine does not independently validate coherence-vector claims.

| Dimension | State | Note |
| --- | --- | --- |
|  |  | No fixture-authored coherence vector was found. |

## Not Established


## Not Run


## Human Review Prompt

Review the trace for authority gaps, boundary laundering, category drift, missing excluded records, and whether blocked outputs are explained as clearly as composed outputs.
