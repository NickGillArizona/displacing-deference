# Pro se vs. represented pleading-failure mechanism divergence

## Scope and inputs

- Data source: `data/FHA_Unified_Database.json`, joined to `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_merged.json` and checked against `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_results.json`.
- Existing disability-wave classifications were carried forward from `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`.
- The missing screened disability pleading-loss remainder was queued through `results/screened_disability_pleading_loss_missing_source_files.txt` and classified through the repo-local OpenRouter runner, with consolidated final gap codings saved at `results/unified_overnight_openrouter_screened_disability_pleading_loss_gap_final_results.json`.
- Supporting handoff artifacts now distinguish raw lookup-row counts from deduped unique `source_file` counts: `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_build_audit.json` and `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_id_lookup_deduped_by_source_file.json`.
- Some merge artifacts point to `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/FHA_Unified_Database.json` instead of repo-local `data/FHA_Unified_Database.json`; the build audit records that those inputs are SHA-256 identical, so the difference is path drift rather than data drift.
- Pleading-stage loss is defined as `procedural_posture` in `{MOTION_TO_DISMISS, SCREENING_ORDER}` and `outcome` in `{DEFENDANT_WIN, PROCEDURAL}`.
- Representation status comes from the `pro_se` boolean; rows with unknown representation are retained descriptively but excluded from inferential tests.

## Universe and coverage

| Measure | Value |
| --- | --- |
| Screened disability cases | 1770 |
| Full screened disability pleading-loss universe | 676 |
| Previously covered disability-wave pleading-loss subset | 535 |
| Newly added pre-wave / unassigned remainder | 141 |
| Classified full-universe target cases | 676/676 |
| Full-universe classification coverage | 100.0% |
| Residual uncoded remainder | 0 |
| No-failure / claim-survives codings in full target set | 26 |

| Cohort | Target cases | Pro se | Represented | Unknown | Pro se share |
| --- | --- | --- | --- | --- | --- |
| PRE_WAVE | 141 | 113 | 28 | 0 | 80.1% |
| P1 | 239 | 203 | 36 | 0 | 84.9% |
| P2 | 96 | 81 | 14 | 1 | 84.4% |
| P3 | 200 | 187 | 13 | 0 | 93.5% |

The exact broadening step is now explicit: the old p2 memo covered 535 disability-wave pleading-loss cases, while the full screened disability pleading-loss universe contains 676. The newly added remainder contributes 141 older pre-wave cases, and the residual uncoded remainder is 0.

## Full screened disability pleading-loss universe

Using the broadened full-universe raw case-level target set (n = 676), the mechanism mix differs materially by representation status.

- Raw full-universe collapsed test: χ²(8) = 33.229579, p = 5.5989428e-05, Cramér's V = 0.221876. Kept labels: REQUEST_NOT_ALLEGED, ELEMENTS_NOT_TIED_TO_FACTS, JURISDICTION_OR_STANDING, MIXED, DISABILITY_NEXUS_MISSING, ADVERSE_ACTION_NOT_CONNECTED, NO_COGNIZABLE_FHA_THEORY, COMPARATOR_OR_INTENT_GAP + OTHER.
- Strict-failure full-universe sensitivity test: χ²(7) = 33.104928, p = 2.5310969e-05, Cramér's V = 0.225852. Kept labels: REQUEST_NOT_ALLEGED, ELEMENTS_NOT_TIED_TO_FACTS, JURISDICTION_OR_STANDING, MIXED, DISABILITY_NEXUS_MISSING, ADVERSE_ACTION_NOT_CONNECTED, NO_COGNIZABLE_FHA_THEORY + OTHER.

These collapsed χ² readouts use adaptive top-n-plus-OTHER sparse-cell reduction for inference; the full uncollapsed contingency tables remain in `results/pro_se_mechanism_divergence_results.json`.

Top mechanisms among pro se cases:

| Mechanism | Count | Share |
| --- | --- | --- |
| REQUEST_NOT_ALLEGED | 97 | 16.6% |
| ELEMENTS_NOT_TIED_TO_FACTS | 83 | 14.2% |
| JURISDICTION_OR_STANDING | 63 | 10.8% |
| DISABILITY_NEXUS_MISSING | 59 | 10.1% |
| MIXED | 59 | 10.1% |

Top mechanisms among represented cases:

| Mechanism | Count | Share |
| --- | --- | --- |
| JURISDICTION_OR_STANDING | 25 | 27.5% |
| CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS | 13 | 14.3% |
| ELEMENTS_NOT_TIED_TO_FACTS | 12 | 13.2% |
| ADVERSE_ACTION_NOT_CONNECTED | 10 | 11.0% |
| MIXED | 8 | 8.8% |

Strict-failure divergence by mechanism:

| Mechanism | Pro se share | Represented share | Gap (pro se - represented) | Odds ratio | Overrepresented in |
| --- | --- | --- | --- | --- | --- |
| REQUEST_NOT_ALLEGED | 17.0% | 5.1% | +11.9 pp | 3.40 | pro se |
| COMPARATOR_OR_INTENT_GAP | 6.5% | 2.6% | +3.9 pp | 2.15 | pro se |
| NO_COGNIZABLE_FHA_THEORY | 7.5% | 3.8% | +3.7 pp | 1.78 | pro se |
| STATUTORY_HOOK_UNCLEAR | 6.1% | 2.6% | +3.6 pp | 2.02 | pro se |
| DISABILITY_NEXUS_MISSING | 10.3% | 7.7% | +2.6 pp | 1.29 | pro se |
| JURISDICTION_OR_STANDING | 11.0% | 32.1% | -21.0 pp | 0.26 | represented |
| ADVERSE_ACTION_NOT_CONNECTED | 9.3% | 12.8% | -3.5 pp | 0.67 | represented |
| ELEMENT_MISMATCH | 0.0% | 1.3% | -1.3 pp | 0.05 | represented |

At the family level, `TRANSLATION` accounts for 48.3% of pro se strict failures versus 17.9% of represented strict failures, while `PROCEDURAL_GATEWAY` accounts for 18.2% of pro se strict failures versus 37.2% of represented strict failures.

## Previously covered disability-wave subset (comparison)

The previously analyzed disability-wave subset remains 535 cases. Broadening the universe does not replace that tranche; it nests it inside the larger full-universe result.

- Raw disability-wave collapsed test: χ²(5) = 19.597706, p = 0.001486617624, Cramér's V = 0.191572. Kept labels: REQUEST_NOT_ALLEGED, ELEMENTS_NOT_TIED_TO_FACTS, JURISDICTION_OR_STANDING, ADVERSE_ACTION_NOT_CONNECTED, DISABILITY_NEXUS_MISSING + OTHER.
- Strict-failure disability-wave sensitivity test: χ²(3) = 25.774633, p = 1.0631859e-05, Cramér's V = 0.224149. Kept labels: REQUEST_NOT_ALLEGED, ELEMENTS_NOT_TIED_TO_FACTS, JURISDICTION_OR_STANDING + OTHER.

## Newly added pre-wave / unassigned remainder

| Cohort | Target cases | Pro se | Represented | Unknown | Pro se share |
| --- | --- | --- | --- | --- | --- |
| PRE_WAVE | 141 | 113 | 28 | 0 | 80.1% |

All newly added cases fall outside the P1/P2/P3 disability-wave window: the added tranche contains 141 cases, of which 141 are pre-wave and 0 are unassigned by date.

- Raw added-tranche collapsed test: χ²(3) = 9.384572, p = 0.024591558067, Cramér's V = 0.257987. Kept labels: MIXED, DISABILITY_NEXUS_MISSING, STATUTORY_HOOK_UNCLEAR + OTHER.
- Strict-failure added-tranche sensitivity test: χ²(2) = 3.103499, p = 0.211876952882, Cramér's V = 0.151062. Kept labels: MIXED, DISABILITY_NEXUS_MISSING + OTHER.

Both added-tranche χ² readouts still trigger a sparse-cell caution (`low_expected_cells` > 0 in both tests), so these inferential results should be read as directional rather than clean confirmatory estimates.

## Quality-control note

The broadened full-universe target set contains 26 cases coded as `NO_FAILURE_*` or `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS` even though the case-level filter marks them as pleading-stage defendant/procedural outcomes. Those are retained in the raw reproducibility tables but excluded from the strict-failure sensitivity read.

Residual uncoded remainder: 0. If this is nonzero, the exact source files are listed under `quality_flags.missing_classification_rows` in the JSON output.

For handoff, note that the raw consolidated lookup files count custom-id rows rather than deduped cases: the combined lookup has 682 raw rows mapping to 676 unique `source_file`s, and the gap-final lookup has 147 raw rows mapping to 141 unique `source_file`s because 6 rerun custom IDs duplicate already covered cases. The build audit and deduped lookup artifact make that distinction explicit.

## Bottom line

Broadened to the full screened disability pleading-loss universe, the core story still holds within this pleading-loss sample: pro se and represented cases sort into a different mechanism mix. Pro se strict pleading losses remain disproportionately concentrated in translation failures such as unalleged requests, unclear FHA hooks, and noncognizable theories, while represented plaintiffs' remaining pleading losses skew much more toward threshold gateway defects such as jurisdiction and standing. The broader universe therefore reinforces rather than narrows the note's institutional-translation account.
