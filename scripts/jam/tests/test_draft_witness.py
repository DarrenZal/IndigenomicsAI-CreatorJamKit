"""Tests for scripts/jam/draft_witness.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_draft_witness -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import draft_witness as dw  # noqa: E402
from jam.stub_model import StubModelAdapter  # noqa: E402


SAMPLE_BUILD_PACKET = {
    "schema_version": "agentic-build-packet-v0",
    "packet_id": "test-123",
    "team_spec": {
        "team_name": "Test Team",
        "site": "other",
        "vision": "Build a small thing.",
        "spec": "Make a Python CLI that does X.",
        "build_target": "single-file Python CLI",
    },
    "freeze_record": {"frozen": True, "frozen_at": "2026-05-25T00:00:00Z"},
    "allowed_inputs": [{"name": "off-1", "kind": "offering", "content": "..."}],
    "excluded_inputs": [
        {"id": "b-001", "visibility": "marker-only", "boundary": "protected",
         "disallowed_use": ["embed", "send-to-ai"]}
    ],
    "build_instructions": "Build it.",
    "acceptance_criteria": {"description": ["CLI runs", "Output is valid"]},
    "review_checks": ["check 1"],
    "witness_record_seed": {"team": "Test Team", "date": "TBD", "fields": []},
}


SAMPLE_BUILD_ATTEMPT = {
    "model": "telus-gemma",
    "finding": "built-clean",
    "test_outcomes": {"passed": 2, "failed": 0},
}


class WitnessRecordRenderingTests(unittest.TestCase):
    def setUp(self):
        self.drafted_empty = {
            "what_we_brought": "",
            "what_we_attempted": "",
            "what_worked": "",
            "what_did_not_work": "",
            "what_we_learned": "",
            "boundaries_that_remain": "",
        }

    def test_renders_with_empty_drafted_fields_using_fallbacks(self):
        """When model returns empty fields, renderer uses packet-derived defaults."""
        md = dw.render_witness_record_md(
            team_name="Test Team",
            team_id="team-test",
            site="other",
            finding="built-clean",
            build_packet=SAMPLE_BUILD_PACKET,
            build_attempt=SAMPLE_BUILD_ATTEMPT,
            reviewer_findings=None,
            drafted_fields=self.drafted_empty,
        )
        # All sections present
        for section in ("What we brought", "What we attempted", "What worked",
                        "What did not work", "What we learned",
                        "Boundaries that remain", "Receipt"):
            self.assertIn(f"## {section}", md, f"missing section: {section}")
        # Receipt statement present (validator gate)
        self.assertIn("does not establish authority", md.lower())
        # Vision falls through as "what we brought" default
        self.assertIn("Build a small thing.", md)

    def test_renders_with_drafted_fields(self):
        drafted = {
            "what_we_brought": "Custom brought text",
            "what_we_attempted": "Custom attempted text",
            "what_worked": "Custom worked text",
            "what_did_not_work": "Custom did-not-work text",
            "what_we_learned": "Custom learned text",
            "boundaries_that_remain": "Custom boundaries text",
        }
        md = dw.render_witness_record_md(
            team_name="Test Team",
            team_id="team-test",
            site="other",
            finding="built-clean",
            build_packet=SAMPLE_BUILD_PACKET,
            build_attempt=SAMPLE_BUILD_ATTEMPT,
            reviewer_findings=None,
            drafted_fields=drafted,
        )
        for field_text in drafted.values():
            self.assertIn(field_text, md)

    def test_renders_refusal_finding(self):
        md = dw.render_witness_record_md(
            team_name="Test Team",
            team_id="team-test",
            site="other",
            finding="refusal",
            build_packet=SAMPLE_BUILD_PACKET,
            build_attempt=None,
            reviewer_findings=None,
            drafted_fields=self.drafted_empty,
        )
        self.assertIn("finding: **refusal**", md)

    def test_boundaries_section_reflects_excluded_inputs_present(self):
        """When the packet has excluded_inputs, the boundary section
        mentions that marker-only content was held back."""
        md = dw.render_witness_record_md(
            team_name="Test Team", team_id="team-test", site="other",
            finding="built-clean",
            build_packet=SAMPLE_BUILD_PACKET,  # has 1 excluded_inputs entry
            build_attempt=None, reviewer_findings=None,
            drafted_fields=self.drafted_empty,
        )
        self.assertIn("marker-only", md.lower())

    def test_boundaries_section_when_no_excluded_inputs(self):
        packet = {**SAMPLE_BUILD_PACKET, "excluded_inputs": []}
        md = dw.render_witness_record_md(
            team_name="Test Team", team_id="team-test", site="other",
            finding="built-clean",
            build_packet=packet, build_attempt=None, reviewer_findings=None,
            drafted_fields=self.drafted_empty,
        )
        self.assertIn("No marker-only or protected content was named", md)


class StubAdapterIntegrationTests(unittest.TestCase):
    def test_stub_drafts_witness_with_required_fields(self):
        adapter = StubModelAdapter()
        result = dw.call_prompt3(
            adapter,
            SAMPLE_BUILD_PACKET,
            SAMPLE_BUILD_ATTEMPT,
            None,
            "built-clean",
        )
        self.assertEqual(result["model_source"], "stub")
        # Stub returns at least what_we_brought + what_we_attempted
        self.assertIn("stub:", result.get("what_we_brought", "").lower() + result.get("what_we_attempted", "").lower())

    def test_stub_end_to_end_to_validator_clean(self):
        adapter = StubModelAdapter()
        drafted = dw.call_prompt3(adapter, SAMPLE_BUILD_PACKET, None, None, "built-clean")
        md = dw.render_witness_record_md(
            team_name="Stub Team", team_id="team-stub", site="other",
            finding="built-clean",
            build_packet=SAMPLE_BUILD_PACKET,
            build_attempt=None, reviewer_findings=None,
            drafted_fields=drafted,
        )
        tmp = Path(tempfile.mkdtemp()) / "draft.md"
        tmp.write_text(md)
        result = dw.run_validator(tmp)
        self.assertTrue(result["ok"], f"validator failed: {result['output']}")

    def test_valid_findings_set(self):
        self.assertIn("built-clean", dw.VALID_FINDINGS)
        self.assertIn("refusal", dw.VALID_FINDINGS)
        self.assertIn("failed", dw.VALID_FINDINGS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
