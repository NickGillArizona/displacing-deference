"""
Kitagawa-Oaxaca-Blinder decomposition of the P1 -> P3 aggregate strict-win-rate
decline in disability FHA litigation, reproducing the headline in
note_empirical_v1 Section IV.A:

    "Kitagawa decomposition: composition-first ordering attributes 73 percent
     of the aggregate decline to shift in representation mix; rate-first
     ordering attributes 77 percent. Averaged: approximately 76 percent."

Period boundaries (from note Section III.A):
    P1 : 2022-01-01  <=  date_filed  <  2024-06-28
    P2 : 2024-06-28  <=  date_filed  <  2025-02-05
    P3 : 2025-02-05  <=  date_filed

Output: results/decomposition_results.json
"""
from __future__ import annotations

import sys
import json
import os
import warnings
from datetime import date

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import UNIFIED_DB_PATH, RESULTS_DIR

OUTPUT_PATH = os.path.join(RESULTS_DIR, "decomposition_results.json")

P1_START = date(2022, 1, 1)
P2_START = date(2024, 6, 28)
P3_START = date(2025, 2, 5)

EXCLUDED_OUTCOMES = {"PROCEDURAL", "SETTLEMENT", "UNDETERMINED"}


def load_disability_decided() -> pd.DataFrame:
    with open(UNIFIED_DB_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)

    rows = []
    for r in raw:
        if r.get("screening_result") != "YES":
            continue
        protected = r.get("protected_classes") or []
        if not (r.get("disability_alleged") or r.get("is_ra_case") or "disability" in protected):
            continue

        raw_date = r.get("date_filed")
        if not raw_date:
            continue
        try:
            d = date.fromisoformat(raw_date[:10])
        except ValueError:
            continue
        if d < P1_START:
            continue

        if d < P2_START:
            period = "P1"
        elif d < P3_START:
            period = "P2"
        else:
            period = "P3"

        outcome = r.get("outcome")
        if outcome in EXCLUDED_OUTCOMES or outcome is None:
            continue

        rows.append({
            "period": period,
            "pro_se": bool(r.get("pro_se")),
            "strict_win": int(outcome == "PLAINTIFF_WIN"),
            "broad_win": int(outcome in ("PLAINTIFF_WIN", "MIXED")),
        })

    return pd.DataFrame(rows)


def kitagawa_decomposition(a: pd.DataFrame, b: pd.DataFrame, outcome_col: str) -> dict:
    """Kitagawa (1955) decomposition of the change in mean outcome from period a
    to period b, where the population is stratified by representation status.

    Returns both orderings and their average, plus the component values.
    """
    sa_ps = a.loc[a.pro_se, outcome_col].mean() if a.pro_se.any() else 0.0
    sa_rep = a.loc[~a.pro_se, outcome_col].mean() if (~a.pro_se).any() else 0.0
    sb_ps = b.loc[b.pro_se, outcome_col].mean() if b.pro_se.any() else 0.0
    sb_rep = b.loc[~b.pro_se, outcome_col].mean() if (~b.pro_se).any() else 0.0
    wa_ps = a.pro_se.mean()
    wb_ps = b.pro_se.mean()

    mean_a = a[outcome_col].mean()
    mean_b = b[outcome_col].mean()
    total_delta = mean_b - mean_a

    # Composition-first ordering: hold rates at a, shift weights from a to b
    comp_first_composition = (wb_ps - wa_ps) * (sa_ps - sa_rep)
    comp_first_rate = wb_ps * (sb_ps - sa_ps) + (1 - wb_ps) * (sb_rep - sa_rep)

    # Rate-first ordering: hold weights at a, shift rates from a to b
    rate_first_rate = wa_ps * (sb_ps - sa_ps) + (1 - wa_ps) * (sb_rep - sa_rep)
    rate_first_composition = (wb_ps - wa_ps) * (sb_ps - sb_rep)

    # Averages (symmetric / path-independent)
    avg_composition = 0.5 * (comp_first_composition + rate_first_composition)
    avg_rate = 0.5 * (comp_first_rate + rate_first_rate)

    def pct_share(part: float) -> float:
        if abs(total_delta) < 1e-12:
            return float("nan")
        return part / total_delta

    return {
        "period_a_mean": mean_a,
        "period_b_mean": mean_b,
        "total_delta": total_delta,
        "subgroup_rates": {
            "a_pro_se": sa_ps,
            "a_represented": sa_rep,
            "b_pro_se": sb_ps,
            "b_represented": sb_rep,
        },
        "subgroup_weights": {
            "a_pro_se_share": wa_ps,
            "b_pro_se_share": wb_ps,
        },
        "composition_first": {
            "composition_component": comp_first_composition,
            "rate_component": comp_first_rate,
            "composition_share": pct_share(comp_first_composition),
            "rate_share": pct_share(comp_first_rate),
        },
        "rate_first": {
            "composition_component": rate_first_composition,
            "rate_component": rate_first_rate,
            "composition_share": pct_share(rate_first_composition),
            "rate_share": pct_share(rate_first_rate),
        },
        "average": {
            "composition_component": avg_composition,
            "rate_component": avg_rate,
            "composition_share": pct_share(avg_composition),
            "rate_share": pct_share(avg_rate),
        },
    }


def oaxaca_blinder(a: pd.DataFrame, b: pd.DataFrame, outcome_col: str) -> dict:
    """Oaxaca-Blinder decomposition of the mean-outcome change using the
    two-group binary covariate pro_se. This is the linear-regression analogue
    of the Kitagawa decomposition above and should agree on the signed shares.
    """
    # Using reference = period a for rate-first
    sa_ps = a.loc[a.pro_se, outcome_col].mean() if a.pro_se.any() else 0.0
    sa_rep = a.loc[~a.pro_se, outcome_col].mean() if (~a.pro_se).any() else 0.0
    sb_ps = b.loc[b.pro_se, outcome_col].mean() if b.pro_se.any() else 0.0
    sb_rep = b.loc[~b.pro_se, outcome_col].mean() if (~b.pro_se).any() else 0.0
    wa_ps = a.pro_se.mean()
    wb_ps = b.pro_se.mean()

    # Endowments (composition) effect at period-a coefficients:
    endowments_a_coef = (wb_ps - wa_ps) * sa_ps + ((1 - wb_ps) - (1 - wa_ps)) * sa_rep
    # Coefficients (rate) effect at period-b endowments:
    coefficients_b_endow = wb_ps * (sb_ps - sa_ps) + (1 - wb_ps) * (sb_rep - sa_rep)
    # Interaction term (for reference):
    interaction = (wb_ps - wa_ps) * (sb_ps - sa_ps) + ((1 - wb_ps) - (1 - wa_ps)) * (sb_rep - sa_rep)

    total_delta = (b[outcome_col].mean()) - (a[outcome_col].mean())

    def pct_share(part: float) -> float:
        if abs(total_delta) < 1e-12:
            return float("nan")
        return part / total_delta

    return {
        "endowments_effect_a_coef": endowments_a_coef,
        "coefficients_effect_b_endow": coefficients_b_endow,
        "interaction_term": interaction,
        "total_delta": total_delta,
        "composition_share_a_coef": pct_share(endowments_a_coef),
        "rate_share_b_endow": pct_share(coefficients_b_endow),
    }


def fmt_pct(x: float) -> str:
    return f"{x:.4f}" if np.isfinite(x) else "nan"


def main() -> None:
    df = load_disability_decided()
    print(f"Decided, dated disability cases: {len(df)}")
    for p in ("P1", "P2", "P3"):
        sub = df[df.period == p]
        print(f"  {p}: n={len(sub)}, strict_win={sub.strict_win.mean():.4f}, "
              f"pro_se_share={sub.pro_se.mean():.4f}")

    results = {
        "metadata": {
            "period_boundaries": {
                "P1": ["2022-01-01", "2024-06-27"],
                "P2": ["2024-06-28", "2025-02-04"],
                "P3": ["2025-02-05", "endpoint"],
            },
            "excluded_outcomes": sorted(EXCLUDED_OUTCOMES),
            "stratification_variable": "pro_se",
            "unified_db_path": UNIFIED_DB_PATH,
        },
        "decompositions": {},
    }

    for p_from, p_to in [("P1", "P3"), ("P1", "P2"), ("P2", "P3")]:
        a = df[df.period == p_from]
        b = df[df.period == p_to]
        if len(a) == 0 or len(b) == 0:
            continue

        print(f"\n{'='*70}")
        print(f"Kitagawa decomposition: {p_from} -> {p_to}, outcome=strict_win")
        print("="*70)

        kit = kitagawa_decomposition(a, b, "strict_win")
        print(f"  {p_from} mean: {kit['period_a_mean']:.4f}")
        print(f"  {p_to} mean: {kit['period_b_mean']:.4f}")
        print(f"  Total delta: {kit['total_delta']:.4f}")
        print(f"  Composition-first: composition={fmt_pct(kit['composition_first']['composition_share'])}, "
              f"rate={fmt_pct(kit['composition_first']['rate_share'])}")
        print(f"  Rate-first:        composition={fmt_pct(kit['rate_first']['composition_share'])}, "
              f"rate={fmt_pct(kit['rate_first']['rate_share'])}")
        print(f"  Averaged:          composition={fmt_pct(kit['average']['composition_share'])}, "
              f"rate={fmt_pct(kit['average']['rate_share'])}")

        ob = oaxaca_blinder(a, b, "strict_win")
        print(f"  Oaxaca-Blinder (endowments at {p_from} coef): "
              f"composition={fmt_pct(ob['composition_share_a_coef'])}")
        print(f"  Oaxaca-Blinder (coefficients at {p_to} endow): "
              f"rate={fmt_pct(ob['rate_share_b_endow'])}")

        results["decompositions"][f"{p_from}_to_{p_to}"] = {
            "outcome": "strict_win",
            "kitagawa": kit,
            "oaxaca_blinder": ob,
        }

    # Also run the broad-win decomposition for P1 -> P3 since the note cites both
    print(f"\n{'='*70}")
    print("Kitagawa decomposition: P1 -> P3, outcome=broad_win")
    print("="*70)
    a = df[df.period == "P1"]
    b = df[df.period == "P3"]
    kit_broad = kitagawa_decomposition(a, b, "broad_win")
    print(f"  Total delta: {kit_broad['total_delta']:.4f}")
    print(f"  Averaged: composition={fmt_pct(kit_broad['average']['composition_share'])}, "
          f"rate={fmt_pct(kit_broad['average']['rate_share'])}")

    results["decompositions"]["P1_to_P3_broad"] = {
        "outcome": "broad_win",
        "kitagawa": kit_broad,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
