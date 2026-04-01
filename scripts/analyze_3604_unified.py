"""Comprehensive analysis of the unified 3604 database."""
import json
from collections import Counter

DB_PATH = r'C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\FHA_3604_Database_unified_20260328_104352.json'

with open(DB_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

fha = [r for r in data if r.get('screening_result', '').upper() != 'NO']
print(f'=== 3604 DATABASE ANALYSIS (n={len(fha)}) ===\n')

DECIDED = ('PLAINTIFF_WIN', 'DEFENDANT_WIN', 'MIXED')

def win_stats(subset, label=''):
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if not d:
        return
    p = sum(1 for r in d if r.get('outcome') == 'PLAINTIFF_WIN')
    m = sum(1 for r in d if r.get('outcome') == 'MIXED')
    dw = sum(1 for r in d if r.get('outcome') == 'DEFENDANT_WIN')
    broad = p + m
    prefix = f'  {label:45s}' if label else '  '
    print(f'{prefix} n={len(d):>4}  PW={p:>3} ({100*p/len(d):5.1f}%)  MX={m:>3}  DW={dw:>3}  Broad={100*broad/len(d):5.1f}%')

# 1. Outcome distribution
print('--- OUTCOME DISTRIBUTION ---')
outcomes = Counter(r.get('outcome', 'UNKNOWN') for r in fha)
for o, c in outcomes.most_common():
    print(f'  {o:25s} {c:>5} ({100*c/len(fha):5.1f}%)')

# Overall win rate
print('\n--- OVERALL WIN RATE ---')
win_stats(fha, 'ALL')

# 2. Year by year
print('\n--- YEAR BY YEAR ---')
years = sorted(set(r.get('year') for r in fha if r.get('year')))
for y in years:
    subset = [r for r in fha if r.get('year') == y]
    win_stats(subset, str(y))

# 3. Pre/Post Loper Bright
print('\n--- PRE/POST LOPER BRIGHT ---')
pre_lb = [r for r in fha if r.get('year') and int(r.get('year', 0)) <= 2023]
post_lb = [r for r in fha if r.get('year') and int(r.get('year', 0)) >= 2024]
win_stats(pre_lb, 'Pre-LB (<=2023)')
win_stats(post_lb, 'Post-LB (2024+)')

# Chi-squared for pre/post
d_pre = [r for r in pre_lb if r.get('outcome') in DECIDED]
d_post = [r for r in post_lb if r.get('outcome') in DECIDED]
if d_pre and d_post:
    pw_pre = sum(1 for r in d_pre if r.get('outcome') == 'PLAINTIFF_WIN')
    pw_post = sum(1 for r in d_post if r.get('outcome') == 'PLAINTIFF_WIN')
    n_pre = len(d_pre)
    n_post = len(d_post)
    # 2x2 chi-squared (PW vs not-PW)
    from scipy import stats as scipy_stats
    import numpy as np
    table = np.array([[pw_pre, n_pre - pw_pre], [pw_post, n_post - pw_post]])
    chi2, p_val, dof, expected = scipy_stats.chi2_contingency(table)
    print(f'  Chi-squared (PW strict): chi2={chi2:.2f}, p={p_val:.4f}')

    # Broad: PW+MX vs DW
    broad_pre = sum(1 for r in d_pre if r.get('outcome') in ('PLAINTIFF_WIN', 'MIXED'))
    broad_post = sum(1 for r in d_post if r.get('outcome') in ('PLAINTIFF_WIN', 'MIXED'))
    dw_pre = n_pre - broad_pre
    dw_post = n_post - broad_post
    table2 = np.array([[broad_pre, dw_pre], [broad_post, dw_post]])
    chi2b, p_valb, _, _ = scipy_stats.chi2_contingency(table2)
    print(f'  Chi-squared (Broad): chi2={chi2b:.2f}, p={p_valb:.4f}')

# 4. Accommodation type
print('\n--- BY ACCOMMODATION TYPE ---')
acc_types = Counter(r.get('accommodation_type', 'UNKNOWN') for r in fha)
for acc, _ in sorted(acc_types.items(), key=lambda x: -x[1]):
    subset = [r for r in fha if r.get('accommodation_type') == acc]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 5:
        win_stats(subset, acc)

# 5. Defendant type
print('\n--- BY DEFENDANT TYPE ---')
def_types = Counter(r.get('defendant_type', 'UNKNOWN') for r in fha)
for dt, _ in sorted(def_types.items(), key=lambda x: -x[1]):
    subset = [r for r in fha if r.get('defendant_type') == dt]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, dt)

# 6. Disability category
print('\n--- BY DISABILITY CATEGORY ---')
dis_cats = Counter(r.get('disability_category', 'UNKNOWN') for r in fha)
for dc, _ in sorted(dis_cats.items(), key=lambda x: -x[1]):
    subset = [r for r in fha if r.get('disability_category') == dc]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, dc)

# 7. Procedural posture
print('\n--- BY PROCEDURAL POSTURE ---')
pp_types = Counter(r.get('procedural_posture', 'UNKNOWN') for r in fha)
for pp, _ in sorted(pp_types.items(), key=lambda x: -x[1]):
    subset = [r for r in fha if r.get('procedural_posture') == pp]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, pp)

# 8. Plaintiff type
print('\n--- BY PLAINTIFF TYPE ---')
pt_types = Counter(r.get('plaintiff_type', 'UNKNOWN') for r in fha)
for pt, _ in sorted(pt_types.items(), key=lambda x: -x[1]):
    subset = [r for r in fha if r.get('plaintiff_type') == pt]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 5:
        win_stats(subset, pt)

# 9. Interactive process
print('\n--- INTERACTIVE PROCESS ---')
for val in ['YES', 'NO']:
    subset = [r for r in fha if r.get('interactive_process_discussed') == val]
    win_stats(subset, f'IP={val}')

# 10. Delay as denial
print('\n--- DELAY AS DENIAL ---')
for val in ['YES', 'NO']:
    subset = [r for r in fha if r.get('delay_as_denial') == val]
    win_stats(subset, f'DAD={val}')

# 11. Loper Bright cited
print('\n--- LOPER BRIGHT CITED ---')
for val in ['YES', 'NO']:
    subset = [r for r in fha if r.get('loper_bright_cited') == val]
    win_stats(subset, f'LB={val}')

# 12. Race mentioned
print('\n--- RACE MENTIONED ---')
for val in ['YES', 'NO']:
    subset = [r for r in fha if r.get('race_mentioned') == val]
    win_stats(subset, f'Race={val}')

# 13. Top states
print('\n--- TOP STATES ---')
state_counts = Counter(r.get('property_state', 'UNK') for r in fha)
for st, _ in state_counts.most_common(20):
    subset = [r for r in fha if r.get('property_state') == st]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, st)

# 14. Design & construction specific
print('\n--- DESIGN & CONSTRUCTION FOCUS ---')
d_and_c = [r for r in fha if r.get('accommodation_type') in ('DESIGN_CONSTRUCTION', 'STRUCTURAL_MODIFICATION')]
print(f'  Design/construction + structural mod cases: {len(d_and_c)}')
win_stats(d_and_c, 'D&C + Structural Mod')

# 15. FHA section cited
print('\n--- FHA SECTION CITED ---')
fha_sections = Counter(r.get('fha_section_cited', 'UNKNOWN') for r in fha)
for sec, count in fha_sections.most_common():
    print(f'  {sec:40s} {count:>5} ({100*count/len(fha):5.1f}%)')

# 16. Primary claim type
print('\n--- PRIMARY CLAIM TYPE ---')
claim_types = Counter(r.get('primary_claim_type', 'UNKNOWN') for r in fha)
for ct, count in claim_types.most_common():
    subset = [r for r in fha if r.get('primary_claim_type') == ct]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, ct)
    else:
        print(f'  {ct:45s} n={count} (too few decided)')

# 17. Housing type
print('\n--- HOUSING TYPE ---')
housing = Counter(r.get('housing_type', 'UNKNOWN') for r in fha)
for ht, _ in housing.most_common():
    subset = [r for r in fha if r.get('housing_type') == ht]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 10:
        win_stats(subset, ht)

# 18. Interactive process pre/post LB
print('\n--- INTERACTIVE PROCESS x PRE/POST LB ---')
for period, subset in [('Pre-LB', pre_lb), ('Post-LB', post_lb)]:
    ip_yes = [r for r in subset if r.get('interactive_process_discussed') == 'YES']
    ip_no = [r for r in subset if r.get('interactive_process_discussed') == 'NO']
    win_stats(ip_yes, f'{period} IP=YES')
    win_stats(ip_no, f'{period} IP=NO')

# 19. Delay as denial pre/post LB
print('\n--- DELAY AS DENIAL x PRE/POST LB ---')
for period, subset in [('Pre-LB', pre_lb), ('Post-LB', post_lb)]:
    dad_yes = [r for r in subset if r.get('delay_as_denial') == 'YES']
    dad_no = [r for r in subset if r.get('delay_as_denial') == 'NO']
    win_stats(dad_yes, f'{period} DAD=YES')
    win_stats(dad_no, f'{period} DAD=NO')

print('\n=== END OF ANALYSIS ===')
