---
type: template
status: v0-manual-first
created: 2026-05-16
author: Darren Zal
drafting_partner: AI coding partner
composes_with:
  - spec-fragment-wrapper-v0.md
  - jam-witness-ceremony-v0.md
  - witnessing-receipt-schema-v0.2.md
---

# Jam Offering Integration Report - v0

**Purpose:** Run a human-facilitated Offering Integration Session during the Creator Jam.

This report helps a group turn many heterogeneous contributions into one or more candidate bundles for final witnessed execution. It is not an automation layer. It is a facilitator document.

The Jam is a place to learn together and build together. People bring offerings: ideas, sketches, prompts, code, practices, commitments, refusals, and questions. Some offerings will fit together into shared bundles; some will not fit yet and should be preserved with care. The goal is not to force one system, but to make contribution, consent, attribution, reciprocity, repair, and next commitments more visible.

## How To Use This In The Room

1. Wrap incoming contributions with `spec-fragment-wrapper-v0.md`.
2. Group fragments by purpose, dependency, and permission fit.
3. Name candidate bundles.
4. Record what fits, what conflicts, what needs review, and what should remain separate.
5. Freeze one or two bundles for final ceremony execution.
6. Preserve unresolved fragments respectfully. Do not force a mega-spec.

## Report Metadata

```yaml
report_id: jam-integration:<date>-<short-slug>
event: Indigenomics Creator Jam
offering_integration_session_date:
facilitator:
operators:
participants_or_teams:
source_workspace:
final_ceremony_date:
```

## 1. Fragment Inventory

| Fragment ID | Title | Type | Contributor(s) | Artifact Ref | Review State | Fit State | Notes |
|---|---|---|---|---|---|---|---|
| `frag:` |  | vision/spec/code/etc. |  | path/url/receipt | not_required/pending/etc. | candidate/included/etc. |  |

Facilitator check:

- Are all participant contributions represented?
- Are protected or authority-bound fragments marked before any AI use?
- Are prior receipts or witness records linked where available?

## 2. Candidate Bundles

| Bundle ID | Title | Purpose | Candidate Fragments | Execution Mode | Status | Notes |
|---|---|---|---|---|---|---|
| `bundle:` |  |  | `frag:`, `frag:` | authoring_only/agent_build/render/review_only | ready/partial/blocked/deferred |  |

Execution modes:

- `authoring_only`: bundle is valuable but not sent to AI for building.
- `agent_build`: builder agent may attempt implementation or generation.
- `render`: existing prototype or artifact is rendered/witnessed.
- `review_only`: bundle is held for human/steward review.

## 3. Permission Envelope

For each candidate bundle, record the most restrictive applicable permission. Do not average permissions.

| Bundle ID | Transparency Tier | Sovereignty Class | License/IP | FPIC/TK/OCAP/CARE Notes | AI Use Allowed? | Public Rendering Allowed? | Basis |
|---|---|---|---|---|---|---|---|
| `bundle:` | T1/T2/T3/T4 | public/community/nation_specific/private |  |  | yes/no/review_required | yes/no/review_required |  |

Rule of thumb:

- Unknown permission means not cleared.
- Review-required means not sent to AI.
- Contributor openness does not override Nation/community authority.
- AI execution is a witnessed rendering attempt, not a legitimacy decision.

## 4. Conflict / Non-Fit Table

Use this table to make conflict and non-fit visible without treating it as failure.

| ID | Fragment(s) / Bundle | Issue Type | Description | Severity | Proposed Repair | Owner / Review Route | Status |
|---|---|---|---|---|---|---|---|
| `obs:` |  | conflict/missing/permission/refusal/authority/unsafe/timeline/attribution/runnable_status |  | concern/blocking/non_fit |  |  | open/resolved/deferred |

Common issue types:

- conflicting goals
- incompatible permissions
- missing acceptance criteria
- unclear authority
- unsafe or protected content
- impossible timeline
- unresolved attribution
- contradictory refusal logs
- non-runnable prototype
- optional TELUS/Jupyter showcase path unclear

## 5. Authority Or Steward Review Queue

| Review ID | Fragment / Bundle | Routed To | Why Review Is Needed | Material Sent To AI? | Needed Before | Status | Decision / Notes |
|---|---|---|---|---|---|---|---|
| `review:` |  | contributor/steward/Carol Anne/Pravin/operator/analyst |  | no | composition/final ceremony/post-Jam | pending/approved/refused/outside_authority |  |

Hard rule: protected or authority-bound material is not sent into AI for checking. The system may record that review is required. It cannot compute legitimacy.

## 6. Include / Exclude / Fork / Merge Decisions

| Decision ID | Operation | Fragment(s) | Bundle ID | Decision | Reason | Decided By | Receipt / Evidence |
|---|---|---|---|---|---|---|---|
| `dec:` | include/exclude/fork/merge/link_dependency/refine_criteria/quarantine/request_review/lift_to_handoff/withdraw/tombstone |  |  |  |  |  |  |

Decision guidance:

- `include`: fragment fits the bundle as-is or with named repair.
- `exclude`: fragment does not fit this bundle; preserve with reason.
- `fork`: create a separate bundle rather than force fit.
- `merge`: combine fragments after compatibility and permission review.
- `quarantine`: preserve but do not process or render.
- `lift_to_handoff`: bundle is ready for AI execution packet.
- `withdraw`: contributor removed active permission.
- `tombstone`: derived output is stale because a source changed or withdrew.

## 7. Selected Bundle(s) For Final Ceremony

| Selected Bundle | Why This Bundle | Handoff Packet Ref | Acceptance Matrix Ready? | Refusal Matrix Ready? | Receipt Plan Ready? | Risks To Name Aloud |
|---|---|---|---|---|---|---|
| `bundle:` |  |  | yes/no | yes/no | yes/no |  |

Ceremony readiness means:

- purpose is clear
- inputs are authorized
- acceptance criteria are evaluable or marked not evaluable
- refusal boundaries are explicit
- any AI/TELUS/Jupyter showcase path is ready, or the bundle can be witnessed manually without treating runtime failure as bundle failure
- protected material is excluded or held for human/steward review
- the final witness surface can show pass/fail/partial/refused honestly

## 8. Unresolved Fragments Preserved For Later

| Fragment ID | Why Unresolved | Preservation Action | Owner | Next Review Moment |
|---|---|---|---|---|
| `frag:` |  | preserve/protect/defer/tombstone |  | post-Jam/Sept 26/other |

Preservation actions:

- `preserve`: keep for future composition.
- `protect`: keep out of AI/public rendering.
- `defer`: revisit after missing dependency or authority decision.
- `tombstone`: mark previous derived uses as stale.

## 9. Frozen Handoff Packet Summary

Use this only for bundles selected for execution.

```yaml
handoff_packet_id:
bundle_id:
title:
vision:
inputs:
  - authorized input ids only
acceptance_criteria:
  - id:
    statement:
    method:
refusal_log:
  - id:
    constraint:
    check_stage:
    authority:
attribution_lineage:
  - fragment ids, contributors, sources, prior receipts
execution_runtime:
  default_demo_path: manual/static rendering, workshop facilitation, or other non-blocking path
  optional_showcase_path: TELUS-hosted model/resource, TELUS/Jupyter notebook, or none
  fallback: manual review or narrower witnessed attempt
  comparison_only: Claude Code or other non-default tools, if explicitly used for comparison
jupyter_or_deployment_target:
receipt_plan:
  step_receipts: yes/no/manual
  master_receipt: yes/no/manual
```

## 10. Lifecycle Record

| Lifecycle Stage | Evidence / Link | Status | Notes |
|---|---|---|---|
| Draft contribution |  | complete/partial/missing |  |
| Wrapped fragment |  | complete/partial/missing |  |
| Offering integration attempt |  | complete/partial/missing |  |
| Candidate bundle |  | ready/partial/blocked/deferred |  |
| Frozen handoff packet |  | ready/partial/blocked/deferred |  |
| Execution attempt |  | pass/fail/partial/refused/not_run |  |
| Review / refusal / failure |  | complete/partial/missing |  |
| Final receipt |  | emitted/manual/missing |  |
| Withdrawal / tombstone |  | none/active/pending |  |

## 11. Closing Summary For Facilitator

Use this as the spoken summary before final ceremony:

```text
The Offering Integration Session reviewed <N> fragments.
We formed <N> candidate bundles.
We selected <N> bundle(s) for witnessed execution.
We preserved <N> unresolved or protected fragments.
The main reasons for non-fit were: <reasons>.
The execution attempt should be received as a witnessed rendering, not as proof of legitimacy.
Any authority-bound material remains with the named human or steward review path.
```
