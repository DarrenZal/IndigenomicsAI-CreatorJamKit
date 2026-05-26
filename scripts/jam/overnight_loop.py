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
from jam.agent_planner import (  # noqa: E402
    Planner,
    read_spec_dependencies,
    topological_levels,
)


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

    # NOTE: team_key passed ONLY via env (TELUS_TEAM_KEY) to avoid argv
    # leak (Codex A1). The subprocess reads os.environ for the key.
    cmd = [
        "python3", str(orchestrator_py), "run",
        "--kit-root", str(kit_root),
        "--gateway", gateway,
        "--models", model,
        "--specs", spec_id,
        "--max-specs", "1",
        "--max-telus-calls", str(per_round_call_budget),
        "--time-budget-min", str(per_round_time_budget_min),
        "--builder-mode", builder_mode,
        "--bus-root", str(bus_root),
        "--out-dir", str(round_dir),
        "--wall-root", str(wall_root),
        "--allowed-root", str(persistent_root),
    ]
    if mesh_mode:
        cmd.append("--mesh-mode")

    sub_env = {**os.environ, "TELUS_TEAM_KEY": team_key}

    started_at = now_iso()
    t0 = time.time()
    rc = -1
    stderr_tail = ""
    # Use Popen so we can SIGKILL after timeout (Codex E1). subprocess.run
    # only sends SIGTERM and may leave the orchestrator lingering.
    proc = subprocess.Popen(
        cmd, env=sub_env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = proc.communicate(
            timeout=per_round_time_budget_min * 60 + 60,
        )
        rc = proc.returncode
        stderr_tail = (stderr_b or b"").decode("utf-8", errors="replace")[-2000:]
    except subprocess.TimeoutExpired:
        # SIGTERM then SIGKILL — guarantee the subprocess is gone.
        proc.terminate()
        try:
            stdout_b, stderr_b = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                stdout_b, stderr_b = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                stdout_b, stderr_b = b"", b""
        rc = 124
        stderr_tail = "subprocess TIMEOUT (sent SIGTERM, then SIGKILL)"

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

    # Codex E1: when subprocess timed out, conservatively charge the
    # full per-round call budget so the loop's cumulative-call cap is
    # not undercounted into overshoot territory.
    if rc == 124 and telus_calls == 0:
        telus_calls = per_round_call_budget
        outcome = "subprocess-timeout"

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

    # --dag-mode implies --planner-mode (DAG scheduling lives inside Planner)
    if getattr(args, "dag_mode", False):
        args.planner_mode = True

    # --archive-prior-run: move prior-run artifacts to _archive-<ts>/
    # BEFORE the stale-HALT check, so a prior failed run doesn't block
    # this launch.
    if getattr(args, "archive_prior_run", False):
        import shutil
        from datetime import datetime as _dt
        ts = _dt.now().strftime("%Y%m%dT%H%M%S")
        archive_dir = persistent_root / f"_archive-{ts}"
        moved = []
        # Move standard prior-run directories + files
        # Note: loop.log is intentionally NOT in this list — when the
        # operator launches via `nohup ... > loop.log 2>&1 &`, shell
        # creates loop.log BEFORE the python process starts; moving it
        # here would leave the file descriptor pointing at the archive
        # location (silent monitoring breakage).
        for name in ("rounds", "wall", "bus", "aggregator",
                       "planner-events.json", "overnight-master-log.jsonl",
                       "closing-witness-readout.md",
                       "coherence-synthesis.md",
                       "STOP", "STOP.txt"):
            src = persistent_root / name
            if src.exists():
                if not moved:
                    archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(archive_dir / name))
                moved.append(name)
        # Also move any HALT-* tombstones
        for halt in list(persistent_root.glob("HALT-*.txt")):
            if not moved:
                archive_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(halt), str(archive_dir / halt.name))
            moved.append(halt.name)
        if moved:
            print(f"  archived prior-run artifacts to {archive_dir}: "
                  f"{', '.join(moved)}")

    # Verify kit_root looks like the kit
    if not (kit_root / "scripts" / "jam" / "orchestrator.py").exists():
        print(f"error: kit_root does not contain expected orchestrator.py: {kit_root}",
               file=sys.stderr)
        sys.exit(2)

    # Team-key resolution: env var preferred. argv falls back; warn if used.
    team_key = os.environ.get("TELUS_TEAM_KEY") or args.team_key
    if not team_key:
        print("error: team key required via TELUS_TEAM_KEY env (preferred) "
              "or --team-key", file=sys.stderr)
        sys.exit(2)
    if args.team_key and not os.environ.get("TELUS_TEAM_KEY"):
        print("WARNING: --team-key on argv exposes key via /proc; "
              "prefer 'export TELUS_TEAM_KEY=...'", file=sys.stderr)
    args.team_key = team_key

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

    # Planner: optionally use the adaptive scheduler. When --no-planner
    # (or --planner-mode off), fall back to dumb round-robin via
    # itertools.cycle. When enabled, Planner demotes pairs after K
    # consecutive non-publish outcomes + consumes aggregator
    # recommendations to demote globally.
    pairs = list(itertools.product(specs, models))
    cycle = itertools.cycle(pairs)
    planner: Optional[Planner] = None
    if getattr(args, "planner_mode", False):
        # If --dag-mode, read spec depends_on from frontmatter and
        # pass the DAG to Planner so the scheduler waits for deps to
        # publish before attempting downstream specs.
        dag_deps = None
        if getattr(args, "dag_mode", False):
            specs_root = kit_root / "specs"
            dag_deps = read_spec_dependencies(specs_root, specs)
            levels = topological_levels(dag_deps)
            print(f"  DAG topological levels:")
            for i, lv in enumerate(levels):
                print(f"    L{i}: {len(lv)} spec(s) — {lv}")
        planner = Planner(
            specs=specs,
            models=models,
            consecutive_threshold=args.planner_threshold,
            dag_deps=dag_deps,
        )

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

            if planner is not None:
                pair = planner.next_pair()
                if pair is None:
                    halt_reason = ("planner has no active (spec, model) "
                                   "pairs remaining — all demoted")
                    break
                spec_id, model = pair
            else:
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
                # Codex A2: include round_dir fallback so the credential
                # scan below doesn't KeyError. The error dir is created
                # so the scan finds an empty dir (no hits).
                error_dir = ensure_path_within(
                    persistent_root / "rounds" /
                    f"round-{round_idx:04d}-error",
                    persistent_root,
                )
                error_dir.mkdir(parents=True, exist_ok=True)
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
                    "round_dir": str(error_dir),
                    "stderr_tail": str(e)[:500],
                }

            append_master_log(persistent_root, record)
            rounds_completed += 1
            cumulative_telus += record.get("telus_calls", 0)

            # Feed the round outcome to the Planner so it can demote
            # pairs after K consecutive non-publishes.
            if planner is not None:
                planner.update(record)
                # Surface demotion events to the master log
                if planner.events:
                    last_event = planner.events[-1]
                    if last_event.get("event") == "pair_demoted":
                        append_master_log(persistent_root, {
                            "kind": "planner_pair_demoted",
                            "at": now_iso(),
                            "round_idx": round_idx,
                            **{k: v for k, v in last_event.items()
                                if k not in ("demoted_pairs", "demoted_specs",
                                              "demoted_models")},
                        })
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
                    # Planner-P2: consume aggregator output for
                    # machine-actionable demotions.
                    if planner is not None:
                        try:
                            recs_text = agg_path.read_text()
                            n_actions = planner.consume_aggregator(recs_text)
                            if n_actions > 0:
                                append_master_log(persistent_root, {
                                    "kind": "planner_aggregator_consumed",
                                    "at": now_iso(),
                                    "round_idx": round_idx,
                                    "actions_applied": n_actions,
                                    "status": planner.status(),
                                })
                                print(f"  [planner] consumed {n_actions} "
                                      f"aggregator rec(s); status: "
                                      f"{planner.status()['pairs_active']} "
                                      f"active pairs", flush=True)
                        except Exception as e:
                            print(f"  [planner] aggregator-consume "
                                  f"failed: {e}", flush=True)

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
    if planner is not None:
        ps = planner.status()
        print(f"  planner: {ps['pairs_active']}/{ps['pairs_total']} pairs "
              f"active; {ps['pairs_demoted']} pair(s) demoted, "
              f"{ps['specs_demoted']} spec(s) demoted, "
              f"{ps['models_demoted']} model(s) demoted")
        # Persist final planner audit log
        planner_log = persistent_root / "planner-events.json"
        planner_log.write_text(json.dumps({
            "final_status": ps,
            "events": planner.events,
        }, indent=2))

    # Generate the closing-witness-readout markdown — the kit's
    # canonical closing-ceremony artifact, populated from this run.
    try:
        from jam.closing_readout import render_readout
        readout_md = render_readout(persistent_root)
        readout_path = persistent_root / "closing-witness-readout.md"
        readout_path.write_text(readout_md)
        print(f"  closing readout: {readout_path}")
    except Exception as e:
        print(f"  closing readout: FAIL — {e}")

    # Generate the coherence-synthesis markdown — cross-spec synthesis
    # across the published wall records. This calls TELUS one more time
    # (post-loop, single call) so it's bounded.
    try:
        from jam.coherence_synthesizer import synthesize
        synth_path = persistent_root / "coherence-synthesis.md"
        synth_md = synthesize(
            persistent_root=persistent_root,
            gateway=args.gateway,
            team_key=team_key,
            model="telus-gemma",  # Gemma was the most reliable publisher
        )
        synth_path.write_text(synth_md)
        print(f"  coherence synthesis: {synth_path}")
    except ImportError:
        # Module not present yet; soft-skip
        pass
    except Exception as e:
        print(f"  coherence synthesis: FAIL — {e}")

    # Generate composition proposals — cross-spec composition primitives
    # that propose new specs composing the published ones. Bounded to
    # max-proposals to avoid combinatorial explosion.
    try:
        from jam.agent_composer import compose as _compose
        comp_dir = persistent_root / "compositions"
        comp_summary = _compose(
            persistent_root=persistent_root,
            gateway=args.gateway,
            team_key=team_key,
            model="telus-gemma",
            out_dir=comp_dir,
            max_proposals=8,
        )
        print(f"  compositions: {comp_dir} — "
              f"{comp_summary.get('proposals_attempted', 0)} proposal(s) "
              f"across {comp_summary.get('components_found', 0)} components")
    except ImportError:
        pass
    except Exception as e:
        print(f"  compositions: FAIL — {e}")

    # Weave the layered artifacts into one ceremony document.
    # No new LLM calls — pure markdown composition.
    try:
        from jam.ceremony_artifact import weave_artifact
        artifact_path = persistent_root / "ceremony-artifact.md"
        artifact_path.write_text(weave_artifact(persistent_root))
        print(f"  ceremony artifact: {artifact_path}")
    except ImportError:
        pass
    except Exception as e:
        print(f"  ceremony artifact: FAIL — {e}")


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(prog="overnight_loop.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_run = sub.add_parser("run", help="run the overnight loop")
    ap_run.add_argument("--kit-root", required=True)
    ap_run.add_argument("--gateway", required=True)
    ap_run.add_argument("--team-key", default=None,
                          help="STRONGLY PREFER env var TELUS_TEAM_KEY. "
                               "Passing on argv exposes the key via "
                               "/proc/<pid>/cmdline for the loop's "
                               "lifetime (6+ hours unattended).")
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
    ap_run.add_argument("--planner-mode", action="store_true",
                          default=False,
                          help="enable adaptive scheduling: demote "
                               "(spec, model) pairs after K consecutive "
                               "non-publish outcomes; consume aggregator "
                               "recommendations to demote globally")
    ap_run.add_argument("--planner-threshold", type=int, default=2,
                          help="consecutive non-publish count before "
                               "Planner demotes a pair (default 2; bump "
                               "to 3 for noisier model fleets)")
    ap_run.add_argument("--dag-mode", action="store_true", default=False,
                          help="enable DAG-aware scheduling: reads "
                               "depends_on: from spec frontmatter; "
                               "downstream specs only attempted after "
                               "their deps have published. Implies "
                               "--planner-mode.")
    ap_run.add_argument("--archive-prior-run", action="store_true",
                          default=False,
                          help="if persistent_root has prior-run "
                               "artifacts (rounds/, wall/, etc.), move "
                               "them to <persistent_root>/_archive-<ts>/ "
                               "before starting. Eliminates the manual "
                               "mv step at launch time.")
    ap_run.set_defaults(func=cmd_run)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
