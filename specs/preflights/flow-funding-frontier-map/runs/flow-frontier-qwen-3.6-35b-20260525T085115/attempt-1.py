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
    
    try:
        nodes = data["nodes"]
        edges = data["edges"]
    except (KeyError, TypeError):
        print("error: invalid structure")
        sys.exit(0)
    
    # Build node lookup
    node_map = {}
    for node in nodes:
        try:
            node_map[node["id"]] = node
        except (KeyError, TypeError):
            continue
    
    total_edges = len(edges)
    fundable_edges = []
    
    for edge in edges:
        try:
            from_id = edge["from"]
            to_id = edge["to"]
            kind = edge["kind"]
            
            from_node = node_map.get(from_id)
            to_node = node_map.get(to_id)
            
            if from_node is None or to_node is None:
                continue
            
            from_type = from_node["type"]
            to_type = to_node["type"]
            from_status = from_node["status"]
            to_status = to_node["status"]
            
            is_fundable = False
            
            # Rule 1: from.type==dream AND to.type==commitment AND from.status==open AND to.status==open
            if (from_type == "dream" and to_type == "commitment" and 
                from_status == "open" and to_status == "open"):
                is_fundable = True
            
            # Rule 2: from.type==commitment AND to.type==pool AND from.status==witnessed AND to.status==open
            if (from_type == "commitment" and to_type == "pool" and 
                from_status == "witnessed" and to_status == "open"):
                is_fundable = True
            
            if is_fundable:
                fundable_edges.append(edge)
        except (KeyError, TypeError):
            continue
    
    F = len(fundable_edges)
    N = len(nodes)
    E = total_edges
    
    print(f"FLOW FUNDING FRONTIER ({F} fundable / {E} total edges)")
    print()
    
    for edge in fundable_edges:
        from_id = edge["from"]
        to_id = edge["to"]
        kind = edge["kind"]
        
        from_node = node_map.get(from_id, {})
        to_node = node_map.get(to_id, {})
        
        from_type = from_node.get("type", "unknown")
        to_type = to_node.get("type", "unknown")
        
        print(f"- {from_id}({from_type}) --[{kind}]--> {to_id}({to_type})")
    
    print()
    print(f"SUMMARY: {F} fundable, {N} nodes, {E} edges")

if __name__ == "__main__":
    main()