import sys
import json
import math

def main():
    if len(sys.argv) < 3:
        print("error: missing arguments")
        sys.exit(0)

    obs_path = sys.argv[1]
    actions_path = sys.argv[2]

    # Read and parse observations
    try:
        with open(obs_path, 'r') as f:
            obs_data = json.load(f)
    except (IOError, json.JSONDecodeError):
        print("error: invalid JSON in observations")
        sys.exit(0)

    # Read and parse actions
    try:
        with open(actions_path, 'r') as f:
            act_data = json.load(f)
    except (IOError, json.JSONDecodeError):
        print("error: invalid JSON in actions")
        sys.exit(0)

    # Validate and filter observations
    valid_obs = []
    if "observations" in obs_data and isinstance(obs_data["observations"], list):
        for obs in obs_data["observations"]:
            if not isinstance(obs, dict):
                continue
            if "canopy_percent" not in obs or "site" not in obs or "bioregion" not in obs:
                continue
            cp = obs["canopy_percent"]
            if not isinstance(cp, (int, float)):
                continue
            if cp < 0 or cp > 100:
                continue
            valid_obs.append(obs)

    # Validate and filter actions
    valid_action_types = {"work-party", "beach-cleanup", "eelgrass-survey", "kelp-count", "planting"}
    valid_actions = []
    if "actions" in act_data and isinstance(act_data["actions"], list):
        for act in act_data["actions"]:
            if not isinstance(act, dict):
                continue
            if "action_type" not in act or "bioregion" not in obs:
                continue
            if act["action_type"] not in valid_action_types:
                continue
            valid_actions.append(act)

    # Collect all bioregions
    bioregions = set()
    for obs in valid_obs:
        bioregions.add(obs["bioregion"])
    for act in valid_actions:
        bioregions.add(act["bioregion"])

    sorted_bioregions = sorted(bioregions)

    # Process kelp data per bioregion
    # Structure: bioregion -> site -> list of canopy_percent
    kelp_data = {}
    for br in sorted_bioregions:
        kelp_data[br] = {}
        for obs in valid_obs:
            if obs["bioregion"] == br:
                site = obs["site"]
                if site not in kelp_data[br]:
                    kelp_data[br][site] = []
                kelp_data[br][site].append(obs["canopy_percent"])

    # Process actions per bioregion
    # Structure: bioregion -> action_type -> count
    action_data = {}
    for br in sorted_bioregions:
        action_data[br] = {}
        for act in valid_actions:
            if act["bioregion"] == br:
                at = act["action_type"]
                if at not in action_data[br]:
                    action_data[br][at] = 0
                action_data[br][at] += 1

    # Helper to round half away from zero
    def round_half_away(x):
        if x >= 0:
            return int(math.floor(x + 0.5))
        else:
            return int(math.ceil(x - 0.5))

    # Build output
    output_lines = []

    # Header
    output_lines.append(f"KELP-BED STEWARDSHIP REPORT ({len(sorted_bioregions)} bioregions)")

    # Per bioregion sections
    for br in sorted_bioregions:
        output_lines.append(f"== {br} =="
        
        # KELP block
        output_lines.append("KELP:")
        sites = kelp_data[br]
        if not sites:
            output_lines.append("  none")
        else:
            # Sort sites alphabetically
            for site in sorted(sites.keys()):
                values = sites[site]
                mean = sum(values) / len(values)
                rounded_mean = round_half_away(mean)
                if mean >= 60:
                    condition = "healthy"
                elif mean >= 30:
                    condition = "declining"
                else:
                    condition = "stressed"
                output_lines.append(f"  {site}: {condition} (mean canopy {rounded_mean}%)")
        
        # ACTIONS block
        output_lines.append("ACTIONS:")
        actions = action_data[br]
        if not actions:
            output_lines.append("  none")
        else:
            # Sort by count descending, then action_type alphabetically ascending
            sorted_actions = sorted(actions.items(), key=lambda x: (-x[1], x[0]))
            for at, count in sorted_actions:
                output_lines.append(f"  {at}: {count}")
        
        output_lines.append("")  # Blank line after each bioregion section (except last, handled below)

    # Remove the trailing blank line added after the last bioregion
    if output_lines and output_lines[-1] == "":
        output_lines.pop()

    # Summary line
    total_healthy = 0
    total_declining = 0
    total_stressed = 0
    for br in sorted_bioregions:
        for site, values in kelp_data[br].items():
            mean = sum(values) / len(values)
            if mean >= 60:
                total_healthy += 1
            elif mean >= 30:
                total_declining += 1
            else:
                total_stressed += 1
    
    total_actions = len(valid_actions)
    
    output_lines.append(f"SUMMARY: {total_healthy} healthy / {total_declining} declining / {total_stressed} stressed sites, {total_actions} stewardship actions")

    # Print all output
    for line in output_lines:
        print(line)

if __name__ == "__main__":
    main()