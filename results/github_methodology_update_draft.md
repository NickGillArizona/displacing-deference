# GitHub Methodology Update Draft

Generated: 2026-04-15T07:31:18.645957+00:00

## New overnight research path

The overnight unified-corpus extension now uses a hybrid workflow:

1. Codex CLI for planning, script generation, prompt/schema refinement, disagreement review, and synthesis.
2. OpenRouter for economical structured classification of the overnight schema.
3. Local merge/analysis scripts for downstream memos and note integration.

## Model plan

- Primary bulk model: `moonshotai/kimi-k2.5`
- Escalation model for malformed/low-confidence subsets: `z-ai/glm-5.1`

## Why this change

The original Anthropic overnight batch path was blocked by API credit limits. The revised path preserves the overnight research design while shifting bulk structured extraction to a lower-cost OpenRouter route and using Codex for higher-value reasoning tasks.

## Current overnight artifacts

- `scripts/unified_overnight_openrouter.py`
- `results/unified_overnight_openrouter*_manifest.json`
- `results/unified_overnight_openrouter*_methodology.md`
- `results/overnight_status_updates.md`
- `results/overnight_methodology_run_log.md`

## Suggested README/CREDITS updates

- Note that the overnight extension path uses OpenRouter with Kimi K2.5 for economical bulk classification and GLM 5.1 for bounded escalation.
- Note that Codex CLI was used for repo-local script generation, execution-planning, and output-synthesis support.
