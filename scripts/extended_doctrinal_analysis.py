#!/usr/bin/env python3
"""
Extended Doctrinal Analysis for Disability-Centered AFFH Note
==============================================================
Three deeper analyses of the FHA Unified Database:

  1. Iqbal/Twombly Evolution Analysis
     - Citation frequency by period (P1, P2, P3) in disability cases
     - Citation rates by plaintiff representation status
     - Citation rates by claim type (specific-duty vs open-textured)
     - Whether Iqbal/Twombly correlates with pro se filings
     - Temporal trends in pleading standard invocation

  2. Settlement Rate Estimation (Iceberg Correction)
     - Voluntary-dismissal / settlement proxies by representation
     - Estimated "true" represented win rate if settlements were wins
     - Effect on composition-effect finding

  3. Circuit-Level Doctrinal Trends
     - Iqbal/Twombly citation rate by circuit
     - Pro se surge by circuit
     - Circuit conservatism proxy (Republican-appointed judges in circuit)
     - P1-to-P3 decline by circuit
     - Circuit-specific patterns

Outputs console results plus a JSON dump of all findings.
"""
import json
import re
from collections import Counter, defaultdict
from statistics import mean

from config import UNIFIED_DB_PATH, RESULTS_DIR
import os

# ── Load database ────────────────────────────────────────────────────────────
with open(UNIFIED_DB_PATH, "r", encoding="utf-8") as f:
    cases = json.load(f)

print(f"Total cases loaded: {len(cases)}\n")

# ── Filter to disability cases (screened-in) ─────────────────────────────────
def is_disability(c):
    return (c.get("primary_protected_class") == "disability"
            or "disability" in (c.get("protected_classes") or []))

disability = [c for c in cases if is_disability(c)
              and c.get("screening_result") == "YES"]
print(f"Disability cases (screened-in): {len(disability)}\n")

# ── Period classification ────────────────────────────────────────────────────
# Three-period framework used in Appendix C:
#   P1 = 2013-2020 (mature post-Iqbal baseline)
#   P2 = 2021-2022 (immediate pre-Loper Bright)
#   P3 = 2023-2026 (post-Loper Bright environment)
def period_of(year):
    if year is None:
        return None
    if year <= 2020:
        return "P1"
    if year <= 2022:
        return "P2"
    return "P3"

for c in disability:
    c["_period"] = period_of(c.get("year"))

dated = [c for c in disability if c["_period"]]
print(f"Dated disability cases: {len(dated)}")
p_counts = Counter(c["_period"] for c in dated)
for p in ("P1", "P2", "P3"):
    print(f"  {p}: {p_counts[p]}")
print()

# ── Helpers ──────────────────────────────────────────────────────────────────
def pct(num, denom):
    if not denom:
        return "0/0 (N/A)"
    return f"{num}/{denom} ({100*num/denom:.1f}%)"

def rate(num, denom):
    return 100.0 * num / denom if denom else 0.0

def is_mtd(c):
    return (c.get("procedural_posture") or "").upper() == "MOTION_TO_DISMISS"

def cites_iqbal_twombly(c):
    """Uses the boolean field, with fallback to key_cases_cited list."""
    if c.get("iqbal_twombly_cited") is True:
        return True
    kcc = c.get("key_cases_cited") or []
    if isinstance(kcc, list):
        joined = " ".join(str(x) for x in kcc).lower()
        return "iqbal" in joined or "twombly" in joined
    return False

def is_pro_se(c):
    return c.get("pro_se") is True

def def_win(c):
    return c.get("outcome") == "DEFENDANT_WIN"

def pl_win(c):
    return c.get("outcome") == "PLAINTIFF_WIN"

def mixed_outcome(c):
    return c.get("outcome") == "MIXED"

def broad_win(c):
    return c.get("outcome") in ("PLAINTIFF_WIN", "MIXED")

# Claim type taxonomy (specific-duty vs open-textured).
# Specific-duty claims impose a discrete affirmative obligation on housing
# providers (reasonable accommodation, modification, design-and-construction).
# Open-textured claims require inferential proof of discriminatory motive or
# effect (disparate treatment, disparate impact, interference, retaliation).
SPECIFIC_DUTY = {
    "reasonable_accommodation_denial",
    "REASONABLE_ACCOMMODATION",
    "reasonable_modification_denial",
    "design_and_construction",
    "DESIGN_AND_CONSTRUCTION",
}
OPEN_TEXTURED = {
    "disparate_treatment",
    "DISPARATE_TREATMENT",
    "disparate_impact",
    "interference_coercion",
    "retaliation",
    "discriminatory_advertising",
    "discriminatory_lending",
}

def claim_family(c):
    pt = c.get("primary_claim_type") or ""
    if pt in SPECIFIC_DUTY:
        return "specific_duty"
    if pt in OPEN_TEXTURED:
        return "open_textured"
    return "other"

# Settlement proxies.
# We treat the following as "likely settled/resolved in plaintiff's favor":
#   1. Existing outcome == "SETTLEMENT"
#   2. procedural_posture == "SETTLEMENT_CONSENT"
#   3. Any fha_claim dismissal_reason == "SETTLEMENT"
#   4. Free-text settlement/voluntary-dismissal language in key_holding
#      or brief_summary (joint motion, Rule 41(a), stipulated dismissal,
#      consent decree, settlement agreement, etc.)
SETTLE_PATTERN = re.compile(
    r"(voluntary\s+dismiss|stipulat(?:ed|ion)\s+of\s+dismiss|stipulat(?:ed|ion)\s+to\s+dismiss|"
    r"joint\s+stipulat|settl(?:ed|ement)(?:\s+agreement)?|rule\s*41\s*\(a\)|consent\s+decree|"
    r"consent\s+judgment|agreed\s+to\s+dismiss|parties\s+have\s+settled)",
    re.IGNORECASE,
)

def settlement_proxy(c):
    """Return True if this case is likely a settlement."""
    if c.get("outcome") == "SETTLEMENT":
        return True
    if (c.get("procedural_posture") or "").upper() == "SETTLEMENT_CONSENT":
        return True
    for claim in (c.get("fha_claims") or []):
        if (claim.get("dismissal_reason") or "").upper() == "SETTLEMENT":
            return True
    kh = c.get("key_holding") or ""
    bs = c.get("brief_summary") or ""
    if SETTLE_PATTERN.search(kh) or SETTLE_PATTERN.search(bs):
        return True
    return False

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 1: IQBAL / TWOMBLY EVOLUTION
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 80)
print("ANALYSIS 1: IQBAL / TWOMBLY EVOLUTION")
print("=" * 80)

results_1 = {}

# 1a. Citation frequency by period
print("\n1a. Iqbal/Twombly citation rate by period (all disability cases)")
print(f"  {'Period':<8}{'Cases':>8}{'Cited':>8}{'Rate':>10}")
a1a = {}
for p in ("P1", "P2", "P3"):
    p_cases = [c for c in dated if c["_period"] == p]
    cited = sum(1 for c in p_cases if cites_iqbal_twombly(c))
    print(f"  {p:<8}{len(p_cases):>8}{cited:>8}{rate(cited, len(p_cases)):>9.1f}%")
    a1a[p] = {"n": len(p_cases), "cited": cited, "rate": round(rate(cited, len(p_cases)), 2)}
results_1["1a_citation_by_period"] = a1a

# 1a-MTD: same but restricted to MTD posture
print("\n1a-MTD. Iqbal/Twombly citation rate by period (disability MTD only)")
print(f"  {'Period':<8}{'MTD':>8}{'Cited':>8}{'Rate':>10}")
a1a_mtd = {}
for p in ("P1", "P2", "P3"):
    p_cases = [c for c in dated if c["_period"] == p and is_mtd(c)]
    cited = sum(1 for c in p_cases if cites_iqbal_twombly(c))
    print(f"  {p:<8}{len(p_cases):>8}{cited:>8}{rate(cited, len(p_cases)):>9.1f}%")
    a1a_mtd[p] = {"n": len(p_cases), "cited": cited, "rate": round(rate(cited, len(p_cases)), 2)}
results_1["1a_citation_by_period_mtd"] = a1a_mtd

# 1b. Citation by representation
print("\n1b. Iqbal/Twombly citation rate by representation status")
print(f"  {'Rep':<14}{'Cases':>8}{'Cited':>8}{'Rate':>10}")
a1b = {}
for label, fn in (("Pro se", is_pro_se),
                  ("Represented", lambda c: not is_pro_se(c))):
    subset = [c for c in dated if fn(c)]
    cited = sum(1 for c in subset if cites_iqbal_twombly(c))
    print(f"  {label:<14}{len(subset):>8}{cited:>8}{rate(cited, len(subset)):>9.1f}%")
    a1b[label] = {"n": len(subset), "cited": cited, "rate": round(rate(cited, len(subset)), 2)}
results_1["1b_citation_by_representation"] = a1b

# 1b-period: period x representation
print("\n1b-period. Iqbal/Twombly citation rate by period x representation")
print(f"  {'Period':<8}{'Rep':<14}{'Cases':>8}{'Cited':>8}{'Rate':>10}")
a1b_period = {}
for p in ("P1", "P2", "P3"):
    a1b_period[p] = {}
    for label, fn in (("Pro se", is_pro_se),
                      ("Represented", lambda c: not is_pro_se(c))):
        subset = [c for c in dated if c["_period"] == p and fn(c)]
        cited = sum(1 for c in subset if cites_iqbal_twombly(c))
        print(f"  {p:<8}{label:<14}{len(subset):>8}{cited:>8}{rate(cited, len(subset)):>9.1f}%")
        a1b_period[p][label] = {"n": len(subset), "cited": cited,
                                "rate": round(rate(cited, len(subset)), 2)}
results_1["1b_period_x_representation"] = a1b_period

# 1b-MTD: period x representation within MTD stage
print("\n1b-MTD. Iqbal/Twombly citation rate by period x representation (MTD only)")
print(f"  {'Period':<8}{'Rep':<14}{'MTD':>8}{'Cited':>8}{'Rate':>10}")
a1b_period_mtd = {}
for p in ("P1", "P2", "P3"):
    a1b_period_mtd[p] = {}
    for label, fn in (("Pro se", is_pro_se),
                      ("Represented", lambda c: not is_pro_se(c))):
        subset = [c for c in dated if c["_period"] == p and is_mtd(c) and fn(c)]
        cited = sum(1 for c in subset if cites_iqbal_twombly(c))
        print(f"  {p:<8}{label:<14}{len(subset):>8}{cited:>8}{rate(cited, len(subset)):>9.1f}%")
        a1b_period_mtd[p][label] = {"n": len(subset), "cited": cited,
                                    "rate": round(rate(cited, len(subset)), 2)}
results_1["1b_period_x_representation_mtd"] = a1b_period_mtd

# 1c. Citation by claim type (specific-duty vs open-textured)
print("\n1c. Iqbal/Twombly citation rate by claim type")
print(f"  {'Family':<18}{'Cases':>8}{'Cited':>8}{'Rate':>10}")
a1c = {}
for fam in ("specific_duty", "open_textured", "other"):
    subset = [c for c in dated if claim_family(c) == fam]
    cited = sum(1 for c in subset if cites_iqbal_twombly(c))
    print(f"  {fam:<18}{len(subset):>8}{cited:>8}{rate(cited, len(subset)):>9.1f}%")
    a1c[fam] = {"n": len(subset), "cited": cited, "rate": round(rate(cited, len(subset)), 2)}
results_1["1c_citation_by_claim_family"] = a1c

# 1c-period: family x period
print("\n1c-period. Iqbal/Twombly citation rate by period x claim family")
print(f"  {'Period':<8}{'Family':<18}{'Cases':>8}{'Cited':>8}{'Rate':>10}")
a1c_period = {}
for p in ("P1", "P2", "P3"):
    a1c_period[p] = {}
    for fam in ("specific_duty", "open_textured", "other"):
        subset = [c for c in dated if c["_period"] == p and claim_family(c) == fam]
        cited = sum(1 for c in subset if cites_iqbal_twombly(c))
        print(f"  {p:<8}{fam:<18}{len(subset):>8}{cited:>8}{rate(cited, len(subset)):>9.1f}%")
        a1c_period[p][fam] = {"n": len(subset), "cited": cited,
                              "rate": round(rate(cited, len(subset)), 2)}
results_1["1c_period_x_family"] = a1c_period

# 1d. Correlation between Iqbal/Twombly and pro se (2x2 odds ratio)
print("\n1d. 2x2 contingency: Iqbal/Twombly x Pro se (all disability, MTD)")
ct = {"pro_se_cited": 0, "pro_se_nocited": 0,
      "rep_cited": 0, "rep_nocited": 0}
for c in dated:
    if not is_mtd(c):
        continue
    cited = cites_iqbal_twombly(c)
    pro = is_pro_se(c)
    if cited and pro:     ct["pro_se_cited"] += 1
    elif not cited and pro: ct["pro_se_nocited"] += 1
    elif cited and not pro: ct["rep_cited"] += 1
    else:                 ct["rep_nocited"] += 1
print(f"                 Cited    Not cited")
print(f"  Pro se         {ct['pro_se_cited']:>5}    {ct['pro_se_nocited']:>5}")
print(f"  Represented    {ct['rep_cited']:>5}    {ct['rep_nocited']:>5}")
# Odds ratio
num = ct["pro_se_cited"] * ct["rep_nocited"]
den = ct["pro_se_nocited"] * ct["rep_cited"]
or_val = num / den if den else float("inf")
print(f"  Odds ratio (pro se cited|Iqbal): {or_val:.3f}")
# Chi-square (manual, no scipy dependency)
total = sum(ct.values())
row_pro = ct["pro_se_cited"] + ct["pro_se_nocited"]
row_rep = ct["rep_cited"] + ct["rep_nocited"]
col_cited = ct["pro_se_cited"] + ct["rep_cited"]
col_nocit = ct["pro_se_nocited"] + ct["rep_nocited"]
if total:
    exp = {
        "pro_se_cited":   row_pro * col_cited / total,
        "pro_se_nocited": row_pro * col_nocit / total,
        "rep_cited":      row_rep * col_cited / total,
        "rep_nocited":    row_rep * col_nocit / total,
    }
    chi2 = sum((ct[k] - exp[k]) ** 2 / exp[k] for k in ct if exp[k] > 0)
    print(f"  Chi-squared (df=1): {chi2:.3f}")
else:
    chi2 = None
results_1["1d_mtd_contingency"] = {"table": ct, "odds_ratio": round(or_val, 4),
                                   "chi2": round(chi2, 4) if chi2 is not None else None}

# 1e. Temporal trends in outcomes conditioned on Iqbal/Twombly citation
print("\n1e. MTD outcomes by period x Iqbal-citation status")
print(f"  {'Period':<8}{'Cite':<8}{'N':>6}{'DW':>6}{'PW':>6}{'Mix':>6}{'PW%':>7}{'Broad%':>9}")
a1e = {}
for p in ("P1", "P2", "P3"):
    a1e[p] = {}
    for label, fn in (("Cite I/T", cites_iqbal_twombly),
                      ("No Cite", lambda c: not cites_iqbal_twombly(c))):
        subset = [c for c in dated if c["_period"] == p and is_mtd(c) and fn(c)]
        n = len(subset)
        dw = sum(1 for c in subset if def_win(c))
        pw = sum(1 for c in subset if pl_win(c))
        mx = sum(1 for c in subset if mixed_outcome(c))
        bw = pw + mx
        print(f"  {p:<8}{label:<8}{n:>6}{dw:>6}{pw:>6}{mx:>6}{rate(pw,n):>6.1f}%{rate(bw,n):>8.1f}%")
        a1e[p][label] = {"n": n, "dw": dw, "pw": pw, "mixed": mx,
                         "strict_pw_rate": round(rate(pw, n), 2),
                         "broad_win_rate": round(rate(bw, n), 2)}
results_1["1e_mtd_outcomes_by_period_citation"] = a1e

# 1e-rep: period x representation x Iqbal-citation for MTD cases
print("\n1e-rep. MTD outcomes by period x representation x Iqbal/Twombly citation")
print(f"  {'Period':<8}{'Rep':<14}{'Cite':<8}{'N':>6}{'DW%':>7}{'Broad%':>9}")
a1e_rep = {}
for p in ("P1", "P2", "P3"):
    a1e_rep[p] = {}
    for rep_label, rep_fn in (("Pro se", is_pro_se),
                              ("Represented", lambda c: not is_pro_se(c))):
        a1e_rep[p][rep_label] = {}
        for cite_label, cite_fn in (("Cite", cites_iqbal_twombly),
                                     ("NoCite", lambda c: not cites_iqbal_twombly(c))):
            subset = [c for c in dated
                      if c["_period"] == p and is_mtd(c) and rep_fn(c) and cite_fn(c)]
            n = len(subset)
            dw = sum(1 for c in subset if def_win(c))
            bw = sum(1 for c in subset if broad_win(c))
            print(f"  {p:<8}{rep_label:<14}{cite_label:<8}{n:>6}{rate(dw,n):>6.1f}%{rate(bw,n):>8.1f}%")
            a1e_rep[p][rep_label][cite_label] = {
                "n": n, "dw": dw, "broad_win": bw,
                "dw_rate": round(rate(dw, n), 2),
                "broad_win_rate": round(rate(bw, n), 2),
            }
results_1["1e_mtd_by_period_rep_citation"] = a1e_rep

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 2: SETTLEMENT RATE ESTIMATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n" + "=" * 80)
print("ANALYSIS 2: SETTLEMENT RATE ESTIMATION (ICEBERG CORRECTION)")
print("=" * 80)

results_2 = {}

# 2a. Overall settlement-proxy rate by representation
print("\n2a. Settlement-proxy rate by representation (all disability cases)")
print(f"  {'Rep':<14}{'Cases':>8}{'Settle':>8}{'Rate':>10}")
a2a = {}
for label, fn in (("Pro se", is_pro_se),
                  ("Represented", lambda c: not is_pro_se(c))):
    subset = [c for c in dated if fn(c)]
    n = len(subset)
    s = sum(1 for c in subset if settlement_proxy(c))
    print(f"  {label:<14}{n:>8}{s:>8}{rate(s,n):>9.1f}%")
    a2a[label] = {"n": n, "settled": s, "rate": round(rate(s, n), 2)}
results_2["2a_settlement_by_representation"] = a2a

# 2b. Settlement by period x representation
print("\n2b. Settlement-proxy rate by period x representation")
print(f"  {'Period':<8}{'Rep':<14}{'Cases':>8}{'Settle':>8}{'Rate':>10}")
a2b = {}
for p in ("P1", "P2", "P3"):
    a2b[p] = {}
    for label, fn in (("Pro se", is_pro_se),
                      ("Represented", lambda c: not is_pro_se(c))):
        subset = [c for c in dated if c["_period"] == p and fn(c)]
        n = len(subset)
        s = sum(1 for c in subset if settlement_proxy(c))
        print(f"  {p:<8}{label:<14}{n:>8}{s:>8}{rate(s,n):>9.1f}%")
        a2b[p][label] = {"n": n, "settled": s, "rate": round(rate(s, n), 2)}
results_2["2b_settlement_by_period_representation"] = a2b

# 2c. Observed win rates by representation (baseline)
print("\n2c. Observed plaintiff win rates by representation x period")
print(f"  {'Period':<8}{'Rep':<14}{'N':>6}{'Strict%':>9}{'Broad%':>9}")
a2c = {}
for p in ("P1", "P2", "P3"):
    a2c[p] = {}
    for label, fn in (("Pro se", is_pro_se),
                      ("Represented", lambda c: not is_pro_se(c))):
        subset = [c for c in dated if c["_period"] == p and fn(c)]
        # Exclude cases we flagged as settlement proxies to avoid double-count
        decided = [c for c in subset if not settlement_proxy(c)]
        n = len(decided)
        pw = sum(1 for c in decided if pl_win(c))
        bw = sum(1 for c in decided if broad_win(c))
        print(f"  {p:<8}{label:<14}{n:>6}{rate(pw,n):>8.1f}%{rate(bw,n):>8.1f}%")
        a2c[p][label] = {"n": n, "strict": round(rate(pw, n), 2),
                         "broad": round(rate(bw, n), 2)}
results_2["2c_observed_win_rates"] = a2c

# 2d. Adjusted win rates counting settlements as plaintiff wins
print("\n2d. Adjusted plaintiff win rates (counting settlements as plaintiff wins)")
print(f"  {'Period':<8}{'Rep':<14}{'N':>6}{'Adj Strict%':>13}{'Adj Broad%':>13}")
a2d = {}
for p in ("P1", "P2", "P3"):
    a2d[p] = {}
    for label, fn in (("Pro se", is_pro_se),
                      ("Represented", lambda c: not is_pro_se(c))):
        subset = [c for c in dated if c["_period"] == p and fn(c)]
        n = len(subset)
        pw = sum(1 for c in subset if pl_win(c))
        bw = sum(1 for c in subset if broad_win(c))
        s = sum(1 for c in subset if settlement_proxy(c))
        # Treat settlements as plaintiff wins (iceberg correction)
        adj_pw = pw + s
        adj_bw = bw + s
        # Subtract any settlements already captured in PLAINTIFF_WIN/MIXED to avoid double count
        already = sum(1 for c in subset if settlement_proxy(c) and broad_win(c))
        adj_pw -= sum(1 for c in subset if settlement_proxy(c) and pl_win(c))
        adj_bw -= already
        print(f"  {p:<8}{label:<14}{n:>6}{rate(adj_pw,n):>12.1f}%{rate(adj_bw,n):>12.1f}%")
        a2d[p][label] = {"n": n,
                         "adj_strict": round(rate(adj_pw, n), 2),
                         "adj_broad": round(rate(adj_bw, n), 2),
                         "settled_n": s}
results_2["2d_adjusted_win_rates"] = a2d

# 2e. Composition-effect check: how much does adjustment close the gap?
print("\n2e. Rep-vs-pro-se gap, observed vs adjusted (broad win rate)")
print(f"  {'Period':<8}{'Obs Gap':>12}{'Adj Gap':>12}{'Closed':>10}")
a2e = {}
for p in ("P1", "P2", "P3"):
    obs_rep = a2c[p]["Represented"]["broad"]
    obs_pro = a2c[p]["Pro se"]["broad"]
    adj_rep = a2d[p]["Represented"]["adj_broad"]
    adj_pro = a2d[p]["Pro se"]["adj_broad"]
    obs_gap = obs_rep - obs_pro
    adj_gap = adj_rep - adj_pro
    closed = obs_gap - adj_gap
    print(f"  {p:<8}{obs_gap:>11.1f}%{adj_gap:>11.1f}%{closed:>9.1f}%")
    a2e[p] = {"obs_gap_pp": round(obs_gap, 2),
              "adj_gap_pp": round(adj_gap, 2),
              "gap_change_pp": round(closed, 2)}
results_2["2e_gap_change"] = a2e

# 2f. Settlement-proxy rate by claim family
print("\n2f. Settlement-proxy rate by claim family")
print(f"  {'Family':<18}{'Cases':>8}{'Settle':>8}{'Rate':>10}")
a2f = {}
for fam in ("specific_duty", "open_textured", "other"):
    subset = [c for c in dated if claim_family(c) == fam]
    n = len(subset)
    s = sum(1 for c in subset if settlement_proxy(c))
    print(f"  {fam:<18}{n:>8}{s:>8}{rate(s,n):>9.1f}%")
    a2f[fam] = {"n": n, "settled": s, "rate": round(rate(s, n), 2)}
results_2["2f_settlement_by_claim_family"] = a2f

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 3: CIRCUIT-LEVEL DOCTRINAL TRENDS
# ─────────────────────────────────────────────────────────────────────────────
print("\n\n" + "=" * 80)
print("ANALYSIS 3: CIRCUIT-LEVEL DOCTRINAL TRENDS")
print("=" * 80)

results_3 = {}

# Circuit list in standard order
CIRCUITS = [
    "1st Circuit", "2nd Circuit", "3rd Circuit", "4th Circuit",
    "5th Circuit", "6th Circuit", "7th Circuit", "8th Circuit",
    "9th Circuit", "10th Circuit", "11th Circuit", "D.C. Circuit",
]

# Rough "conservatism" proxy -- share of active judges appointed by Republican
# presidents. Approximations as of April 2026 based on public seat-count data;
# used only as a qualitative sort, not a causal variable.
CIRCUIT_CONSERVATISM = {
    "1st Circuit":  0.17,  # 1R / 6 active
    "2nd Circuit":  0.31,  # ~4/13
    "3rd Circuit":  0.43,  # ~6/14
    "4th Circuit":  0.47,  # ~7/15
    "5th Circuit":  0.76,  # ~13/17
    "6th Circuit":  0.63,  # ~10/16
    "7th Circuit":  0.36,  # ~4/11
    "8th Circuit":  0.82,  # ~9/11
    "9th Circuit":  0.31,  # ~9/29
    "10th Circuit": 0.42,  # ~5/12
    "11th Circuit": 0.75,  # ~9/12
    "D.C. Circuit": 0.36,  # ~4/11
}

# 3a. Iqbal/Twombly citation rate by circuit (disability cases)
print("\n3a. Iqbal/Twombly citation rate by circuit (disability cases, n>=20)")
print(f"  {'Circuit':<16}{'N':>6}{'Cited':>8}{'Rate':>9}")
a3a = {}
for circ in CIRCUITS:
    subset = [c for c in dated if c.get("circuit") == circ]
    n = len(subset)
    if n < 20:
        continue
    cited = sum(1 for c in subset if cites_iqbal_twombly(c))
    print(f"  {circ:<16}{n:>6}{cited:>8}{rate(cited, n):>8.1f}%")
    a3a[circ] = {"n": n, "cited": cited, "rate": round(rate(cited, n), 2),
                 "conservatism": CIRCUIT_CONSERVATISM.get(circ)}
results_3["3a_iqbal_by_circuit"] = a3a

# 3b. P1 -> P3 decline in broad win rate by circuit
print("\n3b. Broad plaintiff win-rate decline P1 -> P3 by circuit (disability, both n>=10)")
print(f"  {'Circuit':<16}{'P1 N':>6}{'P1 Broad':>10}{'P3 N':>6}{'P3 Broad':>10}{'Delta pp':>10}")
a3b = {}
for circ in CIRCUITS:
    p1 = [c for c in dated if c.get("circuit") == circ and c["_period"] == "P1"]
    p3 = [c for c in dated if c.get("circuit") == circ and c["_period"] == "P3"]
    if len(p1) < 10 or len(p3) < 10:
        continue
    p1_bw = rate(sum(1 for c in p1 if broad_win(c)), len(p1))
    p3_bw = rate(sum(1 for c in p3 if broad_win(c)), len(p3))
    delta = p3_bw - p1_bw
    print(f"  {circ:<16}{len(p1):>6}{p1_bw:>9.1f}%{len(p3):>6}{p3_bw:>9.1f}%{delta:>+9.1f}")
    a3b[circ] = {"p1_n": len(p1), "p1_broad": round(p1_bw, 2),
                 "p3_n": len(p3), "p3_broad": round(p3_bw, 2),
                 "delta_pp": round(delta, 2),
                 "conservatism": CIRCUIT_CONSERVATISM.get(circ)}
results_3["3b_p1_p3_decline"] = a3b

# 3c. Correlation: conservatism proxy vs. P1->P3 decline and Iqbal citation rate
print("\n3c. Pearson correlations across circuits")
# Build paired lists
paired_decline = [(a3b[c]["conservatism"], a3b[c]["delta_pp"])
                  for c in a3b if a3b[c]["conservatism"] is not None]
paired_iqbal = [(a3a[c]["conservatism"], a3a[c]["rate"])
                for c in a3a if a3a[c]["conservatism"] is not None]

def pearson(pairs):
    n = len(pairs)
    if n < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = mean(xs); my = mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in pairs) / n
    sx = (sum((x - mx) ** 2 for x in xs) / n) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys) / n) ** 0.5
    if sx == 0 or sy == 0:
        return None
    return cov / (sx * sy)

r_decline = pearson(paired_decline)
r_iqbal = pearson(paired_iqbal)
print(f"  Conservatism x (P3 - P1 broad win): r = {r_decline:.3f} (n={len(paired_decline)})"
      if r_decline is not None else "  Conservatism x decline: insufficient data")
print(f"  Conservatism x Iqbal citation rate: r = {r_iqbal:.3f} (n={len(paired_iqbal)})"
      if r_iqbal is not None else "  Conservatism x Iqbal rate: insufficient data")
results_3["3c_correlations"] = {
    "conservatism_vs_decline": round(r_decline, 4) if r_decline is not None else None,
    "conservatism_vs_iqbal_rate": round(r_iqbal, 4) if r_iqbal is not None else None,
    "n_circuits_decline": len(paired_decline),
    "n_circuits_iqbal": len(paired_iqbal),
}

# 3d. Pro se surge by circuit (P1 pro se share vs P3 pro se share)
print("\n3d. Pro se share P1 vs P3 by circuit (disability, both periods n>=10)")
print(f"  {'Circuit':<16}{'P1 %':>8}{'P3 %':>8}{'Delta pp':>10}")
a3d = {}
for circ in CIRCUITS:
    p1 = [c for c in dated if c.get("circuit") == circ and c["_period"] == "P1"]
    p3 = [c for c in dated if c.get("circuit") == circ and c["_period"] == "P3"]
    if len(p1) < 10 or len(p3) < 10:
        continue
    p1_ps = rate(sum(1 for c in p1 if is_pro_se(c)), len(p1))
    p3_ps = rate(sum(1 for c in p3 if is_pro_se(c)), len(p3))
    delta = p3_ps - p1_ps
    print(f"  {circ:<16}{p1_ps:>7.1f}%{p3_ps:>7.1f}%{delta:>+9.1f}")
    a3d[circ] = {"p1_prose": round(p1_ps, 2), "p3_prose": round(p3_ps, 2),
                 "delta_pp": round(delta, 2)}
results_3["3d_pro_se_surge"] = a3d

# 3e. Circuit-level MTD dismissal rate by period
print("\n3e. MTD defendant-win rate by circuit x period (disability, each cell n>=5)")
print(f"  {'Circuit':<16}{'P1 DW%':>10}{'P2 DW%':>10}{'P3 DW%':>10}{'P1->P3 pp':>12}")
a3e = {}
for circ in CIRCUITS:
    row = {"circuit": circ, "periods": {}}
    dws = {}
    ns = {}
    for p in ("P1", "P2", "P3"):
        subset = [c for c in dated if c.get("circuit") == circ
                  and c["_period"] == p and is_mtd(c)]
        if len(subset) < 5:
            dws[p] = None
            ns[p] = len(subset)
            continue
        dw = sum(1 for c in subset if def_win(c))
        dws[p] = round(rate(dw, len(subset)), 2)
        ns[p] = len(subset)
    if all(dws[p] is not None for p in ("P1", "P3")):
        delta = dws["P3"] - dws["P1"]
    else:
        delta = None
    d_strs = {p: f"{dws[p]:.1f}%" if dws[p] is not None else "  n/a"
              for p in ("P1", "P2", "P3")}
    d_str = f"{delta:+.1f}" if delta is not None else "  n/a"
    print(f"  {circ:<16}{d_strs['P1']:>10}{d_strs['P2']:>10}{d_strs['P3']:>10}{d_str:>12}")
    row["periods"] = {p: {"n": ns[p], "dw_rate": dws[p]} for p in ("P1", "P2", "P3")}
    row["p1_p3_delta"] = delta
    a3e[circ] = row
results_3["3e_mtd_dw_by_circuit_period"] = a3e

# 3f. Ranking of circuits by "most collapsed" (greatest P1->P3 broad decline)
print("\n3f. Circuits ranked by broad win-rate decline (P1 -> P3)")
ranked = sorted(
    [(c, a3b[c]["delta_pp"]) for c in a3b],
    key=lambda x: x[1],
)
for i, (circ, d) in enumerate(ranked):
    print(f"  {i+1:2d}. {circ:<16}{d:+.1f} pp")
results_3["3f_decline_ranking"] = [{"circuit": c, "delta": d} for c, d in ranked]

# 3g. Circuit-specific Iqbal citation rate vs MTD defendant-win rate (correlation)
print("\n3g. Circuit-level correlation: Iqbal citation rate x MTD defendant-win rate")
circuit_pairs = []
for circ in CIRCUITS:
    mtd_subset = [c for c in dated if c.get("circuit") == circ and is_mtd(c)]
    if len(mtd_subset) < 20:
        continue
    ir = rate(sum(1 for c in mtd_subset if cites_iqbal_twombly(c)), len(mtd_subset))
    dwr = rate(sum(1 for c in mtd_subset if def_win(c)), len(mtd_subset))
    circuit_pairs.append((circ, ir, dwr))

print(f"  {'Circuit':<16}{'Iqbal %':>10}{'MTD DW %':>11}")
for circ, ir, dwr in circuit_pairs:
    print(f"  {circ:<16}{ir:>9.1f}%{dwr:>10.1f}%")
r_iqbal_dw = pearson([(p[1], p[2]) for p in circuit_pairs])
if r_iqbal_dw is not None:
    print(f"\n  Pearson r (Iqbal rate vs MTD DW rate) = {r_iqbal_dw:.3f} (n={len(circuit_pairs)})")
results_3["3g_iqbal_vs_dw_correlation"] = {
    "pairs": [{"circuit": p[0], "iqbal_rate": round(p[1], 2),
               "mtd_dw_rate": round(p[2], 2)} for p in circuit_pairs],
    "pearson_r": round(r_iqbal_dw, 4) if r_iqbal_dw is not None else None,
}

# 3h. Integrated district/judge deep dive for the steepest circuit declines
print("\n3h. Integrated district/judge deep dive for the steepest circuit declines")
from circuit_district_deep_dive import run_analysis as run_circuit_district_deep_dive

deep_dive_output = run_circuit_district_deep_dive(write_outputs=True, emit_console=False)
deep_dive_json_path = os.path.join(RESULTS_DIR, "circuit_district_deep_dive_results.json")
deep_dive_md_path = os.path.join(RESULTS_DIR, "circuit_district_deep_dive_analysis.md")
deep_dive_findings = deep_dive_output.get("cross_circuit_findings", {})
print(f"  Saved integrated deep dive JSON to: {deep_dive_json_path}")
print(f"  Saved integrated deep dive memo to: {deep_dive_md_path}")

# ─────────────────────────────────────────────────────────────────────────────
# SAVE RESULTS
# ─────────────────────────────────────────────────────────────────────────────
output = {
    "dataset": {"total_cases": len(cases),
                "disability_screened_in": len(disability),
                "dated_disability": len(dated),
                "periods": {"P1": "2013-2020", "P2": "2021-2022", "P3": "2023-2026"}},
    "analysis_1_iqbal_evolution": results_1,
    "analysis_2_settlement": results_2,
    "analysis_3_circuit": results_3,
    "analysis_3_circuit_deep_dive": {
        "integrated_script": "scripts/circuit_district_deep_dive.py",
        "results_json": deep_dive_json_path,
        "results_memo": deep_dive_md_path,
        "top_5_circuits_by_full_decline": deep_dive_output["top_5_circuits_by_full_decline"],
        "high_impact_full_circuit_shortfall_cutoff": deep_dive_output["method"].get("high_impact_full_circuit_shortfall_cutoff"),
        "high_impact_judges_with_post_2025_appointments": deep_dive_findings.get("high_impact_judges_with_post_2025_appointments", []),
        "unresolved_high_impact_judges": deep_dive_findings.get("unresolved_high_impact_judges", []),
    },
}
out_path = os.path.join(RESULTS_DIR, "extended_doctrinal_analysis.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False, default=str)
print(f"\n\nResults saved to: {out_path}")
print("Script complete.")
