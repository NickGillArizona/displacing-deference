#!/usr/bin/env python3
"""
Build a raw-text target inventory for the unified overnight run.

Outputs:
- data/2/unified_raw_text_target_inventory.json

Usage:
  python3 unified_raw_text_target_inventory.py
"""

from __future__ import annotations

import csv
import difflib
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SHORT_SUMMARY_THRESHOLD = 700
FUZZY_MATCH_THRESHOLD = 0.74
EXPORT_LIMIT_PER_BUCKET = 250
PUBLIC_DEFENDANTS = {"MUNICIPALITY", "HOUSING_AUTHORITY", "GOVERNMENT"}
OPEN_TEXTURED_CLAIM_TYPES = {"disparate_impact", "other", "interference_coercion", "retaliation", "UNCLEAR", "UNDETERMINED"}
PLEADING_AUTHORITIES = {
    "ashcroft v. iqbal",
    "bell atlantic corp. v. twombly",
    "bell atlantic corp v. twombly",
    "lujan v. defenders of wildlife",
    "celotex corp. v. catrett",
    "anderson v. liberty lobby, inc.",
}
SUBSTANTIVE_AUTHORITIES = {
    "havens realty corp. v. coleman",
    "city of cleburne v. cleburne living center",
    "giebeler v. m & b associates",
    "dubois v. ass'n of apartment owners of 2987 kalakaua",
    "bhogaita v. altamonte heights condo. ass'n, inc.",
    "schwarz v. city of treasure island",
    "hollis v. chestnut bend homeowners ass'n",
    "city of edmonds v. oxford house, inc.",
    "texas dep't of hous. & cmty. affairs v. inclusive communities project, inc.",
}


def workspace_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    explicit = os.environ.get("FHA_WORKSPACE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    return repo_root.parent


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    ws = workspace_root() / "data" / "2"
    if ws.exists():
        return ws
    return repo_root() / "data"


def unified_db_path() -> Path:
    return data_dir() / "FHA_Unified_Database.json"


def metadata_csv_path() -> Path:
    return data_dir() / "FHA_Cases_Metadata.csv"


def raw_text_dir() -> Path:
    candidates = [workspace_root() / "allFHAcases", workspace_root() / "fhaCases", repo_root() / "data" / "cases"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"\bet al\.?\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def case_name_slug(text: str) -> str:
    text = slugify(text)
    stopwords = {
        "the", "of", "and", "inc", "llc", "corp", "corporation", "company", "co", "assoc", "association",
        "assn", "authority", "city", "county", "township", "department", "dept", "board", "homeowners",
        "owners", "housing", "america", "united", "states", "state", "et", "al"
    }
    return " ".join(token for token in text.split() if token not in stopwords)


def load_database() -> List[dict]:
    with unified_db_path().open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_metadata_rows() -> List[dict]:
    path = metadata_csv_path()
    encodings = ["utf-8-sig", "cp1252", "latin-1"]
    last_error = None
    for encoding in encodings:
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return list(csv.DictReader(handle))
        except UnicodeDecodeError as exc:
            last_error = exc
    raise RuntimeError(f"Could not decode metadata CSV: {path} ({last_error})")


def screened_cases(records: List[dict]) -> List[dict]:
    return [r for r in records if r.get("screening_result") == "YES" and r.get("case_name")]


def summary_text(case: dict) -> str:
    return " ".join(part.strip() for part in [case.get("brief_summary") or "", case.get("key_holding") or ""] if part and part.strip())


def boolish(value) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    return text not in {"", "0", "false", "none", "no", "n/a", "unknown"}


def normalize_authority(raw: str) -> str:
    raw = unicodedata.normalize("NFKD", raw or "").encode("ascii", "ignore").decode("ascii")
    raw = raw.strip()
    match = re.search(r"([A-Za-z0-9'&.\- ]+?\s+v\.?\s+[A-Za-z0-9'&.\- ]+?)(?=,\s*\d|\s*\(\d{4}\)|$)", raw)
    if match:
        raw = match.group(1)
    return raw.replace(" v ", " v. ").replace("  ", " ").strip().lower()


def load_raw_text_index() -> Dict[str, Path]:
    directory = raw_text_dir()
    if not directory.exists():
        return {}
    index: Dict[str, Path] = {}
    for entry in directory.iterdir():
        if entry.is_file() and entry.suffix.lower() == ".txt":
            index[entry.stem.lower()] = entry
    return index


def build_metadata_index(rows: List[dict]) -> Tuple[Dict[Tuple[str, str], List[dict]], Dict[str, List[Tuple[str, dict]]]]:
    by_exact = defaultdict(list)
    by_year = defaultdict(list)
    for row in rows:
        year = (row.get("Date Filed") or "")[:4]
        name_slug = case_name_slug(row.get("Case Name") or "")
        by_exact[(name_slug, year)].append(row)
        by_year[year].append((name_slug, row))
    return by_exact, by_year


def resolve_raw_text(case: dict, raw_index: Dict[str, Path], metadata_exact, metadata_by_year) -> Tuple[Optional[str], str, float, Optional[str]]:
    source_file = (case.get("source_file") or "").strip()
    if source_file:
        direct = raw_index.get(source_file.lower())
        if direct:
            return str(direct), "source_file_exact", 1.0, source_file
        direct = raw_index.get(Path(source_file).stem.lower())
        if direct:
            return str(direct), "source_file_stem", 1.0, source_file

    case_slug = case_name_slug(case.get("case_name") or "")
    year = str(case.get("year") or "")
    exact_rows = metadata_exact.get((case_slug, year), [])
    for row in exact_rows:
        filename = row.get("File Name") or ""
        path = raw_index.get(Path(filename).stem.lower())
        if path:
            return str(path), "metadata_exact", 0.95, filename

    best_score = 0.0
    best_row = None
    for candidate_slug, row in metadata_by_year.get(year, []):
        score = difflib.SequenceMatcher(None, case_slug, candidate_slug).ratio()
        if score > best_score:
            best_score = score
            best_row = row
    if best_row and best_score >= FUZZY_MATCH_THRESHOLD:
        filename = best_row.get("File Name") or ""
        path = raw_index.get(Path(filename).stem.lower())
        if path:
            return str(path), "metadata_fuzzy", round(best_score, 3), filename

    if case_slug:
        tokens = set(case_slug.split())
        year_fragment = f"_{year}_" if year else ""
        best_path = None
        best_score = 0.0
        for stem, path in raw_index.items():
            if year_fragment and year_fragment not in path.name:
                continue
            filename_slug = case_name_slug(path.stem)
            shared = len(tokens & set(filename_slug.split()))
            score = difflib.SequenceMatcher(None, case_slug, filename_slug).ratio()
            if shared >= 2 and score > best_score:
                best_path = path
                best_score = score
        if best_path and best_score >= 0.82:
            return str(best_path), "filename_token_scan", round(best_score, 3), best_path.name

    return None, "unresolved", 0.0, None


def base_entry(case: dict, raw_path: Optional[str], match_strategy: str, match_confidence: float, matched_filename: Optional[str], reasons: List[str], score: float) -> dict:
    return {
        "case_name": case.get("case_name"),
        "source_file": case.get("source_file"),
        "year": case.get("year"),
        "court": case.get("court"),
        "circuit": case.get("circuit"),
        "procedural_posture": case.get("procedural_posture"),
        "outcome": case.get("outcome"),
        "plaintiff_type": case.get("plaintiff_type"),
        "defendant_type": case.get("defendant_type"),
        "primary_claim_type": case.get("primary_claim_type"),
        "pro_se": case.get("pro_se"),
        "citation_count": len(case.get("key_cases_cited") or []),
        "summary_length": len(summary_text(case)),
        "raw_text_path": raw_path,
        "raw_text_available": bool(raw_path),
        "match_strategy": match_strategy,
        "match_confidence": match_confidence,
        "matched_filename": matched_filename,
        "priority_score": round(score, 3),
        "reasons": reasons,
    }


def main() -> None:
    db = load_database()
    cases = screened_cases(db)
    metadata_rows = load_metadata_rows()
    raw_index = load_raw_text_index()
    metadata_exact, metadata_by_year = build_metadata_index(metadata_rows)

    buckets = {
        "tiny_summaries": [],
        "likely_ambiguous_pleading_losses": [],
        "public_defendant_process_cases": [],
        "open_textured_cases_with_nontrivial_citations": [],
        "citation_differential_exemplars": [],
    }

    resolution_counter = Counter()
    unresolved = []

    for case in cases:
        raw_path, strategy, confidence, matched_filename = resolve_raw_text(case, raw_index, metadata_exact, metadata_by_year)
        resolution_counter[strategy] += 1
        if not raw_path:
            unresolved.append(case.get("source_file") or case.get("case_name"))

        text = summary_text(case)
        summary_len = len(text)
        claim_types = [str(item).strip() for item in (case.get("claim_types") or []) if str(item).strip()]
        normalized_authorities = {normalize_authority(item) for item in (case.get("key_cases_cited") or []) if isinstance(item, str) and item.strip()}
        has_pleading_authority = bool(normalized_authorities & PLEADING_AUTHORITIES)
        has_substantive_authority = bool(normalized_authorities & SUBSTANTIVE_AUTHORITIES)
        open_textured = (
            case.get("primary_claim_type") in OPEN_TEXTURED_CLAIM_TYPES
            or any("3608" in item or "affirmatively further" in item.lower() for item in claim_types)
        )
        public_process = (
            case.get("defendant_type") in PUBLIC_DEFENDANTS
            and (
                boolish(case.get("interactive_process_discussed"))
                or case.get("primary_claim_type") in {"reasonable_accommodation_denial", "reasonable_modification_denial"}
                or "accommodation" in text.lower()
                or "request" in text.lower()
                or "process" in text.lower()
            )
        )
        likely_pleading_loss = case.get("procedural_posture") == "MOTION_TO_DISMISS" and case.get("outcome") in {"DEFENDANT_WIN", "PROCEDURAL"}

        if summary_len <= SHORT_SUMMARY_THRESHOLD:
            reasons = [f"combined summary length={summary_len}", "candidate for raw-text reopening because structured summary is unusually short"]
            score = 1.0 + (0.5 if raw_path else 0.0) + min(len(normalized_authorities), 5) * 0.05
            buckets["tiny_summaries"].append(base_entry(case, raw_path, strategy, confidence, matched_filename, reasons, score))

        if likely_pleading_loss:
            ambiguity_score = 1.0
            reasons = ["motion-to-dismiss loss"]
            if case.get("pro_se") is True:
                ambiguity_score += 0.8
                reasons.append("pro se plaintiff")
            if has_pleading_authority:
                ambiguity_score += 0.6
                reasons.append("pleading-plausibility authority cited")
            if len(claim_types) >= 2:
                ambiguity_score += 0.4
                reasons.append("multiple claim types")
            if summary_len <= 850:
                ambiguity_score += 0.4
                reasons.append("compressed structured summary")
            if not case.get("fha_section_cited"):
                ambiguity_score += 0.2
                reasons.append("missing FHA section citation")
            if ambiguity_score >= 2.0:
                buckets["likely_ambiguous_pleading_losses"].append(base_entry(case, raw_path, strategy, confidence, matched_filename, reasons, ambiguity_score))

        if public_process:
            reasons = ["public or quasi-public defendant", "accommodation/process signal in structured fields"]
            score = 1.5 + (0.4 if boolish(case.get("interactive_process_discussed")) else 0.0) + (0.4 if raw_path else 0.0)
            if has_substantive_authority:
                score += 0.3
                reasons.append("substantive FHA/disability authority present")
            buckets["public_defendant_process_cases"].append(base_entry(case, raw_path, strategy, confidence, matched_filename, reasons, score))

        if open_textured and len(normalized_authorities) >= 3:
            reasons = ["open-textured claim proxy", f"nontrivial citation count={len(normalized_authorities)}"]
            score = 1.2 + min(len(normalized_authorities), 8) * 0.12 + (0.4 if raw_path else 0.0)
            if case.get("defendant_type") in PUBLIC_DEFENDANTS:
                score += 0.25
                reasons.append("public-defendant overlap")
            buckets["open_textured_cases_with_nontrivial_citations"].append(base_entry(case, raw_path, strategy, confidence, matched_filename, reasons, score))

        if len(normalized_authorities) >= 5 and has_pleading_authority and has_substantive_authority:
            reasons = ["mixed procedural and substantive citation profile", f"normalized citation count={len(normalized_authorities)}"]
            score = 1.5 + min(len(normalized_authorities), 10) * 0.15 + (0.4 if raw_path else 0.0)
            if likely_pleading_loss:
                score += 0.35
                reasons.append("also a pleading-stage loss")
            buckets["citation_differential_exemplars"].append(base_entry(case, raw_path, strategy, confidence, matched_filename, reasons, score))

    bucket_totals = {name: len(entries) for name, entries in buckets.items()}
    bucket_raw_totals = {name: sum(1 for entry in entries if entry["raw_text_available"]) for name, entries in buckets.items()}

    for name in buckets:
        buckets[name].sort(key=lambda item: (-item["priority_score"], not item["raw_text_available"], item["year"] or 0, item["case_name"] or ""))
        buckets[name] = buckets[name][:EXPORT_LIMIT_PER_BUCKET]

    output = {
        "workspace_root": str(workspace_root()),
        "unified_db_path": str(unified_db_path()),
        "metadata_csv_path": str(metadata_csv_path()),
        "raw_text_dir": str(raw_text_dir()),
        "screened_case_count": len(cases),
        "raw_text_resolution_counts": dict(resolution_counter),
        "raw_text_resolved_cases": sum(1 for strategy, count in resolution_counter.items() if strategy != "unresolved" for _ in range(count)),
        "bucket_counts_total": bucket_totals,
        "bucket_raw_text_available_counts_total": bucket_raw_totals,
        "bucket_export_limit": EXPORT_LIMIT_PER_BUCKET,
        "bucket_counts_exported": {name: len(entries) for name, entries in buckets.items()},
        "bucket_raw_text_available_counts_exported": {name: sum(1 for entry in entries if entry["raw_text_available"]) for name, entries in buckets.items()},
        "buckets": buckets,
        "unresolved_examples": unresolved[:100],
    }

    out_path = data_dir() / "unified_raw_text_target_inventory.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, ensure_ascii=False)

    print(f"Wrote {out_path}")
    print(f"Raw text resolved for {output['raw_text_resolved_cases']} of {len(cases)} screened cases")
    for bucket, count in output["bucket_counts_total"].items():
        exported = output["bucket_counts_exported"][bucket]
        raw_hits = output["bucket_raw_text_available_counts_total"][bucket]
        print(f"{bucket}: {count} total targets, {exported} exported, {raw_hits} with raw text")


if __name__ == "__main__":
    main()
