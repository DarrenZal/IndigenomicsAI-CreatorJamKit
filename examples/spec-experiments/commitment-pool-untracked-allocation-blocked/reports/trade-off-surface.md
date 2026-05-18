---
doc_kind: trade-off-surface
status: fixture_example
visibility: public_sample
last_updated: 2026-05-17
---

# Trade-Off Surface: Commitment Pool + Untracked Allocation

Fixture: `commitment-pool-untracked-allocation-blocked-public-sample-v0.1`
Template: `templates/trade-off-surface.md`
Review date: 2026-05-17

This surface tests whether deliberation support can handle a `non_composable` result without treating refusal, privacy, or deliberate non-legibility as failure.

## Three Checks

| Check | Fixture State | Note |
| --- | --- | --- |
| Composability | `no` | The route diagnostic requires structured route fields, but the allocation record intentionally withholds amount, recipient, route permission, and computation permission. |
| Coherence | `holds_as_blocked` | The fixture is coherent because it preserves the allocation boundary and records why direct routing should stop. |
| Desirability / health | `block_for_now` | Direct composition would create surveillance pressure and change the nature of the gift. The healthy move is to preserve separate and record a summary-only receipt. |

## Gains

| Gain | Why It Matters |
| --- | --- |
| Non-composability is recorded as a valid result. | Participants can see that a blocked route is not a failed contribution. |
| Private relational support remains non-routeable. | The fixture preserves the reason the allocation was not tracked. |
| The repair path is narrow. | Future public offers must be new records with explicit consent, not backfilled from private support. |
| The engine now detects the exclusion boundary cleanly. | `do_not_compute` is represented as an explicit excluded record, not only as narrative prose. |

## Losses, Costs, Or Burdens

| Cost | Who May Carry It | Mitigation |
| --- | --- | --- |
| The commitment pool cannot count this support as capacity. | Pool stewards and route reviewers. | Keep capacity arithmetic honest and invite a separate public offer only if the contributor chooses. |
| The public story is less complete. | Facilitators, display readers. | Use summary-only wording and do not expose hidden details to make the story more satisfying. |
| Reviewers must resist helpful inference. | Reviewers, AI assistants, future indexers. | Preserve `do_not_compute`, AI-use receipt exclusions, and prohibited actions. |
| The contributor may not get public recognition. | Original contributor. | Treat non-recognition as a valid privacy-preserving outcome, not a defect. |

## Fragilities

| Fragility | What Could Drift |
| --- | --- |
| Summary-only receipt could become a public story. | A display surface might imply value, beneficiary, or route impact that was intentionally hidden. |
| Repair path could become pressure. | "Make a separate public offer" could be heard as "you should make this legible." |
| AI systems could infer around redaction. | Private notes, recipient identity, or amount could be reconstructed from surrounding context if indexed. |
| Matrix rows could overgeneralize the result. | Future readers may assume all untracked allocations are non-composable with every other surface. |

## Adjacent Possibilities

| Possibility | Required Guardrail |
| --- | --- |
| Contributor later creates a separate public offer. | Treat it as a new record with explicit consent; do not backfill from the private allocation. |
| Receipt wall names a private-support boundary. | Display review must keep details absent and obstruction markers visible. |
| Commitment pool records "capacity not counted." | Do not infer amount, recipient, route tags, or beneficiary. |
| CAT-style receipts later anchor the blocked transition. | Content addressing must not expose protected payloads or imply routeability. |

## Foreclosures

| Foreclosure | Why It Is Healthy Here |
| --- | --- |
| No routeable commitment is created. | Routeability would require consent and structured fields that do not exist by design. |
| No funding edge is created. | A funding edge would turn private relational support into finance-like infrastructure. |
| No pool capacity update is allowed. | Capacity updates need quantity and unit fields that were intentionally not tracked. |
| No private notes are summarized or embedded. | The private note pointer is a boundary marker, not a hidden data source. |

## Affected Perspectives

| Perspective | Possible Benefit | Possible Burden | Missing Review Needed |
| --- | --- | --- | --- |
| Original contributor | Their private support is not converted into public routing data. | They may receive less visible recognition. | Contributor review before any later public offer. |
| Potential recipient | Their identity remains protected. | They may be invisible in aggregate support stories. | Recipient consent if any public story is later proposed. |
| Pool steward | Gets a clear stop condition. | Cannot include the support in pool capacity. | Steward review of summary-only receipt language. |
| Facilitator | Can explain why blocked composition is valid. | Must avoid pressure to make private support legible. | Facilitation wording check. |
| Future indexer or AI assistant | Gets explicit prohibited actions. | Must not infer around redaction. | AI-use and indexing policy check. |

## Time Horizons

| Horizon | Question |
| --- | --- |
| Immediate | Did the fixture stop direct routing and preserve the private allocation boundary? |
| Jam scale | Can participants see that non-composability protects dignity rather than blocking contribution? |
| Seasonal | If a contributor later wants public routing, can the new record stay separate from the private one? |
| Long horizon | Does the system preserve spaces for generosity that should not become accounting infrastructure? |

## AI Role

AI can help identify route-field gaps and draft a plain-language boundary receipt. AI must not infer hidden fields, reconstruct private notes, estimate value, identify recipients, or decide that a private allocation should become routeable.

## Decision Support Result

Status: `preserve_separate`

Reason: The composition is technically blocked and health-preserving as blocked. The right next move is to keep the summary-only receipt and prevent route, value, display, or inference drift.

Next human decision: A facilitator or sample steward should review any display use of the summary-only receipt before it appears outside fixture documentation.

## Not Established

- routeable commitment
- funding eligibility
- pool capacity update
- financial value
- public recognition claim
- goodness or health beyond this fixture
- authority
- legitimacy
- certification
- cultural fit
- permission for other uses
