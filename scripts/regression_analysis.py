"""
FHA Disability Enforcement - Multivariate Regression Analysis (RA #9)
Logistic regression models for 3604 Database and RA Database
"""

import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.formula.api import logit
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. LOAD AND PREPARE DATA
# ============================================================

with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\FHA_3604_Database_unified_20260328_104352.json", "r", encoding="utf-8") as f:
    db3604_raw = json.load(f)

with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\FHA_RA_Database_unified_20260328_090852.json", "r", encoding="utf-8") as f:
    ra_raw = json.load(f)

print(f"3604 Database raw: {len(db3604_raw)} cases")
print(f"RA Database raw: {len(ra_raw)} cases")

def prepare_df(raw_data, label):
    df = pd.DataFrame(raw_data)

    # Filter: screening_result=YES
    df = df[df['screening_result'] == 'YES'].copy()
    print(f"{label} after screening_result=YES: {len(df)}")

    # Filter: exclude PROCEDURAL, SETTLEMENT, UNDETERMINED outcomes
    excluded = ['PROCEDURAL', 'SETTLEMENT', 'UNDETERMINED']
    df = df[~df['outcome'].isin(excluded)].copy()
    print(f"{label} after excluding procedural/settlement/undetermined: {len(df)}")

    # Show outcome distribution
    print(f"  Outcome distribution: {df['outcome'].value_counts().to_dict()}")
    print(f"  Year range: {df['year'].min()}-{df['year'].max()}")

    # Create binary variables
    df['post_loper_bright'] = (df['year'] >= 2024).astype(int)
    df['interactive_process_discussed_bin'] = (df['interactive_process_discussed'] == 'YES').astype(int)
    df['delay_as_denial_bin'] = (df['delay_as_denial'] == 'YES').astype(int)
    df['race_mentioned_bin'] = (df['race_mentioned'] == 'YES').astype(int)

    # DV: strict win (1=PLAINTIFF_WIN, 0=DEFENDANT_WIN or MIXED)
    df['strict_win'] = (df['outcome'] == 'PLAINTIFF_WIN').astype(int)

    # DV: broad win (1=PLAINTIFF_WIN or MIXED, 0=DEFENDANT_WIN)
    df['broad_win'] = (df['outcome'].isin(['PLAINTIFF_WIN', 'MIXED'])).astype(int)

    # Map procedural_posture to categories
    posture_map = {
        'MOTION_TO_DISMISS': 'MTD',
        'SUMMARY_JUDGMENT': 'SJ',
        'APPEAL': 'APPEAL',
        'ADMINISTRATIVE_REVIEW': 'OTHER',
        'TRIAL': 'OTHER',
        'BENCH_TRIAL': 'OTHER',
        'PRELIMINARY_INJUNCTION': 'OTHER',
        'POST_TRIAL': 'OTHER',
        'DEFAULT_JUDGMENT': 'OTHER',
        'REMAND': 'OTHER',
    }
    df['posture_cat'] = df['procedural_posture'].map(posture_map).fillna('OTHER')

    # Map defendant_type
    def_map = {
        'PRIVATE_LANDLORD': 'PRIVATE_LANDLORD',
        'HOUSING_AUTHORITY': 'HOUSING_AUTHORITY',
        'HOA_CONDO_ASSN': 'HOA_CONDO_ASSN',
        'HOA_CONDO_BOARD': 'HOA_CONDO_ASSN',
        'MUNICIPALITY': 'MUNICIPALITY',
        'PROPERTY_MANAGEMENT': 'PROPERTY_MANAGEMENT',
    }
    df['def_cat'] = df['defendant_type'].map(def_map).fillna('OTHER')

    # Map accommodation_type
    accom_map = {
        'DISCRIMINATION_PRIMARY': 'DISCRIMINATION_PRIMARY',
        'ASSISTANCE_ANIMAL': 'ASSISTANCE_ANIMAL',
        'EMOTIONAL_SUPPORT_ANIMAL': 'ASSISTANCE_ANIMAL',
        'SERVICE_ANIMAL': 'ASSISTANCE_ANIMAL',
        'SOBER_LIVING_GROUP_HOME_ZONING': 'SOBER_LIVING',
        'SOBER_LIVING': 'SOBER_LIVING',
        'GROUP_HOME_ZONING': 'SOBER_LIVING',
        'POLICY_EXCEPTION': 'POLICY_EXCEPTION',
        'PARKING_ACCOMMODATION': 'POLICY_EXCEPTION',
        'TRANSFER_REQUEST': 'POLICY_EXCEPTION',
        'STRUCTURAL_MODIFICATION': 'STRUCTURAL_MODIFICATION',
        'EVICTION_DEFENSE': 'OTHER',
        'UNDETERMINED': 'OTHER',
    }
    df['accom_cat'] = df['accommodation_type'].map(accom_map).fillna('OTHER')

    # Map plaintiff_type
    pl_map = {
        'INDIVIDUAL_TENANT': 'INDIVIDUAL_TENANT',
        'GROUP_HOME_OPERATOR': 'GROUP_HOME_OPERATOR',
        'FAIR_HOUSING_ORG': 'FAIR_HOUSING_ORG',
        'FAIR_HOUSING_ORGANIZATION': 'FAIR_HOUSING_ORG',
        'GOVERNMENT': 'GOVERNMENT',
        'DOJ': 'GOVERNMENT',
    }
    df['pl_cat'] = df['plaintiff_type'].map(pl_map).fillna('OTHER')

    print(f"  post_loper_bright: {df['post_loper_bright'].value_counts().to_dict()}")
    print(f"  posture_cat: {df['posture_cat'].value_counts().to_dict()}")
    print(f"  def_cat: {df['def_cat'].value_counts().to_dict()}")
    print(f"  accom_cat: {df['accom_cat'].value_counts().to_dict()}")
    print(f"  pl_cat: {df['pl_cat'].value_counts().to_dict()}")
    print(f"  interactive_process: {df['interactive_process_discussed_bin'].value_counts().to_dict()}")
    print(f"  delay_as_denial: {df['delay_as_denial_bin'].value_counts().to_dict()}")
    print(f"  race_mentioned: {df['race_mentioned_bin'].value_counts().to_dict()}")
    print()

    return df

print("=" * 70)
print("DATA PREPARATION")
print("=" * 70)
df3604 = prepare_df(db3604_raw, "3604 DB")
print()
dfra = prepare_df(ra_raw, "RA DB")

# ============================================================
# 2. HELPER: RUN AND FORMAT LOGISTIC REGRESSION
# ============================================================

def run_logit(df, dv, label, add_interactions=False):
    """Run logistic regression and return formatted results."""

    # Check minimum cell sizes - drop categories with <5 cases
    for col in ['posture_cat', 'def_cat', 'accom_cat', 'pl_cat']:
        counts = df[col].value_counts()
        small_cats = counts[counts < 5].index.tolist()
        if small_cats:
            df = df[~df[col].isin(small_cats)].copy()

    # Build formula
    base_vars = [
        'post_loper_bright',
        'C(posture_cat, Treatment(reference="MTD"))',
        'C(def_cat, Treatment(reference="PRIVATE_LANDLORD"))',
        'C(accom_cat, Treatment(reference="DISCRIMINATION_PRIMARY"))',
        'interactive_process_discussed_bin',
        'delay_as_denial_bin',
        'race_mentioned_bin',
        'C(pl_cat, Treatment(reference="INDIVIDUAL_TENANT"))',
    ]

    if add_interactions:
        base_vars.append('post_loper_bright:C(posture_cat, Treatment(reference="MTD"))')
        base_vars.append('post_loper_bright:interactive_process_discussed_bin')

    formula = f'{dv} ~ ' + ' + '.join(base_vars)

    # Check if DV has variation
    if df[dv].nunique() < 2:
        print(f"\n*** {label}: DV '{dv}' has no variation. Skipping. ***")
        return None

    try:
        model = logit(formula, data=df).fit(disp=0, maxiter=100, method='bfgs')
    except Exception as e:
        try:
            model = logit(formula, data=df).fit(disp=0, maxiter=200, method='newton')
        except Exception as e2:
            print(f"\n*** {label}: Model failed to converge: {e2} ***")
            return None

    print(f"\n{'=' * 80}")
    print(f"  {label}")
    print(f"{'=' * 80}")
    print(f"  N = {int(model.nobs)}")
    print(f"  Pseudo R-squared (McFadden) = {model.prsquared:.4f}")
    print(f"  AIC = {model.aic:.1f}")
    print(f"  Log-Likelihood = {model.llf:.1f}")
    print(f"  LLR p-value = {model.llr_pvalue:.4e}")

    # Build results table
    results = pd.DataFrame({
        'Coef': model.params,
        'SE': model.bse,
        'z': model.tvalues,
        'p': model.pvalues,
        'OR': np.exp(model.params),
        'CI_low': np.exp(model.conf_int()[0]),
        'CI_high': np.exp(model.conf_int()[1]),
    })

    # Clean up variable names for display
    name_map = {}
    for idx in results.index:
        clean = idx
        clean = clean.replace('C(posture_cat, Treatment(reference="MTD"))[T.', 'Posture: ').rstrip(']')
        clean = clean.replace('C(def_cat, Treatment(reference="PRIVATE_LANDLORD"))[T.', 'Defendant: ').rstrip(']')
        clean = clean.replace('C(accom_cat, Treatment(reference="DISCRIMINATION_PRIMARY"))[T.', 'Accommodation: ').rstrip(']')
        clean = clean.replace('C(pl_cat, Treatment(reference="INDIVIDUAL_TENANT"))[T.', 'Plaintiff: ').rstrip(']')
        clean = clean.replace('interactive_process_discussed_bin', 'Interactive Process')
        clean = clean.replace('delay_as_denial_bin', 'Delay as Denial')
        clean = clean.replace('race_mentioned_bin', 'Race Mentioned')
        clean = clean.replace('post_loper_bright', 'Post-Loper Bright')
        clean = clean.replace('Intercept', '(Intercept)')
        # Interaction terms
        clean = clean.replace('Post-Loper Bright:', 'Post-LB x ')
        name_map[idx] = clean

    results.index = [name_map.get(i, i) for i in results.index]

    # Format for display
    def sig_stars(p):
        if p < 0.001: return '***'
        if p < 0.01: return '**'
        if p < 0.05: return '*'
        if p < 0.1: return '+'
        return ''

    print(f"\n  {'Variable':<45} {'OR':>7} {'95% CI':>16} {'p':>8} {'Sig':>4}")
    print(f"  {'-'*45} {'-'*7} {'-'*16} {'-'*8} {'-'*4}")

    for idx, row in results.iterrows():
        ci_str = f"[{row['CI_low']:.3f}, {row['CI_high']:.3f}]"
        sig = sig_stars(row['p'])
        print(f"  {idx:<45} {row['OR']:>7.3f} {ci_str:>16} {row['p']:>8.4f} {sig:>4}")

    print(f"\n  Significance: *** p<0.001, ** p<0.01, * p<0.05, + p<0.10")

    return model, results


# ============================================================
# 3. RUN MODELS
# ============================================================

print("\n\n")
print("#" * 80)
print("#  MODEL 1: 3604 Database - Strict Win (PLAINTIFF_WIN vs. all else)")
print("#" * 80)
m1 = run_logit(df3604.copy(), 'strict_win', 'Model 1: 3604 DB - Strict Plaintiff Win')

print("\n\n")
print("#" * 80)
print("#  MODEL 2: 3604 Database - Broad Win (PLAINTIFF_WIN + MIXED vs. DEFENDANT_WIN)")
print("#" * 80)
m2 = run_logit(df3604.copy(), 'broad_win', 'Model 2: 3604 DB - Broad Plaintiff Win')

print("\n\n")
print("#" * 80)
print("#  MODEL 3: RA Database - Strict Win")
print("#" * 80)
m3 = run_logit(dfra.copy(), 'strict_win', 'Model 3: RA DB - Strict Plaintiff Win')

print("\n\n")
print("#" * 80)
print("#  MODEL 4: RA Database - Broad Win")
print("#" * 80)
m4 = run_logit(dfra.copy(), 'broad_win', 'Model 4: RA DB - Broad Plaintiff Win')

print("\n\n")
print("#" * 80)
print("#  MODEL 5: 3604 DB - Strict Win with Interaction Terms")
print("#" * 80)
m5 = run_logit(df3604.copy(), 'strict_win', 'Model 5: 3604 DB - Strict Win + Interactions', add_interactions=True)

print("\n\n")
print("#" * 80)
print("#  MODEL 6: 3604 DB - Broad Win with Interaction Terms")
print("#" * 80)
m6 = run_logit(df3604.copy(), 'broad_win', 'Model 6: 3604 DB - Broad Win + Interactions', add_interactions=True)

print("\n\n")
print("#" * 80)
print("#  MODEL 7: RA DB - Strict Win with Interaction Terms")
print("#" * 80)
m7 = run_logit(dfra.copy(), 'strict_win', 'Model 7: RA DB - Strict Win + Interactions', add_interactions=True)


# ============================================================
# 4. SUMMARY COMPARISON TABLE
# ============================================================

print("\n\n")
print("=" * 80)
print("  SUMMARY: POST-LOPER BRIGHT EFFECT ACROSS ALL MODELS")
print("=" * 80)
print(f"\n  {'Model':<50} {'OR':>7} {'p':>8} {'Sig':>4}")
print(f"  {'-'*50} {'-'*7} {'-'*8} {'-'*4}")

models_info = [
    ('M1: 3604 Strict Win', m1),
    ('M2: 3604 Broad Win', m2),
    ('M3: RA Strict Win', m3),
    ('M4: RA Broad Win', m4),
    ('M5: 3604 Strict + Interactions', m5),
    ('M6: 3604 Broad + Interactions', m6),
    ('M7: RA Strict + Interactions', m7),
]

for name, result in models_info:
    if result is None:
        print(f"  {name:<50} {'N/A':>7} {'N/A':>8} {'':>4}")
        continue
    model_obj, results_df = result
    # Find post_loper_bright row
    plb_rows = [r for r in results_df.index if 'Post-Loper Bright' in r and 'x' not in r and 'Post-LB' not in r]
    if plb_rows:
        row = results_df.loc[plb_rows[0]]
        sig = '***' if row['p'] < 0.001 else '**' if row['p'] < 0.01 else '*' if row['p'] < 0.05 else '+' if row['p'] < 0.1 else ''
        print(f"  {name:<50} {row['OR']:>7.3f} {row['p']:>8.4f} {sig:>4}")

print("\n")
print("=" * 80)
print("  SUMMARY: INTERACTIVE PROCESS EFFECT ACROSS ALL MODELS")
print("=" * 80)
print(f"\n  {'Model':<50} {'OR':>7} {'p':>8} {'Sig':>4}")
print(f"  {'-'*50} {'-'*7} {'-'*8} {'-'*4}")

for name, result in models_info:
    if result is None:
        print(f"  {name:<50} {'N/A':>7} {'N/A':>8} {'':>4}")
        continue
    model_obj, results_df = result
    ip_rows = [r for r in results_df.index if 'Interactive Process' in r and 'x' not in r and 'Post-LB' not in r]
    if ip_rows:
        row = results_df.loc[ip_rows[0]]
        sig = '***' if row['p'] < 0.001 else '**' if row['p'] < 0.01 else '*' if row['p'] < 0.05 else '+' if row['p'] < 0.1 else ''
        print(f"  {name:<50} {row['OR']:>7.3f} {row['p']:>8.4f} {sig:>4}")


# ============================================================
# 5. INTERACTION TERMS DETAIL
# ============================================================

print("\n\n")
print("=" * 80)
print("  INTERACTION TERMS DETAIL")
print("=" * 80)

for name, result in [('M5: 3604 Strict + Interactions', m5), ('M6: 3604 Broad + Interactions', m6), ('M7: RA Strict + Interactions', m7)]:
    if result is None:
        continue
    model_obj, results_df = result
    interaction_rows = [r for r in results_df.index if 'Post-LB x' in r]
    if interaction_rows:
        print(f"\n  {name}:")
        for idx in interaction_rows:
            row = results_df.loc[idx]
            sig = '***' if row['p'] < 0.001 else '**' if row['p'] < 0.01 else '*' if row['p'] < 0.05 else '+' if row['p'] < 0.1 else ''
            print(f"    {idx:<55} OR={row['OR']:.3f}  p={row['p']:.4f} {sig}")


# ============================================================
# 6. PUBLICATION-READY LATEX-STYLE TABLE
# ============================================================

print("\n\n")
print("=" * 80)
print("  PUBLICATION-READY REGRESSION TABLE")
print("=" * 80)

def format_cell(row):
    sig = '***' if row['p'] < 0.001 else '**' if row['p'] < 0.01 else '*' if row['p'] < 0.05 else '+' if row['p'] < 0.1 else ''
    return f"{row['OR']:.2f}{sig}"

def format_ci(row):
    return f"({row['CI_low']:.2f}-{row['CI_high']:.2f})"

# Collect all models for side-by-side
all_models = []
model_labels = []
for name, result in [('M1: 3604\nStrict', m1), ('M2: 3604\nBroad', m2), ('M3: RA\nStrict', m3), ('M4: RA\nBroad', m4)]:
    if result is not None:
        model_labels.append(name)
        all_models.append(result[1])

# Get union of all variables
all_vars = []
for res in all_models:
    for v in res.index:
        if v not in all_vars:
            all_vars.append(v)

print(f"\n  {'Variable':<45}", end='')
for lbl in model_labels:
    print(f"  {lbl.split(chr(10))[0]:>14}", end='')
print()
print(f"  {'':<45}", end='')
for lbl in model_labels:
    short = lbl.split('\n')[1] if '\n' in lbl else ''
    print(f"  {short:>14}", end='')
print()
print(f"  {'-'*45}", end='')
for _ in model_labels:
    print(f"  {'-'*14}", end='')
print()

for v in all_vars:
    if v == '(Intercept)':
        continue
    print(f"  {v:<45}", end='')
    for res in all_models:
        if v in res.index:
            row = res.loc[v]
            cell = format_cell(row)
            print(f"  {cell:>14}", end='')
        else:
            print(f"  {'--':>14}", end='')
    print()
    # CI row
    print(f"  {'':>45}", end='')
    for res in all_models:
        if v in res.index:
            row = res.loc[v]
            ci = format_ci(row)
            print(f"  {ci:>14}", end='')
        else:
            print(f"  {'':>14}", end='')
    print()

# Model fit statistics
print(f"  {'-'*45}", end='')
for _ in model_labels:
    print(f"  {'-'*14}", end='')
print()

print(f"  {'N':<45}", end='')
for name, result in [('', m1), ('', m2), ('', m3), ('', m4)]:
    if result is not None:
        print(f"  {int(result[0].nobs):>14}", end='')
print()

print(f"  {'Pseudo R-squared':<45}", end='')
for name, result in [('', m1), ('', m2), ('', m3), ('', m4)]:
    if result is not None:
        print(f"  {result[0].prsquared:>14.4f}", end='')
print()

print(f"  {'AIC':<45}", end='')
for name, result in [('', m1), ('', m2), ('', m3), ('', m4)]:
    if result is not None:
        print(f"  {result[0].aic:>14.1f}", end='')
print()

print(f"  {'LLR p-value':<45}", end='')
for name, result in [('', m1), ('', m2), ('', m3), ('', m4)]:
    if result is not None:
        p = result[0].llr_pvalue
        print(f"  {p:>14.4e}", end='')
print()

print(f"\n  Significance: *** p<0.001, ** p<0.01, * p<0.05, + p<0.10")
print(f"  Reference categories: Procedural posture=MTD, Defendant=Private Landlord,")
print(f"  Accommodation=Discrimination Primary, Plaintiff=Individual Tenant")
print(f"  Odds ratios reported with 95% confidence intervals in parentheses")
