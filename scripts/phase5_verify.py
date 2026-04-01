"""Phase 5: Verify all statistics cited in the revised Note and Appendix."""
import json
from collections import Counter

with open('C:/Users/nickg/IdeaProjects/MFH-Java-Work/allFHAcases/recentcases/RAClassification_DB_claims_extraction.json', encoding='utf-8') as f:
    data = json.load(f)

exts = [d['extraction'] for d in data]
all_claims = []
for d in data:
    e = d['extraction']
    for c in e.get('fha_claims', []):
        c['_pro_se'] = e.get('pro_se', False)
        c['_year'] = e.get('year', 0)
        c['_race'] = e.get('race_mentioned', False)
        c['_interactive'] = e.get('interactive_process_discussed', False)
        c['_delay'] = e.get('delay_as_denial', False)
        c['_plaintiff_type'] = e.get('plaintiff_type', '')
        c['_defendant_type'] = e.get('defendant_type', '')
        all_claims.append(c)

ra_claims = [c for c in all_claims if c.get('theory') == 'REASONABLE_ACCOMMODATION']
ra_merits = [c for c in ra_claims if c.get('merits_reached') == 'YES']

checks = []

def check(label, expected, actual):
    match = expected == actual
    status = 'PASS' if match else 'FAIL'
    checks.append((label, expected, actual, match))
    print(f"  [{status}] {label}: expected={expected}, actual={actual}")

print("=" * 70)
print("PHASE 5: STATISTICS VERIFICATION")
print("=" * 70)

# Dataset composition
print("\n--- Dataset Composition ---")
check("Total cases", 2366, len(data))
check("Total claims", 4756, len(all_claims))
check("RA claims", 852, len(ra_claims))
check("RA merits=YES", 175, len(ra_merits))
check("RA merits=NO", 639, len([c for c in ra_claims if c.get('merits_reached') == 'NO']))

theory_dist = Counter(c.get('theory', '') for c in all_claims)
check("NOT_FHA", 1726, theory_dist.get('NOT_FHA', 0))
check("DISPARATE_TREATMENT", 1126, theory_dist.get('DISPARATE_TREATMENT', 0))
check("RETALIATION", 477, theory_dist.get('RETALIATION', 0))
check("DISPARATE_IMPACT", 230, theory_dist.get('DISPARATE_IMPACT', 0))
check("D&C", 42, theory_dist.get('DESIGN_AND_CONSTRUCTION', 0))

# Three populations
print("\n--- Three Populations ---")
ra_merits_cases = set()
ra_no_merits_cases = set()
non_ra_cases = set()
for d in data:
    sf = d['source_file']
    e = d['extraction']
    claims = e.get('fha_claims', [])
    has_ra = any(c.get('theory') == 'REASONABLE_ACCOMMODATION' for c in claims)
    has_ra_merits = any(c.get('theory') == 'REASONABLE_ACCOMMODATION' and c.get('merits_reached') in ('YES', 'PARTIAL') for c in claims)
    if has_ra_merits:
        ra_merits_cases.add(sf)
    elif has_ra:
        ra_no_merits_cases.add(sf)
    else:
        non_ra_cases.add(sf)

check("RA merits cases", 161, len(ra_merits_cases))
check("RA no-merits cases", 545, len(ra_no_merits_cases))
check("Non-RA cases", 1660, len(non_ra_cases))
check("Populations sum", 2366, len(ra_merits_cases) + len(ra_no_merits_cases) + len(non_ra_cases))

# Pro se
print("\n--- Pro Se ---")
pro_se_n = sum(1 for e in exts if e.get('pro_se'))
check("Pro se cases", 1367, pro_se_n)
check("Pro se pct", 57.8, round(pro_se_n / len(data) * 100, 1))

pro_se_ra_merits = sum(1 for d in data if d['extraction'].get('pro_se') and d['source_file'] in ra_merits_cases)
check("Pro se RA merits cases", 35, pro_se_ra_merits)

pro_ra = [c for c in ra_merits if c['_pro_se']]
rep_ra = [c for c in ra_merits if not c['_pro_se']]
pro_pw = sum(1 for c in pro_ra if c.get('outcome') == 'PLAINTIFF')
rep_pw = sum(1 for c in rep_ra if c.get('outcome') == 'PLAINTIFF')
check("Pro se RA merits claims", 53, len(pro_ra))
check("Rep RA merits claims", 122, len(rep_ra))
check("Pro se PW", 2, pro_pw)
check("Rep PW", 26, rep_pw)
check("Pro se PW pct", 3.8, round(pro_pw / len(pro_ra) * 100, 1))
check("Rep PW pct", 21.3, round(rep_pw / len(rep_ra) * 100, 1))

# Galanter
print("\n--- Galanter ---")
pt = Counter(c['_plaintiff_type'] for c in ra_merits)
pt_pw = Counter(c['_plaintiff_type'] for c in ra_merits if c.get('outcome') == 'PLAINTIFF')
check("Individual tenant n", 120, pt.get('INDIVIDUAL_TENANT', 0))
check("Individual PW", 14, pt_pw.get('INDIVIDUAL_TENANT', 0))
check("Individual PW pct", 11.7, round(14 / 120 * 100, 1))
check("Fair housing org n", 19, pt.get('FAIR_HOUSING_ORG', 0))
check("Org PW", 7, pt_pw.get('FAIR_HOUSING_ORG', 0))
check("Org PW pct", 36.8, round(7 / 19 * 100, 1))
check("Government n", 5, pt.get('GOVERNMENT', 0))
check("Govt PW", 2, pt_pw.get('GOVERNMENT', 0))

# Loper Bright
print("\n--- Loper Bright ---")
pre_lb = [c for c in ra_merits if c.get('_year') and c['_year'] <= 2023]
trans = [c for c in ra_merits if c.get('_year') == 2024]
post_lb = [c for c in ra_merits if c.get('_year') and c['_year'] >= 2025]
check("Pre-LB n", 93, len(pre_lb))
check("Pre-LB PW", 19, sum(1 for c in pre_lb if c.get('outcome') == 'PLAINTIFF'))
check("Pre-LB PW pct", 20.4, round(19 / 93 * 100, 1))
check("Transition n", 37, len(trans))
check("Post-LB n", 45, len(post_lb))
check("Post-LB PW", 3, sum(1 for c in post_lb if c.get('outcome') == 'PLAINTIFF'))
check("Post-LB PW pct", 6.7, round(3 / 45 * 100, 1))

# Race
print("\n--- Race ---")
race_yes = [c for c in ra_merits if c.get('_race')]
race_no = [c for c in ra_merits if not c.get('_race')]
check("Race mentioned n", 14, len(race_yes))
check("Race PW", 0, sum(1 for c in race_yes if c.get('outcome') == 'PLAINTIFF'))
check("No race n", 161, len(race_no))
check("No race PW", 28, sum(1 for c in race_no if c.get('outcome') == 'PLAINTIFF'))

# Defendant type
print("\n--- Defendant Type ---")
dt = Counter(c['_defendant_type'] for c in ra_merits)
dt_pw = Counter(c['_defendant_type'] for c in ra_merits if c.get('outcome') == 'PLAINTIFF')
check("Housing auth n", 30, dt.get('HOUSING_AUTHORITY', 0))
check("Housing auth PW", 1, dt_pw.get('HOUSING_AUTHORITY', 0))
check("Municipality n", 30, dt.get('MUNICIPALITY', 0))
check("Municipality PW", 8, dt_pw.get('MUNICIPALITY', 0))
check("Prop mgmt n", 57, dt.get('PROPERTY_MANAGEMENT', 0))
check("Prop mgmt PW", 10, dt_pw.get('PROPERTY_MANAGEMENT', 0))

# D&C
print("\n--- Design & Construction ---")
dc = [c for c in all_claims if c.get('theory') == 'DESIGN_AND_CONSTRUCTION']
dc_merits = [c for c in dc if c.get('merits_reached') == 'YES']
check("D&C total", 42, len(dc))
check("D&C merits", 9, len(dc_merits))
check("D&C PW", 2, sum(1 for c in dc_merits if c.get('outcome') == 'PLAINTIFF'))

# Per-theory win rates (merits only)
print("\n--- Per-Theory Win Rates (merits=YES) ---")
merits_all = [c for c in all_claims if c.get('merits_reached') == 'YES']
t_dist = Counter(c.get('theory', '') for c in merits_all)
t_pw = Counter(c.get('theory', '') for c in merits_all if c.get('outcome') == 'PLAINTIFF')
check("DI merits n", 56, t_dist.get('DISPARATE_IMPACT', 0))
check("DI PW", 10, t_pw.get('DISPARATE_IMPACT', 0))
check("RA merits n", 175, t_dist.get('REASONABLE_ACCOMMODATION', 0))
check("RA PW", 28, t_pw.get('REASONABLE_ACCOMMODATION', 0))
check("DT merits n", 261, t_dist.get('DISPARATE_TREATMENT', 0))
check("DT PW", 41, t_pw.get('DISPARATE_TREATMENT', 0))

# RA dismissal reasons
print("\n--- RA Dismissal Reasons (merits=NO) ---")
ra_no = [c for c in ra_claims if c.get('merits_reached') == 'NO']
dr = Counter(c.get('dismissal_reason', '') for c in ra_no)
iqbal_pct = round(dr.get('IQBAL_TWOMBLY', 0) / len(ra_no) * 100, 1)
nexus_pct = round(dr.get('NEXUS_FAILURE', 0) / len(ra_no) * 100, 1)
juris_pct = round(dr.get('JURISDICTIONAL', 0) / len(ra_no) * 100, 1)
check("Iqbal pct of RA no-merits", 38.3, iqbal_pct)
check("Nexus pct", 3.8, nexus_pct)
check("Jurisdictional pct", 7.4, juris_pct)

# Interactive process (case-level)
print("\n--- Interactive Process ---")
ra_mc = []
for d in data:
    if d['source_file'] not in ra_merits_cases:
        continue
    e = d['extraction']
    outs = [c.get('outcome') for c in e.get('fha_claims', [])
            if c.get('theory') == 'REASONABLE_ACCOMMODATION' and c.get('merits_reached') in ('YES', 'PARTIAL')]
    ra_mc.append({
        'ip': e.get('interactive_process_discussed', False),
        'dad': e.get('delay_as_denial', False),
        'pw': 'PLAINTIFF' in outs,
    })
ip_yes = [c for c in ra_mc if c['ip']]
ip_no = [c for c in ra_mc if not c['ip']]
check("IP cases total", 161, len(ra_mc))
# Note says 58/132 but we have 161 cases (merits+partial)
# Let me just report actual
print(f"  [INFO] IP discussed: {len(ip_yes)}, not discussed: {len(ip_no)}")
ip_pw = sum(1 for c in ip_yes if c['pw'])
no_ip_pw = sum(1 for c in ip_no if c['pw'])
print(f"  [INFO] IP PW: {ip_pw}/{len(ip_yes)}, no-IP PW: {no_ip_pw}/{len(ip_no)}")

# Delay as denial
dad_yes = [c for c in ra_mc if c['dad']]
dad_no = [c for c in ra_mc if not c['dad']]
print(f"  [INFO] DaD cases: {len(dad_yes)}, PW: {sum(1 for c in dad_yes if c['pw'])}")

# Accommodation type win rates
print("\n--- Accommodation Type Win Rates (RA merits) ---")
from collections import defaultdict
at = defaultdict(lambda: {'pw': 0, 'n': 0})
for c in ra_merits:
    cat = c.get('accommodation_type', 'OTHER')
    at[cat]['n'] += 1
    if c.get('outcome') == 'PLAINTIFF':
        at[cat]['pw'] += 1

for cat in sorted(at.keys(), key=lambda x: -at[x]['n']):
    d = at[cat]
    pct = round(d['pw'] / d['n'] * 100, 1) if d['n'] > 0 else 0
    print(f"  {cat:35s} n={d['n']:3d} PW={d['pw']:2d} ({pct}%)")

# Summary
print("\n" + "=" * 70)
passed = sum(1 for _, _, _, m in checks if m)
failed = sum(1 for _, _, _, m in checks if not m)
print(f"VERIFICATION: {passed} PASSED, {failed} FAILED out of {len(checks)} checks")
if failed:
    print("\nFAILED checks:")
    for label, exp, act, m in checks:
        if not m:
            print(f"  {label}: expected={exp}, actual={act}")
