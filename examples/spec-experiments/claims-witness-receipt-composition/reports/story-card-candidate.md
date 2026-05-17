---
doc_kind: story-card-candidate
status: draft
visibility_tier: do_not_display
display_approval: pending
do_not_show_externally: true
created_at: 2026-05-17
source_fixture: ../fixtures/claims-witness-receipt-fixture.json
derived_from_transitions:
  - "transition:CWRC-002"
withdrawal_path: "A fictional display reviewer or sample steward can withdraw or narrow this candidate; remove it from reports, receipt wall drafts, indexes, and summaries."
---

# Story Card Candidate: Riverbend Commons Sample Garden Sessions

Display gate: `display_approval: pending` and `do_not_show_externally: true`.

This is an internal display-review candidate only. It is not a public-ready story card and must not be shown externally.

## Candidate Summary

A fictional role-only reviewer receipt says the narrow claim `claim:CWRC-001` was checked against aggregate public-sample evidence for the worked composition reference.

## Derived From

| Source | Role |
|---|---|
| `transition:CWRC-002` | Speech-act transition from `witness_record` to `story_candidate`. |
| `claim:CWRC-001` | Narrow public-sample claim about two fictional demo garden sessions. |
| `witness:CWRC-001` | Human-review witness record; software/reviewer receipt only. |
| `receipt:CWRC-001` | Reviewer-evaluation receipt with display approval pending. |

`derived_from_transitions`: [`transition:CWRC-002`]

## Excluded Source

`evidence:CWRC-003` is excluded from this candidate. It has `permission_state: refused`, `do_not_compute: true`, `evidence_visibility: private`, and no display approval. It may be named only as an exclusion marker; its underlying content must not be summarized, inferred, routed, indexed, trained on, or displayed.

## Boundary

This candidate does not establish:

- authority
- legitimacy
- certification
- cultural fit
- readiness for reuse
- permission for other uses

The witness record is a software/reviewer receipt only. It is not ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority.

## AI-Use Receipt

| Field | Value |
|---|---|
| `receipt_id` | `ai-use:CWRC-story-candidate-001` |
| `ai_used` | `true` |
| `approved_for_this_use` | `true` |
| `touched_material` | Fictional public-sample fixture fields, local public-sample specs and templates, role-only reviewer objects. |
| `excluded_material` | Private evidence, protected content, cultural or ceremonial material, and the underlying content for `evidence:CWRC-003`. |
| `output_review_state` | `pending_display_review` |

## Withdrawal Path

A fictional display reviewer or sample steward can withdraw, narrow, or return this candidate. If withdrawn, remove it from `story-card-candidate.md`, the composition report, receipt wall drafts, search indexes, and any summaries derived from this fixture.
