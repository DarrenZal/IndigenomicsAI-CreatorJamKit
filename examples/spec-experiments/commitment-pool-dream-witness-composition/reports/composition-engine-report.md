---
doc_kind: composition-engine-report
status: generated
visibility: public_sample
last_updated: 2026-05-17
---

# Composition Engine Diagnostic Report

Fixture: `commitment-pool-dream-witness-composition-public-sample-v0.1`
Engine: `Creator Jam Composition Engine Prototype` `0.1.1`

This report is diagnostic output for human review. It is not a verdict, score, approval, authority grant, or display approval.

## Composition Attempt

- `attempt_id`: composition:CPDWC-001
- `purpose`: Test whether dream, offer, promise, refusal, and withdrawal records can compose into a commitment-pool reviewer receipt without category drift.
- `composition_shape`: adapter_needed
- `composition_disposition`: approved_for_fixture
- `review_date`: 2026-05-17

## Source Records

| Record | Speech Act | Explicit Or Inferred | Visibility | Permission | do_not_compute |
| --- | --- | --- | --- | --- | --- |
| `dream:CPDWC-001` | `dream` | `explicit` | `public_sample` | `approved_for_review` | `false` |
| `authorization:CPDWC-001` | `participant_authorization` | `explicit` | `public_sample` | `approved_for_review` | `false` |
| `offer:CPDWC-002` | `offer` | `explicit` | `public_sample` | `approved_for_review` | `false` |
| `promise:CPDWC-003` | `promise` | `explicit` | `public_sample` | `approved_for_review` | `false` |
| `withdrawal:CPDWC-003` | `withdrawal` | `explicit` | `public_sample` | `approved_for_review` | `false` |
| `refusal:CPDWC-004` | `refusal` | `explicit` | `boundary_marker_only` | `refused` | `true` |
| `protected-source:CPDWC-005` | `care_note` | `explicit` | `private` | `refused` | `true` |

## Speech-Act Transitions

| Transition | From | To | Disposition | Result | AI Receipt | Authority Record | Contributor Consent | Explicit Contributor Authority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `transition:CPDWC-001` | `dream` | `commitment` | `approved_for_fixture` | `transitioned_with_limits` | `true` | `true` | `false` | `true` |
| `transition:CPDWC-002` | `offer` | `commitment` | `blocked` | `blocked` | `true` | `false` | `true` | `true` |
| `transition:CPDWC-003` | `promise` | `commitment` | `approved_for_fixture` | `transitioned` | `true` | `false` | `true` | `true` |
| `transition:CPDWC-004` | `commitment` | `other` | `approved_for_fixture` | `transitioned_with_limits` | `true` | `true` | `false` | `true` |

## Hard Checks

| Check | Status | Detail |
| --- | --- | --- |
| `source_records_explicit_or_inferred` | `ok` | All source records carry explicit_or_inferred. |
| `transition_ai_use_receipts` | `ok` | All transitions include AI-use receipts. |
| `derived_from_transitions` | `ok` | Composed outputs point to known transition IDs. |
| `do_not_compute_exclusions` | `ok` | do_not_compute source records are represented as excluded records. |
| `speech_act_authority_markers` | `ok` | Load-bearing speech-act transitions carry authority markers. |

## Blocked Or Returned Items

| Transition | Reason | Next Action |
| --- | --- | --- |
| `transition:CPDWC-002` | candidate quantity exceeds routeable remaining capacity; pool acceptance would silently over-allocate the fixture pool | Return with repair path: wait for capacity, narrow quantity, or route to another pool. |

## Excluded Records

| Record | Reason | Prohibited Actions |
| --- | --- | --- |
| `protected-source:CPDWC-005` | permission_state refused; visibility_tier private; do_not_compute true; share_policy protected_private_no_ai_no_public_route; standing refusal applies | summarize underlying content; infer commitment; route into pool; embed or index; train on; display |
| `refusal:CPDWC-004` | active refusal; do_not_compute true | convert refusal to backlog item; search for missing details; treat refusal as capacity |

## Coherence Vector

These states are preserved from the fixture. The v0.1.x engine does not independently validate coherence-vector claims.

| Dimension | State | Note |
| --- | --- | --- |
| `logical_coherence` | `holds_for_fixture` | Capacity arithmetic is explicit and no accepted record exceeds routeable capacity. |
| `epistemic_coherence` | `holds_for_fixture` | Every composed output cites source records and transition IDs. |
| `normative_coherence` | `holds_with_limits` | Commitments enter only through contributor authority; returned offers are not treated as lower value. |
| `relational_cultural_coherence` | `holds_for_fixture` | Witness language is bounded to reviewer/software receipts and refusal markers are preserved. |
| `temporal_coherence` | `holds_with_limits` | Time windows are explicit; post-acceptance withdrawal changes capacity before the commitment window begins. |

## Not Established

- real-world commitment
- funding eligibility
- authority
- legitimacy
- certification
- cultural fit
- ceremonial witnessing
- permission for other uses

## Not Run

- live pool update
- real commitment routing
- payment, grant, or allocation execution
- participant or community review workflow
- public receipt wall export
- AI processing of private or protected material

## Human Review Prompt

Review the trace for authority gaps, boundary laundering, category drift, missing excluded records, and whether blocked outputs are explained as clearly as composed outputs.
