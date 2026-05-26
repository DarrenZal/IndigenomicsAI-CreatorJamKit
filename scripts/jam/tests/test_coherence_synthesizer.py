"""Tests for scripts/jam/coherence_synthesizer.py — stdlib unittest, no network."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import coherence_synthesizer as cs  # noqa: E402


def make_persistent_root_with_records(tmpdir: Path) -> Path:
    """Build a persistent_root with two wall records, two build packets,
    and one reviewer-findings file.
    """
    root = tmpdir / "persistent"
    root.mkdir()

    wall_dir = root / "wall" / "witness-records"
    wall_dir.mkdir(parents=True)
    (wall_dir / "20260526T040000-team-orchestrator-spec-a-abc123.md") \
        .write_text(
            "# witness record A\n\n- finding: **built-clean**\n\n"
            "## what we witnessed\n\nThe receipt wall recorded the "
            "build attempt.\n"
        )
    (wall_dir / "20260526T040500-team-orchestrator-spec-b-def456.md") \
        .write_text(
            "# witness record B\n\n- finding: **fixed**\n\n"
            "## what we observed\n\nThe commitment pool route was "
            "surfaced.\n"
        )

    # Build packets (deeply nested per spec, mirroring overnight_loop layout)
    bp_a_dir = root / "rounds" / "round-0001" / "spec-a" / "run-1" / "drafting" / "r1"
    bp_a_dir.mkdir(parents=True)
    (bp_a_dir / "5-agentic-build-packet-v0.json").write_text(json.dumps({
        "team_spec": {
            "title": "Receipt wall story gallery",
            "vision": "A receipt wall that surfaces story cards as witness records.",
            "build_target": "static HTML/JS",
            "spec_id": "spec-a",
        },
    }))
    bp_b_dir = root / "rounds" / "round-0002" / "spec-b" / "run-1" / "drafting" / "r1"
    bp_b_dir.mkdir(parents=True)
    (bp_b_dir / "5-agentic-build-packet-v0.json").write_text(json.dumps({
        "team_spec": {
            "title": "Commitment pool route diagnostic",
            "vision": "A diagnostic that traces commitment pool flow between teams.",
            "build_target": "single-file Python CLI",
        },
    }))

    # Reviewer findings (one round)
    rev_dir = root / "rounds" / "round-0001" / "spec-a" / "run-1"
    (rev_dir / "reviewer-findings.json").write_text(json.dumps({
        "findings": {
            "review_passed": True,
            "halt_publish": False,
            "checks": [
                {"name": "overclaim-vocabulary", "status": "ok", "note": "ok"},
                {"name": "boundary-honored-in-draft", "status": "flag", "note": "thin"},
            ],
            "recommendations": [],
        },
    }))
    return root


def make_persistent_root_empty(tmpdir: Path) -> Path:
    root = tmpdir / "persistent_empty"
    root.mkdir()
    return root


class ClusterTests(unittest.TestCase):
    def test_cluster_witnessing(self):
        vision = "A receipt wall that surfaces witness records for teams."
        self.assertEqual(cs.cluster_for_vision(vision), "WITNESSING")

    def test_cluster_uncategorized_when_no_match(self):
        vision = "A tool that does an unrelated thing entirely."
        self.assertEqual(cs.cluster_for_vision(vision), cs.UNCATEGORIZED)

    def test_cluster_economic_flows(self):
        vision = "Traces commitment pool flow across teams."
        self.assertEqual(cs.cluster_for_vision(vision), "ECONOMIC-FLOWS")

    def test_cluster_handles_non_string(self):
        self.assertEqual(cs.cluster_for_vision(None), cs.UNCATEGORIZED)


class CollectorTests(unittest.TestCase):
    def test_collect_wall_records_walks_subdirs(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))
            records = cs.collect_wall_records(root)
            self.assertEqual(len(records), 2)
            names = sorted(r["name"] for r in records)
            self.assertIn(
                "20260526T040000-team-orchestrator-spec-a-abc123.md", names
            )
            self.assertIn(
                "20260526T040500-team-orchestrator-spec-b-def456.md", names
            )

    def test_collect_wall_records_empty_when_no_wall_dir(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_empty(Path(td))
            records = cs.collect_wall_records(root)
            self.assertEqual(records, [])

    def test_collect_build_packets_uses_rglob(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))
            packets = cs.collect_build_packets(root)
            self.assertEqual(len(packets), 2)
            sids = sorted(p["spec_id"] for p in packets)
            self.assertEqual(sids, ["spec-a", "spec-b"])

    def test_collect_reviewer_findings(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))
            findings = cs.collect_reviewer_findings(root)
            self.assertEqual(len(findings), 1)
            self.assertFalse(findings[0]["halt_publish"])
            self.assertEqual(findings[0]["flags"], 1)


class RenderTests(unittest.TestCase):
    def test_render_with_no_records_returns_empty_section(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_empty(Path(td))
            md = cs.synthesize(
                persistent_root=root,
                gateway="http://unused",
                model="telus-gemma",
                team_key="unused",
            )
            self.assertIn("no published witness records were found", md.lower())
            self.assertIn("## Closing Boundary", md)
            # Critical: gateway should NOT have been called (verified
            # implicitly — no network mock needed because the empty
            # path short-circuits before the call).

    def test_render_includes_closing_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))
            # Patch gateway to return a benign synthesis string so we
            # exercise the full-render path without network.
            with patch.object(
                cs, "call_synthesizer_gateway", return_value="synthesis prose"
            ):
                md = cs.synthesize(
                    persistent_root=root,
                    gateway="http://stub",
                    model="telus-gemma",
                    team_key="stub-key",
                )
            self.assertIn("## Closing Boundary", md)
            self.assertIn(
                "does not establish legitimacy", md
            )

    def test_synthesis_skipped_when_gateway_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))

            def boom(**kwargs):
                raise RuntimeError("upstream 500")

            with patch.object(cs, "call_synthesizer_gateway", side_effect=boom):
                md = cs.synthesize(
                    persistent_root=root,
                    gateway="http://stub",
                    model="telus-gemma",
                    team_key="stub-key",
                )
            # Fallback markdown was produced, without the LLM section
            # but WITH the cluster listing + closing boundary.
            self.assertIn("LLM synthesis was not produced", md)
            self.assertIn("gateway error: upstream 500", md)
            self.assertIn("## Spec themes observed", md)
            self.assertIn("## Closing Boundary", md)

    def test_render_includes_cluster_section(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root_with_records(Path(td))
            with patch.object(
                cs, "call_synthesizer_gateway", return_value="prose"
            ):
                md = cs.synthesize(
                    persistent_root=root,
                    gateway="http://stub",
                    model="telus-gemma",
                    team_key="stub-key",
                )
            # spec-a's vision contains 'witness'/'receipt' -> WITNESSING
            # spec-b's vision contains 'commitment'/'pool'/'flow' -> ECONOMIC-FLOWS
            self.assertIn("### WITNESSING", md)
            self.assertIn("### ECONOMIC-FLOWS", md)
            self.assertIn("`spec-a`", md)
            self.assertIn("`spec-b`", md)

    def test_payload_caps_record_body(self):
        records = [
            {"name": "r1.md", "body": "x" * 5000},
            {"name": "r2.md", "body": "y" * 200},
        ]
        clusters = {}
        payload = cs.build_synthesis_payload(records, clusters)
        self.assertEqual(
            len(payload["wall_records"][0]["body"]),
            cs.PER_RECORD_BODY_CAP,
        )
        self.assertEqual(len(payload["wall_records"][1]["body"]), 200)


if __name__ == "__main__":
    unittest.main()
