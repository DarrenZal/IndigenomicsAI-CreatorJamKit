#!/usr/bin/env python3
import sys
import json
import re

def normalize_kind(kind):
    if not isinstance(kind, str):
        return ''
    kind = kind.strip()
    kind = re.sub(r'\s+', ' ', kind)
    return kind.lower()

def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def fmt_number(val):
    if isinstance(val, (int, float)) and val == int(val):
        return str(int(val))
    return str(val)

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

    per_kind = {}
    blockers = []  # (contributor, kind, units)

    def ensure_kind(k):
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
            ensure_kind(kind)
            per_kind[kind]["offered_units"] += units
            per_kind[kind]["contributors"].add(contributor)
        else:
            # withheld consent, not dropped, appears in blockers
            blockers.append((contributor, kind, units))

    # Process needs
    for need in needs:
        kind_raw = need.get("kind")
        kind = normalize_kind(kind_raw)
        units = need.get("units")
        if not is_number(units) or kind == "":
            continue  # drop invalid need
        requester = need.get("requester", "")
        ensure_kind(kind)
        per_kind[kind]["needed_units"] += units
        per_kind[kind]["requesters"].add(requester)

    # Output header
    em_dash = "\u2014"
    print(f"POOL ROUTING DIAGNOSTIC {em_dash} {pool_id}")
    print()

    # Per-kind blocks
    for kind in sorted(per_kind.keys()):
        entry = per_kind[kind]
        O = entry["offered_units"]
        C = len(entry["contributors"])
        D = entry["needed_units"]
        R = len(entry["requesters"])

        # Determine status according to spec
        if D > 0:
            if O == 0:
                status = "no supply"
            elif O >= D:
                status = "fits"
            else:
                diff = D - O
                status = f"short by {fmt_number(diff)} units"
        else:  # D == 0
            if O > 0:
                status = "no demand"
            else:
                status = "idle"

        print(f"kind: {kind}")
        print(f"offered: {fmt_number(O)} units ({C} contributors consenting)")
        print(f"needed: {fmt_number(D)} units ({R} requesters)")
        print(f"status: {status}")
        print()  # blank line after block

    # Blockers footer
    if not blockers:
        print("BLOCKERS: none")
    else:
        print("BLOCKERS:")
        blockers.sort(key=lambda x: (x[0], x[1]))
        for contributor, kind, units in blockers:
            print(f"- {contributor} withheld consent on {kind} ({fmt_number(units)} units)")

if __name__ == "__main__":
    main()