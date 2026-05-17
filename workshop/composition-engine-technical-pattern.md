---
doc_kind: workshop-analysis
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Composition Engine Technical Pattern

This note describes the technical pattern behind the Creator Jam composition work. It is operator-facing. It is not a participant handout, not a production architecture, and not approval to process real participant material.

Use only fictional, public-sample, or explicitly approved material when testing any idea from this note.

## Core Claim

LLMs can propose compositions. They should not authorize them.

Embeddings, graph search, clustering, and LLM reasoning are useful for finding possible overlaps, dependencies, tensions, and bundles. Authority, consent, visibility, `do_not_compute`, withdrawal, and display approval are not probabilistic questions. They require hard constraints, scoped review, and receipts.

The compact rule:

> Composition is reviewed gluing under authority, provenance, and boundary constraints.

## Knowledge Gardening Frame

The technical pattern is closer to knowledge gardening than claim extraction.

Gardening is precise here:

- Tending: records need review, narrowing, repair, and pruning.
- Seasons: some records need time before they can compose.
- Companion planting: some records work better in proximity without becoming one record.
- Beds and fences: local boundaries matter.
- Soil: substrate, provenance, and governance shape what can grow.
- Harvest: receipts come due when something is built, shown, funded, or learned from.
- Compost: records age, retire, withdraw, or transform.

The system should help people tend a field of offerings, claims, commitments, refusals, and specs. It should not optimize the field into one bundle.

## Layer Model

| Layer | Role | Useful Techniques | Hard Boundary |
| --- | --- | --- | --- |
| 1. Garden | Raw participant language: dreams, ideas, stories, offers, refusals, notes, transcripts, specs. | Forms, chat, meeting notes, voice transcription, manual notes. | Raw input is not consent to extract, publish, route, or compute. |
| 2. Extraction | Candidate structured records. | LLM structured output, source-span extraction, classifiers. | Extracted records are proposals, not authority. |
| 3. Provenance | Lineage, source spans, author, time, visibility, AI use, withdrawal path. | PROV-style graphs, content IDs, source pointers, audit logs. | A record without provenance should not compose. |
| 4. Relation | Suggested overlap, duplicate, dependency, conflict, complement, bridge, or obstruction. | Embeddings, clustering, graph search, structural diff, LLM relation review. | Similarity is not permission. |
| 5. Authority | Who has standing to compose or transform these records. | Authority matrices, role scopes, contributor authorization records. | A valid-looking composition without standing is invalid for the kit. |
| 6. Composition | Candidate bundles, required transitions, exclusions, blockers, repair paths. | LLM bundle proposal, graph neighborhood search, constraint-aware planners. | Bundle selection is discovery, not optimization. |
| 7. Coherence Vector | Multi-dimensional fit check. | LLM critique, rule checks, reviewer checklist, graph consistency checks. | Coherence is not one score. |
| 8. Constraint | Deterministic gates. | SAT/CSP-style checks, schema validators, policy engines. | Consent, visibility, `do_not_compute`, withdrawal, and display approval must not be overridden by LLM confidence. |
| 9. Review / Witness / Receipt | Human or scoped reviewer accepts, narrows, blocks, returns, or records. | Reviewer checklist, witness receipt, display review, AI-use receipt. | Receipts record what happened; they do not establish legitimacy. |
| 10. Learning | Reviewed projections can inform future patterns. | Private learning ledger, aggregate metrics, retrospectives. | Do not train, embed, index, or summarize protected raw material. |

## Extraction Contract

Every extracted candidate record should carry at least:

```yaml
candidate_id:
source_record_id:
source_span:
extracted_type: claim | question | offer | need | commitment | refusal | constraint | spec_fragment | evidence_pointer | other
speech_act:
explicit_or_inferred: explicit | inferred | ambiguous
confidence:
visibility_tier:
permission_state:
intended_use:
ai_use:
time_window:
issuer_or_contributor:
withdrawal_path:
not_established:
```

The important field is `explicit_or_inferred`. A directly stated commitment and an inferred possible commitment are different records. They should not share the same authority path.

## Relation Contract

Relation proposals should be typed. Useful relation types include:

| Relation | Meaning | Typical Technique |
| --- | --- | --- |
| `duplicate_of` | Same or near-same record. | Embeddings plus structural diff. |
| `overlaps_with` | Shared subject, place, time, or purpose. | Embeddings, graph search, LLM comparison. |
| `depends_on` | One record needs another before it can proceed. | Graph edges, LLM analysis, rule checks. |
| `conflicts_with` | Records cannot both be accepted as stated. | Contradiction detection, reviewer check. |
| `complements` | Records strengthen each other without merging. | Cluster review, LLM suggestion. |
| `blocks` | A boundary, refusal, capacity limit, or missing field stops composition. | Constraint checks. |
| `same_word_different_epistemic` | Shared vocabulary, different authority or meaning. | Human review, LLM critique. |
| `candidate_bundle_member` | Potential bundle membership. | Bundle proposal plus review. |

Relations are suggestions unless a reviewer or deterministic rule has authority to assert them.

## Authority Layer

Authority answers a different question than review.

Review asks: does this record meet a criterion?

Authority asks: who has standing to make this move?

Examples:

- A facilitator can notice that a dream could become a commitment, but only the contributor can authorize the transition.
- A technical reviewer can confirm fields line up, but cannot grant display approval.
- A pool steward can record capacity, but cannot turn private care into routeable finance.
- An LLM can suggest that two records relate, but cannot authorize a composition.

Authority should be represented explicitly:

```yaml
authority_check:
  move:
  required_authority:
    - original_contributor
    - pool_steward
    - display_reviewer
  authority_record:
  authority_state: present | missing | refused | outside_scope
  not_authorized_by:
    - llm_confidence
    - embedding_similarity
    - graph_edge
    - facilitator_without_consent
  contributor_consent_check:
    contributor_record:
    consent_state: explicit_in_source | reconfirmed_for_transition | missing | refused
    reconfirmation_required_before_acceptance: true | false
```

## Coherence Vector

Coherence is a vector, not a scalar. A composition can hold in one dimension and fail in another.

| Dimension | Question | Example Failure |
| --- | --- | --- |
| Logical coherence | Do the records contradict each other? | Two records allocate the same one remaining pool hour. |
| Epistemic coherence | Does evidence support what the composition says? | A citation is treated as verified claim support. |
| Normative coherence | Does the composition do what it should? | A returned offer becomes a negative ranking. |
| Relational/cultural coherence | Does the composition preserve the boundaries that make records meaningful? | A software witness receipt is read as ceremonial witnessing. |
| Temporal coherence | Does the composition hold across time? | A stale commitment is routed after its time window expires. |

The output should preserve the vector:

```yaml
coherence_vector:
  logical_coherence:
    state: holds | holds_with_limits | blocked | unknown
    note:
  epistemic_coherence:
    state:
    note:
  normative_coherence:
    state:
    note:
  relational_cultural_coherence:
    state:
    note:
  temporal_coherence:
    state:
    note:
```

## Epistemic And Normative Frontier

The composition engine sits between descriptive and prescriptive records.

| Register | Plain Meaning | Record Types |
| --- | --- | --- |
| Epistemic | What is known, observed, cited, measured, or claimed. | observations, evidence pointers, citations, claims, sensor readings, notes. |
| Normative | What should happen, what is promised, what is refused, or what is governed. | commitments, protocols, agreements, refusals, constraints, review decisions. |
| Governance pathway | How a field moves from what is known toward what should happen. | discovery, deliberation, authorization, commitment, receipt, withdrawal. |

Most risky transitions cross this frontier:

- citation -> claim
- observation -> attestation
- dream -> commitment
- route diagnostic -> funding discussion
- receipt -> public story
- risk signal -> insurance discussion

The existing `templates/speech-act-transition.md` is already the frontier-crossing record. This note names why that template is load-bearing.

## Constraint Layer

Some checks should be deterministic:

- `do_not_compute: true` blocks indexing, summarization, routing, embedding, and AI use.
- `visibility_tier` must not be widened by composition.
- `permission_state: refused` blocks use except marker-only references.
- `display_approval: pending` blocks public projection.
- `time_window` blocks stale commitments or expired offers.
- `pool_capacity` blocks over-allocation.
- `authority_state: missing` blocks speech-act transitions.

These can be modeled as constraint satisfaction rather than LLM judgment. A useful implementation could combine:

- JSON schema validation for shape.
- Policy checks for hard boundaries.
- Constraint solver or rules engine for capacity, visibility, and authority gates.
- LLM explanation after the hard result, not instead of it.

## Algorithmic Toolkit

| Technique | Good Use | Bad Use |
| --- | --- | --- |
| LLM structured extraction | Turning narrative into candidate records with source spans. | Treating inferred commitments as real commitments. |
| Embeddings | Finding similar or adjacent offerings/specs. | Treating similarity as consent or authority. |
| Clustering | Seeing themes, neighborhoods, and candidate workstreams. | Forcing every record into one cluster. |
| Graph search | Finding dependencies, provenance, and affected downstream records. | Treating graph paths as proof of legitimacy. |
| Structural diff | Comparing two records with same subject but different fields. | Ignoring the diff because embeddings are close. |
| Constraint solvers | Enforcing hard gates like capacity, visibility, and `do_not_compute`. | Encoding cultural or relational authority as a simple Boolean without review. |
| Time-aware retrieval | Filtering records by valid time window and freshness. | Routing stale commitments because they remain semantically similar. |
| Provenance graphs | Withdrawal propagation and derived-record review. | Exposing private source context to prove lineage. |

## Sheaf And Cosheaf Operator Note

The sheaf intuition remains useful: local views can agree on overlaps, and obstructions should be recorded when they do not glue.

For this work, cosheaves may often be the better operator metaphor. A sheaf asks whether local data can glue into a coherent global object. A cosheaf can assemble local contributions into a larger object through colimits without pretending that the global object overrides local sources.

In kit language:

- local records remain canonical
- overlaps are reviewed
- gluing conditions are explicit
- obstructions are receipts
- the composed output does not erase source authority

Keep this language operator-only unless it helps a specific technical discussion.

## Failure Modes To Avoid

| Failure Mode | What It Looks Like | Guardrail |
| --- | --- | --- |
| Composition-as-optimization drift | Bundle selection becomes a scoring/search problem. | Treat bundle selection as discovery plus review. |
| Confidence collapse | LLM confidence gets treated as authorization. | Store confidence only as proposal metadata. |
| Provenance loss | Extracted records lose source context and cannot be withdrawn. | Require source spans and derived-from links. |
| Category drift | Dream becomes obligation, citation becomes truth, receipt becomes legitimacy. | Speech-act transitions and obstruction markers. |
| Authority drift | Reviewer without standing composes records. | Authority layer before composition. |
| Boundary laundering | Private/protected material is summarized to justify a public record. | Marker-only references and `do_not_compute` constraints. |
| Temporal flattening | Expired offers and stale claims remain routable. | Time-aware retrieval and freshness checks. |
| Global overwrite | A composed object erases local context or refusal. | Cosheaf-style assembly: local remains canonical. |

## Current Fixture Evidence

The pattern is now grounded by three kinds of fixture:

| Fixture | What It Shows |
| --- | --- |
| `examples/spec-experiments/claims-witness-receipt-composition/` | Evidence, claim, witness record, receipt, display review, excluded source, and AI-use receipt discipline. |
| `examples/spec-experiments/commitment-pool-untracked-allocation-blocked/` | A non-composable result where non-legibility must be preserved. |
| `examples/spec-experiments/commitment-pool-dream-witness-composition/` | Contributor authority, capacity pressure, time windows, post-acceptance withdrawal, and commitment speech-act transitions. |

## Related Workstreams

The same composition pattern appears across related work in Spore, Intelligence Commons, RegenAI Claims Engine, bioregional mapping, flow funding, and Indigenomics AI app design. This note does not claim those systems are the same. It says the Creator Jam kit now has a concrete technical substrate for testing where their primitives can compose, where they need adapters, and where they should remain separate.

## Minimal Engine Loop

```text
raw garden input
  -> extract candidate records with source spans
  -> attach provenance, visibility, intended use, and withdrawal path
  -> propose typed relations
  -> check authority for requested moves
  -> propose candidate bundle
  -> run hard constraints
  -> produce coherence vector
  -> reviewer narrows, accepts, blocks, or returns
  -> record witness/receipt and derived_from_transitions
  -> allow only reviewed projections into future learning
```

The loop is useful only if it preserves the ability to say no, not yet, not public, not computable, not mine to authorize, or not coherent.
