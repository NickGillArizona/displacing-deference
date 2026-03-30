# Model Configuration and Cost Summary

## Classification Pipeline Models

### Stage 1: FHA Relevance Screening

| Parameter | Value |
|-----------|-------|
| Model | Google Gemini 3.1 Flash Lite |
| Temperature | 0.0 |
| Reasoning | Disabled |
| Task | Binary YES/NO FHA relevance screening |
| Estimated cost | < $5 total |

### Stage 2: Triple-Model Independent Classification (via OpenRouter API)

| Model | Provider | Role | Temperature | Reasoning Budget | Max Output | Output Cost/M |
|-------|----------|------|-------------|-----------------|------------|---------------|
| MiniMax M2.7 | MiniMax | Primary extraction | 0.2 | 2,048 tokens | 8,192 | $1.20 |
| DeepSeek V3.2 | DeepSeek | Consensus verification | 0.2 | 16,384 tokens | 8,192 | $0.38 |
| Kimi K2.5 | Moonshot AI | Consensus verification | 0.2 | 1,024 tokens | 8,192 | $2.20 |

**Input truncation:** Case texts exceeding 50,000 characters are truncated, preserving the first 25,000 and last 25,000 characters.

**Reasoning budget rationale:** Calibrated primarily by cost. DeepSeek received the largest budget because its output pricing ($0.38/M) made extended reasoning inexpensive. Kimi received a smaller budget despite higher cost because its verification role did not require extended deliberation.

### Stage 3: Tiered Consensus Adjudication

| Model | Stage | Task | Configuration |
|-------|-------|------|---------------|
| Claude Haiku 4.5 | Tier 3 | Non-critical field 3-way splits | Batch API (50% discount), default settings |
| Claude Sonnet 4.6 | Tier 4 | Critical field 3-way splits | Batch API (50% discount), 2,000 thinking tokens, 4,000 max output |

### Stage 4: Per-Claim Structured Extraction

| Parameter | Value |
|-----------|-------|
| Model | Claude Haiku 4.5 (Anthropic Batch API) |
| Temperature | 0.1 |
| Records processed | 3,193 cases |
| Output | 6,718 claims (4,464 FHA + 2,254 non-FHA) |
| Cost | ~$17.58 (26.4M input + 1.7M output tokens) |

### Stage 5: Reproducibility Audit

| Parameter | Value |
|-----------|-------|
| Model | Claude Opus 4.6 (Anthropic Batch API) |
| Temperature | Default |
| Max output | 16,000 tokens |
| Cases audited | 50 (stratified random sample) |
| Cost | $4.56 (490,833 input + 23,373 output tokens) |

---

## Cost Summary

### OpenRouter API Costs (extracted from provider activity export, March 28, 2026)

| Component | Cost |
|-----------|------|
| MiniMax M2.7 classification | $14.85 |
| DeepSeek V3.2 classification | $31.33 |
| Kimi K2.5 classification | $39.41 |
| GLM-5 abandoned evaluation (sunk cost, not used) | $49.32 |
| **OpenRouter subtotal** | **$134.90** |

*12,290 generation records total, including the abandoned GLM-5 run.*

### Anthropic Batch API Costs

| Component | Cost |
|-----------|------|
| Haiku 4.5 per-claim extraction | ~$17.58 |
| Opus 4.6 reproducibility audit | $4.56 |
| Haiku 4.5 Tier 3 adjudication | Available upon request |
| Sonnet 4.6 Tier 4 adjudication | Available upon request |

### Other

| Component | Cost |
|-----------|------|
| Gemini 3.1 Flash Lite screening | < $5 (estimated) |

---

## Tiered Resolution Distribution

### RA Database (n=1,857)

| Tier | Description | Records | % |
|------|-------------|---------|---|
| 0 | Unanimous consensus | 12 | 0.6% |
| 1 | Majority, non-critical fields | 278 | 15.0% |
| 2 | Majority, critical fields | 565 | 30.4% |
| 3 | Haiku 4.5 adjudicated | 697 | 37.5% |
| 4 | Sonnet 4.6 adjudicated | 302 | 16.3% |
| Other | Fallback | 3 | 0.2% |

### 2015 FHA Database (n=1,496)

| Tier | Description | Records | % |
|------|-------------|---------|---|
| 0 | Unanimous consensus | 48 | 3.2% |
| 1 | Majority, non-critical | 271 | 18.1% |
| 2 | Majority, critical | 435 | 29.1% |
| 3 | MiniMax tiebreaker, non-critical | 171 | 11.4% |
| 4 | MiniMax tiebreaker, critical | 571 | 38.2% |

---

## Inter-Model Agreement Rates (RA Database, pre-adjudication)

| Field | Unanimous (3/3) | Majority (2/3) | No Majority |
|-------|-----------------|----------------|-------------|
| Court | 96.9% | 2.9% | 0.2% |
| Year | 98.7% | 1.2% | 0.2% |
| Outcome | 69.1% | 28.0% | 2.9% |
| Primary Claim Type | 62.6% | 32.2% | 5.2% |
| Claim Types | 44.2% | 43.4% | 12.4% |
| Accommodation Type | 34.7% | 45.8% | 19.5% |
| Disability Category | 47.9% | 47.4% | 4.7% |
| Plaintiff Type | 87.3% | 10.8% | 1.9% |
| Defendant Type | 57.6% | 34.8% | 7.6% |
| Procedural Posture | 69.2% | 28.8% | 2.0% |
| Housing Type | 70.9% | 26.8% | 2.3% |

---

## Reproducibility Audit Results (Opus 4.6 vs. Pipeline, n=50)

| Field | Match Rate | Cohen's Kappa |
|-------|------------|---------------|
| loper_bright_cited | 100.0% | — |
| interactive_process_discussed | 98.0% | — |
| delay_as_denial | 98.0% | — |
| race_mentioned | 96.0% | — |
| plaintiff_type | 90.0% | 0.668 (Substantial) |
| defendant_type | 78.0% | 0.740 (Substantial) |
| outcome | 70.0% | 0.561 (Moderate) |
| disability_category | 62.2% | 0.639 (Substantial) |
| primary_claim_type | 62.0% | 0.511 (Moderate) |
| accommodation_type | 50.0%* | 0.453 (Moderate) |

*Accommodation type: 83% of mismatches due to vocabulary mismatch (5 pipeline categories absent from audit prompt). Effective match rate on shared vocabulary: ~92%.

**Corrected aggregate (12 vocabulary-aligned fields): 81.5%**
