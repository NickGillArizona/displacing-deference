"""Final stats extraction using the correct v4 unified RA database."""
import json
from collections import Counter, defaultdict

# v4 unified RA Database (2,366 records, same source_files as claims extraction)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\FHA_RA_Database_unified_20260328_090852.json", encoding="utf-8") as f:
    ra_v4 = json.load(f)

# RA claims extraction (pro_se data)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\recentcases\RAClassification_DB_claims_extraction.json", encoding="utf-8") as f:
    ra_claims = json.load(f)

# 3604 claims extraction (pro_se data)
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\3604\RAClassification_DB_3604_claims_extraction.json", encoding="utf-8") as f:
    s3604_claims = json.load(f)

print(f"RA v4 unified: {len(ra_v4)}")
print(f"RA claims: {len(ra_claims)}")
print(f"3604 claims: {len(s3604_claims)}")

# Check screening_result
screening = Counter(r.get("screening_result", "?") for r in ra_v4)
print(f"\nRA v4 screening_result: {dict(screening)}")

# Outcomes
outcomes = Counter(r.get("outcome", "?") for r in ra_v4)
print(f"RA v4 outcomes: {dict(outcomes)}")

# Build pro_se lookup from claims
claims_prose = {}
for r in ra_claims:
    sf = r.get("source_file", "")
    claims_prose[sf] = r.get("extraction", {}).get("pro_se")

# Match v4 records to claims and count pro_se
print("\n" + "=" * 70)
print("RA v4: PRO SE BY SCREENING STATUS")
print("=" * 70)

# FHA-relevant = screening_result != "?" and outcome != "?"
# Or maybe: screening_result = some specific value
# Let's see what screening values exist
fha_relevant = [r for r in ra_v4 if r.get("outcome", "?") != "?"]
print(f"\nFHA-relevant (outcome != '?'): {len(fha_relevant)}")

# Count pro_se for FHA-relevant
fha_prose = 0
fha_rep = 0
fha_no_match = 0
for r in fha_relevant:
    sf = r.get("source_file", "")
    ps = claims_prose.get(sf)
    if ps is True:
        fha_prose += 1
    elif ps is False:
        fha_rep += 1
    else:
        fha_no_match += 1

print(f"FHA-relevant pro se: {fha_prose}")
print(f"FHA-relevant represented: {fha_rep}")
print(f"FHA-relevant no match/unknown: {fha_no_match}")
fha_known = fha_prose + fha_rep
print(f"FHA-relevant pro se rate: {fha_prose}/{fha_known} = {fha_prose/fha_known*100:.1f}%")

# Count pro_se for ALL 2,366 records
all_prose = 0
all_rep = 0
all_no_match = 0
for r in ra_v4:
    sf = r.get("source_file", "")
    ps = claims_prose.get(sf)
    if ps is True:
        all_prose += 1
    elif ps is False:
        all_rep += 1
    else:
        all_no_match += 1

print(f"\nAll 2,366 RA records:")
print(f"Pro se: {all_prose}")
print(f"Represented: {all_rep}")
print(f"No match: {all_no_match}")
print(f"Pro se rate (all): {all_prose}/{all_prose+all_rep} = {all_prose/(all_prose+all_rep)*100:.1f}%")

# 3604 claims
s3604_prose = sum(1 for r in s3604_claims if r.get("extraction", {}).get("pro_se") is True)
s3604_rep = sum(1 for r in s3604_claims if r.get("extraction", {}).get("pro_se") is False)
s3604_unk = len(s3604_claims) - s3604_prose - s3604_rep
print(f"\n3604 unique (828):")
print(f"Pro se: {s3604_prose}")
print(f"Represented: {s3604_rep}")
print(f"Unknown: {s3604_unk}")
print(f"Pro se rate: {s3604_prose}/{s3604_prose+s3604_rep} = {s3604_prose/(s3604_prose+s3604_rep)*100:.1f}%")

# ============================================================
print("\n" + "=" * 70)
print("COMBINED PRO SE (for the note)")
print("=" * 70)

# Note says: RA Database v4 = 1,857
# FHA-relevant from v4 unified = those with outcome != "?"
# Let's see if that's 1,857
print(f"\nRA v4 FHA-relevant (outcome != '?'): {len(fha_relevant)}")
print(f"Note says RA v4 = 1,857")

# Maybe 1,857 includes some outcome='?' records?
# Let me check: 1,857 = total - 509 = 2,366 - 509
non_q = [r for r in ra_v4 if r.get("outcome", "?") != "?"]
print(f"2,366 - 509 = {2366 - 509} (close to 1,857)")
print(f"Actually: outcome != '?': {len(non_q)}")

# So 1,857 = 2,366 - 509 = 1,857. Yes!
# The 509 are the non-FHA records.
# So FHA-relevant RA = 1,857 records.

# FINAL COMPUTATION
print("\n" + "=" * 70)
print("FINAL PRO SE FIGURES")
print("=" * 70)

# RA FHA-relevant: fha_prose / (fha_prose + fha_rep) known
# 3604 unique: s3604_prose / (s3604_prose + s3604_rep) known
# Pilot: 2 / 44

combined_prose = fha_prose + s3604_prose + 2
combined_rep = fha_rep + s3604_rep + 42
combined_total = len(fha_relevant) + len(s3604_claims) + 44
combined_known = combined_prose + combined_rep

print(f"RA FHA-relevant: {fha_prose} pro se / {fha_known} known = {fha_prose/fha_known*100:.1f}%")
print(f"3604 unique: {s3604_prose} pro se / {s3604_prose+s3604_rep} known = {s3604_prose/(s3604_prose+s3604_rep)*100:.1f}%")
print(f"Pilot: 2 pro se / 44 known = 4.5%")
print(f"\nCombined: {combined_prose} pro se / {combined_known} known = {combined_prose/combined_known*100:.1f}%")
print(f"Combined total cases: {combined_total}")
print(f"Note's denominator: 2,410 (= 1,857 + 828 - ~275 overlap?... check)")
print(f"Note's claim: 1,369/2,410 = 56.8%")

# Actually: the note says unique = RA(1,857) + 3604(1,496) - overlap(987) + pilot(44) = 2,410
# The 3604 has 1,496 total, but only 828 are unique to 3604 (not in RA)
# So: 1,857 + 828 = 2,685 unique case files... but note says 2,410
# Wait: 1,857 + 1,496 - 987 = 2,366. Plus 44 pilot = 2,410.
# The 828 unique-to-3604 PLUS 668 overlap = 1,496 total 3604 cases
# The overlap cases have pro_se from BOTH databases
# For deduplicated count: use RA pro_se for overlap cases, 3604 pro_se for unique-to-3604

# So the pro_se for 2,410 unique cases would be:
# RA FHA-relevant (1,857): fha_prose
# 3604 unique-to-3604 (828): s3604_prose
# Pilot unique (44): 2
# But wait: 1,857 + 828 = 2,685, not 2,410-44 = 2,366

# The math: RA has 1,857 FHA-relevant out of 2,366 total
# 3604 has 1,496 total, overlap with RA is 987
# So unique-to-3604 = 1,496 - 987 = 509
# But the 3604 claims extraction has 828 records
# So 828 ≠ 509

# Let me check: maybe not all 828 are FHA-relevant
# If 828 = 1,661 (downloaded) - 833 (in RA source) = 828
# Then some of those 828 failed FHA screening too
# 1,496 FHA-relevant from 1,661 downloaded = 90.1% pass rate
# 987 overlap with RA (FHA-relevant)
# So unique-to-3604 FHA-relevant = 1,496 - 987 = 509
# If 828 total unique-to-3604 files, ~509 FHA-relevant + ~319 non-FHA

# For the note: pro se rate should be:
# RA FHA (1,857): fha_prose pro se
# 3604 unique FHA (~509): need to filter 828 to ~509 FHA-relevant
# Pilot (44): 2 pro se
# Total: ~2,410

# Without a 3604 screening file, I can approximate:
# If 90.1% of 3604 passed screening, ~746 of 828 would be FHA-relevant... but that's too high
# The actual count should be 509 (1,496 - 987 overlap)

print("\n" + "=" * 70)
print("ADJUSTED COMPUTATION (accounting for overlap)")
print("=" * 70)
print("RA FHA-relevant: 1,857 records")
print(f"  Pro se: {fha_prose}")
print(f"  Represented: {fha_rep}")
print(f"  Unknown: {fha_no_match}")

print(f"\n3604 unique-to-3604 (all 828, includes some non-FHA):")
print(f"  Pro se: {s3604_prose}")
print(f"  Represented: {s3604_rep}")

# Note's 2,410 = 1,857 + 509 + 44 = 2,410
# Or: 1,857 + 1,496 - 987 + 44 = 2,410
# The 509 FHA-relevant unique-to-3604 cases are a subset of the 828

# Best estimate: assume pro se rate among FHA-relevant 3604 unique
# is same as overall 3604 rate (33.6%)
# 509 * 33.6% = ~171 pro se
est_3604_prose = round(509 * s3604_prose / (s3604_prose + s3604_rep))
print(f"\nEstimated 3604 unique FHA-relevant pro se: ~{est_3604_prose} (of ~509)")

final_prose = fha_prose + est_3604_prose + 2
final_total = 1857 + 509 + 44  # = 2,410
print(f"\nFinal estimate: {final_prose} / {final_total} = {final_prose/final_total*100:.1f}%")
print(f"Note currently says: 1,369 / 2,410 = 56.8%")

# ============================================================
print("\n" + "=" * 70)
print("PLAINTIFF TYPE WIN RATES (RA v4 FHA-relevant)")
print("=" * 70)

pt_stats = defaultdict(lambda: {"total": 0, "pw": 0, "dw": 0, "mixed": 0})
for r in fha_relevant:
    pt = r.get("plaintiff_type", "UNKNOWN")
    outcome = r.get("outcome", "")
    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        pt_stats[pt]["total"] += 1
        if outcome == "PLAINTIFF_WIN": pt_stats[pt]["pw"] += 1
        elif outcome == "DEFENDANT_WIN": pt_stats[pt]["dw"] += 1
        elif outcome == "MIXED": pt_stats[pt]["mixed"] += 1

print(f"\n{'Plaintiff Type':<30} {'n':>5} {'PW':>5} {'DW':>5} {'MX':>5} {'Strict%':>8} {'Broad%':>8}")
print("-" * 75)
for pt in sorted(pt_stats.keys(), key=lambda x: pt_stats[x]["pw"]/max(pt_stats[x]["total"],1), reverse=True):
    s = pt_stats[pt]
    if s["total"] < 5:
        continue
    strict = s["pw"] / s["total"] * 100 if s["total"] > 0 else 0
    broad = (s["pw"] + s["mixed"]) / s["total"] * 100 if s["total"] > 0 else 0
    print(f"{pt:<30} {s['total']:>5} {s['pw']:>5} {s['dw']:>5} {s['mixed']:>5} {strict:>7.1f}% {broad:>7.1f}%")

# ============================================================
print("\n" + "=" * 70)
print("DEFENDANT TYPE WIN RATES (RA v4 FHA-relevant)")
print("=" * 70)

dt_stats = defaultdict(lambda: {"total": 0, "pw": 0, "dw": 0, "mixed": 0})
for r in fha_relevant:
    dt = r.get("defendant_type", "UNKNOWN")
    outcome = r.get("outcome", "")
    if outcome in ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED"):
        dt_stats[dt]["total"] += 1
        if outcome == "PLAINTIFF_WIN": dt_stats[dt]["pw"] += 1
        elif outcome == "DEFENDANT_WIN": dt_stats[dt]["dw"] += 1
        elif outcome == "MIXED": dt_stats[dt]["mixed"] += 1

print(f"\n{'Defendant Type':<35} {'n':>5} {'PW':>5} {'DW':>5} {'MX':>5} {'Strict%':>8} {'Broad%':>8}")
print("-" * 80)
for dt in sorted(dt_stats.keys(), key=lambda x: (dt_stats[x]["pw"]+dt_stats[x]["mixed"])/max(dt_stats[x]["total"],1), reverse=True):
    s = dt_stats[dt]
    if s["total"] < 10:
        continue
    strict = s["pw"] / s["total"] * 100 if s["total"] > 0 else 0
    broad = (s["pw"] + s["mixed"]) / s["total"] * 100 if s["total"] > 0 else 0
    print(f"{dt:<35} {s['total']:>5} {s['pw']:>5} {s['dw']:>5} {s['mixed']:>5} {strict:>7.1f}% {broad:>7.1f}%")
