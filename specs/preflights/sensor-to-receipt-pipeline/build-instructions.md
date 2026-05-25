# Build instructions — Sensor-to-Receipt Pipeline (preflight)

Build `tool.py`. Run:

```
python3 tool.py <observations_json_path>
```

Reads:

```json
{ "observations": [ {
  "observation_id": "...",
  "observation_type": "sensor_reading" | "field_note" | "photo" | "audio" | "manual_count" | "repair_event",
  "source": "...",
  "location": "...",
  "location_precision": "exact" | "site" | "region",
  "time": "YYYY-MM-DD",
  "measurement": <number> | null,
  "unit": "..." | null,
  "calibration_state": "calibrated" | "uncalibrated" | "unknown",
  "sensitive_location_flag": <boolean>,
  "review_state": "reviewed" | "pending" | "contested" | "not-applicable"
}, ... ] }
```

## Public-safe transformations (per observation kept)

1. **Sensitive location redaction**: if `sensitive_location_flag == true` OR (`location_precision == "exact"` AND `sensitive_location_flag == true`), replace `location` with the literal string `region-level only`.
2. **Calibration confidence**: map `calibration_state` → confidence: `calibrated → high`, `uncalibrated → low`, `unknown → unknown`.
3. **Qualitative observation**: if `measurement` is `null`, output `qualitative observation` in the data field instead of a number+unit.
4. **Reject** (skip, count as rejected) any observation where `observation_id` is empty, `observation_type` is missing, or `time` does not match `YYYY-MM-DD`.

## Output

```
SENSOR-TO-RECEIPT EVIDENCE PACKETS (<N> kept / <M> total)

- id: <observation_id>
  type: <observation_type>
  source: <source>
  location: <location-or-redacted>
  time: <time>
  data: <measurement> <unit>   ← or 'qualitative observation' if measurement is null
  calibration_confidence: <high|low|unknown>
  review_state: <state>

- id: ...
  ...

SUMMARY: <K> kept, <R> rejected, <S> sensitive-location-redacted of <M> total
```

- One blank line between header and first observation block.
- One blank line between observation blocks (including after the last block, before SUMMARY).
- Lead each field line with two spaces (under the `- id:` indent).

Counts:
- `<K>` = kept (passed all filters)
- `<R>` = rejected (skipped per drop rules)
- `<S>` = how many kept observations had their location redacted
- `<M>` = total observations in the input

## Errors

Single `error:` line on invalid input, exit 0.

## Constraints

Stdlib only; no network; no credentials.
