# Displacing Deference: Administrative Failure, Empirical Evidence, and the Case for a Disability-Centered AFFH

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE) [![License: CC BY 4.0](https://img.shields.io/badge/Data-CC_BY_4.0-lightgrey.svg)](LICENSE-DATA)

**Nicholas Gill** | J.D. Candidate, 2027 | University of Arizona James E. Rogers College of Law | nickgill@arizona.edu

## Abstract

Federal fair housing law requires agencies to "affirmatively further" fair housing but has never defined what that obligation means — and HUD's administrative choices, not judicial doctrine, created the resulting enforcement crisis. This replication package supports a law review note demonstrating that HUD's withdrawal of institutional support — guidance rescission, FHIP defunding, and zero reasonable-cause charges — drove the post-2024 decline in plaintiff success, while disability, the protected class generating the majority of all FHA complaints, has produced zero published federal precedent under the affirmative mandate. The empirical foundation is the **FHA Unified Database**: 2,522 federal FHA cases across all protected classes (1,720 disability), constructed through a novel multi-model LLM consensus pipeline this Note terms **Agile Empirical Legal Studies (Agile ELS)**. No comparable classified FHA litigation dataset exists in the published literature; HUD has never produced one. The repository also contains the first published race-by-disability housing cost-burden estimates derived from ACS 2020-2024 5-Year PUMS microdata with confidence intervals. Together, the litigation and Census analyses demonstrate that disability is simultaneously the largest axis of housing cost burden, the dominant source of fair housing complaints, and the most neglected category in federal AFFH enforcement — and that rebuilding the mandate around the Act's disability-specific commands in 42 U.S.C. § 3604(f)(3) offers a durable alternative that does not depend on the ambiguous delegation no administration has been able to sustain.

---

## Key Findings

**The convergence thesis.** Disability is the dominant axis of housing cost burden across racial groups. The disability penalty (10-17 percentage points, depending on race) exceeds the entire racial cost-burden gap among non-disabled renters (8.4 points Black-White). Among disabled renters, the Black-White gap compresses to 1.6 percentage points. Enforcing § 3604(f)(3) does not trade off against racial equity — it reaches the same populations through a larger axis of disadvantage.

**The enforcement desert.** At minimum 823,000 disabled renters of color reside in non-entitlement communities structurally excluded from CDBG enforcement under the integration model. For this population, disability-centered enforcement is the only federal pathway that exists.

**The litigation decline.** Three-period analysis reveals strict win rates falling from 18.0% (P1: pre-*Loper Bright*) to 7.8% (P2: post-*Loper Bright*, pre-HUD Secretary change) to 10.7% (P3: post-HUD Secretary), with the P1-to-P2 decline statistically significant (p=0.007). Multivariate logistic regression confirms 40-51% lower odds of plaintiff victory after controlling for procedural posture, defendant type, accommodation type, and plaintiff type.

**The capability gap.** Pro se plaintiffs constitute 64.8% of disability filings, surging to 76.7% in P3 (consistent with FHIP defunding), and win 5.3% of the time versus 32.1% for represented plaintiffs. Represented plaintiff success fully recovers to pre-*Loper Bright* levels in P3 (34.3%); the aggregate decline is entirely a composition effect driven by the withdrawal of institutional support.

**The procedural gatekeeping problem.** Courts cite *Iqbal*/*Twombly* in 82.4% of disability motions to dismiss. MTD broad survival rates show continuous three-period decline: 25.5% → 18.6% → 14.1%.

**The design-and-construction gap.** 47% estimated noncompliance rate in pre-1990 multifamily housing, against 0.8% of fair housing complaints — a 56:1 enforcement-to-violation ratio.

---

## The Dataset

This repository provides what HUD does not: a structured empirical dataset of federal FHA litigation, unified from multiple source corpora into a single classified database.

| Scope | Cases |
|-------|:---:|
| Total screened-in FHA cases (all protected classes) | 2,522 |
| **Disability cases (analysis population)** | **1,720** |
| Dated disability cases (three-period analysis) | 1,191 |

**Three-Period Design:**

| Period | Date Range | n |
|--------|-----------|:---:|
| P1: Pre-*Loper Bright* | Jan 1, 2022 – June 28, 2024 | 456 |
| P2: Post-LB / Pre-HUD Secretary | June 28, 2024 – Feb 5, 2025 | 116 |
| P3: Post-HUD Secretary | Feb 5, 2025 – present | 317 |

Each case record contains 28 classified fields — including procedural posture, outcome, accommodation type, disability category, plaintiff and defendant type, *Iqbal*/*Twombly* citation, and nested per-claim decomposition — plus full pipeline provenance metadata. For the complete field-level schema with types, enumerated values, and examples, see [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

The repository also includes Census PUMS analysis producing the first published race-by-disability cost-burden cross-tabulations with confidence intervals, using successive-differences replication with 80 replicate weights per the Census Bureau's recommended variance estimation method.

---

## Methodology: Agile ELS

Traditional empirical legal studies at this scale — manually reading and coding 2,522 court opinions into structured data — would require roughly 600 researcher-hours, substantial institutional funding, and extensive inter-rater reliability testing. This dataset was constructed in one week for approximately $200.

The approach, which this Note terms **Agile Empirical Legal Studies (Agile ELS)**, rests on a straightforward methodological insight: rather than trusting a single LLM to classify thousands of cases, each opinion is processed by three architecturally independent models, and their disagreement is treated as a quality signal — the same logic that governs inter-rater reliability in traditional human-coded empirical legal research, transposed to computational classifiers.

**Independence by design.** The three primary classifiers (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) were selected for training-corpus independence: different training data (Chinese and Western sources), different parameter scales, and different fine-tuning approaches. This ensures that consensus reflects textual signal in the opinion rather than shared model bias.

**Tiered adjudication.** When all three models agree, the classification is accepted without further review. When they disagree, contested fields escalate to progressively stronger adjudicators — first Claude Haiku 4.5, then Claude Sonnet 4.6 with fresh narrative extraction. Every record carries full provenance metadata: which tier resolved it, which models agreed, and what the adjudicator decided.

**Cost structure.** 46% of cases resolved through consensus or majority vote alone, requiring no additional API call. The remaining cases escalated, concentrating cost on the genuinely difficult classifications. Total pipeline cost for 2,522 cases: approximately $160.

To the best of the author's knowledge, no published legal study has employed multi-model LLM consensus with tiered adjudication for structured legal data extraction at this scale.

### Pipeline Architecture

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
              │  Tier 0: Unanimous    (0.6%)     │──► Accept
              │  Tier 1-2: Majority   (45.4%)    │──► Accept
              │  Tier 3: Haiku 4.5    (37.5%)    │──► Adjudicate
              │  Tier 4: Sonnet 4.6   (16.3%)    │──► Re-extract
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
              └─────────────────────────────────┘
```

See [`pipeline/`](pipeline/) for full model specifications, cost breakdowns, agreement rates, and resolution algorithms.

---

## Validation and Limitations

The multi-model design performed well on objective fields and showed meaningful divergence on interpretive fields where human coders would also disagree:

| Field | Unanimous (3/3) | Majority (2/3) | No Majority |
|-------|:---:|:---:|:---:|
| Court | 96.9% | 2.9% | 0.2% |
| Year | 98.7% | 1.2% | 0.2% |
| Outcome | 69.1% | 28.0% | 2.9% |
| Primary Claim Type | 62.6% | 32.2% | 5.2% |
| Accommodation Type | 34.7% | 45.8% | 19.5% |

Only 0.6% of cases achieved full unanimous consensus across all fields — meaning the multi-model design caught disagreements requiring resolution in 99.4% of records.

**Reproducibility audit.** Opus 4.6 independently re-classified a stratified random sample of 50 cases. Cohen's Kappa ranged from Moderate to Substantial (κ = 0.56–0.74) across substantive fields, consistent with inter-rater reliability benchmarks in empirical legal research. The outcome kappa (κ = 0.561) warrants context: of 15 disagreements, 11 (73%) involved the procedural/substantive boundary — whether a dismissal without prejudice constitutes a "Defendant Win" or a "Procedural" disposition. These are genuine boundary disputes that produce moderate kappa scores even among trained human coders. Because the disagreement pattern is directional — pipeline classifications skewing toward "procedural" — any resulting measurement error attenuates regression coefficients toward the null, making statistically significant findings conservative estimates.

**What this audit does and does not show.** The reproducibility audit measures inter-classifier agreement, not accuracy against human-coded ground truth. No human-coded FHA litigation dataset of comparable scope exists against which to benchmark. The kappa scores are consistent with published inter-rater reliability standards — but the claim is that independent classifiers operating under identical protocols reach substantially similar results, not that the pipeline achieves perfect accuracy.

**Additional limitations.** The dataset captures federal written opinions only, not the universe of FHA disputes, settlements, or administrative resolutions. Small-N subgroup analyses (n < 30) are flagged as suggestive throughout the article. Causal claims about *Loper Bright*'s independent judicial effect are expressly disclaimed; this Note treats the post-2024 period as a changed legal-administrative environment encompassing guidance withdrawal, FHIP defunding, and zero reasonable-cause charges alongside the elimination of *Chevron* deference.

---

## Supplementary Appendices

The following appendices are referenced throughout the Note's footnotes. Each is available as a standalone document in [`appendices/`](appendices/).

| Appendix | Title |
|----------|-------|
| [A](appendices/Appendix_A_Case_Dataset_Methodology.md) | FHA Case Dataset — Construction Methodology |
| [A-2](appendices/Appendix_A2_PUMS_Replication.md) | PUMS Replication Methodology |
| [A-3](appendices/Appendix_A3_Extended_Empirical_Analysis.md) | Extended Empirical Analysis |
| [A-4](appendices/Appendix_A4_Reproducibility_Audit.md) | Classification Reproducibility Audit |
| [B](appendices/Appendix_B_Results_Tables.md) | Post-*Loper Bright* Analysis |
| [C](appendices/Appendix_C_Iqbal_Citation_Analysis.md) | *Iqbal* Citation Analysis |
| [D](appendices/Appendix_D_Protected_Class_Distribution.md) | Protected-Class Distribution |
| [E](appendices/Appendix_E_Accommodation_Defendant_Analysis.md) | Accommodation & Defendant-Type Analysis |
| [F](appendices/Appendix_F_Galanter_Plaintiff_Type.md) | Galanter Plaintiff-Type Analysis |
| [G](appendices/Appendix_G_Circuit_Level_Analysis.md) | Circuit-Level Analysis |
| [H](appendices/Appendix_H_Supplementary_Data.md) | Supplementary Data |
| [I](appendices/Appendix_I_AFFH_Case_Classification.md) | AFFH Case Classification |
| [J](appendices/Appendix_J_Safe_Harbor_Detail.md) | Safe Harbor Operational Detail |
| [K](appendices/Appendix_K_Classification_Prompts.md) | Classification Prompts |

---

## Data Sources

| Source | Description |
|--------|-------------|
| [CourtListener REST API v4](https://www.courtlistener.com/api/rest/v4/) | Federal court opinion text |
| [ACS 2020-2024 5-Year PUMS](https://api.census.gov/data/2024/acs/acs5/pums) | Census microdata for housing analysis |
| [OpenRouter API](https://openrouter.ai/) | Multi-model LLM access for classification pipeline |

---

## Replication

```bash
pip install -r requirements.txt
python scripts/run_all.py              # Full replication (litigation + PUMS)
python scripts/run_all.py --litigation-only
python scripts/run_all.py --pums-only
```

The FHA Unified Database JSON files are included in `data/`. PUMS scripts query the Census Bureau's public API and do not require an API key. Individual analysis scripts are documented in [`scripts/`](scripts/); see [`scripts/run_all.py`](scripts/run_all.py) for the complete execution sequence.

---

## How to Cite

Nicholas Gill, *Displacing Deference: Administrative Failure, Empirical Evidence, and the Case for a Disability-Centered AFFH*, __ ___. L. Rev. __ (forthcoming 2026).

```bibtex
@article{gill_displacing_2026,
  author    = {Gill, Nicholas},
  title     = {Displacing Deference: Administrative Failure, Empirical Evidence, and the Case for a Disability-Centered AFFH},
  journal   = {__ ___. L. Rev.},
  year      = {2026},
  note      = {Forthcoming}
}
```

---

## License

- **Code** (scripts/, pipeline/, queries/, prompts/): [MIT](LICENSE)
- **Data and documentation** (data/, appendices/): [CC BY 4.0](LICENSE-DATA)

The underlying court opinions are public domain. See [CREDITS.md](CREDITS.md) for full data source attributions.
