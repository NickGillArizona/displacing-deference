# Overnight Methodology Run Log

## 2026-04-15T07:27:59.921772+00:00 — OpenRouter path activated
- Codex CLI verified authenticated (`Logged in using ChatGPT`).
- OpenRouter key wired via workspace env file at `../fha-research/.env`.
- New repo-local OpenRouter runner created: `scripts/unified_overnight_openrouter.py`.
- Smoke test passed with 3 schema examples and API key loaded.
- Cost estimates generated: pilot 36 cases ≈ $0.115 on Kimi K2.5; disability wave 1,330 cases ≈ $4.27 on Kimi K2.5.
- Pilot run launched in background using Kimi K2.5 primary + optional GLM 5.1 escalation.
- Expected next outputs: live pilot results JSON, malformed/error logs, then pilot review and prompt calibration memo.

## 2026-04-15T07:28:39.665298+00:00 — Pilot dependency fix
- Operational change: live OpenRouter runner now uses `uv run` dependency injection to avoid mutating the system Python while still enabling `httpx` + `.env` loading.

## 2026-04-15T07:40:39.608148+00:00 — Pilot rerun launched (R2)
- Runner defaults revised based on Codex pilot review: reasoning budgets set to 0 by default and max output tokens raised to 1400.
- New output prefix: `unified_overnight_openrouter_pilot_r2`.
- R2 pilot launched with Kimi K2.5 primary and optional GLM 5.1 escalation, but without reasoning-token budgets.
- This rerun is intended to test whether the original failure mode was parameter-driven rather than model-driven.

## 2026-04-15T08:04:16.336523+00:00 — Corrected pilot completed
- OpenRouter corrected pilot (`unified_overnight_openrouter_pilot_r2`) finished with 35 successful classifications, 1 error, 0 malformed outputs.
- Error rate is low enough to proceed to the main disability-wave run.
- Remaining pilot error appears to be a transport/truncation problem on a single escalated case rather than a systemic schema failure.
- Decision: proceed to full disability wave on Kimi K2.5 with GLM 5.1 reserved for bounded escalation only.

## 2026-04-15T08:13:59.820852+00:00 — Parallel memo work while disability wave runs
- Added `results/pro_se_pleading_mechanism_divergence_memo.md` from existing overnight outputs and baseline/citation evidence.
- Added `results/public_defendant_process_failure_memo.md` from existing overnight outputs, raw-text-target inventory, and current subset statistics.
- These memos are bounded, note-facing, and do not consume paid API calls.
