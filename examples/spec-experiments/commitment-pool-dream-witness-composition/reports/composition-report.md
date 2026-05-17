# Commitment Pool Dream Witness Composition Report

Fixture: `commitment-pool-dream-witness-composition-public-sample-v0.1`
Report date: 2026-05-17
Reference: `dream / offer / promise / refusal -> commitment pool -> reviewer witness receipt`

## Participant Safety

This report uses fictional public-sample data only. It contains no participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material. The marker-only source `protected-source:CPDWC-005` is included only to show an exclusion boundary; the underlying content is not present and must not be summarized, inferred, routed, indexed, trained on, or displayed.

Witness records here are software/reviewer receipts only. They are not ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority.

## Composition Question

Can a dream-to-fulfillment board compose with a commitment-pool route diagnostic without:

- pressuring dreams into commitments
- letting a facilitator authorize a contributor's commitment
- dropping records when capacity is tight
- routing around refusals
- hiding post-acceptance withdrawal effects
- treating witness receipts as legitimacy or cultural authority

## Reviewer And Authority Objects

| Reviewer | reviewer_type | Fictional Role | Authority Scope | Boundary |
| --- | --- | --- | --- | --- |
| `contributor:CPDWC-A` | `other` | Original contributor authorizing own dream transition. | May authorize or refuse transition for own records. | Does not authorize other contributors or pool governance. |
| `reviewer:CPDWC-facilitator` | `facilitator` | Records contributor authorization and boundary notes. | May record authorization, refusal, and routing notes. | Cannot convert dreams to commitments without contributor authorization. |
| `reviewer:CPDWC-pool-steward` | `human_reviewer` | Checks pool capacity, time windows, and route rules. | May approve fixture pool acceptance or return capacity-blocked candidates. | Does not approve real-world funding, legitimacy, or authority. |
| `reviewer:CPDWC-technical` | `technical_reviewer` | Checks field composition and boundary propagation. | May check schema shape and `derived_from_transitions`. | Does not authorize speech-act transitions. |

## Pool Capacity

| Pool | Unit | Total | Accepted Before Fixture | Remaining Before Fixture | Reserve Not Routeable | Routeable Remaining Before Fixture |
| --- | --- | ---:| ---:| ---:| ---:| ---:|
| `pool:cedar-care-sprint-near-full` | volunteer_hours | 12 | 10 | 2 | 1 | 1 |

The pool is intentionally near full. This tests whether the composition records a capacity block instead of silently accepting, dropping, or ranking a candidate.

## Source Records

| Record | Speech Act | Boundary Outcome | Composition Use |
| --- | --- | --- | --- |
| `dream:CPDWC-001` | `dream` | Can remain a dream; can become one-hour candidate only with contributor authorization. | Source for `transition:CPDWC-001`. |
| `authorization:CPDWC-001` | `participant_authorization` | Authorizes only the exact one-hour fixture transition. | Authority record for `transition:CPDWC-001`. |
| `offer:CPDWC-002` | `offer` | Valid offer, but pool capacity blocks route acceptance. | Returned by `transition:CPDWC-002`. |
| `promise:CPDWC-003` | `promise` | Already-accepted fixture commitment. | Source for withdrawal propagation test. |
| `withdrawal:CPDWC-003` | `withdrawal` | Narrows accepted commitment from two hours to one hour. | Authority record for `transition:CPDWC-004`. |
| `refusal:CPDWC-004` | `refusal` | Active refusal, marker-only. | Excluded from composition. |
| `protected-source:CPDWC-005` | `care_note` | Private, refused, `do_not_compute`. | Excluded from composition; marker only. |

## Speech-Act Transitions

See `reports/speech-act-transitions.md` for the full transition details.

| Transition | Speech-Act Change | Source | Target | Disposition | Authority | Result |
| --- | --- | --- | --- | --- | --- | --- |
| `transition:CPDWC-001` | `dream -> commitment` | `dream:CPDWC-001` | `commitment-candidate:CPDWC-001` | `approved_for_fixture` | `contributor:CPDWC-A` | One-hour candidate created with limits. |
| `transition:CPDWC-002` | `offer -> commitment` | `offer:CPDWC-002` | `commitment-candidate:CPDWC-002` | `blocked` with `capacity_until_changes` reason | pool steward plus contributor offer | Returned because capacity is insufficient. |
| `transition:CPDWC-003` | `promise -> commitment` | `promise:CPDWC-003` | `accepted-commitment:CPDWC-003` | `approved_for_fixture` | pool steward for fixture record | Included to test withdrawal. |
| `transition:CPDWC-004` | `commitment -> narrowed commitment` | `accepted-commitment:CPDWC-003` | `accepted-commitment:CPDWC-003-narrowed` | `approved_for_fixture` | `contributor:CPDWC-C` | Narrows from two hours to one hour. |

## Transition Risk Callouts

| Transition | Template Risk | Required Marker In This Fixture |
| --- | --- | --- |
| `transition:CPDWC-001` | `dream -> commitment` | Contributor authority, one-hour limit, time window, and no broader obligation. |
| `transition:CPDWC-002` | offer becoming routeable commitment | Capacity block and return reason; no contributor ranking or silent drop. |
| `transition:CPDWC-003` | promise becoming accepted commitment | Fixture-only acceptance and no ceremonial witness language. |
| `transition:CPDWC-004` | accepted commitment withdrawal | Capacity effect, downstream expectation effect, and no fault language. |

## Capacity Effects

| Event | Quantity | Routeable Capacity Before | Routeable Capacity After | Handling |
| --- | ---:| ---:| ---:| --- |
| Before fixture | not applicable | 1 | 1 | Near-full pool with one routeable hour. |
| Accept `commitment-candidate:CPDWC-001` | 1 | 1 | 0 | Accepted for fixture because contributor authorized and capacity exists. |
| Return `commitment-candidate:CPDWC-002` | 3 | 0 | 0 | Returned because capacity is insufficient. |
| Narrow `accepted-commitment:CPDWC-003` | +1 restored | 0 | 1 | Capacity effect recorded after contributor withdrawal. |

The returned offer remains visible as a returned candidate with a repair path: wait for capacity, narrow quantity, or route to another pool. It is not treated as invalid or lower value.

## Excluded Source

`protected-source:CPDWC-005` and `refusal:CPDWC-004` do not meet the boundary check for composition. They have refused or marker-only permission, `do_not_compute: true`, and no approval for routing, indexing, summarization, training, or display.

Excluded means:

- no summary of underlying content
- no inference from the marker
- no route into the pool
- no claim, commitment, or capacity support
- no embedding, indexing, training, or public display

## Composed Output

The worked composition reference produces one fixture-only reviewer receipt:

| Output | composition_shape | composition_disposition | derived_from_transitions | Included Records | Excluded Records |
| --- | --- | --- | --- | --- | --- |
| `commitment-pool-composition:CPDWC-001` | `adapter_needed` | `approved_for_fixture` | `transition:CPDWC-001`, `transition:CPDWC-002`, `transition:CPDWC-003`, `transition:CPDWC-004` | `dream:CPDWC-001`, `authorization:CPDWC-001`, `offer:CPDWC-002`, `promise:CPDWC-003`, `withdrawal:CPDWC-003` | `refusal:CPDWC-004`, `protected-source:CPDWC-005` |

Candidate summary:

> Fixture-only reviewer receipt: a fictional contributor-authorized one-hour commitment entered a near-full public-sample pool, a larger offer was returned because capacity was insufficient, an already-accepted commitment was narrowed by the contributor, and refusal/private markers remained excluded.

This is not a public story card and not a real-world commitment record.

## Witness Receipts

| Witness | witness_type | Reviewer | Statement Boundary |
| --- | --- | --- | --- |
| `witness:CPDWC-001` | `human_review` | `reviewer:CPDWC-pool-steward` | Reviewed the one-hour contributor-authorized commitment candidate and capacity effect for fixture use only. |
| `witness:CPDWC-002` | `facilitator_note` | `reviewer:CPDWC-facilitator` | Recorded that contributor authorization was required and present for `transition:CPDWC-001`. |

These are reviewer/software receipts only. They do not establish ceremonial witnessing, cultural authority, legitimacy, funding eligibility, or permission for other uses.

## Coherence Vector

| Dimension | Fixture Result | Evidence |
| --- | --- | --- |
| Logical coherence | `holds_for_fixture` | Capacity arithmetic is explicit and no accepted record exceeds routeable capacity. |
| Epistemic coherence | `holds_for_fixture` | Every composed output cites source records and transition IDs. |
| Normative coherence | `holds_with_limits` | Commitments enter only through contributor authority; returned offers are not treated as lower value. |
| Relational/cultural coherence | `holds_for_fixture` | Witness language is bounded and refusal markers are preserved. |
| Temporal coherence | `holds_with_limits` | Time windows are explicit; post-acceptance withdrawal changes capacity before the commitment window begins. |

## AI-Use Receipts

| Receipt | ai_used | Scope | Excluded Material | Review State |
| --- | --- | --- | --- | --- |
| `ai-use:CPDWC-transition-001` | `false` | Dream-to-commitment transition. | Private/protected content and `protected-source:CPDWC-005`. | `reviewed_for_fixture` |
| `ai-use:CPDWC-transition-002` | `false` | Offer-to-returned-candidate transition. | Private/protected content and `protected-source:CPDWC-005`. | `reviewed_for_fixture` |
| `ai-use:CPDWC-transition-003` | `false` | Promise-to-accepted-commitment fixture transition. | Private/protected content and `protected-source:CPDWC-005`. | `reviewed_for_fixture` |
| `ai-use:CPDWC-transition-004` | `false` | Accepted-commitment narrowing transition. | Private/protected content and `protected-source:CPDWC-005`. | `reviewed_for_fixture` |

## Withdrawal Paths

| Record | Who Can Withdraw Or Correct | Action |
| --- | --- | --- |
| `commitment-candidate:CPDWC-001` | `contributor:CPDWC-A` | Mark withdrawn and restore the one hour to routeable pool capacity in fixture summaries. |
| `commitment-candidate:CPDWC-002` | `contributor:CPDWC-B` or pool steward for capacity facts | Remove from returned queue or update repair path; do not infer replacement capacity. |
| `accepted-commitment:CPDWC-003` | `contributor:CPDWC-C` | Apply `transition:CPDWC-004` and record capacity/downstream expectation effect. |
| `transition:CPDWC-004` | `contributor:CPDWC-C` or pool steward for capacity arithmetic | Restore previous accepted quantity only after contributor confirmation. |

## Acceptance Checks

| ID | Status | Evidence |
| --- | --- | --- |
| `AC1` | pass | `dream:CPDWC-001` becomes a commitment candidate only through `authorization:CPDWC-001` and `transition:CPDWC-001`. |
| `AC2` | pass | Pool capacity includes total, accepted, reserve, and routeable remaining fields. |
| `AC3` | pass | `offer:CPDWC-002` is returned because the near-full pool lacks capacity; the record is not dropped. |
| `AC4` | pass | All transitions include AI-use receipts with `ai_used: false`. |
| `AC5` | pass | Composed output includes `derived_from_transitions`. |
| `AC6` | pass | `transition:CPDWC-004` records post-acceptance withdrawal and capacity effect. |
| `AC7` | pass | Refusal and protected marker records are excluded without exposing underlying content. |

## Not Established

This fixture does not establish:

- real-world commitment
- funding eligibility
- authority
- legitimacy
- certification
- cultural fit
- ceremonial witnessing
- contributor reliability scoring
- permission for other uses

## Not Run

- No live pool update.
- No real commitment routing.
- No payment, grant, or allocation execution.
- No participant or community review workflow.
- No public receipt wall export.
- No AI processing of private or protected material.
