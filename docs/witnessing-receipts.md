# Witnessing-Receipt Schema v0.2

**Status:** v0.2 — Draft. Iteration of v0.1 incorporating K's review feedback (`kIndigenomics/AI` issue #21).
**Sibling artifacts:** `examples/witnessing/sample-receipt-v0.2.json` (worked example), `examples/witnessing/witnessing-receipt-v0.2.schema.json` (JSON Schema).
**Supersedes:** [`witnessing-receipt-schema-v0.1.md`](./witnessing-receipt-schema-v0.1.md) (kept as historical reference).
**Composes with:** `docs/specs/multi-witness-inference-v0.md` (S4/S5/S6/S7 outputs bind to AI witnesses), `docs/methodology/ruddick-commitment-pool-bridge.md` (CVLE × RVLFHG × commitment tuple as upstream formalism), `docs/synthesis/gift-obligation-and-return-obligations-v0.1.md` (R1-R5 + N4 + MS + HM rules as witness obligations).

## Changelog from v0.1

**Primary change:** Attribution-chain visibility is now an explicit, declared toggle. Not every reader of a receipt wants (or should see) the full witness chain. Defaults to opt-in.

- **New required field** `attribution_disclosure_level` (enum) — declares how much of the witness chain + attribution lineage is surfaced to a reader. K's review (issue #21, "5 things it is"): *"User-visible attribution: Great for dev, QC, research, but not every user will want to see the chain. Maybe it's a toggle?"* — adopted.
- **New optional field** `severity_resolution_authority` on each `ai_witness` — when an AI-witness flags a result at blocking severity, who has authority to resolve it? K's review ("5. Composition with the 13-lens annotation taxonomy"): *"If S4 raises a voice flag at severity: blocking, K should not be the arbiter. Either the question will require (a) deep knowledge of CAH's views & words — either she or an expert team member should decide these or (b) fundamental research skills — anyone with a discerning eye, including appropriate junior analyst, should be able to see if there's a mismatch."* — adopted. Schema now requires resolution-authority for any flag at severity `blocking`.
- **Refusal block enriched** — `state_history` made required (not just optional); each transition includes `witness_chain_ref` linking which witnesses arbitrated the transition. Surfaces gift-obligation R2 (correction & withdrawal) and R4 (honored refusal) discipline.
- **Hash canonicalization rule** — receipts MUST use RFC 8785 (JCS) JSON canonicalization for the content_hash computation. Removes the v0.1 open question.
- **Schema evolution rule** — readers MUST check `schema_version`; v0.2 readers gracefully ignore unknown fields; v0.1 readers SHOULD warn if presented a v0.2 receipt (missing `attribution_disclosure_level` field is the easy detection).
- **Carried unchanged from v0.1:** contributor / contribution / temporal / place / purpose / linked_to / witnesses subtree (except severity_resolution_authority addition) / transparency_tier / sovereignty / ip_framework / source_claim_ledger / multi_witness_bind / attribution_chain.

K findings *not* adopted in v0.2 (deferred or assigned elsewhere):
- **Vagueness detection** — not schema-side; multi-witness pipeline (`multi-witness-inference-v0.md`) issue. Routed there.
- **Cost estimates misleading** — operational concern; not schema. Routed to TELUS-conversation track.
- **6-10s response time** — UX concern; participant-gateway-UI work (offering #5).
- **S6 narrowness + 10th-check-contested-polarity reference** — multi-witness spec issue. Routed there.
- **Ensemble averaging/weighting consideration** — orthogonal architectural option. Recorded as v0.3+ exploration item; not v0.2 schema change.

## Purpose

A receipt is what the system gives back when someone contributes — a structured record of *who contributed what, when, where, why, witnessed by whom, under what sovereignty + IP frame, and with what disclosure level for the witness chain*. Receipts are the integration surface other Jam participants can plug onto. They're also the falsifiability backbone of the gift-obligation discipline: every commitment the system makes (R1 traceable use, R3 protection from misuse, etc.) becomes a checkable field in the receipt.

Receipts are not just metadata. They are the architecture's way of being **witnessed by the witnessed**. They make the system inspectable instead of opaque — *but inspection is opt-in, declared, and respectful of the reader's bandwidth*.

## Design principles

1. **Schema first, refine later.** v0.2 incorporates K's review feedback; expect v0.3 as worked examples surface more.
2. **Sovereignty + IP first-class, not afterthought.** Every receipt carries explicit sovereignty class, IP framework, and authorization basis. Defaults to most-conservative; participants opt into openness.
3. **Multi-witness composability.** Each receipt can bind to a multi-witness inference run; each witness type (self / peer / AI / schema / group / PGS) is a typed slot, not a free-text blob.
4. **Attribution as declared toggle.** v0.1 surfaced witness chain implicitly; v0.2 makes disclosure level explicit + reader-configurable. *(New in v0.2 per K.)*
5. **Refusal + withdrawal as first-class state.** A contribution's refusal isn't a deletion event; it's a state transition with its own attribution chain — and the state_history names which witnesses arbitrated each transition.
6. **Severity routing has named authority.** AI-witness flags at blocking severity must declare who has authority to resolve. *(New in v0.2 per K.)*
7. **Content-addressable + canonicalized.** Each receipt has a content-hash computed over RFC 8785 (JCS)-canonicalized JSON; receipts are tamper-evident across systems.
8. **Plug-in points clearly named.** Other Jam participants can integrate by emitting receipts conforming to this schema, or by binding to specific subfields.

## Field structure (v0.2)

### `receipt_id` (string, required)
Globally unique identifier. Format: `witnessing-receipt:<context>-<short-id>`. Example: `witnessing-receipt:srm-001`.

### `schema_version` (string, required)
Semver. v0.2 receipts MUST use `"0.2"`. Receipt readers MUST check schema version before parsing.

### `contributor` (object, required)
Who made the contribution. (Unchanged from v0.1.)
- `id` (string, required) — DID or other resolvable identifier
- `name` (string, required) — Display name
- `role` (enum, required) — `jam_participant` | `operator` | `system` | `nation_representative` | `community_member` | `other`
- `sovereignty_context` (string, optional) — The contributor's sovereignty container

### `contribution` (object, required)
What was contributed. (Unchanged from v0.1.)
- `type` (enum, required) — `claim` | `commitment` | `data` | `artifact` | `question` | `refusal` | `attestation` | `correction` | `withdrawal`
- `body` (object, required)
- `content_hash` (string, required) — SHA-256 over RFC 8785-canonicalized body
- `ref` (string, optional)

### `temporal` (object, required)
Unchanged from v0.1. (composes with TEMP-001 temporal schema).

### `place` (object, optional)
Unchanged from v0.1.

### `purpose` (string, optional)
Unchanged from v0.1.

### `linked_to` (array of receipt_ids, optional)
Unchanged from v0.1.

### `witnesses` (object, required)
The multi-witness composition. **v0.2 change: each `ai_witness` now has `severity_resolution_authority` when result.severity is `blocking`.**

- **`self_attestation`** (object, required) — Unchanged from v0.1.

- **`peer_witnesses`** (array, optional) — Unchanged from v0.1.

- **`ai_witnesses`** (array, optional) — Multi-witness inference pipeline outputs
  - `witness_type` (enum) — `S4_voice_audit` | `S5_citation_audit` | `S6_worldview_audit` | `S7_composition` | `schema_conformance` | `vagueness_detection` *(new in v0.2 placeholder; routed to multi-witness spec for definition)*
  - `pipeline_run_id` (string)
  - `result` (object) — Now structured (was string in v0.1):
    - `severity` (enum) — `pass` | `concern` | `blocking`
    - `summary` (string) — One-line human-readable summary
    - `confidence` (float 0-1, optional)
  - `severity_resolution_authority` (object, **required when result.severity = "blocking"**) — *(new in v0.2 per K)*
    - `authority_type` (enum) — `expert_team_member` | `subject_authority_holder` | `any_discerning_analyst` | `system_only` | `contributor_self`
    - `authority_id` (string, optional) — Specific person or role if applicable (e.g., `did:example:cah`)
    - `routing_rationale` (string) — Why this authority type per K's framework
  - `audit_trace` (object, optional) — Full audit detail; readers honor `attribution_disclosure_level`

- **`schema_witness`** (object, optional) — Unchanged from v0.1.
- **`group_witnesses`** (array, optional) — Unchanged from v0.1.
- **`pgs_witnesses`** (array, optional) — Unchanged from v0.1.

### `attribution_disclosure_level` (string, required) ← NEW in v0.2

Declares how much of the witness chain + attribution lineage is surfaced to a reader. Per K's review.

Values:
- `full` — Full witness chain + audit traces + complete attribution_chain visible to every reader. Use for dev / QC / research / formal-review contexts where transparency is the point.
- `summary` — Witness counts + audit pass/concern/blocking summary visible; full audit traces hidden but available on explicit request. Default for production-facing contexts where the receipt should be informative but not overwhelming.
- `opt_in` — Default-hidden; reader explicitly toggles "show witness chain" to see anything beyond self_attestation. Per K's suggested default for general users.
- `hidden` — Witness chain not visible to any reader; only schema-level conformance signal surfaces. For receipts where the contribution should land but the attribution mechanics are intentionally backgrounded (e.g., low-stakes peer attestation).

Recommended defaults by surface:
- Public `/graph` (Living Intelligence chat surface): `opt_in`
- `/graph/dev` lab + research surfaces: `full`
- Standard Creator-Jam participant interactions: `summary`
- Low-stakes peer attestation: `hidden`

The disclosure level is a contributor declaration (set at receipt creation) but readers MAY further restrict (e.g., a reader's view-layer may surface only summary even when the receipt declares full). Disclosure is a MAXIMUM permission, not a forced display.

### `transparency_tier` (enum, required)
Unchanged from v0.1. K's T1-T4 four-layer transparency. Distinct from `attribution_disclosure_level` (transparency_tier governs the *contribution's* visibility; attribution_disclosure_level governs the *witness chain's* visibility).

### `sovereignty` (object, required)
Unchanged from v0.1.

### `ip_framework` (object, required)
Unchanged from v0.1.

### `source_claim_ledger` (object, optional)
Unchanged from v0.1.

### `multi_witness_bind` (object, optional)
Unchanged from v0.1.

### `attribution_chain` (object, optional)
Unchanged from v0.1. Visibility honors `attribution_disclosure_level`.

### `refusal` (object, required) ← Enriched in v0.2
Refusal + withdrawal state.
- `state` (enum, required) — `active` | `refused` | `withdrawn` | `retracted` | `superseded`
- `reason` (string, optional)
- `withdrawal_authority` (string, required)
- `state_history` (array, **required in v0.2** — was optional in v0.1) — Audit trail
  - Each entry: `state`, `transitioned_at`, `transitioned_by`, `reason`, `witness_chain_ref` *(new — links to the witnesses that arbitrated the transition)*

## Worked example

See `examples/witnessing/sample-receipt-v0.2.json` — same Race Rocks kelp monitoring commitment as v0.1, updated to v0.2 schema.

## JSON Schema

See `examples/witnessing/witnessing-receipt-v0.2.schema.json`.

## Integration recipes

### Recipe 1: Default disclosure level for production-facing receipts
```python
emit_receipt(
    ...,
    attribution_disclosure_level="opt_in",  # Per K's default; reader toggles to see chain
)
```

### Recipe 2: Severity-blocking with named authority
When a multi-witness pipeline run produces an `ai_witness` with `result.severity = "blocking"`, the receipt MUST include `severity_resolution_authority`:
```json
{
  "witness_type": "S4_voice_audit",
  "result": {"severity": "blocking", "summary": "Detected voice_discipline violation: synthesis-across-asymmetric-registers"},
  "severity_resolution_authority": {
    "authority_type": "subject_authority_holder",
    "authority_id": "did:example:cah",
    "routing_rationale": "Voice-discipline at blocking severity requires deep knowledge of CAH's views/words per K's review §5"
  }
}
```

### Recipe 3: Reader's view honors disclosure level
A consumer reading the receipt MUST honor `attribution_disclosure_level`. E.g., a public-graph view rendering a receipt with `attribution_disclosure_level = "opt_in"` should show only `contributor.name`, `contribution.body`, `purpose`, and a "show witness chain" affordance — not the full `witnesses.ai_witnesses` audit traces by default.

### Recipe 4: Withdrawing a contribution (gift-obligation R2)
```python
withdraw_receipt(
    receipt_id="witnessing-receipt:srm-001",
    new_state="withdrawn",
    reason="Contributor decided to revoke after consultation with Race Rocks coordinators.",
    withdrawing_authority="did:example:alice",
    witness_chain_ref="mw-run:withdraw-arbiter-2026-05-14"
)
```
Receipt's `refusal.state` transitions to `withdrawn`; `state_history` appends an entry with `witness_chain_ref` capturing which witnesses arbitrated.

### Recipe 5: Manual Jam offering integration event (v0 session)

For the Creator Jam Offering Integration Session, do not block facilitation on schema evolution. A composition decision can be recorded under `contribution.type = "attestation"` or `"artifact"` with the composition details in `contribution.body`:

```json
{
  "kind": "composition_decision",
  "operation": "include",
  "fragment_id": "frag:commitment-pool-primer",
  "bundle_id": "bundle:open-kit-receipts-pool",
  "decision": "included",
  "reason": "Clean fit with receipt schema; ecological demo content is public and non-Nation-specific.",
  "authority_or_review_route": "operator",
  "report_ref": "docs/specs/jam-spec-composition-worked-example-v0.md"
}
```

Candidate v0.3 schema extension: add a first-class `composition_event` block with `operation`, `fragment_id`, `bundle_id`, `decision`, `reason`, `authority_or_review_route`, `prior_receipts`, and `derived_receipts`.

## Open questions (carried + new from v0.2)

1. **Vagueness detection witness type** — placeholder added in v0.2; full definition routed to multi-witness spec update (per K Finding 1: IPEA-attribution as vagueness-detection failure, not drift)
2. **PGS witness implementation** — still v1.5 roadmap; v0.2 keeps field as placeholder
3. **Disclosure-level downgrade rules** — if a receipt declares `full` but a reader's surface enforces `summary`, where is that policy declared? (Probably out-of-band, reader-side config; document in v0.3)
4. **Severity-blocking routing matrix** — v0.2 introduces `severity_resolution_authority` as a per-witness field; should there be a default-routing matrix (witness_type → default authority_type) that the schema enforces? Or strictly per-receipt declaration?
5. **Ensemble averaging / weighting** — K raised as architectural option to consider; not v0.2 schema change, recorded as v0.3+ exploration
6. **10th check (contested polarity) reference** — K asked what S6 references; multi-witness spec needs to ground or remove this reference
7. **Composition-event first-class support** — Jam v0 can record composition decisions in `contribution.body`; v0.3 should decide whether `spec_fragment`, `bundle`, `non_fit_report`, `handoff_packet`, and `composition_decision` become explicit contribution types.

## Sovereignty + IP discipline (unchanged from v0.1)

- Defaults: most-conservative → contributor explicitly opts into more openness
- Indigenous cultural / linguistic / ceremonial content: NEVER witnessed without `nation_specific_authorization` populated
- Schema enforces this via JSON Schema conditional validation
- Audit-trace: every receipt creation, modification, and state transition is logged; receipts are append-only

## Iteration plan

- **v0.1 (May 13 morning):** Initial spec + JSON Schema + sample receipt — shipped
- **v0.2 (May 13 afternoon — this doc):** K-review feedback adoption (`attribution_disclosure_level` toggle, `severity_resolution_authority` on blocking flags, hash canonicalization rule, schema evolution rule, refusal state_history with witness_chain_ref)
- **v0.3 (May 17):** First receipt validated against real multi-witness inference output; severity-routing matrix decision; disclosure-downgrade policy
- **v0.4 (May 22):** Integration guide for other Jam participants; cross-system anchoring pattern (Waka bridge); group-witness flow speced (jam-track aha-ritual integration)
