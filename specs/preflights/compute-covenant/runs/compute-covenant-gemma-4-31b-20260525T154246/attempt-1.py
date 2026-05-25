import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error:")
        sys.exit(0)

    jam = data.get("jam", "")
    date = data.get("date", "")
    site = data.get("site", "")
    teams_raw = data.get("teams", [])

    kept_teams = []
    rejected_count = 0
    total_count = len(teams_raw)

    for t in teams_raw:
        # Validation
        team_name = t.get("team")
        disclosure = t.get("disclosure")
        
        # Check basic presence and types
        try:
            kwh = t.get("total_kwh")
            in_tok = t.get("input_tokens")
            out_tok = t.get("output_tokens")
            
            # Must be numeric and non-negative
            if not (isinstance(kwh, (int, float)) and kwh >= 0):
                raise ValueError()
            if not (isinstance(in_tok, int) and in_tok >= 0):
                raise ValueError()
            if not (isinstance(out_tok, int) and out_tok >= 0):
                raise ValueError()
            
            if not team_name or disclosure not in ("public", "withheld"):
                raise ValueError()
                
            kept_teams.append(t)
        except (ValueError, TypeError):
            rejected_count += 1

    # Aggregates
    k_total = len(kept_teams)
    k_public = len([t for t in kept_teams if t.get("disclosure") == "public"])
    k_withheld = len([t for t in kept_teams if t.get("disclosure") == "withheld"])
    
    sum_kwh = sum(t.get("total_kwh", 0.0) for t in kept_teams)
    sum_input = sum(t.get("input_tokens", 0) for t in kept_teams)
    sum_output = sum(t.get("output_tokens", 0) for t in kept_teams)
    
    all_models = set()
    for t in kept_teams:
        models = t.get("models", [])
        if isinstance(models, list):
            all_models.update(models)
    
    sorted_models = sorted(list(all_models))
    models_str = ", ".join(sorted_models) if sorted_models else "none"

    # Output
    print(f"COMPUTE COVENANT — {jam} ({date})")
    print(f"site: {site}")
    print()
    print("ECOSYSTEM ENERGY")
    print(f"  teams: {k_total} kept ({k_public} public, {k_withheld} withheld), {rejected_count} rejected of {total_count} total")
    print(f"  jam_kwh: {sum_kwh:.4f}")
    print(f"  tokens: {sum_input} in / {sum_output} out")
    print(f"  models: {models_str}")
    print()
    print("PER-TEAM CONTRIBUTIONS")
    print()
    
    public_teams = [t for t in kept_teams if t.get("disclosure") == "public"]
    if not public_teams:
        print("  (no public-disclosure teams)")
    else:
        for t in public_teams:
            t_name = t.get("team")
            t_kwh = t.get("total_kwh")
            t_kept = t.get("kept_events", 0)
            t_rej = t.get("rejected_events", 0)
            t_in = t.get("input_tokens")
            t_out = t.get("output_tokens")
            
            themes = t.get("intention_themes", [])
            themes_str = ", ".join(themes) if themes else "none"
            
            t_models = t.get("models", [])
            t_models_str = ", ".join(sorted(t_models)) if t_models else "none"
            
            print(f"- team: {t_name}")
            print(f"  kWh: {t_kwh}")
            print(f"  events: {t_kept} kept, {t_rej} rejected")
            print(f"  tokens: {t_in} in / {t_out} out")
            print(f"  intention themes: {themes_str}")
            print(f"  models: {t_models_str}")
            print()

    withheld_line = f"WITHHELD: {k_withheld} team(s) opted out of public energy disclosure."
    if k_withheld > 0:
        withheld_line += " Their compute is\nincluded in ECOSYSTEM ENERGY; their names and per-team numbers are not."
    
    print(withheld_line)
    print()
    print("COVENANT")
    print(f"This jam consumed {sum_kwh:.4f} kWh on {site}. Equivalent to roughly")
    print(f"{sum_kwh / 0.4:.2f} Vancouver homes for an hour (0.4 kWh/home/hour reference).")
    print("Witnessed.")
    print()
    print("BOUNDARY: This is a record of compute that happened, on a grid that ran on")
    print("~99% renewable hydro on the day named. It does not offset, certify carbon")
    print("neutrality, claim ecological repair, or grant a reuse license.")

if __name__ == "__main__":
    main()