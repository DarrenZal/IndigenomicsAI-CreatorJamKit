import sys
import json
import re

def normalize_kind(kind):
    if not isinstance(kind, str):
        return ""
    # Strip whitespace from both ends
    s = kind.strip()
    # Collapse internal runs of whitespace to a single space
    s = re.sub(r'\s+', ' ', s)
    # Lowercase
    return s.lower()

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error: failed to read or parse JSON")
        sys.exit(0)

    pool_id = data.get("pool_id", "Unknown")
    offers_raw = data.get("offers", [])
    needs_raw = data.get("needs", [])

    # Data structures for aggregation
    # kind -> { 'offered_units': 0, 'consenting_contributors': set(), 'needed_units': 0, 'requesters': set() }
    stats = {}
    blockers = []

    # Process Offers
    for off in offers_raw:
        kind_raw = off.get("kind")
        units = off.get("units")
        contributor = off.get("contributor")
        consent = off.get("consent_to_route")

        # Drop rules: units must be a number, kind must not normalize to empty
        if not isinstance(units, (int, float)):
            continue
        
        norm_kind = normalize_kind(kind_raw)
        if not norm_kind:
            continue

        if norm_kind not in stats:
            stats[norm_kind] = {'offered_units': 0, 'consenting_contributors': set(), 'needed_units': 0, 'requesters': set()}

        if consent is True:
            stats[norm_kind]['offered_units'] += units
            if contributor is not None:
                stats[norm_kind]['consenting_contributors'].add(contributor)
        elif consent is False:
            blockers.append({
                'contributor': contributor if contributor is not None else "",
                'kind': norm_kind,
                'units': units
            })

    # Process Needs
    for need in needs_raw:
        kind_raw = need.get("kind")
        units = need.get("units")
        requester = need.get("requester")

        # Drop rules: units must be a number, kind must not normalize to empty
        if not isinstance(units, (int, float)):
            continue
        
        norm_kind = normalize_kind(kind_raw)
        if not norm_kind:
            continue

        if norm_kind not in stats:
            stats[norm_kind] = {'offered_units': 0, 'consenting_contributors': set(), 'needed_units': 0, 'requesters': set()}

        stats[norm_kind]['needed_units'] += units
        if requester is not None:
            stats[norm_kind]['requesters'].add(requester)

    # (1) Header
    print(f"POOL ROUTING DIAGNOSTIC — {pool_id}")
    
    # (2) Blank line
    print()

    # (3) Per-kind block
    sorted_kinds = sorted(stats.keys())
    for k in sorted_kinds:
        s = stats[k]
        o = s['offered_units']
        c = len(s['consenting_contributors'])
        d = s['needed_units']
        r = len(s['requesters'])

        # Status logic
        if o >= d and d > 0:
            status = "fits"
        elif o < d and d > 0:
            status = f"short by {d - o} units"
        elif d == 0 and o > 0:
            status = "no demand"
        elif o == 0 and d > 0:
            status = "no supply"
        else: # o == 0 and d == 0
            status = "idle"

        print(f"kind: {k}")
        print(f"offered: {o} units ({c} contributors consenting)")
        print(f"needed: {d} units ({r} requesters)")
        print(f"status: {status}")
        print() # Blank line after each block

    # (4) Blockers footer
    print("BLOCKERS:")
    if not blockers:
        print("none")
    else:
        # Sort by contributor ascending, then by kind ascending
        blockers.sort(key=lambda x: (x['contributor'], x['kind']))
        for b in blockers:
            print(f"- {b['contributor']} withheld consent on {b['kind']} ({b['units']} units)")

if __name__ == "__main__":
    main()