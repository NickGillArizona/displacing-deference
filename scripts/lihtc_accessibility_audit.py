#!/usr/bin/env python3
"""
Audit the LIHTC accessibility reporting gap using the repo-local HUD LIHTC public
file plus the completed 2023 Kelsey state-category reconstruction.

Outputs:
- results/lihtc_accessibility_audit_results.json
- results/lihtc_accessibility_audit_analysis.md

Important interpretive caution:
This script reports observed program-overlap proxies from HUD's public LIHTC file.
Those proxies are not definitive Section 504 applicability determinations.
The Kelsey state/QAP categories used here are reconstructed current/2023
categories mapped onto HUD's public LIHTC stock, not project-year historical
determinations at the time of placement in service.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
DATA_DIR = REPO_DIR / "data"
LIHTC_DIR = DATA_DIR / "lihtc"
RESULTS_DIR = REPO_DIR / "results"

INPUT_CSV = LIHTC_DIR / "LIHTCPUB.csv"
INPUT_DICTIONARY = LIHTC_DIR / "lihtc_dictionary.txt"
KELSEY_FACTSHEET = DATA_DIR / "The-Kelsey-State-LIHTC-Accessibility-Factsheet.txt"
KELSEY_LAYOUT = DATA_DIR / "The-Kelsey-State-LIHTC-Accessibility-Factsheet-layout.txt"
KELSEY_COMMENTS = DATA_DIR / "The-Kelsey-504-ANPRM-Comments.txt"

OUTPUT_JSON = RESULTS_DIR / "lihtc_accessibility_audit_results.json"
OUTPUT_MD = RESULTS_DIR / "lihtc_accessibility_audit_analysis.md"

FILES_CREATED_OR_MODIFIED = [
    "scripts/lihtc_accessibility_audit.py",
    "results/lihtc_accessibility_audit_results.json",
    "results/lihtc_accessibility_audit_analysis.md",
]

CATEGORY_ORDER = [
    "more_than_504",
    "requires_504",
    "less_than_504",
    "incentives",
    "no_requirements",
]

CATEGORY_LABELS = {
    "more_than_504": "Requires more than Section 504",
    "requires_504": "Requires Section 504",
    "less_than_504": "Requirements less than Section 504",
    "incentives": "Incentives for accessible units",
    "no_requirements": "No observed QAP accessibility requirement",
}

CATEGORY_STATES = {
    "more_than_504": ["CA", "IL"],
    "requires_504": ["AK", "FL", "GA", "KS", "ME", "MD", "MA", "NH", "NY", "OH", "SD", "TX", "WV"],
    "less_than_504": ["AZ", "IN", "IA", "KY", "NE", "NC", "WA"],
    "incentives": ["AL", "DE", "MN", "MS", "MT", "PA", "RI", "SC", "VA"],
    "no_requirements": ["AR", "CO", "CT", "HI", "ID", "LA", "MI", "MO", "NV", "NJ", "NM", "ND", "OK", "OR", "TN", "UT", "VT", "WI", "WY"],
}

KELSEY_STATE_TO_CATEGORY = {
    state: category
    for category, states in CATEGORY_STATES.items()
    for state in states
}

NUMERIC_COLUMNS = ["n_units", "n_unitsr", "yr_pis"]
PROGRAM_FLAG_COLUMNS = [
    "home",
    "cdbg",
    "htf",
    "mff_ra",
    "fmha_514",
    "fmha_515",
    "fmha_538",
    "fha",
    "hopevi",
    "tcap",
    "tcep",
    "rad",
]

STRICT_OVERLAP_FIELDS = [
    "home",
    "cdbg",
    "htf",
    "mff_ra",
    "fmha_514",
    "fmha_515",
    "hopevi",
    "tcap",
    "tcep",
    "rad",
]

STRICT_OVERLAP_LABELS = {
    "home": "HOME",
    "cdbg": "CDBG",
    "htf": "HTF",
    "mff_ra": "MFF_RA",
    "fmha_514": "FMHA_514",
    "fmha_515": "FMHA_515",
    "hopevi": "HOPEVI",
    "tcap": "TCAP",
    "tcep": "TCEP",
    "rad": "RAD",
    "fha": "FHA",
    "fmha_538": "FMHA_538",
}

RENTASSIST_LABELS = {
    "1": "Federal",
    "2": "State",
    "3": "Both Federal and State",
    "4": "Neither",
    "5": "Unknown whether Federal or State",
}

INVENTORY_KEYWORD_PATTERN = re.compile(
    r"\b(?:access|accessible|accessibility|ada|ufas|wheelchair|mobility|hearing|visual|sensory)\b",
    re.IGNORECASE,
)

TRGT_DIS_PATTERN = re.compile(r"TRGT_DIS|disabled", re.IGNORECASE)

INPUT_USECOLS = [
    "hud_id",
    "proj_st",
    "n_units",
    "n_unitsr",
    "yr_pis",
    "trgt_dis",
    "rentassist",
    *PROGRAM_FLAG_COLUMNS,
]

FIELD_FIRST_REQUESTED = {
    "2003": ["HOME", "CDBG", "FHA", "HOPEVI", "TRGT_POP", "TRGT_FAM", "TRGT_ELD", "TRGT_DIS", "TRGT_HML", "TRGT_OTH", "TRGT_SPC"],
    "2006": ["INC_CEIL", "LOW_CEIL", "HOME_AMT", "CDBG_AMT", "RENTASST"],
    "2012": ["TCAP", "TCAP_AMT", "TCEP", "TCEP_AMT"],
    "2018": ["SCATTERED", "RESYND", "HTF", "HTF_AMT", "RAD", "QOZF", "QOZF_AMT"],
}

DECADE_WINDOWS = [
    ("1987-1996", 1987, 1996),
    ("1997-2006", 1997, 2006),
    ("2007-2016", 2007, 2016),
    ("2017-2023", 2017, 2023),
]

CATEGORY_GROUPS = [
    {
        "group": "construction_requirement_any_level",
        "label": "Any QAP accessibility construction requirement",
        "categories": ["more_than_504", "requires_504", "less_than_504"],
    },
    {
        "group": "requires_or_exceeds_504",
        "label": "Requires or exceeds Section 504",
        "categories": ["more_than_504", "requires_504"],
    },
    {
        "group": "incentives_only",
        "label": "Incentives only",
        "categories": ["incentives"],
    },
    {
        "group": "no_requirements",
        "label": "No QAP accessibility requirement observed",
        "categories": ["no_requirements"],
    },
]


def ensure_inputs() -> None:
    required = [INPUT_CSV, INPUT_DICTIONARY, KELSEY_FACTSHEET, KELSEY_COMMENTS]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required input files: " + ", ".join(missing))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_string(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def share(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 6)


def pct(numerator: int | float, denominator: int | float) -> float | None:
    value = share(numerator, denominator)
    return None if value is None else round(value * 100.0, 2)


def fmt_int(value: int | float | None) -> str:
    if value is None:
        return "N/A"
    return f"{int(round(float(value))):,}"


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def markdown_table(headers: list[str], rows: Iterable[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def read_text_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def file_header_columns(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        first_line = handle.readline().strip()
    return [column.strip() for column in first_line.split(",")]


def line_matches(lines: list[str], pattern: re.Pattern[str]) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for index, line in enumerate(lines, start=1):
        if pattern.search(line):
            matches.append({"line_number": index, "text": line.strip()})
    return matches


def trgt_dis_excerpt(lines: list[str]) -> list[dict[str, object]]:
    for index, line in enumerate(lines):
        if line.strip().upper() == "TRGT_DIS":
            excerpt: list[dict[str, object]] = []
            for offset in range(index, min(index + 5, len(lines))):
                excerpt.append({"line_number": offset + 1, "text": lines[offset].strip()})
            return excerpt
    return []


def load_lihtc() -> pd.DataFrame:
    frame = pd.read_csv(INPUT_CSV, usecols=INPUT_USECOLS, dtype=str, low_memory=False)
    for column in frame.columns:
        if column not in NUMERIC_COLUMNS:
            frame[column] = clean_string(frame[column])
    for column in NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame["units_final"] = (
        frame["n_units"].where(frame["n_units"].fillna(0) > 0, frame["n_unitsr"]).fillna(0).round().astype(int)
    )
    frame["kelsey_category"] = frame["proj_st"].map(KELSEY_STATE_TO_CATEGORY)
    return frame


def summarize_mask(frame: pd.DataFrame, mask: pd.Series, properties_denominator: int | None = None, units_denominator: int | None = None) -> dict[str, object]:
    properties = int(mask.sum())
    units = int(frame.loc[mask, "units_final"].sum())
    result: dict[str, object] = {
        "properties": properties,
        "units": units,
    }
    if properties_denominator is not None:
        result["properties_share"] = share(properties, properties_denominator)
        result["properties_share_pct"] = pct(properties, properties_denominator)
    if units_denominator is not None:
        result["units_share"] = share(units, units_denominator)
        result["units_share_pct"] = pct(units, units_denominator)
    return result


def category_totals(frame: pd.DataFrame) -> dict[str, object]:
    total_properties = len(frame)
    total_units = int(frame["units_final"].sum())
    rows: list[dict[str, object]] = []
    for category in CATEGORY_ORDER:
        mask = frame["kelsey_category"].eq(category)
        properties = int(mask.sum())
        units = int(frame.loc[mask, "units_final"].sum())
        rows.append(
            {
                "category": category,
                "label": CATEGORY_LABELS[category],
                "state_count": len(CATEGORY_STATES[category]),
                "states": CATEGORY_STATES[category],
                "properties": properties,
                "units": units,
                "share_of_all_properties": share(properties, total_properties),
                "share_of_all_properties_pct": pct(properties, total_properties),
                "share_of_all_units": share(units, total_units),
                "share_of_all_units_pct": pct(units, total_units),
            }
        )

    mapped_mask = frame["kelsey_category"].notna()
    mapped_properties = int(mapped_mask.sum())
    mapped_units = int(frame.loc[mapped_mask, "units_final"].sum())
    mapped_summary = summarize_mask(
        frame,
        mapped_mask,
        properties_denominator=total_properties,
        units_denominator=total_units,
    )
    mapped_summary["state_count"] = len(KELSEY_STATE_TO_CATEGORY)

    group_rows: list[dict[str, object]] = []
    group_rows_by_name: dict[str, dict[str, object]] = {}
    for group in CATEGORY_GROUPS:
        states = sorted(state for category in group["categories"] for state in CATEGORY_STATES[category])
        mask = frame["kelsey_category"].isin(group["categories"])
        summary = summarize_mask(
            frame,
            mask,
            properties_denominator=total_properties,
            units_denominator=total_units,
        )
        summary.update(
            {
                "group": group["group"],
                "label": group["label"],
                "categories": group["categories"],
                "state_count": len(states),
                "states": states,
                "share_of_all_properties": summary.get("properties_share"),
                "share_of_all_properties_pct": summary.get("properties_share_pct"),
                "share_of_all_units": summary.get("units_share"),
                "share_of_all_units_pct": summary.get("units_share_pct"),
                "share_of_mapped_properties": share(summary["properties"], mapped_properties),
                "share_of_mapped_properties_pct": pct(summary["properties"], mapped_properties),
                "share_of_mapped_units": share(summary["units"], mapped_units),
                "share_of_mapped_units_pct": pct(summary["units"], mapped_units),
            }
        )
        group_rows.append(summary)
        group_rows_by_name[group["group"]] = summary

    return {
        "rows": rows,
        "group_rows": group_rows,
        "group_rows_by_name": group_rows_by_name,
        "mapped_jurisdictions_only": mapped_summary,
        "construction_requirement_any_level": group_rows_by_name["construction_requirement_any_level"],
        "requires_or_exceeds_504_combined": group_rows_by_name["requires_or_exceeds_504"],
        "incentives_only": group_rows_by_name["incentives_only"],
        "no_requirements": group_rows_by_name["no_requirements"],
    }


def summarize_trgt_dis(frame: pd.DataFrame) -> dict[str, object]:
    counts = {
        "1_yes": int(frame["trgt_dis"].eq("1").sum()),
        "2_no": int(frame["trgt_dis"].eq("2").sum()),
        "0_not_indicated": int(frame["trgt_dis"].eq("0").sum()),
        "blank_or_missing": int(frame["trgt_dis"].eq("").sum()),
    }
    units = {
        "1_yes": int(frame.loc[frame["trgt_dis"].eq("1"), "units_final"].sum()),
        "2_no": int(frame.loc[frame["trgt_dis"].eq("2"), "units_final"].sum()),
        "0_not_indicated": int(frame.loc[frame["trgt_dis"].eq("0"), "units_final"].sum()),
        "blank_or_missing": int(frame.loc[frame["trgt_dis"].eq("").fillna(False), "units_final"].sum()),
    }

    yes_properties = counts["1_yes"]
    yes_units = units["1_yes"]
    yes_no_properties = counts["1_yes"] + counts["2_no"]
    nonblank_properties = yes_no_properties + counts["0_not_indicated"]

    return {
        "code_counts": counts,
        "units_by_code": units,
        "yes_properties": yes_properties,
        "yes_units": yes_units,
        "yes_share_of_all_properties": share(yes_properties, len(frame)),
        "yes_share_of_all_properties_pct": pct(yes_properties, len(frame)),
        "yes_share_of_all_units": share(yes_units, int(frame["units_final"].sum())),
        "yes_share_of_all_units_pct": pct(yes_units, int(frame["units_final"].sum())),
        "yes_share_of_yes_no_properties_only": share(yes_properties, yes_no_properties),
        "yes_share_of_yes_no_properties_only_pct": pct(yes_properties, yes_no_properties),
        "yes_share_of_nonblank_properties": share(yes_properties, nonblank_properties),
        "yes_share_of_nonblank_properties_pct": pct(yes_properties, nonblank_properties),
        "yes_no_properties": yes_no_properties,
        "nonblank_properties": nonblank_properties,
    }


def trgt_dis_by_decade(frame: pd.DataFrame, base_mask: pd.Series | None = None) -> dict[str, object]:
    if base_mask is None:
        base_mask = pd.Series(True, index=frame.index, dtype=bool)

    base_properties = int(base_mask.sum())
    base_units = int(frame.loc[base_mask, "units_final"].sum())
    rows: list[dict[str, object]] = []
    requested_mask = pd.Series(False, index=frame.index, dtype=bool)

    for label, start_year, end_year in DECADE_WINDOWS:
        decade_mask = base_mask & frame["yr_pis"].between(start_year, end_year, inclusive="both")
        requested_mask |= frame["yr_pis"].between(start_year, end_year, inclusive="both")

        decade_properties = int(decade_mask.sum())
        decade_units = int(frame.loc[decade_mask, "units_final"].sum())
        yes_mask = decade_mask & frame["trgt_dis"].eq("1")
        yes_properties = int(yes_mask.sum())
        yes_units = int(frame.loc[yes_mask, "units_final"].sum())
        yes_no_properties = int((decade_mask & frame["trgt_dis"].isin(["1", "2"])).sum())
        nonblank_properties = int((decade_mask & frame["trgt_dis"].isin(["0", "1", "2"])).sum())

        rows.append(
            {
                "decade": label,
                "start_year": start_year,
                "end_year": end_year,
                "properties": decade_properties,
                "units": decade_units,
                "share_of_base_properties": share(decade_properties, base_properties),
                "share_of_base_properties_pct": pct(decade_properties, base_properties),
                "share_of_base_units": share(decade_units, base_units),
                "share_of_base_units_pct": pct(decade_units, base_units),
                "trgt_dis_yes_properties": yes_properties,
                "trgt_dis_yes_units": yes_units,
                "trgt_dis_yes_share_of_decade_properties": share(yes_properties, decade_properties),
                "trgt_dis_yes_share_of_decade_properties_pct": pct(yes_properties, decade_properties),
                "trgt_dis_yes_share_of_decade_units": share(yes_units, decade_units),
                "trgt_dis_yes_share_of_decade_units_pct": pct(yes_units, decade_units),
                "trgt_dis_yes_share_of_yes_no_properties": share(yes_properties, yes_no_properties),
                "trgt_dis_yes_share_of_yes_no_properties_pct": pct(yes_properties, yes_no_properties),
                "trgt_dis_yes_share_of_nonblank_properties": share(yes_properties, nonblank_properties),
                "trgt_dis_yes_share_of_nonblank_properties_pct": pct(yes_properties, nonblank_properties),
                "yes_no_properties": yes_no_properties,
                "nonblank_properties": nonblank_properties,
            }
        )

    outside_mask = base_mask & ~requested_mask
    outside_yes_mask = outside_mask & frame["trgt_dis"].eq("1")

    return {
        "base_properties": base_properties,
        "base_units": base_units,
        "requested_windows": rows,
        "outside_requested_windows": {
            "properties": int(outside_mask.sum()),
            "units": int(frame.loc[outside_mask, "units_final"].sum()),
            "trgt_dis_yes_properties": int(outside_yes_mask.sum()),
            "trgt_dis_yes_units": int(frame.loc[outside_yes_mask, "units_final"].sum()),
        },
        "note": "Requested decade windows follow the original research prompt: 1987-1996, 1997-2006, 2007-2016, and 2017-2023. Properties outside those windows are reported separately.",
    }


def overlap_masks(frame: pd.DataFrame) -> dict[str, pd.Series]:
    post_2003 = frame["yr_pis"].between(2003, 2023, inclusive="both")

    strict = pd.Series(False, index=frame.index, dtype=bool)
    for column in STRICT_OVERLAP_FIELDS:
        strict |= frame[column].eq("1")
    strict |= frame["rentassist"].isin(["1", "3"])

    broad = strict | frame["fha"].eq("1") | frame["fmha_538"].eq("1") | frame["rentassist"].eq("5")

    return {
        "post_2003": post_2003,
        "strict": strict,
        "broad": broad,
    }


def overlap_component_rows(frame: pd.DataFrame, base_mask: pd.Series) -> list[dict[str, object]]:
    base_properties = int(base_mask.sum())
    base_units = int(frame.loc[base_mask, "units_final"].sum())
    rows: list[dict[str, object]] = []

    for column in STRICT_OVERLAP_FIELDS + ["fha", "fmha_538"]:
        mask = base_mask & frame[column].eq("1")
        properties = int(mask.sum())
        units = int(frame.loc[mask, "units_final"].sum())
        rows.append(
            {
                "component": column,
                "label": STRICT_OVERLAP_LABELS[column],
                "properties": properties,
                "units": units,
                "share_of_base_properties": share(properties, base_properties),
                "share_of_base_properties_pct": pct(properties, base_properties),
                "share_of_base_units": share(units, base_units),
                "share_of_base_units_pct": pct(units, base_units),
            }
        )

    for code, label in RENTASSIST_LABELS.items():
        mask = base_mask & frame["rentassist"].eq(code)
        properties = int(mask.sum())
        units = int(frame.loc[mask, "units_final"].sum())
        rows.append(
            {
                "component": f"rentassist_{code}",
                "label": f"RENTASST={code} ({label})",
                "properties": properties,
                "units": units,
                "share_of_base_properties": share(properties, base_properties),
                "share_of_base_properties_pct": pct(properties, base_properties),
                "share_of_base_units": share(units, base_units),
                "share_of_base_units_pct": pct(units, base_units),
            }
        )

    return rows


def state_level_qap_crosswalk(frame: pd.DataFrame, post_2003: pd.Series, strict: pd.Series, broad: pd.Series) -> dict[str, object]:
    total_properties = len(frame)
    total_units = int(frame["units_final"].sum())
    rows: list[dict[str, object]] = []

    for state in sorted(KELSEY_STATE_TO_CATEGORY):
        category = KELSEY_STATE_TO_CATEGORY[state]
        state_mask = frame["proj_st"].eq(state)
        post_mask = state_mask & post_2003
        trgt_yes_mask = state_mask & frame["trgt_dis"].eq("1")
        row = {
            "state": state,
            "qap_accessibility_category": category,
            "qap_accessibility_label": CATEGORY_LABELS[category],
            "has_qap_accessibility_construction_requirement": category in {"more_than_504", "requires_504", "less_than_504"},
            "is_incentives_only_state": category == "incentives",
            "is_no_requirement_state": category == "no_requirements",
            "properties": int(state_mask.sum()),
            "units": int(frame.loc[state_mask, "units_final"].sum()),
            "share_of_all_properties": share(int(state_mask.sum()), total_properties),
            "share_of_all_properties_pct": pct(int(state_mask.sum()), total_properties),
            "share_of_all_units": share(int(frame.loc[state_mask, "units_final"].sum()), total_units),
            "share_of_all_units_pct": pct(int(frame.loc[state_mask, "units_final"].sum()), total_units),
            "trgt_dis_yes_properties": int(trgt_yes_mask.sum()),
            "trgt_dis_yes_units": int(frame.loc[trgt_yes_mask, "units_final"].sum()),
            "trgt_dis_yes_share_of_state_properties": share(int(trgt_yes_mask.sum()), int(state_mask.sum())),
            "trgt_dis_yes_share_of_state_properties_pct": pct(int(trgt_yes_mask.sum()), int(state_mask.sum())),
            "trgt_dis_yes_share_of_state_units": share(int(frame.loc[trgt_yes_mask, "units_final"].sum()), int(frame.loc[state_mask, "units_final"].sum())),
            "trgt_dis_yes_share_of_state_units_pct": pct(int(frame.loc[trgt_yes_mask, "units_final"].sum()), int(frame.loc[state_mask, "units_final"].sum())),
            "post_2003_properties": int(post_mask.sum()),
            "post_2003_units": int(frame.loc[post_mask, "units_final"].sum()),
            "post_2003_no_strict_overlap_properties": int((post_mask & ~strict).sum()),
            "post_2003_no_strict_overlap_units": int(frame.loc[post_mask & ~strict, "units_final"].sum()),
            "post_2003_no_broad_overlap_properties": int((post_mask & ~broad).sum()),
            "post_2003_no_broad_overlap_units": int(frame.loc[post_mask & ~broad, "units_final"].sum()),
        }
        rows.append(row)

    alphabetical_rows = sorted(rows, key=lambda row: row["state"])
    by_units_desc = sorted(rows, key=lambda row: (row["units"], row["properties"], row["state"]), reverse=True)
    by_category_then_units = sorted(
        rows,
        key=lambda row: (CATEGORY_ORDER.index(row["qap_accessibility_category"]), -row["units"], row["state"]),
    )

    return {
        "state_count": len(alphabetical_rows),
        "alphabetical_rows": alphabetical_rows,
        "by_units_desc": by_units_desc,
        "by_category_then_units": by_category_then_units,
        "top_15_by_units": by_units_desc[:15],
    }


def no_requirement_state_rows(crosswalk: dict[str, object]) -> list[dict[str, object]]:
    return [
        row
        for row in crosswalk["by_units_desc"]
        if row["qap_accessibility_category"] == "no_requirements"
    ]


def unmapped_jurisdictions(frame: pd.DataFrame) -> dict[str, object]:
    unmapped_mask = frame["kelsey_category"].isna()
    grouped = (
        frame.loc[unmapped_mask]
        .groupby("proj_st", dropna=False)
        .agg(properties=("hud_id", "size"), units=("units_final", "sum"))
        .reset_index()
        .sort_values(["units", "properties"], ascending=[False, False])
    )

    rows = [
        {
            "jurisdiction": str(record["proj_st"]),
            "properties": int(record["properties"]),
            "units": int(record["units"]),
        }
        for record in grouped.to_dict(orient="records")
    ]

    summary = summarize_mask(
        frame,
        unmapped_mask,
        properties_denominator=len(frame),
        units_denominator=int(frame["units_final"].sum()),
    )
    summary["rows"] = rows
    return summary


def accessibility_field_audit() -> dict[str, object]:
    columns = file_header_columns(INPUT_CSV)
    dictionary_lines = read_text_lines(INPUT_DICTIONARY)

    return {
        "csv_header_accessibility_keyword_hits": [column for column in columns if INVENTORY_KEYWORD_PATTERN.search(column)],
        "csv_header_target_population_columns": [column for column in columns if column.startswith("trgt_")],
        "dictionary_accessibility_keyword_hits": line_matches(dictionary_lines, INVENTORY_KEYWORD_PATTERN),
        "dictionary_trgt_dis_hits": line_matches(dictionary_lines, TRGT_DIS_PATTERN),
        "dictionary_trgt_dis_excerpt": trgt_dis_excerpt(dictionary_lines),
        "conclusion": "No public LIHTC header field was found for accessible-unit counts or inventories. The nearest disability-related field is TRGT_DIS, which HUD defines as a target-population flag rather than an accessible-unit inventory.",
    }


def build_results(frame: pd.DataFrame) -> dict[str, object]:
    total_properties = len(frame)
    total_units = int(frame["units_final"].sum())
    trgt_summary = summarize_trgt_dis(frame)
    trgt_decades = trgt_dis_by_decade(frame)
    category_summary = category_totals(frame)
    masks = overlap_masks(frame)
    post_2003 = masks["post_2003"]
    strict = masks["strict"]
    broad = masks["broad"]
    zero_mask = frame["kelsey_category"].eq("no_requirements")
    zero_post_2003 = zero_mask & post_2003

    zero_overall = summarize_mask(
        frame,
        zero_mask,
        properties_denominator=total_properties,
        units_denominator=total_units,
    )
    zero_post_summary = summarize_mask(
        frame,
        zero_post_2003,
        properties_denominator=int(post_2003.sum()),
        units_denominator=int(frame.loc[post_2003, "units_final"].sum()),
    )
    zero_post_no_strict = summarize_mask(
        frame,
        zero_post_2003 & ~strict,
        properties_denominator=int(zero_post_2003.sum()),
        units_denominator=int(frame.loc[zero_post_2003, "units_final"].sum()),
    )
    zero_post_no_broad = summarize_mask(
        frame,
        zero_post_2003 & ~broad,
        properties_denominator=int(zero_post_2003.sum()),
        units_denominator=int(frame.loc[zero_post_2003, "units_final"].sum()),
    )
    zero_post_with_strict = summarize_mask(
        frame,
        zero_post_2003 & strict,
        properties_denominator=int(zero_post_2003.sum()),
        units_denominator=int(frame.loc[zero_post_2003, "units_final"].sum()),
    )
    zero_post_with_broad = summarize_mask(
        frame,
        zero_post_2003 & broad,
        properties_denominator=int(zero_post_2003.sum()),
        units_denominator=int(frame.loc[zero_post_2003, "units_final"].sum()),
    )

    post_2003_summary = summarize_mask(
        frame,
        post_2003,
        properties_denominator=total_properties,
        units_denominator=total_units,
    )
    post_2003_no_strict = summarize_mask(
        frame,
        post_2003 & ~strict,
        properties_denominator=int(post_2003.sum()),
        units_denominator=int(frame.loc[post_2003, "units_final"].sum()),
    )
    post_2003_with_strict = summarize_mask(
        frame,
        post_2003 & strict,
        properties_denominator=int(post_2003.sum()),
        units_denominator=int(frame.loc[post_2003, "units_final"].sum()),
    )
    post_2003_no_broad = summarize_mask(
        frame,
        post_2003 & ~broad,
        properties_denominator=int(post_2003.sum()),
        units_denominator=int(frame.loc[post_2003, "units_final"].sum()),
    )
    post_2003_with_broad = summarize_mask(
        frame,
        post_2003 & broad,
        properties_denominator=int(post_2003.sum()),
        units_denominator=int(frame.loc[post_2003, "units_final"].sum()),
    )

    zero_targeted = summarize_mask(
        frame,
        zero_mask & frame["trgt_dis"].eq("1"),
        properties_denominator=int(zero_mask.sum()),
        units_denominator=int(frame.loc[zero_mask, "units_final"].sum()),
    )
    zero_post_targeted = summarize_mask(
        frame,
        zero_post_2003 & frame["trgt_dis"].eq("1"),
        properties_denominator=int(zero_post_2003.sum()),
        units_denominator=int(frame.loc[zero_post_2003, "units_final"].sum()),
    )

    crosswalk = state_level_qap_crosswalk(frame, post_2003, strict, broad)
    no_requirement_rows = no_requirement_state_rows(crosswalk)
    zero_decades = trgt_dis_by_decade(frame, base_mask=zero_mask)

    strict_black_hole_state_count = sum(1 for row in no_requirement_rows if row["post_2003_no_strict_overlap_units"] > 0)
    broad_black_hole_state_count = sum(1 for row in no_requirement_rows if row["post_2003_no_broad_overlap_units"] > 0)

    headline_title = (
        f"{zero_post_no_strict['properties']:,} LIHTC properties containing "
        f"{zero_post_no_strict['units']:,} units across {strict_black_hole_state_count:,} states lack public accessible-unit inventory, are in states with no observed QAP accessibility requirement, and show no observed strict federal-overlap proxy"
    )

    results = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_dir": str(REPO_DIR),
        "inputs": {
            "lihtc_csv": str(INPUT_CSV),
            "lihtc_dictionary": str(INPUT_DICTIONARY),
            "kelsey_factsheet_text": str(KELSEY_FACTSHEET),
            "kelsey_factsheet_layout": str(KELSEY_LAYOUT),
            "kelsey_504_comments_text": str(KELSEY_COMMENTS),
        },
        "files_created_or_modified": FILES_CREATED_OR_MODIFIED,
        "headline_title": headline_title,
        "headline_findings": [
            (
                f"Accessibility-data black-hole floor: {zero_post_no_strict['properties']:,} properties and {zero_post_no_strict['units']:,} units "
                f"across {strict_black_hole_state_count} states with no observed QAP accessibility requirement show no observed strict federal-overlap proxy in the 2003-2023 window; "
                f"the broader overlap screen still leaves {zero_post_no_broad['properties']:,} properties and {zero_post_no_broad['units']:,} units "
                f"across {broad_black_hole_state_count} states."
            ),
            (
                f"HUD's public LIHTC file covers {total_properties:,} properties and {total_units:,} units but exposes no public accessible-unit inventory field."
            ),
            (
                f"TRGT_DIS is a target-population flag, not an accessible-unit count; TRGT_DIS=1 appears on {trgt_summary['yes_properties']:,} properties and {trgt_summary['yes_units']:,} units, rising from "
                f"{trgt_decades['requested_windows'][0]['trgt_dis_yes_share_of_decade_properties_pct']:.2f}% of 1987-1996 properties to {trgt_decades['requested_windows'][-1]['trgt_dis_yes_share_of_decade_properties_pct']:.2f}% in 2017-2023."
            ),
            (
                f"The reconstructed Kelsey taxonomy sorts the 50 states into 22 with accessibility construction requirements, 9 with incentives only, and 19 with no observed QAP accessibility requirement; only 2 states exceed Section 504."
            ),
        ],
        "dataset": {
            "properties": total_properties,
            "units": total_units,
            "jurisdiction_count_in_hud_file": int(frame["proj_st"].nunique(dropna=True)),
            "jurisdictions_in_hud_file": sorted(frame["proj_st"].dropna().unique().tolist()),
            "unit_measure_note": "Units are counted as N_UNITS when positive, otherwise N_UNITSR, matching the completed probe scripts.",
        },
        "accessibility_field_audit": accessibility_field_audit(),
        "trgt_dis_summary": trgt_summary,
        "trgt_dis_by_decade": trgt_decades,
        "kelsey_taxonomy": {
            "source_summary": "The Kelsey 2023 LIHTC accessibility factsheet splits the 50 states into 2 that require more than Section 504, 13 that require Section 504, 7 with requirements less than Section 504, 9 with incentives only, and 19 with no observed QAP accessibility requirement. This audit maps those reconstructed current/2023 state categories onto HUD's public LIHTC stock; it does not reconstruct each project's historical QAP status at the time of placement in service. The companion 2023 Section 504 ANPRM comments say 15 states require LIHTC-financed homes to be 504 compliant through QAP requirements or legislative changes.",
            "category_labels": CATEGORY_LABELS,
            "states_by_category": CATEGORY_STATES,
            "category_state_counts": {category: len(states) for category, states in CATEGORY_STATES.items()},
            "category_totals": category_summary,
        },
        "state_level_qap_crosswalk": {
            "source_summary": "Full 50-state crosswalk matching HUD LIHTC counts to the reconstructed current/2023 Kelsey QAP accessibility categories mapped onto the HUD stock. Rows include state totals, units, TRGT_DIS shares, and 2003+ overlap-proxy counts; the markdown memo presents a reduced quick-review version rather than every JSON field.",
            **crosswalk,
        },
        "field_first_requested_notes": FIELD_FIRST_REQUESTED,
        "federal_overlap_proxy_definitions": {
            "strict": {
                "description": "Observed explicit non-LIHTC overlap markers in the HUD LIHTC file. This is a proxy for layered federal participation, not a legal Section 504 determination.",
                "yes_no_fields": STRICT_OVERLAP_FIELDS,
                "rentassist_positive_codes": [
                    {"code": "1", "label": RENTASSIST_LABELS["1"]},
                    {"code": "3", "label": RENTASSIST_LABELS["3"]},
                ],
                "note": "The strict proxy excludes FHA, FMHA_538, and RENTASST=5 because those entries suggest a federal nexus or ambiguity but do not by themselves definitively establish the kind of direct federal financial assistance relevant to a building-level Section 504 analysis.",
            },
            "broad": {
                "description": "Strict proxy plus ambiguous or insurance/guarantee-style indicators that may signal a federal nexus.",
                "includes_strict_proxy": True,
                "additional_fields": ["fha", "fmha_538"],
                "additional_rentassist_codes": [
                    {"code": "5", "label": RENTASSIST_LABELS["5"]},
                ],
                "note": "Broad overlap remains an observed proxy only. It should not be cited as a definitive Section 504 applicability measure.",
            },
        },
        "post_2003_overlap_overall": {
            "window": "YR_PIS between 2003 and 2023 inclusive",
            "all_post_2003": post_2003_summary,
            "with_strict_overlap_proxy": post_2003_with_strict,
            "no_strict_overlap_proxy": post_2003_no_strict,
            "with_broad_overlap_proxy": post_2003_with_broad,
            "no_broad_overlap_proxy": post_2003_no_broad,
            "component_rows": overlap_component_rows(frame, post_2003),
        },
        "perimeter_gap": {
            "definition": "Conservative proxy for the note's excluded standalone-LIHTC perimeter: properties in Kelsey's 19-state no-observed-QAP-accessibility-requirement category, placed in service 2003-2023, with no public accessible-unit inventory and no observed federal-overlap marker in the HUD LIHTC file. These are observed-proxy counts, not definitive Section 504 holdings.",
            "headline_title": headline_title,
            "strict_proxy_floor_2003_2023": zero_post_no_strict,
            "broad_proxy_floor_2003_2023": zero_post_no_broad,
            "strict_proxy_state_count": strict_black_hole_state_count,
            "broad_proxy_state_count": broad_black_hole_state_count,
            "state_rows": no_requirement_rows,
            "top_10_states_by_units": no_requirement_rows[:10],
        },
        "no_requirement_states": {
            "overall": zero_overall,
            "overall_trgt_dis_yes": zero_targeted,
            "trgt_dis_by_decade": zero_decades,
            "post_2003": zero_post_summary,
            "post_2003_trgt_dis_yes": zero_post_targeted,
            "post_2003_with_strict_overlap_proxy": zero_post_with_strict,
            "post_2003_no_strict_overlap_proxy": zero_post_no_strict,
            "post_2003_with_broad_overlap_proxy": zero_post_with_broad,
            "post_2003_no_broad_overlap_proxy": zero_post_no_broad,
            "state_rows": no_requirement_rows,
            "top_10_states_by_units": no_requirement_rows[:10],
            "post_2003_component_rows": overlap_component_rows(frame, zero_post_2003),
        },
        "unmapped_jurisdictions": unmapped_jurisdictions(frame),
        "limitations": [
            "HUD's public LIHTC file does not publish an accessible-unit inventory, mobility-unit count, sensory-unit count, or direct Section 504 applicability flag.",
            "TRGT_DIS indicates that a property targets disabled households; it is not a count of accessible units and should not be interpreted as one.",
            "The Kelsey taxonomy is a reconstructed current/2023 50-state category map applied to HUD's public LIHTC stock; it is not a project-year historical determination of what each state's QAP required when a property was placed in service. HUD LIHTC records in DC and territories remain outside that state-only taxonomy.",
            "Observed strict and broad overlap measures are proxies derived from publicly visible co-funding, rental-assistance, insurance, or guarantee fields. They are not definitive legal conclusions about Section 504 recipient status.",
            "The proxy window begins in 2003 because several relevant fields first appear with 2003 properties, but some overlap fields were introduced later (RENTASST in 2006; TCAP/TCEP in 2012; HTF/RAD in 2018), so 'no observed overlap' should be read conservatively.",
            "The note's proposed reporting regime can directly reach HUD-funded or HUD-inspected programs; this audit uses LIHTC overlap proxies to quantify the excluded standalone-LIHTC perimeter, not to collapse it into a definitive Section 504-covered population.",
        ],
    }
    return results


def build_markdown(results: dict[str, object]) -> str:
    dataset = results["dataset"]
    trgt = results["trgt_dis_summary"]
    trgt_decades = results["trgt_dis_by_decade"]
    taxonomy = results["kelsey_taxonomy"]
    state_crosswalk = results["state_level_qap_crosswalk"]
    perimeter = results["perimeter_gap"]
    no_req = results["no_requirement_states"]
    unmapped = results["unmapped_jurisdictions"]

    group_rows = [
        taxonomy["category_totals"]["construction_requirement_any_level"],
        taxonomy["category_totals"]["requires_or_exceeds_504_combined"],
        taxonomy["category_totals"]["incentives_only"],
        taxonomy["category_totals"]["no_requirements"],
    ]
    category_rows = taxonomy["category_totals"]["rows"]

    category_group_table = markdown_table(
        ["Group", "States", "Properties", "Units", "Share of all units"],
        [
            [
                row["label"],
                fmt_int(row["state_count"]),
                fmt_int(row["properties"]),
                fmt_int(row["units"]),
                fmt_pct(row["share_of_all_units_pct"]),
            ]
            for row in group_rows
        ],
    )

    category_table = markdown_table(
        ["Detailed category", "States", "Properties", "Units", "Share of all units"],
        [
            [
                row["label"],
                fmt_int(row["state_count"]),
                fmt_int(row["properties"]),
                fmt_int(row["units"]),
                fmt_pct(row["share_of_all_units_pct"]),
            ]
            for row in category_rows
        ],
    )

    decade_table = markdown_table(
        ["Decade", "Properties", "Units", "TRGT_DIS=1 properties", "TRGT_DIS share of properties", "TRGT_DIS share of units"],
        [
            [
                row["decade"],
                fmt_int(row["properties"]),
                fmt_int(row["units"]),
                fmt_int(row["trgt_dis_yes_properties"]),
                fmt_pct(row["trgt_dis_yes_share_of_decade_properties_pct"]),
                fmt_pct(row["trgt_dis_yes_share_of_decade_units_pct"]),
            ]
            for row in trgt_decades["requested_windows"]
        ],
    )

    state_crosswalk_table = markdown_table(
        ["State", "QAP category", "Properties", "Units", "TRGT_DIS=1 properties", "TRGT_DIS share of state properties"],
        [
            [
                row["state"],
                row["qap_accessibility_label"],
                fmt_int(row["properties"]),
                fmt_int(row["units"]),
                fmt_int(row["trgt_dis_yes_properties"]),
                fmt_pct(row["trgt_dis_yes_share_of_state_properties_pct"]),
            ]
            for row in state_crosswalk["by_category_then_units"]
        ],
    )

    top_zero_table = markdown_table(
        ["State", "Properties", "Units", "2003+ units", "2003+ no strict proxy units", "2003+ no broad proxy units"],
        [
            [
                row["state"],
                fmt_int(row["properties"]),
                fmt_int(row["units"]),
                fmt_int(row["post_2003_units"]),
                fmt_int(row["post_2003_no_strict_overlap_units"]),
                fmt_int(row["post_2003_no_broad_overlap_units"]),
            ]
            for row in no_req["top_10_states_by_units"]
        ],
    )

    unmapped_table = markdown_table(
        ["Jurisdiction", "Properties", "Units"],
        [
            [row["jurisdiction"], fmt_int(row["properties"]), fmt_int(row["units"])]
            for row in unmapped["rows"]
        ],
    )

    lines = [
        f"# {results['headline_title']}",
        "",
        "## LIHTC Accessibility Audit Memo",
        "",
        f"Generated: {results['generated_at_utc']}",
        f"Repo: `{results['repo_dir']}`",
        "",
        "## Bottom line",
        "",
        (
            f"This memo quantifies the LIHTC accessibility-data black hole. HUD's public LIHTC file covers {fmt_int(dataset['properties'])} properties and {fmt_int(dataset['units'])} units, but the public header exposes no accessible-unit inventory field. "
            f"The nearest disability-related field is `TRGT_DIS`, which HUD's dictionary defines as `Targets a specific population – disabled` rather than an accessible-unit count."
        ),
        "",
        (
            f"The conservative perimeter-gap floor is {fmt_int(perimeter['strict_proxy_floor_2003_2023']['properties'])} properties and {fmt_int(perimeter['strict_proxy_floor_2003_2023']['units'])} units across {fmt_int(perimeter['strict_proxy_state_count'])} states: "
            f"projects in the 19 states with no observed QAP accessibility requirement, placed in service 2003-2023, with no observed strict federal-overlap proxy in HUD's public LIHTC file. "
            f"Under the broader overlap screen, {fmt_int(perimeter['broad_proxy_floor_2003_2023']['properties'])} properties and {fmt_int(perimeter['broad_proxy_floor_2003_2023']['units'])} units across {fmt_int(perimeter['broad_proxy_state_count'])} states remain."
        ),
        "",
        (
            f"That is the note's standalone-LIHTC perimeter problem in numeric form: no public federal accessible-unit inventory, no observed state QAP accessibility requirement in 19 states, and a large 2003+ subset with no observed federal-overlap marker. "
            f"These counts are observed-proxy bounds, not definitive Section 504 noncoverage holdings."
        ),
        "",
        "## Sources and scope",
        "",
        f"- HUD LIHTC public file: `{results['inputs']['lihtc_csv']}`",
        f"- HUD LIHTC dictionary: `{results['inputs']['lihtc_dictionary']}`",
        f"- The Kelsey 2023 factsheet text: `{results['inputs']['kelsey_factsheet_text']}`",
        f"- The Kelsey 2023 Section 504 comments text: `{results['inputs']['kelsey_504_comments_text']}`",
        "- Units are counted as `N_UNITS` when positive, otherwise `N_UNITSR`, matching the completed probe scripts used in the prior research pass.",
        "- The Kelsey taxonomy is a 50-state map. DC and territories remain outside that taxonomy and are reported separately below.",
        "- The state/QAP categories here are reconstructed current/2023 Kelsey categories mapped onto HUD's public LIHTC stock, not project-year historical determinations of what a state's QAP required when a given property was placed in service.",
        "",
        "## Key findings",
        "",
        f"1. No public accessible-unit inventory field was observed in the HUD LIHTC file. The file contains target-population flags (`TRGT_*`) but not a public count of mobility-accessible or sensory-accessible units.",
        f"2. `TRGT_DIS=1` appears on {fmt_int(trgt['yes_properties'])} properties / {fmt_int(trgt['yes_units'])} units overall. It is a targeting flag, not an accessibility inventory.",
        f"3. The requested decade analysis shows `TRGT_DIS=1` rising from {fmt_pct(trgt_decades['requested_windows'][0]['trgt_dis_yes_share_of_decade_properties_pct'])} of 1987-1996 properties to {fmt_pct(trgt_decades['requested_windows'][-1]['trgt_dis_yes_share_of_decade_properties_pct'])} in 2017-2023.",
        f"4. The Kelsey reconstruction sorts the 50 states into 22 with accessibility construction requirements, 9 with incentives only, and 19 with no observed QAP accessibility requirement. Only 2 states exceed Section 504.",
        f"5. The 19 states with no observed QAP accessibility requirement account for {fmt_int(no_req['overall']['properties'])} properties / {fmt_int(no_req['overall']['units'])} units overall and {fmt_int(no_req['post_2003']['properties'])} properties / {fmt_int(no_req['post_2003']['units'])} units in the 2003+ overlap-proxy window.",
        f"6. Within that 2003+ subset in states with no observed QAP accessibility requirement, {fmt_int(no_req['post_2003_no_strict_overlap_proxy']['properties'])} properties / {fmt_int(no_req['post_2003_no_strict_overlap_proxy']['units'])} units show no observed strict federal-overlap proxy, and {fmt_int(no_req['post_2003_no_broad_overlap_proxy']['properties'])} properties / {fmt_int(no_req['post_2003_no_broad_overlap_proxy']['units'])} units show no observed broad proxy.",
        "",
        "## The accessibility-data black hole and the perimeter",
        "",
        "The LIHTC black hole is three-sided:",
        "- the federal LIHTC public file has no accessible-unit inventory field,",
        f"- 19 states in the Kelsey 2023 taxonomy have no observed QAP accessibility requirement, and",
        f"- even after limiting to 2003-2023 properties and screening for observed federal overlap, {fmt_int(perimeter['strict_proxy_floor_2003_2023']['units'])} units remain in the conservative strict proxy floor.",
        "",
        (
            f"This framing is stronger than simply saying LIHTC lacks a field. It identifies the perimeter gap the note leaves outside its defended HUD-reporting regime: apparently standalone LIHTC in states with no observed QAP accessibility requirement where the public file also shows no observed federal-overlap marker. "
            f"The broad screen narrows that subset only modestly, from {fmt_int(perimeter['strict_proxy_floor_2003_2023']['units'])} to {fmt_int(perimeter['broad_proxy_floor_2003_2023']['units'])} units."
        ),
        "",
        "## What the HUD file can and cannot say",
        "",
        "The HUD file can say:",
        "- how many LIHTC properties/units exist in the public extract,",
        "- whether a project was flagged as targeting disabled households (`TRGT_DIS=1`), and",
        "- whether the public file records selected co-funding, rent-assistance, insurance, or guarantee markers.",
        "",
        "The HUD file cannot say:",
        "- how many accessible units a project contains,",
        "- how many units are mobility-accessible or sensory-accessible, or",
        "- whether Section 504 definitively applies to a given project as a matter of law.",
        "",
        "## TRGT_DIS by requested decades",
        "",
        decade_table,
        "",
        (
            f"The decade trend matters because it shows why `TRGT_DIS` cannot substitute for an accessibility inventory. The targeting flag's prevalence changes substantially over time: {fmt_pct(trgt_decades['requested_windows'][0]['trgt_dis_yes_share_of_decade_properties_pct'])} in 1987-1996, {fmt_pct(trgt_decades['requested_windows'][1]['trgt_dis_yes_share_of_decade_properties_pct'])} in 1997-2006, {fmt_pct(trgt_decades['requested_windows'][2]['trgt_dis_yes_share_of_decade_properties_pct'])} in 2007-2016, and {fmt_pct(trgt_decades['requested_windows'][3]['trgt_dis_yes_share_of_decade_properties_pct'])} in 2017-2023."
        ),
        "",
        (
            f"Within the 19 states with no observed QAP accessibility requirement, the same pattern rises from {fmt_pct(no_req['trgt_dis_by_decade']['requested_windows'][0]['trgt_dis_yes_share_of_decade_properties_pct'])} to {fmt_pct(no_req['trgt_dis_by_decade']['requested_windows'][-1]['trgt_dis_yes_share_of_decade_properties_pct'])}. "
            f"Outside the requested windows, {fmt_int(trgt_decades['outside_requested_windows']['properties'])} properties / {fmt_int(trgt_decades['outside_requested_windows']['units'])} units remain and are reported separately in the JSON."
        ),
        "",
        "## Kelsey/QAP accessibility categories and totals",
        "",
        category_group_table,
        "",
        category_table,
        "",
        (
            f"The key Kelsey crosswalk takeaway is structural: 22 states impose some accessibility construction requirement through their QAPs, 9 rely on incentives only, and 19 have no observed QAP accessibility requirement. "
            f"Those state labels are reconstructed current/2023 categories mapped onto the HUD stock, not year-specific historical QAP determinations at placement in service. "
            f"The stricter 15-state require-or-exceed-504 subset still covers {fmt_int(taxonomy['category_totals']['requires_or_exceeds_504_combined']['properties'])} properties / {fmt_int(taxonomy['category_totals']['requires_or_exceeds_504_combined']['units'])} units."
        ),
        "",
        "## Full 50-state QAP crosswalk",
        "",
        "The JSON output contains the fuller state-level crosswalk with counts, units, `TRGT_DIS` shares, overlap-proxy counts, and additional state fields. The markdown table below is a reduced quick-review table with a subset of those columns.",
        "",
        state_crosswalk_table,
        "",
        "## States with no observed QAP accessibility requirement and the perimeter-gap floor",
        "",
        f"- Overall states with no observed QAP accessibility requirement: {fmt_int(no_req['overall']['properties'])} properties / {fmt_int(no_req['overall']['units'])} units ({fmt_pct(no_req['overall']['units_share_pct'])} of all LIHTC units).",
        f"- `TRGT_DIS=1` within those states: {fmt_int(no_req['overall_trgt_dis_yes']['properties'])} properties / {fmt_int(no_req['overall_trgt_dis_yes']['units'])} units.",
        f"- 2003+ subset: {fmt_int(no_req['post_2003']['properties'])} properties / {fmt_int(no_req['post_2003']['units'])} units.",
        f"- 2003+ with no observed strict overlap proxy: {fmt_int(no_req['post_2003_no_strict_overlap_proxy']['properties'])} properties / {fmt_int(no_req['post_2003_no_strict_overlap_proxy']['units'])} units ({fmt_pct(no_req['post_2003_no_strict_overlap_proxy']['units_share_pct'])} of 2003+ units in states with no observed QAP accessibility requirement).",
        f"- 2003+ with no observed broad overlap proxy: {fmt_int(no_req['post_2003_no_broad_overlap_proxy']['properties'])} properties / {fmt_int(no_req['post_2003_no_broad_overlap_proxy']['units'])} units ({fmt_pct(no_req['post_2003_no_broad_overlap_proxy']['units_share_pct'])} of 2003+ units in states with no observed QAP accessibility requirement).",
        "",
        "Top states with no observed QAP accessibility requirement by units:",
        "",
        top_zero_table,
        "",
        "## How the overlap proxies were defined",
        "",
        "Strict overlap proxy:",
        "- positive `HOME`, `CDBG`, `HTF`, `MFF_RA`, `FMHA_514`, `FMHA_515`, `HOPEVI`, `TCAP`, `TCEP`, or `RAD`; or",
        "- `RENTASST=1` (Federal) or `RENTASST=3` (Both Federal and State).",
        "",
        "Broad overlap proxy:",
        "- everything in the strict proxy, plus",
        "- `FHA=1`, `FMHA_538=1`, or `RENTASST=5` (Unknown whether Federal or State).",
        "",
        "Interpretive caution:",
        "- A positive proxy is evidence of an observed federal nexus in the public LIHTC file, not a final legal Section 504 holding.",
        "- A negative proxy means only that the public file shows no observed marker under these rules. It does not prove lack of federal financial assistance or lack of Section 504 coverage.",
        "",
        "## Why the overlap analysis starts in 2003",
        "",
        "HUD's dictionary says several relevant fields first appear with 2003 properties, including `HOME`, `CDBG`, `FHA`, `HOPEVI`, and `TRGT_DIS`. But some fields were added later: `RENTASST` in 2006, `TCAP/TCEP` in 2012, and `HTF/RAD` in 2018. Accordingly, even the 2003+ proxy window still under-observes some later-added forms of overlap, especially in the early years of that window.",
        "",
        "## Why standalone LIHTC stays outside the proposed HUD reporting regime",
        "",
        (
            f"The note's defended reporting perimeter is HUD-funded or HUD-inspected housing where HUD can amend existing forms and collect accessibility counts through channels it already controls. Standalone LIHTC is different. The public LIHTC file is observational, not a live HUD reporting hook; it provides no accessible-unit inventory; and the available overlap fields only proxy federal participation rather than conclusively resolving project-level Section 504 status."
        ),
        "",
        (
            f"That is why this audit quantifies standalone LIHTC as a perimeter problem rather than treating it as automatically inside the proposed regime. The strict proxy floor of {fmt_int(perimeter['strict_proxy_floor_2003_2023']['units'])} units shows the size of the excluded black hole, while the proposal itself remains limited to programs HUD already funds, inspects, or directly administers. In short: the memo uses LIHTC to show what HUD still cannot see, not to claim that every LIHTC property is already within HUD's defended reporting authority."
        ),
        "",
        "## Unmapped jurisdictions outside the 50-state taxonomy",
        "",
        f"{fmt_int(unmapped['properties'])} properties / {fmt_int(unmapped['units'])} units are in jurisdictions not covered by the 50-state Kelsey taxonomy.",
        "",
        unmapped_table,
        "",
        "## Bottom-line limitations for citation",
        "",
        "- Do not cite this audit as counting accessible units; it does not and cannot from the public LIHTC file.",
        "- Do not treat `TRGT_DIS` as an accessible-unit measure; it is a target-population flag.",
        "- Do not equate the strict or broad overlap proxies with definitive Section 504 applicability. They are conservative observed-federal-overlap screens, useful for bounding the gap but not for resolving building-level legal status.",
        "- Read the standalone-LIHTC perimeter numbers as observed-proxy bounds on the excluded black hole, not as final legal coverage determinations.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_inputs()
    frame = load_lihtc()
    results = build_results(frame)
    markdown = build_markdown(results)

    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(markdown, encoding="utf-8")

    print("Created/updated:")
    for path in FILES_CREATED_OR_MODIFIED:
        print(f"- {path}")
    print()
    print("Headline findings:")
    for finding in results["headline_findings"]:
        print(f"- {finding}")


if __name__ == "__main__":
    main()
