"""Tests for scripts/jam/chain_overnight.py — stdlib-only."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import chain_overnight as co  # noqa: E402


class LogTests(unittest.TestCase):
    def test_log_appends_to_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            co.log(root, "event_a", foo="bar")
            co.log(root, "event_b", num=42)
            content = (root / "chain-log.jsonl").read_text()
            lines = [l for l in content.splitlines() if l]
            self.assertEqual(len(lines), 2)
            self.assertEqual(json.loads(lines[0])["kind"], "event_a")
            self.assertEqual(json.loads(lines[1])["kind"], "event_b")
            self.assertEqual(json.loads(lines[1])["num"], 42)


class SentinelStopTests(unittest.TestCase):
    def test_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            self.assertIsNone(co.check_sentinel_stop(root))

    def test_returns_content_when_present(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            (root / "CHAIN-STOP").write_text("morning")
            self.assertIn("morning", co.check_sentinel_stop(root))


class PidRunningTests(unittest.TestCase):
    def test_zero_returns_false(self):
        self.assertFalse(co.is_pid_running(0))

    def test_negative_returns_false(self):
        self.assertFalse(co.is_pid_running(-1))

    def test_nonexistent_returns_false(self):
        # PID 99999999 is almost certainly not in use
        self.assertFalse(co.is_pid_running(99999999))

    def test_self_returns_true(self):
        import os
        self.assertTrue(co.is_pid_running(os.getpid()))


class LoopConfigurationTests(unittest.TestCase):
    def test_returns_two_default_configs(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = Path(td) / "test-root"
            configs = co.loop_configurations(3.0, prefix)
            self.assertEqual(len(configs), 2)
            labels = [c["label"] for c in configs]
            self.assertIn("lenient-no-dag", labels)
            self.assertIn("dag-strict", labels)

    def test_configs_have_distinct_persistent_roots(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = Path(td) / "test-root"
            configs = co.loop_configurations(3.0, prefix)
            roots = [str(c["persistent_root"]) for c in configs]
            self.assertEqual(len(roots), len(set(roots)),
                              "persistent_roots should be distinct")

    def test_lenient_uses_threshold_3(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = Path(td) / "test-root"
            configs = co.loop_configurations(3.0, prefix)
            lenient = [c for c in configs if c["label"] == "lenient-no-dag"][0]
            args_str = " ".join(lenient["args"])
            self.assertIn("--planner-threshold 3", args_str)
            self.assertNotIn("--dag-mode", args_str)

    def test_dag_strict_includes_dag_mode(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = Path(td) / "test-root"
            configs = co.loop_configurations(3.0, prefix)
            strict = [c for c in configs if c["label"] == "dag-strict"][0]
            args_str = " ".join(strict["args"])
            self.assertIn("--dag-mode", args_str)
            self.assertIn("--planner-threshold 2", args_str)

    def test_time_budget_propagated(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = Path(td) / "test-root"
            configs = co.loop_configurations(2.5, prefix)
            for c in configs:
                args_str = " ".join(c["args"])
                self.assertIn("--time-budget-hours 2.5", args_str)


if __name__ == "__main__":
    unittest.main()
