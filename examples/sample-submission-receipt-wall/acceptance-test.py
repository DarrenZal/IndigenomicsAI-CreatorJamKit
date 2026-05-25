#!/usr/bin/env python3
"""Acceptance test for the Story Receipts Wall sample build attempt."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "tool.py")
SUBPROCESS_TIMEOUT = 10


def _write_json(dirpath, name, obj):
    path = os.path.join(dirpath, name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return path


def _write_raw(dirpath, name, text):
    path = os.path.join(dirpath, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


class StoryReceiptsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="story-receipts-fixtures-")

    def _run(self, input_path):
        return subprocess.run(
            [sys.executable, TOOL, input_path],
            capture_output=True, text=True, timeout=SUBPROCESS_TIMEOUT,
        )

    def _lines(self, stdout):
        return [ln.rstrip() for ln in stdout.rstrip("\n").split("\n")]

    def test_1_happy_path_two_public_one_withheld(self):
        path = _write_json(self.tmp, "happy.json", {"receipts": [
            {"id": "r1", "contributor": "A. Cedar", "date": "2026-05-12", "text": "Read with the room.", "display_scope": "public", "tags": ["learning"]},
            {"id": "r2", "contributor": "M. Salal", "date": "2026-05-13", "text": "The freeze step caught a missing consent question.", "display_scope": "public"},
            {"id": "r3", "contributor": "J. Fir", "date": "2026-05-14", "text": "Will share aloud Tuesday but not in writing.", "display_scope": "spoken-only"},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["# Story Receipts Wall (2 shown / 3 total)",
             "",
             "## A. Cedar — 2026-05-12",
             "",
             "> Read with the room.",
             "",
             "tags: learning",
             "",
             "## M. Salal — 2026-05-13",
             "",
             "> The freeze step caught a missing consent question.",
             "",
             "---",
             "",
             "Receipts withheld from display: 1"],
            "header, two public receipts sorted by date, tags line only when tags present, '---' + withheld count footer")

    def test_2_multi_line_receipt_each_line_quoted(self):
        path = _write_json(self.tmp, "multi.json", {"receipts": [
            {"id": "r1", "contributor": "A. Cedar", "date": "2026-05-12", "text": "Line one.\nLine two.\nLine three.", "display_scope": "public"},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertEqual(
            self._lines(proc.stdout),
            ["# Story Receipts Wall (1 shown / 1 total)",
             "",
             "## A. Cedar — 2026-05-12",
             "",
             "> Line one.",
             "> Line two.",
             "> Line three.",
             "",
             "---",
             "",
             "Receipts withheld from display: 0"],
            "each line of multi-line text is quoted individually with '> '")

    def test_3_sort_date_then_id(self):
        path = _write_json(self.tmp, "sort.json", {"receipts": [
            {"id": "r3", "contributor": "C", "date": "2026-05-12", "text": "x", "display_scope": "public"},
            {"id": "r1", "contributor": "A", "date": "2026-05-12", "text": "x", "display_scope": "public"},
            {"id": "r2", "contributor": "B", "date": "2026-05-10", "text": "x", "display_scope": "public"},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        out = proc.stdout
        # r2 (earliest date) first, then r1 (id tie-break), then r3
        b_pos = out.find("## B —")
        a_pos = out.find("## A —")
        c_pos = out.find("## C —")
        self.assertTrue(0 <= b_pos < a_pos < c_pos,
                        "sort: date ascending then id ascending; got B@%d A@%d C@%d" % (b_pos, a_pos, c_pos))

    def test_4_empty_text_is_withheld(self):
        path = _write_json(self.tmp, "empty.json", {"receipts": [
            {"id": "r1", "contributor": "A", "date": "2026-05-12", "text": "good", "display_scope": "public"},
            {"id": "r2", "contributor": "B", "date": "2026-05-12", "text": "", "display_scope": "public"},
            {"id": "r3", "contributor": "C", "date": "2026-05-12", "text": "   ", "display_scope": "public"},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        first_line = proc.stdout.split("\n")[0]
        self.assertEqual(first_line, "# Story Receipts Wall (1 shown / 3 total)",
                         "two of three receipts have empty/whitespace text — both withheld")
        self.assertIn("Receipts withheld from display: 2", proc.stdout,
                      "withheld count = total - shown = 3 - 1 = 2")

    def test_5_missing_scope_treated_as_withheld(self):
        path = _write_json(self.tmp, "no-scope.json", {"receipts": [
            {"id": "r1", "contributor": "A", "date": "2026-05-12", "text": "shown", "display_scope": "public"},
            {"id": "r2", "contributor": "B", "date": "2026-05-12", "text": "hidden"},
        ]})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        self.assertIn("# Story Receipts Wall (1 shown / 2 total)", proc.stdout,
                      "missing display_scope counts as withheld")
        self.assertNotIn("hidden", proc.stdout, "withheld receipt text must not appear in output")

    def test_6_empty_receipts_list(self):
        path = _write_json(self.tmp, "zero.json", {"receipts": []})
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "tool must exit 0; stderr=%r" % proc.stderr)
        lines = self._lines(proc.stdout)
        self.assertEqual(lines[0], "# Story Receipts Wall (0 shown / 0 total)")
        self.assertIn("Receipts withheld from display: 0", proc.stdout)

    def test_7_invalid_json(self):
        path = _write_raw(self.tmp, "broken.json", "{this is not valid json,,,")
        proc = self._run(path)
        self.assertEqual(proc.returncode, 0, "malformed JSON must exit 0; stderr=%r" % proc.stderr)
        self.assertTrue(proc.stdout.strip().startswith("error:"),
                        "malformed JSON prints single 'error:' line; got: %r" % proc.stdout)


def _main():
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    summary = {
        "tests": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors),
        "failures": sorted(t.id() for t, _ in result.failures),
        "errors": sorted(t.id() for t, _ in result.errors),
    }
    print("M2LITE_SUMMARY " + json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(_main())
