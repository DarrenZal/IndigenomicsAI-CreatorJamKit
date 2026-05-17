---
doc_kind: workshop-analysis
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Waka, Claims Engine, And Coordination Canoe Primitive Comparison

This is an internal analysis artifact for the Creator Jam kit. It compares three coordination surfaces before we write any interop spec:

- **Waka:** Austin Wade Smith / RiverComputer's Waka project.
- **RegenAI Claims Engine:** the RegenAI claim, evidence, verification, and anchoring rail.
- **Coordination Canoe:** the Creator Jam composition pattern where offerings, specs, commitments, refusals, reviews, build attempts, and receipts can be carried into a selected build.

This document is not a Waka spec, not a commitment to adopt Waka, and not a representation of Austin's desired direction. Mapping does not mean adoption. Similar words do not mean shared semantics. The purpose is to find the shared primitives, the mismatches, and the questions that should be asked before anyone builds a premature bridge.

Use only fictional, public-sample, or explicitly approved material when testing any idea from this note.

## Source Map

| Surface | Current Source | Notes |
| --- | --- | --- |
| Waka | `https://github.com/RiverComputer/waka_docs` | External project. Treat current docs as primary source, but confirm posture and implementation direction with Austin before writing an interop spec. |
| RegenAI Claims Engine | RegenAI local claims engine notes and Waka/Regen translation memo | Implemented internal claim/evidence rail with verification states, entity graph integration, MCP/CLI/API surfaces, and Regen anchoring. Do not copy credentials, endpoint details, or operational secrets into this kit. |
| Coordination Canoe | Creator Jam kit specs, templates, examples, and workshop files | Local working pattern for participant offerings becoming bundles, build attempts, reviews, receipts, blocked examples, and public projections. |

## Three Surfaces

| Surface | Center Of Gravity | What It Is Trying To Preserve |
| --- | --- | --- |
| Waka | Sovereign data, witnessed claims, composable witness methods, identity, anchoring, and issuance across multiple substrates. | Claims sovereignty, contextual integrity, durable records, and protocol-agnostic portability. |
| RegenAI Claims Engine | A practical claims/evidence system that can create claims, attach evidence, move through verification states, and anchor content-addressed claim records. | Append-only claim lineage, evidence coherence, verification state, and ledger-backed anchoring. |
| Coordination Canoe | A jam/workshop pattern where participants bring offerings, specs, commitments, and refusals that may compose into candidate bundles and reviewed build attempts. | Consent boundaries, refusal boundaries, speech-act transitions, display gates, and non-composability as a valid result. |

## Primitive Comparison

| Primitive | Waka | RegenAI Claims Engine | Coordination Canoe | Overlap Status | Risk Or Question |
| --- | --- | --- | --- | --- | --- |
| Actor or identity | DID-rooted identity, including user, project, and organization contexts. | Entity and claimant URIs; operational auth lives in app/API surfaces. | Participant, contributor, reviewer, witness, facilitator, and display reviewer roles. | Partial overlap. | Identity systems may not carry the same authority model. |
| Claim | A subject plus accreting signed witness records; designed to produce portable witnessed claims. | Claim record with statement, claimant, entity, claim type, evidence, verification state, content hash, and lineage. | A possible output of a spec or evidence review, never automatic from a citation or offering. | Strong word overlap, different implementation shape. | Do not let "claim" mean "truth" or "approved story." |
| Evidence | Linked resources that can be witnessed, validated, and carried with a claim record. | Evidence pointers and source documents attached to claims. | Evidence pointers with visibility, review state, and permission fields. | Strong overlap. | Evidence visibility is not claim visibility. Protected evidence must not be exposed to prove a claim. |
| Witness | Human or machine witness methods composed by witness policy into validation records. | Verification and evidence review can be represented in claim state and related records; Waka/Regen memo explores witness records as a bridge. | Software/reviewer receipt only, explicitly not ceremonial witnessing or cultural authority. | High-risk word overlap. | Witness-model collision is the main bridge risk. A Waka witness record, a Regen verification, and a Creator Jam witness rollup may not authorize the same thing. |
| Review or verification | Witness policies combine methods, roles, registries, thresholds, and verdicts. | Verification state machine such as self-reported, peer-reviewed, verified, ledger-anchored, or withdrawn. | Review states, reviewer objects, reviewer_type, display approval, refusal boundaries, and repair paths. | Partial overlap. | Linear verification states may flatten composable witness records or local review constraints. |
| Receipt | Waka produces records that carry evidence, witness method, and signatures; downstream systems can inspect them. | Anchoring and history endpoints can produce operational receipts for claim lifecycle events. | Receipts record what happened, what was not run, what was refused, and what is not established. | Partial overlap. | Receipts can be mistaken for legitimacy, certification, or permission. |
| Anchor | Multi-substrate anchoring and issuance across AT Protocol, IPFS/Filecoin, EAS, Regen, Hypercerts, and related surfaces. | Content-addressed claim records anchored through Regen tooling, with reconciliation to avoid ghost anchors. | Optional pointer or receipt field, not a guarantee of public display or reuse. | Strong overlap at the word level. | Anchor must not imply consent, completeness, or cultural authority. |
| Bundle or composition | Witness records accrete on a claim and policies compose methods into verdicts. | Claims can link evidence, supersede prior claims, and connect to entity graph relationships. | Offerings and specs compose into candidate bundles, selected bundles, build instructions, and reviewer/witness rollups. | Useful analogy, not same object. | A Waka composition is not automatically a Creator Jam bundle. |
| Speech-act transition | Waka moves resources through witnessing into claims and downstream instruments. | AI extraction or human entry can turn text into claims; verification changes state. | Explicit transition records for citation to claim, observation to attestation, dream to commitment, witness record to attribution, and receipt to story. | Coordination Canoe has the clearest current guardrail. | Any bridge needs transition records so citations, observations, or receipts do not silently become claims. |
| Withdrawal or supersession | To confirm with Austin in current implementation and policy design. | Withdrawn is a terminal state; supersedes_rid supports claim lineage. | Withdrawal paths and cascading propagation are required on composed records. | Partial overlap. | Withdrawal semantics must survive any adapter, especially after public projection or anchoring. |
| Public projection | Waka has public read-only snapshots and portable records when chosen by a project. | Claims may be exposed through API/UI depending on application policy. | Story cards and receipt wall entries require display approval and obstruction markers. | Partial overlap. | Public readability does not mean display approval or participant consent. |
| AI use | Machine witness can include AI or agent methods in Waka's witness design space. | AI claim extraction can generate candidate claims with confidence metadata. | AI use requires specific approval and receipts that name what AI touched and did not touch. | Useful overlap. | AI cannot become a reviewer of consent, authority, ceremony fit, or community legitimacy. |
| Non-composability | Waka witness policies can reject or not satisfy a validation path. | Verification can fail, remain self-reported, or be withdrawn. | Blocked and non-composable examples are first-class outputs. | Coordination Canoe makes this most explicit. | A bridge should preserve "do not compose" as a valid result, not treat it as missing data. |
| Durability | Explicit long-horizon design across identity, storage, claim, and issuance substrates. | Append-only records and ledger anchoring support auditability. | Receipts and rollups are durable enough for workshop memory, not by themselves long-term proof infrastructure. | Waka is strongest here. | The Creator Jam kit should not imply it has Waka's durability guarantees. |

## What Waka Appears To Bring

These are strengths visible from the current Waka docs and should still be confirmed with Austin before design work proceeds:

- A three-layer architecture: identity, claims, and anchoring/issuance.
- DID-rooted identity with individual, project, and organization contexts.
- Claims as subjects with accreting signed witness records.
- Human and machine witness methods composed by witness policies.
- Policy and registry separation, so a policy can name admissible roles while local registries bind roles to concrete signers.
- Multi-substrate anchoring and issuance, so one claim can be portable across different downstream systems.
- A durability frame that is stronger than the Creator Jam kit currently attempts to provide.

## What The RegenAI Claims Engine Brings

The RegenAI Claims Engine is closer to an implemented operational rail:

- Claim records with claimant, entity, statement, claim type, evidence, verification, content hash, and lineage fields.
- Claim creation, listing, evidence attachment, verification, extraction, anchoring, history, and reconciliation surfaces.
- A concrete verification state machine and withdrawn state.
- Integration with an entity graph and MCP/CLI/API workflows.
- Regen anchoring lifecycle and reconciliation discipline.

The bridge risk is that the RegenAI model can look simpler because it is more linear. That simplicity is useful operationally, but it may collapse Waka's composable witness model if treated as equivalent.

## What Coordination Canoe Brings

Coordination Canoe is not a claims engine. It is a participant and facilitator pattern for composition discipline:

- Offerings can become spec fragments.
- Spec fragments can become candidate bundles.
- A selected bundle can become frozen build instructions.
- Agents or people can attempt the selected build.
- Reviewers can check outputs against acceptance criteria and refusal boundaries.
- Witness rollups and receipts can record what happened.
- Speech-act transitions make category shifts visible.
- Display gates keep receipt candidates from becoming public stories too early.
- Blocked and non-composable examples are treated as successful discoveries.

The bridge value is that Coordination Canoe can test whether Waka-shaped, RegenAI-shaped, and jam-shaped records compose without enclosing each other.

## Same Word, Different Epistemic

These words need special care in any bridge artifact:

| Word | Collision To Watch |
| --- | --- |
| Witness | Waka witness methods may be validation primitives; Regen verification may be operational review state; Creator Jam witness records are software/facilitator receipts and not cultural authority. |
| Claim | A claim can be a portable witnessed object, an internal claim row, or a candidate assertion extracted from participant material. |
| Evidence | Evidence can support a claim without being public, AI-readable, or display-approved. |
| Verification | Verification can mean policy satisfaction, reviewer state, ledger anchoring, or display review. These should not be merged. |
| Anchor | Anchoring can make a record durable without making it true, complete, consented, or reusable. |
| Receipt | A receipt can say what happened without authorizing downstream use. |
| Withdrawal | Withdrawal can remove permission to use or display material even when some anchor, hash, or public pointer still exists. |

## Bridge Risks

- **Mapping becomes adoption:** A comparison table should not quietly convert Creator Jam records into Waka records or RegenAI claims.
- **Interop becomes implementation:** Once fields map, teams may start building before Austin's posture is known.
- **Witness authority leaks:** A witness record in one system may carry more, less, or different authority in another.
- **Speech-act drift:** Citations can become claims, observations can become attestations, dreams can become commitments, and receipts can become stories unless transition records are required.
- **Protected data leakage:** Bridge tests must not move protected evidence into public fixtures, AI contexts, or external systems.
- **Linearization:** RegenAI's verification states may be useful, but a bridge must not flatten Waka's accreting witness records into one status field unless that loss is explicit.
- **Display drift:** A portable or anchored record is not automatically a public story-card, gallery item, or participant-approved display object.
- **Speaking for Austin:** Until Austin responds, write questions and comparison notes, not claims about what Waka should become.

## Posture Questions For Austin

Before writing a Waka interop spec, ask Austin a low-stakes posture question:

- Would you rather we run Waka against fictional/sample Creator Jam or RegenAI claims data?
- Would you rather external systems map toward Waka's primitives?
- Would you rather this remain a comparison between parallel patterns for now?
- What are the load-bearing Waka primitives we should not simplify?
- What is the minimum viable witness record shape?
- How should withdrawal, supersession, and public snapshots be treated when an external system bridges into Waka?
- Would a fictional sample fixture help, or would it create noise before the design question is clear?

## Draft Austin Note

> Creator Jam work and the RegenAI Claims Engine are surfacing primitives adjacent to Waka: evidence, claim, witness, receipt, anchor, withdrawal, and public projection. We have been meaning to bridge Claims Engine and Waka for a while, but we do not want to write the wrong spec before we understand your current posture.
>
> What would be most useful from your side: running Waka against fictional/sample external data, mapping external systems toward Waka primitives, treating the systems as parallel patterns for now, or something else? No ask or commitment here. We are orienting before we build.

## Creator Jam Experiment Shape

If we test this inside the jam, keep it as an analysis or fixture exercise:

1. Pick one fictional Creator Jam claim/evidence fixture.
2. Express it as a RegenAI-style claim record.
3. Sketch what a Waka witness-record shape might need, without pretending to implement Waka.
4. Add a speech-act transition record for each category shift.
5. Add a display approval state and obstruction marker.
6. Record what does not compose.

The output should be a comparison receipt, not a production bridge.

## Next Decisions

| Decision | Default For Now |
| --- | --- |
| Write a Waka interop spec? | Not yet. Wait for Austin's posture or choose a deliberately fictional fixture. |
| Use Coordination Canoe name? | Yes, as the local English working metaphor already named in `docs/glossary.md`. Do not present it as a language or ceremonial claim. |
| Ask Carol Anne about language naming? | Optional and separate. If asked, make it an invitation, not a request to approve a decision. |
| Add a jam build task? | Yes: create a fictional comparison fixture only after this primitive comparison has review. |
| Compose with Claims Engine? | Yes, but first as comparison and sample mapping, not adoption. |
