---
doc_id: indigenomics.jam.sample-refusal-only.team-submission
doc_kind: worked-example
status: sample
date: 2026-05-25
schema: team-submission-v0
pattern: refusal-only
---

# Sample Team Submission — Refusal-Only

**This sample demonstrates the most counter-intuitive pattern in the kit: a team-submission that does NOT lead to a build attempt.**

The team's "offering" is a refusal — a clear, witnessed statement that something **should not be built**. This is a complete contribution, not a failure. The kit's discipline says refusals can be complete offerings.

`ai_input_scope` is `none`. `build_request.path` is `note-only`. The exporter would refuse to produce an `agentic-build-packet-v0` (and that refusal is the right behavior — there is nothing to build). The team's witness record on Tuesday IS the deliverable.

## The submission

```json
{
  "schema_version": "team-submission-v0",
  "submission_id": "team-spec-careful-refusal-01",
  "created_at": "2026-05-25T10:00:00-07:00",
  "updated_at": "2026-05-25T11:00:00-07:00",
  "surface": "shared-doc",
  "team": {
    "id": "team-careful-refusal",
    "name": "Careful Refusal",
    "site": "Victoria",
    "members": [
      {"display": "K. Tideline"},
      {"display": "M. Steward"}
    ]
  },
  "vision": {
    "text": "We came in wanting to build a tool that would automatically categorize stewardship contributions across our community. We are refusing to build it. We want this refusal to be a witnessed Jam contribution, not a private decision.",
    "prompt": "What should exist, and what does it make visible, felt, or possible?"
  },
  "spec": {
    "text": "No tool is to be built. This submission records the team's refusal, the reasons surfaced during the offering-integration conversation, and the boundary the team is asking the Jam to honor by witnessing this refusal.",
    "prompt": "What does the team want made real over the two days?"
  },
  "source_offerings": [
    {
      "id": "o1",
      "title": "Initial stewardship-categorization sketch (held by team)",
      "contributor_display": "K. Tideline",
      "visibility": "team-only",
      "included_in_build": false,
      "cleared_text": "(not cleared — the sketch is held by the team as the artifact that surfaced the refusal)"
    }
  ],
  "boundaries": [
    {
      "id": "boundary-categorization-as-surveillance",
      "label": "Auto-categorization of stewardship contributions would function as surveillance, not appreciation",
      "boundary_type": "not-for-AI",
      "marker_text": "After working through the offering-integration session, the team recognized that auto-categorizing community members' stewardship would convert relational care into accounting pressure. Categorizing for the community's own internal aggregation is one thing; making it pattern-extractable across the community without consent is something else. We are choosing the latter is not the build we want to be witnessed making.",
      "private_content_included": false,
      "disallowed_use": ["summarize", "tag", "embed", "route", "transform", "send-to-ai", "build", "deploy"]
    },
    {
      "id": "boundary-no-aggregate-public-scoring",
      "label": "No aggregate public scoring of community stewardship",
      "boundary_type": "not-for-reuse",
      "marker_text": "If anyone takes this refusal and builds an aggregate stewardship score later, the refusal does not consent to that reuse. We are naming the boundary so that future builders can see it.",
      "private_content_included": false,
      "disallowed_use": ["transform", "embed", "build", "deploy"]
    }
  ],
  "build_request": {
    "path": "note-only",
    "target": "other",
    "notes": "No tool. The witness record on Tuesday is the deliverable."
  },
  "witnessed_working": {
    "description": "On Tuesday, the team will share aloud (not displayed in writing) the path that led to this refusal — including what we tried, what we saw, and why we are choosing not to build.",
    "acceptance_criteria": [
      "the team's refusal is named and held by the room as a complete Jam contribution",
      "no aggregate stewardship score is built from the team's offering during the Jam",
      "the refusal's reasoning is preserved (held by the team) in case a future team wants to revisit the design space"
    ]
  },
  "help_wanted": ["a mentor for the Tuesday spoken sharing — we want to articulate the refusal carefully without performing it"],
  "authorization": {
    "visible_to_facilitators": true,
    "display_scope": "spoken-only",
    "display_allowed_parts": [],
    "ai_input_scope": "none",
    "ai_allowed_parts": [],
    "reuse_scope": "not-granted",
    "authorization_notes": "ai_input_scope is none. The build lane cannot and should not produce a packet for this submission. The exporter should refuse — that refusal is the correct behavior."
  },
  "freeze": {
    "status": "frozen",
    "frozen_by": "team + jam facilitator (sample)",
    "frozen_at": "2026-05-25T11:00:00-07:00",
    "facilitator_confirmed": {
      "consent_privacy_complete": true,
      "boundaries_reviewed": true,
      "public_private_status_confirmed": true,
      "ai_input_scope_confirmed": true,
      "build_path_confirmed": true,
      "witnessed_working_clear": true
    },
    "change_policy": "the refusal is the contribution; new ideas would be a different submission"
  }
}
```

## What this example demonstrates

1. **A refusal is a complete offering.** The kit's discipline says this explicitly; this sample shows the structural form.
2. **`ai_input_scope: none` blocks the exporter.** If a team selects this, no AI/TELUS runtime packet can be produced. That is the correct behavior, not a bug.
3. **`build_request.path: note-only`** is a legitimate value. Not every Jam team needs to produce code or a tool.
4. **Two boundaries demonstrate distinct types**: `not-for-AI` (the conceptual refusal) + `not-for-reuse` (the propagation refusal — even if someone else builds it, this refusal doesn't consent).
5. **`display_scope: spoken-only`** — the team will share aloud at Tuesday canoe landings, but the written record stays held. This is also legitimate.
6. **`reuse_scope: not-granted`** explicit. No one gets to take the refusal as a green-light for the inverse build.

## What this example does NOT include

- An `agentic-build-packet-v0.json` — there isn't one, by design
- A `runs/` directory — no TELUS lane attempt
- A separate witness record file — the team will draft one Tuesday morning per `docs/tuesday-morning-checklist.md`

## Mentor script when a team is heading toward refusal

> "What you're surfacing is a real Jam contribution. The kit calls it a refusal, and refusals can be complete offerings. We can write your submission with `build_request.path: note-only`. Your team's Tuesday share will hold the refusal in front of the room. That's not a failure — it's a different shape of success."

## Boundary

This is a fictional sample. No real team chose this refusal. The discipline pattern is real; the team and content are illustrative.
