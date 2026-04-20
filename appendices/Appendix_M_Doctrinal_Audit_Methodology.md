# Appendix M: Doctrinal Audit Methodology

## M.1 Overview

This Appendix documents the fourteen doctrinal and administrative-record audits cited in the footnotes of *Duty Without Data: Part 121, Feature Verification, and Fair Housing's Missing Middle* (note_v100.md). It complements Appendix L (HUD Administrative Data) by specifically tying the Note's doctrinal footnote apparatus to the underlying audit memoranda, search strings, inclusion/exclusion rules, and data snapshots. It is designed to satisfy the "Note on Sources and Reproducibility" pointer that appears in the Note immediately before the footnotes.

Every claim in the Note's main text relies only on cited Westlaw, Federal Register, OMB, Census/ACS, HUD, GAO, and OIG records. The audit files referenced below are pointers into those public sources — each file identifies the query, run date, inclusion rule, and output that let an independent reader replicate the Note's quantitative and qualitative claims without access to any private data.

**File-to-footnote crosswalk.** Fourteen audit files underlie the Note's footnote apparatus. All are present in this repository:

| Audit file | Note footnote(s) | Section(s) |
|---|---|---|
| `results/westlaw_part121_doj_audits_2026-04-18.md` | `intro-dormancy`, `I-C-part121`, `I-C-doj-zero`, `I-C-other7` | Introduction; Part I.C |
| `results/westlaw_3614a_audit_2026-04-18.md` | `I-C-3614a` | Part I.C |
| `oira_harvest/cfr_part121_analysis.md` | `I-B-121.2` | Part I.B |
| `results/verification_hud27061_2022_supporting_statement.md` | `I-B-2022pra` | Part I.B |
| `results/affh_t_disability_visualization_gap_audit.md` | `intro-affht`, `I-D-affht-arch` | Introduction; Part I.D |
| `results/nspire_ufas_crosswalk_analysis.md` | `intro-nspire`, `II-B-crosswalk` | Introduction; Part II.B |
| `results/pre_1991_stock_hardening.md` | `intro-504deficit`, `II-A-65pct`, `II-A-msa` | Introduction; Part II.A |
| `results/1988_fhaa_legislative_history_disability_data.md` | `I-B-preamble` | Part I.B |
| `results/qap_accessibility_update_analysis.md` | `II-A-qap` | Part II.A |
| `results/pro_se_mechanism_divergence_analysis.md` | `intro-mech`, `II-C-mech` | Introduction; Part II.C |
| `results/analysis_of_impediments_disability_audit.md` | `II-D-afh` | Part II.D |
| `results/hud_annual_report_longitudinal_audit.md` | `III-A-fy23`, `III-B-longitudinal` | Part III.A; Part III.B |
| `results/disclosure_effect_meta_analysis.md` | `III-B-hmda-pipeline` | Part III.B |
| `results/australia_sda_analysis.md` | `III-E-sda`, `I-E-sda` | Part I.E; Part III.E |

---

## M.2 Westlaw Citation-Count Audits

### M.2.1 24 C.F.R. Part 121 / DOJ § 3604(f)(3) joint audit

**File:** `results/westlaw_part121_doj_audits_2026-04-18.md`

**Run date:** April 18, 2026.

**Scope (two paired queries):**

1. *8-PDF Part 121 set.* Westlaw advanced query `adv: 24 CFR s 121 And (disab OR handicap OR fair housing)`. Complete reported population of federal opinions citing 24 C.F.R. Part 121 in any fair-housing or disability context.
2. *39-PDF DOJ set.* Westlaw advanced query `adv: TI(United States OR US) And (3604(f)(3) OR s 3604(f))`. Complete reported population of decisions in which the United States was a captioned party in an FHA § 3604(f)(3) matter.

**Inclusion rule.** All reported Westlaw decisions on each query with at least one substantive opinion text. Unpublished dispositions without opinion text are excluded. Subsequent history (aff'd, rev'd) is reported on the primary decision.

**Coding.** Each opinion is coded for (i) whether "24 C.F.R. Part 121" (or "Part 121") appears substantively, in a footnote, or not at all; (ii) whether 42 U.S.C. § 3614a is cited; (iii) whether the United States litigated a § 3604(f)(3) claim; (iv) the disposition of any Part 121 / § 3614a argument.

**Headline findings supporting v100 footnotes:**

- Across the 47-opinion combined population (1978–2025), "24 C.F.R. Part 121" appears substantively in exactly one opinion — *ADAPT v. HUD*, 1998 WL 113802, at *6 n.20 (E.D. Pa. Mar. 12, 1998), where it is dismissed as "meritless." (Note footnotes `intro-dormancy`, `I-C-part121`, `I-C-other7`.)
- 42 U.S.C. § 3614a is cited exactly twice — *Noble Homes*, 173 F. Supp. 3d 568, 572 (N.D. Ohio 2016); *Scott*, 788 F. Supp. 1555, 1559 n.6 (D. Kan. 1992) — each time in a non-enforcement posture. (Note footnote `I-C-doj-zero`.)
- The remaining seven Part 121 decisions cite the regulation only as the applicable race-and-ethnicity reporting rule; none engages § 121.2's enumeration of handicap or family characteristics. (Note footnote `I-C-other7`.)

### M.2.2 42 U.S.C. § 3614a audit

**File:** `results/westlaw_3614a_audit_2026-04-18.md`

**Run date:** April 18, 2026.

**Scope.** Westlaw advanced query `adv:3614a`. Complete reported population of 42 federal opinions citing 42 U.S.C. § 3614a.

**Inclusion rule.** All reported Westlaw decisions returning the `3614a` citation string. Statutory-list recitations and deferential-framework boilerplate are retained but separately coded.

**Coding.** Each opinion is classified into one of four categories: BOILERPLATE (35 of 42) — § 3614a recited in a list of statutory grants with no substantive engagement; SUBSTANTIVE (2–3 of 42) — § 3614a invoked in reasoning about HUD's rulemaking authority; PARENTHETICAL (1 of 42 — *Snyder*) — § 3614a appears in a quoted statutory-text parenthetical; BACKGROUND (remainder) — non-substantive reference. Zero opinions in the 42-case set cross-cite Part 121 as the instrument implementing § 3614a.

**Headline finding supporting note footnote `I-C-3614a`.** The operative-regulation citation pattern predicted by enforcement-live statutes (one-to-several substantive invocations per year; cross-citation to implementing regulations) is absent. The absence is consistent with operational dormancy, paired with the DOJ zero-invocation sweep in M.2.1. (v100 Part II.D no longer claims a specific 5:1–100:1 citation-ratio benchmark; the pattern is offered descriptively.)

---

## M.3 24 C.F.R. Part 121 Text-and-History Verification

**File:** `oira_harvest/cfr_part121_analysis.md`

**Sources combined.**

- eCFR snapshots of 24 C.F.R. Part 121 at three reference points: 2017 edition, September 27, 2022, and the current edition (April 2026).
- Federal Register publication history for Part 121: 54 Fed. Reg. 3,278, 3,317 (Jan. 23, 1989), and subsequent non-substantive codification entries.
- reginfo.gov ICR history for HUD information collections cross-referencing 24 C.F.R. Part 121.
- Westlaw `adv: 24 CFR s 121` universe for text-level verification.

**Verification findings supporting note footnote `I-B-121.2`.**

- Part 121 contains only § 121.1 (purpose) and § 121.2 (operative furnishing provision).
- § 121.2 enumerates "race, color, religion, sex, national origin, age, handicap, and family characteristics" as the categories program participants "shall furnish . . . such data . . . as the Secretary may determine to be necessary or appropriate."
- The 2017, 2022, and current eCFR snapshots are textually identical. Part 121 has not been materially amended since the 1989 Final Rule.
- § 121.2 is the only HUD rule that enumerates both handicap and family characteristics in a single data-collection command.

**Interpretive note honored by v100.** The "necessary or appropriate" qualifier attaches to the Secretary's discretion over collection design and weighs against a § 706(1) compulsion remedy. The regulatory enumeration supplies the predicate for § 706(2)(A) review of the 2023 reversion. v100 Part V.C reflects this reading and does not treat § 3608(e)(6) as textually free of the qualifier.

---

## M.4 2022–2023 HUD-27061 PRA Cycle Record

**File:** `results/verification_hud27061_2022_supporting_statement.md`

**Sources.**

- 87 Fed. Reg. 58,524 (Sept. 27, 2022) — 60-Day Notice announcing intent to update Form HUD-27061 to "collect protected class data as required by the Fair Housing Act and HUD regulations at 24 CFR 121" and inviting comment on "particular data fields."
- 87 Fed. Reg. 71,432 (Nov. 22, 2022) — 30-Day Notice.
- 88 Fed. Reg. 32,089 (May 18, 2023) — Final Notice reverting to the narrower instrument.
- reginfo.gov ICR 2535-0113 supporting statements, public comments, and PRA approval history for the 2022–2023 cycle.
- Public comments from AAPD, SAGE, Williams Institute, and others.

**Verification findings.**

- The 8,625-hour annual PRA respondent-burden estimate is identical in the 2022 proposal and the 2023 reversion. Neither notice identifies increased PRA respondent burden as the reason for narrowing the instrument. (This is the empirical spine of the Note's State Farm argument in Part V.A. v100 has removed all "zero marginal burden" framing in favor of this narrower record claim.)
- The 2022 60-Day Notice expressly invokes "24 CFR 121" and expressly invites comment on "particular data fields." The 2023 Final Notice provides no paragraph-level explanation of why the disability and family-characteristics fields were not included in the final instrument.

---

## M.5 AFFH-T Disability-Visualization Gap

**File:** `results/affh_t_disability_visualization_gap_audit.md`

**Sources.**

- U.S. Dep't of Hous. & Urban Dev., *AFFH Data and Mapping Tool User Guide*, v4.0 (July 2017).
- U.S. Dep't of Hous. & Urban Dev., *AFFHT0007 Data Documentation* (Aug. 2024).
- HUD AFFH-T endpoint `egis.hud.gov/affht/` (status check performed during audit).

**Coding rule.** Each map and each table in the AFFH-T is coded as (i) race-bearing, (ii) disability-bearing, or (iii) general/geographic. Opportunity-indicator cross-tabulations are coded on whether a disability-axis analog exists.

**Findings supporting note footnotes `intro-affht` and `I-D-affht-arch`.**

- Race-bearing map layers: 22. Disability-bearing map layers: 5. Ratio 5:1–7.3:1 depending on whether general population layers are counted as race-bearing.
- Maps 1–13 and 16–17 are race-or-general. Maps 14–15 are disability-standalone. There is no Map-14/15 disability cross-axis analog of the Maps 1–13 race cross-tabulations.
- Tables 1–12 use race cross-tabulation axes. Tables 13–15 are disability-standalone. There is no "Opportunity Indicators by Disability" analog to Table 12 "Opportunity Indicators by Race/Ethnicity."
- Tool endpoint returned HTTP 503 at audit date — consistent with the Note's point that the architectural gap persists beyond access windows.

---

## M.6 NSPIRE / UFAS § 504 Crosswalk

**File:** `results/nspire_ufas_crosswalk_analysis.md`

**Sources.**

- HUD, *NSPIRE Final Standards* (Apr. 2023).
- 24 C.F.R. Part 8 (§ 504 regulations) and Uniform Federal Accessibility Standards (UFAS).
- HUD REAC inspection score datasets (public housing and multifamily; see Appendix L.3).

**Coding rule.** 17 consolidated UFAS / § 504 accessibility-requirement categories are cross-walked against the NSPIRE inspection manual. Each category is scored FULL (NSPIRE inspects the category), PARTIAL (NSPIRE inspects a component, not the full standard), or NONE (NSPIRE does not inspect).

**Findings supporting note footnotes `intro-nspire` and `II-B-crosswalk`.**

| Category | Score | Count |
|---|---|---|
| FULL | 0 | 0 / 17 (0%) |
| PARTIAL | 4 | 4 / 17 (23.5%) — accessible routes / ramps, elevators, grab-bar secureness, alarms |
| NONE | 13 | 13 / 17 (76.5%) |

**Caveat.** The crosswalk measures inspection-protocol coverage only. Some on-site inspectors may observe uncoded accessibility conditions during visits; the published schema does not record such observations. See Appendix L.3 verification that no accessibility field exists in the published REAC/NSPIRE score dataset schema.

---

## M.7 Part 8 Stock-Level Verification Gap and Pre-1991 Stock Hardening

**File:** `results/pre_1991_stock_hardening.md`

**Sources.**

- 2023 American Community Survey 5-Year, Table B25034 (year-built) and Table B01003 (total population), joined by MSA GEOID.
- U.S. Dep't of Hous. & Urban Dev., *A Picture of Subsidized Households: 2024* (POSH; snapshot Dec. 31, 2024).
- Luke Bo'sher et al., *Accessibility of America's Housing Stock: Analysis of the 2011 American Housing Survey*, U.S. Dep't of Hous. & Urban Dev., Off. of Pol'y Dev. & Rsch. (2015).
- U.S. Gov't Accountability Office, *Housing Assistance: HUD Should Improve Data Collection on Accessibility of Rental Housing for People with Disabilities*, GAO-23-105083 (Apr. 2023).

**Derivation of the illustrative verification gap.** Project-based federally assisted pool of 2,346,974 units (Public Housing + PBS8 + Sections 202/811) is drawn from POSH 2024Q4. § 8.22(b) 5% new-construction floor applied to that pool yields 117,349 units. A 1%–2% current-accessible range drawn from the 2015 Bo'sher study applied to the same pool yields 23,470–46,940 units. The difference — 70,000 to 94,000 units — is reported in v100 not as a violation count but as an **illustrative verification gap**: the order-of-magnitude range that remains unresolved because HUD does not publish a Part 8-specific accessible-unit count. The GAO-23-105083 PHA self-reported medians (6% fully accessible in Public Housing; 9% in PBRA) are reproduced for comparison but flagged as unverified.

**Derivation of the 65.1% pre-1991 stock share supporting note footnote `II-A-65pct`.** 2023 ACS 5-Year Table B25034 is re-weighted within the 1990–1999 decade bin using coefficient 437/3,652 = 0.1197 to isolate the pre-March-1991 portion. Applied across all year-built bins, the within-decade-adjusted pre-March-1991 share is 65.1% of the national housing stock.

**Top-50 MSA statistics supporting note footnote `II-A-msa`.** 2023 ACS 5-Year Tables B25034 and B01003 joined on MSA GEOID yield top-50 MSA unit-weighted pre-March-1991 share of 65.8%; mean 61.5%; median 61.0%. Representative shares: 84.7% Buffalo–Cheektowaga; 83.0% Providence–Warwick; 82.4% New York–Newark–Jersey City; 81.3% Los Angeles–Long Beach–Anaheim; 78.4% Boston–Cambridge–Newton.

**v100 conventions honored.** Part III.A renames this figure the "stock-level verification gap" and explicitly flags it as illustrative, not a compliance-violation estimate. The Note's core diagnostic is that HUD does not publish a Part 8-specific accessible-unit count; the quantity range is secondary.

---

## M.8 1988 FHAA Legislative-History Disability-Data Preamble

**File:** `results/1988_fhaa_legislative_history_disability_data.md`

**Sources.**

- 54 Fed. Reg. 3,278, 3,278–79 (Jan. 23, 1989) (preamble).
- H.R. Rep. No. 100-711 (1988).
- Relevant committee-report passages discussing disability-data integration into HUD's administrative collections under the 1988 Fair Housing Amendments.

**Content.** Collects and verifies the preamble passages that commit HUD to disability-data collection as an implementation component of the 1988 Amendments, with cross-references to the committee report.

**Use in note footnote `I-B-preamble`.** Supports the Note's claim that the 1989 codification of handicap and family characteristics in § 121.2 was not a drafting accident: the operative preamble language frames the enumeration as an implementation response to the 1988 Amendments.

---

## M.9 LIHTC QAP Accessibility — 51-Jurisdiction Audit

**File:** `results/qap_accessibility_update_analysis.md`

**Sources.** Qualified Allocation Plans (QAPs) for the 2025–2026 LIHTC cycle for all 51 jurisdictions (50 states + D.C.).

**Coding rule.** Each QAP is classified into one of four categories with respect to § 504 / disability accessibility:

- **Exceeds 504** — QAP imposes accessibility requirements beyond 504 (e.g., 20% Type-A / accessible-unit set-aside).
- **Requires 504** — QAP references § 504 / Part 8 as a condition precedent without exceeding it.
- **Incentives only** — QAP offers scoring incentives for accessibility but does not require it.
- **None** — QAP does not reference § 504 / accessibility at all.

**Findings supporting note footnote `II-A-qap`.**

- Exceeds 504: 2 (Oregon, Pennsylvania; both 20% Type-A / accessible).
- Requires 504: 26.
- Incentives only: 7.
- None: 13.

48 non-error records are classified above; 7 jurisdictions are flagged for manual review. The resulting pattern — only two of 51 jurisdictions exceeding § 504 — supports the Note's feeder-program insight that stock-level accessibility is largely a floor-compliance regime at the LIHTC level.

---

## M.10 Pro Se Mechanism Divergence — 676-Case Pleading Universe

**File:** `results/pro_se_mechanism_divergence_analysis.md`

**Sources.**

- FHA Unified Database (n=2,522; 1,770 disability; see Appendix A). 1,330-case disability-wave tranche fully classified.
- 676-case pleading-loss universe, constructed as 535 disability-wave cases plus 141 pre-wave cases, all with MTD or Rule 12(c) pleading-stage dispositions.

**Coding rule.** Each MTD/12(c) loss is assigned to one of nine mechanism families, coded by Haiku 4.5 over the extracted `reasoning` text. Mechanism families include TRANSLATION (plaintiff failed to identify the operative legal theory), PROCEDURAL_GATEWAY (exhaustion, standing, ripeness), and seven others. Cases may appear in multiple families; the primary family is used for the contingency table.

**Findings supporting note footnotes `intro-mech` and `II-C-mech`.**

- TRANSLATION-family share: 48.3% pro se vs. 17.9% represented.
- PROCEDURAL_GATEWAY-family share: 18.2% pro se vs. 37.2% represented.
- Collapsed 9-into-5 contingency: χ²(8) = 33.23; p = 5.6 × 10⁻⁵; Cramér's V = 0.22.
- Strict-failure sensitivity test: χ²(7) = 33.10; p = 2.5 × 10⁻⁵; Cramér's V = 0.23.

**v100 framing.** Part III.C presents this pattern as a narrower pleading-burden diagnostic rather than as the legal predicate for a remand remedy. The TRANSLATION concentration is explicitly not offered as the State Farm predicate; the remand rests on HUD's 2023 final ICR record.

---

## M.11 47-AFH Analysis of Impediments Disability Audit

**File:** `results/analysis_of_impediments_disability_audit.md`

**Sources.** 47 publicly available Analyses of Impediments (AIs), Assessments of Fair Housing (AFHs), and equivalent fair-housing-planning documents. Sampling is purposive (large jurisdictions + illustrative mid-size jurisdictions) and not representative of the national AFH universe.

**Coding rule.** Each AI / AFH is coded for: (i) presence of a disability section; (ii) presence of quantitative disability goals; (iii) presence of accessible-unit inventory; (iv) comparative depth of disability analysis versus race analysis.

**Findings supporting note footnote `II-D-afh`.**

| Metric | Count | Share |
|---|---|---|
| Disability section present | 45/47 | 95.7% |
| Quantitative disability goals | 13/47 | 27.7% |
| Accessible-unit inventory | 11/47 | 23.4% |
| Race analysis deeper than disability | 46/47 | 97.9% |

Representative illustrative example: Lake County, Indiana, *Assessment of Fair Housing* (Nov. 2017 final) ("Nearly seven percent of the population of the jurisdiction has an ambulatory disability, yet there is known accessible accommodation for fewer than 300 people.").

**Caveat.** Sampling is purposive, not stratified-random. The audit establishes an existence pattern, not a population-level estimate.

---

## M.12 HUD Annual Report Longitudinal Audit (FY 1989 – FY 2023)

**File:** `results/hud_annual_report_longitudinal_audit.md`

**Sources.** HUD Office of Fair Housing and Equal Opportunity (FHEO) annual reports on fair housing, FY 1989 through FY 2023. Coverage gap: FY 1992–2002 reports unrecovered.

**Coding rule.** Each recovered annual report is coded for: (i) number of disability / handicap complaint bases reported; (ii) disability share of total complaint bases; (iii) table schema (which cross-tabulations are presented).

**Findings supporting note footnotes `III-A-fy23` and `III-B-longitudinal`.**

- FY 1989: 713 handicap bases at 19% share of total bases.
- FY 2018: disability share rises to 60.4%.
- FY 2023: 5,128 disability complaint bases.
- Schema instability: no two consecutive reports use identical cross-tabulation tables; FY 1992–2002 reports are unrecovered.

**Use in Note.** Part III.A presents the disability share trajectory (19% → 60.4%) paired with the Note's argument that HUD's public reporting has not been standardized on disaggregated disability outputs. Part III.B uses the schema instability finding to support the feasibility of a stable disaggregation module.

---

## M.13 Disclosure-Effect Meta-Analysis

**File:** `results/disclosure_effect_meta_analysis.md`

**Sources.** Federal Reserve Board, *Annual Report on the Home Mortgage Disclosure Act* (annual series). Peer-reviewed disclosure-effect literature on HMDA, FCRA, and related financial-disclosure regimes.

**Content.** Reviews empirical estimates of the disclosure-effect magnitude under HMDA's "sunshine" architecture (annual lender outlier-screening referrals averaging ≈ 200 lenders). Synthesizes estimates across the disclosure-effect literature to anchor the Note's claim in Part III.B that a HUD-disability-data disclosure layer would have a non-zero deterrent effect.

**Use in note footnote `III-B-hmda-pipeline`.** The HMDA referral rate (≈200 lenders/year) is offered as an anchor, not as a quantitative prediction about what a HUD-disability-data disclosure layer would yield. Part IV explicitly disclaims that the HMDA analog is a cost or effect forecast.

---

## M.14 Australia SDA Comparative Note

**File:** `results/australia_sda_analysis.md`

**Source.** National Disability Insurance Agency, *Annual Report 2022–23* (Australia Specialist Disability Accommodation program).

**Content.** Summarizes the Australian SDA administrative architecture: nationally standardized accommodation-tier definitions, property-level registration, and participant-payment linkage. Reports aggregate registration counts, participant counts, and provider counts.

**Use in note footnotes `I-E-sda` and `III-E-sda`.** Part I.E uses SDA as a reference point for what a standardized, unit-level disability-housing registry looks like in a federal-state system. Part III.E uses SDA figures as an external anchor in Part IV's proposal sketch. The Note does not recommend cloning SDA; the comparative use is bounded.

---

## M.15 Reproducibility Convention

- **Snapshot discipline.** v100 reports the Westlaw audit run dates (April 18, 2026) and the ACS / POSH / NSPIRE snapshot dates directly in the footnotes. Where a number is computed from a rolling source (e.g., reginfo.gov), the Note reports the retrieval date.
- **No private data.** No claim in the Note's main text depends on any source outside the Westlaw, Federal Register, OMB / reginfo.gov, Census / ACS, HUD, GAO, and OIG records that the audit memoranda above identify.
- **Disputed numbers.** REPRODUCE.md § "Known numerical gaps flagged by reproduction run" documents three small drifts between the Note's reported numbers and the current snapshot. Those gaps are unrelated to the doctrinal audit materials in this Appendix; they pertain to the FHA Unified Database and are addressed in Appendix A and REPRODUCE.md.
- **Update path.** If any audit memorandum in this Appendix is revised, the revision should be reflected in (i) the Note's footnote carrying the file pointer, and (ii) this Appendix's corresponding section. The file-to-footnote crosswalk in M.1 is the canonical index.
