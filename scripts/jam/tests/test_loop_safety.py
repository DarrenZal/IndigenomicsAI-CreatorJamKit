"""Tests for jam.loop_safety — overnight-loop-time safety helpers."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import loop_safety as ls


class ScanForCredentialsTests(unittest.TestCase):
    def test_scan_credentials_clean_text(self):
        hits = ls.scan_for_credentials(
            "kelp herring eelgrass salmon — no creds here"
        )
        self.assertEqual(hits, [])

    def test_scan_credentials_bearer_token(self):
        hits = ls.scan_for_credentials(
            "Authorization: Bearer abc123def456ghi789jkl012mno345xyz"
        )
        self.assertGreaterEqual(len(hits), 1)
        names = {h["pattern_name"] for h in hits}
        self.assertIn("bearer_token_value", names)

    def test_scan_credentials_dev_key_prefix(self):
        hits_iai = ls.scan_for_credentials("the key iai_dev_victoria was used")
        self.assertGreaterEqual(len(hits_iai), 1)
        self.assertIn("dev_key_prefix", {h["pattern_name"] for h in hits_iai})

        hits_sk = ls.scan_for_credentials("sk-1234567890abcdefghij")
        self.assertGreaterEqual(len(hits_sk), 1)
        self.assertIn("dev_key_prefix", {h["pattern_name"] for h in hits_sk})

    def test_scan_credentials_jwt_shape(self):
        # Regex requires eyJ + 8+ chars, then . + 8+ chars, then . + 8+ chars.
        # The spec's example shape was indicative; adjust to satisfy length.
        hits = ls.scan_for_credentials(
            "token eyJabcdefgh.eyJklmnopqr.signature123"
        )
        self.assertGreaterEqual(len(hits), 1)
        self.assertIn("jwt_shape", {h["pattern_name"] for h in hits})

    def test_scan_credentials_masks_value_in_hit(self):
        token = "abc123def456ghi789jkl012mno345xyz"
        text = f"Authorization: Bearer {token}"
        hits = ls.scan_for_credentials(text)
        self.assertGreaterEqual(len(hits), 1)
        for h in hits:
            self.assertNotIn(token, h["matched_value_masked"])
            self.assertIn("[redacted-len=", h["matched_value_masked"])


class EnsurePathWithinTests(unittest.TestCase):
    def test_ensure_path_within_inside_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            target = root / "sub" / "a.txt"
            result = ls.ensure_path_within(target, root)
            # Should be under root
            result.relative_to(root)  # no exception means under root

    def test_ensure_path_within_outside_raises(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            with self.assertRaises(PermissionError):
                ls.ensure_path_within(Path("/etc/passwd"), root)

    def test_ensure_path_within_dotdot_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            evil = root / ".." / ".." / "evil.txt"
            with self.assertRaises(PermissionError):
                ls.ensure_path_within(evil, root)


class SentinelStopTests(unittest.TestCase):
    def test_check_sentinel_stop_returns_none_when_absent(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertIsNone(ls.check_sentinel_stop(Path(td)))

    def test_check_sentinel_stop_returns_content_when_present(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "STOP").write_text("halt please")
            result = ls.check_sentinel_stop(root)
            self.assertIsNotNone(result)
            self.assertIn("halt please", result)


class GatewayHealthTests(unittest.TestCase):
    def test_check_gateway_health_unreachable_returns_false(self):
        # Port 9 (discard) reliably refuses; do not raise.
        ok, reason = ls.check_gateway_health("http://localhost:9", timeout=1)
        self.assertFalse(ok)
        self.assertIsInstance(reason, str)


class WriteHaltTests(unittest.TestCase):
    def test_write_halt_creates_file_and_jsonl(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            halt_path = ls.write_halt(root, "CREDS", {"foo": "bar"})
            self.assertTrue(halt_path.exists())
            self.assertEqual(halt_path.name, "HALT-CREDS.txt")

            log_path = root / "halt-log.jsonl"
            self.assertTrue(log_path.exists())
            lines = log_path.read_text().strip().split("\n")
            self.assertEqual(len(lines), 1)
            self.assertIn("CREDS", lines[0])
            # Make sure JSONL is well-formed
            record = json.loads(lines[0])
            self.assertEqual(record["kind"], "CREDS")


if __name__ == "__main__":
    unittest.main()
