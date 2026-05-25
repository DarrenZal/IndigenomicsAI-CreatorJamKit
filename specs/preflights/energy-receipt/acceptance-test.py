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


def _evt(**overrides):
    base = {
        "event_id": "e1",
        "intention": "default intention",
        "model": "gemma-4-31b",
        "input_tokens": 100,
        "output_tokens": 200,
        "duration_seconds": 1.5,
        "estimated_kwh": 0.001,
        "outcome_summary": "default outcome",
    }
    base.update(overrides)
    return base


class EnergyReceiptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="enr-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args),
                              capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_header_and_basic_event(self):
        p = _write(self.tmp, "basic.json", {
            "team": "Kelp Watchers",
            "events": [_evt(event_id="e1", intention="draft opener",
                            model="gemma-4-31b", input_tokens=240,
                            output_tokens=410, duration_seconds=6.2,
                            estimated_kwh=0.0042, outcome_summary="kept first draft")],
        })
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ENERGY RECEIPT — Kelp Watchers", proc.stdout)
        self.assertIn("- event_id: e1", proc.stdout)
        self.assertIn("intention: draft opener", proc.stdout)
        self.assertIn("model: gemma-4-31b", proc.stdout)
        self.assertIn("kWh: 0.0042", proc.stdout)
        self.assertIn("tokens: 240 in / 410 out", proc.stdout)
        self.assertIn("duration_s: 6.2", proc.stdout)
        self.assertIn("outcome: kept first draft", proc.stdout)

    def test_2_totals_and_distinct_models(self):
        p = _write(self.tmp, "totals.json", {
            "team": "Herring Friends",
            "events": [
                _evt(event_id="a", model="gemma-4-31b", input_tokens=100,
                     output_tokens=200, estimated_kwh=0.01),
                _evt(event_id="b", model="qwen-3.6-35b", input_tokens=300,
                     output_tokens=500, estimated_kwh=0.02),
                _evt(event_id="c", model="gemma-4-31b", input_tokens=50,
                     output_tokens=50, estimated_kwh=0.005),
            ],
        })
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("TOTALS", proc.stdout)
        self.assertIn("events: 3 kept, 0 rejected of 3 total", proc.stdout)
        self.assertIn("kWh: 0.0350", proc.stdout)
        self.assertIn("tokens: 450 in / 750 out", proc.stdout)
        self.assertIn("models: gemma-4-31b, qwen-3.6-35b", proc.stdout)

    def test_3_reflection_and_boundary(self):
        p = _write(self.tmp, "ref.json", {"team": "T", "events": [_evt()]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("REFLECTION", proc.stdout)
        self.assertIn("Did the work justify its footprint?", proc.stdout)
        self.assertIn("What would you do differently?", proc.stdout)
        self.assertIn("What reciprocity is owed?", proc.stdout)
        self.assertIn("BOUNDARY:", proc.stdout)
        self.assertIn("does not offset", proc.stdout)
        self.assertIn("certify carbon neutrality", proc.stdout)
        self.assertIn("reuse license", proc.stdout)

    def test_4_rejects_malformed(self):
        p = _write(self.tmp, "bad.json", {
            "team": "T",
            "events": [
                _evt(event_id="ok"),
                _evt(event_id=""),                          # empty id
                _evt(event_id="x", intention=""),            # empty intention
                _evt(event_id="x", model=""),                # empty model
                _evt(event_id="x", estimated_kwh=-0.01),     # negative kwh
                _evt(event_id="x", input_tokens="not-a-num"),# non-numeric
            ],
        })
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("events: 1 kept, 5 rejected of 6 total", proc.stdout)

    def test_5_no_kept_events(self):
        p = _write(self.tmp, "none.json", {"team": "Empty", "events": [_evt(event_id="")]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("ENERGY RECEIPT — Empty", proc.stdout)
        self.assertIn("events: 0 kept, 1 rejected of 1 total", proc.stdout)
        self.assertIn("models: none", proc.stdout)
        self.assertIn("REFLECTION", proc.stdout)
        self.assertIn("BOUNDARY:", proc.stdout)

    def test_6_invalid_json(self):
        p = _write(self.tmp, "bad", "{not valid")
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(proc.stdout.strip().startswith("error:"))


def _main():
    s = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    r = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(s)
    print("M2LITE_SUMMARY " + json.dumps({
        "tests": r.testsRun,
        "passed": r.testsRun - len(r.failures) - len(r.errors),
        "failures": sorted(t.id() for t, _ in r.failures),
        "errors": sorted(t.id() for t, _ in r.errors),
    }))
    return 0 if r.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(_main())
