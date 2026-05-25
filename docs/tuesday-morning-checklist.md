---
doc_id: indigenomics.jam.tuesday-morning-checklist
doc_kind: participant-guide
status: v0
date: 2026-05-25
audience: participants on Tuesday before 3 PM canoe landings
---

# Tuesday Morning — Participant Checklist

Day 2 of the Creator Jam closes with **canoe landings + team sharing at ~3 PM**. By then, your team needs a witness record ready to share with the room.

This is what to do Tuesday morning.

## Step 1 — Reconcile your team-submission with what actually happened

Look at your `team-submission-v0` from Monday. Does it still describe what your team actually did?

If yes: great.

If no — your team adjusted the spec mid-build, or the build went a different direction, or you discovered something — that's fine. **Note the divergence.** It goes in your witness record under "what we learned" or "what did not work / what broke."

## Step 2 — Open your build-attempt artifacts (if applicable)

If your team used the TELUS lane, open `build-attempt.json` and read the `finding` field. Open `reviewer-findings.json` and read the per-check status. Open the generated tool (`attempt-1.py`).

If your team built by hand or used your own AI, gather your equivalent artifacts: the tool, the test results, any reviewer notes.

## Step 3 — Draft the witness record

If your build attempt produced `canoe-landing/witness-record.md`, start from that draft. Edit it.

If not, use `templates/witness-rollup.md` as a starting point.

The witness record has six fields:

1. **What we brought** — your offerings, sources, the spec you wrote
2. **What we attempted** — the build attempt, hand or AI lane, anything you tried
3. **What worked** — concrete: tests passed, the room can recognize "yes, that worked"
4. **What did not work / what broke** — concrete: failed tests, missing pieces, gaps you noticed
5. **What we learned** — the divergence between Monday's plan and Tuesday's reality. The thing you didn't see coming.
6. **Boundaries that remain** — what stays held by the team, what was named only as a marker, what would need authorization to revisit

Plus the **receipt statement** — verbatim from `templates/witness-rollup.md`:

> "This record states what happened. It does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse."

## Step 4 — Validate the witness record

Run the overclaim validator:

```bash
python3 tools/witness-record-validator.py <path-to-your-witness-record.md>
```

It flags language the kit's discipline says witness records must not carry: "certified", "officially", "authorized", "community-approved", "AI-validated", "ready for reuse", and similar.

If you get any flags, edit the language. The disclaimer-context detector understands the receipt statement boilerplate — it won't flag those words inside the disclaimer itself, only when they're used to make claims.

Aim for **zero high-severity findings + receipt statement present**.

## Step 5 — Decide what's shared aloud vs. shared in writing

Your team set the Tuesday `display_scope` at freeze time. Honor it.

- `whole` — the whole witness record can be shown to the room
- `partial` — only the named parts can be shown
- `spoken-only` — your team shares aloud Tuesday; nothing in writing on a wall
- `none` — your witness record stays with your team

If anything has changed (e.g., a contributor changed their mind about display), record the change. The witness record itself should reflect what's being shared.

## Step 6 — If something was withdrawn

If a team member or contributor withdrew a contribution since Monday, use the propagation tool:

```bash
python3 tools/withdrawal-propagation.py <manifest.json> <withdrawn-id>
```

It shows which surfaces and summaries reference the withdrawn item. Manually update each — the tool doesn't auto-update.

The withdrawn item gets a line in your "Boundaries that remain" section noting the withdrawal.

## Step 7 — Bring your witness record to the canoe landings

At 3 PM, each team reads (or shares aloud) their witness record. Other teams listen. There is no scoring, no ranking, no "best team." The room witnesses what happened.

If your witness record is "not-fit-yet" — your offering didn't compose, your build attempt didn't converge, your spec turned out to be different from what your team imagined — **read it anyway.** Non-fit and refusal are valid Jam outcomes. The room learns from your discipline as much as from anyone's success.

## Final reminder

> A refusal can be a complete offering. "Doesn't fit yet" is a real outcome. We will witness that together.

You don't have to have built something to have brought something. What you brought is the offering. What you learned is the receipt.

## Boundary

This is a participant-facing checklist. Your facilitator + the canoe-landing-runbook (facilitator-facing) are the sources of truth for the actual Tuesday flow.

This document also does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.

🛶
