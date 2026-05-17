---
doc_kind: workshop-matrix
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Spec Composition Matrix

This matrix treats each spec as a small interface. The jam experiment is to discover which interfaces actually line up, which need a reviewer or adapter, which overlap too much, and which should not be composed.

## Composition States

| State | Meaning | Jam Decision |
| --- | --- | --- |
| Direct | Output fields from one spec can become input fields for another with no sensitive change. | Safe to prototype with sample/public data. |
| Mediated | Specs can compose only through a reviewer, witness record, consent decision, or adapter. | Prototype the adapter or review step. |
| Overlap | Specs cover the same behavior or language. | Decide whether to merge, keep separate, or name the difference. |
| Blocked | Composition would violate consent, visibility, cultural authority, governance, or intended-use boundaries. | Record non-composability as a valid result. |
| Unknown | More context is needed. | Write the missing question as the next spec improvement. |

## Shared Interface Fields

These fields are the first places to test coherence:

| Interface Field | Appears In | Why It Matters |
| --- | --- | --- |
| `visibility_tier` | Almost all specs | The main boundary between public, local-only, private, and not-for-computation records. |
| `review_state` | Claims, atlas, insights, app, sensors, learning | Prevents raw material from becoming public or authoritative too early. |
| `evidence_pointers` | Claims, sensors, risk, insights, sidecar, commitments | Lets specs link to support without copying protected evidence. |
| `witness_records` | Witness, receipts, sidecar, flow funding, dream board | Lets multiple review/witness events stack without becoming one score. |
| `receipt_policy` | Gateway, allocations, receipt wall, sensors | Controls what can be shown after an action. |
| `do_not_compute` | Claims, atlas, learning, sensors | Hard boundary for indexing, summarization, routing, and AI use. |
| `bioregion_uri` | Commitment pools, atlas, mapping, risk, insights | Connects place-based records without forcing exact geospatial disclosure. |
| `intended_use` | Claims, risk, insights, gateway | Keeps a report scoped to the use it was reviewed for. |

## Spec Interface Map

| Spec | Primary Outputs | Likely Composes With | Main Risk |
| --- | --- | --- | --- |
| Witness Record Interop Profile | Witness records, diagnostics, optional anchor payload | Claims, receipts, sidecar, dream board, sensors | Witness records being mistaken for legitimacy or authority. |
| Claims Evidence Coherence Report | Claim status, evidence freshness, repair paths | Witness profile, risk map, insights brief, sidecar | Evidence laundering or overbroad public claims. |
| Commitment Pool Route Diagnostic | Route status, capacity summary, repair paths | Flow funding, dream board, spec composer | Routing around refusal or consent. |
| Flow Funding Frontier Map | Funding edges, pool readiness, witness gaps | Commitment pools, allocations, receipts | Ranking people or projects by fundability. |
| Untracked Allocation Ledger | Allocation receipt, aggregate summary, not-tracked register | Flow funding, receipt wall, private learning | Surveillance pressure through accounting. |
| Bioregional Mapping Layer Board | Layer manifests, review queue, missing layer list | Atlas, insights, sensors, risk | Publishing sensitive place-based knowledge. |
| Living Atlas Coherence Packet | Review queue, coherence summary, repair paths | Mapping, insights, claims, sensors | Turning workshop speech into public data by default. |
| Bioregional Insights Briefing | Brief, source table, review decisions | Atlas, claims, sensors, risk, sidecar | Summaries leaking private source context. |
| Risk and Insurance Coherence Map | Risk packet, investment shortlist, sensitive boundary report | Sensors, claims, insights, mapping | Becoming an underwriting, premium, or eligibility model. |
| Participant Gateway | Access record, agreement receipt, first offering | Spec composer, sidecar, receipt wall | Treating entry as publication consent. |
| Graph Chat Witness Sidecar | Citation table, claim diagnostics, AI-use receipt | Claims, witness profile, insights, gateway | Citations being treated as verified claims. |
| Sensor To Receipt Pipeline | Observation packet, review diagnostics, receipt | Claims, risk, atlas, insights | Raw readings being treated as verified claims. |
| Private Learning Ledger | Learning summary, withdrawal propagation report | Atlas, gateway, sidecar, receipt wall | Training or indexing raw protected data. |
| Dream To Fulfillment Board | Transition diagnostics, bundle candidates, receipts | Commitment pools, flow funding, witness profile | Pressuring dreams or care into commitments. |
| Receipt Wall Story Gallery | Story cards, approval diagnostics, public manifest | Witness profile, allocations, gateway, sidecar | Publishing without display approval. |
| Spec Composer Bundle Board | Bundle diagnostics, frozen build instructions | All specs | Composition being mistaken for consent. |

## High-Value Composition Tests

| Test | Specs | Expected Result | What We Learn |
| --- | --- | --- | --- |
| Claim -> witness -> receipt | Claims Evidence + Witness Profile + Receipt Wall | Mediated composition through reviewer and display approval. | Whether a public receipt can preserve evidence boundaries. |
| Offering -> pool -> flow edge | Dream Board + Commitment Pool + Flow Funding | Mediated composition through route diagnostics and pool rules. | Whether commitments can become fundable without flattening refusal. |
| Sensor -> claim -> risk packet | Sensor Pipeline + Claims Evidence + Risk Map | Mediated composition through evidence review and non-underwriting boundary. | Whether sensor evidence can inform resilience without becoming actuarial. |
| Atlas -> insights -> sidecar | Living Atlas + Insights Briefing + Graph Chat Sidecar | Direct for public sample records; mediated for local-only records. | Whether app answers can show source coherence without leaking context. |
| Gateway -> composer -> selected build | Participant Gateway + Spec Composer + Build Attempt Templates | Direct if consent and AI-use preferences are explicit. | Whether participant entry can flow into spec-driven builds. |
| Allocation -> receipt wall | Untracked Allocation + Receipt Wall | Often blocked or summary-only. | Whether deliberate non-legibility can remain a valid outcome. |

## Known Non-Composability Candidates

These should be tested openly. A blocked composition is a successful discovery if the boundary is recorded.

| Pair | Why It May Not Compose | Possible Adapter |
| --- | --- | --- |
| Risk Map + Flow Funding | Risk signals could create investment or insurance implications beyond the reviewed use. | Reviewer-approved resilience action shortlist with non-underwriting language. |
| Receipt Wall + Private Learning Ledger | Public story cards can expose private learning context. | Public projection record and withdrawal propagation check. |
| Bioregional Mapping + Graph Chat Sidecar | App citations can leak sensitive layer names or locations. | Citation redaction plus local-only sidecar state. |
| Commitment Pool + Untracked Allocation | Route diagnostics want structured fields; untracked allocation preserves non-legibility. | Summary-only allocation receipt with no routing. |
| Dream Board + Commitment Pool | Dreams and care can be pressured into commitments. | Explicit transition state: not-a-commitment. |

## Coherence Hypotheses

- Coherence is strongest where specs share boundary fields: `visibility_tier`, `review_state`, `evidence_pointers`, `witness_records`, and `receipt_policy`.
- The main adapter pattern is not technical. It is review: consent review, steward review, display approval, AI-use approval, or intended-use review.
- The main conflict pattern is category drift: claims become truth, citations become verification, maps become authority, risks become underwriting, dreams become obligations, and receipts become legitimacy.
- The sheaf-theory intuition may be useful as a light metaphor: local sections can agree on overlaps without forcing one global object. In jam language, each spec can keep its local boundaries while overlaps are tested explicitly.

## Tomorrow Output Targets

- One filled composition matrix row for each participant-selected bundle.
- At least three fixture-backed composition tests.
- A list of non-composable pairs and why they are blocked.
- A short list of shared fields that should become common schema fragments.
- A decision on whether the sheaf-theory framing helps participants or should stay operator-only.
