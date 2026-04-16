#!/usr/bin/env python3
"""Repo-local OpenRouter runner for the unified overnight FHA corpus schema."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:  # pragma: no cover
    load_dotenv = None


P1_START = datetime(2022, 1, 1)
P1_END = datetime(2024, 6, 28)
P2_END = datetime(2025, 2, 5)
DEFAULT_INPUT_CHARS_PER_TOKEN = float(os.environ.get("UNIFIED_OVERNIGHT_CHARS_PER_TOKEN", "4.0"))
DEFAULT_OUTPUT_TOKENS_EST = int(os.environ.get("UNIFIED_OVERNIGHT_EST_OUTPUT_TOKENS", "260"))
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_REASONING_CHARS = 1200

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
NOTE_ROOT = SCRIPT_PATH.parents[2]
RESULTS_DIR = REPO_ROOT / "results"

PRIMARY_MODEL_DEFAULT = "moonshotai/kimi-k2.5"
ESCALATION_MODEL_DEFAULT = os.environ.get("UNIFIED_OVERNIGHT_ESCALATION_MODEL", "z-ai/glm-5.1")

SYSTEM_PROMPT = """You are a legal research assistant classifying federal Fair Housing Act case records using only structured extracted data. You are not reading raw opinions. Return ONLY valid JSON that matches the required schema. Do not include markdown fences, commentary, or extra keys.

General rules:
- Ground every classification in the supplied structured record.
- Use conservative labels when the record is thin.
- Do not invent facts not present in the structured record.
- If the record reflects a plaintiff win or surviving claim, do not force a pleading-failure diagnosis.
- Arrays must contain unique values and must not mix NONE_APPARENT or UNCLEAR with substantive values.
- reasoning must be 2-4 sentences and concise.
"""

USER_PROMPT_TEMPLATE = """Classify this screened FHA unified case record for the overnight supplemental schema.

SCHEMA REFERENCE:
{schema_text}

EXAMPLES:
{examples_text}

CASE DATA:
{case_data}

Return ONLY a JSON object with exactly these keys:
- pleading_failure_family
- pleading_failure_mechanism
- institutional_function_missing
- administratively_observable_fact_pattern
- raw_text_review_priority
- doctrinal_gap_signal
- public_process_failure_flag
- tier1_tier2_fixability
- classification_confidence
- reasoning
"""


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelConfig:
    id: str
    label: str
    input_cost_per_million: Optional[float]
    output_cost_per_million: Optional[float]
    reasoning_budget: int
    temperature: float = 0.0
    max_output_tokens: int = 2400


@dataclass
class BatchSelection:
    records: List[Dict[str, Any]]
    subset_name: str
    scope_record_count: int
    counts_by_period: Dict[str, int]
    counts_by_bucket: Dict[str, int]


def load_env_files() -> None:
    candidates = [
        REPO_ROOT / ".env",
        NOTE_ROOT / "fha-research" / ".env",
        NOTE_ROOT / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            if load_dotenv is not None:
                load_dotenv(candidate, override=False)
            else:
                load_env_file_fallback(candidate)


def load_env_file_fallback(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue
        value = value.strip().strip("'").strip('"')
        os.environ[key] = value


def data_candidates(filename: str) -> List[Path]:
    return [
        REPO_ROOT / "data" / filename,
        NOTE_ROOT / "data" / "2" / filename,
        NOTE_ROOT / "data" / filename,
    ]


def resolve_existing_path(candidates: Iterable[Path], label: str) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    joined = ", ".join(str(item) for item in candidates)
    raise ConfigError(f"Could not locate {label}. Tried: {joined}")


def resolve_input_db() -> Path:
    return resolve_existing_path(data_candidates("FHA_Unified_Database.json"), "FHA_Unified_Database.json")


def resolve_schema_path() -> Path:
    extra = [
        REPO_ROOT / "pipeline" / "unified_overnight_schema.md",
        NOTE_ROOT / "data" / "2" / "unified_overnight_schema.md",
    ]
    return resolve_existing_path(extra, "unified_overnight_schema.md")


def resolve_examples_path() -> Path:
    extra = [
        REPO_ROOT / "pipeline" / "unified_overnight_examples.json",
        NOTE_ROOT / "data" / "2" / "unified_overnight_examples.json",
    ]
    return resolve_existing_path(extra, "unified_overnight_examples.json")


def ensure_results_dir() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)


def safe_text(value: Any, limit: Optional[int] = None) -> Any:
    if isinstance(value, str):
        cleaned = re.sub(r"\s+", " ", value).strip()
        if limit is not None and len(cleaned) > limit:
            return cleaned[: limit - 3].rstrip() + "..."
        return cleaned
    return value


def normalize_text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


def summarize_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "claim_number": claim.get("claim_number"),
        "theory": claim.get("theory"),
        "accommodation_type": claim.get("accommodation_type"),
        "stage": claim.get("stage"),
        "dismissal_reason": claim.get("dismissal_reason") or claim.get("disposition"),
        "outcome": claim.get("outcome"),
        "merits_reached": claim.get("merits_reached"),
        "reasoning": safe_text(claim.get("reasoning", ""), 320),
    }


def extract_case_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source_file": record.get("source_file"),
        "case_name": record.get("case_name"),
        "year": record.get("year"),
        "court": record.get("court"),
        "circuit": record.get("circuit"),
        "screening_result": record.get("screening_result"),
        "date_filed": record.get("date_filed"),
        "procedural_posture": safe_text(record.get("procedural_posture", ""), 220),
        "outcome": record.get("outcome"),
        "pro_se": record.get("pro_se"),
        "counsel_named": record.get("counsel_named"),
        "plaintiff_type": record.get("plaintiff_type"),
        "defendant_type": record.get("defendant_type"),
        "housing_type": record.get("housing_type"),
        "subsidy_program": record.get("subsidy_program"),
        "disability_alleged": record.get("disability_alleged"),
        "disability_category": record.get("disability_category"),
        "primary_protected_class": record.get("primary_protected_class"),
        "protected_classes": record.get("protected_classes"),
        "claim_types": record.get("claim_types", []),
        "primary_claim_type": record.get("primary_claim_type"),
        "fha_section_cited": record.get("fha_section_cited"),
        "interactive_process_discussed": record.get("interactive_process_discussed"),
        "delay_as_denial": record.get("delay_as_denial"),
        "iqbal_twombly_cited": record.get("iqbal_twombly_cited"),
        "loper_bright_cited": record.get("loper_bright_cited"),
        "key_cases_cited": record.get("key_cases_cited", [])[:12],
        "accommodation_type": record.get("accommodation_type"),
        "secondary_accommodation_type": record.get("secondary_accommodation_type"),
        "accommodation_description": safe_text(record.get("accommodation_description", ""), 240),
        "key_holding": safe_text(record.get("key_holding", ""), 450),
        "brief_summary": safe_text(record.get("brief_summary", ""), 550),
        "fha_claims": [summarize_claim(c) for c in record.get("fha_claims", [])[:8]],
    }


def parse_date(value: Any, year: Any = None) -> Optional[datetime]:
    if isinstance(value, str) and value.strip():
        raw = value.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"):
            try:
                if fmt == "%Y-%m-%dT%H:%M:%S":
                    return datetime.strptime(raw[:19], fmt)
                return datetime.strptime(raw[:10], fmt)
            except ValueError:
                continue
    if isinstance(year, int):
        return datetime(year, 1, 1)
    return None


def assign_period(record: Dict[str, Any]) -> Optional[str]:
    dt = parse_date(record.get("date_filed"), record.get("year"))
    if dt is None or dt < P1_START:
        return None
    if dt < P1_END:
        return "P1"
    if dt < P2_END:
        return "P2"
    return "P3"


def has_disability(record: Dict[str, Any]) -> bool:
    classes = record.get("protected_classes") or []
    if isinstance(classes, str):
        classes = [classes]
    return any("disability" in str(item).lower() for item in classes) or bool(record.get("disability_alleged"))


def infer_bucket(record: Dict[str, Any]) -> str:
    defendant_type = normalize_text(record.get("defendant_type")).upper()
    housing_type = normalize_text(record.get("housing_type")).upper()
    plaintiff_type = normalize_text(record.get("plaintiff_type")).upper()
    claim_types = " ".join(record.get("claim_types") or []).upper()
    brief = f"{record.get('brief_summary', '')} {record.get('key_holding', '')}".upper()
    if has_disability(record):
        return "disability"
    if str(record.get("pro_se")).strip().lower() in {"true", "yes", "1"}:
        return "pro_se"
    if any(token in defendant_type for token in ["HOUSING_AUTHORITY", "MUNICIPALITY", "GOVERNMENT"]):
        return "public"
    if any(token in housing_type for token in ["PUBLIC_HOUSING", "SECTION_8", "LIHTC", "SUPPORTIVE", "OTHER_SUBSIDIZED"]):
        return "public"
    if plaintiff_type in {"GOVERNMENT", "FAIR_HOUSING_ORG", "GROUP_HOME_OPERATOR"}:
        return "institutional"
    if any(token in claim_types for token in ["DESIGN", "CONSTRUCTION", "DISPARATE_IMPACT"]):
        return "institutional"
    if "PATTERN" in brief or "POLICY" in brief:
        return "institutional"
    return "remaining"


def stable_sort_key(record: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        assign_period(record) or "P0",
        normalize_text(record.get("source_file"), "~"),
        normalize_text(record.get("case_name"), "~"),
    )


def select_records(records: Sequence[Dict[str, Any]], args: argparse.Namespace) -> BatchSelection:
    screened = [
        record
        for record in records
        if normalize_text(record.get("screening_result"), "NO").upper() != "NO"
        and record.get("case_name")
        and record.get("outcome") not in (None, "", "?")
    ]
    if args.subset == "pilot":
        disability_wave = [record for record in screened if has_disability(record) and assign_period(record)]
        grouped: Dict[str, List[Dict[str, Any]]] = {"P1": [], "P2": [], "P3": []}
        for record in sorted(disability_wave, key=stable_sort_key):
            period = assign_period(record)
            if period in grouped:
                grouped[period].append(record)
        pilot_size = args.limit or 36
        selected: List[Dict[str, Any]] = []
        while len(selected) < pilot_size:
            progressed = False
            for period in ("P1", "P2", "P3"):
                if grouped[period] and len(selected) < pilot_size:
                    selected.append(grouped[period].pop(0))
                    progressed = True
            if not progressed:
                break
        scope = disability_wave
    elif args.subset == "disability-wave":
        scope = [record for record in screened if has_disability(record) and assign_period(record)]
        selected = sorted(scope, key=stable_sort_key)
        if args.limit:
            selected = selected[: args.limit]
        if args.offset:
            selected = selected[args.offset :]
    elif args.subset == "all-screened":
        scope = screened
        selected = sorted(scope, key=stable_sort_key)
        if args.limit:
            selected = selected[: args.limit]
        if args.offset:
            selected = selected[args.offset :]
    else:
        raise ConfigError(f"Unsupported subset: {args.subset}")

    if args.only_source_files:
        raw_value = args.only_source_files.strip()
        if raw_value.startswith("@"):
            source_path = Path(raw_value[1:]).expanduser().resolve()
            allowed = {
                line.strip()
                for line in source_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        else:
            allowed = {item.strip() for item in raw_value.split(",") if item.strip()}
        selected = [record for record in selected if normalize_text(record.get("source_file")) in allowed]

    counts_by_period = Counter(assign_period(record) or "P0" for record in selected)
    counts_by_bucket = Counter(infer_bucket(record) for record in selected)
    return BatchSelection(
        records=selected,
        subset_name=args.subset,
        scope_record_count=len(scope),
        counts_by_period=dict(sorted(counts_by_period.items())),
        counts_by_bucket=dict(sorted(counts_by_bucket.items())),
    )


def make_custom_id(source_file: str, index: int) -> str:
    digest = hashlib.md5(source_file.encode("utf-8")).hexdigest()[:12]
    return f"uor-{index:04d}-{digest}"


def estimate_tokens_from_text(text: str) -> int:
    return int(math.ceil(len(text) / DEFAULT_INPUT_CHARS_PER_TOKEN)) if text else 0


def estimate_request_tokens(payload: Dict[str, Any], schema_text: str, examples_text: str) -> int:
    prompt = USER_PROMPT_TEMPLATE.format(
        schema_text=schema_text,
        examples_text=examples_text,
        case_data=json.dumps(payload, indent=2, ensure_ascii=False),
    )
    return estimate_tokens_from_text(SYSTEM_PROMPT) + estimate_tokens_from_text(prompt)


def build_requests(args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    input_db = resolve_input_db()
    schema_path = resolve_schema_path()
    examples_path = resolve_examples_path()
    records = read_json(input_db)
    if isinstance(records, dict):
        records = list(records.values())
    selection = select_records(records, args)
    schema_text = schema_path.read_text(encoding="utf-8").strip()
    examples_text = json.dumps(read_json(examples_path), indent=2, ensure_ascii=False)

    requests: List[Dict[str, Any]] = []
    id_lookup: Dict[str, Any] = {}
    input_tokens = 0
    output_tokens = 0

    for index, record in enumerate(selection.records):
        source_file = normalize_text(record.get("source_file"), f"record_{index}")
        case_fields = extract_case_fields(record)
        prompt = USER_PROMPT_TEMPLATE.format(
            schema_text=schema_text,
            examples_text=examples_text,
            case_data=json.dumps(case_fields, indent=2, ensure_ascii=False),
        )
        custom_id = make_custom_id(source_file, index)
        estimated_input = estimate_request_tokens(case_fields, schema_text, examples_text)
        input_tokens += estimated_input
        output_tokens += DEFAULT_OUTPUT_TOKENS_EST
        id_lookup[custom_id] = {
            "source_file": source_file,
            "case_name": record.get("case_name"),
            "period": assign_period(record),
            "bucket": infer_bucket(record),
            "year": record.get("year"),
            "estimated_input_tokens": estimated_input,
        }
        requests.append(
            {
                "custom_id": custom_id,
                "source_file": source_file,
                "case_name": record.get("case_name"),
                "prompt": prompt,
                "payload": case_fields,
            }
        )

    manifest = {
        "generated_at": datetime.now(UTC).isoformat(),
        "workspace_root": str(NOTE_ROOT),
        "repo_root": str(REPO_ROOT),
        "input_db": str(input_db),
        "schema_path": str(schema_path),
        "examples_path": str(examples_path),
        "subset": selection.subset_name,
        "selected_records": len(requests),
        "subset_scope_records": selection.scope_record_count,
        "counts_by_period": selection.counts_by_period,
        "counts_by_bucket": selection.counts_by_bucket,
        "token_estimates": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "method": f"characters/{DEFAULT_INPUT_CHARS_PER_TOKEN} + fixed output token estimate {DEFAULT_OUTPUT_TOKENS_EST}",
        },
        "offset": args.offset,
        "limit": args.limit,
        "only_source_files": args.only_source_files,
    }
    return requests, id_lookup, manifest


def build_model_config(args: argparse.Namespace, which: str) -> ModelConfig:
    if which == "primary":
        return ModelConfig(
            id=args.primary_model,
            label="primary",
            input_cost_per_million=args.primary_input_cost,
            output_cost_per_million=args.primary_output_cost,
            reasoning_budget=args.primary_reasoning_budget,
            max_output_tokens=args.primary_max_output_tokens,
        )
    if which == "escalation":
        return ModelConfig(
            id=args.escalation_model,
            label="escalation",
            input_cost_per_million=args.escalation_input_cost,
            output_cost_per_million=args.escalation_output_cost,
            reasoning_budget=args.escalation_reasoning_budget,
            max_output_tokens=args.escalation_max_output_tokens,
        )
    raise ConfigError(f"Unknown model slot: {which}")


def estimate_cost(model: ModelConfig, input_tokens: int, output_tokens: int) -> Optional[float]:
    if model.input_cost_per_million is None or model.output_cost_per_million is None:
        return None
    return round(
        (input_tokens / 1_000_000) * model.input_cost_per_million
        + (output_tokens / 1_000_000) * model.output_cost_per_million,
        4,
    )


def strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def extract_first_json_object(text: str) -> str:
    cleaned = strip_code_fences(text)
    start = cleaned.find("{")
    if start == -1:
        raise ValueError("No JSON object found")
    depth = 0
    in_string = False
    escaped = False
    for pos in range(start, len(cleaned)):
        char = cleaned[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return cleaned[start : pos + 1]
    raise ValueError("JSON object appears truncated")


def normalize_array(values: Any) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    normalized: List[str] = []
    seen = set()
    for item in values:
        if not isinstance(item, str):
            continue
        token = item.strip()
        if token and token not in seen:
            normalized.append(token)
            seen.add(token)
    return normalized


def parse_model_json(raw_text: str) -> Dict[str, Any]:
    return json.loads(extract_first_json_object(raw_text))


def validate_classification(payload: Dict[str, Any]) -> Tuple[bool, List[str]]:
    required = [
        "pleading_failure_family",
        "pleading_failure_mechanism",
        "institutional_function_missing",
        "administratively_observable_fact_pattern",
        "raw_text_review_priority",
        "doctrinal_gap_signal",
        "public_process_failure_flag",
        "tier1_tier2_fixability",
        "classification_confidence",
        "reasoning",
    ]
    issues: List[str] = []
    for key in required:
        if key not in payload:
            issues.append(f"missing:{key}")
    if issues:
        return False, issues
    if not isinstance(payload.get("public_process_failure_flag"), bool):
        issues.append("public_process_failure_flag:not_bool")
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, str) or not reasoning.strip():
        issues.append("reasoning:empty")
    if isinstance(reasoning, str) and len(reasoning) > MAX_REASONING_CHARS:
        issues.append("reasoning:too_long")
    for array_key in ("institutional_function_missing", "administratively_observable_fact_pattern"):
        normalized = normalize_array(payload.get(array_key))
        if not normalized:
            issues.append(f"{array_key}:empty_or_invalid")
        payload[array_key] = normalized
    return len(issues) == 0, issues


def extract_message_text(message: Any) -> str:
    if isinstance(message, str):
        return message
    if isinstance(message, list):
        parts: List[str] = []
        for item in message:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif item.get("type") == "text" and isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join(part for part in parts if part)
    if isinstance(message, dict):
        if isinstance(message.get("content"), str):
            return message["content"]
        return extract_message_text(message.get("content"))
    return ""


def build_artifact_paths(prefix: str) -> Dict[str, Path]:
    return {
        "manifest": RESULTS_DIR / f"{prefix}_manifest.json",
        "lookup": RESULTS_DIR / f"{prefix}_id_lookup.json",
        "requests": RESULTS_DIR / f"{prefix}_requests.jsonl",
        "results": RESULTS_DIR / f"{prefix}_results.json",
        "errors": RESULTS_DIR / f"{prefix}_errors.json",
        "malformed": RESULTS_DIR / f"{prefix}_malformed.json",
        "progress": RESULTS_DIR / f"{prefix}_progress.json",
        "status_md": RESULTS_DIR / f"{prefix}_status.md",
        "methodology_md": RESULTS_DIR / f"{prefix}_methodology.md",
        "memo_md": RESULTS_DIR / f"{prefix}_execution_memo.md",
    }


def load_existing_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    payload = read_json(path)
    return payload if isinstance(payload, list) else []


def write_requests_jsonl(path: Path, requests: Sequence[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for request in requests:
            fh.write(json.dumps(request, ensure_ascii=False) + "\n")


def should_escalate(args: argparse.Namespace, parsed: Dict[str, Any], issues: List[str], error: str = "") -> bool:
    if not args.enable_escalation:
        return False
    if error:
        return True
    if issues:
        return True
    if args.escalate_low_confidence and normalize_text(parsed.get("classification_confidence")).upper() == "LOW":
        return True
    return False


async def call_openrouter(
    client: Any,
    model: ModelConfig,
    prompt: str,
    api_key: str,
    custom_id: str,
) -> Dict[str, Any]:
    body = {
        "model": model.id,
        "temperature": model.temperature,
        "max_tokens": model.max_output_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    if model.reasoning_budget > 0:
        body["reasoning"] = {"max_tokens": model.reasoning_budget}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/nickgill-law/displacing-deference",
        "X-Title": "Unified Overnight OpenRouter Runner",
    }
    response = await client.post(OPENROUTER_URL, headers=headers, json=body)
    response.raise_for_status()
    payload = response.json()
    choice = (payload.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    text = extract_message_text(message.get("content"))
    usage = payload.get("usage") or {}
    return {
        "custom_id": custom_id,
        "model": model.id,
        "raw_text": text,
        "usage": {
            "input_tokens": usage.get("prompt_tokens") or usage.get("input_tokens") or 0,
            "output_tokens": usage.get("completion_tokens") or usage.get("output_tokens") or 0,
            "total_tokens": usage.get("total_tokens") or 0,
        },
        "provider_response_id": payload.get("id"),
    }


async def run_requests(
    args: argparse.Namespace,
    requests: Sequence[Dict[str, Any]],
    id_lookup: Dict[str, Any],
    artifact_paths: Dict[str, Path],
) -> Dict[str, Any]:
    load_env_files()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ConfigError("OPENROUTER_API_KEY is not set. The runner loads repo/.env, Note/fha-research/.env, and Note/.env.")

    try:
        import httpx  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise ConfigError("httpx is required for the live `run` command. Install repo requirements before using OpenRouter.") from exc

    primary_model = build_model_config(args, "primary")
    escalation_model = build_model_config(args, "escalation")
    existing_results = load_existing_list(artifact_paths["results"])
    existing_errors = load_existing_list(artifact_paths["errors"])
    existing_malformed = load_existing_list(artifact_paths["malformed"])
    completed_ids = {
        normalize_text(row.get("custom_id"))
        for row in existing_results + existing_errors + existing_malformed
        if normalize_text(row.get("custom_id"))
    }
    pending = [request for request in requests if normalize_text(request.get("custom_id")) not in completed_ids]

    results = list(existing_results)
    errors = list(existing_errors)
    malformed = list(existing_malformed)

    progress = {
        "updated_at": datetime.now(UTC).isoformat(),
        "total_requests": len(requests),
        "completed_results": len(results),
        "completed_errors": len(errors),
        "completed_malformed": len(malformed),
        "pending_requests": len(pending),
        "max_concurrency": args.max_concurrency,
        "primary_model": primary_model.id,
        "escalation_model": escalation_model.id if args.enable_escalation else None,
    }
    write_json(artifact_paths["progress"], progress)

    semaphore = asyncio.Semaphore(args.max_concurrency)
    write_lock = asyncio.Lock()

    async def process_one(request: Dict[str, Any], client: httpx.AsyncClient) -> None:
        custom_id = request["custom_id"]
        source_file = request["source_file"]
        prompt = request["prompt"]

        async with semaphore:
            provider_calls: List[Dict[str, Any]] = []
            parsed: Optional[Dict[str, Any]] = None
            issues: List[str] = []
            error_message = ""
            usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

            try:
                primary = await call_openrouter(client, primary_model, prompt, api_key, custom_id)
                provider_calls.append(primary)
                usage = dict(primary["usage"])
                parsed = parse_model_json(primary["raw_text"])
                ok, issues = validate_classification(parsed)
                if not ok and args.enable_escalation:
                    raise ValueError("primary_validation_failed")
            except Exception as exc:  # noqa: BLE001
                error_message = str(exc)

            if should_escalate(args, parsed or {}, issues, error_message):
                try:
                    escalation = await call_openrouter(client, escalation_model, prompt, api_key, custom_id)
                    provider_calls.append(escalation)
                    usage = {
                        "input_tokens": usage["input_tokens"] + escalation["usage"]["input_tokens"],
                        "output_tokens": usage["output_tokens"] + escalation["usage"]["output_tokens"],
                        "total_tokens": usage["total_tokens"] + escalation["usage"]["total_tokens"],
                    }
                    parsed = parse_model_json(escalation["raw_text"])
                    ok, issues = validate_classification(parsed)
                    error_message = "" if ok else error_message
                except Exception as exc:  # noqa: BLE001
                    error_message = f"{error_message}; escalation:{exc}" if error_message else f"escalation:{exc}"

            async with write_lock:
                if parsed is not None:
                    ok, issues = validate_classification(parsed)
                else:
                    ok = False
                    if not issues:
                        issues = ["no_parsed_payload"]

                row_base = {
                    "source_file": source_file,
                    "custom_id": custom_id,
                    "case_name": request.get("case_name"),
                    "input_tokens": usage["input_tokens"],
                    "output_tokens": usage["output_tokens"],
                    "provider_trace": provider_calls,
                }
                if parsed is not None:
                    row_base["classification"] = parsed
                if ok:
                    results.append(row_base)
                elif parsed is not None:
                    malformed.append({
                        **row_base,
                        "issues": issues,
                        "raw": (provider_calls[-1]["raw_text"] if provider_calls else "")[:4000],
                    })
                else:
                    errors.append({
                        **row_base,
                        "error": error_message or "unknown_error",
                        "issues": issues,
                    })

                progress.update(
                    {
                        "updated_at": datetime.now(UTC).isoformat(),
                        "completed_results": len(results),
                        "completed_errors": len(errors),
                        "completed_malformed": len(malformed),
                        "pending_requests": len(requests) - len(results) - len(errors) - len(malformed),
                    }
                )
                write_json(artifact_paths["results"], results)
                write_json(artifact_paths["errors"], errors)
                write_json(artifact_paths["malformed"], malformed)
                write_json(artifact_paths["progress"], progress)

    timeout = httpx.Timeout(args.timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        await asyncio.gather(*(process_one(request, client) for request in pending))

    return progress


def render_updates(
    manifest: Dict[str, Any],
    primary_model: ModelConfig,
    escalation_model: ModelConfig,
    artifact_paths: Dict[str, Path],
    args: argparse.Namespace,
) -> None:
    results = load_existing_list(artifact_paths["results"])
    errors = load_existing_list(artifact_paths["errors"])
    malformed = load_existing_list(artifact_paths["malformed"])
    progress = read_json(artifact_paths["progress"]) if artifact_paths["progress"].exists() else {}

    primary_cost = estimate_cost(
        primary_model,
        manifest["token_estimates"]["input_tokens"],
        manifest["token_estimates"]["output_tokens"],
    )
    disabled_wave_n = manifest["subset_scope_records"] if manifest["subset"] == "disability-wave" else None

    status_lines = [
        "# Unified Overnight OpenRouter Status",
        "",
        f"- Generated at: {manifest['generated_at']}",
        f"- Repo root: `{manifest['repo_root']}`",
        f"- Input database: `{manifest['input_db']}`",
        f"- Schema: `{manifest['schema_path']}`",
        f"- Examples: `{manifest['examples_path']}`",
        f"- Selected subset: `{manifest['subset']}`",
        f"- Selected records: {manifest['selected_records']}",
        f"- Subset scope size before pilot/limit: {manifest['subset_scope_records']}",
        f"- Counts by period: {manifest['counts_by_period']}",
        f"- Counts by bucket: {manifest['counts_by_bucket']}",
        f"- Primary model: `{primary_model.id}`",
        f"- Escalation model: `{escalation_model.id}`" if args.enable_escalation else "- Escalation model: disabled for current run",
        f"- Estimated input tokens: {manifest['token_estimates']['input_tokens']:,}",
        f"- Estimated output tokens: {manifest['token_estimates']['output_tokens']:,}",
        f"- Kimi-only estimated cost: ${primary_cost:.2f}" if primary_cost is not None else "- Kimi-only estimated cost: unavailable",
        "",
        "## Current artifacts",
        "",
        f"- Requests JSONL: `{artifact_paths['requests']}`",
        f"- Manifest JSON: `{artifact_paths['manifest']}`",
        f"- ID lookup JSON: `{artifact_paths['lookup']}`",
        f"- Results JSON: `{artifact_paths['results']}`",
        f"- Errors JSON: `{artifact_paths['errors']}`",
        f"- Malformed JSON: `{artifact_paths['malformed']}`",
    ]
    if progress:
        status_lines.extend(
            [
                "",
                "## Live progress",
                "",
                f"- Completed results: {progress.get('completed_results', 0)}",
                f"- Completed errors: {progress.get('completed_errors', 0)}",
                f"- Completed malformed: {progress.get('completed_malformed', 0)}",
                f"- Pending requests: {progress.get('pending_requests', manifest['selected_records'])}",
            ]
        )
    artifact_paths["status_md"].write_text("\n".join(status_lines) + "\n", encoding="utf-8")

    methodology_lines = [
        "# Unified Overnight OpenRouter Methodology",
        "",
        "## Scope",
        "",
        f"- This repo-local path classifies the unified overnight schema against `{resolve_input_db()}`.",
        "- It reuses the existing overnight structured prompt shape rather than the older Java full-text pipeline.",
        "- Output is constrained to the overnight schema fields already expected by the downstream merge and memo scripts.",
        "",
        "## Subsets",
        "",
        "- `pilot`: balanced deterministic sample across P1/P2/P3 from the disability-wave population; default size 36 unless `--limit` is set.",
        "- `disability-wave`: all screened disability cases with dated P1/P2/P3 placement.",
        "- `all-screened`: all screened cases with resolved outcomes.",
        "",
        "## Models",
        "",
        f"- Primary bulk model: `{primary_model.id}` with reasoning budget {primary_model.reasoning_budget} and max output {primary_model.max_output_tokens}.",
        f"- Optional escalation model: `{escalation_model.id}` with reasoning budget {escalation_model.reasoning_budget}." if args.enable_escalation else "- Optional escalation model support is built in but not enabled unless `--enable-escalation` is passed.",
        "- Escalation is intended for malformed outputs, parser failures, and optionally low-confidence results only, not a second full-pass batch.",
        "",
        "## Budget logic",
        "",
        "- Kimi pricing is hard-coded from the repo's documented OpenRouter cost table: $0.45/M input tokens and $2.20/M output tokens.",
        "- GLM 5.1 pricing is left configurable because the prior GLM experiment was explicitly documented as cost-volatile and unsuitable for uncapped bulk use.",
        "- The execution path therefore plans the full disability-wave on Kimi alone and treats GLM as a narrow reserve lane rather than part of the base budget.",
        "",
        "## Runtime behavior",
        "",
        "- Requests are built once, stored as JSONL, and assigned stable `custom_id` values from `source_file`.",
        "- The live runner is resumable: existing completed IDs in `results`, `errors`, and `malformed` are skipped automatically.",
        "- Concurrent OpenRouter calls are supported through `httpx.AsyncClient` and `asyncio`, with checkpoint writes after each completion.",
        "- The result shape matches the overnight merge contract: `source_file`, `custom_id`, token usage, and `classification`.",
    ]
    artifact_paths["methodology_md"].write_text("\n".join(methodology_lines) + "\n", encoding="utf-8")

    memo_lines = [
        "# Unified Overnight OpenRouter Execution Memo",
        "",
        "## Recommended commands",
        "",
        "```bash",
        "python3 scripts/unified_overnight_openrouter.py smoke-test --subset pilot",
        "python3 scripts/unified_overnight_openrouter.py estimate-cost --subset pilot",
        "python3 scripts/unified_overnight_openrouter.py estimate-cost --subset disability-wave",
        "python3 scripts/unified_overnight_openrouter.py run --subset pilot --max-concurrency 6 --enable-escalation --escalate-low-confidence",
        "python3 scripts/unified_overnight_openrouter.py run --subset disability-wave --max-concurrency 10",
        "python3 scripts/unified_overnight_merge.py --results results/unified_overnight_openrouter_results.json --lookup results/unified_overnight_openrouter_id_lookup.json --output results/unified_overnight_openrouter_merged.json --report results/unified_overnight_openrouter_merge_report.md",
        "```",
        "",
        "## Budget rationale",
        "",
        f"- Pilot selection size: {manifest['selected_records']} records." if manifest["subset"] == "pilot" else "- Pilot selection should be estimated separately with `--subset pilot`.",
        f"- Disability-wave scope size: {disabled_wave_n} records." if disabled_wave_n is not None else "- Full disability-wave size is available via `estimate-cost --subset disability-wave`.",
        f"- Kimi-only base estimate for the current manifest: ${primary_cost:.2f}." if primary_cost is not None else "- Kimi-only base estimate for the current manifest is unavailable until pricing is supplied.",
        "- The efficient path is to pay Kimi once for the full disability-wave and reserve GLM 5.1 only for malformed or low-confidence cases.",
        "- That keeps the bulk budget anchored to the repo's documented Kimi pricing while avoiding a repeat of the earlier uncapped GLM spend.",
        "",
        "## Current run state",
        "",
        f"- Completed good results: {len(results)}",
        f"- Errors: {len(errors)}",
        f"- Malformed outputs: {len(malformed)}",
        "- This memo is auto-generated from the same manifest used to build requests, so GitHub and methodology updates can quote it directly.",
    ]
    artifact_paths["memo_md"].write_text("\n".join(memo_lines) + "\n", encoding="utf-8")


def cmd_smoke_test(args: argparse.Namespace) -> int:
    ensure_results_dir()
    load_env_files()
    requests, id_lookup, manifest = build_requests(args)
    artifact_paths = build_artifact_paths(args.output_prefix)
    write_requests_jsonl(artifact_paths["requests"], requests[: min(len(requests), 3)])
    write_json(artifact_paths["manifest"], manifest)
    write_json(artifact_paths["lookup"], id_lookup)
    write_json(artifact_paths["results"], [])
    write_json(artifact_paths["errors"], [])
    write_json(artifact_paths["malformed"], [])
    write_json(
        artifact_paths["progress"],
        {
            "updated_at": datetime.now(UTC).isoformat(),
            "total_requests": len(requests),
            "completed_results": 0,
            "completed_errors": 0,
            "completed_malformed": 0,
            "pending_requests": len(requests),
            "api_key_loaded": bool(os.environ.get("OPENROUTER_API_KEY")),
        },
    )

    examples = read_json(resolve_examples_path())
    validated = 0
    for example in examples:
        parsed = example.get("expected_output")
        if not isinstance(parsed, dict):
            raise ConfigError("Example output is not a dict")
        ok, issues = validate_classification(parsed)
        if not ok:
            raise ConfigError(f"Example validation failed: {issues}")
        validated += 1

    primary_model = build_model_config(args, "primary")
    escalation_model = build_model_config(args, "escalation")
    render_updates(manifest, primary_model, escalation_model, artifact_paths, args)
    print(json.dumps({
        "subset": manifest["subset"],
        "selected_records": manifest["selected_records"],
        "validated_examples": validated,
        "api_key_loaded": bool(os.environ.get("OPENROUTER_API_KEY")),
        "requests_preview_written": str(artifact_paths["requests"]),
    }, indent=2))
    return 0


def cmd_estimate_cost(args: argparse.Namespace) -> int:
    ensure_results_dir()
    requests, id_lookup, manifest = build_requests(args)
    artifact_paths = build_artifact_paths(args.output_prefix)
    write_requests_jsonl(artifact_paths["requests"], requests)
    write_json(artifact_paths["manifest"], manifest)
    write_json(artifact_paths["lookup"], id_lookup)
    primary_model = build_model_config(args, "primary")
    escalation_model = build_model_config(args, "escalation")
    primary_cost = estimate_cost(
        primary_model,
        manifest["token_estimates"]["input_tokens"],
        manifest["token_estimates"]["output_tokens"],
    )
    write_json(
        artifact_paths["progress"],
        {
            "updated_at": datetime.now(UTC).isoformat(),
            "total_requests": len(requests),
            "completed_results": 0,
            "completed_errors": 0,
            "completed_malformed": 0,
            "pending_requests": len(requests),
        },
    )
    render_updates(manifest, primary_model, escalation_model, artifact_paths, args)
    print(json.dumps({
        **manifest,
        "primary_model": asdict(primary_model),
        "escalation_model": asdict(escalation_model),
        "estimated_primary_cost_usd": primary_cost,
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    ensure_results_dir()
    requests, id_lookup, manifest = build_requests(args)
    artifact_paths = build_artifact_paths(args.output_prefix)
    write_requests_jsonl(artifact_paths["requests"], requests)
    write_json(artifact_paths["manifest"], manifest)
    write_json(artifact_paths["lookup"], id_lookup)
    progress = asyncio.run(run_requests(args, requests, id_lookup, artifact_paths))
    primary_model = build_model_config(args, "primary")
    escalation_model = build_model_config(args, "escalation")
    render_updates(manifest, primary_model, escalation_model, artifact_paths, args)
    print(json.dumps(progress, indent=2, ensure_ascii=False))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    artifact_paths = build_artifact_paths(args.output_prefix)
    manifest = read_json(artifact_paths["manifest"])
    primary_model = build_model_config(args, "primary")
    escalation_model = build_model_config(args, "escalation")
    render_updates(manifest, primary_model, escalation_model, artifact_paths, args)
    status = {
        "manifest": str(artifact_paths["manifest"]),
        "status_md": str(artifact_paths["status_md"]),
        "methodology_md": str(artifact_paths["methodology_md"]),
        "memo_md": str(artifact_paths["memo_md"]),
        "results": len(load_existing_list(artifact_paths["results"])),
        "errors": len(load_existing_list(artifact_paths["errors"])),
        "malformed": len(load_existing_list(artifact_paths["malformed"])),
    }
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repo-local OpenRouter runner for the unified overnight schema")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--subset", choices=["pilot", "disability-wave", "all-screened"], default="pilot")
        subparser.add_argument("--limit", type=int, default=0)
        subparser.add_argument("--offset", type=int, default=0)
        subparser.add_argument("--only-source-files", default="")
        subparser.add_argument("--output-prefix", default="unified_overnight_openrouter")
        subparser.add_argument("--primary-model", default=PRIMARY_MODEL_DEFAULT)
        subparser.add_argument("--primary-input-cost", type=float, default=0.45)
        subparser.add_argument("--primary-output-cost", type=float, default=2.20)
        subparser.add_argument("--primary-reasoning-budget", type=int, default=0)
        subparser.add_argument("--primary-max-output-tokens", type=int, default=2400)
        subparser.add_argument("--escalation-model", default=ESCALATION_MODEL_DEFAULT)
        subparser.add_argument("--escalation-input-cost", type=float, default=None)
        subparser.add_argument("--escalation-output-cost", type=float, default=None)
        subparser.add_argument("--escalation-reasoning-budget", type=int, default=0)
        subparser.add_argument("--escalation-max-output-tokens", type=int, default=2400)
        subparser.add_argument("--enable-escalation", action="store_true")
        subparser.add_argument("--escalate-low-confidence", action="store_true")

    smoke = subparsers.add_parser("smoke-test", help="Validate schema/examples and write repo-local manifests without paid API calls")
    add_common_options(smoke)
    smoke.set_defaults(func=cmd_smoke_test)

    estimate = subparsers.add_parser("estimate-cost", help="Build requests and estimate Kimi-only spend")
    add_common_options(estimate)
    estimate.set_defaults(func=cmd_estimate_cost)

    run = subparsers.add_parser("run", help="Run the OpenRouter classification path")
    add_common_options(run)
    run.add_argument("--max-concurrency", type=int, default=8)
    run.add_argument("--timeout-seconds", type=float, default=120.0)
    run.set_defaults(func=cmd_run)

    status = subparsers.add_parser("status", help="Refresh status/methodology markdown from current artifacts")
    add_common_options(status)
    status.set_defaults(func=cmd_status)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
