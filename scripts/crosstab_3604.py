"""Cross-tabulations for the 3604 database."""
import json
from collections import Counter
import numpy as np
from scipy import stats as scipy_stats

DB_PATH = r'C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\FHA_3604_Database_unified_20260328_104352.json'

with open(DB_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

fha = [r for r in data if r.get('screening_result', '').upper() != 'NO']
DECIDED = ('PLAINTIFF_WIN', 'DEFENDANT_WIN', 'MIXED')

def win_line(subset, label):
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) < 5:
        print(f'  {label:55s} n={len(d):>4}  (too few)')
        return
    p = sum(1 for r in d if r.get('outcome') == 'PLAINTIFF_WIN')
    m = sum(1 for r in d if r.get('outcome') == 'MIXED')
    dw = sum(1 for r in d if r.get('outcome') == 'DEFENDANT_WIN')
    print(f'  {label:55s} n={len(d):>4}  PW={p:>3} ({100*p/len(d):5.1f}%)  MX={m:>3}  DW={dw:>3}  Broad={100*(p+m)/len(d):5.1f}%')

def chi2_test(subset1, subset2, label, measure='strict'):
    d1 = [r for r in subset1 if r.get('outcome') in DECIDED]
    d2 = [r for r in subset2 if r.get('outcome') in DECIDED]
    if len(d1) < 5 or len(d2) < 5:
        return
    if measure == 'strict':
        a = sum(1 for r in d1 if r.get('outcome') == 'PLAINTIFF_WIN')
        b = sum(1 for r in d2 if r.get('outcome') == 'PLAINTIFF_WIN')
    else:
        a = sum(1 for r in d1 if r.get('outcome') in ('PLAINTIFF_WIN', 'MIXED'))
        b = sum(1 for r in d2 if r.get('outcome') in ('PLAINTIFF_WIN', 'MIXED'))
    table = np.array([[a, len(d1)-a], [b, len(d2)-b]])
    if np.any(table < 0):
        return
    try:
        chi2, p, _, _ = scipy_stats.chi2_contingency(table)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f'    {label} ({measure}): chi2={chi2:.2f}, p={p:.4f} {sig}')
    except:
        pass

pre_lb = [r for r in fha if r.get('year') and int(r.get('year', 0)) <= 2023]
post_lb = [r for r in fha if r.get('year') and int(r.get('year', 0)) >= 2024]

# ============================================================
print('=' * 80)
print('1. ACCOMMODATION TYPE x PRE/POST LOPER BRIGHT')
print('=' * 80)
acc_types = ['ASSISTANCE_ANIMAL', 'PARKING', 'SOBER_LIVING_GROUP_HOME_ZONING',
             'COMMUNICATION_ACCOMMODATION', 'LIVE_IN_AIDE', 'STRUCTURAL_MODIFICATION',
             'POLICY_EXCEPTION', 'EVICTION_DEFENSE', 'TRANSFER',
             'DISCRIMINATION_PRIMARY', 'OTHER']
for acc in acc_types:
    pre = [r for r in pre_lb if r.get('accommodation_type') == acc]
    post = [r for r in post_lb if r.get('accommodation_type') == acc]
    d_pre = [r for r in pre if r.get('outcome') in DECIDED]
    d_post = [r for r in post if r.get('outcome') in DECIDED]
    if len(d_pre) >= 5 and len(d_post) >= 5:
        print(f'\n  {acc}:')
        win_line(pre, f'Pre-LB')
        win_line(post, f'Post-LB')
        chi2_test(pre, post, 'Pre vs Post', 'strict')
        chi2_test(pre, post, 'Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('2. INTERACTIVE PROCESS x PLAINTIFF TYPE')
print('=' * 80)
pt_types = ['INDIVIDUAL_TENANT', 'GROUP_HOME_OPERATOR', 'FAIR_HOUSING_ORG', 'GOVERNMENT']
for pt in pt_types:
    ip_yes = [r for r in fha if r.get('plaintiff_type') == pt and r.get('interactive_process_discussed') == 'YES']
    ip_no = [r for r in fha if r.get('plaintiff_type') == pt and r.get('interactive_process_discussed') == 'NO']
    total_pt = [r for r in fha if r.get('plaintiff_type') == pt]
    ip_rate = len([r for r in total_pt if r.get('interactive_process_discussed') == 'YES'])
    total_decided = len([r for r in total_pt if r.get('outcome') in DECIDED])
    if total_decided >= 10:
        print(f'\n  {pt} (IP rate: {100*ip_rate/len(total_pt):.1f}%):')
        win_line(ip_yes, f'IP=YES')
        win_line(ip_no, f'IP=NO')

# ============================================================
print('\n' + '=' * 80)
print('3. MTD SURVIVAL RATES BY ACCOMMODATION TYPE')
print('=' * 80)
mtd = [r for r in fha if r.get('procedural_posture') == 'MOTION_TO_DISMISS']
print(f'Total MTD cases: {len(mtd)}')
for acc in acc_types:
    subset = [r for r in mtd if r.get('accommodation_type') == acc]
    d = [r for r in subset if r.get('outcome') in DECIDED]
    if len(d) >= 5:
        win_line(subset, f'MTD: {acc}')

# MTD pre/post LB
print('\n  MTD Pre/Post LB:')
mtd_pre = [r for r in mtd if r.get('year') and int(r.get('year', 0)) <= 2023]
mtd_post = [r for r in mtd if r.get('year') and int(r.get('year', 0)) >= 2024]
win_line(mtd_pre, 'MTD Pre-LB')
win_line(mtd_post, 'MTD Post-LB')
chi2_test(mtd_pre, mtd_post, 'MTD Pre vs Post', 'strict')
chi2_test(mtd_pre, mtd_post, 'MTD Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('4. DELAY AS DENIAL x ACCOMMODATION TYPE')
print('=' * 80)
for acc in acc_types:
    dad_yes = [r for r in fha if r.get('accommodation_type') == acc and r.get('delay_as_denial') == 'YES']
    dad_no = [r for r in fha if r.get('accommodation_type') == acc and r.get('delay_as_denial') == 'NO']
    if len([r for r in dad_yes if r.get('outcome') in DECIDED]) >= 3:
        print(f'\n  {acc}:')
        win_line(dad_yes, f'DAD=YES')
        win_line(dad_no, f'DAD=NO')

# ============================================================
print('\n' + '=' * 80)
print('5. PLAINTIFF TYPE x PRE/POST LOPER BRIGHT')
print('=' * 80)
for pt in pt_types + ['OTHER']:
    pre = [r for r in pre_lb if r.get('plaintiff_type') == pt]
    post = [r for r in post_lb if r.get('plaintiff_type') == pt]
    d_pre = [r for r in pre if r.get('outcome') in DECIDED]
    d_post = [r for r in post if r.get('outcome') in DECIDED]
    if len(d_pre) >= 5 and len(d_post) >= 5:
        print(f'\n  {pt}:')
        win_line(pre, f'Pre-LB')
        win_line(post, f'Post-LB')
        chi2_test(pre, post, 'Pre vs Post', 'strict')
        chi2_test(pre, post, 'Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('6. DEFENDANT TYPE x PRE/POST LOPER BRIGHT')
print('=' * 80)
def_types = ['PRIVATE_LANDLORD', 'PROPERTY_MANAGEMENT', 'MUNICIPALITY',
             'HOUSING_AUTHORITY', 'HOA_CONDO_ASSN', 'OTHER', 'GOVERNMENT']
for dt in def_types:
    pre = [r for r in pre_lb if r.get('defendant_type') == dt]
    post = [r for r in post_lb if r.get('defendant_type') == dt]
    d_pre = [r for r in pre if r.get('outcome') in DECIDED]
    d_post = [r for r in post if r.get('outcome') in DECIDED]
    if len(d_pre) >= 5 and len(d_post) >= 5:
        print(f'\n  {dt}:')
        win_line(pre, f'Pre-LB')
        win_line(post, f'Post-LB')
        chi2_test(pre, post, 'Pre vs Post', 'strict')
        chi2_test(pre, post, 'Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('7. DISABILITY CATEGORY x PRE/POST LOPER BRIGHT')
print('=' * 80)
dis_cats = ['MOBILITY', 'MENTAL_HEALTH', 'SUBSTANCE_USE', 'INTELLECTUAL_DEVELOPMENTAL',
            'SENSORY', 'MULTIPLE_UNSPECIFIED']
for dc in dis_cats:
    pre = [r for r in pre_lb if r.get('disability_category') == dc]
    post = [r for r in post_lb if r.get('disability_category') == dc]
    d_pre = [r for r in pre if r.get('outcome') in DECIDED]
    d_post = [r for r in post if r.get('outcome') in DECIDED]
    if len(d_pre) >= 5 and len(d_post) >= 5:
        print(f'\n  {dc}:')
        win_line(pre, f'Pre-LB')
        win_line(post, f'Post-LB')
        chi2_test(pre, post, 'Pre vs Post', 'strict')
        chi2_test(pre, post, 'Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('8. HOUSING TYPE x PRE/POST LOPER BRIGHT')
print('=' * 80)
ht_types = ['PRIVATE_MARKET', 'HOA_CONDO', 'SECTION_8_VOUCHER', 'SUPPORTIVE_HOUSING',
            'PUBLIC_HOUSING', 'LIHTC']
for ht in ht_types:
    pre = [r for r in pre_lb if r.get('housing_type') == ht]
    post = [r for r in post_lb if r.get('housing_type') == ht]
    d_pre = [r for r in pre if r.get('outcome') in DECIDED]
    d_post = [r for r in post if r.get('outcome') in DECIDED]
    if len(d_pre) >= 5 and len(d_post) >= 5:
        print(f'\n  {ht}:')
        win_line(pre, f'Pre-LB')
        win_line(post, f'Post-LB')
        chi2_test(pre, post, 'Pre vs Post', 'strict')
        chi2_test(pre, post, 'Pre vs Post', 'broad')

# ============================================================
print('\n' + '=' * 80)
print('9. IQBAL DETECTION (key_cases_cited)')
print('=' * 80)
iqbal_cases = []
non_iqbal = []
for r in fha:
    kcc = r.get('key_cases_cited', [])
    if kcc is None:
        kcc = []
    if isinstance(kcc, str):
        kcc = [kcc]
    has_iqbal = any('iqbal' in str(c).lower() for c in kcc)
    if has_iqbal:
        iqbal_cases.append(r)
    else:
        non_iqbal.append(r)

print(f'  Iqbal cited: {len(iqbal_cases)} ({100*len(iqbal_cases)/len(fha):.1f}%)')
print(f'  Iqbal not cited: {len(non_iqbal)} ({100*len(non_iqbal)/len(fha):.1f}%)')
win_line(iqbal_cases, 'Iqbal cited')
win_line(non_iqbal, 'Iqbal not cited')
chi2_test(iqbal_cases, non_iqbal, 'Iqbal effect', 'strict')
chi2_test(iqbal_cases, non_iqbal, 'Iqbal effect', 'broad')

# Iqbal at MTD
iqbal_mtd = [r for r in iqbal_cases if r.get('procedural_posture') == 'MOTION_TO_DISMISS']
non_iqbal_mtd = [r for r in non_iqbal if r.get('procedural_posture') == 'MOTION_TO_DISMISS']
print(f'\n  Iqbal at MTD: {len(iqbal_mtd)}')
win_line(iqbal_mtd, 'Iqbal cited at MTD')
win_line(non_iqbal_mtd, 'Iqbal not cited at MTD')

# Iqbal pre/post LB
iqbal_pre = [r for r in iqbal_cases if r.get('year') and int(r.get('year', 0)) <= 2023]
iqbal_post = [r for r in iqbal_cases if r.get('year') and int(r.get('year', 0)) >= 2024]
print(f'\n  Iqbal pre/post LB:')
win_line(iqbal_pre, 'Iqbal Pre-LB')
win_line(iqbal_post, 'Iqbal Post-LB')

# ============================================================
print('\n' + '=' * 80)
print('10. DESIGN & CONSTRUCTION DEEP DIVE')
print('=' * 80)
# All § 3604(f)(3)(C) citations
dc_section = [r for r in fha if r.get('fha_section_cited') and '3604(f)(3)(C)' in str(r.get('fha_section_cited', ''))]
dc_accom = [r for r in fha if r.get('accommodation_type') == 'DESIGN_CONSTRUCTION']
dc_claim = [r for r in fha if r.get('primary_claim_type') == 'design_and_construction']
dc_struct = [r for r in fha if r.get('accommodation_type') == 'STRUCTURAL_MODIFICATION']

print(f'  § 3604(f)(3)(C) cited: {len(dc_section)}')
print(f'  accommodation_type=DESIGN_CONSTRUCTION: {len(dc_accom)}')
print(f'  primary_claim_type=design_and_construction: {len(dc_claim)}')
print(f'  accommodation_type=STRUCTURAL_MODIFICATION: {len(dc_struct)}')

# Union of D&C related
dc_all = set()
for r in dc_section + dc_accom + dc_claim + dc_struct:
    dc_all.add(r.get('source_file'))
dc_combined = [r for r in fha if r.get('source_file') in dc_all]
print(f'  Combined D&C universe: {len(dc_combined)}')
win_line(dc_combined, 'All D&C related')

# D&C by plaintiff type
for pt in pt_types:
    subset = [r for r in dc_combined if r.get('plaintiff_type') == pt]
    if len([r for r in subset if r.get('outcome') in DECIDED]) >= 3:
        win_line(subset, f'D&C: {pt}')

# D&C by defendant type
for dt in def_types:
    subset = [r for r in dc_combined if r.get('defendant_type') == dt]
    if len([r for r in subset if r.get('outcome') in DECIDED]) >= 3:
        win_line(subset, f'D&C: {dt}')

print('\n=== CROSS-TABULATION COMPLETE ===')
