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

    def test_t1_public_visible(self):
        p = _write(self.tmp, "t1_public_visible.json", {'actions': [{'action_id': 'a', 'action_type': 'review', 'steward_visibility': 'public', 'private_notes': 'HIDDEN', 'outcome_summary': 'shown'}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('a [review]: shown', proc.stdout)
        self.assertNotIn('HIDDEN', proc.stdout)

    def test_t2_private_hidden(self):
        p = _write(self.tmp, "t2_private_hidden.json", {'actions': [{'action_id': 'a', 'action_type': 'refusal', 'steward_visibility': 'private', 'private_notes': 'X', 'outcome_summary': 'WILL_NOT_APPEAR'}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('a [refusal]: held by steward', proc.stdout)
        self.assertNotIn('WILL_NOT_APPEAR', proc.stdout)
        self.assertNotIn('X', proc.stdout)

    def test_t3_private_notes_never_leak(self):
        p = _write(self.tmp, "t3_private_notes_never_leak.json", {'actions': [{'action_id': 'a', 'action_type': 'review', 'steward_visibility': 'public', 'private_notes': 'DEFINITELY_PRIVATE', 'outcome_summary': 'public ok'}]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0, "stderr=%r" % proc.stderr)
        self.assertIn('public ok', proc.stdout)
        self.assertNotIn('DEFINITELY_PRIVATE', proc.stdout)


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
