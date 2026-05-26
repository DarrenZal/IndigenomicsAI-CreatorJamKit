"""Tests for jam.agent_aggregator — multi-round pattern aggregation."""

import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import agent_aggregator as ag


def _make_round_entry(spec_id="spec-foo", run_id="run-x", *,
                       outcome="frozen-and-published",
                       model="telus-qwen",
                       reviewer_findings=None,
                       witness_draft_present=False):
    return {
        "spec_id": spec_id,
        "run_id": run_id,
        "result": {"outcome": outcome, "model": model},
        "reviewer_findings": reviewer_findings,
        "witness_draft_present": witness_draft_present,
    }


def _make_round(round_id, entries):
    return {"round_id": round_id, "summary": None, "per_spec": entries}


class CollectRoundsTests(unittest.TestCase):
    def test_collect_rounds_empty_dir_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as td:
            rounds_dir = Path(td) / "rounds"
            # Directory does not exist; function should return []
            self.assertEqual(ag.collect_rounds(rounds_dir), [])

    def test_collect_rounds_walks_subdirs(self):
        with tempfile.TemporaryDirectory() as td:
            rounds_dir = Path(td)
            run_dir = rounds_dir / "round-001" / "spec-foo" / "run-x"
            run_dir.mkdir(parents=True)
            (run_dir / "result.json").write_text(
                json.dumps({"outcome": "frozen-and-published",
                             "model": "telus-qwen"})
            )

            rounds = ag.collect_rounds(rounds_dir)
            self.assertEqual(len(rounds), 1)
            self.assertEqual(rounds[0]["round_id"], "round-001")
            per_spec = rounds[0]["per_spec"]
            self.assertEqual(len(per_spec), 1)
            self.assertIsNotNone(per_spec[0]["result"])
            self.assertEqual(per_spec[0]["result"]["outcome"],
                              "frozen-and-published")
            self.assertEqual(per_spec[0]["spec_id"], "spec-foo")
            self.assertEqual(per_spec[0]["run_id"], "run-x")


class AnalyzeOutcomesTests(unittest.TestCase):
    def test_analyze_outcomes_counts_publish_and_refuse(self):
        rounds = [
            _make_round("round-001", [
                _make_round_entry(outcome="frozen-and-published",
                                   model="telus-qwen"),
            ]),
            _make_round("round-002", [
                _make_round_entry(outcome="refused-by-model: cultural authorization",
                                   model="telus-mistral"),
            ]),
        ]
        result = ag.analyze_outcomes(rounds)
        self.assertIsInstance(result["overall"], Counter)
        self.assertEqual(result["overall"]["frozen-and-published"], 1)
        self.assertEqual(
            result["overall"]["refused-by-model: cultural authorization"], 1
        )
        # per_model populated
        self.assertIn("telus-qwen", result["per_model"])
        self.assertIn("telus-mistral", result["per_model"])


class AnalyzeReviewerFindingsTests(unittest.TestCase):
    def test_analyze_reviewer_findings_counts_halts(self):
        rounds = [
            _make_round("round-001", [
                _make_round_entry(reviewer_findings={
                    "findings": {
                        "review_passed": False,
                        "halt_publish": True,
                        "checks": [
                            {"name": "overclaim-vocabulary",
                             "status": "halt",
                             "note": "x"}
                        ],
                    }
                }),
            ]),
        ]
        result = ag.analyze_reviewer_findings(rounds)
        self.assertEqual(result["halted_count"], 1)
        self.assertEqual(result["reviewed_count"], 1)
        self.assertEqual(
            result["check_status_counts"]["overclaim-vocabulary"]["halt"], 1
        )


class DeriveRecommendationsTests(unittest.TestCase):
    def test_derive_recommendations_no_patterns_returns_default_message(self):
        rounds = [
            _make_round("round-001", [
                _make_round_entry(outcome="frozen-and-published",
                                   model="telus-qwen"),
            ]),
        ]
        outcomes = ag.analyze_outcomes(rounds)
        reviewer = ag.analyze_reviewer_findings(rounds)
        recs = ag.derive_recommendations(outcomes, reviewer, rounds)
        self.assertEqual(len(recs), 1)
        self.assertIn("No multi-round patterns detected", recs[0])

    def test_derive_recommendations_detects_repeated_refusal(self):
        refusal = "refused-by-model: requires cultural authorization"
        rounds = [
            _make_round("round-001", [
                _make_round_entry(outcome=refusal, model="telus-qwen"),
            ]),
            _make_round("round-002", [
                _make_round_entry(outcome=refusal, model="telus-qwen"),
            ]),
        ]
        outcomes = ag.analyze_outcomes(rounds)
        reviewer = ag.analyze_reviewer_findings(rounds)
        recs = ag.derive_recommendations(outcomes, reviewer, rounds)
        self.assertTrue(
            any("Refusal pattern observed" in r for r in recs),
            f"expected 'Refusal pattern observed' in recs; got {recs}"
        )


class RenderMarkdownTests(unittest.TestCase):
    def test_render_markdown_includes_round_count(self):
        with tempfile.TemporaryDirectory() as td:
            wall_root = Path(td) / "wall"
            rounds = [
                _make_round("round-001", [
                    _make_round_entry(outcome="frozen-and-published",
                                       model="telus-qwen"),
                ]),
            ]
            outcomes = ag.analyze_outcomes(rounds)
            reviewer = ag.analyze_reviewer_findings(rounds)
            recs = ag.derive_recommendations(outcomes, reviewer, rounds)
            md = ag.render_markdown(rounds, outcomes, reviewer, recs, wall_root)
            self.assertIn("rounds analyzed: ", md)
            self.assertIn("## Recommendations", md)


if __name__ == "__main__":
    unittest.main()
