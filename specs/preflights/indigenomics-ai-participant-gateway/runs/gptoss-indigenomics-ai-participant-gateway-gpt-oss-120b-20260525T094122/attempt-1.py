#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error: missing input path")
        return

    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print("error: invalid JSON")
        return

    # Extract fields with sensible defaults
    name = data.get('name', '')
    email = data.get('email', '')
    requested_spec = data.get('requested_spec', '')
    consent_team_visibility = data.get('consent_team_visibility', False)
    consent_ai_use = data.get('consent_ai_use', '')
    flag_protected = data.get('flag_protected', False)

    # Decision logic
    if not name or not email:
        decision = 'REFUSE'
        reason = 'no name or no email'
    elif flag_protected:
        decision = 'HOLD'
        reason = 'protected flag — needs steward review'
    elif consent_ai_use == 'none' and requested_spec:
        decision = 'HOLD'
        reason = 'AI use refused but spec requested — clarify'
    elif consent_team_visibility and consent_ai_use in ('public', 'all'):
        decision = 'ROUTE'
        reason = 'all required consents present'
    else:
        decision = 'HOLD'
        reason = 'missing required field'

    next_action_map = {
        'ROUTE': 'forward submission to selected spec',
        'HOLD': 'hold for steward review and follow-up',
        'REFUSE': 'ask for completed contact info'
    }
    next_action = next_action_map[decision]

    # Output
    print(f'DECISION: {decision}')
    print()
    print(f'reason: {reason}')
    print()
    print(f'next_action: {next_action}')

if __name__ == '__main__':
    main()