# tools/ — Jam-day mentor helper utilities

Four small Python utilities mentors can run during the jam. Standard library only; no install required.

## `witness-record-validator.py`

Catch overclaim language in a Tuesday witness record before it's read aloud.

```
python3 witness-record-validator.py path/to/witness-record.md
```

Flags phrases that imply certification, authority, legitimacy, or reuse permission — language the kit's discipline says witness records must not carry. Severity-graded (high/medium/low). Also checks for the receipt-statement boilerplate.

When to use: Tuesday morning, before each team reads their witness record aloud at canoe landings. ~30 seconds per record.

## `withdrawal-propagation.py`

When a record is withdrawn, show which surfaces and downstream summaries need to update.

```
python3 withdrawal-propagation.py manifest.json <record-id> [more-ids...]
```

Reads a dependency manifest (records → surfaces → downstream summaries) and reports which surfaces reference the withdrawn record and which summaries depend on those surfaces. Does NOT auto-update anything — humans execute updates.

When to use: any time during the jam when a participant or steward changes their mind about something they recorded. Often the next morning, after they've slept on it.

## `composition-merger.py`

Merge two team submissions into a candidate bundle with conflicts surfaced.

```
python3 composition-merger.py team-a-submission.json team-b-submission.json --out candidate-bundle.json
```

Output bundle has:
- Combined offerings (with team provenance preserved)
- Union of boundaries (composition never relaxes boundaries)
- Intersected authorization (most restrictive wins)
- Explicit `conflicts_surfaced` list
- `bundle_status: candidate` until both teams re-confirm
- Reuse scope forced to `ask-first` regardless of input

When to use: late Monday or Tuesday morning when two teams realize their offerings might compose. The output is a CANDIDATE — both teams must re-freeze in the composed context before any build attempt runs.

## `spec-linter.py`

Flag the 5 most-common failure modes in a draft spec before freeze.

```
python3 spec-linter.py team-submission-v0-draft.json
```

Rules (with evidence from overnight preflights):
1. **optional CLI arg without test coverage** — both Witness Validator and Claims Coherence preflights failed for this reason
2. **markdown output without whitespace assertion** — Story Receipts Wall Qwen run failed for this
3. **acceptance criteria too thin (< 3)**
4. **`ai_input_scope: none` but `telus-lane` build path** — exporter will refuse
5. **spec implies network/database/install access** — lane runs in scrubbed environment
6. (bonus) **boundary missing `disallowed_use` list** — exporter can't enforce
7. (bonus) **not yet frozen** — info-level reminder

When to use: when a team thinks they're ready to freeze. Run this first; the team fixes anything flagged; then they freeze.

## Boundary

These tools are mentor aids, not authority. They check for structural issues; they do not check for cultural appropriateness, community fit, ceremony alignment, or steward judgment. Those remain human work.

They are stdlib-only; reading or writing files only as named on the command line; no network access.

## Self-test

Each tool runs against the kit's own sample submissions:

```bash
python3 spec-linter.py ../examples/sample-submission-pair/sample-team-submission-v0.md
# (uses the JSON embedded in the markdown — actually pull the JSON or pass a .json file)

python3 witness-record-validator.py ../examples/sample-submission-pair/sample-witness-record.md
```
