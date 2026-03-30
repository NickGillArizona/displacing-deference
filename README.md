# Displacing Deference: Data and Doctrine for a Disability-Centered AFFH

**Nick Gill** | Arizona State University Sandra Day O'Connor College of Law

---

## Why This Exists

Disability is the dominant axis of federal fair housing enforcement — 54.6% of all complaints, 38.1% of federal litigation — yet no large-scale empirical dataset of disability accommodation case outcomes exists. Researchers who want to study how courts actually decide reasonable-accommodation claims under 42 U.S.C. § 3604(f)(3) must read thousands of opinions by hand.

In 2023, HUD's Office of Policy Development and Research published [*Generative AI: Mining Housing Data With a Higher Powered Shovel*](https://www.huduser.gov/portal/periodicals/cityscape/vol25num3/ch9.pdf) (Dylan J. Hayden, *Cityscape* Vol. 25 No. 3), demonstrating that generative AI could accelerate housing data analysis — producing in a single day what would otherwise take a week with traditional tools, while flagging the risks of bias and hallucination that demand human supervision.

This repository takes HUD's insight and applies it to a harder problem: **structured legal classification of court opinions**, where accuracy matters more than speed and a single model's errors can propagate silently through an entire dataset.

### Why Three Models Instead of One

A single LLM classifying legal opinions will hallucinate, miscategorize, and silently drop fields — exactly the risks Hayden's HUD article identified. The solution is not to avoid AI but to architect around its failure modes:

1. **No single point of failure.** Three independent models (MiniMax M2.7, DeepSeek V3.2, Kimi K2.5) classify each case separately. When two or three agree, confidence is high. When all three disagree, the case is flagged for adjudication rather than silently miscoded.

2. **Disagreement is signal, not noise.** A three-way split on `outcome` or `claim_type` usually means the case is genuinely ambiguous — multi-claim opinions, mixed dispositions, or unusual procedural postures. The pipeline routes these to stronger models (Haiku 4.5 or Sonnet 4.6) that see all three answers plus the original text.

3. **Cost-tiered escalation.** Most cases resolve at the cheap consensus tier (~$0.01/case). Only the hard cases escalate to expensive adjudication models. Total pipeline cost for 3,193 cases: ~$160. A single-model approach using a frontier model would cost 5-10x more with no disagreement signal.

4. **Auditable at every stage.** Every record carries resolution metadata: which tier resolved it, which models agreed, what the adjudicator decided and why. The audit database preserves all three model outputs (~91 fields/record) alongside the canonical answer (~27 fields).

The result: a dataset of 3,193 cases decomposed into 6,718 individual claims, with inter-model agreement rates, Cohen's kappa scores, and a 50-case reproducibility audit against Claude Opus 4.6.

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

## Data Sources

| Source | Access |
|--------|--------|
| CourtListener REST API v4 | https://www.courtlistener.com/api/rest/v4/ |
| ACS 2020-2024 5-Year PUMS | https://api.census.gov/data/2024/acs/acs5/pums |
| OpenRouter API | https://openrouter.ai/ |
| Anthropic Message Batches API | https://docs.anthropic.com/ |

## Classification Pipeline

The pipeline processes court opinions through five stages:

1. **FHA Screening** — Gemini 3.1 Flash Lite binary classifier filters non-FHA opinions
2. **Triple-Model Classification** — MiniMax M2.7 + DeepSeek V3.2 + Kimi K2.5 independently produce 28-field structured JSON per case
3. **Tiered Consensus Resolution** — Unanimous → majority vote → Haiku 4.5 adjudication → Sonnet 4.6 adjudication
4. **Per-Claim Extraction** — Haiku 4.5 decomposes multi-claim cases into individual legal claims
5. **Reproducibility Audit** — Opus 4.6 re-classifies a stratified sample for inter-rater reliability

See [`pipeline/`](pipeline/) for full documentation including model costs, agreement rates, and resolution tier distributions.

## Source Code

The Java and Python source code for the download pipeline, classification clients, and evaluation framework is maintained in the companion repository:

**[MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work)**

## Dataset

The unified dataset (N=3,193 cases, 6,718 claims) and full audit trail are available upon request.

## License

This replication package is provided for academic use. The underlying court opinions are public domain.
