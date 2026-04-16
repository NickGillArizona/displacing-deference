# Disability wave noisy queue cleanup memo

## Scope
Targeted cleanup pass on the highest-priority noisy early-procedural/non-merits Tranche 1 records flagged in the validation priority memo, with emphasis on:

- `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord`
- `9885949_2023_Rosa v. Pathstone Corporation_nysd`
- `9913834_2022_Chapman v. Franklin County Sheriff_ohsd`

I also checked three similarly situated early-procedural rows that could be resolved quickly from the queue:

- `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd`
- `10219016_2022_Shepherd v. Cornerstone Residential_utd`
- `10193953_2024_Avila v. ACACIA Network, Inc._nysd`

Sources reviewed:

- `results/disability_wave_validation_priority_memo.md`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`
- underlying opinion texts in `allFHAcases/`

## Bottom line
These six rows are all early procedural records and should be held out from substantive analytics. None should presently be retained as meaningful doctrinal or merits support. At most, they can be kept as context-only records documenting pipeline noise, pro se case posture, or the existence of an asserted FHA claim.

In short:

- Hold out from substantive analytics: 6
- Keep only as context: 6
- Retain as meaningful support: 0

## Record-by-record cleanup decisions

| Source file | Opinion posture | What the opinion actually does | Cleanup recommendation | Why |
|---|---|---|---|---|
| `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord` | counsel-denial order | Denies motion for appointment of counsel with leave to renew; no claim adjudication | Hold out from substantive analytics; keep only as context | The order expressly says the case is at an early stage and only evaluates exceptional-circumstances counsel factors. It does not resolve any FHA element, pleading defect, or merits issue. |
| `9885949_2023_Rosa v. Pathstone Corporation_nysd` | service order | Directs issuance of summonses and Marshals service in IFP case; no merits review | Hold out from substantive analytics; keep only as context | This is pure service administration. The court notes plaintiff brings FHA and § 1983 claims regarding Section 8 voucher termination, but it does not test plausibility or decide any FHA issue. |
| `9913834_2022_Chapman v. Franklin County Sheriff_ohsd` | partial screening/recommit order | Dismisses some parties, but recommits for further screening of claims against sheriff; no final FHA merits ruling | Hold out from substantive analytics; keep only as context | The court specifically says the complaint may or may not state claims and sends the matter back for claim-by-claim screening. That is too preliminary to count as substantive support for pleading failure or merits disposition. |
| `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd` | counsel-denial order | Denies appointed counsel; notes complaint alleges FHA and other claims but does not adjudicate them | Hold out from substantive analytics; keep only as context | The order contains some descriptive allegations about repairs, water shutoff, and attempted eviction, but those facts are not judicial findings and are not tied to any FHA merits holding. |
| `10219016_2022_Shepherd v. Cornerstone Residential_utd` | counsel-denial order | Denies renewed motions for counsel without prejudice; notes complaint already survived IFP screening | Hold out from substantive analytics; keep only as context | The only substantive signal is that the complaint survived initial screening, which is not an FHA merits decision and does not establish a useful pleading-failure diagnosis. |
| `10193953_2024_Avila v. ACACIA Network, Inc._nysd` | service order | Orders service in pro se FHA/ADA/state-law action | Hold out from substantive analytics; keep only as context | Like Rosa, this is an administrative service order only. It confirms the asserted theories but supplies no analytic basis for coding a substantive FHA failure or success. |

## Specific notes on the three named priority rows

### 1. `10671080_2025_Jacobson v. AH Gresham Park, LLC_ord`
Disposition: hold out from substantive analytics; retain only as context.

Why:
- The opinion is solely about appointment of pro bono counsel.
- The court says plaintiff has not yet shown likelihood of success and that the case is still at an early stage.
- References to ADA/FHA claims appear only to describe the case background and plaintiff's ability to litigate pro se.

Analytic use:
- Acceptable as context that a pro se litigant asserted FHA-related claims against housing defendants.
- Not acceptable as support for any pleading-failure mechanism, no-failure merits outcome, or doctrinal proposition.

### 2. `9885949_2023_Rosa v. Pathstone Corporation_nysd`
Disposition: hold out from substantive analytics; retain only as context.

Why:
- The order does nothing except facilitate service by the Marshals Service after IFP status.
- The court recites that plaintiff alleges FHA and § 1983 violations arising from voucher termination, but there is no screening analysis beyond service logistics.
- Because the case sits in public-program/Section 8 space, it may still be useful to remember as a context record, but not as substantive support.

Analytic use:
- Acceptable as a contextual indicator of an asserted Section 8/FHA grievance in a public-process setting.
- Not acceptable for substantive counts or citations about translation failure, denial, refusal, nexus, or dismissal grounds.

### 3. `9913834_2022_Chapman v. Franklin County Sheriff_ohsd`
Disposition: hold out from substantive analytics; retain only as context.

Why:
- This is somewhat less empty than a service order, but still not a merits adjudication.
- The district judge adopts an R&R only in part, dismisses certain parties, and recommits the matter for further screening of the sheriff claims.
- The order expressly says the court doubts the complaint states claims and wants clearer screening as to which claims survive. That language signals unresolved screening, not a final diagnosis of the FHA claim.

Analytic use:
- Acceptable only as context for noisy early screening-stage litigation involving an asserted FHA claim against a government defendant.
- Not acceptable as evidence of a completed pleading failure or a meaningful public-process merits ruling.

## Quick resolutions for similarly situated rows

### `10243934_2023_Sandles v. Secretary of Veterans Affairs_wawd`
Disposition: hold out from substantive analytics; retain only as context.

Reason:
- The order is limited to denial of appointed counsel.
- It summarizes allegations involving repairs, water shutoff, and attempted eviction, but the court does not resolve jurisdiction, statutory fit, or the FHA claim itself.
- Because the defendant is a federal official and the opinion itself flags related jurisdiction/removal problems, this row is especially unsafe for substantive use.

### `10219016_2022_Shepherd v. Cornerstone Residential_utd`
Disposition: hold out from substantive analytics; retain only as context.

Reason:
- The court denies motions for counsel and notes only that the complaint survived screening.
- Surviving IFP screening is not a developed merits signal and should not be treated as a plaintiff win or a stable no-failure coding.
- This row can remain in the dataset only as background context that an FHA case proceeded past initial screening.

### `10193953_2024_Avila v. ACACIA Network, Inc._nysd`
Disposition: hold out from substantive analytics; retain only as context.

Reason:
- Another pure order-of-service opinion.
- The opinion identifies FHA, ADA, and retaliation theories but contains no adjudication.
- It is too preliminary to support either substantive failure coding or a doctrinal/public-process proposition.

## Cleanup rule emerging from this pass
A narrow queue rule appears justified for this cluster of cases:

If the opinion is only an order of service, Marshals-service directive, or denial of appointed counsel, and it does not adjudicate an FHA issue, then it should be excluded from substantive analytics and preserved only as context metadata.

The same default should apply to incomplete screening/recommit orders unless the order actually resolves the FHA claim in a way that can be coded with confidence.

## Recommended dataset treatment
For these six rows:

1. Remove from any denominator or supporting set used to make substantive claims about FHA pleading failure, merits outcomes, or doctrinal patterns.
2. Preserve in a context-only bucket for tracking pro se pipeline noise and early procedural posture.
3. Do not cite these opinions in draft text as support for accommodation-request failure, nexus failure, refusal, jurisdictional failure, or public-process failure on the merits.
4. If a later merits or screening opinion exists in the same case, prefer the later opinion for analytic coding.

## Net result of this cleanup pass
This pass confirms that the targeted noisy Tranche 1 records reviewed here are genuine analytic-noise risks rather than hidden substantive support. The proper cleanup move is conservative exclusion from substantive analysis, not recoding them into a more specific failure family.
