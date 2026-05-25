#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        return
    path = sys.argv[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        print('error:')
        return

    contributions = data.get('contributions', [])
    total = len(contributions)
    clean_cnt = 0
    flagged_cnt = 0
    results = []

    valid_consents = {'public', 'steward-review', 'private'}

    for contrib in contributions:
        cid = contrib.get('id', '')
        layer = contrib.get('layer', '')
        consent = contrib.get('consent')
        findings = []

        if consent not in valid_consents:
            findings.append('missing_consent')
        else:
            if consent == 'steward-review':
                findings.append('needs_steward_review')
            elif consent == 'public':
                cited = contrib.get('cited_sources', [])
                if not cited:
                    findings.append('uncited_public')

        if findings:
            flagged_cnt += 1
            findings_str = ','.join(sorted(findings))
        else:
            clean_cnt += 1
            findings_str = 'clean'

        results.append(f"{cid} [{layer}]: {findings_str}")

    # Header
    print(f"ATLAS COHERENCE PACKET ({clean_cnt} clean / {flagged_cnt} flagged of {total} contributions)")
    print()

    # Contributions
    for line in results:
        print(line)
        print()

    # Boundary line
    print("BOUNDARY: this packet flags coherence; it does not force fit, replace steward review, or grant any visibility upgrade.")

if __name__ == "__main__":
    main()