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
        print("error: invalid JSON structure")
        sys.exit(0)

    receipts = data["receipts"]
    if not isinstance(receipts, list):
        print("error: receipts must be a list")
        sys.exit(0)

    total_count = len(receipts)
    
    public_receipts = []
    for r in receipts:
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
        # splitlines() is used to handle various newline characters
        lines = text.splitlines()
        for line in lines:
            print(f"> {line}")
        
        # The spec says: "After the tags line (or after the quoted text if no tags), 
        # emit exactly one blank line before the next receipt block (or the footer)."
        # The previous attempt added an extra print() before the tags check.
        
        if isinstance(tags, list) and tags:
            # We need a blank line between the quoted text and the tags line? 
            # Looking at the failed test output:
            # '> Read with the room.', '', 'tags: learning', ''
            # This implies a blank line between text and tags.
            print()
            print(f"tags: {', '.join(map(str, tags))}")
        
        # Exactly one blank line after the block
        print()

    # (4) Footer
    # The failed tests show that the previous attempt had an extra blank line 
    # before the '---' when the last receipt block ended.
    # Since we print() at the end of every block, we have one blank line.
    # The spec says: "The --- is on its own line, then one blank line, then the withheld-count line."
    # If there were no public receipts, we still need the footer.
    
    # If we had public receipts, the last one ended with a blank line.
    # The test failure shows: ['...text', '', '', '---', '', '...'] 
    # vs ['...text', '', '---', '', '...']
    # This means the blank line at the end of the block IS the blank line before '---'.
    # But wait, the spec says: "After the tags line... emit exactly one blank line before the next receipt block (or the footer)."
    # Then "The --- is on its own line".
    # This means: [Block] -> [Blank Line] -> [---] -> [Blank Line] -> [Withheld Count]
    
    # If there are no public receipts, we don't have that trailing blank line from the loop.
    if shown_count == 0:
        # No blocks, just header, blank line, then footer.
        # Header is already printed, then print().
        pass 

    print("---")
    print()
    print(f"Receipts withheld from display: {withheld_count}")

if __name__ == "__main__":
    main()