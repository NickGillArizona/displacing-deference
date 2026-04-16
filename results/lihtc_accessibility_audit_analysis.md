# 4,918 LIHTC properties containing 360,843 units across 19 states lack public accessible-unit inventory, are in states with no observed QAP accessibility requirement, and show no observed strict federal-overlap proxy

## LIHTC Accessibility Audit Memo

Generated: 2026-04-16T11:41:49+00:00
Repo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH`

## Bottom line

This memo quantifies the LIHTC accessibility-data black hole. HUD's public LIHTC file covers 54,102 properties and 3,732,739 units, but the public header exposes no accessible-unit inventory field. The nearest disability-related field is `TRGT_DIS`, which HUD's dictionary defines as `Targets a specific population – disabled` rather than an accessible-unit count.

The conservative perimeter-gap floor is 4,918 properties and 360,843 units across 19 states: projects in the 19 states with no observed QAP accessibility requirement, placed in service 2003-2023, with no observed strict federal-overlap proxy in HUD's public LIHTC file. Under the broader overlap screen, 4,732 properties and 345,353 units across 19 states remain.

That is the note's standalone-LIHTC perimeter problem in numeric form: no public federal accessible-unit inventory, no observed state QAP accessibility requirement in 19 states, and a large 2003+ subset with no observed federal-overlap marker. These counts are observed-proxy bounds, not definitive Section 504 noncoverage holdings.

## Sources and scope

- HUD LIHTC public file: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/lihtc/LIHTCPUB.csv`
- HUD LIHTC dictionary: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/lihtc/lihtc_dictionary.txt`
- The Kelsey 2023 factsheet text: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/The-Kelsey-State-LIHTC-Accessibility-Factsheet.txt`
- The Kelsey 2023 Section 504 comments text: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/The-Kelsey-504-ANPRM-Comments.txt`
- Units are counted as `N_UNITS` when positive, otherwise `N_UNITSR`, matching the completed probe scripts used in the prior research pass.
- The Kelsey taxonomy is a 50-state map. DC and territories remain outside that taxonomy and are reported separately below.
- The state/QAP categories here are reconstructed current/2023 Kelsey categories mapped onto HUD's public LIHTC stock, not project-year historical determinations of what a state's QAP required when a given property was placed in service.

## Key findings

1. No public accessible-unit inventory field was observed in the HUD LIHTC file. The file contains target-population flags (`TRGT_*`) but not a public count of mobility-accessible or sensory-accessible units.
2. `TRGT_DIS=1` appears on 5,245 properties / 398,458 units overall. It is a targeting flag, not an accessibility inventory.
3. The requested decade analysis shows `TRGT_DIS=1` rising from 3.37% of 1987-1996 properties to 15.52% in 2017-2023.
4. The Kelsey reconstruction sorts the 50 states into 22 with accessibility construction requirements, 9 with incentives only, and 19 with no observed QAP accessibility requirement. Only 2 states exceed Section 504.
5. The 19 states with no observed QAP accessibility requirement account for 14,423 properties / 851,160 units overall and 7,402 properties / 523,174 units in the 2003+ overlap-proxy window.
6. Within that 2003+ subset in states with no observed QAP accessibility requirement, 4,918 properties / 360,843 units show no observed strict federal-overlap proxy, and 4,732 properties / 345,353 units show no observed broad proxy.

## The accessibility-data black hole and the perimeter

The LIHTC black hole is three-sided:
- the federal LIHTC public file has no accessible-unit inventory field,
- 19 states in the Kelsey 2023 taxonomy have no observed QAP accessibility requirement, and
- even after limiting to 2003-2023 properties and screening for observed federal overlap, 360,843 units remain in the conservative strict proxy floor.

This framing is stronger than simply saying LIHTC lacks a field. It identifies the perimeter gap the note leaves outside its defended HUD-reporting regime: apparently standalone LIHTC in states with no observed QAP accessibility requirement where the public file also shows no observed federal-overlap marker. The broad screen narrows that subset only modestly, from 360,843 to 345,353 units.

## What the HUD file can and cannot say

The HUD file can say:
- how many LIHTC properties/units exist in the public extract,
- whether a project was flagged as targeting disabled households (`TRGT_DIS=1`), and
- whether the public file records selected co-funding, rent-assistance, insurance, or guarantee markers.

The HUD file cannot say:
- how many accessible units a project contains,
- how many units are mobility-accessible or sensory-accessible, or
- whether Section 504 definitively applies to a given project as a matter of law.

## TRGT_DIS by requested decades

| Decade | Properties | Units | TRGT_DIS=1 properties | TRGT_DIS share of properties | TRGT_DIS share of units |
| --- | --- | --- | --- | --- | --- |
| 1987-1996 | 14,205 | 558,745 | 479 | 3.37% | 4.26% |
| 1997-2006 | 15,612 | 1,225,329 | 1,585 | 10.15% | 7.80% |
| 2007-2016 | 14,492 | 1,107,200 | 1,846 | 12.74% | 12.18% |
| 2017-2023 | 6,996 | 612,865 | 1,086 | 15.52% | 17.91% |

The decade trend matters because it shows why `TRGT_DIS` cannot substitute for an accessibility inventory. The targeting flag's prevalence changes substantially over time: 3.37% in 1987-1996, 10.15% in 1997-2006, 12.74% in 2007-2016, and 15.52% in 2017-2023.

Within the 19 states with no observed QAP accessibility requirement, the same pattern rises from 1.98% to 10.23%. Outside the requested windows, 2,797 properties / 228,600 units remain and are reported separately in the JSON.

## Kelsey/QAP accessibility categories and totals

| Group | States | Properties | Units | Share of all units |
| --- | --- | --- | --- | --- |
| Any QAP accessibility construction requirement | 22 | 31,409 | 2,397,046 | 64.22% |
| Requires or exceeds Section 504 | 15 | 22,978 | 1,944,279 | 52.09% |
| Incentives only | 9 | 7,597 | 427,084 | 11.44% |
| No QAP accessibility requirement observed | 19 | 14,423 | 851,160 | 22.80% |

| Detailed category | States | Properties | Units | Share of all units |
| --- | --- | --- | --- | --- |
| Requires more than Section 504 | 2 | 6,454 | 524,078 | 14.04% |
| Requires Section 504 | 13 | 16,524 | 1,420,201 | 38.05% |
| Requirements less than Section 504 | 7 | 8,431 | 452,767 | 12.13% |
| Incentives for accessible units | 9 | 7,597 | 427,084 | 11.44% |
| No observed QAP accessibility requirement | 19 | 14,423 | 851,160 | 22.80% |

The key Kelsey crosswalk takeaway is structural: 22 states impose some accessibility construction requirement through their QAPs, 9 rely on incentives only, and 19 have no observed QAP accessibility requirement. Those state labels are reconstructed current/2023 categories mapped onto the HUD stock, not year-specific historical QAP determinations at placement in service. The stricter 15-state require-or-exceed-504 subset still covers 22,978 properties / 1,944,279 units.

## Full 50-state QAP crosswalk

The JSON output contains the fuller state-level crosswalk with counts, units, `TRGT_DIS` shares, overlap-proxy counts, and additional state fields. The markdown table below is a reduced quick-review table with a subset of those columns.

| State | QAP category | Properties | Units | TRGT_DIS=1 properties | TRGT_DIS share of state properties |
| --- | --- | --- | --- | --- | --- |
| CA | Requires more than Section 504 | 4,916 | 407,063 | 121 | 2.46% |
| IL | Requires more than Section 504 | 1,538 | 117,015 | 117 | 7.61% |
| TX | Requires Section 504 | 2,997 | 333,104 | 601 | 20.05% |
| NY | Requires Section 504 | 4,079 | 328,934 | 471 | 11.55% |
| FL | Requires Section 504 | 1,545 | 209,614 | 16 | 1.04% |
| GA | Requires Section 504 | 1,630 | 156,435 | 0 | 0.00% |
| OH | Requires Section 504 | 2,105 | 132,941 | 58 | 2.76% |
| MA | Requires Section 504 | 1,035 | 83,523 | 93 | 8.99% |
| MD | Requires Section 504 | 921 | 81,545 | 165 | 17.92% |
| KS | Requires Section 504 | 729 | 35,312 | 5 | 0.69% |
| WV | Requires Section 504 | 354 | 15,039 | 33 | 9.32% |
| ME | Requires Section 504 | 355 | 13,236 | 6 | 1.69% |
| NH | Requires Section 504 | 275 | 11,891 | 9 | 3.27% |
| SD | Requires Section 504 | 311 | 10,764 | 10 | 3.22% |
| AK | Requires Section 504 | 188 | 7,863 | 24 | 12.77% |
| WA | Requirements less than Section 504 | 1,419 | 122,437 | 681 | 47.99% |
| NC | Requirements less than Section 504 | 2,884 | 113,599 | 182 | 6.31% |
| IN | Requirements less than Section 504 | 1,325 | 85,651 | 63 | 4.75% |
| AZ | Requirements less than Section 504 | 576 | 47,753 | 22 | 3.82% |
| KY | Requirements less than Section 504 | 905 | 32,716 | 0 | 0.00% |
| IA | Requirements less than Section 504 | 752 | 31,465 | 157 | 20.88% |
| NE | Requirements less than Section 504 | 570 | 19,146 | 11 | 1.93% |
| VA | Incentives for accessible units | 1,229 | 111,624 | 18 | 1.46% |
| PA | Incentives for accessible units | 1,968 | 77,313 | 192 | 9.76% |
| MN | Incentives for accessible units | 1,106 | 66,965 | 157 | 14.20% |
| SC | Incentives for accessible units | 874 | 46,929 | 36 | 4.12% |
| MS | Incentives for accessible units | 914 | 44,688 | 231 | 25.27% |
| AL | Incentives for accessible units | 833 | 44,176 | 426 | 51.14% |
| RI | Incentives for accessible units | 201 | 13,979 | 41 | 20.40% |
| DE | Incentives for accessible units | 177 | 11,066 | 0 | 0.00% |
| MT | Incentives for accessible units | 295 | 10,344 | 3 | 1.02% |
| NJ | No observed QAP accessibility requirement | 1,505 | 114,138 | 8 | 0.53% |
| MI | No observed QAP accessibility requirement | 1,693 | 109,664 | 147 | 8.68% |
| TN | No observed QAP accessibility requirement | 1,147 | 74,995 | 369 | 32.17% |
| MO | No observed QAP accessibility requirement | 1,917 | 74,170 | 200 | 10.43% |
| CO | No observed QAP accessibility requirement | 830 | 67,478 | 4 | 0.48% |
| LA | No observed QAP accessibility requirement | 1,110 | 64,225 | 87 | 7.84% |
| WI | No observed QAP accessibility requirement | 1,223 | 57,510 | 5 | 0.41% |
| OR | No observed QAP accessibility requirement | 749 | 44,959 | 107 | 14.29% |
| AR | No observed QAP accessibility requirement | 796 | 42,559 | 1 | 0.13% |
| NV | No observed QAP accessibility requirement | 355 | 35,782 | 22 | 6.20% |
| UT | No observed QAP accessibility requirement | 554 | 33,637 | 16 | 2.89% |
| OK | No observed QAP accessibility requirement | 613 | 33,071 | 69 | 11.26% |
| CT | No observed QAP accessibility requirement | 455 | 27,670 | 12 | 2.64% |
| NM | No observed QAP accessibility requirement | 321 | 21,435 | 0 | 0.00% |
| ID | No observed QAP accessibility requirement | 286 | 12,915 | 0 | 0.00% |
| HI | No observed QAP accessibility requirement | 139 | 12,357 | 0 | 0.00% |
| VT | No observed QAP accessibility requirement | 347 | 10,252 | 2 | 0.58% |
| ND | No observed QAP accessibility requirement | 252 | 8,887 | 59 | 23.41% |
| WY | No observed QAP accessibility requirement | 131 | 5,456 | 0 | 0.00% |

## States with no observed QAP accessibility requirement and the perimeter-gap floor

- Overall states with no observed QAP accessibility requirement: 14,423 properties / 851,160 units (22.80% of all LIHTC units).
- `TRGT_DIS=1` within those states: 1,108 properties / 72,455 units.
- 2003+ subset: 7,402 properties / 523,174 units.
- 2003+ with no observed strict overlap proxy: 4,918 properties / 360,843 units (68.97% of 2003+ units in states with no observed QAP accessibility requirement).
- 2003+ with no observed broad overlap proxy: 4,732 properties / 345,353 units (66.01% of 2003+ units in states with no observed QAP accessibility requirement).

Top states with no observed QAP accessibility requirement by units:

| State | Properties | Units | 2003+ units | 2003+ no strict proxy units | 2003+ no broad proxy units |
| --- | --- | --- | --- | --- | --- |
| NJ | 1,505 | 114,138 | 79,755 | 73,926 | 73,239 |
| MI | 1,693 | 109,664 | 69,746 | 36,738 | 34,604 |
| TN | 1,147 | 74,995 | 53,402 | 26,544 | 26,544 |
| MO | 1,917 | 74,170 | 39,257 | 31,273 | 30,065 |
| CO | 830 | 67,478 | 48,228 | 36,847 | 33,236 |
| LA | 1,110 | 64,225 | 38,206 | 36,408 | 36,344 |
| WI | 1,223 | 57,510 | 32,330 | 8,864 | 8,662 |
| OR | 749 | 44,959 | 24,441 | 16,313 | 12,798 |
| AR | 796 | 42,559 | 25,249 | 11,584 | 11,584 |
| NV | 355 | 35,782 | 21,687 | 15,565 | 15,406 |

## How the overlap proxies were defined

Strict overlap proxy:
- positive `HOME`, `CDBG`, `HTF`, `MFF_RA`, `FMHA_514`, `FMHA_515`, `HOPEVI`, `TCAP`, `TCEP`, or `RAD`; or
- `RENTASST=1` (Federal) or `RENTASST=3` (Both Federal and State).

Broad overlap proxy:
- everything in the strict proxy, plus
- `FHA=1`, `FMHA_538=1`, or `RENTASST=5` (Unknown whether Federal or State).

Interpretive caution:
- A positive proxy is evidence of an observed federal nexus in the public LIHTC file, not a final legal Section 504 holding.
- A negative proxy means only that the public file shows no observed marker under these rules. It does not prove lack of federal financial assistance or lack of Section 504 coverage.

## Why the overlap analysis starts in 2003

HUD's dictionary says several relevant fields first appear with 2003 properties, including `HOME`, `CDBG`, `FHA`, `HOPEVI`, and `TRGT_DIS`. But some fields were added later: `RENTASST` in 2006, `TCAP/TCEP` in 2012, and `HTF/RAD` in 2018. Accordingly, even the 2003+ proxy window still under-observes some later-added forms of overlap, especially in the early years of that window.

## Why standalone LIHTC stays outside the proposed HUD reporting regime

The note's defended reporting perimeter is HUD-funded or HUD-inspected housing where HUD can amend existing forms and collect accessibility counts through channels it already controls. Standalone LIHTC is different. The public LIHTC file is observational, not a live HUD reporting hook; it provides no accessible-unit inventory; and the available overlap fields only proxy federal participation rather than conclusively resolving project-level Section 504 status.

That is why this audit quantifies standalone LIHTC as a perimeter problem rather than treating it as automatically inside the proposed regime. The strict proxy floor of 360,843 units shows the size of the excluded black hole, while the proposal itself remains limited to programs HUD already funds, inspects, or directly administers. In short: the memo uses LIHTC to show what HUD still cannot see, not to claim that every LIHTC property is already within HUD's defended reporting authority.

## Unmapped jurisdictions outside the 50-state taxonomy

673 properties / 57,449 units are in jurisdictions not covered by the 50-state Kelsey taxonomy.

| Jurisdiction | Properties | Units |
| --- | --- | --- |
| DC | 256 | 30,849 |
| PR | 245 | 23,075 |
| VI | 33 | 1,475 |
| GU | 15 | 1,349 |
| AS | 119 | 428 |
| MP | 5 | 273 |

## Bottom-line limitations for citation

- Do not cite this audit as counting accessible units; it does not and cannot from the public LIHTC file.
- Do not treat `TRGT_DIS` as an accessible-unit measure; it is a target-population flag.
- Do not equate the strict or broad overlap proxies with definitive Section 504 applicability. They are conservative observed-federal-overlap screens, useful for bounding the gap but not for resolving building-level legal status.
- Read the standalone-LIHTC perimeter numbers as observed-proxy bounds on the excluded black hole, not as final legal coverage determinations.
