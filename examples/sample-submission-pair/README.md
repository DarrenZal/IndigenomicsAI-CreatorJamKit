# Sample submission pair — worked example

A complete, end-to-end worked example pair for facilitators and mentors to show participants:

- **`sample-team-submission-v0.md`** — what a finished `team-submission-v0` looks like (the rich gateway/fallback record). Inline JSON.
- **`sample-agentic-build-packet-v0.json`** — what the runtime build packet looks like after facilitator freeze + exporter. The lean JSON the TELUS build lane consumes.
- **`build-instructions.md`** — the frozen build spec the build attempt works from (referenced by the packet).
- **`acceptance-test.py`** — the smoke test the build attempt runs against (referenced by the packet).
- **`sample-witness-record.md`** — what the Tuesday canoe-landing record looks like for this attempt.

## When to show this

A team asks one of:

- "What does a finished submission look like?"
- "What gets sent to the AI lane?"
- "What does the Tuesday witness record look like?"
- "How modest can a build attempt be?"

Walk them through the four files in the order above. Stop at the boundary-and-authorization fields and explain those carefully — most teams get the schema, but the consent + boundary fields are where the real discipline lives.

## What this example demonstrates

| Aspect | How this example shows it |
|---|---|
| Modest scope | One single-file CLI, ~50 lines of Python, doable in 4 hours |
| Real boundary | A monitoring site within a Nation's reserved area, named only; never enters the build |
| Authorization clear | `ai_input_scope: whole` for cleared offerings; `reuse_scope: ask-first`; display scope explicit |
| Witness-shaped acceptance | Six acceptance criteria a room can recognize, with an executable test |
| Salish-Sea-ecological framing | Eelgrass canopy, kelp-blade length, shoot density — public, no cultural authorization needed |
| Reviewer leak-checks | Two explicit checks that no excluded record appears in tool or output |

## Two worked examples now exist

This sample (`Kelp Watch`) and the M2.6 dogfood (`Tide Tally`, in `IndigenomicsAI` repo at `examples/jam-dogfood-m2-6/`) are different shapes deliberately:

| | Tide Tally (M2.6 dogfood) | Kelp Watch (this sample) |
|---|---|---|
| Shape | Tag counter | Observation rollup |
| Domain | Tagged offerings | Time-stamped, multi-indicator observations |
| Normalization | Strip + collapse + lowercase tags | Strip + collapse + lowercase site, indicator |
| Drop rules | Tags normalizing to empty or to "private" | Bad-value + empty-site + empty-indicator |
| Boundary | One marker-only (elders' recording) | Two: marker-only + not-for-AI |
| Aggregation | Count per tag | Per-site, per-indicator mean + count |

Show whichever fits the team you're working with. A team that wants something small and discrete: Tide Tally. A team thinking about a longitudinal log: Kelp Watch.

## What this example is not

- Not a real team submission — `Kelp Watch` is fictional; all sites and observers are made up
- Not authority, approval, certification, or reuse permission for any pattern shown
- Not a template — teams write their own vision/spec in their own words, not by copying this one
- Not the only valid shape — many builds will look nothing like this; the schemas accommodate a wide range of attempts
