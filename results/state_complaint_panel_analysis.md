# State complaint panel: Massachusetts vs. CT/NH/VT/RI

Generated: 2026-04-16T07:45:40.460959+00:00

## What this file does

This memo builds a state x year panel from the local HUD/FHEO filed-case file for Massachusetts and four New England comparator states (CT, NH, VT, RI), then asks whether that panel can credibly support a Housing Navigator Massachusetts launch analysis.

## Core data coverage

- Primary panel source: `data/fheo-filed-cases.xlsx`
- FHEO file coverage for this panel: 2006-01-03 to 2020-06-30
- The local FHEO case-level file therefore supports full annual state comparisons only through 2019; 2020 is partial because the file ends on 2020-06-30.
- Housing Navigator Massachusetts launch marker used here: 2021-08-18 (Housing Navigator Massachusetts launch)
- Complaint-volume comparisons use raw filed-complaint counts. They are not normalized by population, renter households, disability prevalence, or housing stock.

## Provenance note on the HUD files

- This analysis uses `data/fheo-filed-cases.xlsx`, the local HUD/FHEO case-level workbook, because it preserves filing dates and extends through 2020-06-30.
- Those filing dates let the script rebuild the MA/CT/NH/VT/RI panel directly from underlying rows and correctly flag 2020 as a partial year.
- The older `data/fha-cases-by-year.xls` file in the repo is an earlier pre-aggregated year/state table documented in this repo as covering 2000-2019. It remains useful as an aggregate reference for overlapping pre-2020 years, but it lacks the case-level filing dates and later 2020 coverage used for this memo.

## Bottom line

There is no defensible Massachusetts-vs-control post-launch DiD in the FHEO panel because the comparable state-level file stops before the August 2021 launch. The FHEO data remain useful as a pre-launch baseline, but not as post-launch causal evidence.

## How to read the control comparisons

- Average control state: Simple mean of CT/NH/VT/RI state-year values; each control state receives equal weight.
- Pooled controls: Within-year sum of CT/NH/VT/RI state-year values; larger control states contribute more raw complaints.
- The plots use the average-control series, not the pooled-control sum.

## Main pre-launch panel findings

- Massachusetts had the largest FHEO complaint volume in this five-state comparison throughout the full-year window (2006-2019).
- From 2006 to 2019, Massachusetts total complaints rose by 34.28% and disability-basis complaints rose by 71.77%.
- Over the same years, the average comparator state's total complaints were essentially flat (-1.54%), while average disability complaints rose 12.50%.
- Massachusetts's disability share rose by 12.23 percentage points across the full pre-launch window, but it still sat 12.40 points below the average control-state disability share in the latest full year (2019).
- In 2019, Massachusetts recorded 380 total complaints and 213 disability-basis complaints, versus an average control-state level of 63.75 total complaints and 40.5 disability complaints.
- In that same year, the pooled controls (CT/NH/VT/RI summed together) recorded 255 total complaints and 162 disability-basis complaints, with a 63.53% disability share.
- In the latest full year, Massachusetts had about 5.96x the average control state's total complaint volume and 5.26x the average control state's disability complaint volume; versus pooled controls, Massachusetts was 1.49x and 1.31x as large, respectively.

## Latest full-year panel snapshot (2019)

| State | Total complaints | Disability complaints | Disability share |
|---|---:|---:|---:|
| MA | 380 | 213 | 56.05% |
| CT | 126 | 73 | 57.94% |
| RI | 79 | 51 | 64.56% |
| NH | 28 | 22 | 78.57% |
| VT | 22 | 16 | 72.73% |

## What the FHEO panel can and cannot identify

What it can do:
- Establish a clean pre-launch baseline for Massachusetts relative to nearby comparator states.
- Show long-run pre-2021 levels and disability-share trajectories.
- Demonstrate that Massachusetts complaint volume was already much larger than comparator-state averages before the registry launch.

What it cannot do:
- Estimate a Massachusetts-vs-controls post-2021 treatment effect for Housing Navigator.
- Support a simple DiD with the chosen controls, because the comparable state-level panel ends before treatment.
- Treat all of calendar year 2021 as post in any future annual-panel DiD refresh; with an August 18, 2021 launch, 2021 is a transition year and 2022 would be the first clean annual post period.

## Supplemental context (not directly comparable to the FHEO panel)

### NFHA national trend series

These national series show that disability remained the largest basis of fair housing complaints after 2020, but they are national aggregates rather than Massachusetts-vs-control state data.

| Complaint year | Total complaints | Disability complaints | Disability share | Source |
|---|---:|---:|---:|---|
| 2020 | 28,712 | 15,664 | 54.56% | [2021 Fair Housing Trends Report](https://nationalfairhousing.org/wp-content/uploads/2021/07/2021-Fair-Housing-Trends-Report_FINAL.pdf) |
| 2021 | 31,216 | 16,758 | 53.68% | [2022 Fair Housing Trends Report](https://nationalfairhousing.org/wp-content/uploads/2022/11/2022-Fair-Housing-Trends-Report.pdf) |
| 2022 | 33,007 | 17,580 | 53.26% | [2023 Fair Housing Trends Report](https://nationalfairhousing.org/wp-content/uploads/2023/08/2023-Trends-Report-Final.pdf) |
| 2023 | 34,150 | 17,986 | 52.61% | [2024 Fair Housing Trends Report](https://nationalfairhousing.org/wp-content/uploads/2023/04/2024-Fair-Housing-Trends-Report-FINAL_07.2024.pdf) |
| 2024 | 32,321 | 17,645 | 54.59% | [2025 Fair Housing Trends Report](https://nationalfairhousing.org/wp-content/uploads/2025/11/2025-NFHA-Fair-Housing-Trends-Report.pdf) |

### Massachusetts-only MCAD series

These figures are useful context for Massachusetts complaint-processing activity after launch, but they are not a substitute for the missing post-2021 control-state panel. MCAD covers multiple jurisdictions beyond housing, reports by fiscal year, and its disability counts are not housing-specific.

| Fiscal year | Period | All MCAD complaints | Housing-jurisdiction complaints | Disability protected-category complaints | Source |
|---|---|---:|---:|---:|---|
| FY20 | 2019-07-01 to 2020-06-30 | 2,778 | 329 | 1,083 | [report](https://www.mass.gov/doc/mcad-fy20-annual-report/download) |
| FY21 | 2020-07-01 to 2021-06-30 | 2,463 | 263 | 1,060 | [report](https://www.mass.gov/doc/mcad-fy21-annual-report/download) |
| FY22 | 2021-07-01 to 2022-06-30 | 2,822 | 366 | 1,088 | [report](https://www.mass.gov/doc/mcad-fy22-annual-report/download) |
| FY23 | 2022-07-01 to 2023-06-30 | 3,086 | 427 | 1,237 | [report](https://www.mass.gov/doc/mcad-fy23-annual-report/download) |
| FY24 | 2023-07-01 to 2024-06-30 | 3,553 | — | — | [report](https://www.mass.gov/doc/mcad-fy24-annual-report/download) |
| FY25 | 2024-07-01 to 2025-06-30 | 3,243 | — | — | [report](https://www.mass.gov/doc/mcad-fy25-annual-report/download) |

Contextual read:
- MCAD all-jurisdiction complaints rose from 2,463 in FY21 to 3,086 in FY23.
- MCAD housing-jurisdiction complaints likewise rose from 263 in FY21 to 427 in FY23.
- That pattern is consistent with continued demand for complaint-processing capacity in Massachusetts, but it cannot isolate any effect of the Housing Navigator registry because the series lacks comparable control states and mixes housing with broader MCAD jurisdictional structure.

## Limitations

1. The primary comparable state-level FHEO file ends on 2020-06-30, so 2020 is partial and there are no post-launch years for a clean DiD.
2. Any future annual-panel DiD should exclude 2021 as a transition year because the launch occurred on 2021-08-18 rather than on January 1.
3. Complaint-volume comparisons here use raw filed-complaint counts; they are not normalized by population, renter households, disability prevalence, or housing stock.
4. FHEO disability counts are basis counts, not mutually exclusive case categories; a single complaint can list multiple protected-class bases.
5. MCAD post-2020 data are Massachusetts-only, fiscal-year, and broader than fair-housing-only Title VIII complaints.
6. NFHA trend data are national aggregates compiled from mixed reporting calendars (private groups report calendar-year data; HUD/FHAP/DOJ report by federal fiscal year).
7. Small comparator states, especially NH and VT, have low annual counts, so disability-share series are more volatile there.

## Output files

- `results/state_complaint_panel_results.json`
- `results/state_complaint_panel_analysis.md`
- `results/state_complaint_panel_total_complaints.svg`
- `results/state_complaint_panel_disability_share.svg`
