#!/usr/bin/env python3
import sys
import json
import re

def normalize_kind(kind):
    if not isinstance(kind, str):
        return ''
    # Strip ends, collapse internal whitespace, lowercase
    kind = kind.strip()
    kind = re.sub(r'\s+', ' ', kind)
    return kind.lower()

def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def main():
    if len(sys.argv) < 2:
        print("error: missing input path")
        return
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error:")
        return

    pool_id = data.get("pool_id", "")
    offers = data.get("offers", [])
    needs = data.get("needs", [])

    # Aggregation structures
    per_kind = {}
    blockers = []  # list of (contributor, kind, units)

    def ensure_kind_entry(k):
        if k not in per_kind:
            per_kind[k] = {
                "offered_units": 0,
                "contributors": set(),
                "needed_units": 0,
                "requesters": set(),
            }

    # Process offers
    for offer in offers:
        kind_raw = offer.get("kind")
        kind = normalize_kind(kind_raw)
        units = offer.get("units")
        if not is_number(units) or kind == "":
            continue  # drop invalid offer
        consent = offer.get("consent_to_route", False)
        contributor = offer.get("contributor", "")
        if consent is True:
            ensure_kind_entry(kind)
            per_kind[kind]["offered_units"] += units
            per_kind[kind]["contributors"].add(contributor)
        else:
            # withheld consent, still a blocker
            blockers.append((contributor, kind, units))

    # Process needs
    for need in needs:
        kind_raw = need.get("kind")
        kind = normalize_kind(kind_raw)
        units = need.get("units")
        if not is_number(units) or kind == "":
            continue  # drop invalid need
        requester = need.get("requester", "")
        ensure_kind_entry(kind)
        per_kind[kind]["needed_units"] += units
        per_kind[kind]["requesters"].add(requester)

    # Output
    em_dash = "\u2014"
    print(f"POOL ROUTING DIAGNOSTIC {em_dash} {pool_id}")
    print()

    # Sort kinds alphabetically
    for kind in sorted(per_kind.keys()):
        entry = per_kind[kind]
        O = entry["offered_units"]
        C = len(entry["contributors"])
        D = entry["needed_units"]
        R = len(entry["requesters"])

        # Determine status
        if D > 0:
            if O >= D:
                status = "fits"
            else:
                diff = D - O
                # Remove trailing .0 for integers
                diff_str = str(int(diff)) if diff == int(diff) else str(diff)
                status = f"short by {diff_str} units"
        else:  # D == 0
            if O > 0:
                status = "no demand"
            else:
                status = "idle"

        # Helper to format units (remove .0 if integer)
        def fmt_units(val):
            return str(int(val)) if isinstance(val, (int, float)) and val == int(val) else str(val)

        print(f"kind: {kind}")
        print(f"offered: {fmt_units(O)} units ({C} contributors consenting)")
        print(f"needed: {fmt_units(D)} units ({R} requesters)")
        print(f"status: {status}")
        print()  # blank line after each block

    # Blockers section
    if not blockers:
        print("BLOCKERS: none")
    else:
        print("BLOCKERS:")
        # Sort blockers by contributor then kind
        blockers.sort(key=lambda x: (x[0], x[1]))
        for contributor, kind, units in blockers:
            units_str = str(int(units)) if isinstance(units, (int, float)) and units == int(units) else str(units)
            print(f"- {contributor} withheld consent on {kind} ({units_str} units)")

if __name__ == "__main__":
    main()