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


def _team(**overrides):
    base = {
        "team": "T1",
        "kept_events": 1,
        "rejected_events": 0,
        "total_kwh": 0.01,
        "input_tokens": 100,
        "output_tokens": 200,
        "models": ["gemma-4-31b"],
        "intention_themes": ["kelp"],
        "disclosure": "public",
    }
    base.update(overrides)
    return base


def _doc(**overrides):
    base = {
        "jam": "IndigenomicsAI Creator Jam",
        "date": "2026-05-25",
        "site": "TELUS-Rimouski hydro",
        "teams": [],
    }
    base.update(overrides)
    return base


class ComputeCovenantTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="cov-")

    def _run(self, *args):
        return subprocess.run([sys.executable, TOOL] + list(args),
                              capture_output=True, text=True, timeout=TIMEOUT)

    def test_1_header_and_ecosystem_rollup(self):
        p = _write(self.tmp, "basic.json", _doc(teams=[
            _team(team="Kelp", total_kwh=0.02, input_tokens=100,
                  output_tokens=300, models=["gemma-4-31b"]),
            _team(team="Herring", total_kwh=0.03, input_tokens=200,
                  output_tokens=400, models=["qwen-3.6-35b"]),
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("COMPUTE COVENANT — IndigenomicsAI Creator Jam (2026-05-25)", proc.stdout)
        self.assertIn("site: TELUS-Rimouski hydro", proc.stdout)
        self.assertIn("ECOSYSTEM ENERGY", proc.stdout)
        self.assertIn("teams: 2 kept (2 public, 0 withheld), 0 rejected of 2 total", proc.stdout)
        self.assertIn("jam_kwh: 0.0500", proc.stdout)
        self.assertIn("tokens: 300 in / 700 out", proc.stdout)
        self.assertIn("models: gemma-4-31b, qwen-3.6-35b", proc.stdout)

    def test_2_per_team_block(self):
        p = _write(self.tmp, "pt.json", _doc(teams=[
            _team(team="Kelp Watchers", kept_events=5, rejected_events=1,
                  total_kwh=0.0420, input_tokens=2400, output_tokens=5100,
                  models=["qwen-3.6-35b", "gemma-4-31b"],
                  intention_themes=["kelp", "eelgrass"]),
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("PER-TEAM CONTRIBUTIONS", proc.stdout)
        self.assertIn("- team: Kelp Watchers", proc.stdout)
        self.assertIn("kWh: 0.042", proc.stdout)
        self.assertIn("events: 5 kept, 1 rejected", proc.stdout)
        self.assertIn("tokens: 2400 in / 5100 out", proc.stdout)
        self.assertIn("intention themes: kelp, eelgrass", proc.stdout)
        self.assertIn("models: gemma-4-31b, qwen-3.6-35b", proc.stdout)

    def test_3_withheld_not_named_but_counted(self):
        p = _write(self.tmp, "wh.json", _doc(teams=[
            _team(team="PublicTeam", total_kwh=0.01),
            _team(team="SecretCircle", total_kwh=0.05, input_tokens=500,
                  output_tokens=900, models=["gpt-oss-120b"],
                  disclosure="withheld"),
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        # ecosystem includes both
        self.assertIn("jam_kwh: 0.0600", proc.stdout)
        self.assertIn("teams: 2 kept (1 public, 1 withheld), 0 rejected of 2 total", proc.stdout)
        # per-team block names public only
        self.assertIn("- team: PublicTeam", proc.stdout)
        self.assertNotIn("SecretCircle", proc.stdout, "withheld team name must not appear")
        self.assertIn("WITHHELD: 1 team(s) opted out of public energy disclosure.", proc.stdout)
        self.assertIn("Their compute is included in ECOSYSTEM ENERGY", proc.stdout)

    def test_4_covenant_and_boundary(self):
        p = _write(self.tmp, "cov.json", _doc(teams=[
            _team(team="T", total_kwh=0.8),  # 0.8 / 0.4 = 2.00 Vancouver homes
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("COVENANT", proc.stdout)
        self.assertIn("This jam consumed 0.8000 kWh on TELUS-Rimouski hydro.", proc.stdout)
        self.assertIn("Equivalent to roughly 2.00 Vancouver homes for an hour", proc.stdout)
        self.assertIn("(0.4 kWh/home/hour reference)", proc.stdout)
        self.assertIn("Witnessed.", proc.stdout)
        self.assertIn("BOUNDARY:", proc.stdout)
        self.assertIn("~99% renewable hydro", proc.stdout)
        self.assertIn("does not offset", proc.stdout)
        self.assertIn("ecological repair", proc.stdout)
        self.assertIn("reuse license", proc.stdout)

    def test_5_rejects_malformed(self):
        p = _write(self.tmp, "bad.json", _doc(teams=[
            _team(team="ok"),
            _team(team=""),                                    # empty team
            _team(team="x", disclosure="maybe"),               # bad disclosure
            _team(team="x", total_kwh=-0.1),                   # negative kwh
            _team(team="x", input_tokens="oops"),              # non-numeric
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("teams: 1 kept (1 public, 0 withheld), 4 rejected of 5 total",
                      proc.stdout)

    def test_6_no_public_teams(self):
        p = _write(self.tmp, "wh-only.json", _doc(teams=[
            _team(team="A", disclosure="withheld"),
            _team(team="B", disclosure="withheld"),
        ]))
        proc = self._run(p)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("(no public-disclosure teams)", proc.stdout)
        self.assertIn("WITHHELD: 2 team(s) opted out", proc.stdout)
        self.assertNotIn("- team: A", proc.stdout)
        self.assertNotIn("- team: B", proc.stdout)

    def test_7_invalid_json(self):
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
