# Claims Evidence Coherence Spec Experiment

This experiment instantiates `specs/claims-evidence-coherence-report.md` with public-sample material only.

## Files

- `fixtures/claims-evidence-fixture.json` contains five fictional claim records, six evidence pointers, freshness windows, and expected diagnostics.
- `reports/claims-evidence-coherence-report.md` is the generated sample report for the fixture.

## Participant Safety

- All names, places, organizations, claims, reviewers, and evidence references are fictional public-sample content.
- The fixture does not contain participant-private, protected, cultural, ceremonial, linguistic, Nation-specific, credential-bearing, or authority-bound material.
- One record demonstrates a `do_not_compute` boundary using a marker only. The protected content is not described, summarized, or inferred.
- Raw private evidence is not included and is not required to reproduce the report.

## Acceptance Checks

| Check | Fixture Coverage |
|---|---|
| Public claims require evidence and reviewer context. | Claims `claim:CER-001` through `claim:CER-004` include reviewer context; missing or weak support is called out in diagnostics. |
| Stale evidence is surfaced by claim-type freshness windows. | `claim:CER-003` uses stale impact evidence against the 365-day window. |
| Conflicting claims remain visible and are not merged. | `claim:CER-004` is kept visible as contested and linked to the accessibility walkthrough evidence. |
| `do_not_compute` records are excluded from summarization, routing, and public display. | `claim:CER-005` is marker-only and listed as excluded. |
| The report states the intended use it supports or blocks. | The report names a public workshop demo briefing as the intended use. |

## Refusal Boundaries

- Do not adjudicate ultimate truth.
- Do not produce a legitimacy score.
- Do not launder weak evidence into strong public language.
- Do not train on, summarize, or reconstruct raw private evidence.
- Do not treat a reviewer note as cultural, legal, financial, or community authority.
