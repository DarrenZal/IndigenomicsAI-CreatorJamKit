# Claims Evidence Coherence Report

Fixture: `claims-evidence-coherence-public-sample-v0.1`  
Report date: 2026-05-17  
Intended use: public workshop demo briefing that shows which fictional claims can be reused, repaired, or excluded.

## Participant Safety

This report uses fictional public-sample content only. It contains no participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material. The `do_not_compute` record is marker-only and is not summarized beyond the existence of a non-use boundary.

## Rule Assumptions

| Claim Type | Freshness Window |
|---|---:|
| descriptive | 365 days |
| commitment_status | 90 days |
| outcome | 180 days |
| impact | 365 days |
| risk | 120 days |
| eligibility | 180 days |

Public claims require an intended use, at least one evidence pointer, reviewer context, and a review date. These diagnostics do not adjudicate truth or legitimacy.

## Claim Status Summary

| Claim | Type | Status | Evidence | Reviewer | Use Decision |
|---|---|---|---|---|---|
| `claim:CER-001` | descriptive | `ready_for_use` | `evidence:CER-001`, `evidence:CER-002` | Public Sample Steward, 2026-05-12 | May be used for the named public demo briefing. |
| `claim:CER-002` | outcome | `ready_for_use` | `evidence:CER-003` | Public Sample Steward, 2026-05-01 | May be used if wording stays narrow and aggregate-only. |
| `claim:CER-003` | impact | `stale_evidence` | `evidence:CER-004` | Public Sample Steward, 2026-05-16 | Block public impact language; repair or downgrade to a question. |
| `claim:CER-004` | eligibility | `contested` | `evidence:CER-005` | Accessibility Note Checker, 2026-05-16 | Block "no barriers" wording; replace with bounded access language. |
| `claim:CER-005` | commitment_status | `do_not_compute` | `evidence:CER-006` | Public Sample Steward, 2026-05-14 | Exclude from summarization, routing, training, and public display. |

## Evidence Freshness

| Evidence | Date | Used By | Window | Age on Report Date | Freshness Result |
|---|---:|---|---:|---:|---|
| `evidence:CER-001` | 2026-05-10 | `claim:CER-001` | 365 days | 7 days | fresh |
| `evidence:CER-002` | 2026-05-12 | `claim:CER-001` | 365 days | 5 days | fresh |
| `evidence:CER-003` | 2026-04-29 | `claim:CER-002` | 180 days | 18 days | fresh |
| `evidence:CER-004` | 2024-09-15 | `claim:CER-003` | 365 days | 609 days | stale |
| `evidence:CER-005` | 2026-03-30 | `claim:CER-004` | 180 days | 48 days | fresh but conflicting |
| `evidence:CER-006` | 2026-05-14 | `claim:CER-005` | 90 days | 3 days | boundary marker only |

## Diagnostics

| Claim | Diagnostic Codes | Repair Path |
|---|---|---|
| `claim:CER-001` | `evidence_present`, `reviewer_present`, `fresh_for_descriptive_use` | No repair required for the named demo briefing use. |
| `claim:CER-002` | `aggregate_evidence_present`, `reviewer_present`, `fresh_for_outcome_use` | Keep language narrow: completed public sample workshops only; do not imply individual outcomes. |
| `claim:CER-003` | `stale_evidence`, `overbroad`, `weak_for_impact` | Replace with current, approved, aggregate impact evidence or downgrade to a question for review. |
| `claim:CER-004` | `conflicting_evidence_visible`, `overbroad`, `needs_rewording` | Name known route constraints and route accommodation questions to a human contact. |
| `claim:CER-005` | `boundary_marker_only`, `excluded_from_summary`, `excluded_from_public_display` | Preserve the non-use marker and do not inspect or reconstruct underlying content. |

## Acceptance Checks

| ID | Status | Evidence |
|---|---|---|
| `AC1` | pass | Public sample claims include evidence pointers, reviewer IDs, and review dates. |
| `AC2` | pass | `claim:CER-003` is stale against the impact freshness window. |
| `AC3` | pass | `claim:CER-004` remains visible as contested; it is not merged away. |
| `AC4` | pass | `claim:CER-005` is excluded as `do_not_compute`. |
| `AC5` | pass | The report names the public workshop demo briefing as the only supported intended use. |

## Refusal Boundaries

| Boundary | Status | Evidence |
|---|---|---|
| Do not adjudicate ultimate truth. | honored | The report assigns use-readiness diagnostics only. |
| Do not produce a legitimacy score. | honored | No score, rank, or certification appears. |
| Do not launder weak evidence into strong public language. | honored | The impact claim is blocked as stale and overbroad. |
| Do not train on raw private evidence. | honored | No raw private evidence is present; the boundary marker is marker-only. |

## Not Run

- No live evidence retrieval.
- No participant review workflow.
- No production claim registry update.
- No AI summarization over private or protected material.
