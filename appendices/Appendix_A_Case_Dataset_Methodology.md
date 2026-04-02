## Appendix A: FHA Case Dataset — Construction Methodology

### A.1 Overview

This Appendix describes the construction of the **FHA Unified Database**, the principal empirical dataset underlying the case-classification analysis in this Note.

**The FHA Unified Database** (n=2,522 screened-in FHA cases; **1,720 disability cases**) is the single source of truth for all statistical claims in this Note. It was constructed by merging two overlapping source corpora — the RA Database (1,857 all-protected-class FHA cases, 2021–2026) and the 2015 FHA Database (1,461 screened-in § 3604(f) disability cases, 2015–2026) — with 796 cases appearing in both. A per-claim structured extraction via Haiku 4.5 Batch API enriched each record with detailed claim-level data. For the Note's disability-focused analysis, the unified database is filtered to the 1,720 cases where disability is a protected class.

**Three-Period Temporal Design.** Exact decision dates (resolved for all cases via CourtListener API, opinion text extraction, and Google Scholar) enable a three-period analysis:

| Period | Date Range | Boundary Event | Dated Disability Decided |
|--------|-----------|----------------|:---:|
| P1 | Jan 1, 2022 – June 28, 2024 | Pre-*Loper Bright* | 456 |
| P2 | June 28, 2024 – Feb 5, 2025 | *Loper Bright* decision → HUD Secretary confirmation | 116 |
| P3 | Feb 5, 2025 – present | Post-HUD Secretary change | 317 |

Of 1,720 disability cases, 1,191 have exact decision dates falling within the study period (2022–present). The remaining 529 are undated or pre-2022; they are included in overall statistics but excluded from three-period analysis.

**Source corpora.** The unified database draws from:

- **RA Database** (n=1,857): All-protected-class FHA cases, 2021–2026, from a CourtListener "fair housing act" search.
- **2015 FHA Database** (n=1,461 screened-in): Section 3604(f) disability cases, 2015–2026, from a CourtListener search supplemented by Google Scholar.

Both source databases were classified across twenty-eight substantive fields including case outcome, claim types, accommodation type, disability category, and procedural posture, using a multi-model classification pipeline with automated consensus detection. The RA Database used tiered consensus adjudication with model adjudication for three-way splits; the 2015 FHA Database used the same triple-model classification pipeline but resolved three-way splits using MiniMax M2.7 as the tiebreaker rather than API adjudication. After deduplication and merging, all cases were subjected to per-claim structured extraction via Haiku 4.5 Batch API. See Section A.5 for the reconciliation analysis.

### A.1.1 Research Design and Database Rationale

The three databases reflect an iterative research design. The FHA Pilot Database (n=331; see Section A.4) was constructed to investigate racial zoning disputes under the FHA. Analysis of the pilot data revealed that disability-based claims constituted 38.1% of federal FHA litigation — the largest single category, despite search terms designed to favor race-and-zoning cases — prompting a dedicated disability analysis.

Both principal databases were constructed using the same automated download pipeline, which queries the CourtListener REST API (v4) for the exact phrase "fair housing act" across all federal courts (Supreme Court, all circuits, all districts), including published, unpublished, and unknown-status opinions, with results deduplicated by cluster ID. The two databases differ in their filing-date filter, post-classification scope, and supplemental sources:

The **2015 FHA Database** (n=1,496) used a filing-date filter beginning January 1, 2015, chosen to coincide with HUD's promulgation of the Affirmatively Furthering Fair Housing Rule, 80 Fed. Reg. 42,272 (July 16, 2015). The original research question — whether the 2015 Rule affected disability enforcement — was superseded when the data revealed that *Loper Bright Enterprises v. Raimondo*, 144 S. Ct. 2244 (2024), produced a sharper empirical signal. The 2015 start date was retained for the decade of pre-*Loper Bright* baseline it provides. The CourtListener download (1,446 opinions) was supplemented by 215 case texts identified through Google Scholar to capture opinions not indexed in CourtListener, producing a corpus of 1,661 documents. The screening and classification pipeline then identified the subset involving § 3604(f) disability claims. The Google Scholar supplement consists entirely of post-*Loper Bright* cases (2024+) with a higher plaintiff win rate (18.9% strict) than the CourtListener-only post-*Loper Bright* cases (11.9% strict); including these cases attenuates the reported post-*Loper Bright* decline from 9.6 to 7.8 percentage points, making the reported effect size a conservative estimate.

The **RA Database** (n=1,857) used a filing-date filter of January 1, 2021 and retained all FHA protected classes after classification — no post-classification narrowing to disability. This broader scope enables cross-class comparisons — particularly the *Iqbal* citation disparity analysis (Appendix C) and protected-class distribution (Appendix D) — that the disability-only 2015 FHA Database cannot support.

### A.2 RA Database (n=1,857)

#### A.2.1 Source Documents

Case texts were obtained from CourtListener (Free Law Project) using the CourtListener REST API (v4). A Java application queried the search endpoint for the exact phrase "fair housing act" across all federal courts (Supreme Court, all circuit courts of appeals, and all district courts), filtered to opinions filed after January 1, 2021, and including published, unpublished, and unknown-status opinions. The application paginated through all results, collected case metadata (cluster ID, opinion IDs, case caption, date filed, court, circuit, judge, panel members, citations, and docket number), then downloaded full opinion text for each case using 10-thread parallel retrieval from the opinions endpoint. Results were deduplicated by cluster ID. Each case was stored as a plain-text file derived from the full text of the court opinion or order. The corpus comprises 2,366 documents. The 2021 start date and all-protected-class scope were chosen to enable cross-class comparisons that the 2015 FHA Database (§ 3604(f) only, 2015–2026) cannot support; see Section A.1.1. The source code for the download pipeline is available upon request from the author.

#### A.2.2 FHA Relevance Screening

Each document was first screened for FHA relevance using Google's Gemini 3.1 Flash Lite model, a lightweight classifier configured at zero temperature. The screening prompt instructed the model to determine whether the document was a legal decision adjudicating a claim under the Fair Housing Act, returning only "YES" or "NO." Documents classified as non-FHA were excluded from further processing. Of 2,366 documents screened, 1,857 passed the relevance filter (78.5%).

#### A.2.3 Triple-Model Independent Classification

Each FHA-relevant case was independently classified by three large language models via the OpenRouter API:

| Model | Provider | Suffix | Role |
|-------|----------|--------|------|
| MiniMax M2.7 | MiniMax | `_minmax` | Primary extraction model |
| DeepSeek V3.2 | DeepSeek | `_deepseek` | Independent verification |
| Kimi K2.5 | Moonshot AI | `_kimi` | Independent verification |

All three models received identical inputs: (1) a system prompt specifying the classification schema with controlled vocabulary for each field, and (2) the full case text (truncated to 50,000 characters for longer opinions, preserving the first 25,000 and last 25,000 characters). The system prompt enforced a flat JSON output structure with twenty-eight fields spanning:

- **Case identification**: case name, citation, court, year
- **Substantive classification**: FHA section cited, accommodation type, disability category, claim types, outcome
- **Party identification**: plaintiff type, defendant type
- **Procedural context**: procedural posture, housing type, property location
- **Doctrinal indicators**: interactive process discussion, delay-as-denial, *Loper Bright* citation, race-disability intersection
- **Narrative fields**: key holding, brief summary, accommodation description, key cases cited

Each model was configured at temperature 0.2 with explicit reasoning budget caps. An earlier evaluation using GLM-5 (Zhipu) — subsequently cancelled due to cost — revealed that reasoning-enabled models produce unpredictable output token volumes when reasoning budgets are unconstrained, significantly complicating cost estimation and pipeline reliability. This prompted the adoption of per-model reasoning budget limits for all subsequent runs.

| Model | Role | Temperature | Reasoning Budget | Max Output Tokens | Output Cost/M |
|-------|------|-------------|-----------------|-------------------|---------------|
| MiniMax M2.7 | Primary extraction | 0.2 | 2,048 tokens | 8,192 | $1.20 |
| DeepSeek V3.2 | Consensus verification | 0.2 | 16,384 tokens | 8,192 | $0.38 |
| Kimi K2.5 | Consensus verification | 0.2 | 1,024 tokens | 8,192 | $2.20 |
| Gemini 3.1 Flash Lite | FHA relevance screening | 0.0 | 0 (disabled) | — | — |
| Haiku 4.5 | Tier 3 adjudication (Batch API) | default | default | default | — |
| Claude Sonnet 4.6 | Tier 4 adjudication (Batch API) | default | 2,000 (thinking) | 4,000 | — |

Reasoning budgets were calibrated primarily by cost. MiniMax M2.7 served as the primary extraction model; DeepSeek V3.2 and Kimi K2.5 served as independent verification models whose role was to confirm or dispute MiniMax's classifications. DeepSeek received the largest reasoning budget (16,384 tokens) because its output pricing ($0.38/M) made extended reasoning inexpensive. Kimi K2.5 received a smaller budget (1,024 tokens) despite higher output cost ($2.20/M) because its verification role did not require extended deliberation. MiniMax's budget (2,048 tokens) balanced extraction quality against its moderate output cost ($1.20/M).

The three models processed each case concurrently, producing three independent classification records per case.

**Coding protocol.** Each case was coded for the following fields:

| Field | Description | Coding Method |
|-------|-------------|---------------|
| outcome | Case outcome | PLAINTIFF_WIN, DEFENDANT_WIN, MIXED, PROCEDURAL, SETTLEMENT, UNDETERMINED |
| accommodation_type | Primary accommodation at issue | 13 categories (see Technical Appendix K.2); UNDETERMINED if not determinable |
| secondary_accommodation | Secondary accommodation if any | Same categories as above; NONE if single issue |
| defendant_type | Institutional category of defendant | PRIVATE_LANDLORD, PROPERTY_MANAGEMENT, HOA_CONDO_ASSN, HOUSING_AUTHORITY, DEVELOPER, MUNICIPALITY, OTHER |
| plaintiff_type | Institutional category of plaintiff | INDIVIDUAL_TENANT, GROUP_HOME_OPERATOR, FAIR_HOUSING_ORG, GOVERNMENT, OTHER |
| disability_category | Primary disability type | MENTAL_HEALTH, SUBSTANCE_USE, MOBILITY, SENSORY, INTELLECTUAL_DEVELOPMENTAL, MULTIPLE_UNSPECIFIED, OTHER |
| procedural_posture | Stage at which decision occurred | MOTION_TO_DISMISS, SUMMARY_JUDGMENT, PRELIMINARY_INJUNCTION, TRIAL, DEFAULT_JUDGMENT, APPEAL, SETTLEMENT_CONSENT, ADMINISTRATIVE_REVIEW, DISCOVERY, OTHER_PROCEDURAL |
| property_state | State where property is located | Two-letter abbreviation |
| housing_type | Type of housing | PRIVATE_MARKET, PUBLIC_HOUSING, SECTION_8_VOUCHER, SECTION_8_PBV, LIHTC, SECTION_811, SECTION_202, SUPPORTIVE_HOUSING, OTHER_SUBSIDIZED, HOA_CONDO, MANUFACTURED_HOUSING, UNDETERMINED |
| year | Year of decision | Numeric |
| court | Deciding court | Standard abbreviation |

#### A.2.4 Consensus Detection and Tiered Adjudication

The three-model outputs were consolidated into a single canonical record using a tiered resolution strategy designed to minimize cost while preserving classification accuracy:

**Tier 0 — Full Consensus (No API Call).** Where all three models returned identical values for every categorical field, that value was adopted as canonical. Twelve records achieved full consensus across all categorical fields (0.6% of FHA-relevant records).

**Tier 1 — Majority Agreement, Non-Critical Fields (No API Call).** Where two of three models agreed on all fields, with dissent limited to non-critical fields (any field other than outcome, primary claim type, or claim types), the majority value was adopted. 278 records fell into this tier (15.0%).

**Tier 2 — Majority Agreement, Critical Fields (No API Call).** Where two of three models agreed on outcome, primary claim type, or claim types but one model dissented, the 2-of-3 consensus was treated as sufficient. 565 records fell into this tier (30.4%).

**Tier 3 — Three-Way Split, Non-Critical Fields → Haiku 4.5 Adjudication.** Where all three models returned different values for non-critical fields (e.g., accommodation type, defendant type, disability category) with no majority, the case was submitted to Claude Haiku 4.5 (Anthropic) for adjudication. Haiku received the original case text alongside each model's answer for the disputed fields and was instructed to determine the correct classification using the same controlled vocabulary. 697 cases were adjudicated by Haiku (37.5%).

**Tier 4 — Three-Way Split, Critical Fields → Sonnet 4.6 Adjudication.** Where all three models returned different values for outcome, primary claim type, or claim types, the case was submitted to Claude Sonnet 4.6 (Anthropic) — a more capable model — for adjudication. In addition to resolving the disputed categorical fields, Sonnet re-extracted the four free-text narrative fields (key holding, brief summary, accommodation description, key cases cited) fresh from the source text. 302 cases were adjudicated by Sonnet (16.3%).

Both adjudication tiers used the Anthropic Message Batches API, which processes requests asynchronously at a 50% cost discount. Each adjudication request included the original case text and a structured presentation of each model's answer for the disputed fields. The adjudicating model was required to provide reasoning for each resolution, which was stored as metadata in the final record.

**Free-Text Field Resolution.** For narrative fields (key holding, brief summary, accommodation description, key cases cited), exact consensus is not meaningful because models produce different phrasings of equivalent content. For Tier 4 (Sonnet-adjudicated) records, Sonnet re-extracted these fields from the source text. For all other records, the MiniMax M2.7 version was adopted as the canonical text, as it consistently produced the most detailed extractions.

#### A.2.5 Agreement Rates Across Models

The following table reports inter-model agreement rates for key classification fields prior to adjudication (n=1,857 FHA-relevant records):

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

Fields with near-perfect agreement (court, year) confirm that all three models correctly identified basic case metadata. Fields with lower agreement rates (accommodation type, disability category) reflect three identified sources of disagreement: (1) genuine classification ambiguity where cases involve overlapping accommodation types or multiple disabilities; (2) non-RA case contamination, where cases involving pure disparate treatment, design-and-construction enforcement, or non-FHA claims passed the initial screening filter (a supplemental per-claim extraction found that 68.1% of cases in the database contain no reasonable accommodation claim at all; see Section A.2.7); and (3) systematic positional bias, where models anchor to different accommodations in multi-claim opinions — MiniMax anchors to the first-mentioned accommodation (57% of informative cases), while Kimi anchors to the most-discussed (79%), with the three-model ensemble partially self-correcting via these opposing biases (Fisher's exact test: OR=4.89, p=0.12, n=14 informative cases). Even on the most contested field (accommodation type, 34.7% unanimous), the combination of majority agreement and adjudication resolved 100% of records to a canonical value.

#### A.2.6 Final Dataset Composition

The final consolidated dataset contains 1,857 FHA-relevant records, each with canonical (unsuffixed) values for all twenty-eight classification fields. The unified database achieves 100% field coverage on twenty-six of twenty-eight fields; the two partial fields — primary claim type (95.9%) and primary protected class (98.5%) — reflect cases where no model could determine the value and the adjudicating model likewise returned no result, indicating genuine indeterminacy in the source opinion.

Two database files are produced:

- **Unified database** (`FHA_RA_Database_unified_[timestamp].json`): Contains only canonical fields, resolution metadata, and identity fields — the single source of truth for analysis. Average of 27 fields per record.
- **Audit database** (`FHA_RA_Database_audit_[timestamp].json`): Preserves all three model-specific values with suffixes (`_minmax`, `_deepseek`, `_kimi`) alongside canonical values and adjudication reasoning — the full provenance trail. Average of 91 fields per record.

| Resolution Method | Records | Percentage |
|-------------------|---------|------------|
| Unanimous (all 3 models agree on every field) | 12 | 0.6% |
| Majority (non-critical field dissent only) | 278 | 15.0% |
| Majority (critical field dissent, 2-of-3 trusted) | 565 | 30.4% |
| Haiku 4.5 adjudicated (non-critical 3-way splits) | 697 | 37.5% |
| Sonnet 4.6 adjudicated (critical 3-way splits) | 302 | 16.3% |
| Other (consensus/majority fallback) | 3 | 0.2% |
| **Total FHA-relevant** | **1,857** | **100%** |

Of the 1,857 FHA-relevant records, 858 (46.2%) were resolved entirely through consensus or majority vote with no additional API calls (Tiers 0–2 plus 3 Other cases). The remaining 999 (53.8%) required adjudication by an Anthropic model to resolve at least one three-way disagreement (Tiers 3–4).

#### A.2.7 Supplemental Per-Claim Extraction (Haiku 4.5)

A supplemental extraction pass was conducted on all 2,366 source documents (including the 509 that failed the initial FHA relevance screen) using Claude Haiku 4.5 (Anthropic) via the Message Batches API at temperature 0.1. Unlike the pipeline's single-case-single-classification approach, this pass decomposed each case into its constituent legal claims, extracting an independent record for each FHA claim the court addressed.

**Extraction schema.** Each case produced a JSON record containing: (1) case-level fields (pro se status, counsel identification, disability alleged, plaintiff type, defendant type, disability category, housing type, FHA sections cited, interactive process discussed, delay-as-denial, *Loper Bright* cited, *Iqbal*/*Twombly* cited, race mentioned); and (2) an array of claim-level objects, one per distinct FHA claim, each classified by legal theory (REASONABLE_ACCOMMODATION, DISPARATE_TREATMENT, DISPARATE_IMPACT, RETALIATION, DESIGN_AND_CONSTRUCTION, INTERFERENCE_COERCION, NOT_FHA, or UNCLEAR), accommodation type (for RA claims only), RA standard applied, procedural stage, disposition, merits reached (YES/NO/PARTIAL/SETTLEMENT), dismissal reason, outcome, and reasoning. Non-FHA claims were collapsed into a single object per case.

**Results.** The unified per-claim extraction produced 6,718 total claims from 3,193 cases (average 2.1 claims per case) with zero parse errors. Key findings:

| Metric | Value |
|--------|-------|
| Total claims | 6,718 |
| FHA claims | 4,464 |
| Non-FHA claims | 2,254 |
| DISPARATE_TREATMENT claims | 1,731 (38.8% of FHA) |
| REASONABLE_ACCOMMODATION claims | 1,257 (28.2% of FHA) |
| RETALIATION claims | 601 (13.5% of FHA) |
| DISPARATE_IMPACT claims | 392 (8.8% of FHA) |
| INTERFERENCE_COERCION claims | 243 (5.4% of FHA) |
| UNCLEAR claims | 168 (3.8% of FHA) |
| DESIGN_AND_CONSTRUCTION claims | 72 (1.6% of FHA) |

**Merits distribution.** Of all FHA claims in the unified dataset: merits_reached=NO 72.0%, merits_reached=YES 24.7%, merits_reached=PARTIAL 2.6%, merits_reached=SETTLEMENT 0.8%.

**Per-theory merits win rates.** Among claims reaching merits adjudication:

| Theory | Merits Claims | Plaintiff Wins | Win Rate |
|--------|--------------|----------------|----------|
| DESIGN_AND_CONSTRUCTION | 18 | 5 | 27.8% |
| DISPARATE_TREATMENT | 499 | 110 | 22.0% |
| DISPARATE_IMPACT | 118 | 22 | 18.6% |
| REASONABLE_ACCOMMODATION | 367 | 59 | 16.1% |
| INTERFERENCE_COERCION | 68 | 6 | 8.8% |
| RETALIATION | 142 | 8 | 5.6% |

Accommodation-type win rates and RA-specific findings in the Note are computed on the RA merits population (367 claims reaching merits) unless otherwise noted.

**Cross-validation.** The Haiku per-claim extraction achieved 65.9% exact match (87/132 cases) with the pipeline's canonical accommodation-type classification on RA merits cases. Divergences were concentrated in taxonomic boundary disputes: sober-living zoning cases classified as POLICY_EXCEPTION by Haiku versus SOBER_LIVING_GROUP_HOME_ZONING by the pipeline (7 cases), and pipeline residual categories (DISCRIMINATION_PRIMARY, UNDETERMINED) refined by Haiku into specific categories (4 cases). No systematic directional bias was identified.

**Merits_reached classification rule.** The extraction enforced a stage-dependent rule for merits_reached: at the motion-to-dismiss or § 1915 screening stage, *Iqbal*/*Twombly* and nexus-failure dismissals were classified as merits_reached=NO (the court assessed pleading sufficiency, not the substantive legal standard); at the summary judgment or trial stage, all outcomes were classified as merits_reached=YES (the court evaluated the evidentiary record against the substantive elements of the claim, even if the plaintiff lost). This distinction is critical for separating pro se pleading failures from substantive merits losses.

**Cost.** The Haiku extraction cost approximately $17.58 via the Batch API (50% discount): 26.4M input tokens + 1.7M output tokens.

**Development history.** The RA Database was developed through an iterative process. An initial exploratory dataset (the FHA Pilot Database, n=331; see Section A.4), originally constructed to investigate racial zoning disputes, unexpectedly revealed that disability-based reasonable accommodation claims dominated the federal FHA docket and exhibited distinctive enforcement patterns, redirecting the research toward § 3604(f)(3)(B) and the post-*Loper Bright* timeline. Pilot iterations (v1–v3, n=802–1,029) refined the classification schema and search methodology for this narrower domain. These pilot iterations used single-model classification (Claude Sonnet 4.6), which proved cost-prohibitive at scale. The final iteration (v4, n=1,857) adopted the triple-model pipeline described above (MiniMax, DeepSeek, Kimi via OpenRouter) as a cost-effective alternative that also improved classification reliability through consensus. The v4 database replaced all prior iterations for every statistical claim in this Note.

### A.3 2015 FHA Database (n=1,496) — Disability Enforcement Cases

**Source documents.** The corpus comprises 1,661 case texts from two sources: 1,446 opinions downloaded from the CourtListener REST API using the same automated pipeline as the RA Database (the exact phrase "fair housing act" across all federal courts) with a filing-date filter of January 1, 2015 (see Section A.1.1 for rationale), and 215 supplemental opinions identified through Google Scholar to capture cases not indexed in CourtListener. The search downloaded all FHA opinions regardless of protected class; the § 3604(f) disability narrowing was performed during screening and classification.

**Screening.** Each of 1,661 downloaded case texts was screened for FHA relevance using Google Gemini 3.1 Flash Lite at zero temperature. 1,496 cases (90.1%) passed the relevance filter; 165 were excluded as non-FHA.

**Classification pipeline.** The same triple-model classification pipeline used for the RA Database v4, with independent classification by MiniMax M2.7, DeepSeek V3.2, and Kimi K2.5 (via OpenRouter API), followed by tiered consensus resolution:

| Resolution Method | Records | Percentage |
|-------------------|---------|------------|
| Unanimous (all 3 agree on every field) | 48 | 3.2% |
| Majority (non-critical field dissent only) | 271 | 18.1% |
| Majority (critical field dissent, 2-of-3 trusted) | 435 | 29.1% |
| MiniMax tiebreaker (non-critical 3-way splits) | 171 | 11.4% |
| MiniMax tiebreaker (critical 3-way splits) | 571 | 38.2% |
| **Total FHA-relevant** | **1,496** | **100%** |

Unlike the RA Database, three-way splits in the 2015 FHA Database were resolved using the MiniMax model as tiebreaker rather than Anthropic model adjudication. The higher three-way split rate (49.6% vs. 53.8% requiring adjudication in the RA Database) reflects comparable classification ambiguity. Field-level agreement rates: outcome 68.3% unanimous, accommodation_type 38.0%, disability_category 50.7%, court 93.3%, year 97.5%.

**Coding protocol.** The same 28-field schema as the RA Database v4, with identical controlled vocabulary. The unified database contains canonical values for all fields, with an audit trail preserving all three model-specific values.

**Normalization.** Free-text fields (race_if_mentioned, subsidy_program, defendant_type, disability_category) were normalized to controlled vocabulary using a separate normalization pipeline that maps synonyms to canonical categories (e.g., "African American" → "Black"; "Section 8" / "Housing Choice Voucher" → "SECTION_8_HCV").

### A.4 FHA Pilot Database (n=331)

**Search methodology.** Cases were downloaded from the CourtListener REST API using a query requiring all three terms — "fair housing act," "race," and "zoning" — across all federal courts. The search period covers 2012 through 2026. The query was originally designed to investigate the intersection of racial zoning disputes and Fair Housing Act enforcement — specifically, whether race-based exclusionary zoning claims produced different litigation outcomes than other FHA theories. The resulting dataset unexpectedly revealed that disability-based reasonable accommodation claims dominated the federal docket and exhibited distinctive enforcement patterns not captured by the race-and-zoning framing. This finding redirected the research toward § 3604(f)(3)(B) and the post-*Loper Bright* enforcement landscape, prompting the construction of the RA Database and § 2015 FHA Database described above.

**Coding protocol.** The same schema as the RA Database, with additional fields for protected class identification and *Iqbal* citation tracking. Because the pilot query captured cases across all FHA protected classes (not limited to disability), this database enabled cross-class comparisons — particularly the *Iqbal* citation disparity analysis — that the disability-only RA Database could not support.

**Protected-class distribution.** Of the 331 pilot cases, disability-based claims constituted 38.1% (n=126) — the largest single category — compared with race at 30.8% (n=102), despite search terms requiring "race" and "zoning." This unexpected dominance of disability claims prompted the dedicated disability analysis that became this Note.

| Protected Class | n | Share of Cases |
|----------------|---|----------------|
| Disability | 126 | 38.1% |
| Race | 102 | 30.8% |
| Sex | 26 | 7.9% |
| Familial Status | 25 | 7.6% |
| National Origin | 22 | 6.6% |
| Unclear | 17 | 5.1% |
| Religion | 13 | 3.9% |

HUD administrative complaint data shows disability at **54.6%** of all complaints (2024), versus 15.58% for race. The pilot database's 38.1% litigation share is lower than the administrative complaint share, suggesting either that disability claims are less likely to reach federal court or that the pilot database underrepresents disability due to its search terms — requiring "race" and "zoning" — which systematically over-represent race-related cases. The RA Database (Section A.2), which uses a broader "fair housing act" query without race or zoning restrictions, provides a more representative cross-class distribution: disability 59.1%, race 22.8%.

### A.5 Deduplication and Unified Dataset Construction

The RA Database (2,366 source documents) and 2015 FHA Database (1,661 source documents) were deduplicated by source file to produce 3,193 unique cases. The combined corpus was then subjected to per-claim structured extraction via Haiku 4.5 Batch API, producing the unified dataset (N=3,193 cases, 6,718 claims) that serves as the single source of truth for all statistical claims in this Note.
**Relationship to the "approximately 2,566" figure in the Note.** The Note refers to "approximately 2,566 unique federal FHA cases" when describing the combined corpus across all three databases. This figure reflects the total unique cases after deduplicating across the RA Database (1,857 FHA-relevant), 2015 FHA Database (1,496 FHA-relevant), and FHA Pilot Database (331 FHA-relevant), with approximately 1,118 cases appearing in multiple databases. The Unified Dataset (N=3,193) is larger because it counts the RA and 2015 FHA Databases before cross-database deduplication — each case retains its source-database classification for comparison purposes, while per-claim extraction treats the deduplicated set as a single corpus. The 2,566 figure is the correct unique-case count; the 3,193 figure is the correct input count for per-claim extraction.

The unified dataset contains 4,464 FHA claims and 2,254 non-FHA claims. Theory distribution among FHA claims: DISPARATE_TREATMENT 1,731 (38.8%), REASONABLE_ACCOMMODATION 1,257 (28.2%), RETALIATION 601 (13.5%), DISPARATE_IMPACT 392 (8.8%), INTERFERENCE_COERCION 243 (5.4%), UNCLEAR 168 (3.8%), DESIGN_AND_CONSTRUCTION 72 (1.6%).

**Defendant type distribution** (N=3,193 cases): OTHER 800 (25.1%), PROPERTY_MANAGEMENT 755 (23.6%), MUNICIPALITY 624 (19.5%), PRIVATE_LANDLORD 384 (12.0%), HOUSING_AUTHORITY 287 (9.0%), HOA_CONDO 267 (8.4%).

**Race mentioned**: 1,024 of 3,193 cases (32.1%).

### A.6 Cost and Reproducibility

| Pipeline Stage | Model | Records | Estimated Cost |
|----------------|-------|---------|----------------|
| Screening | Gemini 3.1 Flash Lite | 2,366 | *See note below* |
| Triple classification | MiniMax M2.7 ($14.85) + DeepSeek V3.2 ($31.33) + Kimi K2.5 ($39.41) (via OpenRouter) | 1,857 x 3 | $85.59 |
| Abandoned model evaluation (GLM-5) | GLM-5 via OpenRouter (partial run, not used in final pipeline) | — | $49.32 |
| Tier 3 adjudication | Claude Haiku 4.5 (Anthropic Batch API) | 697 | *See note below* |
| Tier 4 adjudication | Claude Sonnet 4.6 (Anthropic Batch API) | 302 | *See note below* |
| **OpenRouter subtotal** | | | **$134.90** |
| **Total (all providers)** | | | **$134.90 + Gemini + Anthropic Batch** |

*Note: OpenRouter API costs were extracted from the provider activity export dated March 28, 2026 (12,290 generation records). GLM-5 (Zhipu) was initially evaluated as one of the classification models but was cancelled partway through due to cost. The $49.32 represents sunk cost from the partial run; GLM-5 outputs were not used in the consensus pipeline or any statistical claims. The 12,290 generation records in the OpenRouter export include this abandoned run alongside the triple-model classification passes. Gemini 3.1 Flash Lite screening costs (Google API) and Anthropic Batch API adjudication costs are billed separately and are not included in the OpenRouter total. Gemini Flash Lite pricing at the time of the screening run was approximately $0.01–0.02 per 1M input tokens; the screening stage's total token volume (2,366 documents × average prompt length) places the estimated screening cost below $5. Anthropic Batch API costs for Haiku 4.5 and Sonnet 4.6 adjudication are available upon request from the author.*

The full pipeline — source texts, consolidation code, and the final dataset with all model-specific outputs — is available upon request from the author. The classification prompts are reproduced in Technical Appendix K. The adjudication model's field-by-field reasoning is preserved in the `_adjudication_reasoning` metadata field of each adjudicated record, enabling post-hoc review of every resolution decision.

### A.7 Known Limitations

1. **Convenience sampling.** The unified dataset is a convenience sample drawn from published and electronically available opinions, not census data. Cases resolved through settlement, unpublished orders, or state courts are excluded. The dataset cannot claim representativeness of all disability FHA litigation.

2. **Pilot iterations superseded.** Pilot iterations (v1–v3) contained data quality issues including incomplete boolean field extraction; all such issues were resolved in the v4 rebuild. All statistical claims in this Note use v4 data exclusively.

3. **Accommodation type classification.** Approximately 30% of v4 cases received a specific accommodation-type classification; the remainder were classified as DISCRIMINATION_PRIMARY (24.5%), OTHER (12.6%), or UNDETERMINED (32.8%), reflecting cases where discrimination rather than accommodation was the central claim or where the accommodation type could not be determined from the opinion text. The supplemental per-claim extraction (Section A.2.7) revealed that 68.1% of the database contains no reasonable accommodation claim at all, explaining much of the residual-category concentration. Accommodation-type win rates in the Note are therefore computed only on the 175 RA claims that reached merits adjudication, with 95% Wilson confidence intervals reported for all categories.

4. **UNDETERMINED values (v4).** UNDETERMINED rates by field: disability_category 55.1%, accommodation_type 32.8%, housing_type 15.5%, defendant_type varies. The high disability_category UNDETERMINED rate reflects many opinions that do not specify the plaintiff's particular disability. The per-claim extraction confirmed that 52.1% of cases involve no disability allegation at all, explaining the high UNDETERMINED rate.

5. **No regression adjustment.** All win rates are unadjusted bivariate comparisons. Confounders including defendant type, circuit, procedural posture, time period, and accommodation type have not been isolated through multivariate regression. Descriptive patterns should not be interpreted as causal. (Multivariate regression results are reported separately in Appendix A-3.)

6. **Full population parameters unknown.** Without knowing the total universe of disability FHA cases filed in federal court during the study period, selection bias cannot be ruled out.

7. **50,000-character truncation.** The truncation applied to longer opinions means that analysis in the middle sections of lengthy decisions may be lost, though the head-and-tail preservation strategy retains the caption, introduction, and conclusion where courts typically state their holdings.

8. **Non-RA case contamination.** The FHA relevance screening filter (Gemini Flash Lite) passed 1,857 cases as FHA-relevant, but the per-claim extraction (Section A.2.7) found that only 755 cases (31.9%) contain any reasonable accommodation claim. The remaining 68.1% involve disparate treatment, retaliation, design-and-construction, or non-FHA claims that share FHA keywords but are not RA cases. Human validation of 20 randomly sampled cases with model disagreements confirmed this pattern: 7 of 20 (35%) were not RA cases at all, including design-and-construction consent decrees, pure racial discrimination claims, and insurance disputes with no housing nexus. The three-population segmentation described in Section A.2.7 addresses this contamination by computing RA-specific statistics only on the merits-RA population.

9. **Pro se pleading failure population.** The per-claim extraction identified 1,643 pro se cases (51.5% of the unified dataset), with an overall win rate of 0.9% compared to 9.1% for represented plaintiffs (1,550 cases). *Iqbal*/*Twombly* dismissals account for 1,433 claims (32.1% of all claims), confirming the centrality of the motion-to-dismiss stage as the primary gatekeeping mechanism. These cases inflate the defendant-win rate in every accommodation category and depress apparent accommodation-type effectiveness when included in the analysis denominator. The Note reports both full-dataset and merits-only statistics where they diverge.

10. **Design-and-construction misclassification.** The per-claim extraction identified 42 D&C claims (0.9% of all claims), compared to zero cases classified as DESIGN_AND_CONSTRUCTION by the pipeline's accommodation-type field. The pipeline misclassified D&C cases as OTHER (14), STRUCTURAL_MODIFICATION (3), POLICY_EXCEPTION (2), and other categories. Because D&C cases involve no individual accommodation request — they enforce statutory design mandates under § 3604(f)(3)(C) — they are excluded from accommodation-type win rate analysis. Of 42 D&C claims, only 9 reached merits adjudication, achieving a 22.2% plaintiff success rate (95% CI: 6.3%–54.7%).

11. **Positional bias in multi-claim cases.** Full-text scanning revealed that 38.5% of cases mention two or more accommodation categories in the opinion text. In 14 informative cases where the first-mentioned and most-discussed accommodations differ, MiniMax anchored to the first-mentioned accommodation (57%) while Kimi anchored to the most-discussed (79%). The three-model ensemble partially self-corrects: the majority-vote canonical resolution favored the most-discussed accommodation 8:5 over the first-mentioned. Fisher's exact test (MiniMax vs. Kimi): OR=4.89, p=0.12 — suggestive but not significant at n=14. Pooled across all models, no overall positional bias was detected (binomial test: 18 first vs. 22 most, p=0.64).

Despite these limitations, the triple-model-with-adjudication methodology substantially improves on single-model classification. The supplemental per-claim extraction addresses the most significant limitation — the single-case-single-classification constraint — by decomposing cases into independent claims and enabling proper population segmentation. The 97–99% unanimous agreement rate on objective fields (court, year) confirms that the models reliably extract factual information, while the tiered adjudication process ensures that genuinely ambiguous classifications receive attention from a more capable model rather than being resolved by arbitrary tiebreaking.

### A.8 Classification Prompts

The FHA relevance screening prompt and case classification prompt constitute the instruments used to generate all classification data in both databases. They are reproduced in full in Technical Appendix K to enable replication. Cross-references to the prompt controlled vocabulary (e.g., "13 categories (see Section A.8.2)") refer to Technical Appendix K.

---
