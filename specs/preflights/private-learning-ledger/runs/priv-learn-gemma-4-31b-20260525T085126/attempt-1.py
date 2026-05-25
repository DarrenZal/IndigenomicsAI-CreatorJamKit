import json
import sys
from collections import Counter

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, ValueError):
        print("error:")
        sys.exit(0)

    actions = data.get("actions", [])
    
    total = len(actions)
    public_count = 0
    hidden_count = 0
    type_counts = Counter()

    # First pass to calculate totals and counts
    for action in actions:
        visibility = action.get("steward_visibility")
        if visibility == "public":
            public_count += 1
        else:
            hidden_count += 1
        
        action_type = action.get("action_type")
        if action_type:
            type_counts[action_type] += 1

    # Header
    print(f"PRIVATE LEARNING LEDGER ({public_count} public / {hidden_count} hidden of {total} total)")
    print()

    # Action list
    for action in actions:
        action_id = action.get("action_id", "unknown")
        action_type = action.get("action_type", "unknown")
        visibility = action.get("steward_visibility")
        
        if visibility == "public":
            summary = action.get("outcome_summary", "")
            print(f"{action_id} [{action_type}]: {summary}")
        else:
            print(f"{action_id} [{action_type}]: held by steward")
        print()

    # Summary by type
    print("BY ACTION TYPE:")
    for a_type in sorted(type_counts.keys()):
        print(f"  {a_type}: {type_counts[a_type]}")
    
    print()
    print("BOUNDARY: private_notes never appear in this output. Counts do not imply judgment.")

if __name__ == "__main__":
    main()