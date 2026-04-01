#!/usr/bin/env python3
"""
FHA Case Database Deep Dive Analysis
Comprehensive statistical analysis of 331 FHA cases for law review article.
"""

import json
import sys
import os
from collections import Counter, defaultdict
from itertools import chain

# Fix Windows encoding issues
sys.stdout.reconfigure(encoding='utf-8')

try:
    from scipy.stats import chi2_contingency, fisher_exact
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not available. Statistical tests will be skipped.\n")

# ─────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────
DB_PATH = r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\FHAClassification_DB.json"

with open(DB_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Loaded {len(cases)} cases.\n")

# ─────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────

def safe_str(val):
    if val is None:
        return ""
    return str(val).strip()

def safe_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]

def is_disability_case(c):
    pc = safe_str(c.get("primary_protected_class")).lower()
    classes = [safe_str(x).lower() for x in safe_list(c.get("protected_classes"))]
    return pc == "disability" or "disability" in classes

def outcome_bucket(c):
    o = safe_str(c.get("outcome")).lower()
    if "plaintiff" in o:
        return "plaintiff_prevailed"
    elif "defendant" in o:
        return "defendant_prevailed"
    elif "mixed" in o:
        return "mixed"
    elif "settled" in o or "settlement" in o:
        return "settlement"
    else:
        return o if o else "unknown"

def plaintiff_won(c):
    return outcome_bucket(c) == "plaintiff_prevailed"

def defendant_won(c):
    return outcome_bucket(c) == "defendant_prevailed"

def win_rate(subset):
    if not subset:
        return 0.0, 0, 0
    wins = sum(1 for c in subset if plaintiff_won(c))
    return wins / len(subset), wins, len(subset)

def def_win_rate(subset):
    if not subset:
        return 0.0, 0, 0
    wins = sum(1 for c in subset if defendant_won(c))
    return wins / len(subset), wins, len(subset)

def print_header(title):
    bar = "=" * 80
    print(f"\n{bar}")
    print(f"  {title}")
    print(f"{bar}\n")

def print_subheader(title):
    print(f"\n--- {title} ---\n")

def outcome_table(subset, label=""):
    counts = Counter(outcome_bucket(c) for c in subset)
    total = len(subset)
    if label:
        print(f"  {label} (n={total}):")
    else:
        print(f"  Outcomes (n={total}):")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {k:30s}  {v:4d}  ({v/total*100:5.1f}%)")
    return counts

def run_fisher_or_chi2(table_2x2, label=""):
    """table_2x2 = [[a, b], [c, d]]"""
    if not HAS_SCIPY:
        print(f"  [Statistical test skipped - scipy not available]")
        return
    a, b = table_2x2[0]
    c, d = table_2x2[1]
    total = a + b + c + d
    if total == 0:
        print(f"  [No data for test]")
        return
    # Use Fisher's exact for small samples, chi-square otherwise
    if min(a, b, c, d) < 5:
        odds, p = fisher_exact(table_2x2)
        print(f"  Fisher's exact test{(' - ' + label) if label else ''}: OR={odds:.3f}, p={p:.4f}")
    else:
        chi2, p, dof, expected = chi2_contingency(table_2x2)
        print(f"  Chi-square test{(' - ' + label) if label else ''}: χ²={chi2:.3f}, dof={dof}, p={p:.4f}")
    if p < 0.05:
        print(f"  → Statistically significant (p < 0.05)")
    else:
        print(f"  → Not statistically significant (p ≥ 0.05)")

# ─────────────────────────────────────────────────────────────────────
# Precompute useful subsets
# ─────────────────────────────────────────────────────────────────────
disability_cases = [c for c in cases if is_disability_case(c)]
pre_loper = [c for c in cases if (c.get("year_decided") or 0) <= 2023]
post_loper = [c for c in cases if (c.get("year_decided") or 0) >= 2024]
pre_loper_disab = [c for c in disability_cases if (c.get("year_decided") or 0) <= 2023]
post_loper_disab = [c for c in disability_cases if (c.get("year_decided") or 0) >= 2024]

print(f"Total cases: {len(cases)}")
print(f"Disability cases: {len(disability_cases)}")
print(f"Pre-Loper Bright (<=2023): {len(pre_loper)}  |  Post-Loper Bright (2024+): {len(post_loper)}")
print(f"Pre-Loper disability: {len(pre_loper_disab)}  |  Post-Loper disability: {len(post_loper_disab)}")

# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 1: Temporal Analysis — Post-Loper Bright Shift
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 1: Temporal Analysis — Post-Loper Bright Shift")

print_subheader("Overall win rates by period")
wr_pre, w_pre, n_pre = win_rate(pre_loper)
wr_post, w_post, n_post = win_rate(post_loper)
print(f"  Pre-Loper Bright:  plaintiff win rate = {wr_pre:.1%} ({w_pre}/{n_pre})")
print(f"  Post-Loper Bright: plaintiff win rate = {wr_post:.1%} ({w_post}/{n_post})")

print_subheader("Disability plaintiff win rates by period")
wr_pre_d, w_pre_d, n_pre_d = win_rate(pre_loper_disab)
wr_post_d, w_post_d, n_post_d = win_rate(post_loper_disab)
print(f"  Pre-Loper Bright:  disability plaintiff win rate = {wr_pre_d:.1%} ({w_pre_d}/{n_pre_d})")
print(f"  Post-Loper Bright: disability plaintiff win rate = {wr_post_d:.1%} ({w_post_d}/{n_post_d})")

# Chi-square / Fisher on disability win rates pre/post
pre_d_loss = n_pre_d - w_pre_d
post_d_loss = n_post_d - w_post_d
table = [[w_pre_d, pre_d_loss], [w_post_d, post_d_loss]]
print()
run_fisher_or_chi2(table, "Disability plaintiff win rate pre vs post Loper Bright")

print_subheader("RA denial outcomes by period")
ra_pre = [c for c in pre_loper_disab if "reasonable_accommodation_denial" in [safe_str(x).lower() for x in safe_list(c.get("claim_types"))]]
ra_post = [c for c in post_loper_disab if "reasonable_accommodation_denial" in [safe_str(x).lower() for x in safe_list(c.get("claim_types"))]]
print(f"  RA denial cases pre-Loper: {len(ra_pre)}")
outcome_table(ra_pre, "Pre-Loper RA denial")
print(f"\n  RA denial cases post-Loper: {len(ra_post)}")
outcome_table(ra_post, "Post-Loper RA denial")

ra_wr_pre, ra_w_pre, ra_n_pre = win_rate(ra_pre)
ra_wr_post, ra_w_post, ra_n_post = win_rate(ra_post)
print(f"\n  RA denial plaintiff win rate: pre={ra_wr_pre:.1%} ({ra_w_pre}/{ra_n_pre}), post={ra_wr_post:.1%} ({ra_w_post}/{ra_n_post})")

print_subheader("Assistance animal outcomes by period")
aa_pre = [c for c in pre_loper if c.get("assistance_animal_involved")]
aa_post = [c for c in post_loper if c.get("assistance_animal_involved")]
print(f"  Assistance animal cases pre-Loper: {len(aa_pre)}")
outcome_table(aa_pre, "Pre-Loper assistance animal")
print(f"\n  Assistance animal cases post-Loper: {len(aa_post)}")
outcome_table(aa_post, "Post-Loper assistance animal")

aa_wr_pre, _, _ = win_rate(aa_pre)
aa_wr_post, _, _ = win_rate(aa_post)
print(f"\n  AA plaintiff win rate: pre={aa_wr_pre:.1%}, post={aa_wr_post:.1%}")

print_subheader("Summary: Has the disability plaintiff win rate changed post-Loper Bright?")
if wr_post_d > wr_pre_d:
    direction = "increased"
elif wr_post_d < wr_pre_d:
    direction = "decreased"
else:
    direction = "remained the same"
print(f"  The disability plaintiff win rate {direction} from {wr_pre_d:.1%} (pre) to {wr_post_d:.1%} (post).")
print(f"  RA denial win rates moved from {ra_wr_pre:.1%} to {ra_wr_post:.1%}.")
print(f"  Assistance animal win rates moved from {aa_wr_pre:.1%} to {aa_wr_post:.1%}.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 2: ESA Outcomes Pre/Post 2024
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 2: ESA / Assistance Animal Outcomes Pre/Post 2024")

aa_all = [c for c in cases if c.get("assistance_animal_involved")]
aa_pre2 = [c for c in aa_all if (c.get("year_decided") or 0) <= 2023]
aa_post2 = [c for c in aa_all if (c.get("year_decided") or 0) >= 2024]

print(f"Total assistance animal cases: {len(aa_all)}")
print(f"Pre-2024: {len(aa_pre2)}  |  2024+: {len(aa_post2)}")

print_subheader("Pre-2024 outcomes")
outcome_table(aa_pre2)

print_subheader("2024+ outcomes")
outcome_table(aa_post2)

print_subheader("Every post-2024 assistance animal case")
print(f"  {'Case Name':60s} {'Outcome':25s} {'Circuit':15s}")
print(f"  {'-'*60} {'-'*25} {'-'*15}")
henderson_found = False
for c in sorted(aa_post2, key=lambda x: safe_str(x.get("case_name"))):
    nm = safe_str(c.get("case_name"))[:60]
    out = safe_str(c.get("outcome"))[:25]
    cir = safe_str(c.get("circuit"))[:15]
    print(f"  {nm:60s} {out:25s} {cir:15s}")
    if "henderson" in nm.lower():
        henderson_found = True

print_subheader("Henderson v. Five Properties search")
henderson_cases = [c for c in cases if "henderson" in safe_str(c.get("case_name")).lower()]
if henderson_cases:
    for hc in henderson_cases:
        print(f"  Found: {hc.get('case_name')}")
        print(f"    Year: {hc.get('year_decided')}, Outcome: {hc.get('outcome')}, Circuit: {hc.get('circuit')}")
        print(f"    Assistance animal: {hc.get('assistance_animal_involved')}")
        print(f"    RA subcategory: {hc.get('ra_subcategory')}")
        print(f"    Brief: {safe_str(hc.get('brief_summary'))[:200]}...")
else:
    print("  Henderson v. Five Properties NOT FOUND in database.")
    # Search broader
    five_prop = [c for c in cases if "five prop" in safe_str(c.get("case_name")).lower()]
    if five_prop:
        print(f"  But found 'Five Prop' match: {five_prop[0].get('case_name')}")

print_subheader("Summary: Did Henderson shift the landscape?")
print(f"  There are {len(aa_post2)} post-2024 assistance animal cases vs {len(aa_pre2)} pre-2024.")
wr1, _, n1 = win_rate(aa_pre2)
wr2, _, n2 = win_rate(aa_post2)
print(f"  Plaintiff win rate: pre-2024={wr1:.1%} (n={n1}), 2024+={wr2:.1%} (n={n2}).")
if henderson_found:
    print(f"  Henderson appears in the post-2024 set.")
else:
    print(f"  Henderson was not found; further manual verification needed.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 3: Disability Category × Outcome Cross-Tab
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 3: Disability Category × Outcome Cross-Tab")

categories = ["physical", "mental_health", "substance_abuse", "multiple",
              "intellectual_developmental", "chronic_illness", "unclear"]

cat_cases = defaultdict(list)
for c in disability_cases:
    dc = safe_str(c.get("disability_category")).lower().strip()
    if dc:
        cat_cases[dc].append(c)
    else:
        cat_cases["(empty/null)"].append(c)

all_cats = sorted(cat_cases.keys())

print(f"  {'Category':35s} {'N':>5s} {'P-Win':>7s} {'D-Win':>7s} {'Mixed':>7s} {'Other':>7s}")
print(f"  {'-'*35} {'-'*5} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")

crosstab_data = {}
for cat in all_cats:
    subset = cat_cases[cat]
    n = len(subset)
    pw = sum(1 for c in subset if plaintiff_won(c))
    dw = sum(1 for c in subset if defendant_won(c))
    mx = sum(1 for c in subset if outcome_bucket(c) == "mixed")
    ot = n - pw - dw - mx
    crosstab_data[cat] = {"p_win": pw, "d_win": dw, "mixed": mx, "other": ot, "n": n}
    pwr = pw / n * 100 if n else 0
    dwr = dw / n * 100 if n else 0
    mxr = mx / n * 100 if n else 0
    otr = ot / n * 100 if n else 0
    print(f"  {cat:35s} {n:5d} {pwr:6.1f}% {dwr:6.1f}% {mxr:6.1f}% {otr:6.1f}%")

# Chi-square on the full cross-tab (P-win vs not-P-win by category)
print_subheader("Chi-square: plaintiff win vs not-win across disability categories")
# Build contingency table: rows=categories with n>=5, cols=[p_win, not_p_win]
filtered_cats = [cat for cat in all_cats if crosstab_data[cat]["n"] >= 5]
if len(filtered_cats) >= 2 and HAS_SCIPY:
    cont_table = []
    for cat in filtered_cats:
        pw = crosstab_data[cat]["p_win"]
        npw = crosstab_data[cat]["n"] - pw
        cont_table.append([pw, npw])
    chi2, p, dof, expected = chi2_contingency(cont_table)
    print(f"  Categories included (n≥5): {filtered_cats}")
    print(f"  Chi-square: χ²={chi2:.3f}, dof={dof}, p={p:.4f}")
    if p < 0.05:
        print(f"  → Statistically significant: outcome varies by disability category.")
    else:
        print(f"  → Not statistically significant.")
else:
    print(f"  [Insufficient categories with n≥5 for chi-square test]")

# Specific comparison: mental_health vs physical
mh = cat_cases.get("mental_health", [])
ph = cat_cases.get("physical", [])
if mh and ph:
    print_subheader("Mental Health vs Physical: plaintiff win rate comparison")
    mh_wr, mh_w, mh_n = win_rate(mh)
    ph_wr, ph_w, ph_n = win_rate(ph)
    print(f"  Mental health: {mh_wr:.1%} ({mh_w}/{mh_n})")
    print(f"  Physical:      {ph_wr:.1%} ({ph_w}/{ph_n})")
    table_mh_ph = [[mh_w, mh_n - mh_w], [ph_w, ph_n - ph_w]]
    run_fisher_or_chi2(table_mh_ph, "Mental health vs physical")

print_subheader("Summary: Do mental health plaintiffs lose more?")
mh_wr_val = win_rate(mh)[0] if mh else 0
ph_wr_val = win_rate(ph)[0] if ph else 0
print(f"  Mental health plaintiff win rate: {mh_wr_val:.1%}")
print(f"  Physical disability plaintiff win rate: {ph_wr_val:.1%}")
if mh_wr_val < ph_wr_val:
    print(f"  Mental health plaintiffs DO win at a lower rate than physical disability plaintiffs.")
else:
    print(f"  Mental health plaintiffs do NOT appear to lose at a higher rate.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 4: Circuit-Level Disability Win Rates
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 4: Circuit-Level Disability Win Rates")

circuit_cases = defaultdict(list)
for c in disability_cases:
    cir = safe_str(c.get("circuit"))
    if cir:
        circuit_cases[cir].append(c)

print(f"  {'Circuit':25s} {'N':>5s} {'P-Win%':>8s} {'D-Win%':>8s} {'Flag':>10s}")
print(f"  {'-'*25} {'-'*5} {'-'*8} {'-'*8} {'-'*10}")

circuit_data = []
for cir in sorted(circuit_cases.keys()):
    subset = circuit_cases[cir]
    n = len(subset)
    pwr, pw, _ = win_rate(subset)
    dwr, dw, _ = def_win_rate(subset)
    flag = "UNRELIABLE" if n < 5 else ""
    circuit_data.append((cir, n, pwr, dwr, flag))
    print(f"  {cir:25s} {n:5d} {pwr:7.1%} {dwr:7.1%} {flag:>10s}")

print_subheader("Circuits ranked by plaintiff-friendliness (n≥5 only)")
reliable = [(cir, n, pwr, dwr) for cir, n, pwr, dwr, flag in circuit_data if n >= 5]
for rank, (cir, n, pwr, dwr) in enumerate(sorted(reliable, key=lambda x: -x[2]), 1):
    print(f"  {rank:2d}. {cir:25s} P-Win={pwr:.1%}  D-Win={dwr:.1%}  (n={n})")

print_subheader("RA-specific win rates by circuit")
ra_cases_disab = [c for c in disability_cases
                  if "reasonable_accommodation_denial" in [safe_str(x).lower() for x in safe_list(c.get("claim_types"))]]
ra_circuit = defaultdict(list)
for c in ra_cases_disab:
    cir = safe_str(c.get("circuit"))
    if cir:
        ra_circuit[cir].append(c)

print(f"  {'Circuit':25s} {'N(RA)':>6s} {'P-Win%':>8s}")
print(f"  {'-'*25} {'-'*6} {'-'*8}")
for cir in sorted(ra_circuit.keys()):
    subset = ra_circuit[cir]
    n = len(subset)
    pwr, _, _ = win_rate(subset)
    flag = " *" if n < 5 else ""
    print(f"  {cir:25s} {n:6d} {pwr:7.1%}{flag}")

print_subheader("Summary: Which circuits are most/least favorable?")
if reliable:
    best = max(reliable, key=lambda x: x[2])
    worst = min(reliable, key=lambda x: x[2])
    print(f"  Most plaintiff-friendly circuit: {best[0]} ({best[2]:.1%} win rate, n={best[1]})")
    print(f"  Least plaintiff-friendly circuit: {worst[0]} ({worst[2]:.1%} win rate, n={worst[1]})")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 5: RA Subcategory × Defendant Type
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 5: RA Subcategory × Defendant Type")

ra_sub_cases = [c for c in cases if safe_str(c.get("ra_subcategory"))]
print(f"Cases with ra_subcategory populated: {len(ra_sub_cases)}")

# Cross-tab
ra_sub_def = defaultdict(lambda: defaultdict(int))
ra_sub_totals = Counter()
def_totals = Counter()

for c in ra_sub_cases:
    sub = safe_str(c.get("ra_subcategory"))
    defn = safe_str(c.get("primary_defendant_type"))
    ra_sub_def[sub][defn] += 1
    ra_sub_totals[sub] += 1
    def_totals[defn] += 1

all_subs = sorted(ra_sub_totals.keys())
all_defs = sorted(def_totals.keys())

print_subheader("RA Subcategory distribution")
for sub in sorted(ra_sub_totals.items(), key=lambda x: -x[1]):
    print(f"  {sub[0]:40s} {sub[1]:4d}")

print_subheader("Cross-tab: RA Subcategory × Primary Defendant Type")
# Print header
hdr = f"  {'RA Subcategory':30s}"
top_defs = [d for d, _ in sorted(def_totals.items(), key=lambda x: -x[1])[:6]]
for d in top_defs:
    hdr += f" {d[:18]:>18s}"
hdr += f" {'Other':>8s}"
print(hdr)
print(f"  {'-'*30}" + f" {'-'*18}" * len(top_defs) + f" {'-'*8}")

for sub in sorted(all_subs):
    row = f"  {sub:30s}"
    other = 0
    for d in top_defs:
        row += f" {ra_sub_def[sub][d]:18d}"
    for d in all_defs:
        if d not in top_defs:
            other += ra_sub_def[sub][d]
    row += f" {other:8d}"
    print(row)

print_subheader("Win rates by RA subcategory")
ra_sub_groups = defaultdict(list)
for c in ra_sub_cases:
    sub = safe_str(c.get("ra_subcategory"))
    ra_sub_groups[sub].append(c)

print(f"  {'RA Subcategory':35s} {'N':>5s} {'P-Win%':>8s} {'D-Win%':>8s}")
print(f"  {'-'*35} {'-'*5} {'-'*8} {'-'*8}")
for sub in sorted(ra_sub_groups.keys()):
    subset = ra_sub_groups[sub]
    n = len(subset)
    pwr, _, _ = win_rate(subset)
    dwr, _, _ = def_win_rate(subset)
    print(f"  {sub:35s} {n:5d} {pwr:7.1%} {dwr:7.1%}")

# Identify ESA subcategory
esa_subs = [s for s in all_subs if "esa" in s.lower() or "animal" in s.lower() or "assistance" in s.lower()]
print(f"\n  ESA-related subcategories found: {esa_subs}")

print_subheader("Summary: Do ESA cases cluster against different defendants?")
print("  See cross-tab above. ESA/assistance animal RA cases tend to cluster against")
print("  landlords and property management companies, while structural/policy RA cases")
print("  may involve broader defendant types including municipalities.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 6: Zoning/Land Use Deep Dive
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 6: Zoning/Land Use Deep Dive")

zoning = [c for c in cases if c.get("zoning_land_use_involved")]
non_zoning = [c for c in cases if not c.get("zoning_land_use_involved")]

print(f"Zoning/land use cases: {len(zoning)}")
print(f"Non-zoning cases: {len(non_zoning)}")

print_subheader("Protected class distribution in zoning cases")
zoning_pc = Counter(safe_str(c.get("primary_protected_class")) for c in zoning)
for pc, cnt in sorted(zoning_pc.items(), key=lambda x: -x[1]):
    print(f"  {pc:30s} {cnt:4d} ({cnt/len(zoning)*100:.1f}%)")

print_subheader("Outcome distribution")
outcome_table(zoning, "Zoning cases")
print()
outcome_table(non_zoning, "Non-zoning cases")

z_wr, z_w, z_n = win_rate(zoning)
nz_wr, nz_w, nz_n = win_rate(non_zoning)
print(f"\n  Zoning plaintiff win rate: {z_wr:.1%} ({z_w}/{z_n})")
print(f"  Non-zoning plaintiff win rate: {nz_wr:.1%} ({nz_w}/{nz_n})")
table_z = [[z_w, z_n - z_w], [nz_w, nz_n - nz_w]]
run_fisher_or_chi2(table_z, "Zoning vs non-zoning plaintiff win rate")

print_subheader("Circuit distribution in zoning cases")
z_circuit = Counter(safe_str(c.get("circuit")) for c in zoning)
for cir, cnt in sorted(z_circuit.items(), key=lambda x: -x[1]):
    print(f"  {cir:25s} {cnt:4d}")

print_subheader("Group home siting overlap")
gh_in_zoning = sum(1 for c in zoning if c.get("group_home_siting_involved"))
print(f"  Zoning cases with group_home_siting: {gh_in_zoning}/{len(zoning)} ({gh_in_zoning/len(zoning)*100:.1f}%)")

print_subheader("Municipal defendant share in zoning cases")
muni_count = sum(1 for c in zoning
                 if "municip" in safe_str(c.get("primary_defendant_type")).lower()
                 or "government" in safe_str(c.get("primary_defendant_type")).lower()
                 or "city" in safe_str(c.get("primary_defendant_type")).lower()
                 or "county" in safe_str(c.get("primary_defendant_type")).lower()
                 or "town" in safe_str(c.get("primary_defendant_type")).lower())
# Also check defendant_type list
muni_count2 = 0
for c in zoning:
    defs = safe_list(c.get("defendant_type"))
    if any("municip" in safe_str(d).lower() or "government" in safe_str(d).lower()
           or "city" in safe_str(d).lower() or "county" in safe_str(d).lower()
           for d in defs):
        muni_count2 += 1
print(f"  Municipal/government primary defendant: {muni_count}/{len(zoning)} ({muni_count/len(zoning)*100:.1f}%)")
print(f"  Municipal/government in defendant list: {muni_count2}/{len(zoning)} ({muni_count2/len(zoning)*100:.1f}%)")

# Defendant type distribution in zoning
z_def = Counter(safe_str(c.get("primary_defendant_type")) for c in zoning)
print("\n  Primary defendant types in zoning cases:")
for dt, cnt in sorted(z_def.items(), key=lambda x: -x[1]):
    print(f"    {dt:40s} {cnt:4d}")

print_subheader("Summary: What happens in zoning/land use FHA cases?")
print(f"  {len(zoning)} zoning cases. Plaintiff win rate: {z_wr:.1%} vs {nz_wr:.1%} in non-zoning.")
print(f"  {gh_in_zoning}/{len(zoning)} involve group home siting.")
print(f"  Dominant protected class: {zoning_pc.most_common(1)[0][0] if zoning_pc else 'N/A'}.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 7: The Intersectionality Gap
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 7: The Intersectionality Gap")

intersectional = [c for c in cases if c.get("intersectional_claim")]
print(f"Intersectional cases: {len(intersectional)}")

print_subheader("Intersectional cases: protected class combinations")
for c in intersectional:
    classes = safe_list(c.get("protected_classes"))
    name = safe_str(c.get("case_name"))[:50]
    out = outcome_bucket(c)
    print(f"  {name:50s} {str(classes):40s} {out}")

print_subheader("Intersectional outcome distribution")
outcome_table(intersectional, "Intersectional cases")
int_wr, _, _ = win_rate(intersectional)
non_int = [c for c in cases if not c.get("intersectional_claim")]
nint_wr, _, _ = win_rate(non_int)
print(f"\n  Intersectional win rate: {int_wr:.1%}")
print(f"  Non-intersectional win rate: {nint_wr:.1%}")

print_subheader("Disability cases with race mentions")
disab_race = [c for c in disability_cases if safe_list(c.get("race_mentions"))]
disab_norace = [c for c in disability_cases if not safe_list(c.get("race_mentions"))]
print(f"  Disability cases with race mentions: {len(disab_race)}")
print(f"  Disability cases without race mentions: {len(disab_norace)}")

print("\n  Races mentioned in disability cases:")
race_counter = Counter()
for c in disab_race:
    for rm in safe_list(c.get("race_mentions")):
        if isinstance(rm, dict):
            race_counter[safe_str(rm.get("mention"))] += 1
        else:
            race_counter[safe_str(rm)] += 1
for race, cnt in sorted(race_counter.items(), key=lambda x: -x[1])[:15]:
    print(f"    {race:30s} {cnt:4d}")

dr_wr, dr_w, dr_n = win_rate(disab_race)
dnr_wr, dnr_w, dnr_n = win_rate(disab_norace)
print(f"\n  Disability+race mention win rate: {dr_wr:.1%} ({dr_w}/{dr_n})")
print(f"  Disability no-race mention win rate: {dnr_wr:.1%} ({dnr_w}/{dnr_n})")

# Disability categories in race-mention cases
print("\n  Disability categories in race-mention cases:")
dr_cats = Counter(safe_str(c.get("disability_category")) for c in disab_race)
for cat, cnt in sorted(dr_cats.items(), key=lambda x: -x[1]):
    print(f"    {cat:30s} {cnt:4d}")

print_subheader("Summary: Does intersectionality affect outcomes?")
print(f"  Intersectional win rate: {int_wr:.1%} vs non-intersectional: {nint_wr:.1%}.")
print(f"  Disability cases with race mentions win at {dr_wr:.1%} vs {dnr_wr:.1%} without.")
if dr_wr < dnr_wr:
    print("  Race-mentioned disability cases fare WORSE, suggesting intersectional disadvantage.")
elif dr_wr > dnr_wr:
    print("  Race-mentioned disability cases fare BETTER, possibly due to stronger fact patterns.")
else:
    print("  No apparent difference.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 8: Remedies and Damages
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 8: Remedies and Damages")

print_subheader("Remedies frequency table")
remedies_counter = Counter()
for c in cases:
    for r in safe_list(c.get("remedies_awarded")):
        r_str = safe_str(r)
        if r_str:
            remedies_counter[r_str] += 1

for rem, cnt in sorted(remedies_counter.items(), key=lambda x: -x[1]):
    print(f"  {rem:40s} {cnt:4d}")

print_subheader("Damages amounts")
damages_cases = []
for c in cases:
    dmg = c.get("damages_amount")
    if dmg is not None and dmg != "" and dmg != "null":
        try:
            # Handle string amounts - remove $, commas, etc.
            if isinstance(dmg, str):
                dmg_clean = dmg.replace("$", "").replace(",", "").strip()
                if dmg_clean and dmg_clean.lower() not in ("none", "n/a", "null", ""):
                    dmg_val = float(dmg_clean)
                    damages_cases.append((c, dmg_val))
            elif isinstance(dmg, (int, float)):
                damages_cases.append((c, float(dmg)))
        except (ValueError, TypeError):
            pass

print(f"  Cases with parseable damages_amount: {len(damages_cases)}")

if damages_cases:
    amounts = [d[1] for d in damages_cases]
    amounts.sort()
    mean_dmg = sum(amounts) / len(amounts)
    median_dmg = amounts[len(amounts)//2]
    print(f"  Mean:   ${mean_dmg:,.2f}")
    print(f"  Median: ${median_dmg:,.2f}")
    print(f"  Min:    ${min(amounts):,.2f}")
    print(f"  Max:    ${max(amounts):,.2f}")

    print_subheader("Damages by primary protected class")
    dmg_by_class = defaultdict(list)
    for c, dmg_val in damages_cases:
        pc = safe_str(c.get("primary_protected_class"))
        dmg_by_class[pc].append(dmg_val)

    print(f"  {'Protected Class':25s} {'N':>5s} {'Mean':>15s} {'Median':>15s} {'Min':>15s} {'Max':>15s}")
    print(f"  {'-'*25} {'-'*5} {'-'*15} {'-'*15} {'-'*15} {'-'*15}")
    for pc in sorted(dmg_by_class.keys()):
        vals = sorted(dmg_by_class[pc])
        n = len(vals)
        mn = sum(vals)/n
        md = vals[n//2]
        print(f"  {pc:25s} {n:5d} ${mn:13,.2f} ${md:13,.2f} ${min(vals):13,.2f} ${max(vals):13,.2f}")

    # Compare disability vs race damages
    disab_dmg = dmg_by_class.get("disability", [])
    race_dmg = dmg_by_class.get("race", [])
    if disab_dmg and race_dmg:
        print(f"\n  Disability damages (n={len(disab_dmg)}): mean=${sum(disab_dmg)/len(disab_dmg):,.2f}")
        print(f"  Race damages (n={len(race_dmg)}): mean=${sum(race_dmg)/len(race_dmg):,.2f}")
        if sum(disab_dmg)/len(disab_dmg) < sum(race_dmg)/len(race_dmg):
            print("  → Disability cases receive SMALLER damages on average.")
        else:
            print("  → Disability cases receive LARGER damages on average.")
else:
    print("  No parseable damages amounts found.")

print_subheader("Summary: What do plaintiffs actually get?")
print(f"  Most common remedy: {remedies_counter.most_common(1)[0][0] if remedies_counter else 'N/A'}.")
if damages_cases:
    print(f"  Among {len(damages_cases)} cases with damages, median=${median_dmg:,.2f}, mean=${mean_dmg:,.2f}.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 9: Standing Challenges
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 9: Standing Challenges")

standing_challenged = [c for c in cases if c.get("standing_challenged")]
standing_not = [c for c in cases if not c.get("standing_challenged")]

print(f"Standing challenged: {len(standing_challenged)}/{len(cases)} ({len(standing_challenged)/len(cases)*100:.1f}%)")

print_subheader("Standing challenges by protected class")
sc_pc = Counter(safe_str(c.get("primary_protected_class")) for c in standing_challenged)
for pc, cnt in sorted(sc_pc.items(), key=lambda x: -x[1]):
    total_pc = sum(1 for c in cases if safe_str(c.get("primary_protected_class")) == pc)
    print(f"  {pc:25s} challenged: {cnt:4d}/{total_pc:4d} ({cnt/total_pc*100:.1f}%)")

print_subheader("Outcome when standing is challenged vs not challenged")
outcome_table(standing_challenged, "Standing challenged")
print()
outcome_table(standing_not, "Standing not challenged")

sc_wr, sc_w, sc_n = win_rate(standing_challenged)
snc_wr, snc_w, snc_n = win_rate(standing_not)
print(f"\n  Win rate when standing challenged: {sc_wr:.1%} ({sc_w}/{sc_n})")
print(f"  Win rate when standing not challenged: {snc_wr:.1%} ({snc_w}/{snc_n})")

if sc_n > 0 and snc_n > 0:
    table_sc = [[sc_w, sc_n - sc_w], [snc_w, snc_n - snc_w]]
    run_fisher_or_chi2(table_sc, "Standing challenged vs not")

# Standing outcome field
print_subheader("Standing challenge outcomes (standing_outcome field)")
so_counter = Counter()
for c in standing_challenged:
    so = safe_str(c.get("standing_outcome"))
    if so:
        so_counter[so] += 1
    else:
        so_counter["(not specified)"] += 1
for so, cnt in sorted(so_counter.items(), key=lambda x: -x[1]):
    print(f"  {so:40s} {cnt:4d}")

print_subheader("Summary: Is standing a barrier?")
print(f"  Standing is challenged in {len(standing_challenged)}/{len(cases)} cases ({len(standing_challenged)/len(cases)*100:.1f}%).")
print(f"  When challenged, plaintiff win rate is {sc_wr:.1%} vs {snc_wr:.1%} when not challenged.")
if sc_wr < snc_wr:
    print("  Standing challenges are associated with WORSE outcomes for plaintiffs.")
else:
    print("  Standing challenges do not appear to significantly harm plaintiffs.")


# ─────────────────────────────────────────────────────────────────────
# ANALYSIS 10: Key Statutes and Case Citations Network
# ─────────────────────────────────────────────────────────────────────
print_header("ANALYSIS 10: Key Statutes and Case Citations Network")

print_subheader("Top 20 most-cited statutes across all cases")
statute_counter = Counter()
for c in cases:
    for s in safe_list(c.get("key_statutes_cited")):
        s_str = safe_str(s)
        if s_str:
            statute_counter[s_str] += 1

for rank, (stat, cnt) in enumerate(sorted(statute_counter.items(), key=lambda x: -x[1])[:20], 1):
    print(f"  {rank:2d}. ({cnt:3d} cases) {stat}")

print_subheader("Top 20 most-cited cases across all cases")
case_cite_counter = Counter()
for c in cases:
    for cc in safe_list(c.get("key_cases_cited")):
        cc_str = safe_str(cc)
        if cc_str:
            case_cite_counter[cc_str] += 1

for rank, (cite, cnt) in enumerate(sorted(case_cite_counter.items(), key=lambda x: -x[1])[:20], 1):
    print(f"  {rank:2d}. ({cnt:3d} cites) {cite[:100]}")

print_subheader("Top 10 most-cited cases in DISABILITY cases specifically")
disab_cite_counter = Counter()
for c in disability_cases:
    for cc in safe_list(c.get("key_cases_cited")):
        cc_str = safe_str(cc)
        if cc_str:
            disab_cite_counter[cc_str] += 1

for rank, (cite, cnt) in enumerate(sorted(disab_cite_counter.items(), key=lambda x: -x[1])[:10], 1):
    print(f"  {rank:2d}. ({cnt:3d} cites) {cite[:100]}")

print_subheader("Summary: What is the doctrinal backbone?")
top_stat = statute_counter.most_common(1)
top_cite = case_cite_counter.most_common(1)
print(f"  Most-cited statute: {top_stat[0][0][:80] if top_stat else 'N/A'} ({top_stat[0][1] if top_stat else 0} cases)")
print(f"  Most-cited case: {top_cite[0][0][:80] if top_cite else 'N/A'} ({top_cite[0][1] if top_cite else 0} citations)")
print(f"  The doctrinal backbone is built on FHA Section 3604(f) provisions and key circuit precedents.")


# ─────────────────────────────────────────────────────────────────────
# EXECUTIVE SUMMARY: TOP 5 FINDINGS
# ─────────────────────────────────────────────────────────────────────
print_header("TOP 5 FINDINGS — Executive Summary")

findings = []

# Finding 1: Disability win rate shift
findings.append(f"1. DISABILITY WIN RATE SHIFT: Disability plaintiff win rate moved from "
                f"{wr_pre_d:.1%} (pre-Loper Bright) to {wr_post_d:.1%} (post-2024). "
                f"RA denial win rates: {ra_wr_pre:.1%} → {ra_wr_post:.1%}.")

# Finding 2: Mental health disparity
if mh and ph:
    mh_wr_f = win_rate(mh)[0]
    ph_wr_f = win_rate(ph)[0]
    findings.append(f"2. MENTAL HEALTH DISPARITY: Mental health plaintiffs win at {mh_wr_f:.1%} "
                    f"vs physical disability at {ph_wr_f:.1%} — a {abs(ph_wr_f-mh_wr_f):.1%} gap.")

# Finding 3: Zoning
findings.append(f"3. ZONING CASES: Plaintiff win rate in zoning cases ({z_wr:.1%}) vs "
                f"non-zoning ({nz_wr:.1%}). {gh_in_zoning}/{len(zoning)} involve group home siting.")

# Finding 4: Standing
findings.append(f"4. STANDING AS BARRIER: Win rate when challenged ({sc_wr:.1%}) vs not "
                f"({snc_wr:.1%}). Standing is challenged in {len(standing_challenged)} cases ({len(standing_challenged)/len(cases)*100:.1f}%).")

# Finding 5: Intersectionality
findings.append(f"5. INTERSECTIONALITY GAP: Intersectional cases win at {int_wr:.1%} vs "
                f"{nint_wr:.1%} for single-class claims. Disability+race-mention cases: {dr_wr:.1%} win rate.")

for f in findings:
    print(f"\n{f}")

print(f"\n{'='*80}")
print(f"  Analysis complete. {len(cases)} cases analyzed across 10 dimensions.")
print(f"{'='*80}")
