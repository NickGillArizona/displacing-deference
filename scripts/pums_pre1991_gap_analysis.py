"""
Estimate the pre-March 13, 1991 statutory accessibility gap in the current
U.S. renter-occupied housing stock using ACS 2020-2024 5-Year PUMS.

Outputs:
  - results/pre1991_statutory_gap_analysis.json
  - results/pre1991_statutory_gap_analysis.md

Method summary:
  * Universe: renter-occupied householders (TEN=3, SPORDER=1), 50 states + DC.
    Puerto Rico is excluded from the U.S. total and metro/non-metro split.
  * Weight: WGTP (housing-unit weight).
  * Disability proxy: DPHY=1 or DOUT=1 for the householder.
  * 4+ proxy: BLD=05-09. ACS PUMS does not separate 4-unit from 3-unit
    buildings, so BLD=05 (3-4 units) is retained as the closest reproducible
    proxy and labeled accordingly in outputs.
  * Pre-trigger dating: ACS PUMS collapses 1990-1999 into one YRBLT bucket.
    The script therefore reports both:
      (1) a strict lower bound that counts only pre-1990 buckets as exempt; and
      (2) an adjusted estimate that allocates 437 / 3652 = 11.966% of the
          1990-1999 bucket to the pre-March 13, 1991 period, assuming a
          uniform distribution within that decade bucket.
  * Metro split: 2020 tract-to-PUMA relationship file plus the July 2023 OMB
    delineation file (based on 2020 standards). A PUMA is classified as metro
    when a majority of its constituent tracts lie in metropolitan counties.

This script uses curl for Census API reliability because large PUMS requests are
substantially more stable through curl --compressed than through urllib alone in
this workspace.
"""

from __future__ import annotations

import csv
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from json import JSONDecoder
from typing import Dict, Iterable, Iterator, List, Tuple
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RESULTS_DIR

BASE_URL = "https://api.census.gov/data/2024/acs/acs5/pums"
TRACT_TO_PUMA_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/"
    "2020_Census_Tract_to_2020_PUMA.txt"
)
CBSA_DELINEATION_URL = (
    "https://www2.census.gov/programs-surveys/metro-micro/geographies/"
    "reference-files/2023/delineation-files/list1_2023.xlsx"
)

NONCOMPLIANCE_RATE = 0.47
NONCOMPLIANCE_RATE_SOURCE = (
    "Housing Equality Center of Pennsylvania regional testing, as summarized in "
    "appendices/Appendix_H_Supplementary_Data.md"
)

PRE_1990_CODES = {"1939", "1940", "1950", "1960", "1970", "1980"}
YRBLT_1990S_CODE = "1990"
POST_1999_CODES = {"2000", "2010", "2020", "2021", "2022", "2023", "2024"}
KNOWN_YRBLT_CODES = PRE_1990_CODES | {YRBLT_1990S_CODE} | POST_1999_CODES

# 1990-01-01 through 1991-03-13 inclusive = 437 days.
# 1990-1999 inclusive = 3652 days.
PRE_TRIGGER_1990S_FRACTION = 437 / 3652

SIZE_BUCKETS = {
    "four_unit_proxy": {
        "label": "3-4 unit bucket (includes 4-unit buildings)",
        "codes": {"05"},
    },
    "five_to_nineteen": {
        "label": "5-19 units",
        "codes": {"06", "07"},
    },
    "twenty_to_forty_nine": {
        "label": "20-49 units",
        "codes": {"08"},
    },
    "fifty_plus": {
        "label": "50+ units",
        "codes": {"09"},
    },
}
SIZE_BUCKET_BY_CODE = {
    code: bucket_name
    for bucket_name, spec in SIZE_BUCKETS.items()
    for code in spec["codes"]
}
FOUR_PLUS_PROXY_CODES = set(SIZE_BUCKET_BY_CODE)

YEAR_BUILT_BUCKETS = [
    ("1939", "1939 or earlier"),
    ("1940", "1940-49"),
    ("1950", "1950-59"),
    ("1960", "1960-69"),
    ("1970", "1970-79"),
    ("1980", "1980-89"),
    ("1990", "1990-1999"),
    ("2000", "2000-2009"),
    ("2010", "2010-2019"),
    ("2020", "2020"),
    ("2021", "2021"),
    ("2022", "2022"),
    ("2023", "2023"),
    ("2024", "2024"),
    ("unknown", "Unknown year built"),
]
YEAR_BUILT_LABELS = dict(YEAR_BUILT_BUCKETS)

STOCK_TABLE_SIZE_BUCKETS = {
    "mobile_or_nonbuilding": {
        "label": "Mobile home / boat / RV / van",
        "codes": {"01", "10"},
    },
    "one_unit": {
        "label": "1 unit (detached or attached)",
        "codes": {"02", "03"},
    },
    "two_units": {
        "label": "2 units",
        "codes": {"04"},
    },
    "three_to_four_units": {
        "label": "3-4 units (includes 4-unit buildings)",
        "codes": {"05"},
    },
    "five_to_nineteen": {
        "label": "5-19 units",
        "codes": {"06", "07"},
    },
    "twenty_to_forty_nine": {
        "label": "20-49 units",
        "codes": {"08"},
    },
    "fifty_plus": {
        "label": "50+ units",
        "codes": {"09"},
    },
    "unknown_other": {
        "label": "Unknown / other",
        "codes": set(),
    },
}
STOCK_TABLE_SIZE_BUCKET_BY_CODE = {
    code: bucket_name
    for bucket_name, spec in STOCK_TABLE_SIZE_BUCKETS.items()
    for code in spec["codes"]
}

EXCLUDED_STATE_CODES = {"72"}  # Puerto Rico


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def pct(num: float, den: float) -> float:
    return num / den if den else 0.0


def fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def fmt_pct2(x: float) -> str:
    return f"{x * 100:.2f}%"


def fmt_int(x: float) -> str:
    return f"{int(round(x)):,.0f}"


def fmt_millions(x: float) -> str:
    return f"{x / 1_000_000:.2f} million"


def download_bytes(url: str, timeout: int = 120, retries: int = 4) -> bytes:
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:  # pragma: no cover - network retry path
            if attempt == retries:
                raise
            wait = 3 * attempt
            print(f"  retrying download after error: {exc} (sleep {wait}s)", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"unreachable download retry loop for {url}")


def parse_xlsx_rows(raw: bytes, worksheet_name: str = "xl/worksheets/sheet1.xml") -> Iterator[List[str]]:
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{namespace}si"):
                text = "".join((t.text or "") for t in si.findall(f".//{namespace}t"))
                shared_strings.append(text)

        sheet = ET.fromstring(zf.read(worksheet_name))
        for row in sheet.findall(f".//{namespace}row"):
            values: List[str] = []
            for cell in row.findall(f"{namespace}c"):
                cell_type = cell.attrib.get("t")
                value_node = cell.find(f"{namespace}v")
                if value_node is None:
                    values.append("")
                    continue
                value = value_node.text or ""
                if cell_type == "s" and value:
                    value = shared_strings[int(value)]
                values.append(value)
            yield values


def build_puma_metro_map() -> Dict[str, bool]:
    print("Building PUMA metro/non-metro classification ...", flush=True)
    print("  downloading tract-to-PUMA relationship file ...", flush=True)
    tract_raw = download_bytes(TRACT_TO_PUMA_URL, timeout=180)
    tract_text = tract_raw.decode("utf-8-sig")

    puma_counties: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    reader = csv.DictReader(io.StringIO(tract_text))
    for row in reader:
        state = row.get("STATEFP", "")
        county = row.get("COUNTYFP", "")
        puma = row.get("PUMA5CE", "")
        if not state or not county or not puma or state in EXCLUDED_STATE_CODES:
            continue
        puma_counties[(state, puma)][state + county] += 1

    print("  downloading metropolitan delineation file ...", flush=True)
    cbsa_raw = download_bytes(CBSA_DELINEATION_URL, timeout=180)
    rows = list(parse_xlsx_rows(cbsa_raw))
    if len(rows) < 4:
        raise RuntimeError("unexpected CBSA worksheet shape")

    header = rows[2]
    try:
        metro_type_idx = header.index("Metropolitan/Micropolitan Statistical Area")
        state_idx = header.index("FIPS State Code")
        county_idx = header.index("FIPS County Code")
    except ValueError as exc:
        raise RuntimeError(f"CBSA header mismatch: {header}") from exc

    metro_counties = set()
    for row in rows[3:]:
        if len(row) <= max(metro_type_idx, state_idx, county_idx):
            continue
        metro_type = row[metro_type_idx].strip().lower()
        if metro_type != "metropolitan statistical area":
            continue
        state = row[state_idx].zfill(2)
        county = row[county_idx].zfill(3)
        if state in EXCLUDED_STATE_CODES:
            continue
        metro_counties.add(state + county)

    puma_metro: Dict[str, bool] = {}
    for (state, puma), county_counter in puma_counties.items():
        total_tracts = sum(county_counter.values())
        metro_tracts = sum(
            tract_count
            for county_fips, tract_count in county_counter.items()
            if county_fips in metro_counties
        )
        puma_metro[f"{state}:{puma}"] = metro_tracts > total_tracts / 2

    metro_pumas = sum(1 for value in puma_metro.values() if value)
    nonmetro_pumas = sum(1 for value in puma_metro.values() if not value)
    print(
        f"  classified {len(puma_metro):,} PUMAs: {metro_pumas:,} metro, {nonmetro_pumas:,} non-metro",
        flush=True,
    )
    return puma_metro


def require_curl() -> str:
    curl_path = shutil.which("curl")
    if not curl_path:
        raise RuntimeError("curl is required for stable Census API queries in this workspace")
    return curl_path


def download_census_response(url: str, label: str, retries: int = 4) -> str:
    curl_path = require_curl()
    fd, temp_path = tempfile.mkstemp(prefix="census_pums_", suffix=".json")
    os.close(fd)

    for attempt in range(1, retries + 1):
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            run = subprocess.run(
                [
                    curl_path,
                    "-L",
                    "--compressed",
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--retry",
                    "5",
                    "--retry-all-errors",
                    "--retry-delay",
                    "3",
                    "--output",
                    temp_path,
                    url,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=False,
            )
            if run.returncode != 0:
                err_text = run.stderr.decode("utf-8", "replace").strip()
                raise RuntimeError(f"{label}: curl exited with {run.returncode}: {err_text}")
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                raise RuntimeError(f"{label}: curl produced an empty response file")
            return temp_path
        except Exception as exc:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if attempt == retries:
                raise
            wait = 5 * attempt
            print(
                f"  {label} failed on attempt {attempt}/{retries}: {exc}. retrying in {wait}s ...",
                flush=True,
            )
            time.sleep(wait)

    raise RuntimeError(f"unreachable Census retry loop for {label}")


def iter_census_objects_from_stream(stream: io.TextIOBase, label: str) -> Iterator[List[str]]:
    decoder = JSONDecoder()
    buffer = ""
    started = False
    finished = False
    first_error_snippet = None

    while True:
        chunk = stream.read(1 << 16)
        if not chunk:
            break
        buffer += chunk

        while True:
            buffer = buffer.lstrip()
            if not started:
                if not buffer:
                    break
                if not buffer.startswith("["):
                    first_error_snippet = buffer[:240]
                    raise RuntimeError(
                        f"{label}: Census response was not JSON: {first_error_snippet!r}"
                    )
                buffer = buffer[1:]
                started = True
                continue

            if not buffer:
                break
            if buffer.startswith(","):
                buffer = buffer[1:]
                continue
            if buffer.startswith("]"):
                buffer = buffer[1:]
                finished = True
                break

            try:
                obj, idx = decoder.raw_decode(buffer)
            except json.JSONDecodeError:
                break

            yield obj
            buffer = buffer[idx:].lstrip()
            if buffer.startswith(","):
                buffer = buffer[1:]
                continue
            if buffer.startswith("]"):
                buffer = buffer[1:]
                finished = True
                break
        if finished:
            break

    while True:
        buffer = buffer.lstrip()
        if not buffer:
            break
        if not started:
            if not buffer.startswith("["):
                first_error_snippet = buffer[:240]
                raise RuntimeError(
                    f"{label}: Census response was not JSON: {first_error_snippet!r}"
                )
            buffer = buffer[1:]
            started = True
            continue
        if buffer.startswith(","):
            buffer = buffer[1:]
            continue
        if buffer.startswith("]"):
            buffer = buffer[1:]
            finished = True
            break
        try:
            obj, idx = decoder.raw_decode(buffer)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{label}: failed to parse trailing Census response segment"
            ) from exc
        yield obj
        buffer = buffer[idx:].lstrip()
        if buffer.startswith(","):
            buffer = buffer[1:]
            continue
        if buffer.startswith("]"):
            buffer = buffer[1:]
            finished = True
            break

    if not started:
        raise RuntimeError(f"{label}: empty response from Census API")
    if not finished:
        raise RuntimeError(f"{label}: response did not terminate cleanly")


def iter_census_objects(url: str, label: str, retries: int = 4) -> Iterator[List[str]]:
    response_path = download_census_response(url, label, retries=retries)
    try:
        with open(response_path, "r", encoding="utf-8") as fh:
            yield from iter_census_objects_from_stream(fh, label)
    finally:
        if os.path.exists(response_path):
            os.remove(response_path)


def census_query_url(get_vars: Iterable[str]) -> str:
    vars_fragment = ",".join(get_vars)
    return f"{BASE_URL}?get={vars_fragment}&for=state:*&SPORDER=1&TEN=3"


def new_size_bucket_template() -> Dict[str, float]:
    return {
        "total": 0.0,
        "disabled": 0.0,
        "pre1990_lower": 0.0,
        "yr1990s": 0.0,
        "post1999": 0.0,
        "disabled_pre1990_lower": 0.0,
        "disabled_yr1990s": 0.0,
        "disabled_post1999": 0.0,
    }


def new_stock_table_template() -> Dict[str, Dict[str, float]]:
    return {
        year_code: {bucket_name: 0.0 for bucket_name in STOCK_TABLE_SIZE_BUCKETS}
        for year_code, _ in YEAR_BUILT_BUCKETS
    }


def new_segment_template() -> Dict[str, object]:
    return {
        "total": 0.0,
        "disabled": 0.0,
        "all_pre1990_lower": 0.0,
        "all_yr1990s": 0.0,
        "all_post1999": 0.0,
        "disabled_all_pre1990_lower": 0.0,
        "disabled_all_yr1990s": 0.0,
        "disabled_all_post1999": 0.0,
        "four_plus_total": 0.0,
        "four_plus_disabled": 0.0,
        "four_plus_pre1990_lower": 0.0,
        "four_plus_yr1990s": 0.0,
        "four_plus_post1999": 0.0,
        "four_plus_disabled_pre1990_lower": 0.0,
        "four_plus_disabled_yr1990s": 0.0,
        "four_plus_disabled_post1999": 0.0,
        "unknown_year_total": 0.0,
        "unknown_year_disabled": 0.0,
        "size_buckets": {name: new_size_bucket_template() for name in SIZE_BUCKETS},
        "building_stock_by_year_built_size_tenure": new_stock_table_template(),
    }


def update_segment(segment: Dict[str, object], weight: int, disabled: bool, bld: str, yrblt: str) -> None:
    segment["total"] += weight
    if disabled:
        segment["disabled"] += weight

    year_known = yrblt in KNOWN_YRBLT_CODES
    year_table_code = yrblt if year_known else "unknown"
    stock_size_bucket_name = STOCK_TABLE_SIZE_BUCKET_BY_CODE.get(bld, "unknown_other")
    segment["building_stock_by_year_built_size_tenure"][year_table_code][stock_size_bucket_name] += weight
    if not year_known:
        segment["unknown_year_total"] += weight
        if disabled:
            segment["unknown_year_disabled"] += weight
    elif yrblt in PRE_1990_CODES:
        segment["all_pre1990_lower"] += weight
        if disabled:
            segment["disabled_all_pre1990_lower"] += weight
    elif yrblt == YRBLT_1990S_CODE:
        segment["all_yr1990s"] += weight
        if disabled:
            segment["disabled_all_yr1990s"] += weight
    else:
        segment["all_post1999"] += weight
        if disabled:
            segment["disabled_all_post1999"] += weight

    if bld not in FOUR_PLUS_PROXY_CODES:
        return

    segment["four_plus_total"] += weight
    if disabled:
        segment["four_plus_disabled"] += weight

    if year_known:
        if yrblt in PRE_1990_CODES:
            segment["four_plus_pre1990_lower"] += weight
            if disabled:
                segment["four_plus_disabled_pre1990_lower"] += weight
        elif yrblt == YRBLT_1990S_CODE:
            segment["four_plus_yr1990s"] += weight
            if disabled:
                segment["four_plus_disabled_yr1990s"] += weight
        else:
            segment["four_plus_post1999"] += weight
            if disabled:
                segment["four_plus_disabled_post1999"] += weight

    size_bucket_name = SIZE_BUCKET_BY_CODE[bld]
    size_bucket = segment["size_buckets"][size_bucket_name]
    size_bucket["total"] += weight
    if disabled:
        size_bucket["disabled"] += weight
    if year_known:
        if yrblt in PRE_1990_CODES:
            size_bucket["pre1990_lower"] += weight
            if disabled:
                size_bucket["disabled_pre1990_lower"] += weight
        elif yrblt == YRBLT_1990S_CODE:
            size_bucket["yr1990s"] += weight
            if disabled:
                size_bucket["disabled_yr1990s"] += weight
        else:
            size_bucket["post1999"] += weight
            if disabled:
                size_bucket["disabled_post1999"] += weight


def build_geo_lookup(puma_metro: Dict[str, bool]) -> Tuple[Dict[str, bool], Dict[str, int]]:
    print("Fetching PUMA geography lookup from Census PUMS ...", flush=True)
    url = census_query_url(["SERIALNO", "PUMA"])
    serial_to_metro: Dict[str, bool] = {}
    stats = {
        "rows_seen": 0,
        "excluded_rows_puerto_rico": 0,
        "unmatched_puma_rows": 0,
        "duplicate_serial_conflicts": 0,
    }

    header = None
    serial_idx = puma_idx = state_idx = None
    started = time.time()
    for obj in iter_census_objects(url, label="geo lookup query"):
        if header is None:
            header = obj
            serial_idx = header.index("SERIALNO")
            puma_idx = header.index("PUMA")
            state_idx = header.index("state")
            continue

        stats["rows_seen"] += 1
        if stats["rows_seen"] % 250_000 == 0:
            elapsed = time.time() - started
            print(f"  geo rows processed: {stats['rows_seen']:,} ({elapsed:.1f}s)", flush=True)

        serial = obj[serial_idx]
        state = obj[state_idx]
        if state in EXCLUDED_STATE_CODES:
            stats["excluded_rows_puerto_rico"] += 1
            continue

        puma = obj[puma_idx]
        metro_value = puma_metro.get(f"{state}:{puma}")
        if metro_value is None:
            stats["unmatched_puma_rows"] += 1
            continue

        key = f"{state}:{serial}"
        prior = serial_to_metro.get(key)
        if prior is not None and prior != metro_value:
            stats["duplicate_serial_conflicts"] += 1
        serial_to_metro[key] = metro_value

    print(
        f"  geo lookup complete: {len(serial_to_metro):,} matched householders; "
        f"{stats['unmatched_puma_rows']:,} unmatched PUMA rows",
        flush=True,
    )
    return serial_to_metro, stats


def aggregate_housing(serial_to_metro: Dict[str, bool]) -> Tuple[Dict[str, Dict[str, object]], Dict[str, int]]:
    print("Fetching housing/disability/year-built microdata from Census PUMS ...", flush=True)
    url = census_query_url(["SERIALNO", "WGTP", "DPHY", "DOUT", "BLD", "YRBLT"])
    segments = {
        "overall": new_segment_template(),
        "Metro": new_segment_template(),
        "Non-metro": new_segment_template(),
    }
    stats = {
        "rows_seen": 0,
        "excluded_rows_puerto_rico": 0,
        "missing_geo_lookup_rows": 0,
        "blank_weight_rows": 0,
    }

    header = None
    serial_idx = weight_idx = dphy_idx = dout_idx = bld_idx = yrblt_idx = state_idx = None
    started = time.time()
    for obj in iter_census_objects(url, label="core housing query"):
        if header is None:
            header = obj
            serial_idx = header.index("SERIALNO")
            weight_idx = header.index("WGTP")
            dphy_idx = header.index("DPHY")
            dout_idx = header.index("DOUT")
            bld_idx = header.index("BLD")
            yrblt_idx = header.index("YRBLT")
            state_idx = header.index("state")
            continue

        stats["rows_seen"] += 1
        if stats["rows_seen"] % 250_000 == 0:
            elapsed = time.time() - started
            print(f"  housing rows processed: {stats['rows_seen']:,} ({elapsed:.1f}s)", flush=True)

        state = obj[state_idx]
        if state in EXCLUDED_STATE_CODES:
            stats["excluded_rows_puerto_rico"] += 1
            continue

        serial = obj[serial_idx]
        key = f"{state}:{serial}"
        metro_bool = serial_to_metro.get(key)
        if metro_bool is None:
            stats["missing_geo_lookup_rows"] += 1

        weight_raw = (obj[weight_idx] or "").strip()
        if not weight_raw:
            stats["blank_weight_rows"] += 1
            continue
        weight = int(weight_raw)
        disabled = (obj[dphy_idx] == "1") or (obj[dout_idx] == "1")
        bld = obj[bld_idx].zfill(2)
        yrblt = obj[yrblt_idx]

        update_segment(segments["overall"], weight, disabled, bld, yrblt)
        if metro_bool is True:
            update_segment(segments["Metro"], weight, disabled, bld, yrblt)
        elif metro_bool is False:
            update_segment(segments["Non-metro"], weight, disabled, bld, yrblt)

    print(
        f"  housing aggregation complete; {stats['missing_geo_lookup_rows']:,} rows lacked geo classification",
        flush=True,
    )
    return segments, stats


def summarize_component(total: float, lower: float, bucket_1990s: float, post1999: float) -> Dict[str, float]:
    pre_trigger_est = lower + PRE_TRIGGER_1990S_FRACTION * bucket_1990s
    post_trigger_est = post1999 + (1 - PRE_TRIGGER_1990S_FRACTION) * bucket_1990s
    return {
        "total": total,
        "pre_trigger_lower_bound": lower,
        "yr1990s_bucket": bucket_1990s,
        "pre_trigger_estimate": pre_trigger_est,
        "post_trigger_estimate": post_trigger_est,
        "pre_trigger_estimate_share": pct(pre_trigger_est, total),
        "post_trigger_estimate_share": pct(post_trigger_est, total),
        "pre_trigger_lower_bound_share": pct(lower, total),
    }


def finalize_size_bucket(raw_bucket: Dict[str, float], total_renters: float, total_disabled: float) -> Dict[str, float]:
    total = raw_bucket["total"]
    disabled = raw_bucket["disabled"]
    summary = summarize_component(
        total=total,
        lower=raw_bucket["pre1990_lower"],
        bucket_1990s=raw_bucket["yr1990s"],
        post1999=raw_bucket["post1999"],
    )
    disabled_summary = summarize_component(
        total=disabled,
        lower=raw_bucket["disabled_pre1990_lower"],
        bucket_1990s=raw_bucket["disabled_yr1990s"],
        post1999=raw_bucket["disabled_post1999"],
    )
    summary.update(
        {
            "share_of_all_renters": pct(total, total_renters),
            "disabled_count": disabled,
            "disabled_share_within_size_bucket": pct(disabled, total),
            "disabled_share_of_all_disabled_renters": pct(disabled, total_disabled),
            "disabled_pre_trigger_estimate": disabled_summary["pre_trigger_estimate"],
            "disabled_post_trigger_estimate": disabled_summary["post_trigger_estimate"],
            "disabled_pre_trigger_share_of_all_disabled_renters": pct(
                disabled_summary["pre_trigger_estimate"], total_disabled
            ),
            "disabled_post_trigger_share_of_all_disabled_renters": pct(
                disabled_summary["post_trigger_estimate"], total_disabled
            ),
        }
    )
    return summary


def build_stock_table_rows(
    raw_table: Dict[str, Dict[str, float]], total_renters: float
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for year_code, year_label in YEAR_BUILT_BUCKETS:
        year_data = raw_table[year_code]
        for bucket_name, spec in STOCK_TABLE_SIZE_BUCKETS.items():
            count = year_data[bucket_name]
            if count <= 0:
                continue
            rows.append(
                {
                    "year_built_category": year_label,
                    "building_size_category": spec["label"],
                    "tenure": "Renter-occupied",
                    "weighted_units": count,
                    "share_of_all_renter_stock": pct(count, total_renters),
                }
            )
    return rows


def combine_raw_size_buckets(raw_buckets: Iterable[Dict[str, float]]) -> Dict[str, float]:
    combined = new_size_bucket_template()
    for bucket in raw_buckets:
        for key in combined:
            combined[key] += bucket[key]
    return combined


def summarize_raw_size_bucket(raw_bucket: Dict[str, float], disabled: bool = False) -> Dict[str, float]:
    if disabled:
        return summarize_component(
            total=raw_bucket["disabled"],
            lower=raw_bucket["disabled_pre1990_lower"],
            bucket_1990s=raw_bucket["disabled_yr1990s"],
            post1999=raw_bucket["disabled_post1999"],
        )
    return summarize_component(
        total=raw_bucket["total"],
        lower=raw_bucket["pre1990_lower"],
        bucket_1990s=raw_bucket["yr1990s"],
        post1999=raw_bucket["post1999"],
    )


def format_component_assumption(labels: List[str]) -> str:
    if not labels:
        return "none of the indeterminate BLD=05 components is treated as exact 4-unit"
    if len(labels) == 1:
        joined = labels[0]
    else:
        joined = ", ".join(labels[:-1]) + f" and {labels[-1]}"
    return f"only {joined} {'is' if len(labels) == 1 else 'are'} treated as exact 4-unit"


def component_share_bounds(
    base_total: float,
    base_pre: float,
    optional_components: List[Tuple[str, float, float]],
) -> Dict[str, object]:
    combos: List[Dict[str, object]] = []
    for mask in range(1 << len(optional_components)):
        total = base_total
        pre = base_pre
        labels: List[str] = []
        for idx, (label, component_total, component_pre) in enumerate(optional_components):
            if mask & (1 << idx):
                total += component_total
                pre += component_pre
                labels.append(label)
        combos.append(
            {
                "total": total,
                "pre_trigger_estimate": pre,
                "share": pct(pre, total),
                "included_components": labels,
            }
        )

    min_combo = min(combos, key=lambda item: item["share"])
    max_combo = max(combos, key=lambda item: item["share"])
    return {
        "minimum_share": min_combo["share"],
        "minimum_pre_trigger_estimate": min_combo["pre_trigger_estimate"],
        "minimum_total": min_combo["total"],
        "minimum_assumption": format_component_assumption(min_combo["included_components"]),
        "maximum_share": max_combo["share"],
        "maximum_pre_trigger_estimate": max_combo["pre_trigger_estimate"],
        "maximum_total": max_combo["total"],
        "maximum_assumption": format_component_assumption(max_combo["included_components"]),
    }


def build_literal_four_plus_bounds(
    raw_segment: Dict[str, object], total_renters: float, total_disabled: float
) -> Dict[str, object]:
    raw_size_buckets = raw_segment["size_buckets"]
    exact_five_plus_raw = combine_raw_size_buckets(
        [
            raw_size_buckets["five_to_nineteen"],
            raw_size_buckets["twenty_to_forty_nine"],
            raw_size_buckets["fifty_plus"],
        ]
    )
    indeterminate_raw = raw_size_buckets["four_unit_proxy"]

    exact_five_plus = summarize_raw_size_bucket(exact_five_plus_raw)
    exact_five_plus_disabled = summarize_raw_size_bucket(exact_five_plus_raw, disabled=True)
    indeterminate = summarize_raw_size_bucket(indeterminate_raw)
    indeterminate_disabled = summarize_raw_size_bucket(indeterminate_raw, disabled=True)

    stock_share_bounds = component_share_bounds(
        base_total=exact_five_plus["total"],
        base_pre=exact_five_plus["pre_trigger_estimate"],
        optional_components=[
            (
                "the BLD=05 pre-1990 component",
                indeterminate_raw["pre1990_lower"],
                indeterminate_raw["pre1990_lower"],
            ),
            (
                "the BLD=05 1990-1999 component",
                indeterminate_raw["yr1990s"],
                PRE_TRIGGER_1990S_FRACTION * indeterminate_raw["yr1990s"],
            ),
            (
                "the BLD=05 post-1999 component",
                indeterminate_raw["post1999"],
                0.0,
            ),
        ],
    )
    disabled_share_bounds = component_share_bounds(
        base_total=exact_five_plus_disabled["total"],
        base_pre=exact_five_plus_disabled["pre_trigger_estimate"],
        optional_components=[
            (
                "the disabled BLD=05 pre-1990 component",
                indeterminate_raw["disabled_pre1990_lower"],
                indeterminate_raw["disabled_pre1990_lower"],
            ),
            (
                "the disabled BLD=05 1990-1999 component",
                indeterminate_raw["disabled_yr1990s"],
                PRE_TRIGGER_1990S_FRACTION * indeterminate_raw["disabled_yr1990s"],
            ),
            (
                "the disabled BLD=05 post-1999 component",
                indeterminate_raw["disabled_post1999"],
                0.0,
            ),
        ],
    )

    lower_disabled_accessibility_deficit = (
        exact_five_plus_disabled["pre_trigger_estimate"]
        + NONCOMPLIANCE_RATE * exact_five_plus_disabled["post_trigger_estimate"]
    )
    upper_disabled_accessibility_deficit = (
        exact_five_plus_disabled["pre_trigger_estimate"]
        + indeterminate_disabled["pre_trigger_estimate"]
        + NONCOMPLIANCE_RATE
        * (
            exact_five_plus_disabled["post_trigger_estimate"]
            + indeterminate_disabled["post_trigger_estimate"]
        )
    )

    return {
        "checked_public_sources": [
            "ACS detailed-table metadata: B25024 and B25032 use a '3 or 4' category; B25127 uses '2 to 4'",
            "Local AHS 2019/2023 public-use metadata: BLD=05 is labeled '3 to 4 apartments'",
        ],
        "exact_size_gap_status": (
            "Public Census products available in this workspace do not point-identify exact 4-unit buildings; "
            "the residual uncertainty is confined to the ACS/AHS BLD=05 bucket."
        ),
        "exact_five_plus_stock_floor": {
            **exact_five_plus,
            "share_of_all_renters": pct(exact_five_plus["total"], total_renters),
            "pre_trigger_share_of_all_renters": pct(exact_five_plus["pre_trigger_estimate"], total_renters),
        },
        "indeterminate_bld05_bucket": {
            **indeterminate,
            "share_of_all_renters": pct(indeterminate["total"], total_renters),
            "pre_trigger_share_of_all_renters": pct(indeterminate["pre_trigger_estimate"], total_renters),
            "disabled_total": indeterminate_disabled["total"],
            "disabled_share_of_all_disabled_renters": pct(indeterminate_disabled["total"], total_disabled),
            "disabled_pre_trigger_estimate": indeterminate_disabled["pre_trigger_estimate"],
            "disabled_post_trigger_estimate": indeterminate_disabled["post_trigger_estimate"],
            "disabled_pre_trigger_share_of_all_disabled_renters": pct(
                indeterminate_disabled["pre_trigger_estimate"], total_disabled
            ),
            "disabled_post_trigger_share_of_all_disabled_renters": pct(
                indeterminate_disabled["post_trigger_estimate"], total_disabled
            ),
        },
        "literal_four_plus_stock_bounds": {
            "total_lower_bound": exact_five_plus["total"],
            "total_upper_bound": exact_five_plus["total"] + indeterminate["total"],
            "share_of_all_renters_lower_bound": pct(exact_five_plus["total"], total_renters),
            "share_of_all_renters_upper_bound": pct(
                exact_five_plus["total"] + indeterminate["total"], total_renters
            ),
            "pre_trigger_estimate_lower_bound": exact_five_plus["pre_trigger_estimate"],
            "pre_trigger_estimate_upper_bound": (
                exact_five_plus["pre_trigger_estimate"] + indeterminate["pre_trigger_estimate"]
            ),
            "pre_trigger_share_of_all_renters_lower_bound": pct(
                exact_five_plus["pre_trigger_estimate"], total_renters
            ),
            "pre_trigger_share_of_all_renters_upper_bound": pct(
                exact_five_plus["pre_trigger_estimate"] + indeterminate["pre_trigger_estimate"],
                total_renters,
            ),
            "pre_trigger_share_within_literal_four_plus_minimum": stock_share_bounds[
                "minimum_share"
            ],
            "pre_trigger_share_within_literal_four_plus_maximum": stock_share_bounds[
                "maximum_share"
            ],
            "minimum_share_assumption": stock_share_bounds["minimum_assumption"],
            "maximum_share_assumption": stock_share_bounds["maximum_assumption"],
        },
        "literal_four_plus_disabled_bounds": {
            "total_lower_bound": exact_five_plus_disabled["total"],
            "total_upper_bound": exact_five_plus_disabled["total"] + indeterminate_disabled["total"],
            "share_of_all_disabled_renters_in_literal_four_plus_lower_bound": pct(
                exact_five_plus_disabled["total"], total_disabled
            ),
            "share_of_all_disabled_renters_in_literal_four_plus_upper_bound": pct(
                exact_five_plus_disabled["total"] + indeterminate_disabled["total"],
                total_disabled,
            ),
            "pre_trigger_estimate_lower_bound": exact_five_plus_disabled["pre_trigger_estimate"],
            "pre_trigger_estimate_upper_bound": (
                exact_five_plus_disabled["pre_trigger_estimate"]
                + indeterminate_disabled["pre_trigger_estimate"]
            ),
            "share_of_all_disabled_renters_pre_trigger_lower_bound": pct(
                exact_five_plus_disabled["pre_trigger_estimate"], total_disabled
            ),
            "share_of_all_disabled_renters_pre_trigger_upper_bound": pct(
                exact_five_plus_disabled["pre_trigger_estimate"]
                + indeterminate_disabled["pre_trigger_estimate"],
                total_disabled,
            ),
            "pre_trigger_share_within_literal_four_plus_minimum": disabled_share_bounds[
                "minimum_share"
            ],
            "pre_trigger_share_within_literal_four_plus_maximum": disabled_share_bounds[
                "maximum_share"
            ],
            "minimum_share_assumption": disabled_share_bounds["minimum_assumption"],
            "maximum_share_assumption": disabled_share_bounds["maximum_assumption"],
            "accessibility_deficit_disabled_households_lower_bound": lower_disabled_accessibility_deficit,
            "accessibility_deficit_disabled_households_upper_bound": upper_disabled_accessibility_deficit,
            "accessibility_deficit_share_of_all_disabled_renters_lower_bound": pct(
                lower_disabled_accessibility_deficit, total_disabled
            ),
            "accessibility_deficit_share_of_all_disabled_renters_upper_bound": pct(
                upper_disabled_accessibility_deficit, total_disabled
            ),
        },
    }


def finalize_segment(raw_segment: Dict[str, object], segment_label: str) -> Dict[str, object]:
    total = raw_segment["total"]
    disabled_total = raw_segment["disabled"]
    all_stock = summarize_component(
        total=total,
        lower=raw_segment["all_pre1990_lower"],
        bucket_1990s=raw_segment["all_yr1990s"],
        post1999=raw_segment["all_post1999"],
    )
    all_stock_disabled = summarize_component(
        total=disabled_total,
        lower=raw_segment["disabled_all_pre1990_lower"],
        bucket_1990s=raw_segment["disabled_all_yr1990s"],
        post1999=raw_segment["disabled_all_post1999"],
    )
    four_plus = summarize_component(
        total=raw_segment["four_plus_total"],
        lower=raw_segment["four_plus_pre1990_lower"],
        bucket_1990s=raw_segment["four_plus_yr1990s"],
        post1999=raw_segment["four_plus_post1999"],
    )
    four_plus_disabled = summarize_component(
        total=raw_segment["four_plus_disabled"],
        lower=raw_segment["four_plus_disabled_pre1990_lower"],
        bucket_1990s=raw_segment["four_plus_disabled_yr1990s"],
        post1999=raw_segment["four_plus_disabled_post1999"],
    )

    disabled_pre_trigger_share = pct(four_plus_disabled["pre_trigger_estimate"], disabled_total)
    disabled_post_trigger_share = pct(four_plus_disabled["post_trigger_estimate"], disabled_total)
    noncompliant_post_trigger_share = disabled_post_trigger_share * NONCOMPLIANCE_RATE
    accessibility_deficit_share = disabled_pre_trigger_share + noncompliant_post_trigger_share

    size_buckets = {
        bucket_name: finalize_size_bucket(bucket_raw, total, disabled_total)
        for bucket_name, bucket_raw in raw_segment["size_buckets"].items()
    }
    literal_four_plus_bounds = build_literal_four_plus_bounds(
        raw_segment=raw_segment,
        total_renters=total,
        total_disabled=disabled_total,
    )

    return {
        "segment": segment_label,
        "total_renter_occupied_units": total,
        "disabled_renter_households": disabled_total,
        "disabled_share_of_all_renters": pct(disabled_total, total),
        "unknown_year_total": raw_segment["unknown_year_total"],
        "unknown_year_disabled": raw_segment["unknown_year_disabled"],
        "all_rental_stock": all_stock,
        "all_rental_stock_disabled": {
            **all_stock_disabled,
            "share_of_all_disabled_renters_pre_trigger_estimate": pct(
                all_stock_disabled["pre_trigger_estimate"], disabled_total
            ),
            "share_of_all_disabled_renters_post_trigger_estimate": pct(
                all_stock_disabled["post_trigger_estimate"], disabled_total
            ),
        },
        "four_plus_proxy_stock": {
            **four_plus,
            "share_of_all_renters": pct(four_plus["total"], total),
            "pre_trigger_share_within_four_plus_proxy": four_plus["pre_trigger_estimate_share"],
            "post_trigger_share_within_four_plus_proxy": four_plus["post_trigger_estimate_share"],
            "pre_trigger_share_of_all_renters": pct(four_plus["pre_trigger_estimate"], total),
            "post_trigger_share_of_all_renters": pct(four_plus["post_trigger_estimate"], total),
        },
        "four_plus_proxy_disabled": {
            **four_plus_disabled,
            "share_of_all_disabled_renters_in_four_plus_proxy": pct(four_plus_disabled["total"], disabled_total),
            "share_of_all_disabled_renters_pre_trigger_estimate": disabled_pre_trigger_share,
            "share_of_all_disabled_renters_post_trigger_estimate": disabled_post_trigger_share,
            "disabled_share_within_pre_trigger_four_plus_proxy": pct(
                four_plus_disabled["pre_trigger_estimate"], four_plus["pre_trigger_estimate"]
            ),
            "disabled_share_within_post_trigger_four_plus_proxy": pct(
                four_plus_disabled["post_trigger_estimate"], four_plus["post_trigger_estimate"]
            ),
            "post_trigger_noncompliant_share_of_all_disabled_renters": noncompliant_post_trigger_share,
            "accessibility_deficit_share_of_all_disabled_renters": accessibility_deficit_share,
            "accessibility_deficit_disabled_households_estimate": (
                four_plus_disabled["pre_trigger_estimate"]
                + NONCOMPLIANCE_RATE * four_plus_disabled["post_trigger_estimate"]
            ),
            "accessibility_deficit_share_within_four_plus_proxy_disabled_households": pct(
                four_plus_disabled["pre_trigger_estimate"]
                + NONCOMPLIANCE_RATE * four_plus_disabled["post_trigger_estimate"],
                four_plus_disabled["total"],
            ),
        },
        "literal_four_plus_bounds": literal_four_plus_bounds,
        "size_buckets": size_buckets,
        "building_stock_by_year_built_size_tenure": build_stock_table_rows(
            raw_segment["building_stock_by_year_built_size_tenure"],
            total,
        ),
    }


def build_results(segments: Dict[str, Dict[str, object]], query_stats: Dict[str, Dict[str, int]]) -> Dict[str, object]:
    finalized = {name: finalize_segment(raw, name) for name, raw in segments.items()}
    overall = finalized["overall"]
    literal = overall["literal_four_plus_bounds"]

    top_line = {
        "all_rental_stock_pre_trigger_estimate_share": overall["all_rental_stock"]["pre_trigger_estimate_share"],
        "literal_four_plus_share_of_all_renters_lower_bound": literal["literal_four_plus_stock_bounds"][
            "share_of_all_renters_lower_bound"
        ],
        "literal_four_plus_share_of_all_renters_upper_bound": literal["literal_four_plus_stock_bounds"][
            "share_of_all_renters_upper_bound"
        ],
        "literal_four_plus_pre_trigger_share_within_minimum": literal["literal_four_plus_stock_bounds"][
            "pre_trigger_share_within_literal_four_plus_minimum"
        ],
        "literal_four_plus_pre_trigger_share_within_maximum": literal["literal_four_plus_stock_bounds"][
            "pre_trigger_share_within_literal_four_plus_maximum"
        ],
        "literal_four_plus_disabled_pre_trigger_share_of_all_disabled_renters_lower_bound": literal[
            "literal_four_plus_disabled_bounds"
        ]["share_of_all_disabled_renters_pre_trigger_lower_bound"],
        "literal_four_plus_disabled_pre_trigger_share_of_all_disabled_renters_upper_bound": literal[
            "literal_four_plus_disabled_bounds"
        ]["share_of_all_disabled_renters_pre_trigger_upper_bound"],
        "literal_four_plus_disabled_pre_trigger_share_within_minimum": literal[
            "literal_four_plus_disabled_bounds"
        ]["pre_trigger_share_within_literal_four_plus_minimum"],
        "literal_four_plus_disabled_pre_trigger_share_within_maximum": literal[
            "literal_four_plus_disabled_bounds"
        ]["pre_trigger_share_within_literal_four_plus_maximum"],
        "literal_four_plus_disabled_accessibility_deficit_share_of_all_disabled_renters_lower_bound": literal[
            "literal_four_plus_disabled_bounds"
        ]["accessibility_deficit_share_of_all_disabled_renters_lower_bound"],
        "literal_four_plus_disabled_accessibility_deficit_share_of_all_disabled_renters_upper_bound": literal[
            "literal_four_plus_disabled_bounds"
        ]["accessibility_deficit_share_of_all_disabled_renters_upper_bound"],
        "four_plus_proxy_share_of_all_renters": overall["four_plus_proxy_stock"]["share_of_all_renters"],
        "four_plus_proxy_pre_trigger_share_within_four_plus": overall["four_plus_proxy_stock"][
            "pre_trigger_share_within_four_plus_proxy"
        ],
        "four_plus_proxy_pre_trigger_share_of_all_renters": overall["four_plus_proxy_stock"][
            "pre_trigger_share_of_all_renters"
        ],
        "disabled_pre_trigger_four_plus_share_of_all_disabled_renters": overall["four_plus_proxy_disabled"][
            "share_of_all_disabled_renters_pre_trigger_estimate"
        ],
        "disabled_post_trigger_four_plus_share_of_all_disabled_renters": overall["four_plus_proxy_disabled"][
            "share_of_all_disabled_renters_post_trigger_estimate"
        ],
        "disabled_pre_trigger_four_plus_households": overall["four_plus_proxy_disabled"][
            "pre_trigger_estimate"
        ],
        "disabled_post_trigger_four_plus_households": overall["four_plus_proxy_disabled"][
            "post_trigger_estimate"
        ],
        "disabled_pre_trigger_four_plus_share_within_multifamily": overall["four_plus_proxy_disabled"][
            "pre_trigger_estimate_share"
        ],
        "disabled_post_trigger_four_plus_share_within_multifamily": overall["four_plus_proxy_disabled"][
            "post_trigger_estimate_share"
        ],
        "disabled_post_trigger_noncompliant_share_of_all_disabled_renters": overall[
            "four_plus_proxy_disabled"
        ]["post_trigger_noncompliant_share_of_all_disabled_renters"],
        "disabled_accessibility_deficit_share_of_all_disabled_renters": overall[
            "four_plus_proxy_disabled"
        ]["accessibility_deficit_share_of_all_disabled_renters"],
        "disabled_accessibility_deficit_share_within_multifamily": overall[
            "four_plus_proxy_disabled"
        ]["accessibility_deficit_share_within_four_plus_proxy_disabled_households"],
    }

    return {
        "analysis_timestamp_utc": now_iso(),
        "data_source": {
            "survey": "ACS 2020-2024 5-Year PUMS",
            "api": BASE_URL,
            "universe": "Renter-occupied householders (TEN=3, SPORDER=1), 50 states + DC; Puerto Rico excluded",
            "weight": "WGTP",
        },
        "methodology": {
            "four_plus_proxy_definition": (
                "BLD=05-09. BLD=05 is the combined 3-4-unit bucket and serves as the closest reproducible proxy for exact 4-unit buildings."
            ),
            "exact_building_size_gap_assessment": overall["literal_four_plus_bounds"][
                "exact_size_gap_status"
            ],
            "checked_public_exact_size_sources": overall["literal_four_plus_bounds"][
                "checked_public_sources"
            ],
            "pre_trigger_fraction_applied_to_1990s_bucket": PRE_TRIGGER_1990S_FRACTION,
            "pre_trigger_fraction_explanation": (
                "437 of 3,652 days in the ACS 1990-1999 YRBLT bucket fall on or before March 13, 1991."
            ),
            "metro_classification": (
                "2020 tract-to-PUMA relationship file plus July 2023 OMB delineation file (2020 standards); PUMA classified metro if a majority of its tracts fall in metropolitan counties."
            ),
            "post_1991_noncompliance_rate": NONCOMPLIANCE_RATE,
            "post_1991_noncompliance_rate_source": NONCOMPLIANCE_RATE_SOURCE,
        },
        "top_line": top_line,
        "overall": overall,
        "by_metro_status": {
            "Metro": finalized["Metro"],
            "Non_metro": finalized["Non-metro"],
        },
        "query_stats": query_stats,
    }


def build_markdown(results: Dict[str, object]) -> str:
    overall = results["overall"]
    metro = results["by_metro_status"]["Metro"]
    nonmetro = results["by_metro_status"]["Non_metro"]
    top = results["top_line"]
    method = results["methodology"]
    literal = overall["literal_four_plus_bounds"]
    literal_stock = literal["literal_four_plus_stock_bounds"]
    literal_disabled = literal["literal_four_plus_disabled_bounds"]
    exact_five_plus_floor = literal["exact_five_plus_stock_floor"]
    indeterminate_bld05 = literal["indeterminate_bld05_bucket"]

    bounds_rows = [
        "| Literal FHA 4+ renter households | {lower} | {upper} |".format(
            lower=fmt_int(literal_stock["total_lower_bound"]),
            upper=fmt_int(literal_stock["total_upper_bound"]),
        ),
        "| Literal FHA 4+ share of all renter households | {lower} | {upper} |".format(
            lower=fmt_pct(literal_stock["share_of_all_renters_lower_bound"]),
            upper=fmt_pct(literal_stock["share_of_all_renters_upper_bound"]),
        ),
        "| Pre-trigger literal FHA 4+ renter households | {lower} | {upper} |".format(
            lower=fmt_int(literal_stock["pre_trigger_estimate_lower_bound"]),
            upper=fmt_int(literal_stock["pre_trigger_estimate_upper_bound"]),
        ),
        "| Pre-trigger literal FHA 4+ share of all renter households | {lower} | {upper} |".format(
            lower=fmt_pct(literal_stock["pre_trigger_share_of_all_renters_lower_bound"]),
            upper=fmt_pct(literal_stock["pre_trigger_share_of_all_renters_upper_bound"]),
        ),
        "| Pre-trigger share within literal FHA 4+ renter universe | {lower} | {upper} |".format(
            lower=fmt_pct(literal_stock["pre_trigger_share_within_literal_four_plus_minimum"]),
            upper=fmt_pct(literal_stock["pre_trigger_share_within_literal_four_plus_maximum"]),
        ),
        "| Disabled renters in pre-trigger literal FHA 4+ multifamily | {lower} | {upper} |".format(
            lower=fmt_int(literal_disabled["pre_trigger_estimate_lower_bound"]),
            upper=fmt_int(literal_disabled["pre_trigger_estimate_upper_bound"]),
        ),
        "| Pre-trigger literal FHA 4+ share of all disabled renters | {lower} | {upper} |".format(
            lower=fmt_pct(literal_disabled["share_of_all_disabled_renters_pre_trigger_lower_bound"]),
            upper=fmt_pct(literal_disabled["share_of_all_disabled_renters_pre_trigger_upper_bound"]),
        ),
        "| Pre-trigger share within literal FHA 4+ disabled universe | {lower} | {upper} |".format(
            lower=fmt_pct(literal_disabled["pre_trigger_share_within_literal_four_plus_minimum"]),
            upper=fmt_pct(literal_disabled["pre_trigger_share_within_literal_four_plus_maximum"]),
        ),
        "| Combined accessible-feature deficit share of all disabled renters | {lower} | {upper} |".format(
            lower=fmt_pct(literal_disabled["accessibility_deficit_share_of_all_disabled_renters_lower_bound"]),
            upper=fmt_pct(literal_disabled["accessibility_deficit_share_of_all_disabled_renters_upper_bound"]),
        ),
    ]

    size_rows = []
    for bucket_name, spec in SIZE_BUCKETS.items():
        data = overall["size_buckets"][bucket_name]
        size_rows.append(
            "| {label} | {count} | {share_all} | {pre_share_within} | {pre_share_all} | {dis_share} |".format(
                label=spec["label"],
                count=fmt_int(data["total"]),
                share_all=fmt_pct(data["share_of_all_renters"]),
                pre_share_within=fmt_pct(data["pre_trigger_estimate_share"]),
                pre_share_all=fmt_pct(pct(data["pre_trigger_estimate"], overall["total_renter_occupied_units"])),
                dis_share=fmt_pct(data["disabled_share_within_size_bucket"]),
            )
        )

    stock_table_rows = []
    for row in overall["building_stock_by_year_built_size_tenure"]:
        stock_table_rows.append(
            "| {year} | {size} | {tenure} | {units} | {share} |".format(
                year=row["year_built_category"],
                size=row["building_size_category"],
                tenure=row["tenure"],
                units=fmt_int(row["weighted_units"]),
                share=fmt_pct(row["share_of_all_renter_stock"]),
            )
        )

    metro_rows = []
    for label, data in [("Metro", metro), ("Non-metro", nonmetro)]:
        metro_rows.append(
            "| {label} | {total} | {share4} | {pre4} | {pre4all} | {dispre} | {dispost} |".format(
                label=label,
                total=fmt_int(data["total_renter_occupied_units"]),
                share4=fmt_pct(data["four_plus_proxy_stock"]["share_of_all_renters"]),
                pre4=fmt_pct(data["four_plus_proxy_stock"]["pre_trigger_share_within_four_plus_proxy"]),
                pre4all=fmt_pct(data["four_plus_proxy_stock"]["pre_trigger_share_of_all_renters"]),
                dispre=fmt_pct(data["four_plus_proxy_disabled"]["share_of_all_disabled_renters_pre_trigger_estimate"]),
                dispost=fmt_pct(data["four_plus_proxy_disabled"]["share_of_all_disabled_renters_post_trigger_estimate"]),
            )
        )

    md = f"""# Pre-1991 statutory accessibility gap analysis

Generated: {results['analysis_timestamp_utc']}

## Question

Estimate what share of the current U.S. renter-occupied housing stock predates the March 13, 1991 FHA design-and-construction trigger and therefore falls outside § 3604(f)(3)(C), then connect that stock split to disabled renter concentration and the 47% post-1991 noncompliance figure already summarized in Appendix H.

## Data and method

- Survey: {results['data_source']['survey']}
- API: `{results['data_source']['api']}`
- Universe: {results['data_source']['universe']}
- Weight: `{results['data_source']['weight']}`
- Disability proxy: householder has ambulatory difficulty (`DPHY=1`) or independent-living difficulty (`DOUT=1`)
- 4+ proxy: {method['four_plus_proxy_definition']}
- Exact-size gap assessment: {method['exact_building_size_gap_assessment']}
- Checked public exact-size sources: {"; ".join(method['checked_public_exact_size_sources'])}
- March 13, 1991 adjustment: {method['pre_trigger_fraction_explanation']} The script reports a strict lower bound and an adjusted estimate; the memo below uses the adjusted estimate unless noted otherwise.
- Metro/non-metro: {method['metro_classification']}
- Post-1991 noncompliance assumption: {NONCOMPLIANCE_RATE:.0%} from {NONCOMPLIANCE_RATE_SOURCE}

## Exact 4-unit gap: strongest defensible bounds

The only unresolved building-size mass is the ACS `BLD=05` bucket. It contains {fmt_int(indeterminate_bld05['total'])} renter households ({fmt_pct(indeterminate_bld05['share_of_all_renters'])} of all renters), and any exact 4-unit cases must be a subset of that bucket. The exact floor from unquestionably covered `5+` buildings is {fmt_int(exact_five_plus_floor['total'])} renter households ({fmt_pct(exact_five_plus_floor['share_of_all_renters'])} of all renters).

| Metric | Minimum | Maximum |
|---|---:|---:|
{chr(10).join(bounds_rows)}

Note: the minimum/maximum values for the “within literal FHA 4+ universe” rows come from all feasible allocations of exact 4-unit buildings across the observed pre-1990, 1990-1999, and post-1999 portions of the indeterminate `BLD=05` bucket. The minimum share occurs when {literal_stock['minimum_share_assumption']}; the maximum occurs when {literal_stock['maximum_share_assumption']}. For disabled-household composition, the corresponding minimum occurs when {literal_disabled['minimum_share_assumption']}; the maximum occurs when {literal_disabled['maximum_share_assumption']}.

## Top-line findings

- Public Census sources checked here do not isolate exact 4-unit buildings, but the remaining uncertainty is bounded: literal FHA 4+ renter stock falls between {fmt_pct(top['literal_four_plus_share_of_all_renters_lower_bound'])} and {fmt_pct(top['literal_four_plus_share_of_all_renters_upper_bound'])} of all renter households.
- Within the literal FHA 4+ renter universe, the pre-trigger share is bounded between {fmt_pct(top['literal_four_plus_pre_trigger_share_within_minimum'])} and {fmt_pct(top['literal_four_plus_pre_trigger_share_within_maximum'])}; the inclusive ACS proxy (`BLD=05-09`) yields {fmt_pct(top['four_plus_proxy_pre_trigger_share_within_four_plus'])}.
- For disabled renters, the pre-trigger share within the literal FHA 4+ universe is bounded between {fmt_pct(top['literal_four_plus_disabled_pre_trigger_share_within_minimum'])} and {fmt_pct(top['literal_four_plus_disabled_pre_trigger_share_within_maximum'])}; the inclusive ACS proxy yields {fmt_pct(top['disabled_pre_trigger_four_plus_share_within_multifamily'])}.
- Share of all disabled renter households living in pre-trigger literal FHA 4+ multifamily: between {fmt_pct(top['literal_four_plus_disabled_pre_trigger_share_of_all_disabled_renters_lower_bound'])} and {fmt_pct(top['literal_four_plus_disabled_pre_trigger_share_of_all_disabled_renters_upper_bound'])}.
- Combined date-gap plus post-1991 noncompliance deficit for all disabled renters is bounded between {fmt_pct(top['literal_four_plus_disabled_accessibility_deficit_share_of_all_disabled_renters_lower_bound'])} and {fmt_pct(top['literal_four_plus_disabled_accessibility_deficit_share_of_all_disabled_renters_upper_bound'])}.
- Inclusive proxy reference point: within the ACS 4+ proxy universe (`BLD=05-09`), {fmt_pct(top['four_plus_proxy_pre_trigger_share_within_four_plus'])} of renter households and {fmt_pct(top['disabled_pre_trigger_four_plus_share_within_multifamily'])} of disabled renter households are estimated to live in pre-trigger structures.

## Core stock counts

| Metric | Estimate |
|---|---:|
| Total renter-occupied units | {fmt_int(overall['total_renter_occupied_units'])} |
| Disabled renter households | {fmt_int(overall['disabled_renter_households'])} |
| Disabled share of all renter households | {fmt_pct(overall['disabled_share_of_all_renters'])} |
| All-stock pre-trigger lower bound (pre-1990 only) | {fmt_pct(overall['all_rental_stock']['pre_trigger_lower_bound_share'])} |
| All-stock pre-trigger adjusted estimate | {fmt_pct(overall['all_rental_stock']['pre_trigger_estimate_share'])} |
| Literal FHA 4+ share of all renter stock, lower bound | {fmt_pct(literal_stock['share_of_all_renters_lower_bound'])} |
| Literal FHA 4+ share of all renter stock, upper bound | {fmt_pct(literal_stock['share_of_all_renters_upper_bound'])} |
| Literal FHA 4+ pre-trigger share within universe, minimum | {fmt_pct(literal_stock['pre_trigger_share_within_literal_four_plus_minimum'])} |
| Literal FHA 4+ pre-trigger share within universe, maximum | {fmt_pct(literal_stock['pre_trigger_share_within_literal_four_plus_maximum'])} |
| 4+ proxy share of all renter stock | {fmt_pct(overall['four_plus_proxy_stock']['share_of_all_renters'])} |
| 4+ proxy pre-trigger lower bound | {fmt_pct(overall['four_plus_proxy_stock']['pre_trigger_lower_bound_share'])} |
| 4+ proxy pre-trigger adjusted estimate | {fmt_pct(overall['four_plus_proxy_stock']['pre_trigger_share_within_four_plus_proxy'])} |
| 4+ proxy pre-trigger share of all renter stock | {fmt_pct(overall['four_plus_proxy_stock']['pre_trigger_share_of_all_renters'])} |

## Building stock by year built × building-size category × tenure

| Year built bucket | Building size category | Tenure | Weighted renter-occupied units | Share of all renter stock |
|---|---|---|---:|---:|
{chr(10).join(stock_table_rows)}

Note: tenure is constant because Prompt 37's universe is renter-occupied households. The `3-4 units` rows use the ACS PUMS `BLD=05` bucket, which necessarily includes some 3-unit structures.

## By building size within the 4+ proxy universe

| Building size bucket | Weighted renter households | Share of all renter stock | Pre-trigger share within bucket | Pre-trigger share of all renter stock | Disabled share within bucket |
|---|---:|---:|---:|---:|---:|
{chr(10).join(size_rows)}

Note: the first row is a `3-4 unit` ACS PUMS bucket that necessarily includes some 3-unit buildings because the public microdata do not isolate exact 4-unit structures.

## Metro vs. non-metro

| Geography | Weighted renter households | 4+ proxy share of all renters | Pre-trigger share within 4+ proxy | Pre-trigger 4+ proxy share of all renters | Disabled pre-trigger 4+ proxy share of disabled renters | Disabled post-trigger 4+ proxy share of disabled renters |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(metro_rows)}

## Disabled-renter statutory gap metrics

| Metric | Estimate |
|---|---:|
| Disabled renters in pre-trigger literal FHA 4+ multifamily, lower bound | {fmt_int(literal_disabled['pre_trigger_estimate_lower_bound'])} |
| Disabled renters in pre-trigger literal FHA 4+ multifamily, upper bound | {fmt_int(literal_disabled['pre_trigger_estimate_upper_bound'])} |
| Share of all disabled renters in pre-trigger literal FHA 4+ multifamily, lower bound | {fmt_pct(literal_disabled['share_of_all_disabled_renters_pre_trigger_lower_bound'])} |
| Share of all disabled renters in pre-trigger literal FHA 4+ multifamily, upper bound | {fmt_pct(literal_disabled['share_of_all_disabled_renters_pre_trigger_upper_bound'])} |
| Share of disabled renters in literal FHA 4+ multifamily who live in pre-trigger structures, minimum | {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_minimum'])} |
| Share of disabled renters in literal FHA 4+ multifamily who live in pre-trigger structures, maximum | {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_maximum'])} |
| Combined accessible-feature deficit share of all disabled renters, lower bound | {fmt_pct(literal_disabled['accessibility_deficit_share_of_all_disabled_renters_lower_bound'])} |
| Combined accessible-feature deficit share of all disabled renters, upper bound | {fmt_pct(literal_disabled['accessibility_deficit_share_of_all_disabled_renters_upper_bound'])} |
| Disabled renters in pre-trigger 4+ proxy multifamily | {fmt_int(overall['four_plus_proxy_disabled']['pre_trigger_estimate'])} |
| Disabled renters in post-trigger 4+ proxy multifamily | {fmt_int(overall['four_plus_proxy_disabled']['post_trigger_estimate'])} |
| Share of disabled renters in 4+ proxy multifamily who live in pre-trigger structures | {fmt_pct(overall['four_plus_proxy_disabled']['pre_trigger_estimate_share'])} |
| Share of disabled renters in 4+ proxy multifamily who live in post-trigger structures | {fmt_pct(overall['four_plus_proxy_disabled']['post_trigger_estimate_share'])} |
| Share of all disabled renters in pre-trigger 4+ proxy multifamily | {fmt_pct(overall['four_plus_proxy_disabled']['share_of_all_disabled_renters_pre_trigger_estimate'])} |
| Share of all disabled renters in post-trigger 4+ proxy multifamily | {fmt_pct(overall['four_plus_proxy_disabled']['share_of_all_disabled_renters_post_trigger_estimate'])} |
| Post-trigger noncompliant share of all disabled renters ({NONCOMPLIANCE_RATE:.0%} x post-trigger share) | {fmt_pct(overall['four_plus_proxy_disabled']['post_trigger_noncompliant_share_of_all_disabled_renters'])} |
| Combined accessible-feature deficit share of all disabled renters | {fmt_pct(overall['four_plus_proxy_disabled']['accessibility_deficit_share_of_all_disabled_renters'])} |
| Combined accessible-feature deficit, disabled households | {fmt_int(overall['four_plus_proxy_disabled']['accessibility_deficit_disabled_households_estimate'])} |
| Combined accessible-feature deficit within disabled 4+ proxy households | {fmt_pct(overall['four_plus_proxy_disabled']['accessibility_deficit_share_within_four_plus_proxy_disabled_households'])} |

## Requested within-multifamily finding

Best exact-size formulation: public Census sources do not point-identify exact 4-unit buildings. For the literal FHA 4+ universe, the share of disabled renters in multifamily housing who live in pre-1991 structures is bounded between {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_minimum'])} and {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_maximum'])}. The corresponding count of disabled renter households living in pre-trigger literal FHA 4+ multifamily is bounded between {fmt_millions(literal_disabled['pre_trigger_estimate_lower_bound'])} and {fmt_millions(literal_disabled['pre_trigger_estimate_upper_bound'])}. The inclusive ACS proxy (`BLD=05-09`) yields {fmt_pct(overall['four_plus_proxy_disabled']['pre_trigger_estimate_share'])} and {fmt_millions(overall['four_plus_proxy_disabled']['pre_trigger_estimate'])}.

## Interpretation for Prompt 37

Using public Census data, the exact 4-unit margin remains irreducible because available ACS and AHS public products collapse it into a combined `3-4` or `2-4` category. But the residual uncertainty is now tightly bounded and explicit. The only unresolved stock is the {fmt_int(indeterminate_bld05['total'])}-household ACS `BLD=05` bucket ({fmt_pct(indeterminate_bld05['share_of_all_renters'])} of all renters). Given that constraint, the literal FHA 4+ renter universe falls between {fmt_pct(literal_stock['share_of_all_renters_lower_bound'])} and {fmt_pct(literal_stock['share_of_all_renters_upper_bound'])} of all renter households, and its pre-trigger share falls between {fmt_pct(literal_stock['pre_trigger_share_within_literal_four_plus_minimum'])} and {fmt_pct(literal_stock['pre_trigger_share_within_literal_four_plus_maximum'])}. For disabled renters, the pre-trigger share of all disabled renter households in literal FHA 4+ multifamily falls between {fmt_pct(literal_disabled['share_of_all_disabled_renters_pre_trigger_lower_bound'])} and {fmt_pct(literal_disabled['share_of_all_disabled_renters_pre_trigger_upper_bound'])}. Applying the Appendix H {NONCOMPLIANCE_RATE:.0%} noncompliance figure to the post-trigger portion yields a combined accessible-feature deficit between {fmt_pct(literal_disabled['accessibility_deficit_share_of_all_disabled_renters_lower_bound'])} and {fmt_pct(literal_disabled['accessibility_deficit_share_of_all_disabled_renters_upper_bound'])} of all disabled renter households.

## Implications for the Note

These estimates sharpen the Note's institutional point without overstating the exact-size evidence. The verification regime matters not just for monitoring whether post-1991 buildings comply with FHA design-and-construction requirements, but also for identifying the scale of the accessibility deficit embedded in the pre-1991 stock. Even under the hard lower-bound construction that counts only unquestionably covered `5+` buildings, {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_minimum'])} of disabled renters in the literal FHA 4+ universe live in pre-trigger structures; under the most inclusive public-data construction, the figure reaches {fmt_pct(literal_disabled['pre_trigger_share_within_literal_four_plus_maximum'])}. That bounded formulation cleanly distinguishes two problems: hidden noncompliance in nominally covered post-1991 buildings and the much larger legacy deficit residing in stock the statute never directly reached.

## Query diagnostics

- Geo lookup rows processed: {results['query_stats']['geo_lookup']['rows_seen']:,}
- Core housing rows processed: {results['query_stats']['core_housing']['rows_seen']:,}
- Geo rows unmatched to metro classification: {results['query_stats']['geo_lookup']['unmatched_puma_rows']:,}
- Housing rows missing geo lookup: {results['query_stats']['core_housing']['missing_geo_lookup_rows']:,}
"""
    return md


def write_outputs(results: Dict[str, object]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_path = os.path.join(RESULTS_DIR, "pre1991_statutory_gap_analysis.json")
    md_path = os.path.join(RESULTS_DIR, "pre1991_statutory_gap_analysis.md")

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(build_markdown(results))

    print(f"Saved JSON to {json_path}", flush=True)
    print(f"Saved memo to {md_path}", flush=True)


def main() -> None:
    started = time.time()
    print("Pre-1991 statutory accessibility gap analysis", flush=True)
    print("Source: ACS 2020-2024 5-Year PUMS", flush=True)
    print(f"Started: {now_iso()}", flush=True)

    puma_metro = build_puma_metro_map()
    serial_to_metro, geo_stats = build_geo_lookup(puma_metro)
    segments, core_stats = aggregate_housing(serial_to_metro)

    if core_stats["rows_seen"] != geo_stats["rows_seen"]:
        raise RuntimeError(
            "Census housing-row count mismatch: "
            f"geo query saw {geo_stats['rows_seen']:,} rows but core housing query saw {core_stats['rows_seen']:,}. "
            "The Census API response was likely truncated; rerun to obtain a complete extract."
        )

    results = build_results(
        segments=segments,
        query_stats={
            "geo_lookup": geo_stats,
            "core_housing": core_stats,
        },
    )
    write_outputs(results)

    elapsed = time.time() - started
    print(f"Completed in {elapsed / 60:.1f} minutes", flush=True)
    print(
        "Top line: literal FHA 4+ pre-trigger share within universe is bounded between "
        f"{fmt_pct(results['top_line']['literal_four_plus_pre_trigger_share_within_minimum'])} and "
        f"{fmt_pct(results['top_line']['literal_four_plus_pre_trigger_share_within_maximum'])}; "
        f"inclusive ACS proxy = {fmt_pct(results['top_line']['four_plus_proxy_pre_trigger_share_within_four_plus'])}.",
        flush=True,
    )


if __name__ == "__main__":
    main()
