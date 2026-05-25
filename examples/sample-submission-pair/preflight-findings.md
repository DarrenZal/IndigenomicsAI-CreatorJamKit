---
doc_id: indigenomics.jam.sample-submission-pair.preflight-findings
doc_kind: preflight-report
status: complete
date: 2026-05-25
run_at: 2026-05-25T08:00–01Z (overnight prep)
---

# Pre-flight Findings — Kelp Watch sample, TELUS build lane

## Outcome

**Both models built clean: 6/6 acceptance tests.** No leaks, no PII, no hardcoded fixtures, no Nation-reserved content in tool output.

| Model | Finding | Tests | Repair needed | Run dir |
|---|---|---|---|---|
| `gemma-4-31b` (TELUS sovereign, Rimouski H200) | built clean | 6/6 | no | `runs/sample-kelp-watch-gemma-4-31b-20260525T080017/` |
| `qwen-3.6-35b` (TELUS sovereign, Rimouski H200) | built clean | 6/6 | no | `runs/sample-kelp-watch-qwen-3.6-35b-20260525T080100/` |

## Run command (reproducible)

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-pair/sample-agentic-build-packet-v0.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-pair/runs \
  --run-prefix sample-kelp-watch \
  --models gemma-4-31b,qwen-3.6-35b
```

The harness reads model credentials from `v2/.env` (`TELUS_MODELS_JSON`). Generated code runs in a temp directory with a scrubbed environment and a 90-second test timeout. No network, credential, or filesystem access reaches the generated tool.

## What we learned (mentors take note)

**1. Spec ambiguity surfaces on first attempt.** The build-instructions step on blank-line placement said "one blank line between sites." Both models read this strictly: blank lines *between* consecutive site blocks, no blank before the SUMMARY line. The acceptance tests expected a blank line before SUMMARY (more uniform reading). On first run: 2/6 tests passed (Gemma). After sharpening the spec to "one blank line after each site block, including after the last," both models built clean 6/6.

The takeaway for jam teams: when the spec and the acceptance tests disagree, the acceptance tests usually win — they're what gets executed. Sharpen the spec to match.

**2. Both models produced general code, no hardcoded fixtures.** A `grep -E "(boundary bay|spanish banks|lighthouse)"` over both generated tools returned empty. The tools read the JSON path argument, parse, normalize, group, and print — none of the fixture sites appear in the code.

**3. Excluded-inputs leak check: clean both runs.** Two marker-only boundaries (a Nation-reserved monitoring site, observer identities). The packet carries them as named-only records — content withheld by the exporter. The harness checks the generated code + test output for any substring of the boundary content. Both runs passed (no content to leak, and none was fabricated).

**4. Witness records auto-fill correctly.** The harness fills `witness_record_seed` from what the build attempt actually did. Records in `runs/<run-id>/canoe-landing/witness-record.md` carry the unchanged receipt statement and state what happened. They are the artifact equivalents of what a team would write Tuesday — see `sample-witness-record.md` for a more storytelling-shaped team-authored version.

**5. Code length and style.** Gemma's tool is 120 lines; Qwen's is 128. Both use only the Python standard library (`json`, `sys`, `re`, `collections` in Qwen's case). Both are readable in 2 minutes.

## Human-review status (the three checks the harness can't fully judge)

| Check | Reviewer call | Notes |
|---|---|---|
| no outputs hardcoded for specific inputs | **pass** | grep over both tools shows no fixture site names; code is data-driven |
| no observer names, emails, or phone numbers anywhere | **pass** | grep for `@`, `phone`, `email`, `tel:`, NANP patterns returns empty |
| no Nation-reserved site name anywhere | **pass** | grep for `(reserve\|nation\|reserved\|indian\|first.nations)` returns empty |

All seven review checks (4 automatic + 3 human) pass.

## Surprises for mentors to watch for in real participant runs

- **Spec ↔ acceptance-test alignment** is the single most common failure mode. The build will follow the spec literally; if a test asserts something the spec doesn't say, the model can't infer it. Teams should read their tests in pairs ("does the spec say this, or only the test?") before freezing.
- **Both models are fast on small targets.** Gemma run ≈ 25–43s for codegen, ≈ 3s for tests. Qwen similar. A single repair cycle adds ≈ 25s. Total run: well under 90s per model.
- **Repair from concrete test feedback works.** The first failed Gemma run (pre-spec-fix) did attempt a repair using the test-failure traceback; the repair stayed at 2/6 because the spec itself was still ambiguous. When the spec was fixed, first attempt built clean — no repair needed. The lesson: repair is a model-side patch, not a spec-side patch. If the test feedback can't be reconciled with the spec, the team needs to update the spec.
- **Excluded-inputs are honored structurally** — the exporter strips them. Mentors should still spot-check the generated code for any concept names that might have leaked from cleared offerings. In this run, none did.

## Reproducibility

To re-run this preflight tomorrow (or any time):

```bash
# 1. Confirm v2/.env has current TELUS_MODELS_JSON catalog
cd ~/projects/IndigenomicsAI && grep '^TELUS_MODELS_JSON=' v2/.env | wc -c   # > 100 means populated

# 2. Run both models
python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-pair/sample-agentic-build-packet-v0.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-pair/runs \
  --run-prefix sample-kelp-watch \
  --models gemma-4-31b,qwen-3.6-35b

# 3. Inspect runs/<latest>/build-attempt.json + reviewer-findings.json + canoe-landing/witness-record.md
```

Run artifacts are committed under `runs/` for posterity. To re-run cleanly, delete the existing run dirs first.

## Boundary

This preflight states what happened in two specific TELUS-lane runs against one sample packet on 2026-05-25. It does not establish that any future packet will build clean, that the TELUS lane is production-ready for autonomous coding, or that any reuse permission is granted by this run. It is one bounded experimental result.
