import json
import sys
import re

def normalize_area(area):
    if not area:
        return ""
    # strip, collapse whitespace, lower
    return " ".join(area.strip().split()).lower()

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        print("error:")
        sys.exit(0)

    signals = data.get("signals", [])
    
    total_count = len(signals)
    public_signals = [s for s in signals if s.get("public_share") is True]
    public_count = len(public_signals)

    # Group public signals by normalized area
    area_groups = {}
    for s in public_signals:
        raw_area = s.get("area", "")
        norm_area = normalize_area(raw_area)
        if norm_area not in area_groups:
            area_groups[norm_area] = []
        area_groups[norm_area].append(s)

    # Header
    print(f"RESILIENCE SIGNAL MAP ({public_count} public / {total_count} total)")
    print()

    # Sorted areas
    sorted_areas = sorted(area_groups.keys())
    
    for i, area in enumerate(sorted_areas):
        group = area_groups[area]
        
        # Extract kinds and markers
        kinds = sorted(list(set(s.get("kind", "") for s in group if s.get("kind"))))
        markers = sorted(list(set(s.get("severity_marker", "") for s in group if s.get("severity_marker"))))
        
        print(f"area: {area}")
        print(f"  signals: {len(group)} (kinds: {', '.join(kinds)})")
        print(f"  severity markers: {', '.join(markers)}")
        
        # Blank between areas, but not after the last one
        if i < len(sorted_areas) - 1:
            print()

    # Footer
    print()
    print("BOUNDARY: this map does not rank, score, underwrite, or price. It states what was observed.")

if __name__ == "__main__":
    main()