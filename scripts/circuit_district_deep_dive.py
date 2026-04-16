#!/usr/bin/env python3
"""
District / judge-level extension of the circuit pleading-gate analysis.

This script reuses the same disability-case universe and period definitions as
scripts/extended_doctrinal_analysis.py, then adds a district-court deep dive for
the five circuits with the steepest P1 -> P3 broad-win decline.

Outputs:
- results/circuit_district_deep_dive_results.json
- results/circuit_district_deep_dive_analysis.md
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

from config import RESULTS_DIR, UNIFIED_DB_PATH

TOP_CIRCUITS_N = 5
APPOINTMENT_CUTOFF = dt.date(2025, 1, 31)
HIGH_IMPACT_FULL_SHORTFALL_SHARE = 0.05
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKI_USER_AGENT = "Mozilla/5.0 (district-deep-dive research script)"
WIKI_SLEEP_SECONDS = 0.25

DISTRICT_MAP = {
    # 2d Cir.
    "S.D.N.Y.": "S.D.N.Y.",
    "E.D.N.Y.": "E.D.N.Y.",
    "N.D.N.Y.": "N.D.N.Y.",
    "W.D.N.Y.": "W.D.N.Y.",
    "D. Conn.": "D. Conn.",
    "D. Vt.": "D. Vt.",
    # 4th Cir.
    "D. Md.": "D. Md.",
    "E.D.N.C.": "E.D.N.C.",
    "D.S.C.": "D.S.C.",
    "M.D.N.C.": "M.D.N.C.",
    "W.D. Va.": "W.D. Va.",
    "E.D. Va.": "E.D. Va.",
    "S.D.W.Va.": "S.D.W. Va.",
    "S.D.W.V.": "S.D.W. Va.",
    "N.D. W. Va.": "N.D.W. Va.",
    "W.D.N.C.": "W.D.N.C.",
    # 10th Cir.
    "D. Kan.": "D. Kan.",
    "D. Utah": "D. Utah",
    "D. Utah, Central Division": "D. Utah",
    "E.D. Okla.": "E.D. Okla.",
    "D.N.M.": "D.N.M.",
    "D. Colo.": "D. Colo.",
    "W.D. Okla.": "W.D. Okla.",
    "N.D. Okla.": "N.D. Okla.",
    # 5th Cir.
    "N.D. Tex.": "N.D. Tex.",
    "E.D. La.": "E.D. La.",
    "W.D. Tex.": "W.D. Tex.",
    "E.D. Tex.": "E.D. Tex.",
    "S.D. Tex.": "S.D. Tex.",
    "S.D. Miss.": "S.D. Miss.",
    "M.D. La.": "M.D. La.",
    "W.D. La.": "W.D. La.",
    "N.D. Miss.": "N.D. Miss.",
    # 3d Cir.
    "E.D. Pa.": "E.D. Pa.",
    "D.N.J.": "D.N.J.",
    "D. Del.": "D. Del.",
    "M.D. Pa.": "M.D. Pa.",
    "W.D. Pa.": "W.D. Pa.",
    "D.V.I.": "D.V.I.",
}

FILE_SUFFIX_TO_DISTRICT = {
    "nysd": "S.D.N.Y.",
    "nyed": "E.D.N.Y.",
    "nynd": "N.D.N.Y.",
    "nywd": "W.D.N.Y.",
    "ctd": "D. Conn.",
    "vtd": "D. Vt.",
    "mdd": "D. Md.",
    "nced": "E.D.N.C.",
    "scd": "D.S.C.",
    "ncmd": "M.D.N.C.",
    "vawd": "W.D. Va.",
    "vaed": "E.D. Va.",
    "wvsd": "S.D.W. Va.",
    "wvnd": "N.D.W. Va.",
    "ncwd": "W.D.N.C.",
    "ksd": "D. Kan.",
    "utd": "D. Utah",
    "oked": "E.D. Okla.",
    "nmd": "D.N.M.",
    "cod": "D. Colo.",
    "okwd": "W.D. Okla.",
    "oknd": "N.D. Okla.",
    "txnd": "N.D. Tex.",
    "laed": "E.D. La.",
    "txwd": "W.D. Tex.",
    "txed": "E.D. Tex.",
    "txsd": "S.D. Tex.",
    "mssd": "S.D. Miss.",
    "lamd": "M.D. La.",
    "lawd": "W.D. La.",
    "msnd": "N.D. Miss.",
    "paed": "E.D. Pa.",
    "njd": "D.N.J.",
    "ded": "D. Del.",
    "pamd": "M.D. Pa.",
    "pawd": "W.D. Pa.",
    "vid": "D.V.I.",
}

DISTRICT_NAME_PATTERNS = {
    "S.D.N.Y.": ("southern district of new york",),
    "E.D.N.Y.": ("eastern district of new york",),
    "N.D.N.Y.": ("northern district of new york",),
    "W.D.N.Y.": ("western district of new york",),
    "D. Conn.": ("district of connecticut",),
    "D. Vt.": ("district of vermont",),
    "D. Md.": ("district of maryland",),
    "E.D.N.C.": ("eastern district of north carolina",),
    "D.S.C.": ("district of south carolina",),
    "M.D.N.C.": ("middle district of north carolina",),
    "W.D. Va.": ("western district of virginia",),
    "E.D. Va.": ("eastern district of virginia",),
    "S.D.W. Va.": ("southern district of west virginia",),
    "N.D.W. Va.": ("northern district of west virginia",),
    "W.D.N.C.": ("western district of north carolina",),
    "D. Kan.": ("district of kansas",),
    "D. Utah": ("district of utah",),
    "E.D. Okla.": ("eastern district of oklahoma",),
    "D.N.M.": ("district of new mexico",),
    "D. Colo.": ("district of colorado",),
    "W.D. Okla.": ("western district of oklahoma",),
    "N.D. Okla.": ("northern district of oklahoma",),
    "N.D. Tex.": ("northern district of texas",),
    "E.D. La.": ("eastern district of louisiana",),
    "W.D. Tex.": ("western district of texas",),
    "E.D. Tex.": ("eastern district of texas",),
    "S.D. Tex.": ("southern district of texas",),
    "S.D. Miss.": ("southern district of mississippi",),
    "M.D. La.": ("middle district of louisiana",),
    "W.D. La.": ("western district of louisiana",),
    "N.D. Miss.": ("northern district of mississippi",),
    "E.D. Pa.": ("eastern district of pennsylvania",),
    "D.N.J.": ("district of new jersey",),
    "D. Del.": ("district of delaware",),
    "M.D. Pa.": ("middle district of pennsylvania",),
    "W.D. Pa.": ("western district of pennsylvania",),
    "D.V.I.": ("district of the virgin islands", "district court of the virgin islands"),
}

BAD_JUDGE_WORDS = {
    "court", "district", "united", "states", "plaintiff", "plaintiffs", "defendant",
    "defendants", "order", "reasons", "memorandum", "opinion", "recommendation",
    "report", "findings", "conclusions", "action", "civil", "case", "section",
    "docket", "motion", "filed", "judge", "magistrate", "summary", "judgment",
    "matter", "matters", "accepted", "date", "foregoing", "introduction",
    "recommendationof", "therefore", "service", "addresses", "address", "attorney",
    "attorneys", "counsel", "llp", "llc", "firm", "radler", "rivkin",
}
ALLOWED_LOWER_NAME_TOKENS = {"la", "le", "van", "von", "jr", "sr", "ii", "iii", "iv", "v"}
SUFFIX_TOKEN_MAP = {
    "jr": "Jr.",
    "sr": "Sr.",
    "ii": "II",
    "iii": "III",
    "iv": "IV",
    "v": "V",
}
MANUAL_REJECT_JUDGES = {
    "Solve",
    "Sef",
    "BRANTLE Bi",
    "s/",
    "New York New York",
    "Brooklyn New York",
    "Dated: Brooklyn New York",
    "Robery Kirscu Wa",
    "Ajmel A. Quereshi",
    "Ary Kay Lanthier",
    "Florence South Carolina",
    "Greg Wr Bel Woods",
    "It Is So Ordered",
    "Ze B. At",
    "On} Charles Eskridg",
}

MANUAL_CANONICAL_JUDGES = {
    "Hon Brenda K. Sannes": "Brenda K. Sannes",
    "Hon Anne M. Nardacci": "Anne M. Nardacci",
    "Sarala v Nagala": "Sarala V. Nagala",
    "Sarala V Nagala": "Sarala V. Nagala",
    "George C. Hanks jr": "George C. Hanks Jr.",
    "Hal R. Ray jr": "Hal R. Ray Jr.",
    "Joseph F. Leeson jr": "Joseph F. Leeson Jr.",
    "Gregoryb.Williams": "Gregory B. Williams",
    "GREGORYB.WILLIAMS": "Gregory B. Williams",
    "D. Biery": "Fred Biery",
    "Wigenton": "Susan D. Wigenton",
    "Susan D. Wigenton X": "Susan D. Wigenton",
    "Susan D. Wigenton X.": "Susan D. Wigenton",
    "Salas": "Esther Salas",
    "Quraishi": "Zahid N. Quraishi",
    "Gene E.K Pratter": "Gene E. K. Pratter",
    "Gene E.K. Pratter": "Gene E. K. Pratter",
    "Gene E.k Pratter": "Gene E. K. Pratter",
    "Gene E.k. Pratter": "Gene E. K. Pratter",
    "DeboralrL Boardman": "Deborah L. Boardman",
    "Dated Matthew J. Maddox": "Matthew J. Maddox",
    "Carl J. Barbierv": "Carl J. Barbier",
    "Charles Eskrid": "Charles Eskridge",
    "Lo Eskridge": "Charles Eskridge",
    "Michael EB Farbiarz": "Michael E. Farbiarz",
    "Michael Eb Farbiarz": "Michael E. Farbiarz",
    "Albany New York Anne M. Nardacci": "Anne M. Nardacci",
    "Albany New York Christian F. Hummel": "Christian F. Hummel",
    "Andrew L. Carter jr": "Andrew L. Carter Jr.",
    "George L. Russell iii": "George L. Russell III",
    "Harvey Bartle iii": "Harvey Bartle III",
    "JUDITH C. McCARTHY": "Judith C. McCarthy",
    "Joseph Dawson iii": "Joseph Dawson III",
    "KAYLA DYE McCLUSKY": "Kayla Dye McClusky",
    "Lashann Dearcy Hall": "LaShann DeArcy Hall",
    "LaSHANN DeARCY HALL": "LaShann DeArcy Hall",
    "Louis Guirola jr": "Louis Guirola Jr.",
    "Mae A. D' Agostino”": "Mae A. D'Agostino",
    "Mae A. D‘ Agostino”": "Mae A. D'Agostino",
    "Peter Bea": "Peter Bray",
    "Ramón E. Reyes jr": "Ramón E. Reyes Jr.",
    "Richard E. Myers ii": "Richard E. Myers II",
    "Richard L. Bou S. jr": "Richard L. Bourgeois Jr.",
    "Richard L. Bou S. Jr.": "Richard L. Bourgeois Jr.",
    "Robert B. Jones jr": "Robert B. Jones Jr.",
    "Thomas E. Rogers iii": "Thomas E. Rogers III",
    "William K. Sessions iii": "William K. Sessions III",
    "John Fy Heil iii": "John F. Heil III",
    "JOHN F. HEI Il": "John F. Heil III",
    "John F. Hei Il": "John F. Heil III",
    "George Castner": "Georgette Castner",
    "Barba B. Kadota": "Charles B. Goodwin",
    "Barbs B. Kadota": "Charles B. Goodwin",
    "Denise Cote": "Denise L. Cote",
    "Lape": "David L. Horan",
}

MANUAL_APPOINTMENT_LOOKUPS = {
    "Esther Salas": {
        "status": "resolved",
        "page_title": "Esther Salas",
        "appointment_date": "2011-06-14",
        "office": "Judge of the United States District Court for the District of New Jersey",
        "term_start_raw": "June 14, 2011",
        "lookup_method": "manual_seed",
        "source_url": "https://en.wikipedia.org/wiki/Esther_Salas",
    },
    "Gene E. K. Pratter": {
        "status": "resolved",
        "page_title": "Gene E. K. Pratter",
        "appointment_date": "2004-06-16",
        "office": "Judge of the United States District Court for the Eastern District of Pennsylvania",
        "term_start_raw": "June 16, 2004",
        "lookup_method": "manual_seed",
        "source_url": "https://en.wikipedia.org/wiki/Gene_E._K._Pratter",
    },
    "Gerald J. Pappert": {
        "status": "resolved",
        "page_title": "Jerry Pappert",
        "appointment_date": "2014-12-04",
        "office": "Judge of the United States District Court for the Eastern District of Pennsylvania",
        "term_start_raw": "December 4, 2014",
        "lookup_method": "manual_seed",
        "source_url": "https://en.wikipedia.org/wiki/Gerald_J._Pappert",
    },
    "Gerald L. Jackson": {
        "status": "resolved",
        "page_title": None,
        "appointment_date": "2022-08-01",
        "office": "United States Magistrate Judge, Eastern District of Oklahoma",
        "term_start_raw": "August 1, 2022",
        "lookup_method": "manual_seed",
        "source_url": "https://www.oked.uscourts.gov/sites/oked/files/GLJ%20-%20Press%20Release%20Final.pdf",
    },
    "Hal R. Ray Jr.": {
        "status": "resolved",
        "page_title": "Hal R. Ray Jr.",
        "appointment_date": "2016-06-24",
        "office": "United States Magistrate Judge, Northern District of Texas",
        "term_start_raw": "June 24, 2016",
        "lookup_method": "manual_seed",
        "source_url": "https://ballotpedia.org/Hal_Ray",
    },
    "Holly L. Teeter": {
        "status": "resolved",
        "page_title": "Holly L. Teeter",
        "appointment_date": "2018-08-01",
        "office": "Judge of the United States District Court for the District of Kansas",
        "term_start_raw": "August 1, 2018",
        "lookup_method": "manual_seed",
        "source_url": "https://www.ksd.uscourts.gov/content/district-judge-holly-l-teeter",
    },
    "J. Mark Coulson": {
        "status": "resolved",
        "page_title": None,
        "appointment_date": "2014-08-01",
        "office": "United States Magistrate Judge, District of Maryland",
        "term_start_raw": "August 1, 2014",
        "lookup_method": "manual_seed",
        "source_url": "https://www.mdd.uscourts.gov/news/appointment-j-mark-coulson-us-magistrate-judge-2014-06-19t000000",
    },
    "Katharine H. Parker": {
        "status": "resolved",
        "page_title": "Katharine Parker",
        "appointment_date": "2016-11-04",
        "office": "United States Magistrate Judge, Southern District of New York",
        "term_start_raw": "November 4, 2016",
        "lookup_method": "manual_seed",
        "source_url": "https://ballotpedia.org/Katharine_Parker",
    },
    "Leslie G. Foschio": {
        "status": "resolved",
        "page_title": None,
        "appointment_date": "1991-02-01",
        "office": "United States Magistrate Judge, Western District of New York",
        "term_start_raw": "February 1, 1991",
        "lookup_method": "manual_seed",
        "source_url": "https://www.courtlistener.com/person/9454/leslie-g-foschio/",
    },
    "Ona T. Wang": {
        "status": "resolved",
        "page_title": "Ona Wang",
        "appointment_date": "2018-03-05",
        "office": "United States Magistrate Judge, Southern District of New York",
        "term_start_raw": "March 5, 2018",
        "lookup_method": "manual_seed",
        "source_url": "https://ballotpedia.org/Ona_Wang",
    },
    "Robert Pitman": {
        "status": "resolved",
        "page_title": "Robert Pitman",
        "appointment_date": "2014-12-19",
        "office": "Judge of the United States District Court for the Western District of Texas",
        "term_start_raw": "December 19, 2014",
        "lookup_method": "manual_seed",
        "source_url": "https://ballotpedia.org/Robert_Pitman",
    },
    "Steven I. Locke": {
        "status": "resolved",
        "page_title": None,
        "appointment_date": "2014-08-01",
        "office": "United States Magistrate Judge, Eastern District of New York",
        "term_start_raw": "August 1, 2014",
        "lookup_method": "manual_seed",
        "source_url": "https://www.nyed.uscourts.gov/magistrate-judge-steven-i-locke",
    },
    "Stewart D. Aaron": {
        "status": "resolved",
        "page_title": "Stewart D. Aaron",
        "appointment_date": "2017-12-01",
        "office": "United States Magistrate Judge, Southern District of New York",
        "term_start_raw": "December 1, 2017",
        "lookup_method": "manual_seed",
        "source_url": "https://www.uscourts.gov/about-federal-courts/about-federal-judges/judicial-milestones/stewart-d-aaron",
    },
    "Susan D. Wigenton": {
        "status": "resolved",
        "page_title": "Susan D. Wigenton",
        "appointment_date": "2006-06-12",
        "office": "Judge of the United States District Court for the District of New Jersey",
        "term_start_raw": "June 12, 2006",
        "lookup_method": "manual_seed",
        "source_url": "https://en.wikipedia.org/wiki/Susan_D._Wigenton",
    },
    "Susan Hightower": {
        "status": "resolved",
        "page_title": None,
        "appointment_date": "2019-07-01",
        "office": "United States Magistrate Judge, Western District of Texas",
        "term_start_raw": "July 1, 2019",
        "lookup_method": "manual_seed",
        "source_url": "https://ballotpedia.org/Susan_Hightower_(Texas)",
    },
    "Zahid N. Quraishi": {
        "status": "resolved",
        "page_title": "Zahid Quraishi",
        "appointment_date": "2021-06-22",
        "office": "Judge of the United States District Court for the District of New Jersey",
        "term_start_raw": "June 22, 2021",
        "lookup_method": "manual_seed",
        "source_url": "https://en.wikipedia.org/wiki/Zahid_Quraishi",
    },
}

JUDGE_SAME_LINE_PATTERNS = [
    re.compile(
        r"^(?P<name>[A-Za-z][A-Za-z .\-\'’]+?(?:,?\s(?:Jr\.|Sr\.|II|III|IV))?),\s*"
        r"(?:Chief\s+)?(?:Senior\s+)?(?:(?:United States|U\.S\.)\s+)?District Judge[:.]?$",
        re.I,
    ),
    re.compile(
        r"^(?P<name>[A-Za-z][A-Za-z .\-\'’]+?(?:,?\s(?:Jr\.|Sr\.|II|III|IV))?),\s*"
        r"(?:Chief\s+)?(?:Senior\s+)?(?:(?:United States|U\.S\.)\s+)?Magistrate Judge[:.]?$",
        re.I,
    ),
    re.compile(r"^(?P<name>[A-Za-z][A-Za-z .\-\'’]+?),\s*(?:U\.S\.)?D\.J\.?[:]?$", re.I),
    re.compile(r"^(?P<name>[A-Za-z][A-Za-z .\-\'’]+?),\s*(?:U\.S\.)?M\.J\.?[:]?$", re.I),
    re.compile(r"^/s/\s*(?P<name>[A-Za-z][A-Za-z .\-\'’]+?)_*$"),
    re.compile(r"^To:?\s+the\s+Honorable\s+(?:United States\s+)?District Judge\s+(?P<name>[A-Za-z][A-Za-z .\-\'’]+?)[:.]?$", re.I),
]

JUDGE_TITLE_LINE_PATTERN = re.compile(
    r"^(?:Chief\s+)?(?:Senior\s+)?(?:(?:United States|U\.S\.)\s+)?District Judge[:.]?$"
    r"|^(?:(?:United States|U\.S\.)\s+)?Magistrate Judge[:.]?$"
    r"|^(?:U\.S\.)?D\.J\.?[:]?$"
    r"|^(?:U\.S\.)?M\.J\.?[:]?$",
    re.I,
)


_TEXT_CACHE: Dict[str, str] = {}


def workspace_root() -> Path:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    explicit = os.environ.get("FHA_WORKSPACE_ROOT")
    if explicit:
        return Path(explicit).resolve()
    return repo_root.parent


def raw_text_dir() -> Path:
    candidates = [
        workspace_root() / "allFHAcases",
        workspace_root() / "fhaCases",
        Path(UNIFIED_DB_PATH).resolve().parent / "cases",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def load_database() -> List[dict]:
    with open(UNIFIED_DB_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def is_disability(case: dict) -> bool:
    return (
        case.get("primary_protected_class") == "disability"
        or "disability" in (case.get("protected_classes") or [])
    ) and case.get("screening_result") == "YES"


def period_of(year: Optional[int]) -> Optional[str]:
    if year is None:
        return None
    if year <= 2020:
        return "P1"
    if year <= 2022:
        return "P2"
    return "P3"


def broad_win(case: dict) -> bool:
    return case.get("outcome") in ("PLAINTIFF_WIN", "MIXED")


def def_win(case: dict) -> bool:
    return case.get("outcome") == "DEFENDANT_WIN"


def is_mtd(case: dict) -> bool:
    return (case.get("procedural_posture") or "").upper() == "MOTION_TO_DISMISS"


def is_pro_se(case: dict) -> bool:
    return case.get("pro_se") is True


def pct(num: float, denom: float) -> Optional[float]:
    if not denom:
        return None
    return 100.0 * num / denom


def round_or_none(value: Optional[float], digits: int = 2) -> Optional[float]:
    return round(value, digits) if value is not None else None


def share_or_none(num: float, denom: float) -> Optional[float]:
    if not denom:
        return None
    return num / denom


def conservative_single_judge_test(top_observed_shortfall: float, unresolved_shortfall: float, denominator: float) -> dict:
    observed_share = share_or_none(top_observed_shortfall, denominator)
    unresolved_share = share_or_none(unresolved_shortfall, denominator)
    max_possible_share = share_or_none(top_observed_shortfall + max(unresolved_shortfall, 0.0), denominator)
    if observed_share is None or max_possible_share is None:
        status = "not_applicable"
    elif observed_share > 0.5:
        status = "definitive_yes"
    elif max_possible_share <= 0.5:
        status = "definitive_no"
    else:
        status = "indeterminate"
    return {
        "observed_share": round_or_none(observed_share, 4),
        "unresolved_share": round_or_none(unresolved_share, 4),
        "max_possible_share": round_or_none(max_possible_share, 4),
        "status": status,
    }


def fmt_pct(value: Optional[float], digits: int = 2) -> str:
    return f"{value:.{digits}f}%" if value is not None else "NA"


def fmt_share(value: Optional[float], digits: int = 1) -> str:
    return f"{100.0 * value:.{digits}f}%" if value is not None else "NA"


def district_from_case(case: dict) -> Optional[str]:
    return DISTRICT_MAP.get((case.get("court") or "").strip())


def district_from_filename(path: Path) -> Optional[str]:
    match = re.search(r"_([a-z]{3,4}d)$", path.stem.lower())
    if not match:
        return None
    return FILE_SUFFIX_TO_DISTRICT.get(match.group(1))


def read_text(path: Path) -> str:
    key = str(path)
    if key not in _TEXT_CACHE:
        _TEXT_CACHE[key] = path.read_text(encoding="utf-8", errors="ignore")
    return _TEXT_CACHE[key]


def build_raw_text_index() -> Dict[str, Path]:
    root = raw_text_dir()
    index: Dict[str, Path] = {}
    if not root.exists():
        return index
    for path in root.rglob("*.txt"):
        stem = path.stem.lower()
        current = index.get(stem)
        if current is None or (len(path.parts), len(str(path))) < (len(current.parts), len(str(current))):
            index[stem] = path
    return index


def normalize_candidate_name(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    text = raw.replace("’", "'").replace("`", "")
    text = re.sub(r"^/s/\s*", "", text)
    text = re.sub(r"^(?:To:\s*)?(?:the\s+)?honorable\s+", "", text, flags=re.I)
    text = re.sub(r"^Date\s+", "", text)
    text = text.replace("Hon. ", "").replace("Hon ", "")
    text = " ".join(text.strip().strip("_").strip().split())
    text = text.strip(" ,:;.-_")
    if not text or len(text) > 40:
        return None

    def smart_title_case(token: str) -> str:
        pieces = re.split(r"([-'])", token.lower())
        rebuilt = "".join(piece.capitalize() if piece not in {"-", "'"} else piece for piece in pieces)
        rebuilt = re.sub(r"\bMc([a-z])", lambda match: f"Mc{match.group(1).upper()}", rebuilt)
        rebuilt = re.sub(r"\bMac([a-z])", lambda match: f"Mac{match.group(1).upper()}", rebuilt)
        return rebuilt

    tokens = [tok.strip(".,()[]") for tok in text.split() if tok.strip(".,()[]")]
    if not tokens or len(tokens) > 6:
        return None

    cleaned: List[str] = []
    upperish = 0
    for token in tokens:
        if any(ch.isdigit() for ch in token):
            return None
        low = token.lower()
        if low in BAD_JUDGE_WORDS:
            return None
        if low in SUFFIX_TOKEN_MAP:
            cleaned.append(SUFFIX_TOKEN_MAP[low])
            continue
        if low in ALLOWED_LOWER_NAME_TOKENS:
            cleaned.append(low)
            continue
        if re.fullmatch(r"[A-Z]\.?,?", token):
            cleaned.append(token[0].upper() + ".")
            upperish += 1
            continue
        if token.isupper() or token.islower() or (len(token) > 2 and any(ch.islower() for ch in token) and sum(ch.isupper() for ch in token[1:]) >= 2):
            token = smart_title_case(token)
        if token and token[0].isupper():
            cleaned.append(token)
            upperish += 1
            continue
        return None

    if upperish == 0:
        return None
    if len(cleaned) == 1 and len(cleaned[0]) < 3:
        return None
    return " ".join(cleaned)


def judge_candidate_quality(name: str) -> Tuple[int, int, int]:
    tokens = name.split()
    substantive = [tok for tok in tokens if tok.lower().rstrip(".") not in ALLOWED_LOWER_NAME_TOKENS]
    token_letters = [re.sub(r"[^A-Za-z]", "", tok) for tok in tokens]
    return (
        1 if is_full_name(name) else 0,
        sum(1 for token in substantive if len(token) > 1),
        sum(len(token) for token in token_letters),
    )


def extract_explicit_judge(text: str) -> Optional[str]:
    lines = [re.sub(r"\s+", " ", line.strip()) for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    candidates: List[str] = []

    def add_candidate(raw_name: Optional[str]) -> None:
        name = normalize_candidate_name(raw_name)
        if name:
            candidates.append(name)

    for line in lines[:120] + lines[-80:]:
        for pattern in JUDGE_SAME_LINE_PATTERNS:
            match = pattern.match(line)
            if match:
                add_candidate(match.group("name"))

    for seq in (lines[:120], lines[-80:]):
        for left, right in zip(seq, seq[1:]):
            if JUDGE_TITLE_LINE_PATTERN.match(right):
                add_candidate(left)
            if JUDGE_TITLE_LINE_PATTERN.match(left):
                add_candidate(right)

    if not candidates:
        return None
    return max(enumerate(candidates), key=lambda row: (judge_candidate_quality(row[1]), row[0]))[1]


def extract_docket_initials(text: str) -> Optional[str]:
    head = "\n".join(text.splitlines()[:60])
    patterns = [
        re.compile(r"\((?P<judge>[A-Z]{2,4})(?:/[A-Z]{2,4})?\)"),
        re.compile(r"No\.\s*[0-9:A-Za-z\-]+-(?P<judge>[A-Z]{2,4})(?:-[A-Z]{2,4})?\b"),
        re.compile(r"Case No\.\s*[0-9:A-Za-z\-]+-(?P<judge>[A-Z]{2,4})(?:-[A-Z]{2,4})?\b", re.I),
        re.compile(r"Civil Action No\.\s*[0-9:A-Za-z\-]+-(?P<judge>[A-Z]{2,4})(?:-[A-Z]{2,4})?\b", re.I),
    ]
    banned = {"CV", "NO", "CIV", "TILA", "IFP", "HUD", "JOSH"}
    for pattern in patterns:
        match = pattern.search(head)
        if match:
            judge = match.group("judge")
            if judge and judge not in banned:
                return judge
    return None


def surname_key(name: str) -> Optional[str]:
    if not name:
        return None
    tail = name.split()[-1]
    key = re.sub(r"[^A-Za-z]", "", tail).lower()
    return key or None


def is_full_name(name: str) -> bool:
    tokens = name.split()
    if len(tokens) < 2:
        return False
    substantive = [tok for tok in tokens if tok.lower().rstrip(".") not in ALLOWED_LOWER_NAME_TOKENS]
    return len(substantive) >= 2


def most_likely_counter_name(counter: Optional[Counter]) -> Optional[str]:
    if not counter:
        return None
    ranked = counter.most_common(2)
    if not ranked:
        return None
    if len(ranked) == 1 or ranked[0][1] > ranked[1][1]:
        return ranked[0][0]
    return None


def canonicalize_judge_name(
    raw_name: Optional[str],
    district: Optional[str],
    district_surname_map: Dict[Tuple[str, str], Counter],
    global_surname_map: Dict[str, Counter],
) -> Optional[str]:
    if not raw_name:
        return None
    name = MANUAL_CANONICAL_JUDGES.get(raw_name, raw_name)
    name = normalize_candidate_name(name)
    name = MANUAL_CANONICAL_JUDGES.get(name or "", name)
    name = normalize_candidate_name(name)
    if not name or name in MANUAL_REJECT_JUDGES:
        return None

    surname = surname_key(name)
    if not surname:
        return None

    if not is_full_name(name):
        if district and district_surname_map.get((district, surname)):
            district_match = most_likely_counter_name(district_surname_map[(district, surname)])
            if district_match:
                return district_match
        global_match = most_likely_counter_name(global_surname_map.get(surname))
        if global_match:
            return global_match
        return None
    return MANUAL_CANONICAL_JUDGES.get(name, name)


def build_judge_reference_maps(raw_index: Dict[str, Path]) -> Tuple[Dict[Tuple[str, str], Counter], Dict[Tuple[str, str], Counter], Dict[str, Counter]]:
    initials_map: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    district_surname_map: Dict[Tuple[str, str], Counter] = defaultdict(Counter)
    global_surname_map: Dict[str, Counter] = defaultdict(Counter)

    for path in raw_index.values():
        district = district_from_filename(path)
        if not district:
            continue
        text = read_text(path)
        explicit = extract_explicit_judge(text)
        explicit = MANUAL_CANONICAL_JUDGES.get(explicit or "", explicit)
        explicit = normalize_candidate_name(explicit)
        explicit = MANUAL_CANONICAL_JUDGES.get(explicit or "", explicit)
        explicit = normalize_candidate_name(explicit)
        initials = extract_docket_initials(text)
        if explicit and explicit not in MANUAL_REJECT_JUDGES and is_full_name(explicit):
            surname = surname_key(explicit)
            if surname:
                district_surname_map[(district, surname)][explicit] += 1
                global_surname_map[surname][explicit] += 1
        if explicit and initials and is_full_name(explicit):
            initials_map[(district, initials)][explicit] += 1

    return initials_map, district_surname_map, global_surname_map


def resolve_raw_text_path(case: dict, raw_index: Dict[str, Path]) -> Optional[Path]:
    source_file = (case.get("source_file") or "").strip().lower()
    if not source_file:
        return None
    return raw_index.get(source_file)


def judge_assignment_for_case(
    case: dict,
    raw_index: Dict[str, Path],
    initials_map: Dict[Tuple[str, str], Counter],
    district_surname_map: Dict[Tuple[str, str], Counter],
    global_surname_map: Dict[str, Counter],
) -> dict:
    district = district_from_case(case)
    path = resolve_raw_text_path(case, raw_index)
    if not district:
        return {
            "district": None,
            "raw_text_path": None,
            "judge_raw": None,
            "judge": None,
            "judge_source": "no_district",
        }
    if not path:
        return {
            "district": district,
            "raw_text_path": None,
            "judge_raw": None,
            "judge": None,
            "judge_source": "raw_text_missing",
        }

    text = read_text(path)
    judge_raw = extract_explicit_judge(text)
    judge_source = "explicit" if judge_raw else None
    docket_initials = extract_docket_initials(text)
    if not judge_raw and docket_initials and initials_map.get((district, docket_initials)):
        judge_raw = most_likely_counter_name(initials_map[(district, docket_initials)])
        judge_source = "docket_initials_map"

    judge = canonicalize_judge_name(judge_raw, district, district_surname_map, global_surname_map)
    if judge is None and docket_initials and initials_map.get((district, docket_initials)):
        fallback_judge = most_likely_counter_name(initials_map[(district, docket_initials)])
        if fallback_judge:
            judge_raw = fallback_judge
            judge = canonicalize_judge_name(judge_raw, district, district_surname_map, global_surname_map)
            if judge is not None:
                judge_source = "docket_initials_map_after_reject"
    if judge is None:
        judge_source = judge_source or "unidentified"

    return {
        "district": district,
        "raw_text_path": str(path),
        "judge_raw": judge_raw,
        "judge": judge,
        "judge_source": judge_source,
    }


class WikipediaAppointmentLookup:
    def __init__(self, seed_cache: Optional[Dict[str, dict]] = None) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": WIKI_USER_AGENT})
        self.lookup_cache: Dict[str, dict] = dict(seed_cache or {})
        self.lookup_cache.update(MANUAL_APPOINTMENT_LOOKUPS)
        self.text_cache: Dict[str, Tuple[Optional[str], Optional[str]]] = {}

    def request_json(self, params: dict, retries: int = 3) -> dict:
        last_error = None
        for attempt in range(retries):
            try:
                response = self.session.get(WIKIPEDIA_API, params=params, timeout=30)
                response.raise_for_status()
                payload = response.json()
                time.sleep(WIKI_SLEEP_SECONDS)
                return payload
            except Exception as exc:
                last_error = exc
                time.sleep(WIKI_SLEEP_SECONDS * (attempt + 2))
        raise RuntimeError(f"Wikipedia API request failed: {last_error}")

    def fetch_wikitext(self, title: str) -> Tuple[Optional[str], Optional[str]]:
        if title in self.text_cache:
            return self.text_cache[title]
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "titles": title,
            "format": "json",
            "formatversion": "2",
        }
        try:
            data = self.request_json(params)
        except Exception:
            self.text_cache[title] = (None, None)
            return self.text_cache[title]
        page = data.get("query", {}).get("pages", [{}])[0]
        if page.get("missing"):
            self.text_cache[title] = (None, page.get("title"))
            return self.text_cache[title]
        revisions = page.get("revisions") or []
        content = revisions[0].get("content") if revisions else None
        self.text_cache[title] = (content, page.get("title"))
        return self.text_cache[title]

    @staticmethod
    def parse_date(raw: str) -> Optional[dt.date]:
        text = (raw or "").strip()
        if not text:
            return None
        template = re.search(r"\{\{(?:start date(?: and age)?|birth date(?: and age)?)\|(\d{4})\|(\d{1,2})\|(\d{1,2})", text, re.I)
        if template:
            try:
                return dt.date(int(template.group(1)), int(template.group(2)), int(template.group(3)))
            except ValueError:
                return None
        text = text.replace("[[", "").replace("]]", "")
        text = re.sub(r"<.*?>", "", text)
        text = text.replace("{{nowrap|", "").replace("}}", "").strip()
        text = text.replace("·", " ").replace("–", "-")
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y", "%Y-%m-%d"):
            try:
                return dt.datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        embedded = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", text)
        if embedded:
            try:
                return dt.datetime.strptime(embedded.group(1), "%B %d, %Y").date()
            except ValueError:
                return None
        return None

    @staticmethod
    def normalize_office_text(raw: str) -> str:
        text = (raw or "").lower().replace("[[", "").replace("]]", "")
        text = text.replace("{{", "").replace("}}", "")
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"\|", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def classify_federal_office(cls, office: str) -> Optional[str]:
        office_text = cls.normalize_office_text(office)
        if not office_text or "chief judge" in office_text:
            return None
        if "magistrate judge" in office_text:
            return "magistrate_judge"
        if "court of appeals" in office_text or "circuit judge" in office_text:
            return "circuit_judge"
        if "district court" in office_text or "district judge" in office_text:
            return "district_judge"
        return None

    @classmethod
    def parse_federal_judge_start(cls, wikitext: str, expected_district: Optional[str] = None) -> Optional[dict]:
        offices: Dict[str, str] = {}
        starts: Dict[str, str] = {}
        for line in wikitext.splitlines():
            office_match = re.match(r"\|\s*office(\d*)\s*=\s*(.*)", line)
            if office_match:
                offices[office_match.group(1)] = office_match.group(2).strip()
            start_match = re.match(r"\|\s*term_start(\d*)\s*=\s*(.*)", line)
            if start_match:
                starts[start_match.group(1)] = start_match.group(2).strip()

        candidates = []
        for suffix, office in offices.items():
            office_role = cls.classify_federal_office(office)
            if not office_role:
                continue
            parsed = cls.parse_date(starts.get(suffix, ""))
            if parsed:
                candidates.append({
                    "date": parsed,
                    "office": office,
                    "office_text": cls.normalize_office_text(office),
                    "office_role": office_role,
                    "term_start_raw": starts.get(suffix, ""),
                })
        if not candidates:
            return None

        selection_basis = None
        selected_candidates = candidates
        district_patterns = DISTRICT_NAME_PATTERNS.get(expected_district or "", ())
        if district_patterns:
            district_matches = [
                row for row in candidates
                if any(pattern in row["office_text"] for pattern in district_patterns)
            ]
            if not district_matches:
                return None
            role_set = {row["office_role"] for row in district_matches}
            if len(role_set) != 1:
                return None
            selected_candidates = district_matches
            selection_basis = "district_match"

        if selection_basis is None:
            if len(candidates) == 1:
                selection_basis = "single_federal_office"
            else:
                role_set = {row["office_role"] for row in candidates}
                office_set = {row["office_text"] for row in candidates}
                if len(role_set) == 1 and len(office_set) == 1:
                    selection_basis = "same_role_same_office"
                else:
                    return None

        selected_candidates = sorted(selected_candidates, key=lambda row: (row["date"], row["office_text"]))
        selected = dict(selected_candidates[0])
        selected["selection_basis"] = selection_basis
        return selected

    def lookup(self, name: str, expected_district: Optional[str] = None) -> dict:
        cache_key = f"{name}||{expected_district or ''}"
        if cache_key in self.lookup_cache:
            return self.lookup_cache[cache_key]
        seeded = self.lookup_cache.get(name)
        if expected_district is None and seeded is not None:
            return seeded
        if expected_district is not None and seeded is not None and seeded.get("lookup_method") == "manual_seed":
            self.lookup_cache[cache_key] = seeded
            return seeded
        if len(name.split()) < 2:
            result = {"status": "unresolved", "page_title": None, "appointment_date": None, "office": None, "term_start_raw": None, "lookup_method": None, "office_selection_basis": None}
            self.lookup_cache[cache_key] = result
            if expected_district is None:
                self.lookup_cache[name] = result
            return result

        surname = surname_key(name) or ""
        tried_titles = set()

        def validate_title(title: str) -> Optional[dict]:
            if not title or title in tried_titles:
                return None
            tried_titles.add(title)
            wikitext, resolved_title = self.fetch_wikitext(title)
            if not wikitext or not resolved_title:
                return None
            if surname and surname not in re.sub(r"[^a-z]", "", resolved_title.lower()):
                # Keep only pages that still look like the right person.
                if surname not in re.sub(r"[^a-z]", "", wikitext.lower()[:5000]):
                    return None
            parsed = self.parse_federal_judge_start(wikitext, expected_district=expected_district)
            if not parsed:
                return None
            return {
                "status": "resolved",
                "page_title": resolved_title,
                "appointment_date": parsed["date"].isoformat(),
                "office": parsed["office"],
                "term_start_raw": parsed["term_start_raw"],
                "office_selection_basis": parsed.get("selection_basis"),
            }

        exact = validate_title(name)
        if exact:
            exact["lookup_method"] = "exact_title"
            self.lookup_cache[cache_key] = exact
            if expected_district is None:
                self.lookup_cache[name] = exact
            return exact

        queries = [f'"{name}" federal judge', f'"{name}" judge', name]
        for query in queries:
            try:
                data = self.request_json({
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json",
                })
            except Exception:
                continue
            for row in data.get("query", {}).get("search", [])[:5]:
                candidate = validate_title(row.get("title", ""))
                if candidate:
                    candidate["lookup_method"] = f"search:{query}"
                    self.lookup_cache[cache_key] = candidate
                    if expected_district is None:
                        self.lookup_cache[name] = candidate
                    return candidate

        result = {"status": "unresolved", "page_title": None, "appointment_date": None, "office": None, "term_start_raw": None, "lookup_method": None, "office_selection_basis": None}
        self.lookup_cache[cache_key] = result
        if expected_district is None:
            self.lookup_cache[name] = result
        return result


def lookup_cutoff_status(lookup: dict) -> str:
    appointment_date = lookup.get("appointment_date")
    if not appointment_date:
        return "unknown"
    try:
        parsed = dt.date.fromisoformat(appointment_date)
    except Exception:
        return "unknown"
    return "after_cutoff" if parsed > APPOINTMENT_CUTOFF else "before_cutoff"


def select_top_decline_circuits(cases: List[dict]) -> List[dict]:
    by_circuit: Dict[str, Dict[str, List[dict]]] = defaultdict(lambda: defaultdict(list))
    for case in cases:
        circuit = case.get("circuit")
        if circuit:
            by_circuit[circuit][case["_period"]].append(case)

    ranked = []
    for circuit, period_map in by_circuit.items():
        p1 = period_map.get("P1", [])
        p3 = period_map.get("P3", [])
        if len(p1) < 10 or len(p3) < 10:
            continue
        p1_rate = pct(sum(1 for case in p1 if broad_win(case)), len(p1))
        p3_rate = pct(sum(1 for case in p3 if broad_win(case)), len(p3))
        ranked.append({
            "circuit": circuit,
            "p1_n": len(p1),
            "p3_n": len(p3),
            "p1_broad_rate": round_or_none(p1_rate),
            "p3_broad_rate": round_or_none(p3_rate),
            "delta_pp": round_or_none((p3_rate or 0.0) - (p1_rate or 0.0)),
        })
    ranked.sort(key=lambda row: row["delta_pp"])
    return ranked[:TOP_CIRCUITS_N]


def analyze_circuit(
    circuit: str,
    cases: List[dict],
    raw_index: Dict[str, Path],
    initials_map: Dict[Tuple[str, str], Counter],
    district_surname_map: Dict[Tuple[str, str], Counter],
    global_surname_map: Dict[str, Counter],
    appointment_lookup: WikipediaAppointmentLookup,
) -> dict:
    full_p1 = [case for case in cases if case.get("circuit") == circuit and case["_period"] == "P1"]
    full_p3 = [case for case in cases if case.get("circuit") == circuit and case["_period"] == "P3"]

    full_p1_rate = (sum(1 for case in full_p1 if broad_win(case)) / len(full_p1)) if full_p1 else 0.0
    full_p3_broad = sum(1 for case in full_p3 if broad_win(case))
    full_shortfall = len(full_p3) * full_p1_rate - full_p3_broad

    district_p1 = [case for case in full_p1 if district_from_case(case)]
    district_p3 = [case for case in full_p3 if district_from_case(case)]
    district_p1_rate = (sum(1 for case in district_p1 if broad_win(case)) / len(district_p1)) if district_p1 else 0.0
    district_p3_broad = sum(1 for case in district_p3 if broad_win(case))
    district_shortfall = len(district_p3) * district_p1_rate - district_p3_broad

    p3_annotations = []
    for case in district_p3:
        assignment = judge_assignment_for_case(case, raw_index, initials_map, district_surname_map, global_surname_map)
        p3_annotations.append({"case": case, **assignment})

    districts = sorted({district_from_case(case) for case in district_p1 + district_p3 if district_from_case(case)})
    district_rows = []
    for district in districts:
        p1_cases = [case for case in district_p1 if district_from_case(case) == district]
        p3_rows = [row for row in p3_annotations if row["district"] == district]
        p3_cases = [row["case"] for row in p3_rows]
        p1_broad = sum(1 for case in p1_cases if broad_win(case))
        p3_broad = sum(1 for case in p3_cases if broad_win(case))
        expected = len(p3_cases) * district_p1_rate
        shortfall = expected - p3_broad
        mtd_cases = [case for case in p3_cases if is_mtd(case)]
        mtd_survival = pct(sum(1 for case in mtd_cases if not def_win(case)), len(mtd_cases))
        unique_judges = sorted({row["judge"] for row in p3_rows if row["judge"]})
        district_rows.append({
            "district": district,
            "p1_n": len(p1_cases),
            "p1_broad_rate": round_or_none(pct(p1_broad, len(p1_cases))),
            "p3_n": len(p3_cases),
            "p3_broad_rate": round_or_none(pct(p3_broad, len(p3_cases))),
            "expected_p3_broad_at_circuit_district_p1_rate": round(expected, 3),
            "actual_p3_broad": p3_broad,
            "shortfall_cases": round(shortfall, 3),
            "share_of_district_court_shortfall": round_or_none(shortfall / district_shortfall if district_shortfall else None, 4),
            "share_of_full_circuit_shortfall": round_or_none(shortfall / full_shortfall if full_shortfall else None, 4),
            "p3_pro_se_share": round_or_none(pct(sum(1 for case in p3_cases if is_pro_se(case)), len(p3_cases))),
            "p3_mtd_n": len(mtd_cases),
            "p3_mtd_survival_rate": round_or_none(mtd_survival),
            "p3_identified_judges_n": len(unique_judges),
            "p3_identified_judges": unique_judges,
            "p3_unknown_judge_cases_n": sum(1 for row in p3_rows if not row["judge"]),
        })
    district_rows.sort(key=lambda row: (-row["shortfall_cases"], -row["p3_n"], row["district"]))

    judge_groups: Dict[str, List[dict]] = defaultdict(list)
    unknown_rows = []
    for row in p3_annotations:
        if row["judge"]:
            judge_groups[row["judge"]].append(row)
        else:
            unknown_rows.append(row)

    judge_rows = []
    judge_district_map = {}
    for judge, rows in judge_groups.items():
        p3_cases = [row["case"] for row in rows]
        p3_broad = sum(1 for case in p3_cases if broad_win(case))
        expected = len(p3_cases) * district_p1_rate
        shortfall = expected - p3_broad
        district_counts = Counter(row["district"] for row in rows if row["district"])
        dominant_district = district_counts.most_common(1)[0][0] if district_counts else None
        judge_district_map[judge] = dominant_district
        judge_rows.append({
            "judge": judge,
            "district": dominant_district,
            "p3_n": len(p3_cases),
            "p3_broad_rate": round_or_none(pct(p3_broad, len(p3_cases))),
            "expected_p3_broad_at_circuit_district_p1_rate": round(expected, 3),
            "actual_p3_broad": p3_broad,
            "shortfall_cases": round(shortfall, 3),
            "share_of_district_court_shortfall": round_or_none(shortfall / district_shortfall if district_shortfall else None, 4),
            "share_of_full_circuit_shortfall": round_or_none(shortfall / full_shortfall if full_shortfall else None, 4),
        })
    judge_rows.sort(key=lambda row: (-row["shortfall_cases"], -row["p3_n"], row["judge"]))

    identified_counts = Counter(row["judge"] for row in p3_annotations if row["judge"])
    identified_total = sum(identified_counts.values())
    unknown_total = len(unknown_rows)
    total_district_p3 = len(p3_annotations)

    hhi_identified = None
    if identified_total:
        hhi_identified = 10000.0 * sum((count / identified_total) ** 2 for count in identified_counts.values())
    counts_with_unknown = list(identified_counts.values()) + ([unknown_total] if unknown_total else [])
    hhi_with_unknown = None
    if total_district_p3:
        hhi_with_unknown = 10000.0 * sum((count / total_district_p3) ** 2 for count in counts_with_unknown)

    appointment_results = {}
    recent_appointees = []
    judge_district_lookup = {
        row["judge"]: row.get("district")
        for row in judge_rows
        if row.get("judge")
    }
    for judge in sorted(judge_groups):
        lookup = appointment_lookup.lookup(judge, expected_district=judge_district_lookup.get(judge))
        appointment_results[judge] = lookup
        if lookup.get("appointment_date"):
            appointment_date = dt.date.fromisoformat(lookup["appointment_date"])
            if appointment_date > APPOINTMENT_CUTOFF:
                recent_appointees.append({
                    "judge": judge,
                    "appointment_date": lookup["appointment_date"],
                    "office": lookup.get("office"),
                    "page_title": lookup.get("page_title"),
                    "lookup_method": lookup.get("lookup_method"),
                })

    resolved_lookup_count = sum(1 for lookup in appointment_results.values() if lookup.get("status") == "resolved")
    unresolved_lookup_count = sum(1 for lookup in appointment_results.values() if lookup.get("status") != "resolved")

    top_district = district_rows[0] if district_rows else None
    top_judge = judge_rows[0] if judge_rows else None
    top_judge_shortfall = top_judge.get("shortfall_cases") if top_judge else 0.0
    unknown_shortfall = round((unknown_total * district_p1_rate) - sum(1 for row in unknown_rows if broad_win(row["case"])), 3) if unknown_rows else 0.0
    judge_full_test = conservative_single_judge_test(top_judge_shortfall, unknown_shortfall, full_shortfall)
    judge_district_test = conservative_single_judge_test(top_judge_shortfall, unknown_shortfall, district_shortfall)
    post_2025_status = "definitive_positive" if recent_appointees else (
        "indeterminate" if unresolved_lookup_count or unknown_total else "definitive_negative"
    )

    return {
        "circuit": circuit,
        "full_circuit_decline": {
            "p1_n": len(full_p1),
            "p1_broad_rate": round_or_none(100.0 * full_p1_rate),
            "p3_n": len(full_p3),
            "p3_broad_rate": round_or_none(pct(full_p3_broad, len(full_p3))),
            "delta_pp": round_or_none(pct(full_p3_broad, len(full_p3)) - (100.0 * full_p1_rate)),
            "full_circuit_shortfall_cases": round(full_shortfall, 3),
        },
        "district_court_component": {
            "p1_n": len(district_p1),
            "p1_broad_rate": round_or_none(100.0 * district_p1_rate),
            "p3_n": len(district_p3),
            "p3_broad_rate": round_or_none(pct(district_p3_broad, len(district_p3))),
            "delta_pp": round_or_none(pct(district_p3_broad, len(district_p3)) - (100.0 * district_p1_rate)),
            "district_court_shortfall_cases": round(district_shortfall, 3),
            "share_of_full_p3_cases": round_or_none(len(district_p3) / len(full_p3) if full_p3 else None, 4),
            "share_of_full_shortfall": round_or_none(district_shortfall / full_shortfall if full_shortfall else None, 4),
        },
        "districts": district_rows,
        "judges": {
            "identified_p3_cases": identified_total,
            "unknown_p3_cases": unknown_total,
            "identification_rate": round_or_none(identified_total / total_district_p3 if total_district_p3 else None, 4),
            "unknown_shortfall_cases": unknown_shortfall,
            "judge_hhi_identified_only_10000": round_or_none(hhi_identified, 2),
            "judge_hhi_with_unknown_bucket_10000": round_or_none(hhi_with_unknown, 2),
            "judge_rows": judge_rows,
            "appointment_lookup": appointment_results,
            "appointed_after_2025_01_31": recent_appointees,
            "post_2025_appointee_check": {
                "status": post_2025_status,
                "resolved_lookup_count": resolved_lookup_count,
                "unresolved_lookup_count": unresolved_lookup_count,
                "unknown_judge_p3_cases": unknown_total,
                "post_2025_appointees_found": len(recent_appointees),
            },
        },
        "threshold_tests": {
            "top_district": {
                "district": top_district.get("district") if top_district else None,
                "share_of_district_court_shortfall": top_district.get("share_of_district_court_shortfall") if top_district else None,
                "share_of_full_circuit_shortfall": top_district.get("share_of_full_circuit_shortfall") if top_district else None,
                "gt_50pct_of_district_court_shortfall": bool(top_district and (top_district.get("share_of_district_court_shortfall") or 0) > 0.5),
                "gt_50pct_of_full_circuit_shortfall": bool(top_district and (top_district.get("share_of_full_circuit_shortfall") or 0) > 0.5),
            },
            "top_identified_judge": {
                "scope": "identified_judges_only",
                "judge": top_judge.get("judge") if top_judge else None,
                "share_of_district_court_shortfall": top_judge.get("share_of_district_court_shortfall") if top_judge else None,
                "share_of_full_circuit_shortfall": top_judge.get("share_of_full_circuit_shortfall") if top_judge else None,
                "observed_gt_50pct_of_district_court_shortfall": bool(top_judge and (top_judge.get("share_of_district_court_shortfall") or 0) > 0.5),
                "observed_gt_50pct_of_full_circuit_shortfall": bool(top_judge and (top_judge.get("share_of_full_circuit_shortfall") or 0) > 0.5),
            },
            "unknown_judge_bucket": {
                "p3_cases": unknown_total,
                "shortfall_cases": unknown_shortfall,
                "share_of_district_court_shortfall": round_or_none(share_or_none(unknown_shortfall, district_shortfall), 4),
                "share_of_full_circuit_shortfall": round_or_none(share_or_none(unknown_shortfall, full_shortfall), 4),
            },
            "any_single_judge": {
                "top_identified_judge": top_judge.get("judge") if top_judge else None,
                "observed_top_identified_share_of_district_court_shortfall": judge_district_test["observed_share"],
                "observed_top_identified_share_of_full_circuit_shortfall": judge_full_test["observed_share"],
                "unknown_judge_share_of_district_court_shortfall": judge_district_test["unresolved_share"],
                "unknown_judge_share_of_full_circuit_shortfall": judge_full_test["unresolved_share"],
                "max_possible_single_judge_share_of_district_court_shortfall": judge_district_test["max_possible_share"],
                "max_possible_single_judge_share_of_full_circuit_shortfall": judge_full_test["max_possible_share"],
                "gt_50pct_of_district_court_shortfall_status": judge_district_test["status"],
                "gt_50pct_of_full_circuit_shortfall_status": judge_full_test["status"],
            },
        },
    }


def summarize_cross_circuit_findings(top_circuits: List[dict], circuit_results: Dict[str, dict]) -> dict:
    majority_districts_full = []
    majority_districts_district = []
    majority_judges_full = []
    majority_judges_district = []
    indeterminate_judges_full = []
    indeterminate_judges_district = []
    definitive_no_judges_full = []
    definitive_no_judges_district = []
    judge_test_rows = []
    recent_appointee_circuits = []
    indeterminate_appointment_circuits = []
    definitive_negative_appointment_circuits = []
    unresolved_lookup_counts = {}
    hhi_rows = []
    high_impact_post_2025 = []
    unresolved_high_impact = []

    for row in top_circuits:
        circuit = row["circuit"]
        detail = circuit_results[circuit]
        top_district = detail["threshold_tests"]["top_district"]
        judge_test = detail["threshold_tests"]["any_single_judge"]
        appointment_check = detail["judges"]["post_2025_appointee_check"]

        for district_row in detail["districts"]:
            district_summary = {
                "circuit": circuit,
                "district": district_row["district"],
                "share_of_full_circuit_shortfall": district_row.get("share_of_full_circuit_shortfall"),
                "share_of_district_court_shortfall": district_row.get("share_of_district_court_shortfall"),
            }
            if (district_row.get("share_of_full_circuit_shortfall") or 0) > 0.5:
                majority_districts_full.append(district_summary)
            if (district_row.get("share_of_district_court_shortfall") or 0) > 0.5:
                majority_districts_district.append(district_summary)

        judge_row = {
            "circuit": circuit,
            "judge": judge_test.get("top_identified_judge"),
            "observed_top_identified_share_of_full_circuit_shortfall": judge_test.get("observed_top_identified_share_of_full_circuit_shortfall"),
            "observed_top_identified_share_of_district_court_shortfall": judge_test.get("observed_top_identified_share_of_district_court_shortfall"),
            "unknown_judge_share_of_full_circuit_shortfall": judge_test.get("unknown_judge_share_of_full_circuit_shortfall"),
            "unknown_judge_share_of_district_court_shortfall": judge_test.get("unknown_judge_share_of_district_court_shortfall"),
            "max_possible_single_judge_share_of_full_circuit_shortfall": judge_test.get("max_possible_single_judge_share_of_full_circuit_shortfall"),
            "max_possible_single_judge_share_of_district_court_shortfall": judge_test.get("max_possible_single_judge_share_of_district_court_shortfall"),
            "gt_50pct_of_full_circuit_shortfall_status": judge_test.get("gt_50pct_of_full_circuit_shortfall_status"),
            "gt_50pct_of_district_court_shortfall_status": judge_test.get("gt_50pct_of_district_court_shortfall_status"),
        }
        judge_test_rows.append(judge_row)

        full_status = judge_row["gt_50pct_of_full_circuit_shortfall_status"]
        if full_status == "definitive_yes":
            majority_judges_full.append(judge_row)
        elif full_status == "indeterminate":
            indeterminate_judges_full.append(judge_row)
        elif full_status == "definitive_no":
            definitive_no_judges_full.append(judge_row)

        district_status = judge_row["gt_50pct_of_district_court_shortfall_status"]
        if district_status == "definitive_yes":
            majority_judges_district.append(judge_row)
        elif district_status == "indeterminate":
            indeterminate_judges_district.append(judge_row)
        elif district_status == "definitive_no":
            definitive_no_judges_district.append(judge_row)

        recent = detail["judges"]["appointed_after_2025_01_31"]
        if appointment_check["status"] == "definitive_positive":
            recent_appointee_circuits.append({"circuit": circuit, "judges": recent})
        elif appointment_check["status"] == "indeterminate":
            indeterminate_appointment_circuits.append({
                "circuit": circuit,
                "resolved_lookup_count": appointment_check["resolved_lookup_count"],
                "unresolved_lookup_count": appointment_check["unresolved_lookup_count"],
                "unknown_judge_p3_cases": appointment_check["unknown_judge_p3_cases"],
            })
        else:
            definitive_negative_appointment_circuits.append({
                "circuit": circuit,
                "resolved_lookup_count": appointment_check["resolved_lookup_count"],
            })

        unresolved_lookup_counts[circuit] = appointment_check["unresolved_lookup_count"]
        hhi_rows.append({
            "circuit": circuit,
            "judge_hhi_identified_only_10000": detail["judges"]["judge_hhi_identified_only_10000"],
            "judge_hhi_with_unknown_bucket_10000": detail["judges"]["judge_hhi_with_unknown_bucket_10000"],
        })

        for judge_row in detail["judges"]["judge_rows"]:
            share_of_full = judge_row.get("share_of_full_circuit_shortfall")
            if share_of_full is None or share_of_full < HIGH_IMPACT_FULL_SHORTFALL_SHARE:
                continue
            lookup = (detail["judges"].get("appointment_lookup") or {}).get(judge_row["judge"], {})
            high_impact_row = {
                "circuit": circuit,
                "judge": judge_row["judge"],
                "district": judge_row.get("district"),
                "p3_n": judge_row.get("p3_n"),
                "share_of_full_circuit_shortfall": share_of_full,
                "appointment_lookup_status": lookup.get("status"),
                "appointment_date": lookup.get("appointment_date"),
                "office": lookup.get("office"),
                "lookup_method": lookup.get("lookup_method"),
            }
            if lookup_cutoff_status(lookup) == "after_cutoff":
                high_impact_post_2025.append(high_impact_row)
            elif lookup.get("status") != "resolved" or not lookup.get("appointment_date"):
                unresolved_high_impact.append(high_impact_row)

    overall_post_2025_status = "definitive_positive" if recent_appointee_circuits else (
        "indeterminate" if indeterminate_appointment_circuits else "definitive_negative"
    )

    return {
        "districts_over_50pct_of_full_circuit_shortfall": majority_districts_full,
        "districts_over_50pct_of_district_court_shortfall": majority_districts_district,
        "judges_over_50pct_of_full_circuit_shortfall": majority_judges_full,
        "judges_over_50pct_of_district_court_shortfall": majority_judges_district,
        "single_judge_gt50_test_rows": judge_test_rows,
        "circuits_with_indeterminate_single_judge_gt50_full_circuit_test": indeterminate_judges_full,
        "circuits_with_indeterminate_single_judge_gt50_district_court_test": indeterminate_judges_district,
        "circuits_with_definitive_no_single_judge_gt50_full_circuit_test": definitive_no_judges_full,
        "circuits_with_definitive_no_single_judge_gt50_district_court_test": definitive_no_judges_district,
        "circuits_with_post_2025_appointees": recent_appointee_circuits,
        "post_2025_appointee_check_status": overall_post_2025_status,
        "circuits_with_indeterminate_post_2025_appointee_check": indeterminate_appointment_circuits,
        "circuits_with_definitive_no_post_2025_appointee_check": definitive_negative_appointment_circuits,
        "unresolved_appointment_lookup_counts": unresolved_lookup_counts,
        "total_unresolved_appointment_lookups": sum(unresolved_lookup_counts.values()),
        "high_impact_judges_with_post_2025_appointments": high_impact_post_2025,
        "unresolved_high_impact_judges": unresolved_high_impact,
        "judge_hhi_rows": hhi_rows,
    }


def build_memo(results: dict) -> str:
    lines: List[str] = []
    findings = results["cross_circuit_findings"]
    identified_hhi_values = [
        row["judge_hhi_identified_only_10000"]
        for row in findings["judge_hhi_rows"]
        if row["judge_hhi_identified_only_10000"] is not None
    ]
    unknown_hhi_values = [
        row["judge_hhi_with_unknown_bucket_10000"]
        for row in findings["judge_hhi_rows"]
        if row["judge_hhi_with_unknown_bucket_10000"] is not None
    ]

    def appointee_check_label(detail: dict) -> str:
        check = detail["judges"]["post_2025_appointee_check"]
        if check["status"] == "definitive_positive":
            return str(check["post_2025_appointees_found"])
        if check["status"] == "definitive_negative":
            return "0 (complete)"
        return "0 resolved; indeterminate"

    def judge_test_sentence(detail: dict) -> str:
        judge_test = detail["threshold_tests"]["any_single_judge"]
        status = judge_test["gt_50pct_of_full_circuit_shortfall_status"]
        observed = fmt_share(judge_test.get("observed_top_identified_share_of_full_circuit_shortfall"))
        unknown = fmt_share(judge_test.get("unknown_judge_share_of_full_circuit_shortfall"))
        maximum = fmt_share(judge_test.get("max_possible_single_judge_share_of_full_circuit_shortfall"))
        label = judge_test.get("top_identified_judge") or "NA"
        if status == "definitive_yes":
            return f"definitive yes; observed top identified judge {label} = {observed}."
        if status == "definitive_no":
            return f"definitive no; observed top identified judge {label} = {observed}, unknown-judge bucket = {unknown}, conservative max possible single-judge share = {maximum}."
        return f"indeterminate; observed top identified judge {label} = {observed}, unknown-judge bucket = {unknown}, conservative max possible single-judge share = {maximum}."

    def join_labels(labels: List[str]) -> str:
        items = [label for label in labels if label]
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} and {items[1]}"
        return ", ".join(items[:-1]) + f", and {items[-1]}"

    def unique_circuits(rows: List[dict]) -> List[str]:
        return list(dict.fromkeys(row.get("circuit") for row in rows if row.get("circuit")))

    def single_judge_scope_sentence() -> str:
        definitive_yes = unique_circuits(findings["judges_over_50pct_of_full_circuit_shortfall"])
        definitive_no = unique_circuits(findings["circuits_with_definitive_no_single_judge_gt50_full_circuit_test"])
        indeterminate = unique_circuits(findings["circuits_with_indeterminate_single_judge_gt50_full_circuit_test"])
        if definitive_yes:
            return f"The no-single-judge claim is affirmatively false in {join_labels(definitive_yes)}."
        if definitive_no and indeterminate:
            return f"The no-single-judge claim is definitive only in {join_labels(definitive_no)} and remains unresolved in {join_labels(indeterminate)}."
        if definitive_no:
            return f"The no-single-judge claim is definitive in {join_labels(definitive_no)}."
        if indeterminate:
            return f"The no-single-judge claim remains unresolved in {join_labels(indeterminate)}."
        return "The single-judge >50% test is not informative in the current top-decline set."

    def post_2025_scope_sentence() -> str:
        status = findings["post_2025_appointee_check_status"]
        if status == "definitive_positive":
            circuits = unique_circuits(findings["circuits_with_post_2025_appointees"])
            return f"The post-2025-appointee check is positive in {join_labels(circuits)}."
        if status == "definitive_negative":
            return "The post-2025-appointee check is definitively negative across the top-decline circuits."
        return "The post-2025-appointee check remains indeterminate because some P3 judges still lack office-relevant appointment dates or judge identification."

    lines.append("# Circuit District Deep-Dive Analysis")
    lines.append("")
    lines.append(f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## Method and assumptions")
    lines.append("")
    lines.append("- Reused the same screened-in disability universe and the same period definitions as scripts/extended_doctrinal_analysis.py: P1 = 2013-2020, P2 = 2021-2022, P3 = 2023-2026.")
    lines.append("- Kept the original broad-win definition: outcome in {PLAINTIFF_WIN, MIXED}.")
    lines.append("- Ranked circuits by the full-universe P1 -> P3 broad-win decline, then did the district/judge attribution on district-court cases inside those circuits.")
    lines.append("- The unified database has no native district or judge fields. Districts were derived from the structured court field; judges were parsed from opinion headers/signatures in the raw-text opinion files under ../allFHAcases.")
    lines.append("- Singleton surnames and obvious OCR fragments are now only counted as identified judges when they can be canonically matched to a fuller identity; otherwise they are pushed into the unresolved bucket so they do not overstate identification coverage or depress the unknown-inclusive HHI.")
    lines.append("- District and judge 'decline' shares are expressed as a P3 shortfall count: expected P3 broad wins at the circuit's district-court P1 baseline minus actual P3 broad wins. They locate where the P3 shortfall is concentrated, not whose own P1 -> P3 rate changed the most.")
    lines.append("- Share-of-full-decline ratios are diagnostic, non-additive shares rather than partition totals. They can exceed 100% because a district-court shortfall is being compared with a full-circuit denominator while offsetting negative contributions and non-district components remain outside the numerator.")
    lines.append("- The district-side >50% test is complete because every P3 district-court case is district-assigned. The judge-side >50% test now reports conservative bounds: observed top identified judge share, unknown-judge share, and the max possible single-judge share if all unresolved judge shortfall belonged to one judge.")
    lines.append("- MTD survival is coded as 1 - defendant-win rate among P3 district-court motion-to-dismiss cases.")
    lines.append("- Post-Jan.-2025 appointee checks use office-relevant appointment dates when a single federal office can be tied to the judge's case district; same-district multi-office biographies are left unresolved rather than forced into a negative.")
    lines.append("- A circuit-level post-Jan.-2025 result is only definitive when both judge identification and appointment lookups are complete; otherwise the result is reported as indeterminate rather than as a clean negative.")
    lines.append("- Appointment dates come from manual seeds first, then any prior district-keyed lookup results already cached in results/circuit_district_deep_dive_results.json when that file exists, and only then from live Wikipedia lookups. That makes reruns reproducible within this workspace, but a fresh machine or later Wikipedia edits can still change the unresolved/resolved mix at the margins.")
    lines.append("")

    lines.append("## Table: top-5 declining circuits with district-level decomposition")
    lines.append("")
    lines.append("| Circuit | Full P1→P3 decline | P3 district-court cases | Leading district (identified P3 judges) | District share of full decline | Leading judge | Judge share of full decline | HHI (identified / +unknown) | Post-Jan-2025 appointee check |")
    lines.append("| --- | ---: | ---: | --- | ---: | --- | ---: | ---: | --- |")
    for row in results["top_5_circuits_by_full_decline"]:
        circuit = row["circuit"]
        detail = results["circuits"][circuit]
        top_district = detail["threshold_tests"]["top_district"]
        top_judge = detail["threshold_tests"]["top_identified_judge"]
        top_district_detail = detail["districts"][0] if detail["districts"] else None
        top_district_label = top_district.get("district") or "NA"
        if top_district_detail is not None:
            top_district_label = f"{top_district_label} ({top_district_detail['p3_identified_judges_n']})"
        hhi_identified = detail["judges"]["judge_hhi_identified_only_10000"]
        hhi_unknown = detail["judges"]["judge_hhi_with_unknown_bucket_10000"]
        hhi_label = "NA"
        if hhi_identified is not None and hhi_unknown is not None:
            hhi_label = f"{hhi_identified:.2f} / {hhi_unknown:.2f}"
        lines.append(
            f"| {circuit} | {fmt_pct(row['p1_broad_rate'])} → {fmt_pct(row['p3_broad_rate'])} ({row['delta_pp']:+.2f} pp) | "
            f"{detail['district_court_component']['p3_n']} | {top_district_label} | {fmt_share(top_district.get('share_of_full_circuit_shortfall'))} | "
            f"{top_judge.get('judge') or 'NA'} | {fmt_share(top_judge.get('share_of_full_circuit_shortfall'))} | "
            f"{hhi_label} | {appointee_check_label(detail)} |"
        )
    lines.append("")
    lines.append("## Finding: is the decline concentrated in a few judges or genuinely diffuse?")
    lines.append("")
    if findings["districts_over_50pct_of_full_circuit_shortfall"]:
        district_bits = "; ".join(
            f"{row['circuit']} — {row['district']} ({fmt_share(row['share_of_full_circuit_shortfall'])} of full-circuit shortfall)"
            for row in findings["districts_over_50pct_of_full_circuit_shortfall"]
        )
        district_circuits = unique_circuits(findings["districts_over_50pct_of_full_circuit_shortfall"])
        district_entry_label = "entry" if len(findings["districts_over_50pct_of_full_circuit_shortfall"]) == 1 else "entries"
        circuit_label = "circuit" if len(district_circuits) == 1 else "circuits"
        lines.append(
            f"- Districts clearing the >50% full-circuit-decline threshold appear in {len(district_circuits)} {circuit_label}; there are {len(findings['districts_over_50pct_of_full_circuit_shortfall'])} qualifying district {district_entry_label}: {district_bits}."
        )
    else:
        lines.append("- No district clears the >50% full-circuit-decline threshold in any of the five circuits.")
    if findings["judges_over_50pct_of_full_circuit_shortfall"]:
        judge_bits = "; ".join(
            f"{row['circuit']} — {row['judge']} ({fmt_share(row['observed_top_identified_share_of_full_circuit_shortfall'])})"
            for row in findings["judges_over_50pct_of_full_circuit_shortfall"]
        )
        lines.append(f"- A single judge definitively clears the >50% full-circuit-decline threshold in: {judge_bits}.")
    else:
        lines.append("- No circuit has a definitive observed >50% single-judge concentration.")
    if findings["circuits_with_definitive_no_single_judge_gt50_full_circuit_test"]:
        definite_no_bits = "; ".join(
            f"{row['circuit']} (max possible single-judge share {fmt_share(row['max_possible_single_judge_share_of_full_circuit_shortfall'])})"
            for row in findings["circuits_with_definitive_no_single_judge_gt50_full_circuit_test"]
        )
        lines.append(f"- The judge-side >50% full-circuit test resolves to no in: {definite_no_bits}.")
    if findings["circuits_with_indeterminate_single_judge_gt50_full_circuit_test"]:
        indeterminate_bits = "; ".join(
            f"{row['circuit']} (observed top identified={fmt_share(row['observed_top_identified_share_of_full_circuit_shortfall'])}, unknown bucket={fmt_share(row['unknown_judge_share_of_full_circuit_shortfall'])}, max possible={fmt_share(row['max_possible_single_judge_share_of_full_circuit_shortfall'])})"
            for row in findings["circuits_with_indeterminate_single_judge_gt50_full_circuit_test"]
        )
        lines.append(f"- The judge-side >50% full-circuit test remains indeterminate where unresolved judge assignments are too large to rule out a single-judge concentration: {indeterminate_bits}.")
    if identified_hhi_values and unknown_hhi_values:
        lines.append(
            f"- Judge-concentration HHI ranges from {min(identified_hhi_values):.2f} to {max(identified_hhi_values):.2f} on identified judges only, and from {min(unknown_hhi_values):.2f} to {max(unknown_hhi_values):.2f} when the unknown-judge bucket is treated as one extra chamber."
        )
    if findings["districts_over_50pct_of_full_circuit_shortfall"]:
        district_circuits = unique_circuits(findings["districts_over_50pct_of_full_circuit_shortfall"])
        district_clause = (
            f"{len(findings['districts_over_50pct_of_full_circuit_shortfall'])} district entries across {len(district_circuits)} circuits clear the >50% full-circuit threshold"
        )
    else:
        district_clause = "no district clears the >50% full-circuit threshold"
    definitive_no_circuits = unique_circuits(findings["circuits_with_definitive_no_single_judge_gt50_full_circuit_test"])
    indeterminate_circuits = unique_circuits(findings["circuits_with_indeterminate_single_judge_gt50_full_circuit_test"])
    if definitive_no_circuits and indeterminate_circuits:
        judge_clause = f"the single-judge test resolves to no in {join_labels(definitive_no_circuits)} and remains indeterminate in {join_labels(indeterminate_circuits)}"
    elif definitive_no_circuits:
        judge_clause = f"the single-judge test resolves to no in {join_labels(definitive_no_circuits)}"
    elif indeterminate_circuits:
        judge_clause = f"the single-judge test remains indeterminate in {join_labels(indeterminate_circuits)}"
    else:
        judge_clause = "the single-judge test is not dispositive in this set"
    lines.append(f"- Overall, the P3 shortfall is more district-concentrated than judge-concentrated: {district_clause}, while {judge_clause}.")
    lines.append("")
    lines.append("## Finding: does any post-2025 appointee drive meaningful share of P3 outcomes?")
    lines.append("")
    if findings["circuits_with_post_2025_appointees"]:
        recent_bits = "; ".join(
            f"{row['circuit']} — " + ", ".join(
                f"{judge['judge']} ({judge['appointment_date']})"
                for judge in row["judges"]
            )
            for row in findings["circuits_with_post_2025_appointees"]
        )
        lines.append(
            f"- Yes. Resolved judge biographies show post-Jan.-2025 appointees in the P3 set: {recent_bits}."
        )
    elif findings["post_2025_appointee_check_status"] == "definitive_negative":
        lines.append(
            "- No resolved judge biography shows a post-Jan.-2025 appointee in the P3 set, and the overall check is definitively negative."
        )
    else:
        lines.append(
            "- No resolved judge biography shows a post-Jan.-2025 appointee in the P3 set, but the overall check is indeterminate rather than definitively negative."
        )
    if findings["circuits_with_indeterminate_post_2025_appointee_check"]:
        unresolved_bits = "; ".join(
            f"{row['circuit']} ({row['unresolved_lookup_count']} unresolved appointment lookups; {row['unknown_judge_p3_cases']} P3 cases with unidentified judges)"
            for row in findings["circuits_with_indeterminate_post_2025_appointee_check"]
        )
        lines.append(
            f"- Remaining gaps that prevent a definitive negative: {unresolved_bits}."
        )
    elif findings["circuits_with_definitive_no_post_2025_appointee_check"]:
        lines.append(
            "- Appointment-date coverage is complete for the identified P3 judges in each top-decline circuit, so the negative result is no longer qualification-dependent."
        )
    lines.append(
        f"- Unresolved appointment lookups alone still total {findings['total_unresolved_appointment_lookups']} across the five circuits."
    )
    lines.append("")
    lines.append("## Conclusion: effect on the 'institutional, not ideological' claim")
    lines.append("")
    lines.append("- This deep dive still points most strongly to a district-level pleading gate: the steepest declines are heavily concentrated in a few districts, and those districts tend to pair high P3 pro se shares with very low P3 MTD survival.")
    lines.append(f"- But the no-single-judge and no-post-2025-appointee claims are not fully global. {single_judge_scope_sentence()} {post_2025_scope_sentence()}")
    lines.append("")
    lines.append("## Circuit-by-circuit findings")
    lines.append("")
    for row in results["top_5_circuits_by_full_decline"]:
        circuit = row["circuit"]
        detail = results["circuits"][circuit]
        judge_test = detail["threshold_tests"]["any_single_judge"]
        appointment_check = detail["judges"]["post_2025_appointee_check"]
        lines.append(f"### {circuit}")
        lines.append("")
        full = detail["full_circuit_decline"]
        district_component = detail["district_court_component"]
        td = detail["threshold_tests"]["top_district"]
        lines.append(
            f"- Full circuit decline: {fmt_pct(full['p1_broad_rate'])} -> {fmt_pct(full['p3_broad_rate'])} ({full['delta_pp']:+.2f} pp), producing a P3 shortfall of {full['full_circuit_shortfall_cases']:.2f} broad-win-equivalent cases."
        )
        lines.append(
            f"- District-court component: {fmt_pct(district_component['p1_broad_rate'])} -> {fmt_pct(district_component['p3_broad_rate'])} ({district_component['delta_pp']:+.2f} pp), with {district_component['district_court_shortfall_cases']:.2f} shortfall cases across {district_component['p3_n']} P3 district-court cases ({fmt_share(district_component['share_of_full_p3_cases'])} of the circuit's P3 docket)."
        )
        district_bits = []
        for district_row in detail["districts"][:3]:
            district_bits.append(
                f"{district_row['district']} ({district_row['shortfall_cases']:.2f} shortfall cases; {fmt_share(district_row['share_of_full_circuit_shortfall'])} of full-circuit decline; identified P3 judges={district_row['p3_identified_judges_n']}; P3 pro se={fmt_pct(district_row['p3_pro_se_share'])}; P3 MTD survival={fmt_pct(district_row['p3_mtd_survival_rate'])})"
            )
        if district_bits:
            lines.append("- Largest district shortfall concentrations: " + "; ".join(district_bits) + ".")
        judge_bits = []
        for judge_row in detail["judges"]["judge_rows"][:3]:
            judge_bits.append(
                f"{judge_row['judge']} ({judge_row['district']}; {judge_row['shortfall_cases']:.2f} shortfall cases; {fmt_share(judge_row['share_of_full_circuit_shortfall'])} of full-circuit decline)"
            )
        if judge_bits:
            lines.append("- Largest identified judge shortfall concentrations: " + "; ".join(judge_bits) + ".")
        lines.append(
            f"- Judge identification coverage: {detail['judges']['identified_p3_cases']} / {detail['judges']['identified_p3_cases'] + detail['judges']['unknown_p3_cases']} P3 district-court cases ({fmt_share(detail['judges']['identification_rate'])})."
        )
        lines.append(
            f"- Concentration: HHI identified-only={detail['judges']['judge_hhi_identified_only_10000']}; HHI with unknown bucket={detail['judges']['judge_hhi_with_unknown_bucket_10000']}."
        )
        lines.append(
            f"- >50% test for full-circuit decline: top district {td['district'] or 'NA'} = {fmt_share(td.get('share_of_full_circuit_shortfall'))}; judge-side result = {judge_test_sentence(detail)}"
        )
        if appointment_check["status"] == "definitive_positive":
            recent_bits = [
                f"{recent_row['judge']} ({recent_row['appointment_date']}; {recent_row['office']})"
                for recent_row in detail["judges"]["appointed_after_2025_01_31"]
            ]
            lines.append(
                "- Post-Jan. 2025 appointee check: positive — " + "; ".join(recent_bits) + "."
            )
        elif appointment_check["status"] == "indeterminate":
            lines.append(
                f"- Post-Jan. 2025 appointee check: indeterminate; {appointment_check['post_2025_appointees_found']} resolved post-Jan. 2025 appointees found, but {appointment_check['unresolved_lookup_count']} identified judges still lack appointment dates and {appointment_check['unknown_judge_p3_cases']} P3 cases still lack judge identification."
            )
        else:
            lines.append(
                f"- Post-Jan. 2025 appointee check: negative; {appointment_check['post_2025_appointees_found']} resolved post-Jan. 2025 appointees found, {appointment_check['unresolved_lookup_count']} identified judges still lack appointment dates, and {appointment_check['unknown_judge_p3_cases']} P3 cases still lack judge identification."
            )
        lines.append("")
    lines.append("## Limitations")
    lines.append("")
    lines.append("- Judge parsing depends on OCR quality in the raw opinion texts; district totals are more reliable than judge-name totals where signatures were badly scanned or where orders only exposed docket initials/section numbers.")
    lines.append("- The conservative max-possible single-judge share assumes all unresolved judge shortfall could collapse onto one judge; that is the correct bound for the >50% test, but it is intentionally worst-case rather than a point estimate.")
    lines.append("- Appointment-date coverage is now strongest for the judges occupying the largest identified shortfall shares; lower-impact magistrate names and judges without stable public biography pages still leave the all-judges census incomplete, and same-district multi-office biographies are treated conservatively as unresolved when the office-relevant appointment date cannot be isolated.")
    lines.append("- Because share-of-full-decline uses a full-circuit denominator, district and judge rows should not be added together and should not be read as exhausting the full decline even when an individual row exceeds 100%.")
    lines.append("- The appointment-lookup layer is partly path-dependent: if a prior deep-dive JSON exists in this workspace, the script reuses those resolved biographies before hitting live Wikipedia. That improves stability inside this repository but should be disclosed in replication notes.")
    lines.append("- Because the unified database has no district/judge variables, this output should be treated as a reproducible derived layer built on top of the structured database, not as native database fields.")
    lines.append("")
    return "\n".join(lines)


def load_cached_appointment_results(results_path: Path) -> Dict[str, dict]:
    if not results_path.exists():
        return {}
    try:
        payload = json.loads(results_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    cache: Dict[str, dict] = {}
    for detail in (payload.get("circuits") or {}).values():
        judges_block = detail.get("judges", {}) or {}
        judge_rows = judges_block.get("judge_rows", []) or []
        judge_district_map = {
            row.get("judge"): row.get("district")
            for row in judge_rows
            if row.get("judge") and row.get("district")
        }
        for judge, lookup in (judges_block.get("appointment_lookup", {}) or {}).items():
            if not isinstance(lookup, dict) or not judge:
                continue
            district = judge_district_map.get(judge)
            if district:
                cache[f"{judge}||{district}"] = lookup
            if lookup.get("status") == "resolved" and lookup.get("appointment_date"):
                cache[judge] = lookup
    return cache


def run_analysis(write_outputs: bool = True, emit_console: bool = True) -> dict:
    cases = load_database()
    disability = []
    for case in cases:
        if is_disability(case):
            period = period_of(case.get("year"))
            if period:
                cloned = dict(case)
                cloned["_period"] = period
                disability.append(cloned)

    top_circuits = select_top_decline_circuits(disability)
    raw_index = build_raw_text_index()
    initials_map, district_surname_map, global_surname_map = build_judge_reference_maps(raw_index)
    cached_results_path = Path(RESULTS_DIR) / "circuit_district_deep_dive_results.json"
    cached_appointment_results = load_cached_appointment_results(cached_results_path)
    appointment_lookup = WikipediaAppointmentLookup(seed_cache=cached_appointment_results)

    circuit_results = {}
    for row in top_circuits:
        circuit = row["circuit"]
        circuit_results[circuit] = analyze_circuit(
            circuit,
            disability,
            raw_index,
            initials_map,
            district_surname_map,
            global_surname_map,
            appointment_lookup,
        )

    output = {
        "dataset": {
            "total_cases": len(cases),
            "disability_screened_in_dated": len(disability),
            "periods": {"P1": "2013-2020", "P2": "2021-2022", "P3": "2023-2026"},
            "raw_text_dir": str(raw_text_dir()),
            "raw_text_indexed_files": len(raw_index),
        },
        "method": {
            "top_circuits_n": TOP_CIRCUITS_N,
            "broad_win_definition": ["PLAINTIFF_WIN", "MIXED"],
            "district_shortfall_definition": "expected P3 broad wins at the circuit's district-court P1 baseline minus actual P3 broad wins",
            "mtd_survival_definition": "share of P3 district-court MTD cases that are not coded DEFENDANT_WIN",
            "appointment_cutoff": APPOINTMENT_CUTOFF.isoformat(),
            "high_impact_full_circuit_shortfall_cutoff": HIGH_IMPACT_FULL_SHORTFALL_SHARE,
            "judge_name_canonicalization_policy": "Singleton surnames and OCR-fragment strings are counted as identified judges only when they can be confidently canonicalized to a fuller identity; otherwise they remain unresolved.",
            "share_of_full_shortfall_caveat": "District/judge shares of full-circuit shortfall are non-additive diagnostic ratios and may exceed 1.0 because the numerator is a district/judge shortfall while the denominator is the full-circuit shortfall, which also reflects non-district and offsetting components.",
            "appointment_lookup_sources": [
                "manual high-impact seeds and OCR corrections",
                "cached prior lookups that already record an office-relevant selection basis",
                "live Wikipedia lookup when needed",
            ],
            "appointment_lookup_rule": "Use an office-relevant appointment date when a single federal office can be tied to the judge's case district; otherwise leave the lookup unresolved.",
            "appointment_lookup_reproducibility_note": "Appointment lookup uses manual seeds first, then prior district-keyed lookup entries cached from results/circuit_district_deep_dive_results.json when present, and only then live Wikipedia lookups as needed.",
            "appointment_lookup_cache_seed_path": str(cached_results_path) if cached_results_path.exists() else None,
            "appointment_lookup_cache_seed_entries": len(cached_appointment_results),
        },
        "top_5_circuits_by_full_decline": top_circuits,
        "cross_circuit_findings": summarize_cross_circuit_findings(top_circuits, circuit_results),
        "circuits": circuit_results,
    }

    if write_outputs:
        json_path = Path(RESULTS_DIR) / "circuit_district_deep_dive_results.json"
        md_path = Path(RESULTS_DIR) / "circuit_district_deep_dive_analysis.md"
        json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(build_memo(output), encoding="utf-8")
        if emit_console:
            print(f"Saved JSON results to {json_path}")
            print(f"Saved memo to {md_path}")

    if emit_console:
        print("Top circuits:")
        for row in top_circuits:
            print(f"  {row['circuit']}: {row['delta_pp']:+.2f} pp")
    return output


def main() -> None:
    run_analysis(write_outputs=True, emit_console=True)


if __name__ == "__main__":
    main()
