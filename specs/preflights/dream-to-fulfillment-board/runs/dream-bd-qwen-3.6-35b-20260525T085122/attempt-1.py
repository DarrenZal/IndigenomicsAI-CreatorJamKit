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
        print("error:")
        sys.exit(0)

    valid_stages = ["dream", "offer_or_need", "promise", "witnessed", "fulfilled", "withdrawn"]
    stage_order = ["dream", "offer_or_need", "promise", "witnessed", "fulfilled", "withdrawn"]

    items = data.get("items", [])
    if not isinstance(items, list):
        print("error:")
        sys.exit(0)

    kept_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if "id" not in item or "title" not in item or "stage" not in item or "updated_at" not in item:
            continue
        if not isinstance(item["id"], str) or not isinstance(item["title"], str):
            continue
        if not isinstance(item["updated_at"], str):
            continue
        stage = item["stage"]
        if stage not in valid_stages:
            continue
        kept_items.append(item)

    # Group by stage
    stage_groups = {}
    for item in kept_items:
        stage = item["stage"]
        if stage not in stage_groups:
            stage_groups[stage] = []
        stage_groups[stage].append(item)

    # Sort items within each stage: by updated_at desc, then id asc
    for stage in stage_groups:
        stage_groups[stage].sort(key=lambda x: (-ord(x["updated_at"][0]) if x["updated_at"] else 0, x["id"]))
        # More robust sorting:
        stage_groups[stage].sort(key=lambda x: (x["updated_at"], x["id"]), reverse=False)
        # We need updated_at desc, so we can negate or use a custom key
        # Let's do it properly:
        stage_groups[stage].sort(key=lambda x: (x["updated_at"], x["id"]))
        # Now reverse the list to get desc order for updated_at, but we need stable sort
        # Actually, let's use a tuple key with negation for date
        # Since dates are YYYY-MM-DD, we can reverse the string comparison by negating
        # But simpler: sort by updated_at desc, then id asc
        stage_groups[stage].sort(key=lambda x: (x["updated_at"], x["id"]))
        # To get desc for updated_at, we can reverse the list after sorting by updated_at asc, id asc
        # But that would also reverse id order. So we need a different approach.
        # Let's use a key that inverts the date string.
        # Since dates are fixed format, we can just sort with a custom key.
        stage_groups[stage].sort(key=lambda x: (x["updated_at"], x["id"]))
        # This sorts by updated_at asc, id asc. We want updated_at desc, id asc.
        # So we can sort by (-date_value, id) but date is string.
        # Alternative: sort by updated_at desc, then id asc.
        # We can do: stage_groups[stage].sort(key=lambda x: (x["updated_at"], x["id"]), reverse=False)
        # Then reverse the list? No, that reverses both.
        # Let's use a tuple key where we invert the date.
        # Since dates are YYYY-MM-DD, we can convert to a comparable number.
        # Or we can just sort twice: first by id asc, then by updated_at desc (stable sort).
        stage_groups[stage].sort(key=lambda x: x["id"])
        stage_groups[stage].sort(key=lambda x: x["updated_at"], reverse=True)

    # Count distinct stages
    distinct_stages = set()
    for item in kept_items:
        distinct_stages.add(item["stage"])

    K = len(kept_items)
    S = len(distinct_stages)

    print(f"DREAM-TO-FULFILLMENT BOARD ({K} items across {S} stages)")
    print()

    first_block = True
    for stage in stage_order:
        if stage in stage_groups and len(stage_groups[stage]) > 0:
            if not first_block:
                print()
            first_block = False
            count = len(stage_groups[stage])
            print(f"## {stage} ({count})")
            for item in stage_groups[stage]:
                print(f"- {item['id']}: {item['title']}")

if __name__ == "__main__":
    main()