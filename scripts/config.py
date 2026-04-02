"""
Centralized path configuration for all analysis scripts.

To run on your machine, either:
  1. Set the FHA_DATA_DIR environment variable to the directory containing
     the database JSON files, OR
  2. Place the database files in the repo's data/ directory (the default).

Required database files:
  - FHA_Unified_Database.json           (primary: 1,720 disability cases)
  - FHA_3604_Database_unified_*.json    (2015 FHA Database, § 3604(f) cases)
  - FHA_RA_Database_unified_*.json      (RA Database, all protected classes)
"""
import os
import glob

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_DEFAULT_DATA_DIR = os.path.join(_REPO_ROOT, "data")

DATA_DIR = os.environ.get("FHA_DATA_DIR", _DEFAULT_DATA_DIR)

# Primary database
UNIFIED_DB_PATH = os.path.join(DATA_DIR, "FHA_Unified_Database.json")

# Source databases (names include timestamps; resolve via glob)
def _find(pattern):
    matches = glob.glob(os.path.join(DATA_DIR, pattern))
    return matches[0] if matches else os.path.join(DATA_DIR, pattern)

DB_3604_PATH = _find("FHA_3604_Database_unified_*.json")
DB_RA_PATH = _find("FHA_RA_Database_unified_*.json")

# Resolved RA database (positional bias analysis)
DB_RA_RESOLVED_PATH = _find("RAClassification_DB_resolved_*.json")

# Case directory (contains individual case JSON files for opinion text)
CASE_DIR = os.environ.get("FHA_CASE_DIR", os.path.join(DATA_DIR, "cases"))

# Output directories
RESULTS_DIR = os.path.join(_REPO_ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
