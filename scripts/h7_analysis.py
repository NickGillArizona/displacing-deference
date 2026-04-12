"""
H7 Analysis: Is the post-2024 downturn concentrated at early procedural stages?

Tests the institutional-withdrawal thesis by examining whether case outcomes
deteriorated primarily at threshold/pleading stages rather than uniformly.

Outputs: h7_results.json
"""
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
from collections import Counter, defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/2/FHA_Unified_Database.json'
OUTPUT_PATH = 'h7_results.json'

# ============================================================
# 1. LOAD AND PREPARE DATA
# ============================================================
with open(DB_PATH, 'r', encoding='utf-8') as f:
    raw = json.load(f)

# Disability filter: screening_result=YES and disability-related
disability = [r for r in raw if r.get('screening_result') == 'YES'
              and (r.get('disability_alleged') or r.get('is_ra_case')
                   or 'disability' in (r.get('protected_classes') or []))]

print(f"Total records: {len(raw)}")
print(f"Screened-in: {sum(1 for r in raw if r.get('screening_result') == 'YES')}")
print(f"Disability screened-in: {len(disability)}")

# ============================================================
# 2. CLASSIFY TERMINAL STAGE AND MTD SURVIVAL
# ============================================================

THRESHOLD_REASONS = {'SCREENING_1915', 'STANDING', 'JURISDICTIONAL', 'STATUTE_OF_LIMITATIONS'}
PLEADING_REASONS = {'IQBAL_TWOMBLY', 'NEXUS_FAILURE'}
SURVIVED_REASONS = {'SURVIVES_MTD', 'SURVIVES_PROCEDURAL'}
MERITS_REASONS = {'PLAINTIFF_PREVAILS_MERITS', 'DEFENDANT_PREVAILS_MERITS',
                  'SUMMARY_JUDGMENT_GRANTED', 'SUMMARY_JUDGMENT_DENIED'}

STAGE_ORDER = {
    'SCREENING_1915': 0, 'MTD': 1, 'PRELIMINARY_INJUNCTION': 2,
    'SUMMARY_JUDGMENT': 3, 'TRIAL': 4, 'APPEAL': 5,
    'CONSENT_DECREE': 6, 'OTHER': 1,
}


def classify_case(record):
    """Classify a case's terminal stage, MTD survival, and stage category."""
    claims = record.get('fha_claims', [])
    fha_claims = [c for c in claims if c.get('theory') != 'NOT_FHA']

    if not fha_claims:
        return {'terminal_stage': None, 'mtd_survived': None,
                'stage_category': None, 'n_fha_claims': 0}

    # Terminal stage = highest stage reached by any FHA claim
    max_stage = 'SCREENING_1915'
    max_order = -1
    for c in fha_claims:
        stage = c.get('stage', 'OTHER')
        order = STAGE_ORDER.get(stage, 1)
        if order > max_order:
            max_order = order
            max_stage = stage

    # MTD survival: did any FHA claim survive past pleading?
    mtd_relevant = False
    mtd_survived = False
    for c in fha_claims:
        stage = c.get('stage', 'OTHER')
        reason = c.get('dismissal_reason', 'OTHER')
        if stage in ('MTD', 'SCREENING_1915', 'OTHER'):
            mtd_relevant = True
            if reason in SURVIVED_REASONS or reason in MERITS_REASONS or reason == 'SETTLEMENT':
                mtd_survived = True
        elif stage in ('SUMMARY_JUDGMENT', 'TRIAL', 'CONSENT_DECREE'):
            mtd_survived = True
            mtd_relevant = True

    # Stage category for the case
    all_reasons = set(c.get('dismissal_reason', 'OTHER') for c in fha_claims)
    all_outcomes = set(c.get('outcome', 'PENDING') for c in fha_claims)

    if all_reasons <= THRESHOLD_REASONS:
        stage_cat = 'THRESHOLD'
    elif all_reasons <= (THRESHOLD_REASONS | PLEADING_REASONS):
        stage_cat = 'PLEADING'
    elif all_reasons & MERITS_REASONS:
        stage_cat = 'MERITS_RESOLVED'
    elif all_reasons & SURVIVED_REASONS:
        stage_cat = 'SURVIVED_PENDING'
    elif 'SETTLEMENT' in all_reasons:
        stage_cat = 'SETTLEMENT'
    elif all_reasons & {'AFFIRMED', 'REVERSED', 'REMANDED'}:
        stage_cat = 'APPELLATE'
    else:
        stage_cat = 'OTHER'

    return {
        'terminal_stage': max_stage,
        'mtd_survived': mtd_survived if mtd_relevant else None,
        'stage_category': stage_cat,
        'n_fha_claims': len(fha_claims),
    }


# Apply classification
for r in disability:
    result = classify_case(r)
    r.update(result)

# Assign periods
for r in disability:
    yr = r.get('year')
    if yr is None:
        r['period'] = None
    elif yr <= 2023:
        r['period'] = 'P1'
    elif yr == 2024:
        r['period'] = 'P2'
    else:
        r['period'] = 'P3'

# Build DataFrame
df = pd.DataFrame(disability)
dated = df[df['period'].notna()].copy()
print(f"\nDated disability cases: {len(dated)}")
print(f"  P1: {(dated['period']=='P1').sum()}, P2: {(dated['period']=='P2').sum()}, P3: {(dated['period']=='P3').sum()}")

# ============================================================
# 3. CROSS-TABULATION: STAGE CATEGORY × PERIOD × REPRESENTATION
# ============================================================

print("\n" + "="*70)
print("CROSS-TABULATION: Stage Category × Period")
print("="*70)

# Stage category × period
stage_period = pd.crosstab(dated['stage_category'], dated['period'],
                           margins=True, margins_name='Total')
stage_period_pct = pd.crosstab(dated['stage_category'], dated['period'],
                               normalize='columns') * 100
print("\nCounts:")
print(stage_period.to_string())
print("\nColumn percentages:")
print(stage_period_pct.round(1).to_string())

# Stage category × period × pro_se
print("\n" + "="*70)
print("STAGE CATEGORY × PERIOD × REPRESENTATION")
print("="*70)

for ps_label, ps_val in [('Pro se', True), ('Represented', False)]:
    subset = dated[dated['pro_se'] == ps_val]
    ct = pd.crosstab(subset['stage_category'], subset['period'], margins=True, margins_name='Total')
    ct_pct = pd.crosstab(subset['stage_category'], subset['period'], normalize='columns') * 100
    print(f"\n{ps_label} (n={len(subset)}):")
    print(ct.to_string())
    print(f"\n{ps_label} column %:")
    print(ct_pct.round(1).to_string())

# ============================================================
# 4. MTD SURVIVAL ANALYSIS
# ============================================================

print("\n" + "="*70)
print("MTD SURVIVAL ANALYSIS")
print("="*70)

mtd_cases = dated[dated['mtd_survived'].notna()].copy()
mtd_cases['mtd_survived_int'] = mtd_cases['mtd_survived'].astype(int)
print(f"\nCases with MTD-relevant claims: {len(mtd_cases)}")

# MTD survival rates by period
mtd_by_period = mtd_cases.groupby('period')['mtd_survived_int'].agg(['mean', 'sum', 'count'])
mtd_by_period.columns = ['survival_rate', 'survived', 'total']
print("\nMTD survival by period:")
print(mtd_by_period.to_string())

# MTD survival by period × representation
print("\nMTD survival by period × representation:")
for p in ['P1', 'P2', 'P3']:
    p_data = mtd_cases[mtd_cases['period'] == p]
    for ps_label, ps_val in [('Pro se', True), ('Represented', False)]:
        subset = p_data[p_data['pro_se'] == ps_val]
        if len(subset) > 0:
            rate = subset['mtd_survived_int'].mean()
            n = len(subset)
            survived = subset['mtd_survived_int'].sum()
            print(f"  {p} / {ps_label}: {survived}/{n} = {rate:.1%}")

# Chi-squared test: MTD survival vs period
contingency_mtd = pd.crosstab(mtd_cases['period'], mtd_cases['mtd_survived'])
chi2_mtd, p_mtd, dof_mtd, expected_mtd = stats.chi2_contingency(contingency_mtd)
print(f"\nChi-squared (MTD survival ~ period): chi2={chi2_mtd:.3f}, p={p_mtd:.4f}, df={dof_mtd}")

# ============================================================
# 5. LOGISTIC REGRESSION MODELS
# ============================================================

print("\n" + "="*70)
print("LOGISTIC REGRESSION MODELS")
print("="*70)

# Prepare regression data
reg_data = dated.copy()
reg_data['pro_se_int'] = reg_data['pro_se'].apply(lambda x: 1 if x is True else 0)
reg_data['post_2024'] = (reg_data['year'] >= 2024).astype(int)

# Map defendant type to categories
def_map = {
    'PRIVATE_LANDLORD': 'PRIVATE', 'PROPERTY_MANAGEMENT': 'PRIVATE',
    'HOA_CONDO_ASSN': 'PRIVATE', 'HOA_CONDO_BOARD': 'PRIVATE',
    'HOA_CONDO': 'PRIVATE', 'REAL_ESTATE_AGENT': 'PRIVATE',
    'DEVELOPER': 'PUBLIC_QUASI', 'DEVELOPER_BUILDER': 'PRIVATE',
    'HOUSING_AUTHORITY': 'PUBLIC_QUASI', 'MUNICIPALITY': 'PUBLIC_QUASI',
}
reg_data['def_cat'] = reg_data['defendant_type'].map(def_map).fillna('OTHER')

# Binary outcomes
excluded_outcomes = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
decided = reg_data[~reg_data['outcome'].isin(excluded_outcomes)].copy()
decided['strict_win'] = (decided['outcome'] == 'PLAINTIFF_WIN').astype(int)
decided['broad_win'] = decided['outcome'].isin(['PLAINTIFF_WIN', 'MIXED']).astype(int)

# Encode stage_category
decided['at_threshold'] = (decided['stage_category'] == 'THRESHOLD').astype(int)
decided['at_pleading'] = (decided['stage_category'] == 'PLEADING').astype(int)
decided['at_merits'] = (decided['stage_category'] == 'MERITS_RESOLVED').astype(int)

print(f"\nDecided cases for regression: {len(decided)}")
print(f"  Strict win rate: {decided['strict_win'].mean():.1%}")
print(f"  Broad win rate: {decided['broad_win'].mean():.1%}")

results_store = {}

# --- Model 1: MTD survival ~ period + pro_se + defendant_type ---
print("\n--- Model 1: MTD Survival ---")
mtd_reg = mtd_cases.copy()
mtd_reg['pro_se_int'] = mtd_reg['pro_se'].apply(lambda x: 1 if x is True else 0)
mtd_reg['post_2024'] = (mtd_reg['year'] >= 2024).astype(int)
mtd_reg['def_cat'] = mtd_reg['defendant_type'].map(def_map).fillna('OTHER')

# Ensure enough variation
print(f"  N={len(mtd_reg)}, MTD survived={mtd_reg['mtd_survived_int'].sum()}")

try:
    formula_mtd = 'mtd_survived_int ~ post_2024 + pro_se_int + C(def_cat)'
    model_mtd = logit(formula_mtd, data=mtd_reg).fit(disp=0)
    print(model_mtd.summary2().tables[1].to_string())
    results_store['model1_mtd_survival'] = {
        'formula': formula_mtd,
        'n': int(model_mtd.nobs),
        'pseudo_r2': round(model_mtd.prsquared, 4),
        'coefficients': {name: {'coef': round(model_mtd.params[name], 4),
                                'se': round(model_mtd.bse[name], 4),
                                'p': round(model_mtd.pvalues[name], 4),
                                'or': round(np.exp(model_mtd.params[name]), 4)}
                         for name in model_mtd.params.index}
    }
except Exception as e:
    print(f"  Model 1 failed: {e}")
    results_store['model1_mtd_survival'] = {'error': str(e)}

# --- Model 2: Broad win ~ period + stage + pro_se + defendant ---
print("\n--- Model 2: Broad Win with Stage Controls ---")
try:
    formula_win = 'broad_win ~ post_2024 + pro_se_int + at_threshold + at_pleading + C(def_cat)'
    model_win = logit(formula_win, data=decided).fit(disp=0)
    print(model_win.summary2().tables[1].to_string())
    results_store['model2_broad_win'] = {
        'formula': formula_win,
        'n': int(model_win.nobs),
        'pseudo_r2': round(model_win.prsquared, 4),
        'coefficients': {name: {'coef': round(model_win.params[name], 4),
                                'se': round(model_win.bse[name], 4),
                                'p': round(model_win.pvalues[name], 4),
                                'or': round(np.exp(model_win.params[name]), 4)}
                         for name in model_win.params.index}
    }
except Exception as e:
    print(f"  Model 2 failed: {e}")
    results_store['model2_broad_win'] = {'error': str(e)}

# --- Model 3: Interaction model - period * stage ---
print("\n--- Model 3: Period × Stage Interaction ---")
try:
    decided['post_x_threshold'] = decided['post_2024'] * decided['at_threshold']
    decided['post_x_pleading'] = decided['post_2024'] * decided['at_pleading']

    formula_int = ('broad_win ~ post_2024 + pro_se_int + at_threshold + at_pleading '
                   '+ post_x_threshold + post_x_pleading + C(def_cat)')
    model_int = logit(formula_int, data=decided).fit(disp=0)
    print(model_int.summary2().tables[1].to_string())
    results_store['model3_interaction'] = {
        'formula': formula_int,
        'n': int(model_int.nobs),
        'pseudo_r2': round(model_int.prsquared, 4),
        'coefficients': {name: {'coef': round(model_int.params[name], 4),
                                'se': round(model_int.bse[name], 4),
                                'p': round(model_int.pvalues[name], 4),
                                'or': round(np.exp(model_int.params[name]), 4)}
                         for name in model_int.params.index}
    }
except Exception as e:
    print(f"  Model 3 failed: {e}")
    results_store['model3_interaction'] = {'error': str(e)}

# --- Model 4: MTD survival with period × representation interaction ---
print("\n--- Model 4: MTD Survival with Period × Representation Interaction ---")
try:
    mtd_reg['post_x_prose'] = mtd_reg['post_2024'] * mtd_reg['pro_se_int']
    formula_mtd2 = 'mtd_survived_int ~ post_2024 + pro_se_int + post_x_prose + C(def_cat)'
    model_mtd2 = logit(formula_mtd2, data=mtd_reg).fit(disp=0)
    print(model_mtd2.summary2().tables[1].to_string())
    results_store['model4_mtd_period_x_rep'] = {
        'formula': formula_mtd2,
        'n': int(model_mtd2.nobs),
        'pseudo_r2': round(model_mtd2.prsquared, 4),
        'coefficients': {name: {'coef': round(model_mtd2.params[name], 4),
                                'se': round(model_mtd2.bse[name], 4),
                                'p': round(model_mtd2.pvalues[name], 4),
                                'or': round(np.exp(model_mtd2.params[name]), 4)}
                         for name in model_mtd2.params.index}
    }
except Exception as e:
    print(f"  Model 4 failed: {e}")
    results_store['model4_mtd_period_x_rep'] = {'error': str(e)}

# ============================================================
# 6. STRATIFIED ANALYSIS: WIN RATES BY STAGE × PERIOD
# ============================================================

print("\n" + "="*70)
print("STRATIFIED ANALYSIS: Win Rates by Stage Category × Period")
print("="*70)

stratified = {}
for stage_cat in ['THRESHOLD', 'PLEADING', 'MERITS_RESOLVED', 'SURVIVED_PENDING', 'OTHER']:
    stage_data = decided[decided['stage_category'] == stage_cat]
    if len(stage_data) == 0:
        continue
    strat = {}
    for p in ['P1', 'P2', 'P3']:
        p_data = stage_data[stage_data['period'] == p]
        if len(p_data) > 0:
            strat[p] = {
                'n': int(len(p_data)),
                'strict_win_rate': round(p_data['strict_win'].mean(), 4),
                'broad_win_rate': round(p_data['broad_win'].mean(), 4),
            }
    stratified[stage_cat] = strat
    print(f"\n{stage_cat}:")
    for p in ['P1', 'P2', 'P3']:
        if p in strat:
            s = strat[p]
            print(f"  {p}: n={s['n']}, strict={s['strict_win_rate']:.1%}, broad={s['broad_win_rate']:.1%}")

results_store['stratified_win_rates'] = stratified

# ============================================================
# 7. CLAIM-LEVEL ANALYSIS: DISMISSAL REASONS BY PERIOD
# ============================================================

print("\n" + "="*70)
print("CLAIM-LEVEL ANALYSIS: Dismissal Reasons by Period")
print("="*70)

claim_rows = []
for r in disability:
    if r.get('period') is None:
        continue
    for c in r.get('fha_claims', []):
        if c.get('theory') == 'NOT_FHA':
            continue
        claim_rows.append({
            'period': r['period'],
            'pro_se': r.get('pro_se', False),
            'stage': c.get('stage', 'OTHER'),
            'dismissal_reason': c.get('dismissal_reason', 'OTHER'),
            'outcome': c.get('outcome', 'PENDING'),
            'theory': c.get('theory', 'UNCLEAR'),
        })

claims_df = pd.DataFrame(claim_rows)
print(f"\nTotal FHA claims (dated): {len(claims_df)}")

# Dismissal reason × period
reason_period = pd.crosstab(claims_df['dismissal_reason'], claims_df['period'],
                            normalize='columns') * 100
print("\nDismissal reason distribution by period (column %):")
print(reason_period.round(1).to_string())

# Stage × period
stage_period_claims = pd.crosstab(claims_df['stage'], claims_df['period'],
                                  normalize='columns') * 100
print("\nClaim stage distribution by period (column %):")
print(stage_period_claims.round(1).to_string())

# Early-exit rate (threshold + pleading) by period
claims_df['early_exit'] = claims_df['dismissal_reason'].isin(
    THRESHOLD_REASONS | PLEADING_REASONS).astype(int)
early_by_period = claims_df.groupby('period')['early_exit'].agg(['mean', 'sum', 'count'])
early_by_period.columns = ['early_exit_rate', 'early_exits', 'total_claims']
print("\nEarly-exit rate (threshold + pleading dismissals) by period:")
print(early_by_period.to_string())

# Early-exit by period × representation
print("\nEarly-exit rate by period × representation:")
for p in ['P1', 'P2', 'P3']:
    p_claims = claims_df[claims_df['period'] == p]
    for ps_label, ps_val in [('Pro se', True), ('Represented', False)]:
        subset = p_claims[p_claims['pro_se'] == ps_val]
        if len(subset) > 0:
            rate = subset['early_exit'].mean()
            print(f"  {p} / {ps_label}: {rate:.1%} ({subset['early_exit'].sum()}/{len(subset)})")

results_store['claim_level'] = {
    'early_exit_by_period': {p: {
        'rate': round(early_by_period.loc[p, 'early_exit_rate'], 4),
        'n': int(early_by_period.loc[p, 'total_claims']),
    } for p in ['P1', 'P2', 'P3'] if p in early_by_period.index},
}

# ============================================================
# 8. THREE-PERIOD DECOMPOSITION
# ============================================================

print("\n" + "="*70)
print("THREE-PERIOD DECOMPOSITION: P1→P2→P3 Transitions")
print("="*70)

# For each stage category, show the P1→P2→P3 trajectory
for stage_cat in ['THRESHOLD', 'PLEADING', 'MERITS_RESOLVED']:
    stage_data = dated[dated['stage_category'] == stage_cat]
    print(f"\n{stage_cat}:")
    for p in ['P1', 'P2', 'P3']:
        p_data = stage_data[stage_data['period'] == p]
        p_all = dated[dated['period'] == p]
        share = len(p_data) / len(p_all) * 100 if len(p_all) > 0 else 0
        prose_share = (p_data['pro_se'] == True).mean() * 100 if len(p_data) > 0 else 0
        print(f"  {p}: {len(p_data)} cases ({share:.1f}% of period), {prose_share:.0f}% pro se")

# ============================================================
# 9. KEY FINDING: Composition shift test
# ============================================================

print("\n" + "="*70)
print("COMPOSITION SHIFT TEST")
print("="*70)

# Test whether the stage distribution differs significantly across periods
stage_counts = pd.crosstab(dated['stage_category'], dated['period'])
# Only use categories with sufficient counts
stage_counts_filtered = stage_counts[stage_counts.sum(axis=1) >= 10]
if len(stage_counts_filtered) >= 2:
    chi2_comp, p_comp, dof_comp, _ = stats.chi2_contingency(stage_counts_filtered)
    print(f"Chi-squared (stage composition ~ period): chi2={chi2_comp:.3f}, p={p_comp:.4f}, df={dof_comp}")
    results_store['composition_shift_chi2'] = {
        'chi2': round(chi2_comp, 3), 'p': round(p_comp, 4), 'df': int(dof_comp)
    }

# Pro se composition by period
prose_by_period = dated.groupby('period')['pro_se'].apply(lambda x: (x == True).mean())
print(f"\nPro se share by period:")
for p in ['P1', 'P2', 'P3']:
    if p in prose_by_period.index:
        print(f"  {p}: {prose_by_period[p]:.1%}")

# ============================================================
# 10. SAVE RESULTS
# ============================================================

# Add cross-tab data to results
results_store['cross_tabs'] = {
    'stage_by_period': stage_period.to_dict(),
    'stage_by_period_pct': stage_period_pct.round(4).to_dict(),
}

results_store['mtd_survival'] = {
    'by_period': {p: {
        'rate': round(mtd_by_period.loc[p, 'survival_rate'], 4),
        'survived': int(mtd_by_period.loc[p, 'survived']),
        'total': int(mtd_by_period.loc[p, 'total']),
    } for p in ['P1', 'P2', 'P3'] if p in mtd_by_period.index},
    'chi2': round(chi2_mtd, 3),
    'p_value': round(p_mtd, 4),
}

results_store['composition'] = {
    'total_disability': len(disability),
    'dated': len(dated),
    'decided': len(decided),
    'pro_se_by_period': {p: round(prose_by_period.get(p, 0), 4) for p in ['P1', 'P2', 'P3']},
}

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(results_store, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"RESULTS SAVED TO {OUTPUT_PATH}")
print(f"{'='*70}")
