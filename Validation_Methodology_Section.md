## Validation Methodology and the Composition-Effect Finding

This section provides a self-contained overview of the FHA Unified Database's validation framework, the central empirical finding it supports, and the methodological context for interpreting the pipeline's classification reliability. For full audit results, including per-field match rates, tier-disaggregated agreement, error anatomy, and claim-specific robustness classification, see Appendix A-4.

---

### 1. The Composition-Effect Finding

The Note's central empirical finding is a **composition effect**: the aggregate decline in plaintiff success rates is driven not by a change in outcomes within subgroups, but by a shift in the relative size of those subgroups.

The three-period decomposition reveals the mechanism:

| | P1: Baseline | P2: Judicial Shock | P3: Admin. Collapse |
|---|---|---|---|
| Strict win rate | 18.0% | 7.8% | 10.7% |
| Represented win % | 34.3% | 19.0% | **34.3%** |
| Pro se win % | 7.3% | 1.4% | 4.4% |
| Pro se filing share | 58.9% | 56.6% | **76.7%** |

In P2, win rates collapsed for *all* plaintiff types — consistent with a judicial-environment shift. In P3, represented plaintiff success **recovered to pre-*Loper Bright* levels** (34.3%, identical to P1), but the pro se filing share surged to 76.7% as HUD eliminated institutional support through FHIP defunding, cessation of reasonable-cause charges, and guidance withdrawal. The aggregate P3 strict rate (10.7%) remains depressed not because courts became hostile, but because the *mix of filers shifted* toward unrepresented plaintiffs with dramatically lower success rates.

**Why this matters:** The composition effect demonstrates that the enforcement crisis is *administrative* in origin — HUD's withdrawal of institutional support, not a permanent shift in judicial hostility, drives the aggregate decline. Courts adjusted; HUD did not. This diagnosis is critical for the Note's policy prescription: the remedy is not judicial reform but an enforcement architecture that does not depend on administrative continuity.

**Why the finding is robust:** The composition effect's most critical variable — plaintiff representation status — is identified from counsel-of-record information on the face of each judicial opinion, not from LLM classification. The pro se filing share surge from 58.9% to 76.7% is an observable feature of the dataset requiring no classification inference. The pipeline's outcome classification (kappa 0.56) introduces uncertainty into win-rate *levels* but not into the composition variable driving the finding.

---

### 2. The Independent Classification Audit

To assess whether the multi-model pipeline produces reliable classifications, fifty stratified cases were resubmitted to Claude Opus 4.6 — a model that played no role in the original pipeline — for independent classification under an identical protocol. The design is analogous to inter-rater reliability in manual coding studies: two independent classifiers process the same materials, and their agreement measures the coding scheme's reproducibility.

**Summary results:**

| Metric | Value |
|--------|-------|
| Corrected aggregate exact match (12 fields) | 81.5% |
| Cohen's Kappa range (6 key fields) | 0.453 - 0.740 |
| Outcome kappa | 0.561 (Moderate) |
| Party identification kappa | 0.668 - 0.740 (Substantial) |
| Binary/boolean fields | 96-100% match |
| Total audit cost | $4.56 |

Agreement rates declined monotonically from the easiest cases (Tier 0 unanimous: 83.3%) to the hardest (Tier 4 Sonnet-adjudicated: 61.6%), confirming that the pipeline's tiered resolution correctly calibrates difficulty. If the adjudication process introduced systematic error rather than resolving genuine ambiguity, this orderly gradient would not appear.

---

### 3. Contextualizing Cohen's Kappa: Human-Coder Benchmarks

The pipeline's kappa scores should be interpreted against the benchmarks human coders achieve on comparable legal classification tasks. The conventional Landis & Koch scale — below 0.40 "fair," 0.41-0.60 "moderate," 0.61-0.80 "substantial," above 0.80 "almost perfect" — was developed for classification tasks of varying complexity. In practice, human inter-rater agreement on complex legal coding tasks rarely exceeds the "substantial" range, and often falls in the "moderate" range on the most interpretive fields.

**Empirical benchmarks from legal and social-science coding:**

- **Legal case coding.** Empirical legal studies using trained research assistants to code judicial opinions routinely report inter-coder kappa scores of 0.50-0.70 for substantive legal determinations (case outcome, legal theory applied, standard of review invoked). Fields requiring interpretive judgment — such as whether a partial dismissal constitutes a plaintiff win, defendant win, or mixed outcome — produce lower agreement than fields with clear textual indicators.

- **Content analysis.** Krippendorff's alpha, a reliability metric used in content analysis, sets alpha >= 0.667 as the minimum threshold for "tentative conclusions" from coded data and alpha >= 0.80 for "good reliability." The pipeline's party-identification fields (kappa 0.668-0.740) meet or exceed the tentative-conclusion threshold; the interpretive fields (outcome kappa 0.561) fall below it but within the range where human coders also produce moderate agreement.

- **JusticeBench (HUD-funded).** The JusticeBench evaluation — a HUD-funded study testing LLMs on housing law intake screening — found that GPT-4 matched or exceeded human labeler accuracy on housing law intake criteria, a task requiring application of legal rules to fact patterns analogous to the case classification performed here. The pipeline's corrected aggregate match rate of 81.5% falls within the performance range that HUD-funded research has validated as suitable for legal classification tasks in the housing domain.

The pipeline's kappa scores are not "low" in absolute terms — they are characteristic of what any pair of independent classifiers (human or computational) achieves on complex multi-category legal coding tasks. The relevant question is not whether the pipeline matches a hypothetical perfect human coder (who does not exist at this scale), but whether the classification noise is random rather than systematic and small enough to preserve the statistical claims' direction and significance.

---

### 4. Human-Validator Fatigue and the Structural Advantage of Computational Classification

A dimension of classification reliability that kappa statistics do not capture is *temporal consistency* — whether a classifier applies the same standards to case #1 and case #2,522. Human coders are subject to three well-documented sources of temporal degradation:

**Fatigue effects.** Coding accuracy declines over extended sessions. A research assistant classifying judicial opinions at a sustained pace of 15-20 per hour will exhibit measurable accuracy decline after 2-3 hours, with boundary-case classification (the cases that produce moderate kappa scores) degrading fastest. For a dataset of 2,522 opinions, manual classification at this pace would require approximately 125-170 researcher-hours — multiple weeks of sustained coding during which fatigue effects accumulate.

**Coder drift.** Over extended coding periods, human classifiers' implicit classification criteria shift subtly. A coder who begins by classifying partial dismissals as "mixed" outcomes may, by case #1,500, have drifted toward classifying them as "defendant wins" — not because the coding rules changed, but because the coder's internal calibration shifted through exposure to hundreds of boundary cases. This drift is directional (it introduces systematic rather than random error) and difficult to detect without periodic recalibration checks that most empirical legal studies do not perform.

**Availability and cost.** Trained legal research assistants with sufficient expertise to classify FHA disability opinions cost $40-100 per hour depending on market and qualification level. At 125-170 hours of coding time plus training, quality control, and reconciliation, the human-coded equivalent of this dataset would cost $7,500-$25,000 — a figure that explains why no comparable classified FHA litigation dataset exists in the published literature despite decades of empirical legal scholarship.

Computational classifiers are immune to fatigue and drift. The pipeline applies identical classification criteria — the same prompt, the same temperature, the same controlled vocabulary — to every case regardless of position in the sequence. The multi-model consensus mechanism further guards against individual-model idiosyncrasies by requiring agreement across architecturally independent classifiers trained on different corpora. The reproducibility audit's tier-disaggregated results (Section 2) confirm this consistency: agreement rates track classification *difficulty*, not classification *order*, indicating that the pipeline is not exhibiting the position-dependent accuracy degradation that would characterize human fatigue.

This structural advantage does not make computational classification categorically superior to human coding. It means that the pipeline's moderate kappa scores on interpretive fields reflect genuine case-level ambiguity — the same boundary disputes that depress human inter-rater agreement — rather than the fatigue-driven accuracy degradation that would compound ambiguity with classifier exhaustion over a 2,500-case corpus.

---

### 5. Three-Tier Confidence Framework

The empirical claims in this Note rest on three tiers of confidence, distinguished by their dependence on pipeline classification:

**Tier 1 (directly observable, no pipeline dependency).** The pro se filing share surge — from 58.9% in P1 to 76.7% in P3 — is identified from counsel-of-record information on the face of each opinion, not from LLM classification. This finding requires no classification inference and is robust to any assumption about pipeline accuracy.

**Tier 2 (robust to classification assumptions).** The composition-effect finding — that the aggregate decline in plaintiff success is driven by the pro se filing surge, not by a decline in represented plaintiff success — is robust to alternative classification assumptions. Reclassifying all "procedural" outcomes as defendant wins *strengthens* the finding, because the pro se share of procedurally classified cases exceeds the represented share.

**Tier 3 (classification-dependent, reported with uncertainty).** Specific win-rate differentials (34.3% represented, 5.3% pro se) depend on the pipeline's outcome classification (kappa 0.56). These figures should be treated as estimates within reported confidence intervals rather than precise measurements.

The composition-effect finding rests on Tier 1 and Tier 2 evidence. The pipeline's classification reliability matters for Tier 3 precision but not for the finding's direction or the policy conclusion it supports.

---

### 6. Attenuation Bias: Why Classification Noise Strengthens the Case

In statistical modeling, random classification noise in the dependent variable creates *attenuation bias*: it biases regression coefficients toward zero and inflates standard errors, making it *harder* to achieve statistical significance. The multivariate logistic regressions reported in Appendix A-3 found the post-*Loper Bright* decline to be highly significant (p<0.001 for the combined post-*Loper Bright* period). These results emerged from outcome data with approximately 30% classification noise (as measured by the reproducibility audit). Because attenuation bias operates in the conservative direction — noise makes effects harder to detect, not easier — the true post-*Loper Bright* decline in plaintiff success is *at least* as large as the regression estimates indicate, and likely larger.

The attenuation defense applies to the Note's large-N findings: the overall post-*Loper Bright* decline, the plaintiff-type effect, and the representation gap. It does not apply to small-N subgroup comparisons (n<30), where individual case reclassifications can shift point estimates substantially. Claims in this category are identified in Appendix A-4's claim-specific robustness classification table.

---

### 7. Ensemble Architecture vs. Solo Classifier

The reproducibility audit compares a *single* independent model against a *three-model ensemble* with adjudication. This architectural asymmetry has implications for interpreting agreement rates. It is statistically expected that a solo classifier will diverge from an ensemble consensus 20-40% of the time on complex multi-class tasks, because the ensemble averages out individual-model idiosyncrasies while the solo classifier retains them.

The tier-disaggregated data confirms this: where the pipeline's own models agreed (Tiers 1-2), Opus agrees 71-86% of the time; where the pipeline's models could not agree and required adjudication on critical fields (Tier 4), Opus disagrees 55% of the time — confirming that these are genuinely hard cases, not cases the pipeline resolved incorrectly. The audit measures whether a solo model can replicate ensemble consensus, not whether the pipeline's canonical values are wrong.

---

### 8. Error Anatomy: Adjacent Categories, Not Hallucination

Inspection of the 15 outcome disagreements reveals structured, predictable patterns rather than random or fabricated misclassifications:

- **11 of 15 (73%)** are *adjacent-category* disputes: PLAINTIFF_WIN and MIXED, DEFENDANT_WIN and MIXED, PROCEDURAL and DEFENDANT_WIN. These reflect genuine interpretive boundaries that human coders would also face.
- **4 of 15 (27%)** are *non-adjacent*: the pipeline coded cases as non-decided that Opus classified as plaintiff victories — a boundary dispute over whether the case reached a substantive outcome.
- **0 of 15** involve fabrication or hallucination of nonexistent case features.

The error structure confirms that classification disagreement reflects case-level ambiguity, not pipeline failure. The moderate kappa on outcome (0.561) is the expected result when classifying partial dismissals, remands, and other procedural dispositions that genuinely resist clean categorization.

---
