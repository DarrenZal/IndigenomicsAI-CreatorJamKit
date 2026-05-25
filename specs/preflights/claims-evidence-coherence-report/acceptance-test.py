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


class ClaimsCoherenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="ccr-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_ready_for_use(self):
        p = _write(self.tmp, "ready.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [{"id":"e","created_at":"2026-05-15","reviewer":"R"}],
             "reviewer": "R", "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("c1 [outcome]: ready_for_use", proc.stdout)
        self.assertNotIn("repair_path:", proc.stdout)

    def test_2_do_not_compute(self):
        p = _write(self.tmp, "dnc.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "internal", "visibility_tier": "not-for-computation",
             "evidence_pointers": [], "reviewer": None, "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("c1 [outcome]: do_not_compute", proc.stdout)
        self.assertIn("preserve as marker-only", proc.stdout)

    def test_3_visibility_blocked(self):
        p = _write(self.tmp, "vb.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "private",
             "evidence_pointers": [{"id":"e","created_at":"2026-05-15","reviewer":"R"}],
             "reviewer": "R", "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("c1 [outcome]: visibility_blocked", proc.stdout)

    def test_4_stale(self):
        p = _write(self.tmp, "stale.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [{"id":"e","created_at":"2024-01-01","reviewer":"R"}],
             "reviewer": "R", "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("stale_evidence", proc.stdout)
        self.assertIn("refresh evidence within freshness window for outcome", proc.stdout)

    def test_5_missing_evidence(self):
        p = _write(self.tmp, "me.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [], "reviewer": None, "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("missing_evidence", proc.stdout)

    def test_6_contested(self):
        p = _write(self.tmp, "cont.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [{"id":"e","created_at":"2026-05-15","reviewer":"R"}],
             "reviewer": "R", "contested": True},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("contested", proc.stdout)

    def test_7_summary_counts(self):
        p = _write(self.tmp, "mix.json", {"claims": [
            {"claim_id": "c1", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [{"id":"e","created_at":"2026-05-15","reviewer":"R"}], "reviewer": "R", "contested": False},
            {"claim_id": "c2", "claim_text": "x", "claim_type": "outcome",
             "intended_use": "public_share", "visibility_tier": "public",
             "evidence_pointers": [], "reviewer": None, "contested": False},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("SUMMARY: 1 ready / 1 needing work of 2 total", proc.stdout)

    def test_8_invalid_json(self):
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
