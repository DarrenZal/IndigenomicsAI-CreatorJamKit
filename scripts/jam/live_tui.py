#!/usr/bin/env python3
"""Live curses TUI for monitoring the overnight automated-jam loop.

Reads a JSONL master log produced by overnight_loop.py and renders a
projection-friendly dashboard: recent rounds (color-coded), per-model
totals, per-spec totals, and elapsed / budget headers.

Pure stdlib. Designed for a 9-hour overnight projection.
"""

from __future__ import annotations

import argparse
import curses
import json
import os
import signal
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# --- Defaults ---------------------------------------------------------------

DEFAULT_LOG = "/Users/darrenzal/overnight-jam-2026-05-26/overnight-master-log.jsonl"
DEFAULT_STOP = "/Users/darrenzal/overnight-jam-2026-05-26/STOP"
REFRESH_SECONDS = 2.0
POLL_SECONDS = 1.0
RECENT_ROUNDS = 15

# --- Color classification ---------------------------------------------------

COLOR_GREEN = "green"
COLOR_YELLOW = "yellow"
COLOR_RED = "red"
COLOR_GRAY = "gray"
COLOR_DEFAULT = "default"

OUTCOME_PREFIXES = (
    ("frozen-and-published", COLOR_GREEN),
    ("review-halted", COLOR_YELLOW),
    ("refused", COLOR_RED),
    ("error", COLOR_GRAY),
)


def classify_outcome(outcome: str | None, subprocess_returncode: int | None) -> str:
    """Map an outcome string + subprocess return code to a color name.

    Rules (in order):
      - subprocess_returncode != 0 -> gray (treated as error regardless of outcome text)
      - prefix match on outcome
      - otherwise -> default

    A None subprocess_returncode is treated as 0 (success) — it only signals
    "not yet known" and we don't want to gray-out a frozen round on that basis.
    """
    if subprocess_returncode is not None and subprocess_returncode != 0:
        return COLOR_GRAY
    if not outcome:
        return COLOR_DEFAULT
    text = outcome.strip()
    for prefix, color in OUTCOME_PREFIXES:
        if text.startswith(prefix):
            return color
    return COLOR_DEFAULT


def outcome_bucket(outcome: str | None, subprocess_returncode: int | None) -> str:
    """Map an outcome to a short bucket label used in per-model/spec totals."""
    color = classify_outcome(outcome, subprocess_returncode)
    if color == COLOR_GREEN:
        return "frozen"
    if color == COLOR_YELLOW:
        return "review-halted"
    if color == COLOR_RED:
        return "refused"
    if color == COLOR_GRAY:
        return "error"
    return "other"


# --- State / aggregation ----------------------------------------------------


def new_state() -> dict:
    """Build an empty aggregator state."""
    return {
        "started_at": None,          # datetime or None
        "models": [],                # list[str] declared at loop_start
        "specs": [],                 # list[str] declared at loop_start
        "max_rounds": None,
        "time_budget_hours": None,
        "max_telus_calls": None,
        "rounds": [],                # list[dict] in arrival order
        "per_model": defaultdict(lambda: {
            "rounds": 0, "frozen": 0, "refused": 0,
            "review-halted": 0, "error": 0, "other": 0,
            "telus_calls": 0,
        }),
        "per_spec": defaultdict(lambda: {
            "rounds": 0, "frozen": 0, "refused": 0,
            "review-halted": 0, "error": 0, "other": 0,
        }),
        "total_telus_calls": 0,
    }


def _parse_started_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        # Python 3.11+ accepts "...+00:00" via fromisoformat; .replace("Z", "+00:00")
        # for older serializers.
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def apply_event(state: dict, event: dict) -> None:
    """Mutate `state` by applying a single JSONL event.

    Unknown `kind` values are silently skipped.
    """
    kind = event.get("kind")
    if kind == "loop_start":
        state["started_at"] = _parse_started_at(event.get("started_at"))
        models = event.get("models") or []
        specs = event.get("specs") or []
        if isinstance(models, list):
            state["models"] = list(models)
        if isinstance(specs, list):
            state["specs"] = list(specs)
        state["max_rounds"] = event.get("max_rounds")
        state["time_budget_hours"] = event.get("time_budget_hours")
        state["max_telus_calls"] = event.get("max_telus_calls")
        return

    if kind == "round":
        state["rounds"].append(event)
        model = event.get("model") or "(unknown)"
        spec = event.get("spec_id") or "(unknown)"
        outcome = event.get("outcome")
        rc = event.get("subprocess_returncode")
        bucket = outcome_bucket(outcome, rc)

        m = state["per_model"][model]
        m["rounds"] += 1
        m[bucket] = m.get(bucket, 0) + 1
        try:
            m["telus_calls"] += int(event.get("telus_calls") or 0)
        except (TypeError, ValueError):
            pass

        s = state["per_spec"][spec]
        s["rounds"] += 1
        s[bucket] = s.get(bucket, 0) + 1

        try:
            state["total_telus_calls"] += int(event.get("telus_calls") or 0)
        except (TypeError, ValueError):
            pass
        return

    # Unknown kind: ignore quietly. Future event types may be added.


def parse_jsonl_lines(lines):
    """Yield parsed JSON dicts from an iterable of strings. Bad lines are skipped."""
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def build_state_from_lines(lines) -> dict:
    """Build a fresh state by applying every event from `lines`."""
    state = new_state()
    for event in parse_jsonl_lines(lines):
        apply_event(state, event)
    return state


# --- Tail-follow ------------------------------------------------------------


class TailFollower:
    """Stdlib tail -F. Handles non-existent files, rotation, and partial lines.

    Usage:
        follower = TailFollower(path)
        new_lines = follower.read_new_lines()  # returns list[str]; may be empty
    """

    def __init__(self, path: str | os.PathLike):
        self.path = str(path)
        self._pos = 0
        self._inode = None
        self._buffer = ""  # holds a partial trailing line across reads

    def _stat(self):
        try:
            return os.stat(self.path)
        except FileNotFoundError:
            return None

    def read_new_lines(self) -> list[str]:
        """Return any complete lines that have appeared since the last call.

        Behaviour:
          - File missing -> [].
          - File shrank or inode changed -> restart from offset 0.
          - Partial trailing line (no terminating newline) is buffered and
            returned only after the newline arrives.
        """
        st = self._stat()
        if st is None:
            return []

        rotated = False
        if self._inode is not None and st.st_ino != self._inode:
            rotated = True
        if st.st_size < self._pos:
            rotated = True

        if rotated:
            self._pos = 0
            self._buffer = ""

        self._inode = st.st_ino

        if st.st_size == self._pos:
            return []

        with open(self.path, "r", encoding="utf-8", errors="replace") as fh:
            fh.seek(self._pos)
            chunk = fh.read()
            self._pos = fh.tell()

        data = self._buffer + chunk
        if data.endswith("\n"):
            lines = data.splitlines()
            self._buffer = ""
        else:
            parts = data.split("\n")
            self._buffer = parts[-1]
            lines = parts[:-1]

        # Filter out blank lines but preserve order.
        return [ln for ln in lines if ln.strip()]


# --- Formatting helpers -----------------------------------------------------


def format_elapsed(started_at: datetime | None, now: datetime | None = None) -> str:
    if started_at is None:
        return "--h --m"
    now = now or datetime.now(timezone.utc)
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    delta = now - started_at
    total_seconds = max(0, int(delta.total_seconds()))
    hours, rem = divmod(total_seconds, 3600)
    minutes = rem // 60
    return f"{hours}h {minutes:02d}m"


def truncate(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: width - 1] + "…"


def format_header(state: dict, now: datetime | None = None, stop_present: bool = False) -> str:
    elapsed = format_elapsed(state.get("started_at"), now=now)
    rounds_done = len(state.get("rounds", []))
    max_rounds = state.get("max_rounds")
    max_calls = state.get("max_telus_calls")
    calls = state.get("total_telus_calls", 0)
    parts = [
        f"Overnight Jam Loop  ·  {elapsed} elapsed",
        f"{rounds_done}/{max_rounds if max_rounds is not None else '?'} rounds",
        f"{calls}/{max_calls if max_calls is not None else '?'} TELUS calls",
    ]
    if stop_present:
        parts.append("*** HALT REQUESTED ***")
    return "  ·  ".join(parts)


def format_recent_round(round_event: dict, width: int) -> tuple[str, str]:
    """Return (text, color_name) for one recent-round row, fitted to width."""
    idx = round_event.get("round_idx", "?")
    spec = round_event.get("spec_id", "?")
    model = round_event.get("model", "?")
    outcome = round_event.get("outcome", "") or ""
    rc = round_event.get("subprocess_returncode")
    elapsed = round_event.get("elapsed_seconds", 0.0) or 0.0
    color = classify_outcome(outcome, rc)

    # Fixed-ish columns; if there's no room we truncate the outcome.
    spec_col = truncate(spec, 36).ljust(36)
    model_col = truncate(model, 14).ljust(14)
    idx_col = f"#{idx:>3}"
    try:
        elapsed_col = f"{float(elapsed):>6.1f}s"
    except (TypeError, ValueError):
        elapsed_col = "    ?s"

    # Compute how much room is left for the outcome string.
    prefix = f"  {idx_col}  {spec_col}  {model_col}  "
    suffix = f"  {elapsed_col}"
    room = width - len(prefix) - len(suffix)
    if room < 8:
        # Drop the elapsed column to make room for outcome.
        suffix = ""
        room = width - len(prefix)
    outcome_col = truncate(outcome, max(0, room))
    line = prefix + outcome_col.ljust(max(0, room)) + suffix
    return truncate(line, width), color


def format_model_row(model: str, totals: dict, width: int) -> str:
    line = (
        f"  {truncate(model, 16).ljust(16)}  "
        f"{totals.get('rounds', 0):>3} rounds  "
        f"{totals.get('frozen', 0):>3} frozen  "
        f"{totals.get('refused', 0):>3} refused  "
        f"{totals.get('review-halted', 0):>3} review-halted  "
        f"{totals.get('error', 0):>3} error  "
        f"{totals.get('telus_calls', 0):>4} calls"
    )
    return truncate(line, width)


def format_spec_row(spec: str, totals: dict, width: int) -> str:
    line = (
        f"  {truncate(spec, 38).ljust(38)}  "
        f"{totals.get('rounds', 0):>3} rounds  "
        f"{totals.get('frozen', 0):>3} frozen  "
        f"{totals.get('refused', 0):>3} refused  "
        f"{totals.get('review-halted', 0):>3} review-halted  "
        f"{totals.get('error', 0):>3} error"
    )
    return truncate(line, width)


def build_render_lines(state: dict, width: int, *, now: datetime | None = None,
                       stop_present: bool = False) -> list[tuple[str, str]]:
    """Return a list of (text, color) lines to render. Pure function.

    Color is one of: default, green, yellow, red, gray, bold-default.
    """
    lines: list[tuple[str, str]] = []

    header = format_header(state, now=now, stop_present=stop_present)
    lines.append((truncate(header, width), "red" if stop_present else "bold-default"))
    stop_path = DEFAULT_STOP
    lines.append((truncate(f"  STOP file: {stop_path}", width), "default"))
    lines.append(("", "default"))

    lines.append(("Recent rounds", "bold-default"))
    recent = state.get("rounds", [])[-RECENT_ROUNDS:][::-1]  # newest first
    if not recent:
        lines.append(("  (no rounds yet — waiting for first round to finish…)", "default"))
    else:
        for r in recent:
            text, color = format_recent_round(r, width)
            lines.append((text, color))
    lines.append(("", "default"))

    lines.append(("Per-model totals", "bold-default"))
    per_model = state.get("per_model", {})
    # Preserve declared model order; append any extras at the end.
    declared = list(state.get("models", []))
    seen = set()
    ordered_models = []
    for m in declared:
        if m in per_model:
            ordered_models.append(m)
            seen.add(m)
    for m in per_model:
        if m not in seen:
            ordered_models.append(m)
    if not ordered_models:
        lines.append(("  (no model activity yet)", "default"))
    else:
        for m in ordered_models:
            lines.append((format_model_row(m, per_model[m], width), "default"))
    lines.append(("", "default"))

    lines.append(("Per-spec totals", "bold-default"))
    per_spec = state.get("per_spec", {})
    declared_specs = list(state.get("specs", []))
    seen_s = set()
    ordered_specs = []
    for s in declared_specs:
        if s in per_spec:
            ordered_specs.append(s)
            seen_s.add(s)
    for s in per_spec:
        if s not in seen_s:
            ordered_specs.append(s)
    if not ordered_specs:
        lines.append(("  (no spec activity yet)", "default"))
    else:
        for s in ordered_specs:
            lines.append((format_spec_row(s, per_spec[s], width), "default"))
    lines.append(("", "default"))

    ts = (now or datetime.now()).strftime("%H:%M:%S")
    footer = f"Last update: {ts}  ·  Press Ctrl-C to exit"
    lines.append((truncate(footer, width), "default"))
    return lines


# --- Curses rendering -------------------------------------------------------


def _setup_colors() -> dict:
    """Initialize color pairs and return name -> attr mapping."""
    pair_map: dict[str, int] = {}
    if not curses.has_colors():
        return {}
    try:
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        curses.init_pair(1, curses.COLOR_GREEN, bg)
        curses.init_pair(2, curses.COLOR_YELLOW, bg)
        curses.init_pair(3, curses.COLOR_RED, bg)
        # "gray" → dim white
        curses.init_pair(4, curses.COLOR_WHITE, bg)
        curses.init_pair(5, curses.COLOR_WHITE, bg)
        pair_map["green"] = curses.color_pair(1) | curses.A_BOLD
        pair_map["yellow"] = curses.color_pair(2) | curses.A_BOLD
        pair_map["red"] = curses.color_pair(3) | curses.A_BOLD
        pair_map["gray"] = curses.color_pair(4) | curses.A_DIM
        pair_map["default"] = curses.color_pair(5)
        pair_map["bold-default"] = curses.color_pair(5) | curses.A_BOLD
    except curses.error:
        return {}
    return pair_map


def _attr_for(pair_map: dict, color: str) -> int:
    if not pair_map:
        return curses.A_BOLD if color == "bold-default" else curses.A_NORMAL
    return pair_map.get(color, pair_map.get("default", curses.A_NORMAL))


def _curses_main(stdscr, log_path: str, stop_path: str) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(int(REFRESH_SECONDS * 1000))
    pair_map = _setup_colors()

    follower = TailFollower(log_path)
    state = new_state()
    last_render = 0.0
    last_poll = 0.0

    # Initial fill — read everything currently present.
    initial = follower.read_new_lines()
    for ev in parse_jsonl_lines(initial):
        apply_event(state, ev)

    while True:
        now_ts = time.time()

        if now_ts - last_poll >= POLL_SECONDS:
            try:
                new_lines = follower.read_new_lines()
            except OSError:
                new_lines = []
            for ev in parse_jsonl_lines(new_lines):
                apply_event(state, ev)
            last_poll = now_ts

        if now_ts - last_render >= REFRESH_SECONDS:
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            stop_present = os.path.exists(stop_path)
            now_dt_utc = datetime.now(timezone.utc)
            now_dt_local = datetime.now()
            rendered = build_render_lines(
                state, width, now=now_dt_utc, stop_present=stop_present
            )
            # Substitute local time into the last footer line if it's present.
            if rendered:
                last_text, last_color = rendered[-1]
                if last_text.startswith("Last update:"):
                    footer = (
                        f"Last update: {now_dt_local.strftime('%H:%M:%S')}  ·  "
                        "Press Ctrl-C to exit"
                    )
                    rendered[-1] = (truncate(footer, width), last_color)

            for row, (text, color) in enumerate(rendered):
                if row >= height:
                    break
                attr = _attr_for(pair_map, color)
                try:
                    stdscr.addnstr(row, 0, text, max(0, width - 1), attr)
                except curses.error:
                    pass
            try:
                stdscr.refresh()
            except curses.error:
                pass
            last_render = now_ts

        # Handle keys / resize.
        try:
            ch = stdscr.getch()
        except KeyboardInterrupt:
            break
        if ch == curses.KEY_RESIZE:
            # Force redraw next tick.
            last_render = 0.0
            continue
        if ch in (ord("q"), ord("Q")):
            break


def run_once(log_path: str, stop_path: str) -> str:
    """Read the log once, build state, render to plain text. No curses."""
    follower = TailFollower(log_path)
    lines = follower.read_new_lines()
    state = build_state_from_lines(lines)
    width = max(80, _terminal_width())
    stop_present = os.path.exists(stop_path)
    rendered = build_render_lines(state, width, stop_present=stop_present)
    return "\n".join(text for text, _ in rendered)


def _terminal_width(default: int = 120) -> int:
    try:
        return os.get_terminal_size().columns
    except (OSError, ValueError):
        return default


# --- Entry point ------------------------------------------------------------


def _install_sigterm_handler() -> None:
    def _handler(signum, frame):
        raise KeyboardInterrupt
    try:
        signal.signal(signal.SIGTERM, _handler)
    except (ValueError, OSError):
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Live curses TUI for the overnight automated-jam loop.",
    )
    parser.add_argument(
        "--log",
        default=DEFAULT_LOG,
        help=f"Path to the JSONL master log (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--stop-file",
        default=DEFAULT_STOP,
        help=f"Path to the HALT sentinel file (default: {DEFAULT_STOP})",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Render one frame to stdout as plain text and exit (no curses).",
    )
    args = parser.parse_args(argv)

    if args.once:
        sys.stdout.write(run_once(args.log, args.stop_file) + "\n")
        return 0

    # Wait for log to appear if it's not there yet.
    if not Path(args.log).exists():
        # Don't fail — start curses and let the follower poll.
        pass

    _install_sigterm_handler()
    try:
        curses.wrapper(_curses_main, args.log, args.stop_file)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
