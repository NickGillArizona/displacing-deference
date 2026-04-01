"""Get all final verified numbers for the note update."""
import json
from collections import defaultdict

# RA v4 unified (the authoritative RA Database)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\FHA_RA_Database_unified_20260328_090852.json", encoding="utf-8") as f:
    ra_v4 = json.load(f)

# RA claims extraction (has pro_se)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\RAClassification_DB_claims_extraction.json", encoding="utf-8") as f:
    ra_claims = json.load(f)

# 3604 claims extraction (has pro_se)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\RAClassification_DB_3604_claims_extraction.json", encoding="utf-8") as f:
    s3604_claims = json.load(f)

# 3604 unified DB
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\FHA_3604_Database_unified_20260328_104352.json", encoding="utf-8") as f:
    s3604_db = json.load(f)

# Build pro_se lookup from RA claims
ra_prose_map = {}
for r in ra_claims:
    sf = r.get("source_file", "")
    ra_prose_map[sf] = r.get("extraction", {}).get("pro_se")

# Build pro_se lookup from 3604 claims
s3604_prose_map = {}
for r in s3604_claims:
    sf = r.get("source_file", "")
    s3604_prose_map[sf] = r.get("extraction", {}).get("pro_se")

# RA v4 FHA-relevant
ra_fha = [r for r in ra_v4 if r.get("screening_result") == "YES"]

print("=" * 70)
print("1. DEFENDANT-TYPE WIN RATES (RA v4, FHA-relevant, n=1,857)")
print("=" * 70)

dt_stats = defaultdict(lambda: {"total": 0, "pw": 0, "dw": 0, "mixed": 0})
for r in ra_fha:
    dt = r.get("defendant_type", "?")
    outcome = r.get("outcome", "?")
    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        dt_stats[dt]["total"] += 1
        if outcome == "PLAINTIFF_WIN": dt_stats[dt]["pw"] += 1
        elif outcome == "DEFENDANT_WIN": dt_stats[dt]["dw"] += 1
        elif outcome == "MIXED": dt_stats[dt]["mixed"] += 1

print(f"{'Defendant Type':<30} {'n':>5} {'PW':>4} {'DW':>4} {'MX':>4} {'Strict':>7} {'Broad':>7}")
print("-" * 70)
for dt in sorted(dt_stats.keys(), key=lambda x: (dt_stats[x]["pw"]+dt_stats[x]["mixed"])/max(dt_stats[x]["total"],1), reverse=True):
    s = dt_stats[dt]
    if s["total"] < 5:
        continue
    strict = s["pw"] / s["total"] * 100
    broad = (s["pw"] + s["mixed"]) / s["total"] * 100
    print(f"{dt:<30} {s['total']:>5} {s['pw']:>4} {s['dw']:>4} {s['mixed']:>4} {strict:>6.1f}% {broad:>6.1f}%")

print("\n" + "=" * 70)
print("2. PRO SE RATE (FHA-relevant only)")
print("=" * 70)

# RA FHA-relevant pro se
ra_fha_prose = 0
ra_fha_rep = 0
for r in ra_fha:
    sf = r.get("source_file", "")
    ps = ra_prose_map.get(sf)
    if ps is True: ra_fha_prose += 1
    elif ps is False: ra_fha_rep += 1

print(f"RA FHA-relevant (n=1,857): {ra_fha_prose} pro se / {ra_fha_prose+ra_fha_rep} known = {ra_fha_prose/(ra_fha_prose+ra_fha_rep)*100:.1f}%")

# 3604 FHA-relevant pro se
# The 3604 claims has 828 unique-to-3604 files
# The 3604 DB has 1,496 screened YES out of 1,661
# Need to identify which of the 828 are screened YES
s3604_screened = set()
for r in s3604_db:
    if r.get("screening_result") == "YES":
        s3604_screened.add(r.get("source_file", ""))

# Check how many 3604 claims files are in the 3604 DB
s3604_fha_prose = 0
s3604_fha_rep = 0
s3604_fha_count = 0
s3604_not_in_db = 0
for r in s3604_claims:
    sf = r.get("source_file", "")
    if sf in s3604_screened:
        s3604_fha_count += 1
        ps = r.get("extraction", {}).get("pro_se")
        if ps is True: s3604_fha_prose += 1
        elif ps is False: s3604_fha_rep += 1
    else:
        s3604_not_in_db += 1

print(f"3604 unique FHA-relevant: {s3604_fha_count} of 828 claims files screened YES")
print(f"  Pro se: {s3604_fha_prose}, Represented: {s3604_fha_rep}")
if s3604_fha_prose + s3604_fha_rep > 0:
    print(f"  Rate: {s3604_fha_prose/(s3604_fha_prose+s3604_fha_rep)*100:.1f}%")
print(f"  Not in 3604 DB (overlap with RA or non-FHA): {s3604_not_in_db}")

# But wait - the 828 are supposed to be UNIQUE to 3604 (not in RA)
# The 3604 DB has 1,661 total, 1,496 screened YES
# Overlap with RA = 987
# So unique-to-3604 screened YES = 1,496 - 987 = 509
# Let me check: how many of the 828 claims files appear in the 3604 DB?
s3604_db_files = set(r.get("source_file", "") for r in s3604_db)
s3604_claims_files = set(r.get("source_file", "") for r in s3604_claims)
in_db = s3604_claims_files & s3604_db_files
print(f"\n3604 claims files found in 3604 DB: {len(in_db)} of {len(s3604_claims_files)}")

# Also check: how many 3604 DB files are in RA v4?
ra_files = set(r.get("source_file", "") for r in ra_v4)
s3604_in_ra = s3604_db_files & ra_files
print(f"3604 DB files also in RA v4: {len(s3604_in_ra)} (overlap)")

# Unique to 3604 and screened YES
s3604_unique_screened = set()
for r in s3604_db:
    sf = r.get("source_file", "")
    if r.get("screening_result") == "YES" and sf not in ra_files:
        s3604_unique_screened.add(sf)
print(f"3604 unique-to-3604 screened YES: {len(s3604_unique_screened)}")

# Pro se among unique-to-3604 screened YES
s3604_uniq_prose = 0
s3604_uniq_rep = 0
for sf in s3604_unique_screened:
    ps = s3604_prose_map.get(sf)
    if ps is True: s3604_uniq_prose += 1
    elif ps is False: s3604_uniq_rep += 1

s3604_uniq_known = s3604_uniq_prose + s3604_uniq_rep
print(f"  Pro se: {s3604_uniq_prose}, Represented: {s3604_uniq_rep}")
if s3604_uniq_known > 0:
    print(f"  Rate: {s3604_uniq_prose}/{s3604_uniq_known} = {s3604_uniq_prose/s3604_uniq_known*100:.1f}%")

# FINAL COMBINED
print(f"\n{'='*70}")
print("FINAL PRO SE COMPUTATION")
print("=" * 70)
total_prose = ra_fha_prose + s3604_uniq_prose + 2  # +2 from pilot
total_rep = ra_fha_rep + (s3604_uniq_known - s3604_uniq_prose) + 42  # +42 from pilot
total_known = total_prose + total_rep
total_cases = 1857 + len(s3604_unique_screened) + 44

print(f"RA FHA (1,857): {ra_fha_prose} pro se")
print(f"3604 unique FHA ({len(s3604_unique_screened)}): {s3604_uniq_prose} pro se")
print(f"Pilot (44): 2 pro se")
print(f"Total: {total_prose} pro se / {total_known} known")
print(f"Total cases: {total_cases}")
print(f"Pro se rate: {total_prose}/{total_known} = {total_prose/total_known*100:.1f}%")
print(f"Note's 2,410 denominator check: 1,857 + {len(s3604_unique_screened)} + 44 = {1857 + len(s3604_unique_screened) + 44}")

# Pro se win rates
print(f"\n{'='*70}")
print("3. PRO SE x OUTCOME (RA v4 FHA-relevant)")
print("=" * 70)
prose_wins = {"pw": 0, "dw": 0, "mixed": 0, "other": 0}
rep_wins = {"pw": 0, "dw": 0, "mixed": 0, "other": 0}

for r in ra_fha:
    sf = r.get("source_file", "")
    ps = ra_prose_map.get(sf)
    outcome = r.get("outcome", "?")

    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        bucket = prose_wins if ps is True else rep_wins if ps is False else None
        if bucket:
            if outcome == "PLAINTIFF_WIN": bucket["pw"] += 1
            elif outcome == "DEFENDANT_WIN": bucket["dw"] += 1
            elif outcome == "MIXED": bucket["mixed"] += 1

prose_decided = prose_wins["pw"] + prose_wins["dw"] + prose_wins["mixed"]
rep_decided = rep_wins["pw"] + rep_wins["dw"] + rep_wins["mixed"]

print(f"Pro se decided: {prose_decided}")
print(f"  PW={prose_wins['pw']} ({prose_wins['pw']/prose_decided*100:.1f}%), DW={prose_wins['dw']}, MX={prose_wins['mixed']}")
print(f"  Strict: {prose_wins['pw']/prose_decided*100:.1f}%, Broad: {(prose_wins['pw']+prose_wins['mixed'])/prose_decided*100:.1f}%")

print(f"Represented decided: {rep_decided}")
print(f"  PW={rep_wins['pw']} ({rep_wins['pw']/rep_decided*100:.1f}%), DW={rep_wins['dw']}, MX={rep_wins['mixed']}")
print(f"  Strict: {rep_wins['pw']/rep_decided*100:.1f}%, Broad: {(rep_wins['pw']+rep_wins['mixed'])/rep_decided*100:.1f}%")

# Total decided
total_decided = prose_decided + rep_decided
# Plus undecided outcomes
all_decided = sum(1 for r in ra_fha if r.get("outcome") in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"))
print(f"\nTotal decided (RA FHA): {all_decided}")
