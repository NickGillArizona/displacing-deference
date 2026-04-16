# The FHA Unified Database

### 2,522 federal fair housing opinions. Classified by AI. Built for $135.

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE) [![License: CC BY 4.0](https://img.shields.io/badge/Data-CC_BY_4.0-lightgrey.svg)](LICENSE-DATA)

**Nicholas Gill** | J.D. Candidate 2027 | University of Arizona James E. Rogers College of Law

---

## The short version

Disability generates **55% of all fair housing complaints** in the United States. After *Loper Bright* and HUD's 2025 enforcement withdrawal, aggregate plaintiff win rates dropped from 18% to 11%. The natural conclusion is that courts turned against disability plaintiffs.

**That conclusion is wrong.**

We built a classified database of 1,770 federal disability FHA opinions and decomposed the decline. The drop is **dominantly compositional** — roughly **76% is a composition effect** driven by the surge in pro se (unrepresented) filers from 59% to 77% as the fair housing organizations that screen and develop cases got defunded. Represented plaintiffs held steady at 34.3% in both periods. A residual within-group deterioration is detectable in the strongest-case represented subset (broad win rates fell from 69.0% to 52.3%), consistent with a tightening pleading gate even for represented plaintiffs — but the primary driver is infrastructure collapse, not judicial hostility.

*Represented plaintiffs recovered. The system did not.*

---

## What's in the database

| | Count |
|---|---:|
| Federal FHA opinions screened in (all protected classes) | 2,522 |
| Disability opinions (primary analysis population) | 1,770 |
| With exact decision dates (Jan 2022 -- Mar 2026) | 1,191 |
| With resolved outcomes (win/lose/mixed) | 889 |
| Individual claims extracted (per-claim decomposition) | 6,718 |
| Classified fields per opinion | 28 |

Every opinion is coded for outcome, procedural posture, accommodation type, defendant type, plaintiff type, disability category, *Iqbal*/*Twombly* citation, and more — with full pipeline provenance metadata tracking which model classified each field and how disagreements were resolved.

---

## How it was built

Traditional approach: manually read 2,500 opinions, train coders, run inter-rater reliability. ~600 researcher-hours. Institutional funding. Months of work.

Our approach: **three independent LLMs classify each opinion, and their disagreement is the quality signal.** Same logic as inter-rater reliability, transposed to computational classifiers.

```
CourtListener API (4,027 opinions)
        │
        ▼
  Stage 1: Screening ──────────── Gemini Flash Lite (< $5)
  Binary FHA relevance filter      1,505 discarded → 2,522 kept
        │
        ▼
  Stage 2: Triple Classification
  ┌─────────────┐ ┌──────────────┐ ┌───────────┐
  │ MiniMax M2.7 │ │ DeepSeek V3.2│ │  Kimi K2.5│    $85 total
  └──────┬──────┘ └──────┬───────┘ └─────┬─────┘
         └───────────────┼───────────────┘
                         ▼
  Stage 3: Consensus Resolution
  Unanimous?  → accept (0.6%)
  Majority?   → accept (45.4%)
  Split?      → escalate to Haiku 4.5 (37.5%)
  Critical split? → Sonnet 4.6 re-extracts (16.3%)
                         │
                         ▼
  Stage 4: Per-Claim Extraction ── Haiku 4.5 batch ($18)
  3,193 opinions → 6,718 individual claims
                         │
                         ▼
  Stage 5: Reproducibility Audit ── Opus 4.6 ($4.56)
  50-case stratified sample
  81.5% inter-classifier agreement | κ = 0.561
```

**Why three models?** MiniMax, DeepSeek, and Kimi were chosen for training-corpus independence — different training data, parameter scales, and fine-tuning approaches. When all three agree, the signal is strong. When they disagree, the contested fields escalate to more powerful adjudicators. Every record carries provenance metadata: which tier resolved it, which models agreed, what the adjudicator decided.

**How often do the models agree?**

| Field | Unanimous (3/3) | Majority (2/3) | No Majority |
|-------|:---:|:---:|:---:|
| Court | 96.9% | 2.9% | 0.2% |
| Year | 98.7% | 1.2% | 0.2% |
| Outcome | 69.1% | 28.0% | 2.9% |
| Primary Claim Type | 62.6% | 32.2% | 5.2% |
| Accommodation Type | 34.7% | 45.8% | 19.5% |

Objective fields (court, year) hit near-perfect consensus. Interpretive fields (accommodation type) diverge — exactly where human coders would too. Only 0.6% of cases achieved full unanimous consensus across *all* fields, meaning the multi-model design caught disagreements in 99.4% of records.

**Total cost: $134.90.** One week from first API call to validated database.

---

## What we found

### The composition effect (the headline)

| | P1: Baseline | P2: Transition | P3: Post-Withdrawal |
|---|---|---|---|
| Aggregate strict win rate | 18.0% | 7.8% | 10.7% |
| **Represented** win rate | **34.3%** | 19.0% | **34.3%** |
| Pro se win rate | 7.3% | 1.4% | 4.4% |
| Pro se filing share | 58.9% | 56.6% | **76.7%** |

P1 = pre-*Loper Bright* (Jan 2022 -- June 2024). P2 = transition. P3 = post-HUD withdrawal (Feb 2025 -- present).

A [Kitagawa-Oaxaca-Blinder decomposition](appendices/Appendix_A5_Robustness_Checks.md) confirms: **76% composition effect, 24% rate effect.** The rate-effect coefficient is p = 0.991 — statistically indistinguishable from zero. A residual within-group deterioration is detectable in the strongest-case represented subset (broad win rates fell from 69.0% to 52.3%), consistent with a tightening pleading gate even for represented plaintiffs. Five robustness checks (reclassification sensitivity, boundary shifts, category exclusion, bootstrap CIs, Oaxaca-Blinder) all converge.

### The pipeline is broken

- **17,600** disability complaints filed in 2024 (+8.7% since 2018)
- **1.5%** result in a formal charge
- **53:1** ratio of complaints to federal cases
- **78** FHIP grants across 66 organizations in 33 states (~87% of U.S. population) terminated (Feb 2025); FHEO charges fell from ~25/year to 4 between January and July 2025; at least 115 cases closed or halted
- Fair housing orgs dropped from 86 → 82 in one year

### The decline concentrates at the gate

Represented plaintiffs survived motions to dismiss at stable rates across all three periods — courts aren't dismissing good cases more often:

| | P1 | P2 | P3 |
|---|---|---|---|
| Represented MTD survival | 82.0% | 76.1% | 82.8% |
| Aggregate MTD survival | 53.6% | — | 38.6% |
| Merits broad win rate | 39.8% | — | 42.1% |

The aggregate MTD survival fell because more pro se cases are hitting the gate, not because the gate got narrower for represented plaintiffs. Cases that reach the merits actually win at *slightly higher* rates in P3 than P1.

### Institutional plaintiffs outperform — and they're disappearing

| Plaintiff type | N | Broad win |
|---|---|---|
| Government | 10 | 90.0% |
| Fair housing organizations | 31 | 67.7% |
| Group home operators | 78 | 42.3% |
| Individual tenants | 740 | 20.0% |

Chi-squared = 76.7 (p < 0.0001). Institutional status predicts reaching the merits (OR = 1.41, p = 0.037) but not winning once there (OR = 1.27, p = 0.21) — institutions get cases past the pleading stage; case quality takes over from there. The mechanism is representation: 72% of individual tenants are pro se.

Institutional plaintiffs shrank from 16.9% of filings (P1) to 12.1% (P3). The screening infrastructure is contracting.

### Specific claims win; vague claims don't

| Claim type | Broad win rate |
|---|---|
| Specific-duty (accessible design, accommodations) | 39.3% |
| Open-textured (general discrimination) | 1.0% |

OR = 12.33 (p < 10^-17). Statutory precision is the strongest predictor of outcome — stronger than representation, period, or defendant type. 88.5% of open-textured cases are pro se.

Within specific-duty claims, the hierarchy tracks verifiability:

| Accommodation type | Strict win | Broad win | N |
|---|---|---|---|
| Design & construction | 46.7% | 70.0% | 30 |
| Assistance animal | 35.3% | 56.9% | 102 |
| Parking | 34.0% | 55.3% | 47 |
| Policy exception | 14.2% | 25.9% | 197 |
| Eviction defense | 14.5% | 18.2% | 55 |

Design-and-construction claims win most often — but constitute only **2.2%** of litigated cases despite widespread documented noncompliance. The Housing Equality Center of Pennsylvania found 47% noncompliance across 38 covered communities tested regionally (2005–2014); the Equal Rights Center documented a 69.6% violation rate in its 2019 D.C. testing. The 2003 HUD/Steven Winter national study found composite conformance scores of 73–95%, indicating substantial but uneven compliance. A massive gap persists between known violations and litigated cases.

### Circuit-level variation

MTD survival rates vary wildly across circuits — from 14.5% (2d Cir.) to 45.8% (1st Cir.):

| Circuit | P1 Broad % | P2+P3 Broad % | Delta |
|---|---|---|---|
| 11th Circuit | 38.1% (n=21) | 0.0% (n=12) | -38.1 pp |
| 5th Circuit | 45.0% (n=20) | 19.0% (n=21) | -26.0 pp |
| 3rd Circuit | 20.0% (n=35) | 20.6% (n=34) | +0.6 pp |
| 10th Circuit | 27.3% (n=11) | 26.3% (n=19) | -1.0 pp |

The Eleventh Circuit went from 38.1% to literally zero. The Third and Tenth Circuits barely moved. Geographic heterogeneity this large suggests circuit-level factors beyond *Loper Bright*.

### HUD can't see the problem

- **$67.7 billion** in cumulative CDBG grants → none of the housing rehabilitation activity codes (14A–14L) records whether rehabilitation added accessibility features
- **34,000+** properties inspected through NSPIRE → **no** accessibility output
- **1.8 million** disabled households in subsidized housing → **no** accessible-unit data
- NSPIRE failure rates jumped from 4.4% → 16.8% after updated standards — showing that inspection changes actually work
- Among federal Section 504 agencies, HUD is an outlier: ED's CRDC, DOT's NTD, and DOL's Form CC-305 all produce recurring disability-compliance data that HUD has never built

### The disability penalty

Disabled renters face a cost-burden penalty **larger than the Black-White racial gap**:

| Race | Disability Penalty (pp) | SE |
|---|---|---|
| White | 16.9 | 0.25 |
| Black | 10.1 | 0.43 |
| AIAN | 7.3 | 1.40 |

For comparison: the Black-White cost-burden gap among non-disabled renters is 8.4 pp.

An estimated **823,000** disabled renters of color live in communities that HUD's prior AFFH model never directly reached.

---

## Validation — what we know and what we don't

**What the audit shows:** An independent classifier (Opus 4.6) re-classified 50 opinions from scratch. Inter-classifier agreement: 81.5%. Cohen's kappa: 0.561 (moderate-to-substantial). 73% of disagreements are boundary disputes (e.g., dismissal without prejudice: "defendant win" or "procedural"?).

**What the audit does not show:** Accuracy against human-coded ground truth. No comparable human-coded FHA dataset exists to benchmark against. The claim is reproducibility — independent classifiers reaching substantially similar results — not perfection.

**Measurement error direction:** The disagreement pattern skews toward "procedural" — meaning classification error attenuates findings toward the null. Significant results are conservative estimates.

**Other limitations:** Federal written opinions only (no settlements, no administrative resolutions). Small-N subgroups flagged throughout. No causal claims about *Loper Bright* specifically — the post-2024 period is a changed legal-administrative environment encompassing multiple concurrent shocks.

---

## Repo structure

```
.
├── data/                     # FHA Unified Database (JSON)
├── results/                  # Computed statistics, reports, CSVs
├── scripts/                  # 31 Python analysis scripts
│   ├── run_all.py            # Master replication script
│   ├── recompute_stats_unified.py
│   ├── robustness_checks.py
│   ├── census_pums_replication.py
│   └── ...
├── appendices/               # Extended analyses (A-3 through K)
├── pipeline/                 # Classification pipeline docs
│   ├── consensus_resolution.md
│   ├── model_configuration.md
│   └── per_claim_extraction_schema.json
├── prompts/                  # Full LLM classification prompts
├── queries/                  # CourtListener + Census API queries
├── CITATION.cff
├── CONTRIBUTING.md
├── CREDITS.md
└── requirements.txt
```

---

## Appendices

| Appendix | What's in it |
|----------|-------------|
| [A-3](appendices/Appendix_A3_Extended_Empirical_Analysis.md) | Extended analysis: regression models, pro se three-population framework, interactive process reversal, Hispanic/Latino convergence, invisible population, CHAS feasibility |
| [A-4](appendices/Appendix_A4_Reproducibility_Audit.md) | Full reproducibility audit: per-field agreement, tier-disaggregated results, error anatomy, attenuation bias defense |
| [A-5](appendices/Appendix_A5_Robustness_Checks.md) | Five robustness checks: reclassification, boundary sensitivity, category exclusion, bootstrap CIs, Oaxaca-Blinder |
| [B](appendices/Appendix_B_Results_Tables.md) | Core results tables: three-period, year-by-year, procedural disposition, chi-squared tests |
| [C](appendices/Appendix_C_Iqbal_Citation_Analysis.md) | *Iqbal*/*Twombly* citation analysis with cross-class comparison |
| [D](appendices/Appendix_D_Protected_Class_Distribution.md) | Protected-class distribution across the database |
| [E](appendices/Appendix_E_Accommodation_Defendant_Analysis.md) | Win rates by accommodation type (13 categories) and defendant type (8 categories), all with three-period breakdowns |
| [F](appendices/Appendix_F_Galanter_Plaintiff_Type.md) | Galanter repeat-player analysis with pro se cross-tabulation |
| [G](appendices/Appendix_G_Circuit_Level_Analysis.md) | Circuit-level win rates, MTD survival, and interactive process discussion rates |
| [H](appendices/Appendix_H_Supplementary_Data.md) | Modification desert data, design-and-construction noncompliance ratio, enforcement infrastructure, pro se x defendant cross-tab |
| [J](appendices/Appendix_J_Safe_Harbor_Detail.md) | Safe harbor operational detail (population thresholds, cost analysis, FCA enforcement) |
| [K](appendices/Appendix_K_Classification_Prompts.md) | Full text of all LLM classification prompts |

---

## Mapping: article sections to scripts

If you're trying to replicate a specific finding from the empirical article:

| Finding / Section | Run this | Check this output |
|---|---|---|
| Database composition | `recompute_stats_unified.py` | `results/unified_stats_report.md` Sec. A |
| Three-period win rates | `recompute_stats_unified.py` | `results/unified_stats_report.md` Sec. B |
| Composition effect / Oaxaca-Blinder | `robustness_checks.py` | `results/robustness_checks_output.txt` |
| Procedural-stage analysis | `h7_analysis.py` | Appendix A-3 Sec. B |
| Institutional plaintiff hierarchy | `h5_analysis.py` | Appendix F |
| Claim specificity (OR = 12.33) | `h1_h2_analysis.py` | — |
| Physical evidence effect | `h6_analysis.py` | — |
| Circuit-level variation | `recompute_all_appendices.py` | Appendix G |
| Disability cost-burden penalty | `census_pums_replication.py` | `results/pums_results.csv` |
| Sensitivity (DIS=1 vs. DPHY/DOUT) | `pums_dis1_sensitivity.py` | `results/pums_sensitivity_results.json` |
| Housing stock analysis | `pums_housing_stock_analysis.py` | `results/housing_stock_results.json` |
| CDBG measurement gap | `cdbg_analysis.py` | — |
| POSH disability rates | `posh_analysis.py` | — |
| NSPIRE inspection analysis | `reac_analysis.py` | — |

---

## Data sources

| Source | What we use it for | Link |
|---|---|---|
| CourtListener REST API v4 | Federal court opinion text | [courtlistener.com/api](https://www.courtlistener.com/api/rest/v4/) |
| ACS 2020-2024 5-Year PUMS | Census microdata for disability housing analysis | [Census API](https://api.census.gov/data/2024/acs/acs5/pums) |
| OpenRouter | Multi-model LLM access for classification | [openrouter.ai](https://openrouter.ai/) |

---

## Run it yourself

```bash
pip install -r requirements.txt

# Everything
python scripts/run_all.py

# Litigation stats only
python scripts/recompute_stats_unified.py
python scripts/recompute_all_appendices.py
python scripts/robustness_checks.py

# Census PUMS only
python scripts/census_pums_replication.py
python scripts/pums_dis1_sensitivity.py
python scripts/pums_housing_stock_analysis.py
```

The database JSON files are included in `data/`. PUMS scripts hit the Census Bureau's public API — no API key needed.

---

## Publications

This repository supports two articles:

- **Empirical article:** "Beyond Aggregate Win Rates: Composition Effects and Measurement Failure in Disability Fair Housing Litigation" — the dataset, methodology, and results as a standalone contribution
- **Doctrinal note:** "The Enacted Floor: Reinforcement, Not Replication in Disability-Centered AFFH" — the legal argument, using the empirical findings as its evidentiary foundation

---

## How to cite

```bibtex
@article{gill_composition_2026,
  author  = {Gill, Nicholas},
  title   = {Beyond Aggregate Win Rates: Composition Effects and
             Measurement Failure in Disability Fair Housing Litigation},
  year    = {2026},
  note    = {Manuscript}
}

@misc{gill_fha_database_2026,
  author  = {Gill, Nicholas},
  title   = {FHA Unified Database: Replication Package},
  year    = {2026},
  url     = {https://github.com/NickGillArizona/displacing-deference}
}
```

---

## License

- **Code**: [MIT](LICENSE)
- **Data and documentation**: [CC BY 4.0](LICENSE-DATA)
- Court opinions are public domain. See [CREDITS.md](CREDITS.md) for source attributions.

---

## AI disclosure

LLMs were used for corpus assembly, classification, data processing, and reproducibility checks. The pipeline is part of the methodology — it's what we're studying, not something we're hiding. All analytical, doctrinal, and editorial decisions are the author's. Full classification prompts and pipeline documentation are in this repo.

**Contact:** [nickgill@arizona.edu](mailto:nickgill@arizona.edu)
