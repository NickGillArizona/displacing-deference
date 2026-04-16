"""
Robustness Checks for "Displacing Deference" - FHA Unified Database
=====================================================================
Runs five formal sensitivity analyses on the composition-effect finding.

Central claim: The aggregate decline in plaintiff success rates is driven
by a surge in pro se filings (58.9% -> 76.7%), NOT by courts becoming
hostile to represented plaintiffs (whose win rate recovered to 34.3% in P3).

Checks:
  1. Reclassification Sensitivity - procedural outcomes -> defendant wins
  2. Period-Boundary Sensitivity - shift P2/P3 boundary +/- 2 months
  3. Category Exclusion - drop smallest case categories
  4. Bootstrap Confidence Intervals - 10,000 resamples for P3 represented win rate
  5. Composition Shift Significance - chi-squared and permutation tests
"""

import json
import os
import sys
import math
import copy
import random
from collections import defaultdict
from datetime import datetime

# -- Paths --
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "FHA_Unified_Database.json"
)

# -- Period definitions --
P1_START = "2022-01-01"
P1_END   = "2024-06-28"   # Loper Bright decided
P2_END   = "2025-02-05"   # HUD guidance withdrawal

DECIDED_OUTCOMES = {"PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"}


def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    screened = [r for r in raw if r.get("screening_result", "") != "NO" and r.get("case_name")]
    disab = [r for r in screened if "disability" in [p.lower() for p in (r.get("protected_classes") or [])]]
    return disab


def assign_period(rec, p1_end=P1_END, p2_end=P2_END):
    d = rec.get("date_filed")
    if not d or d < P1_START:
        return None
    if d < p1_end:
        return "P1"
    if d < p2_end:
        return "P2"
    return "P3"


def win_rate_strict(cases):
    decided = [r for r in cases if r.get("outcome") in DECIDED_OUTCOMES]
    n = len(decided)
    if n == 0:
        return 0, 0, 0
    pw = sum(1 for r in decided if r["outcome"] == "PLAINTIFF_WIN")
    return round(100 * pw / n, 1), pw, n


def win_rate_broad(cases):
    decided = [r for r in cases if r.get("outcome") in DECIDED_OUTCOMES]
    n = len(decided)
    if n == 0:
        return 0, 0, 0
    pwm = sum(1 for r in decided if r["outcome"] in ("PLAINTIFF_WIN", "MIXED"))
    return round(100 * pwm / n, 1), pwm, n


def pro_se_share(cases):
    known = [r for r in cases if r.get("pro_se") is not None]
    ps = [r for r in known if r["pro_se"] is True]
    n = len(known)
    if n == 0:
        return 0, 0, 0
    return round(100 * len(ps) / n, 1), len(ps), n


def split_pro_se(cases):
    known = [r for r in cases if r.get("pro_se") is not None]
    ps = [r for r in known if r["pro_se"] is True]
    rep = [r for r in known if r["pro_se"] is False]
    return ps, rep


def chi2_2x2(a, b, c, d):
    n = a + b + c + d
    if n == 0:
        return None, None
    r1, r2 = a + b, c + d
    c1, c2 = a + c, b + d
    cells = [(a, r1*c1/n), (b, r1*c2/n), (c, r2*c1/n), (d, r2*c2/n)]
    chi2 = sum((obs - exp)**2 / exp if exp > 0 else 0 for obs, exp in cells)
    p = math.erfc(math.sqrt(chi2) / math.sqrt(2)) if chi2 > 0 else 1.0
    return round(chi2, 3), round(p, 6)


def pct(num, denom):
    return round(100 * num / denom, 1) if denom else None


# ====================================================================
#  CHECK 1: RECLASSIFICATION SENSITIVITY
# ====================================================================

def check_1_reclassification(disab):
    print("=" * 72)
    print("CHECK 1: RECLASSIFICATION SENSITIVITY")
    print("Reclassifying all non-decided outcomes as DEFENDANT_WIN")
    print("=" * 72)

    dated = [r for r in disab if assign_period(r) is not None]
    for r in dated:
        r["_period"] = assign_period(r)

    p1 = [r for r in dated if r["_period"] == "P1"]
    p2 = [r for r in dated if r["_period"] == "P2"]
    p3 = [r for r in dated if r["_period"] == "P3"]

    # Count non-decided outcomes by period
    print("\n  Non-decided outcomes by period:")
    for label, cases in [("P1", p1), ("P2", p2), ("P3", p3)]:
        outcomes = defaultdict(int)
        for r in cases:
            oc = r.get("outcome", "NONE")
            if oc not in DECIDED_OUTCOMES:
                outcomes[oc] += 1
        total_non = sum(outcomes.values())
        print("    {}: {} non-decided out of {} ({:.1f}%)".format(
            label, total_non, len(cases),
            100 * total_non / len(cases) if cases else 0
        ))
        for oc, n in sorted(outcomes.items(), key=lambda x: -x[1]):
            print("      {}: {}".format(oc, n))

    # Create reclassified copies
    reclass = copy.deepcopy(dated)
    reclassed_count = 0
    for r in reclass:
        if r.get("outcome") not in DECIDED_OUTCOMES:
            r["outcome"] = "DEFENDANT_WIN"
            reclassed_count += 1
    print("\n  Total reclassified: {} cases\n".format(reclassed_count))

    p1r = [r for r in reclass if r["_period"] == "P1"]
    p2r = [r for r in reclass if r["_period"] == "P2"]
    p3r = [r for r in reclass if r["_period"] == "P3"]

    # Table header
    hdr = "{:<35} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}"
    print(hdr.format("Metric", "P1 Base", "P1 Recl", "P2 Base", "P2 Recl", "P3 Base", "P3 Recl"))
    print("-" * 95)

    row = "{:<35} {:>10} {:>10} {:>10} {:>10} {:>10} {:>10}"

    # N decided
    nd1 = len([r for r in p1 if r.get("outcome") in DECIDED_OUTCOMES])
    nd1r = len([r for r in p1r if r.get("outcome") in DECIDED_OUTCOMES])
    nd2 = len([r for r in p2 if r.get("outcome") in DECIDED_OUTCOMES])
    nd2r = len([r for r in p2r if r.get("outcome") in DECIDED_OUTCOMES])
    nd3 = len([r for r in p3 if r.get("outcome") in DECIDED_OUTCOMES])
    nd3r = len([r for r in p3r if r.get("outcome") in DECIDED_OUTCOMES])
    print(row.format("N decided", nd1, nd1r, nd2, nd2r, nd3, nd3r))

    # Aggregate strict win rate
    p1s, _, _ = win_rate_strict(p1); p1sr, _, _ = win_rate_strict(p1r)
    p2s, _, _ = win_rate_strict(p2); p2sr, _, _ = win_rate_strict(p2r)
    p3s, _, _ = win_rate_strict(p3); p3sr, _, _ = win_rate_strict(p3r)
    print(row.format("Agg strict win rate %", p1s, p1sr, p2s, p2sr, p3s, p3sr))

    # Aggregate broad win rate
    p1b, _, _ = win_rate_broad(p1); p1br, _, _ = win_rate_broad(p1r)
    p2b, _, _ = win_rate_broad(p2); p2br, _, _ = win_rate_broad(p2r)
    p3b, _, _ = win_rate_broad(p3); p3br, _, _ = win_rate_broad(p3r)
    print(row.format("Agg broad win rate %", p1b, p1br, p2b, p2br, p3b, p3br))

    # Pro se share (unchanged by reclassification)
    ps1, _, _ = pro_se_share(p1)
    ps2, _, _ = pro_se_share(p2)
    ps3, _, _ = pro_se_share(p3)
    print(row.format("Pro se share % (unchanged)", ps1, ps1, ps2, ps2, ps3, ps3))

    # Pro se win rates
    ps_p1, rep_p1 = split_pro_se(p1)
    ps_p2, rep_p2 = split_pro_se(p2)
    ps_p3, rep_p3 = split_pro_se(p3)
    ps_p1r, rep_p1r = split_pro_se(p1r)
    ps_p2r, rep_p2r = split_pro_se(p2r)
    ps_p3r, rep_p3r = split_pro_se(p3r)

    pss1, _, _ = win_rate_strict(ps_p1); pss1r, _, _ = win_rate_strict(ps_p1r)
    pss2, _, _ = win_rate_strict(ps_p2); pss2r, _, _ = win_rate_strict(ps_p2r)
    pss3, _, _ = win_rate_strict(ps_p3); pss3r, _, _ = win_rate_strict(ps_p3r)
    print(row.format("Pro se strict win rate %", pss1, pss1r, pss2, pss2r, pss3, pss3r))

    reps1, _, _ = win_rate_strict(rep_p1); reps1r, _, _ = win_rate_strict(rep_p1r)
    reps2, _, _ = win_rate_strict(rep_p2); reps2r, _, _ = win_rate_strict(rep_p2r)
    reps3, _, _ = win_rate_strict(rep_p3); reps3r, _, _ = win_rate_strict(rep_p3r)
    print(row.format("Represented strict win rate %", reps1, reps1r, reps2, reps2r, reps3, reps3r))

    repsb1, _, _ = win_rate_broad(rep_p1); repsb1r, _, _ = win_rate_broad(rep_p1r)
    repsb3, _, _ = win_rate_broad(rep_p3); repsb3r, _, _ = win_rate_broad(rep_p3r)
    print(row.format("Represented broad win rate %", repsb1, repsb1r, "", "", repsb3, repsb3r))

    print("\n  COMPOSITION EFFECT TEST (reclassified):")
    print("    P1 represented strict: {}% -> P3 represented strict: {}%".format(reps1r, reps3r))
    print("    P3 pro se share: {}%".format(ps3))
    delta = reps3r - reps1r
    print("    Delta (P3 - P1 rep win rate): {:+.1f} pp".format(delta))
    if delta >= 0:
        print("    RESULT: Finding STRENGTHENED - reclassification raises P3 rep win rate")
    elif abs(delta) < 5:
        print("    RESULT: Finding HOLDS - rep win rate essentially stable (<5pp change)")
    else:
        print("    RESULT: Finding WEAKENED")


# ====================================================================
#  CHECK 2: PERIOD-BOUNDARY SENSITIVITY
# ====================================================================

def check_2_boundary_sensitivity(disab):
    print("\n" + "=" * 72)
    print("CHECK 2: PERIOD-BOUNDARY SENSITIVITY")
    print("Shifting P2/P3 boundary +/- 2 months")
    print("=" * 72)

    boundaries = [
        ("Dec 2024 (early)",   "2024-06-28", "2024-12-05"),
        ("Feb 2025 (original)","2024-06-28", "2025-02-05"),
        ("Apr 2025 (late)",    "2024-06-28", "2025-04-05"),
    ]

    hdr = "\n{:<25} {:>6} {:>6} {:>8} {:>9} {:>10} {:>10}"
    print(hdr.format("Boundary", "P2 N", "P3 N", "P3 PS%", "PS Win%", "Rep Win%", "Agg Win%"))
    print("-" * 76)

    row = "{:<25} {:>6} {:>6} {:>8} {:>9} {:>10} {:>10}"

    for label, p1_end, p2_end in boundaries:
        dated = []
        for r in disab:
            p = assign_period(r, p1_end, p2_end)
            if p is not None:
                r["_period_test"] = p
                dated.append(r)

        p2 = [r for r in dated if r.get("_period_test") == "P2"]
        p3 = [r for r in dated if r.get("_period_test") == "P3"]

        ps_pct_val, _, _ = pro_se_share(p3)
        ps3, rep3 = split_pro_se(p3)
        ps_wr, _, _ = win_rate_strict(ps3)
        rep_wr, _, _ = win_rate_strict(rep3)
        agg_wr, _, _ = win_rate_strict(p3)

        print(row.format(label, len(p2), len(p3), ps_pct_val, ps_wr, rep_wr, agg_wr))

    # Also check P1/P2 boundary
    print("\n  P1/P2 boundary shifts:")
    p12_boundaries = [
        ("Apr 2024 (early)",    "2024-04-28", "2025-02-05"),
        ("Jun 2024 (original)", "2024-06-28", "2025-02-05"),
        ("Aug 2024 (late)",     "2024-08-28", "2025-02-05"),
    ]

    hdr2 = "\n{:<25} {:>6} {:>6} {:>8} {:>12}"
    print(hdr2.format("P1/P2 Boundary", "P1 N", "P2 N", "P1 PS%", "P1 Rep Win%"))
    print("-" * 60)

    row2 = "{:<25} {:>6} {:>6} {:>8} {:>12}"

    for label, p1_end, p2_end in p12_boundaries:
        dated = []
        for r in disab:
            p = assign_period(r, p1_end, p2_end)
            if p is not None:
                r["_period_test"] = p
                dated.append(r)

        p1 = [r for r in dated if r.get("_period_test") == "P1"]
        p2 = [r for r in dated if r.get("_period_test") == "P2"]

        ps_pct_val, _, _ = pro_se_share(p1)
        _, rep1 = split_pro_se(p1)
        rep_wr, _, _ = win_rate_strict(rep1)

        print(row2.format(label, len(p1), len(p2), ps_pct_val, rep_wr))


# ====================================================================
#  CHECK 3: CATEGORY EXCLUSION
# ====================================================================

def check_3_category_exclusion(disab):
    print("\n" + "=" * 72)
    print("CHECK 3: CATEGORY EXCLUSION")
    print("Excluding smallest defendant_type and plaintiff_type categories")
    print("=" * 72)

    dated = [r for r in disab if assign_period(r) is not None]
    for r in dated:
        r["_period"] = assign_period(r)

    dt_counts = defaultdict(int)
    pt_counts = defaultdict(int)
    at_counts = defaultdict(int)
    for r in dated:
        dt_counts[r.get("defendant_type", "UNKNOWN")] += 1
        pt_counts[r.get("plaintiff_type", "UNKNOWN")] += 1
        at_counts[r.get("accommodation_type", "UNKNOWN")] += 1

    print("\n  Defendant type distribution:")
    for dt, n in sorted(dt_counts.items(), key=lambda x: -x[1]):
        print("    {}: {}".format(dt, n))

    print("\n  Plaintiff type distribution:")
    for pt, n in sorted(pt_counts.items(), key=lambda x: -x[1]):
        print("    {}: {}".format(pt, n))

    # Exclude smallest categories (< 5% of total)
    threshold = len(dated) * 0.05
    small_dt = {dt for dt, n in dt_counts.items() if n < threshold}
    small_pt = {pt for pt, n in pt_counts.items() if n < threshold}

    print("\n  Threshold (5% of {} = {:.0f}):".format(len(dated), threshold))
    print("  Small defendant types: {}".format(small_dt))
    print("  Small plaintiff types: {}".format(small_pt))

    filtered = [r for r in dated
                if r.get("defendant_type") not in small_dt
                and r.get("plaintiff_type") not in small_pt]

    print("  Cases after exclusion: {} (removed {})".format(
        len(filtered), len(dated) - len(filtered)))

    p1 = [r for r in filtered if r["_period"] == "P1"]
    p2 = [r for r in filtered if r["_period"] == "P2"]
    p3 = [r for r in filtered if r["_period"] == "P3"]

    hdr = "\n{:<8} {:>5} {:>7} {:>9} {:>10} {:>10}"
    print(hdr.format("Period", "N", "PS%", "PS Win%", "Rep Win%", "Agg Win%"))
    print("-" * 50)

    row = "{:<8} {:>5} {:>7} {:>9} {:>10} {:>10}"

    for label, cases in [("P1", p1), ("P2", p2), ("P3", p3)]:
        ps_pct_val, _, _ = pro_se_share(cases)
        ps, rep = split_pro_se(cases)
        ps_wr, _, _ = win_rate_strict(ps)
        rep_wr, _, _ = win_rate_strict(rep)
        agg_wr, _, _ = win_rate_strict(cases)
        print(row.format(label, len(cases), ps_pct_val, ps_wr, rep_wr, agg_wr))


# ====================================================================
#  CHECK 4: BOOTSTRAP CONFIDENCE INTERVALS
# ====================================================================

def check_4_bootstrap_ci(disab, n_boot=10000):
    print("\n" + "=" * 72)
    print("CHECK 4: BOOTSTRAP CONFIDENCE INTERVALS (n={})".format(n_boot))
    print("Testing whether P3 represented win rate CI overlaps P1")
    print("=" * 72)

    random.seed(42)

    dated = [r for r in disab if assign_period(r) is not None]
    for r in dated:
        r["_period"] = assign_period(r)

    p1 = [r for r in dated if r["_period"] == "P1"]
    p2 = [r for r in dated if r["_period"] == "P2"]
    p3 = [r for r in dated if r["_period"] == "P3"]

    def boot_win_rate(cases, n_iter):
        decided = [r for r in cases if r.get("outcome") in DECIDED_OUTCOMES]
        n = len(decided)
        if n == 0:
            return 0, (0, 0)
        point = sum(1 for r in decided if r["outcome"] == "PLAINTIFF_WIN") / n

        rates = []
        for _ in range(n_iter):
            sample = random.choices(decided, k=n)
            pw = sum(1 for r in sample if r["outcome"] == "PLAINTIFF_WIN")
            rates.append(pw / n)

        rates.sort()
        lo = rates[int(0.025 * n_iter)]
        hi = rates[int(0.975 * n_iter)]
        return round(100 * point, 1), (round(100 * lo, 1), round(100 * hi, 1))

    groups = [
        ("P1 represented", split_pro_se(p1)[1]),
        ("P1 pro se",      split_pro_se(p1)[0]),
        ("P2 represented", split_pro_se(p2)[1]),
        ("P2 pro se",      split_pro_se(p2)[0]),
        ("P3 represented", split_pro_se(p3)[1]),
        ("P3 pro se",      split_pro_se(p3)[0]),
        ("P1 aggregate",   p1),
        ("P2 aggregate",   p2),
        ("P3 aggregate",   p3),
    ]

    hdr = "\n{:<20} {:>10} {:>18} {:>10}"
    print(hdr.format("Group", "Point Est", "95% CI", "N decided"))
    print("-" * 60)

    row = "{:<20} {:>9}% {:>18} {:>10}"

    results = {}
    for name, cases in groups:
        n_dec = len([r for r in cases if r.get("outcome") in DECIDED_OUTCOMES])
        pt, ci = boot_win_rate(cases, n_boot)
        results[name] = (pt, ci, n_dec)
        ci_str = "[{}, {}]".format(ci[0], ci[1])
        print(row.format(name, pt, ci_str, n_dec))

    # Key overlap tests
    p1_rep_ci = results["P1 represented"][1]
    p3_rep_ci = results["P3 represented"][1]
    p1_rep_pt = results["P1 represented"][0]
    p3_rep_pt = results["P3 represented"][0]

    overlap = p3_rep_ci[1] >= p1_rep_ci[0] and p1_rep_ci[1] >= p3_rep_ci[0]
    print("\n  P1 represented: {:.1f}% [{}, {}]".format(p1_rep_pt, p1_rep_ci[0], p1_rep_ci[1]))
    print("  P3 represented: {:.1f}% [{}, {}]".format(p3_rep_pt, p3_rep_ci[0], p3_rep_ci[1]))
    print("  CIs overlap: {}".format("YES" if overlap else "NO"))
    if overlap:
        print("  -> Represented win rate statistically INDISTINGUISHABLE P1 vs P3")
    else:
        print("  -> Represented win rate statistically DIFFERENT P1 vs P3")

    # Pro se share bootstrap
    print("\n  Pro se share bootstrap (95% CI):")
    for label, cases in [("P1", p1), ("P2", p2), ("P3", p3)]:
        known = [r for r in cases if r.get("pro_se") is not None]
        n_known = len(known)
        if n_known == 0:
            continue
        point = sum(1 for r in known if r["pro_se"] is True) / n_known
        shares = []
        for _ in range(n_boot):
            sample = random.choices(known, k=n_known)
            ps_count = sum(1 for r in sample if r["pro_se"] is True)
            shares.append(ps_count / n_known)
        shares.sort()
        lo = shares[int(0.025 * n_boot)]
        hi = shares[int(0.975 * n_boot)]
        print("    {}: {:.1f}% [{:.1f}, {:.1f}] (n={})".format(
            label, 100*point, 100*lo, 100*hi, n_known))


# ====================================================================
#  CHECK 5: COMPOSITION SHIFT SIGNIFICANCE
# ====================================================================

def check_5_composition_significance(disab):
    print("\n" + "=" * 72)
    print("CHECK 5: STATISTICAL SIGNIFICANCE OF COMPOSITION SHIFT")
    print("Chi-squared test for pro se share P1 vs P3")
    print("=" * 72)

    dated = [r for r in disab if assign_period(r) is not None]
    for r in dated:
        r["_period"] = assign_period(r)

    p1 = [r for r in dated if r["_period"] == "P1"]
    p3 = [r for r in dated if r["_period"] == "P3"]

    p1_known = [r for r in p1 if r.get("pro_se") is not None]
    p3_known = [r for r in p3 if r.get("pro_se") is not None]

    p1_ps = sum(1 for r in p1_known if r["pro_se"] is True)
    p1_rep = len(p1_known) - p1_ps
    p3_ps = sum(1 for r in p3_known if r["pro_se"] is True)
    p3_rep = len(p3_known) - p3_ps

    print("\n  P1: {} pro se, {} represented (total {})".format(p1_ps, p1_rep, len(p1_known)))
    print("  P3: {} pro se, {} represented (total {})".format(p3_ps, p3_rep, len(p3_known)))
    print("  P1 pro se share: {:.1f}%".format(100 * p1_ps / len(p1_known)))
    print("  P3 pro se share: {:.1f}%".format(100 * p3_ps / len(p3_known)))

    chi2, p = chi2_2x2(p1_ps, p1_rep, p3_ps, p3_rep)
    print("\n  Chi-squared (pro se share P1 vs P3): chi2={}, p={}".format(chi2, p))
    sig = "YES" if p and p < 0.001 else "NO"
    print("  Significant at p<0.001: {}".format(sig))

    # Win rate tests
    print("\n  Win rate chi-squared tests:")

    rep1 = split_pro_se(p1)[1]
    rep3 = split_pro_se(p3)[1]
    dec_rep1 = [r for r in rep1 if r.get("outcome") in DECIDED_OUTCOMES]
    dec_rep3 = [r for r in rep3 if r.get("outcome") in DECIDED_OUTCOMES]
    pw_rep1 = sum(1 for r in dec_rep1 if r["outcome"] == "PLAINTIFF_WIN")
    pw_rep3 = sum(1 for r in dec_rep3 if r["outcome"] == "PLAINTIFF_WIN")
    chi2_rep, p_rep = chi2_2x2(pw_rep1, len(dec_rep1)-pw_rep1, pw_rep3, len(dec_rep3)-pw_rep3)
    print("    Represented win rate P1 vs P3: chi2={}, p={}".format(chi2_rep, p_rep))
    print("    P1: {:.1f}% ({}/{})".format(100*pw_rep1/len(dec_rep1), pw_rep1, len(dec_rep1)))
    print("    P3: {:.1f}% ({}/{})".format(100*pw_rep3/len(dec_rep3), pw_rep3, len(dec_rep3)))

    dec_p1 = [r for r in p1 if r.get("outcome") in DECIDED_OUTCOMES]
    dec_p3 = [r for r in p3 if r.get("outcome") in DECIDED_OUTCOMES]
    pw_p1 = sum(1 for r in dec_p1 if r["outcome"] == "PLAINTIFF_WIN")
    pw_p3 = sum(1 for r in dec_p3 if r["outcome"] == "PLAINTIFF_WIN")
    chi2_agg, p_agg = chi2_2x2(pw_p1, len(dec_p1)-pw_p1, pw_p3, len(dec_p3)-pw_p3)
    print("\n    Aggregate win rate P1 vs P3: chi2={}, p={}".format(chi2_agg, p_agg))
    print("    P1: {:.1f}% ({}/{})".format(100*pw_p1/len(dec_p1), pw_p1, len(dec_p1)))
    print("    P3: {:.1f}% ({}/{})".format(100*pw_p3/len(dec_p3), pw_p3, len(dec_p3)))

    # Decomposition: how much of aggregate decline is explained by composition?
    print("\n  OAXACA-BLINDER-STYLE DECOMPOSITION:")
    p1_ps_share = p1_ps / len(p1_known)
    p3_ps_share = p3_ps / len(p3_known)
    p1_ps_wr = win_rate_strict(split_pro_se(p1)[0])[0] / 100
    p3_ps_wr = win_rate_strict(split_pro_se(p3)[0])[0] / 100
    p1_rep_wr = win_rate_strict(split_pro_se(p1)[1])[0] / 100
    p3_rep_wr = win_rate_strict(split_pro_se(p3)[1])[0] / 100

    # Aggregate win rates from weighted composition
    p1_agg = p1_ps_share * p1_ps_wr + (1 - p1_ps_share) * p1_rep_wr
    p3_agg = p3_ps_share * p3_ps_wr + (1 - p3_ps_share) * p3_rep_wr

    # Counterfactual: P3 rates with P1 composition
    cf_p1_comp = p1_ps_share * p3_ps_wr + (1 - p1_ps_share) * p3_rep_wr

    total_decline = p3_agg - p1_agg
    composition_effect = p3_agg - cf_p1_comp
    rate_effect = cf_p1_comp - p1_agg

    print("    P1 weighted aggregate: {:.1f}%".format(100 * p1_agg))
    print("    P3 weighted aggregate: {:.1f}%".format(100 * p3_agg))
    print("    Counterfactual (P3 rates, P1 composition): {:.1f}%".format(100 * cf_p1_comp))
    print("    Total decline: {:.1f} pp".format(100 * total_decline))
    print("    Composition effect: {:.1f} pp ({:.0f}% of decline)".format(
        100 * composition_effect,
        100 * abs(composition_effect / total_decline) if total_decline != 0 else 0
    ))
    print("    Rate effect: {:.1f} pp ({:.0f}% of decline)".format(
        100 * rate_effect,
        100 * abs(rate_effect / total_decline) if total_decline != 0 else 0
    ))


# ====================================================================
#  MAIN
# ====================================================================

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("DISPLACING DEFERENCE -- EMPIRICAL ROBUSTNESS CHECKS")
    print("Run date: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    print("Database: {}".format(DB_PATH))
    print()

    disab = load_db()
    print("Loaded {} disability cases from FHA Unified Database".format(len(disab)))

    # Show baseline
    dated = [r for r in disab if assign_period(r) is not None]
    for r in dated:
        r["_period"] = assign_period(r)
    p1 = [r for r in dated if r["_period"] == "P1"]
    p2 = [r for r in dated if r["_period"] == "P2"]
    p3 = [r for r in dated if r["_period"] == "P3"]

    print("\nBASELINE:")
    print("  Dated disability cases: {} (P1:{}, P2:{}, P3:{})".format(
        len(dated), len(p1), len(p2), len(p3)))
    for label, cases in [("P1", p1), ("P2", p2), ("P3", p3)]:
        ps_pct_val, _, _ = pro_se_share(cases)
        ps, rep = split_pro_se(cases)
        ps_wr, _, _ = win_rate_strict(ps)
        rep_wr, _, _ = win_rate_strict(rep)
        agg_wr, _, _ = win_rate_strict(cases)
        print("  {}: PS share={:.1f}%, PS win={:.1f}%, Rep win={:.1f}%, Agg win={:.1f}%".format(
            label, ps_pct_val, ps_wr, rep_wr, agg_wr))

    print()
    check_1_reclassification(disab)
    check_2_boundary_sensitivity(disab)
    check_3_category_exclusion(disab)
    check_4_bootstrap_ci(disab)
    check_5_composition_significance(disab)

    print("\n" + "=" * 72)
    print("ALL ROBUSTNESS CHECKS COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
