#!/usr/bin/env python3
import sys
import json

def main():
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

    # Validate structure
    if not isinstance(data, dict) or 'layers' not in data or not isinstance(data['layers'], list):
        print('error:')
        return

    layers = data['layers']

    # Counters
    total = len(layers)
    public_cnt = sum(1 for l in layers if l.get('consent_tier') == 'public')
    steward_cnt = sum(1 for l in layers if l.get('consent_tier') == 'steward-review')
    private_cnt = sum(1 for l in layers if l.get('consent_tier') == 'private')

    # Header
    print(f'LAYER BOARD ({public_cnt} public / {steward_cnt} steward-review / {private_cnt} private of {total} total layers)')
    print()

    # Public layers section
    print('PUBLIC LAYERS:')
    for layer in layers:
        if layer.get('consent_tier') == 'public':
            layer_id = layer.get('layer_id', '')
            category = layer.get('category', '')
            feature_count = layer.get('feature_count', 0)
            print(f'- {layer_id} [{category}]: {feature_count} features')
    print()

    # Withheld summary
    print(f'WITHHELD: {steward_cnt} steward-review + {private_cnt} private layers — content not displayed.')

if __name__ == '__main__':
    main()