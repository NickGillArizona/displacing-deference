"""Extract pro se stats, capability gap stats, and defendant-type stats from databases."""
import json
from collections import Counter, defaultdict

# Load databases
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\Unified_Claims_Extraction.json", encoding="utf-8") as f:
    unified = json.load(f)

with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\RAClassification_DB_dualmodel_confirmed.json", encoding="utf-8") as f:
    ra_db = json.load(f)

# ============================================================
# SECTION 1: PRO SE ANALYSIS (Unified DB)
# ============================================================
print("=" * 70)
print("SECTION 1: PRO SE ANALYSIS (Unified Claims Extraction)")
print("=" * 70)

# Count by database source
by_source = defaultdict(lambda: {"total": 0, "pro_se": 0, "represented": 0, "unknown": 0})
total_prose = 0
total_rep = 0
total_unknown = 0

for r in unified:
    ext = r.get("extraction", {})
    src = r.get("database_source", "unknown")
    by_source[src]["total"] += 1

    ps = ext.get("pro_se")
    if ps is True:
        by_source[src]["pro_se"] += 1
        total_prose += 1
    elif ps is False:
        by_source[src]["represented"] += 1
        total_rep += 1
    else:
        by_source[src]["unknown"] += 1
        total_unknown += 1

print(f"\nTotal records: {len(unified)}")
print(f"  Pro se: {total_prose}")
print(f"  Represented: {total_rep}")
print(f"  Unknown: {total_unknown}")
print(f"  Pro se rate: {total_prose}/{total_prose + total_rep} = {total_prose/(total_prose+total_rep)*100:.1f}%")

print(f"\nBy database source:")
for src, counts in sorted(by_source.items()):
    known = counts["pro_se"] + counts["represented"]
    rate = counts["pro_se"] / known * 100 if known > 0 else 0
    print(f"  {src}: n={counts['total']}, pro_se={counts['pro_se']}, rep={counts['represented']}, unk={counts['unknown']}, rate={rate:.1f}%")

# ============================================================
# SECTION 2: PLAINTIFF TYPE WIN RATES (RA DB - has outcome field)
# ============================================================
print("\n" + "=" * 70)
print("SECTION 2: PLAINTIFF TYPE WIN RATES (RA Database)")
print("=" * 70)

pt_stats = defaultdict(lambda: {"total": 0, "pw": 0, "dw": 0, "mixed": 0, "other": 0})

for r in ra_db:
    pt = r.get("plaintiff_type", "UNKNOWN")
    outcome = r.get("outcome", "UNKNOWN")

    # Only count decided outcomes
    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        pt_stats[pt]["total"] += 1
        if outcome == "PLAINTIFF_WIN":
            pt_stats[pt]["pw"] += 1
        elif outcome == "DEFENDANT_WIN":
            pt_stats[pt]["dw"] += 1
        elif outcome == "MIXED":
            pt_stats[pt]["mixed"] += 1

print(f"\nPlaintiff Type Win Rates (decided cases only):")
print(f"{'Plaintiff Type':<30} {'n':>5} {'PW':>5} {'DW':>5} {'MX':>5} {'Strict%':>8} {'Broad%':>8}")
print("-" * 75)
for pt in sorted(pt_stats.keys(), key=lambda x: pt_stats[x]["pw"]/max(pt_stats[x]["total"],1), reverse=True):
    s = pt_stats[pt]
    strict = s["pw"] / s["total"] * 100 if s["total"] > 0 else 0
    broad = (s["pw"] + s["mixed"]) / s["total"] * 100 if s["total"] > 0 else 0
    print(f"{pt:<30} {s['total']:>5} {s['pw']:>5} {s['dw']:>5} {s['mixed']:>5} {strict:>7.1f}% {broad:>7.1f}%")

# ============================================================
# SECTION 3: DEFENDANT TYPE WIN RATES (RA DB)
# ============================================================
print("\n" + "=" * 70)
print("SECTION 3: DEFENDANT TYPE WIN RATES (RA Database)")
print("=" * 70)

dt_stats = defaultdict(lambda: {"total": 0, "pw": 0, "dw": 0, "mixed": 0})

for r in ra_db:
    dt = r.get("defendant_type", "UNKNOWN")
    outcome = r.get("outcome", "UNKNOWN")

    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        dt_stats[dt]["total"] += 1
        if outcome == "PLAINTIFF_WIN":
            dt_stats[dt]["pw"] += 1
        elif outcome == "DEFENDANT_WIN":
            dt_stats[dt]["dw"] += 1
        elif outcome == "MIXED":
            dt_stats[dt]["mixed"] += 1

print(f"\nDefendant Type Win Rates (decided, n>=10):")
print(f"{'Defendant Type':<35} {'n':>5} {'PW':>5} {'DW':>5} {'MX':>5} {'Strict%':>8} {'Broad%':>8}")
print("-" * 80)
for dt in sorted(dt_stats.keys(), key=lambda x: (dt_stats[x]["pw"]+dt_stats[x]["mixed"])/max(dt_stats[x]["total"],1), reverse=True):
    s = dt_stats[dt]
    if s["total"] < 10:
        continue
    strict = s["pw"] / s["total"] * 100 if s["total"] > 0 else 0
    broad = (s["pw"] + s["mixed"]) / s["total"] * 100 if s["total"] > 0 else 0
    print(f"{dt:<35} {s['total']:>5} {s['pw']:>5} {s['dw']:>5} {s['mixed']:>5} {strict:>7.1f}% {broad:>7.1f}%")

# ============================================================
# SECTION 4: PRO SE x OUTCOME (Unified DB - need outcome from RA)
# ============================================================
print("\n" + "=" * 70)
print("SECTION 4: PRO SE x OUTCOME")
print("=" * 70)

# Build lookup from RA DB by source_file
ra_by_file = {}
for r in ra_db:
    sf = r.get("source_file", "")
    ra_by_file[sf] = r

prose_outcome = {"total": 0, "pw": 0, "dw": 0, "mixed": 0}
rep_outcome = {"total": 0, "pw": 0, "dw": 0, "mixed": 0}

for r in unified:
    ext = r.get("extraction", {})
    ps = ext.get("pro_se")
    sf = r.get("source_file", r.get("custom_id", ""))

    # Try to get outcome from RA DB
    ra_rec = ra_by_file.get(sf)
    if ra_rec:
        outcome = ra_rec.get("outcome", "")
    else:
        # Try extraction for outcome
        outcome = ext.get("outcome", "")

    if outcome not in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        continue

    if ps is True:
        prose_outcome["total"] += 1
        if outcome == "PLAINTIFF_WIN": prose_outcome["pw"] += 1
        elif outcome == "DEFENDANT_WIN": prose_outcome["dw"] += 1
        elif outcome == "MIXED": prose_outcome["mixed"] += 1
    elif ps is False:
        rep_outcome["total"] += 1
        if outcome == "PLAINTIFF_WIN": rep_outcome["pw"] += 1
        elif outcome == "DEFENDANT_WIN": rep_outcome["dw"] += 1
        elif outcome == "MIXED": rep_outcome["mixed"] += 1

print(f"\nPro Se outcomes (matched to RA DB):")
for label, stats in [("Pro Se", prose_outcome), ("Represented", rep_outcome)]:
    if stats["total"] > 0:
        strict = stats["pw"] / stats["total"] * 100
        broad = (stats["pw"] + stats["mixed"]) / stats["total"] * 100
        print(f"  {label}: n={stats['total']}, PW={stats['pw']}, DW={stats['dw']}, MX={stats['mixed']}, Strict={strict:.1f}%, Broad={broad:.1f}%")
    else:
        print(f"  {label}: no matched outcomes")

# ============================================================
# SECTION 5: TOTAL DECIDED CASES
# ============================================================
print("\n" + "=" * 70)
print("SECTION 5: TOTAL DECIDED CASES ACROSS DATABASES")
print("=" * 70)

decided_ra = sum(1 for r in ra_db if r.get("outcome") in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"))
total_ra = len(ra_db)
print(f"RA DB: {decided_ra} decided out of {total_ra} total")

# Count outcomes in RA DB
ra_outcomes = Counter(r.get("outcome", "UNKNOWN") for r in ra_db)
print(f"RA outcome distribution: {dict(ra_outcomes)}")
