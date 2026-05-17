---
doc_kind: workshop-reference
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Common Spec Fields

These fields are candidates for shared schema fragments across the Creator Jam specs. They are not final. Use them to test whether specs can compose without erasing local meaning.

## Boundary Fields

| Field | Suggested Values | Notes |
| --- | --- | --- |
| `visibility_tier` | public_sample, public_approved, local_only, private, protected, do_not_display | Governs display and sharing. |
| `permission_state` | unknown, draft, approved_for_review, approved_for_ai_use, approved_for_public_display, withdrawn, refused | Consent is use-specific, not global. |
| `do_not_compute` | true, false | If true, exclude from indexing, summarization, routing, embedding, and AI processing. |
| `sensitive_location_flag` | true, false | If true, reduce precision or omit location from public output. |
| `intended_use` | review, public_story, build_attempt, risk_packet, funding_discussion, learning_summary | Prevents reuse drift. |

## Review Fields

| Field | Suggested Values | Notes |
| --- | --- | --- |
| `review_state` | unreviewed, needs_review, reviewed, contested, stale, blocked, withdrawn | Should travel with records across specs. |
| `reviewer` | string or role | Can be a role if naming a person is inappropriate. |
| `review_date` | ISO date | Useful for freshness and withdrawal propagation. |
| `repair_path` | list | Next actions, not automatic fixes. |
| `limitations` | list | Public-facing constraints and uncertainty. |

## Evidence Fields

| Field | Suggested Values | Notes |
| --- | --- | --- |
| `evidence_pointer` | URI, file path, record id, or redacted pointer | Points without copying protected content. |
| `evidence_type` | document, observation, sensor_reading, witness_record, receipt, claim, review_note | Helps freshness and review logic. |
| `evidence_date` | ISO date or time window | Used for freshness checks. |
| `evidence_visibility` | public, local_only, private, protected | Separate from the claim or receipt visibility. |
| `confidence` | low, medium, high, unknown | Describes evidence confidence, not human legitimacy. |

## Witness And Receipt Fields

| Field | Suggested Values | Notes |
| --- | --- | --- |
| `witness_record_id` | string | Lets multiple witnesses stack without producing a score. |
| `witness_type` | human_review, participant_receipt, facilitator_note, sensor_observation, ai_assisted_review | Names how something was witnessed. |
| `receipt_id` | string | Records what happened. |
| `receipt_policy` | no_receipt, private_receipt, role_only_public, public_sample, public_approved | Controls public display. |
| `display_approval` | true, false, role_only, pending | Required for receipt wall outputs. |

## Place And Routing Fields

| Field | Suggested Values | Notes |
| --- | --- | --- |
| `bioregion_uri` | URI or local id | Prefer coarse or consent-approved place references. |
| `area_of_interest` | string | Can be fictional in samples. |
| `routing_tags` | list | Used by commitment pool and flow funding specs. |
| `timeframe` | ISO date, range, or descriptive window | Needed for commitments, risk, and evidence freshness. |
| `capacity` | number, range, unknown, not_applicable | Prevents over-routing. |

## Composition Rules

- If two records disagree on `visibility_tier`, use the more restrictive one unless a reviewer approves a projection.
- If any source has `do_not_compute: true`, the composed output must exclude that source from AI, routing, indexing, and summarization.
- If a record lacks `intended_use`, do not reuse it for public display, risk, funding, or learning summaries.
- If evidence is private, the composed output may cite a redacted pointer but must not reveal the protected content.
- If a composition changes the speech act, such as dream to commitment or citation to verified claim, it needs an explicit transition record using `templates/speech-act-transition.md`.

## Tomorrow Question

Which of these fields are truly common, and which are only superficially similar across specs?
