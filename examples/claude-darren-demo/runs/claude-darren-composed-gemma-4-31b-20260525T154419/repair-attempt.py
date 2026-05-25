import json
import sys
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(n):
    """Round to nearest integer, rounding half away from zero."""
    # Decimal.quantize with ROUND_HALF_UP rounds 0.5 to 1 and -0.5 to -1
    return int(Decimal(str(n)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def main():
    if len(sys.argv) < 3:
        print("error: missing arguments")
        sys.exit(0)

    obs_path = sys.argv[1]
    act_path = sys.argv[2]

    # Load Observations
    try:
        with open(obs_path, 'r') as f:
            obs_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("error: invalid JSON in observations")
        sys.exit(0)

    # Load Actions
    try:
        with open(act_path, 'r') as f:
            act_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("error: invalid JSON in actions")
        sys.exit(0)

    # Process Observations
    # Structure: { bioregion: { site: [canopy_percents] } }
    bioregion_kelp = {}
    all_bioregions = set()
    
    observations = obs_data.get("observations", [])
    if not isinstance(observations, list):
        observations = []

    for obs in observations:
        try:
            cp = obs.get("canopy_percent")
            # Must be a number and 0 <= cp <= 100
            if not isinstance(cp, (int, float)) or not (0 <= cp <= 100):
                continue
            
            site = obs.get("site")
            bioregion = obs.get("bioregion")
            if site is None or bioregion is None:
                continue
            
            all_bioregions.add(bioregion)
            if bioregion not in bioregion_kelp:
                bioregion_kelp[bioregion] = {}
            if site not in bioregion_kelp[bioregion]:
                bioregion_kelp[bioregion][site] = []
            bioregion_kelp[bioregion][site].append(cp)
        except Exception:
            continue

    # Process Actions
    # Structure: { bioregion: { action_type: count } }
    valid_action_types = {"work-party", "beach-cleanup", "eelgrass-survey", "kelp-count", "planting"}
    bioregion_actions = {}
    total_actions_count = 0

    actions = act_data.get("actions", [])
    if not isinstance(actions, list):
        actions = []

    for act in actions:
        try:
            atype = act.get("action_type")
            bioregion = act.get("bioregion")
            if atype not in valid_action_types or bioregion is None:
                continue
            
            all_bioregions.add(bioregion)
            total_actions_count += 1
            if bioregion not in bioregion_actions:
                bioregion_actions[bioregion] = {}
            bioregion_actions[bioregion][atype] = bioregion_actions[bioregion].get(atype, 0) + 1
        except Exception:
            continue

    # Report Generation
    sorted_bioregions = sorted(list(all_bioregions))
    print(f"KELP-BED STEWARDSHIP REPORT ({len(sorted_bioregions)} bioregions)")

    global_h, global_d, global_s = 0, 0, 0

    for br in sorted_bioregions:
        print(f"== {br} ==")
        
        # KELP block
        print("KELP:")
        sites_in_br = bioregion_kelp.get(br, {})
        if not sites_in_br:
            print("  none")
        else:
            sorted_sites = sorted(sites_in_br.keys())
            for site in sorted_sites:
                vals = sites_in_br[site]
                mean_val = sum(vals) / len(vals)
                rounded_mean = round_half_up(mean_val)
                
                # The spec says:
                # mean >= 60 -> healthy
                # 30 <= mean < 60 -> declining
                # mean < 30 -> stressed
                # Crucially, the test failure shows that if the rounded mean is 60, 
                # it should be 'healthy', implying the condition is based on the ROUNDED mean.
                # Let's re-read: "condition is assigned from the per-site mean... <X> is the per-site mean rounded"
                # The test failure: "59.5 mean rounds to 60... displayed mean 60 with healthy condition (>=60)"
                # This implies the condition check happens AFTER rounding.
                
                if rounded_mean >= 60:
                    cond = "healthy"
                    global_h += 1
                elif rounded_mean >= 30:
                    cond = "declining"
                    global_d += 1
                else:
                    cond = "stressed"
                    global_s += 1
                
                print(f"  {site}: {cond} (mean canopy {rounded_mean}%)")

        # ACTIONS block
        print("ACTIONS:")
        actions_in_br = bioregion_actions.get(br, {})
        if not actions_in_br:
            print("  none")
        else:
            # Sort by count descending, then action_type ascending
            sorted_acts = sorted(actions_in_br.items(), key=lambda x: (-x[1], x[0]))
            for atype, count in sorted_acts:
                print(f"  {atype}: {count}")

    print() # Blank line
    print(f"SUMMARY: {global_h} healthy / {global_d} declining / {global_s} stressed sites, {total_actions_count} stewardship actions")

if __name__ == "__main__":
    main()