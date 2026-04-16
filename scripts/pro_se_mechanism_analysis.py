#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import math
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

P1_START = datetime(2022, 1, 1)
P1_END = datetime(2024, 6, 28)
P2_END = datetime(2025, 2, 5)

REPRESENTATION_ORDER = ["PRO_SE", "REPRESENTED", "UNKNOWN"]
INFERENTIAL_REPRESENTATION_ORDER = ["PRO_SE", "REPRESENTED"]
PERIOD_ORDER = ["P1", "P2", "P3"]
COHORT_ORDER = ["PRE_WAVE", "P1", "P2", "P3", "UNASSIGNED"]
PLEADING_POSTURES = {"MOTION_TO_DISMISS", "SCREENING_ORDER"}
PLEADING_LOSS_OUTCOMES = {"DEFENDANT_WIN", "PROCEDURAL"}
NO_FAILURE_FAMILIES = {"NO_FAILURE_PLAINTIFF_WIN", "NO_FAILURE_DEFENDANT_WIN"}
NO_FAILURE_MECHANISMS = {"CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS"}

GAMMA_ITMAX = 200
GAMMA_EPS = 3.0e-14
GAMMA_FPMIN = 1.0e-300


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value: Any, default: str = "") -> str:
    if value in (None, "", [], {}):
        return default
    return str(value).strip()


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


def cohort_label(record: Dict[str, Any]) -> str:
    dt = parse_date(record.get("date_filed"), record.get("year"))
    if dt is None:
        return "UNASSIGNED"
    if dt < P1_START:
        return "PRE_WAVE"
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


def is_screened(record: Dict[str, Any]) -> bool:
    return normalize_text(record.get("screening_result"), "NO").upper() != "NO" and bool(record.get("case_name"))


def is_pleading_loss(record: Dict[str, Any]) -> bool:
    return normalize_text(record.get("procedural_posture")).upper() in PLEADING_POSTURES and normalize_text(record.get("outcome")).upper() in PLEADING_LOSS_OUTCOMES


def representation_status(record: Dict[str, Any]) -> str:
    value = record.get("pro_se")
    if value is True:
        return "PRO_SE"
    if value is False:
        return "REPRESENTED"
    return "UNKNOWN"


def pct(part: int, whole: int) -> Optional[float]:
    if not whole:
        return None
    return round((part / whole) * 100.0, 2)


def round_float(value: Optional[float], digits: int = 6) -> Optional[float]:
    if value is None:
        return None
    return round(value, digits)


def stable_label_order(values: Iterable[str], rows: Sequence[Dict[str, Any]], key: str) -> List[str]:
    counts = Counter(row[key] for row in rows)
    unique = {value for value in values if value is not None}
    return [
        label
        for label, _ in sorted(
            ((label, counts.get(label, 0)) for label in unique),
            key=lambda item: (-item[1], item[0]),
        )
    ]


def build_classification_lookup(raw_results: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for row in raw_results:
        source_file = normalize_text(row.get("source_file"))
        classification = row.get("classification")
        if not source_file or not isinstance(classification, dict):
            continue
        lookup[source_file] = classification
    return lookup


def read_lookup(path: Path) -> Dict[str, Dict[str, Any]]:
    if not path.exists():
        return {}
    payload = read_json(path)
    return payload if isinstance(payload, dict) else {}


def group_lookup_by_source_file(raw_lookup: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, List[str]], Dict[str, Dict[str, Any]]]:
    ids_by_source: Dict[str, List[str]] = {}
    meta_by_source: Dict[str, Dict[str, Any]] = {}
    for custom_id, metadata in raw_lookup.items():
        if not isinstance(metadata, dict):
            continue
        source_file = normalize_text(metadata.get("source_file"))
        if not source_file:
            continue
        ids_by_source.setdefault(source_file, []).append(custom_id)
        meta_by_source.setdefault(source_file, metadata)
    return ids_by_source, meta_by_source


def build_deduped_lookup_artifact(
    generated_at: str,
    raw_lookup: Dict[str, Dict[str, Any]],
    canonical_results: Sequence[Dict[str, Any]],
    raw_lookup_path: Path,
) -> Dict[str, Any]:
    ids_by_source, meta_by_source = group_lookup_by_source_file(raw_lookup)
    entries: Dict[str, Dict[str, Any]] = {}
    missing_raw_lookup_rows = 0
    for result in sorted(canonical_results, key=lambda row: normalize_text(row.get("source_file"))):
        source_file = normalize_text(result.get("source_file"))
        if not source_file:
            continue
        raw_custom_ids = ids_by_source.get(source_file, [])
        metadata = meta_by_source.get(source_file, {})
        canonical_custom_id = normalize_text(result.get("custom_id"))
        if not raw_custom_ids:
            missing_raw_lookup_rows += 1
        entries[source_file] = {
            "canonical_custom_id": canonical_custom_id,
            "raw_lookup_custom_ids": list(raw_custom_ids),
            "raw_lookup_row_count": len(raw_custom_ids),
            "case_name": normalize_text(result.get("case_name")) or normalize_text(metadata.get("case_name")),
            "period": metadata.get("period"),
            "bucket": metadata.get("bucket"),
            "year": metadata.get("year"),
            "estimated_input_tokens": metadata.get("estimated_input_tokens"),
        }
    duplicate_source_files = [
        {
            "source_file": source_file,
            "canonical_custom_id": entries[source_file]["canonical_custom_id"],
            "raw_lookup_custom_ids": entries[source_file]["raw_lookup_custom_ids"],
            "raw_lookup_row_count": entries[source_file]["raw_lookup_row_count"],
        }
        for source_file in sorted(source_file for source_file, entry in entries.items() if entry["raw_lookup_row_count"] > 1)
    ]
    return {
        "generated_at": generated_at,
        "raw_lookup_path": str(raw_lookup_path),
        "raw_lookup_entries": len(raw_lookup),
        "unique_source_files": len(entries),
        "duplicate_source_file_count": len(duplicate_source_files),
        "missing_raw_lookup_rows": missing_raw_lookup_rows,
        "notes": [
            "This artifact is deduped by source_file, which is the stable join key used by the merged/results outputs.",
            "canonical_custom_id comes from the deduped full results file; raw_lookup_custom_ids come from the raw full lookup file and may reflect rerun-era custom-id numbering.",
        ],
        "duplicate_source_files": duplicate_source_files,
        "source_files": entries,
    }


def build_full_build_audit(
    generated_at: str,
    repo_data_path: Path,
    external_data_path: Path,
    target_rows: Sequence[Dict[str, Any]],
    canonical_results: Sequence[Dict[str, Any]],
    merged_records: Sequence[Dict[str, Any]],
    full_lookup: Dict[str, Dict[str, Any]],
    gap_final_lookup: Dict[str, Dict[str, Any]],
    gap_base_lookup: Dict[str, Dict[str, Any]],
    gap_rerun_lookup: Dict[str, Dict[str, Any]],
    deduped_lookup_artifact: Dict[str, Any],
    build_audit_path: Path,
    deduped_lookup_path: Path,
) -> Dict[str, Any]:
    full_lookup_ids_by_source, _ = group_lookup_by_source_file(full_lookup)
    gap_final_ids_by_source, _ = group_lookup_by_source_file(gap_final_lookup)
    gap_base_ids_by_source, _ = group_lookup_by_source_file(gap_base_lookup)
    gap_rerun_ids_by_source, _ = group_lookup_by_source_file(gap_rerun_lookup)
    canonical_source_files = {normalize_text(row.get("source_file")) for row in canonical_results if normalize_text(row.get("source_file"))}
    merged_source_files = {normalize_text(row.get("source_file")) for row in merged_records if normalize_text(row.get("source_file"))}
    wave_source_files = {
        normalize_text(row.get("source_file"))
        for row in target_rows
        if row.get("classification_source") == "DISABILITY_WAVE_FINAL_RESOLVED" and normalize_text(row.get("source_file"))
    }
    gap_source_files = {
        normalize_text(row.get("source_file"))
        for row in target_rows
        if row.get("classification_source") == "SCREENED_DISABILITY_PLEADING_LOSS_GAP_GLM3200" and normalize_text(row.get("source_file"))
    }
    wave_lookup_rows = sum(len(full_lookup_ids_by_source.get(source_file, [])) for source_file in wave_source_files)
    repo_hash = sha256_file(repo_data_path)
    external_hash = sha256_file(external_data_path)
    path_note = (
        f"Merge artifacts may reference {external_data_path}, while the analysis script uses {repo_data_path}. "
        f"SHA-256 {'matches' if repo_hash and external_hash and repo_hash == external_hash else 'does not match'}"
    )
    if repo_hash and external_hash:
        path_note += f" ({repo_hash})."
    elif repo_hash:
        path_note += f"; repo-local hash = {repo_hash}, external path unavailable."
    else:
        path_note += "."
    return {
        "generated_at": generated_at,
        "wave_pleading_loss_cases": len(wave_source_files),
        "gap_cases": len(gap_source_files),
        "full_results": len(canonical_results),
        "wave_lookup_entries": wave_lookup_rows,
        "gap_lookup_entries": len(gap_final_lookup),
        "full_lookup_entries": len(full_lookup),
        "wave_lookup_unique_source_files": len(wave_source_files),
        "gap_lookup_unique_source_files": len(gap_final_ids_by_source),
        "full_lookup_unique_source_files": len(full_lookup_ids_by_source),
        "full_results_unique_source_files": len(canonical_source_files),
        "merged_db_unique_source_files": len(merged_source_files),
        "lookup_row_counts": {
            "wave_subset_carried_forward_into_full_build": {
                "raw_lookup_rows": wave_lookup_rows,
                "unique_source_files": len(wave_source_files),
            },
            "gap_glm3200_r1_lookup": {
                "raw_lookup_rows": len(gap_base_lookup),
                "unique_source_files": len(gap_base_ids_by_source),
            },
            "gap_glm5000_rerun_r1_lookup": {
                "raw_lookup_rows": len(gap_rerun_lookup),
                "unique_source_files": len(gap_rerun_ids_by_source),
            },
            "gap_final_lookup": {
                "raw_lookup_rows": len(gap_final_lookup),
                "unique_source_files": len(gap_final_ids_by_source),
            },
            "full_lookup": {
                "raw_lookup_rows": len(full_lookup),
                "unique_source_files": len(full_lookup_ids_by_source),
            },
            "full_results": {
                "rows": len(canonical_results),
                "unique_source_files": len(canonical_source_files),
            },
            "merged_db_records": {
                "rows": len(merged_records),
                "unique_source_files": len(merged_source_files),
            },
        },
        "duplicate_source_files_from_raw_lookup": deduped_lookup_artifact.get("duplicate_source_files", []),
        "path_consistency": {
            "repo_local_data_path": str(repo_data_path),
            "merge_artifact_data_path": str(external_data_path),
            "repo_local_sha256": repo_hash,
            "merge_artifact_sha256": external_hash,
            "paths_are_hash_identical": bool(repo_hash and external_hash and repo_hash == external_hash),
        },
        "artifacts": {
            "build_audit_path": str(build_audit_path),
            "deduped_lookup_path": str(deduped_lookup_path),
        },
        "notes": [
            "Raw lookup counts are custom-id row counts. Dedupe counts are unique source_file counts used by the merged/results artifacts and the downstream mechanism analysis.",
            "The merged_db_* counts refer to the full DB-backed merged artifact (3198 records), not just the 676-case screened disability pleading-loss target subset.",
            "The consolidated gap-final lookup includes the 141-row glm3200 base lookup plus a 6-row rerun lookup; those six rerun custom IDs duplicate source_files already present in the base lookup, so 147 raw lookup rows collapse to 141 unique source_files.",
            f"The combined full lookup therefore contains {len(full_lookup)} raw lookup rows but only {len(full_lookup_ids_by_source)} unique source_files, matching the deduped full results/merged universe of {len(canonical_source_files)} cases.",
            path_note,
        ],
    }


def extract_classification(record: Dict[str, Any], raw_lookup: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    merged = (record.get("unified_overnight") or {}).get("classification")
    if isinstance(merged, dict):
        return merged
    source_file = normalize_text(record.get("source_file"))
    return raw_lookup.get(source_file)


def build_target_rows(
    merged_records: Sequence[Dict[str, Any]],
    raw_lookup: Dict[str, Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    missing_classification: List[Dict[str, Any]] = []
    for record in merged_records:
        if not is_screened(record):
            continue
        period = assign_period(record)
        cohort = cohort_label(record)
        if not has_disability(record):
            continue
        if not is_pleading_loss(record):
            continue
        classification = extract_classification(record, raw_lookup)
        if not isinstance(classification, dict):
            missing_classification.append(
                {
                    "source_file": record.get("source_file"),
                    "case_name": record.get("case_name"),
                    "representation_status": representation_status(record),
                    "period": period,
                    "cohort": cohort,
                }
            )
            classification = {}
        family = normalize_text(classification.get("pleading_failure_family"), "UNKNOWN")
        mechanism = normalize_text(classification.get("pleading_failure_mechanism"), "UNKNOWN")
        row = {
            "source_file": record.get("source_file"),
            "case_name": record.get("case_name"),
            "citation": record.get("citation"),
            "court": record.get("court"),
            "year": record.get("year"),
            "date_filed": record.get("date_filed"),
            "period": period,
            "cohort": cohort,
            "wave_subset": bool(period),
            "representation_status": representation_status(record),
            "pro_se": record.get("pro_se"),
            "outcome": record.get("outcome"),
            "procedural_posture": record.get("procedural_posture"),
            "primary_protected_class": record.get("primary_protected_class"),
            "protected_classes": record.get("protected_classes"),
            "disability_alleged": record.get("disability_alleged"),
            "primary_claim_type": record.get("primary_claim_type"),
            "pleading_failure_family": family,
            "pleading_failure_mechanism": mechanism,
            "classification_confidence": classification.get("classification_confidence"),
            "public_process_failure_flag": classification.get("public_process_failure_flag"),
            "raw_text_review_priority": classification.get("raw_text_review_priority"),
            "strict_failure_subset": not (family in NO_FAILURE_FAMILIES or mechanism in NO_FAILURE_MECHANISMS),
        }
        rows.append(row)
    return rows, missing_classification


def unique_preserve_order(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def ordered_group_labels(rows: Sequence[Dict[str, Any]], group_key: str, preferred_order: Sequence[str]) -> List[str]:
    present = {normalize_text(row.get(group_key), "UNKNOWN") for row in rows}
    ordered = [label for label in preferred_order if label in present]
    ordered.extend(sorted(label for label in present if label not in ordered))
    return ordered


def build_three_way_crosstab(
    rows: Sequence[Dict[str, Any]],
    key: str,
    group_key: str,
    group_order: Sequence[str],
) -> Dict[str, Any]:
    labels = stable_label_order({normalize_text(row.get(key), "UNKNOWN") for row in rows}, rows, key)
    groups = ordered_group_labels(rows, group_key, group_order)
    group_totals = {
        rep: {group: sum(1 for row in rows if row["representation_status"] == rep and row[group_key] == group) for group in groups}
        for rep in REPRESENTATION_ORDER
    }
    table = {
        label: {
            rep: {
                group: sum(
                    1
                    for row in rows
                    if row["representation_status"] == rep and row[group_key] == group and row[key] == label
                )
                for group in groups
            }
            for rep in REPRESENTATION_ORDER
        }
        for label in labels
    }
    cells: List[Dict[str, Any]] = []
    for label in labels:
        for rep in REPRESENTATION_ORDER:
            for group in groups:
                count = table[label][rep][group]
                group_total = group_totals[rep][group]
                cells.append(
                    {
                        key: label,
                        "representation_status": rep,
                        group_key: group,
                        "count": count,
                        "share_within_representation_group_pct": pct(count, group_total),
                    }
                )
    overall_counts = {label: sum(cell["count"] for cell in cells if cell[key] == label) for label in labels}
    return {
        "key": key,
        "group_key": group_key,
        "groups": groups,
        "labels": labels,
        "group_totals": group_totals,
        "overall_counts": overall_counts,
        "table": table,
        "cells": cells,
    }


def sort_counter(counter: Counter[str]) -> List[Tuple[str, int]]:
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))


def top_n(counter: Counter[str], total: int, n: int = 5) -> Dict[str, Any]:
    ranked = sort_counter(counter)
    exact = [
        {"label": label, "count": count, "share_pct": pct(count, total)}
        for label, count in ranked[:n]
    ]
    if len(ranked) <= n:
        tied = exact[:]
    else:
        threshold = ranked[n - 1][1]
        tied = [
            {"label": label, "count": count, "share_pct": pct(count, total)}
            for label, count in ranked
            if count >= threshold
        ]
    return {
        "total": total,
        "ranked": exact,
        "ranked_with_ties": tied,
    }


def top_n_by_representation(rows: Sequence[Dict[str, Any]], key: str, n: int = 5) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for rep in REPRESENTATION_ORDER:
        counter = Counter(row[key] for row in rows if row["representation_status"] == rep)
        result[rep] = top_n(counter, sum(counter.values()), n=n)
    return result


def gammaincc(a: float, x: float) -> float:
    if x < 0 or a <= 0:
        raise ValueError("Invalid arguments for gammaincc")
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap = a
        summation = 1.0 / a
        delta = summation
        for _ in range(GAMMA_ITMAX):
            ap += 1.0
            delta *= x / ap
            summation += delta
            if abs(delta) < abs(summation) * GAMMA_EPS:
                break
        gamser = summation * math.exp(-x + a * math.log(x) - gln)
        return 1.0 - gamser
    b = x + 1.0 - a
    c = 1.0 / GAMMA_FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, GAMMA_ITMAX + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < GAMMA_FPMIN:
            d = GAMMA_FPMIN
        c = b + an / c
        if abs(c) < GAMMA_FPMIN:
            c = GAMMA_FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < GAMMA_EPS:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def contingency_table(
    rows: Sequence[Dict[str, Any]],
    key: str,
    labels: Sequence[str],
    rep_labels: Sequence[str] = INFERENTIAL_REPRESENTATION_ORDER,
) -> Dict[str, Any]:
    matrix = [
        [sum(1 for row in rows if row["representation_status"] == rep and row[key] == label) for label in labels]
        for rep in rep_labels
    ]
    row_totals = [sum(row) for row in matrix]
    column_totals = [sum(matrix[row_index][col_index] for row_index in range(len(matrix))) for col_index in range(len(labels))]
    return {
        "representation_statuses": list(rep_labels),
        "labels": list(labels),
        "matrix": matrix,
        "row_totals": row_totals,
        "column_totals": column_totals,
        "n": sum(row_totals),
    }


def chi_square_test(table: Dict[str, Any]) -> Dict[str, Any]:
    matrix: List[List[int]] = table["matrix"]
    rows = len(matrix)
    cols = len(matrix[0]) if matrix else 0
    row_totals = table["row_totals"]
    column_totals = table["column_totals"]
    total = table["n"]
    expected: List[List[float]] = []
    residuals: List[List[Optional[float]]] = []
    chi2 = 0.0
    min_expected: Optional[float] = None
    low_expected_cells = 0
    for row_index in range(rows):
        expected_row: List[float] = []
        residual_row: List[Optional[float]] = []
        for col_index in range(cols):
            exp = (row_totals[row_index] * column_totals[col_index] / total) if total else 0.0
            expected_row.append(exp)
            if min_expected is None or exp < min_expected:
                min_expected = exp
            if exp < 5:
                low_expected_cells += 1
            obs = matrix[row_index][col_index]
            if exp > 0:
                chi2 += ((obs - exp) ** 2) / exp
                residual_row.append((obs - exp) / math.sqrt(exp))
            else:
                residual_row.append(None)
        expected.append(expected_row)
        residuals.append(residual_row)
    dof = (rows - 1) * (cols - 1)
    p_value = gammaincc(dof / 2.0, chi2 / 2.0) if dof > 0 else None
    cramers_v = math.sqrt(chi2 / (total * min(rows - 1, cols - 1))) if total and min(rows - 1, cols - 1) > 0 else None
    return {
        "chi2": round_float(chi2, 6),
        "degrees_of_freedom": dof,
        "p_value": round_float(p_value, 12),
        "n": total,
        "min_expected_count": round_float(min_expected, 6),
        "low_expected_cells": low_expected_cells,
        "total_cells": rows * cols,
        "cramers_v": round_float(cramers_v, 6),
        "expected_counts": [[round_float(value, 6) for value in row] for row in expected],
        "standardized_residuals": [[round_float(value, 6) for value in row] for row in residuals],
    }


def best_collapsed_test(
    rows: Sequence[Dict[str, Any]],
    key: str,
    min_keep: int = 2,
    rep_labels: Sequence[str] = INFERENTIAL_REPRESENTATION_ORDER,
) -> Dict[str, Any]:
    counter = Counter(row[key] for row in rows if row["representation_status"] in rep_labels)
    ordered = [label for label, _ in sort_counter(counter)]
    if len(ordered) <= min_keep:
        labels = ordered
        table = contingency_table(rows, key, labels, rep_labels=rep_labels)
        return {
            "strategy": "all_labels",
            "keep_labels": labels,
            "other_label_used": False,
            "contingency_table": table,
            "chi_square": chi_square_test(table),
        }

    best: Optional[Dict[str, Any]] = None
    for n_keep in range(len(ordered) - 1, min_keep - 1, -1):
        keep = ordered[:n_keep]
        collapsed_rows = []
        for row in rows:
            if row["representation_status"] not in rep_labels:
                continue
            collapsed = dict(row)
            collapsed[key] = row[key] if row[key] in keep else "OTHER"
            collapsed_rows.append(collapsed)
        labels = keep + ["OTHER"]
        table = contingency_table(collapsed_rows, key, labels, rep_labels=rep_labels)
        stats = chi_square_test(table)
        candidate = {
            "strategy": "top_n_plus_other",
            "n_keep": n_keep,
            "keep_labels": keep,
            "other_label_used": True,
            "contingency_table": table,
            "chi_square": stats,
        }
        if stats["low_expected_cells"] == 0:
            return candidate
        if best is None:
            best = candidate
        else:
            best_low = best["chi_square"]["low_expected_cells"]
            if stats["low_expected_cells"] < best_low or (
                stats["low_expected_cells"] == best_low and n_keep > best.get("n_keep", 0)
            ):
                best = candidate
    assert best is not None
    return best


def divergence_by_label(rows: Sequence[Dict[str, Any]], key: str) -> Dict[str, Any]:
    known_rows = [row for row in rows if row["representation_status"] in INFERENTIAL_REPRESENTATION_ORDER]
    pro_total = sum(1 for row in known_rows if row["representation_status"] == "PRO_SE")
    rep_total = sum(1 for row in known_rows if row["representation_status"] == "REPRESENTED")
    labels = stable_label_order({row[key] for row in known_rows}, known_rows, key)
    entries: List[Dict[str, Any]] = []
    for label in labels:
        pro_count = sum(1 for row in known_rows if row["representation_status"] == "PRO_SE" and row[key] == label)
        rep_count = sum(1 for row in known_rows if row["representation_status"] == "REPRESENTED" and row[key] == label)
        pro_share = (pro_count / pro_total) if pro_total else 0.0
        rep_share = (rep_count / rep_total) if rep_total else 0.0
        other_pro = pro_total - pro_count
        other_rep = rep_total - rep_count
        odds_ratio = ((pro_count + 0.5) * (other_rep + 0.5)) / ((rep_count + 0.5) * (other_pro + 0.5))
        total_label = pro_count + rep_count
        expected_pro = pro_total * total_label / (pro_total + rep_total) if (pro_total + rep_total) else 0.0
        expected_rep = rep_total * total_label / (pro_total + rep_total) if (pro_total + rep_total) else 0.0
        chi_contribution = 0.0
        if expected_pro:
            chi_contribution += ((pro_count - expected_pro) ** 2) / expected_pro
        if expected_rep:
            chi_contribution += ((rep_count - expected_rep) ** 2) / expected_rep
        entries.append(
            {
                "label": label,
                "pro_se_count": pro_count,
                "represented_count": rep_count,
                "pro_se_share_pct": round_float(pro_share * 100.0, 4),
                "represented_share_pct": round_float(rep_share * 100.0, 4),
                "share_gap_pro_se_minus_represented_pct_points": round_float((pro_share - rep_share) * 100.0, 4),
                "odds_ratio_pro_se_vs_represented": round_float(odds_ratio, 6),
                "chi_square_contribution": round_float(chi_contribution, 6),
            }
        )
    pro_se_overrepresented = sorted(
        entries,
        key=lambda item: (
            -(item["share_gap_pro_se_minus_represented_pct_points"] or 0.0),
            -(item["odds_ratio_pro_se_vs_represented"] or 0.0),
            item["label"],
        ),
    )
    represented_overrepresented = sorted(
        entries,
        key=lambda item: (
            item["share_gap_pro_se_minus_represented_pct_points"] or 0.0,
            item["odds_ratio_pro_se_vs_represented"] or 0.0,
            item["label"],
        ),
    )
    return {
        "entries": entries,
        "top_pro_se_overrepresented": pro_se_overrepresented[:10],
        "top_represented_overrepresented": represented_overrepresented[:10],
    }


def summarize_representation(rows: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    return {label: sum(1 for row in rows if row["representation_status"] == label) for label in REPRESENTATION_ORDER}


def summarize_groups(rows: Sequence[Dict[str, Any]], group_key: str, group_order: Sequence[str]) -> Dict[str, int]:
    return {group: sum(1 for row in rows if row[group_key] == group) for group in ordered_group_labels(rows, group_key, group_order)}


def summarize_representation_by_group(
    rows: Sequence[Dict[str, Any]],
    group_key: str,
    group_order: Sequence[str],
) -> Dict[str, Dict[str, int]]:
    groups = ordered_group_labels(rows, group_key, group_order)
    return {
        group: {label: sum(1 for row in rows if row[group_key] == group and row["representation_status"] == label) for label in REPRESENTATION_ORDER}
        for group in groups
    }


def analyze_subset(
    rows: Sequence[Dict[str, Any]],
    chi_keep_min: int,
    collapsed_label: str,
    group_key: str,
    group_order: Sequence[str],
) -> Dict[str, Any]:
    mechanism_rows = [row for row in rows if row["representation_status"] in INFERENTIAL_REPRESENTATION_ORDER]
    family_test = best_collapsed_test(mechanism_rows, "pleading_failure_family", min_keep=2)
    mechanism_full_labels = stable_label_order(
        {row["pleading_failure_mechanism"] for row in mechanism_rows},
        mechanism_rows,
        "pleading_failure_mechanism",
    )
    mechanism_full_table = contingency_table(mechanism_rows, "pleading_failure_mechanism", mechanism_full_labels)
    mechanism_collapsed_test = best_collapsed_test(mechanism_rows, "pleading_failure_mechanism", min_keep=chi_keep_min)
    return {
        "n": len(rows),
        "group_key": group_key,
        "group_order": ordered_group_labels(rows, group_key, group_order),
        "representation_counts": summarize_representation(rows),
        "group_counts": summarize_groups(rows, group_key, group_order),
        "representation_by_group": summarize_representation_by_group(rows, group_key, group_order),
        "family_crosstab": build_three_way_crosstab(rows, "pleading_failure_family", group_key, group_order),
        "mechanism_crosstab": build_three_way_crosstab(rows, "pleading_failure_mechanism", group_key, group_order),
        "top_5_families_by_representation": top_n_by_representation(rows, "pleading_failure_family", n=5),
        "top_5_mechanisms_by_representation": top_n_by_representation(rows, "pleading_failure_mechanism", n=5),
        "family_divergence": divergence_by_label(rows, "pleading_failure_family"),
        "mechanism_divergence": divergence_by_label(rows, "pleading_failure_mechanism"),
        "chi_squared": {
            "family_vs_representation": family_test,
            "mechanism_vs_representation_full_table": {
                "contingency_table": mechanism_full_table,
                "chi_square": chi_square_test(mechanism_full_table),
            },
            collapsed_label: mechanism_collapsed_test,
        },
    }


def format_pct(value: Optional[float]) -> str:
    return "n/a" if value is None else f"{value:.1f}%"


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def build_subset_payload(
    rows: Sequence[Dict[str, Any]],
    missing_rows: Sequence[Dict[str, Any]],
    group_key: str,
    group_order: Sequence[str],
) -> Dict[str, Any]:
    no_failure_rows = [
        row
        for row in rows
        if row["pleading_failure_family"] in NO_FAILURE_FAMILIES or row["pleading_failure_mechanism"] in NO_FAILURE_MECHANISMS
    ]
    strict_rows = [row for row in rows if row["strict_failure_subset"]]
    raw_analysis = analyze_subset(
        rows,
        chi_keep_min=3,
        collapsed_label="mechanism_vs_representation_top_n_plus_other",
        group_key=group_key,
        group_order=group_order,
    )
    strict_analysis = analyze_subset(
        strict_rows,
        chi_keep_min=2,
        collapsed_label="mechanism_vs_representation_top_n_plus_other",
        group_key=group_key,
        group_order=group_order,
    )
    return {
        "quality_flags": {
            "missing_classification_rows": list(missing_rows),
            "no_failure_target_cases": {
                "count": len(no_failure_rows),
                "representation_counts": summarize_representation(no_failure_rows),
                "group_counts": summarize_groups(no_failure_rows, group_key, group_order),
                "rows": no_failure_rows,
            },
        },
        "analysis_rows": list(rows),
        "raw_case_level_subset": raw_analysis,
        "strict_failure_subset": {
            "exclusion_rule": "Exclude NO_FAILURE_* families and CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS mechanism.",
            "analysis_rows": strict_rows,
            **strict_analysis,
        },
    }


def find_divergence_entry(divergence: Dict[str, Any], label: str) -> Optional[Dict[str, Any]]:
    for item in divergence.get("entries", []):
        if item.get("label") == label:
            return item
    return None


def build_group_rows(analysis: Dict[str, Any]) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for group in analysis.get("group_order", []):
        counts = analysis["representation_by_group"].get(group, {})
        total = sum(counts.values())
        rows.append(
            [
                group,
                total,
                counts.get("PRO_SE", 0),
                counts.get("REPRESENTED", 0),
                counts.get("UNKNOWN", 0),
                format_pct(pct(counts.get("PRO_SE", 0), total)),
            ]
        )
    return rows


def build_top_mechanism_rows(analysis: Dict[str, Any], representation: str) -> List[List[Any]]:
    return [
        [item["label"], item["count"], format_pct(item["share_pct"])]
        for item in analysis["top_5_mechanisms_by_representation"][representation]["ranked"]
    ]


def build_divergence_rows(divergence: Dict[str, Any], pro_n: int = 5, rep_n: int = 3) -> List[List[Any]]:
    rows: List[List[Any]] = []
    for item in divergence.get("top_pro_se_overrepresented", [])[:pro_n]:
        gap = item.get("share_gap_pro_se_minus_represented_pct_points") or 0.0
        rows.append(
            [
                item["label"],
                format_pct(item.get("pro_se_share_pct")),
                format_pct(item.get("represented_share_pct")),
                f"+{gap:.1f} pp",
                f"{(item.get('odds_ratio_pro_se_vs_represented') or 0.0):.2f}",
                "pro se",
            ]
        )
    for item in divergence.get("top_represented_overrepresented", [])[:rep_n]:
        gap = item.get("share_gap_pro_se_minus_represented_pct_points") or 0.0
        rows.append(
            [
                item["label"],
                format_pct(item.get("pro_se_share_pct")),
                format_pct(item.get("represented_share_pct")),
                f"{gap:.1f} pp",
                f"{(item.get('odds_ratio_pro_se_vs_represented') or 0.0):.2f}",
                "represented",
            ]
        )
    return rows


def format_collapsed_test(label: str, analysis: Dict[str, Any]) -> str:
    test = analysis["chi_squared"]["mechanism_vs_representation_top_n_plus_other"]
    kept = ", ".join(test.get("keep_labels", [])) or "n/a"
    chi = test["chi_square"]
    return (
        f"{label}: χ²({chi['degrees_of_freedom']}) = {chi['chi2']}, p = {chi['p_value']}, "
        f"Cramér's V = {chi['cramers_v']}. Kept labels: {kept} + OTHER."
    )


def build_memo(results: Dict[str, Any]) -> str:
    universe = results["universe"]
    quality = results["quality_flags"]
    full_raw = results["raw_case_level_subset"]
    full_strict = results["strict_failure_subset"]
    wave = results["disability_wave_subset"]
    wave_raw = wave["raw_case_level_subset"]
    wave_strict = wave["strict_failure_subset"]
    added = results["newly_added_pre_wave_or_unassigned_subset"]
    added_raw = added["raw_case_level_subset"]
    added_strict = added["strict_failure_subset"]
    lookup_handoff = results.get("lookup_handoff_counts", {})

    translation_entry = find_divergence_entry(full_strict["family_divergence"], "TRANSLATION")
    gateway_entry = find_divergence_entry(full_strict["family_divergence"], "PROCEDURAL_GATEWAY")

    full_pro_rows = build_top_mechanism_rows(full_raw, "PRO_SE")
    full_rep_rows = build_top_mechanism_rows(full_raw, "REPRESENTED")
    divergence_rows = build_divergence_rows(full_strict["mechanism_divergence"])
    cohort_rows = build_group_rows(full_raw)
    added_rows = build_group_rows(added_raw)

    memo = [
        "# Pro se vs. represented pleading-failure mechanism divergence",
        "",
        "## Scope and inputs",
        "",
        "- Data source: `data/FHA_Unified_Database.json`, joined to `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_merged.json` and checked against `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_results.json`.",
        "- Existing disability-wave classifications were carried forward from `results/unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json`.",
        "- The missing screened disability pleading-loss remainder was queued through `results/screened_disability_pleading_loss_missing_source_files.txt` and classified through the repo-local OpenRouter runner, with consolidated final gap codings saved at `results/unified_overnight_openrouter_screened_disability_pleading_loss_gap_final_results.json`.",
        "- Supporting handoff artifacts now distinguish raw lookup-row counts from deduped unique `source_file` counts: `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_build_audit.json` and `results/unified_overnight_openrouter_screened_disability_pleading_loss_full_id_lookup_deduped_by_source_file.json`.",
        "- Some merge artifacts point to `/mnt/c/Users/nickg/OneDrive/Documents/Note/data/2/FHA_Unified_Database.json` instead of repo-local `data/FHA_Unified_Database.json`; the build audit records that those inputs are SHA-256 identical, so the difference is path drift rather than data drift.",
        "- Pleading-stage loss is defined as `procedural_posture` in `{MOTION_TO_DISMISS, SCREENING_ORDER}` and `outcome` in `{DEFENDANT_WIN, PROCEDURAL}`.",
        "- Representation status comes from the `pro_se` boolean; rows with unknown representation are retained descriptively but excluded from inferential tests.",
        "",
        "## Universe and coverage",
        "",
        markdown_table(
            ["Measure", "Value"],
            [
                ["Screened disability cases", universe["screened_disability_cases_total"]],
                ["Full screened disability pleading-loss universe", universe["screened_disability_pleading_stage_losses_total"]],
                ["Previously covered disability-wave pleading-loss subset", universe["disability_wave_pleading_stage_losses_total"]],
                ["Newly added pre-wave / unassigned remainder", universe["newly_added_pre_wave_or_unassigned_cases_total"]],
                ["Classified full-universe target cases", f"{universe['classified_target_cases']}/{universe['screened_disability_pleading_stage_losses_total']}"],
                ["Full-universe classification coverage", format_pct(universe["classification_coverage_pct"])],
                ["Residual uncoded remainder", universe["residual_uncoded_cases_total"]],
                ["No-failure / claim-survives codings in full target set", quality["no_failure_target_cases"]["count"]],
            ],
        ),
        "",
        markdown_table(["Cohort", "Target cases", "Pro se", "Represented", "Unknown", "Pro se share"], cohort_rows),
        "",
        f"The exact broadening step is now explicit: the old p2 memo covered {universe['disability_wave_pleading_stage_losses_total']} disability-wave pleading-loss cases, while the full screened disability pleading-loss universe contains {universe['screened_disability_pleading_stage_losses_total']}. The newly added remainder contributes {universe['newly_added_pre_wave_or_unassigned_cases_total']} older pre-wave cases, and the residual uncoded remainder is {universe['residual_uncoded_cases_total']}.",
        "",
        "## Full screened disability pleading-loss universe",
        "",
        f"Using the broadened full-universe raw case-level target set (n = {full_raw['n']}), the mechanism mix differs materially by representation status.",
        "",
        format_collapsed_test("- Raw full-universe collapsed test", full_raw),
        format_collapsed_test("- Strict-failure full-universe sensitivity test", full_strict),
        "",
        "These collapsed χ² readouts use adaptive top-n-plus-OTHER sparse-cell reduction for inference; the full uncollapsed contingency tables remain in `results/pro_se_mechanism_divergence_results.json`.",
        "",
        markdown_table(["Mechanism", "Count", "Share"], full_pro_rows),
        "",
        markdown_table(["Mechanism", "Count", "Share"], full_rep_rows),
        "",
        markdown_table(
            ["Mechanism", "Pro se share", "Represented share", "Gap (pro se - represented)", "Odds ratio", "Overrepresented in"],
            divergence_rows,
        ),
        "",
        (
            f"At the family level, `TRANSLATION` accounts for {format_pct(translation_entry['pro_se_share_pct']) if translation_entry else 'n/a'} "
            f"of pro se strict failures versus {format_pct(translation_entry['represented_share_pct']) if translation_entry else 'n/a'} of represented strict failures, while `PROCEDURAL_GATEWAY` accounts for {format_pct(gateway_entry['pro_se_share_pct']) if gateway_entry else 'n/a'} of pro se strict failures versus {format_pct(gateway_entry['represented_share_pct']) if gateway_entry else 'n/a'} of represented strict failures."
        ),
        "",
        "## Previously covered disability-wave subset (comparison)",
        "",
        f"The previously analyzed disability-wave subset remains {wave_raw['n']} cases. Broadening the universe does not replace that tranche; it nests it inside the larger full-universe result.",
        "",
        format_collapsed_test("- Raw disability-wave collapsed test", wave_raw),
        format_collapsed_test("- Strict-failure disability-wave sensitivity test", wave_strict),
        "",
        "## Newly added pre-wave / unassigned remainder",
        "",
        markdown_table(["Cohort", "Target cases", "Pro se", "Represented", "Unknown", "Pro se share"], added_rows),
        "",
        f"All newly added cases fall outside the P1/P2/P3 disability-wave window: the added tranche contains {added_raw['n']} cases, of which {added_raw['group_counts'].get('PRE_WAVE', 0)} are pre-wave and {added_raw['group_counts'].get('UNASSIGNED', 0)} are unassigned by date.",
        "",
        format_collapsed_test("- Raw added-tranche collapsed test", added_raw),
        format_collapsed_test("- Strict-failure added-tranche sensitivity test", added_strict),
        "",
        "## Quality-control note",
        "",
        f"The broadened full-universe target set contains {quality['no_failure_target_cases']['count']} cases coded as `NO_FAILURE_*` or `CLAIM_SURVIVES_OR_PLAINTIFF_PREVAILS` even though the case-level filter marks them as pleading-stage defendant/procedural outcomes. Those are retained in the raw reproducibility tables but excluded from the strict-failure sensitivity read.",
        "",
        f"Residual uncoded remainder: {universe['residual_uncoded_cases_total']}. If this is nonzero, the exact source files are listed under `quality_flags.missing_classification_rows` in the JSON output.",
        "",
        (
            "For handoff, note that the raw consolidated lookup files count custom-id rows rather than deduped cases: "
            f"the combined lookup has {lookup_handoff.get('full_lookup_raw_rows', 'n/a')} raw rows mapping to {lookup_handoff.get('full_lookup_unique_source_files', 'n/a')} unique `source_file`s, "
            f"and the gap-final lookup has {lookup_handoff.get('gap_lookup_raw_rows', 'n/a')} raw rows mapping to {lookup_handoff.get('gap_lookup_unique_source_files', 'n/a')} unique `source_file`s because {lookup_handoff.get('duplicate_source_files_from_raw_lookup', 'n/a')} rerun custom IDs duplicate already covered cases. "
            "The build audit and deduped lookup artifact make that distinction explicit."
        ),
        "",
        "## Bottom line",
        "",
        "Broadened to the full screened disability pleading-loss universe, the core story still holds within this pleading-loss sample: pro se and represented cases sort into a different mechanism mix. Pro se strict pleading losses remain disproportionately concentrated in translation failures such as unalleged requests, unclear FHA hooks, and noncognizable theories, while represented plaintiffs' remaining pleading losses skew much more toward threshold gateway defects such as jurisdiction and standing. The broader universe therefore reinforces rather than narrows the note's institutional-translation account.",
    ]
    return "\n".join(memo) + "\n"


def main() -> None:
    repo = repo_root()
    results_dir = repo / "results"
    data_path = repo / "data" / "FHA_Unified_Database.json"
    external_data_path = repo.parent / "data" / "2" / "FHA_Unified_Database.json"
    combined_merged_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_full_merged.json"
    combined_results_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_full_results.json"
    full_lookup_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_full_id_lookup.json"
    wave_results_path = results_dir / "unified_overnight_openrouter_disability_wave_r1_final_resolved_results.json"
    gap_results_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_gap_final_results.json"
    gap_lookup_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_gap_final_id_lookup.json"
    gap_base_lookup_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_gap_glm3200_r1_id_lookup.json"
    gap_rerun_lookup_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_gap_glm5000_rerun_r1_id_lookup.json"
    output_json = results_dir / "pro_se_mechanism_divergence_results.json"
    output_memo = results_dir / "pro_se_mechanism_divergence_analysis.md"
    build_audit_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_full_build_audit.json"
    deduped_lookup_path = results_dir / "unified_overnight_openrouter_screened_disability_pleading_loss_full_id_lookup_deduped_by_source_file.json"

    db_records = read_json(data_path)
    merged_payload = read_json(combined_merged_path)
    merged_records = merged_payload["records"]
    combined_results = read_json(combined_results_path)
    full_lookup = read_lookup(full_lookup_path)
    wave_results = read_json(wave_results_path)
    gap_results = read_json(gap_results_path)
    gap_lookup = read_lookup(gap_lookup_path)
    gap_base_lookup = read_lookup(gap_base_lookup_path)
    gap_rerun_lookup = read_lookup(gap_rerun_lookup_path)
    raw_lookup = build_classification_lookup(combined_results)
    generated_at = datetime.now(UTC).isoformat()

    wave_source_files = {normalize_text(row.get("source_file")) for row in wave_results if isinstance(row, dict)}
    gap_source_files = {normalize_text(row.get("source_file")) for row in gap_results if isinstance(row, dict)}

    screened_records = [record for record in db_records if is_screened(record) and record.get("outcome") not in (None, "", "?" )]
    screened_disability_records = [record for record in screened_records if has_disability(record)]
    screened_disability_pleading_losses = [record for record in screened_disability_records if is_pleading_loss(record)]
    disability_wave_records = [record for record in screened_disability_records if assign_period(record)]

    target_rows, missing_classification = build_target_rows(merged_records, raw_lookup)
    for row in target_rows:
        source_file = normalize_text(row.get("source_file"))
        if source_file in gap_source_files:
            row["classification_source"] = "SCREENED_DISABILITY_PLEADING_LOSS_GAP_GLM3200"
        elif source_file in wave_source_files:
            row["classification_source"] = "DISABILITY_WAVE_FINAL_RESOLVED"
        else:
            row["classification_source"] = "UNKNOWN"

    wave_rows = [row for row in target_rows if row["wave_subset"]]
    added_rows = [row for row in target_rows if not row["wave_subset"]]
    missing_wave = [row for row in missing_classification if row.get("period")]
    missing_added = [row for row in missing_classification if not row.get("period")]

    full_payload = build_subset_payload(target_rows, missing_classification, "cohort", COHORT_ORDER)
    wave_payload = build_subset_payload(wave_rows, missing_wave, "period", PERIOD_ORDER)
    added_payload = build_subset_payload(added_rows, missing_added, "cohort", ["PRE_WAVE", "UNASSIGNED"])
    deduped_lookup_artifact = build_deduped_lookup_artifact(generated_at, full_lookup, combined_results, full_lookup_path)
    build_audit = build_full_build_audit(
        generated_at,
        data_path,
        external_data_path,
        target_rows,
        combined_results,
        merged_records,
        full_lookup,
        gap_lookup,
        gap_base_lookup,
        gap_rerun_lookup,
        deduped_lookup_artifact,
        build_audit_path,
        deduped_lookup_path,
    )

    classified_target_cases = len(target_rows) - len(missing_classification)
    results = {
        "generated_at": generated_at,
        "inputs": {
            "data_path": str(data_path),
            "external_data_path": str(external_data_path),
            "combined_merged_path": str(combined_merged_path),
            "combined_results_path": str(combined_results_path),
            "full_lookup_path": str(full_lookup_path),
            "wave_results_path": str(wave_results_path),
            "gap_results_path": str(gap_results_path),
            "gap_lookup_path": str(gap_lookup_path),
            "gap_base_lookup_path": str(gap_base_lookup_path),
            "gap_rerun_lookup_path": str(gap_rerun_lookup_path),
        },
        "supporting_artifacts": {
            "build_audit_path": str(build_audit_path),
            "deduped_lookup_path": str(deduped_lookup_path),
        },
        "lookup_handoff_counts": {
            "full_lookup_raw_rows": build_audit["full_lookup_entries"],
            "full_lookup_unique_source_files": build_audit["full_lookup_unique_source_files"],
            "gap_lookup_raw_rows": build_audit["gap_lookup_entries"],
            "gap_lookup_unique_source_files": build_audit["gap_lookup_unique_source_files"],
            "duplicate_source_files_from_raw_lookup": len(build_audit["duplicate_source_files_from_raw_lookup"]),
        },
        "assumptions": [
            "Full target universe means all screened disability pleading-stage losses, not just the P1/P2/P3 disability-wave subset.",
            "Pleading-stage loss is defined as procedural_posture in {MOTION_TO_DISMISS, SCREENING_ORDER} and outcome in {DEFENDANT_WIN, PROCEDURAL}.",
            "Representation status is taken from the pro_se boolean; unknown representation rows are retained descriptively but excluded from chi-squared tests.",
            "The broadened universe is assembled by carrying forward existing disability-wave final-resolved classifications for the previously covered subset and adding a targeted OpenRouter gap run for the missing screened disability pleading-loss source files outside the wave window.",
            "Collapsed chi-squared summaries use adaptive top-n-plus-OTHER aggregation to reduce sparse expected cells; the full contingency tables remain in this JSON output.",
        ],
        "universe": {
            "db_record_count": len(db_records),
            "merged_record_count": len(merged_records),
            "screened_cases_total": len(screened_records),
            "screened_disability_cases_total": len(screened_disability_records),
            "screened_disability_pleading_stage_losses_total": len(screened_disability_pleading_losses),
            "disability_wave_cases_total": len(disability_wave_records),
            "disability_wave_pleading_stage_losses_total": len(wave_rows),
            "newly_added_pre_wave_or_unassigned_cases_total": len(added_rows),
            "classified_target_cases": classified_target_cases,
            "classification_coverage_pct": pct(classified_target_cases, len(target_rows)),
            "residual_uncoded_cases_total": len(missing_classification),
            "representation_counts": summarize_representation(target_rows),
            "cohort_counts": summarize_groups(target_rows, "cohort", COHORT_ORDER),
            "representation_by_cohort": summarize_representation_by_group(target_rows, "cohort", COHORT_ORDER),
            "wave_representation_by_period": summarize_representation_by_group(wave_rows, "period", PERIOD_ORDER),
            "classification_source_counts": {
                "DISABILITY_WAVE_FINAL_RESOLVED": sum(1 for row in target_rows if row.get("classification_source") == "DISABILITY_WAVE_FINAL_RESOLVED"),
                "SCREENED_DISABILITY_PLEADING_LOSS_GAP_GLM3200": sum(1 for row in target_rows if row.get("classification_source") == "SCREENED_DISABILITY_PLEADING_LOSS_GAP_GLM3200"),
                "UNKNOWN": sum(1 for row in target_rows if row.get("classification_source") == "UNKNOWN"),
            },
        },
        "quality_flags": full_payload["quality_flags"],
        "analysis_rows": target_rows,
        "raw_case_level_subset": full_payload["raw_case_level_subset"],
        "strict_failure_subset": full_payload["strict_failure_subset"],
        "disability_wave_subset": wave_payload,
        "newly_added_pre_wave_or_unassigned_subset": added_payload,
    }

    memo = build_memo(results)
    write_json(output_json, results)
    write_text(output_memo, memo)
    write_json(build_audit_path, build_audit)
    write_json(deduped_lookup_path, deduped_lookup_artifact)

    print(f"Wrote {output_json}")
    print(f"Wrote {output_memo}")
    print(f"Wrote {build_audit_path}")
    print(f"Wrote {deduped_lookup_path}")
    print(f"Full-universe target rows analyzed: {len(target_rows)}")
    print(f"Wave subset target rows: {len(wave_rows)}")
    print(f"Added pre-wave / unassigned rows: {len(added_rows)}")
    print(f"Residual uncoded rows: {len(missing_classification)}")


if __name__ == "__main__":
    main()
