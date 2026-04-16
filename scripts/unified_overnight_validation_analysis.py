#!/usr/bin/env python3
"""Analyze human validation against unified overnight batch classifications."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class ConfigError(RuntimeError):
    pass


COMPARISON_FIELDS = [
    "pleading_failure_family",
    "pleading_failure_mechanism",
    "institutional_function_missing",
    "administratively_observable_fact_pattern",
    "raw_text_review_priority",
    "doctrinal_gap_signal",
    "public_process_failure_flag",
    "tier1_tier2_fixability",
]

ARRAY_FIELDS = {
    "institutional_function_missing",
    "administratively_observable_fact_pattern",
}
BOOLEAN_FIELDS = {"public_process_failure_flag"}


def script_path() -> Path:
    return Path(__file__).resolve()


def repo_root() -> Path:
    return script_path().parents[1]


def workspace_root() -> Path:
    return script_path().parents[2]


def data_dir() -> Path:
    return workspace_root() / "data" / "2"


def results_dir() -> Path:
    return workspace_root() / "results"


def resolve_validation_sample(path_arg: str) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return data_dir() / "unified_overnight_validation_sample.json"


def resolve_model_results(path_arg: str) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return data_dir() / "unified_overnight_results.json"


def resolve_output_paths(output_arg: str, report_arg: str) -> Tuple[Path, Path]:
    json_path = Path(output_arg).expanduser().resolve() if output_arg else data_dir() / "unified_overnight_validation_analysis.json"
    report_path = Path(report_arg).expanduser().resolve() if report_arg else results_dir() / "unified_overnight_validation_analysis.md"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    return json_path, report_path


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def normalize_text(value: Any) -> str:
    if value in (None, "", [], {}):
        return ""
    return str(value).strip()


def normalize_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    token = normalize_text(value).lower()
    if token in {"true", "yes", "1"}:
        return True
    if token in {"false", "no", "0"}:
        return False
    return None


def normalize_array(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",")]
        return sorted({part for part in parts if part})
    if isinstance(value, list):
        return sorted({normalize_text(item) for item in value if normalize_text(item)})
    return []


def normalize_value(field: str, value: Any) -> Any:
    if field in ARRAY_FIELDS:
        return normalize_array(value)
    if field in BOOLEAN_FIELDS:
        return normalize_bool(value)
    return normalize_text(value)


def extract_human_labels(record: Dict[str, Any]) -> Dict[str, Any]:
    review = record.get("review_template") or {}
    labels = review.get("human_labels") or {}
    payload = {field: normalize_value(field, labels.get(field)) for field in COMPARISON_FIELDS}
    return payload


def human_labels_completed(labels: Dict[str, Any]) -> bool:
    return any(value not in ("", [], None) for value in labels.values())


def build_model_lookup(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    duplicates: List[str] = []
    for row in results:
        source_file = normalize_text(row.get("source_file"))
        custom_id = normalize_text(row.get("custom_id"))
        key = source_file or custom_id
        if not key:
            continue
        if key in lookup:
            duplicates.append(key)
        lookup[key] = row
    if duplicates:
        raise ConfigError(f"Duplicate model result entries found for keys: {', '.join(sorted(set(duplicates))[:10])}")
    return lookup


def compare_record(record: Dict[str, Any], model_row: Dict[str, Any]) -> Dict[str, Any]:
    source_file = normalize_text(record.get("source_file"))
    case_name = normalize_text(record.get("case_name"))
    bucket = normalize_text(record.get("bucket"))
    human = extract_human_labels(record)
    model_payload = model_row.get("classification") or {}
    field_results: Dict[str, Any] = {}
    matches = 0
    compared = 0
    disagreements: List[str] = []

    for field in COMPARISON_FIELDS:
        human_value = normalize_value(field, human.get(field))
        model_value = normalize_value(field, model_payload.get(field))
        is_compared = human_value not in ("", [], None)
        is_match = is_compared and human_value == model_value
        if is_compared:
            compared += 1
            if is_match:
                matches += 1
            else:
                disagreements.append(field)
        field_results[field] = {
            "human": human_value,
            "model": model_value,
            "compared": is_compared,
            "match": is_match,
        }

    return {
        "source_file": source_file,
        "case_name": case_name,
        "bucket": bucket,
        "compared_fields": compared,
        "matched_fields": matches,
        "match_rate": round(matches / compared, 4) if compared else None,
        "disagreement_fields": disagreements,
        "notes": normalize_text((record.get("review_template") or {}).get("notes")),
        "field_results": field_results,
    }


def markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return lines


def build_report(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines: List[str] = []
    lines.append("# Unified Overnight Validation Analysis")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at']}")
    lines.append(f"Validation sample: `{payload['validation_sample_path']}`")
    lines.append(f"Model results: `{payload['model_results_path']}`")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Metric", "Value"],
            [
                ["Sample records", summary["sample_records"]],
                ["Records with any human labels", summary["records_with_completed_labels"]],
                ["Records with model matches available", summary["records_with_model_outputs"]],
                ["Records compared", summary["records_compared"]],
                ["Compared fields", summary["fields_compared"]],
                ["Matched fields", summary["fields_matched"]],
                ["Overall field agreement", summary["overall_field_agreement_pct"]],
                ["Missing model outputs for labeled records", summary["missing_model_outputs_for_labeled_records"]],
            ],
        )
    )
    lines.append("")

    lines.append("## Field-level agreement")
    field_rows = [
        [
            field,
            stats["compared"],
            stats["matched"],
            stats["agreement_pct"],
        ]
        for field, stats in payload["field_level"].items()
    ]
    lines.extend(markdown_table(["Field", "Compared", "Matched", "Agreement %"], field_rows))
    lines.append("")

    if payload["bucket_level"]:
        lines.append("## Bucket-level agreement")
        bucket_rows = [
            [bucket, stats["records_compared"], stats["fields_compared"], stats["agreement_pct"]]
            for bucket, stats in sorted(payload["bucket_level"].items())
        ]
        lines.extend(markdown_table(["Bucket", "Records compared", "Fields compared", "Agreement %"], bucket_rows))
        lines.append("")

    if payload["summary"]["missing_model_output_preview"]:
        lines.append("## Labeled records missing model outputs")
        for item in payload["summary"]["missing_model_output_preview"]:
            lines.append(f"- {item}")
        lines.append("")

    if payload["disagreement_examples"]:
        lines.append("## Disagreement examples")
        for item in payload["disagreement_examples"]:
            lines.append(f"### {item['case_name']} ({item['bucket']})")
            lines.append(f"- source_file: {item['source_file']}")
            if item.get("notes"):
                lines.append(f"- notes: {item['notes']}")
            for field in item["disagreement_fields"]:
                field_result = item["field_results"][field]
                lines.append(f"- {field}: human={field_result['human']} | model={field_result['model']}")
            lines.append("")
    else:
        lines.append("## Disagreement examples")
        lines.append("No disagreements captured in the completed labeled subset.")
        lines.append("")

    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    validation_sample_path = resolve_validation_sample(args.validation_sample)
    model_results_path = resolve_model_results(args.model_results)
    output_path, report_path = resolve_output_paths(args.output, args.report)

    if not validation_sample_path.exists():
        raise ConfigError(f"Validation sample file not found: {validation_sample_path}")
    if not model_results_path.exists():
        raise ConfigError(
            "Unified overnight model results not found. Expected results JSON at "
            f"{model_results_path}. Run unified_overnight_batch.py download after the batch finishes."
        )

    sample_payload = load_json(validation_sample_path)
    if not isinstance(sample_payload, dict) or not isinstance(sample_payload.get("records"), list):
        raise ConfigError("Validation sample JSON must be an object with a 'records' list.")
    model_payload = load_json(model_results_path)
    if not isinstance(model_payload, list):
        raise ConfigError("Model results JSON must be a list of batch result rows.")

    model_lookup = build_model_lookup(model_payload)
    field_counters: Dict[str, Counter[str]] = {field: Counter() for field in COMPARISON_FIELDS}
    bucket_counters: Dict[str, Counter[str]] = defaultdict(Counter)
    comparisons: List[Dict[str, Any]] = []
    missing_model_outputs: List[str] = []
    records_with_completed_labels = 0
    records_with_model_outputs = 0

    for record in sample_payload["records"]:
        human = extract_human_labels(record)
        if not human_labels_completed(human):
            continue
        records_with_completed_labels += 1
        source_file = normalize_text(record.get("source_file"))
        model_row = model_lookup.get(source_file)
        if model_row is None:
            missing_model_outputs.append(source_file or normalize_text(record.get("case_name")) or "UNKNOWN_RECORD")
            continue
        records_with_model_outputs += 1
        comparison = compare_record(record, model_row)
        comparisons.append(comparison)
        bucket = comparison["bucket"] or "UNKNOWN_BUCKET"
        bucket_counters[bucket]["records_compared"] += 1
        for field, result in comparison["field_results"].items():
            if not result["compared"]:
                continue
            field_counters[field]["compared"] += 1
            bucket_counters[bucket]["fields_compared"] += 1
            if result["match"]:
                field_counters[field]["matched"] += 1
                bucket_counters[bucket]["fields_matched"] += 1

    if records_with_completed_labels == 0:
        raise ConfigError(
            "Validation sample is present but contains no completed human labels yet. Fill review_template.human_labels in "
            f"{validation_sample_path} before running validation analysis."
        )

    total_fields_compared = sum(counter["compared"] for counter in field_counters.values())
    total_fields_matched = sum(counter["matched"] for counter in field_counters.values())
    field_level = {
        field: {
            "compared": counter["compared"],
            "matched": counter["matched"],
            "agreement_pct": round((counter["matched"] / counter["compared"]) * 100, 1) if counter["compared"] else None,
        }
        for field, counter in field_counters.items()
    }
    bucket_level = {
        bucket: {
            "records_compared": counter["records_compared"],
            "fields_compared": counter["fields_compared"],
            "fields_matched": counter["fields_matched"],
            "agreement_pct": round((counter["fields_matched"] / counter["fields_compared"]) * 100, 1) if counter["fields_compared"] else None,
        }
        for bucket, counter in bucket_counters.items()
    }

    disagreement_examples = [item for item in comparisons if item["disagreement_fields"]]
    disagreement_examples.sort(key=lambda item: (-len(item["disagreement_fields"]), item["case_name"]))

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "workspace_root": str(workspace_root()),
        "repo_root": str(repo_root()),
        "validation_sample_path": str(validation_sample_path),
        "model_results_path": str(model_results_path),
        "summary": {
            "sample_records": len(sample_payload["records"]),
            "records_with_completed_labels": records_with_completed_labels,
            "records_with_model_outputs": records_with_model_outputs,
            "records_compared": len(comparisons),
            "fields_compared": total_fields_compared,
            "fields_matched": total_fields_matched,
            "overall_field_agreement_pct": round((total_fields_matched / total_fields_compared) * 100, 1) if total_fields_compared else None,
            "missing_model_outputs_for_labeled_records": len(missing_model_outputs),
            "missing_model_output_preview": missing_model_outputs[:25],
        },
        "field_level": field_level,
        "bucket_level": bucket_level,
        "disagreement_examples": disagreement_examples[:20],
        "comparisons": comparisons,
    }

    write_json(output_path, payload)
    report_path.write_text(build_report(payload), encoding="utf-8")
    print(f"Validation analysis JSON written to {output_path}")
    print(f"Validation analysis report written to {report_path}")
    print(f"Records compared: {len(comparisons)}")
    print(f"Overall field agreement: {payload['summary']['overall_field_agreement_pct']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze completed human validation labels against unified overnight model outputs")
    parser.add_argument("--validation-sample", default="", help="Optional path to unified_overnight_validation_sample.json")
    parser.add_argument("--model-results", default="", help="Optional path to unified_overnight_results.json")
    parser.add_argument("--output", default="", help="Optional path for JSON analysis output")
    parser.add_argument("--report", default="", help="Optional path for markdown analysis report")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
