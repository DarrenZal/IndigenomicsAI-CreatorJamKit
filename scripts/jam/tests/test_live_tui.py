"""Tests for live_tui pure-data functions and tail-follow behavior.

Curses is never initialized in these tests. Each test exercises only the
module-level pure functions or the TailFollower class.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.jam import live_tui


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _append_text(path: Path, text: str) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(text)


class ParseLoopStartTests(unittest.TestCase):

    def test_loop_start_populates_specs_and_budget(self):
        state = live_tui.new_state()
        event = {
            "kind": "loop_start",
            "started_at": "2026-05-26T05:58:31.597836+00:00",
            "models": ["telus-qwen", "telus-gemma", "telus-gpt-oss"],
            "specs": [
                "witness-record-interop-profile",
                "commitment-pool-route-diagnostic",
                "dream-to-fulfillment-board",
            ],
            "max_rounds": 150,
            "time_budget_hours": 9.0,
            "max_telus_calls": 1200,
        }
        live_tui.apply_event(state, event)

        self.assertEqual(state["models"],
                         ["telus-qwen", "telus-gemma", "telus-gpt-oss"])
        self.assertEqual(len(state["specs"]), 3)
        self.assertIn("dream-to-fulfillment-board", state["specs"])
        self.assertEqual(state["max_rounds"], 150)
        self.assertEqual(state["time_budget_hours"], 9.0)
        self.assertEqual(state["max_telus_calls"], 1200)
        self.assertIsNotNone(state["started_at"])
        self.assertEqual(state["started_at"].tzinfo, timezone.utc)


class ParseRoundTests(unittest.TestCase):

    def test_round_updates_model_and_spec_counters(self):
        state = live_tui.new_state()
        live_tui.apply_event(state, {
            "kind": "loop_start",
            "models": ["telus-qwen", "telus-gemma"],
            "specs": ["spec-a", "spec-b"],
            "max_rounds": 10,
            "max_telus_calls": 100,
            "started_at": "2026-05-26T00:00:00+00:00",
        })
        live_tui.apply_event(state, {
            "kind": "round", "round_idx": 1, "spec_id": "spec-a",
            "model": "telus-qwen", "subprocess_returncode": 0,
            "outcome": "frozen-and-published", "telus_calls": 7,
            "elapsed_seconds": 12.3,
        })
        live_tui.apply_event(state, {
            "kind": "round", "round_idx": 2, "spec_id": "spec-a",
            "model": "telus-qwen", "subprocess_returncode": 0,
            "outcome": "refused-by-model: requires cultural authorization",
            "telus_calls": 4, "elapsed_seconds": 9.4,
        })
        live_tui.apply_event(state, {
            "kind": "round", "round_idx": 3, "spec_id": "spec-b",
            "model": "telus-gemma", "subprocess_returncode": 0,
            "outcome": "review-halted: missing evidence", "telus_calls": 5,
        })

        self.assertEqual(state["per_model"]["telus-qwen"]["rounds"], 2)
        self.assertEqual(state["per_model"]["telus-qwen"]["frozen"], 1)
        self.assertEqual(state["per_model"]["telus-qwen"]["refused"], 1)
        self.assertEqual(state["per_model"]["telus-qwen"]["telus_calls"], 11)

        self.assertEqual(state["per_model"]["telus-gemma"]["rounds"], 1)
        self.assertEqual(state["per_model"]["telus-gemma"]["review-halted"], 1)
        self.assertEqual(state["per_model"]["telus-gemma"]["telus_calls"], 5)

        self.assertEqual(state["per_spec"]["spec-a"]["rounds"], 2)
        self.assertEqual(state["per_spec"]["spec-a"]["frozen"], 1)
        self.assertEqual(state["per_spec"]["spec-a"]["refused"], 1)
        self.assertEqual(state["per_spec"]["spec-b"]["rounds"], 1)
        self.assertEqual(state["per_spec"]["spec-b"]["review-halted"], 1)

        self.assertEqual(state["total_telus_calls"], 16)
        self.assertEqual(len(state["rounds"]), 3)

    def test_unknown_event_kind_is_skipped(self):
        state = live_tui.new_state()
        # Should not raise.
        live_tui.apply_event(state, {"kind": "future-event-type", "foo": "bar"})
        live_tui.apply_event(state, {"kind": None})
        live_tui.apply_event(state, {})
        self.assertEqual(state["rounds"], [])
        self.assertEqual(state["total_telus_calls"], 0)


class OutcomeClassificationTests(unittest.TestCase):

    def test_frozen_prefix_is_green(self):
        self.assertEqual(
            live_tui.classify_outcome("frozen-and-published", 0),
            live_tui.COLOR_GREEN,
        )
        # Trailing detail still classifies as frozen.
        self.assertEqual(
            live_tui.classify_outcome("frozen-and-published: receipt 0xabc", 0),
            live_tui.COLOR_GREEN,
        )

    def test_review_halted_prefix_is_yellow(self):
        self.assertEqual(
            live_tui.classify_outcome("review-halted", 0),
            live_tui.COLOR_YELLOW,
        )
        self.assertEqual(
            live_tui.classify_outcome("review-halted: missing evidence", 0),
            live_tui.COLOR_YELLOW,
        )

    def test_refused_prefix_is_red(self):
        self.assertEqual(
            live_tui.classify_outcome("refused", 0),
            live_tui.COLOR_RED,
        )
        self.assertEqual(
            live_tui.classify_outcome(
                "refused-by-model: requires cultural authorization", 0),
            live_tui.COLOR_RED,
        )

    def test_error_prefix_is_gray(self):
        self.assertEqual(
            live_tui.classify_outcome("error: gateway timeout", 0),
            live_tui.COLOR_GRAY,
        )

    def test_nonzero_returncode_forces_gray_regardless_of_outcome(self):
        # Even a "frozen" outcome with a non-zero return code is treated as error.
        self.assertEqual(
            live_tui.classify_outcome("frozen-and-published", 1),
            live_tui.COLOR_GRAY,
        )
        self.assertEqual(
            live_tui.classify_outcome("anything", -9),
            live_tui.COLOR_GRAY,
        )

    def test_unknown_outcome_is_default(self):
        self.assertEqual(
            live_tui.classify_outcome("something-novel", 0),
            live_tui.COLOR_DEFAULT,
        )
        self.assertEqual(
            live_tui.classify_outcome("", 0),
            live_tui.COLOR_DEFAULT,
        )
        self.assertEqual(
            live_tui.classify_outcome(None, 0),
            live_tui.COLOR_DEFAULT,
        )

    def test_bucket_labels(self):
        self.assertEqual(
            live_tui.outcome_bucket("frozen-and-published", 0), "frozen")
        self.assertEqual(
            live_tui.outcome_bucket("review-halted: x", 0), "review-halted")
        self.assertEqual(
            live_tui.outcome_bucket("refused-by-model: y", 0), "refused")
        self.assertEqual(
            live_tui.outcome_bucket("error: z", 0), "error")
        self.assertEqual(
            live_tui.outcome_bucket("frozen-and-published", 2), "error")
        self.assertEqual(
            live_tui.outcome_bucket("mystery", 0), "other")


class TailFollowPartialLineTests(unittest.TestCase):

    def test_partial_trailing_line_is_buffered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "log.jsonl"
            _write_text(p, '{"kind":"loop_start","models":["a"],"specs":["s"]}\n')
            follower = live_tui.TailFollower(p)
            first = follower.read_new_lines()
            self.assertEqual(len(first), 1)
            self.assertIn("loop_start", first[0])

            # Append a partial line (no newline yet) — should be buffered.
            _append_text(p, '{"kind":"round","round_idx":1')
            second = follower.read_new_lines()
            self.assertEqual(second, [],
                             "partial trailing line must not be returned yet")

            # Finish the line — now we should see the complete record.
            _append_text(p, ',"spec_id":"s","model":"a",'
                            '"subprocess_returncode":0,'
                            '"outcome":"frozen-and-published",'
                            '"telus_calls":3}\n')
            third = follower.read_new_lines()
            self.assertEqual(len(third), 1)
            parsed = json.loads(third[0])
            self.assertEqual(parsed["round_idx"], 1)
            self.assertEqual(parsed["outcome"], "frozen-and-published")


class TailFollowRotationTests(unittest.TestCase):

    def test_file_rotation_restarts_from_offset_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "log.jsonl"
            original_content = (
                '{"kind":"loop_start","models":["m"],"specs":["s"]}\n'
                '{"kind":"round","round_idx":1,"spec_id":"s","model":"m",'
                '"subprocess_returncode":0,"outcome":"frozen-and-published",'
                '"telus_calls":2}\n'
            )
            _write_text(p, original_content)
            follower = live_tui.TailFollower(p)
            first = follower.read_new_lines()
            self.assertEqual(len(first), 2)
            # No new content — should return [].
            self.assertEqual(follower.read_new_lines(), [])

            # Rotation: rewrite the file with shorter content.
            # On macOS unlinking + recreating changes the inode; truncate alone
            # changes the size. Test the shrink case (size < pos).
            shorter = '{"kind":"loop_start","models":["m2"],"specs":["s2"]}\n'
            _write_text(p, shorter)
            after_rotation = follower.read_new_lines()
            self.assertEqual(len(after_rotation), 1)
            self.assertIn("m2", after_rotation[0])

    def test_inode_change_restarts_from_offset_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "log.jsonl"
            # Make the first file LONGER than the replacement so the size check
            # alone wouldn't trigger; we want the inode-change path.
            long_content = (
                '{"kind":"loop_start","models":["a"],"specs":["s"]}\n'
                + ('{"kind":"round","round_idx":99,"spec_id":"s","model":"a",'
                   '"subprocess_returncode":0,"outcome":"frozen-and-published",'
                   '"telus_calls":1,"padding":"' + ("x" * 500) + '"}\n')
            )
            _write_text(p, long_content)
            follower = live_tui.TailFollower(p)
            first = follower.read_new_lines()
            self.assertEqual(len(first), 2)

            # Replace the file via unlink + create-with-same-name → new inode,
            # but write content that's ALSO longer than the original so the
            # size>pos check wouldn't catch it on its own.
            os.unlink(p)
            replacement = (
                '{"kind":"loop_start","models":["b"],"specs":["s2"]}\n'
                '{"kind":"round","round_idx":1,"spec_id":"s2","model":"b",'
                '"subprocess_returncode":0,"outcome":"refused: x",'
                '"telus_calls":1,"padding":"' + ("y" * 2000) + '"}\n'
            )
            _write_text(p, replacement)
            after_rotation = follower.read_new_lines()
            # Should see both new lines because we restarted from offset 0.
            self.assertEqual(len(after_rotation), 2)
            self.assertIn('"b"', after_rotation[0])

    def test_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "not-there.jsonl"
            follower = live_tui.TailFollower(p)
            self.assertEqual(follower.read_new_lines(), [])
            # File appears later.
            _write_text(p, '{"kind":"loop_start","models":[],"specs":[]}\n')
            lines = follower.read_new_lines()
            self.assertEqual(len(lines), 1)


class HeaderFormattingTests(unittest.TestCase):

    def test_format_elapsed(self):
        started = datetime(2026, 5, 26, 0, 0, 0, tzinfo=timezone.utc)
        now = datetime(2026, 5, 26, 7, 23, 0, tzinfo=timezone.utc)
        self.assertEqual(live_tui.format_elapsed(started, now=now), "7h 23m")
        # None started_at -> placeholder.
        self.assertEqual(live_tui.format_elapsed(None, now=now), "--h --m")

    def test_format_header_includes_halt_when_stop_present(self):
        state = live_tui.new_state()
        state["started_at"] = datetime(2026, 5, 26, 0, 0, 0, tzinfo=timezone.utc)
        state["max_rounds"] = 150
        state["max_telus_calls"] = 1200
        state["total_telus_calls"] = 42
        state["rounds"] = [{} for _ in range(5)]
        now = datetime(2026, 5, 26, 1, 0, 0, tzinfo=timezone.utc)
        header = live_tui.format_header(state, now=now, stop_present=True)
        self.assertIn("5/150 rounds", header)
        self.assertIn("42/1200 TELUS calls", header)
        self.assertIn("HALT REQUESTED", header)
        self.assertIn("1h 00m elapsed", header)


class BuildRenderLinesTests(unittest.TestCase):

    def test_render_includes_sections(self):
        state = live_tui.new_state()
        live_tui.apply_event(state, {
            "kind": "loop_start",
            "started_at": "2026-05-26T00:00:00+00:00",
            "models": ["telus-qwen", "telus-gemma"],
            "specs": ["spec-a"],
            "max_rounds": 10, "max_telus_calls": 100,
        })
        live_tui.apply_event(state, {
            "kind": "round", "round_idx": 1, "spec_id": "spec-a",
            "model": "telus-qwen", "subprocess_returncode": 0,
            "outcome": "frozen-and-published", "telus_calls": 3,
            "elapsed_seconds": 11.1,
        })
        lines = live_tui.build_render_lines(state, width=140)
        texts = [t for t, _ in lines]
        joined = "\n".join(texts)
        self.assertIn("Overnight Jam Loop", joined)
        self.assertIn("Recent rounds", joined)
        self.assertIn("Per-model totals", joined)
        self.assertIn("Per-spec totals", joined)
        self.assertIn("telus-qwen", joined)
        self.assertIn("spec-a", joined)

    def test_narrow_width_does_not_overflow(self):
        state = live_tui.new_state()
        live_tui.apply_event(state, {
            "kind": "loop_start",
            "started_at": "2026-05-26T00:00:00+00:00",
            "models": ["telus-qwen"], "specs": ["spec-a-with-a-long-name"],
            "max_rounds": 10, "max_telus_calls": 100,
        })
        live_tui.apply_event(state, {
            "kind": "round", "round_idx": 1, "spec_id": "spec-a-with-a-long-name",
            "model": "telus-qwen", "subprocess_returncode": 0,
            "outcome": "refused-by-model: " + ("x" * 200),
            "telus_calls": 1, "elapsed_seconds": 1.0,
        })
        for w in (40, 60, 80, 200):
            lines = live_tui.build_render_lines(state, width=w)
            for text, _ in lines:
                self.assertLessEqual(len(text), w, f"line too wide at width={w}: {text!r}")


if __name__ == "__main__":
    unittest.main()
