# Data Dictionary — FHA Unified Database

The FHA Unified Database (`data/FHA_Unified_Database.json`) contains **3,198 federal FHA opinions** in the raw corpus (RA Database 2,366 ∪ 2015 § 3604(f) Database 1,661; 829 overlap by `source_file`). Of these, **2,522** are screened-in federal FHA cases (`screening_result == "YES"`), and **1,770** are screened-in disability cases (`screening_result == "YES"` AND (`protected_classes` contains `"disability"` OR `disability_alleged == True`)). The narrower filter `protected_classes` contains `"disability"` alone yields **1,720**; the 50-case gap is records flagged `disability_alleged=True` without `"disability"` appearing in `protected_classes`. **1,770** is the canonical disability-analysis population; all downstream subsets (disability-wave tranche, pleading-loss universe, etc.) are nested within it.

Each record is a JSON object with the following 28 fields, produced by the Agile ELS multi-model consensus pipeline.

## Case Identification

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `case_name` | string | Full case caption | "Smith v. ABC Apartments" |
| `citation` | string | Reporter citation or docket number | "2024 WL 1234567" |
| `court` | string | Deciding court | "D. Ariz." |
| `year` | integer | Decision year | 2024 |
| `circuit` | string | Federal circuit | "9th Cir." |

## Substantive Classification

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `procedural_posture` | enum | Procedural stage at decision | MTD, summary_judgment, trial, preliminary_injunction, default_judgment, appeal, other |
| `fha_section_cited` | array | FHA sections invoked | ["3604(f)", "3604(c)"] |
| `primary_protected_class` | enum | Dominant protected class | disability, race, national_origin, familial_status, religion, sex, color |
| `accommodation_type` | enum | Type of accommodation sought | structural_modification, equipment, service_animal, emotional_support_animal, policy_exception, parking, transfer, other |
| `outcome` | enum | Case disposition | plaintiff_win, defendant_win, mixed, settled, procedural |
| `primary_claim_type` | enum | Lead FHA theory | reasonable_accommodation, disparate_treatment, disparate_impact, design_and_construction, retaliation, interference |
| `claim_types` | array | All FHA theories raised | ["reasonable_accommodation", "disparate_treatment"] |
| `plaintiff_type` | enum | Plaintiff category | individual, fair_housing_org, government, group_home_operator, class_action |
| `defendant_type` | enum | Defendant category | landlord, hoa, municipality, property_manager, developer, other |
| `disability_category` | enum | Primary disability type | mobility, mental_health, substance_abuse, sensory, intellectual, chronic_illness, other |
| `housing_type` | enum | Housing context | apartment, single_family, group_home, public_housing, condo, assisted_living, other |
| `subsidy_program` | string | Federal housing program | "Section 8", "LIHTC", "none" |

## Doctrinal Markers

| Field | Type | Description |
|-------|------|-------------|
| `iqbal_twombly_cited` | boolean | Whether *Iqbal*/*Twombly* pleading standards are invoked |
| `loper_bright_cited` | boolean | Whether *Loper Bright Enterprises v. Raimondo* is cited |
| `interactive_process_discussed` | boolean | Whether the reasonable-accommodation interactive process is analyzed |

## Narrative Fields

| Field | Type | Description |
|-------|------|-------------|
| `brief_summary` | string | One-paragraph case summary |
| `key_holding` | string | Primary legal holding |
| `key_cases_cited` | array | Principal authorities cited |

## Per-Claim Decomposition

| Field | Type | Description |
|-------|------|-------------|
| `fha_claims` | array of objects | Individual legal claims extracted by Haiku 4.5. Each object contains `claim_type`, `outcome`, `reasoning`, and `protected_class`. |

## Pipeline Metadata

| Field | Type | Description |
|-------|------|-------------|
| `resolution_tier` | integer (0-4) | Consensus tier that resolved this record. 0 = unanimous, 1-2 = majority vote, 3 = Haiku adjudication, 4 = Sonnet adjudication. |
| `model_agreement` | object | Per-field agreement metadata across three classifiers (MiniMax, DeepSeek, Kimi) |
| `adjudicator` | string | Model that adjudicated disagreements, if escalated ("haiku-4.5", "sonnet-4.6", or null) |
| `source_corpus` | enum | Origin corpus: "ra_database" (2021+ RA cases), "fha_2015_database" (2015 FHA Database § 3604(f)), or "recent_supplement" |

## Source Databases

The unified database merges records from two source corpora:

| Database | File | Scope | Raw n | Screened-in n |
|----------|------|-------|-------|---------------|
| RA Database | `FHA_RA_Database_unified_20260328_090852.json` | Reasonable accommodation cases, all protected classes, 2021+ | 2,366 | 1,857 |
| 2015 FHA Database | `FHA_3604_Database_unified_20260328_104352.json` | § 3604(f) cases from 2015 FHA Database, 2015+ | 1,661 | 1,461 |
| **Unified (raw)** | `FHA_Unified_Database.json` | Raw union (by `source_file`); 829 raw overlap | **3,198** | — |
| **Unified (screened)** | `FHA_Unified_Database.json`, filtered | `screening_result == "YES"`; 796 screened overlap | — | **2,522** |
| **Disability population** | `FHA_Unified_Database.json`, filtered | Screened-in AND (`protected_classes` ∋ `"disability"` OR `disability_alleged`) | — | **1,770** |

## Within-Group Analysis: Strong-Case Represented Subset

The within-group analysis reported in the Note uses a "strong-case represented subset" to test whether represented plaintiffs experienced any deterioration beyond the composition effect. This subset is defined as:

1. **Represented**: `pro_se` = false (plaintiff has counsel)
2. **Specific-duty claim**: `primary_claim_type` in {`reasonable_accommodation`, `design_and_construction`} (excludes open-textured discrimination claims)
3. **Dated**: case has an exact decision date within the P1 or P3 period windows

This subset isolates the cases most likely to reflect genuine judicial treatment effects, filtering out the pro se filing surge and vague claims that drive the aggregate decline. In this subset, broad win rates fell from 69.0% (P1) to 52.3% (P3), indicating a residual within-group deterioration consistent with a tightening pleading gate even for represented plaintiffs. The database does not contain a dedicated `strong_case_subset` flag; the subset is constructed analytically by applying the three filters above.

## Notes

- Enum values are lowercase with underscores. Array fields may contain multiple values.
- The `fha_claims` array enables claim-level analysis (6,718 total claims across 3,193 cases).
- Pipeline metadata fields allow tier-disaggregated reliability analysis.
- For the per-claim extraction schema, see [`pipeline/per_claim_extraction_schema.json`](pipeline/per_claim_extraction_schema.json).

---

# HUD Administrative Datasets

The repository also includes three HUD administrative datasets used for the institutional-infrastructure analysis in Parts I, III, and IV. Detailed methodology and findings are documented in [Appendix L](appendices/Appendix_L_HUD_Administrative_Data.md). Analysis scripts are in `scripts/`.

## CDBG National Accomplishment Reports

**File:** `data/CDBG_Accomp_Natl.xlsx` | **Script:** `scripts/cdbg_analysis.py` | **Output:** `results/cdbg_results.json`

CDBG grantee accomplishment data (FY2005–FY2024), reporting persons/households served by activity code. Key fields in output: `disability_analysis_by_year` (yearly 05B/03B beneficiary counts), `summary_statistics` (20-year totals, shares, trends), `activity_categories` (full code inventory).

## Picture of Subsidized Households (POSH)

**Files:** `data/US_2024_2020census.xlsx`, `data/STATE_2024_2020census.xlsx`, `data/dictionary_2024.pdf` | **Script:** `scripts/posh_analysis.py` | **Output:** `results/posh_results.json`

HUD's annual census of ~5.1 million subsidized housing units. Key fields in output: `national_summary` (total units, disability rates, estimated disabled households), `by_program` (program-level breakdowns for HCV, Project-Based Section 8, Public Housing, Section 811, Section 202, Mod Rehab).

## REAC/NSPIRE Physical Inspection Scores

**Files:** `data/public_housing_physical_inspection_scores.xlsx`, `data/multifamily_physical_inspection_scores.xlsx` | **Script:** `scripts/reac_analysis.py` | **Output:** `results/reac_results.json`

HUD REAC inspection scores for 34,649 properties (6,190 public housing, 28,459 multifamily). Key fields in output: `inspection_overview` (property counts, score distributions, failure rates), `nspire_transition_insight` (UPCS vs. NSPIRE failure rate comparison), `accessibility_keyword_search` (verification that no accessibility fields exist in published schema).
