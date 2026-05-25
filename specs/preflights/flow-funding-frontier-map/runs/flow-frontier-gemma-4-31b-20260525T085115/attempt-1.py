import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, ValueError):
        print("error:")
        sys.exit(0)

    nodes_list = data.get("nodes", [])
    edges_list = data.get("edges", [])

    # Map nodes by ID for quick lookup
    nodes_map = {node["id"]: node for node in nodes_list if "id" in node}
    
    fundable_edges = []
    total_edges = len(edges_list)

    for edge in edges_list:
        from_id = edge.get("from")
        to_id = edge.get("to")
        kind = edge.get("kind")
        
        from_node = nodes_map.get(from_id)
        to_node = nodes_map.get(to_id)
        
        if not from_node or not to_node:
            continue
            
        f_type = from_node.get("type")
        f_status = from_node.get("status")
        t_type = to_node.get("type")
        t_status = to_node.get("status")
        
        is_fundable = False
        
        # Condition 1: dream (open) -> commitment (open)
        if (f_type == "dream" and t_type == "commitment" and 
            f_status == "open" and t_status == "open"):
            is_fundable = True
        # Condition 2: commitment (witnessed) -> pool (open)
        elif (f_type == "commitment" and t_type == "pool" and 
              f_status == "witnessed" and t_status == "open"):
            is_fundable = True
            
        if is_fundable:
            fundable_edges.append({
                "from": from_id,
                "from_type": f_type,
                "kind": kind,
                "to": to_id,
                "to_type": t_type
            })

    f_count = len(fundable_edges)
    e_count = total_edges
    n_count = len(nodes_list)

    print(f"FLOW FUNDING FRONTIER ({f_count} fundable / {e_count} total edges)")
    print()

    for fe in fundable_edges:
        print(f"- {fe['from']}({fe['from_type']}) --[{fe['kind']}]--> {fe['to']}({fe['to_type']})")
        print()

    print(f"SUMMARY: {f_count} fundable, {n_count} nodes, {e_count} edges")

if __name__ == "__main__":
    main()