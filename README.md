# Displacing Deference: Data and Doctrine for a Disability-Centered AFFH

**Nick Gill** | University of Arizona James E. Rogers College of Law

This repository contains the replication package, classified dataset documentation, and supplementary appendices for a law review note arguing that the post-*Loper Bright* constitutional landscape counsels recalibrating AFFH through the disability-specific mandates of 42 U.S.C. § 3604(f)(3). The empirical foundation is a structured dataset of 3,193 federal FHA cases (6,718 individual claims) constructed through a novel multi-model LLM consensus pipeline — what this Note terms **Agile Empirical Legal Studies (Agile ELS)**.

---

## Key Findings

**The convergence thesis.** Disability is the dominant axis of housing cost burden across racial groups. Using ACS 2020-2024 5-Year PUMS microdata — producing the first published race-by-disability cost-burden estimates with confidence intervals — the disability penalty (10-17 percentage points, depending on race) exceeds the entire racial cost-burden gap among non-disabled renters (8.4 points Black-White). Among disabled renters, the Black-White gap compresses to 1.6 percentage points (56.3% vs. 54.7%). Enforcing § 3604(f)(3) does not trade off against racial equity. It reaches the same populations through a larger axis of disadvantage.

**The enforcement desert.** At minimum 823,000 disabled renters of color reside in non-entitlement communities that the integration model structurally excluded from CDBG enforcement. For this population, disability-centered enforcement is not a policy preference — it is the only federal pathway that exists.

**The litigation decline.** After *Loper Bright*, disability plaintiff win rates in the § 3604 Database fell from 21.5% to 13.7% (p=0.0004). The RA Database corroborates the decline across all protected classes: 16.7% to 9.0%. Multivariate logistic regression confirms 40-51% lower odds of plaintiff victory after controlling for procedural posture, defendant type, accommodation type, and plaintiff type.

**The capability gap.** Institutional plaintiffs — fair housing organizations, government agencies, group home operators — succeed at four to eight times the rate of individual tenants, even after controlling for claim type and procedural posture. Pro se plaintiffs constitute 54.3% of the database and win 4.9% of the time, versus 27.0% for represented plaintiffs.

**The procedural gatekeeping problem.** Courts cite *Iqbal* in disability cases at 3.3x the rate observed in race cases. When invoked, defendant success at motion-to-dismiss rises from 43.1% to 66.7%.

**The design-and-construction gap.** 47% estimated noncompliance rate in pre-1990 multifamily housing, against 0.8% of fair housing complaints — a 56:1 ratio.

---

## The Dataset

This repository provides what HUD does not: a structured empirical dataset of approximately 2,566 unique federal FHA cases across all protected classes, drawn from three databases and deduplicated into a Unified Dataset of 3,193 cases with 6,718 individual claims for per-claim analysis.

| Database | Scope | Cases (screened) |
|----------|-------|:---:|
| RA Database | All FHA protected classes, 2021-2026 | 1,857 |
| 2015 FHA Database | § 3604(f) disability cases | 1,496 |
| FHA Pilot Database | Initial validation cohort | 331 |
| **Unified Dataset** | **Deduplicated, per-claim extraction** | **3,193 (6,718 claims)** |

The repository also includes the first systematic use of ACS PUMS microdata to quantify disability-specific housing cost burden by race. HUD has never cross-tabulated disability status with race in its cost-burden reporting; the Census Bureau publishes disability prevalence and housing cost burden in separate tables that cannot be linked at the individual level without microdata access. This analysis queries the 2020-2024 ACS 5-Year PUMS at the householder level using successive-differences replication with 80 replicate weights for standard errors — the Census Bureau's recommended variance estimation method. Full replication queries, variable definitions, and sensitivity analyses appear in [Appendix A-2](appendices/Appendix_A2_PUMS_Replication.md).

---

## Methodology: Agile ELS

Traditional empirical legal studies at this scale — manually reading and coding 3,193 court opinions into structured data — would require roughly 800 hours of researcher time, substantial institutional funding, and extensive inter-rater reliability testing. I constructed this dataset in one week for approximately $160.

The approach, which I am calling **Agile Empirical Legal Studies (Agile ELS)**, rests on a straightforward insight: rather than trusting a single LLM to classify thousands of cases — fast but unreliable — I ran each case through three independent models and treated their disagreement as a quality signal. When all three agreed, I accepted the answer. When they disagreed, I escalated to a stronger model that could see all three outputs and adjudicate. This transposes the logic of inter-rater reliability — the same principle that governs human coding in empirical legal research — from human coders to computational classifiers.

To the best of my knowledge, no published legal study has employed multi-model LLM consensus with tiered adjudication for structured legal data extraction at this scale.

### Three principles

**1. Fail-fast hypothesis testing.** Rather than committing years of labor to a coding scheme before discovering whether a hypothesis survives contact with data, Agile ELS supports rapid exploratory cycles: construct a prototype dataset, test the claim, pivot or deepen — in the same week. The entire empirical foundation of this Note — 3,193 classified cases, 6,718 individual claims, eight hypothesis tests, and seven regression models — was constructed and analyzed in a single research sprint.

**2. Tiered consensus extraction.** Three architecturally independent LLMs (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) classify each case separately. They were selected for independence: different training corpora (Chinese and Western sources), different parameter scales, different fine-tuning approaches — ensuring that consensus reflects textual signal rather than shared model bias. Agreement determines confidence; disagreement routes contested cases to progressively stronger adjudicators (Haiku 4.5, then Sonnet 4.6). Every record carries full provenance metadata: which tier resolved it, which models agreed, what the adjudicator decided and why.

**3. Democratized access.** Total pipeline cost for 3,193 cases: ~$160. Forty-six percent of cases resolved through consensus or majority vote alone, without requiring an additional API call. The difficult cases escalated; the straightforward ones were effectively free.

> **Project summary.** Dataset: 3,193 cases, 6,718 claims. Classification: 3 independent LLMs + tiered adjudication. Cost: ~$160. Timeline: one week. Validation: Cohen's κ 0.56-0.74 across substantive fields.

### Pipeline stages

The pipeline processes court opinions through five stages:

1. **FHA Screening** — Gemini 3.1 Flash Lite binary classifier filters non-FHA opinions
2. **Triple-Model Classification** — MiniMax M2.7 + DeepSeek V3.2 + Kimi K2.5 independently produce 28-field structured JSON per case
3. **Tiered Consensus Resolution** — Unanimous → majority vote → Haiku 4.5 adjudication → Sonnet 4.6 adjudication (RA Database). The 2015 FHA Database resolves three-way splits via MiniMax M2.7 tiebreaker; see Appendix A, Section A.3
4. **Per-Claim Extraction** — Haiku 4.5 decomposes multi-claim cases into individual legal claims
5. **Reproducibility Audit** — Opus 4.6 re-classifies a stratified sample for inter-rater reliability

See [`pipeline/`](pipeline/) for full documentation including model costs, agreement rates, and resolution tier distributions.

### Resolution tier distribution (n=1,857 RA cases)

| Tier | Resolution Method | Records | % |
|:---:|---|:---:|:---:|
| 0 | Unanimous consensus | 12 | 0.6% |
| 1-2 | Majority vote (no API call) | 843 | 45.4% |
| 3 | Haiku 4.5 adjudication | 697 | 37.5% |
| 4 | Sonnet 4.6 adjudication | 302 | 16.3% |

Nearly half of all cases resolved at the majority-vote tier. The remaining cases escalated to progressively stronger adjudicators — concentrating cost on the genuinely difficult classifications.

---

## Validation and Limitations

The multi-model design performed well on objective fields — court identification (96.9% unanimous), year (98.7%) — and showed meaningful divergence on interpretive fields where human coders would also disagree:

| Field | Unanimous (3/3) | Majority (2/3) | No Majority |
|-------|:---:|:---:|:---:|
| Court | 96.9% | 2.9% | 0.2% |
| Year | 98.7% | 1.2% | 0.2% |
| Outcome | 69.1% | 28.0% | 2.9% |
| Primary Claim Type | 62.6% | 32.2% | 5.2% |
| Accommodation Type | 34.7% | 45.8% | 19.5% |
| Disability Category | 47.9% | 47.4% | 4.7% |
| Housing Type | 70.9% | 26.8% | 2.3% |

Only 0.6% of cases achieved full unanimous consensus across all fields — meaning the multi-model design caught disagreements requiring resolution in 99.4% of records.

**Reproducibility audit.** Claude Opus 4.6 independently re-classified a stratified random sample of 50 cases. Aggregate match rate across 12 vocabulary-aligned fields: **81.5%**. Cohen's Kappa ranged from Moderate to Substantial:

| Field | Match Rate | Cohen's Kappa |
|-------|:---:|:---:|
| Plaintiff Type | 90.0% | 0.668 (Substantial) |
| Defendant Type | 78.0% | 0.740 (Substantial) |
| Outcome | 70.0% | 0.561 (Moderate) |
| Primary Claim Type | 62.0% | 0.511 (Moderate) |

The outcome kappa (κ=0.561) warrants context. Of 15 disagreements, 11 (73%) involved the procedural/substantive boundary — whether a dismissal without prejudice constitutes a "Defendant Win" or a "Procedural" disposition, whether a partial settlement is "Mixed" or a "Plaintiff Win." These are genuine boundary disputes: in complex housing litigation, the line between a mixed-outcome settlement and a procedural dismissal is notoriously porous. The audit detects this irreducible legal ambiguity rather than measuring classifier error. In manual empirical legal studies, boundary disputes between adjacent procedural categories routinely produce moderate kappa scores even among trained human coders applying identical protocols. Because the disagreement pattern is directional — pipeline classifications skewing toward "procedural" relative to the auditor — any resulting measurement error attenuates regression coefficients toward the null, making the statistically significant post-2024 findings conservative estimates.

**What this audit does and does not show.** The reproducibility audit measures inter-classifier agreement, not accuracy against human-coded ground truth. No human-coded FHA litigation dataset of comparable scope exists against which to benchmark; this dataset is, to the author's knowledge, the first comprehensive classified FHA litigation corpus. The kappa scores are consistent with inter-rater reliability benchmarks in empirical legal research — but the claim is that independent classifiers operating under identical protocols reach substantially similar results, not that the pipeline achieves perfect accuracy.

**Additional limitations.** Small-N subgroup analyses (n < 30) are flagged as suggestive throughout the article. The dataset captures federal written opinions only, not the universe of FHA disputes, settlements, or administrative resolutions; the coding task is one of structured extraction from judicial opinions into a pre-specified vocabulary, not autonomous legal judgment. Causal claims about *Loper Bright*'s independent judicial effect are expressly disclaimed; the observed decline is consistent with, but not proven to result from, the decision alone — this Note treats the post-2024 period as a changed legal-administrative environment encompassing guidance withdrawal, FHIP defunding, and zero reasonable-cause charges alongside the elimination of *Chevron* deference.

See [`pipeline/model_configuration.md`](pipeline/model_configuration.md) for full agreement rates, cost breakdowns, and audit methodology. The complete classification protocol, sampling methodology, and tier-disaggregated results appear in [Appendix A-4](appendices/Appendix_A4_Reproducibility_Audit.md).

---

## Broader Significance

The substantive findings of this Note bear on fair housing policy. The methodology bears on legal scholarship more broadly. If a comprehensive classified litigation dataset can be built for $160 in a week, the resource barriers that have historically confined large-N empirical legal research to well-funded institutions are not what they were.

Any legal domain where structured extraction from judicial opinions is the bottleneck — antitrust enforcement patterns, immigration adjudication, employment discrimination outcomes, habeas corpus petitions — can adopt the same architecture. The pipeline is not domain-specific; the classification prompts are. The primary constraint in this project was financial: I used cost-effective models for initial classification and reserved frontier models for adjudication. With standard institutional funding, researchers could deploy frontier models across all tiers and replace static voting with active multi-agent debate strategies — where LLMs evaluate each other's reasoning rather than merely casting independent votes.

The Agile ELS pipeline — the classification, consensus resolution, and per-claim extraction stages — is documented in [`pipeline/`](pipeline/) and the companion repository [MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work). A researcher with access to the CourtListener API and an OpenRouter account can replicate the full pipeline for a comparable corpus at comparable cost.

---

## Data Sources

| Source | Access |
|--------|--------|
| CourtListener REST API v4 | https://www.courtlistener.com/api/rest/v4/ |
| ACS 2020-2024 5-Year PUMS | https://api.census.gov/data/2024/acs/acs5/pums |
| OpenRouter API | https://openrouter.ai/ |
| Anthropic Message Batches API | https://docs.anthropic.com/ |

The Java and Python source code for the download pipeline, classification clients, and evaluation framework is maintained in the companion repository: **[MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work)**

The unified dataset (N=3,193 cases, 6,718 claims) and full audit trail are available upon request.

---

## Replication Guide

### Prerequisites

```bash
pip install pandas numpy scipy httpx requests anthropic openpyxl python-dotenv statsmodels
```

The PUMS scripts that query the Census API require a Census API key set in a `.env` file. The litigation analysis scripts require the case database JSON files (available upon request).

### Pipeline 1: Litigation Database Analysis

These scripts analyze the classified FHA case databases. They expect JSON database files in their working directory (paths are hardcoded to the author's local environment; update paths before running).

```bash
# Primary § 3604(f) disability litigation statistics
# Produces: pre/post Loper Bright win rates, MTD survival, pro se gaps,
# interactive process effect, defendant-type disparities
python scripts/disability_only_stats.py

# Reconciled statistics across all three databases
# Produces: unified pro se rates (4.9% vs 27.0%), defendant-type win rates
python scripts/final_numbers.py

# Cross-tabulation: accommodation type × defendant type
python scripts/crosstab_3604.py

# Deep-dive 3604 analysis (1,256 lines)
python scripts/combined_case_analysis.py

# Unified § 3604 database analysis
python scripts/analyze_3604_unified.py

# Multivariate logistic regression (7 models across 2 databases)
python scripts/regression_analysis.py

# Verification of computed vs. expected values
python scripts/phase5_verify.py

# Iqbal pleading barrier quantification (331 FHA cases)
python scripts/fha_iqbal_analysis.py

# Comprehensive FHA case statistical analysis
python scripts/fha_case_deep_dive.py

# Positional bias analysis in LLM classification
python scripts/positional_bias_v2.py

# Recompute note statistics from Haiku per-claim extraction
python scripts/phase2_recompute.py

# Final stats extraction using v4 unified database
python scripts/extract_final.py
```

### Pipeline 2: Census PUMS Housing Analysis

These scripts query ACS PUMS microdata. Some pull directly from the Census API; others read pre-downloaded CSV files (`pums_1year_2023_renters.csv`, `pums_5year_2023_renters.csv` — not included due to size).

```bash
# Primary: cost burden by race × disability with standard errors
# Produces: disability penalty (16.9pp White, 10.1pp Black),
# racial gap compression, results → pums_se_results.json
python scripts/pums_costburden_analysis.py

# Standard errors via successive-differences replication (80 weights)
# Produces: pums_se_results.json
python scripts/pums_cb_se.py

# Replication weight methodology
python scripts/pums_replicate_weights.py

# Pre-1990 vs. post-1990 housing stock accessibility gaps
# Produces: housing_stock_results.json
python scripts/pums_housing_stock_analysis.py

# ACS 5-Year AIAN-focused analysis
python scripts/pums_5year_aian_analysis.py

# CDBG non-entitlement community analysis
python scripts/pums_cdbg_analysis.py

# Disability definition sensitivity analysis
# Produces: pums_sensitivity_results.json
python scripts/pums_dis1_sensitivity.py
```

### Key Output Files

| File | Contents |
|------|----------|
| `results/RESULTS_3604_database_analysis.md` | § 3604 case analysis: pre/post *Loper Bright*, win rates by defendant/accommodation type |
| `results/RESULTS_recentFHA_hypothesis_tests.md` | 8 hypothesis tests on disability litigation patterns |
| `results/pums_results.csv` | Cost burden rates by race × disability status with SE and 90% MOE |
| `results/pums_se_results.json` | Detailed standard error calculations, disability penalty, GRPIP distributions |
| `results/housing_stock_results.json` | Building type/era distribution, pre-1990 accessibility gaps |
| `results/pums_sensitivity_results.json` | Disability-definition sensitivity analysis (DPHY-only vs. DPHY∪DOUT) |
| `results/regression_results_RA9.txt` | Logistic regression output (7 model specifications) |

---

## Appendices

The following supplementary appendices are referenced throughout the Note's footnotes. Each appendix is available as a standalone document in the [`appendices/`](appendices/) directory.

| Appendix | Title | Description |
|----------|-------|-------------|
| [A](appendices/Appendix_A_Case_Dataset_Methodology.md) | FHA Case Dataset — Construction Methodology | Full dataset construction methodology, source accounting, deduplication, classification protocol, and known limitations |
| [A-2](appendices/Appendix_A2_PUMS_Replication.md) | PUMS Replication Methodology | ACS 2020-2024 5-Year PUMS variable definitions, replication queries, standard errors via successive-differences replication, and sensitivity analysis |
| [A-3](appendices/Appendix_A3_Extended_Empirical_Analysis.md) | Extended Empirical Analysis | Multivariate regression specifications, pro se plaintiff analysis, interactive process findings, Hispanic/Latino PUMS analysis, housing stock data, and subsidy program analysis |
| [A-4](appendices/Appendix_A4_Reproducibility_Audit.md) | Classification Reproducibility Audit | 50-case stratified-random reproducibility audit: sampling protocol, field-level match rates, Cohen's kappa values, tier-disaggregated results, and robustness assessment |
| [B](appendices/Appendix_B_Results_Tables.md) | Post-*Loper Bright* Analysis | Year-by-year plaintiff win rates (Table B.3), pre/post comparison tables, and chi-squared results |
| [C](appendices/Appendix_C_Iqbal_Citation_Analysis.md) | *Iqbal* Citation Analysis | *Iqbal* citation rates, temporal patterns, and accommodation-type MTD survival rates |
| [D](appendices/Appendix_D_Protected_Class_Distribution.md) | Protected-Class Distribution | Distribution of protected classes across the litigation dataset |
| [E](appendices/Appendix_E_Accommodation_Defendant_Analysis.md) | Accommodation & Defendant-Type Analysis | Win rates by accommodation type, legal theory, defendant type, and disability category |
| [F](appendices/Appendix_F_Galanter_Plaintiff_Type.md) | Galanter Plaintiff-Type Analysis | Repeat-player hypothesis testing, individual vs. organizational plaintiff outcomes, and the "double gatekeeping" framework |
| [G](appendices/Appendix_G_Circuit_Level_Analysis.md) | Circuit-Level Analysis | Circuit-by-circuit win rates, MTD survival rates, pre/post *Loper Bright* variation, and interactive process discussion rates |
| [H](appendices/Appendix_H_Supplementary_Data.md) | Supplementary Data | Modification desert data, design-and-construction noncompliance ratios, PUMS disability housing summary, enforcement infrastructure data, and procedural posture win rates |
| [I](appendices/Appendix_I_AFFH_Case_Classification.md) | AFFH Case Classification | LLM-assisted classification methodology and results for 71 CourtListener AFFH decisions |
| [J](appendices/Appendix_J_Safe_Harbor_Detail.md) | Safe Harbor Operational Detail | Worked examples, rural edge cases, Availability Audit mechanics, and multi-jurisdiction population threshold survey |
| [K](appendices/Appendix_K_Classification_Prompts.md) | Classification Prompts | Full text of FHA relevance screening and case classification prompts |

---

## Repository Structure

```
prompts/                              # LLM classification instruments
  fha_screening_prompt.txt            # Stage 1: Gemini binary FHA screening
  case_classification_prompt.txt      # Stage 2: 28-field structured extraction

queries/                              # API query specifications
  census_pums_queries.md              # ACS 2020-2024 5-Year PUMS queries
  courtlistener_api.md                # CourtListener REST API v4 download specs

scripts/                              # Executable replication scripts
  census_pums_replication.py          # Census PUMS cost-burden replication (Python 3, no deps)
  pums_analysis.py                    # Core PUMS national-level disability prevalence & cost burden
  pums_costburden_analysis.py         # Cost burden by race × disability with SE (primary PUMS script)
  pums_cb_se.py                       # Cost burden with replicate-weight standard errors
  pums_replicate_weights.py           # Successive-differences replication methodology (80 weights)
  pums_housing_stock_analysis.py      # Pre-1990 building stock gap analysis
  pums_housing_stock_fast.py          # Optimized housing stock analysis (vectorized NumPy)
  pums_cdbg_analysis.py              # CDBG non-entitlement community analysis
  pums_5year_aian_analysis.py         # ACS 5-Year AIAN-focused disability & cost burden
  pums_dis1_sensitivity.py           # Disability-definition sensitivity analysis
  disability_only_stats.py            # § 3604(f) litigation statistics (primary case analysis)
  combined_case_analysis.py           # Deep-dive 3604 accommodation & defendant-type analysis
  crosstab_3604.py                    # Cross-tabulation: accommodation type × defendant type
  extract_stats.py                    # Pro se statistics & capability gap extraction
  regression_analysis.py              # Multivariate logistic regression (7 models, 2 databases)
  regression_analysis_full.py         # Full 4-model regression with interaction terms
  analyze_3604_unified.py            # Section 3604 database analysis (pre/post Loper Bright)
  final_numbers.py                   # Authoritative statistics generator for the Note
  extract_final.py                   # Final stats extraction using v4 unified database
  phase5_verify.py                   # Verification: expected vs. computed values
  phase2_recompute.py                # Recompute note statistics from Haiku extraction
  fha_iqbal_analysis.py              # Iqbal pleading barrier analysis (331 cases)
  fha_case_deep_dive.py              # Comprehensive FHA case statistical analysis
  ra_v3_analysis.py                  # RA v3 database analysis
  positional_bias.py                 # Positional bias in claim classification
  positional_bias_full.py            # Extended positional bias analysis
  positional_bias_v2.py              # Refined positional bias methodology
  extract_stats2.py                  # Pro se count reconciliation across databases
  pums_export_csv.py                 # Export Census PUMS microdata to CSV

results/                              # Output data and summary tables
  RESULTS_3604_database_analysis.md   # § 3604 database analysis results
  RESULTS_recentFHA_hypothesis_tests.md # Hypothesis test results (8 tests)
  pums_results.csv                    # Cost burden rates by race × disability with SE
  pums_se_results.json                # Detailed standard error calculations
  pums_sensitivity_results.json       # Disability-definition sensitivity analysis
  housing_stock_results.json          # Housing stock accessibility analysis output
  regression_results_RA9.txt          # Regression model output

pipeline/                             # Classification pipeline documentation
  model_configuration.md              # Model specs, costs, and agreement rates
  consensus_resolution.md             # Tiered consensus algorithm
  per_claim_extraction_schema.json    # Haiku 4.5 per-claim schema
  field_normalization.md              # Free-text normalization rules

appendices/                            # Supplementary appendices (A through K)

Validation_Methodology_Section.md     # Validation methodology documentation
empirical_claims_verification_report.md # Empirical claims verification report
```

## License

This replication package is provided for academic use. The underlying court opinions are public domain.
