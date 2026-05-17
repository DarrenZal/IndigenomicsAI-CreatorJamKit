#!/usr/bin/env python3
"""Lightweight Markdown frontmatter check for the Creator Jam Kit."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECK_DIRS = [ROOT / "docs", ROOT / "templates", ROOT / "examples", ROOT / "workshop", ROOT / "games"]


def markdown_files():
    for base in CHECK_DIRS:
        if not base.exists():
            continue
        yield from sorted(base.rglob("*.md"))


def has_frontmatter(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return text.startswith("---\n")


def main() -> int:
    warnings = []
    required_for_templates = []

    for path in markdown_files():
        rel = path.relative_to(ROOT)
        if rel.parts[0] == "templates" and not has_frontmatter(path):
            required_for_templates.append(str(rel))
        if "\t" in path.read_text(encoding="utf-8"):
            warnings.append(f"{rel}: contains tab characters")

    if required_for_templates:
        print("Templates missing frontmatter:")
        for item in required_for_templates:
            print(f"- {item}")
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}")

    print("frontmatter check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
