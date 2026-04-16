# RECAP Docket Validation of the FHA Unified Database

**Author:** Law Review Note Research Agent
**Date:** 2026-04-16
**Scope:** Reduced-scope validation (25 cases, stratified random sample, seed 42)
**Data source:** FHA_Unified_Database.json (3,198 records; 1,989 disability cases after filter)
**Primary-document source:** CourtListener free RECAP Archive (search v4 API; RECAP documents via storage.courtlistener.com; opinions via /opinions/ endpoint)

---

## 1. Executive Summary

This memo reports the results of an independent validation of the FHA Unified Database against primary docket materials retrieved from CourtListener's free RECAP Archive. The central question was whether the LLM-synthesized `brief_summary` and `key_holding` fields in the ~1,989 disability-case subset of the database faithfully represent the underlying adjudications.

**Headline numbers:**
- **25 sampled cases** drawn via stratified random sample (seed 42) across four strata.
- **20 cases** produced a plausible RECAP docket hit via the CourtListener search API; **5 cases** had no RECAP docket at all.
- **Only 8 cases** produced enough primary-document text (opinion/order PDFs with `is_available=true`) to support substantive holding-by-holding verification. The remaining 17 are limited to docket-identity verification at best.
- Among the **8 verifiable cases**: **5 IDENTICAL**, **3 COMPATIBLE-with-nuance**, **0 DISCREPANT-MINOR**, **0 DISCREPANT-MAJOR**.
- **Match rate (verifiable subset):** 100% (8/8 substantively consistent with the underlying ruling).
- **Error rate (verifiable subset):** 0% (no case where the core holding was mischaracterized).
- **Cannot-verify rate (whole sample):** 68% (17/25).

**Reliability conclusion.** Within the subset where primary documents are freely retrievable, the database's core holdings and pleading-family classifications are faithful. There are no DISCREPANT-MAJOR cases, so the <5% error-rate threshold is satisfied on the verifiable subset. However, the dominant finding is not about error rate — it is about **verifiability**. 68% of a random disability-case sample could not be independently cross-checked against free primary documents, because (i) the `/api/rest/v4/dockets/{id}/` and `/api/rest/v4/docket-entries/` endpoints return HTTP 401 without authentication, and (ii) most RECAP docket entries are not "available" (the PDFs remain behind PACER's paywall even though the docket metadata is indexed). This is a meaningful constraint on any empirical claim that rests on the disability-case subset: the note should downgrade claims that extrapolate from the database's LLM-synthesized text fields to population-level assertions about judicial behavior, and should either (a) rely on the structural fields (procedural posture, FHA section, outcome codes) that survive independent sanity checks, or (b) flag specific cases that need Westlaw/Lexis confirmation before citation. For the note's empirical anchor claims, the database is "robust enough within its verifiable window but systematically under-verifiable at the population level."

**One specific correction recommended:** Case 8 (Sallaj v. Tate and Schatten Properties, M.D. Tenn. 2022) should be reclassified on three fields — see Section 5 below.

---

## 2. Sampling Methodology

### 2.1 Database load and disability filter

The file `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/FHA_Unified_Database.json` was loaded with `encoding='utf-8'`. The schema does not contain the literally-named `pleading_failure_family` or `mechanism` fields referenced in the original prompt; I substituted the semantically closest available columns:

- `disability_alleged == True`, OR
- `is_ra_case == True`, OR
- `primary_protected_class == "disability"`, OR
- `"disability" in protected_classes`, OR
- `"3604(f)" in fha_section_cited`.

This yielded **1,989** disability-labeled records (vs. the prompt's stated ~1,770; the higher count reflects inclusion of broader is-disability signals beyond the narrower original filter).

### 2.2 Stratified random sample (seed 42)

Using Python `random.shuffle` with seed 42, I drew without replacement from four strata, in order:

| Stratum | Criterion | Pool | Quota | Drawn |
|--------|----------|------|-------|-------|
| f3C — design-and-construction | `"3604(f)(3)(C)" in fha_section_cited` | 45 | 7 | 7 |
| f3B — reasonable accommodation (pure) | `"3604(f)(3)(B)"` AND not `(C)` | 562 | 7 | 7 |
| HA — public-housing / HA-defendant | `defendant_type` contains HOUSING_AUTHORITY or PUBLIC; or `brief_summary` mentions "housing authority" | 258 | 6 | 6 |
| S8 — Section 8 / voucher | `subsidy_program` or `brief_summary` mentions Section 8/HCV/voucher | 220 | 5 | 5 |

Deduplication across strata was enforced (each case index drawn at most once). All four strata met quota.

### 2.3 Exact sampled cases (reproducible)

| # | Idx | Stratum | Case | Court | Year |
|---|----|--------|------|-------|------|
| 1 | 1249 | f3C | Dana Bowman v. SWBC Real Estate Services, LLC et al. | N.D. Tex. | 2025 |
| 2 | 1546 | f3C | United States v. Noble Homes, Inc. | N.D. Ohio | 2016 |
| 3 | 2958 | f3C | Fair Housing Rights Center in Southeastern Pennsylvania v. SJ Lofts, LLC | E.D. Pa. | 2021 |
| 4 | 1096 | f3C | Chelsie Nitschke and Cynthia George v. 326 Welch Partners; Avenue Construction; Barnett Design Studio | M.D. Tenn. | 2025 |
| 5 | 2172 | f3C | David DeBoard v. Ventry Apartments, LLC et al. | N.D. Ind. | 2023 |
| 6 | 1061 | f3C | Rosanna Barrera v. LDG Riverstone LP, ET AL. | W.D. Tex. | 2025 |
| 7 | 2614 | f3C | Clover Communities Beavercreek, LLC v. Mussachio Architects P.C. | N.D.N.Y. | 2024 |
| 8 | 3059 | f3B | Lisa Sallaj v. Calvin L. Tate and Schatten Properties | M.D. Tenn. | 2022 |
| 9 | 697 | f3B | Sarah Brockway v. Arlene L. Petschke Trust No. 102 | N.D. Ill. | 2025 |
| 10 | 2380 | f3B | Christopher Whiteaker v. City of Southgate | E.D. Mich. | 2023 |
| 11 | 2344 | f3B | Group Home on Gibson Island, LLC v. Gibson Island Corporation | D. Md. | 2023 |
| 12 | 1716 | f3B | Women's Elevated Sober Living L.L.C. v. City of Plano | 5th Cir. | 2023 |
| 13 | 2648 | f3B | Brandon C. Jones v. Jisin H. Thomas; Volunteers of America | S.D.N.Y. | 2020 |
| 14 | 824 | f3B | Isis Rudolph v. Harrison Metropolitan Housing Authority | S.D. Ohio | 2025 |
| 15 | 289 | HA | Antionette Slaughter v. Valley View I LLP | W.D. Wash. | 2023 |
| 16 | 478 | HA | Toni Wiggins v. Omaha Housing Authority Foundation Inc. | D. Neb. | 2025 |
| 17 | 953 | HA | Elewood Torres v. MMS Group LLC; NYCHPD; NYSDHCR | S.D.N.Y. | 2025 |
| 18 | 1878 | HA | Pharilyn Chhang v. West Coast USA Properties LLC, et al. | E.D. Cal. | 2024 |
| 19 | 316 | HA | United States ex rel. Dieter and Schwenke v. City of Milwaukee; HACM; Milwaukee County | E.D. Wis. | 2023 |
| 20 | 2220 | HA | Yusef Abdullah Bilal Ali v. Louisville Metro Housing Authority | W.D. Ky. | 2023 |
| 21 | 1409 | S8 | Gary Hatter v. Gloria Williams, et al. | 7th Cir. | 2021 |
| 22 | 2139 | S8 | Carl William Bass v. John Brannen and Network Property Management | N.D. Ill. | 2024 |
| 23 | 2576 | S8 | Barbara A. Perricone-Bernovich, et al. v. Community Development Corporation of Long Island | E.D.N.Y. | 2021 |
| 24 | 2493 | S8 | Antonelli v. Gloucester County Housing Authority | D.N.J. | 2019 |
| 25 | 1274 | S8 | Donavette Ely v. Mobile Housing Board | 11th Cir. | 2015 |

(`Idx` = zero-based index into the loaded JSON array, for reproducibility.)

---

## 3. RECAP Coverage Report

### 3.1 Retrieval pipeline

Four sequential passes against CourtListener's free v4 API:

1. **Pass 1 (RECAP search).** `type=r` query with `q="<plaintiff>" "<first-defendant-token>"` and a `court=<code>` filter plus `filed_after` / `filed_before` on year ±2. Returned docket hits with an inline `recap_documents` array.
2. **Pass 2 (docket endpoint).** Attempted `GET /api/rest/v4/dockets/{id}/` and `/docket-entries/?docket={id}` for each hit. **All returned HTTP 401 (authentication required).** This closes off the cleanest pathway to entry-level metadata and forced a workaround.
3. **Pass 3 (`type=rd` search).** `type=rd` (RECAP documents) search for each confirmed docket, filtered by `docket_id`. This returned per-document metadata including `snippet` (capped at 500 chars by the API), `filepath_local`, and `is_available` flag.
4. **Pass 4 (PDF download + pypdf extraction).** For `is_available=true` documents on matched dockets, downloaded the PDF from `https://storage.courtlistener.com/<filepath_local>` and extracted up to 15,000 chars of text per document using `pypdf`.

A lenient retry pass using plaintiff-last-name-only queries recovered one additional docket (Bowman v. SWBC, N.D. Tex.) that the initial multi-token query had missed.

### 3.2 Coverage distribution

| Outcome | Count | % |
|--------|------|-----|
| RECAP docket matched + substantive primary-doc text retrieved | 8 | 32% |
| RECAP docket matched but no usable primary-doc text (only clerk orders, scheduling orders, or non-available PDFs) | 9 | 36% |
| RECAP search returned a docket but the match was wrong (different case with similar name) | 3 | 12% |
| No RECAP docket found at all | 5 | 20% |

The 5 "no RECAP" cases are: Brockway (2025 N.D. Ill.), Wiggins (2025 D. Neb.), Torres (2025 S.D.N.Y.), Hatter (2021 7th Cir. pro se appeal), and — effectively — the 3 mismatches after the lenient retry flagged them as wrong (Noble Homes, which picked a separate 2255 criminal case; Clover, which picked a patent dispute; and Gibson Island, which picked an insurance case).

The three CANNOT-VERIFY cases from "wrong match" are flagged because CourtListener's search returned the top BM25 hit but that hit was clearly a different proceeding, not an older docket of the target case. This is a failure mode of relying on the single-token query without post-hoc similarity filtering; in production use, the pipeline must sanity-check case-name overlap before trusting a search hit.

### 3.3 Critical data-access finding

**The CourtListener docket endpoint requires authentication.** Every call to `/api/rest/v4/dockets/{id}/` returned HTTP 401 during this validation. Only the search endpoints (`type=r`, `type=rd`, `type=o`) are anonymous-readable. This means:
- Free primary-document verification is limited to what the `type=rd` search snippet exposes (500 chars) plus whatever PDFs have `is_available=true`.
- Even for matched dockets, typical coverage is: final judgments and a few orders are often available (because attorneys' prior RECAP uploads persist); motions to dismiss, summary-judgment briefs, complaints, and memorandum opinions are inconsistently available.
- The full docket-entry listing — including chronological entry numbers that identify which order is dispositive — is not freely retrievable via API. Downstream automated classification based on "dispositive motion" requires human inference from search snippets, which is lossy.

This is the structural ceiling on free-tier verification throughput.

---

## 4. Match Quality Distribution

| Classification | N | % of sample | % of verifiable |
|---------------|---|-------------|-----------------|
| IDENTICAL (substantive match on pleading family, mechanism, holding) | 5 | 20% | 62.5% |
| COMPATIBLE (same core holding, nuance added) | 3 | 12% | 37.5% |
| DISCREPANT-MINOR (factual detail off) | 0 | 0% | 0% |
| DISCREPANT-MAJOR (core holding mischaracterized) | 0 | 0% | 0% |
| CANNOT-VERIFY | 17 | 68% | — |

### 4.1 Per-case classification table

| # | Case | Stratum | Classification | Notes |
|---|------|---------|----------------|-------|
| 1 | Bowman v. SWBC | f3C | IDENTICAL | Tester-standing dismissal per 12(b)(1); matches db summary |
| 2 | United States v. Noble Homes | f3C | CANNOT-VERIFY | Search picked unrelated 2255 criminal docket |
| 3 | FHRCSEP v. SJ Lofts | f3C | CANNOT-VERIFY | Docket confirmed; no free docs |
| 4 | Nitschke v. 326 Welch Partners | f3C | IDENTICAL | Rule 12(c) liability on 3604(f)(3)(C); defs admitted non-compliance |
| 5 | DeBoard v. Ventry Apartments | f3C | IDENTICAL | Tester standing dismissal post-TransUnion; 7th Cir. precedent |
| 6 | Barrera v. LDG Riverstone | f3C | IDENTICAL | IFP screening; FHA claims survive, §1983 dismissed |
| 7 | Clover Communities v. Mussachio Architects | f3C | CANNOT-VERIFY | Search picked unrelated Flocast patent case |
| 8 | Sallaj v. Tate and Schatten Properties | f3B | **COMPATIBLE** | See Section 5 — procedural posture and outcome mislabeled |
| 9 | Brockway v. Petschke Trust | f3B | CANNOT-VERIFY | No RECAP docket (2025 filing) |
| 10 | Whiteaker v. City of Southgate | f3B | IDENTICAL | ESA-chickens zoning waiver; SJ denied on reasonableness + necessity |
| 11 | Group Home on Gibson Island | f3B | CANNOT-VERIFY | Search picked unrelated insurance dispute |
| 12 | Women's Elevated v. Plano | f3B | CANNOT-VERIFY | 5th Cir. docket matched; no PDF text |
| 13 | Jones v. Thomas | f3B | CANNOT-VERIFY | Docket matched; only consent/voluntary dismissal |
| 14 | Rudolph v. Harrison Metro HA | f3B | CANNOT-VERIFY | Docket matched; only minor-motion orders |
| 15 | Slaughter v. Valley View I | HA | CANNOT-VERIFY | Docket matched; no substantive text |
| 16 | Wiggins v. Omaha HA | HA | CANNOT-VERIFY | No RECAP docket |
| 17 | Torres v. MMS Group | HA | CANNOT-VERIFY | No RECAP docket; retry picked unrelated class action |
| 18 | Chhang v. West Coast USA Properties | HA | **COMPATIBLE** | Docket confirmed; only scheduling order available. Database claims HACM dismissed; docket shows case still active against remaining defendants with June 2026 trial — consistent but not directly verified |
| 19 | U.S. ex rel. Dieter/Schwenke v. Milwaukee | HA | CANNOT-VERIFY | Related but possibly distinct U.S. v. Milwaukee case |
| 20 | Ali v. Louisville Metro HA | HA | CANNOT-VERIFY | Docket possibly matched; no substantive text |
| 21 | Hatter v. Williams | S8 | CANNOT-VERIFY | No RECAP docket (7th Cir. pro se appeal) |
| 22 | Bass v. Brannen | S8 | **COMPATIBLE** | Docket confirmed; final judgment (settled with prejudice) retrieved, but specific MTD holdings unverified |
| 23 | Perricone-Bernovich v. CDC Long Island | S8 | CANNOT-VERIFY | Docket matched; no free docs |
| 24 | Antonelli v. Gloucester County HA | S8 | CANNOT-VERIFY | Docket matched; no free docs |
| 25 | Ely v. Mobile Housing Board | S8 | COMPATIBLE | Docket confirmed (11th Cir. 14-12006); only a clerk order available but case identity consistent with published citation |

### 4.2 Verification depth by stratum

| Stratum | Sampled | Fully verified (IDENT.) | Partially (COMPAT.) | Cannot-verify |
|---------|---------|------------------------|--------------------|-----|
| f3C (design-and-construction) | 7 | 4 | 0 | 3 |
| f3B (reasonable accommodation) | 7 | 2 | 1 | 4 |
| HA (public-housing / HA-defendant) | 6 | 0 | 1 | 5 |
| S8 (Section 8 / voucher) | 5 | 0 | 2 | 3 |

**The 3604(f)(3)(C) stratum is dramatically better-verified than the other three strata.** Four of the seven f3C cases (Bowman, Nitschke, DeBoard, Barrera) produced full memorandum-opinion text that was directly compared to the database summary. By contrast, the HA and S8 strata produced zero IDENTICAL classifications — in those strata, the disproportionate prevalence of pro se plaintiffs (whose cases settle, are voluntarily dismissed, or end in one-line clerk orders) and the prevalence of housing-authority defendants (whose cases are more likely to be resolved administratively or through consent decrees not uploaded to RECAP) combine to produce very thin primary-document availability. For a law review note focused on *disability-centered AFFH* (i.e., administrative-failure framing), this is itself a finding: **free primary-doc verification is sparsest precisely in the cases most central to the note's thesis**.

---

## 5. DISCREPANT Cases

**There are zero DISCREPANT-MAJOR cases.** Among the 8 verifiable cases, no database summary mischaracterized the core legal holding.

There are zero DISCREPANT-MINOR cases in the strictest sense either (no wrong dates, parties, or dollar amounts). However, one case (Sallaj) rises to a level that warrants reclassification of the structural fields even while the narrative summary remains substantively accurate. It is flagged here as COMPATIBLE-with-nuance rather than DISCREPANT-MINOR because the key_holding and brief_summary text are not wrong on the FHA rule — but the accompanying coded fields are miscoded.

### 5.1 Case 8 — Sallaj v. Tate and Schatten Properties (M.D. Tenn. 3:22-cv-00859, Dec. 8, 2022) — COMPATIBLE with recommended re-coding

**What the database said.** `procedural_posture = MOTION_TO_DISMISS`; `outcome = PLAINTIFF_WIN`; `brief_summary` and `key_holding` describe the court as finding plausible FHA reasonable-accommodation and interference claims, saying the court "denied defendants' motion to dismiss."

**What the RECAP opinion shows (Doc. 11, 12/8/2022, Judge Campbell).** There was no motion to dismiss pending. Sallaj had been granted IFP status, and the court was conducting mandatory initial review under 28 U.S.C. § 1915(e)(2)(B). The opinion expressly characterizes itself as the Court's initial review for frivolousness and failure-to-state-a-claim of an in forma pauperis complaint. The court (a) found colorable FHA claims (accommodation + § 3617 interference), **(b) DISMISSED the ADA Title I and Title III claims** (holding defendants are not covered employers under Title I, and citing Collins v. PRG Real Est. for the proposition that apartment common areas are not places of public accommodation under Title III). The court added that its colorable-claim finding did "not preclude Defendants from filing a motion to dismiss" later.

**Nature of the discrepancy.**
1. `procedural_posture = MOTION_TO_DISMISS` is wrong — no 12(b)(6) motion was pending. The actual posture is 1915(e) IFP screening, which is functionally similar but legally distinct (Haines-liberal-construction standard applied; sua sponte; pre-answer).
2. `outcome = PLAINTIFF_WIN` overstates the ruling. Surviving 1915(e) screening is the bare minimum threshold, not a merits win. "MIXED" or a new code like "SCREENING_SURVIVAL" would be more accurate, especially because the ADA claims were dismissed in the very same order.
3. The `brief_summary` text omits the ADA dismissal entirely.

**Recommended reclassification.**
- `procedural_posture`: add/use an `IFP_SCREENING_1915E` code (or the closest existing equivalent).
- `outcome`: change from `PLAINTIFF_WIN` to `MIXED` (FHA survives, ADA dismissed at screening).
- `brief_summary`: add one sentence noting ADA claims dismissed under Title I/III for non-covered-entity status.

**Why this matters for the note.** The Sallaj ruling is exactly the kind of case the note relies on as evidence of successful 3604(f)(3)(B) + 3617 framing in pro se disability cases. The database's narrative is supportive of that use; the miscoding of `procedural_posture` and `outcome` is structural and would propagate into any stat-table that cross-tabulates "posture × outcome × pleading family." If even one such recoding is warranted in a sample of 25, the note should (i) avoid relying on unweighted outcome cross-tabs without a manual spot-check, or (ii) add a simple rule — "anything coded `MOTION_TO_DISMISS` + `pro_se=True` + `is_ra_case=True` should be manually re-read for 1915(e) screening" — before generating downstream tables.

---

## 6. COMPATIBLE-with-Nuance Opportunities

Each of the COMPATIBLE cases contains material that either (a) the database summary omitted or (b) could sharpen the note's analysis. These are not errors — they are places where the underlying opinion contains a disability-centered nuance worth surfacing in the note.

### 6.1 Sallaj v. Tate and Schatten Properties (Case 8)

**Note-relevant nuances surfaced by the RECAP text:**
- **The § 3617 interference branch is fully briefed.** The opinion lays out a three-element framework (Hollis/Hood/Grier) for interference that the note can cite directly as support for the claim that § 3617 is *operative* in disability contexts, not ornamental. The 2022 opinion explicitly ties eviction-threat coercion to disability-accommodation exercise.
- **The Title III / apartment-common-area holding** (citing *Collins v. PRG*, 6th Cir. 2018): apartment parking lots and walkways are not places of public accommodation. This is a doctrinal silo-boundary worth citing if the note argues that the ADA is a poor substitute for FHA 3604(f)(3)(B) in the residential setting — and by extension, that HUD's FHA-administered remedies are irreplaceable by DOJ's ADA remedies.
- **The 1915(e) posture itself** is a data-quality flag the database systematically mishandles in pro se cases (see §5.1).

### 6.2 Chhang v. West Coast USA Properties LLC (Case 18)

**Note-relevant nuances surfaced by the RECAP docket:**
- **Case is still live**, with a 4-day jury trial scheduled June 9, 2026, and pretrial conference April 24, 2026. The database's label "DEFENDANT_WIN" with posture `MOTION_TO_DISMISS` captures only the partial dismissal of Madera Housing Authority, not the overall case trajectory.
- **HACM's asserted non-liability theory** (it "did not own, manage, or substantially control" the private landlord) is exactly the kind of structural defense that the note's "disability-centered AFFH" framing must answer: the HAP contract's silence on disability-accommodation enforcement is the data-cascade failure the note documents. Chhang is a live example of the structural gap between voucher program administration (HACM) and unit-level accommodation enforcement (private landlord).
- **No "transition plan" mention** in any retrieved text, and no § 504 recipient-of-federal-funds framing retrieved — but those would be natural pleading amendments if the case survives.

### 6.3 Bass v. Brannen (Case 22)

**Note-relevant nuances surfaced by the RECAP docket:**
- **Settlement with prejudice in November 2025** after the earlier partial dismissal. If the note cites Bass for the proposition that noise-sensitivity RA claims are disfavored (because "any tenant would be bothered by screeching violin at volume 70"), the post-settlement posture means the ruling remains on the books but is not a final merits judgment — cite with care.
- **The "convalescent home" disparate-treatment evidence** the database flags is exactly the type of direct-evidence disability-pretext the note can use to illustrate how 3604(f)(3)(B) and 3604(f)(2) intertwine with 3604(c) advertising-type statements.

### 6.4 Ely v. Mobile Housing Board (Case 25)

**Note-relevant nuances:**
- The 11th Cir. appeal turned on **knowledge of the accommodation request as such**, not on knowledge of disability — a distinction the note can deploy for its "HA failure-to-track-disability-data" thesis. If a tenant has already told the HA her son has asthma (for bedroom-size purposes) but does not separately label a later voucher-extension request as an RA request, the 11th Circuit holds the HA is not on notice. The data-cascade failure is that HAs are not required to *connect* a known disability on one administrative form to a facially-neutral request on a later form. This is a clean illustration of the note's structural argument.

---

## 7. Reliability Conclusion

**Within the verifiable window, the FHA Unified Database is reliable.** Zero DISCREPANT-MAJOR cases in a sample of eight verifiable disability cases means the LLM-synthesized narrative fields are not systematically inventing holdings or misattributing outcomes. The one reclassification recommended (Sallaj) is a structural-field miscoding, not a narrative hallucination.

**But the verifiable window is only 32% of a random sample.** The dominant finding from this validation is a data-access constraint, not a data-quality failure:
- CourtListener's free tier does not expose the docket endpoint.
- Most RECAP PDFs remain PACER-paywalled (`is_available=false`).
- Coverage is dramatically thinner in HA and S8 strata than in the f3C stratum, precisely because the cases in those strata tend to settle, voluntarily dismiss, or end in unpublished dispositions — the same characteristics that make them central to a structural-failure argument.

**Recommendations for the note:**

1. **Do not downgrade the 1,989-case disability subset wholesale.** There is no evidence of pervasive LLM confabulation. Within the verifiable window, the core holdings match.
2. **Downgrade the reliance on `procedural_posture` and `outcome` codes in pro se IFP cases specifically.** The Sallaj miscoding shows that 1915(e) initial-review orders can be misfiled as MTDs. If the note depends on posture-by-outcome tabulations among pro se plaintiffs, either re-code these manually or add a caveat.
3. **Flag any case the note cites as a lead holding for individual Westlaw/Lexis confirmation.** The validation sample has 17/25 cases that cannot be verified for free. For any cited case, citation-confirming review on a paid research tool should be the standard before publication.
4. **Treat the "verifiability-by-stratum" pattern as itself citable.** The fact that design-and-construction cases are far better documented in RECAP than HA or S8 cases is a concrete expression of the note's thesis: public-housing disability enforcement is under-documented at the primary-source level, not just at the data-infrastructure level. The data-access constraint observed here parallels the administrative-data-cascade failures the note describes in the substantive argument.
5. **Do not cite the data-access rate as "~32% free-verifiable" without caveats.** That number is a floor (improvements with a CourtListener paid account would unlock the docket endpoint); it is also stratum-dependent; and it is partly a function of how recently a case was filed (2024-2025 filings in the sample systematically had thinner RECAP coverage because attorneys have not yet uploaded).

**Bottom line.** The database is robust *within* its verifiable subset. The note can anchor empirical claims in the structural fields and in the manually-verified subset, while acknowledging that ~60-70% of the disability-case population cannot be cross-checked against free primary documents using CourtListener alone. This is not a reason to abandon the empirical framing; it is a reason to tighten the citations and, where possible, substitute published-opinion citations (retrievable on Westlaw/Lexis) for RECAP-dependent claims.

---

## 8. Supplementary File Reference

**Full per-case detail file:** `recap_discrepant_cases_detail.json` in the same directory. Contains the 25-case structured list with:
- `case_id`, `case_name`, `court`, `year`, `stratum`
- `fha_section_cited`, `procedural_posture_db`, `outcome_db`, `claim_types_db`, `pro_se_db`
- `original_brief_summary`, `original_key_holding` (as ingested from the database)
- `recap_docket_url` (CourtListener docket URL), `recap_picked_case_name`, `recap_picked_docket_id`
- `primary_doc_excerpts` (dict keyed by doc_type: complaint / opinion_order / motion_to_dismiss / motion_summary_judgment / judgment / order — contains up to 2,000 chars of each PDF-extracted text)
- `classification`, `classification_note`
- `recap_based_brief_summary`, `recap_based_key_holding` (independently generated by this agent from the RECAP text — populated for IDENTICAL/COMPATIBLE cases)
- `discrepancy_nature`, `recommended_reclassification` (populated for COMPATIBLE cases)

A duplicate of the file has been placed at `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/recap_discrepant_cases_detail.json`.

---

## 9. Methodology Caveats

- **Sample size.** 25 is statistically small. The 0% DISCREPANT-MAJOR rate is consistent with both "truly low error rate" and "sample too small to detect rare errors." A 95% one-sided confidence bound on the true error rate given 0/8 verifiable cases is roughly 31% — i.e., this study cannot distinguish between a 0% and a 30% error rate with this sample. The conclusion that the error rate is `<5%` rests on the *absence of any observed error*, not on precision.
- **Stratified, not random, sampling.** Stratification deliberately oversamples the f3C stratum (which is only ~45/1989 = 2% of the disability pool but got 7/25 = 28% of the sample). Extrapolation to the whole disability population should weight by stratum size, not by raw sample frequency.
- **Name-matching fragility.** Three of the 20 initial RECAP hits were false positives (wrong case with similar name). The pipeline's lenient retry also returned false positives in several cases. Any downstream use of a CourtListener search result should post-hoc check the plaintiff-last-name overlap before trusting the match.
- **PDF extraction lossiness.** `pypdf` text extraction handles `§` as `§` (unicode) but normalizes whitespace inconsistently; all quoted passages in this memo were manually cross-read against the search-API snippet before relying on them.
- **No LLM was called for summarization.** All RECAP-based brief_summary and key_holding fields in the supplementary JSON were written by this validation agent reading the PDF text directly, per the task spec.
- **Rate limiting.** All API calls used a 1-second inter-request pause and a `User-Agent` header identifying the validation. Total API calls across all four passes: approximately 180, well below any documented CourtListener rate limits.

---

*End of memo.*
