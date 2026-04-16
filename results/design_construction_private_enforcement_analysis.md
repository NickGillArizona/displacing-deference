# FHA design-and-construction private-enforcement barriers memo

Generated: 2026-04-16T05:46:31-07:00
Repo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH`

## Bottom line

The best-supported explanation for the thin private-enforcement pipeline under 42 U.S.C. § 3604(f)(3)(C) is not that federal courts regularly kill these cases on mootness or Rule 23 grounds. The stronger barriers are:

1. standing doctrine as applied in several recent cases now demands a highly particularized plaintiff-specific injury theory, especially after `TransUnion`,
2. statute-of-limitations rules in `Garcia v. Brockway` jurisdictions that can start the clock before any disabled person or tester encounters the building, and
3. expert-heavy inspection/discovery costs that make these cases unusually counsel- and organization-dependent.

The local FHA Unified Database supports that framing, but the relevant denominator is the repo-standard screened disability written-opinion cohort rather than all 3,198 rows in the JSON file. Within that screened disability cohort (`screening_result != NO`, non-empty `case_name`, and `protected_classes` including `disability`), the repo-standard D&C selector (`primary_claim_type == design_and_construction` OR `fha_section_cited == 3604(f)(3)(C)` OR lowercase `claim_types` containing `design_and_construction`) yields 56 federal written opinions. The narrower local keyword-review selector based on D&C tags in `claim_types` also yields 56 opinions, but not the identical 56 opinions because one opinion is tagged only in `primary_claim_type` while another uses uppercase `DESIGN_AND_CONSTRUCTION` in `claim_types`. In either 56-opinion local snapshot, the aggregate counts below are unchanged. Of those 56:

- 26 are motion-to-dismiss opinions,
- 5 are discovery opinions,
- 6 are settlement/consent opinions,
- 48 are not pro se,
- 20 are brought by fair-housing organizations or government plaintiffs,
- 0 mention `class certification` / `Rule 23` in the coded `key_holding` or `brief_summary` text, and
- only 1 mentions mootness at all, and that one is incidental rather than a merits barrier.

At the same time, once these cases are actually litigated, they often do relatively well. Among the 41 non-procedural D&C opinions in the local database, 32 (78.0%) ended in a plaintiff win, mixed result, or settlement. That supports a bottleneck story: the hardest part is getting a technically viable, timely, properly-plaintiffed case into court, not winning every merits issue once there.

## Exact search sources used

Public legal sources reviewed:

1. CourtListener search API:
   - `https://www.courtlistener.com/api/rest/v4/search/`
   - queries used:
     - `"Fair Housing Act" "design and construction" standing`
     - `"Fair Housing Act" "design and construction" mootness`
     - `"Fair Housing Act" "design and construction" "class certification"`
     - `"Fair Housing Act" "design and construction" "statute of limitations"`
     - `"Garcia v. Brockway"`
     - plus follow-on case-name searches for `Jafri`, `Post Goldtex`, `Spanos`, `Noble Homes`, `DeBoard`, and `203 Jay St.`
2. Garcia en banc opinion PDF (Justia mirror):
   - `https://cases.justia.com/federal/appellate-courts/ca9/05-35647/0535647-2011-02-25.pdf?ts=1411056308`
3. Sixth Circuit `Village of Olde St. Andrews` PDF (Justia mirror):
   - `https://cases.justia.com/federal/appellate-courts/ca6/05-5862/06a0900n-06-2011-02-25.pdf?ts=1411011977`
4. `Jafri v. Chandler LLC` summary (Midpage):
   - `https://app.midpage.ai/case/jafri-v-chandler-llc-8711421`
5. `Fair Housing Justice Center, Inc. v. 203 Jay St. Associates, LLC` summary (Midpage):
   - `https://app.midpage.ai/case/fair-housing-justice-center-inc-10308487`
6. `National Fair Housing Alliance v. A.G. Spanos Construction, Inc.` orders:
   - DOJ PDF: `https://www.justice.gov/sites/default/files/crt/legacy/2010/12/15/spanosorder.pdf`
   - Relman PDF: `https://www.relmanlaw.com/media/cases/781_Spanos_-_Order_Denying_Def_Motions_to_Dismiss.pdf`
7. `Sentell v. RPM Management Company, Inc.` summary (CaseMine):
   - `https://www.casemine.com/judgement/us/5914b15dadd7b04934758e0b`
8. `DeBoard v. Elmwood One, LLC` summary (CaseMine):
   - `https://www.casemine.com/judgement/us/611a6a704653d0107d671d54`
9. `DEBD. v. VENTRY APARTMENTS, LLC` summary (Studicata):
   - `https://www.studicata.com/summaries/united-states-district-court-northern-district-of-indiana/debd-v-ventry-apartments-llc-2023-e2riv1/`
10. `Smith v. Pacific Properties & Development Corp.` standing summary source:
   - `https://www.tascnow.com/wp-content/uploads/2019/03/TASC_0404_fha_testers.pdf`

Local source reviewed:

11. FHA Unified Database:
   - `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/FHA_Unified_Database.json`
   - method: repo-standard descriptive counts use the screened disability cohort (`screening_result != NO`, non-empty `case_name`, disability in `protected_classes`) and the repo-standard D&C selector (`primary_claim_type == design_and_construction` OR `fha_section_cited == 3604(f)(3)(C)` OR lowercase `claim_types` contains `design_and_construction`). The local keyword review of `key_holding` and `brief_summary` used the D&C-tagged `claim_types` snapshot, which matches the 56-count but differs by one record because of a field-placement/casing inconsistency.

## Local database snapshot

### Repo-standard screened disability written-opinion cohort used here

- Raw rows in local unified database file: 3,198
- Repo-standard screened FHA written-opinion cohort (`screening_result != NO` and non-empty `case_name`): 2,522
- Repo-standard disability cohort (`protected_classes` includes `disability`): 1,720
- Repo-standard D&C opinions (`primary_claim_type == design_and_construction` OR `fha_section_cited == 3604(f)(3)(C)` OR lowercase `claim_types` includes `design_and_construction`): 56
- Narrower local D&C-tag snapshot used for keyword review (`claim_types` includes lowercase or uppercase D&C tag): 56
- D&C share of screened FHA cohort: 2.22%
- D&C share of screened disability cohort: 3.26%

The one-record difference between the two local 56-opinion selectors does not change the aggregate counts reported below because both swap-in / swap-out opinions are represented fair-housing-organization procedural orders coded `OTHER_PROCEDURAL`.

### Plaintiff type in D&C opinions

- Individual tenant: 34
- Fair-housing organization: 13
- Government: 7
- Other: 2

### Representation proxy

- Not pro se: 48
- Pro se: 8
- Represented individual tenants: 26
- Institutional plaintiffs (fair-housing org + government): 20

That composition matters. D&C suits are unusually dependent on counsel and institutional support. The low pro se share does not itself prove a doctrinal bar, but it is consistent with high technical and procedural entry costs.

### Procedural posture in D&C opinions

- Motion to dismiss: 26
- Other procedural: 9
- Summary judgment: 9
- Settlement/consent: 6
- Discovery: 5
- Appeal: 1

### Outcome distribution in D&C opinions

- Procedural: 15
- Plaintiff win: 14
- Mixed: 12
- Defendant win: 9
- Settlement: 6

## Main doctrinal barriers actually supported by the cases

## 1. Standing is a real barrier, but mostly as a particularization problem

The standing cases do not show that private D&C suits are categorically unavailable. They instead suggest that several courts insist on plaintiff-specific injury allegations and are less receptive to bare statutory-violation theories.

### A. Older doctrine was comparatively receptive to testers and organizations

- `Smith v. Pacific Properties & Development Corp., 358 F.3d 1097 (9th Cir. 2004)` treated tester/organizational standing as available in the disability-accessibility context.
- `Fair Housing Council, Inc. v. Village of Olde St. Andrews, Inc., 210 F. App'x 469 (6th Cir. 2006)` held that the Fair Housing Council had standing because it spent resources on testing and investigation, but the Center for Accessible Living did not because it showed too little beyond identifying testers.
- `Fair Housing Justice Center, Inc. v. 203 Jay St. Associates, LLC, 2022 WL 3100557 (E.D.N.Y. 2022)` held that FHJC had Article III and FHA statutory standing based on diversion of resources, and also rejected the argument that a D&C claim requires an actual attempted rental by a disabled person.

That line of authority shows that private systemic enforcement through fair-housing organizations can succeed.

### B. Some post-TransUnion district courts have tightened standing for testers and organizations

Recent district-court cases show a narrower trend:

- `Disability Law Center v. SG Boulevard Multifamily LLC` (D. Utah 2023) dismissed a D&C suit for lack of organizational standing, reasoning that the organization's claimed testing/monitoring expenses were speculative future harms or part of its ordinary operations rather than a cognizable diversion of resources.
- `DeBoard v. Ventry Apartments, LLC` (N.D. Ind. 2023) dismissed a tester's D&C suit because a professional tester who never intended to rent and alleged only a statutory violation did not plead a concrete injury after `TransUnion`.
- `Dana Bowman v. SWBC Real Estate Services, LLC` / `Bowman v. SWBC Real Estates Services, LLC` (N.D. Tex. 2024-25) show the same demand for plaintiff-specific injury: the plaintiff had to connect the alleged barriers to his own wheelchair use and his own inability to access the rental privileges.
- `Casey Millerborg v. Blue Bonnet Trail LLC` (N.D. Tex. 2025) dismissed for lack of standing where the complaint did not sufficiently allege that the plaintiff personally experienced, rather than merely observed, the barriers.

### C. Individual deterrence standing still exists when the plaintiff is concrete enough

The trend is not uniformly defense-friendly. Some courts still recognize standing where the plaintiff is a disabled would-be renter who visited the property, encountered barriers, and was deterred from renting:

- `Jafri v. Chandler LLC, 970 F. Supp. 2d 852 (N.D. Ill. 2013)` held that both the disabled plaintiff and the organization had standing.
- `Chapuis v. Forest Hill Group LLC` (W.D. Tenn. 2025) held that a disabled visitor deterred by barriers had standing.
- `Amy Burnett v. Rutledge Flats, LLC` (M.D. Tenn. 2025) held that a deterred disabled plaintiff plausibly alleged standing against owners and architect.

### D. Best-supported synthesis on standing

Standing is therefore a real private-enforcement barrier, but the cases reviewed do not support the broader claim that “disabled plaintiffs lack standing.” The problem documented here is narrower and more structural:

- a bare observation of noncompliance is often not enough,
- tester and organizational standing is less secure than it was pre-`TransUnion`, and
- individual plaintiffs must plead a personal connection to the barriers with care.

That helps explain why the written-opinion subset skews toward repeat-player organizations and represented plaintiffs with sophisticated pleading and testing protocols.

## 2. Limitations/accrual is the clearest doctrinal barrier, and Garcia matters a lot

This is the strongest doctrinal barrier I found.

### A. Garcia's rule is harsh

`Garcia v. Brockway, 526 F.3d 456 (9th Cir. 2008) (en banc)` held that for private FHA design-and-construction suits, the two-year statute of limitations begins when the design-and-construction phase ends, specifically when the last certificate of occupancy issues. The consequence is severe: the limitations period can expire before a disabled renter or tester ever encounters the inaccessible building.

That is exactly the structural problem the note is trying to identify. Standing requires a concrete plaintiff, but `Garcia` can start the clock before such a plaintiff exists or discovers the problem.

### B. Other courts have taken less restrictive approaches

There is no single nationwide accrual rule.

- `Village of Olde St. Andrews` rejected the statute-of-limitations defense where plaintiffs alleged a continuing policy/practice across the development.
- `Sentell v. RPM Management Company, Inc., 653 F. Supp. 2d 917 (E.D. Ark. 2009)` distinguished between an architect's completed act and an owner/manager's continuing leasing/administration of noncompliant units, allowing the claims against the owner/manager to proceed under a continuing-violation theory.
- `Jafri v. Chandler LLC, 970 F. Supp. 2d 852 (N.D. Ill. 2013)` refused to dismiss on limitations grounds at the pleading stage and treated continuing-violation arguments as plausibly available.
- `Fair Housing Justice Center, Inc. v. JDS Development LLC, 2020 WL 1264493 (S.D.N.Y. 2020)` held that accrual occurs when a protected person encounters the inaccessible design elements, not when construction ends.
- `Fair Housing Justice Center, Inc. v. Lighthouse Living LLC, 2021 WL 4428957 (S.D.N.Y. 2021)` similarly applied continuing-violation reasoning to keep D&C claims timely.

### C. Recent district courts still apply Garcia-like logic outside the Ninth Circuit

The restrictive approach is not confined to the Ninth Circuit.

- `George v. Overall Creek Apartments, LLC` (M.D. Tenn. 2024) held a D&C claim time-barred because the clock started when the last available rental unit was first rented, and an unrented model unit did not extend the period.
- The local database also flags `Birdwell v. AvalonBay Communities, Inc.` (N.D. Cal. 2023) as dismissing D&C allegations as time-barred under Garcia-type reasoning.

### D. Best-supported synthesis on limitations

If the question is “which doctrinal barrier is most clearly documented in the cases?,” the answer is limitations/accrual.

This is the strongest candidate for why underenforcement persists despite relatively favorable merits outcomes once cases are filed. In the stricter jurisdictions, the private suit window may close before the right holder discovers the violation.

## 3. Mootness is a plausible hypothesis, but I found weak support for it as a recurring published barrier

The initial hypothesis that D&C plaintiffs often lose because they move out or because remediation moots the case is not strongly supported by the federal published-opinion set I reviewed.

### What I actually found

- In the 56-opinion local written-opinion subset, a keyword review found only 1 mootness mention, and that reference was incidental in a discovery order rather than a merits ruling.
- `Jafri v. Chandler LLC` is the clearest public mootness hit I found. There, the court rejected the argument that the case was moot simply because the developer temporarily leased one accessible parking space to the plaintiff; the court treated voluntary cessation as insufficient.

### What this means

Mootness can arise, especially if defendants retrofit barriers or change access arrangements mid-case. But in this written-opinion subset it does not appear to be the dominant bottleneck. That is negative evidence within the analyzed opinions, not proof that mootness disputes are absent from underlying dockets.

For note-writing purposes, the careful formulation is:

- supported: mootness occasionally appears, usually in voluntary-cessation/remediation form;
- not well supported: “plaintiffs who move out routinely lose standing or render D&C claims moot.”

I would not make that broader claim without additional docket-level rather than opinion-level research.

## 4. Class certification also looks overstated as an explanation for underenforcement

In the written-opinion subset reviewed here, I found very little evidence that Rule 23 doctrine is doing the main gatekeeping work in private D&C enforcement.

### Evidence

- CourtListener searches for `"Fair Housing Act" "design and construction" "class certification"` returned only a handful of hits, with substantial noise.
- The 56 D&C opinions in the local database produced 0 `class certification` / `Rule 23` hits in the `key_holding` and `brief_summary` fields. That is a negative finding about this coded written-opinion subset, not proof that no D&C dockets involve class-certification disputes.
- The major private systemic D&C cases I found are usually brought by organizations and resolved through large settlements rather than litigated class-certification opinions.

### Best example: Spanos

`National Fair Housing Alliance v. A.G. Spanos Construction, Inc., 542 F. Supp. 2d 1054 (N.D. Cal. 2008)` is the main class-related federal D&C case that surfaced. But even there, the court did not use Rule 23 as a gatekeeping device at the pleading stage. The court held that a proposed defendant owner class was not defeated by personal-jurisdiction objections at that stage. The case later settled, with retrofits to roughly 12,300 units across 82 complexes.

### Best-supported synthesis on class certification

The written-opinion evidence points away from “class certification barrier” as the main explanation for the scarcity of private D&C suits. The stronger explanation from this review is that organizations and represented plaintiffs already serve as the main aggregation mechanism, and many of the biggest cases settle before any class-certification opinion becomes the central published event.

## 5. Discovery and cost barriers are substantial, even when not formally doctrinal

The cases strongly support a technical-burden story.

### A. D&C proof is expert-heavy

These cases often require:

- property inspections,
- architectural measurements,
- comparisons to FHA safe harbors / guidelines,
- sampling across unit types and common areas,
- expert reports on design deviations, and
- document discovery from owners, developers, builders, architects, and property managers.

Examples:

- `United States v. Noble Homes, Inc., 173 F. Supp. 3d 568 (N.D. Ohio 2016)` denied summary judgment because competing experts created genuine disputes over whether deviations from HUD safe harbors amounted to FHA violations.
- `DeBoard v. Elmwood One, LLC` (S.D. Ind. 2021) involved 66 alleged accessibility violations, Rule 26 fights over expert reports, and partial exclusion/preclusion of defense experts.
- `DeBoard v. Union at Crescent, LP` (S.D. Ind. 2023) limited inspection discovery to one unit of each type and one day, illustrating how costly and operationally disruptive inspection practice can become.
- `Geonna Rickey v. GVD Hyde Park, LLC` (E.D. Tex. 2021) required defendants to preserve detailed photos and measurements of modifications before inspection, confirming how quickly evidentiary issues become technical.

### B. Cost stakes are high enough to deter small private suits

- `Dana Bowman v. Prida Construction, Inc.` (S.D. Tex. 2021) reduced a requested fee award from $159,308.75 to $79,213.75. Even with a reduction, that still shows the litigation-cost scale of a single successful accessibility case.
- `Stason Sutton / FHJC v. CREF 546 West 44th Street` (S.D.N.Y. 2025) settled for $1.1 million plus retrofits.
- Public reporting on `FHJC v. JDS Development LLC` describes a $2.9 million resolution.
- The `Spanos` settlement required retrofits on a truly national scale.

### C. Multi-defendant satellite litigation adds friction

The local database repeatedly shows owner/developer/architect contribution and indemnity disputes:

- `Fair Housing Justice Center v. 203 Jay St. Associates, LLC`
- `George v. Overall Creek Apartments, LLC`
- `Bowman v. Shadowbriar Apartments, LLC`

Those disputes do not necessarily block plaintiffs from stating a claim, but they increase cost, delay, and complexity. From a private-enforcement perspective, that is another reason D&C suits tend to require repeat-player counsel and organizational backing.

## Secondary but real substantive narrowing rules

These are not the main pipeline barriers requested in the prompt, but they matter:

1. `Fair Housing Rights Center in Southeastern Pennsylvania v. Post Goldtex GP, LLC, 823 F.3d 209 (3d Cir. 2016)` narrowed § 3604(f)(3)(C) by holding that a converted commercial building was outside the FHA design-and-construction duty under HUD's first-occupancy interpretation.
2. Coverage disputes about what counts as a `covered multifamily dwelling` or a `building` can consume substantial litigation effort before the merits of the accessibility violations themselves are reached.

These are more properly described as scope-of-duty limitations than standing barriers, but they further thin the set of viable private cases.

## What is actually supported, and what is not

### Strongly supported by the cases

- standing can be a real and sometimes severe barrier, especially for testers and organizations in some post-`TransUnion` cases;
- limitations/accrual is the clearest structural doctrinal barrier, especially in `Garcia` jurisdictions;
- D&C litigation is inspection-, expert-, and cost-intensive;
- private D&C enforcement is disproportionately carried by represented plaintiffs and fair-housing organizations rather than pro se renters.

### Weakly supported or overstated if stated too strongly

- “mootness is the main reason private D&C suits fail”;
- “plaintiffs who move out routinely lose standing in published D&C cases”;
- “class certification doctrine is the main reason there are so few D&C cases.”

## Takeaway for the note

The most defensible formulation is:

Private enforcement of § 3604(f)(3)(C) is underinclusive because private suits still depend on a plaintiff concrete enough to satisfy modern Article III standing, while in the most restrictive jurisdictions the limitations period may start before any such plaintiff encounters the building. Add expert inspections, safe-harbor disputes, multi-defendant discovery, and retrofit-scale remedies, and the practical result is a highly counsel-dependent enforcement channel that organizations can sometimes use but ordinary disabled renters often cannot.

That is a stronger and better-supported claim than saying mootness or class-certification doctrine is doing most of the work.

## Appendix: key cases reviewed by issue

### Standing
- `Smith v. Pacific Properties & Development Corp., 358 F.3d 1097 (9th Cir. 2004)`
- `Fair Housing Council, Inc. v. Village of Olde St. Andrews, Inc., 210 F. App'x 469 (6th Cir. 2006)`
- `Fair Housing Justice Center, Inc. v. 203 Jay St. Associates, LLC, 2022 WL 3100557 (E.D.N.Y. 2022)`
- `Disability Law Center v. SG Boulevard Multifamily LLC` (D. Utah 2023)
- `DeBoard v. Ventry Apartments, LLC` (N.D. Ind. 2023)
- `Bowman v. SWBC Real Estate Services, LLC` (N.D. Tex. 2024-25)
- `Casey Millerborg v. Blue Bonnet Trail LLC` (N.D. Tex. 2025)
- `Chapuis v. Forest Hill Group LLC` (W.D. Tenn. 2025)
- `Amy Burnett v. Rutledge Flats, LLC` (M.D. Tenn. 2025)

### Limitations / Garcia split
- `Garcia v. Brockway, 526 F.3d 456 (9th Cir. 2008) (en banc)`
- `Fair Housing Council, Inc. v. Village of Olde St. Andrews, Inc., 210 F. App'x 469 (6th Cir. 2006)`
- `Sentell v. RPM Management Company, Inc., 653 F. Supp. 2d 917 (E.D. Ark. 2009)`
- `Jafri v. Chandler LLC, 970 F. Supp. 2d 852 (N.D. Ill. 2013)`
- `Fair Housing Justice Center, Inc. v. JDS Development LLC, 2020 WL 1264493 (S.D.N.Y. 2020)`
- `Fair Housing Justice Center, Inc. v. Lighthouse Living LLC, 2021 WL 4428957 (S.D.N.Y. 2021)`
- `George v. Overall Creek Apartments, LLC` (M.D. Tenn. 2024)

### Mootness
- `Jafri v. Chandler LLC, 970 F. Supp. 2d 852 (N.D. Ill. 2013)`

### Class / aggregation
- `National Fair Housing Alliance v. A.G. Spanos Construction, Inc., 542 F. Supp. 2d 1054 (N.D. Cal. 2008)`

### Discovery / cost / technical proof
- `United States v. Noble Homes, Inc., 173 F. Supp. 3d 568 (N.D. Ohio 2016)`
- `DeBoard v. Elmwood One, LLC` (S.D. Ind. 2021)
- `DeBoard v. Union at Crescent, LP` (S.D. Ind. 2023)
- `Geonna Rickey v. GVD Hyde Park, LLC` (E.D. Tex. 2021)
- `Dana Bowman v. Prida Construction, Inc.` (S.D. Tex. 2021)

### Scope-of-duty / coverage narrowing
- `Fair Housing Rights Center in Southeastern Pennsylvania v. Post Goldtex GP, LLC, 823 F.3d 209 (3d Cir. 2016)`
