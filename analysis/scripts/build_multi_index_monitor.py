#!/usr/bin/env python3
"""Build multi-index drought monitor datasets for dashboard_vnext.

Implements SPI, SPEI, SMI plus validation metrics and consistency scores.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import fisk, gamma, norm

BASE = Path(__file__).resolve().parents[2]
RESULTS = BASE / "analysis" / "results"
OUT_PUBLIC = BASE / "dashboard_vnext" / "public" / "data"


@dataclass
class ValidationMetrics:
    kge: float
    kge_r: float
    kge_alpha: float
    kge_beta: float
    nse: float
    rmse: float
    mae: float
    bias: float
    peak_error: float
    timing_error_days: float


def classify_index(v: float | None) -> str:
    if v is None or not np.isfinite(v):
        return "unknown"
    if v >= 2.0:
        return "extremely_wet"
    if v >= 1.5:
        return "severely_wet"
    if v >= 1.0:
        return "moderately_wet"
    if v > -1.0:
        return "near_normal"
    if v > -1.5:
        return "moderate_drought"
    if v > -2.0:
        return "severe_drought"
    return "extreme_drought"


def _rolling_sum(s: pd.Series, scale: int) -> pd.Series:
    return s.rolling(window=scale, min_periods=scale).sum()


def calc_spi(precip: pd.Series, scale: int) -> pd.Series:
    agg = _rolling_sum(precip.clip(lower=0), scale)
    valid = agg.dropna()
    out = pd.Series(np.nan, index=precip.index, dtype=float)
    if len(valid) < 12:
        return out

    x = valid.to_numpy(float)
    x = np.where(x <= 0, 1e-3, x)
    try:
        a, loc, scale_p = gamma.fit(x, floc=0)
        cdf = gamma.cdf(x, a, loc=loc, scale=scale_p)
    except Exception:
        ranks = pd.Series(x).rank(method="average").to_numpy(float)
        cdf = ranks / (len(x) + 1.0)

    cdf = np.clip(cdf, 1e-6, 1 - 1e-6)
    spi = norm.ppf(cdf)
    out.loc[valid.index] = spi
    return out


def calc_spei(precip: pd.Series, pet: pd.Series, scale: int) -> pd.Series:
    wb = precip - pet
    agg = _rolling_sum(wb, scale)
    valid = agg.dropna()
    out = pd.Series(np.nan, index=precip.index, dtype=float)
    if len(valid) < 12:
        return out

    x = valid.to_numpy(float)
    shift = float(np.min(x))
    xp = x - shift + 1e-3

    try:
        c, loc, sc = fisk.fit(xp, floc=0)
        cdf = fisk.cdf(xp, c, loc=loc, scale=sc)
    except Exception:
        ranks = pd.Series(x).rank(method="average").to_numpy(float)
        cdf = ranks / (len(x) + 1.0)

    cdf = np.clip(cdf, 1e-6, 1 - 1e-6)
    spei = norm.ppf(cdf)
    out.loc[valid.index] = spei
    return out


def calc_smi(smi_percent: pd.Series) -> pd.Series:
    # SMI = (percentile - 0.5) * 4 ; percentile in [0,1]
    p = smi_percent.astype(float) / 100.0
    return (p - 0.5) * 4.0


def calc_validation(daily: pd.DataFrame) -> ValidationMetrics:
    v = daily[["qobs", "qsim"]].dropna()
    if v.empty:
        return ValidationMetrics(*(float("nan") for _ in range(10)))

    obs = v["qobs"].to_numpy(float)
    sim = v["qsim"].to_numpy(float)

    r = np.corrcoef(obs, sim)[0, 1] if len(v) > 1 else np.nan
    std_obs, std_sim = np.std(obs), np.std(sim)
    mu_obs, mu_sim = np.mean(obs), np.mean(sim)

    alpha = std_sim / std_obs if std_obs != 0 else np.nan
    beta = mu_sim / mu_obs if mu_obs != 0 else np.nan
    kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

    nse_den = np.sum((obs - mu_obs) ** 2)
    nse = 1 - np.sum((obs - sim) ** 2) / nse_den if nse_den != 0 else np.nan

    rmse = float(np.sqrt(np.mean((obs - sim) ** 2)))
    mae = float(np.mean(np.abs(obs - sim)))
    bias = float((mu_sim - mu_obs) / mu_obs * 100) if mu_obs != 0 else np.nan

    # Peak error: top 5% flow mean difference
    q95 = np.quantile(obs, 0.95)
    obs_peak = obs[obs >= q95]
    sim_peak = sim[obs >= q95]
    peak_error = float((np.mean(sim_peak) - np.mean(obs_peak)) / np.mean(obs_peak) * 100) if len(obs_peak) else np.nan

    # Timing error: lag maximizing cross-correlation in +/- 31 days
    max_lag = min(31, len(obs) // 3)
    best_lag = 0
    best_corr = -np.inf
    obs_d = obs - np.mean(obs)
    sim_d = sim - np.mean(sim)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            x, y = obs_d[-lag:], sim_d[: len(sim_d) + lag]
        elif lag > 0:
            x, y = obs_d[: len(obs_d) - lag], sim_d[lag:]
        else:
            x, y = obs_d, sim_d
        if len(x) < 10:
            continue
        c = np.corrcoef(x, y)[0, 1]
        if np.isfinite(c) and c > best_corr:
            best_corr = c
            best_lag = lag

    return ValidationMetrics(
        kge=float(kge),
        kge_r=float(r),
        kge_alpha=float(alpha),
        kge_beta=float(beta),
        nse=float(nse),
        rmse=rmse,
        mae=mae,
        bias=bias,
        peak_error=float(peak_error),
        timing_error_days=float(best_lag),
    )


def simple_decomposition(series: pd.Series) -> Dict[str, List[float | None]]:
    s = series.astype(float)
    trend = s.rolling(window=12, center=True, min_periods=6).mean()
    detrended = s - trend
    month_means = detrended.groupby(detrended.index.month).mean()
    seasonal = detrended.index.month.map(month_means)
    resid = s - trend - seasonal
    return {
        "trend": [None if pd.isna(v) else float(v) for v in trend],
        "seasonal": [None if pd.isna(v) else float(v) for v in seasonal],
        "resid": [None if pd.isna(v) else float(v) for v in resid],
    }


def build_domain(domain: str) -> dict:
    m_path = RESULTS / domain / "monthly_drought_indices.csv"
    d_path = RESULTS / domain / "daily_discharge.csv"

    monthly = pd.read_csv(m_path)
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly = monthly.sort_values("date").reset_index(drop=True)

    daily = pd.read_csv(d_path)
    daily["date"] = pd.to_datetime(daily["date"])

    # Indices
    monthly["spi_1"] = calc_spi(monthly["precip"], 1)
    monthly["spi_3"] = calc_spi(monthly["precip"], 3)
    monthly["spi_6"] = calc_spi(monthly["precip"], 6)
    monthly["spi_12"] = calc_spi(monthly["precip"], 12)
    monthly["spei_3"] = calc_spei(monthly["precip"], monthly["pet"], 3)
    monthly["smi"] = calc_smi(monthly["smi_percent"])

    # Monthly discharge from daily
    dm = daily.set_index("date").resample("MS").agg({"qobs": "mean", "qsim": "mean"}).reset_index()
    merged = monthly.merge(dm, on="date", how="left")

    # Categories and consistency
    cons = []
    for _, r in merged.iterrows():
        spi = r["spi_3"]
        spei = r["spei_3"]
        smi = r["smi"]
        c_spi = classify_index(spi)
        c_spei = classify_index(spei)
        c_smi = classify_index(smi)
        cats = [c_spi, c_spei, c_smi]
        agree = max(cats.count(c) for c in set(cats)) / 3.0
        dom = None
        if agree >= 2 / 3:
            dom = max(set(cats), key=cats.count)
        cons.append(
            {
                "date": r["date"].strftime("%Y-%m-%d"),
                "spi_category": c_spi,
                "spei_category": c_spei,
                "smi_category": c_smi,
                "agreement_score": float(agree),
                "dominant_drought": dom,
            }
        )

    # Export monthly csv for transparency
    out_dir = RESULTS / domain
    out_df = merged[
        [
            "date",
            "spi_1",
            "spi_3",
            "spi_6",
            "spi_12",
            "spei_3",
            "smi",
            "qobs",
            "qsim",
        ]
    ].copy()
    out_df.to_csv(out_dir / "monitor_indices.csv", index=False)

    val = calc_validation(daily)
    decomp = simple_decomposition(merged.set_index("date")["smi"])

    points = []
    for _, r in out_df.iterrows():
        points.append(
            {
                "date": pd.Timestamp(r["date"]).strftime("%Y-%m-%d"),
                "spi_1": None if pd.isna(r["spi_1"]) else float(r["spi_1"]),
                "spi_3": None if pd.isna(r["spi_3"]) else float(r["spi_3"]),
                "spi_6": None if pd.isna(r["spi_6"]) else float(r["spi_6"]),
                "spi_12": None if pd.isna(r["spi_12"]) else float(r["spi_12"]),
                "spei_3": None if pd.isna(r["spei_3"]) else float(r["spei_3"]),
                "smi": None if pd.isna(r["smi"]) else float(r["smi"]),
                "discharge_observed": None if pd.isna(r["qobs"]) else float(r["qobs"]),
                "discharge_simulated": None if pd.isna(r["qsim"]) else float(r["qsim"]),
            }
        )

    payload = {
        "domain": domain,
        "metadata": {
            "start": merged["date"].min().strftime("%Y-%m-%d"),
            "end": merged["date"].max().strftime("%Y-%m-%d"),
            "n_points": int(len(merged)),
            "timescales": [1, 3, 6, 12],
        },
        "validation": asdict(val),
        "decomposition": decomp,
        "points": points,
        "consistency": cons,
    }

    OUT_PUBLIC.mkdir(parents=True, exist_ok=True)
    (OUT_PUBLIC / f"{domain}_monitor.json").write_text(json.dumps(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", choices=["test_domain", "catchment_custom", "all"], default="all")
    args = parser.parse_args()

    domains = [args.domain] if args.domain in {"test_domain", "catchment_custom"} else ["test_domain", "catchment_custom"]
    for d in domains:
        payload = build_domain(d)
        print(f"[{d}] points={payload['metadata']['n_points']} kge={payload['validation']['kge']:.3f}")


if __name__ == "__main__":
    main()
