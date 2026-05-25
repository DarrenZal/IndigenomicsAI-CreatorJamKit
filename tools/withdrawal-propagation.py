#!/usr/bin/env python3
"""withdrawal-propagation — when a record is withdrawn, show what surfaces need to update.

A jam-day mentor tool. Reads a small dependency manifest (records + surfaces +
mentions) and outputs the propagation set for a withdrawn record.

Usage:
    python3 withdrawal-propagation.py <manifest.json> <withdrawn-record-id> [...more-ids]

Manifest shape:
    {
      "records": [
        {"record_id": "...", "kind": "..."}, ...
      ],
      "surfaces": [
        {"surface_id": "receipt-wall", "kind": "public-display", "shown_records": ["..."]},
        {"surface_id": "aggregate-summary", "kind": "summary", "uses_records": ["..."]},
        {"surface_id": "agentic-build-packet-X", "kind": "build-packet", "cleared_records": ["..."]},
        ...
      ],
      "downstream_summaries": [
        {"summary_id": "...", "rolls_up_from": ["surface_id"]}
      ]
    }

Output: for each withdrawn record, which surfaces show it (must remove/redact) and which
downstream summaries depend on those surfaces (must recompute).

Standard library only. Read-only.
"""
import argparse
import json
import sys
from pathlib import Path


def propagate(manifest: dict, withdrawn_ids: list) -> dict:
    surfaces = manifest.get("surfaces", [])
    downstream = manifest.get("downstream_summaries", [])

    actions_per_record = {}

    for wid in withdrawn_ids:
        affected_surfaces = []
        for s in surfaces:
            uses = (s.get("shown_records") or []) + (s.get("uses_records") or []) + (s.get("cleared_records") or [])
            if wid in uses:
                affected_surfaces.append(s.get("surface_id"))

        affected_downstream = []
        for d in downstream:
            if any(sid in (d.get("rolls_up_from") or []) for sid in affected_surfaces):
                affected_downstream.append(d.get("summary_id"))

        actions_per_record[wid] = {
            "surfaces_to_update": affected_surfaces,
            "downstream_summaries_to_recompute": affected_downstream,
        }

    return actions_per_record


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("manifest", help="path to manifest.json")
    parser.add_argument("withdrawn", nargs="+", help="withdrawn record_ids")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args(argv)

    path = Path(args.manifest)
    if not path.exists():
        print(f"error: manifest not found: {path}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON in manifest: {e}", file=sys.stderr)
        return 2

    result = propagate(manifest, args.withdrawn)

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"WITHDRAWAL PROPAGATION (manifest: {path.name})")
    print()

    for rec_id, actions in result.items():
        surfaces = actions["surfaces_to_update"]
        downstream = actions["downstream_summaries_to_recompute"]
        print(f"Withdrawn record: {rec_id}")
        if not surfaces and not downstream:
            print(f"  no surfaces or summaries reference this record — nothing to update")
        else:
            if surfaces:
                print(f"  surfaces to update ({len(surfaces)}):")
                for s in surfaces:
                    print(f"    - {s}")
            if downstream:
                print(f"  downstream summaries to recompute ({len(downstream)}):")
                for d in downstream:
                    print(f"    - {d}")
        print()

    print("BOUNDARY: this propagation lists which surfaces reference the withdrawn record(s)")
    print("based on the manifest. It does not auto-update anything. Humans execute the updates.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
