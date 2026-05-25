import sys
import json

def main():
    # Read input from command line argument
    if len(sys.argv) < 2:
        print("error: no input file specified")
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError, OSError):
        print("error: invalid JSON or unreadable file")
        return

    # Extract top-level fields
    jam = data.get("jam", "")
    date = data.get("date", "")
    site = data.get("site", "")
    teams = data.get("teams", [])

    # Process teams
    kept_teams = []
    rejected_count = 0
    total_teams = len(teams)

    for team_data in teams:
        team_name = team_data.get("team", "")
        disclosure = team_data.get("disclosure", "")
        
        # Check for empty team name
        if not team_name:
            rejected_count += 1
            continue
        
        # Check disclosure validity
        if disclosure not in ("public", "withheld"):
            rejected_count += 1
            continue
        
        # Check numeric fields
        try:
            total_kwh = team_data["total_kwh"]
            input_tokens = team_data["input_tokens"]
            output_tokens = team_data["output_tokens"]
            
            # Check if they are numeric
            if not isinstance(total_kwh, (int, float)):
                rejected_count += 1
                continue
            if not isinstance(input_tokens, (int, float)):
                rejected_count += 1
                continue
            if not isinstance(output_tokens, (int, float)):
                rejected_count += 1
                continue
            
            # Check if they are non-negative
            if total_kwh < 0 or input_tokens < 0 or output_tokens < 0:
                rejected_count += 1
                continue
                
        except (KeyError, TypeError):
            rejected_count += 1
            continue
        
        # Team is kept
        kept_teams.append(team_data)

    # Calculate ecosystem energy totals
    total_kwh = sum(t["total_kwh"] for t in kept_teams)
    total_input_tokens = sum(t["input_tokens"] for t in kept_teams)
    total_output_tokens = sum(t["output_tokens"] for t in kept_teams)
    
    # Count public and withheld teams
    public_teams = [t for t in kept_teams if t.get("disclosure") == "public"]
    withheld_teams = [t for t in kept_teams if t.get("disclosure") == "withheld"]
    
    # Collect all models from kept teams
    all_models = set()
    for t in kept_teams:
        for model in t.get("models", []):
            all_models.add(model)
    
    # Format models list
    if all_models:
        models_str = ", ".join(sorted(all_models))
    else:
        models_str = "none"
    
    # Build output
    output_lines = []
    
    # Header
    output_lines.append(f"COMPUTE COVENANT — {jam} ({date})")
    output_lines.append(f"site: {site}")
    output_lines.append("")
    
    # Ecosystem Energy section
    output_lines.append("ECOSYSTEM ENERGY")
    output_lines.append(f"  teams: {len(kept_teams)} kept ({len(public_teams)} public, {len(withheld_teams)} withheld), {rejected_count} rejected of {total_teams} total")
    output_lines.append(f"  jam_kwh: {total_kwh:.4f}")
    output_lines.append(f"  tokens: {total_input_tokens} in / {total_output_tokens} out")
    output_lines.append(f"  models: {models_str}")
    output_lines.append("")
    
    # Per-Team Contributions section
    output_lines.append("PER-TEAM CONTRIBUTIONS")
    
    if public_teams:
        output_lines.append("")
        for team_data in public_teams:
            team_name = team_data["team"]
            total_kwh_team = team_data["total_kwh"]
            kept_events = team_data.get("kept_events", 0)
            rejected_events = team_data.get("rejected_events", 0)
            input_tokens_team = team_data["input_tokens"]
            output_tokens_team = team_data["output_tokens"]
            intention_themes = team_data.get("intention_themes", [])
            models = team_data.get("models", [])
            
            # Format intention themes
            if intention_themes:
                themes_str = ", ".join(intention_themes)
            else:
                themes_str = "none"
            
            # Format models
            if models:
                models_team_str = ", ".join(sorted(models))
            else:
                models_team_str = "none"
            
            output_lines.append(f"- team: {team_name}")
            output_lines.append(f"  kWh: {total_kwh_team}")
            output_lines.append(f"  events: {kept_events} kept, {rejected_events} rejected")
            output_lines.append(f"  tokens: {input_tokens_team} in / {output_tokens_team} out")
            output_lines.append(f"  intention themes: {themes_str}")
            output_lines.append(f"  models: {models_team_str}")
            output_lines.append("")
    else:
        output_lines.append("  (no public-disclosure teams)")
        output_lines.append("")
    
    # Withheld section
    output_lines.append(f"WITHHELD: {len(withheld_teams)} team(s) opted out of public energy disclosure.")
    if len(withheld_teams) > 0:
        output_lines.append("Their compute is included in ECOSYSTEM ENERGY; their names and per-team numbers are not.")
    output_lines.append("")
    
    # Covenant section
    vancouver_homes = total_kwh / 0.4
    output_lines.append("COVENANT")
    output_lines.append(f"This jam consumed {total_kwh:.4f} kWh on {site}. Equivalent to roughly {vancouver_homes:.2f} Vancouver homes for an hour (0.4 kWh/home/hour reference).")
    output_lines.append("Witnessed.")
    output_lines.append("")
    
    # Boundary section
    output_lines.append("BOUNDARY: This is a record of compute that happened, on a grid that ran on")
    output_lines.append("~99% renewable hydro on the day named. It does not offset, certify carbon")
    output_lines.append("neutrality, claim ecological repair, or grant a reuse license.")
    
    # Print output
    print("\n".join(output_lines))

if __name__ == "__main__":
    main()