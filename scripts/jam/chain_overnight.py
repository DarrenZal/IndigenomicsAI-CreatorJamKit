#!/usr/bin/env python3
"""chain_overnight.py — multi-loop chained overnight runs.

Once one overnight_loop completes, this script auto-finalizes its
artifacts (composer + ceremony-artifact for runs where the loop
was launched before those wire-ins existed) and launches the next
run with DIFFERENT settings into a fresh persistent_root.

The point: the substrate explores its own behavior space across
configurations during the operator's sleep. Different
planner-thresholds → different demotion patterns → different
artifact sets → real evidence about which settings work best.

Discipline:
  - Each loop writes to its own persistent_root; the chain script
    NEVER modifies a finished loop's output dir.
  - The chain script is itself launched via nohup + disown so it
    survives the operator's shell exit.
  - If a loop fails to launch, the chain halts soft — prior loops'
    data is preserved.
  - Sentinel-stop: dropping <chain_root>/CHAIN-STOP halts the chain
    between runs (doesn't kill the currently-running loop).

Usage:
  python3 scripts/jam/chain_overnight.py run \\
      --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \\
      --gateway http://localhost:8000 \\
      --chain-root ~/overnight-jam-2026-05-26-chain \\
      --watch-pid 56348 \\
      [--max-loops 3] \\
      [--default-budget-hours 3]

  python3 scripts/jam/chain_overnight.py run --chain-root <dir> \\
      --gateway http://localhost:8000 --kit-root <kit> --immediate

Behavior:
  --watch-pid: wait for this PID to finish (the already-running loop),
    then start chained loops. If PID is already gone, start immediately.
  --immediate: skip watch; start chained loops now (use when no prior
    loop is running).

Configurations cycled for chained loops:
  Loop 2: planner-threshold=3, no DAG, large budget
          (probe what happens when Planner is more lenient)
  Loop 3: planner-threshold=2, DAG mode, focus on L1 dependents
          (probe what happens when foundations have been published)
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(chain_root: Path, kind: str, **fields):
    """Append an event to the chain log."""
    chain_root.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"at": now_iso(), "kind": kind, **fields})
    log_path = chain_root / "chain-log.jsonl"
    with log_path.open("a") as f:
        f.write(line + "\n")
    print(line, flush=True)


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def wait_for_pid(pid: int, poll_seconds: int = 30,
                  chain_root: Optional[Path] = None) -> None:
    """Block until pid is no longer running."""
    if chain_root:
        log(chain_root, "watch_start", watch_pid=pid)
    while is_pid_running(pid):
        time.sleep(poll_seconds)
    if chain_root:
        log(chain_root, "watch_end", watch_pid=pid)


def check_sentinel_stop(chain_root: Path) -> Optional[str]:
    """If <chain_root>/CHAIN-STOP exists, return its contents."""
    p = chain_root / "CHAIN-STOP"
    if p.exists():
        try:
            return p.read_text()[:500] or ""
        except Exception:
            return ""
    return None


# --------------------------------------------------------------------- #
# Auto-finalize an existing persistent_root                             #
# --------------------------------------------------------------------- #

def finalize_persistent_root(
    persistent_root: Path,
    kit_root: Path,
    gateway: str,
    team_key: str,
    chain_root: Path,
) -> None:
    """Run composer + ceremony_artifact against a finished
    persistent_root. Safe to invoke even if the wire-ins already
    auto-ran during loop finish (composer overwrites idempotently,
    ceremony_artifact regenerates).
    """
    if not persistent_root.exists():
        log(chain_root, "finalize_skip",
            reason="persistent_root absent",
            path=str(persistent_root))
        return

    # 1. Composer
    comp_dir = persistent_root / "compositions"
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "agent_composer.py"),
        "compose",
        "--persistent-root", str(persistent_root),
        "--gateway", gateway,
        "--model", "telus-gemma",
        "--out-dir", str(comp_dir),
        "--max-proposals", "8",
    ]
    sub_env = {**os.environ, "TELUS_TEAM_KEY": team_key}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                            env=sub_env, timeout=600)
        log(chain_root, "finalize_composer_done",
            persistent_root=str(persistent_root),
            rc=r.returncode,
            stdout_tail=(r.stdout or "")[-300:])
    except subprocess.TimeoutExpired:
        log(chain_root, "finalize_composer_timeout",
            persistent_root=str(persistent_root))

    # 2. Ceremony artifact
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "ceremony_artifact.py"),
        "weave",
        "--persistent-root", str(persistent_root),
        "--out", str(persistent_root / "ceremony-artifact.md"),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        log(chain_root, "finalize_ceremony_done",
            persistent_root=str(persistent_root),
            rc=r.returncode,
            stdout_tail=(r.stdout or "")[-300:])
    except subprocess.TimeoutExpired:
        log(chain_root, "finalize_ceremony_timeout",
            persistent_root=str(persistent_root))


# --------------------------------------------------------------------- #
# Loop configurations                                                   #
# --------------------------------------------------------------------- #

def loop_configurations(default_budget_hours: float,
                         persistent_root_prefix: Path) -> List[Dict[str, Any]]:
    """Return the loop configs cycled in chained execution.

    Each dict has:
      - label: short string for the config
      - persistent_root: target dir for this loop's artifacts
      - args: list of additional argv for overnight_loop.py run
    """
    return [
        {
            "label": "lenient-no-dag",
            "persistent_root": persistent_root_prefix.with_name(
                persistent_root_prefix.name + "-run2-lenient"
            ),
            "args": [
                "--planner-threshold", "3",
                "--max-rounds", "200",
                "--max-telus-calls", "1200",
                "--time-budget-hours", str(default_budget_hours),
                "--per-round-time-budget-min", "8",
                "--aggregate-every", "5",
                "--inter-round-pause-seconds", "8",
                "--builder-mode", "telus",
                "--mesh-mode", "--planner-mode",
                # No --dag-mode here — see how scheduling differs
            ],
        },
        {
            "label": "dag-strict",
            "persistent_root": persistent_root_prefix.with_name(
                persistent_root_prefix.name + "-run3-dag-strict"
            ),
            "args": [
                "--planner-threshold", "2",
                "--max-rounds", "200",
                "--max-telus-calls", "1200",
                "--time-budget-hours", str(default_budget_hours),
                "--per-round-time-budget-min", "8",
                "--aggregate-every", "5",
                "--inter-round-pause-seconds", "8",
                "--builder-mode", "telus",
                "--mesh-mode", "--planner-mode", "--dag-mode",
            ],
        },
    ]


# --------------------------------------------------------------------- #
# Launch one loop + wait                                                #
# --------------------------------------------------------------------- #

def launch_and_wait(
    config: Dict[str, Any],
    kit_root: Path,
    gateway: str,
    team_key: str,
    chain_root: Path,
) -> int:
    persistent_root = Path(config["persistent_root"]).expanduser()
    persistent_root.mkdir(parents=True, exist_ok=True)
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "overnight_loop.py"), "run",
        "--kit-root", str(kit_root),
        "--gateway", gateway,
        "--persistent-root", str(persistent_root),
        "--models", "telus-qwen,telus-gemma,telus-gpt-oss",
        "--per-round-call-budget", "15",
    ] + config["args"]

    log(chain_root, "loop_launching",
        label=config["label"],
        persistent_root=str(persistent_root),
        cmd_tail=" ".join(cmd[-10:]))

    sub_env = {**os.environ, "TELUS_TEAM_KEY": team_key}
    log_path = persistent_root / "loop.log"
    # Inline launch — block until done. The chain script itself is
    # under nohup, so the chain process owns this subprocess; clean
    # exit propagates.
    with log_path.open("w") as logf:
        proc = subprocess.Popen(
            cmd, env=sub_env, stdout=logf, stderr=subprocess.STDOUT,
        )
        rc = proc.wait()

    log(chain_root, "loop_finished",
        label=config["label"],
        persistent_root=str(persistent_root),
        rc=rc)
    return rc


# --------------------------------------------------------------------- #
# Main                                                                  #
# --------------------------------------------------------------------- #

def cmd_run(args):
    chain_root = Path(args.chain_root).expanduser().resolve()
    kit_root = Path(args.kit_root).expanduser().resolve()
    chain_root.mkdir(parents=True, exist_ok=True)

    team_key = os.environ.get("TELUS_TEAM_KEY")
    if not team_key:
        print("error: TELUS_TEAM_KEY env required", file=sys.stderr)
        sys.exit(2)

    log(chain_root, "chain_start",
        kit_root=str(kit_root), gateway=args.gateway,
        chain_root=str(chain_root),
        watch_pid=args.watch_pid, immediate=args.immediate,
        max_loops=args.max_loops)

    # Step 1: optionally wait for an existing loop to finish
    if not args.immediate and args.watch_pid:
        log(chain_root, "watching", pid=args.watch_pid)
        wait_for_pid(args.watch_pid, poll_seconds=args.poll_seconds,
                      chain_root=chain_root)

    # Step 2: finalize the watched loop's persistent_root (if provided)
    if args.watched_persistent_root:
        watched_root = Path(args.watched_persistent_root).expanduser()
        finalize_persistent_root(
            persistent_root=watched_root,
            kit_root=kit_root,
            gateway=args.gateway,
            team_key=team_key,
            chain_root=chain_root,
        )

    # Step 3: cycle through chained loop configurations
    configs = loop_configurations(
        default_budget_hours=args.default_budget_hours,
        persistent_root_prefix=Path(args.persistent_root_prefix).expanduser(),
    )
    if args.max_loops > 0:
        configs = configs[:args.max_loops]

    for i, config in enumerate(configs):
        # Sentinel check
        stop = check_sentinel_stop(chain_root)
        if stop is not None:
            log(chain_root, "chain_sentinel_stop", reason=stop[:300])
            break

        log(chain_root, "loop_starting_in_chain",
            loop_idx=i + 1, total=len(configs),
            label=config["label"])
        try:
            rc = launch_and_wait(config, kit_root, args.gateway,
                                  team_key, chain_root)
        except Exception as e:
            log(chain_root, "loop_launch_error",
                label=config["label"], error=str(e)[:300])
            continue

        # Finalize this loop's outputs
        finalize_persistent_root(
            persistent_root=Path(config["persistent_root"]).expanduser(),
            kit_root=kit_root,
            gateway=args.gateway,
            team_key=team_key,
            chain_root=chain_root,
        )

    log(chain_root, "chain_done", loops_completed=len(configs))
    print(f"chain log: {chain_root}/chain-log.jsonl")


def main():
    ap = argparse.ArgumentParser(prog="chain_overnight.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    apr = sub.add_parser("run")
    apr.add_argument("--kit-root", required=True)
    apr.add_argument("--gateway", required=True)
    apr.add_argument("--chain-root", required=True,
                     help="dir for chain log + sentinel STOP")
    apr.add_argument("--persistent-root-prefix",
                     default="~/overnight-jam-2026-05-26",
                     help="base path; chained roots derived as "
                          "<prefix>-run2-..., <prefix>-run3-...")
    apr.add_argument("--watch-pid", type=int, default=0,
                     help="wait for this PID to finish before "
                          "launching chain (0 = skip)")
    apr.add_argument("--watched-persistent-root",
                     help="persistent_root of the watched loop; "
                          "finalized after watch ends")
    apr.add_argument("--poll-seconds", type=int, default=30)
    apr.add_argument("--immediate", action="store_true",
                     help="skip --watch-pid even if set")
    apr.add_argument("--max-loops", type=int, default=2,
                     help="max chained loops to run (0 = all configured)")
    apr.add_argument("--default-budget-hours", type=float, default=3.0)
    apr.set_defaults(func=cmd_run)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
