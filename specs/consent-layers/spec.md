---
doc_kind: jam-spec
status: draft
visibility: public_sample
area: consent_infrastructure
last_updated: 2026-05-25
spec_shape: integrated
note: |
  This jam-spec covers three coordinated layers (participant app, organizer
  dashboard, AI content compliance reviewer) in one document — a slight
  deviation from the kit's typical narrow-spec convention. It could later be
  split into three narrow sub-specs if maintainers prefer; the integrated
  form exists to support single-document review and coding-agent handoff,
  which is the purpose of the sibling `handoff-prompt.md` in this folder.
---

# Consent Layers

## Invitation

Build a small consent infrastructure for in-person gatherings — a participant mobile web app, an organizer dashboard, and an AI content-compliance reviewer — coordinated by a shared living consent state, so participants control their data and attention sovereignty in real time and every published artifact and connection request flows through a consent gate before it leaves the room.

## What Could Be Built

- A QR-launched participant mobile web app with visual sliders for two layers (data and attention), a My Consent Card view, a plain-language activity feed, per-use revocation, and a portable Kantara-format consent receipt export.
- An organizer dashboard with a Cultural Calibration Profile editor (signed by the convening organization), an action-attached Live Consent View, an Asset Pipeline Queue with agent verdicts and human signatures, an Audit Trail Browser, and a re-consent request workflow.
- An AI Content Compliance Reviewer that scans publication drafts (press release, recap, social caption, transcript) against current consent state, outputs a structured redline (approved / re-consent required / violation / suggested rewording), and emits a non-disable-able AI Use Receipt per call.
- A shared Real-time Consent Bus that propagates each state change within 24 hours to all subscribed downstream subscribers, including any sponsor CRM that has elected to integrate.
- A coordinated set of eight record types (Consent Receipt, Consent State Change Event, Cultural Calibration Profile, Asset Pipeline Entry, Compliance Review, Audit Trail Entry, AI Use Receipt, and an optional Connection Request) sharing common schemas and producing a single auditable trail per event.
- (Optional) An Attention Gatekeeper agent that routes approach requests according to recipient attention state.

## Inputs

### Participant layer

- `participant_id`
- `event_id`
- `cultural_calibration_profile_ref`
- `data_consent`: object with dimensions `face`, `voice`, `name`, `quote`, `presence`, `post_event_reference`, each with `level` ∈ `no | anonymized | within_event | public` and `valid_until`
- `attention_consent`: object with `approach_mode` ∈ `no | warm_intro | topic_scoped | open`, `topics_open[]`, `topics_closed[]`, `daily_contact_budget`, `quiet_windows[]`
- `state_changes[]`: each with `change_id`, `dimension`, `from_level`, `to_level`, `timestamp`, `actor`
- `revocation_history[]`: per-dimension and per-specific-use append-only

### Organizer layer

- `convening_org_id`
- `cultural_calibration_profile`: object with `default_states[]`, `nation_specific_overrides[]`, `language_settings[]`, `authorized_by`, `valid_until`, `agents_enabled[]`, `ai_vendor`, `model_version_pinned`
- `asset_pipeline_entry`: object with `asset_id`, `asset_type`, `identifiable_subjects[]`, `quoted_speakers[]`, `embedded_images[]`, `compliance_status` ∈ `pending | clear | needs_review | violates_consent`, `agent_verdict_ref`, `human_decision`, `human_signature`, `decision_timestamp`
- `connection_request` (if Attention Gatekeeper deployed): `request_id`, `requester_id`, `recipient_id`, `proposed_topic`, `routing_decision`
- `audit_trail_entry`: `entry_id`, `action_ref`, `consent_state_at_action`, `human_signature`, `timestamp`, `agent_recommendation_ref`

### AI Compliance layer

- `asset_id`
- `asset_type` ∈ `photo | audio | video | transcript | press_release | recap_draft | social_caption | partner_deck`
- `draft_content_pointer` (never the raw protected content)
- `identifiable_subjects[]`
- `current_consent_state_snapshot` (read-only projection from Real-time Consent Bus)
- `cultural_calibration_profile_ref`
- `agent_strictness` ∈ `loose | standard | strict` (set by convening organization; affects threshold only, never identification rules)

## Outputs

- A Kantara-format Consent Receipt per participant per event.
- A Consent State Change Event per modification, published to the Real-time Consent Bus.
- A per-use revocation record when a participant revokes a specific past use.
- A signed Cultural Calibration Profile per event.
- An Asset Pipeline Entry per asset, with terminal status set only by human signature.
- A Compliance Review per asset reviewed, with `severity` ∈ `pass | concern | blocking`, `findings[]`, `redline_proposals[]`, `requires_re_consent_from[]`.
- An Audit Trail Entry per published asset and per facilitated connection.
- An AI Use Receipt per AI call, with `fields_accessed[]`, `fields_excluded[]`, `output_summary`, `reviewer_id`, `review_approved`, `zero_retention_confirmed`.
- A consent history export package on participant demand.

## Acceptance Criteria

- Default state for every consent dimension is the most restrictive level; participants actively grant rather than refuse, and a participant who does nothing remains maximally protected.
- Each consent dimension is set, modified, and revoked independently of every other dimension; no bundling control exists across data layer or across attention layer or between the two layers.
- Revocation is a single-step action; propagation completes within 24 hours to all subscribed downstream subscribers including any sponsor CRM integration, and the audit trail records the propagation lag.
- Deployment of the organizer dashboard fails closed if the Cultural Calibration Profile is incomplete; the operator cannot fill missing fields, and the profile carries an explicit `authorized_by` signature from the convening organization.
- Every published asset and every facilitated connection carries a human signature distinct from the agent recommendation; bulk-approval of more than 20 items in fewer than 5 minutes is flagged for review.
- Every AI call produces a non-disable-able AI Use Receipt; protected, nation_specific, and `do_not_compute` fields never enter the AI prompt; the agent model version is pinned per event and any mid-event change requires re-validation.
- Refusal at any layer (participant declining a dimension, organizer holding an asset, agent flagging a violation, convening organization pausing the pilot mid-event) is recorded as a first-class state, never displayed as missing data, pending action, or quality issue.

## Refusal Boundaries

- **Do not treat any record produced by this infrastructure** — Consent Receipt, Compliance Review, Audit Trail Entry, AI Use Receipt, or Cultural Calibration Profile — **as legal indemnity, GDPR certification, ESG attestation, DEI achievement, cultural authority, or community legitimacy.** Every record describes what happened; none certifies what should happen or whether it was appropriate.
- **Do not surface aggregate, distributional, demographic, or segmented views of consent state to any actor**, and do not let protected, nation_specific, or `do_not_compute` fields enter any AI prompt, external surface, or aggregation. Counts may only attach to specific pending actions; cross-record statistics on consent are unsupported by design.
- **Do not allow AI agents, system automation, operator action, or any non-participant party to decide cultural authority, consent, or protocol appropriateness on behalf of the sovereign party.** Do not allow auto-import of consent without active grant. Do not allow bulk-approval without per-item human signature. Do not allow mid-event vendor or model change without re-validation and re-signing.
- **Do not extend records, agents, or infrastructure into external regulated systems** — HR personnel files, ESG disclosures, GDPR compliance reports, insurance underwriting, tax compliance, sponsor / partner CRM bypass, or marketing collateral outside the event's authorized assets — without a separately reviewed spec. This infrastructure governs event-time consent only.

## First Build Step

Create a fictional fixture bundle containing: one signed Cultural Calibration Profile; three participant Consent Receipts (one fully restrictive default, one partial-grant with a mid-event dimension-level revocation, one broad-grant with a per-specific-use refusal post-event); three Asset Pipeline Entries (one clear publication, one held-for-rewrite due to a partially-consented quote, one post-publication withdrawal triggered by per-use revocation); three Compliance Reviews matching the entries; three AI Use Receipts; three Audit Trail Entries including one with documented propagation lag. Place under `examples/spec-experiments/consent-layers-bundle/` and run `python3 scripts/composition_engine.py examples/spec-experiments/consent-layers-bundle --write` to verify the disposition is `composes_with_review` or better.

## Source Notes

Synthesized from the kit primitives `indigenomics-ai-participant-gateway.md` (gateway / agreement / visibility defaults), `witness-record-interop-profile.md` (state_history pattern, refusal as first-class state), `private-learning-ledger.md` (withdrawal propagation, `do_not_compute` flag), `untracked-allocation-ledger.md` (multi-dimensional independent visibility), `claims-evidence-coherence-report.md` (review-before-publish, severity model), `receipt-wall-story-gallery.md` and `templates/display-review-checklist.md` (display gate), `templates/witness-rollup.md` (audit trail shape), `templates/spec-fragment.md` Plain-Language Permission Picker (visual sliders, default-restrictive convention), `indigenomics-ai-graph-chat-witness-sidecar.md` (AI Use Receipt model), and the Kantara Initiative Consent Receipt Specification (portable receipt format).
