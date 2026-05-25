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
    
    if not isinstance(data, dict) or "contributions" not in data:
        print("error: invalid JSON structure")
        sys.exit(0)
    
    contributions = data["contributions"]
    if not isinstance(contributions, list):
        print("error: contributions must be a list")
        sys.exit(0)
    
    valid_consent_values = {"public", "steward-review", "private"}
    n = len(contributions)
    flagged_count = 0
    findings_list = []
    
    for contrib in contributions:
        if not isinstance(contrib, dict):
            continue
        
        contrib_id = contrib.get("id", "unknown")
        layer = contrib.get("layer", "unknown")
        consent = contrib.get("consent", "")
        cited_sources = contrib.get("cited_sources", [])
        
        findings = []
        
        # Check 1: missing_consent
        if consent not in valid_consent_values:
            findings.append("missing_consent")
        
        # Check 2: needs_steward_review
        if consent == "steward-review":
            findings.append("needs_steward_review")
        
        # Check 3: uncited_public
        if consent == "public" and (not cited_sources or not isinstance(cited_sources, list) or len(cited_sources) == 0):
            findings.append("uncited_public")
        
        # Sort findings alphabetically
        findings.sort()
        
        if findings:
            flagged_count += 1
            findings_str = ", ".join(findings)
        else:
            findings_str = "clean"
        
        findings_list.append((contrib_id, layer, findings_str))
    
    # Determine header counts
    clean_count = n - flagged_count
    flagged_count_actual = flagged_count
    
    # Print header
    print(f"ATLAS COHERENCE PACKET ({clean_count} clean / {flagged_count_actual} flagged of {n} contributions)")
    print()
    
    # Print each contribution
    for contrib_id, layer, findings_str in findings_list:
        print(f"{contrib_id} [{layer}]: {findings_str}")
        print()
    
    # Print boundary statement
    print("BOUNDARY: this packet flags coherence; it does not force fit, replace steward review, or grant any visibility upgrade.")

if __name__ == "__main__":
    main()