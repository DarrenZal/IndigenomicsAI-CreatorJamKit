#!/usr/bin/env python3
import sys
import json
import re
from collections import defaultdict

def normalize_area(area):
    """Normalize area string: strip, collapse whitespace, lower case."""
    if not isinstance(area, str):
        return ''
    return re.sub(r'\s+', ' ', area.strip()).lower()

def main():
    # Expect a path argument
    if len(sys.argv) < 2:
        print('error:')
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print('error:')
        return

    # Validate JSON structure
    if not isinstance(data, dict) or 'signals' not in data or not isinstance(data['signals'], list):
        print('error:')
        return

    signals = data['signals']
    total_signals = len(signals)
    public_signals = [s for s in signals if s.get('public_share') is True]
    public_count = len(public_signals)

    # Group public signals by normalized area
    area_groups = defaultdict(list)
    for sig in public_signals:
        norm = normalize_area(sig.get('area', ''))
        area_groups[norm].append(sig)

    # Sort areas alphabetically
    sorted_areas = sorted(area_groups.keys())

    # Header
    print(f'RESILIENCE SIGNAL MAP ({public_count} public / {total_signals} total)')
    print()

    # Area blocks
    for idx, area in enumerate(sorted_areas):
        group = area_groups[area]
        count = len(group)

        kinds = sorted({sig.get('kind') for sig in group if isinstance(sig.get('kind'), str)})
        markers = sorted({sig.get('severity_marker') for sig in group if isinstance(sig.get('severity_marker'), str)})

        kinds_str = ', '.join(kinds)
        markers_str = ', '.join(markers)

        print(f'area: {area}')
        print(f'  signals: {count} (kinds: {kinds_str})')
        print(f'  severity markers: {markers_str}')

        # Blank line between areas (not after the last one)
        if idx != len(sorted_areas) - 1:
            print()

    # Boundary statement (no ranking keywords like "score")
    print()
    print('BOUNDARY: this map does not rank, underwrite, or price. It states what was observed.')

if __name__ == '__main__':
    main()