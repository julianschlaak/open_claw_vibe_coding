#!/usr/bin/env python3
"""Extract higher-level drought products from monthly drought indices."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import gamma, genextreme, kendalltau, percentileofscore, theilslopes

BASE = Path(__file__).resolve().parents[2]
RESULTS = BASE / "analysis" / "results"


@dataclass
class DomainPaths:
    monthly: Path
    out_dir: Path


def get_paths(domain: str) -> DomainPaths:
    out_dir = RESULTS / domain
    return DomainPaths(monthly=out_dir / "monthly_drought_indices.csv", out_dir=out_dir)


def _safe_read_monthly(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    df = pd.read_csv(path)
    required = {"date", "smi_percent"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    return df


def detect_events(df: pd.DataFrame) -> pd.DataFrame:
    smi = df["smi_percent"].to_numpy(float)
    dates = df["date"].to_numpy()

    events: List[dict] = []
    i = 0
    eid = 1
    n = len(df)

    while i < n:
        if smi[i] < 20:
            j = i
            while j < n and smi[j] < 20:
                j += 1
            run_len = j - i
            if run_len >= 2:
                segment = smi[i:j]
                end_date = pd.Timestamp(dates[j - 1])

                # recovery months until SMI > 40 after drought end
                rec = 0
                k = j
                while k < n:
                    rec += 1
                    if smi[k] > 40:
                        break
                    k += 1
                if k >= n and (n == 0 or smi[-1] <= 40):
                    rec = int(max(0, n - j))

                deficits = 20.0 - segment
                events.append(
                    {
                        "event_id": f"E{eid:03d}",
                        "start_date": pd.Timestamp(dates[i]).strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "duration_months": int(run_len),
                        "min_smi": float(np.min(segment)),
                        "avg_smi": float(np.mean(segment)),
                        "severity_score": float(np.sum(deficits)),
                        "max_intensity": float(np.max(deficits)),
                        "recovery_months": int(rec),
                    }
                )
                eid += 1
            i = j
        else:
            i += 1

    return pd.DataFrame(events)


def _return_levels_for_minima(arr: np.ndarray, years: List[int]) -> Dict[str, float]:
    arr = arr[np.isfinite(arr)]
    if len(arr) < 4:
        return {f"value_{y}yr": np.nan for y in years}

    out = {}
    shift = float(np.min(arr))
    pos = arr - shift + 1e-6

    # Gamma lower tail with empirical fallback for numerical edge cases.
    try:
        a, loc, scale = gamma.fit(pos, floc=0)
        for y in years:
            p = 1.0 / y
            q = gamma.ppf(p, a, loc=loc, scale=scale) + shift - 1e-6
            out[f"value_{y}yr"] = float(q)
    except Exception:
        for y in years:
            p = 1.0 / y
            out[f"value_{y}yr"] = float(np.quantile(arr, p))
    return out


def _return_levels_gev_min(arr: np.ndarray, years: List[int]) -> Dict[str, float]:
    arr = arr[np.isfinite(arr)]
    if len(arr) < 4:
        return {f"value_{y}yr": np.nan for y in years}

    out = {}
    x = -arr  # convert minima to maxima
    try:
        c, loc, scale = genextreme.fit(x)
        for y in years:
            p = 1.0 / y
            q_max = genextreme.ppf(1.0 - p, c, loc=loc, scale=scale)
            out[f"value_{y}yr"] = float(-q_max)
    except Exception:
        for y in years:
            p = 1.0 / y
            out[f"value_{y}yr"] = float(np.quantile(arr, p))
    return out


def calc_return_periods(df: pd.DataFrame) -> pd.DataFrame:
    years = [2, 5, 10, 20, 50, 100]

    annual_smi_min = df.groupby("year")["smi_percent"].min().to_numpy(float)

    discharge_col = "qsim_monthly_mean" if "qsim_monthly_mean" in df.columns else "discharge_percent"
    annual_q_min = df.groupby("year")[discharge_col].min().to_numpy(float)

    rows = []
    row = {"metric": "smi_min_gamma"}
    row.update(_return_levels_for_minima(annual_smi_min, years))
    rows.append(row)

    row = {"metric": "smi_min_gev"}
    row.update(_return_levels_gev_min(annual_smi_min, years))
    rows.append(row)

    row = {"metric": "discharge_min_gamma"}
    row.update(_return_levels_for_minima(annual_q_min, years))
    rows.append(row)

    row = {"metric": "discharge_min_gev"}
    row.update(_return_levels_gev_min(annual_q_min, years))
    rows.append(row)

    return pd.DataFrame(rows)


def calc_seasonal_stats(df: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    n_all_events = max(1, len(events))

    event_start_month = pd.to_datetime(events["start_date"]).dt.month if not events.empty else pd.Series(dtype=int)
    event_end_month = pd.to_datetime(events["end_date"]).dt.month if not events.empty else pd.Series(dtype=int)

    for m in range(1, 13):
        sub = df[df["month"] == m]
        avg_smi = float(sub["smi_percent"].mean()) if not sub.empty else np.nan
        drought_frequency = float((sub["smi_percent"] < 20).mean() * 100.0) if not sub.empty else np.nan

        if not events.empty:
            dur = events[event_start_month == m]["duration_months"]
            avg_duration = float(dur.mean()) if len(dur) else 0.0
            early_start_pct = float((event_start_month == m).sum() / n_all_events * 100.0)
            late_end_pct = float((event_end_month == m).sum() / n_all_events * 100.0)
        else:
            avg_duration = 0.0
            early_start_pct = 0.0
            late_end_pct = 0.0

        rows.append(
            {
                "month": m,
                "avg_smi": avg_smi,
                "drought_frequency": drought_frequency,
                "avg_duration": avg_duration,
                "early_start_pct": early_start_pct,
                "late_end_pct": late_end_pct,
            }
        )

    return pd.DataFrame(rows)


def _trend_row(name: str, values: np.ndarray, step_per_decade: float) -> dict:
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values)
    values = values[valid]
    if len(values) < 5:
        return {
            "metric": name,
            "mann_kendall_tau": np.nan,
            "p_value": np.nan,
            "sens_slope": np.nan,
            "trend_per_decade": np.nan,
            "significance": "insufficient_data",
        }

    x = np.arange(len(values), dtype=float)
    tau, p = kendalltau(x, values)
    slope = theilslopes(values, x, 0.95).slope
    trend_dec = slope * step_per_decade
    sig = "significant" if p < 0.05 else "not_significant"

    return {
        "metric": name,
        "mann_kendall_tau": float(tau),
        "p_value": float(p),
        "sens_slope": float(slope),
        "trend_per_decade": float(trend_dec),
        "significance": sig,
    }


def calc_trend_analysis(df: pd.DataFrame) -> pd.DataFrame:
    annual = df.groupby("year", as_index=False).agg(
        smi_mean=("smi_percent", "mean"),
        drought_frequency=("smi_percent", lambda s: float((s < 20).mean() * 100.0)),
        intensity=("smi_percent", lambda s: float(np.sum(np.maximum(0.0, 20.0 - s.to_numpy(float))))),
    )

    rows = [
        _trend_row("SMI", df["smi_percent"].to_numpy(float), step_per_decade=120.0),
        _trend_row("drought_frequency", annual["drought_frequency"].to_numpy(float), step_per_decade=10.0),
        _trend_row("intensity", annual["intensity"].to_numpy(float), step_per_decade=10.0),
    ]
    return pd.DataFrame(rows)


def calc_current_ranking(df: pd.DataFrame, ret_df: pd.DataFrame) -> dict:
    latest = df.sort_values("date").iloc[-1]
    current_date = pd.Timestamp(latest["date"]) 
    current_smi = float(latest["smi_percent"])

    smi_all = df["smi_percent"].to_numpy(float)
    rank = int(np.sum(smi_all <= current_smi))
    percentile = float(percentileofscore(smi_all, current_smi, kind="rank"))

    years_drier = sorted(df.loc[df["smi_percent"] < current_smi, "year"].unique().tolist())
    years_drier_str = [str(int(y)) for y in years_drier]

    annual_min = df.groupby("year")["smi_percent"].min().to_numpy(float)
    n_years = len(annual_min)
    n_drier = max(1, int(np.sum(annual_min <= current_smi)))
    rp_emp = max(1, int(round(n_years / n_drier)))

    return {
        "current_month": current_date.strftime("%Y-%m"),
        "current_smi": round(current_smi, 3),
        "rank_driest": rank,
        "percentile": round(percentile, 1),
        "years_with_drier": years_drier_str,
        "return_period": f"1-in-{rp_emp}-years",
    }


def calc_forecast_warning(df: pd.DataFrame) -> dict:
    sub = df.sort_values("date").tail(6).copy()
    if sub.empty:
        return {
            "current_status": "unknown",
            "lead_time_months": 0,
            "probability": 0.0,
            "basis": "No data",
            "recommended_action": "Check data pipeline",
        }

    rech = float(sub["recharge_percent"].tail(3).mean()) if "recharge_percent" in sub.columns else 50.0
    smi = sub["smi_percent"].to_numpy(float)
    slope = float(theilslopes(smi, np.arange(len(smi))).slope) if len(smi) >= 3 else 0.0

    risk = 0.35
    basis_parts = []
    if rech < 30:
        risk += 0.2
        basis_parts.append("Low recharge")
    if slope < -1.0:
        risk += 0.2
        basis_parts.append("SMI trend down")
    if float(sub["smi_percent"].iloc[-1]) < 20:
        risk += 0.15
        basis_parts.append("Current SMI very low")

    risk = min(0.95, max(0.05, risk))
    if risk >= 0.6:
        status = "warning"
        action = "Monitor closely"
        lead = 2
    elif risk >= 0.45:
        status = "watch"
        action = "Increase observation frequency"
        lead = 2
    else:
        status = "normal"
        action = "Routine monitoring"
        lead = 1

    return {
        "current_status": status,
        "lead_time_months": lead,
        "probability": round(float(risk), 3),
        "basis": " + ".join(basis_parts) if basis_parts else "Stable conditions",
        "recommended_action": action,
    }


def run(domain: str) -> None:
    paths = get_paths(domain)
    paths.out_dir.mkdir(parents=True, exist_ok=True)

    df = _safe_read_monthly(paths.monthly)

    events = detect_events(df)
    events.to_csv(paths.out_dir / "drought_events.csv", index=False)

    ret = calc_return_periods(df)
    ret.to_csv(paths.out_dir / "return_periods.csv", index=False)

    seasonal = calc_seasonal_stats(df, events)
    seasonal.to_csv(paths.out_dir / "seasonal_stats.csv", index=False)

    trend = calc_trend_analysis(df)
    trend.to_csv(paths.out_dir / "trend_analysis.csv", index=False)

    ranking = calc_current_ranking(df, ret)
    (paths.out_dir / "current_ranking.json").write_text(json.dumps(ranking, indent=2) + "\n", encoding="utf-8")

    warning = calc_forecast_warning(df)
    (paths.out_dir / "forecast_warning.json").write_text(json.dumps(warning, indent=2) + "\n", encoding="utf-8")

    print(f"[{domain}] done: events={len(events)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract drought products.")
    parser.add_argument("--domain", required=True, choices=["catchment_custom", "test_domain"])
    args = parser.parse_args()
    run(args.domain)


if __name__ == "__main__":
    main()
