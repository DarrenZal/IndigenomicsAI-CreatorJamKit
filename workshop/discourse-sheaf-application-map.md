---
doc_kind: workshop-analysis
status: draft
visibility: public_sample
last_updated: 2026-05-18
---

# Discourse Sheaf Application Map

This note applies the discourse-sheaf frame from opinion dynamics to the Creator Jam composition work.

It is operator-facing. It is not a participant handout, not a consensus machine, not a production architecture, not a scoring method, and not approval to process real participant material.

Use only fictional, public-sample, or explicitly approved material when testing ideas from this note.

## Core Translation

Creator Jam does not need people to converge on one opinion.

It needs purpose-bound shared surfaces where different local worlds can coordinate without being flattened.

In the kit's language:

> A coherent composition is a reviewed composition for one stated use, under stated authority, with stated exclusions.

It is not the true global view. It is not consensus, consent, legitimacy, certification, cultural fit, or permission for other uses.

## Why This Helps

The discourse-sheaf model separates local belief spaces from shared discourse spaces. People can hold different internal contexts while learning to express narrow, purpose-bound projections that can coordinate on a shared surface.

That matches the Creator Jam discipline:

- local records remain canonical
- shared surfaces see reviewed projections only
- restriction maps are review, permission, and authority policies
- obstructions are valid findings
- fixed boundaries remain fixed
- coordination should improve expression across difference, not force assimilation

This is operator math for coherence and boundary diagnostics. It should stay out of participant-facing materials unless it directly helps a room think clearly.

## Working Map

| Discourse Sheaf Idea | Creator Jam Meaning |
| --- | --- |
| Vertex stalks | Participant, steward, organization, Nation, project, or record-local context. |
| Edge stalks | Shared surface: bundle review, claim review, commitment pool, receipt wall, risk packet, display review, app card, or funding discussion. |
| Restriction maps | Reviewed projections: what can be said, shared, computed, routed, or displayed for this exact use. |
| Global section | A coherent composition for one stated purpose, not a totalizing view. |
| Coboundary / disagreement | Projection mismatch, missing authority, visibility conflict, category drift, or incompatible intended use. |
| Cohomology / obstruction | The reason local records cannot glue without violating a boundary. |
| Stubborn agents | Refusals, protocols, `do_not_compute`, protected records, authority limits, display blocks, and withdrawal states. |
| Harmonic extension | What can still compose while fixed boundaries remain fixed. |
| Expression-map dynamics | Learning how to communicate across difference without changing or extracting private realities. |

## Three Application Planes

There are at least three sheaf-like systems in this work. Keep them separate when reasoning about obstructions.

### 1. Jam Spec Composition

People bring visions, specs, offerings, refusals, and commitments. The jam asks what can compose into a build.

In this plane:

- local views are each person, spec, offering, refusal, or commitment
- overlaps are shared fields, dependencies, themes, goals, and boundary conditions
- projection maps decide what can enter a candidate bundle
- obstructions name what should not compose
- a global section is a selected build bundle for one stated purpose

This is the "what should we build during the jam?" layer.

### 2. App Discourse Graph

The Indigenomics AI app could let people contribute comments, questions, claims, evidence, hypotheses, commitments, needs, offers, and refusals through chat or app flows.

In this plane, discourse sheaves apply directly. Each contributor or source has local meaning. The app creates shared surfaces such as:

- claim review
- evidence panels
- map layers
- commitment pools
- recommendation surfaces
- receipt or witness rollups
- chat answers

The key question is:

> What projection from a person's discourse into the app graph is authorized, reviewed, and safe?

Possible future spec:

- `specs/indigenomics-ai-discourse-graph-contribution-surface.md`

Purpose: let people contribute structured discourse objects through chat or app flows without turning every utterance into a claim, commitment, public story, or graph fact.

### 3. Knowledge Graph Composition

The knowledge graph is itself a composed object made from many sources. Entity resolution, deduplication, triples, summaries, and recommendations are all gluing operations.

In this plane, the operator questions are:

- Do these two sources actually refer to the same entity?
- Do their claims agree only under a narrower projection?
- Is there an obstruction because source authority differs?
- Should this stay as two local records instead of one merged node?
- What downstream recommendations depend on this merge?

Possible future operator note:

- `workshop/knowledge-graph-composition-diagnostics.md`

Purpose: name entity-resolution, provenance, source-authority, and recommendation-boundary diagnostics without treating graph merges as truth or consent.

## Local Contexts And Shared Surfaces

Local contexts can include:

- participant offerings
- dreams, needs, promises, refusals, and withdrawals
- evidence pointers
- stewardship records
- place-based records
- reviewer notes
- cultural or protocol boundaries
- private or protected records
- `do_not_compute` records

Shared surfaces can include:

- candidate bundle review
- speech-act transition review
- commitment-pool routing
- claim review
- AI-use review
- display review
- receipt wall story selection
- risk or resilience packet review
- app graph/chat answer surface
- funding or insurance discussion

The shared surface is not allowed to consume the full local context by default. It receives only the projection that has been reviewed for the stated use.

## Projection Maps As Review Policies

A projection map is the path from a local record into a shared surface.

In the kit, projection maps already appear as:

- `allowed_projection`
- `allowed_fields`
- `excluded_fields`
- `not_established`
- `visibility_tier`
- `permission_state`
- `do_not_compute`
- `ai_use_receipt`
- `withdrawal_path`
- `display_approval`
- `content_mode`: `full_content`, `projection`, `marker_only`, `hash_only`, or `withheld`

The projection map should answer:

1. What source context exists?
2. What may cross into this shared surface?
3. What must stay out?
4. Who has standing to authorize the projection?
5. What does the projection not establish?
6. What downstream surfaces must update if the source is withdrawn, narrowed, or corrected?

## Obstructions As First-Class Findings

An obstruction is not a failure of the kit. It is the record of why gluing should stop.

Common obstruction classes:

| Obstruction | What It Means | Correct Handling |
| --- | --- | --- |
| `missing_authority` | The shared surface needs a move no one present has standing to authorize. | Return for authority review or preserve separate. |
| `visibility_conflict` | One record would need wider visibility than allowed. | Narrow the projection or block display. |
| `do_not_compute_conflict` | The composition would require indexing, summarizing, embedding, routing, or AI use of protected material. | Use marker-only reference or block the move. |
| `category_drift` | The projection changes speech act: dream to commitment, citation to claim, receipt to story, observation to attestation. | Require `templates/speech-act-transition.md`. |
| `purpose_mismatch` | Records can technically connect but not for the stated use. | Preserve separate or write a narrower intended use. |
| `incomparable_values` | Values or criteria cannot be ranked on one scale. | Use a trade-off surface, value-lens view, or preserve separate. |
| `display_boundary` | Internal coherence exists but public projection is not approved. | Keep display gate closed. |
| `lifecycle_conflict` | A stale, withdrawn, superseded, or composted record is being routed as active. | Run lifecycle review before composition. |

The composition engine can eventually report obstruction sites, but it should not override them.

## Refusals And Protocols As Fixed Boundary Conditions

The discourse-sheaf model has a useful analogy for stubborn or fixed agents. In Creator Jam, the fixed points are not just people being stubborn. They can be valid boundaries:

- a refusal
- a protocol requirement
- a `do_not_compute` flag
- a withdrawal
- a protected source
- a local-only record
- a display block
- a contributor-only authority move

The right question is not "how do we get around this boundary?"

The right question is:

> What can still compose while this boundary remains fixed?

That is the Creator Jam version of harmonic extension: a composition can adapt around fixed boundaries, or discover that no reviewed composition exists for the stated use.

## Expression-Map Dynamics

The most useful part of the opinion-dynamics frame is the distinction between changing opinions and changing expressions.

For Creator Jam, do not model coordination as:

```text
participants update private beliefs until they agree
```

Model it as:

```text
participants keep deeper contexts and authorities
shared projections become more precise, reviewed, and less extractive
```

This is the practical meaning of learning to coordinate without assimilation.

Examples:

- A contributor's dream does not become an obligation, but the projection can name a one-hour commitment if the contributor authorizes that exact move.
- A private allocation does not become routeable finance, but a summary-only receipt can record that the route is intentionally not legible.
- A citation does not become verified truth, but a claim review can produce a narrow claim with evidence limits.
- A witness record does not become ceremony or cultural authority, but a role-scoped reviewer receipt can travel with a fixture.

## Lattice And Partial-Order Note

Vector-space opinion models are useful, but Creator Jam values are not scalar.

Many Creator Jam states are partial-order or lattice-like:

- `ok`, `warn`, `block`
- `approved_for_fixture`, `review_required`, `blocked`, `non_composable`, `preserve_separate`
- public, local-only, private, protected, `do_not_display`
- active, narrowed, superseded, withdrawn, archived, composted
- comparable, incomparable, missing authority, outside scope

Some values should not be ranked. Some can meet at a more restrictive boundary. Some have no shared join for the stated use.

The lattice-sheaf direction is a better long-term operator model than scalar opinion intensity. It may help with value-lens views, trade-off surfaces, and lifecycle states. Keep it research-facing until a concrete fixture needs it.

## Threat Model

The control-theory side of discourse sheaves is useful as a warning.

If someone controls enough expression maps, reviewer roles, or shared surfaces, they may be able to create apparent consensus without legitimate authority or consent.

Creator Jam failure modes to watch:

| Failure Mode | What It Looks Like | Guardrail |
| --- | --- | --- |
| Apparent consensus | Shared outputs agree while local contexts were narrowed improperly. | Require transition receipts, authority records, and excluded-field review. |
| Reviewer capture | A small set of reviewers can steer many projections. | Separate authority from review; name reviewer role scope and support reviewer rotation. |
| Legibility pressure | Participants are pushed to expose more context to make a bundle work. | Allow marker-only, hash-only, withheld, non-composable, and preserve-separate results. |
| Public-story laundering | A receipt or witness rollup becomes endorsement. | Run display review for each surface and keep `not_established` visible. |
| AI expression control | AI rewrites participant language into stronger claims or commitments. | Treat AI output as proposal only; require human standing for speech-act transitions. |

## Minimal Trace Shape

If this becomes executable later, a diagnostic trace could include:

```yaml
surface_id:
surface_type: bundle_review | claim_review | commitment_pool | display_review | risk_packet | app_answer | other
local_contexts:
  - record_id:
    context_type: participant | steward | org | nation | project | protected_source | other
projection_maps:
  - source_record_id:
    target_surface_id:
    content_mode: full_content | projection | marker_only | hash_only | withheld
    authority_state: present | missing | refused | outside_scope
    allowed_fields:
      - 
    excluded_fields:
      - 
fixed_boundary_conditions:
  - record_id:
    boundary_type: refusal | protocol | do_not_compute | withdrawal | display_block | local_only | protected | other
obstructions:
  - obstruction_type:
    records:
      - 
    reviewer_note:
result:
  composition_disposition: approved_for_fixture | review_required | blocked | non_composable | preserve_separate
  diagnostic_status: ok | warn | block
  not_established:
    - 
```

## Operator Questions

Use these before applying sheaf language to a new fixture:

1. What are the local contexts?
2. What is the shared surface?
3. What projection maps are authorized?
4. What fixed boundaries must remain fixed?
5. Where do projections disagree?
6. Is the obstruction technical, epistemic, normative, relational, temporal, or display-related?
7. Does a narrower shared surface exist?
8. What must be preserved separate?
9. What changes if a source record is withdrawn or composted?
10. Would this framing help the operator, or is plain language enough?

## Source Map

Primary technical source:

- Jakob Hansen and Robert Ghrist, "Opinion Dynamics on Discourse Sheaves," arXiv: <https://arxiv.org/abs/2005.12798>; SIAM Journal on Applied Mathematics: <https://epubs.siam.org/doi/abs/10.1137/20M1341088>.

Kit sources this note extends:

- `workshop/composition-engine-technical-pattern.md`
- `workshop/spec-composition-lab.md`
- `workshop/coherence-vs-goodness.md`
- `templates/speech-act-transition.md`
- `workshop/transition-receipt-spec-v0.2.md`
- `examples/spec-experiments/claims-witness-receipt-composition/`
- `examples/spec-experiments/commitment-pool-dream-witness-composition/`
- `examples/spec-experiments/commitment-pool-untracked-allocation-blocked/`

## Boundary

This note should sharpen operator diagnosis. It should not become a demand that participants learn sheaf theory, a claim that mathematics authorizes a composition, or a reason to optimize the room toward consensus.

Use the math only where it helps preserve boundaries more clearly than plain language.
