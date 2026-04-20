"""
H6 Analysis: Objective physical evidence improves outcomes in
physical-accessibility cases.

Tests whether the presence of photographs, measurements, inspection
reports, or other physical evidence improves survival and success
rates in design-and-construction, structural modification, and
other physical-accessibility disputes.

Outputs: h6_results.json
"""
import sys
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
from collections import Counter
import os
import warnings
warnings.filterwarnings('ignore')

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import UNIFIED_DB_PATH, RESULTS_DIR

DB_PATH = UNIFIED_DB_PATH
SUPP_PATH = os.path.join(RESULTS_DIR, 'supplemental_classification_results.json')
OUTPUT_PATH = os.path.join(RESULTS_DIR, 'h6_results.json')

# ============================================================
# 1. LOAD AND MERGE
# ============================================================

with open(DB_PATH, 'r', encoding='utf-8') as f:
    db = json.load(f)
with open(SUPP_PATH, 'r', encoding='utf-8') as f:
    supp_raw = json.load(f)

supp_map = {r['source_file']: r['classification'] for r in supp_raw}

disability = [r for r in db if r.get('screening_result') == 'YES'
              and (r.get('disability_alleged') or r.get('is_ra_case')
                   or 'disability' in (r.get('protected_classes') or []))]

for r in disability:
    r['supp'] = supp_map.get(r.get('source_file', ''), {})

print(f"Disability screened-in: {len(disability)}")

# ============================================================
# 2. IDENTIFY PHYSICAL-ACCESSIBILITY CASES
# ============================================================

PHYSICAL_ACC_TYPES = {'STRUCTURAL_MODIFICATION', 'PARKING'}
PHYSICAL_THEORIES = {'DESIGN_AND_CONSTRUCTION'}

records = []
for r in disability:
    supp = r.get('supp', {})
    fha_claims = [c for c in r.get('fha_claims', []) if c.get('theory') != 'NOT_FHA']

    acc_type = r.get('accommodation_type', '')
    sec_acc = r.get('secondary_accommodation_type', '')
    has_physical_theory = any(c.get('theory') in PHYSICAL_THEORIES for c in fha_claims)
    has_physical_acc = acc_type in PHYSICAL_ACC_TYPES or sec_acc in PHYSICAL_ACC_TYPES

    is_physical_case = has_physical_theory or has_physical_acc
    physical_evidence = supp.get('physical_evidence_present', False)
    expert_needed = supp.get('expert_proof_needed', False)

    survived_mtd = any(c.get('dismissal_reason') in ('SURVIVES_MTD', 'SURVIVES_PROCEDURAL',
                        'SUMMARY_JUDGMENT_GRANTED', 'SUMMARY_JUDGMENT_DENIED',
                        'PLAINTIFF_PREVAILS_MERITS', 'DEFENDANT_PREVAILS_MERITS')
                       for c in fha_claims)
    reached_merits = any(c.get('merits_reached') in ('YES', 'PARTIAL') for c in fha_claims)

    records.append({
        'source_file': r.get('source_file', ''),
        'year': r.get('year'),
        'outcome': r.get('outcome', ''),
        'pro_se': r.get('pro_se', False),
        'defendant_type': r.get('defendant_type', ''),
        'accommodation_type': acc_type,
        'is_physical_case': is_physical_case,
        'has_physical_theory': has_physical_theory,
        'has_physical_acc': has_physical_acc,
        'physical_evidence': physical_evidence,
        'expert_needed': expert_needed,
        'survived_mtd': survived_mtd,
        'reached_merits': reached_merits,
        'n_fha_claims': len(fha_claims),
    })

df = pd.DataFrame(records)
df['period'] = df['year'].apply(lambda y: 'P1' if y and y <= 2023
                                else ('P2' if y == 2024
                                      else ('P3' if y and y >= 2025 else None)))
dated = df[df['period'].notna()].copy()

# Physical-accessibility subset
physical = dated[dated['is_physical_case']].copy()
print(f"\nPhysical-accessibility cases (dated): {len(physical)}")
print(f"  With physical evidence: {physical['physical_evidence'].sum()}")
print(f"  Without physical evidence: {(~physical['physical_evidence']).sum()}")
print(f"  Expert proof needed: {physical['expert_needed'].sum()}")

# Also analyze physical_evidence across ALL cases for comparison
all_cases = dated.copy()
print(f"\nAll dated disability cases: {len(all_cases)}")
print(f"  With physical evidence: {all_cases['physical_evidence'].sum()}")

results_store = {}

# ============================================================
# 3. OUTCOMES: PHYSICAL EVIDENCE vs NO PHYSICAL EVIDENCE
# ============================================================

print("\n" + "=" * 70)
print("H6: PHYSICAL EVIDENCE AND OUTCOMES")
print("=" * 70)

# --- Within physical-accessibility cases ---
excluded = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
phys_decided = physical[~physical['outcome'].isin(excluded)].copy()
phys_decided['strict_win'] = (phys_decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
phys_decided['broad_win'] = phys_decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

print(f"\nPhysical-accessibility decided cases: {len(phys_decided)}")

h6_rates = {}
for ev_label, ev_val in [('With evidence', True), ('Without evidence', False)]:
    subset = phys_decided[phys_decided['physical_evidence'] == ev_val]
    if len(subset) > 0:
        h6_rates[ev_label] = {
            'n': int(len(subset)),
            'strict_win': round(subset['strict_win'].mean(), 4),
            'broad_win': round(subset['broad_win'].mean(), 4),
            'mtd_survival': round(subset['survived_mtd'].mean(), 4),
            'merits_reached': round(subset['reached_merits'].mean(), 4),
            'pro_se_share': round((subset['pro_se'] == True).mean(), 4),
        }
        print(f"  {ev_label}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}, MTD surv={subset['survived_mtd'].mean():.1%}, "
              f"merits={subset['reached_merits'].mean():.1%}, pro_se={(subset['pro_se']==True).mean():.1%}")

results_store['physical_case_rates'] = h6_rates

# Fisher's exact (small N might make chi2 unreliable)
if len(phys_decided) > 10:
    contingency = pd.crosstab(phys_decided['physical_evidence'], phys_decided['broad_win'])
    if contingency.shape == (2, 2):
        odds_ratio, fisher_p = stats.fisher_exact(contingency)
        print(f"\nFisher's exact (broad_win ~ physical_evidence, physical cases): OR={odds_ratio:.3f}, p={fisher_p:.4f}")
        results_store['fisher_physical_cases'] = {'or': round(odds_ratio, 3), 'p': round(fisher_p, 4)}

# --- Across ALL disability cases ---
print("\n--- Physical evidence effect across ALL disability cases ---")
all_decided = dated[~dated['outcome'].isin(excluded)].copy()
all_decided['strict_win'] = (all_decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
all_decided['broad_win'] = all_decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

h6_all_rates = {}
for ev_label, ev_val in [('With evidence', True), ('Without evidence', False)]:
    subset = all_decided[all_decided['physical_evidence'] == ev_val]
    if len(subset) > 0:
        h6_all_rates[ev_label] = {
            'n': int(len(subset)),
            'strict_win': round(subset['strict_win'].mean(), 4),
            'broad_win': round(subset['broad_win'].mean(), 4),
            'mtd_survival': round(subset['survived_mtd'].mean(), 4),
            'merits_reached': round(subset['reached_merits'].mean(), 4),
        }
        print(f"  {ev_label}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}, MTD surv={subset['survived_mtd'].mean():.1%}")

results_store['all_case_rates'] = h6_all_rates

contingency_all = pd.crosstab(all_decided['physical_evidence'], all_decided['broad_win'])
chi2_all, p_all, _, _ = stats.chi2_contingency(contingency_all)
print(f"\nChi-squared (broad_win ~ physical_evidence, all cases): chi2={chi2_all:.3f}, p={p_all:.4f}")
results_store['chi2_all_cases'] = {'chi2': round(chi2_all, 3), 'p': round(p_all, 4)}

# ============================================================
# 4. MTD SURVIVAL AND MERITS BY EVIDENCE
# ============================================================

print("\n" + "=" * 70)
print("MTD SURVIVAL BY PHYSICAL EVIDENCE")
print("=" * 70)

# Physical cases
print("\nPhysical-accessibility cases:")
for ev_label, ev_val in [('With evidence', True), ('Without evidence', False)]:
    subset = physical[physical['physical_evidence'] == ev_val]
    if len(subset) > 0:
        print(f"  {ev_label}: MTD survival={subset['survived_mtd'].mean():.1%} (n={len(subset)}), "
              f"merits reached={subset['reached_merits'].mean():.1%}")

# All cases
print("\nAll disability cases:")
for ev_label, ev_val in [('With evidence', True), ('Without evidence', False)]:
    subset = dated[dated['physical_evidence'] == ev_val]
    if len(subset) > 0:
        print(f"  {ev_label}: MTD survival={subset['survived_mtd'].mean():.1%} (n={len(subset)}), "
              f"merits reached={subset['reached_merits'].mean():.1%}")

# ============================================================
# 5. REGRESSION: PHYSICAL EVIDENCE EFFECT
# ============================================================

print("\n" + "=" * 70)
print("REGRESSION: PHYSICAL EVIDENCE")
print("=" * 70)

reg = all_decided.copy()
reg['phys_ev_int'] = reg['physical_evidence'].astype(int)
reg['pro_se_int'] = reg['pro_se'].apply(lambda x: 1 if x is True else 0)
reg['post_2024'] = (reg['year'] >= 2024).astype(int)
reg['is_physical_int'] = reg['is_physical_case'].astype(int)

def_map = {
    'PRIVATE_LANDLORD': 'PRIVATE', 'PROPERTY_MANAGEMENT': 'PRIVATE',
    'HOA_CONDO_ASSN': 'PRIVATE', 'HOA_CONDO_BOARD': 'PRIVATE',
    'HOA_CONDO': 'PRIVATE', 'REAL_ESTATE_AGENT': 'PRIVATE',
    'DEVELOPER_BUILDER': 'PRIVATE',
    'HOUSING_AUTHORITY': 'PUBLIC_QUASI', 'MUNICIPALITY': 'PUBLIC_QUASI',
}
reg['def_cat'] = reg['defendant_type'].map(def_map).fillna('OTHER')

# Model 1: Physical evidence on all cases
print("\n--- All cases: Broad Win ~ physical_evidence + controls ---")
try:
    formula1 = 'broad_win ~ phys_ev_int + pro_se_int + post_2024 + C(def_cat)'
    model1 = logit(formula1, data=reg).fit(disp=0)
    print(model1.summary2().tables[1].to_string())
    results_store['model_all_cases'] = {
        'formula': formula1,
        'n': int(model1.nobs),
        'pseudo_r2': round(model1.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model1.params[name], 4),
            'se': round(model1.bse[name], 4),
            'p': round(model1.pvalues[name], 4),
            'or': round(np.exp(model1.params[name]), 4)
        } for name in model1.params.index}
    }
except Exception as e:
    print(f"  Model failed: {e}")
    results_store['model_all_cases'] = {'error': str(e)}

# Model 2: Physical evidence with interaction for physical-case type
print("\n--- All cases: Broad Win ~ physical_evidence * is_physical_case + controls ---")
reg['phys_x_physcase'] = reg['phys_ev_int'] * reg['is_physical_int']
try:
    formula2 = 'broad_win ~ phys_ev_int + is_physical_int + phys_x_physcase + pro_se_int + post_2024 + C(def_cat)'
    model2 = logit(formula2, data=reg).fit(disp=0)
    print(model2.summary2().tables[1].to_string())
    results_store['model_interaction'] = {
        'formula': formula2,
        'n': int(model2.nobs),
        'pseudo_r2': round(model2.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model2.params[name], 4),
            'se': round(model2.bse[name], 4),
            'p': round(model2.pvalues[name], 4),
            'or': round(np.exp(model2.params[name]), 4)
        } for name in model2.params.index}
    }
except Exception as e:
    print(f"  Model failed: {e}")
    results_store['model_interaction'] = {'error': str(e)}

# Model 3: Physical-accessibility cases only (if N sufficient)
phys_reg = phys_decided.copy()
if len(phys_reg) >= 30:
    phys_reg['phys_ev_int'] = phys_reg['physical_evidence'].astype(int)
    phys_reg['pro_se_int'] = phys_reg['pro_se'].apply(lambda x: 1 if x is True else 0)
    phys_reg['post_2024'] = (phys_reg['year'] >= 2024).astype(int)

    print("\n--- Physical cases only: Broad Win ~ physical_evidence + pro_se + period ---")
    try:
        formula3 = 'broad_win ~ phys_ev_int + pro_se_int + post_2024'
        model3 = logit(formula3, data=phys_reg).fit(disp=0)
        print(model3.summary2().tables[1].to_string())
        results_store['model_physical_only'] = {
            'formula': formula3,
            'n': int(model3.nobs),
            'pseudo_r2': round(model3.prsquared, 4),
            'coefficients': {name: {
                'coef': round(model3.params[name], 4),
                'se': round(model3.bse[name], 4),
                'p': round(model3.pvalues[name], 4),
                'or': round(np.exp(model3.params[name]), 4)
            } for name in model3.params.index}
        }
    except Exception as e:
        print(f"  Model failed: {e}")
        results_store['model_physical_only'] = {'error': str(e)}

# ============================================================
# 6. DESIGN-AND-CONSTRUCTION SUBSET
# ============================================================

print("\n" + "=" * 70)
print("DESIGN-AND-CONSTRUCTION CASES")
print("=" * 70)

dc = dated[dated.apply(lambda row: any(c.get('theory') == 'DESIGN_AND_CONSTRUCTION'
                                        for c in disability[0].get('fha_claims', [])) if False else False,
                       axis=1)].copy()

# Re-derive from raw data
dc_records = []
for r in disability:
    if r.get('year') is None:
        continue
    fha = [c for c in r.get('fha_claims', []) if c.get('theory') == 'DESIGN_AND_CONSTRUCTION']
    if fha:
        dc_records.append({
            'source_file': r.get('source_file'),
            'year': r['year'],
            'outcome': r.get('outcome'),
            'pro_se': r.get('pro_se'),
            'physical_evidence': r.get('supp', {}).get('physical_evidence_present', False),
            'expert_needed': r.get('supp', {}).get('expert_proof_needed', False),
        })

if dc_records:
    dc_df = pd.DataFrame(dc_records)
    dc_decided = dc_df[~dc_df['outcome'].isin(excluded)].copy()
    dc_decided['broad_win'] = dc_decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)
    print(f"\nDesign-and-construction cases: {len(dc_df)}")
    print(f"Decided: {len(dc_decided)}")
    if len(dc_decided) > 0:
        for ev in [True, False]:
            sub = dc_decided[dc_decided['physical_evidence'] == ev]
            if len(sub) > 0:
                print(f"  Physical evidence={ev}: n={len(sub)}, broad_win={sub['broad_win'].mean():.1%}")
        results_store['design_construction'] = {
            'n_total': int(len(dc_df)),
            'n_decided': int(len(dc_decided)),
        }
else:
    print("  No design-and-construction cases identified from claim theory.")

# ============================================================
# 7. SAVE
# ============================================================

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results_store, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"H6 RESULTS SAVED TO {OUTPUT_PATH}")
print(f"{'='*70}")
