# Unified Overnight OpenRouter Methodology

## Scope

- This repo-local path classifies the unified overnight schema against `/mnt/c/Users/nickg/OneDrive/Documents/Note/Displacing-Deference-Data-and-Doctrine-for-a-Disability-Centered-AFFH/data/FHA_Unified_Database.json`.
- It reuses the existing overnight structured prompt shape rather than the older Java full-text pipeline.
- Output is constrained to the overnight schema fields already expected by the downstream merge and memo scripts.

## Subsets

- `pilot`: balanced deterministic sample across P1/P2/P3 from the disability-wave population; default size 36 unless `--limit` is set.
- `disability-wave`: all screened disability cases with dated P1/P2/P3 placement.
- `all-screened`: all screened cases with resolved outcomes.

## Models

- Primary bulk model: `moonshotai/kimi-k2.5` with reasoning budget 0 and max output 3200.
- Optional escalation model: `z-ai/glm-5.1` with reasoning budget 0.
- Escalation is intended for malformed outputs, parser failures, and optionally low-confidence results only, not a second full-pass batch.

## Budget logic

- Kimi pricing is hard-coded from the repo's documented OpenRouter cost table: $0.45/M input tokens and $2.20/M output tokens.
- GLM 5.1 pricing is left configurable because the prior GLM experiment was explicitly documented as cost-volatile and unsuitable for uncapped bulk use.
- The execution path therefore plans the full disability-wave on Kimi alone and treats GLM as a narrow reserve lane rather than part of the base budget.

## Runtime behavior

- Requests are built once, stored as JSONL, and assigned stable `custom_id` values from `source_file`.
- The live runner is resumable: existing completed IDs in `results`, `errors`, and `malformed` are skipped automatically.
- Concurrent OpenRouter calls are supported through `httpx.AsyncClient` and `asyncio`, with checkpoint writes after each completion.
- The result shape matches the overnight merge contract: `source_file`, `custom_id`, token usage, and `classification`.
