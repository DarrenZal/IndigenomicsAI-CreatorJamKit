# Build instructions — Energy Receipt (preflight)

Build `tool.py`. Run:

```
python3 tool.py <events_json_path>
```

Reads:

```json
{
  "team": "...",
  "events": [
    {
      "event_id": "...",
      "intention": "...",
      "model": "gemma-4-31b" | "qwen-3.6-35b" | "gpt-oss-120b" | "...",
      "input_tokens": <int>,
      "output_tokens": <int>,
      "duration_seconds": <float>,
      "estimated_kwh": <float>,
      "outcome_summary": "..."
    }
  ]
}
```

`estimated_kwh` is the value produced by the TELUS metrics API (out of scope
for this tool — this tool only summarizes what it's given). TELUS Rimouski runs
on the Quebec hydro grid (~99% renewable, ~1.2 g CO2e/kWh). The receipt does
not compute carbon equivalents.

## Per-event filtering

Reject (skip, count as `rejected`) any event where:

- `event_id` is empty
- `intention` is empty
- `model` is empty
- `input_tokens`, `output_tokens`, `duration_seconds`, or `estimated_kwh` is
  missing or not a number
- `estimated_kwh` is negative

Kept events feed every total. Rejected events count toward `total` only.

## Output (markdown to stdout)

```
ENERGY RECEIPT — <team>

- event_id: <event_id>
  intention: <intention>
  model: <model>
  kWh: <estimated_kwh>
  tokens: <input_tokens> in / <output_tokens> out
  duration_s: <duration_seconds>
  outcome: <outcome_summary>

- event_id: ...
  ...

TOTALS
  events: <K> kept, <R> rejected of <N> total
  kWh: <sum_kwh>
  tokens: <sum_input> in / <sum_output> out
  models: <comma-separated sorted distinct model ids, kept events only>

REFLECTION
  Did the work justify its footprint?
  What would you do differently?
  What reciprocity is owed?

BOUNDARY: This is a receipt of what was computed. It does not offset, certify
carbon neutrality, or grant a reuse license.
```

Formatting rules:

- One blank line between the header and the first event block.
- One blank line between event blocks.
- One blank line between the last event block and `TOTALS`.
- One blank line between `TOTALS` and `REFLECTION`.
- One blank line between `REFLECTION` and `BOUNDARY`.
- `kWh:`, `tokens:`, `duration_s:`, etc. lines lead with two spaces (under the
  `- event_id:` indent).
- `sum_kwh` is formatted to 4 decimal places (e.g. `0.1234`).
- If there are no kept events, still print `TOTALS`, `REFLECTION`, and
  `BOUNDARY`; the model list line reads `models: none`.

## Errors

On invalid JSON or unreadable file: single `error:` line, exit 0.

## Constraints

Stdlib only; no network; no credentials; no hardcoded outputs.
