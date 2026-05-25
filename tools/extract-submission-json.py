#!/usr/bin/env python3
"""extract-submission-json — pull the team-submission JSON out of a sample .md file.

The sample submission examples embed their team-submission-v0 JSON inside a ```json
fenced code block in markdown. This tool extracts that JSON to stdout (or to a file)
so the spec-linter and other tools can read it.

Usage:
    python3 extract-submission-json.py <sample-team-submission.md> [--out output.json]

Standard library only. Read-only on input.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def extract(text: str) -> str:
    """Find the first ```json ... ``` code block and return its contents."""
    # Match ```json (optional whitespace + newline) then capture until closing ```
    pattern = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
    m = pattern.search(text)
    if not m:
        # Try alternative fence styles
        pattern2 = re.compile(r"```\s*json\s*\n(.*?)\n```", re.DOTALL)
        m = pattern2.search(text)
    if not m:
        raise ValueError("no ```json code block found in input")
    return m.group(1)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("path", help="markdown file containing a team-submission JSON code block")
    parser.add_argument("--out", help="write extracted JSON to this path (else stdout)")
    parser.add_argument("--validate", action="store_true", help="parse + validate extracted JSON before writing")
    args = parser.parse_args(argv)

    src = Path(args.path)
    if not src.exists():
        print(f"error: file not found: {src}", file=sys.stderr)
        return 2

    text = src.read_text(encoding="utf-8")
    try:
        json_text = extract(text)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.validate:
        try:
            obj = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"error: extracted JSON is invalid: {e}", file=sys.stderr)
            return 1
        # Re-emit canonically formatted
        json_text = json.dumps(obj, indent=2)

    if args.out:
        Path(args.out).write_text(json_text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(json_text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
