"""
Census Bureau ACS 2023 1-Year PUMS Analysis:
Cost-Burdened Disabled Renters - National Estimates with Standard Errors

Uses successive-differences replication for standard errors.
"""

import requests
import sys
import math
from collections import defaultdict

API_BASE = "https://api.census.gov/data/2023/acs/acs1/pums"

def fetch_pums_chunk(variables, predicates=None):
    """Fetch a chunk of variables from the PUMS API."""
    params = {
        "get": ",".join(variables),
    }
    if predicates:
        params["ucgid"] = "0100000US"  # National level
        # Build predicate string
        pred_parts = []
        for k, v in predicates.items():
            pred_parts.append(f"{k}={v}")
        # Use the PUMS predicate approach

    # For PUMS, filtering is done differently - use the predicate parameter
    url = API_BASE
    get_str = ",".join(variables)

    # Build URL with predicates
    full_url = f"{url}?get={get_str}&ucgid=0100000US"
    if predicates:
        for k, v in predicates.items():
            full_url += f"&{k}={v}"

    print(f"  Fetching {len(variables)} variables... ", end="", flush=True)
    resp = requests.get(full_url, timeout=120)
    print(f"Status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"  Error response: {resp.text[:500]}")
        return None

    data = resp.json()
    headers = data[0]
    rows = data[1:]
    return headers, rows

def main():
    print("=" * 80)
    print("ACS 2023 1-Year PUMS: Cost-Burdened Disabled Renters Analysis")
    print("=" * 80)
    print()

    # Define variable groups - need to stay under 50 per call
    # Core variables needed on every call for merging
    merge_key = ["SERIALNO", "SPORDER"]

    # Group 1: Core demographic + housing variables
    core_vars = ["SERIALNO", "SPORDER", "TEN", "GRPIP", "RAC1P", "DPHY", "DOUT", "WGTP", "PWGTP"]

    # Group 2: Replicate weights 1-40
    rep_weights_1 = ["SERIALNO", "SPORDER"] + [f"WGTP{i}" for i in range(1, 41)]

    # Group 3: Replicate weights 41-80
    rep_weights_2 = ["SERIALNO", "SPORDER"] + [f"WGTP{i}" for i in range(41, 81)]

    predicates = {"TEN": "3", "SPORDER": "1"}

    print("Step 1: Fetching data from Census API...")
    print(f"  Filter: TEN=3 (renters), SPORDER=1 (householder)")
    print()

    # Fetch core variables
    print("  --- Call 1: Core variables ---")
    result1 = fetch_pums_chunk(core_vars, predicates)
    if result1 is None:
        print("Failed to fetch core variables. Exiting.")
        sys.exit(1)
    headers1, rows1 = result1
    print(f"  Retrieved {len(rows1)} records")

    # Fetch replicate weights group 1
    print("  --- Call 2: Replicate weights 1-40 ---")
    result2 = fetch_pums_chunk(rep_weights_1, predicates)
    if result2 is None:
        print("Failed to fetch replicate weights 1-40. Exiting.")
        sys.exit(1)
    headers2, rows2 = result2
    print(f"  Retrieved {len(rows2)} records")

    # Fetch replicate weights group 2
    print("  --- Call 3: Replicate weights 41-80 ---")
    result3 = fetch_pums_chunk(rep_weights_2, predicates)
    if result3 is None:
        print("Failed to fetch replicate weights 41-80. Exiting.")
        sys.exit(1)
    headers3, rows3 = result3
    print(f"  Retrieved {len(rows3)} records")

    # Build lookup dicts keyed on SERIALNO+SPORDER
    print()
    print("Step 2: Merging datasets...")

    def build_dict(headers, rows):
        d = {}
        sn_idx = headers.index("SERIALNO")
        sp_idx = headers.index("SPORDER")
        for row in rows:
            key = (row[sn_idx], row[sp_idx])
            d[key] = {h: row[i] for i, h in enumerate(headers)}
        return d

    dict1 = build_dict(headers1, rows1)
    dict2 = build_dict(headers2, rows2)
    dict3 = build_dict(headers3, rows3)

    # Merge all into one record per householder
    records = []
    missing_count = 0
    for key, core in dict1.items():
        if key not in dict2 or key not in dict3:
            missing_count += 1
            continue
        merged = {}
        merged.update(core)
        merged.update(dict2[key])
        merged.update(dict3[key])
        records.append(merged)

    print(f"  Merged records: {len(records)}")
    if missing_count > 0:
        print(f"  Records dropped (missing replicate weights): {missing_count}")
    print()

    # Parse numeric fields
    print("Step 3: Parsing and classifying records...")

    parsed = []
    for r in records:
        try:
            rec = {}
            rec["WGTP"] = int(r["WGTP"])
            rec["GRPIP"] = int(r["GRPIP"]) if r["GRPIP"] not in ("", None) else -1
            rec["RAC1P"] = int(r["RAC1P"]) if r["RAC1P"] not in ("", None) else -1
            rec["DPHY"] = int(r["DPHY"]) if r["DPHY"] not in ("", None, "N/A") else 0
            rec["DOUT"] = int(r["DOUT"]) if r["DOUT"] not in ("", None, "N/A") else 0
            rec["rep_weights"] = []
            for i in range(1, 81):
                wk = f"WGTP{i}"
                rec["rep_weights"].append(int(r[wk]))
            parsed.append(rec)
        except (ValueError, KeyError) as e:
            pass  # skip unparseable

    print(f"  Parsed records: {len(parsed)}")

    # Classify disability
    for rec in parsed:
        rec["has_disability"] = (rec["DPHY"] == 1 or rec["DOUT"] == 1)
        if rec["DPHY"] == 1 and rec["DOUT"] == 1:
            rec["disab_type"] = "both"
        elif rec["DPHY"] == 1:
            rec["disab_type"] = "ambulatory_only"
        elif rec["DOUT"] == 1:
            rec["disab_type"] = "indepliving_only"
        else:
            rec["disab_type"] = "none"

    # Classify race
    for rec in parsed:
        rac = rec["RAC1P"]
        if rac == 1:
            rec["race_cat"] = "White alone"
        elif rac == 2:
            rec["race_cat"] = "Black alone"
        elif rac in (3, 4, 5):
            rec["race_cat"] = "AIAN alone"
        else:
            rec["race_cat"] = "All other"

    # Classify cost burden
    for rec in parsed:
        grpip = rec["GRPIP"]
        if grpip == 101:
            rec["cb_cat"] = "not_computed"
        elif grpip > 50:
            rec["cb_cat"] = "severe"
        elif grpip > 30:
            rec["cb_cat"] = "moderate"  # 31-50
        else:
            rec["cb_cat"] = "not_burdened"

    # Count disabled renters
    disabled_recs = [r for r in parsed if r["has_disability"]]
    print(f"  Disabled renter householders: {len(disabled_recs)} (unweighted)")
    print()

    # ---- Computation functions ----

    def weighted_count(subset, weight_field="WGTP"):
        """Compute weighted count using WGTP."""
        return sum(r[weight_field] for r in subset)

    def weighted_count_rep(subset, rep_index):
        """Compute weighted count using replicate weight r (0-indexed)."""
        return sum(r["rep_weights"][rep_index] for r in subset)

    def compute_se(subset):
        """Compute standard error using successive-differences replication."""
        estimate = weighted_count(subset)
        sum_sq = 0.0
        for r_idx in range(80):
            est_r = weighted_count_rep(subset, r_idx)
            sum_sq += (est_r - estimate) ** 2
        se = math.sqrt((4.0 / 80.0) * sum_sq)
        return se

    def compute_estimate_and_se(subset):
        est = weighted_count(subset)
        se = compute_se(subset)
        return est, se

    def fmt(val):
        """Format number with commas."""
        return f"{val:,.0f}"

    def fmt_pct(num, denom):
        if denom == 0:
            return "N/A"
        return f"{100.0 * num / denom:.1f}%"

    # ---- Compute all estimates ----

    print("Step 4: Computing weighted estimates and standard errors...")
    print("  (This may take a moment for replicate-weight SEs)")
    print()

    # Total renters (all parsed, since we filtered TEN=3, SPORDER=1)
    total_renters_est = weighted_count(parsed)

    # A. Overall disabled renter counts
    all_disabled = [r for r in parsed if r["has_disability"]]
    disabled_cost_eligible = [r for r in all_disabled if r["GRPIP"] != 101]  # exclude not-computed
    disabled_not_computed = [r for r in all_disabled if r["GRPIP"] == 101]
    disabled_burdened = [r for r in all_disabled if r["cb_cat"] in ("moderate", "severe")]
    disabled_severe = [r for r in all_disabled if r["cb_cat"] == "severe"]
    disabled_moderate = [r for r in all_disabled if r["cb_cat"] == "moderate"]

    results = {}

    print("  Computing overall totals...")
    results["total_renters"] = (weighted_count(parsed), 0)  # skip SE for total renters
    results["total_disabled"] = compute_estimate_and_se(all_disabled)
    results["disabled_cost_eligible"] = compute_estimate_and_se(disabled_cost_eligible)
    results["disabled_not_computed"] = compute_estimate_and_se(disabled_not_computed)
    results["disabled_burdened"] = compute_estimate_and_se(disabled_burdened)
    results["disabled_moderate"] = compute_estimate_and_se(disabled_moderate)
    results["disabled_severe"] = compute_estimate_and_se(disabled_severe)

    # B. By race
    race_cats = ["White alone", "Black alone", "AIAN alone", "All other"]
    race_results = {}

    print("  Computing by race...")
    for race in race_cats:
        sub_disabled = [r for r in all_disabled if r["race_cat"] == race]
        sub_burdened = [r for r in sub_disabled if r["cb_cat"] in ("moderate", "severe")]
        sub_severe = [r for r in sub_disabled if r["cb_cat"] == "severe"]
        sub_not_computed = [r for r in sub_disabled if r["GRPIP"] == 101]

        race_results[race] = {
            "disabled": compute_estimate_and_se(sub_disabled),
            "burdened": compute_estimate_and_se(sub_burdened),
            "severe": compute_estimate_and_se(sub_severe),
            "not_computed": compute_estimate_and_se(sub_not_computed),
        }

    # C. By disability type
    disab_types = ["ambulatory_only", "indepliving_only", "both"]
    disab_labels = {
        "ambulatory_only": "Ambulatory only (DPHY=1, DOUT=0)",
        "indepliving_only": "Indep. living only (DPHY=0, DOUT=1)",
        "both": "Both (DPHY=1, DOUT=1)",
    }
    disab_results = {}

    print("  Computing by disability type...")
    for dtype in disab_types:
        sub = [r for r in parsed if r["disab_type"] == dtype]
        sub_burdened = [r for r in sub if r["cb_cat"] in ("moderate", "severe")]
        sub_severe = [r for r in sub if r["cb_cat"] == "severe"]
        sub_not_computed = [r for r in sub if r["GRPIP"] == 101]

        disab_results[dtype] = {
            "total": compute_estimate_and_se(sub),
            "burdened": compute_estimate_and_se(sub_burdened),
            "severe": compute_estimate_and_se(sub_severe),
            "not_computed": compute_estimate_and_se(sub_not_computed),
        }

    # ---- Print results ----

    print()
    print("=" * 90)
    print("RESULTS: ACS 2023 1-Year PUMS — Disabled Renter Householders, National Estimates")
    print("=" * 90)
    print()

    print("-" * 90)
    print("A. OVERALL SUMMARY")
    print("-" * 90)

    def print_row(label, est, se, denom_est=None):
        pct_str = ""
        if denom_est and denom_est > 0:
            pct_str = f"  ({100.0 * est / denom_est:5.1f}%)"
        moe = 1.645 * se  # 90% MOE
        print(f"  {label:<52s} {fmt(est):>14s}  ± {fmt(se):>10s}{pct_str}")

    e, s = results["total_renters"]
    print(f"  {'Total renter householders (all)':<52s} {fmt(e):>14s}")

    e_d, s_d = results["total_disabled"]
    print_row("Disabled renter householders (DPHY=1 or DOUT=1)", e_d, s_d, e)

    e_ce, s_ce = results["disabled_cost_eligible"]
    print_row("  With computable GRPIP (excl. 101)", e_ce, s_ce, e_d)

    e_nc, s_nc = results["disabled_not_computed"]
    print_row("  GRPIP=101 (not computed/zero income)", e_nc, s_nc, e_d)

    print()
    e_b, s_b = results["disabled_burdened"]
    print_row("Cost-burdened (GRPIP > 30)", e_b, s_b, e_d)

    e_m, s_m = results["disabled_moderate"]
    print_row("  Moderately burdened (GRPIP 31-50)", e_m, s_m, e_d)

    e_sv, s_sv = results["disabled_severe"]
    print_row("  Severely burdened (GRPIP > 50)", e_sv, s_sv, e_d)

    print()
    print(f"  Cost-burden rate among disabled renters:  {100.0 * e_b / e_d:.1f}%")
    print(f"  Severe cost-burden rate:                  {100.0 * e_sv / e_d:.1f}%")
    if e_ce > 0:
        print(f"  Cost-burden rate (excl. GRPIP=101):       {100.0 * e_b / e_ce:.1f}%")

    print()
    print("-" * 90)
    print("B. BY RACE")
    print("-" * 90)
    print(f"  {'Category':<25s} {'Disabled':>14s} {'Cost-Burd':>14s} {'Severe':>14s} {'GRPIP=101':>14s}")
    print(f"  {'':25s} {'(SE)':>14s} {'(SE)':>14s} {'(SE)':>14s} {'(SE)':>14s}")
    print("  " + "-" * 84)

    for race in race_cats:
        rd = race_results[race]
        d_e, d_s = rd["disabled"]
        b_e, b_s = rd["burdened"]
        sv_e, sv_s = rd["severe"]
        nc_e, nc_s = rd["not_computed"]

        print(f"  {race:<25s} {fmt(d_e):>14s} {fmt(b_e):>14s} {fmt(sv_e):>14s} {fmt(nc_e):>14s}")
        print(f"  {'':25s} ({fmt(d_s):>10s}) ({fmt(b_s):>10s}) ({fmt(sv_s):>10s}) ({fmt(nc_s):>10s})")
        if d_e > 0:
            print(f"  {'  (% of group disabled)':25s} {'':>14s} {100*b_e/d_e:>13.1f}% {100*sv_e/d_e:>13.1f}% {100*nc_e/d_e:>13.1f}%")
        print()

    print("-" * 90)
    print("C. BY DISABILITY TYPE")
    print("-" * 90)
    print(f"  {'Type':<40s} {'Total':>12s} {'Cost-Burd':>12s} {'Severe':>12s} {'GRPIP=101':>12s}")
    print(f"  {'':40s} {'(SE)':>12s} {'(SE)':>12s} {'(SE)':>12s} {'(SE)':>12s}")
    print("  " + "-" * 88)

    for dtype in disab_types:
        dd = disab_results[dtype]
        t_e, t_s = dd["total"]
        b_e, b_s = dd["burdened"]
        sv_e, sv_s = dd["severe"]
        nc_e, nc_s = dd["not_computed"]

        label = disab_labels[dtype]
        print(f"  {label:<40s} {fmt(t_e):>12s} {fmt(b_e):>12s} {fmt(sv_e):>12s} {fmt(nc_e):>12s}")
        print(f"  {'':40s} ({fmt(t_s):>8s}) ({fmt(b_s):>8s}) ({fmt(sv_s):>8s}) ({fmt(nc_s):>8s})")
        if t_e > 0:
            print(f"  {'  (% of type total)':40s} {'':>12s} {100*b_e/t_e:>11.1f}% {100*sv_e/t_e:>11.1f}% {100*nc_e/t_e:>11.1f}%")
        print()

    print("=" * 90)
    print("NOTES:")
    print("  - Source: ACS 2023 1-Year PUMS via Census API")
    print("  - Universe: Renter householders (TEN=3, SPORDER=1) nationally")
    print("  - Disability: DPHY=1 (ambulatory) or DOUT=1 (independent living difficulty)")
    print("  - Cost burden: GRPIP > 30; Severe: GRPIP > 50")
    print("  - GRPIP=101 means not computed (zero/negative income); excluded from burden rates")
    print("  - Weights: WGTP (housing unit weight)")
    print("  - SE via successive-differences replication: sqrt((4/80)*sum(est_r - est)^2)")
    print("  - AIAN = American Indian and Alaska Native (RAC1P = 3, 4, or 5)")
    print("=" * 90)

if __name__ == "__main__":
    main()
