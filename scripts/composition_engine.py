#!/usr/bin/env python3
"""Tiny diagnostic composition engine for Creator Jam fixture JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ENGINE_NAME = "Creator Jam Composition Engine Prototype"
ENGINE_VERSION = "0.1.0"


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
    return str(review.get("composition_disposition", "unknown"))


def transition_result(transition: dict[str, Any]) -> str:
    result = transition.get("result", {})
    return str(result.get("status", "unknown"))


def source_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    records = fixture.get("source_records", [])
    return records if isinstance(records, list) else []


def speech_act_transitions(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    transitions = fixture.get("speech_act_transitions", [])
    return transitions if isinstance(transitions, list) else []


def excluded_records(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    records = fixture.get("excluded_records", [])
    return records if isinstance(records, list) else []


def composed_outputs(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    outputs = fixture.get("composed_outputs", [])
    return outputs if isinstance(outputs, list) else []


def record_id(record: dict[str, Any]) -> str:
    return str(record.get("record_id", "unknown-record"))


def check_source_records_have_explicit_marker(records: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [record_id(record) for record in records if "explicit_or_inferred" not in record]
    return {
        "code": "source_records_explicit_or_inferred",
        "status": "ok" if not missing else "warn",
        "detail": "All source records carry explicit_or_inferred." if not missing else "Missing explicit_or_inferred.",
        "records": missing,
    }


def check_transition_ai_receipts(transitions: list[dict[str, Any]]) -> dict[str, Any]:
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

    for output in composed_outputs(fixture):
        output_id = str(output.get("output_id", "unknown-output"))
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
    records: list[dict[str, Any]], excluded: list[dict[str, Any]]
) -> dict[str, Any]:
    excluded_ids = {record_id(item) for item in excluded}
    missing = [record_id(record) for record in records if record.get("do_not_compute") is True and record_id(record) not in excluded_ids]
    return {
        "code": "do_not_compute_exclusions",
        "status": "ok" if not missing else "block",
        "detail": "do_not_compute source records are represented as excluded records."
        if not missing
        else "A do_not_compute record is not represented in excluded_records.",
        "records": missing,
    }


def check_authority_markers(transitions: list[dict[str, Any]]) -> dict[str, Any]:
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


def build_trace(experiment_dir: Path, fixture_path: Path, fixture: dict[str, Any]) -> dict[str, Any]:
    records = source_records(fixture)
    transitions = speech_act_transitions(fixture)
    excluded = excluded_records(fixture)
    outputs = composed_outputs(fixture)

    hard_checks = [
        check_source_records_have_explicit_marker(records),
        check_transition_ai_receipts(transitions),
        check_derived_from_transitions(fixture, transitions),
        check_do_not_compute_exclusions(records, excluded),
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
        if transition_disposition(item) == "blocked" or transition_result(item) == "blocked"
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
                "speech_act": item.get("speech_act"),
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
                "source_record": item.get("source_record"),
                "target_record": item.get("target_record"),
                "composition_disposition": transition_disposition(item),
                "result_status": transition_result(item),
                "has_ai_use_receipt": "ai_use_receipt" in item,
                "has_authority_record": "authority_record" in item,
                "has_contributor_consent_check": "contributor_consent_check" in item,
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
                    f"`{record.get('speech_act')}`",
                    f"`{record.get('explicit_or_inferred')}`",
                    f"`{record.get('visibility_tier')}`",
                    f"`{record.get('permission_state')}`",
                    f"`{md_value(record.get('do_not_compute'))}`",
                ]
            )
        )

    lines.extend(["", "## Speech-Act Transitions", "", md_table_row(["Transition", "From", "To", "Disposition", "Result", "AI Receipt", "Authority", "Contributor Consent"]), md_table_row(["---", "---", "---", "---", "---", "---", "---", "---"])])
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
                        f"`{item.get('record_id')}`",
                        "; ".join(item.get("excluded_reason", [])),
                        "; ".join(item.get("prohibited_actions", [])),
                    ]
                )
            )
    else:
        lines.append("No excluded records were found in the fixture trace.")

    lines.extend(["", "## Coherence Vector", "", md_table_row(["Dimension", "State", "Note"]), md_table_row(["---", "---", "---"])])
    for dimension, payload in (trace.get("coherence_vector") or {}).items():
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
