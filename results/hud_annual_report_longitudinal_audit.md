# HUD annual-report longitudinal disability-data audit memo

Date: 2026-04-16
Prepared for: p14
Primary artifact: `results/hud_annual_report_longitudinal_audit.md`

Inputs used:
- `/tmp/hud_ar_audit_summary.json`
- cached PDFs in `/tmp/hud_ar_audit/`
- limited confirmatory follow-up lookups for unrecovered public PDFs for FY 2008, FY 2009, FY 2014-2015, FY 2016, and FY 2017

## Bottom line

The strongest supported conclusion is not that HUD's annual fair-housing reports omitted disability altogether. The stronger and better-grounded conclusion is that disability data appears repeatedly but inconsistently. Across the recovered reports, HUD repeatedly reports disability complaint counts, reasonable-accommodation or modification issues, and sometimes disability-related participant or household characteristics. But the series is longitudinally unstable because titles change, year coverage is uneven, some reports are combined across multiple fiscal years, older documents use different terminology (`handicap`, `disabled/handicapped`), and many years remain unrecovered or only partially confirmed. The problem is therefore shifting formats, publication gaps, and incomplete recoverability, not total absence.

A second, note-relevant conclusion also holds: even in the more recent reports, disability is usually published as a separate protected-class count or issue category, not as a stable intersectional race-by-disability series. That makes the annual reports useful evidence of repeated disability recognition, but weak infrastructure for longitudinal intersectional analysis.

## Scope and method

I did not redo the full crawl. I used the already-produced summary JSON and cached PDFs as the core record. That cache contains 13 report artifacts covering the following fiscal years or year-groups:
- 1989
- 1991
- 2003-2006
- 2010
- 2012-2013
- 2018-2023

Expanded to single fiscal years, the recovered cache covers 15 fiscal years:
- 1989
- 1991
- 2003
- 2004
- 2005
- 2006
- 2010
- 2012
- 2013
- 2018
- 2019
- 2020
- 2021
- 2022
- 2023

Expanded-year gaps in the recovered cache are:
- 1990
- 1992-2002
- 2007-2009
- 2011
- 2014-2017

I then did only a light follow-up check on those gap years to distinguish between true nonexistence and public-but-unrecovered reports. That limited check confirmed public report PDFs for FY 2008, FY 2009, FY 2014-2015, FY 2016, and FY 2017. I did not fully re-audit those PDFs into the cache, so they are treated here as confirmed but unrecovered for the original pass.

## What counts as disability data in these reports

Across the recovered and lightly confirmed reports, disability data appears in four recurring forms:

1. Complaint-basis tables
   Disability often appears as one of the listed bases of complaints filed with HUD and FHAP agencies, and in many later years it is the largest single basis.

2. Issue tables and enforcement narratives
   Reasonable accommodation, reasonable modification, assistance animals, accessibility, and design-and-construction compliance recur as issue categories or case summaries.

3. Program participant or household characteristic tables
   Some reports include disability-related counts or shares for public housing residents, voucher households, homeless-assistance participants, or other HUD program beneficiaries.

4. Older civil-rights data collection narrative
   The earliest recovered reports use `handicap` terminology and frame disability data as part of HUD's broader civil-rights data-collection responsibilities.

## Timeline: recovered, unrecovered, and confirmed-public years

| Year(s) | Status | Evidence | Type of disability data located or inferred |
|---|---|---|---|
| 1989 | Recovered in cache | `Annual Report to Congress 1989` (URL file name `Annual-Report-1990.pdf`). The report states HUD collects civil-rights data on race, sex, ethnicity, `handicap`, and family characteristics; notes Section 202/8 elderly and handicapped units; and reports 713 handicap complaint bases (19 percent) after the 1988 amendments took effect. | Civil-rights data narrative; complaint-basis table; some program counts. |
| 1990 | Unrecovered; probable existence | No report was recovered in the cache. Probable existence is suggested by the adjacent filename pattern (`Annual-Report-1990.pdf` for the 1989 report and `Annual-Report-1992.pdf` for the 1991 report) and by the annual reporting structure. | Probable annual report, but no audited disability data recovered. |
| 1991 | Recovered in cache | `Annual Report to Congress 1991` reports civil-rights data on `handicap`; states 12 percent of reported PHA households were `Disabled/Handicapped`; and reports handicap as 20.6 percent of complaint bases. | Civil-rights data narrative; program participant table; complaint-basis table. |
| 1992-2002 | Unrecovered | No reports from this span were present in the cache, and the limited follow-up did not confirm public PDFs for these years. | No audited disability data recovered for this span. |
| 2003 | Recovered in cache | `State of Fair Housing FY 2003` reports disability complaints as 43 percent of all complaints, discusses reasonable accommodation, and includes program-level disability data such as physical/developmental disability among homeless entrants and `with disability` shares in housing tables. | Complaint-basis table; accommodation issues; program participant tables. |
| 2004 | Recovered in cache | `State of Fair Housing FY 2004` includes a dedicated `Reasonable Accommodations Guidance` section, complaint issue tables, and some `households reporting a disability` tables. | Accommodation guidance; complaint issue tables; some program tables. |
| 2005 | Recovered in cache | `State of Fair Housing FY 2005` includes disability-focused testing discussion, reasonable-accommodation inquiry tables, and accessibility/design content. | Complaint and inquiry data; accommodation/modification content; accessibility/design discussion. |
| 2006 | Recovered in cache | `State of Fair Housing FY 2006` reports disability complaints at 45 percent and race complaints at 44 percent; reports failure to make a reasonable accommodation at 20 percent of HUD complaints; and includes accessibility/design-and-construction material. | Complaint-basis and issue tables; accommodation/modification; accessibility/design content. |
| 2007 | Unrecovered; probable existence only | No FY 2007 report was recovered in the cache, and the limited follow-up did not confirm a public PDF. Probable existence is suggested by the surrounding annual sequence and the publicly confirmed FY 2008 and FY 2009 reports. | Probable annual report, but no audited disability data recovered. |
| 2008 | Public PDF confirmed, but not recovered into the original cache | Light follow-up confirmed `FY 2008 Annual Report on Fair Housing`. The report states disability was the most common complaint basis (4,675 complaints, 44 percent) and failure to make a reasonable accommodation was 2,401 complaints (23 percent). It also expressly states HUD's annual duty to report disability characteristics of program participants and beneficiaries. | Complaint-basis table; issue table; annual demographic-reporting duty expressly stated. |
| 2009 | Public PDF confirmed, but not recovered into the original cache | Light follow-up confirmed `Annual Report on Fair Housing FY 2009`. The report states disability was the most common complaint basis (44 percent) and failure to make a reasonable accommodation was 22 percent of issues. | Complaint-basis table; issue table. |
| 2010 | Recovered in cache | `Annual Report on Fair Housing FY 2010` reports disability complaints at 48 percent versus race at 34 percent, and reports failure to make a reasonable accommodation at 2,556 complaints (25 percent). | Complaint-basis table; issue table; accommodation case examples. |
| 2011 | Standalone report unrecovered; probable existence or subsumed reporting | No standalone FY 2011 report was recovered. The FY 2012-2013 combined report includes charts covering FY 2010-FY 2013, which shows continuity of annual tracking, but the limited follow-up did not confirm a standalone FY 2011 PDF. | Continuity of annual tracking is evident, but standalone FY 2011 recoverability remains unresolved. |
| 2012-2013 | Recovered in cache as a combined report | `Annual Report on Fair Housing FY 2012-2013` reports disability complaints at 53 percent in FY 2013 versus race at 28 percent, and reports failure to make a reasonable accommodation at 2,543 complaints (30 percent). It also includes disability-specific policy material such as the 2013 assistance-animal notice. | Combined-year complaint-basis and issue tables; accommodation policy guidance. |
| 2014-2015 | Public combined PDF confirmed, but not recovered into the original cache | Light follow-up confirmed `FHEO Annual Report FY 2014 & 2015`. The report is publicly available and expressly covers complaint data and HUD program demographics under the annual-report statutes, but I did not re-audit its disability tables page by page into the cache. | Public report confirmed; complaint/program-demographic reporting likely present; not fully re-audited here. |
| 2016 | Public PDF confirmed, but not recovered into the original cache | Light follow-up confirmed `HUD FHEO Annual Report to Congress — FY 2016`. The report confirms 8,385 complaints filed and continues annual fair-housing reporting under the statutory mandate; disability remains one of the expressly covered protected categories. | Public report confirmed; annual complaint/program reporting continues; not fully re-audited here. |
| 2017 | Public PDF confirmed, but not recovered into the original cache | Light follow-up confirmed `FHEO Annual Report FY 2017`. It reports disability as the largest complaint basis with 4,865 complaints (59.4 percent) and failure to make a reasonable accommodation at 3,366 complaints (41.1 percent). The report also references the 2017 HUD rental-housing discrimination study on mental disabilities. | Complaint-basis table; issue table; research mention. |
| 2018-2019 | Recovered in cache as a combined report | `Annual Report on Fair Housing FY 2018/2019` reports disability complaint counts of 4,705 (60.4 percent) in FY 2018 and 4,767 (61.7 percent) in FY 2019. It reports failure to make reasonable accommodation at 3,318 and 3,324 complaints, respectively. | Combined-year complaint-basis and issue tables; some program definitions/examples. |
| 2020 | Recovered in cache | `Annual Report on Fair Housing FY 2020` reports 4,612 disability complaints (60.9 percent) and includes disability-accessibility enforcement examples, including retrofit, modification, and assistance-animal relief. | Complaint-basis table; accommodation/accessibility case examples. |
| 2021 | Recovered in cache | `Annual Report on Fair Housing FY 2021` reports 4,791 disability complaints (57.0 percent) and 3,485 reasonable-accommodation issues (41.5 percent), with multiple disability accommodation case summaries. | Complaint-basis table; issue table; accommodation case examples. |
| 2022 | Recovered in cache | `Annual Report on Fair Housing FY 2022` reports 5,069 disability complaints (59.5 percent) and 3,767 reasonable-accommodation issues (44.2 percent), plus accommodation/modification settlements. | Complaint-basis table; issue table; accommodation/modification case examples. |
| 2023 | Recovered in cache | `State of Fair Housing FY 2023` reports 5,128 disability complaint bases and multiple reasonable-accommodation or modification case examples. The current note's draft materials already rely on the FY 2023 report for the proposition that HUD reports protected-class complaint counts separately rather than as race-by-disability cross-tabs. | Complaint-basis counts; accommodation/modification cases; separate-basis reporting rather than stable intersectional tabulation. |

## Main longitudinal patterns

### 1. Disability is repeatedly present, but the terminology and form shift over time

The earliest recovered reports do not use contemporary disability terminology consistently. In 1989 and 1991, the operative terms are `handicap` and `disabled/handicapped`. By 2003 and after, the reports shift to `disability`, `reasonable accommodation`, `reasonable modification`, `assistance animals`, and accessibility/design-and-construction language. That linguistic shift matters because a simple keyword search for `disability` would understate earlier reporting.

### 2. Complaint-basis reporting is the strongest continuity in the series

Whenever a report was recovered or lightly confirmed for the later period, disability appears as a complaint basis, and in the 2003-forward reports it is often the largest single basis. Examples:
- FY 2003: disability complaints are 43 percent.
- FY 2006: disability complaints are 45 percent, nearly equal to race at 44 percent.
- FY 2010: disability complaints are 48 percent.
- FY 2013: disability complaints are 53 percent.
- FY 2018: disability complaints are 60.4 percent.
- FY 2019: disability complaints are 61.7 percent.
- FY 2020: disability complaints are 60.9 percent.
- FY 2021: disability complaints are 57.0 percent.
- FY 2022: disability complaints are 59.5 percent.
- FY 2023: disability complaint bases total 5,128.

That continuity makes it impossible to say the annual reports ignored disability in a simple yes-or-no sense.

### 3. Reasonable accommodation/modification reporting becomes a second durable strand

Beginning in the 2003-2006 period and continuing through the 2020s, the reports repeatedly foreground reasonable accommodation and reasonable modification as issue categories or enforcement narratives. By the 2010s and 2020s, failure to make a reasonable accommodation is one of the largest recurring issue categories in the reports. This is an important form of disability reporting, but it is different from stable beneficiary-demographic reporting or cross-tabulated intersectional data.

### 4. Program participant and household disability tables appear intermittently, not uniformly

Some reports include program-beneficiary disability data, but not in a stable format across the entire series. Clear examples include:
- 1991 PHA data showing 12 percent `Disabled/Handicapped` households.
- 2003 tables reporting `with disability` shares in voucher-related data and disability shares among homeless entrants.
- 2004 references to `households reporting a disability` tables.
- scattered later appendices and program summaries, especially in the 2020s.

This matters because the reports do sometimes contain disability-demographic information beyond complaints, but those tables are not consistently recoverable year to year in a common schema.

### 5. The biggest longitudinal weakness is not silence but instability

The series has at least five kinds of instability:
- missing or unrecovered years;
- combined-year reports (2012-2013, 2018-2019, and publicly confirmed 2014-2015);
- shifting titles (`Annual Report to Congress`, `State of Fair Housing`, `Annual Report on Fair Housing`, `FHEO Annual Report`);
- OCR and terminology variation in older reports;
- changing table structures and emphasis from complaint statistics to policy guidance to program appendices.

These features make the reports a poor source for a clean uninterrupted longitudinal disability series, even though they are a strong source for proving repeated disability inclusion.

### 6. The annual reports remain weak for intersectional race-disability analysis

The reports repeatedly list disability and race as separate complaint bases. They do not, in the recovered materials, provide a stable published race-by-disability cross-tab that would support direct longitudinal intersectional analysis. That is consistent with the draft's existing footnote use of FY 2023 as evidence that HUD reports complaint data by protected class without publishing race-disability cross-tabulation.

## Best-supported statement for the note

The safest note-facing synthesis is:

HUD's own annual fair-housing reports repeatedly include disability, first through `handicap` and `disabled/handicapped` categories and later through disability complaint tables, reasonable-accommodation issue counts, and occasional beneficiary or household characteristics tables. But the inclusion is longitudinally inconsistent. The public record is interrupted by missing or unrecovered years, combined-year reports, title changes, shifting table formats, and the absence of a stable published race-by-disability series. The best historical characterization is therefore not total omission, but repeated yet unstable disability reporting.

## Caveats

1. This memo distinguishes between `recovered in the original cache` and `publicly confirmed in light follow-up`.
   The latter category improves the historical account of probable existence, but those reports were not reprocessed into the original summary JSON.

2. Some nonrecovered years may still have existed historically even though I could not confirm them quickly.
   That is especially plausible where annual-report sequencing strongly suggests continuity.

3. The reports are not identical instruments across time.
   Longitudinal comparison therefore requires caution even when disability data is present.

## Deliverable created

- `results/hud_annual_report_longitudinal_audit.md`
