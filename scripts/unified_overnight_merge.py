#!/usr/bin/env python3
"""Merge unified overnight batch classifications back onto the FHA unified database."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


class ConfigError(RuntimeError):
    pass


SCHEMA_FIELDS = [
    "pleading_failure_family",
    "pleading_failure_mechanism",
    "institutional_function_missing",
    "administratively_observable_fact_pattern",
    "raw_text_review_priority",
    "doctrinal_gap_signal",
    "public_process_failure_flag",
    "tier1_tier2_fixability",
    "classification_confidence",
    "reasoning",
]


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


def resolve_input_db() -> Path:
    candidates = [
        data_dir() / "FHA_Unified_Database.json",
        repo_root() / "data" / "FHA_Unified_Database.json",
        workspace_root() / "data" / "FHA_Unified_Database.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise ConfigError("Could not locate FHA_Unified_Database.json in workspace or repo data directories.")


def resolve_results_path(path_arg: str) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return data_dir() / "unified_overnight_results.json"


def resolve_lookup_path(path_arg: str) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return data_dir() / "unified_overnight_id_lookup.json"


def resolve_optional_path(path_arg: str, default_name: str) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return data_dir() / default_name


def resolve_output_paths(output_arg: str, report_arg: str) -> Tuple[Path, Path]:
    merged_path = Path(output_arg).expanduser().resolve() if output_arg else data_dir() / "unified_overnight_merged.json"
    report_path = Path(report_arg).expanduser().resolve() if report_arg else results_dir() / "unified_overnight_merge_report.md"
    merged_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    return merged_path, report_path


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


def normalize_classification(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(payload)
    for key in ("institutional_function_missing", "administratively_observable_fact_pattern"):
        values = normalized.get(key)
        if values is None:
            normalized[key] = []
        elif isinstance(values, list):
            normalized[key] = [str(item).strip() for item in values if str(item).strip()]
        elif isinstance(values, str):
            token = values.strip()
            normalized[key] = [token] if token else []
        else:
            normalized[key] = []
    reasoning = normalized.get("reasoning")
    normalized["reasoning"] = normalize_text(reasoning)
    return normalized


def build_result_lookup(results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
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
        raise ConfigError(f"Duplicate overnight results for keys: {', '.join(sorted(set(duplicates))[:10])}")
    return lookup


def build_id_lookup(id_lookup: Dict[str, Any]) -> Dict[str, str]:
    reverse: Dict[str, str] = {}
    for custom_id, meta in id_lookup.items():
        if not isinstance(meta, dict):
            continue
        source_file = normalize_text(meta.get("source_file"))
        if source_file:
            reverse[source_file] = custom_id
    return reverse


def merge_records(
    db_records: List[Dict[str, Any]],
    result_lookup: Dict[str, Dict[str, Any]],
    reverse_id_lookup: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    matched = 0
    unmatched_records: List[str] = []
    family_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()
    review_priority_counts: Counter[str] = Counter()

    for record in db_records:
        source_file = normalize_text(record.get("source_file"))
        custom_id = reverse_id_lookup.get(source_file, "")
        batch_row = result_lookup.get(source_file) or result_lookup.get(custom_id)

        overnight_block: Dict[str, Any] = {
            "matched": bool(batch_row),
            "source_file": source_file,
            "custom_id": normalize_text(batch_row.get("custom_id")) if batch_row else custom_id,
            "classification": None,
            "token_usage": None,
        }
        if batch_row:
            matched += 1
            classification = normalize_classification(batch_row.get("classification") or {})
            overnight_block["classification"] = classification
            overnight_block["token_usage"] = {
                "input_tokens": batch_row.get("input_tokens"),
                "output_tokens": batch_row.get("output_tokens"),
            }
            family_counts[normalize_text(classification.get("pleading_failure_family")) or "UNKNOWN"] += 1
            confidence_counts[normalize_text(classification.get("classification_confidence")) or "UNKNOWN"] += 1
            review_priority_counts[normalize_text(classification.get("raw_text_review_priority")) or "UNKNOWN"] += 1
        else:
            if source_file:
                unmatched_records.append(source_file)

        merged.append({**record, "unified_overnight": overnight_block})

    matched_keys = {
        normalize_text(row.get("source_file")) or normalize_text(row.get("custom_id"))
        for row in result_lookup.values()
    }
    db_keys = {
        normalize_text(record.get("source_file")) or reverse_id_lookup.get(normalize_text(record.get("source_file")), "")
        for record in db_records
    }
    orphan_results = sorted(key for key in matched_keys if key and key not in db_keys)

    summary = {
        "db_record_count": len(db_records),
        "matched_record_count": matched,
        "unmatched_record_count": len(unmatched_records),
        "orphan_result_count": len(orphan_results),
        "unmatched_source_files_preview": unmatched_records[:25],
        "orphan_result_keys_preview": orphan_results[:25],
        "pleading_failure_family_counts": dict(sorted(family_counts.items())),
        "classification_confidence_counts": dict(sorted(confidence_counts.items())),
        "raw_text_review_priority_counts": dict(sorted(review_priority_counts.items())),
    }
    return merged, summary


def markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return lines


def build_report(
    input_db: Path,
    results_path: Path,
    merged_path: Path,
    summary: Dict[str, Any],
    malformed_count: int,
    error_count: int,
) -> str:
    lines: List[str] = []
    lines.append("# Unified Overnight Merge Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')}")
    lines.append(f"Input DB: `{input_db}`")
    lines.append(f"Batch results: `{results_path}`")
    lines.append(f"Merged output: `{merged_path}`")
    lines.append("")
    lines.extend(
        markdown_table(
            ["Metric", "Value"],
            [
                ["DB record count", summary["db_record_count"]],
                ["Matched record count", summary["matched_record_count"]],
                ["Unmatched record count", summary["unmatched_record_count"]],
                ["Orphan result count", summary["orphan_result_count"]],
                ["Malformed parsed responses logged", malformed_count],
                ["Hard errors logged", error_count],
            ],
        )
    )
    lines.append("")
    for label, key in [
        ("Pleading-failure family distribution", "pleading_failure_family_counts"),
        ("Confidence distribution", "classification_confidence_counts"),
        ("Raw-text review priority distribution", "raw_text_review_priority_counts"),
    ]:
        lines.append(f"## {label}")
        rows = [[k, v] for k, v in summary[key].items()]
        if rows:
            lines.extend(markdown_table(["Label", "Count"], rows))
        else:
            lines.append("No matched results yet.")
        lines.append("")

    if summary["unmatched_source_files_preview"]:
        lines.append("## Unmatched source-file preview")
        for item in summary["unmatched_source_files_preview"]:
            lines.append(f"- {item}")
        lines.append("")
    if summary["orphan_result_keys_preview"]:
        lines.append("## Orphan result-key preview")
        for item in summary["orphan_result_keys_preview"]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> int:
    input_db = resolve_input_db()
    results_path = resolve_results_path(args.results)
    lookup_path = resolve_lookup_path(args.id_lookup)
    malformed_path = resolve_optional_path(args.malformed, "unified_overnight_malformed.json")
    errors_path = resolve_optional_path(args.errors, "unified_overnight_errors.json")
    merged_path, report_path = resolve_output_paths(args.output, args.report)

    if not results_path.exists():
        raise ConfigError(
            "Unified overnight batch results not found. Expected results JSON at "
            f"{results_path}. Run unified_overnight_batch.py download after the batch finishes."
        )

    db_records = load_json(input_db)
    if not isinstance(db_records, list):
        raise ConfigError(f"Expected list payload in {input_db}, got {type(db_records).__name__}")

    batch_results = load_json(results_path)
    if not isinstance(batch_results, list):
        raise ConfigError(f"Expected list payload in {results_path}, got {type(batch_results).__name__}")

    id_lookup_payload = load_json(lookup_path) if lookup_path.exists() else {}
    if not isinstance(id_lookup_payload, dict):
        raise ConfigError(f"Expected dict payload in {lookup_path}, got {type(id_lookup_payload).__name__}")

    result_lookup = build_result_lookup(batch_results)
    reverse_id_lookup = build_id_lookup(id_lookup_payload)
    merged, summary = merge_records(db_records, result_lookup, reverse_id_lookup)

    malformed_count = 0
    if malformed_path.exists():
        malformed_payload = load_json(malformed_path)
        if isinstance(malformed_payload, list):
            malformed_count = len(malformed_payload)
    error_count = 0
    if errors_path.exists():
        error_payload = load_json(errors_path)
        if isinstance(error_payload, list):
            error_count = len(error_payload)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "workspace_root": str(workspace_root()),
        "repo_root": str(repo_root()),
        "input_db": str(input_db),
        "results_path": str(results_path),
        "id_lookup_path": str(lookup_path),
        "summary": summary,
        "records": merged,
    }
    write_json(merged_path, payload)
    report_path.write_text(build_report(input_db, results_path, merged_path, summary, malformed_count, error_count), encoding="utf-8")

    print(f"Merged output written to {merged_path}")
    print(f"Merge report written to {report_path}")
    print(f"Matched {summary['matched_record_count']} of {summary['db_record_count']} records")
    print(f"Orphan result count: {summary['orphan_result_count']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge unified overnight batch outputs onto the FHA unified database")
    parser.add_argument("--results", default="", help="Optional path to unified_overnight_results.json")
    parser.add_argument("--id-lookup", default="", help="Optional path to unified_overnight_id_lookup.json")
    parser.add_argument("--malformed", default="", help="Optional path to unified_overnight_malformed.json")
    parser.add_argument("--errors", default="", help="Optional path to unified_overnight_errors.json")
    parser.add_argument("--output", default="", help="Optional path for merged JSON output")
    parser.add_argument("--report", default="", help="Optional path for markdown merge report")
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
