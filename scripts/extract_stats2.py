"""Reconcile pro se counts with the 2,410 unique case figure."""
import json
from collections import Counter

# Load databases
with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\Unified_Claims_Extraction.json", encoding="utf-8") as f:
    unified = json.load(f)

with open(r"C:\Users\nickg\IdeaProjects\MFH-Java-Work\allFHAcases\RAClassification_DB_dualmodel_confirmed.json", encoding="utf-8") as f:
    ra_db = json.load(f)

# The unified extraction has 3,194 records: 2,366 RA + 828 3604
# But the note says:
#   RA Database v4 = 1,857 FHA-relevant cases
#   3604 Database = 1,496 FHA-relevant cases
#   Overlap = ~987
#   Unique = ~2,410 (including 44 pilot)
#
# Question: how does 2,366 RA records relate to 1,857 FHA-relevant?
# And how does 828 3604 records relate to 1,496?

print("=" * 70)
print("UNIFIED EXTRACTION STRUCTURE")
print("=" * 70)

# Check which RA records are FHA-relevant
# The unified extraction has "disability_alleged" and "is_ra_case" fields
ra_records = [r for r in unified if r.get("database_source") == "RA"]
s3604_records = [r for r in unified if r.get("database_source") == "3604"]

print(f"RA source records: {len(ra_records)}")
print(f"3604 source records: {len(s3604_records)}")

# Check disability_alleged and is_ra_case distributions
ra_disability = Counter(r.get("extraction", {}).get("disability_alleged") for r in ra_records)
ra_is_ra = Counter(r.get("extraction", {}).get("is_ra_case") for r in ra_records)
print(f"\nRA source - disability_alleged: {dict(ra_disability)}")
print(f"RA source - is_ra_case: {dict(ra_is_ra)}")

s3604_disability = Counter(r.get("extraction", {}).get("disability_alleged") for r in s3604_records)
s3604_is_ra = Counter(r.get("extraction", {}).get("is_ra_case") for r in s3604_records)
print(f"\n3604 source - disability_alleged: {dict(s3604_disability)}")
print(f"3604 source - is_ra_case: {dict(s3604_is_ra)}")

# Now check RA DB (the classified database) - it has 3,419 records
# How many are FHA-relevant? Check outcomes
ra_outcomes = Counter(r.get("outcome", "UNKNOWN") for r in ra_db)
print(f"\nRA DB (classified) outcome distribution:")
for k, v in sorted(ra_outcomes.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Check primary_protected_class
ra_ppc = Counter(r.get("primary_protected_class", "UNKNOWN") for r in ra_db)
print(f"\nRA DB primary_protected_class:")
for k, v in sorted(ra_ppc.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# What does "1,857" correspond to?
# Maybe it's decided + procedural + settlement (excluding UNKNOWN and NOT_FHA)?
fha_relevant = [r for r in ra_db if r.get("outcome") not in ("UNKNOWN", "UNDETERMINED - NOT AN FHA CASE")]
print(f"\nRA DB FHA-relevant (outcome != UNKNOWN/NOT_FHA): {len(fha_relevant)}")

# Or maybe excluding UNKNOWN only
not_unknown = [r for r in ra_db if r.get("outcome") != "UNKNOWN"]
print(f"RA DB outcome != UNKNOWN: {len(not_unknown)}")

print("\n" + "=" * 70)
print("PRO SE RATES BY FHA-RELEVANCE FILTER")
print("=" * 70)

# Pro se rate for RA source, all records
ra_prose_all = sum(1 for r in ra_records if r.get("extraction", {}).get("pro_se") is True)
ra_rep_all = sum(1 for r in ra_records if r.get("extraction", {}).get("pro_se") is False)
print(f"\nRA source ALL: {ra_prose_all} pro se / {ra_prose_all + ra_rep_all} known = {ra_prose_all/(ra_prose_all+ra_rep_all)*100:.1f}%")

# Pro se rate for RA source, disability_alleged=True only
ra_dis = [r for r in ra_records if r.get("extraction", {}).get("disability_alleged") is True]
ra_prose_dis = sum(1 for r in ra_dis if r.get("extraction", {}).get("pro_se") is True)
ra_rep_dis = sum(1 for r in ra_dis if r.get("extraction", {}).get("pro_se") is False)
print(f"RA source disability_alleged=True: n={len(ra_dis)}, {ra_prose_dis} pro se / {ra_prose_dis + ra_rep_dis} known = {ra_prose_dis/(ra_prose_dis+ra_rep_dis)*100:.1f}%")

# Pro se rate for RA source, is_ra_case=True only
ra_ra = [r for r in ra_records if r.get("extraction", {}).get("is_ra_case") is True]
ra_prose_ra = sum(1 for r in ra_ra if r.get("extraction", {}).get("pro_se") is True)
ra_rep_ra = sum(1 for r in ra_ra if r.get("extraction", {}).get("pro_se") is False)
print(f"RA source is_ra_case=True: n={len(ra_ra)}, {ra_prose_ra} pro se / {ra_prose_ra + ra_rep_ra} known = {ra_prose_ra/(ra_prose_ra+ra_rep_ra)*100:.1f}%")

# 3604 source
s3604_prose = sum(1 for r in s3604_records if r.get("extraction", {}).get("pro_se") is True)
s3604_rep = sum(1 for r in s3604_records if r.get("extraction", {}).get("pro_se") is False)
print(f"\n3604 source ALL: {s3604_prose} pro se / {s3604_prose + s3604_rep} known = {s3604_prose/(s3604_prose+s3604_rep)*100:.1f}%")

# Combined (RA all + 3604 all + pilot)
total_prose = ra_prose_all + s3604_prose + 2  # 2 from pilot
total_known = (ra_prose_all + ra_rep_all) + (s3604_prose + s3604_rep) + 44  # 44 pilot
print(f"\nCombined (all unified + pilot): {total_prose} pro se / {total_known} known = {total_prose/total_known*100:.1f}%")

# The note's original claim: 1,367/2,366 = 57.8%
# What does 1,367 correspond to?
print(f"\nNote's original: 1,367 pro se / 2,366 total = 57.8%")
print(f"RA source all: {ra_prose_all} pro se / {len(ra_records)} total = {ra_prose_all/len(ra_records)*100:.1f}%")
print(f"Match? {ra_prose_all == 1367}")
