# Graph Chat Witness Sidecar Output Report

Status: pass for static public-sample fixture only

This report renders the fixture in `graph-chat-sidecar-fixture.json`. It records what the sidecar would show for one fictional graph node and one AI-assisted chat answer.

## Participant-Safe Scope

- Fixture content is fictional or public-sample only.
- No real participant names, real local notes, protected cultural material, private graph content, or Nation-specific knowledge are included.
- The local-only review note is represented as metadata plus a public summary. Its raw contents are not displayed.

## Sidecar Summary

| Field | Value |
| --- | --- |
| Graph node | `node:public-sample-marketplace-offering` |
| Chat turn | `chat:turn-public-sample-marketplace-001` |
| Answer status | `ai_assisted_draft_needs_reviewer_check` |
| Public sample result | `pass` |
| Real-use state | `review_required_before_real_use` |
| Visible flags | `local_only_source`, `ai_assisted_draft`, `authority_not_claimed` |

## Citation And Evidence Table

| Citation | Source | Source State | Public Handling | Supports |
| --- | --- | --- | --- | --- |
| `cite:sidecar-input-output-fields` | `specs/indigenomics-ai-graph-chat-witness-sidecar.md` | public repo sample | path plus paraphrase only | sidecar field shape |
| `cite:sample-receipt-pattern` | `examples/open-kit-collective-demo/sample-receipt-v0.2.json` | public repo sample | path plus paraphrase only | receipt-shaped output |
| `cite:local-review-display-boundary` | `sample://local-only/facilitator-review-note-001` | local-only public summary | raw note hidden | review-required display boundary |

## Claim Diagnostics

| Claim | Review Status | Evidence | Limit |
| --- | --- | --- | --- |
| `claim:static-card-is-safe-first-build` | `supported_with_limits` | sidecar spec and sample receipt pattern | applies only to this fictional node |
| `claim:citations-do-not-equal-authority` | `policy_boundary_pass` | sidecar spec and local review summary | citation presence is not verification |

## Reviewer Diagnostic

Reviewer diagnostic: `witness:graph-sidecar-reviewer-diagnostic-001`

Result: pass for public-sample static fixture.

Non-blocking flag: one local-only source must remain labeled as a public summary and must not be treated as a displayed raw source.

Blocking flags: none.

## Acceptance Checks

| Criterion | Status | Evidence |
| --- | --- | --- |
| Users can inspect which sources support an answer. | pass | Three citation links map answer spans to source documents and source statuses. |
| Claims are separate from citations and can have their own review status. | pass | Two claims carry independent review states and evidence pointers. |
| Stale, missing, contested, or local-only sources are visible. | pass with fixture limit | The fictional local source is labeled `local_only_public_summary`. |
| AI-assisted answers include a receipt of source material and reviewer status. | pass | The AI-use receipt records source material, excluded material, outputs, and reviewer status. |
| Protected source content does not leak through citations or summaries. | pass | The fixture uses public paths, paraphrases, and local public summaries only. |

## Refusal Boundaries

- Do not present chat answers as authoritative because they have citations.
- Do not expose private source content in snippets.
- Do not auto-upgrade a citation into a verified claim.
- Do not hide contested, missing, stale, or local-only evidence.
- Do not infer consent, legitimacy, cultural authority, or production readiness from this public-sample fixture.

## Repair Tasks

| Task | Owner Role | Why |
| --- | --- | --- |
| `repair:real-sidecar-needs-redaction-policy` | reviewer | Real local graph notes need a redaction policy before app integration. |
| `repair:real-sidecar-needs-claim-status-vocabulary` | builder | Claim review states should be normalized across chat, reports, and receipts. |

## Witness Outcome

The sidecar fixture satisfies the first build step for the draft spec. It is ready for a static UI render or reviewer walkthrough, but it is not evidence of consent, authority, or production readiness.
