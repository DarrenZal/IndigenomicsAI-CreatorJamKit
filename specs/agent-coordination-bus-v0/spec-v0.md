---
doc_id: indigenomics.jam.specs.agent-coordination-bus-v0.spec
doc_kind: jam-meta-spec
status: v0
visibility: public_sample
area: agent-coordination
last_updated: 2026-05-25
---

# Agent Coordination Bus — Spec v0

## Invitation

Provide a small, dependency-free substrate that lets participant-helping
agents emit the 7 messages defined in
[`specs/coordination-protocol-v0.md`](../coordination-protocol-v0.md),
have those messages validated against refusal-boundary rules, and store
them in append-only logs that mentors and witness drafters can read.

This is the **operational substrate** beneath the protocol — the
protocol says *what gets sent*, this spec says *what receives, validates,
stores, and audits it for v0 of the jam*.

## Schema reality check

Implementation follows the existing
[`specs/coordination-protocol-v0.md`](../coordination-protocol-v0.md)
schemas exactly. Two notes on divergence from a hypothetical "build a new
bus" approach:

1. **No new schemas.** The 7 wire types + common envelope are
   already specified. This bus does NOT introduce new fields.
2. **Stdlib-only Python.** The plan that initiated this work suggested
   `uv` + `pyproject.toml` + `pytest` for participants to get a
   reproducible environment. **The existing kit reality is**: every tool
   under `tools/*.py` (composition-merger, withdrawal-propagation,
   witness-record-validator, spec-linter, extract-submission-json) is
   plain `python3` with stdlib only and no dependency manifest. To
   compose cleanly with the existing kit, `bus.py` is **also**
   stdlib-only Python and tests use `unittest`, not `pytest`. No
   `pyproject.toml` is added. Participants who want a richer environment
   can layer one on top; the bus does not require it.

## What this v0 ships

- `scripts/jam/bus.py` — single-file CLI with subcommands `init`, `post`,
  `read`, `audit`, `validate`, `replay`.
- `scripts/jam/tests/test_bus.py` — 20 unittest cases, runnable via
  `python3 -m unittest scripts.jam.tests.test_bus -v`.
- `examples/agent-coordination-bus-demo/` — 13 demo messages (12 valid
  posts + 1 expected-fail) showing three Salish-Sea-ecological-framed
  teams using all 7 wire types in a realistic discovery / share /
  refuse / compose / withdraw / retry flow.

## Storage layout

Under a `bus_root` directory:

```
bus_root/
  bus/
    meta.json              # {version: "v0", created_at: iso8601}
    teams/
      <team-id>.jsonl      # append-only per-team log
    global.jsonl           # append-only global log
```

Every posted message is appended to BOTH involved teams' logs (from + to)
AND the global log. A team's own self-mark (e.g. internal `boundary_marker`)
appears once in its team log (from == to dedupes to one entry).

## Message lifecycle

1. **Author**: agent or human produces a JSON file matching one of the 7
   wire types' schemas + the common envelope.
2. **Validate**: `bus.py validate <file>` checks envelope shape, payload
   schema, refusal boundaries.
3. **Post**: `bus.py post <bus-root> <file>` validates again, then
   appends to both team logs + global log.
4. **Read**: `bus.py read <bus-root> --team <id>` or `--global`.
5. **Audit**: `bus.py audit <bus-root>` checks append-only invariant
   (every line valid JSON, message_ids unique).

## Validation rules (enforced)

All rules from coordination-protocol-v0.md §Refusal boundaries +
§Acceptance Criteria are enforced. Specifically:

| Rule | How enforced |
|---|---|
| Every cross-team content move needs `share_request` + `share_grant` | Schema requires references on `share_grant` |
| Per-request consent (no bulk-yes) | `composition_propose.acceptance_required_from` must be non-empty |
| Refusals can have no reason | `share_refuse.reason` is optional (validator does not require it) |
| Withdrawal can't be silently absorbed | `withdraw_notice.acknowledgment_required_from` must be non-empty |
| Protected content cannot travel in non-`boundary_marker` payloads | `share_request.what.preview.body` with `mode: marker_only` is scanned for protected-content-leak markers (`[PROTECTED]`, `[MARKER_ONLY]`, `[NOT_FOR_AI]`, `[NOT_FOR_REUSE]`, `[PRIVATE]`) |
| `witness_observe` is not authority | `not_an_authority_claim: true` is required; missing or `false` rejects |
| No reputation / trust score fields | Validator rejects unknown payload structures via schema-driven checks |
| Vague intents fail | `share_request.why.intent` must be a non-empty string ≥ 5 chars |

## What is NOT in v0 (but IS in v0.1)

- **HTTP transport.** v0.1 **ships as `scripts/jam/bus_server.py`** — a
  stdlib `http.server` thin shim around `bus.py` storage + validators.
  Endpoints: `GET /health`, `POST /messages` (bearer auth required),
  `GET /teams/<id>`, `GET /global`, `GET /audit`, `GET /audit/<id>`.
  Single shared bearer token via `BUS_SERVER_TOKEN` env var (fine for
  dev + small jams; not multi-tenant). 12 unittest cases (run +
  read + audit + 401/422/404 paths + path-traversal rejection +
  silent-share rejection at HTTP layer).
- **Cryptographic signatures.** v0's `signature` field is a SHA-256 hash
  of `<team_id>:<message_id>` (not a real key signature). Real signing
  requires gateway-issued team tokens (see participant-gateway spec).
- **Cross-bus federation.** Teams using separate bus roots must
  exchange serialized messages out-of-band. Federation is a follow-up.
- **Glob support in `.mirror-exclude`.** SHA-only for v0.

## Trade-offs deliberately accepted

- **File-based over HTTP**: trades multi-machine convenience for zero
  infra dependency and clean git-merge semantics. Participants can use
  the bus on their laptops without running any services.
- **No `pyproject.toml`**: trades dependency hygiene for compose-clean
  with the existing kit tools, all of which are stdlib python3.
- **No cryptographic auth**: trades zero-trust against forged messages
  for time-to-ship. Forged-message resistance lands when the production
  gateway wires its team-token issuance.

## Acceptance criteria

- All 7 wire types from coordination-protocol-v0.md validate as expected
  (happy paths + listed failure cases).
- Append-only invariant holds across replay of the 12-message demo.
- Each team's log shows only messages where it is `from` or `to`.
- A `share_refuse` with no `reason` field is accepted (refusal is
  complete; no justification required).
- A `share_request` with `mode: marker_only` and protected-content-leak
  text is rejected with a clear error.
- A `composition_propose` with empty `acceptance_required_from` is
  rejected.
- A `withdraw_notice` with empty `acknowledgment_required_from` is
  rejected.
- A `witness_observe` without `not_an_authority_claim: true` is rejected.

## Refusal boundaries (inherited from coordination-protocol-v0.md)

This bus MUST NOT:
- Persist messages that fail validation.
- Allow message_id collisions to be silently accepted (audit surfaces).
- Add trust / reputation / authority fields to any payload.
- Introduce side-channel transports that bypass `bus.py post`.

## Composition prompts

- Tuesday morning composition sprint: teams that pick this spec build
  on top — natural extensions are (a) HTTP wrapper, (b) gateway
  team-token signature, (c) cross-bus federation, (d) refusal-pattern
  visualization for the witness wall.
- The bus emits `witness_observe` records that
  [`witness-record-append-v0/`](../witness-record-append-v0/)
  (Tuesday) reads as draft input to the public witness wall.

## Next steps

If your team picks this spec:
1. Run the demo: `python3 scripts/jam/bus.py replay /tmp/bus examples/agent-coordination-bus-demo/`.
2. Read `spec-v0.md` (this file) and `coordination-protocol-v0.md` end-to-end.
3. Write your team's first `share_request` to a JSON file. Validate it.
4. Post it. Read the global log.
5. Decide what to extend (HTTP wrapper? federation? signature? visualization?).
6. Tuesday morning: emit `witness_observe` messages that flow into the witness wall.

## Boundary

This is a coordination substrate. It records what was said. It does not
certify, authorize, approve, or grant authority. Refusals are honored;
withdrawals propagate; protected content stays protected. The team's
judgment remains the deciding voice.

🛶
