"""
Export ACS PUMS renter householder data to CSV files.
Fetches from Census API and saves raw microdata for replication.

Outputs:
  - pums_1year_2023_renters.csv  (2023 ACS 1-Year, ~337K records)
  - pums_5year_2023_renters.csv  (2019-2023 ACS 5-Year, ~1.6M records, state-by-state)
"""

import urllib.request
import urllib.error
import json
import csv
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RESULTS_DIR
OUTPUT_DIR = RESULTS_DIR
OUTPUT_DIR_LOCAL = RESULTS_DIR

API_1YR = "https://api.census.gov/data/2023/acs/acs1/pums"
API_5YR = "https://api.census.gov/data/2023/acs/acs5/pums"

CORE_VARS = ["SERIALNO","SPORDER","TEN","GRPIP","RAC1P","DPHY","DOUT","WGTP","PWGTP"]
REP_W1 = [f"WGTP{i}" for i in range(1, 41)]
REP_W2 = [f"WGTP{i}" for i in range(41, 81)]

STATE_FIPS = [
    "01","02","04","05","06","08","09","10","11","12",
    "13","15","16","17","18","19","20","21","22","23",
    "24","25","26","27","28","29","30","31","32","33",
    "34","35","36","37","38","39","40","41","42","44",
    "45","46","47","48","49","50","51","53","54","55",
    "56","72"
]

def fetch_api(base_url, variables, predicates="", geo=""):
    """Fetch from Census API, return list of dicts."""
    var_str = ",".join(variables)
    url = f"{base_url}?get={var_str}{predicates}{geo}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "PUMS-Research/1.0")
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            headers = data[0]
            rows = data[1:]
            return [dict(zip(headers, row)) for row in rows]
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
            else:
                print(f"  FAILED after 3 attempts: {e}", file=sys.stderr)
                return []

def merge_on_serialno(core_rows, rep1_rows, rep2_rows):
    """Merge three API call results on SERIALNO."""
    rep1_map = {r["SERIALNO"]: r for r in rep1_rows}
    rep2_map = {r["SERIALNO"]: r for r in rep2_rows}
    merged = []
    for row in core_rows:
        sn = row["SERIALNO"]
        if sn in rep1_map and sn in rep2_map:
            combined = {**row, **rep1_map[sn], **rep2_map[sn]}
            merged.append(combined)
    return merged

def export_1year():
    """Fetch and save 1-Year PUMS."""
    outpath = os.path.join(OUTPUT_DIR, "pums_1year_2023_renters.csv")
    print(f"\n{'='*70}")
    print("Fetching 2023 ACS 1-Year PUMS (all states at once)...")
    print(f"{'='*70}\n")

    pred = "&TEN=3&SPORDER=1"

    print("  Call 1/3: Core variables...")
    core = fetch_api(API_1YR, CORE_VARS, pred)
    print(f"    {len(core)} records")

    print("  Call 2/3: Replicate weights 1-40...")
    rep1 = fetch_api(API_1YR, ["SERIALNO"] + REP_W1, pred)
    print(f"    {len(rep1)} records")

    print("  Call 3/3: Replicate weights 41-80...")
    rep2 = fetch_api(API_1YR, ["SERIALNO"] + REP_W2, pred)
    print(f"    {len(rep2)} records")

    merged = merge_on_serialno(core, rep1, rep2)
    print(f"\n  Merged: {len(merged)} records")

    if not merged:
        print("  ERROR: No data to save!")
        return

    # Define column order
    all_cols = CORE_VARS + [f"WGTP{i}" for i in range(1, 81)] + ["PWGTP", "state"]
    # Use whatever columns exist in the data
    actual_cols = [c for c in all_cols if c in merged[0]]
    # Add any extra columns not in our list
    for c in merged[0]:
        if c not in actual_cols:
            actual_cols.append(c)

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=actual_cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(merged)

    size_mb = os.path.getsize(outpath) / (1024 * 1024)
    print(f"\n  Saved: {outpath}")
    print(f"  Size: {size_mb:.1f} MB, {len(merged)} rows, {len(actual_cols)} columns")

def export_5year():
    """Fetch and save 5-Year PUMS state-by-state."""
    outpath = os.path.join(OUTPUT_DIR, "pums_5year_2023_renters.csv")
    print(f"\n{'='*70}")
    print("Fetching 2019-2023 ACS 5-Year PUMS (state-by-state)...")
    print(f"{'='*70}\n")

    pred = "&TEN=3&SPORDER=1"
    total_records = 0
    first_state = True

    with open(outpath, "w", newline="", encoding="utf-8") as f:
        writer = None

        for i, fips in enumerate(STATE_FIPS, 1):
            geo = f"&for=state:{fips}"
            print(f"  [{i}/{len(STATE_FIPS)}] State {fips}...", end=" ", flush=True)

            core = fetch_api(API_5YR, CORE_VARS, pred, geo)
            if not core:
                print("SKIPPED (no data)")
                continue

            rep1 = fetch_api(API_5YR, ["SERIALNO"] + REP_W1, pred, geo)
            rep2 = fetch_api(API_5YR, ["SERIALNO"] + REP_W2, pred, geo)

            merged = merge_on_serialno(core, rep1, rep2)
            print(f"{len(merged)} records")

            if not merged:
                continue

            if first_state:
                all_cols = CORE_VARS + [f"WGTP{i}" for i in range(1, 81)] + ["PWGTP", "state"]
                actual_cols = [c for c in all_cols if c in merged[0]]
                for c in merged[0]:
                    if c not in actual_cols:
                        actual_cols.append(c)
                writer = csv.DictWriter(f, fieldnames=actual_cols, extrasaction="ignore")
                writer.writeheader()
                first_state = False

            writer.writerows(merged)
            total_records += len(merged)

            # Rate limit
            time.sleep(0.5)

    size_mb = os.path.getsize(outpath) / (1024 * 1024)
    print(f"\n  Saved: {outpath}")
    print(f"  Size: {size_mb:.1f} MB, {total_records} rows")

if __name__ == "__main__":
    print("PUMS Data Export to CSV")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] == "--1year-only":
        export_1year()
    elif len(sys.argv) > 1 and sys.argv[1] == "--5year-only":
        export_5year()
    else:
        export_1year()
        export_5year()

    print("\nDone.")
