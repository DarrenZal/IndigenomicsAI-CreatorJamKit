# Sensor To Receipt Output Report

Status: pass for public-sample packet and receipt fixtures only

This report renders `sensor-observation-packets.json` and `witness-receipts.json`. It tests whether three different observation types can become public-safe evidence packets and receipts without overclaiming.

## Participant-Safe Scope

- All people, devices, places, measurements, and evidence pointers are fictional.
- No exact coordinates, sensitive site details, real participant identities, protected cultural material, or Nation-specific knowledge are included.
- Public summaries are generalized and cannot be used for enforcement, eligibility, underwriting, risk pricing, or compliance inference.

## Packet Inventory

| Packet | Type | Public Location | Review State | Computation State |
| --- | --- | --- | --- | --- |
| `obs:temp-blue-heron-001` | sensor reading | approximate 10 km grid | reviewed with limits | allowed as sample observation only |
| `obs:field-note-blue-heron-002` | field note | approximate 25 km grid | needs review before computation | not for computation |
| `obs:repair-blue-heron-003` | repair event | approximate 10 km grid | reviewed with limits | allowed as sample event only |

## Receipt Rollup

| Receipt | What It Records | What It Does Not Prove |
| --- | --- | --- |
| `receipt:sensor-temp-blue-heron-001` | A fictional 12.4 degC demo reading with visible calibration and uncertainty. | Watershed condition, trend, deployment, or verification. |
| `receipt:field-note-blue-heron-002` | A fictional qualitative note with reduced public location precision. | Species verification, trend evidence, or computation-ready data. |
| `receipt:repair-blue-heron-003` | A fictional reported maintenance event. | Restoration success, compliance, or real-world completion. |

## Acceptance Checks

| Criterion | Status | Evidence |
| --- | --- | --- |
| Sensor readings and human observations can share one packet model. | pass | Sensor reading, field note, and repair event use the same top-level model. |
| Location precision can be reduced for sensitive places. | pass | The field note is `sensitive_location_flag: true` and uses `coarse_region_only`. |
| Calibration and uncertainty are visible. | pass | Each packet and receipt exposes calibration or not-applicable status plus uncertainty limits. |
| Public receipts do not expose protected locations or identities. | pass | Receipts use fictional identities, generalized locations, and no coordinates. |
| Records can be withdrawn, corrected, or marked not-for-computation. | pass | Each packet has correction/withdrawal fields; the field note is marked not-for-computation. |

## Refusal Boundaries

- Do not treat a raw sensor reading as a verified claim.
- Do not publish sensitive ecological or cultural locations.
- Do not infer compliance, enforcement, risk pricing, underwriting, or eligibility from these packets.
- Do not assume a device owner or observer has authority to publish place-based knowledge.
- Do not reuse a withdrawn, corrected, or not-for-computation packet without review.

## Review Notes

- The temperature packet can demonstrate receipt emission, but a single reading cannot establish a trend.
- The field note demonstrates reduced public precision and not-for-computation handling.
- The repair event can be receipted as reported maintenance, but the receipt must not claim restoration outcomes.

## Witness Outcome

The pipeline fixture satisfies the first build step for the draft spec: one temperature sensor reading, one field note, one restoration repair event, and one public-safe witness receipt for each. The fixtures are ready for a static renderer, CLI validator, or reviewer walkthrough, but they are not real-world evidence.
