---
doc_kind: workshop-analysis
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Coordination Canoe Weave Map

This is a map of the field before the next spec or build artifact is selected. It is not a new protocol, not a participant instruction packet, and not approval to process real participant material.

Use only fictional, public-sample, or explicitly approved material when testing any idea from this map.

## Central Field Question

Can a Creator Jam treat offerings, claims, commitments, refusals, evidence, review, witness records, build attempts, receipts, and display decisions as composable coordination primitives while preserving the speech-act boundaries, consent constraints, authority limits, and relationship context that make those records meaningful?

A shorter operator question:

What can participants safely bring, what can the kit safely carry, what can reviewers safely compose, and what must remain separate?

## What Participants Actually Encounter

Most participants should not need to understand the full architecture. Their direct surface is smaller:

1. Bring an offering, idea, spec, question, commitment, constraint, or refusal.
2. Turn it into a quick card or spec fragment.
3. See whether it fits with other fragments in a candidate bundle.
4. Review what the bundle would do, what it would not do, and what boundaries travel with it.
5. Freeze one selected bundle into build attempt instructions.
6. Attempt a build by hand, with code, or with an AI assistant.
7. Review what happened against acceptance criteria and refusal boundaries.
8. Record a receipt or witness rollup.
9. Run display review before any story, receipt wall item, slide, or public readout.

Operator-only surfaces include Waka comparison, Claims Engine bridge design, multi-witness runtime design, private learning, and any transcript-to-claims or transcript-to-commitments experiment.

## Field Shape

Coordination Canoe is the local working pattern for carrying offerings into reviewed composition. It is not a claims engine, not a Waka implementation, not ceremony, and not a replacement for human review.

The current field shape is:

```text
offering or fragment
  -> candidate record
  -> boundary and speech-act review
  -> candidate bundle
  -> selected bundle
  -> build attempt
  -> reviewer check
  -> witness or receipt rollup
  -> display review before public projection
```

The strongest current insight is that composition is not only a technical fit problem. It is a boundary-preservation problem.

## Primitive Maturity

| Maturity | Primitives | Current Evidence | Next Discipline |
| --- | --- | --- | --- |
| Well-defined in this kit | Offering quick card, spec fragment, candidate bundle, selected bundle, build attempt, review state, receipt, witness rollup, refusal boundary, visibility, intended use. | Templates, Open Kit flow, composition v0 example, common fields. | Keep participant-facing path simple. |
| Fixture-backed | Claims evidence -> witness record -> receipt/story candidate, commitment pool dream/witness composition, blocked commitment pool -> untracked allocation, display review walkthrough. | `examples/spec-experiments/` and `templates/display-review-checklist.md`. | Use fixtures as teaching examples, not proof of real-world readiness. |
| Spec-backed but not fully composed | Commitment pool, flow funding frontier, dream-to-fulfillment board, sensors, graph/chat sidecar, bioregional insights, risk/insurance, app gateway. | Draft specs in `specs/` and matrix rows. | Pick narrow fixtures that preserve boundaries. |
| Adjacent implementation surfaces | RegenAI Claims Engine, KOI/session and meeting-note processing, Indigenomics AI app, sensor pipelines. | Local implementation notes and working pipelines outside the kit. | Compose with reviewed projections instead of rebuilding infrastructure here. |
| External or posture-pending | Austin Wade Smith / RiverComputer Waka project. | Primitive comparison note and Austin posture question. | Wait for Austin's posture before writing an interop spec. |
| Exploratory and high-risk | Transcript -> claims, transcript -> commitments, automatic witness inference, ceremonial witnessing, insurance inference, public graph mutation. | Sketches and related work, but not a safe Creator Jam fixture yet. | Start with hazard maps or review-only sketches before build specs. |

## Composition Map

| Weave | Current Shape | Composition State | Boundary To Watch |
| --- | --- | --- | --- |
| Offering/spec -> candidate bundle -> selected build | Direct kit path. | Working prototype. | Composition does not create consent or erase refusal. |
| Evidence -> claim -> witness record -> receipt -> story candidate | Fixture-backed worked composition reference. | Usable as a teaching reference with display gates. | Citation is not a claim, receipt is not legitimacy, display review is per use. |
| Dream/offer/promise/refusal -> commitment pool -> flow funding | Spec-backed, partially blocked by allocation/privacy tensions. | Good next candidate after map review. | Dream is not commitment, support is not automatically routeable finance. |
| Conversation/transcript -> structured records -> claims or commitments | Adjacent pipelines exist, but this bundle is too large to build casually. | High-value, high-risk, not selected yet. | A transcript is not consent to extract claims or commitments. AI-inferred speech acts need human review. |
| Sensor/observation -> evidence packet -> claim/risk/insight | Spec-backed. | Strong boundary-stress candidate after reviewer pattern is stable. | Observation is not attestation. Risk signal is not underwriting or enforcement. |
| Bioregional mapping -> living atlas -> insights -> graph/chat sidecar | Spec-backed and app-relevant. | Likely adapter-mediated. | Sensitive places, local-only knowledge, and uncertainty must survive projection. |
| Claims Engine -> Coordination Canoe | Comparison-backed, not yet implemented. | Candidate bridge after narrow fictional mapping. | Verification state does not equal display approval or cultural authority. |
| Waka -> Claims Engine -> Coordination Canoe | Comparison-backed, Austin posture pending. | Do not write interop spec yet. | Mapping does not mean adoption; similar words can carry different epistemics. |
| Receipt wall -> public story -> team or participant readout | Display-review-backed. | Proceed only with exact display approval. | Public story does not establish legitimacy, certification, or reuse permission. |
| Private learning -> future recommendations | Spec-backed. | Keep separate from public projection. | Reviewed projections may be learned from; raw protected material and `do_not_compute` records may not. |

## Boundary Map

| Boundary | Do Not Collapse Into | Required Guardrail |
| --- | --- | --- |
| Citation | Verified claim | Speech-act transition and claim review. |
| Observation | Attestation | Reviewer or witness record with scoped authority. |
| Dream | Commitment | Explicit participant transition and withdrawal path. |
| Offer | Promise | Role, scope, time window, and acceptance state. |
| Promise | Witnessed commitment | Witness or reviewer receipt with exact meaning. |
| Software witness record | Ceremonial witnessing or cultural authority | Explicit non-ceremonial disclaimer and role-only reviewer type. |
| Receipt | Legitimacy, certification, or permission | Obstruction marker naming what the receipt does not establish. |
| Anchor | Consent or completeness | Visibility, intended use, withdrawal, and display review fields. |
| Transcript | Consent to extract | Consent state, exact intended use, and human review. |
| Public sample | Participant approval | Fixture-only language and no transfer to real people. |
| Risk signal | Underwriting or enforcement | Non-underwriting boundary and steward review. |
| Allocation note | Routeable financial instruction | Public/private/untracked distinction and no automatic routing. |

## Existing Infrastructure To Compose With

The kit should not rebuild every adjacent capability. It should name what it can compose with, what it needs as a reviewed projection, and what must stay outside the jam surface.

| Surface | Existing Role | How The Kit Should Touch It |
| --- | --- | --- |
| Meeting notes and transcript processing | Transcripts can become structured notes, people links, action items, and Notion or vault records. | Consume reviewed projections only. Do not make transcript extraction a participant-facing commitment engine without a separate review path. |
| KOI/session indexing | Sessions, entities, facts, and related documents can be indexed and retrieved. | Treat as evidence/search infrastructure, not as consent or display approval. |
| RegenAI Claims Engine | Claim, evidence, verification, anchoring, extraction, and withdrawal rail. | Bridge through sample claims and explicit transition records before any operational adapter. |
| Waka | External witness, claim, identity, anchoring, and issuance design space. | Wait for Austin's posture. Keep Waka as Austin Wade Smith / RiverComputer's project. |
| Multi-witness inference | Runtime pattern for intent, retrieval, answer, voice, citation, worldview, and composition audits. | Useful for app runtime design, but not a replacement for human or protocol review. |
| Discourse graph as yarning | Possible conversation and annotation graph pattern. | Treat as yarning/sketch until sovereignty, witness, and implementation falsifiers are checked. |
| Indigenomics AI app | Participant gateway, graph/chat sidecar, display surfaces, and AI-use receipts. | Use the kit to produce fixture-backed app requirements and review gates. |
| Sensor pipelines | Observation packets, evidence receipts, and field signals. | Use fictional or public sample data unless sensitive-location review clears exact use. |

## Where Coherence Lives

Coherence appears in several layers at once:

- Shared fields: `visibility_tier`, `review_state`, `evidence_pointers`, `witness_records`, `receipt_policy`, `do_not_compute`, `bioregion_uri`, `intended_use`, withdrawal path, and display approval.
- Speech-act transitions: citation to claim, observation to attestation, dream to commitment, witness record to attribution, receipt to story, and route diagnostic to funding discussion.
- Review paths: who reviews, what they are allowed to approve, and what they are not approving.
- Boundary preservation: refusals, local-only records, protected fields, sensitive locations, private allocations, and not-for-computation states.
- Evidence movement: whether evidence can be cited, summarized, displayed, routed, indexed, anchored, or only pointed to.
- Public projection: what survives when a record becomes a story, wall item, slide, app card, or briefing.
- Repair paths: what happens when something is stale, contested, missing permission, overbroad, or outside authority.
- Human meaning: participant intent, steward judgment, cultural authority, relationship, and context that should not be flattened into a software field.

## What Should Stay Separate For Now

These separations are not defects. They are useful discoveries:

- Ceremony, protocol authority, and cultural witnessing should remain separate from software witness records.
- Waka interop should remain separate from Waka comparison until Austin's posture is known.
- Conversation-to-claims and conversation-to-commitments should remain separate from participant-facing flows until a human-reviewed fixture proves the transition discipline.
- Insurance underwriting should remain separate from resilience, risk, and bioregional insight packets.
- Private learning should remain separate from public stories and receipt walls.
- Sensitive bioregional mapping should remain separate from graph/chat display unless exact review clears the projection.
- Untracked allocation should remain separate from routeable commitment pools unless the participant has explicitly made it trackable.

## Likely Next Experiments Revealed By The Map

Do not treat this list as today's build order. Pick the next artifact after reviewing this map.

| Candidate | Why It Matters | Smallest Useful Artifact |
| --- | --- | --- |
| Commitment Pool + Dream/Fulfillment + Witness mini-fixture | Tests whether offers, promises, refusals, and witnessed commitments compose before adding transcript inference. | Added as `examples/spec-experiments/commitment-pool-dream-witness-composition/`; use review feedback before extending it. |
| Conversation-to-records hazard map | Names the exact risk modes before a transcript-to-claims or transcript-to-commitments spec. | Review-only hazard map with examples of what must not be inferred. |
| Sensors + Claims + Risk boundary stress test | Exercises observation, evidence, claim, risk, and non-underwriting boundaries. | Three fictional observation packets, one claim candidate, one risk note with obstruction markers. |
| App Gateway + Graph/Chat Sidecar fixture | Connects directly to the Indigenomics AI web app and AI-use receipt discipline. | One participant gateway sample, one sidecar card, one AI-use receipt, one display review state. |
| Waka/Claims Engine fictional mapping receipt | Tests bridge language without representing Austin's implementation direction. | One fictional claim primitive mapped across surfaces with mismatch notes. |
| Bioregional Atlas + Insights packet | Tests place, uncertainty, steward review, and public projection. | One fictional watershed packet with source visibility and limitation language. |

## Decision Questions Before Artifact Two

1. Is the central field question the right one for the Creator Jam?
2. Should the next fixture test commitment-pool composition before any transcript-to-claims or transcript-to-commitments work?
3. What external surface matters most tomorrow: participant kit, Eve/Shawn review, Austin conversation, Carol Anne naming/protocol question, or app requirements?
4. Which surfaces should remain operator-only during the jam?
5. Does optional sheaf-theory language help operators find obstructions, or should it stay out of the kit for now?
6. What would make the next artifact useful for a participant in one sitting?

## Queued Review And Authorization Items

| Item | Status | Note |
| --- | --- | --- |
| Austin / Waka posture | Message sent in relationship channel. | Wait for posture before writing any Waka interop spec. |
| Carol Anne language term question | Optional, not a blocker for the English working metaphor. | If asked, make it an invitation about whether there is a term she would want used, not a request to bless this document. |
| Eve/Shawn team review note | Needs refresh before dispatch. | The kit now includes speech-act transitions, worked and blocked examples, display review, Waka comparison, and this map. |
| Matrix row for Waka comparison | Still open. | Add during EOD rollup or the next matrix pass. |
| Story-card display reviewer role | Done in current fixture. | Keep exact display approval separate from fixture approval. |
| Transition risk callout in composition report | Done in current fixture. | Preserve this as a pattern for later reports. |

## Source Map

Primary kit sources:

- `workshop/spec-composition-lab.md`
- `workshop/spec-composition-matrix.md`
- `workshop/common-spec-fields.md`
- `workshop/waka-claims-engine-primitive-comparison.md`
- `templates/speech-act-transition.md`
- `templates/display-review-checklist.md`
- `examples/spec-experiments/claims-witness-receipt-composition/`
- `examples/spec-experiments/commitment-pool-untracked-allocation-blocked/`
- `specs/commitment-pool-route-diagnostic.md`
- `specs/dream-to-fulfillment-board.md`
- `specs/indigenomics-ai-graph-chat-witness-sidecar.md`
- `specs/private-learning-ledger.md`
- `specs/sensor-to-receipt-pipeline.md`
- `specs/bioregional-insights-briefing.md`

Adjacent local sources used for orientation:

- `/Users/darrenzal/projects/IndigenomicsAI/docs/synthesis/discourse-graph-as-yarning.md`
- `/Users/darrenzal/projects/IndigenomicsAI/docs/specs/multi-witness-inference-v0.md`
- `/Users/darrenzal/projects/IndigenomicsAI/docs/specs/jam-ceremony-as-commitment-pool-v0.md`
- `/Users/darrenzal/projects/IndigenomicsAI/docs/specs/jam-witness-ceremony-v0-sketch.md`
- `/Users/darrenzal/projects/RegenAI/koi-processor/docs/claims/team-commitment-stewardship.md`
- `/Users/darrenzal/projects/RegenAI/docs/strategy/regen-ai-vision.md`
- `/Users/darrenzal/projects/darren-workflow/skills/meeting-notes/SKILL.md`

## Recommended Pause

Review this map before selecting the next artifact. The strongest current signal is that commitment pooling, claims, witnessing, receipts, Waka, sensors, bioregional insight, and conversation processing are part of one broad coordination field, but they are not all equally ready to compose.

The next artifact should be chosen because this map reveals it as the highest-leverage test, not because it was already on the idea list.
