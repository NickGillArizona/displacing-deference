# Appendix L: HUD Administrative Data Analysis

This appendix documents the methodology and detailed findings from three HUD administrative datasets analyzed to support the institutional-infrastructure arguments in Parts I, III, and IV of the Note. All source data are publicly available from HUD and Data.gov.

---

## L.1 CDBG National Accomplishment Reports

**Source:** U.S. Dep't of Hous. & Urban Dev., CDBG National Accomplishment Reports (FY2005–FY2024), https://files.hudexchange.info/resources/documents/CDBG_Accomp_Natl.xlsx

**Unit of analysis:** Persons/households served (accomplishments), not dollar expenditures.

**Fiscal years covered:** FY2005–FY2024 (20 years).

### Activity Code Inventory

HUD's CDBG accomplishment system uses approximately 50 activity codes organized into categories: housing (12+13+14A–14J+16A), public services (03T+05A–05Z), public improvements (03A–03Z), and economic development. Of these, exactly two are disability-specific:

| Code | Name | Category |
|------|------|----------|
| 05B | Services for Persons with Disabilities | Public Services |
| 03B | Facility for Persons with Disabilities | Public Improvements |

No code covers housing accessibility, ADA compliance, disability-specific housing rehabilitation, or accessible-unit modifications. Housing rehabilitation codes 14A–14J may include some accessibility work, but the system does not track such spending separately. Code 05J (Fair Housing Activities) contains no disability subcategory despite disability being a protected class under the Fair Housing Act.

### Twenty-Year Summary Statistics

| Metric | Value |
|--------|-------|
| Total CDBG formula grant appropriations (FY2005–FY2024) | $67.7 billion |
| 05B (disability services) total beneficiaries | 4,610,160 |
| 03B (disability facilities) total beneficiaries | 765,191 |
| Combined disability share of public service beneficiaries | 2.51% |
| Combined disability share of public improvement beneficiaries | 1.32% |

### Disability Facility Construction Trend (Code 03B)

| Period | Average Annual 03B Beneficiaries |
|--------|----------------------------------|
| FY2005–2009 | 68,803 |
| FY2010–2014 | 34,638 |
| FY2015–2019 | 20,309 |
| FY2019–2023 | 24,315 |
| **Change, FY2005–2009 to FY2019–2023** | **−64.7%** |

### Year-by-Year Detail

| Fiscal Year | 05B Beneficiaries | 03B Beneficiaries | Combined | 05J Fair Housing | CDBG Allocation ($B) |
|-------------|-------------------|-------------------|----------|------------------|---------------------|
| 2005 | 154,149 | 107,768 | 261,917 | 86,413 | 4.117 |
| 2006 | 178,952 | 6,941 | 185,893 | 74,260 | 3.711 |
| 2007 | 73,002 | 124,795 | 197,797 | 118,437 | 3.711 |
| 2008 | 116,459 | 22,852 | 139,311 | 99,420 | 3.593 |
| 2009 | 145,854 | 81,661 | 227,515 | 97,757 | 3.642 |
| 2010 | 115,498 | 43,962 | 159,460 | 62,515 | 3.948 |
| 2011 | 148,827 | 36,106 | 184,933 | 109,674 | 3.303 |
| 2012 | 141,560 | 28,548 | 170,108 | 40,504 | 2.948 |
| 2013 | 81,900 | 50,209 | 132,109 | 93,072 | 3.078 |
| 2014 | 141,181 | 14,466 | 155,647 | 170,103 | 3.030 |
| 2015 | 86,779 | 16,827 | 103,606 | 47,961 | 3.066 |
| 2016 | 339,590 | 20,257 | 359,847 | 46,788 | 3.000 |
| 2017 | 145,857 | 15,545 | 161,402 | 78,961 | 3.000 |
| 2018 | 429,399 | 19,328 | 448,727 | 63,729 | 3.365 |
| 2019 | 427,391 | 28,921 | 456,312 | 64,668 | 3.365 |
| 2020 | 488,625 | 16,817 | 505,442 | 95,992 | 3.425 |
| 2021 | 650,273 | 249 | 650,522 | 2,659 | 3.450 |
| 2022 | 53,757 | 14,966 | 68,723 | 90,755 | 3.300 |
| 2023 | 597,640 | 60,620 | 658,260 | 151,655 | 3.300 |
| 2024 | 93,467 | 54,353 | 147,820 | 49,746 | 3.300 |

**FY2021 anomaly:** The 05B share spikes to 46.6% of public services in FY2021, reflecting depressed overall public service numbers (likely COVID-related), not increased disability spending. The 03B figure for FY2021 (249) is also anomalously low.

### Caveats

- Grantees may spend on disability accessibility under generic rehabilitation codes (14A–14J); the 2.2% disability share captures only spending coded specifically to disability. Actual disability-related spending may be higher but is unmeasurable—which is itself the point.
- CDBG is one of several federal housing programs. HOME, HOPWA, Section 811, and other programs may have disability-specific reporting that CDBG lacks. The CDBG finding should not be generalized to all federal housing spending without checking.

---

## L.2 Picture of Subsidized Households (POSH)

**Source:** HUD USER, A Picture of Subsidized Households: 2024, https://www.huduser.gov/portal/datasets/assthsg.html

**Data dictionary:** https://www.huduser.gov/portal/datasets/pictures/dictionary_2024.pdf

**Snapshot date:** December 31, 2024.

### National Disability Estimates by Program

| Program | Total Units | Weighted Disability Rate | Est. Disabled Households |
|---------|-------------|--------------------------|--------------------------|
| Housing Choice Vouchers | 2,787,090 | 45.2% | 1,096,529 |
| Project-Based Section 8 | 1,319,774 | 29.9% | 365,946 |
| Public Housing | 872,153 | 38.1% | 294,080 |
| Section 811/PRAC | 33,664 | 97.9% | 30,501 |
| Section 202/PRAC | 121,383 | 7.8% | 9,165 |
| Mod Rehab | 11,329 | 55.5% | 8,457 |
| **All HUD Programs** | **5,149,303** | **39.3%** | **~1,801,784** |

### Methodology

The weighted household disability rate (39.3%) combines under-62 and 62-and-over disability rates using total household counts per program as weights. The formula: for each program, `disability_rate = (pct_disabled_lt62 × share_under_62) + (pct_disabled_ge62 × share_62_plus)`, then weighted across programs by household count.

### Caveats

- POSH reports disability of the household head, spouse, or co-head, not all household members. The all-persons disability rate is lower (approximately 24%).
- Race-by-disability cross-tabulation is not available in the published POSH data. The 67% minority household rate and 39.3% disability rate imply substantial intersectional exposure, but a precise cross-tabulation cannot be computed from these data.
- The weighted 39.3% is an estimate; HUD does not publish a single aggregate disability rate.

---

## L.3 REAC/NSPIRE Inspection Score Data

**Sources:**
- HUD Real Estate Assessment Center, Public Housing Physical Inspection Scores (dataset, Aug. 2025)
- HUD Real Estate Assessment Center, Multifamily Physical Inspection Scores (dataset, Aug. 2025)
- https://www.hud.gov/program_offices/public_indian_housing/reac

### Scale of the Existing Inspection Infrastructure

| Metric | Public Housing | Multifamily | Combined |
|--------|---------------|-------------|----------|
| Properties inspected | 6,190 | 28,459 | **34,649** |
| Date range | Jun 2013–Jul 2025 | Feb 2013–Aug 2025 | ~12 years |
| States/territories | 54 | 55 | Nationwide |
| NSPIRE protocol share | 49.3% | 56.4% | ~55% |
| Mean score | 83.1 | 89.4 | 88.3 |
| Failure rate (<60) | 10.5% | 2.8% | 4.2% |

### What the Published Inspection Schema Contains

Both datasets share a nearly identical 18–20 column schema consisting exclusively of:
- Property identification (ID, name, address)
- Geographic identifiers (city, county, CBSA, state, zip, lat/long)
- A single aggregate inspection result (INSPECTION_ID, INSPECTION_SCORE, INSPECTION_DATE, INSPECTION_PROTOCOL)
- Public housing file adds PHA_CODE and PHA_NAME

The only inspection output is a **single integer score (0–100)** per property per inspection cycle.

### What the Published Inspection Schema Does NOT Contain

Neither dataset contains:
- Any sub-scores or inspection category breakdowns
- Any column referencing accessibility, disability, ADA, Section 504, design-and-construction, fair housing, or physical barriers
- Any indication of what specific deficiency items were assessed
- Any data on compliance with section 3604(f)(3)(C) requirements

**Verification method:** Comprehensive keyword searches across every string column in both files for "accessib," "disab," "ada," "section 504," "design and construction," "fair housing," and "barrier" returned only incidental matches in property names and street addresses (e.g., properties named "Accessible Apts. No 1" or addresses on "Ada Street").

### NSPIRE Transition and Failure-Rate Impact

| Protocol | Public Housing Failure Rate | Multifamily Failure Rate |
|----------|-----------------------------|--------------------------|
| UPCS (legacy) | 4.4% | 0.9% |
| NSPIRE (new) | 16.8% | 4.2% |
| **Increase factor** | **3.8×** | **4.7×** |

The NSPIRE protocol transition is ongoing (approximately 55% of inspections now use NSPIRE). The sharp increase in detected failures under NSPIRE demonstrates that updated inspection standards can materially increase deficiency detection in the same housing stock—and creates a natural regulatory insertion point for an accessibility compliance module.

### Caveats

- The published score data prove that the inspection architecture does not systematically assess or report accessibility outputs. They do not prove that inspectors never observe accessibility-related conditions during visits.
- No unit counts are available in the inspection datasets. The data is at the property level, not the unit level.
- The geographic REAC-to-litigation correlation is weak (Spearman rho = −0.285, p = 0.038) and should not be cited as a causal relationship.

---

## L.4 FHEO Historical Enforcement Data

**Source:** Data.gov, FHEO Filed Title VIII Complaints and Cases by Year and State (2000–2019).

### HUD-Direct Charge Rate (2019)

| Metric | Value |
|--------|-------|
| FHEO filed cases | 7,801 |
| HUD-direct reasonable-cause charges | 7 |
| Charge rate | 0.09% |
| States producing charges | CO (1), GA (1), MA (1), OR (1), PA (2), RI (1) |

This figure captures charges issued by HUD (through FHEO) only, not charges issued by FHAP state and local agencies. The NFHA 2025 Report shows 37 charges for 2019; the difference (30) represents FHAP-agency cause determinations. The 2014–2020 average is approximately 30 HUD-direct charges per year; 2019 may reflect internal processing delays or staffing patterns.

### Disability Share of FHEO-Filed Cases (2000–2019)

| Year | Disability-Basis Cases | Disability Share |
|------|----------------------|------------------|
| 2000 | 2,454 | 34.5% |
| 2005 | 3,967 | 42.0% |
| 2010 | 4,878 | 47.2% |
| 2015 | 4,572 | 55.7% |
| 2019 | 4,848 | 62.1% |

Cases may list multiple bases; the disability count is not mutually exclusive with other protected-class counts. The 2024 NFHA figure (54.6%) uses a different denominator (all complaints across FHOs, HUD, FHAP agencies, and DOJ) and is not directly comparable to the FHEO-only series.

---

## File Inventory

| File | Location | Description |
|------|----------|-------------|
| `CDBG_Accomp_Natl.xlsx` | `data/` | CDBG national accomplishments (FY2005–2024) |
| `STATE_2024_2020census.xlsx` | `data/` | POSH state-level data (2024) |
| `US_2024_2020census.xlsx` | `data/` | POSH national-level data (2024) |
| `dictionary_2024.pdf` | `data/` | POSH data dictionary |
| `public_housing_physical_inspection_scores.xlsx` | `data/` | REAC public housing inspection scores |
| `multifamily_physical_inspection_scores.xlsx` | `data/` | REAC multifamily inspection scores |
| `fha-cases-by-year.xls` | `data/` | FHEO filed cases by year/state (2000–2019) |
| `cdbg_results.json` | `results/` | CDBG analysis output |
| `posh_results.json` | `results/` | POSH analysis output |
| `reac_results.json` | `results/` | REAC analysis output |
