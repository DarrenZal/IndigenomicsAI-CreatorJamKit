"""Tests for scripts/jam/agent_reviewer.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_agent_reviewer -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import agent_reviewer as ar  # noqa: E402


CLEAN_DRAFT = """# Witness Record

## What we brought
A small idea.

## What we attempted
A short prototype attempt.

## What worked
We observed the output formed.

## What did not work
Some rough edges remained.

## What we learned
We recorded some lessons.

## Boundaries that remain
Marker-only content was held back; details not embedded.

## Receipt
This record does not establish authority.
"""


OVERCLAIM_DRAFT = """# Witness Record

## What we brought
A serious idea.

## What we attempted
A run-through.

## What worked
This build is certified by our team and authorized for release.

## What did not work
N/A.

## What we learned
A lot.

## Boundaries that remain
Marker-only content was held back.

## Receipt
This record does not establish authority.
"""


SAMPLE_BUILD_PACKET = {
    "schema_version": "agentic-build-packet-v0",
    "packet_id": "test-rev-001",
    "team_spec": {
        "team_name": "Test Team",
        "site": "other",
        "vision": "Build a small thing.",
        "spec": "Make a Python CLI that does X.",
        "build_target": "single-file Python CLI",
    },
    "freeze_record": {"frozen": True, "frozen_at": "2026-05-25T00:00:00Z"},
    "allowed_inputs": [],
    "excluded_inputs": [],
    "build_instructions": "Build it.",
    "acceptance_criteria": {"description": ["CLI runs"]},
    "review_checks": [],
    "witness_record_seed": {"team": "Test Team", "date": "TBD", "fields": []},
}


class StubReviewerTests(unittest.TestCase):
    def test_stub_clean_draft_passes(self):
        out = ar.call_reviewer_stub({"witness_draft": CLEAN_DRAFT})
        normalized = ar.normalize_findings(out["parsed"])
        self.assertIs(normalized["review_passed"], True)
        self.assertIs(normalized["halt_publish"], False)

    def test_stub_overclaim_draft_halts(self):
        out = ar.call_reviewer_stub({"witness_draft": OVERCLAIM_DRAFT})
        normalized = ar.normalize_findings(out["parsed"])
        self.assertIs(normalized["halt_publish"], True)
        overclaim_halts = [
            c for c in normalized["checks"]
            if c["name"] == "overclaim-vocabulary" and c["status"] == "halt"
        ]
        self.assertGreaterEqual(
            len(overclaim_halts), 1,
            f"expected an overclaim-vocabulary halt; got {normalized['checks']}",
        )


class NormalizeFindingsTests(unittest.TestCase):
    def test_normalize_findings_handles_none(self):
        result = ar.normalize_findings(None)
        self.assertIsInstance(result, dict)
        self.assertIs(result["review_passed"], False)
        parse_failed = [
            c for c in result["checks"]
            if c["name"] == "reviewer-parse-failed"
        ]
        self.assertEqual(len(parse_failed), 1)
        self.assertEqual(parse_failed[0]["status"], "flag")

    def test_normalize_findings_handles_refusal_key(self):
        result = ar.normalize_findings(
            {"refusal": "cultural authorization required"}
        )
        self.assertIs(result["halt_publish"], True)
        self.assertIn("refusal", result)
        refusal_checks = [
            c for c in result["checks"] if c["name"] == "reviewer-refusal"
        ]
        self.assertGreaterEqual(len(refusal_checks), 1)

    def test_normalize_findings_backfills_missing_checks(self):
        result = ar.normalize_findings({
            "review_passed": True,
            "halt_publish": False,
            "checks": [
                {"name": "overclaim-vocabulary", "status": "ok", "note": ""},
            ],
        })
        check_names = {c["name"] for c in result["checks"]}
        required = set(ar.REQUIRED_CHECK_NAMES)
        self.assertTrue(
            required.issubset(check_names),
            f"missing required check names: {required - check_names}",
        )
        # Backfilled ones should be at status 'ok'
        for c in result["checks"]:
            if c["name"] in (required - {"overclaim-vocabulary"}):
                self.assertEqual(c["status"], "ok")

    def test_normalize_findings_halt_propagates(self):
        result = ar.normalize_findings({
            "review_passed": True,
            "halt_publish": False,
            "checks": [
                {"name": "x", "status": "halt", "note": "bad"},
            ],
        })
        self.assertIs(result["halt_publish"], True)
        self.assertIs(result["review_passed"], False)


class BuildPayloadTests(unittest.TestCase):
    def test_build_payload_bounds_witness_draft_size(self):
        payload = ar.build_payload({}, None, "A" * 20000)
        self.assertLessEqual(len(payload["witness_draft"]), 8000)


class ReviewEndToEndTests(unittest.TestCase):
    def test_review_function_with_stub_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            packet_path = tmp_path / "build_packet.json"
            draft_path = tmp_path / "witness-draft.md"
            packet_path.write_text(json.dumps(SAMPLE_BUILD_PACKET))
            draft_path.write_text(CLEAN_DRAFT)

            record = ar.review(
                build_packet_path=packet_path,
                witness_draft_path=draft_path,
                build_attempt_path=None,
                model_source="stub",
                gateway=None,
                team_key=None,
                model=None,
            )
            self.assertIn("findings", record)
            self.assertIn("raw_content", record)
            self.assertEqual(record["schema"], "reviewer-findings-v0")


class ReviewerPromptCarveOutTests(unittest.TestCase):
    """Verify REVIEWER_SYSTEM has the finding-line carve-out.

    Sharpened after supervised-run round 1 revealed the live model
    was halting on the literal word 'failed' appearing in the
    finding metadata line — a real false-positive."""

    def test_prompt_includes_finding_line_carveout(self):
        self.assertIn("finding-line", ar.REVIEWER_SYSTEM.lower())
        self.assertIn("metadata", ar.REVIEWER_SYSTEM.lower())

    def test_prompt_lists_failed_in_standard_outcomes(self):
        self.assertIn("'failed'", ar.REVIEWER_SYSTEM)

    def test_prompt_includes_carveout_example(self):
        self.assertIn("- finding: **failed**", ar.REVIEWER_SYSTEM)


if __name__ == "__main__":
    unittest.main()
