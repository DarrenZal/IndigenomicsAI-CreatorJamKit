#!/usr/bin/env python3
"""witness-record-validator — flag overclaim language in a Tuesday witness record.

A jam-day mentor tool. Reads a witness-record.md file, scans for phrases that imply
certification, authority, legitimacy, or reuse permission — language the kit's
discipline says witness records must not carry.

Usage:
    python3 witness-record-validator.py <witness-record.md>

Standard library only. No network. Read-only.
"""
import argparse
import re
import sys
from pathlib import Path


# Phrases the kit explicitly discourages in witness records.
# Each entry: (regex, severity, suggestion)
OVERCLAIM_PATTERNS = [
    # Certification / authority
    (r"\bcertif(ied|ication|ies)\b", "high", "witness records state what happened; they do not certify"),
    (r"\bofficially\b", "high", "remove 'officially' — implies institutional authority not granted by a witness record"),
    (r"\bauthoriz(ed|ation|es)\b", "high", "authorization is granted by people, not by witness records"),
    (r"\blegitima(te|tes|cy)\b", "high", "legitimacy is granted by community/Nation/steward authority, not by this record"),
    (r"\bapprov(ed|al|es)\b", "medium", "a witness record is not approval; if there was an approval, attribute it to the approver"),

    # Cultural authority claims
    (r"\bcommunity[- ]?approved\b", "high", "community approval requires named community + named process — do not assert generally"),
    (r"\bnation[- ]?approved\b", "high", "Nation approval requires named Nation + explicit authority — do not assert generally"),
    (r"\belders?[- ]?endorsed\b", "high", "elder endorsement requires explicit named-elder authority — do not assert generally"),

    # Reuse / readiness
    (r"\bready[- ]for[- ]reuse\b", "high", "witness records do not grant reuse permission"),
    (r"\bready[- ]for[- ]production\b", "medium", "the jam's validated scope is experimental build attempts; production is not the lane's scope"),
    (r"\bproven\b", "medium", "one build attempt is not proof — consider 'attempted' or 'tried'"),

    # Best / superlative claims
    (r"\b(best|optimal|definitive)\b", "low", "soften superlatives — witness records describe one attempt, not the best path"),

    # AI authority
    (r"\bAI[- ]validated\b", "high", "AI does not validate cultural authority or legitimacy"),
    (r"\bAI[- ]approved\b", "high", "AI does not approve"),
    (r"\bAI[- ]certif(ied|ication)\b", "high", "AI does not certify"),

    # Boundary leak indicators
    (r"\bdeconstruct(ed|ing|s)?\b", "low", "kit verb-discipline: render, surface, diagnose — not 'deconstruct'"),
    (r"\bdismantl(ed|ing|es)\b", "low", "kit verb-discipline: render, surface, diagnose — not 'dismantle'"),
]


REQUIRED_PHRASES = [
    # The receipt statement boilerplate or close variants.
    (r"\b(does not|do not)\s+(establish|certify|approve|authorize|grant)\b",
     "missing receipt statement",
     "witness records should include a 'this record does not establish authority/approval/certification/reuse' statement"),
]


DISCLAIMER_CONTEXT_REGEX = re.compile(
    # Catches: "does not establish authority, approval, certification, legitimacy"
    # and similar receipt-statement boilerplate where the words appear as a disclaimer.
    r"\b(does not|do not|never|will not|cannot|isn'?t|are not|is not)\s+"
    r"(establish|certify|approve|authorize|grant|imply|claim|constitute|carry|confer|validate)",
    re.IGNORECASE,
)


# Descriptive-negation context: when the model DESCRIBES what the tool
# does NOT do (a refusal-as-design statement), forbidden words appearing
# AFTER one of these negation markers on the same line are honest
# description, not overclaim.
#
# Added 2026-05-26 after overnight Loop 1 round 36 (publish-failed):
# the witness draft contained "...without performing routing or
# legitimacy calculations" — the model accurately reporting that the
# tool refuses to compute legitimacy. The validator caught "legitimacy"
# without the context.
DESCRIPTIVE_NEGATION_REGEX = re.compile(
    r"\b(without|deliberately\s+avoids?|explicitly\s+refuses?|"
    r"by\s+design\s+does\s+not|never\s+(?:performs|computes|claims|"
    r"asserts|grants))\b",
    re.IGNORECASE,
)


def _is_in_descriptive_negation(line: str, col: int) -> bool:
    """Check whether a descriptive-negation marker appears BEFORE the
    matched word on the same line. If so, the forbidden word is being
    used in 'the tool does not X' framing — honest description, not
    overclaim.
    """
    preceding = line[:col]
    return bool(DESCRIPTIVE_NEGATION_REGEX.search(preceding))


def _is_in_disclaimer_context(line: str, col: int, prev_lines: list = None) -> bool:
    """Check whether the matched word is part of a disclaimer (e.g., 'does not certify').

    Multi-line disclaimer statements like:

        This record states what happened. It does not establish authority,
        approval, certification, legitimacy, community consent, or readiness
        for reuse.

    span 3 lines. The disclaimer-context regex matches on line 1; the
    over-claim words appear on line 2. So we look at a 3-line lookback
    window: the line itself + the two preceding lines.

    Also checks descriptive-negation context ("without performing X")
    on the same line.
    """
    if DISCLAIMER_CONTEXT_REGEX.search(line):
        return True
    if _is_in_descriptive_negation(line, col):
        return True
    if prev_lines:
        for prev in prev_lines[-2:]:  # check up to 2 lines back
            if DISCLAIMER_CONTEXT_REGEX.search(prev):
                return True
    return False


def validate(text: str) -> dict:
    findings = []
    lines = text.split("\n")

    for pattern, severity, suggestion in OVERCLAIM_PATTERNS:
        regex = re.compile(pattern, re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            for m in regex.finditer(line):
                prev_lines = lines[max(0, i - 3):i - 1]  # up to 2 preceding lines
                if _is_in_disclaimer_context(line, m.start(), prev_lines):
                    continue  # skip — this is the boilerplate disclaimer, not overclaim
                findings.append({
                    "line": i,
                    "column": m.start() + 1,
                    "matched": m.group(0),
                    "severity": severity,
                    "suggestion": suggestion,
                    "context": line.strip()[:120],
                })

    # Required-phrase checks: each required pattern must appear at least once.
    missing_required = []
    for pattern, what, suggestion in REQUIRED_PHRASES:
        regex = re.compile(pattern, re.IGNORECASE)
        if not regex.search(text):
            missing_required.append({"missing": what, "suggestion": suggestion})

    return {"overclaim_findings": findings, "missing_required": missing_required}


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("path", help="path to witness-record.md")
    parser.add_argument("--json", action="store_true", help="output JSON instead of text")
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")

    result = validate(text)

    if args.json:
        import json
        print(json.dumps(result, indent=2))
        return 0 if not result["overclaim_findings"] and not result["missing_required"] else 1

    # Text output
    n_high = sum(1 for f in result["overclaim_findings"] if f["severity"] == "high")
    n_med = sum(1 for f in result["overclaim_findings"] if f["severity"] == "medium")
    n_low = sum(1 for f in result["overclaim_findings"] if f["severity"] == "low")
    n_missing = len(result["missing_required"])

    print(f"WITNESS RECORD VALIDATION: {path}")
    print(f"  high: {n_high}, medium: {n_med}, low: {n_low}, missing-required: {n_missing}")
    print()

    if result["overclaim_findings"]:
        print("OVERCLAIM FINDINGS:")
        for f in result["overclaim_findings"]:
            print(f"  line {f['line']} [{f['severity']}]: '{f['matched']}' — {f['suggestion']}")
            print(f"    > {f['context']}")
        print()

    if result["missing_required"]:
        print("MISSING REQUIRED:")
        for m in result["missing_required"]:
            print(f"  - {m['missing']}: {m['suggestion']}")
        print()

    if not result["overclaim_findings"] and not result["missing_required"]:
        print("CLEAN — no overclaim findings detected; required phrases present.")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
