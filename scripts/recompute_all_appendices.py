"""
Comprehensive recalculation of ALL appendix statistics on the
FHA Unified Database, filtered to disability cases only.

Three periods:
  P1: 2022-01-01 to 2024-06-28  (Pre-Loper Bright)
  P2: 2024-06-28 to 2025-02-05  (Post-LB / Pre-HUD Secretary)
  P3: 2025-02-05 to present     (Post-HUD Secretary)

Produces: data/2/appendix_data.json  (machine-readable)
          data/2/appendix_report.md  (human-readable)
"""
import json, os, sys, math
from collections import Counter, defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'C:\Users\nickg\OneDrive\Documents\Note\data\2'
DB_PATH  = os.path.join(DATA_DIR, 'FHA_Unified_Database.json')
OUT_JSON = os.path.join(DATA_DIR, 'appendix_data.json')
OUT_MD   = os.path.join(DATA_DIR, 'appendix_report.md')

P1_START = '2022-01-01'; P1_END = '2024-06-28'; P2_END = '2025-02-05'
DECIDED = {'PLAINTIFF_WIN','DEFENDANT_WIN','MIXED'}

def load(): return json.load(open(DB_PATH,'r',encoding='utf-8'))

def has_disability(r):
    return 'disability' in [p.lower() for p in (r.get('protected_classes') or [])]

def period(r):
    d = r.get('date_filed')
    if not d or d < P1_START: return None
    if d < P1_END: return 'P1'
    if d < P2_END: return 'P2'
    return 'P3'

def old_era(r):
    y = r.get('year')
    if y is None: return None
    return 'pre' if y <= 2023 else 'post'

def wr(cases):
    dec = [r for r in cases if r.get('outcome') in DECIDED]
    n = len(dec)
    if n == 0: return {'n':0,'pw':0,'dw':0,'mx':0,'s':None,'b':None}
    pw = sum(1 for r in dec if r['outcome']=='PLAINTIFF_WIN')
    dw = sum(1 for r in dec if r['outcome']=='DEFENDANT_WIN')
    mx = sum(1 for r in dec if r['outcome']=='MIXED')
    return {'n':n,'pw':pw,'dw':dw,'mx':mx,
            's':round(100*pw/n,1),'b':round(100*(pw+mx)/n,1)}

def pct(a,b): return round(100*a/b,1) if b else None

def chi2(a_pw,a_n,b_pw,b_n):
    if a_n==0 or b_n==0: return None,None
    a2,b2 = a_n-a_pw, b_n-b_pw
    N = a_pw+a2+b_pw+b2
    if N==0: return None,None
    cells=[(a_pw,(a_pw+a2)*(a_pw+b_pw)/N),(a2,(a_pw+a2)*(a2+b2)/N),
           (b_pw,(b_pw+b2)*(a_pw+b_pw)/N),(b2,(b_pw+b2)*(a2+b2)/N)]
    c = sum((o-e)**2/e if e>0 else 0 for o,e in cells)
    p = math.erfc(math.sqrt(c)/math.sqrt(2)) if c>0 else 1.0
    return round(c,2), round(p,6)

def grp(cases, field):
    g = defaultdict(list)
    for r in cases:
        v = r.get(field)
        if v: g[v].append(r)
    return dict(g)

L = []  # report lines
D = {}  # data dict

def sec(t): L.append(f"\n## {t}\n")
def th(c): L.append('| '+' | '.join(c)+' |'); L.append('|'+'|'.join(['---']*len(c))+'|')
def tr(v): L.append('| '+' | '.join(str(x) for x in v)+' |')

def main():
    db = load()
    allsc = [r for r in db if r.get('screening_result','')!='NO' and r.get('case_name')]
    dis = [r for r in allsc if has_disability(r)]
    for r in dis: r['_p']=period(r); r['_e']=old_era(r)
    dated = [r for r in dis if r['_p']]
    p1=[r for r in dated if r['_p']=='P1']
    p2=[r for r in dated if r['_p']=='P2']
    p3=[r for r in dated if r['_p']=='P3']
    pre=[r for r in dis if r['_e']=='pre']
    post=[r for r in dis if r['_e']=='post']

    D['meta'] = {'total_fha':len(allsc),'disability':len(dis),
                 'dated':len(dated),'P1':len(p1),'P2':len(p2),'P3':len(p3)}

    # ===== APPENDIX B: RESULTS TABLES =====
    sec("APPENDIX B: Results Tables")

    # B.1 Three-period win rates
    L.append("### B.1 Three-Period Win Rates\n")
    th(['Period','N decided','PW','DW','MIXED','Strict %','Broad %'])
    for lbl,c in [('P1',p1),('P2',p2),('P3',p3),('P2+P3',p2+p3),('All dated',dated)]:
        w=wr(c); tr([lbl,w['n'],w['pw'],w['dw'],w['mx'],w['s'],w['b']])
    D['B1_win_rates'] = {lbl:wr(c) for lbl,c in [('P1',p1),('P2',p2),('P3',p3),('P2+P3',p2+p3),('All',dated)]}

    # B.2 Binary validation
    L.append("\n### B.2 Binary Split Validation\n")
    th(['Era','N decided','Strict %','Broad %'])
    for lbl,c in [('pre (<=2023)',pre),('post (>=2024)',post)]:
        w=wr(c); tr([lbl,w['n'],w['s'],w['b']])

    # B.3 Year-by-year
    L.append("\n### B.3 Year-by-Year (Table B.3)\n")
    th(['Year','N decided','Strict %','Broad %'])
    yg = grp(dis,'year')
    for y in sorted(k for k in yg if k and 2015<=k<=2026):
        w=wr(yg[y]); tr([y,w['n'],w['s'],w['b']])

    # B.4 Dismissal/disposition breakdown
    L.append("\n### B.4 Procedural Disposition\n")
    th(['Disposition','Count','% of decided'])
    dec_all = [r for r in dis if r.get('outcome') in DECIDED]
    disp_map = Counter()
    for r in dis:
        if r.get('outcome') in DECIDED:
            pp = r.get('procedural_posture','UNKNOWN')
            disp_map[pp] += 1
    for pp,cnt in disp_map.most_common():
        tr([pp,cnt,pct(cnt,len(dec_all))])

    # B.5 Chi-squared
    L.append("\n### B.5 Statistical Tests\n")
    tests = [('P1','P2'),('P1','P3'),('P2','P3'),('P1','P2+P3')]
    wrs = {lbl:wr(c) for lbl,c in [('P1',p1),('P2',p2),('P3',p3),('P2+P3',p2+p3)]}
    L.append("**Strict:**")
    for a,b in tests:
        wa,wb=wrs[a],wrs[b]
        c2,p=chi2(wa['pw'],wa['n'],wb['pw'],wb['n'])
        L.append(f"  {a} vs {b}: χ²={c2}, p={p}")
    L.append("\n**Broad:**")
    for a,b in tests:
        wa,wb=wrs[a],wrs[b]
        c2,p=chi2(wa['pw']+wa['mx'],wa['n'],wb['pw']+wb['mx'],wb['n'])
        L.append(f"  {a} vs {b}: χ²={c2}, p={p}")

    # ===== APPENDIX C: IQBAL =====
    sec("APPENDIX C: Iqbal/Twombly Analysis")

    # C.1 Overall citation rates
    mtd_all = [r for r in dis if r.get('procedural_posture')=='MOTION_TO_DISMISS'
               and r.get('iqbal_twombly_cited') is not None]
    iq_cited = [r for r in mtd_all if r['iqbal_twombly_cited'] is True]
    L.append(f"MTD Iqbal citation rate: {len(iq_cited)}/{len(mtd_all)} = {pct(len(iq_cited),len(mtd_all))}%\n")

    # C.2 Citation rate by period
    L.append("**By period:**")
    for lbl,c in [('P1',p1),('P2',p2),('P3',p3)]:
        m=[r for r in c if r.get('procedural_posture')=='MOTION_TO_DISMISS' and r.get('iqbal_twombly_cited') is not None]
        ic=[r for r in m if r['iqbal_twombly_cited'] is True]
        L.append(f"  {lbl}: {len(ic)}/{len(m)} = {pct(len(ic),len(m))}%")

    # C.3 Outcome effect
    L.append("\n**Iqbal effect on outcomes (all disability):**")
    th(['Period','Iqbal Strict %','Iqbal N','No-Iqbal Strict %','No-Iqbal N','Iqbal Broad %','No-Iqbal Broad %'])
    for lbl,c in [('All',dis),('P1',p1),('P2',p2),('P3',p3)]:
        iy=[r for r in c if r.get('iqbal_twombly_cited') is True]
        in_=[r for r in c if r.get('iqbal_twombly_cited') is False]
        wy,wn=wr(iy),wr(in_)
        tr([lbl,wy['s'],wy['n'],wn['s'],wn['n'],wy['b'],wn['b']])

    # C.4 MTD outcome with/without Iqbal
    L.append("\n**MTD outcomes with/without Iqbal:**")
    th(['Metric','Iqbal Cited','Not Cited'])
    mtd_iq = [r for r in mtd_all if r['iqbal_twombly_cited'] is True and r.get('outcome') in DECIDED]
    mtd_noiq = [r for r in mtd_all if r['iqbal_twombly_cited'] is False and r.get('outcome') in DECIDED]
    wi,wni = wr(mtd_iq), wr(mtd_noiq)
    tr(['N decided',wi['n'],wni['n']])
    tr(['DW %',pct(wi['dw'],wi['n']),pct(wni['dw'],wni['n'])])
    tr(['PW %',wi['s'],wni['s']])
    tr(['Broad %',wi['b'],wni['b']])

    # C.5 Cross-class Iqbal citation (disability vs race vs other)
    L.append("\n**Cross-class Iqbal MTD citation rates:**")
    for cls_name, cls_filter in [('disability', lambda r: 'disability' in [p.lower() for p in (r.get('protected_classes') or [])]),
                                  ('race', lambda r: 'race' in [p.lower() for p in (r.get('protected_classes') or [])]),
                                  ('familial_status', lambda r: 'familial_status' in [p.lower() for p in (r.get('protected_classes') or [])])]:
        cls_cases = [r for r in allsc if cls_filter(r) and r.get('procedural_posture')=='MOTION_TO_DISMISS'
                     and r.get('iqbal_twombly_cited') is not None]
        cls_iq = [r for r in cls_cases if r['iqbal_twombly_cited'] is True]
        L.append(f"  {cls_name}: {len(cls_iq)}/{len(cls_cases)} = {pct(len(cls_iq),len(cls_cases))}%")

    # ===== APPENDIX E: ACCOMMODATION & DEFENDANT =====
    sec("APPENDIX E: Accommodation & Defendant Analysis")

    # E.1 Accommodation type (all disability)
    L.append("### E.1 Win Rates by Accommodation Type (all disability decided)\n")
    accom_order = ['ASSISTANCE_ANIMAL','PARKING','SOBER_LIVING_GROUP_HOME_ZONING','LIVE_IN_AIDE',
                   'COMMUNICATION_ACCOMMODATION','EVICTION_DEFENSE','STRUCTURAL_MODIFICATION',
                   'OTHER','POLICY_EXCEPTION','DISCRIMINATION_PRIMARY','TRANSFER','RENT_PAYMENT','UNDETERMINED']
    ag = grp(dis,'accommodation_type')
    th(['Accommodation Type','N decided','PW %','DW %','MIXED %','Strict %','Broad %'])
    for at in accom_order:
        w=wr(ag.get(at,[]))
        if w['n']>=5:
            tr([at,w['n'],pct(w['pw'],w['n']),pct(w['dw'],w['n']),pct(w['mx'],w['n']),w['s'],w['b']])

    # E.1a Accommodation type by period
    for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
        L.append(f"\n**{plbl}:**")
        pag = grp(pc,'accommodation_type')
        th(['Accommodation Type','N decided','Strict %','Broad %'])
        for at in accom_order:
            w=wr(pag.get(at,[]))
            if w['n']>=3: tr([at,w['n'],w['s'],w['b']])

    # E.2 Defendant type (all disability)
    L.append("\n### E.2 Win Rates by Defendant Type (all disability decided)\n")
    dt_order = ['DEVELOPER','HOA_CONDO_ASSN','PRIVATE_LANDLORD','MUNICIPALITY',
                'PROPERTY_MANAGEMENT','OTHER','HOUSING_AUTHORITY','GOVERNMENT','LENDER']
    dg = grp(dis,'defendant_type')
    th(['Defendant Type','N decided','Strict %','Broad %'])
    for dt in dt_order:
        w=wr(dg.get(dt,[]))
        if w['n']>=5: tr([dt,w['n'],w['s'],w['b']])

    # E.2a Defendant type by period
    for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
        L.append(f"\n**{plbl}:**")
        pdg = grp(pc,'defendant_type')
        th(['Defendant Type','N decided','Strict %','Broad %'])
        for dt in dt_order:
            w=wr(pdg.get(dt,[]))
            if w['n']>=3: tr([dt,w['n'],w['s'],w['b']])

    # E.3 Disability category
    L.append("\n### E.3 Win Rates by Disability Category\n")
    dc_order = ['SENSORY','INTELLECTUAL_DEVELOPMENTAL','MOBILITY','SUBSTANCE_USE',
                'MENTAL_HEALTH','MULTIPLE_UNSPECIFIED','OTHER','UNDETERMINED']
    dcg = grp(dis,'disability_category')
    th(['Disability Category','N decided','Strict %','Broad %'])
    for dc in dc_order:
        w=wr(dcg.get(dc,[]))
        if w['n']>=5: tr([dc,w['n'],w['s'],w['b']])

    # E.3a Disability category by period
    for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
        L.append(f"\n**{plbl}:**")
        pdcg = grp(pc,'disability_category')
        th(['Disability Category','N decided','Strict %','Broad %'])
        for dc in dc_order:
            w=wr(pdcg.get(dc,[]))
            if w['n']>=3: tr([dc,w['n'],w['s'],w['b']])

    # E.4 Legal theory (from claim_types)
    L.append("\n### E.4 Win Rates by Legal Theory (primary_claim_type)\n")
    ct_order = ['reasonable_accommodation_denial','disparate_treatment','disparate_impact',
                'interference_coercion','retaliation','design_and_construction','reasonable_modification_denial','other']
    ctg = grp(dis,'primary_claim_type')
    th(['Claim Type','N decided','Strict %','Broad %'])
    for ct in ct_order:
        w=wr(ctg.get(ct,[]))
        if w['n']>=5: tr([ct,w['n'],w['s'],w['b']])

    # E.5 FHA section cited
    L.append("\n### E.5 FHA Section Cited Effect\n")
    sec_order = ['3604(f)(3)(B)','3604(f)(3)(A)','3604(f)(3)(C)','3604(f)(1)','3604(f)(2)','NONE_SPECIFIC']
    sg = grp(dis,'fha_section_cited')
    th(['Section','N decided','Strict %','Broad %'])
    for s in sec_order:
        w=wr(sg.get(s,[]))
        if w['n']>=5: tr([s,w['n'],w['s'],w['b']])

    # ===== APPENDIX F: GALANTER PLAINTIFF TYPE =====
    sec("APPENDIX F: Galanter Plaintiff-Type Analysis")

    # F.1 Plaintiff type overall + by period
    pt_order = ['INDIVIDUAL_TENANT','GROUP_HOME_OPERATOR','FAIR_HOUSING_ORG','GOVERNMENT','OTHER']
    L.append("### F.1 Plaintiff Type Win Rates\n")
    L.append("**All disability (full DB):**")
    ptg = grp(dis,'plaintiff_type')
    th(['Plaintiff Type','N decided','Strict %','Broad %'])
    for pt in pt_order:
        w=wr(ptg.get(pt,[]))
        if w['n']>=3: tr([pt,w['n'],w['s'],w['b']])

    for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
        L.append(f"\n**{plbl}:**")
        pptg = grp(pc,'plaintiff_type')
        th(['Plaintiff Type','N decided','Strict %','Broad %'])
        for pt in pt_order:
            w=wr(pptg.get(pt,[]))
            if w['n']>=1: tr([pt,w['n'],w['s'],w['b']])

    # F.2 Plaintiff-type × pro se
    L.append("\n### F.2 Plaintiff Type × Pro Se\n")
    th(['Plaintiff Type','Pro Se %','PS Strict %','Rep Strict %'])
    for pt in pt_order:
        ptc = [r for r in dis if r.get('plaintiff_type')==pt and r.get('pro_se') is not None]
        ps = [r for r in ptc if r['pro_se'] is True]
        rp = [r for r in ptc if r['pro_se'] is False]
        wps,wrp = wr(ps),wr(rp)
        tr([pt, pct(len(ps),len(ptc)), wps['s'], wrp['s']])

    # ===== APPENDIX G: CIRCUIT ANALYSIS =====
    sec("APPENDIX G: Circuit-Level Analysis")

    circ_order = ['1st Circuit','2nd Circuit','3rd Circuit','4th Circuit','5th Circuit',
                  '6th Circuit','7th Circuit','8th Circuit','9th Circuit','10th Circuit',
                  '11th Circuit','D.C. Circuit']

    # G.1 Overall win rates by circuit
    L.append("### G.1 Overall Win Rates by Circuit (all disability decided)\n")
    cg = grp(dis,'circuit')
    th(['Circuit','N decided','Strict %','Broad %'])
    for c in circ_order:
        w=wr(cg.get(c,[]))
        if w['n']>=10: tr([c,w['n'],w['s'],w['b']])

    # G.2 MTD broad by circuit
    L.append("\n### G.2 MTD Broad Win Rates by Circuit\n")
    mtd_dis = [r for r in dis if r.get('outcome') in DECIDED and r.get('procedural_posture')=='MOTION_TO_DISMISS']
    mcg = grp(mtd_dis,'circuit')
    th(['Circuit','MTD N','MTD Broad %'])
    for c in circ_order:
        w=wr(mcg.get(c,[]))
        if w['n']>=10: tr([c,w['n'],w['b']])

    # G.3 Pre/post by circuit (binary)
    L.append("\n### G.3 Binary Pre/Post by Circuit\n")
    th(['Circuit','Pre N','Pre Broad %','Post N','Post Broad %','Delta pp'])
    for c in circ_order:
        pre_c = [r for r in pre if r.get('circuit')==c]
        post_c = [r for r in post if r.get('circuit')==c]
        wp,wq = wr(pre_c),wr(post_c)
        if wp['n']>=10 and wq['n']>=10:
            delta = round(wq['b']-wp['b'],1) if wp['b'] is not None and wq['b'] is not None else None
            tr([c,wp['n'],wp['b'],wq['n'],wq['b'],delta])

    # G.4 Three-period MTD by circuit
    L.append("\n### G.4 Three-Period MTD by Circuit (P1 vs P2+P3, n≥10 both)\n")
    mtd_p1 = [r for r in p1 if r.get('outcome') in DECIDED and r.get('procedural_posture')=='MOTION_TO_DISMISS']
    mtd_p23 = [r for r in p2+p3 if r.get('outcome') in DECIDED and r.get('procedural_posture')=='MOTION_TO_DISMISS']
    th(['Circuit','P1 N','P1 Broad %','P2+P3 N','P2+P3 Broad %','Delta pp'])
    for c in circ_order:
        pre_c = [r for r in mtd_p1 if r.get('circuit')==c]
        post_c = [r for r in mtd_p23 if r.get('circuit')==c]
        wp,wq = wr(pre_c),wr(post_c)
        if wp['n']>=10 and wq['n']>=10:
            delta = round(wq['b']-wp['b'],1) if wp['b'] is not None and wq['b'] is not None else None
            tr([c,wp['n'],wp['b'],wq['n'],wq['b'],delta])

    # G.5 Interactive process by circuit
    L.append("\n### G.5 Interactive Process Discussion Rate by Circuit\n")
    th(['Circuit','Total','IP Discussed','IP %'])
    for c in circ_order:
        cc = [r for r in dis if r.get('circuit')==c]
        ip = [r for r in cc if r.get('interactive_process_discussed')=='YES']
        if len(cc)>=20: tr([c,len(cc),len(ip),pct(len(ip),len(cc))])

    # ===== APPENDIX H: SUPPLEMENTARY =====
    sec("APPENDIX H: Supplementary Data")

    # H.1 Procedural posture win rates
    L.append("### H.1 Win Rates by Procedural Posture\n")
    pp_order = ['MOTION_TO_DISMISS','SUMMARY_JUDGMENT','APPEAL','PRELIMINARY_INJUNCTION',
                'TRIAL','DEFAULT_JUDGMENT','DISCOVERY','OTHER_PROCEDURAL','SETTLEMENT_CONSENT']
    ppg = grp(dis,'procedural_posture')
    th(['Posture','N decided','Strict %','Broad %'])
    for pp in pp_order:
        w=wr(ppg.get(pp,[]))
        if w['n']>=5: tr([pp,w['n'],w['s'],w['b']])

    # H.1a Procedural posture by period
    for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
        L.append(f"\n**{plbl}:**")
        pppg = grp(pc,'procedural_posture')
        th(['Posture','N decided','Strict %','Broad %'])
        for pp in pp_order:
            w=wr(pppg.get(pp,[]))
            if w['n']>=3: tr([pp,w['n'],w['s'],w['b']])

    # H.2 Housing type
    L.append("\n### H.2 Win Rates by Housing Type\n")
    ht_order = ['PRIVATE_MARKET','PUBLIC_HOUSING','SECTION_8','SUBSIDIZED_OTHER',
                'GROUP_HOME','OTHER_SUBSIDIZED','UNDETERMINED']
    htg = grp(dis,'housing_type')
    th(['Housing Type','N decided','Strict %','Broad %'])
    for ht in ht_order:
        w=wr(htg.get(ht,[]))
        if w['n']>=5: tr([ht,w['n'],w['s'],w['b']])

    # H.3 Loper Bright citation
    L.append("\n### H.3 Loper Bright Citation\n")
    for lbl,c in [('All disability',dis),('P1',p1),('P2',p2),('P3',p3)]:
        lb = [r for r in c if r.get('loper_bright_cited')=='YES']
        L.append(f"  {lbl}: {len(lb)} cases cite Loper Bright")

    # H.4 Delay-as-denial
    L.append("\n### H.4 Delay-as-Denial\n")
    dad_y = [r for r in dis if r.get('delay_as_denial')=='YES']
    dad_n = [r for r in dis if r.get('delay_as_denial')=='NO']
    wy,wn = wr(dad_y),wr(dad_n)
    L.append(f"Delay-as-denial invoked: {len(dad_y)} cases ({pct(len(dad_y),len(dad_y)+len(dad_n))}%)")
    L.append(f"  DaD strict win: {wy['s']}% (n={wy['n']})")
    L.append(f"  No DaD strict win: {wn['s']}% (n={wn['n']})")
    L.append(f"  DaD broad win: {wy['b']}% (n={wy['n']})")
    L.append(f"  No DaD broad win: {wn['b']}% (n={wn['n']})")

    # H.5 Interactive process + DaD co-occurrence
    L.append("\n### H.5 Interactive Process + Delay-as-Denial\n")
    ip_y = [r for r in dis if r.get('interactive_process_discussed')=='YES']
    ip_dad = [r for r in ip_y if r.get('delay_as_denial')=='YES']
    L.append(f"IP discussed: {len(ip_y)}, of which DaD also invoked: {len(ip_dad)} ({pct(len(ip_dad),len(ip_y))}%)")
    w_both = wr(ip_dad)
    L.append(f"  Combined IP+DaD strict: {w_both['s']}% (n={w_both['n']})")
    L.append(f"  Combined IP+DaD broad: {w_both['b']}% (n={w_both['n']})")

    # H.6 Pro se × defendant type (detailed)
    L.append("\n### H.6 Pro Se × Defendant Type Cross-Tab\n")
    th(['Defendant','PS N dec','PS Strict','PS Broad','Rep N dec','Rep Strict','Rep Broad'])
    for dt in dt_order:
        ps_dt = [r for r in dis if r.get('defendant_type')==dt and r.get('pro_se') is True and r.get('outcome') in DECIDED]
        rp_dt = [r for r in dis if r.get('defendant_type')==dt and r.get('pro_se') is False and r.get('outcome') in DECIDED]
        wps,wrp = wr(ps_dt),wr(rp_dt)
        if wps['n']>=3 or wrp['n']>=3:
            tr([dt,wps['n'],wps['s'],wps['b'],wrp['n'],wrp['s'],wrp['b']])

    # ===== APPENDIX A-3 EXTENDED =====
    sec("APPENDIX A-3: Extended Empirical Analysis (Key Cross-Tabs)")

    # A3.1 Procedural posture × period (for interaction model)
    L.append("### A3.1 Procedural Posture × Period\n")
    for pp in ['MOTION_TO_DISMISS','SUMMARY_JUDGMENT','APPEAL']:
        L.append(f"\n**{pp}:**")
        th(['Period','N decided','Strict %','Broad %'])
        for plbl,pc in [('P1',p1),('P2',p2),('P3',p3)]:
            sub = [r for r in pc if r.get('procedural_posture')==pp]
            w=wr(sub)
            tr([plbl,w['n'],w['s'],w['b']])

    # A3.2 Interactive process × defendant type
    L.append("\n### A3.2 Interactive Process × Defendant Type\n")
    th(['Defendant Type','IP Cases','Total','IP %','IP Broad %','No-IP Broad %'])
    for dt in ['HOA_CONDO_ASSN','PRIVATE_LANDLORD','MUNICIPALITY','PROPERTY_MANAGEMENT','HOUSING_AUTHORITY']:
        dt_c = [r for r in dis if r.get('defendant_type')==dt]
        ip = [r for r in dt_c if r.get('interactive_process_discussed')=='YES']
        nip = [r for r in dt_c if r.get('interactive_process_discussed')=='NO']
        wip,wnip = wr(ip),wr(nip)
        tr([dt,len(ip),len(dt_c),pct(len(ip),len(dt_c)),wip['b'],wnip['b']])

    # A3.3 State-level top/bottom (decided disability cases)
    L.append("\n### A3.3 State-Level Win Rates (n≥20 decided)\n")
    state_g = grp(dis,'property_state')
    state_wr = {}
    for s,cases in state_g.items():
        if s and s != 'UNDETERMINED':
            w = wr(cases)
            if w['n'] >= 20: state_wr[s] = w
    sorted_states = sorted(state_wr.items(), key=lambda x: x[1]['s'] or 0, reverse=True)
    th(['State','N decided','Strict %','Broad %'])
    for s,w in sorted_states:
        tr([s,w['n'],w['s'],w['b']])

    # ===== SAVE =====
    header = f"""# FHA Unified Database — Complete Appendix Data

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Database:** FHA Unified Database, disability cases only
- Total FHA screened-in: {len(allsc)}
- Disability cases: {len(dis)} ({pct(len(dis),len(allsc))}%)
- Dated disability: {len(dated)} — P1: {len(p1)}, P2: {len(p2)}, P3: {len(p3)}

**Periods:**
- P1: Pre-*Loper Bright* (1/1/2022 – 6/28/2024)
- P2: Post-LB / Pre-HUD Secretary (6/28/2024 – 2/5/2025)
- P3: Post-HUD Secretary (2/5/2025 – present)
"""
    with open(OUT_MD,'w',encoding='utf-8') as f:
        f.write(header + '\n'.join(L))
    with open(OUT_JSON,'w',encoding='utf-8') as f:
        json.dump(D, f, indent=2, ensure_ascii=False, default=str)
    print(f"Report: {OUT_MD}")
    print(f"Data: {OUT_JSON}")
    print(f"Disability cases: {len(dis)}, Dated: {len(dated)}")

if __name__=='__main__': main()
