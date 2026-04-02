"""
Recompute all note v40 litigation statistics on the FHA Unified Database,
filtered to disability cases only (disability in protected_classes).

Single database, no subsets. Three periods:
  P1: 2022-01-01 to 2024-06-28  (Pre-Loper Bright)
  P2: 2024-06-28 to 2025-02-05  (Post-LB / Pre-HUD Secretary)
  P3: 2025-02-05 to present     (Post-HUD Secretary)

Usage:
  python recompute_stats_unified.py
"""

import json
import os
import sys
import math
from collections import Counter, defaultdict
from datetime import datetime
from config import UNIFIED_DB_PATH, RESULTS_DIR

sys.stdout.reconfigure(encoding='utf-8')

UNIFIED_DB = UNIFIED_DB_PATH
STATS_OUTPUT = os.path.join(RESULTS_DIR, 'unified_stats.json')
REPORT_OUTPUT = os.path.join(RESULTS_DIR, 'unified_stats_report.md')

P1_START = '2022-01-01'
P1_END   = '2024-06-28'
P2_END   = '2025-02-05'

DECIDED = {'PLAINTIFF_WIN', 'DEFENDANT_WIN', 'MIXED'}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def has_disability(rec):
    return 'disability' in [p.lower() for p in (rec.get('protected_classes') or [])]


def assign_period(rec):
    d = rec.get('date_filed')
    if not d or d < P1_START:
        return None
    if d < P1_END:
        return 'P1'
    if d < P2_END:
        return 'P2'
    return 'P3'


def assign_old_era(rec):
    y = rec.get('year')
    if y is None:
        return None
    return 'pre' if y <= 2023 else 'post'


def win_rates(cases):
    decided = [r for r in cases if r.get('outcome') in DECIDED]
    n = len(decided)
    if n == 0:
        return {'n_decided': 0, 'strict_pct': None, 'broad_pct': None,
                'pw': 0, 'dw': 0, 'mixed': 0}
    pw = sum(1 for r in decided if r['outcome'] == 'PLAINTIFF_WIN')
    dw = sum(1 for r in decided if r['outcome'] == 'DEFENDANT_WIN')
    mx = sum(1 for r in decided if r['outcome'] == 'MIXED')
    return {
        'n_decided': n, 'pw': pw, 'dw': dw, 'mixed': mx,
        'strict_pct': round(100 * pw / n, 1),
        'broad_pct': round(100 * (pw + mx) / n, 1),
    }


def chi2_test(n1_pw, n1_total, n2_pw, n2_total):
    if n1_total == 0 or n2_total == 0:
        return None, None
    a, b = n1_pw, n1_total - n1_pw
    c, d = n2_pw, n2_total - n2_pw
    n = a + b + c + d
    if n == 0:
        return None, None
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    cells = [(a, row1*col1/n), (b, row1*col2/n), (c, row2*col1/n), (d, row2*col2/n)]
    chi2 = sum((obs - exp)**2 / exp if exp > 0 else 0 for obs, exp in cells)
    p = math.erfc(math.sqrt(chi2) / math.sqrt(2)) if chi2 > 0 else 1.0
    return round(chi2, 2), round(p, 6)


def pct(num, denom):
    return round(100 * num / denom, 1) if denom else None


def group_by(cases, field):
    groups = defaultdict(list)
    for r in cases:
        v = r.get(field)
        if v:
            groups[v].append(r)
    return dict(groups)


def main():
    db = load_json(UNIFIED_DB)

    # All screened-in
    all_screened = [r for r in db if r.get('screening_result', '') != 'NO' and r.get('case_name')]
    # Disability filter
    disab = [r for r in all_screened if has_disability(r)]

    for r in disab:
        r['_period'] = assign_period(r)
        r['_old_era'] = assign_old_era(r)

    dated = [r for r in disab if r['_period'] is not None]
    p1 = [r for r in dated if r['_period'] == 'P1']
    p2 = [r for r in dated if r['_period'] == 'P2']
    p3 = [r for r in dated if r['_period'] == 'P3']

    old_pre = [r for r in disab if r['_old_era'] == 'pre']
    old_post = [r for r in disab if r['_old_era'] == 'post']

    stats = {}
    lines = []

    def section(title):
        lines.append(f"\n## {title}\n")

    def th(cols):
        lines.append('| ' + ' | '.join(cols) + ' |')
        lines.append('|' + '|'.join(['---'] * len(cols)) + '|')

    def tr(vals):
        lines.append('| ' + ' | '.join(str(v) for v in vals) + ' |')

    print(f"All screened-in: {len(all_screened)}")
    print(f"Disability cases: {len(disab)} ({100*len(disab)/len(all_screened):.1f}%)")
    print(f"Dated disability: {len(dated)}")
    print(f"  P1: {len(p1)}, P2: {len(p2)}, P3: {len(p3)}")

    # ============================================================
    # A. DATABASE COMPOSITION
    # ============================================================
    section("A. Database Composition")

    lines.append(f"Total screened-in FHA cases: {len(all_screened)}")
    lines.append(f"Disability cases: {len(disab)} ({100*len(disab)/len(all_screened):.1f}%)")
    lines.append(f"Dated disability cases: {len(dated)}")
    lines.append(f"Undated disability cases: {len(disab) - len(dated)}")
    lines.append("")

    th(['Period', 'Total', 'Decided'])
    for label, cases in [('P1', p1), ('P2', p2), ('P3', p3), ('All dated', dated)]:
        dec = len([r for r in cases if r.get('outcome') in DECIDED])
        tr([label, len(cases), dec])

    stats['composition'] = {
        'all_screened': len(all_screened), 'disability': len(disab),
        'dated': len(dated), 'P1': len(p1), 'P2': len(p2), 'P3': len(p3),
        'P1_decided': len([r for r in p1 if r.get('outcome') in DECIDED]),
        'P2_decided': len([r for r in p2 if r.get('outcome') in DECIDED]),
        'P3_decided': len([r for r in p3 if r.get('outcome') in DECIDED]),
    }

    # ============================================================
    # B. OVERALL WIN RATES
    # ============================================================
    section("B. Overall Win Rates")

    th(['Period', 'N decided', 'PW', 'DW', 'MIXED', 'Strict %', 'Broad %'])
    wr_stats = {}
    for label, cases in [('P1', p1), ('P2', p2), ('P3', p3), ('P2+P3', p2+p3), ('All', dated)]:
        wr = win_rates(cases)
        wr_stats[label] = wr
        tr([label, wr['n_decided'], wr['pw'], wr['dw'], wr['mixed'],
            wr['strict_pct'], wr['broad_pct']])

    lines.append(f"\nOld binary split (validation):")
    th(['Era', 'N decided', 'PW', 'DW', 'MIXED', 'Strict %', 'Broad %'])
    for label, cases in [('pre (<=2023)', old_pre), ('post (>=2024)', old_post)]:
        wr = win_rates(cases)
        wr_stats[label] = wr
        tr([label, wr['n_decided'], wr['pw'], wr['dw'], wr['mixed'],
            wr['strict_pct'], wr['broad_pct']])

    # Chi-squared
    lines.append(f"\nChi-squared tests (strict):")
    for a, b in [('P1','P2'), ('P1','P3'), ('P2','P3'), ('P1','P2+P3')]:
        wa, wb = wr_stats[a], wr_stats[b]
        if wa['n_decided'] and wb['n_decided']:
            c2, p = chi2_test(wa['pw'], wa['n_decided'], wb['pw'], wb['n_decided'])
            lines.append(f"  {a} vs {b}: chi2={c2}, p={p}")

    lines.append(f"\nChi-squared tests (broad):")
    for a, b in [('P1','P2'), ('P1','P3'), ('P2','P3'), ('P1','P2+P3')]:
        wa, wb = wr_stats[a], wr_stats[b]
        if wa['n_decided'] and wb['n_decided']:
            c2, p = chi2_test(wa['pw']+wa['mixed'], wa['n_decided'],
                              wb['pw']+wb['mixed'], wb['n_decided'])
            lines.append(f"  {a} vs {b}: chi2={c2}, p={p}")

    stats['win_rates'] = wr_stats

    # ============================================================
    # C. YEAR-BY-YEAR
    # ============================================================
    section("C. Year-by-Year Win Rates")

    th(['Year', 'N decided', 'Strict %', 'Broad %'])
    by_year = group_by(disab, 'year')
    yby = {}
    for y in sorted(by_year.keys()):
        if y and 2018 <= y <= 2026:
            wr = win_rates(by_year[y])
            yby[str(y)] = wr
            tr([y, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])
    stats['year_by_year'] = yby

    # ============================================================
    # D. PLAINTIFF TYPE
    # ============================================================
    section("D. Plaintiff Type Win Rates")

    pt_order = ['INDIVIDUAL_TENANT', 'GOVERNMENT', 'FAIR_HOUSING_ORG', 'GROUP_HOME_OPERATOR', 'OTHER']

    lines.append("**Overall (dated):**")
    th(['Plaintiff Type', 'N decided', 'Strict %', 'Broad %'])
    pt_groups = group_by(dated, 'plaintiff_type')
    pt_stats = {}
    for pt in pt_order:
        wr = win_rates(pt_groups.get(pt, []))
        pt_stats[pt] = wr
        tr([pt, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])

    for plabel, pcases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        lines.append(f"\n**{plabel}:**")
        th(['Plaintiff Type', 'N decided', 'Strict %', 'Broad %'])
        g = group_by(pcases, 'plaintiff_type')
        for pt in pt_order:
            wr = win_rates(g.get(pt, []))
            pt_stats[f'{pt}_{plabel}'] = wr
            if wr['n_decided'] > 0:
                tr([pt, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])
    stats['plaintiff_type'] = pt_stats

    # ============================================================
    # E. DEFENDANT TYPE
    # ============================================================
    section("E. Defendant Type Win Rates")

    dt_order = ['DEVELOPER', 'HOA_CONDO_ASSN', 'PRIVATE_LANDLORD', 'MUNICIPALITY',
                'PROPERTY_MANAGEMENT', 'OTHER', 'HOUSING_AUTHORITY', 'GOVERNMENT']

    lines.append("**Overall (dated):**")
    th(['Defendant Type', 'N decided', 'Strict %', 'Broad %'])
    dt_groups = group_by(dated, 'defendant_type')
    dt_stats = {}
    for dt in dt_order:
        wr = win_rates(dt_groups.get(dt, []))
        dt_stats[dt] = wr
        tr([dt, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])

    # Full DB validation
    lines.append(f"\nValidation (full disability DB including undated):")
    th(['Defendant Type', 'N decided', 'Strict %', 'Broad %'])
    dt_all = group_by(disab, 'defendant_type')
    for dt in dt_order:
        wr = win_rates(dt_all.get(dt, []))
        dt_stats[f'{dt}_full'] = wr
        tr([dt, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])

    for plabel, pcases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        lines.append(f"\n**{plabel}:**")
        th(['Defendant Type', 'N decided', 'Strict %', 'Broad %'])
        g = group_by(pcases, 'defendant_type')
        for dt in dt_order:
            wr = win_rates(g.get(dt, []))
            dt_stats[f'{dt}_{plabel}'] = wr
            if wr['n_decided'] > 0:
                tr([dt, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])
    stats['defendant_type'] = dt_stats

    # ============================================================
    # F. PRO SE
    # ============================================================
    section("F. Pro Se Analysis")

    known = [r for r in dated if r.get('pro_se') is not None]
    ps = [r for r in known if r['pro_se'] is True]
    rep = [r for r in known if r['pro_se'] is False]

    ps_stats = {
        'overall': {
            'known': len(known), 'pro_se': len(ps),
            'pro_se_pct': pct(len(ps), len(known)),
            'pro_se_win': win_rates(ps), 'rep_win': win_rates(rep),
        }
    }

    th(['Metric', 'Value'])
    tr(['Known status (dated disability)', len(known)])
    tr(['Pro se count', len(ps)])
    tr(['Pro se %', ps_stats['overall']['pro_se_pct']])
    tr(['Pro se strict %', ps_stats['overall']['pro_se_win']['strict_pct']])
    tr(['Represented strict %', ps_stats['overall']['rep_win']['strict_pct']])
    tr(['Pro se broad %', ps_stats['overall']['pro_se_win']['broad_pct']])
    tr(['Represented broad %', ps_stats['overall']['rep_win']['broad_pct']])

    lines.append(f"\nBy period:")
    th(['Period', 'Pro Se %', 'N pro se', 'N rep', 'PS Strict %', 'Rep Strict %', 'PS Broad %', 'Rep Broad %'])
    for plabel, pcases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        ks = [r for r in pcases if r.get('pro_se') is not None]
        pse = [r for r in ks if r['pro_se'] is True]
        rp = [r for r in ks if r['pro_se'] is False]
        pw_ps, pw_rp = win_rates(pse), win_rates(rp)
        ps_stats[plabel] = {
            'pro_se_pct': pct(len(pse), len(ks)),
            'n_ps': len(pse), 'n_rep': len(rp),
            'ps_win': pw_ps, 'rep_win': pw_rp,
        }
        tr([plabel, pct(len(pse), len(ks)), len(pse), len(rp),
            pw_ps['strict_pct'], pw_rp['strict_pct'],
            pw_ps['broad_pct'], pw_rp['broad_pct']])

    # Validation vs full disability DB
    lines.append(f"\nValidation (full disability DB):")
    ks_all = [r for r in disab if r.get('pro_se') is not None]
    ps_all = [r for r in ks_all if r['pro_se'] is True]
    rp_all = [r for r in ks_all if r['pro_se'] is False]
    lines.append(f"  Pro se: {len(ps_all)}/{len(ks_all)} = {pct(len(ps_all), len(ks_all))}%")
    lines.append(f"  Pro se strict: {win_rates(ps_all)['strict_pct']}% (n={win_rates(ps_all)['n_decided']})")
    lines.append(f"  Represented strict: {win_rates(rp_all)['strict_pct']}% (n={win_rates(rp_all)['n_decided']})")

    # Pro se x defendant type
    lines.append(f"\nPro se x defendant type (disability, decided):")
    dec_known = [r for r in disab if r.get('outcome') in DECIDED and r.get('pro_se') is not None]
    th(['Defendant Type', 'PS Strict %', 'PS N', 'Rep Strict %', 'Rep N'])
    for dt in ['PROPERTY_MANAGEMENT', 'HOA_CONDO_ASSN', 'PRIVATE_LANDLORD', 'HOUSING_AUTHORITY', 'MUNICIPALITY']:
        ps_dt = [r for r in dec_known if r['pro_se'] is True and r.get('defendant_type') == dt]
        rp_dt = [r for r in dec_known if r['pro_se'] is False and r.get('defendant_type') == dt]
        ps_pw = sum(1 for r in ps_dt if r['outcome'] == 'PLAINTIFF_WIN')
        rp_pw = sum(1 for r in rp_dt if r['outcome'] == 'PLAINTIFF_WIN')
        tr([dt,
            f"{pct(ps_pw, len(ps_dt))}% ({ps_pw}/{len(ps_dt)})" if ps_dt else 'N/A', len(ps_dt),
            f"{pct(rp_pw, len(rp_dt))}% ({rp_pw}/{len(rp_dt)})" if rp_dt else 'N/A', len(rp_dt)])
    stats['pro_se'] = ps_stats

    # ============================================================
    # G. MTD GATEKEEPING
    # ============================================================
    section("G. MTD Gatekeeping")

    mtd_stats = {}
    lines.append("**MTD share and survival:**")
    th(['Period', 'Decided', 'MTD Decided', 'MTD Share %', 'MTD Strict %', 'MTD Broad %'])
    for label, cases in [('All', dated), ('P1', p1), ('P2', p2), ('P3', p3)]:
        dec = [r for r in cases if r.get('outcome') in DECIDED]
        mtd = [r for r in dec if r.get('procedural_posture') == 'MOTION_TO_DISMISS']
        mwr = win_rates(mtd)
        mtd_stats[label] = {
            'n_decided': len(dec), 'n_mtd': len(mtd),
            'mtd_share': pct(len(mtd), len(dec)),
            'mtd_strict': mwr['strict_pct'], 'mtd_broad': mwr['broad_pct'],
        }
        tr([label, len(dec), len(mtd), pct(len(mtd), len(dec)),
            mwr['strict_pct'], mwr['broad_pct']])

    # Old split
    lines.append(f"\nOld split validation:")
    th(['Era', 'MTD N', 'MTD Strict %', 'MTD Broad %'])
    for label, cases in [('pre', old_pre), ('post', old_post)]:
        mtd = [r for r in cases if r.get('outcome') in DECIDED
               and r.get('procedural_posture') == 'MOTION_TO_DISMISS']
        wr = win_rates(mtd)
        tr([label, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])

    # MTD by accommodation type
    lines.append(f"\n**MTD by accommodation type (all disability):**")
    mtd_all = [r for r in disab if r.get('outcome') in DECIDED
               and r.get('procedural_posture') == 'MOTION_TO_DISMISS']
    accom_g = group_by(mtd_all, 'accommodation_type')
    accom_order = ['PARKING', 'ASSISTANCE_ANIMAL', 'SOBER_LIVING_GROUP_HOME_ZONING',
                   'COMMUNICATION_ACCOMMODATION', 'EVICTION_DEFENSE', 'POLICY_EXCEPTION',
                   'STRUCTURAL_MODIFICATION', 'DISCRIMINATION_PRIMARY', 'TRANSFER']
    th(['Accommodation Type', 'N', 'Broad %'])
    for at in accom_order:
        wr = win_rates(accom_g.get(at, []))
        mtd_stats[f'accom_{at}'] = wr
        if wr['n_decided'] >= 5:
            tr([at, wr['n_decided'], wr['broad_pct']])

    # MTD by circuit
    lines.append(f"\n**MTD by circuit (all disability, n>=20):**")
    circ_g = group_by(mtd_all, 'circuit')
    circ_order = ['1st Circuit','2nd Circuit','3rd Circuit','4th Circuit','5th Circuit',
                  '6th Circuit','7th Circuit','8th Circuit','9th Circuit','10th Circuit',
                  '11th Circuit','D.C. Circuit']
    th(['Circuit', 'N', 'Broad %'])
    for c in circ_order:
        wr = win_rates(circ_g.get(c, []))
        if wr['n_decided'] >= 20:
            mtd_stats[f'circuit_{c}'] = wr
            tr([c, wr['n_decided'], wr['broad_pct']])

    # Circuit pre/post
    lines.append(f"\n**Circuit MTD P1 vs P2+P3 (n>=10 both):**")
    mtd_p1 = [r for r in p1 if r.get('outcome') in DECIDED and r.get('procedural_posture') == 'MOTION_TO_DISMISS']
    mtd_p23 = [r for r in p2+p3 if r.get('outcome') in DECIDED and r.get('procedural_posture') == 'MOTION_TO_DISMISS']
    th(['Circuit', 'P1 N', 'P1 Broad %', 'P2+P3 N', 'P2+P3 Broad %', 'Delta pp'])
    for c in circ_order:
        pre_c = [r for r in mtd_p1 if r.get('circuit') == c]
        post_c = [r for r in mtd_p23 if r.get('circuit') == c]
        pwr, qwr = win_rates(pre_c), win_rates(post_c)
        if pwr['n_decided'] >= 10 and qwr['n_decided'] >= 10:
            delta = round(qwr['broad_pct'] - pwr['broad_pct'], 1) if pwr['broad_pct'] is not None and qwr['broad_pct'] is not None else None
            tr([c, pwr['n_decided'], pwr['broad_pct'], qwr['n_decided'], qwr['broad_pct'], delta])
    stats['mtd'] = mtd_stats

    # ============================================================
    # H. INTERACTIVE PROCESS
    # ============================================================
    section("H. Interactive Process")

    ip_stats = {}
    th(['Period', 'Total', 'IP Discussed', 'IP %', 'IP Strict %', 'No-IP Strict %', 'IP Broad %', 'No-IP Broad %'])
    for label, cases in [('All', disab), ('P1', p1), ('P2', p2), ('P3', p3)]:
        total = len(cases)
        ip_y = [r for r in cases if r.get('interactive_process_discussed') == 'YES']
        ip_n = [r for r in cases if r.get('interactive_process_discussed') == 'NO']
        wy, wn = win_rates(ip_y), win_rates(ip_n)
        ip_stats[label] = {
            'total': total, 'ip_discussed': len(ip_y), 'ip_pct': pct(len(ip_y), total),
            'ip_yes_win': wy, 'ip_no_win': wn,
        }
        tr([label, total, len(ip_y), pct(len(ip_y), total),
            wy['strict_pct'], wn['strict_pct'], wy['broad_pct'], wn['broad_pct']])
    stats['interactive_process'] = ip_stats

    # ============================================================
    # I. DESIGN-AND-CONSTRUCTION
    # ============================================================
    section("I. Design-and-Construction")

    def is_dc(r):
        return (r.get('primary_claim_type') == 'design_and_construction' or
                r.get('fha_section_cited') == '3604(f)(3)(C)' or
                'design_and_construction' in (r.get('claim_types') or []))

    dc_stats = {}
    th(['Period', 'D&C Cases', 'D&C Decided', 'Strict %', 'Share %'])
    for label, cases in [('All', disab), ('P1', p1), ('P2', p2), ('P3', p3)]:
        dc = [r for r in cases if is_dc(r)]
        dwr = win_rates(dc)
        dc_stats[label] = {'dc_count': len(dc), 'dc_decided': dwr['n_decided'],
                           'dc_win': dwr, 'dc_share': pct(len(dc), len(cases))}
        tr([label, len(dc), dwr['n_decided'], dwr['strict_pct'], pct(len(dc), len(cases))])

    # Section citation effect
    lines.append(f"\n**FHA Section Citation Effect:**")
    sec_b = [r for r in disab if r.get('fha_section_cited') == '3604(f)(3)(B)']
    sec_none = [r for r in disab if r.get('fha_section_cited') in ('NONE_SPECIFIC', None, '')]
    wb, wn = win_rates(sec_b), win_rates(sec_none)
    lines.append(f"§ 3604(f)(3)(B) cited: {wb['strict_pct']}% strict (n={wb['n_decided']})")
    lines.append(f"No specific section: {wn['strict_pct']}% strict (n={wn['n_decided']})")

    lines.append(f"\n§ 3604(f)(3)(B) by period:")
    th(['Period', 'N decided', 'Strict %'])
    for label, cases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        sub = [r for r in cases if r.get('fha_section_cited') == '3604(f)(3)(B)']
        wr = win_rates(sub)
        tr([label, wr['n_decided'], wr['strict_pct']])
    stats['design_construction'] = dc_stats

    # ============================================================
    # J. IQBAL/TWOMBLY
    # ============================================================
    section("J. Iqbal/Twombly")

    iq_stats = {}
    mtd_iq = [r for r in disab if r.get('procedural_posture') == 'MOTION_TO_DISMISS'
              and r.get('iqbal_twombly_cited') is not None]
    iq_cited = [r for r in mtd_iq if r['iqbal_twombly_cited'] is True]
    iq_stats['mtd_citation_rate'] = pct(len(iq_cited), len(mtd_iq))
    lines.append(f"MTD Iqbal citation rate: {len(iq_cited)}/{len(mtd_iq)} = {iq_stats['mtd_citation_rate']}%")

    th(['Period', 'Iqbal Strict %', 'Iqbal N', 'No-Iqbal Strict %', 'No-Iqbal N'])
    for label, cases in [('All', disab), ('P1', p1), ('P2', p2), ('P3', p3)]:
        iy = [r for r in cases if r.get('iqbal_twombly_cited') is True]
        in_ = [r for r in cases if r.get('iqbal_twombly_cited') is False]
        wiy, win_ = win_rates(iy), win_rates(in_)
        iq_stats[f'{label}_yes'] = wiy
        iq_stats[f'{label}_no'] = win_
        tr([label, wiy['strict_pct'], wiy['n_decided'], win_['strict_pct'], win_['n_decided']])

    lines.append(f"\nMTD Iqbal citation rate by period:")
    for label, cases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        m = [r for r in cases if r.get('procedural_posture') == 'MOTION_TO_DISMISS'
             and r.get('iqbal_twombly_cited') is not None]
        ic = [r for r in m if r['iqbal_twombly_cited'] is True]
        lines.append(f"  {label}: {len(ic)}/{len(m)} = {pct(len(ic), len(m))}%")
    stats['iqbal'] = iq_stats

    # ============================================================
    # K. LOPER BRIGHT CITATION
    # ============================================================
    section("K. Loper Bright Citation")

    for label, cases in [('All', disab), ('P1', p1), ('P2', p2), ('P3', p3)]:
        lb = [r for r in cases if r.get('loper_bright_cited') == 'YES']
        lines.append(f"{label}: {len(lb)} cases cite Loper Bright")

    # ============================================================
    # L. ACCOMMODATION TYPE BY PERIOD
    # ============================================================
    section("L. Accommodation Type Win Rates by Period")

    for plabel, pcases in [('P1', p1), ('P2', p2), ('P3', p3)]:
        lines.append(f"\n**{plabel}:**")
        ag = group_by(pcases, 'accommodation_type')
        th(['Accommodation Type', 'N decided', 'Strict %', 'Broad %'])
        for at in accom_order:
            wr = win_rates(ag.get(at, []))
            if wr['n_decided'] >= 5:
                tr([at, wr['n_decided'], wr['strict_pct'], wr['broad_pct']])

    # ============================================================
    # SAVE
    # ============================================================
    with open(STATS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False, default=str)

    header = f"""# FHA Unified Database — Disability Cases — Three-Period Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Database:** FHA Unified Database, filtered to disability cases (disability in protected_classes)
- Total FHA screened-in: {len(all_screened)}
- Disability cases: {len(disab)} ({100*len(disab)/len(all_screened):.1f}%)
- Dated disability: {len(dated)} — P1: {len(p1)}, P2: {len(p2)}, P3: {len(p3)}
- Undated disability: {len(disab) - len(dated)}

**Periods:**
- P1: Pre-Loper Bright (1/1/2022 – 6/28/2024)
- P2: Post-LB / Pre-HUD Secretary (6/28/2024 – 2/5/2025)
- P3: Post-HUD Secretary (2/5/2025 – present)

**Decided:** PLAINTIFF_WIN, DEFENDANT_WIN, MIXED
"""
    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(header + '\n'.join(lines))

    print(f"\nStats: {STATS_OUTPUT}")
    print(f"Report: {REPORT_OUTPUT}")


if __name__ == '__main__':
    main()
