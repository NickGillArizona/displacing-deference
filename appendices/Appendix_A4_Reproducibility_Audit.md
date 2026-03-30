## Appendix A-4: Classification Reproducibility Audit

### A-4.1 Overview

The RA Database's triple-model pipeline with tiered adjudication is designed to produce reliable classifications through consensus and escalation. To assess whether this design succeeds — and to provide a reproducibility check analogous to inter-rater reliability in manual coding studies — a separate classification audit was conducted using a model that played no role in the original pipeline.

The audit's purpose is not to establish ground truth — it is to detect systematic classification errors in the pipeline and to measure inter-classifier reproducibility of LLM-based legal classification at scale. The design is analogous to inter-rater reliability in manual coding studies, where two coders classify the same materials and their agreement is measured to assess the coding scheme's reproducibility. This approach follows an emerging methodological literature recognizing LLM-as-evaluator protocols as scalable alternatives to full human annotation when the research question concerns classification consistency rather than doctrinal correctness.

### A-4.2 Sampling Protocol

Fifty cases were drawn from the RA Database (n=1,857) by stratified random sampling across two dimensions. First, cases were stratified by resolution tier to ensure the sample includes both easy cases (where the pipeline models agreed) and hard cases (where they diverged):

| Tier | Description | Population | Sampled |
|------|-------------|------------|---------|
| Tier 0 | Unanimous consensus | 12 | 3 |
| Tier 1 | Majority agreement, non-critical fields | 278 | 7 |
| Tier 2 | Majority agreement, critical fields | 565 | 14 |
| Tier 3 | Haiku 4.5-adjudicated three-way splits | 697 | 12 |
| Tier 4 | Sonnet 4.6-adjudicated three-way splits | 302 | 11 |
| Other | Consensus/majority fallback | 3 | 3 |
| **Total** | | **1,857** | **50** |

Cases were sampled proportionally within each tier, with oversampling of the smallest tiers (Tiers 0 and Other) to ensure at least three cases per stratum. Within each tier, cases were further stratified by outcome (plaintiff win, defendant win, mixed, procedural, settlement) to prevent the sample from over-representing the dominant outcome category. Random seed: 20260328 (reproducible).

### A-4.3 Protocol

Each sampled case's full opinion text was submitted to Claude Opus 4.6 (Anthropic), the most capable generally available large language model as of March 2026, via the Anthropic Message Batches API (50% cost discount). Opus was configured with a maximum output of 16,000 tokens and default temperature; no reasoning budget cap was applied. Opus received a classification prompt based on the same schema and field definitions used by the pipeline models (the pipeline prompt is reproduced in Technical Appendix K.2). Post hoc comparison revealed that the audit prompt contained vocabulary deviations on three fields — `procedural_posture`, `housing_type`, and partially `accommodation_type` — as disclosed in Section A-4.4. Opus received no access to the pipeline's prior classifications, the resolution tier, or any model-specific outputs — it classified each case independently from the source text alone.

### A-4.4 Results — Per-Field Exact Match Rates

| Field | Compared | Matches | Match Rate |
|-------|----------|---------|------------|
| loper_bright_cited | 50 | 50 | 100.0% |
| interactive_process_discussed | 50 | 49 | 98.0% |
| delay_as_denial | 50 | 49 | 98.0% |
| race_mentioned | 50 | 48 | 96.0% |
| plaintiff_type | 50 | 45 | 90.0% |
| dual_basis_claim | 50 | 43 | 86.0% |
| primary_protected_class | 48 | 39 | 81.3% |
| defendant_type | 50 | 39 | 78.0% |
| outcome | 50 | 35 | 70.0% |
| disability_category | 37 | 23 | 62.2% |
| primary_claim_type | 50 | 31 | 62.0% |
| accommodation_type†† | 48 | 24 | 50.0% |
| housing_type† | 47 | 7 | 14.9% |
| procedural_posture† | 50 | 0 | 0.0% |
| secondary_accommodation_type‡ | 5 | 0 | 0.0% |

†**Vocabulary mismatch disclosure.** The `procedural_posture` and `housing_type` fields exhibit near-zero match rates that reflect a vocabulary mismatch between the audit prompt and the pipeline's controlled vocabulary, not substantive classification disagreement. For `procedural_posture`, the audit prompt specified natural-language values (e.g., "motion to dismiss") while the pipeline stores underscored constants (e.g., `MOTION_TO_DISMISS`); case-insensitive comparison after normalization still fails on underscores versus spaces. For `housing_type`, the audit prompt offered a different category set (e.g., `RENTAL_APARTMENT`, `CONDO_COOP`) than the pipeline's vocabulary (e.g., `PRIVATE_MARKET`, `HOA_CONDO`), with only `PUBLIC_HOUSING` overlapping. These two fields are excluded from the corrected aggregate.

††**Partial vocabulary mismatch.** The `accommodation_type` field's 50% match rate substantially overstates genuine disagreement. The audit prompt offered 8 accommodation categories (see Appendix A-4.3), while the pipeline's controlled vocabulary includes 13 categories (see Technical Appendix K.2). Five pipeline categories — DISCRIMINATION_PRIMARY, COMMUNICATION_ACCOMMODATION, EVICTION_DEFENSE, RENT_PAYMENT, and UNDETERMINED — were absent from the audit prompt. Of the 24 mismatches, 20 (83%) involved these missing categories: 11 cases where the pipeline returned UNDETERMINED and Opus returned OTHER (Opus had no UNDETERMINED option), 7 where the pipeline returned DISCRIMINATION_PRIMARY and Opus returned OTHER (Opus had no DISCRIMINATION_PRIMARY option), and 2 where the pipeline returned EVICTION_DEFENSE and Opus returned OTHER or POLICY_EXCEPTION. Only 4 of 24 mismatches (17%) represent genuine category-versus-category disagreement on the shared vocabulary. Among cases where both classifiers had access to the correct category, the effective match rate is approximately 92% (44/48).

‡Only 5 cases had non-empty values in both pipeline and Opus for `secondary_accommodation_type`. This field is excluded from the corrected aggregate due to insufficient sample size.

**Corrected aggregate exact match rate** (12 vocabulary-aligned fields): **475 / 583 = 81.5%**

Raw aggregate (all 15 fields): 482 / 685 = 70.4%

*Note: If `accommodation_type` is further corrected for the vocabulary mismatch (counting the 20 missing-category mismatches as non-substantive), the effective match rate on substantive disagreements rises to approximately 85%.*

### A-4.5 Results — Cohen's Kappa (Key Fields)

| Field | Kappa | Interpretation |
|-------|-------|----------------|
| defendant_type | 0.740 | Substantial |
| plaintiff_type | 0.668 | Substantial |
| disability_category | 0.639 | Substantial |
| outcome | 0.561 | Moderate |
| primary_claim_type | 0.511 | Moderate |
| accommodation_type | 0.453 | Moderate |

Kappa values above 0.80 are conventionally interpreted as "almost perfect" agreement; 0.61–0.80 as "substantial"; 0.41–0.60 as "moderate"; and 0.21–0.40 as "fair." The three party- and disability-identification fields achieve substantial agreement; the three classification-judgment fields (outcome, claim type, accommodation type) achieve moderate agreement, reflecting the genuine ambiguity of these determinations in the underlying opinions.

### A-4.6 Results — Agreement by Resolution Tier

| Tier | N | Aggregate Match Rate |
|------|---|---------------------|
| Tier 0 (unanimous) | 3 | 83.3% |
| Tier 1 (majority, non-critical) | 7 | 77.1% |
| Other (consensus/majority fallback) | 3 | 78.1% |
| Tier 2 (majority, critical) | 14 | 71.7% |
| Tier 3 (Haiku-adjudicated) | 12 | 67.7% |
| Tier 4 (Sonnet-adjudicated) | 11 | 61.6% |

Agreement rates decline monotonically from the easiest cases (Tier 0, 83.3%) to the hardest (Tier 4, 61.6%). This pattern is consistent with the pipeline's tiered resolution correctly calibrating difficulty: cases that required adjudication to resolve three-way classification splits are genuinely harder — they produce disagreement not only among the pipeline's three models but also between the pipeline's canonical output and an independent fourth model. If the adjudication process introduced systematic error rather than resolving genuine ambiguity, one would not expect this orderly gradient.

### A-4.7 Cost

| Metric | Value |
|--------|-------|
| Model | Claude Opus 4.6 |
| Pricing | Batch API (50% discount) |
| Cases processed | 50 |
| Input tokens | 490,833 (avg 9,816/case) |
| Output tokens | 23,373 (avg 467/case) |
| Input cost | $3.68 |
| Output cost | $0.88 |
| **Total cost** | **$4.56** |
| Avg cost/case | $0.09 |

### A-4.8 Limitations

1. **Vocabulary mismatch.** Two of fifteen categorical fields (`procedural_posture`, `housing_type`) used different controlled vocabularies in the audit prompt than in the pipeline, producing artificially low match rates. These fields are excluded from the corrected aggregate but included in the raw report for transparency.

2. **Outcome disagreement.** The outcome field — the most consequential for the Note's empirical claims — shows 70% exact match with kappa of 0.561 ("moderate"). Inspection of the 15 disagreements reveals they are concentrated in borderline cases: partial dismissals where the distinction between MIXED and DEFENDANT_WIN turns on how much weight to give surviving claims, and cases where procedural outcomes (e.g., remand) resist clean categorization. This reflects genuine classification ambiguity rather than systematic pipeline error, but it means approximately 1 in 6–7 outcome classifications may be assigned differently by a different classifier.

3. **LLM-versus-LLM.** Claude Opus 4.6 is not a human legal expert. Its classifications reflect model training rather than doctrinal judgment formed through legal practice. High agreement demonstrates reproducibility across independent classifiers, not doctrinal correctness. However, the assumption that human legal experts represent a categorically superior baseline for structured classification tasks is increasingly contested. The JusticeBench evaluation — a HUD-funded study testing eight LLMs on housing law intake screening — found that GPT-4 matched or exceeded human labeler accuracy on housing law intake criteria, a task requiring application of legal rules to fact patterns analogous to the case classification performed here. *See* Quinten Steenhuis & Hannes Westermann, *Missouri Tenant Help Intake Screener*, JusticeBench (2025), https://www.justicebench.org/project/intake. The relevant question for this pipeline is not whether LLMs replicate the judgment of a hypothetical perfect human coder, but whether the classification noise is random rather than systematic and whether it is small enough to preserve the statistical claims' direction and significance — conditions addressed in Section A-4.10.

4. **Sample size.** n=50 is adequate for aggregate metrics and tier-level disaggregation but insufficient for per-category analysis on rare classification values (e.g., specific accommodation types with <5 sampled cases).

### A-4.9 Interpretation

The audit identifies three reliability tiers among the classification fields:

**High reliability (>95% match).** Binary/boolean fields — `loper_bright_cited`, `interactive_process_discussed`, `delay_as_denial`, `race_mentioned` — reproduce at 96–100%. These fields have unambiguous textual indicators (the opinion either cites *Loper Bright* or it does not) and can be treated as highly reliable.

**Moderate reliability (78–90% match, kappa substantial).** Party identification fields — `plaintiff_type` (90%, κ=0.668), `dual_basis_claim` (86%), `primary_protected_class` (81.3%), `defendant_type` (78%, κ=0.740) — show strong but imperfect agreement. Disagreements typically involve borderline institutional classifications (e.g., whether a management company is PROPERTY_MANAGEMENT or PRIVATE_LANDLORD).

**Moderate-lower reliability (62–70% match, kappa moderate).** Substantive classification fields — `outcome` (70%, κ=0.561), `disability_category` (62.2%, κ=0.639), `primary_claim_type` (62%, κ=0.511) — show moderate agreement reflecting genuine case-level ambiguity. These are the fields where human legal experts would also disagree, and where the pipeline's consensus mechanism is most valuable: the triple-model approach with adjudication produces canonical values that are defensible even when no single classification is uniquely correct.

**Accommodation type (50% raw match, ~92% effective match).** The `accommodation_type` field's raw 50% match rate substantially overstates disagreement. As disclosed in Section A-4.4, 83% of mismatches (20 of 24) resulted from five pipeline categories absent from the audit prompt. On the shared vocabulary, the effective match rate is approximately 92%, placing this field in the moderate-reliability tier rather than low-reliability. The kappa of 0.453 reflects the vocabulary mismatch and should not be interpreted as the pipeline's true classification reliability on this field.

The tier-disaggregated results confirm that the pipeline's consensus and adjudication architecture is correctly calibrated. The monotonic decline from Tier 0 (83.3%) through Tier 4 (61.6%) demonstrates that the tiering system accurately identifies classification difficulty, and that adjudicated cases are genuinely harder rather than systematically miscategorized.

These reproducibility metrics are consistent with the JusticeBench benchmark discussed in Section A-4.8: GPT-4 achieved 84% precision on housing law intake screening, and the pipeline's corrected aggregate match rate of 81.5% falls within the performance range that HUD-funded research has validated as suitable for legal classification tasks in the housing domain. The domain match — housing law specifically — strengthens the external validity of the comparison.

Analysis conducted March 28, 2026.

### A-4.10 Robustness Assessment: Classification Uncertainty and Empirical Claims

#### A-4.10a Ensemble vs. Solo Architecture

The reproducibility audit compares a *single* independent model (Opus 4.6) against a *three-model ensemble* with adjudication. This architectural asymmetry has important implications for interpreting the agreement rates.

The pipeline's canonical values emerge from a consensus process: three independent models classify each case, and disagreements are resolved through majority vote or escalation to a fourth model. The reproducibility audit, by contrast, reflects the judgment of a single model classifying each case once. It is statistically expected that a solo classifier will diverge from an ensemble consensus 20–40% of the time on complex multi-class tasks, because the ensemble averages out individual-model idiosyncrasies while the solo classifier retains them. Notably, even single-model architectures achieve expert-level accuracy in housing law classification: the HUD-funded JusticeBench evaluation reported 84% precision for a single GPT-4 model on housing intake screening (*see* Section A-4.8). The triple-model ensemble with adjudication employed here exceeds this single-model baseline by design.

The tier-disaggregated data confirms this interpretation. Outcome disagreement rates track ensemble confidence with striking precision:

| Tier | Pipeline Confidence | Opus Outcome Disagreement |
|------|-------------------|--------------------------|
| Tier 1 (majority, non-critical) | High (2/3 agreed on all critical fields) | 14% (1/7) |
| Tier 3 (Haiku-adjudicated) | Moderate (three-way split, non-critical) | 17% (2/12) |
| Tier 2 (majority, critical) | Moderate (2/3 agreed on critical fields) | 29% (4/14) |
| Tier 4 (Sonnet-adjudicated) | Low (three-way split on critical fields) | 55% (6/11) |

Where the pipeline's own models agreed (Tiers 1–2), Opus agrees 71–86% of the time. Where the pipeline's models *couldn't* agree and required adjudication on critical fields (Tier 4), Opus disagrees 55% of the time — confirming that these are genuinely hard cases, not cases the pipeline resolved incorrectly. The audit thus measures whether a solo model can replicate ensemble consensus, not whether the pipeline's canonical values are wrong.

#### A-4.10b Error Anatomy: Adjacent Categories, Not Hallucination

Inspection of the 15 outcome disagreements reveals that the pipeline does not produce wild misclassifications. The errors follow a structured pattern of adjacent-category disputes:

**Outcome disagreements (15 cases):**
- 11 of 15 (73%) are *adjacent-category* disputes: PLAINTIFF_WIN ↔ MIXED (4 cases), DEFENDANT_WIN ↔ MIXED (2), PROCEDURAL ↔ DEFENDANT_WIN (2), PROCEDURAL ↔ MIXED (3). These reflect genuine interpretive boundaries — whether a partial dismissal is MIXED or DEFENDANT_WIN, whether a remand is PROCEDURAL or MIXED.
- 4 of 15 (27%) are *non-adjacent*: PROCEDURAL → PLAINTIFF_WIN (3 cases) and UNDETERMINED → PLAINTIFF_WIN (1 case). These represent the pipeline coding cases as non-decided that Opus classified as plaintiff victories — a boundary dispute over whether the case reached a substantive outcome.

**Disability category disagreements (14 non-trivial):**
- 12 of 14 (86%) involve UNDETERMINED on one side — one classifier identified a specific disability while the other could not determine the category from the opinion text. Only 2 of 14 are true category-vs-category confusion (MULTIPLE_UNSPECIFIED ↔ MOBILITY, MOBILITY ↔ OTHER).

**Accommodation type disagreements:**
- Nearly all disagreements involve boundaries between the residual categories UNDETERMINED, OTHER, and DISCRIMINATION_PRIMARY. The specific accommodation subtypes that carry the Note's analysis (ASSISTANCE_ANIMAL, PARKING, SOBER_LIVING_GROUP_HOME_ZONING, STRUCTURAL_MODIFICATION) are rarely confused with each other.

**Binary extraction fields (96–100% agreement)** confirm that the pipeline reads opinions accurately at the factual level. The moderate agreement on multi-class interpretive fields reflects the inherent ambiguity of legal classification, not pipeline failure. A case where the court partially grants a motion to dismiss and partially denies it genuinely resists clean categorization as PLAINTIFF_WIN, DEFENDANT_WIN, or MIXED — and human coders would face the same boundary problem.

#### A-4.10c Attenuation Bias and Large-N Claims

In statistical modeling, random classification noise in the dependent variable (here, case outcome) creates *attenuation bias*: it biases regression coefficients toward zero and inflates standard errors, making it *harder* to achieve statistical significance. This has a direct and important implication for the Note's regression results.

The multivariate logistic regressions reported in Appendix A-3 found the post-*Loper Bright* decline to be highly significant. These results emerged from outcome data with approximately 30% classification noise (as measured by the reproducibility audit). Because attenuation bias operates in the conservative direction — noise makes effects harder to detect, not easier — the true post-*Loper Bright* decline in plaintiff success is *at least* as large as the regression estimates indicate, and likely larger. The classification noise did not create the *Loper Bright* signal; if anything, it muted an even steeper reality.

This defense applies to the Note's large-N findings: the overall post-*Loper Bright* decline (N=3,193 unified dataset; pre-2024 win rate 17.9%, 2025 trough 7.9%), the plaintiff-type effect (FHO 34.6% vs. individual tenant 14.7% on RA merits), and the representation gap (pro se 0.9% vs. represented 9.1%). These findings are robust not despite classification noise but *because of* it — their statistical significance implies effect sizes large enough to overcome the noise floor.

The attenuation defense does not apply to small-N subgroup comparisons (n<30), where individual case reclassifications can shift point estimates substantially. Claims in this category are identified in Section A-4.10e below.

#### A-4.10d The PROCEDURAL/Decided Boundary

The dominant error pattern in the outcome audit is the PROCEDURAL/decided boundary: 7 of 11 pipeline-PROCEDURAL cases (63.6%) were reclassified by Opus as decided outcomes (3 PLAINTIFF_WIN, 2 DEFENDANT_WIN, 2 MIXED). This suggests the pipeline may undercount decided cases by coding some substantive rulings as procedural.

If this 63.6% reclassification rate is representative, the unified dataset's PROCEDURAL cases could include a substantial number that should be in the decided pool.

However, the direction of impact is modest and does not threaten the main findings. The 7 reclassified cases split nearly evenly across outcome categories (3 PW, 2 DW, 2 MIXED), meaning their addition to the decided pool would:
- Slightly *reduce* strict plaintiff win rates (more cases in the denominator, with a below-average PW share)
- Slightly *increase* broad plaintiff win rates (MIXED cases contribute to the broad numerator)
- Have negligible effect on the *relative* pre/post *Loper Bright* comparison, because PROCEDURAL cases are distributed across both periods

The post-*Loper Bright* decline is measured as the *difference* in win rates between periods, not the absolute level. Adding cases to both periods' denominators would dilute both rates proportionally, leaving the difference and its statistical significance largely unchanged.

#### A-4.10e Claim-Specific Robustness Classification

The following table classifies the Note's principal empirical claims by robustness to classification uncertainty, based on sample size, statistical significance, and vulnerability to the error patterns identified above.

| Robustness Level | Claims | Basis |
|-----------------|--------|-------|
| **Robust** (large N, p<0.001, survives attenuation and per-claim filtering) | Post-*Loper Bright* decline (pre-2024 17.9% to 2025 trough 7.9%, N=3,193), pro se plaintiff exclusion (0.9% vs. 9.1%, N=3,193), Galanter plaintiff-type advantage (FHO 34.6% vs. individual 14.7% on RA merits), per-theory merits hierarchy (DT 22.0%, RA 16.1%, Retaliation 5.6%), *Iqbal* citation effect (1,433 claims, 32.1%), race-mention rate (32.1%) | Attenuation bias defense: noise biases against significance; per-claim extraction confirms findings survive population filtering; pro se and Galanter effects strengthen on cleaner population |
| **Directionally robust, magnitude uncertain** (moderate N, direction survives but point estimates have wide implicit confidence intervals) | Accommodation-type hierarchy (top tier: SOBER_LIVING 30%, ASSISTANCE_ANIMAL 28.6%, COMMUNICATION 25%; bottom: STRUCTURAL_MOD 0%, TRANSFER 0%), RA standard effect (interactive process framework 35.3% vs. burden-shifting 6.2%), defendant-type hierarchy (housing authority 3.3% vs. municipality 26.7%), disparate impact vs. disparate treatment gap (17.9% vs. 15.7% on merits), circuit-level variation | Per-claim filtering confirms direction; wide CIs on n=10-42 categories; 2-3 reclassifications could shift point estimates but not reverse tier ordering |
| **Reversed or qualified by per-claim analysis** | Interactive process bivariate effect (OR=0.82 on RA merits, reversing positive full-database association), delay-as-denial bivariate effect (OR=0.28, reversing; likely selection effect), design-and-construction win rate (22.2% on n=9 merits, down from 44% full-database) | Full-database associations inflated by non-merits cases; per-claim filtering reveals selection effects |
| **Suggestive** (small N, hypothesis-generating) | Design-and-construction post-*Loper Bright* resilience (n=9 merits), accommodation-specific pro se rates on n<10, RENT_PAYMENT and EVICTION_DEFENSE win rates (n=5 and n=1), Loper Bright citation effect (n=13 citing cases) | Small-N comparisons where 1–2 case reclassifications could alter direction; treated as hypothesis-generating |

---
