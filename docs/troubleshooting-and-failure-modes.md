---
doc_id: indigenomics.jam.troubleshooting-failure-modes
doc_kind: facilitator-reference
status: v0
date: 2026-05-25
audience: mentors during the jam
---

# Troubleshooting + Failure-Mode Catalog

Observed across **5 TELUS-lane preflights** overnight on 2026-05-25 (Mon morning):
- 3 sample submission pairs (Kelp Watch, Story Receipts, Pool Routing)
- 4 spec preflights (Witness Validator, Claims Coherence, Sensor-to-Receipt, Untracked Allocation)
- Both Gemma 4 31B and Qwen 3.6 35B exercised on each
- ~18 total model build attempts, ~8 repair attempts

This catalog tells mentors **"if the model does X, here's what to tell the team."**

---

## The five failure modes I observed (ranked by frequency)

### 1. Spec ↔ acceptance-test misalignment

**Frequency**: Most common. Showed up in Kelp Watch (initial), all three repairs on Story Receipts, both Witness Validator attempts.

**What it looks like**: Model produces output that's "obviously what the spec says," but doesn't match the acceptance test exactly. Often a tiny detail: blank line placement, em-dash vs hyphen, plural-vs-singular, "for" vs "of" in a label.

**Why it happens**: Models read the spec strictly. Tests assert behavior. When the spec is ambiguous about a detail, the model picks one interpretation; the test asserts the other.

**Mentor action**:
- Pull up the test failure diff (it's in `runs/<id>/attempt-1-test-output.txt` or `repair-test-output.txt`)
- Ask the team: "Does the spec say this, or only the test?"
- Either sharpen the spec (more common, better long-term) or relax the test
- Re-run the build attempt

**Worked example**: Kelp Watch's first attempt failed 4/6 because the spec said "one blank line between sites" — ambiguous about blank-line-before-SUMMARY. Sharpening the spec to "one blank line after each site block, including the last" fixed it on both models first try.

### 2. Optional CLI arguments not wired up

**Frequency**: Both Witness Validator attempts (Gemma + Qwen) and Claims Coherence (Gemma) failed for this reason.

**What it looks like**: Spec says "Run as `python3 tool.py <required_arg> [optional_arg]`." Model implements the required arg, ignores the optional one and defaults to something derived from the data.

**Why it happens**: Optional CLI args are easy to miss. The model reads "this defaults to X if not provided," picks "X derived from the data," and skips parsing `sys.argv[2]` entirely.

**Mentor action**: Three options, in order of preference:
1. **Make the arg required** — change the spec, eliminate the failure mode
2. **Write an acceptance test that explicitly exercises the arg** — gives the model a feedback signal to repair against
3. **Default to a fixed value, not data-derived** — easier for the model to get right than "latest date in the data"

**Worked example**: Witness Record Validator had `as_of YYYY-MM-DD` as optional second arg. Both models defaulted to "latest evidence created_at" and missed the CLI parameter. Test asserted `as_of=2026-05-20`, model used 2026-05-15 (the data's latest date). 1 test failed, both attempts.

### 3. Text-format outputs with strict whitespace rules

**Frequency**: Story Receipts (both models), Commitment Pool (both models in first attempt, Gemma repaired)

**What it looks like**: Model produces correct content with wrong vertical whitespace — missing blank lines, extra blank lines, or wrong blank-line placement between blocks.

**Why it happens**: Models prioritize content correctness over presentation rules. Markdown vertical whitespace gets compressed or expanded as the model "renders."

**Mentor action**:
- If the team chose a markdown/text-format output, expect at least one repair cycle
- Write at least one acceptance test that asserts exact line-by-line output for a small fixture
- Consider whether the team really needs strict markdown — a JSON output with whitespace handled downstream may be more model-friendly

**Pattern**: Gemma usually recovers from blank-line failures with concrete test feedback in repair; Qwen sometimes doesn't.

### 4. Numeric/structural shape (rollup, routing) — most robust

**Frequency**: Both Kelp Watch (after spec sharpening) and Sensor-to-Receipt + Untracked Allocation hit 6/6 first try on both models.

**What it looks like**: Specs that ask for numeric rollups, per-key aggregations, or categorical status determinations are the most model-robust shape. No whitespace traps, no optional-arg ambiguity, clear "what to compute and print."

**Mentor action**:
- If a team is choosing a spec shape, recommend numeric/tabular over markdown when stakes are tight
- For exploratory teams, markdown is fine — just expect one repair cycle

### 5. Boundaries and excluded inputs — honored structurally

**Frequency**: Across all 7 preflights (5 sample/spec runs × 2 models = ~14 builds), **zero boundary leaks** were observed in any generated tool or output.

**What it looks like**: The exporter strips `excluded_inputs` content before the packet reaches the model. The model never sees the protected material. The reviewer-findings auto-check confirms no excluded-content substring appears in the generated code or output.

**Mentor action**: This is reassuring data. Teams worried about "what if the model leaks our protected material?" can be shown the reviewer-findings.json — the structural pattern works.

**Caveat**: This is one night of preflights. A team should still spot-check generated code for any concept names that might have leaked from cleared offerings (boundaries are honored; cleared offerings can still produce surprising outputs).

---

## Decision tree for "the build failed"

```
Did the codegen step succeed (model returned code)?
├─ NO  → API/timeout issue. Re-run. If still failing, check v2/.env has TELUS_MODELS_JSON.
└─ YES → Did tests pass?
    ├─ ALL PASS → Built clean. Done.
    ├─ SOME PASS → Did repair attempt converge?
    │   ├─ YES (built clean after repair) → Good. This is normal for spec-heavy formats.
    │   ├─ NO (improved but still partial) → Check WHICH tests failed:
    │   │   ├─ Whitespace/formatting failures → See failure mode #3. Sharpen spec or accept.
    │   │   ├─ Missing-feature failures → See failure mode #2. Was an optional arg involved?
    │   │   └─ Logic failures → See failure mode #1. Spec ↔ test misalignment.
    │   └─ NO REPAIR (no-change) → Same checks as "improved but still partial."
    └─ NONE PASS → Spec is severely misaligned with tests. Walk through the spec
                   word-by-word with the team. Often a fundamental interpretation gap.
```

---

## What I'd tell a team in the moment

### When the model returns 6/6 first try
> "Clean build. Read the generated code — does it match what you imagined? If yes, you're done. If no, that's still useful — it tells you something about how your spec was interpreted."

### When the model returns 4/6 → 6/6 after repair
> "Normal. The first generation interpreted the spec one way; the repair fed it the failing test as feedback and it adjusted. This is exactly what the lane is designed to do."

### When the model returns 4/6 → 4/6 no-change
> "The repair attempt didn't converge. Two paths: (a) read the failing test and sharpen the spec to match — usually the right move; (b) read the model's code and judge whether what it produced is what you wanted, in which case relax the test. Either way, the witness record captures what happened."

### When the model returns 0/6 or 1/6
> "Severe misalignment. Let's read the spec out loud together and find where the model interpreted it differently from how we wrote the tests. This is the most valuable kind of failure — it tells us the spec wasn't carrying what we thought it was."

### When the team asks "should we try a different model?"
> "Maybe. Gemma 4 31B is the default. Qwen 3.6 35B sometimes catches what Gemma misses, and vice versa. But if the failure is spec-vs-test alignment, neither model will fix it — that's a spec problem, not a model problem. Try sharpening first; switch models second."

---

## Model-by-model patterns observed (this one night only)

| Pattern | Gemma 4 31B | Qwen 3.6 35B |
|---|---|---|
| Numeric/tabular outputs | strong | strong |
| Markdown blank-line rules | repairs well from test feedback | sometimes stuck even after feedback |
| Optional CLI args | often misses | sometimes catches |
| Drop-rule logic | strong | strong |
| Normalization (strip/collapse/lowercase) | strong | strong |
| Multi-block structured output | repairs well | repairs partially |
| First-try success rate | ~50% | ~50% |
| Repair convergence rate | high | medium |

**Caveat**: This is one night. Don't generalize. The data exists in `examples/sample-submission-*/preflight-findings.md` and `specs/preflights/*/runs/`.

---

## Things I expected to be failure modes but weren't

- **Boundary leaks**: zero observed. The exporter strips content structurally.
- **Network/credential access in generated code**: zero observed. Models follow the "stdlib only" constraint reliably.
- **Hardcoded fixture data**: zero observed. Models produce data-driven code, not look-up tables.
- **Infinite loops / timeouts**: zero observed (90s timeout was never hit).
- **Carol Anne overclaims or culturally insensitive language**: zero observed. Salish-Sea-ecological framings produced no concerning outputs.

---

## When to call for help

If you've spent 20+ minutes with a team and the build is still failing:

1. Pull in **Bill Edmunds** (floater mentor)
2. If it's a spec-architecture question, pull in **Carol Anne** for a 1:1 check-in
3. If it's a TELUS-lane harness issue, **Shawn** owns the gateway; pull him in
4. Worst case: switch the team to a hand-build or own-AI path; the lane is one option, not the only path

The team's two days are valuable. A spec that won't build is data — record it as a witness record finding, not as a failure to ship.

## Boundary

This catalog reflects one night of preflights against five small specs and four model attempts each. It does not predict every team's experience, certify model behavior on different specs, or guarantee any particular failure mode is impossible. Mentors observe, name, and adjust as the day unfolds.
