#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        # No input path provided; nothing to do per spec
        return

    input_path = sys.argv[1]

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        print('error:')
        sys.exit(0)

    # Extract required fields with defaults to avoid crashes if missing
    briefing_title = data.get('briefing_title', '')
    as_of = data.get('as_of', '')
    claims = data.get('claims', [])
    evidence_count = data.get('evidence_count', 0)
    observation_count = data.get('observation_count', 0)
    reviewer = data.get('reviewer')

    lines = [
        f"# {briefing_title}",
        "",
        f"_as of {as_of}_",
        "",
        "## Inputs",
        "",
        f"- claims: {len(claims)}",
        "",
        f"- evidence pointers: {evidence_count}",
        "",
        f"- observations: {observation_count}",
        "",
        "## Reviewer",
        "",
        "NOT YET REVIEWED" if reviewer is None else str(reviewer),
        "",
        "## Boundary",
        "",
        "This briefing summarizes inputs. It does not certify, score, or authorize any action."
    ]

    output = "\n".join(lines)
    print(output)

if __name__ == "__main__":
    main()