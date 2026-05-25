import sys
import json
import re

def main():
    # Read input file
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (IOError, OSError):
        print("error: cannot read input file")
        sys.exit(0)
    except json.JSONDecodeError:
        print("error: invalid JSON")
        sys.exit(0)
    
    # Validate structure
    if not isinstance(data, dict) or 'observations' not in data:
        print("error: invalid JSON structure")
        sys.exit(0)
    
    observations = data.get('observations', [])
    if not isinstance(observations, list):
        print("error: observations must be a list")
        sys.exit(0)
    
    # Date pattern
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    
    # Normalize function
    def normalize(s):
        if not isinstance(s, str):
            return ""
        s = s.strip()
        s = re.sub(r'\s+', ' ', s)
        s = s.lower()
        return s
    
    # Process observations
    kept = []
    for obs in observations:
        if not isinstance(obs, dict):
            continue
        
        # Check value is a JSON number (not string, null, boolean)
        value = obs.get('value')
        if value is None or isinstance(value, bool) or isinstance(value, str):
            continue
        if not isinstance(value, (int, float)):
            continue
        
        # Normalize site and indicator
        site = normalize(obs.get('site', ''))
        indicator = normalize(obs.get('indicator', ''))
        
        # Drop if empty site or indicator
        if not site or not indicator:
            continue
        
        # Get date
        date = obs.get('date', '')
        valid_date = None
        if isinstance(date, str) and date_pattern.match(date):
            valid_date = date
        
        kept.append({
            'site': site,
            'indicator': indicator,
            'value': value,
            'date': valid_date
        })
    
    # Count kept observations and distinct sites
    N = len(kept)
    sites = set(obs['site'] for obs in kept)
    S = len(sites)
    
    # Print header
    print(f"KELP BED WATCH ({N} observations across {S} sites)")
    
    if N == 0:
        # Empty case: skip site blocks and blank lines
        print("SUMMARY: 0 observations, 0 sites, no dates")
        sys.exit(0)
    
    # Group by site and indicator
    site_data = {}
    for obs in kept:
        site = obs['site']
        indicator = obs['indicator']
        if site not in site_data:
            site_data[site] = {}
        if indicator not in site_data[site]:
            site_data[site][indicator] = []
        site_data[site][indicator].append(obs['value'])
    
    # Collect all valid dates
    all_dates = [obs['date'] for obs in kept if obs['date'] is not None]
    
    # Print site blocks
    for site in sorted(site_data.keys()):
        print(f"== {site} =="
              )
        indicators = sorted(site_data[site].keys())
        for indicator in indicators:
            values = site_data[site][indicator]
            mean = sum(values) / len(values)
            mean_rounded = round(mean, 2)
            # Format mean to 2 decimal places
            mean_str = f"{mean_rounded:.2f}"
            print(f"{indicator}: mean {mean_str}, n={len(values)}")
        print()  # Blank line after each site block
    
    # Print summary
    if all_dates:
        from_date = min(all_dates)
        to_date = max(all_dates)
        print(f"SUMMARY: {N} observations, {S} sites, {from_date} .. {to_date}")
    else:
        print(f"SUMMARY: {N} observations, {S} sites, no dates")

if __name__ == '__main__':
    main()