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

class PreflightTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.tmp = tempfile.mkdtemp(prefix="pre-")
    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, timeout=TIMEOUT)

    def test_t1_basic(self):
        p = _write(self.tmp, "t1_basic.json", {'briefing_title': 'T', 'as_of': '2026-05-01', 'claims': ['a'], 'evidence_count': 2, 'observation_count': 3, 'reviewer': 'R'})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('# T', proc.stdout)
        self.assertIn('_as of 2026-05-01_', proc.stdout)
        self.assertIn('claims: 1', proc.stdout)
        self.assertIn('R', proc.stdout)

    def test_t2_no_reviewer(self):
        p = _write(self.tmp, "t2_no_reviewer.json", {'briefing_title': 'X', 'as_of': '2026-05-01', 'claims': [], 'evidence_count': 0, 'observation_count': 0, 'reviewer': None})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('NOT YET REVIEWED', proc.stdout)


    def test_zz_invalid_json(self):
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
