"""
PUMS Three-Way Cross-Tabulation: Disability x Race x Severe Cost Burden Among Renters
======================================================================================
Uses Census API to fetch 2023 ACS 1-Year PUMS microdata.
"""

import pandas as pd
import numpy as np
import requests
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RESULTS_DIR

API_BASE = "https://api.census.gov/data/2023/acs/acs1/pums"

def fetch_pums_api(variables, predicates=None):
    """Fetch from Census PUMS API, one state at a time to avoid size limits."""
    all_rows = []
    headers = None

    # Fetch all states at once with core vars only
    pred_str = ""
    if predicates:
        pred_str = "&" + "&".join(f"{k}={v}" for k, v in predicates.items())

    url = f"{API_BASE}?get={','.join(variables)}{pred_str}&for=state:*"
    print(f"  Fetching {len(variables)} variables...")

    resp = requests.get(url, timeout=180)
    if resp.status_code != 200:
        print(f"  Error {resp.status_code}: {resp.text[:200]}")
        return None

    data = resp.json()
    headers = data[0]
    all_rows.extend(data[1:])

    # Census API returns duplicate column names for predicates; deduplicate
    seen = {}
    clean_headers = []
    for h in headers:
        if h in seen:
            clean_headers.append(f"{h}_dup{seen[h]}")
            seen[h] += 1
        else:
            seen[h] = 1
            clean_headers.append(h)

    df = pd.DataFrame(all_rows, columns=clean_headers)
    print(f"  Retrieved {len(df)} records")
    return df


def fetch_data():
    """Fetch core PUMS variables + replicate weights in batches."""

    core_vars = ["SERIALNO", "SPORDER", "RAC1P", "DPHY", "DOUT", "TEN", "GRPIP", "WGTP"]
    predicates = {"SPORDER": "1", "TEN": "3"}

    print("Step 1: Fetching core variables...")
    df = fetch_pums_api(core_vars, predicates)
    if df is None:
        sys.exit("Failed to fetch core data")

    # Convert types
    for col in ["SPORDER", "RAC1P", "DPHY", "DOUT", "TEN", "GRPIP", "WGTP"]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fetch replicate weights in batches of 20
    print("\nStep 2: Fetching replicate weights for standard errors...")
    for batch_start in range(1, 81, 20):
        batch_end = min(batch_start + 19, 80)
        rep_vars = ["SERIALNO"] + [f"WGTP{i}" for i in range(batch_start, batch_end + 1)]

        print(f"  Batch: WGTP{batch_start}-WGTP{batch_end}...")
        rep_df = fetch_pums_api(rep_vars, predicates)

        if rep_df is not None:
            for col in [f"WGTP{i}" for i in range(batch_start, batch_end + 1)]:
                rep_df[col] = pd.to_numeric(rep_df[col], errors='coerce')

            # The API returns records in the same order, so align by index
            # (SERIALNO may have duplicates across states, so index-based merge is safer)
            if len(rep_df) == len(df):
                for col in [f"WGTP{i}" for i in range(batch_start, batch_end + 1)]:
                    df[col] = rep_df[col].values
            else:
                print(f"  WARNING: Row count mismatch ({len(rep_df)} vs {len(df)}), skipping batch")
        else:
            print(f"  WARNING: Failed to fetch batch, will compute without SEs")
            break

    return df


def analyze(df):
    """Run the three-way cross-tabulation."""

    has_rep_weights = 'WGTP1' in df.columns

    # Filter valid GRPIP (0-100; 101 = not computed)
    renters = df[(df['GRPIP'] >= 0) & (df['GRPIP'] <= 100)].copy()
    print(f"\nRenter householders with valid GRPIP: {len(renters)}")

    # Derived variables
    renters['disabled'] = ((renters['DPHY'] == 1) | (renters['DOUT'] == 1)).astype(int)
    renters['severe_burden'] = (renters['GRPIP'] > 50).astype(int)

    # Race groups (RAC1P: 1=White, 2=Black, 3=AIAN, 4=Alaska Native, 5=AIAN+AN combo)
    renters['race_group'] = 'Other'
    renters.loc[renters['RAC1P'] == 1, 'race_group'] = 'White alone'
    renters.loc[renters['RAC1P'] == 2, 'race_group'] = 'Black alone'
    renters.loc[renters['RAC1P'].isin([3, 4, 5]), 'race_group'] = 'AIAN alone'

    total_disabled_wtd = renters[renters['disabled'] == 1]['WGTP'].sum()
    total_burdened_wtd = renters[renters['severe_burden'] == 1]['WGTP'].sum()
    total_wtd = renters['WGTP'].sum()
    print(f"Total weighted renter householders: {total_wtd:,.0f}")
    print(f"Disabled renter householders (weighted): {total_disabled_wtd:,.0f}")
    print(f"Severely cost-burdened (weighted): {total_burdened_wtd:,.0f}")

    # ==============================================================
    # THE THREE-WAY CROSS-TABULATION
    # ==============================================================
    print("\n" + "=" * 80)
    print("THREE-WAY CROSS-TABULATION: Disability x Race x Severe Cost Burden (>50% income)")
    print("Universe: Renter householders, 2023 ACS 1-Year PUMS")
    print("Disability = ambulatory difficulty (DPHY=1) OR independent living difficulty (DOUT=1)")
    print("=" * 80)

    results = []

    for race in ['White alone', 'Black alone', 'AIAN alone', 'Other']:
        for dis in [0, 1]:
            subset = renters[(renters['race_group'] == race) & (renters['disabled'] == dis)]

            n = len(subset)
            total_w = subset['WGTP'].sum()
            burdened_w = subset[subset['severe_burden'] == 1]['WGTP'].sum()
            rate = (burdened_w / total_w * 100) if total_w > 0 else 0

            # Standard errors via successive-differences replication
            se = None
            moe = None
            if has_rep_weights and total_w > 0:
                rep_rates = []
                for i in range(1, 81):
                    wt = f'WGTP{i}'
                    if wt in subset.columns:
                        t_r = subset[wt].sum()
                        b_r = subset[subset['severe_burden'] == 1][wt].sum()
                        rep_rates.append((b_r / t_r * 100) if t_r > 0 else 0)

                if len(rep_rates) == 80:
                    sum_sq = sum((r - rate) ** 2 for r in rep_rates)
                    se = np.sqrt(sum_sq * 4 / 80)
                    moe = se * 1.645  # 90% CI per Census convention

            dis_label = "Disabled" if dis == 1 else "Non-disabled"
            results.append({
                'Race': race,
                'Disability': dis_label,
                'N_unweighted': n,
                'Total_weighted': int(total_w),
                'Burdened_weighted': int(burdened_w),
                'Rate_pct': round(rate, 1),
                'SE': round(se, 2) if se else None,
                'MOE_90': round(moe, 1) if moe else None
            })

    # Print formatted
    print(f"\n{'Race':<15} {'Disability':<14} {'N(unwtd)':>9} {'Total(wtd)':>12} {'Burdened':>10} {'Rate%':>7} {'SE':>6} {'MOE90':>7}")
    print("-" * 82)
    for r in results:
        se_str = f"{r['SE']:.2f}" if r['SE'] else "N/A"
        moe_str = f"±{r['MOE_90']}" if r['MOE_90'] else "N/A"
        print(f"{r['Race']:<15} {r['Disability']:<14} {r['N_unweighted']:>9,} {r['Total_weighted']:>12,} {r['Burdened_weighted']:>10,} {r['Rate_pct']:>7} {se_str:>6} {moe_str:>7}")

    # ==============================================================
    # CONVERGENCE THESIS TEST
    # ==============================================================
    print("\n" + "=" * 80)
    print("CONVERGENCE THESIS TEST")
    print("=" * 80)

    def get_rate(race, dis):
        for r in results:
            if r['Race'] == race and r['Disability'] == dis:
                return r['Rate_pct'], r['SE']
        return None, None

    for race in ['White alone', 'Black alone', 'AIAN alone']:
        d_rate, d_se = get_rate(race, 'Disabled')
        nd_rate, nd_se = get_rate(race, 'Non-disabled')
        penalty = round(d_rate - nd_rate, 1)
        print(f"\n{race}:")
        print(f"  Disabled severe burden:     {d_rate}%" + (f" (SE={d_se})" if d_se else ""))
        print(f"  Non-disabled severe burden:  {nd_rate}%" + (f" (SE={nd_se})" if nd_se else ""))
        print(f"  Disability penalty:          +{penalty} pp")

    w_d, _ = get_rate('White alone', 'Disabled')
    b_d, b_se = get_rate('Black alone', 'Disabled')
    a_d, a_se = get_rate('AIAN alone', 'Disabled')
    b_nd, _ = get_rate('Black alone', 'Non-disabled')

    print(f"\n--- Key Comparisons ---")
    print(f"Disabled Black ({b_d}%) vs Disabled White ({w_d}%): gap = {round(b_d - w_d, 1)} pp")
    print(f"Disabled AIAN ({a_d}%) vs Disabled White ({w_d}%): gap = {round(a_d - w_d, 1)} pp")
    print(f"Disabled Black ({b_d}%) vs Non-disabled Black ({b_nd}%): gap = {round(b_d - b_nd, 1)} pp")

    print(f"\n--- VERDICT ---")
    if b_d > w_d and b_d > b_nd:
        print("CONVERGENCE THESIS SUPPORTED.")
        print("Disabled Black renters face the highest severe cost-burden rate.")
        print("Disability enforcement targeting § 3604(f)(3) would disproportionately")
        print("benefit Black renters, producing racially progressive outcomes.")
    elif b_d > w_d:
        print("PARTIALLY SUPPORTED: racial disparity exists among disabled renters,")
        print("but the disability penalty within Black renters needs qualification.")
    else:
        print("CONVERGENCE THESIS NOT SUPPORTED by the data. The manuscript must")
        print("qualify or revise the claim.")

    # Note about AIAN
    aian_n = sum(r['N_unweighted'] for r in results if r['Race'] == 'AIAN alone')
    print(f"\nNOTE: AIAN unweighted sample = {aian_n} (1-Year PUMS).")
    if aian_n < 200:
        print("Sample too small for reliable estimates. Use 5-Year PUMS for AIAN analysis.")

    # Save
    out = os.path.join(RESULTS_DIR, "pums_results.csv")
    pd.DataFrame(results).to_csv(out, index=False)
    print(f"\nResults saved to {out}")


if __name__ == "__main__":
    df = fetch_data()
    analyze(df)
