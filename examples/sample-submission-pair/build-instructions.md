# Build instructions — Kelp Bed Watch (sample)

Build a single-file Python tool, run as:

```
python3 tool.py <observations_json_path>
```

It reads the JSON file at the path given as its first command-line argument. The file is an object shaped:

```json
{
  "observations": [
    { "id": "...", "site": "...", "date": "YYYY-MM-DD", "indicator": "...", "value": <number>, "notes": "optional string" },
    ...
  ]
}
```

Print to stdout, in this order:

1. A header line, exactly:
   `KELP BED WATCH (<N> observations across <S> sites)`
   where `<N>` is the count of observations kept (after dropping bad rows), and `<S>` is the count of distinct sites.
2. For each site, ordered alphabetically by site name, a block consisting of:
   - A line: `== <site> ==`
   - For each distinct indicator at that site, ordered alphabetically: `<indicator>: mean <mean>, n=<count>` — `<mean>` rounded to 2 decimals.
3. Exactly one blank line after each site block, including after the last site block. (Equivalently: every site block is followed by one blank line; the SUMMARY line is then printed.)
4. A final summary line:
   `SUMMARY: <N> observations, <S> sites, <FROM> .. <TO>`
   where `<FROM>` and `<TO>` are the earliest and latest dates in `YYYY-MM-DD` form. If no observation kept has a parseable date, print `no dates` in place of `<FROM> .. <TO>`.

If there are zero kept observations, skip step 2 and step 3 entirely: print the header line, then the SUMMARY line directly (with `0 observations, 0 sites, no dates`). Do not print any blank line in the empty case.

## Normalization rules

Normalize every `site` and `indicator` before grouping:

- Strip whitespace from both ends.
- Collapse internal runs of whitespace to a single space.
- Lowercase.

Display the normalized form (lowercased + collapsed) in the output.

## Drop rules

Drop an observation entirely if any of:

- `value` is not a JSON number (after parsing) — i.e. strings, nulls, booleans dropped.
- `site` normalizes to the empty string.
- `indicator` normalizes to the empty string.

A dropped observation does not contribute to `<N>`, the per-indicator mean, or the date range.

## Date handling

Dates are strings in `YYYY-MM-DD` form. For the SUMMARY range, ignore observations whose `date` is missing or does not match `YYYY-MM-DD`. If no kept observation has a valid date, output `no dates` for the range.

## Error handling

If the input cannot be read, or is not valid JSON, print a single line beginning with `error:` and exit 0.

## Constraints

- Python standard library only.
- No network access.
- No filesystem access beyond reading the path argument.
- No credential or environment-variable reads.
- The tool must be a single file.
