"""Tests for scripts/jam/agent_planner.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_agent_planner -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import agent_planner as ap  # noqa: E402


class OutcomeClassificationTests(unittest.TestCase):
    def test_publish_outcome(self):
        self.assertEqual(ap.classify_outcome("frozen-and-published"), "publish")

    def test_refusal_outcomes(self):
        self.assertEqual(
            ap.classify_outcome("refused-by-gatekeeper"), "refusal")
        self.assertEqual(
            ap.classify_outcome("refused-by-model: cultural authorization"),
            "refusal")
        self.assertEqual(
            ap.classify_outcome("offering-generation-failed: HTTP 401"),
            "refusal")

    def test_non_publish_outcomes(self):
        for o in ["doesnt-fit-yet-no-packet", "review-halted",
                   "subprocess-timeout", "publish-timeout", "loop-error"]:
            self.assertEqual(ap.classify_outcome(o), "non-publish",
                              f"failed on {o}")

    def test_non_string_input(self):
        self.assertEqual(ap.classify_outcome(None), "non-publish")
        self.assertEqual(ap.classify_outcome(123), "non-publish")


class PlannerStateMachineTests(unittest.TestCase):
    def setUp(self):
        self.specs = ["spec-a", "spec-b"]
        self.models = ["model-x", "model-y"]
        self.p = ap.Planner(self.specs, self.models, consecutive_threshold=2)

    def test_initial_state_all_pairs_active(self):
        self.assertEqual(len(self.p.active_pairs()), 4)

    def test_demotes_pair_after_threshold_consecutive_non_publish(self):
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: cultural"})
        # Not yet demoted (1 of 2 threshold)
        self.assertEqual(len(self.p.demoted_pairs), 0)
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "doesnt-fit-yet-no-packet"})
        # Now demoted
        self.assertIn(("spec-a", "model-x"), self.p.demoted_pairs)
        self.assertEqual(len(self.p.active_pairs()), 3)

    def test_publish_resets_consecutive_counter(self):
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: cultural"})
        self.assertEqual(self.p.consecutive_non_publish[("spec-a", "model-x")], 1)
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "frozen-and-published"})
        self.assertEqual(self.p.consecutive_non_publish[("spec-a", "model-x")], 0)
        self.assertNotIn(("spec-a", "model-x"), self.p.demoted_pairs)

    def test_one_publish_then_one_refusal_does_not_demote(self):
        """Counter resets fully on publish; single subsequent refusal
        starts counter at 1, not 2."""
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: x"})
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "frozen-and-published"})
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: y"})
        self.assertNotIn(("spec-a", "model-x"), self.p.demoted_pairs)

    def test_demoted_pair_excluded_from_active_pairs(self):
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: x"})
        self.p.update({"spec_id": "spec-a", "model": "model-x",
                        "outcome": "refused-by-model: y"})
        active = self.p.active_pairs()
        self.assertNotIn(("spec-a", "model-x"), active)
        self.assertIn(("spec-a", "model-y"), active)

    def test_threshold_3_requires_three_consecutive(self):
        p3 = ap.Planner(self.specs, self.models, consecutive_threshold=3)
        p3.update({"spec_id": "spec-a", "model": "model-x",
                    "outcome": "refused-by-model: x"})
        p3.update({"spec_id": "spec-a", "model": "model-x",
                    "outcome": "refused-by-model: y"})
        # 2 of 3 — not yet
        self.assertNotIn(("spec-a", "model-x"), p3.demoted_pairs)
        p3.update({"spec_id": "spec-a", "model": "model-x",
                    "outcome": "refused-by-model: z"})
        self.assertIn(("spec-a", "model-x"), p3.demoted_pairs)

    def test_missing_spec_id_or_model_ignored(self):
        # Should not raise; should not affect state
        self.p.update({"outcome": "frozen-and-published"})
        self.p.update({"spec_id": "spec-a", "outcome": "frozen-and-published"})
        self.assertEqual(len(self.p.events), 0)


class NextPairSchedulingTests(unittest.TestCase):
    def test_next_pair_cycles_active(self):
        p = ap.Planner(["a", "b"], ["x", "y"])
        seen = set()
        for _ in range(8):
            pair = p.next_pair()
            self.assertIsNotNone(pair)
            seen.add(pair)
        # All 4 pairs visited
        self.assertEqual(len(seen), 4)

    def test_next_pair_returns_none_when_all_demoted(self):
        p = ap.Planner(["a"], ["x"], consecutive_threshold=1)
        p.update({"spec_id": "a", "model": "x",
                   "outcome": "refused-by-model: x"})
        self.assertIsNone(p.next_pair())

    def test_next_pair_skips_demoted(self):
        p = ap.Planner(["a", "b"], ["x"], consecutive_threshold=1)
        p.update({"spec_id": "a", "model": "x",
                   "outcome": "refused-by-model: x"})
        # Only (b, x) is active
        for _ in range(4):
            self.assertEqual(p.next_pair(), ("b", "x"))


class AggregatorConsumptionTests(unittest.TestCase):
    def test_consume_spec_zero_publish_pattern(self):
        p = ap.Planner(["witness-record-interop-profile",
                         "flow-funding-frontier-map"],
                        ["telus-qwen", "telus-gemma"])
        agg = (
            "1. Spec `witness-record-interop-profile` ran 3 time(s) and "
            "never reached publish. Outcomes: {'refused-by-model': 3}. "
            "Consider whether the spec body is structured in a way that "
            "consistently trips a refusal layer."
        )
        actions = p.consume_aggregator(agg)
        self.assertEqual(actions, 1)
        self.assertIn("witness-record-interop-profile", p.demoted_specs)

    def test_consume_model_zero_publish_pattern(self):
        p = ap.Planner(["a"], ["telus-qwen", "telus-gemma"])
        agg = "Model `telus-qwen` published 0 of 5 round(s). Outcomes: {...}"
        actions = p.consume_aggregator(agg)
        self.assertEqual(actions, 1)
        self.assertIn("telus-qwen", p.demoted_models)

    def test_consume_ignores_specs_not_in_planner(self):
        p = ap.Planner(["a"], ["x"])
        agg = "Spec `unknown-spec` ran 3 time(s) and never reached publish."
        actions = p.consume_aggregator(agg)
        self.assertEqual(actions, 0)
        self.assertEqual(len(p.demoted_specs), 0)

    def test_consume_idempotent_on_already_demoted(self):
        p = ap.Planner(["a"], ["x", "y"])
        agg = "Spec `a` ran 3 time(s) and never reached publish."
        p.consume_aggregator(agg)
        self.assertEqual(p.consume_aggregator(agg), 0)

    def test_consume_handles_non_string_input(self):
        p = ap.Planner(["a"], ["x"])
        self.assertEqual(p.consume_aggregator(None), 0)
        self.assertEqual(p.consume_aggregator(123), 0)


class StatusReportingTests(unittest.TestCase):
    def test_status_reports_counts(self):
        p = ap.Planner(["a", "b"], ["x", "y"])
        s = p.status()
        self.assertEqual(s["specs_total"], 2)
        self.assertEqual(s["models_total"], 2)
        self.assertEqual(s["pairs_total"], 4)
        self.assertEqual(s["pairs_active"], 4)
        self.assertEqual(s["pairs_demoted"], 0)


if __name__ == "__main__":
    unittest.main()
