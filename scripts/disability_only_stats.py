#!/usr/bin/env python3
"""
FHA Disability Litigation Statistics for Law Review Note
Analyzes case-level and claim-level JSON databases.
"""

import json
import sys
import os
from collections import Counter, defaultdict

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Helper: chi-squared 2x2 test (no scipy dependency)
# ---------------------------------------------------------------------------
def chi2_2x2(a, b, c, d):
    """
    2x2 contingency table chi-squared test (with Yates correction).
    Layout:  [[a, b], [c, d]]
    Returns (chi2, p_value_approx).
    p-value via survival function of chi2(1) using Wilson-Hilferty approx.
    """
    import math
    n = a + b + c + d
    if n == 0:
        return (0.0, 1.0)
    num = n * (abs(a * d - b * c) - n / 2) ** 2
    denom = (a + b) * (c + d) * (a + c) * (b + d)
    if denom == 0:
        return (0.0, 1.0)
    chi2 = num / denom
    # p-value approximation for chi2(1) using formula: P(X > x) ≈ erfc(sqrt(x/2))/2
    p = 0.5 * math.erfc(math.sqrt(chi2 / 2))
    return (chi2, p)


def sig_label(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    elif p < 0.10:
        return "†"
    else:
        return "n.s."


def pct(num, denom):
    if denom == 0:
        return "N/A"
    return f"{100 * num / denom:.1f}%"


def normalize(val):
    """Normalize a field value to uppercase string."""
    if val is None:
        return None
    if isinstance(val, bool):
        return "YES" if val else "NO"
    return str(val).strip().upper()


def is_yes(val):
    n = normalize(val)
    return n in ("YES", "TRUE")


def safe_int_year(y):
    if y is None:
        return None
    try:
        return int(float(y))
    except (ValueError, TypeError):
        return None


# ===========================================================================
# LOAD DATA
# ===========================================================================
FILE1 = r"C:\Users\nickg\OneDrive\Documents\Note\allFHAcases\3604\RAClassification_DB_3604_resolved_20260328_104314.json"
FILE2 = r"C:\Users\nickg\OneDrive\Documents\Note\allFHAcases\3604\RAClassification_DB_3604_claims_extraction.json"

with open(FILE1, encoding="utf-8") as f:
    cases_all = json.load(f)

with open(FILE2, encoding="utf-8") as f:
    claims_raw = json.load(f)

# ===========================================================================
# FILE 1 PREP
# ===========================================================================
cases_yes = [c for c in cases_all if normalize(c.get("screening_result")) == "YES"]
EXCLUDE_OUTCOMES = {"PROCEDURAL", "SETTLEMENT", "UNDETERMINED"}
decided = [c for c in cases_yes if normalize(c.get("outcome")) not in EXCLUDE_OUTCOMES and normalize(c.get("outcome")) is not None]


def strict_pw(cases):
    return sum(1 for c in cases if normalize(c.get("outcome")) == "PLAINTIFF_WIN")


def broad_pw(cases):
    return sum(1 for c in cases if normalize(c.get("outcome")) in ("PLAINTIFF_WIN", "MIXED"))


# ===========================================================================
# FILE 2 PREP
# ===========================================================================
all_claims = []
case_extractions = []
for entry in claims_raw:
    ext = entry.get("extraction", {})
    case_extractions.append(ext)
    for claim in ext.get("fha_claims", []):
        claim["_case"] = ext  # back-reference
        all_claims.append(claim)

fha_claims = [cl for cl in all_claims if normalize(cl.get("theory")) != "NOT_FHA"]
CLAIM_EXCLUDE = {"UNDETERMINED", "PENDING"}
decided_claims = [cl for cl in fha_claims if normalize(cl.get("outcome")) not in CLAIM_EXCLUDE and normalize(cl.get("outcome")) is not None]


def claim_pw_strict(cls):
    return sum(1 for c in cls if normalize(c.get("outcome")) == "PLAINTIFF")


def claim_pw_broad(cls):
    return sum(1 for c in cls if normalize(c.get("outcome")) in ("PLAINTIFF", "MIXED"))


# ===========================================================================
# PRINT HELPERS
# ===========================================================================
def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_winrate_table(rows, header=None):
    """rows: list of (label, n, strict%, broad%)"""
    if header is None:
        header = ("Category", "N decided", "Strict PW%", "Broad PW+MX%")
    widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    print(fmt.format(*header))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*r))


def winrate_by_field(field, group_threshold=0):
    """Compute win rates grouped by a case-level field. Returns rows."""
    groups = defaultdict(list)
    for c in decided:
        val = normalize(c.get(field))
        if val is None or val in ("N/A", "NONE", ""):
            val = "UNKNOWN"
        groups[val].append(c)
    # Optionally group small categories
    if group_threshold > 0:
        other = []
        to_remove = []
        for k, v in groups.items():
            if len(v) < group_threshold:
                other.extend(v)
                to_remove.append(k)
        for k in to_remove:
            del groups[k]
        if other:
            groups["OTHER"] = groups.get("OTHER", []) + other
    rows = []
    for k in sorted(groups, key=lambda x: -len(groups[x])):
        g = groups[k]
        n = len(g)
        rows.append((k, str(n), pct(strict_pw(g), n), pct(broad_pw(g), n)))
    return rows


def binary_effect(field_name, field_key):
    """Print win-rate comparison for a YES/NO binary field with chi-squared."""
    yes_cases = [c for c in decided if is_yes(c.get(field_key))]
    no_cases = [c for c in decided if not is_yes(c.get(field_key)) and c.get(field_key) is not None]
    ny, nn = len(yes_cases), len(no_cases)
    spy, bpy = strict_pw(yes_cases), broad_pw(yes_cases)
    spn, bpn = strict_pw(no_cases), broad_pw(no_cases)
    print(f"\n  {field_name} = YES : n={ny}, strict PW = {pct(spy, ny)}, broad PW+MX = {pct(bpy, ny)}")
    print(f"  {field_name} = NO  : n={nn}, strict PW = {pct(spn, nn)}, broad PW+MX = {pct(bpn, nn)}")
    # Chi-squared on strict PW
    a, b = spy, ny - spy
    c, d = spn, nn - spn
    chi2, p = chi2_2x2(a, b, c, d)
    print(f"  Chi-squared (strict PW): χ²={chi2:.3f}, p={p:.4f} {sig_label(p)}")
    # Chi-squared on broad
    a2, b2 = bpy, ny - bpy
    c2, d2 = bpn, nn - bpn
    chi2b, pb = chi2_2x2(a2, b2, c2, d2)
    print(f"  Chi-squared (broad PW+MX): χ²={chi2b:.3f}, p={pb:.4f} {sig_label(pb)}")


# ###########################################################################
#  OUTPUT
# ###########################################################################

print("=" * 80)
print("  FHA DISABILITY LITIGATION STATISTICS")
print("  Generated for Law Review Note")
print("=" * 80)

# ---- 1. Total counts ----
print_header("1. TOTAL COUNTS (File 1 - Case Level)")
print(f"  Total entries in database:        {len(cases_all)}")
print(f"  Screened YES (FHA-relevant):      {len(cases_yes)}")
print(f"  Decided (excl PROCEDURAL/SETTLEMENT/UNDETERMINED): {len(decided)}")
excluded_proc = sum(1 for c in cases_yes if normalize(c.get("outcome")) == "PROCEDURAL")
excluded_sett = sum(1 for c in cases_yes if normalize(c.get("outcome")) == "SETTLEMENT")
excluded_und = sum(1 for c in cases_yes if normalize(c.get("outcome")) == "UNDETERMINED")
print(f"  Excluded - PROCEDURAL:  {excluded_proc}")
print(f"  Excluded - SETTLEMENT:  {excluded_sett}")
print(f"  Excluded - UNDETERMINED: {excluded_und}")

# ---- 2. Overall win rates ----
print_header("2. OVERALL WIN RATES (Case Level)")
n_dec = len(decided)
sp = strict_pw(decided)
bp = broad_pw(decided)
dw = sum(1 for c in decided if normalize(c.get("outcome")) == "DEFENDANT_WIN")
mx = sum(1 for c in decided if normalize(c.get("outcome")) == "MIXED")
print(f"  PLAINTIFF_WIN:  {sp}  ({pct(sp, n_dec)})")
print(f"  DEFENDANT_WIN:  {dw}  ({pct(dw, n_dec)})")
print(f"  MIXED:          {mx}  ({pct(mx, n_dec)})")
print(f"  Strict PW rate:       {pct(sp, n_dec)}  (n={n_dec})")
print(f"  Broad PW+MIXED rate:  {pct(bp, n_dec)}  (n={n_dec})")

# ---- 3. Pre/Post Loper Bright ----
print_header("3. PRE/POST LOPER BRIGHT WIN RATES (year <= 2023 vs >= 2024)")
pre = [c for c in decided if safe_int_year(c.get("year")) is not None and safe_int_year(c.get("year")) <= 2023]
post = [c for c in decided if safe_int_year(c.get("year")) is not None and safe_int_year(c.get("year")) >= 2024]
npre, npost = len(pre), len(post)
sp_pre, sp_post = strict_pw(pre), strict_pw(post)
bp_pre, bp_post = broad_pw(pre), broad_pw(post)
print(f"  Pre  (<=2023): n={npre}, strict PW={pct(sp_pre, npre)}, broad PW+MX={pct(bp_pre, npre)}")
print(f"  Post (>=2024): n={npost}, strict PW={pct(sp_post, npost)}, broad PW+MX={pct(bp_post, npost)}")
chi2s, ps = chi2_2x2(sp_pre, npre - sp_pre, sp_post, npost - sp_post)
chi2b, pb = chi2_2x2(bp_pre, npre - bp_pre, bp_post, npost - bp_post)
print(f"  Chi-squared (strict):  χ²={chi2s:.3f}, p={ps:.4f} {sig_label(ps)}")
print(f"  Chi-squared (broad):   χ²={chi2b:.3f}, p={pb:.4f} {sig_label(pb)}")

# ---- 4. Year-by-year ----
print_header("4. YEAR-BY-YEAR WIN RATES")
years = sorted(set(safe_int_year(c.get("year")) for c in decided if safe_int_year(c.get("year")) is not None))
rows = []
for y in years:
    yc = [c for c in decided if safe_int_year(c.get("year")) == y]
    n = len(yc)
    rows.append((str(y), str(n), pct(strict_pw(yc), n), pct(broad_pw(yc), n)))
print_winrate_table(rows, ("Year", "N decided", "Strict PW%", "Broad PW+MX%"))

# ---- 5. By plaintiff type ----
print_header("5. WIN RATES BY PLAINTIFF TYPE")
rows = winrate_by_field("plaintiff_type")
print_winrate_table(rows)

# ---- 6. By defendant type ----
print_header("6. WIN RATES BY DEFENDANT TYPE")
rows = winrate_by_field("defendant_type", group_threshold=20)
print_winrate_table(rows)

# ---- 7. By accommodation type ----
print_header("7. WIN RATES BY ACCOMMODATION TYPE")
rows = winrate_by_field("accommodation_type")
print_winrate_table(rows)

# ---- 8. By disability category ----
print_header("8. WIN RATES BY DISABILITY CATEGORY")
rows = winrate_by_field("disability_category")
print_winrate_table(rows)

# ---- 9. Interactive process effect ----
print_header("9. INTERACTIVE PROCESS EFFECT")
binary_effect("interactive_process_discussed", "interactive_process_discussed")

# ---- 10. Delay as denial ----
print_header("10. DELAY AS DENIAL EFFECT")
binary_effect("delay_as_denial", "delay_as_denial")

# ---- 11. Race mentioned ----
print_header("11. RACE MENTIONED EFFECT")
binary_effect("race_mentioned", "race_mentioned")

# ---- 12. By housing type ----
print_header("12. WIN RATES BY HOUSING TYPE")
rows = winrate_by_field("housing_type")
print_winrate_table(rows)

# ---- 13. Procedural posture distribution ----
print_header("13. PROCEDURAL POSTURE DISTRIBUTION (all screened YES)")
posture_counts = Counter(normalize(c.get("procedural_posture")) for c in cases_yes)
total_yes = len(cases_yes)
rows = []
for k, v in posture_counts.most_common():
    rows.append((str(k), str(v), pct(v, total_yes)))
print_winrate_table(rows, ("Posture", "Count", "% of screened"))

# ---- 14. Win rates by procedural posture ----
print_header("14. WIN RATES BY PROCEDURAL POSTURE")
rows = winrate_by_field("procedural_posture")
print_winrate_table(rows)

# ###########################################################################
# FILE 2 - CLAIM LEVEL
# ###########################################################################

print_header("15. CLAIM-LEVEL TOTALS (File 2)")
print(f"  Total entries in claims file:     {len(claims_raw)}")
print(f"  Total claims (all theories):      {len(all_claims)}")
print(f"  FHA-relevant claims (excl NOT_FHA): {len(fha_claims)}")
print(f"  Decided FHA claims (excl UNDETERMINED/PENDING): {len(decided_claims)}")
remanded = sum(1 for cl in fha_claims if normalize(cl.get("outcome")) == "REMANDED")
print(f"  REMANDED claims:                  {remanded}")
# Outcome distribution for FHA claims
claim_outcomes = Counter(normalize(cl.get("outcome")) for cl in fha_claims)
print("\n  FHA claim outcome distribution:")
for k, v in claim_outcomes.most_common():
    print(f"    {k}: {v} ({pct(v, len(fha_claims))})")

# ---- 16. Pro se rate ----
print_header("16. PRO SE RATE (File 2 - case level)")
pro_se_true = sum(1 for ext in case_extractions if ext.get("pro_se") is True)
pro_se_false = sum(1 for ext in case_extractions if ext.get("pro_se") is False)
pro_se_null = sum(1 for ext in case_extractions if ext.get("pro_se") is None)
pro_se_known = pro_se_true + pro_se_false
print(f"  Pro se = true:  {pro_se_true}")
print(f"  Pro se = false: {pro_se_false}")
print(f"  Pro se = null:  {pro_se_null}")
print(f"  Pro se rate (of known): {pct(pro_se_true, pro_se_known)} (n={pro_se_known})")

# ---- 17. Pro se win rates at claim level ----
print_header("17. PRO SE WIN RATES (Claim Level)")
pro_se_claims = [cl for cl in decided_claims if cl["_case"].get("pro_se") is True]
rep_claims = [cl for cl in decided_claims if cl["_case"].get("pro_se") is False]
nps, nrep = len(pro_se_claims), len(rep_claims)
sps = claim_pw_strict(pro_se_claims)
bps = claim_pw_broad(pro_se_claims)
sr = claim_pw_strict(rep_claims)
br = claim_pw_broad(rep_claims)
print(f"  Pro se claims:       n={nps}, strict PW={pct(sps, nps)}, broad PW+MX={pct(bps, nps)}")
print(f"  Represented claims:  n={nrep}, strict PW={pct(sr, nrep)}, broad PW+MX={pct(br, nrep)}")
chi2s, ps = chi2_2x2(sps, nps - sps, sr, nrep - sr)
chi2b2, pb2 = chi2_2x2(bps, nps - bps, br, nrep - br)
print(f"  Chi-squared (strict): χ²={chi2s:.3f}, p={ps:.4f} {sig_label(ps)}")
print(f"  Chi-squared (broad):  χ²={chi2b2:.3f}, p={pb2:.4f} {sig_label(pb2)}")

# ---- 18. Iqbal/Twombly effect ----
print_header("18. IQBAL/TWOMBLY EFFECT (Claim Level)")
it_yes = [cl for cl in decided_claims if is_yes(cl["_case"].get("iqbal_twombly_cited"))]
it_no = [cl for cl in decided_claims if not is_yes(cl["_case"].get("iqbal_twombly_cited")) and cl["_case"].get("iqbal_twombly_cited") is not None]
nity, nitn = len(it_yes), len(it_no)
sity, bity = claim_pw_strict(it_yes), claim_pw_broad(it_yes)
sitn, bitn = claim_pw_strict(it_no), claim_pw_broad(it_no)
print(f"  Iqbal/Twombly cited YES: n={nity}, strict PW={pct(sity, nity)}, broad PW+MX={pct(bity, nity)}")
print(f"  Iqbal/Twombly cited NO:  n={nitn}, strict PW={pct(sitn, nitn)}, broad PW+MX={pct(bitn, nitn)}")
chi2s, ps = chi2_2x2(sity, nity - sity, sitn, nitn - sitn)
chi2b2, pb2 = chi2_2x2(bity, nity - bity, bitn, nitn - bitn)
print(f"  Chi-squared (strict): χ²={chi2s:.3f}, p={ps:.4f} {sig_label(ps)}")
print(f"  Chi-squared (broad):  χ²={chi2b2:.3f}, p={pb2:.4f} {sig_label(pb2)}")

# ---- 19. MTD survival rates ----
print_header("19. MTD SURVIVAL RATES (Claim Level)")
mtd_claims = [cl for cl in fha_claims if normalize(cl.get("stage")) == "MTD"]
mtd_decided = [cl for cl in mtd_claims if normalize(cl.get("outcome")) not in CLAIM_EXCLUDE and normalize(cl.get("outcome")) is not None]
mtd_survived = [cl for cl in mtd_decided if normalize(cl.get("outcome")) in ("PLAINTIFF", "MIXED")]
print(f"  MTD claims total:   {len(mtd_claims)}")
print(f"  MTD claims decided: {len(mtd_decided)}")
print(f"  MTD survived (PW or MIXED): {len(mtd_survived)} ({pct(len(mtd_survived), len(mtd_decided))})")

# Pre/post Loper Bright MTD
mtd_pre = [cl for cl in mtd_decided if safe_int_year(cl["_case"].get("year")) is not None and safe_int_year(cl["_case"].get("year")) <= 2023]
mtd_post = [cl for cl in mtd_decided if safe_int_year(cl["_case"].get("year")) is not None and safe_int_year(cl["_case"].get("year")) >= 2024]
mtd_surv_pre = sum(1 for cl in mtd_pre if normalize(cl.get("outcome")) in ("PLAINTIFF", "MIXED"))
mtd_surv_post = sum(1 for cl in mtd_post if normalize(cl.get("outcome")) in ("PLAINTIFF", "MIXED"))
print(f"  Pre Loper Bright MTD:  n={len(mtd_pre)}, survived={mtd_surv_pre} ({pct(mtd_surv_pre, len(mtd_pre))})")
print(f"  Post Loper Bright MTD: n={len(mtd_post)}, survived={mtd_surv_post} ({pct(mtd_surv_post, len(mtd_post))})")
if len(mtd_pre) > 0 and len(mtd_post) > 0:
    chi2s, ps = chi2_2x2(mtd_surv_pre, len(mtd_pre) - mtd_surv_pre, mtd_surv_post, len(mtd_post) - mtd_surv_post)
    print(f"  Chi-squared: χ²={chi2s:.3f}, p={ps:.4f} {sig_label(ps)}")

# ---- 20. Merits reached ----
print_header("20. MERITS REACHED (Claim Level)")
merits_yes = sum(1 for cl in fha_claims if normalize(cl.get("merits_reached")) == "YES")
merits_no = sum(1 for cl in fha_claims if normalize(cl.get("merits_reached")) == "NO")
print(f"  Merits reached YES: {merits_yes} ({pct(merits_yes, len(fha_claims))})")
print(f"  Merits reached NO:  {merits_no} ({pct(merits_no, len(fha_claims))})")
print(f"\n  Merits reached by stage:")
stages = sorted(set(normalize(cl.get("stage")) for cl in fha_claims if normalize(cl.get("stage"))))
rows = []
for s in stages:
    scl = [cl for cl in fha_claims if normalize(cl.get("stage")) == s]
    my = sum(1 for cl in scl if normalize(cl.get("merits_reached")) == "YES")
    rows.append((s, str(len(scl)), str(my), pct(my, len(scl))))
print_winrate_table(rows, ("Stage", "Total claims", "Merits YES", "Merits %"))

# ---- 21. Dismissal reasons ----
print_header("21. DISMISSAL REASON DISTRIBUTION (FHA Claims)")
dr_counts = Counter(normalize(cl.get("dismissal_reason")) for cl in fha_claims)
rows = []
for k, v in dr_counts.most_common():
    rows.append((str(k), str(v), pct(v, len(fha_claims))))
print_winrate_table(rows, ("Dismissal Reason", "Count", "% of FHA claims"))

# ---- 22. RA standard applied ----
print_header("22. RA STANDARD APPLIED - DISTRIBUTION AND WIN RATES")
ra_groups = defaultdict(list)
for cl in decided_claims:
    val = normalize(cl.get("ra_standard_applied"))
    if val is None or val in ("N/A", "NONE", ""):
        val = "NONE/N/A"
    ra_groups[val].append(cl)
rows = []
for k in sorted(ra_groups, key=lambda x: -len(ra_groups[x])):
    g = ra_groups[k]
    n = len(g)
    rows.append((k, str(n), pct(claim_pw_strict(g), n), pct(claim_pw_broad(g), n)))
print_winrate_table(rows, ("RA Standard", "N decided", "Strict PW%", "Broad PW+MX%"))

# ---- 23. Claim theory distribution ----
print_header("23. CLAIM THEORY DISTRIBUTION (all claims incl NOT_FHA)")
theory_counts = Counter(normalize(cl.get("theory")) for cl in all_claims)
rows = []
for k, v in theory_counts.most_common():
    rows.append((str(k), str(v), pct(v, len(all_claims))))
print_winrate_table(rows, ("Theory", "Count", "% of all claims"))

# FHA-only theory distribution
print(f"\n  FHA-only theory distribution (n={len(fha_claims)}):")
fha_theory = Counter(normalize(cl.get("theory")) for cl in fha_claims)
rows = []
for k, v in fha_theory.most_common():
    rows.append((str(k), str(v), pct(v, len(fha_claims))))
print_winrate_table(rows, ("Theory", "Count", "% of FHA claims"))

# ---- 24. Per-claim win rates by accommodation type ----
print_header("24. CLAIM-LEVEL WIN RATES BY ACCOMMODATION TYPE")
accom_groups = defaultdict(list)
for cl in decided_claims:
    val = normalize(cl.get("accommodation_type"))
    if val is None or val in ("N/A", "NONE", ""):
        val = "NONE/N/A"
    accom_groups[val].append(cl)
rows = []
for k in sorted(accom_groups, key=lambda x: -len(accom_groups[x])):
    g = accom_groups[k]
    n = len(g)
    rows.append((k, str(n), pct(claim_pw_strict(g), n), pct(claim_pw_broad(g), n)))
print_winrate_table(rows, ("Accommodation Type", "N decided", "Strict PW%", "Broad PW+MX%"))

# ---- 25. Interactive process at claim level ----
print_header("25. INTERACTIVE PROCESS EFFECT AT CLAIM LEVEL")
ip_yes_cl = [cl for cl in decided_claims if is_yes(cl["_case"].get("interactive_process_discussed"))]
ip_no_cl = [cl for cl in decided_claims if not is_yes(cl["_case"].get("interactive_process_discussed"))]
nipy, nipn = len(ip_yes_cl), len(ip_no_cl)
sipy, bipy = claim_pw_strict(ip_yes_cl), claim_pw_broad(ip_yes_cl)
sipn, bipn = claim_pw_strict(ip_no_cl), claim_pw_broad(ip_no_cl)
print(f"  Interactive process YES: n={nipy}, strict PW={pct(sipy, nipy)}, broad PW+MX={pct(bipy, nipy)}")
print(f"  Interactive process NO:  n={nipn}, strict PW={pct(sipn, nipn)}, broad PW+MX={pct(bipn, nipn)}")
chi2s, ps = chi2_2x2(sipy, nipy - sipy, sipn, nipn - sipn)
chi2b2, pb2 = chi2_2x2(bipy, nipy - bipy, bipn, nipn - bipn)
print(f"  Chi-squared (strict): χ²={chi2s:.3f}, p={ps:.4f} {sig_label(ps)}")
print(f"  Chi-squared (broad):  χ²={chi2b2:.3f}, p={pb2:.4f} {sig_label(pb2)}")

# ---- 26. Pro se x defendant type cross-tab ----
print_header("26. PRO SE × DEFENDANT TYPE CROSS-TAB (Claim Level Win Rates)")
def_types_claim = sorted(set(normalize(cl["_case"].get("defendant_type")) or "UNKNOWN" for cl in decided_claims))
rows = []
for dt in def_types_claim:
    ps_dt = [cl for cl in decided_claims if (normalize(cl["_case"].get("defendant_type")) or "UNKNOWN") == dt and cl["_case"].get("pro_se") is True]
    rep_dt = [cl for cl in decided_claims if (normalize(cl["_case"].get("defendant_type")) or "UNKNOWN") == dt and cl["_case"].get("pro_se") is False]
    if len(ps_dt) + len(rep_dt) == 0:
        continue
    rows.append((
        dt,
        f"n={len(ps_dt)}",
        pct(claim_pw_strict(ps_dt), len(ps_dt)),
        pct(claim_pw_broad(ps_dt), len(ps_dt)),
        f"n={len(rep_dt)}",
        pct(claim_pw_strict(rep_dt), len(rep_dt)),
        pct(claim_pw_broad(rep_dt), len(rep_dt)),
    ))
header = ("Defendant Type", "ProSe N", "ProSe Strict%", "ProSe Broad%", "Rep N", "Rep Strict%", "Rep Broad%")
widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
fmt = " | ".join(f"{{:<{w}}}" for w in widths)
print(fmt.format(*header))
print("-+-".join("-" * w for w in widths))
for r in rows:
    print(fmt.format(*r))

# ###########################################################################
# CROSS-DATABASE
# ###########################################################################

# ---- 27. Post-Loper Bright x plaintiff type ----
print_header("27. PRE/POST LOPER BRIGHT × PLAINTIFF TYPE (Case Level)")
ptypes = sorted(set(normalize(c.get("plaintiff_type")) or "UNKNOWN" for c in decided))
rows = []
for pt in ptypes:
    pre_pt = [c for c in pre if (normalize(c.get("plaintiff_type")) or "UNKNOWN") == pt]
    post_pt = [c for c in post if (normalize(c.get("plaintiff_type")) or "UNKNOWN") == pt]
    if len(pre_pt) + len(post_pt) < 5:
        continue
    rows.append((
        pt,
        f"n={len(pre_pt)}", pct(strict_pw(pre_pt), len(pre_pt)), pct(broad_pw(pre_pt), len(pre_pt)),
        f"n={len(post_pt)}", pct(strict_pw(post_pt), len(post_pt)), pct(broad_pw(post_pt), len(post_pt)),
    ))
header = ("Plaintiff Type", "Pre N", "Pre Strict%", "Pre Broad%", "Post N", "Post Strict%", "Post Broad%")
widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
fmt = " | ".join(f"{{:<{w}}}" for w in widths)
print(fmt.format(*header))
print("-+-".join("-" * w for w in widths))
for r in rows:
    print(fmt.format(*r))

# ---- 28. Post-Loper Bright x procedural posture ----
print_header("28. PRE/POST LOPER BRIGHT × PROCEDURAL POSTURE (Case Level)")
postures = sorted(set(normalize(c.get("procedural_posture")) or "UNKNOWN" for c in decided))
rows = []
for pp in postures:
    pre_pp = [c for c in pre if (normalize(c.get("procedural_posture")) or "UNKNOWN") == pp]
    post_pp = [c for c in post if (normalize(c.get("procedural_posture")) or "UNKNOWN") == pp]
    if len(pre_pp) + len(post_pp) < 5:
        continue
    rows.append((
        pp,
        f"n={len(pre_pp)}", pct(strict_pw(pre_pp), len(pre_pp)), pct(broad_pw(pre_pp), len(pre_pp)),
        f"n={len(post_pp)}", pct(strict_pw(post_pp), len(post_pp)), pct(broad_pw(post_pp), len(post_pp)),
    ))
header = ("Posture", "Pre N", "Pre Strict%", "Pre Broad%", "Post N", "Post Strict%", "Post Broad%")
widths = [max(len(str(r[i])) for r in [header] + rows) for i in range(len(header))]
fmt = " | ".join(f"{{:<{w}}}" for w in widths)
print(fmt.format(*header))
print("-+-".join("-" * w for w in widths))
for r in rows:
    print(fmt.format(*r))

print(f"\n{'='*80}")
print("  END OF STATISTICS REPORT")
print(f"{'='*80}")
