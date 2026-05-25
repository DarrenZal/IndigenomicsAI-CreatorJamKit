# Build instructions — Story Receipts Wall (sample)

Build a single-file Python tool, run as:

```
python3 tool.py <receipts_json_path>
```

It reads the JSON file at the path given as its first command-line argument. The file is an object shaped:

```json
{
  "receipts": [
    {
      "id": "...",
      "contributor": "...",
      "date": "YYYY-MM-DD",
      "text": "...",
      "display_scope": "public" | "team-only" | "spoken-only" | "none",
      "tags": ["..."]   // optional list of strings
    },
    ...
  ]
}
```

Print to stdout a markdown wall in this order:

## (1) Header line

Exactly:

```
# Story Receipts Wall (<S> shown / <N> total)
```

where `<S>` is the count of receipts with `display_scope == "public"` and a non-empty text (after stripping), and `<N>` is the total receipt count (every entry in the array, regardless of scope or text).

## (2) One blank line after the header.

## (3) Each public receipt block

For each receipt with `display_scope == "public"` and non-empty stripped text, sorted by `date` ascending then by `id` ascending for ties:

```
## <contributor> — <date>

> <line 1 of text>
> <line 2 of text>
> ...

tags: <tag1>, <tag2>, ...
```

Then exactly one blank line.

Rules:
- The `##` line uses an em-dash with a space on each side: `## <contributor> — <date>` (the em-dash character is U+2014).
- The text is quoted with `> ` (greater-than + space) prefix on each line. Preserve the receipt's internal line breaks; quote every line individually.
- If `tags` is present and non-empty, emit a `tags: <comma-separated>` line. Otherwise omit the tags line entirely.
- After the tags line (or after the quoted text if no tags), emit exactly one blank line before the next receipt block (or the footer).

## (4) Footer

After all public receipt blocks:

```
---

Receipts withheld from display: <W>
```

where `<W>` = `<N>` − `<S>`. (Total minus shown.) The `---` is on its own line, then one blank line, then the withheld-count line.

## Drop rules

Treat as **withheld** (not shown, but counted toward `<W>`):

- `display_scope` is not exactly the string `"public"` (so: `"team-only"`, `"spoken-only"`, `"none"`, any other value, missing key — all withheld).
- `text` is empty after stripping whitespace from both ends.

## Error handling

If the input file cannot be read, or is not valid JSON, print a single line beginning with `error:` and exit 0.

## Constraints

- Python standard library only.
- No network access.
- No filesystem access beyond reading the path argument.
- No credential or environment-variable reads.
- The tool must be a single file.
- Output is markdown (UTF-8); do not strip or modify the receipt text other than quoting each of its lines with `> `.
