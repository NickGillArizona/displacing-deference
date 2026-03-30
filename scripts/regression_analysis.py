"""
Multivariate Logistic Regression Analysis
==========================================
Replicates the regression models reported in Appendix A-3, Section B.

Requires: statsmodels, json
Input: Unified dataset JSON (N=3,193 cases, 6,718 claims)

Models:
  Model 1: Strict win (DV: 1=PLAINTIFF_WIN, 0=DEFENDANT_WIN or MIXED)
  Model 2: Broad win (DV: 1=PLAINTIFF_WIN or MIXED, 0=DEFENDANT_WIN)
  Models 5-6: Interaction models (post_LB x procedural_posture, post_LB x IP)

Independent Variables:
  - post_loper_bright (1 if year >= 2024, 0 otherwise)
  - procedural_posture (dummy: MTD reference)
  - defendant_type (dummy: PRIVATE_LANDLORD reference)
  - accommodation_type (dummy: DISCRIMINATION_PRIMARY reference)
  - interactive_process_discussed (binary)
  - delay_as_denial (binary)
  - race_mentioned (binary)
  - plaintiff_type (dummy: INDIVIDUAL_TENANT reference)

Analysis conducted March 28, 2026.
Libraries: json, math, collections, statsmodels
"""

import json
import sys
from collections import Counter

try:
    import statsmodels.api as sm
    import numpy as np
except ImportError:
    print("This script requires statsmodels and numpy.")
    print("Install with: pip install statsmodels numpy")
    sys.exit(1)


def load_dataset(filepath: str) -> list:
    """Load the unified dataset JSON."""
    with open(filepath) as f:
        return json.load(f)


def create_dummies(data: list, field: str, reference: str) -> dict:
    """Create dummy variables for a categorical field."""
    values = set(r.get(field, "OTHER") for r in data) - {reference}
    return {
        f"{field}_{v}": [1 if r.get(field) == v else 0 for r in data]
        for v in sorted(values)
    }


def build_regression_data(records: list, broad: bool = False):
    """
    Build X and y arrays for logistic regression.

    Args:
        records: List of case records with canonical fields
        broad: If True, DV = PLAINTIFF_WIN or MIXED; if False, DV = PLAINTIFF_WIN only
    """
    # Filter to decided cases
    decided = [r for r in records if r.get("outcome") in
               ("PLAINTIFF_WIN", "DEFENDANT_WIN", "MIXED")]

    if broad:
        y = [1 if r["outcome"] in ("PLAINTIFF_WIN", "MIXED") else 0 for r in decided]
    else:
        y = [1 if r["outcome"] == "PLAINTIFF_WIN" else 0 for r in decided]

    # Independent variables
    X_data = {
        "post_loper_bright": [1 if r.get("year", 0) >= 2024 else 0 for r in decided],
        "interactive_process": [1 if r.get("interactive_process_discussed") == "YES" else 0
                               for r in decided],
        "delay_as_denial": [1 if r.get("delay_as_denial") == "YES" else 0
                           for r in decided],
        "race_mentioned": [1 if r.get("race_mentioned") == "YES" else 0
                          for r in decided],
    }

    # Add dummy variables
    for field, ref in [
        ("procedural_posture", "MOTION_TO_DISMISS"),
        ("defendant_type", "PRIVATE_LANDLORD"),
        ("accommodation_type", "DISCRIMINATION_PRIMARY"),
        ("plaintiff_type", "INDIVIDUAL_TENANT"),
    ]:
        dummies = create_dummies(decided, field, ref)
        X_data.update(dummies)

    X = np.column_stack([X_data[k] for k in sorted(X_data.keys())])
    X = sm.add_constant(X)

    return np.array(y), X, sorted(X_data.keys())


def run_model(records: list, broad: bool = False, label: str = ""):
    """Run logistic regression and print results."""
    y, X, names = build_regression_data(records, broad)

    model = sm.Logit(y, X)
    result = model.fit(disp=0)

    print(f"\n{'='*60}")
    print(f"Model: {label}")
    print(f"N = {len(y)}, Events = {sum(y)}")
    print(f"Pseudo R-squared: {result.prsquared:.4f}")
    print(f"{'='*60}")

    print(f"\n{'Variable':<40} {'OR':>8} {'p-value':>10} {'95% CI':>20}")
    print("-" * 80)

    params = result.params
    pvalues = result.pvalues
    conf = result.conf_int()

    for i, name in enumerate(["const"] + names):
        or_val = np.exp(params[i])
        p = pvalues[i]
        ci_lo = np.exp(conf[i][0])
        ci_hi = np.exp(conf[i][1])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"{name:<40} {or_val:>8.3f} {p:>10.4f} [{ci_lo:.3f}, {ci_hi:.3f}] {sig}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python regression_analysis.py <unified_dataset.json>")
        print()
        print("The unified dataset JSON should contain an array of case records")
        print("with canonical fields including: outcome, year, procedural_posture,")
        print("defendant_type, accommodation_type, interactive_process_discussed,")
        print("delay_as_denial, race_mentioned, plaintiff_type.")
        sys.exit(1)

    records = load_dataset(sys.argv[1])
    print(f"Loaded {len(records)} records")

    # Model 1: Strict win
    run_model(records, broad=False, label="Model 1: Strict Win (PW only)")

    # Model 2: Broad win
    run_model(records, broad=True, label="Model 2: Broad Win (PW + MIXED)")
