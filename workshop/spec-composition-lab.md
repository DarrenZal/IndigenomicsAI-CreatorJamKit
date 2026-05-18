---
doc_kind: workshop-lab
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Spec Composition Lab

Use this lab to discover which Creator Jam specs can compose into useful bundles, which ones should stay separate for now, and where the real coherence work lives.

This is an experiment protocol, not an academic exercise. The goal is to help participants, builders, reviewers, and facilitators make clear choices by the end of the jam.

## Participant-Safe Frame

Use only public sample material, fictional fixtures, or participant material that has been explicitly approved for this exact use.

Do not bring protected, Nation-specific, ceremonial, participant-private, credential-bearing, authority-bound, sensitive-location, or local-only content into the lab unless the right authority has approved that exact use. You can always mark something as "review required", "protect and preserve", "local-only", "do not compute", or "does not fit yet" without exposing the protected material itself.

Composition does not create consent. A bundle can look technically elegant and still be blocked by permission, authority, review, or purpose.

## Source Specs

Start from the specs in `specs/`. The most useful source map is:

- `specs/README.md` for the ready-to-jam list and suggested bundles.
- `specs/spec-composer-bundle-board.md` for the meta-composition workflow.
- `specs/witness-record-interop-profile.md`, `specs/claims-evidence-coherence-report.md`, and `specs/receipt-wall-story-gallery.md` for claims, witness records, evidence, review, and public receipt surfaces.
- `specs/commitment-pool-route-diagnostic.md`, `specs/flow-funding-frontier-map.md`, `specs/untracked-allocation-ledger.md`, and `specs/dream-to-fulfillment-board.md` for commitments, pools, flow, refusal, and allocation privacy.
- `specs/bioregional-mapping-layer-board.md`, `specs/sensor-to-receipt-pipeline.md`, `specs/living-atlas-coherence-packet.md`, `specs/bioregional-insights-briefing.md`, and `specs/risk-insurance-coherence-map.md` for place, sensors, atlas records, insight generation, and risk boundaries.
- `specs/indigenomics-ai-participant-gateway.md`, `specs/indigenomics-ai-graph-chat-witness-sidecar.md`, and `specs/private-learning-ledger.md` for app entry, AI use receipts, citation review, and learning boundaries.

## Executable Fixture Diagnostics

Run `python3 scripts/composition_engine.py examples/spec-experiments/<experiment-dir> --write` to generate a human-readable diagnostic report and machine-readable trace for any fixture-backed experiment.

## Experiment Questions

Ask these questions before trying to build anything:

1. What purpose would the bundle serve tomorrow?
2. Which inputs are shared across the specs?
3. Which outputs from one spec can become allowed inputs for another?
4. What review, consent, visibility, or refusal states must survive composition?
5. Where does evidence travel, and where must it stop?
6. Which fields mean the same thing across specs, and which only look similar?
7. What gets duplicated if the specs are merged too quickly?
8. Which participant intent, boundary, or role could be changed by accident?
9. What would make this bundle misleading if shown publicly?
10. What is the smallest fixture that would teach us whether the bundle works?

## Composition States

Use these states in the matrix and bundle board.

| State | Meaning | Jam action |
| --- | --- | --- |
| `ready_to_compose` | The specs share a purpose, compatible fields, and compatible boundaries for a small sample build. | Create a fixture and build attempt instructions. |
| `composes_with_review` | The shape fits, but a reviewer must check consent, visibility, evidence, authority language, or public display. | Add to review queue before freezing the bundle. |
| `partial_overlap` | Some fields or outputs connect, but the specs serve different purposes. | Build only the connecting piece; leave the rest separate. |
| `duplicate_overlap` | Two specs create similar records, screens, or diagnostics. | Pick one owner or define a handoff to avoid double-entry. |
| `blocked_until_repair` | A missing field, stale evidence, unclear permission, or unresolved dependency blocks the bundle. | Name the repair path and do not build around the gap. |
| `non_composable` | The specs conflict in purpose, authority, consent, or refusal boundaries. | Keep separate and record why. |
| `protect_separate` | The spec can only be represented as present, protected, or review-required in this lab. | Preserve the boundary; do not simulate protected content. |

## Where Coherence Lives

Coherence is not only in a schema. In these specs, coherence usually lives in one or more of these places:

- Shared field meaning: `visibility_tier`, `review_state`, `evidence_pointers`, `witness_records`, `time_window`, `freshness`, `restrictions`, and `do_not_compute`.
- Purpose: the intended use of a claim, map, pool, receipt, insight, or gateway step.
- Review path: who must review, what they are reviewing, and what decision states are allowed.
- Boundary preservation: refusals, local-only records, protected fields, sensitive locations, and not-for-computation states.
- Evidence movement: whether evidence can be cited, summarized, displayed, routed, or only pointed to.
- Public projection: what can be shown without leaking private context.
- Repair path: the next responsible action when a record is missing evidence, stale, contested, blocked, or overbroad.
- Human meaning: participant intent, steward judgment, cultural authority, relationship, and context that should not be flattened into software fields.

When a bundle fails, look first at these coherence points before changing the specs.

## Overlap Types

Name the type of overlap before deciding whether it is useful.

| Overlap type | What it looks like | Example from the spec set |
| --- | --- | --- |
| Productive handoff | One spec output is a clean input to another. | `sensor-to-receipt-pipeline` creates evidence packets that can inform `claims-evidence-coherence-report`. |
| Shared boundary | Specs depend on the same consent, visibility, or refusal rule. | `participant-gateway`, `private-learning-ledger`, and `receipt-wall-story-gallery` all need explicit approval boundaries. |
| Shared evidence | Multiple specs need the same evidence pointer, source, freshness, or reviewer context. | Claims, risk, insights, sensors, and graph/chat sidecars all touch evidence. |
| Shared witness | Multiple specs need witness records, receipts, or reviewer checks. | Witness records can support claims, commitments, fulfillment, and receipt wall stories. |
| Dependency | One spec is not useful until another produces a needed record. | A public receipt wall story should wait for reviewer checks and display approval. |
| Diagnostic overlap | Two specs both identify gaps, blockers, or repair paths. | Commitment routing, claims coherence, atlas packets, and risk maps all produce diagnostics. |
| Output surface overlap | Two specs want to publish similar cards, reports, or summaries. | Insights briefs, receipt wall stories, and public atlas packets can duplicate public narrative surfaces. |
| Duplication risk | Two specs record the same thing under different names. | `review_state`, reviewer decisions, evidence freshness, and public-safe summaries may be double-entered. |
| Boundary collision | Two specs want incompatible uses of the same material. | A sensor packet may be usable for local review but not for public risk mapping. |

## Non-Composability Reasons

Use plain reasons. Avoid treating "does not fit" as failure.

- The intended uses differ too much.
- One spec requires public display while another only permits local or private use.
- The bundle would turn a refusal into a backlog item or route around it.
- Evidence is missing, stale, contested, or not approved for the new use.
- A shared field has different meanings in different specs.
- The bundle would imply authority, certification, legitimacy, eligibility, pricing, underwriting, compliance, or investment advice.
- Sensitive location, cultural, governance, or private participant context would be exposed.
- A human review decision is being replaced by automation.
- The composition would require protected data to make the demo convincing.
- The bundle creates duplicate ledgers, duplicate receipts, duplicate diagnostics, or unclear ownership.
- The output would make uncertainty look resolved.
- The repair path is known, but cannot be completed during the jam.

## Optional Sheaf Language

Use this only if it helps the room. Do not force it.

Plain version:

- Each spec is a local view of the jam.
- Shared fields are the places where local views overlap.
- A bundle works when the overlapping parts agree well enough for the stated purpose.
- A bundle fails when the overlaps disagree, hide a boundary, or require information that cannot be shared.
- A public output is a projection: it shows only the parts approved for that surface.

Light sheaf version:

- A spec is like a local section.
- An overlap is where two local sections describe the same thing.
- A restriction is the participant-safe view that can move from one context to another.
- Gluing is the act of forming a bundle when overlaps agree.
- An obstruction is the reason gluing should stop: consent, stale evidence, incompatible purpose, protected context, duplication, or unresolved review.

Facilitator note: if the word "sheaf" slows the room down, drop it. The lab works with the plain version.

## Sample Matrix

This is a starting matrix. Update it during the lab.

| Candidate bundle | Source specs | Main overlap | Composition state | Review required | Duplication or stop point |
| --- | --- | --- | --- | --- | --- |
| Claims + Witness + Receipt Wall | `claims-evidence-coherence-report`, `witness-record-interop-profile`, `receipt-wall-story-gallery` | Claim status, evidence pointers, witness records, public receipts | `composes_with_review` | Evidence visibility, reviewer status, display approval | Do not duplicate reviewer checks across claim report and story card. |
| Commitment Pool + Flow Funding + Allocation | `commitment-pool-route-diagnostic`, `flow-funding-frontier-map`, `untracked-allocation-ledger` | Offers, needs, commitments, pools, receipts, allocation privacy | `partial_overlap` | Pool rules, consent to route, capacity, allocation visibility | Stop if a graph edge starts acting like consent or financial advice. |
| Bioregional Atlas + Sensors + Insights | `bioregional-mapping-layer-board`, `sensor-to-receipt-pipeline`, `living-atlas-coherence-packet`, `bioregional-insights-briefing` | Place layers, observation packets, atlas records, citations, public-safe briefs | `composes_with_review` | Sensitive locations, source authority, steward review, freshness | Do not turn raw observations into verified public claims. |
| Risk + Sensors + Claims | `risk-insurance-coherence-map`, `sensor-to-receipt-pipeline`, `claims-evidence-coherence-report` | Hazard signals, local observations, evidence freshness, claim status | `blocked_until_repair` | Insurance boundaries, sensitive sites, stale signals, intended use | Stop before premium, underwriting, eligibility, or actuarial language. |
| Indigenomics AI App Flow | `indigenomics-ai-participant-gateway`, `spec-composer-bundle-board`, `indigenomics-ai-graph-chat-witness-sidecar` | Consent entry, bundle selection, citations, AI use receipt, review flags | `ready_to_compose` for fictional fixtures; `composes_with_review` for real participants | Gateway agreement, AI use preference, protected source handling | Token redemption must not become publication consent. |
| Dream To Fulfillment + Witness + Flow | `dream-to-fulfillment-board`, `witness-record-interop-profile`, `flow-funding-frontier-map` | Promises, witnessed commitments, fulfillment receipts, funding edges | `partial_overlap` | Witness context, commitment visibility, fulfillment evidence | Do not force dreams or care into delivery logic. |
| Private Learning + Any Public Surface | `private-learning-ledger` plus receipt wall, insights, graph/chat, or atlas outputs | Reviewed projections, withdrawal propagation, do-not-compute status | `protect_separate` until reviewed | Raw data exclusion, withdrawal/correction, public projection | Do not train, summarize, route, embed, or display `do_not_compute` records. |

## Five Candidate Experiments

Run these as small tests. Each experiment should produce a fixture, a matrix update, a review note, and a short "what we learned" receipt.

### 1. Claims, Witness, Receipt Wall

Question: Can a claim report, witness record, and public story card share one evidence and review trail without implying certification?

Try:

- Create two fictional claims, three evidence pointers, one witness record, and one story card.
- Mark one claim `ready_for_use` and one `needs_review`.
- Show how the receipt wall displays only approved public fields.

Watch for:

- Reviewer status duplicated in multiple places.
- Private evidence leaking into public story copy.
- Witness language sounding like proof of cultural authority.

Output:

- One mini report, one witness card, one receipt wall story, and one display approval diagnostic.

### 2. Commitment Pool, Flow Funding, Allocation Privacy

Question: Can offers, needs, commitments, pools, and allocations connect without turning relational generosity into surveillance?

Try:

- Create three fictional declarations, two candidate pools, three graph edges, and three allocation records.
- Include one route-ready record, one capacity block, and one deliberately untracked allocation.
- Show where the flow map points to the allocation ledger without exposing amount, funder, or recipient.

Watch for:

- Routing around refusals.
- Treating a graph edge as consent.
- Making allocation visibility more public than the original record allows.

Output:

- One route diagnostic, one frontier map sketch, one not-tracked register entry, and one stop condition.

### 3. Bioregional Atlas, Sensors, Insights

Question: Can place layers, sensor observations, atlas records, and briefs compose while preserving sensitive locations and local review?

Try:

- Create a fictional watershed with five layers, three observations, two atlas records, and one short insight brief.
- Include one sensitive-location flag, one stale signal, and one local-only record.
- Reduce location precision for public output.

Watch for:

- Raw sensor readings becoming verified claims.
- Cultural or ecological layers being exposed by summary.
- The brief sounding more certain than the source records allow.

Output:

- One layer board slice, three observation packets, one atlas coherence packet, one brief, and one limitation note.

### 4. Risk, Sensors, Claims

Question: Can risk signals and evidence review produce a resilience diagnostic without becoming insurance scoring?

Try:

- Create one fictional watershed risk packet with two public layers, one local observation, one sensor summary, and two claims.
- Mark one signal stale and one claim overbroad.
- Add two candidate resilience actions for steward review.

Watch for:

- Premium, underwriting, eligibility, compliance, or actuarial language.
- Risk inferred for a person, household, or private property.
- Public layers mixed with local-only observations.

Output:

- One risk coherence packet, one claims repair list, and one boundary statement suitable for a reviewer.

### 5. Gateway, Spec Composer, Graph/Chat Sidecar

Question: Can a participant enter the jam, select a bundle, and see AI-assisted citations without confusing access, consent, and publication?

Try:

- Create one fictional invite token, agreement receipt, offering quick-card, candidate bundle, graph node, chat answer, and citation sidecar.
- Record AI use preference separately from public display consent.
- Show one claim with stale evidence and one source marked local-only.

Watch for:

- Token redemption being treated as consent to publish.
- Citations being treated as verified claims.
- AI summaries hiding source status or reviewer status.

Output:

- One gateway receipt, one selected bundle receipt, one sidecar fixture, and one AI use receipt.

## Review Protocol

Use this protocol for each candidate bundle.

1. Name the purpose.
   - What are we trying to learn or build by tomorrow?
   - Who is the output for?

2. Inventory the specs.
   - Which specs are included?
   - Which inputs, outputs, acceptance criteria, and refusal boundaries matter most?

3. Mark allowed material.
   - Public sample, fictional, local-only, review-required, protected, or do-not-compute.
   - If any protected material is necessary for the demo, stop and redesign the fixture.

4. Map overlaps.
   - Shared fields.
   - Handoffs.
   - Duplicated records.
   - Boundary collisions.
   - Missing fields or stale evidence.

5. Assign a composition state.
   - Use one state from the composition state table.
   - Record why in one sentence.

6. Build the smallest fixture.
   - Use fictional or sample-safe records.
   - Include at least one blocker, one review-needed state, and one public-safe output.

7. Review before display.
   - Check consent, visibility, evidence, authority language, sensitive locations, AI use, and withdrawal or correction paths.
   - Do not display a receipt, story, claim, map, or brief without explicit display approval.

8. Record the result.
   - Fit.
   - Does not fit yet.
   - Repair path.
   - Duplication found.
   - Open question.
   - Next responsible action.

## Lab Worksheet

Copy this block for each experiment.

```md
## Bundle Name

Purpose:

Included specs:

Allowed material:

Shared fields:

Handoffs:

Boundary checks:

Overlap type:

Composition state:

Duplication found:

Does not fit yet:

Repair path:

Public output allowed:

Review required:

What we learned:
```

## Outputs For Tomorrow

By the next working session, aim to have:

- A filled composition matrix with at least five candidate bundles.
- One selected bundle that is small enough for a build attempt.
- One `does-not-fit-yet` list that protects material instead of discarding it.
- One overlap and duplication list with proposed owners or handoffs.
- One non-composability list with plain reasons.
- One review queue for consent, visibility, evidence, authority language, sensitive locations, AI use, and display approval.
- One set of fictional fixtures for the selected bundle.
- One frozen build-attempt instruction packet.
- One witness receipt that records what was tried, what fit, what did not fit, what was refused, what was protected, and what remains unresolved.
- Optional: one lightweight sheaf note translating the experiment into local sections, overlaps, gluing, and obstructions, only if it helped the room think clearly.

## Facilitator Closing Questions

Ask these before freezing any build:

1. What composed cleanly?
2. What composed only with review?
3. What should stay separate?
4. Where did duplication appear?
5. What boundary protected the most meaning?
6. What is the smallest next build that respects the review queue?
