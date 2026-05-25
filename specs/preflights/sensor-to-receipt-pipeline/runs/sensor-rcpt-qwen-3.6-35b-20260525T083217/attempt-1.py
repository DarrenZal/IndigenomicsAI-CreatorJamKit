import sys
import json
import re

def main():
    if len(sys.argv) != 2:
        print("error: invalid input")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        print("error: invalid input")
        sys.exit(0)
    
    if not isinstance(data, dict) or 'observations' not in data:
        print("error: invalid input")
        sys.exit(0)
    
    observations = data['observations']
    if not isinstance(observations, list):
        print("error: invalid input")
        sys.exit(0)
    
    total = len(observations)
    kept = []
    rejected = 0
    sensitive_redacted_count = 0
    
    time_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    for obs in observations:
        if not isinstance(obs, dict):
            rejected += 1
            continue
        
        obs_id = obs.get('observation_id', None)
        obs_type = obs.get('observation_type', None)
        time_val = obs.get('time', None)
        
        # Reject if observation_id is empty
        if obs_id is None or obs_id == '':
            rejected += 1
            continue
        
        # Reject if observation_type is missing
        if obs_type is None:
            rejected += 1
            continue
        
        # Reject if time does not match YYYY-MM-DD
        if time_val is None or not isinstance(time_val, str) or not time_pattern.match(time_val):
            rejected += 1
            continue
        
        # Process kept observation
        location = obs.get('location', '')
        sensitive_flag = obs.get('sensitive_location_flag', False)
        location_precision = obs.get('location_precision', '')
        
        # Sensitive location redaction
        # if sensitive_location_flag == true OR (location_precision == "exact" AND sensitive_location_flag == true)
        # The second condition is redundant since it's a subset of the first.
        # So effectively: if sensitive_location_flag is true, redact.
        if sensitive_flag is True:
            location = "region-level only"
            sensitive_redacted_count += 1
        
        # Calibration confidence
        cal_state = obs.get('calibration_state', 'unknown')
        if cal_state == 'calibrated':
            confidence = 'high'
        elif cal_state == 'uncalibrated':
            confidence = 'low'
        else:
            confidence = 'unknown'
        
        # Qualitative observation
        measurement = obs.get('measurement', None)
        unit = obs.get('unit', None)
        
        if measurement is None:
            data_str = 'qualitative observation'
        else:
            # Format measurement and unit
            # If unit is None, just show measurement
            if unit is None:
                data_str = str(measurement)
            else:
                data_str = f"{measurement} {unit}"
        
        review_state = obs.get('review_state', 'not-applicable')
        source = obs.get('source', '')
        
        kept.append({
            'id': obs_id,
            'type': obs_type,
            'source': source,
            'location': location,
            'time': time_val,
            'data': data_str,
            'calibration_confidence': confidence,
            'review_state': review_state
        })
    
    kept_count = len(kept)
    rejected_count = rejected
    
    # Output
    print(f"SENSOR-TO-RECEIPT EVIDENCE PACKETS ({kept_count} kept / {total} total)")
    print()
    
    for i, obs in enumerate(kept):
        print(f"- id: {obs['id']}")
        print(f"  type: {obs['type']}")
        print(f"  source: {obs['source']}")
        print(f"  location: {obs['location']}")
        print(f"  time: {obs['time']}")
        print(f"  data: {obs['data']}")
        print(f"  calibration_confidence: {obs['calibration_confidence']}")
        print(f"  review_state: {obs['review_state']}")
        
        # Blank line between observation blocks (including after the last block, before SUMMARY)
        print()
    
    print(f"SUMMARY: {kept_count} kept, {rejected_count} rejected, {sensitive_redacted_count} sensitive-location-redacted of {total} total")

if __name__ == '__main__':
    main()