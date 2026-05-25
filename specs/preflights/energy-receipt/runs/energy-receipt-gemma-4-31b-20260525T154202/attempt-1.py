import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        print("error:")
        sys.exit(0)

    team = data.get("team", "Unknown Team")
    events_list = data.get("events", [])
    
    kept_events = []
    rejected_count = 0
    total_count = 0

    for event in events_list:
        total_count += 1
        
        # Validation checks
        try:
            # Required fields presence and non-emptiness
            if not event.get("event_id") or not event.get("intention") or not event.get("model"):
                rejected_count += 1
                continue
            
            # Numeric checks
            metrics = ["input_tokens", "output_tokens", "duration_seconds", "estimated_kwh"]
            valid_metrics = True
            for m in metrics:
                val = event.get(m)
                if val is None or not isinstance(val, (int, float)):
                    valid_metrics = False
                    break
            
            if not valid_metrics:
                rejected_count += 1
                continue
            
            # Negative kWh check
            if event["estimated_kwh"] < 0:
                rejected_count += 1
                continue
                
            kept_events.append(event)
        except Exception:
            rejected_count += 1

    # Header
    print(f"ENERGY RECEIPT — {team}")
    print()

    # Event blocks
    for i, event in enumerate(kept_events):
        print(f"- event_id: {event['event_id']}")
        print(f"  intention: {event['intention']}")
        print(f"  model: {event['model']}")
        print(f"  kWh: {event['estimated_kwh']}")
        print(f"  tokens: {event['input_tokens']} in / {event['output_tokens']} out")
        print(f"  duration_s: {event['duration_seconds']}")
        print(f"  outcome: {event['outcome_summary']}")
        if i < len(kept_events) - 1:
            print()

    print()

    # Totals
    sum_kwh = sum(e['estimated_kwh'] for e in kept_events)
    sum_in = sum(e['input_tokens'] for e in kept_events)
    sum_out = sum(e['output_tokens'] for e in kept_events)
    
    models = sorted(list(set(e['model'] for e in kept_events)))
    models_str = ", ".join(models) if models else "none"

    print("TOTALS")
    print(f"  events: {len(kept_events)} kept, {rejected_count} rejected of {total_count} total")
    print(f"  kWh: {sum_kwh:.4f}")
    print(f"  tokens: {sum_in} in / {sum_out} out")
    print(f"  models: {models_str}")

    print()
    print("REFLECTION")
    print("  Did the work justify its footprint?")
    print("  What would you do differently?")
    print("  What reciprocity is owed?")
    print()
    print("BOUNDARY: This is a receipt of what was computed. It does not offset, certify carbon neutrality, or grant a reuse license.")

if __name__ == "__main__":
    main()