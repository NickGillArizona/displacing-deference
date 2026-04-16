#!/usr/bin/env python3
"""
Analyze accessibility-related content in the 2023 AHS national PUF and compare the
remaining comparable measures to 2011 and 2019.

Outputs:
- results/ahs_2023_accessibility_results.json
- results/ahs_2023_accessibility_analysis.md

Notes:
- 2023 does not include the dedicated Home Accessibility topical module that appeared
  in 2019. The script therefore distinguishes between:
  (1) directly comparable core measures that remain in 2011/2019/2023, chiefly
      no-step entry (NOSTEP); and
  (2) module-specific measures that cannot be carried forward to 2023.
- The script uses published 2011 HUD report figures for the canonical Bo'sher
  three-tier framework and also reports a public-PUF reconstruction attempt for 2011.
"""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.request import urlretrieve

import pandas as pd


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
DATA_DIR = REPO_DIR / "data" / "ahs_accessibility"
RAW_DIR = DATA_DIR / "raw"
RESULTS_DIR = REPO_DIR / "results"

OUTPUT_JSON = RESULTS_DIR / "ahs_2023_accessibility_results.json"
OUTPUT_MD = RESULTS_DIR / "ahs_2023_accessibility_analysis.md"

SOURCE_URLS = {
    "2023_flat_csv": "https://www2.census.gov/programs-surveys/ahs/2023/AHS%202023%20National%20PUF%20v1.1%20Flat%20CSV.zip",
    "2019_flat_csv": "https://www2.census.gov/programs-surveys/ahs/2019/AHS%202019%20National%20PUF%20v1.1%20Flat%20CSV.zip",
    "2011_flat_csv": "https://www2.census.gov/programs-surveys/ahs/2011/AHS%202011%20National%20PUF%20v3.0%20Flat%20CSV.zip",
    "2023_value_labels": "https://www2.census.gov/programs-surveys/ahs/2023/AHS%202023%20Value%20Labels%20Package.zip",
    "2019_value_labels": "https://www2.census.gov/programs-surveys/ahs/2019/AHS%202019%20Value%20Labels%20Package.zip",
    "2011_value_labels": "https://www2.census.gov/programs-surveys/ahs/2011/AHS%202011%20National%20Value%20Labels%20Package.zip",
    "2023_table_specs": "https://www2.census.gov/programs-surveys/ahs/2023/AHS%202023%20Table%20Specifications%20and%20PUF%20Estimates%20for%20User%20Verification.xlsx",
    "2019_table_specs": "https://www2.census.gov/programs-surveys/ahs/2019/2019%20AHS%20Table%20Specifications%20and%20PUF%20Estimates%20for%20User%20Verification.xlsx",
    "2011_table_specs": "https://www2.census.gov/programs-surveys/ahs/2011/AHS_%202011_Table_Specs.xls",
    "2011_hud_report": "https://www.huduser.gov/portal/sites/default/files/pdf/accessibility-america-housingStock.pdf",
    "2015_2023_puf_guide": "https://www.census.gov/content/dam/Census/programs-surveys/ahs/tech-documentation/2015/Getting%20Started%20with%20the%20AHS%20PUF%202015%20and%20Beyond.pdf",
}

RAW_FILES = {
    "2023_flat_csv": RAW_DIR / "AHS 2023 National PUF v1.1 Flat CSV.zip",
    "2019_flat_csv": RAW_DIR / "AHS 2019 National PUF v1.1 Flat CSV.zip",
    "2011_flat_csv": RAW_DIR / "AHS 2011 National PUF v3.0 Flat CSV.zip",
    "2023_value_labels": RAW_DIR / "AHS 2023 Value Labels Package.zip",
    "2019_value_labels": RAW_DIR / "AHS 2019 Value Labels Package.zip",
    "2011_value_labels": RAW_DIR / "AHS 2011 National Value Labels Package.zip",
    "2023_table_specs": RAW_DIR / "AHS 2023 Table Specifications and PUF Estimates for User Verification.xlsx",
    "2019_table_specs": RAW_DIR / "2019 AHS Table Specifications and PUF Estimates for User Verification.xlsx",
    "2011_table_specs": RAW_DIR / "AHS_ 2011_Table_Specs.xls",
    "2011_hud_report": RAW_DIR / "accessibility-america-housingStock.pdf",
    "2015_2023_puf_guide": RAW_DIR / "Getting Started with the AHS PUF 2015 and Beyond.pdf",
}

PUBLISHED_2011_BOSHER = {
    "all_housing_units": {
        "level_1_potentially_modifiable_share": 0.3334,
        "level_2_livable_share": 0.0376,
        "level_3_wheelchair_accessible_share": 0.0015,
    },
    "housing_units_with_resident_wheelchair_user": {
        "level_1_potentially_modifiable_share": 0.4420,
        "level_2_livable_share": 0.1240,
        "level_3_wheelchair_accessible_share": 0.0073,
    },
    "source": "HUD PD&R, Accessibility of America's Housing Stock: Analysis of the 2011 American Housing Survey (2015), executive summary and Table 7.",
}

VARIABLE_INVENTORY_2023 = [
    {
        "variable": "NOSTEP",
        "description": "Whether use of steps is not required to enter the building/home from outside.",
        "source": "2023 AHS Table Specifications, Housing Unit Characteristics and General Housing tables.",
        "weight": "WEIGHT",
        "comparability": "Directly comparable core item in 2011 and 2019.",
    },
    {
        "variable": "HMRACCESS",
        "description": "Whether an owner-occupied unit's home improvement activity in the last two years was done for accessibility for elderly or disabled residents.",
        "source": "2023 AHS Table Specifications, Home Improvement table.",
        "weight": "WEIGHT",
        "comparability": "Available in 2019, not available in 2011.",
    },
    {
        "variable": "DISHH",
        "description": "Whether at least one disabled person lives in the unit.",
        "source": "2023 AHS Table Specifications, Disability table and Column Variables sheet.",
        "weight": "WEIGHT",
        "comparability": "Directly comparable to 2019 DISHH; only approximately harmonized to 2011 HDSB because the 2011 disability recode is not identical.",
    },
    {
        "variable": "NUMWALK",
        "description": "Count category for persons in the unit with a physical disability: none, one, or two or more.",
        "source": "2023 AHS Table Specifications, Disability table; 2023 Value Labels package.",
        "weight": "WEIGHT",
        "comparability": "Directly comparable to 2019 NUMWALK; only approximately harmonized to 2011 HWALK because the 2011 household physical-disability recode is not identical.",
    },
    {
        "variable": "UNITFLOORS / BEDROOMS / BATHROOMS",
        "description": "Structural variables used only to build a lower-bound proxy for Bo'sher level 1 in 2023 because the dedicated accessibility module is absent.",
        "source": "2023 AHS flat PUF core household file.",
        "weight": "WEIGHT",
        "comparability": "Proxy only; not a direct substitute for the 2011 or 2019 accessibility-module questions and not a clean cross-year trend measure.",
    },
]

FILES_CREATED_OR_MODIFIED = [
    "scripts/ahs_2023_accessibility_analysis.py",
    "results/ahs_2023_accessibility_results.json",
    "results/ahs_2023_accessibility_analysis.md",
]

RAW_FILES_CREATED = [
    "data/ahs_accessibility/raw/AHS 2023 National PUF v1.1 Flat CSV.zip",
    "data/ahs_accessibility/raw/AHS 2019 National PUF v1.1 Flat CSV.zip",
    "data/ahs_accessibility/raw/AHS 2011 National PUF v3.0 Flat CSV.zip",
    "data/ahs_accessibility/raw/AHS 2023 Value Labels Package.zip",
    "data/ahs_accessibility/raw/AHS 2019 Value Labels Package.zip",
    "data/ahs_accessibility/raw/AHS 2011 National Value Labels Package.zip",
    "data/ahs_accessibility/raw/AHS 2023 Table Specifications and PUF Estimates for User Verification.xlsx",
    "data/ahs_accessibility/raw/2019 AHS Table Specifications and PUF Estimates for User Verification.xlsx",
    "data/ahs_accessibility/raw/AHS_ 2011_Table_Specs.xls",
    "data/ahs_accessibility/raw/accessibility-america-housingStock.pdf",
    "data/ahs_accessibility/raw/Getting Started with the AHS PUF 2015 and Beyond.pdf",
]


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_downloads() -> None:
    for key, url in SOURCE_URLS.items():
        path = RAW_FILES[key]
        if path.exists():
            continue
        print(f"Downloading {path.name} ...")
        urlretrieve(url, path)


def clean_code(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.strip("'")


def round_or_none(value: float | None, digits: int = 4) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), digits)


def weighted_share(mask: pd.Series, weights: pd.Series) -> float | None:
    total = float(weights.sum())
    if total == 0:
        return None
    return float(weights[mask].sum() / total)


def weighted_count(mask: pd.Series, weights: pd.Series) -> float:
    return float(weights[mask].sum())


def pct(value: float | None) -> float | None:
    return None if value is None else round(value * 100.0, 2)


def fmt_pct(value: float | None) -> str:
    return "N/A" if value is None else f"{value * 100:.2f}%"


def fmt_millions(value: float) -> str:
    return f"{value / 1_000_000:.2f}M"


def recode_tenure(code: str) -> str | None:
    if code == "1":
        return "owner"
    if code in {"2", "3"}:
        return "renter_or_no_cash_rent"
    return None


def recode_building_202x(code: str) -> str | None:
    if code == "02":
        return "single_family_detached"
    if code == "03":
        return "single_family_attached"
    if code in {"04", "05"}:
        return "multifamily_2_4"
    if code in {"06", "07"}:
        return "multifamily_5_19"
    if code in {"08", "09"}:
        return "multifamily_20_plus"
    if code in {"01", "10"}:
        return "mobile_or_other"
    return None


def recode_building_2011(nunit2: str, nunits: float | int | None) -> str | None:
    if nunit2 == "1":
        return "single_family_detached"
    if nunit2 == "2":
        return "single_family_attached"
    if nunit2 == "4":
        return "mobile_or_other"
    if nunit2 == "3":
        if nunits is None or pd.isna(nunits):
            return None
        nunits = float(nunits)
        if 2 <= nunits <= 4:
            return "multifamily_2_4"
        if 5 <= nunits <= 19:
            return "multifamily_5_19"
        if nunits >= 20:
            return "multifamily_20_plus"
    return None


def recode_year_bin(value: float | int | None) -> str | None:
    if value is None or pd.isna(value):
        return None
    year = int(value)
    if year <= 1930:
        return "pre_1940"
    if 1940 <= year <= 1950:
        return "1940_1959"
    if 1960 <= year <= 1975:
        return "1960_1979"
    if 1980 <= year <= 1995:
        return "1980_1999"
    if year >= 2000:
        return "2000_plus"
    return None


def grouped_share_table(
    frame: pd.DataFrame,
    weight_col: str,
    indicator_col: str,
    group_col: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for group_value in sorted(v for v in frame[group_col].dropna().unique()):
        sub = frame[frame[group_col] == group_value]
        weights = sub[weight_col]
        share = weighted_share(sub[indicator_col], weights)
        rows.append(
            {
                "group": str(group_value),
                "weighted_count": round(float(weights.sum()), 2),
                "indicator_weighted_count": round(weighted_count(sub[indicator_col], weights), 2),
                "share": round_or_none(share, 6),
                "share_pct": pct(share),
            }
        )
    return rows


def group_row(rows: list[dict[str, object]], group_value: object) -> dict[str, object]:
    group_key = str(group_value)
    for row in rows:
        if str(row["group"]) == group_key:
            return row
    raise KeyError(f"Group {group_key!r} not found in grouped results")


def load_2023() -> pd.DataFrame:
    cols = [
        "INTSTATUS",
        "WEIGHT",
        "TENURE",
        "BLD",
        "YRBUILT",
        "NOSTEP",
        "HMRACCESS",
        "DISHH",
        "NUMWALK",
        "UNITFLOORS",
        "BEDROOMS",
        "BATHROOMS",
    ]
    df = pd.read_csv(RAW_FILES["2023_flat_csv"], compression="zip", usecols=cols)
    for col in ["INTSTATUS", "TENURE", "BLD", "NOSTEP", "HMRACCESS", "DISHH", "NUMWALK", "BATHROOMS"]:
        df[col] = clean_code(df[col])
    return df


def load_2019() -> pd.DataFrame:
    cols = [
        "INTSTATUS",
        "WEIGHT",
        "SP2WEIGHT",
        "TENURE",
        "BLD",
        "YRBUILT",
        "NOSTEP",
        "HMRACCESS",
        "DISHH",
        "NUMWALK",
        "UNITFLOORS",
        "BEDROOMS",
        "BATHROOMS",
        "HAGETHOME",
        "HAGETBED",
        "HAGETKIT",
        "HAGETBATH",
        "HABEDUSE",
        "HAKITUSE",
        "HABATHUSE",
        "HARAMP",
        "HALIFT",
        "HABEDENTRY",
        "HABATHENTRY",
        "HAFUTURE",
        "HASUPP",
        "WCHAIR",
        "ECHAIR",
        "CRUTCH",
        "CANE",
        "MOBOTHER",
    ]
    df = pd.read_csv(RAW_FILES["2019_flat_csv"], compression="zip", usecols=cols)
    for col in [
        "INTSTATUS",
        "TENURE",
        "BLD",
        "NOSTEP",
        "HMRACCESS",
        "DISHH",
        "NUMWALK",
        "BATHROOMS",
        "HAGETHOME",
        "HAGETBED",
        "HAGETKIT",
        "HAGETBATH",
        "HABEDUSE",
        "HAKITUSE",
        "HABATHUSE",
        "HARAMP",
        "HALIFT",
        "HABEDENTRY",
        "HABATHENTRY",
        "HAFUTURE",
        "HASUPP",
        "WCHAIR",
        "ECHAIR",
        "CRUTCH",
        "CANE",
        "MOBOTHER",
    ]:
        df[col] = clean_code(df[col])
    return df


def load_2011() -> pd.DataFrame:
    cols = [
        "STATUS",
        "WGT90GEO",
        "TENURE",
        "NUNIT2",
        "NUNITS",
        "BUILT",
        "NOSTEP",
        "HDSB",
        "HWALK",
        "WCHAIR",
        "ECHAIR",
        "CRUTCH",
        "CANE",
        "SPOTHR",
        "HMELEVATE",
        "HMENTBD",
        "HMENTBTH",
        "HMLEVEL",
        "HMHNDRL",
        "HMBRL",
        "HMXWDR",
        "HMHNDLE",
        "HMSKLVR",
        "HMOUTLET",
        "HMSWITCH",
        "HMCLCTRL",
        "HMACAB",
        "HMCOUNT",
        "HMKIT",
        "HMBROOM",
        "FLOORS",
        "BEDRMS",
        "BATHS",
    ]
    df = pd.read_csv(RAW_FILES["2011_flat_csv"], compression="zip", usecols=cols)
    for col in [
        c
        for c in cols
        if c not in {"WGT90GEO", "NUNITS", "BUILT", "BEDRMS", "BATHS"}
    ]:
        df[col] = clean_code(df[col])
    return df


def add_common_fields_202x(df: pd.DataFrame, *, year: int) -> pd.DataFrame:
    out = df.copy()
    out["occupied"] = out["INTSTATUS"] == "1"
    out["all_housing"] = out["INTSTATUS"].isin(["1", "2", "3"])
    out["nostep"] = out["NOSTEP"] == "1"
    out["tenure_group"] = out["TENURE"].map(recode_tenure)
    out["building_group"] = out["BLD"].map(recode_building_202x)
    out["year_built_group"] = out["YRBUILT"].map(recode_year_bin)
    out["disabled_any"] = out["DISHH"] == "1"
    out["disabled_physical"] = out["NUMWALK"].isin(["2", "3"])
    out["year"] = year
    return out


def add_common_fields_2011(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["occupied"] = out["STATUS"] == "1"
    out["all_housing"] = out["STATUS"].isin(["1", "2", "3"])
    out["nostep"] = out["NOSTEP"] == "1"
    out["tenure_group"] = out["TENURE"].map(recode_tenure)
    out["building_group"] = [
        recode_building_2011(nunit2, nunits)
        for nunit2, nunits in zip(out["NUNIT2"], out["NUNITS"])
    ]
    out["year_built_group"] = out["BUILT"].map(recode_year_bin)
    out["disabled_any"] = out["HDSB"] == "1"
    out["disabled_physical"] = out["HWALK"] == "1"
    out["year"] = 2011
    return out


def compute_nostep_summary(df: pd.DataFrame, *, year: int, weight_col: str) -> dict[str, object]:
    all_housing = df[df["all_housing"]].copy()
    occupied = df[df["occupied"]].copy()
    return {
        "year": year,
        "all_housing_weighted_count": round(float(all_housing[weight_col].sum()), 2),
        "occupied_weighted_count": round(float(occupied[weight_col].sum()), 2),
        "nostep_all_housing_share": round_or_none(weighted_share(all_housing["nostep"], all_housing[weight_col]), 6),
        "nostep_all_housing_share_pct": pct(weighted_share(all_housing["nostep"], all_housing[weight_col])),
        "nostep_occupied_share": round_or_none(weighted_share(occupied["nostep"], occupied[weight_col]), 6),
        "nostep_occupied_share_pct": pct(weighted_share(occupied["nostep"], occupied[weight_col])),
        "nostep_occupied_by_tenure": grouped_share_table(occupied, weight_col, "nostep", "tenure_group"),
        "nostep_occupied_by_building_type": grouped_share_table(occupied, weight_col, "nostep", "building_group"),
        "nostep_occupied_by_year_built": grouped_share_table(occupied, weight_col, "nostep", "year_built_group"),
        "nostep_occupied_by_disabled_household": grouped_share_table(occupied, weight_col, "nostep", "disabled_any"),
        "nostep_occupied_by_physical_disability_household": grouped_share_table(occupied, weight_col, "nostep", "disabled_physical"),
    }


def compute_home_improvement_accessibility(df: pd.DataFrame, *, year: int) -> dict[str, object]:
    occupied_owner = (df["INTSTATUS"] == "1") & (df["TENURE"] == "1")
    universe = occupied_owner & (~df["HMRACCESS"].isin(["-6", "N", "nan"]))
    weights = df.loc[universe, "WEIGHT"]
    overall_mask = df.loc[universe, "HMRACCESS"] == "1"

    def subshare(mask: pd.Series) -> dict[str, object]:
        sub = df[universe & mask]
        subweights = sub["WEIGHT"]
        yes_mask = sub["HMRACCESS"] == "1"
        share = weighted_share(yes_mask, subweights)
        return {
            "weighted_universe": round(float(subweights.sum()), 2),
            "weighted_accessibility_yes": round(weighted_count(yes_mask, subweights), 2),
            "share": round_or_none(share, 6),
            "share_pct": pct(share),
        }

    return {
        "year": year,
        "universe_description": "Owner-occupied occupied units with a non-missing response to HMRACCESS, i.e., the home-improvement universe in the AHS Home Improvement table.",
        "overall": {
            "weighted_universe": round(float(weights.sum()), 2),
            "weighted_accessibility_yes": round(weighted_count(overall_mask, weights), 2),
            "share": round_or_none(weighted_share(overall_mask, weights), 6),
            "share_pct": pct(weighted_share(overall_mask, weights)),
        },
        "by_disabled_household": {
            "disabled_any": subshare(df["DISHH"] == "1"),
            "disabled_physical": subshare(df["NUMWALK"].isin(["2", "3"])),
            "non_disabled": subshare(df["DISHH"] == "2"),
        },
    }


def compute_2019_access_problem_history(df: pd.DataFrame) -> dict[str, object]:
    module = df[(df["INTSTATUS"] == "1") & (df["SP2WEIGHT"] > 0)].copy()
    problem_vars = {
        "entering_home_or_property": "HAGETHOME",
        "getting_to_bedroom": "HAGETBED",
        "using_bedroom": "HABEDUSE",
        "getting_to_kitchen": "HAGETKIT",
        "using_kitchen": "HAKITUSE",
        "getting_to_bathroom": "HAGETBATH",
        "using_bathroom": "HABATHUSE",
    }

    def bundle(mask: pd.Series) -> dict[str, object]:
        sub = module[mask].copy()
        weights = sub["SP2WEIGHT"]
        out: dict[str, object] = {
            "weighted_universe": round(float(weights.sum()), 2),
        }
        for label, var in problem_vars.items():
            share = weighted_share(sub[var] == "1", weights)
            out[label] = {"share": round_or_none(share, 6), "share_pct": pct(share)}
        return out

    return {
        "universe_description": "2019 occupied units in topical-module Group 2 (SP2WEIGHT > 0); no comparable 2023 module exists.",
        "all_households": bundle(pd.Series(True, index=module.index)),
        "disabled_households": bundle(module["DISHH"] == "1"),
        "physical_disability_households": bundle(module["NUMWALK"].isin(["2", "3"])),
        "non_disabled_households": bundle(module["DISHH"] == "2"),
    }


def compute_bosher_section(d11: pd.DataFrame, d19: pd.DataFrame, d23: pd.DataFrame) -> dict[str, object]:
    yes12: Callable[[pd.Series], pd.Series] = lambda s: s.isin(["1", "2"])

    all11 = d11[d11["STATUS"].isin(["1", "2", "3"])].copy()
    w11 = all11["WGT90GEO"]
    level1_repl = (
        (all11["NOSTEP"] == "1")
        & (yes12(all11["HMENTBTH"]) | yes12(all11["HMELEVATE"]) | (all11["FLOORS"] == "1"))
        & (yes12(all11["HMENTBD"]) | yes12(all11["HMELEVATE"]) | (all11["FLOORS"] == "1"))
    )
    level2_repl = level1_repl & (yes12(all11["HMLEVEL"]) | yes12(all11["HMHNDRL"])) & yes12(all11["HMBRL"])
    level3_repl = (
        level2_repl
        & yes12(all11["HMXWDR"])
        & yes12(all11["HMLEVEL"])
        & yes12(all11["HMHNDLE"])
        & yes12(all11["HMSKLVR"])
        & yes12(all11["HMOUTLET"])
        & yes12(all11["HMSWITCH"])
        & yes12(all11["HMCLCTRL"])
        & yes12(all11["HMACAB"])
        & yes12(all11["HMCOUNT"])
        & yes12(all11["HMKIT"])
    )

    module19 = d19[(d19["INTSTATUS"] == "1") & (d19["SP2WEIGHT"] > 0)].copy()
    level1_approx_2019 = (
        (module19["NOSTEP"] == "1")
        & ((module19["HALIFT"] == "1") | (module19["UNITFLOORS"] == 1) | (module19["HABEDENTRY"] == "1"))
        & ((module19["HALIFT"] == "1") | (module19["UNITFLOORS"] == 1) | (module19["HABATHENTRY"] == "1"))
    )

    all23 = d23[d23["INTSTATUS"].isin(["1", "2", "3"])].copy()
    bath23 = pd.to_numeric(all23["BATHROOMS"], errors="coerce")
    level1_lower_bound_2023 = (
        (all23["NOSTEP"] == "1")
        & (all23["UNITFLOORS"] == 1)
        & (all23["BEDROOMS"] >= 1)
        & (bath23 >= 1)
    )

    return {
        "2011_published": PUBLISHED_2011_BOSHER,
        "2011_public_puf_reconstruction": {
            "description": "Approximate public-PUF reconstruction using NOSTEP, inferred one-story entry-level bedroom/bathroom, and 2011 accessibility-module feature variables. Level 1 and level 3 track the published HUD report closely; level 2 does not, so the published HUD values remain the authoritative benchmark.",
            "level_1_share": round_or_none(weighted_share(level1_repl, w11), 6),
            "level_1_share_pct": pct(weighted_share(level1_repl, w11)),
            "level_2_share": round_or_none(weighted_share(level2_repl, w11), 6),
            "level_2_share_pct": pct(weighted_share(level2_repl, w11)),
            "level_3_share": round_or_none(weighted_share(level3_repl, w11), 6),
            "level_3_share_pct": pct(weighted_share(level3_repl, w11)),
        },
        "2019_level_1_approximation": {
            "description": "Approximate level-1-style structural measure using occupied 2019 topical-module Group 2 cases (SP2WEIGHT > 0), weighted by SP2WEIGHT, with NOSTEP plus HALIFT/HABEDENTRY/HABATHENTRY and UNITFLOORS. 2019 lacks the 2011 level-2/level-3 feature battery, and this estimate is not directly comparable to the 2023 lower-bound proxy.",
            "share": round_or_none(weighted_share(level1_approx_2019, module19["SP2WEIGHT"]), 6),
            "share_pct": pct(weighted_share(level1_approx_2019, module19["SP2WEIGHT"])),
        },
        "2023_level_1_lower_bound_proxy": {
            "description": "Lower-bound proxy only, computed on the 2023 all-housing core-file universe and weighted by WEIGHT: no-step entry plus a one-floor unit with at least one bedroom and one bathroom. 2023 lacks the 2019/2011 entry-level bedroom, entry-level bathroom, elevator, and wheelchair-feature questions needed for exact Bo'sher replication, so this is not directly comparable to the 2019 approximation.",
            "share": round_or_none(weighted_share(level1_lower_bound_2023, all23["WEIGHT"]), 6),
            "share_pct": pct(weighted_share(level1_lower_bound_2023, all23["WEIGHT"])),
        },
        "comparability_note": "The 2019 level-1-style approximation and the 2023 lower-bound level-1 proxy are not a clean 2019→2023 time series: the 2019 figure is an occupied topical-module Group 2 estimate weighted with SP2WEIGHT, while the 2023 figure is an all-housing core-file proxy weighted with WEIGHT.",
        "feasibility": {
            "2011": "Canonical three-tier framework available from the 2011 accessibility module and published HUD report.",
            "2019": "Only a partial level-1-style approximation is possible from public materials; the 2019 module was redesigned around accessibility problems and selected features rather than the full 2011 feature battery.",
            "2023": "Exact replication not possible. The 2015-2023 PUF guide lists no 2023 Home Accessibility topical module, and the 2023 table-spec workbook has no Home Accessibility sheet.",
        },
    }


def compute_results() -> dict[str, object]:
    ensure_dirs()
    ensure_downloads()

    d23 = add_common_fields_202x(load_2023(), year=2023)
    d19 = add_common_fields_202x(load_2019(), year=2019)
    d11 = add_common_fields_2011(load_2011())

    nostep_summaries = {
        "2011": compute_nostep_summary(d11, year=2011, weight_col="WGT90GEO"),
        "2019": compute_nostep_summary(d19, year=2019, weight_col="WEIGHT"),
        "2023": compute_nostep_summary(d23, year=2023, weight_col="WEIGHT"),
    }

    home_improvement = {
        "2019": compute_home_improvement_accessibility(d19, year=2019),
        "2023": compute_home_improvement_accessibility(d23, year=2023),
    }

    access_problems_2019 = compute_2019_access_problem_history(d19)
    bosher = compute_bosher_section(d11, d19, d23)

    headline = {
        "2023_nostep_all_housing_share_pct": nostep_summaries["2023"]["nostep_all_housing_share_pct"],
        "2023_nostep_occupied_share_pct": nostep_summaries["2023"]["nostep_occupied_share_pct"],
        "2019_nostep_occupied_share_pct": nostep_summaries["2019"]["nostep_occupied_share_pct"],
        "2011_nostep_occupied_share_pct": nostep_summaries["2011"]["nostep_occupied_share_pct"],
        "2023_accessibility_improvement_share_pct": home_improvement["2023"]["overall"]["share_pct"],
        "2019_accessibility_improvement_share_pct": home_improvement["2019"]["overall"]["share_pct"],
        "2011_bosher_level_1_published_pct": 33.34,
        "2011_bosher_level_2_published_pct": 3.76,
        "2011_bosher_level_3_published_pct": 0.15,
        "2019_approx_level_1_pct": bosher["2019_level_1_approximation"]["share_pct"],
        "2023_lower_bound_level_1_proxy_pct": bosher["2023_level_1_lower_bound_proxy"]["share_pct"],
    }

    limitations = [
        "The 2023 AHS national PUF does not include the dedicated Home Accessibility topical module that existed in 2019, so there is no 2023 analogue for the 2011 feature battery used by Bo'sher et al.",
        "2019 Home Accessibility variables use SP2WEIGHT because they are topical-module Group 2 items; 2023 accessibility-related variables used here are core-file items and therefore use WEIGHT.",
        "The canonical 2011 Bo'sher three-tier figures are reported from the published HUD report. Public-PUF reconstruction comes close for levels 1 and 3 but not level 2, so published HUD values remain the authoritative 2011 benchmark.",
        "The 2019 level-1-style approximation and 2023 lower-bound proxy are not a clean 2019→2023 comparable series because they use different universes, weights, and question batteries (2019 occupied topical-module Group 2 cases with SP2WEIGHT versus a 2023 all-housing core-file proxy with WEIGHT).",
        "The 2023 Bo'sher-style result is only a lower-bound structural proxy based on no-step entry plus one-floor units with at least one bedroom and one bathroom; it is not directly comparable to the full 2011 level-1 index.",
        "Because 2023 lacks the 2019 problem-based accessibility module, 2019 home-accessibility problem shares are historical context only, not trend estimates continued into 2023.",
        "Reported differences in this memo are descriptive weighted differences from AHS tabulations; the script does not estimate sampling variance or test statistical significance.",
        "Cross-year subgroup comparisons are approximate harmonizations rather than exact apples-to-apples measures: 2011 uses HDSB/HWALK recodes, while 2019 and 2023 use DISHH/NUMWALK or related proxies.",
    ]

    results = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo_path": str(REPO_DIR),
            "analysis_title": "2023 AHS accessibility analysis",
            "primary_task": "Research task p4: download and analyze the 2023 AHS national PUF for accessibility-related measures and compare to 2011 and 2019.",
        },
        "sources": {
            key: {"url": url, "local_path": str(RAW_FILES[key])}
            for key, url in SOURCE_URLS.items()
        },
        "module_history": {
            "2019": "The 2015-2023 PUF guide lists 2019 Home Accessibility as topical-module Group 2 (Accessibility), implying SP2WEIGHT for module variables.",
            "2023": "The same guide lists 2023 topical modules such as heat risk, power outages, healthy homes, housing insecurity, and SOGI, but no 2023 Home Accessibility topical module.",
            "consequence": "2023 analysis must rely on core accessibility proxies and home-improvement accessibility motive, not the detailed 2011/2019 module battery.",
        },
        "2023_variable_inventory": VARIABLE_INVENTORY_2023,
        "headline_findings": headline,
        "nostep_comparison": nostep_summaries,
        "home_improvement_accessibility": home_improvement,
        "2019_home_accessibility_problem_context": access_problems_2019,
        "bosher_three_tier_framework": bosher,
        "limitations": limitations,
        "files_created_or_modified": FILES_CREATED_OR_MODIFIED,
        "raw_files_downloaded": RAW_FILES_CREATED,
    }
    return results


def md_table(
    rows: list[dict[str, object]],
    *,
    header1: str,
    label_map: dict[str, str] | None = None,
) -> str:
    lines = [f"| {header1} | Weighted universe | Weighted yes | Share |", "|---|---:|---:|---:|"]
    for row in rows:
        group_label = str(row["group"])
        if label_map is not None:
            group_label = label_map.get(group_label, group_label)
        lines.append(
            f"| {group_label} | {fmt_millions(float(row['weighted_count']))} | {fmt_millions(float(row['indicator_weighted_count']))} | {row['share_pct']:.2f}% |"
        )
    return "\n".join(lines)


def write_markdown(results: dict[str, object]) -> None:
    n11 = results["nostep_comparison"]["2011"]
    n19 = results["nostep_comparison"]["2019"]
    n23 = results["nostep_comparison"]["2023"]
    hi19 = results["home_improvement_accessibility"]["2019"]
    hi23 = results["home_improvement_accessibility"]["2023"]
    bosher = results["bosher_three_tier_framework"]
    access2019 = results["2019_home_accessibility_problem_context"]
    disabled_row_2023 = group_row(n23["nostep_occupied_by_disabled_household"], True)
    non_disabled_row_2023 = group_row(n23["nostep_occupied_by_disabled_household"], False)
    physical_disabled_row_2023 = group_row(n23["nostep_occupied_by_physical_disability_household"], True)

    lines: list[str] = []
    lines.append("# 2023 AHS Accessibility Analysis Memo")
    lines.append("")
    lines.append(f"Generated: {results['metadata']['generated_at']}")
    lines.append(f"Repo: `{results['metadata']['repo_path']}`")
    lines.append("")
    lines.append("## Bottom line")
    lines.append("")
    lines.append("The 2023 AHS national PUF does not include the dedicated Home Accessibility topical module that appeared in 2019, so the 2023 file cannot support a full Bo'sher-style three-tier accessibility replication. The 2023 PUF still supports several core accessibility-relevant measures, especially no-step entry (`NOSTEP`), disability-household status (`DISHH`, `NUMWALK`), and accessibility-motivated home improvements (`HMRACCESS`).")
    lines.append("")
    lines.append(f"Using Census weights, the share of occupied units with no-step entry rose from {n11['nostep_occupied_share_pct']:.2f}% in 2011 to {n19['nostep_occupied_share_pct']:.2f}% in 2019 and {n23['nostep_occupied_share_pct']:.2f}% in 2023.")
    lines.append("")
    lines.append(f"Among owner-occupied units in the AHS home-improvement universe, the share reporting accessibility-for-elderly-or-disabled work increased from {hi19['overall']['share_pct']:.2f}% in 2019 to {hi23['overall']['share_pct']:.2f}% in 2023.")
    lines.append("")
    lines.append("## Source-discipline finding: 2023 has no dedicated home accessibility topical module")
    lines.append("")
    lines.append("Public Census documentation matters here. The 2015-2023 AHS PUF guide lists `2019 Home Accessibility` as a Group 2 topical module but does not list any 2023 Home Accessibility module. The 2023 table-spec workbook likewise has no `Home Accessibility` sheet, unlike the 2019 workbook. That is why the 2023 analysis below relies on the remaining core variables instead of a full feature battery.")
    lines.append("")
    lines.append("## 2023 accessibility-related variables identified from public AHS materials")
    lines.append("")
    for item in results["2023_variable_inventory"]:
        lines.append(f"- `{item['variable']}`: {item['description']} Source: {item['source']} Weight: `{item['weight']}`. Comparability: {item['comparability']}")
    lines.append("")
    lines.append("## Key weighted findings")
    lines.append("")
    lines.append("All differences reported below are descriptive weighted differences from AHS tabulations; they are not significance-tested estimates.")
    lines.append("")
    lines.append(f"- 2023 all-housing-unit no-step share: {n23['nostep_all_housing_share_pct']:.2f}%.")
    lines.append(f"- 2023 occupied-unit no-step share: {n23['nostep_occupied_share_pct']:.2f}%.")
    lines.append(f"- 2023 occupied disabled-household no-step share: {disabled_row_2023['share_pct']:.2f}% versus {non_disabled_row_2023['share_pct']:.2f}% for non-disabled households.")
    lines.append(f"- 2023 occupied physically disabled-household no-step share: {physical_disabled_row_2023['share_pct']:.2f}%.")
    lines.append(f"- 2023 owner-improver accessibility-motive share: {hi23['overall']['share_pct']:.2f}% of the weighted home-improvement universe ({fmt_millions(hi23['overall']['weighted_accessibility_yes'])} out of {fmt_millions(hi23['overall']['weighted_universe'])}).")
    lines.append(f"- In 2023 that accessibility-motive share rises to {hi23['by_disabled_household']['disabled_any']['share_pct']:.2f}% for disabled households and {hi23['by_disabled_household']['disabled_physical']['share_pct']:.2f}% for physically disabled households, compared with {hi23['by_disabled_household']['non_disabled']['share_pct']:.2f}% for non-disabled households.")
    lines.append("")
    lines.append("## No-step entry trend, 2011 to 2023")
    lines.append("")
    lines.append("| Year | Occupied no-step share | All-housing no-step share | Weighted occupied universe |")
    lines.append("|---|---:|---:|---:|")
    for label, block in [("2011", n11), ("2019", n19), ("2023", n23)]:
        lines.append(f"| {label} | {block['nostep_occupied_share_pct']:.2f}% | {block['nostep_all_housing_share_pct']:.2f}% | {fmt_millions(block['occupied_weighted_count'])} |")
    lines.append("")
    lines.append("## 2023 disaggregation: no-step entry among occupied units")
    lines.append("")
    lines.append("### By tenure")
    lines.append("")
    lines.append(md_table(n23["nostep_occupied_by_tenure"], header1="Tenure"))
    lines.append("")
    lines.append("### By building type")
    lines.append("")
    lines.append(md_table(n23["nostep_occupied_by_building_type"], header1="Building type"))
    lines.append("")
    lines.append("### By year built")
    lines.append("")
    lines.append(md_table(n23["nostep_occupied_by_year_built"], header1="Year built group"))
    lines.append("")
    lines.append("### By disability household")
    lines.append("")
    lines.append(
        md_table(
            n23["nostep_occupied_by_disabled_household"],
            header1="Disabled household",
            label_map={
                "False": "No disabled household member",
                "True": "At least one disabled household member",
            },
        )
    )
    lines.append("")
    lines.append("## 2019 module-only context")
    lines.append("")
    lines.append("The 2019 Home Accessibility topical module asked problem-based questions that disappear in 2023. Those results are therefore historical context, not a continued trend line. Using SP2WEIGHT, the 2019 physically disabled household subset reported the following problem rates:")
    lines.append("")
    phys = access2019["physical_disability_households"]
    lines.append(f"- Trouble entering home/property: {phys['entering_home_or_property']['share_pct']:.2f}%")
    lines.append(f"- Trouble getting to bedroom: {phys['getting_to_bedroom']['share_pct']:.2f}%")
    lines.append(f"- Trouble using bedroom: {phys['using_bedroom']['share_pct']:.2f}%")
    lines.append(f"- Trouble getting to kitchen: {phys['getting_to_kitchen']['share_pct']:.2f}%")
    lines.append(f"- Trouble using kitchen: {phys['using_kitchen']['share_pct']:.2f}%")
    lines.append(f"- Trouble getting to bathroom: {phys['getting_to_bathroom']['share_pct']:.2f}%")
    lines.append(f"- Trouble using bathroom: {phys['using_bathroom']['share_pct']:.2f}%")
    lines.append("")
    lines.append("## Bo'sher three-tier framework")
    lines.append("")
    lines.append("Published 2011 HUD benchmark:")
    lines.append("")
    lines.append(f"- Level 1 potentially modifiable: {PUBLISHED_2011_BOSHER['all_housing_units']['level_1_potentially_modifiable_share'] * 100:.2f}%")
    lines.append(f"- Level 2 livable for moderate mobility difficulty: {PUBLISHED_2011_BOSHER['all_housing_units']['level_2_livable_share'] * 100:.2f}%")
    lines.append(f"- Level 3 wheelchair accessible: {PUBLISHED_2011_BOSHER['all_housing_units']['level_3_wheelchair_accessible_share'] * 100:.2f}%")
    lines.append("")
    lines.append("What can be done with public materials beyond that benchmark:")
    lines.append("")
    lines.append(f"- 2011 public-PUF reconstruction: L1 {bosher['2011_public_puf_reconstruction']['level_1_share_pct']:.2f}%, L2 {bosher['2011_public_puf_reconstruction']['level_2_share_pct']:.2f}%, L3 {bosher['2011_public_puf_reconstruction']['level_3_share_pct']:.2f}%. This reproduces levels 1 and 3 fairly closely but overshoots level 2, so the HUD report remains the authoritative 2011 reference.")
    lines.append(f"- 2019 level-1-style approximation: {bosher['2019_level_1_approximation']['share_pct']:.2f}% among occupied topical-module Group 2 cases, weighted with SP2WEIGHT.")
    lines.append(f"- 2023 lower-bound level-1 proxy: {bosher['2023_level_1_lower_bound_proxy']['share_pct']:.2f}% across the all-housing core-file universe, weighted with WEIGHT.")
    lines.append("")
    lines.append(bosher["comparability_note"])
    lines.append("")
    lines.append("The critical limitation is that 2023 lacks the dedicated accessibility-module variables needed for level 2 and level 3. The script therefore reports those as infeasible for exact replication in 2023.")
    lines.append("")
    lines.append("## Main limitations")
    lines.append("")
    for item in results["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Files created or modified by this task")
    lines.append("")
    for item in FILES_CREATED_OR_MODIFIED:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Raw downloads created for reproducibility")
    lines.append("")
    for item in RAW_FILES_CREATED:
        lines.append(f"- {item}")

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results = compute_results()
    OUTPUT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results)
    print(f"Wrote {OUTPUT_JSON}")
    print(f"Wrote {OUTPUT_MD}")


if __name__ == "__main__":
    main()
