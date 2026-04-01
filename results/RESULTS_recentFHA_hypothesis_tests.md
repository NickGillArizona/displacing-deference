# Hypothesis Test Results — recentFHA Database

**Database:** `RAClassification_DB_openrouter_batch.json`
**Total cases:** 2,366 (1,857 screened as FHA; 509 non-FHA)
**Period:** 2021–2026 (bulk is 2022–2026)
**Date:** 2026-03-27

---

## Test 1: Disability Dominance — STRONGLY CONFIRMED

| Protected Class | n | Share |
|---|---|---|
| **Disability** | **1,229** | **66.2%** |
| Race | 389 | 20.9% |
| Sex | 61 | 3.3% |
| Familial Status | 30 | 1.6% |
| National Origin | 30 | 1.6% |
| Religion | 29 | 1.6% |

**Disability share: 66.2% (95% CI: 64.0%–68.3%)**

Disability isn't just the plurality — it's a two-thirds supermajority of recent federal FHA litigation. This is *higher* than the 54.6% HUD administrative complaint share, which reverses the expected pattern (complaints typically exceed litigation). The article's "dominance" framing is fully supported.

**Impact on article:** The 38.1% figure from the old FHA Pilot DB was wrong. Replace with **66.2%** throughout. This is a much stronger number.

---

## Test 2: Iqbal Citation Disparity — NOT CONFIRMED (reversed)

| | Disability | Race |
|---|---|---|
| Overall Iqbal citation rate | 35.6% (438/1,229) | 50.1% (195/389) |
| MTD Iqbal citation rate | 60.6% (405/668) | 73.6% (173/235) |
| **Ratio** | **0.82x** | **—** |

**Race cases cite Iqbal MORE than disability cases, not less.** The old 3.3x ratio from the 331-case Pilot DB is not replicated in the larger sample. At MTD, race cases cite Iqbal at 73.6% vs. disability at 60.6% — the opposite direction.

This makes doctrinal sense: *Iqbal* is a pleading standard case, and disparate treatment claims (which dominate race litigation at 77.6%) live or die on plausibility pleading. Reasonable accommodation claims (53.6% of disability litigation) are analyzed under a different framework (necessity + reasonableness), where *Iqbal* is less central.

**Impact on article:** The *Iqbal* disparity argument must be dropped or fundamentally reframed. The data does not support the claim that disability plaintiffs face a unique *Iqbal* burden.

---

## Test 3: Iqbal Effect on Outcomes — WEAKLY CONFIRMED

| | Iqbal Cited | No Iqbal |
|---|---|---|
| Overall DW rate | 78.1% (524/671) | 73.4% (592/807) |
| MTD DW rate | 78.4% (486/620) | 81.5% (242/297) |

**Overall:** When Iqbal is cited, defendants win 4.7pp more often (p=0.035). **But at MTD specifically, the effect reverses** — cases without Iqbal have a slightly higher DW rate (81.5% vs. 78.4%).

**Stratified by class:**
- Disability: Iqbal DW 78.7% vs. no-Iqbal 74.5% (+4.1pp)
- Race: Iqbal DW 76.6% vs. no-Iqbal 75.2% (+1.5pp)

The Iqbal penalty is real but modest and not disability-specific. The effect is slightly larger for disability (+4.1pp) than race (+1.5pp), but this hasn't been tested for statistical significance of the *difference in differences*.

**Impact on article:** Can note that Iqbal citations correlate with worse outcomes overall, but cannot claim this is a disability-specific problem.

---

## Test 4: Disability Win Rate Disadvantage — NOT CONFIRMED

| Class | n | PW | MX | DW | PW% | PW+MX% | DW% |
|---|---|---|---|---|---|---|---|
| Disability | 957 | 56 | 171 | 730 | 5.9% | 23.7% | 76.3% |
| Race | 333 | 9 | 71 | 253 | 2.7% | 24.0% | 76.0% |
| Sex | 48 | 11 | 12 | 25 | 22.9% | 47.9% | 52.1% |
| Familial Status | 20 | 3 | 6 | 11 | 15.0% | 45.0% | 55.0% |

**Disability PW+MX rate: 23.7% vs. Race: 24.0% — virtually identical (p=0.91).**

Disability plaintiffs do not lose more than race plaintiffs. Both classes have ~76% DW rates. The real story is that **all FHA plaintiffs lose at very high rates** — and sex/familial status plaintiffs do dramatically better (47.9% and 45.0% PW+MX rates).

Note: Strict PW rates show disability (5.9%) actually *outperforming* race (2.7%), p=0.024. The gap disappears when MIXED is included.

**Impact on article:** Cannot claim disability faces uniquely worse outcomes. Can claim FHA enforcement fails plaintiffs across the board, with sex and familial status as the only classes with reasonable success rates.

---

## Test 5: Claim Type Distribution — STRONGLY CONFIRMED

**Disability primary claim type:**
| Claim Type | n | Share |
|---|---|---|
| Reasonable accommodation denial | 659 | 53.6% |
| Disparate treatment | 222 | 18.1% |
| Retaliation | 81 | 6.6% |

**Race primary claim type:**
| Claim Type | n | Share |
|---|---|---|
| Disparate treatment | 302 | 77.6% |
| Disparate impact | 50 | 12.9% |
| Retaliation | 8 | 2.1% |

Disability litigation runs through § 3604(f)(3)(B) accommodation analysis (53.6% primary, 67.9% appearing anywhere). Race litigation runs through § 3604(a) disparate treatment (77.6% primary, 88.2% appearing anywhere). These are structurally different enforcement regimes operating under the same statute.

**Impact on article:** This is the strongest empirical finding. The recalibration argument doesn't need disability to lose *more* — it needs disability to be *different*. The claim type data proves that disability enforcement operates through different statutory provisions requiring different regulatory infrastructure.

---

## Test 6: Procedural Funnel — PARTIALLY CONFIRMED

**Disability:**
| Stage | n | DW% | PW+MX% |
|---|---|---|---|
| MTD | 584 | 80.1% | 19.9% |
| SJ | 118 | 61.9% | 38.1% |
| Trial | 14 | 57.1% | 42.9% |

**Race:**
| Stage | n | DW% | PW+MX% |
|---|---|---|---|
| MTD | 223 | 76.2% | 23.8% |
| SJ | 48 | 70.8% | 29.2% |
| Trial | 3 | 100.0% | 0.0% |

MTD is where both classes die — 584 of 957 disability decided cases (61%) are at MTD. Disability MTD DW rate is 3.9pp worse than race (80.1% vs. 76.2%), but the structural pattern is similar: most cases never get past MTD.

The interesting finding: disability plaintiffs who survive to SJ do much better (38.1% PW+MX) than race plaintiffs at SJ (29.2%). This suggests disability claims are winnowed early but the survivors are stronger.

**Impact on article:** The "disability cases die at MTD" narrative is true but not distinctive — race cases die there too. The more interesting argument is the SJ divergence.

---

## Test 7: Defendant Type Patterns — CONFIRMED (descriptively)

Key differences:
- Disability has more **housing authority** defendants (12.9% vs. 4.9%) with the worst outcomes (13.2% PW+MX)
- Race has more **private landlord** defendants (29.0% vs. 21.2%)
- Both classes fare best against **HOA/condo** defendants (~36.6% PW+MX) and worst against **housing authorities** and **government**

Disability enforcement disproportionately involves public and quasi-public defendants (housing authorities 12.9% + government 3.4% + municipality 13.4% = 29.7%) compared with race (4.9% + 1.8% + 17.2% = 23.9%).

**Impact on article:** Supports the § 3604(f)(3) enforcement argument — disability cases disproportionately involve institutional defendants where § 3608(d) affirmative obligations are most relevant.

---

## Summary: What the Data Supports

| Claim | Status | Strength |
|---|---|---|
| Disability dominates FHA enforcement | **CONFIRMED** | Very strong (66.2%) |
| Disability faces unique *Iqbal* burden | **NOT CONFIRMED** | Reversed — race cites Iqbal more |
| Disability plaintiffs win less | **NOT CONFIRMED** | Identical to race (23.7% vs 24.0%) |
| Disability uses different legal framework | **CONFIRMED** | Very strong (53.6% RA vs 77.6% DT) |
| Disability cases die at MTD | **PARTIALLY CONFIRMED** | True but not unique to disability |
| Enforcement involves different defendants | **CONFIRMED** | Descriptively clear |

## Revised Empirical Narrative for the Article

The data does **not** support a story about disability plaintiffs being uniquely disadvantaged in outcomes. It supports a different — and arguably stronger — story:

**Disability dominates FHA enforcement (66.2% of litigation) but operates through an entirely different legal framework than race.** While race enforcement runs through disparate treatment analysis under § 3604(a), disability enforcement runs through reasonable accommodation analysis under § 3604(f)(3)(B). Both classes lose at nearly identical rates (~76% DW), but they lose for *different doctrinal reasons* requiring *different regulatory responses*. The AFFH apparatus — built for racial integration metrics — has no infrastructure for the accommodation-based enforcement that constitutes two-thirds of the statute's actual caseload. The recalibration argument is about institutional alignment, not outcome disparity.
