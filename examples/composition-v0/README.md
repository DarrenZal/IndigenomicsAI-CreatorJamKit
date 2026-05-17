# Creator Jam Composition v0

Status: simulated manual-first prototype

## Purpose

This folder tests the next Jam milestone:

many offerings -> candidate bundles -> one selected collective bundle -> witnessed build attempt

The point is to learn whether individual offerings can become collective candidate specs without forcing one mega-spec or letting AI decide consent, authority, or reuse readiness.

## Contents

- `contributions/`: eight simulated participant offering folders
- `bundles/`: three candidate collective bundle folders
- `integration-report.md`: facilitator/operator report across all offerings

## Governed Graph Check

Each contribution quick card and bundle file has minimal frontmatter for `doc_id`, `doc_kind`, `status`, and `depends_on`.

Run:

```bash
python3 scripts/jam/validate-composition-dag.py
```

## Rule For This Prototype

Use human/facilitator judgment first. AI can help summarize public or explicitly approved material, but it cannot compute legitimacy, consent, cultural authority, ceremony fit, or permission.
