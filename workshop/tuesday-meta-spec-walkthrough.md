---
doc_id: indigenomics.jam.workshop.tuesday-meta-spec-walkthrough
doc_kind: workshop-playbook
status: v0
visibility: public_sample
last_updated: 2026-05-25
duration: 30 minutes
audience: jam mentors + participants picking a meta-spec for the composition sprint
---

# Tuesday — Meta-Spec Walkthrough

A 30-minute walk through the three meta-specs that shipped during Day 1
of the jam. The point: **the jam's substrate is buildable from the
kit's own primitives**. Teams that pick a meta-spec on Tuesday's
composition sprint are extending the substrate they're already using.

## Audience

- Mentors orienting teams to the meta-specs
- Teams choosing what to build on Tuesday's composition sprint
- Anyone curious how the jam dogfoods itself

## What to say (and not say)

✅ Say:
- "These three specs were built during Day 1 of this same jam, in ~6 hours."
- "Pick one. Extend it. Or compose two together."
- "Each spec has tests; extensions should add tests too."
- "'Doesn't fit yet' is a complete outcome — saying no to extending is honored."

❌ Don't say:
- "These are authority / certified / production-ready."
- "Your team has to extend them."
- "Pick this one over that one." (let teams choose)

## The three meta-specs (5 min each)

### 1. `specs/agent-coordination-bus-v0/`

**What it is**: File-based JSONL bus implementing the 7 wire types
from `coordination-protocol-v0.md`. Two team agents (or two humans
typing JSON) can post share_request / share_grant / share_refuse /
withdraw_notice / boundary_marker / composition_propose / witness_observe
to each other with full validation.

**Try it (60 sec)**:

```bash
# Replay the 13-message demo with 3 simulated teams
python3 scripts/jam/bus.py replay /tmp/bus-demo examples/agent-coordination-bus-demo/

# See the global ledger
python3 scripts/jam/bus.py read /tmp/bus-demo --global --summary

# Verify append-only
python3 scripts/jam/bus.py audit /tmp/bus-demo
```

**Extension ideas (composition sprint)**:
- HTTP wrapper (FastAPI) — gives multi-machine teams the same primitives
- Gateway-token signature — replace the placeholder `signature` field with real auth
- Cross-bus federation — exchange serialized messages across team boundaries
- Refusal-pattern visualization — render the wall of refusals as a teaching surface

### 2. `specs/agentic-spec-drafting-loop-v0/`

**What it is**: 5-stage orchestrator that takes a loose offering
through Prompts 1, 2, 4 + composition engine to produce a frozen
`agentic-build-packet-v0.json`. Stub mode is deterministic offline;
gateway mode hits the local indigenomics-ai-gateway.

**Try it (60 sec)**:

```bash
# Offline / deterministic
python3 scripts/jam/spec_drafting_loop.py run \
  examples/spec-drafting-loop-demo/offering-kelp-cover-map.md \
  --model-source stub --confirm-freeze \
  --team-name "Kelp Bed Observers" --team-site Victoria \
  --out-dir /tmp/runs
```

**Extension ideas (composition sprint)**:
- Stage 6: witness drafting (Prompt 3) downstream of build execution
- Structured-parse gateway responses (v0 captures raw text)
- Multi-model fan-out (Gemma + Qwen + gpt-oss in parallel for diversity)
- Real facilitator freeze flow (interactive checklist, not autonomous)
- Real build attempt execution (compose with TELUS lane preflight pipeline)

### 3. `specs/witness-record-append-v0/`

**What it is**: Public witness-wall publication CLI. Reads a witness
record markdown, validates against overclaim language + receipt
statement, requires `--confirm-publish`, then appends to
`wall/witness-records/`. Renders the wall as a single markdown doc.
Refusal-as-record publishes equally.

**Try it (60 sec)**:

```bash
# Publish all 3 sample records to a temp wall
WALL=/tmp/wall-demo
rm -rf $WALL
for f in examples/witness-wall-v0/sample-record-*.md; do
  python3 scripts/jam/witness_append.py append "$f" --confirm-publish --wall-root $WALL
done

# Render the wall
python3 scripts/jam/witness_append.py wall --wall-root $WALL
```

**Extension ideas (composition sprint)**:
- HTML rendering (markdown only in v0)
- RSS / Atom feed
- Gateway-token authentication (anyone can write to wall dir today)
- Cross-wall federation (multiple sites)
- Per-team digest emails

## How they compose

```
Offering -> drafting-loop -> frozen build packet -> TELUS lane -> outputs
                ↓                                                    ↓
            (witness_observe to bus)                       Witness record
                                                                  ↓
                                                          witness_append
                                                                  ↓
                                                           Public wall
```

The bus carries cross-team coordination at any point. The drafting
loop produces frozen packets. The wall publishes the outcomes.

Tuesday composition sprint material:
- Team A picks `bus` + builds HTTP wrapper. Team B picks `wall` + builds RSS feed. Together they make a witness-wall-with-realtime-updates.
- Team C picks `drafting-loop` + adds stage 6 (witness drafting). Their output flows directly to `witness_append`.
- Team D picks `bus` + adds federation. Two of those federated buses can be the substrate for cross-team coordination across Vancouver + Victoria sites.

## Discipline reminder for facilitators

Each meta-spec already enforces:
- ✅ Consent at every membrane crossing
- ✅ Refusal is a complete outcome
- ✅ Boundaries before sharing
- ✅ AI is execution helper, not judgment authority

Extensions teams build on Tuesday should preserve these. If a team's
extension would BYPASS one (e.g., a bus extension that allows aggregated
consent), surface it during composition review.

## Bugs caught + fixed during Day 1

Two bugs in existing kit tooling surfaced during meta-spec work:

1. **`tools/witness-record-validator.py`** was rejecting every
   well-formed receipt statement (multi-line wrap broke the
   line-scoped disclaimer-context check). Fixed at source via 3-line
   lookback. **Without this fix, Tuesday's witness wall would have
   refused every record.**

2. **`mirror-to-public.sh`** used `--first-parent` which hid
   second-parent commits from the patch series. Caught on first
   mirror run. Patched + documented.

These illustrate: **meta-spec work tests the substrate**. Building on
top found bugs that downstream users would have hit. Worth showing
during Tuesday: extensions are a learning surface, not just deployment.

## Closing

"The relational economy isn't built once and shipped. It's enacted, in
code that refuses certain moves, every time someone runs the CLI. The
substrate teaches the discipline by enforcing it."

🛶
