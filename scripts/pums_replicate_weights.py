"""
PUMS Replicate Weight Standard Error Computation
Queries Census API for 80 replicate weights to compute SEs via successive-differences replication.
"""
import urllib.request, json, math, time, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import RESULTS_DIR

BASE = 'https://api.census.gov/data/2024/acs/acs5/pums'

def query_pums(weight_var, race_code, extra_vars=''):
    """Query PUMS API for renter householders of given race, using specified weight variable."""
    get_vars = f'{weight_var},DPHY,DOUT'
    if extra_vars:
        get_vars += f',{extra_vars}'
    url = f'{BASE}?get={get_vars}&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    return data

def compute_disability_prevalence(data, weight_idx=0):
    """Compute weighted disability prevalence from API response."""
    rows = data[1:]
    total = 0
    disabled = 0
    for row in rows:
        wt = int(row[weight_idx])
        dphy = row[1]
        dout = row[2]
        total += wt
        if dphy == '1' or dout == '1':
            disabled += wt
    return disabled / total if total > 0 else 0

def compute_cost_burden(data, weight_idx=0, grpip_idx=3):
    """Compute cost burden rate and disability penalty from API response with GRPIP."""
    rows = data[1:]
    dis_burden = 0
    dis_denom = 0
    nondis_burden = 0
    nondis_denom = 0
    dis_grpip101 = 0
    dis_total = 0

    for row in rows:
        wt = int(row[weight_idx])
        dphy = row[1]
        dout = row[2]
        grpip_raw = row[grpip_idx]
        if not grpip_raw or grpip_raw == '':
            continue
        grpip = int(grpip_raw)
        is_disabled = (dphy == '1' or dout == '1')

        if is_disabled:
            dis_total += wt
            if grpip == 101:
                dis_grpip101 += wt
            elif grpip > 30:
                dis_burden += wt
                dis_denom += wt
            else:
                dis_denom += wt
        else:
            if grpip <= 100:
                if grpip > 30:
                    nondis_burden += wt
                    nondis_denom += wt
                else:
                    nondis_denom += wt

    dis_rate = dis_burden / dis_denom if dis_denom > 0 else 0
    nondis_rate = nondis_burden / nondis_denom if nondis_denom > 0 else 0
    penalty = dis_rate - nondis_rate
    grpip101_rate = dis_grpip101 / dis_total if dis_total > 0 else 0

    return {
        'dis_cb': dis_rate,
        'nondis_cb': nondis_rate,
        'penalty': penalty,
        'grpip101': grpip101_rate
    }


# === PART 1: Disability Prevalence ===
print("=" * 60)
print("PART 1: Disability Prevalence - Replicate Weight SEs")
print("=" * 60)

races = [(1, 'White'), (2, 'Black'), (3, 'AIAN')]
prevalence_results = {}

for race_code, race_name in races:
    print(f"\n--- {race_name} (RAC1P={race_code}) ---")

    # Main estimate
    print(f"  Querying main weight (PWGTP)...")
    main_data = query_pums('PWGTP', race_code)
    main_est = compute_disability_prevalence(main_data)
    print(f"  Main estimate: {main_est*100:.4f}%")

    # We need to query each replicate weight separately since the API
    # can only return a limited number of variables
    # Strategy: query PWGTP1-PWGTP80 in batches alongside DPHY, DOUT

    rep_estimates = []
    batch_size = 10  # Query 10 replicate weights at a time

    for batch_start in range(1, 81, batch_size):
        batch_end = min(batch_start + batch_size, 81)
        rep_vars = ','.join([f'PWGTP{i}' for i in range(batch_start, batch_end)])
        get_str = f'DPHY,DOUT,{rep_vars}'
        url = f'{BASE}?get={get_str}&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'

        retry = 0
        while retry < 3:
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                break
            except Exception as e:
                retry += 1
                if retry == 3:
                    print(f"  FAILED batch {batch_start}-{batch_end-1}: {e}")
                    sys.exit(1)
                time.sleep(2)

        rows = data[1:]
        header = data[0]

        # For each replicate weight in this batch
        for i, rep_num in enumerate(range(batch_start, batch_end)):
            wt_idx = 2 + i  # DPHY=0, DOUT=1, then replicate weights start at 2
            total = 0
            disabled = 0
            for row in rows:
                wt = int(row[wt_idx])
                dphy = row[0]
                dout = row[1]
                total += wt
                if dphy == '1' or dout == '1':
                    disabled += wt
            rep_est = disabled / total if total > 0 else 0
            rep_estimates.append(rep_est)

        sys.stdout.write(f"  Replicates {batch_start}-{batch_end-1} done\r")
        sys.stdout.flush()

    # Compute SE using successive-differences formula
    sum_sq_diff = sum((r - main_est) ** 2 for r in rep_estimates)
    se = math.sqrt((4.0 / 80.0) * sum_sq_diff)
    ci_low = main_est - 1.96 * se
    ci_high = main_est + 1.96 * se
    moe = 1.96 * se

    prevalence_results[race_name] = {
        'estimate': main_est,
        'se': se,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'moe': moe
    }

    print(f"\n  Estimate: {main_est*100:.2f}%")
    print(f"  SE: {se*100:.4f}%")
    print(f"  95% CI: [{ci_low*100:.2f}%, {ci_high*100:.2f}%]")
    print(f"  MOE: +/- {moe*100:.4f}%")


# === PART 2: Cost Burden ===
print("\n" + "=" * 60)
print("PART 2: Cost Burden Rates - Replicate Weight SEs")
print("=" * 60)

cb_results = {}

for race_code, race_name in races:
    print(f"\n--- {race_name} (RAC1P={race_code}) ---")

    # Main estimate with GRPIP
    print(f"  Querying main weight with GRPIP...")
    url = f'{BASE}?get=PWGTP,DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        main_data = json.loads(resp.read())

    main_cb = compute_cost_burden(main_data, weight_idx=0, grpip_idx=3)
    print(f"  Disabled CB: {main_cb['dis_cb']*100:.1f}%, Non-disabled CB: {main_cb['nondis_cb']*100:.1f}%, Penalty: {main_cb['penalty']*100:.1f}pp")

    # Replicate weights - need DPHY, DOUT, GRPIP, plus replicate weights
    rep_dis_cb = []
    rep_nondis_cb = []
    rep_penalty = []
    rep_grpip101 = []

    batch_size = 8  # Smaller batches since we also need GRPIP

    for batch_start in range(1, 81, batch_size):
        batch_end = min(batch_start + batch_size, 81)
        rep_vars = ','.join([f'PWGTP{i}' for i in range(batch_start, batch_end)])
        get_str = f'DPHY,DOUT,GRPIP,{rep_vars}'
        url = f'{BASE}?get={get_str}&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'

        retry = 0
        while retry < 3:
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                break
            except Exception as e:
                retry += 1
                if retry == 3:
                    print(f"  FAILED batch {batch_start}-{batch_end-1}: {e}")
                    sys.exit(1)
                time.sleep(2)

        rows = data[1:]

        for i, rep_num in enumerate(range(batch_start, batch_end)):
            wt_idx = 3 + i  # DPHY=0, DOUT=1, GRPIP=2, then replicate weights

            dis_burden = 0; dis_denom = 0
            nondis_burden = 0; nondis_denom = 0
            dis_grpip101 = 0; dis_total = 0

            for row in rows:
                wt = int(row[wt_idx])
                dphy = row[0]
                dout = row[1]
                grpip_raw = row[2]
                if not grpip_raw or grpip_raw == '':
                    continue
                grpip = int(grpip_raw)
                is_disabled = (dphy == '1' or dout == '1')

                if is_disabled:
                    dis_total += wt
                    if grpip == 101:
                        dis_grpip101 += wt
                    elif grpip > 30:
                        dis_burden += wt
                        dis_denom += wt
                    else:
                        dis_denom += wt
                else:
                    if grpip <= 100:
                        if grpip > 30:
                            nondis_burden += wt
                            nondis_denom += wt
                        else:
                            nondis_denom += wt

            d_rate = dis_burden / dis_denom if dis_denom > 0 else 0
            nd_rate = nondis_burden / nondis_denom if nondis_denom > 0 else 0
            rep_dis_cb.append(d_rate)
            rep_nondis_cb.append(nd_rate)
            rep_penalty.append(d_rate - nd_rate)
            rep_grpip101.append(dis_grpip101 / dis_total if dis_total > 0 else 0)

        sys.stdout.write(f"  Replicates {batch_start}-{batch_end-1} done\r")
        sys.stdout.flush()

    # Compute SEs
    def se_from_reps(main_val, reps):
        return math.sqrt((4.0/80.0) * sum((r - main_val)**2 for r in reps))

    se_dis = se_from_reps(main_cb['dis_cb'], rep_dis_cb)
    se_nondis = se_from_reps(main_cb['nondis_cb'], rep_nondis_cb)
    se_penalty = se_from_reps(main_cb['penalty'], rep_penalty)
    se_grpip101 = se_from_reps(main_cb['grpip101'], rep_grpip101)

    cb_results[race_name] = {
        'dis_cb': main_cb['dis_cb'], 'se_dis_cb': se_dis,
        'nondis_cb': main_cb['nondis_cb'], 'se_nondis_cb': se_nondis,
        'penalty': main_cb['penalty'], 'se_penalty': se_penalty,
        'grpip101': main_cb['grpip101'], 'se_grpip101': se_grpip101
    }

    print(f"\n  Disabled CB: {main_cb['dis_cb']*100:.1f}% (SE={se_dis*100:.2f}%)")
    print(f"  Non-disabled CB: {main_cb['nondis_cb']*100:.1f}% (SE={se_nondis*100:.2f}%)")
    print(f"  Penalty: {main_cb['penalty']*100:.1f}pp (SE={se_penalty*100:.2f}pp)")
    print(f"  GRPIP=101: {main_cb['grpip101']*100:.1f}% (SE={se_grpip101*100:.2f}%)")


# === SUMMARY ===
print("\n" + "=" * 60)
print("SUMMARY: All Results with 95% Confidence Intervals")
print("=" * 60)

print("\nDisability Prevalence Among Renter Householders:")
print(f"{'Race':<8} {'Estimate':<12} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = prevalence_results[race]
    print(f"{race:<8} {r['estimate']*100:.2f}%      {r['se']*100:.4f}%  [{r['ci_low']*100:.2f}%, {r['ci_high']*100:.2f}%]")

# Test: do AIAN and White CIs overlap?
aian = prevalence_results['AIAN']
white = prevalence_results['White']
overlap = aian['ci_high'] > white['ci_low'] and white['ci_high'] > aian['ci_low']
print(f"\nAIAN-White CI overlap: {'YES' if overlap else 'NO'}")
if overlap:
    print("  -> AIAN reversal is NOT statistically significant at 95% level")
else:
    print("  -> AIAN reversal IS statistically significant at 95% level")

# Also test via z-test
diff = white['estimate'] - aian['estimate']
se_diff = math.sqrt(white['se']**2 + aian['se']**2)
z = diff / se_diff if se_diff > 0 else 0
p_two_sided = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
print(f"  White - AIAN difference: {diff*100:.2f}pp (SE={se_diff*100:.4f}pp, z={z:.2f}, p={p_two_sided:.4f})")

print("\nCost Burden Rates (Disabled Renters):")
print(f"{'Race':<8} {'CB Rate':<12} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['dis_cb'] - 1.96*r['se_dis_cb']
    hi = r['dis_cb'] + 1.96*r['se_dis_cb']
    print(f"{race:<8} {r['dis_cb']*100:.1f}%       {r['se_dis_cb']*100:.2f}%    [{lo*100:.1f}%, {hi*100:.1f}%]")

print("\nDisability Penalty (pp):")
print(f"{'Race':<8} {'Penalty':<12} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['penalty'] - 1.96*r['se_penalty']
    hi = r['penalty'] + 1.96*r['se_penalty']
    print(f"{race:<8} {r['penalty']*100:.1f}pp      {r['se_penalty']*100:.2f}pp   [{lo*100:.1f}pp, {hi*100:.1f}pp]")

print("\nGRPIP=101 Rate (Disabled Renters):")
print(f"{'Race':<8} {'Rate':<12} {'SE':<10} {'95% CI':<25}")
for race in ['White', 'Black', 'AIAN']:
    r = cb_results[race]
    lo = r['grpip101'] - 1.96*r['se_grpip101']
    hi = r['grpip101'] + 1.96*r['se_grpip101']
    print(f"{race:<8} {r['grpip101']*100:.1f}%       {r['se_grpip101']*100:.2f}%    [{lo*100:.1f}%, {hi*100:.1f}%]")

# Save results to JSON for later use
all_results = {
    'prevalence': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in prevalence_results.items()},
    'cost_burden': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in cb_results.items()}
}
with open(os.path.join(RESULTS_DIR, 'pums_se_results.json'), 'w') as f:
    json.dump(all_results, f, indent=2)
print("\nResults saved to pums_se_results.json")
