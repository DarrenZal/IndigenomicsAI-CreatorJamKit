---
doc_id: indigenomics.jam.specs.witness-record-append-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Witness Record Append v0

The third meta-spec for the jam — the public witness-wall surface
that publishes validated witness records after Tuesday's canoe
landings.

## What it is

- CLI: `scripts/jam/witness_append.py` with subcommands `append`, `wall`, `audit`, `validate`
- Wraps existing [`tools/witness-record-validator.py`](../../tools/witness-record-validator.py) for overclaim detection
- Per-record `--confirm-publish` gate (no batch publishing)
- Wall directory: `wall/witness-records/<timestamp>-<team-id>-<short>.md`
- Renders the wall as a single markdown document (deterministic order)
- Honors **refusal-as-record**: a team's decision not to publish lands on the wall too

## What it is not

- Not certification, authority, or grant of permission
- Not a retroactive-edit surface — corrections happen via NEW records that reference prior record-id
- Not a discovery service — the wall is the publication surface; finding records elsewhere uses other tools

## Try it (60 seconds)

```bash
# Validate without publishing
python3 scripts/jam/witness_append.py validate examples/witness-wall-v0/sample-record-1-kelp-clean-build.md

# Publish (requires explicit flag)
python3 scripts/jam/witness_append.py append \
  examples/witness-wall-v0/sample-record-1-kelp-clean-build.md \
  --confirm-publish --wall-root /tmp/wall

# Render the wall
python3 scripts/jam/witness_append.py wall --wall-root /tmp/wall

# Audit every record on the wall
python3 scripts/jam/witness_append.py audit --wall-root /tmp/wall
```

See [`examples/witness-wall-v0/README.md`](../../examples/witness-wall-v0/README.md)
for the full 3-record demo.

## Composition

- [`tools/witness-record-validator.py`](../../tools/witness-record-validator.py) — overclaim detector; this spec wraps it
- [`templates/witness-rollup.md`](../../templates/witness-rollup.md) — witness rollup template used by participants
- [`templates/display-review-checklist.md`](../../templates/display-review-checklist.md) — display approval pattern this spec composes with
- [`specs/witness-record-interop-profile.md`](../witness-record-interop-profile.md) — schema profile the wall is consistent with
- [`specs/agentic-spec-drafting-loop-v0/`](../agentic-spec-drafting-loop-v0/) — produces witness record drafts (downstream of build attempt) that this CLI publishes
- [`specs/agent-coordination-bus-v0/`](../agent-coordination-bus-v0/) — emits `witness_observe` messages that feed into witness records (upstream)

## Tests

```bash
python3 -m unittest scripts.jam.tests.test_witness_append -v
```

Expected: 11 tests OK.

## Files

- `spec-v0.md` — formal spec
- `../../scripts/jam/witness_append.py` — main CLI
- `../../scripts/jam/tests/test_witness_append.py` — 11 unittest cases
- `../../examples/witness-wall-v0/` — 3-record demo (1 clean, 1 refusal-as-record, 1 partial-build)

## Validator patch shipped

While building this spec's demo, the existing `tools/witness-record-validator.py`
was found to falsely-flag the standard receipt statement as overclaim
(line-scoped disclaimer-context check missed multi-line wraps). Fix
shipped at source: 3-line window in `_is_in_disclaimer_context`.

## Boundary

Validated lane = publication of validated witness records to a public
wall with explicit per-record consent gate. The wall states what
happened. It does not certify, approve, authorize, or grant authority.
Refusals are honored equally with other outcomes.
