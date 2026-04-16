# Disability wave R1 validation priority memo

## Scope and method
I reviewed the three queue files plus the final resolved results file:

- `disability_wave_r1_low_confidence_queue.json` (54 rows)
- `disability_wave_r1_high_review_queue.json` (132 rows)
- `disability_wave_r1_priority_validation_queue.json` (333 rows)
- `unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json` (1330 rows)

Key queue facts:

- The low-confidence and high-review queues produce a union of 144 unique records.
- 42 records appear in both low-confidence and high-review.
- Every low-confidence and high-review row is already present in the 333-row priority validation queue.
- The low-confidence queue is dominated by `UNCLEAR` or non-merits records; the high-review queue is dominated by `TRANSLATION`, `PROCEDURAL_GATEWAY`, and other draft-sensitive rows.

This memo is validation-oriented rather than merits-adjudicative: it prioritizes which rows are most likely to distort the draft if left unchecked.

## Bottom line
The biggest near-term draft risk is overclaiming from early-stage or non-merits records that are currently coded as if they support a substantive pleading-failure story when the opinion text may not yet justify that move. The second biggest risk is underclaiming in public-process cases where a real administrative failure or translation breakdown may be present, but the current coding may be too shallow, too jurisdictional, or mapped to the wrong statute.

Recommended next pass: validate the low+high intersection first, with special attention to the subset that combines (1) low confidence, (2) high raw-text review priority, and (3) either early procedural posture or public-process/theory-mapping conflict.

## Validation tranches

### Tranche 1: Early/non-merits records that could inflate counts
Risk type: overclaiming
Count: 16 records
Composition: 11 in both low-confidence and high-review; 5 in low-confidence only
Why this tranche matters:
- These records often involve service orders, counsel-denial orders, discovery orders, or otherwise pending cases.
- If the draft treats them as evidence of substantive FHA pleading failure, it risks attributing meaning the opinion has not yet supplied.
- These rows are especially dangerous because they can silently expand the denominator or be cited as support for doctrinal claims that the underlying orders do not actually resolve.

Highest-priority examples:
1. `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd`
   - Low confidence, high review, public-process flagged, doctrinal gap = medium.
   - Record is still pending after counsel denial, but the classification also says the theory may actually be `NOT_FHA` despite an accommodation-denial frame.
   - This is the single most draft-sensitive row because it combines early posture with statutory-fit uncertainty.
2. `10219016_2022_Shepherd v. Cornerstone Residential_utd`
   - Only a counsel-denial ruling; no FHA merits adjudication.
   - Current coding points to theory-selection/fact-development gaps, but the opinion may be too thin to support any failure diagnosis.
3. `10193953_2024_Avila v. ACACIA Network, Inc._nysd`
   - Service-of-process order only; all claims remain pending.
   - Current `UNCLEAR` coding is probably appropriate, but the row should not be allowed to function as positive support for a pleading-failure proposition.
4. `9913834_2022_Chapman v. Franklin County Sheriff_ohsd`
   - Recommitted for screening review, not finally dismissed.
   - Government defendant and thin facts make it tempting to overread; that should be checked directly.
5. `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord`
   - Procedural counsel ruling only; no substantive FHA adjudication.
6. `9885949_2023_Rosa v. Pathstone Corporation_nysd`
   - Procedural service order; public-process flagged, but still too early for confident substantive coding.

Validation instruction for this tranche:
- Confirm whether the opinion actually adjudicates an FHA claim.
- If not, preserve the row for tracking but remove it from any analytic use that implies a pleading failure, no-failure merits win, or doctrinal proposition.

### Tranche 2: Theory-mapping and category-fit conflicts
Risk type: mixed, but highly draft-sensitive
Count: 46 records
Composition: 21 in both queues, 21 in high-review only, 4 in low-confidence only
Why this tranche matters:
- These are the rows most likely to swing the draft’s characterization of what kind of failure is happening.
- They often involve records where the grievance may be real but the current FHA coding is unstable: wrong statutory hook, wrong defendant, retaliation vs accommodation mismatch, or an `UNCLEAR` label sitting on top of a stronger theory.
- Errors here can create both overclaiming and underclaiming at once.

Highest-priority examples:
1. `10803192_2026_Jermaine Capel v. Norfolk Redevelopment _ Housing Authority_ca4`
   - Public housing context, low confidence, high review.
   - Current code says `TRANSLATION / NO_COGNIZABLE_FHA_THEORY`, with theory marked `NOT_FHA` and accommodation details undetermined.
   - High leverage because validating it will clarify whether this is an actual FHA translation failure or a non-FHA false positive.
2. `10609257_2025_McLain v. Sedgwick County Sheriff's Office_ksd`
   - Public defendant, but requested relief appears to be litigation accommodations rather than housing relief.
   - Likely ADA/public-entity or procedural-access issue, not FHA.
   - Important for cleaning false positives from the public-process bucket.
3. `9939426_2023_WISSMAN v. PGM REAL ESTATE LLC, PROPERTY MANAGEMENT_paed`
   - Screening dismissal with `STATUTORY_HOOK_UNCLEAR` and undetermined accommodation type.
   - Good candidate for a model re-read because the grievance may be FHA-relevant but under-described.
4. `9589809_2023_Goodwin v. City Attorney's Office_caed`
   - Municipal/public-process setting, low confidence, `STATUTORY_HOOK_UNCLEAR`.
   - Could matter for whether the draft is capturing public housing-adjacent failures or merely general municipal grievances.
5. `10337087_2025_Anderson Bey v. Roc Nation LLC_nysd`
   - Mixed complaint with public housing authority and private entities; current no-failure/unclear coding is unstable.
6. `9913834_2022_Chapman v. Franklin County Sheriff_ohsd`
   - Also belongs here because the combination of government defendant + `UNCLEAR` theory + incomplete screening posture makes category fit uncertain.

Validation instruction for this tranche:
- Re-read the underlying opinion to answer one narrow question first: is this actually an FHA case, or is it better understood as ADA, due process, Section 1983, landlord-tenant, or general grievance litigation?
- If FHA remains plausible, then validate the failure family and mechanism.

### Tranche 3: Public-process cases likely to be undercounted if left shallowly coded
Risk type: underclaiming
Count: 16 records
Composition: 15 in high-review only, 1 in both queues
Why this tranche matters:
- This is the tranche most likely to matter for a disability-centered AFFH argument about administrative process failure, public intermediaries, and institutionally observable facts.
- Many of these cases are currently coded as jurisdictional or translation failures, but the reasoning suggests deeper problems: wrong defendant targeting, missing disability nexus articulation, failure to specify the accommodation request, or inability to connect repair/program facts to FHA doctrine.
- If validated well, these rows can strengthen the draft without overclaiming because the opinions do contain adverse rulings, just not always under the most analytically useful label.

Highest-priority examples:
1. `10631726_2025_Ballentine v. Cares for the Homeless_nysd`
   - The only low+high overlap in this tranche.
   - Jurisdictional dismissal against NYC DHS, but the reasoning suggests intake, theory selection, and public-process failure all at once.
   - This is the best candidate for immediate checking if the draft leans on homeless-services/public-process breakdowns.
2. `9873146_2022_Sykes v. New York City Housing Authority_nysd`
   - Public housing authority; disability nexus to emergency repairs was not properly alleged.
   - Strong underclaiming candidate because the observable facts may support a richer accommodation-process story than the current coding reflects.
3. `9695934_2022_Johnson v. South Bend Housing Authority_innd`
   - Mold/heat and relocation-assistance allegations in public housing, dismissed for failure to plead federal-question-worthy FHA discrimination.
   - Useful for showing public-process failure tied to repair requests and relocation framing.
4. `9680054_2022_Jackson v. Chicago Housing Authority_ilnd`
   - Section 8 context; wrong-entity problem and causal-link failure.
   - High-value because proper-defendant confusion is central to institutional triage.
5. `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4`
   - Housing authority defendant, request not clearly alleged, per curiam affirmance with thin factual/legal articulation.
   - Good candidate for model validation because the present record may understate the accommodation-request story.
6. `9741403_2023_Cooper v. Mr. Timmins_mdd`
   - Public-process flagged, request not adequately articulated.

Validation instruction for this tranche:
- Use a merits-oriented re-read focused on three points: what was requested, which public entity controlled the process, and whether the court’s failure language is really jurisdictional or instead reflects a missing translation of administratively observable facts into FHA elements.

### Tranche 4: Standard translation follow-up with lower marginal payoff
Risk type: mostly underclaiming, but lower urgency
Count: 66 records
Composition: 54 in high-review only, 9 in both queues, 3 in low-confidence only
Why this tranche matters less right now:
- These rows are still worth checking, but many already look directionally stable.
- They mostly concern familiar pleading failures: request not alleged, disability nexus missing, adverse action not connected, or jurisdiction/standing issues with reasonably legible fact patterns.
- They are less likely than tranches 1-3 to materially distort the core draft if deferred one round.

Examples:
- `9880628_2022_Jones v. City of New York_nysd`
- `10195301_2024_MacNeal v. The State of New York_nysd`
- `9833369_2023_Brown v. American Homes 4 Rent_nvd`
- `10632353_2025_Waheed v. Ballon Stoll Bader and Nadler PC_nysd`

## Highest-value next validation pass
I recommend a two-step next pass rather than a broad sweep.

### Pass 1: 12-record manual/model validation set
Purpose: minimize overclaiming first, while also clearing the most analytically consequential category-fit conflicts.

Validate these 12 records first:
1. `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd`
2. `10219016_2022_Shepherd v. Cornerstone Residential_utd`
3. `10193953_2024_Avila v. ACACIA Network, Inc._nysd`
4. `9913834_2022_Chapman v. Franklin County Sheriff_ohsd`
5. `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord`
6. `9885949_2023_Rosa v. Pathstone Corporation_nysd`
7. `10803192_2026_Jermaine Capel v. Norfolk Redevelopment _ Housing Authority_ca4`
8. `10609257_2025_McLain v. Sedgwick County Sheriff's Office_ksd`
9. `9939426_2023_WISSMAN v. PGM REAL ESTATE LLC, PROPERTY MANAGEMENT_paed`
10. `9589809_2023_Goodwin v. City Attorney's Office_caed`
11. `10631726_2025_Ballentine v. Cares for the Homeless_nysd`
12. `9873146_2022_Sykes v. New York City Housing Authority_nysd`

Why this set:
- It covers the most dangerous overclaiming cases.
- It also tests whether the public-process bucket is currently too noisy or too narrow.
- It has a high share of low-confidence/high-review overlap, which maximizes expected gain per checked row.

### Pass 2: public-process expansion set
After Pass 1, validate the rest of Tranche 3 before returning to the broader translation backlog.

Recommended follow-ons:
- `9695934_2022_Johnson v. South Bend Housing Authority_innd`
- `9680054_2022_Jackson v. Chicago Housing Authority_ilnd`
- `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4`
- `9741403_2023_Cooper v. Mr. Timmins_mdd`
- `9590670_2023_(PS) Peters v. Ervin_caed`
- `10762570_2025_Shirley Drummer v. Southern Nevada Regional Housing Authority, et al._nvd`

## Practical checking rules
For the next pass, each checked row should answer these questions in order:
1. Did the court actually adjudicate an FHA issue, or is the order only procedural?
2. Is the current statute/theory mapping correct?
3. If the ruling is adverse, what exactly failed: request articulation, disability nexus, defendant selection, jurisdiction, or some other element?
4. Does the opinion contain administratively observable facts that the current coding underuses?
5. Should the row remain in analytic counts, be recoded, or be held out as context only?

## Net assessment for the draft
- Main overclaiming threat: early-stage `UNCLEAR` records being read as evidence of substantive pleading failure.
- Main underclaiming threat: public-process cases where the current coding stops at jurisdiction or thin translation language and misses a richer administrative-failure pattern.
- Best immediate use of validation time: the 12-record Pass 1 list above.

## File note
This memo is based on queue-level and resolved-results review, not fresh line-by-line re-reading of every underlying opinion. It is therefore designed to prioritize the next validation pass, not to substitute for it.
