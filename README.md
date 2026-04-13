# Displacing Deference: Reinforcement, Replication, and Disability-Centered AFFH

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE) [![License: CC BY 4.0](https://img.shields.io/badge/Data-CC_BY_4.0-lightgrey.svg)](LICENSE-DATA)

**Nicholas Gill** | J.D. Candidate, 2027 | University of Arizona James E. Rogers College of Law | nickgill@arizona.edu

## Abstract

This replication package supports a Note arguing that AFFH's present problem is a durability failure and that disability exposes it most clearly. Four incompatible AFFH frameworks from 2015 to 2025 demonstrate that affirmative content built chiefly on section 3608(d)'s undefined language has not survived political turnover. The 2015 Rule operationalized race-centered integration while leaving disability structurally underbuilt — and no published federal AFFH decision applies the affirmative integration obligation to disability.

The empirical foundation is the **FHA Unified Database**: 2,522 federal FHA cases across all protected classes (1,770 disability), constructed through a multi-model LLM consensus pipeline. The central empirical finding is a **composition effect**: represented plaintiffs recovered to roughly their pre-*Loper Bright* success rates (Level C), but the pro se filing share surged to 76.7% as institutional intermediaries contracted, concentrating the aggregate decline at the pleading stage. The post-2024 downturn is better understood as an enforcement-pipeline failure — disability complaints reached approximately 17,600 in 2024 while only ~1.5% resulted in charges and roughly 53 complaints entered the administrative system for every case reaching federal litigation — than as generalized judicial hostility.

The Note's doctrinal contribution is a limiting principle: the distinction between *reinforcement* — using HUD's administration and reporting authority under sections 3608(e)(5)–(6) and its rulemaking power under section 3614a to verify compliance with duties Congress enacted in section 3604(f)(3) — and *replication* — generating broad new obligations from section 3608(d)'s undefined text. Under present conditions, AFFH is on firmer ground reinforcing enacted disability duties than replicating the full 2015-style integration project. The repository also contains race-by-disability housing cost-burden estimates derived from ACS 2020–2024 5-Year PUMS microdata with confidence intervals.

---

## Original Contributions

- **Doctrinal limiting principle**: The reinforcement/replication distinction — grounded in the statutory architecture of sections 3608(d), 3608(e)(5)–(6), 3614a, and 3604(f)(3) — as the basis for a disability-centered AFFH model that verifies compliance with enacted duties rather than reconstructing broad planning obligations from open-textured statutory text
- **Classified FHA litigation dataset**: 1,770 federal FHA disability decisions (from a broader corpus of 2,522 FHA cases across protected classes), each with 28 classified fields, constructed through multi-model LLM consensus classification with tiered adjudication — no comparable classified FHA litigation dataset exists in the published literature
- **Enforcement-pipeline analysis**: Integration of administrative-system data (CDBG activity codes, REAC/NSPIRE inspection outputs, POSH disability rates, FHEO complaint series) documenting that HUD's grant-reporting and inspection architectures contain no field for housing accessibility despite covering approximately 1.8 million disabled households
- **Race-by-disability housing cost-burden cross-tabulations**: First published estimates with confidence intervals, derived from ACS 2020–2024 5-Year PUMS microdata using successive-differences replication

---

## Key Findings

The data support a narrower institutional account of the post-2024 downturn than a simple "courts turned hostile" story.

**The composition effect.** Pro se plaintiffs surged to 76.7% of disability filings in P3 (Level A), consistent with FHIP disruption and institutional contraction. Represented plaintiff success recovered to roughly pre-*Loper Bright* levels — 34.3% strict win in both P1 and P3 (Level C) — while pro se plaintiffs won on the merits 5.3% of the time versus 32.1% for represented plaintiffs. A Kitagawa composition/rate decomposition attributes 76% of the aggregate P1-to-P3 win-rate decline to the shifting composition of the plaintiff pool rather than within-group deterioration. The aggregate decline is a composition effect consistent with institutional contraction, not a generalized shift in judicial hostility. See [Appendix A-5](appendices/Appendix_A5_Robustness_Checks.md) for full robustness checks.

**The enforcement pipeline.** Disability complaints reached approximately 17,600 in 2024 (+8.7% since 2018), yet fair housing organizations processing 74% of all complaints declined from 86 to 82 in a single year, only ~1.5% of disability complaints resulted in a charge or cause finding, and roughly 53 complaints entered the administrative system for every case reaching federal litigation. Nothing in the current administrative record suggests that the underlying violation rate is declining.

**The administrative measurement failure.** HUD's CDBG accomplishment system contains approximately fifty activity codes; none covers housing accessibility. HUD's REAC/NSPIRE inspection program reaches over 34,000 properties but produces a single aggregate physical-condition score with no accessibility or design-and-construction field. Approximately 1.8 million disabled households reside in federally subsidized housing (weighted disability rate: 39.3%), yet the systems that fund, certify, and inspect their housing cannot generate disability-specific compliance data.

**The litigation decline.** Three-period analysis reveals strict win rates falling from 18.0% (P1: baseline) to 7.8% (P2: transition) to 10.7% (P3: post-withdrawal). Represented plaintiff MTD survival remains stable across all three periods (82.0%/76.1%/82.8%), while aggregate MTD survival falls from 53.6% to 38.6%, confirming that the decline concentrates at the pleading stage among unrepresented plaintiffs.

**Specificity drives outcomes.** Specific-duty claims grounded in section 3604(f)(3) achieve a 39.3% broad win rate; open-textured claims relying on broad statutory purpose achieve 1.0%. After controls, open-textured framing reduces odds of success by 97% (OR=0.033, p<10⁻¹⁰), while enacted-duty framing increases odds more than twelvefold (OR=12.33, p<10⁻¹⁷). The composition confound is real — 88.5% of open-textured cases are pro se — but specificity remains the dominant predictor after controlling for representation.

**The disability penalty.** The disability cost-burden penalty (7.3–16.9 percentage points, depending on race) exceeds the racial cost-burden gap among non-disabled renters (8.4 points Black–White). An estimated 823,000 disabled renters of color reside in non-entitlement communities the 2015 model never directly reached. These distributional facts are descriptive, not thesis-bearing.

**The design-and-construction gap.** 47% estimated noncompliance rate in covered multifamily housing, against 0.8% of fair housing complaints and 2.2% of litigated cases. Physical evidence is present in 37 of 40 decided design-and-construction cases, confirming the tractability of verification-centered enforcement.

---

## The Dataset

This repository provides what HUD does not: a structured empirical dataset of federal FHA litigation, unified from multiple source corpora into a single classified database.

| Scope | Cases |
|-------|:---:|
| Total screened-in FHA cases (all protected classes) | 2,522 |
| **Disability cases (analysis population)** | **1,770** |
| Dated disability cases (three-period analysis) | 1,191 |
| Resolved-outcome cases (temporal analysis) | 889 |

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
                    │     │  Gemini Flash Lite    │    │
                    │     │  Binary FHA filter    │    │
                    │     └──────────────────────┘     │
                    │                                  │
                 YES (2,522)                       NO (1,505)
                    │                             [discarded]
                    │
         ┌──────────▼──────────────────────────────────┐
         │    Stage 2: Triple-Model Classification     │
         │  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
         │  │ MiniMax  │ │ DeepSeek │ │    Kimi      │ │
         │  │  M2.7    │ │  V3.2    │ │    K2.5      │ │
         │  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
         │       │             │              │        │
         │       └─────────────┼──────────────┘        │
         └─────────────────────┼───────────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 3: Tiered Consensus      │
              │                                 │
              │  Tier 0: Unanimous    (0.6%)    │──► Accept
              │  Tier 1-2: Majority   (45.4%)   │──► Accept
              │  Tier 3: Haiku 4.5    (37.5%)   │──► Adjudicate
              │  Tier 4: Sonnet 4.6   (16.3%)   │──► Re-extract
              └────────────────┬────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 4: Per-Claim Extraction  │
              │  Haiku 4.5 decomposes           │
              │  3,193 cases → 6,718 claims     │
              └────────────────┬────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │  Stage 5: Reproducibility Audit │
              │  Opus 4.6 re-classifies         │
              │  50-case stratified sample      │
              │  Cohen's κ: 0.56–0.74           │
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
| [L](appendices/Appendix_L_HUD_Administrative_Data.md) | HUD Administrative Data (CDBG, POSH, REAC/NSPIRE) |

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

Nicholas Gill, *Displacing Deference: Reinforcement, Replication, and Disability-Centered AFFH* (forthcoming 2026).

```bibtex
@article{gill_displacing_2026,
  author    = {Gill, Nicholas},
  title     = {Displacing Deference: Reinforcement, Replication, and Disability-Centered AFFH},
  year      = {2026},
  note      = {Forthcoming}
}
```

---

## About the Author

**Nicholas Gill** is a J.D. Candidate (2027) at the University of Arizona James E. Rogers College of Law. The FHA Unified Database was designed and built by the author. Contact: [nickgill@arizona.edu](mailto:nickgill@arizona.edu).

---
## AI Use Policy

Artificial-intelligence tools assisted limited aspects of research, document classification, data processing, and drafting in this project. The empirical methodology is also intended to show that AI-assisted legal classification can help individual researchers construct and validate datasets at a scale that previously required institutional resources. AI outputs were used as research aids and analytical instruments, not as legal authority and not as substitutes for primary-source analysis. The author independently reviewed and verified all cited authorities, quotations, source characterizations, coding judgments, and empirical results, and made all analytical, doctrinal, and editorial decisions. No confidential or privileged information was submitted to external AI systems. The full classification pipeline and replication materials are documented here.

---
## License

- **Code** (scripts/, pipeline/, queries/, prompts/): [MIT](LICENSE)
- **Data and documentation** (data/, appendices/): [CC BY 4.0](LICENSE-DATA)

The underlying court opinions are public domain. See [CREDITS.md](CREDITS.md) for full data source attributions.
