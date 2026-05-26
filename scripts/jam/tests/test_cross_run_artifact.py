"""Tests for scripts/jam/cross_run_artifact.py — stdlib-only, no network."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import cross_run_artifact as cra  # noqa: E402
from jam import closing_readout as cr  # noqa: E402


def _write_master_log(run_dir: Path, entries):
    log = run_dir / "overnight-master-log.jsonl"
    log.write_text("\n".join(json.dumps(e) for e in entries) + "\n")


def _make_fake_run(
    parent: Path,
    name: str,
    config_extras=None,
    rounds=None,
    wall_record_files=None,
    coherence_md=None,
    proposals=None,
) -> Path:
    """Build a fake persistent_root with a loop_start, some rounds, an
    optional wall/, optional coherence-synthesis.md, optional proposals.
    """
    root = parent / name
    root.mkdir(parents=True, exist_ok=True)
    loop_start = {
        "kind": "loop_start",
        "started_at": "2026-05-26T00:00:00+00:00",
        "kit_root": "/fake/kit",
        "persistent_root": str(root),
        "gateway": "http://localhost:8000",
        "models": ["telus-qwen", "telus-gemma"],
        "specs": ["spec-a", "spec-b"],
        "max_rounds": 50,
        "time_budget_hours": 3.0,
        "max_telus_calls": 1200,
        "aggregate_every": 5,
        "builder_mode": "telus",
        "mesh_mode": True,
    }
    if config_extras:
        loop_start.update(config_extras)
    entries = [loop_start]
    for r in rounds or []:
        entries.append({"kind": "round", **r})
    entries.append({
        "kind": "loop_finish",
        "finished_at": "2026-05-26T03:00:00+00:00",
        "halt_reason": "done",
        "rounds_completed": len(rounds or []),
        "wall_seconds": 10000,
        "cumulative_telus_calls": 100,
    })
    _write_master_log(root, entries)
    if wall_record_files:
        wall = root / "wall"
        wall.mkdir(parents=True, exist_ok=True)
        for fname, body in wall_record_files:
            (wall / fname).write_text(body)
    if coherence_md is not None:
        (root / "coherence-synthesis.md").write_text(coherence_md)
    if proposals:
        comp = root / "compositions"
        comp.mkdir(parents=True, exist_ok=True)
        for fname, body in proposals:
            (comp / fname).write_text(body)
    return root


class DiscoverRunsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.parent = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_discover_runs_from_persistent_roots(self):
        r1 = _make_fake_run(
            self.parent, "run-a",
            rounds=[
                {"spec_id": "spec-a", "model": "telus-qwen",
                 "outcome": "frozen-and-published"},
                {"spec_id": "spec-a", "model": "telus-gemma",
                 "outcome": "refused-by-model"},
            ],
            wall_record_files=[("w1.md", "body")],
        )
        r2 = _make_fake_run(
            self.parent, "run-b",
            rounds=[
                {"spec_id": "spec-b", "model": "telus-qwen",
                 "outcome": "review-halted"},
            ],
        )
        runs = cra.discover_runs([r1, r2])
        self.assertEqual(len(runs), 2)
        labels = [r["label"] for r in runs]
        self.assertIn("run-a", labels)
        self.assertIn("run-b", labels)
        run_a = next(r for r in runs if r["label"] == "run-a")
        self.assertEqual(run_a["rounds_total"], 2)
        self.assertEqual(run_a["wall_record_count"], 1)
        # config copied through
        self.assertEqual(run_a["config"]["mesh_mode"], True)
        # refusal rates per model
        rr = run_a["refusal_rates"]
        self.assertEqual(rr["telus-gemma"]["refused"], 1)
        self.assertEqual(rr["telus-qwen"]["refused"], 0)


class ExtractConfigTests(unittest.TestCase):
    def test_extract_config_from_loop_start_entry_with_all_fields(self):
        entry = {
            "kind": "loop_start",
            "planner_threshold": 3,
            "mesh_mode": True,
            "dag_mode": "strict",
            "max_rounds": 200,
            "time_budget_hours": 3.0,
            "models": ["telus-qwen"],
            "specs": ["spec-a"],
        }
        cfg = cra.extract_config_from_loop_start(entry)
        self.assertEqual(cfg["planner_threshold"], 3)
        self.assertEqual(cfg["mesh_mode"], True)
        self.assertEqual(cfg["dag_mode"], "strict")
        self.assertEqual(cfg["max_rounds"], 200)
        self.assertEqual(cfg["time_budget_hours"], 3.0)
        self.assertEqual(cfg["models"], ["telus-qwen"])
        self.assertEqual(cfg["specs"], ["spec-a"])

    def test_extract_config_handles_missing_optional_fields(self):
        entry = {"kind": "loop_start", "mesh_mode": False}
        cfg = cra.extract_config_from_loop_start(entry)
        self.assertIsNone(cfg["planner_threshold"])
        self.assertEqual(cfg["mesh_mode"], False)
        self.assertIsNone(cfg["dag_mode"])

    def test_extract_config_accepts_dag_alias(self):
        entry = {"kind": "loop_start", "dag": "lenient"}
        cfg = cra.extract_config_from_loop_start(entry)
        self.assertEqual(cfg["dag_mode"], "lenient")

    def test_extract_config_non_dict_input(self):
        cfg = cra.extract_config_from_loop_start(None)
        self.assertEqual(cfg["models"], [])
        self.assertIsNone(cfg["mesh_mode"])


class OutcomeBucketingTests(unittest.TestCase):
    def test_outcome_bucketing_uses_closing_readout_bucket_for(self):
        rounds = [
            {"outcome": "frozen-and-published"},
            {"outcome": "frozen-and-published"},
            {"outcome": "review-halted"},
            {"outcome": "refused-by-model"},
            {"outcome": "refused-by-gatekeeper"},
            {"outcome": "loop-error"},
        ]
        counts = cra.bucket_outcome_counts(rounds)
        self.assertEqual(counts["passed"], 2)
        self.assertEqual(counts["partial"], 1)
        self.assertEqual(counts["refused"], 2)
        self.assertEqual(counts["failed"], 1)
        # no-publish = everything except passed = 4
        self.assertEqual(counts["no-publish"], 4)

    def test_bucket_for_uses_same_logic_as_closing_readout(self):
        # Sanity: cra delegates to cr.bucket_for
        self.assertEqual(
            cr.bucket_for("frozen-and-published"), "passed",
        )
        self.assertEqual(
            cr.bucket_for("refused-by-anything"), "refused",
        )


class RenderTests(unittest.TestCase):
    def test_render_with_no_runs_returns_stub(self):
        md = cra.render_cross_run_document(
            runs=[], highlights=[], synthesis_prose=None,
            synthesis_skipped_reason="empty",
        )
        self.assertIn("Cross-Run Closing Ceremony Artifact", md)
        self.assertIn("nothing to weave", md)
        # Closing boundary still present, exactly once.
        self.assertEqual(md.count("Closing Boundary"), 1)

    def test_render_includes_closing_boundary_once(self):
        # Two fake runs, render document, count "Closing Boundary"
        runs = [
            {
                "label": "run-a",
                "persistent_root": "/tmp/run-a",
                "config": {"planner_threshold": 2, "mesh_mode": True,
                            "dag_mode": None, "max_rounds": 150,
                            "time_budget_hours": 9.0},
                "outcome_counts": {"passed": 5, "refused": 1},
                "rounds_total": 6,
                "refusal_rates": {
                    "telus-qwen": {"total": 3, "refused": 0,
                                    "refusal_rate": 0.0},
                },
                "top_specs": [("spec-a", 3)],
                "wall_record_count": 5,
                "synthesis_prose": "Some prose.",
            },
            {
                "label": "run-b",
                "persistent_root": "/tmp/run-b",
                "config": {"planner_threshold": 3, "mesh_mode": True,
                            "dag_mode": None, "max_rounds": 200,
                            "time_budget_hours": 3.0},
                "outcome_counts": {"passed": 4, "partial": 1},
                "rounds_total": 5,
                "refusal_rates": {
                    "telus-qwen": {"total": 2, "refused": 0,
                                    "refusal_rate": 0.0},
                },
                "top_specs": [("spec-b", 2)],
                "wall_record_count": 4,
                "synthesis_prose": "Other prose.",
            },
        ]
        md = cra.render_cross_run_document(
            runs=runs, highlights=[],
            synthesis_prose="agreed... diverged... observed...",
        )
        # Exactly ONE closing boundary heading.
        self.assertEqual(md.count("## Closing Boundary"), 1)
        # The bound CROSS_RUN_CLOSING_BOUNDARY substring shows up once.
        self.assertEqual(
            md.count("does not establish legitimacy"), 1
        )
        # Both run labels listed.
        self.assertIn("`run-a`", md)
        self.assertIn("`run-b`", md)
        # Substrate synthesis section rendered.
        self.assertIn("agreed", md)


class GatewayFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.parent = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_synthesis_skipped_when_gateway_fails(self):
        r1 = _make_fake_run(
            self.parent, "run-a",
            rounds=[
                {"spec_id": "spec-a", "model": "telus-qwen",
                 "outcome": "frozen-and-published"},
            ],
            wall_record_files=[("w1.md", "body")],
            coherence_md=(
                "# Coherence Synthesis\n\n"
                "## What these specs say together\n\n"
                "Things were observed.\n\n"
                "## Open coherence questions\n\n"
                "- ?\n"
            ),
        )
        with mock.patch.object(
            cra, "call_cross_run_gateway",
            side_effect=RuntimeError("upstream down"),
        ):
            md = cra.weave(
                persistent_roots=[r1],
                gateway="http://localhost:8000",
                model="telus-gemma",
                team_key="iai_test",
            )
        # Document still produced
        self.assertIn("Cross-Run Closing Ceremony Artifact", md)
        # Statistics still rendered
        self.assertIn("Cross-run aggregate", md)
        # Inventory still rendered
        self.assertIn("run-a", md)
        # Skipped notice present
        self.assertIn("LLM cross-run synthesis was not produced", md)
        self.assertIn("upstream down", md)
        # One closing boundary
        self.assertEqual(md.count("## Closing Boundary"), 1)

    def test_no_team_key_skips_synthesis_softly(self):
        r1 = _make_fake_run(
            self.parent, "run-a",
            rounds=[{"spec_id": "s", "model": "telus-qwen",
                      "outcome": "frozen-and-published"}],
        )
        md = cra.weave(
            persistent_roots=[r1],
            gateway="http://localhost:8000",
            model="telus-gemma",
            team_key=None,
        )
        self.assertIn("team key not provided", md)


class CompositionHighlightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.parent = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def _proposal(self, title, specs, intent="cluster-internal:X",
                  caveats="Some caveat.", refusal=False, vision=None):
        body = [f"# {title}", "",
                f"- intent: {intent}", "",
                "## Components composed", ""]
        for s in specs:
            body += [f"### `{s}` (cluster: X)", "",
                      "- title: t", "- vision: v",
                      "- build_target: bt", ""]
        body += ["## Proposed composition", "",
                  "### Title", "", title, "",
                  "### Vision", "",
                  vision if vision is not None else "Some vision body.", ""]
        body += ["### Composition seams", "",
                  "- seam one", ""]
        if caveats:
            body += ["### Composition caveats", "", caveats, ""]
        body += ["## Boundary", "",
                  "This is a proposal. Do not reuse.", ""]
        return "\n".join(body)

    def test_highlights_pick_diverse_compositions(self):
        # Build 4 proposals across 2 runs:
        #   p1: specs {a,b} — caveats
        #   p2: specs {a,b} — DUPLICATE spec set — should be skipped
        #   p3: specs {c,d} — caveats
        #   p4: specs {e,f} — refusal-as-record
        proposals = [
            ("proposal-00.md",
             self._proposal("Comp One", ["a", "b"])),
            ("proposal-01.md",
             self._proposal("Comp Two", ["a", "b"])),
            ("proposal-02.md",
             self._proposal("Comp Three", ["c", "d"])),
            ("proposal-03.md",
             self._proposal("Refused composition",
                              ["e", "f"], refusal=True,
                              vision="Refused to compose: incompatible.")),
        ]
        r1 = _make_fake_run(
            self.parent, "run-a",
            rounds=[{"spec_id": "a", "model": "telus-qwen",
                      "outcome": "frozen-and-published"}],
            proposals=proposals,
        )
        run_summary = cra.discover_runs([r1])[0]
        all_props = cra.collect_compositions(run_summary)
        self.assertEqual(len(all_props), 4)
        # is_refusal detected
        refusals = [p for p in all_props if p["is_refusal"]]
        self.assertEqual(len(refusals), 1)
        # has_caveats detected
        with_caveats = [p for p in all_props if p["has_caveats"]]
        self.assertGreaterEqual(len(with_caveats), 3)

        picked = cra.pick_diverse_highlights(all_props, max_n=5)
        # Refusal always picked (first-class).
        picked_files = {p["filename"] for p in picked}
        self.assertIn("proposal-03.md", picked_files)
        # We pick at most one of the duplicate-spec-set proposals (p1/p2)
        n_dup = sum(
            1 for p in picked
            if set(p["specs_touched"]) == {"a", "b"}
        )
        self.assertLessEqual(n_dup, 1)
        # And we pick the distinct-spec proposal too.
        self.assertIn("proposal-02.md", picked_files)


if __name__ == "__main__":
    unittest.main()
