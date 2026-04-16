# Disability-Wave R1 Reprocess and Next-Research Memo

Generated from the completed OpenRouter disability-wave run (`unified_overnight_openrouter_disability_wave_r1`).

## Final run state

- Total requests: 1330
- Successful classifications: 1256
- Hard errors: 74
- Malformed parsed outputs: 0
- Pending: 0
- Merge status: 1256 result rows matched onto the unified database with 0 orphan results

Important interpretation: the `1942` unmatched records in the merge report are not merge failures. They are the rest of the full 3,198-record unified database outside the disability-wave classification subset.

## What clearly needs reprocessing

### 1. The 74 hard-error rows

These are the only true must-rerun cases from the completed disability-wave batch.

Failure tranches:
- Legacy 1400-cap truncation/empty-output errors: 64
- New 2400-cap failures: 9
- Empty on both primary and escalation models: 33
- Truncated with partial JSON present: 41

Operational implication:
- The first rerun tranche should be all 74 error rows.
- Within that tranche, the 41 rows with partial JSON are the easiest salvage targets.
- The 33 rows with empty output from both models are the hardest failures and likely need a changed prompt/output strategy, not just another identical rerun.

### 2. Low-confidence but successful rows (validation rerun candidates)

Count: 54

Why they matter:
- These are not missing data, but they are the most obvious quality-control tranche among successful rows.
- Their mechanisms are dominated by `UNCLEAR` and `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`, which suggests ambiguity rather than ordinary easy cases.

Top low-confidence mechanisms:
- `UNCLEAR`: 28
- `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`: 13
- `JURISDICTION_OR_STANDING`: 6

### 3. High raw-text-review-priority rows

Count: 132

Why they matter:
- The model itself is flagging these as the most likely places where structured-record-only coding is insufficient.
- This is the best queue for a second-stage raw-text close-reading project.

Top mechanisms in the high-review queue:
- `UNCLEAR`: 24
- `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`: 20
- `REQUEST_NOT_ALLEGED`: 20
- `ELEMENTS_NOT_TIED_TO_FACTS`: 16

### 4. Public-process + doctrinal-gap rows

Count: 220

Why they matter:
- This is the strongest substantive follow-on queue for the note.
- It is tightly aligned with the note’s claim that disability failures often reflect institutional-process and enforcement-pipeline problems rather than simple merits collapse.

Top mechanisms in this queue:
- `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`: 35
- `ELEMENTS_NOT_TIED_TO_FACTS`: 27
- `JURISDICTION_OR_STANDING`: 26
- `REQUEST_NOT_ALLEGED`: 25
- `MIXED`: 20

## What the successful results are already saying

### Core family distribution
- `NO_FAILURE_PLAINTIFF_WIN`: 353
- `TRANSLATION`: 253
- `PROCEDURAL_GATEWAY`: 230
- `CAUSAL_LINK`: 92
- `NO_FAILURE_DEFENDANT_WIN`: 76
- `ELEMENT_MISMATCH`: 67
- `MIXED`: 66
- `MERITS_EVIDENCE`: 55
- `UNCLEAR`: 41
- `FACTUAL_DETAIL`: 23

### Mechanism signals
Top mechanisms:
- `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS`: 383
- `JURISDICTION_OR_STANDING`: 146
- `ELEMENTS_NOT_TIED_TO_FACTS`: 117
- `REQUEST_NOT_ALLEGED`: 108
- `UNCLEAR`: 99
- `MIXED`: 88
- `DISABILITY_NEXUS_MISSING`: 56
- `ADVERSE_ACTION_NOT_CONNECTED`: 54
- `NO_COGNIZABLE_FHA_THEORY`: 45

### Institutional-function-missing signals
Top signals:
- `THEORY_SELECTION`: 647
- `FACT_DEVELOPMENT`: 642
- `DOCUMENT_ASSEMBLY`: 460
- `JURISDICTIONAL_TRIAGE`: 309
- `NONE_APPARENT`: 281

This strongly supports the note’s current framing that the disability docket is not best understood as a clean merits-rejection story. A large share of the coded failures look like translation, pleading, documentation, and triage failures.

### Administrative-observability signals
Top observable patterns:
- `NOTICE_OR_TIMELINE_RECORD`: 941
- `DOCUMENTED_REQUEST`: 832
- `PUBLIC_PROGRAM_RULE_OR_DECISION`: 425
- `LEASE_OR_POLICY_TEXT`: 275
- `MEDICAL_OR_PROVIDER_LETTER`: 264
- `DENIAL_OR_NO_RESPONSE_RECORD`: 256
- `HEARING_OR_GRIEVANCE_RECORD`: 242

This matters for the note because many disputes appear administratively legible in principle. The bottleneck often seems to be institutional translation and enforcement conversion, not total factual invisibility.

### Confidence / review / gap signals
- Confidence: HIGH 432 / MEDIUM 770 / LOW 54
- Raw-text review priority: HIGH 132 / MEDIUM 985 / LOW 139
- Doctrinal gap: HIGH 18 / MEDIUM 385 / LOW 576 / NONE 277
- Public-process flag true: 503 rows (40.0% of successful classifications)
- Tier1/Tier2 fixability:
  - `BOTH`: 681
  - `TIER2_INSTITUTIONAL_INTERMEDIATION`: 284
  - `NEITHER`: 258

This is promising for the note’s reinforcement thesis. Much of the classified docket is coded as potentially responsive to reporting/verification plus institutional-intermediation support rather than direct doctrinal revolution.

## Prioritized reprocessing plan

### Do now
1. Rerun the 74 hard-error rows with a revised output strategy.
2. Build a validation tranche from the 54 low-confidence rows.
3. Build a raw-text review tranche from the 132 high-review rows.

### Do next
4. Launch a targeted public-process doctrinal-gap study on the 220 public-process + medium/high-gap rows.
5. Build a note-facing memo from the successful disability-wave results before doing broader corpus expansion.

### Defer unless needed
6. Full all-screened recoding of the entire non-disability corpus.
7. Broad off-thesis expansion into unrelated FHA subdomains.

## Best additional compute to burn next

### A. Error-only rerun with a changed output contract
Value: highest
Why:
- Directly improves completion coverage.
- Small queue (74) with obvious payoff.
- Especially worthwhile for the 41 partial-JSON truncation rows.

### B. Raw-text second-pass on high-review and low-confidence disability cases
Value: very high
Why:
- Produces the strongest validation layer for the new schema.
- Most likely to generate note-usable case studies.
- Best targets: intersection of HIGH review, LOW confidence, and public-process/gap flags.

### C. Public-process refinement study
Value: very high
Why:
- Closest fit with the note’s institutional and reinforcement claims.
- The 220-row public-process + gap queue is large enough to support a serious memo or appendix.

### D. Matched non-disability comparison autopsy
Value: medium-high
Why:
- Could sharpen whether the observed translation/gateway pattern is disability-specific or just general FHA pro se attrition.
- Better than a full all-screened run if compute should stay thesis-aligned.

### E. Citation-gap / doctrinal-omission close-reading using the new disability-wave outputs
Value: medium-high
Why:
- Best for linking empirical findings to the doctrinal sections of the note.
- Should be narrower than a giant recoding pass; use the public-process and high-gap queues first.

## Overall judgment

The main disability-wave run succeeded well enough that the next work should not be “rerun everything.”

The correct approach is:
- reprocess the 74 true failures,
- validate the 54 low-confidence and 132 high-review rows,
- and spend remaining compute on the public-process / doctrinal-gap lanes that best strengthen the note’s existing thesis.

The biggest mistake now would be launching a broad, expensive corpus expansion before harvesting the note-facing value from the successful disability-wave output already on disk.
