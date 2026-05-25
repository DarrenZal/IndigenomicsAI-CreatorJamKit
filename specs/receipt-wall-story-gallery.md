---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: receipt_surfaces
last_updated: 2026-05-17
---

# Receipt Wall Story Gallery

## Invitation

Build a public/sample-safe gallery that shows what happened in the jam: selected bundles, build attempts, reviewer checks, witness rollups, and participant-approved stories.

## What Could Be Built

- A static receipt wall.
- A story card template.
- A privacy checker for public display.
- A filter for bundle, spec area, reviewer state, and witness type.

## Inputs

- `receipt_id`
- `bundle_id`
- `build_attempt_id`
- `story_summary`
- `participants_displayed`
- `display_approval`
- `witness_rollup`
- `reviewer_check`
- `media_pointers`
- `visibility_tier`

## Outputs

- Receipt wall gallery.
- Story cards.
- Display approval diagnostics.
- Public export manifest.

## Acceptance Criteria

- A receipt can be displayed only when display approval is explicit.
- The gallery can include anonymous or role-only acknowledgements.
- Reviewer checks and witness rollups are linked.
- Private details can be omitted without invalidating the receipt.
- The wall clearly distinguishes sample/demo receipts from real participant receipts.

## Refusal Boundaries

- Do not publish participant names, images, work, or stories without approval.
- Do not imply certification, prize status, or legitimacy.
- Do not use private review notes as public story copy.
- Do not make non-display approval look like a failure.

## First Build Step

Create three story card fixtures: one public, one anonymous, and one not displayed.

## Source Notes

Synthesized from Creator Jam receipt wall examples, witness rollup templates, and consent review desk patterns.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
