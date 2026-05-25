#!/usr/bin/env python3
"""spec-linter — flag the 5 most-common failure modes in a draft spec before freeze.

A jam-day mentor tool. Read a team-submission-v0 draft and flag patterns observed
in overnight preflights:

1. Optional CLI argument with no test coverage
2. Markdown/text-format output with no whitespace assertion in tests
3. Empty 'witnessed_working.acceptance_criteria' or fewer than 3 criteria
4. 'ai_input_scope: none' but build_request.path uses 'telus-lane'
5. Spec text mentions a model behavior that the model can't actually do

Usage:
    python3 spec-linter.py <team-submission-v0.json>

Standard library only. Read-only.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def lint(submission: dict) -> list:
    findings = []
    spec_text = (submission.get("spec") or {}).get("text", "") or ""
    spec_lower = spec_text.lower()
    witnessed = submission.get("witnessed_working") or {}
    criteria = witnessed.get("acceptance_criteria") or []
    auth = submission.get("authorization") or {}
    build_req = submission.get("build_request") or {}

    # Check 1: optional CLI argument
    # heuristic: spec mentions square brackets like [optional] or [--flag] or "(optional)"
    optional_patterns = [
        r"\[\s*[A-Z_a-z0-9-]+\s*\]",      # [foo]
        r"\(optional\)",
        r"\boptional(?:ly)?\b\s+(arg|argument|flag|parameter|param)",
    ]
    found_optional = []
    for pat in optional_patterns:
        m = re.search(pat, spec_text)
        if m:
            found_optional.append(m.group(0))
            break
    if found_optional:
        # Check if acceptance criteria mentions the optional arg explicitly
        if not any("optional" in c.lower() or any(o.strip("[]()").lower() in c.lower() for o in found_optional)
                   for c in criteria):
            findings.append({
                "rule": "optional_cli_arg_no_test_coverage",
                "severity": "high",
                "detail": f"spec mentions an optional argument ({found_optional[0]!r}) but acceptance_criteria don't appear to exercise it",
                "fix": "either make the argument required, or add an acceptance criterion that explicitly tests the optional-arg path (e.g., 'when <arg> is provided, output ...')",
                "evidence_from_preflights": "overnight: both Witness Validator and Claims Coherence Report failed for this exact reason — models don't wire up optional args",
            })

    # Check 2: markdown output without explicit whitespace assertion
    has_markdown_signal = bool(re.search(r"\b(markdown|md|`\s*#+\s*`|`\s*>\s*`|`\s*-\s*`|render markdown)\b", spec_lower))
    has_whitespace_signal = bool(re.search(r"(blank line|exactly one|whitespace|newline)", " ".join(criteria).lower() + " " + spec_lower))
    if has_markdown_signal and not has_whitespace_signal:
        findings.append({
            "rule": "markdown_output_no_whitespace_assertion",
            "severity": "high",
            "detail": "spec asks for markdown output but neither the spec nor acceptance criteria assert explicit whitespace rules",
            "fix": "add at least one acceptance criterion specifying blank-line placement (e.g., 'one blank line after each block, including the last')",
            "evidence_from_preflights": "overnight: Story Receipts Wall — Qwen 5/7 no-change because markdown blank-line rules were inferred not asserted",
        })

    # Check 3: thin acceptance criteria
    if len(criteria) < 3:
        findings.append({
            "rule": "acceptance_criteria_too_thin",
            "severity": "high",
            "detail": f"only {len(criteria)} acceptance criteria — typical preflighted specs had 6–8",
            "fix": "add criteria for: happy path, drop/skip rules, error handling, edge cases (empty, normalization, etc.)",
        })

    # Check 4: ai_input_scope none but telus-lane path
    if auth.get("ai_input_scope") == "none" and build_req.get("path") in ("telus-lane", "mixed"):
        findings.append({
            "rule": "ai_input_scope_none_but_telus_lane",
            "severity": "blocker",
            "detail": "authorization.ai_input_scope is 'none' but build_request.path is '" + build_req.get("path") + "' — the exporter will refuse to produce a runtime packet",
            "fix": "either change build_request.path to 'hand' or 'own-ai', or raise ai_input_scope to 'partial' (with named cleared parts) or 'whole'",
        })

    # Check 5: spec mentions capabilities the model can't do
    no_can_do = [
        ("network", "tools must be stdlib-only / no network — but spec says 'fetch', 'download', 'HTTP', or 'API'"),
        ("database", "tools must have no database access — spec mentions database"),
        ("install", "tools are single-file — installing additional packages is out of scope for the v0 lane"),
    ]
    for token, desc in no_can_do:
        # Match more carefully — avoid false positives like "no network" in constraints
        # We want positive mentions (e.g., "fetches from https://...")
        if re.search(rf"\b(fetch|download|http|api)\b.*\b(from|to|via)\b", spec_lower) and token == "network":
            findings.append({
                "rule": "spec_implies_network_access",
                "severity": "blocker",
                "detail": desc,
                "fix": "remove network-dependent behavior; the lane runs in a scrubbed environment with no network",
            })
            break

    # Check 6 (bonus): boundaries declared but disallowed_use missing
    boundaries = submission.get("boundaries", []) or []
    for b in boundaries:
        bid = b.get("id") or b.get("label", "?")
        if not b.get("disallowed_use"):
            findings.append({
                "rule": "boundary_missing_disallowed_use",
                "severity": "medium",
                "detail": f"boundary {bid!r} has no 'disallowed_use' list — exporter cannot enforce specific exclusions",
                "fix": "add disallowed_use like ['summarize', 'tag', 'embed', 'route', 'transform', 'send-to-ai'] tailored to the boundary",
            })

    # Check 7 (bonus): no freeze checklist filled
    fz = submission.get("freeze", {}) or {}
    if fz.get("status") != "frozen":
        findings.append({
            "rule": "not_frozen",
            "severity": "info",
            "detail": f"freeze.status is '{fz.get('status', 'absent')}' — submission cannot enter the build lane until frozen",
            "fix": "review with facilitator + complete the freeze checklist + set freeze.status = 'frozen'",
        })

    return findings


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("path", help="team-submission-v0 JSON")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    try:
        sub = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    findings = lint(sub)

    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
        return 0 if not findings else 1

    n_blocker = sum(1 for f in findings if f["severity"] == "blocker")
    n_high = sum(1 for f in findings if f["severity"] == "high")
    n_med = sum(1 for f in findings if f["severity"] == "medium")
    n_info = sum(1 for f in findings if f["severity"] == "info")

    print(f"SPEC LINT: {path}")
    print(f"  blocker: {n_blocker}, high: {n_high}, medium: {n_med}, info: {n_info}")
    print()

    if not findings:
        print("CLEAN — no issues flagged.")
        return 0

    for f in findings:
        print(f"[{f['severity']}] {f['rule']}")
        print(f"  detail: {f['detail']}")
        print(f"  fix: {f['fix']}")
        if "evidence_from_preflights" in f:
            print(f"  evidence: {f['evidence_from_preflights']}")
        print()

    return 1 if n_blocker or n_high else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
