"""
Census Bureau 2019-2023 ACS 5-Year PUMS Analysis
AIAN Disability Cost-Burden Estimates with Successive-Differences Replication SEs

Queries the Census API state-by-state, merges multi-call results,
and computes cost-burden rates by race for disabled renter householders.
"""
# NOTE: This script uses the 2019-2023 ACS 5-Year vintage (predecessor analysis).
# The authoritative results in the Note use the 2020-2024 ACS 5-Year vintage
# via census_pums_replication.py and pums_costburden_analysis.py.

import urllib.request
import urllib.error
import json
import math
import time
import sys

API_BASE = "https://api.census.gov/data/2023/acs/acs5/pums"

# All FIPS state codes (01-56, skipping gaps)
STATE_FIPS = [
    "01","02","04","05","06","08","09","10","11","12",
    "13","15","16","17","18","19","20","21","22","23",
    "24","25","26","27","28","29","30","31","32","33",
    "34","35","36","37","38","39","40","41","42","44",
    "45","46","47","48","49","50","51","53","54","55",
    "56","72"  # 72 = Puerto Rico
]

# Variables for call 1: core demographics + WGTP + WGTP1-WGTP40
CORE_VARS = ["SERIALNO","SPORDER","TEN","GRPIP","RAC1P","DPHY","DOUT","WGTP"]
REP_WEIGHTS_1 = [f"WGTP{i}" for i in range(1, 41)]   # WGTP1-WGTP40
REP_WEIGHTS_2 = [f"WGTP{i}" for i in range(41, 81)]   # WGTP41-WGTP80

CALL1_VARS = CORE_VARS + REP_WEIGHTS_1  # 8 + 40 = 48 variables
CALL2_VARS = ["SERIALNO"] + REP_WEIGHTS_2  # 1 + 40 = 41 variables


def fetch_api(variables, state_fips, predicates=None, max_retries=3):
    """Fetch data from Census API with retry logic."""
    var_str = ",".join(variables)
    url = f"{API_BASE}?get={var_str}&for=state:{state_fips}"
    if predicates:
        for k, v in predicates.items():
            url += f"&{k}={v}"

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Python/ACS-Research')
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
            return data
        except urllib.error.HTTPError as e:
            if e.code == 204:  # No content
                return None
            print(f"  HTTP {e.code} for state {state_fips} attempt {attempt+1}: {e.reason}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise
        except Exception as e:
            print(f"  Error for state {state_fips} attempt {attempt+1}: {e}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise


def race_group(rac1p):
    """Classify RAC1P into analysis groups."""
    r = int(rac1p)
    if r == 1:
        return "White alone"
    elif r == 2:
        return "Black alone"
    elif r in (3, 4, 5):
        return "AIAN alone"
    else:
        return "All other"


def main():
    print("=" * 80)
    print("Census Bureau 2019-2023 ACS 5-Year PUMS Analysis")
    print("AIAN Disability Cost-Burden Among Renter Householders")
    print("=" * 80)
    print(flush=True)

    # Storage: list of dicts with all person-level data
    all_records = []

    total_states = len(STATE_FIPS)

    for idx, st in enumerate(STATE_FIPS):
        print(f"[{idx+1}/{total_states}] Fetching state {st}...", end=" ", flush=True)

        # -- Call 1: core vars + replicate weights 1-40 --
        # Filter: TEN=3 (renters), SPORDER=1 (householder)
        try:
            data1 = fetch_api(
                CALL1_VARS, st,
                predicates={"TEN": "3", "SPORDER": "1"}
            )
        except Exception as e:
            print(f"FAILED call1: {e}", flush=True)
            continue

        if data1 is None or len(data1) <= 1:
            print("no data", flush=True)
            continue

        header1 = data1[0]
        rows1 = data1[1:]

        # Build dict keyed by SERIALNO for call 1
        serno_idx1 = header1.index("SERIALNO")
        records_by_serno = {}
        for row in rows1:
            serno = row[serno_idx1]
            rec = {}
            for i, col in enumerate(header1):
                if col == "state":
                    continue
                rec[col] = row[i]
            records_by_serno[serno] = rec

        # -- Call 2: SERIALNO + replicate weights 41-80 --
        # Same filters
        try:
            data2 = fetch_api(
                CALL2_VARS, st,
                predicates={"TEN": "3", "SPORDER": "1"}
            )
        except Exception as e:
            print(f"FAILED call2: {e}", flush=True)
            continue

        if data2 is None or len(data2) <= 1:
            print(f"no data in call2 (had {len(rows1)} in call1)", flush=True)
            # Still use call1 data but mark missing weights
            for serno, rec in records_by_serno.items():
                for w in REP_WEIGHTS_2:
                    rec[w] = "0"
                all_records.append(rec)
            continue

        header2 = data2[0]
        rows2 = data2[1:]
        serno_idx2 = header2.index("SERIALNO")

        # Merge call2 into call1 records
        for row in rows2:
            serno = row[serno_idx2]
            if serno in records_by_serno:
                for i, col in enumerate(header2):
                    if col in ("SERIALNO", "state"):
                        continue
                    records_by_serno[serno][col] = row[i]

        # Add to all_records
        for rec in records_by_serno.values():
            all_records.append(rec)

        print(f"{len(rows1)} records", flush=True)

        # Small delay to be nice to the API
        time.sleep(0.3)

    print(f"\nTotal records fetched: {len(all_records)}", flush=True)
    print(flush=True)

    if len(all_records) == 0:
        print("ERROR: No records fetched. Cannot proceed.")
        return

    # ----------------------------------------------------------------
    # Classify records
    # ----------------------------------------------------------------
    # For each record, determine:
    #   - Race group
    #   - Disabled (DPHY=1 OR DOUT=1)
    #   - GRPIP value (gross rent as % of income)
    #   - Cost-burdened (GRPIP > 30 and GRPIP <= 101)
    #   - Severely cost-burdened (GRPIP > 50 and GRPIP <= 101)
    #   - Zero income (GRPIP == 101)

    # Group data structure:
    # groups[race_group] = {
    #   "disabled": { "count_wt": 0, "cb_wt": 0, "scb_wt": 0, "zero_wt": 0,
    #                 "count_unwt": 0, "cb_unwt": 0, "scb_unwt": 0, "zero_unwt": 0,
    #                 "rep_count": [80 floats], "rep_cb": [...], "rep_scb": [...], "rep_zero": [...] },
    #   "nondisabled": { same },
    #   "all": { same }
    # }

    race_groups = ["White alone", "Black alone", "AIAN alone", "All other", "Total"]
    statuses = ["disabled", "nondisabled", "all"]

    def make_bucket():
        return {
            "count_wt": 0.0, "cb_wt": 0.0, "scb_wt": 0.0, "zero_wt": 0.0,
            "count_unwt": 0, "cb_unwt": 0, "scb_unwt": 0, "zero_unwt": 0,
            "rep_count": [0.0]*80, "rep_cb": [0.0]*80, "rep_scb": [0.0]*80, "rep_zero": [0.0]*80
        }

    groups = {}
    for rg in race_groups:
        groups[rg] = {}
        for s in statuses:
            groups[rg][s] = make_bucket()

    missing_weight_count = 0

    for rec in all_records:
        try:
            rac1p = rec.get("RAC1P", "")
            dphy = rec.get("DPHY", "")
            dout = rec.get("DOUT", "")
            grpip_str = rec.get("GRPIP", "")
            wgtp_str = rec.get("WGTP", "0")

            rg = race_group(rac1p)

            # Parse disability
            is_disabled = (str(dphy) == "1" or str(dout) == "1")

            # Parse GRPIP
            grpip = int(grpip_str) if grpip_str not in ("", "N") else -1

            # Parse weight
            wgtp = float(wgtp_str) if wgtp_str not in ("", "N") else 0.0

            # Cost burden flags (GRPIP of 101 means zero/negative income)
            is_cb = grpip > 30 and grpip <= 101
            is_scb = grpip > 50 and grpip <= 101
            is_zero = grpip == 101

            # Replicate weights
            rep_wts = []
            for i in range(1, 81):
                w_str = rec.get(f"WGTP{i}", "0")
                try:
                    rep_wts.append(float(w_str) if w_str not in ("", "N", None) else 0.0)
                except (ValueError, TypeError):
                    rep_wts.append(0.0)
                    missing_weight_count += 1

            # Determine status categories
            if is_disabled:
                status_list = ["disabled", "all"]
            else:
                status_list = ["nondisabled", "all"]

            # Determine race categories
            race_list = [rg, "Total"]

            for race in race_list:
                for status in status_list:
                    b = groups[race][status]
                    b["count_wt"] += wgtp
                    b["count_unwt"] += 1
                    if is_cb:
                        b["cb_wt"] += wgtp
                        b["cb_unwt"] += 1
                    if is_scb:
                        b["scb_wt"] += wgtp
                        b["scb_unwt"] += 1
                    if is_zero:
                        b["zero_wt"] += wgtp
                        b["zero_unwt"] += 1

                    for r in range(80):
                        rw = rep_wts[r]
                        b["rep_count"][r] += rw
                        if is_cb:
                            b["rep_cb"][r] += rw
                        if is_scb:
                            b["rep_scb"][r] += rw
                        if is_zero:
                            b["rep_zero"][r] += rw
        except Exception as e:
            pass  # skip malformed records

    if missing_weight_count > 0:
        print(f"Note: {missing_weight_count} missing/unparseable replicate weight values (set to 0)", flush=True)

    # ----------------------------------------------------------------
    # Compute rates and standard errors
    # ----------------------------------------------------------------
    def compute_rate_and_se(num_wt, denom_wt, rep_num, rep_denom):
        """Compute rate = num/denom and SE using successive-differences replication."""
        if denom_wt == 0:
            return 0.0, 0.0
        rate = num_wt / denom_wt

        sum_sq = 0.0
        for r in range(80):
            if rep_denom[r] == 0:
                rep_rate = 0.0
            else:
                rep_rate = rep_num[r] / rep_denom[r]
            sum_sq += (rep_rate - rate) ** 2

        se = math.sqrt((4.0 / 80.0) * sum_sq)
        return rate, se

    def compute_count_se(est_wt, rep_wts_list):
        """Compute SE for a weighted count."""
        sum_sq = 0.0
        for r in range(80):
            sum_sq += (rep_wts_list[r] - est_wt) ** 2
        se = math.sqrt((4.0 / 80.0) * sum_sq)
        return se

    # ----------------------------------------------------------------
    # Print results
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 1: DISABLED RENTER HOUSEHOLDERS BY RACE - COST BURDEN RATES")
    print("         (Disabled = DPHY=1 OR DOUT=1, Renters = TEN=3, Householders = SPORDER=1)")
    print("=" * 100)
    print(flush=True)

    header_fmt = "{:<15} {:>12} {:>10} {:>14} {:>8} {:>14} {:>8} {:>14} {:>8}"
    row_fmt =    "{:<15} {:>12,} {:>10,} {:>13.1f}% {:>7.3f} {:>13.1f}% {:>7.3f} {:>13.1f}% {:>7.3f}"

    print(header_fmt.format(
        "Race Group", "Wtd Total", "Unwt n",
        "Cost-Burd%", "SE", "Sev CB%", "SE", "Zero Inc%", "SE"
    ))
    print("-" * 100)

    results = {}

    for rg in race_groups:
        b = groups[rg]["disabled"]

        cb_rate, cb_se = compute_rate_and_se(
            b["cb_wt"], b["count_wt"], b["rep_cb"], b["rep_count"])
        scb_rate, scb_se = compute_rate_and_se(
            b["scb_wt"], b["count_wt"], b["rep_scb"], b["rep_count"])
        zero_rate, zero_se = compute_rate_and_se(
            b["zero_wt"], b["count_wt"], b["rep_zero"], b["rep_count"])

        results[rg] = {
            "disabled": {
                "wtd_total": b["count_wt"],
                "unwt_n": b["count_unwt"],
                "cb_rate": cb_rate, "cb_se": cb_se,
                "scb_rate": scb_rate, "scb_se": scb_se,
                "zero_rate": zero_rate, "zero_se": zero_se
            }
        }

        print(row_fmt.format(
            rg, int(b["count_wt"]), b["count_unwt"],
            cb_rate * 100, cb_se * 100,
            scb_rate * 100, scb_se * 100,
            zero_rate * 100, zero_se * 100
        ))

    print(flush=True)

    # ----------------------------------------------------------------
    # Non-disabled rates
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 2: NON-DISABLED RENTER HOUSEHOLDERS BY RACE - COST BURDEN RATES")
    print("=" * 100)
    print(flush=True)

    print(header_fmt.format(
        "Race Group", "Wtd Total", "Unwt n",
        "Cost-Burd%", "SE", "Sev CB%", "SE", "Zero Inc%", "SE"
    ))
    print("-" * 100)

    for rg in race_groups:
        b = groups[rg]["nondisabled"]

        cb_rate, cb_se = compute_rate_and_se(
            b["cb_wt"], b["count_wt"], b["rep_cb"], b["rep_count"])
        scb_rate, scb_se = compute_rate_and_se(
            b["scb_wt"], b["count_wt"], b["rep_scb"], b["rep_count"])
        zero_rate, zero_se = compute_rate_and_se(
            b["zero_wt"], b["count_wt"], b["rep_zero"], b["rep_count"])

        results[rg]["nondisabled"] = {
            "wtd_total": b["count_wt"],
            "unwt_n": b["count_unwt"],
            "cb_rate": cb_rate, "cb_se": cb_se,
            "scb_rate": scb_rate, "scb_se": scb_se,
            "zero_rate": zero_rate, "zero_se": zero_se
        }

        print(row_fmt.format(
            rg, int(b["count_wt"]), b["count_unwt"],
            cb_rate * 100, cb_se * 100,
            scb_rate * 100, scb_se * 100,
            zero_rate * 100, zero_se * 100
        ))

    print(flush=True)

    # ----------------------------------------------------------------
    # Disability penalty
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 3: DISABILITY PENALTY (Disabled Rate - Non-Disabled Rate)")
    print("=" * 100)
    print(flush=True)

    pen_header = "{:<15} {:>16} {:>8} {:>16} {:>8} {:>16} {:>8}"
    pen_row =    "{:<15} {:>15.1f}pp {:>7.3f} {:>15.1f}pp {:>7.3f} {:>15.1f}pp {:>7.3f}"

    print(pen_header.format(
        "Race Group", "CB Penalty", "SE", "SCB Penalty", "SE", "Zero Penalty", "SE"
    ))
    print("-" * 90)

    for rg in race_groups:
        d = groups[rg]["disabled"]
        nd = groups[rg]["nondisabled"]

        # For the penalty SE, we compute the difference of two rates using replication
        def penalty_se(d_num, d_den, d_rnum, d_rden, nd_num, nd_den, nd_rnum, nd_rden):
            if d_den == 0 or nd_den == 0:
                return 0.0, 0.0
            rate_d = d_num / d_den
            rate_nd = nd_num / nd_den
            diff = rate_d - rate_nd

            sum_sq = 0.0
            for r in range(80):
                rd = d_rnum[r] / d_rden[r] if d_rden[r] != 0 else 0.0
                rnd = nd_rnum[r] / nd_rden[r] if nd_rden[r] != 0 else 0.0
                sum_sq += (rd - rnd - diff) ** 2
            se = math.sqrt((4.0 / 80.0) * sum_sq)
            return diff, se

        cb_pen, cb_pen_se = penalty_se(
            d["cb_wt"], d["count_wt"], d["rep_cb"], d["rep_count"],
            nd["cb_wt"], nd["count_wt"], nd["rep_cb"], nd["rep_count"])
        scb_pen, scb_pen_se = penalty_se(
            d["scb_wt"], d["count_wt"], d["rep_scb"], d["rep_count"],
            nd["scb_wt"], nd["count_wt"], nd["rep_scb"], nd["rep_count"])
        zero_pen, zero_pen_se = penalty_se(
            d["zero_wt"], d["count_wt"], d["rep_zero"], d["rep_count"],
            nd["zero_wt"], nd["count_wt"], nd["rep_zero"], nd["rep_count"])

        print(pen_row.format(
            rg,
            cb_pen * 100, cb_pen_se * 100,
            scb_pen * 100, scb_pen_se * 100,
            zero_pen * 100, zero_pen_se * 100
        ))

    print(flush=True)

    # ----------------------------------------------------------------
    # ALL renter householders (disabled + nondisabled)
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 4: ALL RENTER HOUSEHOLDERS BY RACE - COST BURDEN RATES")
    print("=" * 100)
    print(flush=True)

    print(header_fmt.format(
        "Race Group", "Wtd Total", "Unwt n",
        "Cost-Burd%", "SE", "Sev CB%", "SE", "Zero Inc%", "SE"
    ))
    print("-" * 100)

    for rg in race_groups:
        b = groups[rg]["all"]

        cb_rate, cb_se = compute_rate_and_se(
            b["cb_wt"], b["count_wt"], b["rep_cb"], b["rep_count"])
        scb_rate, scb_se = compute_rate_and_se(
            b["scb_wt"], b["count_wt"], b["rep_scb"], b["rep_count"])
        zero_rate, zero_se = compute_rate_and_se(
            b["zero_wt"], b["count_wt"], b["rep_zero"], b["rep_count"])

        print(row_fmt.format(
            rg, int(b["count_wt"]), b["count_unwt"],
            cb_rate * 100, cb_se * 100,
            scb_rate * 100, scb_se * 100,
            zero_rate * 100, zero_se * 100
        ))

    print(flush=True)

    # ----------------------------------------------------------------
    # 1-Year vs 5-Year comparison for AIAN
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 5: KEY COMPARISON - AIAN DISABLED RENTER HOUSEHOLDERS")
    print("          1-Year (2023) vs 5-Year (2019-2023)")
    print("=" * 100)
    print(flush=True)

    aian_d = results.get("AIAN alone", {}).get("disabled", {})

    print(f"{'Metric':<35} {'1-Year (2023)':>18} {'5-Year (2019-2023)':>20}")
    print("-" * 75)
    print(f"{'Unweighted sample size (n)':<35} {'670':>18} {aian_d.get('unwt_n', 0):>20,}")
    print(f"{'Weighted total':<35} {'~':>18} {int(aian_d.get('wtd_total', 0)):>20,}")
    print(f"{'Cost-burdened rate':<35} {'~%':>18} {aian_d.get('cb_rate', 0)*100:>19.1f}%")
    print(f"{'Cost-burden SE':<35} {'~':>18} {aian_d.get('cb_se', 0)*100:>19.3f}%")
    print(f"{'Severely cost-burdened rate':<35} {'~17.7%':>18} {aian_d.get('scb_rate', 0)*100:>19.1f}%")
    print(f"{'Severe cost-burden SE':<35} {'1.280%':>18} {aian_d.get('scb_se', 0)*100:>19.3f}%")
    print(f"{'Zero/negative income rate':<35} {'~%':>18} {aian_d.get('zero_rate', 0)*100:>19.1f}%")
    print(f"{'Zero income SE':<35} {'~':>18} {aian_d.get('zero_se', 0)*100:>19.3f}%")
    print()

    # Confidence interval comparison
    if aian_d.get('scb_se', 0) > 0:
        scb5 = aian_d['scb_rate'] * 100
        se5 = aian_d['scb_se'] * 100
        scb1 = 17.7
        se1 = 1.280
        print(f"AIAN Severe Cost-Burden 95% CI (1-Year): {scb1:.1f}% +/- {1.96*se1:.2f}% = [{scb1 - 1.96*se1:.1f}%, {scb1 + 1.96*se1:.1f}%]")
        print(f"AIAN Severe Cost-Burden 95% CI (5-Year): {scb5:.1f}% +/- {1.96*se5:.2f}% = [{scb5 - 1.96*se5:.1f}%, {scb5 + 1.96*se5:.1f}%]")
        print(f"SE reduction factor (1yr/5yr): {se1/se5:.2f}x")

    print(flush=True)

    # ----------------------------------------------------------------
    # Summary statistics
    # ----------------------------------------------------------------
    print("=" * 100)
    print("SECTION 6: SUMMARY STATISTICS")
    print("=" * 100)
    print(flush=True)

    total_all = groups["Total"]["all"]
    total_dis = groups["Total"]["disabled"]
    print(f"Total renter householders in sample (unweighted): {total_all['count_unwt']:,}")
    print(f"Total renter householders (weighted): {int(total_all['count_wt']):,}")
    print(f"Total disabled renter householders (unweighted): {total_dis['count_unwt']:,}")
    print(f"Total disabled renter householders (weighted): {int(total_dis['count_wt']):,}")
    print(f"Disability rate among renter HHers: {total_dis['count_wt']/total_all['count_wt']*100:.1f}%")
    print(flush=True)

    for rg in ["White alone", "Black alone", "AIAN alone", "All other"]:
        d = groups[rg]["disabled"]
        a = groups[rg]["all"]
        print(f"{rg}: {d['count_unwt']:,} disabled renter HHers (unwt), "
              f"{int(d['count_wt']):,} (wtd), "
              f"disability rate = {d['count_wt']/a['count_wt']*100:.1f}%")

    print(flush=True)
    print("Analysis complete.", flush=True)


if __name__ == "__main__":
    main()
