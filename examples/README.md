# `examples/` — Worked examples and seed bundles

A menu of worked examples. Show whichever fits the team you're working with.

## Sample submission pairs (different output shapes)

These are end-to-end worked examples: `team-submission-v0` → frozen → `agentic-build-packet-v0` → TELUS lane run → witness record.

| Example | Shape | When to show | TELUS preflight |
|---|---|---|---|
| [`sample-submission-pair/`](sample-submission-pair/) (Kelp Watch) | Numeric rollup (means + counts) | Team wants observation/measurement aggregation | ✅ Gemma 6/6, Qwen 6/6 |
| [`sample-submission-receipt-wall/`](sample-submission-receipt-wall/) (Story Receipts) | Markdown text aggregation with consent gates | Team wants public-display wall with per-record consent | ⚠️ Gemma 7/7 (fixed), Qwen 5/7 |
| [`sample-submission-commitment-pool/`](sample-submission-commitment-pool/) (Pool Routing) | Per-kind routing diagnostic | Team thinking about offer/need fit and consent as blocker | ⚠️ Gemma 7/7 (fixed), Qwen 6/7 |

## Composition + bundling examples

| Example | Purpose | When to show |
|---|---|---|
| [`composition-v0/`](composition-v0/) | Simulated participant offerings becoming candidate bundles | Team wants to understand how multiple offerings combine |
| [`open-kit-collective-demo/`](open-kit-collective-demo/) | End-to-end Open Kit prototype path | Team wants to see the full receipt/witness loop |

## Pattern examples

| Example | Pattern shown |
|---|---|
| [`consent-review-desk/`](consent-review-desk/) | Refusal, review, withdrawal, and display approval |
| [`receipt-wall-static/`](receipt-wall-static/) | Public/sample-only witnessing surface |
| [`handoff-packet-studio/`](handoff-packet-studio/) | Freezing a selected bundle |
| [`ai-attempt-review-pattern/`](ai-attempt-review-pattern/) | Reviewing an AI-assisted attempt without treating AI output as authority |
| [`spec-experiments/`](spec-experiments/) | First fixture-backed spec experiments |

## Which to show when a team asks…

| Team's question | Show |
|---|---|
| "What does a finished submission look like?" | `sample-submission-pair/sample-team-submission-v0.md` |
| "What does the runtime packet look like?" | `sample-submission-pair/sample-agentic-build-packet-v0.json` |
| "What does the Tuesday witness record look like?" | `sample-submission-pair/sample-witness-record.md` |
| "What if our output is text / markdown?" | `sample-submission-receipt-wall/` |
| "How do we model consent at the per-record level?" | `sample-submission-receipt-wall/` |
| "How does the TELUS lane actually run?" | Any of the `sample-submission-*/preflight-findings.md` + their `runs/` dirs |
| "How do offerings become a bundle?" | `composition-v0/README.md` |
| "How do you handle refusal/withdrawal?" | `consent-review-desk/` |
| "Can we see something working end-to-end?" | `open-kit-collective-demo/` |

## Anti-patterns documented here

- **None of these examples claim authority, certification, or reuse permission.** Each example explicitly carries that disclaimer.
- **All worked examples use Salish-Sea-ecological framings** (kelp, herring, eelgrass, salmon) — no Indigenous-cultural content without authorization. The discipline is consistent across the directory.

## Reproducing the preflight runs

Each `sample-submission-*/` has a `preflight-findings.md` with the exact run command. To reproduce:

```bash
cd ~/projects/IndigenomicsAI && python3 scripts/jam/run-build-packet.py \
  --packet <path-to-sample-agentic-build-packet-v0.json> \
  --output-dir <path-to-sample-submission-*/runs> \
  --run-prefix <prefix> \
  --models gemma-4-31b,qwen-3.6-35b
```
