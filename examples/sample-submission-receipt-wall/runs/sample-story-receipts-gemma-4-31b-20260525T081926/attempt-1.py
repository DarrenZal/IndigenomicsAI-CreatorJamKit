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
        print("error: could not read or parse input file")
        sys.exit(0)

    if not isinstance(data, dict) or "receipts" not in data:
        # While not explicitly requested, we handle malformed JSON structure as an error
        print("error: invalid JSON structure")
        sys.exit(0)

    receipts = data["receipts"]
    total_count = len(receipts)
    
    public_receipts = []
    for r in receipts:
        # Check if it's a dict to avoid crashes on malformed list items
        if not isinstance(r, dict):
            continue
            
        scope = r.get("display_scope")
        text = r.get("text")
        
        # Drop rules:
        # 1. display_scope must be exactly "public"
        # 2. text must be non-empty after stripping
        if scope == "public" and isinstance(text, str) and text.strip():
            public_receipts.append(r)

    # Sort by date ascending, then by id ascending
    # We use .get() with empty strings to ensure sorting doesn't crash on missing keys
    public_receipts.sort(key=lambda x: (x.get("date", ""), x.get("id", "")))

    shown_count = len(public_receipts)
    withheld_count = total_count - shown_count

    # (1) Header line
    print(f"# Story Receipts Wall ({shown_count} shown / {total_count} total)")
    
    # (2) One blank line after header
    print()

    # (3) Public receipt blocks
    for r in public_receipts:
        contributor = r.get("contributor", "")
        date = r.get("date", "")
        text = r.get("text", "")
        tags = r.get("tags")

        # Header: ## <contributor> — <date> (U+2014 em-dash)
        print(f"## {contributor} — {date}")
        print()

        # Quoted text: preserve internal line breaks, quote every line
        lines = text.splitlines()
        # If text is just whitespace but passed the strip() check, 
        # splitlines() might be empty or contain empty strings.
        # The spec says "preserve internal line breaks".
        for line in lines:
            print(f"> {line}")
        
        # Handle case where text ends with a newline (splitlines doesn't keep trailing empty)
        # but the spec says "quote every line individually". 
        # Standard splitlines behavior is usually sufficient for "lines of text".

        print()

        # Tags line
        if isinstance(tags, list) and tags:
            print(f"tags: {', '.join(map(str, tags))}")
        
        # Exactly one blank line after the block
        print()

    # (4) Footer
    print("---")
    print()
    print(f"Receipts withheld from display: {withheld_count}")

if __name__ == "__main__":
    main()