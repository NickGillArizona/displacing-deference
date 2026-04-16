# Final Research Batch Handoff — 2026-04-16

Audience
- another agent deciding how to edit the paper
- especially useful for Claude Code / another LLM doing revision triage against `v89_A` and `v89_B`

Scope
- This memo summarizes the completed Hermes research batch.
- It is meant to reduce re-reading, not replace the underlying artifacts.
- It focuses on what is safe to use, what is provisional, and what should drive editing choices.

Current draft targets
- `note_v89_A.md`
- `note_v89_B.md`

Bottom line
- The research batch is complete and broadly handoff-ready.
- No additional broad research is necessary before another agent decides how to edit the paper.
- The right next move is editorial synthesis/revision, not more large-scale research collection.

Overall verdict
- READY WITH CAVEATS

Read order for the next agent
1. `FINAL_HANDOFF_TO_NEXT_AGENT_2026-04-16.md`
2. this file
3. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/pro_se_mechanism_divergence_analysis.md`
4. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/public_defendant_process_failure_analysis.md`
5. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/ahs_2023_accessibility_analysis.md`
6. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/lihtc_accessibility_audit_analysis.md`
7. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/circuit_district_deep_dive_analysis.md`
8. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/loper_bright_fha_citation_check_2025_2026.md`
9. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/nspire_ufas_crosswalk_analysis.md`
10. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/qap_accessibility_update_analysis.md`
11. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/australia_sda_analysis.md`
12. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/hud_annual_report_longitudinal_audit.md`
13. `Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/design_construction_private_enforcement_analysis.md`

Completed task inventory
1. `results/disability_wave_completion_memo.md`
2. `scripts/pro_se_mechanism_analysis.py`
   - `results/pro_se_mechanism_divergence_results.json`
   - `results/pro_se_mechanism_divergence_analysis.md`
3. `scripts/public_defendant_analysis.py`
   - `results/public_defendant_process_failure_results.json`
   - `results/public_defendant_process_failure_analysis.md`
4. `scripts/ahs_2023_accessibility_analysis.py`
   - `results/ahs_2023_accessibility_results.json`
   - `results/ahs_2023_accessibility_analysis.md`
5. `scripts/lihtc_accessibility_audit.py`
   - `results/lihtc_accessibility_audit_results.json`
   - `results/lihtc_accessibility_audit_analysis.md`
6. `scripts/state_complaint_panel.py`
   - `results/state_complaint_panel_results.json`
   - `results/state_complaint_panel_analysis.md`
7. `scripts/circuit_district_deep_dive.py`
   - `results/circuit_district_deep_dive_results.json`
   - `results/circuit_district_deep_dive_analysis.md`
   - refreshed `results/extended_doctrinal_analysis.json`
8. `results/loper_bright_fha_citation_check_2025_2026.md`
9. `results/scooping_defense_check_april2026.md`
10. `results/nspire_ufas_crosswalk.json`
    - `results/nspire_ufas_crosswalk_analysis.md`
11. `scripts/qap_accessibility_2025_2026_scan.py`
    - `results/qap_accessibility_2025_2026.json`
    - `results/qap_accessibility_update_analysis.md`
12. `results/disclosure_effect_meta_analysis.md`
13. `results/australia_sda_analysis.md`
14. `results/hud_annual_report_longitudinal_audit.md`
15. `results/design_construction_private_enforcement_analysis.md`

Highest-confidence findings to use in editing
1. Disability-wave completion / scope
- The disability-wave tranche is complete.
- The old “roughly 440 remaining” assumption was stale.
- Use `results/disability_wave_completion_memo.md` for that closure point.

2. Pro se vs represented pleading-failure divergence
- Use `results/pro_se_mechanism_divergence_analysis.md`.
- The analysis now covers the full screened disability pleading-loss universe, not just the original disability-wave subset.
- Safe takeaway:
  - pro se failures are much more translation-heavy
  - represented failures skew more toward gateway/jurisdictional problems
- This is a strong support memo for the pipeline-failure / intermediation story.

3. Public-defendant process failures
- Use `results/public_defendant_process_failure_analysis.md`.
- Safe takeaway:
  - the proposed reporting architecture is a strong evidentiary fit for many public-defendant losses,
  - but reporting alone is not the full fix; Tier 2 / intermediation still matters.

4. 2023 AHS accessibility evidence
- Use `results/ahs_2023_accessibility_analysis.md`.
- Safe takeaway:
  - 2023 supports strong accessibility-related proxy analysis,
  - but 2023 lacks the dedicated accessibility topical module needed for a full 2011/2019-style replication.
- Use the no-step-entry and HMRACCESS findings; do not oversell exact Bo'sher replication.

5. LIHTC accessibility black hole
- Use `results/lihtc_accessibility_audit_analysis.md`.
- Safe takeaway:
  - the public LIHTC file has no accessible-unit inventory,
  - TRGT_DIS is not an accessibility count,
  - there is a large observed-proxy perimeter gap.
- Keep the overlap language careful: observed proxy, not definitive Section 504 applicability.

6. NSPIRE is not accessibility compliance
- Use `results/nspire_ufas_crosswalk_analysis.md`.
- This is one of the cleanest note-usable outputs.
- Quote-ready bottom line is already in the memo.

7. Loper Bright correction
- Use `results/loper_bright_fha_citation_check_2025_2026.md`.
- This supersedes any older “no FHA-specific Loper Bright citation” claim.
- Safe takeaway:
  - at least Watts and Twyman are in-window substantive FHA opinion hits,
  - Heimkes is a procedural/non-substantive hit.

8. D&C private-enforcement barriers
- Use `results/design_construction_private_enforcement_analysis.md`.
- Safe takeaway:
  - the strongest documented barriers are standing/particularization, accrual/limitations, and technical proof/discovery cost,
  - not primarily mootness or Rule 23.

Strong but caveated findings
1. Circuit/district deep dive
- Use `results/circuit_district_deep_dive_analysis.md`.
- Strongest use:
  - district-level concentration and pleading-gate geography.
- Weaker use:
  - absolute negative claims about single judges or post-2025 appointees.
- Keep judge/appointee findings qualified.

2. State complaint panel
- Use `results/state_complaint_panel_analysis.md`.
- Strong use:
  - pre-launch baseline and comparators.
- Do not claim a post-2021 causal registry effect from this file.
- The memo itself says no defensible post-launch DiD is available.

3. QAP update (p11)
- Use `results/qap_accessibility_update_analysis.md` only as current-best/provisional.
- This is the least settled artifact in the batch.
- Remaining manual-review/error states are explicitly flagged.
- Good for directional claims; risky for hard final counts unless another agent chooses to clean it further.

4. Australia SDA comparator
- Use `results/australia_sda_analysis.md` as an administrability comparator.
- Do not use it as if it proves direct transferability to HUD.
- Resident-cap and small-scale findings are proxies, not proof of community-integration outcomes.

5. HUD annual report longitudinal audit
- Use `results/hud_annual_report_longitudinal_audit.md`.
- Safe takeaway:
  - disability data appears repeatedly but inconsistently,
  - the problem is not total absence but unstable formats, publication gaps, and incomplete recoverability.
- Slight caveat: some support work was originally staged via `/tmp` artifacts rather than a fully persisted repo subpackage.

Cross-file cautions the next agent must know
1. p1 vs p2 are different universes, not conflicting results.
- p1 = disability-wave subset completion.
- p2 = full screened disability pleading-loss universe.

2. p5 and p11 are not automatically synchronized.
- p5 uses the reconstructed Kelsey 2023 baseline.
- p11 is the newer 2025–2026 scan and still somewhat provisional.
- Do not merge those counts casually.

3. p3 is subset-bounded.
- It is very useful, but it is not a fully expanded 413-case final recode.

4. p8 should override older contrary language.
- If another memo/draft still says “no FHA-specific Loper Bright citation,” treat that as outdated.

Artifacts that should be treated as provisional rather than frozen
- `results/qap_accessibility_2025_2026.json`
- `results/qap_accessibility_update_analysis.md`
- secondarily: judge/appointee parts of p7
- secondarily: any use of p13 beyond feasibility/administrability comparison

What additional research is still necessary?
- None is necessary before an editing agent decides how to revise the paper.
- Only optional targeted follow-up remains.

Optional follow-up, if another agent wants to tighten the record further
1. synchronize p5 with p11 so LIHTC perimeter numbers use the newer QAP categories
2. extend p3 beyond the coded subset if public-defendant coverage becomes central to the edit strategy
3. persist p14 support artifacts into the repo if a fully reproducible archive trail is important
4. finalize p11 manual-review states if the edit strategy leans heavily on current-state QAP counts

Recommended editorial use strategy for the next agent
If the next agent is deciding how to edit v89_A / v89_B, prioritize:
1. p2 + p3 for the pipeline-failure / intermediation / reporting-floor argument
2. p10 + p5 for the observability / verification mismatch argument
3. p4 for current accessibility-conditions support
4. p8 for legal-update cleanup
5. p15 for design-and-construction underenforcement / complaint-inadequacy framing
6. p11 and p13 only as bounded feasibility/comparator support

Do not let the next agent:
- treat p11 as fully final without noting unresolved states
- treat p13 as a direct transplant model
- overstate p7 judge/appointee negatives
- revive the old “no FHA-specific Loper Bright citation” claim

One-line handoff summary
- The research is complete enough for revision now; the strongest themes are verification mismatch, pipeline failure, request/log/record deficits, and the limits of existing HUD observability systems, with a few clearly marked provisional artifacts (mainly p11).