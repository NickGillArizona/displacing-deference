"""
Fast PUMS Housing Stock Analysis - Point Estimates Only (no replicate weights).
Queries 2020-2024 ACS 5-Year PUMS via Census API.
Run the full replicate-weight version later for SEs.
"""

import urllib.request, json, math, time, sys, ssl
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


RACES = [(1, 'White'), (2, 'Black'), (3, 'AIAN')]

# BLD: 01=Mobile, 02=1-det, 03=1-att, 04=2apt, 05=3-4, 06=5-9, 07=10-19, 08=20-49, 09=50+, 10=Boat/RV
BLD_LABELS = {
    '1': 'Mobile home', '2': '1-fam detached', '3': '1-fam attached',
    '4': '2 apts', '5': '3-4 apts', '6': '5-9 apts',
    '7': '10-19 apts', '8': '20-49 apts', '9': '50+ apts', '10': 'Boat/RV'
}
# 4+ units for FHA 3604(f)(3)(C): BLD 5 (3-4 apts includes 4-unit), 6-9
FOUR_PLUS = {'5', '6', '7', '8', '9'}

# YRBLT: pre-1990 = before FHA design-and-construction requirements (eff. 3/13/1991)
PRE_1990 = {'1939', '1940', '1950', '1960', '1970', '1980'}
POST_1990 = {'1990', '2000', '2010', '2020', '2021', '2022', '2023', '2024'}

YRBLT_LABELS = {
    '1939': 'Pre-1940', '1940': '1940s', '1950': '1950s', '1960': '1960s',
    '1970': '1970s', '1980': '1980s', '1990': '1990s', '2000': '2000s',
    '2010': '2010s', '2020': '2020', '2021': '2021', '2022': '2022',
    '2023': '2023', '2024': '2024'
}

print("=" * 80)
print("  PUMS Housing Stock Analysis — Point Estimates")
print("  2020-2024 ACS 5-Year | Renter Householders (TEN=3, SPORDER=1)")
print("  Disability = DPHY=1 or DOUT=1 (ambulatory or independent living)")
print("=" * 80)

all_results = {}

for race_code, race_name in RACES:
    print(f"\n{'='*70}")
    print(f"  {race_name} (RAC1P={race_code})")
    print(f"{'='*70}")

    url = (f'{BASE}?get=WGTP,DPHY,DOUT,GRPIP,BLD,YRBLT,PLM'
           f'&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}')
    print("  Fetching data...")
    data = fetch(url)
    header = data[0]
    rows = data[1:]
    print(f"  Records: {len(rows)}")

    # Parse into structured records
    parsed = []
    for row in rows:
        d = {h: row[i] for i, h in enumerate(header)}
        wt = int(d['WGTP'])
        disabled = (d.get('DPHY') == '1' or d.get('DOUT') == '1')
        grpip_raw = d.get('GRPIP', '')
        grpip = int(grpip_raw) if grpip_raw else -1
        bld = d.get('BLD', '')
        yrblt = d.get('YRBLT', '')
        plm = d.get('PLM', '')

        parsed.append({
            'wt': wt, 'disabled': disabled,
            'grpip': grpip,
            'cost_burdened': 0 < grpip <= 100 and grpip > 30,
            'severe': 0 < grpip <= 100 and grpip > 50,
            'grpip_101': grpip == 101,
            'cb_computable': 0 < grpip <= 100,
            'bld': bld,
            'four_plus': bld in FOUR_PLUS,
            'yrblt': yrblt,
            'pre_1990': yrblt in PRE_1990,
            'post_1990': yrblt in POST_1990,
            'incomplete_plumbing': plm == '2',
        })

    dis = [r for r in parsed if r['disabled']]
    nondis = [r for r in parsed if not r['disabled']]
    w = lambda recs: sum(r['wt'] for r in recs)

    total_dis = w(dis)
    total_nondis = w(nondis)
    total_all = total_dis + total_nondis

    R = {}  # results dict
    R['total_disabled'] = total_dis
    R['total_nondis'] = total_nondis
    R['disability_prevalence'] = total_dis / total_all if total_all else 0

    print(f"\n  Disabled renter HHers: {total_dis:,.0f} ({R['disability_prevalence']*100:.1f}%)")

    # ===== 1. PRE-1990 BUILDING OCCUPANCY =====
    dis_pre = [r for r in dis if r['pre_1990']]
    nondis_pre = [r for r in nondis if r['pre_1990']]
    R['dis_pre90_pct'] = w(dis_pre) / total_dis
    R['nondis_pre90_pct'] = w(nondis_pre) / total_nondis
    R['pre90_penalty_pp'] = (R['dis_pre90_pct'] - R['nondis_pre90_pct']) * 100

    print(f"\n  Pre-1990 occupancy:")
    print(f"    Disabled:     {R['dis_pre90_pct']*100:.1f}%")
    print(f"    Non-disabled: {R['nondis_pre90_pct']*100:.1f}%")
    print(f"    Penalty:      {R['pre90_penalty_pp']:.1f} pp")

    # ===== 2. 3604(f)(3)(C) STATUTORY GAP =====
    dis_4p_pre = [r for r in dis if r['four_plus'] and r['pre_1990']]
    dis_4p_post = [r for r in dis if r['four_plus'] and r['post_1990']]
    nondis_4p_pre = [r for r in nondis if r['four_plus'] and r['pre_1990']]

    R['dis_4p_pre90_count'] = w(dis_4p_pre)
    R['dis_4p_pre90_pct'] = w(dis_4p_pre) / total_dis
    R['dis_4p_post90_count'] = w(dis_4p_post)
    R['dis_4p_post90_pct'] = w(dis_4p_post) / total_dis
    R['gap_ratio'] = R['dis_4p_pre90_count'] / R['dis_4p_post90_count'] if R['dis_4p_post90_count'] else 0

    # Also non-disabled for comparison
    R['nondis_4p_pre90_pct'] = w(nondis_4p_pre) / total_nondis if total_nondis else 0

    print(f"\n  3604(f)(3)(C) Statutory Gap (4+ unit buildings):")
    print(f"    Pre-1990 (gap):     {R['dis_4p_pre90_pct']*100:.1f}% ({R['dis_4p_pre90_count']:,.0f})")
    print(f"    Post-1990 (covered): {R['dis_4p_post90_pct']*100:.1f}% ({R['dis_4p_post90_count']:,.0f})")
    print(f"    Gap ratio:          {R['gap_ratio']:.1f}:1")

    # ===== 3. COST BURDEN BY BUILDING ERA =====
    for era, era_filter in [('pre90', lambda r: r['pre_1990']), ('post90', lambda r: r['post_1990'])]:
        for label, subset in [('dis', dis), ('nd', nondis)]:
            era_sub = [r for r in subset if era_filter(r)]
            cb_elig = [r for r in era_sub if r['cb_computable']]
            cb = [r for r in era_sub if r['cost_burdened']]
            sev = [r for r in era_sub if r['severe']]
            d = w(cb_elig)
            R[f'{label}_{era}_cb'] = w(cb) / d if d else 0
            R[f'{label}_{era}_severe'] = w(sev) / d if d else 0
            R[f'{label}_{era}_count'] = w(era_sub)

    print(f"\n  Cost burden by building era:")
    print(f"    Pre-1990 disabled:  CB {R['dis_pre90_cb']*100:.1f}%, Severe {R['dis_pre90_severe']*100:.1f}%")
    print(f"    Post-1990 disabled: CB {R['dis_post90_cb']*100:.1f}%, Severe {R['dis_post90_severe']*100:.1f}%")
    print(f"    Pre-1990 non-dis:   CB {R['nd_pre90_cb']*100:.1f}%, Severe {R['nd_pre90_severe']*100:.1f}%")
    print(f"    Post-1990 non-dis:  CB {R['nd_post90_cb']*100:.1f}%, Severe {R['nd_post90_severe']*100:.1f}%")

    # ===== 4. COST BURDEN IN 4+ UNIT PRE-1990 (the intersection) =====
    cb_elig_4p = [r for r in dis_4p_pre if r['cb_computable']]
    cb_4p = [r for r in dis_4p_pre if r['cost_burdened']]
    sev_4p = [r for r in dis_4p_pre if r['severe']]
    g101_4p = [r for r in dis_4p_pre if r['grpip_101']]
    d_4p = w(cb_elig_4p)
    R['dis_4p_pre90_cb'] = w(cb_4p) / d_4p if d_4p else 0
    R['dis_4p_pre90_severe'] = w(sev_4p) / d_4p if d_4p else 0
    R['dis_4p_pre90_g101_pct'] = w(g101_4p) / R['dis_4p_pre90_count'] if R['dis_4p_pre90_count'] else 0

    print(f"\n  4+ unit pre-1990 disabled renters:")
    print(f"    CB rate:     {R['dis_4p_pre90_cb']*100:.1f}%")
    print(f"    Severe:      {R['dis_4p_pre90_severe']*100:.1f}%")
    print(f"    GRPIP=101:   {R['dis_4p_pre90_g101_pct']*100:.1f}%")

    # ===== 5. BUILDING TYPE DISTRIBUTION =====
    print(f"\n  Building type distribution (disabled renters):")
    R['bld_dist'] = {}
    for code in sorted(BLD_LABELS.keys()):
        sub = [r for r in dis if r['bld'] == code]
        count = w(sub)
        pct = count / total_dis if total_dis else 0
        R['bld_dist'][BLD_LABELS[code]] = {'count': count, 'pct': round(pct * 100, 1)}
        print(f"    {BLD_LABELS[code]:<18s}: {count:>10,.0f} ({pct*100:.1f}%)")

    # ===== 6. YEAR BUILT DISTRIBUTION =====
    print(f"\n  Year built distribution (disabled renters):")
    R['yrblt_dist'] = {}
    for code in sorted(YRBLT_LABELS.keys()):
        sub = [r for r in dis if r['yrblt'] == code]
        count = w(sub)
        pct = count / total_dis if total_dis else 0
        R['yrblt_dist'][YRBLT_LABELS[code]] = {'count': count, 'pct': round(pct * 100, 1)}
        if count > 0:
            print(f"    {YRBLT_LABELS[code]:<12s}: {count:>10,.0f} ({pct*100:.1f}%)")

    # ===== 7. INCOMPLETE PLUMBING =====
    dis_noplmb = [r for r in dis if r['incomplete_plumbing']]
    nd_noplmb = [r for r in nondis if r['incomplete_plumbing']]
    R['dis_incomplete_plmb'] = w(dis_noplmb) / total_dis if total_dis else 0
    R['nd_incomplete_plmb'] = w(nd_noplmb) / total_nondis if total_nondis else 0
    R['plmb_ratio'] = R['dis_incomplete_plmb'] / R['nd_incomplete_plmb'] if R['nd_incomplete_plmb'] else 0

    print(f"\n  Incomplete plumbing:")
    print(f"    Disabled:     {R['dis_incomplete_plmb']*100:.3f}%")
    print(f"    Non-disabled: {R['nd_incomplete_plmb']*100:.3f}%")
    print(f"    Ratio:        {R['plmb_ratio']:.1f}x")

    # ===== 8. 4+ UNIT PRE-1990 GRPIP BANDS =====
    print(f"\n  GRPIP bands in 4+ unit pre-1990 (disabled):")
    R['grpip_bands_4p_pre90'] = {}
    for label, filt in [
        ('Not burdened (0-30)', lambda r: 0 < r['grpip'] <= 30),
        ('Moderate (31-50)', lambda r: 30 < r['grpip'] <= 50),
        ('Severe (51-100)', lambda r: 50 < r['grpip'] <= 100),
        ('Not computed (101)', lambda r: r['grpip'] == 101),
    ]:
        sub = [r for r in dis_4p_pre if filt(r)]
        count = w(sub)
        pct = count / R['dis_4p_pre90_count'] if R['dis_4p_pre90_count'] else 0
        R['grpip_bands_4p_pre90'][label] = {'count': count, 'pct': round(pct * 100, 1)}
        print(f"    {label:<25s}: {count:>10,.0f} ({pct*100:.1f}%)")

    # ===== 9. NEW: Cost burden penalty by building era =====
    R['era_penalty_pre90'] = R['dis_pre90_cb'] - R['nd_pre90_cb']
    R['era_penalty_post90'] = R['dis_post90_cb'] - R['nd_post90_cb']

    print(f"\n  Disability cost-burden penalty by era:")
    print(f"    Pre-1990:  {R['era_penalty_pre90']*100:.1f} pp")
    print(f"    Post-1990: {R['era_penalty_post90']*100:.1f} pp")

    # ===== 10. NEW: 4+ unit share among ALL disabled vs. non-disabled =====
    dis_4p_all = [r for r in dis if r['four_plus']]
    nondis_4p_all = [r for r in nondis if r['four_plus']]
    R['dis_4p_all_pct'] = w(dis_4p_all) / total_dis if total_dis else 0
    R['nd_4p_all_pct'] = w(nondis_4p_all) / total_nondis if total_nondis else 0

    print(f"\n  4+ unit share (all eras):")
    print(f"    Disabled:     {R['dis_4p_all_pct']*100:.1f}%")
    print(f"    Non-disabled: {R['nd_4p_all_pct']*100:.1f}%")

    all_results[race_name] = R
    time.sleep(1)


# ========================================================================
# CROSS-RACE COMPARISON TABLE
# ========================================================================

print("\n\n" + "=" * 80)
print("  CROSS-RACE COMPARISONS")
print("=" * 80)

def fmt(v, pct=True):
    if pct:
        return f"{v*100:.1f}%"
    return f"{v:,.0f}"

metrics = [
    ('Disability prevalence', 'disability_prevalence', True),
    ('Pre-1990 occupancy (dis)', 'dis_pre90_pct', True),
    ('Pre-1990 occupancy (non-dis)', 'nondis_pre90_pct', True),
    ('Pre-1990 penalty (pp)', 'pre90_penalty_pp', False),
    ('4+ pre-1990 (statutory gap)', 'dis_4p_pre90_pct', True),
    ('4+ pre-1990 count', 'dis_4p_pre90_count', False),
    ('4+ post-1990 (covered)', 'dis_4p_post90_pct', True),
    ('4+ post-1990 count', 'dis_4p_post90_count', False),
    ('Gap ratio', 'gap_ratio', False),
    ('CB pre-1990 (dis)', 'dis_pre90_cb', True),
    ('CB post-1990 (dis)', 'dis_post90_cb', True),
    ('CB 4+ pre-1990 (dis)', 'dis_4p_pre90_cb', True),
    ('Severe 4+ pre-1990 (dis)', 'dis_4p_pre90_severe', True),
    ('GRPIP=101 in 4+ pre-1990', 'dis_4p_pre90_g101_pct', True),
    ('Incomplete plumbing (dis)', 'dis_incomplete_plmb', True),
    ('Incomplete plumbing ratio', 'plmb_ratio', False),
    ('Era penalty pre-1990 (pp)', 'era_penalty_pre90', True),
    ('Era penalty post-1990 (pp)', 'era_penalty_post90', True),
    ('4+ unit share all eras (dis)', 'dis_4p_all_pct', True),
]

print(f"\n  {'Metric':<35s} {'White':>12s} {'Black':>12s} {'AIAN':>12s}")
print(f"  {'-'*35} {'-'*12} {'-'*12} {'-'*12}")
for label, key, is_pct in metrics:
    vals = []
    for race in ['White', 'Black', 'AIAN']:
        v = all_results[race].get(key, 0)
        if is_pct and key not in ('pre90_penalty_pp',):
            vals.append(f"{v*100:.1f}%")
        elif key == 'pre90_penalty_pp':
            vals.append(f"{v:.1f} pp")
        elif key == 'gap_ratio' or key == 'plmb_ratio':
            vals.append(f"{v:.1f}x")
        elif isinstance(v, float) and v > 1000:
            vals.append(f"{v:,.0f}")
        else:
            vals.append(f"{v:,.0f}" if isinstance(v, (int, float)) and v > 10 else f"{v:.1f}")
    print(f"  {label:<35s} {vals[0]:>12s} {vals[1]:>12s} {vals[2]:>12s}")


# ========================================================================
# KEY FINDINGS FOR STRATEGY 3
# ========================================================================

print("\n\n" + "=" * 80)
print("  KEY FINDINGS FOR NOTE REVISION (Strategy 3)")
print("=" * 80)

b = all_results['Black']
w_r = all_results['White']
a = all_results['AIAN']

print(f"""
1. THE TEMPORAL GAP
   {b['dis_pre90_pct']*100:.1f}% of Black disabled renters live in pre-1990 buildings
   vs. {w_r['dis_pre90_pct']*100:.1f}% of White disabled renters
   Pre-1990 penalty: Black {b['pre90_penalty_pp']:.1f}pp, White {w_r['pre90_penalty_pp']:.1f}pp

2. THE 3604(f)(3)(C) STATUTORY GAP
   Black disabled renters in 4+ unit pre-1990 buildings: {b['dis_4p_pre90_count']:,.0f} ({b['dis_4p_pre90_pct']*100:.1f}%)
   vs. 4+ unit post-1990 (potentially covered): {b['dis_4p_post90_count']:,.0f} ({b['dis_4p_post90_pct']*100:.1f}%)
   Gap ratio: {b['gap_ratio']:.1f}:1
   These are the buildings Congress targeted (4+ units) but in structures
   predating the March 13, 1991 first-occupancy trigger.

3. COST BURDEN COMPOUNDS IN OLDER BUILDINGS
   Pre-1990 disabled CB: Black {b['dis_pre90_cb']*100:.1f}%, White {w_r['dis_pre90_cb']*100:.1f}%
   4+ pre-1990 disabled CB: Black {b['dis_4p_pre90_cb']*100:.1f}%, White {w_r['dis_4p_pre90_cb']*100:.1f}%
   Disability era penalty (pre-1990): Black {b['era_penalty_pre90']*100:.1f}pp, White {w_r['era_penalty_pre90']*100:.1f}pp

4. PHYSICAL INADEQUACY
   Incomplete plumbing (disabled): Black {b['dis_incomplete_plmb']*100:.3f}%, AIAN {a['dis_incomplete_plmb']*100:.3f}%
   Disabled-to-non-disabled ratio: Black {b['plmb_ratio']:.1f}x, AIAN {a['plmb_ratio']:.1f}x

5. INVISIBLE POPULATION IN THE GAP
   GRPIP=101 in 4+ pre-1990: Black {b['dis_4p_pre90_g101_pct']*100:.1f}%, White {w_r['dis_4p_pre90_g101_pct']*100:.1f}%
""")


# Save results
output = {}
for race in all_results:
    output[race] = {k: v for k, v in all_results[race].items()
                    if not isinstance(v, dict)}
    for dk in ['bld_dist', 'yrblt_dist', 'grpip_bands_4p_pre90']:
        if dk in all_results[race]:
            output[race][dk] = all_results[race][dk]

with open('C:/Users/nickg/OneDrive/Documents/Note/housing_stock_results.json', 'w') as f:
    json.dump(output, f, indent=2, default=float)
print("Results saved to housing_stock_results.json")
