#!/usr/bin/env python3
import sys
import json
import re

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"error: {e}")
        sys.exit(0)

def is_valid_date(date_str):
    return bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', date_str))

def main():
    if len(sys.argv) < 2:
        print("error: missing input file path")
        sys.exit(0)

    data = load_json(sys.argv[1])

    if not isinstance(data, dict) or 'observations' not in data:
        print("error: invalid input structure")
        sys.exit(0)

    observations = data['observations']
    if not isinstance(observations, list):
        print("error: observations should be a list")
        sys.exit(0)

    total = len(observations)
    kept = []
    rejected = 0
    redacted_count = 0

    for obs in observations:
        # Basic validation for required fields
        obs_id = obs.get('observation_id', '')
        obs_type = obs.get('observation_type')
        time_str = obs.get('time', '')

        if not obs_id or obs_type is None or not isinstance(obs_type, str):
            rejected += 1
            continue
        if not isinstance(time_str, str) or not is_valid_date(time_str):
            rejected += 1
            continue

        # Passed filters, now transform
        transformed = {}

        transformed['observation_id'] = obs_id
        transformed['observation_type'] = obs_type
        transformed['source'] = obs.get('source', '')
        location = obs.get('location', '')
        location_precision = obs.get('location_precision', '')
        sensitive_flag = obs.get('sensitive_location_flag', False)

        # Sensitive location redaction
        if sensitive_flag is True:
            location = "region-level only"
            redacted_count += 1
        transformed['location'] = location

        transformed['time'] = time_str

        measurement = obs.get('measurement')
        unit = obs.get('unit')
        if measurement is None:
            transformed['data'] = "qualitative observation"
        else:
            if unit is None:
                transformed['data'] = f"{measurement}"
            else:
                transformed['data'] = f"{measurement} {unit}"

        cal_state = obs.get('calibration_state', 'unknown')
        cal_map = {
            'calibrated': 'high',
            'uncalibrated': 'low',
            'unknown': 'unknown'
        }
        transformed['calibration_confidence'] = cal_map.get(cal_state, 'unknown')
        transformed['review_state'] = obs.get('review_state', '')

        kept.append(transformed)

    kept_count = len(kept)

    # Output
    out_lines = []
    out_lines.append(f"SENSOR-TO-RECEIPT EVIDENCE PACKETS ({kept_count} kept / {total} total)")
    out_lines.append("")  # blank line

    for obs in kept:
        out_lines.append(f"- id: {obs['observation_id']}")
        out_lines.append(f"  type: {obs['observation_type']}")
        out_lines.append(f"  source: {obs['source']}")
        out_lines.append(f"  location: {obs['location']}")
        out_lines.append(f"  time: {obs['time']}")
        out_lines.append(f"  data: {obs['data']}")
        out_lines.append(f"  calibration_confidence: {obs['calibration_confidence']}")
        out_lines.append(f"  review_state: {obs['review_state']}")
        out_lines.append("")  # blank line after each block

    out_lines.append(f"SUMMARY: {kept_count} kept, {rejected} rejected, {redacted_count} sensitive-location-redacted of {total} total")

    sys.stdout.write("\n".join(out_lines))

if __name__ == "__main__":
    main()