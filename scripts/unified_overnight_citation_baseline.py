#!/usr/bin/env python3
"""
Build citation-normalization and doctrinal baseline outputs for the unified overnight run.

Outputs:
- data/2/unified_normalized_citations.json
- data/2/doctrinal_function_taxonomy.md
- results/unified_overnight_citation_baseline.md

Usage:
  python3 unified_overnight_citation_baseline.py
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

TOP_AUTHORITIES = 50

EXPLICIT_CANONICAL_MAP = {
    "ashcroft v iqbal": "Ashcroft v. Iqbal",
    "ashcroft v iqbal 556 u s 662 2009": "Ashcroft v. Iqbal",
    "bell atl corp v twombly": "Bell Atlantic Corp. v. Twombly",
    "bell atl corp v twombly 550 u s 544 2007": "Bell Atlantic Corp. v. Twombly",
    "bell atlantic corp v twombly": "Bell Atlantic Corp. v. Twombly",
    "bell atlantic corp v twombly 550 u s 544 2007": "Bell Atlantic Corp. v. Twombly",
    "bell atlantic v twombly": "Bell Atlantic Corp. v. Twombly",
    "mcdonnell douglas corp v green": "McDonnell Douglas Corp. v. Green",
    "mcdonnell douglas corp v green 411 u s 792 1973": "McDonnell Douglas Corp. v. Green",
    "havens realty corp v coleman": "Havens Realty Corp. v. Coleman",
    "havens realty corp v coleman 455 u s 363 1982": "Havens Realty Corp. v. Coleman",
    "city of cleburne v cleburne living center": "City of Cleburne v. Cleburne Living Center",
    "city of cleburne v cleburne living center inc": "City of Cleburne v. Cleburne Living Center",
    "city of cleburne v cleburne living center 473 u s 432 1985": "City of Cleburne v. Cleburne Living Center",
    "lujan v defenders of wildlife": "Lujan v. Defenders of Wildlife",
    "lujan v defenders of wildlife 504 u s 555 1992": "Lujan v. Defenders of Wildlife",
    "celotex corp v catrett": "Celotex Corp. v. Catrett",
    "celotex corp v catrett 477 u s 317 1986": "Celotex Corp. v. Catrett",
    "anderson v liberty lobby inc": "Anderson v. Liberty Lobby, Inc.",
    "anderson v liberty lobby inc 477 u s 242 1986": "Anderson v. Liberty Lobby, Inc.",
    "meyer v holley": "Meyer v. Holley",
    "meyer v holley 537 u s 280 2003": "Meyer v. Holley",
    "bloch v frischholz": "Bloch v. Frischholz",
    "bloch v frischholz 587 f 3d 771 7th cir 2009": "Bloch v. Frischholz",
    "giebeler v m b assocs": "Giebeler v. M & B Associates",
    "giebeler v m b associates": "Giebeler v. M & B Associates",
    "giebeler v m b assocs 343 f 3d 1143 9th cir 2003": "Giebeler v. M & B Associates",
    "dubois v assn of apartment owners of 2987 kalakaua": "Dubois v. Ass'n of Apartment Owners of 2987 Kalakaua",
    "dubois v assn of apartment owners of 2987 kalakaua 453 f 3d 1175 9th cir 2006": "Dubois v. Ass'n of Apartment Owners of 2987 Kalakaua",
    "schwarz v city of treasure island": "Schwarz v. City of Treasure Island",
    "bhogaita v altamonte heights condo assn inc": "Bhogaita v. Altamonte Heights Condo. Ass'n, Inc.",
    "hollis v chestnut bend homeowners assn": "Hollis v. Chestnut Bend Homeowners Ass'n",
    "lapid laurel llc v zoning bd of adjustment of twp of scotch plains": "Lapid-Laurel, LLC v. Zoning Bd. of Adjustment of Twp. of Scotch Plains",
    "oxford house inc v city of virginia beach": "Oxford House, Inc. v. City of Virginia Beach",
    "city of edmonds v oxford house inc": "City of Edmonds v. Oxford House, Inc.",
    "city of edmonds v oxford house inc 514 u s 725 1995": "City of Edmonds v. Oxford House, Inc.",
    "tsombanidis v west haven fire dept": "Tsombanidis v. West Haven Fire Dep't",
    "trafficante v metropolitan life ins co": "Trafficante v. Metropolitan Life Ins. Co.",
    "village of arlington heights v metropolitan housing development corp": "Village of Arlington Heights v. Metropolitan Housing Dev. Corp.",
    "texas dept of housing and community affairs v inclusive communities project inc": "Texas Dep't of Hous. & Cmty. Affairs v. Inclusive Communities Project, Inc.",
    "inclusive communities project inc v texas dept of housing and community affairs": "Texas Dep't of Hous. & Cmty. Affairs v. Inclusive Communities Project, Inc.",
    "alexander v choate": "Alexander v. Choate",
    "sutton v united air lines inc": "Sutton v. United Air Lines, Inc.",
    "bragdon v abbott": "Bragdon v. Abbott",
    "christiansburg garment co v eeoc": "Christiansburg Garment Co. v. EEOC",
    "spokeo inc v robins": "Spokeo, Inc. v. Robins",
    "overlook mut homes inc v spencer": "Overlook Mut. Homes, Inc. v. Spencer",
    "community services inc v wind gap mun auth": "Community Services, Inc. v. Wind Gap Mun. Auth.",
    "cmty servs inc v wind gap mun auth": "Community Services, Inc. v. Wind Gap Mun. Auth.",
    "pac shores props llc v city of newport beach": "Pacific Shores Properties, LLC v. City of Newport Beach",
    "pacific shores props llc v city of newport beach": "Pacific Shores Properties, LLC v. City of Newport Beach",
}

AUTHORITY_FUNCTION_MAP = {
    "Ashcroft v. Iqbal": ["pleading_plausibility", "federal_procedure"],
    "Bell Atlantic Corp. v. Twombly": ["pleading_plausibility", "federal_procedure"],
    "McDonnell Douglas Corp. v. Green": ["burden_shifting", "proof_structure"],
    "Havens Realty Corp. v. Coleman": ["standing", "fha_substantive"],
    "City of Cleburne v. Cleburne Living Center": ["disability_status", "equal_protection_analog"],
    "Lujan v. Defenders of Wildlife": ["standing", "jurisdiction"],
    "Celotex Corp. v. Catrett": ["summary_judgment", "federal_procedure"],
    "Anderson v. Liberty Lobby, Inc.": ["summary_judgment", "federal_procedure"],
    "Meyer v. Holley": ["vicarious_liability", "fha_substantive"],
    "Bloch v. Frischholz": ["interference_coercion", "fha_substantive"],
    "Dubois v. Ass'n of Apartment Owners of 2987 Kalakaua": ["reasonable_accommodation", "fha_substantive"],
    "Giebeler v. M & B Associates": ["reasonable_accommodation", "fha_substantive"],
    "Bhogaita v. Altamonte Heights Condo. Ass'n, Inc.": ["reasonable_accommodation", "fha_substantive"],
    "Schwarz v. City of Treasure Island": ["zoning_group_home", "fha_substantive"],
    "Hollis v. Chestnut Bend Homeowners Ass'n": ["reasonable_accommodation", "fha_substantive"],
    "Lapid-Laurel, LLC v. Zoning Bd. of Adjustment of Twp. of Scotch Plains": ["zoning_group_home", "reasonable_accommodation"],
    "City of Edmonds v. Oxford House, Inc.": ["zoning_group_home", "fha_substantive"],
    "Oxford House, Inc. v. City of Virginia Beach": ["zoning_group_home", "fha_substantive"],
    "Tsombanidis v. West Haven Fire Dep't": ["reasonable_accommodation", "disparate_impact"],
    "Trafficante v. Metropolitan Life Ins. Co.": ["standing", "fha_substantive"],
    "Village of Arlington Heights v. Metropolitan Housing Dev. Corp.": ["disparate_impact", "intent_framework"],
    "Texas Dep't of Hous. & Cmty. Affairs v. Inclusive Communities Project, Inc.": ["disparate_impact", "fha_substantive"],
    "Christiansburg Garment Co. v. EEOC": ["fees_and_remedies", "federal_procedure"],
    "Bragdon v. Abbott": ["disability_status", "ada_crosswalk"],
    "Alexander v. Choate": ["disability_status", "rehab_act_crosswalk"],
}

PLAINTIFF_BUCKETS = [
    "INDIVIDUAL_TENANT",
    "GROUP_HOME_OPERATOR",
    "FAIR_HOUSING_ORG",
    "GOVERNMENT",
]

CASE_TYPE_BUCKETS = [
    "reasonable_accommodation_denial",
    "disparate_treatment",
    "disparate_impact",
    "retaliation",
    "design_and_construction",
]


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


def results_dir() -> Path:
    path = repo_root() / "results"
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_database() -> List[dict]:
    path = data_dir() / "FHA_Unified_Database.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def screened_cases(records: Iterable[dict]) -> List[dict]:
    return [r for r in records if r.get("screening_result") == "YES" and r.get("case_name")]


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\s+", " ", text).strip(" ,;:")
    return text


def title_case_case_name(name: str) -> str:
    tokens = []
    for raw in name.split():
        lower = raw.lower()
        if lower in {"v", "v.", "vs", "vs."}:
            tokens.append("v.")
        elif lower in {"u.s.", "u.s", "us"}:
            tokens.append("U.S.")
        elif lower in {"inc", "inc."}:
            tokens.append("Inc.")
        elif lower in {"corp", "corp."}:
            tokens.append("Corp.")
        elif lower in {"co", "co."}:
            tokens.append("Co.")
        elif lower in {"llc", "l.l.c."}:
            tokens.append("LLC")
        elif lower in {"assn", "ass'n", "assoc.", "association"}:
            tokens.append(raw)
        else:
            tokens.append(raw[0].upper() + raw[1:] if raw else raw)
    return " ".join(tokens)


def infer_case_name(raw_citation: str) -> str:
    raw_citation = clean_text(raw_citation)
    reporter_split = re.search(r",\s*\d+\s+[A-Z]", raw_citation)
    if reporter_split:
        return clean_text(raw_citation[: reporter_split.start()])
    date_split = re.search(r"\s*\(\d{4}\)$", raw_citation)
    if date_split:
        return clean_text(raw_citation[: date_split.start()])
    if " v. " in raw_citation or " v " in raw_citation:
        return raw_citation
    return raw_citation


def normalize_citation(raw_citation: str) -> Tuple[str, str]:
    raw_citation = clean_text(raw_citation)
    guessed = infer_case_name(raw_citation)
    slug = slugify(guessed)
    canonical = EXPLICIT_CANONICAL_MAP.get(slug)
    if canonical:
        return canonical, slugify(canonical)
    canonical = title_case_case_name(guessed)
    canonical = canonical.replace(" V. ", " v. ")
    canonical = re.sub(r"\bv\.\.\b", "v.", canonical)
    return canonical, slugify(canonical)


def classify_authority(authority: str) -> List[str]:
    if authority in AUTHORITY_FUNCTION_MAP:
        return AUTHORITY_FUNCTION_MAP[authority]
    slug = slugify(authority)
    tags: List[str] = []
    if any(token in slug for token in ["iqbal", "twombly", "weiland"]):
        tags.extend(["pleading_plausibility", "federal_procedure"])
    if any(token in slug for token in ["lujan", "spokeo", "havens", "trafficante"]):
        tags.append("standing")
    if any(token in slug for token in ["celotex", "liberty lobby", "matsushita"]):
        tags.extend(["summary_judgment", "federal_procedure"])
    if any(token in slug for token in ["giebeler", "bhogaita", "hollis", "dubois", "lapid laurel"]):
        tags.append("reasonable_accommodation")
    if any(token in slug for token in ["oxford house", "schwarz", "edmonds", "tsombanidis", "cleburne"]):
        tags.append("zoning_group_home")
    if any(token in slug for token in ["inclusive communities", "arlington heights"]):
        tags.append("disparate_impact")
    if any(token in slug for token in ["meyer", "frischholz", "holley"]):
        tags.append("fha_substantive")
    if not tags:
        tags.append("uncoded_general_authority")
    ordered = []
    for tag in tags:
        if tag not in ordered:
            ordered.append(tag)
    return ordered


def bucket_top_counts(cases: List[dict], key_fn, top_n: int = 10) -> List[Tuple[str, int]]:
    counter = Counter()
    for case in cases:
        for citation in key_fn(case):
            counter[citation] += 1
    return counter.most_common(top_n)


def render_count_table(rows: List[Tuple[str, int]], headers: Tuple[str, str]) -> List[str]:
    lines = [f"| {headers[0]} | {headers[1]} |", "|---|---:|"]
    for label, value in rows:
        lines.append(f"| {label} | {value} |")
    return lines


def main() -> None:
    db = load_database()
    cases = screened_cases(db)
    out_json = data_dir() / "unified_normalized_citations.json"
    out_report = results_dir() / "unified_overnight_citation_baseline.md"
    out_taxonomy = data_dir() / "doctrinal_function_taxonomy.md"

    normalized_records = []
    raw_counter = Counter()
    normalized_counter = Counter()
    authority_to_raw = defaultdict(Counter)
    record_lookup: Dict[str, List[str]] = {}

    for case in cases:
        raw_items = [item for item in (case.get("key_cases_cited") or []) if isinstance(item, str) and item.strip()]
        normalized_items = []
        for item in raw_items:
            raw_counter[item] += 1
            canonical, canonical_slug = normalize_citation(item)
            normalized_counter[canonical] += 1
            authority_to_raw[canonical][item] += 1
            normalized_items.append(
                {
                    "raw": item,
                    "normalized": canonical,
                    "normalized_slug": canonical_slug,
                    "doctrinal_functions": classify_authority(canonical),
                }
            )
        record_lookup[case.get("source_file") or case["case_name"]] = [entry["normalized"] for entry in normalized_items]
        normalized_records.append(
            {
                "case_name": case.get("case_name"),
                "source_file": case.get("source_file"),
                "year": case.get("year"),
                "plaintiff_type": case.get("plaintiff_type"),
                "primary_claim_type": case.get("primary_claim_type"),
                "pro_se": case.get("pro_se"),
                "raw_citation_count": len(raw_items),
                "normalized_citation_count": len(normalized_items),
                "normalized_citations": normalized_items,
            }
        )

    top_authorities = []
    for authority, count in normalized_counter.most_common(TOP_AUTHORITIES):
        variants = authority_to_raw[authority].most_common(5)
        top_authorities.append(
            {
                "authority": authority,
                "count": count,
                "doctrinal_functions": classify_authority(authority),
                "raw_variants": [{"citation": raw, "count": raw_count} for raw, raw_count in variants],
            }
        )

    plaintiff_breakdowns = {}
    for bucket in PLAINTIFF_BUCKETS:
        subset = [case for case in normalized_records if case.get("plaintiff_type") == bucket]
        plaintiff_breakdowns[bucket] = bucket_top_counts(subset, lambda c: [x["normalized"] for x in c["normalized_citations"]])

    case_type_breakdowns = {}
    for bucket in CASE_TYPE_BUCKETS:
        subset = [case for case in normalized_records if case.get("primary_claim_type") == bucket]
        case_type_breakdowns[bucket] = bucket_top_counts(subset, lambda c: [x["normalized"] for x in c["normalized_citations"]])

    pro_se_subset = [c for c in normalized_records if c.get("pro_se") is True]
    represented_subset = [c for c in normalized_records if c.get("pro_se") is False]

    stats = {
        "screened_case_count": len(cases),
        "cases_with_citations": sum(1 for c in normalized_records if c["raw_citation_count"] > 0),
        "raw_total_citation_mentions": sum(raw_counter.values()),
        "raw_unique_citations": len(raw_counter),
        "normalized_total_citation_mentions": sum(normalized_counter.values()),
        "normalized_unique_authorities": len(normalized_counter),
        "top_authorities": top_authorities,
        "top_by_plaintiff_bucket": {
            bucket: [{"authority": name, "count": count} for name, count in rows]
            for bucket, rows in plaintiff_breakdowns.items()
        },
        "top_by_case_type_bucket": {
            bucket: [{"authority": name, "count": count} for name, count in rows]
            for bucket, rows in case_type_breakdowns.items()
        },
        "pro_se_top_authorities": [{"authority": name, "count": count} for name, count in bucket_top_counts(pro_se_subset, lambda c: [x["normalized"] for x in c["normalized_citations"]])],
        "represented_top_authorities": [{"authority": name, "count": count} for name, count in bucket_top_counts(represented_subset, lambda c: [x["normalized"] for x in c["normalized_citations"]])],
        "records": normalized_records,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)

    taxonomy_lines = [
        "# Doctrinal Function Taxonomy for Unified Overnight Citation Baseline",
        "",
        f"Top authorities coded: {len(top_authorities)}",
        "",
        "| Authority | Mentions | Doctrinal function tags | Representative raw variants |",
        "|---|---:|---|---|",
    ]
    for item in top_authorities:
        variants = "; ".join(v["citation"] for v in item["raw_variants"][:3])
        tags = ", ".join(item["doctrinal_functions"])
        taxonomy_lines.append(f"| {item['authority']} | {item['count']} | {tags} | {variants} |")
    out_taxonomy.write_text("\n".join(taxonomy_lines) + "\n", encoding="utf-8")

    report_lines = [
        "# Unified Overnight Citation Baseline",
        "",
        f"Screened cases analyzed: {len(cases)}",
        f"Cases with at least one citation: {stats['cases_with_citations']}",
        f"Raw citation mentions: {stats['raw_total_citation_mentions']}",
        f"Raw unique citation strings: {stats['raw_unique_citations']}",
        f"Normalized unique authorities: {stats['normalized_unique_authorities']}",
        "",
        "## Top normalized authorities overall",
        "",
    ]
    report_lines.extend(render_count_table([(item["authority"], item["count"]) for item in top_authorities[:20]], ("Authority", "Mentions")))
    report_lines.extend([
        "",
        "## Pro se vs represented top citations",
        "",
        "### Pro se",
        "",
    ])
    report_lines.extend(render_count_table(bucket_top_counts(pro_se_subset, lambda c: [x["normalized"] for x in c["normalized_citations"]]), ("Authority", "Mentions")))
    report_lines.extend(["", "### Represented", ""])
    report_lines.extend(render_count_table(bucket_top_counts(represented_subset, lambda c: [x["normalized"] for x in c["normalized_citations"]]), ("Authority", "Mentions")))

    for bucket in PLAINTIFF_BUCKETS:
        report_lines.extend(["", f"## Top citations for plaintiff bucket: {bucket}", ""])
        report_lines.extend(render_count_table(plaintiff_breakdowns[bucket], ("Authority", "Mentions")))

    for bucket in CASE_TYPE_BUCKETS:
        report_lines.extend(["", f"## Top citations for case-type bucket: {bucket}", ""])
        report_lines.extend(render_count_table(case_type_breakdowns[bucket], ("Authority", "Mentions")))

    report_lines.extend([
        "",
        "## Notes",
        "",
        "- Normalization collapses reporter variants and short-form duplications into a canonical authority name.",
        "- Doctrinal function tags are intentionally lightweight and are designed to scaffold follow-on citation-gap analysis, not to replace later close reading.",
        f"- Detailed per-record normalization output is in `{out_json}`.",
        f"- Top-authority doctrinal tags are in `{out_taxonomy}`.",
    ])
    out_report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_taxonomy}")
    print(f"Wrote {out_report}")
    print(f"Normalized {len(raw_counter)} raw citation strings into {len(normalized_counter)} authorities")


if __name__ == "__main__":
    main()
