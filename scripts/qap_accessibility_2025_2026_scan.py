from __future__ import annotations

import html
import io
import json
import re
import subprocess
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

warnings.simplefilter("ignore", InsecureRequestWarning)

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CACHE = RESULTS / "qap_accessibility_2025_2026_cache"
CACHE.mkdir(parents=True, exist_ok=True)

OUTPUT_JSON = RESULTS / "qap_accessibility_2025_2026.json"
OUTPUT_MD = RESULTS / "qap_accessibility_update_analysis.md"

CATEGORY_LABELS = {
    "exceeds_504": "Exceeds Section 504",
    "requires_504": "Requires Section 504",
    "less_than_504": "Direct requirement below Section 504",
    "incentives_only": "Incentives only",
    "none": "No direct QAP accessibility provision observed",
    "manual_review": "Manual review needed",
}

REQUESTED_CATEGORY_MAP = {
    "exceeds_504": "exceeds_504",
    "requires_504": "requires_at_504",
    "less_than_504": "none",
    "incentives_only": "incentives_only",
    "none": "none",
    "manual_review": "none",
}

REQUESTED_LABELS = {
    "exceeds_504": "Exceeds 504",
    "requires_at_504": "Requires 504",
    "incentives_only": "Incentives only",
    "none": "None",
}

BASELINE = {
    "AL": "incentives_only",
    "AK": "requires_504",
    "AZ": "less_than_504",
    "AR": "none",
    "CA": "exceeds_504",
    "CO": "none",
    "CT": "none",
    "DE": "incentives_only",
    "FL": "requires_504",
    "GA": "requires_504",
    "HI": "none",
    "IA": "less_than_504",
    "ID": "none",
    "IL": "exceeds_504",
    "IN": "less_than_504",
    "KS": "requires_504",
    "KY": "less_than_504",
    "LA": "none",
    "MA": "requires_504",
    "MD": "requires_504",
    "ME": "requires_504",
    "MI": "none",
    "MN": "incentives_only",
    "MO": "none",
    "MS": "incentives_only",
    "MT": "incentives_only",
    "NC": "less_than_504",
    "ND": "none",
    "NE": "less_than_504",
    "NH": "requires_504",
    "NJ": "none",
    "NM": "none",
    "NV": "none",
    "NY": "requires_504",
    "OH": "requires_504",
    "OK": "none",
    "OR": "none",
    "PA": "incentives_only",
    "RI": "incentives_only",
    "SC": "incentives_only",
    "SD": "requires_504",
    "TN": "none",
    "TX": "requires_504",
    "UT": "none",
    "VA": "incentives_only",
    "VT": "none",
    "WA": "less_than_504",
    "WI": "none",
    "WV": "requires_504",
    "WY": "none",
}

STATE_NAMES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MS": "Mississippi",
    "MT": "Montana",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}

STATE_DOCS = {
    "AL": {"url": "https://www.ahfa.com/programs/rental-housing/allocation-application-information/current-year-allocation-plans", "kind": "page"},
    "AK": {"url": "https://www.ahfc.us/application/files/6517/5088/4408/FY2026_GOAL_Qualified_Allocation_Plan_06-25-25.pdf", "kind": "pdf"},
    "AZ": {"url": "https://housing.az.gov/2026-2027-qap-final-version-posted", "kind": "page"},
    "AR": {"url": "https://adfa.arkansas.gov/documents/2026-qualified-allocation-plan-qap/", "kind": "page"},
    "CA": {"url": "https://www.treasurer.ca.gov/ctcac/programreg/2025/regulations.pdf", "kind": "pdf"},
    "CO": {"url": "https://www.novoco.com/public-media/documents/colorado-lihtc-final-qap-2025-26-11212024.pdf", "kind": "pdf"},
    "CT": {"url": "https://www.chfa.org/assets/1/19/FINAL_2026_QAP.pdf?14379", "kind": "pdf"},
    "DE": {"url": "https://www.novoco.com/public-media/documents/delaware-final-qap-2025-2026-04232025.pdf", "kind": "pdf"},
    "DC": {"url": "https://dhcd.dc.gov/sites/default/files/dc/sites/dhcd/publication/attachments/2025%20Qualified%20Allocation%20Plan%20Final%20Published%2012.9.25.pdf", "kind": "pdf"},
    "FL": {"url": "https://www.floridahousing.org/docs/default-source/programs/competitive/2025-rule-development-process/2025-qualified-allocation-plan-(qap-2-7-25-draft.pdf?sfvrsn=80f6f07b_1", "kind": "pdf"},
    "GA": {"url": "https://dca.georgia.gov/document/document/2026-2027-qap-draft-3pdf/download", "kind": "pdf"},
    "HI": {"url": "https://dbedt.hawaii.gov/hhfdc/files/2025/06/2026-QAP.For_.Public.Hearing.Ramseyer.pdf", "kind": "pdf"},
    "IA": {"url": "https://opportunityiowa.gov/housing/rental-programs/programs-developers-communities-and-property-owners/housing-tax-credit-program/resources/lihtc-notices", "kind": "page"},
    "ID": {"url": "https://www.idahohousing.com/documents/combined-annual-lihtc-application-information.pdf/", "kind": "pdf"},
    "IL": {"url": "https://www.ihda.org/developers/qap/", "kind": "page"},
    "IN": {"url": "https://www.in.gov/ihcda/files/2025-QAP-Final.pdf", "kind": "pdf"},
    "KS": {"url": "https://kshousingcorp.org/wp-content/uploads/2025/10/2026-QAP-FINAL.pdf", "kind": "pdf"},
    "KY": {"url": "https://www.kyhousing.org/Partners/Developers/Multifamily/Documents/2025-2026%20Qualified%20Allocation%20Plan.pdf", "kind": "pdf"},
    "LA": {"url": "https://www.lhc.la.gov/hubfs/Document%20Libraries/Housing%20Development/Funding%20Opportunities/LIHTC/2025-2026%20Draft%20QAP%20Redlined%20as%20of%2010-03-24.pdf", "kind": "pdf"},
    "MA": {"url": "https://www.mass.gov/doc/2025-2026-lihtc-qap/download", "kind": "pdf"},
    "MD": {"url": "https://dhcd.maryland.gov/HousingDevelopment/Documents/QAP_MRFP/2025-QAP-Final-Draft-Clean.pdf", "kind": "pdf"},
    "ME": {"url": "https://www.mainehousing.org/docs/default-source/development/qap/2025-2026-qap.pdf?sfvrsn=a78d9e15_2", "kind": "pdf"},
    "MI": {"url": "https://www.michigan.gov/mshda/developers/lihtc/lihtc/qualified-allocation-plan", "kind": "page"},
    "MN": {"url": "https://mnhousing.gov/home/rental-housing/housing-development-and-capital-programs/housing-tax-credits/qualified-allocation-plan-qap", "kind": "page"},
    "MO": {"url": "https://mhdc.com/media/j3hj0emf/2026-qap_draft_clean-version.pdf", "kind": "pdf"},
    "MS": {"url": "https://www.novoco.com/public-media/documents/mississippi-lihtc-qap-final-2025-01072025.pdf", "kind": "pdf"},
    "MT": {"url": "https://commerce.mt.gov/_shared/housing/Multifamily/docs/2026-QAP-20241125-Final-Approved.pdf", "kind": "pdf"},
    "NC": {"url": "https://nchfa.com/sites/default/files/forms_resources/2025-12/2026FinalQAP.pdf", "kind": "pdf"},
    "ND": {"url": "https://www.ndhousing.nd.gov/sites/www/files/documents/Plans/2026LIHTCAllocationPlan.pdf", "kind": "pdf"},
    "NE": {"url": "https://opportunity.nebraska.gov/wp-content/uploads/2025/05/LIHTC-2024-25-QAP.pdf", "kind": "pdf"},
    "NH": {"url": "https://www.nhhfa.org/wp-content/uploads/2024/04/2025-2026-Qualified-Allocation-Plan.pdf", "kind": "pdf"},
    "NJ": {"url": "https://www.nj.gov/dca/hmfa/developers/docs/lihtc/qap/tc_qap_download.pdf", "kind": "pdf"},
    "NM": {"url": "https://housingnm.org/uploads/documents/FINAL_2025_QAP.pdf", "kind": "pdf"},
    "NV": {"url": "https://housing.nv.gov/uploadedFiles/housingnewnvgov/Content/Programs/LIT/QAP/2026%20QAP%20clean%20final%2012.24.2025.pdf", "kind": "pdf"},
    "NY": {"url": "https://hcr.ny.gov/system/files/documents/2025/06/rule-text-title-9-part-2040-9-dhcr-qap-effective-6-11-2025.pdf", "kind": "pdf"},
    "OH": {"url": "https://ohiohome.org/ppd/documents/2026-2027-9Percent-LIHTC-QAP-Redline.pdf", "kind": "pdf"},
    "OK": {"url": "https://www.novoco.com/public-media/documents/oklahoma-final-qap-2026-09242025.pdf", "kind": "pdf"},
    "OR": {"url": "https://www.oregon.gov/ohcs/rental-housing/housing-development/development-resources/Documents/QAP/2025-qap-final.pdf", "kind": "pdf"},
    "PA": {"url": "https://www.phfa.org/forms/multifamily_news/news/2024/2025-2026-lihtc-qap.pdf", "kind": "pdf"},
    "RI": {"url": "https://www.rihousing.com/wp-content/uploads/2026-Section-7-QAP.pdf", "kind": "pdf"},
    "SC": {"url": "https://schousing.sc.gov/sites/schousing/files/Documents/Development/LIHTC/2026%20LIHTC%20Program/2026-QAP-20251015.pdf", "kind": "pdf"},
    "SD": {"url": "https://www.sdhousing.org/forms/low-income-housing-tax-credit-qualified-allocation-plan", "kind": "page"},
    "TN": {"url": "https://thda.org/wp-content/uploads/2025/10/2026-QAP-FOR-GOV-SIGNATURE-10.23.2025.pdf", "kind": "pdf"},
    "TX": {"url": "https://www.tdhca.texas.gov/sites/default/files/multifamily/docs/26-QAP.pdf", "kind": "pdf"},
    "UT": {"url": "https://www.novoco.com/public-media/documents/utah-final-qap-2026-05092025.pdf", "kind": "pdf"},
    "VA": {"url": "https://www.novoco.com/public-media/documents/virginia-lihtc-qap-2025-12112024.pdf", "kind": "pdf"},
    "VT": {"url": "https://vhfa.org/developers/lihtc/qap", "kind": "page"},
    "WA": {"url": "https://www.wshfc.org/mhcf/9percent/2026application/ProgramDocs/2026qap.pdf", "kind": "pdf"},
    "WI": {"url": "https://www.wheda.com/globalassets/documents/tax-credits/htc/2025/2025-26-qap.pdf", "kind": "pdf"},
    "WV": {"url": "https://www.wvhdf.com/wp-content/uploads/2025/05/2025-and-2026-Allocation-Plan.pdf", "kind": "pdf"},
    "WY": {"url": "https://www.wyomingcda.com/affordable-housing/", "kind": "page"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}

KEYWORD_PATTERN = re.compile(
    r"(?i)section 504|ufas|accessible|accessibility|mobility|hearing|visual|sensory|type a|type\s*a|ansi|adaptable|visitable|universal design|barrier free|ada"
)

PAGE_TEXT_CLEANUP = re.compile(r"\s+")
YEAR_PATTERN = re.compile(r"\b(20[0-9]{2})(?:\s*[-/]\s*(20[0-9]{2}))?\b")

REQUESTED_TAXONOMY_NOTE = (
    "Requested four-way taxonomy collapses detailed 'less_than_504' and provisional 'manual_review' "
    "records into requested category 'none'; see current_detailed_category for the more faithful coding."
)

PREFERRED_PAGE_PDFS = {
    "VT": "https://vhfa.org/sites/default/files/developers/Draft_QAP_3-24-26.pdf",
}

MANUAL_OVERRIDES: dict[str, dict[str, Any]] = {
    "VT": {
        "document_year_guess": "2026",
        "current_detailed_category": "less_than_504",
        "auto_classification_reason": "Manual override: Vermont's newer 2026 draft QAP requires all projects and units to meet VHFA Universal Design Policy plus Vermont adaptable/visitable standards; treated as a direct below-Section-504 requirement rather than a full Section 504/UFAS floor.",
        "keyword_snippets": [
            "All projects and units must meet the VHFA Universal Design Policy, the Vermont Access Rules for being “adaptable” and “visitable”, and the VHCB/VHFA Building Design Standards.",
            "Projects will be given preference, in order, for: Rehabilitating existing affordable housing, including adding new accessible units and improving visitability.",
        ],
        "document_status_note": "Vermont page listed a March 24, 2026 draft QAP (titled 2027-2028) plus a 2024-25 current QAP; this record uses the newer 2026-released draft to avoid the stale 2020-2021 source previously selected by the page-scoring routine.",
        "manual_notes": "Manual override applied because the page-scoring routine previously selected Vermont's 2020-2021 QAP from the archive list. The newer March 24, 2026 draft and the still-current 2024-25 QAP both impose adaptable/visitable or universal-design requirements, but not a full Section 504/UFAS 5%/2% floor.",
    }
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def cache_path(key: str, ext: str) -> Path:
    return CACHE / f"{slugify(key)}.{ext}"


def fetch(url: str, binary: bool = False) -> bytes | str:
    ext = "bin" if binary else "txt"
    path = cache_path(url, ext)
    if path.exists():
        return path.read_bytes() if binary else path.read_text(encoding="utf-8")
    resp = requests.get(url, headers=HEADERS, timeout=90, verify=False, allow_redirects=True)
    resp.raise_for_status()
    if binary:
        path.write_bytes(resp.content)
        return resp.content
    resp.encoding = resp.encoding or "utf-8"
    path.write_text(resp.text, encoding="utf-8")
    return resp.text


def pdf_text_from_url(url: str) -> str:
    pdf_bytes = fetch(url, binary=True)
    if PdfReader is not None:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            texts = []
            for page in reader.pages:
                try:
                    texts.append(page.extract_text() or "")
                except Exception:
                    texts.append("")
            text = "\n".join(texts)
            if text.strip():
                return text
        except Exception:
            pass

    pdf_path = cache_path(url, "pdf")
    pdf_path.write_bytes(pdf_bytes)
    txt_path = cache_path(url, "pdftotext.txt")
    subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=True)
    return txt_path.read_text(encoding="utf-8", errors="ignore")


def strip_html(raw: str) -> str:
    raw = re.sub(r"<script.*?</script>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<style.*?</style>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return PAGE_TEXT_CLEANUP.sub(" ", raw).strip()


def score_link(url: str, text: str = "") -> int:
    val = url.lower() + " " + text.lower()
    score = 0
    if ".pdf" in val:
        score += 50
    if any(token in val for token in ["qap", "qualified allocation", "allocation plan", "rule text", "regulations", "regulation", "lihtc"]):
        score += 35
    if any(token in val for token in ["2026", "2025", "2027"]):
        score += 12
    if any(token in val for token in ["final", "adopted", "approved", "current", "effective"]):
        score += 10
    if any(token in val for token in ["summary", "faq", "notice", "calendar", "award", "allocations", "hearing", "comment", "scores", "score", "income-rent-limits", "rent-limits", "limits", "manual", "guide", "application", "schedule", "board", "packet", "memo", "presentation"]):
        score -= 35
    return score


def find_best_pdf_from_page(page_url: str, html_text: str) -> tuple[str | None, list[dict[str, Any]]]:
    candidates = []
    for href in re.findall(r'href=["\']([^"\']+)["\']', html_text, flags=re.I):
        abs_url = urljoin(page_url, html.unescape(href))
        if not abs_url.startswith("http"):
            continue
        s = score_link(abs_url)
        if s > 0:
            candidates.append({"url": abs_url, "score": s})
    dedup = {}
    for c in candidates:
        dedup[c["url"]] = max(c["score"], dedup.get(c["url"], 0))
    ranked = sorted(({"url": u, "score": s} for u, s in dedup.items()), key=lambda x: (-x["score"], x["url"]))
    return (ranked[0]["url"] if ranked else None, ranked[:10])


def resolve_document(state: str, config: dict[str, str]) -> dict[str, Any]:
    source_url = config["url"]
    source_kind = config["kind"]
    if source_kind == "pdf":
        text = pdf_text_from_url(source_url)
        return {
            "selected_url": source_url,
            "selected_kind": "pdf",
            "source_url": source_url,
            "source_kind": source_kind,
            "page_candidates": [],
            "text": text,
        }
    html_text = fetch(source_url, binary=False)
    best_pdf, candidates = find_best_pdf_from_page(source_url, html_text)
    preferred_pdf = PREFERRED_PAGE_PDFS.get(state)
    if preferred_pdf and any(candidate["url"] == preferred_pdf for candidate in candidates):
        best_pdf = preferred_pdf
    if best_pdf:
        try:
            text = pdf_text_from_url(best_pdf)
            return {
                "selected_url": best_pdf,
                "selected_kind": "pdf_from_page",
                "source_url": source_url,
                "source_kind": source_kind,
                "page_candidates": candidates,
                "text": text,
            }
        except Exception:
            pass
    return {
        "selected_url": source_url,
        "selected_kind": "html_page",
        "source_url": source_url,
        "source_kind": source_kind,
        "page_candidates": candidates,
        "text": strip_html(html_text),
    }


def pick_snippets(text: str, limit: int = 6, window: int = 180) -> list[str]:
    snippets = []
    for m in KEYWORD_PATTERN.finditer(text):
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        snippet = text[start:end].replace("\n", " ").strip()
        snippet = PAGE_TEXT_CLEANUP.sub(" ", snippet)
        if snippet not in snippets:
            snippets.append(snippet)
        if len(snippets) >= limit:
            break
    return snippets


def extract_title(text: str, fallback: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return fallback
    title = " ".join(lines[:3])[:250]
    title = PAGE_TEXT_CLEANUP.sub(" ", title).strip()
    return title or fallback


def guess_qap_year(text: str, selected_url: str) -> str | None:
    years = []
    for candidate in [selected_url, text[:6000]]:
        for m in YEAR_PATTERN.finditer(candidate):
            y1 = m.group(1)
            y2 = m.group(2)
            years.append(y1 if not y2 else f"{y1}-{y2}")
    return years[0] if years else None


def classify(text: str, snippets: list[str]) -> tuple[str, str]:
    lc = text.lower()
    has_5 = bool(re.search(r"5\s*%", lc))
    has_2 = bool(re.search(r"2\s*%", lc))
    accessible = "accessible" in lc or "accessibility" in lc
    mobility = "mobility" in lc
    hearing_visual = "hearing" in lc or "visual" in lc or "sensory" in lc
    type_a = bool(re.search(r"type\s*a", lc))
    ufas = "ufas" in lc or "section 504" in lc

    if re.search(r"20\s*%[^\.]{0,120}(type\s*a|accessible|adaptable)", lc):
        return "exceeds_504", "Detected 20% Type A/accessible requirement."
    if re.search(r"10\s*%[^\.]{0,120}(accessible|mobility|type\s*a)", lc) and not re.search(r"maximum|up to|bonus|points", lc):
        return "exceeds_504", "Detected 10% accessible/mobility threshold requirement."
    if (ufas or (has_5 and has_2)) and accessible and (mobility or hearing_visual or type_a):
        return "requires_504", "Detected Section 504/UFAS-style 5% and 2% accessibility language."
    if re.search(r"5\s*%[^\.]{0,120}(accessible|mobility|type\s*a)", lc) or re.search(r"2\s*%[^\.]{0,120}(hearing|visual|sensory)", lc):
        if has_5 and has_2 and (mobility or hearing_visual or accessible):
            return "requires_504", "Detected explicit 5% and 2% accessible-unit requirement."
        return "less_than_504", "Detected explicit accessibility requirement below full Section 504 floor."
    if re.search(r"points?[^\.]{0,160}(accessible|accessibility|type\s*a|special needs|universal design)", lc) or re.search(r"(accessible|accessibility|type\s*a)[^\.]{0,160}points?", lc):
        return "incentives_only", "Detected accessibility as scoring incentive rather than threshold."
    if re.search(r"(section 504|ada|fair housing)[^\.]{0,180}(comply|compliance|required)", lc):
        return "none", "Only general legal-compliance language detected."
    if snippets:
        return "manual_review", "Keyword hit(s) detected but auto-classifier could not confidently place the state."
    return "none", "No direct accessibility provision detected in extracted text."


def compare_to_baseline(current_detailed: str, baseline_detailed: str | None) -> str:
    if baseline_detailed is None:
        return "no_kelsey_baseline"
    if current_detailed == baseline_detailed:
        return "no_change"
    order = ["none", "incentives_only", "less_than_504", "requires_504", "exceeds_504"]
    if current_detailed in order and baseline_detailed in order:
        if order.index(current_detailed) > order.index(baseline_detailed):
            return "strengthened"
        return "weakened"
    return "changed"


def requested_shift(current_requested: str, baseline_detailed: str | None) -> str:
    if baseline_detailed is None:
        return "no_kelsey_baseline"
    baseline_requested = REQUESTED_CATEGORY_MAP[baseline_detailed]
    if current_requested == baseline_requested:
        return "no_change"
    order = ["none", "incentives_only", "requires_at_504", "exceeds_504"]
    if current_requested in order and baseline_requested in order:
        if order.index(current_requested) > order.index(baseline_requested):
            return "stronger_in_requested_taxonomy"
        return "weaker_in_requested_taxonomy"
    return "changed"


def derive_record_status(record: dict[str, Any]) -> str:
    if record.get("error"):
        return "error"
    if record.get("current_detailed_category") == "manual_review":
        return "manual_review"
    return "classified"


def apply_manual_override(state: str, result: dict[str, Any]) -> dict[str, Any]:
    override = MANUAL_OVERRIDES.get(state)
    if not override:
        result["record_status"] = derive_record_status(result)
        return result
    result.update(override)
    detailed = result["current_detailed_category"]
    requested = override.get("current_requested_category", REQUESTED_CATEGORY_MAP[detailed])
    result["current_detailed_label"] = CATEGORY_LABELS[detailed]
    result["current_requested_category"] = requested
    result["current_requested_label"] = REQUESTED_LABELS[requested]
    if result.get("current_requested_taxonomy_note") != "Extraction failed.":
        result["current_requested_taxonomy_note"] = REQUESTED_TAXONOMY_NOTE
    result["baseline_shift_detailed"] = compare_to_baseline(detailed, result["baseline_kelsey_2023_detailed_category"])
    result["baseline_shift_requested"] = requested_shift(requested, result["baseline_kelsey_2023_detailed_category"])
    result["record_status"] = derive_record_status(result)
    return result


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts_detailed = {}
    counts_requested = {}
    counts_requested_classified_only = {}
    counts_requested_none_breakdown = {"none": 0, "less_than_504": 0, "manual_review": 0}
    shifts = {}
    coverage = {"total_records": len(records), "non_error_records": 0, "classified": 0, "manual_review": 0, "error": 0}
    for rec in records:
        status = rec.get("record_status") or derive_record_status(rec)
        coverage[status] += 1
        if status == "error":
            continue
        coverage["non_error_records"] += 1
        counts_detailed[rec["current_detailed_category"]] = counts_detailed.get(rec["current_detailed_category"], 0) + 1
        counts_requested[rec["current_requested_category"]] = counts_requested.get(rec["current_requested_category"], 0) + 1
        if status == "classified":
            counts_requested_classified_only[rec["current_requested_category"]] = counts_requested_classified_only.get(rec["current_requested_category"], 0) + 1
        if rec["current_requested_category"] == "none":
            detailed = rec["current_detailed_category"]
            if detailed in counts_requested_none_breakdown:
                counts_requested_none_breakdown[detailed] += 1
        shifts[rec["baseline_shift_detailed"]] = shifts.get(rec["baseline_shift_detailed"], 0) + 1
    return {
        "coverage": coverage,
        "counts_detailed": counts_detailed,
        "counts_requested": counts_requested,
        "counts_requested_note": "Tallied across non-error records. In the requested four-way taxonomy, 'none' includes detailed 'none', detailed 'less_than_504', and provisional 'manual_review' records.",
        "counts_requested_classified_only": counts_requested_classified_only,
        "counts_requested_none_breakdown": counts_requested_none_breakdown,
        "baseline_shift_detailed": shifts,
    }


def record_for_state(state: str) -> dict[str, Any]:
    config = STATE_DOCS[state]
    baseline_detailed = BASELINE.get(state)
    try:
        resolved = resolve_document(state, config)
        text = resolved["text"]
        snippets = pick_snippets(text)
        detailed, auto_reason = classify(text, snippets)
        title = extract_title(text, f"{STATE_NAMES[state]} QAP")
        qap_year = guess_qap_year(text, resolved["selected_url"])
        result = {
            "state": state,
            "state_name": STATE_NAMES[state],
            "source_lookup_url": config["url"],
            "selected_document_url": resolved["selected_url"],
            "selected_document_kind": resolved["selected_kind"],
            "document_title_guess": title,
            "document_year_guess": qap_year,
            "page_pdf_candidates": resolved["page_candidates"],
            "baseline_kelsey_2023_detailed_category": baseline_detailed,
            "baseline_kelsey_2023_detailed_label": CATEGORY_LABELS.get(baseline_detailed) if baseline_detailed else None,
            "current_detailed_category": detailed,
            "current_detailed_label": CATEGORY_LABELS[detailed],
            "current_requested_category": REQUESTED_CATEGORY_MAP[detailed],
            "current_requested_label": REQUESTED_LABELS[REQUESTED_CATEGORY_MAP[detailed]],
            "current_requested_taxonomy_note": REQUESTED_TAXONOMY_NOTE,
            "auto_classification_reason": auto_reason,
            "keyword_snippets": snippets,
            "baseline_shift_detailed": compare_to_baseline(detailed, baseline_detailed),
            "baseline_shift_requested": requested_shift(REQUESTED_CATEGORY_MAP[detailed], baseline_detailed),
            "document_status_note": "Current public 2025-2026-era document used; some states publish 2026 drafts or 2025-2026 combined plans rather than a single final 2026 QAP.",
            "manual_notes": None,
            "error": None,
            "record_status": None,
        }
        return apply_manual_override(state, result)
    except Exception as exc:
        return {
            "state": state,
            "state_name": STATE_NAMES[state],
            "source_lookup_url": config["url"],
            "selected_document_url": None,
            "selected_document_kind": None,
            "document_title_guess": None,
            "document_year_guess": None,
            "page_pdf_candidates": [],
            "baseline_kelsey_2023_detailed_category": baseline_detailed,
            "baseline_kelsey_2023_detailed_label": CATEGORY_LABELS.get(baseline_detailed) if baseline_detailed else None,
            "current_detailed_category": "manual_review",
            "current_detailed_label": CATEGORY_LABELS["manual_review"],
            "current_requested_category": "none",
            "current_requested_label": REQUESTED_LABELS["none"],
            "current_requested_taxonomy_note": "Extraction failed.",
            "auto_classification_reason": "Extraction failed.",
            "keyword_snippets": [],
            "baseline_shift_detailed": compare_to_baseline("manual_review", baseline_detailed),
            "baseline_shift_requested": requested_shift("none", baseline_detailed),
            "document_status_note": None,
            "manual_notes": None,
            "error": repr(exc),
            "record_status": "error",
        }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    records = payload["records"]
    lines = []
    lines.append("# QAP accessibility update: 2025-2026 scan")
    lines.append("")
    lines.append(f"Generated: {payload['generated_at_utc']}")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Baseline: Kelsey 2023 five-way taxonomy reconstructed in the existing LIHTC accessibility audit (exceeds 504 / requires 504 / less than 504 / incentives / none).")
    lines.append("- Current scan: latest public 2025-2026-era QAP, allocation plan, regulations, or directly linked state page located for each state plus DC.")
    lines.append("- Requested four-way taxonomy reported here: exceeds 504 / requires 504 / incentives only / none.")
    lines.append("- To preserve fidelity, the JSON also retains a five-way detailed field and flags sub-504 direct requirements separately.")
    lines.append("- Coding rule: only direct QAP/allocation-plan/regulation language counted. Generic references to independent legal obligations (ADA, Fair Housing Act, Section 504 where otherwise applicable) were not treated as standalone QAP accessibility requirements.")
    lines.append("- Caveat: some jurisdictions had 2026 drafts or amendments rather than a single final 2026 plan; those documents were still captured because the task asked for a 2025-2026 update.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Total records: {summary['coverage']['total_records']}")
    lines.append(f"- Non-error records with usable source text: {summary['coverage']['non_error_records']}")
    lines.append(f"- Classified without manual review: {summary['coverage']['classified']}")
    lines.append(f"- Manual-review/provisional records: {summary['coverage']['manual_review']}")
    lines.append(f"- Extraction errors: {summary['coverage']['error']}")
    lines.append("")
    lines.append("## Requested four-way counts")
    lines.append("")
    lines.append(f"- Across all non-error records ({summary['coverage']['non_error_records']}):")
    for key in ["exceeds_504", "requires_at_504", "incentives_only", "none"]:
        lines.append(f"  - {REQUESTED_LABELS[key]}: {summary['counts_requested'].get(key, 0)}")
    none_breakdown = summary["counts_requested_none_breakdown"]
    lines.append(
        "- Requested-category 'None' breakdown: "
        f"{none_breakdown['none']} detailed none + {none_breakdown['less_than_504']} detailed less_than_504 + {none_breakdown['manual_review']} manual_review/provisional."
    )
    lines.append(f"- Across classified records only ({summary['coverage']['classified']}; excludes manual_review and errors):")
    for key in ["exceeds_504", "requires_at_504", "incentives_only", "none"]:
        lines.append(f"  - {REQUESTED_LABELS[key]}: {summary['counts_requested_classified_only'].get(key, 0)}")
    lines.append("")
    lines.append("## Five-way detailed counts")
    lines.append("")
    lines.append(f"- Tallied across non-error records ({summary['coverage']['non_error_records']}).")
    for key in ["exceeds_504", "requires_504", "less_than_504", "incentives_only", "none", "manual_review"]:
        lines.append(f"  - {CATEGORY_LABELS[key]}: {summary['counts_detailed'].get(key, 0)}")
    lines.append("")
    lines.append("## Change from Kelsey 2023 baseline (detailed five-way)")
    lines.append("")
    for key in ["no_change", "strengthened", "weakened", "changed", "no_kelsey_baseline"]:
        if key in summary["baseline_shift_detailed"]:
            lines.append(f"- {key}: {summary['baseline_shift_detailed'][key]}")
    lines.append("")
    lines.append("## State-by-state table")
    lines.append("")
    lines.append("| State | Current requested category | Current detailed category | Kelsey 2023 baseline | Shift | QAP year guess | Notes |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for rec in records:
        note = rec.get("manual_notes") or rec.get("auto_classification_reason") or ""
        note = note.replace("|", "/")[:120]
        lines.append(
            f"| {rec['state']} | {rec['current_requested_label']} | {rec['current_detailed_label']} | {rec['baseline_kelsey_2023_detailed_label'] or 'N/A'} | {rec['baseline_shift_detailed']} | {rec.get('document_year_guess') or ''} | {note} |"
        )
    lines.append("")
    lines.append("## Main observations")
    lines.append("")
    lines.append("- The requested four-way taxonomy can understate states with sub-504 direct requirements and can also hide provisional records, because both `less_than_504` and `manual_review` map to requested-category `none`.")
    lines.append("- The strongest evidence generally appears in states whose QAPs explicitly specify accessibility percentages, Type A/UFAS standards, or scoring incentives for additional accessible units.")
    lines.append("- States coded `manual_review` or records with extraction errors should be manually checked before making any claim of a definitive downgrade or upgrade.")
    vt_record = next((rec for rec in records if rec["state"] == "VT"), None)
    if vt_record is not None:
        lines.append(f"- Vermont stale-source fix: this refresh uses {vt_record.get('selected_document_url') or vt_record['source_lookup_url']} and codes Vermont as {vt_record['current_detailed_label']} / requested = {vt_record['current_requested_label']}, rather than relying on the archived 2020-2021 QAP.")
    lines.append("")
    lines.append("## Evidence snippets")
    lines.append("")
    for rec in records:
        lines.append(f"### {rec['state']} — {rec['state_name']}")
        lines.append(f"- Source: {rec.get('selected_document_url') or rec['source_lookup_url']}")
        lines.append(f"- Coding: {rec['current_detailed_label']} / requested = {rec['current_requested_label']}")
        if rec.get("error"):
            lines.append(f"- Error: {rec['error']}")
        else:
            if rec.get("keyword_snippets"):
                for snip in rec["keyword_snippets"][:3]:
                    lines.append(f"- Snippet: {snip[:500]}")
            else:
                lines.append("- No keyword snippet extracted.")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    records = [record_for_state(state) for state in sorted(STATE_DOCS)]
    summary = summarize(records)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "methodology": {
            "baseline_source": "Kelsey 2023 taxonomy as reconstructed in scripts/lihtc_accessibility_audit.py and results/lihtc_accessibility_audit_results.json",
            "current_source_rule": "Latest public 2025-2026-era QAP/allocation-plan/regulation page located for each jurisdiction; direct QAP text counted, adjacent state-law background excluded where possible.",
            "requested_taxonomy": REQUESTED_LABELS,
            "detailed_taxonomy": CATEGORY_LABELS,
            "requested_taxonomy_collapse_note": REQUESTED_TAXONOMY_NOTE,
        },
        "summary": summary,
        "records": records,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
