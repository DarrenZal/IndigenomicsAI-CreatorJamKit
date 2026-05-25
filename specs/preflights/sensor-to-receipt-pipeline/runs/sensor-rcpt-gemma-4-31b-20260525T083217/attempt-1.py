import json
import sys
import re

def validate_date(date_str):
    if not isinstance(date_str, str):
        return False
    # Simple YYYY-MM-DD regex check
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str))

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except Exception:
        print("error: invalid input")
        sys.exit(0)

    if not isinstance(data, dict) or "observations" not in data:
        print("error: invalid input")
        sys.exit(0)

    observations = data["observations"]
    if not isinstance(observations, list):
        print("error: invalid input")
        sys.exit(0)

    total_count = len(observations)
    kept_list = []
    rejected_count = 0
    redacted_count = 0

    calibration_map = {
        "calibrated": "high",
        "uncalibrated": "low",
        "unknown": "unknown"
    }

    for obs in observations:
        if not isinstance(obs, dict):
            rejected_count += 1
            continue

        # Rejection rules
        obs_id = obs.get("observation_id")
        obs_type = obs.get("observation_type")
        time_val = obs.get("time")

        if not obs_id or not obs_type or not validate_date(time_val):
            rejected_count += 1
            continue

        # Transformation: Sensitive location redaction
        location = obs.get("location", "")
        precision = obs.get("location_precision", "")
        sensitive_flag = obs.get("sensitive_location_flag", False)
        
        is_redacted = False
        if sensitive_flag is True or (precision == "exact" and sensitive_flag is True):
            location = "region-level only"
            is_redacted = True
        
        # Transformation: Calibration confidence
        cal_state = obs.get("calibration_state", "unknown")
        confidence = calibration_map.get(cal_state, "unknown")

        # Transformation: Qualitative observation
        measurement = obs.get("measurement")
        unit = obs.get("unit")
        if measurement is None:
            data_field = "qualitative observation"
        else:
            data_field = f"{measurement} {unit if unit else ''}".strip()

        kept_list.append({
            "id": obs_id,
            "type": obs_type,
            "source": obs.get("source", ""),
            "location": location,
            "time": time_val,
            "data": data_field,
            "confidence": confidence,
            "review": obs.get("review_state", "")
        })
        
        if is_redacted:
            redacted_count += 1

    kept_count = len(kept_list)
    
    # Output
    print(f"SENSOR-TO-RECEIPT EVIDENCE PACKETS ({kept_count} kept / {total_count} total)")
    print()

    for i, item in enumerate(kept_list):
        print(f"- id: {item['id']}")
        print(f"  type: {item['type']}")
        print(f"  source: {item['source']}")
        print(f"  location: {item['location']}")
        print(f"  time: {item['time']}")
        print(f"  data: {item['data']}")
        print(f"  calibration_confidence: {item['confidence']}")
        print(f"  review_state: {item['review']}")
        print()

    print(f"SUMMARY: {kept_count} kept, {rejected_count} rejected, {redacted_count} sensitive-location-redacted of {total_count} total")

if __name__ == "__main__":
    main()