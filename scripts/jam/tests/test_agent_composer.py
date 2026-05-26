"""Tests for scripts/jam/agent_composer.py — stdlib-only (unittest)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import agent_composer as ac  # noqa: E402


SAMPLE_COMPONENTS_WITNESSING_PAIR = [
    {"spec_id": "witness-record-interop-profile", "cluster": "WITNESSING",
     "title": "Witness Record Interop",
     "vision": "Portable witness records with receipts.",
     "spec": "...", "build_target": "single-file Python CLI",
     "acceptance_criteria": ["A1", "A2"]},
    {"spec_id": "receipt-wall-story-gallery", "cluster": "WITNESSING",
     "title": "Receipt Wall Gallery",
     "vision": "Static gallery of receipts.",
     "spec": "...", "build_target": "static HTML/JS",
     "acceptance_criteria": ["B1"]},
]

SAMPLE_COMPONENTS_CROSS_CLUSTER = [
    {"spec_id": "witness-record-interop-profile", "cluster": "WITNESSING",
     "title": "Interop", "vision": "v", "spec": "s",
     "build_target": "CLI", "acceptance_criteria": []},
    {"spec_id": "claims-evidence-coherence-report", "cluster": "CLAIMS",
     "title": "Claims Coherence", "vision": "v", "spec": "s",
     "build_target": "CLI", "acceptance_criteria": []},
]


class PickCompositionTuplesTests(unittest.TestCase):
    def test_cluster_internal_pairs_returned(self):
        tuples = ac.pick_composition_tuples(
            SAMPLE_COMPONENTS_WITNESSING_PAIR, max_proposals=8,
        )
        self.assertEqual(len(tuples), 1)
        intent, comps = tuples[0]
        self.assertTrue(intent.startswith("cluster-internal:WITNESSING"))
        self.assertEqual(len(comps), 2)

    def test_cross_cluster_pair_returned(self):
        tuples = ac.pick_composition_tuples(
            SAMPLE_COMPONENTS_CROSS_CLUSTER, max_proposals=8,
        )
        # Should pick the WITNESSING + CLAIMS affinity cross-cluster
        intents = [t[0] for t in tuples]
        self.assertTrue(
            any(intent.startswith("cross-cluster") for intent in intents),
            f"no cross-cluster proposal in {intents}",
        )

    def test_respects_max_proposals(self):
        # Build N specs in one cluster
        comps = [
            {"spec_id": f"spec-{i}", "cluster": "WITNESSING",
             "title": f"t{i}", "vision": "v", "spec": "s",
             "build_target": "CLI", "acceptance_criteria": []}
            for i in range(8)
        ]
        tuples = ac.pick_composition_tuples(comps, max_proposals=3)
        self.assertLessEqual(len(tuples), 3)

    def test_no_proposals_when_fewer_than_two_components(self):
        comps = [{"spec_id": "alone", "cluster": "WITNESSING",
                   "title": "t", "vision": "v", "spec": "s",
                   "build_target": "CLI", "acceptance_criteria": []}]
        tuples = ac.pick_composition_tuples(comps)
        # cluster-internal needs >= 2 in cluster; no cross-cluster
        # affinity with only one cluster; result should be []
        self.assertEqual(tuples, [])


class RenderProposalMDTests(unittest.TestCase):
    def test_render_with_valid_parsed_includes_sections(self):
        parsed = {
            "title": "Composed Witness Tool",
            "vision": "A tool that surfaces witness records into a gallery.",
            "spec": "Stitches the interop CLI + the gallery renderer.",
            "build_target": "multi-file Python package",
            "acceptance_criteria_draft": ["ac1", "ac2"],
            "composition_seams": ["interop emits JSON; gallery consumes it"],
            "composition_caveats": ["receipt statements must be preserved"],
        }
        md = ac.render_proposal_md(
            "cluster-internal:WITNESSING",
            SAMPLE_COMPONENTS_WITNESSING_PAIR,
            parsed, "raw", "test-model",
        )
        self.assertIn("## Proposed composition", md)
        self.assertIn("Composed Witness Tool", md)
        self.assertIn("Composition seams", md)
        self.assertIn("Composition caveats", md)
        self.assertIn("## Boundary", md)

    def test_render_with_refusal_records_as_refusal(self):
        parsed = {"refusal": "components operate on incompatible domains"}
        md = ac.render_proposal_md(
            "cross-cluster:WITNESSING+ASPIRATIONS",
            SAMPLE_COMPONENTS_CROSS_CLUSTER,
            parsed, "raw", "test-model",
        )
        self.assertIn("Composition refused", md)
        self.assertIn("incompatible domains", md)

    def test_render_with_parse_failure_preserves_raw(self):
        md = ac.render_proposal_md(
            "cluster-internal:WITNESSING",
            SAMPLE_COMPONENTS_WITNESSING_PAIR,
            None, "the model returned non-JSON garbage",
            "test-model",
        )
        self.assertIn("parse failure", md)
        self.assertIn("non-JSON garbage", md)

    def test_render_always_includes_closing_boundary(self):
        md = ac.render_proposal_md(
            "cluster-internal:WITNESSING",
            SAMPLE_COMPONENTS_WITNESSING_PAIR,
            {"title": "x"}, "raw", "model",
        )
        self.assertIn("## Boundary", md)
        self.assertIn("not authority", md)


class DiscoverComponentsTests(unittest.TestCase):
    def test_discover_returns_empty_when_no_wall(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            self.assertEqual(ac.discover_components(root), [])


class ComposeEndToEndOfflineTests(unittest.TestCase):
    def test_compose_no_components_writes_stub(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            out_dir = root / "compositions"
            summary = ac.compose(
                persistent_root=root,
                gateway="http://localhost:9",  # unreachable
                team_key="fake",
                model="telus-gemma",
                out_dir=out_dir,
                max_proposals=4,
            )
            self.assertEqual(summary["proposals_attempted"], 0)
            self.assertTrue((out_dir / "no-compositions.md").exists())


class ComposerSystemPromptTests(unittest.TestCase):
    def test_system_prompt_includes_anti_overclaim_discipline(self):
        self.assertIn("verb discipline", ac.COMPOSER_SYSTEM.lower())
        self.assertIn("certified", ac.COMPOSER_SYSTEM)
        self.assertIn("refusal", ac.COMPOSER_SYSTEM.lower())

    def test_system_prompt_requires_composition_seams_and_caveats(self):
        self.assertIn("composition_seams", ac.COMPOSER_SYSTEM)
        self.assertIn("composition_caveats", ac.COMPOSER_SYSTEM)


if __name__ == "__main__":
    unittest.main()
