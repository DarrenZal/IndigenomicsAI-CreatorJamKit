import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error:")
        sys.exit(0)

    if not isinstance(data, dict) or "allocations" not in data:
        print("error:")
        sys.exit(0)

    allocations = data["allocations"]
    if not isinstance(allocations, list):
        print("error:")
        sys.exit(0)

    n_total = len(allocations)
    p_count = 0
    t_count = 0
    w_count = 0
    
    # For aggregate counts: non-withdrawn, non-not-tracked
    type_counts = {}

    # First pass: calculate header counts
    for entry in allocations:
        withdrawn = entry.get("withdrawn", False)
        not_tracked = entry.get("not_tracked_reason")
        
        if withdrawn:
            w_count += 1
        elif not_tracked is not None:
            t_count += 1
        else:
            p_count += 1

    print(f"UNTRACKED ALLOCATION LEDGER ({p_count} public / {t_count} not-tracked / {w_count} withdrawn of {n_total} total)")
    print()

    # Second pass: render entries and calculate aggregates
    for entry in allocations:
        withdrawn = entry.get("withdrawn", False)
        if withdrawn:
            continue
            
        not_tracked = entry.get("not_tracked_reason")
        alloc_id = entry.get("allocation_id", "unknown")
        alloc_type = entry.get("allocation_type", "unknown")
        summary = entry.get("public_summary", "")

        print(f"- {alloc_id} [{alloc_type}]:")
        print(f"    summary: {summary}")

        if not_tracked is not None:
            print(f"    not-tracked-by-design: {not_tracked}")
        else:
            # Track for aggregate
            type_counts[alloc_type] = type_counts.get(alloc_type, 0) + 1
            
            if entry.get("recipient_visibility") == "public":
                print(f"    recipient: {entry.get('recipient', '')}")
            if entry.get("funder_visibility") == "public":
                print(f"    funder: {entry.get('funder', '')}")
            if entry.get("amount_visibility") == "public" and entry.get("amount") is not None:
                amount = entry.get("amount")
                unit = entry.get("unit", "")
                print(f"    amount: {amount} {unit}".strip())
        
        print()

    print("AGGREGATE BY TYPE:")
    for t in sorted(type_counts.keys()):
        print(f"  {t}: {type_counts[t]} entries")

if __name__ == "__main__":
    main()