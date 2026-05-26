#!/usr/bin/env python3
"""loop_safety.py — overnight-loop-time safety helpers.

Loop-time (not operator-time) safety primitives used by overnight_loop.py:

  - gateway preflight (probe /health before each round)
  - write-boundary guard (refuse paths outside the persistent dir)
  - credential regex scan (TELUS responses + generated build_attempt.py)
  - sentinel-stop file detection
  - HALT-CREDS.txt writer

These are intentionally lightweight defensive checks. They are NOT a
replacement for the operator-time `audit-public-safety.sh` (which has
git context the loop does not). They are the loop-time minimum so an
autonomous run cannot silently exfiltrate credentials, write outside
its persistent dir, or keep running after a sentinel-stop is requested.

Usage (called from overnight_loop.py):
    from jam.loop_safety import (
        check_gateway_health, scan_for_credentials,
        ensure_path_within, check_sentinel_stop, write_halt_creds,
    )
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple


# --------------------------------------------------------------------- #
# Credential-scan regex                                                 #
# --------------------------------------------------------------------- #

# Patterns are intentionally narrow + bounded to catch the obvious
# credential-leak class. Each pattern must be specific enough to avoid
# triggering on the kit's discipline-text (which discusses these terms
# at length). When in doubt, prefer false-negatives at the regex layer
# — the audit-public-safety.sh at operator-time is the wider net.
CREDENTIAL_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # bearer-token shape: "Bearer <thing-that-looks-like-a-token>"
    ("bearer_token_value",
     re.compile(r"\bBearer\s+([A-Za-z0-9_\-\.]{20,})", re.IGNORECASE)),
    # api_key / API_KEY = "value" (assignment shape)
    ("api_key_assignment",
     re.compile(r"\b(api[_\-]?key|apikey|secret|password|access[_\-]?token|"
                 r"private[_\-]?key|client[_\-]?secret)"
                 r"\s*[=:]\s*[\"']?([A-Za-z0-9_\-\.+/=]{16,})",
                 re.IGNORECASE)),
    # iai_dev_* dev keys + sk-* style OpenAI-class keys
    ("dev_key_prefix",
     re.compile(r"\b(iai_dev_[a-z]+|sk-[A-Za-z0-9]{20,})\b")),
    # JWT-shape: three base64 segments separated by .
    ("jwt_shape",
     re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")),
    # AWS-style access key id (AKIA…)
    ("aws_akia",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # PEM block headers
    ("pem_private_key",
     re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----")),
    # Codex C2 additions:
    # GitHub PAT / OAuth tokens (ghp_/gho_/ghs_/ghu_/ghr_/github_pat_)
    ("github_token",
     re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}\b|"
                 r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    # Slack tokens (xoxb-, xoxa-, xoxp-, xoxr-)
    ("slack_token",
     re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    # Telegram bot tokens: <numeric-id>:<35-char-base62>
    ("telegram_bot_token",
     re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{35}\b")),
    # NOTE: a generic 40+ char hex pattern was added per Codex C2 review
    # but REMOVED 2026-05-26 after the overnight run halted Loop 1 on a
    # legitimate SHA-256 packet_hash value emitted by the
    # sensor-to-receipt-pipeline build. Content-addressed hashes are a
    # foundational kit primitive — they appear in receipts, build
    # packets, witness records BY DESIGN. The pattern was catching the
    # substrate's own discipline. Real credential SHAPES (bearer tokens,
    # api_key assignments, dev key prefixes, JWTs, AWS AKIA, PEM blocks,
    # GitHub / Slack / Telegram tokens) all have distinguishing prefixes
    # or assignment context covered by the patterns above. A standalone
    # 40-char hex string is almost never a credential.
]


def scan_for_credentials(text: str,
                          source_label: str = "unknown") -> List[dict]:
    """Scan text for credential-shape patterns. Returns list of hits,
    each with {pattern_name, source, snippet (bounded), span}.

    NEVER raises. Empty list = clean.
    """
    if not isinstance(text, str) or not text:
        return []
    hits = []
    for name, pattern in CREDENTIAL_PATTERNS:
        for m in pattern.finditer(text):
            start, end = m.span()
            # Bound snippet to 80 chars around the match, and partially
            # mask the matched value so the HALT log itself doesn't echo
            # the credential.
            snippet = text[max(0, start - 20):min(len(text), end + 20)]
            matched_value = m.group(0)
            masked = (matched_value[:6] + "…[redacted-len="
                       + str(len(matched_value)) + "]…"
                       + matched_value[-4:]) if len(matched_value) > 12 else "[…redacted…]"
            # Codex C1: replace the FULL m.group(0) span in snippet, AND
            # also redact any sub-group capture if it appears separately
            # in the snippet. Defense-in-depth against bearer-style patterns
            # where group(1) is the value-only portion.
            safe_snippet = snippet[:80].replace(matched_value, "[MATCH]")
            if m.groups():
                for sub in m.groups():
                    if sub and isinstance(sub, str) and len(sub) > 8:
                        safe_snippet = safe_snippet.replace(sub, "[MATCH-VAL]")
            hits.append({
                "pattern_name": name,
                "source": source_label,
                "snippet_context": safe_snippet,
                "matched_value_masked": masked,
                "span": [start, end],
            })
    return hits


# --------------------------------------------------------------------- #
# Write-boundary guard                                                  #
# --------------------------------------------------------------------- #

def ensure_path_within(target: Path, allowed_root: Path) -> Path:
    """Resolve target and verify it sits under allowed_root.

    Raises PermissionError if the resolved target escapes allowed_root.
    Uses .resolve() to defeat symlink + '..' tricks; allowed_root
    must also resolve cleanly.
    """
    allowed = allowed_root.expanduser().resolve()
    candidate = Path(target).expanduser().resolve()
    try:
        candidate.relative_to(allowed)
    except ValueError:
        raise PermissionError(
            f"write-boundary violation: {candidate} is outside {allowed}"
        )
    return candidate


# --------------------------------------------------------------------- #
# Gateway preflight                                                     #
# --------------------------------------------------------------------- #

def check_gateway_health(gateway_url: str, timeout: int = 10) -> Tuple[bool, str]:
    """Probe gateway /health. Returns (ok, reason).

    Returns (True, status) on 2xx. Returns (False, reason) on any failure.
    NEVER raises.
    """
    url = gateway_url.rstrip("/") + "/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            if 200 <= code < 300:
                # Read a small bound so we don't slurp a huge body
                body = resp.read(512).decode("utf-8", errors="replace")
                return True, f"http {code}: {body[:200]}"
            return False, f"non-2xx: http {code}"
    except Exception as e:
        return False, f"gateway preflight failed: {e!r}"


# --------------------------------------------------------------------- #
# Sentinel-stop                                                         #
# --------------------------------------------------------------------- #

def check_sentinel_stop(persistent_root: Path) -> Optional[str]:
    """If a STOP file exists in persistent_root, return its contents
    (or empty string). Otherwise None.

    Sentinel files (in order checked):
      <persistent_root>/STOP
      <persistent_root>/STOP.txt
    """
    for name in ("STOP", "STOP.txt"):
        p = Path(persistent_root).expanduser() / name
        if p.exists():
            try:
                return p.read_text()[:500] or ""
            except Exception:
                return ""
    return None


# --------------------------------------------------------------------- #
# HALT writer                                                           #
# --------------------------------------------------------------------- #

def write_halt(persistent_root: Path, kind: str, details: dict) -> Path:
    """Write a HALT-<kind>.txt with details. Returns the path.

    kind is uppercase short label (e.g., 'CREDS', 'BOUNDARY', 'GATEWAY').
    """
    pr = Path(persistent_root).expanduser()
    pr.mkdir(parents=True, exist_ok=True)
    halt_path = pr / f"HALT-{kind.upper()}.txt"
    record = {
        "halt_at": datetime.now(timezone.utc).isoformat(),
        "kind": kind.upper(),
        "details": details,
    }
    halt_path.write_text(
        f"# HALT — {kind.upper()}\n\n"
        f"Time: {record['halt_at']}\n\n"
        f"## Details\n\n"
        f"```json\n{json.dumps(details, indent=2)}\n```\n"
    )
    # Also append a JSONL entry for machine parsing
    log_path = pr / "halt-log.jsonl"
    with log_path.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return halt_path


def write_halt_creds(persistent_root: Path,
                     hits: List[dict],
                     source_label: str) -> Path:
    """Convenience: HALT due to credential-scan hits."""
    return write_halt(persistent_root, "CREDS", {
        "source": source_label,
        "hit_count": len(hits),
        "hits": hits[:10],  # bound size; halt log is for humans
    })


# --------------------------------------------------------------------- #
# Self-test                                                             #
# --------------------------------------------------------------------- #

if __name__ == "__main__":
    # Lightweight self-check; not part of the test suite.
    samples = [
        ("clean text — kelp herring eelgrass salmon",
         0, "clean"),
        ("Authorization: Bearer abc123def456ghi789jkl012mno345",
         1, "bearer"),
        ("iai_dev_victoria leaked into output",
         1, "dev_key"),
        ("api_key = 'sk-1234567890abcdefghij'",
         2, "api_key + sk-prefix"),  # both patterns fire
        ("-----BEGIN PRIVATE KEY-----\nMIIEv...",
         1, "pem"),
    ]
    for text, expected_min, label in samples:
        hits = scan_for_credentials(text, source_label=label)
        status = "ok" if len(hits) >= expected_min else "FAIL"
        print(f"[{status}] {label}: {len(hits)} hits (expected >= {expected_min})")
