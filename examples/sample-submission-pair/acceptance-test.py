#!/usr/bin/env python3
"""Acceptance test for the Kelp Bed Watch sample build attempt.

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


class KelpBedWatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="kelp-watch-fixtures-")

    def _run(self, input_path):
        return subprocess.run(
            [sys.executable, TOOL, input_path],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )

    def _lines(self, stdout):
        # exact lines: trailing newlines removed, each line right-stripped;
        # internal blank lines are preserved as ""
        return [ln.rstrip() for ln in stdout.rstrip("\n").split("\n")]

    def test_1_happy_path_two_sites_two_indicators(self):
        path = _write_json(self.tmp, "happy.json", {"observations": [
            {"id": "a", "site": "Spanish Banks", "date": "2026-04-20", "indicator": "canopy_percent", "value": 22.3},
            {"id": "b", "site": "Spanish Banks", "date": "2026-05-04", "indicator": "canopy_percent", "value": 25.7},
            {"id": "c", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "shoot_density", "value": 100},
            {"id": "d", "site": "Boundary Bay", "date": "2026-04-26", "indicator": "shoot_density", "value": 140},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["KELP BED WATCH (4 observations across 2 sites)",
             "== boundary bay ==",
             "shoot_density: mean 120.00, n=2",
             "",
             "== spanish banks ==",
             "canopy_percent: mean 24.00, n=2",
             "",
             "SUMMARY: 4 observations, 2 sites, 2026-04-12 .. 2026-05-04"],
            "header, sites alphabetical, indicators alphabetical within site, "
            "means rounded to 2 decimals, n=<count>, SUMMARY with date range")

    def test_2_normalization_collapses_to_one_bucket(self):
        path = _write_json(self.tmp, "normalize.json", {"observations": [
            {"id": "a", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "Canopy_Percent", "value": 38.5},
            {"id": "b", "site": "boundary bay", "date": "2026-04-26", "indicator": "canopy_percent", "value": 41.0},
            {"id": "c", "site": "  Boundary  Bay ", "date": "2026-05-10", "indicator": "CANOPY_PERCENT", "value": 44.2},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["KELP BED WATCH (3 observations across 1 sites)",
             "== boundary bay ==",
             "canopy_percent: mean 41.23, n=3",
             "",
             "SUMMARY: 3 observations, 1 sites, 2026-04-12 .. 2026-05-10"],
            "case + whitespace variants normalize to one bucket; (38.5+41+44.2)/3"
            "=41.233... -> 41.23")

    def test_3_drop_rules(self):
        path = _write_json(self.tmp, "drops.json", {"observations": [
            {"id": "a", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": 38.5},
            {"id": "b", "site": "", "date": "2026-04-12", "indicator": "canopy_percent", "value": 50.0},
            {"id": "c", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "  ", "value": 50.0},
            {"id": "d", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": "string"},
            {"id": "e", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": None},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["KELP BED WATCH (1 observations across 1 sites)",
             "== boundary bay ==",
             "canopy_percent: mean 38.50, n=1",
             "",
             "SUMMARY: 1 observations, 1 sites, 2026-04-12 .. 2026-04-12"],
            "drop: empty site, empty indicator, non-numeric value, null value; "
            "only the one clean observation survives")

    def test_4_empty_observations(self):
        path = _write_json(self.tmp, "empty.json", {"observations": []})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["KELP BED WATCH (0 observations across 0 sites)",
             "SUMMARY: 0 observations, 0 sites, no dates"],
            "empty observations: header line, then SUMMARY directly (no site "
            "blocks, no blank line in between), 'no dates' for the range")

    def test_5_invalid_json_exit_zero(self):
        path = _write_raw(self.tmp, "broken.json", "{this is not valid json,,,")
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "malformed JSON must still exit 0; stderr=%r" % proc.stderr)
        self.assertTrue(
            proc.stdout.strip().startswith("error:"),
            "malformed JSON must print a single line beginning with 'error:' "
            "to stdout; got: %r" % proc.stdout)

    def test_6_indicator_alphabetical_within_site(self):
        path = _write_json(self.tmp, "alpha.json", {"observations": [
            {"id": "a", "site": "Site A", "date": "2026-04-01", "indicator": "zeta", "value": 1.0},
            {"id": "b", "site": "Site A", "date": "2026-04-01", "indicator": "alpha", "value": 2.0},
            {"id": "c", "site": "Site A", "date": "2026-04-01", "indicator": "mu", "value": 3.0},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0,
                         "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["KELP BED WATCH (3 observations across 1 sites)",
             "== site a ==",
             "alpha: mean 2.00, n=1",
             "mu: mean 3.00, n=1",
             "zeta: mean 1.00, n=1",
             "",
             "SUMMARY: 3 observations, 1 sites, 2026-04-01 .. 2026-04-01"],
            "indicators sort alphabetically within a site, regardless of input "
            "order")


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
