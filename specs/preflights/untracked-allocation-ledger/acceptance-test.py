#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "tool.py")
TIMEOUT = 10


def _write(d, n, o):
    p = os.path.join(d, n)
    with open(p, "w") as f:
        if isinstance(o, str): f.write(o)
        else: json.dump(o, f)
    return p


class UntrackedLedgerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="ual-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_all_public(self):
        p = _write(self.tmp, "pub.json", {"allocations": [
            {"allocation_id": "a1", "allocation_type": "money", "public_summary": "x",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R", "funder": "F", "amount": 100, "unit": "CAD",
             "not_tracked_reason": None, "withdrawn": False},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("UNTRACKED ALLOCATION LEDGER (1 public / 0 not-tracked / 0 withdrawn of 1 total)", proc.stdout)
        self.assertIn("recipient: R", proc.stdout)
        self.assertIn("funder: F", proc.stdout)
        self.assertIn("amount: 100 CAD", proc.stdout)

    def test_2_private_recipient(self):
        p = _write(self.tmp, "priv.json", {"allocations": [
            {"allocation_id": "a1", "allocation_type": "time", "public_summary": "x",
             "recipient_visibility": "private", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "PRIVATE_NAME", "funder": "F", "amount": 1, "unit": "hour",
             "not_tracked_reason": None, "withdrawn": False},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("PRIVATE_NAME", proc.stdout, "private recipient must not leak")
        self.assertNotIn("recipient:", proc.stdout, "no recipient line when private")
        self.assertIn("funder: F", proc.stdout)

    def test_3_not_tracked_suppresses_all(self):
        p = _write(self.tmp, "ntb.json", {"allocations": [
            {"allocation_id": "a1", "allocation_type": "care", "public_summary": "an act of care",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "PUBLIC_R", "funder": "PUBLIC_F", "amount": 5, "unit": "hours",
             "not_tracked_reason": "by design", "withdrawn": False},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        # Visibility says public but not-tracked-by-design overrides
        self.assertNotIn("PUBLIC_R", proc.stdout, "not-tracked overrides public recipient")
        self.assertNotIn("PUBLIC_F", proc.stdout, "not-tracked overrides public funder")
        self.assertNotIn("amount:", proc.stdout, "not-tracked suppresses amount")
        self.assertIn("not-tracked-by-design: by design", proc.stdout)
        self.assertIn("(0 public / 1 not-tracked", proc.stdout)

    def test_4_withdrawn_excluded(self):
        p = _write(self.tmp, "wd.json", {"allocations": [
            {"allocation_id": "a1", "allocation_type": "money", "public_summary": "kept",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R", "funder": "F", "amount": 100, "unit": "CAD",
             "not_tracked_reason": None, "withdrawn": False},
            {"allocation_id": "a2", "allocation_type": "money", "public_summary": "WITHDRAWN_SUMMARY",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R2", "funder": "F2", "amount": 200, "unit": "CAD",
             "not_tracked_reason": None, "withdrawn": True},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(1 public / 0 not-tracked / 1 withdrawn of 2 total)", proc.stdout)
        self.assertNotIn("WITHDRAWN_SUMMARY", proc.stdout, "withdrawn entry not listed")
        self.assertNotIn("R2", proc.stdout)

    def test_5_aggregate_counts(self):
        p = _write(self.tmp, "agg.json", {"allocations": [
            {"allocation_id": "a1", "allocation_type": "money", "public_summary": "x",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R", "funder": "F", "amount": 100, "unit": "CAD",
             "not_tracked_reason": None, "withdrawn": False},
            {"allocation_id": "a2", "allocation_type": "money", "public_summary": "y",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R", "funder": "F", "amount": 50, "unit": "CAD",
             "not_tracked_reason": None, "withdrawn": False},
            {"allocation_id": "a3", "allocation_type": "time", "public_summary": "z",
             "recipient_visibility": "public", "funder_visibility": "public", "amount_visibility": "public",
             "recipient": "R", "funder": "F", "amount": 1, "unit": "hour",
             "not_tracked_reason": None, "withdrawn": False},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("AGGREGATE BY TYPE:", proc.stdout)
        self.assertIn("money: 2 entries", proc.stdout)
        self.assertIn("time: 1 entries", proc.stdout)
        # Anti-surveillance: must NOT sum amounts
        self.assertNotIn("150", proc.stdout, "must not aggregate amounts across entries")
        self.assertNotIn("total amount", proc.stdout.lower())

    def test_6_invalid_json(self):
        p = _write(self.tmp, "bad", "{not valid")
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.strip().startswith("error:"))


def _main():
    s = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    r = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
    print("M2LITE_SUMMARY " + json.dumps({"tests": r.testsRun, "passed": r.testsRun - len(r.failures) - len(r.errors),
                                          "failures": sorted(t.id() for t,_ in r.failures), "errors": sorted(t.id() for t,_ in r.errors)}))
    return 0 if r.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(_main())
