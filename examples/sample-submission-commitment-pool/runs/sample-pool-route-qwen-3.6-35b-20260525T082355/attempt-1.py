import sys
import json
import re

def main():
    # Read input
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (IOError, OSError, json.JSONDecodeError):
        print("error: cannot read or parse input file")
        sys.exit(0)
    
    # Validate structure
    if not isinstance(data, dict):
        print("error: invalid JSON structure")
        sys.exit(0)
    
    pool_id = data.get("pool_id", "")
    offers = data.get("offers", [])
    needs = data.get("needs", [])
    
    if not isinstance(offers, list) or not isinstance(needs, list):
        print("error: invalid JSON structure")
        sys.exit(0)
    
    # Normalize kind function
    def normalize_kind(kind):
        if not isinstance(kind, str):
            return ""
        # Strip whitespace from both ends
        kind = kind.strip()
        # Collapse internal runs of whitespace to a single space
        kind = re.sub(r'\s+', ' ', kind)
        # Lowercase
        kind = kind.lower()
        return kind
    
    # Check if units is a valid number
    def is_valid_units(units):
        return isinstance(units, (int, float)) and not isinstance(units, bool)
    
    # Process offers
    # For each kind, track:
    # - offered units (only from consenting offers)
    # - consenting contributors (distinct)
    # - withheld offers (for blockers)
    
    kind_offered = {}  # kind -> total units (consenting only)
    kind_contributors = {}  # kind -> set of contributors (consenting only)
    kind_withheld = {}  # kind -> list of (contributor, units) tuples
    
    for offer in offers:
        if not isinstance(offer, dict):
            continue
        
        contributor = offer.get("contributor", "")
        kind_raw = offer.get("kind", "")
        units = offer.get("units")
        consent = offer.get("consent_to_route")
        
        # Normalize kind
        kind = normalize_kind(kind_raw)
        
        # Drop if kind is empty
        if not kind:
            continue
        
        # Drop if units is not a number
        if not is_valid_units(units):
            continue
        
        # Initialize if needed
        if kind not in kind_offered:
            kind_offered[kind] = 0
            kind_contributors[kind] = set()
            kind_withheld[kind] = []
        
        # Check consent
        if consent is True:
            # Consenting offer
            kind_offered[kind] += units
            kind_contributors[kind].add(contributor)
        elif consent is False:
            # Withheld offer - add to blockers
            kind_withheld[kind].append((contributor, units))
        # If consent is neither True nor False, treat as not consenting (drop from O and C, but not dropped entirely)
        # Actually, the spec says "consent_to_route is exactly false" for withheld.
        # If it's not a boolean or not False, it's not a withheld offer.
        # But it also doesn't count toward O or C.
        # So we just ignore it for O and C, and don't add to blockers.
    
    # Process needs
    kind_needed = {}  # kind -> total units
    kind_requesters = {}  # kind -> set of requesters
    
    for need in needs:
        if not isinstance(need, dict):
            continue
        
        requester = need.get("requester", "")
        kind_raw = need.get("kind", "")
        units = need.get("units")
        
        # Normalize kind
        kind = normalize_kind(kind_raw)
        
        # Drop if kind is empty
        if not kind:
            continue
        
        # Drop if units is not a number
        if not is_valid_units(units):
            continue
        
        # Initialize if needed
        if kind not in kind_needed:
            kind_needed[kind] = 0
            kind_requesters[kind] = set()
        
        kind_needed[kind] += units
        kind_requesters[kind].add(requester)
    
    # Collect all distinct normalized kinds
    all_kinds = set()
    all_kinds.update(kind_offered.keys())
    all_kinds.update(kind_needed.keys())
    
    # Sort kinds alphabetically
    sorted_kinds = sorted(all_kinds)
    
    # Print header
    print(f"POOL ROUTING DIAGNOSTIC — {pool_id}")
    print()
    
    # Print per-kind blocks
    for kind in sorted_kinds:
        O = kind_offered.get(kind, 0)
        C = len(kind_contributors.get(kind, set()))
        D = kind_needed.get(kind, 0)
        R = len(kind_requesters.get(kind, set()))
        
        # Determine status
        if D == 0 and O == 0:
            status = "idle"
        elif D == 0 and O > 0:
            status = "no demand"
        elif O >= D and D > 0:
            status = "fits"
        elif O < D and D > 0:
            status = f"short by {D - O} units"
        else:
            # O == 0 and D > 0
            status = "no supply"
        
        print(f"kind: {kind}")
        print(f"offered: {O} units ({C} contributors consenting)")
        print(f"needed: {D} units ({R} requesters)")
        print(f"status: {status}")
        print()
    
    # Print blockers
    print("BLOCKERS:")
    
    # Collect all withheld offers
    all_blockers = []
    for kind in kind_withheld:
        for contributor, units in kind_withheld[kind]:
            all_blockers.append((contributor, kind, units))
    
    if not all_blockers:
        print("none")
    else:
        # Sort by contributor ascending, then by kind ascending
        all_blockers.sort(key=lambda x: (x[0], x[1]))
        
        for contributor, kind, units in all_blockers:
            print(f"- {contributor} withheld consent on {kind} ({units} units)")

if __name__ == "__main__":
    main()