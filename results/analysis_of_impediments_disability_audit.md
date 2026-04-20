# AI-era disability-treatment audit memo

Date: 2026-04-16
Prepared for: Prompt 49 (Historical Analysis of Impediments disability audit)
Primary artifact: `results/analysis_of_impediments_disability_audit.md`
Support artifacts: `results/ai_audit_coding.csv`, `results/ai_afh_matched_examples.json`, `results/ai_audit_sample_ledger.md`, and downloaded PDFs/texts in `results/ai_audit_docs/`

## Bottom line

This memo's main contributions are:
- one high-confidence pre-2006 AI (`Oregon non-entitlement areas`, 2005) in the recovered sample;
- one more same-jurisdiction AI-to-AFH pair (`Winston-Salem/Forsyth County`, 2009-2013 AI -> later AFH);
- topline counts aligned with the support CSV;
- a final claim framed as structural disability under-operationalization rather than literal disability silence; and
- a concise auditability ledger for the preserved denominator and surfaced-but-not-counted candidates.

The recovered denominator in this memo contains 17 public-PDF AI documents. Sixteen are dated 2005-2015, and the seventeenth is New Haven's 2010 update to a 1996-origin AI. Four jurisdictions in the recovered sample later appear in the 47-AFH corpus: Dallas, Burlington, Washtenaw, and Winston-Salem/Forsyth County.

Headline coding results for the recovered 17-document public-PDF sample:
- Disability section present: 17 of 17
- Quantitative disability data: 17 of 17
- Disability-specific impediments identified: 16 of 17
- Disability-specific actions proposed: 14 of 17
- Race analysis deeper than disability analysis under the structural rubric below: 13 of 17

This recovered sample does not support a claim that the reviewed AI documents literally ignored disability. In the recovered sample, disability was almost always present and almost always quantified. But the sample does support a narrower claim: disability was usually handled through an accessibility / special-needs / reasonable-accommodation lane, while race and ethnicity more often supplied the document's segregation, lending, and opportunity architecture. The memo also draws a second, separate point about inventories / verification / monitoring. That point is a qualitative synthesis from row notes and examples, not a sixth binary count: even the stronger disability AIs in this recovered sample rarely showed durable accessible-unit inventories, verified Section 504-style needs-assessment machinery, or monitoring systems capable of checking whether accessible units and integrated-placement obligations were actually being met.

## Scope and evidentiary framing

1. Direct counted coverage includes a high-confidence pre-2006 AI.
   - `Oregon non-entitlement areas` (2005) is an official, publicly archived state AI.
   - It moves the direct recovered denominator back from 2006 to 2005.

2. The matched same-jurisdiction set includes one more direct AI-to-AFH comparison.
   - `Winston-Salem/Forsyth County` now joins Dallas, Burlington, and Washtenaw as a direct AI-to-AFH pair.

3. The denominator follows a strict evidentiary rule.
   - I counted only original AI documents or formal AI updates that I could directly recover as public PDFs/texts.
   - I did not count derivative references inside later AFHs or secondary summaries as separate AIs.
   - I do use such derivative material as corroboration when it helps explain the historical arc, but not in the denominator.

4. The backward-extension claim is intentionally bounded.
   - The recovered document-date range is 2005-2015 plus one 2010 update to a 1996-origin AI, not the full 1996-2015 universe.
   - New Haven still matters as a 2010 update to an AI originally prepared in 1996.
   - Oregon's 2005 AI also reproduces appendix summaries of older local AIs from 1996 and 2004; I treat those as corroborating evidence, not additional counted observations.

5. A concise auditability aid accompanies the memo.
   - `results/ai_audit_sample_ledger.md` crosswalks each counted row to its local text extract and logs the main surfaced-but-not-counted candidates/exclusions in `results/ai_audit_docs/`.
   - That ledger makes the preserved 17-document denominator easier to audit and separates it clearly from the broader exploratory search folder.

## Method and coding rules

I grounded the audit in repo materials first, especially:
- `research_outputs/T_afh_extension.md` for the completed 47-AFH topline counts.
- `research/afh_content_analysis/afh_coding.csv` for matched-jurisdiction AFH examples.
- `note_v89_B.md`, `v89_RESEARCH_MEMO_COMPLETE.md`, and `FUTURE_RESEARCH_DESIGN.md` for the note's refined claim that the real problem is thin operationalization, not total silence.

The denominator is intentionally limited to the recovered sample already coded in `results/ai_audit_coding.csv`. A document entered the denominator only if all three conditions were met: (1) I directly recovered the AI itself, or a formal AI update, as a public PDF/text; (2) enough text survived to let me code all five binary fields below; and (3) I entered a row in `results/ai_audit_coding.csv`. Other locally saved search hits, board packets, presentations, or degraded fragments are not included in the denominator. A short inclusion/exclusion ledger lives at `results/ai_audit_sample_ledger.md`.

For the AI audit, I searched for public AI PDFs, prioritized official city/county/state PDFs when available, and used archived PDFs when I could not get an official download. For each counted AI, I searched for disability/disabled/handicap/accessible/accessibility and coded five binary fields requested by Prompt 49:
1. disability section present?
2. quantitative disability data?
3. disability-specific impediments identified?
4. disability-specific actions proposed?
5. race analysis deeper than disability analysis?

### How the `race analysis deeper than disability` field was coded

This fifth field was a structured comparative judgment, not a word-count rule. I compared the race/ethnicity module and the disability module within the same document.

I coded `Y` when race/ethnicity received a clearly broader planning architecture than disability, ordinarily shown by at least two of the following:
- a distinct race/ethnicity-only analytic module that disability lacked, such as segregation/concentration analysis, HMDA lending analysis, racially concentrated poverty analysis, or broader opportunity / neighborhood-inequality mapping;
- materially more tables, maps, or narrative analysis tied to race/ethnicity than to disability; and
- findings or action framing that treated race/ethnicity as a document-wide organizing axis while disability remained mainly in a narrower accessibility / reasonable-accommodation / special-needs / group-home / transit lane.

I coded `N` when disability analysis was roughly coequal inside the document: typically a dedicated disability section with quantitative data, named impediments, and linked actions, and no clearly broader race-only architecture that made race materially deeper overall. Borderline cases were resolved conservatively toward `N`, which is why Burlington, New Haven, Spokane, and Washtenaw are the four `N` rows.

I did **not** use simple keyword counts as the coding rule. The helper files in `results/ai_audit_docs/ai_keyword_support.json` and `ai_precode_support.json` were retrieval aids. Final `Y/N` calls came from table-of-contents structure, substantive section review, and the row notes preserved in `results/ai_audit_coding.csv`.

Coding was intentionally conservative.
- When a document clearly discussed disability but I could not verify a distinct disability-tagged forward action step, I coded the action field `N` rather than inferring from a general fair-housing action plan.
- When an older item surfaced only through a degraded scan or a derivative reference inside another document, I did not promote it into the counted sample.
- The memo's later discussion of inventories, verification, and monitoring is **not** a sixth binary field. It is a qualitative synthesis from the row notes and example passages.

Important scope note: the recovered public-PDF sample likely overrepresents higher-capacity jurisdictions that preserved planning documents online. That means this audit probably biases upward, not downward, the apparent quality of disability treatment in the reviewed AI documents.

## AI-by-AI coding table

| Jurisdiction | AI year | Public source | Later AFH in 47 corpus? | Disability section | Quant disability data | Disability-specific impediments | Disability-specific actions | Race deeper than disability? | Notes |
|---|---:|---|---|---|---|---|---|---|---|
| Boston MA | 2010 | official city PDF | N | Y | Y | Y | N | Y | Dedicated `Housing for People with Disabilities` section; tables on disability and MassAccess registry counts; disability impediments explicit; action steps not clearly disability-tagged in extract. |
| Burlington VT | 2010 | official city PDF | Y | Y | Y | Y | Y | N | One of the stronger AIs: Impediment 4 is limited supply of housing features needed by people with disabilities, with action items including universal-design incentives. |
| Clark County WA | 2012 | official county PDF | N | Y | Y | Y | Y | Y | Includes disability demographics, zoning-definition impediment, transit barrier for disabled residents, universal-design recommendation, and action plan item on transit needs. |
| Dallas TX | 2015 | official city PDF | Y | Y | Y | Y | Y | Y | Stronger disability AI; accessible-housing impediment and explicit action items, but race/ethnicity and spatial analysis still dominate. |
| Durham NC | 2015 | archived city PDF | N | Y | Y | Y | Y | Y | Impediment 6 is accessible housing; includes goal and action items to expand accessible affordable units and accessibility compliance. |
| Los Angeles CA | 2006 | official city PDF (city clerk archive) | N | Y | Y | Y | Y | Y | Official Los Angeles AI dated January 2006; identifies barriers for people with mental disabilities and responds with Reasonable Accommodation Ordinance action steps. |
| Louisiana non-entitlement areas | 2010 | official state PDF | N | Y | Y | Y | Y | Y | Uses disability-by-age and concentration data; discusses accessibility failures and includes statewide actions on reasonable accommodation and testing of new rentals. |
| New Haven CT | 2010 | archived city PDF | N | Y | Y | Y | Y | N | One of the strongest disability treatments: dedicated disability-community section, explicit accessible-unit and outreach impediments, and linked action items. |
| Oregon non-entitlement areas | 2005 | official state archive PDF | N | Y | Y | Y | Y | Y | Official Oregon state AI for non-entitlement areas. Uses 2000 Census disability rates and complaint data; identifies persons with disabilities as especially vulnerable to discrimination; flags companion-animal and land-use barriers; recommends regulatory clarification, more testing, and fair-housing training. |
| Phoenix AZ | 2015 | official city PDF | N | Y | Y | Y | Y | Y | Identifies accessibility barriers in older stock and recommends funding accessibility retrofits, training, and compliance efforts. |
| Prince George's County/Bowie MD | 2011-2012 | official county PDF | N | Y | Y | Y | Y | Y | Contains explicit action-plan goals to expand accessible housing and update Section 504/accessibility needs assessments. |
| San Antonio TX | 2010 | official city PDF | N | Y | Y | N | N | Y | Contains disability/accessibility law discussion and handicap-accessible waiting-list tables, but I did not confirm clearly disability-tagged impediments or action items. |
| San Diego Regional AI | 2011 | official regional PDF | N | Y | Y | Y | Y | Y | Repeatedly identifies housing-for-disability impediments across prior AI cycles and proposes accessibility strategies; still heavily race/segregation and HMDA driven. |
| Snohomish County WA | 2012 | official county PDF | N | Y | Y | Y | Y | Y | Strong disability data and survey material; explicit complaint, transit, zoning, and accessibility impediments plus recommendation to address housing needs of persons with disabilities. |
| Spokane WA | 2008 | official city PDF | N | Y | Y | Y | Y | N | Strong disability treatment: disability complaints exceed any other protected class; identifies accessibility/design-construction impediments and recommends centralized applicant and accessible-unit strategies. |
| Washtenaw Urban County MI | 2011 | official county PDF | Y | Y | Y | Y | Y | N | Another relatively strong disability AI; numerous accessibility and zoning recommendations, including building-code changes and supportive-housing ordinance work. |
| Winston-Salem/Forsyth County NC | 2009-2013 | official city archive PDF | Y | Y | Y | Y | N | Y | Short internally produced AI/action plan. Contains a distinct Handicap section with 1999 complaint-share data and detailed accessibility-design noncompliance rates; identifies shortage of accessible units, persistent design-and-construction noncompliance, and landlord stereotyping of disabled tenants. Final action items are mostly general rather than clearly disability-tagged. |

## Main findings from the AI sample

### 1. Disability was usually present and quantified, but usually as diagnosis rather than infrastructure

Every counted AI in the recovered sample had a disability section or distinct disability/accessibility component. Every counted AI also included quantitative disability material of some kind: disability prevalence, complaint shares, accessibility noncompliance rates, waiting-list counts, or accessible-unit counts.

Examples:
- Boston used MassAccess counts and disability tables.
- Dallas reviewed affordable accessible housing inventory and paired it with explicit disability actions.
- Oregon's 2005 state AI used statewide disability rates and complaint patterns, and identified companion-animal and land-use barriers affecting disabled renters.
- Winston-Salem's 2009-2013 AI reported a 33% handicap complaint share and detailed design-and-construction noncompliance rates.

But in most documents in the recovered sample, disability analysis remained framed around accessibility shortfalls, special-needs housing, companion animals, or reasonable-accommodation issues. It rarely became a continuing data system that would let the jurisdiction verify where accessible units were, whether they were occupied by households needing them, or whether integrated-setting obligations were actually being met.

### 2. Race still supplied the dominant planning architecture in most documents in the recovered sample

In 13 of 17 recovered AIs, race analysis was deeper than disability analysis under the rubric above. The difference usually showed up in three places:
- detailed racial/ethnic demographic and segregation chapters;
- HMDA lending analysis by race/ethnicity; and
- broader opportunity, concentration, or neighborhood-inequality analysis centered on race and ethnicity.

Disability, by contrast, was usually routed into one of four narrower lanes:
- accessible housing supply;
- group homes / supportive housing / special-needs housing;
- reasonable accommodation and modification rules; and
- public-infrastructure accessibility or transit barriers.

Within this recovered sample, disability treatment was not negligible; it was usually thinner in structure and in the types of analytic tools deployed.

### 3. Qualitative synthesis from row notes: even the stronger AIs rarely showed durable feature-verification systems

This subsection is not a sixth frequency count. The five coded binary fields do **not** directly code inventories, registries, needs-assessment systems, or monitoring machinery. The conclusion here is a qualitative synthesis from the row notes and example passages.

A few AIs were notably stronger than the rest:
- New Haven (2010 update to a 1996 AI) had a dedicated disability-community section and explicit accessible-unit and outreach impediments.
- Prince George's County/Bowie (2011-2012) had disability-specific action-plan goals and accessibility-assessment tasks.
- Dallas (2015) had one of the clearest disability impediment/action structures.
- Washtenaw (2011), Spokane (2008), Burlington (2010), and Oregon (2005) all contained serious disability or accessibility recommendations.

But even these stronger documents in the recovered sample usually stopped short of a standing compliance architecture. Boston's reliance on MassAccess remains the clearest counted exception. Prince George's County's Section 504 needs-assessment language points in the same direction. New Haven recommended drafting a list of accessible housing, and Spokane recommended conducting an inventory of accessible units — recommendations that themselves underscore the absence of a settled system. Dallas reviewed inventory and need, but not as a clearly durable registry/monitoring apparatus. So the modal AI response was still education, outreach, training, code review, complaint response, or generalized accessible-housing encouragement, rather than a standing registry, verified inventory, or monitoring system.

### 4. Direct coverage reaches only modestly backward in time

The recovered sample reaches back to 2005 through Oregon's official statewide AI. That matters because Oregon's 2005 document already shows, within a directly reviewable pre-2006 case, the pattern this memo is describing:
- disability is visible;
- disability complaint data are real;
- disability-specific barriers are named; and
- the wider planning architecture still runs more through race, lending, land use, and general affordability.

Oregon's 2005 AI also includes Appendix B summaries of older local fair-housing plans and AIs, including:
- Multnomah County / Portland / Gresham / urban Multnomah County (1996), which included recommendations tied to transportation access and homeownership support for people with disabilities; and
- Washington County / Beaverton / Hillsboro (2004), which included recommendations to require ADA compliance in publicly supported housing and to protect voucher holders who need accessible features.

I do not count those appendix summaries as separate recovered AIs. They are corroborative only. At most, they suggest that similar planning architecture may have been present in some older materials; they do not justify enlarging the denominator or making a census claim about the whole pre-2005 AI era.

I also surfaced a Delaware state AI dated 2003. The public OCR remains too incomplete for confident full coding, so I do not promote it into the counted denominator. The recoverable text is nonetheless sufficient for a narrower corroborative use: the front matter clearly identifies a `Delaware Analysis of Impediments to Fair Housing Choice` prepared for the Delaware State Housing Authority in `July 2003`, and the table of exhibits includes `Percent Disabled by Age Group, Delaware Counties and Cities, 2000` plus complaint tables covering `1991-2002`. That is enough to show that at least one pre-2005 statewide AI was not literally silent on disability data, even though the surviving scan still does not let me code disability-specific impediments/actions at high confidence.

A related New Castle County 2011 presentation summarizing the collaborative Delaware AI provides a second corroborative clue, but not a new denominator case. It reports common impediments across the four Delaware entitlement jurisdictions that included `expand the supply of accessible housing for persons with mobility impairments` and `expand mobility of Section 8 Housing Choice Voucher holders.` Because that document is a later presentation about the AI rather than the underlying 2003 AI itself, I treat it as corroboration only.

## Explicit comparison to the 47-AFH corpus

The AI results still need to be compared carefully to the AFH coding because the two planning regimes were not identical. AIs were more diagnostic and often included large demographic appendices; AFHs forced a more formal goal-setting exercise. The cleanest AFH comparison comes from `research_outputs/T_afh_extension.md`, which reports combined 47-AFH counts:
- Disability section present: 45/47 (95.7%)
- Accessibility substantive: 43/47 (91.5%)
- Integration substantive: 29/47 (61.7%)
- Quantitative disability goal present: 13/47 (27.7%)
- Accessible-unit inventory discussed (strict): 11/47 (23.4%)
- Race deeper or much deeper: 46/47 (97.9%)

What the comparison shows:

1. Both datasets usually mentioned disability.
   - Recovered AI sample: 17/17 had disability sections or distinct disability components.
   - AFH corpus: 45/47 had disability sections.
   These results continue to reject the overclaim that fair-housing planning simply ignored disability.

2. The recovered AI sample often had more raw disability data than the AFH era had measurable disability goals.
   - Recovered AI sample: 17/17 had quantitative disability data of some kind.
   - AFH corpus: only 13/47 had quantitative disability goals.
   This reflects format differences: AIs commonly inserted disability tables, while AFHs more clearly exposed whether analysis translated into measurable goals and metrics.

3. The deeper continuity is operational, not textual.
   - Recovered AI sample: disability usually appeared, but mostly as accessibility / special-needs diagnosis without durable inventory systems.
   - AFH corpus: disability also usually appeared, but only about one-quarter of AFHs produced quantitative disability goals and only about one-quarter discussed accessible-unit inventories.
   - In both datasets, race was much more likely to organize the document's core planning architecture.

4. Compared with this recovered AI sample, the AFH regime did not cure the same disability weakness; it changed its form.
   - AIs often had raw disability data and sometimes disability-specific recommendations.
   - AFHs more clearly demanded goals, but most jurisdictions still did not convert disability analysis into measurable targets or inventory-backed implementation.

## Matched AI-to-AFH examples from jurisdictions that appear in both corpora

### Dallas
- AI (2015): explicit accessible-housing impediment, affordable-accessible inventory review, and concrete disability actions.
- AFH: one of the strongest disability AFHs in the corpus, with quantitative disability goals and inventory discussion — yet still coded `race_much_deeper`.
- Takeaway: even one of the strongest AI-to-AFH progressions did not eliminate the race/disability asymmetry.

### Burlington
- AI (2010): disability-featured housing shortage was one of the principal impediments, with action items tied to universal design and production.
- AFH: disability section present, quantitative disability goals present, disability actions specific, but still coded `race_much_deeper`.
- Takeaway: jurisdictions could improve disability treatment across regimes and still leave race as the dominant planning frame.

### Washtenaw
- AI (2011): multiple accessibility and disability-related recommendations, including zoning and building-code changes.
- AFH: disability section present and actions specific, but still coded `race_much_deeper`.
- Takeaway: even where disability was taken seriously in both datasets, it still did not become the coequal organizing axis of fair-housing planning.

### Winston-Salem/Forsyth County
- AI (2009-2013): short but revealing disability section with handicap complaint-share data, design-and-construction noncompliance findings, and explicit accessible-unit shortage diagnosis; no clearly disability-tagged forward action plan.
- AFH: stronger disability section by AFH standards, including some supply-side counts and specific disability actions, but still coded `race_much_deeper`.
- Takeaway: the AFH regime improved disability specificity here, but not enough to alter the underlying race-centered planning architecture.

## Interpretation for the note

The safest reading of this recovered public-PDF sample is this:
- The recovered AI documents did not usually omit disability in a literal sense.
- They did usually omit disability in the infrastructural sense that matters to this note.
- Disability was commonly recognized as a protected-class concern, but the reviewed documents rarely built the feature-verification tools necessary to monitor accessible units, integrated placement, or design-and-construction compliance over time.
- The AFH corpus shows a related weakness. AFHs were more standardized and more race-analytic, but they still rarely produced inventory-backed disability planning.

That makes the omission structural across these two datasets, but only if the note states the omission precisely. The pattern is not `disability never appeared.` The pattern is `disability usually appeared without the data architecture needed to make it operationally equal to race-based fair-housing planning.`

## Finding in Prompt 49's terms

In this recovered 17-document public-PDF AI sample, disability received thinner treatment than race and ethnicity. The sample consists of sixteen directly recovered AI documents dated 2005-2015 plus one directly recovered 2010 update to a 1996-origin AI (New Haven). Across those 17 documents, disability was usually listed among the protected classes, usually accompanied by quantitative data, and often tied to identified impediments and actions. But disability still usually occupied a narrower accessibility / special-needs lane rather than the main segregation / lending / opportunity architecture. Where disability-specific actions appeared, they were most often education, outreach, training, testing, code review, or general accessible-housing encouragement — only rarely a registry, verified inventory, or monitoring system. Compared with the 47-AFH corpus, the continuity is structural: both datasets usually included disability in text but rarely converted it into inventory-backed disability planning.

This finding carries one explicit caution: the directly recovered document-date coverage reaches confidently to 2005, not to every year of the 1996-2015 AI era. The broader 1996-rooted inference is supported only indirectly by New Haven's 1996-origin AI update and by Oregon's appendix summaries of 1996 and 2004 local AIs, and does not justify overstating direct era coverage beyond the documents actually recovered.

## Caveats and next-best follow-up

1. This remains a transparent recovered public-PDF sample, not a census of all AIs.
   It is still not full-universe coverage.

2. Direct coverage still reaches only modestly backward in time.
   The counted pre-2006 evidence consists of one high-confidence document (Oregon 2005) plus one 1996-rooted update (New Haven 2010). A broad run of directly reviewable 1996-2004 city/county AIs was not recovered.

3. Some older or matched-jurisdiction materials surfaced but were not countable at high confidence.
   - Delaware's 2003 state AI is now better characterized: the surviving OCR is still too incomplete for confident full coding, but it is strong enough to verify a July 2003 statewide AI and a disability table (`Percent Disabled by Age Group, Delaware Counties and Cities, 2000`) plus 1991-2002 complaint series.
   - A 2011 New Castle County presentation about that collaborative Delaware AI corroborates that early-era impediments included accessible-housing supply and Section 8 mobility, but it is not the underlying AI and therefore not a denominator case.
   - San Mateo County's apparent 2012 AI link is now dead / misdirected on the public site.
   - Clackamas, Philadelphia, Richland County, and Seattle/King County remain only partially recoverable as same-jurisdiction AI matches.
   - `results/ai_audit_sample_ledger.md` logs the main surfaced-but-not-counted local candidates for audit reference.

4. Public availability probably biases the sample upward.
   Jurisdictions that preserved or reposted their AIs are likely better resourced than the average entitlement jurisdiction.

5. Highest-value follow-up.
   The highest-value follow-up is a same-jurisdiction recovery effort focused on San Mateo County, Clackamas County, Philadelphia, Richland County, and Seattle/King County, with explicit preference for archived official PDFs over derivative references inside later AFHs.

## Source list for counted AI sample

- Boston MA (2010): https://www.boston.gov/sites/default/files/embed/b/boston_ai_press_pdf_version_tcm3-16790.pdf
- Burlington VT (2010): https://www.burlingtonvt.gov/DocumentCenter/View/4728
- Clark County WA (2012): https://clark.wa.gov/sites/default/files/dept/files/community-services/CDBG/FullAIReport.pdf
- Dallas TX (2015): https://dallascityhall.com/departments/fairhousing/DCH%20Documents/Title_VI/2015%20AI.pdf
- Durham NC (2015): https://www.fairhousingnc.org/wp-content/uploads/2017/09/2015-AI-Durham-NC.pdf
- Los Angeles CA (2006): https://cityclerk.lacity.org/onlinedocs/2014/14-0118-S2_misc_01-27-14.pdf
- Louisiana non-entitlement areas (2010): https://www.doa.la.gov/media/ihqjfmwh/analysis-of-impediments-to-fair-housing-choice-non-entitlement-areas-2010.pdf
- New Haven CT (2010): https://ctdatahaven.org/wp-content/uploads/2025/12/NewHaven-Analysis-of-Impediments-Fair-Housing-2010.pdf
- Oregon non-entitlement areas (2005): https://digitalcollections.library.oregon.gov/assets/downloadwiz/274081
- Phoenix AZ (2015): https://www.phoenix.gov/nsdsite/Documents/nsd_rp_aitfh.pdf
- Prince George's County/Bowie MD (2011-2012): https://www.princegeorgescountymd.gov/sites/default/files/Department-of-Housing-and-Community-Development-Analysis-Impediment-Fair-Housing-PDF.pdf
- San Antonio TX (2010): https://www.sa.gov/files/assets/main/nhsd/documents/analysis-of-impediments.pdf
- San Diego Regional AI (2011): https://www.sandiego.gov/sites/default/files/legacy/cdbg/pdf/110600ai.pdf
- Snohomish County WA (2012): https://snohomishcountywa.gov/DocumentCenter/View/6579
- Spokane WA (2008): https://static.spokanecity.org/documents/chhs/plans-reports/planning/2008-fair-housing-impediments-analysis.pdf
- Washtenaw Urban County MI (2011): https://content.civicplus.com/api/assets/04e8ab98-35df-401c-8966-f0a1700e42fa
- Winston-Salem/Forsyth County NC (2009-2013): https://www.cityofws.org/ArchiveCenter/ViewFile/Item/512
