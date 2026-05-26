#!/usr/bin/env python3
"""agent_composer.py — cross-spec composition proposal generator.

Reads published wall records + their build packets from a persistent_root
and proposes COMPOSED specs: "if these N tools were combined, here's the
v0 composed spec." Each proposal is a markdown document the operator
can promote to a real composed spec for a follow-up build attempt.

v0 scope:
  - Single-LLM-call per N-tuple (not autonomous full build)
  - Proposes composition AT the kit's coordination-protocol layer
    (composition_propose semantics from coordination-protocol-v0)
  - Honors the kit's anti-overclaim discipline
  - Output is PROPOSAL, not build — operator decides whether to add as
    a new spec in a future run

Composition strategy v0:
  - Cluster published specs by the same heuristic as coherence_synthesizer
    (WITNESSING / ECONOMIC-FLOWS / CLAIMS / ASPIRATIONS / BIOREGIONAL)
  - For each cluster with >= 2 published specs, propose ONE composition
  - For cross-cluster pairs that semantically pair (e.g. WITNESSING +
    CLAIMS), propose ONE composition each

Bounded:
  - Max 8 proposals per run (avoid combinatorial explosion)
  - Each call uses temperature=0.3 for slight diversity
  - One-shot retry on transient gateway failures

Discipline:
  - Refusal-as-record: the model can output {"refusal": "..."} if it
    can't honestly propose a composition (e.g., if the input specs
    are incompatible). Recorded as a "proposal-refused" outcome.
  - Composition does NOT execute or build anything — strictly proposal
  - Standard closing-boundary appended to each proposal
  - No autonomous publishing — operator review required before any
    composed spec gets added to ORCHESTRATOR_CANDIDATE_SPECS

Usage:
  python3 scripts/jam/agent_composer.py compose \\
      --persistent-root <path> \\
      --gateway http://localhost:8000 \\
      --model telus-gemma \\
      [--team-key KEY  | env TELUS_TEAM_KEY] \\
      [--max-proposals 8] \\
      --out-dir <path>
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jam.coherence_synthesizer import (  # noqa: E402
    cluster_for_vision,
    collect_wall_records,
    collect_build_packets,
)
from jam.spec_drafting_loop import _try_parse_json  # noqa: E402


COMPOSER_SYSTEM = (
    "You are a Spec Composition Proposer for the IndigenomicsAI Creator "
    "Jam. You read 2-3 published witness records describing tools that "
    "were built tonight, and propose a v0 COMPOSED spec — a description "
    "of what a new tool that integrates these would look like.\n\n"
    "INPUT: a JSON payload with `components` (a list of 2-3 published "
    "witness summaries, each with team_spec.title, vision, spec, "
    "build_target, acceptance_criteria) + `composition_intent` (one of "
    "'cluster-internal' or 'cross-cluster' + cluster labels).\n\n"
    "OUTPUT FORMAT — STRICT:\n"
    "Reply with ONE JSON object, no prose, no markdown, no fence. "
    "Fields:\n"
    "  - title: string (short, descriptive — names the composed thing)\n"
    "  - vision: string (1-3 sentences: what would the composed thing "
    "BE — not how it's built)\n"
    "  - spec: string (concrete description of the v0 composed build: "
    "what surfaces, what flows between component pieces, what gets "
    "preserved from each component)\n"
    "  - build_target: string (e.g. 'single-file Python CLI', "
    "'static HTML/JS', 'multi-file Python package')\n"
    "  - acceptance_criteria_draft: array of strings (5-7 specific, "
    "testable criteria for the COMPOSED build)\n"
    "  - composition_seams: array of strings (where the component "
    "pieces touch — e.g. 'witness records from spec-a flow into "
    "claim-evidence checker of spec-b')\n"
    "  - composition_caveats: array of strings (what about combining "
    "these specs is risky, what discipline would need to be "
    "transferred, what would be lost in composition)\n"
    "  - refusal_path_used: boolean (false unless refusing)\n\n"
    "REFUSAL: if the components don't honestly compose (e.g. they "
    "operate on incompatible domains, OR composition would require "
    "cultural authorization the kit doesn't hold, OR the boundaries "
    "of one component would be violated by composing it with another), "
    "output ONLY: {\"refusal\": \"<one-line reason>\"} — do not "
    "fabricate a composition.\n\n"
    "DISCIPLINE (load-bearing):\n"
    "- Use the kit's verb discipline (observed, witnessed, recorded, "
    "surfaced, held). NEVER use 'certified', 'approved', 'authorized', "
    "'validated', 'legitimate', 'official', 'successful' as summary "
    "judgment, or 'failed' as summary judgment.\n"
    "- Composed specs are PROPOSALS, not builds. Do not claim the "
    "composed thing will work — only what it would BE if built.\n"
    "- Honor each component's boundaries: if component A says X is "
    "marker-only, the composition must NOT relax that boundary.\n"
    "- 'composition_seams' should be specific — name the interface "
    "between components, not abstract handwaving.\n"
    "- 'composition_caveats' is the honest part — what would make "
    "this composition fail. Don't skip it.\n"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# --------------------------------------------------------------------- #
# Component discovery — pair published wall records with their packets  #
# --------------------------------------------------------------------- #

KNOWN_SPEC_STEMS = [
    "witness-record-interop-profile",
    "claims-evidence-coherence-report",
    "commitment-pool-route-diagnostic",
    "dream-to-fulfillment-board",
    "receipt-wall-story-gallery",
    "flow-funding-frontier-map",
    "bioregional-mapping-layer-board",
    "spec-composer-bundle-board",
    "living-atlas-coherence-packet",
    "bioregional-insights-briefing",
    "sensor-to-receipt-pipeline",
    "untracked-allocation-ledger",
    "risk-insurance-coherence-map",
]


def _infer_spec_id_from_wall_name(name: str) -> str:
    """Wall filenames: <ts>-team-<team-id>-<hash>.md, where team-id
    usually contains the spec_id. Look for known stems in the name."""
    for stem in KNOWN_SPEC_STEMS:
        if stem in name:
            return stem
    return ""


def discover_components(persistent_root: Path) -> List[Dict[str, Any]]:
    """Walk persistent_root for published wall records + their packets.
    Returns a list of {spec_id, cluster, title, vision, spec,
    build_target, acceptance_criteria}.

    Only returns components that have BOTH a wall record AND a build
    packet — those are the published specs the orchestrator successfully
    drove through the chain.
    """
    wall = collect_wall_records(persistent_root)
    packets = collect_build_packets(persistent_root)
    # Index packets by spec_id (best-effort; spec_id inferred from path
    # by collect_build_packets; flat dict shape from coherence_synthesizer)
    pkt_by_spec: Dict[str, Dict[str, Any]] = {}
    for p in packets:
        sid = p.get("spec_id")
        if sid and sid not in pkt_by_spec:
            pkt_by_spec[sid] = p
    components = []
    seen_specs = set()
    for w in wall:
        sid = _infer_spec_id_from_wall_name(w.get("name", ""))
        if not sid or sid in seen_specs:
            continue
        seen_specs.add(sid)
        pkt = pkt_by_spec.get(sid)
        if not pkt:
            continue
        # coherence_synthesizer returns FLAT dicts with vision/title/
        # build_target already extracted from team_spec.
        vision = pkt.get("vision", "") or ""
        cluster = cluster_for_vision(vision)
        components.append({
            "spec_id": sid,
            "cluster": cluster,
            "title": pkt.get("title") or sid,
            "vision": vision[:600],
            "spec": (pkt.get("spec") or "")[:600],
            "build_target": pkt.get("build_target", "") or "",
            "acceptance_criteria": (pkt.get("acceptance_criteria") or [])[:6],
        })
    return components


# --------------------------------------------------------------------- #
# Composition pair selection — heuristic                                #
# --------------------------------------------------------------------- #

# Cross-cluster pairs that often compose well (operator-curated, v0)
CROSS_CLUSTER_AFFINITIES: List[Tuple[str, str]] = [
    ("WITNESSING", "CLAIMS"),
    ("WITNESSING", "ECONOMIC-FLOWS"),
    ("CLAIMS", "ECONOMIC-FLOWS"),
    ("BIOREGIONAL", "WITNESSING"),
    ("ASPIRATIONS", "ECONOMIC-FLOWS"),
]


def pick_composition_tuples(
    components: List[Dict[str, Any]],
    max_proposals: int = 8,
) -> List[Tuple[str, List[Dict[str, Any]]]]:
    """Choose component tuples to propose compositions over. Returns a
    list of (intent, components) pairs, where intent is one of
    'cluster-internal' or 'cross-cluster'.

    v0 heuristic:
      - Cluster-internal: for each cluster with >= 2 components, pick
        ONE pair (first two by spec_id sort). Stops adding once we hit
        max_proposals.
      - Cross-cluster: for each affinity pair, pick ONE composition
        (one component from each cluster, first by spec_id sort).
    """
    by_cluster: Dict[str, List[Dict[str, Any]]] = {}
    for c in components:
        by_cluster.setdefault(c["cluster"], []).append(c)
    for k in by_cluster:
        by_cluster[k].sort(key=lambda c: c["spec_id"])

    tuples: List[Tuple[str, List[Dict[str, Any]]]] = []

    # Cluster-internal compositions first
    for cluster_name in sorted(by_cluster.keys()):
        comps = by_cluster[cluster_name]
        if len(comps) >= 2:
            tuples.append((
                f"cluster-internal:{cluster_name}",
                comps[:2],
            ))
        if len(tuples) >= max_proposals:
            return tuples

    # Cross-cluster compositions
    for a, b in CROSS_CLUSTER_AFFINITIES:
        if a in by_cluster and b in by_cluster:
            tuples.append((
                f"cross-cluster:{a}+{b}",
                [by_cluster[a][0], by_cluster[b][0]],
            ))
            if len(tuples) >= max_proposals:
                return tuples

    return tuples


# --------------------------------------------------------------------- #
# Composer gateway call                                                 #
# --------------------------------------------------------------------- #

def call_composer_gateway(
    base_url: str,
    team_key: str,
    model: str,
    payload: Dict[str, Any],
    timeout: int = 120,
) -> Dict[str, Any]:
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": COMPOSER_SYSTEM},
            {"role": "user", "content": json.dumps(payload)},
        ],
        "temperature": 0.3,  # slight diversity for proposals
    }).encode()

    last_err = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(
                f"{base_url.rstrip('/')}/v1/chat/completions",
                data=body,
                headers={
                    "Authorization": f"Bearer {team_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
            break
        except Exception as e:
            last_err = e
            if attempt == 2:
                raise RuntimeError(f"composer gateway failed: {e}")
            import time
            time.sleep(2)

    content = data["choices"][0]["message"]["content"]
    parsed = _try_parse_json(content)
    return {
        "raw_content": content,
        "parsed": parsed,
        "model_label": data.get("model", model),
        "seed": (data.get("id") or "")[:12],
    }


# --------------------------------------------------------------------- #
# Proposal rendering                                                    #
# --------------------------------------------------------------------- #

def render_proposal_md(
    intent: str,
    components: List[Dict[str, Any]],
    parsed: Optional[Dict[str, Any]],
    raw_content: str,
    model_label: str,
) -> str:
    component_lines = []
    for c in components:
        component_lines += [
            f"### `{c['spec_id']}` (cluster: {c['cluster']})",
            "",
            f"- title: {c['title']}",
            f"- vision: {c['vision']}",
            f"- build_target: {c['build_target']}",
            "",
        ]
    component_block = "\n".join(component_lines)

    if parsed is None:
        body = (
            "## Composition (parse failure)\n\n"
            "The composer model output did not parse as JSON. Raw "
            "content preserved below for operator review.\n\n"
            f"```\n{raw_content[:2000]}\n```\n"
        )
    elif "refusal" in parsed and isinstance(parsed["refusal"], str):
        body = (
            "## Composition refused (proposal-refused-as-record)\n\n"
            f"The composer model refused to propose this composition. "
            f"Reason recorded:\n\n"
            f"> {parsed['refusal']}\n\n"
            f"This is refusal-as-record — the model declined to "
            f"fabricate a composition where one would not honestly hold.\n"
        )
    else:
        body = "## Proposed composition\n\n"
        body += f"### Title\n\n{parsed.get('title', '(no title)')}\n\n"
        body += f"### Vision\n\n{parsed.get('vision', '(no vision)')}\n\n"
        body += f"### Spec\n\n{parsed.get('spec', '(no spec)')}\n\n"
        body += (f"### Build target\n\n"
                  f"`{parsed.get('build_target', '(unspecified)')}`\n\n")
        ac = parsed.get("acceptance_criteria_draft", [])
        if isinstance(ac, list) and ac:
            body += "### Acceptance criteria (draft)\n\n"
            for item in ac:
                body += f"- {item}\n"
            body += "\n"
        seams = parsed.get("composition_seams", [])
        if isinstance(seams, list) and seams:
            body += "### Composition seams\n\n"
            for s in seams:
                body += f"- {s}\n"
            body += "\n"
        caveats = parsed.get("composition_caveats", [])
        if isinstance(caveats, list) and caveats:
            body += "### Composition caveats\n\n"
            for c in caveats:
                body += f"- {c}\n"
            body += "\n"

    return (
        f"# Composition Proposal — {intent}\n\n"
        f"- generated: {now_iso()}\n"
        f"- composer model: {model_label}\n"
        f"- intent: {intent}\n"
        f"- components: {len(components)}\n\n"
        f"## Components composed\n\n{component_block}"
        f"{body}\n"
        f"## Boundary\n\n"
        f"This is a PROPOSAL. It is NOT a build, not authority, not "
        f"approval. Operator review is required before any composed "
        f"spec is added to the kit's spec menu. The receipt statement "
        f"on each component witness record still holds; this proposal "
        f"does not relax those receipts.\n"
    )


# --------------------------------------------------------------------- #
# Main entrypoint                                                       #
# --------------------------------------------------------------------- #

def compose(
    persistent_root: Path,
    gateway: str,
    team_key: Optional[str],
    model: str,
    out_dir: Path,
    max_proposals: int = 8,
) -> Dict[str, Any]:
    """Returns a summary dict; writes proposal markdown files to out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    components = discover_components(persistent_root)
    if len(components) < 2:
        # Nothing to compose; write a stub
        stub = out_dir / "no-compositions.md"
        stub.write_text(
            "# No compositions\n\n"
            f"Fewer than 2 published components found in {persistent_root}. "
            f"Composition requires at least 2 published specs to operate.\n"
        )
        return {"proposals_attempted": 0, "components_found": len(components)}

    tuples = pick_composition_tuples(components, max_proposals=max_proposals)
    if not tuples:
        return {"proposals_attempted": 0,
                 "components_found": len(components)}

    results = []
    for i, (intent, comps) in enumerate(tuples):
        proposal_id = f"{i:02d}-{intent.replace(':', '-').replace('+', '-')}"
        out_path = out_dir / f"proposal-{proposal_id}.md"
        payload = {
            "composition_intent": intent,
            "components": [
                {k: c[k] for k in ("spec_id", "cluster", "title",
                                     "vision", "spec", "build_target",
                                     "acceptance_criteria")}
                for c in comps
            ],
        }
        try:
            r = call_composer_gateway(gateway, team_key, model, payload)
            md = render_proposal_md(
                intent, comps, r.get("parsed"),
                r.get("raw_content", ""), r.get("model_label", model),
            )
            results.append({
                "proposal_id": proposal_id,
                "intent": intent,
                "components": [c["spec_id"] for c in comps],
                "outcome": (
                    "refused"
                    if isinstance(r.get("parsed"), dict)
                       and "refusal" in r["parsed"]
                    else "proposed"
                ),
                "path": str(out_path),
            })
        except Exception as e:
            md = (
                f"# Composition Proposal — {intent}\n\n"
                f"## Gateway error\n\n{e!s}\n"
            )
            results.append({
                "proposal_id": proposal_id,
                "intent": intent,
                "components": [c["spec_id"] for c in comps],
                "outcome": "gateway-error",
                "path": str(out_path),
                "error": str(e)[:300],
            })
        out_path.write_text(md)

    # Summary index
    index_md = "# Composition Proposals — Index\n\n"
    index_md += f"- generated: {now_iso()}\n"
    index_md += f"- components found: {len(components)}\n"
    index_md += f"- proposals attempted: {len(results)}\n\n"
    for r in results:
        components_str = ", ".join(f"`{c}`" for c in r["components"])
        index_md += (f"- **{r['proposal_id']}** ({r['outcome']}) — "
                       f"{components_str}\n")
    (out_dir / "index.md").write_text(index_md)

    return {
        "proposals_attempted": len(results),
        "components_found": len(components),
        "results": results,
    }


# --------------------------------------------------------------------- #
# CLI                                                                   #
# --------------------------------------------------------------------- #

def cmd_compose(args):
    persistent_root = Path(args.persistent_root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser()
    team_key = args.team_key or os.environ.get("TELUS_TEAM_KEY")
    if not team_key:
        raise SystemExit(
            "team key required via --team-key or TELUS_TEAM_KEY env"
        )
    summary = compose(
        persistent_root=persistent_root,
        gateway=args.gateway,
        team_key=team_key,
        model=args.model,
        out_dir=out_dir,
        max_proposals=args.max_proposals,
    )
    print(f"compositions → {out_dir}")
    print(f"  proposals attempted: {summary['proposals_attempted']}")
    print(f"  components found: {summary['components_found']}")


def main():
    ap = argparse.ArgumentParser(prog="agent_composer.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    apc = sub.add_parser("compose")
    apc.add_argument("--persistent-root", required=True)
    apc.add_argument("--gateway", required=True)
    apc.add_argument("--model", default="telus-gemma")
    apc.add_argument("--team-key")
    apc.add_argument("--out-dir", required=True)
    apc.add_argument("--max-proposals", type=int, default=8)
    apc.set_defaults(func=cmd_compose)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
