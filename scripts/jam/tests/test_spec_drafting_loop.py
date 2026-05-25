"""Tests for scripts/jam/spec_drafting_loop.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_spec_drafting_loop -v

Tests cover:
- Stub model adapter returns deterministic responses by prompt name
- parse_offering handles md + json
- boundary_leak_check detects markers outside boundaries[]
- boundary_leak_check ALLOWS markers inside boundaries[]
- Loop end-to-end with stub adapter and --confirm-freeze produces
  team-submission-v0.md + agentic-build-packet-v0.json + freeze record
- Loop without --confirm-freeze stops at stage 4 (draft-only)
- Build packet schema matches agentic-build-packet-v0 template
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Make `jam` importable when running from kit root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import spec_drafting_loop as loop  # noqa: E402
from jam.stub_model import StubModelAdapter  # noqa: E402


class StubModelTests(unittest.TestCase):
    def test_deterministic_same_input_same_output(self):
        a = StubModelAdapter()
        r1 = a.complete("spec-drafter", {"offering": {"title": "T", "body": "B"}})
        r2 = a.complete("spec-drafter", {"offering": {"title": "T", "body": "B"}})
        self.assertEqual(r1["seed"], r2["seed"])
        self.assertEqual(r1["draft_spec"]["title"], r2["draft_spec"]["title"])

    def test_unknown_prompt_rejected(self):
        a = StubModelAdapter()
        with self.assertRaises(ValueError):
            a.complete("some-fake-prompt", {})

    def test_all_4_prompts_succeed(self):
        a = StubModelAdapter()
        names = ["spec-drafter", "boundary-checker", "collaboration-facilitator", "witness-drafter"]
        for n in names:
            payload = (
                {"offering": {"title": "T", "body": "B"}} if n == "spec-drafter"
                else {"draft_spec": {"title": "T"}} if n == "boundary-checker"
                else {"proposed_bundle": {"composes": [{"team_id": "A"}, {"team_id": "B"}]}} if n == "collaboration-facilitator"
                else {"team": {"name": "T"}, "build_outcome": "ok"}
            )
            r = a.complete(n, payload)
            self.assertEqual(r["model_source"], "stub")
            self.assertIn("stub:", str(r))


class OfferingParserTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_parse_json(self):
        p = Path(self.tmp) / "o.json"
        p.write_text(json.dumps({"id": "x", "title": "X", "body": "B"}))
        result = loop.parse_offering(p)
        self.assertEqual(result["id"], "x")

    def test_parse_md_with_frontmatter(self):
        p = Path(self.tmp) / "off.md"
        p.write_text("---\ntitle: My Offering\ncontributor: alice\n---\n\nBody text here.\n")
        r = loop.parse_offering(p)
        self.assertEqual(r["title"], "My Offering")
        self.assertEqual(r["contributor_display"], "alice")
        self.assertIn("Body text here", r["body"])

    def test_parse_md_no_frontmatter(self):
        p = Path(self.tmp) / "off.md"
        p.write_text("Just body, no frontmatter.\n")
        r = loop.parse_offering(p)
        self.assertEqual(r["title"], "off")
        self.assertIn("Just body", r["body"])


class BoundaryLeakCheckTests(unittest.TestCase):
    def test_no_leak_passes(self):
        spec = {"vision": "clean spec", "spec": "clean", "boundaries": []}
        self.assertIsNone(loop.boundary_leak_check(spec))

    def test_marker_inside_boundaries_ok(self):
        # A marker INSIDE the boundaries list is the marker's definition,
        # not a leak.
        spec = {
            "vision": "clean spec",
            "spec": "no leak",
            "boundaries": [
                {"boundary_type": "protected", "marker_text": "This is [PROTECTED]"},
            ],
        }
        self.assertIsNone(loop.boundary_leak_check(spec))

    def test_marker_in_vision_rejected(self):
        spec = {
            "vision": "leaking [PROTECTED] content into vision",
            "spec": "clean",
            "boundaries": [],
        }
        result = loop.boundary_leak_check(spec)
        self.assertIsNotNone(result)
        self.assertIn("[PROTECTED]", result)


class LoopEndToEndTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Create a minimal offering
        self.offering = Path(self.tmp) / "off.md"
        self.offering.write_text(
            "---\ntitle: Test Offering\n---\n\nSmall test offering body.\n"
        )
        self.out_dir = Path(self.tmp) / "runs"

    def _run(self, confirm_freeze):
        # Capture sys.exit cleanly
        try:
            loop.run_loop(
                offering_files=[self.offering],
                out_dir=self.out_dir,
                adapter=StubModelAdapter(),
                confirm_freeze=confirm_freeze,
                team_name="Test Team",
                team_site="other",
            )
        except SystemExit:
            pass
        # Find the run dir
        run_dirs = list(self.out_dir.iterdir())
        self.assertEqual(len(run_dirs), 1, f"expected 1 run dir, got {run_dirs}")
        return run_dirs[0]

    def test_loop_without_freeze_stops_at_stage_4(self):
        run_dir = self._run(confirm_freeze=False)
        files = {f.name for f in run_dir.iterdir()}
        self.assertIn("1-offering.json", files)
        self.assertIn("2-draft-spec.json", files)
        self.assertIn("3-annotated-spec.json", files)
        self.assertNotIn("5-team-submission-v0.md", files)
        self.assertNotIn("5-agentic-build-packet-v0.json", files)
        run = json.loads((run_dir / "run.json").read_text())
        self.assertIn("draft-only", run["outcome"])

    def test_loop_with_freeze_emits_packet(self):
        run_dir = self._run(confirm_freeze=True)
        files = {f.name for f in run_dir.iterdir()}
        self.assertIn("5-team-submission-v0.md", files)
        self.assertIn("5-agentic-build-packet-v0.json", files)
        self.assertIn("5-freeze-record.json", files)
        run = json.loads((run_dir / "run.json").read_text())
        self.assertEqual(run["outcome"], "frozen-build-packet-ready")
        # Check packet schema
        packet = json.loads((run_dir / "5-agentic-build-packet-v0.json").read_text())
        self.assertEqual(packet["schema_version"], "agentic-build-packet-v0")
        for required in ["packet_id", "team_spec", "freeze_record", "allowed_inputs",
                         "excluded_inputs", "build_instructions", "acceptance_criteria",
                         "review_checks", "witness_record_seed"]:
            self.assertIn(required, packet, f"build packet missing {required}")

    def test_freeze_record_marks_frozen(self):
        run_dir = self._run(confirm_freeze=True)
        fr = json.loads((run_dir / "5-freeze-record.json").read_text())
        self.assertTrue(fr["frozen"])
        self.assertIn("autonomous", fr["frozen_by"].lower())
        # The frozen-by note should explicitly say this is for stub/demo
        # and does not grant authority
        self.assertIn("authority", fr["note"].lower())


class GatewayAdapterParsingTests(unittest.TestCase):
    """Phase-3.5 additions: structured-parse of gateway responses."""

    def test_strip_json_fences_with_language_tag(self):
        text = '```json\n{"key": "value"}\n```'
        self.assertEqual(loop._strip_json_fences(text), '{"key": "value"}')

    def test_strip_json_fences_without_language_tag(self):
        text = '```\n{"key": "value"}\n```'
        self.assertEqual(loop._strip_json_fences(text), '{"key": "value"}')

    def test_strip_json_fences_no_fences(self):
        text = '{"key": "value"}'
        self.assertEqual(loop._strip_json_fences(text), '{"key": "value"}')

    def test_try_parse_json_ok(self):
        text = '```json\n{"vision": "v", "spec": "s"}\n```'
        parsed = loop._try_parse_json(text)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["vision"], "v")

    def test_try_parse_json_returns_none_on_garbage(self):
        text = "just random text, no json"
        self.assertIsNone(loop._try_parse_json(text))

    def test_try_parse_json_normalizes_non_breaking_hyphen(self):
        # gpt-oss emits U+2011 (non-breaking hyphen) — must not break parse
        text = '```json\n{"vision": "team‑kelp‑observers"}\n```'
        parsed = loop._try_parse_json(text)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["vision"], "team-kelp-observers")


class FreezeSanityRefusalTests(unittest.TestCase):
    """Phase-3.5 additions: refuse-to-freeze on null/empty content."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out_dir = Path(self.tmp) / "runs"

    def test_freeze_refuses_when_annotated_spec_not_dict(self):
        """When the gateway adapter fails to parse, annotated_spec falls
        back to a string. The loop must refuse to freeze."""

        class FailingAdapter:
            """Returns gateway-shape responses where annotated_spec is missing
            (string fall-through case)."""
            def complete(self, prompt_name, payload):
                if prompt_name == "spec-drafter":
                    return {
                        "model_source": "gateway",
                        "model_label": "test",
                        "stage": prompt_name,
                        "raw_content": "not json",
                        "_parsed_ok": False,
                        # NOTE: no draft_spec field — fall-through
                    }
                if prompt_name == "boundary-checker":
                    return {
                        "model_source": "gateway",
                        "model_label": "test",
                        "stage": prompt_name,
                        "raw_content": "not json either",
                        "_parsed_ok": False,
                        # NOTE: no annotated_spec field
                    }
                return {}

        offering = Path(self.tmp) / "o.md"
        offering.write_text("---\ntitle: T\n---\nbody\n")
        try:
            loop.run_loop(
                offering_files=[offering],
                out_dir=self.out_dir,
                adapter=FailingAdapter(),
                confirm_freeze=True,
                team_name="Test", team_site="other",
            )
        except SystemExit:
            pass
        run_dirs = list(self.out_dir.iterdir())
        run = json.loads((run_dirs[0] / "run.json").read_text())
        # Must NOT have a frozen-build-packet-ready outcome
        self.assertNotEqual(run["outcome"], "frozen-build-packet-ready")
        self.assertIn("doesn't-fit-yet", run["outcome"])

    def test_freeze_refuses_when_vision_and_spec_both_empty(self):
        """Parsed dict but both fields empty — refuse."""

        class EmptyAdapter:
            def complete(self, prompt_name, payload):
                if prompt_name == "spec-drafter":
                    return {
                        "model_source": "gateway",
                        "stage": prompt_name,
                        "raw_content": "{}",
                        "draft_spec": {"vision": "", "spec": ""},
                    }
                if prompt_name == "boundary-checker":
                    return {
                        "model_source": "gateway",
                        "stage": prompt_name,
                        "raw_content": "{}",
                        "annotated_spec": {"vision": "", "spec": "", "boundaries": []},
                    }
                return {}

        offering = Path(self.tmp) / "o.md"
        offering.write_text("---\ntitle: T\n---\nbody\n")
        try:
            loop.run_loop(
                offering_files=[offering],
                out_dir=self.out_dir,
                adapter=EmptyAdapter(),
                confirm_freeze=True,
                team_name="Test", team_site="other",
            )
        except SystemExit:
            pass
        run_dirs = list(self.out_dir.iterdir())
        run = json.loads((run_dirs[0] / "run.json").read_text())
        self.assertNotEqual(run["outcome"], "frozen-build-packet-ready")
        self.assertIn("doesn't-fit-yet", run["outcome"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
