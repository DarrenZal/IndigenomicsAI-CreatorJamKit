# Build instructions — Compute Covenant (preflight)

Build `tool.py`. Run:

```
python3 tool.py <covenant_json_path>
```

This tool composes downstream of `energy-receipt`. It reads multiple team
energy summaries (the per-team totals that an Energy Receipt produces) plus
opt-out markers, and produces a jam-level rollup.

Reads:

```json
{
  "jam": "...",
  "date": "YYYY-MM-DD",
  "site": "TELUS-Rimouski hydro",
  "teams": [
    {
      "team": "...",
      "kept_events": <int>,
      "rejected_events": <int>,
      "total_kwh": <float>,
      "input_tokens": <int>,
      "output_tokens": <int>,
      "models": ["gemma-4-31b", "qwen-3.6-35b", "..."],
      "intention_themes": ["kelp", "herring", "..."],
      "disclosure": "public" | "withheld"
    }
  ]
}
```

`disclosure` controls whether a team's numbers are shown by name. `withheld`
teams still contribute to ECOSYSTEM ENERGY totals (the jam consumed the
electricity); they just aren't named in the per-team list.

## Per-team filtering

Reject (skip, count as `rejected_teams`) any team where:

- `team` is empty
- `disclosure` is not `public` or `withheld`
- `total_kwh`, `input_tokens`, or `output_tokens` is missing, non-numeric, or
  negative

Kept teams feed ECOSYSTEM ENERGY. Rejected teams do not.

## Output (markdown to stdout)

```
COMPUTE COVENANT — <jam> (<date>)
site: <site>

ECOSYSTEM ENERGY
  teams: <K_total> kept (<K_public> public, <K_withheld> withheld), <R> rejected of <N> total
  jam_kwh: <sum_kwh, 4dp>
  tokens: <sum_input> in / <sum_output> out
  models: <comma-separated sorted distinct kept-team models, or none>

PER-TEAM CONTRIBUTIONS
- team: <team>
  kWh: <total_kwh>
  events: <kept_events> kept, <rejected_events> rejected
  tokens: <input_tokens> in / <output_tokens> out
  intention themes: <comma-separated themes, or none>
  models: <comma-separated sorted distinct team models, or none>

- team: ...
  ...

WITHHELD: <W> team(s) opted out of public energy disclosure. Their compute is
included in ECOSYSTEM ENERGY; their names and per-team numbers are not.

COVENANT
This jam consumed <sum_kwh, 4dp> kWh on <site>. Equivalent to roughly
<sum_kwh / 0.4, 2dp> Vancouver homes for an hour (0.4 kWh/home/hour reference).
Witnessed.

BOUNDARY: This is a record of compute that happened, on a grid that ran on
~99% renewable hydro on the day named. It does not offset, certify carbon
neutrality, claim ecological repair, or grant a reuse license.
```

Formatting rules:

- Blank line between major sections.
- The `PER-TEAM CONTRIBUTIONS` header is followed by a blank line, then the
  first `- team:` block. Public teams only — `withheld` teams do not appear in
  the per-team list.
- If there are no kept public teams, write `  (no public-disclosure teams)`
  under the header instead of any `- team:` blocks.
- The `WITHHELD` line always appears — `<W>` is the count of kept teams with
  `disclosure == "withheld"`. If `W == 0`, the line still appears: `WITHHELD:
  0 team(s) opted out of public energy disclosure.` (the rest of the sentence
  omitted in that case).
- `jam_kwh` and the covenant kWh are formatted to 4 decimal places.
- The Vancouver-homes equivalent is formatted to 2 decimal places and uses
  the literal divisor `0.4` (0.4 kWh/home/hour is the reference).
- The COVENANT block ends with the literal word `Witnessed.` on its own.

## Errors

On invalid JSON or unreadable file: single `error:` line, exit 0.

## Constraints

Stdlib only; no network; no credentials; no hardcoded outputs.
