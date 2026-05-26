"""Tests for scripts/jam/ceremony_artifact.py — stdlib-only."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import ceremony_artifact as ca  # noqa: E402


class HeadingTransformTests(unittest.TestCase):
    def test_strip_first_heading_removes_h1_and_blank(self):
        text = "# Title\n\nBody here\n## Sub\nMore\n"
        out = ca._strip_first_heading(text)
        self.assertFalse(out.startswith("# Title"))
        self.assertIn("Body here", out)
        self.assertIn("## Sub", out)

    def test_strip_first_heading_noop_when_no_h1(self):
        text = "## Already a sub\nBody\n"
        self.assertEqual(ca._strip_first_heading(text).rstrip(),
                          text.rstrip())

    def test_demote_headings_shifts_by_levels(self):
        text = "# A\n## B\n### C\nBody\n"
        out = ca._demote_headings(text, levels=1)
        self.assertIn("## A", out)
        self.assertIn("### B", out)
        self.assertIn("#### C", out)

    def test_demote_headings_caps_at_six(self):
        text = "##### deep\n"
        out = ca._demote_headings(text, levels=3)
        # 5 + 3 = 8 → capped at 6
        self.assertIn("###### deep", out)
        self.assertNotIn("####### deep", out)

    def test_strip_trailing_closing_boundary(self):
        text = "# Title\n\nBody\n## Closing Boundary\n\nDo not reuse.\n"
        out = ca._strip_trailing_closing_boundary(text)
        self.assertNotIn("Closing Boundary", out)
        self.assertIn("Body", out)

    def test_strip_trailing_boundary_handles_short_form(self):
        text = "# T\nBody\n## Boundary\n\nClosing text.\n"
        out = ca._strip_trailing_closing_boundary(text)
        self.assertNotIn("## Boundary", out)


class WeaveArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_weave_missing_all_artifacts_degrades_gracefully(self):
        md = ca.weave_artifact(self.root)
        self.assertIn("# Closing Ceremony Artifact", md)
        self.assertIn("degraded", md.lower())
        # Boundary always present
        self.assertIn("## Closing Boundary", md)

    def test_weave_with_closing_readout_embeds_it(self):
        (self.root / "closing-witness-readout.md").write_text(
            "# Closing Witness Readout — Run\n\n"
            "## What Passed\n\n- spec-a × model-x\n\n"
            "## Closing Boundary\n\nReceipt stuff.\n"
        )
        md = ca.weave_artifact(self.root)
        # Original heading stripped + content nested under ceremony's h2
        self.assertIn("What Passed", md)
        self.assertIn("spec-a × model-x", md)
        # Only ONE closing boundary remains
        self.assertEqual(md.count("## Closing Boundary"), 1)

    def test_weave_with_coherence_section_demotes_headings(self):
        (self.root / "coherence-synthesis.md").write_text(
            "# Coherence Synthesis\n\n"
            "## Spec themes observed\n\n"
            "Body content here.\n"
        )
        md = ca.weave_artifact(self.root)
        self.assertIn("Spec themes observed", md)
        # The synthesis's own h2 should now be ### (demoted by one)
        self.assertIn("### Spec themes observed", md)

    def test_weave_with_compositions_embeds_proposals(self):
        comp_dir = self.root / "compositions"
        comp_dir.mkdir()
        (comp_dir / "proposal-00-cluster-internal-X.md").write_text(
            "# Composition Proposal — cluster-internal:X\n\n"
            "## Proposed composition\n\n### Title\n\nFoo\n\n"
            "## Boundary\n\nDont reuse.\n"
        )
        md = ca.weave_artifact(self.root)
        self.assertIn("proposal-00-cluster-internal-X.md", md)
        self.assertIn("Proposed composition", md)
        # Boundary inside proposal should be stripped
        # Only one final closing boundary
        self.assertEqual(md.count("## Closing Boundary"), 1)

    def test_weave_when_compositions_missing_offers_fallback_command(self):
        md = ca.weave_artifact(self.root)
        self.assertIn("agent_composer.py", md)

    def test_weave_includes_layered_narrative(self):
        md = ca.weave_artifact(self.root)
        self.assertIn("## 1. What happened", md)
        self.assertIn("## 2. What it means together", md)
        self.assertIn("## 3. What could be composed next", md)


if __name__ == "__main__":
    unittest.main()
