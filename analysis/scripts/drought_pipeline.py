#!/usr/bin/env python3
"""End-to-end drought index pipeline for mHM test domain outputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass(frozen=True)
class Paths:
    repo: Path
    output_dir: Path
    results_dir: Path
    plot_dir: Path


def _paths() -> Paths:
    repo = Path(__file__).resolve().parents[2]
    output_dir = repo / "code" / "mhm" / "test_domain" / "output_b1"
    return Paths(
        repo=repo,
        output_dir=output_dir,
        results_dir=repo / "analysis" / "results",
        plot_dir=repo / "analysis" / "plots",
    )


def _to_datetime(time_var) -> pd.DatetimeIndex:
    t = nc.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def _spatial_mean(ds: nc.Dataset, var_name: str) -> np.ndarray:
    # NetCDF variables are masked arrays; convert masked cells to NaN before averaging.
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(float)
    return np.nanmean(arr, axis=(1, 2))


def _percentile(series: pd.Series) -> pd.Series:
    return series.rank(method="average", pct=True) * 100.0


def _standardized_from_percentile(percentile: pd.Series) -> pd.Series:
    p = np.clip(percentile / 100.0, 1e-6, 1.0 - 1e-6)
    return pd.Series(norm.ppf(p), index=percentile.index)


def _load_monthly(paths: Paths) -> pd.DataFrame:
    ds = nc.Dataset(paths.output_dir / "mHM_Fluxes_States.nc")
    try:
        time = _to_datetime(ds.variables["time"])
        df = pd.DataFrame(
            {
                "date": time,
                "sm": _spatial_mean(ds, "SM_Lall"),
                "recharge": _spatial_mean(ds, "recharge"),
                "runoff": _spatial_mean(ds, "Q"),
            }
        )
    finally:
        ds.close()

    df["smi_percent"] = _percentile(df["sm"])
    df["ssi"] = _standardized_from_percentile(df["smi_percent"])
    df["recharge_percent"] = _percentile(df["recharge"])
    df["runoff_percent"] = _percentile(df["runoff"])
    return df


def _load_daily_discharge(paths: Paths) -> pd.DataFrame:
    ds = nc.Dataset(paths.output_dir / "discharge.nc")
    try:
        qsim_var = next(name for name in ds.variables if name.startswith("Qsim_"))
        time = _to_datetime(ds.variables["time"])
        qsim = np.asarray(ds.variables[qsim_var][:], dtype=float)
    finally:
        ds.close()

    daily = pd.DataFrame({"date": time, "qsim": qsim})
    monthly = daily.resample("MS", on="date").mean().rename(columns={"qsim": "qsim_monthly_mean"}).reset_index()
    monthly["discharge_percent"] = _percentile(monthly["qsim_monthly_mean"])
    return daily, monthly


def _classify(row: pd.Series) -> str:
    vals = [row["smi_percent"], row["recharge_percent"], row["runoff_percent"], row["discharge_percent"]]
    if all(v <= 10 for v in vals):
        return "extreme_drought"
    if all(v <= 20 for v in vals):
        return "severe_drought"
    if all(v <= 30 for v in vals):
        return "moderate_drought"
    return "normal_or_wet"


def _make_time_series_plot(df: pd.DataFrame, out_file: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), constrained_layout=True)

    axes[0].plot(df["date"], df["sm"], label="SM_Lall")
    axes[0].set_title("Mean Soil Moisture (SM_Lall)")
    axes[0].set_ylabel("mm mm-1")
    axes[0].grid(alpha=0.3)

    axes[1].plot(df["date"], df["smi_percent"], label="SMI percentile")
    axes[1].plot(df["date"], df["recharge_percent"], label="Recharge percentile")
    axes[1].plot(df["date"], df["runoff_percent"], label="Runoff percentile")
    axes[1].plot(df["date"], df["discharge_percent"], label="Discharge percentile")
    axes[1].axhline(20, color="red", linestyle="--", linewidth=1, label="Drought threshold (20%)")
    axes[1].set_title("Hydrological Drought Indices")
    axes[1].set_ylabel("Percentile")
    axes[1].set_ylim(0, 100)
    axes[1].grid(alpha=0.3)
    axes[1].legend(loc="best")

    fig.savefig(out_file, dpi=170)
    plt.close(fig)


def _make_heatmap(df: pd.DataFrame, column: str, title: str, out_file: Path) -> None:
    data = df.copy()
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    pivot = data.pivot(index="year", columns="month", values=column)

    fig, ax = plt.subplots(figsize=(12, 3 + 0.5 * max(1, len(pivot))))
    im = ax.imshow(pivot.values, aspect="auto", interpolation="nearest", vmin=0, vmax=100, cmap="RdYlBu")
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.set_xticks(np.arange(12), labels=[str(i) for i in range(1, 13)])
    ax.set_yticks(np.arange(len(pivot.index)), labels=[str(y) for y in pivot.index])
    fig.colorbar(im, ax=ax, label="Percentile")

    fig.tight_layout()
    fig.savefig(out_file, dpi=170)
    plt.close(fig)


def main() -> None:
    paths = _paths()
    paths.results_dir.mkdir(parents=True, exist_ok=True)
    paths.plot_dir.mkdir(parents=True, exist_ok=True)

    monthly = _load_monthly(paths)
    daily_discharge, monthly_discharge = _load_daily_discharge(paths)

    merged = monthly.merge(
        monthly_discharge[["date", "qsim_monthly_mean", "discharge_percent"]],
        on="date",
        how="left",
    )
    merged["drought_class"] = merged.apply(_classify, axis=1)

    monthly_file = paths.results_dir / "monthly_drought_indices.csv"
    daily_file = paths.results_dir / "daily_discharge_qsim.csv"
    summary_file = paths.results_dir / "drought_summary.csv"

    merged.to_csv(monthly_file, index=False)
    daily_discharge.to_csv(daily_file, index=False)

    summary = (
        merged.assign(year=merged["date"].dt.year)
        .groupby("year", as_index=False)
        .agg(
            min_smi_percent=("smi_percent", "min"),
            min_recharge_percent=("recharge_percent", "min"),
            min_runoff_percent=("runoff_percent", "min"),
            min_discharge_percent=("discharge_percent", "min"),
            drought_months=("drought_class", lambda s: int((s != "normal_or_wet").sum())),
        )
    )
    summary.to_csv(summary_file, index=False)

    _make_time_series_plot(merged, paths.plot_dir / "drought_indices_timeseries.png")
    _make_heatmap(merged, "smi_percent", "SMI Percentile Heatmap", paths.plot_dir / "heatmap_smi_percent.png")
    _make_heatmap(
        merged,
        "recharge_percent",
        "Recharge Percentile Heatmap",
        paths.plot_dir / "heatmap_recharge_percent.png",
    )
    _make_heatmap(
        merged,
        "discharge_percent",
        "Discharge Percentile Heatmap",
        paths.plot_dir / "heatmap_discharge_percent.png",
    )

    print("Pipeline completed")
    print(f"Monthly indices: {monthly_file}")
    print(f"Daily discharge: {daily_file}")
    print(f"Summary: {summary_file}")
    print(f"Plots directory: {paths.plot_dir}")


if __name__ == "__main__":
    main()
