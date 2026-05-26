# Handoff Prompt — Consent Layers Participant App Demo

You are picking up a self-contained build task. You **do not need** any conversation that produced these files. Everything you need is in this folder (`spec.md` + this prompt).

This is a **demo-grade, local-only, single-layer build**. Tech-stack decisions are yours, but you MUST record them in a `TECH_CHOICES.md` file marked "demo only" so a future deployment team can revisit them.

---

## 1. What you're building

A runnable local interactive demo of the **participant-facing surfaces** of the Consent Layers infrastructure described in the sibling file `spec.md`.

The product in one sentence: **sovereignty infrastructure for the two resources every participant brings into a public gathering — their data (face / voice / name / quoted speech / presence) and their attention (approach mode / topic scope / contact budget / quiet windows).**

The integrated spec describes three coordinated layers. **You build only the participant layer.** The other two — organizer dashboard and AI compliance reviewer — are sibling layers, out of scope for this build.

---

## 2. Inputs

| File | Required reading | Purpose |
|---|---|---|
| `./spec.md` (sibling) | **Required, all 8 sections** | The integrated jam-spec. You implement only the **Participant layer** subsection of §"Inputs" and the participant-related items in §"What Could Be Built" and §"Outputs". |

Seed data for first-run localStorage is described inline in §5 below.

---

## 3. Tech constraints

| Constraint | Value |
|---|---|
| Tech stack | Your choice, client-side only |
| Persistence | `localStorage` only (no backend, no DB) |
| Backend / API | None for this build |
| Authentication | Skip — assume a logged-in participant |
| Network calls | None except optional CDN-loaded libraries |
| Build / run | Single command (`npm run dev` or `python -m http.server` simplicity) |
| Browser | Modern evergreen, mobile-first viewport |
| Dependencies | < 5 npm packages or vanilla JS |
| Accessibility | Keyboard navigable, screen-reader labels |

---

## 4. Must implement — 5 surfaces

All described in `spec.md` §"What Could Be Built" (the participant app bullet).

### 4.1 Consent Setup Wizard
- Two layers: **data** (6 dimensions: face / voice / name / quote / presence / post_event_reference) and **attention** (4 dimensions: approach_mode / topics / daily_contact_budget / quiet_windows).
- Each data dimension has 4 levels: `no` / `anonymized` / `within_event` / `public`. **Default to `no`**.
- Each dimension has its own slider/control. **No "set all" mega-toggles.**
- Each control has a one-sentence explainer and a concrete example.
- Wizard completion → write Consent Receipt to `localStorage`.

### 4.2 My Consent Card
- Single screen showing every current setting across both layers.
- One-tap revoke per dimension.
- "Export Kantara Receipt" button that displays / downloads the receipt JSON.

### 4.3 Activity Feed
- Timeline view of every `state_change` and (mocked) every recorded use.
- Plain language: "Your face was photographed at 14:32" / "Someone tried to approach you about hiring but you weren't open to that topic today" / "You were quoted in the closing panel."
- Seed with 5-10 plausible mock entries on first run.

### 4.4 Per-item Revoke
- Distinct from dimension-level revoke. Each activity entry has its own "revoke this specific use."
- Use the `revocation_history[]` shape from `spec.md` §Inputs, with a `dimension: "per_specific_use"` entry pointing to a specific activity feed item.
- Entry visibly changes state within 1 second; no nested confirms.

### 4.5 Kantara Receipt Export
- Button on My Consent Card → produces downloadable JSON.
- Format MUST follow the Inputs shape in `spec.md` (`participant_id`, `event_id`, `data_consent {}`, `attention_consent {}`, `state_changes []`, `revocation_history []`).

---

## 5. Sample seed data scenarios

Generate three sample Consent Receipt JSON objects in code to seed `localStorage` on first run. They correspond to the three scenarios the spec is designed around. Use these directly as seed data, and as the basis for the verification walkthroughs in §10.

### Scenario A — Fully restrictive default
- All 6 data dimensions: `no`
- Attention: `approach_mode: "no"`, `topics_open: []`, `daily_contact_budget: 0`, `quiet_windows: ["all_day"]`
- `state_changes`: a single entry recording the participant accepted defaults at session start
- `revocation_history`: empty
- Purpose: verifies that the system honors "all-refused" as a valid participation mode, not as missing data.

### Scenario B — Partial grant with mid-event dimension-level revocation
- Data: `face: within_event`, `name: within_event`, `voice: no`, `quote: no` (originally `within_event`, then revoked mid-event), `presence: public`, `post_event_reference: within_event`
- Attention: `approach_mode: "topic_scoped"`, `topics_open: ["learning", "partnerships"]`, `topics_closed: ["hiring", "fundraising"]`, `daily_contact_budget: 5`, `quiet_windows: ["12:00-13:00"]`
- `state_changes`: two entries — one session-start, one for the `quote` dimension change
- `revocation_history`: one entry against the `quote` dimension showing `previous_level: within_event`, `propagation_status: complete_within_24h`
- Purpose: verifies independent-dimension grants and dimension-level revocation.

### Scenario C — Broad grant with per-use post-event refusal
- Data: all 6 dimensions at `public`
- Attention: `approach_mode: "open"`, `topics_open: ["all"]`, `daily_contact_budget: 15`, `quiet_windows: []`
- `state_changes`: one session-start entry recording broad active grant
- `revocation_history`: one entry with `dimension: "per_specific_use"`, `specific_use_ref` pointing to a seeded activity-feed asset (e.g., `"recap_video_segment_07:42"`), and `note` explaining the dimension-level grant remains intact
- Purpose: verifies per-use revocation as distinct from dimension-level revocation.

---

## 6. Acceptance criteria

| # | Criterion | How to verify |
|---|---|---|
| AC1 | Default for every dimension is most restrictive | Clear localStorage, open, wait 30s, inspect — every dimension is `no` |
| AC2 | Each dimension independent — no bundling | Reproduce Scenario B: change face to `within_event`; quote stays `no`; attention dimensions independent |
| AC3 | Revocation is single-step | UI step count ≤ 2 taps |
| AC4 | Revocation propagates within 1 second in UI; "propagated to N systems (mocked)" indicator appears | Visible feedback within 1s; mocked downstream count is shown |
| AC5 | Refusal is first-class | After revoke, dimension shows "revoked at [ts]" with a corresponding `revocation_history[]` entry |
| AC6 | Kantara export matches the shape in `spec.md` §Inputs | Exported JSON contains the expected top-level keys and structure |

---

## 7. Refusal Boundaries — MUST NOT exist in your demo

The integrated spec has 4 Refusal Boundaries (`spec.md` §"Refusal Boundaries"). As they apply to the participant app:

| Forbidden | Source RB | Why |
|---|---|---|
| Compliance certificate PDF / share button on Consent Card | RB1 | Receipts describe what happened; never certify legitimacy. |
| Aggregate consent score / "openness" / leaderboard / demographic view | RB2 | No aggregate consent surveillance. |
| "Compare with average participant" view | RB2 | Same. |
| Push notifications nudging participant to extend consent for better recap | RB3 | System does not nudge the sovereign party. |
| "Suggested settings" smart defaults bypassing active grant | RB3 | Active grant required for every dimension. |
| "Auto-import last event's settings" without active grant | RB3 | Same. |
| Network size / connection count / engagement metric / "people you may know" | RB1 | This is not LinkedIn. |
| Export to LinkedIn / sponsor CRM / any external system at runtime | RB4 | No external regulated system scope creep. |

If you find yourself building any of these, **stop** and re-read `spec.md` §"Refusal Boundaries."

---

## 8. Out of scope

| Out of scope | Where it belongs |
|---|---|
| Organizer Dashboard, Asset Pipeline Queue, Audit Trail Browser, Cultural Calibration Profile Editor | Organizer layer of the integrated spec — different build |
| AI Content Compliance Reviewer | AI Compliance layer of the integrated spec — different build |
| Cross-event consent portability (importing previous Kantara Receipts) | A later phase |
| Real Real-time Consent Bus across processes | Needs server infra; mock with in-tab events / `localStorage` only |
| Sponsor CRM integration | A later phase |
| Quarterly re-consent email loop | Needs email infra |
| Cultural Calibration Profile authoring UI | Organizer layer; use a hardcoded profile in the demo |
| Authentication / identity verification | Mock as logged-in |
| Production deployment | This is a demo |

---

## 9. Deliverables

Place all under a new directory `consent-layers-demo/participant-app/`.

| # | Deliverable |
|---|---|
| 1 | Runnable code (entry point + supporting files) |
| 2 | `README.md` with single-command start instructions |
| 3 | `TECH_CHOICES.md` listing every tech choice + "demo only" rationale + "what to reconsider for production" note |
| 4 | `ACCEPTANCE_WALKTHROUGH.md` — step-by-step manual test script for AC1-AC6 |
| 5 | (Optional) Screenshots or short screen recording |

The `TECH_CHOICES.md` is **non-negotiable**.

---

## 10. Verification before declaring done

Walk through these in order:

1. **Fresh-load**: Clear localStorage, open, do nothing 30s, inspect — every dimension is `no`.
2. **Scenario B walkthrough**: Reproduce the partial-grant scenario from §5. Grant face + name; keep voice + quote restrictive; set attention to topic-scoped (learning + partnerships only). Then revoke quote.
3. **Scenario C walkthrough**: Reproduce the broad-grant scenario from §5. Grant broadly. Revoke a seeded activity feed entry. Confirm dimension-level grant unchanged.
4. **Export**: Click Export Kantara Receipt. Compare exported JSON shape to `spec.md` §Inputs.
5. **Refusal check**: Try to find any of the 8 forbidden features (§7). Confirm none exist.

If any walkthrough fails, fix and re-run.

---

## 11. Time and effort

A capable engineer / coding agent should produce a working v1 in **1 to 3 focused days**. Beyond 5 days → re-check §8 for scope creep.

---

## 12. After you're done

Write a 1-page summary:
- What went smoothly in the spec
- What was unclear and required improvisation
- Which Acceptance Criteria felt easy; which felt forced

---

## Quick-reference — 5 essential sentences

If you forget everything else:

1. **Default state is the most restrictive level.** Participant grants actively; never has to actively refuse.
2. **Each dimension is independent.** No bundling controls across data + attention or within either layer.
3. **Revocation is single-step.** One tap, optionally one confirm, done.
4. **Refusal is first-class.** A revoked state is shown explicitly with timestamp, not hidden as "missing data."
5. **Kantara Receipt is the portable master record.** Everything else references it.

---

*End of handoff. Read `./spec.md` next. Begin work. Do not improvise on Refusal Boundaries or the default-restrictive rule.*
