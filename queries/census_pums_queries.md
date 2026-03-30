# Census PUMS API Queries

All queries use the ACS 2020-2024 5-Year PUMS endpoint. No API key required.

**Base URL:** `https://api.census.gov/data/2024/acs/acs5/pums`

**Common filters:** `&SPORDER=1&TEN=3` (renter householders only)

---

## Query 1: Disability Prevalence by Race

*Supports Part II.E, paragraph 2, and footnote [72].*

```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,DPHY,DOUT
  &for=state:*
  &SPORDER=1
  &TEN=3
  &RAC1P={1,2,3}
```

Run once per race code: RAC1P=1 (White), RAC1P=2 (Black/AA), RAC1P=3 (AIAN).

**Disability definition:** DPHY=1 OR DOUT=1

---

## Query 2: Cost Burden by Disability Status and Race

*Supports Part II.E, paragraph 1, and footnotes [68a] and [71].*

```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,DPHY,DOUT,GRPIP
  &for=state:*
  &SPORDER=1
  &TEN=3
  &RAC1P={1,2,3}
```

**Cost burden:** GRPIP > 30, excluding GRPIP=101

---

## Query 3: GRPIP=101 Rate by Race

*Supports Part II.E, paragraph 5, and footnotes [58] and [177].*

```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,DPHY,DOUT,HINCP,GRPIP
  &for=state:*
  &SPORDER=1
  &TEN=3
  &RAC1P={1,2,3}
```

---

## Query 4: Hispanic/Latino Analysis

*Supports Appendix A-3, Section E.*

```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,DPHY,DOUT,GRPIP,RAC1P,HISP
  &for=state:*
  &SPORDER=1
  &TEN=3
```

**Hispanic filter:** HISP != 01

---

## Query 5: Housing Adequacy and Building Stock

*Supports Appendix A-3, Section F.*

```
GET https://api.census.gov/data/2024/acs/acs5/pums
  ?get=PWGTP,DPHY,DOUT,PLM,KIT,RMSP,NP,YRBLT,BLD,RAC1P
  &for=state:*
  &SPORDER=1
  &TEN=3
```

**FHA Section 3604(f)(3)(C) coverage estimate:**
- BLD in {5,6,7,8,9} (buildings with 3+ apartments, proxy for 4+ units)
- AND YRBLT in 1990-or-later categories

---

## Variable Definitions

| Variable | Description | Values Used |
|----------|-------------|-------------|
| SPORDER | Person number within household | =1 (householder only) |
| TEN | Tenure | =3 (rented) |
| RAC1P | Recoded detailed race code | 1=White, 2=Black/AA, 3=AIAN |
| DPHY | Ambulatory difficulty | 1=Yes, 2=No |
| DOUT | Independent living difficulty | 1=Yes, 2=No |
| GRPIP | Gross rent as % of household income | 1-100=%, 101=not computed |
| HINCP | Household income (past 12 months) | Integer (can be negative) |
| HISP | Hispanic origin | 01=Not Hispanic, 02-24=Hispanic |
| PLM | Plumbing facilities | 1=Yes, 2=No |
| KIT | Kitchen facilities | 1=Yes, 2=No |
| RMSP | Number of rooms | Integer |
| NP | Number of persons | Integer |
| YRBLT | Year structure built | Coded categories |
| BLD | Building type | 5-9 = 3+ apartment buildings |
| PWGTP | Person weight | Integer |
