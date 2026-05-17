# Claims Witness Receipt Composition Report

Fixture: `claims-witness-receipt-composition-public-sample-v0.1`  
Report date: 2026-05-17  
Reference: `claims evidence -> witness record -> receipt/story candidate worked composition reference`

## Participant Safety

This report uses fictional public-sample data only. It contains no participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material. The marker-only source `evidence:CWRC-003` is included only to show an exclusion boundary; the underlying content is not present and must not be summarized, inferred, routed, indexed, trained on, or displayed.

Witness records here are software/reviewer receipts only. They are not ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority.

## Reviewer Objects

| Reviewer | reviewer_type | Fictional Role | Boundary |
|---|---|---|---|
| `reviewer:CWRC-sample-steward` | `sample_steward` | Checks sample-use boundaries. | Does not certify truth, legitimacy, consent, cultural fit, or permission for other uses. |
| `reviewer:CWRC-human-reviewer` | `human_reviewer` | Checks claim wording against evidence pointers. | Does not establish authority, legitimacy, certification, or cultural authority. |
| `reviewer:CWRC-technical-reviewer` | `technical_reviewer` | Checks field composition and boundary propagation. | Does not approve public display or certify reuse. |
| `reviewer:CWRC-facilitator` | `facilitator` | Records bounded facilitation notes. | Does not perform ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority. |
| `reviewer:CWRC-display-reviewer` | `display_reviewer` | Reviews display candidates. | Does not grant permission for other uses. |

## Source Records

| Record | Source Type | evidence_visibility | Record Visibility | Boundary Outcome | Composition Use |
|---|---|---|---|---|---|
| `evidence:CWRC-001` | aggregate evidence pointer | `public` | `public_sample` | available for narrow transition | Supports `claim:CWRC-001`. |
| `evidence:CWRC-002` | role-only review note | `local_only` | `local_only` | available as role-only context | Supports role-only witness wording. |
| `evidence:CWRC-003` | marker-only refusal boundary | `private` | `do_not_display` | blocked and excluded | May be named only as an exclusion marker. |
| `claim:CWRC-001` | outcome claim | not applicable | `public_sample` | reviewed for fixture use | Becomes the reviewed claim source for witness receipt. |
| `witness:CWRC-001` | witness record | not applicable | `public_sample` | reviewed for fixture use | Seeds the internal story candidate. |
| `receipt:CWRC-001` | receipt event | not applicable | `public_sample` | `display_approval: pending` | Linked to the candidate, not externally shown. |

Evidence visibility is intentionally separate from claim visibility. The public evidence pointer `evidence:CWRC-001` supports a public-sample claim, while local-only context `evidence:CWRC-002` is projected only as role-only context. The private marker `evidence:CWRC-003` is not projected into the claim, witness record, receipt, or story candidate.

## Speech-Act Transitions

| Transition | Speech-Act Change | Source | Target | Disposition | Reviewer | Boundary |
|---|---|---|---|---|---|---|
| `transition:CWRC-001` | `evidence -> claim` | `evidence:CWRC-001` | `claim:CWRC-001` | `transitioned_with_limits` | `technical_reviewer` | Only aggregate session-count wording may move into the claim. |
| `transition:CWRC-002` | `witness_record -> story_candidate` | `witness:CWRC-001` | `story-candidate:CWRC-001` | `review_required` | `display_reviewer` | Display remains pending; the candidate cannot be shown externally. |

### Transition Risk Callouts

These transitions map directly to `templates/speech-act-transition.md`:

| Transition | Template Risk | Required Marker In This Fixture |
|---|---|---|
| `transition:CWRC-001` | `citation -> claim` / evidence pointer becoming claim support | `not_established` excludes truth adjudication, legitimacy, authority, impact, eligibility, and reuse permission. |
| `transition:CWRC-002` | `witness record -> attribution` and `receipt -> public story` | `display_approval: pending`, `do_not_show_externally: true`, non-ceremonial witness boundary, and `not_established` markers. |

### Transition Notes

`transition:CWRC-001` changes an aggregate evidence pointer into a narrow claim. It does not adjudicate ultimate truth, create public display approval, or allow impact, eligibility, authority, legitimacy, certification, cultural fit, readiness-for-reuse, or permission-for-other-use language.

`transition:CWRC-002` changes a human-review witness record into an internal story candidate. The witness record is a reviewer/software receipt only. It does not become ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, protocol authority, certification, endorsement, or permission for external display.

## Excluded Source

`evidence:CWRC-003` does not meet the boundary check for composition. It has `permission_state: refused`, `do_not_compute: true`, `evidence_visibility: private`, and no display approval. It is excluded from the composed output and may be named only as a marker that an exclusion boundary exists.

Excluded means:

- no summary of underlying content
- no inference from the marker
- no claim support
- no story support
- no routing, indexing, embedding, training, or public display

## Composed Output

The worked composition reference produces one internal candidate:

| Candidate | Visibility | display_approval | do_not_show_externally | derived_from_transitions | Included Records | Excluded Records |
|---|---|---|---|---|---|---|
| `story-candidate:CWRC-001` | `do_not_display` | `pending` with `display_reviewer_role: display_reviewer` | `true` | `transition:CWRC-002` | `claim:CWRC-001`, `witness:CWRC-001`, `receipt:CWRC-001` | `evidence:CWRC-003` |

Candidate summary:

> Internal display-review candidate: a fictional role-only reviewer receipt says a narrow public-sample claim was checked against aggregate sample evidence.

This is not a public-ready story card. The candidate remains internal until a display reviewer explicitly changes `display_approval` and removes the external display block in a later reviewed record.

## AI-Use Receipts

| Receipt | ai_used | Scope | Excluded Material | Review State |
|---|---|---|---|---|
| `ai-use:CWRC-transition-001` | `false` | In-fixture transition from evidence to claim. | Private evidence, protected content, cultural or ceremonial material, and `evidence:CWRC-003`. | `reviewed` |
| `ai-use:CWRC-transition-002` | `false` | In-fixture transition from witness record to story candidate. | Private evidence, protected content, cultural or ceremonial material, and `evidence:CWRC-003`. | `pending_display_review` |
| `ai-use:CWRC-story-candidate-001` | `true` | Drafting this fictional public-sample story candidate from local specs and fixture fields. | Private evidence, protected content, cultural or ceremonial material, and the underlying content for `evidence:CWRC-003`. | `pending_display_review` |

## Withdrawal Paths

| Record | Who Can Withdraw Or Correct | Action |
|---|---|---|
| `claim:CWRC-001` | sample steward or human reviewer | Remove the claim from composed outputs and mark dependent transitions and story candidates withdrawn. |
| `witness:CWRC-001` | human reviewer or sample steward | Mark `witness:CWRC-001` and `transition:CWRC-002` withdrawn; remove dependent story text from display review. |
| `receipt:CWRC-001` | human reviewer, display reviewer, or sample steward | Remove the receipt from story candidate derivation and mark dependent output withdrawn. |
| `story-candidate:CWRC-001` | display reviewer or sample steward | Remove the candidate from review queues and mark all derived references withdrawn. |

## Not Established

Every public/display-facing candidate in this fixture states that it does not establish:

- authority
- legitimacy
- certification
- cultural fit
- readiness for reuse
- permission for other uses

## Not Run

- No live evidence retrieval.
- No production claim registry update.
- No participant or community review workflow.
- No public receipt wall export.
- No AI processing of private or protected material.
