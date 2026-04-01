#!/usr/bin/env python3
"""
Combined FHA Case Database Analysis
For law review article on disability fair housing enforcement after Loper Bright.
Analyzes both the RA-specific (3604) database and the general FHA pilot database.
"""

import json
import sys
import re
from collections import Counter, defaultdict
from datetime import datetime

# Try importing scipy for statistical tests
try:
    from scipy.stats import fisher_exact, chi2_contingency
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not available. Statistical tests will be skipped.\n")

# ============================================================
# LOADING
# ============================================================

RA_PATH = r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\RAClassification_DB.json"
FHA_PATH = r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\FHAClassification_DB.json"

with open(RA_PATH, "r", encoding="utf-8") as f:
    ra_cases = json.load(f)

with open(FHA_PATH, "r", encoding="utf-8") as f:
    fha_cases = json.load(f)


# ============================================================
# HELPER: Normalize RA database (inconsistent nesting)
# ============================================================

def normalize_ra(case):
    """Flatten the RA database records which have inconsistent nesting."""
    n = {}
    # case_identification fields
    if "case_identification" in case:
        ci = case["case_identification"]
        n["case_name"] = ci.get("case_name", "")
        n["citation"] = ci.get("citation", "")
        n["court"] = ci.get("court", "")
        n["year"] = ci.get("year")
        n["procedural_posture"] = ci.get("procedural_posture", "")
    else:
        n["case_name"] = case.get("case_name", "")
        n["citation"] = case.get("citation", "")
        n["court"] = case.get("court", "")
        n["year"] = case.get("year")
        n["procedural_posture"] = case.get("procedural_posture", "")

    # accommodation_type
    if "accommodation_type" in case and isinstance(case["accommodation_type"], dict):
        at = case["accommodation_type"]
        n["accommodation_primary"] = at.get("primary", at.get("accommodation_type", ""))
        n["accommodation_description"] = at.get("accommodation_description", "")
        n["accommodation_secondary"] = at.get("secondary_accommodation_type", "NONE")
    else:
        n["accommodation_primary"] = case.get("accommodation_type", "")
        n["accommodation_description"] = case.get("accommodation_description", "")
        n["accommodation_secondary"] = case.get("secondary_accommodation_type", "NONE")

    # parties
    if "parties" in case:
        p = case["parties"]
        n["plaintiff_type"] = p.get("plaintiff_type", "")
        n["defendant_type"] = p.get("defendant_type", "")
    else:
        n["plaintiff_type"] = case.get("plaintiff_type", "")
        n["defendant_type"] = case.get("defendant_type", "")

    # disability
    if "disability_type" in case and isinstance(case["disability_type"], dict):
        dt = case["disability_type"]
        n["disability_category"] = dt.get("disability_category", "")
    else:
        n["disability_category"] = case.get("disability_category", "")

    # outcome
    if "outcome" in case and isinstance(case["outcome"], dict):
        o = case["outcome"]
        n["outcome"] = o.get("outcome", "")
        n["key_holding"] = o.get("key_holding", "")
    else:
        n["outcome"] = case.get("outcome", "")
        n["key_holding"] = case.get("key_holding", "")

    # race / intersection
    if "race_disability_intersection" in case:
        ri = case["race_disability_intersection"]
        n["race_mentioned"] = ri.get("race_mentioned", "NO")
        n["dual_basis_claim"] = ri.get("dual_basis_claim", "NO")
    else:
        n["race_mentioned"] = case.get("race_mentioned", "NO")
        n["dual_basis_claim"] = case.get("dual_basis_claim", "NO")

    # interactive process
    if "interactive_process" in case:
        ip = case["interactive_process"]
        n["interactive_process_discussed"] = ip.get("interactive_process_discussed", "NO")
        n["delay_as_denial"] = ip.get("delay_as_denial", "NO")
    else:
        n["interactive_process_discussed"] = case.get("interactive_process_discussed", "NO")
        n["delay_as_denial"] = case.get("delay_as_denial", "NO")

    n["source_file"] = case.get("source_file", "")
    return n


def normalize_fha(case):
    """Normalize FHA pilot database records."""
    n = {}
    n["case_name"] = case.get("case_name", "")
    n["citation"] = case.get("citation", "")
    n["court"] = case.get("court", "")
    n["circuit"] = case.get("circuit", "")
    n["year"] = case.get("year_decided")
    n["judge"] = case.get("judge_author", "")
    n["protected_classes"] = case.get("protected_classes", [])
    n["primary_protected_class"] = case.get("primary_protected_class", "")
    n["intersectional_claim"] = case.get("intersectional_claim", False)
    n["claim_types"] = case.get("claim_types", [])
    n["primary_claim_type"] = case.get("primary_claim_type", "")
    n["defendant_type"] = case.get("defendant_type", [])
    n["primary_defendant_type"] = case.get("primary_defendant_type", "")
    n["plaintiff_type"] = case.get("plaintiff_type", "")
    n["procedural_posture"] = case.get("procedural_posture", "")
    n["outcome"] = case.get("outcome", "")
    n["outcome_detail"] = case.get("outcome_detail", "")
    n["remedies_awarded"] = case.get("remedies_awarded", [])
    n["damages_amount"] = case.get("damages_amount")
    n["standing_challenged"] = case.get("standing_challenged", False)
    n["zoning_land_use_involved"] = case.get("zoning_land_use_involved", False)
    n["group_home_siting_involved"] = case.get("group_home_siting_involved", False)
    n["voucher_soi_discrimination"] = case.get("voucher_soi_discrimination", False)
    n["design_construction_claim"] = case.get("design_construction_claim", False)
    n["assistance_animal_involved"] = case.get("assistance_animal_involved", False)
    n["disability_type"] = case.get("disability_type", "")
    n["disability_category"] = case.get("disability_category", "")
    n["reasonable_accommodation_type"] = case.get("reasonable_accommodation_type", "")
    n["reasonable_accommodation_detail"] = case.get("reasonable_accommodation_detail", "")
    n["key_statutes_cited"] = case.get("key_statutes_cited", [])
    n["key_cases_cited"] = case.get("key_cases_cited", [])
    n["race_mentions"] = case.get("race_mentions", [])
    n["disability_mentions"] = case.get("disability_mentions", [])
    n["complaint_basis_codes"] = case.get("complaint_basis_codes", [])
    n["complaint_issue_codes"] = case.get("complaint_issue_codes", [])
    n["dual_basis_claim"] = case.get("dual_basis_claim", False)
    n["ra_subcategory"] = case.get("ra_subcategory", "")
    n["assistance_animal_detail"] = case.get("assistance_animal_detail", "")
    n["design_construction_noncompliance"] = case.get("design_construction_noncompliance", "")
    n["brief_summary"] = case.get("brief_summary", "")
    n["source_file"] = case.get("source_file", "")
    return n


ra_norm = [normalize_ra(c) for c in ra_cases]
fha_norm = [normalize_fha(c) for c in fha_cases]

# Fix year types - ensure all are int or None
for c in ra_norm:
    if c["year"] is not None:
        try:
            c["year"] = int(c["year"])
        except (ValueError, TypeError):
            c["year"] = None

for c in fha_norm:
    if c["year"] is not None:
        try:
            c["year"] = int(c["year"])
        except (ValueError, TypeError):
            c["year"] = None


def str_upper(val):
    """Safely get uppercase string from value that might be bool, None, or str."""
    if isinstance(val, bool):
        return "YES" if val else "NO"
    if val is None:
        return ""
    return str(val).upper()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def section(title):
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def subsection(title):
    print(f"\n--- {title} ---")


def pct(num, denom):
    if denom == 0:
        return "N/A"
    return f"{num}/{denom} ({100*num/denom:.1f}%)"


def print_counter(counter, title="", top_n=None):
    if title:
        print(f"  {title}:")
    items = counter.most_common(top_n)
    for k, v in items:
        print(f"    {k}: {v}")


def fisher_test(a, b, c, d, label=""):
    """2x2 contingency: [[a,b],[c,d]]. Returns p-value or None."""
    if not HAS_SCIPY:
        return None
    if min(a, b, c, d) < 0:
        return None
    try:
        odds, p = fisher_exact([[a, b], [c, d]])
        sig = " ***" if p < 0.001 else " **" if p < 0.01 else " *" if p < 0.05 else ""
        if label:
            print(f"    Fisher's exact test ({label}): OR={odds:.2f}, p={p:.4f}{sig}")
        return p
    except Exception:
        return None


def chi2_test(table, label=""):
    """Generic chi-square on a 2D table."""
    if not HAS_SCIPY:
        return None
    try:
        chi2, p, dof, expected = chi2_contingency(table)
        sig = " ***" if p < 0.001 else " **" if p < 0.01 else " *" if p < 0.05 else ""
        if label:
            print(f"    Chi-square ({label}): chi2={chi2:.2f}, dof={dof}, p={p:.4f}{sig}")
        return p
    except Exception:
        return None


# ============================================================
# CIRCUIT MAPPING
# ============================================================

COURT_TO_CIRCUIT = {
    # Circuit courts
    "1st Cir.": "1st", "2nd Cir.": "2nd", "2d Cir.": "2nd", "3rd Cir.": "3rd",
    "4th Cir.": "4th", "5th Cir.": "5th", "6th Cir.": "6th", "7th Cir.": "7th",
    "8th Cir.": "8th", "9th Cir.": "9th", "10th Cir.": "10th", "11th Cir.": "11th",
    "D.C. Cir.": "DC",
    # District courts by state (approximate mapping)
    "D.N.J.": "3rd", "E.D. Pa.": "3rd", "W.D. Pa.": "3rd", "M.D. Pa.": "3rd", "D. Del.": "3rd",
    "S.D.N.Y.": "2nd", "E.D.N.Y.": "2nd", "N.D.N.Y.": "2nd", "W.D.N.Y.": "2nd",
    "D. Conn.": "2nd", "D. Vt.": "2nd",
    "D. Mass.": "1st", "D.R.I.": "1st", "D.N.H.": "1st", "D. Me.": "1st", "D.P.R.": "1st",
    "E.D. Va.": "4th", "W.D. Va.": "4th", "D. Md.": "4th", "D.S.C.": "4th",
    "M.D.N.C.": "4th", "W.D.N.C.": "4th", "E.D.N.C.": "4th",
    "N.D. Tex.": "5th", "S.D. Tex.": "5th", "E.D. Tex.": "5th", "W.D. Tex.": "5th",
    "E.D. La.": "5th", "W.D. La.": "5th", "M.D. La.": "5th", "S.D. Miss.": "5th", "N.D. Miss.": "5th",
    "N.D. Ill.": "7th", "S.D. Ill.": "7th", "C.D. Ill.": "7th",
    "E.D. Wis.": "7th", "W.D. Wis.": "7th", "N.D. Ind.": "7th", "S.D. Ind.": "7th",
    "E.D. Mich.": "6th", "W.D. Mich.": "6th", "N.D. Ohio": "6th", "S.D. Ohio": "6th",
    "E.D. Ky.": "6th", "W.D. Ky.": "6th", "E.D. Tenn.": "6th", "W.D. Tenn.": "6th", "M.D. Tenn.": "6th",
    "D. Minn.": "8th", "E.D. Mo.": "8th", "W.D. Mo.": "8th", "D. Neb.": "8th",
    "N.D. Iowa": "8th", "S.D. Iowa": "8th", "D.S.D.": "8th", "D.N.D.": "8th", "E.D. Ark.": "8th", "W.D. Ark.": "8th",
    "C.D. Cal.": "9th", "N.D. Cal.": "9th", "S.D. Cal.": "9th", "E.D. Cal.": "9th",
    "D. Or.": "9th", "W.D. Wash.": "9th", "E.D. Wash.": "9th", "D. Ariz.": "9th",
    "D. Nev.": "9th", "D. Idaho": "9th", "D. Mont.": "9th", "D. Alaska": "9th", "D. Haw.": "9th",
    "D. Colo.": "10th", "D. Kan.": "10th", "D. Utah": "10th", "D.N.M.": "10th",
    "N.D. Okla.": "10th", "W.D. Okla.": "10th", "E.D. Okla.": "10th", "D. Wyo.": "10th",
    "N.D. Ga.": "11th", "M.D. Ga.": "11th", "S.D. Ga.": "11th",
    "N.D. Fla.": "11th", "M.D. Fla.": "11th", "S.D. Fla.": "11th",
    "N.D. Ala.": "11th", "M.D. Ala.": "11th", "S.D. Ala.": "11th",
    "D.D.C.": "DC",
}


def get_circuit_ra(case):
    court = case.get("court", "")
    return COURT_TO_CIRCUIT.get(court, "Unknown")


def get_circuit_fha(case):
    circ = case.get("circuit", "")
    if circ:
        # Normalize: "9th Circuit" -> "9th", "D.C. Circuit" -> "DC"
        circ = circ.replace(" Circuit", "").replace("D.C.", "DC")
        return circ
    court = case.get("court", "")
    # Try mapping from court name
    for key, val in COURT_TO_CIRCUIT.items():
        if key.lower() in court.lower():
            return val
    # Try to extract from court string
    if "ninth" in court.lower() or "9th" in court.lower():
        return "9th"
    if "second" in court.lower() or "2nd" in court.lower():
        return "2nd"
    return "Unknown"


# Outcome normalization
def norm_outcome_ra(o):
    o = o.upper().strip()
    if "PLAINTIFF" in o:
        return "PLAINTIFF_WIN"
    if "DEFENDANT" in o:
        return "DEFENDANT_WIN"
    if "MIXED" in o:
        return "MIXED"
    if "SETTLEMENT" in o:
        return "SETTLEMENT"
    return o


def norm_outcome_fha(o):
    o = o.lower().strip()
    if "plaintiff" in o:
        return "PLAINTIFF_WIN"
    if "defendant" in o:
        return "DEFENDANT_WIN"
    if "mixed" in o:
        return "MIXED"
    if "settlement" in o:
        return "SETTLEMENT"
    return o.upper()


# ============================================================
# STRUCTURE EXPLORATION
# ============================================================

section("DATABASE STRUCTURE EXPLORATION")

subsection("RA Database (3604) - Sample Record Fields")
if ra_norm:
    for k, v in ra_norm[0].items():
        print(f"  {k}: {repr(v)[:80]}")

subsection("FHA Database (Pilot) - Sample Record Fields")
if fha_norm:
    for k, v in fha_norm[0].items():
        print(f"  {k}: {repr(v)[:80]}")


# ############################################################
#  SECTION 1: RA DATABASE ANALYSIS
# ############################################################

section("1. RA DATABASE (3604) - BASIC DESCRIPTIVES")

print(f"\nTotal cases: {len(ra_norm)}")

# Date range
ra_years = [c["year"] for c in ra_norm if c["year"]]
print(f"Year range: {min(ra_years)} - {max(ra_years)}")

subsection("Distribution by Year")
year_counts_ra = Counter(ra_years)
for y in sorted(year_counts_ra):
    print(f"  {y}: {year_counts_ra[y]}")

subsection("Distribution by Accommodation Type (Primary)")
accom_counts = Counter(c["accommodation_primary"] for c in ra_norm)
print_counter(accom_counts)

subsection("Distribution by Defendant Type")
def_counts_ra = Counter(c["defendant_type"] for c in ra_norm)
print_counter(def_counts_ra)

subsection("Distribution by Plaintiff Type")
pl_counts_ra = Counter(c["plaintiff_type"] for c in ra_norm)
print_counter(pl_counts_ra)

subsection("Distribution by Disability Category")
dis_counts_ra = Counter(c["disability_category"] for c in ra_norm if c["disability_category"])
print_counter(dis_counts_ra)

subsection("Distribution by Outcome")
outcome_counts_ra = Counter(norm_outcome_ra(c["outcome"]) for c in ra_norm if c["outcome"])
print_counter(outcome_counts_ra)
total_decided_ra = sum(outcome_counts_ra.values())
pw_ra = outcome_counts_ra.get("PLAINTIFF_WIN", 0)
dw_ra = outcome_counts_ra.get("DEFENDANT_WIN", 0)
mx_ra = outcome_counts_ra.get("MIXED", 0)
print(f"\n  Plaintiff win rate: {pct(pw_ra, total_decided_ra)}")
print(f"  Defendant win rate: {pct(dw_ra, total_decided_ra)}")
print(f"  Mixed: {pct(mx_ra, total_decided_ra)}")

subsection("Distribution by Court / Circuit")
circuit_counts_ra = Counter(get_circuit_ra(c) for c in ra_norm)
print_counter(circuit_counts_ra)

subsection("Interactive Process Discussion")
ip_yes = sum(1 for c in ra_norm if str_upper(c.get("interactive_process_discussed", "")) == "YES")
ip_no = len(ra_norm) - ip_yes
print(f"  Discussed: {ip_yes} ({100*ip_yes/len(ra_norm):.1f}%)")
print(f"  Not discussed: {ip_no}")

subsection("Delay as Denial")
dad_yes = sum(1 for c in ra_norm if str_upper(c.get("delay_as_denial", "")) == "YES")
print(f"  Delay as denial found: {dad_yes} ({100*dad_yes/len(ra_norm):.1f}%)")

subsection("Win Rates by RA Subcategory (Accommodation Type)")
accom_outcomes = defaultdict(lambda: Counter())
for c in ra_norm:
    at = c["accommodation_primary"]
    oc = norm_outcome_ra(c["outcome"]) if c["outcome"] else None
    if oc:
        accom_outcomes[at][oc] += 1

for at in sorted(accom_outcomes):
    cts = accom_outcomes[at]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {at}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}, Mixed={pct(mx,total)}")

subsection("Win Rates by Disability Category (RA DB)")
dis_outcomes_ra = defaultdict(lambda: Counter())
for c in ra_norm:
    dc = c["disability_category"] if c["disability_category"] else "UNKNOWN"
    oc = norm_outcome_ra(c["outcome"]) if c["outcome"] else None
    if oc:
        dis_outcomes_ra[dc][oc] += 1

for dc in sorted(dis_outcomes_ra):
    cts = dis_outcomes_ra[dc]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    print(f"  {dc}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}")

subsection("Win Rates by Defendant Type (RA DB)")
def_outcomes_ra = defaultdict(lambda: Counter())
for c in ra_norm:
    dt = c["defendant_type"]
    oc = norm_outcome_ra(c["outcome"]) if c["outcome"] else None
    if oc:
        def_outcomes_ra[dt][oc] += 1

for dt in sorted(def_outcomes_ra):
    cts = def_outcomes_ra[dt]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    print(f"  {dt}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}")


# ############################################################
#  SECTION 2: FHA PILOT DATABASE ANALYSIS
# ############################################################

section("2. FHA PILOT DATABASE - BASIC DESCRIPTIVES")

print(f"\nTotal cases: {len(fha_norm)}")

fha_years = [c["year"] for c in fha_norm if c["year"]]
print(f"Year range: {min(fha_years)} - {max(fha_years)}")

subsection("Distribution by Year")
year_counts_fha = Counter(fha_years)
for y in sorted(year_counts_fha):
    print(f"  {y}: {year_counts_fha[y]}")

subsection("Distribution by Primary Protected Class")
pc_counts = Counter(c["primary_protected_class"] for c in fha_norm if c["primary_protected_class"])
print_counter(pc_counts)

subsection("Distribution by Primary Claim Type")
ct_counts = Counter(c["primary_claim_type"] for c in fha_norm if c["primary_claim_type"])
print_counter(ct_counts)

subsection("Distribution by Outcome")
outcome_counts_fha = Counter(norm_outcome_fha(c["outcome"]) for c in fha_norm if c["outcome"])
print_counter(outcome_counts_fha)
total_decided_fha = sum(outcome_counts_fha.values())
pw_fha = outcome_counts_fha.get("PLAINTIFF_WIN", 0)
dw_fha = outcome_counts_fha.get("DEFENDANT_WIN", 0)
mx_fha = outcome_counts_fha.get("MIXED", 0)
print(f"\n  Plaintiff win rate: {pct(pw_fha, total_decided_fha)}")
print(f"  Defendant win rate: {pct(dw_fha, total_decided_fha)}")
print(f"  Mixed: {pct(mx_fha, total_decided_fha)}")

subsection("Distribution by Primary Defendant Type")
fha_def_counts = Counter(c["primary_defendant_type"] for c in fha_norm if c["primary_defendant_type"])
print_counter(fha_def_counts)

subsection("Distribution by Plaintiff Type")
fha_pl_counts = Counter(c["plaintiff_type"] for c in fha_norm if c["plaintiff_type"])
print_counter(fha_pl_counts)

subsection("Distribution by Circuit")
circuit_counts_fha = Counter(get_circuit_fha(c) for c in fha_norm)
print_counter(circuit_counts_fha)

subsection("Distribution by Procedural Posture")
pp_counts = Counter(c["procedural_posture"] for c in fha_norm if c["procedural_posture"])
print_counter(pp_counts)

subsection("Special Case Flags")
print(f"  Design & Construction claims: {sum(1 for c in fha_norm if c['design_construction_claim'])}")
print(f"  Assistance animal involved: {sum(1 for c in fha_norm if c['assistance_animal_involved'])}")
print(f"  Zoning/Land use: {sum(1 for c in fha_norm if c['zoning_land_use_involved'])}")
print(f"  Group home siting: {sum(1 for c in fha_norm if c['group_home_siting_involved'])}")
print(f"  Voucher/SOI discrimination: {sum(1 for c in fha_norm if c['voucher_soi_discrimination'])}")
print(f"  Standing challenged: {sum(1 for c in fha_norm if c['standing_challenged'])}")
print(f"  Intersectional claims: {sum(1 for c in fha_norm if c['intersectional_claim'])}")


# ############################################################
#  SECTION 3: DISABILITY-SPECIFIC ANALYSIS (FHA DB)
# ############################################################

section("3. DISABILITY-SPECIFIC ANALYSIS (FHA PILOT DB)")

fha_disability = [c for c in fha_norm if "disability" in [pc.lower() for pc in c["protected_classes"]]]
fha_disability_primary = [c for c in fha_norm if c["primary_protected_class"].lower() == "disability"]

print(f"\nCases involving disability (any): {len(fha_disability)} of {len(fha_norm)} ({100*len(fha_disability)/len(fha_norm):.1f}%)")
print(f"Cases with disability as PRIMARY class: {len(fha_disability_primary)} of {len(fha_norm)} ({100*len(fha_disability_primary)/len(fha_norm):.1f}%)")

subsection("Disability Category Distribution (FHA DB)")
dis_cat_fha = Counter(c["disability_category"] for c in fha_disability if c["disability_category"])
print_counter(dis_cat_fha)

subsection("RA Subcategory Distribution (FHA DB)")
ra_sub_fha = Counter(c["ra_subcategory"] for c in fha_norm if c["ra_subcategory"])
print_counter(ra_sub_fha)

subsection("Win Rates: Disability vs Non-Disability (FHA DB)")
dis_outcomes = Counter(norm_outcome_fha(c["outcome"]) for c in fha_disability if c["outcome"])
non_dis = [c for c in fha_norm if "disability" not in [pc.lower() for pc in c["protected_classes"]]]
non_dis_outcomes = Counter(norm_outcome_fha(c["outcome"]) for c in non_dis if c["outcome"])

dis_total = sum(dis_outcomes.values())
dis_pw = dis_outcomes.get("PLAINTIFF_WIN", 0)
dis_dw = dis_outcomes.get("DEFENDANT_WIN", 0)
non_total = sum(non_dis_outcomes.values())
non_pw = non_dis_outcomes.get("PLAINTIFF_WIN", 0)
non_dw = non_dis_outcomes.get("DEFENDANT_WIN", 0)

print(f"  Disability cases: P_win={pct(dis_pw, dis_total)}, D_win={pct(dis_dw, dis_total)}")
print(f"  Non-disability cases: P_win={pct(non_pw, non_total)}, D_win={pct(non_dw, non_total)}")

if dis_total > 0 and non_total > 0:
    fisher_test(dis_pw, dis_total - dis_pw, non_pw, non_total - non_pw,
                "Disability vs Non-disability plaintiff win rate")

subsection("Win Rates by Claim Type (Disability cases, FHA DB)")
claim_outcomes_fha = defaultdict(lambda: Counter())
for c in fha_disability:
    ct = c["primary_claim_type"] if c["primary_claim_type"] else "unknown"
    oc = norm_outcome_fha(c["outcome"]) if c["outcome"] else None
    if oc:
        claim_outcomes_fha[ct][oc] += 1

for ct in sorted(claim_outcomes_fha):
    cts = claim_outcomes_fha[ct]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {ct}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}, Mixed={pct(mx,total)}")

subsection("Win Rates by RA Subcategory (FHA DB)")
ra_sub_outcomes = defaultdict(lambda: Counter())
for c in fha_norm:
    sub = c["ra_subcategory"]
    if not sub:
        continue
    oc = norm_outcome_fha(c["outcome"]) if c["outcome"] else None
    if oc:
        ra_sub_outcomes[sub][oc] += 1

for sub in sorted(ra_sub_outcomes):
    cts = ra_sub_outcomes[sub]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {sub}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}, Mixed={pct(mx,total)}")


# ############################################################
#  SECTION 4: PRE/POST LOPER BRIGHT
# ############################################################

section("4. PRE/POST LOPER BRIGHT ANALYSIS (June 28, 2024)")

LOPER_BRIGHT_YEAR = 2024  # cases decided in or after mid-2024

# For a rough cut, we only have year. Cases in 2024 may be pre or post.
# We'll treat 2024+ as "post-Loper era" and <2024 as pre.
# A more precise approach would need exact decision dates.

subsection("RA Database - Pre/Post 2024")
ra_pre = [c for c in ra_norm if c["year"] and c["year"] < 2024]
ra_post = [c for c in ra_norm if c["year"] and c["year"] >= 2024]
print(f"  Pre-2024 cases: {len(ra_pre)}")
print(f"  2024+ cases: {len(ra_post)}")

ra_pre_out = Counter(norm_outcome_ra(c["outcome"]) for c in ra_pre if c["outcome"])
ra_post_out = Counter(norm_outcome_ra(c["outcome"]) for c in ra_post if c["outcome"])

ra_pre_total = sum(ra_pre_out.values())
ra_post_total = sum(ra_post_out.values())
ra_pre_pw = ra_pre_out.get("PLAINTIFF_WIN", 0)
ra_post_pw = ra_post_out.get("PLAINTIFF_WIN", 0)

print(f"  Pre-2024: P_win={pct(ra_pre_pw, ra_pre_total)}")
print(f"  2024+: P_win={pct(ra_post_pw, ra_post_total)}")

if ra_pre_total > 0 and ra_post_total > 0:
    fisher_test(ra_pre_pw, ra_pre_total - ra_pre_pw,
                ra_post_pw, ra_post_total - ra_post_pw,
                "RA DB Pre vs Post 2024 plaintiff win rate")

subsection("FHA Database - Pre/Post 2024")
fha_pre = [c for c in fha_norm if c["year"] and c["year"] < 2024]
fha_post = [c for c in fha_norm if c["year"] and c["year"] >= 2024]
print(f"  Pre-2024 cases: {len(fha_pre)}")
print(f"  2024+ cases: {len(fha_post)}")

fha_pre_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_pre if c["outcome"])
fha_post_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_post if c["outcome"])

fha_pre_total = sum(fha_pre_out.values())
fha_post_total = sum(fha_post_out.values())
fha_pre_pw = fha_pre_out.get("PLAINTIFF_WIN", 0)
fha_post_pw = fha_post_out.get("PLAINTIFF_WIN", 0)

print(f"  Pre-2024: P_win={pct(fha_pre_pw, fha_pre_total)}, outcomes: {dict(fha_pre_out)}")
print(f"  2024+: P_win={pct(fha_post_pw, fha_post_total)}, outcomes: {dict(fha_post_out)}")

if fha_pre_total > 0 and fha_post_total > 0:
    fisher_test(fha_pre_pw, fha_pre_total - fha_pre_pw,
                fha_post_pw, fha_post_total - fha_post_pw,
                "FHA DB Pre vs Post 2024 plaintiff win rate")

subsection("Disability Cases Pre/Post 2024 (FHA DB)")
fha_dis_pre = [c for c in fha_disability if c["year"] and c["year"] < 2024]
fha_dis_post = [c for c in fha_disability if c["year"] and c["year"] >= 2024]
print(f"  Pre-2024 disability: {len(fha_dis_pre)}")
print(f"  2024+ disability: {len(fha_dis_post)}")

dis_pre_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_dis_pre if c["outcome"])
dis_post_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_dis_post if c["outcome"])
dis_pre_t = sum(dis_pre_out.values())
dis_post_t = sum(dis_post_out.values())
dis_pre_pw = dis_pre_out.get("PLAINTIFF_WIN", 0)
dis_post_pw = dis_post_out.get("PLAINTIFF_WIN", 0)

print(f"  Pre-2024: P_win={pct(dis_pre_pw, dis_pre_t)}")
print(f"  2024+: P_win={pct(dis_post_pw, dis_post_t)}")

if dis_pre_t > 0 and dis_post_t > 0:
    fisher_test(dis_pre_pw, dis_pre_t - dis_pre_pw,
                dis_post_pw, dis_post_t - dis_post_pw,
                "Disability pre vs post 2024")

subsection("Claim Type Distribution Shift Pre/Post 2024 (FHA DB)")
pre_claims = Counter(c["primary_claim_type"] for c in fha_pre if c["primary_claim_type"])
post_claims = Counter(c["primary_claim_type"] for c in fha_post if c["primary_claim_type"])
all_claims = sorted(set(list(pre_claims.keys()) + list(post_claims.keys())))
print(f"  {'Claim Type':<40} {'Pre-2024':>10} {'2024+':>10}")
for cl in all_claims:
    pre_n = pre_claims.get(cl, 0)
    post_n = post_claims.get(cl, 0)
    pre_pct = f"{100*pre_n/len(fha_pre):.1f}%" if fha_pre else "N/A"
    post_pct = f"{100*post_n/len(fha_post):.1f}%" if fha_post else "N/A"
    print(f"  {cl:<40} {pre_n:>4} ({pre_pct:>5}) {post_n:>4} ({post_pct:>5})")


# ############################################################
#  SECTION 5: IQBAL / TWOMBLY ANALYSIS (FHA DB)
# ############################################################

section("5. IQBAL / TWOMBLY ANALYSIS (FHA PILOT DB)")

def cites_iqbal_twombly(case):
    """Check if case cites Iqbal or Twombly."""
    cited = case.get("key_cases_cited", [])
    text = " ".join(cited).lower() if cited else ""
    detail = (case.get("outcome_detail", "") or "").lower()
    summary = (case.get("brief_summary", "") or "").lower()
    combined = text + " " + detail + " " + summary
    has_iqbal = "iqbal" in combined
    has_twombly = "twombly" in combined
    return has_iqbal or has_twombly

fha_iqbal = [c for c in fha_norm if cites_iqbal_twombly(c)]
fha_no_iqbal = [c for c in fha_norm if not cites_iqbal_twombly(c)]

print(f"\nCases citing Iqbal/Twombly: {len(fha_iqbal)} of {len(fha_norm)} ({100*len(fha_iqbal)/len(fha_norm):.1f}%)")

subsection("Outcomes: Iqbal/Twombly cited vs not")
iq_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_iqbal if c["outcome"])
no_iq_out = Counter(norm_outcome_fha(c["outcome"]) for c in fha_no_iqbal if c["outcome"])

iq_total = sum(iq_out.values())
no_iq_total = sum(no_iq_out.values())
iq_dw = iq_out.get("DEFENDANT_WIN", 0)
no_iq_dw = no_iq_out.get("DEFENDANT_WIN", 0)
iq_pw = iq_out.get("PLAINTIFF_WIN", 0)
no_iq_pw = no_iq_out.get("PLAINTIFF_WIN", 0)

print(f"  Iqbal/Twombly cited: n={iq_total}, D_win={pct(iq_dw, iq_total)}, P_win={pct(iq_pw, iq_total)}")
print(f"  Not cited: n={no_iq_total}, D_win={pct(no_iq_dw, no_iq_total)}, P_win={pct(no_iq_pw, no_iq_total)}")

if iq_total > 0 and no_iq_total > 0:
    fisher_test(iq_dw, iq_total - iq_dw, no_iq_dw, no_iq_total - no_iq_dw,
                "Defendant win rate: Iqbal cited vs not")

subsection("MTD Outcomes (FHA DB)")
mtd_cases = [c for c in fha_norm if "motion_to_dismiss" in (c["procedural_posture"] or "").lower()
             or "12(b)(6)" in (c["procedural_posture"] or "").lower()
             or "dismiss" in (c["procedural_posture"] or "").lower()]
print(f"  MTD cases: {len(mtd_cases)}")
mtd_out = Counter(norm_outcome_fha(c["outcome"]) for c in mtd_cases if c["outcome"])
mtd_total = sum(mtd_out.values())
print(f"  Outcomes: {dict(mtd_out)}")
if mtd_total:
    print(f"  Dismissal (defendant win) rate: {pct(mtd_out.get('DEFENDANT_WIN',0), mtd_total)}")

subsection("MTD + Iqbal/Twombly")
mtd_iq = [c for c in mtd_cases if cites_iqbal_twombly(c)]
mtd_no_iq = [c for c in mtd_cases if not cites_iqbal_twombly(c)]
mtd_iq_out = Counter(norm_outcome_fha(c["outcome"]) for c in mtd_iq if c["outcome"])
mtd_no_iq_out = Counter(norm_outcome_fha(c["outcome"]) for c in mtd_no_iq if c["outcome"])

mtd_iq_t = sum(mtd_iq_out.values())
mtd_no_iq_t = sum(mtd_no_iq_out.values())
mtd_iq_dw = mtd_iq_out.get("DEFENDANT_WIN", 0)
mtd_no_iq_dw = mtd_no_iq_out.get("DEFENDANT_WIN", 0)

print(f"  MTD + Iqbal cited: n={mtd_iq_t}, D_win={pct(mtd_iq_dw, mtd_iq_t)}")
print(f"  MTD + no Iqbal: n={mtd_no_iq_t}, D_win={pct(mtd_no_iq_dw, mtd_no_iq_t)}")

if mtd_iq_t > 0 and mtd_no_iq_t > 0:
    fisher_test(mtd_iq_dw, mtd_iq_t - mtd_iq_dw,
                mtd_no_iq_dw, mtd_no_iq_t - mtd_no_iq_dw,
                "MTD dismissal: Iqbal cited vs not")


# ############################################################
#  SECTION 6: CIRCUIT ANALYSIS
# ############################################################

section("6. CIRCUIT ANALYSIS")

subsection("RA Database - Win Rates by Circuit")
circ_outcomes_ra = defaultdict(lambda: Counter())
for c in ra_norm:
    circ = get_circuit_ra(c)
    oc = norm_outcome_ra(c["outcome"]) if c["outcome"] else None
    if oc:
        circ_outcomes_ra[circ][oc] += 1

print(f"  {'Circuit':<12} {'N':>4} {'P_Win':>12} {'D_Win':>12} {'Mixed':>12}")
for circ in sorted(circ_outcomes_ra, key=lambda x: x if x != "Unknown" else "ZZZ"):
    cts = circ_outcomes_ra[circ]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {circ:<12} {total:>4} {pct(pw,total):>12} {pct(dw,total):>12} {pct(mx,total):>12}")

subsection("FHA Database - Win Rates by Circuit (Disability Cases)")
circ_outcomes_fha_dis = defaultdict(lambda: Counter())
for c in fha_disability:
    circ = get_circuit_fha(c)
    oc = norm_outcome_fha(c["outcome"]) if c["outcome"] else None
    if oc:
        circ_outcomes_fha_dis[circ][oc] += 1

print(f"  {'Circuit':<12} {'N':>4} {'P_Win':>12} {'D_Win':>12} {'Mixed':>12}")
for circ in sorted(circ_outcomes_fha_dis, key=lambda x: x if x != "Unknown" else "ZZZ"):
    cts = circ_outcomes_fha_dis[circ]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {circ:<12} {total:>4} {pct(pw,total):>12} {pct(dw,total):>12} {pct(mx,total):>12}")

subsection("FHA Database - Win Rates by Circuit (All Cases)")
circ_outcomes_fha_all = defaultdict(lambda: Counter())
for c in fha_norm:
    circ = get_circuit_fha(c)
    oc = norm_outcome_fha(c["outcome"]) if c["outcome"] else None
    if oc:
        circ_outcomes_fha_all[circ][oc] += 1

print(f"  {'Circuit':<12} {'N':>4} {'P_Win':>12} {'D_Win':>12} {'Mixed':>12}")
for circ in sorted(circ_outcomes_fha_all, key=lambda x: x if x != "Unknown" else "ZZZ"):
    cts = circ_outcomes_fha_all[circ]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {circ:<12} {total:>4} {pct(pw,total):>12} {pct(dw,total):>12} {pct(mx,total):>12}")


# ############################################################
#  SECTION 7: DESIGN & CONSTRUCTION
# ############################################################

section("7. DESIGN & CONSTRUCTION ANALYSIS (FHA DB)")

dc_cases = [c for c in fha_norm if c["design_construction_claim"]]
print(f"\nD&C cases: {len(dc_cases)} of {len(fha_norm)} ({100*len(dc_cases)/len(fha_norm):.1f}%)")

dc_out = Counter(norm_outcome_fha(c["outcome"]) for c in dc_cases if c["outcome"])
dc_total = sum(dc_out.values())
dc_pw = dc_out.get("PLAINTIFF_WIN", 0)
dc_dw = dc_out.get("DEFENDANT_WIN", 0)
print(f"  Outcomes: {dict(dc_out)}")
print(f"  P_win rate: {pct(dc_pw, dc_total)}")

# Compare D&C vs RA vs other
ra_fha_cases = [c for c in fha_norm if "reasonable_accommodation" in (c["primary_claim_type"] or "").lower()
                or c["ra_subcategory"]]
other_fha = [c for c in fha_norm if c not in dc_cases and c not in ra_fha_cases]

ra_fha_out = Counter(norm_outcome_fha(c["outcome"]) for c in ra_fha_cases if c["outcome"])
other_fha_out = Counter(norm_outcome_fha(c["outcome"]) for c in other_fha if c["outcome"])

ra_fha_t = sum(ra_fha_out.values())
ra_fha_pw = ra_fha_out.get("PLAINTIFF_WIN", 0)
other_t = sum(other_fha_out.values())
other_pw = other_fha_out.get("PLAINTIFF_WIN", 0)

print(f"\n  D&C win rate: {pct(dc_pw, dc_total)}")
print(f"  RA win rate (FHA DB): {pct(ra_fha_pw, ra_fha_t)}")
print(f"  Other claims win rate: {pct(other_pw, other_t)}")


# ############################################################
#  SECTION 8: ASSISTANCE ANIMAL / ESA
# ############################################################

section("8. ASSISTANCE ANIMAL / ESA ANALYSIS")

subsection("FHA Database - Assistance Animal Cases")
aa_fha = [c for c in fha_norm if c["assistance_animal_involved"]]
print(f"  Assistance animal cases: {len(aa_fha)} of {len(fha_norm)} ({100*len(aa_fha)/len(fha_norm):.1f}%)")

aa_out = Counter(norm_outcome_fha(c["outcome"]) for c in aa_fha if c["outcome"])
aa_total = sum(aa_out.values())
aa_pw = aa_out.get("PLAINTIFF_WIN", 0)
aa_dw = aa_out.get("DEFENDANT_WIN", 0)
print(f"  Outcomes: {dict(aa_out)}")
print(f"  P_win rate: {pct(aa_pw, aa_total)}")

# Defendant types for AA cases
aa_def = Counter(c["primary_defendant_type"] for c in aa_fha)
print(f"  Defendant types:")
print_counter(aa_def)

# AA detail
aa_detail = Counter(c["assistance_animal_detail"] for c in aa_fha if c["assistance_animal_detail"])
if aa_detail:
    print(f"  Assistance animal detail:")
    print_counter(aa_detail)

subsection("RA Database - ESA/Assistance Animal Cases")
esa_ra = [c for c in ra_norm if "ESA" in str_upper(c["accommodation_primary"])
          or "ASSISTANCE_ANIMAL" in str_upper(c["accommodation_primary"])
          or "EMOTIONAL" in str_upper(c.get("accommodation_description", ""))
          or "SERVICE_ANIMAL" in str_upper(c["accommodation_primary"])
          or "SERVICE ANIMAL" in str_upper(c.get("accommodation_description", ""))]
print(f"  ESA/AA cases in RA DB: {len(esa_ra)}")

esa_out = Counter(norm_outcome_ra(c["outcome"]) for c in esa_ra if c["outcome"])
esa_total = sum(esa_out.values())
esa_pw = esa_out.get("PLAINTIFF_WIN", 0)
esa_dw = esa_out.get("DEFENDANT_WIN", 0)
print(f"  Outcomes: {dict(esa_out)}")
print(f"  P_win rate: {pct(esa_pw, esa_total)}")

esa_def = Counter(c["defendant_type"] for c in esa_ra)
print(f"  Defendant types:")
print_counter(esa_def)

subsection("Combined ESA/AA from RA DB accommodation types")
# Check all accommodation types containing ESA or animal
for at, cnt in accom_counts.items():
    if "ESA" in at.upper() or "ANIMAL" in at.upper():
        print(f"  {at}: {cnt} cases")


# ############################################################
#  SECTION 9: CROSS-DATABASE COMPARISON
# ############################################################

section("9. CROSS-DATABASE COMPARISON")

subsection("Overlap Detection")
# Try matching on case names
ra_names = set(c["case_name"].strip().lower() for c in ra_norm if c["case_name"])
fha_names = set(c["case_name"].strip().lower() for c in fha_norm if c["case_name"])
overlap_names = ra_names & fha_names
print(f"  RA database case count: {len(ra_norm)}")
print(f"  FHA database case count: {len(fha_norm)}")
print(f"  Exact name matches: {len(overlap_names)}")

# Fuzzy overlap: check source_file overlap
ra_sources = set(c["source_file"].strip().lower() for c in ra_norm if c["source_file"])
fha_sources = set(c["source_file"].strip().lower() for c in fha_norm if c["source_file"])
overlap_sources = ra_sources & fha_sources
print(f"  Exact source_file matches: {len(overlap_sources)}")

# Partial name matching
partial_matches = 0
for rn in ra_names:
    for fn in fha_names:
        # Check if substantial part of the name matches
        rn_words = set(rn.split())
        fn_words = set(fn.split())
        if len(rn_words & fn_words) >= 3 and len(rn_words & fn_words) / max(len(rn_words), len(fn_words)) > 0.5:
            partial_matches += 1
            break
print(f"  Partial name matches (>=3 shared words, >50% overlap): {partial_matches}")

if overlap_names:
    print(f"\n  Overlapping case names (sample up to 10):")
    for name in sorted(list(overlap_names))[:10]:
        print(f"    - {name}")

subsection("Combined Year Distribution")
all_years = ra_years + fha_years
combined_years = Counter(all_years)
print(f"  Combined unique years: {sorted(combined_years.keys())}")
print(f"  Combined total cases (before dedup): {len(ra_norm) + len(fha_norm)}")
print(f"  Estimated unique cases: {len(ra_norm) + len(fha_norm) - len(overlap_names) - partial_matches}")

subsection("Database Scope Comparison")
print(f"  RA DB: All cases are disability/RA-focused (§3604(f)(3)(B))")
print(f"  FHA DB: Covers all protected classes and claim types")
print(f"  RA DB year range: {min(ra_years)}-{max(ra_years)}")
print(f"  FHA DB year range: {min(fha_years)}-{max(fha_years)}")

# Compare outcomes
print(f"\n  Overall plaintiff win rates:")
print(f"    RA DB: {pct(pw_ra, total_decided_ra)}")
print(f"    FHA DB (all): {pct(pw_fha, total_decided_fha)}")
print(f"    FHA DB (disability only): {pct(dis_pw, dis_total)}")


# ############################################################
#  SECTION 10: INTERACTIVE PROCESS & DELAY AS DENIAL (RA DB)
# ############################################################

section("10. INTERACTIVE PROCESS ANALYSIS (RA DB)")

ip_cases = [c for c in ra_norm if str_upper(c.get("interactive_process_discussed", "")) == "YES"]
no_ip_cases = [c for c in ra_norm if str_upper(c.get("interactive_process_discussed", "")) != "YES"]

ip_out = Counter(norm_outcome_ra(c["outcome"]) for c in ip_cases if c["outcome"])
no_ip_out = Counter(norm_outcome_ra(c["outcome"]) for c in no_ip_cases if c["outcome"])

ip_t = sum(ip_out.values())
no_ip_t = sum(no_ip_out.values())
ip_pw = ip_out.get("PLAINTIFF_WIN", 0)
no_ip_pw = no_ip_out.get("PLAINTIFF_WIN", 0)

print(f"\n  IP discussed: n={ip_t}, P_win={pct(ip_pw, ip_t)}")
print(f"  IP not discussed: n={no_ip_t}, P_win={pct(no_ip_pw, no_ip_t)}")

if ip_t > 0 and no_ip_t > 0:
    fisher_test(ip_pw, ip_t - ip_pw, no_ip_pw, no_ip_t - no_ip_pw,
                "Win rate: IP discussed vs not")

subsection("Delay as Denial - Outcomes")
dad_cases = [c for c in ra_norm if str_upper(c.get("delay_as_denial", "")) == "YES"]
dad_out = Counter(norm_outcome_ra(c["outcome"]) for c in dad_cases if c["outcome"])
dad_t = sum(dad_out.values())
dad_pw = dad_out.get("PLAINTIFF_WIN", 0)
print(f"  Delay-as-denial cases: n={dad_t}, P_win={pct(dad_pw, dad_t)}")
print(f"  Outcomes: {dict(dad_out)}")


# ############################################################
#  SECTION 11: RACE-DISABILITY INTERSECTION
# ############################################################

section("11. RACE-DISABILITY INTERSECTION")

subsection("RA Database")
race_yes = sum(1 for c in ra_norm if str_upper(c.get("race_mentioned", "")) == "YES")
dual_yes = sum(1 for c in ra_norm if str_upper(c.get("dual_basis_claim", "")) == "YES")
print(f"  Race mentioned: {race_yes} of {len(ra_norm)} ({100*race_yes/len(ra_norm):.1f}%)")
print(f"  Dual basis claims: {dual_yes} of {len(ra_norm)} ({100*dual_yes/len(ra_norm):.1f}%)")

subsection("FHA Database")
fha_intersectional = [c for c in fha_norm if c["intersectional_claim"]]
fha_dual = [c for c in fha_norm if c["dual_basis_claim"]]
print(f"  Intersectional claims: {len(fha_intersectional)} of {len(fha_norm)} ({100*len(fha_intersectional)/len(fha_norm):.1f}%)")
print(f"  Dual basis claims: {len(fha_dual)} of {len(fha_norm)} ({100*len(fha_dual)/len(fha_norm):.1f}%)")

# Race mentions in disability cases
dis_race = [c for c in fha_disability if c["race_mentions"]]
print(f"  Disability cases mentioning race: {len(dis_race)} of {len(fha_disability)} ({100*len(dis_race)/len(fha_disability):.1f}%)" if fha_disability else "")


# ############################################################
#  SECTION 12: PROCEDURAL POSTURE ANALYSIS
# ############################################################

section("12. PROCEDURAL POSTURE ANALYSIS")

subsection("RA Database - Outcomes by Procedural Posture")
pp_outcomes_ra = defaultdict(lambda: Counter())
for c in ra_norm:
    pp = c["procedural_posture"] if c["procedural_posture"] else "unknown"
    oc = norm_outcome_ra(c["outcome"]) if c["outcome"] else None
    if oc:
        pp_outcomes_ra[pp][oc] += 1

for pp in sorted(pp_outcomes_ra):
    cts = pp_outcomes_ra[pp]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {pp}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}, Mixed={pct(mx,total)}")

subsection("FHA Database - Outcomes by Procedural Posture")
pp_outcomes_fha = defaultdict(lambda: Counter())
for c in fha_norm:
    pp = c["procedural_posture"] if c["procedural_posture"] else "unknown"
    oc = norm_outcome_fha(c["outcome"]) if c["outcome"] else None
    if oc:
        pp_outcomes_fha[pp][oc] += 1

for pp in sorted(pp_outcomes_fha):
    cts = pp_outcomes_fha[pp]
    total = sum(cts.values())
    pw = cts.get("PLAINTIFF_WIN", 0)
    dw = cts.get("DEFENDANT_WIN", 0)
    mx = cts.get("MIXED", 0)
    print(f"  {pp}: n={total}, P_win={pct(pw,total)}, D_win={pct(dw,total)}, Mixed={pct(mx,total)}")


# ############################################################
#  SECTION 13: GOVERNMENT PLAINTIFFS
# ############################################################

section("13. GOVERNMENT vs PRIVATE PLAINTIFFS")

subsection("RA Database")
gov_ra = [c for c in ra_norm if "GOVERNMENT" in str_upper(c["plaintiff_type"]) or "DOJ" in str_upper(c["plaintiff_type"]) or "UNITED STATES" in str_upper(c["plaintiff_type"])]
priv_ra = [c for c in ra_norm if c not in gov_ra]

gov_out = Counter(norm_outcome_ra(c["outcome"]) for c in gov_ra if c["outcome"])
priv_out = Counter(norm_outcome_ra(c["outcome"]) for c in priv_ra if c["outcome"])
gov_t = sum(gov_out.values())
priv_t = sum(priv_out.values())
gov_pw = gov_out.get("PLAINTIFF_WIN", 0)
priv_pw = priv_out.get("PLAINTIFF_WIN", 0)

print(f"  Government plaintiffs: n={gov_t}, P_win={pct(gov_pw, gov_t)}")
print(f"  Private plaintiffs: n={priv_t}, P_win={pct(priv_pw, priv_t)}")

if gov_t > 0 and priv_t > 0:
    fisher_test(gov_pw, gov_t - gov_pw, priv_pw, priv_t - priv_pw,
                "Gov vs Private plaintiff win rate")

subsection("FHA Database")
gov_fha = [c for c in fha_norm if "government" in c["plaintiff_type"].lower() or "doj" in c["plaintiff_type"].lower()]
priv_fha = [c for c in fha_norm if c not in gov_fha]

gov_fha_out = Counter(norm_outcome_fha(c["outcome"]) for c in gov_fha if c["outcome"])
priv_fha_out = Counter(norm_outcome_fha(c["outcome"]) for c in priv_fha if c["outcome"])
gov_fha_t = sum(gov_fha_out.values())
priv_fha_t = sum(priv_fha_out.values())
gov_fha_pw = gov_fha_out.get("PLAINTIFF_WIN", 0)
priv_fha_pw = priv_fha_out.get("PLAINTIFF_WIN", 0)

print(f"  Government plaintiffs: n={gov_fha_t}, P_win={pct(gov_fha_pw, gov_fha_t)}")
print(f"  Private plaintiffs: n={priv_fha_t}, P_win={pct(priv_fha_pw, priv_fha_t)}")


# ############################################################
#  SECTION 14: NECESSITY STANDARD ANALYSIS (RA DB)
# ############################################################

section("14. NECESSITY STANDARD IN RA CASES")

# Check key holdings for necessity language
necessity_cases = []
for c in ra_norm:
    holding = (c.get("key_holding", "") or "").lower()
    if "necessar" in holding or "necessity" in holding or "indispensable" in holding:
        necessity_cases.append(c)

print(f"\nCases discussing necessity standard: {len(necessity_cases)} of {len(ra_norm)} ({100*len(necessity_cases)/len(ra_norm):.1f}%)")

nec_out = Counter(norm_outcome_ra(c["outcome"]) for c in necessity_cases if c["outcome"])
nec_t = sum(nec_out.values())
nec_pw = nec_out.get("PLAINTIFF_WIN", 0)
nec_dw = nec_out.get("DEFENDANT_WIN", 0)
print(f"  Outcomes: {dict(nec_out)}")
print(f"  P_win when necessity discussed: {pct(nec_pw, nec_t)}")

# Cases where necessity was the dispositive issue (defendant won on necessity)
nec_def_win = [c for c in necessity_cases
               if norm_outcome_ra(c["outcome"]) == "DEFENDANT_WIN"
               and ("not necessary" in (c.get("key_holding", "") or "").lower()
                    or "failed to establish" in (c.get("key_holding", "") or "").lower()
                    or "failed to show" in (c.get("key_holding", "") or "").lower())]
print(f"  Cases where plaintiff lost on necessity: {len(nec_def_win)}")


# ############################################################
#  TOP 10 FINDINGS
# ############################################################

section("TOP 10 MOST IMPORTANT FINDINGS FOR LAW REVIEW ARTICLE")

findings = []

# Collect key stats for ranking
findings.append(("Database scope", f"RA DB contains {len(ra_norm)} disability/RA cases ({min(ra_years)}-{max(ra_years)}); FHA DB contains {len(fha_norm)} cases across all protected classes ({min(fha_years)}-{max(fha_years)}). Combined unique dataset estimated at ~{len(ra_norm) + len(fha_norm) - len(overlap_names) - partial_matches} cases."))

findings.append(("Disability dominance", f"Disability is the primary protected class in {len(fha_disability_primary)} of {len(fha_norm)} FHA pilot cases ({100*len(fha_disability_primary)/len(fha_norm):.1f}%), confirming disability's outsized role in FHA litigation."))

findings.append(("Overall plaintiff win rates", f"RA DB: {pct(pw_ra, total_decided_ra)} plaintiff wins. FHA DB: {pct(pw_fha, total_decided_fha)} overall, {pct(dis_pw, dis_total)} for disability cases. Defendants prevail in the majority of decided cases."))

if ra_post_total > 0:
    findings.append(("Post-Loper Bright shift (RA)", f"Pre-2024 plaintiff win rate: {pct(ra_pre_pw, ra_pre_total)}. Post-2024: {pct(ra_post_pw, ra_post_total)}. {'Decline' if ra_post_pw/max(ra_post_total,1) < ra_pre_pw/max(ra_pre_total,1) else 'No decline'} in plaintiff success after Loper Bright era."))

if fha_post_total > 0:
    findings.append(("Post-Loper Bright shift (FHA)", f"Pre-2024: {pct(fha_pre_pw, fha_pre_total)}. Post-2024: {pct(fha_post_pw, fha_post_total)}. FHA DB shows {'decline' if fha_post_pw/max(fha_post_total,1) < fha_pre_pw/max(fha_pre_total,1) else 'no decline'} in plaintiff success."))

findings.append(("Iqbal/Twombly effect", f"{len(fha_iqbal)} of {len(fha_norm)} FHA cases cite Iqbal/Twombly ({100*len(fha_iqbal)/len(fha_norm):.1f}%). Defendant win rate when cited: {pct(iq_dw, iq_total)} vs {pct(no_iq_dw, no_iq_total)} when not cited."))

findings.append(("RA subcategory variation", "Win rates vary substantially by accommodation type. Key subcategories: " +
    "; ".join(f"{at}: P_win={pct(accom_outcomes[at].get('PLAINTIFF_WIN',0), sum(accom_outcomes[at].values()))}"
              for at in sorted(accom_outcomes) if sum(accom_outcomes[at].values()) >= 3)))

findings.append(("Interactive process", f"Interactive process discussed in {ip_t} RA cases. When discussed, P_win={pct(ip_pw, ip_t)}; when not discussed, P_win={pct(no_ip_pw, no_ip_t)}. Delay-as-denial found in {dad_t} cases with P_win={pct(dad_pw, dad_t)}."))

findings.append(("Design & Construction", f"D&C cases: {len(dc_cases)} in FHA DB. P_win rate: {pct(dc_pw, dc_total)}."))

findings.append(("ESA/Assistance Animals", f"FHA DB: {len(aa_fha)} assistance animal cases ({100*len(aa_fha)/len(fha_norm):.1f}%), P_win={pct(aa_pw, aa_total)}. RA DB: {len(esa_ra)} ESA/AA cases, P_win={pct(esa_pw, esa_total)}."))

findings.append(("Necessity standard", f"{len(necessity_cases)} RA cases explicitly discuss necessity ({100*len(necessity_cases)/len(ra_norm):.1f}%). When necessity is discussed, P_win={pct(nec_pw, nec_t)}. {len(nec_def_win)} cases where plaintiff lost specifically on necessity grounds."))

print()
for i, (title, detail) in enumerate(findings, 1):
    print(f"  {i}. [{title.upper()}]")
    print(f"     {detail}")
    print()

print("=" * 70)
print("  ANALYSIS COMPLETE")
print("=" * 70)
