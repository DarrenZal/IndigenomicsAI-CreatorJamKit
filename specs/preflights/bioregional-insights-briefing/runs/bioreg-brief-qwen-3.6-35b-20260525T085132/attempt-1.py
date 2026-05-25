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
        print("error:")
        sys.exit(0)
    
    briefing_title = data.get("briefing_title", "")
    as_of = data.get("as_of", "")
    claims = data.get("claims", [])
    evidence_count = data.get("evidence_count", 0)
    observation_count = data.get("observation_count", 0)
    reviewer = data.get("reviewer", None)
    
    print(f"# {briefing_title}")
    print()
    print(f"_as of {as_of}_")
    print()
    print("## Inputs")
    print()
    print(f"- claims: {len(claims)}")
    print()
    print(f"- evidence pointers: {evidence_count}")
    print()
    print(f"- observations: {observation_count}")
    print()
    print("## Reviewer")
    print()
    if reviewer is None:
        print("NOT YET REVIEWED")
    else:
        print(f"{reviewer}")
    print()
    print("## Boundary")
    print()
    print("This briefing summarizes inputs. It does not certify, score, or authorize any action.")

if __name__ == "__main__":
    main()