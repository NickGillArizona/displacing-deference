# LLM Handoff Research Memo: Disability-Wave Research Package

Date: 2026-04-15
Prepared by: Hermes Agent
Primary audience: another LLM asked to revise, plan revisions for, or otherwise use the disability-wave research package for the FHA/AFFH law-note project.
Primary draft target: `drafts/current_draft.md`
Project frame: disability-centered AFFH enforcement / reinforcement-not-replication / verification mismatch / enforcement-pipeline failure.

## 0. Purpose of this memo

This memo is a self-contained handoff packet for another LLM. Its purpose is to explain:

1. what research has already been done,
2. what the final disability-wave dataset now establishes,
3. what findings are safe enough to use directly in the note,
4. what findings must be qualified or used cautiously,
5. which examples are validated enough to cite,
6. what revision priorities follow from the research,
7. and what research should now be treated as optional or deferred.

This memo is written so a receiving LLM does not need to reconstruct the entire history of the overnight research run.

## 0.1 What the receiving LLM should know before using this memo

This project is not a blank-slate article. It sits inside a controlled law-note workspace with explicit editorial rules.

The receiving LLM should assume:
- the live working draft is `drafts/current_draft.md`
- the current work order treats `note_v84_GPT.md` / `drafts/current_draft.md` as the authoritative target
- the note's approved architecture should be preserved unless a higher-priority instruction expressly authorizes redesign
- the main job is empirical-firming, narrowing, and clarification — not rewriting the note into a new paper

The receiving LLM should also know that the project has two neighboring but distinct lines of thought:
- the current live draft's disability-centered AFFH / reinforcement-not-replication frame
- the broader or more experimental data-mandate / registry work summarized in other memos

This handoff memo is primarily about the first line of work: how to use the completed disability-wave package to improve the current note.

## 0.2 Recommended read order for a receiving LLM

If the next task is revision, planning, or editorial synthesis, the safest read order is:

1. `control_plane/CURRENT_WORK_ORDER.md`
2. `control_plane/STANDING_EDITOR_DIRECTIVES.md`
3. `control_plane/DECISION_LEDGER.md`
4. `drafts/current_draft.md`
5. `results/master_editorial_packet_disability_wave.md`
6. `.hermes/plans/disability-wave-revision-plan.md`
7. `results/disability_wave_final_empirical_support_memo.md`
8. `results/composition_tension_resolution_memo.md`
9. `results/disability_wave_top12_validation_results.md`
10. `results/disability_wave_public_process_validation_pass2.md`
11. `results/disability_wave_noisy_queue_cleanup_memo.md`
12. `results/disability_wave_extra_compute_addendum.md`

If the next task is only quick orientation, the minimum viable set is:
- this memo
- `results/master_editorial_packet_disability_wave.md`
- `.hermes/plans/disability-wave-revision-plan.md`
- `drafts/current_draft.md`

## 1. Executive bottom line

The research phase has now matured enough that the next high-value step is draft revision, not broad new research collection.

The central final synthesis is:

The post-withdrawal disability-enforcement downturn is best understood as a layered pipeline failure. A dominant compositional shift toward pro se filings still explains most aggregate decline. But some within-group deterioration also appears, especially at the pleading gate in stronger represented subsets. The disability-wave coding explains why both can be true at once: many disputes are administratively legible in principle, yet they repeatedly fail in translation, theory selection, fact development, document assembly, jurisdictional triage, and authority-specific routing.

This supports the current note’s larger institutional argument, but it requires disciplined phrasing in two places:

- Composition remains dominant, but it is no longer safe to imply composition is the whole story.
- “Administrative invisibility” should now be framed as failed administrative capture and verification, not total factual absence.

The research does NOT justify:
- a new judicial-hostility thesis,
- a broad merits-collapse thesis,
- a structural redesign of the note,
- or a claim that reporting architecture alone would fix the disability docket.

## 2. What was completed

### 2.1 Main disability-wave tranche

A disability-wave OpenRouter coding run was completed and then fully repaired.

Final state:
- total disability-wave requests: 1330
- final resolved disability-wave records: 1330 / 1330
- orphan results: 0
- malformed parsed responses: 0
- hard errors after final repair: 0

This resolution required:
- initial full disability-wave run,
- reruns of the original hard-error tranche,
- a second rerun for filename-selection edge cases,
- and manual salvage of the final 2 unrecovered records.

### 2.2 Merge status

Final merge report:
- matched records: 1330 of 3198 database records
- orphan results: 0

Important clarification:
- The remaining 3198 - 1330 = 1868 records are not merge failures. They are outside the disability-wave subset or otherwise outside this tranche’s scope.

### 2.3 Additional memo work already completed

The following research outputs already exist and should be treated as part of the working package:

Core synthesis / planning
- `results/master_editorial_packet_disability_wave.md`
- `.hermes/plans/disability-wave-revision-plan.md`
- `results/disability_wave_final_empirical_support_memo.md`
- `results/disability_wave_note_facing_synthesis_v2.md`
- `results/composition_tension_resolution_memo.md`
- `results/disability_wave_extra_compute_addendum.md`

Public-process and doctrinal-gap work
- `results/public_process_follow_on_memo_v2.md`
- `results/public_process_raw_text_study_memo.md`
- `results/disability_wave_public_process_validation_pass2.md`

Validation / queue cleanup work
- `results/disability_wave_validation_priority_memo.md`
- `results/disability_wave_top12_validation_results.md`
- `results/disability_wave_noisy_queue_cleanup_memo.md`

Underlying merge/final result artifacts
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merged.json`
- `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_merge_report.md`

## 3. Most important final empirical findings

These are the main results a receiving LLM should treat as the safest empirical propositions.

### 3.1 The disability docket is not best described as a clean merits-failure docket

In the final resolved 1330-case disability-wave tranche:
- `TRANSLATION`: 268 cases (20.2%)
- `PROCEDURAL_GATEWAY`: 240 cases (18.0%)
- `MERITS_EVIDENCE`: 58 cases (4.4%)
- `FACTUAL_DETAIL`: 24 cases (1.8%)
- `NO_FAILURE_PLAINTIFF_WIN`: 374 cases (28.1%)

Combined:
- translation + procedural-gateway failures = 508 cases (38.2%)
- merits-evidence + factual-detail failures = 82 cases (6.2%)

Best use:
- The disability docket is dominated by failed conversion of grievances into viable claims, not by mature merits defeat.

### 3.2 The mechanism layer strongly supports a pipeline-failure story

Most common missing institutional functions:
- `THEORY_SELECTION`: 683 (51.4%)
- `FACT_DEVELOPMENT`: 681 (51.2%)
- `DOCUMENT_ASSEMBLY`: 480 (36.1%)
- `JURISDICTIONAL_TRIAGE`: 322 (24.2%)

Best use:
- Complaint-driven enforcement is failing not only because rights are hard to vindicate, but because institutions are failing to convert recognizable disputes into legally legible records and theories.

### 3.3 Many disability disputes are administratively legible in principle

Most common observable fact patterns:
- `NOTICE_OR_TIMELINE_RECORD`: 979 (73.6%)
- `DOCUMENTED_REQUEST`: 875 (65.8%)
- `PUBLIC_PROGRAM_RULE_OR_DECISION`: 452 (34.0%)
- `LEASE_OR_POLICY_TEXT`: 296 (22.3%)
- `MEDICAL_OR_PROVIDER_LETTER`: 277 (20.8%)
- `DENIAL_OR_NO_RESPONSE_RECORD`: 272 (20.5%)
- `HEARING_OR_GRIEVANCE_RECORD`: 250 (18.8%)
- `PHYSICAL_ACCESS_BARRIER`: 137 (10.3%)
- `INSPECTION_OR_MEASUREMENT_DATA`: 54 (4.1%)
- `NONE_APPARENT`: only 83 (6.2%)

Best use:
- The strongest formulation is qualified administrative invisibility. The recurring problem is not that facts are usually absent, but that agencies and intermediaries do not systematically capture, standardize, verify, and route recurring disability-relevant facts.

### 3.4 Public-process failure is substantial

`public_process_failure_flag = true` appears in 531 cases (39.9%).

Best use:
- A substantial share of the disability housing docket arises in process-heavy, authority-fragmented, often public or quasi-public settings.

### 3.5 The fixability coding supports modesty

Fixability / tier coding:
- `BOTH`: 714 (53.7%)
- `TIER2_INSTITUTIONAL_INTERMEDIATION`: 300 (22.6%)
- `NEITHER`: 278 (20.9%)
- `UNCLEAR`: 31 (2.3%)
- `TIER1_REPORTING_ARCHITECTURE`: 7 (0.5%)

Combined:
- `BOTH` + `TIER2_INSTITUTIONAL_INTERMEDIATION` = 1014 (76.2%)

Best use:
- Reporting and targeted verification are best defended as an administrative floor, not a full cure. The coding does not support a claim that disclosure alone would solve the disability docket.

## 4. What is validated enough for direct note use

These are strong enough to be used affirmatively in the note.

1. The final resolved disability-wave tranche is a clean 1330-record matched file with no orphan results, malformed parsed responses, or hard merge errors.
2. Translation and procedural-gateway failure together account for 38.2% of coded cases, while merits-evidence and factual-detail failures account for only 6.2%.
3. The most common missing institutional functions are theory selection, fact development, document assembly, and jurisdictional triage.
4. Many disputes are administratively legible in principle; only 6.2% of coded cases lack any apparent observable fact pattern.
5. Public-process failure is substantial rather than peripheral at 39.9% of the resolved tranche.
6. The fixability pattern supports floor-not-ceiling modesty: most cases appear responsive to a combination of reporting/verification plus intermediation, not reporting alone.
7. The aggregate downturn remains mostly compositional, but some within-group deterioration also appears, especially in stronger represented pleading-stage subsets.

## 5. What must be qualified or used cautiously

### 5.1 Represented-plaintiff recovery
Safe version:
- represented plaintiffs recover in aggregate from the P2 shock.

Required qualification:
- newer reanalysis also shows a drop from 69.0% to 52.3% among represented plaintiffs at MTD where Iqbal/Twombly is cited.

Rule:
- do not say represented plaintiffs simply held steady.

### 5.2 Composition story
Safe version:
- composition remains the dominant aggregate explanation.

Required qualification:
- composition is dominant, not exclusive.

### 5.3 Administrative invisibility
Safe version:
- disability enforcement remains administratively undercaptured.

Required qualification:
- many facts exist in recognizable form; the problem is failed capture and verification, not total invisibility.

### 5.4 Doctrinal-gap story
Safe version:
- upstream filtering thins doctrine-producing cases.

Required qualification:
- the coding does not prove a generalized doctrinal vacuum; high doctrinal-gap rows are rare.

### 5.5 Public-process examples
Safe version:
- public-process examples are useful as selective illustrations.

Required qualification:
- they should not become the note’s new center of gravity.

## 6. Validation findings the receiving LLM must respect

### 6.0 Practical evidence hierarchy

The receiving LLM should treat the research package using this hierarchy:

Tier 1 — safest direct support
- tranche-level distributions from the final resolved 1330-case file
- merge cleanliness / resolved status
- mechanism distributions that were not invalidated by later validation passes

Tier 2 — usable with explicit qualification
- public-process examples that were manually validated but still require narrow framing
- composition-plus-residual-within-group language
- observability findings framed as failed capture rather than total invisibility

Tier 3 — context only / holdout material
- early procedural orders
- service orders
- counsel-denial orders
- incomplete screening/recommit orders
- queue records that later validation flagged as weak public-process examples or likely false positives

Default rule:
- if a proposition can be supported at the tranche/body level, prefer that over any single case example
- if a single-case example is used, use a validated case and describe it narrowly

### 6.1 Top-12 validation result
The top-12 validation pass found substantial queue noise.

Key outcome:
- 8 of the 12 checked records were early procedural orders or otherwise non-merits records
- 7 should be kept only as context/non-merits tracking
- 1 likely false positive should be recoded out of the FHA merits pool
- only 1 record in the twelve (`Sykes`) is a strong, clean substantive public-process merits example
- `Wissman` and `Goodwin` are usable only with narrower mechanism descriptions
- `Capel` remains provisional unless validated against the district-court opinion

Rule:
- do not treat queue-level examples as affirmative support unless they have been manually validated.

### 6.2 Noisy queue cleanup
The following were reviewed and should be held out from substantive analytics and used only as context:
- `Jacobson`
- `Rosa`
- `Chapman`
- `Sandles`
- `Shepherd`
- `Avila`

Reason:
- these are service orders, counsel-denial orders, or incomplete screening-stage orders that do not adjudicate substantive FHA issues.

### 6.3 Second public-process validation pass
Validated public-process expansion set results:

Strong keep
- `Jackson`
- `Drummer`

Strong but needs recoding
- `Fedynich`

Usable with caution / mechanism recode
- `Cooper`

Weak for the disability-centered public-process story
- `Johnson`

Likely false positive / should be recoded out of core FHA public-process counts
- `Peters`

Net implication:
- the public-process lane is real and important, but the bench of validated examples is narrower than the raw queue suggested.

### 6.4 Best validated example set for note use

If the receiving LLM needs a short approved example list, use this:

Strongest clean example
- `Sykes`

Best public-process examples after additional validation
- `Jackson`
- `Drummer`
- `Fedynich` (but only if described as a disability/nexus translation failure rather than request absence)

Secondary / careful-use examples
- `Cooper`
- `Wissman`
- `Goodwin`

Do not rely on as core examples
- `Johnson`
- `Peters`
- `Jacobson`
- `Rosa`
- `Chapman`
- `Sandles`
- `Shepherd`
- `Avila`

Likely false positive / should be recoded out of core FHA public-process counts
- `Peters`

Net implication:
- the public-process lane is real and important, but the bench of validated examples is narrower than the raw queue suggested.

## 7. Best current public-process examples

The receiving LLM should treat the following as the best validated or near-validated public-process examples:

### Strongest clean example
- `Sykes`
  - strongest validated example of administratively observable facts that never become a legally sufficient FHA claim

### Strong examples from later validation
- `Jackson`
  - voucher context, wrong-defendant / institutional-attribution failure
- `Drummer`
  - rich administrative record, complaint structurally disorganized, defendant-specific pleading failure in public-housing setting
- `Fedynich`
  - repeated requests existed; failure is better understood as disability/nexus translation failure, not request absence

### Use more cautiously
- `Cooper`
  - public-housing/FHA retaliation context, but the mechanism is causation/knowledge failure rather than request-articulation failure
- `Wissman`
- `Goodwin`
  - usable only with narrower mechanism descriptions

### Do not rely on as core examples
- `Johnson`
- `Peters`
- the cleaned noisy/non-merits rows listed above

## 8. Revision priorities for the current draft

The research package supports a narrow, sequenced pass rather than a broad rewrite.

Priority order:
1. Part II.C
2. Part II.B
3. Part III.D
4. Abstract and Introduction
5. Part II.D
6. light synchronization in Parts III.A-C and IV.A-D
7. Conclusion

### 8.1 Part II.C — highest priority
Required move:
- keep composition as the lead claim,
- replace “the key pattern is compositional” with “the dominant aggregate pattern is compositional,”
- add the residual qualification that some within-group deterioration also appears,
- add a mechanism paragraph using the disability-wave counts,
- and replace any clean recovery slogan with a layered pipeline-failure formulation.

### 8.2 Part II.B — second priority
Required move:
- sharpen the distinction between total invisibility and failed administrative capture,
- insert observability counts,
- shift rhetoric from “cannot see” to “does not systematically collect, standardize, and verify.”

### 8.3 Part III.D — third priority
Required move:
- preserve the narrow first-wave reporting floor,
- add explicit candor that reporting alone is insufficient,
- use fixability coding to support floor-not-ceiling modesty.

### 8.4 Abstract and Introduction — fourth priority
Required move:
- sync front matter to the revised Part II account,
- preview a two-layer pipeline failure,
- avoid implying complete represented-plaintiff stability or total factual invisibility.

## 9. Recommended language posture

The receiving LLM should prefer these formulations:

Use
- dominant aggregate pattern is compositional
- qualified administrative invisibility
- failed administrative capture and verification
- failed conversion of grievances into viable claims
- reporting and verification as an administrative floor
- floor, not ceiling

Avoid
- pure composition is the whole story
- represented plaintiffs fully recovered, full stop
- total factual invisibility
- broad merits-collapse thesis
- disclosure alone would fix the system

## 10. What additional research remains worthwhile

Additional research is now optional, not necessary.

Best remaining bounded research, if explicitly requested:
1. more selective public-process validation,
2. small recode/holdout cleanup of validated noisy/public-process records,
3. limited additional raw-text checks for edge cases.

Not recommended as the next default move for this note:
- broad new empirical collection,
- full state-registry comparative project,
- broad non-disability corpus expansion.

Why:
- the note already has enough research support for revision,
- and additional broad research risks scope drift.

## 11. Relation to FUTURE_RESEARCH_DESIGN.md

`FUTURE_RESEARCH_DESIGN.md` is important, but it should be treated as a future article-length or appendix-scale research design, not the next mandatory step for this note.

What is useful from it right now:
- LIHTC lacks unit-level accessibility tracking,
- court-ordered registries often fail in implementation,
- Massachusetts’s voluntary model appears better than remedial-order models,
- administrative capacity is the binding constraint,
- the absence of federal feature-verification infrastructure supports the verification-mismatch thesis.

What should NOT happen unless expressly intended:
- the receiving LLM should not turn the note into a full Massachusetts/Connecticut/control-state difference-in-differences project.

## 12. Practical instructions for the next LLM

### 12.1 If the next task is draft revision

Do this:
1. Read the control-plane files first.
2. Read `drafts/current_draft.md` in full.
3. Use this memo plus `master_editorial_packet_disability_wave.md` and `disability-wave-revision-plan.md` as the operative research package.
4. Revise Part II first, especially Part II.C and Part II.B.
5. Prefer tranche-level findings over single-case illustrations.
6. Use only validated examples for affirmative support.
7. Preserve the current architecture unless a higher-priority instruction authorizes redesign.

Do not do this:
- do not turn the note into a general judicial-hostility paper
- do not overstate within-group deterioration as the main story
- do not present public-process examples as if there were a large bench of equally validated merits cases
- do not use noisy early-procedural queue entries as substantive support
- do not convert the note into the large Massachusetts/Connecticut registry project

### 12.2 If the next task is planning only

- Use `.hermes/plans/disability-wave-revision-plan.md` as the operative roadmap.
- Treat the task as a surgical narrowing / empirical-firming pass, not a redesign exercise.

### 12.3 If the next task is editorial synthesis or comparison of proposal options

- Start from `results/master_editorial_packet_disability_wave.md` and this memo together.
- Use the evidence hierarchy in section 6 of this memo.
- Distinguish sharply between validated tranche-level findings and queue-level or case-level illustrations.

### 12.4 If the next task is more research rather than revision

Only do more research if explicitly requested.
Preferred bounded follow-ons:
- additional selective validation,
- limited recode / holdout cleanup,
- narrow public-process raw-text checks.

Avoid by default:
- broad new corpus expansion,
- full state-registry comparative build-out,
- large off-thesis empirical modules.

## 13. Most important one-paragraph synthesis for reuse

If you need one paragraph to orient another LLM quickly, use this:

The final resolved disability-wave research package supports a narrower but stronger empirical story than a broad merits-collapse or judicial-hostility account. In the fully resolved 1330-case disability-wave tranche, translation and procedural-gateway failures together account for 38.2% of cases, while merits-evidence and factual-detail failures account for only 6.2%. The most common missing institutional functions are theory selection, fact development, document assembly, and jurisdictional triage. At the same time, many disputes are administratively legible in principle: notice/timeline records, documented requests, public-program decisions, policy texts, hearing records, and denial records recur at high rates, while only 6.2% of cases lack any apparent observable fact pattern. The best interpretation is therefore a layered pipeline-failure story: composition remains the dominant aggregate explanation, some within-group deterioration also appears, and the central practical failure is not total invisibility but failed administrative capture, verification, and conversion of recurring disability-relevant facts into mature claims.
