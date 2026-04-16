#!/usr/bin/env python3
"""Unified overnight baseline analysis for the FHA unified database."""

from __future__ import annotations

import json
import math
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

P1_START = datetime(2022, 1, 1)
P1_END = datetime(2024, 6, 28)
P2_END = datetime(2025, 2, 5)
DECIDED_OUTCOMES = {"PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"}
PUBLIC_DEFENDANT_TYPES = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
INDIVIDUAL_PLAINTIFF_TYPES = {"INDIVIDUAL_TENANT", "INDIVIDUAL_PROSPECTIVE"}
INSTITUTIONAL_PLAINTIFF_TYPES = {"GROUP_HOME_OPERATOR", "FAIR_HOUSING_ORG", "GOVERNMENT"}
STAGE_ORDER = [
    "SCREENING_1915",
    "JURISDICTIONAL",
    "MTD",
    "PRELIMINARY_INJUNCTION",
    "DISCOVERY",
    "SUMMARY_JUDGMENT",
    "TRIAL",
    "CONSENT_DECREE",
    "APPEAL",
    "OTHER",
]
STAGE_RANK = {stage: idx for idx, stage in enumerate(STAGE_ORDER)}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def candidate_data_paths() -> List[Path]:
    ws = workspace_root()
    repo = repo_root()
    return [
        ws / "data" / "2" / "FHA_Unified_Database.json",
        repo / "data" / "FHA_Unified_Database.json",
        ws / "data" / "FHA_Unified_Database.json",
    ]


def resolve_input_path() -> Path:
    for path in candidate_data_paths():
        if path.exists():
            return path
    raise FileNotFoundError("Could not locate FHA_Unified_Database.json in workspace or repo data directories.")


def resolve_output_paths() -> tuple[Path, Path]:
    ws = workspace_root()
    results_dir = ws / "results"
    data_dir = ws / "data" / "2"
    results_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    return (
        results_dir / "unified_overnight_baseline_report.md",
        data_dir / "unified_overnight_baseline_tables.json",
    )


def load_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict):
        return list(data.values())
    if not isinstance(data, list):
        raise TypeError(f"Expected list or dict JSON payload, got {type(data).__name__}")
    return data


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


def truthy_pro_se(value: Any) -> bool:
    if value is True:
        return True
    return str(value).strip().lower() in {"true", "yes", "1"}


def normalize_text(value: Any, default: str = "UNKNOWN") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value)


def claims_for(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    claims = record.get("fha_claims") or []
    return [claim for claim in claims if isinstance(claim, dict)]


def furthest_stage(record: Dict[str, Any]) -> str:
    stages = []
    for claim in claims_for(record):
        stage = normalize_text(claim.get("stage")).upper()
        if stage != "UNKNOWN":
            stages.append(stage)
    if not stages:
        return "UNKNOWN"
    return max(stages, key=lambda stage: STAGE_RANK.get(stage, len(STAGE_ORDER)))


def dominant_dismissal_reason(record: Dict[str, Any]) -> str:
    reasons = [normalize_text(claim.get("dismissal_reason")).upper() for claim in claims_for(record)]
    reasons = [reason for reason in reasons if reason != "UNKNOWN"]
    if not reasons:
        return "UNKNOWN"
    counts = Counter(reasons)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def plaintiff_bucket(record: Dict[str, Any]) -> str:
    plaintiff_type = normalize_text(record.get("plaintiff_type")).upper()
    if plaintiff_type in INDIVIDUAL_PLAINTIFF_TYPES:
        return "INDIVIDUAL"
    if plaintiff_type in INSTITUTIONAL_PLAINTIFF_TYPES:
        return "INSTITUTIONAL"
    return "OTHER_OR_UNKNOWN"


def defendant_bucket(record: Dict[str, Any]) -> str:
    defendant_type = normalize_text(record.get("defendant_type")).upper()
    if defendant_type in PUBLIC_DEFENDANT_TYPES:
        return "PUBLIC"
    if defendant_type == "UNKNOWN":
        return "UNKNOWN"
    return "PRIVATE_OR_NONPUBLIC"


def pct(num: int, den: int) -> Optional[float]:
    if not den:
        return None
    return round((num / den) * 100, 1)


def summarize_outcomes(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(records)
    counts = Counter(normalize_text(row.get("outcome")).upper() for row in rows)
    total = len(rows)
    plaintiff_favorable = counts.get("PLAINTIFF_WIN", 0) + counts.get("MIXED", 0)
    return {
        "n": total,
        "outcome_counts": dict(sorted(counts.items())),
        "defendant_win_pct": pct(counts.get("DEFENDANT_WIN", 0), total),
        "plaintiff_win_pct": pct(counts.get("PLAINTIFF_WIN", 0), total),
        "plaintiff_favorable_pct": pct(plaintiff_favorable, total),
        "procedural_pct": pct(counts.get("PROCEDURAL", 0), total),
    }


def top_items(counter: Counter, limit: int = 15) -> List[Dict[str, Any]]:
    total = sum(counter.values())
    rows = []
    for key, value in counter.most_common(limit):
        rows.append({"label": key, "count": value, "pct": pct(value, total)})
    return rows


def to_markdown_table(headers: List[str], rows: List[List[Any]]) -> List[str]:
    rendered = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        rendered.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return rendered


def main() -> None:
    input_path = resolve_input_path()
    report_path, tables_path = resolve_output_paths()

    db = load_json(input_path)
    all_records = len(db)
    screened = [
        record
        for record in db
        if normalize_text(record.get("screening_result")).upper() != "NO"
        and record.get("case_name")
        and record.get("outcome") not in (None, "", "?")
    ]

    for record in screened:
        record["_period"] = assign_period(record)
        record["_has_disability"] = has_disability(record)
        record["_furthest_stage"] = furthest_stage(record)
        record["_dominant_dismissal_reason"] = dominant_dismissal_reason(record)
        record["_plaintiff_bucket"] = plaintiff_bucket(record)
        record["_defendant_bucket"] = defendant_bucket(record)

    disability_cases = [record for record in screened if record["_has_disability"]]
    non_disability_cases = [record for record in screened if not record["_has_disability"]]
    dated_cases = [record for record in screened if record["_period"]]

    claim_stage_counts = Counter()
    dismissal_reason_counts = Counter()
    for record in screened:
        for claim in claims_for(record):
            claim_stage_counts[normalize_text(claim.get("stage")).upper()] += 1
            dismissal_reason_counts[normalize_text(claim.get("dismissal_reason")).upper()] += 1

    period_stage_case = defaultdict(Counter)
    period_plaintiff_type = defaultdict(Counter)
    for record in dated_cases:
        period = record["_period"]
        period_stage_case[period][record["_furthest_stage"]] += 1
        period_plaintiff_type[period][normalize_text(record.get("plaintiff_type")).upper()] += 1

    disability_stage = Counter(record["_furthest_stage"] for record in disability_cases)
    nondisability_stage = Counter(record["_furthest_stage"] for record in non_disability_cases)

    public_cases = [record for record in screened if record["_defendant_bucket"] == "PUBLIC"]
    private_cases = [record for record in screened if record["_defendant_bucket"] == "PRIVATE_OR_NONPUBLIC"]
    institutional_cases = [record for record in screened if record["_plaintiff_bucket"] == "INSTITUTIONAL"]
    individual_cases = [record for record in screened if record["_plaintiff_bucket"] == "INDIVIDUAL"]

    output = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "input_path": str(input_path),
        "cohort_definition": "screening_result != NO, case_name present, outcome present",
        "counts": {
            "all_records": all_records,
            "screened_cases": len(screened),
            "dated_cases": len(dated_cases),
            "disability_cases": len(disability_cases),
            "non_disability_cases": len(non_disability_cases),
            "public_defendant_cases": len(public_cases),
            "private_or_nonpublic_defendant_cases": len(private_cases),
            "institutional_plaintiff_cases": len(institutional_cases),
            "individual_plaintiff_cases": len(individual_cases),
        },
        "dismissal_reason_distribution": {
            "claim_level_total": sum(dismissal_reason_counts.values()),
            "top_reasons": top_items(dismissal_reason_counts, limit=20),
        },
        "claim_stage_distribution": {
            "claim_level_total": sum(claim_stage_counts.values()),
            "top_stages": top_items(claim_stage_counts, limit=15),
        },
        "stage_distribution_by_period_case_level": {
            period: [{"stage": stage, "count": count, "pct": pct(count, sum(counter.values()))} for stage, count in counter.most_common()]
            for period, counter in sorted(period_stage_case.items())
        },
        "plaintiff_type_by_period": {
            period: [{"plaintiff_type": label, "count": count, "pct": pct(count, sum(counter.values()))} for label, count in counter.most_common()]
            for period, counter in sorted(period_plaintiff_type.items())
        },
        "disability_vs_non_disability": {
            "disability": summarize_outcomes(disability_cases) | {"stage_top": top_items(disability_stage, limit=10)},
            "non_disability": summarize_outcomes(non_disability_cases) | {"stage_top": top_items(nondisability_stage, limit=10)},
        },
        "public_vs_private": {
            "public": summarize_outcomes(public_cases),
            "private_or_nonpublic": summarize_outcomes(private_cases),
        },
        "institutional_vs_individual": {
            "institutional": summarize_outcomes(institutional_cases),
            "individual": summarize_outcomes(individual_cases),
        },
    }

    tables_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    top_dismissals = output["dismissal_reason_distribution"]["top_reasons"][:10]
    stage_rows = []
    for period in ("P1", "P2", "P3"):
        period_rows = output["stage_distribution_by_period_case_level"].get(period, [])[:5]
        for row in period_rows:
            stage_rows.append([period, row["stage"], row["count"], row["pct"]])

    plaintiff_rows = []
    for period in ("P1", "P2", "P3"):
        period_rows = output["plaintiff_type_by_period"].get(period, [])[:5]
        for row in period_rows:
            plaintiff_rows.append([period, row["plaintiff_type"], row["count"], row["pct"]])

    disability_summary = output["disability_vs_non_disability"]
    public_summary = output["public_vs_private"]
    inst_summary = output["institutional_vs_individual"]

    lines: List[str] = []
    lines.append("# Unified Overnight Baseline Report")
    lines.append("")
    lines.append(f"Generated: {output['generated_at']}")
    lines.append(f"Input: `{input_path}`")
    lines.append(f"Cohort definition: {output['cohort_definition']}")
    lines.append("")
    lines.append("## Cohort counts")
    lines.extend(
        to_markdown_table(
            ["Measure", "Count"],
            [[key, value] for key, value in output["counts"].items()],
        )
    )
    lines.append("")
    lines.append("## Current dismissal-reason distribution (claim level)")
    lines.extend(
        to_markdown_table(
            ["Dismissal reason", "Count", "Pct"],
            [[row["label"], row["count"], row["pct"]] for row in top_dismissals],
        )
    )
    lines.append("")
    lines.append("## Stage distributions by period (case-level furthest FHA stage)")
    lines.append("Case-level stage is derived from the furthest stage reached by any FHA claim in the record.")
    lines.extend(to_markdown_table(["Period", "Stage", "Count", "Pct"], stage_rows))
    lines.append("")
    lines.append("## Plaintiff-type distributions by period")
    lines.extend(to_markdown_table(["Period", "Plaintiff type", "Count", "Pct"], plaintiff_rows))
    lines.append("")
    lines.append("## Disability vs. non-disability stage/outcome differences")
    lines.extend(
        to_markdown_table(
            ["Group", "N", "Defendant win %", "Plaintiff favorable %", "Procedural %"],
            [
                [
                    "Disability",
                    disability_summary["disability"]["n"],
                    disability_summary["disability"]["defendant_win_pct"],
                    disability_summary["disability"]["plaintiff_favorable_pct"],
                    disability_summary["disability"]["procedural_pct"],
                ],
                [
                    "Non-disability",
                    disability_summary["non_disability"]["n"],
                    disability_summary["non_disability"]["defendant_win_pct"],
                    disability_summary["non_disability"]["plaintiff_favorable_pct"],
                    disability_summary["non_disability"]["procedural_pct"],
                ],
            ],
        )
    )
    lines.append("")
    lines.append("Top disability stages:")
    lines.extend(
        to_markdown_table(
            ["Stage", "Count", "Pct"],
            [[row["label"], row["count"], row["pct"]] for row in disability_summary["disability"]["stage_top"][:8]],
        )
    )
    lines.append("")
    lines.append("Top non-disability stages:")
    lines.extend(
        to_markdown_table(
            ["Stage", "Count", "Pct"],
            [[row["label"], row["count"], row["pct"]] for row in disability_summary["non_disability"]["stage_top"][:8]],
        )
    )
    lines.append("")
    lines.append("## Public/private differences")
    lines.extend(
        to_markdown_table(
            ["Group", "N", "Defendant win %", "Plaintiff favorable %", "Procedural %"],
            [
                [
                    "Public defendants",
                    public_summary["public"]["n"],
                    public_summary["public"]["defendant_win_pct"],
                    public_summary["public"]["plaintiff_favorable_pct"],
                    public_summary["public"]["procedural_pct"],
                ],
                [
                    "Private/nonpublic defendants",
                    public_summary["private_or_nonpublic"]["n"],
                    public_summary["private_or_nonpublic"]["defendant_win_pct"],
                    public_summary["private_or_nonpublic"]["plaintiff_favorable_pct"],
                    public_summary["private_or_nonpublic"]["procedural_pct"],
                ],
            ],
        )
    )
    lines.append("")
    lines.append("## Institutional/individual plaintiff differences")
    lines.extend(
        to_markdown_table(
            ["Group", "N", "Defendant win %", "Plaintiff favorable %", "Procedural %"],
            [
                [
                    "Institutional plaintiffs",
                    inst_summary["institutional"]["n"],
                    inst_summary["institutional"]["defendant_win_pct"],
                    inst_summary["institutional"]["plaintiff_favorable_pct"],
                    inst_summary["institutional"]["procedural_pct"],
                ],
                [
                    "Individual plaintiffs",
                    inst_summary["individual"]["n"],
                    inst_summary["individual"]["defendant_win_pct"],
                    inst_summary["individual"]["plaintiff_favorable_pct"],
                    inst_summary["individual"]["procedural_pct"],
                ],
            ],
        )
    )
    lines.append("")
    lines.append("## Notes")
    lines.append("- This baseline uses the unified screened cohort with non-empty outcomes (2,522 cases).")
    lines.append("- Dismissal reasons and stages are taken from nested `fha_claims` entries; case-level stage is a derived summary for period comparisons.")
    lines.append("- Institutional plaintiff comparisons use an intentionally conservative bucket: group home operators, fair housing organizations, and government plaintiffs.")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote report: {report_path}")
    print(f"Wrote tables: {tables_path}")
    print(f"Screened cohort: {len(screened)} cases")
    print(f"Disability cases: {len(disability_cases)} | Non-disability cases: {len(non_disability_cases)}")


if __name__ == "__main__":
    main()
