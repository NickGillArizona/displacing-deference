#!/usr/bin/env python3
"""
Build a Massachusetts-vs-controls state complaint panel from HUD/FHEO filed cases.

Outputs:
- results/state_complaint_panel_results.json
- results/state_complaint_panel_analysis.md
- results/state_complaint_panel_total_complaints.svg
- results/state_complaint_panel_disability_share.svg

Design choices:
- Uses only the Python standard library so it can run in the current WSL repo
  environment without pandas/openpyxl.
- Reads the local FHEO case-level XLSX if present; otherwise downloads it from
  the public HUD/Data.gov URL referenced in the catalog metadata.
- Computes a state x year panel for MA, CT, NH, VT, and RI.
- Treats 2020 as a partial year because the local FHEO case-level file ends on
  2020-06-30.
- Includes supplemental national NFHA trend data and Massachusetts-only MCAD
  trend data, but does not treat those series as directly comparable to the
  state-level FHEO panel.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import shutil
import statistics
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from html import escape
from pathlib import Path
from typing import Any
from zipfile import ZipFile


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
DATA_DIR = REPO_DIR / "data"
RESULTS_DIR = REPO_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FHEO_XLSX_PATH = DATA_DIR / "fheo-filed-cases.xlsx"
LEGACY_FHEO_XLS_PATH = DATA_DIR / "fha-cases-by-year.xls"
FHEO_DOWNLOAD_URL = (
    "https://inventory.data.gov/dataset/c592e01e-3ce8-4fb7-b112-8b5819fd2072/"
    "resource/94b8f073-7d71-4519-8a2b-2cec554e3dcd/download/fheo-filed-cases.xlsx"
)

OUTPUT_JSON = RESULTS_DIR / "state_complaint_panel_results.json"
OUTPUT_MD = RESULTS_DIR / "state_complaint_panel_analysis.md"
OUTPUT_TOTAL_SVG = RESULTS_DIR / "state_complaint_panel_total_complaints.svg"
OUTPUT_SHARE_SVG = RESULTS_DIR / "state_complaint_panel_disability_share.svg"

XML_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
SHEET_MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CELL_REF_RE = re.compile(r"([A-Z]+)(\d+)")

TARGET_STATES = [
    ("MA", "Massachusetts"),
    ("CT", "Connecticut"),
    ("NH", "New Hampshire"),
    ("VT", "Vermont"),
    ("RI", "Rhode Island"),
]
STATE_NAME_TO_ABBR = {name: abbr for abbr, name in TARGET_STATES}
STATE_ABBR_TO_NAME = {abbr: name for abbr, name in TARGET_STATES}
CONTROL_STATES = ["CT", "NH", "VT", "RI"]
TREATMENT_STATE = "MA"

LAUNCH_DATE = dt.date(2021, 8, 18)
LAUNCH_LABEL = "Housing Navigator Massachusetts launch"

NFHA_NATIONAL_SERIES = [
    {
        "complaint_year": 2020,
        "total_complaints": 28712,
        "disability_complaints": 15664,
        "disability_share_pct": 54.56,
        "report_title": "2021 Fair Housing Trends Report",
        "report_url": "https://nationalfairhousing.org/wp-content/uploads/2021/07/2021-Fair-Housing-Trends-Report_FINAL.pdf",
    },
    {
        "complaint_year": 2021,
        "total_complaints": 31216,
        "disability_complaints": 16758,
        "disability_share_pct": 53.68,
        "report_title": "2022 Fair Housing Trends Report",
        "report_url": "https://nationalfairhousing.org/wp-content/uploads/2022/11/2022-Fair-Housing-Trends-Report.pdf",
    },
    {
        "complaint_year": 2022,
        "total_complaints": 33007,
        "disability_complaints": 17580,
        "disability_share_pct": 53.26,
        "report_title": "2023 Fair Housing Trends Report",
        "report_url": "https://nationalfairhousing.org/wp-content/uploads/2023/08/2023-Trends-Report-Final.pdf",
    },
    {
        "complaint_year": 2023,
        "total_complaints": 34150,
        "disability_complaints": 17986,
        "disability_share_pct": 52.61,
        "report_title": "2024 Fair Housing Trends Report",
        "report_url": "https://nationalfairhousing.org/wp-content/uploads/2023/04/2024-Fair-Housing-Trends-Report-FINAL_07.2024.pdf",
    },
    {
        "complaint_year": 2024,
        "total_complaints": 32321,
        "disability_complaints": 17645,
        "disability_share_pct": 54.59,
        "report_title": "2025 Fair Housing Trends Report",
        "report_url": "https://nationalfairhousing.org/wp-content/uploads/2025/11/2025-NFHA-Fair-Housing-Trends-Report.pdf",
    },
]

MCAD_SERIES = [
    {
        "fiscal_year": "FY20",
        "period": "2019-07-01 to 2020-06-30",
        "all_jurisdiction_complaints": 2778,
        "housing_jurisdiction_complaints": 329,
        "disability_protected_category_complaints": 1083,
        "report_url": "https://www.mass.gov/doc/mcad-fy20-annual-report/download",
        "comparability_note": "MCAD covers all commission jurisdictions; disability complaints are not housing-specific.",
    },
    {
        "fiscal_year": "FY21",
        "period": "2020-07-01 to 2021-06-30",
        "all_jurisdiction_complaints": 2463,
        "housing_jurisdiction_complaints": 263,
        "private_housing_complaints": 212,
        "public_housing_complaints": 51,
        "disability_protected_category_complaints": 1060,
        "report_url": "https://www.mass.gov/doc/mcad-fy21-annual-report/download",
        "comparability_note": "MCAD covers all commission jurisdictions; disability complaints are not housing-specific.",
    },
    {
        "fiscal_year": "FY22",
        "period": "2021-07-01 to 2022-06-30",
        "all_jurisdiction_complaints": 2822,
        "housing_jurisdiction_complaints": 366,
        "private_housing_complaints": 285,
        "public_housing_complaints": 81,
        "disability_protected_category_complaints": 1088,
        "report_url": "https://www.mass.gov/doc/mcad-fy22-annual-report/download",
        "comparability_note": "MCAD covers all commission jurisdictions; disability complaints are not housing-specific.",
    },
    {
        "fiscal_year": "FY23",
        "period": "2022-07-01 to 2023-06-30",
        "all_jurisdiction_complaints": 3086,
        "housing_jurisdiction_complaints": 427,
        "private_housing_complaints": 306,
        "public_housing_complaints": 121,
        "disability_protected_category_complaints": 1237,
        "report_url": "https://www.mass.gov/doc/mcad-fy23-annual-report/download",
        "comparability_note": "MCAD covers all commission jurisdictions; disability complaints are not housing-specific.",
    },
    {
        "fiscal_year": "FY24",
        "period": "2023-07-01 to 2024-06-30",
        "all_jurisdiction_complaints": 3553,
        "housing_jurisdiction_complaints": None,
        "disability_protected_category_complaints": None,
        "report_url": "https://www.mass.gov/doc/mcad-fy24-annual-report/download",
        "comparability_note": "The report text gives total complaints filed, but the housing/disability chart values were not machine-readable in text extraction.",
    },
    {
        "fiscal_year": "FY25",
        "period": "2024-07-01 to 2025-06-30",
        "all_jurisdiction_complaints": 3243,
        "housing_jurisdiction_complaints": None,
        "disability_protected_category_complaints": None,
        "report_url": "https://www.mass.gov/doc/mcad-fy25-annual-report/download",
        "comparability_note": "The report text gives total complaints filed, but the housing/disability chart values were not machine-readable in text extraction.",
    },
]


def download_if_missing(path: Path, url: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, path.open("wb") as output:
        shutil.copyfileobj(response, output)


def safe_int(value: Any) -> int:
    if value in (None, "", "."):
        return 0
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    text = str(value).replace(",", "").strip()
    if not text:
        return 0
    return int(round(float(text)))


def safe_float(value: Any) -> float | None:
    if value in (None, "", "."):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    return float(text)


def pct_change(old: float, new: float) -> float | None:
    if old == 0:
        return None
    return ((new - old) / old) * 100.0


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return statistics.mean(values)


def round_or_none(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(value, digits)


def excel_serial_to_date(value: Any) -> dt.date | None:
    if value in (None, ""):
        return None
    if isinstance(value, dt.date):
        return value
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, (int, float)):
        serial = float(value)
    else:
        text = str(value).strip()
        if not text:
            return None
        try:
            serial = float(text)
        except ValueError:
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
                try:
                    return dt.datetime.strptime(text, fmt).date()
                except ValueError:
                    continue
            return None
    return (dt.datetime(1899, 12, 30) + dt.timedelta(days=serial)).date()


def load_shared_strings(zf: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    shared_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for si in shared_root:
        values.append("".join(t.text or "" for t in si.iter(f"{SHEET_MAIN_NS}t")))
    return values


def first_sheet_path(zf: ZipFile) -> str:
    workbook = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
    first_sheet = workbook.find("a:sheets", XML_NS)[0]
    rel_id = first_sheet.attrib[f"{{{XML_NS['r']}}}id"]
    return "xl/" + rel_map[rel_id]


def cell_value(cell: ET.Element, shared_strings: list[str]) -> str | None:
    cell_type = cell.attrib.get("t")
    value_node = cell.find("a:v", XML_NS)
    inline_node = cell.find("a:is", XML_NS)
    if cell_type == "s" and value_node is not None:
        return shared_strings[int(value_node.text)]
    if cell_type == "inlineStr" and inline_node is not None:
        return "".join(t.text or "" for t in inline_node.iter(f"{SHEET_MAIN_NS}t"))
    if value_node is not None:
        return value_node.text
    return None


def iter_fheo_cases(xlsx_path: Path) -> tuple[list[dict[str, Any]], dt.date, dt.date]:
    rows: list[dict[str, Any]] = []
    min_date: dt.date | None = None
    max_date: dt.date | None = None
    wanted_cols = {"B", "C", "E", "T"}

    with ZipFile(xlsx_path) as zf:
        shared_strings = load_shared_strings(zf)
        sheet_root = ET.fromstring(zf.read(first_sheet_path(zf)))
        sheet_data = sheet_root.find("a:sheetData", XML_NS)
        if sheet_data is None:
            raise ValueError(f"No sheet data found in {xlsx_path}")

        for row in sheet_data:
            row_number = int(row.attrib["r"])
            if row_number < 6:
                continue
            row_map: dict[str, Any] = {}
            for cell in row:
                ref = cell.attrib.get("r", "")
                match = CELL_REF_RE.match(ref)
                if not match:
                    continue
                col = match.group(1)
                if col not in wanted_cols:
                    continue
                row_map[col] = cell_value(cell, shared_strings)

            state_name = str(row_map.get("C") or "").strip()
            if state_name not in STATE_NAME_TO_ABBR:
                continue
            filing_date = excel_serial_to_date(row_map.get("B"))
            if filing_date is None:
                continue

            if min_date is None or filing_date < min_date:
                min_date = filing_date
            if max_date is None or filing_date > max_date:
                max_date = filing_date

            rows.append(
                {
                    "state_name": state_name,
                    "state_abbr": STATE_NAME_TO_ABBR[state_name],
                    "year": filing_date.year,
                    "filing_date": filing_date.isoformat(),
                    "total_complaints": safe_int(row_map.get("E")),
                    "disability_complaints": safe_int(row_map.get("T")),
                }
            )

    if min_date is None or max_date is None:
        raise ValueError("No usable FHEO rows found for target states")
    return rows, min_date, max_date


def build_panel(case_rows: list[dict[str, Any]], max_date: dt.date) -> list[dict[str, Any]]:
    panel_map: dict[tuple[str, int], dict[str, Any]] = {}
    partial_year = max_date.year if max_date.month < 12 or max_date.day < 31 else None

    for row in case_rows:
        key = (row["state_abbr"], row["year"])
        if key not in panel_map:
            panel_map[key] = {
                "state_abbr": row["state_abbr"],
                "state_name": row["state_name"],
                "year": row["year"],
                "total_complaints": 0,
                "disability_complaints": 0,
            }
        panel_map[key]["total_complaints"] += row["total_complaints"]
        panel_map[key]["disability_complaints"] += row["disability_complaints"]

    panel = []
    for _, entry in sorted(panel_map.items(), key=lambda item: (item[0][0], item[0][1])):
        total = entry["total_complaints"]
        disability = entry["disability_complaints"]
        share = (disability / total) if total else None
        panel.append(
            {
                **entry,
                "disability_share": round_or_none(share, 6),
                "disability_share_pct": round_or_none(share * 100 if share is not None else None, 2),
                "is_partial_year": entry["year"] == partial_year,
            }
        )
    return panel


def control_series(panel: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_year_avg: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_year_sum: dict[int, dict[str, Any]] = defaultdict(lambda: {"total": 0, "disability": 0})

    for row in panel:
        if row["state_abbr"] in CONTROL_STATES:
            by_year_avg[row["year"]].append(row)
            by_year_sum[row["year"]]["total"] += row["total_complaints"]
            by_year_sum[row["year"]]["disability"] += row["disability_complaints"]

    avg_rows: list[dict[str, Any]] = []
    combined_rows: list[dict[str, Any]] = []
    for year in sorted(by_year_avg):
        rows = by_year_avg[year]
        total_avg = statistics.mean(r["total_complaints"] for r in rows)
        disability_avg = statistics.mean(r["disability_complaints"] for r in rows)
        share_avg = statistics.mean(float(r["disability_share"] or 0.0) for r in rows)
        avg_rows.append(
            {
                "year": year,
                "control_states": CONTROL_STATES,
                "average_total_complaints": round(total_avg, 4),
                "average_disability_complaints": round(disability_avg, 4),
                "average_disability_share": round(share_avg, 6),
                "average_disability_share_pct": round(share_avg * 100, 2),
                "is_partial_year": any(r["is_partial_year"] for r in rows),
            }
        )

        combined_total = by_year_sum[year]["total"]
        combined_disability = by_year_sum[year]["disability"]
        combined_share = combined_disability / combined_total if combined_total else None
        combined_rows.append(
            {
                "year": year,
                "combined_control_total_complaints": combined_total,
                "combined_control_disability_complaints": combined_disability,
                "combined_control_disability_share": round_or_none(combined_share, 6),
                "combined_control_disability_share_pct": round_or_none(
                    combined_share * 100 if combined_share is not None else None, 2
                ),
                "is_partial_year": any(r["is_partial_year"] for r in rows),
            }
        )
    return avg_rows, combined_rows


def rows_by_state(panel: list[dict[str, Any]], state_abbr: str, full_year_only: bool = False) -> list[dict[str, Any]]:
    rows = [row for row in panel if row["state_abbr"] == state_abbr]
    if full_year_only:
        rows = [row for row in rows if not row["is_partial_year"]]
    return sorted(rows, key=lambda row: row["year"])


def build_summary(panel: list[dict[str, Any]], control_avg: list[dict[str, Any]], control_combined: list[dict[str, Any]]) -> dict[str, Any]:
    mass_rows = rows_by_state(panel, TREATMENT_STATE, full_year_only=True)
    control_rows = [row for row in control_avg if not row["is_partial_year"]]
    combined_rows = [row for row in control_combined if not row["is_partial_year"]]

    first_year = min(row["year"] for row in mass_rows)
    latest_full_year = max(row["year"] for row in mass_rows)

    mass_first = next(row for row in mass_rows if row["year"] == first_year)
    mass_last = next(row for row in mass_rows if row["year"] == latest_full_year)
    control_first = next(row for row in control_rows if row["year"] == first_year)
    control_last = next(row for row in control_rows if row["year"] == latest_full_year)
    combined_last = next(row for row in combined_rows if row["year"] == latest_full_year)

    state_rank_latest = sorted(
        (row for row in panel if row["year"] == latest_full_year),
        key=lambda row: row["total_complaints"],
        reverse=True,
    )

    mass_peak_total = max(mass_rows, key=lambda row: row["total_complaints"])
    mass_peak_share = max(mass_rows, key=lambda row: float(row["disability_share"] or 0.0))

    return {
        "full_year_window": {"start_year": first_year, "end_year": latest_full_year},
        "massachusetts_full_year_averages": {
            "average_total_complaints": round(mean_or_none([row["total_complaints"] for row in mass_rows]) or 0.0, 4),
            "average_disability_complaints": round(mean_or_none([row["disability_complaints"] for row in mass_rows]) or 0.0, 4),
            "average_disability_share_pct": round(mean_or_none([row["disability_share_pct"] for row in mass_rows]) or 0.0, 2),
        },
        "average_control_state_full_year_averages": {
            "average_total_complaints": round(mean_or_none([row["average_total_complaints"] for row in control_rows]) or 0.0, 4),
            "average_disability_complaints": round(mean_or_none([row["average_disability_complaints"] for row in control_rows]) or 0.0, 4),
            "average_disability_share_pct": round(mean_or_none([row["average_disability_share_pct"] for row in control_rows]) or 0.0, 2),
        },
        "massachusetts_change_first_to_latest_full_year": {
            "first_year": first_year,
            "latest_full_year": latest_full_year,
            "total_complaints_pct_change": round_or_none(
                pct_change(float(mass_first["total_complaints"]), float(mass_last["total_complaints"])), 2
            ),
            "disability_complaints_pct_change": round_or_none(
                pct_change(float(mass_first["disability_complaints"]), float(mass_last["disability_complaints"])), 2
            ),
            "disability_share_pp_change": round(
                float(mass_last["disability_share_pct"] or 0.0) - float(mass_first["disability_share_pct"] or 0.0),
                2,
            ),
        },
        "average_control_state_change_first_to_latest_full_year": {
            "first_year": first_year,
            "latest_full_year": latest_full_year,
            "total_complaints_pct_change": round_or_none(
                pct_change(float(control_first["average_total_complaints"]), float(control_last["average_total_complaints"])), 2
            ),
            "disability_complaints_pct_change": round_or_none(
                pct_change(float(control_first["average_disability_complaints"]), float(control_last["average_disability_complaints"])), 2
            ),
            "disability_share_pp_change": round(
                float(control_last["average_disability_share_pct"] or 0.0)
                - float(control_first["average_disability_share_pct"] or 0.0),
                2,
            ),
        },
        "latest_full_year_comparison": {
            "year": latest_full_year,
            "massachusetts_total_complaints": mass_last["total_complaints"],
            "massachusetts_disability_complaints": mass_last["disability_complaints"],
            "massachusetts_disability_share_pct": mass_last["disability_share_pct"],
            "average_control_total_complaints": control_last["average_total_complaints"],
            "average_control_disability_complaints": control_last["average_disability_complaints"],
            "average_control_disability_share_pct": control_last["average_disability_share_pct"],
            "combined_controls_total_complaints": combined_last["combined_control_total_complaints"],
            "combined_controls_disability_complaints": combined_last["combined_control_disability_complaints"],
            "combined_controls_disability_share_pct": combined_last["combined_control_disability_share_pct"],
            "pooled_controls_total_complaints": combined_last["combined_control_total_complaints"],
            "pooled_controls_disability_complaints": combined_last["combined_control_disability_complaints"],
            "pooled_controls_disability_share_pct": combined_last["combined_control_disability_share_pct"],
            "massachusetts_to_average_control_total_ratio": round(
                mass_last["total_complaints"] / float(control_last["average_total_complaints"]), 2
            ),
            "massachusetts_to_average_control_disability_ratio": round(
                mass_last["disability_complaints"] / float(control_last["average_disability_complaints"]), 2
            ),
            "massachusetts_vs_average_control_share_gap_pp": round(
                float(mass_last["disability_share_pct"] or 0.0)
                - float(control_last["average_disability_share_pct"] or 0.0),
                2,
            ),
            "massachusetts_to_pooled_controls_total_ratio": round(
                mass_last["total_complaints"] / float(combined_last["combined_control_total_complaints"]), 2
            ),
            "massachusetts_to_pooled_controls_disability_ratio": round(
                mass_last["disability_complaints"] / float(combined_last["combined_control_disability_complaints"]), 2
            ),
            "massachusetts_vs_pooled_controls_share_gap_pp": round(
                float(mass_last["disability_share_pct"] or 0.0)
                - float(combined_last["combined_control_disability_share_pct"] or 0.0),
                2,
            ),
            "massachusetts_vs_combined_controls_total_pct": round_or_none(
                pct_change(
                    float(combined_last["combined_control_total_complaints"]),
                    float(mass_last["total_complaints"]),
                ),
                2,
            ),
            "massachusetts_vs_combined_controls_disability_pct": round_or_none(
                pct_change(
                    float(combined_last["combined_control_disability_complaints"]),
                    float(mass_last["disability_complaints"]),
                ),
                2,
            ),
        },
        "massachusetts_peaks": {
            "peak_total_complaints_year": mass_peak_total["year"],
            "peak_total_complaints": mass_peak_total["total_complaints"],
            "peak_disability_share_year": mass_peak_share["year"],
            "peak_disability_share_pct": mass_peak_share["disability_share_pct"],
        },
        "latest_full_year_state_rankings": [
            {
                "rank": idx + 1,
                "state_abbr": row["state_abbr"],
                "state_name": row["state_name"],
                "total_complaints": row["total_complaints"],
                "disability_complaints": row["disability_complaints"],
                "disability_share_pct": row["disability_share_pct"],
            }
            for idx, row in enumerate(state_rank_latest)
        ],
    }


def annual_panel_did_design() -> dict[str, Any]:
    if LAUNCH_DATE.month == 1 and LAUNCH_DATE.day == 1:
        return {
            "pre_end_year": LAUNCH_DATE.year - 1,
            "post_start_year": LAUNCH_DATE.year,
            "pre_period_rule": f"year <= {LAUNCH_DATE.year - 1}",
            "post_period_rule": f"year >= {LAUNCH_DATE.year}",
            "excluded_transition_years": [],
            "annual_panel_note": (
                "Annual state-year rows can treat the launch year as fully post only when treatment starts "
                "on January 1."
            ),
        }
    return {
        "pre_end_year": LAUNCH_DATE.year - 1,
        "post_start_year": LAUNCH_DATE.year + 1,
        "pre_period_rule": f"year <= {LAUNCH_DATE.year - 1}",
        "post_period_rule": f"year >= {LAUNCH_DATE.year + 1}",
        "excluded_transition_years": [LAUNCH_DATE.year],
        "annual_panel_note": (
            f"{LAUNCH_DATE.year} is excluded from annual pre/post cells because treatment starts on "
            f"{LAUNCH_DATE.isoformat()} and a single state-year row cannot separate pre- and post-launch filings."
        ),
    }


def compute_simple_did(panel: list[dict[str, Any]]) -> dict[str, Any]:
    did_design = annual_panel_did_design()
    usable = [
        row
        for row in panel
        if not row["is_partial_year"] and row["year"] not in did_design["excluded_transition_years"]
    ]
    post_rows = [row for row in usable if row["year"] >= did_design["post_start_year"]]
    if not post_rows:
        return {
            "available": False,
            "treatment_state": TREATMENT_STATE,
            "control_states": CONTROL_STATES,
            "pre_period_rule": did_design["pre_period_rule"],
            "post_period_rule": did_design["post_period_rule"],
            "excluded_transition_years": did_design["excluded_transition_years"],
            "annual_panel_note": did_design["annual_panel_note"],
            "reason": (
                "No comparable post-launch full-year state panel exists in the FHEO file. The local case-level "
                "dataset ends on 2020-06-30, so it never reaches the first clean annual post period defined above; "
                "later supplementary series are Massachusetts-only or nationally aggregated rather than comparable "
                "state x year controls."
            ),
        }

    mass_pre = [
        row for row in usable if row["state_abbr"] == TREATMENT_STATE and row["year"] <= did_design["pre_end_year"]
    ]
    mass_post = [
        row for row in usable if row["state_abbr"] == TREATMENT_STATE and row["year"] >= did_design["post_start_year"]
    ]
    control_pre = [
        row for row in usable if row["state_abbr"] in CONTROL_STATES and row["year"] <= did_design["pre_end_year"]
    ]
    control_post = [
        row for row in usable if row["state_abbr"] in CONTROL_STATES and row["year"] >= did_design["post_start_year"]
    ]

    if not (mass_pre and mass_post and control_pre and control_post):
        return {
            "available": False,
            "treatment_state": TREATMENT_STATE,
            "control_states": CONTROL_STATES,
            "pre_period_rule": did_design["pre_period_rule"],
            "post_period_rule": did_design["post_period_rule"],
            "excluded_transition_years": did_design["excluded_transition_years"],
            "annual_panel_note": did_design["annual_panel_note"],
            "reason": "At least one required pre/post treatment/control cell is empty.",
        }

    outcome_map = {
        "total_complaints": "total_complaints",
        "disability_complaints": "disability_complaints",
        "disability_share_pct": "disability_share_pct",
    }
    estimates: dict[str, Any] = {}
    for label, key in outcome_map.items():
        ma_pre_mean = statistics.mean(float(row[key]) for row in mass_pre)
        ma_post_mean = statistics.mean(float(row[key]) for row in mass_post)
        control_pre_mean = statistics.mean(float(row[key]) for row in control_pre)
        control_post_mean = statistics.mean(float(row[key]) for row in control_post)
        estimates[label] = {
            "massachusetts_pre_mean": round(ma_pre_mean, 4),
            "massachusetts_post_mean": round(ma_post_mean, 4),
            "control_pre_mean": round(control_pre_mean, 4),
            "control_post_mean": round(control_post_mean, 4),
            "difference_in_differences": round((ma_post_mean - ma_pre_mean) - (control_post_mean - control_pre_mean), 4),
        }

    return {
        "available": True,
        "treatment_state": TREATMENT_STATE,
        "control_states": CONTROL_STATES,
        "pre_period_rule": did_design["pre_period_rule"],
        "post_period_rule": did_design["post_period_rule"],
        "excluded_transition_years": did_design["excluded_transition_years"],
        "annual_panel_note": did_design["annual_panel_note"],
        "estimates": estimates,
    }


def latest_full_year_rows(panel: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full_years = sorted({row["year"] for row in panel if not row["is_partial_year"]})
    latest = full_years[-1]
    return sorted(
        [row for row in panel if row["year"] == latest],
        key=lambda row: row["total_complaints"],
        reverse=True,
    )


def y_ticks(max_value: float, steps: int = 5) -> list[float]:
    if max_value <= 0:
        return [0.0]
    raw_step = max_value / steps
    magnitude = 10 ** int(math.floor(math.log10(raw_step))) if raw_step > 0 else 1
    residual = raw_step / magnitude
    if residual <= 1:
        nice = 1
    elif residual <= 2:
        nice = 2
    elif residual <= 5:
        nice = 5
    else:
        nice = 10
    step = nice * magnitude
    top = math.ceil(max_value / step) * step
    ticks = [i * step for i in range(0, int(top / step) + 1)]
    return ticks if ticks else [0.0]


def line_path(years: list[int], values_by_year: dict[int, float], x_fn: Any, y_fn: Any) -> str:
    points = [(x_fn(year), y_fn(values_by_year[year])) for year in years if year in values_by_year]
    if not points:
        return ""
    commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    commands.extend(f"L {x:.2f} {y:.2f}" for x, y in points[1:])
    return " ".join(commands)


def write_svg_line_chart(
    path: Path,
    years: list[int],
    series: list[dict[str, Any]],
    title: str,
    subtitle: str,
    value_label: str,
    note: str,
) -> None:
    width, height = 920, 560
    left, right, top, bottom = 80, 30, 85, 70
    plot_width = width - left - right
    plot_height = height - top - bottom

    x_years = sorted(set(years + [LAUNCH_DATE.year]))
    x_min = min(x_years)
    x_max = max(x_years)
    all_values: list[float] = []
    for item in series:
        all_values.extend(item["data"].values())
    max_y = max(all_values) if all_values else 1.0
    tick_values = y_ticks(max_y * 1.05)
    y_max = max(tick_values) if tick_values else max_y
    if y_max == 0:
        y_max = 1.0

    def x_pos(year: int) -> float:
        span = x_max - x_min if x_max != x_min else 1
        return left + ((year - x_min) / span) * plot_width

    def y_pos(value: float) -> float:
        return top + plot_height - (value / y_max) * plot_height

    x_labels = x_years if len(x_years) <= 12 else [year for year in x_years if year % 2 == 0 or year == x_min or year == x_max]
    launch_x = x_pos(LAUNCH_DATE.year)

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="32" font-family="Arial, sans-serif" font-size="22" font-weight="bold">{escape(title)}</text>',
        f'<text x="{left}" y="54" font-family="Arial, sans-serif" font-size="12" fill="#555">{escape(subtitle)}</text>',
        f'<text x="{left}" y="{height - 18}" font-family="Arial, sans-serif" font-size="11" fill="#666">{escape(note)}</text>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#333" stroke-width="1.2"/>',
        f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#333" stroke-width="1.2"/>',
    ]

    for tick in tick_values:
        y = y_pos(tick)
        label = f"{tick:.0f}%" if value_label == "percent" else f"{tick:,.0f}"
        svg.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" stroke="#e5e5e5" stroke-width="1"/>')
        svg.append(
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#555">{escape(label)}</text>'
        )

    for year in x_labels:
        x = x_pos(year)
        svg.append(f'<line x1="{x:.2f}" y1="{top + plot_height}" x2="{x:.2f}" y2="{top + plot_height + 6}" stroke="#333" stroke-width="1"/>')
        svg.append(
            f'<text x="{x:.2f}" y="{top + plot_height + 22}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#555">{year}</text>'
        )

    svg.append(
        f'<line x1="{launch_x:.2f}" y1="{top}" x2="{launch_x:.2f}" y2="{top + plot_height}" stroke="#999" stroke-width="1.5" stroke-dasharray="6 4"/>'
    )
    svg.append(
        f'<text x="{launch_x + 6:.2f}" y="{top + 14}" font-family="Arial, sans-serif" font-size="11" fill="#666">2021 launch</text>'
    )

    for item in series:
        ordered_years = sorted(item["data"])
        path_d = line_path(ordered_years, item["data"], x_pos, y_pos)
        svg.append(
            f'<path d="{path_d}" fill="none" stroke="{item["color"]}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for year in ordered_years:
            value = item["data"][year]
            svg.append(
                f'<circle cx="{x_pos(year):.2f}" cy="{y_pos(value):.2f}" r="3.5" fill="{item["color"]}"/>'
            )

    legend_x = left + plot_width - 190
    legend_y = top + 8
    for idx, item in enumerate(series):
        y = legend_y + idx * 22
        svg.append(f'<line x1="{legend_x}" y1="{y}" x2="{legend_x + 22}" y2="{y}" stroke="{item["color"]}" stroke-width="3"/>')
        svg.append(
            f'<text x="{legend_x + 30}" y="{y + 4}" font-family="Arial, sans-serif" font-size="12" fill="#333">{escape(item["name"])}</text>'
        )

    svg.append('</svg>')
    path.write_text("\n".join(svg), encoding="utf-8")


def latest_year_table_md(rows: list[dict[str, Any]]) -> str:
    header = "| State | Total complaints | Disability complaints | Disability share |\n|---|---:|---:|---:|"
    body = [
        f"| {row['state_abbr']} | {row['total_complaints']:,} | {row['disability_complaints']:,} | {row['disability_share_pct']:.2f}% |"
        for row in rows
    ]
    return "\n".join([header] + body)


def supplemental_table_md_nfha() -> str:
    header = "| Complaint year | Total complaints | Disability complaints | Disability share | Source |\n|---|---:|---:|---:|---|"
    body = [
        f"| {row['complaint_year']} | {row['total_complaints']:,} | {row['disability_complaints']:,} | {row['disability_share_pct']:.2f}% | [{row['report_title']}]({row['report_url']}) |"
        for row in NFHA_NATIONAL_SERIES
    ]
    return "\n".join([header] + body)


def supplemental_table_md_mcad() -> str:
    header = "| Fiscal year | Period | All MCAD complaints | Housing-jurisdiction complaints | Disability protected-category complaints | Source |\n|---|---|---:|---:|---:|---|"
    body = []
    for row in MCAD_SERIES:
        housing = "—" if row.get("housing_jurisdiction_complaints") is None else f"{row['housing_jurisdiction_complaints']:,}"
        disability = "—" if row.get("disability_protected_category_complaints") is None else f"{row['disability_protected_category_complaints']:,}"
        body.append(
            f"| {row['fiscal_year']} | {row['period']} | {row['all_jurisdiction_complaints']:,} | {housing} | {disability} | [report]({row['report_url']}) |"
        )
    return "\n".join([header] + body)


def build_memo(results: dict[str, Any]) -> str:
    summary = results["summary_stats"]
    latest = summary["latest_full_year_comparison"]
    latest_rows = latest_full_year_rows(results["panel"])
    mcad_fy21 = next(row for row in MCAD_SERIES if row["fiscal_year"] == "FY21")
    mcad_fy23 = next(row for row in MCAD_SERIES if row["fiscal_year"] == "FY23")
    provenance = results["metadata"]["source_provenance"]
    comparison = results["metadata"]["comparison_construction"]
    count_note = results["metadata"]["count_normalization_note"]

    return f"""# State complaint panel: Massachusetts vs. CT/NH/VT/RI

Generated: {results['metadata']['generated_at_utc']}

## What this file does

This memo builds a state x year panel from the local HUD/FHEO filed-case file for Massachusetts and four New England comparator states (CT, NH, VT, RI), then asks whether that panel can credibly support a Housing Navigator Massachusetts launch analysis.

## Core data coverage

- Primary panel source: `data/fheo-filed-cases.xlsx`
- FHEO file coverage for this panel: {results['metadata']['source_date_range']['min_filing_date']} to {results['metadata']['source_date_range']['max_filing_date']}
- The local FHEO case-level file therefore supports full annual state comparisons only through {summary['full_year_window']['end_year']}; 2020 is partial because the file ends on 2020-06-30.
- Housing Navigator Massachusetts launch marker used here: {LAUNCH_DATE.isoformat()} ({LAUNCH_LABEL})
- {count_note}

## Provenance note on the HUD files

- This analysis uses `{provenance['primary_panel_source']['path']}`, the local HUD/FHEO case-level workbook, because it preserves filing dates and extends through 2020-06-30.
- Those filing dates let the script rebuild the MA/CT/NH/VT/RI panel directly from underlying rows and correctly flag 2020 as a partial year.
- The older `{provenance['older_aggregate_reference']['path']}` file in the repo is an earlier pre-aggregated year/state table documented in this repo as covering {provenance['older_aggregate_reference']['repo_documentation_coverage']}. It remains useful as an aggregate reference for overlapping pre-2020 years, but it lacks the case-level filing dates and later 2020 coverage used for this memo.

## Bottom line

There is no defensible Massachusetts-vs-control post-launch DiD in the FHEO panel because the comparable state-level file stops before the August 2021 launch. The FHEO data remain useful as a pre-launch baseline, but not as post-launch causal evidence.

## How to read the control comparisons

- Average control state: {comparison['average_control_state']['definition']}
- Pooled controls: {comparison['pooled_controls']['definition']}
- The plots use the average-control series, not the pooled-control sum.

## Main pre-launch panel findings

- Massachusetts had the largest FHEO complaint volume in this five-state comparison throughout the full-year window ({summary['full_year_window']['start_year']}-{summary['full_year_window']['end_year']}).
- From {summary['full_year_window']['start_year']} to {summary['full_year_window']['end_year']}, Massachusetts total complaints rose by {summary['massachusetts_change_first_to_latest_full_year']['total_complaints_pct_change']:.2f}% and disability-basis complaints rose by {summary['massachusetts_change_first_to_latest_full_year']['disability_complaints_pct_change']:.2f}%.
- Over the same years, the average comparator state's total complaints were essentially flat ({summary['average_control_state_change_first_to_latest_full_year']['total_complaints_pct_change']:.2f}%), while average disability complaints rose {summary['average_control_state_change_first_to_latest_full_year']['disability_complaints_pct_change']:.2f}%.
- Massachusetts's disability share rose by {summary['massachusetts_change_first_to_latest_full_year']['disability_share_pp_change']:.2f} percentage points across the full pre-launch window, but it still sat {abs(latest['massachusetts_vs_average_control_share_gap_pp']):.2f} points below the average control-state disability share in the latest full year ({latest['year']}).
- In {latest['year']}, Massachusetts recorded {latest['massachusetts_total_complaints']:,} total complaints and {latest['massachusetts_disability_complaints']:,} disability-basis complaints, versus an average control-state level of {latest['average_control_total_complaints']:,} total complaints and {latest['average_control_disability_complaints']:,} disability complaints.
- In that same year, the pooled controls (CT/NH/VT/RI summed together) recorded {latest['pooled_controls_total_complaints']:,} total complaints and {latest['pooled_controls_disability_complaints']:,} disability-basis complaints, with a {latest['pooled_controls_disability_share_pct']:.2f}% disability share.
- In the latest full year, Massachusetts had about {latest['massachusetts_to_average_control_total_ratio']:.2f}x the average control state's total complaint volume and {latest['massachusetts_to_average_control_disability_ratio']:.2f}x the average control state's disability complaint volume; versus pooled controls, Massachusetts was {latest['massachusetts_to_pooled_controls_total_ratio']:.2f}x and {latest['massachusetts_to_pooled_controls_disability_ratio']:.2f}x as large, respectively.

## Latest full-year panel snapshot ({latest['year']})

{latest_year_table_md(latest_rows)}

## What the FHEO panel can and cannot identify

What it can do:
- Establish a clean pre-launch baseline for Massachusetts relative to nearby comparator states.
- Show long-run pre-2021 levels and disability-share trajectories.
- Demonstrate that Massachusetts complaint volume was already much larger than comparator-state averages before the registry launch.

What it cannot do:
- Estimate a Massachusetts-vs-controls post-2021 treatment effect for Housing Navigator.
- Support a simple DiD with the chosen controls, because the comparable state-level panel ends before treatment.
- Treat all of calendar year 2021 as post in any future annual-panel DiD refresh; with an August 18, 2021 launch, 2021 is a transition year and 2022 would be the first clean annual post period.

## Supplemental context (not directly comparable to the FHEO panel)

### NFHA national trend series

These national series show that disability remained the largest basis of fair housing complaints after 2020, but they are national aggregates rather than Massachusetts-vs-control state data.

{supplemental_table_md_nfha()}

### Massachusetts-only MCAD series

These figures are useful context for Massachusetts complaint-processing activity after launch, but they are not a substitute for the missing post-2021 control-state panel. MCAD covers multiple jurisdictions beyond housing, reports by fiscal year, and its disability counts are not housing-specific.

{supplemental_table_md_mcad()}

Contextual read:
- MCAD all-jurisdiction complaints rose from {mcad_fy21['all_jurisdiction_complaints']:,} in {mcad_fy21['fiscal_year']} to {mcad_fy23['all_jurisdiction_complaints']:,} in {mcad_fy23['fiscal_year']}.
- MCAD housing-jurisdiction complaints likewise rose from {mcad_fy21['housing_jurisdiction_complaints']:,} in {mcad_fy21['fiscal_year']} to {mcad_fy23['housing_jurisdiction_complaints']:,} in {mcad_fy23['fiscal_year']}.
- That pattern is consistent with continued demand for complaint-processing capacity in Massachusetts, but it cannot isolate any effect of the Housing Navigator registry because the series lacks comparable control states and mixes housing with broader MCAD jurisdictional structure.

## Limitations

1. The primary comparable state-level FHEO file ends on 2020-06-30, so 2020 is partial and there are no post-launch years for a clean DiD.
2. Any future annual-panel DiD should exclude 2021 as a transition year because the launch occurred on 2021-08-18 rather than on January 1.
3. Complaint-volume comparisons here use raw filed-complaint counts; they are not normalized by population, renter households, disability prevalence, or housing stock.
4. FHEO disability counts are basis counts, not mutually exclusive case categories; a single complaint can list multiple protected-class bases.
5. MCAD post-2020 data are Massachusetts-only, fiscal-year, and broader than fair-housing-only Title VIII complaints.
6. NFHA trend data are national aggregates compiled from mixed reporting calendars (private groups report calendar-year data; HUD/FHAP/DOJ report by federal fiscal year).
7. Small comparator states, especially NH and VT, have low annual counts, so disability-share series are more volatile there.

## Output files

- `results/state_complaint_panel_results.json`
- `results/state_complaint_panel_analysis.md`
- `results/state_complaint_panel_total_complaints.svg`
- `results/state_complaint_panel_disability_share.svg`
"""


def main() -> None:
    download_if_missing(FHEO_XLSX_PATH, FHEO_DOWNLOAD_URL)
    case_rows, min_date, max_date = iter_fheo_cases(FHEO_XLSX_PATH)
    panel = build_panel(case_rows, max_date)
    control_avg, control_combined = control_series(panel)
    summary = build_summary(panel, control_avg, control_combined)
    did = compute_simple_did(panel)

    mass_series_total = {
        row["year"]: float(row["total_complaints"]) for row in rows_by_state(panel, TREATMENT_STATE)
    }
    control_series_total = {
        row["year"]: float(row["average_total_complaints"]) for row in control_avg
    }
    mass_series_share = {
        row["year"]: float(row["disability_share_pct"] or 0.0) for row in rows_by_state(panel, TREATMENT_STATE)
    }
    control_series_share = {
        row["year"]: float(row["average_disability_share_pct"] or 0.0) for row in control_avg
    }
    chart_years = sorted({row["year"] for row in panel})

    write_svg_line_chart(
        OUTPUT_TOTAL_SVG,
        chart_years,
        [
            {"name": "Massachusetts", "color": "#1f77b4", "data": mass_series_total},
            {"name": "Average controls (CT/NH/VT/RI)", "color": "#ff7f0e", "data": control_series_total},
        ],
        "FHEO filed complaints: Massachusetts vs. average controls",
        "Orange line is the average control state (not the pooled-control sum); 2020 is partial-year through 2020-06-30.",
        "count",
        "Counts are raw complaints, not population- or housing-stock-normalized; the August 2021 launch marker is reference only.",
    )

    write_svg_line_chart(
        OUTPUT_SHARE_SVG,
        chart_years,
        [
            {"name": "Massachusetts", "color": "#1f77b4", "data": mass_series_share},
            {"name": "Average controls (CT/NH/VT/RI)", "color": "#ff7f0e", "data": control_series_share},
        ],
        "Disability complaint share: Massachusetts vs. average controls",
        "Orange line is the average control state; disability share is disability-basis complaints divided by total complaints within each state-year.",
        "percent",
        "2020 is partial-year; the 2021 launch marker is included for reference only because no comparable post-launch state panel exists here.",
    )

    results = {
        "metadata": {
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "script": str(Path(__file__).relative_to(REPO_DIR)),
            "source_file_used": str(FHEO_XLSX_PATH.relative_to(REPO_DIR)),
            "source_download_url_if_missing": FHEO_DOWNLOAD_URL,
            "source_date_range": {
                "min_filing_date": min_date.isoformat(),
                "max_filing_date": max_date.isoformat(),
            },
            "target_states": [
                {"state_abbr": abbr, "state_name": name} for abbr, name in TARGET_STATES
            ],
            "launch_event": {
                "label": LAUNCH_LABEL,
                "date": LAUNCH_DATE.isoformat(),
            },
            "comparison_construction": {
                "average_control_state": {
                    "definition": "Simple mean of CT/NH/VT/RI state-year values; each control state receives equal weight.",
                    "used_in_plots": True,
                },
                "pooled_controls": {
                    "definition": "Within-year sum of CT/NH/VT/RI state-year values; larger control states contribute more raw complaints.",
                    "used_in_plots": False,
                    "legacy_json_name": "combined_controls",
                },
            },
            "count_normalization_note": (
                "Complaint-volume comparisons use raw filed-complaint counts. They are not normalized by population, "
                "renter households, disability prevalence, or housing stock."
            ),
            "source_provenance": {
                "primary_panel_source": {
                    "path": str(FHEO_XLSX_PATH.relative_to(REPO_DIR)),
                    "type": "HUD/FHEO case-level workbook",
                    "sheet_name": "Filed Title VIII Cases",
                    "why_used_here": (
                        "Provides filing dates and extends through 2020-06-30, allowing the script to rebuild the "
                        "five-state panel directly from underlying rows and mark 2020 as a partial year."
                    ),
                },
                "older_aggregate_reference": {
                    "path": str(LEGACY_FHEO_XLS_PATH.relative_to(REPO_DIR)),
                    "type": "Older HUD/FHEO pre-aggregated year/state table",
                    "repo_documentation_coverage": "2000-2019",
                    "relationship_to_primary_source": (
                        "Useful as an older aggregate reference for overlapping pre-2020 years, but it lacks the case-level "
                        "filing dates and later 2020 coverage used for this memo."
                    ),
                },
            },
            "plots": [
                str(OUTPUT_TOTAL_SVG.relative_to(REPO_DIR)),
                str(OUTPUT_SHARE_SVG.relative_to(REPO_DIR)),
            ],
        },
        "panel": panel,
        "control_average_by_year": control_avg,
        "control_combined_by_year": control_combined,
        "control_pooled_by_year": control_combined,
        "summary_stats": summary,
        "did": did,
        "supplementary_context": {
            "nfha_national_series": NFHA_NATIONAL_SERIES,
            "mcad_massachusetts_series": MCAD_SERIES,
        },
        "limitations": [
            "Primary comparable state-level FHEO file ends on 2020-06-30, so 2020 is partial and there are no post-launch years for a clean DiD.",
            "Annual DiD coding excludes 2021 as a transition year because the August 18, 2021 launch does not align with calendar-year state-panel boundaries.",
            "Complaint-volume comparisons use raw filed-complaint counts and are not normalized by population, renter households, disability prevalence, or housing stock.",
            "Disability basis counts are not mutually exclusive case categories; one complaint may list multiple bases.",
            "MCAD post-2020 data are Massachusetts-only and broader than fair-housing-only Title VIII complaint counts.",
            "NFHA post-2020 data are national aggregates and combine agencies reporting on different reporting calendars.",
            "Small control states have low annual counts, which makes disability-share comparisons noisier.",
        ],
    }

    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_memo(results), encoding="utf-8")

    print("Created:")
    print(f"- {OUTPUT_JSON.relative_to(REPO_DIR)}")
    print(f"- {OUTPUT_MD.relative_to(REPO_DIR)}")
    print(f"- {OUTPUT_TOTAL_SVG.relative_to(REPO_DIR)}")
    print(f"- {OUTPUT_SHARE_SVG.relative_to(REPO_DIR)}")


if __name__ == "__main__":
    main()
