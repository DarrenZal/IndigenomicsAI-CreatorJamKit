"""Tests for scripts/jam/bus_server.py — stdlib-only (unittest).

Boots the server in a thread per test, hits via urllib.

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_bus_server -v
"""

import json
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import bus  # noqa: E402
from jam import bus_server as srv  # noqa: E402


WRITE_TOKEN = "test-bus-token-12345"


def _post(url, body, token=None):
    data = json.dumps(body).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode(), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


def _get(url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.getcode(), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body


class BusServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.bus_root = Path(cls.tmp) / "bus"
        cls.port = 18765  # avoid colliding with the production default
        cls.host = "127.0.0.1"
        cls.base = f"http://{cls.host}:{cls.port}"
        # boot server in a thread
        cls.httpd = srv.serve(
            cls.bus_root, cls.host, cls.port, WRITE_TOKEN, read_auth_required=False
        )
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        # tiny wait so port is bound
        time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=1)

    def _valid_share_request(self):
        msg = bus.make_envelope("team-A", "team-B", "share_request")
        msg["payload"] = {
            "what": {"content_kind": "offering",
                     "preview": {"mode": "paraphrased", "body": "hello"}},
            "why": {"intent": "Combine our kelp-cover with your salmon counts"},
            "consent_terms": {"display_scope": "partial",
                              "ai_input_scope": "none",
                              "reuse_scope": "ask-first"},
        }
        return msg

    def test_health(self):
        code, body = _get(f"{self.base}/health")
        self.assertEqual(code, 200)
        self.assertEqual(body["status"], "ok")

    def test_post_message_unauthorized(self):
        code, body = _post(f"{self.base}/messages", self._valid_share_request())
        self.assertEqual(code, 401)

    def test_post_message_wrong_token(self):
        code, body = _post(f"{self.base}/messages", self._valid_share_request(),
                            token="wrong-token")
        self.assertEqual(code, 401)

    def test_post_message_valid(self):
        msg = self._valid_share_request()
        code, body = _post(f"{self.base}/messages", msg, token=WRITE_TOKEN)
        self.assertEqual(code, 200)
        self.assertEqual(body["message_id"], msg["message_id"])
        self.assertEqual(body["message_type"], "share_request")

    def test_post_message_invalid_payload_rejected(self):
        msg = bus.make_envelope("team-A", "team-B", "share_request")
        msg["payload"] = {}  # missing required fields
        code, body = _post(f"{self.base}/messages", msg, token=WRITE_TOKEN)
        self.assertEqual(code, 422)
        self.assertEqual(body["error"], "validation failed")

    def test_post_silent_share_rejected(self):
        """Protected-content leak via marker_only should be rejected."""
        msg = bus.make_envelope("team-A", "team-B", "share_request")
        msg["payload"] = {
            "what": {"content_kind": "offering",
                     "preview": {"mode": "marker_only",
                                 "body": "[PROTECTED] cultural content leaking"}},
            "why": {"intent": "Trying to leak via marker mode"},
            "consent_terms": {"display_scope": "whole", "ai_input_scope": "whole",
                              "reuse_scope": "public-ok"},
        }
        code, body = _post(f"{self.base}/messages", msg, token=WRITE_TOKEN)
        self.assertEqual(code, 422)

    def test_get_team_messages(self):
        # post one message, then read team A's log via HTTP
        msg = self._valid_share_request()
        msg["from_agent"]["team_id"] = "team-readtest"
        msg["to_agent"]["team_id"] = "team-X"
        code, _ = _post(f"{self.base}/messages", msg, token=WRITE_TOKEN)
        self.assertEqual(code, 200)
        code, body = _get(f"{self.base}/teams/team-readtest")
        self.assertEqual(code, 200)
        self.assertEqual(body["team_id"], "team-readtest")
        self.assertGreaterEqual(body["count"], 1)

    def test_get_global_log(self):
        code, body = _get(f"{self.base}/global")
        self.assertEqual(code, 200)
        self.assertGreaterEqual(body["count"], 0)
        self.assertIsInstance(body["messages"], list)

    def test_get_audit_global(self):
        code, body = _get(f"{self.base}/audit")
        self.assertEqual(code, 200)
        self.assertIn("ok", body)
        self.assertIn("lines", body)

    def test_get_audit_team(self):
        code, body = _get(f"{self.base}/audit/team-readtest")
        self.assertEqual(code, 200)
        self.assertEqual(body.get("team_id"), "team-readtest")

    def test_team_id_traversal_rejected(self):
        """Path traversal in team_id is refused."""
        code, body = _get(f"{self.base}/teams/..%2Fetc%2Fpasswd")
        self.assertEqual(code, 400)

    def test_unknown_path_404(self):
        code, body = _get(f"{self.base}/nope")
        self.assertEqual(code, 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
