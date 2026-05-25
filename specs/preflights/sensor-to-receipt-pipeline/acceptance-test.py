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


class SensorReceiptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="srp-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args), capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_basic_packet(self):
        p = _write(self.tmp, "basic.json", {"observations": [
            {"observation_id": "o1", "observation_type": "sensor_reading", "source": "S",
             "location": "site1", "location_precision": "site", "time": "2026-05-15",
             "measurement": 1.5, "unit": "m", "calibration_state": "calibrated",
             "sensitive_location_flag": False, "review_state": "reviewed"},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("SENSOR-TO-RECEIPT EVIDENCE PACKETS (1 kept / 1 total)", proc.stdout)
        self.assertIn("- id: o1", proc.stdout)
        self.assertIn("data: 1.5 m", proc.stdout)
        self.assertIn("calibration_confidence: high", proc.stdout)

    def test_2_sensitive_redacted(self):
        p = _write(self.tmp, "sens.json", {"observations": [
            {"observation_id": "o1", "observation_type": "field_note", "source": "K",
             "location": "exact GPS 49.28,-123.12", "location_precision": "exact", "time": "2026-05-16",
             "measurement": None, "unit": None, "calibration_state": "unknown",
             "sensitive_location_flag": True, "review_state": "pending"},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("location: region-level only", proc.stdout, "sensitive flag triggers redaction")
        self.assertNotIn("49.28", proc.stdout, "exact GPS must not appear")
        self.assertIn("data: qualitative observation", proc.stdout)
        self.assertIn("sensitive-location-redacted", proc.stdout)

    def test_3_qualitative(self):
        p = _write(self.tmp, "qual.json", {"observations": [
            {"observation_id": "o1", "observation_type": "field_note", "source": "S",
             "location": "site", "location_precision": "site", "time": "2026-05-15",
             "measurement": None, "unit": None, "calibration_state": "unknown",
             "sensitive_location_flag": False, "review_state": "reviewed"},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("data: qualitative observation", proc.stdout)

    def test_4_reject_malformed(self):
        p = _write(self.tmp, "bad.json", {"observations": [
            {"observation_id": "o1", "observation_type": "sensor_reading", "source": "S",
             "location": "x", "location_precision": "site", "time": "2026-05-15",
             "measurement": 1.0, "unit": "m", "calibration_state": "calibrated",
             "sensitive_location_flag": False, "review_state": "reviewed"},
            {"observation_id": "", "observation_type": "field_note", "source": "x",
             "location": "x", "location_precision": "site", "time": "2026-05-15",
             "measurement": None, "unit": None, "calibration_state": "unknown",
             "sensitive_location_flag": False, "review_state": "pending"},
            {"observation_id": "o3", "observation_type": "field_note", "source": "x",
             "location": "x", "location_precision": "site", "time": "not-a-date",
             "measurement": None, "unit": None, "calibration_state": "unknown",
             "sensitive_location_flag": False, "review_state": "pending"},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(1 kept / 3 total)", proc.stdout)
        self.assertIn("SUMMARY: 1 kept, 2 rejected, 0 sensitive-location-redacted of 3 total", proc.stdout)

    def test_5_calibration_mapping(self):
        p = _write(self.tmp, "cal.json", {"observations": [
            {"observation_id": "a", "observation_type": "sensor_reading", "source": "S", "location": "x",
             "location_precision": "site", "time": "2026-05-15", "measurement": 1.0, "unit": "m",
             "calibration_state": "calibrated", "sensitive_location_flag": False, "review_state": "reviewed"},
            {"observation_id": "b", "observation_type": "sensor_reading", "source": "S", "location": "x",
             "location_precision": "site", "time": "2026-05-15", "measurement": 1.0, "unit": "m",
             "calibration_state": "uncalibrated", "sensitive_location_flag": False, "review_state": "reviewed"},
            {"observation_id": "c", "observation_type": "sensor_reading", "source": "S", "location": "x",
             "location_precision": "site", "time": "2026-05-15", "measurement": 1.0, "unit": "m",
             "calibration_state": "unknown", "sensitive_location_flag": False, "review_state": "reviewed"},
        ]})
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("calibration_confidence: high", proc.stdout)
        self.assertIn("calibration_confidence: low", proc.stdout)
        self.assertIn("calibration_confidence: unknown", proc.stdout)

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
