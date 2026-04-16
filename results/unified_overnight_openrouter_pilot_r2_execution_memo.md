# Unified Overnight OpenRouter Execution Memo

## Recommended commands

```bash
python3 scripts/unified_overnight_openrouter.py smoke-test --subset pilot
python3 scripts/unified_overnight_openrouter.py estimate-cost --subset pilot
python3 scripts/unified_overnight_openrouter.py estimate-cost --subset disability-wave
python3 scripts/unified_overnight_openrouter.py run --subset pilot --max-concurrency 6 --enable-escalation --escalate-low-confidence
python3 scripts/unified_overnight_openrouter.py run --subset disability-wave --max-concurrency 10
python3 scripts/unified_overnight_merge.py --results results/unified_overnight_openrouter_results.json --lookup results/unified_overnight_openrouter_id_lookup.json --output results/unified_overnight_openrouter_merged.json --report results/unified_overnight_openrouter_merge_report.md
```

## Budget rationale

- Pilot selection size: 36 records.
- Full disability-wave size is available via `estimate-cost --subset disability-wave`.
- Kimi-only base estimate for the current manifest: $0.12.
- The efficient path is to pay Kimi once for the full disability-wave and reserve GLM 5.1 only for malformed or low-confidence cases.
- That keeps the bulk budget anchored to the repo's documented Kimi pricing while avoiding a repeat of the earlier uncapped GLM spend.

## Current run state

- Completed good results: 35
- Errors: 1
- Malformed outputs: 0
- This memo is auto-generated from the same manifest used to build requests, so GitHub and methodology updates can quote it directly.
