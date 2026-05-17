---
doc_kind: workshop-plan
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Tomorrow Spec Build Plan

This plan assumes tonight's work produces a composition matrix, a composition lab note, and a few fixture-backed spec experiments.

## Aim

Use tomorrow to move from a spec menu to evidence about composition:

- Which specs compose directly?
- Which specs compose only through review, consent, witness, or adapter steps?
- Which specs overlap and should be merged or clarified?
- Which specs should not compose, and what boundary explains that?
- Which specs are ready for prototype builds during the jam?

## Morning Pass

1. Review `specs/README.md` and pick 3-5 specs that feel most alive for the jam.
2. Open `workshop/spec-composition-matrix.md` and mark each chosen spec as direct, mediated, overlap, blocked, or unknown with the others.
3. Read `workshop/spec-composition-lab.md` if present and pull out the clearest experiment questions.
4. Decide whether sheaf-theory language is useful for the builder group or should remain an operator metaphor.

## Build Tracks

| Track | Starter Artifact | Build Goal |
| --- | --- | --- |
| Claims and witnessing | `examples/spec-experiments/claims-evidence-coherence/` | Turn sample claims into a reviewed report and witness receipt path. |
| Commitment pooling and flow | `examples/spec-experiments/commitment-pool-route/` | Turn candidate declarations into route diagnostics and flow-funding blockers. |
| Graph/chat sidecar | `examples/spec-experiments/graph-chat-witness-sidecar/` | Show how app answers expose citations, claims, evidence, review state, and AI-use receipts. |
| Sensor evidence | `examples/spec-experiments/sensor-to-receipt/` | Turn observations into evidence packets and receipts without overclaiming. |
| Composition board | `workshop/spec-composition-matrix.md` | Record which specs compose, overlap, or block each other. |

Starter fixture packets live in `examples/spec-experiments/`.

## Suggested First Bundle

Start with a three-spec composition:

1. `specs/claims-evidence-coherence-report.md`
2. `specs/witness-record-interop-profile.md`
3. `specs/receipt-wall-story-gallery.md`

Reason: this bundle is small, close to the current prototype, and tests a core pattern used by the rest of the system: evidence -> review -> witness -> public-safe receipt.

## Suggested Second Bundle

Then test a bioregional/resilience bundle:

1. `specs/sensor-to-receipt-pipeline.md`
2. `specs/claims-evidence-coherence-report.md`
3. `specs/risk-insurance-coherence-map.md`

Reason: this bundle forces the important boundary between "evidence for resilience review" and "insurance/underwriting inference." If it fails, the failure is useful.

## Suggested Third Bundle

Then test the app-facing bundle:

1. `specs/indigenomics-ai-participant-gateway.md`
2. `specs/spec-composer-bundle-board.md`
3. `specs/indigenomics-ai-graph-chat-witness-sidecar.md`

Reason: this connects participant entry, spec-driven development, and the Indigenomics AI web app surface.

## End-Of-Day Receipt

By the end of tomorrow, produce one receipt rollup that says:

- Specs attempted.
- Specs composed directly.
- Specs composed with mediation.
- Specs not composed and why.
- Shared fields that should become common schema fragments.
- Build artifacts created.
- Review or consent questions still open.

## Guardrails

- Composition is not consent.
- A cited answer is not a verified claim.
- A map is not authority.
- A risk packet is not an insurance model.
- A dream is not a commitment.
- A receipt records what happened; it does not certify legitimacy.
