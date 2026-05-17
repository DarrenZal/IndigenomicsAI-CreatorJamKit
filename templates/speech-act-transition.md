---
doc_kind: template
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Speech Act Transition

Use this when a record crosses from one kind of act to another. The transition is the review point that prevents category drift.

Examples:

- citation -> claim
- observation -> attestation
- dream -> commitment
- witness record -> attribution
- receipt -> public story
- route diagnostic -> funding discussion

## Boundary

A transition record does not create consent, authority, legitimacy, certification, eligibility, underwriting confidence, or cultural fit.

If a transition uses the word `witness`, mark whether it is a software receipt, human reviewer note, participant acknowledgement, or another limited record. Do not treat a software witness record as ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority.

## Quick Fill

```yaml
transition_id: transition:<short-slug>
from_speech_act: citation | observation | dream | offer | need | promise | refusal | evidence_pointer | witness_record | receipt | route_diagnostic | allocation_record | other
to_speech_act: claim | attestation | commitment | attribution | public_story | funding_discussion | risk_packet | learning_summary | other

source_record:
  id:
  title:
  visibility_tier: public_sample | public_approved | local_only | private | protected | do_not_display
  evidence_visibility: public | local_only | private | protected | not_applicable
  permission_state: unknown | draft | approved_for_review | approved_for_ai_use | approved_for_public_display | withdrawn | refused
  do_not_compute: true | false

target_record:
  id:
  intended_use:
  target_visibility_tier:
  public_display_requested: true | false
  ai_use_requested: true | false

transition_review:
  composition_shape: direct | adapter_needed | partial_overlap | no_shared_interface | unknown
  composition_disposition: approved_for_fixture | review_required | blocked | non_composable | preserve_separate
  transition_reviewer:
    reviewer_id:
    reviewer_type: facilitator | human_reviewer | sample_steward | technical_reviewer | display_reviewer | other
  review_date:
  transition_reason:

boundary_obstructions:
  - # what blocks or limits this transition

not_established:
  - # what the transition must not be read as proving

allowed_projection:
  summary:
  allowed_fields:
    - # fields allowed into the target record
  excluded_fields:
    - # fields that must stay out

ai_use_receipt:
  ai_used: true | false
  approved_for_this_use: true | false | not_applicable
  touched_material:
    - # exactly what the assistant or model touched
  excluded_material:
    - # material not sent to AI
  output_review_state:

withdrawal_path:
  who_can_withdraw_or_correct:
  affected_surfaces:
    - # reports, receipts, public stories, indexes, summaries
  action_if_withdrawn:

result:
  status: transitioned | transitioned_with_limits | review_required | blocked | preserve_separate
  next_action:
```

## Review Questions

1. What changed when the record crossed this boundary?
2. Did the new record imply more than the source allowed?
3. Did the transition preserve `visibility_tier`, `permission_state`, `evidence_visibility`, and `do_not_compute`?
4. Is AI use approved for this exact transition?
5. What does this transition explicitly not establish?
6. Who can withdraw, correct, or narrow the transition later?

## Reviewer Types

| reviewer_type | Use |
| --- | --- |
| `facilitator` | Records bounded facilitation notes or workshop handling. |
| `human_reviewer` | Checks content, wording, evidence, or receipt interpretation. |
| `sample_steward` | Checks public-sample boundaries and fixture safety. |
| `technical_reviewer` | Checks field shape, schema, and boundary propagation. |
| `display_reviewer` | Checks whether a candidate can be shown externally. |
| `other` | Use only with a plain-language role description. |

For sample fixtures, use fictional roles only.

## Common Transition Risks

| Transition | Risk | Required Marker |
| --- | --- | --- |
| citation -> claim | A citation can look like verification. | `not_established: verified truth, legitimacy, authority` |
| observation -> attestation | A raw reading can look like reviewed evidence. | `review_state` and uncertainty limits |
| dream -> commitment | A possibility can become an obligation. | explicit consent and timeframe |
| witness record -> attribution | A software receipt can look like ceremonial witnessing or cultural authority. | limited witness type and non-authority boundary |
| receipt -> public story | A record can look like endorsement or legitimacy. | display approval and obstruction marker |
| allocation record -> route diagnostic | Private generosity can become routable finance. | allocation visibility and not-tracked reason |

## Minimal Public Text

Use this when a transition is shown publicly:

> This record changed use from `<from_speech_act>` to `<to_speech_act>` for `<intended_use>`. The transition was reviewed for the stated use only. It does not establish authority, legitimacy, certification, eligibility, or permission for other uses.

Keep the public text shorter if needed, but do not remove the `does not establish` boundary.
