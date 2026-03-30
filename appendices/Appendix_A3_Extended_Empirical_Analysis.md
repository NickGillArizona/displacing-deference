## Appendix A-3: Extended Empirical Analysis Methodology

This Appendix describes the methodology for the extended empirical analyses reported in this Note. These analyses supplement the case-classification methodology described in Appendix A and the PUMS replication methodology described in Appendix A-2.

### A. Overview

The extended analyses draw on three data sources: (1) the unified dataset (N=3,193 cases, 6,718 claims) described in Appendix A; (2) the 2020–2024 ACS 5-Year PUMS described in Appendix A-2; and (3) HUD's Comprehensive Housing Affordability Strategy (CHAS) data documentation. Ten research areas were investigated, producing findings integrated into the body text and footnotes of this Note.

### B. Multivariate Regression Analysis

#### B.1 Model Specification

Logistic regression models were estimated using Python's statsmodels package. Models were estimated on the unified dataset (N=3,193 cases, 6,718 claims):

- Model 1: Unified dataset, strict win (DV: 1=PLAINTIFF_WIN, 0=DEFENDANT_WIN or MIXED)
- Model 2: Unified dataset, broad win (DV: 1=PLAINTIFF_WIN or MIXED, 0=DEFENDANT_WIN)

Independent variables:
- post_loper_bright (1 if year≥2024, 0 otherwise)
- procedural_posture (dummy: MTD reference, SUMMARY_JUDGMENT, APPEAL, OTHER)
- defendant_type (dummy: PRIVATE_LANDLORD reference, HOUSING_AUTHORITY, HOA_CONDO_ASSN, MUNICIPALITY, PROPERTY_MANAGEMENT, OTHER)
- accommodation_type (dummy: DISCRIMINATION_PRIMARY reference, ASSISTANCE_ANIMAL, SOBER_LIVING_GROUP_HOME_ZONING, POLICY_EXCEPTION, STRUCTURAL_MODIFICATION, OTHER)
- interactive_process_discussed (binary)
- delay_as_denial (binary)
- race_mentioned (binary)
- plaintiff_type (dummy: INDIVIDUAL_TENANT reference, GROUP_HOME_OPERATOR, FAIR_HOUSING_ORG, GOVERNMENT, OTHER)

Two interaction models were also estimated (Models 5–6): post_loper_bright × procedural_posture and post_loper_bright × interactive_process_discussed.

#### B.2 Key Results

Post-Loper Bright effect (strict win): § 3604 OR=0.60, p=0.002; RA OR=0.49, p<0.001. Post-LB × appeal interaction: OR=3.34, p=0.002. Interactive process: OR=1.16–1.58, all p>0.10 (not independently significant). Delay-as-denial: OR=1.95–3.69 (significant in broad models). Race mentioned: OR=0.40–0.49, p<0.001. Pseudo R-squared: 0.10–0.17.

#### B.3 Limitations

All models use published federal opinions, a convenience sample subject to selection bias. Unmeasured variables—legal representation quality, medical documentation strength, judicial ideology—may confound estimates. Standard errors are robust but heteroskedasticity-consistent standard errors were not employed.

One structural feature of the results partially addresses the Priest-Klein selection-bias concern. If the post-*Loper Bright* decline were driven purely by changes in the composition of filed cases, the selection effect should operate relatively uniformly across procedural stages. Instead, the decline is overwhelmingly concentrated at the motion-to-dismiss stage (broad rate decline from 38.7% to 19.7%, p<0.0001), with no statistically significant change at summary judgment (49.7% to 45.4%, p=0.50) or appeal (38.9% to 37.2%, p=0.81). This stage-specific concentration is inconsistent with a pure case-selection explanation.

### C. Pro Se Plaintiff Analysis

#### C.1 Detection Methodology

Pro se status was identified through two independent methods: (1) case-insensitive text-pattern search of the pipeline's brief_summary, key_holding, accommodation_description, and case_name fields for "pro se," "in forma pauperis," "IFP," "self-represented," "without counsel," "unrepresented," "prisoner," and "incarcerated"; and (2) the supplemental Haiku per-claim extraction, which classified pro_se status and counsel_named as independent fields from the full opinion text.

#### C.2 Detection Rates

The per-claim extraction identified 1,643 pro se cases (51.5% of the unified dataset, N=3,193), with 1,550 cases (48.5%) involving represented plaintiffs. Pro se win rate: 0.9%; represented win rate: 9.1%.

#### C.3 Three-Population Framework

The per-claim extraction reveals that pro se status operates primarily as a threshold barrier to merits adjudication rather than a predictor of outcomes on the merits. In the unified dataset (N=3,193), pro se plaintiffs constitute 51.5% (1,643 cases) but achieve only a 0.9% win rate, compared to 9.1% for represented plaintiffs (1,550 cases). The 10.1-fold representation gap represents a structural barrier operating at every stage of litigation.

#### C.4 RA Merits Win Rates by Representation Status

| Category | Pro Se n | Pro Se PW% | Rep n | Rep PW% |
|----------|----------|------------|-------|---------|
| ASSISTANCE_ANIMAL | 4 | 25.0% | 17 | 29.4% |
| STRUCTURAL_MODIFICATION | 8 | 0.0% | 9 | 0.0% |
| TRANSFER | 8 | 0.0% | 3 | 0.0% |
| POLICY_EXCEPTION | 5 | 0.0% | 37 | 13.5% |
| PARKING | 4 | 0.0% | 7 | 28.6% |
| COMMUNICATION | 2 | 0.0% | 14 | 28.6% |
| SOBER_LIVING | 0 | — | 10 | 30.0% |

The 5.6-fold gap (3.8% vs. 21.3%) represents the representation effect *after* controlling for the pleading barrier — pro se plaintiffs who manage to reach the merits still face dramatically worse outcomes. The representation effect is concentrated in categories requiring sophisticated legal framing (POLICY_EXCEPTION, PARKING, COMMUNICATION) where represented plaintiffs win 13–30% and pro se plaintiffs win 0%.

#### C.5 Pro Se × Defendant Type Cross-Tabulation

**Methodology.** Pro se status and defendant type were extracted from the per-claim Haiku classification of full opinion text (N=2,366 cases). Plaintiff win was coded from the `plaintiff_wins` field. The cross-tabulation was computed at the case level across the full database, then separately on the RA merits-reached subset. No statistical model was applied; rates are descriptive.

**Full-Database Cross-Tabulation (N=3,193 cases).** Pro se plaintiffs are channeled disproportionately toward housing authority defendants. Conversely, 69% of all housing-authority cases are brought pro se, compared to the 51.5% database-wide baseline.

| Defendant Type | Pro Se n | PS Win% | Represented n | Rep Win% |
|---|---|---|---|---|
| Housing Authority | 198 | 1.5% | 89 | 10.1% |
| Property Management | 488 | 0.8% | 267 | 13.1% |
| Private Landlord | 213 | 1.9% | 171 | 13.5% |
| **Total** | **1,643** | **0.9%** | **1,550** | **9.1%** |

The overall pro se win rate (0.9%) represents a 10.1-fold disadvantage relative to represented plaintiffs (9.1%). The pro se penalty dominates the interaction: unrepresented plaintiffs win at approximately 0.8–1.9% regardless of defendant type. The compounding of pro se status with housing-authority defendants (1.5% win rate) is severe in absolute terms but not multiplicative, suggesting the two disadvantages do not interact synergistically.

**RA Merits-Reached Subset (n=156).** Restricting to decided RA merits claims (excluding PENDING and REMANDED outcomes) reveals a different pattern:

| Defendant Type | Pro Se n | Pro Se PW | Pro Se PW% | Rep n | Rep PW | Rep PW% |
|---|---|---|---|---|---|---|
| Property Management | 21 | 1 | 4.8% | 25 | 9 | 36.0% |
| Housing Authority | 15 | 2 | 13.3% | 13 | 2 | 15.4% |
| Private Landlord | 9 | 0 | 0.0% | 10 | 2 | 20.0% |
| HOA/Condo | 4 | 0 | 0.0% | 21 | 5 | 23.8% |
| Municipality | 1 | 1 | 100.0% | 28 | 8 | 28.6% |
| Other | 4 | 0 | 0.0% | 5 | 2 | 40.0% |
| **Total** | **54** | **4** | **7.4%** | **102** | **28** | **27.5%** |

On the merits, the representation gap is largest against property management companies (31.2 pp) and private landlords (20.0 pp), where informal negotiation and adversarial litigation capability are most consequential. Against housing authorities, the gap effectively disappears (13.3% vs. 15.4%), consistent with the hypothesis that formalized public-housing grievance procedures partially substitute for litigation capability. The municipality pro se cell (n=1) is unreliable. Cell sizes are modest throughout.

**Interpretation.** The full-database and merits-reached analyses tell complementary stories. The full database reveals that the pro se penalty operates primarily as a threshold barrier—92% pleading-stage attrition versus 65% for represented plaintiffs (*see* Section C above)—compounded by channeling into housing-authority defendants where even represented plaintiffs win at below-average rates. The merits-reached subset shows that among the small number of pro se plaintiffs who survive dismissal, defendant type matters more than representation status in certain matchups. Both findings are consistent with the Galanter repeat-player framework: the pro se disadvantage is structural and operates at multiple stages of litigation.

#### C.6 Post-Loper Bright Pro Se Trends

Post-*Loper Bright* decline is concentrated among represented plaintiffs (broad rate -6.6 pp RA, -8.7 pp § 3604); pro se changes are statistically insignificant because the baseline was already near zero. On RA merits claims, the post-*Loper Bright* decline from 20.4% to 6.7% plaintiff win rate represents a 67% relative decline — more severe than the full-database decline — suggesting that the deference-free environment particularly disadvantages accommodation claims.

#### C.7 State-Level and Circuit-Level Analysis

**State-level plaintiff win rates (§ 3604 Database, n=1,496, states with n≥10 decided).** Top-performing states (strict): Illinois 35.7% (n=56), Louisiana 33.3% (n=27), Tennessee 29.2% (n=24), Florida 27.7% (n=65). Top broad rates: Louisiana 59.3%, Illinois 55.4%, Florida 52.3%, DC 48.3% (n=29), New Jersey 48.8% (n=43). Lowest-performing (strict): Maryland 9.3% (n=54), Texas 11.3% (n=62), Arizona 12.1% (n=33), New York 15.0% (n=180), California 15.6% (n=122). State-level rates may reflect case-selection effects: high-volume jurisdictions (particularly S.D.N.Y.) attract higher proportions of pro se filings, prisoner complaints, and shelter-related claims that inflate defendant-win rates.

**S.D.N.Y. concentration effect.** S.D.N.Y. cases: RA Database 63.0% pro se (0.0% strict win rate); § 3604 Database 47.7% pro se (0.0% strict). The 2d Circuit's 10.2% MTD broad rate (lowest of circuits with n≥20) is substantially explained by the S.D.N.Y. pro se concentration effect.

**State-level disability cost-burden penalties (2020–2024 ACS 5-Year PUMS).** Top White disability penalties: Ohio 19.3 pp, Pennsylvania 19.1 pp, Maryland 18.8 pp, Texas 18.7 pp, Illinois 18.0 pp. Spearman rank correlations (n=10 states with highest case volumes): penalty vs. litigation volume rho=-0.03; White penalty vs. § 3604 broad win rate rho=-0.43. Housing authority defendant share in high-penalty states: 13.0% vs. 6.1% in low-penalty states.

### D. Interactive Process and Delay-as-Denial Analysis

#### D.1 Cross-Tabulation Methodology

The interactive_process_discussed and delay_as_denial fields (binary YES/NO) were cross-tabulated with defendant_type, accommodation_type, disability_category, procedural_posture, plaintiff_type, and circuit (derived from court field). Chi-squared tests were applied where expected cell counts >=5. The per-claim extraction enabled a more precise analysis restricted to RA merits cases (n=132 cases, 175 claims).

#### D.2 Full-Database Findings

Interactive process effect on win rates (unified dataset, N=3,193): 12.2% win rate when interactive process is discussed versus 4.2% when not discussed. Strongest effects by accommodation type: transfer +45.2 pp broad (57.1% vs. 11.9%), parking +36.1 pp (83.3% vs. 47.2%). By defendant type: HOA/condo 18.5% IP rate, private landlord 7.4%. By circuit: 1st Circuit 38.5%, 2d Circuit 9.2%, 3d Circuit 4.9%.

Delay-as-denial: raised in 2.8% of cases. Against private landlords: 2.3% rate, 80.0% broad win. Against HOAs: 9.0% rate, 73.7% broad.

IP and DaD co-occur at dramatically elevated rates (84.4% of DaD cases also involve IP). Combined broad win: 64.8%, strict 40.7%.

Post-Loper Bright: IP invocation declined (8.7% to 6.3%, p=0.038) while effectiveness held steady. DaD invocation declined non-significantly.

#### D.3 Per-Claim RA Merits Findings

The per-claim analysis restricted to RA merits cases (n=132 cases) reveals a more nuanced picture:

**Interactive process.** Discussed in 44% of RA merits cases (58/132). Plaintiff win rate: 16.9% when discussed versus 20.0% when not (OR=0.82). This reverses the positive association observed in the full-database analysis, likely because courts discuss the interactive process when analyzing *why the landlord's response was inadequate* — a discussion that does not reliably translate to plaintiff victories.

**RA standard applied.** The analytical framework the court applies proves more predictive than whether the interactive process is discussed:

| RA Standard | n | PW% |
|-------------|---|-----|
| INTERACTIVE_PROCESS | 17 | 35.3% |
| DIRECT_BALANCING | 120 | 16.7% |
| BURDEN_SHIFTING | 16 | 6.2% |
| UNDUE_BURDEN_DEFENSE | 7 | 0.0% |
| FUNDAMENTAL_ALTERATION_DEFENSE | 3 | 0.0% |

When courts apply the interactive process *framework* — evaluating the reasonableness of the landlord's process rather than the outcome — plaintiff success reaches 35.3%, more than five times the 6.2% rate under burden-shifting. This suggests that the procedural framework directs substantive outcomes.

**Delay-as-denial.** Among RA merits cases, plaintiff win rate when delay-as-denial is raised: 4.8% (1/21) versus 20.7% (29/140) without (OR=0.28). This reverses the full-database finding (39.3% strict win rate), indicating a selection effect: plaintiffs invoke delay-as-denial when their substantive case is weakest. The full-database positive association was inflated by non-merits outcomes and cases where delay-as-denial accompanied stronger substantive claims.

**Interpretation.** The divergence between full-database and RA-merits findings on both doctrines illustrates the importance of the three-population segmentation. The full-database analysis included pleading failures and non-RA cases where interactive process and delay-as-denial discussion correlated with different case characteristics. The RA-merits analysis isolates the doctrinal effect on cases that actually reached substantive adjudication.

### E. Hispanic/Latino PUMS Analysis

#### E.1 Methodology

Census PUMS API: GET https://api.census.gov/data/2024/acs/acs5/pums?get=PWGTP,DPHY,DOUT,GRPIP,RAC1P,HISP&for=state:*&SPORDER=1&TEN=3

The HISP variable distinguishes Hispanic (HISP=02–24) from non-Hispanic (HISP=01). Disability defined as DPHY=1 or DOUT=1. Cost burden as GRPIP>30 excluding GRPIP=101.

#### E.2 Key Results

Non-Hispanic White penalty: 17.5 pp. Non-Hispanic Black: 10.1 pp. Non-Hispanic AIAN: 11.1 pp. Hispanic (any race): 7.6 pp.

Hispanic-NHW convergence: non-disabled gap 9.2 pp inverts to −0.7 pp among disabled renters (compression >100%).

AIAN composition finding: 47.9% of AIAN-alone renter householders are Hispanic. Removing them raises disability prevalence from 13.1% to 17.2% and the penalty from 7.3 pp to 11.1 pp.

### F. Housing Adequacy and Building Stock Analysis

#### F.1 Methodology

Census PUMS API queries for PLM (plumbing), KIT (kitchen), RMSP/NP (rooms/persons for overcrowding), YRBLT (year built), and BLD (building type), cross-tabulated with DPHY, DOUT, RAC1P.

FHA § 3604(f)(3)(C) coverage estimated by: BLD in {5,6,7,8,9} (≥3 apartments, proxy for 4+ units) AND YRBLT in {1990 or later categories}.

#### F.2 Key Results

Pre-1990 building occupancy (disabled): White 67.7%, Black 72.5%, AIAN 69.8%. Disability penalty: White 5.1 pp, Black 8.2 pp, AIAN 5.1 pp.

FHA coverage (disabled renters in 4+ unit post-1990 buildings): White 23.7%, Black 19.8%, AIAN 15.4%.

45.1% of Black disabled renters live in 4+ unit pre-1990 buildings—the building type targeted by § 3604(f)(3)(C) but outside its temporal scope.

### G. Subsidy Program and Housing-Type Analysis

#### G.1 Methodology

Unified dataset (N=3,193) classified by housing_type and subsidy_program fields. Win rates computed as strict (PLAINTIFF_WIN / decided) and broad ((PLAINTIFF_WIN + MIXED) / decided), excluding PROCEDURAL, SETTLEMENT, and UNDETERMINED outcomes. Pre/post Loper Bright comparison using year ≤2023 vs. ≥2024.

#### G.2 Key Results

§ 3604(f)(3)(C) resilience: 42.9% strict post-LB vs. 38.5% pre-LB (n=27 decided). Section 8 voucher collapse: 13.6% to 3.0% strict. Section 504-covered housing: 5.7% strict post-LB. Cases citing § 3604(f)(3)(B) explicitly: 25.4% strict (n=433) vs. 11.7% for NONE_SPECIFIC (n=1,241).

### H. State-Level Geographic Convergence

#### H.1 Methodology

State-level plaintiff win rates computed from the unified dataset (N=3,193) for states with n≥15 decided cases. Census PUMS disability cost-burden penalties computed by state for the 10 highest-volume states.

#### H.2 Key Results

Spearman rank correlations (n=10 states): White penalty vs. litigation volume rho=−0.03; White penalty vs. § 3604 broad win rate rho=−0.43. High-penalty states have 2.1x the housing authority defendant rate. Top penalties: Ohio 19.3 pp, Pennsylvania 19.1 pp, Maryland 18.8 pp (White).

### I. Invisible Population Analysis

#### I.1 Methodology

Disabled renter householders excluded from cost-burden analysis identified as those with GRPIP=101 (no cash rent, positive income) or GRPIP=0 (zero/negative income).

#### I.2 Key Results

Total invisible population (disabled, three racial groups): 867,019. Invisibility rates: Black disabled 23.1%, White disabled 18.3%, AIAN disabled 16.2%. Non-disabled comparisons: Black 14.6%, White 9.4%, AIAN 10.7%. No-cash-rent subpopulation median HINCP: $7,400 (Black), $9,000 (White), $7,200 (AIAN).

### J. CHAS Data Feasibility Assessment

The HUD CHAS (2018–2022 vintage) was assessed for disability × race × housing problems cross-tabulation. Finding: no CHAS table combines all three dimensions. This data gap is cited in the body text as evidence of the enforcement infrastructure's failure to treat disability and race as intersecting axes.

### K. Disability Category Analysis

#### K.1 Methodology

Unified dataset (N=3,193) cross-tabulated disability_category with accommodation_type, procedural_posture, and pre/post Loper Bright period. PUMS cost-burden penalties disaggregated by the six ACS disability types (DPHY, DOUT, DREM, DDRS, DEAR, DEYE).

#### K.2 Key Results

Win rate hierarchy (strict): sensory 29.7%, I/DD 29.8%, mobility 25.8%, substance use 22.4%, mental health 18.4%. Post-LB collapse: sensory −31.7 pp (small n), I/DD −15.8 pp, substance use −4.4 pp (most resilient). MTD dismissal rate: mental health 76%, mobility 56%. PUMS confirms DPHY/DOUT definition captures highest-penalty disabilities.

### L. Computational Environment

All analyses were performed on March 28, 2026 using Python 3.x with the json, math, collections, and statsmodels libraries. Census PUMS queries used the 2024 ACS 5-Year endpoint. Regression scripts and full output are preserved in the project repository and available upon request from the author.

---
