#!/usr/bin/env python3
"""
Master replication script for:
  Displacing Deference: Data and Doctrine for a Disability-Centered AFFH

Runs the full analysis pipeline in order, checking prerequisites first.
Usage:
    python run_all.py                # run everything
    python run_all.py --litigation-only   # Group 1 only
    python run_all.py --pums-only         # Group 2 only
"""
import sys
import os
import subprocess
import argparse
import glob
import importlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.environ.get("FHA_DATA_DIR", os.path.join(REPO_ROOT, "data"))

BANNER = """
================================================================================
  Displacing Deference -- Full Replication Pipeline
================================================================================
  This script runs every analysis script in the correct order and reports
  success or failure for each step.

  Data directory : {data_dir}
  Python         : {python}
================================================================================
"""

# ── database checks ──────────────────────────────────────────────────────────

REQUIRED_FILES = [
    ("FHA_Unified_Database.json", False),          # exact name
    ("FHA_3604_Database_unified_*.json", True),     # glob
    ("FHA_RA_Database_unified_*.json", True),       # glob
]

REQUIRED_PACKAGES = ["pandas", "numpy", "statsmodels", "requests", "scipy"]

GROUP_1 = [
    "recompute_all_appendices.py",
    "recompute_stats_unified.py",
    "regression_analysis.py",
    "regression_analysis_full.py",
    "robustness_checks.py",
    "cdbg_analysis.py",
    "posh_analysis.py",
    "reac_analysis.py",
]

GROUP_2 = [
    "census_pums_replication.py",
    "pums_costburden_analysis.py",
    "pums_cb_se.py",
    "pums_housing_stock_analysis.py",
    "pums_dis1_sensitivity.py",
]


def check_databases():
    """Return True if all required database files are present."""
    ok = True
    for pattern, is_glob in REQUIRED_FILES:
        if is_glob:
            matches = glob.glob(os.path.join(DATA_DIR, pattern))
            if not matches:
                print(f"  [MISSING] {pattern}  (no match in {DATA_DIR})")
                ok = False
            else:
                print(f"  [  OK   ] {matches[0]}")
        else:
            path = os.path.join(DATA_DIR, pattern)
            if os.path.isfile(path):
                print(f"  [  OK   ] {path}")
            else:
                print(f"  [MISSING] {path}")
                ok = False
    return ok


def check_packages():
    """Return True if all required Python packages can be imported."""
    ok = True
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
            print(f"  [  OK   ] {pkg}")
        except ImportError:
            print(f"  [MISSING] {pkg}  -- install with: pip install {pkg}")
            ok = False
    return ok


def run_script(name):
    """Run a single script via subprocess. Returns 'success', 'failure', or 'skipped'."""
    path = os.path.join(SCRIPT_DIR, name)
    if not os.path.isfile(path):
        print(f"  [{name}] SKIPPED -- file not found")
        return "skipped"

    print(f"  [{name}] running ...", end="", flush=True)
    result = subprocess.run(
        [sys.executable, path],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(" OK")
        return "success"
    else:
        print(" FAILED (exit code {})".format(result.returncode))
        if result.stderr:
            for line in result.stderr.strip().splitlines()[-5:]:
                print(f"    | {line}")
        return "failure"


def main():
    parser = argparse.ArgumentParser(description="Run full replication pipeline.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--litigation-only", action="store_true",
                       help="Run only Group 1 (litigation analysis)")
    group.add_argument("--pums-only", action="store_true",
                       help="Run only Group 2 (Census PUMS)")
    args = parser.parse_args()

    print(BANNER.format(data_dir=DATA_DIR, python=sys.executable))

    # ── prerequisite checks ──────────────────────────────────────────────
    print("Checking database files ...")
    db_ok = check_databases()
    print()
    print("Checking Python packages ...")
    pkg_ok = check_packages()
    print()

    if not db_ok:
        print("ERROR: One or more required database files are missing.")
        print("       Place them in the data/ directory or set FHA_DATA_DIR.")
        sys.exit(1)
    if not pkg_ok:
        print("ERROR: One or more required packages are not installed.")
        sys.exit(1)

    # ── determine which scripts to run ───────────────────────────────────
    scripts = []
    if args.pums_only:
        print("Running Group 2 only (Census PUMS)\n")
        scripts = GROUP_2
    elif args.litigation_only:
        print("Running Group 1 only (Litigation Analysis)\n")
        scripts = GROUP_1
    else:
        print("Running all scripts\n")
        scripts = GROUP_1 + GROUP_2

    # ── execute ──────────────────────────────────────────────────────────
    counts = {"success": 0, "failure": 0, "skipped": 0}
    for name in scripts:
        status = run_script(name)
        counts[status] += 1

    # ── summary ──────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print(f"  DONE  --  {counts['success']} succeeded, "
          f"{counts['failure']} failed, {counts['skipped']} skipped")
    print("=" * 60)

    sys.exit(1 if counts["failure"] > 0 else 0)


if __name__ == "__main__":
    main()
