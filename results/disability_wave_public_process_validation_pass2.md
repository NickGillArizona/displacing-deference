# Disability wave public-process validation pass 2

I completed the second public-process validation pass identified in the priority memo for these six records:

- `9695934_2022_Johnson v. South Bend Housing Authority_innd`
- `9680054_2022_Jackson v. Chicago Housing Authority_ilnd`
- `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4`
- `9741403_2023_Cooper v. Mr. Timmins_mdd`
- `9590670_2023_(PS) Peters v. Ervin_caed`
- `10762570_2025_Shirley Drummer v. Southern Nevada Regional Housing Authority, et al._nvd`

Method: I checked the resolved-results classification against the underlying opinion text in `allFHAcases`. Where the appellate opinion was too thin, I used the available district-court opinion for the same dispute when present.

## Bottom line

This pass confirms that the expansion set is mixed. Two records are genuinely useful public-process cases (`Jackson`, `Drummer`), one is a good public-process case but needs mechanism recoding (`Fedynich`), one is a real FHA/public-housing case but currently miscoded on the failure mechanism (`Cooper`), and two are weak for the disability-centered public-process story (`Johnson`, `Peters`).

Most important correction: the weak cases are weak for different reasons. `Johnson` is a public-housing repair/jurisdiction case with no real disability or protected-class pleading; `Peters` looks like a general grievance/custody/eviction case with only a conclusory FHA label and should probably be removed from analytic public-process counts altogether.

## Case-by-case validation

### 1. `9695934_2022_Johnson v. South Bend Housing Authority_innd`
Current model classification:
- `PROCEDURAL_GATEWAY / JURISDICTION_OR_STANDING`
- public-process flag: `true`

What the opinion actually says:
- The court dismissed for lack of subject matter jurisdiction.
- Johnson alleged mold, insufficient heat, and generally unsafe conditions in public housing, and asked for repairs or “fair & equal housing relocation assistance.”
- But the court stressed that she did not allege discrimination on a protected FHA ground, did not clearly invoke the FHA, and did not establish diversity jurisdiction.
- The court also found amendment futile because it could not discern facts supporting a federal claim.

Validation assessment:
- Merits of current family: mostly right.
- Public-process value: weak.

Why:
- This is indeed a public-housing dispute, and the dismissal is jurisdiction/pleading driven rather than merits-driven.
- But it is not a strong disability/public-process case. The opinion reads more like an untransformed housing-conditions grievance than a disability accommodation or public-administration breakdown with a clearly pleaded FHA nexus.
- The model’s public-process framing is usable only in a very limited sense: a tenant sought institutional relief from a housing authority and failed to translate a repair/relocation grievance into an FHA claim.

Recommendation:
- Keep the general `PROCEDURAL_GATEWAY` result.
- Do not use this as a lead disability-centered public-process example.
- Treat as weak support or context-only for the public-process story unless the project separately wants public-housing false starts that never became cognizable discrimination claims.

Confidence in validation: high.

### 2. `9680054_2022_Jackson v. Chicago Housing Authority_ilnd`
Current model classification:
- `CAUSAL_LINK / ELEMENTS_NOT_TIED_TO_FACTS`
- public-process flag: `true`

What the opinion actually says:
- Jackson was in the CHA Housing Choice Voucher Program.
- He alleged that Lake Street Studios denied him equal access to services, including laundry access and disabled parking, and retaliated after he reported conditions.
- The court held that the alleged ADA/FHA harms were directed at Lake Street Studios and its employees, not CHA.
- The opinion affirmatively states that CHA employees helped him transfer housing.
- The CHA defendants were dismissed because Jackson did not allege personal involvement, and he also failed to plead any CHA policy or practice for official-capacity liability.

Validation assessment:
- Strong public-process record.
- Classification is substantially right, though the most precise gloss is “wrong defendant / no factual tie to CHA,” not generic causation in the abstract.

Why:
- This is a good institutional-triage case in a voucher context.
- The public-process story is not that no grievance existed. It is that the grievance was directed at the landlord-side actor while the plaintiff sued the public intermediary that had actually assisted him.
- That makes it analytically useful for the memo’s “proper-defendant confusion” point.

Recommendation:
- Keep in analytic counts.
- Keep public-process flag.
- If recoding is allowed, refine the mechanism note toward wrong-defendant or defendant-attribution failure. If not, current `ELEMENTS_NOT_TIED_TO_FACTS` is still acceptable.

Confidence in validation: high.

### 3. `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4`
Current model classification:
- `TRANSLATION / REQUEST_NOT_ALLEGED`
- public-process flag: `true`

What the opinion actually says:
- The Fourth Circuit affirmance is very thin, but the underlying E.D. Va. opinion is informative.
- Plaintiffs alleged multiple concrete requests in the Section 8/HCV process: expedited inspection, voucher extension, higher payment standard, and repeated extension requests tied to disability-related housing needs.
- They also alleged physician letters and repeated failures to engage in an interactive process across several public housing intermediaries.
- The district court dismissed because plaintiffs did not plausibly allege a qualifying disability and did not establish a plausible nexus between their disabilities, the requested accommodations, and the alleged discrimination.
- The court explicitly said the requests existed but were too weakly connected to a defined disability theory.

Validation assessment:
- Strong public-process case.
- Current mechanism needs recoding.

Why:
- `REQUEST_NOT_ALLEGED` is not the best reading. The requests were alleged repeatedly.
- The real failure is disability-definition/nexus translation: plaintiffs labeled themselves disabled, attached provider material, and described repeated accommodation requests, but did not plausibly connect the specific disabilities to the requested modifications in a legally sufficient way.
- This is exactly the sort of public-process underclaiming case the memo flagged.

Recommendation:
- Keep in analytic counts.
- Keep public-process flag.
- Recode away from `REQUEST_NOT_ALLEGED` toward a nexus-based translation failure, likely `ELEMENTS_NOT_TIED_TO_FACTS` or a disability-nexus variant if available in the schema.

Confidence in validation: high.

### 4. `9741403_2023_Cooper v. Mr. Timmins_mdd`
Current model classification:
- `TRANSLATION / REQUEST_NOT_ALLEGED`
- public-process flag: `true`

What the opinion actually says:
- The 2023 opinion in `recentcases` is a reconsideration denial, but the available 2022 district-court dismissal opinion provides the underlying reasoning.
- Cooper brought an FHA retaliation case against individual Housing Authority of Baltimore City employees.
- The court held that she failed to state a retaliation claim because the complaint did not plausibly allege that these defendants knew of her 2015 protected activity and did not plausibly allege causation, especially given the four-year gap between the 2015 lawsuit and the alleged retaliation beginning in 2019.
- She later tried to shift the suit toward HABC itself, but the court denied amendment as futile because causation still was not plausibly alleged.

Validation assessment:
- Public-process relevance: moderate but real.
- Current mechanism is wrong and should be recoded.

Why:
- This is not a request-articulation case.
- It is an FHA retaliation case that fails on knowledge and causal connection, with some additional wrong-defendant drift because she sued individual employees and then tried to reframe the case against HABC.
- For the public-process story, it is usable only if the project wants retaliation and institutional-defendant targeting failures; it is weaker than `Jackson` or `Fedynich` for accommodation-process analysis.

Recommendation:
- Keep as a public-housing/FHA case, but not as a request-translation exemplar.
- Recode from `REQUEST_NOT_ALLEGED` to a causation-based mechanism.
- Use cautiously in the public-process section, mainly for institutional targeting/retaliation pleading problems.

Confidence in validation: high once the underlying 2022 opinion is used; lower if one looked only at the thin 2023 reconsideration order.

### 5. `9590670_2023_(PS) Peters v. Ervin_caed`
Current model classification:
- `TRANSLATION / COMPARATOR_OR_INTENT_GAP`
- public-process flag: `true`

What the opinion actually says:
- This is a screening order against a sprawling complaint naming judges, clerks, sheriffs, social workers, public defenders, behavioral health workers, and other county officials.
- The core factual narrative concerns custody proceedings, loss of children, an untimely appeal, homelessness, county-program denials, and an eviction.
- The FHA allegation is expressly described by the court as conclusory and unsupported by facts from which the court could infer an FHA cause of action.
- The court said plaintiff did not allege that defendants refused to rent housing for discriminatory reasons.

Validation assessment:
- Weak public-process case.
- Likely needs recoding out of the FHA/public-process lane.

Why:
- This does not read like a housing-authority or public-housing administrative-process case at all.
- It is better understood as a general grievance action with an unsupported FHA label attached.
- The current classification understates the category-fit problem. The key issue is not comparator proof or discriminatory-intent detail within an otherwise recognizable FHA case; the key issue is that the FHA hook itself is barely present.

Recommendation:
- Recode toward `NO_COGNIZABLE_FHA_THEORY` or otherwise mark as effectively non-analytic for FHA public-process counting.
- Remove from any core public-process narrative.
- At most, retain as a false-positive example in a theory-mapping cleanup file.

Confidence in validation: high.

### 6. `10762570_2025_Shirley Drummer v. Southern Nevada Regional Housing Authority, et al._nvd`
Current model classification:
- `TRANSLATION / ELEMENTS_NOT_TIED_TO_FACTS`
- public-process flag: `true`

What the opinion actually says:
- This is a screened fifth amended complaint after repeated amendment opportunities.
- Plaintiff alleged primary progressive multiple sclerosis, anxiety, depression, cognitive issues, provider documentation, a request for a live-in aide and extra bedroom for medical supplies, repeated HUD complaints, and discriminatory or retaliatory conduct by Southern Nevada Regional Housing Authority personnel.
- The court’s overriding concern was Rule 8: the complaint lumped defendants together and failed to specify which defendants committed which acts under which cause of action.
- Related screening material in the same case also shows a voucher bifurcation/termination dispute, hearing issues, a request for the housing file, and a physician-supported accommodation request to waive file-copy costs.

Validation assessment:
- Strong public-process case.
- Current classification is broadly right.

Why:
- This is exactly the kind of institutional process case the memo was worried about: there are medical records, accommodation requests, hearing/file/grievance facts, and a housing-authority administrative setting, but the complaint repeatedly fails to organize those facts into defendant-specific legal claims.
- The result is not a false-positive public-process label; it is a real public-process case whose pleadings remain structurally unusable.

Recommendation:
- Keep in analytic counts.
- Keep current family/mechanism unless a more precise Rule-8/defendant-attribution subcode exists.
- This is a strong example for the public-process story because the administrative record appears rich while the complaint remains legally disorganized.

Confidence in validation: high.

## Overall recommendations for this expansion set

### Strong public-process cases to keep
- `9680054_2022_Jackson v. Chicago Housing Authority_ilnd`
- `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4` (but recode mechanism)
- `10762570_2025_Shirley Drummer v. Southern Nevada Regional Housing Authority, et al._nvd`

### Moderate/usable with caution
- `9741403_2023_Cooper v. Mr. Timmins_mdd` (real FHA/public-housing case, but mechanism is causation/knowledge, not request articulation)

### Weak or should be held out from the core public-process story
- `9695934_2022_Johnson v. South Bend Housing Authority_innd`
- `9590670_2023_(PS) Peters v. Ervin_caed`

## Recommended recodes

1. `9374094_2023_Elizabeth Fedynich v. Boulder Housing Partners_ca4`
   - From: `TRANSLATION / REQUEST_NOT_ALLEGED`
   - To: translation/nexus failure (`ELEMENTS_NOT_TIED_TO_FACTS` or nearest disability-nexus equivalent)

2. `9741403_2023_Cooper v. Mr. Timmins_mdd`
   - From: `TRANSLATION / REQUEST_NOT_ALLEGED`
   - To: causation-based retaliation failure

3. `9590670_2023_(PS) Peters v. Ervin_caed`
   - From: `TRANSLATION / COMPARATOR_OR_INTENT_GAP`
   - To: `NO_COGNIZABLE_FHA_THEORY` or other non-FHA / false-positive cleanup code

4. `9695934_2022_Johnson v. South Bend Housing Authority_innd`
   - Formal family may stay `PROCEDURAL_GATEWAY`, but analytic status should be downgraded for disability-centered public-process use.

## Net assessment for the draft

This pass supports the memo’s core warning that the public-process bucket contains both high-value undercounted cases and noisy false positives.

The best support here comes from `Jackson`, `Fedynich`, and `Drummer`, because each involves an identifiable public housing intermediary and a tangible administrative process failure: wrong-defendant targeting, disability-nexus translation failure despite actual requests, or defendant-specific pleading breakdown despite a rich administrative record.

The clearest cases to avoid overclaiming from are `Johnson` and especially `Peters`, which do not carry much weight for a disability-centered public-process account.
