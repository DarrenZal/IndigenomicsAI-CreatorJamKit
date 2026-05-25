#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        return
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print('error:')
        return

    fragments_raw = data.get('fragments')
    if not isinstance(fragments_raw, list):
        fragments_raw = []

    valid = []
    for frag in fragments_raw:
        if not isinstance(frag, dict):
            continue
        fid = frag.get('id')
        prod = frag.get('produces')
        cons = frag.get('consumes')
        if not isinstance(fid, str):
            continue
        if not isinstance(prod, list) or not isinstance(cons, list):
            continue
        # ensure all items are strings (optional, but keep as is)
        prod_set = set(str(x) for x in prod)
        cons_set = set(str(x) for x in cons)
        valid.append({
            'id': fid,
            'produces': prod_set,
            'consumes': cons_set
        })

    N = len(valid)

    # distinct interfaces
    interfaces = set()
    for frag in valid:
        interfaces.update(frag['produces'])
        interfaces.update(frag['consumes'])
    S = len(interfaces)

    # candidate pairs
    candidates = []
    for a in valid:
        for b in valid:
            if a['id'] == b['id']:
                continue
            shared = a['produces'].intersection(b['consumes'])
            if shared:
                shared_list = sorted(shared)
                candidates.append((a['id'], b['id'], shared_list))

    candidates.sort(key=lambda x: (x[0], x[1]))
    P = len(candidates)

    # output
    print(f'BUNDLE BOARD ({P} candidate pairs of {N} fragments)')
    print()
    for a_id, b_id, shared_list in candidates:
        shared_str = ','.join(shared_list)
        print(f'{a_id} -> {b_id} via {shared_str}')
        print()
    print(f'SUMMARY: {P} candidate pairs, {N} fragments, {S} distinct interfaces')

if __name__ == '__main__':
    main()