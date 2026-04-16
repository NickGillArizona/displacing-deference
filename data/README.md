# Data Directory Contents

This directory holds the source datasets the replication pipeline depends on. Most files are committed to the repository; a few large external downloads are retrieved on demand because they exceed practical git-storage size or come from rate-limited APIs.

## Committed in this repo

| Path | Source | Used by |
|---|---|---|
| `FHA_Unified_Database.json` | Built from `FHA_RA_Database_unified_*.json` + `FHA_3604_Database_unified_*.json` via `scripts/build_unified_db.py` (parent workspace) | All hypothesis-test scripts (`h1_h2_analysis.py`, `h5_analysis.py`, `h6_analysis.py`, `h7_analysis.py`, `h8_analysis.py`), `robustness_checks.py`, `supplemental_batch.py` |
| `FHA_RA_Database_unified_20260328_090852.json` | CourtListener REST API (§3604(f) reasonable-accommodation screen) | Source corpus 1 for unified database |
| `FHA_3604_Database_unified_20260328_104352.json` | CourtListener REST API (§3604 general screen) | Source corpus 2 for unified database |
| HUD administrative datasets (CDBG, REAC/NSPIRE, POSH, HMDA rollups) | HUD User, huduser.gov | `cdbg_analysis.py`, `reac_analysis.py`, `posh_analysis.py`, `cdbg_accessibility_gap_analysis.py` |
| `lihtc/` + `lihtcpub.zip` | HUD LIHTC public database (huduser.gov/portal/datasets/lihtc.html) | `lihtc_accessibility_audit.py` |
| `australia_sda/` | NDIS (Australia) Specialist Disability Accommodation participant + dwellings snapshot | `australia_sda_analysis` (comparative accessibility benchmark) |
| `CDBG_Expend_NatlAll.xlsx` | HUD IDIS, CDBG national expenditure rollup (FY2005–2024) | `cdbg_analysis.py`, `cdbg_accessibility_gap_analysis.py` |
| `Disability-Forward-QAP-Advocacy-Guide.{pdf,txt}` | Disability Forward | QAP accessibility scan (qualitative input) |
| `The-Kelsey-504-ANPRM-Comments.{pdf,txt}` | The Kelsey (public comments on HUD 504 ANPRM) | Safe-harbor architecture (Appendix J) |
| `The-Kelsey-State-LIHTC-Accessibility-Factsheet*` | The Kelsey | `lihtc_accessibility_audit.py` |

## NOT in the repo — retrieve these manually

### `ahs_accessibility/` (~423 MB)

Source: Census Bureau / HUD — American Housing Survey Public Use Files.

**Required files:**

```
ahs_accessibility/
├── raw/
│   ├── 2019 AHS Table Specifications and PUF Estimates for User Verification.xlsx
│   ├── AHS 2011 National PUF v3.0 Flat CSV.zip
│   ├── AHS 2011 National Value Labels Package.zip
│   ├── AHS 2019 National PUF v1.1 Flat CSV.zip
│   ├── AHS 2019 Value Labels Package.zip
│   └── AHS 2023 National PUF v1.0 Flat CSV.zip  (or equivalent)
└── extracted/
    ├── AHS_2011N_Value_Labels.csv
    ├── AHS_2019_Value_Labels.csv
    ├── AHS_2023_Value_Labels.csv
    ├── Apply_AHS_Formats.SAS
    └── READ_ME_American_Housing_Survey_2011_Value_Labels_Package.pdf
```

**How to retrieve:**

1. Go to the Census AHS page: https://www.census.gov/programs-surveys/ahs/data/2023.html (and the 2011/2019 equivalents).
2. Download the National PUF Flat CSV and Value Labels zips for 2011, 2019, and 2023.
3. Unzip into `data/ahs_accessibility/raw/` and `data/ahs_accessibility/extracted/` as shown above.
4. Re-run `scripts/ahs_2023_accessibility_analysis.py` to reproduce `results/ahs_2023_accessibility_results.json` and the associated analysis memo.

**Why not committed:** 423 MB total; Census publishes the file directly and updates the series annually, so it's cleaner to fetch from the canonical source than to vendor a snapshot here.

## License

Code in this directory (none at time of writing): MIT (see `/LICENSE`).
Data: varies by source. HUD datasets are public domain under federal-works rules; Census AHS data is public domain; NDIS Australia SDA data is released under Creative Commons; The Kelsey materials are used per their publication terms. See `/LICENSE-DATA` for the aggregate terms applied to derivative data products in this repository.
