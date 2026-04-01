"""
Phase 2: Recompute all Note statistics using the Haiku per-claim extraction data.
Outputs a comprehensive JSON summary for use in Note and Appendix revisions.
"""
import json
import math
from collections import Counter, defaultdict

# Load data
with open('C:/Users/nickg/IdeaProjects/MFH-Java-Work/allFHAcases/recentcases/RAClassification_DB_claims_extraction.json', encoding='utf-8') as f:
    data = json.load(f)

with open('C:/Users/nickg/IdeaProjects/MFH-Java-Work/allFHAcases/recentcases/RAClassification_DB_resolved_20260328_085823.json', encoding='utf-8') as f:
    pipeline = json.load(f)

pipe_lookup = {r.get('source_file', ''): r for r in pipeline}
exts = [d['extraction'] for d in data]

# Flatten claims
all_claims = []
for d in data:
    e = d['extraction']
    for c in e.get('fha_claims', []):
        c['_sf'] = d['source_file']
        c['_pro_se'] = e.get('pro_se', False)
        c['_counsel'] = e.get('counsel_named', False)
        c['_plaintiff_type'] = e.get('plaintiff_type', '')
        c['_defendant_type'] = e.get('defendant_type', '')
        c['_housing_type'] = e.get('housing_type', '')
        c['_disability_cat'] = e.get('disability_category', '')
        c['_interactive'] = e.get('interactive_process_discussed', False)
        c['_delay'] = e.get('delay_as_denial', False)
        c['_loper'] = e.get('loper_bright_cited', False)
        c['_iqbal'] = e.get('iqbal_twombly_cited', False)
        c['_year'] = e.get('year', 0)
        c['_race'] = e.get('race_mentioned', False)
        all_claims.append(c)

ra_claims = [c for c in all_claims if c.get('theory') == 'REASONABLE_ACCOMMODATION']
ra_merits = [c for c in ra_claims if c.get('merits_reached') == 'YES']
ra_merits_partial = [c for c in ra_claims if c.get('merits_reached') in ('YES', 'PARTIAL')]
ra_no_merits = [c for c in ra_claims if c.get('merits_reached') == 'NO']

def wilson_ci(successes, total, z=1.96):
    """Wilson score confidence interval for proportions."""
    if total == 0:
        return (0, 0, 0)
    p = successes / total
    denom = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    return (max(0, center - spread), center, min(1, center + spread))

def odds_ratio(a, b, c, d):
    """2x2 odds ratio with Haldane correction."""
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    return (a * d) / (b * c)

results = {}

# ============================================================
# 1. DATASET COMPOSITION
# ============================================================
print("=" * 70)
print("1. DATASET COMPOSITION")
print("=" * 70)

total_cases = len(data)
total_claims = len(all_claims)
zero_claim = sum(1 for e in exts if len(e.get('fha_claims', [])) == 0)

results['dataset'] = {
    'total_cases': total_cases,
    'total_claims': total_claims,
    'zero_claim_cases': zero_claim,
    'avg_claims_per_case': round(total_claims / total_cases, 2),
    'pro_se_cases': sum(1 for e in exts if e.get('pro_se')),
    'pro_se_pct': round(sum(1 for e in exts if e.get('pro_se')) / total_cases * 100, 1),
    'disability_alleged': sum(1 for e in exts if e.get('disability_alleged')),
    'is_ra_case': sum(1 for e in exts if e.get('is_ra_case')),
    'ra_claims': len(ra_claims),
    'ra_merits_claims': len(ra_merits),
    'ra_merits_partial_claims': len(ra_merits_partial),
    'ra_no_merits_claims': len(ra_no_merits),
}

print(f"Cases: {total_cases}, Claims: {total_claims}")
print(f"RA claims: {len(ra_claims)} ({len(ra_claims)/total_claims*100:.1f}%)")
print(f"RA merits=YES: {len(ra_merits)}, merits=NO: {len(ra_no_merits)}")

# Three populations (case-level)
ra_merits_cases = set()
ra_no_merits_cases = set()
non_ra_cases = set()
for d in data:
    sf = d['source_file']
    e = d['extraction']
    claims = e.get('fha_claims', [])
    has_ra = any(c.get('theory') == 'REASONABLE_ACCOMMODATION' for c in claims)
    has_ra_merits = any(
        c.get('theory') == 'REASONABLE_ACCOMMODATION' and c.get('merits_reached') in ('YES', 'PARTIAL')
        for c in claims
    )
    if has_ra_merits:
        ra_merits_cases.add(sf)
    elif has_ra:
        ra_no_merits_cases.add(sf)
    else:
        non_ra_cases.add(sf)

results['populations'] = {
    'ra_merits_cases': len(ra_merits_cases),
    'ra_no_merits_cases': len(ra_no_merits_cases),
    'non_ra_cases': len(non_ra_cases),
}
print(f"\nPopulations: RA merits={len(ra_merits_cases)}, RA no-merits={len(ra_no_merits_cases)}, Non-RA={len(non_ra_cases)}")


# ============================================================
# 2. ACCOMMODATION TYPE WIN RATES (RA merits only)
# ============================================================
print("\n" + "=" * 70)
print("2. ACCOMMODATION TYPE WIN RATES (RA merits_reached=YES, n=175)")
print("=" * 70)

at_data = defaultdict(lambda: {'pw': 0, 'dw': 0, 'mixed': 0, 'other': 0, 'total': 0})
for c in ra_merits:
    at = c.get('accommodation_type', 'OTHER')
    out = c.get('outcome', '')
    at_data[at]['total'] += 1
    if out == 'PLAINTIFF':
        at_data[at]['pw'] += 1
    elif out == 'DEFENDANT':
        at_data[at]['dw'] += 1
    elif out == 'MIXED':
        at_data[at]['mixed'] += 1
    else:
        at_data[at]['other'] += 1

results['accommodation_type_win_rates'] = {}
print(f"\n{'Category':35s} {'n':>4s} {'PW':>4s} {'DW':>4s} {'MIX':>4s} {'PW%':>7s} {'95% CI':>15s}")
print("-" * 80)
for cat in sorted(at_data.keys(), key=lambda x: -at_data[x]['total']):
    d = at_data[cat]
    n = d['total']
    pw = d['pw']
    pct = pw / n * 100 if n > 0 else 0
    lo, mid, hi = wilson_ci(pw, n)
    flag = " *" if n < 10 else ""
    print(f"  {cat:33s} {n:4d} {pw:4d} {d['dw']:4d} {d['mixed']:4d} {pct:6.1f}% [{lo*100:5.1f}%-{hi*100:5.1f}%]{flag}")
    results['accommodation_type_win_rates'][cat] = {
        'n': n, 'pw': pw, 'dw': d['dw'], 'mixed': d['mixed'],
        'pw_pct': round(pct, 1),
        'ci_lower': round(lo * 100, 1), 'ci_upper': round(hi * 100, 1),
        'small_n': n < 10,
    }


# ============================================================
# 3. PRO SE ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("3. PRO SE ANALYSIS")
print("=" * 70)

# 3a. RA merits: pro se vs represented
pro_ra_merits = [c for c in ra_merits if c['_pro_se']]
rep_ra_merits = [c for c in ra_merits if not c['_pro_se']]
pro_pw = sum(1 for c in pro_ra_merits if c.get('outcome') == 'PLAINTIFF')
rep_pw = sum(1 for c in rep_ra_merits if c.get('outcome') == 'PLAINTIFF')

print(f"\nRA merits claims:")
print(f"  Pro se:       {pro_pw}/{len(pro_ra_merits)} = {pro_pw/len(pro_ra_merits)*100:.1f}% PW" if pro_ra_merits else "  Pro se: 0 claims")
print(f"  Represented:  {rep_pw}/{len(rep_ra_merits)} = {rep_pw/len(rep_ra_merits)*100:.1f}% PW" if rep_ra_merits else "  Represented: 0 claims")

# OR
if pro_ra_merits and rep_ra_merits:
    a = pro_pw
    b = len(pro_ra_merits) - pro_pw
    c = rep_pw
    d_val = len(rep_ra_merits) - rep_pw
    or_val = odds_ratio(a, b, c, d_val)
    print(f"  Odds ratio (pro se vs represented): {or_val:.2f}")

results['pro_se'] = {
    'ra_merits_pro_se': {'n': len(pro_ra_merits), 'pw': pro_pw, 'pw_pct': round(pro_pw/len(pro_ra_merits)*100, 1) if pro_ra_merits else 0},
    'ra_merits_represented': {'n': len(rep_ra_merits), 'pw': rep_pw, 'pw_pct': round(rep_pw/len(rep_ra_merits)*100, 1) if rep_ra_merits else 0},
}

# 3b. Per-category pro se vs represented (RA merits)
print(f"\n{'Category':30s} {'ProSe n':>7s} {'ProSe PW%':>10s} {'Rep n':>6s} {'Rep PW%':>9s}")
print("-" * 70)
cats = sorted(set(c.get('accommodation_type','') for c in ra_merits))
for cat in cats:
    pro = [c for c in pro_ra_merits if c.get('accommodation_type') == cat]
    rep = [c for c in rep_ra_merits if c.get('accommodation_type') == cat]
    pro_p = sum(1 for c in pro if c.get('outcome') == 'PLAINTIFF')
    rep_p = sum(1 for c in rep if c.get('outcome') == 'PLAINTIFF')
    pro_pct = pro_p / len(pro) * 100 if pro else 0
    rep_pct = rep_p / len(rep) * 100 if rep else 0
    print(f"  {cat:28s} {len(pro):5d}   {pro_pct:8.1f}%  {len(rep):4d}  {rep_pct:7.1f}%")


# ============================================================
# 4. GALANTER / PLAINTIFF TYPE (RA merits)
# ============================================================
print("\n" + "=" * 70)
print("4. GALANTER ANALYSIS — PLAINTIFF TYPE (RA merits)")
print("=" * 70)

pt_data = defaultdict(lambda: {'pw': 0, 'total': 0})
for c in ra_merits:
    pt = c['_plaintiff_type']
    pt_data[pt]['total'] += 1
    if c.get('outcome') == 'PLAINTIFF':
        pt_data[pt]['pw'] += 1

print(f"\n{'Plaintiff Type':30s} {'n':>5s} {'PW':>4s} {'PW%':>7s} {'95% CI':>15s}")
print("-" * 65)
results['galanter'] = {}
for pt in sorted(pt_data.keys(), key=lambda x: -pt_data[x]['total']):
    d = pt_data[pt]
    pct = d['pw'] / d['total'] * 100 if d['total'] else 0
    lo, hi_val, _ = wilson_ci(d['pw'], d['total'])
    _, _, hi = wilson_ci(d['pw'], d['total'])
    print(f"  {pt:28s} {d['total']:5d} {d['pw']:4d} {pct:6.1f}% [{lo*100:5.1f}%-{hi*100:5.1f}%]")
    results['galanter'][pt] = {'n': d['total'], 'pw': d['pw'], 'pw_pct': round(pct, 1)}


# ============================================================
# 5. INTERACTIVE PROCESS & DELAY-AS-DENIAL (RA merits cases)
# ============================================================
print("\n" + "=" * 70)
print("5. INTERACTIVE PROCESS & DELAY-AS-DENIAL (RA merits)")
print("=" * 70)

# Case-level (since these are case-level fields)
ra_merits_case_data = []
for d in data:
    sf = d['source_file']
    if sf not in ra_merits_cases:
        continue
    e = d['extraction']
    # Get the RA merits claim outcome(s)
    ra_outcomes = [c.get('outcome') for c in e.get('fha_claims', [])
                   if c.get('theory') == 'REASONABLE_ACCOMMODATION' and c.get('merits_reached') in ('YES', 'PARTIAL')]
    has_pw = 'PLAINTIFF' in ra_outcomes
    ra_merits_case_data.append({
        'sf': sf,
        'interactive': e.get('interactive_process_discussed', False),
        'delay': e.get('delay_as_denial', False),
        'pw': has_pw,
        'pro_se': e.get('pro_se', False),
    })

ip_yes = [c for c in ra_merits_case_data if c['interactive']]
ip_no = [c for c in ra_merits_case_data if not c['interactive']]
ip_yes_pw = sum(1 for c in ip_yes if c['pw'])
ip_no_pw = sum(1 for c in ip_no if c['pw'])

print(f"\nInteractive process discussed:")
print(f"  YES: {ip_yes_pw}/{len(ip_yes)} PW ({ip_yes_pw/len(ip_yes)*100:.1f}%)" if ip_yes else "  YES: 0")
print(f"  NO:  {ip_no_pw}/{len(ip_no)} PW ({ip_no_pw/len(ip_no)*100:.1f}%)" if ip_no else "  NO: 0")
if ip_yes and ip_no:
    ip_or = odds_ratio(ip_yes_pw, len(ip_yes) - ip_yes_pw, ip_no_pw, len(ip_no) - ip_no_pw)
    print(f"  OR: {ip_or:.2f}")

dad_yes = [c for c in ra_merits_case_data if c['delay']]
dad_no = [c for c in ra_merits_case_data if not c['delay']]
dad_yes_pw = sum(1 for c in dad_yes if c['pw'])
dad_no_pw = sum(1 for c in dad_no if c['pw'])

print(f"\nDelay as denial:")
print(f"  YES: {dad_yes_pw}/{len(dad_yes)} PW ({dad_yes_pw/len(dad_yes)*100:.1f}%)" if dad_yes else "  YES: 0")
print(f"  NO:  {dad_no_pw}/{len(dad_no)} PW ({dad_no_pw/len(dad_no)*100:.1f}%)" if dad_no else "  NO: 0")
if dad_yes and dad_no:
    dad_or = odds_ratio(dad_yes_pw, len(dad_yes) - dad_yes_pw, dad_no_pw, len(dad_no) - dad_no_pw)
    print(f"  OR: {dad_or:.2f}")

results['interactive_process'] = {
    'ip_yes': {'n': len(ip_yes), 'pw': ip_yes_pw},
    'ip_no': {'n': len(ip_no), 'pw': ip_no_pw},
}
results['delay_as_denial'] = {
    'dad_yes': {'n': len(dad_yes), 'pw': dad_yes_pw},
    'dad_no': {'n': len(dad_no), 'pw': dad_no_pw},
}


# ============================================================
# 6. PER-THEORY WIN RATES (merits=YES, all theories)
# ============================================================
print("\n" + "=" * 70)
print("6. PER-THEORY WIN RATES (merits_reached=YES)")
print("=" * 70)

merits_claims = [c for c in all_claims if c.get('merits_reached') == 'YES']
theory_data = defaultdict(lambda: {'pw': 0, 'dw': 0, 'total': 0})
for c in merits_claims:
    t = c.get('theory', '')
    theory_data[t]['total'] += 1
    if c.get('outcome') == 'PLAINTIFF':
        theory_data[t]['pw'] += 1
    elif c.get('outcome') == 'DEFENDANT':
        theory_data[t]['dw'] += 1

results['theory_win_rates'] = {}
print(f"\n{'Theory':35s} {'n':>5s} {'PW':>4s} {'DW':>5s} {'PW%':>7s} {'95% CI':>15s}")
print("-" * 75)
for t in sorted(theory_data.keys(), key=lambda x: -theory_data[x]['total']):
    d = theory_data[t]
    pct = d['pw'] / d['total'] * 100 if d['total'] else 0
    lo, _, hi = wilson_ci(d['pw'], d['total'])
    print(f"  {t:33s} {d['total']:5d} {d['pw']:4d} {d['dw']:5d} {pct:6.1f}% [{lo*100:5.1f}%-{hi*100:5.1f}%]")
    results['theory_win_rates'][t] = {
        'n': d['total'], 'pw': d['pw'], 'dw': d['dw'],
        'pw_pct': round(pct, 1),
        'ci_lower': round(lo * 100, 1), 'ci_upper': round(hi * 100, 1),
    }


# ============================================================
# 7. LOPER BRIGHT (pre/post)
# ============================================================
print("\n" + "=" * 70)
print("7. LOPER BRIGHT PRE/POST ANALYSIS")
print("=" * 70)

# Loper Bright decided June 28, 2024
# Pre: year <= 2023 or (year == 2024 and before June)
# Since we only have year, use year <= 2023 as pre, year >= 2025 as post, 2024 as transition

for period_label, year_filter in [('Pre-LB (<=2023)', lambda y: y and y <= 2023),
                                   ('2024 (transition)', lambda y: y == 2024),
                                   ('Post-LB (>=2025)', lambda y: y and y >= 2025)]:
    period_ra = [c for c in ra_merits if year_filter(c.get('_year', 0))]
    pw = sum(1 for c in period_ra if c.get('outcome') == 'PLAINTIFF')
    n = len(period_ra)
    pct = pw / n * 100 if n else 0
    print(f"  {period_label:25s} {pw:3d}/{n:3d} = {pct:5.1f}% PW")

# Also check: RA claims that cite Loper Bright
lb_ra = [c for c in ra_merits if c.get('_loper')]
print(f"\n  RA merits claims citing Loper Bright: {len(lb_ra)}")
if lb_ra:
    lb_pw = sum(1 for c in lb_ra if c.get('outcome') == 'PLAINTIFF')
    print(f"  Of those: {lb_pw}/{len(lb_ra)} PW")

# Broader: all claims citing Loper Bright
lb_all = [c for c in all_claims if c.get('_loper')]
print(f"  All claims in cases citing LB: {len(lb_all)}")

results['loper_bright'] = {
    'ra_merits_citing_lb': len(lb_ra),
    'total_cases_citing_lb': sum(1 for e in exts if e.get('loper_bright_cited')),
}


# ============================================================
# 8. DEFENDANT TYPE (RA merits)
# ============================================================
print("\n" + "=" * 70)
print("8. DEFENDANT TYPE (RA merits)")
print("=" * 70)

dt_data = defaultdict(lambda: {'pw': 0, 'total': 0})
for c in ra_merits:
    dt = c['_defendant_type']
    dt_data[dt]['total'] += 1
    if c.get('outcome') == 'PLAINTIFF':
        dt_data[dt]['pw'] += 1

results['defendant_type'] = {}
print(f"\n{'Defendant Type':30s} {'n':>5s} {'PW':>4s} {'PW%':>7s}")
print("-" * 50)
for dt in sorted(dt_data.keys(), key=lambda x: -dt_data[x]['total']):
    d = dt_data[dt]
    pct = d['pw'] / d['total'] * 100 if d['total'] else 0
    print(f"  {dt:28s} {d['total']:5d} {d['pw']:4d} {pct:6.1f}%")
    results['defendant_type'][dt] = {'n': d['total'], 'pw': d['pw'], 'pw_pct': round(pct, 1)}


# ============================================================
# 9. RACE INTERACTION (RA merits)
# ============================================================
print("\n" + "=" * 70)
print("9. RACE MENTIONED (RA merits)")
print("=" * 70)

race_yes = [c for c in ra_merits if c.get('_race')]
race_no = [c for c in ra_merits if not c.get('_race')]
race_yes_pw = sum(1 for c in race_yes if c.get('outcome') == 'PLAINTIFF')
race_no_pw = sum(1 for c in race_no if c.get('outcome') == 'PLAINTIFF')

print(f"  Race mentioned: {race_yes_pw}/{len(race_yes)} PW ({race_yes_pw/len(race_yes)*100:.1f}%)" if race_yes else "  Race mentioned: 0")
print(f"  No race:        {race_no_pw}/{len(race_no)} PW ({race_no_pw/len(race_no)*100:.1f}%)" if race_no else "  No race: 0")

if race_yes and race_no:
    race_or = odds_ratio(race_yes_pw, len(race_yes) - race_yes_pw, race_no_pw, len(race_no) - race_no_pw)
    print(f"  OR: {race_or:.2f}")

results['race'] = {
    'race_yes': {'n': len(race_yes), 'pw': race_yes_pw},
    'race_no': {'n': len(race_no), 'pw': race_no_pw},
}


# ============================================================
# 10. RA STANDARD APPLIED
# ============================================================
print("\n" + "=" * 70)
print("10. RA STANDARD APPLIED (RA merits)")
print("=" * 70)

ra_std = defaultdict(lambda: {'pw': 0, 'total': 0})
for c in ra_merits:
    std = c.get('ra_standard_applied', 'N/A')
    ra_std[std]['total'] += 1
    if c.get('outcome') == 'PLAINTIFF':
        ra_std[std]['pw'] += 1

print(f"\n{'Standard':40s} {'n':>5s} {'PW':>4s} {'PW%':>7s}")
print("-" * 60)
for std in sorted(ra_std.keys(), key=lambda x: -ra_std[x]['total']):
    d = ra_std[std]
    pct = d['pw'] / d['total'] * 100 if d['total'] else 0
    print(f"  {std:38s} {d['total']:5d} {d['pw']:4d} {pct:6.1f}%")


# ============================================================
# SAVE RESULTS
# ============================================================
output_path = 'C:/Users/nickg/OneDrive/Documents/Note/haiku_extraction_analysis.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n\nSaved analysis to {output_path}")
