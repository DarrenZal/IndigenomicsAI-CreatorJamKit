---
doc_kind: template
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Display Review Checklist

Use this before any receipt, witness rollup, story card, gallery item, screenshot, or public readout moves from internal review into a display surface.

Display review is per exact use. It does not create consent for other uses, certify truth, establish legitimacy, judge cultural authority, or approve reuse.

## Quick Fill

```yaml
display_review_id: display-review:<short-slug>
candidate_id:
candidate_path:
review_date:

display_reviewer:
  reviewer_id:
  reviewer_type: display_reviewer
  reviewer_role:

requested_display_use:
  surface: receipt_wall | workshop_readout | repo_example | slide | website | other
  audience:
  duration:
  public_display_requested: true | false

source_state:
  visibility_tier:
  display_approval: pending | approved_for_fixture | approved_for_public_sample | returned_for_revision | blocked | withdrawn
  do_not_show_externally: true | false
  derived_from_transitions:
    - transition:
  excluded_source_records:
    - record:

decision:
  status: approved_for_display | approved_for_fixture_only | returned_for_revision | blocked_do_not_display | preserve_separate
  reason:
  required_repairs:
    - repair:

not_established:
  - authority
  - legitimacy
  - certification
  - cultural fit
  - readiness for reuse
  - permission for other uses

withdrawal_path:
  who_can_withdraw_or_correct:
  affected_surfaces:
    - surface:
  action_if_withdrawn:
```

## Required Checks

| ID | Check | Acceptable Result |
| --- | --- | --- |
| DR1 | The candidate names the exact display use and audience. | Use is explicit and bounded. |
| DR2 | The candidate has a display reviewer route. | `display_reviewer` uses role-only fixture data or an approved real reviewer for the exact use. |
| DR3 | The candidate carries display gates. | `display_approval` and `do_not_show_externally` are present and interpreted per exact use. |
| DR4 | The candidate names its speech-act transitions. | `derived_from_transitions` is present for any receipt, witness, claim, or story projection. |
| DR5 | Obstruction markers survive projection. | The display text names what it does not establish. |
| DR6 | Excluded sources remain excluded. | Private, refused, protected, or `do_not_compute` records are marker-only or absent. |
| DR7 | Evidence visibility stays separate from claim visibility. | Public claim text does not expose private or local-only evidence. |
| DR8 | Witness language is bounded. | Software or reviewer records are not described as ceremonial witnessing, Knowledge Keeper witnessing, cultural authority, or protocol authority. |
| DR9 | AI use is scoped. | Any AI-use receipt says exactly what AI touched and what it did not touch. |
| DR10 | Withdrawal can propagate. | A reviewer or steward can withdraw, correct, or narrow the display and derived summaries. |
| DR11 | Public text is narrow. | The text does not add impact, legitimacy, authority, eligibility, underwriting, certification, or reuse claims. |
| DR12 | The result is recorded. | The review records approved, fixture-only, returned, blocked, or preserve-separate status. |

## Result States

| Status | Meaning | Required Action |
| --- | --- | --- |
| `approved_for_display` | The exact display use is approved. | Create or update the display artifact with reviewer, date, source, boundaries, and withdrawal path. |
| `approved_for_fixture_only` | The candidate can be shown as a sample fixture, but not as an external story. | Keep public/external gates closed. |
| `returned_for_revision` | The candidate is close, but one or more required checks need repair. | Do not display until a new review clears the repair. |
| `blocked_do_not_display` | The candidate has a boundary conflict. | Preserve the candidate internally or remove it from display queues. |
| `preserve_separate` | The material should remain present only as a protected, private, or review-required record. | Do not project it into a story or gallery. |

## Minimal Display Boundary

Use or adapt this on display-facing artifacts:

> This display records a reviewed sample event for the stated use only. It does not establish authority, legitimacy, certification, cultural fit, readiness for reuse, or permission for other uses.
