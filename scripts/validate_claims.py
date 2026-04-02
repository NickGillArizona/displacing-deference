#!/usr/bin/env python3
"""
Validate key statistics reported in the note against the database.

Loads FHA_Unified_Database.json and checks counts, win rates, and
pro-se rates against the values cited in the article.
"""
import json
import sys
import os
from datetime import datetime

# ── paths ────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import UNIFIED_DB_PATH, DB_RA_PATH

# ── period boundaries ────────────────────────────────────────────────────────
P1_START = datetime(2022, 1, 1)
P1_END   = datetime(2024, 6, 28)
P2_END   = datetime(2025, 2, 5)
# P3 = everything after P2_END

DECIDED = {"PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"}

TOLERANCE_PP = 0.5  # percentage-point tolerance for rate comparisons


def load_db(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(s[:10], fmt)
        except ValueError:
            continue
    return None


def is_disability(case):
    classes = case.get("protected_classes", [])
    if isinstance(classes, list):
        return any("disability" in c.lower() for c in classes)
    if isinstance(classes, str):
        return "disability" in classes.lower()
    return False


def get_period(case):
    d = parse_date(case.get("date_filed") or case.get("decision_date") or "")
    if d is None:
        return None
    if d < P1_START:
        return None
    if d < P1_END:
        return "P1"
    if d < P2_END:
        return "P2"
    return "P3"


def strict_win_rate(cases):
    decided = [c for c in cases if c.get("outcome") in DECIDED]
    if not decided:
        return 0.0, 0
    wins = sum(1 for c in decided if c.get("outcome") == "PLAINTIFF_WIN")
    return (wins / len(decided)) * 100.0, len(decided)


def pro_se_rate(cases):
    if not cases:
        return 0.0
    pro_se = sum(1 for c in cases
                 if str(c.get("pro_se", "")).lower() in ("true", "yes", "1")
                 or c.get("pro_se") is True)
    return (pro_se / len(cases)) * 100.0


def main():
    print("Loading database:", UNIFIED_DB_PATH)
    db = load_db(UNIFIED_DB_PATH)
    if isinstance(db, dict):
        db = list(db.values())

    # Also load RA database for total FHA count
    ra_cases = []
    if os.path.isfile(DB_RA_PATH):
        ra_cases = load_db(DB_RA_PATH)
        if isinstance(ra_cases, dict):
            ra_cases = list(ra_cases.values())

    # The unified DB contains ~3,198 records; "screened-in FHA cases" are those
    # with a non-empty outcome field (2,522).
    fha_cases = [c for c in db if c.get("outcome") not in (None, "", "?")]
    disability_cases = [c for c in fha_cases if is_disability(c)]

    # Split disability cases by period
    p1 = [c for c in disability_cases if get_period(c) == "P1"]
    p2 = [c for c in disability_cases if get_period(c) == "P2"]
    p3 = [c for c in disability_cases if get_period(c) == "P3"]

    p1_wr, p1_n = strict_win_rate(p1)
    p2_wr, p2_n = strict_win_rate(p2)
    p3_wr, p3_n = strict_win_rate(p3)

    pro_se_all = pro_se_rate(disability_cases)
    pro_se_p3  = pro_se_rate(p3)

    # ── claims ───────────────────────────────────────────────────────────
    claims = [
        ("Total FHA cases",       2522,  len(fha_cases),  0,             "count"),
        ("Disability cases",      1720,  len(disability_cases), 1,       "count"),
        ("P1 strict win rate %",  18.0,  p1_wr,           TOLERANCE_PP,  "pct"),
        ("P2 strict win rate %",   7.8,  p2_wr,           TOLERANCE_PP,  "pct"),
        ("P3 strict win rate %",  10.7,  p3_wr,           TOLERANCE_PP,  "pct"),
        ("P1 decided n",          456,   p1_n,            0,             "count"),
        ("P2 decided n",          116,   p2_n,            0,             "count"),
        ("P3 decided n",          317,   p3_n,            1,             "count"),
        ("Pro se overall %",      60.0,  pro_se_all,      2.0,          "pct"),
        ("Pro se P3 %",           76.7,  pro_se_p3,       TOLERANCE_PP,  "pct"),
    ]

    passes = 0
    fails  = 0

    print()
    print(f"{'CLAIM':<25} {'EXPECTED':>10} {'ACTUAL':>10}  RESULT")
    print("-" * 60)

    for label, expected, actual, tol, kind in claims:
        if kind == "pct":
            exp_s = f"{expected:.1f}%"
            act_s = f"{actual:.1f}%"
            ok = abs(expected - actual) <= tol
        else:
            exp_s = str(expected)
            act_s = str(actual)
            ok = abs(expected - actual) <= tol

        status = "PASS" if ok else "FAIL"
        if ok:
            passes += 1
        else:
            fails += 1
        print(f"  {label:<23} {exp_s:>10} {act_s:>10}  {status}")

    print("-" * 60)
    print(f"  {passes} passed, {fails} failed out of {passes + fails} claims")
    print()

    sys.exit(1 if fails > 0 else 0)


if __name__ == "__main__":
    main()
