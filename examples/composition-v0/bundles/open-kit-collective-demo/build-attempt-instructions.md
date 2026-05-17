# Frozen Build Attempt Instructions: Open Kit Collective Demo

Status: frozen for composition v0 rehearsal

## Packet

```yaml
packet_id: handoff:composition-v0-open-kit-collective-demo
bundle_id: bundle:open-kit-collective-demo
default_demo_path: manual/static HTML walkthrough
optional_showcase_path: TELUS notes-only builder/reviewer/witness harness
```

## Goal

Attempt a bounded public demo showing one collective bundle becoming executable:

1. Read the selected bundle files.
2. Use only public sample or display-approved content.
3. Show how the public commitment maps to the existing Open Kit commitment-pool demo.
4. Confirm refusal and consent boundaries are visible.
5. Produce builder notes, reviewer notes, and witness rollup.

## Authorized Inputs

- `docs/jam/composition-v0/integration-report.md`
- `docs/jam/composition-v0/bundles/open-kit-collective-demo/bundle.md`
- `docs/jam/composition-v0/bundles/open-kit-collective-demo/included-fragments.md`
- `docs/jam/composition-v0/bundles/open-kit-collective-demo/does-not-fit-yet.md`
- `docs/jam/composition-v0/bundles/open-kit-collective-demo/review-required.md`
- `docs/jam/composition-v0/bundles/open-kit-collective-demo/discourse.md`
- `docs/specs/open-kit-frozen-handoff-packet-v0.md`
- `docs/specs/open-kit-facilitator-script-v0.md`
- `examples/commitment-pool/salish-sea-ecological-v0.1.html`
- `examples/witnessing/witnessing-receipt-v0.2.schema.json`

## Non-Inputs

Do not use:

- protected cultural, language, protocol, ceremony, or Nation-specific material
- participant-private notes
- private contact details
- unapproved real receipts
- production credentials or deployment secrets

## Acceptance Criteria

| ID | Criterion |
|---|---|
| `AC1` | The selected bundle has clear included, review-required, and does-not-fit-yet notes. |
| `AC2` | The build attempt stays within the Open Kit public/sample path. |
| `AC3` | The receipt boundary is explicit: records what happened, not approval or authority. |
| `AC4` | TELUS/Jupyter remains optional. |
| `AC5` | The witness rollup records pass, partial, fail, refused, and not-run states honestly. |

## Refusal Boundaries

| ID | Boundary | Required Action |
|---|---|---|
| `RF1` | Protected or authority-bound material appears. | Stop and route to review. |
| `RF2` | A receipt is framed as legitimacy, authority, certification, or reuse readiness. | Stop and repair language. |
| `RF3` | TELUS/Jupyter is treated as required. | Return to manual/static path. |
| `RF4` | The attempt expands into a full agent framework or platform. | Stop and defer. |

## Execution Note

Before running this packet through the TELUS notes-only builder/reviewer/witness harness, run:

```bash
python3 scripts/jam/validate-composition-dag.py
```

Run-specific evidence belongs in `receipt-rollup.md` and the generated harness output. Do not edit this packet during a harness run.
