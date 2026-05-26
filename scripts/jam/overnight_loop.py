#!/usr/bin/env python3
"""overnight_loop.py — overnight-loop-v0 driver.

Subprocess-per-round pattern: for each round, invoke orchestrator.py
with --max-specs 1 (one spec, one model), parse run.json, aggregate
to overnight-master-log.jsonl. Cycle through models + specs. Bounded
by time budget OR call budget OR sentinel-stop.

Process boundary per round is intentional — clean resource cleanup,
no in-process state accumulation, easier to interpret partial runs.

Discipline:
  - ALL outputs land in <persistent_root> ONLY (default
    ~/overnight-jam-2026-05-26/). Loop never writes to the kit repo,
    IndigenomicsAI repo, or anywhere else.
  - Loop process never invokes `git`. Commits during the build phase
    are normal operator workflow; the LOOP is the part with the
    "no autonomous commits" rule.
  - Gateway preflight before each round. If gateway is down → halt soft
    (write HALT-GATEWAY, continue checking on retry-interval).
  - Credential regex scan on every TELUS response surfaced via the
    round's output dir + on every generated build_attempt.py. On hit
    → HALT-CREDS + stop loop.
  - Sentinel-stop file at <persistent_root>/STOP → graceful exit.
  - Aggregator runs every N rounds (default 5) to surface patterns.

Usage:
  python3 scripts/jam/overnight_loop.py run \\
      --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \\
      --gateway http://localhost:8000 \\
      --team-key "$DOGFOOD_TEAM_KEY" \\
      --persistent-root ~/overnight-jam-2026-05-26 \\
      --max-rounds 100 \\
      --time-budget-hours 6 \\
      --max-telus-calls 600 \\
      --aggregate-every 5 \\
      --models telus-qwen,telus-gemma,telus-gpt-oss \\
      [--specs spec1,spec2,...]
"""

import argparse
import itertools
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.loop_safety import (  # noqa: E402
    check_gateway_health,
    scan_for_credentials,
    ensure_path_within,
    check_sentinel_stop,
    write_halt,
    write_halt_creds,
)
from jam.orchestrator import ORCHESTRATOR_CANDIDATE_SPECS  # noqa: E402


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_master_log(persistent_root: Path, record: Dict[str, Any]) -> None:
    """Append-only JSONL log of every round + safety event."""
    log_path = persistent_root / "overnight-master-log.jsonl"
    with log_path.open("a") as f:
        f.write(json.dumps(record) + "\n")


# --------------------------------------------------------------------- #
# Round runner                                                          #
# --------------------------------------------------------------------- #

def run_round(
    *,
    round_idx: int,
    kit_root: Path,
    persistent_root: Path,
    gateway: str,
    team_key: str,
    spec_id: str,
    model: str,
    bus_root: Path,
    builder_mode: str,
    mesh_mode: bool,
    wall_root: Path,
    per_round_call_budget: int,
    per_round_time_budget_min: int,
) -> Dict[str, Any]:
    """Invoke orchestrator.py as a subprocess for ONE spec, ONE model.
    Returns a record summarizing the round."""
    round_id = f"round-{round_idx:04d}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
    round_dir = ensure_path_within(
        persistent_root / "rounds" / round_id, persistent_root
    )
    round_dir.mkdir(parents=True, exist_ok=True)

    orchestrator_py = kit_root / "scripts" / "jam" / "orchestrator.py"

    cmd = [
        "python3", str(orchestrator_py), "run",
        "--kit-root", str(kit_root),
        "--gateway", gateway,
        "--team-key", team_key,
        "--models", model,
        "--specs", spec_id,
        "--max-specs", "1",
        "--max-telus-calls", str(per_round_call_budget),
        "--time-budget-min", str(per_round_time_budget_min),
        "--builder-mode", builder_mode,
        "--bus-root", str(bus_root),
        "--out-dir", str(round_dir),
        "--wall-root", str(wall_root),
    ]
    if mesh_mode:
        cmd.append("--mesh-mode")

    started_at = now_iso()
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=per_round_time_budget_min * 60 + 60,
        )
        rc = proc.returncode
        stdout_tail = proc.stdout[-2000:] if proc.stdout else ""
        stderr_tail = proc.stderr[-2000:] if proc.stderr else ""
    except subprocess.TimeoutExpired as e:
        rc = 124
        stdout_tail = (e.stdout or b"").decode("utf-8", errors="replace")[-2000:] \
            if e.stdout else ""
        stderr_tail = "subprocess TIMEOUT"

    elapsed = round(time.time() - t0, 1)

    # Find the latest summary in round_dir
    summary = None
    summary_paths = sorted(round_dir.glob("orchestrator-summary-*.json"))
    if summary_paths:
        try:
            summary = json.loads(summary_paths[-1].read_text())
        except Exception:
            summary = None

    outcome = "unknown"
    telus_calls = 0
    if summary:
        outcome = (
            (summary.get("results") or [{}])[0].get("outcome", "unknown")
            if summary.get("results") else "no-results"
        )
        telus_calls = summary.get("counter", {}).get("telus_calls", 0)

    record = {
        "kind": "round",
        "round_idx": round_idx,
        "round_id": round_id,
        "started_at": started_at,
        "finished_at": now_iso(),
        "elapsed_seconds": elapsed,
        "spec_id": spec_id,
        "model": model,
        "subprocess_returncode": rc,
        "outcome": outcome,
        "telus_calls": telus_calls,
        "round_dir": str(round_dir),
        "stderr_tail": stderr_tail[-500:],
    }
    return record


# --------------------------------------------------------------------- #
# Credential scan over a round's output dir                             #
# --------------------------------------------------------------------- #

CRED_SCAN_FILE_GLOBS = [
    "**/*.md",
    "**/*.json",
    "**/build_attempt.py",
    "**/*.py",
]


def scan_round_for_credentials(round_dir: Path,
                                source_label_prefix: str) -> List[dict]:
    """Walk round_dir for files matching CRED_SCAN_FILE_GLOBS; scan each
    for credential patterns. Returns aggregate hits across files.
    Bounded: skip files > 1 MB (LLM outputs are < 100KB typically).
    """
    all_hits: List[dict] = []
    seen = set()
    for pattern in CRED_SCAN_FILE_GLOBS:
        for f in round_dir.glob(pattern):
            if f in seen:
                continue
            seen.add(f)
            if not f.is_file():
                continue
            try:
                if f.stat().st_size > 1_000_000:
                    continue
                text = f.read_text(errors="replace")
            except Exception:
                continue
            hits = scan_for_credentials(
                text, source_label=f"{source_label_prefix}:{f.name}"
            )
            for h in hits:
                h["file"] = str(f.relative_to(round_dir.parent))
            all_hits.extend(hits)
    return all_hits


# --------------------------------------------------------------------- #
# Aggregator invocation                                                 #
# --------------------------------------------------------------------- #

def invoke_aggregator(
    *,
    kit_root: Path,
    persistent_root: Path,
    wall_root: Path,
    rounds_so_far: int,
) -> Optional[Path]:
    aggregator_py = kit_root / "scripts" / "jam" / "agent_aggregator.py"
    rounds_dir = persistent_root / "rounds"
    if not rounds_dir.exists():
        return None
    out_dir = persistent_root / "aggregator"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"recommendations-after-round-{rounds_so_far:04d}.md"
    cmd = [
        "python3", str(aggregator_py), "aggregate",
        "--rounds-dir", str(rounds_dir),
        "--wall-root", str(wall_root),
        "--out", str(out_path),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"  [aggregator] FAIL rc={r.returncode}: {r.stderr[-300:]}",
                   flush=True)
            return None
        return out_path
    except subprocess.TimeoutExpired:
        print(f"  [aggregator] TIMEOUT", flush=True)
        return None


# --------------------------------------------------------------------- #
# Main loop                                                             #
# --------------------------------------------------------------------- #

def cmd_run(args):
    kit_root = Path(args.kit_root).expanduser().resolve()
    persistent_root = Path(args.persistent_root).expanduser().resolve()
    persistent_root.mkdir(parents=True, exist_ok=True)

    # Verify kit_root looks like the kit
    if not (kit_root / "scripts" / "jam" / "orchestrator.py").exists():
        print(f"error: kit_root does not contain expected orchestrator.py: {kit_root}",
               file=sys.stderr)
        sys.exit(2)

    # Pre-flight: gateway health
    ok, reason = check_gateway_health(args.gateway, timeout=10)
    if not ok:
        msg = f"gateway preflight failed at startup: {reason}"
        print(f"error: {msg}", file=sys.stderr)
        write_halt(persistent_root, "GATEWAY", {"reason": reason,
                                                   "stage": "startup"})
        sys.exit(2)

    # Sanity: no stale HALT files
    stale_halts = list(persistent_root.glob("HALT-*.txt"))
    if stale_halts and not args.ignore_stale_halts:
        print(f"error: stale HALT files exist in {persistent_root}:",
               file=sys.stderr)
        for p in stale_halts:
            print(f"  {p.name}", file=sys.stderr)
        print("Remove them or pass --ignore-stale-halts to continue.",
               file=sys.stderr)
        sys.exit(2)

    # Sentinel: don't start if one is already set
    stop = check_sentinel_stop(persistent_root)
    if stop is not None:
        print(f"error: sentinel STOP already present: {stop[:80]}",
               file=sys.stderr)
        sys.exit(2)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        print("error: --models must be non-empty", file=sys.stderr)
        sys.exit(2)
    specs = (
        [s.strip() for s in args.specs.split(",") if s.strip()]
        if args.specs else list(ORCHESTRATOR_CANDIDATE_SPECS)
    )
    if not specs:
        print("error: no specs to run", file=sys.stderr)
        sys.exit(2)

    bus_root = persistent_root / "bus"
    wall_root = ensure_path_within(persistent_root / "wall", persistent_root)
    wall_root.mkdir(parents=True, exist_ok=True)

    start_time = time.time()
    deadline = start_time + args.time_budget_hours * 3600
    cumulative_telus = 0

    pairs = list(itertools.product(specs, models))
    cycle = itertools.cycle(pairs)

    start_record = {
        "kind": "loop_start",
        "started_at": now_iso(),
        "kit_root": str(kit_root),
        "persistent_root": str(persistent_root),
        "gateway": args.gateway,
        "models": models,
        "specs": specs,
        "max_rounds": args.max_rounds,
        "time_budget_hours": args.time_budget_hours,
        "max_telus_calls": args.max_telus_calls,
        "aggregate_every": args.aggregate_every,
        "builder_mode": args.builder_mode,
        "mesh_mode": args.mesh_mode,
    }
    append_master_log(persistent_root, start_record)

    print(f"=== overnight-loop-v0 starting ===", flush=True)
    print(f"  persistent_root: {persistent_root}")
    print(f"  models: {models}")
    print(f"  specs: {len(specs)} ({specs[:3]}{'...' if len(specs) > 3 else ''})")
    print(f"  time budget: {args.time_budget_hours} hr")
    print(f"  call budget: {args.max_telus_calls}")
    print(f"  aggregate every: {args.aggregate_every} round(s)")
    print(f"  builder_mode: {args.builder_mode}")
    print(f"  mesh_mode: {args.mesh_mode}")
    print()

    round_idx = 0
    rounds_completed = 0
    halt_reason = None

    try:
        while True:
            round_idx += 1
            if round_idx > args.max_rounds:
                halt_reason = f"max_rounds reached ({args.max_rounds})"
                break
            if time.time() >= deadline:
                halt_reason = f"time budget exceeded ({args.time_budget_hours} hr)"
                break
            if cumulative_telus >= args.max_telus_calls:
                halt_reason = (f"call budget exceeded "
                               f"({cumulative_telus} >= {args.max_telus_calls})")
                break

            # Sentinel check
            stop = check_sentinel_stop(persistent_root)
            if stop is not None:
                halt_reason = f"sentinel STOP: {stop[:120]}"
                break

            # Gateway preflight per round
            ok, reason = check_gateway_health(args.gateway, timeout=10)
            if not ok:
                # Soft halt: wait + retry
                print(f"  [round {round_idx}] gateway down: {reason}; "
                      f"retrying in {args.gateway_retry_seconds}s",
                      flush=True)
                append_master_log(persistent_root, {
                    "kind": "gateway_unhealthy",
                    "at": now_iso(),
                    "round_idx": round_idx,
                    "reason": reason,
                })
                time.sleep(args.gateway_retry_seconds)
                round_idx -= 1  # don't count this as a round
                continue

            spec_id, model = next(cycle)

            print(f"\n[round {round_idx:04d}] spec={spec_id} model={model} "
                  f"cumulative_calls={cumulative_telus}", flush=True)

            try:
                record = run_round(
                    round_idx=round_idx,
                    kit_root=kit_root,
                    persistent_root=persistent_root,
                    gateway=args.gateway,
                    team_key=args.team_key,
                    spec_id=spec_id,
                    model=model,
                    bus_root=bus_root,
                    builder_mode=args.builder_mode,
                    mesh_mode=args.mesh_mode,
                    wall_root=wall_root,
                    per_round_call_budget=args.per_round_call_budget,
                    per_round_time_budget_min=args.per_round_time_budget_min,
                )
            except PermissionError as e:
                # Write-boundary violation — halt hard
                halt_reason = f"write-boundary: {e}"
                write_halt(persistent_root, "BOUNDARY", {"error": str(e)})
                break
            except Exception as e:
                record = {
                    "kind": "round",
                    "round_idx": round_idx,
                    "spec_id": spec_id,
                    "model": model,
                    "subprocess_returncode": -1,
                    "outcome": "loop-error",
                    "telus_calls": 0,
                    "started_at": now_iso(),
                    "finished_at": now_iso(),
                    "elapsed_seconds": 0,
                    "stderr_tail": str(e)[:500],
                }

            append_master_log(persistent_root, record)
            rounds_completed += 1
            cumulative_telus += record.get("telus_calls", 0)
            print(f"  → outcome={record['outcome']} "
                  f"telus_calls={record['telus_calls']} "
                  f"elapsed={record['elapsed_seconds']}s "
                  f"rc={record['subprocess_returncode']}",
                  flush=True)

            # Credential scan over the round's output
            round_dir = Path(record["round_dir"])
            hits = scan_round_for_credentials(
                round_dir, source_label_prefix=f"round-{round_idx:04d}"
            )
            if hits:
                halt_reason = (f"credential scan hit: {len(hits)} pattern "
                               f"match(es) in round {round_idx}")
                halt_path = write_halt_creds(
                    persistent_root, hits,
                    source_label=f"round-{round_idx:04d}",
                )
                append_master_log(persistent_root, {
                    "kind": "halt_creds",
                    "at": now_iso(),
                    "round_idx": round_idx,
                    "hit_count": len(hits),
                    "halt_path": str(halt_path),
                })
                break

            # Aggregator invocation every N rounds
            if (args.aggregate_every > 0 and
                    round_idx % args.aggregate_every == 0):
                agg_path = invoke_aggregator(
                    kit_root=kit_root,
                    persistent_root=persistent_root,
                    wall_root=wall_root,
                    rounds_so_far=round_idx,
                )
                if agg_path:
                    print(f"  [aggregator] {agg_path}", flush=True)
                    append_master_log(persistent_root, {
                        "kind": "aggregator",
                        "at": now_iso(),
                        "round_idx": round_idx,
                        "path": str(agg_path),
                    })

            # Brief pause between rounds (prevents pathological tight loops
            # if the orchestrator subprocess returns instantly)
            time.sleep(args.inter_round_pause_seconds)

    except KeyboardInterrupt:
        halt_reason = "KeyboardInterrupt"

    if halt_reason is None:
        halt_reason = "loop exited normally"

    finish_record = {
        "kind": "loop_finish",
        "finished_at": now_iso(),
        "halt_reason": halt_reason,
        "rounds_completed": rounds_completed,
        "wall_seconds": round(time.time() - start_time, 1),
        "cumulative_telus_calls": cumulative_telus,
    }
    append_master_log(persistent_root, finish_record)

    # Final aggregator pass
    final_agg = invoke_aggregator(
        kit_root=kit_root,
        persistent_root=persistent_root,
        wall_root=wall_root,
        rounds_so_far=rounds_completed,
    )

    print()
    print(f"=== overnight-loop-v0 finished ===")
    print(f"  halt reason: {halt_reason}")
    print(f"  rounds completed: {finish_record['rounds_completed']}")
    print(f"  wall time: {finish_record['wall_seconds']}s")
    print(f"  cumulative telus calls: {cumulative_telus}")
    if final_agg:
        print(f"  final aggregator: {final_agg}")


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(prog="overnight_loop.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_run = sub.add_parser("run", help="run the overnight loop")
    ap_run.add_argument("--kit-root", required=True)
    ap_run.add_argument("--gateway", required=True)
    ap_run.add_argument("--team-key", required=True)
    ap_run.add_argument("--persistent-root", required=True,
                          help="ALL writes land here; loop never writes "
                               "outside this dir")
    ap_run.add_argument("--models",
                          default="telus-qwen,telus-gemma,telus-gpt-oss")
    ap_run.add_argument("--specs",
                          help="comma-separated; default: orchestrator "
                               "candidate list")
    ap_run.add_argument("--max-rounds", type=int, default=100)
    ap_run.add_argument("--time-budget-hours", type=float, default=6.0)
    ap_run.add_argument("--max-telus-calls", type=int, default=600)
    ap_run.add_argument("--per-round-call-budget", type=int, default=20)
    ap_run.add_argument("--per-round-time-budget-min", type=int, default=8)
    ap_run.add_argument("--aggregate-every", type=int, default=5,
                          help="invoke aggregator every N rounds; 0 = "
                               "only at end")
    ap_run.add_argument("--builder-mode", choices=["queue", "telus", "skip"],
                          default="telus")
    ap_run.add_argument("--mesh-mode", action="store_true", default=True,
                          help="enable mesh-mode (Reviewer between draft "
                               "and publish); default on for overnight")
    ap_run.add_argument("--no-mesh-mode", action="store_false",
                          dest="mesh_mode",
                          help="disable mesh-mode (Reviewer skipped)")
    ap_run.add_argument("--gateway-retry-seconds", type=int, default=30,
                          help="wait + retry on gateway preflight failure")
    ap_run.add_argument("--inter-round-pause-seconds", type=float, default=2.0)
    ap_run.add_argument("--ignore-stale-halts", action="store_true",
                          help="proceed even if HALT-*.txt files are "
                               "present in persistent_root")
    ap_run.set_defaults(func=cmd_run)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
