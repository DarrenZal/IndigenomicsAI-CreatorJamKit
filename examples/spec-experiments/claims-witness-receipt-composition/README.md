# Claims Witness Receipt Composition

This directory contains a fixture-backed worked composition reference for:

`claims evidence -> witness record -> receipt/story candidate`

All records are fictional public-sample data. They are meant to test whether fields from the claims evidence, witness record, speech-act transition, and receipt/story gallery specs can compose without changing the meaning or permissions of source records.

## Files

- `fixtures/claims-witness-receipt-fixture.json` contains the source records, reviewer objects, boundary checks, speech-act transition records, composed output, display gate, withdrawal paths, and AI-use receipts.
- `reports/composition-report.md` is the human-readable worked composition reference for the fixture.
- `reports/story-card-candidate.md` is an internal display-review candidate only. It is gated with `display_approval: pending` and `do_not_show_externally: true`.

## Participant Safety

- This experiment uses fictional/public-sample data only.
- No participant-private, protected, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound content is included.
- A marker-only source record demonstrates a non-use boundary. It is excluded from the composed output and no underlying content is described, summarized, inferred, routed, indexed, trained on, or displayed.
- Witness records here are software/reviewer receipts only, not ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority.

## Composition Boundaries

- Evidence visibility is separate from claim visibility. Evidence records carry `evidence_visibility`; claim and story records carry their own `visibility_tier` and display gates.
- Reviewer objects include `reviewer_type` enum values using fictional roles only: `facilitator`, `human_reviewer`, `sample_steward`, `technical_reviewer`, and `display_reviewer`.
- The fixture includes two speech-act transition records:
  - `evidence -> claim`
  - `witness_record -> story_candidate`
- The story candidate includes `derived_from_transitions` and cannot be shown externally while `display_approval` is `pending`.
- Public/display-facing candidates must state that they do not establish authority, legitimacy, certification, cultural fit, readiness for reuse, or permission for other uses.

## Not Established

This worked composition reference does not establish:

- authority
- legitimacy
- certification
- cultural fit
- readiness for reuse
- permission for other uses

## Not Run

- No live evidence retrieval.
- No production registry update.
- No participant or community review workflow.
- No public receipt wall export.
- No AI processing of private or protected material.
