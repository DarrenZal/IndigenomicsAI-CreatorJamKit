import sys
import json

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("error: expected exactly one argument: receipts_json_path")
        sys.exit(0)
    
    json_path = sys.argv[1]
    
    # Read the input file
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        print("error: could not read file")
        sys.exit(0)
    
    # Parse JSON
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        print("error: invalid JSON")
        sys.exit(0)
    
    # Validate structure
    if not isinstance(data, dict) or 'receipts' not in data:
        print("error: invalid JSON structure")
        sys.exit(0)
    
    receipts = data['receipts']
    if not isinstance(receipts, list):
        print("error: receipts must be an array")
        sys.exit(0)
    
    total_count = len(receipts)
    
    # Filter public receipts with non-empty text
    public_receipts = []
    for r in receipts:
        if not isinstance(r, dict):
            continue
        display_scope = r.get('display_scope', '')
        if display_scope != 'public':
            continue
        text = r.get('text', '')
        if not isinstance(text, str):
            continue
        if text.strip() == '':
            continue
        public_receipts.append(r)
    
    # Sort by date ascending, then by id ascending for ties
    public_receipts.sort(key=lambda r: (r.get('date', ''), r.get('id', '')))
    
    shown_count = len(public_receipts)
    withheld_count = total_count - shown_count
    
    # Build output
    output_lines = []
    
    # (1) Header line
    output_lines.append(f"# Story Receipts Wall ({shown_count} shown / {total_count} total)")
    
    # (2) One blank line after the header
    output_lines.append("")
    
    # (3) Each public receipt block
    for r in public_receipts:
        contributor = r.get('contributor', '')
        date = r.get('date', '')
        text = r.get('text', '')
        tags = r.get('tags', [])
        
        # ## <contributor> — <date>
        output_lines.append(f"## {contributor} — {date}")
        
        # Quote each line of text with "> "
        text_lines = text.split('\n')
        for line in text_lines:
            output_lines.append(f"> {line}")
        
        # Tags line if present and non-empty
        if tags and isinstance(tags, list) and len(tags) > 0:
            tags_str = ", ".join(str(t) for t in tags)
            output_lines.append(f"tags: {tags_str}")
        
        # One blank line after each receipt block
        output_lines.append("")
    
    # (4) Footer
    output_lines.append("---")
    output_lines.append("")
    output_lines.append(f"Receipts withheld from display: {withheld_count}")
    
    # Print output
    print('\n'.join(output_lines))

if __name__ == '__main__':
    main()