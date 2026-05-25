import sys
import json

def main():
    if len(sys.argv) != 2:
        print("error: invalid input")
        return

    input_path = sys.argv[1]

    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except Exception:
        print("error: invalid input")
        return

    if not isinstance(data, dict) or 'allocations' not in data:
        print("error: invalid input")
        return

    allocations = data['allocations']
    if not isinstance(allocations, list):
        print("error: invalid input")
        return

    # Validate each allocation
    valid_types = {"money", "time", "material", "introduction", "care", "knowledge", "infrastructure"}
    valid_visibilities = {"public", "private"}

    for alloc in allocations:
        if not isinstance(alloc, dict):
            print("error: invalid input")
            return
        
        required_fields = ['allocation_id', 'allocation_type', 'public_summary', 
                          'recipient_visibility', 'funder_visibility', 'amount_visibility',
                          'recipient', 'funder', 'amount', 'unit', 'not_tracked_reason', 'withdrawn']
        
        for field in required_fields:
            if field not in alloc:
                print("error: invalid input")
                return
        
        if alloc['allocation_type'] not in valid_types:
            print("error: invalid input")
            return
        
        if alloc['recipient_visibility'] not in valid_visibilities:
            print("error: invalid input")
            return
        
        if alloc['funder_visibility'] not in valid_visibilities:
            print("error: invalid input")
            return
        
        if alloc['amount_visibility'] not in valid_visibilities:
            print("error: invalid input")
            return
        
        if not isinstance(alloc['withdrawn'], bool):
            print("error: invalid input")
            return
        
        # amount can be number or null
        if alloc['amount'] is not None and not isinstance(alloc['amount'], (int, float)):
            print("error: invalid input")
            return
        
        # unit can be string or null
        if alloc['unit'] is not None and not isinstance(alloc['unit'], str):
            print("error: invalid input")
            return
        
        # not_tracked_reason can be string or null
        if alloc['not_tracked_reason'] is not None and not isinstance(alloc['not_tracked_reason'], str):
            print("error: invalid input")
            return

    total = len(allocations)
    withdrawn_count = sum(1 for a in allocations if a['withdrawn'])
    not_tracked_count = sum(1 for a in allocations if not a['withdrawn'] and a['not_tracked_reason'] is not None)
    public_count = sum(1 for a in allocations if not a['withdrawn'] and a['not_tracked_reason'] is None)

    print(f"UNTRACKED ALLOCATION LEDGER ({public_count} public / {not_tracked_count} not-tracked / {withdrawn_count} withdrawn of {total} total)")
    print()

    # Process entries
    entries = []
    for alloc in allocations:
        if alloc['withdrawn']:
            continue
        
        entry_lines = []
        entry_lines.append(f"- {alloc['allocation_id']} [{alloc['allocation_type']}]:")
        entry_lines.append(f"    summary: {alloc['public_summary']}")
        
        if alloc['not_tracked_reason'] is not None:
            entry_lines.append(f"    not-tracked-by-design: {alloc['not_tracked_reason']}")
        else:
            # Not tracked by design is null, so show visibility-based fields
            if alloc['recipient_visibility'] == 'public':
                entry_lines.append(f"    recipient: {alloc['recipient']}")
            
            if alloc['funder_visibility'] == 'public':
                entry_lines.append(f"    funder: {alloc['funder']}")
            
            if alloc['amount_visibility'] == 'public' and alloc['amount'] is not None:
                amount_str = str(alloc['amount'])
                unit_str = alloc['unit'] if alloc['unit'] else ''
                if unit_str:
                    entry_lines.append(f"    amount: {amount_str} {unit_str}")
                else:
                    entry_lines.append(f"    amount: {amount_str}")
        
        entries.append(entry_lines)

    # Print entries
    for i, entry_lines in enumerate(entries):
        for line in entry_lines:
            print(line)
        print()

    # Aggregate by type
    type_counts = {}
    for alloc in allocations:
        if alloc['withdrawn'] or alloc['not_tracked_reason'] is not None:
            continue
        alloc_type = alloc['allocation_type']
        type_counts[alloc_type] = type_counts.get(alloc_type, 0) + 1

    print("AGGREGATE BY TYPE:")
    for alloc_type in sorted(type_counts.keys()):
        print(f"  {alloc_type}: {type_counts[alloc_type]} entries")

if __name__ == "__main__":
    main()