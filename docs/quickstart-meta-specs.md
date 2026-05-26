---
doc_id: indigenomics.jam.docs.quickstart-meta-specs
doc_kind: participant-quickstart
status: v0
visibility: public_sample
last_updated: 2026-05-26
audience: jam participants picking a meta-spec to extend on Tuesday
---

# Quickstart — using the meta-specs

The kit ships **5 meta-specs** that compose the jam's own substrate. This
quickstart is for participants who want to USE them as participants OR
EXTEND them on Tuesday's composition sprint.

The 5 meta-specs:

| # | Spec | What it does | Where it composes |
|---|---|---|---|
| 1 | [agent-coordination-bus-v0](../specs/agent-coordination-bus-v0/) | File-based JSONL bus implementing the 7 wire types from `coordination-protocol-v0.md`. Per-team append-only logs + audit. | Cross-team coordination at any chain step |
| 2 | [agentic-spec-drafting-loop-v0](../specs/agentic-spec-drafting-loop-v0/) | 5-stage pipeline: offering → spec draft (Prompt 1) → boundary check (Prompt 2) → composition (Prompt 4 optional) → freeze. | Takes an offering, produces a frozen build packet |
| 3 | [draft-witness-v0](../specs/draft-witness-v0/) | Stage-6 CLI: takes a frozen build packet + build outputs → witness record DRAFT via Prompt 3. | After the build, before the wall |
| 4 | [witness-record-append-v0](../specs/witness-record-append-v0/) | Public witness-wall publication. `--confirm-publish` per record, overclaim validator, refusal-as-record support. | Tuesday canoe-landings |
| 5 | [orchestrator-v0](../specs/orchestrator-v0/) | Autonomous network composing 1+2+3+4: given the spec menu, runs the chain for N specs, honors refusal at every layer. | Tuesday composition sprint: extend with your own primitives |

Plus the bus HTTP wrapper (`scripts/jam/bus_server.py`) for multi-machine teams.

## Try the full chain (5 min)

Pre-req: you have the kit cloned and Python 3.10+.

```bash
cd ~/projects/IndigenomicsAI-CreatorJamKit

# 1. Run the full chain offline (stub model, no network)
# Write a small offering:
cat > /tmp/my-offering.md <<EOF
---
title: My team's tool idea
contributor: team-mine
---

# What we want to build

A small CLI that reads JSON of bird counts and writes a markdown receipt
grouping by species, with no inference about populations.
EOF

# 2. Run the drafting loop in stub mode
python3 scripts/jam/spec_drafting_loop.py run \
  /tmp/my-offering.md \
  --model-source stub --confirm-freeze \
  --team-name "My Team" --team-site other \
  --out-dir /tmp/my-runs

# 3. Read the frozen packet
RUN=$(ls -dt /tmp/my-runs/2* | head -1)
cat "$RUN/5-team-submission-v0.md"

# 4. Draft a witness record (you'd build something first, then witness)
python3 scripts/jam/draft_witness.py draft \
  "$RUN/5-agentic-build-packet-v0.json" \
  --finding built-clean \
  --team-name "My Team" \
  --out /tmp/my-witness.md \
  --model-source stub

# 5. Publish to a personal wall
python3 scripts/jam/witness_append.py append /tmp/my-witness.md \
  --confirm-publish --wall-root /tmp/my-wall

# 6. See the wall
python3 scripts/jam/witness_append.py wall --wall-root /tmp/my-wall
```

That's the full chain. Replace `--model-source stub` with
`--model-source gateway --gateway <url> --team-key <key>` (when Shawn
issues team keys) to use real TELUS models.

## Try the autonomous orchestrator (5 min)

Pre-req: local TELUS-mode gateway running, or use stub.

```bash
# Pick 3 candidate specs from the menu (preflighted-clean, non-cultural)
python3 scripts/jam/orchestrator.py run \
  --kit-root . \
  --gateway http://localhost:8000 --team-key iai_dev_victoria \
  --models telus-qwen \
  --max-specs 3 --max-telus-calls 30 --time-budget-min 15 \
  --bus-root /tmp/my-orch-bus \
  --out-dir /tmp/my-orch-runs

# Report on what ran
python3 scripts/jam/orchestrator.py report /tmp/my-orch-runs
```

The orchestrator will:
1. Pick 3 specs from the candidate list
2. Generate a participant-shape offering for each (TELUS)
3. Drive them through the chain
4. Refuse to attempt any spec with cultural-content markers
5. Publish built-clean records OR refusal-as-record entries to the wall

## Try the bus HTTP wrapper (3 min)

```bash
# Start the server with a dev token
BUS_SERVER_TOKEN=my-dev-token-12345 \
  BUS_ROOT=/tmp/my-bus \
  python3 scripts/jam/bus_server.py --port 8765 &

# Post a share_request from another shell:
curl -X POST http://localhost:8765/messages \
  -H "Authorization: Bearer my-dev-token-12345" \
  -H "Content-Type: application/json" \
  -d @some-message.json

# Read what's there:
curl http://localhost:8765/global | jq .
curl http://localhost:8765/audit | jq .

# Stop the server (Ctrl-C from its terminal)
```

## What participants build on Tuesday

The composition sprint is for EXTENDING meta-specs. Some directions
already documented as v0.1 enhancements:

- **Bus**: federation between two bus instances; gateway-token signature (replaces single shared secret); reputation-free coordination metrics
- **Drafting-loop**: multi-model fan-out (run all 3 TELUS models in parallel per stage, return diverse drafts); auto-detect cultural framings BEFORE TELUS call
- **Draft-witness**: Prompt 3 v0.2 (sharpened like Prompt 2 was); witness-cluster diffing across multiple records
- **Wall**: HTML rendering with CSS; RSS feed; cross-wall federation
- **Orchestrator**: TELUS-builder mode (model generates the CLI code, not just spec); 2-round reviewer loop; cross-spec composition (e.g., spec A's outputs become spec B's inputs)

## Discipline reminders

These hold regardless of what you build:

- **Refusal is a complete outcome**. If a spec doesn't fit, "doesn't fit yet" is success.
- **Witness records are not certifications**. They state what happened.
- **Cultural / Nation-specific content requires explicit authorization**. The orchestrator's gatekeeper is conservative — false-positives refuse-by-default.
- **Boundaries before sharing**. Use `boundary_marker` messages on the bus; don't leak protected content via other payload types.
- **AI is execution helper, not judgment authority**. Every CLI marks `not_an_authority_claim: true` or equivalent.

## Pointers

- Full specs: `specs/`
- Worked examples: `examples/`
- Tests (71/71): `python3 -m unittest discover -s scripts/jam/tests`
- Mentor Field Guide: `docs/MENTOR_FIELD_GUIDE.md`

## Boundary

This quickstart points at participant-eligible substrate. Extensions
you build participate in the Tuesday-sprint demonstration; nothing
here certifies, authorizes, or grants authority. The team's judgment
remains the deciding voice.

🛶
