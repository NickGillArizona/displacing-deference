# Disclosure-effect comparison memo

This memo consolidates disclosure-effect evidence preserved in the allowed local research record. It is a comparison table, not a pooled statistical meta-analysis: the cited studies use different outcomes and designs, so the useful synthesis is side-by-side comparison of mechanism, effect size, and timing.

Verified support used:
- /mnt/c/Users/nickg/OneDrive/Documents/Note/v89_MEMO_APPENDIX_F_REGISTRIES_HMDA.md §§ F.20-F.27
- /mnt/c/Users/nickg/OneDrive/Documents/Note/COMPLETED_RESEARCH_FINDINGS.md § V

## Consolidated table

| Regime | Statutory Authority | Year Expanded | Unit of Observation | Primary Users | Effect Measure | Effect Size | Time to Effect | Key Citation |
|---|---|---|---|---|---|---|---|---|
| HMDA | 12 U.S.C. §§ 2803-2804 | 2002-2004 Regulation C overhaul; 2015 CFPB final-rule expansion | Individual mortgage application / Loan Application Register row, with census-tract, pricing, and property fields | Federal Reserve, CFPB, prudential regulators, DOJ, and public officials | Outlier screening and enforcement referrals using expanded HMDA pricing/property fields | Federal Reserve used HMDA to flag about 200 lenders annually; Countrywide ($335M) plus Wells Fargo ($175M) produced $510M in settlements tied to that screening pipeline | 3-7 years | Avery, Brevoort & Canner, 91 Fed. Res. Bull. A344 (Summer 2005); Munnell et al., 86 Am. Econ. Rev. 25 (1996) |
| EEO-1 | 42 U.S.C. § 2000e-8(c); 29 C.F.R. pt. 1602 | 1966 original; expanded periodically | Establishment (physical workplace) × job category × race/ethnicity × sex | EEOC, OFCCP, and compliance reviewers | Long-run management-composition change after compliance reviews | Kalev & Dobbin find higher shares of women and African Americans in management after reviews, with effects still measurable 20+ years later; burden context: ~5.2 million hours/year and about $273 million annually | Decades (20+ years) | Kalev & Dobbin, 31 Law & Soc. Inquiry 855 (2006) |
| TRI | EPCRA § 313, 42 U.S.C. §§ 11001-11050 | 1986 enactment; first public release 1989 | Facility × chemical × release pathway × quantity | EPA/regulators plus community, media, and market actors | Stock-market sanction on first public disclosure day; long-run releases trend | $4.1 million average stock loss per firm on the first TRI release day; EPA reports a 49% decline in toxic releases since TRI inception | Immediate market reaction; 2-5 years for behavioral/emissions response | Hamilton, 28 J. Envtl. Econ. & Mgmt. 98 (1995); Konar & Cohen, 32 J. Envtl. Econ. & Mgmt. 109 (1997) |
| OSHA injury logs | 29 U.S.C. § 657 | Various | Workplace × injury type | OSHA inspectors | Serious-injury reduction after random OSHA inspections | Each inspection produced 2.4 fewer serious injuries over 5 years (9%) | 5 years | Johnson, Levine & Toffel, 15 Am. Econ. J.: Applied Econ. 30 (2023) |
| Energy benchmarking | 42 U.S.C. § 17103 + local benchmarking ordinances | 2008+ (55+ jurisdictions) | Building × energy consumption × year | Local regulators, building owners/managers, and public/market actors | Utility-expenditure change in covered office buildings | Benchmarking mandates reduced utility expenditures by about 3% in covered office buildings | 2-5 years | Palmer & Walls, RFF DP 15-12 (2015); Kontokosta & Tull, 187 Applied Energy 386 (2017) |
| Proposed accessibility reporting regime | 42 U.S.C. §§ 3608(e)(5)-(6), 3614a; 24 C.F.R. pt. 121 | Proposed | Unit × building × accommodation process | HUD FHEO; fair housing organizations | TBD | Not yet observed | Not yet observed | Appendix F §§ F.22, F.25-F.26; COMPLETED_RESEARCH_FINDINGS § V |

## Verification notes

- HMDA: I use the verified Federal Reserve Bulletin cite preserved in Appendix F, 91 Fed. Res. Bull. A344 (Summer 2005). The task prompt's A73 pinpoint is not independently reverified in the allowed sections.
- EEO-1: the year cell now shows the clean prompt-spec value. The burden figures and the long-run Kalev & Dobbin effect are independently preserved in Appendix F § F.27 and COMPLETED_RESEARCH_FINDINGS § V.1.
- TRI: the year cell now shows the clean prompt-spec value. Hamilton's $4.1M result is the causal event-study estimate; EPA's 49% decline is a descriptive agency trend, not the same design.
- OSHA: the table now shows the clean prompt-spec statutory, year, unit, user, and effect values. COMPLETED_RESEARCH_FINDINGS § V.4 preserves inspection-effect evidence from a random-inspection design rather than a clean independently preserved injury-log disclosure estimate.
- Energy benchmarking: COMPLETED_RESEARCH_FINDINGS § V.4 independently preserves both the ~3% utility-expenditure result and the point that, since 2008, at least 55 U.S. jurisdictions have adopted benchmarking laws. The fuller Kontokosta & Tull citation detail remains prompt-supplied rather than independently reverified in those sections.
- Proposed regime: the table now shows the clean prompt-spec authority, unit, and user values. The FHA statutory anchors are reverified in Appendix F §§ F.22, F.25-F.26, while the Part 121 citation, unit language, and fair-housing-organization user component remain prompt-supplied.

## Analysis

Four synthesis points are strong enough to use in later drafting.

1. HMDA remains the strongest authority-side analogy.

Appendix F §§ F.22, F.25-F.26 preserve the best doctrinal comparison for the note's proposed move from person-level housing data to more granular building-linked reporting. HMDA shows that a disclosure regime can expand from lower-granularity reporting to application-level and property-linked fields under a general rulemaking grant, and that the expanded dataset then feeds an enforcement referral pipeline.

2. Energy benchmarking is the cleanest building-level behavior-change analogue.

Among the non-HMDA comparators, energy benchmarking is the most structurally similar regime because it operates at the building level, relies on mandatory reporting, and preserves a measured downstream outcome change (~3% lower utility expenditures in covered office buildings). For note-writing, this is the best comparator for the proposition that standardized building-level reporting can change management behavior before direct enforcement occurs.

3. TRI and EEO-1 show two different disclosure pathways: immediate sanction and durable structural change.

TRI supplies the clearest immediate-response evidence: the first public disclosure produced a $4.1M average stock loss per firm in Hamilton's event study, while later sources preserve broader emissions reductions as descriptive context. EEO-1 supplies the opposite end of the timing spectrum: compliance reviews produced management-composition changes that remained visible decades later. Together they support a staged theory of change rather than a single disclosure-effect mechanism.

4. OSHA should be cited narrowly.

The OSHA material preserved in COMPLETED_RESEARCH_FINDINGS § V.4 supports the proposition that inspection/targeting informed by safety-reporting systems can reduce harms over a multi-year horizon. It should not be described in later drafting as a directly verified injury-log disclosure effect. If used, it should be introduced explicitly as adjacent inspection evidence, not as a clean parallel to HMDA, TRI, or energy benchmarking.

## Revision log for this pass

- kept all six regime rows and all required columns;
- rewrote the OSHA row, verification note, and analysis to frame OSHA as adjacent inspection/targeting evidence rather than as a directly verified injury-log disclosure result;
- removed inline prompt labels from the table and kept caveats in the verification notes;
- separated TRI's causal event-study result ($4.1M stock loss) from EPA's descriptive 49% decline so they are not presented as the same kind of estimate;
- removed the prior overstatement that the 2008+/55+ jurisdictions energy-benchmarking point was unreverified;
- replaced the old "What changed in this fix" language with a revision log plus drafting-oriented analysis.

## Drafting handoff

- Lead with HMDA for the statutory-authority argument under § 3614a.
- Pair energy benchmarking with TRI when arguing that disclosure can change behavior before formal enforcement.
- Use EEO-1 for durability and burden-comparison points.
- Use OSHA only with the narrowed phrasing above: adjacent inspection/targeting evidence, not a standalone verified injury-log disclosure effect.
- Before converting any prompt-supplied table detail noted above into a footnote or firm factual assertion in the note, reverify it against the underlying primary source.
