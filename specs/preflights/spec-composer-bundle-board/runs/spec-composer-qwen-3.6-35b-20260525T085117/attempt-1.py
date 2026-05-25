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
        print("error: invalid JSON or file not found")
        sys.exit(0)
    
    if not isinstance(data, dict) or 'fragments' not in data:
        print("error: invalid JSON structure")
        sys.exit(0)
    
    fragments = data['fragments']
    
    if not isinstance(fragments, list):
        print("error: fragments is not a list")
        sys.exit(0)
    
    # Filter valid fragments
    valid_fragments = []
    for frag in fragments:
        if not isinstance(frag, dict):
            continue
        if 'id' not in frag:
            continue
        if not isinstance(frag.get('produces'), list):
            continue
        if not isinstance(frag.get('consumes'), list):
            continue
        valid_fragments.append(frag)
    
    # Find candidate pairs
    candidate_pairs = []
    for i, a in enumerate(valid_fragments):
        for j, b in enumerate(valid_fragments):
            if i == j:
                continue
            # Check if A.produces shares at least one item with B.consumes
            shared = set(a['produces']) & set(b['consumes'])
            if shared:
                candidate_pairs.append((a['id'], b['id'], sorted(shared)))
    
    # Sort by (A.id, B.id) ascending
    candidate_pairs.sort(key=lambda x: (x[0], x[1]))
    
    # Calculate distinct interfaces
    all_interfaces = set()
    for frag in valid_fragments:
        all_interfaces.update(frag['produces'])
        all_interfaces.update(frag['consumes'])
    
    n = len(valid_fragments)
    p = len(candidate_pairs)
    s = len(all_interfaces)
    
    # Print output
    print(f"BUNDLE BOARD ({p} candidate pairs of {n} fragments)")
    print()
    
    for a_id, b_id, shared in candidate_pairs:
        shared_str = ", ".join(shared)
        print(f"{a_id} -> {b_id} via {shared_str}")
    
    print()
    print(f"SUMMARY: {p} candidate pairs, {n} fragments, {s} distinct interfaces")

if __name__ == "__main__":
    main()