#!/usr/bin/env python3
import sys
import json
from collections import Counter

def main():
    if len(sys.argv) < 2:
        print("error: missing input file path")
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"error: {e}")
        return

    actions = data.get("actions", [])
    total = len(actions)
    public_actions = [a for a in actions if a.get("steward_visibility") == "public"]
    private_actions = [a for a in actions if a.get("steward_visibility") == "private"]
    public_count = len(public_actions)
    private_count = len(private_actions)

    # Header
    print(f"PRIVATE LEARNING LEDGER ({public_count} public / {private_count} hidden of {total} total)")
    print()

    # Action lines in input order
    for act in actions:
        aid = act.get("action_id", "")
        atype = act.get("action_type", "")
        visibility = act.get("steward_visibility", "")
        if visibility == "public":
            outcome = act.get("outcome_summary", "")
            print(f"{aid} [{atype}]: {outcome}")
        else:
            print(f"{aid} [{atype}]: held by steward")
    print()

    # Counts by action type
    type_counter = Counter()
    for act in actions:
        atype = act.get("action_type", "")
        type_counter[atype] += 1

    print("BY ACTION TYPE:")
    for atype in sorted(type_counter):
        print(f"  {atype}: {type_counter[atype]}")
    print()

    # Boundary statement
    print("BOUNDARY: private_notes never appear in this output. Counts do not imply judgment.")

if __name__ == "__main__":
    main()