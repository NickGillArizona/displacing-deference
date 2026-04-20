"""
Bootstrap confidence intervals for the headline decomposition numbers reported
in note_empirical_v1 Section V.A:

    "All reported period comparisons also survive a 10,000-resample bootstrap
     (seed 42) that preserves period assignment and representation status."

Periods are keyed to the two external shocks cited in note_empirical_v1 Section III.A:
    P1 : 2022-01-01  <=  date_filed  <  2024-06-28   (pre-Loper Bright baseline)
    P2 : 2024-06-28  <=  date_filed  <  2025-02-05   (transition)
    P3 : 2025-02-05  <=  date_filed                  (post-withdrawal)

Date boundaries:
    * 2024-06-28 = Loper Bright Enters. v. Raimondo decided
    * 2025-02-05 = HUD enforcement withdrawal

Output: results/bootstrap_ci_results.json

The bootstrap resamples decided dated cases with replacement (same N per period)
and recomputes: aggregate strict-win rate; represented strict-win rate; pro se
share; and the Kitagawa composition share. Reports 2.5 / 50 / 97.5 percentiles.
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

OUTPUT_PATH = os.path.join(RESULTS_DIR, "bootstrap_ci_results.json")

N_RESAMPLES = 10_000
SEED = 42

P1_START = date(2022, 1, 1)
P2_START = date(2024, 6, 28)
P3_START = date(2025, 2, 5)

EXCLUDED_OUTCOMES = {"PROCEDURAL", "SETTLEMENT", "UNDETERMINED"}


def load_disability_cases() -> pd.DataFrame:
    with open(UNIFIED_DB_PATH, encoding="utf-8") as fh:
        raw = json.load(fh)

    def is_disability(r: dict) -> bool:
        if r.get("screening_result") != "YES":
            return False
        if r.get("disability_alleged") or r.get("is_ra_case"):
            return True
        protected = r.get("protected_classes") or []
        return "disability" in protected

    cases = [r for r in raw if is_disability(r)]

    rows = []
    for r in cases:
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
            "date_filed": d,
            "period": period,
            "outcome": outcome,
            "strict_win": int(outcome == "PLAINTIFF_WIN"),
            "broad_win": int(outcome in ("PLAINTIFF_WIN", "MIXED")),
            "pro_se": bool(r.get("pro_se")),
        })

    return pd.DataFrame(rows)


def point_estimates(df: pd.DataFrame) -> dict:
    out = {}
    for p in ("P1", "P2", "P3"):
        sub = df[df.period == p]
        rep = sub[~sub.pro_se]
        ps = sub[sub.pro_se]
        out[p] = {
            "n": int(len(sub)),
            "strict_win_rate": float(sub.strict_win.mean()) if len(sub) else float("nan"),
            "broad_win_rate": float(sub.broad_win.mean()) if len(sub) else float("nan"),
            "pro_se_share": float(sub.pro_se.mean()) if len(sub) else float("nan"),
            "represented_strict_win": float(rep.strict_win.mean()) if len(rep) else float("nan"),
            "represented_broad_win": float(rep.broad_win.mean()) if len(rep) else float("nan"),
            "pro_se_strict_win": float(ps.strict_win.mean()) if len(ps) else float("nan"),
            "n_represented": int(len(rep)),
            "n_pro_se": int(len(ps)),
        }
    return out


def kitagawa_composition(df: pd.DataFrame, p_from: str = "P1", p_to: str = "P3") -> float:
    """Fraction of the aggregate strict-win-rate change from p_from to p_to attributable
    to composition (representation-mix) change, averaging composition-first and rate-first
    orderings.
    """
    a = df[df.period == p_from]
    b = df[df.period == p_to]

    if len(a) == 0 or len(b) == 0:
        return float("nan")

    agg_delta = b.strict_win.mean() - a.strict_win.mean()
    if abs(agg_delta) < 1e-12:
        return float("nan")

    sa_rep = a[~a.pro_se].strict_win.mean() if (~a.pro_se).any() else 0.0
    sa_ps = a[a.pro_se].strict_win.mean() if a.pro_se.any() else 0.0
    sb_rep = b[~b.pro_se].strict_win.mean() if (~b.pro_se).any() else 0.0
    sb_ps = b[b.pro_se].strict_win.mean() if b.pro_se.any() else 0.0
    wa_ps = a.pro_se.mean()
    wb_ps = b.pro_se.mean()

    # Composition-first: hold rates at period-a, shift weights to period-b
    comp_first = (wb_ps - wa_ps) * (sa_ps - sa_rep)
    # Rate-first: hold rates at period-b, shift weights to period-b
    rate_first = (wb_ps - wa_ps) * (sb_ps - sb_rep)
    comp_avg = 0.5 * (comp_first + rate_first)

    return float(comp_avg / agg_delta)


def percentile_ci(samples: np.ndarray, low: float = 2.5, high: float = 97.5) -> tuple[float, float, float]:
    arr = np.asarray(samples)
    arr = arr[~np.isnan(arr)]
    if arr.size == 0:
        return (float("nan"), float("nan"), float("nan"))
    return (float(np.percentile(arr, low)),
            float(np.percentile(arr, 50)),
            float(np.percentile(arr, high)))


def run_bootstrap(df: pd.DataFrame, n_resamples: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)

    # Pre-index rows by period for faster resampling
    period_indices = {p: df.index[df.period == p].to_numpy() for p in ("P1", "P2", "P3")}

    draws: dict[str, list[float]] = {
        "P1_strict_win_rate": [], "P2_strict_win_rate": [], "P3_strict_win_rate": [],
        "P1_pro_se_share":    [], "P2_pro_se_share":    [], "P3_pro_se_share":    [],
        "P1_represented_strict_win": [], "P3_represented_strict_win": [],
        "P1_pro_se_strict_win":      [], "P3_pro_se_strict_win":      [],
        "composition_share_P1_to_P3": [],
    }

    for _ in range(n_resamples):
        resampled_parts = []
        for p in ("P1", "P2", "P3"):
            idx = period_indices[p]
            if idx.size == 0:
                continue
            chosen = rng.choice(idx, size=idx.size, replace=True)
            resampled_parts.append(df.loc[chosen])
        sample = pd.concat(resampled_parts, ignore_index=True)

        ests = point_estimates(sample)
        for p in ("P1", "P2", "P3"):
            draws[f"{p}_strict_win_rate"].append(ests[p]["strict_win_rate"])
            draws[f"{p}_pro_se_share"].append(ests[p]["pro_se_share"])
        draws["P1_represented_strict_win"].append(ests["P1"]["represented_strict_win"])
        draws["P3_represented_strict_win"].append(ests["P3"]["represented_strict_win"])
        draws["P1_pro_se_strict_win"].append(ests["P1"]["pro_se_strict_win"])
        draws["P3_pro_se_strict_win"].append(ests["P3"]["pro_se_strict_win"])
        draws["composition_share_P1_to_P3"].append(kitagawa_composition(sample))

    cis = {}
    for key, samples in draws.items():
        arr = np.asarray(samples)
        lo, med, hi = percentile_ci(arr)
        cis[key] = {
            "p2_5": lo,
            "median": med,
            "p97_5": hi,
            "mean": float(np.nanmean(arr)),
            "std": float(np.nanstd(arr, ddof=1)),
            "n_valid": int(np.sum(~np.isnan(arr))),
        }
    return cis


def main() -> None:
    print(f"Loading data from {UNIFIED_DB_PATH}")
    df = load_disability_cases()
    print(f"Decided, dated disability cases: {len(df)}")
    print(f"  P1 (2022-01-01 to 2024-06-27): {(df.period == 'P1').sum()}")
    print(f"  P2 (2024-06-28 to 2025-02-04): {(df.period == 'P2').sum()}")
    print(f"  P3 (2025-02-05 onward):        {(df.period == 'P3').sum()}")

    point = point_estimates(df)
    print("\nPoint estimates:")
    for p in ("P1", "P2", "P3"):
        ests = point[p]
        print(f"  {p}: n={ests['n']}, strict_win={ests['strict_win_rate']:.3f}, "
              f"pro_se_share={ests['pro_se_share']:.3f}, "
              f"rep_strict_win={ests['represented_strict_win']:.3f}")

    comp_point = kitagawa_composition(df)
    print(f"\nKitagawa composition share P1->P3: {comp_point:.3f}")

    print(f"\nRunning bootstrap: n_resamples={N_RESAMPLES}, seed={SEED}")
    cis = run_bootstrap(df, N_RESAMPLES, SEED)

    print("\n95% percentile CIs:")
    for key, ci in cis.items():
        print(f"  {key:>32}: [{ci['p2_5']:.4f}, {ci['p97_5']:.4f}] "
              f"median={ci['median']:.4f} n={ci['n_valid']}")

    out = {
        "metadata": {
            "n_resamples": N_RESAMPLES,
            "seed": SEED,
            "period_boundaries": {
                "P1": ["2022-01-01", "2024-06-27"],
                "P2": ["2024-06-28", "2025-02-04"],
                "P3": ["2025-02-05", "endpoint"],
            },
            "excluded_outcomes": sorted(EXCLUDED_OUTCOMES),
            "unified_db_path": UNIFIED_DB_PATH,
        },
        "point_estimates_by_period": point,
        "composition_share_P1_to_P3_point": comp_point,
        "bootstrap_ci": cis,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False, default=str)
    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
