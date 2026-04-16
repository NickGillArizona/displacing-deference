# 2023 AHS Accessibility Analysis Memo

Generated: 2026-04-16T11:23:02.320184+00:00
Repo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH`

## Bottom line

The 2023 AHS national PUF does not include the dedicated Home Accessibility topical module that appeared in 2019, so the 2023 file cannot support a full Bo'sher-style three-tier accessibility replication. The 2023 PUF still supports several core accessibility-relevant measures, especially no-step entry (`NOSTEP`), disability-household status (`DISHH`, `NUMWALK`), and accessibility-motivated home improvements (`HMRACCESS`).

Using Census weights, the share of occupied units with no-step entry rose from 42.38% in 2011 to 53.57% in 2019 and 57.41% in 2023.

Among owner-occupied units in the AHS home-improvement universe, the share reporting accessibility-for-elderly-or-disabled work increased from 5.07% in 2019 to 6.18% in 2023.

## Source-discipline finding: 2023 has no dedicated home accessibility topical module

Public Census documentation matters here. The 2015-2023 AHS PUF guide lists `2019 Home Accessibility` as a Group 2 topical module but does not list any 2023 Home Accessibility module. The 2023 table-spec workbook likewise has no `Home Accessibility` sheet, unlike the 2019 workbook. That is why the 2023 analysis below relies on the remaining core variables instead of a full feature battery.

## 2023 accessibility-related variables identified from public AHS materials

- `NOSTEP`: Whether use of steps is not required to enter the building/home from outside. Source: 2023 AHS Table Specifications, Housing Unit Characteristics and General Housing tables. Weight: `WEIGHT`. Comparability: Directly comparable core item in 2011 and 2019.
- `HMRACCESS`: Whether an owner-occupied unit's home improvement activity in the last two years was done for accessibility for elderly or disabled residents. Source: 2023 AHS Table Specifications, Home Improvement table. Weight: `WEIGHT`. Comparability: Available in 2019, not available in 2011.
- `DISHH`: Whether at least one disabled person lives in the unit. Source: 2023 AHS Table Specifications, Disability table and Column Variables sheet. Weight: `WEIGHT`. Comparability: Directly comparable to 2019 DISHH; only approximately harmonized to 2011 HDSB because the 2011 disability recode is not identical.
- `NUMWALK`: Count category for persons in the unit with a physical disability: none, one, or two or more. Source: 2023 AHS Table Specifications, Disability table; 2023 Value Labels package. Weight: `WEIGHT`. Comparability: Directly comparable to 2019 NUMWALK; only approximately harmonized to 2011 HWALK because the 2011 household physical-disability recode is not identical.
- `UNITFLOORS / BEDROOMS / BATHROOMS`: Structural variables used only to build a lower-bound proxy for Bo'sher level 1 in 2023 because the dedicated accessibility module is absent. Source: 2023 AHS flat PUF core household file. Weight: `WEIGHT`. Comparability: Proxy only; not a direct substitute for the 2011 or 2019 accessibility-module questions and not a clean cross-year trend measure.

## Key weighted findings

All differences reported below are descriptive weighted differences from AHS tabulations; they are not significance-tested estimates.

- 2023 all-housing-unit no-step share: 56.35%.
- 2023 occupied-unit no-step share: 57.41%.
- 2023 occupied disabled-household no-step share: 58.68% versus 57.03% for non-disabled households.
- 2023 occupied physically disabled-household no-step share: 60.52%.
- 2023 owner-improver accessibility-motive share: 6.18% of the weighted home-improvement universe (3.19M out of 51.55M).
- In 2023 that accessibility-motive share rises to 13.29% for disabled households and 19.94% for physically disabled households, compared with 3.83% for non-disabled households.

## No-step entry trend, 2011 to 2023

| Year | Occupied no-step share | All-housing no-step share | Weighted occupied universe |
|---|---:|---:|---:|
| 2011 | 42.38% | 41.79% | 114.83M |
| 2019 | 53.57% | 52.31% | 124.14M |
| 2023 | 57.41% | 56.35% | 133.23M |

## 2023 disaggregation: no-step entry among occupied units

### By tenure

| Tenure | Weighted universe | Weighted yes | Share |
|---|---:|---:|---:|
| owner | 86.85M | 51.02M | 58.75% |
| renter_or_no_cash_rent | 46.38M | 25.47M | 54.92% |

### By building type

| Building type | Weighted universe | Weighted yes | Share |
|---|---:|---:|---:|
| mobile_or_other | 7.24M | 1.93M | 26.64% |
| multifamily_20_plus | 12.23M | 7.89M | 64.50% |
| multifamily_2_4 | 9.10M | 4.05M | 44.45% |
| multifamily_5_19 | 11.24M | 5.37M | 47.78% |
| single_family_attached | 8.16M | 5.54M | 67.88% |
| single_family_detached | 85.26M | 51.72M | 60.66% |

### By year built

| Year built group | Weighted universe | Weighted yes | Share |
|---|---:|---:|---:|
| 1940_1959 | 18.05M | 9.34M | 51.76% |
| 1960_1979 | 32.42M | 19.80M | 61.07% |
| 1980_1999 | 33.71M | 19.86M | 58.91% |
| 2000_plus | 32.79M | 21.22M | 64.72% |
| pre_1940 | 16.27M | 6.27M | 38.57% |

### By disability household

| Disabled household | Weighted universe | Weighted yes | Share |
|---|---:|---:|---:|
| No disabled household member | 102.19M | 58.28M | 57.03% |
| At least one disabled household member | 31.04M | 18.21M | 58.68% |

## 2019 module-only context

The 2019 Home Accessibility topical module asked problem-based questions that disappear in 2023. Those results are therefore historical context, not a continued trend line. Using SP2WEIGHT, the 2019 physically disabled household subset reported the following problem rates:

- Trouble entering home/property: 21.34%
- Trouble getting to bedroom: 11.37%
- Trouble using bedroom: 15.37%
- Trouble getting to kitchen: 11.38%
- Trouble using kitchen: 17.49%
- Trouble getting to bathroom: 12.84%
- Trouble using bathroom: 17.81%

## Bo'sher three-tier framework

Published 2011 HUD benchmark:

- Level 1 potentially modifiable: 33.34%
- Level 2 livable for moderate mobility difficulty: 3.76%
- Level 3 wheelchair accessible: 0.15%

What can be done with public materials beyond that benchmark:

- 2011 public-PUF reconstruction: L1 32.17%, L2 5.73%, L3 0.14%. This reproduces levels 1 and 3 fairly closely but overshoots level 2, so the HUD report remains the authoritative 2011 reference.
- 2019 level-1-style approximation: 40.51% among occupied topical-module Group 2 cases, weighted with SP2WEIGHT.
- 2023 lower-bound level-1 proxy: 30.50% across the all-housing core-file universe, weighted with WEIGHT.

The 2019 level-1-style approximation and the 2023 lower-bound level-1 proxy are not a clean 2019→2023 time series: the 2019 figure is an occupied topical-module Group 2 estimate weighted with SP2WEIGHT, while the 2023 figure is an all-housing core-file proxy weighted with WEIGHT.

The critical limitation is that 2023 lacks the dedicated accessibility-module variables needed for level 2 and level 3. The script therefore reports those as infeasible for exact replication in 2023.

## Main limitations

- The 2023 AHS national PUF does not include the dedicated Home Accessibility topical module that existed in 2019, so there is no 2023 analogue for the 2011 feature battery used by Bo'sher et al.
- 2019 Home Accessibility variables use SP2WEIGHT because they are topical-module Group 2 items; 2023 accessibility-related variables used here are core-file items and therefore use WEIGHT.
- The canonical 2011 Bo'sher three-tier figures are reported from the published HUD report. Public-PUF reconstruction comes close for levels 1 and 3 but not level 2, so published HUD values remain the authoritative 2011 benchmark.
- The 2019 level-1-style approximation and 2023 lower-bound proxy are not a clean 2019→2023 comparable series because they use different universes, weights, and question batteries (2019 occupied topical-module Group 2 cases with SP2WEIGHT versus a 2023 all-housing core-file proxy with WEIGHT).
- The 2023 Bo'sher-style result is only a lower-bound structural proxy based on no-step entry plus one-floor units with at least one bedroom and one bathroom; it is not directly comparable to the full 2011 level-1 index.
- Because 2023 lacks the 2019 problem-based accessibility module, 2019 home-accessibility problem shares are historical context only, not trend estimates continued into 2023.
- Reported differences in this memo are descriptive weighted differences from AHS tabulations; the script does not estimate sampling variance or test statistical significance.
- Cross-year subgroup comparisons are approximate harmonizations rather than exact apples-to-apples measures: 2011 uses HDSB/HWALK recodes, while 2019 and 2023 use DISHH/NUMWALK or related proxies.

## Files created or modified by this task

- scripts/ahs_2023_accessibility_analysis.py
- results/ahs_2023_accessibility_results.json
- results/ahs_2023_accessibility_analysis.md

## Raw downloads created for reproducibility

- data/ahs_accessibility/raw/AHS 2023 National PUF v1.1 Flat CSV.zip
- data/ahs_accessibility/raw/AHS 2019 National PUF v1.1 Flat CSV.zip
- data/ahs_accessibility/raw/AHS 2011 National PUF v3.0 Flat CSV.zip
- data/ahs_accessibility/raw/AHS 2023 Value Labels Package.zip
- data/ahs_accessibility/raw/AHS 2019 Value Labels Package.zip
- data/ahs_accessibility/raw/AHS 2011 National Value Labels Package.zip
- data/ahs_accessibility/raw/AHS 2023 Table Specifications and PUF Estimates for User Verification.xlsx
- data/ahs_accessibility/raw/2019 AHS Table Specifications and PUF Estimates for User Verification.xlsx
- data/ahs_accessibility/raw/AHS_ 2011_Table_Specs.xls
- data/ahs_accessibility/raw/accessibility-america-housingStock.pdf
- data/ahs_accessibility/raw/Getting Started with the AHS PUF 2015 and Beyond.pdf
