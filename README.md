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

This repository provides what HUD does not: a structured empirical dataset of 3,193 federal disability accommodation cases decomposed into 6,718 individual claims, classified by accommodation type, outcome, procedural posture, disability category, and housing type — enabling the first large-scale analysis of how courts actually decide reasonable-accommodation claims under § 3604(f)(3).

### Key Empirical Findings

- **Plaintiff win rates declined significantly after *Loper Bright***: from 25.3% (n=673) to 17.9% (n=330), p=0.012
- **Procedural gatekeeping disproportionately burdens disability claims**: courts cite *Iqbal* in disability cases at ~3.3x the rate observed in race cases; when invoked, defendant success at MTD rises from 43.1% to 66.7%
- **Accommodation type predicts outcomes**: assistance-animal claims yield 38.7% plaintiff success; transfer claims yield 5.4% — suggesting the doctrinal framework advantages discrete, low-cost accommodations over structural or administrative changes
- **Design-and-construction enforcement is virtually absent**: 47% noncompliance rate against 0.8% of complaints — a 56:1 ratio

---

## Why Three Models Instead of One

The core empirical claim of this project requires classifying 3,193 federal court opinions into structured data — extracting accommodation type, outcome, procedural posture, disability category, and housing type from each case, ultimately yielding 6,718 individual claims. That is the kind of dataset HUD has never built and no existing legal database provides.

**Manual review was not feasible.** A single researcher reading and coding 3,193 opinions at even 15 minutes per case would need approximately 800 hours — roughly five months of full-time work. Traditional research-assistant coding at that scale introduces its own reliability problems (coder drift, inconsistent application of classification rules, fatigue-induced errors) and would require extensive inter-rater reliability testing to validate. The dataset simply could not exist without automated classification.

**But a single LLM is not trustworthy enough.** In 2023, HUD's Office of Policy Development and Research published [*Generative AI: Mining Housing Data With a Higher Powered Shovel*](https://www.huduser.gov/portal/periodicals/cityscape/vol25num3/ch9.pdf) (Dylan J. Hayden, *Cityscape* Vol. 25 No. 3), demonstrating that generative AI could accelerate housing data analysis while flagging the risks of bias and hallucination that demand human supervision. A single LLM will hallucinate, miscategorize, and silently drop fields — and when the entire empirical foundation of a law review article depends on the accuracy of that classification, silent errors are unacceptable.

**The solution was to use three independent LLMs and treat disagreement as a quality signal.** Rather than trusting any single model, the pipeline runs each case through three separate models and uses their agreement (or lack of it) to determine confidence and route difficult cases to stronger adjudicators. This approach applies the logic of inter-rater reliability — the same principle that governs human coding in empirical legal research — to automated classification:

1. **No single point of failure.** Three independent models (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) classify each case separately. When all three disagree, the case is flagged for adjudication rather than silently miscoded.

2. **Disagreement is signal, not noise.** A three-way split on `outcome` or `claim_type` usually means the case is genuinely ambiguous — multi-claim opinions, mixed dispositions, or unusual procedural postures. The pipeline routes these to stronger adjudication models that see all three answers plus the original text.

3. **Cost-tiered escalation.** Most cases resolve at the cheap consensus tier. Only the hard cases escalate. Total pipeline cost for 3,193 cases: ~$160.

4. **Auditable at every stage.** Every record carries resolution metadata: which tier resolved it, which models agreed, what the adjudicator decided and why. The audit database preserves all three model outputs (~91 fields/record) alongside the canonical answer (~27 fields).

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
  census_pums_replication.py          # Full Census PUMS analysis (Python 3)
  regression_analysis.py              # Multivariate logistic regression

pipeline/                             # Classification pipeline documentation
  model_configuration.md              # Model specs, costs, and agreement rates
  consensus_resolution.md             # Tiered consensus algorithm
  per_claim_extraction_schema.json    # Haiku 4.5 per-claim schema
  field_normalization.md              # Free-text normalization rules

analysis/                             # Extended analysis methodology
```

## Quick Start

### Census PUMS Replication (no dependencies)

```bash
python scripts/census_pums_replication.py
```

Queries the Census Bureau Data API directly. No API key required. Reproduces disability prevalence, cost-burden penalties, and GRPIP=101 rates.

### Regression Analysis (requires statsmodels)

```bash
pip install statsmodels numpy
python scripts/regression_analysis.py <unified_dataset.json>
```

## Classification Pipeline

The pipeline processes court opinions through five stages:

1. **FHA Screening** — Gemini 3.1 Flash Lite binary classifier filters non-FHA opinions
2. **Triple-Model Classification** — MiniMax M2.7 + DeepSeek V3.2 + Kimi K2.5 independently produce 28-field structured JSON per case
3. **Tiered Consensus Resolution** — Unanimous → majority vote → Haiku 4.5 adjudication → Sonnet 4.6 adjudication
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
