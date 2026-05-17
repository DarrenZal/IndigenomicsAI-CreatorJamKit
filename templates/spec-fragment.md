---
type: template
status: v0-manual-first
created: 2026-05-16
author: Darren Zal
drafting_partner: AI coding partner
composes_with:
  - jam-spec-composition-report-v0.md
  - jam-witness-ceremony-v0.md
  - witnessing-receipt-schema-v0.2.md
---

# Spec Fragment Wrapper - v0

**Use this during the Creator Jam when a participant, team, or operator wants to bring any contribution into the Offering Integration Session.**

This is intentionally lightweight. It does not force every contribution into one format. A vision doc, spec, code module, prompt, prototype, refusal log, acceptance criteria list, prior receipt, or shared repo can all be wrapped as a fragment.

The wrapper answers one question: **can this contribution safely and usefully fit into a candidate bundle, and if not, how should it be preserved?**

## Facilitator Instructions

1. Start with the participant's native artifact. Do not rewrite it first.
2. Ask participants to answer the quick card first.
3. If a field needs authority, consent, or steward review, mark it that way. Do not guess.
4. Protected, Nation-specific, ceremonial, linguistic, participant-private, or otherwise authority-bound material should not be sent into AI for "checking." Record that review is required.
5. If the fragment does not fit any bundle, preserve it with a reason. Non-fit is a valid Jam output.
6. Facilitators and operators fill the fit, review, bundle, receipt, and handoff fields. Participants do not need to complete the full YAML.

## Participant Quick Card

Participants only need to answer:

- What are you offering?
- What do you hope it helps with?
- What should it not be used for?
- Is anything private, protected, or review-required?
- Who should be credited or asked before it is used?

Facilitators/operators fill the remaining fit, review, bundle, receipt, and handoff fields.

## Plain-Language Permission Picker

Use this before filling the detailed permission fields:

| Choice | Meaning | AI Use |
|---|---|---|
| `public` | This can be shared publicly for the stated use. | Allowed if no other review is needed. |
| `group_only` | This can be shared only with the named group or session. | Only if the group has agreed. |
| `private` | This is for the contributor or named holders only. | Not allowed. |
| `review_required` | Someone with authority needs to review before use. | Not allowed until review clears the stated use. |
| `do_not_use` | This should be preserved but not used. | Not allowed. |

If unsure, choose `review_required`.

## Quick Fill Version

```yaml
fragment_id: frag:<short-slug>
title:
contribution_type: vision | spec | spec_dag | acceptance_criteria | refusal_log | source_record | permission_record | code | prototype | prompt | receipt | shared_doc | other
contributor_names:
artifact_ref: # path, URL, repo, doc title, receipt id, or "in-room note"
purpose:
desired_use:
  - include_in_bundle
  - inspire_bundle
  - review_only
  - preserve_for_later
  - do_not_use_without_review

inputs:
  - # what this fragment needs in order to be useful
outputs:
  - # what this fragment offers or produces
dependencies:
  - # other fragments, docs, people, tools, data, or approvals needed

permissions:
  transparency_tier: T1 | T2 | T3 | T4 | unknown
  sovereignty_class: public | community | nation_specific | private | unknown
  authorization_basis:
  license_or_ip:
  fpic_status: obtained | pending | not_applicable | withheld | unknown
  care_ocap_tk_notes:

refusal_boundaries:
  - # what this fragment must not be used for

acceptance_criteria:
  - id: AC1
    statement:
    verification_method: manual_review | command_exit_zero | text_check | schema_check | demo_observation | not_yet_defined

source_lineage:
  - # sources, contributors, prior work, prior receipts

code_or_prototype:
  ref:
  runnable_status: runs_now | needs_setup | demo_only | unknown | not_applicable
  required_environment:

authority_or_steward_review:
  state: not_required | requested | pending | approved | refused | outside_authority | unknown
  routed_to:
  reason:

composition_status: # facilitator/operator field; participant-facing label: fit state
  state: candidate | included | excluded | forked | merged | protected | withdrawn | tombstoned | unresolved
  bundle_ids:
  notes:

receipt_links:
  - # prior or newly emitted witnessing receipts
```

## Plain Language Prompts

Use these when filling the wrapper with participants:

- What did you bring?
- What do you hope it contributes?
- What should it not be used for?
- Who else or what else does it depend on?
- What would make it successful?
- Is anything in it private, protected, or authority-bound?
- Does anyone need to review this before it can be used?
- Should it be included now, held for later, or kept separate?

## Review States

| State | Meaning |
|---|---|
| `not_required` | No special review needed for the stated use. |
| `requested` | Someone has asked for review, but it has not started. |
| `pending` | Review is underway or waiting on a named person/role. |
| `approved` | Review cleared this fragment for the stated use only. |
| `refused` | Review found this use should not proceed. |
| `outside_authority` | This Jam does not have standing to decide. Preserve and do not use. |
| `unknown` | The facilitator does not know yet. Treat as not cleared. |

## Fit States

| State | Meaning |
|---|---|
| `candidate` | Fragment may fit one or more bundles. |
| `included` | Fragment is included in a named candidate bundle. |
| `excluded` | Fragment is left out with a reason. |
| `forked` | Fragment starts or moves to a separate bundle. |
| `merged` | Fragment has been combined with another compatible fragment. |
| `protected` | Fragment is preserved but not processed, shown, or sent to AI. |
| `withdrawn` | Contributor withdrew the fragment or permission. |
| `tombstoned` | A prior use is now stale because source permission changed. |
| `unresolved` | Fit is not settled by the end of the clinic. |

## Minimal Receipt Guidance

For v0, do not block the workshop on perfect receipt automation.

At minimum, record:

- fragment id
- contributor name or chosen display name
- artifact reference
- fit state
- permission summary
- review state
- linked bundle id, if included

If the receipt generator is available, emit a receipt. If not, the composition report can serve as the manual receipt source and be converted later.

## Safety Boundary

The wrapper can record that authority or steward review is required. It cannot compute legitimacy.

Do not paste protected cultural, ceremonial, linguistic, Nation-specific, participant-private, or otherwise restricted content into an AI system for evaluation. The correct v0 action is:

```yaml
authority_or_steward_review:
  state: pending
  routed_to: <named person or role>
  reason: "Review required before use."
composition_status:
  state: protected
  notes: "Not sent to AI. Preserved for human/steward decision."
```
