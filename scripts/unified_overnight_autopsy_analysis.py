#!/usr/bin/env python3
"""
Build the main pleading-autopsy analysis infrastructure for the unified overnight FHA run.

Primary outputs:
- data/2/unified_overnight_autopsy_analysis.json
- results/unified_overnight_autopsy_analysis.md

The script is intentionally resilient:
- If `data/2/unified_overnight_results.json` exists, it uses the overnight enriched labels.
- If overnight results are missing or partial, it falls back to conservative structured-data heuristics.
- If baseline companion files are missing, it still emits a scaffolded report describing the blocker.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PUBLIC_DEFENDANTS = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
INSTITUTIONAL_PLAINTIFFS = {"GROUP_HOME_OPERATOR", "FAIR_HOUSING_ORG", "GOVERNMENT"}
OPEN_TEXTURED_TYPES = {"other", "UNCLEAR", "UNDETERMINED", "disparate_impact", "interference_coercion", "retaliation"}
PROCEDURAL_GATEWAY_REASONS = {"STANDING", "JURISDICTION", "MOOTNESS", "EXHAUSTION", "PRECLUSION", "STATUTE_OF_LIMITATIONS"}
PLEADING_REASONS = {"IQBAL_TWOMBLY", "NEXUS_FAILURE", "SCREENING_1915"}
MERITS_REASONS = {"DEFENDANT_PREVAILS_MERITS", "NO_DISCRIMINATORY_INTENT", "NO_REASONABLE_JURY", "NO_PRIMA_FACIE_CASE"}


def workspace_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    repo = script_dir.parent
    explicit = os.environ.get("FHA_WORKSPACE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    return repo.parent


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    ws = workspace_root() / "data" / "2"
    if ws.exists():
        return ws
    return repo_root() / "data"


def results_dir() -> Path:
    out = repo_root() / "results"
    out.mkdir(parents=True, exist_ok=True)
    return out


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def screened_cases(records: Iterable[dict]) -> List[dict]:
    return [r for r in records if r.get("screening_result") == "YES" and r.get("case_name")]


def summary_text(case: dict) -> str:
    return " ".join(
        part.strip()
        for part in [case.get("brief_summary") or "", case.get("key_holding") or ""]
        if isinstance(part, str) and part.strip()
    )


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def claim_rows(case: dict) -> List[dict]:
    rows = case.get("fha_claims") or []
    return [row for row in rows if isinstance(row, dict)]


def normalize_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def parse_year(case: dict) -> Optional[int]:
    value = case.get("year")
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except Exception:
        return None


def primary_source_id(case: dict) -> str:
    return normalize_str(case.get("source_file") or case.get("case_name"), "UNKNOWN")


def fallback_autopsy(case: dict, citation_lookup: Dict[str, dict], raw_inventory_lookup: Dict[str, dict]) -> Dict[str, Any]:
    source_id = primary_source_id(case)
    citation_record = citation_lookup.get(source_id, {})
    raw_record = raw_inventory_lookup.get(source_id, {})
    text = summary_text(case).lower()
    claims = claim_rows(case)
    posture = normalize_str(case.get("procedural_posture")).upper()
    outcome = normalize_str(case.get("outcome")).upper()
    claim_type = normalize_str(case.get("primary_claim_type")).lower()
    defendant_type = normalize_str(case.get("defendant_type")).upper()
    plaintiff_type = normalize_str(case.get("plaintiff_type")).upper()
    summary_len = len(summary_text(case))
    dismissal_reasons = {normalize_str(c.get("dismissal_reason")).upper() for c in claims if c.get("dismissal_reason")}
    stages = {normalize_str(c.get("stage")).upper() for c in claims if c.get("stage")}
    theories = {normalize_str(c.get("theory")).upper() for c in claims if c.get("theory")}
    normalized_citations = citation_record.get("normalized_citations", [])
    authorities = [item.get("normalized", "") for item in normalized_citations if isinstance(item, dict)]
    authority_text = " ".join(authorities)
    has_iqbal = "Iqbal" in authority_text or "Twombly" in authority_text
    public_process = (
        defendant_type in PUBLIC_DEFENDANTS
        and (
            boolish(case.get("interactive_process_discussed"))
            or boolish(case.get("delay_as_denial"))
            or "process" in text
            or "hearing" in text
            or "termination" in text
            or "voucher" in text
            or "authority" in text
            or "subsid" in text
        )
    )
    design_case = claim_type == "design_and_construction" or "design" in text and "construction" in text
    open_textured = claim_type in OPEN_TEXTURED_TYPES or not normalize_str(case.get("fha_section_cited")).strip()

    if outcome in {"PLAINTIFF_WIN", "MIXED"}:
        family = "NO_FAILURE_PLAINTIFF_WIN"
        mechanism = "CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS"
    elif posture in {"MOTION_TO_DISMISS", "SCREENING_1915"} or stages & {"MTD", "SCREENING_1915"}:
        if dismissal_reasons & PROCEDURAL_GATEWAY_REASONS:
            family = "PROCEDURAL_GATEWAY"
        elif dismissal_reasons & PLEADING_REASONS or has_iqbal:
            if public_process:
                family = "TRANSLATION"
            elif claim_type in {"reasonable_accommodation_denial", "reasonable_modification_denial"}:
                family = "TRANSLATION"
            elif claim_type in {"disparate_treatment", "retaliation"}:
                family = "CAUSAL_LINK"
            else:
                family = "FACTUAL_DETAIL"
        else:
            family = "UNCLEAR"

        if dismissal_reasons & {"STANDING", "JURISDICTION", "MOOTNESS"}:
            mechanism = "JURISDICTION_OR_STANDING"
        elif dismissal_reasons & {"STATUTE_OF_LIMITATIONS"}:
            mechanism = "LIMITATIONS_OR_TIMELINESS"
        elif public_process:
            mechanism = "INTERACTIVE_PROCESS_BREAKDOWN"
        elif claim_type in {"reasonable_accommodation_denial", "reasonable_modification_denial"}:
            mechanism = "REQUEST_NOT_ALLEGED" if summary_len < 900 else "DISABILITY_NEXUS_MISSING"
        elif claim_type == "disparate_impact":
            mechanism = "POLICY_OR_PRACTICE_NOT_SPECIFIED"
        elif claim_type in {"disparate_treatment", "retaliation"}:
            mechanism = "ADVERSE_ACTION_NOT_CONNECTED"
        elif open_textured:
            mechanism = "STATUTORY_HOOK_UNCLEAR"
        else:
            mechanism = "ELEMENTS_NOT_TIED_TO_FACTS"
    elif design_case or stages & {"SUMMARY_JUDGMENT", "TRIAL"} or dismissal_reasons & MERITS_REASONS:
        family = "MERITS_EVIDENCE"
        mechanism = "TECHNICAL_PROOF_GAP" if design_case else "ELEMENTS_NOT_TIED_TO_FACTS"
    elif public_process and outcome == "DEFENDANT_WIN":
        family = "NO_FAILURE_DEFENDANT_WIN"
        mechanism = "INTERACTIVE_PROCESS_BREAKDOWN"
    elif outcome == "DEFENDANT_WIN":
        family = "NO_FAILURE_DEFENDANT_WIN"
        mechanism = "UNCLEAR"
    else:
        family = "UNCLEAR"
        mechanism = "UNCLEAR"

    missing_functions: List[str] = []
    observable_facts: List[str] = []

    if mechanism in {"REQUEST_NOT_ALLEGED", "DISABILITY_NEXUS_MISSING", "STATUTORY_HOOK_UNCLEAR"}:
        missing_functions.extend(["THEORY_SELECTION", "FACT_DEVELOPMENT"])
    if mechanism in {"ELEMENTS_NOT_TIED_TO_FACTS", "ADVERSE_ACTION_NOT_CONNECTED", "POLICY_OR_PRACTICE_NOT_SPECIFIED"}:
        missing_functions.extend(["FACT_DEVELOPMENT", "DOCUMENT_ASSEMBLY"])
    if public_process:
        missing_functions.append("NEGOTIATION_OR_INTERACTIVE_PROCESS_SUPPORT")
        missing_functions.append("ADMINISTRATIVE_RECORD_BUILDING")
    if design_case:
        missing_functions = ["EXPERT_OR_TECHNICAL_TRANSLATION"]
    if family == "PROCEDURAL_GATEWAY":
        missing_functions = ["JURISDICTIONAL_TRIAGE"]
    if family in {"NO_FAILURE_PLAINTIFF_WIN", "NO_FAILURE_DEFENDANT_WIN"} and not public_process and not design_case:
        missing_functions = ["NONE_APPARENT"]
    if not missing_functions:
        missing_functions = ["UNCLEAR"]

    if claim_type in {"reasonable_accommodation_denial", "reasonable_modification_denial"} or "accommodation" in text:
        observable_facts.extend(["DOCUMENTED_REQUEST", "NOTICE_OR_TIMELINE_RECORD"])
    if boolish(case.get("interactive_process_discussed")) or boolish(case.get("delay_as_denial")):
        observable_facts.append("DENIAL_OR_NO_RESPONSE_RECORD")
    if public_process:
        observable_facts.extend(["PUBLIC_PROGRAM_RULE_OR_DECISION", "HEARING_OR_GRIEVANCE_RECORD"])
    if design_case:
        observable_facts = ["PHYSICAL_ACCESS_BARRIER", "INSPECTION_OR_MEASUREMENT_DATA"]
    elif claim_type == "disparate_impact":
        observable_facts.extend(["LEASE_OR_POLICY_TEXT", "COMPARATOR_OR_PATTERN_EVIDENCE"])
    if not observable_facts:
        observable_facts = ["UNCLEAR"]

    doctrinal_gap = "NONE"
    if open_textured and normalize_str(case.get("outcome")).upper() in {"DEFENDANT_WIN", "PROCEDURAL", "UNDETERMINED"}:
        doctrinal_gap = "HIGH" if len(authorities) >= 3 else "MEDIUM"
    elif public_process or plaintiff_type in INSTITUTIONAL_PLAINTIFFS:
        doctrinal_gap = "MEDIUM"
    elif has_iqbal and not authorities:
        doctrinal_gap = "LOW"

    confidence = "HIGH"
    if summary_len < 900 or raw_record.get("match_strategy") == "unresolved":
        confidence = "MEDIUM"
    if summary_len < 500 or not claims:
        confidence = "LOW"

    raw_priority = "LOW"
    if confidence == "LOW" or (doctrinal_gap in {"HIGH", "MEDIUM"} and summary_len < 900):
        raw_priority = "HIGH"
    elif confidence == "MEDIUM" or public_process:
        raw_priority = "MEDIUM"

    if design_case:
        fixability = "NEITHER"
    elif family == "PROCEDURAL_GATEWAY":
        fixability = "TIER2_INSTITUTIONAL_INTERMEDIATION"
    elif public_process and mechanism in {"INTERACTIVE_PROCESS_BREAKDOWN", "REQUEST_NOT_ALLEGED", "DISABILITY_NEXUS_MISSING"}:
        fixability = "BOTH"
    elif mechanism in {"REQUEST_NOT_ALLEGED", "DISABILITY_NEXUS_MISSING", "STATUTORY_HOOK_UNCLEAR"}:
        fixability = "BOTH"
    elif mechanism in {"ADVERSE_ACTION_NOT_CONNECTED", "ELEMENTS_NOT_TIED_TO_FACTS", "POLICY_OR_PRACTICE_NOT_SPECIFIED"}:
        fixability = "TIER2_INSTITUTIONAL_INTERMEDIATION"
    else:
        fixability = "UNCLEAR"

    def uniq(items: List[str], limit: int) -> List[str]:
        out: List[str] = []
        for item in items:
            if item not in out:
                out.append(item)
        return out[:limit]

    return {
        "pleading_failure_family": family,
        "pleading_failure_mechanism": mechanism,
        "institutional_function_missing": uniq(missing_functions, 3),
        "administratively_observable_fact_pattern": uniq(observable_facts, 4),
        "raw_text_review_priority": raw_priority,
        "doctrinal_gap_signal": doctrinal_gap,
        "public_process_failure_flag": public_process,
        "tier1_tier2_fixability": fixability,
        "classification_confidence": confidence,
        "reasoning": "Fallback heuristic derived from procedural posture, outcome, claim type, structured dismissal signals, and summary compression.",
    }


def load_companion_lookups(base_data_dir: Path) -> Tuple[Dict[str, dict], Dict[str, dict]]:
    citation_lookup: Dict[str, dict] = {}
    citation_payload = read_json(base_data_dir / "unified_normalized_citations.json", default={}) or {}
    for record in citation_payload.get("records", []):
        key = normalize_str(record.get("source_file") or record.get("case_name"), "")
        if key:
            citation_lookup[key] = record

    raw_lookup: Dict[str, dict] = {}
    raw_payload = read_json(base_data_dir / "unified_raw_text_target_inventory.json", default={}) or {}
    for bucket_records in (raw_payload.get("buckets") or {}).values():
        for record in bucket_records:
            key = normalize_str(record.get("source_file") or record.get("case_name"), "")
            if key and key not in raw_lookup:
                raw_lookup[key] = record
    return citation_lookup, raw_lookup


def render_table(rows: List[Tuple[str, int]], headers: Tuple[str, str]) -> List[str]:
    out = [f"| {headers[0]} | {headers[1]} |", "|---|---:|"]
    for label, value in rows:
        out.append(f"| {label} | {value} |")
    return out


def build_cross_tab(records: List[dict], row_field: str, col_field: str, row_values: List[str], col_values: List[str]) -> Dict[str, Dict[str, int]]:
    table: Dict[str, Dict[str, int]] = {}
    for row_value in row_values:
        table[row_value] = {col_value: 0 for col_value in col_values}
    for record in records:
        row_key = normalize_str(record.get(row_field), "UNKNOWN")
        col_key = normalize_str(record.get(col_field), "UNKNOWN")
        if row_key not in table:
            table[row_key] = {col_value: 0 for col_value in col_values}
        if col_key not in table[row_key]:
            table[row_key][col_key] = 0
        table[row_key][col_key] += 1
    return table


def top_records(records: List[dict], score_key: str, limit: int = 20) -> List[dict]:
    def sort_key(item: dict) -> Tuple[Any, ...]:
        year = parse_year(item) or 0
        return (-float(item.get(score_key, 0) or 0), -(1 if item.get("raw_text_available") else 0), -year, normalize_str(item.get("case_name")))
    return sorted(records, key=sort_key)[:limit]


def main() -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    base_data_dir = data_dir()
    db_path = base_data_dir / "FHA_Unified_Database.json"
    overnight_path = base_data_dir / "unified_overnight_results.json"
    out_json = base_data_dir / "unified_overnight_autopsy_analysis.json"
    out_report = results_dir() / "unified_overnight_autopsy_analysis.md"

    if not db_path.exists():
        payload = {
            "status": "blocked_missing_database",
            "generated_at": now,
            "db_path": str(db_path),
            "message": "Missing FHA_Unified_Database.json; autopsy infrastructure scaffold created but analysis could not run.",
        }
        write_json(out_json, payload)
        out_report.write_text(
            "# Unified Overnight Autopsy Analysis\n\n"
            f"Status: blocked. Missing database input `{db_path}`.\n",
            encoding="utf-8",
        )
        print(f"Wrote scaffold {out_json}")
        print(f"Wrote scaffold {out_report}")
        return

    database = read_json(db_path, default=[])
    cases = screened_cases(database)
    overnight_results = read_json(overnight_path, default=[]) or []
    overnight_lookup = {
        normalize_str(item.get("source_file") or item.get("custom_id"), ""): item
        for item in overnight_results
        if isinstance(item, dict)
    }
    citation_lookup, raw_inventory_lookup = load_companion_lookups(base_data_dir)

    merged_records: List[dict] = []
    source_counter = Counter()
    family_counter = Counter()
    mechanism_counter = Counter()
    confidence_counter = Counter()
    raw_priority_counter = Counter()
    gap_counter = Counter()
    fixability_counter = Counter()

    for case in cases:
        source_id = primary_source_id(case)
        overnight = overnight_lookup.get(source_id)
        citation_record = citation_lookup.get(source_id, {})
        raw_record = raw_inventory_lookup.get(source_id, {})
        if overnight and isinstance(overnight.get("classification"), dict):
            classification = overnight["classification"]
            classification_source = "overnight_batch"
        else:
            classification = fallback_autopsy(case, citation_lookup, raw_inventory_lookup)
            classification_source = "fallback_heuristic"

        source_counter[classification_source] += 1
        family_counter[normalize_str(classification.get("pleading_failure_family"), "UNKNOWN")] += 1
        mechanism_counter[normalize_str(classification.get("pleading_failure_mechanism"), "UNKNOWN")] += 1
        confidence_counter[normalize_str(classification.get("classification_confidence"), "UNKNOWN")] += 1
        raw_priority_counter[normalize_str(classification.get("raw_text_review_priority"), "UNKNOWN")] += 1
        gap_counter[normalize_str(classification.get("doctrinal_gap_signal"), "UNKNOWN")] += 1
        fixability_counter[normalize_str(classification.get("tier1_tier2_fixability"), "UNKNOWN")] += 1

        merged_records.append(
            {
                "source_file": case.get("source_file"),
                "case_name": case.get("case_name"),
                "year": case.get("year"),
                "court": case.get("court"),
                "circuit": case.get("circuit"),
                "plaintiff_type": case.get("plaintiff_type"),
                "defendant_type": case.get("defendant_type"),
                "primary_claim_type": case.get("primary_claim_type"),
                "procedural_posture": case.get("procedural_posture"),
                "outcome": case.get("outcome"),
                "pro_se": case.get("pro_se"),
                "summary_length": len(summary_text(case)),
                "citation_count": citation_record.get("normalized_citation_count", len(case.get("key_cases_cited") or [])),
                "raw_text_available": bool(raw_record.get("raw_text_available")),
                "raw_text_path": raw_record.get("raw_text_path"),
                "classification_source": classification_source,
                "classification": classification,
                "input_tokens": overnight.get("input_tokens") if overnight else None,
                "output_tokens": overnight.get("output_tokens") if overnight else None,
            }
        )

    pro_se_records = [r for r in merged_records if r.get("pro_se") is True]
    represented_records = [r for r in merged_records if r.get("pro_se") is False]
    public_process = [r for r in merged_records if r["classification"].get("public_process_failure_flag") is True]
    high_priority = [r for r in merged_records if r["classification"].get("raw_text_review_priority") == "HIGH"]
    high_gap = [r for r in merged_records if r["classification"].get("doctrinal_gap_signal") == "HIGH"]
    low_conf = [r for r in merged_records if r["classification"].get("classification_confidence") == "LOW"]
    institutional_missing = [
        r for r in merged_records
        if "THEORY_SELECTION" in (r["classification"].get("institutional_function_missing") or [])
        or "FACT_DEVELOPMENT" in (r["classification"].get("institutional_function_missing") or [])
    ]

    subgroup_family = {
        "pro_se": dict(Counter(r["classification"].get("pleading_failure_family") for r in pro_se_records)),
        "represented": dict(Counter(r["classification"].get("pleading_failure_family") for r in represented_records)),
        "public_process": dict(Counter(r["classification"].get("pleading_failure_family") for r in public_process)),
        "high_gap": dict(Counter(r["classification"].get("pleading_failure_family") for r in high_gap)),
    }

    crosstab = build_cross_tab(
        merged_records,
        "plaintiff_type",
        "classification_source",
        sorted({normalize_str(r.get("plaintiff_type"), "UNKNOWN") for r in merged_records}),
        ["overnight_batch", "fallback_heuristic"],
    )

    payload = {
        "status": "ok" if overnight_results else "fallback_only",
        "generated_at": now,
        "inputs": {
            "database": str(db_path),
            "overnight_results": str(overnight_path),
            "overnight_results_present": overnight_path.exists(),
            "citation_baseline_present": (base_data_dir / "unified_normalized_citations.json").exists(),
            "raw_text_inventory_present": (base_data_dir / "unified_raw_text_target_inventory.json").exists(),
        },
        "coverage": {
            "screened_case_count": len(cases),
            "overnight_result_rows": len(overnight_results),
            "classification_source_counts": dict(source_counter),
            "overnight_coverage_rate": round(source_counter.get("overnight_batch", 0) / len(cases), 4) if cases else 0.0,
        },
        "distributions": {
            "pleading_failure_family": dict(family_counter),
            "pleading_failure_mechanism": dict(mechanism_counter),
            "classification_confidence": dict(confidence_counter),
            "raw_text_review_priority": dict(raw_priority_counter),
            "doctrinal_gap_signal": dict(gap_counter),
            "tier1_tier2_fixability": dict(fixability_counter),
        },
        "subgroups": {
            "family_by_key_group": subgroup_family,
            "counts": {
                "pro_se": len(pro_se_records),
                "represented": len(represented_records),
                "public_process": len(public_process),
                "high_priority_raw_text": len(high_priority),
                "high_doctrinal_gap": len(high_gap),
                "low_confidence": len(low_conf),
                "institutional_function_missing_core": len(institutional_missing),
            },
            "classification_source_by_plaintiff_type": crosstab,
        },
        "queues": {
            "top_high_priority_raw_text": top_records([
                {**r, "priority_score": (3 if r['classification'].get('classification_confidence') == 'LOW' else 0) + (2 if r['classification'].get('doctrinal_gap_signal') == 'HIGH' else 0) + (1 if r.get('raw_text_available') else 0)}
                for r in high_priority
            ], "priority_score", 25),
            "top_public_process_cases": top_records([
                {**r, "priority_score": (2 if r.get('raw_text_available') else 0) + (2 if r['classification'].get('doctrinal_gap_signal') in {'HIGH', 'MEDIUM'} else 0) + (1 if r['classification'].get('classification_confidence') == 'LOW' else 0)}
                for r in public_process
            ], "priority_score", 25),
            "top_high_gap_cases": top_records([
                {**r, "priority_score": (2 if r.get('raw_text_available') else 0) + (2 if r['classification'].get('raw_text_review_priority') == 'HIGH' else 0) + (1 if r['classification'].get('classification_confidence') != 'HIGH' else 0)}
                for r in high_gap
            ], "priority_score", 25),
        },
        "records": merged_records,
    }
    write_json(out_json, payload)

    lines = [
        "# Unified Overnight Autopsy Analysis",
        "",
        f"Generated: {now}",
        f"Status: {payload['status']}",
        "",
        "## Input coverage",
        "",
        f"- Screened cases analyzed: {len(cases)}",
        f"- Overnight result rows present: {len(overnight_results)}",
        f"- Cases using overnight labels: {source_counter.get('overnight_batch', 0)}",
        f"- Cases using fallback heuristics: {source_counter.get('fallback_heuristic', 0)}",
        f"- Citation baseline present: {payload['inputs']['citation_baseline_present']}",
        f"- Raw-text inventory present: {payload['inputs']['raw_text_inventory_present']}",
        "",
        "## Pleading failure family distribution",
        "",
    ]
    lines.extend(render_table(family_counter.most_common(), ("Family", "Cases")))
    lines.extend([
        "",
        "## Pleading mechanism distribution",
        "",
    ])
    lines.extend(render_table(mechanism_counter.most_common(20), ("Mechanism", "Cases")))
    lines.extend([
        "",
        "## Confidence / review queue status",
        "",
    ])
    lines.extend(render_table(confidence_counter.most_common(), ("Confidence", "Cases")))
    lines.extend([""])
    lines.extend(render_table(raw_priority_counter.most_common(), ("Raw-text review priority", "Cases")))
    lines.extend([
        "",
        "## Key subgroup counts",
        "",
        f"- Pro se cases: {len(pro_se_records)}",
        f"- Represented cases: {len(represented_records)}",
        f"- Public-process flagged cases: {len(public_process)}",
        f"- High doctrinal-gap cases: {len(high_gap)}",
        f"- High raw-text-priority cases: {len(high_priority)}",
        f"- Low-confidence cases: {len(low_conf)}",
        f"- Core institutional-missing queue (theory/fact development): {len(institutional_missing)}",
        "",
        "## Pro se family distribution",
        "",
    ])
    lines.extend(render_table(sorted(subgroup_family["pro_se"].items(), key=lambda kv: (-kv[1], kv[0])), ("Family", "Cases")))
    lines.extend(["", "## Represented family distribution", ""])
    lines.extend(render_table(sorted(subgroup_family["represented"].items(), key=lambda kv: (-kv[1], kv[0])), ("Family", "Cases")))
    lines.extend(["", "## Public-process family distribution", ""])
    lines.extend(render_table(sorted(subgroup_family["public_process"].items(), key=lambda kv: (-kv[1], kv[0])), ("Family", "Cases")))
    lines.extend([
        "",
        "## Immediate queues",
        "",
        f"- Top high-priority raw-text queue exported in JSON: {len(payload['queues']['top_high_priority_raw_text'])} records.",
        f"- Top public-process queue exported in JSON: {len(payload['queues']['top_public_process_cases'])} records.",
        f"- Top doctrinal-gap queue exported in JSON: {len(payload['queues']['top_high_gap_cases'])} records.",
        "",
        "## Notes",
        "",
        "- This file is the infrastructure layer for the overnight pleading-autopsy lane rather than a polished substantive memo.",
        "- When `unified_overnight_results.json` is absent or incomplete, the script uses conservative structured-data fallback classifications and marks that coverage explicitly.",
        f"- Detailed merged case-level output is in `{out_json}`.",
    ])
    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_report}")
    print(f"Autopsy status: {payload['status']}")
    print(f"Overnight-labeled cases: {source_counter.get('overnight_batch', 0)} / {len(cases)}")


if __name__ == "__main__":
    main()
