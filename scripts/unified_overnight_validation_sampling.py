#!/usr/bin/env python3
"""Create a validation sampling packet for the unified overnight FHA run."""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

P1_START = datetime(2022, 1, 1)
P1_END = datetime(2024, 6, 28)
P2_END = datetime(2025, 2, 5)
PUBLIC_DEFENDANT_TYPES = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
INSTITUTIONAL_PLAINTIFF_TYPES = {"GROUP_HOME_OPERATOR", "FAIR_HOUSING_ORG", "GOVERNMENT"}
_REPO_ROOT = Path(__file__).resolve().parents[1]
_WORKSPACE_ROOT = _REPO_ROOT.parent
KNOWN_TEXT_DIRS = [
    _WORKSPACE_ROOT / "allFHAcases",
    _WORKSPACE_ROOT / "data" / "cases",
    _REPO_ROOT / "data" / "cases",
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_input_path() -> Path:
    candidates = [
        workspace_root() / "data" / "2" / "FHA_Unified_Database.json",
        repo_root() / "data" / "FHA_Unified_Database.json",
        workspace_root() / "data" / "FHA_Unified_Database.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Could not locate FHA_Unified_Database.json")


def resolve_output_paths() -> Tuple[Path, Path]:
    ws = workspace_root()
    results_dir = ws / "results"
    data_dir = ws / "data" / "2"
    results_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    return (
        results_dir / "unified_overnight_validation_packet.md",
        data_dir / "unified_overnight_validation_sample.json",
    )


def load_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if isinstance(payload, dict):
        return list(payload.values())
    if not isinstance(payload, list):
        raise TypeError(f"Expected list/dict JSON but received {type(payload).__name__}")
    return payload


def normalize_text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value)


def parse_date(value: Any, year: Any = None) -> Optional[datetime]:
    if isinstance(value, str) and value.strip():
        raw = value.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"):
            try:
                if fmt == "%Y-%m-%dT%H:%M:%S":
                    return datetime.strptime(raw[:19], fmt)
                return datetime.strptime(raw[:10], fmt)
            except ValueError:
                continue
    if isinstance(year, int):
        return datetime(year, 1, 1)
    return None


def assign_period(record: Dict[str, Any]) -> Optional[str]:
    dt = parse_date(record.get("date_filed"), record.get("year"))
    if dt is None or dt < P1_START:
        return None
    if dt < P1_END:
        return "P1"
    if dt < P2_END:
        return "P2"
    return "P3"


def has_disability(record: Dict[str, Any]) -> bool:
    classes = record.get("protected_classes") or []
    if isinstance(classes, str):
        classes = [classes]
    return any("disability" in str(item).lower() for item in classes)


def is_screened_case(record: Dict[str, Any]) -> bool:
    return (
        normalize_text(record.get("screening_result"), "NO").upper() != "NO"
        and bool(record.get("case_name"))
        and record.get("outcome") not in (None, "", "?")
    )


def claims_for(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    claims = record.get("fha_claims") or []
    return [claim for claim in claims if isinstance(claim, dict)]


def truthy_pro_se(value: Any) -> bool:
    if value is True:
        return True
    return str(value).strip().lower() in {"true", "yes", "1"}


def institutional_plaintiff(record: Dict[str, Any]) -> bool:
    return normalize_text(record.get("plaintiff_type")).upper() in INSTITUTIONAL_PLAINTIFF_TYPES


def pleading_loss(record: Dict[str, Any]) -> bool:
    if normalize_text(record.get("outcome")).upper() not in {"DEFENDANT_WIN", "PROCEDURAL"}:
        return False
    for claim in claims_for(record):
        stage = normalize_text(claim.get("stage")).upper()
        reason = normalize_text(claim.get("dismissal_reason")).upper()
        disposition = normalize_text(claim.get("disposition")).lower()
        if stage in {"MTD", "SCREENING_1915"}:
            return True
        if "12(b)(6)" in disposition or "failure to state a claim" in disposition:
            return True
        if reason in {"IQBAL_TWOMBLY", "SCREENING_1915", "NEXUS_FAILURE", "STANDING", "STATUTE_OF_LIMITATIONS"}:
            return True
    return False


def public_process_case(record: Dict[str, Any]) -> bool:
    if normalize_text(record.get("defendant_type")).upper() not in PUBLIC_DEFENDANT_TYPES:
        return False
    if normalize_text(record.get("interactive_process_discussed")).upper() == "YES":
        return True
    if normalize_text(record.get("delay_as_denial")).upper() == "YES":
        return True
    haystack = " ".join(
        [normalize_text(record.get("brief_summary"))]
        + [normalize_text(claim.get("reasoning")) for claim in claims_for(record)]
    ).lower()
    return "process" in haystack or "accommodation" in haystack


def design_and_construction_case(record: Dict[str, Any]) -> bool:
    values: List[str] = []
    for field in ("primary_claim_type", "brief_summary"):
        values.append(normalize_text(record.get(field)))
    claim_types = record.get("claim_types") or []
    if isinstance(claim_types, list):
        values.extend(str(item) for item in claim_types)
    else:
        values.append(str(claim_types))
    text = " ".join(values).lower()
    return "design_and_construction" in text or ("design" in text and "construction" in text)


def open_textured_case(record: Dict[str, Any]) -> bool:
    if normalize_text(record.get("primary_claim_type")).lower() == "other":
        return True
    if normalize_text(record.get("outcome")).upper() == "UNDETERMINED":
        return True
    for claim in claims_for(record):
        if normalize_text(claim.get("dismissal_reason")).upper() == "OTHER":
            return True
        if normalize_text(claim.get("disposition")).upper() in {"OTHER", "N/A"}:
            return True
    return False


def institutional_win(record: Dict[str, Any]) -> bool:
    return institutional_plaintiff(record) and normalize_text(record.get("outcome")).upper() in {"PLAINTIFF_WIN", "MIXED"}


def stable_score(record: Dict[str, Any]) -> str:
    parts = [
        assign_period(record) or "P0",
        normalize_text(record.get("outcome"), "UNKNOWN"),
        normalize_text(record.get("circuit"), "NO_CIRCUIT"),
        normalize_text(record.get("source_file"), "NO_SOURCE"),
    ]
    return "|".join(parts)


def sanitize_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def find_raw_text_path(record: Dict[str, Any]) -> Tuple[Optional[str], str]:
    source_file = normalize_text(record.get("source_file"))
    if source_file:
        for directory in KNOWN_TEXT_DIRS:
            exact_path = directory / f"{source_file}.txt"
            if exact_path.exists():
                return str(exact_path), "exact_source_file_match"
        numeric_prefix_match = re.match(r"^(\d+)", source_file)
        if numeric_prefix_match and KNOWN_TEXT_DIRS[0].exists():
            prefix = numeric_prefix_match.group(1)
            candidates = sorted(KNOWN_TEXT_DIRS[0].glob(f"{prefix}_*.txt"))
            if len(candidates) == 1:
                return str(candidates[0]), "numeric_prefix_match"

    case_name = normalize_text(record.get("case_name"))
    if case_name and KNOWN_TEXT_DIRS[0].exists():
        word_tokens = [sanitize_token(part) for part in re.split(r"\W+", case_name) if sanitize_token(part)]
        useful_tokens = [token for token in word_tokens if len(token) >= 4][:4]
        if useful_tokens:
            for candidate in KNOWN_TEXT_DIRS[0].glob("*.txt"):
                lower_name = sanitize_token(candidate.stem)
                if all(token in lower_name for token in useful_tokens[:2]):
                    return str(candidate), "fuzzy_case_name_match"
    return None, "not_found"


def sample_bucket(records: Sequence[Dict[str, Any]], desired_n: int, used_ids: set[str]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {"P1": [], "P2": [], "P3": [], "P0": []}
    for record in sorted(records, key=stable_score):
        record_id = normalize_text(record.get("source_file") or record.get("case_name"))
        if not record_id or record_id in used_ids:
            continue
        grouped[assign_period(record) or "P0"].append(record)

    selected: List[Dict[str, Any]] = []
    order = ["P1", "P2", "P3", "P0"]
    while len(selected) < desired_n:
        made_progress = False
        for period in order:
            if grouped[period] and len(selected) < desired_n:
                chosen = grouped[period].pop(0)
                record_id = normalize_text(chosen.get("source_file") or chosen.get("case_name"))
                used_ids.add(record_id)
                selected.append(chosen)
                made_progress = True
        if not made_progress:
            break
    return selected


def record_summary(record: Dict[str, Any], bucket: str) -> Dict[str, Any]:
    raw_text_path, raw_text_status = find_raw_text_path(record)
    claim_stages = sorted({normalize_text(claim.get("stage")).upper() for claim in claims_for(record) if normalize_text(claim.get("stage"))})
    dismissal_reasons = sorted({normalize_text(claim.get("dismissal_reason")).upper() for claim in claims_for(record) if normalize_text(claim.get("dismissal_reason"))})
    return {
        "bucket": bucket,
        "source_file": normalize_text(record.get("source_file")),
        "case_name": normalize_text(record.get("case_name")),
        "citation": normalize_text(record.get("citation")),
        "period": assign_period(record),
        "year": record.get("year"),
        "outcome": normalize_text(record.get("outcome")),
        "plaintiff_type": normalize_text(record.get("plaintiff_type")),
        "defendant_type": normalize_text(record.get("defendant_type")),
        "pro_se": bool(truthy_pro_se(record.get("pro_se"))),
        "protected_classes": record.get("protected_classes") or [],
        "primary_claim_type": normalize_text(record.get("primary_claim_type")),
        "claim_types": record.get("claim_types") or [],
        "claim_stage_values": claim_stages,
        "dismissal_reason_values": dismissal_reasons,
        "interactive_process_discussed": normalize_text(record.get("interactive_process_discussed")),
        "delay_as_denial": normalize_text(record.get("delay_as_denial")),
        "key_cases_cited": record.get("key_cases_cited") or [],
        "brief_summary": normalize_text(record.get("brief_summary")),
        "raw_text_candidate_path": raw_text_path,
        "raw_text_lookup_status": raw_text_status,
        "review_template": {
            "human_labels": {
                "pleading_failure_family": "",
                "pleading_failure_mechanism": "",
                "institutional_function_missing": "",
                "administratively_observable_fact_pattern": "",
                "raw_text_review_priority": "",
                "doctrinal_gap_signal": "",
                "public_process_failure_flag": "",
                "tier1_tier2_fixability": "",
            },
            "notes": "",
        },
    }


def markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return lines


def main() -> None:
    input_path = resolve_input_path()
    packet_path, sample_path = resolve_output_paths()
    records = [record for record in load_json(input_path) if is_screened_case(record)]

    bucket_rules = [
        ("pro_se_pleading_losses", 8, lambda r: truthy_pro_se(r.get("pro_se")) and pleading_loss(r)),
        ("represented_pleading_losses", 8, lambda r: (r.get("pro_se") is False) and pleading_loss(r)),
        ("public_defendant_process_cases", 8, public_process_case),
        ("institutional_wins", 8, institutional_win),
        ("design_and_construction_technical_cases", 8, design_and_construction_case),
        ("open_textured_cases", 8, open_textured_case),
        ("disability_controls", 6, has_disability),
        ("non_disability_controls", 6, lambda r: not has_disability(r)),
    ]

    used_ids: set[str] = set()
    sampled: List[Dict[str, Any]] = []
    bucket_meta: List[Dict[str, Any]] = []

    for bucket_name, desired_n, predicate in bucket_rules:
        eligible = [record for record in records if predicate(record)]
        selected = sample_bucket(eligible, desired_n, used_ids)
        bucket_meta.append(
            {
                "bucket": bucket_name,
                "eligible_n": len(eligible),
                "selected_n": len(selected),
                "sample_target": desired_n,
                "period_counts": dict(Counter(assign_period(record) or "P0" for record in selected)),
            }
        )
        sampled.extend(record_summary(record, bucket_name) for record in selected)

    payload = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "input_path": str(input_path),
        "cohort_size": len(records),
        "sample_size": len(sampled),
        "bucket_meta": bucket_meta,
        "records": sampled,
    }
    sample_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Unified Overnight Validation Packet")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at']}")
    lines.append(f"Input: `{input_path}`")
    lines.append(f"Screened cohort used for sampling: {len(records)} cases")
    lines.append(f"Validation sample size: {len(sampled)} cases")
    lines.append("")
    lines.append("## Sampling buckets")
    lines.extend(
        markdown_table(
            ["Bucket", "Eligible N", "Selected N", "Target", "Selected period mix"],
            [
                [
                    meta["bucket"],
                    meta["eligible_n"],
                    meta["selected_n"],
                    meta["sample_target"],
                    json.dumps(meta["period_counts"], sort_keys=True),
                ]
                for meta in bucket_meta
            ],
        )
    )
    lines.append("")
    lines.append("## Review instructions")
    lines.append("1. Review the structured record and, if available, the raw-text candidate path.")
    lines.append("2. Fill the human labels for each sampled case using the overnight schema fields.")
    lines.append("3. Flag any disagreement between structured metadata and the overnight autopsy output.")
    lines.append("4. Use raw-text reopening first for `not_found` or fuzzy matches that look high-value.")
    lines.append("")

    for index, record in enumerate(sampled, start=1):
        lines.append(f"## {index}. {record['case_name']} [{record['bucket']}]")
        lines.append("")
        lines.extend(
            markdown_table(
                ["Field", "Value"],
                [
                    ["Source file", record["source_file"]],
                    ["Citation", record["citation"]],
                    ["Period", record["period"]],
                    ["Outcome", record["outcome"]],
                    ["Plaintiff type", record["plaintiff_type"]],
                    ["Defendant type", record["defendant_type"]],
                    ["Pro se", record["pro_se"]],
                    ["Primary claim type", record["primary_claim_type"]],
                    ["Claim types", ", ".join(record["claim_types"]) if record["claim_types"] else ""],
                    ["Claim stages", ", ".join(record["claim_stage_values"])],
                    ["Dismissal reasons", ", ".join(record["dismissal_reason_values"])],
                    ["Interactive process discussed", record["interactive_process_discussed"]],
                    ["Delay as denial", record["delay_as_denial"]],
                    ["Raw-text candidate path", record["raw_text_candidate_path"] or ""],
                    ["Raw-text lookup status", record["raw_text_lookup_status"]],
                ],
            )
        )
        lines.append("")
        lines.append("Summary:")
        lines.append(record["brief_summary"] or "")
        lines.append("")
        lines.append("Suggested schema review fields:")
        for field in record["review_template"]["human_labels"].keys():
            lines.append(f"- {field}: ")
        lines.append("- notes: ")
        lines.append("")

    packet_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote packet: {packet_path}")
    print(f"Wrote sample JSON: {sample_path}")
    print(f"Sample size: {len(sampled)} across {len(bucket_meta)} buckets")


if __name__ == "__main__":
    main()
