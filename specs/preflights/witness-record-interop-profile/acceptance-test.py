#!/usr/bin/env python3
import json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "tool.py")
TIMEOUT = 10


def _write(dirpath, name, obj):
    p = os.path.join(dirpath, name)
    with open(p, "w") as f:
        if isinstance(obj, str): f.write(obj)
        else: json.dump(obj, f)
    return p


class WitnessValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="wrv-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_ok_record(self):
        p = _write(self.tmp, "ok.json", {"records": [
            {"record_id": "r1", "statement": "small claim", "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [],
             "evidence_pointers": [{"id":"e1","created_at":"2026-05-10"}],
             "visibility_tier": "public", "permission_state": "granted",
             "review_state": "reviewed", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("r1: OK", proc.stdout)
        self.assertIn("SUMMARY: 1 ok, 0 with findings of 1 total", proc.stdout)

    def test_2_missing_consent(self):
        p = _write(self.tmp, "mc.json", {"records": [
            {"record_id": "r1", "statement": "x", "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [], "evidence_pointers": [{"id":"e","created_at":"2026-05-10"}],
             "visibility_tier": "public", "permission_state": "pending",
             "review_state": "reviewed", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("missing_consent", proc.stdout)

    def test_3_stale_evidence(self):
        p = _write(self.tmp, "stale.json", {"records": [
            {"record_id": "r1", "statement": "x", "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [], "evidence_pointers": [{"id":"e","created_at":"2024-01-01"}],
             "visibility_tier": "private", "permission_state": "granted",
             "review_state": "reviewed", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("stale_evidence", proc.stdout)

    def test_4_overbroad(self):
        long_statement = "x " * 200  # > 240 chars
        p = _write(self.tmp, "ob.json", {"records": [
            {"record_id": "r1", "statement": long_statement, "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [], "evidence_pointers": [{"id":"e","created_at":"2026-05-10"}],
             "visibility_tier": "public", "permission_state": "granted",
             "review_state": "reviewed", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("overbroad_public_claim", proc.stdout)

    def test_5_authority_language(self):
        p = _write(self.tmp, "auth.json", {"records": [
            {"record_id": "r1", "statement": "This is a CERTIFIED outcome.", "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [], "evidence_pointers": [{"id":"e","created_at":"2026-05-10"}],
             "visibility_tier": "private", "permission_state": "granted",
             "review_state": "pending", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("unsupported_authority_language", proc.stdout)

    def test_6_findings_alphabetical(self):
        long_statement = ("This is an authorized outcome. " * 20)
        p = _write(self.tmp, "multi.json", {"records": [
            {"record_id": "r1", "statement": long_statement, "record_type": "claim",
             "actor_or_issuer": "A", "witnesses": [], "evidence_pointers": [{"id":"e","created_at":"2024-01-01"}],
             "visibility_tier": "public", "permission_state": "pending",
             "review_state": "pending", "created_at": "2026-05-15"},
        ]})
        proc = self._run(p, "2026-05-20")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("missing_consent, overbroad_public_claim, stale_evidence, unsupported_authority_language", proc.stdout)

    def test_7_invalid_json(self):
        p = _write(self.tmp, "bad.json", "{not valid")
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.strip().startswith("error:"))


def _main():
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    summary = {"tests": result.testsRun, "passed": result.testsRun - len(result.failures) - len(result.errors),
               "failures": sorted(t.id() for t,_ in result.failures), "errors": sorted(t.id() for t,_ in result.errors)}
    print("M2LITE_SUMMARY " + json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(_main())
