#!/usr/bin/env python3
"""
Unified overnight supplemental batch workflow for the FHA unified corpus.

Primary inputs
- workspace data: data/2/FHA_Unified_Database.json
- schema doc:    data/2/unified_overnight_schema.md
- examples doc:  data/2/unified_overnight_examples.json

Commands
- dry-run
- estimate-cost
- submit
- status
- download
- export-jsonl

The script is path-aware for the Note workspace even though it lives inside the
AFFH repo's scripts/ directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import textwrap
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import anthropic  # type: ignore
except ImportError:
    anthropic = None

try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    load_dotenv = None

SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[1]
WORKSPACE_ROOT = SCRIPT_PATH.parents[2]
DATA_DIR = WORKSPACE_ROOT / "data" / "2"
RESULTS_DIR = WORKSPACE_ROOT / "results"
INPUT_DB = DATA_DIR / "FHA_Unified_Database.json"
SCHEMA_PATH = DATA_DIR / "unified_overnight_schema.md"
EXAMPLES_PATH = DATA_DIR / "unified_overnight_examples.json"
OUTPUT_PATH = DATA_DIR / "unified_overnight_results.json"
ERROR_LOG = DATA_DIR / "unified_overnight_errors.json"
MALFORMED_LOG = DATA_DIR / "unified_overnight_malformed.json"
BATCH_ID_FILE = DATA_DIR / "unified_overnight_batch_id.txt"
ID_LOOKUP_FILE = DATA_DIR / "unified_overnight_id_lookup.json"
REQUEST_EXPORT_DEFAULT = DATA_DIR / "unified_overnight_requests.jsonl"
BATCH_META_FILE = DATA_DIR / "unified_overnight_batch_meta.json"
SUBMISSION_LOG = RESULTS_DIR / "unified_overnight_submission_log.md"

MODEL = os.environ.get("UNIFIED_OVERNIGHT_MODEL", "claude-haiku-4-5")
TEMPERATURE = 0.0
MAX_OUTPUT_TOKENS = int(os.environ.get("UNIFIED_OVERNIGHT_MAX_TOKENS", "650"))
DEFAULT_OUTPUT_TOKENS_EST = int(os.environ.get("UNIFIED_OVERNIGHT_EST_OUTPUT_TOKENS", "260"))
DEFAULT_INPUT_CHARS_PER_TOKEN = float(os.environ.get("UNIFIED_OVERNIGHT_CHARS_PER_TOKEN", "4.0"))
MAX_REASONING_CHARS = 1200

BATCH_PRICE_TABLE = {
    "claude-haiku-4-5": {"input": 0.40, "output": 2.00},
    "claude-3-5-haiku-20241022": {"input": 0.40, "output": 2.00},
    "claude-sonnet-4-20250514": {"input": 1.50, "output": 7.50},
}

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


@dataclass
class BatchSelection:
    records: List[Dict[str, Any]]
    counts_by_bucket: Counter
    total_records: int
    total_requests: int


class ConfigError(RuntimeError):
    pass


def load_env() -> None:
    if load_dotenv is None:
        return
    env_candidates = [
        WORKSPACE_ROOT / ".env",
        WORKSPACE_ROOT / "fha-research" / ".env",
        REPO_ROOT / ".env",
    ]
    for candidate in env_candidates:
        if candidate.exists():
            load_dotenv(candidate, override=False)


def ensure_paths() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_DB.exists():
        raise ConfigError(f"Input database not found: {INPUT_DB}")
    if not SCHEMA_PATH.exists():
        raise ConfigError(f"Schema file not found: {SCHEMA_PATH}")
    if not EXAMPLES_PATH.exists():
        raise ConfigError(f"Examples file not found: {EXAMPLES_PATH}")


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
    fields = {
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
    return fields


def load_schema_and_examples() -> Tuple[str, str]:
    schema_text = SCHEMA_PATH.read_text(encoding="utf-8").strip()
    examples = read_json(EXAMPLES_PATH)
    examples_text = json.dumps(examples, indent=2, ensure_ascii=False)
    return schema_text, examples_text


def infer_bucket(record: Dict[str, Any]) -> str:
    defendant_type = (record.get("defendant_type") or "").upper()
    housing_type = (record.get("housing_type") or "").upper()
    plaintiff_type = (record.get("plaintiff_type") or "").upper()
    claim_types = " ".join(record.get("claim_types") or []).upper()
    brief = f"{record.get('brief_summary', '')} {record.get('key_holding', '')}".upper()

    if bool(record.get("disability_alleged")):
        return "disability"
    if bool(record.get("pro_se")):
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


def select_records(records: Sequence[Dict[str, Any]], args: argparse.Namespace) -> BatchSelection:
    screened = [r for r in records if (not args.screened_only) or r.get("screening_result") == "YES"]

    if args.bucket == "all":
        selected = list(screened)
    else:
        selected = [r for r in screened if infer_bucket(r) == args.bucket]

    if args.only_source_files:
        allowed = {item.strip() for item in args.only_source_files.split(",") if item.strip()}
        selected = [r for r in selected if r.get("source_file") in allowed]

    if args.offset:
        selected = selected[args.offset :]
    if args.limit:
        selected = selected[: args.limit]

    counts = Counter(infer_bucket(r) for r in selected)
    return BatchSelection(
        records=selected,
        counts_by_bucket=counts,
        total_records=len(screened),
        total_requests=len(selected),
    )


def make_custom_id(source_file: str, index: int) -> str:
    digest = hashlib.md5(source_file.encode("utf-8")).hexdigest()[:12]
    return f"uob-{index:04d}-{digest}"


def estimate_tokens_from_text(text: str) -> int:
    if not text:
        return 0
    return int(math.ceil(len(text) / DEFAULT_INPUT_CHARS_PER_TOKEN))


def estimate_request_tokens(payload: Dict[str, Any], schema_text: str, examples_text: str) -> int:
    prompt = USER_PROMPT_TEMPLATE.format(
        schema_text=schema_text,
        examples_text=examples_text,
        case_data=json.dumps(payload, indent=2, ensure_ascii=False),
    )
    return estimate_tokens_from_text(SYSTEM_PROMPT) + estimate_tokens_from_text(prompt)


def build_requests(args: argparse.Namespace) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    ensure_paths()
    load_env()
    records = read_json(INPUT_DB)
    schema_text, examples_text = load_schema_and_examples()
    selection = select_records(records, args)

    requests: List[Dict[str, Any]] = []
    id_lookup: Dict[str, Any] = {}
    token_estimates = {
        "input_tokens": 0,
        "output_tokens": 0,
    }

    for index, record in enumerate(selection.records):
        source_file = record.get("source_file") or f"record_{index}"
        case_fields = extract_case_fields(record)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            schema_text=schema_text,
            examples_text=examples_text,
            case_data=json.dumps(case_fields, indent=2, ensure_ascii=False),
        )
        custom_id = make_custom_id(source_file, index)
        estimated_input = estimate_request_tokens(case_fields, schema_text, examples_text)
        token_estimates["input_tokens"] += estimated_input
        token_estimates["output_tokens"] += DEFAULT_OUTPUT_TOKENS_EST

        id_lookup[custom_id] = {
            "source_file": source_file,
            "case_name": record.get("case_name"),
            "bucket": infer_bucket(record),
            "year": record.get("year"),
            "estimated_input_tokens": estimated_input,
        }
        requests.append(
            {
                "custom_id": custom_id,
                "params": {
                    "model": MODEL,
                    "max_tokens": MAX_OUTPUT_TOKENS,
                    "temperature": TEMPERATURE,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            }
        )

    manifest = {
        "workspace_root": str(WORKSPACE_ROOT),
        "repo_root": str(REPO_ROOT),
        "input_db": str(INPUT_DB),
        "schema_path": str(SCHEMA_PATH),
        "examples_path": str(EXAMPLES_PATH),
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "screened_only": args.screened_only,
        "bucket": args.bucket,
        "limit": args.limit,
        "offset": args.offset,
        "shard_size": args.shard_size,
        "only_source_files": args.only_source_files,
        "selected_records": selection.total_requests,
        "total_screened_scope": selection.total_records,
        "bucket_counts": dict(selection.counts_by_bucket),
        "token_estimates": token_estimates,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    return requests, id_lookup, manifest


def estimate_costs(token_estimates: Dict[str, int], model: str) -> Dict[str, Any]:
    pricing = BATCH_PRICE_TABLE.get(model, BATCH_PRICE_TABLE["claude-haiku-4-5"])
    input_m = token_estimates["input_tokens"] / 1_000_000
    output_m = token_estimates["output_tokens"] / 1_000_000
    return {
        "model": model,
        "estimated_input_tokens": token_estimates["input_tokens"],
        "estimated_output_tokens": token_estimates["output_tokens"],
        "estimated_cost_usd": round(input_m * pricing["input"] + output_m * pricing["output"], 4),
        "pricing_per_million": pricing,
        "token_estimation_method": f"characters/{DEFAULT_INPUT_CHARS_PER_TOKEN} + fixed output token estimate {DEFAULT_OUTPUT_TOKENS_EST}",
    }


def shard_requests(requests: Sequence[Dict[str, Any]], shard_size: int) -> List[List[Dict[str, Any]]]:
    if shard_size <= 0:
        return [list(requests)]
    return [list(requests[i : i + shard_size]) for i in range(0, len(requests), shard_size)]


def require_anthropic() -> None:
    if anthropic is None:
        raise ConfigError("anthropic package not installed. Install it before submit/status/download.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ConfigError("ANTHROPIC_API_KEY is not set. submit/status/download require a live API key.")


def get_client():
    load_env()
    require_anthropic()
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def write_batch_files(batch_ids: List[str], id_lookup: Dict[str, Any], meta: Dict[str, Any]) -> None:
    BATCH_ID_FILE.write_text("\n".join(batch_ids) + "\n", encoding="utf-8")
    write_json(ID_LOOKUP_FILE, id_lookup)
    write_json(BATCH_META_FILE, meta)


def append_submission_log(meta: Dict[str, Any], batch_ids: List[str], cost_info: Dict[str, Any]) -> None:
    lines = [
        f"# Unified Overnight Submission Log",
        "",
        f"- Timestamp (UTC): {meta['generated_at']}",
        f"- Model: {meta['model']}",
        f"- Bucket: {meta['bucket']}",
        f"- Selected records: {meta['selected_records']}",
        f"- Shard size: {meta['shard_size']}",
        f"- Estimated input tokens: {cost_info['estimated_input_tokens']:,}",
        f"- Estimated output tokens: {cost_info['estimated_output_tokens']:,}",
        f"- Estimated batch cost: ${cost_info['estimated_cost_usd']:.2f}",
        "- Batch IDs:",
    ]
    lines.extend([f"  - {batch_id}" for batch_id in batch_ids])
    SUBMISSION_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_dry_run(args: argparse.Namespace) -> int:
    requests, id_lookup, manifest = build_requests(args)
    cost_info = estimate_costs(manifest["token_estimates"], MODEL)
    print(f"Workspace root: {WORKSPACE_ROOT}")
    print(f"Input DB: {INPUT_DB}")
    print(f"Schema: {SCHEMA_PATH.name}")
    print(f"Examples: {EXAMPLES_PATH.name}")
    print(f"Selected records: {len(requests)} / {manifest['total_screened_scope']}")
    print(f"Bucket filter: {manifest['bucket']}")
    print(f"Bucket counts in selection: {dict(manifest['bucket_counts'])}")
    print(f"Estimated input tokens: {cost_info['estimated_input_tokens']:,}")
    print(f"Estimated output tokens: {cost_info['estimated_output_tokens']:,}")
    print(f"Estimated cost: ${cost_info['estimated_cost_usd']:.2f}")
    for i, request in enumerate(requests[: args.preview]):
        lookup = id_lookup[request['custom_id']]
        prompt = request['params']['messages'][0]['content']
        print("-" * 80)
        print(f"Preview {i + 1}: {lookup['source_file']}")
        print(f"  case_name: {lookup.get('case_name')}")
        print(f"  bucket: {lookup.get('bucket')}")
        print(f"  est_input_tokens: {lookup.get('estimated_input_tokens')}")
        print(textwrap.shorten(prompt.replace("\n", " "), width=420, placeholder=" ..."))
    return 0


def cmd_estimate_cost(args: argparse.Namespace) -> int:
    _, _, manifest = build_requests(args)
    cost_info = estimate_costs(manifest["token_estimates"], MODEL)
    print(json.dumps({**manifest, "cost_estimate": cost_info}, indent=2, ensure_ascii=False))
    return 0


def cmd_export_jsonl(args: argparse.Namespace) -> int:
    requests, id_lookup, manifest = build_requests(args)
    export_path = Path(args.output) if args.output else REQUEST_EXPORT_DEFAULT
    with export_path.open("w", encoding="utf-8") as fh:
        for request in requests:
            fh.write(json.dumps(request, ensure_ascii=False) + "\n")
    write_json(ID_LOOKUP_FILE, id_lookup)
    write_json(BATCH_META_FILE, manifest)
    print(f"Exported {len(requests)} requests to {export_path}")
    print(f"Lookup written to {ID_LOOKUP_FILE}")
    print(f"Manifest written to {BATCH_META_FILE}")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    requests, id_lookup, manifest = build_requests(args)
    if not requests:
        print("No requests selected; nothing to submit.")
        return 1
    client = get_client()
    shards = shard_requests(requests, args.shard_size)
    batch_ids: List[str] = []
    for idx, shard in enumerate(shards, start=1):
        batch = client.messages.batches.create(requests=shard)
        batch_ids.append(batch.id)
        print(f"Submitted shard {idx}/{len(shards)}: {batch.id} ({len(shard)} requests)")
    cost_info = estimate_costs(manifest["token_estimates"], MODEL)
    meta = {**manifest, "batch_ids": batch_ids}
    write_batch_files(batch_ids, id_lookup, meta)
    append_submission_log(meta, batch_ids, cost_info)
    print(f"Saved batch IDs to {BATCH_ID_FILE}")
    print(f"Saved lookup to {ID_LOOKUP_FILE}")
    print(f"Estimated batch cost: ${cost_info['estimated_cost_usd']:.2f}")
    return 0


def load_batch_ids() -> List[str]:
    if not BATCH_ID_FILE.exists():
        raise ConfigError(f"Batch ID file not found: {BATCH_ID_FILE}")
    return [line.strip() for line in BATCH_ID_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def cmd_status(_: argparse.Namespace) -> int:
    client = get_client()
    batch_ids = load_batch_ids()
    total_succeeded = total_processing = total_errored = total_canceled = total_expired = 0
    for index, batch_id in enumerate(batch_ids, start=1):
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts
        total_succeeded += counts.succeeded
        total_processing += counts.processing
        total_errored += counts.errored
        total_canceled += counts.canceled
        total_expired += counts.expired
        total = counts.processing + counts.succeeded + counts.errored + counts.canceled + counts.expired
        print(
            f"Shard {index}/{len(batch_ids)} {batch_id}: status={batch.processing_status} "
            f"succeeded={counts.succeeded}/{total} processing={counts.processing} "
            f"errored={counts.errored} canceled={counts.canceled} expired={counts.expired}"
        )
    print(
        f"Overall: succeeded={total_succeeded} processing={total_processing} errored={total_errored} "
        f"canceled={total_canceled} expired={total_expired}"
    )
    return 0


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


def parse_model_json(raw_text: str) -> Dict[str, Any]:
    candidate = extract_first_json_object(raw_text)
    parsed = json.loads(candidate)
    return parsed


def normalize_array(values: Any) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return []
    normalized = []
    seen = set()
    for item in values:
        if not isinstance(item, str):
            continue
        token = item.strip()
        if token and token not in seen:
            normalized.append(token)
            seen.add(token)
    return normalized


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
    if not isinstance(payload.get("reasoning"), str) or not payload["reasoning"].strip():
        issues.append("reasoning:empty")
    if len(payload.get("reasoning", "")) > MAX_REASONING_CHARS:
        issues.append("reasoning:too_long")
    for array_key in ["institutional_function_missing", "administratively_observable_fact_pattern"]:
        normalized = normalize_array(payload.get(array_key))
        if not normalized:
            issues.append(f"{array_key}:empty_or_invalid")
        payload[array_key] = normalized
    return len(issues) == 0, issues


def iter_batch_results(client: Any, batch_id: str) -> Iterable[Any]:
    return client.messages.batches.results(batch_id)


def cmd_download(_: argparse.Namespace) -> int:
    client = get_client()
    batch_ids = load_batch_ids()
    id_lookup = read_json(ID_LOOKUP_FILE) if ID_LOOKUP_FILE.exists() else {}
    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    malformed: List[Dict[str, Any]] = []
    total_input_tokens = 0
    total_output_tokens = 0

    for batch_id in batch_ids:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status != "ended":
            raise ConfigError(f"Batch {batch_id} is not complete yet: {batch.processing_status}")
        for result in iter_batch_results(client, batch_id):
            lookup = id_lookup.get(result.custom_id, {"source_file": result.custom_id})
            source_file = lookup.get("source_file", result.custom_id)
            if result.result.type != "succeeded":
                errors.append({
                    "source_file": source_file,
                    "custom_id": result.custom_id,
                    "error": f"result_type:{result.result.type}",
                })
                continue
            message = result.result.message
            total_input_tokens += getattr(message.usage, "input_tokens", 0)
            total_output_tokens += getattr(message.usage, "output_tokens", 0)
            raw_text = "\n".join(block.text for block in message.content if hasattr(block, "text"))
            try:
                parsed = parse_model_json(raw_text)
                ok, issues = validate_classification(parsed)
                if not ok:
                    malformed.append({
                        "source_file": source_file,
                        "custom_id": result.custom_id,
                        "issues": issues,
                        "raw": raw_text[:4000],
                        "parsed": parsed,
                    })
                results.append({
                    "source_file": source_file,
                    "custom_id": result.custom_id,
                    "input_tokens": getattr(message.usage, "input_tokens", 0),
                    "output_tokens": getattr(message.usage, "output_tokens", 0),
                    "classification": parsed,
                })
            except Exception as exc:  # noqa: BLE001
                errors.append({
                    "source_file": source_file,
                    "custom_id": result.custom_id,
                    "error": str(exc),
                    "raw": raw_text[:4000],
                })

    write_json(OUTPUT_PATH, results)
    write_json(ERROR_LOG, errors)
    write_json(MALFORMED_LOG, malformed)
    pricing = estimate_costs({"input_tokens": total_input_tokens, "output_tokens": total_output_tokens}, MODEL)
    print(f"Downloaded results: {len(results)}")
    print(f"Errors: {len(errors)}")
    print(f"Malformed-but-parsed: {len(malformed)}")
    print(f"Actual-ish tokens from API: {total_input_tokens:,} input / {total_output_tokens:,} output")
    print(f"Estimated cost from API token totals: ${pricing['estimated_cost_usd']:.2f}")
    print(f"Results written to {OUTPUT_PATH}")
    print(f"Error log written to {ERROR_LOG}")
    print(f"Malformed log written to {MALFORMED_LOG}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified overnight structured-data batch workflow")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_selection_options(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--bucket", choices=["all", "disability", "pro_se", "public", "institutional", "remaining"], default="all")
        subparser.add_argument("--limit", type=int, default=0, help="Limit selected records after filtering")
        subparser.add_argument("--offset", type=int, default=0, help="Skip N selected records after filtering")
        subparser.add_argument("--only-source-files", default="", help="Comma-separated exact source_file values for subset reruns")
        subparser.add_argument("--shard-size", type=int, default=300, help="Requests per shard for submit/export planning")
        subparser.add_argument("--all-records", action="store_false", dest="screened_only", help="Include non-screened records too")
        subparser.set_defaults(screened_only=True)

    dry_run = subparsers.add_parser("dry-run", help="Build requests locally and print a preview")
    add_selection_options(dry_run)
    dry_run.add_argument("--preview", type=int, default=3, help="How many request previews to print")
    dry_run.set_defaults(func=cmd_dry_run)

    estimate = subparsers.add_parser("estimate-cost", help="Estimate token volume and batch cost")
    add_selection_options(estimate)
    estimate.set_defaults(func=cmd_estimate_cost)

    export = subparsers.add_parser("export-jsonl", help="Export requests to JSONL for inspection/debugging")
    add_selection_options(export)
    export.add_argument("--output", default="", help="Optional output JSONL path")
    export.set_defaults(func=cmd_export_jsonl)

    submit = subparsers.add_parser("submit", help="Submit one or more Anthropic message batches")
    add_selection_options(submit)
    submit.set_defaults(func=cmd_submit)

    status = subparsers.add_parser("status", help="Check saved batch IDs")
    status.set_defaults(func=cmd_status)

    download = subparsers.add_parser("download", help="Download completed batch results")
    download.set_defaults(func=cmd_download)

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
