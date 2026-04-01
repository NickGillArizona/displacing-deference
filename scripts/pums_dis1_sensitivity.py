"""DIS=1 sensitivity analysis: compare DPHY/DOUT definition vs DIS=1 (any disability)."""
import urllib.request, json, math, time, ssl

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
results = {}

for race_code, race_name in races:
    print(f"\n{'='*50}")
    print(f"{race_name} (RAC1P={race_code})")
    print(f"{'='*50}")

    # Query with DIS variable (any disability recode)
    url = f'{BASE}?get=PWGTP,DIS,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
    print(f"  Querying DIS=1 data...")
    data = fetch_with_retry(url)
    rows = data[1:]

    # Prevalence: DIS=1
    total_wt = 0
    dis_wt = 0
    # Cost burden
    dis_burden = 0; dis_denom = 0
    nondis_burden = 0; nondis_denom = 0

    for row in rows:
        wt = int(row[0])
        dis_flag = row[1]  # DIS: 1=with disability, 2=without
        grpip_raw = row[2]
        total_wt += wt

        is_disabled = (dis_flag == '1')
        if is_disabled:
            dis_wt += wt

        if not grpip_raw or grpip_raw == '':
            continue
        grpip = int(grpip_raw)

        if is_disabled:
            if grpip <= 100:
                if grpip > 30:
                    dis_burden += wt
                dis_denom += wt
        else:
            if grpip <= 100:
                if grpip > 30:
                    nondis_burden += wt
                nondis_denom += wt

    prev = dis_wt / total_wt if total_wt else 0
    dis_cb = dis_burden / dis_denom if dis_denom else 0
    nondis_cb = nondis_burden / nondis_denom if nondis_denom else 0
    penalty = dis_cb - nondis_cb

    results[race_name] = {
        'prevalence': prev,
        'dis_cb': dis_cb,
        'nondis_cb': nondis_cb,
        'penalty': penalty,
        'total_wt': total_wt,
        'dis_wt': dis_wt
    }

    print(f"  DIS=1 Prevalence: {prev*100:.2f}%")
    print(f"  DIS=1 Disabled CB: {dis_cb*100:.1f}%")
    print(f"  DIS=1 Non-disabled CB: {nondis_cb*100:.1f}%")
    print(f"  DIS=1 Penalty: {penalty*100:.1f}pp")

    time.sleep(1)

# Also query DPHY/DOUT for direct comparison (to confirm appendix values)
print(f"\n{'='*50}")
print("DPHY/DOUT comparison (confirming appendix values)")
print(f"{'='*50}")

dphy_results = {}
for race_code, race_name in races:
    url = f'{BASE}?get=PWGTP,DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={race_code}'
    print(f"  Querying {race_name} DPHY/DOUT data...")
    data = fetch_with_retry(url)
    rows = data[1:]

    total_wt = 0; dis_wt = 0
    dis_burden = 0; dis_denom = 0
    nondis_burden = 0; nondis_denom = 0

    for row in rows:
        wt = int(row[0])
        dphy = row[1]; dout = row[2]; grpip_raw = row[3]
        total_wt += wt
        is_disabled = (dphy == '1' or dout == '1')
        if is_disabled:
            dis_wt += wt

        if not grpip_raw or grpip_raw == '':
            continue
        grpip = int(grpip_raw)

        if is_disabled:
            if grpip <= 100:
                if grpip > 30:
                    dis_burden += wt
                dis_denom += wt
        else:
            if grpip <= 100:
                if grpip > 30:
                    nondis_burden += wt
                nondis_denom += wt

    prev = dis_wt / total_wt if total_wt else 0
    dis_cb = dis_burden / dis_denom if dis_denom else 0
    nondis_cb = nondis_burden / nondis_denom if nondis_denom else 0
    penalty = dis_cb - nondis_cb

    dphy_results[race_name] = {
        'prevalence': prev,
        'dis_cb': dis_cb,
        'nondis_cb': nondis_cb,
        'penalty': penalty
    }

    print(f"  {race_name} DPHY/DOUT Prev: {prev*100:.2f}%, CB Penalty: {penalty*100:.1f}pp")
    time.sleep(1)

# Print comparison table
print(f"\n{'='*60}")
print("SENSITIVITY ANALYSIS: DPHY/DOUT vs DIS=1")
print(f"{'='*60}")
print(f"\n{'Metric':<35} {'DPHY/DOUT':<15} {'DIS=1':<15}")
print("-" * 65)
for race in ['White', 'Black', 'AIAN']:
    d = dphy_results[race]
    r = results[race]
    print(f"{race + ' prevalence':<35} {d['prevalence']*100:.2f}%        {r['prevalence']*100:.2f}%")
for race in ['White', 'Black', 'AIAN']:
    d = dphy_results[race]
    r = results[race]
    print(f"{race + ' disability penalty':<35} {d['penalty']*100:.1f}pp        {r['penalty']*100:.1f}pp")

# Save results
all_results = {
    'dis1': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in results.items()},
    'dphy_dout': {k: {kk: float(vv) for kk, vv in v.items()} for k, v in dphy_results.items()}
}
with open('pums_sensitivity_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print("\nResults saved to pums_sensitivity_results.json")
