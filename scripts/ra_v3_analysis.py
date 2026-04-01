#!/usr/bin/env python3
"""
Comprehensive Analysis of RAClassification_DB_v3.json
For Law Review Article: Disability Fair Housing Enforcement After Loper Bright
"""

import json
import sys
import re
from collections import Counter, defaultdict
from itertools import combinations

# ---------------------------------------------------------------------------
# Try to import scipy for Fisher's exact test; fall back gracefully
# ---------------------------------------------------------------------------
try:
    from scipy.stats import fisher_exact, chi2_contingency
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not installed. Fisher's exact tests will be skipped.\n")

# ===========================================================================
# LOAD DATA
# ===========================================================================
DATA_PATH = r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\RAClassification_DB_v3.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

print("=" * 80)
print("  RA v3 CASE DATABASE — COMPREHENSIVE ANALYSIS")
print("=" * 80)

# ===========================================================================
# 0. DATA EXPLORATION
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 0: DATA EXPLORATION")
print("=" * 80)

print(f"\nTotal cases loaded: {len(cases)}")

# All field names
all_keys = set()
for c in cases:
    all_keys.update(c.keys())
all_keys = sorted(all_keys)
print(f"\nTotal unique fields: {len(all_keys)}")
print("Fields:")
for k in all_keys:
    print(f"  - {k}")

# Schema consistency
field_counts = Counter()
for c in cases:
    for k in c.keys():
        field_counts[k] += 1

print("\nSchema consistency check (fields present in fewer than all records):")
inconsistent = False
for k in all_keys:
    if field_counts[k] != len(cases):
        print(f"  {k}: present in {field_counts[k]}/{len(cases)} records")
        inconsistent = True
if not inconsistent:
    print("  ALL fields present in ALL records — schema is consistent.")

# Sample 3 records
print("\n--- Sample Records (first 3) ---")
for i, c in enumerate(cases[:3]):
    print(f"\nRecord {i+1}:")
    for k, v in c.items():
        val = str(v)
        if len(val) > 120:
            val = val[:120] + "..."
        print(f"  {k}: {val}")


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def pct(n, total):
    """Return percentage string."""
    if total == 0:
        return "0.0%"
    return f"{100*n/total:.1f}%"

def print_table(rows, headers, title=""):
    """Print a formatted table."""
    if title:
        print(f"\n{title}")
        print("-" * len(title))
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in col_widths]))
    for row in rows:
        print(fmt.format(*[str(c) for c in row]))

def fisher_test(win_a, total_a, win_b, total_b, label=""):
    """Run Fisher's exact test and print result."""
    if not HAS_SCIPY:
        return None
    table = [[win_a, total_a - win_a],
             [win_b, total_b - win_b]]
    try:
        odds_ratio, p = fisher_exact(table)
        sig = ""
        if p < 0.05:
            sig = " *** STATISTICALLY SIGNIFICANT ***"
        elif p < 0.10:
            sig = " * marginally significant *"
        if label:
            print(f"  Fisher's exact test ({label}): OR={odds_ratio:.3f}, p={p:.4f}{sig}")
        return p
    except Exception as e:
        print(f"  Fisher's test error: {e}")
        return None

def is_plaintiff_win(outcome):
    return outcome in ("PLAINTIFF_WIN", "MIXED_PLAINTIFF_FAVORABLE")

def is_defendant_win(outcome):
    return outcome in ("DEFENDANT_WIN", "MIXED_DEFENDANT_FAVORABLE")

def win_rate_analysis(cases_subset, group_field, min_n=3):
    """Compute plaintiff win rates by a grouping field. Returns sorted rows."""
    groups = defaultdict(list)
    for c in cases_subset:
        val = c.get(group_field, "UNKNOWN")
        if val is None:
            val = "UNKNOWN"
        groups[val].append(c)

    rows = []
    for val, group_cases in sorted(groups.items()):
        total = len(group_cases)
        p_wins = sum(1 for c in group_cases if is_plaintiff_win(c["outcome"]))
        d_wins = sum(1 for c in group_cases if is_defendant_win(c["outcome"]))
        rows.append((val, total, p_wins, pct(p_wins, total), d_wins, pct(d_wins, total)))
    # Sort by plaintiff win rate descending
    rows.sort(key=lambda r: float(r[3].replace("%", "")), reverse=True)
    return rows

def extract_circuit(court):
    """Extract circuit from court string."""
    if not court:
        return "UNKNOWN"
    court = court.strip()
    def ordinal_circuit(n):
        """Convert number to proper circuit name."""
        n = int(n)
        if n == 1: return "1st Cir."
        if n == 2: return "2nd Cir."
        if n == 3: return "3rd Cir."
        return f"{n}th Cir."

    # Federal circuit courts
    circuit_patterns = [
        (r"^(\d+)(?:st|nd|rd|th|d)\s+Cir", lambda m: ordinal_circuit(m.group(1))),
        (r"^D\.C\.\s*Cir", lambda m: "D.C. Cir."),
        (r"^Fed\.\s*Cir", lambda m: "Fed. Cir."),
    ]
    for pat, fn in circuit_patterns:
        m = re.match(pat, court)
        if m:
            return fn(m)

    # District courts -> map to circuit
    district_to_circuit = {
        # 1st Circuit
        "D. Me.": "1st Cir.", "D. Mass.": "1st Cir.", "D.N.H.": "1st Cir.",
        "D.R.I.": "1st Cir.", "D.P.R.": "1st Cir.", "D. Mass": "1st Cir.",
        "D.Mass.": "1st Cir.", "D. Me": "1st Cir.", "D.Me.": "1st Cir.",
        "D.N.H": "1st Cir.", "D. N.H.": "1st Cir.", "D. R.I.": "1st Cir.",
        # 2nd Circuit
        "S.D.N.Y.": "2nd Cir.", "E.D.N.Y.": "2nd Cir.", "N.D.N.Y.": "2nd Cir.",
        "W.D.N.Y.": "2nd Cir.", "D. Conn.": "2nd Cir.", "D. Vt.": "2nd Cir.",
        "D.Conn.": "2nd Cir.", "D.Vt.": "2nd Cir.",
        # 3rd Circuit
        "D.N.J.": "3rd Cir.", "E.D. Pa.": "3rd Cir.", "W.D. Pa.": "3rd Cir.",
        "M.D. Pa.": "3rd Cir.", "D. Del.": "3rd Cir.", "D.V.I.": "3rd Cir.",
        "D. N.J.": "3rd Cir.", "E.D.Pa.": "3rd Cir.", "W.D.Pa.": "3rd Cir.",
        "M.D.Pa.": "3rd Cir.", "D.Del.": "3rd Cir.",
        # 4th Circuit
        "D. Md.": "4th Cir.", "E.D. Va.": "4th Cir.", "W.D. Va.": "4th Cir.",
        "D.S.C.": "4th Cir.", "E.D.N.C.": "4th Cir.", "M.D.N.C.": "4th Cir.",
        "W.D.N.C.": "4th Cir.", "S.D.W. Va.": "4th Cir.", "N.D.W. Va.": "4th Cir.",
        "D.Md.": "4th Cir.", "E.D.Va.": "4th Cir.", "W.D.Va.": "4th Cir.",
        "D. S.C.": "4th Cir.", "E.D. N.C.": "4th Cir.", "M.D. N.C.": "4th Cir.",
        "W.D. N.C.": "4th Cir.", "S.D. W.Va.": "4th Cir.", "N.D. W.Va.": "4th Cir.",
        "S.D.W.Va.": "4th Cir.", "N.D.W.Va.": "4th Cir.",
        # 5th Circuit
        "N.D. Tex.": "5th Cir.", "S.D. Tex.": "5th Cir.", "E.D. Tex.": "5th Cir.",
        "W.D. Tex.": "5th Cir.", "E.D. La.": "5th Cir.", "W.D. La.": "5th Cir.",
        "M.D. La.": "5th Cir.", "S.D. Miss.": "5th Cir.", "N.D. Miss.": "5th Cir.",
        "N.D.Tex.": "5th Cir.", "S.D.Tex.": "5th Cir.", "E.D.Tex.": "5th Cir.",
        "W.D.Tex.": "5th Cir.", "E.D.La.": "5th Cir.", "W.D.La.": "5th Cir.",
        "M.D.La.": "5th Cir.", "S.D.Miss.": "5th Cir.", "N.D.Miss.": "5th Cir.",
        # 6th Circuit
        "N.D. Ohio": "6th Cir.", "S.D. Ohio": "6th Cir.", "E.D. Mich.": "6th Cir.",
        "W.D. Mich.": "6th Cir.", "E.D. Ky.": "6th Cir.", "W.D. Ky.": "6th Cir.",
        "E.D. Tenn.": "6th Cir.", "M.D. Tenn.": "6th Cir.", "W.D. Tenn.": "6th Cir.",
        "N.D.Ohio": "6th Cir.", "S.D.Ohio": "6th Cir.", "E.D.Mich.": "6th Cir.",
        "W.D.Mich.": "6th Cir.", "E.D.Ky.": "6th Cir.", "W.D.Ky.": "6th Cir.",
        "E.D.Tenn.": "6th Cir.", "M.D.Tenn.": "6th Cir.", "W.D.Tenn.": "6th Cir.",
        # 7th Circuit
        "N.D. Ill.": "7th Cir.", "C.D. Ill.": "7th Cir.", "S.D. Ill.": "7th Cir.",
        "N.D. Ind.": "7th Cir.", "S.D. Ind.": "7th Cir.", "E.D. Wis.": "7th Cir.",
        "W.D. Wis.": "7th Cir.",
        "N.D.Ill.": "7th Cir.", "C.D.Ill.": "7th Cir.", "S.D.Ill.": "7th Cir.",
        "N.D.Ind.": "7th Cir.", "S.D.Ind.": "7th Cir.", "E.D.Wis.": "7th Cir.",
        "W.D.Wis.": "7th Cir.",
        # 8th Circuit
        "D. Minn.": "8th Cir.", "E.D. Mo.": "8th Cir.", "W.D. Mo.": "8th Cir.",
        "E.D. Ark.": "8th Cir.", "W.D. Ark.": "8th Cir.", "N.D. Iowa": "8th Cir.",
        "S.D. Iowa": "8th Cir.", "D. Neb.": "8th Cir.", "D.S.D.": "8th Cir.",
        "D.N.D.": "8th Cir.",
        "D.Minn.": "8th Cir.", "E.D.Mo.": "8th Cir.", "W.D.Mo.": "8th Cir.",
        "E.D.Ark.": "8th Cir.", "W.D.Ark.": "8th Cir.", "N.D.Iowa": "8th Cir.",
        "S.D.Iowa": "8th Cir.", "D.Neb.": "8th Cir.", "D. S.D.": "8th Cir.",
        "D. N.D.": "8th Cir.", "D. Neb": "8th Cir.",
        # 9th Circuit
        "C.D. Cal.": "9th Cir.", "N.D. Cal.": "9th Cir.", "S.D. Cal.": "9th Cir.",
        "E.D. Cal.": "9th Cir.", "D. Ariz.": "9th Cir.", "D. Nev.": "9th Cir.",
        "D. Or.": "9th Cir.", "W.D. Wash.": "9th Cir.", "E.D. Wash.": "9th Cir.",
        "D. Idaho": "9th Cir.", "D. Mont.": "9th Cir.", "D. Alaska": "9th Cir.",
        "D. Haw.": "9th Cir.", "D. Guam": "9th Cir.",
        "C.D.Cal.": "9th Cir.", "N.D.Cal.": "9th Cir.", "S.D.Cal.": "9th Cir.",
        "E.D.Cal.": "9th Cir.", "D.Ariz.": "9th Cir.", "D.Nev.": "9th Cir.",
        "D.Or.": "9th Cir.", "W.D.Wash.": "9th Cir.", "E.D.Wash.": "9th Cir.",
        "D.Idaho": "9th Cir.", "D.Mont.": "9th Cir.", "D.Alaska": "9th Cir.",
        "D.Haw.": "9th Cir.",
        # 10th Circuit
        "D. Colo.": "10th Cir.", "D. Kan.": "10th Cir.", "D.N.M.": "10th Cir.",
        "N.D. Okla.": "10th Cir.", "W.D. Okla.": "10th Cir.", "E.D. Okla.": "10th Cir.",
        "D. Utah": "10th Cir.", "D. Wyo.": "10th Cir.",
        "D.Colo.": "10th Cir.", "D.Kan.": "10th Cir.", "D. N.M.": "10th Cir.",
        "N.D.Okla.": "10th Cir.", "W.D.Okla.": "10th Cir.", "E.D.Okla.": "10th Cir.",
        "D.Utah": "10th Cir.", "D.Wyo.": "10th Cir.",
        # 11th Circuit
        "N.D. Ga.": "11th Cir.", "M.D. Ga.": "11th Cir.", "S.D. Ga.": "11th Cir.",
        "N.D. Ala.": "11th Cir.", "M.D. Ala.": "11th Cir.", "S.D. Ala.": "11th Cir.",
        "N.D. Fla.": "11th Cir.", "M.D. Fla.": "11th Cir.", "S.D. Fla.": "11th Cir.",
        "N.D.Ga.": "11th Cir.", "M.D.Ga.": "11th Cir.", "S.D.Ga.": "11th Cir.",
        "N.D.Ala.": "11th Cir.", "M.D.Ala.": "11th Cir.", "S.D.Ala.": "11th Cir.",
        "N.D.Fla.": "11th Cir.", "M.D.Fla.": "11th Cir.", "S.D.Fla.": "11th Cir.",
        # D.C. Circuit
        "D.D.C.": "D.C. Cir.", "D. D.C.": "D.C. Cir.",
        # Spelled-out variants
        "D. Maryland": "4th Cir.", "D. Puerto Rico": "1st Cir.",
        "W.D. Washington": "9th Cir.", "N.D. Oklahoma": "10th Cir.",
        "D. New Mexico": "10th Cir.", "D. Minnesota": "8th Cir.",
        "E.D. Louisiana": "5th Cir.", "M.D. North Carolina": "4th Cir.",
    }

    # Try direct match
    if court in district_to_circuit:
        return district_to_circuit[court]

    # Try partial match
    for dist, circ in district_to_circuit.items():
        if dist in court or court in dist:
            return circ

    # Check if it's a circuit court directly
    circ_match = re.search(r'(\d+)(?:st|nd|rd|th|d)\s*Cir', court)
    if circ_match:
        return ordinal_circuit(circ_match.group(1))
    if "D.C." in court and "Cir" in court:
        return "D.C. Cir."

    # State courts and SCOTUS
    if "Supreme Court" in court and ("U.S." in court or "United States" in court):
        return "U.S. Supreme Court"
    # Catch state courts
    state_court_indicators = ["Ct. App.", "App. Div.", "DCA", "Super.", "Cmwlth.",
                              "Commw.", "SJC", "N.Y. Ct.", "Mich. Ct.", "Ct. App"]
    for ind in state_court_indicators:
        if ind in court:
            return "State Court"
    if "Supreme Court" in court or "N.J." in court.split():
        return "State Court"

    return f"UNMAPPED ({court})"


# ===========================================================================
# 1. BASIC DESCRIPTIVES
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 1: BASIC DESCRIPTIVES")
print("=" * 80)

total = len(cases)
print(f"\nTotal case count: {total}")

years = [c["year"] for c in cases]
print(f"Date range: {min(years)} - {max(years)}")

year_dist = Counter(years)
print("\nDistribution by year:")
rows = [(y, year_dist[y], pct(year_dist[y], total)) for y in sorted(year_dist.keys())]
print_table(rows, ["Year", "Count", "Pct"], "Year Distribution")


# ===========================================================================
# 2. ACCOMMODATION TYPE DISTRIBUTION
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 2: ACCOMMODATION TYPE DISTRIBUTION")
print("=" * 80)

acc_dist = Counter(c["accommodation_type"] for c in cases)
rows = [(at, cnt, pct(cnt, total)) for at, cnt in acc_dist.most_common()]
print_table(rows, ["Accommodation Type", "Count", "Pct"], "Accommodation Type Distribution")

# New categories check
new_cats = ["COMMUNICATION_ACCOMMODATION", "EVICTION_DEFENSE", "RENT_PAYMENT",
            "VISITOR_GUEST", "LEASE_RENEWAL", "TRANSFER"]
print("\nNew/expanded categories check:")
for cat in new_cats:
    cnt = acc_dist.get(cat, 0)
    print(f"  {cat}: {cnt} cases ({pct(cnt, total)})")

other_count = acc_dist.get("OTHER", 0)
print(f"\nOTHER category: {other_count} cases ({pct(other_count, total)})")
print(f"  v1 had ~802 total cases. OTHER was the dominant catch-all.")
print(f"  v3 has {total} total cases. OTHER = {pct(other_count, total)} of total.")

# Secondary accommodation types
sec_dist = Counter(c.get("secondary_accommodation_type", "NONE") for c in cases)
print("\nSecondary accommodation types:")
for at, cnt in sec_dist.most_common():
    print(f"  {at}: {cnt} ({pct(cnt, total)})")


# ===========================================================================
# 3. OUTCOME ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 3: OUTCOME ANALYSIS")
print("=" * 80)

outcome_dist = Counter(c["outcome"] for c in cases)
rows = [(o, cnt, pct(cnt, total)) for o, cnt in outcome_dist.most_common()]
print_table(rows, ["Outcome", "Count", "Pct"], "Overall Outcome Distribution")

p_wins_total = sum(1 for c in cases if is_plaintiff_win(c["outcome"]))
d_wins_total = sum(1 for c in cases if is_defendant_win(c["outcome"]))
print(f"\nPlaintiff win rate (incl. mixed-favorable): {p_wins_total}/{total} = {pct(p_wins_total, total)}")
print(f"Defendant win rate (incl. mixed-favorable): {d_wins_total}/{total} = {pct(d_wins_total, total)}")

# Win rates by accommodation type
print("\n--- Win Rates by Accommodation Type ---")
rows = win_rate_analysis(cases, "accommodation_type")
print_table(rows, ["Acc. Type", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Accommodation Type")

# Win rates by defendant type
print("\n--- Win Rates by Defendant Type ---")
rows = win_rate_analysis(cases, "defendant_type")
print_table(rows, ["Defendant Type", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Defendant Type")

# Win rates by disability category
print("\n--- Win Rates by Disability Category ---")
rows = win_rate_analysis(cases, "disability_category")
print_table(rows, ["Disability Cat.", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Disability Category")

# Win rates by plaintiff type
print("\n--- Win Rates by Plaintiff Type ---")
rows = win_rate_analysis(cases, "plaintiff_type")
print_table(rows, ["Plaintiff Type", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Plaintiff Type")

# Win rates by procedural posture
print("\n--- Win Rates by Procedural Posture ---")
rows = win_rate_analysis(cases, "procedural_posture")
print_table(rows, ["Proc. Posture", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Procedural Posture")


# ===========================================================================
# 4. POST-LOPER BRIGHT ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 4: POST-LOPER BRIGHT ANALYSIS")
print("=" * 80)

# Loper Bright decided June 28, 2024
# Use year > 2024 as strict post, year >= 2024 as inclusive
pre_lb = [c for c in cases if c["year"] < 2024]
post_lb_inclusive = [c for c in cases if c["year"] >= 2024]
post_lb_strict = [c for c in cases if c["year"] > 2024]
cases_2024 = [c for c in cases if c["year"] == 2024]

print(f"\nPre-Loper Bright (year < 2024): {len(pre_lb)} cases")
print(f"Year 2024 (transitional): {len(cases_2024)} cases")
print(f"Post-Loper Bright inclusive (year >= 2024): {len(post_lb_inclusive)} cases")
print(f"Post-Loper Bright strict (year > 2024): {len(post_lb_strict)} cases")

# Win rates pre vs post
for label, pre, post in [
    ("Inclusive (>=2024)", pre_lb, post_lb_inclusive),
    ("Strict (>2024)", pre_lb, post_lb_strict),
]:
    pre_pw = sum(1 for c in pre if is_plaintiff_win(c["outcome"]))
    post_pw = sum(1 for c in post if is_plaintiff_win(c["outcome"]))
    print(f"\n  {label}:")
    print(f"    Pre-LB plaintiff win rate:  {pre_pw}/{len(pre)} = {pct(pre_pw, len(pre))}")
    print(f"    Post-LB plaintiff win rate: {post_pw}/{len(post)} = {pct(post_pw, len(post))}")
    fisher_test(pre_pw, len(pre), post_pw, len(post), f"Pre vs Post LB ({label})")

# Loper Bright cited field
lb_dist = Counter(c.get("loper_bright_cited", "MISSING") for c in cases)
print(f"\nloper_bright_cited distribution:")
for val, cnt in lb_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

lb_cited = [c for c in cases if c.get("loper_bright_cited") == "YES"]
if lb_cited:
    print(f"\nCases citing Loper Bright: {len(lb_cited)}")
    for c in lb_cited:
        print(f"  - {c['case_name']} ({c['year']}) [{c['court']}] -> {c['outcome']}")
        if c.get("key_holding"):
            holding = c["key_holding"][:200]
            print(f"    Holding: {holding}...")

# Accommodation type breakdown pre vs post
print("\n--- Accommodation Type: Pre vs Post Loper Bright (inclusive) ---")
pre_acc = Counter(c["accommodation_type"] for c in pre_lb)
post_acc = Counter(c["accommodation_type"] for c in post_lb_inclusive)
all_acc_types = sorted(set(list(pre_acc.keys()) + list(post_acc.keys())))
rows = []
for at in all_acc_types:
    pre_n = pre_acc.get(at, 0)
    post_n = post_acc.get(at, 0)
    pre_pw = sum(1 for c in pre_lb if c["accommodation_type"] == at and is_plaintiff_win(c["outcome"]))
    post_pw = sum(1 for c in post_lb_inclusive if c["accommodation_type"] == at and is_plaintiff_win(c["outcome"]))
    rows.append((at, pre_n, pct(pre_pw, pre_n) if pre_n else "N/A",
                 post_n, pct(post_pw, post_n) if post_n else "N/A"))
print_table(rows, ["Acc. Type", "Pre-N", "Pre-P-Win%", "Post-N", "Post-P-Win%"],
            "Pre vs Post LB by Accommodation Type")


# ===========================================================================
# 5. IQBAL/TWOMBLY ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 5: IQBAL/TWOMBLY ANALYSIS")
print("=" * 80)

# Check for explicit fields
iqbal_fields = [k for k in all_keys if "iqbal" in k.lower() or "twombly" in k.lower()]
print(f"\nExplicit Iqbal/Twombly fields: {iqbal_fields if iqbal_fields else 'NONE'}")

# Search key_holding for mentions
iqbal_cases = []
twombly_cases = []
for c in cases:
    holding = (c.get("key_holding") or "").lower()
    desc = (c.get("accommodation_description") or "").lower()
    text = holding + " " + desc
    if "iqbal" in text:
        iqbal_cases.append(c)
    if "twombly" in text:
        twombly_cases.append(c)

iqbal_or_twombly = []
for c in cases:
    holding = (c.get("key_holding") or "").lower()
    desc = (c.get("accommodation_description") or "").lower()
    text = holding + " " + desc
    if "iqbal" in text or "twombly" in text:
        iqbal_or_twombly.append(c)

iqbal_set = set(id(c) for c in iqbal_or_twombly)
not_iqbal = [c for c in cases if id(c) not in iqbal_set]

print(f"\nCases mentioning 'Iqbal' in key_holding/description: {len(iqbal_cases)}")
print(f"Cases mentioning 'Twombly' in key_holding/description: {len(twombly_cases)}")
print(f"Cases mentioning either: {len(iqbal_or_twombly)}")

if iqbal_or_twombly:
    iq_pw = sum(1 for c in iqbal_or_twombly if is_plaintiff_win(c["outcome"]))
    iq_dw = sum(1 for c in iqbal_or_twombly if is_defendant_win(c["outcome"]))
    niq_pw = sum(1 for c in not_iqbal if is_plaintiff_win(c["outcome"]))
    print(f"\n  Iqbal/Twombly cases plaintiff win rate: {iq_pw}/{len(iqbal_or_twombly)} = {pct(iq_pw, len(iqbal_or_twombly))}")
    print(f"  Non-Iqbal/Twombly plaintiff win rate: {niq_pw}/{len(not_iqbal)} = {pct(niq_pw, len(not_iqbal))}")
    fisher_test(iq_pw, len(iqbal_or_twombly), niq_pw, len(not_iqbal), "Iqbal/Twombly vs non")

    # Dismissal rate
    dismiss_proc = ["MOTION_TO_DISMISS", "12B6_MOTION"]
    iq_dismiss = sum(1 for c in iqbal_or_twombly if c.get("procedural_posture") in dismiss_proc
                     or "DISMISS" in (c.get("procedural_posture") or "").upper())
    niq_dismiss = sum(1 for c in not_iqbal if c.get("procedural_posture") in dismiss_proc
                      or "DISMISS" in (c.get("procedural_posture") or "").upper())
    print(f"\n  Dismissal-stage cases among Iqbal/Twombly mentions: {iq_dismiss}/{len(iqbal_or_twombly)}")
    print(f"  Dismissal-stage cases among non-mentions: {niq_dismiss}/{len(not_iqbal)}")

    # List them
    print("\n  Cases mentioning Iqbal/Twombly:")
    for c in iqbal_or_twombly[:20]:
        print(f"    - {c['case_name']} ({c['year']}) [{c['court']}] -> {c['outcome']}")


# ===========================================================================
# 6. INTERACTIVE PROCESS ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 6: INTERACTIVE PROCESS ANALYSIS")
print("=" * 80)

ip_dist = Counter(c.get("interactive_process_discussed", "MISSING") for c in cases)
print("\ninteractive_process_discussed distribution:")
for val, cnt in ip_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

ip_yes = [c for c in cases if c.get("interactive_process_discussed") == "YES"]
ip_no = [c for c in cases if c.get("interactive_process_discussed") == "NO"]

if ip_yes and ip_no:
    yes_pw = sum(1 for c in ip_yes if is_plaintiff_win(c["outcome"]))
    no_pw = sum(1 for c in ip_no if is_plaintiff_win(c["outcome"]))
    print(f"\n  IP discussed - plaintiff win rate: {yes_pw}/{len(ip_yes)} = {pct(yes_pw, len(ip_yes))}")
    print(f"  IP NOT discussed - plaintiff win rate: {no_pw}/{len(ip_no)} = {pct(no_pw, len(ip_no))}")
    fisher_test(yes_pw, len(ip_yes), no_pw, len(ip_no), "IP discussed vs not")


# ===========================================================================
# 7. DELAY-AS-DENIAL ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 7: DELAY-AS-DENIAL ANALYSIS")
print("=" * 80)

dad_dist = Counter(c.get("delay_as_denial", "MISSING") for c in cases)
print("\ndelay_as_denial distribution:")
for val, cnt in dad_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

dad_yes = [c for c in cases if c.get("delay_as_denial") == "YES"]
dad_no = [c for c in cases if c.get("delay_as_denial") == "NO"]

if dad_yes and dad_no:
    yes_pw = sum(1 for c in dad_yes if is_plaintiff_win(c["outcome"]))
    no_pw = sum(1 for c in dad_no if is_plaintiff_win(c["outcome"]))
    print(f"\n  Delay-as-denial YES - plaintiff win rate: {yes_pw}/{len(dad_yes)} = {pct(yes_pw, len(dad_yes))}")
    print(f"  Delay-as-denial NO - plaintiff win rate: {no_pw}/{len(dad_no)} = {pct(no_pw, len(dad_no))}")
    fisher_test(yes_pw, len(dad_yes), no_pw, len(dad_no), "Delay-as-denial vs not")


# ===========================================================================
# 8. RACE-DISABILITY INTERSECTION
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 8: RACE-DISABILITY INTERSECTION")
print("=" * 80)

race_dist = Counter(c.get("race_mentioned", "MISSING") for c in cases)
print("\nrace_mentioned distribution:")
for val, cnt in race_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

dual_dist = Counter(c.get("dual_basis_claim", "MISSING") for c in cases)
print("\ndual_basis_claim distribution:")
for val, cnt in dual_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

race_yes = [c for c in cases if c.get("race_mentioned") == "YES"]
race_no = [c for c in cases if c.get("race_mentioned") == "NO"]

if race_yes and race_no:
    yes_pw = sum(1 for c in race_yes if is_plaintiff_win(c["outcome"]))
    no_pw = sum(1 for c in race_no if is_plaintiff_win(c["outcome"]))
    print(f"\n  Race mentioned - plaintiff win rate: {yes_pw}/{len(race_yes)} = {pct(yes_pw, len(race_yes))}")
    print(f"  Race NOT mentioned - plaintiff win rate: {no_pw}/{len(race_no)} = {pct(no_pw, len(race_no))}")
    fisher_test(yes_pw, len(race_yes), no_pw, len(race_no), "Race mentioned vs not")

dual_yes = [c for c in cases if c.get("dual_basis_claim") == "YES"]
dual_no = [c for c in cases if c.get("dual_basis_claim") == "NO"]

if dual_yes and dual_no:
    yes_pw = sum(1 for c in dual_yes if is_plaintiff_win(c["outcome"]))
    no_pw = sum(1 for c in dual_no if is_plaintiff_win(c["outcome"]))
    print(f"\n  Dual-basis claim - plaintiff win rate: {yes_pw}/{len(dual_yes)} = {pct(yes_pw, len(dual_yes))}")
    print(f"  Single-basis claim - plaintiff win rate: {no_pw}/{len(dual_no)} = {pct(no_pw, len(dual_no))}")
    fisher_test(yes_pw, len(dual_yes), no_pw, len(dual_no), "Dual vs single basis")

# Race categories
race_cat_dist = Counter()
for c in cases:
    rc = c.get("race_categories", "N/A")
    if rc and rc != "N/A":
        # May be comma-separated
        for cat in str(rc).split(","):
            cat = cat.strip()
            if cat:
                race_cat_dist[cat] += 1
if race_cat_dist:
    print("\nRace categories mentioned:")
    for cat, cnt in race_cat_dist.most_common():
        print(f"  {cat}: {cnt}")


# ===========================================================================
# 9. CIRCUIT ANALYSIS
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 9: CIRCUIT ANALYSIS")
print("=" * 80)

# Map each case to a circuit
for c in cases:
    c["_circuit"] = extract_circuit(c.get("court", ""))

circuit_dist = Counter(c["_circuit"] for c in cases)
print("\nCase volume by circuit:")
rows = [(circ, cnt, pct(cnt, total)) for circ, cnt in circuit_dist.most_common()]
print_table(rows, ["Circuit", "Count", "Pct"], "Cases by Circuit")

# Check unmapped
unmapped = [c for c in cases if c["_circuit"].startswith("UNMAPPED")]
if unmapped:
    unmapped_courts = Counter(c["court"] for c in unmapped)
    print(f"\nUnmapped courts ({len(unmapped)} cases):")
    for court, cnt in unmapped_courts.most_common(20):
        print(f"  {court}: {cnt}")

print("\n--- Win Rates by Circuit ---")
rows = win_rate_analysis(cases, "_circuit", min_n=5)
print_table(rows, ["Circuit", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Circuit")


# ===========================================================================
# 10. DEFENDANT TYPE DEEP DIVE
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 10: DEFENDANT TYPE DEEP DIVE")
print("=" * 80)

# Already printed win rates above, now do accommodation type by defendant
def_types = sorted(set(c["defendant_type"] for c in cases))
print("\n--- Accommodation Type Distribution by Defendant Type ---")
for dt in def_types:
    dt_cases = [c for c in cases if c["defendant_type"] == dt]
    if len(dt_cases) < 3:
        continue
    acc_ct = Counter(c["accommodation_type"] for c in dt_cases)
    print(f"\n  {dt} (n={len(dt_cases)}):")
    for at, cnt in acc_ct.most_common(5):
        print(f"    {at}: {cnt} ({pct(cnt, len(dt_cases))})")


# ===========================================================================
# 11. NEW FIELDS CHECK
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 11: NEW FIELDS IN V3")
print("=" * 80)

new_fields = ["housing_type", "subsidy_program", "property_state", "property_city",
              "loper_bright_cited", "fha_section_cited", "race_categories",
              "national_origin", "race_notes", "secondary_accommodation_type",
              "race_if_mentioned_raw", "subsidy_program_raw", "defendant_type_raw",
              "disability_category_raw"]

for field in new_fields:
    # Handle unhashable types (lists) by converting to strings
    vals = Counter(str(c.get(field)) for c in cases)
    unique_non_null = {k: v for k, v in vals.items() if k not in ("None", "N/A")}
    present = sum(1 for c in cases if str(c.get(field)) not in ("None", "N/A"))
    print(f"\n{field}: {len(unique_non_null)} unique values, present in {present}/{total} cases")
    for val, cnt in vals.most_common(10):
        print(f"  {val}: {cnt}")

# Housing type analysis
ht_dist = Counter(c.get("housing_type", "MISSING") for c in cases)
print("\n--- Win Rates by Housing Type ---")
rows = win_rate_analysis(cases, "housing_type")
print_table(rows, ["Housing Type", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Housing Type")

# Subsidy program
sp_dist = Counter(c.get("subsidy_program", "MISSING") for c in cases)
print("\n--- Win Rates by Subsidy Program ---")
rows = win_rate_analysis(cases, "subsidy_program")
print_table(rows, ["Subsidy Program", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
            "Plaintiff Win Rate by Subsidy Program")

# FHA section cited
fha_dist = Counter(c.get("fha_section_cited", "MISSING") for c in cases)
print("\nFHA Section Cited distribution:")
for val, cnt in fha_dist.most_common():
    print(f"  {val}: {cnt} ({pct(cnt, total)})")

# State distribution (top 15)
state_dist = Counter(c.get("property_state", "UNKNOWN") for c in cases)
print("\nTop 15 states by case volume:")
for st, cnt in state_dist.most_common(15):
    print(f"  {st}: {cnt} ({pct(cnt, total)})")


# ===========================================================================
# 12. STRUCTURAL MODIFICATION VS OTHER TYPES
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 12: STRUCTURAL MODIFICATION ANALYSIS")
print("=" * 80)

struct_mod = [c for c in cases if c["accommodation_type"] == "STRUCTURAL_MODIFICATION"]
non_struct = [c for c in cases if c["accommodation_type"] != "STRUCTURAL_MODIFICATION"]

sm_pw = sum(1 for c in struct_mod if is_plaintiff_win(c["outcome"]))
nsm_pw = sum(1 for c in non_struct if is_plaintiff_win(c["outcome"]))

print(f"\nStructural modification cases: {len(struct_mod)}")
print(f"  Plaintiff win rate: {sm_pw}/{len(struct_mod)} = {pct(sm_pw, len(struct_mod))}")
print(f"All other types: {len(non_struct)}")
print(f"  Plaintiff win rate: {nsm_pw}/{len(non_struct)} = {pct(nsm_pw, len(non_struct))}")
fisher_test(sm_pw, len(struct_mod), nsm_pw, len(non_struct), "Structural mod vs others")

# Defendant types for structural mod
if struct_mod:
    sm_def = Counter(c["defendant_type"] for c in struct_mod)
    print("\n  Defendant types in structural modification cases:")
    for dt, cnt in sm_def.most_common():
        print(f"    {dt}: {cnt} ({pct(cnt, len(struct_mod))})")

    sm_dis = Counter(c["disability_category"] for c in struct_mod)
    print("\n  Disability categories in structural modification cases:")
    for dc, cnt in sm_dis.most_common():
        print(f"    {dc}: {cnt} ({pct(cnt, len(struct_mod))})")


# ===========================================================================
# 13. SUBSTANCE ABUSE CASES
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 13: SUBSTANCE ABUSE CASES")
print("=" * 80)

# Check what the category is called
substance_cats = [k for k in Counter(c["disability_category"] for c in cases).keys()
                  if "SUBSTANCE" in k.upper() or "ADDICTION" in k.upper() or "ALCOHOL" in k.upper()]
print(f"Substance-related disability categories found: {substance_cats}")

sa_cases = [c for c in cases if c["disability_category"] in substance_cats
            or "SUBSTANCE" in (c.get("disability_category") or "").upper()]

# Also check for broader match
if not sa_cases:
    sa_cases = [c for c in cases if "substance" in (c.get("disability_category") or "").lower()
                or "addiction" in (c.get("disability_category") or "").lower()
                or "substance" in (c.get("disability_category_raw") or "").lower()]

print(f"Substance abuse cases: {len(sa_cases)}")

if sa_cases:
    sa_pw = sum(1 for c in sa_cases if is_plaintiff_win(c["outcome"]))
    sa_ids = set(id(c) for c in sa_cases)
    non_sa = [c for c in cases if id(c) not in sa_ids]
    non_sa_pw = sum(1 for c in non_sa if is_plaintiff_win(c["outcome"]))

    print(f"  Plaintiff win rate: {sa_pw}/{len(sa_cases)} = {pct(sa_pw, len(sa_cases))}")
    print(f"  Non-substance plaintiff win rate: {non_sa_pw}/{len(non_sa)} = {pct(non_sa_pw, len(non_sa))}")
    fisher_test(sa_pw, len(sa_cases), non_sa_pw, len(non_sa), "Substance vs non-substance")

    sa_acc = Counter(c["accommodation_type"] for c in sa_cases)
    print("\n  Accommodation types in substance abuse cases:")
    for at, cnt in sa_acc.most_common():
        print(f"    {at}: {cnt} ({pct(cnt, len(sa_cases))})")

    sa_def = Counter(c["defendant_type"] for c in sa_cases)
    print("\n  Defendant types in substance abuse cases:")
    for dt, cnt in sa_def.most_common():
        print(f"    {dt}: {cnt} ({pct(cnt, len(sa_cases))})")

    sa_out = Counter(c["outcome"] for c in sa_cases)
    print("\n  Outcome distribution:")
    for o, cnt in sa_out.most_common():
        print(f"    {o}: {cnt} ({pct(cnt, len(sa_cases))})")


# ===========================================================================
# 14. HOA/ESA CLUSTERING
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 14: HOA/ESA CLUSTERING")
print("=" * 80)

esa_cases = [c for c in cases if c["accommodation_type"] == "ASSISTANCE_ANIMAL"]
print(f"\nAssistance animal cases: {len(esa_cases)}")

if esa_cases:
    esa_def = Counter(c["defendant_type"] for c in esa_cases)
    print("\n  Defendant type distribution for assistance animal cases:")
    for dt, cnt in esa_def.most_common():
        pw = sum(1 for c in esa_cases if c["defendant_type"] == dt and is_plaintiff_win(c["outcome"]))
        print(f"    {dt}: {cnt} ({pct(cnt, len(esa_cases))}) -> P-win: {pct(pw, cnt)}")

    # HOA specifically
    hoa_esa = [c for c in esa_cases if c["defendant_type"] == "HOA_CONDO_ASSN"]
    non_hoa_esa = [c for c in esa_cases if c["defendant_type"] != "HOA_CONDO_ASSN"]
    if hoa_esa and non_hoa_esa:
        hoa_pw = sum(1 for c in hoa_esa if is_plaintiff_win(c["outcome"]))
        nhoa_pw = sum(1 for c in non_hoa_esa if is_plaintiff_win(c["outcome"]))
        print(f"\n  HOA + ESA: {hoa_pw}/{len(hoa_esa)} = {pct(hoa_pw, len(hoa_esa))} plaintiff win rate")
        print(f"  Non-HOA + ESA: {nhoa_pw}/{len(non_hoa_esa)} = {pct(nhoa_pw, len(non_hoa_esa))} plaintiff win rate")
        fisher_test(hoa_pw, len(hoa_esa), nhoa_pw, len(non_hoa_esa), "HOA-ESA vs non-HOA-ESA")

    # Cross-tab: ESA by defendant type and outcome
    print("\n  Cross-tab: Assistance Animal by Defendant Type")
    esa_defs = sorted(set(c["defendant_type"] for c in esa_cases))
    rows = []
    for dt in esa_defs:
        sub = [c for c in esa_cases if c["defendant_type"] == dt]
        pw = sum(1 for c in sub if is_plaintiff_win(c["outcome"]))
        dw = sum(1 for c in sub if is_defendant_win(c["outcome"]))
        rows.append((dt, len(sub), pw, pct(pw, len(sub)), dw, pct(dw, len(sub))))
    rows.sort(key=lambda r: float(r[3].replace("%", "")), reverse=True)
    print_table(rows, ["Defendant", "N", "P-Win", "P-Win%", "D-Win", "D-Win%"],
                "ESA Cases by Defendant Type")


# ===========================================================================
# 15. TRANSFER ACCOMMODATION
# ===========================================================================
print("\n" + "=" * 80)
print("  SECTION 15: TRANSFER ACCOMMODATION ANALYSIS")
print("=" * 80)

transfer_cases = [c for c in cases if c["accommodation_type"] == "TRANSFER"]
print(f"\nTransfer accommodation cases: {len(transfer_cases)}")

if transfer_cases:
    t_pw = sum(1 for c in transfer_cases if is_plaintiff_win(c["outcome"]))
    print(f"  Plaintiff win rate: {t_pw}/{len(transfer_cases)} = {pct(t_pw, len(transfer_cases))}")
    print(f"  (Previously reported as 3.4% in v1)")

    t_def = Counter(c["defendant_type"] for c in transfer_cases)
    print("\n  Defendant types:")
    for dt, cnt in t_def.most_common():
        print(f"    {dt}: {cnt} ({pct(cnt, len(transfer_cases))})")

    t_dis = Counter(c["disability_category"] for c in transfer_cases)
    print("\n  Disability categories:")
    for dc, cnt in t_dis.most_common():
        print(f"    {dc}: {cnt} ({pct(cnt, len(transfer_cases))})")

    t_out = Counter(c["outcome"] for c in transfer_cases)
    print("\n  Outcome distribution:")
    for o, cnt in t_out.most_common():
        print(f"    {o}: {cnt} ({pct(cnt, len(transfer_cases))})")

    # Housing type for transfer
    t_ht = Counter(c.get("housing_type", "UNKNOWN") for c in transfer_cases)
    print("\n  Housing types:")
    for ht, cnt in t_ht.most_common():
        print(f"    {ht}: {cnt} ({pct(cnt, len(transfer_cases))})")


# ===========================================================================
# SUMMARY: TOP 15 FINDINGS
# ===========================================================================
print("\n" + "=" * 80)
print("  TOP 15 FINDINGS FOR LAW REVIEW ARTICLE")
print("=" * 80)

findings = []

# 1. Dataset size
findings.append(f"1. EXPANDED DATASET: v3 contains {total} cases (up from 802 in v1), spanning {min(years)}-{max(years)}.")

# 2. Overall win rate
findings.append(f"2. OVERALL PLAINTIFF WIN RATE: {pct(p_wins_total, total)} ({p_wins_total}/{total}). "
                f"Defendant win rate: {pct(d_wins_total, total)}.")

# 3. Accommodation types
other_pct = pct(acc_dist.get("OTHER", 0), total)
esa_n = acc_dist.get("ASSISTANCE_ANIMAL", 0)
findings.append(f"3. ACCOMMODATION TAXONOMY: OTHER category = {other_pct} of cases. "
                f"Top types: {', '.join(f'{at}({cnt})' for at, cnt in acc_dist.most_common(5))}.")

# 4. ESA/HOA
if esa_cases:
    hoa_esa_n = sum(1 for c in esa_cases if c["defendant_type"] == "HOA_CONDO_ASSN")
    findings.append(f"4. HOA/ESA CLUSTERING: {hoa_esa_n}/{len(esa_cases)} ESA cases ({pct(hoa_esa_n, len(esa_cases))}) "
                    f"involve HOAs/condo associations.")

# 5. Transfer
if transfer_cases:
    t_pw = sum(1 for c in transfer_cases if is_plaintiff_win(c["outcome"]))
    findings.append(f"5. TRANSFER CASES: {len(transfer_cases)} cases with {pct(t_pw, len(transfer_cases))} plaintiff win rate.")

# 6. Loper Bright
lb_count = sum(1 for c in cases if c.get("loper_bright_cited") == "YES")
findings.append(f"6. LOPER BRIGHT: {lb_count} cases cite Loper Bright. Post-2024 cases: {len(post_lb_strict)}.")

# 7. Interactive process
if ip_yes:
    yes_pw = sum(1 for c in ip_yes if is_plaintiff_win(c["outcome"]))
    no_pw_count = sum(1 for c in ip_no if is_plaintiff_win(c["outcome"]))
    findings.append(f"7. INTERACTIVE PROCESS: Discussed in {len(ip_yes)}/{total} cases ({pct(len(ip_yes), total)}). "
                    f"Win rate when discussed: {pct(yes_pw, len(ip_yes))} vs {pct(no_pw_count, len(ip_no))} when not.")

# 8. Delay as denial
if dad_yes:
    dad_pw = sum(1 for c in dad_yes if is_plaintiff_win(c["outcome"]))
    findings.append(f"8. DELAY-AS-DENIAL: {len(dad_yes)} cases ({pct(len(dad_yes), total)}). "
                    f"Plaintiff win rate: {pct(dad_pw, len(dad_yes))}.")

# 9. Race intersection
if race_yes:
    race_pw = sum(1 for c in race_yes if is_plaintiff_win(c["outcome"]))
    findings.append(f"9. RACE-DISABILITY INTERSECTION: Race mentioned in {len(race_yes)} cases ({pct(len(race_yes), total)}). "
                    f"Plaintiff win rate: {pct(race_pw, len(race_yes))}.")

# 10. Dual basis
if dual_yes:
    dual_pw = sum(1 for c in dual_yes if is_plaintiff_win(c["outcome"]))
    findings.append(f"10. DUAL-BASIS CLAIMS: {len(dual_yes)} cases. "
                    f"Plaintiff win rate: {pct(dual_pw, len(dual_yes))}.")

# 11. Structural modification
if struct_mod:
    findings.append(f"11. STRUCTURAL MODIFICATIONS: {len(struct_mod)} cases, "
                    f"plaintiff win rate {pct(sm_pw, len(struct_mod))}.")

# 12. Iqbal/Twombly
findings.append(f"12. IQBAL/TWOMBLY: {len(iqbal_or_twombly)} cases mention these standards in holdings.")

# 13. Circuit variation
top_circuits = circuit_dist.most_common(3)
findings.append(f"13. CIRCUIT CONCENTRATION: Top circuits: "
                f"{', '.join(f'{circ}({cnt})' for circ, cnt in top_circuits)}.")

# 14. Substance abuse
if sa_cases:
    sa_pw_n = sum(1 for c in sa_cases if is_plaintiff_win(c["outcome"]))
    findings.append(f"14. SUBSTANCE ABUSE: {len(sa_cases)} cases, "
                    f"plaintiff win rate {pct(sa_pw_n, len(sa_cases))}.")
else:
    findings.append("14. SUBSTANCE ABUSE: No dedicated category found; check disability_category values.")

# 15. New v3 fields
new_field_names = [f for f in new_fields if any(c.get(f) not in (None, "N/A", "NONE", "NONE_MENTIONED") for c in cases)]
findings.append(f"15. NEW V3 FIELDS: {len(new_field_names)} fields with substantive data: "
                f"{', '.join(new_field_names[:8])}.")

print()
for f in findings:
    print(f)


# ===========================================================================
# COMPARISON TABLE: V1 vs V3
# ===========================================================================
print("\n" + "=" * 80)
print("  COMPARISON TABLE: V1 (802 cases) vs V3")
print("=" * 80)

v1_stats = {
    "Total cases": "802",
    "Transfer win rate": "3.4%",
    "OTHER category": "dominant (exact % TBD)",
}
v3_stats = {
    "Total cases": str(total),
    "Transfer win rate": pct(sum(1 for c in transfer_cases if is_plaintiff_win(c["outcome"])), len(transfer_cases)) if transfer_cases else "N/A",
    "OTHER category": pct(acc_dist.get("OTHER", 0), total),
}

rows = []
for key in ["Total cases", "Transfer win rate", "OTHER category"]:
    rows.append((key, v1_stats.get(key, "N/A"), v3_stats.get(key, "N/A")))

# Add more comparison rows
rows.append(("Overall P win rate", "~38% (est.)", pct(p_wins_total, total)))
rows.append(("ESA cases", "TBD", str(acc_dist.get("ASSISTANCE_ANIMAL", 0))))
rows.append(("Loper Bright cited", "0 (pre-decision)", str(lb_count)))
rows.append(("New acc. categories", "0", str(sum(1 for cat in new_cats if acc_dist.get(cat, 0) > 0))))
rows.append(("Fields per record", "~15 (est.)", str(len(all_keys))))

print_table(rows, ["Metric", "V1", "V3"], "V1 vs V3 Comparison")


# ===========================================================================
# RECOMMENDATIONS FOR REVISION STRATEGY
# ===========================================================================
print("\n" + "=" * 80)
print("  RECOMMENDATIONS FOR REVISION STRATEGY")
print("=" * 80)

recommendations = [
    "1. UPDATE ALL DESCRIPTIVE STATISTICS: Replace v1 numbers (802 cases) with v3 throughout.",
    f"2. HIGHLIGHT EXPANDED TAXONOMY: v3 has {len(acc_dist)} accommodation categories vs fewer in v1. "
    f"   The OTHER category at {pct(acc_dist.get('OTHER', 0), total)} shows improved classification.",
    "3. ADD POST-LOPER BRIGHT SECTION: Even with limited post-2024 cases, the framework is now testable.",
    f"4. EMPHASIZE TRANSFER CASES: With {len(transfer_cases)} transfer cases, the extremely low win rate "
    f"   ({pct(sum(1 for c in transfer_cases if is_plaintiff_win(c['outcome'])), len(transfer_cases)) if transfer_cases else 'N/A'}) "
    "   is a powerful narrative finding.",
    "5. INTERACTIVE PROCESS FINDING: The differential in win rates when interactive process is discussed "
    "   supports the doctrinal argument about its importance.",
    "6. ESA/HOA CLUSTERING: Cross-tabulate to strengthen the argument about regulatory burden on HOAs.",
    "7. USE NEW FIELDS: housing_type, subsidy_program, and property_state enable geographic and "
    "   housing-market-type analyses not possible in v1.",
    "8. CIRCUIT SPLITS: Use circuit-level win rate data to identify doctrinal divergences.",
    "9. RACE-DISABILITY INTERSECTION: If dual-basis claims show different win rates, this supports "
    "   the intersectionality argument.",
    "10. RUN THE SCRIPT ON FINAL DATA: Re-run before submission to capture any last additions.",
]

for r in recommendations:
    print(f"\n{r}")


# ===========================================================================
# EXTRA: Disability category full listing
# ===========================================================================
print("\n" + "=" * 80)
print("  APPENDIX: FULL DISABILITY CATEGORY LISTING")
print("=" * 80)

dis_dist = Counter(c["disability_category"] for c in cases)
rows = [(dc, cnt, pct(cnt, total)) for dc, cnt in dis_dist.most_common()]
print_table(rows, ["Disability Category", "Count", "Pct"], "All Disability Categories")


# ===========================================================================
# EXTRA: Full outcome by year heatmap (text)
# ===========================================================================
print("\n" + "=" * 80)
print("  APPENDIX: OUTCOME BY YEAR")
print("=" * 80)

outcomes = sorted(set(c["outcome"] for c in cases))
year_list = sorted(set(c["year"] for c in cases))
header = ["Year"] + outcomes
rows = []
for y in year_list:
    yr_cases = [c for c in cases if c["year"] == y]
    row = [str(y)]
    for o in outcomes:
        cnt = sum(1 for c in yr_cases if c["outcome"] == o)
        row.append(str(cnt))
    rows.append(tuple(row))
print_table(rows, header, "Outcome by Year")


print("\n" + "=" * 80)
print("  ANALYSIS COMPLETE")
print("=" * 80)
