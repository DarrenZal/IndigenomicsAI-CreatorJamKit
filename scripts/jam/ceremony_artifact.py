#!/usr/bin/env python3
"""ceremony_artifact.py — unified closing-ceremony artifact generator.

The autonomous overnight run produces three layered artifacts:
  - closing-witness-readout.md    (what happened — outcome-level)
  - coherence-synthesis.md        (what it means together — synthesis)
  - compositions/*.md             (what could be composed — proposals)

This module weaves them into a single ceremony-artifact.md document
that presents in narrative order, with smart cross-references and a
single closing boundary at the end. The output is what the operator
shows at the closing ceremony.

Discipline:
  - No new LLM calls. Pure markdown composition over the already-
    generated artifacts. The substrate has spoken in the underlying
    docs; this module just orders + braids them.
  - If any of the three input artifacts is missing, the corresponding
    ceremony section gracefully degrades to a placeholder.
  - Standard closing boundary preserved.

Usage:
  python3 scripts/jam/ceremony_artifact.py weave \\
      --persistent-root <path> \\
      --out <ceremony-artifact.md>

Auto-invoked at overnight_loop finish (last step after closing-readout,
coherence-synthesis, and compositions).
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_or_empty(path: Path) -> str:
    if path.exists():
        try:
            return path.read_text()
        except Exception:
            return ""
    return ""


def _strip_first_heading(text: str) -> str:
    """Remove the first '# Title' line + blank, so we can re-nest the
    document under our own h2."""
    lines = text.lstrip().splitlines()
    out_start = 0
    if lines and lines[0].startswith("# "):
        out_start = 1
        while out_start < len(lines) and not lines[out_start].strip():
            out_start += 1
    return "\n".join(lines[out_start:])


def _demote_headings(text: str, levels: int = 1) -> str:
    """Add `levels` `#` to every heading (# → ##, ## → ###, etc.).
    Caps at ###### so we don't drift into invalid markdown."""
    out_lines = []
    for line in text.splitlines():
        m = re.match(r"^(#{1,5})\s", line)
        if m:
            new_prefix = "#" * min(len(m.group(1)) + levels, 6)
            line = new_prefix + line[len(m.group(1)):]
        out_lines.append(line)
    return "\n".join(out_lines)


def _strip_trailing_closing_boundary(text: str) -> str:
    """Remove a trailing '## Closing Boundary' / '## Boundary' section
    so the unified artifact has ONE boundary at the end, not three."""
    # Match the last ## (Closing )?Boundary heading + everything after
    pattern = re.compile(
        r"\n(##+)\s+(Closing\s+)?Boundary\s*\n.*$",
        re.DOTALL | re.IGNORECASE,
    )
    return pattern.sub("\n", text).rstrip() + "\n"


def _read_compositions(comp_dir: Path) -> List[Dict[str, str]]:
    """Read all proposal-*.md files in the compositions dir. Returns
    list of {filename, title_line, body}.
    """
    out: List[Dict[str, str]] = []
    if not comp_dir.exists():
        return out
    for p in sorted(comp_dir.glob("proposal-*.md")):
        try:
            body = p.read_text()
        except Exception:
            continue
        # First non-empty line should be the title (# Composition Proposal...)
        title_line = ""
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title_line = stripped[2:]
                break
        out.append({
            "filename": p.name,
            "title_line": title_line,
            "body": body,
        })
    return out


def _read_compositions_index(comp_dir: Path) -> str:
    idx = comp_dir / "index.md"
    if idx.exists():
        try:
            return idx.read_text()
        except Exception:
            return ""
    return ""


def weave_artifact(persistent_root: Path) -> str:
    """Weave the three artifacts into one ceremony document. Never
    raises; missing sections degrade to placeholders."""
    closing_path = persistent_root / "closing-witness-readout.md"
    coherence_path = persistent_root / "coherence-synthesis.md"
    comp_dir = persistent_root / "compositions"

    closing = _read_or_empty(closing_path)
    coherence = _read_or_empty(coherence_path)
    compositions = _read_compositions(comp_dir)
    comp_index = _read_compositions_index(comp_dir)

    closing_section = (
        _demote_headings(
            _strip_trailing_closing_boundary(_strip_first_heading(closing)),
            levels=1,
        )
        if closing
        else "_closing-witness-readout.md was not produced; section "
             "degraded._"
    )
    coherence_section = (
        _demote_headings(
            _strip_trailing_closing_boundary(_strip_first_heading(coherence)),
            levels=1,
        )
        if coherence
        else "_coherence-synthesis.md was not produced; section "
             "degraded._"
    )

    parts: List[str] = []
    parts.append("# Closing Ceremony Artifact — Autonomous Overnight")
    parts.append("")
    parts.append(
        "_This document weaves the three layered outputs of tonight's "
        "autonomous overnight run into a single ceremony artifact. It "
        "speaks in the substrate's own voice (the underlying docs were "
        "produced by the gateway models honoring the kit's anti-overclaim "
        "discipline). No new LLM calls were made to produce this "
        "weaving — the artifacts already spoken were ordered + braided._"
    )
    parts.append("")
    parts.append(f"- generated: {now_iso()}")
    parts.append(f"- persistent_root: `{persistent_root}`")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Layer 1 — what happened
    parts.append("## 1. What happened (witness readout)")
    parts.append("")
    parts.append(
        "The autonomous loop attempted N rounds across the spec menu × "
        "model fleet. Each round was witnessed at five tiers (refusal "
        "gatekeeper, model refusal, reviewer halt, validator, operator "
        "review). The receipt below records outcomes — refusal "
        "outcomes are first-class, not failures."
    )
    parts.append("")
    parts.append(closing_section)
    parts.append("")
    parts.append("---")
    parts.append("")

    # Layer 2 — what it means together
    parts.append("## 2. What it means together (coherence synthesis)")
    parts.append("")
    parts.append(
        "After witnessing N rounds, the substrate read its own wall "
        "records and synthesized what the body of work says together. "
        "Clusters are descriptive operator labels, not authority claims. "
        "The synthesis prose was produced by the gateway model honoring "
        "the kit's verb discipline (observed, witnessed, recorded, "
        "surfaced)."
    )
    parts.append("")
    parts.append(coherence_section)
    parts.append("")
    parts.append("---")
    parts.append("")

    # Layer 3 — what could be composed
    parts.append("## 3. What could be composed next (proposals)")
    parts.append("")
    parts.append(
        "Using the published wall records as components, the substrate "
        "proposed compositions — new specs that would weave the "
        "published tools together. Each proposal carries explicit "
        "composition seams (where the components touch) AND composition "
        "caveats (the honest risks). Refusal-as-record: when components "
        "don't compose honestly, the proposer refused rather than "
        "fabricating."
    )
    parts.append("")
    if compositions:
        for c in compositions:
            parts.append(f"### Proposal: `{c['filename']}`")
            parts.append("")
            inner = _strip_trailing_closing_boundary(
                _strip_first_heading(c["body"]))
            parts.append(_demote_headings(inner, levels=2))
            parts.append("")
    else:
        parts.append(
            "_No compositions present at `compositions/`. Run "
            "`scripts/jam/agent_composer.py compose --persistent-root "
            "<root> --out-dir <root>/compositions ...` to generate._"
        )
        if comp_index:
            parts.append("")
            parts.append("### Composition index (from prior run)")
            parts.append("")
            parts.append(_demote_headings(
                _strip_first_heading(comp_index), levels=2))
    parts.append("")
    parts.append("---")
    parts.append("")

    # The single, unified closing boundary
    parts.append("## Closing Boundary")
    parts.append("")
    parts.append(
        "This ceremony artifact records what happened during an "
        "autonomous experimental overnight run. It does not establish "
        "legitimacy, authority, certification, community consent, or "
        "readiness for reuse."
    )
    parts.append("")
    parts.append(
        "The witness records on the wall are DRAFTS produced by the "
        "autonomous chain. The synthesis is the substrate's reading of "
        "its own work. The composition proposals are speculative — "
        "they propose, they do not authorize."
    )
    parts.append("")
    parts.append(
        "Operator review before external sharing is the human authority "
        "that ratifies the closing presentation. The audience at the "
        "closing ceremony is the next witness layer; their questions, "
        "objections, and observations are part of the witnessing record "
        "this artifact begins."
    )
    parts.append("")
    return "\n".join(parts)


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_weave(args):
    persistent_root = Path(args.persistent_root).expanduser().resolve()
    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = weave_artifact(persistent_root)
    out_path.write_text(md)
    print(f"ceremony-artifact → {out_path}")
    print(f"  size: {len(md)} bytes")


def main():
    ap = argparse.ArgumentParser(prog="ceremony_artifact.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    apw = sub.add_parser("weave")
    apw.add_argument("--persistent-root", required=True)
    apw.add_argument("--out", required=True)
    apw.set_defaults(func=cmd_weave)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
