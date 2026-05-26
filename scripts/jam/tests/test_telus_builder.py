"""Tests for scripts/jam/telus_builder.py — stdlib-only (unittest).

Covers:
  - single-file mode backward compat (packet without `output_artifacts`)
  - multi-file mode routing (packet with `output_artifacts` length > 1)
  - envelope parsing happy path
  - envelope rejects unsafe filenames
  - envelope rejects placeholder content
  - envelope returns finding=failed on malformed JSON (no crash)

Gateway calls are stubbed by monkey-patching `urllib.request.urlopen`
inside the telus_builder module, so no network I/O occurs.

Run from kit root:
    python3 -m unittest scripts.jam.tests.test_telus_builder -v
"""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from jam import telus_builder as tb  # noqa: E402


# -------------------- shared fixtures --------------------

SINGLE_FILE_PACKET = {
    "schema_version": "agentic-build-packet-v0",
    "packet_id": "t-single-1",
    "team_spec": {"team_name": "Solo", "site": "other",
                  "vision": "v", "spec": "s", "build_target": "single-file CLI"},
    "freeze_record": {"frozen": True, "frozen_at": "2026-05-25T00:00:00Z"},
    "allowed_inputs": [],
    "excluded_inputs": [],
    "build_instructions": "Print the string 'hi'.",
    "acceptance_criteria": {"description": ["prints hi"]},
    "review_checks": [],
    # no output_artifacts → single-file mode
}


MULTI_FILE_PACKET = {
    "schema_version": "agentic-build-packet-v0",
    "packet_id": "t-multi-1",
    "team_spec": {"team_name": "Pair", "site": "other",
                  "vision": "v", "spec": "s", "build_target": "multi-file CLI"},
    "freeze_record": {"frozen": True, "frozen_at": "2026-05-25T00:00:00Z"},
    "allowed_inputs": [],
    "excluded_inputs": [],
    "build_instructions": "cli.py imports greet() from lib.py and prints it.",
    "acceptance_criteria": {"description": ["entrypoint prints HELLO"]},
    "review_checks": [],
    "output_artifacts": [
        {"filename": "cli.py", "kind": "python", "role": "entrypoint"},
        {"filename": "lib.py", "kind": "python", "role": "support"},
    ],
}


class _FakeAdapter:
    """Stand-in for GatewayModelAdapter — only needs base_url, team_key,
    model attributes for `_call_builder`."""

    def __init__(self, model: str = "test-model"):
        self.base_url = "http://localhost:0"
        self.team_key = "fake-key"
        self.model = model


def _fake_urlopen_returning(content: str):
    """Return a callable that mimics `urllib.request.urlopen(...)` and
    yields an OpenAI-shape JSON response whose
    `choices[0].message.content` is `content`."""

    body = json.dumps({"choices": [{"message": {"content": content}}]}).encode()

    class _Resp:
        def __init__(self, body_bytes):
            self._body = body_bytes

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self._body

    def _fake(req, timeout=None):
        return _Resp(body)

    return _fake


def _fake_urlopen_sequence(contents):
    """Return a urlopen that yields successive `contents` per call."""
    state = {"i": 0}
    bodies = [
        json.dumps({"choices": [{"message": {"content": c}}]}).encode()
        for c in contents
    ]

    class _Resp:
        def __init__(self, body_bytes):
            self._body = body_bytes

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return self._body

    def _fake(req, timeout=None):
        i = state["i"]
        if i >= len(bodies):
            i = len(bodies) - 1
        state["i"] += 1
        return _Resp(bodies[i])

    return _fake


# -------------------- envelope parsing --------------------

class EnvelopeParsingTests(unittest.TestCase):
    def test_envelope_parsing_happy_path(self):
        raw = json.dumps({"files": {
            "cli.py": "import sys\nprint('hi')\n",
            "lib.py": "def greet():\n    return 'HELLO'\n",
        }})
        files, err = tb._parse_multi_file_envelope(
            raw, declared_filenames=["cli.py", "lib.py"])
        self.assertIsNone(err, msg=f"unexpected err: {err}")
        self.assertIsNotNone(files)
        self.assertEqual(set(files.keys()), {"cli.py", "lib.py"})
        self.assertIn("HELLO", files["lib.py"])

    def test_envelope_parses_with_code_fences(self):
        raw = "```json\n" + json.dumps({"files": {
            "cli.py": "print('hi')\n",
        }}) + "\n```"
        files, err = tb._parse_multi_file_envelope(raw)
        self.assertIsNone(err)
        self.assertIn("cli.py", files)

    def test_envelope_rejects_unsafe_filenames(self):
        cases = [
            "../etc/passwd",
            "foo/bar.py",
            "~/secret.py",
            "/abs/path.py",
            "..\\windows.py",
            "",
            ".hidden.py",
            "-flag.py",
        ]
        for bad in cases:
            raw = json.dumps({"files": {bad: "print('x')\n"}})
            files, err = tb._parse_multi_file_envelope(raw)
            self.assertIsNone(files, msg=f"should reject {bad!r}")
            self.assertIn("unsafe filename", err or "",
                          msg=f"reason for {bad!r} was: {err}")

    def test_envelope_rejects_placeholder_content(self):
        cases = ["...", "", "   ", "TODO", "# TODO", "pass"]
        for bad in cases:
            raw = json.dumps({"files": {"cli.py": bad}})
            files, err = tb._parse_multi_file_envelope(raw)
            self.assertIsNone(files, msg=f"should reject content {bad!r}")
            err_l = (err or "").lower()
            self.assertTrue(
                "placeholder" in err_l or "empty" in err_l,
                msg=f"reason for {bad!r}: {err}",
            )

    def test_envelope_malformed_json_rejected(self):
        for bad in ["not json at all", "{\"files\":", "[]", "42",
                    "{\"files\": \"not-a-dict\"}", "{\"files\": {}}"]:
            files, err = tb._parse_multi_file_envelope(bad)
            self.assertIsNone(files, msg=f"should reject {bad!r}")
            self.assertIsNotNone(err)

    def test_envelope_rejects_non_stdlib_imports(self):
        raw = json.dumps({"files": {
            "cli.py": "import requests\nprint('hi')\n",
        }})
        files, err = tb._parse_multi_file_envelope(raw)
        self.assertIsNone(files)
        self.assertIn("disallowed import", err)

    def test_envelope_allows_sibling_imports(self):
        raw = json.dumps({"files": {
            "cli.py": "from lib import greet\nprint(greet())\n",
            "lib.py": "def greet():\n    return 'HELLO'\n",
        }})
        files, err = tb._parse_multi_file_envelope(
            raw, declared_filenames=["cli.py", "lib.py"])
        self.assertIsNone(err, msg=f"err: {err}")
        self.assertIsNotNone(files)

    def test_envelope_rejects_missing_declared_file(self):
        raw = json.dumps({"files": {"cli.py": "print('hi')\n"}})
        files, err = tb._parse_multi_file_envelope(
            raw, declared_filenames=["cli.py", "lib.py"])
        self.assertIsNone(files)
        self.assertIn("missing declared files", err)

    def test_envelope_rejects_extra_undeclared_file(self):
        raw = json.dumps({"files": {
            "cli.py": "print('hi')\n",
            "extra.py": "x = 1\n",
        }})
        files, err = tb._parse_multi_file_envelope(
            raw, declared_filenames=["cli.py"])
        self.assertIsNone(files)
        self.assertIn("undeclared files", err)


# -------------------- safe-filename helper --------------------

class FilenameSafetyTests(unittest.TestCase):
    def test_safe_filenames(self):
        for good in ["cli.py", "lib.py", "index.html", "style.css",
                     "script.js", "a", "a_b-c.py", "Module1.py"]:
            self.assertTrue(tb._is_safe_filename(good), msg=good)

    def test_unsafe_filenames(self):
        for bad in ["../x.py", "a/b.py", "~/x", "/etc/x", "..", ".",
                    "", "-flag", ".hidden", "a\\b.py", None]:
            self.assertFalse(tb._is_safe_filename(bad), msg=repr(bad))


# -------------------- routing: single vs multi --------------------

class ModeRoutingTests(unittest.TestCase):
    def test_single_file_mode_unchanged(self):
        """A packet WITHOUT `output_artifacts` routes to single-file
        path. We verify by inspecting the system message used in the
        gateway call."""
        sandbox = Path(tempfile.mkdtemp(prefix="tb-single-"))
        captured = {"system_msgs": []}

        single_file_code = (
            "import sys\n"
            "if __name__ == '__main__':\n"
            "    if '--help' in sys.argv:\n"
            "        print('usage: cli')\n"
            "    else:\n"
            "        print('hi')\n"
        )

        def fake_call(adapter, packet, system_msg, payload):
            captured["system_msgs"].append(system_msg)
            return single_file_code

        with mock.patch.object(tb, "_call_builder", side_effect=fake_call):
            result = tb.build_from_packet(
                SINGLE_FILE_PACKET, _FakeAdapter(),
                sandbox_dir=sandbox, allow_repair=False,
            )

        self.assertEqual(len(captured["system_msgs"]), 1)
        self.assertIs(captured["system_msgs"][0], tb.BUILDER_SYSTEM_MESSAGE)
        # No acceptance test in this packet → smoke-runs --help, which
        # the stub CLI handles cleanly.
        self.assertIn(result["finding"], ("built-clean", "fixed"))
        self.assertTrue(Path(result["build_file"]).exists())
        # Single-file shape: build_file points at the legacy
        # build_attempt.py path
        self.assertTrue(result["build_file"].endswith("build_attempt.py"))

    def test_multi_file_mode_routing(self):
        """A packet WITH `output_artifacts` length > 1 routes to
        multi-file path and uses MULTI_FILE_BUILDER_SYSTEM_MESSAGE."""
        sandbox = Path(tempfile.mkdtemp(prefix="tb-multi-"))
        captured = {"system_msgs": []}

        envelope = json.dumps({"files": {
            "cli.py": (
                "import sys\n"
                "from lib import greet\n"
                "if __name__ == '__main__':\n"
                "    if '--help' in sys.argv:\n"
                "        print('usage: cli')\n"
                "    else:\n"
                "        print(greet())\n"
            ),
            "lib.py": "def greet():\n    return 'HELLO'\n",
        }})

        def fake_call(adapter, packet, system_msg, payload):
            captured["system_msgs"].append(system_msg)
            return envelope

        with mock.patch.object(tb, "_call_builder", side_effect=fake_call):
            result = tb.build_from_packet(
                MULTI_FILE_PACKET, _FakeAdapter(),
                sandbox_dir=sandbox, allow_repair=False,
            )

        self.assertEqual(len(captured["system_msgs"]), 1)
        self.assertIs(captured["system_msgs"][0], tb.MULTI_FILE_BUILDER_SYSTEM_MESSAGE)
        # Both files written
        self.assertTrue((sandbox / "cli.py").exists())
        self.assertTrue((sandbox / "lib.py").exists())
        self.assertEqual(result.get("entrypoint"), "cli.py")
        # Smoke --help should pass cleanly
        self.assertEqual(result["finding"], "built-clean")

    def test_multi_file_failure_returns_finding_failed_no_crash(self):
        """Malformed envelope from the model → finding=failed, no
        exception."""
        sandbox = Path(tempfile.mkdtemp(prefix="tb-bad-"))

        def fake_call(adapter, packet, system_msg, payload):
            return "this is not json at all"

        with mock.patch.object(tb, "_call_builder", side_effect=fake_call):
            result = tb.build_from_packet(
                MULTI_FILE_PACKET, _FakeAdapter(),
                sandbox_dir=sandbox, allow_repair=False,
            )

        self.assertEqual(result["finding"], "failed")
        self.assertIn("failure_reason", result)
        self.assertEqual(len(result["attempts"]), 1)
        self.assertFalse(result["attempts"][0]["test_passed"])

    def test_multi_file_envelope_with_unsafe_filename_does_not_write(self):
        """If the model returns an envelope with `../etc/passwd`, the
        file must NOT be written outside the sandbox."""
        sandbox = Path(tempfile.mkdtemp(prefix="tb-unsafe-"))
        envelope = json.dumps({"files": {
            "cli.py": "print('hi')\n",
            "../escape.py": "print('escape')\n",
        }})

        def fake_call(adapter, packet, system_msg, payload):
            return envelope

        # Multi-file packet declares cli.py + lib.py; envelope above is
        # a different shape but the safety check must fire either way.
        # Build a packet that declares the unsafe name too — to prove
        # the safety check (not declared-set check) is what blocks it.
        unsafe_packet = {
            **MULTI_FILE_PACKET,
            "output_artifacts": [
                {"filename": "cli.py", "kind": "python", "role": "entrypoint"},
                {"filename": "../escape.py", "kind": "python", "role": "support"},
            ],
        }

        with mock.patch.object(tb, "_call_builder", side_effect=fake_call):
            result = tb.build_from_packet(
                unsafe_packet, _FakeAdapter(),
                sandbox_dir=sandbox, allow_repair=False,
            )

        self.assertEqual(result["finding"], "failed")
        # And no escape.py written above the sandbox
        self.assertFalse((sandbox.parent / "escape.py").exists())


# -------------------- urlopen-level integration --------------------

class GatewayUrlopenStubTests(unittest.TestCase):
    """Stubs `urllib.request.urlopen` at the import inside
    `_call_builder` so the full code path exercises actual envelope
    parsing + file writing + test running."""

    def test_multi_file_end_to_end_via_urlopen_stub(self):
        sandbox = Path(tempfile.mkdtemp(prefix="tb-e2e-"))
        envelope = json.dumps({"files": {
            "cli.py": (
                "import sys\n"
                "from lib import greet\n"
                "if __name__ == '__main__':\n"
                "    if '--help' in sys.argv:\n"
                "        print('usage: cli')\n"
                "    else:\n"
                "        print(greet())\n"
            ),
            "lib.py": "def greet():\n    return 'HELLO'\n",
        }})
        # _call_builder does `import urllib.request` locally then calls
        # urllib.request.urlopen — patch the module attribute.
        import urllib.request as urlreq
        with mock.patch.object(urlreq, "urlopen",
                               side_effect=_fake_urlopen_returning(envelope)):
            result = tb.build_from_packet(
                MULTI_FILE_PACKET, _FakeAdapter(),
                sandbox_dir=sandbox, allow_repair=False,
            )
        self.assertEqual(result["finding"], "built-clean")
        self.assertTrue((sandbox / "cli.py").exists())
        self.assertTrue((sandbox / "lib.py").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
