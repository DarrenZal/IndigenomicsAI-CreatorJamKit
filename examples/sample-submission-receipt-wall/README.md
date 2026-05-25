# Story Receipts Wall — sample submission pair

A second worked example showing a different output shape from `sample-submission-pair/` (Kelp Watch). Kelp Watch was a numeric rollup; this one is a text/markdown aggregation with per-record consent gates.

## When to show this to a team

- A team wants to display a wall of contributions / stories / receipts publicly
- A team is thinking about consent at the per-record level (not just at the boundary level)
- A team is interested in markdown output, formatted display, or "what gets shown vs counted"
- A team wants a worked example of how withholding is honored (counted but not displayed)

## Files

- `sample-team-submission-v0.md` — what a finished team submission looks like (inline JSON)
- `sample-agentic-build-packet-v0.json` — frozen runtime packet exported from the submission
- `build-instructions.md` — the frozen build spec the build attempt works from
- `acceptance-test.py` — 7 unittest cases, stdlib only
- `preflight-findings.md` — results of the actual TELUS-lane run (split result: Gemma fixed-after-repair, Qwen no-change)
- `runs/` — committed artifacts from both model runs

## Differences from `sample-submission-pair/` (Kelp Watch)

| Aspect | Kelp Watch | Story Receipts |
|---|---|---|
| Output shape | numeric rollup (means + counts) | text aggregation (markdown wall) |
| Per-record gate | drop bad data (non-numeric, empty key) | consent gate (display_scope) |
| Counting | what got tallied | what got withheld |
| Boundary illustration | site held privately by team | per-record display gates set by contributor |
| Acceptance tests | 6 | 7 |
| Both models clean? | yes (after spec sharpening) | Gemma fixed-after-repair; Qwen no-change |

## What this teaches mentors

1. **Text-format outputs are harder than numeric.** Both models stumbled on markdown blank-line placement; only Gemma recovered on repair. Mentors should warn teams choosing markdown output that whitespace rules need explicit acceptance tests.
2. **Consent is per-record, not just per-team.** Each receipt sets its own `display_scope`. A receipt being in the file ≠ the receipt being shown.
3. **Withholding is counted, transparently.** The wall reports "Receipts withheld from display: <W>" at the bottom — honest without disclosing content.
4. **The exporter strips boundaries structurally.** Two boundaries (`marker-only` non-public scopes; `not-for-AI` contact details) are named only; the runtime packet carries no content from them.

## What this is not

- Not a finished product
- Not approval or reuse permission
- Not a template — teams write their own vision/spec
- Not the canonical "what every team should build" — most teams will build something nothing like this
