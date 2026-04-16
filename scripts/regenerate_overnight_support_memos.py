#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import os

REPO_NAME = "Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH"
DEFAULT_WORKSPACE = Path(
    os.environ.get("NOTE_WORKSPACE", Path(__file__).resolve().parents[2])
)


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_baseline_metrics(text: str) -> dict:
    metrics = {}
    for key in [
        "Screened cases analyzed",
        "Cases with at least one citation",
        "Raw citation mentions",
        "Raw unique citation strings",
        "Normalized unique authorities",
    ]:
        match = re.search(rf"{re.escape(key)}: (\d+)", text)
        if match:
            metrics[key] = int(match.group(1))

    overall_table = re.search(
        r"## Top normalized authorities overall\n\n\| Authority \| Mentions \|\n\|---\|---:\|\n(?P<body>.*?)(?:\n## |\Z)",
        text,
        re.S,
    )
    top_rows = []
    if overall_table:
        for line in overall_table.group("body").strip().splitlines():
            m = re.match(r"\|\s*(.*?)\s*\|\s*(\d+)\s*\|", line)
            if m:
                top_rows.append((m.group(1), int(m.group(2))))
    metrics["top_authorities"] = top_rows[:5]
    return metrics


def build_synthesis_memo(workspace: Path) -> str:
    repo = workspace / REPO_NAME
    baseline_path = repo / "results" / "unified_overnight_citation_baseline.md"
    follow_on_path = repo / "results" / "unified_follow_on_opportunities.md"
    stats = load_json(workspace / "data/2/unified_stats.json")
    inventory = load_json(workspace / "data/2/unified_raw_text_target_inventory.json")
    validation = load_json(workspace / "data/2/unified_overnight_validation_sample.json")
    batch_meta = load_json(workspace / "data/2/unified_overnight_batch_meta.json")
    baseline = parse_baseline_metrics(read_text(baseline_path))

    top_authorities = ", ".join(
        f"{name} ({count})" for name, count in baseline["top_authorities"][:5]
    )
    validation_bucket_lines = []
    for bucket in validation["bucket_meta"]:
        validation_bucket_lines.append(
            f"- {bucket['bucket']}: selected {bucket['selected_n']} of {bucket['eligible_n']} eligible."
        )

    return f"""# Overnight Synthesis Memo (Pre-Batch Return)

## What tonight has already accomplished

The overnight infrastructure has already produced a usable pre-batch package from existing `results/` and `data/2/` outputs, even though the Anthropic batch itself has not yet returned.

Completed artifacts already on disk:
- Citation baseline memo: `{baseline_path}`
- Raw-text target inventory: `{workspace / 'data/2/unified_raw_text_target_inventory.json'}`
- Validation sample: `{workspace / 'data/2/unified_overnight_validation_sample.json'}`
- Baseline tables: `{workspace / 'data/2/unified_overnight_baseline_tables.json'}`
- Unified stats report/data: `{workspace / 'data/2/unified_stats_report.md'}` and `{workspace / 'data/2/unified_stats.json'}`
- Batch request scaffold/meta: `{workspace / 'data/2/unified_overnight_requests.jsonl'}` and `{workspace / 'data/2/unified_overnight_batch_meta.json'}`

Operationally, that means the run already has:
- a normalized citation map for the screened FHA corpus,
- a raw-text-availability inventory showing which promising sub-queues can be worked immediately,
- a balanced 60-case validation sample,
- and a 50-record batch payload prepared for when Anthropic credits/API execution are available again.

## What the current outputs show

### 1. The screened corpus is large enough to support note-facing synthesis now
- Screened cases analyzed: {baseline['Screened cases analyzed']}
- Cases with at least one citation: {baseline['Cases with at least one citation']}
- Raw citation mentions: {baseline['Raw citation mentions']}
- Raw unique citation strings: {baseline['Raw unique citation strings']}
- Normalized unique authorities: {baseline['Normalized unique authorities']}

This is already enough to support descriptive doctrinal synthesis before any batch autopsy results return.

### 2. Procedural authorities dominate the citation environment
Top normalized authorities overall: {top_authorities}.

The current citation picture strongly supports a gatekeeping story: Iqbal and Twombly are the two dominant authorities by a very large margin, with substantive FHA authorities appearing much further down the list. That gives the note a present-tense empirical basis for saying that much of the disability FHA docket is being filtered through procedural sufficiency doctrine rather than developed through FHA-specific merits law.

### 3. The disability docket remains plaintiff-hostile in the post-Loper periods
From `data/2/unified_stats.json` / `unified_stats_report.md`:
- Disability cases in the screened corpus: {stats['composition']['disability']} of {stats['composition']['all_screened']} screened cases.
- Dated disability cases: {stats['composition']['dated']}.
- Strict plaintiff win rate fell from {stats['win_rates']['P1']['strict_pct']}% in P1 to {stats['win_rates']['P2']['strict_pct']}% in P2 and {stats['win_rates']['P3']['strict_pct']}% in P3.
- Broad plaintiff win rate fell from {stats['win_rates']['P1']['broad_pct']}% in P1 to {stats['win_rates']['P2']['broad_pct']}% in P2 and {stats['win_rates']['P3']['broad_pct']}% in P3.

That means the preexisting empirical claim is not just that disability cases dominate the corpus, but that plaintiff-side success remains weak after the doctrinal/administrative transition points the note cares about.

### 4. Pro se status looks central, not incidental
From the same stats outputs:
- Known pro se share in dated disability cases: {stats['pro_se']['overall']['pro_se_pct']}% ({stats['pro_se']['overall']['pro_se']} of {stats['pro_se']['overall']['known']}).
- Pro se strict win rate: {stats['pro_se']['overall']['pro_se_win']['strict_pct']}%.
- Represented strict win rate: {stats['pro_se']['overall']['rep_win']['strict_pct']}%.
- In P3 specifically, pro se share rises to {stats['pro_se']['P3']['pro_se_pct']}%.

That makes pro se pleading failure one of the most usable immediate explanations for the baseline’s procedural-authority dominance.

### 5. Defendant type matters in a way that is useful for the note’s institutional story
Selected strict plaintiff win rates from the current stats outputs:
- Fair-housing-organization plaintiffs: {stats['plaintiff_type']['FAIR_HOUSING_ORG']['strict_pct']}%
- Group-home-operator plaintiffs: {stats['plaintiff_type']['GROUP_HOME_OPERATOR']['strict_pct']}%
- Individual-tenant plaintiffs: {stats['plaintiff_type']['INDIVIDUAL_TENANT']['strict_pct']}%
- Housing-authority defendants: {stats['defendant_type']['HOUSING_AUTHORITY']['strict_pct']}%
- Government defendants: {stats['defendant_type']['GOVERNMENT']['strict_pct']}%

The immediate note-facing takeaway is that individual disability plaintiffs fare far worse than institutional plaintiffs, and public/institutional defendants are among the hardest targets. That aligns well with an argument about institutional process failures and plaintiff-side tractability limits.

### 6. There is already a workable raw-text queue even without more credits
From `unified_raw_text_target_inventory.json`:
- Raw text resolved for {inventory['raw_text_resolved_cases']} of {inventory['screened_case_count']} screened cases.
- Exported buckets currently ready for note-facing follow-on work:
  - Ambiguous pleading losses: {inventory['bucket_counts_exported']['likely_ambiguous_pleading_losses']} exported / {inventory['bucket_raw_text_available_counts_exported']['likely_ambiguous_pleading_losses']} with raw text already mapped.
  - Public-defendant process cases: {inventory['bucket_counts_exported']['public_defendant_process_cases']} exported / {inventory['bucket_raw_text_available_counts_exported']['public_defendant_process_cases']} with raw text.
  - Open-textured citation-rich cases: {inventory['bucket_counts_exported']['open_textured_cases_with_nontrivial_citations']} exported / {inventory['bucket_raw_text_available_counts_exported']['open_textured_cases_with_nontrivial_citations']} with raw text.
  - Citation-differential exemplars: {inventory['bucket_counts_exported']['citation_differential_exemplars']} exported / {inventory['bucket_raw_text_available_counts_exported']['citation_differential_exemplars']} with raw text.
  - Tiny-summary reopen queue: {inventory['bucket_counts_exported']['tiny_summaries']} exported / {inventory['bucket_raw_text_available_counts_exported']['tiny_summaries']} with raw text.

So the run is not blocked from producing useful memo work; it is only blocked from expanding the batch-dependent layer.

### 7. Validation design is already in place
The validation sample is balanced across eight useful buckets:
{chr(10).join(validation_bucket_lines)}

This matters because any morning memo can already distinguish between what is a baseline finding and what is awaiting confirmation from the validation/autopsy lane.

### 8. Batch execution is prepared but not yet returned
From `unified_overnight_batch_meta.json`:
- Model configured: {batch_meta['model']}
- Selected records in current payload: {batch_meta['selected_records']}
- Request lines prepared: 50
- Batch meta generated at: {batch_meta['generated_at']}

At the moment, the overnight repo `results/` folder contains the citation-baseline output but no downloaded batch-results artifact. Given the blocked Anthropic-credit situation, the right framing for tomorrow morning is: the preparation work succeeded, the queueing/scaffolding work succeeded, and the batch-dependent enrichment layer is the only missing piece.

## Bottom-line note-facing synthesis

Before the batch returns, tonight’s outputs already support three defensible propositions for the note:
1. Disability FHA litigation is citation-dense but procedurally dominated, with Iqbal/Twombly vastly outpacing FHA-specific merits authorities.
2. The plaintiff-hostility story is especially acute for pro se and individual-tenant cases, which helps explain why the disability docket can be large yet still undergenerate plaintiff-favorable doctrine.
3. The public-defendant / housing-authority subset appears especially difficult for plaintiffs, which makes institutional-process analysis a productive next note-facing lane even without any new Anthropic output.

## Current blocker

The only material blocker is the Anthropic-credit/API return path. The prep artifacts are ready, but no batch-return file is yet present in `results/`. Until credits are restored and the batch can run/download, the highest-value work is memo synthesis from the existing baseline, stats, inventory, and resolved raw-text subsets.

## Companion queue memo

For the ranked offline-first queue, see `{follow_on_path}` and the companion note-facing research queue generated alongside this memo.
"""


def build_queue_memo(workspace: Path) -> str:
    repo = workspace / REPO_NAME
    follow_on = read_text(repo / "results" / "unified_follow_on_opportunities.md")
    inventory = load_json(workspace / "data/2/unified_raw_text_target_inventory.json")
    baseline = parse_baseline_metrics(read_text(repo / "results" / "unified_overnight_citation_baseline.md"))

    def score_of(title: str) -> str:
        m = re.search(rf"### \d+\. {re.escape(title)} \((?:HIGH|MEDIUM|MEDIUM-HIGH), score ([0-9.]+)\)", follow_on)
        return m.group(1) if m else ""

    return f"""# Ranked Additional Research Queue Memo (Offline-First, Anthropic-Credit Block)

## Working assumption

Anthropic-credit constraints mean the overnight run should prioritize work that can be completed from existing `results/` and `data/2/` outputs, plus already-resolved raw text, without waiting for the batch return.

## Ranking principle

Priority goes to projects that are:
1. immediately executable from existing outputs,
2. likely to produce note-facing prose rather than just backend cleanup,
3. closely tied to the current empirical story, and
4. resilient to the absence of fresh Anthropic completions.

## Ranked queue

### 1. Pro se pleading-mechanism divergence memo
Priority: HIGH
Existing score: {score_of('Pro se pleading-mechanism divergence memo')}

Why this should go first:
- The citation baseline shows Ashcroft v. Iqbal and Bell Atlantic Corp. v. Twombly as the two dominant authorities in the screened corpus.
- The follow-on memo already identifies a 27.0-point pro se/represented gap in Iqbal-Twombly appearance rates.
- The broader stats outputs also show an extreme outcome gap: pro se strict win rate is far below represented strict win rate.
- This project can begin now from the existing pleading-loss inventory, citation baseline, and the subset of resolved raw-text cases.

Best note-facing product:
- A short memo explaining that the disability docket is not just plaintiff-hostile in the aggregate; it is filtered through a specific pro se pleading mechanism that suppresses substantive FHA development.

Why it is robust to the credit block:
- It uses existing counts, existing bucket exports, and manual/raw-text review of already-mapped cases.

### 2. Public-defendant process-failure subset study
Priority: HIGH
Existing score: {score_of('Public-defendant process-failure subset study')}

Why this is next:
- `{inventory['bucket_raw_text_available_counts_exported']['public_defendant_process_cases']}` exported public-defendant process cases already have raw text mapped.
- The stats outputs show especially weak plaintiff performance against housing-authority and government defendants.
- This subset is directly relevant to the note’s institutional and implementation story, not just its descriptive empirical claims.

Best note-facing product:
- A memo isolating where public-process breakdowns seem to occur: request clarity, eligibility proof, fragmented institutional authority, or failure to translate accommodation norms into administrative workflows.

Why it is robust to the credit block:
- The available raw-text subset is already large enough to support a bounded close-reading memo without waiting for new model output.

### 3. Citation-gap / doctrinal-omission memo for open-textured cases
Priority: HIGH
Existing score: {score_of('Citation-gap / doctrinal-omission memo for open-textured cases')}

Why this remains high-value:
- `{inventory['bucket_raw_text_available_counts_exported']['open_textured_cases_with_nontrivial_citations']}` open-textured, citation-rich cases already have raw text.
- The citation baseline shows heavy procedural-authority dominance, which raises an obvious omission question: when do opinions rely on general pleading doctrine without pairing it with FHA-specific accommodation or zoning authorities?
- This project translates the baseline tables into a doctrinal claim the note can actually use.

Best note-facing product:
- A memo showing that some disability FHA opinions are citation-rich but still underdevelop FHA-specific doctrine, helping explain why doctrinal clarity lags even in a large litigation corpus.

Why it is robust to the credit block:
- It depends on existing citation normalization and already-resolved raw text, not on batch autopsy completions.

### 4. Citation-differential exemplar packet
Priority: MEDIUM-HIGH
Existing score: {score_of('Citation-differential exemplar packet')}

Why this is a good bridge product:
- `{inventory['bucket_raw_text_available_counts_exported']['citation_differential_exemplars']}` exemplars already have raw text.
- It can be turned quickly into note-facing narrative examples that concretize the citation baseline.
- It is especially useful if the morning needs quotable, teachable case studies rather than another aggregate table.

Best note-facing product:
- A compact exemplar packet with 8-12 cases showing how procedural and substantive authorities interact, crowd out one another, or diverge by plaintiff/defendant type.

Why it is robust to the credit block:
- It is essentially a synthesis/selection task on top of already-existing outputs.

### 5. Tiny-summary reopening queue
Priority: MEDIUM
Existing score: {score_of('Tiny-summary reopening queue')}

Why this should stay fifth:
- It is more of a quality-improvement and validation-support queue than a thesis-facing memo.
- Only `{inventory['bucket_raw_text_available_counts_exported']['tiny_summaries']}` exported cases in the queue already have raw text.
- It becomes more valuable if morning review suggests the structured summaries are too thin for close doctrinal use.

Best note-facing product:
- Not a standalone memo first; better framed as a support queue for fixing thin summaries that matter to the top-ranked memo lanes.

Why it is less urgent under the credit block:
- It improves confidence, but it does not itself advance the note’s argument as directly as the top three projects.

## Default recommendation if only one memo gets written before credits are restored

Write the pro se pleading-mechanism divergence memo first. It sits closest to the current baseline’s most important descriptive fact: the disability FHA docket is dominated by procedural citations, and that dominance appears to be concentrated in the pro se subset.

## Packaging recommendation for tomorrow morning

If time is limited, collapse the queue into a single note-facing packet with three sections:
1. Procedural gatekeeping in the disability docket.
2. Public-defendant process failure as an institutional subset.
3. Exemplar cases showing doctrinal omission or mismatch.

That single packet would convert the current outputs into something editorially useful even if Anthropic credits remain blocked through the morning.

## Current constraint statement

The current block is not lack of material. The current block is lack of fresh batch completions. Existing outputs already support a meaningful offline-first synthesis workflow.

## Reference point from the current baseline

For orientation, the top five normalized authorities are: {', '.join(f'{name} ({count})' for name, count in baseline['top_authorities'])}. That is why the queue is organized around pleading, omission, and institutional process rather than around a generic resurvey of the corpus.
"""


def main() -> None:
    workspace = DEFAULT_WORKSPACE
    repo = workspace / REPO_NAME
    results_dir = repo / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    synthesis_path = results_dir / "overnight_note_facing_synthesis_memo.md"
    queue_path = results_dir / "overnight_additional_research_queue_memo.md"

    synthesis_path.write_text(build_synthesis_memo(workspace), encoding="utf-8")
    queue_path.write_text(build_queue_memo(workspace), encoding="utf-8")

    print(f"wrote {synthesis_path}")
    print(f"wrote {queue_path}")


if __name__ == "__main__":
    main()
