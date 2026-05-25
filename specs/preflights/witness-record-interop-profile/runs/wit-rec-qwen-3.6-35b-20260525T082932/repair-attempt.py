import sys
import json
from datetime import datetime, timedelta

def main():
    # Parse arguments
    if len(sys.argv) < 2:
        print("error: missing input file path")
        sys.exit(0)
    
    input_path = sys.argv[1]
    as_of_str = None
    if len(sys.argv) >= 3:
        as_of_str = sys.argv[2]
    
    # Read and parse JSON
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except (IOError, OSError):
        print("error: could not read file")
        sys.exit(0)
    except json.JSONDecodeError:
        print("error: invalid JSON")
        sys.exit(0)
    
    # Validate structure
    if not isinstance(data, dict) or 'records' not in data:
        print("error: invalid JSON structure")
        sys.exit(0)
    
    records = data['records']
    if not isinstance(records, list):
        print("error: invalid JSON structure")
        sys.exit(0)
    
    # Determine as_of date
    if as_of_str:
        try:
            as_of = datetime.strptime(as_of_str, '%Y-%m-%d').date()
        except ValueError:
            print("error: invalid as_of date format")
            sys.exit(0)
    else:
        # Find latest created_at
        latest_date = None
        for record in records:
            if 'created_at' in record:
                try:
                    d = datetime.strptime(record['created_at'], '%Y-%m-%d').date()
                    if latest_date is None or d > latest_date:
                        latest_date = d
                except ValueError:
                    pass
        if latest_date:
            as_of = latest_date
        else:
            as_of = datetime.strptime('2026-05-26', '%Y-%m-%d').date()
    
    # Process each record
    findings_map = {}
    for record in records:
        record_id = record.get('record_id', 'unknown')
        findings = []
        
        # 1. missing_consent
        visibility_tier = record.get('visibility_tier', '')
        permission_state = record.get('permission_state', '')
        if visibility_tier == 'public' and permission_state != 'granted':
            findings.append('missing_consent')
        
        # 2. stale_evidence
        evidence_pointers = record.get('evidence_pointers', [])
        if isinstance(evidence_pointers, list):
            for ep in evidence_pointers:
                if isinstance(ep, dict) and 'created_at' in ep:
                    try:
                        ep_date = datetime.strptime(ep['created_at'], '%Y-%m-%d').date()
                        if (as_of - ep_date).days > 365:
                            if 'stale_evidence' not in findings:
                                findings.append('stale_evidence')
                    except ValueError:
                        pass
        
        # 3. overbroad_public_claim
        record_type = record.get('record_type', '')
        statement = record.get('statement', '')
        if record_type in ('claim', 'attestation', 'promise') and visibility_tier == 'public' and len(statement) > 240:
            findings.append('overbroad_public_claim')
        
        # 4. unsupported_authority_language
        review_state = record.get('review_state', '')
        if review_state != 'reviewed':
            statement_lower = statement.lower()
            authority_words = ['certified', 'authorized', 'legitimate', 'official']
            for word in authority_words:
                if word in statement_lower:
                    if 'unsupported_authority_language' not in findings:
                        findings.append('unsupported_authority_language')
                    break
        
        # Sort findings alphabetically
        findings.sort()
        findings_map[record_id] = findings
    
    # Output
    print(f"WITNESS RECORD VALIDATION (as_of {as_of})")
    print()
    
    ok_count = 0
    fail_count = 0
    total_findings = 0
    
    for record in records:
        record_id = record.get('record_id', 'unknown')
        findings = findings_map[record_id]
        if findings:
            print(f"{record_id}: {', '.join(findings)}")
            fail_count += 1
            total_findings += len(findings)
        else:
            print(f"{record_id}: OK")
            ok_count += 1
    
    print()
    print(f"SUMMARY: {ok_count} ok, {fail_count} with findings of {total_findings} total")

if __name__ == '__main__':
    main()