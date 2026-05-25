---
doc_id: indigenomics.jam.examples.witness-wall-v0
doc_kind: worked-example
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Witness Wall v0 — worked example

Three sample witness records demonstrating the
[`specs/witness-record-append-v0/`](../../specs/witness-record-append-v0/)
publication flow. Salish-Sea-ecological framings only.

## Records

| # | Team | Finding | Refusal? |
|---|------|---------|---------:|
| 1 | team-kelp-bed-observers | built clean | no |
| 2 | team-salmon-counters | refusal — chose not to publish | **yes** |
| 3 | team-steward-calendar | built, partial — 2/3 acceptance | no |

Record 2 is a **refusal-as-record**: the team considered publishing,
reviewed the consent implications with a mentor, and decided not to.
That decision is itself a complete outcome and earns its place on the
wall alongside the other records (marked with ⟂).

## Try it (60 seconds)

From the kit root:

```bash
# 1. Publish all 3 records to a temporary wall
WALL=/tmp/witness-wall-demo
rm -rf $WALL
for f in examples/witness-wall-v0/sample-record-*.md; do
  python3 scripts/jam/witness_append.py append "$f" --confirm-publish --wall-root $WALL
done

# 2. Audit the wall
python3 scripts/jam/witness_append.py audit --wall-root $WALL

# 3. Render the wall as markdown
python3 scripts/jam/witness_append.py wall --wall-root $WALL

# 4. Try to publish without --confirm-publish (validates but doesn't append)
python3 scripts/jam/witness_append.py append \
  examples/witness-wall-v0/sample-record-1-kelp-clean-build.md \
  --wall-root /tmp/other-wall
```

## What this demo proves

- ✅ Records publish only with `--confirm-publish`
- ✅ Receipt-statement presence is required (defense in depth on top of validator)
- ✅ Overclaim validator (from `tools/witness-record-validator.py`) catches high-severity language and blocks publish
- ✅ **Refusal-as-record** publishes equally — refusal is honored, not summarized away
- ✅ Wall renders deterministically (alphabetical by timestamp), with ⟂ marker on refusal records
- ✅ Audit walks every record and confirms all are validator-clean + receipt-present

## Validator bug found + fixed during demo development

While building this demo, the existing
`tools/witness-record-validator.py` flagged the standard receipt
statement ("does not establish authority, approval, certification,
legitimacy") as overclaim. Root cause: the disclaimer-context check
was line-scoped, but receipt statements wrap across multiple lines —
"does not establish" lands on line N, but "certification" /
"legitimacy" appear on line N+1.

Fix shipped at source: `_is_in_disclaimer_context` now looks at a
3-line window (current line + 2 lines back). Regression test in
`scripts/jam/tests/test_witness_append.py`.

## Boundary

Validated lane = publication of validated witness records to a public
wall with explicit per-record consent gate. NOT certification, NOT
authority, NOT a substitute for community/Nation/steward judgment.
