---
doc_id: indigenomics.jam.what-happens-next
doc_kind: participant-guide
status: v0
date: 2026-05-25
audience: participants who have just submitted their team-submission
---

# What Happens After You Submit

You've drafted your team-submission-v0. Here's what happens next, from your perspective.

## Right after you submit

**A facilitator walks through your submission with your team.** They check the freeze checklist:

- Did your team review the final vision/spec text together?
- Are the included offerings cleared (do you have permission to use them)?
- Are private/protected/marker-only records named only as boundaries (not disclosed)?
- Is the Tuesday sharing scope explicit (whole / partial / spoken-only / none)?
- Is the AI/TELUS input scope explicit (whole / partial / none)?
- Is the build path confirmed (hand / own-AI / TELUS lane / mixed)?
- Is "witnessed working" clear enough for a reviewer to understand?

If anything is unclear, the facilitator marks the submission `needs-review` and your team resolves it together.

## Freeze

If everything is clear, the facilitator confirms the freeze. They read aloud:

> "This submission is frozen for a build attempt. It is not approval, certification, authority, or reuse permission. New ideas require re-freeze before they enter the build lane."

Your team can still bring new ideas — but they require a re-freeze before they can enter the build lane.

## If your build path is "TELUS lane" or "mixed"

An operator (or the gateway, if it's running) exports your `team-submission-v0` into an `agentic-build-packet-v0` — a leaner runtime packet that:

- Carries your vision, spec, and cleared offerings
- **Strips the content of all boundaries** (your protected material never goes to the model — only the boundary's existence is recorded)
- Sends only what your `ai_input_scope` permits

Then the TELUS build lane runs your packet through one or both models (Gemma 4 31B, Qwen 3.6 35B):

1. **Codegen**: the model produces a single-file Python tool from your spec
2. **Acceptance test**: the test you wrote runs against the generated tool in a scrubbed environment (no network, no credentials)
3. **One repair attempt** (if first try fails): the model sees the failing tests and tries again
4. **Reviewer findings**: automatic checks for stdlib-only-ness, excluded-input leak, and the specific review checks you wrote

Time: typically 30s–2min total.

You'll see: `build-attempt.json` (what the model did), `reviewer-findings.json` (what the automatic checks saw), `attempt-1.py` (the generated tool), and a draft `witness-record.md` (auto-filled from your `witness_record_seed`).

## If your build path is "hand" or "own AI"

You write the tool yourself, or use your own AI tools. The kit's `run-build-packet.py` is optional — you can verify your build against your acceptance tests however you like.

The freeze step still applies. The witness record still applies Tuesday.

## During the build

You can keep working. The build attempt is asynchronous — you don't have to babysit it. Your team can prepare your Tuesday share, write reflections, or pair with another team.

If you have ideas the build attempt didn't capture: write them down. They go in your team's notes, not into the running build packet. After freeze, the build packet is the build packet — new ideas need a re-freeze.

## When the build returns

Open `build-attempt.json` (or have your mentor open it). The `finding` field tells you what happened:

- **`built clean`**: the model produced a tool that passed your acceptance tests on the first attempt
- **`fixed`**: the model needed one repair cycle from test feedback, then passed
- **`improved`**: the repair attempt got closer but still partial
- **`no change`**: the repair didn't converge — the model couldn't reconcile the spec with the tests
- **`build failed`**: something went wrong in codegen or testing

**A failed build is not a failed jam.** A failed build is data. Read `attempt-1-test-output.txt` and `repair-test-output.txt` — they show exactly what the model produced and what your tests expected. The gap is informative.

Common situations:
- **Spec ↔ test misalignment** — your spec said X, your tests assert Y. Sharpen the spec or relax the test. Most common failure mode.
- **Optional CLI argument not wired up** — common with optional args. Make it required, or write a test that exercises it.
- **Markdown blank-line rules** — text-format outputs often need one repair cycle even when the spec is clear.

See `docs/troubleshooting-and-failure-modes.md` for the full catalog.

## Tuesday morning

Each team writes a witness record at canoe landings (Tuesday ~3 PM). See `docs/tuesday-morning-checklist.md` for what to prepare.

If your build attempt produced a draft `canoe-landing/witness-record.md`, you can start from that draft. Edit it to add what you actually want the room to hear.

Before reading aloud, run `tools/witness-record-validator.py` against your draft. It catches overclaim language (certification / approval / "official" / "ready for reuse") that the kit's discipline says witness records must not carry.

## If you change your mind

You can withdraw a record any time. Use `tools/withdrawal-propagation.py` to see which surfaces and summaries need to update. The propagation tool doesn't auto-update anything — humans execute the updates. But it shows what's affected.

## Boundary

This walks through the typical post-submit flow. The lived day will adjust. Your facilitator is the source of truth for what's actually happening at any moment.

This document also does not establish authority, approval, certification, legitimacy, community consent, or readiness for reuse.
