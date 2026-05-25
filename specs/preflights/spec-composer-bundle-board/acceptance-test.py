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
        p = _write(self.tmp, "t1_basic.json", {'fragments': [{'id': 'a', 'produces': ['x'], 'consumes': []}, {'id': 'b', 'produces': [], 'consumes': ['x']}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('BUNDLE BOARD (1 candidate pairs of 2 fragments)', proc.stdout)
        self.assertIn('a -> b via x', proc.stdout)

    def test_t2_no_overlap(self):
        p = _write(self.tmp, "t2_no_overlap.json", {'fragments': [{'id': 'a', 'produces': ['x'], 'consumes': []}, {'id': 'b', 'produces': ['y'], 'consumes': ['z']}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('(0 candidate pairs', proc.stdout)
        self.assertNotIn('a -> b', proc.stdout)

    def test_t3_distinct_count(self):
        p = _write(self.tmp, "t3_distinct_count.json", {'fragments': [{'id': 'a', 'produces': ['x', 'y'], 'consumes': ['z']}, {'id': 'b', 'produces': ['z'], 'consumes': ['x']}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('', proc.stdout)
        self.assertIn('3 distinct interfaces', proc.stdout)


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
