# Graph Chat Witness Sidecar Spec Experiment

Status: public-sample fixture packet

This experiment backs `specs/indigenomics-ai-graph-chat-witness-sidecar.md` with one static, participant-safe sidecar fixture and one output report.

No real participant content, private source text, protected cultural material, Nation-specific knowledge, or confidential app data is included. All people, notes, identifiers, and graph objects are fictional or public-sample placeholders.

## Files

- `graph-chat-sidecar-fixture.json` - one graph node, one chat turn, three citation links, two reviewed claims, evidence pointers, witness records, acceptance checks, refusal boundaries, and repair tasks.
- `output-report.md` - rendered reviewer-facing summary of the fixture and its acceptance/refusal status.

## Role Split

- Builder: loads the JSON fixture and renders the sidecar UI or report.
- Reviewer: checks claim status, citation status, local-only flags, and refusal boundaries.
- Witness: records whether the rendered output stayed public-safe and whether any repair tasks remain.

## Acceptance Checks

- Users can inspect which sources support an answer.
- Claims are separate from citations and can have their own review status.
- Stale, missing, contested, or local-only sources are visible.
- AI-assisted answers include a receipt of source material and reviewer status.
- Protected source content does not leak through citations or summaries.

## Refusal Boundaries

- Do not present chat answers as authoritative because they have citations.
- Do not expose private source content in snippets.
- Do not auto-upgrade a citation into a verified claim.
- Do not hide contested, missing, stale, or local-only evidence.
- Do not use this fixture to imply consent, cultural authority, certification, or production readiness.
