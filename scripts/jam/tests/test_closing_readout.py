"""Tests for scripts/jam/closing_readout.py — stdlib-only (unittest)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import closing_readout as cr  # noqa: E402


def make_persistent_root(tmpdir: Path) -> Path:
    """Build a minimal persistent_root layout with 4 rounds: 2 passed,
    1 review-halted, 1 refused-by-model."""
    root = tmpdir / "persistent"
    root.mkdir()
    log_path = root / "overnight-master-log.jsonl"
    entries = [
        {"kind": "loop_start", "started_at": "2026-05-26T04:00:00Z",
         "specs": ["spec-a", "spec-b"],
         "models": ["telus-qwen", "telus-gemma"]},
        {"kind": "round", "round_idx": 1, "spec_id": "spec-a",
         "model": "telus-qwen", "outcome": "frozen-and-published",
         "telus_calls": 7, "round_dir": str(root / "rounds" / "r1")},
        {"kind": "round", "round_idx": 2, "spec_id": "spec-a",
         "model": "telus-gemma", "outcome": "frozen-and-published",
         "telus_calls": 7, "round_dir": str(root / "rounds" / "r2")},
        {"kind": "round", "round_idx": 3, "spec_id": "spec-b",
         "model": "telus-qwen", "outcome": "review-halted",
         "telus_calls": 8, "round_dir": str(root / "rounds" / "r3")},
        {"kind": "round", "round_idx": 4, "spec_id": "spec-b",
         "model": "telus-gemma",
         "outcome": "refused-by-model: requires cultural authorization",
         "telus_calls": 4, "round_dir": str(root / "rounds" / "r4")},
        {"kind": "loop_finish", "finished_at": "2026-05-26T05:00:00Z",
         "halt_reason": "max_rounds reached (4)",
         "rounds_completed": 4, "wall_seconds": 600,
         "cumulative_telus_calls": 26},
    ]
    log_path.write_text("\n".join(json.dumps(e) for e in entries) + "\n")
    # Wall record
    wall_dir = root / "wall" / "witness-records"
    wall_dir.mkdir(parents=True)
    (wall_dir / "20260526T040000-team-orchestrator-spec-a-abc123.md") \
        .write_text("# witness record")
    (wall_dir / "20260526T040500-team-orchestrator-spec-a-def456.md") \
        .write_text("# witness record")
    return root


class ClosingReadoutTests(unittest.TestCase):
    def test_render_includes_metadata_section(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("## Run metadata", md)
            self.assertIn("rounds attempted: 4", md)
            self.assertIn("cumulative TELUS calls: 26", md)

    def test_render_includes_what_passed_with_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("## What Passed", md)
            self.assertIn("`spec-a` × `telus-qwen`", md)
            self.assertIn("`spec-a` × `telus-gemma`", md)

    def test_render_includes_what_was_partial(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("## What Was Partial", md)
            self.assertIn("review-halted", md)

    def test_render_includes_what_was_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("## What Was Refused", md)
            self.assertIn("requires cultural authorization", md)

    def test_render_includes_closing_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("## Closing Boundary", md)
            self.assertIn("does not establish legitimacy", md)

    def test_render_walks_wall_records(self):
        with tempfile.TemporaryDirectory() as td:
            root = make_persistent_root(Path(td))
            md = cr.render_readout(root)
            self.assertIn("Wall records", md)
            self.assertIn(
                "20260526T040000-team-orchestrator-spec-a-abc123.md", md)

    def test_bucket_classification(self):
        self.assertEqual(cr.bucket_for("frozen-and-published"), "passed")
        self.assertEqual(cr.bucket_for("review-halted"), "partial")
        self.assertEqual(cr.bucket_for("doesnt-fit-yet-no-packet"), "partial")
        self.assertEqual(
            cr.bucket_for("refused-by-model: requires X"), "refused")
        self.assertEqual(cr.bucket_for("refused-by-gatekeeper"), "refused")
        self.assertEqual(cr.bucket_for("subprocess-timeout"), "failed")
        self.assertEqual(cr.bucket_for("loop-error"), "failed")

    def test_handles_missing_log_gracefully(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "empty"
            root.mkdir()
            md = cr.render_readout(root)
            self.assertIn("rounds attempted: 0", md)
            self.assertIn("## Closing Boundary", md)


if __name__ == "__main__":
    unittest.main()
