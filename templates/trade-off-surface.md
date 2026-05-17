---
doc_kind: template
status: draft
visibility: public_sample
last_updated: 2026-05-17
---

# Trade-Off Surface

Use this after a composition looks technically possible and coherent, but before treating it as a good next move.

A trade-off surface is deliberation support. It does not approve the composition, define community values, decide what is healthy, or authorize action.

## Quick Fill

```yaml
trade_off_surface_id: trade-off:<short-slug>
composition_candidate_id:
composition_candidate_path:
review_date:

reviewer:
  reviewer_id:
  reviewer_type: facilitator | human_reviewer | sample_steward | technical_reviewer | display_reviewer | other
  reviewer_role:

three_checks:
  composability:
    state: yes | yes_with_adapter | no | partial | unknown
    note:
  coherence:
    state: holds | holds_with_limits | does_not_hold | unknown
    note:
  desirability_health:
    state: promising | promising_for_fixture_only | concerning | mixed | blocked | unknown
    note:

gains:
  - what becomes possible or stronger

losses_or_costs:
  - what becomes harder, weaker, more expensive, or more exposed

fragilities:
  - what could break, drift, or become harmful if conditions change

foreclosures:
  - what this composition may close down, make unavailable, or make harder to choose later

affected_perspectives:
  - perspective:
    possible_benefit:
    possible_burden:
    missing_review_needed:

time_horizons:
  immediate:
  jam_scale:
  seasonal:
  long_horizon:

refusal_and_withdrawal:
  preserved_paths:
    - path:
  risks:
    - risk:

ai_role_if_any:
  ai_used: true | false
  useful_for:
  not_for:

decision_support_result:
  status: proceed_to_review | revise_before_review | preserve_separate | block_for_now | defer
  reason:
  next_human_decision:

not_established:
  - goodness
  - health
  - authority
  - legitimacy
  - certification
  - cultural fit
  - permission for other uses
```

## Required Checks

| ID | Check | Acceptable Result |
| --- | --- | --- |
| TO1 | The three checks stay separate. | Technical composability, coherence, and desirability/health are not collapsed into one verdict. |
| TO2 | The surface names gains and losses. | Benefits are not described without costs, burdens, or fragilities. |
| TO3 | Affected perspectives are named. | The template asks who benefits, who carries burden, and whose review is missing. |
| TO4 | Refusal and withdrawal remain live. | The composition does not turn refusal, silence, or withdrawal into a defect. |
| TO5 | Future paths are considered. | The surface names adjacent possibilities and foreclosures. |
| TO6 | AI's role is bounded. | AI may surface tradeoffs and alternatives, but does not decide desirability or authorize action. |
| TO7 | The result routes to human standing. | The next decision names a human, steward, contributor, or review body with standing. |

## Minimal Boundary Text

Use this on trade-off artifacts:

> This surface names possible gains, losses, fragilities, and foreclosures for deliberation. It is not a verdict that the composition is good, healthy, legitimate, or authorized.
