# Comprehensive Data and Methods Handoff Memo

Date: 2026-04-15
Prepared by: Hermes Agent
Audience: another LLM that needs the full disability-wave research package, including methodology, data artifacts, raw distributions, validation results, and caveats, without being forced into a narrow editorial interpretation.
Primary draft target in the workspace: `drafts/current_draft.md`
Project domain: disability-centered AFFH / FHA enforcement / verification mismatch / reinforcement-not-replication / pipeline failure.

## 0. What this memo is for

This memo is intentionally broader and less filtered than the shorter editorial handoff memos.

Its purpose is to give another LLM enough detail to:
- understand what was done,
- find the actual raw/processed data files,
- understand the coding methodology,
- see the key distributions and counts,
- inspect validation and cleanup work,
- understand what was considered strong, weak, noisy, or provisional,
- and make its own decision about how to use the material in the note.

This memo is not trying to decide the final editorial use for the next LLM. It is trying to expose the full package clearly enough that the next LLM can decide how to implement it.

## 1. Short orientation

This research package centers on a completed disability-wave coding project run over a subset of the FHA Unified Database.

The disability-wave subset is a tranche of disability-related, screened-in FHA cases placed into the note’s P1 / P2 / P3 temporal framework. The coding was done using a structured overnight schema via a repo-local OpenRouter runner. The run was completed, repaired, rerun where necessary, and finally merged back onto the unified database.

The most important point for a receiving LLM:
- the disability-wave work is no longer an in-progress experiment.
- it now exists as a fully resolved 1330-case tranche with supporting validation, cleanup, and follow-on memos.

## 2. Read order for a receiving LLM

If you want the full context before using this package, the safest read order is:

1. `control_plane/CURRENT_WORK_ORDER.md`
2. `control_plane/STANDING_EDITOR_DIRECTIVES.md`
3. `control_plane/DECISION_LEDGER.md`
4. `drafts/current_draft.md`
5. `results/LLM_HANDOFF_RESEARCH_MEMO.md`
6. `results/master_editorial_packet_disability_wave.md`
7. this memo
8. `.hermes/plans/disability-wave-revision-plan.md`
9. `results/disability_wave_final_empirical_support_memo.md`
10. `results/composition_tension_resolution_memo.md`
11. validation / public-process memos listed below

If you only need the data/methods package, you can start with sections 3 through 10 of this memo.

## 3. Core artifact inventory

### 3.1 Final raw / merged result files

These are the core machine-readable outputs.

1. Final resolved raw result rows
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`
- This is the most important case-level result file.
- It contains one row per resolved disability-wave case, including:
  - `source_file`
  - `custom_id`
  - `case_name`
  - token usage
  - `provider_trace`
  - `classification` object

2. Final resolved merged file
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json`
- This merges the final resolved classification rows back onto the unified FHA database record structure.

3. Final resolved merge report
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merge_report.md`
- This is the cleanest quick report for final tranche size and major distributions.

### 3.2 Methodology / execution files

4. Methodology memo
- `results/unified_overnight_openrouter_disability_wave_r1_methodology.md`

5. Execution memo
- `results/unified_overnight_openrouter_disability_wave_r1_execution_memo.md`

6. Original disability-wave methodology memo (non-r1-specific path)
- `results/unified_overnight_openrouter_disability_wave_methodology.md`

7. Original disability-wave execution memo (non-r1-specific path)
- `results/unified_overnight_openrouter_disability_wave_execution_memo.md`

### 3.3 Rerun / repair artifacts

8. Error rerun outputs
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_results.json`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_errors.json`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_status.md`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_methodology.md`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_execution_memo.md`

9. Remaining-error rerun outputs
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_remaining_v2_results.json`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_remaining_v2_errors.json`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_remaining_v2_status.md`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_remaining_v2_methodology.md`
- `results/unified_overnight_openrouter_disability_wave_r1_errors_rerun_remaining_v2_execution_memo.md`

10. Manual salvage file for the last 2 unresolved records
- `results/unified_overnight_openrouter_disability_wave_r1_manual_salvage_results.json`

### 3.4 Queue / validation / follow-on files

11. Priority validation memo
- `results/disability_wave_validation_priority_memo.md`

12. Top-12 validation results
- `results/disability_wave_top12_validation_results.md`

13. Public-process validation pass 2
- `results/disability_wave_public_process_validation_pass2.md`

14. Noisy queue cleanup memo
- `results/disability_wave_noisy_queue_cleanup_memo.md`

15. Public-process follow-on memo
- `results/public_process_follow_on_memo_v2.md`

16. Public-process raw-text study memo
- `results/public_process_raw_text_study_memo.md`

17. Final empirical support memo
- `results/disability_wave_final_empirical_support_memo.md`

18. Composition-tension memo
- `results/composition_tension_resolution_memo.md`

19. Master editorial packet
- `results/master_editorial_packet_disability_wave.md`

20. Broad handoff memo
- `results/LLM_HANDOFF_RESEARCH_MEMO.md`

21. Paste-ready prompt
- `results/LLM_HANDOFF_PASTE_READY_PROMPT.md`

### 3.5 Queue data files

22. Rerun / validation / public-process queue files
- `results/disability_wave_r1_error_rerun_queue.json`
- `results/disability_wave_r1_error_partial_json_queue.json`
- `results/disability_wave_r1_error_empty_output_queue.json`
- `results/disability_wave_r1_error_2400_cap_queue.json`
- `results/disability_wave_r1_low_confidence_queue.json`
- `results/disability_wave_r1_high_review_queue.json`
- `results/disability_wave_r1_public_gap_queue.json`
- `results/disability_wave_r1_priority_validation_queue.json`

## 4. Dataset scope and final resolved status

From the final resolved merge report:
- DB record count: 3198
- Matched disability-wave record count: 1330
- Unmatched record count: 1868
- Orphan result count: 0
- Malformed parsed responses logged: 0
- Hard errors logged: 0

Important clarification:
- The 1868 unmatched records are not merge failures.
- They are simply outside this disability-wave tranche.

The disability-wave tranche is therefore fully resolved.

## 5. Methodology summary

### 5.1 Scope

The repo-local OpenRouter path classified the overnight schema against:
- `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/FHA_Unified_Database.json`

The runner reused the existing overnight structured prompt shape, not the older Java full-text extraction pipeline.

The output was constrained to the overnight schema fields expected by downstream merge and memo scripts.

### 5.2 Subset types supported by the runner

The runner supported these subsets:
- `pilot`: deterministic balanced sample across P1/P2/P3 from the disability-wave population
- `disability-wave`: all screened disability cases with dated P1/P2/P3 placement
- `all-screened`: all screened cases with resolved outcomes

The disability-wave package discussed in this memo is the completed `disability-wave` tranche.

### 5.3 Models used

Methodology memos indicate:
- Primary bulk model: `moonshotai/kimi-k2.5`
- Optional escalation model: `z-ai/glm-5.1`
- reasoning budget: 0 for both lanes in the stabilized runner
- stabilized max output tokens in the methodology file: 2400

However, there is an important procedural nuance:
- after length/truncation failures, later reruns used higher output ceilings (including 3200-token rerun settings) for targeted error recovery.
- the final resolved result file therefore contains a mixture of original-run results, rerun results, and two manually salvaged rows.

### 5.4 Runtime behavior

The methodology file says:
- requests were built once and stored as JSONL
- each request got a stable `custom_id` from `source_file`
- the runner was resumable: existing completed IDs in `results`, `errors`, and `malformed` were skipped automatically
- OpenRouter calls ran concurrently through `httpx.AsyncClient` and `asyncio`
- checkpoint writes occurred after each completion

### 5.5 Budget logic

Execution / methodology memos record:
- Kimi pricing hard-coded at $0.45 / million input tokens and $2.20 / million output tokens
- disability-wave size estimated at 1330 records
- Kimi-only base estimate for the disability-wave was approximately $4.27
- GLM 5.1 was treated as a bounded escalation lane, not the primary bulk path

## 6. Repair / rerun history

The final 1330-case resolved tranche was not produced in one clean pass. It required staged repair.

### 6.1 Initial full run
The initial disability-wave run completed with a large successful tranche but some hard errors.

### 6.2 Error diagnosis
The main problems encountered were length / truncation related and parser failures. These produced:
- partial JSON truncation
- empty raw outputs from both models for some rows
- filename-selection edge cases in the rerun mechanism because some `source_file` names contained commas

### 6.3 Reruns
The hard-error tranche was rerun in two main waves:
- first rerun recovered 53 of 54 in its selected tranche
- second rerun recovered 19 of 20 in the comma-containing filename tranche after the runner was patched to support `--only-source-files @file.txt`

### 6.4 Manual salvage
The final two unrecovered rows were manually salvaged from:
- truncated rerun output,
- Unified_Claims_Extraction.json,
- and available underlying opinion text.

Those rows were then added via:
- `unified_overnight_openrouter_disability_wave_r1_manual_salvage_results.json`

## 7. Final data distributions

### 7.1 Pleading-failure family distribution

From the final resolved merge report / aggregated case-level results:
- NO_FAILURE_PLAINTIFF_WIN: 374
- TRANSLATION: 268
- PROCEDURAL_GATEWAY: 240
- CAUSAL_LINK: 96
- NO_FAILURE_DEFENDANT_WIN: 87
- ELEMENT_MISMATCH: 72
- MIXED: 66
- MERITS_EVIDENCE: 58
- UNCLEAR: 45
- FACTUAL_DETAIL: 24

Key combined comparison:
- TRANSLATION + PROCEDURAL_GATEWAY = 508 (38.2%)
- MERITS_EVIDENCE + FACTUAL_DETAIL = 82 (6.2%)

### 7.2 Confidence distribution

- HIGH: 464
- MEDIUM: 807
- LOW: 59

### 7.3 Raw-text review priority distribution

- HIGH: 140
- MEDIUM: 1043
- LOW: 147

### 7.4 Top pleading mechanisms

Top mechanism counts from the final resolved results:
- CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS: 407
- JURISDICTION_OR_STANDING: 149
- ELEMENTS_NOT_TIED_TO_FACTS: 120
- REQUEST_NOT_ALLEGED: 113
- UNCLEAR: 108
- MIXED: 90
- DISABILITY_NEXUS_MISSING: 60
- ADVERSE_ACTION_NOT_CONNECTED: 58
- NO_COGNIZABLE_FHA_THEORY: 50
- COMPARATOR_OR_INTENT_GAP: 44
- EXHAUSTION_OR_PRECLUSION: 33
- TECHNICAL_PROOF_GAP: 30
- LIMITATIONS_OR_TIMELINESS: 28
- STATUTORY_HOOK_UNCLEAR: 25
- TIMING_OR_NOTICE_GAP: 10
- INTERACTIVE_PROCESS_BREAKDOWN: 2
- ELEMENT_MISMATCH: 2
- POLICY_OR_PRACTICE_NOT_SPECIFIED: 1

### 7.5 Most common missing institutional functions

- THEORY_SELECTION: 683
- FACT_DEVELOPMENT: 681
- DOCUMENT_ASSEMBLY: 480
- JURISDICTIONAL_TRIAGE: 322
- NONE_APPARENT: 296
- MEDICAL_OR_DISABILITY_CORROBORATION: 127
- ADMINISTRATIVE_RECORD_BUILDING: 94
- INTAKE_SCREENING: 73
- NEGOTIATION_OR_INTERACTIVE_PROCESS_SUPPORT: 66
- EXPERT_OR_TECHNICAL_TRANSLATION: 63
- COMPARATOR_DEVELOPMENT: 50
- UNCLEAR: 18

### 7.6 Most common administratively observable fact patterns

- NOTICE_OR_TIMELINE_RECORD: 979
- DOCUMENTED_REQUEST: 875
- PUBLIC_PROGRAM_RULE_OR_DECISION: 452
- LEASE_OR_POLICY_TEXT: 296
- MEDICAL_OR_PROVIDER_LETTER: 277
- DENIAL_OR_NO_RESPONSE_RECORD: 272
- HEARING_OR_GRIEVANCE_RECORD: 250
- PHYSICAL_ACCESS_BARRIER: 137
- COMPARATOR_OR_PATTERN_EVIDENCE: 95
- NONE_APPARENT: 83
- UNCLEAR: 55
- INSPECTION_OR_MEASUREMENT_DATA: 54

### 7.7 Doctrinal-gap counts

- LOW: 611
- MEDIUM: 410
- NONE: 289
- HIGH: 20

### 7.8 Fixability counts

- BOTH: 714
- TIER2_INSTITUTIONAL_INTERMEDIATION: 300
- NEITHER: 278
- UNCLEAR: 31
- TIER1_REPORTING_ARCHITECTURE: 7

### 7.9 Public-process flag

- public_process_failure_flag = true: 531
- percent of tranche: 39.9%

### 7.10 Reasoning length metadata

From the final resolved results:
- mean reasoning length: 558.8 characters
- median reasoning length: 549.5 characters

### 7.11 Primary model provenance in the final resolved file

Approximate counts by first provider_trace model:
- moonshotai/kimi-k2.5: 1326
- z-ai/glm-5.1: 2
- manual_salvage_from_partial_and_case_text: 2

Interpretation:
- almost all final rows originate from Kimi-primary executions, whether or not escalation was used later in the provider trace.

## 8. Main interpretive claims that prior memos drew from these data

This section reports what prior memos concluded, not what a future LLM must conclude.

### 8.1 The dominant interpretive line in prior memos

Prior memos repeatedly argued that:
- the disability docket is dominated by failed conversion of grievances into viable claims,
- many disputes are administratively legible in principle,
- complaint-driven enforcement underperforms because institutions fail to capture, standardize, verify, and route recurring disability-relevant facts,
- and public/quasi-public process settings are a major part of that story.

### 8.2 Composition tension

A major refinement from the broader synthesis work:
- composition remains the dominant aggregate explanation,
- but some within-group deterioration also appears, especially in stronger represented pleading-stage subsets.

That point is developed in:
- `results/composition_tension_resolution_memo.md`

### 8.3 Administrative invisibility refinement

Earlier draft language leaned toward “administrative invisibility.”
Later memos refined this into:
- qualified administrative invisibility,
- failed administrative capture and verification,
- or recurring facts that exist in principle but are not systematically gathered and routed.

## 9. Validation and cleanup results

### 9.1 Why validation mattered

The queue-level outputs contained noise. Some records flagged as interesting examples were later shown to be:
- early procedural orders,
- service orders,
- counsel-denial orders,
- incomplete screening / recommit orders,
- or likely false positives for the core FHA/public-process story.

So a receiving LLM should not assume every queued case is a note-facing merits example.

### 9.2 Top-12 validation pass

From `disability_wave_top12_validation_results.md`:
- 8 of the 12 checked records were early procedural orders or otherwise non-merits records
- 7 should be kept only as context/non-merits tracking
- 1 likely false positive should be recoded out of the FHA merits pool
- only 1 record in the twelve (`Sykes`) emerged as a strong, clean substantive public-process merits example
- `Wissman` and `Goodwin` remained usable only with narrower mechanism descriptions
- `Capel` remained provisional unless validated against a district-court opinion

### 9.3 Noisy queue cleanup

The following were explicitly reviewed and should be treated as context-only, not substantive support:
- Jacobson
- Rosa
- Chapman
- Sandles
- Shepherd
- Avila

Reason:
- service orders,
- counsel-denial orders,
- or incomplete screening-stage orders that do not adjudicate substantive FHA issues.

### 9.4 Second public-process validation pass

From `disability_wave_public_process_validation_pass2.md`:

Strong keep:
- Jackson
- Drummer

Strong but needs recoding:
- Fedynich

Usable with caution / mechanism recode:
- Cooper

Weak public-process example:
- Johnson

Likely false positive / recode out of core FHA public-process counts:
- Peters

## 10. Example-status table for another LLM

### 10.1 Strongest validated examples

- Sykes
  - strongest clean public-process example
  - good for administratively observable facts that never become a legally sufficient FHA claim

- Jackson
  - validated public-process example
  - useful for wrong-defendant / institutional attribution failure in voucher context

- Drummer
  - validated public-process example
  - useful for a rich administrative record that remains legally disorganized

### 10.2 Valid but needs careful framing

- Fedynich
  - useful public-process example
  - should be described as disability/nexus translation failure, not request absence

- Cooper
  - usable with caution
  - better read as causation / knowledge failure in retaliation/public-housing setting, not request-articulation failure

- Wissman
- Goodwin
  - usable only with narrower mechanism descriptions

### 10.3 Weak / provisional / context-only examples

- Johnson
- Peters
- Capel (provisional)
- Jacobson
- Rosa
- Chapman
- Sandles
- Shepherd
- Avila

## 11. Existing synthesis / planning memos and what each does

### 11.1 Best memo for final tranche-level empirical support
- `results/disability_wave_final_empirical_support_memo.md`
- Best if you want the main distributions and the strongest research-backed empirical claims.

### 11.2 Best memo for final editorial synthesis
- `results/master_editorial_packet_disability_wave.md`
- Best if you want the whole package translated into revision priorities.

### 11.3 Best memo for revision planning
- `.hermes/plans/disability-wave-revision-plan.md`
- Section-by-section revision roadmap.

### 11.4 Best memo for public-process follow-on work
- `results/public_process_raw_text_study_memo.md`
- plus `results/disability_wave_public_process_validation_pass2.md`

### 11.5 Best memo for validation / exclusion discipline
- `results/disability_wave_validation_priority_memo.md`
- `results/disability_wave_top12_validation_results.md`
- `results/disability_wave_noisy_queue_cleanup_memo.md`

### 11.6 Best memo for another LLM’s quick orientation
- `results/LLM_HANDOFF_RESEARCH_MEMO.md`

## 12. What another LLM could do with this package

This memo is not telling the next LLM what it must conclude. It is telling the next LLM what exists.

Possible uses include:
- revising the current draft using tranche-level findings,
- writing a fresh editorial synthesis,
- extracting tables or support propositions,
- reassessing the note’s empirical framing,
- building a more detailed appendix,
- or comparing the disability-wave package against other research memos in the workspace.

## 13. Key cautions for another LLM

1. Do not confuse the raw result file with the filtered editorial packet.
2. Do not assume every queue record is a valid note-facing merits example.
3. Do not assume public-process examples are equally strong.
4. Do not assume the disability-wave results prove a broad judicial-hostility thesis.
5. Do not assume composition is the whole story without reading the composition-tension memo.
6. Do not assume the broader Massachusetts / Connecticut registry design memo should automatically drive the current note.

## 14. Minimal one-paragraph reuse summary

The completed disability-wave package now consists of a fully resolved 1330-case tranche merged back onto the FHA Unified Database, supported by methodology, validation, and editorial synthesis memos. The final distributions show that translation and procedural-gateway failures together account for 38.2% of cases, while merits-evidence and factual-detail failures account for 6.2%. The most common missing institutional functions are theory selection, fact development, document assembly, and jurisdictional triage, while administratively observable fact patterns such as requests, timelines, denials, policy texts, and public-program decisions recur at high rates. Public-process failure appears in 39.9% of the tranche. Validation work also showed that some queued examples are early procedural noise or weak/false-positive public-process cases, so any future use of individual examples should be more selective than use of tranche-level distributions.
