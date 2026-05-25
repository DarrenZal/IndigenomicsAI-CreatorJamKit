import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        print("error: invalid JSON")
        sys.exit(0)

    # Extract fields with defaults to avoid KeyErrors
    name = data.get("name", "")
    email = data.get("email", "")
    requested_spec = data.get("requested_spec", "")
    consent_team_visibility = data.get("consent_team_visibility", False)
    consent_ai_use = data.get("consent_ai_use", "")
    flag_protected = data.get("flag_protected", False)

    # Decision Logic
    # 1. REFUSE if name is empty OR email is empty
    if not name or not email:
        decision = "REFUSE"
        reason = "no name or no email"
        next_action = "ask for completed contact info"
    
    # 2. HOLD if flag_protected==true OR (consent_ai_use=='none' AND requested_spec is given)
    elif flag_protected is True:
        decision = "HOLD"
        reason = "protected flag — needs steward review"
        next_action = "hold for steward review and follow-up"
    elif consent_ai_use == 'none' and requested_spec:
        decision = "HOLD"
        reason = "AI use refused but spec requested — clarify"
        next_action = "hold for steward review and follow-up"
    
    # 3. ROUTE if consent_team_visibility==true AND email AND name AND consent_ai_use in {public,all}
    elif (consent_team_visibility is True and 
          email and 
          name and 
          consent_ai_use in {"public", "all"}):
        decision = "ROUTE"
        reason = "all required consents present"
        next_action = "forward submission to selected spec"
    
    # 4. Otherwise HOLD
    else:
        decision = "HOLD"
        reason = "missing required field"
        next_action = "hold for steward review and follow-up"

    # Output format
    print(f"DECISION: {decision}")
    print("")
    print(f"reason: {reason}")
    print("")
    print(f"next_action: {next_action}")

if __name__ == "__main__":
    main()