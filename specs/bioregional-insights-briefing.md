---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: bioregional_insights
last_updated: 2026-05-17
---

# Bioregional Insights Briefing

## Invitation

Build a steward-reviewed briefing generator that summarizes atlas records, claims, evidence, sensor signals, and commitments without pretending to replace local judgment.

## What Could Be Built

- A briefing template for a watershed, neighborhood, or corridor.
- An insight generator that only uses approved records.
- A citation and witness sidecar for every insight.
- A review screen for "use", "revise", "local-only", or "do not publish".

## Inputs

- `briefing_id`
- `area_of_interest`
- `time_window`
- `source_records`
- `claims`
- `evidence_pointers`
- `sensor_summaries`
- `commitment_records`
- `visibility_tier`
- `reviewer`
- `intended_audience`

## Outputs

- Bioregional insights brief.
- Source and citation table.
- Confidence and limitation notes.
- Review decisions.
- Follow-up questions.

## Acceptance Criteria

- Every insight links to approved source records or says why evidence is missing.
- The brief separates observation, interpretation, recommendation, and unresolved question.
- Private or local-only records can inform a private brief but are excluded from public briefs.
- Reviewer decisions are recorded.
- The brief can be regenerated after a withdrawal or correction.

## Refusal Boundaries

- Do not generate official policy, legal, cultural, or governance conclusions without the appropriate review path.
- Do not expose private source records through summaries.
- Do not smooth over uncertainty to make a brief sound more complete.
- Do not rank communities, Nations, or participants.

## First Build Step

Create a sample briefing for one fictional watershed using three atlas records, two claims, one sensor summary, and one unresolved question.

## Source Notes

Synthesized from living atlas, claims evidence, sensor, and bioregional mapping threads.

## Next steps

If your team picks this spec:

1. Read `examples/sample-submission-pair/sample-team-submission-v0.md` for what a filled-in submission looks like.
2. Open `templates/team-submission-v0.md` — fill in your team's vision, spec, offerings, boundaries, authorization, and witnessed_working using the five questions from `docs/facilitator-quick-card.md`.
3. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to catch the most common failure modes.
4. Walk through the freeze checklist with your facilitator.
5. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>` Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
