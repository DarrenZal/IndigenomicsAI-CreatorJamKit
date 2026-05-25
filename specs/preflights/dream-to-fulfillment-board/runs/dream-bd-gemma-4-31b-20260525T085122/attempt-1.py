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

    if not isinstance(data, dict) or "items" not in data:
        # Based on spec, if JSON is valid but structure is wrong, 
        # it doesn't explicitly say 'error:', but usually implies 
        # handling the data provided. We'll treat missing 'items' as empty.
        items_list = []
    else:
        items_list = data["items"]

    if not isinstance(items_list, list):
        items_list = []

    valid_stages = ["dream", "offer_or_need", "promise", "witnessed", "fulfilled", "withdrawn"]
    
    kept_items = []
    for item in items_list:
        if not isinstance(item, dict):
            continue
        
        item_id = item.get("id")
        stage = item.get("stage")
        
        if item_id is not None and stage in valid_stages:
            kept_items.append(item)

    # Calculate K and S
    k = len(kept_items)
    present_stages = set(item["stage"] for item in kept_items)
    s = len(present_stages)

    print(f"DREAM-TO-FULFILLMENT BOARD ({k} items across {s} stages)")
    print()

    # Group items by stage
    stage_groups = {stage: [] for stage in valid_stages}
    for item in kept_items:
        stage_groups[item["stage"]].append(item)

    first_block = True
    for stage in valid_stages:
        items_in_stage = stage_groups[stage]
        if not items_in_stage:
            continue
        
        if not first_block:
            print()
        
        # Sort: updated_at desc, then id asc
        # updated_at is YYYY-MM-DD, so string sort works.
        # To sort desc for date and asc for id, we can use a custom key.
        items_in_stage.sort(key=lambda x: (x.get("updated_at", ""), x.get("id", "")), reverse=False)
        # Since we need updated_at DESC and id ASC, we can't just use reverse=True.
        # We sort by id ASC first, then by updated_at DESC (stable sort).
        items_in_stage.sort(key=lambda x: x.get("id", ""))
        items_in_stage.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

        print(f"## {stage} ({len(items_in_stage)})")
        for item in items_in_stage:
            print(f"- {item.get('id')}: {item.get('title', '')}")
        
        first_block = False

if __name__ == "__main__":
    main()