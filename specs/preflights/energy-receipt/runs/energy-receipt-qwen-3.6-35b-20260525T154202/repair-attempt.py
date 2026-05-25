import sys
import json

def main():
    # Read input from command line argument
    if len(sys.argv) < 2:
        print("error: no input file specified")
        return
    
    input_path = sys.argv[1]
    
    # Try to read and parse the JSON file
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, IOError, json.JSONDecodeError):
        print("error: invalid JSON or unreadable file")
        return
    
    # Extract team and events
    team = data.get("team", "Unknown Team")
    events = data.get("events", [])
    
    # Validate and filter events
    kept_events = []
    rejected_count = 0
    
    for event in events:
        # Check required fields
        event_id = event.get("event_id")
        intention = event.get("intention")
        model = event.get("model")
        
        # Check for empty strings
        if not event_id or not intention or not model:
            rejected_count += 1
            continue
        
        # Check numeric fields
        try:
            input_tokens = event["input_tokens"]
            output_tokens = event["output_tokens"]
            duration_seconds = event["duration_seconds"]
            estimated_kwh = event["estimated_kwh"]
            
            # Verify they are numbers
            if not isinstance(input_tokens, (int, float)):
                rejected_count += 1
                continue
            if not isinstance(output_tokens, (int, float)):
                rejected_count += 1
                continue
            if not isinstance(duration_seconds, (int, float)):
                rejected_count += 1
                continue
            if not isinstance(estimated_kwh, (int, float)):
                rejected_count += 1
                continue
                
            # Check for negative estimated_kwh
            if estimated_kwh < 0:
                rejected_count += 1
                continue
                
        except (KeyError, TypeError):
            rejected_count += 1
            continue
        
        # Event is valid, add to kept events
        kept_events.append(event)
    
    # Calculate totals
    total_events = len(events)
    kept_count = len(kept_events)
    
    sum_kwh = sum(e["estimated_kwh"] for e in kept_events)
    sum_input = sum(e["input_tokens"] for e in kept_events)
    sum_output = sum(e["output_tokens"] for e in kept_events)
    
    # Get distinct models from kept events
    models = sorted(set(e["model"] for e in kept_events))
    models_str = ", ".join(models) if models else "none"
    
    # Build output
    output_lines = []
    
    # Header
    output_lines.append(f"ENERGY RECEIPT — {team}")
    output_lines.append("")
    
    # Event blocks
    for i, event in enumerate(kept_events):
        output_lines.append(f"- event_id: {event['event_id']}")
        output_lines.append(f"  intention: {event['intention']}")
        output_lines.append(f"  model: {event['model']}")
        output_lines.append(f"  kWh: {event['estimated_kwh']}")
        output_lines.append(f"  tokens: {event['input_tokens']} in / {event['output_tokens']} out")
        output_lines.append(f"  duration_s: {event['duration_seconds']}")
        output_lines.append(f"  outcome: {event['outcome_summary']}")
        
        # Add blank line between event blocks
        if i < len(kept_events) - 1:
            output_lines.append("")
    
    # Blank line before TOTALS if there were kept events
    if kept_events:
        output_lines.append("")
    
    # TOTALS section
    output_lines.append("TOTALS")
    output_lines.append(f"  events: {kept_count} kept, {rejected_count} rejected of {total_events} total")
    output_lines.append(f"  kWh: {sum_kwh:.4f}")
    output_lines.append(f"  tokens: {sum_input} in / {sum_output} out")
    output_lines.append(f"  models: {models_str}")
    
    # Blank line before REFLECTION
    output_lines.append("")
    
    # REFLECTION section
    output_lines.append("REFLECTION")
    output_lines.append("  Did the work justify its footprint?")
    output_lines.append("  What would you do differently?")
    output_lines.append("  What reciprocity is owed?")
    
    # Blank line before BOUNDARY
    output_lines.append("")
    
    # BOUNDARY section - must be a single line
    output_lines.append("BOUNDARY: This is a receipt of what was computed. It does not offset, certify carbon neutrality, or grant a reuse license.")
    
    # Print output
    print("\n".join(output_lines))

if __name__ == "__main__":
    main()