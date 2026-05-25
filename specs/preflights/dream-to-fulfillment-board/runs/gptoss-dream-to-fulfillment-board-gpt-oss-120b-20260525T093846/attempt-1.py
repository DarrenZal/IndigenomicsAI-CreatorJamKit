#!/usr/bin/env python3
import sys
import json
from datetime import date

def main():
    if len(sys.argv) < 2:
        print("error:")
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("error:")
        return

    items = data.get("items", [])
    if not isinstance(items, list):
        items = []

    valid_stages = [
        "dream",
        "offer_or_need",
        "promise",
        "witnessed",
        "fulfilled",
        "withdrawn",
    ]

    kept = []
    for it in items:
        if not isinstance(it, dict):
            continue
        if not it.get("id"):
            continue
        stage = it.get("stage")
        if stage not in valid_stages:
            continue
        # Ensure updated_at exists and is a valid date; if not, skip item
        upd = it.get("updated_at")
        try:
            dt = date.fromisoformat(upd)
        except Exception:
            continue
        it["_date_obj"] = dt
        kept.append(it)

    K = len(kept)
    distinct_stages = {it["stage"] for it in kept}
    S = len(distinct_stages)

    print(f"DREAM-TO-FULFILLMENT BOARD ({K} items across {S} stages)")
    print()

    for stage in valid_stages:
        stage_items = [it for it in kept if it["stage"] == stage]
        if not stage_items:
            continue

        # Sort: id ascending, then date descending (stable sorts)
        stage_items.sort(key=lambda x: x["id"])
        stage_items.sort(key=lambda x: x["_date_obj"], reverse=True)

        print(f"## {stage} ({len(stage_items)})")
        for it in stage_items:
            title = it.get("title", "")
            print(f"- {it['id']}: {title}")
        print()

if __name__ == "__main__":
    main()