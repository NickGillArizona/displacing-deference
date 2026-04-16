# Overnight Synthesis Memo (Pre-Batch Return)

## What tonight has already accomplished

The overnight infrastructure has already produced a usable pre-batch package from existing `results/` and `data/2/` outputs, even though the Anthropic batch itself has not yet returned.

Completed artifacts already on disk:
- Citation baseline memo: `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/unified_overnight_citation_baseline.md`
- Raw-text target inventory: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_raw_text_target_inventory.json`
- Validation sample: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_overnight_validation_sample.json`
- Baseline tables: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_overnight_baseline_tables.json`
- Unified stats report/data: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_stats_report.md` and `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_stats.json`
- Batch request scaffold/meta: `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_overnight_requests.jsonl` and `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/unified_overnight_batch_meta.json`

Operationally, that means the run already has:
- a normalized citation map for the screened FHA corpus,
- a raw-text-availability inventory showing which promising sub-queues can be worked immediately,
- a balanced 60-case validation sample,
- and a 50-record batch payload prepared for when Anthropic credits/API execution are available again.

## What the current outputs show

### 1. The screened corpus is large enough to support note-facing synthesis now
- Screened cases analyzed: 2522
- Cases with at least one citation: 2493
- Raw citation mentions: 10337
- Raw unique citation strings: 4924
- Normalized unique authorities: 4441

This is already enough to support descriptive doctrinal synthesis before any batch autopsy results return.

### 2. Procedural authorities dominate the citation environment
Top normalized authorities overall: Ashcroft v. Iqbal (1013), Bell Atlantic Corp. v. Twombly (964), McDonnell Douglas Corp. v. Green (109), Havens Realty Corp. v. Coleman (106), City of Cleburne v. Cleburne Living Center (98).

The current citation picture strongly supports a gatekeeping story: Iqbal and Twombly are the two dominant authorities by a very large margin, with substantive FHA authorities appearing much further down the list. That gives the note a present-tense empirical basis for saying that much of the disability FHA docket is being filtered through procedural sufficiency doctrine rather than developed through FHA-specific merits law.

### 3. The disability docket remains plaintiff-hostile in the post-Loper periods
From `data/2/unified_stats.json` / `unified_stats_report.md`:
- Disability cases in the screened corpus: 1720 of 2522 screened cases.
- Dated disability cases: 1191.
- Strict plaintiff win rate fell from 18.0% in P1 to 7.8% in P2 and 10.7% in P3.
- Broad plaintiff win rate fell from 30.0% in P1 to 20.7% in P2 and 18.9% in P3.

That means the preexisting empirical claim is not just that disability cases dominate the corpus, but that plaintiff-side success remains weak after the doctrinal/administrative transition points the note cares about.

### 4. Pro se status looks central, not incidental
From the same stats outputs:
- Known pro se share in dated disability cases: 64.8% (772 of 1191).
- Pro se strict win rate: 5.3%.
- Represented strict win rate: 32.1%.
- In P3 specifically, pro se share rises to 76.7%.

That makes pro se pleading failure one of the most usable immediate explanations for the baseline’s procedural-authority dominance.

### 5. Defendant type matters in a way that is useful for the note’s institutional story
Selected strict plaintiff win rates from the current stats outputs:
- Fair-housing-organization plaintiffs: 51.6%
- Group-home-operator plaintiffs: 26.9%
- Individual-tenant plaintiffs: 10.8%
- Housing-authority defendants: 4.8%
- Government defendants: 0.0%

The immediate note-facing takeaway is that individual disability plaintiffs fare far worse than institutional plaintiffs, and public/institutional defendants are among the hardest targets. That aligns well with an argument about institutional process failures and plaintiff-side tractability limits.

### 6. There is already a workable raw-text queue even without more credits
From `unified_raw_text_target_inventory.json`:
- Raw text resolved for 205 of 2522 screened cases.
- Exported buckets currently ready for note-facing follow-on work:
  - Ambiguous pleading losses: 250 exported / 7 with raw text already mapped.
  - Public-defendant process cases: 250 exported / 33 with raw text.
  - Open-textured citation-rich cases: 250 exported / 42 with raw text.
  - Citation-differential exemplars: 113 exported / 21 with raw text.
  - Tiny-summary reopen queue: 250 exported / 5 with raw text.

So the run is not blocked from producing useful memo work; it is only blocked from expanding the batch-dependent layer.

### 7. Validation design is already in place
The validation sample is balanced across eight useful buckets:
- pro_se_pleading_losses: selected 8 of 981 eligible.
- represented_pleading_losses: selected 8 of 274 eligible.
- public_defendant_process_cases: selected 8 of 392 eligible.
- institutional_wins: selected 8 of 159 eligible.
- design_and_construction_technical_cases: selected 8 of 59 eligible.
- open_textured_cases: selected 8 of 200 eligible.
- disability_controls: selected 6 of 1721 eligible.
- non_disability_controls: selected 6 of 801 eligible.

This matters because any morning memo can already distinguish between what is a baseline finding and what is awaiting confirmation from the validation/autopsy lane.

### 8. Batch execution is prepared but not yet returned
From `unified_overnight_batch_meta.json`:
- Model configured: claude-haiku-4-5
- Selected records in current payload: 50
- Request lines prepared: 50
- Batch meta generated at: 2026-04-15T06:21:24.562507+00:00

At the moment, the overnight repo `results/` folder contains the citation-baseline output but no downloaded batch-results artifact. Given the blocked Anthropic-credit situation, the right framing for tomorrow morning is: the preparation work succeeded, the queueing/scaffolding work succeeded, and the batch-dependent enrichment layer is the only missing piece.

## Bottom-line note-facing synthesis

Before the batch returns, tonight’s outputs already support three defensible propositions for the note:
1. Disability FHA litigation is citation-dense but procedurally dominated, with Iqbal/Twombly vastly outpacing FHA-specific merits authorities.
2. The plaintiff-hostility story is especially acute for pro se and individual-tenant cases, which helps explain why the disability docket can be large yet still undergenerate plaintiff-favorable doctrine.
3. The public-defendant / housing-authority subset appears especially difficult for plaintiffs, which makes institutional-process analysis a productive next note-facing lane even without any new Anthropic output.

## Current blocker

The only material blocker is the Anthropic-credit/API return path. The prep artifacts are ready, but no batch-return file is yet present in `results/`. Until credits are restored and the batch can run/download, the highest-value work is memo synthesis from the existing baseline, stats, inventory, and resolved raw-text subsets.

## Companion queue memo

For the ranked offline-first queue, see `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/results/unified_follow_on_opportunities.md` and the companion note-facing research queue generated alongside this memo.
