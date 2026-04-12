"""
H5 Analysis: Institutional/intermediary-supported cases disproportionately
generate favorable doctrine.

Tests whether institutional plaintiffs (fair housing orgs, government,
group home operators) produce better outcomes, reach merits more often,
and generate more complex legal analysis than individual plaintiffs.

Outputs: h5_results.json
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
OUTPUT_PATH = 'h5_results.json'

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
# 2. BUILD DATAFRAME
# ============================================================

records = []
for r in disability:
    supp = r.get('supp', {})
    fha_claims = [c for c in r.get('fha_claims', []) if c.get('theory') != 'NOT_FHA']

    # Doctrinal richness proxies
    n_fha_claims = len(fha_claims)
    n_theories = len(set(c.get('theory', '') for c in fha_claims))
    reached_merits = any(c.get('merits_reached') in ('YES', 'PARTIAL') for c in fha_claims)
    survived_mtd = any(c.get('dismissal_reason') in ('SURVIVES_MTD', 'SURVIVES_PROCEDURAL',
                        'SUMMARY_JUDGMENT_GRANTED', 'SUMMARY_JUDGMENT_DENIED',
                        'PLAINTIFF_PREVAILS_MERITS', 'DEFENDANT_PREVAILS_MERITS')
                       for c in fha_claims)
    reached_sj_or_trial = any(c.get('stage') in ('SUMMARY_JUDGMENT', 'TRIAL') for c in fha_claims)
    has_interactive_process = r.get('interactive_process_discussed') in ('YES', True)

    # Plaintiff classification
    pt = r.get('plaintiff_type', '')
    if pt in ('FAIR_HOUSING_ORG', 'GOVERNMENT'):
        plaintiff_cat = 'INSTITUTIONAL'
    elif pt == 'GROUP_HOME_OPERATOR':
        plaintiff_cat = 'GROUP_HOME'
    else:
        plaintiff_cat = 'INDIVIDUAL'

    records.append({
        'source_file': r.get('source_file', ''),
        'year': r.get('year'),
        'outcome': r.get('outcome', ''),
        'pro_se': r.get('pro_se', False),
        'plaintiff_type': pt,
        'plaintiff_cat': plaintiff_cat,
        'defendant_type': r.get('defendant_type', ''),
        'n_fha_claims': n_fha_claims,
        'n_theories': n_theories,
        'reached_merits': reached_merits,
        'survived_mtd': survived_mtd,
        'reached_sj_or_trial': reached_sj_or_trial,
        'has_interactive_process': has_interactive_process,
        'claim_specificity': supp.get('claim_specificity', 'MISSING'),
        'technical_complexity': supp.get('technical_complexity', 'MISSING'),
    })

df = pd.DataFrame(records)

# Period
df['period'] = df['year'].apply(lambda y: 'P1' if y and y <= 2023
                                else ('P2' if y == 2024
                                      else ('P3' if y and y >= 2025 else None)))
dated = df[df['period'].notna()].copy()

# Binary outcomes
excluded = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
decided = dated[~dated['outcome'].isin(excluded)].copy()
decided['strict_win'] = (decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
decided['broad_win'] = decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

print(f"Dated: {len(dated)}, Decided: {len(decided)}")
print(f"Plaintiff categories: {dict(Counter(dated['plaintiff_cat']))}")

results_store = {}

# ============================================================
# 3. OUTCOME COMPARISON: INSTITUTIONAL vs INDIVIDUAL
# ============================================================

print("\n" + "=" * 70)
print("H5: INSTITUTIONAL vs INDIVIDUAL PLAINTIFF OUTCOMES")
print("=" * 70)

# Win rates by plaintiff category
print("\nWin rates by plaintiff category:")
h5_rates = {}
for cat in ['INSTITUTIONAL', 'GROUP_HOME', 'INDIVIDUAL']:
    subset = decided[decided['plaintiff_cat'] == cat]
    if len(subset) > 0:
        h5_rates[cat] = {
            'n': int(len(subset)),
            'strict_win': round(subset['strict_win'].mean(), 4),
            'broad_win': round(subset['broad_win'].mean(), 4),
            'pro_se_share': round((subset['pro_se'] == True).mean(), 4),
        }
        print(f"  {cat}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}, pro_se={(subset['pro_se']==True).mean():.1%}")

results_store['win_rates_by_plaintiff'] = h5_rates

# Detailed breakdown
print("\nDetailed plaintiff_type breakdown:")
for pt in ['INDIVIDUAL_TENANT', 'GROUP_HOME_OPERATOR', 'FAIR_HOUSING_ORG', 'GOVERNMENT']:
    subset = decided[decided['plaintiff_type'] == pt]
    if len(subset) >= 5:
        print(f"  {pt}: n={len(subset)}, strict={subset['strict_win'].mean():.1%}, "
              f"broad={subset['broad_win'].mean():.1%}")

# Chi-squared
contingency = pd.crosstab(decided['plaintiff_cat'], decided['broad_win'])
chi2, p, dof, _ = stats.chi2_contingency(contingency)
print(f"\nChi-squared (broad_win ~ plaintiff_cat): chi2={chi2:.3f}, p={p:.4f}")
results_store['chi2_plaintiff_outcome'] = {'chi2': round(chi2, 3), 'p': round(p, 4)}

# ============================================================
# 4. PROCEDURAL DEPTH: WHO REACHES THE MERITS?
# ============================================================

print("\n" + "=" * 70)
print("PROCEDURAL DEPTH BY PLAINTIFF CATEGORY")
print("=" * 70)

depth_stats = {}
for cat in ['INSTITUTIONAL', 'GROUP_HOME', 'INDIVIDUAL']:
    subset = dated[dated['plaintiff_cat'] == cat]
    if len(subset) > 0:
        depth_stats[cat] = {
            'n': int(len(subset)),
            'mtd_survival': round(subset['survived_mtd'].mean(), 4),
            'merits_reached': round(subset['reached_merits'].mean(), 4),
            'sj_or_trial': round(subset['reached_sj_or_trial'].mean(), 4),
            'interactive_process': round(subset['has_interactive_process'].mean(), 4),
            'avg_fha_claims': round(subset['n_fha_claims'].mean(), 2),
            'avg_theories': round(subset['n_theories'].mean(), 2),
        }
        print(f"\n  {cat} (n={len(subset)}):")
        print(f"    MTD survival:      {subset['survived_mtd'].mean():.1%}")
        print(f"    Merits reached:    {subset['reached_merits'].mean():.1%}")
        print(f"    SJ or trial:       {subset['reached_sj_or_trial'].mean():.1%}")
        print(f"    Interactive proc:  {subset['has_interactive_process'].mean():.1%}")
        print(f"    Avg FHA claims:    {subset['n_fha_claims'].mean():.2f}")
        print(f"    Avg theories:      {subset['n_theories'].mean():.2f}")

results_store['procedural_depth'] = depth_stats

# Chi-squared on merits-reached
contingency_merits = pd.crosstab(dated['plaintiff_cat'], dated['reached_merits'])
chi2_m, p_m, dof_m, _ = stats.chi2_contingency(contingency_merits)
print(f"\nChi-squared (merits_reached ~ plaintiff_cat): chi2={chi2_m:.3f}, p={p_m:.4f}")
results_store['chi2_merits_reached'] = {'chi2': round(chi2_m, 3), 'p': round(p_m, 4)}

# ============================================================
# 5. CLAIM SPECIFICITY AND COMPLEXITY BY PLAINTIFF TYPE
# ============================================================

print("\n" + "=" * 70)
print("CLAIM SPECIFICITY × PLAINTIFF CATEGORY")
print("=" * 70)

for cat in ['INSTITUTIONAL', 'GROUP_HOME', 'INDIVIDUAL']:
    subset = dated[dated['plaintiff_cat'] == cat]
    spec_dist = subset['claim_specificity'].value_counts(normalize=True) * 100
    comp_dist = subset['technical_complexity'].value_counts(normalize=True) * 100
    print(f"\n  {cat} (n={len(subset)}):")
    print(f"    Specificity: {spec_dist.to_dict()}")
    print(f"    Complexity:  {comp_dist.to_dict()}")

# ============================================================
# 6. PERIOD ANALYSIS: INSTITUTIONAL PRESENCE OVER TIME
# ============================================================

print("\n" + "=" * 70)
print("INSTITUTIONAL PRESENCE BY PERIOD")
print("=" * 70)

period_presence = {}
for p in ['P1', 'P2', 'P3']:
    p_data = dated[dated['period'] == p]
    inst_share = (p_data['plaintiff_cat'].isin(['INSTITUTIONAL', 'GROUP_HOME'])).mean()
    inst_n = (p_data['plaintiff_cat'].isin(['INSTITUTIONAL', 'GROUP_HOME'])).sum()
    period_presence[p] = {
        'total': int(len(p_data)),
        'institutional_n': int(inst_n),
        'institutional_share': round(inst_share, 4),
    }
    print(f"  {p}: {inst_n}/{len(p_data)} institutional ({inst_share:.1%})")

results_store['institutional_by_period'] = period_presence

# Institutional win rates by period
print("\nInstitutional plaintiff broad win by period:")
inst_decided = decided[decided['plaintiff_cat'].isin(['INSTITUTIONAL', 'GROUP_HOME'])]
for p in ['P1', 'P2', 'P3']:
    subset = inst_decided[inst_decided['period'] == p]
    if len(subset) >= 5:
        print(f"  {p}: {subset['broad_win'].mean():.1%} (n={len(subset)})")

# ============================================================
# 7. REGRESSION: INSTITUTIONAL EFFECT ON OUTCOMES
# ============================================================

print("\n" + "=" * 70)
print("REGRESSION: INSTITUTIONAL EFFECT")
print("=" * 70)

reg = decided.copy()
reg['is_institutional'] = reg['plaintiff_cat'].isin(['INSTITUTIONAL', 'GROUP_HOME']).astype(int)
reg['pro_se_int'] = reg['pro_se'].apply(lambda x: 1 if x is True else 0)
reg['post_2024'] = (reg['year'] >= 2024).astype(int)

def_map = {
    'PRIVATE_LANDLORD': 'PRIVATE', 'PROPERTY_MANAGEMENT': 'PRIVATE',
    'HOA_CONDO_ASSN': 'PRIVATE', 'HOA_CONDO_BOARD': 'PRIVATE',
    'HOA_CONDO': 'PRIVATE', 'REAL_ESTATE_AGENT': 'PRIVATE',
    'DEVELOPER_BUILDER': 'PRIVATE',
    'HOUSING_AUTHORITY': 'PUBLIC_QUASI', 'MUNICIPALITY': 'PUBLIC_QUASI',
}
reg['def_cat'] = reg['defendant_type'].map(def_map).fillna('OTHER')

# Model: broad_win ~ institutional + pro_se + period + defendant
try:
    formula = 'broad_win ~ is_institutional + pro_se_int + post_2024 + C(def_cat)'
    model = logit(formula, data=reg).fit(disp=0)
    print(model.summary2().tables[1].to_string())
    results_store['model_institutional'] = {
        'formula': formula,
        'n': int(model.nobs),
        'pseudo_r2': round(model.prsquared, 4),
        'coefficients': {name: {
            'coef': round(model.params[name], 4),
            'se': round(model.bse[name], 4),
            'p': round(model.pvalues[name], 4),
            'or': round(np.exp(model.params[name]), 4)
        } for name in model.params.index}
    }
except Exception as e:
    print(f"  Model failed: {e}")
    results_store['model_institutional'] = {'error': str(e)}

# Model with merits_reached as DV
print("\n--- Merits Reached ~ Institutional + Controls ---")
reg_all = dated.copy()
reg_all['is_institutional'] = reg_all['plaintiff_cat'].isin(['INSTITUTIONAL', 'GROUP_HOME']).astype(int)
reg_all['pro_se_int'] = reg_all['pro_se'].apply(lambda x: 1 if x is True else 0)
reg_all['post_2024'] = (reg_all['year'] >= 2024).astype(int)
reg_all['def_cat'] = reg_all['defendant_type'].map(def_map).fillna('OTHER')
reg_all['merits_int'] = reg_all['reached_merits'].astype(int)

try:
    formula2 = 'merits_int ~ is_institutional + pro_se_int + post_2024 + C(def_cat)'
    model2 = logit(formula2, data=reg_all).fit(disp=0)
    print(model2.summary2().tables[1].to_string())
    results_store['model_merits_reached'] = {
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
    results_store['model_merits_reached'] = {'error': str(e)}

# ============================================================
# 8. SAVE RESULTS
# ============================================================

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results_store, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"H5 RESULTS SAVED TO {OUTPUT_PATH}")
print(f"{'='*70}")
