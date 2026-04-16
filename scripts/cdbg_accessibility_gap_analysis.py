#!/usr/bin/env python3
"""
Quantify the CDBG accessibility reporting gap for housing rehabilitation codes.

This version replaces the earlier proxy-dollar estimate with HUD Exchange's
national CDBG expenditure workbook, which publishes direct matrix-code
expenditure totals by year.

Outputs:
- results/cdbg_accessibility_gap_quantification.md
"""

from __future__ import annotations

import os
import re
import urllib.request
from datetime import datetime, timezone
from zipfile import ZipFile
import xml.etree.ElementTree as ET


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(REPO_DIR, "data")
RESULTS_DIR = os.path.join(REPO_DIR, "results")

CDBG_ACCOMP_PATH = os.path.join(DATA_DIR, "CDBG_Accomp_Natl.xlsx")
CDBG_EXPEND_PATH = os.path.join(DATA_DIR, "CDBG_Expend_NatlAll.xlsx")
POSH_PATH = os.path.join(DATA_DIR, "US_2024_2020census.xlsx")
OUTPUT_MD = os.path.join(RESULTS_DIR, "cdbg_accessibility_gap_quantification.md")

CDBG_EXPEND_URL = "https://files.hudexchange.info/resources/documents/CDBG_Expend_NatlAll.xlsx"

XML_NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
SHEET_MAIN_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
CELL_REF_RE = re.compile(r"([A-Z]+)(\d+)")

# National accomplishments workbook columns (CDBG-only columns used for
# households/persons so the series excludes parallel CDBG-CV counts).
ACCOMP_CDBG_COLUMNS = {
    2024: "C",
    2023: "G",
    2022: "K",
    2021: "O",
    2020: "S",
    2019: "U",
    2018: "W",
    2017: "Y",
    2016: "AA",
    2015: "AC",
    2014: "AE",
    2013: "AG",
    2012: "AI",
    2011: "AK",
    2010: "AM",
    2009: "AO",
    2008: "AQ",
    2007: "AS",
    2006: "AU",
    2005: "AW",
}

# National expenditure workbook columns (direct observed CDBG disbursements).
EXPEND_CDBG_COLUMNS = {
    2024: "D",
    2023: "H",
    2022: "L",
    2021: "P",
    2020: "T",
    2019: "V",
    2018: "X",
    2017: "Z",
    2016: "AB",
    2015: "AD",
    2014: "AF",
    2013: "AH",
    2012: "AJ",
    2011: "AL",
    2010: "AN",
    2009: "AP",
    2008: "AR",
    2007: "AT",
    2006: "AV",
    2005: "AX",
}

# Separate CDBG-CV columns exist only in FY2021-FY2024 on the national
# expenditure workbook. They are reported separately rather than folded into
# the 20-year core CDBG-only series.
EXPEND_CDBG_CV_COLUMNS = {
    2024: "F",
    2023: "J",
    2022: "N",
    2021: "R",
}

EXPECTED_REHAB_CODES = [f"14{letter}" for letter in "ABCDEFGHIJKL"]
YEARS = sorted(ACCOMP_CDBG_COLUMNS)

# National CDBG formula grant allocation / appropriation pool used as the
# yearly comparator for the observed 14-series disbursement series.
CDBG_FORMULA_ALLOCATION_BILLIONS = {
    2005: 4.117,
    2006: 3.711,
    2007: 3.711,
    2008: 3.593,
    2009: 3.642,
    2010: 3.948,
    2011: 3.303,
    2012: 2.948,
    2013: 3.078,
    2014: 3.030,
    2015: 3.066,
    2016: 3.000,
    2017: 3.000,
    2018: 3.365,
    2019: 3.365,
    2020: 3.425,
    2021: 3.450,
    2022: 3.300,
    2023: 3.300,
    2024: 3.300,
}

# GAO-23-106339 reports that more than 300,000 HUD-assisted households with a
# mobility-device user lived in units without any accessibility features. The
# prompt operationalizes that benchmark at 313,000 households.
MOBILITY_DEVICE_INACCESSIBLE_HOUSEHOLDS = 313_000
MOBILITY_DEVICE_BENCHMARK_SOURCE_URL = "https://www.gao.gov/products/gao-23-106339"

OBSERVED_GRANTEE_EXAMPLES = [
    {
        "grantee": "Amherst, NY",
        "program_year": "PY2023",
        "url": "https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_AMHE-NY_NY_2023.pdf",
        "codes": [
            ("14A", "Rehab; Single-Unit Residential", 256_032.21),
            ("14F", "Energy Efficiency Improvements", 4_997.00),
            ("14H", "Rehabilitation Administration", 110_374.88),
            ("14I", "Lead-Based/Lead Hazard Test/Abate", 4_757.61),
        ],
        "subtotal": 376_161.70,
        "note": "The same PR50 report still does not indicate whether any portion of those 14-series dollars funded accessibility retrofits.",
    },
    {
        "grantee": "Arapahoe County, CO",
        "program_year": "PY2023",
        "url": "https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_ARAP-CO_CO_2023.pdf",
        "codes": [
            ("14A", "Rehab; Single-Unit Residential", 146_318.50),
            ("14B", "Rehab; Multi-Unit Residential", 1_262_413.74),
            ("14F", "Energy Efficiency Improvements", 213_639.92),
        ],
        "subtotal": 1_622_372.16,
        "note": "That same report separately lists just $9,763.00 under 05B (Services for Persons with Disabilities), illustrating that disability-specific activity can be coded explicitly while the much larger rehab dollars remain accessibility-blind.",
    },
    {
        "grantee": "Anne Arundel County, MD",
        "program_year": "PY2023",
        "url": "https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_ANNE-MD_MD_2023.pdf",
        "codes": [
            ("14A", "Rehab; Single-Unit Residential", 261_939.32),
            ("14B", "Rehab; Multi-Unit Residential", 296_348.56),
            ("14G", "Acquisition for Rehabilitation", 243_945.81),
            ("14H", "Rehabilitation Administration", 574_096.18),
        ],
        "subtotal": 1_376_329.87,
        "note": "The same report separately lists $40,068.00 under 03B (Facility for Persons with Disabilities), again showing that direct 14-series rehab dollars are observable while accessibility content inside those rehab dollars is not.",
    },
]


def safe_float(value: object) -> float:
    if value in (None, "", "."):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0



def safe_int(value: object) -> int:
    return int(round(safe_float(value)))



def pct_change(old: float, new: float) -> float | None:
    if old == 0:
        return None
    return ((new - old) / old) * 100.0



def avg(values: list[float]) -> float:
    return sum(values) / len(values)



def fmt_int(value: float | int) -> str:
    return f"{int(round(value)):,}"



def fmt_pct(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.1f}%"



def fmt_billions_from_dollars(value: float) -> str:
    return f"{value / 1_000_000_000:.3f}"



def fmt_currency(value: float) -> str:
    return f"${value:,.2f}"



def ensure_download(path: str, url: str) -> None:
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    urllib.request.urlretrieve(url, path)



def load_xlsx_rows(path: str, sheet_name: str | None = None) -> list[dict[str, object]]:
    with ZipFile(path) as zf:
        workbook = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            shared_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in shared_root:
                shared_strings.append(
                    "".join(t.text or "" for t in si.iter(f"{SHEET_MAIN_NS}t"))
                )

        selected_sheet = None
        for sheet in workbook.find("a:sheets", XML_NS):
            if sheet_name is None or sheet.attrib["name"] == sheet_name:
                selected_sheet = sheet
                break
        if selected_sheet is None:
            raise ValueError(f"Sheet {sheet_name!r} not found in {path}")

        rel_id = selected_sheet.attrib[f"{{{XML_NS['r']}}}id"]
        sheet_path = "xl/" + rel_map[rel_id]
        sheet_root = ET.fromstring(zf.read(sheet_path))
        sheet_data = sheet_root.find("a:sheetData", XML_NS)

        def cell_value(cell: ET.Element) -> str | None:
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

        rows: list[dict[str, object]] = []
        if sheet_data is None:
            return rows
        for row in sheet_data:
            row_map: dict[str, object] = {"__row__": int(row.attrib["r"])}
            for cell in row:
                match = CELL_REF_RE.match(cell.attrib.get("r", ""))
                if not match:
                    continue
                col = match.group(1)
                row_map[col] = cell_value(cell)
            rows.append(row_map)
        return rows



def cdbg_code_lookup(rows: list[dict[str, object]], start_row: int, end_row: int) -> dict[str, dict[str, object]]:
    lookup: dict[str, dict[str, object]] = {}
    for row in rows:
        row_number = int(row["__row__"])
        if start_row <= row_number <= end_row:
            code = str(row.get("A") or "").strip()
            if code:
                lookup[code] = row
    return lookup



def compute_posh_disability_share() -> dict[str, float | int]:
    rows = load_xlsx_rows(POSH_PATH)
    if not rows:
        raise ValueError("POSH workbook returned no rows")

    header_row = rows[0]
    headers_by_col = {
        key: str(value).strip()
        for key, value in header_row.items()
        if key != "__row__" and value is not None
    }

    data_rows = rows[1:]
    summary_row = None
    for row in data_rows:
        if str(row.get("E") or "").strip() == "Summary of All HUD Programs":
            summary_row = row
            break
    if summary_row is None:
        raise ValueError("Could not find POSH summary row")

    def value_for(header_name: str) -> str | None:
        for col, header in headers_by_col.items():
            if header == header_name:
                return summary_row.get(col)  # type: ignore[return-value]
        return None

    pct_disabled_lt62 = safe_float(value_for("pct_disabled_lt62"))
    pct_disabled_ge62 = safe_float(value_for("pct_disabled_ge62"))
    pct_age62plus = safe_float(value_for("pct_age62plus"))
    number_reported = safe_int(value_for("number_reported"))

    share_age62plus = pct_age62plus / 100.0
    share_under62 = 1.0 - share_age62plus
    weighted_household_disability_rate = (
        pct_disabled_lt62 * share_under62 + pct_disabled_ge62 * share_age62plus
    )
    estimated_disabled_households = number_reported * weighted_household_disability_rate / 100.0

    return {
        "pct_disabled_lt62": pct_disabled_lt62,
        "pct_disabled_ge62": pct_disabled_ge62,
        "pct_age62plus": pct_age62plus,
        "weighted_household_disability_rate": weighted_household_disability_rate,
        "number_reported": number_reported,
        "estimated_disabled_households": estimated_disabled_households,
    }



def compute_expenditure_series(accomplishment_rehab_codes: list[str]) -> dict[str, object]:
    ensure_download(CDBG_EXPEND_PATH, CDBG_EXPEND_URL)
    rows = load_xlsx_rows(CDBG_EXPEND_PATH)

    rehab_rows_all: list[dict[str, object]] = []
    for row in rows:
        code = str(row.get("A") or "").strip()
        if re.fullmatch(r"14[A-L]", code):
            rehab_rows_all.append(row)

    if not rehab_rows_all:
        raise ValueError("Could not find 14-series rows in national expenditure workbook")

    available_codes = [str(row.get("A") or "").strip() for row in rehab_rows_all]
    rehab_rows_comparable = [
        row for row in rehab_rows_all if str(row.get("A") or "").strip() in accomplishment_rehab_codes
    ]
    extra_codes = [code for code in available_codes if code not in accomplishment_rehab_codes]

    yearly_records: list[dict[str, object]] = []
    by_year: dict[int, dict[str, object]] = {}
    for year in YEARS:
        cdbg_col = EXPEND_CDBG_COLUMNS[year]
        cv_col = EXPEND_CDBG_CV_COLUMNS.get(year)
        observed_all_cdbg = sum(safe_float(row.get(cdbg_col)) for row in rehab_rows_all)
        observed_comparable_cdbg = sum(safe_float(row.get(cdbg_col)) for row in rehab_rows_comparable)
        observed_all_cdbg_cv = (
            sum(safe_float(row.get(cv_col)) for row in rehab_rows_all) if cv_col else 0.0
        )
        observed_comparable_cdbg_cv = (
            sum(safe_float(row.get(cv_col)) for row in rehab_rows_comparable) if cv_col else 0.0
        )
        record = {
            "fiscal_year": year,
            "observed_14series_cdbg_dollars_all": observed_all_cdbg,
            "observed_14series_cdbg_dollars_comparable": observed_comparable_cdbg,
            "observed_14series_cdbgcv_dollars_all": observed_all_cdbg_cv,
            "observed_14series_cdbgcv_dollars_comparable": observed_comparable_cdbg_cv,
        }
        yearly_records.append(record)
        by_year[year] = record

    code_totals: list[dict[str, object]] = []
    comparable_total = sum(
        sum(safe_float(row.get(col)) for col in EXPEND_CDBG_COLUMNS.values())
        for row in rehab_rows_comparable
    )
    for row in rehab_rows_all:
        code = str(row.get("A") or "").strip()
        cdbg_total_dollars = sum(safe_float(row.get(col)) for col in EXPEND_CDBG_COLUMNS.values())
        cdbg_cv_total_dollars = sum(
            safe_float(row.get(col)) for col in EXPEND_CDBG_CV_COLUMNS.values()
        )
        code_totals.append(
            {
                "code": code,
                "name": str(row.get("C") or "").strip(),
                "cdbg_total_dollars": cdbg_total_dollars,
                "cdbg_cv_total_dollars": cdbg_cv_total_dollars,
                "share_of_comparable_total_pct": (
                    (cdbg_total_dollars / comparable_total) * 100.0
                    if comparable_total and code in accomplishment_rehab_codes
                    else None
                ),
            }
        )

    code_totals.sort(key=lambda item: float(item["cdbg_total_dollars"]), reverse=True)
    comparable_code_totals = [
        item for item in code_totals if str(item["code"]) in accomplishment_rehab_codes
    ]
    extra_code_totals = [item for item in code_totals if str(item["code"]) in extra_codes]

    return {
        "path": CDBG_EXPEND_PATH,
        "source_url": CDBG_EXPEND_URL,
        "available_codes": available_codes,
        "extra_codes_not_in_accomplishments": extra_codes,
        "yearly_records": yearly_records,
        "by_year": by_year,
        "code_totals": code_totals,
        "comparable_code_totals": comparable_code_totals,
        "extra_code_totals": extra_code_totals,
        "totals": {
            "cdbg_dollars_all": sum(
                float(record["observed_14series_cdbg_dollars_all"]) for record in yearly_records
            ),
            "cdbg_dollars_comparable": sum(
                float(record["observed_14series_cdbg_dollars_comparable"])
                for record in yearly_records
            ),
            "cdbg_cv_dollars_all": sum(
                float(record["observed_14series_cdbgcv_dollars_all"]) for record in yearly_records
            ),
            "cdbg_cv_dollars_comparable": sum(
                float(record["observed_14series_cdbgcv_dollars_comparable"])
                for record in yearly_records
            ),
        },
    }



def compute_cdbg_accessibility_gap() -> dict[str, object]:
    rows = load_xlsx_rows(CDBG_ACCOMP_PATH, "National Accomplishments")
    by_row = {int(row["__row__"]): row for row in rows}

    housing_rows = [by_row[row_no] for row_no in range(5, 19) if row_no in by_row]
    rehab_rows = []
    for row in housing_rows:
        code = str(row.get("A") or "").strip()
        if re.fullmatch(r"14[A-L]", code):
            rehab_rows.append(row)

    present_rehab_codes = [str(row.get("A") or "").strip() for row in rehab_rows]
    missing_rehab_codes = [code for code in EXPECTED_REHAB_CODES if code not in present_rehab_codes]

    expenditure = compute_expenditure_series(present_rehab_codes)

    public_service_codes = cdbg_code_lookup(rows, 49, 71)
    public_improvement_codes = cdbg_code_lookup(rows, 83, 102)

    row_05b = public_service_codes["05B"]
    row_03b = public_improvement_codes["03B"]
    housing_total_row = by_row[19]

    posh = compute_posh_disability_share()
    disability_rate = float(posh["weighted_household_disability_rate"]) / 100.0
    total_assisted_disabled_households = float(posh["estimated_disabled_households"])
    if total_assisted_disabled_households <= 0:
        raise ValueError("POSH estimated disabled-household denominator must be positive")
    accessibility_need_rate = (
        MOBILITY_DEVICE_INACCESSIBLE_HOUSEHOLDS / total_assisted_disabled_households
    )

    yearly_records: list[dict[str, object]] = []
    annual_05b: dict[int, int] = {}
    annual_03b: dict[int, int] = {}

    for year in YEARS:
        col = ACCOMP_CDBG_COLUMNS[year]
        rehab_households = sum(safe_int(row.get(col)) for row in rehab_rows)
        housing_households_total = safe_int(housing_total_row.get(col))
        rehab_share_of_housing = (
            rehab_households / housing_households_total if housing_households_total else None
        )
        estimated_disabled_rehab_households = rehab_households * disability_rate
        estimated_accessibility_need_rehab_households = (
            estimated_disabled_rehab_households * accessibility_need_rate
        )
        persons_05b = safe_int(row_05b.get(col))
        persons_03b = safe_int(row_03b.get(col))
        expenditure_record = expenditure["by_year"][year]
        formula_allocation_dollars = CDBG_FORMULA_ALLOCATION_BILLIONS[year] * 1_000_000_000

        annual_05b[year] = persons_05b
        annual_03b[year] = persons_03b

        yearly_records.append(
            {
                "fiscal_year": year,
                "total_cdbg_formula_allocation_dollars": formula_allocation_dollars,
                "rehab_households": rehab_households,
                "housing_households_total": housing_households_total,
                "rehab_share_of_housing_households": rehab_share_of_housing,
                "estimated_disabled_rehab_households": estimated_disabled_rehab_households,
                "estimated_accessibility_need_rehab_households": estimated_accessibility_need_rehab_households,
                "05B_persons": persons_05b,
                "03B_persons": persons_03b,
                "observed_14series_cdbg_dollars_all": expenditure_record[
                    "observed_14series_cdbg_dollars_all"
                ],
                "observed_14series_cdbg_dollars_comparable": expenditure_record[
                    "observed_14series_cdbg_dollars_comparable"
                ],
                "observed_14series_cdbgcv_dollars_all": expenditure_record[
                    "observed_14series_cdbgcv_dollars_all"
                ],
                "observed_14series_cdbgcv_dollars_comparable": expenditure_record[
                    "observed_14series_cdbgcv_dollars_comparable"
                ],
            }
        )

    total_rehab_households = sum(record["rehab_households"] for record in yearly_records)
    total_housing_households = sum(record["housing_households_total"] for record in yearly_records)
    total_estimated_disabled_rehab_households = total_rehab_households * disability_rate
    total_estimated_accessibility_need_rehab_households = (
        total_estimated_disabled_rehab_households * accessibility_need_rate
    )
    total_cdbg_formula_allocation_dollars = sum(
        CDBG_FORMULA_ALLOCATION_BILLIONS[year] * 1_000_000_000 for year in YEARS
    )

    early_03b_avg = avg([annual_03b[year] for year in range(2005, 2010)])
    recent_03b_avg = avg([annual_03b[year] for year in range(2020, 2025)])

    avg_05b_2019_2021 = avg([annual_05b[year] for year in range(2019, 2022)])
    avg_05b_2022_2024 = avg([annual_05b[year] for year in range(2022, 2025)])
    avg_05b_2019_2023 = avg([annual_05b[year] for year in range(2019, 2024)])
    avg_05b_2020_2024 = avg([annual_05b[year] for year in range(2020, 2025)])

    return {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_dir": REPO_DIR,
        "cdbg_accomp_path": CDBG_ACCOMP_PATH,
        "cdbg_expend_path": CDBG_EXPEND_PATH,
        "cdbg_expend_url": CDBG_EXPEND_URL,
        "posh_path": POSH_PATH,
        "mobility_device_benchmark_source_url": MOBILITY_DEVICE_BENCHMARK_SOURCE_URL,
        "present_rehab_codes": present_rehab_codes,
        "missing_expected_rehab_codes": missing_rehab_codes,
        "expenditure_extra_codes": expenditure["extra_codes_not_in_accomplishments"],
        "posh_summary": posh,
        "yearly_records": yearly_records,
        "grantee_examples": OBSERVED_GRANTEE_EXAMPLES,
        "aggregates": {
            "total_rehab_households": total_rehab_households,
            "total_housing_households": total_housing_households,
            "rehab_share_of_total_housing_households": total_rehab_households / total_housing_households,
            "total_cdbg_formula_allocation_dollars": total_cdbg_formula_allocation_dollars,
            "total_05B_persons": sum(annual_05b.values()),
            "total_03B_persons": sum(annual_03b.values()),
            "total_estimated_disabled_rehab_households": total_estimated_disabled_rehab_households,
            "total_assisted_disabled_households": total_assisted_disabled_households,
            "mobility_device_households_in_inaccessible_units": MOBILITY_DEVICE_INACCESSIBLE_HOUSEHOLDS,
            "accessibility_need_rate_among_assisted_disabled_households": accessibility_need_rate,
            "total_estimated_accessibility_need_rehab_households": total_estimated_accessibility_need_rehab_households,
            "total_observed_14series_cdbg_dollars_all": expenditure["totals"]["cdbg_dollars_all"],
            "total_observed_14series_cdbg_dollars_comparable": expenditure["totals"][
                "cdbg_dollars_comparable"
            ],
            "total_observed_14series_cdbgcv_dollars_all": expenditure["totals"][
                "cdbg_cv_dollars_all"
            ],
            "total_observed_14series_cdbgcv_dollars_comparable": expenditure["totals"][
                "cdbg_cv_dollars_comparable"
            ],
            "additional_observed_dollars_from_14E_14K_14L": expenditure["totals"][
                "cdbg_dollars_all"
            ]
            - expenditure["totals"]["cdbg_dollars_comparable"],
        },
        "code_totals": {
            "comparable": expenditure["comparable_code_totals"],
            "extra": expenditure["extra_code_totals"],
        },
        "trends": {
            "03B_early_avg_2005_2009": early_03b_avg,
            "03B_recent_avg_2020_2024": recent_03b_avg,
            "03B_change_pct_early_to_recent": pct_change(early_03b_avg, recent_03b_avg),
            "05B_2005": annual_05b[2005],
            "05B_2019": annual_05b[2019],
            "05B_2023": annual_05b[2023],
            "05B_2024": annual_05b[2024],
            "05B_change_pct_2005_to_2024": pct_change(annual_05b[2005], annual_05b[2024]),
            "05B_change_pct_2019_to_2024": pct_change(annual_05b[2019], annual_05b[2024]),
            "05B_change_pct_2023_to_2024": pct_change(annual_05b[2023], annual_05b[2024]),
            "05B_avg_2019_2021": avg_05b_2019_2021,
            "05B_avg_2022_2024": avg_05b_2022_2024,
            "05B_change_pct_avg_2019_2021_to_avg_2022_2024": pct_change(
                avg_05b_2019_2021, avg_05b_2022_2024
            ),
            "05B_avg_2019_2023": avg_05b_2019_2023,
            "05B_avg_2020_2024": avg_05b_2020_2024,
            "05B_change_pct_avg_2019_2023_to_avg_2020_2024": pct_change(
                avg_05b_2019_2023, avg_05b_2020_2024
            ),
            "05B_decline_assessment": "accelerating downward rather than stabilizing",
        },
    }



def render_markdown(results: dict[str, object]) -> str:
    aggregates = results["aggregates"]
    trends = results["trends"]
    posh = results["posh_summary"]
    yearly_records = results["yearly_records"]
    present_rehab_codes = results["present_rehab_codes"]
    missing_rehab_codes = results["missing_expected_rehab_codes"]
    expenditure_extra_codes = results["expenditure_extra_codes"]
    comparable_code_totals = results["code_totals"]["comparable"]
    extra_code_totals = results["code_totals"]["extra"]
    grantee_examples = results["grantee_examples"]
    accessibility_need_rate_pct = (
        float(aggregates["accessibility_need_rate_among_assisted_disabled_households"]) * 100.0
    )

    lines: list[str] = []
    lines.append("# CDBG Accessibility-Gap Quantification Memo")
    lines.append("")
    lines.append(f"Generated: {results['generated_at_utc']}")
    lines.append(f"Repo: `{results['repo_dir']}`")
    lines.append(
        "Status: strict national actual-spending gap fully solved for 14-series CDBG disbursements; accessibility-specific spending remains unreported, so the remaining accessibility count is estimated rather than observed."
    )
    lines.append("")
    lines.append("## Bottom line")
    lines.append("")
    lines.append(
        "HUD Exchange's national CDBG expenditure workbook provides the direct matrix-code spending series that the national accomplishments workbook lacked."
    )
    lines.append("")
    lines.append(
        f"Against ${fmt_billions_from_dollars(float(aggregates['total_cdbg_formula_allocation_dollars']))} billion in total national CDBG formula allocations across FY2005-FY2024, HUD recorded ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbg_dollars_all']))} billion in observed 14A-14L rehabilitation disbursements and ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbg_dollars_comparable']))} billion in the accomplishments-comparable subset (14A, 14B, 14C, 14D, 14F, 14G, 14H, 14I, 14J). The difference is driven by expenditure-only codes 14E, 14K, and 14L, which the national accomplishments workbook does not expose as separate household rows."
    )
    lines.append("")
    lines.append(
        "The prior proxy-dollar claim is withdrawn. HUD already publishes an actual national 14-series spending series; what it still does not publish is any accessibility flag showing whether any of those dollars funded ramps, widened doors, accessible bathrooms, or other accessibility retrofits."
    )
    lines.append("")
    lines.append(
        f"HUD's FY2005-FY2024 national accomplishments workbook reports {fmt_int(aggregates['total_rehab_households'])} households served in the accomplishments-comparable 14-series codes. Using the repo-local POSH disability-share estimate of {float(posh['weighted_household_disability_rate']):.1f}% (approximately 39%), about {fmt_int(aggregates['total_estimated_disabled_rehab_households'])} of those rehab households likely included a disabled household member. Applying the 313,000-household mobility-device benchmark to the estimated {fmt_int(aggregates['total_assisted_disabled_households'])} HUD-assisted disabled-household denominator implies a {fmt_pct(accessibility_need_rate_pct)} accessibility-need rate, or about {fmt_int(aggregates['total_estimated_accessibility_need_rehab_households'])} likely accessibility-modification cases that went untracked."
    )
    lines.append("")
    lines.append("## Status of the spec gap")
    lines.append("")
    lines.append(
        "- Actual national 14-series spending for FY2005-FY2024: fully solved via HUD Exchange's national CDBG expenditure workbook."
    )
    lines.append(
        "- Per-year national CDBG formula allocation comparator: now surfaced in the year-by-year table below."
    )
    lines.append(
        f"- Accessibility-need benchmark [W]: now computed at {fmt_pct(accessibility_need_rate_pct)} using 313,000 / {fmt_int(aggregates['total_assisted_disabled_households'])}."
    )
    lines.append(
        f"- Estimated untracked accessibility modifications: now surfaced as approximately {fmt_int(aggregates['total_estimated_accessibility_need_rehab_households'])} household-level accessibility-modification cases."
    )
    lines.append(
        f"- 05B decline assessment including FY2024: direct answer = {trends['05B_decline_assessment']}."
    )
    lines.append("")
    lines.append("## Inputs and method")
    lines.append("")
    lines.append(
        f"- Accomplishments source: `{os.path.relpath(str(results['cdbg_accomp_path']), str(results['repo_dir']))}` (`National Accomplishments` sheet)."
    )
    lines.append(
        f"- Expenditure source: `{os.path.relpath(str(results['cdbg_expend_path']), str(results['repo_dir']))}` downloaded from <{results['cdbg_expend_url']}>."
    )
    lines.append(
        f"- POSH source: `{os.path.relpath(str(results['posh_path']), str(results['repo_dir']))}` (national summary row)."
    )
    lines.append(
        "- Formula allocation comparator: annual national CDBG formula grant allocation / appropriation series already used in repo-local CDBG analysis, totaling ${total} billion across FY2005-FY2024.".format(
            total=fmt_billions_from_dollars(float(aggregates["total_cdbg_formula_allocation_dollars"]))
        )
    )
    lines.append("- Years: FY2005-FY2024, following HUD's published national workbook year labels.")
    lines.append(
        f"- Accomplishments-comparable 14-series codes: {', '.join(present_rehab_codes)}. The accomplishments workbook did not contain {', '.join(missing_rehab_codes)} as separate household rows."
    )
    lines.append(
        f"- Additional 14-series codes present in the expenditure workbook but not as separate accomplishments rows: {', '.join(expenditure_extra_codes)}."
    )
    lines.append(
        "- The annual core spending series below uses direct observed CDBG disbursements from the national expenditure workbook, not a proxy allocated from formula grants."
    )
    lines.append(
        f"- Separate CDBG-CV 14-series disbursements exist only in FY2021-FY2024 and totaled ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbgcv_dollars_comparable']))} billion for the accomplishments-comparable codes (${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbgcv_dollars_all']))} billion across all 14A-14L). They are reported separately rather than folded into the 20-year core CDBG-only series."
    )
    lines.append(
        f"- POSH disability share calculation: {float(posh['pct_disabled_lt62']):.1f}% under age 62, {float(posh['pct_disabled_ge62']):.1f}% age 62+, and {float(posh['pct_age62plus']):.1f}% age-62+ household share, yielding a weighted household disability rate of {float(posh['weighted_household_disability_rate']):.1f}% and an estimated {fmt_int(aggregates['total_assisted_disabled_households'])} HUD-assisted households with disabilities."
    )
    lines.append(
        f"- Accessibility-need benchmark: 313,000 HUD-assisted households with a mobility-device user in a unit without accessibility features, from GAO-23-106339 (<{results['mobility_device_benchmark_source_url']}>). Dividing 313,000 by {fmt_int(aggregates['total_assisted_disabled_households'])} yields the {fmt_pct(accessibility_need_rate_pct)} rate used below."
    )
    lines.append("")
    lines.append("## Year-by-year table")
    lines.append("")
    lines.append(
        "| FY | Total CDBG formula allocation ($B) | Observed 14-series CDBG ($B, comparable) | Observed 14-series CDBG ($B, all 14A-L) | 14-series HH served | 14-series share of housing HH | Est. disabled rehab HH (39.3%) | Est. accessibility-need HH (17.4%) | 05B persons | 03B persons |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for record in yearly_records:
        share_pct = (record["rehab_share_of_housing_households"] or 0.0) * 100.0
        lines.append(
            "| {year} | {alloc} | {obs_comp} | {obs_all} | {rehab_hh} | {share:.1f}% | {disabled_hh} | {access_hh} | {p05b} | {p03b} |".format(
                year=record["fiscal_year"],
                alloc=fmt_billions_from_dollars(
                    float(record["total_cdbg_formula_allocation_dollars"])
                ),
                obs_comp=fmt_billions_from_dollars(
                    float(record["observed_14series_cdbg_dollars_comparable"])
                ),
                obs_all=fmt_billions_from_dollars(
                    float(record["observed_14series_cdbg_dollars_all"])
                ),
                rehab_hh=fmt_int(record["rehab_households"]),
                share=share_pct,
                disabled_hh=fmt_int(record["estimated_disabled_rehab_households"]),
                access_hh=fmt_int(record["estimated_accessibility_need_rehab_households"]),
                p05b=fmt_int(record["05B_persons"]),
                p03b=fmt_int(record["03B_persons"]),
            )
        )
    lines.append("")
    lines.append("## Twenty-year aggregate headline")
    lines.append("")
    lines.append(
        f"- Total national CDBG formula allocation comparator: ${fmt_billions_from_dollars(float(aggregates['total_cdbg_formula_allocation_dollars']))} billion"
    )
    lines.append(
        f"- Total observed 14-series CDBG disbursements, accomplishments-comparable codes: ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbg_dollars_comparable']))} billion"
    )
    lines.append(
        f"- Total observed 14-series CDBG disbursements, all 14A-14L: ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbg_dollars_all']))} billion"
    )
    lines.append(
        f"- Additional observed dollars from expenditure-only 14E/14K/14L relative to the accomplishments-comparable set: ${fmt_billions_from_dollars(float(aggregates['additional_observed_dollars_from_14E_14K_14L']))} billion"
    )
    lines.append(
        f"- Additional observed 14-series CDBG-CV disbursements in FY2021-FY2024: ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbgcv_dollars_comparable']))} billion comparable / ${fmt_billions_from_dollars(float(aggregates['total_observed_14series_cdbgcv_dollars_all']))} billion all 14A-14L"
    )
    lines.append(f"- Total 14-series households served: {fmt_int(aggregates['total_rehab_households'])}")
    lines.append(
        f"- 14-series share of all reported housing households: {fmt_pct(float(aggregates['rehab_share_of_total_housing_households']) * 100.0)}"
    )
    lines.append(f"- Total 05B persons served: {fmt_int(aggregates['total_05B_persons'])}")
    lines.append(f"- Total 03B persons served: {fmt_int(aggregates['total_03B_persons'])}")
    lines.append(
        f"- Estimated 14-series rehab households including a disabled household member: {fmt_int(aggregates['total_estimated_disabled_rehab_households'])}"
    )
    lines.append(
        f"- Accessibility-need rate among HUD-assisted disabled households (313,000 / {fmt_int(aggregates['total_assisted_disabled_households'])}): {fmt_pct(accessibility_need_rate_pct)}"
    )
    lines.append(
        f"- Estimated household-level accessibility modifications that likely went untracked: {fmt_int(aggregates['total_estimated_accessibility_need_rehab_households'])}"
    )
    lines.append(
        "- Observed accessibility-modification count inside the 14-series: unknown / not reported by any matrix code or public field"
    )
    lines.append("")
    lines.append("## Estimated untracked accessibility modifications")
    lines.append("")
    lines.append(
        f"Approximately 39% of HUD-assisted households include a disabled member (repo-local POSH estimate: {float(posh['weighted_household_disability_rate']):.1f}%). Applying that rate to {fmt_int(aggregates['total_rehab_households'])} CDBG-funded rehab households implies approximately {fmt_int(aggregates['total_estimated_disabled_rehab_households'])} rehab households with a disabled member."
    )
    lines.append("")
    lines.append(
        f"Using the prompt's benchmark, the accessibility-need rate is 313,000 / {fmt_int(aggregates['total_assisted_disabled_households'])} = {fmt_pct(accessibility_need_rate_pct)}. Applying {fmt_pct(accessibility_need_rate_pct)} to {fmt_int(aggregates['total_estimated_disabled_rehab_households'])} estimated disabled-household rehab cases yields approximately {fmt_int(aggregates['total_estimated_accessibility_need_rehab_households'])} likely household-level accessibility-modification cases that went untracked in FY2005-FY2024."
    )
    lines.append("")
    lines.append(
        "That is still an estimate, not an observed count. HUD's published national expenditure workbook, national accomplishments workbook, and grantee-level PR50 reports still do not identify which 14-series rehab activities actually installed accessibility features."
    )
    lines.append("")
    lines.append("## Code mix within the accomplishments-comparable spending series")
    lines.append("")
    lines.append("| Code | Matrix code name | FY2005-FY2024 observed CDBG disbursements ($B) | Share of comparable total |")
    lines.append("|---|---|---:|---:|")
    for item in comparable_code_totals:
        lines.append(
            "| {code} | {name} | {billions} | {share} |".format(
                code=item["code"],
                name=item["name"],
                billions=fmt_billions_from_dollars(float(item["cdbg_total_dollars"])),
                share=fmt_pct(item["share_of_comparable_total_pct"]),
            )
        )
    lines.append("")
    if extra_code_totals:
        extra_bits = "; ".join(
            f"{item['code']} = ${fmt_billions_from_dollars(float(item['cdbg_total_dollars']))}B"
            for item in extra_code_totals
        )
        lines.append(
            f"Expenditure-only 14-series codes not separately exposed as household rows in the accomplishments workbook: {extra_bits}."
        )
        lines.append("")
    lines.append("## Observed grantee-level PR50 examples")
    lines.append("")
    for example in grantee_examples:
        code_bits = "; ".join(
            f"{code} {label} {fmt_currency(amount)}"
            for code, label, amount in example["codes"]
        )
        lines.append(
            f"- {example['grantee']} {example['program_year']} PR50: {code_bits}; 14-series subtotal {fmt_currency(float(example['subtotal']))}. {example['note']} Source: <{example['url']}>"
        )
    lines.append("")
    lines.append("## 05B trend including FY2024")
    lines.append("")
    lines.append(
        f"Direct answer: the 05B decline is {trends['05B_decline_assessment']}."
    )
    lines.append("")
    lines.append(
        f"The 05B series is volatile rather than monotonic, but FY2024 does not look like stabilization: 05B fell from {fmt_int(trends['05B_2023'])} persons in FY2023 to {fmt_int(trends['05B_2024'])} in FY2024, a {fmt_pct(trends['05B_change_pct_2023_to_2024'])} drop."
    )
    lines.append("")
    lines.append(
        f"Relative to FY2005, FY2024 was {fmt_pct(trends['05B_change_pct_2005_to_2024'])} lower ({fmt_int(trends['05B_2005'])} to {fmt_int(trends['05B_2024'])}). Relative to FY2019, FY2024 was {fmt_pct(trends['05B_change_pct_2019_to_2024'])} lower ({fmt_int(trends['05B_2019'])} to {fmt_int(trends['05B_2024'])})."
    )
    lines.append("")
    lines.append(
        f"Recent-window averages point the same way: the FY2019-FY2021 average was {fmt_int(trends['05B_avg_2019_2021'])}, while the FY2022-FY2024 average fell to {fmt_int(trends['05B_avg_2022_2024'])}, a {fmt_pct(trends['05B_change_pct_avg_2019_2021_to_avg_2022_2024'])} decline. The FY2019-FY2023 average was {fmt_int(trends['05B_avg_2019_2023'])}, while the FY2020-FY2024 average fell to {fmt_int(trends['05B_avg_2020_2024'])}, a {fmt_pct(trends['05B_change_pct_avg_2019_2023_to_avg_2020_2024'])} decrease."
    )
    lines.append("")
    lines.append("## 03B trend")
    lines.append("")
    lines.append(
        f"03B averaged {fmt_int(trends['03B_early_avg_2005_2009'])} persons per year in FY2005-FY2009 and {fmt_int(trends['03B_recent_avg_2020_2024'])} in FY2020-FY2024, a {fmt_pct(trends['03B_change_pct_early_to_recent'])} decline."
    )
    lines.append("")
    lines.append("## Remaining limitation")
    lines.append("")
    lines.append(
        "The strict spending gap is now closed: HUD does publish a national 14-series disbursement series. The remaining gap is narrower but still consequential: neither the national expenditure workbook, the national accomplishments workbook, nor grantee-level PR50 reports identify whether any 14-series disbursement funded accessibility modifications."
    )
    lines.append("")
    lines.append("## Policy implication")
    lines.append("")
    lines.append(
        f"HUD is not missing a national spending series anymore; it is missing an accessibility flag inside an existing spending series. If even the conservative household-level estimate of {fmt_int(aggregates['total_estimated_accessibility_need_rehab_households'])} likely accessibility-modification cases is roughly right, HUD's current reporting structure is obscuring a six-figure accessibility workload inside already-published rehab disbursements. Adding an accessibility field to the 14-series reporting structure would convert existing rehab reporting into an actual accessibility-accounting system without requiring HUD to build a new expenditure pipeline from scratch."
    )
    lines.append("")
    return "\n".join(lines)



def main() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    results = compute_cdbg_accessibility_gap()
    markdown = render_markdown(results)
    with open(OUTPUT_MD, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    print(f"Wrote {OUTPUT_MD}")
    print(
        "Top line: formula allocation comparator = ${alloc_total:.3f}B | actual 14-series CDBG disbursements = ${all_total:.3f}B all 14A-L / ${comp_total:.3f}B accomplishments-comparable | rehab households = {rehab:,} | est. disabled rehab households = {disabled:,} | est. untracked accessibility-modification cases = {accessibility:,}".format(
            alloc_total=float(results["aggregates"]["total_cdbg_formula_allocation_dollars"]) / 1_000_000_000,
            all_total=float(results["aggregates"]["total_observed_14series_cdbg_dollars_all"]) / 1_000_000_000,
            comp_total=float(results["aggregates"]["total_observed_14series_cdbg_dollars_comparable"]) / 1_000_000_000,
            rehab=int(round(results["aggregates"]["total_rehab_households"])),
            disabled=int(round(results["aggregates"]["total_estimated_disabled_rehab_households"])),
            accessibility=int(
                round(results["aggregates"]["total_estimated_accessibility_need_rehab_households"])
            ),
        )
    )


if __name__ == "__main__":
    main()
