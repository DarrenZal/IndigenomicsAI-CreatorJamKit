# Indigenomics AI Creator Jam Kit

Private working repo for Creator Jam participants, facilitators, and invited reviewers.

This repo is for public, sample, or explicitly display-approved material only. Do not add protected, cultural, linguistic, ceremonial, Nation-specific, participant-private, credential-bearing, or authority-bound material unless the right authority has explicitly approved that exact use.

## What You Can Do Here

- Bring an offering, idea, spec, question, commitment, or refusal.
- Turn an offering into a small spec fragment.
- Compose fragments into candidate bundles.
- Freeze one selected bundle into build attempt instructions.
- Attempt a build by hand, with code, or with an AI assistant.
- Review what happened against acceptance criteria and refusal boundaries.
- Record a witness rollup or receipt event.

## Fast Path

1. Read `docs/participant-handout.md`.
2. Fill `templates/offering-quick-card.md`, or ask a facilitator to help.
3. If your offering should be built, wrap it with `templates/spec-fragment.md`.
4. If several offerings fit together, use `templates/bundle.md`.
5. For a selected bundle, use `templates/build-attempt-instructions.md`.
6. After a build attempt, use `templates/reviewer-check.md` and `templates/witness-rollup.md`.
7. Before a story, receipt wall item, slide, or other display surface is shown, use `templates/display-review-checklist.md`.

## Seed Examples

- `examples/open-kit-collective-demo/` shows the current end-to-end prototype path.
- `examples/composition-v0/` shows simulated participant offerings becoming candidate bundles.
- `examples/consent-review-desk/` records refusal, review, withdrawal, and display approval.
- `examples/receipt-wall-static/` sketches a public/sample-only witnessing surface.
- `examples/handoff-packet-studio/` shows how to freeze a selected bundle.
- `examples/ai-attempt-review-pattern/` shows how to review an AI-assisted attempt without treating AI output as authority.

## Spec Backlog

- `specs/README.md` is the Creator Jam spec menu.
- The backlog includes witnessing and claims, commitment pooling, flow funding, bioregional mapping, bioregional insights, insurance and risk, Indigenomics AI app flows, sensors, private learning, receipt walls, and spec composition.
- Participants can build a spec, improve a spec, or compose several specs into a candidate collective build.
- `workshop/spec-composition-lab.md` gives a practical experiment protocol for discovering composability, overlap, non-composability, and coherence.
- `workshop/spec-composition-matrix.md` starts the experiment of discovering which specs compose, overlap, or should remain separate.
- `workshop/common-spec-fields.md` sketches shared fields to test across composed specs.
- `workshop/waka-claims-engine-primitive-comparison.md` compares Austin Wade Smith / RiverComputer's Waka project, the RegenAI Claims Engine, and the Creator Jam Coordination Canoe pattern before any interop spec is written.
- `workshop/coordination-canoe-weave-map.md` maps the central coordination field before the next spec or build artifact is selected.
- `workshop/composition-engine-technical-pattern.md` describes the operator-facing composition engine pattern from raw garden input to candidate bundles, authority checks, coherence vectors, constraints, and receipts.
- `workshop/coherence-vs-goodness.md` separates composability, coherence, and desirability/health so technical fit is not mistaken for a good next move.
- `workshop/tomorrow-spec-build-plan.md` gives a short next-day plan for turning the backlog into fixture-backed builds.
- `examples/spec-experiments/` contains the first fixture-backed spec experiments.
- `games/` contains lightweight play formats that teach the same speech-act, refusal, review, and receipt primitives as the kit.
- `templates/speech-act-transition.md` is the category-drift checkpoint for transitions such as citation to claim, observation to attestation, dream to commitment, witness record to attribution, and receipt to public story.
- `templates/display-review-checklist.md` is the review gate before a receipt, witness rollup, story card, gallery item, or public readout moves into display.
- `docs/glossary.md` names `Coordination Canoe` as the provisional local working metaphor and reserves `Waka` for Austin Wade Smith / RiverComputer's project.

## Boundaries

Receipts record what happened. They do not establish legitimacy, authority, certification, or readiness for reuse.

AI may be used only on public material or material explicitly approved for that specific AI use. AI does not judge cultural authority, consent, ceremony fit, or community legitimacy.

If something is private, protected, cultural, protocol-bound, or review-required, record the boundary. Do not disclose the protected material in order to prove the boundary.

## Local Checks

Run:

```bash
python3 scripts/validate-frontmatter.py
python3 scripts/validate-bundle-links.py
python3 scripts/composition_engine.py examples/spec-experiments/commitment-pool-dream-witness-composition --write
```

These checks are lightweight. They check shape and references; they do not certify permission, authority, or correctness.
