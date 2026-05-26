#!/usr/bin/env python3
"""telus_builder.py — autonomous CLI-building stage for the orchestrator.

Given a frozen agentic-build-packet-v0.json, ask TELUS to generate a
single-file Python CLI that satisfies the build_instructions +
acceptance_criteria. Run the packet's test_file against the generated
code in a sandbox. Optionally do ONE repair attempt with concrete
test feedback.

This closes the orchestrator chain fully autonomous:
  offering → drafting → BUILD (this module) → witness → wall

Builder prompt is strict about:
  - stdlib-only Python (no external imports)
  - single-file output
  - no markdown / no code fences in the output
  - the exact CLI shape from build_instructions

Sandbox:
  - tempdir with allowed_inputs files materialized
  - excluded_inputs NEVER written (their content isn't in the packet)
  - subprocess runs with no network (no special isolation beyond
    Python subprocess; the model's output isn't given network access
    because we just run python3 on the file)
  - 30s timeout per build/test execution

Repair semantics:
  - One repair attempt only (matches preflight pipeline pattern)
  - Repair receives the original code + the test output (stdout+stderr)
  - If repair still fails: finding=no-change OR failed depending on
    whether ANY tests passed

Usage from Python (called by orchestrator.py):
  from jam.telus_builder import build_from_packet
  result = build_from_packet(packet, adapter, sandbox_dir=...)
  # result = {finding, attempts, code, test_outcomes, ...}

Or CLI:
  python3 scripts/jam/telus_builder.py build <packet.json> \\
      --gateway http://localhost:8000 --team-key <key> --model telus-gemma \\
      [--sandbox-dir /tmp/build-sandbox] [--no-repair]

Boundary:
  This module produces EXPERIMENTAL build attempts. The acceptance test
  is what tells us the code works. The CLI output is NOT certified;
  it's evidence the spec was buildable with the given model + packet.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.spec_drafting_loop import GatewayModelAdapter, _strip_json_fences, make_adapter  # noqa: E402
from jam.stub_model import StubModelAdapter  # noqa: E402


BUILDER_SYSTEM_MESSAGE = (
    "You are a Code Builder for a Creator Jam team. Given a frozen "
    "agentic-build-packet-v0 JSON, you produce a single-file Python "
    "stdlib-only CLI implementing build_instructions + satisfying every "
    "acceptance_criteria item.\n\n"
    "OUTPUT FORMAT — STRICT:\n"
    "Reply with ONLY the Python source code. NO markdown. NO code "
    "fences (no ```). NO prose before or after. The first character of "
    "your reply MUST be `#` or `i` or `\"` (a comment, an import, or a "
    "docstring — i.e. the first line of a Python file). The last "
    "character MUST be a newline.\n\n"
    "CONSTRAINTS — STRICT:\n"
    "- Python 3.10+ standard library ONLY. NO `pip install`, NO "
    "non-stdlib imports (no `requests`, `httpx`, `numpy`, `pandas`, "
    "etc.). Allowed: `argparse`, `json`, `sys`, `os`, `re`, "
    "`collections`, `pathlib`, `datetime`, `hashlib`, `uuid`, "
    "`typing`, `subprocess`, `tempfile`, `dataclasses`, `string`, "
    "`io`.\n"
    "- Single file. No imports from sibling modules.\n"
    "- No network requests, no file-system access outside the input "
    "file (named by --input flag).\n"
    "- Exit cleanly on errors with non-zero code + helpful stderr.\n\n"
    "DISCIPLINE:\n"
    "- The acceptance_criteria define what 'works' means. Every "
    "criterion should be satisfied.\n"
    "- excluded_inputs are NEVER touched (their content isn't in the "
    "packet anyway). Do not pretend to access them.\n"
    "- If the build_instructions mention a refusal-clause, INCLUDE it "
    "verbatim in the CLI's output.\n"
    "- No overclaim language ('certified', 'approved', 'authorized', "
    "'validated', 'legitimate') in any output the tool produces; use "
    "alternatives ('surfaced', 'gated', 'recorded').\n"
)


REPAIR_SYSTEM_MESSAGE = (
    "You are a Code Repairer. Your previous build attempt failed the "
    "acceptance test. You will be given the original code + the exact "
    "test output (stdout+stderr). Produce a REVISED single-file Python "
    "CLI that addresses the failure.\n\n"
    "OUTPUT FORMAT — STRICT: same as builder — ONLY Python source, "
    "no fences, no prose, no markdown.\n\n"
    "Same stdlib-only + single-file constraints as the builder.\n"
    "Do not make the code worse to make the test pass — preserve "
    "the acceptance_criteria semantics. If you genuinely cannot "
    "make the test pass without sacrificing semantics, output the "
    "best version you have."
)


def _strip_code_fences(text: str) -> str:
    """Strip ```python ... ``` fences if model output any."""
    text = text.strip()
    m = re.match(r"^```(?:python|py)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].rstrip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def _call_builder(adapter, packet: Dict[str, Any], system_msg: str, user_payload: Dict[str, Any]) -> str:
    """Call TELUS via the adapter's gateway endpoint with a custom system
    message + payload. Returns the raw text reply."""
    import urllib.request
    body = json.dumps({
        "model": adapter.model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        f"{adapter.base_url}/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {adapter.team_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def _materialize_packet(packet: Dict[str, Any], sandbox: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """Materialize allowed_inputs as files; locate test_file. Returns
    (input_file_path, test_file_path)."""
    input_file = None
    for inp in packet.get("allowed_inputs", []):
        # Each entry has name, kind, content. Write as <name>.<json|md|txt>
        name = inp.get("name", "input")
        kind = inp.get("kind", "")
        content = inp.get("content", "")
        # Heuristic for extension
        if kind == "offering" or kind == "spec" or kind == "":
            ext = ".md"
        elif kind == "json":
            ext = ".json"
        else:
            ext = ".txt"
        path = sandbox / f"{name}{ext}"
        path.write_text(str(content))
        if input_file is None:
            input_file = path  # first allowed_input is the primary CLI argument

    # Test file
    test_file = None
    ac = packet.get("acceptance_criteria", {})
    if isinstance(ac, dict):
        tf = ac.get("test_file")
        if isinstance(tf, dict):
            test_content = tf.get("content")
            test_path = tf.get("path")
            if test_content:
                tname = tf.get("name", "acceptance_test.py")
                test_file = sandbox / tname
                test_file.write_text(test_content)
    return input_file, test_file


def _run_test(test_file: Optional[Path], build_file: Path, input_file: Optional[Path],
               timeout: int = 30) -> Tuple[bool, str]:
    """Run the test_file if present. Returns (passed, output).
    If no test_file: smoke-runs `python3 build_file --help`."""
    if test_file is not None:
        # Run test in build_file's directory with an env that makes
        # the build file importable / runnable
        try:
            r = subprocess.run(
                ["python3", str(test_file)],
                cwd=str(build_file.parent),
                capture_output=True, text=True, timeout=timeout,
                env={"PATH": "/usr/bin:/bin:/usr/local/bin"},
            )
            output = (r.stdout or "") + (r.stderr or "")
            return r.returncode == 0, output[:3000]
        except subprocess.TimeoutExpired:
            return False, "test timed out"
    # No test_file: smoke-run --help
    try:
        r = subprocess.run(
            ["python3", str(build_file), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode == 0, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return False, "smoke --help timed out"


def build_from_packet(
    packet: Dict[str, Any],
    adapter,
    sandbox_dir: Optional[Path] = None,
    allow_repair: bool = True,
) -> Dict[str, Any]:
    """Run a build attempt against a frozen build packet using TELUS.

    Returns a dict shaped like:
      {
        "finding": "built-clean" | "fixed" | "no-change" | "failed",
        "attempts": [{"code": "...", "test_passed": bool, "test_output": "..."}],
        "model_label": "...",
        "build_file": "/path/to/written/cli.py",
        "test_file": "/path/to/acceptance_test.py" or None,
        "sandbox": "/path/to/sandbox/dir",
        "elapsed_seconds": float,
      }
    """
    start = time.time()
    if sandbox_dir is None:
        sandbox_dir = Path(tempfile.mkdtemp(prefix="telus-build-"))
    else:
        sandbox_dir = Path(sandbox_dir)
        sandbox_dir.mkdir(parents=True, exist_ok=True)

    # Materialize allowed_inputs + test_file
    input_file, test_file = _materialize_packet(packet, sandbox_dir)

    # Build packet payload for the model
    builder_payload = {
        "team_spec": packet.get("team_spec", {}),
        "build_instructions": packet.get("build_instructions", ""),
        "acceptance_criteria": packet.get("acceptance_criteria", {}).get("description", []),
        "review_checks": packet.get("review_checks", []),
        # Don't send excluded_inputs content (it isn't there anyway) — just the names
        "excluded_input_names": [e.get("id") for e in packet.get("excluded_inputs", [])],
        "input_file_path": str(input_file) if input_file else None,
    }

    # First attempt
    raw_code = _call_builder(adapter, packet, BUILDER_SYSTEM_MESSAGE, builder_payload)
    code = _strip_code_fences(raw_code)
    build_file = sandbox_dir / "build_attempt.py"
    build_file.write_text(code)

    passed, output = _run_test(test_file, build_file, input_file)
    attempts = [{"code": code, "test_passed": passed, "test_output": output}]

    if passed:
        return {
            "finding": "built-clean",
            "attempts": attempts,
            "model_label": getattr(adapter, "model", "unknown"),
            "build_file": str(build_file),
            "test_file": str(test_file) if test_file else None,
            "sandbox": str(sandbox_dir),
            "elapsed_seconds": round(time.time() - start, 2),
        }

    # Attempt repair
    if allow_repair:
        repair_payload = {
            **builder_payload,
            "previous_code": code,
            "test_output": output,
        }
        raw_repair = _call_builder(adapter, packet, REPAIR_SYSTEM_MESSAGE, repair_payload)
        repaired_code = _strip_code_fences(raw_repair)
        build_file.write_text(repaired_code)
        passed2, output2 = _run_test(test_file, build_file, input_file)
        attempts.append({"code": repaired_code, "test_passed": passed2, "test_output": output2})
        if passed2:
            return {
                "finding": "fixed",
                "attempts": attempts,
                "model_label": getattr(adapter, "model", "unknown"),
                "build_file": str(build_file),
                "test_file": str(test_file) if test_file else None,
                "sandbox": str(sandbox_dir),
                "elapsed_seconds": round(time.time() - start, 2),
            }

    # Repair failed (or skipped) — finding = no-change (the original
    # might have been close) or failed (if both attempts produced
    # nothing usable). Heuristic: if either attempt's output mentioned
    # "OK" or test-runner-style "passed", treat as no-change; else failed.
    any_partial = any("OK" in a["test_output"] or "passed" in a["test_output"].lower()
                      for a in attempts)
    finding = "no-change" if any_partial else "failed"
    return {
        "finding": finding,
        "attempts": attempts,
        "model_label": getattr(adapter, "model", "unknown"),
        "build_file": str(build_file),
        "test_file": str(test_file) if test_file else None,
        "sandbox": str(sandbox_dir),
        "elapsed_seconds": round(time.time() - start, 2),
    }


def cmd_build(args):
    packet = json.loads(Path(args.packet).read_text())
    if args.model_source == "stub":
        # Stub builder: just return a placeholder file (for offline tests)
        sandbox = Path(args.sandbox_dir) if args.sandbox_dir else Path(tempfile.mkdtemp(prefix="stub-build-"))
        sandbox.mkdir(parents=True, exist_ok=True)
        bf = sandbox / "build_attempt.py"
        bf.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\nprint('[stub] build attempt placeholder')\n"
        )
        result = {
            "finding": "no-change",
            "attempts": [{"code": bf.read_text(), "test_passed": False, "test_output": "stub mode — no real test"}],
            "model_label": "stub",
            "build_file": str(bf),
            "test_file": None,
            "sandbox": str(sandbox),
            "elapsed_seconds": 0.01,
        }
    else:
        adapter = make_adapter("gateway", args.gateway, args.team_key, args.model)
        result = build_from_packet(packet, adapter,
                                    sandbox_dir=Path(args.sandbox_dir) if args.sandbox_dir else None,
                                    allow_repair=not args.no_repair)
    # Print summary
    print(json.dumps({
        "finding": result["finding"],
        "model_label": result["model_label"],
        "elapsed_seconds": result["elapsed_seconds"],
        "n_attempts": len(result["attempts"]),
        "test_passed_final": result["attempts"][-1]["test_passed"] if result["attempts"] else False,
        "build_file": result["build_file"],
        "sandbox": result["sandbox"],
    }, indent=2))


def main():
    ap = argparse.ArgumentParser(prog="telus_builder.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_b = sub.add_parser("build", help="build a CLI from a frozen build packet")
    ap_b.add_argument("packet", help="path to 5-agentic-build-packet-v0.json")
    ap_b.add_argument("--model-source", choices=["stub", "gateway"], default="gateway")
    ap_b.add_argument("--gateway", help="gateway base URL")
    ap_b.add_argument("--team-key", help="gateway team API key")
    ap_b.add_argument("--model", default="telus-gemma")
    ap_b.add_argument("--sandbox-dir", help="where to write build artifacts")
    ap_b.add_argument("--no-repair", action="store_true",
                       help="skip the one-shot repair attempt on test failure")
    ap_b.set_defaults(func=cmd_build)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
