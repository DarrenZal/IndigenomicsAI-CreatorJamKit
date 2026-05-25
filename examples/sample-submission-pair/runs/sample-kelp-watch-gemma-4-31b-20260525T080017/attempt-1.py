import sys
import json
import re

def normalize(text):
    if not isinstance(text, str):
        return ""
    # Strip whitespace from both ends
    text = text.strip()
    # Collapse internal runs of whitespace to a single space
    text = re.sub(r'\s+', ' ', text)
    # Lowercase
    return text.lower()

def is_valid_date(date_str):
    if not isinstance(date_str, str):
        return False
    # Simple YYYY-MM-DD check: 4 digits, dash, 2 digits, dash, 2 digits
    if len(date_str) != 10:
        return False
    if date_str[4] != '-' or date_str[7] != '-':
        return False
    parts = date_str.split('-')
    if len(parts) != 3:
        return False
    for p in parts:
        if not p.isdigit():
            return False
    return True

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error: could not read or parse JSON file")
        sys.exit(0)

    if not isinstance(data, dict) or "observations" not in data:
        # Technically valid JSON but not the expected shape
        # The spec says "If the input cannot be read, or is not valid JSON"
        # We treat missing 'observations' key as a failure to read the expected data
        print("error: invalid input format")
        sys.exit(0)

    observations = data["observations"]
    if not isinstance(observations, list):
        print("error: observations must be a list")
        sys.exit(0)

    kept = []
    valid_dates = []

    for obs in observations:
        if not isinstance(obs, dict):
            continue
        
        # Drop rule: value must be a JSON number
        val = obs.get("value")
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        
        # Normalization and Drop rules for site and indicator
        site_raw = obs.get("site")
        indicator_raw = obs.get("indicator")
        
        site_norm = normalize(site_raw)
        indicator_norm = normalize(indicator_raw)
        
        if site_norm == "" or indicator_norm == "":
            continue
        
        # Keep the observation
        kept.append({
            "site": site_norm,
            "indicator": indicator_norm,
            "value": float(val)
        })
        
        # Date handling for summary
        date_val = obs.get("date")
        if is_valid_date(date_val):
            valid_dates.append(date_val)

    n_kept = len(kept)
    sites_set = sorted(list(set(o["site"] for o in kept)))
    s_count = len(sites_set)

    # 1. Header
    print(f"KELP BED WATCH ({n_kept} observations across {s_count} sites)")

    if n_kept > 0:
        # 2. Site blocks
        for site in sites_set:
            print(f"== {site} ==")
            
            # Group by indicator for this site
            site_obs = [o for o in kept if o["site"] == site]
            indicators_at_site = sorted(list(set(o["indicator"] for o in site_obs)))
            
            for ind in indicators_at_site:
                vals = [o["value"] for o in site_obs if o["indicator"] == ind]
                mean_val = sum(vals) / len(vals)
                print(f"{ind}: mean {mean_val:.2f}, n={len(vals)}")
            
            # 3. Blank line after each site block
            print()

    # 4. Summary line
    date_range = "no dates"
    if valid_dates:
        date_range = f"{min(valid_dates)} .. {max(valid_dates)}"
    
    print(f"SUMMARY: {n_kept} observations, {s_count} sites, {date_range}")

if __name__ == "__main__":
    main()