#!/usr/bin/env python3
"""Check that bundle depends_on references resolve within seeded examples."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC_ID_RE = re.compile(r"^doc_id:\s*(.+?)\s*$", re.MULTILINE)
DEPENDS_RE = re.compile(r"^depends_on:\s*$\n((?:\s+- .+\n)*)", re.MULTILINE)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_doc_ids():
    ids = {}
    for path in (ROOT / "examples").rglob("*.md"):
        match = DOC_ID_RE.search(read(path))
        if match:
            ids[match.group(1).strip()] = path.relative_to(ROOT)
    return ids


def collect_dependencies():
    deps = []
    for path in (ROOT / "examples").rglob("*.md"):
        text = read(path)
        match = DEPENDS_RE.search(text)
        if not match:
            continue
        for line in match.group(1).splitlines():
            dep = line.strip().removeprefix("-").strip()
            if dep:
                deps.append((path.relative_to(ROOT), dep))
    return deps


def main() -> int:
    ids = collect_doc_ids()
    missing = []
    for source, dep in collect_dependencies():
        if dep not in ids:
            missing.append((source, dep))

    if missing:
        print("Missing bundle dependencies:")
        for source, dep in missing:
            print(f"- {source}: {dep}")
        return 1

    print(f"bundle link check passed ({len(ids)} doc_ids)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

