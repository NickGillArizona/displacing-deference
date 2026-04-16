#!/usr/bin/env python3
"""
Build the main citation-gap analysis infrastructure for the unified overnight FHA run.

Primary outputs:
- data/2/unified_overnight_citation_gap.json
- results/unified_overnight_citation_gap.md

Resilience rules:
- Prefers overnight enriched autopsy output when available.
- Falls back to structured heuristics if overnight/autopsy files are missing.
- Emits scaffolded outputs with blocker notes instead of crashing on absent overnight data.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

PROCEDURAL_TAGS = {"pleading_plausibility", "federal_procedure", "summary_judgment", "standing", "jurisdiction", "proof_structure", "burden_shifting"}
SUBSTANTIVE_TAGS = {"reasonable_accommodation", "zoning_group_home", "fha_substantive", "disparate_impact", "interference_coercion", "disability_status", "intent_framework", "fees_and_remedies"}
PUBLIC_DEFENDANTS = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
ACCOMMODATION_TYPES = {"reasonable_accommodation_denial", "reasonable_modification_denial"}


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


def normalize_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def summary_text(case: dict) -> str:
    return " ".join(
        part.strip()
        for part in [case.get("brief_summary") or "", case.get("key_holding") or ""]
        if isinstance(part, str) and part.strip()
    )


def primary_source_id(case: dict) -> str:
    return normalize_str(case.get("source_file") or case.get("case_name"), "UNKNOWN")


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"true", "yes", "1", "y"}


def render_table(rows: List[Tuple[str, Any]], headers: Tuple[str, str]) -> List[str]:
    out = [f"| {headers[0]} | {headers[1]} |", "|---|---:|"]
    for label, value in rows:
        out.append(f"| {label} | {value} |")
    return out


def expected_authorities(records: List[dict], min_count: int = 8) -> Dict[str, List[Tuple[str, int]]]:
    counter_by_claim: Dict[str, Counter] = defaultdict(Counter)
    for record in records:
        claim_type = normalize_str(record.get("primary_claim_type"), "UNKNOWN")
        for citation in record.get("normalized_citations", []):
            authority = normalize_str(citation.get("normalized"), "")
            tags = citation.get("doctrinal_functions") or []
            if authority and any(tag in SUBSTANTIVE_TAGS for tag in tags):
                counter_by_claim[claim_type][authority] += 1
    return {
        claim_type: [(authority, count) for authority, count in counter.most_common() if count >= min_count][:10]
        for claim_type, counter in counter_by_claim.items()
    }


def load_autopsy_lookup(base_data_dir: Path) -> Tuple[Dict[str, dict], str]:
    autopsy_path = base_data_dir / "unified_overnight_autopsy_analysis.json"
    if autopsy_path.exists():
        payload = read_json(autopsy_path, default={}) or {}
        lookup = {}
        for record in payload.get("records", []):
            key = normalize_str(record.get("source_file") or record.get("case_name"), "")
            if key:
                lookup[key] = record
        return lookup, normalize_str(payload.get("status"), "unknown")

    overnight_path = base_data_dir / "unified_overnight_results.json"
    overnight = read_json(overnight_path, default=[]) or []
    lookup = {}
    for item in overnight:
        key = normalize_str(item.get("source_file") or item.get("custom_id"), "")
        if key:
            lookup[key] = item
    return lookup, "overnight_only" if overnight else "missing"


def fallback_gap_signal(case: dict, citation_record: dict) -> str:
    claim_type = normalize_str(case.get("primary_claim_type")).lower()
    authorities = citation_record.get("normalized_citations", [])
    procedural = sum(1 for item in authorities if any(tag in PROCEDURAL_TAGS for tag in item.get("doctrinal_functions", [])))
    substantive = sum(1 for item in authorities if any(tag in SUBSTANTIVE_TAGS for tag in item.get("doctrinal_functions", [])))
    text = summary_text(case).lower()
    if claim_type in ACCOMMODATION_TYPES and procedural >= 1 and substantive == 0:
        return "HIGH"
    if case.get("defendant_type") in PUBLIC_DEFENDANTS and ("hearing" in text or "process" in text or "termination" in text) and substantive == 0:
        return "HIGH"
    if claim_type == "disparate_impact" and substantive == 0 and procedural >= 1:
        return "HIGH"
    if procedural > substantive:
        return "MEDIUM"
    if procedural and substantive:
        return "LOW"
    return "NONE"


def prevalence_differences(target: List[dict], rest: List[dict], min_target_n: int = 5, min_rest_n: int = 25) -> List[dict]:
    target_n = len(target)
    rest_n = len(rest)
    if target_n < min_target_n or rest_n < min_rest_n:
        return []

    def prevalence(records: List[dict]) -> Dict[str, float]:
        authority_cases: Dict[str, int] = Counter()
        for record in records:
            seen: Set[str] = set()
            for citation in record.get("normalized_citations", []):
                authority = normalize_str(citation.get("normalized"), "")
                tags = citation.get("doctrinal_functions") or []
                if authority and any(tag in SUBSTANTIVE_TAGS for tag in tags):
                    seen.add(authority)
            for authority in seen:
                authority_cases[authority] += 1
        return {authority: count / len(records) for authority, count in authority_cases.items()}

    t_prev = prevalence(target)
    r_prev = prevalence(rest)
    rows = []
    for authority, rest_rate in r_prev.items():
        target_rate = t_prev.get(authority, 0.0)
        diff = round(rest_rate - target_rate, 4)
        if diff > 0.05:
            rows.append(
                {
                    "authority": authority,
                    "target_prevalence": round(target_rate, 4),
                    "rest_prevalence": round(rest_rate, 4),
                    "undercitation_gap": diff,
                }
            )
    rows.sort(key=lambda item: (-item["undercitation_gap"], item["authority"]))
    return rows[:20]


def main() -> None:
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    base_data_dir = data_dir()
    db_path = base_data_dir / "FHA_Unified_Database.json"
    citation_path = base_data_dir / "unified_normalized_citations.json"
    inventory_path = base_data_dir / "unified_raw_text_target_inventory.json"
    out_json = base_data_dir / "unified_overnight_citation_gap.json"
    out_report = results_dir() / "unified_overnight_citation_gap.md"

    if not db_path.exists() or not citation_path.exists():
        payload = {
            "status": "blocked_missing_prerequisites",
            "generated_at": now,
            "missing_database": not db_path.exists(),
            "missing_citation_baseline": not citation_path.exists(),
            "db_path": str(db_path),
            "citation_path": str(citation_path),
        }
        write_json(out_json, payload)
        out_report.write_text(
            "# Unified Overnight Citation Gap Analysis\n\n"
            f"Status: blocked. Missing prerequisite input(s). Database exists={db_path.exists()}, citation baseline exists={citation_path.exists()}.\n",
            encoding="utf-8",
        )
        print(f"Wrote scaffold {out_json}")
        print(f"Wrote scaffold {out_report}")
        return

    database = read_json(db_path, default=[])
    cases = {primary_source_id(case): case for case in screened_cases(database)}
    citation_payload = read_json(citation_path, default={}) or {}
    raw_inventory = read_json(inventory_path, default={}) or {}
    autopsy_lookup, autopsy_status = load_autopsy_lookup(base_data_dir)

    raw_lookup: Dict[str, dict] = {}
    for bucket_records in (raw_inventory.get("buckets") or {}).values():
        for record in bucket_records:
            key = normalize_str(record.get("source_file") or record.get("case_name"), "")
            if key and key not in raw_lookup:
                raw_lookup[key] = record

    merged_records: List[dict] = []
    gap_counter = Counter()
    profile_counter = Counter()

    citation_records = citation_payload.get("records", [])
    expected_by_claim = expected_authorities(citation_records)

    for citation_record in citation_records:
        source_id = normalize_str(citation_record.get("source_file") or citation_record.get("case_name"), "")
        if not source_id or source_id not in cases:
            continue
        case = cases[source_id]
        autopsy_record = autopsy_lookup.get(source_id, {})
        if autopsy_record.get("classification"):
            classification = autopsy_record.get("classification", {})
        else:
            classification = autopsy_record.get("classification", autopsy_record) if autopsy_record else {}

        gap_signal = normalize_str(classification.get("doctrinal_gap_signal"), "") or fallback_gap_signal(case, citation_record)
        public_process = classification.get("public_process_failure_flag")
        if public_process is None:
            public_process = case.get("defendant_type") in PUBLIC_DEFENDANTS and (
                boolish(case.get("interactive_process_discussed"))
                or "process" in summary_text(case).lower()
                or "termination" in summary_text(case).lower()
                or "hearing" in summary_text(case).lower()
            )

        raw_priority = normalize_str(classification.get("raw_text_review_priority"), "") or ("HIGH" if gap_signal == "HIGH" else "MEDIUM" if gap_signal == "MEDIUM" else "LOW")
        confidence = normalize_str(classification.get("classification_confidence"), "") or "MEDIUM"

        procedural_authorities = []
        substantive_authorities = []
        uncoded_authorities = []
        tags_seen: Set[str] = set()
        for item in citation_record.get("normalized_citations", []):
            authority = normalize_str(item.get("normalized"), "")
            tags = item.get("doctrinal_functions") or []
            tags_seen.update(tags)
            if any(tag in PROCEDURAL_TAGS for tag in tags):
                procedural_authorities.append(authority)
            if any(tag in SUBSTANTIVE_TAGS for tag in tags):
                substantive_authorities.append(authority)
            if not tags or tags == ["uncoded_general_authority"]:
                uncoded_authorities.append(authority)

        procedural_unique = sorted(set(procedural_authorities))
        substantive_unique = sorted(set(substantive_authorities))
        profile = "balanced"
        if procedural_unique and not substantive_unique:
            profile = "procedural_only"
        elif substantive_unique and not procedural_unique:
            profile = "substantive_only"
        elif len(procedural_unique) >= 2 and len(substantive_unique) <= 1:
            profile = "procedural_heavy"
        elif len(substantive_unique) >= 2 and len(procedural_unique) <= 1:
            profile = "substantive_heavy"
        elif not procedural_unique and not substantive_unique:
            profile = "uncoded_or_sparse"

        claim_type = normalize_str(case.get("primary_claim_type"), "UNKNOWN")
        expected = [authority for authority, _count in expected_by_claim.get(claim_type, [])]
        missing_expected = [authority for authority in expected if authority not in substantive_unique][:5]
        omission_score = 0
        if profile in {"procedural_only", "procedural_heavy"}:
            omission_score += 2
        if gap_signal == "HIGH":
            omission_score += 2
        elif gap_signal == "MEDIUM":
            omission_score += 1
        if public_process:
            omission_score += 1
        if claim_type in ACCOMMODATION_TYPES and not substantive_unique:
            omission_score += 2
        if missing_expected:
            omission_score += 1
        if normalize_str(case.get("outcome")).upper() in {"DEFENDANT_WIN", "PROCEDURAL"}:
            omission_score += 1
        if bool(raw_lookup.get(source_id, {}).get("raw_text_available")):
            omission_score += 1

        record = {
            "source_file": case.get("source_file"),
            "case_name": case.get("case_name"),
            "year": case.get("year"),
            "court": case.get("court"),
            "circuit": case.get("circuit"),
            "plaintiff_type": case.get("plaintiff_type"),
            "defendant_type": case.get("defendant_type"),
            "primary_claim_type": case.get("primary_claim_type"),
            "outcome": case.get("outcome"),
            "pro_se": case.get("pro_se"),
            "classification_confidence": confidence,
            "raw_text_review_priority": raw_priority,
            "doctrinal_gap_signal": gap_signal,
            "public_process_failure_flag": bool(public_process),
            "citation_profile": profile,
            "procedural_authorities": procedural_unique,
            "substantive_authorities": substantive_unique,
            "uncoded_authorities": sorted(set(uncoded_authorities)),
            "missing_expected_substantive_authorities": missing_expected,
            "omission_score": omission_score,
            "raw_text_available": bool(raw_lookup.get(source_id, {}).get("raw_text_available")),
            "raw_text_path": raw_lookup.get(source_id, {}).get("raw_text_path"),
            "normalized_citation_count": citation_record.get("normalized_citation_count", 0),
        }
        merged_records.append(record)
        gap_counter[gap_signal] += 1
        profile_counter[profile] += 1

    def sort_records(records: List[dict], limit: int = 25) -> List[dict]:
        return sorted(
            records,
            key=lambda item: (-int(item.get("omission_score", 0)), -(1 if item.get("raw_text_available") else 0), -(int(item.get("year") or 0) if str(item.get("year") or "").isdigit() else 0), normalize_str(item.get("case_name"))),
        )[:limit]

    high_gap_cases = [r for r in merged_records if r.get("doctrinal_gap_signal") == "HIGH"]
    procedural_only_cases = [r for r in merged_records if r.get("citation_profile") == "procedural_only"]
    pro_se_procedural_only = [r for r in merged_records if r.get("pro_se") is True and r.get("citation_profile") in {"procedural_only", "procedural_heavy"}]
    public_process_gaps = [r for r in merged_records if r.get("public_process_failure_flag") and r.get("citation_profile") in {"procedural_only", "procedural_heavy"}]
    accommodation_gaps = [r for r in merged_records if normalize_str(r.get("primary_claim_type")).lower() in ACCOMMODATION_TYPES and not r.get("substantive_authorities")]
    open_textured_gaps = [r for r in merged_records if r.get("doctrinal_gap_signal") in {"HIGH", "MEDIUM"} and r.get("missing_expected_substantive_authorities")]

    target_groups = {
        "high_gap_cases": sort_records(high_gap_cases),
        "pro_se_procedural_only": sort_records(pro_se_procedural_only),
        "public_process_gap_cases": sort_records(public_process_gaps),
        "accommodation_without_substantive_authority": sort_records(accommodation_gaps),
        "open_textured_gap_cases": sort_records(open_textured_gaps),
    }

    undercitation = {
        name: prevalence_differences(group_records, [r for r in merged_records if r not in group_records])
        for name, group_records in {
            "high_gap_cases": high_gap_cases,
            "public_process_gap_cases": public_process_gaps,
            "accommodation_without_substantive_authority": accommodation_gaps,
        }.items()
    }

    payload = {
        "status": "ok" if merged_records else "empty",
        "generated_at": now,
        "inputs": {
            "database": str(db_path),
            "citation_baseline": str(citation_path),
            "raw_inventory_present": inventory_path.exists(),
            "autopsy_status": autopsy_status,
            "autopsy_present": (base_data_dir / "unified_overnight_autopsy_analysis.json").exists(),
            "overnight_results_present": (base_data_dir / "unified_overnight_results.json").exists(),
        },
        "summary": {
            "screened_citation_records": len(merged_records),
            "doctrinal_gap_signal": dict(gap_counter),
            "citation_profile": dict(profile_counter),
            "high_gap_cases": len(high_gap_cases),
            "procedural_only_cases": len(procedural_only_cases),
            "pro_se_procedural_only_cases": len(pro_se_procedural_only),
            "public_process_gap_cases": len(public_process_gaps),
            "accommodation_without_substantive_authority": len(accommodation_gaps),
        },
        "expected_substantive_authorities_by_claim_type": expected_by_claim,
        "target_groups": target_groups,
        "undercitation_candidates": undercitation,
        "records": merged_records,
    }
    write_json(out_json, payload)

    lines = [
        "# Unified Overnight Citation Gap Analysis",
        "",
        f"Generated: {now}",
        f"Status: {payload['status']}",
        "",
        "## Input status",
        "",
        f"- Citation baseline present: {citation_path.exists()}",
        f"- Raw-text inventory present: {inventory_path.exists()}",
        f"- Autopsy source status: {autopsy_status}",
        f"- Overnight results present: {payload['inputs']['overnight_results_present']}",
        "",
        "## Doctrinal gap signal distribution",
        "",
    ]
    lines.extend(render_table(sorted(gap_counter.items(), key=lambda kv: (-kv[1], kv[0])), ("Gap signal", "Cases")))
    lines.extend(["", "## Citation profile distribution", ""])
    lines.extend(render_table(sorted(profile_counter.items(), key=lambda kv: (-kv[1], kv[0])), ("Profile", "Cases")))
    lines.extend([
        "",
        "## High-value target groups",
        "",
        f"- High doctrinal-gap cases: {len(high_gap_cases)}",
        f"- Procedural-only citation cases: {len(procedural_only_cases)}",
        f"- Pro se procedural-only/procedural-heavy cases: {len(pro_se_procedural_only)}",
        f"- Public-process citation-gap cases: {len(public_process_gaps)}",
        f"- Accommodation cases missing substantive FHA authority: {len(accommodation_gaps)}",
        "",
        "## Target group exports",
        "",
        f"- `high_gap_cases`: {len(target_groups['high_gap_cases'])} prioritized records",
        f"- `pro_se_procedural_only`: {len(target_groups['pro_se_procedural_only'])} prioritized records",
        f"- `public_process_gap_cases`: {len(target_groups['public_process_gap_cases'])} prioritized records",
        f"- `accommodation_without_substantive_authority`: {len(target_groups['accommodation_without_substantive_authority'])} prioritized records",
        f"- `open_textured_gap_cases`: {len(target_groups['open_textured_gap_cases'])} prioritized records",
        "",
        "## Representative undercited substantive authorities for high-gap cases",
        "",
    ])
    high_gap_undercited = undercitation.get("high_gap_cases", [])
    if high_gap_undercited:
        lines.extend(render_table([(row['authority'], row['undercitation_gap']) for row in high_gap_undercited[:15]], ("Authority", "Undercitation gap")))
    else:
        lines.append("No stable undercitation comparison available.")
    lines.extend([
        "",
        "## Notes",
        "",
        "- This file is infrastructure for the doctrinal-gap lane, not a final note-facing synthesis.",
        "- Where autopsy outputs are missing, doctrinal-gap signals are inferred conservatively from citation mix, claim type, outcome, and public-process context.",
        f"- Detailed case-level output is in `{out_json}`.",
    ])
    out_report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_report}")
    print(f"Citation-gap records analyzed: {len(merged_records)}")


if __name__ == "__main__":
    main()
