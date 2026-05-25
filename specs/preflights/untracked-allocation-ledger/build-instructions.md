# Build instructions — Untracked Allocation Ledger (preflight)

Build `tool.py`. Run:

```
python3 tool.py <ledger_json_path>
```

Reads:

```json
{ "allocations": [ {
  "allocation_id": "...",
  "allocation_type": "money" | "time" | "material" | "introduction" | "care" | "knowledge" | "infrastructure",
  "public_summary": "...",
  "recipient_visibility": "public" | "private",
  "funder_visibility": "public" | "private",
  "amount_visibility": "public" | "private",
  "recipient": "...",
  "funder": "...",
  "amount": <number> | null,
  "unit": "..." | null,
  "not_tracked_reason": "..." | null,
  "withdrawn": <boolean>
}, ... ] }
```

## Output

```
UNTRACKED ALLOCATION LEDGER (<P> public / <T> not-tracked / <W> withdrawn of <N> total)

- <allocation_id> [<allocation_type>]:
    summary: <public_summary>
    recipient: <recipient>          ← only if recipient_visibility == "public"
    funder: <funder>                ← only if funder_visibility == "public"
    amount: <amount> <unit>         ← only if amount_visibility == "public" AND amount != null

- <allocation_id> [<allocation_type>]:
    summary: <public_summary>
    not-tracked-by-design: <not_tracked_reason>    ← if not_tracked_reason is non-null;
                                                     suppresses all of recipient/funder/amount

...

AGGREGATE BY TYPE:
  <type>: <count> entries
  ...
```

## Rules

- **Skip withdrawn entries** from the listing (but count them in the `<W>` header).
- **Not-tracked-by-design overrides visibility flags**: if `not_tracked_reason` is non-null, emit only `summary:` and `not-tracked-by-design:`, never amount/recipient/funder.
- **Aggregate section counts but never sums**: count of non-withdrawn, non-not-tracked entries per type, alphabetically. Do not sum amounts. The whole point of this ledger is to acknowledge support without creating surveillance pressure.
- One blank line between header and first entry.
- One blank line after each entry block (including the last before AGGREGATE BY TYPE).
- Aggregate type lines have 2-space indent.

## Header counts

- `<P>` = entries with `withdrawn == false` AND `not_tracked_reason == null` (rendered with possibly-visible details)
- `<T>` = entries with `withdrawn == false` AND `not_tracked_reason != null`
- `<W>` = entries with `withdrawn == true`
- `<N>` = total entries

## Errors

Single `error:` line on invalid input, exit 0.

## Constraints

Stdlib only; no network; no credentials.
