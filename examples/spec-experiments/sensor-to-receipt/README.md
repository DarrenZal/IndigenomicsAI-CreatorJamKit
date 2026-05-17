# Sensor To Receipt Spec Experiment

Status: public-sample fixture packet

This experiment backs `specs/sensor-to-receipt-pipeline.md` with three participant-safe observation packets and three witness receipts.

No real participant content, sensitive location data, protected cultural material, private ecological site details, or enforcement/eligibility inference is included. All devices, people, places, and evidence pointers are fictional public-sample placeholders.

## Files

- `sensor-observation-packets.json` - three evidence packets: one temperature sensor reading, one field note, and one restoration repair event.
- `witness-receipts.json` - one public-safe witness receipt for each packet.
- `output-report.md` - reviewer-facing rollup of packet state, receipt state, acceptance checks, and refusal boundaries.

## Role Split

- Builder: turns each observation packet into a receipt candidate.
- Reviewer: checks calibration, uncertainty, location precision, visibility, and refusal boundaries.
- Witness: records whether the packet stayed public-safe and whether it can be used for computation, display, or only review.

## Acceptance Checks

- Sensor readings and human observations can share one packet model.
- Location precision can be reduced for sensitive places.
- Calibration and uncertainty are visible.
- Public receipts do not expose protected locations or identities.
- Records can be withdrawn, corrected, or marked not-for-computation.

## Refusal Boundaries

- Do not treat a raw sensor reading as a verified claim.
- Do not publish sensitive ecological or cultural locations.
- Do not infer compliance, enforcement, risk pricing, underwriting, or eligibility from these packets.
- Do not assume a device owner or observer has authority to publish place-based knowledge.
- Do not reuse a packet after withdrawal, correction, or not-for-computation status without review.
