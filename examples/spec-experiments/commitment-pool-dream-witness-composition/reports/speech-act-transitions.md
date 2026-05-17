# Commitment Pool Dream Witness Speech-Act Transitions

Fixture: `commitment-pool-dream-witness-composition-public-sample-v0.1`
Report date: 2026-05-17

## Purpose

This report isolates the speech-act transitions used by the commitment-pool dream/witness fixture. The load-bearing rule is that a transition from dream, offer, or promise into a commitment is not created by graph proximity, LLM confidence, facilitator interpretation, or pool need. It requires the right authority for the specific transition.

## Authority Rule

| Transition Type | Who Can Authorize | Who Can Record | Who Cannot Authorize Alone |
| --- | --- | --- | --- |
| `dream -> commitment` | Original contributor for the dream. | Facilitator with explicit contributor authorization. | Facilitator, technical reviewer, embedding match, LLM, graph edge, pool steward. |
| `offer -> commitment candidate` | Contributor plus pool steward for fixture routing. | Pool steward. | Capacity algorithm alone. |
| `promise -> accepted commitment` | Contributor plus pool steward for fixture routing. | Pool steward. | Public display reviewer, graph edge, LLM. |
| `accepted commitment -> narrowed commitment` | Original contributor. | Pool steward records capacity effect. | Pool steward without contributor request. |

## Transition Table

| Transition | From | To | Source | Target | Disposition | Authority | AI Used | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `transition:CPDWC-001` | `dream` | `commitment` | `dream:CPDWC-001` | `commitment-candidate:CPDWC-001` | `approved_for_fixture` | `contributor:CPDWC-A` | `false` | One-hour candidate created with limits. |
| `transition:CPDWC-002` | `offer` | `commitment` | `offer:CPDWC-002` | `commitment-candidate:CPDWC-002` | `blocked` with `capacity_until_changes` reason | `reviewer:CPDWC-pool-steward` plus contributor offer | `false` | Returned because pool has insufficient routeable capacity. |
| `transition:CPDWC-003` | `promise` | `commitment` | `promise:CPDWC-003` | `accepted-commitment:CPDWC-003` | `approved_for_fixture` | pool steward for already-accepted fixture record | `false` | Included to test post-acceptance withdrawal. |
| `transition:CPDWC-004` | `commitment` | `withdrawn_or_narrowed_commitment` | `accepted-commitment:CPDWC-003` | `accepted-commitment:CPDWC-003-narrowed` | `approved_for_fixture` | `contributor:CPDWC-C` | `false` | Commitment narrowed from two hours to one hour. |

## Transition Details

### `transition:CPDWC-001`

`dream:CPDWC-001` becomes a one-hour commitment candidate only because `contributor:CPDWC-A` authorizes that exact transition. The facilitator records the authorization. The facilitator does not create the commitment.

Allowed projection:

- issuer
- quantity
- unit
- time window
- routing tags
- target pool
- share policy

Excluded:

- broader dream language
- obligation beyond one hour
- commitments by other contributors

Not established:

- real-world commitment
- permission for other uses
- authority over other records
- legitimacy or certification

### `transition:CPDWC-002`

`offer:CPDWC-002` is structurally complete, but the pool has only one routeable hour available. The offer asks for three hours. The correct result is to return the candidate with the capacity reason visible.

The returned offer is not invalid, low value, or rejected as a contributor relationship. It simply does not fit the near-full pool at this time.

### `transition:CPDWC-003`

`promise:CPDWC-003` is an already-accepted fictional commitment included to test a later withdrawal. Its acceptance is fixture-only and does not establish real-world obligation, certification, public endorsement, or cultural authority.

### `transition:CPDWC-004`

`contributor:CPDWC-C` narrows an already-accepted commitment from two hours to one hour. This is different from withdrawing a dream. It affects:

- pool capacity summary
- accepted commitment list
- witness receipt rollup
- any downstream flow-funding edge if one is later created

The withdrawal must not be projected as fault, unreliability, or future ineligibility.

## Excluded Source Rule

`protected-source:CPDWC-005` and `refusal:CPDWC-004` remain outside the composition. They may be named only as boundary markers. No underlying content may be summarized, inferred, embedded, routed, indexed, trained on, or displayed.

## AI-Use Receipts

| Transition | ai_used | Approved For This Use | Touched Material | Excluded Material | Review State |
| --- | --- | --- | --- | --- | --- |
| `transition:CPDWC-001` | `false` | `not_applicable` | none | private/protected content, `protected-source:CPDWC-005` | `reviewed_for_fixture` |
| `transition:CPDWC-002` | `false` | `not_applicable` | none | private/protected content, `protected-source:CPDWC-005` | `reviewed_for_fixture` |
| `transition:CPDWC-003` | `false` | `not_applicable` | none | private/protected content, `protected-source:CPDWC-005` | `reviewed_for_fixture` |
| `transition:CPDWC-004` | `false` | `not_applicable` | none | private/protected content, `protected-source:CPDWC-005` | `reviewed_for_fixture` |

## Minimal Public Text

This fixture shows that a fictional dream, offer, promise, refusal, and withdrawal can be reviewed for commitment-pool composition only when contributor authority, capacity, time windows, exclusion markers, AI-use receipts, and withdrawal paths are explicit. It does not establish real-world commitment, funding eligibility, legitimacy, certification, cultural fit, ceremonial witnessing, or permission for other uses.
