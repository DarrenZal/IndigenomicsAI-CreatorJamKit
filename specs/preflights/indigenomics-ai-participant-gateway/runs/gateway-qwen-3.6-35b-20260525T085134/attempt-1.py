import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: no input file specified")
        sys.exit(0)
    
    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, IOError):
        print("error: invalid JSON or file not found")
        sys.exit(0)
    
    # Extract fields with defaults
    name = data.get("name", "")
    email = data.get("email", "")
    requested_spec = data.get("requested_spec", "")
    consent_team_visibility = data.get("consent_team_visibility", False)
    consent_ai_use = data.get("consent_ai_use", "none")
    consent_display_tuesday = data.get("consent_display_tuesday", False)
    flag_protected = data.get("flag_protected", False)
    
    # Decision logic
    decision = None
    reason = ""
    next_action = ""
    
    # REFUSE if name is empty OR email is empty
    if not name or not email:
        decision = "REFUSE"
        reason = "no name or no email"
        next_action = "ask for completed contact info"
    # ROUTE if consent_team_visibility==true AND email AND name AND consent_ai_use in {public,all}
    elif consent_team_visibility and email and name and consent_ai_use in {"public", "all"}:
        decision = "ROUTE"
        reason = "all required consents present"
        next_action = "forward submission to selected spec"
    # HOLD if flag_protected==true
    elif flag_protected:
        decision = "HOLD"
        reason = "protected flag — needs steward review"
        next_action = "hold for steward review and follow-up"
    # HOLD if consent_ai_use=='none' AND requested_spec is given
    elif consent_ai_use == "none" and requested_spec:
        decision = "HOLD"
        reason = "AI use refused but spec requested — clarify"
        next_action = "hold for steward review and follow-up"
    # Otherwise HOLD
    else:
        decision = "HOLD"
        reason = "missing required field"
        next_action = "hold for steward review and follow-up"
    
    print(f"DECISION: {decision}")
    print()
    print(f"reason: {reason}")
    print()
    print(f"next_action: {next_action}")

if __name__ == "__main__":
    main()