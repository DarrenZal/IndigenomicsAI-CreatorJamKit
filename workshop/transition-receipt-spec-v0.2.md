---
doc_kind: workshop-spec
status: draft
visibility: public_sample
last_updated: 2026-05-18
---

# Transition Receipt Spec v0.2

This spec adapts the Content Addressable Transformation receipt pattern to Creator Jam speech-act transitions.

It is not a Waka interop spec, not a Claims Engine adapter, not a production anchoring design, and not approval to process real participant material. Use only fictional, public-sample, or explicitly approved material.

## Core Rule

Receipts record, not authorize.

A transition receipt records that a reviewed move happened, was blocked, was returned, or was preserved separate. It does not create consent, authority, legitimacy, certification, eligibility, underwriting confidence, public display approval, cultural fit, or permission for other uses.

AI can propose a transition receipt draft. Humans with standing authorize the transition, review the receipt, narrow it, refuse it, or preserve the source records separately.

## What This Adds

`templates/speech-act-transition.md` is the semantic checkpoint: what speech act changed, who had standing, what was allowed to move, and what was not established.

A transition receipt is the provenance checkpoint for that semantic move. It records:

- which content snapshots were used as inputs
- which output snapshot was created or withheld
- which discipline transformed or reviewed the record
- which processor, reviewer, or steward recorded the move
- which prior transition receipts this receipt depends on
- what boundary result the move produced

The pattern borrows from CAT receipts in the RegenAI/KOI stack: content-addressed input and output identifiers, processor/version metadata, timestamped receipt records, and chained provenance. The Creator Jam difference is that the important transformation is often a human-authorized speech-act move, not only a software pipeline step.

## Required Fields

```yaml
transition_receipt_id: transition-receipt:<short-slug>
receipt_schema_version: creator-jam-transition-receipt-v0.2
created_at:
visibility_tier: public_sample | public_approved | local_only | private | protected | do_not_display
intended_use:

transition_ref:
  transition_id:
  from_speech_act:
  to_speech_act:
  transition_record_path:

content_addressing:
  input_cids:
    - cid:
      record_id:
      record_role: source | authority_record | review_record | exclusion_marker | prior_output | other
      visibility_tier:
      content_mode: full_content | projection | marker_only | hash_only | withheld
  output_cid:
  output_record_id:
  output_record_path:
  output_content_mode: full_content | projection | marker_only | hash_only | withheld | not_created
  cid_method: sha256 | ipfs_cid | git_blob | placeholder_for_fixture | other
  canonicalization_note:

discipline:
  discipline_name:
  discipline_version:
  discipline_kind: speech_act_transition | display_review | claim_review | commitment_review | ai_use_review | route_diagnostic | other
  discipline_source:

processor_or_reviewer:
  actor_id:
  actor_type: contributor | facilitator | human_reviewer | sample_steward | technical_reviewer | display_reviewer | pool_steward | software_processor | ai_assistant | other
  role_scope:
  authority_state: present | missing | refused | outside_scope | not_required
  review_state: reviewed | review_required | returned | blocked | preserve_separate | not_reviewed

prior_transition_receipts:
  - transition_receipt_id:
    relation: derives_from | depends_on | supersedes | narrows | blocks | preserves_separate | corrects | other

diagnostic_result:
  composition_shape: direct | adapter_needed | partial_overlap | no_shared_interface | unknown
  composition_disposition: approved_for_fixture | review_required | blocked | non_composable | preserve_separate
  diagnostic_status: ok | warn | block
  result_state: transitioned | transitioned_with_limits | review_required | returned | blocked | preserve_separate
  boundary_obstructions:
    - 
  not_established:
    - 

ai_use_receipt:
  ai_used: true | false
  approved_for_this_use: true | false | not_applicable
  touched_material:
    - 
  excluded_material:
    - 
  output_review_state:

withdrawal_and_repair:
  who_can_withdraw_or_correct:
  affected_surfaces:
    - 
  action_if_withdrawn:
  superseding_receipt_policy:

receipt_boundary:
  public_text:
  not_authorized_by:
    - llm_confidence
    - embedding_similarity
    - graph_edge
    - receipt_existence
```

## Field Notes

| Field | Meaning | Boundary |
| --- | --- | --- |
| `input_cids` | Content identifiers for the exact input snapshots, projections, markers, or hashes used. | Do not hash or expose protected raw content if the allowed projection is marker-only or withheld. |
| `output_cid` | Content identifier for the output record, projection, or marker. | Use `not_created` when the correct outcome is blocked or preserve-separate. |
| `discipline_name` | The named review or transformation discipline applied. | A discipline name is not authority; it only names the check. |
| `discipline_version` | The version of the discipline template, checklist, schema, or review practice used; this is independent of `receipt_schema_version`. | Version drift should produce a new receipt or superseding receipt. |
| `processor_or_reviewer` | Who or what recorded the move. | Authority and review are separate fields; a reviewer can check shape without standing to authorize. |
| `prior_transition_receipts` | Chain links to earlier receipts. | A chain proves lineage only; it does not prove legitimacy or consent. |
| `diagnostic_status` | Machine-readable report status. | Use `ok`, `warn`, or `block`; do not use grading language. |

## Content Addressing Discipline

Content addressing should preserve boundaries rather than force disclosure.

Use full content CIDs only when the content is approved for that exact use. For local-only, private, protected, or `do_not_compute` sources, use the narrowest allowed projection:

- `projection`: reviewed subset of allowed fields
- `marker_only`: record id plus boundary marker, with no underlying content
- `hash_only`: hash retained by an authorized steward, not displayed in the kit
- `withheld`: source exists but cannot be identified in the receipt

If the output is blocked, returned, non-composable, or preserve-separate, the receipt should still exist. The output may be a diagnostic record, a stop condition, or `not_created`.

## Diagnostic Outcomes

| Result | When To Use | Output CID |
| --- | --- | --- |
| `transitioned` | The speech-act transition is authorized and reviewed for the exact intended use. | CID of the output record. |
| `transitioned_with_limits` | The transition is allowed only through a narrowed projection. | CID of the narrowed projection. |
| `review_required` | Shape fits, but authority, consent, evidence, or display review is incomplete. | CID of the review-required candidate. |
| `returned` | The transition needs repair before it can proceed. | CID of the returned diagnostic. |
| `blocked` | A hard boundary stops the transition. | CID of the blocked diagnostic or `not_created`. |
| `preserve_separate` | The correct result is to keep records apart. | CID of the preserve-separate receipt or `not_created`. |

## Example: Evidence Pointer To Claim

```yaml
transition_receipt_id: transition-receipt:CWRC-001-v0.2
receipt_schema_version: creator-jam-transition-receipt-v0.2
created_at: 2026-05-18
visibility_tier: public_sample
intended_use: fixture claim review

transition_ref:
  transition_id: transition:CWRC-001
  from_speech_act: evidence_pointer
  to_speech_act: claim
  transition_record_path: examples/spec-experiments/claims-witness-receipt-composition/fixtures/claims-witness-receipt-fixture.json

content_addressing:
  input_cids:
    - cid: sha256:placeholder-evidence-CWRC-001-projection
      record_id: evidence:CWRC-001
      record_role: source
      visibility_tier: public_sample
      content_mode: projection
    - cid: sha256:placeholder-evidence-CWRC-003-marker
      record_id: evidence:CWRC-003
      record_role: exclusion_marker
      visibility_tier: do_not_display
      content_mode: marker_only
  output_cid: sha256:placeholder-claim-CWRC-001
  output_record_id: claim:CWRC-001
  output_record_path: examples/spec-experiments/claims-witness-receipt-composition/fixtures/claims-witness-receipt-fixture.json
  output_content_mode: projection
  cid_method: placeholder_for_fixture
  canonicalization_note: Fixture placeholders stand in for canonical JSON hashing.

discipline:
  discipline_name: speech-act-transition
  discipline_version: v0.2
  discipline_kind: speech_act_transition
  discipline_source: templates/speech-act-transition.md

processor_or_reviewer:
  actor_id: reviewer:CWRC-human-reviewer
  actor_type: human_reviewer
  role_scope: reviews narrow fictional claim wording against allowed evidence projection
  authority_state: present
  review_state: reviewed

prior_transition_receipts: []

diagnostic_result:
  composition_shape: direct
  composition_disposition: approved_for_fixture
  diagnostic_status: ok
  result_state: transitioned_with_limits
  boundary_obstructions:
    - evidence:CWRC-003 remains marker-only and excluded
  not_established:
    - verified truth
    - authority
    - legitimacy
    - certification
    - permission for other uses

ai_use_receipt:
  ai_used: true
  approved_for_this_use: true
  touched_material:
    - public-sample fixture fields
  excluded_material:
    - underlying content for evidence:CWRC-003
  output_review_state: reviewed_for_fixture

withdrawal_and_repair:
  who_can_withdraw_or_correct: sample steward or authorized source steward
  affected_surfaces:
    - composition engine report
    - story candidate
    - display review
  action_if_withdrawn: supersede claim projection and mark downstream display candidates review_required
  superseding_receipt_policy: create a new transition receipt that supersedes this one

receipt_boundary:
  public_text: This receipt records a fixture transition from evidence pointer to claim for a narrow public-sample use. It does not establish authority, legitimacy, certification, verified truth, or permission for other uses.
  not_authorized_by:
    - llm_confidence
    - embedding_similarity
    - graph_edge
    - receipt_existence
```

## Example: Blocked Or Preserve-Separate Result

```yaml
transition_receipt_id: transition-receipt:CPUA-001-v0.2
receipt_schema_version: creator-jam-transition-receipt-v0.2
created_at: 2026-05-18
visibility_tier: public_sample
intended_use: fixture route diagnostic

transition_ref:
  transition_id: transition:CPUA-001
  from_speech_act: allocation_record
  to_speech_act: route_diagnostic
  transition_record_path: examples/spec-experiments/commitment-pool-untracked-allocation-blocked/fixtures/blocked-composition-fixture.json

content_addressing:
  input_cids:
    - cid: sha256:placeholder-allocation-marker-CPUA-001
      record_id: allocation:CPUA-001
      record_role: source
      visibility_tier: local_only
      content_mode: marker_only
  output_cid: not_created
  output_record_id: none
  output_record_path: none
  output_content_mode: not_created
  cid_method: placeholder_for_fixture
  canonicalization_note: The correct result is a blocked diagnostic, not a routeable output.

discipline:
  discipline_name: commitment-pool-route-diagnostic
  discipline_version: v0.2-style
  discipline_kind: route_diagnostic
  discipline_source: specs/commitment-pool-route-diagnostic.md

processor_or_reviewer:
  actor_id: reviewer:CPUA-pool-steward
  actor_type: pool_steward
  role_scope: records that untracked allocation must not become routeable finance
  authority_state: present
  review_state: preserve_separate

prior_transition_receipts: []

diagnostic_result:
  composition_shape: partial_overlap
  composition_disposition: preserve_separate
  diagnostic_status: block
  result_state: preserve_separate
  boundary_obstructions:
    - untracked allocation cannot be converted to routeable commitment-pool input
    - private generosity must not become public financial instruction
  not_established:
    - funding eligibility
    - route approval
    - public allocation evidence
    - permission to infer amount, funder, or recipient

ai_use_receipt:
  ai_used: false
  approved_for_this_use: not_applicable
  touched_material:
    - none
  excluded_material:
    - private allocation details
  output_review_state: reviewed_for_fixture

withdrawal_and_repair:
  who_can_withdraw_or_correct: allocation steward or original contributor
  affected_surfaces:
    - blocked composition receipt
    - composition engine report
  action_if_withdrawn: keep marker-only reference or remove downstream diagnostic if even marker display is withdrawn
  superseding_receipt_policy: create a correcting receipt with relation corrects or supersedes

receipt_boundary:
  public_text: This receipt records that the fixture transition was preserved separate. It does not establish routeability, funding eligibility, legitimacy, certification, or permission to infer private allocation details.
  not_authorized_by:
    - llm_confidence
    - embedding_similarity
    - graph_edge
    - receipt_existence
```

## Minimal Review Checklist

Before a transition receipt is accepted for a fixture:

1. Are `input_cids`, `output_cid`, `discipline_name`, `discipline_version`, `processor_or_reviewer`, and `prior_transition_receipts` present?
2. Does the receipt point to the semantic transition record?
3. Does every source record use the narrowest allowed content mode?
4. Does the receipt separate authority from review?
5. Does `diagnostic_result` use `ok`, `warn`, or `block` only?
6. Does the receipt say what it does not establish?
7. Does withdrawal or correction identify downstream affected surfaces?
8. If the transition is blocked or preserve-separate, is that result recorded as clearly as a transitioned result?

## Relationship To Adjacent Work

| Surface | Relationship | Boundary |
| --- | --- | --- |
| `templates/speech-act-transition.md` | Semantic source of truth for the speech-act move. | The receipt records lineage; the transition record carries authority and boundary review. |
| Composition engine reports | Diagnostic output can include or point to transition receipt IDs. | Engine output remains diagnostic for human review. |
| RegenAI/KOI CAT receipts | Provenance pattern for content-addressed transformations and receipt chains. | Creator Jam receipts add speech-act authority and boundary-preservation fields. |
| Claims Engine | Possible future adapter through claim/evidence/attestation receipt chains. | Do not treat this spec as adoption or operational integration. |
| Waka | Possible future comparison surface after Austin's posture is known. | Do not write Waka interop from this spec alone. |
| Indigenomics AI app | App gateway can create AI-use and transition receipts for participant-facing flows. | Gateway entry and token redemption do not create publication consent. |

## Minimal Public Text

Use this when a transition receipt must be shown in a fixture or story candidate:

> This receipt records a reviewed transition for the stated use. It records what moved, what did not move, who reviewed or authorized the move, and what was not established. It does not create authority, legitimacy, certification, public display approval, or permission for other uses.
