---
doc_id: indigenomics.jam.specs.witness-record-append-v0.spec
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
area: publication-surface
last_updated: 2026-05-25
---

# Witness Record Append — Spec v0

## Invitation

Provide a small, dependency-free publication surface for the witness
records that close Tuesday's canoe landings. Each team that wants to
publish runs the CLI with their record + `--confirm-publish`. Records
without the standard receipt statement, or with high-severity overclaim
language, are rejected before they land on the wall. Refusal records
publish equally with other outcomes.

## Schema reality check

- `tools/witness-record-validator.py` exists and is the canonical
  overclaim detector. This spec wraps it.
- Witness records use the markdown shape demonstrated in
  `specs/preflights/*/runs/*/canoe-landing/witness-record.md` (already
  produced by the M2.6 build path). This spec consumes that shape; no
  new schema fields.
- `templates/witness-rollup.md` is the participant-facing template; the
  preflight-generated records are the auto-shape; this CLI accepts both.

## CLI subcommands

| Subcommand | Purpose |
|---|---|
| `validate <record.md>` | Run the validator + receipt-statement check; do nothing else |
| `append <record.md> [--confirm-publish] [--wall-root <path>]` | Publish if both checks pass AND `--confirm-publish`; otherwise return reasoned refusal |
| `wall [--wall-root <path>] [--out <wall.md>]` | Render all records on the wall as a single markdown document |
| `audit [--wall-root <path>]` | Re-validate every record on the wall; return pass/fail per file |

## Wall layout

```
<kit-root>/wall/
  witness-records/
    <timestamp>-<team-id>-<short-hash>.md   # one file per published record
```

Filename is deterministic: `YYYYMMDDTHHMMSS-<team-id>-<6-hex>.md`.
Wall renders by sorting filenames alphabetically (which sorts by
timestamp).

## Publication checklist (enforced)

A record publishes ONLY when ALL of these hold:

1. Receipt statement present — pattern matches "this record states what happened" AND "does not establish (authority|approval|certification)".
2. Validator returns clean (overclaim findings of severity ≥ `high` rejected; `medium` / `low` surface as warnings but don't block).
3. `--confirm-publish` flag explicitly set.

If any check fails, the CLI prints a structured JSON refusal and exits
non-zero. The record is NOT modified or moved.

## Refusal-as-record

A team can publish a record that says "we chose not to surface this
offering publicly." That record:
- Validates like any other (receipt statement, no overclaim)
- Publishes with the same flow (`--confirm-publish`)
- Renders on the wall with a ⟂ marker instead of 🛶
- Is honored equally — display does not summarize it away

Detection heuristic (in `parse_record`): the body contains one of:
- "we chose not to"
- "we declined"
- "we refused"
- "refusal-as-record"
- the ⟂ glyph

This is a heuristic; the team can also mark `refusal_as_record: true`
in metadata if they want explicit attribution.

## Wall metadata footer

Each published record gets a metadata footer appended:

```
**Wall metadata** (added by witness_append.py)
- record_id: `<timestamp>-<team-id>-<short-hash>`
- appended_at: <iso8601>
- source: <path>
- refusal_as_record: <bool>
```

The original record text is preserved verbatim above the footer.

## Acceptance criteria

- A clean record (receipt present + validator clean) publishes with `--confirm-publish`.
- A clean record WITHOUT `--confirm-publish` returns a structured refusal that says "re-run with --confirm-publish".
- A record without the receipt statement is rejected with a clear reason.
- A record with high-severity overclaim language is rejected before publication.
- A refusal-as-record publishes equally, gets the ⟂ marker on the wall.
- `audit` walks every record and confirms all are validator-clean + receipt-present.
- `wall` renders deterministically: same input wall → same output text.

## What is NOT in v0

- HTML rendering (markdown only; HTML is post-jam polish).
- Discovery / search across the wall — render is one-shot.
- Federation across multiple walls.
- Editable / retractable records — corrections only via NEW records that reference prior record-id.
- Author-token signing — anyone who can write to the wall directory can publish; future v0.1 may wire gateway team-tokens for authentication.

## Validator patch shipped during this work

Found at source: `tools/witness-record-validator.py`'s `_is_in_disclaimer_context` was line-scoped, missing multi-line receipt statements. Fix: 3-line lookback window.

## Refusal boundaries

This CLI MUST NOT:
- Publish without `--confirm-publish`
- Publish records missing the receipt statement
- Publish records with high-severity overclaim findings
- Auto-correct or edit a record's text
- Silently demote / suppress refusal-as-record entries

## Composition prompts

- Tuesday morning composition sprint: teams that pick this spec can
  build (a) HTML rendering of the wall, (b) wall-level search /
  filtering, (c) RSS / Atom feed, (d) gateway-token authentication.
- The wall is the natural downstream of build attempts; spec-drafting-
  loop's stage 6 (witness drafting via Prompt 3) produces draft
  records that this CLI publishes.

## Boundary

Validated lane = publication of validated witness records to a public
wall with explicit per-record consent gate. NOT certification, NOT
authority, NOT a substitute for community / Nation / steward judgment.

🛶
