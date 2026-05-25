---
doc_kind: spec-index
status: v0-1
visibility: public_sample
last_updated: 2026-05-25
---

# Creator Jam Spec Backlog

This directory is a menu of participant-safe specs for the Creator Jam. Each card can be used in three ways:

- Build the spec as a small prototype.
- Improve the spec by sharpening inputs, outputs, acceptance criteria, or refusal boundaries.
- Compose two or more specs into a candidate bundle for a collective build.

These are sample/public working specs. Do not add protected, Nation-specific, ceremonial, participant-private, credential-bearing, or authority-bound material unless the right authority has explicitly approved that exact use.

## Tag legend

- **Difficulty**: 🟢 good-first-build (single-file CLI, 2–4h) · 🟡 intermediate (single-file CLI but trickier rules) · 🔵 composition-required (works with another spec) · ⚪ doc-shaped (UI / mock / kanban)
- **Boundary weight**: light · medium · heavy (heavy = many simultaneous consent/visibility/refusal markers)
- **Preflighted**: ✅ both models clean · ⚠️ one model clean · ❌ both partial · — not yet
- See `preflights/README.md` for full preflight data; `docs/MENTOR_FIELD_GUIDE.md` for spec-to-team-shape recommendations.

## Ready-To-Jam Specs

| Area | Spec | Difficulty | Boundary | Preflight | Good for |
| --- | --- | --- | --- | --- | --- |
| Witnessing and claims | [Witness Record Interop Profile](witness-record-interop-profile.md) | 🟢 | medium | ❌ | Portable witness records across claims, receipts, attestations, and promises. |
| Witnessing and claims | [Claims Evidence Coherence Report](claims-evidence-coherence-report.md) | 🟡 | medium | ⚠️ Qwen | Reviewing whether a public claim has enough evidence, freshness, and permission context. |
| Commitment pooling | [Commitment Pool Route Diagnostic](commitment-pool-route-diagnostic.md) | 🔵 | light | (sample at `examples/sample-submission-commitment-pool/`) | Checking whether offers, needs, commitments, and refusals can route into a pool. |
| Flow funding | [Flow Funding Frontier Map](flow-funding-frontier-map.md) | 🔵 | medium | — | Mapping the next fundable edges between dreams, commitments, pools, receipts, and retroactive support. |
| Flow funding | [Untracked Allocation Ledger](untracked-allocation-ledger.md) | 🟢 | heavy | ✅ | Recording allocations without turning every gift into surveillance or performance accounting. |
| Bioregional mapping | [Bioregional Mapping Layer Board](bioregional-mapping-layer-board.md) | 🔵 | heavy | — | Building a multi-layer place map that can hold ecological, cultural, economic, and governance layers with consent boundaries. |
| Bioregional insights | [Living Atlas Coherence Packet](living-atlas-coherence-packet.md) | 🔵 | heavy | — | Turning workshop or field contributions into a reviewable atlas packet. |
| Bioregional insights | [Bioregional Insights Briefing](bioregional-insights-briefing.md) | 🔵 | medium | — | Producing steward-reviewed briefs from atlas records, evidence, and sensor signals. |
| Insurance and risk | [Risk and Insurance Coherence Map](risk-insurance-coherence-map.md) | 🔵 | medium | — | Showing resilience risk signals without becoming a premium, underwriting, or actuarial model. |
| Indigenomics AI web app | [Participant Gateway](indigenomics-ai-participant-gateway.md) | ⚪ | medium | — | Improving the invite, token, consent, and entry flow for jam participants. |
| Indigenomics AI web app | [Graph Chat Witness Sidecar](indigenomics-ai-graph-chat-witness-sidecar.md) | ⚪ | medium | — | Connecting graph/chat/citation surfaces to claims, evidence, and witness records. |
| Sensors | [Sensor To Receipt Pipeline](sensor-to-receipt-pipeline.md) | 🟢 | heavy | ✅ | Turning sensor or field observations into reviewable evidence packets and receipts. |
| Private learning | [Private Learning Ledger](private-learning-ledger.md) | 🔵 | heavy | — | Letting systems learn from reviewed actions without training on raw protected data. |
| Commitments | [Dream To Fulfillment Board](dream-to-fulfillment-board.md) | 🔵 | light | — | Tracking dreams, offers, needs, promises, witnessed commitments, and fulfillment receipts. |
| Public receipt surfaces | [Receipt Wall Story Gallery](receipt-wall-story-gallery.md) | 🟡 | medium | (sample at `examples/sample-submission-receipt-wall/`) | Publishing sample-safe witness rollups and build stories. |
| Spec-driven development | [Spec Composer Bundle Board](spec-composer-bundle-board.md) | ⚪ | light | — | Composing participant spec fragments into candidate collective builds. |

**Good-first-builds spot-checked by TELUS lane overnight (Mon 2026-05-25)**:
- ✅ **Sensor To Receipt Pipeline** — both Gemma + Qwen 6/6 clean
- ✅ **Untracked Allocation Ledger** — both Gemma + Qwen 6/6 clean
- ⚠️ **Claims Evidence Coherence Report** — Qwen 8/8 clean; Gemma 7/8 partial (recommend specifying Qwen, or sharpen the as_of CLI arg handling)
- ❌ **Witness Record Interop Profile** — both partial on as_of CLI arg handling (sharpen spec before recommending)

See `preflights/` for the full data.

## Composition Prompts

Useful bundles to test during the jam:

- Claims + witness + receipt wall: `claims-evidence-coherence-report` + `witness-record-interop-profile` + `receipt-wall-story-gallery`.
- Commitment pool + flow funding: `commitment-pool-route-diagnostic` + `flow-funding-frontier-map` + `untracked-allocation-ledger`.
- Bioregional atlas + sensors + insights: `bioregional-mapping-layer-board` + `sensor-to-receipt-pipeline` + `living-atlas-coherence-packet` + `bioregional-insights-briefing`.
- Risk and resilience: `risk-insurance-coherence-map` + `sensor-to-receipt-pipeline` + `claims-evidence-coherence-report`.
- Indigenomics AI app path: `indigenomics-ai-participant-gateway` + `spec-composer-bundle-board` + `graph-chat-witness-sidecar`.

## Brainstorm Seeds

These are not full cards yet, but they are good candidates for future specs:

- Indigenous business network map with consent-gated visibility tiers.
- Protocol translation lab for moving between ceremony language, software language, and funder language without flattening meaning.
- Withdrawal propagation dashboard for seeing which public surfaces need to change when consent changes.
- Stewardship role directory that records responsibilities without publishing private governance structure.
- Treaty witness timeline with explicit non-authority and non-certification boundaries.
- Bioregional repair path console for turning diagnostics into next responsible actions.
- Participant AI use receipt that records what material an assistant touched, what it produced, and who reviewed it.
- Data residency and local-first jam kit for groups that cannot use cloud-hosted AI services.

## Source Notes

This backlog was synthesized from local IndigenomicsAI, bioregional-coordination, bioregional-mapping, and RegenAI working materials. The cards are participant-safe summaries, not direct copies of private source documents.
