"""
H1 + H2 Analysis: Specific-duty outperformance and representation × complexity.

H1: Do specific-duty claims outperform open-textured claims?
H2: Is the representation gap largest in technically demanding claim categories?

Requires supplemental_classification_results.json from supplemental_batch.py.

Outputs: h1_h2_results.json
"""
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/2/FHA_Unified_Database.json'
SUPP_PATH = 'supplemental_classification_results.json'
OUTPUT_PATH = 'h1_h2_results.json'

# ============================================================
# 1. LOAD AND MERGE DATA
# ============================================================

with open(DB_PATH, 'r', encoding='utf-8') as f:
    db_raw = json.load(f)

with open(SUPP_PATH, 'r', encoding='utf-8') as f:
    supp_raw = json.load(f)

# Build lookup from source_file -> supplemental classification
supp_lookup = {}
for r in supp_raw:
    sf = r.get('source_file', '')
    cl = r.get('classification', {})
    supp_lookup[sf] = cl

print(f"Unified DB: {len(db_raw)} records")
print(f"Supplemental classifications: {len(supp_lookup)}")

# Merge
merged = []
matched = 0
for r in db_raw:
    sf = r.get('source_file', '')
    if sf in supp_lookup:
        r['supp'] = supp_lookup[sf]
        matched += 1
    else:
        r['supp'] = {}
    merged.append(r)

print(f"Matched: {matched}")

# Filter to disability screened-in
disability = [r for r in merged if r.get('screening_result') == 'YES'
              and (r.get('disability_alleged') or r.get('is_ra_case')
                   or 'disability' in (r.get('protected_classes') or []))]
print(f"Disability screened-in: {len(disability)}")

# Build DataFrame
records = []
for r in disability:
    supp = r.get('supp', {})
    records.append({
        'source_file': r.get('source_file', ''),
        'year': r.get('year'),
        'court': r.get('court', ''),
        'circuit': r.get('circuit', ''),
        'outcome': r.get('outcome', ''),
        'pro_se': r.get('pro_se', False),
        'plaintiff_type': r.get('plaintiff_type', ''),
        'defendant_type': r.get('defendant_type', ''),
        'procedural_posture': r.get('procedural_posture', ''),
        'claim_types': str(r.get('claim_types', [])),
        'accommodation_type': r.get('accommodation_type', ''),
        'is_ra_case': r.get('is_ra_case', False),
        # Supplemental fields
        'claim_specificity': supp.get('claim_specificity', 'MISSING'),
        'enacted_duty_flag': supp.get('enacted_duty_flag'),
        'measurable_facts_flag': supp.get('measurable_facts_flag'),
        'technical_complexity': supp.get('technical_complexity', 'MISSING'),
        'expert_proof_needed': supp.get('expert_proof_needed'),
        'multi_defendant': supp.get('multi_defendant'),
        'physical_evidence_present': supp.get('physical_evidence_present'),
        'public_quasi_public_defendant': supp.get('public_quasi_public_defendant'),
    })

df = pd.DataFrame(records)

# Assign periods
df['period'] = df['year'].apply(lambda y: 'P1' if y and y <= 2023
                                else ('P2' if y == 2024
                                      else ('P3' if y and y >= 2025 else None)))
dated = df[df['period'].notna()].copy()

# Binary outcome variables
excluded = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
decided = dated[~dated['outcome'].isin(excluded)].copy()
decided['strict_win'] = (decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
decided['broad_win'] = decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

# Binary predictors
decided['pro_se_int'] = decided['pro_se'].apply(lambda x: 1 if x is True else 0)
decided['post_2024'] = (decided['year'] >= 2024).astype(int)

def_map = {
    'PRIVATE_LANDLORD': 'PRIVATE', 'PROPERTY_MANAGEMENT': 'PRIVATE',
    'HOA_CONDO_ASSN': 'PRIVATE', 'HOA_CONDO_BOARD': 'PRIVATE',
    'HOA_CONDO': 'PRIVATE', 'REAL_ESTATE_AGENT': 'PRIVATE',
    'DEVELOPER_BUILDER': 'PRIVATE',
    'HOUSING_AUTHORITY': 'PUBLIC_QUASI', 'MUNICIPALITY': 'PUBLIC_QUASI',
}
decided['def_cat'] = decided['defendant_type'].map(def_map).fillna('OTHER')

print(f"\nDated: {len(dated)}, Decided: {len(decided)}")
print(f"Claim specificity distribution:")
print(decided['claim_specificity'].value_counts().to_string())
print(f"\nTechnical complexity distribution:")
print(decided['technical_complexity'].value_counts().to_string())

results_store = {}

# ============================================================
# 2. H1 ANALYSIS: SPECIFIC-DUTY OUTPERFORMANCE
# ============================================================

print("\n" + "="*70)
print("H1: SPECIFIC-DUTY vs OPEN-TEXTURED CLAIM OUTCOMES")
print("="*70)

# Filter to cases with valid specificity classification
h1_data = decided[decided['claim_specificity'].isin(['SPECIFIC_DUTY', 'MIXED', 'OPEN_TEXTURED'])].copy()
print(f"\nH1 analysis N: {len(h1_data)}")

# Win rates by specificity
print("\nWin rates by claim specificity:")
h1_rates = {}
for spec in ['SPECIFIC_DUTY', 'MIXED', 'OPEN_TEXTURED']:
    subset = h1_data[h1_data['claim_specificity'] == spec]
    if len(subset) > 0:
        h1_rates[spec] = {
            'n': int(len(subset)),
            'strict_win_rate': round(subset['strict_win'].mean(), 4),
            'broad_win_rate': round(subset['broad_win'].mean(), 4),
            'pro_se_share': round((subset['pro_se'] == True).mean(), 4),
        }
        print(f"  {spec}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}, pro_se={( subset['pro_se']==True).mean():.1%}")

results_store['h1_win_rates'] = h1_rates

# Win rates by specificity × period
print("\nWin rates by specificity × period:")
h1_period = {}
for spec in ['SPECIFIC_DUTY', 'MIXED', 'OPEN_TEXTURED']:
    spec_data = h1_data[h1_data['claim_specificity'] == spec]
    h1_period[spec] = {}
    for p in ['P1', 'P2', 'P3']:
        p_data = spec_data[spec_data['period'] == p]
        if len(p_data) >= 5:
            h1_period[spec][p] = {
                'n': int(len(p_data)),
                'strict': round(p_data['strict_win'].mean(), 4),
                'broad': round(p_data['broad_win'].mean(), 4),
            }
            print(f"  {spec}/{p}: n={len(p_data)}, strict={p_data['strict_win'].mean():.1%}, "
                  f"broad={p_data['broad_win'].mean():.1%}")

results_store['h1_period'] = h1_period

# Chi-squared: specificity vs outcome
contingency_h1 = pd.crosstab(h1_data['claim_specificity'], h1_data['broad_win'])
chi2_h1, p_h1, dof_h1, _ = stats.chi2_contingency(contingency_h1)
print(f"\nChi-squared (broad_win ~ specificity): χ²={chi2_h1:.3f}, p={p_h1:.4f}")
results_store['h1_chi2'] = {'chi2': round(chi2_h1, 3), 'p': round(p_h1, 4)}

# Logistic regression: H1
print("\n--- H1 Model: Broad Win ~ Specificity + Controls ---")

# Encode specificity (SPECIFIC_DUTY as reference)
h1_data = h1_data.copy()
h1_data['is_open'] = (h1_data['claim_specificity'] == 'OPEN_TEXTURED').astype(int)
h1_data['is_mixed'] = (h1_data['claim_specificity'] == 'MIXED').astype(int)

try:
    formula_h1 = 'broad_win ~ is_open + is_mixed + pro_se_int + post_2024 + C(def_cat)'
    model_h1 = logit(formula_h1, data=h1_data).fit(disp=0)
    print(model_h1.summary2().tables[1].to_string())
    results_store['h1_model'] = {
        'formula': formula_h1,
        'n': int(model_h1.nobs),
        'pseudo_r2': round(model_h1.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model_h1.params[name], 4),
            'se': round(model_h1.bse[name], 4),
            'p': round(model_h1.pvalues[name], 4),
            'or': round(np.exp(model_h1.params[name]), 4)
        } for name in model_h1.params.index}
    }
except Exception as e:
    print(f"  H1 model failed: {e}")
    results_store['h1_model'] = {'error': str(e)}

# H1 with enacted_duty_flag
print("\n--- H1 Model (enacted duty): Broad Win ~ enacted_duty + Controls ---")
h1_enacted = h1_data[h1_data['enacted_duty_flag'].notna()].copy()
h1_enacted['enacted_int'] = h1_enacted['enacted_duty_flag'].astype(int)
if len(h1_enacted) > 50:
    try:
        formula_h1b = 'broad_win ~ enacted_int + pro_se_int + post_2024 + C(def_cat)'
        model_h1b = logit(formula_h1b, data=h1_enacted).fit(disp=0)
        print(model_h1b.summary2().tables[1].to_string())
        results_store['h1_enacted_model'] = {
            'formula': formula_h1b,
            'n': int(model_h1b.nobs),
            'pseudo_r2': round(model_h1b.prsquared, 4),
            'coefficients': {name: {
                'coef': round(model_h1b.params[name], 4),
                'se': round(model_h1b.bse[name], 4),
                'p': round(model_h1b.pvalues[name], 4),
                'or': round(np.exp(model_h1b.params[name]), 4)
            } for name in model_h1b.params.index}
        }
    except Exception as e:
        print(f"  H1 enacted model failed: {e}")
        results_store['h1_enacted_model'] = {'error': str(e)}

# ============================================================
# 3. H2 ANALYSIS: REPRESENTATION × TECHNICAL COMPLEXITY
# ============================================================

print("\n" + "="*70)
print("H2: REPRESENTATION GAP × TECHNICAL COMPLEXITY")
print("="*70)

h2_data = decided[decided['technical_complexity'].isin(['LOW', 'MODERATE', 'HIGH'])].copy()
print(f"\nH2 analysis N: {len(h2_data)}")

# Win rates by complexity
print("\nWin rates by technical complexity:")
h2_rates = {}
for comp in ['LOW', 'MODERATE', 'HIGH']:
    subset = h2_data[h2_data['technical_complexity'] == comp]
    if len(subset) > 0:
        h2_rates[comp] = {
            'n': int(len(subset)),
            'strict_win_rate': round(subset['strict_win'].mean(), 4),
            'broad_win_rate': round(subset['broad_win'].mean(), 4),
            'pro_se_share': round((subset['pro_se'] == True).mean(), 4),
        }
        print(f"  {comp}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}, pro_se={(subset['pro_se']==True).mean():.1%}")

results_store['h2_win_rates'] = h2_rates

# THE KEY TEST: Representation gap by complexity level
print("\nRepresentation gap by complexity:")
h2_gap = {}
for comp in ['LOW', 'MODERATE', 'HIGH']:
    comp_data = h2_data[h2_data['technical_complexity'] == comp]
    prose = comp_data[comp_data['pro_se'] == True]
    rep = comp_data[comp_data['pro_se'] == False]
    if len(prose) >= 5 and len(rep) >= 5:
        gap = rep['broad_win'].mean() - prose['broad_win'].mean()
        h2_gap[comp] = {
            'represented_n': int(len(rep)),
            'represented_broad_win': round(rep['broad_win'].mean(), 4),
            'prose_n': int(len(prose)),
            'prose_broad_win': round(prose['broad_win'].mean(), 4),
            'gap': round(gap, 4),
        }
        print(f"  {comp}: represented={rep['broad_win'].mean():.1%} (n={len(rep)}), "
              f"pro_se={prose['broad_win'].mean():.1%} (n={len(prose)}), "
              f"gap={gap:.1%}")

results_store['h2_representation_gap'] = h2_gap

# Representation gap by complexity × period
print("\nRepresentation gap by complexity × period:")
for comp in ['LOW', 'MODERATE', 'HIGH']:
    comp_data = h2_data[h2_data['technical_complexity'] == comp]
    for p in ['P1', 'P2', 'P3']:
        p_data = comp_data[comp_data['period'] == p]
        prose = p_data[p_data['pro_se'] == True]
        rep = p_data[p_data['pro_se'] == False]
        if len(prose) >= 3 and len(rep) >= 3:
            gap = rep['broad_win'].mean() - prose['broad_win'].mean()
            print(f"  {comp}/{p}: rep={rep['broad_win'].mean():.1%}(n={len(rep)}), "
                  f"prose={prose['broad_win'].mean():.1%}(n={len(prose)}), gap={gap:.1%}")

# Logistic regression: H2 interaction model
print("\n--- H2 Model: Broad Win ~ pro_se × complexity + Controls ---")

h2_data = h2_data.copy()
h2_data['is_moderate'] = (h2_data['technical_complexity'] == 'MODERATE').astype(int)
h2_data['is_high'] = (h2_data['technical_complexity'] == 'HIGH').astype(int)
h2_data['prose_x_moderate'] = h2_data['pro_se_int'] * h2_data['is_moderate']
h2_data['prose_x_high'] = h2_data['pro_se_int'] * h2_data['is_high']

try:
    formula_h2 = ('broad_win ~ pro_se_int + is_moderate + is_high '
                  '+ prose_x_moderate + prose_x_high + post_2024 + C(def_cat)')
    model_h2 = logit(formula_h2, data=h2_data).fit(disp=0)
    print(model_h2.summary2().tables[1].to_string())
    results_store['h2_model'] = {
        'formula': formula_h2,
        'n': int(model_h2.nobs),
        'pseudo_r2': round(model_h2.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model_h2.params[name], 4),
            'se': round(model_h2.bse[name], 4),
            'p': round(model_h2.pvalues[name], 4),
            'or': round(np.exp(model_h2.params[name]), 4)
        } for name in model_h2.params.index}
    }
except Exception as e:
    print(f"  H2 model failed: {e}")
    results_store['h2_model'] = {'error': str(e)}

# H2: Simpler main-effects model for comparison
print("\n--- H2 Simple Model: Broad Win ~ pro_se + complexity + Controls ---")
try:
    formula_h2s = 'broad_win ~ pro_se_int + is_moderate + is_high + post_2024 + C(def_cat)'
    model_h2s = logit(formula_h2s, data=h2_data).fit(disp=0)
    print(model_h2s.summary2().tables[1].to_string())
    results_store['h2_simple_model'] = {
        'formula': formula_h2s,
        'n': int(model_h2s.nobs),
        'pseudo_r2': round(model_h2s.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model_h2s.params[name], 4),
            'se': round(model_h2s.bse[name], 4),
            'p': round(model_h2s.pvalues[name], 4),
            'or': round(np.exp(model_h2s.params[name]), 4)
        } for name in model_h2s.params.index}
    }
except Exception as e:
    print(f"  H2 simple model failed: {e}")

# ============================================================
# 4. COMBINED MODEL: SPECIFICITY + COMPLEXITY + REPRESENTATION
# ============================================================

print("\n" + "="*70)
print("COMBINED MODEL: All H1+H2 Variables")
print("="*70)

combined = decided[
    (decided['claim_specificity'].isin(['SPECIFIC_DUTY', 'MIXED', 'OPEN_TEXTURED']))
    & (decided['technical_complexity'].isin(['LOW', 'MODERATE', 'HIGH']))
].copy()

combined['is_open'] = (combined['claim_specificity'] == 'OPEN_TEXTURED').astype(int)
combined['is_mixed'] = (combined['claim_specificity'] == 'MIXED').astype(int)
combined['is_moderate'] = (combined['technical_complexity'] == 'MODERATE').astype(int)
combined['is_high'] = (combined['technical_complexity'] == 'HIGH').astype(int)

print(f"Combined model N: {len(combined)}")

try:
    formula_comb = ('broad_win ~ is_open + is_mixed + is_moderate + is_high '
                    '+ pro_se_int + post_2024 + C(def_cat)')
    model_comb = logit(formula_comb, data=combined).fit(disp=0)
    print(model_comb.summary2().tables[1].to_string())
    results_store['combined_model'] = {
        'formula': formula_comb,
        'n': int(model_comb.nobs),
        'pseudo_r2': round(model_comb.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model_comb.params[name], 4),
            'se': round(model_comb.bse[name], 4),
            'p': round(model_comb.pvalues[name], 4),
            'or': round(np.exp(model_comb.params[name]), 4)
        } for name in model_comb.params.index}
    }
except Exception as e:
    print(f"  Combined model failed: {e}")
    results_store['combined_model'] = {'error': str(e)}

# ============================================================
# 5. VALIDATION SAMPLE
# ============================================================

print("\n" + "="*70)
print("VALIDATION SAMPLE")
print("="*70)

import random
random.seed(42)

validation = {}
for spec in ['SPECIFIC_DUTY', 'MIXED', 'OPEN_TEXTURED']:
    candidates = [r for r in disability if r.get('supp', {}).get('claim_specificity') == spec]
    sample = random.sample(candidates, min(10, len(candidates)))
    validation[spec] = [{
        'case_name': s.get('case_name', ''),
        'year': s.get('year'),
        'claim_specificity': spec,
        'specificity_reasoning': s.get('supp', {}).get('specificity_reasoning', ''),
        'key_holding': s.get('key_holding', '')[:200],
    } for s in sample]
    print(f"\n{spec} sample ({len(sample)} cases):")
    for v in validation[spec][:3]:
        print(f"  {v['case_name']} ({v['year']}): {v['specificity_reasoning']}")

for comp in ['LOW', 'MODERATE', 'HIGH']:
    candidates = [r for r in disability if r.get('supp', {}).get('technical_complexity') == comp]
    sample = random.sample(candidates, min(10, len(candidates)))
    validation[f'complexity_{comp}'] = [{
        'case_name': s.get('case_name', ''),
        'year': s.get('year'),
        'technical_complexity': comp,
        'complexity_reasoning': s.get('supp', {}).get('complexity_reasoning', ''),
        'accommodation_type': s.get('accommodation_type', ''),
    } for s in sample]
    print(f"\n{comp} complexity sample ({len(sample)} cases):")
    for v in validation[f'complexity_{comp}'][:3]:
        print(f"  {v['case_name']} ({v['year']}): {v['complexity_reasoning']}")

results_store['validation_samples'] = validation

# ============================================================
# 6. SAVE RESULTS
# ============================================================

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results_store, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"H1+H2 RESULTS SAVED TO {OUTPUT_PATH}")
print(f"{'='*70}")
