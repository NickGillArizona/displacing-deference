#!/usr/bin/env python3
"""
Generate follow-on opportunity scaffolding for the unified overnight run.

Outputs:
- results/unified_follow_on_opportunities.md

Usage:
  python3 unified_follow_on_opportunities.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List


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


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def pct(num: int, den: int) -> float:
    return round(100.0 * num / den, 1) if den else 0.0


def top_count(items: List[dict], field: str) -> str:
    counts: Dict[str, int] = {}
    for item in items:
        key = str(item.get(field) or "UNKNOWN")
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return "none"
    return max(counts.items(), key=lambda kv: kv[1])[0]


def build_opportunity(priority: str, title: str, score: float, evidence: List[str], next_steps: List[str], suggested_output: str) -> dict:
    return {
        "priority": priority,
        "title": title,
        "score": round(score, 2),
        "evidence": evidence,
        "next_steps": next_steps,
        "suggested_output": suggested_output,
    }


def main() -> None:
    citation_path = data_dir() / "unified_normalized_citations.json"
    inventory_path = data_dir() / "unified_raw_text_target_inventory.json"
    report_path = results_dir() / "unified_follow_on_opportunities.md"

    if not citation_path.exists():
        raise SystemExit(f"Missing prerequisite output: {citation_path}")
    if not inventory_path.exists():
        raise SystemExit(f"Missing prerequisite output: {inventory_path}")

    citation = load_json(citation_path)
    inventory = load_json(inventory_path)

    records = citation.get("records", [])
    pro_se_records = [r for r in records if r.get("pro_se") is True]
    represented_records = [r for r in records if r.get("pro_se") is False]
    pro_se_iqbal = sum(1 for r in pro_se_records if any("Iqbal" in item.get("normalized", "") or "Twombly" in item.get("normalized", "") for item in r.get("normalized_citations", [])))
    represented_iqbal = sum(1 for r in represented_records if any("Iqbal" in item.get("normalized", "") or "Twombly" in item.get("normalized", "") for item in r.get("normalized_citations", [])))

    buckets = inventory.get("buckets", {})
    bucket_total_counts = inventory.get("bucket_counts_total") or inventory.get("bucket_counts") or {name: len(items) for name, items in buckets.items()}
    bucket_total_raw_hits = inventory.get("bucket_raw_text_available_counts_total") or inventory.get("bucket_raw_text_available_counts") or {name: sum(1 for item in items if item.get("raw_text_available")) for name, items in buckets.items()}
    ambiguous = buckets.get("likely_ambiguous_pleading_losses", [])
    public_process = buckets.get("public_defendant_process_cases", [])
    open_textured = buckets.get("open_textured_cases_with_nontrivial_citations", [])
    exemplars = buckets.get("citation_differential_exemplars", [])
    tiny = buckets.get("tiny_summaries", [])

    opportunities = []

    pro_se_gap = pct(pro_se_iqbal, len(pro_se_records)) - pct(represented_iqbal, len(represented_records))
    opportunities.append(
        build_opportunity(
            "HIGH",
            "Pro se pleading-mechanism divergence memo",
            9.2 + max(pro_se_gap, 0) / 20.0,
            [
                f"Iqbal/Twombly appears in {pro_se_iqbal}/{len(pro_se_records)} pro se citation-bearing records ({pct(pro_se_iqbal, len(pro_se_records))}%).",
                f"Iqbal/Twombly appears in {represented_iqbal}/{len(represented_records)} represented records ({pct(represented_iqbal, len(represented_records))}%).",
                f"Gap between the two groups: {round(pro_se_gap, 1)} percentage points.",
                f"Raw-text-ready ambiguous pleading-loss inventory already contains {bucket_total_counts.get('likely_ambiguous_pleading_losses', len(ambiguous))} cases, with {bucket_total_raw_hits.get('likely_ambiguous_pleading_losses', sum(1 for x in ambiguous if x.get('raw_text_available')))} raw-text hits.",
            ],
            [
                "Take the top 40 ambiguous pleading-loss cases and split them by pro se status.",
                "Code whether dismissal turns on missing facts, wrong doctrinal hook, or public-process framing failure.",
                "Cross-check whether Iqbal/Twombly is doing actual work or just boilerplate.",
            ],
            "Short note-facing memo plus appendix table comparing pro se and represented pleading-failure mechanisms.",
        )
    )

    opportunities.append(
        build_opportunity(
            "HIGH",
            "Public-defendant process-failure subset study",
            8.8 + min(len(public_process), 250) / 250.0,
            [
                f"Public-defendant process bucket contains {bucket_total_counts.get('public_defendant_process_cases', len(public_process))} cases.",
                f"{bucket_total_raw_hits.get('public_defendant_process_cases', sum(1 for x in public_process if x.get('raw_text_available')))} of those already have resolvable raw text.",
                f"Dominant defendant type in the bucket: {top_count(public_process, 'defendant_type')}.",
                "This subset is directly aligned with the overnight plan's public-defendant process-refinement lane.",
            ],
            [
                "Start with the top 30 scored public-process cases.",
                "Tag whether the court focuses on request clarity, interactive-process breakdown, eligibility proof, or institutional authority fragmentation.",
                "Compare municipalities and housing authorities separately once the raw-text review lands.",
            ],
            "Targeted report feeding the public-defendant process-failure refinement and tractability sections.",
        )
    )

    opportunities.append(
        build_opportunity(
            "HIGH",
            "Citation-gap / doctrinal-omission memo for open-textured cases",
            8.5 + min(len(open_textured), 300) / 300.0,
            [
                f"Open-textured, citation-rich inventory contains {bucket_total_counts.get('open_textured_cases_with_nontrivial_citations', len(open_textured))} cases.",
                f"{bucket_total_raw_hits.get('open_textured_cases_with_nontrivial_citations', sum(1 for x in open_textured if x.get('raw_text_available')))} of them have raw-text paths already resolved.",
                "These are the best candidates for the plan's citation-gap target-group report because they have enough authority density to inspect what is missing, not just what is cited.",
                f"Top authority overall remains {citation.get('top_authorities', [{}])[0].get('authority', 'unknown')}.",
            ],
            [
                "Read the top 25 open-textured cases by score.",
                "Mark whether the opinion cites procedural authorities without pairing them with FHA-specific accommodation or zoning precedents.",
                "Group resulting omissions by plaintiff type and defendant type.",
            ],
            "Doctrinal-gap memo that can be tied directly to plaintiff-side omission and AFFH framing arguments.",
        )
    )

    opportunities.append(
        build_opportunity(
            "MEDIUM-HIGH",
            "Citation-differential exemplar packet",
            7.9 + min(len(exemplars), 150) / 300.0,
            [
                f"Citation-differential exemplars identified: {len(exemplars)}.",
                f"Raw text available for {sum(1 for x in exemplars if x.get('raw_text_available'))} of them.",
                "These cases already show mixed procedural/substantive citation profiles, which makes them efficient teaching examples for a morning memo.",
            ],
            [
                "Select 12 exemplars spanning multiple circuits and plaintiff types.",
                "Extract 1-2 paragraph doctrinal narratives for each case showing how pleading authorities crowd out or coexist with substantive FHA law.",
                "Use the packet as a bridge between citation tables and raw-text close reading.",
            ],
            "Exemplar appendix or synthetic classification memo usable in the note's doctrinal discussion.",
        )
    )

    opportunities.append(
        build_opportunity(
            "MEDIUM",
            "Tiny-summary reopening queue",
            7.2 + min(len(tiny), 300) / 500.0,
            [
                f"Tiny-summary bucket contains {len(tiny)} screened cases using the <=700-character threshold.",
                f"{sum(1 for x in tiny if x.get('raw_text_available'))} already map to raw text.",
                "This is the cleanest queue for improving structured-data confidence if the overnight autopsy returns ambiguous results.",
            ],
            [
                "Reopen the first 50 tiny-summary cases with raw text.",
                "Prioritize the intersection with ambiguous pleading losses and public-process cases.",
                "Use these as the first disagreement-rerun tranche if any autopsy field underperforms validation.",
            ],
            "Validation support queue rather than a standalone thesis memo.",
        )
    )

    opportunities.sort(key=lambda item: (-item["score"], item["title"]))

    lines = [
        "# Unified Follow-On Opportunities",
        "",
        "This file is a scaffolding memo for the overnight run. It ranks bounded next studies that can start immediately from the citation baseline and raw-text inventory outputs.",
        "",
        "## Input status",
        "",
        f"- Citation baseline: `{citation_path}`",
        f"- Raw-text inventory: `{inventory_path}`",
        f"- Screened records in citation baseline: {len(records)}",
        f"- Ambiguous pleading-loss targets: {len(ambiguous)}",
        f"- Public-defendant process targets: {len(public_process)}",
        f"- Open-textured citation-rich targets: {len(open_textured)}",
        f"- Citation-differential exemplars: {len(exemplars)}",
        f"- Tiny-summary reopen queue: {len(tiny)}",
        "",
        "## Ranked opportunities",
        "",
    ]

    for idx, item in enumerate(opportunities, start=1):
        lines.extend([
            f"### {idx}. {item['title']} ({item['priority']}, score {item['score']})",
            "",
            "Evidence:",
        ])
        lines.extend([f"- {e}" for e in item["evidence"]])
        lines.extend(["", "Suggested next steps:"])
        lines.extend([f"- {step}" for step in item["next_steps"]])
        lines.extend(["", f"Suggested output: {item['suggested_output']}", ""])

    lines.extend([
        "## Immediate default recommendation",
        "",
        "If only one additional study can be launched before the batch returns, start with the pro se pleading-mechanism divergence memo and use the ambiguous pleading-loss inventory as the sampling frame.",
        "",
        "## Queue logic",
        "",
        "- If autopsy validation is strong, prioritize the public-defendant process and citation-gap memos.",
        "- If autopsy validation is mixed, use the tiny-summary queue and the exemplar packet as the first raw-text rerun tranche.",
        "- If morning time is short, convert the top-ranked opportunity plus the exemplar packet into a single synthetic memo rather than several separate products.",
    ])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {report_path}")
    print(f"Ranked {len(opportunities)} follow-on opportunities")


if __name__ == "__main__":
    main()
