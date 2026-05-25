#!/usr/bin/env python3
"""Acceptance test for the Kelp-Bed Stewardship Intelligence Report.

Runs `tool.py` (expected in the same directory as this file) as a subprocess
against small JSON fixtures and checks its stdout / exit behaviour against
`build-instructions.md`.

Standard library only. Run directly:

    python3 acceptance-test.py

On exit it prints one machine-readable line to stdout for the adapter:

    M2LITE_SUMMARY {"tests": N, "passed": N, "failures": [...], "errors": [...]}
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "tool.py")
SUBPROCESS_TIMEOUT = 10


def _write_json(dirpath, name, obj):
    path = os.path.join(dirpath, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return path


def _write_raw(dirpath, name, text):
    path = os.path.join(dirpath, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class StewardshipReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="claude-darren-fixtures-")

    def _run(self, obs_path, act_path):
        return subprocess.run(
            [sys.executable, TOOL, obs_path, act_path],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )

    def _lines(self, stdout):
        return [ln.rstrip() for ln in stdout.rstrip("\n").split("\n")]

    def test_1_worked_example(self):
        obs = _write_json(self.tmp, "obs1.json", {"observations": [
            {"date": "2025-08-01", "site": "Boundary Bay",
             "canopy_percent": 70, "observer_alias": "obs-a",
             "bioregion": "Strait of Georgia"},
            {"date": "2025-09-01", "site": "Boundary Bay",
             "canopy_percent": 50, "observer_alias": "obs-b",
             "bioregion": "Strait of Georgia"},
        ]})
        act = _write_json(self.tmp, "act1.json", {"actions": [
            {"date": "2025-09-15", "bioregion": "Strait of Georgia",
             "action_type": "kelp-count", "site_alias": "site-a"},
            {"date": "2025-10-01", "bioregion": "Strait of Georgia",
             "action_type": "kelp-count", "site_alias": "site-a"},
            {"date": "2025-10-15", "bioregion": "Strait of Georgia",
             "action_type": "beach-cleanup", "site_alias": "site-a"},
        ]})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(self._lines(proc.stdout), [
            "KELP-BED STEWARDSHIP REPORT (1 bioregions)",
            "== Strait of Georgia ==",
            "KELP:",
            "  Boundary Bay: healthy (mean canopy 60%)",
            "ACTIONS:",
            "  kelp-count: 2",
            "  beach-cleanup: 1",
            "",
            "SUMMARY: 1 healthy / 0 declining / 0 stressed sites, 3 stewardship actions",
        ], "worked example from build-instructions.md")

    def test_2_three_conditions_two_bioregions(self):
        obs = _write_json(self.tmp, "obs2.json", {"observations": [
            # Strait of Georgia: one healthy site
            {"date": "2025-08-01", "site": "Boundary Bay",
             "canopy_percent": 80, "observer_alias": "a",
             "bioregion": "Strait of Georgia"},
            # Strait of Georgia: one declining site
            {"date": "2025-08-01", "site": "Lighthouse Park",
             "canopy_percent": 40, "observer_alias": "b",
             "bioregion": "Strait of Georgia"},
            # Juan de Fuca: one stressed site
            {"date": "2025-08-01", "site": "Botanical Beach",
             "canopy_percent": 20, "observer_alias": "c",
             "bioregion": "Juan de Fuca"},
        ]})
        act = _write_json(self.tmp, "act2.json", {"actions": []})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(self._lines(proc.stdout), [
            "KELP-BED STEWARDSHIP REPORT (2 bioregions)",
            "== Juan de Fuca ==",
            "KELP:",
            "  Botanical Beach: stressed (mean canopy 20%)",
            "ACTIONS:",
            "  none",
            "== Strait of Georgia ==",
            "KELP:",
            "  Boundary Bay: healthy (mean canopy 80%)",
            "  Lighthouse Park: declining (mean canopy 40%)",
            "ACTIONS:",
            "  none",
            "",
            "SUMMARY: 1 healthy / 1 declining / 1 stressed sites, 0 stewardship actions",
        ], "bioregions alphabetical; sites alphabetical within KELP block")

    def test_3_actions_only_bioregion(self):
        obs = _write_json(self.tmp, "obs3.json", {"observations": []})
        act = _write_json(self.tmp, "act3.json", {"actions": [
            {"date": "2025-09-01", "bioregion": "Puget Sound",
             "action_type": "planting", "site_alias": "p-a"},
            {"date": "2025-09-15", "bioregion": "Puget Sound",
             "action_type": "planting", "site_alias": "p-a"},
            {"date": "2025-09-20", "bioregion": "Puget Sound",
             "action_type": "eelgrass-survey", "site_alias": "p-b"},
        ]})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(self._lines(proc.stdout), [
            "KELP-BED STEWARDSHIP REPORT (1 bioregions)",
            "== Puget Sound ==",
            "KELP:",
            "  none",
            "ACTIONS:",
            "  planting: 2",
            "  eelgrass-survey: 1",
            "",
            "SUMMARY: 0 healthy / 0 declining / 0 stressed sites, 3 stewardship actions",
        ], "bioregion appears even with no observations; ACTIONS sorted count-desc, alpha-asc")

    def test_4_both_empty(self):
        obs = _write_json(self.tmp, "obs4.json", {"observations": []})
        act = _write_json(self.tmp, "act4.json", {"actions": []})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0 on both-empty; stderr=%r" % proc.stderr)
        self.assertEqual(self._lines(proc.stdout), [
            "KELP-BED STEWARDSHIP REPORT (0 bioregions)",
            "",
            "SUMMARY: 0 healthy / 0 declining / 0 stressed sites, 0 stewardship actions",
        ], "both-empty still prints header + blank line + summary")

    def test_5_unknown_action_type_dropped(self):
        obs = _write_json(self.tmp, "obs5.json", {"observations": []})
        act = _write_json(self.tmp, "act5.json", {"actions": [
            {"date": "2025-09-01", "bioregion": "Strait of Georgia",
             "action_type": "kelp-count", "site_alias": "s"},
            {"date": "2025-09-02", "bioregion": "Strait of Georgia",
             "action_type": "not-a-real-action", "site_alias": "s"},
        ]})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(self._lines(proc.stdout), [
            "KELP-BED STEWARDSHIP REPORT (1 bioregions)",
            "== Strait of Georgia ==",
            "KELP:",
            "  none",
            "ACTIONS:",
            "  kelp-count: 1",
            "",
            "SUMMARY: 0 healthy / 0 declining / 0 stressed sites, 1 stewardship actions",
        ], "unknown action_type values are dropped silently")

    def test_6_malformed_observations_json(self):
        obs = _write_raw(self.tmp, "bad-obs.json", "{not valid json,,,")
        act = _write_json(self.tmp, "act6.json", {"actions": []})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "malformed JSON must still exit 0; stderr=%r" % proc.stderr)
        self.assertTrue(
            proc.stdout.strip().startswith("error:"),
            "malformed JSON: single line starting with 'error:'; got %r" % proc.stdout)

    def test_7_missing_arg(self):
        # Only one path provided
        obs = _write_json(self.tmp, "obs7.json", {"observations": []})
        proc = subprocess.run(
            [sys.executable, TOOL, obs],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )
        self.assertEqual(proc.returncode, 0,
                         "missing arg must still exit 0; stderr=%r" % proc.stderr)
        self.assertTrue(
            proc.stdout.strip().startswith("error:"),
            "missing arg: single line starting with 'error:'; got %r" % proc.stdout)

    def test_8_canopy_rounding_half_away_from_zero(self):
        # mean = 59.5 -> 60 -> healthy
        obs = _write_json(self.tmp, "obs8.json", {"observations": [
            {"date": "2025-08-01", "site": "Edge Site",
             "canopy_percent": 59, "observer_alias": "a",
             "bioregion": "Test Region"},
            {"date": "2025-08-02", "site": "Edge Site",
             "canopy_percent": 60, "observer_alias": "b",
             "bioregion": "Test Region"},
        ]})
        act = _write_json(self.tmp, "act8.json", {"actions": []})
        proc = self._run(obs, act)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        # mean 59.5 -> round half away from zero -> 60 -> healthy (>=60)
        lines = self._lines(proc.stdout)
        self.assertIn("  Edge Site: healthy (mean canopy 60%)", lines,
                      "59.5 mean rounds to 60 (half away from zero); "
                      "displayed mean 60 with healthy condition (>=60). "
                      "Got: %r" % lines)


def _main():
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    summary = {
        "tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": sorted(t.id() for t, _ in result.failures),
        "errors": sorted(t.id() for t, _ in result.errors),
    }
    print("M2LITE_SUMMARY " + json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(_main())
