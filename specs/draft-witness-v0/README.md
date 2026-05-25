---
doc_id: indigenomics.jam.specs.draft-witness-v0
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Draft Witness v0 — stage 6 of the spec-drafting chain

After a team has frozen a build packet (via `spec_drafting_loop.py`)
and attempted a build (manually or via the TELUS lane), this CLI
takes the build outputs and produces a **witness record draft** via
Prompt 3 (witness-drafter) — closing the chain
`offering → packet → build → witness → wall`.

## What it is

- CLI: `scripts/jam/draft_witness.py` (stdlib-only)
- Takes: frozen build packet + optional build-attempt result + optional reviewer findings + a finding label
- Calls Prompt 3 via stub OR gateway adapter
- Renders a witness-record markdown DRAFT with fallback defaults so
  the output is never null
- Auto-runs `tools/witness-record-validator.py` on the draft and
  reports validator status
- Output is a DRAFT — team review remains authoritative

## What it is not

- Not autonomous publication. The draft never lands on the wall
  automatically — the team edits + reviews, then runs
  `scripts/jam/witness_append.py append <path> --confirm-publish`.
- Not a substitute for the team's voice. Model-drafted fields fall
  back to "team to fill" placeholders when the model output is missing.

## Try it (60 sec)

From the kit root:

```bash
# Stub mode (offline / deterministic)
python3 scripts/jam/draft_witness.py draft \
  /path/to/5-agentic-build-packet-v0.json \
  --finding built-clean \
  --team-name "My Team" \
  --out /tmp/my-witness-draft.md \
  --model-source stub

# Gateway mode (real model via local gateway)
source ~/projects/indigenomics-ai-gateway/.env.telus
python3 scripts/jam/draft_witness.py draft \
  /path/to/5-agentic-build-packet-v0.json \
  --finding built-clean \
  --team-name "My Team" \
  --out /tmp/my-witness-draft.md \
  --model-source gateway \
  --gateway http://localhost:8000 \
  --team-key "$DOGFOOD_TEAM_KEY" \
  --model telus-gemma
```

## Finding values

The `--finding` flag (default: `built-clean`):

| Finding | When to use |
|---|---|
| `built-clean` | All acceptance criteria passed |
| `fixed` | Initial attempt failed; one repair pass passed |
| `improved` | Attempt partially passes, better than no-change |
| `no-change` | Attempt did not pass acceptance criteria |
| `regressed` | Attempt broke something that was previously working |
| `failed` | Attempt failed; could not produce running code |
| `refusal` | Team chose not to surface this offering publicly — refusal-as-record |

## Composition

- [`agentic-spec-drafting-loop-v0`](../agentic-spec-drafting-loop-v0/) — produces the frozen build packet this CLI consumes
- [`tools/witness-record-validator.py`](../../tools/witness-record-validator.py) — invoked as the final gate before declaring the draft ready for review
- [`witness-record-append-v0`](../witness-record-append-v0/) — the natural next step after team review (`witness_append.py append <draft> --confirm-publish`)
- [`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../../participant-agent-context/PROMPTS_FOR_AGENTS.md) Prompt 3 (Witness Drafter) — the prompt this CLI sends to the model

## Tests

```bash
python3 -m unittest scripts.jam.tests.test_draft_witness -v
```

Expected: 8 tests OK (5 render + 3 stub-integration).

## Files

- `spec-v0.md` — formal spec
- `../../scripts/jam/draft_witness.py` — main CLI
- `../../scripts/jam/tests/test_draft_witness.py` — unittest cases

## Boundary

The output is a DRAFT. Team review remains the deciding voice. The
validator catches overclaim language but cannot vouch for accuracy.
Model-drafted fields fall back to placeholders when the model output
is missing — the renderer never produces a null record.

🛶
