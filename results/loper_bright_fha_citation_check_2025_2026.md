# Loper Bright / FHA citation check (Jan. 2025-Apr. 2026)

Search run: 2026-04-16T02:51:55-07:00

Question: whether any federal court opinion filed from 2025-01-01 through the search date (2026-04-16) cites *Loper Bright Enters. v. Raimondo* in connection with a Fair Housing Act claim or defense, and specifically whether PCI v. Todman changes that answer.

## Bottom line

The earlier conclusion needs correction after reconciling the public-search memo against the local structured case databases.

The accurate bottom line is now:

Terminology note: because the repo's `merits_reached` field is claim-level and treats pleading-stage rulings separately, I use `substantive opinion` below for opinion-level discussion; *Watts* and *Twyman* are pleading-stage FHA opinions in that framework, not `merits_reached = YES` entries.

- For federal FHA substantive opinions generally, there are at least two verified in-window opinions citing *Loper Bright*: *Sara Watts v. Joggers Run Property Owners Association, Inc.*, 133 F.4th 1032 (11th Cir. Apr. 7, 2025), and *Meredith Twyman v. Recap PA Holdings, LLC* (E.D. Pa. Mar. 12, 2025).
- For disability FHA reasonable-accommodation / reasonable-modification substantive opinions, there is at least one verified in-window hit: *Twyman*. It is a pleading-stage § 3604(f)(3)(B) reasonable-accommodation opinion locally coded `loper_bright_cited = YES`.
- I still found no in-window reasonable-modification substantive FHA opinion citing *Loper Bright*.
- There is also an additional in-window disability-FHA procedural opinion citing *Loper Bright*: *Heimkes v. Fairhope Motorcoach Resort Condominium Owners Association* (S.D. Ala. Sept. 10, 2025). But that opinion is a recusal/mistrial order, not a substantive resolution of the FHA accommodation claim, so it should be counted separately as a procedural hit rather than as a substantive disability-FHA opinion.
- PCI v. Todman still does not add a 2025-2026 opinion.

So the corrected conclusion is more complete than the original draft: the answer is not just that *Watts* broke the "no FHA-specific *Loper Bright* citation" proposition; local database reconciliation shows that *Twyman* also does so, and *Twyman* is the key disability reasonable-accommodation pleading-stage opinion hit in the target window.

## Exact search methodology

All searches initially used public sources only.

Important local-reconciliation note:

- After completing the public-source search below, I reconciled the memo against the local structured databases and local audit files:
  - `data/FHA_Unified_Database.json`
  - `data/FHA_RA_Database_unified_20260328_090852.json`
  - `data/FHA_3604_Database_unified_20260328_104352.json`
  - `allFHAcases/recentcases/FHA_RA_Database_audit_20260328_090852.json`
  - `allFHAcases/3604/FHA_3604_Database_audit_20260328_104352.json`
- That local pass revealed an omitted in-window pleading-stage FHA opinion hit (*Twyman*) and a separate in-window procedural hit (*Heimkes*), both coded `loper_bright_cited = YES` in the local structured data.
- The local audit files also support the correction: *Twyman* is coded `loper_bright_cited = YES` across the unified, RA, and 3604 datasets, and the RA audit file shows unanimous `YES` coding for `loper_bright_cited` for *Twyman* and *Heimkes*; *Heimkes* does not appear in the 3604 audit file, which is consistent with treating it as a procedural/non-substantive hit rather than as a substantive § 3604 opinion hit.
- The public-search log is preserved below because it remains useful for documenting the external search, but the bottom-line conclusion must be corrected in light of the local-database reconciliation.

### 1. CourtListener API opinion searches

Base endpoint used:

- `https://www.courtlistener.com/api/rest/v4/search/?type=o&q=...`

Method:

1. Run full-text opinion searches for `Loper Bright` plus FHA-specific and disability-FHA-specific terms.
2. Filter hits by `dateFiled` to 2025-01-01 through 2026-04-16.
3. For every in-window hit, download the public opinion PDF/HTML linked from CourtListener and text-check for actual FHA content (`Fair Housing Act`, `FHA`, `3604`, `3617`, `reasonable accommodation`, `reasonable modification`, `HUD`, `dwelling`).
4. Exclude opinions that merely mention the Fair Housing Act as standing precedent or otherwise are not themselves FHA claims/defenses.

Search log:

| Query | Total CL results | In-window hits | Notes |
|---|---:|---:|---|
| `"Loper Bright" "Fair Housing Act"` | 5 | 4 | Produced one true FHA hit (*Watts*) plus false positives in the public-search pass; local database reconciliation later added *Twyman*. |
| `"Loper Bright" "fair housing"` | 6 | 5 | Same public-search result pattern: *Watts* plus standing / non-FHA false positives; local databases later added *Twyman*. |
| `"Loper Bright" "FHA"` | 1 | 1 | Public search returned only *Watts*. |
| `"Loper Bright" "3617"` | 2 | 1 | Public search returned only *Watts* in window. |
| `"Loper Bright" "3604(f)(2)"` | 1 | 1 | Returned *Watts* because it discusses *Hunt v. Aimco* by analogy. |
| `"Loper Bright" "3604(f)(3)(B)"` | 0 | 0 | Public search returned no hits, but local structured databases later identified *Twyman* (Mar. 12, 2025) as an in-window § 3604(f)(3)(B) opinion citing *Loper Bright*. |
| `"Loper Bright" "24 C.F.R. 100.204"` | 0 | 0 | No public-search hit. |
| `"Loper Bright" "reasonable modification" housing` | 0 | 0 | No public-search hit, and local database reconciliation did not reveal an in-window reasonable-modification substantive FHA opinion citing *Loper Bright*. |
| `"Loper Bright" "reasonable accommodation" housing` | 5 | 4 | Public-search in-window hits were non-FHA cases; local databases later surfaced *Twyman* (substantive pleading-stage opinion) and *Heimkes* (procedural). |
| `"603 U.S. 369" "Fair Housing Act"` | 4 | 4 | Citation-form cross-check returned no additional public-source FHA substantive opinion beyond *Watts*; local database reconciliation later added *Twyman*. |
| `"603 U.S. 369" "3617"` | 1 | 1 | Cross-check again returned only *Watts* in the public-search pass. |

Todman-specific CourtListener checks:

- Opinion search: `"Property Casualty Insurers Association of America" "E. Scott Turner"` -> 0 opinion results.
- Opinion search: `"24-1947" "Property Casualty Insurers Association of America"` -> 0 opinion results.
- Opinion search: `"Property Casualty Insurers Association of America" Todman opinion` -> 0 opinion results.
- Docket search (`type=d`): CourtListener returned the Seventh Circuit docket for *Property Casualty Insurers Association of America v. E. Scott Turner*, No. 24-1947, showing `dateFiled = 2024-06-03`, `dateArgued = 2025-01-16`, and no termination date.

### 2. Google Scholar / web searches

Direct Google Scholar attempt:

- Query attempted: `https://scholar.google.com/scholar?q=%22Loper+Bright%22+%22Fair+Housing+Act%22`
- Result from this environment: HTTP 429 / captcha page, so no usable Scholar result set was available from the CLI session.

Because the task permitted Scholar/web, I used public web search as the fallback cross-check.

Web-search queries used:

- `"Loper Bright" "Fair Housing Act" opinion`
- `"Loper Bright" "42 U.S.C. 3604" opinion`
- `"Loper Bright" "42 U.S.C. 3617" opinion`
- `"Loper Bright" "reasonable accommodation" housing opinion`
- `site:ca11.uscourts.gov Sara Watts Joggers Run Loper Bright Fair Housing Act`
- `site:uscourts.gov "Loper Bright" "Fair Housing Act"`
- `"PCI v. Todman"`
- `"Property Casualty Insurers Association of America v. Todman" opinion 2025 2026`
- `"Property Casualty Insurers Association of America v. Adrianne Todman" Seventh Circuit status`

Web-search results summary:

- General web queries mostly returned commentary, law review articles, and practice notes, not additional federal opinions.
- `site:ca11.uscourts.gov Sara Watts Joggers Run Loper Bright Fair Housing Act` returned the official Eleventh Circuit PDF for *Watts*, confirming the FHA/*Loper Bright* overlap.
- `site:uscourts.gov "Loper Bright" "Fair Housing Act"` returned the *Watts* PDF and unrelated non-FHA government PDFs.
- `"PCI v. Todman"` identified PCI as *Property Casualty Insurers Association of America v. Todman*.
- The 2025/2026 Todman-specific web queries surfaced docket/status pages and commentary, but no 2025-2026 substantive opinion.
- The public web searches did not surface *Twyman* or *Heimkes* in a way that corrected the initial draft; those corrections came from reconciling against the local structured databases and local opinion text.

## Local structured-database reconciliation

Querying the local structured datasets for in-window rows with `loper_bright_cited = YES` produced the following practical reconciliation:

1. *Watts* appears in the unified data more than once because the local databases contain multiple records tied to the same April 7, 2025 Eleventh Circuit opinion and alternate citation records.
2. *Twyman* appears in all three relevant local structured datasets as an E.D. Pa. 2025 opinion with:
   - `procedural_posture = MOTION_TO_DISMISS`
   - `fha_section_cited = 3604(f)(3)(B)`
   - `primary_claim_type = reasonable_accommodation_denial`
   - `loper_bright_cited = YES`
3. A later *Twyman* opinion in the same litigation, filed April 28, 2025, is also in the local databases but is coded `loper_bright_cited = NO`, so it does not change the citation count.
4. *Heimkes* appears in the unified and RA datasets with:
   - `procedural_posture = OTHER_PROCEDURAL`
   - `primary_claim_type = reasonable_accommodation_denial`
   - `loper_bright_cited = YES`
   - a brief summary and key holding describing a recusal order rather than a substantive resolution.
5. No in-window local-database row with `loper_bright_cited = YES` was coded as a reasonable-modification opinion.

That means the local data support three distinct in-window *Loper Bright* / FHA opinion hits overall, but only two are substantive FHA opinion hits (*Watts* and *Twyman*), and only one is a disability reasonable-accommodation pleading-stage opinion hit (*Twyman*). *Heimkes* is best treated separately as a procedural/non-substantive hit.

## Case-level findings

### A. Verified substantive FHA opinion hits

1. *Sara Watts v. Joggers Run Property Owners Association, Inc.*, 133 F.4th 1032 (11th Cir. 2025)
   - Date filed: 2025-04-07
   - CourtListener opinion URL: `https://www.courtlistener.com/opinion/10373706/sara-watts-v-joggers-run-property-owners-association-inc/`
   - Public PDF: `https://media.ca11.uscourts.gov/opinions/pub/files/202213763.pdf`
   - Why it counts:
     - This is an actual Fair Housing Act substantive opinion.
     - The opinion addresses FHA §§ 3604(b) and 3617.
     - The court cites *Loper Bright* while explaining why HUD's contemporaneous FHA regulation remains useful in the court's independent statutory interpretation.
   - Relevant text checked in the PDF:
     - The court describes the case as presenting claims under the "Fair Housing Act (FHA)."
     - The court discusses § 3604(b), § 3617, and 24 C.F.R. § 100.65(b)(4).
     - The opinion expressly cites *Loper Bright* in that FHA interpretive discussion.
   - Result: INCLUDED.

2. *Meredith Twyman v. Recap PA Holdings, LLC* (E.D. Pa. Mar. 12, 2025)
   - Date filed: 2025-03-12
   - Local opinion source: `allFHAcases/recentcases/10377601_2025_TWYMAN v. RECAP PA HOLDINGS, LLC_paed.txt`
   - Local database support:
     - `data/FHA_Unified_Database.json` -> `loper_bright_cited = YES`
     - `data/FHA_RA_Database_unified_20260328_090852.json` -> `loper_bright_cited = YES`
     - `data/FHA_3604_Database_unified_20260328_104352.json` -> `loper_bright_cited = YES`
   - Why it counts:
     - This is an actual FHA pleading-stage opinion, not a pure procedural order.
     - The opinion addresses race and disability FHA theories, including a § 3604(f)(3)(B) reasonable-accommodation claim involving a requested handicapped parking space.
     - The opinion cites *Loper Bright* in its FHA interpretive discussion, in footnote 25: `see also Loper Bright Enters. v. Raimondo, 603 U.S. 369, 413 (2024) (courts may pay careful attention to the judgment of an agency in interpreting a statute).`
     - The same opinion later dismisses the accommodation claim for failure to plead refusal and necessity.
   - Scope note:
     - The *Loper Bright* citation appears in the opinion's broader FHA/HUD-regulation discussion rather than in the accommodation-elements subsection itself. But because the opinion substantively addresses a § 3604(f)(3)(B) reasonable-accommodation claim at the pleading stage, it is still an in-window disability-FHA reasonable-accommodation pleading-stage opinion citing *Loper Bright*.
   - Result: INCLUDED.

### B. Additional in-window procedural / non-substantive disability-FHA hit

3. *Heimkes v. Fairhope Motorcoach Resort Condominium Owners Association* (S.D. Ala. Sept. 10, 2025)
   - Date filed: 2025-09-10
   - Local opinion source: `allFHAcases/recentcases/10669569_2025_Heimkes v. Fairhope Motorcoach Resort Condominium Owners Ass'n_alsd.txt`
   - Local database support:
     - `data/FHA_Unified_Database.json` -> `loper_bright_cited = YES`
     - `data/FHA_RA_Database_unified_20260328_090852.json` -> `loper_bright_cited = YES`
   - Why it should be treated separately:
     - The opinion is a memorandum opinion and order resolving motions to recuse and for mistrial.
     - The local coding is `procedural_posture = OTHER_PROCEDURAL`.
     - The opinion's *Loper Bright* reference comes in describing a voicemail/ex parte-communication dispute in which the clerk advised counsel to review *Loper Bright* rather than rely on *Chevron*.
     - It does not substantively resolve the underlying FHA reasonable-accommodation claim.
   - Result: INCLUDED ONLY AS A PROCEDURAL HIT; EXCLUDED FROM THE SUBSTANTIVE FHA OPINION COUNT.

### C. In-window false positives / excluded public-search cases

4. *National Education Association, et al. v. U.S. Department of Education, et al.* (D.N.H. Apr. 24, 2025)
   - Why it appeared: the opinion cites *Loper Bright* and discusses *Havens Realty*.
   - Why excluded: the Fair Housing Act appears only in a standing discussion about *Havens Realty*; this is not an FHA claim or defense.
   - Result: EXCLUDED.

5. *Refugee and Immigrant Center for Education and Legal Services v. Noem* (D.D.C. Jul. 2, 2025)
   - Why it appeared: query noise from `fair housing` and administrative-law discussion.
   - Why excluded: not an FHA case; no FHA claim/defense.
   - Result: EXCLUDED.

6. *Immigrant Defenders Law Center v. Noem* (9th Cir. Jul. 18, 2025)
   - Why it appeared: the opinion cites *Loper Bright* and mentions the Fair Housing Act through *Havens Realty* standing precedent.
   - Why excluded: the FHA is only an analogy/source of standing doctrine, not the cause of action being litigated.
   - Result: EXCLUDED.

7. *National Labor Relations Board v. Macy's Inc.* (9th Cir. Oct. 21, 2025)
   - Why it appeared: CourtListener search noise.
   - Why excluded: text review did not show an FHA claim/defense.
   - Result: EXCLUDED.

8. *Jay Pemberton v. Bell's Brewery, Inc.* (6th Cir. Sept. 4, 2025)
   - Why it appeared: `reasonable accommodation` query.
   - Why excluded: employment disability accommodation case, not FHA/housing discrimination.
   - Result: EXCLUDED.

9. *National Association of Industrial Bankers v. Weiser* (10th Cir. Nov. 10, 2025)
   - Why it appeared: `reasonable accommodation` query noise.
   - Why excluded: not an FHA case.
   - Result: EXCLUDED.

10. *Powers v. McDonough* (9th Cir. Dec. 23, 2025)
   - Why it appeared: discusses housing as an accommodation and cites *Loper Bright*.
   - Why excluded: not an FHA claim/defense.
   - Result: EXCLUDED.

11. *ANAHEIM GARDENS v. United States* (Fed. Cl. Dec. 19, 2025)
   - Why it appeared: mentions HUD and dwelling units and cites *Loper Bright*.
   - Why excluded: HUD housing-program / contract litigation, not FHA discrimination litigation.
   - Result: EXCLUDED.

12. *Brandi Booth v. Jonathan Lazzara* (6th Cir. Jan. 14, 2026)
   - Why it appeared: disability / accommodation query.
   - Why excluded: not an FHA claim/defense.
   - Result: EXCLUDED.

## PCI v. Todman status

The case referred to as "PCI v. Todman" is:

- *Property Casualty Insurers Association of America v. Todman* at the district-court stage; and
- on appeal, after secretary substitution, *Property Casualty Insurers Association of America v. E. Scott Turner*, Seventh Circuit No. 24-1947.

Public-source findings:

1. Web search for `"PCI v. Todman"` identified the case and linked public docket/status pages.
2. A public FindLaw page reports the district-court opinion on the substance of the FHA dispute as decided on 2024-03-26, i.e., before *Loper Bright*.
3. CourtListener opinion searches returned no 2025-2026 opinion for the appeal.
4. CourtListener's docket search returned the Seventh Circuit docket with argument date 2025-01-16 and no termination date.
5. The U.S. Chamber case page (`https://www.uschamber.com/cases/discrimination/property-casualty-insurers-association-of-america-v-todman`) labels the case status as `Pending`.

Conclusion on PCI/Todman:

- PCI/Todman does not supply a Jan. 2025-Apr. 16, 2026 federal opinion citing *Loper Bright* in an FHA dispute.
- Its only public substantive decision I located is the 2024 district-court decision, which predates *Loper Bright*.
- The Seventh Circuit appeal was still publicly marked pending, with no substantive opinion found.

## Final conclusion

As of 2026-04-16, the statement "there is no FHA-specific *Loper Bright* citation" is not accurate.

The corrected update is:

- There are at least two verified federal FHA substantive opinions in the Jan. 2025-Apr. 2026 search window that cite *Loper Bright*: *Sara Watts v. Joggers Run Property Owners Association, Inc.*, 133 F.4th 1032 (11th Cir. 2025), and *Meredith Twyman v. Recap PA Holdings, LLC* (E.D. Pa. Mar. 12, 2025).
- There is at least one verified Jan. 2025-Apr. 16, 2026 federal disability-FHA reasonable-accommodation pleading-stage opinion citing *Loper Bright*: *Twyman*.
- I found no verified in-window reasonable-modification substantive FHA opinion citing *Loper Bright*.
- *Heimkes v. Fairhope Motorcoach Resort Condominium Owners Association* is best treated as a separate procedural/non-substantive disability-FHA hit because its September 10, 2025 opinion is a recusal order that mentions *Loper Bright* without substantively resolving the FHA accommodation claim.
- PCI v. Todman remains a non-example for this period because its only public substantive opinion predates *Loper Bright* and the appeal was still pending in public sources.
