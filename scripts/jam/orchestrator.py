#!/usr/bin/env python3
"""orchestrator.py — autonomous spec-execution network for the Creator Jam.

Given the kit's spec menu, picks N candidate specs, runs each through the
full chain (offering → drafting-loop → manual build → witness-draft →
publish), and respects refusals at every step.

Architecture:

  spec menu (specs/README.md)
        │
        ▼
   refusal-gatekeeper (this script)
        │   ┌─ if cultural/Nation-specific framing detected → REFUSE
        │   └─ else proceed
        ▼
   participant-simulator (TELUS via gateway)
        │   produces a participant-shape offering for the spec
        ▼
   spec_drafting_loop (TELUS via gateway)
        │   produces frozen agentic-build-packet-v0.json OR refusal
        ▼
   builder (NOT run automatically — orchestrator emits a build prompt
            for a human/subagent to execute; orchestrator records the
            outcome the human/subagent reports)
        ▼
   draft_witness (TELUS via gateway)
        │   produces witness-record-draft.md
        ▼
   witness validator (existing tool)
        │   gates publication
        ▼
   witness_append (--confirm-publish) → wall

Refusal as first-class outcome at every step. Every step also emits a
witness_observe message to the bus so the cross-team coordination
layer can see what's happening.

For v0.1 orchestrator, the BUILDER step is run by Claude Code
subagents OR by the operator manually. The orchestrator emits a
"build prompt" file containing the build packet + instructions for
the builder; the builder produces a CLI; the orchestrator picks it up
and continues. This keeps the orchestrator focused on the
TELUS-reasoning + composition layer while letting the most-capable
code-gen model (which may be Claude in subagent or TELUS in v0.2)
do the build.

v0.1 ships ONLY the orchestration layer + the refusal gatekeeper +
the autonomous TELUS calls. Builder integration is via a "build
queue" directory the orchestrator writes to; builders watch the queue
+ append their results.

Discipline:
  - Honor every refusal. No retry-past-rejection.
  - Cultural/Nation-specific content → auto-refuse-by-design.
  - Budget caps (TELUS calls, time).
  - "Doesn't fit yet" is success.
  - Append-only run log.
  - Every step posts witness_observe to bus.

Usage:
  python3 scripts/jam/orchestrator.py run \\
      --kit-root ~/projects/IndigenomicsAI-CreatorJamKit \\
      --gateway http://localhost:8000 --team-key <key> \\
      --models telus-qwen,telus-gemma,telus-gpt-oss \\
      --max-specs 5 \\
      --max-telus-calls 60 \\
      --time-budget-min 60 \\
      --bus-root /tmp/orchestrator-bus \\
      --out-dir /tmp/orchestrator-runs

  python3 scripts/jam/orchestrator.py report <out-dir>
"""

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Make sibling modules importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam import bus  # noqa: E402
from jam.spec_drafting_loop import GatewayModelAdapter  # noqa: E402
from jam.telus_builder import build_from_packet  # noqa: E402
from jam.agent_reviewer import review as reviewer_review  # noqa: E402


# --------------------------------------------------------------------- #
# Refusal gatekeeper                                                    #
# --------------------------------------------------------------------- #

# Words that, if present in a spec body, trigger auto-refuse-by-design.
# These are spec-body terms that signal cultural/Nation-specific content
# requiring explicit authorization the orchestrator does not have.
CULTURAL_GATEKEEPER_TERMS = [
    "cultural authorization",
    "carol anne",
    "carol-anne",
    "ahousaht",
    "hesquiaht",
    "tla-o-qui-aht",
    "nuu-chah-nulth",
    "indigenous data sovereignty",
    "nation-specific",
    "nation authority",
    "elder",
    "ceremonial",
    "traditional knowledge",
    "ocap",
    "fpic",
    "potlatch",
    "longhouse",
]


def refusal_gatekeeper(spec_path: Path) -> Optional[str]:
    """Return None if the spec is safe to attempt autonomously, OR a
    refusal reason string if not.

    Conservative-by-design: ANY match against the cultural gatekeeper
    list refuses. False-positives (e.g., a spec that quotes the kit's
    discipline on these terms in its Refusal Boundaries section)
    err toward refusal — the operator can manually override.
    """
    if not spec_path.exists():
        return f"spec file not found: {spec_path}"
    body = spec_path.read_text().lower()
    for term in CULTURAL_GATEKEEPER_TERMS:
        if term in body:
            # Be specific: name the term so the operator can decide
            return f"cultural-content-gatekeeper hit on term: {term!r}"
    # Also check the Refusal Boundaries section for "do not use this for X"
    # patterns that would conflict with autonomous execution
    return None


# --------------------------------------------------------------------- #
# Spec menu                                                             #
# --------------------------------------------------------------------- #

# Specs we will attempt (preflighted-clean per kit menu, excluding those
# we've already built tonight + culturally-gated).
ORCHESTRATOR_CANDIDATE_SPECS = [
    # L0 foundation specs (no depends_on)
    "witness-record-interop-profile",
    "commitment-pool-route-diagnostic",
    "dream-to-fulfillment-board",
    "flow-funding-frontier-map",
    "bioregional-mapping-layer-board",
    "sensor-to-receipt-pipeline",
    "untracked-allocation-ledger",
    "risk-insurance-coherence-map",
    # L1 dependent specs (depends_on declared in frontmatter)
    "claims-evidence-coherence-report",
    "receipt-wall-story-gallery",
    "spec-composer-bundle-board",
    "living-atlas-coherence-packet",
    "bioregional-insights-briefing",
]


# --------------------------------------------------------------------- #
# Offering generation (TELUS via gateway)                               #
# --------------------------------------------------------------------- #

OFFERING_GENERATOR_SYSTEM = (
    "You are simulating an IndigenomicsAI Creator Jam participant team. "
    "Given a spec from the jam menu, generate a participant-shape "
    "offering — a markdown document that frames what your team is "
    "bringing, what you'd like to see exist, and what boundaries you "
    "want on the build.\n\n"
    "OUTPUT FORMAT — STRICT: Reply with ONLY the markdown content, no "
    "explanation, no fence. Include YAML frontmatter at the top with "
    "title + contributor fields.\n\n"
    "DISCIPLINE:\n"
    "- Use Salish-Sea ecological framings only (kelp, salmon, "
    "herring, eelgrass, sea-otter, etc.) — NO Indigenous-cultural "
    "content.\n"
    "- 100-200 words.\n"
    "- Frame as a real team's voice (we / our / etc.)\n"
    "- Include what the team explicitly does NOT want the tool to do.\n"
)


def generate_offering(adapter, spec_path: Path, spec_id: str) -> str:
    """Use TELUS to generate a participant-shape offering for a spec."""
    spec_body = spec_path.read_text()[:2000]  # first 2KB
    payload = {
        "spec_id": spec_id,
        "spec_excerpt": spec_body,
    }
    # Direct chat-completion call (not via the existing adapter prompts).
    # We need a one-off custom system message.
    import urllib.request
    body = json.dumps({
        "model": adapter.model,
        "messages": [
            {"role": "system", "content": OFFERING_GENERATOR_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "temperature": 0.4,  # slightly higher for variety
    }).encode()
    req = urllib.request.Request(
        f"{adapter.base_url}/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {adapter.team_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    content = data["choices"][0]["message"]["content"]
    # Strip code fences if present
    content = re.sub(r"^```(?:markdown|md)?\s*\n?", "", content.strip())
    content = re.sub(r"\n?```\s*$", "", content)
    return content


# --------------------------------------------------------------------- #
# Builder queue                                                         #
# --------------------------------------------------------------------- #

def emit_build_queue_entry(build_queue_dir: Path, spec_id: str,
                            run_id: str, packet_path: Path,
                            offering: str) -> Path:
    """Write a build queue entry that a builder (subagent or operator)
    can pick up. The queue is just a directory of JSON files."""
    build_queue_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "spec_id": spec_id,
        "run_id": run_id,
        "packet_path": str(packet_path),
        "offering": offering,
        "queued_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }
    entry_path = build_queue_dir / f"{spec_id}-{run_id}.json"
    entry_path.write_text(json.dumps(entry, indent=2))
    return entry_path


def check_build_result(build_queue_dir: Path, spec_id: str,
                        run_id: str) -> Optional[Dict[str, Any]]:
    """Check if a builder has reported a result for this entry.
    Result file: <spec_id>-<run_id>-result.json with:
        {"finding": built-clean|fixed|...,
         "build_artifact_path": ..., "test_outcomes": ...}"""
    result_path = build_queue_dir / f"{spec_id}-{run_id}-result.json"
    if result_path.exists():
        return json.loads(result_path.read_text())
    return None


# --------------------------------------------------------------------- #
# Bus posting helpers                                                   #
# --------------------------------------------------------------------- #

def post_witness_observe(bus_root: Path, team_id: str, observed_kind: str,
                          body: str, source_messages: List[str] = None):
    """Post a witness_observe to the orchestrator's bus."""
    try:
        bus.init_bus(bus_root)
        msg = bus.make_envelope(team_id, team_id, "witness_observe",
                                  from_role="other")
        msg["payload"] = {
            "observed": {"kind": observed_kind, "body": body[:500]},
            "not_an_authority_claim": True,
            "attribution": {
                "agent_role": "orchestrator",
                "source_messages": source_messages or [],
            },
            "routing": "operator",
        }
        bus.append_message(bus_root, msg)
        return msg["message_id"]
    except Exception as e:
        # Don't let bus failures crash orchestrator — log and continue
        print(f"  (bus post failed: {e})", file=sys.stderr)
        return None


# --------------------------------------------------------------------- #
# Per-spec attempt pipeline                                             #
# --------------------------------------------------------------------- #

def attempt_spec(
    spec_id: str,
    kit_root: Path,
    out_dir: Path,
    bus_root: Path,
    gateway: str,
    team_key: str,
    model: str,
    counter: Dict[str, int],
    build_queue_dir: Path,
    builder_wait_seconds: int = 0,
    builder_mode: str = "queue",
    mesh_mode: bool = False,
    wall_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Run the full chain for one spec. Returns a structured result.

    `counter` is mutated to track TELUS calls + time across the orchestrator
    run.
    """
    run_id = f"{spec_id}-{datetime.now(timezone.utc).strftime('%H%M%S')}-{uuid.uuid4().hex[:4]}"
    run_dir = out_dir / spec_id / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "spec_id": spec_id,
        "run_id": run_id,
        "model": model,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": [],
        "outcome": None,
    }

    def log(stage, status, **extra):
        entry = {
            "stage": stage,
            "status": status,
            "at": datetime.now(timezone.utc).isoformat(),
            **extra,
        }
        result["stages"].append(entry)
        print(f"  [{spec_id}] {stage}: {status}", flush=True)

    # ---------- Stage 1: refusal-gatekeeper ----------
    spec_path = kit_root / "specs" / f"{spec_id}.md"
    refusal_reason = refusal_gatekeeper(spec_path)
    if refusal_reason is not None:
        log("1-gatekeeper", "REFUSE", reason=refusal_reason)
        result["outcome"] = "refused-by-gatekeeper"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        post_witness_observe(bus_root, f"orchestrator-{spec_id}",
                              "boundary_crossed",
                              f"Refusal gatekeeper: {refusal_reason}")
        return result
    log("1-gatekeeper", "ok")

    # ---------- Stage 2: offering generation ----------
    adapter = GatewayModelAdapter(gateway, team_key, model=model)
    try:
        offering_md = generate_offering(adapter, spec_path, spec_id)
        counter["telus_calls"] += 1
        offering_path = run_dir / "1-offering.md"
        offering_path.write_text(offering_md)
        log("2-offering", "ok", path=str(offering_path),
            length=len(offering_md))
    except Exception as e:
        log("2-offering", "FAIL", error=str(e))
        result["outcome"] = f"offering-generation-failed: {e}"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        return result

    # ---------- Stage 3: drafting loop ----------
    drafting_out = run_dir / "drafting"
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "spec_drafting_loop.py"),
        "run",
        str(offering_path),
        "--model-source", "gateway",
        "--gateway", gateway,
        "--model", model,
        "--confirm-freeze",
        "--team-name", f"Orchestrator-{spec_id}",
        "--team-site", "other",
        "--out-dir", str(drafting_out),
    ]
    # Pass team_key via env to avoid argv leak (Codex A1).
    sub_env = {**os.environ, "TELUS_TEAM_KEY": team_key}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                            env=sub_env)
        counter["telus_calls"] += 3  # estimate: spec-drafter + boundary-checker (and sometimes composition)
    except subprocess.TimeoutExpired:
        log("3-drafting", "TIMEOUT")
        result["outcome"] = "drafting-timeout"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        return result

    # Check if stage-2 produced a model-refusal (sharpened prompt produces
    # {"refusal": "..."} when the offering carries cultural-style framing).
    # Look at the latest 2-draft-spec.json in the drafting output tree.
    model_refusal_reason = None
    for p in drafting_out.rglob("2-draft-spec.json"):
        try:
            stage2 = json.loads(p.read_text())
            raw = stage2.get("raw_content", "")
            # JSON-parse + check for refusal key
            try:
                cleaned = re.sub(r"^```(?:json)?\s*\n?", "", raw.strip())
                cleaned = re.sub(r"\n?```\s*$", "", cleaned)
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict) and "refusal" in parsed:
                    model_refusal_reason = str(parsed["refusal"])[:200]
                    break
            except json.JSONDecodeError:
                pass
        except Exception:
            pass
    if model_refusal_reason:
        log("3-drafting", "MODEL-REFUSAL", reason=model_refusal_reason)
        result["outcome"] = f"refused-by-model: {model_refusal_reason}"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        post_witness_observe(bus_root, f"orchestrator-{spec_id}",
                              "refusal_tested",
                              f"Model refused drafting: {model_refusal_reason}")
        return result

    # Find the frozen packet
    packet_path = None
    for p in drafting_out.rglob("5-agentic-build-packet-v0.json"):
        packet_path = p
        break
    if packet_path is None:
        log("3-drafting", "DOESNT-FIT-YET", note="no frozen packet emitted")
        result["outcome"] = "doesnt-fit-yet-no-packet"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        return result
    log("3-drafting", "ok", packet=str(packet_path))

    # ---------- Stage 4: emit build queue entry ----------
    queue_entry = emit_build_queue_entry(
        build_queue_dir, spec_id, run_id, packet_path, offering_md
    )
    log("4-queue", "ok", queue_entry=str(queue_entry))

    # ---------- Stage 5: build (mode = queue | telus | skip) ----------
    build_result = None
    finding = "no-change"
    if builder_mode == "telus":
        log("5-builder", "telus-build-starting")
        try:
            packet = json.loads(packet_path.read_text())
            sandbox = run_dir / "build-sandbox"
            br = build_from_packet(packet, adapter, sandbox_dir=sandbox,
                                    allow_repair=True)
            counter["telus_calls"] += len(br.get("attempts", []))
            finding = br.get("finding", "no-change")
            # Write a build-attempt summary
            (run_dir / "build-attempt.json").write_text(
                json.dumps({
                    "finding": br["finding"],
                    "model_label": br.get("model_label"),
                    "elapsed_seconds": br.get("elapsed_seconds"),
                    "n_attempts": len(br.get("attempts", [])),
                    "test_passed_final": br["attempts"][-1]["test_passed"] if br.get("attempts") else False,
                    "build_file": br.get("build_file"),
                    "sandbox": br.get("sandbox"),
                }, indent=2)
            )
            log("5-builder", "ok", finding=finding,
                attempts=len(br.get("attempts", [])),
                elapsed=br.get("elapsed_seconds"))
            build_result = br
        except Exception as e:
            log("5-builder", "FAIL", error=str(e))
            finding = "failed"
            build_result = {"finding": "failed", "error": str(e)}
    elif builder_wait_seconds > 0:
        log("5-builder-wait", "waiting", seconds=builder_wait_seconds)
        deadline = time.time() + builder_wait_seconds
        while time.time() < deadline:
            build_result = check_build_result(build_queue_dir, spec_id, run_id)
            if build_result is not None:
                break
            time.sleep(min(5, max(1, builder_wait_seconds / 10)))
        if build_result is None:
            log("5-builder", "skipped", reason="no builder result; using finding=no-change")
        else:
            finding = build_result.get("finding", "no-change")
            log("5-builder", "ok", finding=finding)
    else:
        log("5-builder", "skipped", reason="builder_mode=queue, wait=0; finding=no-change")

    # ---------- Stage 6: draft witness ----------
    witness_path = run_dir / "witness-record-draft.md"
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "draft_witness.py"),
        "draft",
        str(packet_path),
        "--finding", finding,
        "--team-name", f"Orchestrator-{spec_id}",
        "--out", str(witness_path),
        "--model-source", "gateway",
        "--gateway", gateway,
        "--model", model,
    ]
    sub_env = {**os.environ, "TELUS_TEAM_KEY": team_key}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                            env=sub_env)
        counter["telus_calls"] += 1
        if r.returncode != 0:
            log("6-witness-draft", "FAIL",
                stderr=r.stderr[-300:])
            result["outcome"] = "witness-draft-failed"
            result["finished_at"] = datetime.now(timezone.utc).isoformat()
            (run_dir / "result.json").write_text(json.dumps(result, indent=2))
            return result
        log("6-witness-draft", "ok", path=str(witness_path))
    except subprocess.TimeoutExpired:
        log("6-witness-draft", "TIMEOUT")
        result["outcome"] = "witness-timeout"
        result["finished_at"] = datetime.now(timezone.utc).isoformat()
        (run_dir / "result.json").write_text(json.dumps(result, indent=2))
        return result

    # ---------- Stage 6.5: reviewer (mesh-mode only) ----------
    if mesh_mode:
        try:
            build_attempt_path = run_dir / "build-attempt.json"
            reviewer_record = reviewer_review(
                build_packet_path=packet_path,
                witness_draft_path=witness_path,
                build_attempt_path=(
                    build_attempt_path if build_attempt_path.exists() else None
                ),
                model_source="gateway",
                gateway=gateway,
                team_key=team_key,
                model=model,
            )
            counter["telus_calls"] += 1
            findings_path = run_dir / "reviewer-findings.json"
            findings_path.write_text(json.dumps(reviewer_record, indent=2))
            findings = reviewer_record.get("findings", {})
            halt_publish = bool(findings.get("halt_publish", False))
            log("6.5-reviewer",
                "HALT" if halt_publish else "ok",
                halt_publish=halt_publish,
                halt_checks=[
                    c["name"] for c in findings.get("checks", [])
                    if c.get("status") == "halt"
                ],
                flag_checks=[
                    c["name"] for c in findings.get("checks", [])
                    if c.get("status") == "flag"
                ])
            post_witness_observe(
                bus_root, f"orchestrator-{spec_id}", "review_completed",
                f"reviewer halt_publish={halt_publish} for {spec_id}",
            )
            if halt_publish:
                result["outcome"] = "review-halted"
                result["finished_at"] = datetime.now(timezone.utc).isoformat()
                (run_dir / "result.json").write_text(json.dumps(result, indent=2))
                return result
        except Exception as e:
            log("6.5-reviewer", "FAIL", error=str(e))
            # Reviewer failure is non-fatal — record it and proceed to publish.
            # The validator (stage 7) is still a hard gate.
            post_witness_observe(
                bus_root, f"orchestrator-{spec_id}", "review_failed",
                f"reviewer error: {str(e)[:200]}",
            )

    # ---------- Stage 7: validate + publish to wall ----------
    effective_wall_root = wall_root if wall_root is not None else (out_dir / "wall")
    cmd = [
        "python3",
        str(kit_root / "scripts" / "jam" / "witness_append.py"),
        "append", str(witness_path),
        "--confirm-publish",
        "--wall-root", str(effective_wall_root),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode != 0:
            log("7-publish", "FAIL", stderr=r.stderr[-300:])
            result["outcome"] = "publish-failed"
        else:
            try:
                pub_info = json.loads(r.stdout)
                log("7-publish", "ok",
                    record_id=pub_info.get("record_id"))
            except Exception:
                log("7-publish", "ok", note="stdout-parse-skipped")
            result["outcome"] = "frozen-and-published"
    except subprocess.TimeoutExpired:
        log("7-publish", "TIMEOUT")
        result["outcome"] = "publish-timeout"

    result["finished_at"] = datetime.now(timezone.utc).isoformat()
    (run_dir / "result.json").write_text(json.dumps(result, indent=2))

    post_witness_observe(
        bus_root, f"orchestrator-{spec_id}", "composition_landed",
        f"Spec {spec_id} attempted with model {model}; outcome: {result['outcome']}",
    )

    return result


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_run(args):
    kit_root = Path(args.kit_root).expanduser()
    out_dir = Path(args.out_dir).expanduser()
    bus_root = Path(args.bus_root).expanduser()
    build_queue_dir = Path(args.build_queue).expanduser() if args.build_queue else (out_dir / "build-queue")
    wall_root = Path(args.wall_root).expanduser() if args.wall_root else None
    mesh_mode = bool(getattr(args, "mesh_mode", False))

    # Team key: prefer env var (TELUS_TEAM_KEY) over argv to avoid argv
    # leaks via /proc/<pid>/cmdline and crash-stderr capture. argv kept
    # for backward-compat + interactive use.
    team_key = args.team_key or os.environ.get("TELUS_TEAM_KEY")
    if not team_key:
        print("error: team key required via --team-key OR TELUS_TEAM_KEY env",
               file=sys.stderr)
        sys.exit(2)
    # Stash for downstream calls; never log this.
    args.team_key = team_key

    # Write-boundary: if --allowed-root supplied, every dir we plan to
    # write under must resolve inside it. Defends against caller-supplied
    # paths that escape via symlink / ..
    if args.allowed_root:
        from jam.loop_safety import ensure_path_within
        allowed = Path(args.allowed_root).expanduser().resolve()
        for label, p in [("out_dir", out_dir), ("bus_root", bus_root),
                          ("build_queue_dir", build_queue_dir)]:
            try:
                ensure_path_within(p, allowed)
            except PermissionError as e:
                print(f"error: {label} write-boundary: {e}", file=sys.stderr)
                sys.exit(2)
        if wall_root is not None:
            try:
                ensure_path_within(wall_root, allowed)
            except PermissionError as e:
                print(f"error: wall_root write-boundary: {e}", file=sys.stderr)
                sys.exit(2)

    out_dir.mkdir(parents=True, exist_ok=True)
    bus.init_bus(bus_root)

    counter = {"telus_calls": 0, "specs_attempted": 0,
               "specs_published": 0, "specs_refused": 0}

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        print("error: --models must be non-empty", file=sys.stderr)
        sys.exit(2)

    candidates = args.specs.split(",") if args.specs else ORCHESTRATOR_CANDIDATE_SPECS
    candidates = [c.strip() for c in candidates if c.strip()][:args.max_specs]

    print(f"Orchestrator starting: {len(candidates)} candidate spec(s), models={models}",
           flush=True)
    print(f"  out_dir: {out_dir}")
    print(f"  bus_root: {bus_root}")
    print(f"  build_queue: {build_queue_dir}")
    print()

    start_time = time.time()
    deadline = start_time + args.time_budget_min * 60

    results = []
    for i, spec_id in enumerate(candidates):
        if counter["telus_calls"] >= args.max_telus_calls:
            print(f"  Budget cap hit: telus_calls={counter['telus_calls']} >= max", flush=True)
            break
        if time.time() >= deadline:
            print(f"  Time budget exceeded ({args.time_budget_min} min)", flush=True)
            break
        # Rotate model across specs
        model = models[i % len(models)]
        print(f"\n=== [{i+1}/{len(candidates)}] {spec_id} (model={model}) ===", flush=True)
        result = attempt_spec(
            spec_id=spec_id,
            kit_root=kit_root,
            out_dir=out_dir,
            bus_root=bus_root,
            gateway=args.gateway,
            team_key=args.team_key,
            model=model,
            counter=counter,
            build_queue_dir=build_queue_dir,
            builder_wait_seconds=args.builder_wait_seconds,
            builder_mode=args.builder_mode,
            mesh_mode=mesh_mode,
            wall_root=wall_root,
        )
        results.append(result)
        counter["specs_attempted"] += 1
        if result["outcome"] == "frozen-and-published":
            counter["specs_published"] += 1
        if result["outcome"] == "refused-by-gatekeeper":
            counter["specs_refused"] += 1

    # Master summary
    summary = {
        "started_at": datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "wall_time_seconds": round(time.time() - start_time, 1),
        "counter": counter,
        "results": results,
    }
    summary_path = out_dir / f"orchestrator-summary-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print()
    print(f"=== ORCHESTRATOR FINISHED ===")
    print(f"  specs attempted: {counter['specs_attempted']}")
    print(f"  specs published to wall: {counter['specs_published']}")
    print(f"  specs refused by gatekeeper: {counter['specs_refused']}")
    print(f"  telus calls: {counter['telus_calls']}")
    print(f"  wall time: {summary['wall_time_seconds']}s")
    print(f"  summary: {summary_path}")


def cmd_report(args):
    out_dir = Path(args.out_dir).expanduser()
    summaries = sorted(out_dir.glob("orchestrator-summary-*.json"))
    if not summaries:
        print("no summaries found in", out_dir, file=sys.stderr)
        sys.exit(1)
    latest = summaries[-1]
    summary = json.loads(latest.read_text())
    print(f"# Orchestrator Report — {latest.name}\n")
    print(f"- started: {summary['started_at']}")
    print(f"- finished: {summary['finished_at']}")
    print(f"- wall time: {summary['wall_time_seconds']}s")
    print(f"- specs attempted: {summary['counter']['specs_attempted']}")
    print(f"- specs published: {summary['counter']['specs_published']}")
    print(f"- specs refused: {summary['counter']['specs_refused']}")
    print(f"- telus calls: {summary['counter']['telus_calls']}")
    print(f"\n## Per-spec results\n")
    for r in summary["results"]:
        print(f"- **{r['spec_id']}** (model={r['model']}) → {r['outcome']}")
        for s in r["stages"]:
            if s["status"] != "ok":
                print(f"    - stage {s['stage']}: {s['status']}")


def main():
    ap = argparse.ArgumentParser(prog="orchestrator.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_run = sub.add_parser("run", help="run the orchestrator")
    ap_run.add_argument("--kit-root", required=True)
    ap_run.add_argument("--gateway", required=True)
    ap_run.add_argument("--team-key", default=None,
                          help="Bearer key for the gateway. PREFER passing "
                               "via TELUS_TEAM_KEY env var (avoids argv "
                               "leak to /proc/<pid>/cmdline + stderr_tail).")
    ap_run.add_argument("--allowed-root",
                          help="restrict all writes (out-dir, bus-root, "
                               "build-queue, wall-root) to this dir; used "
                               "by overnight_loop to enforce write-boundary "
                               "inside the subprocess")
    ap_run.add_argument("--models",
                          default="telus-qwen,telus-gemma",
                          help="comma-separated model list")
    ap_run.add_argument("--specs", help="comma-separated spec IDs; "
                                          "default: orchestrator candidate list")
    ap_run.add_argument("--max-specs", type=int, default=5)
    ap_run.add_argument("--max-telus-calls", type=int, default=60)
    ap_run.add_argument("--time-budget-min", type=int, default=60)
    ap_run.add_argument("--bus-root", default="/tmp/orchestrator-bus")
    ap_run.add_argument("--out-dir", default="/tmp/orchestrator-runs")
    ap_run.add_argument("--build-queue", help="build queue dir (default: <out-dir>/build-queue)")
    ap_run.add_argument("--builder-wait-seconds", type=int, default=0,
                          help="seconds to wait for a builder to report a "
                               "result (default 0: skip building, use "
                               "finding=no-change for witness draft)")
    ap_run.add_argument("--builder-mode", choices=["queue", "telus", "skip"],
                          default="queue",
                          help="how to build: queue (emit build-queue entry + "
                               "wait for external builder); telus (call TELUS "
                               "to generate CLI + run acceptance test + "
                               "one-shot repair); skip (no build attempt, "
                               "draft witness with finding=no-change)")
    ap_run.add_argument("--mesh-mode", action="store_true",
                          help="enable multi-agent-mesh-v0: invoke Reviewer "
                               "between witness-draft and publish; reviewer "
                               "may halt publish")
    ap_run.add_argument("--wall-root",
                          help="explicit wall dir for publish (default: "
                               "<out-dir>/wall); use to share one cumulative "
                               "wall across multiple round subdirs")
    ap_run.set_defaults(func=cmd_run)

    ap_report = sub.add_parser("report", help="report on the latest run")
    ap_report.add_argument("out_dir")
    ap_report.set_defaults(func=cmd_report)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
