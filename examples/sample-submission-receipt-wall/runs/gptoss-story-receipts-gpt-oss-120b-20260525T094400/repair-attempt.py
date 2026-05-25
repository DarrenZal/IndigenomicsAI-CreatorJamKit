#!/usr/bin/env python3
import sys
import json

def main():
    if len(sys.argv) < 2:
        print("error:")
        return

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        print("error:")
        return

    receipts = data.get("receipts")
    if not isinstance(receipts, list):
        print("error:")
        return

    total = len(receipts)

    # Gather public receipts with non‑empty stripped text
    public = []
    for rec in receipts:
        if not isinstance(rec, dict):
            continue
        if rec.get("display_scope") != "public":
            continue
        text = rec.get("text", "")
        if not isinstance(text, str):
            text = str(text)
        if text.strip() == "":
            continue
        public.append(rec)

    shown = len(public)

    # Sort by date then id
    public.sort(key=lambda r: (r.get("date", ""), r.get("id", "")))

    out = []
    out.append(f"# Story Receipts Wall ({shown} shown / {total} total)")
    out.append("")  # blank line after header

    for rec in public:
        contributor = rec.get("contributor", "")
        date = rec.get("date", "")
        out.append(f"## {contributor} \u2014 {date}")
        out.append("")  # blank line after receipt header

        text = rec.get("text", "")
        for line in text.splitlines():
            out.append(f"> {line}")

        out.append("")  # blank line after quoted text

        tags = rec.get("tags")
        if isinstance(tags, list) and tags:
            out.append("tags: " + ", ".join(str(t) for t in tags))
            out.append("")  # blank line after tags line (end of block)

    out.append("---")
    out.append("")
    withheld = total - shown
    out.append(f"Receipts withheld from display: {withheld}")

    sys.stdout.write("\n".join(out))

if __name__ == "__main__":
    main()