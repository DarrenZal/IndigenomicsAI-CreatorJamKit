---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: bioregional_insights
last_updated: 2026-05-17
---

# Living Atlas Coherence Packet

## Invitation

Build a packet that turns workshop or field contributions into reviewable atlas records while preserving permission, context, and refusal boundaries.

## What Could Be Built

- A raw contribution intake table.
- A normalized offer, need, commitment, and evidence record set.
- A steward review queue.
- A coherence packet that shows what can be published, what stays local, and what needs repair.

## Inputs

- `raw_contribution_id`
- `contribution_type`: story, offer, need, commitment, refusal, observation, evidence
- `summary`
- `source_context`
- `bioregion_uri`
- `visibility_tier`
- `review_state`
- `evidence_pointer`
- `restrictions`
- `follow_up_needed`

## Outputs

- Atlas review queue.
- Coherence summary.
- Repair path list.
- Public sample packet.
- Local-only packet.

## Acceptance Criteria

- Raw contributions are not automatically published.
- Records can remain local-only or not-for-computation.
- Public summaries require review state and source context.
- Missing evidence and stale evidence are visible.
- Repair paths name the next responsible action without exposing private content.

## Refusal Boundaries

- Do not turn workshop speech into public data by default.
- Do not compute over records marked `do_not_compute`.
- Do not publish sensitive place, culture, or governance details.
- Do not collapse contradictory contributions into a single official account.

## First Build Step

Create fictional workshop data with five raw contributions, three normalized records, two diagnostics, and one public-safe packet.

## Source Notes

Synthesized from living atlas coherence specs, Creator Jam offerings work, and bioregional mapping notes.
