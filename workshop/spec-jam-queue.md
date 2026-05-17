---
doc_kind: workshop-queue
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Spec Jam Queue

Use this queue when participants ask what to jam on. Each row can become a GitHub issue, a build attempt, or a spec-improvement session.

For composition experiments, start with `workshop/spec-composition-matrix.md`, use `examples/spec-experiments/` for fixture-backed tests, and then move candidate bundles into `workshop/candidate-bundle-board.md`.

| Track | Starting Spec | First Useful Jam Task | Notes |
| --- | --- | --- | --- |
| Witnessing and claims | `specs/witness-record-interop-profile.md` | Create witness record fixtures and a validator. | Good first build for schema, CLI, or UI contributors. |
| Claim review | `specs/claims-evidence-coherence-report.md` | Generate one markdown report from five sample claims. | Pairs well with reviewer-check templates. |
| Commitment pooling | `specs/commitment-pool-route-diagnostic.md` | Build a route diagnostic replay fixture. | Good for deterministic rules and repair paths. |
| Flow funding | `specs/flow-funding-frontier-map.md` | Render a ten-node frontier map. | Can compose with commitment pool diagnostics. |
| Allocation privacy | `specs/untracked-allocation-ledger.md` | Model public, private-summary, and deliberately untracked allocations. | Good policy/spec refinement task. |
| Bioregional mapping | `specs/bioregional-mapping-layer-board.md` | Create a ten-layer fictional catalog and visibility filter. | Avoid real sensitive locations. |
| Living atlas | `specs/living-atlas-coherence-packet.md` | Turn fictional workshop notes into a public-safe packet. | Good facilitation and data modeling task. |
| Bioregional insights | `specs/bioregional-insights-briefing.md` | Produce a steward-reviewed fictional watershed brief. | Needs clear citation and limitation language. |
| Insurance and risk | `specs/risk-insurance-coherence-map.md` | Create a one-page resilience packet with explicit non-underwriting boundaries. | Useful for insurance partners without building a premium model. |
| App gateway | `specs/indigenomics-ai-participant-gateway.md` | Prototype token redeem -> agreement receipt -> first offering. | Connects directly to Indigenomics AI web app work. |
| Graph/chat sidecar | `specs/indigenomics-ai-graph-chat-witness-sidecar.md` | Create one static graph node sidecar with citations, claims, and review state. | Connects directly to graph/chat app work. |
| Sensors | `specs/sensor-to-receipt-pipeline.md` | Create three observation packets and receipts. | Use fictional or public sample sensor data only. |
| Private learning | `specs/private-learning-ledger.md` | Generate a learning summary and withdrawal propagation report. | Good governance and data-sovereignty spec task. |
| Commitments | `specs/dream-to-fulfillment-board.md` | Render an eight-item board with transition diagnostics. | Helps participants see non-build offerings as valid. |
| Receipt wall | `specs/receipt-wall-story-gallery.md` | Build three story card fixtures. | Requires explicit display approval in real use. |
| Spec composition | `specs/spec-composer-bundle-board.md` | Compose six fragments into candidate bundles and one frozen build packet. | Good meta-build for the jam itself. |
| Waka / claims bridge | `workshop/waka-claims-engine-primitive-comparison.md` | Create one fictional primitive mapping receipt without implementing an adapter. | Keep Waka as Austin Wade Smith / RiverComputer's project; mapping is not adoption. |

## Facilitator Use

1. Ask the participant what they want to contribute: code, design, research, facilitation, policy, review, or spec writing.
2. Pick a row where their contribution can produce a small artifact in one sitting.
3. Record refusal boundaries before any build attempt.
4. If two or more rows fit together, move them to `workshop/candidate-bundle-board.md`.
