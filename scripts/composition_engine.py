#!/usr/bin/env python3
"""Tiny diagnostic composition engine for Creator Jam fixture JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ENGINE_NAME = "Creator Jam Composition Engine Prototype"
ENGINE_VERSION = "0.1.1"
RECORD_ID_KEYS = (
    "record_id",
    "id",
    "claim_id",
    "evidence_id",
    "witness_record_id",
    "witness_id",
    "receipt_id",
    "story_candidate_id",
    "output_id",
    "allocation_id",
    "transition_id",
)


def load_fixture(experiment_dir: Path, fixture_path: Path | None) -> tuple[Path, dict[str, Any]]:
    if fixture_path is None:
        fixture_paths = sorted((experiment_dir / "fixtures").glob("*.json"))
        if len(fixture_paths) != 1:
            raise SystemExit(
                f"Expected exactly one fixture JSON under {experiment_dir / 'fixtures'}, found {len(fixture_paths)}"
            )
        fixture_path = fixture_paths[0]

    with fixture_path.open("r", encoding="utf-8") as handle:
        return fixture_path, json.load(handle)


def transition_id(transition: dict[str, Any]) -> str:
    return str(transition.get("transition_id", "unknown-transition"))


def transition_disposition(transition: dict[str, Any]) -> str:
    review = transition.get("transition_review", {})
    if isinstance(review, dict) and review.get("composition_disposition"):
        return str(review["composition_disposition"])
    return str(transition.get("composition_disposition", "unknown"))


def transition_result(transition: dict[str, Any]) -> str:
    result = transition.get("result", {})
    return str(result.get("status", "unknown"))


def source_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    records = normalize_collection(fixture.get("source_records", []))
    allocation_record = fixture.get("untracked_allocation_record")
    if isinstance(allocation_record, dict):
        records.append(allocation_record)
    return dedupe_records(records)


def speech_act_transitions(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    transitions = normalize_collection(fixture.get("speech_act_transitions", []))
    singular_transition = fixture.get("speech_act_transition")
    if isinstance(singular_transition, dict):
        transitions.append(singular_transition)
    return dedupe_records(transitions)


def explicit_excluded_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    records = normalize_collection(fixture.get("excluded_records", []))
    composed = fixture.get("composed_outputs", {})
    if isinstance(composed, dict):
        records.extend(normalize_collection(composed.get("excluded_source_records", [])))
    return dedupe_records(records)


def excluded_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    records = explicit_excluded_records(fixture)
    known_ids = {record_id(item) for item in records}

    for record in source_records(fixture):
        rid = record_id(record)
        if rid in known_ids:
            continue
        if record.get("do_not_compute") is True or record.get("permission_state") == "refused":
            records.append(derived_exclusion_marker(record))
            known_ids.add(rid)

    return records


def composed_outputs(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = fixture.get("composed_outputs", [])
    if isinstance(outputs, list):
        return [item for item in outputs if isinstance(item, dict)]
    if isinstance(outputs, dict):
        normalized = []
        if "derived_from_transitions" in outputs or "output_id" in outputs or "story_candidate_id" in outputs:
            normalized.append(outputs)
        for item in outputs.values():
            for candidate in normalize_collection(item):
                if "derived_from_transitions" in candidate or "output_id" in candidate or "story_candidate_id" in candidate:
                    normalized.append(candidate)
        return dedupe_records(normalized)
    return []


def record_id(record: dict[str, Any]) -> str:
    for key in RECORD_ID_KEYS:
        if record.get(key):
            return str(record[key])
    return "unknown-record"


def ref_id(value: Any) -> str:
    if isinstance(value, dict):
        return record_id(value)
    if value is None:
        return ""
    return str(value)


def normalize_collection(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        if any(key in value for key in RECORD_ID_KEYS) or "transition_id" in value:
            return [value]
        records: list[dict[str, Any]] = []
        for item in value.values():
            records.extend(normalize_collection(item))
        return records
    return []


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for record in records:
        key = record_id(record)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def derived_exclusion_marker(record: dict[str, Any]) -> dict[str, Any]:
    reasons = []
    if record.get("permission_state") == "refused":
        reasons.append("permission_state refused")
    if record.get("do_not_compute") is True:
        reasons.append("do_not_compute true")
    if record.get("visibility_tier"):
        reasons.append(f"visibility_tier {record.get('visibility_tier')}")
    if record.get("share_policy"):
        reasons.append(f"share_policy {record.get('share_policy')}")

    prohibited = record.get("restrictions", [])
    if not isinstance(prohibited, list):
        prohibited = []

    return {
        "record_id": record_id(record),
        "excluded_reason": reasons,
        "allowed_reference": record.get("summary") or record.get("source_summary") or record.get("public_summary", ""),
        "prohibited_actions": prohibited,
        "engine_derived_marker": True,
    }


def speech_act_label(record: dict[str, Any]) -> str:
    for key in ("speech_act", "record_type", "allocation_type", "claim_type", "event_type"):
        if record.get(key):
            return str(record[key])
    return ""


def check_source_records_have_explicit_marker(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "code": "source_records_explicit_or_inferred",
            "status": "warn",
            "detail": "No source records were found to check.",
            "records": [],
        }

    missing = [record_id(record) for record in records if "explicit_or_inferred" not in record]
    return {
        "code": "source_records_explicit_or_inferred",
        "status": "ok" if not missing else "warn",
        "detail": "All source records carry explicit_or_inferred." if not missing else "Missing explicit_or_inferred.",
        "records": missing,
    }


def check_transition_ai_receipts(transitions: list[dict[str, Any]]) -> dict[str, Any]:
    if not transitions:
        return {
            "code": "transition_ai_use_receipts",
            "status": "warn",
            "detail": "No speech-act transitions were found to check.",
            "transitions": [],
        }

    missing = [transition_id(item) for item in transitions if "ai_use_receipt" not in item]
    return {
        "code": "transition_ai_use_receipts",
        "status": "ok" if not missing else "warn",
        "detail": "All transitions include AI-use receipts." if not missing else "Some transitions lack AI-use receipts.",
        "transitions": missing,
    }


def check_derived_from_transitions(fixture: dict[str, Any], transitions: list[dict[str, Any]]) -> dict[str, Any]:
    known = {transition_id(item) for item in transitions}
    missing_outputs = []
    unknown_refs = []
    outputs = composed_outputs(fixture)

    if not outputs:
        return {
            "code": "derived_from_transitions",
            "status": "ok",
            "detail": "No composed outputs were found to check.",
            "missing_outputs": [],
            "unknown_refs": [],
        }

    for output in outputs:
        output_id = record_id(output)
        refs = output.get("derived_from_transitions", [])
        if not refs:
            missing_outputs.append(output_id)
            continue
        for ref in refs:
            if ref not in known:
                unknown_refs.append({"output_id": output_id, "transition_id": ref})

    status = "ok" if not missing_outputs and not unknown_refs else "warn"
    return {
        "code": "derived_from_transitions",
        "status": status,
        "detail": "Composed outputs point to known transition IDs." if status == "ok" else "Some output lineage is incomplete.",
        "missing_outputs": missing_outputs,
        "unknown_refs": unknown_refs,
    }


def check_do_not_compute_exclusions(
    records: list[dict[str, Any]], excluded: list[dict[str, Any]], transitions: list[dict[str, Any]]
) -> dict[str, Any]:
    excluded_ids = {record_id(item) for item in excluded}
    missing = []
    represented_by_blocked_transition = []
    for record in records:
        if record.get("do_not_compute") is not True or record_id(record) in excluded_ids:
            continue
        if blocked_transition_names_do_not_compute(transitions):
            represented_by_blocked_transition.append(record_id(record))
        else:
            missing.append(record_id(record))

    if missing:
        status = "block"
        detail = "A do_not_compute record is not represented in excluded records or blocked transition obstructions."
    elif represented_by_blocked_transition:
        status = "warn"
        detail = "Some do_not_compute source records are represented by blocked transition obstructions, but not by explicit excluded records."
    else:
        status = "ok"
        detail = "do_not_compute source records are represented as excluded records."

    return {
        "code": "do_not_compute_exclusions",
        "status": status,
        "detail": detail,
        "records": missing,
        "represented_by_blocked_transition": represented_by_blocked_transition,
    }


def check_authority_markers(transitions: list[dict[str, Any]]) -> dict[str, Any]:
    if not transitions:
        return {
            "code": "speech_act_authority_markers",
            "status": "warn",
            "detail": "No speech-act transitions were found to check.",
            "warnings": [],
        }

    warnings = []
    for item in transitions:
        from_act = item.get("from_speech_act")
        to_act = item.get("to_speech_act")
        if from_act == "dream" and to_act == "commitment" and "authority_record" not in item:
            warnings.append({"transition_id": transition_id(item), "missing": "authority_record"})
        if from_act in {"offer", "promise"} and to_act == "commitment" and "contributor_consent_check" not in item:
            warnings.append({"transition_id": transition_id(item), "missing": "contributor_consent_check"})

    return {
        "code": "speech_act_authority_markers",
        "status": "ok" if not warnings else "warn",
        "detail": "Load-bearing speech-act transitions carry authority markers."
        if not warnings
        else "Some load-bearing speech-act transitions lack authority markers.",
        "warnings": warnings,
    }


def blocked_transition_names_do_not_compute(transitions: list[dict[str, Any]]) -> bool:
    for item in transitions:
        if transition_disposition(item) not in {"blocked", "non_composable"} and transition_result(item) != "blocked":
            continue
        obstruction_text = " ".join(str(value) for value in item.get("boundary_obstructions", []))
        if "do_not_compute" in obstruction_text:
            return True
    return False


def build_trace(experiment_dir: Path, fixture_path: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    records = source_records(fixture)
    transitions = speech_act_transitions(fixture)
    explicit_excluded = explicit_excluded_records(fixture)
    excluded = excluded_records(fixture)
    outputs = composed_outputs(fixture)

    hard_checks = [
        check_source_records_have_explicit_marker(records),
        check_transition_ai_receipts(transitions),
        check_derived_from_transitions(fixture, transitions),
        check_do_not_compute_exclusions(records, explicit_excluded, transitions),
        check_authority_markers(transitions),
    ]

    blocked_transitions = [
        {
            "transition_id": transition_id(item),
            "from_speech_act": item.get("from_speech_act"),
            "to_speech_act": item.get("to_speech_act"),
            "composition_disposition": transition_disposition(item),
            "result_status": transition_result(item),
            "next_action": item.get("result", {}).get("next_action"),
            "boundary_obstructions": item.get("boundary_obstructions", []),
        }
        for item in transitions
        if transition_disposition(item) in {"blocked", "non_composable", "review_required"}
        or transition_result(item) in {"blocked", "review_required", "returned"}
    ]

    return {
        "engine": {
            "name": ENGINE_NAME,
            "version": ENGINE_VERSION,
            "generated_at": fixture.get("created_at", "unknown"),
        },
        "input": {
            "experiment_dir": str(experiment_dir),
            "fixture_path": str(fixture_path),
        },
        "fixture_id": fixture.get("fixture_id"),
        "composition_attempt": fixture.get("composition_attempt", {}),
        "records": [
            {
                "record_id": record_id(item),
                "speech_act": speech_act_label(item),
                "explicit_or_inferred": item.get("explicit_or_inferred"),
                "visibility_tier": item.get("visibility_tier"),
                "permission_state": item.get("permission_state"),
                "do_not_compute": item.get("do_not_compute"),
            }
            for item in records
        ],
        "transitions": [
            {
                "transition_id": transition_id(item),
                "from_speech_act": item.get("from_speech_act"),
                "to_speech_act": item.get("to_speech_act"),
                "source_record": ref_id(item.get("source_record")),
                "target_record": ref_id(item.get("target_record")),
                "composition_disposition": transition_disposition(item),
                "result_status": transition_result(item),
                "has_ai_use_receipt": "ai_use_receipt" in item,
                "has_authority_record": "authority_record" in item,
                "has_contributor_consent_check": "contributor_consent_check" in item,
                "explicit_contributor_authority": "authority_record" in item
                or "contributor_consent_check" in item,
            }
            for item in transitions
        ],
        "hard_checks": hard_checks,
        "blocked_transitions": blocked_transitions,
        "excluded_records": excluded,
        "composed_outputs": outputs,
        "coherence_vector": fixture.get("coherence_vector", {}),
        "not_established": fixture.get("not_established", []),
        "not_run": fixture.get("not_run", []),
        "human_review_prompt": "Review the trace for authority gaps, boundary laundering, category drift, missing excluded records, and whether blocked outputs are explained as clearly as composed outputs.",
    }


def md_table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value) if value is not None else "" for value in values) + " |"


def md_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def md_join(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def render_report(trace: dict[str, Any]) -> str:
    generated_at = str(trace.get("engine", {}).get("generated_at", "unknown"))
    lines = [
        "---",
        "doc_kind: composition-engine-report",
        "status: generated",
        "visibility: public_sample",
        f"last_updated: {generated_at}",
        "---",
        "",
        "# Composition Engine Diagnostic Report",
        "",
        f"Fixture: `{trace.get('fixture_id')}`",
        f"Engine: `{ENGINE_NAME}` `{ENGINE_VERSION}`",
        "",
        "This report is diagnostic output for human review. It is not a verdict, score, approval, authority grant, or display approval.",
        "",
        "## Composition Attempt",
        "",
    ]

    attempt = trace.get("composition_attempt") or {}
    for key in ["attempt_id", "purpose", "composition_shape", "composition_disposition", "review_date"]:
        if key in attempt:
            lines.append(f"- `{key}`: {attempt[key]}")

    lines.extend(["", "## Source Records", "", md_table_row(["Record", "Speech Act", "Explicit Or Inferred", "Visibility", "Permission", "do_not_compute"]), md_table_row(["---", "---", "---", "---", "---", "---"])])
    for record in trace["records"]:
        lines.append(
            md_table_row(
                [
                    f"`{record['record_id']}`",
                    f"`{md_value(record.get('speech_act'))}`",
                    f"`{md_value(record.get('explicit_or_inferred'))}`",
                    f"`{md_value(record.get('visibility_tier'))}`",
                    f"`{md_value(record.get('permission_state'))}`",
                    f"`{md_value(record.get('do_not_compute'))}`",
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Speech-Act Transitions",
            "",
            md_table_row(
                [
                    "Transition",
                    "From",
                    "To",
                    "Disposition",
                    "Result",
                    "AI Receipt",
                    "Authority Record",
                    "Contributor Consent",
                    "Explicit Contributor Authority",
                ]
            ),
            md_table_row(["---", "---", "---", "---", "---", "---", "---", "---", "---"]),
        ]
    )
    for item in trace["transitions"]:
        lines.append(
            md_table_row(
                [
                    f"`{item['transition_id']}`",
                    f"`{item.get('from_speech_act')}`",
                    f"`{item.get('to_speech_act')}`",
                    f"`{item.get('composition_disposition')}`",
                    f"`{item.get('result_status')}`",
                    f"`{md_value(item.get('has_ai_use_receipt'))}`",
                    f"`{md_value(item.get('has_authority_record'))}`",
                    f"`{md_value(item.get('has_contributor_consent_check'))}`",
                    f"`{md_value(item.get('explicit_contributor_authority'))}`",
                ]
            )
        )

    lines.extend(["", "## Hard Checks", "", md_table_row(["Check", "Status", "Detail"]), md_table_row(["---", "---", "---"])])
    for check in trace["hard_checks"]:
        lines.append(md_table_row([f"`{check['code']}`", f"`{check['status']}`", check["detail"]]))

    lines.extend(["", "## Blocked Or Returned Items", ""])
    if trace["blocked_transitions"]:
        lines.extend([md_table_row(["Transition", "Reason", "Next Action"]), md_table_row(["---", "---", "---"])])
        for item in trace["blocked_transitions"]:
            reason = "; ".join(item.get("boundary_obstructions") or [])
            lines.append(md_table_row([f"`{item['transition_id']}`", reason, item.get("next_action")]))
    else:
        lines.append("No blocked transitions were found in the fixture trace.")

    lines.extend(["", "## Excluded Records", ""])
    excluded = trace.get("excluded_records", [])
    if excluded:
        lines.extend([md_table_row(["Record", "Reason", "Prohibited Actions"]), md_table_row(["---", "---", "---"])])
        for item in excluded:
            lines.append(
                md_table_row(
                    [
                        f"`{record_id(item)}`",
                        md_join(item.get("excluded_reason") or item.get("exclusion_reason")),
                        md_join(item.get("prohibited_actions") or item.get("restrictions")),
                    ]
                )
            )
    else:
        lines.append("No excluded records were found in the fixture trace.")

    lines.extend(
        [
            "",
            "## Coherence Vector",
            "",
            "These states are preserved from the fixture. The v0.1.x engine does not independently validate coherence-vector claims.",
            "",
            md_table_row(["Dimension", "State", "Note"]),
            md_table_row(["---", "---", "---"]),
        ]
    )
    coherence_vector = trace.get("coherence_vector") or {}
    if not coherence_vector:
        lines.append(md_table_row(["", "", "No fixture-authored coherence vector was found."]))
    for dimension, payload in coherence_vector.items():
        if isinstance(payload, dict):
            lines.append(md_table_row([f"`{dimension}`", f"`{payload.get('state')}`", payload.get("note", "")]))

    lines.extend(["", "## Not Established", ""])
    for item in trace.get("not_established", []):
        lines.append(f"- {item}")

    lines.extend(["", "## Not Run", ""])
    for item in trace.get("not_run", []):
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Human Review Prompt",
            "",
            trace["human_review_prompt"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate diagnostic composition trace/report from a fixture.")
    parser.add_argument("experiment_dir", type=Path, help="Experiment directory containing fixtures/")
    parser.add_argument("--fixture", type=Path, default=None, help="Optional explicit fixture JSON path")
    parser.add_argument("--write", action="store_true", help="Write reports/composition-engine-report.md and traces/composition-trace.json")
    args = parser.parse_args()

    experiment_dir = args.experiment_dir.resolve()
    fixture_path, fixture = load_fixture(experiment_dir, args.fixture)
    trace = build_trace(experiment_dir, fixture_path, fixture)
    report = render_report(trace)

    if args.write:
        reports_dir = experiment_dir / "reports"
        traces_dir = experiment_dir / "traces"
        reports_dir.mkdir(parents=True, exist_ok=True)
        traces_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "composition-engine-report.md").write_text(report, encoding="utf-8")
        (traces_dir / "composition-trace.json").write_text(json.dumps(trace, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {reports_dir / 'composition-engine-report.md'}")
        print(f"Wrote {traces_dir / 'composition-trace.json'}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
