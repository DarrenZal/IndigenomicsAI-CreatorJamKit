# Commitment Pool Routing Diagnostic — sample submission pair

Third worked example. Shape: **routing diagnostic** — input → categorical/numeric status per kind. Different from Kelp Watch's rollup and Story Receipts' text-format wall.

## When to show this

- A team thinking about **whether their pool fits** (offers vs needs)
- A team wanting to model **consent as a routing gate** (a withheld offer is a blocker, not a routing failure)
- A team interested in **multi-kind aggregation** with per-kind status
- A team that wants a "yes/no/short-by-N" answer, not a richer text output

## Preflight results

| Model | Finding | Tests |
|---|---|---|
| `gemma-4-31b` | **fixed** | 7/7 (after one repair) |
| `qwen-3.6-35b` | **improved** | 6/7 (after one repair) |

Consistent pattern across both Story Receipts and Pool Route: spec-heavy formats need a repair cycle. Gemma converges; Qwen partial-converges. Mentor takeaway: tell teams using TELUS lane to expect one repair attempt as the baseline, not a single-shot build.

## What this teaches mentors

1. **A withheld offer is a *blocker*, not a *capability failure*.** The diagnostic distinguishes "we don't have enough labor units" (capability) from "we have enough but Z said no" (consent). Both are valid pool states; they require different team responses.
2. **The tool does not route.** It diagnoses whether routing would fit. No side effects. Mentors should reinforce: the diagnostic informs the team's next conversation; it doesn't make decisions for them.
3. **Routing-shape specs are different from rollup-shape.** Status enums + per-kind blocks add structural complexity for the model. Worth noting if a team chooses this shape.
4. **Normalization shows up in many places.** Same `kind` strings get grouped via strip + collapse + lowercase, same as Kelp Watch's site/indicator pattern. This is a kit-wide convention.

## Files

- `sample-agentic-build-packet-v0.json`
- `build-instructions.md`
- `acceptance-test.py` (7 tests)
- `runs/` (Gemma + Qwen artifacts)

(No separate `sample-team-submission-v0.md` for this one — the packet's export_provenance + team_spec capture enough; mentors who want the full submission shape can show `sample-submission-pair/sample-team-submission-v0.md` or `sample-submission-receipt-wall/sample-team-submission-v0.md`.)
