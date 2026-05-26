"""Tests for orchestrator mesh-mode + wall-root wire-in.

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_orchestrator_mesh -v
"""

import inspect
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import orchestrator as orch  # noqa: E402


KIT_ROOT = Path(__file__).resolve().parents[3]


class AttemptSpecSignatureTests(unittest.TestCase):
    def test_attempt_spec_has_mesh_mode_param(self):
        sig = inspect.signature(orch.attempt_spec)
        self.assertIn("mesh_mode", sig.parameters)
        self.assertFalse(sig.parameters["mesh_mode"].default)

    def test_attempt_spec_has_wall_root_param(self):
        sig = inspect.signature(orch.attempt_spec)
        self.assertIn("wall_root", sig.parameters)
        self.assertIsNone(sig.parameters["wall_root"].default)


class CLIFlagsPresent(unittest.TestCase):
    def _run_help(self):
        proc = subprocess.run(
            ["python3", str(KIT_ROOT / "scripts/jam/orchestrator.py"),
             "run", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.stdout + proc.stderr

    def test_help_lists_mesh_mode_flag(self):
        out = self._run_help()
        self.assertIn("--mesh-mode", out)

    def test_help_lists_wall_root_flag(self):
        out = self._run_help()
        self.assertIn("--wall-root", out)


class ReviewerImportedAtModuleLevel(unittest.TestCase):
    def test_reviewer_review_function_imported(self):
        self.assertTrue(hasattr(orch, "reviewer_review"))
        self.assertTrue(callable(orch.reviewer_review))


class WallRootDefaultBehavior(unittest.TestCase):
    """Reading source confirms the default fallback is out_dir/wall when
    wall_root is None — but the explicit flag substitutes when provided.
    This is a smoke-level sanity check; full end-to-end behavior is in
    the smoke-test phase."""

    def test_source_has_effective_wall_root_branch(self):
        src = Path(orch.__file__).read_text()
        self.assertIn("effective_wall_root", src)
        self.assertIn(
            "wall_root if wall_root is not None",
            src,
            "wall_root override branch missing — explicit flag wouldn't work",
        )


if __name__ == "__main__":
    unittest.main()
