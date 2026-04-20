"""
Extended PUMS Cross-Tabulations for Disability-Centered AFFH Note
=================================================================
Produces five cross-tabulation analyses using the same Census API
approach as census_pums_replication.py:

  (a) Metro vs. Non-Metro Disability Cost Burden
  (b) Age-Disability Interaction (working-age vs. elderly)
  (c) Housing Type Distribution by Disability Status
  (d) Joint race × metro/non-metro × housing-type cube
  (e) State-Level Disability Penalty Rankings

Data Source: U.S. Census Bureau, ACS 2020-2024 5-Year PUMS
API Endpoint: https://api.census.gov/data/2024/acs/acs5/pums

Variable Definitions (carried from main replication):
  SPORDER = 1 (householder only)
  TEN = 3 (rented)
  RAC1P: 1=White alone, 2=Black/AA alone, 3=AIAN alone
  DPHY: 1=Ambulatory difficulty, 2=No
  DOUT: 1=Independent living difficulty, 2=No
  GRPIP: Gross rent as % of household income (1-100; 101=not computed)
  PWGTP: Person weight

Additional variables for this script:
  AGEP: Age (0-99)
  BLD:  Units in structure (01-10)
  STATE: State FIPS code
  PUMA:  Public Use Microdata Area code (2020 Census delineation)

Disability definition: DPHY=1 OR DOUT=1 (ambulatory or independent living)
Cost burden: GRPIP > 30 (excluding GRPIP=101)

Analysis conducted April 15, 2026.
"""

import urllib.request
import json
import sys
import time
import csv
import io
import os
import zipfile
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

BASE_URL = "https://api.census.gov/data/2024/acs/acs5/pums"
RACE_LABELS = {1: "White alone", 2: "Black/AA alone", 3: "AIAN alone"}
TRACT_TO_PUMA_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/"
    "2020_Census_Tract_to_2020_PUMA.txt"
)
CBSA_DELINEATION_URL = (
    "https://www2.census.gov/programs-surveys/metro-micro/geographies/"
    "reference-files/2023/delineation-files/list1_2023.xlsx"
)
EXCLUDED_STATE_CODES = {"72"}  # Puerto Rico

STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming", "72": "Puerto Rico",
}

# ── helpers ──────────────────────────────────────────────────────────────

def fetch_pums(variables, filters="", geo="for=state:*"):
    """Fetch PUMS data from Census API with retry logic."""
    url = f"{BASE_URL}?get=PWGTP,{variables}&{geo}&SPORDER=1&TEN=3{filters}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < 2:
                print(f"    [retry {attempt+1}] {e}", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
            else:
                raise


def is_disabled(row, dphy_idx, dout_idx):
    return row[dphy_idx] == "1" or row[dout_idx] == "1"


def pct(num, den):
    return num / den * 100 if den > 0 else 0.0


def download_bytes(url, timeout=120, retries=4):
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            if attempt == retries:
                raise
            wait = 3 * attempt
            print(f"  retrying download after error: {exc} (sleep {wait}s)", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"unreachable download retry loop for {url}")


def parse_xlsx_rows(raw, worksheet_name="xl/worksheets/sheet1.xml"):
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in root.findall(f"{namespace}si"):
                text = "".join((t.text or "") for t in si.findall(f".//{namespace}t"))
                shared_strings.append(text)

        sheet = ET.fromstring(zf.read(worksheet_name))
        for row in sheet.findall(f".//{namespace}row"):
            values = []
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


# ── (a) METRO vs NON-METRO ──────────────────────────────────────────────

def build_puma_metro_map():
    """
    Build a mapping of (STATE_FIPS, PUMA) -> metro/nonmetro.

    Strategy: download tract-to-PUMA crosswalk + county-to-CBSA delineation.
    A PUMA is classified as "metro" if the majority of its component tracts
    fall in counties that belong to a Metropolitan Statistical Area.
    """
    print("  Downloading tract-to-PUMA crosswalk ...", flush=True)
    tract_raw = download_bytes(TRACT_TO_PUMA_URL, timeout=180)
    tract_text = tract_raw.decode("utf-8-sig")

    puma_counties = defaultdict(Counter)
    reader = csv.DictReader(io.StringIO(tract_text))
    for row in reader:
        st = row.get("STATEFP", "")
        co = row.get("COUNTYFP", "")
        puma = row.get("PUMA5CE", "")
        if not st or not co or not puma or st in EXCLUDED_STATE_CODES:
            continue
        puma_counties[(st, puma)][st + co] += 1

    print("  Downloading metropolitan delineation file ...", flush=True)
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
        st = row[state_idx].zfill(2)
        co = row[county_idx].zfill(3)
        if st in EXCLUDED_STATE_CODES:
            continue
        metro_counties.add(st + co)

    print(f"  Metro counties identified: {len(metro_counties)}", flush=True)

    puma_metro = {}
    for (st, puma), county_counts in puma_counties.items():
        total_tracts = sum(county_counts.values())
        metro_tracts = sum(ct for fips, ct in county_counts.items() if fips in metro_counties)
        puma_metro[(st, puma)] = metro_tracts > total_tracts / 2

    metro_count = sum(1 for v in puma_metro.values() if v)
    nonmetro_count = sum(1 for v in puma_metro.values() if not v)
    print(f"  PUMAs classified: {metro_count} metro, {nonmetro_count} non-metro",
          flush=True)
    return puma_metro


def query_metro_nonmetro(puma_metro):
    """
    Cross-tab (a): Metro vs. Non-Metro Disability Cost Burden.
    Queries PUMS at state level with STATE variable to match PUMAs.
    """
    print("\n" + "=" * 65)
    print("Analysis (a): Metro vs. Non-Metro Disability Cost Burden")
    print("=" * 65)

    results = {}

    for race_code, race_label in RACE_LABELS.items():
        print(f"\n  Querying {race_label} (all states) ...", flush=True)
        data = fetch_pums("DPHY,DOUT,GRPIP,PUMA,STATE", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        grpip_idx = header.index("GRPIP")
        puma_idx = header.index("PUMA")
        state_idx = header.index("STATE")

        # Accumulators: [metro/nonmetro][disabled/nondisabled] -> (total, burdened)
        acc = {
            "Metro":    {"dis_total": 0, "dis_burd": 0,
                         "nondis_total": 0, "nondis_burd": 0},
            "Non-metro": {"dis_total": 0, "dis_burd": 0,
                          "nondis_total": 0, "nondis_burd": 0},
        }
        unmatched = 0

        for r in rows:
            weight = int(r[pwgtp_idx])
            grpip = int(r[grpip_idx])
            if grpip == 101:
                continue

            st = r[state_idx]
            puma = r[puma_idx]
            key = (st, puma)

            if key in puma_metro:
                geo = "Metro" if puma_metro[key] else "Non-metro"
            else:
                # PUMA not in crosswalk -- skip (Puerto Rico, etc.)
                unmatched += weight
                continue

            disabled = is_disabled(r, dphy_idx, dout_idx)
            bucket = acc[geo]
            if disabled:
                bucket["dis_total"] += weight
                if grpip > 30:
                    bucket["dis_burd"] += weight
            else:
                bucket["nondis_total"] += weight
                if grpip > 30:
                    bucket["nondis_burd"] += weight

        race_results = {}
        for geo_label, bucket in acc.items():
            dis_rate = pct(bucket["dis_burd"], bucket["dis_total"])
            nondis_rate = pct(bucket["nondis_burd"], bucket["nondis_total"])
            penalty = dis_rate - nondis_rate
            race_results[geo_label] = {
                "disabled_cb_rate": round(dis_rate, 1),
                "nondisabled_cb_rate": round(nondis_rate, 1),
                "disability_penalty_pp": round(penalty, 1),
                "disabled_n": bucket["dis_total"],
                "nondisabled_n": bucket["nondis_total"],
            }
            print(f"    {geo_label}:")
            print(f"      Disabled CB:     {dis_rate:.1f}%  (n={bucket['dis_total']:,})")
            print(f"      Non-disabled CB: {nondis_rate:.1f}%  (n={bucket['nondis_total']:,})")
            print(f"      Penalty:         {penalty:.1f} pp")

        if unmatched:
            print(f"    [Unmatched weight (PR etc.): {unmatched:,}]")

        results[race_label] = race_results

    return results


# ── (b) AGE-DISABILITY INTERACTION ──────────────────────────────────────

def query_age_disability():
    """
    Cross-tab (b): Working-age (18-64) vs. Elderly (65+) disabled renters.
    """
    print("\n" + "=" * 65)
    print("Analysis (b): Age-Disability Interaction (Working-Age vs. Elderly)")
    print("=" * 65)

    results = {}

    for race_code, race_label in RACE_LABELS.items():
        print(f"\n  Querying {race_label} ...", flush=True)
        data = fetch_pums("DPHY,DOUT,GRPIP,AGEP", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        grpip_idx = header.index("GRPIP")
        agep_idx = header.index("AGEP")

        # Age groups: 18-64 (working age), 65+ (elderly)
        groups = {
            "18-64": {"dis_total": 0, "dis_burd": 0,
                      "nondis_total": 0, "nondis_burd": 0},
            "65+":   {"dis_total": 0, "dis_burd": 0,
                      "nondis_total": 0, "nondis_burd": 0},
        }

        for r in rows:
            weight = int(r[pwgtp_idx])
            grpip = int(r[grpip_idx])
            age = int(r[agep_idx])

            if grpip == 101:
                continue
            if age < 18:
                continue

            age_group = "18-64" if age <= 64 else "65+"
            disabled = is_disabled(r, dphy_idx, dout_idx)
            bucket = groups[age_group]
            if disabled:
                bucket["dis_total"] += weight
                if grpip > 30:
                    bucket["dis_burd"] += weight
            else:
                bucket["nondis_total"] += weight
                if grpip > 30:
                    bucket["nondis_burd"] += weight

        race_results = {}
        for age_label, bucket in groups.items():
            dis_rate = pct(bucket["dis_burd"], bucket["dis_total"])
            nondis_rate = pct(bucket["nondis_burd"], bucket["nondis_total"])
            penalty = dis_rate - nondis_rate
            race_results[age_label] = {
                "disabled_cb_rate": round(dis_rate, 1),
                "nondisabled_cb_rate": round(nondis_rate, 1),
                "disability_penalty_pp": round(penalty, 1),
                "disabled_n": bucket["dis_total"],
                "nondisabled_n": bucket["nondis_total"],
            }
            print(f"    {age_label}:")
            print(f"      Disabled CB:     {dis_rate:.1f}%  (n={bucket['dis_total']:,})")
            print(f"      Non-disabled CB: {nondis_rate:.1f}%  (n={bucket['nondis_total']:,})")
            print(f"      Penalty:         {penalty:.1f} pp")

        results[race_label] = race_results

    return results


# ── (c) HOUSING TYPE DISTRIBUTION ───────────────────────────────────────

BLD_LABELS = {
    "01": "Mobile home/trailer",
    "02": "Single-family detached",
    "03": "Single-family attached",
    "04": "2 apartments",
    "05": "3-4 apartments",
    "06": "5-9 apartments",
    "07": "10-19 apartments",
    "08": "20-49 apartments",
    "09": "50+ apartments",
    "10": "Boat/RV/van/etc.",
}

# Aggregated categories for cleaner presentation
# NOTE: Census API returns BLD values without zero-padding (e.g., "2" not "02")
BLD_GROUPS = {
    "Single-family": ["2", "3"],
    "Small multifamily (2-4)": ["4", "5"],
    "Medium multifamily (5-19)": ["6", "7"],
    "Large multifamily (20+)": ["8", "9"],
    "Mobile home": ["1"],
    "Other": ["10", "0"],
}


def query_housing_type():
    """
    Cross-tab (c): Housing type distribution by disability status.
    Also computes cost-burden rates within each housing type.
    """
    print("\n" + "=" * 65)
    print("Analysis (c): Housing Type Distribution by Disability Status")
    print("=" * 65)

    results = {}

    for race_code, race_label in RACE_LABELS.items():
        print(f"\n  Querying {race_label} ...", flush=True)
        data = fetch_pums("DPHY,DOUT,GRPIP,BLD", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        grpip_idx = header.index("GRPIP")
        bld_idx = header.index("BLD")

        # For each BLD group: count total and cost-burdened, by disability
        dis_by_type = {}
        nondis_by_type = {}
        dis_total_all = 0
        nondis_total_all = 0

        for r in rows:
            weight = int(r[pwgtp_idx])
            grpip = int(r[grpip_idx])
            bld = r[bld_idx]
            disabled = is_disabled(r, dphy_idx, dout_idx)

            # Classify into group
            group = "Other"
            for g_label, g_codes in BLD_GROUPS.items():
                if bld in g_codes:
                    group = g_label
                    break

            if disabled:
                dis_total_all += weight
                if group not in dis_by_type:
                    dis_by_type[group] = {"total": 0, "burdened": 0}
                dis_by_type[group]["total"] += weight
                if grpip != 101 and grpip > 30:
                    dis_by_type[group]["burdened"] += weight
            else:
                nondis_total_all += weight
                if group not in nondis_by_type:
                    nondis_by_type[group] = {"total": 0, "burdened": 0}
                nondis_by_type[group]["total"] += weight
                if grpip != 101 and grpip > 30:
                    nondis_by_type[group]["burdened"] += weight

        race_results = {}
        print(f"    {'Type':<28} {'Dis%':>6} {'NonDis%':>8} {'DisCB%':>7} {'NonDisCB%':>10}")
        print(f"    {'-'*28} {'-'*6} {'-'*8} {'-'*7} {'-'*10}")

        for group_label in BLD_GROUPS:
            d = dis_by_type.get(group_label, {"total": 0, "burdened": 0})
            nd = nondis_by_type.get(group_label, {"total": 0, "burdened": 0})
            dis_share = pct(d["total"], dis_total_all)
            nondis_share = pct(nd["total"], nondis_total_all)
            dis_cb = pct(d["burdened"], d["total"])
            nondis_cb = pct(nd["burdened"], nd["total"])

            race_results[group_label] = {
                "disabled_share_pct": round(dis_share, 1),
                "nondisabled_share_pct": round(nondis_share, 1),
                "disabled_cb_rate": round(dis_cb, 1),
                "nondisabled_cb_rate": round(nondis_cb, 1),
                "disabled_n": d["total"],
                "nondisabled_n": nd["total"],
            }
            print(f"    {group_label:<28} {dis_share:>5.1f}% {nondis_share:>7.1f}% "
                  f"{dis_cb:>6.1f}% {nondis_cb:>9.1f}%")

        results[race_label] = race_results

    return results


# ── (d) STATE-LEVEL DISABILITY PENALTY RANKINGS ─────────────────────────

def query_joint_cube(puma_metro):
    """
    Cross-tab (d): race × metro/non-metro × housing type.

    For each race group and metro bucket, computes:
    - disabled and non-disabled housing-type shares within that geo bucket
    - disabled and non-disabled cost-burden rates within that geo/type cell
    - the disability penalty within that geo/type cell

    Distribution shares use all weighted renter records in the geo/type cell.
    Cost-burden rates exclude GRPIP=101, matching the main cost-burden logic.
    """
    print("\n" + "=" * 65)
    print("Analysis (d): Joint race × metro/non-metro × housing type cube")
    print("=" * 65)

    results = {}

    for race_code, race_label in RACE_LABELS.items():
        print(f"\n  Querying {race_label} ...", flush=True)
        data = fetch_pums("DPHY,DOUT,GRPIP,PUMA,STATE,BLD", f"&RAC1P={race_code}")
        header = data[0]
        rows = data[1:]

        pwgtp_idx = header.index("PWGTP")
        dphy_idx = header.index("DPHY")
        dout_idx = header.index("DOUT")
        grpip_idx = header.index("GRPIP")
        puma_idx = header.index("PUMA")
        state_idx = header.index("STATE")
        bld_idx = header.index("BLD")

        geo_totals = {
            "Metro": {"dis_total_all": 0, "nondis_total_all": 0},
            "Non-metro": {"dis_total_all": 0, "nondis_total_all": 0},
        }
        cube = {
            geo: {
                group: {
                    "dis_total_all": 0,
                    "nondis_total_all": 0,
                    "dis_total_cb": 0,
                    "nondis_total_cb": 0,
                    "dis_burd": 0,
                    "nondis_burd": 0,
                }
                for group in BLD_GROUPS
            }
            for geo in ["Metro", "Non-metro"]
        }
        unmatched = 0

        for r in rows:
            weight = int(r[pwgtp_idx])
            st = r[state_idx]
            puma = r[puma_idx]
            key = (st, puma)
            if key not in puma_metro:
                unmatched += weight
                continue

            geo = "Metro" if puma_metro[key] else "Non-metro"
            bld = r[bld_idx]
            grpip = int(r[grpip_idx])
            disabled = is_disabled(r, dphy_idx, dout_idx)

            group = "Other"
            for g_label, g_codes in BLD_GROUPS.items():
                if bld in g_codes:
                    group = g_label
                    break

            cell = cube[geo][group]
            if disabled:
                geo_totals[geo]["dis_total_all"] += weight
                cell["dis_total_all"] += weight
                if grpip != 101:
                    cell["dis_total_cb"] += weight
                    if grpip > 30:
                        cell["dis_burd"] += weight
            else:
                geo_totals[geo]["nondis_total_all"] += weight
                cell["nondis_total_all"] += weight
                if grpip != 101:
                    cell["nondis_total_cb"] += weight
                    if grpip > 30:
                        cell["nondis_burd"] += weight

        race_results = {}
        for geo in ["Metro", "Non-metro"]:
            geo_results = {}
            for group_label in BLD_GROUPS:
                cell = cube[geo][group_label]
                dis_share = pct(cell["dis_total_all"], geo_totals[geo]["dis_total_all"])
                nondis_share = pct(cell["nondis_total_all"], geo_totals[geo]["nondis_total_all"])
                dis_cb = pct(cell["dis_burd"], cell["dis_total_cb"])
                nondis_cb = pct(cell["nondis_burd"], cell["nondis_total_cb"])
                geo_results[group_label] = {
                    "disabled_share_pct": round(dis_share, 1),
                    "nondisabled_share_pct": round(nondis_share, 1),
                    "disabled_cb_rate": round(dis_cb, 1),
                    "nondisabled_cb_rate": round(nondis_cb, 1),
                    "disability_penalty_pp": round(dis_cb - nondis_cb, 1),
                    "disabled_n": cell["dis_total_all"],
                    "nondisabled_n": cell["nondis_total_all"],
                }
            race_results[geo] = geo_results

            lm = geo_results["Large multifamily (20+)"]
            print(f"    {geo}: large multifamily share disabled={lm['disabled_share_pct']:.1f}% nondisabled={lm['nondisabled_share_pct']:.1f}% penalty={lm['disability_penalty_pp']:.1f} pp")

        if unmatched:
            print(f"    [Unmatched weight (PR etc.): {unmatched:,}]")
        results[race_label] = race_results

    return results


# ── (e) STATE-LEVEL DISABILITY PENALTY RANKINGS ─────────────────────────

def query_state_rankings():
    """
    Cross-tab (d): Disability cost-burden penalty by state.
    Uses all renters (all races combined) for adequate sample size.
    Also computes race-specific rankings where feasible.
    """
    print("\n" + "=" * 65)
    print("Analysis (d): State-Level Disability Penalty Rankings")
    print("=" * 65)

    # Query all renters (no RAC1P filter) with STATE variable
    print("  Querying all renters by state ...", flush=True)
    data = fetch_pums("DPHY,DOUT,GRPIP,STATE")
    header = data[0]
    rows = data[1:]

    pwgtp_idx = header.index("PWGTP")
    dphy_idx = header.index("DPHY")
    dout_idx = header.index("DOUT")
    grpip_idx = header.index("GRPIP")
    state_idx = header.index("STATE")

    # Accumulate by state
    state_data = {}
    for r in rows:
        weight = int(r[pwgtp_idx])
        grpip = int(r[grpip_idx])
        st = r[state_idx]

        if grpip == 101:
            continue

        if st not in state_data:
            state_data[st] = {"dis_total": 0, "dis_burd": 0,
                              "nondis_total": 0, "nondis_burd": 0,
                              "dis_n_unwtd": 0, "nondis_n_unwtd": 0}
        disabled = is_disabled(r, dphy_idx, dout_idx)
        bucket = state_data[st]
        if disabled:
            bucket["dis_total"] += weight
            bucket["dis_n_unwtd"] += 1
            if grpip > 30:
                bucket["dis_burd"] += weight
        else:
            bucket["nondis_total"] += weight
            bucket["nondis_n_unwtd"] += 1
            if grpip > 30:
                bucket["nondis_burd"] += weight

    # Compute penalties and rank
    rankings = []
    for st, d in state_data.items():
        state_name = STATE_FIPS.get(st, f"State {st}")
        dis_rate = pct(d["dis_burd"], d["dis_total"])
        nondis_rate = pct(d["nondis_burd"], d["nondis_total"])
        penalty = dis_rate - nondis_rate
        rankings.append({
            "state_fips": st,
            "state_name": state_name,
            "disabled_cb_rate": round(dis_rate, 1),
            "nondisabled_cb_rate": round(nondis_rate, 1),
            "disability_penalty_pp": round(penalty, 1),
            "disabled_n_weighted": d["dis_total"],
            "disabled_n_unweighted": d["dis_n_unwtd"],
        })

    # Sort by penalty descending
    rankings.sort(key=lambda x: x["disability_penalty_pp"], reverse=True)

    # Print top 20 and bottom 5
    print(f"\n  {'Rank':>4} {'State':<22} {'DisCB%':>7} {'NonDisCB%':>10} "
          f"{'Penalty':>8} {'Dis N(unwt)':>12}")
    print(f"  {'-'*4} {'-'*22} {'-'*7} {'-'*10} {'-'*8} {'-'*12}")

    for i, entry in enumerate(rankings[:20]):
        marker = " *" if entry["disability_penalty_pp"] > 8.4 else ""
        print(f"  {i+1:>4} {entry['state_name']:<22} "
              f"{entry['disabled_cb_rate']:>6.1f}% {entry['nondisabled_cb_rate']:>9.1f}% "
              f"{entry['disability_penalty_pp']:>7.1f} pp "
              f"{entry['disabled_n_unweighted']:>11,}{marker}")

    print(f"  {'...':>4}")
    for i, entry in enumerate(rankings[-5:]):
        rank = len(rankings) - 4 + i
        print(f"  {rank:>4} {entry['state_name']:<22} "
              f"{entry['disabled_cb_rate']:>6.1f}% {entry['nondisabled_cb_rate']:>9.1f}% "
              f"{entry['disability_penalty_pp']:>7.1f} pp "
              f"{entry['disabled_n_unweighted']:>11,}")

    # Count states exceeding 8.4 pp racial gap benchmark
    exceed_count = sum(1 for r in rankings if r["disability_penalty_pp"] > 8.4)
    print(f"\n  States where disability penalty exceeds 8.4 pp racial gap: "
          f"{exceed_count}/{len(rankings)}")

    return rankings


# ── MAIN ─────────────────────────────────────────────────────────────────

def main():
    print("Extended PUMS Cross-Tabulations")
    print("Data: ACS 2020-2024 5-Year PUMS")
    print(f"Date: {time.strftime('%B %d, %Y')}")
    print()

    all_results = {}

    # (a) Metro vs. Non-Metro
    print("Building PUMA-to-metro classification ...", flush=True)
    puma_metro = build_puma_metro_map()
    all_results["metro_nonmetro"] = query_metro_nonmetro(puma_metro)

    # (b) Age-Disability Interaction
    all_results["age_disability"] = query_age_disability()

    # (c) Housing Type Distribution
    all_results["housing_type"] = query_housing_type()

    # (d) Joint race × metro/non-metro × housing type cube
    all_results["joint_cube"] = query_joint_cube(puma_metro)

    # (e) State-Level Rankings
    all_results["state_rankings"] = query_state_rankings()

    # Save results as JSON
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(os.path.dirname(script_dir), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "extended_crosstabs_results.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved to: {out_path}")

    print("\n" + "=" * 65)
    print("Extended cross-tabulations complete.")
    print("Source: U.S. Census Bureau, ACS 2020-2024 5-Year PUMS")
    print("API: https://api.census.gov/data/2024/acs/acs5/pums")


if __name__ == "__main__":
    main()
