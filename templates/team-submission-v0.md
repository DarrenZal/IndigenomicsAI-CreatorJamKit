---
doc_id: indigenomics.jam.team-submission-v0
doc_kind: spec
status: draft
date: 2026-05-20
author: Darren Zal
depends_on:
  - docs/jam/agentic-build-packet-v0.md
  - docs/operations/2026-05-20-gateway-build-packet-contract.md
  - docs/jam/operational-kit/team-vision-spec-submission-template.md
target_jam: 2026-05-25
---

# Team Submission v0

> **First time here?** This is the schema reference (~340 lines, dense). Don't read it cold — open `examples/sample-submission-pair/sample-team-submission-v0.md` for a filled-in worked example first, then come back to this doc when you need detail on a specific field.

## Boundary vocabulary (used throughout the schema)

These terms appear in `boundaries[].boundary_type` and `authorization.*_scope`. See `docs/MENTOR_FIELD_GUIDE.md` §2 for the full table with mentor scripts.

- **`marker-only`** — content is held by team; only the boundary's existence is recorded (use for cultural/ceremonial/Nation-specific material)
- **`not-for-AI`** — can be discussed/shared/displayed, but never sent to a compute engine (use for sensitive locations, observer identities)
- **`not-for-reuse`** — useful for the Jam, but do not build products with it (use for experimental protocols, one-time prompts)
- **`private`** — only for the contributor or named stewards (use for personal notes, private commitments)
- **`protected`** — requires explicit authority to use; do not disclose the content to ask permission (use for cultural, treaty-bound, credential-bound material)

Scope values for `authorization`:

- **`display_scope`**: `whole` / `partial` / `spoken-only` / `none`
- **`ai_input_scope`**: `whole` / `partial` / `none`
- **`reuse_scope`**: `not-granted` / `ask-first` / `team-only` / `public-ok`

You don't have to disclose protected material to record a boundary. The exporter strips boundary content before any model attempt runs.

## Purpose

`team-submission-v0` is the rich gateway or fallback form record for a Creator
Jam team vision/spec. It captures the team's words, offerings, boundaries,
build path, consent/privacy choices, and facilitator freeze confirmation.

It is not the executable runtime packet. After human/facilitator freeze, an
operator or gateway exporter transforms `team-submission-v0` into
`agentic-build-packet-v0`, which is the lean packet consumed by the TELUS build
lane.

The intended spine is:

```text
Gateway / fallback form
-> team-submission-v0
-> facilitator freeze
-> agentic-build-packet-v0
-> TELUS build attempt
-> reviewer findings
-> canoe landing / witness record
```

## 1. Field Schema

```yaml
schema_version: team-submission-v0
submission_id: string
created_at: datetime
updated_at: datetime
surface: gateway | notion | shared-doc | github-form | operator

team:
  id: string
  name: string
  site: Vancouver | Victoria | other
  members:
    - display: string
      participant_id: optional string

vision:
  text: string
  prompt: "What should exist, and what does it make visible, felt, or possible?"

spec:
  text: string
  prompt: "What does the team want made real over the two days?"

source_offerings:
  - id: string
    title: string
    contributor_display: optional string
    visibility: public | team-only
    included_in_build: boolean
    cleared_text: string
    note: optional string

boundaries:
  - id: string
    label: string
    boundary_type: marker-only | not-for-AI | not-for-reuse | private | protected
    marker_text: string
    private_content_included: false
    disallowed_use:
      - summarize
      - tag
      - embed
      - route
      - transform
      - send-to-ai

build_request:
  path: hand | own-ai | telus-lane | mixed
  target: single-file-cli | static-html-js | note-only | other
  notes: optional string

witnessed_working:
  description: string
  acceptance_criteria:
    - string

help_wanted:
  - string

authorization:
  visible_to_facilitators: boolean
  display_scope: whole | partial | spoken-only | none
  display_allowed_parts:
    - string
  ai_input_scope: whole | partial | none
  ai_allowed_parts:
    - string
  reuse_scope: not-granted | ask-first | team-only | public-ok
  authorization_notes: optional string

freeze:
  status: draft | frozen | needs-review
  frozen_by: optional string
  frozen_at: optional datetime
  facilitator_confirmed:
    consent_privacy_complete: boolean
    boundaries_reviewed: boolean
    public_private_status_confirmed: boolean
    ai_input_scope_confirmed: boolean
    build_path_confirmed: boolean
    witnessed_working_clear: boolean
  change_policy: "new ideas require re-freeze"
```

## 2. Transformation Boundary

`team-submission-v0` becomes `agentic-build-packet-v0` only after:

- The team has reviewed the vision/spec and intended build path.
- A facilitator has checked consent, privacy, and boundary fields.
- The freeze status is `frozen`.
- The AI/TELUS input scope is explicit.
- No marker-only, private, or protected content is copied into runtime inputs.

If consent is incomplete, boundary status is unclear, or a team member disputes
inclusion, the submission remains `needs-review` and does not export to the
TELUS build lane.

## 3. Mapping Summary

This note does not redefine `agentic-build-packet-v0`. The runtime target is
defined in `docs/jam/agentic-build-packet-v0.md`.

For M2.6, the exporter applies this mapping:

| `team-submission-v0` source | Runtime target | Rule |
|---|---|---|
| `team`, `vision`, `spec`, `build_request` | `team_spec` | Preserve the team's wording where possible. |
| `source_offerings` with `included_in_build: true` and `cleared_text` | `allowed_inputs` | Only cleared text can move into runtime inputs. |
| `boundaries` where `boundary_type` is marker-only, private, protected, not-for-AI, or not-for-reuse | `excluded_inputs` | Marker records only. Do not copy hidden content. |
| `authorization.ai_input_scope` | AI/TELUS export gate | `none` blocks AI/TELUS export; `partial` exports only named cleared parts. |
| `freeze` | `freeze_record` | Build lane runs only when facilitator freeze is confirmed. |
| `witnessed_working.acceptance_criteria` | `acceptance_criteria` | Convert plain-language criteria into reviewable checks. |

## 4. Facilitator Freeze Checklist

Before a submission can be frozen:

- Team has reviewed the final vision/spec text.
- Team has confirmed which offerings are included in the build attempt.
- Included offerings have cleared text.
- Private, protected, marker-only, not-for-AI, and not-for-reuse records are
  named only as boundaries.
- Tuesday sharing scope is explicit.
- AI/TELUS input scope is explicit.
- Build path is confirmed.
- "Witnessed working" is understandable to a reviewer.
- Any disagreement or unclear consent is marked `needs-review`, not frozen.

Facilitator confirmation statement:

> This submission is frozen for a build attempt. It is not approval,
> certification, authority, or reuse permission. New ideas require re-freeze
> before they enter the build lane.

## 5. Participant Freeze Copy

Use this copy in the gateway or fallback form.

**Freeze spec for build attempt**

Freezing means your team is choosing this version of your vision/spec as the
one a build attempt can work from.

It does not mean the idea is finished. It does not mean the Jam has approved
it. It does not give anyone reuse permission. It simply gives the builders or
AI lane a clear, bounded version to attempt.

New ideas are welcome after freeze, but they need a re-freeze before they enter
the build lane.

## 6. Fallback Form Layout

The fallback surface can be Notion, a shared doc, or a GitHub form. It should
use the same fields as the gateway so the operator can export
`team-submission-v0` without translation.

### Team

- Team name
- Site
- Team members or aliases

### Vision

Prompt:

> What should exist, and what does it make visible, felt, or possible?

### Spec

Prompt:

> What does your team want made real over the two days? What does it do, who is
> it for, and what would a working version look like?

### Offerings This Draws On

For each included offering:

- Short title
- Contributor name or alias, if the contributor wants credit
- Cleared text that may be used for this build attempt
- Whether it is included in the build attempt

### Intended Build Path

- By hand
- Own AI tools
- TELUS build-attempt lane
- A mix

### Boundaries

For each boundary:

- Boundary label
- Boundary type: marker-only, not-for-AI, not-for-reuse, private, protected
- Marker text, if any
- Confirmation that private content is not included

### Witnessed Working

Prompt:

> What would you want a reviewer or witness to see on Tuesday to say, "Yes,
> this attempt worked enough to witness"?

### Help Wanted

- Mentor support requested
- Skills needed
- Questions for operators

### Consent And Privacy

- Visible to facilitators/mentors
- What may be shown Tuesday
- What may be sent to the AI/TELUS lane
- Reuse status
- Marker-only / not-for-AI / not-for-reuse records

### Freeze

- Draft / frozen / needs-review
- Facilitator confirmation checklist
- Confirmed by
- Confirmed at

## 7. Consent And Privacy Wording

### Visible To Facilitators / Mentors

Facilitators and mentors may read this submission so they can support your team,
help with the build path, and prepare the Tuesday witness record.

Required choice:

- Yes, facilitators and mentors may read this submission.
- No, this is not ready for facilitator/mentor review.

If the answer is no, the submission cannot be frozen for a build attempt.

### Shown Tuesday

Your team chooses what may be shown during Tuesday's canoe landing.

Choices:

- The whole submission may be shown to the cohort.
- Only selected parts may be shown.
- The written submission stays private; Tuesday sharing is spoken by the team.
- Nothing from this submission may be shown Tuesday.

Selected parts must be named before freeze.

### Sent To AI / TELUS Lane

Your team chooses what, if anything, may be sent to an AI or the TELUS
build-attempt lane.

Choices:

- The whole frozen submission may be sent.
- Only selected cleared parts may be sent.
- Nothing from this submission may be sent to AI.

If "nothing" is selected, the exporter must not create an AI/TELUS runtime
packet. The team can still build by hand, use its own tools, or keep the record
as a witnessed spec without an AI build attempt.

### Marker-Only / Not-For-AI / Not-For-Reuse

Some things can be named only as boundaries.

Marker-only means the record shows that a boundary exists, but the private
content is not included, summarized, tagged, embedded, routed, transformed, or
sent to AI.

Not-for-AI means the item must not enter any AI or TELUS build-attempt input.

Not-for-reuse means no reuse permission is granted by this submission, the
build attempt, or the witness record. Anyone who wants to reuse it must ask the
team again.

## 8. Gateway Implementation Checklist

For Shawn, the smallest useful gateway version is:

- Create or edit a team submission using `team-submission-v0` fields.
- Preserve fallback submissions with the same shape.
- Add consent/privacy choices before freeze.
- Add facilitator-only freeze action.
- Block AI/TELUS export unless `authorization.ai_input_scope` permits it.
- Export frozen submissions to `agentic-build-packet-v0`.
- Preserve marker-only/private/protected records only as excluded-input markers.

## Status

- v0 - drafted 2026-05-20 for M2.6 fallback submission to build-packet export.
