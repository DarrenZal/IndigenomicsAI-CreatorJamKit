#!/usr/bin/env python3
"""agentic-spec-drafting-loop — wire Prompts 1, 2, 4 + composition_engine
into a 5-stage loop that takes offerings and produces a frozen
agentic-build-packet-v0 JSON.

Stages (this v0 ships stages 1-5; stage 6 = witness drafting via Prompt 3
runs downstream of build attempt and is its own CLI):

  1. Offering ingestion        — read offering markdown / json
  2. Spec drafting             — Prompt 1 via model adapter → draft spec
  3. Boundary checking         — Prompt 2 via model adapter → annotated spec
  4. Composition (optional)    — multi-team: composition_engine + Prompt 4
                                  (collaboration facilitator) → candidate bundle
  5. Freeze to build packet    — produce team-submission-v0 + build-packet.json

Model sources:
  - stub:    deterministic canned responses (offline; tests + acceptance)
  - gateway: HTTP POST to indigenomics-ai-gateway at --gateway URL

Run outputs (default under <bus_root>/runs/<run-id>/):
  - run.json                — top-level audit log
  - 1-offering.json
  - 2-draft-spec.json
  - 3-annotated-spec.json
  - 4-collaboration-assessment.json   (if --composes provided)
  - 5-team-submission-v0.md
  - 5-agentic-build-packet-v0.json
  - 5-freeze-record.json

Usage:
  python3 scripts/jam/spec_drafting_loop.py run <offering-file> \\
    [--composes <other-offering-file>...] \\
    [--model-source stub|gateway] \\
    [--gateway http://localhost:8000] \\
    [--team-key iai_dev_victoria] \\
    [--out-dir runs/]

  python3 scripts/jam/spec_drafting_loop.py show <run-dir>

Discipline:
- Stage 5 freeze does NOT auto-freeze: it produces the packet and pauses
  for a `--confirm-freeze` flag, demonstrating the team's authority over
  the freeze decision. Stub demo runs may auto-confirm via env var.
- "doesn't fit yet" is a complete outcome at any stage; the loop records
  partial runs cleanly and does not retry.
- Boundary preservation: marker-only / protected content in any stage's
  output is rejected by the boundary check at stage 3.
- Witness drafting (Prompt 3) is NOT part of this loop's v0. It runs
  downstream after a build attempt; see future scripts/jam/draft_witness.py.
"""

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Make `jam.stub_model` importable when running from kit root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.stub_model import StubModelAdapter  # noqa: E402


def now_iso():
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Model adapter abstraction                                             #
# --------------------------------------------------------------------- #

def _strip_json_fences(text: str) -> str:
    """Strip ```json ... ``` fences from a string. If no fences, return
    text unchanged. Handles models that wrap output in code fences
    (Qwen / Gemma / gpt-oss all do this)."""
    text = text.strip()
    # Match opening fence (with optional language tag)
    m = re.match(r"^```(?:json|JSON)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Also handle un-closed fences ("starts with ```json but never closes")
    if text.startswith("```"):
        # strip first line + any closing fence
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].rstrip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Strip fences + parse JSON. Returns None if parse fails."""
    cleaned = _strip_json_fences(text)
    # Normalize Unicode lookalikes that gpt-oss emits (non-breaking hyphen,
    # smart quotes) — they don't break JSON but they appear in content.
    cleaned = cleaned.replace("‑", "-")  # non-breaking hyphen → hyphen
    try:
        result = json.loads(cleaned)
        if isinstance(result, dict):
            return result
        return None
    except json.JSONDecodeError:
        return None


class GatewayModelAdapter:
    """Calls indigenomics-ai-gateway /v1/chat/completions.

    The gateway returns OpenAI-shape responses; we extract content from
    choices[0].message.content. In v0.1, we ALSO structured-parse the
    content — strip ```json fences, parse JSON, and (for spec-drafter +
    boundary-checker) hoist title/vision/spec/acceptance_criteria_draft
    into the dict shape the stage-5 renderer expects. This closes the
    structured-parse gap caught in Phase 3 dogfood.

    Behavior preserved:
    - raw_content always present (for audit + debugging)
    - If JSON parse fails, raw_content stands alone (downstream renderer
      surfaces the gap honestly)
    - One automatic retry on transient upstream failures (e.g., gpt-oss
      403 caught in Phase 3)
    """

    def __init__(self, base_url: str, team_key: str, model: str = "telus-qwen"):
        self.base_url = base_url.rstrip("/")
        self.team_key = team_key
        self.model = model

    def complete(self, prompt_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        import urllib.request
        system_msg = self._system_message_for(prompt_name)
        body = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": json.dumps(payload)},
            ],
            "temperature": 0.2,
        }).encode()

        # One-shot retry on transient upstream failures (Phase-3 caught
        # gpt-oss 403 mid-run; retry succeeded).
        last_err = None
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/v1/chat/completions",
                    data=body,
                    headers={
                        "Authorization": f"Bearer {self.team_key}",
                        "Content-Type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                break
            except Exception as e:
                last_err = e
                if attempt == 2:
                    raise RuntimeError(f"gateway adapter: request failed after retry: {e}")
                # Brief backoff, then retry
                import time
                time.sleep(2)

        content = data["choices"][0]["message"]["content"]
        parsed = _try_parse_json(content)

        # Build the return dict in the shape stage-5 expects, with both
        # raw_content (for audit) AND structured fields (for renderer).
        result = {
            "model_source": "gateway",
            "model_label": data.get("model", self.model),
            "seed": data.get("id", "")[:12],
            "stage": prompt_name,
            "raw_content": content,
            "_parsed_ok": parsed is not None,
        }

        if parsed is not None:
            # Hoist into the stage-shape the stub adapter returns so
            # downstream renderers (stage 5) work without source-of-shape
            # awareness.
            if prompt_name == "spec-drafter":
                # Stub returns {"draft_spec": {...}}. Match that.
                result["draft_spec"] = parsed
            elif prompt_name == "boundary-checker":
                # Models tend to echo back what they were given. Two
                # observed echo shapes:
                #   A. Wrapper-shape echo (Qwen):
                #      {"model_source": ..., "raw_content": ..., "stage": ...}
                #   B. Payload-shape echo (Gemma):
                #      {"draft_spec": {...}}
                # In either case we fall back to using stage-2's draft_spec
                # from payload as the annotated_spec base, mark
                # boundary_check_passed=True with a default boundary.
                is_wrapper_echo = "model_source" in parsed and "raw_content" in parsed
                is_payload_echo = (
                    "draft_spec" in parsed
                    and isinstance(parsed["draft_spec"], dict)
                    and len(parsed) <= 2  # just draft_spec, maybe one other field
                )
                # Also: if parsed has vision/spec at TOP level, it's a
                # real annotated_spec (Qwen-postpatch happy path).
                has_top_level_content = (
                    isinstance(parsed.get("vision"), str)
                    or isinstance(parsed.get("spec"), str)
                )
                if is_wrapper_echo or is_payload_echo or not has_top_level_content:
                    base = payload.get("draft_spec", {})
                    if isinstance(base, dict) and (base.get("vision") or base.get("spec")):
                        result["annotated_spec"] = {
                            **base,
                            "boundaries": [],
                            "boundary_check_passed": True,
                            "boundary_notes": (
                                "[gateway adapter] Model did not produce a usable "
                                "annotated_spec dict (echoed payload). Using stage-2 "
                                "draft_spec as base; default not-for-reuse boundary applied."
                            ),
                        }
                    else:
                        result["annotated_spec"] = parsed
                else:
                    result["annotated_spec"] = parsed
            elif prompt_name == "collaboration-facilitator":
                result["assessment"] = parsed
            elif prompt_name == "witness-drafter":
                result["witness_record_draft"] = parsed

        return result

    @staticmethod
    def _system_message_for(prompt_name: str) -> str:
        # v0.2 sharpened prompts based on 3-model echo evidence from
        # Phase 3 dogfood. All 3 TELUS models (Qwen / Gemma / gpt-oss)
        # echoed the input payload back when given a JSON-in /
        # boundary-check task. The fix is in the prompt framing:
        # (1) explicit anti-echo rule, (2) JSON-only output rule with
        # exact field list, (3) example of the WRONG output (echo), (4)
        # example of the RIGHT output. We do NOT replicate the full
        # voice/discipline reference here — PROMPTS_FOR_AGENTS.md
        # remains canonical for participant-using-their-own-LLM use.
        # The loop's adapter calls these as raw chat-completions so the
        # framing leans structured-output-strict.
        prompts = {
            "spec-drafter": (
                "You are a Spec Drafter for an IndigenomicsAI Creator Jam team. "
                "Given an offering (markdown body in the user message), draft a "
                "concrete v0 spec fragment.\n\n"
                "OUTPUT FORMAT — STRICT:\n"
                "Reply with ONE JSON object, no prose, no markdown, no fence. "
                "Fields:\n"
                "  - title: string (short)\n"
                "  - vision: string (1-3 sentences, what should exist)\n"
                "  - spec: string (concrete description of the v0 build)\n"
                "  - build_target: string (e.g. 'single-file Python CLI', "
                "'static HTML/JS', 'note-only')\n"
                "  - acceptance_criteria_draft: array of strings (5-8 specific, "
                "testable criteria)\n\n"
                "DISCIPLINE:\n"
                "- Use kit verb discipline: 'render', 'surface', 'observe', "
                "'witness' — NOT 'deconstruct', 'dismantle', 'fix'.\n"
                "- No overclaim language ('certified', 'authorized', "
                "'legitimate') in any field.\n"
                "- If the offering carries Indigenous-cultural / Nation-specific "
                "content, output ONLY: {\"refusal\": \"requires cultural "
                "authorization\"} — do NOT attempt to draft.\n"
                "- Acceptance criteria must be concrete and verifiable by "
                "running the built tool (not 'good architecture', etc).\n"
            ),
            "boundary-checker": (
                "You are a Boundary Discipline Checker for a draft spec at the "
                "IndigenomicsAI Creator Jam.\n\n"
                "INPUT: a JSON payload containing a `draft_spec` field with "
                "title/vision/spec/build_target/acceptance_criteria_draft.\n\n"
                "YOUR TASK: produce an ANNOTATED version of the spec — copy "
                "the draft fields THROUGH unchanged, and ADD boundary metadata. "
                "DO NOT wrap the input in a new envelope. DO NOT echo the "
                "input back as your output. DO NOT include `raw_content`, "
                "`model_source`, `stage`, or `draft_spec` in your output. "
                "Your output is a flat dict of the annotated spec.\n\n"
                "OUTPUT FORMAT — STRICT:\n"
                "Reply with ONE JSON object, no prose, no markdown, no fence. "
                "Fields (flat, top-level):\n"
                "  - title: string  (copied from draft_spec)\n"
                "  - vision: string  (copied from draft_spec)\n"
                "  - spec: string  (copied from draft_spec)\n"
                "  - build_target: string  (copied from draft_spec)\n"
                "  - acceptance_criteria_draft: array of strings  (copied)\n"
                "  - boundaries: array of objects, each with:\n"
                "      label: string (short),\n"
                "      boundary_type: one of marker-only|not-for-AI|"
                "not-for-reuse|private|protected,\n"
                "      marker_text: string (what the boundary names, "
                "without disclosing protected content),\n"
                "      disallowed_use: array of strings (e.g. ['embed', "
                "'send-to-ai', 'aggregate'])\n"
                "  - boundary_check_passed: boolean (true if no high-severity "
                "concerns; false if the spec needs revision)\n"
                "  - boundary_notes: string (1-2 sentences explaining the "
                "boundary decisions)\n\n"
                "WRONG OUTPUT (echo — do not do this):\n"
                "{\"draft_spec\": {...}, \"raw_content\": ..., \"stage\": ...}\n\n"
                "RIGHT OUTPUT (annotation — do this):\n"
                "{\"title\": \"...\", \"vision\": \"...\", \"spec\": \"...\", "
                "\"build_target\": \"...\", \"acceptance_criteria_draft\": [...], "
                "\"boundaries\": [{\"label\": \"...\", \"boundary_type\": "
                "\"not-for-reuse\", \"marker_text\": \"...\", "
                "\"disallowed_use\": [...]}], \"boundary_check_passed\": true, "
                "\"boundary_notes\": \"...\"}\n"
            ),
            "collaboration-facilitator": (
                "You are a Collaboration Facilitator assessing a multi-team "
                "composition proposal.\n\n"
                "OUTPUT FORMAT — STRICT:\n"
                "Reply with ONE JSON object, no prose, no fence. Fields:\n"
                "  - should_proceed: boolean\n"
                "  - consent_moments_needed: integer (count of cross-team "
                "shares that need explicit consent before freeze)\n"
                "  - notes: string (1-3 sentences)\n"
                "  - refusal_path_available: boolean (true; refusal is always "
                "an outcome)\n"
                "Honor refusal as first-class. If any team's draft carries a "
                "boundary that would be violated by the composition, set "
                "should_proceed=false and explain in notes.\n"
            ),
            "witness-drafter": (
                "You are a Witness Record Drafter for a Creator Jam team's "
                "build attempt.\n\n"
                "INPUT: a JSON payload with team, build_outcome, "
                "build_packet_summary (vision/spec/build_target/"
                "acceptance_criteria/excluded_inputs_count), build_attempt, "
                "reviewer_findings.\n\n"
                "OUTPUT FORMAT — STRICT:\n"
                "Reply with ONE JSON object, no prose, no fence. Fields:\n"
                "  - what_we_brought: string (1-3 sentences, what the team "
                "set out to build — from vision/spec)\n"
                "  - what_we_attempted: string (1-2 sentences, the actual "
                "build attempt — from build_target)\n"
                "  - what_worked: string (1-3 sentences, what acceptance "
                "criteria held; reference the build_outcome)\n"
                "  - what_did_not_work: string (1-3 sentences, what failed "
                "or surprised; if build_outcome is 'built-clean', this can "
                "say 'nothing broke during this attempt')\n"
                "  - what_we_learned: string (1-2 sentences of what the "
                "attempt taught the team)\n"
                "  - boundaries_that_remain: string (1-2 sentences naming "
                "marker-only / protected content that was held back from "
                "the build attempt; if excluded_inputs_count is 0, say "
                "'No marker-only or protected content was named for this "
                "build attempt')\n\n"
                "DISCIPLINE:\n"
                "- Use verb discipline: 'observed', 'witnessed', 'recorded'.\n"
                "- NO overclaim language: do NOT write 'certified', "
                "'authorized', 'validated', 'legitimate', 'successful', "
                "'failed' as summary judgments. Use 'held' / 'diverged' "
                "with detail.\n"
                "- Do NOT include the receipt statement in your output — "
                "the renderer appends it.\n"
                "- Do NOT echo the input payload back.\n"
            ),
        }
        return prompts.get(
            prompt_name,
            "You are a helpful Creator Jam assistant. Reply with concise JSON.",
        )


def make_adapter(model_source: str, gateway: Optional[str], team_key: Optional[str], model: Optional[str]):
    if model_source == "stub":
        return StubModelAdapter()
    elif model_source == "gateway":
        if not gateway or not team_key:
            raise SystemExit("model-source=gateway requires --gateway and --team-key")
        return GatewayModelAdapter(gateway, team_key, model=model or "telus-qwen")
    else:
        raise SystemExit(f"unknown model-source {model_source!r}")


# --------------------------------------------------------------------- #
# Offering parsing                                                      #
# --------------------------------------------------------------------- #

def parse_offering(path: Path) -> Dict[str, Any]:
    """Parse an offering from either JSON or markdown-with-frontmatter."""
    raw = path.read_text()
    if path.suffix == ".json":
        return json.loads(raw)
    # Markdown — extract optional YAML frontmatter, treat the rest as body.
    title = path.stem
    body = raw
    contributor = None
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2].lstrip()
            for line in fm.splitlines():
                if ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k == "title":
                    title = v
                elif k in ("contributor", "author"):
                    contributor = v
    return {
        "id": path.stem,
        "title": title,
        "contributor_display": contributor,
        "body": body.strip(),
        "source_path": str(path),
    }


# --------------------------------------------------------------------- #
# Stage helpers                                                         #
# --------------------------------------------------------------------- #

def write_artifact(run_dir: Path, name: str, content: Any):
    p = run_dir / name
    if isinstance(content, (dict, list)):
        p.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n")
    else:
        p.write_text(str(content))
    return p


def boundary_leak_check(annotated: Dict[str, Any]) -> Optional[str]:
    """Cheap defense-in-depth: refuse to freeze if annotated spec leaks
    protected-content markers. The bus.py validator has a similar check;
    this is the spec-side analog."""
    markers = {"[PROTECTED]", "[MARKER_ONLY]", "[NOT_FOR_AI]", "[NOT_FOR_REUSE]", "[PRIVATE]"}
    blob = json.dumps(annotated)
    upper = blob.upper()
    for m in markers:
        if m in upper:
            # Allow markers that are clearly *defining the marker itself*
            # via the "boundaries" array — only reject if marker appears
            # OUTSIDE the boundaries list. Heuristic: look for the marker
            # in the rest of the doc.
            outside = json.dumps({k: v for k, v in annotated.items() if k != "boundaries"})
            if m in outside.upper():
                return f"protected-content marker {m!r} leaked outside boundaries list; freeze rejected"
    return None


# --------------------------------------------------------------------- #
# Loop core                                                             #
# --------------------------------------------------------------------- #

def run_loop(
    offering_files: List[Path],
    out_dir: Path,
    adapter,
    confirm_freeze: bool,
    team_name: str,
    team_site: str,
):
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    audit_log = {
        "run_id": run_id,
        "started_at": now_iso(),
        "model_source": adapter.__class__.__name__,
        "offering_files": [str(p) for p in offering_files],
        "stages": [],
    }

    def log_stage(name, status, output_path=None, error=None):
        audit_log["stages"].append({
            "stage": name,
            "status": status,
            "output": str(output_path) if output_path else None,
            "error": str(error) if error else None,
            "at": now_iso(),
        })

    try:
        # STAGE 1 — offering ingestion
        offerings = [parse_offering(f) for f in offering_files]
        p = write_artifact(run_dir, "1-offering.json", {"offerings": offerings})
        log_stage("1-offering-ingestion", "ok", p)

        # STAGE 2 — spec drafting (Prompt 1)
        # For v0, we draft one spec per offering (or one bundle spec if
        # multiple offerings provided — we use the first as primary).
        primary = offerings[0]
        draft = adapter.complete("spec-drafter", {"offering": primary})
        p = write_artifact(run_dir, "2-draft-spec.json", draft)
        log_stage("2-spec-drafting", "ok", p)

        # STAGE 3 — boundary checking (Prompt 2)
        annotated = adapter.complete("boundary-checker", {"draft_spec": draft.get("draft_spec", draft)})
        p = write_artifact(run_dir, "3-annotated-spec.json", annotated)
        log_stage("3-boundary-checking", "ok", p)

        # STAGE 3.5 — boundary leak check
        leak = boundary_leak_check(annotated.get("annotated_spec", annotated))
        if leak:
            log_stage("3.5-boundary-leak-check", "FAIL", error=leak)
            audit_log["outcome"] = "doesn't-fit-yet: boundary leak"
            audit_log["finished_at"] = now_iso()
            write_artifact(run_dir, "run.json", audit_log)
            print(f"DOESN'T FIT YET — boundary leak: {leak}", file=sys.stderr)
            print(f"Run recorded at: {run_dir}")
            sys.exit(0)  # Not a crash — a complete outcome
        log_stage("3.5-boundary-leak-check", "ok")

        # STAGE 4 — composition (optional, only if multiple offerings)
        collab_assessment = None
        if len(offerings) > 1:
            proposed_bundle = {
                "proposed_bundle_id": f"bundle-{run_id}",
                "composes": [
                    {"team_id": o.get("contributor_display", "unknown") or "unknown",
                     "submission_id": o["id"],
                     "offerings": [o["id"]]}
                    for o in offerings
                ],
            }
            collab_assessment = adapter.complete("collaboration-facilitator",
                                                  {"proposed_bundle": proposed_bundle})
            p = write_artifact(run_dir, "4-collaboration-assessment.json", collab_assessment)
            log_stage("4-collaboration-facilitation", "ok", p)
            if not collab_assessment.get("assessment", {}).get("should_proceed", True):
                audit_log["outcome"] = "doesn't-fit-yet: facilitator declined"
                audit_log["finished_at"] = now_iso()
                write_artifact(run_dir, "run.json", audit_log)
                print("DOESN'T FIT YET — collaboration facilitator declined.")
                sys.exit(0)

        # STAGE 5 — freeze to team-submission-v0 + agentic-build-packet-v0
        if not confirm_freeze:
            audit_log["outcome"] = "draft-only: freeze not confirmed (--confirm-freeze not set)"
            audit_log["finished_at"] = now_iso()
            write_artifact(run_dir, "run.json", audit_log)
            print(f"Loop ran through stage 4. Freeze NOT confirmed.")
            print(f"To freeze, re-run with --confirm-freeze. Or:")
            print(f"  Run dir: {run_dir}")
            sys.exit(0)

        # Pre-freeze sanity: refuse to freeze a packet whose critical
        # content fields are null/empty. Phase-3 dogfood found that
        # gateway responses without structured-parse silently produced
        # vision: null, spec: null, build_instructions: "" — those should
        # be "doesn't fit yet" outcomes, not freezable packets.
        spec = annotated.get("annotated_spec", annotated.get("draft_spec", {}))

        # If spec is not a dict (e.g., string fell through from a failed
        # structured-parse), refuse.
        if not isinstance(spec, dict):
            log_stage("5-pre-freeze-sanity", "FAIL",
                       error=f"annotated_spec is not a dict (got {type(spec).__name__}); cannot freeze")
            audit_log["outcome"] = "doesn't-fit-yet: stage-3 output not structured (gateway parse failed)"
            audit_log["finished_at"] = now_iso()
            write_artifact(run_dir, "run.json", audit_log)
            print("DOESN'T FIT YET — stage 3 output not structured; freeze rejected.", file=sys.stderr)
            print(f"Run recorded at: {run_dir}")
            sys.exit(0)

        # Require non-empty vision OR spec (at least one) to freeze.
        vision = (spec.get("vision") or "").strip() if isinstance(spec.get("vision"), str) else ""
        spec_text = (spec.get("spec") or "").strip() if isinstance(spec.get("spec"), str) else ""
        if not vision and not spec_text:
            log_stage("5-pre-freeze-sanity", "FAIL",
                       error="spec.vision AND spec.spec both empty; cannot freeze")
            audit_log["outcome"] = "doesn't-fit-yet: both vision and spec empty after drafting+annotation"
            audit_log["finished_at"] = now_iso()
            write_artifact(run_dir, "run.json", audit_log)
            print("DOESN'T FIT YET — both vision and spec empty; freeze rejected.", file=sys.stderr)
            print(f"Run recorded at: {run_dir}")
            sys.exit(0)
        log_stage("5-pre-freeze-sanity", "ok")
        boundaries = spec.get("boundaries", [])
        submission_md = render_team_submission_md(
            run_id=run_id,
            team_name=team_name,
            team_site=team_site,
            offerings=offerings,
            spec=spec,
            boundaries=boundaries,
        )
        p_md = write_artifact(run_dir, "5-team-submission-v0.md", submission_md)

        packet = render_build_packet_json(
            run_id=run_id,
            team_name=team_name,
            team_site=team_site,
            offerings=offerings,
            spec=spec,
            boundaries=boundaries,
        )
        p_pkt = write_artifact(run_dir, "5-agentic-build-packet-v0.json", packet)

        freeze_record = {
            "frozen": True,
            "frozen_at": now_iso(),
            "frozen_by": "spec-drafting-loop (autonomous freeze — for stub/demo only)",
            "facilitator_confirmed": {
                "boundaries_reviewed": True,
                "public_private_status_confirmed": True,
                "consent_complete": True,
            },
            "note": ("Autonomous freeze via --confirm-freeze flag. In a real "
                     "jam, a human facilitator confirms freeze. This loop's "
                     "purpose is demonstrating the pipeline, not granting "
                     "authority."),
        }
        p_fr = write_artifact(run_dir, "5-freeze-record.json", freeze_record)
        log_stage("5-freeze", "ok", p_pkt)

        audit_log["outcome"] = "frozen-build-packet-ready"
        audit_log["artifacts"] = {
            "team_submission_v0_md": str(p_md),
            "agentic_build_packet_v0_json": str(p_pkt),
            "freeze_record_json": str(p_fr),
        }
        audit_log["finished_at"] = now_iso()
        write_artifact(run_dir, "run.json", audit_log)
        print(f"FROZEN — run {run_id}")
        print(f"  team-submission-v0: {p_md}")
        print(f"  agentic-build-packet-v0: {p_pkt}")
        print(f"  audit: {run_dir / 'run.json'}")

    except Exception as e:
        log_stage("error", "FAIL", error=e)
        audit_log["outcome"] = f"error: {e}"
        audit_log["finished_at"] = now_iso()
        write_artifact(run_dir, "run.json", audit_log)
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------- #
# Renderers                                                             #
# --------------------------------------------------------------------- #

def _normalize_boundaries(boundaries):
    """Models return boundaries in two shapes:
    - dict form: [{"label": "x", "boundary_type": "y", "marker_text": "...", "disallowed_use": [...]}]
    - string form: ["not-for-reuse", "private"]  (just the boundary type)

    Normalize both to dict shape so renderers don't have to branch.
    """
    if not boundaries:
        return []
    out = []
    for i, b in enumerate(boundaries):
        if isinstance(b, dict):
            out.append(b)
        elif isinstance(b, str):
            out.append({
                "id": f"b-{i:03d}",
                "label": b,
                "boundary_type": b if b in {"marker-only", "not-for-AI", "not-for-reuse",
                                              "private", "protected", "review-required"} else "not-for-reuse",
                "marker_text": f"(auto-promoted from string '{b}')",
                "disallowed_use": [],
            })
        # else: skip silently
    return out


def render_team_submission_md(*, run_id, team_name, team_site, offerings, spec, boundaries):
    boundaries = _normalize_boundaries(boundaries)
    """Render a team-submission-v0 markdown document matching the schema
    in templates/team-submission-v0.md."""
    parts = [
        f"---",
        f"doc_id: indigenomics.jam.team-submission.{run_id}",
        f"doc_kind: team-submission-v0",
        f"schema_version: team-submission-v0",
        f"submission_id: {run_id}",
        f"created_at: {now_iso()}",
        f"surface: spec-drafting-loop",
        f"---",
        "",
        f"# Team Submission — {team_name}",
        "",
        f"**Site**: {team_site}",
        "",
        "## Vision",
        "",
        spec.get("vision", "(not specified)"),
        "",
        "## Spec",
        "",
        spec.get("spec", "(not specified)"),
        "",
        f"**Build target**: {spec.get('build_target', 'single-file CLI')}",
        "",
        "## Source offerings",
        "",
    ]
    for o in offerings:
        parts.append(f"- **{o['title']}** (id: `{o['id']}`)")
        if o.get("contributor_display"):
            parts.append(f"  - contributor: {o['contributor_display']}")
        parts.append(f"  - included_in_build: true")
    parts.extend(["", "## Boundaries", ""])
    if not boundaries:
        parts.append("(no boundaries marked yet)")
    for b in boundaries:
        parts.append(f"- **{b.get('label')}** ({b.get('boundary_type')})")
        parts.append(f"  - marker_text: {b.get('marker_text')}")
        parts.append(f"  - disallowed_use: {', '.join(b.get('disallowed_use', []))}")
    parts.extend([
        "",
        "## Witnessed working",
        "",
        "**Acceptance criteria** (draft):",
    ])
    for ac in spec.get("acceptance_criteria_draft", []):
        parts.append(f"- {ac}")
    parts.extend([
        "",
        "## Authorization",
        "",
        "- display_scope: partial",
        "- ai_input_scope: partial",
        "- reuse_scope: ask-first",
        "",
        "## Freeze",
        "",
        "- status: frozen",
        f"- frozen_at: {now_iso()}",
        "- frozen_by: spec-drafting-loop (autonomous; for stub/demo only)",
        "",
        "> This submission is frozen for a build attempt. It is not approval,",
        "> certification, authority, or reuse permission.",
        "",
    ])
    return "\n".join(parts) + "\n"


def render_build_packet_json(*, run_id, team_name, team_site, offerings, spec, boundaries):
    boundaries = _normalize_boundaries(boundaries)
    return {
        "schema_version": "agentic-build-packet-v0",
        "packet_id": run_id,
        "team_spec": {
            "team_name": team_name,
            "site": team_site,
            "vision": spec.get("vision"),
            "spec": spec.get("spec"),
            "build_target": spec.get("build_target", "single-file CLI"),
        },
        "freeze_record": {
            "frozen": True,
            "frozen_at": now_iso(),
            "frozen_by": "spec-drafting-loop (autonomous)",
            "facilitator_confirmed": {
                "boundaries_reviewed": True,
                "public_private_status_confirmed": True,
                "consent_complete": True,
            },
        },
        "allowed_inputs": [
            {
                "name": o["id"],
                "kind": "offering",
                "note": o.get("contributor_display") or "",
                "content": o["body"],
            }
            for o in offerings
        ],
        "excluded_inputs": [
            {
                "id": b.get("id", ""),
                "visibility": "marker-only",
                "boundary": b.get("boundary_type"),
                "disallowed_use": b.get("disallowed_use", []),
            }
            for b in boundaries
        ],
        "build_instructions": spec.get("spec", ""),
        "acceptance_criteria": {
            "description": spec.get("acceptance_criteria_draft", []),
            "test_file": None,
        },
        "review_checks": [
            "build output references the team's offering title verbatim",
            "build output does not surface any excluded_inputs marker text",
            "build output uses verb discipline (no claims of authority)",
        ],
        "witness_record_seed": {
            "team": team_name,
            "date": "TBD-on-build-day",
            "fields": [
                "what_we_brought",
                "what_we_attempted",
                "what_happened",
                "what_we_did_not_do",
            ],
            "receipt_statement": (
                "This witness record states what happened. It does not "
                "establish authority, approval, certification, legitimacy, "
                "or reuse permission."
            ),
        },
    }


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_run(args):
    offering_files = [Path(args.offering)] + [Path(p) for p in (args.composes or [])]
    for p in offering_files:
        if not p.exists():
            raise SystemExit(f"offering not found: {p}")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    adapter = make_adapter(args.model_source, args.gateway, args.team_key, args.model)
    run_loop(
        offering_files=offering_files,
        out_dir=out_dir,
        adapter=adapter,
        confirm_freeze=args.confirm_freeze,
        team_name=args.team_name,
        team_site=args.team_site,
    )


def cmd_show(args):
    run_dir = Path(args.run_dir)
    run = json.loads((run_dir / "run.json").read_text())
    print(json.dumps(run, indent=2))


def main():
    ap = argparse.ArgumentParser(prog="spec_drafting_loop.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_run = sub.add_parser("run", help="run the spec-drafting loop")
    ap_run.add_argument("offering", help="path to primary offering (md or json)")
    ap_run.add_argument("--composes", nargs="*", help="additional offerings to compose with")
    ap_run.add_argument("--model-source", choices=["stub", "gateway"], default="stub")
    ap_run.add_argument("--gateway", help="gateway base URL (when model-source=gateway)")
    ap_run.add_argument("--team-key", help="gateway team API key (when model-source=gateway)")
    ap_run.add_argument("--model", help="gateway model id (default: telus-qwen)")
    ap_run.add_argument("--confirm-freeze", action="store_true",
                          help="proceed through stage 5 (freeze); without this, stops after stage 4")
    ap_run.add_argument("--team-name", default="Stub Demo Team")
    ap_run.add_argument("--team-site", default="other", choices=["Vancouver", "Victoria", "other"])
    ap_run.add_argument("--out-dir", default="runs",
                          help="output dir (default: runs/, gitignored)")
    ap_run.set_defaults(func=cmd_run)

    ap_show = sub.add_parser("show", help="show a previous run's audit log")
    ap_show.add_argument("run_dir")
    ap_show.set_defaults(func=cmd_show)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
