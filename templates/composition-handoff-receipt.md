---
doc_id: indigenomics.jam.composition-handoff-receipt
doc_kind: template
status: v0
date: 2026-05-25
author: Darren Zal
depends_on:
  - templates/team-submission-v0.md
  - tools/composition-merger.py
  - templates/stigmergic-offering-board.md
  - docs/witnessing-receipts.md
target_jam: 2026-05-25
---

# Composition Handoff Receipt

When Team A's output becomes Team B's input, this receipt preserves the
context that travels with the handoff: original permission state, new use
intent, what the source team did NOT approve for, witness signature, and
rollback path.

**A handoff is not new consent.** It is preservation of the source team's
context as the offering moves into the receiving team's build. If the
receiving team wants to use the offering for a purpose the source team did
not approve, that is a re-ask, not a re-interpretation.

---

## When to use this

- Team A's offering moves into Team B's build (composed or borrowed).
- One team takes another team's artifact as an input.
- A composed bundle goes forward and both source teams need a durable
  record of the handoff.

If two teams are *composing* (running `tools/composition-merger.py` and
re-freezing a bundle), the receipt is created once for the composition.
If Team B is *borrowing* a single offering from Team A's larger
submission, the receipt is created for that one handoff.

If Team A is sharing an offering for general use via the
`stigmergic-offering-board.md` (no specific receiving team), this template
is not needed yet — it's needed when a specific Team B picks it up.

---

## Schema

```yaml
receipt_version: composition-handoff-v0
receipt_id: string                       # unique handoff id, e.g. handoff-eelgrass-to-kelp-01
created_at: datetime
sprint_context: optional string          # e.g. "tuesday-composition-sprint, pair 3 of 5"

source_team:
  id: string
  name: string
  team_submission_id: string             # the submission_id this offering comes from

receiving_team:
  id: string
  name: string
  team_submission_id: string             # the submission_id this offering is moving into

offering:
  offering_id: string                    # the source_offerings[].id from source team-submission-v0
  title: string
  cleared_text_used: boolean             # true if cleared_text moves; false if marker-only
  notes: optional string

source_permission_state_unchanged:
  # Snapshot from source team-submission-v0.authorization
  # This handoff DOES NOT modify these values; it preserves them as context.
  display_scope: whole | partial | spoken-only | none
  ai_input_scope: whole | partial | none
  reuse_scope: not-granted | ask-first | team-only | public-ok
  authorization_notes: optional string

receiving_team_new_use_intent:
  # What the receiving team intends to do with this offering — may differ from
  # source team's original intent, but must NOT exceed source permission state.
  use_description: string
  ai_input_planned: boolean
  display_planned: boolean
  exceeds_source_permission: false       # MUST be false; if true, this is a re-ask, not a handoff

what_source_did_not_approve_for:
  # Boundary markers travel with the handoff. Restate any
  # source-team-named restrictions so they are visible in the receiving
  # team's build context.
  - boundary_id: string                  # source team-submission-v0.boundaries[].id
    boundary_type: marker-only | not-for-AI | not-for-reuse | private | protected
    marker_text: string
    applies_to_this_handoff: boolean

source_team_witness_signature:
  signatory_display: string              # who from source team signed
  signed_at: datetime
  confirmation_statement: |
    "I confirm that this handoff carries our offering's original permission
    state. We have not granted new consent; we have preserved the context.
    If the receiving team's use intent changes, they must re-ask."

rollback_path:
  # If source team later withdraws the underlying offering (via
  # tools/withdrawal-propagation.py or by editing their team-submission-v0),
  # what happens to this handoff?
  on_source_withdrawal: dissolve | freeze-as-historical | review-required
  on_source_withdrawal_description: string
  receiving_team_notified_via: string    # how the receiving team finds out
  propagation_tool: optional string      # e.g. "tools/withdrawal-propagation.py --handoff <receipt_id>"

boundary_statement: |
  This handoff is not new consent. It is preservation of source-team context
  as the offering moves into the receiving team's build. The source team's
  authorization state governs what may happen with this offering; this
  receipt makes that state visible to the receiving team and to any witness.
```

---

## Worked example — Eelgrass Observers handing off to Kelp Monitors

**Setup.** Eelgrass Observers (Team A) built a per-site rollup tool for
canopy observations. Kelp Monitors (Team B) realized in the Tuesday
Composition Sprint that they want to feed their kelp-blade observation log
through the same rollup. They are not fully composing — Team B just wants to
use Team A's tool, with Team A's permission, as an input to Team B's own
build.

```yaml
receipt_version: composition-handoff-v0
receipt_id: handoff-eelgrass-to-kelp-01
created_at: 2026-05-26T10:15:00-07:00
sprint_context: "tuesday-composition-sprint, pair 1 of 3"

source_team:
  id: team-eelgrass-observers
  name: Eelgrass Observers
  team_submission_id: team-spec-eelgrass-observers-01

receiving_team:
  id: team-kelp-monitors
  name: Kelp Monitors
  team_submission_id: team-spec-kelp-monitors-01

offering:
  offering_id: o1
  title: "Per-site rollup script (single-file Python; prints site-grouped means + date range)"
  cleared_text_used: true
  notes: |
    Receiving team will run the script against their Lighthouse Park
    blade-length log, not against the source team's Boundary Bay data.
    The tool moves; the source data does not.

source_permission_state_unchanged:
  display_scope: whole
  ai_input_scope: whole
  reuse_scope: ask-first
  authorization_notes: "Source team asks to be credited as 'Eelgrass Observers' on any output."

receiving_team_new_use_intent:
  use_description: |
    Run the rollup script against Kelp Monitors' own Lighthouse Park
    blade-length observation log. Output goes into Kelp Monitors' Tuesday
    canoe-landing readout. Source team will be credited in the readout.
  ai_input_planned: false
  display_planned: true
  exceeds_source_permission: false

what_source_did_not_approve_for:
  - boundary_id: b1
    boundary_type: not-for-AI
    marker_text: "Observer contact details from Boundary Bay roster are not for AI input."
    applies_to_this_handoff: false   # boundary applies to source data, not to the rollup tool itself
  - boundary_id: b2
    boundary_type: not-for-reuse
    marker_text: "Tool is for Jam build attempts; not approved for production deployment."
    applies_to_this_handoff: true    # receiving team must honor this — no post-Jam productization

source_team_witness_signature:
  signatory_display: S. Eelgrass
  signed_at: 2026-05-26T10:14:00-07:00
  confirmation_statement: |
    "I confirm that this handoff carries our offering's original permission
    state. We have not granted new consent; we have preserved the context.
    If the receiving team's use intent changes, they must re-ask."

rollback_path:
  on_source_withdrawal: dissolve
  on_source_withdrawal_description: |
    If Eelgrass Observers later withdraws the rollup-script offering, Kelp
    Monitors agrees to stop using the script in their build and to mark
    any built artifact as "input-withdrawn" in the witness record. The
    receiving team's own work (the blade-length log, the readout) is
    preserved; only the borrowed component dissolves.
  receiving_team_notified_via: "Jam Telegram + mentor in-person"
  propagation_tool: "tools/withdrawal-propagation.py --handoff handoff-eelgrass-to-kelp-01"

boundary_statement: |
  This handoff is not new consent. It is preservation of Eelgrass Observers'
  context as the rollup script moves into Kelp Monitors' build. The source
  team's authorization state governs what may happen with this offering;
  this receipt makes that state visible to the receiving team and to the
  Tuesday witness record. Boundary b2 (not-for-reuse beyond the Jam) travels
  with the handoff and applies to Kelp Monitors' use.
```

---

## How this fits with other kit pieces

| Piece | Relationship |
|---|---|
| `templates/team-submission-v0.md` | Source of `authorization`, `boundaries`, and `source_offerings[]` referenced here |
| `tools/composition-merger.py` | Produces the candidate bundle; this receipt is created at the moment a bundle is re-frozen for build OR a single offering is handed off |
| `templates/stigmergic-offering-board.md` | The board surfaces offerings; this receipt is the structured record once a specific receiving team picks one up |
| `workshop/tuesday-composition-sprint-v0.md` | Phase 5 of the sprint creates this receipt for "build composed" outcomes |
| `tools/withdrawal-propagation.py` | Reads the `rollback_path` field if source team later withdraws |
| `docs/witnessing-receipts.md` | This handoff receipt is a kind of receipt — included in the Tuesday witness record |

---

## What this receipt does NOT do

- It does not grant new consent. The receiving team's use intent must stay
  within the source team's `authorization` scopes.
- It does not transform the source offering. Cleared text is cleared text;
  boundaries are boundaries; the merger does not relax either.
- It does not survive a source-team withdrawal silently. The
  `rollback_path` is load-bearing.
- It does not certify the receiving team's build, the source team's
  offering, or the composition itself. It is a record of context, not a
  grant of authority.

---

## Mentor script when creating this receipt

> "We're going to write a short receipt that captures the context of this
> handoff. The receipt does three things: it names what is moving from one
> team to the other, it carries the source team's permission state into the
> new context, and it names what happens if the source team later changes
> their mind. The handoff is not new consent — it's preservation. If the
> receiving team's intent later changes in a way that exceeds the source
> team's permission, that's a re-ask, not a re-interpretation."

---

## Boundary

This receipt is a structured preservation of context as an offering moves
between teams. It is not approval, certification, authority, or reuse
permission. It does not modify the source team's `team-submission-v0`. It
does not certify the receiving team's build. A signed handoff receipt does
not establish that the composition will succeed, that the build will work,
or that the offering will be witnessed favorably. The source team retains
the right to withdraw, and the `rollback_path` governs what happens to the
handoff in that case.
