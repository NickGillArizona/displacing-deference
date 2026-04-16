# Unified Overnight OpenRouter Pilot Review

The failures were primarily parameter-driven, not case-driven. In the reviewed outputs, only 17 records parsed successfully while 18 landed in `errors`. Across the error file, all 36 provider calls reported exactly `650` output tokens; 35 of those 36 had empty extracted `raw_text`, and the lone nonempty fallback was truncated JSON. That pattern points to the runner's current combination of a very large prompt, reasoning-enabled requests, and a hard `max_tokens=650` cap. In practice, many calls appear to have spent the budget on reasoning/non-final output and never delivered a usable JSON object in `message.content`; when content did appear at the cap, it was cut off.

## Likely Cause

1. `scripts/unified_overnight_openrouter.py` sends:
   - `max_tokens = 650`
   - `reasoning = {"max_tokens": 1024}` for the primary model
   - `reasoning = {"max_tokens": 2048}` for escalation
2. The prompt itself is unusually long because it inlines the full schema, examples, and case payload.
3. The error pattern is consistent with reasoning-enabled OpenRouter responses exhausting the useful completion budget before emitting final JSON, plus occasional truncation when JSON generation starts too late.

## Exact Recommended Parameter Changes Before Rerun

Change the runner defaults in `scripts/unified_overnight_openrouter.py` before rerunning:

- Set `ModelConfig.max_output_tokens` from `650` to `1400`.
- Run with reasoning disabled for both lanes:
  - `--primary-reasoning-budget 0`
  - `--escalation-reasoning-budget 0`

Recommended rerun command:

```bash
python3 scripts/unified_overnight_openrouter.py run \
  --subset pilot \
  --max-concurrency 6 \
  --enable-escalation \
  --primary-reasoning-budget 0 \
  --escalation-reasoning-budget 0
```

Because `max_output_tokens` is currently hard-coded rather than exposed as a CLI flag, update the `ModelConfig` default to `1400` first, then rerun. If a second pilot still shows cap-hits, raise that value again to `1600`; do not restore reasoning budgets unless you also shorten the prompt substantially.
