## Appendix A-2: PUMS Replication Methodology

This Appendix provides full replication methodology for the American Community Survey Public Use Microdata Sample estimates reported in Part II.E and accompanying footnotes. For the database methodology underlying the case-classification analysis, see Appendix A. Footnote numbers in brackets refer to the corresponding footnotes in the main article text.

### Data Source

U.S. Census Bureau, American Community Survey 2020–2024 5-Year Public Use Microdata Sample (PUMS), accessed via the Census Bureau Data API on March 27, 2026.

**API endpoint**: `https://api.census.gov/data/2024/acs/acs5/pums`

The 2024 vintage of the ACS 5-Year PUMS covers survey years 2020 through 2024. This updates the 2019–2023 5-Year PUMS used in the original analysis.

**Vintage selection.** The 5-Year PUMS is used for all demographic parameters reported in the main text---disability prevalence by race, disability penalties in cost burden, and the racial cost-burden gap---because the AIAN renter-householder subpopulation is too small in the 1-Year PUMS for reliable estimation (n=670 unweighted records versus n=17,877 in the 5-Year, yielding standard-error reductions of approximately 50--60%). The 5-Year window (2020--2024) includes pandemic-era survey years in which temporary rental assistance and stimulus payments suppressed absolute cost-burden rates by approximately 6--8 percentage points relative to the 2019--2023 vintage; the disability *penalty* (the within-race differential between disabled and non-disabled cost-burden rates) is less affected because both numerator and denominator shift in the same direction. Absolute cost-burden rates from the 2023 ACS 1-Year PUMS are available in Appendix D for point-in-time comparison.

### Variable Definitions

| Variable | Description | Values Used |
|----------|-------------|-------------|
| SPORDER | Person number within household | =1 (householder only) |
| TEN | Tenure | =3 (rented) |
| RAC1P | Recoded detailed race code | 1=White alone, 2=Black/AA alone, 3=AIAN alone |
| DPHY | Ambulatory difficulty | 1=Yes, 2=No |
| DOUT | Independent living difficulty | 1=Yes, 2=No |
| GRPIP | Gross rent as % of household income | 1–100=percentage, 101=not computed |
| HINCP | Household income (past 12 months) | Integer (can be negative) |
| PWGTP | Person weight | Integer |

**Disability definition**: A householder is classified as disabled if DPHY=1 OR DOUT=1. This captures ambulatory difficulty and independent living difficulty—the two disability types most directly addressed by the physical accessibility and reasonable accommodation mandates of 42 U.S.C. § 3604(f)(3). This definition excludes hearing, vision, cognitive, and self-care difficulties, which are captured by other PUMS disability variables.

**Renter householder definition**: SPORDER=1 (person is the householder) AND TEN=3 (housing unit is rented). This restricts the analysis to householders, avoiding double-counting household members.

### Replication Queries

All queries follow this template:
```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,{variables}
  &for=state:*
  &SPORDER=1
  &TEN=3
  &RAC1P={race_code}
```

The API returns person-level microdata for all states. Weighted estimates are computed by summing PWGTP across the relevant subpopulation.

#### Query 1: Disability Prevalence by Race

*Supports the disability prevalence estimates reported in Part II.E, paragraph 2, and footnote [72].*

```
GET ...?get=PWGTP,DPHY,DOUT&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
```

**Results**:

| Race | Unweighted n | Weighted Total | Weighted Disabled | Prevalence |
|------|-------------|---------------|-------------------|------------|
| White alone (RAC1P=1) | 933,744 | 22,456,511 | 3,145,803 | 14.01% |
| Black/AA alone (RAC1P=2) | 241,220 | 8,457,493 | 1,232,009 | 14.57% |
| AIAN alone (RAC1P=3) | 17,877 | 332,361 | 43,475 | 13.08% |

#### Query 2: Cost Burden by Disability Status and Race

*Supports the cost-burden disability penalty estimates reported in Part II.E, paragraph 1, and footnotes [68a] and [71].*

```
GET ...?get=PWGTP,DPHY,DOUT,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
```

**Results**:

| Race | Disabled CB Rate | Non-Disabled CB Rate | Disability Penalty |
|------|-----------------|---------------------|-------------------|
| White alone | 54.7% | 37.8% | 16.9 percentage points |
| Black/AA alone | 56.3% | 46.2% | 10.1 percentage points |
| AIAN alone | 48.2% | 40.9% | 7.3 percentage points |

#### Query 3: GRPIP=101 Rate by Race

*Supports the GRPIP=101 analysis reported in Part II.E, paragraph 5, and footnotes [58] and [177].*

```
GET ...?get=PWGTP,DPHY,DOUT,HINCP,GRPIP&for=state:*&SPORDER=1&TEN=3&RAC1P={1,2,3}
```

**Results**:

| Race | GRPIP=101 Rate | Of which HINCP ≤ 0 | Of which HINCP > 0 (primarily no cash rent) |
|------|---------------|--------------------|---------------------------------|
| Black/AA alone | 19.3% | 3.8% | 15.5% |
| White alone | 15.7% | 2.6% | 13.1% |
| AIAN alone | 12.5% | 3.7% | 8.8% |

*Note: The "HINCP > 0" column is derived by subtraction (GRPIP=101 rate minus the share with HINCP ≤ 0). Both the total and HINCP ≤ 0 figures are computed directly from the microdata. The HINCP > 0 residual is predominantly no-cash-rent households, though a small number may reflect other Census coding conditions in which GRPIP cannot be computed despite positive income.*

### Sensitivity Analysis: Alternative Disability Definition

The primary analysis defines disability as DPHY=1 (ambulatory difficulty) or DOUT=1 (independent living difficulty). The Census Bureau's broader recode variable DIS=1 captures any of six disability types.

| Metric | DPHY/DOUT (Primary) | DIS=1 (Any Disability) |
|--------|---------------------|------------------------|
| White prevalence | 14.01% | 21.04% |
| Black prevalence | 14.57% | 20.28% |
| AIAN prevalence | 13.08% | 20.71% |
| White disability penalty | 16.9 percentage points | 14.7 percentage points |
| Black disability penalty | 10.1 percentage points | 9.2 percentage points |
| AIAN disability penalty | 7.3 percentage points | 6.6 percentage points |

Under the broader DIS=1 definition, disability prevalence rises substantially across all groups (to 20–21%), and the disability penalty narrows slightly but remains large (6.6–14.7 percentage points). The directional findings are robust: disability remains the dominant axis of housing cost burden under either definition.

### Comparison to Prior Estimates

| Metric | 2019-2023 5-Year | 2020-2024 5-Year | Change |
|--------|-----------------|-----------------|--------|
| Black disability prevalence (renter HH) | 14.53% | 14.57% | +0.04 percentage points |
| AIAN disability prevalence (renter HH) | 14.34% | 13.08% | -1.26 percentage points |
| White disability prevalence (renter HH) | 13.86% | 14.01% | +0.15 percentage points |
| White cost-burden disability penalty | 19.3 percentage points | 16.9 percentage points | -2.4 percentage points |
| Black cost-burden disability penalty | 12.6 percentage points | 10.1 percentage points | -2.5 percentage points |
| AIAN cost-burden disability penalty | 10.1 percentage points | 7.3 percentage points | -2.8 percentage points |

### Standard Errors via Successive-Differences Replication

**Disability Prevalence Standard Errors:**

| Race | Prevalence | SE | 95% CI |
|------|-----------|-----|--------|
| White alone | 14.01% | 0.049 percentage points | [13.91%, 14.10%] |
| Black/AA alone | 14.57% | 0.081 percentage points | [14.41%, 14.73%] |
| AIAN alone | 13.08% | 0.356 percentage points | [12.38%, 13.78%] |

**Disability Penalty:**

| Race | Penalty | SE | 95% CI |
|------|---------|-----|--------|
| White alone | 16.9 percentage points | 0.25 percentage points | [16.4 percentage points, 17.4 percentage points] |
| Black/AA alone | 10.1 percentage points | 0.43 percentage points | [9.2 percentage points, 10.9 percentage points] |
| AIAN alone | 7.3 percentage points | 1.40 percentage points | [4.6 percentage points, 10.0 percentage points] |

All penalties are statistically significantly greater than zero; the AIAN lower bound (4.6 percentage points) is 3.3 times the SE, confirming the finding even for the smallest sample group.

**GRPIP=101 Rate (Disabled Renters):**

| Race | Rate | SE | 95% CI |
|------|------|----|--------|
| Black/AA alone | 19.3% | 0.26 percentage points | [18.8%, 19.8%] |
| White alone | 15.7% | 0.16 percentage points | [15.4%, 16.0%] |
| AIAN alone | 12.5% | 0.80 percentage points | [11.0%, 14.1%] |

**Derived: Racial Cost-Burden Gap by Disability Status (Black − White):**

| Group | Gap | SE | 95% CI |
|-------|-----|-----|--------|
| Non-disabled renters | 8.4 percentage points | 0.16 percentage points | [8.1 percentage points, 8.7 percentage points] |
| Disabled renters | 1.6 percentage points | 0.45 percentage points | [0.7 percentage points, 2.4 percentage points] |

### Limitations

1. **Race coding**: RAC1P captures single-race identification only. Multiracial individuals are excluded.
2. **Disability definition scope**: The DPHY/DOUT definition captures mobility and independent-living difficulties most relevant to § 3604(f)(3) but excludes other disability types.
3. **Temporal coverage**: The 2020–2024 5-Year PUMS includes pandemic years (2020–2021), during which federal rental assistance temporarily altered housing cost burdens.
4. **Conditional independence assumption**: The place-level analysis assumes disability and renter status are conditionally independent within each race group.
5. **Hispanic/Latino overlap**: RAC1P is a race variable; Hispanic origin is captured separately by the HISP variable. The "White alone" and "AIAN alone" categories include Hispanic individuals.

### Replication Instructions

The analysis can be replicated using any HTTP client capable of querying the Census Bureau Data API. No API key is required.

```python
import urllib.request, json

base = 'https://api.census.gov/data/2024/acs/acs5/pums'

# Disability prevalence for Black renter householders
url = f'{base}?get=PWGTP,DPHY,DOUT&for=state:*&SPORDER=1&TEN=3&RAC1P=2'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read())

rows = data[1:]  # skip header
total_weight = sum(int(r[0]) for r in rows)
disabled_weight = sum(int(r[0]) for r in rows if r[1] == '1' or r[2] == '1')
prevalence = disabled_weight / total_weight * 100
print(f'Black renter householder disability prevalence: {prevalence:.2f}%')
```

### Data Access

U.S. Census Bureau, American Community Survey 2020–2024 5-Year Public Use Microdata Sample (PUMS), https://api.census.gov/data/2024/acs/acs5/pums (last accessed Mar. 27, 2026).

Analysis conducted March 27, 2026.

---
