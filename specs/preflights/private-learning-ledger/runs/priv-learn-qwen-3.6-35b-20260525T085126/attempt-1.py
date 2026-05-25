import sys
import json

def main():
    if len(sys.argv) != 2:
        print("error: expected exactly one argument: ledger_json_path")
        sys.exit(0)

    json_path = sys.argv[1]

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError, OSError):
        print("error: invalid JSON or file not found")
        sys.exit(0)

    if not isinstance(data, dict) or 'actions' not in data:
        print("error: invalid JSON structure")
        sys.exit(0)

    actions = data['actions']
    if not isinstance(actions, list):
        print("error: actions must be a list")
        sys.exit(0)

    total = len(actions)
    public_count = 0
    hidden_count = 0

    for action in actions:
        if not isinstance(action, dict):
            continue
        visibility = action.get('steward_visibility', '')
        if visibility == 'public':
            public_count += 1
        elif visibility == 'private':
            hidden_count += 1

    print(f"PRIVATE LEARNING LEDGER ({public_count} public / {hidden_count} hidden of {total} total)")
    print()

    for action in actions:
        if not isinstance(action, dict):
            continue
        action_id = action.get('action_id', '')
        action_type = action.get('action_type', '')
        visibility = action.get('steward_visibility', '')

        if visibility == 'public':
            outcome_summary = action.get('outcome_summary', '')
            print(f"{action_id} [{action_type}]: {outcome_summary}")
        else:
            print(f"{action_id} [{action_type}]: held by steward")

    print()
    print("BY ACTION TYPE:")

    type_counts = {}
    for action in actions:
        if not isinstance(action, dict):
            continue
        action_type = action.get('action_type', '')
        if action_type:
            type_counts[action_type] = type_counts.get(action_type, 0) + 1

    for action_type in sorted(type_counts.keys()):
        print(f"  {action_type}: {type_counts[action_type]}")

    print()
    print("BOUNDARY: private_notes never appear in this output. Counts do not imply judgment.")

if __name__ == '__main__':
    main()