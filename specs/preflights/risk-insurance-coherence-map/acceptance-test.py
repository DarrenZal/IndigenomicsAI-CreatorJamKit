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
        p = _write(self.tmp, "t1_basic.json", {'signals': [{'signal_id': 's1', 'area': 'area-A', 'kind': 'observation', 'severity_marker': 'low', 'public_share': True}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('RESILIENCE SIGNAL MAP (1 public / 1 total)', proc.stdout)
        self.assertIn('area: area-a', proc.stdout)
        self.assertIn('this map does not rank', proc.stdout)

    def test_t2_no_ranking(self):
        p = _write(self.tmp, "t2_no_ranking.json", {'signals': [{'signal_id': 's1', 'area': 'A', 'kind': 'observation', 'severity_marker': 'high', 'public_share': True}, {'signal_id': 's2', 'area': 'A', 'kind': 'observation', 'severity_marker': 'high', 'public_share': True}, {'signal_id': 's3', 'area': 'A', 'kind': 'observation', 'severity_marker': 'high', 'public_share': True}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertNotIn('3 high', proc.stdout)
        self.assertNotIn('score', proc.stdout)
        self.assertNotIn('ranking', proc.stdout)


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
