---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: agent-coordination
last_updated: 2026-05-25
---

# Coordination Protocol v0

## Invitation

Build a small agent-to-agent messaging library that lets participant-helping
agents exchange offerings, boundaries, refusals, and composition proposals
**without** silently sharing content, aggregating consent, or letting any
party override another team's withdrawal. The protocol is the wire format
underneath the [multi-agent coordination design](../docs/multi-agent-coordination-design.md);
this spec is the message-level contract.

The substrate this protocol sits inside is the gateway's existing
three-dropdown shape (*specs* / *models* / *harnesses*) — message types
described here are **what flows between agent instances** running inside
that substrate, not a new infrastructure layer. Payloads can resolve to
KOI knowledge-object IDs where shared content is referenced across teams
(deduplicating offerings across teams' agent contexts).

## What Could Be Built

- A JSON schema set for the seven message types below.
- A small reference library (Python or TypeScript) that validates messages,
  signs them with a team-scoped token, and routes through either a gateway
  channel or a local shared-folder transport.
- A fixture set with one of each message type, including failure cases
  (silent share attempt, aggregated consent, ignored withdrawal).
- A validator that rejects messages violating the refusal boundaries (§5).
- A simple ledger view showing every message exchanged between two teams
  during a Jam, with refusals as first-class entries.

## Message types

All messages share a common envelope and validate against the boundary
vocabulary in [`team-submission-v0`](../templates/team-submission-v0.md).

### Common envelope

```yaml
message_id: string (uuid)
created_at: datetime
from_agent:
  team_id: string
  participant_id: optional string  # if the message originates from a person agent
  agent_role: spec-drafting | boundary-checker | witness-drafter | mediator | other
to_agent:
  team_id: string
  participant_id: optional string
  agent_role: optional string
message_type: share_request | share_grant | share_refuse | withdraw_notice |
              boundary_marker | composition_propose | witness_observe
references: list of message_id   # prior messages this builds on
signature: string                 # team-scoped token; see §gateway notes
```

### `share_request`

Agent A asks agent B to receive content.

```yaml
what:
  content_kind: offering | spec_fragment | boundary_marker | acceptance_criterion |
                refusal_log_entry | other
  preview:
    mode: cleared_text | paraphrased | marker_only
    body: string   # if mode=marker_only, body MUST NOT contain protected content
why:
  intent: string   # concrete new use intent (vague intents fail validation)
  target_spec: optional string   # e.g. specs/commitment-pool-route-diagnostic.md
consent_terms:
  display_scope: whole | partial | spoken-only | none
  ai_input_scope: whole | partial | none
  reuse_scope: not-granted | ask-first | team-only | public-ok
  expires_at: optional datetime
```

### `share_grant`

Agent B accepts. May add conditions.

```yaml
references: [<share_request.message_id>]
granted: true
added_conditions:
  - condition: string   # e.g. "attribution required as 'Team Kelp Watch'"
  - condition: string   # e.g. "marker-only persists across composition"
effective_until: optional datetime
```

### `share_refuse`

Agent B declines. Reason is **optional and not required**.

```yaml
references: [<share_request.message_id>]
granted: false
reason: optional string
log_as_learning: boolean   # if true, mentor surface receives the refusal as data
```

### `withdraw_notice`

Agent A withdraws something previously shared. References the original
`share_request` and (if granted) the `share_grant`.

```yaml
references: [<share_request.message_id>, <share_grant.message_id>]
withdrawn_record_ids:
  - string
propagation_manifest: optional inline manifest (shape per tools/withdrawal-propagation.py)
acknowledgment_required_from:
  - team_id   # every receiving team must acknowledge before this notice is closed
```

### `boundary_marker`

Agent A names a boundary without disclosing content. Mirrors the kit's
marker-only discipline.

```yaml
label: string
boundary_type: marker-only | not-for-AI | not-for-reuse | private | protected |
               review-required
marker_text: string         # MUST NOT contain protected content
disallowed_use:
  - summarize | tag | embed | route | transform | send-to-ai | aggregate
review_authority: optional string   # e.g. "Carol Anne for cultural framing"
```

### `composition_propose`

Agent A suggests composing offerings with agent B. References both teams'
frozen `team-submission-v0` records.

```yaml
proposed_bundle_id: string
composes:
  - team_id: A
    submission_id: string
    offerings: [list of offering_ids]
  - team_id: B
    submission_id: string
    offerings: [list of offering_ids]
target_spec: optional string
expected_conflicts: optional list   # surfaced ahead via composition-merger.py dry-run
acceptance_required_from:
  - team_id: A
  - team_id: B
```

### `witness_observe`

Agent → witness drafter or operator/mentor surface. Flagged as observation.

```yaml
observed:
  kind: divergence | refusal_tested | untracked_allocation_named |
        boundary_crossed | composition_landed | other
  body: string
not_an_authority_claim: true   # required; the validator rejects messages where this is absent or false
attribution:
  agent_role: string
  source_messages: [list of message_id]
routing: witness_drafter | mentor | operator | facilitator
```

## Inputs

- Two or more participant agents, each loaded with a knowledge bundle and
  one of the prompts in [`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../participant-agent-context/PROMPTS_FOR_AGENTS.md).
- Per-agent settings + per-cross-team rules (see
  [`docs/multi-agent-coordination-design.md`](../docs/multi-agent-coordination-design.md) §4a).
- A transport: gateway-mediated channel **or** shared-folder fallback.

## Outputs

- Validated messages stored as JSON.
- A coordination ledger (append-only) per team pair.
- Diagnostic output from the validator when a message fails refusal-boundary
  checks.
- Optional witness-record observations routed to the Tuesday witness drafter.

## Acceptance Criteria

- All seven message types parse against the schema.
- A `share_request` with `mode: marker_only` and `body` containing protected
  content fails validation.
- A `share_refuse` without `reason` succeeds (reason is optional).
- A `withdraw_notice` is not considered closed until every team listed in
  `acknowledgment_required_from` has acknowledged.
- A `composition_propose` is not actionable until both `acceptance_required_from`
  parties have signed corresponding `share_grant` messages for every shared
  offering.
- A `witness_observe` missing `not_an_authority_claim: true` is rejected.
- The ledger preserves refusals as first-class entries; refusals are not
  summarised away.
- Per-cross-team consent does not aggregate into a single boolean; each
  `share_request` is its own consent decision.

## Refusal boundaries

This spec MUST NOT:

- Allow agents to share content silently. Every cross-team content move
  requires a `share_request` + `share_grant` pair.
- Aggregate multiple share-decisions into a single "yes" flag. Per-request
  consent is mandatory; bulk-yes is rejected by the validator.
- Allow one team's withdrawal to be silently ignored by another. Until every
  receiving team acknowledges, downstream surfaces remain flagged.
- Treat a `witness_observe` as authority. Observations are observations;
  judgment is humans + stewards.
- Encode reason-required refusals. A team may refuse with no reason; the
  protocol records the refusal.
- Permit protected or marker-only content to travel in any payload other
  than `boundary_marker`. The validator strips and rejects.
- Introduce a "trust score" or "reputation" field. Per
  [`witness-record-interop-profile.md`](witness-record-interop-profile.md).

## Composition prompts

This spec composes well with:

- [`witness-record-interop-profile.md`](witness-record-interop-profile.md) —
  `witness_observe` messages become draft witness records; visibility tiers
  align.
- [`claims-evidence-coherence-report.md`](claims-evidence-coherence-report.md) —
  `share_request` payloads referencing claims can be validated for evidence
  freshness before the share lands.
- [`commitment-pool-route-diagnostic.md`](commitment-pool-route-diagnostic.md) —
  `composition_propose` is the natural carrier for offer-need matches that
  the diagnostic surfaces.
- [`untracked-allocation-ledger.md`](untracked-allocation-ledger.md) —
  agent observations of off-graph stewardship enter the ledger via
  `witness_observe` with `kind: untracked_allocation_named`.
- [`spec-composer-bundle-board.md`](spec-composer-bundle-board.md) —
  the board surface absorbs `composition_propose` messages as candidate
  bundle cards.

## First Build Step

Create seven fixture messages (one per type, plus three failure cases:
silent-share, aggregated-yes, ignored-withdrawal) and a
`validate-coordination-message` script that prints diagnostics for each.

## Source Notes

Drafted from the kit's existing boundary vocabulary
([`docs/MENTOR_FIELD_GUIDE.md`](../docs/MENTOR_FIELD_GUIDE.md) §2),
the cross-team artifacts in §11, the sample agent prompts
([`participant-agent-context/PROMPTS_FOR_AGENTS.md`](../participant-agent-context/PROMPTS_FOR_AGENTS.md)),
and the two existing cross-team tools
([`tools/composition-merger.py`](../tools/composition-merger.py),
[`tools/withdrawal-propagation.py`](../tools/withdrawal-propagation.py)).
Authorization vocabulary preserved unchanged from
[`templates/team-submission-v0.md`](../templates/team-submission-v0.md).

## Next steps

If your team picks this spec:

1. Read [`docs/multi-agent-coordination-design.md`](../docs/multi-agent-coordination-design.md)
   for the layer above this protocol (architectural routes, UX layers,
   failure modes).
2. Open [`templates/team-submission-v0.md`](../templates/team-submission-v0.md) —
   fill in your team's vision, spec, offerings, boundaries, authorization,
   and witnessed_working using the five questions from
   [`docs/facilitator-quick-card.md`](../docs/facilitator-quick-card.md).
3. Build the seven fixture messages first; let the validator drive the
   schema.
4. Before freeze, run `python3 tools/spec-linter.py <your-draft.json>` to
   catch the most common failure modes.
5. Walk through the freeze checklist with your facilitator.
6. After build: `python3 tools/witness-record-validator.py <your-witness-record.md>`
   Tuesday morning.

If this spec is preflighted, see `specs/preflights/<this-spec-name>/` for
the worked example + TELUS lane runs. Index: `specs/preflights/README.md`.
