---
doc_id: indigenomics.jam.sample-receipt-wall.preflight-findings
doc_kind: preflight-report
status: complete
date: 2026-05-25
run_at: 2026-05-25T08:19Z
---

# Preflight Findings — Story Receipts Wall sample

## Outcome

**Split result: Gemma fixed after repair (7/7); Qwen no-change after repair (5/7).** A useful real-world demonstration that not every model handles every spec on first attempt.

| Model | Finding | Tests | Repair |
|---|---|---|---|
| `gemma-4-31b` | **fixed** | 7/7 | one repair from test feedback → built clean |
| `qwen-3.6-35b` | **no change** | 5/7 (both attempts) | repair did not converge |

Run dirs:
- `runs/sample-story-receipts-gemma-4-31b-20260525T081926/`
- `runs/sample-story-receipts-qwen-3.6-35b-20260525T081926/`

## What Qwen got stuck on

Failing tests (both attempt-1 and repair): `test_1_happy_path` and `test_2_multi_line_receipt`. The model produced the right content but skipped the blank lines required by the spec between the `##` heading and the quoted text, and between the quoted text and the `tags:` line. Diff:

```
   '## A. Cedar — 2026-05-12',
+  '',           ← Qwen missing this blank
   '> Read with the room.',
+  '',           ← Qwen missing this blank
   'tags: learning',
```

The repair attempt got the same test feedback but produced the same wrong output. Qwen appears to systematically under-spec markdown vertical whitespace.

## What Gemma got right (after repair)

Gemma's first attempt was also 5/7 with the same failure pattern. The repair attempt, fed the concrete test-failure diff, produced a clean 7/7 build.

## Pattern: text-format outputs are harder than numeric

Across both sample pairs preflighted overnight:

| Sample | Output shape | Gemma first try | Gemma after repair | Qwen first try | Qwen after repair |
|---|---|---|---|---|---|
| Kelp Watch (numeric) | tabular CLI, mean/count | 2/6 (spec ambiguous) | n/a (spec sharpened, then 6/6 directly) | n/a | 6/6 directly |
| Story Receipts (markdown) | text-format wall | 5/7 | **7/7 fixed** | 5/7 | 5/7 no-change |

Mentor-takeaway: text-format outputs with strict whitespace rules are a real failure mode. Two mitigations:

1. **Pick numeric/tabular shapes when possible.** A team that wants a markdown wall could equivalently produce a JSON-of-blocks and let a downstream renderer handle whitespace.
2. **If the spec is text-format, write at least one acceptance test that explicitly checks blank lines.** Both Gemma and Qwen needed the test feedback to even attempt the fix; without it, neither would have noticed.

## Boundary / leak check (both models, all attempts)

Reviewer findings on both runs:
- ✅ No excluded/marker-only record appeared in tool or output
- ✅ No contributor email/phone/full-surname (display-name initials only — verified by reading both generated tools)
- ✅ No team-only or spoken-only receipt text rendered in the public wall
- ✅ No outputs hardcoded for specific inputs (code is data-driven)

The two model failures were spec-compliance issues, not boundary issues. Both models honored `excluded_inputs` structurally.

## Run command (reproducible)

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-receipt-wall/sample-agentic-build-packet-v0.json \
  --output-dir ~/projects/IndigenomicsAI-CreatorJamKit/examples/sample-submission-receipt-wall/runs \
  --run-prefix sample-story-receipts \
  --models gemma-4-31b,qwen-3.6-35b
```

## Boundary

This run states what happened on 2026-05-25 in two specific model attempts. It does not certify either model's general capability with markdown output. The "Qwen no-change" finding is one data point, not a permanent failure.
