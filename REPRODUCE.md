# Reproducing the Empirical Findings

This file maps each headline empirical claim in the accompanying article to the script that produces it and the artifact the script writes. Run everything from the repository root with Python 3.11+ and the dependencies in `requirements.txt`.

## Quick start

```bash
pip install -r requirements.txt

# From repo root, each script writes into results/
python scripts/h1_h2_analysis.py          # Claim specificity + representation x complexity
python scripts/h5_analysis.py             # Institutional plaintiff hierarchy
python scripts/h6_analysis.py             # Physical evidence
python scripts/h7_analysis.py             # Three-period trajectory
python scripts/h8_analysis.py             # Private-enforcement adequacy by claim type
python scripts/robustness_bootstrap.py    # 10,000-resample bootstrap CIs (seed 42)
python scripts/decomposition.py           # Kitagawa + Oaxaca-Blinder decomposition
python scripts/robustness_checks.py       # Reclassification + period-boundary sensitivity
```

Scripts resolve paths through `scripts/config.py`, which reads `FHA_DATA_DIR` (default `./data/`) and writes into `./results/`. No hardcoded absolute paths.

## Claim -> artifact map

### Composition-effect headline (Section IV.A of empirical note)

| Claim | Script | Output (key) | Point value | Note value |
|---|---|---|---|---|
| Aggregate strict-win rate P1 | `robustness_bootstrap.py` | `bootstrap_ci_results.json` `point_estimates_by_period.P1.strict_win_rate` | 0.180 | 18.0% |
| Aggregate strict-win rate P3 | " | `point_estimates_by_period.P3.strict_win_rate` | 0.114 | 10.7% |
| Pro se share P1 | " | `point_estimates_by_period.P1.pro_se_share` | 0.597 | 58.9% |
| Pro se share P3 | " | `point_estimates_by_period.P3.pro_se_share` | 0.778 | 76.7% |
| Represented strict-win P1 | " | `point_estimates_by_period.P1.represented_strict_win` | 0.340 | 34.3% |
| Represented strict-win P3 | " | `point_estimates_by_period.P3.represented_strict_win` | 0.361 | 34.3% |
| Composition share (broad-win, avg) | `decomposition.py` | `decompositions.P1_to_P3_broad.kitagawa.average.composition_share` | 0.769 | 76% |

### Bootstrap CIs (Section V.A)

| Claim | Output key | Reproduced (95% percentile) | Note (95% CI) |
|---|---|---|---|
| Represented strict-win P1 | `bootstrap_ci.P1_represented_strict_win` | [0.273, 0.408] | [27.6%, 41.4%] |
| Represented strict-win P3 | `bootstrap_ci.P3_represented_strict_win` | [0.253, 0.472] | [23.9%, 46.3%] |
| Pro se share P1 | `bootstrap_ci.P1_pro_se_share` | [0.553, 0.640] | [55.0%, 62.8%] |
| Pro se share P3 | `bootstrap_ci.P3_pro_se_share` | [0.732, 0.824] | [72.7%, 80.8%] |

### Hypothesis tests (Section IV.B)

| Claim | Script | Output | Note value |
|---|---|---|---|
| Specific-duty broad-win rate | `h1_h2_analysis.py` | `h1_h2_results.json` `enacted_duty_flag` crosstab | 39.3% |
| Open-textured broad-win rate | " | " | 1.0% |
| Specificity OR | " | `enacted_duty` logit `or` | ~12.33 |
| Institutional plaintiff hierarchy | `h5_analysis.py` | `h5_results.json` | see Table 3 |
| Physical evidence OR | `h6_analysis.py` | `h6_results.json` `phys_evidence.or` | 1.63 |
| MTD survival by period x representation | `h7_analysis.py` | `h7_results.json` `model1_mtd_survival` | rep ~82% stable |
| Private-enforcement adequacy by claim type | `h8_analysis.py` | `h8_results.json` | varies |

### PUMS cross-tabulations (Section IV.C)

| Claim | Script | Output | Note value |
|---|---|---|---|
| Disability cost-burden penalty (race decomposition) | `pums_extended_crosstabs.py` | `extended_crosstabs_results.json` | 7.3-16.9 pp |
| Housing stock concentration | `pums_housing_stock_analysis.py` | `housing_stock_results.json` | see Table 4 |
| Pre-1991 statutory gap analysis | `pums_pre1991_gap_analysis.py` | `pre1991_statutory_gap_analysis.json` | see Appendix |

### HUD administrative findings (Section IV.C.1)

| Claim | Script | Output | Note value |
|---|---|---|---|
| CDBG activity-code accessibility gap | `cdbg_analysis.py` + `cdbg_accessibility_gap_analysis.py` | `cdbg_results.json`, `cdbg_accessibility_gap_quantification.md` | 2 of ~100 matrix codes are disability-specific |
| NSPIRE/REAC physical inspection gap | `reac_analysis.py` | `reac_results.json` | see Table 5 |
| POSH subsidized-housing disability rates | `posh_analysis.py` | `posh_results.json` | 39.3% weighted household rate |
| AHS 2023 accessibility module | `ahs_2023_accessibility_analysis.py` | `ahs_2023_accessibility_results.json` | see Section IV.C |

### Doctrinal / qualitative analyses

| Claim | Script | Output |
|---|---|---|
| Iqbal/Twombly application at pleading gate | `fha_iqbal_analysis.py` | `extended_doctrinal_analysis.json` |
| Circuit-level variation in outcomes | `circuit_district_deep_dive.py` | `circuit_district_deep_dive_results.json` |
| Public-defendant process-claim underperformance | `public_defendant_analysis.py` | `public_defendant_process_failure_results.json` |
| Pro se pleading-mechanism divergence | `pro_se_mechanism_analysis.py` | `pro_se_mechanism_divergence_results.json` |
| LIHTC 50-state QAP accessibility audit | `lihtc_accessibility_audit.py`, `qap_accessibility_2025_2026_scan.py` | `lihtc_accessibility_audit_results.json`, `qap_accessibility_2025_2026.json` |

### Doctrinal audit memoranda (v100 footnote apparatus)

The Note's footnote-level citations rely on fourteen human-authored audit memoranda that document Westlaw queries, Federal Register and reginfo.gov records, HUD report coding, and ACS / POSH derivations. Each memorandum states its query / source, run date, and inclusion rule. Methodology and file-to-footnote crosswalk are in [`appendices/Appendix_M_Doctrinal_Audit_Methodology.md`](appendices/Appendix_M_Doctrinal_Audit_Methodology.md).

| Note claim | Audit file | Section(s) |
|---|---|---|
| Part 121 / DOJ § 3604(f)(3) population audit | `results/westlaw_part121_doj_audits_2026-04-18.md` | M.2.1 |
| § 3614a 42-opinion audit | `results/westlaw_3614a_audit_2026-04-18.md` | M.2.2 |
| Part 121 eCFR / Federal Register / ICR verification | `oira_harvest/cfr_part121_analysis.md` | M.3 |
| 2022–2023 HUD-27061 PRA record | `results/verification_hud27061_2022_supporting_statement.md` | M.4 |
| AFFH-T disability-visualization gap | `results/affh_t_disability_visualization_gap_audit.md` | M.5 |
| NSPIRE / UFAS § 504 17-category crosswalk | `results/nspire_ufas_crosswalk_analysis.md` | M.6 |
| Part 8 stock-level verification gap + pre-1991 stock share | `results/pre_1991_stock_hardening.md` | M.7 |
| 1988 FHAA preamble disability-data passages | `results/1988_fhaa_legislative_history_disability_data.md` | M.8 |
| LIHTC QAP 51-jurisdiction audit | `results/qap_accessibility_update_analysis.md` | M.9 |
| 676-case pro se mechanism divergence | `results/pro_se_mechanism_divergence_analysis.md` | M.10 |
| 47-AFH disability-depth audit | `results/analysis_of_impediments_disability_audit.md` | M.11 |
| FY 1989 – FY 2023 HUD annual report longitudinal audit | `results/hud_annual_report_longitudinal_audit.md` | M.12 |
| HMDA disclosure-effect meta-analysis | `results/disclosure_effect_meta_analysis.md` | M.13 |
| Australia SDA comparative note | `results/australia_sda_analysis.md` | M.14 |

## Known numerical gaps flagged by reproduction run

Running the current scripts against the committed `data/FHA_Unified_Database.json` surfaces a few minor gaps worth documenting before final submission:

1. **Strict-win decomposition shares.** The note reports "73 percent composition-first, 77 percent rate-first, averaged approximately 76 percent" for the strict-win aggregate decline (Section IV.A). `decomposition.py` produces 73.8% (composition-first) and 87.2% (rate-first), averaging 80.5%, on the same strict_win outcome. The **broad_win** decomposition averages to 76.9%, matching the note's 76% headline. Review whether the note text should specify that the 76% figure is the broad-win (plaintiff-wins + mixed) decomposition and report strict-win separately as 73%-80%.

2. **Dated-decided N.** The note's Section III.A reports "P1: n = 615, 456 decided; P2: n = 159, 116 decided; P3: n = 417, 317 decided" (1,191 dated, 889 decided). Current scripts produce 911 decided against the committed database (P1=467, P2=120, P3=324). This is a 22-case drift, most likely reflecting reclassification after the note's data snapshot. Decide whether the note's numbers should be updated to the current snapshot or whether the note should cite the specific snapshot date and commit hash.

3. **Institutional plaintiff win rates.** `h5_results.json` yields Government broad win ~86-87% and Fair Housing Org broad win ~60-67%. The note (Table 3) reports 90.0% and 67.7%. The 3-7 pp gap likely reflects the sample-definition difference: the note appears to include undated cases (n=1,720) while the current h5 run filters more tightly. Either reconcile definitions or add a footnote specifying which population Table 3 summarizes.

## Data-snapshot discipline

The empirical note should pin the specific `FHA_Unified_Database.json` snapshot it reports against. Recommended additions to the methods section:

- Repository commit hash used for the numbers (e.g., "numbers reported in this article correspond to commit `<sha>` of https://github.com/NickGillArizona/displacing-deference").
- SHA-256 of `data/FHA_Unified_Database.json` at that commit.
- Date of data collection cutoff (already in the note as "data-collection endpoint").

These three items let any reader regenerate the exact numbers. Otherwise small reclassification drift between snapshots (e.g., the 22-case gap above) can look like a reproducibility failure.

## Dependencies

See `requirements.txt`. Core: pandas, numpy, statsmodels, scipy. Python 3.11+ recommended.

## Questions

Open an issue or email the author (see `CITATION.cff`).
