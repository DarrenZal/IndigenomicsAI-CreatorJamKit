#!/usr/bin/env python3
import sys
import json

def error():
    print("error:")
    sys.exit(0)

def main():
    if len(sys.argv) != 2:
        error()
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        error()

    if not isinstance(data, dict) or 'allocations' not in data:
        error()
    allocations = data['allocations']
    if not isinstance(allocations, list):
        error()

    # Validate each allocation has required keys
    required_keys = {
        "allocation_id", "allocation_type", "public_summary",
        "recipient_visibility", "funder_visibility", "amount_visibility",
        "recipient", "funder", "amount", "unit",
        "not_tracked_reason", "withdrawn"
    }
    for alloc in allocations:
        if not isinstance(alloc, dict):
            error()
        if not required_keys.issubset(alloc.keys()):
            error()

    total = len(allocations)
    withdrawn_cnt = sum(1 for a in allocations if a.get('withdrawn') is True)
    not_tracked_cnt = sum(1 for a in allocations
                          if not a.get('withdrawn') and a.get('not_tracked_reason') is not None)
    public_cnt = sum(1 for a in allocations
                     if not a.get('withdrawn') and a.get('not_tracked_reason') is None)

    out_lines = []
    header = (f"UNTRACKED ALLOCATION LEDGER "
              f"({public_cnt} public / {not_tracked_cnt} not-tracked / "
              f"{withdrawn_cnt} withdrawn of {total} total)")
    out_lines.append(header)
    out_lines.append("")  # blank line after header

    # Process entries (skip withdrawn)
    for alloc in allocations:
        if alloc.get('withdrawn'):
            continue  # skip listing
        aid = alloc['allocation_id']
        atype = alloc['allocation_type']
        summary = alloc['public_summary']
        not_tracked_reason = alloc.get('not_tracked_reason')
        out_lines.append(f"- {aid} [{atype}]:")
        out_lines.append(f"    summary: {summary}")

        if not_tracked_reason is not None:
            # not-tracked overrides visibility
            out_lines.append(f"    not-tracked-by-design: {not_tracked_reason}")
        else:
            # recipient
            if alloc.get('recipient_visibility') == 'public':
                out_lines.append(f"    recipient: {alloc.get('recipient')}")
            # funder
            if alloc.get('funder_visibility') == 'public':
                out_lines.append(f"    funder: {alloc.get('funder')}")
            # amount
            if (alloc.get('amount_visibility') == 'public' and
                alloc.get('amount') is not None):
                amount = alloc['amount']
                unit = alloc.get('unit')
                if unit:
                    out_lines.append(f"    amount: {amount} {unit}")
                else:
                    out_lines.append(f"    amount: {amount}")

        out_lines.append("")  # blank line after each entry

    # Aggregate by type (only public entries)
    agg_counts = {}
    for alloc in allocations:
        if alloc.get('withdrawn'):
            continue
        if alloc.get('not_tracked_reason') is not None:
            continue
        atype = alloc['allocation_type']
        agg_counts[atype] = agg_counts.get(atype, 0) + 1

    out_lines.append("AGGREGATE BY TYPE:")
    for atype in sorted(agg_counts):
        count = agg_counts[atype]
        out_lines.append(f"  {atype}: {count} entries")

    sys.stdout.write("\n".join(out_lines))

if __name__ == "__main__":
    main()