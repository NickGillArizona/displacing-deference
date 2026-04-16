# Paper Methodology Update Draft

Generated: 2026-04-15T07:31:18.645957+00:00

## Overnight extension methodology

After the initial overnight autopsy design was prepared, the implementation path was revised into a hybrid workflow:

- Codex CLI was used for high-value reasoning tasks: pipeline inspection, prompt/schema iteration, script generation, disagreement strategy, and synthesis.
- OpenRouter was selected for the economical bulk classification layer.
- Kimi K2.5 was chosen as the primary model for the structured overnight schema because it offers materially lower token pricing than GLM 5.1 while remaining strong on reasoning/coding tasks.
- GLM 5.1 was reserved as an escalation model for malformed outputs, low-confidence cases, or difficult subsets rather than as the primary full-wave model.

## Planned classification waves

1. Pilot subset: balanced disability-wave sample across P1/P2/P3.
2. Main disability wave: full dated disability subset.
3. Optional escalation subset: malformed or low-confidence pilot/full-wave outputs.

## Reporting practice

Routine overnight updates are logged in repo result files so that every stage records:
- timestamp,
- model and command used,
- cases processed,
- generated outputs,
- and the implications for the note's empirical and methodological claims.

## Caution language

Until the full OpenRouter overnight wave completes and is merged into the enriched unified database, the current fallback memos should be treated as provisional structured-data analyses rather than the final second-pass autopsy layer.
