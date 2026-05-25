#!/usr/bin/env python3
"""composition-merger — merge two team submissions into a candidate bundle.

A jam-day mentor tool. Take two team-submission-v0 JSON files and produce a
candidate-bundle JSON that shows shared offerings, conflicting boundaries,
intersected consent, and combined acceptance criteria. Output flags every
conflict and never silently merges incompatible records.

Usage:
    python3 composition-merger.py <submission-a.json> <submission-b.json> [--out bundle.json]

Standard library only. Read-only on inputs.
"""
import argparse
import json
import sys
from pathlib import Path


def intersect_scope(a: str, b: str, order=["none", "spoken-only", "partial", "whole"]) -> str:
    """Return the more restrictive of two scopes (lower index wins)."""
    if a not in order: return a  # unknown, preserve
    if b not in order: return b
    return order[min(order.index(a), order.index(b))]


def merge_two(sub_a: dict, sub_b: dict) -> dict:
    a_team = sub_a.get("team", {})
    b_team = sub_b.get("team", {})

    # Combine offerings — preserve provenance per offering
    offerings_a = sub_a.get("source_offerings", [])
    offerings_b = sub_b.get("source_offerings", [])
    all_offerings = []
    for o in offerings_a:
        all_offerings.append({**o, "_from_team": a_team.get("id") or a_team.get("name")})
    for o in offerings_b:
        all_offerings.append({**o, "_from_team": b_team.get("id") or b_team.get("name")})

    # Boundaries — UNION namespaced by team (boundaries compose by adding constraints, never relaxing)
    # Two teams can each have a "b1" — they are DIFFERENT boundaries; preserve both.
    a_team_id = a_team.get("id") or a_team.get("name") or "team-a"
    b_team_id = b_team.get("id") or b_team.get("name") or "team-b"
    all_boundaries = []
    for b in sub_a.get("boundaries", []):
        b_copy = dict(b)
        b_copy["_from_team"] = a_team_id
        b_copy["id"] = f"{a_team_id}::{b.get('id') or b.get('label', 'unnamed')}"
        all_boundaries.append(b_copy)
    for b in sub_b.get("boundaries", []):
        b_copy = dict(b)
        b_copy["_from_team"] = b_team_id
        b_copy["id"] = f"{b_team_id}::{b.get('id') or b.get('label', 'unnamed')}"
        all_boundaries.append(b_copy)

    # Authorization — INTERSECT (most restrictive wins)
    a_auth = sub_a.get("authorization", {}) or {}
    b_auth = sub_b.get("authorization", {}) or {}
    intersected_auth = {
        "visible_to_facilitators": bool(a_auth.get("visible_to_facilitators")) and bool(b_auth.get("visible_to_facilitators")),
        "display_scope": intersect_scope(a_auth.get("display_scope", "none"), b_auth.get("display_scope", "none")),
        "ai_input_scope": intersect_scope(a_auth.get("ai_input_scope", "none"), b_auth.get("ai_input_scope", "none"),
                                          order=["none", "partial", "whole"]),
        "reuse_scope": "ask-first",  # composition forces re-ask
        "authorization_notes": "composed: both teams must re-confirm before any build attempt or display",
    }

    # Conflicts to surface
    conflicts = []
    if a_auth.get("ai_input_scope") != b_auth.get("ai_input_scope"):
        conflicts.append({
            "kind": "ai_input_scope_mismatch",
            "team_a_value": a_auth.get("ai_input_scope"),
            "team_b_value": b_auth.get("ai_input_scope"),
            "resolution": "intersected to most restrictive: " + intersected_auth["ai_input_scope"],
        })
    if a_auth.get("display_scope") != b_auth.get("display_scope"):
        conflicts.append({
            "kind": "display_scope_mismatch",
            "team_a_value": a_auth.get("display_scope"),
            "team_b_value": b_auth.get("display_scope"),
            "resolution": "intersected to most restrictive: " + intersected_auth["display_scope"],
        })

    # If either team is not in 'frozen' state, the bundle cannot be used
    a_frozen = (sub_a.get("freeze", {}) or {}).get("status") == "frozen"
    b_frozen = (sub_b.get("freeze", {}) or {}).get("status") == "frozen"

    bundle = {
        "bundle_version": "v0",
        "bundle_id": f"composed-{a_team.get('id', 'a')}-with-{b_team.get('id', 'b')}",
        "composed_from": [sub_a.get("submission_id"), sub_b.get("submission_id")],
        "teams": [a_team, b_team],
        "combined_offerings": all_offerings,
        "combined_boundaries": all_boundaries,
        "intersected_authorization": intersected_auth,
        "conflicts_surfaced": conflicts,
        "bundle_status": "candidate" if (a_frozen and b_frozen) else "needs-re-freeze",
        "freeze_note": "each team must re-confirm their offerings + boundaries in the composed context",
        "boundary": "This bundle is a CANDIDATE composition. It has not been frozen for build. Both teams must re-confirm before any build attempt runs against this bundle.",
    }
    return bundle


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("a", help="team-submission-v0 JSON from team A")
    parser.add_argument("b", help="team-submission-v0 JSON from team B")
    parser.add_argument("--out", help="write bundle JSON to this path (else stdout)")
    args = parser.parse_args(argv)

    def load(p):
        path = Path(p)
        if not path.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)
        return json.loads(path.read_text(encoding="utf-8"))

    sub_a = load(args.a)
    sub_b = load(args.b)
    bundle = merge_two(sub_a, sub_b)

    if args.out:
        Path(args.out).write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        print(f"wrote candidate bundle: {args.out}")
        print(f"  status: {bundle['bundle_status']}")
        print(f"  conflicts surfaced: {len(bundle['conflicts_surfaced'])}")
    else:
        print(json.dumps(bundle, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
