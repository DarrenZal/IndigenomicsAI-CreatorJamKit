---
doc_id: indigenomics.jam.examples.agent-coordination-bus-demo
doc_kind: worked-example
status: v0
visibility: public_sample
last_updated: 2026-05-25
---

# Agent Coordination Bus — worked example

This is a worked example for [`specs/agent-coordination-bus-v0/`](../../specs/agent-coordination-bus-v0/),
showing three simulated teams using the 7 wire types from
[`specs/coordination-protocol-v0.md`](../../specs/coordination-protocol-v0.md)
to discover each other, share an offering, refuse a share, withdraw, and
propose a composition — with one obvious failure case at the end to
demonstrate validator behavior.

**Three teams** (Salish-Sea ecological framings):

- **`team-kelp-bed-observers`** (Victoria) — tracking kelp-bed health.
- **`team-salmon-counters`** (Vancouver) — counting salmon returning to spawn.
- **`team-steward-calendar`** (Remote) — coordinating habitat-restoration days.

## What the demo shows

| # | Message | What's happening |
|---|---|---|
| 01 | `share_request` (kelp → salmon) | Kelp team asks Salmon team to receive their offering "kelp-cover map" for possible joint use |
| 02 | `share_grant` (salmon → kelp) | Salmon team accepts with one added condition (attribution required) |
| 03 | `boundary_marker` (kelp → all) | Kelp team marks an internal cultural framing as **protected** — not for AI input, not for reuse |
| 04 | `share_request` (steward → kelp) | Steward team asks Kelp team for their kelp-cover map for restoration planning |
| 05 | `share_refuse` (kelp → steward) | Kelp team **refuses without reason** — refusal is a complete outcome |
| 06 | `share_request` (steward → salmon) | Steward team asks Salmon team for salmon-count data |
| 07 | `share_grant` (salmon → steward) | Salmon team accepts |
| 08 | `composition_propose` (kelp + salmon) | Kelp and Salmon propose composing into a "near-shore observation bundle" |
| 09 | `witness_observe` (kelp → witness drafter) | Kelp team agent emits an observation noting the refusal was tested cleanly |
| 10 | `withdraw_notice` (salmon → kelp) | Salmon team withdraws the share-grant from #02 |
| 11 | `share_request` (steward → kelp) | Steward retries earlier refused share-request with sharper intent |
| 12 | `share_refuse` (kelp → steward) | Kelp team refuses again — same outcome, recorded |
| 99 | `share_request` (rogue, **expected-fail**) | A malformed message that tries to leak `[PROTECTED]` content through marker-only mode — validator rejects |

## Try it

From the kit root:

```bash
# Initialize a fresh bus and replay the demo
python3 scripts/jam/bus.py replay /tmp/coord-bus-demo \
  examples/agent-coordination-bus-demo/

# Read the global ledger (one line per message)
python3 scripts/jam/bus.py read /tmp/coord-bus-demo --global --summary

# Audit append-only invariant
python3 scripts/jam/bus.py audit /tmp/coord-bus-demo

# Read what a single team saw
python3 scripts/jam/bus.py read /tmp/coord-bus-demo --team team-kelp-bed-observers --summary
```

Expected output: 12 posted, 1 expected REJECT (the rogue message at `99-`).

## What this is and isn't

- ✅ A worked example of the protocol's 7 wire types in motion.
- ✅ Demonstration that refusal is a complete outcome (no retry forcing).
- ✅ Demonstration that protected content cannot leak through non-boundary_marker channels.
- ❌ Not certification or authority for any team. The bus records what was said.
- ❌ Not a production agent transport. v0 is file-based JSONL for local dev.

## Boundary

This demo uses Salish-Sea-ecological framings (kelp, salmon, near-shore
habitat) per the kit's discipline — no Indigenous-cultural content, no
Nation-specific framings, no ceremonial language. Real participant team
data has its own boundaries; mentor surfaces decide what gets witnessed
and what doesn't.
