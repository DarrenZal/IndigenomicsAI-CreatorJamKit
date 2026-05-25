import json
import sys

def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError, OSError):
        print("error:")
        sys.exit(0)

    try:
        title = data.get("briefing_title", "")
        as_of = data.get("as_of", "")
        claims = data.get("claims", [])
        evidence_count = data.get("evidence_count", 0)
        observation_count = data.get("observation_count", 0)
        reviewer = data.get("reviewer")

        # Markdown construction
        output = []
        output.append(f"# {title}")
        output.append("")
        output.append(f"_as of {as_of}_")
        output.append("")
        output.append("## Inputs")
        output.append("")
        output.append(f"- claims: {len(claims)}")
        output.append("")
        output.append(f"- evidence pointers: {evidence_count}")
        output.append("")
        output.append(f"- observations: {observation_count}")
        output.append("")
        output.append("## Reviewer")
        output.append("")
        
        if reviewer is None:
            output.append("NOT YET REVIEWED")
        else:
            output.append(str(reviewer))
            
        output.append("")
        output.append("## Boundary")
        output.append("")
        output.append("This briefing summarizes inputs. It does not certify, score, or authorize any action.")

        print("\n".join(output))

    except Exception:
        print("error:")
        sys.exit(0)

if __name__ == "__main__":
    main()