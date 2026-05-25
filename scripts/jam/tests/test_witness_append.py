"""Tests for scripts/jam/witness_append.py — stdlib-only (unittest).

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_witness_append -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import witness_append as wa  # noqa: E402


VALID_RECORD = """# Canoe Landing — Test Team

- team-id: team-test
- date: 2026-05-26
- finding: **built clean**

## What we brought

A small test offering.

## What worked

Acceptance criteria 1 and 2 passed.

## What we learned

Tests are useful.

## Receipt

This record states what happened. It does not establish authority,
approval, certification, or legitimacy.
"""


REFUSAL_RECORD = """# Canoe Landing — Refusal Team

- team-id: team-refuse
- date: 2026-05-26
- finding: **refusal — we chose not to publish**

## What we brought

An offering we considered publishing.

## What we did

We chose not to surface this offering publicly. Refusal is a complete
outcome.

## Receipt

This record states what happened. It does not establish authority,
approval, certification, or legitimacy.
"""


OVERCLAIM_RECORD = """# Canoe Landing — Bad Team

- team-id: team-bad
- date: 2026-05-26

## What we did

We officially certified this build as community-approved and
authorized for production reuse.

## Receipt

This record states what happened. It does not establish authority.
"""


NO_RECEIPT_RECORD = """# Canoe Landing — Missing Receipt

- team-id: team-no-receipt
- date: 2026-05-26

## What we did

A perfectly fine build, but I forgot the receipt statement.
"""


class ParseRecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def _write(self, content):
        p = Path(self.tmp) / "r.md"
        p.write_text(content)
        return p

    def test_parse_valid(self):
        p = self._write(VALID_RECORD)
        parsed = wa.parse_record(p)
        self.assertEqual(parsed["team_id"], "team-test")
        self.assertTrue(parsed["receipt_present"])
        self.assertFalse(parsed["refusal"])

    def test_parse_refusal(self):
        p = self._write(REFUSAL_RECORD)
        parsed = wa.parse_record(p)
        self.assertTrue(parsed["refusal"])
        self.assertTrue(parsed["receipt_present"])

    def test_parse_no_receipt(self):
        p = self._write(NO_RECEIPT_RECORD)
        parsed = wa.parse_record(p)
        self.assertFalse(parsed["receipt_present"])


class AppendFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.wall = Path(self.tmp) / "wall"
        self.record = Path(self.tmp) / "r.md"

    def _write(self, content):
        self.record.write_text(content)

    def test_append_without_confirm_publish_does_not_publish(self):
        self._write(VALID_RECORD)
        result = wa.append_record(self.record, self.wall, confirm_publish=False)
        self.assertFalse(result["published"])
        self.assertIn("--confirm-publish", result["reason"])
        self.assertFalse((self.wall / "witness-records").exists() and any((self.wall / "witness-records").iterdir()))

    def test_append_with_confirm_publishes_valid_record(self):
        self._write(VALID_RECORD)
        result = wa.append_record(self.record, self.wall, confirm_publish=True)
        self.assertTrue(result["published"])
        self.assertIn("record_id", result)
        files = list((self.wall / "witness-records").iterdir())
        self.assertEqual(len(files), 1)

    def test_append_with_overclaim_rejects(self):
        self._write(OVERCLAIM_RECORD)
        result = wa.append_record(self.record, self.wall, confirm_publish=True)
        self.assertFalse(result["published"])
        self.assertIn("overclaim", result["reason"].lower())

    def test_append_without_receipt_rejects(self):
        self._write(NO_RECEIPT_RECORD)
        result = wa.append_record(self.record, self.wall, confirm_publish=True)
        self.assertFalse(result["published"])
        self.assertIn("receipt", result["reason"].lower())

    def test_refusal_as_record_publishes(self):
        self._write(REFUSAL_RECORD)
        result = wa.append_record(self.record, self.wall, confirm_publish=True)
        self.assertTrue(result["published"])
        self.assertTrue(result["parsed"]["refusal"])


class WallRenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.wall = Path(self.tmp) / "wall"

    def _publish(self, content):
        rec = Path(self.tmp) / f"r-{id(content)}.md"
        rec.write_text(content)
        return wa.append_record(rec, self.wall, confirm_publish=True)

    def test_empty_wall_renders_safe_message(self):
        rendered = wa.render_wall(self.wall)
        self.assertIn("No records yet", rendered)

    def test_wall_renders_published_records(self):
        self._publish(VALID_RECORD)
        self._publish(REFUSAL_RECORD)
        rendered = wa.render_wall(self.wall)
        self.assertIn("Records published**: 2", rendered)
        self.assertIn("team-test", rendered)
        self.assertIn("team-refuse", rendered)
        # Refusal marker
        self.assertIn("⟂", rendered)

    def test_audit_passes_on_clean_wall(self):
        self._publish(VALID_RECORD)
        self._publish(REFUSAL_RECORD)
        result = wa.audit_wall(self.wall)
        self.assertTrue(result["ok"])
        self.assertEqual(result["records"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
