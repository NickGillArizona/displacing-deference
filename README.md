# Displacing Deference: Data and Doctrine for a Disability-Centered AFFH

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://python.org)
[![Dataset: 2,522 cases](https://img.shields.io/badge/Dataset-2%2C522%20FHA%20cases-orange.svg)](#the-dataset)
[![Pipeline Cost: ~$200](https://img.shields.io/badge/Pipeline%20Cost-~%24200-purple.svg)](#methodology-agile-els)

**Nicholas Gill** | J.D. Candidate, 2027 | University of Arizona James E. Rogers College of Law | nickgill@arizona.edu

Replication package for a law review note arguing that the post-*Loper Bright* constitutional landscape counsels rebuilding AFFH around the disability-specific mandates of 42 U.S.C. § 3604(f)(3). The empirical foundation is the **FHA Unified Database** — 2,522 federal FHA cases (1,720 disability) classified through a novel multi-model LLM consensus pipeline this Note terms **Agile Empirical Legal Studies (Agile ELS)**.

---

## Pipeline Architecture

```
                          ┌─────────────────────┐
                          │   CourtListener API  │
                          │   (4,027 opinions)   │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                    ┌─────┤  Stage 1: Screening  ├─────┐
                    │     │  Gemini Flash Lite    │     │
                    │     │  Binary FHA filter    │     │
                    │     └──────────────────────┘     │
                    │                                   │
                 YES (2,522)                        NO (1,505)
                    │                               [discarded]
                    │
         ┌──────────▼──────────────────────────────────┐
         │         Stage 2: Triple-Model Classification │
         │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
         │  │ MiniMax  │ │ DeepSeek │ │    Kimi      │ │
         │  │  M2.7    │ │  V3.2    │ │    K2.5      │ │
         │  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
         │       │             │              │         │
         │       └─────────────┼──────────────┘         │
         └─────────────────────┼────────────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 3: Tiered Consensus       │
              │                                  │
              │  Tier 0: Unanimous    (0.6%)     │
              │  Tier 1-2: Majority   (45.4%)    │──► No API cost
              │  Tier 3: Haiku 4.5    (37.5%)    │──► Adjudication
              │  Tier 4: Sonnet 4.6   (16.3%)    │──► Full re-extract
              └────────────────┬────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 4: Per-Claim Extraction   │
              │  Haiku 4.5 decomposes            │
              │  3,193 cases → 6,718 claims      │
              └────────────────┬────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 5: Reproducibility Audit  │
              │  Opus 4.6 re-classifies          │
              │  50-case stratified sample        │
              │  Cohen's κ: 0.56–0.74            │
              └────────────────┬────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  FHA Unified Database│
                    │  2,522 cases, 28     │
                    │  fields per case     │
                    └─────────────────────┘
```

---

## Key Findings

**The convergence thesis.** Disability is the dominant axis of housing cost burden across racial groups. The disability penalty (10-17 percentage points, depending on race) exceeds the entire racial cost-burden gap among non-disabled renters (8.4 points Black-White). Enforcing § 3604(f)(3) does not trade off against racial equity — it reaches the same populations through a larger axis of disadvantage.

**The enforcement desert.** At minimum 823,000 disabled renters of color reside in non-entitlement communities structurally excluded from CDBG enforcement. For this population, disability-centered enforcement is the only federal pathway that exists.

**The litigation decline.** Three-period analysis reveals strict win rates falling from 18.0% (pre-*Loper Bright*) to 7.8% (post-*Loper Bright*, pre-HUD Secretary change) to 10.7% (post-HUD Secretary), with the P1-to-P2 decline statistically significant (p=0.007). Multivariate logistic regression confirms 40-51% lower odds of plaintiff victory.

**The capability gap.** Pro se plaintiffs constitute 64.8% of disability cases, surging to 76.7% in P3 (consistent with FHIP defunding), and win 5.3% of the time versus 32.1% for represented plaintiffs. Represented plaintiff success fully recovers to pre-*Loper Bright* levels in P3 (34.3%); the aggregate decline is entirely a composition effect.

**The procedural gatekeeping problem.** Courts cite *Iqbal* in 82.4% of disability MTD cases. MTD broad survival rates show continuous three-period decline: 25.5% to 18.6% to 14.1%.

**The design-and-construction gap.** 47% estimated noncompliance rate in pre-1990 multifamily housing, against 0.8% of fair housing complaints — a 56:1 ratio.

---

## The Dataset

| Scope | Cases |
|-------|:---:|
| Total screened-in FHA cases (all protected classes) | 2,522 |
| **Disability cases (analysis population)** | **1,720** |
| Dated disability cases (three-period analysis) | 1,191 |

**Three-Period Design:**

| Period | Date Range | n |
|--------|-----------|:---:|
| P1: Pre-*Loper Bright* | Jan 1, 2022 - June 28, 2024 | 456 |
| P2: Post-LB / Pre-HUD Secretary | June 28, 2024 - Feb 5, 2025 | 116 |
| P3: Post-HUD Secretary | Feb 5, 2025 - present | 317 |

### Data Dictionary (28-field schema)

Each case record contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `case_name` | string | Full case caption |
| `citation` | string | Reporter citation or docket number |
| `court` | string | Deciding court (e.g., "D. Ariz.") |
| `year` | integer | Decision year |
| `circuit` | string | Federal circuit |
| `procedural_posture` | enum | MTD, summary judgment, trial, preliminary injunction, etc. |
| `fha_section_cited` | array | FHA sections invoked (§ 3604(f), § 3604(c), etc.) |
| `primary_protected_class` | enum | Disability, race, national origin, familial status, etc. |
| `accommodation_type` | enum | Structural modification, equipment, service animal, policy exception, etc. |
| `outcome` | enum | Plaintiff win, defendant win, mixed, settled, procedural |
| `primary_claim_type` | enum | Reasonable accommodation, disparate treatment, design-and-construction, etc. |
| `claim_types` | array | All FHA claim theories raised |
| `plaintiff_type` | enum | Individual, fair housing org, government, group home operator |
| `defendant_type` | enum | Landlord, HOA, municipality, property manager, etc. |
| `disability_category` | enum | Mobility, mental health, substance abuse, sensory, etc. |
| `housing_type` | enum | Apartment, single-family, group home, public housing, etc. |
| `subsidy_program` | string | HUD program involvement (Section 8, LIHTC, etc.) |
| `iqbal_twombly_cited` | boolean | Whether *Iqbal*/*Twombly* pleading standards are invoked |
| `loper_bright_cited` | boolean | Whether *Loper Bright* is cited |
| `interactive_process_discussed` | boolean | Whether the interactive process is analyzed |
| `brief_summary` | string | One-paragraph case summary |
| `key_holding` | string | Primary legal holding |
| `key_cases_cited` | array | Principal authorities cited |
| `fha_claims` | array | Nested per-claim breakdown (claim type, outcome, reasoning) |
| `resolution_tier` | integer | Consensus tier that resolved this record (0-4) |
| `model_agreement` | object | Per-field agreement metadata across three classifiers |
| `adjudicator` | string | Which model adjudicated (if escalated) |
| `source_corpus` | enum | RA Database, 2015 FHA Database, or recent supplement |

---

## Methodology: Agile ELS

Traditional empirical legal studies at this scale — manually coding 2,522 court opinions — would require roughly 600 hours and substantial institutional funding. This dataset was constructed in one week for approximately $200.

**Agile Empirical Legal Studies (Agile ELS)** transposes the logic of inter-rater reliability from human coders to computational classifiers: three architecturally independent LLMs classify each case, and their disagreement becomes a quality signal. When they agree, accept. When they disagree, escalate.

### Three Principles

1. **Fail-fast hypothesis testing.** Construct a prototype dataset, test the claim, pivot or deepen — in the same week.
2. **Tiered consensus extraction.** Three independent LLMs (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) — selected for training-corpus independence — classify each case. Agreement determines confidence; disagreement escalates to Haiku 4.5, then Sonnet 4.6.
3. **Democratized access.** Total cost ~$200. 46% of cases resolved through consensus alone without an API call.

### Pipeline Stages

| Stage | Model | Task | Cost |
|:---:|-------|------|------|
| 1 | Gemini 3.1 Flash Lite | Binary FHA screening | ~$5 |
| 2 | MiniMax + DeepSeek + Kimi | 28-field parallel classification | ~$135 |
| 3 | Haiku 4.5 / Sonnet 4.6 | Tiered consensus adjudication | included above |
| 4 | Haiku 4.5 | Per-claim extraction (6,718 claims) | ~$18 |
| 5 | Opus 4.6 | Reproducibility audit (50 cases) | ~$5 |

### Resolution Tier Distribution (n=1,857 RA cases)

| Tier | Method | Records | % | API Cost |
|:---:|--------|:---:|:---:|:---:|
| 0 | Unanimous consensus | 12 | 0.6% | None |
| 1-2 | Majority vote | 843 | 45.4% | None |
| 3 | Haiku 4.5 adjudication | 697 | 37.5% | Low |
| 4 | Sonnet 4.6 adjudication | 302 | 16.3% | Moderate |

See [`pipeline/`](pipeline/) for model specifications, agreement rates, and resolution algorithms.

---

## Validation and Limitations

**Inter-model agreement** performed well on objective fields (court 96.9%, year 98.7%) and showed meaningful divergence on interpretive fields:

| Field | Unanimous | Majority | No Majority |
|-------|:---:|:---:|:---:|
| Court | 96.9% | 2.9% | 0.2% |
| Year | 98.7% | 1.2% | 0.2% |
| Outcome | 69.1% | 28.0% | 2.9% |
| Primary Claim Type | 62.6% | 32.2% | 5.2% |
| Accommodation Type | 34.7% | 45.8% | 19.5% |

**Reproducibility audit.** Opus 4.6 re-classified a stratified sample of 50 cases. Cohen's Kappa: 0.56-0.74 across substantive fields (Moderate to Substantial), consistent with inter-rater benchmarks in empirical legal research.

**Limitations.** The dataset captures federal written opinions only. Small-N subgroups (n < 30) are flagged as suggestive. Causal claims about *Loper Bright*'s independent judicial effect are expressly disclaimed. The reproducibility audit measures inter-classifier agreement, not accuracy against human-coded ground truth — no comparable human-coded dataset exists.

---

## Replication Guide

### Prerequisites

```bash
pip install -r requirements.txt
# Requires: pandas, numpy, scipy, statsmodels, requests, httpx, openpyxl, python-dotenv
```

### Pipeline 1: Litigation Database Analysis

```bash
python scripts/recompute_all_appendices.py    # Three-period stats for all appendices
python scripts/recompute_stats_unified.py     # Win rates, pro se, MTD, circuit analysis
python scripts/regression_analysis.py         # Multivariate logistic regression (7 models)
python scripts/regression_analysis_full.py    # Full regression with interaction terms
python scripts/fha_iqbal_analysis.py          # Iqbal pleading barrier quantification
python scripts/positional_bias_v2.py          # LLM positional bias analysis
```

### Pipeline 2: Census PUMS Housing Analysis

```bash
python scripts/pums_costburden_analysis.py    # Cost burden by race x disability with SE
python scripts/pums_cb_se.py                  # Standard errors (80 replicate weights)
python scripts/pums_housing_stock_analysis.py # Pre-1990 accessibility gaps
python scripts/pums_dis1_sensitivity.py       # Disability-definition sensitivity
python scripts/pums_5year_aian_analysis.py    # AIAN-focused analysis
python scripts/pums_cdbg_analysis.py          # CDBG non-entitlement analysis
```

### Key Outputs

| File | Contents |
|------|----------|
| `results/appendix_report.md` | Three-period statistics for all appendices |
| `results/unified_stats_report.md` | Win rates, pro se, MTD, circuit, interactive process |
| `results/pums_se_results.json` | Cost burden with standard errors and disability penalties |
| `results/housing_stock_results.json` | Building-era accessibility analysis |
| `results/pums_sensitivity_results.json` | Disability-definition sensitivity |

---

## Data Sources

| Source | Description |
|--------|-------------|
| [CourtListener REST API v4](https://www.courtlistener.com/api/rest/v4/) | Federal court opinion text |
| [ACS 2020-2024 5-Year PUMS](https://api.census.gov/data/2024/acs/acs5/pums) | Census microdata for housing analysis |
| [OpenRouter API](https://openrouter.ai/) | Multi-model LLM access |

## Companion Repository

The Java source code for the CourtListener download pipeline, OpenRouter classification clients, and tiered consensus resolution is maintained separately:

**[MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work)** — contains `CourtListenerFHADownloader.java`, `OpenRouterConfirmationClient.java`, and field normalization/consensus resolution logic.

Researchers wishing to replicate the full pipeline from raw CourtListener data need both repositories. Those verifying statistical analyses can use the pre-built database files in `data/`.

---

## How to Cite

```bibtex
@dataset{gill_fha_2026,
  author    = {Gill, Nicholas},
  title     = {FHA Unified Database: Replication Package for Displacing Deference},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/nickgill97/FHAdata}
}
```

Or use the [CITATION.cff](CITATION.cff) file for automatic citation via GitHub's "Cite this repository" feature.

---

## License

[MIT](LICENSE) — This replication package is provided for academic use. The underlying court opinions are public domain.
