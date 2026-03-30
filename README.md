# Displacing Deference: Data and Doctrine for a Disability-Centered AFFH

**Nick Gill** | University of Arizona James E. Rogers College of Law

---

## The Argument

Congress directed federal agencies to "affirmatively further" fair housing but never defined what the obligation required. 42 U.S.C. § 3608(d) specifies neither the content of that mandate nor the outcomes it was meant to produce — an omission that has driven five incompatible regulatory frameworks in a single decade.

The contest has produced two competing models. The **Proactive Integration Model** treats fair housing as a spatial project, measuring progress through dissimilarity indices and racial dispersal across census tracts. The **Equal Access Model** treats fair housing as a transactional guarantee, eliminating discrimination without mandating demographic outcomes. Neither model engages the protected class now dominating fair housing enforcement: **disability**, which constitutes 54.6% of all fair housing complaints and 38.1% of federal litigation.

This project argues that the post-*Loper Bright* constitutional landscape strongly counsels recalibrating AFFH through the disability-specific mandates of § 3604(f)(3). The elimination of *Chevron* deference and the Major Questions Doctrine substantially constrain the integration model's expansive reading of "affirmatively further," while § 3604(f)(3)'s specific statutory commands — reasonable modifications, reasonable accommodations, and design-and-construction accessibility standards — possess constitutional durability that the ambiguous § 3608(d) delegation lacks.

### Why Disability, Not Race, Is the Structural Pivot

The recalibration is not a retreat from racial equity. Disability is the dominant axis of housing cost burden: the disability penalty (10–17 percentage points across racial groups) exceeds the entire racial cost-burden gap among non-disabled renters (8.4 points Black-White). Among disabled renters, the Black-White cost-burden gap compresses to 1.6 percentage points (56.3% vs. 54.7%). The integration model measures the smaller axis. Section 3604(f)(3) targets the larger one.

At minimum 823,000 disabled renters of color reside in non-entitlement communities the integration model structurally excluded. For this population, disability-centered enforcement is not a tradeoff — it is the only federal enforcement pathway that exists.

### The Empirical Gap This Repository Fills

The entire AFFH canon — from *Shannon* to *Inclusive Communities* — was built to address racial segregation. Disability has generated **zero AFFH precedent** despite dominating the complaint docket since at least the mid-2000s. HUD collects no systematic data on accommodation requests or denials and maintains no national accessible housing inventory. None of the forty-nine AFH submissions contained quantitative accessibility data.

This repository provides what HUD does not: a structured empirical dataset of approximately 2,566 unique federal FHA cases across all protected classes — drawn from three databases (RA Database, n=1,857; 2015 FHA Database, n=1,496; FHA Pilot Database, n=331) and deduplicated into a Unified Dataset of 3,193 cases (6,718 individual claims) for per-claim analysis. The disability-specific findings rely primarily on the 2015 FHA Database (§ 3604(f) cases); the RA Database provides cross-class comparisons across all FHA protected classes.

### Key Empirical Findings

- **Plaintiff win rates declined significantly after *Loper Bright***: In the 2015 FHA Database (§ 3604(f) disability cases), strict plaintiff win rates fell from 21.5% to 13.7% (p=0.0004); the RA Database (all protected classes) shows a corroborating decline from 16.7% to 9.0%
- **Procedural gatekeeping disproportionately burdens disability claims**: courts cite *Iqbal* in disability cases at ~3.3x the rate observed in race cases; when invoked, defendant success at MTD rises from 43.1% to 66.7%
- **Accommodation type predicts outcomes**: assistance-animal claims yield 38.7% plaintiff success; transfer claims yield 5.4% — suggesting the doctrinal framework advantages discrete, low-cost accommodations over structural or administrative changes
- **Design-and-construction enforcement is virtually absent**: 47% noncompliance rate against 0.8% of complaints — a 56:1 ratio

---

## Why Three Models Instead of One

The core empirical claim of this project requires classifying approximately 2,566 unique federal FHA opinions into structured data. The RA Database (n=1,857, all protected classes) and 2015 FHA Database (n=1,496, § 3604(f) disability cases) were deduplicated into a Unified Dataset of 3,193 cases, then decomposed via per-claim extraction into 6,718 individual claims. That is the kind of dataset HUD has never built and no existing legal database provides.

**Manual review was not feasible.** A single researcher reading and coding 3,193 opinions at even 15 minutes per case would need approximately 800 hours — roughly five months of full-time work. Traditional research-assistant coding at that scale introduces its own reliability problems (coder drift, inconsistent application of classification rules, fatigue-induced errors) and would require extensive inter-rater reliability testing to validate. The dataset simply could not exist without automated classification.

**But a single LLM is not trustworthy enough.** In 2023, HUD's Office of Policy Development and Research published [*Generative AI: Mining Housing Data With a Higher Powered Shovel*](https://www.huduser.gov/portal/periodicals/cityscape/vol25num3/ch9.pdf) (Dylan J. Hayden, *Cityscape* Vol. 25 No. 3), demonstrating that generative AI could accelerate housing data analysis while flagging the risks of bias and hallucination that demand human supervision. A single LLM will hallucinate, miscategorize, and silently drop fields — and when the entire empirical foundation of a law review article depends on the accuracy of that classification, silent errors are unacceptable.

**The solution was to use three independent LLMs and treat disagreement as a quality signal.** Rather than trusting any single model, the pipeline runs each case through three separate models and uses their agreement (or lack of it) to determine confidence and route difficult cases to stronger adjudicators. This approach applies the logic of inter-rater reliability — the same principle that governs human coding in empirical legal research — to automated classification:

1. **No single point of failure.** Three independent models (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) classify each case separately. When all three disagree, the case is flagged for adjudication rather than silently miscoded.

2. **Disagreement is signal, not noise.** A three-way split on `outcome` or `claim_type` usually means the case is genuinely ambiguous — multi-claim opinions, mixed dispositions, or unusual procedural postures. The pipeline routes these to stronger adjudication models that see all three answers plus the original text.

3. **Cost-tiered escalation.** Most cases resolve at the cheap consensus tier. Only the hard cases escalate. Total pipeline cost for 3,193 cases: ~$160.

4. **Auditable at every stage.** Every record carries resolution metadata: which tier resolved it, which models agreed, what the adjudicator decided and why. The audit database preserves all three model outputs (~91 fields/record) alongside the canonical answer (~27 fields).

### Pipeline Performance

**Inter-model agreement rates** confirm that the three-model design catches real ambiguity rather than generating artificial noise. Objective fields achieve near-perfect consensus while interpretive fields — where human coders would also disagree — show meaningful divergence:

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

**Resolution tier distribution** (n=1,857 RA cases):

| Tier | Resolution Method | Records | % |
|:---:|---|:---:|:---:|
| 0 | Unanimous consensus | 12 | 0.6% |
| 1–2 | Majority vote (no API call) | 843 | 45.4% |
| 3 | Haiku 4.5 adjudication | 697 | 37.5% |
| 4 | Sonnet 4.6 adjudication | 302 | 16.3% |

Nearly half of all cases resolved at the cheap majority-vote tier. The remaining cases escalated to progressively stronger (and more expensive) adjudicators — concentrating cost on the genuinely difficult classifications.

**Reproducibility audit.** Claude Opus 4.6 independently re-classified a stratified random sample of 50 cases. Aggregate match rate across 12 vocabulary-aligned fields: **81.5%**. Cohen's Kappa scores ranged from Moderate (outcome: κ=0.561) to Substantial (defendant type: κ=0.740), consistent with inter-rater reliability benchmarks in empirical legal research.

| Field | Match Rate | Cohen's Kappa |
|-------|:---:|:---:|
| Plaintiff Type | 90.0% | 0.668 (Substantial) |
| Defendant Type | 78.0% | 0.740 (Substantial) |
| Outcome | 70.0% | 0.561 (Moderate) |
| Primary Claim Type | 62.0% | 0.511 (Moderate) |

See [`pipeline/model_configuration.md`](pipeline/model_configuration.md) for full agreement rates, cost breakdowns, and audit methodology.

---

## Classification Pipeline

The pipeline processes court opinions through five stages:

1. **FHA Screening** — Gemini 3.1 Flash Lite binary classifier filters non-FHA opinions
2. **Triple-Model Classification** — MiniMax M2.7 + DeepSeek V3.2 + Kimi K2.5 independently produce 28-field structured JSON per case
3. **Tiered Consensus Resolution** — Unanimous → majority vote → Haiku 4.5 adjudication → Sonnet 4.6 adjudication (RA Database). The 2015 FHA Database uses the same triple-model classification but resolves three-way splits via MiniMax M2.7 tiebreaker rather than API adjudication; see Appendix A, Section A.3
4. **Per-Claim Extraction** — Haiku 4.5 decomposes multi-claim cases into individual legal claims
5. **Reproducibility Audit** — Opus 4.6 re-classifies a stratified sample for inter-rater reliability

See [`pipeline/`](pipeline/) for full documentation including model costs, agreement rates, and resolution tier distributions.

## Data Sources

| Source | Access |
|--------|--------|
| CourtListener REST API v4 | https://www.courtlistener.com/api/rest/v4/ |
| ACS 2020-2024 5-Year PUMS | https://api.census.gov/data/2024/acs/acs5/pums |
| OpenRouter API | https://openrouter.ai/ |
| Anthropic Message Batches API | https://docs.anthropic.com/ |

## Source Code

The Java and Python source code for the download pipeline, classification clients, and evaluation framework is maintained in the companion repository: **[MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work)**

## Dataset

The unified dataset (N=3,193 cases, 6,718 claims) and full audit trail are available upon request.

## License

This replication package is provided for academic use. The underlying court opinions are public domain.

---

## Appendices

The following supplementary appendices are referenced throughout the Note's footnotes. Each appendix is available as a standalone document in the [`appendices/`](appendices/) directory.

| Appendix | Title | Description |
|----------|-------|-------------|
| [A](appendices/Appendix_A_Case_Dataset_Methodology.md) | FHA Case Dataset — Construction Methodology | Full dataset construction methodology, source accounting, deduplication, classification protocol, and known limitations |
| [A-2](appendices/Appendix_A2_PUMS_Replication.md) | PUMS Replication Methodology | ACS 2020–2024 5-Year PUMS variable definitions, replication queries, standard errors via successive-differences replication, and sensitivity analysis |
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

## Repository Structure

```
prompts/                              # LLM classification instruments
  fha_screening_prompt.txt            # Stage 1: Gemini binary FHA screening
  case_classification_prompt.txt      # Stage 2: 28-field structured extraction

queries/                              # API query specifications
  census_pums_queries.md              # ACS 2020-2024 5-Year PUMS queries
  courtlistener_api.md                # CourtListener REST API v4 download specs

scripts/                              # Executable replication scripts
  census_pums_replication.py          # Full Census PUMS analysis (Python 3)
  regression_analysis.py              # Multivariate logistic regression

pipeline/                             # Classification pipeline documentation
  model_configuration.md              # Model specs, costs, and agreement rates
  consensus_resolution.md             # Tiered consensus algorithm
  per_claim_extraction_schema.json    # Haiku 4.5 per-claim schema
  field_normalization.md              # Free-text normalization rules

appendices/                            # Supplementary appendices (A through K)

analysis/                             # Extended analysis methodology
```
