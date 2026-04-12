"""
Administrative Enforcement Pipeline Analysis

Combines NFHA complaint data (2014-2024), Data.gov FHEO filed cases
(2000-2019), and the existing litigation corpus to document the
enforcement pipeline collapse.

Outputs: pipeline_results.json, MEMO_PIPELINE_ANALYSIS.md
"""
import json
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. ENCODE NFHA DATA (from 2025 Trends Report tables)
# ============================================================

# Table: Complaint Data by Agency, 2014-2024 (page 8)
NFHA_COMPLAINTS_BY_AGENCY = [
    {'year': 2014, 'fho': 19026, 'hud': 1710, 'fhap': 6758, 'doj': 34, 'total': 27528},
    {'year': 2015, 'fho': 19645, 'hud': 1274, 'fhap': 6972, 'doj': 46, 'total': 27937},
    {'year': 2016, 'fho': 19740, 'hud': 1371, 'fhap': 7030, 'doj': 40, 'total': 28181},
    {'year': 2017, 'fho': 20595, 'hud': 1311, 'fhap': 6896, 'doj': 41, 'total': 28825},
    {'year': 2018, 'fho': 23407, 'hud': 1784, 'fhap': 5987, 'doj': 24, 'total': 31202},
    {'year': 2019, 'fho': 21117, 'hud': 1771, 'fhap': 5953, 'doj': 39, 'total': 28880},
    {'year': 2020, 'fho': 21089, 'hud': 1697, 'fhap': 5883, 'doj': 43, 'total': 28712},
    {'year': 2021, 'fho': 22674, 'hud': 2093, 'fhap': 6413, 'doj': 36, 'total': 31216},
    {'year': 2022, 'fho': 24404, 'hud': 1915, 'fhap': 6652, 'doj': 36, 'total': 33007},
    {'year': 2023, 'fho': 25789, 'hud': 1742, 'fhap': 6577, 'doj': 42, 'total': 34150},
    {'year': 2024, 'fho': 23957, 'hud': 1566, 'fhap': 6754, 'doj': 44, 'total': 32321},
]

# Table: Complaint Data by Basis and Agency, 2024 (page 10)
NFHA_2024_BY_BASIS = {
    'disability': {'fho': 12275, 'hud': 1033, 'fhap': 4327, 'doj': 10, 'total': 17645, 'pct': 54.59},
    'race': {'fho': 3014, 'hud': 295, 'fhap': 1716, 'doj': 9, 'total': 5034, 'pct': 15.58},
    'sex': {'fho': 1246, 'hud': 223, 'fhap': 824, 'doj': 11, 'total': 2304, 'pct': 7.13},
    'national_origin': {'fho': 1167, 'hud': 104, 'fhap': 564, 'doj': 1, 'total': 1836, 'pct': 5.68},
    'familial_status': {'fho': 1164, 'hud': 125, 'fhap': 496, 'doj': 1, 'total': 1786, 'pct': 5.53},
    'color': {'fho': 381, 'hud': 39, 'fhap': 357, 'doj': 0, 'total': 777, 'pct': 2.40},
    'religion': {'fho': 171, 'hud': 28, 'fhap': 159, 'doj': 5, 'total': 363, 'pct': 1.12},
    'other': {'fho': 4539, 'hud': 208, 'fhap': 1140, 'doj': 7, 'total': 5894, 'pct': 18.24},
}

# Table: HUD Charged Cases by Year, 2014-2024 (page 16)
HUD_CHARGED_CASES = {
    2014: 27, 2015: 28, 2016: 37, 2017: 19, 2018: 28,
    2019: 37, 2020: 36, 2021: 36, 2022: 21, 2023: 47, 2024: 31,
}

# Table: 2024 HUD and FHAP Case Completion Types (page 16)
CASE_COMPLETIONS_2024 = {
    'administrative_closure': {'hud': 272, 'fhap': 829, 'total': 1101},
    'charged_or_caused': {'hud': 31, 'fhap': 440, 'total': 471},
    'conciliation_settlement': {'hud': 567, 'fhap': 1188, 'total': 1755},
    'doj_closure': {'hud': 4, 'fhap': 0, 'total': 4},
    'no_cause': {'hud': 584, 'fhap': 3724, 'total': 4308},
    'withdrawn_after_resolution': {'hud': 121, 'fhap': 428, 'total': 549},
    'total': {'hud': 1579, 'fhap': 6609, 'total': 8188},
}

# Additional context from report
NFHA_CONTEXT = {
    'fho_count_2024': 82,
    'fho_count_2023': 86,
    'fheo_funding_2024': 86_000_000,
    'fheo_funding_needed': 153_000_000,
    'fheo_funding_proposed_fy26': 68_000_000,
    'hud_aged_cases_2024': 1385,
    'hud_aged_cases_2023': 1357,
    'fhap_aged_cases_2024': 3526,
    'disability_complaint_share_2023': 52.61,
    'disability_complaint_share_2024': 54.59,
    'rental_complaints_share_2024': 83.56,
}

# Disability share of complaints for historical estimation
# 2023: 52.61%, 2024: 54.59%. Use these to estimate disability complaints for 2014-2022.
# NFHA reports from prior years show disability has been majority for over a decade.
# Conservative estimate: 50% for 2014-2017, 52% for 2018-2022.
DISABILITY_SHARE_ESTIMATES = {
    2014: 0.50, 2015: 0.50, 2016: 0.50, 2017: 0.50,
    2018: 0.52, 2019: 0.52, 2020: 0.52, 2021: 0.52, 2022: 0.52,
    2023: 0.5261, 2024: 0.5459,
}

print("=" * 70)
print("ADMINISTRATIVE ENFORCEMENT PIPELINE ANALYSIS")
print("=" * 70)

# ============================================================
# 2. PARSE DATA.GOV FHEO DATA (2000-2019)
# ============================================================

print("\n--- Loading Data.gov FHEO filed cases (2000-2019) ---")
try:
    df_gov = pd.read_excel('data/external/fha-cases-by-year.xls', header=None)
    # Find the header row (row 3 in 0-indexed = row 4 in the file)
    # Columns: Year, State, Filed, Race, ..., Disability, Familial Status, Religion, Sex, Retaliation,
    #          Charges, Admin Closures, Conciliations, Withdrawals, No Cause, DOJ, Post-Cause, ALJ, Elections, Appeals, Open

    # Parse the data rows (skip header rows)
    header_row = 3  # 0-indexed
    data_rows = []
    for idx in range(header_row + 1, len(df_gov)):
        row = df_gov.iloc[idx]
        year = row.iloc[0]
        state = row.iloc[1]
        if pd.isna(year) or pd.isna(state):
            continue
        try:
            year = int(year)
        except (ValueError, TypeError):
            continue

        data_rows.append({
            'year': year,
            'state': str(state),
            'filed': int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0,
            'race_basis': int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0,
            'disability_basis': int(row.iloc[17]) if pd.notna(row.iloc[17]) else 0,
            'familial_status_basis': int(row.iloc[18]) if pd.notna(row.iloc[18]) else 0,
            'religion_basis': int(row.iloc[19]) if pd.notna(row.iloc[19]) else 0,
            'sex_basis': int(row.iloc[20]) if pd.notna(row.iloc[20]) else 0,
            'national_origin_basis': int(row.iloc[15]) if pd.notna(row.iloc[15]) else 0,
            'retaliation_basis': int(row.iloc[21]) if pd.notna(row.iloc[21]) else 0,
            'charges': int(row.iloc[22]) if pd.notna(row.iloc[22]) else 0,
            'admin_closures': int(row.iloc[23]) if pd.notna(row.iloc[23]) else 0,
            'conciliations': int(row.iloc[24]) if pd.notna(row.iloc[24]) else 0,
            'withdrawals': int(row.iloc[25]) if pd.notna(row.iloc[25]) else 0,
            'no_cause': int(row.iloc[26]) if pd.notna(row.iloc[26]) else 0,
            'doj_closures': int(row.iloc[27]) if pd.notna(row.iloc[27]) else 0,
            'open_cases': int(row.iloc[32]) if pd.notna(row.iloc[32]) else 0,
        })

    df_fheo = pd.DataFrame(data_rows)

    # National totals by year
    totals = df_fheo[df_fheo['state'] == 'Total'].copy()
    states = df_fheo[df_fheo['state'] != 'Total'].copy()

    print(f"Loaded {len(data_rows)} rows ({len(totals)} year totals, {len(states)} state rows)")
    print(f"Years: {sorted(totals['year'].unique())}")

    # Disability share from FHEO data
    print("\nFHEO Disability cases by year (HUD/FHAP filed):")
    for _, row in totals.iterrows():
        yr = int(row['year'])
        filed = int(row['filed'])
        dis = int(row['disability_basis'])
        pct = dis / filed * 100 if filed > 0 else 0
        print(f"  {yr}: {dis}/{filed} = {pct:.1f}%")

except Exception as e:
    print(f"Error loading Data.gov: {e}")
    totals = pd.DataFrame()
    states = pd.DataFrame()

# ============================================================
# 3. LOAD LITIGATION CORPUS DATA
# ============================================================

print("\n--- Loading litigation corpus ---")
with open('data/2/FHA_Unified_Database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

disability_lit = [r for r in db if r.get('screening_result') == 'YES'
                  and (r.get('disability_alleged') or r.get('is_ra_case')
                       or 'disability' in (r.get('protected_classes') or []))]

# Litigation volume by year
lit_by_year = defaultdict(int)
for r in disability_lit:
    yr = r.get('year')
    if yr:
        lit_by_year[yr] += 1

print(f"Disability litigation cases: {len(disability_lit)}")
print("By year:", dict(sorted(lit_by_year.items())))

# Load H7 and H5 results
with open('h7_results.json', 'r', encoding='utf-8') as f:
    h7 = json.load(f)
with open('h5_results.json', 'r', encoding='utf-8') as f:
    h5 = json.load(f)

results = {}

# ============================================================
# ANALYSIS 1: THE ENFORCEMENT FUNNEL
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 1: THE ENFORCEMENT FUNNEL (2024)")
print("=" * 70)

disability_share = 0.5459
total_completions = CASE_COMPLETIONS_2024['total']['total']

funnel = {
    'disability_complaints_filed': 17645,
    'total_completions': total_completions,
    'est_disability_completions': round(total_completions * disability_share),
    'est_disability_no_cause': round(CASE_COMPLETIONS_2024['no_cause']['total'] * disability_share),
    'est_disability_charged': round(CASE_COMPLETIONS_2024['charged_or_caused']['total'] * disability_share),
    'est_disability_conciliated': round(CASE_COMPLETIONS_2024['conciliation_settlement']['total'] * disability_share),
    'est_disability_admin_closed': round(CASE_COMPLETIONS_2024['administrative_closure']['total'] * disability_share),
    'est_disability_withdrawn': round(CASE_COMPLETIONS_2024['withdrawn_after_resolution']['total'] * disability_share),
    'disability_share_assumption': disability_share,
    'note': 'Disability-specific completions estimated by applying 54.59% share to aggregate completions',
}

# Litigation volume for comparison
# Average ~200-300 disability cases/year in corpus for recent years
recent_lit = sum(lit_by_year.get(y, 0) for y in [2023, 2024, 2025])
recent_lit_avg = recent_lit / 3 if recent_lit > 0 else sum(lit_by_year.values()) / len(lit_by_year)

funnel['litigation_cases_per_year_avg'] = round(recent_lit_avg)
funnel['complaint_to_litigation_ratio'] = round(17645 / recent_lit_avg, 1) if recent_lit_avg > 0 else None
funnel['complaint_to_charge_ratio'] = round(17645 / funnel['est_disability_charged']) if funnel['est_disability_charged'] > 0 else None

print(f"\n  DISABILITY ENFORCEMENT FUNNEL (2024)")
print(f"  {'Stage':<45} {'N':>8}  {'Attrition':>10}")
print(f"  {'-'*65}")
print(f"  {'Disability complaints filed':<45} {funnel['disability_complaints_filed']:>8}")
print(f"  {'Est. administrative completions':<45} {funnel['est_disability_completions']:>8}  {(1 - funnel['est_disability_completions']/17645)*100:>9.1f}% lost")
print(f"  {'Est. no-cause determinations':<45} {funnel['est_disability_no_cause']:>8}  {funnel['est_disability_no_cause']/funnel['est_disability_completions']*100:>9.1f}% of compl")
print(f"  {'Est. charged/caused':<45} {funnel['est_disability_charged']:>8}  {funnel['est_disability_charged']/17645*100:>9.1f}% of filed")
print(f"  {'Est. conciliated/settled':<45} {funnel['est_disability_conciliated']:>8}")
print(f"  {'Disability cases in litigation (avg/yr)':<45} {funnel['litigation_cases_per_year_avg']:>8}  {funnel['litigation_cases_per_year_avg']/17645*100:>9.1f}% of filed")
print(f"\n  Complaint-to-litigation ratio: {funnel['complaint_to_litigation_ratio']}:1")
print(f"  Complaint-to-charge ratio: {funnel['complaint_to_charge_ratio']}:1")

results['funnel_2024'] = funnel

# ============================================================
# ANALYSIS 2: COMPLAINT VOLUME STABILITY vs LITIGATION DECLINE
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 2: COMPLAINT VOLUME vs LITIGATION QUALITY")
print("=" * 70)

# Estimated disability complaints 2014-2024
complaint_series = []
for row in NFHA_COMPLAINTS_BY_AGENCY:
    yr = row['year']
    share = DISABILITY_SHARE_ESTIMATES.get(yr, 0.52)
    est_disability = round(row['total'] * share)
    complaint_series.append({
        'year': yr,
        'total_complaints': row['total'],
        'est_disability_complaints': est_disability,
        'disability_share_used': share,
        'fho_share': round(row['fho'] / row['total'] * 100, 1),
        'hud_share': round(row['hud'] / row['total'] * 100, 1),
        'hud_charged': HUD_CHARGED_CASES.get(yr),
    })

print("\nYear  | Total Compl | Est Disab Compl | HUD Charged | Lit Cases | FHO Share")
print("-" * 85)
for c in complaint_series:
    lit = lit_by_year.get(c['year'], 0)
    charged = c['hud_charged'] or 0
    print(f"  {c['year']}  {c['total_complaints']:>11,}   {c['est_disability_complaints']:>15,}   {charged:>11}   {lit:>9}   {c['fho_share']:>8.1f}%")

# Key metric: complaint volume trend
complaints_2018 = next(c for c in complaint_series if c['year'] == 2018)['est_disability_complaints']
complaints_2024 = next(c for c in complaint_series if c['year'] == 2024)['est_disability_complaints']
complaint_change = (complaints_2024 - complaints_2018) / complaints_2018 * 100

print(f"\nDisability complaint volume change 2018-2024: {complaint_change:+.1f}%")
print(f"Litigation quality change (broad win rate): P1=30.0% -> P3=18.9% ({-37.0:.1f}%)")
print(f"Pro se share change: P1=53.0% -> P3=71.4% ({+34.7:.1f}%)")

results['complaint_vs_litigation'] = {
    'series': complaint_series,
    'disability_complaint_change_2018_2024_pct': round(complaint_change, 1),
    'litigation_broad_win_p1': 30.0,
    'litigation_broad_win_p3': 18.9,
    'pro_se_share_p1': 53.0,
    'pro_se_share_p3': 71.4,
    'diagnosis': 'Complaint volume stable/growing while litigation quality declining. Pipeline failure, not violation decline.',
}

# ============================================================
# ANALYSIS 3: FHO PROCESSING SHARE x INSTITUTIONAL DECLINE
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 3: FHO PROCESSING SHARE x INSTITUTIONAL PLAINTIFF DECLINE")
print("=" * 70)

fho_data = {
    'fho_share_of_complaints_2024': 74.12,
    'hud_share_of_complaints_2024': 4.85,
    'fhap_share_of_complaints_2024': 20.90,
    'fho_count_2024': 82,
    'fho_count_2023': 86,
    'fho_decline': -4,
    'fho_decline_pct': round(-4 / 86 * 100, 1),
    'institutional_plaintiff_share_p1': 16.9,
    'institutional_plaintiff_share_p2': 14.9,
    'institutional_plaintiff_share_p3': 12.1,
    'institutional_plaintiff_decline_p1_to_p3': round(12.1 - 16.9, 1),
}

print(f"\n  Who processes complaints (2024):")
print(f"    FHOs:  {fho_data['fho_share_of_complaints_2024']}% of all complaints ({fho_data['fho_count_2024']} organizations)")
print(f"    FHAP:  {fho_data['fhap_share_of_complaints_2024']}%")
print(f"    HUD:   {fho_data['hud_share_of_complaints_2024']}%")
print(f"\n  FHO organizational decline: {fho_data['fho_count_2023']} -> {fho_data['fho_count_2024']} ({fho_data['fho_decline_pct']}%)")
print(f"  NFHA notes: 'several agencies were not able to submit their information' due to Feb 2025 funding cuts")
print(f"\n  Institutional plaintiffs in litigation:")
print(f"    P1: {fho_data['institutional_plaintiff_share_p1']}%")
print(f"    P2: {fho_data['institutional_plaintiff_share_p2']}%")
print(f"    P3: {fho_data['institutional_plaintiff_share_p3']}%")
print(f"    Decline: {fho_data['institutional_plaintiff_decline_p1_to_p3']} percentage points")
print(f"\n  The organizations processing 74% of complaints are the same organizations")
print(f"  whose presence in litigation is declining. As FHOs close, both complaint")
print(f"  processing AND litigation quality degrade simultaneously.")

results['fho_institutional'] = fho_data

# ============================================================
# ANALYSIS 4: HUD CAUSE-FINDING COLLAPSE
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 4: HUD CAUSE-FINDING COLLAPSE")
print("=" * 70)

charged_series = sorted(HUD_CHARGED_CASES.items())
avg_2014_2020 = np.mean([v for y, v in charged_series if 2014 <= y <= 2020])
avg_2021_2024 = np.mean([v for y, v in charged_series if 2021 <= y <= 2024])

print(f"\n  HUD Charged Cases by Year:")
for yr, n in charged_series:
    bar = '#' * n
    print(f"    {yr}: {n:>3}  {bar}")

print(f"\n  Average 2014-2020: {avg_2014_2020:.1f}")
print(f"  Average 2021-2024: {avg_2021_2024:.1f}")
print(f"  2023->2024 change: {HUD_CHARGED_CASES[2024] - HUD_CHARGED_CASES[2023]:+d} ({(HUD_CHARGED_CASES[2024]/HUD_CHARGED_CASES[2023]-1)*100:+.1f}%)")

# Charge rate: charges per complaint
print(f"\n  HUD charge rate (charges / HUD complaints):")
for row in NFHA_COMPLAINTS_BY_AGENCY:
    yr = row['year']
    charges = HUD_CHARGED_CASES.get(yr, 0)
    rate = charges / row['hud'] * 100 if row['hud'] > 0 else 0
    print(f"    {yr}: {charges}/{row['hud']} = {rate:.1f}%")

# FHEO funding gap
print(f"\n  FHEO Funding:")
print(f"    2024 actual:     ${NFHA_CONTEXT['fheo_funding_2024']:>13,}  ({NFHA_CONTEXT['fheo_funding_2024']/NFHA_CONTEXT['fheo_funding_needed']*100:.0f}% of needed)")
print(f"    Full staffing:   ${NFHA_CONTEXT['fheo_funding_needed']:>13,}")
print(f"    FY26 proposed:   ${NFHA_CONTEXT['fheo_funding_proposed_fy26']:>13,}  ({NFHA_CONTEXT['fheo_funding_proposed_fy26']/NFHA_CONTEXT['fheo_funding_needed']*100:.0f}% of needed)")

results['cause_finding'] = {
    'charged_by_year': HUD_CHARGED_CASES,
    'avg_2014_2020': round(avg_2014_2020, 1),
    'avg_2021_2024': round(avg_2021_2024, 1),
    'change_2023_2024': HUD_CHARGED_CASES[2024] - HUD_CHARGED_CASES[2023],
    'change_2023_2024_pct': round((HUD_CHARGED_CASES[2024] / HUD_CHARGED_CASES[2023] - 1) * 100, 1),
    'fheo_funding_2024': NFHA_CONTEXT['fheo_funding_2024'],
    'fheo_funding_needed': NFHA_CONTEXT['fheo_funding_needed'],
    'fheo_funding_gap_pct': round((1 - NFHA_CONTEXT['fheo_funding_2024'] / NFHA_CONTEXT['fheo_funding_needed']) * 100, 1),
}

# ============================================================
# ANALYSIS 5: GEOGRAPHIC ENFORCEMENT (Data.gov baseline)
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 5: GEOGRAPHIC ENFORCEMENT BASELINE (2015-2019)")
print("=" * 70)

if len(states) > 0:
    # Aggregate 2015-2019 by state
    recent_states = states[(states['year'] >= 2015) & (states['year'] <= 2019)].copy()
    state_agg = recent_states.groupby('state').agg({
        'filed': 'sum',
        'disability_basis': 'sum',
        'charges': 'sum',
        'no_cause': 'sum',
        'conciliations': 'sum',
        'admin_closures': 'sum',
    }).reset_index()

    state_agg['disability_share'] = (state_agg['disability_basis'] / state_agg['filed'] * 100).round(1)
    state_agg['charge_rate'] = (state_agg['charges'] / state_agg['filed'] * 100).round(1)
    state_agg['no_cause_rate'] = (state_agg['no_cause'] / state_agg['filed'] * 100).round(1)

    # Top states by filing volume
    top_states = state_agg.nlargest(15, 'filed')
    print(f"\nTop 15 states by FHEO filed cases (2015-2019 aggregate):")
    print(f"  {'State':<20} {'Filed':>7} {'Disab':>7} {'Dis%':>6} {'Charges':>8} {'Chg%':>6} {'NoCause%':>9}")
    print(f"  {'-'*65}")
    for _, row in top_states.iterrows():
        print(f"  {row['state']:<20} {int(row['filed']):>7} {int(row['disability_basis']):>7} "
              f"{row['disability_share']:>5.1f}% {int(row['charges']):>8} {row['charge_rate']:>5.1f}% {row['no_cause_rate']:>8.1f}%")

    # Compare against litigation corpus geography
    lit_by_state = defaultdict(int)
    for r in disability_lit:
        st = r.get('property_state', '')
        if st:
            lit_by_state[st] += 1

    # Match FHEO states to litigation states
    print(f"\n  Complaint volume vs litigation presence (top states):")
    print(f"  {'State':<20} {'FHEO Filed':>11} {'Lit Cases':>10} {'Ratio':>8}")
    print(f"  {'-'*55}")
    for _, row in top_states.iterrows():
        st_name = row['state']
        # Try to match state names to abbreviations
        lit_n = lit_by_state.get(st_name, 0)
        if lit_n == 0:
            # State name -> abbreviation mapping for common states
            abbrevs = {
                'California': 'CA', 'Texas': 'TX', 'Florida': 'FL', 'New York': 'NY',
                'Illinois': 'IL', 'Ohio': 'OH', 'Pennsylvania': 'PA', 'Michigan': 'MI',
                'Georgia': 'GA', 'Virginia': 'VA', 'North Carolina': 'NC', 'New Jersey': 'NJ',
                'Maryland': 'MD', 'Washington': 'WA', 'Minnesota': 'MN', 'Colorado': 'CO',
                'Arizona': 'AZ', 'Massachusetts': 'MA', 'Indiana': 'IN', 'Tennessee': 'TN',
                'Missouri': 'MO', 'Connecticut': 'CT', 'Oregon': 'OR', 'Wisconsin': 'WI',
                'Louisiana': 'LA', 'South Carolina': 'SC', 'Alabama': 'AL', 'Kentucky': 'KY',
                'Nevada': 'NV', 'Oklahoma': 'OK', 'Iowa': 'IA', 'Mississippi': 'MS',
            }
            abbr = abbrevs.get(st_name, '')
            lit_n = lit_by_state.get(abbr, 0)

        ratio = int(row['filed']) / lit_n if lit_n > 0 else float('inf')
        ratio_str = f"{ratio:.0f}:1" if ratio != float('inf') else "no lit"
        print(f"  {st_name:<20} {int(row['filed']):>11} {lit_n:>10} {ratio_str:>8}")

    results['geographic'] = {
        'top_states': top_states[['state', 'filed', 'disability_basis', 'disability_share',
                                   'charge_rate', 'no_cause_rate']].to_dict('records'),
    }

# ============================================================
# ANALYSIS 6: FHEO HISTORICAL TRENDS (2000-2019)
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS 6: FHEO HISTORICAL TRENDS (2000-2019)")
print("=" * 70)

if len(totals) > 0:
    print(f"\n  FHEO Filed Cases (national totals):")
    print(f"  {'Year':>6} {'Filed':>7} {'Disab':>7} {'Dis%':>6} {'Charges':>8} {'NoCause':>8} {'Concil':>7}")
    for _, row in totals.sort_values('year').iterrows():
        yr = int(row['year'])
        filed = int(row['filed'])
        dis = int(row['disability_basis'])
        pct = dis / filed * 100 if filed > 0 else 0
        charges = int(row['charges'])
        nc = int(row['no_cause'])
        conc = int(row['conciliations'])
        print(f"  {yr:>6} {filed:>7} {dis:>7} {pct:>5.1f}% {charges:>8} {nc:>8} {conc:>7}")

    # Disability share trend
    dis_trend = []
    for _, row in totals.sort_values('year').iterrows():
        yr = int(row['year'])
        filed = int(row['filed'])
        dis = int(row['disability_basis'])
        dis_trend.append({'year': yr, 'filed': filed, 'disability': dis,
                          'pct': round(dis / filed * 100, 1) if filed > 0 else 0})

    results['fheo_historical'] = dis_trend

# ============================================================
# SAVE RESULTS
# ============================================================

with open('pipeline_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False, default=str)

print(f"\n{'='*70}")
print(f"RESULTS SAVED TO pipeline_results.json")
print(f"{'='*70}")
