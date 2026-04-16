# Pre-1991 statutory accessibility gap analysis

Generated: 2026-04-16T16:27:43+00:00

## Question

Estimate what share of the current U.S. renter-occupied housing stock predates the March 13, 1991 FHA design-and-construction trigger and therefore falls outside § 3604(f)(3)(C), then connect that stock split to disabled renter concentration and the 47% post-1991 noncompliance figure already summarized in Appendix H.

## Data and method

- Survey: ACS 2020-2024 5-Year PUMS
- API: `https://api.census.gov/data/2024/acs/acs5/pums`
- Universe: Renter-occupied householders (TEN=3, SPORDER=1), 50 states + DC; Puerto Rico excluded
- Weight: `WGTP`
- Disability proxy: householder has ambulatory difficulty (`DPHY=1`) or independent-living difficulty (`DOUT=1`)
- 4+ proxy: BLD=05-09. BLD=05 is the combined 3-4-unit bucket and serves as the closest reproducible proxy for exact 4-unit buildings.
- Exact-size gap assessment: Public Census products available in this workspace do not point-identify exact 4-unit buildings; the residual uncertainty is confined to the ACS/AHS BLD=05 bucket.
- Checked public exact-size sources: ACS detailed-table metadata: B25024 and B25032 use a '3 or 4' category; B25127 uses '2 to 4'; Local AHS 2019/2023 public-use metadata: BLD=05 is labeled '3 to 4 apartments'
- March 13, 1991 adjustment: 437 of 3,652 days in the ACS 1990-1999 YRBLT bucket fall on or before March 13, 1991. The script reports a strict lower bound and an adjusted estimate; the memo below uses the adjusted estimate unless noted otherwise.
- Metro/non-metro: 2020 tract-to-PUMA relationship file plus July 2023 OMB delineation file (2020 standards); PUMA classified metro if a majority of its tracts fall in metropolitan counties.
- Post-1991 noncompliance assumption: 47% from Housing Equality Center of Pennsylvania regional testing, as summarized in appendices/Appendix_H_Supplementary_Data.md

## Exact 4-unit gap: strongest defensible bounds

The only unresolved building-size mass is the ACS `BLD=05` bucket. It contains 4,639,999 renter households (10.8% of all renters), and any exact 4-unit cases must be a subset of that bucket. The exact floor from unquestionably covered `5+` buildings is 20,757,225 renter households (48.5% of all renters).

| Metric | Minimum | Maximum |
|---|---:|---:|
| Literal FHA 4+ renter households | 20,757,225 | 25,397,224 |
| Literal FHA 4+ share of all renter households | 48.5% | 59.3% |
| Pre-trigger literal FHA 4+ renter households | 12,191,284 | 15,624,995 |
| Pre-trigger literal FHA 4+ share of all renter households | 28.5% | 36.5% |
| Pre-trigger share within literal FHA 4+ renter universe | 55.6% | 64.5% |
| Disabled renters in pre-trigger literal FHA 4+ multifamily | 1,985,668 | 2,435,493 |
| Pre-trigger literal FHA 4+ share of all disabled renters | 36.3% | 44.5% |
| Pre-trigger share within literal FHA 4+ disabled universe | 63.4% | 70.6% |
| Combined accessible-feature deficit share of all disabled renters | 44.9% | 54.3% |

Note: the minimum/maximum values for the “within literal FHA 4+ universe” rows come from all feasible allocations of exact 4-unit buildings across the observed pre-1990, 1990-1999, and post-1999 portions of the indeterminate `BLD=05` bucket. The minimum share occurs when only the BLD=05 1990-1999 component and the BLD=05 post-1999 component are treated as exact 4-unit; the maximum occurs when only the BLD=05 pre-1990 component is treated as exact 4-unit. For disabled-household composition, the corresponding minimum occurs when only the disabled BLD=05 1990-1999 component and the disabled BLD=05 post-1999 component are treated as exact 4-unit; the maximum occurs when only the disabled BLD=05 pre-1990 component is treated as exact 4-unit.

## Top-line findings

- Public Census sources checked here do not isolate exact 4-unit buildings, but the remaining uncertainty is bounded: literal FHA 4+ renter stock falls between 48.5% and 59.3% of all renter households.
- Within the literal FHA 4+ renter universe, the pre-trigger share is bounded between 55.6% and 64.5%; the inclusive ACS proxy (`BLD=05-09`) yields 61.5%.
- For disabled renters, the pre-trigger share within the literal FHA 4+ universe is bounded between 63.4% and 70.6%; the inclusive ACS proxy yields 68.0%.
- Share of all disabled renter households living in pre-trigger literal FHA 4+ multifamily: between 36.3% and 44.5%.
- Combined date-gap plus post-1991 noncompliance deficit for all disabled renters is bounded between 44.9% and 54.3%.
- Inclusive proxy reference point: within the ACS 4+ proxy universe (`BLD=05-09`), 61.5% of renter households and 68.0% of disabled renter households are estimated to live in pre-trigger structures.

## Core stock counts

| Metric | Estimate |
|---|---:|
| Total renter-occupied units | 42,812,726 |
| Disabled renter households | 5,477,392 |
| Disabled share of all renter households | 12.8% |
| All-stock pre-trigger lower bound (pre-1990 only) | 64.3% |
| All-stock pre-trigger adjusted estimate | 65.7% |
| Literal FHA 4+ share of all renter stock, lower bound | 48.5% |
| Literal FHA 4+ share of all renter stock, upper bound | 59.3% |
| Literal FHA 4+ pre-trigger share within universe, minimum | 55.6% |
| Literal FHA 4+ pre-trigger share within universe, maximum | 64.5% |
| 4+ proxy share of all renter stock | 59.3% |
| 4+ proxy pre-trigger lower bound | 60.2% |
| 4+ proxy pre-trigger adjusted estimate | 61.5% |
| 4+ proxy pre-trigger share of all renter stock | 36.5% |

## Building stock by year built × building-size category × tenure

| Year built bucket | Building size category | Tenure | Weighted renter-occupied units | Share of all renter stock |
|---|---|---|---:|---:|
| 1939 or earlier | Mobile home / boat / RV / van | Renter-occupied | 17,651 | 0.0% |
| 1939 or earlier | 1 unit (detached or attached) | Renter-occupied | 1,763,503 | 4.1% |
| 1939 or earlier | 2 units | Renter-occupied | 776,447 | 1.8% |
| 1939 or earlier | 3-4 units (includes 4-unit buildings) | Renter-occupied | 813,631 | 1.9% |
| 1939 or earlier | 5-19 units | Renter-occupied | 870,327 | 2.0% |
| 1939 or earlier | 20-49 units | Renter-occupied | 482,158 | 1.1% |
| 1939 or earlier | 50+ units | Renter-occupied | 564,337 | 1.3% |
| 1940-49 | Mobile home / boat / RV / van | Renter-occupied | 8,770 | 0.0% |
| 1940-49 | 1 unit (detached or attached) | Renter-occupied | 892,648 | 2.1% |
| 1940-49 | 2 units | Renter-occupied | 199,735 | 0.5% |
| 1940-49 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 220,675 | 0.5% |
| 1940-49 | 5-19 units | Renter-occupied | 276,430 | 0.6% |
| 1940-49 | 20-49 units | Renter-occupied | 135,208 | 0.3% |
| 1940-49 | 50+ units | Renter-occupied | 173,372 | 0.4% |
| 1950-59 | Mobile home / boat / RV / van | Renter-occupied | 30,307 | 0.1% |
| 1950-59 | 1 unit (detached or attached) | Renter-occupied | 1,718,501 | 4.0% |
| 1950-59 | 2 units | Renter-occupied | 308,094 | 0.7% |
| 1950-59 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 352,905 | 0.8% |
| 1950-59 | 5-19 units | Renter-occupied | 539,899 | 1.3% |
| 1950-59 | 20-49 units | Renter-occupied | 226,439 | 0.5% |
| 1950-59 | 50+ units | Renter-occupied | 341,678 | 0.8% |
| 1960-69 | Mobile home / boat / RV / van | Renter-occupied | 89,392 | 0.2% |
| 1960-69 | 1 unit (detached or attached) | Renter-occupied | 1,469,921 | 3.4% |
| 1960-69 | 2 units | Renter-occupied | 325,695 | 0.8% |
| 1960-69 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 479,293 | 1.1% |
| 1960-69 | 5-19 units | Renter-occupied | 976,916 | 2.3% |
| 1960-69 | 20-49 units | Renter-occupied | 394,328 | 0.9% |
| 1960-69 | 50+ units | Renter-occupied | 634,188 | 1.5% |
| 1970-79 | Mobile home / boat / RV / van | Renter-occupied | 290,934 | 0.7% |
| 1970-79 | 1 unit (detached or attached) | Renter-occupied | 1,775,352 | 4.1% |
| 1970-79 | 2 units | Renter-occupied | 433,327 | 1.0% |
| 1970-79 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 802,964 | 1.9% |
| 1970-79 | 5-19 units | Renter-occupied | 1,737,292 | 4.1% |
| 1970-79 | 20-49 units | Renter-occupied | 603,757 | 1.4% |
| 1970-79 | 50+ units | Renter-occupied | 952,538 | 2.2% |
| 1980-89 | Mobile home / boat / RV / van | Renter-occupied | 326,912 | 0.8% |
| 1980-89 | 1 unit (detached or attached) | Renter-occupied | 1,486,779 | 3.5% |
| 1980-89 | 2 units | Renter-occupied | 347,829 | 0.8% |
| 1980-89 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 704,938 | 1.6% |
| 1980-89 | 5-19 units | Renter-occupied | 1,679,006 | 3.9% |
| 1980-89 | 20-49 units | Renter-occupied | 528,944 | 1.2% |
| 1980-89 | 50+ units | Renter-occupied | 795,659 | 1.9% |
| 1990-1999 | Mobile home / boat / RV / van | Renter-occupied | 366,159 | 0.9% |
| 1990-1999 | 1 unit (detached or attached) | Renter-occupied | 1,227,024 | 2.9% |
| 1990-1999 | 2 units | Renter-occupied | 250,070 | 0.6% |
| 1990-1999 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 495,611 | 1.2% |
| 1990-1999 | 5-19 units | Renter-occupied | 1,283,475 | 3.0% |
| 1990-1999 | 20-49 units | Renter-occupied | 421,018 | 1.0% |
| 1990-1999 | 50+ units | Renter-occupied | 625,501 | 1.5% |
| 2000-2009 | Mobile home / boat / RV / van | Renter-occupied | 213,333 | 0.5% |
| 2000-2009 | 1 unit (detached or attached) | Renter-occupied | 1,459,409 | 3.4% |
| 2000-2009 | 2 units | Renter-occupied | 223,993 | 0.5% |
| 2000-2009 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 428,724 | 1.0% |
| 2000-2009 | 5-19 units | Renter-occupied | 1,233,678 | 2.9% |
| 2000-2009 | 20-49 units | Renter-occupied | 480,462 | 1.1% |
| 2000-2009 | 50+ units | Renter-occupied | 938,766 | 2.2% |
| 2010-2019 | Mobile home / boat / RV / van | Renter-occupied | 157,737 | 0.4% |
| 2010-2019 | 1 unit (detached or attached) | Renter-occupied | 863,486 | 2.0% |
| 2010-2019 | 2 units | Renter-occupied | 188,571 | 0.4% |
| 2010-2019 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 305,946 | 0.7% |
| 2010-2019 | 5-19 units | Renter-occupied | 1,016,515 | 2.4% |
| 2010-2019 | 20-49 units | Renter-occupied | 635,663 | 1.5% |
| 2010-2019 | 50+ units | Renter-occupied | 1,660,530 | 3.9% |
| 2020 | Mobile home / boat / RV / van | Renter-occupied | 9,869 | 0.0% |
| 2020 | 1 unit (detached or attached) | Renter-occupied | 56,852 | 0.1% |
| 2020 | 2 units | Renter-occupied | 10,413 | 0.0% |
| 2020 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 14,679 | 0.0% |
| 2020 | 5-19 units | Renter-occupied | 53,773 | 0.1% |
| 2020 | 20-49 units | Renter-occupied | 46,126 | 0.1% |
| 2020 | 50+ units | Renter-occupied | 135,378 | 0.3% |
| 2021 | Mobile home / boat / RV / van | Renter-occupied | 5,968 | 0.0% |
| 2021 | 1 unit (detached or attached) | Renter-occupied | 47,200 | 0.1% |
| 2021 | 2 units | Renter-occupied | 6,782 | 0.0% |
| 2021 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 9,964 | 0.0% |
| 2021 | 5-19 units | Renter-occupied | 35,726 | 0.1% |
| 2021 | 20-49 units | Renter-occupied | 33,565 | 0.1% |
| 2021 | 50+ units | Renter-occupied | 100,613 | 0.2% |
| 2022 | Mobile home / boat / RV / van | Renter-occupied | 4,420 | 0.0% |
| 2022 | 1 unit (detached or attached) | Renter-occupied | 33,147 | 0.1% |
| 2022 | 2 units | Renter-occupied | 4,135 | 0.0% |
| 2022 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 6,681 | 0.0% |
| 2022 | 5-19 units | Renter-occupied | 21,332 | 0.0% |
| 2022 | 20-49 units | Renter-occupied | 18,899 | 0.0% |
| 2022 | 50+ units | Renter-occupied | 52,732 | 0.1% |
| 2023 | Mobile home / boat / RV / van | Renter-occupied | 2,783 | 0.0% |
| 2023 | 1 unit (detached or attached) | Renter-occupied | 16,526 | 0.0% |
| 2023 | 2 units | Renter-occupied | 2,595 | 0.0% |
| 2023 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 3,562 | 0.0% |
| 2023 | 5-19 units | Renter-occupied | 10,930 | 0.0% |
| 2023 | 20-49 units | Renter-occupied | 9,377 | 0.0% |
| 2023 | 50+ units | Renter-occupied | 24,962 | 0.1% |
| 2024 | Mobile home / boat / RV / van | Renter-occupied | 480 | 0.0% |
| 2024 | 1 unit (detached or attached) | Renter-occupied | 2,561 | 0.0% |
| 2024 | 2 units | Renter-occupied | 192 | 0.0% |
| 2024 | 3-4 units (includes 4-unit buildings) | Renter-occupied | 426 | 0.0% |
| 2024 | 5-19 units | Renter-occupied | 1,264 | 0.0% |
| 2024 | 20-49 units | Renter-occupied | 1,248 | 0.0% |
| 2024 | 50+ units | Renter-occupied | 3,216 | 0.0% |

Note: tenure is constant because Prompt 37's universe is renter-occupied households. The `3-4 units` rows use the ACS PUMS `BLD=05` bucket, which necessarily includes some 3-unit structures.

## By building size within the 4+ proxy universe

| Building size bucket | Weighted renter households | Share of all renter stock | Pre-trigger share within bucket | Pre-trigger share of all renter stock | Disabled share within bucket |
|---|---:|---:|---:|---:|---:|
| 3-4 unit bucket (includes 4-unit buildings) | 4,639,999 | 10.8% | 74.0% | 8.0% | 12.6% |
| 5-19 units | 9,736,563 | 22.7% | 64.0% | 14.6% | 11.2% |
| 20-49 units | 4,017,192 | 9.4% | 60.3% | 5.7% | 15.1% |
| 50+ units | 7,003,470 | 16.4% | 50.5% | 8.3% | 18.6% |

Note: the first row is a `3-4 unit` ACS PUMS bucket that necessarily includes some 3-unit buildings because the public microdata do not isolate exact 4-unit structures.

## Metro vs. non-metro

| Geography | Weighted renter households | 4+ proxy share of all renters | Pre-trigger share within 4+ proxy | Pre-trigger 4+ proxy share of all renters | Disabled pre-trigger 4+ proxy share of disabled renters | Disabled post-trigger 4+ proxy share of disabled renters |
|---|---:|---:|---:|---:|---:|---:|
| Metro | 38,000,825 | 61.8% | 61.2% | 37.8% | 46.1% | 21.9% |
| Non-metro | 4,811,901 | 40.1% | 65.9% | 26.4% | 35.5% | 15.7% |

## Disabled-renter statutory gap metrics

| Metric | Estimate |
|---|---:|
| Disabled renters in pre-trigger literal FHA 4+ multifamily, lower bound | 1,985,668 |
| Disabled renters in pre-trigger literal FHA 4+ multifamily, upper bound | 2,435,493 |
| Share of all disabled renters in pre-trigger literal FHA 4+ multifamily, lower bound | 36.3% |
| Share of all disabled renters in pre-trigger literal FHA 4+ multifamily, upper bound | 44.5% |
| Share of disabled renters in literal FHA 4+ multifamily who live in pre-trigger structures, minimum | 63.4% |
| Share of disabled renters in literal FHA 4+ multifamily who live in pre-trigger structures, maximum | 70.6% |
| Combined accessible-feature deficit share of all disabled renters, lower bound | 44.9% |
| Combined accessible-feature deficit share of all disabled renters, upper bound | 54.3% |
| Disabled renters in pre-trigger 4+ proxy multifamily | 2,435,493 |
| Disabled renters in post-trigger 4+ proxy multifamily | 1,147,721 |
| Share of disabled renters in 4+ proxy multifamily who live in pre-trigger structures | 68.0% |
| Share of disabled renters in 4+ proxy multifamily who live in post-trigger structures | 32.0% |
| Share of all disabled renters in pre-trigger 4+ proxy multifamily | 44.5% |
| Share of all disabled renters in post-trigger 4+ proxy multifamily | 21.0% |
| Post-trigger noncompliant share of all disabled renters (47% x post-trigger share) | 9.8% |
| Combined accessible-feature deficit share of all disabled renters | 54.3% |
| Combined accessible-feature deficit, disabled households | 2,974,922 |
| Combined accessible-feature deficit within disabled 4+ proxy households | 83.0% |

## Requested within-multifamily finding

Best exact-size formulation: public Census sources do not point-identify exact 4-unit buildings. For the literal FHA 4+ universe, the share of disabled renters in multifamily housing who live in pre-1991 structures is bounded between 63.4% and 70.6%. The corresponding count of disabled renter households living in pre-trigger literal FHA 4+ multifamily is bounded between 1.99 million and 2.44 million. The inclusive ACS proxy (`BLD=05-09`) yields 68.0% and 2.44 million.

## Interpretation for Prompt 37

Using public Census data, the exact 4-unit margin remains irreducible because available ACS and AHS public products collapse it into a combined `3-4` or `2-4` category. But the residual uncertainty is now tightly bounded and explicit. The only unresolved stock is the 4,639,999-household ACS `BLD=05` bucket (10.8% of all renters). Given that constraint, the literal FHA 4+ renter universe falls between 48.5% and 59.3% of all renter households, and its pre-trigger share falls between 55.6% and 64.5%. For disabled renters, the pre-trigger share of all disabled renter households in literal FHA 4+ multifamily falls between 36.3% and 44.5%. Applying the Appendix H 47% noncompliance figure to the post-trigger portion yields a combined accessible-feature deficit between 44.9% and 54.3% of all disabled renter households.

## Implications for the Note

These estimates sharpen the Note's institutional point without overstating the exact-size evidence. The verification regime matters not just for monitoring whether post-1991 buildings comply with FHA design-and-construction requirements, but also for identifying the scale of the accessibility deficit embedded in the pre-1991 stock. Even under the hard lower-bound construction that counts only unquestionably covered `5+` buildings, 63.4% of disabled renters in the literal FHA 4+ universe live in pre-trigger structures; under the most inclusive public-data construction, the figure reaches 70.6%. That bounded formulation cleanly distinguishes two problems: hidden noncompliance in nominally covered post-1991 buildings and the much larger legacy deficit residing in stock the statute never directly reached.

## Query diagnostics

- Geo lookup rows processed: 1,604,632
- Core housing rows processed: 1,604,632
- Geo rows unmatched to metro classification: 0
- Housing rows missing geo lookup: 0
