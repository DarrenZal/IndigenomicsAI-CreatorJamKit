# Multi-Team Composition — Worked Example

What it looks like when two teams' offerings are merged into a candidate bundle.

## The setup

- **Team Eelgrass Observers** wants to build a per-site rollup of eelgrass canopy observations. `ai_input_scope: whole`, `display_scope: whole`, `reuse_scope: ask-first`.
- **Team Kelp Monitors** wants to build a per-site mean of kelp-blade lengths. They have one offering that's a **restricted-release survey** held under Nation-side review — named only as a `protected` boundary. `ai_input_scope: partial`, `display_scope: partial`, `reuse_scope: team-only`.

These two teams realize their work overlaps — both are producing per-site ecological rollups from public-shoreline observations. They want to compose.

## The merge

Run:

```bash
python3 tools/composition-merger.py \
  team-a-submission.json \
  team-b-submission.json \
  --out candidate-bundle.json
```

## What the merger produced

1. **Combined offerings (3 total)** — both teams' offerings, with team-provenance preserved per offering:
   - Boundary Bay observations (from team-eelgrass-observers)
   - Lighthouse Park blade-length log (from team-kelp-monitors, included)
   - Salish Sea kelp survey 2026 dataset (from team-kelp-monitors, NOT included — held by team as boundary)

2. **Combined boundaries (2 total)** — namespaced by team, never collapsed:
   - `team-eelgrass-observers::b1` (not-for-AI, observer contact details)
   - `team-kelp-monitors::b1` (protected, restricted-release survey)

   Both teams happened to use ID `b1` in their own submissions; the merger namespaces them so neither is lost.

3. **Intersected authorization** — most restrictive wins:
   - `ai_input_scope: partial` (Kelp Monitors' restriction wins over Eelgrass Observers' `whole`)
   - `display_scope: partial` (same — Kelp Monitors wins)
   - `reuse_scope: ask-first` (composition forces re-ask regardless of inputs)
   - Note: "composed: both teams must re-confirm before any build attempt or display"

4. **Conflicts surfaced (2)**:
   - `ai_input_scope_mismatch`: team A=whole, team B=partial → resolved to partial
   - `display_scope_mismatch`: team A=whole, team B=partial → resolved to partial

   The merger **does not silently relax** any restriction. Where teams disagreed, the most restrictive answer wins.

5. **Bundle status: `candidate`** — both teams must re-confirm in the composed context before any build attempt runs against the bundle.

## What this teaches mentors

1. **Composition never relaxes boundaries.** If Team A allowed `whole` AI scope and Team B allowed `partial`, the composed bundle is `partial`. The team that gave more permission does not get to override the team that gave less.

2. **IDs are team-namespaced on merge.** Two teams can have a boundary `b1` and both are preserved. No silent collapse.

3. **`reuse_scope` is always forced to `ask-first` on composition.** Even if both source submissions said `public-ok`, the composition forces re-ask. Composition is a new context.

4. **The bundle is `candidate`, not `frozen`.** Both teams must re-confirm before any build attempt. Composition triggers re-freeze.

5. **Conflicts are surfaced explicitly.** The bundle's `conflicts_surfaced` list shows every place where teams disagreed and how the resolution went. This is for transparency, not just record-keeping.

## What this example does NOT include

- A built tool — the bundle is a candidate, not frozen for build. Per the discipline, both teams would need to re-confirm + the operator would need to re-export.
- A witness record — there's nothing to witness yet. If both teams re-confirm and run a build attempt, then there's a witness record.
- An aggregated theme analysis. Aggregation is the team's choice after re-confirming.

## When to use this pattern jam-day

When two teams realize mid-Monday or Tuesday-morning that their offerings overlap and want to compose. Sequence:

1. Each team has a frozen submission already.
2. A mentor or operator runs `composition-merger.py` to produce a candidate bundle.
3. Both teams sit with the candidate bundle, read the conflicts list, and either:
   - Accept the resolutions and re-freeze in composed context (then build can proceed)
   - Adjust their original submissions and re-merge
   - Decide they don't actually want to compose (the candidate becomes a witnessed exploration, not a build path)

## Files in this directory

- `team-a-submission.json` — Eelgrass Observers' submission (fictional)
- `team-b-submission.json` — Kelp Monitors' submission (fictional)
- `candidate-bundle.json` — output of `composition-merger.py team-a team-b`
- `README.md` — this file

## Boundary

These are fictional teams and fictional offerings. The composition pattern is real and works. No real Nation-side restricted-release survey is referenced; the boundary is illustrative.
