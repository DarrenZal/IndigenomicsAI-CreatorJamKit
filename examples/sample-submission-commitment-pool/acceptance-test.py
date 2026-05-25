#!/usr/bin/env python3
"""Acceptance test for the Commitment Pool Routing Diagnostic sample."""
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


class PoolRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pool-route-fixtures-")

    def _run(self, input_path):
        return subprocess.run(
            [sys.executable, TOOL, input_path],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )

    def _lines(self, stdout):
        return [ln.rstrip() for ln in stdout.rstrip("\n").split("\n")]

    def test_1_fits_status(self):
        path = _write_json(self.tmp, "fits.json", {
            "pool_id": "p1",
            "offers": [
                {"id": "o1", "contributor": "A", "kind": "labor", "units": 10, "consent_to_route": True},
                {"id": "o2", "contributor": "B", "kind": "labor", "units": 5, "consent_to_route": True},
            ],
            "needs": [
                {"id": "n1", "requester": "Site1", "kind": "labor", "units": 12},
            ],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["POOL ROUTING DIAGNOSTIC — p1",
             "",
             "kind: labor",
             "offered: 15 units (2 contributors consenting)",
             "needed: 12 units (1 requesters)",
             "status: fits",
             "",
             "BLOCKERS: none"],
            "O=15 (10+5), C=2 distinct, D=12, R=1; O>=D so status=fits; no blockers")

    def test_2_short_status(self):
        path = _write_json(self.tmp, "short.json", {
            "pool_id": "p2",
            "offers": [{"id": "o1", "contributor": "A", "kind": "labor", "units": 5, "consent_to_route": True}],
            "needs": [{"id": "n1", "requester": "S1", "kind": "labor", "units": 12}],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("status: short by 7 units", proc.stdout, "12-5=7")

    def test_3_blockers_listed(self):
        path = _write_json(self.tmp, "block.json", {
            "pool_id": "p3",
            "offers": [
                {"id": "o1", "contributor": "Z", "kind": "labor", "units": 5, "consent_to_route": False},
                {"id": "o2", "contributor": "A", "kind": "tools", "units": 3, "consent_to_route": False},
                {"id": "o3", "contributor": "A", "kind": "labor", "units": 4, "consent_to_route": True},
            ],
            "needs": [],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        out = proc.stdout
        # Blockers sorted: A on tools first (contributor A < Z), then Z on labor
        a_pos = out.find("A withheld consent on tools")
        z_pos = out.find("Z withheld consent on labor")
        self.assertTrue(0 <= a_pos < z_pos,
                        "blockers sort by contributor asc; A on tools before Z on labor")

    def test_4_normalization(self):
        path = _write_json(self.tmp, "norm.json", {
            "pool_id": "p4",
            "offers": [
                {"id": "o1", "contributor": "A", "kind": "Field Hours", "units": 4, "consent_to_route": True},
                {"id": "o2", "contributor": "B", "kind": "  field  hours ", "units": 2, "consent_to_route": True},
                {"id": "o3", "contributor": "C", "kind": "FIELD HOURS", "units": 1, "consent_to_route": True},
            ],
            "needs": [],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("kind: field hours", proc.stdout, "normalized form: lowercase + single space")
        self.assertIn("offered: 7 units (3 contributors consenting)", proc.stdout)
        self.assertNotIn("Field Hours", proc.stdout, "no original case forms in output")

    def test_5_drop_bad_data(self):
        path = _write_json(self.tmp, "drop.json", {
            "pool_id": "p5",
            "offers": [
                {"id": "o1", "contributor": "A", "kind": "labor", "units": 5, "consent_to_route": True},
                {"id": "o2", "contributor": "B", "kind": "", "units": 10, "consent_to_route": True},
                {"id": "o3", "contributor": "C", "kind": "labor", "units": "not a number", "consent_to_route": True},
            ],
            "needs": [],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("offered: 5 units (1 contributors consenting)", proc.stdout,
                      "only o1 survives drop rules")

    def test_6_idle_and_no_supply(self):
        path = _write_json(self.tmp, "mixed.json", {
            "pool_id": "p6",
            "offers": [{"id": "o1", "contributor": "A", "kind": "data", "units": 5, "consent_to_route": True}],
            "needs": [{"id": "n1", "requester": "S1", "kind": "boats", "units": 2}],
        })
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        # boats kind: no supply
        self.assertIn("status: no supply", proc.stdout, "needs but no offers for 'boats'")
        # data kind: no demand
        self.assertIn("status: no demand", proc.stdout, "offers but no needs for 'data'")

    def test_7_invalid_json(self):
        path = _write_raw(self.tmp, "broken.json", "{not valid")
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.strip().startswith("error:"))


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
