import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("error:")
        sys.exit(0)

    if not isinstance(data, dict) or "fragments" not in data:
        # The spec implies we process the fragments list; if missing, we treat as empty
        fragments_raw = []
    else:
        fragments_raw = data.get("fragments", [])

    if not isinstance(fragments_raw, list):
        fragments_raw = []

    # Filter valid fragments
    valid_fragments = []
    for frag in fragments_raw:
        if not isinstance(frag, dict):
            continue
        fid = frag.get("id")
        prod = frag.get("produces")
        cons = frag.get("consumes")
        
        if fid is None or not isinstance(prod, list) or not isinstance(cons, list):
            continue
        
        valid_fragments.append({
            "id": fid,
            "produces": set(prod),
            "consumes": set(cons)
        })

    # Calculate distinct interfaces
    all_interfaces = set()
    for frag in valid_fragments:
        all_interfaces.update(frag["produces"])
        all_interfaces.update(frag["consumes"])

    # Find candidate pairs (A, B) where A.produces intersects B.consumes
    candidate_pairs = []
    for a in valid_fragments:
        for b in valid_fragments:
            if a["id"] == b["id"]:
                continue
            
            shared = a["produces"].intersection(b["consumes"])
            if shared:
                candidate_pairs.append({
                    "a_id": a["id"],
                    "b_id": b["id"],
                    "shared": sorted(list(shared))
                })

    # Sort pairs by (A.id, B.id) ascending
    candidate_pairs.sort(key=lambda x: (x["a_id"], x["b_id"]))

    # Output
    p = len(candidate_pairs)
    n = len(valid_fragments)
    s = len(all_interfaces)

    print(f"BUNDLE BOARD ({p} candidate pairs of {n} fragments)")
    print()

    for pair in candidate_pairs:
        shared_str = ", ".join(pair["shared"])
        print(f"{pair['a_id']} -> {pair['b_id']} via {shared_str}")
        print()

    print(f"SUMMARY: {p} candidate pairs, {n} fragments, {s} distinct interfaces")

if __name__ == "__main__":
    main()