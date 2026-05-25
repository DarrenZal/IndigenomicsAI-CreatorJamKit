# Indigenomics AI Creator Jam Kit

A public kit for participants, facilitators, mentors, and invited reviewers of the Indigenomics AI Creator Jam — a relational build studio (not a hackathon) where people bring offerings, compose them carefully, attempt small builds, and witness what happened.

> **What you can bring**: an idea, sketch, prompt, code, practice, commitment, refusal, or question.
> **What this kit holds**: schemas, sample submissions, spec menus, mentor guides, a knowledge bundle for participant LLMs, and small utilities.
> **What this kit is not**: an authority, an approval surface, or a reuse permission. Receipts record what happened — nothing more.

📍 Jam dates: **2026-05-25 / 2026-05-26** · Vancouver (Northeastern + Space Center) + Victoria (UVic)

---

## Pick your starting point

| You are a… | Start here |
| --- | --- |
| **Participant** | [docs/participant-handout.md](docs/participant-handout.md) → [examples/sample-submission-pair/](examples/sample-submission-pair/) |
| **Participant using an LLM** to help draft your spec | [participant-agent-context/](participant-agent-context/) (especially [PROMPTS_FOR_AGENTS.md](participant-agent-context/PROMPTS_FOR_AGENTS.md)) |
| **Mentor** | [docs/MENTOR_FIELD_GUIDE.md](docs/MENTOR_FIELD_GUIDE.md) — keep this open on your phone |
| **Facilitator** | [docs/facilitator-quick-card.md](docs/facilitator-quick-card.md) + [docs/jam-day-timeline-v0.md](docs/jam-day-timeline-v0.md) |
| **Reviewer** or **operator** | [docs/troubleshooting-and-failure-modes.md](docs/troubleshooting-and-failure-modes.md) + [tools/](tools/) |
| **Just browsing** to understand the shape | [OVERNIGHT_RESEARCH_FINDINGS.md](OVERNIGHT_RESEARCH_FINDINGS.md) — what we learned validating the kit |

---

## The shape of a Jam contribution

```
offerings  →  candidate team spec  →  frozen build spec  →  build attempt
                                                              ↓
                                                  review / witness check
                                                              ↓
                                                       canoe landing record
```

Each step is gentle. **"Doesn't fit yet" is a valid outcome.** A refusal can be a complete offering. The kit's discipline keeps boundaries, consent, attribution, and refusal visible at every step.

---

## What's in this kit

### 📘 Schemas

The two canonical record shapes used throughout the Jam:

- [`templates/team-submission-v0.md`](templates/team-submission-v0.md) — what a team writes (rich gateway/fallback record)
- [`templates/agentic-build-packet-v0.md`](templates/agentic-build-packet-v0.md) — what the build lane consumes after facilitator freeze

Other templates in [`templates/`](templates/): [offering quick card](templates/offering-quick-card.md), [spec fragment](templates/spec-fragment.md), [bundle](templates/bundle.md), [build attempt instructions](templates/build-attempt-instructions.md), [reviewer check](templates/reviewer-check.md), [witness rollup](templates/witness-rollup.md), [display review checklist](templates/display-review-checklist.md), [speech-act transition](templates/speech-act-transition.md), [trade-off surface](templates/trade-off-surface.md).

### 📂 Worked examples ([`examples/`](examples/))

Real, walkable end-to-end examples. See [`examples/README.md`](examples/README.md) for a complete menu. Highlights:

| Example | Shape | TELUS preflight |
| --- | --- | --- |
| [`sample-submission-pair/`](examples/sample-submission-pair/) — Kelp Watch | Numeric rollup | ✅ Gemma 6/6, Qwen 6/6 |
| [`sample-submission-receipt-wall/`](examples/sample-submission-receipt-wall/) — Story Receipts | Markdown text wall with consent gates | ⚠️ Gemma 7/7 (fixed), Qwen 5/7 |
| [`sample-submission-commitment-pool/`](examples/sample-submission-commitment-pool/) — Pool Routing | Per-kind diagnostic | ⚠️ Gemma 7/7 (fixed), Qwen 6/7 |
| [`sample-submission-minimal/`](examples/sample-submission-minimal/) | Smallest plausible-and-valid (~50 lines JSON) | n/a |
| [`sample-refusal-only/`](examples/sample-refusal-only/) | A submission that does **not** lead to a build | n/a |
| [`sample-multi-team-composition/`](examples/sample-multi-team-composition/) | Two team submissions → candidate bundle with conflicts surfaced | n/a |
| [`sample-withdrawal-flow/`](examples/sample-withdrawal-flow/) | Withdrawal propagation across surfaces + summaries | n/a |
| [`composition-v0/`](examples/composition-v0/) | Simulated participant offerings becoming candidate bundles | n/a |
| [`open-kit-collective-demo/`](examples/open-kit-collective-demo/) | End-to-end Open Kit prototype path | n/a |
| [`consent-review-desk/`](examples/consent-review-desk/) | Refusal, review, withdrawal, and display approval workflow | n/a |
| [`receipt-wall-static/`](examples/receipt-wall-static/) | Public/sample-only witnessing surface | n/a |
| [`handoff-packet-studio/`](examples/handoff-packet-studio/) | Freezing a selected bundle | n/a |
| [`ai-attempt-review-pattern/`](examples/ai-attempt-review-pattern/) | Reviewing an AI-assisted attempt without treating output as authority | n/a |

### 🗂️ Spec menu ([`specs/`](specs/))

A backlog of 14 ready-to-jam specs — see [`specs/README.md`](specs/README.md) for the full tagged menu (difficulty, boundary weight, preflight status). Areas: witnessing & claims, commitment pooling, flow funding, bioregional mapping, bioregional insights, insurance & risk, sensors, private learning, app flows, receipt walls, spec composition.

**All 14 specs have been preflighted through the TELUS build lane** on Gemma 4 31B + Qwen 3.6 35B + gpt-oss 120B. See:

- [`specs/preflights/README.md`](specs/preflights/README.md) — per-spec results, spot-checked-good list
- [`specs/preflights/3-model-comparison.md`](specs/preflights/3-model-comparison.md) — where each model converges
- [`specs/preflights/stress-tests/README.md`](specs/preflights/stress-tests/README.md) — 5 adversarial harness probes

### 🤖 For participant LLMs ([`participant-agent-context/`](participant-agent-context/))

A ready-to-ingest knowledge bundle for any LLM helping a participant team draft a spec. Public-safe; Salish-Sea-ecological framings throughout.

| File | What it carries |
| --- | --- |
| [`carol-anne-voice.md`](participant-agent-context/carol-anne-voice.md) | 64 attributed Carol Anne quotes |
| [`25-themes-summary.md`](participant-agent-context/25-themes-summary.md) | All 25 themes with anchoring quotes + sample build ideas |
| [`compositional-field-orientation.md`](participant-agent-context/compositional-field-orientation.md) | Plain-language primer on the kit's architectural framing |
| [`ruddick-cpp-primer.md`](participant-agent-context/ruddick-cpp-primer.md) | Plain-language commitment-pool primer |
| [`johar-discipline.md`](participant-agent-context/johar-discipline.md) | Four-position frame + process moves |
| [`knowledge-bundle.jsonld`](participant-agent-context/knowledge-bundle.jsonld) | Structured JSON-LD (118 entities) |
| [`PROMPTS_FOR_AGENTS.md`](participant-agent-context/PROMPTS_FOR_AGENTS.md) | Three sample system prompts (spec-drafting / boundary-checker / witness-drafter) |
| [`agent-test-results.md`](participant-agent-context/agent-test-results.md) | All three prompts validated against Claude Sonnet 4.6 |

Run an LLM locally with the bundle pre-loaded: `tools/participant-agent.sh [spec-drafting | boundary-checker | witness-drafter]`.

### 🛠️ Tools ([`tools/`](tools/))

Small standard-library Python utilities for jam-day. No installation needed.

| Tool | What it does |
| --- | --- |
| [`witness-record-validator.py`](tools/witness-record-validator.py) | Catches overclaim language in Tuesday witness records |
| [`withdrawal-propagation.py`](tools/withdrawal-propagation.py) | When a record is withdrawn, what surfaces need to update? |
| [`composition-merger.py`](tools/composition-merger.py) | Merge two team submissions into a candidate bundle (conflicts surfaced) |
| [`spec-linter.py`](tools/spec-linter.py) | Flag 5+ common failure modes in a draft spec before freeze |
| [`extract-submission-json.py`](tools/extract-submission-json.py) | Pull the JSON code block from a sample `.md` for piping into other tools |
| [`participant-agent.sh`](tools/participant-agent.sh) | Wrap `claude -p` with the participant-agent knowledge bundle |

See [`tools/README.md`](tools/README.md) for usage + when-to-use guidance.

### 🪵 Workshop notes ([`workshop/`](workshop/))

Working materials from kit development — composition matrices, coordination weave maps, technical patterns. Useful background; not required reading.

Notable docs: [spec-composition-lab.md](workshop/spec-composition-lab.md), [spec-composition-matrix.md](workshop/spec-composition-matrix.md), [composition-engine-technical-pattern.md](workshop/composition-engine-technical-pattern.md), [coherence-vs-goodness.md](workshop/coherence-vs-goodness.md), [coordination-canoe-weave-map.md](workshop/coordination-canoe-weave-map.md), [waka-claims-engine-primitive-comparison.md](workshop/waka-claims-engine-primitive-comparison.md).

### 🎲 Games ([`games/`](games/))

Lightweight play formats that teach the same speech-act, refusal, review, and receipt primitives as the kit.

---

## Boundaries

This repo is for public, sample, or explicitly display-approved material **only**. Do not add protected, cultural, linguistic, ceremonial, Nation-specific, participant-private, credential-bearing, or authority-bound material unless the right authority has explicitly approved that exact use.

Three rules hold across everything in this kit:

1. **Receipts record what happened. They do not establish legitimacy, authority, certification, or readiness for reuse.**
2. **AI may be used only on public material or material the right person has explicitly approved for that specific AI use.** AI does not judge cultural authority, consent, ceremony fit, or community legitimacy.
3. **If something is private, protected, cultural, protocol-bound, or review-required, record the boundary. Do not disclose the protected material in order to prove the boundary.** Marker-only records preserve presence without disclosure.

See [docs/glossary.md](docs/glossary.md) for terminology, including the local working metaphor "Coordination Canoe" and the explicit reservation of "Waka" for [Austin Wade Smith / RiverComputer's project](https://github.com/RiverComputer).

---

## Fast path for participants

If you have 30 minutes:

1. Read [docs/participant-handout.md](docs/participant-handout.md) (~5 min)
2. Skim [examples/sample-submission-minimal/](examples/sample-submission-minimal/) for the smallest valid submission (~5 min)
3. Glance at [specs/README.md](specs/README.md) for the spec menu (~5 min)
4. Sit with the [facilitator quick card](docs/facilitator-quick-card.md) five offering questions (~15 min)

After submit: see [docs/what-happens-next.md](docs/what-happens-next.md).
Tuesday morning: see [docs/tuesday-morning-checklist.md](docs/tuesday-morning-checklist.md).

---

## Local checks

Lightweight shape + reference checks. They do not certify permission, authority, or correctness.

```bash
python3 scripts/validate-frontmatter.py
python3 scripts/validate-bundle-links.py
python3 scripts/composition_engine.py examples/spec-experiments/commitment-pool-dream-witness-composition --write
python3 scripts/composition_engine.py examples/spec-experiments/claims-witness-receipt-composition --write
python3 scripts/composition_engine.py examples/spec-experiments/commitment-pool-untracked-allocation-blocked --write
```

---

## License + reuse

Code under standard repository terms. Documentation and structural patterns are kit-discipline-bound: see [Boundaries](#boundaries) above. Carol Anne Hilton's quoted material lives within fair-use educational context for the Jam; for reuse beyond the Jam, ask first.
