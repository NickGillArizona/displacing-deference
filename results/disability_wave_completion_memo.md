# Disability-Wave Completion Audit Memo

Generated: 2026-04-16T03:32:15Z
Repo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH`

## Bottom line

I re-audited the disability-wave tranche against the current repo-local inputs and confirmed that the tranche is already complete. Applying the `scripts/unified_overnight_openrouter.py` disability-wave subset logic to `data/FHA_Unified_Database.json` yields 1,330 eligible cases, and `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json` already contains 1,330 classified results covering the same 1,330 unique `source_file` values.

Because the verified gap is zero, I did not run a new OpenRouter completion job, did not run the completion-prefix status command, and did not create any `unified_overnight_openrouter_disability_wave_completion*` artifacts. The older `~440 remaining` premise does not describe the narrower disability-wave subset used by the runner here; it appears to reflect a broader or older all-disability count rather than the specifically defined subset of screened-in (`screening_result != "NO"`), outcome-resolved, non-empty-`case_name`, disability-tagged/alleged, 2022-forward records used in `scripts/unified_overnight_openrouter.py`.

## Inputs audited

- `data/FHA_Unified_Database.json`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merge_report.md`
- `scripts/unified_overnight_openrouter.py`
- `scripts/unified_overnight_merge.py`

## Audit method

I used the disability-wave selection logic implemented in `scripts/unified_overnight_openrouter.py`:

1. Keep records where `screening_result != "NO"`.
2. Require a non-empty `case_name`.
3. Require `outcome` not in `{null, "", "?"}`.
4. Require disability scope via either:
   - `protected_classes` containing a disability label, or
   - truthy `disability_alleged`.
5. Require a valid disability-wave period via `assign_period(record)`:
   - exclude records before 2022-01-01 or without a usable filing date/year;
   - P1: 2022-01-01 through 2024-06-27;
   - P2: 2024-06-28 through 2025-02-04;
   - P3: 2025-02-05 forward.

I applied that subset logic to the repo-local `data/FHA_Unified_Database.json`, then compared the resulting disability-wave `source_file` set to the `source_file` set in `unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json` and checked the merged/report artifacts for orphan results and logged errors.

Reproducibility note: this memo's subset audit uses repo-local `data/FHA_Unified_Database.json` because `scripts/unified_overnight_openrouter.py` resolves the repo-local database first. The existing final-resolved merge artifacts instead cite `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/FHA_Unified_Database.json` because `scripts/unified_overnight_merge.py` resolves the workspace-level `data/2` path first. In the audited artifacts the counts line up across those two path conventions (`DB record count = 3198`, `Matched record count = 1330`), so the path inconsistency does not change the zero-gap conclusion, but it should be noted for reproducibility.

## Audit counts

| Metric | Count |
|---|---:|
| Total DB records | 3198 |
| Records passing screening filter (`screening_result != "NO"`) | 2522 |
| Disability-wave eligible cases | 1330 |
| Existing final-resolved classified rows | 1330 |
| Unique eligible `source_file` values | 1330 |
| Unique result `source_file` values | 1330 |
| Classification gap | 0 |
| Orphan result `source_file` values | 0 |
| Duplicate result rows | 0 |
| Final-resolved matched record count | 1330 |
| Final-resolved unmatched record count | 1868 |
| Final-resolved orphan result count | 0 |

Important clarification: the 1,868 unmatched records in the final-resolved merge report are outside the disability-wave tranche, not missing disability-wave classifications.

## Completion decision

No completion rerun was needed.

- New cases classified in this task: 0
- Completion run executed: no
- Completion status command executed: no
- New completion-prefix outputs created: none
- Existing tranche status: fully resolved

## Errors encountered

- No new runtime errors were encountered in this task because no completion run was warranted.
- The existing final-resolved merge report logs `Malformed parsed responses logged = 0` and `Hard errors logged = 0`.

## Updated tranche size

The disability-wave tranche remains 1,330 cases.

## Updated distributions

Because no new rerun occurred, the tables below are unchanged carry-forwards from the existing final-resolved tranche rather than newly generated completion outputs. The family, mechanism, and public-process counts were tabulated from the existing 1,330 matched records in `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json` by counting the merged classification fields `pleading_failure_family`, `pleading_failure_mechanism`, and `public_process_failure_flag`; shares are out of 1,330.

### pleading_failure_family

| Label | Count | Share |
|---|---:|---:|
| CAUSAL_LINK | 96 | 7.2% |
| ELEMENT_MISMATCH | 72 | 5.4% |
| FACTUAL_DETAIL | 24 | 1.8% |
| MERITS_EVIDENCE | 58 | 4.4% |
| MIXED | 66 | 5.0% |
| NO_FAILURE_DEFENDANT_WIN | 87 | 6.5% |
| NO_FAILURE_PLAINTIFF_WIN | 374 | 28.1% |
| PROCEDURAL_GATEWAY | 240 | 18.0% |
| TRANSLATION | 268 | 20.2% |
| UNCLEAR | 45 | 3.4% |

### pleading_failure_mechanism

| Label | Count | Share |
|---|---:|---:|
| ADVERSE_ACTION_NOT_CONNECTED | 58 | 4.4% |
| CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS | 407 | 30.6% |
| COMPARATOR_OR_INTENT_GAP | 44 | 3.3% |
| DISABILITY_NEXUS_MISSING | 60 | 4.5% |
| ELEMENTS_NOT_TIED_TO_FACTS | 120 | 9.0% |
| ELEMENT_MISMATCH | 2 | 0.2% |
| EXHAUSTION_OR_PRECLUSION | 33 | 2.5% |
| INTERACTIVE_PROCESS_BREAKDOWN | 2 | 0.2% |
| JURISDICTION_OR_STANDING | 149 | 11.2% |
| LIMITATIONS_OR_TIMELINESS | 28 | 2.1% |
| MIXED | 90 | 6.8% |
| NO_COGNIZABLE_FHA_THEORY | 50 | 3.8% |
| POLICY_OR_PRACTICE_NOT_SPECIFIED | 1 | 0.1% |
| REQUEST_NOT_ALLEGED | 113 | 8.5% |
| STATUTORY_HOOK_UNCLEAR | 25 | 1.9% |
| TECHNICAL_PROOF_GAP | 30 | 2.3% |
| TIMING_OR_NOTICE_GAP | 10 | 0.8% |
| UNCLEAR | 108 | 8.1% |

### public_process_failure_flag

| Label | Count | Share |
|---|---:|---:|
| false | 799 | 60.1% |
| true | 531 | 39.9% |

## Files changed in this task

Updated:
- `results/disability_wave_completion_memo.md`

No new completion-prefix JSON, merge outputs, or status artifacts were created because the verified classification gap is zero.

## Conclusion

The disability-wave classification gap is already closed in the current repo state. The existing final-resolved results fully cover all 1,330 disability-wave eligible cases, with zero missing cases, zero orphan results, zero duplicate result rows, zero malformed parsed responses logged, and zero hard errors logged.
