import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        print("error: invalid input")
        sys.exit(0)
    
    if not isinstance(data, dict) or 'signals' not in data:
        print("error: invalid input")
        sys.exit(0)
    
    signals = data['signals']
    if not isinstance(signals, list):
        print("error: invalid input")
        sys.exit(0)
    
    total = len(signals)
    public_signals = [s for s in signals if isinstance(s, dict) and s.get('public_share', False) is True]
    public_count = len(public_signals)
    
    # Group public signals by normalized area
    area_groups = {}
    for s in public_signals:
        area = s.get('area', '')
        if not isinstance(area, str):
            continue
        # Normalize: strip, collapse whitespace, lowercase
        normalized_area = ' '.join(area.split()).lower()
        if normalized_area not in area_groups:
            area_groups[normalized_area] = []
        area_groups[normalized_area].append(s)
    
    # Print header
    print(f"RESILIENCE SIGNAL MAP ({public_count} public / {total} total)")
    print()
    
    # Sort areas alphabetically
    sorted_areas = sorted(area_groups.keys())
    
    for i, area in enumerate(sorted_areas):
        group = area_groups[area]
        count = len(group)
        
        # Collect kinds and severity markers
        kinds = set()
        markers = set()
        for s in group:
            kind = s.get('kind', '')
            if isinstance(kind, str) and kind:
                kinds.add(kind)
            marker = s.get('severity_marker', '')
            if isinstance(marker, str) and marker:
                markers.add(marker)
        
        # Sort kinds and markers alphabetically
        sorted_kinds = sorted(kinds)
        sorted_markers = sorted(markers)
        
        print(f"area: {area}")
        print(f"  signals: {count} (kinds: {', '.join(sorted_kinds)})")
        print(f"  severity markers: {', '.join(sorted_markers)}")
        
        # Print blank line between areas, but not after the last one
        if i < len(sorted_areas) - 1:
            print()
    
    print()
    print("BOUNDARY: this map does not rank, score, underwrite, or price. It states what was observed.")

if __name__ == '__main__':
    main()