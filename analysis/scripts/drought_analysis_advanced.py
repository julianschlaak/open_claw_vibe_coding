#!/usr/bin/env python3
"""Advanced drought analysis v3.0 (lag + matrix).

Outputs in flat structure:
- analysis/plots/<catchment>/09_lag_correlation.png
- analysis/plots/<catchment>/10_matrix_drought_index.png
- analysis/results/<catchment>/matrix_drought_index.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")

REPO = Path(__file__).resolve().parents[2]


def _domain_root_from_output(output_dir: Path) -> Path:
    return output_dir.parent if output_dir.name.startswith("output") else output_dir


def _soil_depth_total_mm(domain_root: Path, fallback_mm: float = 200.0) -> float:
    nml = domain_root / "mhm.nml"
    if not nml.exists():
        return fallback_mm
    text = nml.read_text(errors="ignore")
    vals = []
    for m in re.finditer(r"soil_Depth(?:\(\d+\))?\s*=\s*([^\n/]+)", text):
        vals.extend(float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", m.group(1)))
    if not vals:
        return fallback_mm
    total = float(np.nansum(vals))
    return total if total > 0 else fallback_mm


def _to_datetime(time_var) -> pd.DatetimeIndex:
    t = nc.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def _spatial_mean(ds: nc.Dataset, var_name: str) -> np.ndarray:
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(float)
    return np.nanmean(arr, axis=(1, 2))


def _spatial_mean_any(ds: nc.Dataset, candidates: list[str], n_time: int) -> np.ndarray:
    for c in candidates:
        if c in ds.variables:
            return _spatial_mean(ds, c)
    return np.full(n_time, np.nan)


def load_data(mhm_output_dir: Path, fallback_results_dir: Path | None = None) -> pd.DataFrame:
    mhm_nc = mhm_output_dir / "mHM_Fluxes_States.nc"
    q_nc = mhm_output_dir / "discharge.nc"

    if (not mhm_nc.exists() or not q_nc.exists()) and fallback_results_dir is not None:
        cached = fallback_results_dir / "monthly_drought_indices.csv"
        if (not cached.exists()) and fallback_results_dir.name == "catchment_custom":
            cached = fallback_results_dir.parent / "custom_catchment" / "normal" / "monthly_drought_indices.csv"
        if cached.exists():
            df = pd.read_csv(cached, parse_dates=["date"])
            if "qsim_monthly_mean" in df.columns:
                df["discharge"] = df["qsim_monthly_mean"]
            elif "discharge" not in df.columns:
                df["discharge"] = np.nan
            required = ["date", "precip", "sm", "recharge", "runoff", "discharge"]
            for c in required:
                if c not in df.columns:
                    raise KeyError(f"Cached fallback missing column: {c}")
            return df[["date", "precip", "sm", "recharge", "runoff", "discharge"]].sort_values("date")

    ds = nc.Dataset(mhm_nc)
    try:
        time = _to_datetime(ds.variables["time"])
        n_time = len(time)
        swc_top = _spatial_mean_any(ds, ["SWC_L01", "SWC_L1"], n_time)
        if np.isnan(swc_top).all():
            depth_mm = _soil_depth_total_mm(_domain_root_from_output(mhm_output_dir), fallback_mm=200.0)
            swc_lall = _spatial_mean_any(ds, ["SWC_Lall"], n_time)
            sm_vol = swc_lall / depth_mm
        else:
            sm_vol = swc_top / 200.0

        precip = _spatial_mean_any(ds, ["pre", "preEffect"], n_time)
        recharge = _spatial_mean_any(ds, ["recharge", "L1_percol"], n_time)
        runoff = _spatial_mean_any(ds, ["Q", "L1_total_runoff"], n_time)
    finally:
        ds.close()

    ds_q = nc.Dataset(q_nc)
    try:
        qsim_var = next(v for v in ds_q.variables if v.startswith("Qsim_"))
        q_time = _to_datetime(ds_q.variables["time"])
        qsim = np.asarray(ds_q.variables[qsim_var][:], dtype=float)
    finally:
        ds_q.close()

    df = pd.DataFrame({"date": time, "precip": precip, "sm": sm_vol, "recharge": recharge, "runoff": runoff})
    q_df = pd.DataFrame({"date": q_time, "discharge": qsim})
    df_m = df.resample("ME", on="date").mean().reset_index()
    q_m = q_df.resample("ME", on="date").mean().reset_index()
    return df_m.merge(q_m, on="date", how="outer").sort_values("date")


def calculate_lag_correlation(x: pd.Series, y: pd.Series, max_lag: int = 12) -> Tuple[np.ndarray, np.ndarray]:
    lags = np.arange(-max_lag, max_lag + 1)
    corr = np.zeros(len(lags))
    for i, lag in enumerate(lags):
        if lag < 0:
            xs, ys = x.iloc[:lag].values, y.iloc[-lag:].values
        elif lag > 0:
            xs, ys = x.iloc[lag:].values, y.iloc[:-lag].values
        else:
            xs, ys = x.values, y.values
        mask = ~(np.isnan(xs) | np.isnan(ys))
        corr[i] = np.corrcoef(xs[mask], ys[mask])[0, 1] if np.sum(mask) > 3 else np.nan
    return lags, corr


def plot_lag_correlation(df: pd.DataFrame, out_file: Path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    pairs = [
        ("precip", "sm", "Niederschlag → Bodenfeuchte", "b"),
        ("sm", "recharge", "Bodenfeuchte → Recharge", "g"),
        ("recharge", "discharge", "Recharge → Abfluss", "r"),
    ]
    for i, (a, b, title, col) in enumerate(pairs):
        lags, c = calculate_lag_correlation(df[a], df[b])
        axes[i].plot(lags, c, color=col, marker="o", linewidth=2)
        axes[i].axhline(0, color="gray", alpha=0.3)
        axes[i].set_title(title, fontweight="bold")
        axes[i].set_xlabel("Lag [Monate]")
        axes[i].set_ylabel("r")
        axes[i].grid(alpha=0.3)

    vars_map = {"Niederschlag": "precip", "Bodenfeuchte": "sm", "Recharge": "recharge", "Runoff": "runoff", "Abfluss": "discharge"}
    corr_m = np.zeros((len(vars_map), len(vars_map)))
    names = list(vars_map.keys())
    cols = list(vars_map.values())
    for i, ci in enumerate(cols):
        for j, cj in enumerate(cols):
            m = ~(np.isnan(df[ci]) | np.isnan(df[cj]))
            corr_m[i, j] = np.corrcoef(df[ci][m], df[cj][m])[0, 1] if np.sum(m) > 3 else np.nan

    im = axes[3].imshow(corr_m, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    axes[3].set_xticks(range(len(names)))
    axes[3].set_yticks(range(len(names)))
    axes[3].set_xticklabels(names, rotation=45, ha="right")
    axes[3].set_yticklabels(names)
    axes[3].set_title("Korrelationsmatrix (Lag=0)", fontweight="bold")
    plt.colorbar(im, ax=axes[3], shrink=0.8)

    fig.tight_layout()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_matrix_drought_index(df: pd.DataFrame, plot_file: Path, csv_file: Path):
    data = df.copy()
    for c in ["sm", "recharge", "discharge"]:
        data[f"{c}_pct"] = data[c].rank(pct=True) * 100
    data["sm_norm"] = data["sm_pct"] / 100
    data["recharge_norm"] = data["recharge_pct"].shift(1) / 100
    data["discharge_norm"] = data["discharge_pct"].shift(2) / 100
    data["matrix_drought_index"] = 0.4 * data["sm_norm"] + 0.3 * data["recharge_norm"] + 0.3 * data["discharge_norm"]

    def classify(x):
        if pd.isna(x):
            return "unknown"
        if x < 0.2:
            return "extreme_drought"
        if x < 0.4:
            return "severe_drought"
        if x < 0.6:
            return "moderate_drought"
        if x < 0.8:
            return "mild_drought"
        return "normal_or_wet"

    data["matrix_class"] = data["matrix_drought_index"].apply(classify)

    colors = ["#8B0000", "#FF4500", "#FFA500", "#FFD700", "#90EE90"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    pivot = data.pivot(index="year", columns="month", values="matrix_drought_index")

    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    im = axes[0].imshow(pivot.values, aspect="auto", cmap=cmap, norm=norm)
    axes[0].set_title("Matrix Dürre-Index", fontweight="bold")
    axes[0].set_yticks(range(len(pivot.index)))
    axes[0].set_yticklabels(pivot.index)
    axes[0].set_xticks(range(12))
    axes[0].set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    plt.colorbar(im, ax=axes[0], boundaries=bounds, ticks=[0.1, 0.3, 0.5, 0.7, 0.9])

    axes[1].plot(data["date"], data["matrix_drought_index"], "k-", linewidth=2, label="Matrix Index")
    axes[1].plot(data["date"], data["sm_norm"], alpha=0.7, label="SMI (40%)")
    axes[1].plot(data["date"], data["recharge_norm"], alpha=0.7, label="Recharge (30%, lag-1)")
    axes[1].plot(data["date"], data["discharge_norm"], alpha=0.7, label="Discharge (30%, lag-2)")
    axes[1].legend(loc="upper right")
    axes[1].grid(alpha=0.3)

    cnt = data.groupby("year")["matrix_class"].value_counts().unstack(fill_value=0)
    bottom = np.zeros(len(cnt))
    order = ["extreme_drought", "severe_drought", "moderate_drought", "mild_drought", "normal_or_wet"]
    cmap_c = {"extreme_drought": "#8B0000", "severe_drought": "#FF4500", "moderate_drought": "#FFA500", "mild_drought": "#FFD700", "normal_or_wet": "#90EE90"}
    for c in order:
        if c in cnt.columns:
            axes[2].bar(cnt.index, cnt[c], bottom=bottom, color=cmap_c[c], label=c)
            bottom += cnt[c]
    axes[2].legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    axes[2].grid(alpha=0.3, axis="y")

    fig.tight_layout()
    plot_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    csv_file.parent.mkdir(parents=True, exist_ok=True)
    data[["date", "matrix_drought_index", "matrix_class", "sm_norm", "recharge_norm", "discharge_norm"]].to_csv(csv_file, index=False)


def _clip_period(df: pd.DataFrame, start_year: int | None, end_year: int | None) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if start_year is not None:
        out = out[out["date"] >= pd.Timestamp(f"{start_year}-01-01")]
    if end_year is not None:
        out = out[out["date"] <= pd.Timestamp(f"{end_year}-12-31")]
    return out


def main():
    parser = argparse.ArgumentParser(description="Advanced drought analysis v3.0")
    parser.add_argument("--domain", choices=["test_domain", "catchment_custom"], default="test_domain")
    parser.add_argument("--mhm-output-dir", default=None)
    parser.add_argument("--catchment-name", default=None)
    parser.add_argument("--start-year", type=int, default=None)
    parser.add_argument("--end-year", type=int, default=None)
    args = parser.parse_args()

    if args.domain == "test_domain":
        out = args.mhm_output_dir or str(REPO / "code" / "mhm" / "test_domain" / "output_b1")
        catchment = args.catchment_name or "test_domain"
    else:
        out = args.mhm_output_dir or str(REPO / "code" / "mhm" / "catchment_custom" / "output_90410700")
        catchment = args.catchment_name or "catchment_custom"

    output_dir = Path(out)
    plot_dir = REPO / "analysis" / "plots" / catchment
    results_dir = REPO / "analysis" / "results" / catchment

    df = load_data(output_dir, fallback_results_dir=results_dir)
    df = _clip_period(df, args.start_year, args.end_year)
    plot_lag_correlation(df, plot_dir / "09_lag_correlation.png")
    plot_matrix_drought_index(df, plot_dir / "10_matrix_drought_index.png", results_dir / "matrix_drought_index.csv")

    print("Advanced analysis complete")
    print(f"Plots: {plot_dir}")
    print(f"Results: {results_dir}")


if __name__ == "__main__":
    main()
