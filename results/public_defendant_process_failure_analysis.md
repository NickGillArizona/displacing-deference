# Public-defendant process failure analysis

Generated: 2026-04-16T07:32:22.077982+00:00

## Scope and adaptation

- Reconstructed the exact 413-case universe with the existing `public_defendant_process_cases` rule from `scripts/unified_raw_text_target_inventory.py`: screened cases with `defendant_type` in `MUNICIPALITY`, `HOUSING_AUTHORITY`, or `GOVERNMENT` plus an accommodation/request/process signal in the structured fields.
- The disability-wave coding fields are nested under `record["unified_overnight"]["classification"]` in `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json`, not as top-level columns. The script adapts to that actual schema.
- Of the 413 selected cases, 278 have disability-wave classifications and 135 do not. I did not invent missing classifications for the uncoded remainder.
- Loss-fit calculations therefore use the 278 coded cases, especially 229 adverse outcomes (`DEFENDANT_WIN` or `PROCEDURAL`). A stricter diagnosed-loss subset excludes 66 adverse outcomes coded `UNCLEAR` or `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`, leaving 163 cases.

## Topline subset shape

- Defendant mix in the 413-case universe: HOUSING_AUTHORITY 185, MUNICIPALITY 184, GOVERNMENT 44.
- Most common housing types in the 413-case universe: SECTION_8_VOUCHER 95, PRIVATE_MARKET 89, SUPPORTIVE_HOUSING 80, PUBLIC_HOUSING 74, UNDETERMINED 44.
- Most common housing types in the 278 coded cases: SUPPORTIVE_HOUSING 64, SECTION_8_VOUCHER 58, PUBLIC_HOUSING 55, PRIVATE_MARKET 51, UNDETERMINED 31.

## What specific failures dominate

- Family-level pattern in the 163 diagnosed losses: TRANSLATION 52 (31.9%), PROCEDURAL_GATEWAY 46 (28.2%), ELEMENT_MISMATCH 22 (13.5%), and CAUSAL_LINK 20 (12.3%).
- Leading mechanisms: JURISDICTION_OR_STANDING 30 (18.4%), REQUEST_NOT_ALLEGED 27 (16.6%), ELEMENTS_NOT_TIED_TO_FACTS 26 (16.0%), DISABILITY_NEXUS_MISSING 14 (8.6%), EXHAUSTION_OR_PRECLUSION 12 (7.4%).
- Missing institutional functions are concentrated in THEORY_SELECTION 113 (69.3%), FACT_DEVELOPMENT 110 (67.5%), DOCUMENT_ASSEMBLY 70 (42.9%), JURISDICTIONAL_TRIAGE 57 (35.0%).
- The most common administratively observable facts are PUBLIC_PROGRAM_RULE_OR_DECISION 140 (85.9%), DOCUMENTED_REQUEST 135 (82.8%), NOTICE_OR_TIMELINE_RECORD 129 (79.1%), HEARING_OR_GRIEVANCE_RECORD 53 (32.5%).

These counts point to a consistent story: courts are often looking for a request trail, a usable chronology, a defendant-specific theory, and a procedurally proper path into court. The dominant problems are not hidden housing events but failures of translation, record assembly, and jurisdictional routing.

## Housing-type pattern highlights in diagnosed losses

- SECTION_8_VOUCHER cases are led by elements-not-tied-to-facts and request/nexus/causal-link failures: ELEMENTS_NOT_TIED_TO_FACTS 9 (22.5%), ADVERSE_ACTION_NOT_CONNECTED 5 (12.5%), DISABILITY_NEXUS_MISSING 5 (12.5%), MIXED 5 (12.5%), REQUEST_NOT_ALLEGED 5 (12.5%).
- PUBLIC_HOUSING cases are led by request-not-alleged and elements-not-tied-to-facts failures: ELEMENTS_NOT_TIED_TO_FACTS 7 (24.1%), REQUEST_NOT_ALLEGED 7 (24.1%), JURISDICTION_OR_STANDING 5 (17.2%), ADVERSE_ACTION_NOT_CONNECTED 3 (10.3%), DISABILITY_NEXUS_MISSING 3 (10.3%).
- SUPPORTIVE_HOUSING cases show a different mix, with more technical-proof and preclusion/gateway problems: TECHNICAL_PROOF_GAP 7 (21.2%), EXHAUSTION_OR_PRECLUSION 6 (18.2%), ELEMENTS_NOT_TIED_TO_FACTS 5 (15.2%), JURISDICTION_OR_STANDING 5 (15.2%), REQUEST_NOT_ALLEGED 5 (15.2%).

The practical implication is that voucher and public-housing cases are mostly failing on request articulation, factual linkage, and administrative routing, while supportive-housing and zoning-adjacent cases more often add proof or preclusion burdens on top of the process problem.

## Reporting-architecture fit

- In the 229 coded adverse-outcome losses, 220 cases (96.1%) include at least one fact pattern that the proposed reporting architecture would directly generate or standardize.
- That coverage is overwhelmingly request-log coverage: accommodation-request-log patterns appear in 220 losses (96.1%), while accessible-unit-inventory patterns appear in 10 (4.4%) and inspection-flag patterns in 12 (5.2%).
- Fixability coding is more cautionary: BOTH 141 (61.6%), TIER2_INSTITUTIONAL_INTERMEDIATION 77 (33.6%), NEITHER 10 (4.4%).

So the reporting architecture is a very strong evidentiary fit, but mostly as a floor rather than a complete solution. The missing records are usually request-level and decision-level, yet most losses are coded as needing both reporting architecture and institutional intermediation rather than reporting alone.

## Bottom line

The exact 413-case public-defendant process subset is real, but only 278 cases are in the disability-wave coded tranche. Within the coded losses, the dominant failures are request translation, factual mapping, and jurisdictional gateway problems. The proposed architecture fits those failures closely because 96.1% of coded adverse losses already turn on records the regime could generate, above all request logs, notices, program decisions, and grievance trails. But the fixability coding also shows why the note should avoid overclaiming: most of these cases still need authority mapping, theory selection, and legal intermediation on top of better reporting.

## Files produced by this task

- `scripts/public_defendant_analysis.py`
- `results/public_defendant_process_failure_results.json`
- `results/public_defendant_process_failure_analysis.md`
