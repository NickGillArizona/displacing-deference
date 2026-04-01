## Validation: Independent Classification Audit

The RA Database's triple-model pipeline with tiered adjudication is designed to produce reliable classifications through consensus and escalation. To assess whether this design succeeds — and to provide a validity check analogous to inter-rater reliability in manual coding studies — this Note reports the results of an independent classification audit using a model that played no role in the original pipeline.

### Sampling

Fifty cases were drawn from the RA Database (n=1,857) by stratified random sampling across two dimensions. First, cases were stratified by resolution tier to ensure the sample includes both easy cases (where the pipeline models agreed) and hard cases (where they diverged): unanimous consensus (Tier 0, n=12), majority agreement on non-critical fields (Tier 1, n=278), majority agreement on critical fields (Tier 2, n=565), Haiku 4.5-adjudicated three-way splits on non-critical fields (Tier 3, n=697), and Sonnet 4.6-adjudicated three-way splits on critical fields (Tier 4, n=302). Cases were sampled proportionally within each tier, with oversampling of the smallest tiers (Tiers 0 and 1) to ensure at least three cases per stratum. Second, within each tier, cases were stratified by outcome (plaintiff win, defendant win, mixed, procedural, settlement) to prevent the sample from over-representing the dominant outcome category.

### Protocol

Each sampled case's full opinion text was submitted to Claude Opus 4.6 (Anthropic), the most capable generally available large language model as of March 2026, with an identical classification prompt specifying the same twenty-eight fields and controlled vocabulary used by the pipeline models. Opus received no access to the pipeline's prior classifications, the resolution tier, or any model-specific outputs — it classified each case independently from the source text alone. The prompt was identical to the one reproduced in full in this Appendix's Section D, ensuring that any divergence between Opus and the pipeline reflects classification judgment rather than prompt variation.

### Metrics

Agreement between the Opus classifications and the pipeline's canonical values is reported at three levels of granularity.

*Field-level exact match.* For each of the twenty-eight classification fields, the exact match rate reports the percentage of sampled cases where Opus returned the identical value as the pipeline canonical. Exact match is the strictest measure: it treats any divergence, even between defensible alternatives, as disagreement.

*Per-field precision and recall.* Treating Opus as the reference classifier, precision measures the proportion of the pipeline's canonical values that Opus confirms (i.e., of all cases where the pipeline assigned a given category, how many did Opus also assign that category), and recall measures the proportion of Opus's classifications that the pipeline captured (i.e., of all cases Opus assigned a given category, how many did the pipeline also assign it). These metrics are reported for each categorical field.

*Cohen's kappa.* For six key fields — outcome, accommodation_type, primary_claim_type, disability_category, plaintiff_type, and defendant_type — Cohen's kappa provides a chance-corrected agreement statistic that accounts for the probability that two classifiers would agree by random assignment alone. Kappa values above 0.80 are conventionally interpreted as "almost perfect" agreement; 0.61–0.80 as "substantial"; and 0.41–0.60 as "moderate." An aggregate accuracy figure across all categorical fields provides a summary measure of pipeline reliability.

### Disaggregation by Resolution Tier

Agreement rates are reported separately for each resolution tier. This disaggregation tests a specific hypothesis: if the pipeline's consensus and adjudication process introduces systematic classification error rather than merely resolving genuine ambiguity, one would expect agreement with Opus to decline monotonically from Tier 0 (unanimous) through Tier 4 (Sonnet-adjudicated three-way splits). Conversely, if the adjudication process successfully resolves ambiguity, agreement rates should remain stable or decline only modestly across tiers, with any disagreement concentrated in fields where the underlying opinion is genuinely indeterminate. The tier-disaggregated results distinguish these possibilities.

### Framing and Limitations

This validation is LLM-versus-LLM, not human-versus-LLM, and this limitation warrants acknowledgment. Claude Opus 4.6 is not a human legal expert, and its classifications reflect the model's training rather than doctrinal judgment formed through legal practice. However, the validation's purpose is not to establish ground truth — it is to detect systematic classification errors in the pipeline and to measure the internal consistency of LLM-based legal classification at scale. If the pipeline's canonical values and an independent state-of-the-art model's classifications exhibit high agreement, this provides strong evidence that the pipeline is not producing idiosyncratic or systematically biased results. If agreement is low on specific fields, this identifies precisely where human review should be concentrated.

The design is analogous to inter-rater reliability in manual coding studies, where two independent coders classify the same materials and their agreement is measured to validate the coding scheme. In manual studies, neither coder is treated as infallible; the agreement statistic measures the reproducibility of the classification system. The same logic applies here: high Opus-pipeline agreement demonstrates that the classification schema produces reproducible results across independent classifiers, while low agreement on specific fields identifies classification categories that may require refinement or human adjudication. This approach follows an emerging methodological literature recognizing LLM-as-evaluator protocols as scalable alternatives to full human annotation when the research question concerns classification consistency rather than doctrinal correctness.
