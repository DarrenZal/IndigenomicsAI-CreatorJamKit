---
doc_kind: example-index
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Spec Experiments

These examples turn draft specs into fixture-backed experiments. They are not production systems. They are public-sample packets for discovering whether specs compose, where review is required, and where a boundary should stop composition.

## Current Experiment Packets

| Experiment | Source Spec | What It Tests |
| --- | --- | --- |
| [Claims Evidence Coherence](claims-evidence-coherence/) | `specs/claims-evidence-coherence-report.md` | Five fictional claims, six evidence pointers, status diagnostics, and a static report. |
| [Commitment Pool Route](commitment-pool-route/) | `specs/commitment-pool-route-diagnostic.md` | Three candidate declarations, two pools, route readiness, capacity block, and share-policy block. |
| [Graph Chat Witness Sidecar](graph-chat-witness-sidecar/) | `specs/indigenomics-ai-graph-chat-witness-sidecar.md` | One graph node, one chat answer, citations, claims, review state, and AI-use receipt. |
| [Sensor To Receipt](sensor-to-receipt/) | `specs/sensor-to-receipt-pipeline.md` | Three observation packets and public-safe witness receipts. |

## How To Use These

1. Pick one experiment packet.
2. Read the source spec.
3. Open the fixture JSON and output report.
4. Mark the experiment in `workshop/spec-composition-matrix.md` as direct, mediated, overlap, blocked, or unknown.
5. If the experiment composes with another spec, move it to `workshop/candidate-bundle-board.md`.

## Guardrails

- Fixtures are fictional or public-sample only.
- A passing fixture does not prove real-world consent, authority, legitimacy, production readiness, or cultural fit.
- Do not replace reviewer decisions with deterministic checks.
- Treat blocked or non-composable results as valid discoveries.
