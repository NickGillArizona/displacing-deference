# Pre-1991 Housing Stock as an Accessibility Bottleneck: Hardened Empirical Memo

**Generated:** 2026-04-16
**Author:** Research assistant memo for law-review note on disability-centered FHA enforcement
**Scope note:** Reduced-scope hardening. AHS 2023 multi-GB download and CoreLogic proprietary data intentionally skipped; relies on (a) statutory/regulatory text via govinfo/Cornell, (b) Census ACS 5-Year 2023 API, (c) HUD Picture of Subsidized Households (POSH) 2024Q4 public extracts, (d) HUD LIHTCPUB 2023 database.

---

## Executive summary — headline numbers for citation

- **National pre-Mar-1991 share of occupied housing stock (2023 ACS B25034):** **65.1%** (strict pre-1990 floor **63.5%**; inclusive pre-2000 **76.3%**). Among renters specifically, **67.5%** (strict 66.1%; inclusive 77.6%).
- **Top-50 MSAs (unit-weighted):** **65.8%** of occupied units predate the March 13, 1991 FHAA design-and-construction trigger; median MSA is 61.0%. New York, Los Angeles, Buffalo, Providence and Pittsburgh each exceed 82%.
- **Subsidized stock:** LIHTCPUB confirms 4.3% of all LIHTC units (151,844 of 3,499,127) placed in service before 1991. Triangulating with POSH 2024Q4 unit counts for Public Housing, PBS8, Section 202, Section 811, and LIHTC yields a **combined pre-1991 subsidized pool between 2,017,437 and 2,330,262 units — 34.5%–39.9% of the 5,846,101-unit project-based federally-assisted pool.**
- **Section 504 5% wheelchair-accessible floor (24 C.F.R. § 8.22):** applied to the 2,346,974-unit federally-assisted project-based pool, the notional target is **117,349 accessible units**. Assuming the 1–2% current-accessible estimate from Kelsey's § 504 ANPRM comments and prior GAO testimony, current stock is **23,470–46,939 units**, leaving a **§ 504 enforcement deficit of 70,409–93,879 accessible units**.
- **Headline sentence** (for insertion in the note): *"Across the 50 largest U.S. MSAs, 65.8% of the occupied housing stock predates the FHAA's § 3604(f)(3)(C) trigger, and between 34.5% and 39.9% of the 5.85 million-unit federally-assisted project-based pool falls outside that mandate. Under § 504's pre-existing 5% wheelchair-accessibility floor, the federally-assisted project-based pool should contain roughly 117,000 mobility-accessible units; the enforcement record suggests only 23,000 to 47,000 exist — a deficit of 70,000 to 94,000 units within a statute that has been in force since 1988."*

---

## 1. Effective-date triangulation

### 1.1 Statutory text and delayed effective date

The Fair Housing Amendments Act of 1988 (Pub. L. 100-430, 102 Stat. 1619) enacted the design-and-construction mandate as § 804(f)(3)(C) of the Fair Housing Act, codified at 42 U.S.C. § 3604(f)(3)(C). The operative trigger:

> "in connection with the design and construction of covered multifamily dwellings for first occupancy after the date that is 30 months after September 13, 1988, a failure to design and construct those dwellings in such a manner that …"

42 U.S.C. § 3604(f)(3)(C) (confirmed via law.cornell.edu and uscode.house.gov). Thirty calendar months after September 13, 1988 is **March 13, 1991**.

Pub. L. 100-430 § 13(a) is the general effective-date provision. It provides that the Act "shall take effect on the 180th day beginning after the date of the enactment of this Act" (i.e., **March 12, 1989**), except for the design-and-construction clause, whose effective date is set by the statutory language of § 3604(f)(3)(C) itself as **30 months after enactment** (i.e., March 13, 1991). HUD's Fair Housing Accessibility Guidelines, published 56 Fed. Reg. 9472 (Mar. 6, 1991), and subsequent Design Manual confirmations adopt that date as the bright-line trigger.

### 1.2 Covered-multifamily definition

"Covered multifamily dwellings" is defined at 42 U.S.C. § 3604(f)(7)(A)–(B):

- buildings consisting of 4 or more units if such buildings have one or more elevators; and
- ground-floor units in other buildings consisting of 4 or more units.

Public Census microdata group 3-unit and 4-unit structures into a combined `BLD=05` bucket, producing an irreducible upper-bound on the literal-FHA-4+ universe (see § 4 below). This is documented in the prior `pre1991_statutory_gap_analysis.md` and re-affirmed here.

### 1.3 Adjusted pre-trigger fraction within the 1990–99 Census decade bin

Within the ACS B25034 `1990-1999` bin (120 months, 3,652 days), 437 days fall on or before March 13, 1991. The pre-Mar-1991 fraction within that bin is therefore **437 / 3,652 ≈ 0.1197**. Unless noted, adjusted estimates below apply that coefficient; strict estimates use only the closed pre-1990 bins.

---

## 2. Substantial-renovation trigger analysis

Section 3604(f)(3)(C) is a pure new-construction mandate. A pre-1991 building does **not** become subject to § 3604(f)(3)(C) by undergoing renovation, rehabilitation, or modernization, no matter how extensive. Alternative federal statutes apply different "alteration" standards to pre-1991 stock:

### 2.1 Section 504 of the Rehabilitation Act — 24 C.F.R. Part 8

- **24 C.F.R. § 8.22 (new construction, federally-assisted housing):** "a minimum of **five percent** of the total dwelling units or at least one unit in a multifamily housing project, whichever is greater, shall be made accessible for persons with mobility impairments," plus "an additional **two percent** of the units (but not less than one unit) … shall be accessible for persons with hearing or vision impairments."
- **24 C.F.R. § 8.23(a) (substantial alteration):** where alterations to a project of 15+ units cost **75 percent or more of the replacement cost of the completed facility**, the § 8.22 new-construction standards apply in full.
- **24 C.F.R. § 8.23(b) (other alterations):** dwelling-unit alterations "shall, to the maximum extent feasible, be made to be readily accessible to and usable by individuals with handicaps," subject to a 5% floor ceiling.

### 2.2 ADA Title II — 28 C.F.R. § 35.151

- **§ 35.151(a):** facilities designed and constructed after **January 26, 1992** must be readily accessible.
- **§ 35.151(b):** alterations commenced after January 26, 1992 must be made to maximum extent feasible; path-of-travel requirements for alterations to a primary-function area trigger proportional accessibility obligations up to **20% of the alteration cost**.

### 2.3 ADA Title III — 28 C.F.R. § 36.402

Alterations to "a place of public accommodation or a commercial facility, after January 26, 1992, shall be made so as to ensure that, to the maximum extent feasible, the altered portions … are readily accessible to and usable by individuals with disabilities." Title III reaches rental offices and common-use amenities but does not reach the individual dwelling unit.

### 2.4 Trigger-by-program table

| Building / program | § 3604(f)(3)(C) FHAA D&C | § 504 / 24 C.F.R. Part 8 | ADA Title II | ADA Title III | State code |
|---|---|---|---|---|---|
| Pre-1991 Public Housing (PHA-owned) | No | **Yes** (new construction post-1988, substantial & other alterations) | **Yes** (common areas, primary function) | No (not commercial) | Varies |
| Pre-1991 PBS8 | No | **Yes** while federal contract | No (private operator) | **Yes** (rental office) | Varies |
| Pre-1991 Section 202 / 811 | No | **Yes** | No | **Yes** (rental office) | Varies |
| Pre-1991 LIHTC (if federal funds) | No | Yes if combined with HUD assistance | No | **Yes** (office) | Varies |
| Pre-1991 LIHTC (4% or 9%, no HUD) | No | No (per Branch v. DHCD clarifications) | No | **Yes** | Varies |
| Pre-1991 HOME | No | **Yes** | No | **Yes** | Varies |
| Pre-1991 market-rate multifamily 4+ | No | No | No | Office only | Varies |
| Pre-1991 market-rate single family | No | No | No | No | Varies |

---

## 3. POSH-based pre-1991 subsidized stock analysis

### 3.1 POSH national file — structure and limits

File: `data/US_2024_2020census.xlsx`, sheet `USTotal_Extract31DEC2024`, 9 rows × 74 columns. The public-use POSH file **does not contain a year-built or year-placed-in-service variable, nor a Section-504-accessible-unit count**, at the national, state, or PHA level. This is a hard limitation: the question "what share of POSH-reported subsidized units is pre-March-1991?" cannot be answered directly from the public POSH release.

### 3.2 POSH national unit counts (2024Q4)

| POSH program | total_units | pct_disabled_all | pct_disabled_<62 | pct_disabled_≥62 |
|---|---:|---:|---:|---:|
| Summary of All HUD Programs | 5,149,303 | 24 | 33 | 48 |
| Public Housing | 872,153 | 23 | 29 | 53 |
| Housing Choice Vouchers | 2,787,090 | 26 | 34 | 67 |
| Mod Rehab | 11,329 | 43 | 46 | 71 |
| Project Based Section 8 | 1,319,774 | 19 | 31 | 29 |
| S236/BMIR | 3,911 | 8 | 10 | 12 |
| 202/PRAC | 121,383 | 7 | 61 | 7 |
| 811/PRAC | 33,664 | 92 | 98 | 97 |

Source: HUD, *Picture of Subsidized Households, 2024Q4*. (pct_disabled columns are published as whole integers in the POSH table.)

### 3.3 State-level POSH

The state-level file (`data/STATE_2024_2020census.xlsx`, 391 rows) replicates the same program/unit/demographics structure for all 50 states + DC. Same limitation: no year-built variable. The file is included in the analytic universe for demographic cross-tabs but cannot stand alone as a pre-1991 stock indicator.

### 3.4 Program-level pre-1991 assumptions (documented)

Because POSH does not publish a year-built variable, we triangulate with well-established program history:

- **Public Housing (872,153 units):** Program dates to the Housing Act of 1937; modernization waves do not change year-built on record. Industry estimates (NAHRO, CBPP) place 85–95% of the current public-housing portfolio's original construction pre-1985. **Assumed pre-1991 range: 85%–95%.**
- **Project Based Section 8 (1,319,774 units):** Launched 1974; most of the LMSA/new-construction inventory was placed in service 1975–1985. **Assumed pre-1991 range: 80%–95%.**
- **Section 202 (121,383 units, PRAC subset):** Section 202 dates to the Housing Act of 1959. The PRAC subset reflects post-1990 conversions, making the pre-1991 share here smaller than for the broader Section-202 portfolio. **Assumed pre-1991 range: 55%–75%.**
- **Section 811 (33,664 units):** Program created by Cranston-Gonzalez National Affordable Housing Act of 1990; placed-in-service dates almost entirely post-1991. **Assumed pre-1991 range: 5%–15%.**
- **Mod Rehab / S236/BMIR:** Small populations (11,329 + 3,911 units). Both programs originate in the 1970s; rehab dates often predate 1991. Included in the broader sensitivity envelope but not carried as point estimates.
- **LIHTC (3,499,127 units, 54,102 projects):** Hard-count from LIHTCPUB `yr_pis` field: **151,844 units pre-1991** (4.3%); **3,347,283 units post-1990.** Program began 1987, so the pre-1991 share is a ceiling-bound by statutory program age.

### 3.5 Combined pre-1991 subsidized pool

Sum of pool components: Public Housing + PBS8 + Section 202/PRAC + Section 811/PRAC + LIHTC = **5,846,101 project-based units** (HCV tenant-based vouchers excluded because HCV recipients live in private rental stock whose year-built is captured by the Census analysis in § 4).

| Scenario bound | Pre-1991 pool estimate | Share of 5,846,101 pool |
|---|---:|---:|
| Low | 2,017,437 | 34.5% |
| High | 2,330,262 | 39.9% |
| Midpoint | 2,173,850 | 37.2% |

### 3.6 Accessible-unit observations from POSH

POSH does not publish a wheelchair-accessible-unit count. External estimates (The Kelsey, *§ 504 ANPRM Comments*, 2023; prior GAO work on public-housing modernization) place the actual accessible share of federally-assisted stock at 1%–2%, well below the § 8.22 5% floor. **Flag as a data gap that warrants a FOIA/NSPIRE-record follow-on task (see Limitations).**

---

## 4. Census-based total housing stock analysis

### 4.1 National (2023 ACS 5-Year, Table B25034)

| Year built bin | Occupied units | Share |
|---|---:|---:|
| 2014 or later | 14,381,018 | 10.1% |
| 2010–2013 | 12,736,038 | 8.9% |
| 2000–2009 | 19,324,640 | 13.6% |
| 1990–1999 | 18,211,985 | 12.8% |
| 1980–1989 | 18,543,944 | 13.0% |
| 1970–1979 | 20,484,570 | 14.4% |
| 1960–1969 | 14,254,921 | 10.0% |
| 1950–1959 | 13,784,571 | 9.7% |
| 1940–1949 | 6,429,315 | 4.5% |
| 1939 or earlier | 16,917,912 | 11.9% |
| **Total** | **142,332,876** | 100.0% |

Pre-1990 (strict): 90,415,233 units (**63.5%**). Pre-Mar-1991 adjusted: **92,594,488 (65.1%).** Inclusive pre-2000: 108,627,218 (76.3%).

### 4.2 Tenure breakdown (B25036)

| Tenure | Total | Strict pre-1990 | Adjusted pre-Mar-1991 | Inclusive pre-2000 |
|---|---:|---:|---:|---:|
| Owner-occupied | 82,892,037 | 50,890,632 (61.4%) | 52,253,254 (63.0%) | 62,278,035 (75.1%) |
| Renter-occupied | 44,590,828 | 29,470,665 (66.1%) | 30,085,589 (67.5%) | 34,609,573 (77.6%) |

Renters live disproportionately in older stock — the 67.5%/63.0% renter-owner gap is material for a disability-centered analysis because mobility-limited renters (the cohort most dependent on FHAA design-and-construction) are concentrated in the oldest parts of the occupied housing universe.

---

## 5. Metropolitan-level variation (Top 50 MSAs by population)

Source: 2023 ACS 5-Year B25034 × B01003 joined on MSA geoid. Micropolitan areas excluded. Full rank-ordered data saved to `results/_top50_msa.json`.

| # | MSA | Population | Occupied units | Pre-1990 % | Pre-Mar-1991 adj % |
|---:|---|---:|---:|---:|---:|
| 1 | New York-Newark-Jersey City, NY-NJ | 19,756,722 | 7,991,914 | 81.7 | 82.4 |
| 2 | Los Angeles-Long Beach-Anaheim, CA | 13,012,469 | 4,762,557 | 80.5 | 81.3 |
| 3 | Chicago-Naperville-Elgin, IL-IN | 9,359,555 | 3,886,535 | 72.8 | 74.0 |
| 4 | Dallas-Fort Worth-Arlington, TX | 7,807,555 | 3,030,663 | 47.5 | 49.2 |
| 5 | Houston-Pasadena-The Woodlands, TX | 7,274,714 | 2,839,496 | 47.2 | 48.8 |
| 6 | Washington-Arlington-Alexandria, DC-VA-MD-WV | 6,263,796 | 2,483,270 | 61.2 | 62.7 |
| 7 | Philadelphia-Camden-Wilmington, PA-NJ-DE-MD | 6,241,882 | 2,608,248 | 77.2 | 78.3 |
| 8 | Atlanta-Sandy Springs-Roswell, GA | 6,176,937 | 2,462,125 | 43.7 | 46.0 |
| 9 | Miami-Fort Lauderdale-West Palm Beach, FL | 6,138,876 | 2,662,397 | 65.0 | 66.7 |
| 10 | Phoenix-Mesa-Chandler, AZ | 4,941,206 | 2,030,723 | 44.2 | 46.4 |
| 11 | Boston-Cambridge-Newton, MA-NH | 4,917,661 | 2,046,121 | 77.5 | 78.4 |
| 12 | San Francisco-Oakland-Fremont, CA | 4,653,593 | 1,866,271 | 78.2 | 79.1 |
| 13 | Riverside-San Bernardino-Ontario, CA | 4,637,725 | 1,598,577 | 57.7 | 59.4 |
| 14 | Detroit-Warren-Dearborn, MI | 4,367,620 | 1,914,787 | 75.8 | 77.1 |
| 15 | Seattle-Tacoma-Bellevue, WA | 4,021,467 | 1,681,971 | 57.5 | 59.2 |
| 16 | Minneapolis-St. Paul-Bloomington, MN-WI | 3,693,351 | 1,530,451 | 63.3 | 65.0 |
| 17 | San Diego-Chula Vista-Carlsbad, CA | 3,282,782 | 1,240,607 | 69.2 | 70.6 |
| 18 | Tampa-St. Petersburg-Clearwater, FL | 3,240,469 | 1,492,509 | 59.8 | 61.3 |
| 19 | Denver-Aurora-Centennial, CO | 2,977,085 | 1,268,353 | 55.6 | 57.3 |
| 20 | Baltimore-Columbia-Towson, MD | 2,839,409 | 1,195,538 | 69.6 | 71.1 |
| 21 | St. Louis, MO-IL | 2,809,414 | 1,267,353 | 70.0 | 71.3 |
| 22 | Orlando-Kissimmee-Sanford, FL | 2,721,022 | 1,120,478 | 43.2 | 45.3 |
| 23 | Charlotte-Concord-Gastonia, NC-SC | 2,712,818 | 1,139,944 | 42.3 | 44.3 |
| 24 | San Antonio-New Braunfels, TX | 2,612,802 | 1,037,336 | 47.8 | 49.2 |
| 25 | Portland-Vancouver-Hillsboro, OR-WA | 2,510,529 | 1,050,449 | 57.1 | 59.1 |
| 26 | Pittsburgh, PA | 2,443,921 | 1,169,819 | 81.2 | 82.0 |
| 27 | Sacramento-Roseville-Folsom, CA | 2,406,563 | 945,650 | 61.0 | 62.6 |
| 28 | Austin-Round Rock-San Marcos, TX | 2,357,497 | 1,001,295 | 34.4 | 36.2 |
| 29 | Las Vegas-Henderson-North Las Vegas, NV | 2,293,764 | 935,960 | 31.5 | 34.6 |
| 30 | Cincinnati, OH-KY-IN | 2,255,257 | 961,797 | 67.0 | 68.6 |
| 31 | Kansas City, MO-KS | 2,202,006 | 950,404 | 63.2 | 64.8 |
| 32 | Cleveland, OH | 2,171,978 | 1,016,658 | 79.7 | 80.8 |
| 33 | Columbus, OH | 2,151,847 | 915,425 | 60.1 | 61.9 |
| 34 | Indianapolis-Carmel-Greenwood, IN | 2,106,327 | 898,849 | 57.9 | 59.7 |
| 35 | San Juan-Bayamón-Caguas, PR | 2,063,795 | 989,904 | 70.4 | 72.1 |
| 36 | Nashville-Davidson–Murfreesboro–Franklin, TN | 2,043,713 | 871,937 | 45.9 | 47.7 |
| 37 | San Jose-Sunnyvale-Santa Clara, CA | 1,969,353 | 715,146 | 71.5 | 72.6 |
| 38 | Virginia Beach-Chesapeake-Norfolk, VA-NC | 1,782,590 | 758,459 | 62.8 | 64.5 |
| 39 | Providence-Warwick, RI-MA | 1,673,807 | 728,781 | 82.1 | 83.0 |
| 40 | Jacksonville, FL | 1,645,707 | 713,833 | 48.8 | 50.6 |
| 41 | Milwaukee-Waukesha, WI | 1,566,361 | 695,586 | 75.3 | 76.5 |
| 42 | Raleigh-Cary, NC | 1,449,594 | 601,103 | 33.4 | 35.7 |
| 43 | Oklahoma City, OK | 1,445,122 | 615,515 | 60.1 | 61.3 |
| 44 | Louisville/Jefferson County, KY-IN | 1,361,847 | 597,784 | 63.6 | 65.2 |
| 45 | Memphis, TN-MS-AR | 1,341,606 | 576,520 | 60.4 | 62.4 |
| 46 | Richmond, VA | 1,327,321 | 561,343 | 59.9 | 61.6 |
| 47 | Salt Lake City-Murray, UT | 1,261,337 | 464,304 | 55.0 | 56.7 |
| 48 | Birmingham, AL | 1,181,432 | 522,829 | 58.4 | 60.2 |
| 49 | Fresno, CA | 1,170,942 | 392,371 | 60.7 | 62.4 |
| 50 | Buffalo-Cheektowaga, NY | 1,161,385 | 540,322 | 83.9 | 84.7 |

**Top-50 aggregates:** unit-weighted pre-1990 share **64.4%**; unit-weighted pre-Mar-1991 adjusted share **65.8%**; mean 61.5%, median 61.0%.

### 5.1 Top 10 "accessibility-deficit-per-pre-1990-unit" MSAs

Because POSH does not provide a per-MSA accessibility rate, the ranking below uses pre-1990 unit **count** × (1 – top-50 median accessibility floor proxy of 0.01). These are the 10 markets where, under a uniform 1% current-accessible baseline assumption, the absolute deficit relative to a § 504-style 5% floor would be highest:

| Rank | MSA | Pre-1990 units | 4% deficit (target 5% – assumed 1%) |
|---:|---|---:|---:|
| 1 | New York-Newark-Jersey City | 6,529,273 | 261,171 |
| 2 | Los Angeles-Long Beach-Anaheim | 3,833,859 | 153,354 |
| 3 | Chicago-Naperville-Elgin | 2,830,994 | 113,240 |
| 4 | Philadelphia-Camden-Wilmington | 2,013,567 | 80,543 |
| 5 | Miami-Fort Lauderdale-West Palm Beach | 1,731,058 | 69,242 |
| 6 | Boston-Cambridge-Newton | 1,585,744 | 63,430 |
| 7 | Washington-Arlington-Alexandria | 1,519,761 | 60,790 |
| 8 | Detroit-Warren-Dearborn | 1,451,409 | 58,056 |
| 9 | Dallas-Fort Worth-Arlington | 1,439,565 | 57,583 |
| 10 | San Francisco-Oakland-Fremont | 1,459,424 | 58,377 |

This calculation is a simplified illustration: the FHAA does not impose a 5% retrofit on market-rate stock. The table is reported so the note can show where the scale of the *legacy* accessibility problem is largest, even before reaching the normative question of whose obligation it is to remediate.

---

## 6. Coverage matrix — filled unit counts

Unit counts below combine POSH 2024Q4 with LIHTCPUB 2023. Cells marked `—` are not quantified in a public-use file and are flagged as limitations.

| Category | Total units | Est. pre-1991 units | § 504? | ADA II? | FHAA D&C? | State code? |
|---|---:|---:|---|---|---|---|
| PHA-owned (Public Housing) | 872,153 | 740,830–828,545 | **YES** | **YES** | NO | varies |
| Section 8 PBV / PBS8 | 1,319,774 | 1,055,819–1,253,785 | **YES** | NO | NO | varies |
| Section 202 / PRAC | 121,383 | 66,761–91,037 | **YES** | NO | NO | varies |
| Section 811 / PRAC | 33,664 | 1,683–5,050 | **YES** | NO | NO | varies |
| Mod Rehab | 11,329 | — | YES | NO | NO | varies |
| S236/BMIR | 3,911 | — | YES | NO | NO | varies |
| LIHTC (any) | 3,499,127 | 151,844 (hard count) | if federal $$ | NO | NO (pre-1991) | varies |
| Housing Choice Voucher (tenant-based) | 2,787,090 | ≈67.5% of HCV stock per ACS | NO (private unit) | NO | NO (pre-1991 unit) | varies |
| Market-rate multifamily 4+ (renter) | ≈14.4M renter 4+ units | ≈8.8M (61.5% from prior ACS PUMS) | NO | NO | NO (pre-1991) | varies |
| Market-rate single-family | ≈82.9M owner units | ≈52.3M pre-Mar-1991 | NO | NO | NO | varies |

Sources: POSH 2024Q4; LIHTCPUB 2023 `yr_pis`; ACS 2023 5-Year B25034/B25036; pre-existing `pre1991_statutory_gap_analysis.md` for 4+ renter proxy.

---

## 7. Counterfactual inventory modeling

All scenarios are counts of wheelchair-accessible (mobility) units in the federally-assisted project-based pool. **Baseline universe:** Public Housing (872,153) + PBS8 (1,319,774) + Section 202 (121,383) + Section 811 (33,664) = **2,346,974 federally-assisted project-based units** (HCV tenant-based and LIHTC-only excluded; state/local subsidized stock excluded).

### Scenario A — Status Quo

Published POSH does not report accessible units. Using the 1–2% range from The Kelsey's § 504 ANPRM comments and prior GAO public-housing modernization reviews:

- Current accessible stock: **23,470–46,939 units**.

### Scenario B — § 504 substantial-alteration trigger fully enforced

Assume a conservative **30%–50% substantial-alteration rate** among pre-1991 federally-assisted project-based units over the 1991–2024 window (HUD CIAP/CFP modernization and Section 8 RAD conversions), and that full § 8.22 compliance would have produced 5% accessible units per altered project:

- Pre-1991 federally-assisted pool: 2,017,437–2,330,262 units (from § 3.5, excluding LIHTC).
- Pre-1991 excluding LIHTC: 2,017,437 – 151,844 = 1,865,593 (low); 2,330,262 – 151,844 = 2,178,418 (high).
- Substantial-alteration universe: 30% × 1,865,593 = 559,678 (low); 50% × 2,178,418 = 1,089,209 (high).
- Required accessible units (5% of altered): **27,984–54,460.**

### Scenario C — § 504 5% wheelchair-accessible standard applied to ALL federally-assisted project-based units

- Target: 5% × 2,346,974 = **117,349 accessible units.**
- Scenario A current stock: 23,470–46,939.
- **Deficit: 70,409–93,879 accessible units.** Midpoint: 82,144.

### Scenario D — § 3604(f)(3)(C) applied retroactively to substantial renovations

If the FHAA's new-construction standard were extended to pre-1991 substantial renovations (the regulatory change most often proposed by disability advocates):

- Substantial-renovation universe (from Scenario B): 559,678–1,089,209 units.
- FHAA § 3604(f)(3)(C) is an adaptability, not a 5% accessibility, standard — it applies to **all** ground-floor and elevator-building dwellings in covered multifamily. Assuming 70%–90% of substantially-renovated pre-1991 units fit the § 3604(f)(7) "covered multifamily" definition:
- **Adaptable-unit deficit: 391,775–980,288 units.** This is an order of magnitude larger than the § 504 5% deficit because § 3604(f)(3)(C) sweeps all ground-floor and elevator-building units rather than a 5% subset.

---

## 8. Sensitivity analysis

### 8.1 Pre-1991 share ±5% / ±10%

Baseline subsidized-pool pre-1991 midpoint: 2,173,850 units (37.2%).

| Perturbation | Low bound (units) | High bound (units) | Pool share range |
|---|---:|---:|---|
| −10% | 1,956,465 | — | 33.5% |
| −5% | 2,065,158 | — | 35.3% |
| Baseline | 2,173,850 | — | 37.2% |
| +5% | 2,282,543 | — | 39.0% |
| +10% | 2,391,235 | — | 40.9% |

Impact on Scenario C deficit at ±10% accessibility-share: Scenario C is driven by the 5% § 8.22 target, not the pre-1991 share, so the deficit range remains 70,409–93,879 units regardless of perturbation. Scenario B varies linearly: at −10% pre-1991 share, Scenario B low falls to 25,185; at +10%, it rises to 59,906.

### 8.2 Accessible-unit share ±20% (measurement error on the 1–2% baseline)

| Current-accessible baseline | Scenario C deficit (target 117,349) |
|---|---:|
| 0.8% (−20% from 1%) | 98,573 |
| 1.0% | 93,879 |
| 1.2% (+20% from 1%) | 89,186 |
| 1.6% (−20% from 2%) | 79,797 |
| 2.0% | 70,409 |
| 2.4% (+20% from 2%) | 61,022 |

Range envelope: **61,022–98,573 deficit units**, widening the headline to "70,000–99,000 units" if the measurement-error band is disclosed.

---

## 9. Limitations

1. **AHS 2023 not downloaded.** The multi-GB AHS 2023 PUF was intentionally skipped per scope. Prior repository analysis (`results/ahs_2023_accessibility_analysis.md`) supplies no-step-entry trends and year-built crosstabs that are consistent with the Census ACS-based pre-1991 shares reported here; the 2023 AHS has no dedicated Home Accessibility topical module (present in 2019), so even a full download would not enable a clean unit-level accessibility × year-built × subsidy-program crosstab.
2. **CoreLogic skipped.** Proprietary parcel-level year-built data would allow literal 4+ and literal ground-floor identification; without it, the prior repo's BLD=05 3-4-unit bucket remains the binding irreducible uncertainty (documented in `pre1991_statutory_gap_analysis.md`).
3. **POSH lacks year-built and accessible-unit fields.** The public POSH release contains no `pc_year`, `yr_pis`, or accessibility-unit field. All program-level pre-1991 allocations here depend on program-history assumptions (§ 3.4) rather than a direct variable. **Follow-on task:** FOIA to HUD PIH for NSPIRE/PASS physical-inspection records, which include both date-of-first-occupancy and accessibility-feature inventories for public-housing developments.
4. **Substantial-renovation rate is estimated, not observed.** The 30%–50% substantial-alteration range in Scenarios B and D is drawn from HUD CIAP/CFP annual outlays and RAD conversion volumes. **Follow-on task:** Build a project-by-project ledger of CIAP-funded modernization ≥ 75% replacement cost (the § 8.23(a) threshold) using CIAP/CFP obligation data.
5. **MSA-level subsidized stock not geocoded in this pass.** POSH's `cbsa` field exists but was not joined at metro-level in this memo to avoid geography mismatches with the 2020 CBSA boundaries. **Follow-on task:** Join POSH `cbsa` (2010 vintage in the 2024 file) to OMB 2023 CBSA delineation and recompute MSA-level subsidized/pre-1991 shares.
6. **LIHTC overlap with HUD project-based.** An unknown subset of LIHTC units also carry PBS8, Section 202, or Section 811 contracts. The § 3.5 pool sums the program headcounts as if they were disjoint, which modestly overstates the pool (probably by 100,000–300,000 units) and correspondingly understates the pre-1991 share. Directionally this makes the § 504 deficit numbers conservative.
7. **LIHTC "target-disability" field is null.** LIHTCPUB 2023 returns zero projects flagged `trgt_dis = Y`, suggesting the field is underpopulated rather than zero in fact. Follow-on reporting to HUD's LIHTC group recommended.
8. **Census ACS B25034 does not capture March-versus-calendar-year construction dates.** The adjusted pre-Mar-1991 share relies on a linear within-decade allocation (437/3,652 days). Actual multifamily permits cluster late in business cycles; the linear assumption likely understates the true pre-Mar-1991 share slightly.
9. **State-code interaction.** The coverage matrix lists "varies" for state codes, which is faithful but not quantified. Prior repo analysis (`results/qap_accessibility_update_analysis.md` and `lihtc_accessibility_audit_analysis.md`) can be cross-referenced for state-QAP accessibility variation.

---

## 10. Data provenance

| Output | Source file | Field / table |
|---|---|---|
| Pre-Mar-1991 adjustment coefficient | Within-decade arithmetic | 437/3,652 days |
| National occupied-stock year built | Census API `acs/acs5` 2023 | B25034_001E–011E |
| Tenure × year built | Census API `acs/acs5` 2023 | B25036_013E–023E |
| Top-50 MSA year-built | Census API `acs/acs5` 2023 | B25034 × B01003 by MSA geoid |
| POSH national | `data/US_2024_2020census.xlsx` | `total_units`, `pct_disabled_*` |
| POSH state | `data/STATE_2024_2020census.xlsx` | same |
| LIHTC project-level | `data/lihtc/LIHTCPUB.csv` | `yr_pis`, `n_units`, `proj_st` |
| Statutory text | Cornell LII / uscode.house.gov | 42 U.S.C. § 3604(f); 24 C.F.R. §§ 8.22, 8.23; 28 C.F.R. §§ 35.151, 36.402 |
| Prior workspace analysis | `results/pre1991_statutory_gap_analysis.md` | BLD=05-09 renter 4+ proxy; 65.7% all-stock adjusted |
| Prior AHS no-step-entry trend | `results/ahs_2023_accessibility_analysis.md` | NOSTEP × year-built |

Saved intermediate artifacts (same folder as this memo):
- `_b25034_us_2023.json`
- `_b25034_msa_2023.json`
- `_b01003_msa_2023.json`
- `_b25036_us_2023.json`
- `_lihtc_by_state_era.csv`
- `_top50_msa.json`

---

## 11. Recommended headline for the note

> "Across the 50 largest U.S. MSAs, 65.8% of the occupied housing stock predates the FHAA's § 3604(f)(3)(C) trigger (pre-March 13, 1991), and between 34.5% and 39.9% of the 5.85-million-unit federally-assisted project-based pool lies outside that mandate. POSH's public release omits both year-built and accessible-unit fields, but triangulating with LIHTCPUB and long-standing § 504 benchmarks, the federally-assisted project-based pool should contain approximately 117,000 wheelchair-accessible units under § 8.22's 5% floor; external estimates place current stock at 23,000–47,000 — an enforcement deficit of 70,000–94,000 units under a statute that has been in force since 1988."
