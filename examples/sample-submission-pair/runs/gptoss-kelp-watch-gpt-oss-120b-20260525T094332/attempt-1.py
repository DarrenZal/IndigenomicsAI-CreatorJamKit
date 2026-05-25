#!/usr/bin/env python3
import sys
import json
import re
from datetime import date

def normalize(text):
    if not isinstance(text, str):
        return ''
    # Strip ends, collapse internal whitespace, lowercase
    return ' '.join(text.strip().split()).lower()

def parse_date(datestr):
    if not isinstance(datestr, str):
        return None
    # Simple regex check for YYYY-MM-DD
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', datestr):
        return None
    try:
        return date.fromisoformat(datestr)
    except ValueError:
        return None

def main():
    if len(sys.argv) < 2:
        print("error: missing input path")
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"error: {e}")
        return

    if not isinstance(data, dict) or 'observations' not in data:
        print("error: invalid JSON structure")
        return

    observations = data['observations']
    if not isinstance(observations, list):
        print("error: observations is not a list")
        return

    total_obs = 0
    site_set = set()
    site_indicator_stats = {}  # site -> indicator -> [sum, count]
    date_list = []

    for obs in observations:
        # Extract fields
        site_raw = obs.get('site')
        indicator_raw = obs.get('indicator')
        value = obs.get('value')
        date_raw = obs.get('date')

        # Drop rules
        if not isinstance(value, (int, float)):
            continue

        site_norm = normalize(site_raw)
        indicator_norm = normalize(indicator_raw)

        if site_norm == '' or indicator_norm == '':
            continue

        # Keep observation
        total_obs += 1
        site_set.add(site_norm)

        if site_norm not in site_indicator_stats:
            site_indicator_stats[site_norm] = {}
        if indicator_norm not in site_indicator_stats[site_norm]:
            site_indicator_stats[site_norm][indicator_norm] = [0.0, 0]

        stats = site_indicator_stats[site_norm][indicator_norm]
        stats[0] += float(value)
        stats[1] += 1

        # Date handling
        d = parse_date(date_raw)
        if d is not None:
            date_list.append(d)

    site_count = len(site_set)

    # Header
    print(f"KELP BED WATCH ({total_obs} observations across {site_count} sites)")

    if total_obs > 0:
        # Site blocks
        for site in sorted(site_indicator_stats.keys()):
            print(f"== {site} ==")
            indicators = site_indicator_stats[site]
            for indicator in sorted(indicators.keys()):
                sum_val, cnt = indicators[indicator]
                mean_val = sum_val / cnt if cnt else 0.0
                print(f"{indicator}: mean {mean_val:.2f}, n={cnt}")
            print()  # blank line after each site block

        # Summary line
        if date_list:
            from_date = min(date_list).isoformat()
            to_date = max(date_list).isoformat()
            date_range = f"{from_date} .. {to_date}"
        else:
            date_range = "no dates"
        print(f"SUMMARY: {total_obs} observations, {site_count} sites, {date_range}")
    else:
        # No observations kept
        print("SUMMARY: 0 observations, 0 sites, no dates")

if __name__ == "__main__":
    main()