# Ranked Additional Research Queue Memo (Offline-First, Anthropic-Credit Block)

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
Existing score: 10.55

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
Existing score: 9.8

Why this is next:
- `33` exported public-defendant process cases already have raw text mapped.
- The stats outputs show especially weak plaintiff performance against housing-authority and government defendants.
- This subset is directly relevant to the note’s institutional and implementation story, not just its descriptive empirical claims.

Best note-facing product:
- A memo isolating where public-process breakdowns seem to occur: request clarity, eligibility proof, fragmented institutional authority, or failure to translate accommodation norms into administrative workflows.

Why it is robust to the credit block:
- The available raw-text subset is already large enough to support a bounded close-reading memo without waiting for new model output.

### 3. Citation-gap / doctrinal-omission memo for open-textured cases
Priority: HIGH
Existing score: 9.33

Why this remains high-value:
- `42` open-textured, citation-rich cases already have raw text.
- The citation baseline shows heavy procedural-authority dominance, which raises an obvious omission question: when do opinions rely on general pleading doctrine without pairing it with FHA-specific accommodation or zoning authorities?
- This project translates the baseline tables into a doctrinal claim the note can actually use.

Best note-facing product:
- A memo showing that some disability FHA opinions are citation-rich but still underdevelop FHA-specific doctrine, helping explain why doctrinal clarity lags even in a large litigation corpus.

Why it is robust to the credit block:
- It depends on existing citation normalization and already-resolved raw text, not on batch autopsy completions.

### 4. Citation-differential exemplar packet
Priority: MEDIUM-HIGH
Existing score: 8.28

Why this is a good bridge product:
- `21` exemplars already have raw text.
- It can be turned quickly into note-facing narrative examples that concretize the citation baseline.
- It is especially useful if the morning needs quotable, teachable case studies rather than another aggregate table.

Best note-facing product:
- A compact exemplar packet with 8-12 cases showing how procedural and substantive authorities interact, crowd out one another, or diverge by plaintiff/defendant type.

Why it is robust to the credit block:
- It is essentially a synthesis/selection task on top of already-existing outputs.

### 5. Tiny-summary reopening queue
Priority: MEDIUM
Existing score: 7.7

Why this should stay fifth:
- It is more of a quality-improvement and validation-support queue than a thesis-facing memo.
- Only `5` exported cases in the queue already have raw text.
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

For orientation, the top five normalized authorities are: Ashcroft v. Iqbal (1013), Bell Atlantic Corp. v. Twombly (964), McDonnell Douglas Corp. v. Green (109), Havens Realty Corp. v. Coleman (106), City of Cleburne v. Cleburne Living Center (98). That is why the queue is organized around pleading, omission, and institutional process rather than around a generic resurvey of the corpus.
