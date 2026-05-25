#!/usr/bin/env python3
"""Acceptance test for the Kelp Bed Watch sample build attempt.

Invokes the generated tool against several JSON fixtures and checks stdout
matches expected output. Standard library only.

Usage:
    python3 acceptance-test.py path/to/tool.py
"""

import json
import os
import subprocess
import sys
import tempfile


def run_tool(tool_path: str, payload) -> tuple[int, str, str]:
    """Write payload as JSON, run the tool against it, return (rc, stdout, stderr)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        if isinstance(payload, str):
            f.write(payload)
        else:
            json.dump(payload, f)
        input_path = f.name
    try:
        result = subprocess.run(
            ["python3", tool_path, input_path],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(input_path)


def assert_eq(name: str, expected: str, actual: str) -> bool:
    if expected == actual:
        print(f"PASS  {name}")
        return True
    print(f"FAIL  {name}")
    print("  expected:")
    for line in expected.split("\n"):
        print(f"    >{line}")
    print("  actual:")
    for line in actual.split("\n"):
        print(f"    >{line}")
    return False


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 acceptance-test.py <tool.py>", file=sys.stderr)
        return 2
    tool = sys.argv[1]
    if not os.path.exists(tool):
        print(f"tool not found: {tool}", file=sys.stderr)
        return 2

    passed = 0
    failed = 0

    # T1: minimal happy path, two sites two indicators
    payload = {"observations": [
        {"id": "a", "site": "Spanish Banks", "date": "2026-04-20", "indicator": "canopy_percent", "value": 22.3},
        {"id": "b", "site": "Spanish Banks", "date": "2026-05-04", "indicator": "canopy_percent", "value": 25.7},
        {"id": "c", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "shoot_density", "value": 100},
        {"id": "d", "site": "Boundary Bay", "date": "2026-04-26", "indicator": "shoot_density", "value": 140},
    ]}
    expected = (
        "KELP BED WATCH (4 observations across 2 sites)\n"
        "== boundary bay ==\n"
        "shoot_density: mean 120.00, n=2\n"
        "\n"
        "== spanish banks ==\n"
        "canopy_percent: mean 24.00, n=2\n"
        "\n"
        "SUMMARY: 4 observations, 2 sites, 2026-04-12 .. 2026-05-04\n"
    )
    rc, out, _ = run_tool(tool, payload)
    if assert_eq("T1 happy path two sites", expected, out): passed += 1
    else: failed += 1

    # T2: normalization (case + whitespace) collapses to one bucket
    payload = {"observations": [
        {"id": "a", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "Canopy_Percent", "value": 38.5},
        {"id": "b", "site": "boundary bay", "date": "2026-04-26", "indicator": "canopy_percent", "value": 41.0},
        {"id": "c", "site": "  Boundary  Bay ", "date": "2026-05-10", "indicator": "CANOPY_PERCENT", "value": 44.2},
    ]}
    expected = (
        "KELP BED WATCH (3 observations across 1 sites)\n"
        "== boundary bay ==\n"
        "canopy_percent: mean 41.23, n=3\n"
        "\n"
        "SUMMARY: 3 observations, 1 sites, 2026-04-12 .. 2026-05-10\n"
    )
    rc, out, _ = run_tool(tool, payload)
    if assert_eq("T2 normalization collapse", expected, out): passed += 1
    else: failed += 1

    # T3: drop rules — bad value, empty site, empty indicator
    payload = {"observations": [
        {"id": "a", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": 38.5},
        {"id": "b", "site": "", "date": "2026-04-12", "indicator": "canopy_percent", "value": 50.0},
        {"id": "c", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "  ", "value": 50.0},
        {"id": "d", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": "string"},
        {"id": "e", "site": "Boundary Bay", "date": "2026-04-12", "indicator": "canopy_percent", "value": None},
    ]}
    expected = (
        "KELP BED WATCH (1 observations across 1 sites)\n"
        "== boundary bay ==\n"
        "canopy_percent: mean 38.50, n=1\n"
        "\n"
        "SUMMARY: 1 observations, 1 sites, 2026-04-12 .. 2026-04-12\n"
    )
    rc, out, _ = run_tool(tool, payload)
    if assert_eq("T3 drop rules", expected, out): passed += 1
    else: failed += 1

    # T4: empty observations
    payload = {"observations": []}
    expected = (
        "KELP BED WATCH (0 observations across 0 sites)\n"
        "SUMMARY: 0 observations, 0 sites, no dates\n"
    )
    rc, out, _ = run_tool(tool, payload)
    if assert_eq("T4 empty observations", expected, out): passed += 1
    else: failed += 1

    # T5: invalid JSON → error: prefix, exit 0
    rc, out, _ = run_tool(tool, "this is not json {{{")
    if rc == 0 and out.startswith("error:"):
        print("PASS  T5 invalid JSON")
        passed += 1
    else:
        print(f"FAIL  T5 invalid JSON: rc={rc}, out={out!r}")
        failed += 1

    # T6: indicator ordering alphabetical within site
    payload = {"observations": [
        {"id": "a", "site": "Site A", "date": "2026-04-01", "indicator": "zeta", "value": 1.0},
        {"id": "b", "site": "Site A", "date": "2026-04-01", "indicator": "alpha", "value": 2.0},
        {"id": "c", "site": "Site A", "date": "2026-04-01", "indicator": "mu", "value": 3.0},
    ]}
    expected = (
        "KELP BED WATCH (3 observations across 1 sites)\n"
        "== site a ==\n"
        "alpha: mean 2.00, n=1\n"
        "mu: mean 3.00, n=1\n"
        "zeta: mean 1.00, n=1\n"
        "\n"
        "SUMMARY: 3 observations, 1 sites, 2026-04-01 .. 2026-04-01\n"
    )
    rc, out, _ = run_tool(tool, payload)
    if assert_eq("T6 indicator alphabetical", expected, out): passed += 1
    else: failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
