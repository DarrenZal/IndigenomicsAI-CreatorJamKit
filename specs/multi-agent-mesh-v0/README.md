---
doc_id: indigenomics.jam.specs.multi-agent-mesh-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-26
---

# Multi-Agent Mesh v0 — review + aggregate

The sixth meta-spec. Layers two new roles on top of `orchestrator-v0`:
the **Reviewer** (stage 6.5, between witness-draft and publish) and the
**Aggregator** (post-N-rounds, surfacing patterns across runs).

Together they let an autonomous overnight loop (`overnight-loop-v0`)
produce something more than a stack of attempts — it can catch
overclaim drift inside a single round, and recommend prompt sharpening
across many rounds.

## What it is

- **Reviewer**: `scripts/jam/agent_reviewer.py` (stdlib + gateway).
  Reads a frozen build packet + build-attempt + witness-record draft;
  outputs `reviewer-findings.json` with per-check status + a
  `halt_publish` flag. The orchestrator consults this flag before
  invoking `witness_append.py`.

- **Aggregator**: `scripts/jam/agent_aggregator.py` (stdlib only).
  Walks N round subdirs + the cumulative wall; counts outcomes,
  refusal reasons, reviewer flags; emits `aggregator-recommendations.md`
  — markdown-only prose recommendations.

- **Orchestrator wire-in**: `orchestrator.py --mesh-mode` invokes
  Reviewer at stage 6.5. Without `--mesh-mode`, orchestrator behaves
  as v0.1 (no Reviewer call).

## What it is not

- Not a code-modification agent. v0 Aggregator outputs prose
  recommendations only; no `.diff` files, no machine-applicable
  patches. v0.2 may add diff generation.
- Not a Planner. There is no model picking which spec to run next; the
  orchestrator's existing round-robin substitutes for v0.
- Not authority. Reviewer findings shape publish/no-publish for the
  round; they do not certify the build attempt. Witness records still
  carry the standard receipt statement.
- Not a substitute for the validator. `witness_append.py`'s overclaim
  validator is still the final regex gate. Reviewer adds a
  model-level coherence check before that gate.

## Reviewer — the five checks

Reviewer asks the model to evaluate the witness draft against the
build packet + attempt outcome along five axes:

1. **acceptance-criteria-vs-attempt** — does the draft's narrative
   align with the build packet's acceptance criteria + the
   build-attempt outcome?
2. **claim-vs-evidence-coherence** — does the "what worked" section
   match `test_passed_final` / `finding`? If tests failed but the
   draft asserts success without qualification → `halt`.
3. **boundary-honored-in-draft** — when the packet's
   `excluded_inputs` is non-empty, does the draft's
   "boundaries that remain" section explicitly name them?
4. **attempted-vs-witnessed-tense** — flag asserted-tense
   ("certifies", "guarantees", "validates") vs attempted-tense
   ("attempted", "observed", "recorded").
5. **overclaim-vocabulary** — any of certified / approved /
   authorized / validated / legitimate / official / "successful" as
   summary judgment / "failed" as summary judgment, OUTSIDE the
   standard outcome words (`built-clean`, `no-change`, `diverged`,
   `fixed`, `improved`, `regressed`, `refusal`) → `halt`.

Each check returns `ok | flag | halt`. Any `halt` forces
`halt_publish=true`. Missing checks are backfilled at `ok` with a
note that the model didn't return that check.

## Reviewer refusal-as-record

If the witness draft requests cultural authorization, the Reviewer
itself can refuse — emits `{"refusal": "..."}` instead of findings.
The orchestrator records this as a halt with the refusal reason
preserved.

## Aggregator — what patterns it surfaces

Aggregator does NOT invent recommendations. Thresholds are
intentionally conservative:

- **Repeated refusal reason** (≥2 rounds) → "consider removing those
  specs OR sharpening the relevant prompt"
- **Overclaim vocabulary flagged ≥2 times** → "consider adding these
  terms to Prompt 3's forbidden-words list"
- **Boundary-honored flagged ≥2 times** → "consider strengthening
  Prompt 3's instruction to enumerate `excluded_inputs`"
- **Model with 0 publishes across ≥3 rounds** → "consider whether
  this model is mismatched to the spec menu"
- **Spec with 0 publishes across ≥3 rounds** → "consider whether the
  spec body consistently trips a refusal layer"
- **Reviewer halt-rate ≥50%** → "Prompt 3 may need sharpening, OR
  reviewer threshold needs calibration"

If no patterns clear threshold: "No multi-round patterns detected at
the threshold for recommendation."

## Try it (60 sec — mesh-mode against local gateway)

```bash
source ~/projects/indigenomics-ai-gateway/.env.telus
python3 scripts/jam/orchestrator.py run \
  --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \
  --gateway http://localhost:8000 --team-key "$DOGFOOD_TEAM_KEY" \
  --models telus-gemma \
  --specs flow-funding-frontier-map \
  --max-specs 1 \
  --max-telus-calls 20 \
  --time-budget-min 4 \
  --builder-mode telus \
  --mesh-mode \
  --bus-root /tmp/mesh-smoke-bus \
  --out-dir /tmp/mesh-smoke
```

Expected: full chain with a `6.5-reviewer: ok` line between
`6-witness-draft` and `7-publish`. The `reviewer-findings.json`
appears in the per-run dir.

## Aggregator standalone

```bash
python3 scripts/jam/agent_aggregator.py aggregate \
  --rounds-dir ~/overnight-jam-2026-05-26/rounds \
  --wall-root ~/overnight-jam-2026-05-26/wall \
  --out ~/overnight-jam-2026-05-26/aggregator/recs.md
```

## Discipline

- Reviewer never rewrites the draft. Findings only.
- Reviewer is a non-fatal stage in mesh-mode: a Reviewer exception
  (gateway error, parse failure) is recorded but does NOT halt the
  round. The validator at stage 7 is still a hard gate.
- Aggregator output is recommendations, NOT decisions. Operator
  decides whether to apply any of them. "No patterns observed" is a
  valid output and the most common one for short runs.
- Halt status propagates: ANY check returning `halt` forces
  `halt_publish=true` even if the model said `review_passed=true`.
- Reviewer model defaults to the same model running the witness
  draft for that spec. Different-model reviewing is a v0.2 option
  (deliberate independence between drafter + reviewer).

## Files

```
scripts/jam/agent_reviewer.py
scripts/jam/agent_aggregator.py
scripts/jam/orchestrator.py       # --mesh-mode flag + stage 6.5
scripts/jam/tests/test_agent_reviewer.py
scripts/jam/tests/test_agent_aggregator.py
scripts/jam/tests/test_orchestrator_mesh.py
```

## Boundary

This is meta-spec scaffolding for the autonomous-execution layer. It
is not the participant experience; participants at the jam are not
expected to interact with the Reviewer or Aggregator directly. They
appear in operator-facing artifacts (overnight log, recommendations
markdown) — read by humans deciding whether to sharpen the substrate.
