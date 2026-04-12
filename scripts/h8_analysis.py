"""
H8 Analysis: Public/quasi-public defendant cases are dominated by
information and process failures rather than intent disputes.

Tests whether cases against PHAs, municipalities, and subsidized
providers are primarily about recordkeeping, accommodation-process,
and inventory failures rather than intentional discrimination.

Outputs: h8_results.json
"""
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from scipy import stats
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/2/FHA_Unified_Database.json'
SUPP_PATH = 'supplemental_classification_results.json'
OUTPUT_PATH = 'h8_results.json'

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
# 2. CLASSIFY CASES BY DEFENDANT TYPE AND CLAIM PATTERN
# ============================================================

PROCESS_THEORIES = {'REASONABLE_ACCOMMODATION'}
INTENT_THEORIES = {'DISPARATE_TREATMENT', 'RETALIATION', 'INTERFERENCE_COERCION'}
STRUCTURAL_THEORIES = {'DESIGN_AND_CONSTRUCTION', 'DISPARATE_IMPACT'}

records = []
for r in disability:
    supp = r.get('supp', {})
    fha_claims = [c for c in r.get('fha_claims', []) if c.get('theory') != 'NOT_FHA']

    is_public = supp.get('public_quasi_public_defendant', False)
    def_type = r.get('defendant_type', '')

    # Classify defendant
    if def_type in ('HOUSING_AUTHORITY', 'MUNICIPALITY', 'GOVERNMENT'):
        def_cat = 'PUBLIC'
    elif is_public and def_type not in ('PRIVATE_LANDLORD', 'HOA_CONDO_ASSN', 'HOA_CONDO_BOARD',
                                         'HOA_CONDO', 'REAL_ESTATE_AGENT'):
        def_cat = 'QUASI_PUBLIC'
    else:
        def_cat = 'PRIVATE'

    # Claim pattern analysis
    theories = set(c.get('theory', '') for c in fha_claims)
    has_process = bool(theories & PROCESS_THEORIES)
    has_intent = bool(theories & INTENT_THEORIES)
    has_structural = bool(theories & STRUCTURAL_THEORIES)

    # Dominant claim pattern
    if has_process and not has_intent:
        claim_pattern = 'PROCESS_ONLY'
    elif has_intent and not has_process:
        claim_pattern = 'INTENT_ONLY'
    elif has_process and has_intent:
        claim_pattern = 'PROCESS_AND_INTENT'
    elif has_structural:
        claim_pattern = 'STRUCTURAL'
    else:
        claim_pattern = 'OTHER'

    # Process-failure indicators
    interactive = r.get('interactive_process_discussed') in ('YES', True)
    delay = r.get('delay_as_denial') in ('YES', True)
    measurable = supp.get('measurable_facts_flag', False)

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
        'defendant_type': def_type,
        'def_cat': def_cat,
        'is_public_defendant': is_public,
        'claim_pattern': claim_pattern,
        'has_process_claim': has_process,
        'has_intent_claim': has_intent,
        'has_structural_claim': has_structural,
        'interactive_process': interactive,
        'delay_as_denial': delay,
        'measurable_facts': measurable,
        'survived_mtd': survived_mtd,
        'reached_merits': reached_merits,
        'n_fha_claims': len(fha_claims),
        'housing_type': r.get('housing_type', ''),
        'claim_specificity': supp.get('claim_specificity', 'MISSING'),
        'technical_complexity': supp.get('technical_complexity', 'MISSING'),
    })

df = pd.DataFrame(records)
df['period'] = df['year'].apply(lambda y: 'P1' if y and y <= 2023
                                else ('P2' if y == 2024
                                      else ('P3' if y and y >= 2025 else None)))
dated = df[df['period'].notna()].copy()

print(f"\nDated: {len(dated)}")
print(f"Defendant categories: {dict(Counter(dated['def_cat']))}")

results_store = {}

# ============================================================
# 3. CLAIM PATTERN DISTRIBUTION: PUBLIC vs PRIVATE
# ============================================================

print("\n" + "=" * 70)
print("H8: CLAIM PATTERNS BY DEFENDANT TYPE")
print("=" * 70)

# Public vs private
for cat in ['PUBLIC', 'QUASI_PUBLIC', 'PRIVATE']:
    subset = dated[dated['def_cat'] == cat]
    print(f"\n{cat} (n={len(subset)}):")
    pattern_dist = subset['claim_pattern'].value_counts()
    pattern_pct = subset['claim_pattern'].value_counts(normalize=True) * 100
    for pat in ['PROCESS_ONLY', 'INTENT_ONLY', 'PROCESS_AND_INTENT', 'STRUCTURAL', 'OTHER']:
        n = pattern_dist.get(pat, 0)
        pct = pattern_pct.get(pat, 0)
        print(f"  {pat}: {n} ({pct:.1f}%)")

# Consolidated public vs private
print("\n--- Public/Quasi-Public vs Private ---")
pub = dated[dated['def_cat'].isin(['PUBLIC', 'QUASI_PUBLIC'])]
priv = dated[dated['def_cat'] == 'PRIVATE']

pub_patterns = pub['claim_pattern'].value_counts(normalize=True) * 100
priv_patterns = priv['claim_pattern'].value_counts(normalize=True) * 100

comparison = pd.DataFrame({
    'Public/Quasi-Public': pub_patterns,
    'Private': priv_patterns,
}).fillna(0).round(1)
print(comparison.to_string())

results_store['claim_pattern_comparison'] = {
    'public': pub['claim_pattern'].value_counts().to_dict(),
    'private': priv['claim_pattern'].value_counts().to_dict(),
    'public_pct': pub_patterns.round(4).to_dict(),
    'private_pct': priv_patterns.round(4).to_dict(),
}

# Chi-squared: claim pattern ~ defendant type
dated_pub_priv = dated[dated['def_cat'].isin(['PUBLIC', 'QUASI_PUBLIC', 'PRIVATE'])].copy()
dated_pub_priv['is_public'] = dated_pub_priv['def_cat'].isin(['PUBLIC', 'QUASI_PUBLIC']).astype(int)
contingency = pd.crosstab(dated_pub_priv['is_public'], dated_pub_priv['claim_pattern'])
chi2, p, dof, _ = stats.chi2_contingency(contingency)
print(f"\nChi-squared (claim_pattern ~ public/private): chi2={chi2:.3f}, p={p:.4f}, df={dof}")
results_store['chi2_pattern'] = {'chi2': round(chi2, 3), 'p': round(p, 4)}

# ============================================================
# 4. PROCESS-FAILURE INDICATORS BY DEFENDANT TYPE
# ============================================================

print("\n" + "=" * 70)
print("PROCESS-FAILURE INDICATORS")
print("=" * 70)

process_indicators = {}
for cat in ['PUBLIC', 'QUASI_PUBLIC', 'PRIVATE']:
    subset = dated[dated['def_cat'] == cat]
    if len(subset) > 0:
        process_indicators[cat] = {
            'n': int(len(subset)),
            'interactive_process_rate': round(subset['interactive_process'].mean(), 4),
            'delay_as_denial_rate': round(subset['delay_as_denial'].mean(), 4),
            'measurable_facts_rate': round(subset['measurable_facts'].mean(), 4),
            'process_claim_rate': round(subset['has_process_claim'].mean(), 4),
            'intent_claim_rate': round(subset['has_intent_claim'].mean(), 4),
        }
        print(f"\n  {cat} (n={len(subset)}):")
        print(f"    Interactive process discussed: {subset['interactive_process'].mean():.1%}")
        print(f"    Delay as denial:              {subset['delay_as_denial'].mean():.1%}")
        print(f"    Measurable facts:             {subset['measurable_facts'].mean():.1%}")
        print(f"    Has process claim:            {subset['has_process_claim'].mean():.1%}")
        print(f"    Has intent claim:             {subset['has_intent_claim'].mean():.1%}")

results_store['process_indicators'] = process_indicators

# ============================================================
# 5. OUTCOMES BY DEFENDANT TYPE × CLAIM PATTERN
# ============================================================

print("\n" + "=" * 70)
print("OUTCOMES BY DEFENDANT TYPE x CLAIM PATTERN")
print("=" * 70)

excluded = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
decided = dated[~dated['outcome'].isin(excluded)].copy()
decided['strict_win'] = (decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
decided['broad_win'] = decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

outcome_table = {}
for cat in ['PUBLIC', 'QUASI_PUBLIC', 'PRIVATE']:
    cat_data = decided[decided['def_cat'] == cat]
    outcome_table[cat] = {}
    for pat in ['PROCESS_ONLY', 'INTENT_ONLY', 'PROCESS_AND_INTENT']:
        subset = cat_data[cat_data['claim_pattern'] == pat]
        if len(subset) >= 5:
            outcome_table[cat][pat] = {
                'n': int(len(subset)),
                'broad_win': round(subset['broad_win'].mean(), 4),
                'mtd_survival': round(subset['survived_mtd'].mean(), 4),
            }
            print(f"  {cat}/{pat}: n={len(subset)}, broad_win={subset['broad_win'].mean():.1%}, "
                  f"MTD surv={subset['survived_mtd'].mean():.1%}")

results_store['outcome_by_pattern'] = outcome_table

# ============================================================
# 6. HOUSING TYPE DISTRIBUTION FOR PUBLIC DEFENDANTS
# ============================================================

print("\n" + "=" * 70)
print("HOUSING TYPE IN PUBLIC-DEFENDANT CASES")
print("=" * 70)

pub_all = dated[dated['def_cat'].isin(['PUBLIC', 'QUASI_PUBLIC'])]
ht_dist = pub_all['housing_type'].value_counts()
ht_pct = pub_all['housing_type'].value_counts(normalize=True) * 100
print("\nHousing type distribution:")
for ht in ht_dist.index:
    print(f"  {ht}: {ht_dist[ht]} ({ht_pct[ht]:.1f}%)")

results_store['public_housing_types'] = ht_dist.to_dict()

# ============================================================
# 7. SPECIFICITY AND COMPLEXITY IN PUBLIC vs PRIVATE
# ============================================================

print("\n" + "=" * 70)
print("SPECIFICITY AND COMPLEXITY: PUBLIC vs PRIVATE")
print("=" * 70)

for cat in ['PUBLIC', 'QUASI_PUBLIC', 'PRIVATE']:
    subset = dated[dated['def_cat'] == cat]
    spec = subset['claim_specificity'].value_counts(normalize=True) * 100
    comp = subset['technical_complexity'].value_counts(normalize=True) * 100
    print(f"\n  {cat} (n={len(subset)}):")
    print(f"    Specificity: " + ", ".join(f"{k}={v:.1f}%" for k, v in spec.items()))
    print(f"    Complexity:  " + ", ".join(f"{k}={v:.1f}%" for k, v in comp.items()))

# ============================================================
# 8. REGRESSION: PUBLIC DEFENDANT EFFECT
# ============================================================

print("\n" + "=" * 70)
print("REGRESSION: PUBLIC DEFENDANT x PROCESS CLAIMS")
print("=" * 70)

reg = decided.copy()
reg['is_public'] = reg['def_cat'].isin(['PUBLIC', 'QUASI_PUBLIC']).astype(int)
reg['pro_se_int'] = reg['pro_se'].apply(lambda x: 1 if x is True else 0)
reg['post_2024'] = (reg['year'] >= 2024).astype(int)
reg['process_int'] = reg['has_process_claim'].astype(int)
reg['intent_int'] = reg['has_intent_claim'].astype(int)
reg['pub_x_process'] = reg['is_public'] * reg['process_int']

try:
    formula = ('broad_win ~ is_public + process_int + intent_int '
               '+ pub_x_process + pro_se_int + post_2024')
    model = logit(formula, data=reg).fit(disp=0)
    print(model.summary2().tables[1].to_string())
    results_store['model_public_process'] = {
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
    results_store['model_public_process'] = {'error': str(e)}

# ============================================================
# 9. CLAIM-LEVEL ANALYSIS: DISMISSAL REASONS IN PUBLIC CASES
# ============================================================

print("\n" + "=" * 70)
print("CLAIM-LEVEL DISMISSAL REASONS: PUBLIC vs PRIVATE")
print("=" * 70)

claim_rows = []
for r in disability:
    if r.get('year') is None:
        continue
    supp = r.get('supp', {})
    is_pub = supp.get('public_quasi_public_defendant', False)
    for c in r.get('fha_claims', []):
        if c.get('theory') == 'NOT_FHA':
            continue
        claim_rows.append({
            'is_public': is_pub,
            'theory': c.get('theory', ''),
            'dismissal_reason': c.get('dismissal_reason', 'OTHER'),
            'stage': c.get('stage', 'OTHER'),
            'merits_reached': c.get('merits_reached', 'NO'),
        })

claims_df = pd.DataFrame(claim_rows)

# Theory distribution
for label, val in [('Public/quasi-public', True), ('Private', False)]:
    subset = claims_df[claims_df['is_public'] == val]
    theory_pct = subset['theory'].value_counts(normalize=True) * 100
    print(f"\n{label} claim theories (n={len(subset)}):")
    for t in theory_pct.index:
        print(f"  {t}: {theory_pct[t]:.1f}%")

# Dismissal reason comparison
pub_reasons = claims_df[claims_df['is_public']]['dismissal_reason'].value_counts(normalize=True) * 100
priv_reasons = claims_df[~claims_df['is_public']]['dismissal_reason'].value_counts(normalize=True) * 100
reason_comp = pd.DataFrame({
    'Public': pub_reasons,
    'Private': priv_reasons,
}).fillna(0).round(1)
print("\nDismissal reason comparison (%):")
print(reason_comp.to_string())

results_store['claim_level'] = {
    'public_theories': claims_df[claims_df['is_public']]['theory'].value_counts().to_dict(),
    'private_theories': claims_df[~claims_df['is_public']]['theory'].value_counts().to_dict(),
}

# ============================================================
# 10. SAVE
# ============================================================

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results_store, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"H8 RESULTS SAVED TO {OUTPUT_PATH}")
print(f"{'='*70}")
