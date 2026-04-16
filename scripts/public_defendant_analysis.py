#!/usr/bin/env python3
"""Analyze public-defendant process failures and reporting-architecture fit."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "data" / "FHA_Unified_Database.json"
MERGED_PATH = REPO_ROOT / "results" / "unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json"
OUTPUT_JSON = REPO_ROOT / "results" / "public_defendant_process_failure_results.json"
OUTPUT_MEMO = REPO_ROOT / "results" / "public_defendant_process_failure_analysis.md"

PUBLIC_DEFENDANT_TYPES = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
PROCESS_PRIMARY_CLAIM_TYPES = {"reasonable_accommodation_denial", "reasonable_modification_denial"}
LOSS_OUTCOMES = {"DEFENDANT_WIN", "PROCEDURAL"}
UNDIAGNOSED_OR_NONLOSS_MECHANISMS = {"UNCLEAR", "CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS"}

ACCOMMODATION_REQUEST_LOG_PATTERNS = {
    "DOCUMENTED_REQUEST",
    "DENIAL_OR_NO_RESPONSE_RECORD",
    "NOTICE_OR_TIMELINE_RECORD",
    "HEARING_OR_GRIEVANCE_RECORD",
    "PUBLIC_PROGRAM_RULE_OR_DECISION",
}
ACCESSIBLE_UNIT_INVENTORY_PATTERNS = {"PHYSICAL_ACCESS_BARRIER"}
INSPECTION_FLAG_PATTERNS = {"PHYSICAL_ACCESS_BARRIER", "INSPECTION_OR_MEASUREMENT_DATA"}
DIRECT_REPORTING_ARCHITECTURE_PATTERNS = (
    ACCOMMODATION_REQUEST_LOG_PATTERNS
    | ACCESSIBLE_UNIT_INVENTORY_PATTERNS
    | INSPECTION_FLAG_PATTERNS
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


def upper_text(value: Any, default: str = "") -> str:
    return normalize_text(value, default).upper()


def lower_text(value: Any, default: str = "") -> str:
    return normalize_text(value, default).lower()


def boolish(value: Any) -> bool:
    if value is True:
        return True
    return normalize_text(value).lower() in {"true", "yes", "1"}


def pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100.0, 1)


def combined_summary_text(record: Dict[str, Any]) -> str:
    return " ".join(
        part for part in [normalize_text(record.get("brief_summary")), normalize_text(record.get("key_holding"))] if part
    ).lower()


def housing_type(record: Dict[str, Any]) -> str:
    return upper_text(record.get("housing_type"), "UNDETERMINED") or "UNDETERMINED"


def defendant_type(record: Dict[str, Any]) -> str:
    return upper_text(record.get("defendant_type"), "UNDETERMINED") or "UNDETERMINED"


def outcome(record: Dict[str, Any]) -> str:
    return upper_text(record.get("outcome"), "UNDETERMINED") or "UNDETERMINED"


def is_public_defendant_process_case(record: Dict[str, Any]) -> bool:
    if upper_text(record.get("screening_result"), "NO") != "YES":
        return False
    if defendant_type(record) not in PUBLIC_DEFENDANT_TYPES:
        return False
    summary = combined_summary_text(record)
    return (
        boolish(record.get("interactive_process_discussed"))
        or lower_text(record.get("primary_claim_type")) in PROCESS_PRIMARY_CLAIM_TYPES
        or "accommodation" in summary
        or "request" in summary
        or "process" in summary
    )


def extract_classification(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(record, dict):
        return None
    unified = record.get("unified_overnight")
    if not isinstance(unified, dict) or not unified.get("matched"):
        return None
    classification = unified.get("classification")
    if not isinstance(classification, dict):
        return None
    return classification


def classification_list(record: Dict[str, Any], key: str) -> List[str]:
    classification = record.get("classification")
    if not isinstance(classification, dict):
        return []
    value = classification.get(key) or []
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        label = upper_text(item)
        if label and label not in out:
            out.append(label)
    return out


def classification_value(record: Dict[str, Any], key: str, default: str = "UNCLEAR") -> str:
    classification = record.get("classification")
    if not isinstance(classification, dict):
        return default
    label = upper_text(classification.get(key), default)
    return label or default


def ordered_counter(counter: Counter) -> Dict[str, int]:
    items = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    return {key: value for key, value in items}


def counter_with_pct(counter: Counter, total: int) -> Dict[str, Dict[str, float]]:
    items = sorted(counter.items(), key=lambda pair: (-pair[1], pair[0]))
    return {
        key: {
            "count": value,
            "pct": pct(value, total),
        }
        for key, value in items
    }


def crosstab_scalar(
    records: Sequence[Dict[str, Any]],
    row_getter: Callable[[Dict[str, Any]], str],
    column_getter: Callable[[Dict[str, Any]], str],
) -> Dict[str, Any]:
    matrix: Dict[str, Counter] = defaultdict(Counter)
    row_totals: Counter = Counter()
    column_totals: Counter = Counter()

    for record in records:
        row = row_getter(record)
        column = column_getter(record)
        matrix[row][column] += 1
        row_totals[row] += 1
        column_totals[column] += 1

    ordered_rows = [key for key, _ in sorted(row_totals.items(), key=lambda pair: (-pair[1], pair[0]))]
    ordered_columns = [key for key, _ in sorted(column_totals.items(), key=lambda pair: (-pair[1], pair[0]))]

    return {
        "rows": {
            row: {column: matrix[row][column] for column in ordered_columns if matrix[row][column]}
            for row in ordered_rows
        },
        "row_totals": {row: row_totals[row] for row in ordered_rows},
        "column_totals": {column: column_totals[column] for column in ordered_columns},
    }


def crosstab_list(
    records: Sequence[Dict[str, Any]],
    row_getter: Callable[[Dict[str, Any]], Iterable[str]],
    column_getter: Callable[[Dict[str, Any]], str],
) -> Dict[str, Any]:
    matrix: Dict[str, Counter] = defaultdict(Counter)
    row_totals: Counter = Counter()
    column_totals: Counter = Counter()

    for record in records:
        column = column_getter(record)
        seen: List[str] = []
        for row in row_getter(record):
            if row in seen:
                continue
            seen.append(row)
            matrix[row][column] += 1
            row_totals[row] += 1
            column_totals[column] += 1

    ordered_rows = [key for key, _ in sorted(row_totals.items(), key=lambda pair: (-pair[1], pair[0]))]
    ordered_columns = [key for key, _ in sorted(column_totals.items(), key=lambda pair: (-pair[1], pair[0]))]

    return {
        "rows": {
            row: {column: matrix[row][column] for column in ordered_columns if matrix[row][column]}
            for row in ordered_rows
        },
        "row_totals": {row: row_totals[row] for row in ordered_rows},
        "column_totals": {column: column_totals[column] for column in ordered_columns},
    }


def case_count_for_patterns(records: Sequence[Dict[str, Any]], patterns: Iterable[str]) -> int:
    pattern_set = set(patterns)
    return sum(1 for record in records if pattern_set & set(classification_list(record, "administratively_observable_fact_pattern")))


def direct_pattern_case_counts(records: Sequence[Dict[str, Any]], patterns: Iterable[str]) -> Dict[str, int]:
    pattern_set = set(patterns)
    counter: Counter = Counter()
    for record in records:
        observed = set(classification_list(record, "administratively_observable_fact_pattern"))
        for pattern in pattern_set & observed:
            counter[pattern] += 1
    return ordered_counter(counter)


def loss_architecture_fit(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    fixability_counter = Counter(classification_value(record, "tier1_tier2_fixability") for record in records)
    mechanism_counter = Counter(classification_value(record, "pleading_failure_mechanism") for record in records)
    family_counter = Counter(classification_value(record, "pleading_failure_family") for record in records)
    function_counter = Counter(
        item for record in records for item in classification_list(record, "institutional_function_missing")
    )
    fact_counter = Counter(
        item for record in records for item in classification_list(record, "administratively_observable_fact_pattern")
    )
    uncovered_cases = []
    for record in records:
        patterns = set(classification_list(record, "administratively_observable_fact_pattern"))
        if patterns & DIRECT_REPORTING_ARCHITECTURE_PATTERNS:
            continue
        uncovered_cases.append(
            {
                "case_name": normalize_text(record.get("case_name")),
                "source_file": normalize_text(record.get("source_file")),
                "outcome": outcome(record),
                "housing_type": housing_type(record),
                "mechanism": classification_value(record, "pleading_failure_mechanism"),
                "fact_patterns": classification_list(record, "administratively_observable_fact_pattern"),
            }
        )

    component_counts = {
        "accommodation_request_logs": case_count_for_patterns(records, ACCOMMODATION_REQUEST_LOG_PATTERNS),
        "accessible_unit_inventories": case_count_for_patterns(records, ACCESSIBLE_UNIT_INVENTORY_PATTERNS),
        "inspection_flags": case_count_for_patterns(records, INSPECTION_FLAG_PATTERNS),
        "any_direct_reporting_architecture_pattern": case_count_for_patterns(
            records, DIRECT_REPORTING_ARCHITECTURE_PATTERNS
        ),
    }
    total = len(records)

    return {
        "total_cases": total,
        "component_pattern_map": {
            "accommodation_request_logs": sorted(ACCOMMODATION_REQUEST_LOG_PATTERNS),
            "accessible_unit_inventories": sorted(ACCESSIBLE_UNIT_INVENTORY_PATTERNS),
            "inspection_flags": sorted(INSPECTION_FLAG_PATTERNS),
            "any_direct_reporting_architecture_pattern": sorted(DIRECT_REPORTING_ARCHITECTURE_PATTERNS),
        },
        "component_case_counts": component_counts,
        "component_case_shares_pct": {
            key: pct(value, total) for key, value in component_counts.items()
        },
        "fixability": counter_with_pct(fixability_counter, total),
        "pleading_failure_family": counter_with_pct(family_counter, total),
        "pleading_failure_mechanism": counter_with_pct(mechanism_counter, total),
        "institutional_function_missing": counter_with_pct(function_counter, total),
        "administratively_observable_fact_pattern": counter_with_pct(fact_counter, total),
        "direct_pattern_case_counts": direct_pattern_case_counts(records, DIRECT_REPORTING_ARCHITECTURE_PATTERNS),
        "cases_without_direct_reporting_pattern_count": len(uncovered_cases),
        "cases_without_direct_reporting_pattern_preview": uncovered_cases[:10],
    }


def top_mechanisms_by_housing(records: Sequence[Dict[str, Any]], top_housing_limit: int = 5, top_mechanism_limit: int = 5) -> Dict[str, Any]:
    housing_counts = Counter(housing_type(record) for record in records)
    result: Dict[str, Any] = {}
    for housing, count in sorted(housing_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:top_housing_limit]:
        subset = [record for record in records if housing_type(record) == housing]
        mechanism_counts = Counter(classification_value(record, "pleading_failure_mechanism") for record in subset)
        result[housing] = {
            "case_count": count,
            "top_mechanisms": [
                {
                    "mechanism": mechanism,
                    "count": mechanism_count,
                    "pct": pct(mechanism_count, count),
                }
                for mechanism, mechanism_count in sorted(
                    mechanism_counts.items(), key=lambda pair: (-pair[1], pair[0])
                )[:top_mechanism_limit]
            ],
        }
    return result


def build_memo(results: Dict[str, Any]) -> str:
    universe = results["universe_counts"]
    all_413_housing = results["housing_type_counts"]["all_public_defendant_process_cases"]
    coded_housing = results["housing_type_counts"]["coded_public_defendant_process_cases"]
    diagnosed = results["loss_analysis"]["diagnosed_losses_excluding_unclear_or_survival_labels"]
    adverse = results["loss_analysis"]["adverse_outcome_losses_coded"]

    top_mechs = list(diagnosed["pleading_failure_mechanism"].items())[:5]
    top_funcs = list(diagnosed["institutional_function_missing"].items())[:4]
    top_facts = list(diagnosed["administratively_observable_fact_pattern"].items())[:4]

    leading_mechanisms = ", ".join(
        f"{name} {stats['count']} ({stats['pct']}%)" for name, stats in top_mechs
    )
    missing_functions = ", ".join(
        f"{name} {stats['count']} ({stats['pct']}%)" for name, stats in top_funcs
    )
    observable_facts = ", ".join(
        f"{name} {stats['count']} ({stats['pct']}%)" for name, stats in top_facts
    )
    housing_highlights = results["housing_type_highlights_diagnosed_losses"]
    section_8_mechanisms = ", ".join(
        f"{item['mechanism']} {item['count']} ({item['pct']}%)"
        for item in housing_highlights.get("SECTION_8_VOUCHER", {}).get("top_mechanisms", [])
    )
    public_housing_mechanisms = ", ".join(
        f"{item['mechanism']} {item['count']} ({item['pct']}%)"
        for item in housing_highlights.get("PUBLIC_HOUSING", {}).get("top_mechanisms", [])
    )
    supportive_housing_mechanisms = ", ".join(
        f"{item['mechanism']} {item['count']} ({item['pct']}%)"
        for item in housing_highlights.get("SUPPORTIVE_HOUSING", {}).get("top_mechanisms", [])
    )

    lines = [
        "# Public-defendant process failure analysis",
        "",
        f"Generated: {results['generated_at']}",
        "",
        "## Scope and adaptation",
        "",
        "- Reconstructed the exact 413-case universe with the existing `public_defendant_process_cases` rule from `scripts/unified_raw_text_target_inventory.py`: screened cases with `defendant_type` in `MUNICIPALITY`, `HOUSING_AUTHORITY`, or `GOVERNMENT` plus an accommodation/request/process signal in the structured fields.",
        "- The disability-wave coding fields are nested under `record[\"unified_overnight\"][\"classification\"]` in `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json`, not as top-level columns. The script adapts to that actual schema.",
        f"- Of the 413 selected cases, {universe['coded_public_defendant_process_cases']} have disability-wave classifications and {universe['uncoded_public_defendant_process_cases']} do not. I did not invent missing classifications for the uncoded remainder.",
        f"- Loss-fit calculations therefore use the {universe['coded_public_defendant_process_cases']} coded cases, especially {universe['adverse_outcome_losses_coded']} adverse outcomes (`DEFENDANT_WIN` or `PROCEDURAL`). A stricter diagnosed-loss subset excludes {universe['adverse_losses_unclear_or_survival_mechanism']} adverse outcomes coded `UNCLEAR` or `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`, leaving {universe['diagnosed_losses_excluding_unclear_or_survival_labels']} cases.",
        "",
        "## Topline subset shape",
        "",
        f"- Defendant mix in the 413-case universe: HOUSING_AUTHORITY {results['defendant_type_counts']['all_public_defendant_process_cases'].get('HOUSING_AUTHORITY', 0)}, MUNICIPALITY {results['defendant_type_counts']['all_public_defendant_process_cases'].get('MUNICIPALITY', 0)}, GOVERNMENT {results['defendant_type_counts']['all_public_defendant_process_cases'].get('GOVERNMENT', 0)}.",
        f"- Most common housing types in the 413-case universe: {', '.join(f'{name} {count}' for name, count in list(all_413_housing.items())[:5])}.",
        f"- Most common housing types in the 278 coded cases: {', '.join(f'{name} {count}' for name, count in list(coded_housing.items())[:5])}.",
        "",
        "## What specific failures dominate",
        "",
        f"- Family-level pattern in the 163 diagnosed losses: TRANSLATION {diagnosed['pleading_failure_family'].get('TRANSLATION', {}).get('count', 0)} ({diagnosed['pleading_failure_family'].get('TRANSLATION', {}).get('pct', 0.0)}%), PROCEDURAL_GATEWAY {diagnosed['pleading_failure_family'].get('PROCEDURAL_GATEWAY', {}).get('count', 0)} ({diagnosed['pleading_failure_family'].get('PROCEDURAL_GATEWAY', {}).get('pct', 0.0)}%), ELEMENT_MISMATCH {diagnosed['pleading_failure_family'].get('ELEMENT_MISMATCH', {}).get('count', 0)} ({diagnosed['pleading_failure_family'].get('ELEMENT_MISMATCH', {}).get('pct', 0.0)}%), and CAUSAL_LINK {diagnosed['pleading_failure_family'].get('CAUSAL_LINK', {}).get('count', 0)} ({diagnosed['pleading_failure_family'].get('CAUSAL_LINK', {}).get('pct', 0.0)}%).",
        f"- Leading mechanisms: {leading_mechanisms}.",
        f"- Missing institutional functions are concentrated in {missing_functions}.",
        f"- The most common administratively observable facts are {observable_facts}.",
        "",
        "These counts point to a consistent story: courts are often looking for a request trail, a usable chronology, a defendant-specific theory, and a procedurally proper path into court. The dominant problems are not hidden housing events but failures of translation, record assembly, and jurisdictional routing.",
        "",
        "## Housing-type pattern highlights in diagnosed losses",
        "",
        f"- SECTION_8_VOUCHER cases are led by elements-not-tied-to-facts and request/nexus/causal-link failures: {section_8_mechanisms}.",
        f"- PUBLIC_HOUSING cases are led by request-not-alleged and elements-not-tied-to-facts failures: {public_housing_mechanisms}.",
        f"- SUPPORTIVE_HOUSING cases show a different mix, with more technical-proof and preclusion/gateway problems: {supportive_housing_mechanisms}.",
        "",
        "The practical implication is that voucher and public-housing cases are mostly failing on request articulation, factual linkage, and administrative routing, while supportive-housing and zoning-adjacent cases more often add proof or preclusion burdens on top of the process problem.",
        "",
        "## Reporting-architecture fit",
        "",
        f"- In the 229 coded adverse-outcome losses, {adverse['component_case_counts']['any_direct_reporting_architecture_pattern']} cases ({adverse['component_case_shares_pct']['any_direct_reporting_architecture_pattern']}%) include at least one fact pattern that the proposed reporting architecture would directly generate or standardize.",
        f"- That coverage is overwhelmingly request-log coverage: accommodation-request-log patterns appear in {adverse['component_case_counts']['accommodation_request_logs']} losses ({adverse['component_case_shares_pct']['accommodation_request_logs']}%), while accessible-unit-inventory patterns appear in {adverse['component_case_counts']['accessible_unit_inventories']} ({adverse['component_case_shares_pct']['accessible_unit_inventories']}%) and inspection-flag patterns in {adverse['component_case_counts']['inspection_flags']} ({adverse['component_case_shares_pct']['inspection_flags']}%).",
        f"- Fixability coding is more cautionary: BOTH {adverse['fixability'].get('BOTH', {}).get('count', 0)} ({adverse['fixability'].get('BOTH', {}).get('pct', 0.0)}%), TIER2_INSTITUTIONAL_INTERMEDIATION {adverse['fixability'].get('TIER2_INSTITUTIONAL_INTERMEDIATION', {}).get('count', 0)} ({adverse['fixability'].get('TIER2_INSTITUTIONAL_INTERMEDIATION', {}).get('pct', 0.0)}%), NEITHER {adverse['fixability'].get('NEITHER', {}).get('count', 0)} ({adverse['fixability'].get('NEITHER', {}).get('pct', 0.0)}%).",
        "",
        "So the reporting architecture is a very strong evidentiary fit, but mostly as a floor rather than a complete solution. The missing records are usually request-level and decision-level, yet most losses are coded as needing both reporting architecture and institutional intermediation rather than reporting alone.",
        "",
        "## Bottom line",
        "",
        f"The exact 413-case public-defendant process subset is real, but only {universe['coded_public_defendant_process_cases']} cases are in the disability-wave coded tranche. Within the coded losses, the dominant failures are request translation, factual mapping, and jurisdictional gateway problems. The proposed architecture fits those failures closely because {adverse['component_case_shares_pct']['any_direct_reporting_architecture_pattern']}% of coded adverse losses already turn on records the regime could generate, above all request logs, notices, program decisions, and grievance trails. But the fixability coding also shows why the note should avoid overclaiming: most of these cases still need authority mapping, theory selection, and legal intermediation on top of better reporting.",
        "",
        "## Files produced by this task",
        "",
        "- `scripts/public_defendant_analysis.py`",
        "- `results/public_defendant_process_failure_results.json`",
        "- `results/public_defendant_process_failure_analysis.md`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    db_records = load_json(DB_PATH)
    merged_payload = load_json(MERGED_PATH)
    if not isinstance(db_records, list):
        raise TypeError(f"Expected list in {DB_PATH}, got {type(db_records).__name__}")
    if not isinstance(merged_payload, dict) or not isinstance(merged_payload.get("records"), list):
        raise TypeError(f"Expected dict with 'records' list in {MERGED_PATH}")

    merged_by_source = {
        normalize_text(record.get("source_file")): record
        for record in merged_payload["records"]
        if normalize_text(record.get("source_file"))
    }

    selected_records: List[Dict[str, Any]] = []
    for db_record in db_records:
        if not is_public_defendant_process_case(db_record):
            continue
        source_file = normalize_text(db_record.get("source_file"))
        merged_record = merged_by_source.get(source_file)
        enriched = dict(db_record)
        enriched["classification"] = extract_classification(merged_record)
        selected_records.append(enriched)

    if len(selected_records) != 413:
        raise RuntimeError(
            "Expected to reconstruct the established 413-case public-defendant-process universe, "
            f"but found {len(selected_records)} cases."
        )

    coded_records = [record for record in selected_records if isinstance(record.get("classification"), dict)]
    uncoded_records = [record for record in selected_records if not isinstance(record.get("classification"), dict)]
    adverse_outcome_losses = [record for record in coded_records if outcome(record) in LOSS_OUTCOMES]
    diagnosed_losses = [
        record
        for record in adverse_outcome_losses
        if classification_value(record, "pleading_failure_mechanism") not in UNDIAGNOSED_OR_NONLOSS_MECHANISMS
    ]

    adverse_skipped_count = len(adverse_outcome_losses) - len(diagnosed_losses)

    results: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_files": {
            "db_path": str(DB_PATH),
            "merged_path": str(MERGED_PATH),
        },
        "selection_method": {
            "selection_label": "public_defendant_process_cases",
            "selection_source": "Replicates scripts/unified_raw_text_target_inventory.py bucket logic to match the previously reported 413-case universe.",
            "selection_rule": {
                "screening_result": "YES",
                "defendant_type_in": sorted(PUBLIC_DEFENDANT_TYPES),
                "process_signal_any_of": [
                    "interactive_process_discussed is truthy",
                    f"primary_claim_type in {sorted(PROCESS_PRIMARY_CLAIM_TYPES)}",
                    "'accommodation' in brief_summary + key_holding",
                    "'request' in brief_summary + key_holding",
                    "'process' in brief_summary + key_holding",
                ],
            },
            "schema_adaptation": "Classification fields were read from unified_overnight.classification inside the merged disability-wave file, because the repository does not expose them as top-level columns.",
            "no_new_classification_performed": True,
        },
        "universe_counts": {
            "public_defendant_process_cases": len(selected_records),
            "coded_public_defendant_process_cases": len(coded_records),
            "uncoded_public_defendant_process_cases": len(uncoded_records),
            "coded_share_pct": pct(len(coded_records), len(selected_records)),
            "adverse_outcome_losses_total_413": sum(1 for record in selected_records if outcome(record) in LOSS_OUTCOMES),
            "adverse_outcome_losses_coded": len(adverse_outcome_losses),
            "diagnosed_losses_excluding_unclear_or_survival_labels": len(diagnosed_losses),
            "adverse_losses_unclear_or_survival_mechanism": adverse_skipped_count,
        },
        "defendant_type_counts": {
            "all_public_defendant_process_cases": ordered_counter(Counter(defendant_type(record) for record in selected_records)),
            "coded_public_defendant_process_cases": ordered_counter(Counter(defendant_type(record) for record in coded_records)),
            "diagnosed_losses": ordered_counter(Counter(defendant_type(record) for record in diagnosed_losses)),
        },
        "housing_type_counts": {
            "all_public_defendant_process_cases": ordered_counter(Counter(housing_type(record) for record in selected_records)),
            "coded_public_defendant_process_cases": ordered_counter(Counter(housing_type(record) for record in coded_records)),
            "diagnosed_losses": ordered_counter(Counter(housing_type(record) for record in diagnosed_losses)),
        },
        "outcome_counts": {
            "all_public_defendant_process_cases": ordered_counter(Counter(outcome(record) for record in selected_records)),
            "coded_public_defendant_process_cases": ordered_counter(Counter(outcome(record) for record in coded_records)),
        },
        "coded_cross_tabs": {
            "pleading_failure_mechanism_by_housing_type": crosstab_scalar(
                coded_records,
                lambda record: classification_value(record, "pleading_failure_mechanism"),
                housing_type,
            ),
            "institutional_function_missing_by_housing_type": crosstab_list(
                coded_records,
                lambda record: classification_list(record, "institutional_function_missing"),
                housing_type,
            ),
            "administratively_observable_fact_pattern_by_housing_type": crosstab_list(
                coded_records,
                lambda record: classification_list(record, "administratively_observable_fact_pattern"),
                housing_type,
            ),
        },
        "loss_analysis": {
            "loss_definition": {
                "adverse_outcome_losses": "outcome in {'DEFENDANT_WIN', 'PROCEDURAL'}",
                "diagnosed_losses": "adverse outcome losses excluding pleading_failure_mechanism in {'UNCLEAR', 'CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS'}",
            },
            "adverse_outcome_losses_coded": loss_architecture_fit(adverse_outcome_losses),
            "diagnosed_losses_excluding_unclear_or_survival_labels": loss_architecture_fit(diagnosed_losses),
        },
        "housing_type_highlights_diagnosed_losses": top_mechanisms_by_housing(diagnosed_losses),
        "notes": [
            "The requested 413-case public-defendant universe is a process-filtered subset, not the much broader set of all public or subsidized housing cases.",
            "Because only 278 of the 413 cases appear in the disability-wave matched tranche, cross-tabs necessarily rest on the coded subset rather than the full 413-case universe.",
            "I did not infer new classifications for uncoded cases; the results preserve the repository's existing classification boundary.",
        ],
    }

    memo = build_memo(results)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MEMO.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MEMO.write_text(memo, encoding="utf-8")

    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MEMO}")
    print(
        "Summary: "
        f"413 selected / {len(coded_records)} coded / {len(adverse_outcome_losses)} coded losses / {len(diagnosed_losses)} diagnosed losses"
    )


if __name__ == "__main__":
    main()
