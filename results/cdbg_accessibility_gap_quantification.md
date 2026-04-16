# CDBG Accessibility-Gap Quantification Memo

Generated: 2026-04-16T15:56:26+00:00
Repo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH`
Status: strict national actual-spending gap fully solved for 14-series CDBG disbursements; accessibility-specific spending remains unreported, so the remaining accessibility count is estimated rather than observed.

## Bottom line

HUD Exchange's national CDBG expenditure workbook provides the direct matrix-code spending series that the national accomplishments workbook lacked.

Against $67.652 billion in total national CDBG formula allocations across FY2005-FY2024, HUD recorded $15.313 billion in observed 14A-14L rehabilitation disbursements and $14.753 billion in the accomplishments-comparable subset (14A, 14B, 14C, 14D, 14F, 14G, 14H, 14I, 14J). The difference is driven by expenditure-only codes 14E, 14K, and 14L, which the national accomplishments workbook does not expose as separate household rows.

The prior proxy-dollar claim is withdrawn. HUD already publishes an actual national 14-series spending series; what it still does not publish is any accessibility flag showing whether any of those dollars funded ramps, widened doors, accessible bathrooms, or other accessibility retrofits.

HUD's FY2005-FY2024 national accomplishments workbook reports 1,956,873 households served in the accomplishments-comparable 14-series codes. Using the repo-local POSH disability-share estimate of 39.3% (approximately 39%), about 769,051 of those rehab households likely included a disabled household member. Applying the 313,000-household mobility-device benchmark to the estimated 1,801,784 HUD-assisted disabled-household denominator implies a 17.4% accessibility-need rate, or about 133,597 likely accessibility-modification cases that went untracked.

## Status of the spec gap

- Actual national 14-series spending for FY2005-FY2024: fully solved via HUD Exchange's national CDBG expenditure workbook.
- Per-year national CDBG formula allocation comparator: now surfaced in the year-by-year table below.
- Accessibility-need benchmark [W]: now computed at 17.4% using 313,000 / 1,801,784.
- Estimated untracked accessibility modifications: now surfaced as approximately 133,597 household-level accessibility-modification cases.
- 05B decline assessment including FY2024: direct answer = accelerating downward rather than stabilizing.

## Inputs and method

- Accomplishments source: `data/CDBG_Accomp_Natl.xlsx` (`National Accomplishments` sheet).
- Expenditure source: `data/CDBG_Expend_NatlAll.xlsx` downloaded from <https://files.hudexchange.info/resources/documents/CDBG_Expend_NatlAll.xlsx>.
- POSH source: `data/US_2024_2020census.xlsx` (national summary row).
- Formula allocation comparator: annual national CDBG formula grant allocation / appropriation series already used in repo-local CDBG analysis, totaling $67.652 billion across FY2005-FY2024.
- Years: FY2005-FY2024, following HUD's published national workbook year labels.
- Accomplishments-comparable 14-series codes: 14A, 14B, 14C, 14D, 14F, 14G, 14H, 14I, 14J. The accomplishments workbook did not contain 14E, 14K, 14L as separate household rows.
- Additional 14-series codes present in the expenditure workbook but not as separate accomplishments rows: 14E, 14K, 14L.
- The annual core spending series below uses direct observed CDBG disbursements from the national expenditure workbook, not a proxy allocated from formula grants.
- Separate CDBG-CV 14-series disbursements exist only in FY2021-FY2024 and totaled $0.134 billion for the accomplishments-comparable codes ($0.142 billion across all 14A-14L). They are reported separately rather than folded into the 20-year core CDBG-only series.
- POSH disability share calculation: 33.0% under age 62, 48.0% age 62+, and 42.0% age-62+ household share, yielding a weighted household disability rate of 39.3% and an estimated 1,801,784 HUD-assisted households with disabilities.
- Accessibility-need benchmark: 313,000 HUD-assisted households with a mobility-device user in a unit without accessibility features, from GAO-23-106339 (<https://www.gao.gov/products/gao-23-106339>). Dividing 313,000 by 1,801,784 yields the 17.4% rate used below.

## Year-by-year table

| FY | Total CDBG formula allocation ($B) | Observed 14-series CDBG ($B, comparable) | Observed 14-series CDBG ($B, all 14A-L) | 14-series HH served | 14-series share of housing HH | Est. disabled rehab HH (39.3%) | Est. accessibility-need HH (17.4%) | 05B persons | 03B persons |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2005 | 4.117 | 0.922 | 0.954 | 159,259 | 93.3% | 62,589 | 10,873 | 154,149 | 107,768 |
| 2006 | 3.711 | 0.888 | 0.922 | 169,424 | 94.4% | 66,584 | 11,567 | 178,952 | 6,941 |
| 2007 | 3.711 | 0.876 | 0.907 | 144,006 | 94.6% | 56,594 | 9,831 | 73,002 | 124,795 |
| 2008 | 3.593 | 0.817 | 0.848 | 142,182 | 95.3% | 55,878 | 9,707 | 116,459 | 22,852 |
| 2009 | 3.642 | 0.779 | 0.812 | 100,732 | 95.6% | 39,588 | 6,877 | 145,854 | 81,661 |
| 2010 | 3.948 | 0.762 | 0.790 | 102,724 | 94.2% | 40,371 | 7,013 | 115,498 | 43,962 |
| 2011 | 3.303 | 0.747 | 0.776 | 92,260 | 95.5% | 36,258 | 6,299 | 148,827 | 36,106 |
| 2012 | 2.948 | 0.716 | 0.753 | 83,564 | 93.9% | 32,841 | 5,705 | 141,560 | 28,548 |
| 2013 | 3.078 | 0.692 | 0.721 | 87,302 | 92.5% | 34,310 | 5,960 | 81,900 | 50,209 |
| 2014 | 3.030 | 0.647 | 0.676 | 77,244 | 93.5% | 30,357 | 5,274 | 141,181 | 14,466 |
| 2015 | 3.066 | 0.634 | 0.663 | 63,739 | 94.7% | 25,049 | 4,352 | 86,779 | 16,827 |
| 2016 | 3.000 | 0.643 | 0.672 | 70,060 | 95.0% | 27,534 | 4,783 | 339,590 | 20,257 |
| 2017 | 3.000 | 0.617 | 0.646 | 60,715 | 91.5% | 23,861 | 4,145 | 145,857 | 15,545 |
| 2018 | 3.365 | 0.625 | 0.654 | 62,103 | 95.2% | 24,406 | 4,240 | 429,399 | 19,328 |
| 2019 | 3.365 | 0.636 | 0.662 | 79,421 | 94.4% | 31,212 | 5,422 | 427,391 | 28,921 |
| 2020 | 3.425 | 0.633 | 0.655 | 49,607 | 93.6% | 19,496 | 3,387 | 488,625 | 16,817 |
| 2021 | 3.450 | 0.683 | 0.706 | 56,627 | 95.3% | 22,254 | 3,866 | 650,273 | 249 |
| 2022 | 3.300 | 0.765 | 0.786 | 57,274 | 95.3% | 22,509 | 3,910 | 53,757 | 14,966 |
| 2023 | 3.300 | 0.878 | 0.896 | 169,185 | 97.7% | 66,490 | 11,550 | 597,640 | 60,620 |
| 2024 | 3.300 | 0.796 | 0.814 | 129,445 | 97.5% | 50,872 | 8,837 | 93,467 | 54,353 |

## Twenty-year aggregate headline

- Total national CDBG formula allocation comparator: $67.652 billion
- Total observed 14-series CDBG disbursements, accomplishments-comparable codes: $14.753 billion
- Total observed 14-series CDBG disbursements, all 14A-14L: $15.313 billion
- Additional observed dollars from expenditure-only 14E/14K/14L relative to the accomplishments-comparable set: $0.560 billion
- Additional observed 14-series CDBG-CV disbursements in FY2021-FY2024: $0.134 billion comparable / $0.142 billion all 14A-14L
- Total 14-series households served: 1,956,873
- 14-series share of all reported housing households: 94.8%
- Total 05B persons served: 4,610,160
- Total 03B persons served: 765,191
- Estimated 14-series rehab households including a disabled household member: 769,051
- Accessibility-need rate among HUD-assisted disabled households (313,000 / 1,801,784): 17.4%
- Estimated household-level accessibility modifications that likely went untracked: 133,597
- Observed accessibility-modification count inside the 14-series: unknown / not reported by any matrix code or public field

## Estimated untracked accessibility modifications

Approximately 39% of HUD-assisted households include a disabled member (repo-local POSH estimate: 39.3%). Applying that rate to 1,956,873 CDBG-funded rehab households implies approximately 769,051 rehab households with a disabled member.

Using the prompt's benchmark, the accessibility-need rate is 313,000 / 1,801,784 = 17.4%. Applying 17.4% to 769,051 estimated disabled-household rehab cases yields approximately 133,597 likely household-level accessibility-modification cases that went untracked in FY2005-FY2024.

That is still an estimate, not an observed count. HUD's published national expenditure workbook, national accomplishments workbook, and grantee-level PR50 reports still do not identify which 14-series rehab activities actually installed accessibility features.

## Code mix within the accomplishments-comparable spending series

| Code | Matrix code name | FY2005-FY2024 observed CDBG disbursements ($B) | Share of comparable total |
|---|---|---:|---:|
| 14A | Rehabilitation: Single-Unit Residential | 9.209 | 62.4% |
| 14H | Rehabilitation Administration | 2.597 | 17.6% |
| 14B | Rehabilitation: Multi-Unit Residential | 1.609 | 10.9% |
| 14G | Acquisition for Rehabilitation | 0.430 | 2.9% |
| 14C | Public Housing Modernization | 0.328 | 2.2% |
| 14I | Lead-Based Paint/Lead Hazard Test/Abatement | 0.291 | 2.0% |
| 14D | Rehabilitation: Other Publicly-owned Residential Buildings | 0.125 | 0.8% |
| 14J | Housing Services - Excluding Housing Counseling, under 24 CFR 5.100 | 0.094 | 0.6% |
| 14F | Energy Efficiency Improvements | 0.070 | 0.5% |

Expenditure-only 14-series codes not separately exposed as household rows in the accomplishments workbook: 14E = $0.556B; 14K = $0.002B; 14L = $0.001B.

## Observed grantee-level PR50 examples

- Amherst, NY PY2023 PR50: 14A Rehab; Single-Unit Residential $256,032.21; 14F Energy Efficiency Improvements $4,997.00; 14H Rehabilitation Administration $110,374.88; 14I Lead-Based/Lead Hazard Test/Abate $4,757.61; 14-series subtotal $376,161.70. The same PR50 report still does not indicate whether any portion of those 14-series dollars funded accessibility retrofits. Source: <https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_AMHE-NY_NY_2023.pdf>
- Arapahoe County, CO PY2023 PR50: 14A Rehab; Single-Unit Residential $146,318.50; 14B Rehab; Multi-Unit Residential $1,262,413.74; 14F Energy Efficiency Improvements $213,639.92; 14-series subtotal $1,622,372.16. That same report separately lists just $9,763.00 under 05B (Services for Persons with Disabilities), illustrating that disability-specific activity can be coded explicitly while the much larger rehab dollars remain accessibility-blind. Source: <https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_ARAP-CO_CO_2023.pdf>
- Anne Arundel County, MD PY2023 PR50: 14A Rehab; Single-Unit Residential $261,939.32; 14B Rehab; Multi-Unit Residential $296,348.56; 14G Acquisition for Rehabilitation $243,945.81; 14H Rehabilitation Administration $574,096.18; 14-series subtotal $1,376,329.87. The same report separately lists $40,068.00 under 03B (Facility for Persons with Disabilities), again showing that direct 14-series rehab dollars are observable while accessibility content inside those rehab dollars is not. Source: <https://files.hudexchange.info/reports/published/CDBG_Expend_Grantee_ANNE-MD_MD_2023.pdf>

## 05B trend including FY2024

Direct answer: the 05B decline is accelerating downward rather than stabilizing.

The 05B series is volatile rather than monotonic, but FY2024 does not look like stabilization: 05B fell from 597,640 persons in FY2023 to 93,467 in FY2024, a -84.4% drop.

Relative to FY2005, FY2024 was -39.4% lower (154,149 to 93,467). Relative to FY2019, FY2024 was -78.1% lower (427,391 to 93,467).

Recent-window averages point the same way: the FY2019-FY2021 average was 522,096, while the FY2022-FY2024 average fell to 248,288, a -52.4% decline. The FY2019-FY2023 average was 443,537, while the FY2020-FY2024 average fell to 376,752, a -15.1% decrease.

## 03B trend

03B averaged 68,803 persons per year in FY2005-FY2009 and 29,401 in FY2020-FY2024, a -57.3% decline.

## Remaining limitation

The strict spending gap is now closed: HUD does publish a national 14-series disbursement series. The remaining gap is narrower but still consequential: neither the national expenditure workbook, the national accomplishments workbook, nor grantee-level PR50 reports identify whether any 14-series disbursement funded accessibility modifications.

## Policy implication

HUD is not missing a national spending series anymore; it is missing an accessibility flag inside an existing spending series. If even the conservative household-level estimate of 133,597 likely accessibility-modification cases is roughly right, HUD's current reporting structure is obscuring a six-figure accessibility workload inside already-published rehab disbursements. Adding an accessibility field to the 14-series reporting structure would convert existing rehab reporting into an actual accessibility-accounting system without requiring HUD to build a new expenditure pipeline from scratch.
