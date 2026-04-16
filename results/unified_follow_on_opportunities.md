# Unified Follow-On Opportunities

This file is a scaffolding memo for the overnight run. It ranks bounded next studies that can start immediately from the citation baseline and raw-text inventory outputs.

## Input status

- Citation baseline: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_normalized_citations.json`
- Raw-text inventory: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_raw_text_target_inventory.json`
- Screened records in citation baseline: 2522
- Ambiguous pleading-loss targets: 250
- Public-defendant process targets: 250
- Open-textured citation-rich targets: 250
- Citation-differential exemplars: 113
- Tiny-summary reopen queue: 250

## Ranked opportunities

### 1. Pro se pleading-mechanism divergence memo (HIGH, score 10.55)

Evidence:
- Iqbal/Twombly appears in 780/1391 pro se citation-bearing records (56.1%).
- Iqbal/Twombly appears in 328/1129 represented records (29.1%).
- Gap between the two groups: 27.0 percentage points.
- Raw-text-ready ambiguous pleading-loss inventory already contains 819 cases, with 17 raw-text hits.

Suggested next steps:
- Take the top 40 ambiguous pleading-loss cases and split them by pro se status.
- Code whether dismissal turns on missing facts, wrong doctrinal hook, or public-process framing failure.
- Cross-check whether Iqbal/Twombly is doing actual work or just boilerplate.

Suggested output: Short note-facing memo plus appendix table comparing pro se and represented pleading-failure mechanisms.

### 2. Public-defendant process-failure subset study (HIGH, score 9.8)

Evidence:
- Public-defendant process bucket contains 413 cases.
- 33 of those already have resolvable raw text.
- Dominant defendant type in the bucket: HOUSING_AUTHORITY.
- This subset is directly aligned with the overnight plan's public-defendant process-refinement lane.

Suggested next steps:
- Start with the top 30 scored public-process cases.
- Tag whether the court focuses on request clarity, interactive-process breakdown, eligibility proof, or institutional authority fragmentation.
- Compare municipalities and housing authorities separately once the raw-text review lands.

Suggested output: Targeted report feeding the public-defendant process-failure refinement and tractability sections.

### 3. Citation-gap / doctrinal-omission memo for open-textured cases (HIGH, score 9.33)

Evidence:
- Open-textured, citation-rich inventory contains 386 cases.
- 42 of them have raw-text paths already resolved.
- These are the best candidates for the plan's citation-gap target-group report because they have enough authority density to inspect what is missing, not just what is cited.
- Top authority overall remains Ashcroft v. Iqbal.

Suggested next steps:
- Read the top 25 open-textured cases by score.
- Mark whether the opinion cites procedural authorities without pairing them with FHA-specific accommodation or zoning precedents.
- Group resulting omissions by plaintiff type and defendant type.

Suggested output: Doctrinal-gap memo that can be tied directly to plaintiff-side omission and AFFH framing arguments.

### 4. Citation-differential exemplar packet (MEDIUM-HIGH, score 8.28)

Evidence:
- Citation-differential exemplars identified: 113.
- Raw text available for 21 of them.
- These cases already show mixed procedural/substantive citation profiles, which makes them efficient teaching examples for a morning memo.

Suggested next steps:
- Select 12 exemplars spanning multiple circuits and plaintiff types.
- Extract 1-2 paragraph doctrinal narratives for each case showing how pleading authorities crowd out or coexist with substantive FHA law.
- Use the packet as a bridge between citation tables and raw-text close reading.

Suggested output: Exemplar appendix or synthetic classification memo usable in the note's doctrinal discussion.

### 5. Tiny-summary reopening queue (MEDIUM, score 7.7)

Evidence:
- Tiny-summary bucket contains 250 screened cases using the <=700-character threshold.
- 5 already map to raw text.
- This is the cleanest queue for improving structured-data confidence if the overnight autopsy returns ambiguous results.

Suggested next steps:
- Reopen the first 50 tiny-summary cases with raw text.
- Prioritize the intersection with ambiguous pleading losses and public-process cases.
- Use these as the first disagreement-rerun tranche if any autopsy field underperforms validation.

Suggested output: Validation support queue rather than a standalone thesis memo.

## Immediate default recommendation

If only one additional study can be launched before the batch returns, start with the pro se pleading-mechanism divergence memo and use the ambiguous pleading-loss inventory as the sampling frame.

## Queue logic

- If autopsy validation is strong, prioritize the public-defendant process and citation-gap memos.
- If autopsy validation is mixed, use the tiny-summary queue and the exemplar packet as the first raw-text rerun tranche.
- If morning time is short, convert the top-ranked opportunity plus the exemplar packet into a single synthetic memo rather than several separate products.
