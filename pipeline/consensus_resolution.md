# Tiered Consensus Resolution Algorithm

## Overview

Three-model outputs are consolidated into a single canonical record using a
tiered resolution strategy designed to minimize cost while preserving accuracy.

## Algorithm

### Tier 0 — Full Consensus (No API Call)
All three models return identical values for every categorical field.
→ Adopt as canonical.

### Tier 1 — Majority Agreement, Non-Critical Fields (No API Call)
Two of three models agree on all fields; dissent is limited to non-critical
fields (any field other than `outcome`, `primary_claim_type`, or `claim_types`).
→ Adopt majority value.

### Tier 2 — Majority Agreement, Critical Fields (No API Call)
Two of three models agree on `outcome`, `primary_claim_type`, or `claim_types`
but one model dissents.
→ Adopt 2-of-3 consensus.

### Tier 3 — Three-Way Split, Non-Critical → Haiku 4.5
All three models return different values for non-critical fields with no majority.
→ Submit to Haiku 4.5 (Batch API) with original case text
  and each model's answer for disputed fields.
→ Haiku determines correct classification using the same controlled vocabulary.

### Tier 4 — Three-Way Split, Critical → Sonnet 4.6
All three models return different values for `outcome`, `primary_claim_type`,
or `claim_types`.
→ Submit to Sonnet 4.6 (Batch API) with original case text
  and each model's answer.
→ Sonnet also re-extracts four free-text narrative fields fresh from source.

## Critical vs. Non-Critical Fields

**Critical fields** (require Tier 4 / Sonnet adjudication if no majority):
- `outcome`
- `primary_claim_type`
- `claim_types`

**Non-critical fields** (Tier 3 / Haiku adjudication sufficient):
- All other categorical fields (accommodation_type, defendant_type,
  disability_category, plaintiff_type, housing_type, procedural_posture, etc.)

## Free-Text Field Resolution

For narrative fields (`key_holding`, `brief_summary`, `accommodation_description`,
`key_cases_cited`):
- Tier 4 records: Sonnet re-extracts from source text
- All other records: MiniMax M2.7 version adopted (most detailed extractions)

## Output Files

- **Unified database** (`FHA_RA_Database_unified_[timestamp].json`):
  Canonical fields only + resolution metadata. ~27 fields/record.

- **Audit database** (`FHA_RA_Database_audit_[timestamp].json`):
  All three model-specific values (suffixed `_minmax`, `_deepseek`, `_kimi`)
  + canonical values + adjudication reasoning. ~91 fields/record.

## Implementation

The consensus resolution logic is implemented in:
- Java: `src/main/java/mfh/gfo/` in the [MFH-Java-Work](https://github.com/NickGillArizona/MFH-Java-Work) repository
  - `OpenRouterConfirmationClient.java` — OpenRouter API integration
  - `OpusDisagreementResolver.java` — Adjudication dispatch
  - `WestlawOutcomeAdjudicationClient.java` — Outcome adjudication
  - `WestlawClassificationNormalizer.java` — Field normalization
  - `ResultsJsonCompiler.java` — Unified/audit database compilation
