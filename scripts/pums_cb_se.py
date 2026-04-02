"""Cost burden replicate-weight SEs with robust retry logic."""
import urllib.request, json, math, time, sys, ssl, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RESULTS_DIR

BASE = 'https://api.census.gov/data/2024/acs/acs5/pums'
ctx = ssl.create_default_context()

def fetch_with_retry(url, max_retries=5):
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
                return json.loads(resp.read())
        except Exception as e:
            wait = 3 * (attempt + 1)
            print(f"    Retry {attempt+1}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)
    raise Exception(f"Failed after {max_retries} retries: {url[:100]}...")

races = [(1, 'White'), (2, 'Black'), (3, 'AIAN')]
cb_results = {}

# Also save prevalence results from Part 1
prevalence_results = {
    'White': {'estimate': 0.140084, 'se': 0.000489, 'ci_low': 0.13912, 'ci_high': 0.14105},
    'Black': {'estimate': 0.145671, 'se': 0.000812, 'ci_low': 0.14408, 'ci_high': 0.14726},
    'AIAN':  {'estimate': 0.130807, 'se': 0.003559, 'ci_low': 0.12383, 'ci_high': 0.13778}
}

for race_code, race_name in races:
    print(f"\n{'='*50}")
    print(f"{race_name} (RAC1P={race_code})")
    print(f"{'='*50}")

    # Main estimate
    print("  Main weight query...")
    url = f'{BASE}?get=PWGTP,DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
    main_data = fetch_with_retry(url)
    rows = main_data[1:]

    def compute_cb(data_rows, wt_idx, grpip_idx):
        dis_b = 0; dis_d = 0; nd_b = 0; nd_d = 0; d101 = 0; d_tot = 0
        for row in data_rows:
            wt = int(row[wt_idx])
            dphy = row[1] if wt_idx == 0 else row[0]
            dout = row[2] if wt_idx == 0 else row[1]
            g_raw = row[grpip_idx]
            if not g_raw: continue
            g = int(g_raw)
            dis = (dphy == '1' or dout == '1')
            if dis:
                d_tot += wt
                if g == 101: d101 += wt
                elif g > 30: dis_b += wt; dis_d += wt
                else: dis_d += wt
            else:
                if g <= 100:
                    if g > 30: nd_b += wt; nd_d += wt
                    else: nd_d += wt
        dr = dis_b/dis_d if dis_d else 0
        nr = nd_b/nd_d if nd_d else 0
        return dr, nr, dr-nr, d101/d_tot if d_tot else 0

    main_dis, main_nd, main_pen, main_101 = compute_cb(rows, 0, 3)
    print(f"  Disabled CB: {main_dis*100:.1f}%, Penalty: {main_pen*100:.1f}pp, GRPIP101: {main_101*100:.1f}%")

    # Replicate weights - one at a time for reliability
    rep_dis = []; rep_nd = []; rep_pen = []; rep_101 = []

    for rep_num in range(1, 81):
        rep_var = f'PWGTP{rep_num}'
        url = f'{BASE}?get={rep_var},DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
        data = fetch_with_retry(url)
        r = data[1:]

        d_b = 0; d_d = 0; n_b = 0; n_d = 0; g101 = 0; d_t = 0
        for row in r:
            wt = int(row[0])
            dphy = row[1]; dout = row[2]; g_raw = row[3]
            if not g_raw: continue
            g = int(g_raw)
            dis = (dphy == '1' or dout == '1')
            if dis:
                d_t += wt
                if g == 101: g101 += wt
                elif g > 30: d_b += wt; d_d += wt
                else: d_d += wt
            else:
                if g <= 100:
                    if g > 30: n_b += wt; n_d += wt
                    else: n_d += wt

        dr = d_b/d_d if d_d else 0
        nr = n_b/n_d if n_d else 0
        rep_dis.append(dr); rep_nd.append(nr)
        rep_pen.append(dr - nr)
        rep_101.append(g101/d_t if d_t else 0)

        if rep_num % 10 == 0:
            print(f"  Replicate {rep_num}/80 done")
        time.sleep(0.5)  # Rate limit

    def se(main_val, reps):
        return math.sqrt((4.0/80.0) * sum((r - main_val)**2 for r in reps))

    se_d = se(main_dis, rep_dis)
    se_n = se(main_nd, rep_nd)
    se_p = se(main_pen, rep_pen)
    se_1 = se(main_101, rep_101)

    cb_results[race_name] = {
        'dis_cb': main_dis, 'se_dis_cb': se_d,
        'nondis_cb': main_nd, 'se_nondis_cb': se_n,
        'penalty': main_pen, 'se_penalty': se_p,
        'grpip101': main_101, 'se_grpip101': se_1
    }

    print(f"  Disabled CB: {main_dis*100:.1f}% (SE={se_d*100:.2f}%)")
    print(f"  Non-disabled CB: {main_nd*100:.1f}% (SE={se_n*100:.2f}%)")
    print(f"  Penalty: {main_pen*100:.1f}pp (SE={se_p*100:.2f}pp)")
    print(f"  GRPIP=101: {main_101*100:.1f}% (SE={se_1*100:.2f}%)")

# Save all results
all_results = {
    'prevalence': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in prevalence_results.items()},
    'cost_burden': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in cb_results.items()}
}
with open(os.path.join(RESULTS_DIR, 'pums_se_results.json'), 'w') as f:
    json.dump(all_results, f, indent=2)

# Print summary
print("\n" + "="*60)
print("FULL SUMMARY WITH 95% CONFIDENCE INTERVALS")
print("="*60)

print("\nDisability Prevalence:")
for race in ['White', 'Black', 'AIAN']:
    r = prevalence_results[race]
    print(f"  {race}: {r['estimate']*100:.2f}% [{r['ci_low']*100:.2f}%, {r['ci_high']*100:.2f}%]")

import math
diff = prevalence_results['White']['estimate'] - prevalence_results['AIAN']['estimate']
se_diff = math.sqrt(prevalence_results['White']['se']**2 + prevalence_results['AIAN']['se']**2)
z = diff / se_diff
p = 2 * (1 - 0.5*(1+math.erf(abs(z)/math.sqrt(2))))
print(f"\n  White-AIAN difference: {diff*100:.2f}pp (z={z:.2f}, p={p:.4f})")

print("\nCost Burden (Disabled Renters):")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['dis_cb'] - 1.96*r['se_dis_cb']
    hi = r['dis_cb'] + 1.96*r['se_dis_cb']
    print(f"  {race}: {r['dis_cb']*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%]  (SE={r['se_dis_cb']*100:.2f}%)")

print("\nDisability Penalty:")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['penalty'] - 1.96*r['se_penalty']
    hi = r['penalty'] + 1.96*r['se_penalty']
    print(f"  {race}: {r['penalty']*100:.1f}pp [{lo*100:.1f}pp, {hi*100:.1f}pp]  (SE={r['se_penalty']*100:.2f}pp)")

print("\nGRPIP=101 Rate (Disabled):")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['grpip101'] - 1.96*r['se_grpip101']
    hi = r['grpip101'] + 1.96*r['se_grpip101']
    print(f"  {race}: {r['grpip101']*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%]  (SE={r['se_grpip101']*100:.2f}%)")

print("\nDone. Results saved to pums_se_results.json")
