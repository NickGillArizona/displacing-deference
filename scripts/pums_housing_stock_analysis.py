"""
PUMS Housing Stock Analysis for Strategy 3: Structural Accessibility Deficit
Queries 2020-2024 ACS 5-Year PUMS via Census API.

Cross-tabulations:
  1. Building type (BLD) x disability x race
  2. Year built (YBL) x disability x race
  3. Pre-1990 building occupancy x BLD x disability x race x cost burden
  4. 4+ unit pre-1990 buildings (the 3604(f)(3)(C) gap) by race and disability
  5. Cost burden by building age cohort x disability x race
  6. Incomplete plumbing (PLMB) by disability x race

Uses successive-differences replication for standard errors.
"""

import urllib.request, json, math, time, sys, ssl, csv
from collections import defaultdict

BASE = 'https://api.census.gov/data/2024/acs/acs5/pums'
ctx = ssl.create_default_context()

def fetch(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
                return json.loads(resp.read())
        except Exception as e:
            wait = 3 * (attempt + 1)
            print(f"    Retry {attempt+1}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries: {url[:120]}...")


def se_from_reps(main_val, reps):
    return math.sqrt((4.0 / 80.0) * sum((r - main_val) ** 2 for r in reps))


# Race codes
RACES = [(1, 'White'), (2, 'Black'), (3, 'AIAN')]

# BLD codes (2020-2024 ACS 5-Year):
# 01 = Mobile home, 02 = 1-family detached, 03 = 1-family attached,
# 04 = 2 apts, 05 = 3-4, 06 = 5-9, 07 = 10-19, 08 = 20-49, 09 = 50+,
# 10 = Boat/RV/van
BLD_LABELS = {
    '01': 'Mobile home/trailer', '02': '1-family detached',
    '03': '1-family attached', '04': '2 apartments',
    '05': '3-4 apartments', '06': '5-9 apartments',
    '07': '10-19 apartments', '08': '20-49 apartments',
    '09': '50+ apartments', '10': 'Boat/RV/van'
}
# 4+ units for FHA 3604(f)(3)(C) = BLD codes 05,06,07,08,09
# Note: BLD=05 is "3-4 apartments" but includes 4-unit buildings
FOUR_PLUS_CODES = {'05', '06', '07', '08', '09'}

# YRBLT codes (2020-2024 ACS 5-Year) - actual decade start years
# Pre-1990 (before FHA design-and-construction requirements, effective 3/13/1991)
PRE_1990_CODES = {'1939', '1940', '1950', '1960', '1970', '1980'}
POST_1990_CODES = {'1990', '2000', '2010', '2020', '2021', '2022', '2023', '2024'}

YRBLT_LABELS = {
    '1939': '1939 or earlier', '1940': '1940-49', '1950': '1950-59',
    '1960': '1960-69', '1970': '1970-79', '1980': '1980-89',
    '1990': '1990-99', '2000': '2000-09', '2010': '2010-19',
    '2020': '2020', '2021': '2021', '2022': '2022',
    '2023': '2023', '2024': '2024'
}


def query_main(race_code):
    """Get main-weight data with BLD, YRBLT, GRPIP, PLM, disability."""
    url = (f'{BASE}?get=WGTP,DPHY,DOUT,GRPIP,BLD,YRBLT,PLM'
           f'&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}')
    return fetch(url)


def parse_rows(data):
    """Parse API response into list of dicts."""
    header = data[0]
    rows = []
    for row in data[1:]:
        d = {}
        for i, h in enumerate(header):
            d[h] = row[i]
        rows.append(d)
    return rows


def classify(rows):
    """Classify each row by disability, cost burden, building era, building type, plumbing."""
    for r in rows:
        r['wt'] = int(r['WGTP'])
        r['disabled'] = (r.get('DPHY') == '1' or r.get('DOUT') == '1')

        grpip = r.get('GRPIP', '')
        r['grpip_val'] = int(grpip) if grpip and grpip != '' else -1
        r['cost_burdened'] = r['grpip_val'] > 30 and r['grpip_val'] <= 100
        r['severe_burden'] = r['grpip_val'] > 50 and r['grpip_val'] <= 100
        r['grpip_101'] = r['grpip_val'] == 101
        r['cb_computable'] = r['grpip_val'] > 0 and r['grpip_val'] <= 100

        yrblt = r.get('YRBLT', '')
        r['pre_1990'] = yrblt in PRE_1990_CODES
        r['post_1990'] = yrblt in POST_1990_CODES
        r['yrblt_code'] = yrblt

        bld = r.get('BLD', '')
        r['four_plus'] = bld in FOUR_PLUS_CODES
        r['bld_code'] = bld

        plm = r.get('PLM', '')
        r['incomplete_plumbing'] = (plm == '2')  # 2 = No complete plumbing
    return rows


def weighted_sum(rows, field='wt'):
    return sum(r[field] for r in rows)


def rate(num_rows, denom_rows):
    n = weighted_sum(num_rows)
    d = weighted_sum(denom_rows)
    return n / d if d > 0 else 0


# ========================================================================
# MAIN ANALYSIS
# ========================================================================

all_results = {}

for race_code, race_name in RACES:
    print(f"\n{'='*70}")
    print(f"  {race_name} (RAC1P={race_code})")
    print(f"{'='*70}")

    # Fetch and parse main data
    print("  Fetching main weight data...")
    data = query_main(race_code)
    rows = parse_rows(data)
    rows = classify(rows)
    print(f"  Parsed {len(rows)} records")

    # Split by disability
    dis = [r for r in rows if r['disabled']]
    nondis = [r for r in rows if not r['disabled']]

    total_dis = weighted_sum(dis)
    total_nondis = weighted_sum(nondis)

    res = {'total_disabled': total_dis, 'total_nondis': total_nondis}

    # ---- 1. Pre-1990 Building Occupancy ----
    dis_pre90 = [r for r in dis if r['pre_1990']]
    nondis_pre90 = [r for r in nondis if r['pre_1990']]

    res['dis_pre90_rate'] = weighted_sum(dis_pre90) / total_dis if total_dis else 0
    res['nondis_pre90_rate'] = weighted_sum(nondis_pre90) / total_nondis if total_nondis else 0
    res['pre90_penalty'] = res['dis_pre90_rate'] - res['nondis_pre90_rate']

    print(f"  Pre-1990 occupancy: Disabled {res['dis_pre90_rate']*100:.1f}%, "
          f"Non-disabled {res['nondis_pre90_rate']*100:.1f}%, "
          f"Penalty {res['pre90_penalty']*100:.1f}pp")

    # ---- 2. 4+ Unit Pre-1990 (the 3604(f)(3)(C) Gap) ----
    dis_4plus_pre90 = [r for r in dis if r['four_plus'] and r['pre_1990']]
    dis_4plus_post90 = [r for r in dis if r['four_plus'] and r['post_1990']]

    res['dis_4plus_pre90_count'] = weighted_sum(dis_4plus_pre90)
    res['dis_4plus_pre90_rate'] = res['dis_4plus_pre90_count'] / total_dis if total_dis else 0
    res['dis_4plus_post90_count'] = weighted_sum(dis_4plus_post90)
    res['dis_4plus_post90_rate'] = res['dis_4plus_post90_count'] / total_dis if total_dis else 0

    # The statutory gap: 4+ unit pre-1990 = building type targeted by statute but exempt by date
    print(f"  4+ unit pre-1990 (statutory gap): {res['dis_4plus_pre90_rate']*100:.1f}% "
          f"({res['dis_4plus_pre90_count']:,.0f} weighted)")
    print(f"  4+ unit post-1990 (potentially covered): {res['dis_4plus_post90_rate']*100:.1f}% "
          f"({res['dis_4plus_post90_count']:,.0f} weighted)")

    # ---- 3. Cost Burden by Building Era ----
    for era_label, era_filter in [('pre_1990', lambda r: r['pre_1990']),
                                   ('post_1990', lambda r: r['post_1990'])]:
        for dis_label, subset in [('disabled', dis), ('nondis', nondis)]:
            era_sub = [r for r in subset if era_filter(r)]
            era_cb_eligible = [r for r in era_sub if r['cb_computable']]
            era_cb = [r for r in era_sub if r['cost_burdened']]
            era_severe = [r for r in era_sub if r['severe_burden']]

            denom = weighted_sum(era_cb_eligible)
            key_prefix = f'{dis_label}_{era_label}'
            res[f'{key_prefix}_cb_rate'] = weighted_sum(era_cb) / denom if denom else 0
            res[f'{key_prefix}_severe_rate'] = weighted_sum(era_severe) / denom if denom else 0
            res[f'{key_prefix}_count'] = weighted_sum(era_sub)

    print(f"  CB in pre-1990: Disabled {res['disabled_pre_1990_cb_rate']*100:.1f}%, "
          f"Non-disabled {res['nondis_pre_1990_cb_rate']*100:.1f}%")
    print(f"  CB in post-1990: Disabled {res['disabled_post_1990_cb_rate']*100:.1f}%, "
          f"Non-disabled {res['nondis_post_1990_cb_rate']*100:.1f}%")

    # ---- 4. Cost Burden in 4+ Unit Pre-1990 (the intersection) ----
    dis_4pre90_cb_eligible = [r for r in dis_4plus_pre90 if r['cb_computable']]
    dis_4pre90_cb = [r for r in dis_4plus_pre90 if r['cost_burdened']]
    dis_4pre90_severe = [r for r in dis_4plus_pre90 if r['severe_burden']]

    denom_4p = weighted_sum(dis_4pre90_cb_eligible)
    res['dis_4plus_pre90_cb_rate'] = weighted_sum(dis_4pre90_cb) / denom_4p if denom_4p else 0
    res['dis_4plus_pre90_severe_rate'] = weighted_sum(dis_4pre90_severe) / denom_4p if denom_4p else 0

    print(f"  CB in 4+ unit pre-1990 disabled: {res['dis_4plus_pre90_cb_rate']*100:.1f}% "
          f"(severe: {res['dis_4plus_pre90_severe_rate']*100:.1f}%)")

    # ---- 5. Building Type Distribution (disabled renters) ----
    res['bld_dist_disabled'] = {}
    for bld_code, bld_label in BLD_LABELS.items():
        bld_sub = [r for r in dis if r['bld_code'] == bld_code]
        count = weighted_sum(bld_sub)
        res['bld_dist_disabled'][bld_code] = {
            'label': bld_label, 'count': count,
            'pct': count / total_dis if total_dis else 0
        }

    # ---- 6. Year Built Distribution (disabled renters) ----
    res['ybl_dist_disabled'] = {}
    for yrblt_code, yrblt_label in YRBLT_LABELS.items():
        ybl_sub = [r for r in dis if r['yrblt_code'] == yrblt_code]
        count = weighted_sum(ybl_sub)
        res['ybl_dist_disabled'][yrblt_code] = {
            'label': yrblt_label, 'count': count,
            'pct': count / total_dis if total_dis else 0
        }

    # ---- 7. Incomplete Plumbing ----
    dis_incomplete = [r for r in dis if r['incomplete_plumbing']]
    nondis_incomplete = [r for r in nondis if r['incomplete_plumbing']]

    res['dis_incomplete_plumbing_rate'] = weighted_sum(dis_incomplete) / total_dis if total_dis else 0
    res['nondis_incomplete_plumbing_rate'] = weighted_sum(nondis_incomplete) / total_nondis if total_nondis else 0
    res['plumbing_penalty'] = res['dis_incomplete_plumbing_rate'] - res['nondis_incomplete_plumbing_rate']

    print(f"  Incomplete plumbing: Disabled {res['dis_incomplete_plumbing_rate']*100:.3f}%, "
          f"Non-disabled {res['nondis_incomplete_plumbing_rate']*100:.3f}%")

    # ---- 8. 4+ Unit Pre-1990 Cost Burden by GRPIP Band ----
    res['grpip_bands_4plus_pre90'] = {}
    bands = [
        ('0-30 (not burdened)', lambda r: 0 < r['grpip_val'] <= 30),
        ('31-50 (moderate)', lambda r: 30 < r['grpip_val'] <= 50),
        ('51-100 (severe)', lambda r: 50 < r['grpip_val'] <= 100),
        ('101 (not computed)', lambda r: r['grpip_val'] == 101),
    ]
    for band_label, band_filter in bands:
        band_sub = [r for r in dis_4plus_pre90 if band_filter(r)]
        count = weighted_sum(band_sub)
        res['grpip_bands_4plus_pre90'][band_label] = {
            'count': count,
            'pct': count / res['dis_4plus_pre90_count'] if res['dis_4plus_pre90_count'] else 0
        }

    all_results[race_name] = res


# ========================================================================
# REPLICATE-WEIGHT STANDARD ERRORS for key estimates
# ========================================================================
print("\n" + "=" * 70)
print("  Computing Standard Errors via Replicate Weights")
print("  (Key estimates only - pre-1990 rate, 4+ pre-1990 rate, CB in 4+ pre-1990)")
print("=" * 70)

se_results = {}

for race_code, race_name in RACES:
    print(f"\n--- {race_name} ---")

    # Main estimates from above
    main_dis_pre90 = all_results[race_name]['dis_pre90_rate']
    main_4plus_pre90 = all_results[race_name]['dis_4plus_pre90_rate']
    main_4plus_pre90_cb = all_results[race_name]['dis_4plus_pre90_cb_rate']
    main_nondis_pre90 = all_results[race_name]['nondis_pre90_rate']

    rep_dis_pre90 = []
    rep_4plus_pre90 = []
    rep_4plus_pre90_cb = []
    rep_nondis_pre90 = []

    for rep_num in range(1, 81):
        rep_var = f'WGTP{rep_num}'
        url = (f'{BASE}?get={rep_var},DPHY,DOUT,BLD,YRBLT,GRPIP'
               f'&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}')
        data = fetch(url)
        rr = data[1:]

        # Compute replicate estimates
        dis_tot = 0; dis_pre = 0; dis_4pre = 0
        dis_4pre_cb_d = 0; dis_4pre_cb_n = 0
        nd_tot = 0; nd_pre = 0

        for row in rr:
            wt = int(row[0])
            disabled = (row[1] == '1' or row[2] == '1')
            bld = row[3]
            ybl = row[4]
            grpip_raw = row[5]
            grpip = int(grpip_raw) if grpip_raw else -1

            pre90 = ybl in PRE_1990_CODES
            four_plus = bld in FOUR_PLUS_CODES

            if disabled:
                dis_tot += wt
                if pre90:
                    dis_pre += wt
                    if four_plus:
                        dis_4pre += wt
                        if 0 < grpip <= 100:
                            dis_4pre_cb_d += wt
                            if grpip > 30:
                                dis_4pre_cb_n += wt
            else:
                nd_tot += wt
                if pre90:
                    nd_pre += wt

        rep_dis_pre90.append(dis_pre / dis_tot if dis_tot else 0)
        rep_4plus_pre90.append(dis_4pre / dis_tot if dis_tot else 0)
        rep_4plus_pre90_cb.append(dis_4pre_cb_n / dis_4pre_cb_d if dis_4pre_cb_d else 0)
        rep_nondis_pre90.append(nd_pre / nd_tot if nd_tot else 0)

        if rep_num % 20 == 0:
            print(f"  Replicate {rep_num}/80 done")
        time.sleep(0.3)

    se_results[race_name] = {
        'dis_pre90_rate_se': se_from_reps(main_dis_pre90, rep_dis_pre90),
        'dis_4plus_pre90_rate_se': se_from_reps(main_4plus_pre90, rep_4plus_pre90),
        'dis_4plus_pre90_cb_se': se_from_reps(main_4plus_pre90_cb, rep_4plus_pre90_cb),
        'nondis_pre90_rate_se': se_from_reps(main_nondis_pre90, rep_nondis_pre90),
    }

    print(f"  Pre-1990 disabled SE: {se_results[race_name]['dis_pre90_rate_se']*100:.2f}pp")
    print(f"  4+ pre-1990 disabled SE: {se_results[race_name]['dis_4plus_pre90_rate_se']*100:.2f}pp")
    print(f"  CB in 4+ pre-1990 SE: {se_results[race_name]['dis_4plus_pre90_cb_se']*100:.2f}pp")


# ========================================================================
# PRINT FULL RESULTS
# ========================================================================

print("\n\n" + "=" * 80)
print("  FULL RESULTS: Housing Stock Analysis for Strategy 3")
print("=" * 80)

for race_name in ['White', 'Black', 'AIAN']:
    r = all_results[race_name]
    se = se_results[race_name]

    print(f"\n{'='*60}")
    print(f"  {race_name}")
    print(f"{'='*60}")

    print(f"\n  Total disabled renter householders: {r['total_disabled']:,.0f}")
    print(f"  Total non-disabled: {r['total_nondis']:,.0f}")

    print(f"\n  --- Pre-1990 Building Occupancy ---")
    print(f"  Disabled:     {r['dis_pre90_rate']*100:.1f}% (SE={se['dis_pre90_rate_se']*100:.2f}pp)")
    print(f"  Non-disabled: {r['nondis_pre90_rate']*100:.1f}% (SE={se['nondis_pre90_rate_se']*100:.2f}pp)")
    print(f"  Penalty:      {r['pre90_penalty']*100:.1f}pp")

    print(f"\n  --- 3604(f)(3)(C) Statutory Gap ---")
    print(f"  4+ unit pre-1990 (gap):    {r['dis_4plus_pre90_rate']*100:.1f}% "
          f"({r['dis_4plus_pre90_count']:,.0f}) SE={se['dis_4plus_pre90_rate_se']*100:.2f}pp")
    print(f"  4+ unit post-1990 (covered): {r['dis_4plus_post90_rate']*100:.1f}% "
          f"({r['dis_4plus_post90_count']:,.0f})")
    print(f"  Gap ratio: {r['dis_4plus_pre90_count']/r['dis_4plus_post90_count']:.1f}:1"
          if r['dis_4plus_post90_count'] > 0 else "")

    print(f"\n  --- Cost Burden by Building Era ---")
    print(f"  Pre-1990 disabled CB:  {r['disabled_pre_1990_cb_rate']*100:.1f}%")
    print(f"  Post-1990 disabled CB: {r['disabled_post_1990_cb_rate']*100:.1f}%")
    print(f"  Pre-1990 non-dis CB:   {r['nondis_pre_1990_cb_rate']*100:.1f}%")
    print(f"  Post-1990 non-dis CB:  {r['nondis_post_1990_cb_rate']*100:.1f}%")

    print(f"\n  --- 4+ Unit Pre-1990 Disabled: CB Detail ---")
    print(f"  CB rate:     {r['dis_4plus_pre90_cb_rate']*100:.1f}% "
          f"(SE={se['dis_4plus_pre90_cb_se']*100:.2f}pp)")
    print(f"  Severe rate: {r['dis_4plus_pre90_severe_rate']*100:.1f}%")
    for band, bdata in r['grpip_bands_4plus_pre90'].items():
        print(f"    {band}: {bdata['count']:,.0f} ({bdata['pct']*100:.1f}%)")

    print(f"\n  --- Incomplete Plumbing ---")
    print(f"  Disabled:     {r['dis_incomplete_plumbing_rate']*100:.3f}%")
    print(f"  Non-disabled: {r['nondis_incomplete_plumbing_rate']*100:.3f}%")
    print(f"  Ratio:        {r['dis_incomplete_plumbing_rate']/r['nondis_incomplete_plumbing_rate']:.1f}x"
          if r['nondis_incomplete_plumbing_rate'] > 0 else "")

    print(f"\n  --- Building Type Distribution (Disabled Renters) ---")
    for code in sorted(r['bld_dist_disabled'].keys()):
        bd = r['bld_dist_disabled'][code]
        print(f"    {bd['label']:<25s}: {bd['count']:>10,.0f} ({bd['pct']*100:.1f}%)")

    print(f"\n  --- Year Built Distribution (Disabled Renters) ---")
    for code in sorted(r['ybl_dist_disabled'].keys()):
        yd = r['ybl_dist_disabled'][code]
        print(f"    {yd['label']:<15s}: {yd['count']:>10,.0f} ({yd['pct']*100:.1f}%)")


# ========================================================================
# CROSS-RACE COMPARISONS
# ========================================================================

print("\n\n" + "=" * 80)
print("  CROSS-RACE COMPARISONS")
print("=" * 80)

print("\n  Pre-1990 Occupancy (Disabled Renters):")
print(f"  {'Race':<8} {'Rate':<10} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = all_results[race]['dis_pre90_rate']
    s = se_results[race]['dis_pre90_rate_se']
    print(f"  {race:<8} {r*100:.1f}%     {s*100:.2f}pp   [{(r-1.96*s)*100:.1f}%, {(r+1.96*s)*100:.1f}%]")

print(f"\n  Black-White pre-1990 gap (disabled): "
      f"{(all_results['Black']['dis_pre90_rate']-all_results['White']['dis_pre90_rate'])*100:.1f}pp")

print("\n  4+ Unit Pre-1990 (Statutory Gap, Disabled):")
print(f"  {'Race':<8} {'Rate':<10} {'Count':<15} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = all_results[race]['dis_4plus_pre90_rate']
    c = all_results[race]['dis_4plus_pre90_count']
    s = se_results[race]['dis_4plus_pre90_rate_se']
    print(f"  {race:<8} {r*100:.1f}%     {c:>12,.0f}   {s*100:.2f}pp   [{(r-1.96*s)*100:.1f}%, {(r+1.96*s)*100:.1f}%]")

print("\n  Gap Ratios (pre-1990 4+ unit : post-1990 4+ unit, disabled):")
for race in ['White', 'Black', 'AIAN']:
    pre = all_results[race]['dis_4plus_pre90_count']
    post = all_results[race]['dis_4plus_post90_count']
    ratio = pre / post if post > 0 else float('inf')
    print(f"  {race:<8} {ratio:.1f}:1  ({pre:,.0f} pre / {post:,.0f} post)")

print("\n  Cost Burden in 4+ Unit Pre-1990 (Disabled):")
print(f"  {'Race':<8} {'CB Rate':<10} {'Severe':<10} {'SE(CB)':<10}")
for race in ['White', 'Black', 'AIAN']:
    cb = all_results[race]['dis_4plus_pre90_cb_rate']
    sv = all_results[race]['dis_4plus_pre90_severe_rate']
    s = se_results[race]['dis_4plus_pre90_cb_se']
    print(f"  {race:<8} {cb*100:.1f}%     {sv*100:.1f}%     {s*100:.2f}pp")

print("\n  Incomplete Plumbing Rates:")
print(f"  {'Race':<8} {'Disabled':<12} {'Non-disabled':<14} {'Ratio':<8}")
for race in ['White', 'Black', 'AIAN']:
    d = all_results[race]['dis_incomplete_plumbing_rate']
    n = all_results[race]['nondis_incomplete_plumbing_rate']
    ratio = d / n if n > 0 else float('inf')
    print(f"  {race:<8} {d*100:.3f}%     {n*100:.3f}%       {ratio:.1f}x")


# Save all results to JSON
output = {
    race: {
        k: v for k, v in res.items()
        if k not in ('bld_dist_disabled', 'ybl_dist_disabled', 'grpip_bands_4plus_pre90')
    }
    for race, res in all_results.items()
}
# Add SE results
for race in se_results:
    output[race].update(se_results[race])

# Add distributions as simplified dicts
for race in all_results:
    output[race]['bld_distribution'] = {
        v['label']: {'count': v['count'], 'pct': round(v['pct']*100, 1)}
        for v in all_results[race]['bld_dist_disabled'].values()
    }
    output[race]['ybl_distribution'] = {
        v['label']: {'count': v['count'], 'pct': round(v['pct']*100, 1)}
        for v in all_results[race]['ybl_dist_disabled'].values()
    }
    output[race]['grpip_bands_4plus_pre90'] = {
        k: {'count': v['count'], 'pct': round(v['pct']*100, 1)}
        for k, v in all_results[race]['grpip_bands_4plus_pre90'].items()
    }

with open('housing_stock_results.json', 'w') as f:
    json.dump(output, f, indent=2, default=float)
print("\n\nResults saved to housing_stock_results.json")
