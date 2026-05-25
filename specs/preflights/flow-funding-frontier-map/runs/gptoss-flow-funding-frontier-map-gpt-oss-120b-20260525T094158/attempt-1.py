#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: missing input file path")
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"error: {e}")
        return

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Build node lookup by id
    node_by_id = {node.get("id"): node for node in nodes}

    fundable_edges = []

    for edge in edges:
        from_id = edge.get("from")
        to_id = edge.get("to")
        kind = edge.get("kind", "")

        from_node = node_by_id.get(from_id)
        to_node = node_by_id.get(to_id)

        if not from_node or not to_node:
            continue  # skip edges with missing nodes

        f_type = from_node.get("type")
        f_status = from_node.get("status")
        t_type = to_node.get("type")
        t_status = to_node.get("status")

        # Check fundable conditions
        if (f_type == "dream" and t_type == "commitment" and
                f_status == "open" and t_status == "open"):
            fundable_edges.append((from_node, to_node, kind))
        elif (f_type == "commitment" and t_type == "pool" and
                f_status == "witnessed" and t_status == "open"):
            fundable_edges.append((from_node, to_node, kind))

    F = len(fundable_edges)
    E = len(edges)
    N = len(nodes)

    # Output
    print(f"FLOW FUNDING FRONTIER ({F} fundable / {E} total edges)")
    print()
    for from_node, to_node, kind in fundable_edges:
        print(f"- {from_node['id']}({from_node['type']}) --[{kind}]--> {to_node['id']}({to_node['type']})")
    print()
    print(f"SUMMARY: {F} fundable, {N} nodes, {E} edges")

if __name__ == "__main__":
    main()