# Build instructions — Commitment Pool Routing Diagnostic (sample)

Build a single-file Python tool, run as:

```
python3 tool.py <pool_json_path>
```

It reads the JSON file at the path given as its first command-line argument. The file is an object shaped:

```json
{
  "pool_id": "...",
  "offers": [
    { "id": "...", "contributor": "...", "kind": "...", "units": <number>, "consent_to_route": <boolean> }, ...
  ],
  "needs": [
    { "id": "...", "requester": "...", "kind": "...", "units": <number> }, ...
  ]
}
```

Print to stdout in this order:

## (1) Header

Exactly:

```
POOL ROUTING DIAGNOSTIC — <pool_id>
```

(`—` is U+2014, the em-dash, with spaces on either side.)

## (2) One blank line after the header.

## (3) Per-kind block

For each distinct **normalized kind** that appears in offers or needs, in alphabetical order, emit a block:

```
kind: <kind>
offered: <O> units (<C> contributors consenting)
needed: <D> units (<R> requesters)
status: <status>
```

Then **one blank line** after each block (including after the last block — before the BLOCKERS section).

Where:

- `<O>` = sum of `units` across offers of that kind where `consent_to_route` is `true`.
- `<C>` = count of distinct contributors with at least one consenting offer of that kind.
- `<D>` = sum of `units` across needs of that kind.
- `<R>` = count of distinct requesters with at least one need of that kind.

`<status>` is:
- `fits` if `O >= D` and `D > 0`
- `short by <D-O> units` if `O < D` and `D > 0`
- `no demand` if `D == 0` and `O > 0`
- `no supply` if `O == 0` and `D > 0`
- `idle` if `O == 0` and `D == 0`

## (4) Blockers footer

After the last per-kind block:

```
BLOCKERS:
- <contributor> withheld consent on <kind> (<units> units)
- ...
```

Sort the blockers list by `<contributor>` ascending, then by `<kind>` ascending for ties. Use the normalized kind. If there are no withheld offers, emit exactly:

```
BLOCKERS: none
```

## Normalization

Normalize every `kind` string before grouping:
- Strip whitespace from both ends.
- Collapse internal runs of whitespace to a single space.
- Lowercase.

Use the normalized form for display.

## Drop rules

Drop an offer entirely if `units` is not a number or `kind` normalizes to empty. A dropped offer does not contribute to `<O>`, `<C>`, or BLOCKERS.

Drop a need entirely if `units` is not a number or `kind` normalizes to empty. A dropped need does not contribute to `<D>` or `<R>`.

A withheld offer (`consent_to_route` is exactly `false`) is **not** dropped — it appears in BLOCKERS but does not count toward `<O>` or `<C>`.

## Error handling

If the input cannot be read or is not valid JSON, print a single line beginning with `error:` and exit 0.

## Constraints

- Python standard library only.
- No network access.
- No filesystem access beyond reading the path argument.
- No credential or environment-variable reads.
- The tool must be a single file.
- The tool **does not route** anything — it reports whether routing would fit. No side effects beyond stdout.
