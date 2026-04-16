# Disability wave top-12 validation results

## Scope
This memo validates the 12-record manual pass identified in `disability_wave_validation_priority_memo.md`. I reviewed the current model classifications in `unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json` and read the underlying opinion text for each exact record in `allFHAcases/`.

## Bottom line
The memo’s central concern was correct. Most of this 12-record set is not made up of substantive FHA merits rulings. Eight of the twelve records are early procedural orders (service orders, counsel denials, recommittal for screening, or wrong-defendant dismissal without FHA merits analysis) and should not be used as affirmative support for a pleading-failure narrative.

Net assessment of the 12:
- 7 records: keep only as context / non-merits tracking; exclude from analytic counts about substantive FHA pleading failure
- 1 record: likely false-positive FHA record and should be recoded out of the FHA merits pool
- 3 records: real adverse rulings with substantive screening analysis, but 2 of those need mechanism recoding or caution
- 1 record: substantive classification looks strong as currently coded

## Record-by-record results

| # | Record | Current model classification | Validation assessment | Recommended action |
|---|---|---|---|---|
| 1 | `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd` | `UNCLEAR / CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS` | Weak for analytics, but directionally correct that no merits failure can be diagnosed | Hold out as non-merits/context only |
| 2 | `10219016_2022_Shepherd v. Cornerstone Residential_utd` | `UNCLEAR / UNCLEAR` | Strong as a non-merits classification | Hold out as non-merits/context only |
| 3 | `10193953_2024_Avila v. ACACIA Network, Inc._nysd` | `UNCLEAR / UNCLEAR` | Strong as a non-merits classification | Hold out as non-merits/context only |
| 4 | `9913834_2022_Chapman v. Franklin County Sheriff_ohsd` | `UNCLEAR / UNCLEAR` | Weak; likely not an FHA-usable merits record and may be a category-fit false positive | Recode to non-merits/likely non-FHA false-positive context |
| 5 | `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord` | `UNCLEAR / UNCLEAR` | Strong as a non-merits classification | Hold out as non-merits/context only |
| 6 | `9885949_2023_Rosa v. Pathstone Corporation_nysd` | `UNCLEAR / UNCLEAR` | Strong as a non-merits classification | Hold out as non-merits/context only |
| 7 | `10803192_2026_Jermaine Capel v. Norfolk Redevelopment _ Housing Authority_ca4` | `TRANSLATION / NO_COGNIZABLE_FHA_THEORY` | Plausible but weakly grounded from the available text | Keep provisional only; validate against district opinion before relying |
| 8 | `10609257_2025_McLain v. Sedgwick County Sheriff's Office_ksd` | `TRANSLATION / NO_COGNIZABLE_FHA_THEORY` | Needs recoding; this record is about litigation accommodations, not housing discrimination | Recode out of FHA merits pool; treat as ADA/procedural-access context |
| 9 | `9939426_2023_WISSMAN v. PGM REAL ESTATE LLC, PROPERTY MANAGEMENT_paed` | `TRANSLATION / STATUTORY_HOOK_UNCLEAR` | Substantive ruling exists, but mechanism is too shallow | Keep in merits pool but recode mechanism |
| 10 | `9589809_2023_Goodwin v. City Attorney's Office_caed` | `TRANSLATION / STATUTORY_HOOK_UNCLEAR` | Substantive screening ruling exists; code is broadly plausible but still thin | Keep with caution; likely mechanism is `NO_COGNIZABLE_FHA_THEORY` rather than merely unclear hook |
| 11 | `10631726_2025_Ballentine v. Cares for the Homeless_nysd` | `PROCEDURAL_GATEWAY / JURISDICTION_OR_STANDING` | Directionally correct but not a substantive FHA merits record | Hold out as non-merits/context only |
| 12 | `9873146_2022_Sykes v. New York City Housing Authority_nysd` | `TRANSLATION / DISABILITY_NEXUS_MISSING` | Strong | Keep as validated substantive record |

## Detailed notes

### 1. Sandles v. Secretary of Veterans Affairs
Available text: order denying appointment of counsel only.

What the opinion actually does:
- Says plaintiffs alleged FHA and Civil Rights Act violations involving septic-system repairs, water shutoff, and attempted eviction.
- Does not adjudicate any FHA element.
- Notes only that plaintiff had not shown likely success on the merits for counsel-appointment purposes.

Assessment:
- The current `UNCLEAR` family is safer than a merits code.
- But `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS` is not a good analytic signal here because the order is not really a survival ruling.
- This should not be cited as proof of substantive FHA pleading failure or no-failure success.

Recommendation:
- Keep only as context/non-merits tracking.
- If the schema allows, use a procedural/non-merits flag rather than a merits mechanism.

### 2. Shepherd v. Cornerstone Residential
Available text: order denying appointment of counsel only.

What the opinion actually does:
- Expressly says plaintiff brought FHA claims.
- Notes the complaint survived § 1915 screening.
- Does not adjudicate dismissal, pleading sufficiency on the merits, or any FHA element.

Assessment:
- Current `UNCLEAR / UNCLEAR` is appropriate.
- This is a clean example of a record that should be tracked but not counted as a substantive pleading-failure observation.

Recommendation:
- Hold out from analytic counts.

### 3. Avila v. Acacia Network
Available text: order of service only.

What the opinion actually does:
- States plaintiff asserts disability-discrimination and retaliation claims under the FHA, ADA, and state law.
- Merely directs issuance of summonses and marshals service.
- No merits analysis.

Assessment:
- Current `UNCLEAR` coding is strong.
- This record should not support any pleading-failure proposition.

Recommendation:
- Hold out from analytic counts.

### 4. Chapman v. Franklin County Sheriff
Available text: recommittal order after initial screening.

What the opinion actually does:
- Dismisses some defendants.
- Notes plaintiff listed FHA claims among numerous jail/correctional claims.
- Recommits the matter for more specific screening because the court doubts the viability of several claims.
- Does not actually resolve the FHA theory.

Assessment:
- The current low-confidence treatment is warranted.
- This looks especially poor as an FHA record because the defendant is a sheriff/correctional setting, not an ordinary housing provider or housing authority, and the text gives no developed FHA analysis.
- I would not rely on this as either a substantive FHA failure case or a stable public-process housing case.

Recommendation:
- Recode as non-merits and likely false-positive/category-fit problem unless later opinions supply a real FHA housing ruling.

### 5. Jacobson v. AH Gresham Park
Available text: order denying appointment of pro bono counsel only.

What the opinion actually does:
- Says plaintiff asserts claims under the ADA and federal FHA.
- Holds only that counsel is not warranted at this early stage.
- No merits ruling.

Assessment:
- Current `UNCLEAR` coding is appropriate as long as it is not counted as a merits disposition.

Recommendation:
- Hold out from analytic counts.

### 6. Rosa v. Pathstone Corporation
Available text: order of service only.

What the opinion actually does:
- States plaintiff brought suit under FHA § 3604 and § 1983 concerning termination of a Section 8 voucher.
- Directs service of the second amended complaint.
- No merits analysis.

Assessment:
- Current `UNCLEAR` coding is appropriate.
- Public-process flag is plausible because the dispute concerns voucher administration, but there is still no merits ruling.

Recommendation:
- Hold out from analytic counts pending a substantive opinion.

### 7. Jermaine Capel v. Norfolk Redevelopment & Housing Authority
Available text: only a short Fourth Circuit affirmance.

What the opinion actually does:
- Says the district court dismissed the amended complaint under § 1915(e)(2)(B).
- Mentions § 1983 and FHA claims.
- Gives no substantive reasoning beyond affirmance.

Assessment:
- The current `TRANSLATION / NO_COGNIZABLE_FHA_THEORY` classification is plausible, but the available text is too thin to validate the mechanism confidently.
- This is not strong enough yet for careful doctrinal use.

Recommendation:
- Keep only as a provisional coding.
- Before relying on it, retrieve and validate the district court opinion cited in the affirmance.

### 8. McLain v. Sedgwick County Sheriff’s Office
Available text: order denying request for counsel and requested ADA accommodations in the litigation.

What the opinion actually does:
- Describes a suit against a sheriff’s office and other public/private actors.
- Recounts plaintiffs’ request for litigation accommodations: extended filing time, written instructions, and communication accommodations.
- Does not adjudicate a housing discrimination claim.

Assessment:
- This is the clearest likely false positive in the set.
- The opinion text is about disability-related participation in the lawsuit, not denial of housing rights.
- The current `TRANSLATION / NO_COGNIZABLE_FHA_THEORY` code catches the mismatch, but the better move is to remove the record from the FHA merits pool rather than retain it as an FHA translation failure.

Recommendation:
- Recode as non-FHA / ADA-procedural-access context.
- Exclude from FHA substantive analytics.

### 9. Wissman v. PGM Real Estate
Available text: substantive screening memorandum plus dismissal order.

What the opinion actually does:
- Describes a private-landlord/property-management dispute involving repairs, eviction, alleged harassment, Section 8 participation, and plaintiff’s asserted PTSD/depression/bipolar disorder.
- Dismisses FHA claims without prejudice at screening.
- Explains that landlord-tenant maintenance disputes are not enough by themselves.
- Says plaintiff did not plausibly tie the challenged actions to protected-class discrimination.
- Says Section 8 voucher-holder status alone is not protected under the FHA.
- Says alleged sexual-harassment/interference facts were not severe or pervasive enough, and retaliation allegations did not sufficiently link protected activity to adverse action.

Assessment:
- This is a real substantive FHA screening dismissal.
- The present model mechanism `STATUTORY_HOOK_UNCLEAR` undersells what the court actually did.
- The better description is closer to `NO_COGNIZABLE_FHA_THEORY` or, secondarily, `ELEMENTS_NOT_TIED_TO_FACTS`, because the court walked through several possible FHA theories and found the allegations did not plausibly satisfy them.

Recommendation:
- Keep in the merits pool.
- Recode mechanism away from `STATUTORY_HOOK_UNCLEAR` to `NO_COGNIZABLE_FHA_THEORY` or `ELEMENTS_NOT_TIED_TO_FACTS`.

### 10. Goodwin v. City Attorney’s Office
Available text: screening order, findings and recommendations, and final dismissal order.

What the opinion actually does:
- Plaintiff cited “The Fair Housing Act – sections 102 and 103 of the Civil Rights Act of 1991.”
- Complaint alleged only “Denied Fair Housing Act Intentional Discrimination” and a few fragments about property damage and trauma.
- Court held the complaint violated Rule 8 and contained no factual allegations supporting any FHA claim.
- Final dismissal rested on failure to state a claim and failure to prosecute after plaintiff did not amend.

Assessment:
- This is a substantive screening failure, but it is not really a nuanced public-process housing case.
- The current `STATUTORY_HOOK_UNCLEAR` code is defensible because plaintiff miscited the law, but the stronger description is again `NO_COGNIZABLE_FHA_THEORY`: the complaint had almost no housing facts and no cognizable FHA pleading at all.

Recommendation:
- Keep with caution in the merits pool if the project wants to include extremely thin screening dismissals.
- Prefer recoding mechanism to `NO_COGNIZABLE_FHA_THEORY`.

### 11. Ballentine v. Cares for the Homeless
Available text: order of service.

What the opinion actually does:
- Says the court can construe the pleading as asserting FHA claims, but the complaint was brought primarily under constitutional, ADA, and state-law theories.
- Dismisses claims against NYC Department of Homeless Services because it is not a suable entity.
- Orders service on remaining defendants.
- No substantive FHA analysis.

Assessment:
- Current `PROCEDURAL_GATEWAY / JURISDICTION_OR_STANDING` is directionally correct.
- But this still should not count as a substantive FHA failure case.

Recommendation:
- Hold out from analytic counts until a later merits ruling exists.

### 12. Sykes v. NYCHA
Available text: order to amend plus later dismissal order.

What the opinion actually does:
- Plaintiff alleged repeated repair requests, severe apartment conditions, and disability within the household in a NYCHA apartment.
- The court carefully explained why the FHA claim failed: no facts showing disability was a motivating factor in NYCHA’s failure to repair, and no facts showing a requested accommodation necessary to equal enjoyment of the dwelling.
- The dismissal order repeats that plaintiff sought effectively preferential repair priority without pleading the required disability nexus.

Assessment:
- This is the strongest validated merits record in the set.
- The current `TRANSLATION / DISABILITY_NEXUS_MISSING` code fits the opinion well.
- If anything, the case also contains a secondary request-articulation problem, but the current main mechanism is sound.

Recommendation:
- Keep as validated.
- This is one of the few records in the set that can safely support the draft’s substantive pleading-failure analysis.

## Overall recommendations for the dataset

1. Remove or hold out the non-merits records from substantive pleading-failure counts:
   - Sandles
   - Shepherd
   - Avila
   - Chapman
   - Jacobson
   - Rosa
   - Ballentine

2. Recode likely non-FHA false positive:
   - McLain

3. Keep but recode mechanism:
   - Wissman -> likely `NO_COGNIZABLE_FHA_THEORY` or `ELEMENTS_NOT_TIED_TO_FACTS`
   - Goodwin -> likely `NO_COGNIZABLE_FHA_THEORY`

4. Keep as provisional until better text is retrieved:
   - Capel

5. Keep as strong validated substantive record:
   - Sykes

## Draft-use implication
The top-12 pass confirms that the main immediate draft risk is overclaiming from early-stage records. The one clear, strong substantive public-process record in this set is `Sykes`. `Wissman` and `Goodwin` are usable only with narrower descriptions than the current queue framing suggests. The rest of the set is primarily valuable as evidence of queue noise, category-fit instability, or the need for later-stage follow-up rather than as affirmative substantive support.