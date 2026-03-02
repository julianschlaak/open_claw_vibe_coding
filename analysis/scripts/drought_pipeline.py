#!/usr/bin/env python3
"""Drought pipeline v3.0.

Major updates:
1) Volumetric soil moisture from SWC and total soil depth.
2) Flat output structure: analysis/plots/<catchment>/ and analysis/results/<catchment>/.
3) Discharge validation from daily_discharge.out (Qobs + Qsim + metrics box).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm

sns.set_style("whitegrid")
plt.rcParams["font.family"] = "sans-serif"


@dataclass(frozen=True)
class Paths:
    repo: Path
    output_dir: Path
    plot_dir: Path
    results_dir: Path


def _paths(mhm_output_dir: str, catchment: str) -> Paths:
    repo = Path(__file__).resolve().parents[2]
    output_dir = Path(mhm_output_dir)
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    return Paths(
        repo=repo,
        output_dir=output_dir,
        plot_dir=repo / "analysis" / "plots" / catchment,
        results_dir=repo / "analysis" / "results" / catchment,
    )


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


def _domain_root_from_output(output_dir: Path) -> Path:
    return output_dir.parent if output_dir.name.startswith("output") else output_dir


def _soil_depth_total_mm(domain_root: Path, fallback_mm: float = 200.0) -> float:
    nml = domain_root / "mhm.nml"
    if not nml.exists():
        return fallback_mm
    text = nml.read_text(errors="ignore")
    vals = []
    for m in re.finditer(r"soil_Depth(?:\(\d+\))?\s*=\s*([^\n/]+)", text):
        rhs = m.group(1)
        vals.extend(float(x) for x in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", rhs))
    if not vals:
        return fallback_mm
    total = float(np.nansum(vals))
    return total if total > 0 else fallback_mm


def _calendar_percentile(dates: pd.Series, values: pd.Series) -> pd.Series:
    d = pd.to_datetime(dates)
    v = pd.to_numeric(values, errors="coerce")

    # Use day-of-year for daily data and month-of-year for monthly data.
    dd = d.sort_values().diff().dt.days.dropna()
    if len(dd) > 0 and float(dd.median()) <= 2.0:
        key = d.dt.dayofyear
    else:
        key = d.dt.month

    out = pd.Series(np.nan, index=v.index, dtype=float)
    for k in key.dropna().unique():
        idx = key == k
        out.loc[idx] = v.loc[idx].rank(method="average", pct=True) * 100.0
    return out


def _standardized_from_percentile(p: pd.Series) -> pd.Series:
    x = np.clip(p / 100.0, 1e-6, 1 - 1e-6)
    return pd.Series(norm.ppf(x), index=p.index)


def _calculate_metrics(simulated: np.ndarray, observed: np.ndarray) -> dict:
    mask = ~(np.isnan(simulated) | np.isnan(observed))
    s = simulated[mask]
    o = observed[mask]
    if len(s) < 2:
        return {k: np.nan for k in ["KGE", "r", "alpha", "beta", "RMSE", "MAE", "NSE"]}

    r = np.corrcoef(s, o)[0, 1]
    alpha = np.std(s) / np.std(o) if np.std(o) > 0 else np.nan
    beta = np.mean(s) / np.mean(o) if np.mean(o) != 0 else np.nan
    kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    rmse = np.sqrt(np.mean((s - o) ** 2))
    mae = np.mean(np.abs(s - o))
    nse = 1 - np.sum((s - o) ** 2) / np.sum((o - np.mean(o)) ** 2)
    return {"KGE": kge, "r": r, "alpha": alpha, "beta": beta, "RMSE": rmse, "MAE": mae, "NSE": nse}


def _load_monthly(paths: Paths) -> pd.DataFrame:
    nc_file = paths.output_dir / "mHM_Fluxes_States.nc"
    cached = paths.results_dir / "monthly_drought_indices.csv"
    if not nc_file.exists():
        if cached.exists():
            return pd.read_csv(cached, parse_dates=["date"])
        if paths.results_dir.name == "catchment_custom":
            legacy = paths.results_dir.parent / "custom_catchment" / "normal" / "monthly_drought_indices.csv"
            if legacy.exists():
                return pd.read_csv(legacy, parse_dates=["date"])
        raise FileNotFoundError(f"Missing {nc_file} and no cached file at {cached}")

    ds = nc.Dataset(nc_file)
    try:
        time = _to_datetime(ds.variables["time"])
        n_time = len(time)

        swc_top = _spatial_mean_any(ds, ["SWC_L01", "SWC_L1"], n_time)
        if np.isnan(swc_top).all():
            depth_mm = _soil_depth_total_mm(_domain_root_from_output(paths.output_dir), fallback_mm=200.0)
            swc_lall = _spatial_mean_any(ds, ["SWC_Lall"], n_time)
            sm_vol = swc_lall / depth_mm
        else:
            sm_vol = swc_top / 200.0

        df = pd.DataFrame(
            {
                "date": time,
                "sm": sm_vol,
                "sm_l1": _spatial_mean_any(ds, ["SWC_L01", "SWC_L1"], n_time) / 200.0,
                "sm_l2": _spatial_mean_any(ds, ["SWC_L02", "SWC_L2"], n_time) / 200.0,
                "sm_l3": _spatial_mean_any(ds, ["SWC_L03", "SWC_L3"], n_time) / 200.0,
                "recharge": _spatial_mean(ds, "recharge"),
                "runoff": _spatial_mean(ds, "Q"),
                "pet": _spatial_mean_any(ds, ["PET"], n_time),
                "et": _spatial_mean_any(ds, ["ET", "aET"], n_time),
                "precip": _spatial_mean_any(ds, ["pre", "preEffect"], n_time),
            }
        )
    finally:
        ds.close()

    df["smi_percent"] = _calendar_percentile(df["date"], df["sm"])
    df["ssi"] = _standardized_from_percentile(df["smi_percent"])
    df["recharge_percent"] = _calendar_percentile(df["date"], df["recharge"])
    df["runoff_percent"] = _calendar_percentile(df["date"], df["runoff"])
    df["pet_percent"] = _calendar_percentile(df["date"], df["pet"])
    df["et_percent"] = _calendar_percentile(df["date"], df["et"])
    df["aridity_index"] = df["pet"] / df["precip"].replace(0, np.nan)
    return df


def _load_daily_discharge(paths: Paths) -> Tuple[pd.DataFrame, pd.DataFrame]:
    txt_file = paths.output_dir / "daily_discharge.out"
    nc_file = paths.output_dir / "discharge.nc"
    cached_daily = paths.results_dir / "daily_discharge.csv"

    daily = pd.DataFrame()

    if txt_file.exists():
        raw = pd.read_csv(txt_file, sep=r"\s+", engine="python")
        cols_l = {c.lower(): c for c in raw.columns}
        day_col = next((cols_l[k] for k in cols_l if k.startswith("day")), None)
        mon_col = next((cols_l[k] for k in cols_l if k.startswith("mon")), None)
        year_col = next((cols_l[k] for k in cols_l if k.startswith("year")), None)
        qobs_col = next((c for c in raw.columns if "qobs" in c.lower()), None)
        qsim_col = next((c for c in raw.columns if "qsim" in c.lower()), None)
        if day_col and mon_col and year_col and qsim_col:
            daily = pd.DataFrame(
                {
                    "date": pd.to_datetime({"year": raw[year_col].astype(int), "month": raw[mon_col].astype(int), "day": raw[day_col].astype(int)}),
                    "qobs": pd.to_numeric(raw[qobs_col], errors="coerce") if qobs_col else np.nan,
                    "qsim": pd.to_numeric(raw[qsim_col], errors="coerce"),
                }
            )

    if daily.empty and nc_file.exists():
        ds = nc.Dataset(nc_file)
        try:
            time = _to_datetime(ds.variables["time"])
            qsim_var = next(v for v in ds.variables if v.startswith("Qsim_"))
            qobs_var = next((v for v in ds.variables if v.startswith("Qobs_")), None)
            daily = pd.DataFrame(
                {
                    "date": time,
                    "qsim": np.asarray(ds.variables[qsim_var][:], dtype=float),
                    "qobs": np.asarray(ds.variables[qobs_var][:], dtype=float) if qobs_var else np.nan,
                }
            )
        finally:
            ds.close()

    if daily.empty and cached_daily.exists():
        daily = pd.read_csv(cached_daily, parse_dates=["date"])
        if "qobs" not in daily.columns:
            daily["qobs"] = np.nan
    if daily.empty and paths.results_dir.name == "catchment_custom":
        legacy_daily = paths.results_dir.parent / "custom_catchment" / "normal" / "daily_discharge.csv"
        if legacy_daily.exists():
            daily = pd.read_csv(legacy_daily, parse_dates=["date"])
            if "qobs" not in daily.columns:
                daily["qobs"] = np.nan

    if daily.empty:
        raise FileNotFoundError("No discharge source available (daily_discharge.out, discharge.nc, cached csv)")

    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month

    monthly = daily.resample("MS", on="date").agg({"qsim": ["mean", "min", "max", "std"], "qobs": ["mean"]}).reset_index()
    monthly.columns = ["date", "qsim_monthly_mean", "qsim_monthly_min", "qsim_monthly_max", "qsim_monthly_std", "qobs_monthly_mean"]
    monthly["discharge_percent"] = _calendar_percentile(monthly["date"], monthly["qsim_monthly_mean"])
    monthly["sdi"] = _standardized_from_percentile(monthly["discharge_percent"])
    return daily, monthly


def _create_discrete_colormap() -> mcolors.ListedColormap:
    return mcolors.ListedColormap(["#d73027", "#fc8d59", "#fee08b", "#91bfdb", "#4575b4"])


def _plot_timeseries_modern(df: pd.DataFrame, out_file: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), constrained_layout=True)
    axes[0].fill_between(df["date"], df["sm"], alpha=0.3, color="#3498db")
    axes[0].plot(df["date"], df["sm"], color="#2980b9", linewidth=1.2, label="SM volumetric")
    axes[0].axhline(df["sm"].quantile(0.2), color="#e74c3c", linestyle="--", alpha=0.7, label="Q20")
    axes[0].set_title("Bodenfeuchte-Verlauf (volumetrisch)", fontweight="bold")
    axes[0].set_ylabel("m³/m³")
    axes[0].legend(loc="upper right")

    axes[1].plot(df["date"], df["ssi"], label="SSI", color="#2ecc71", linewidth=1.2)
    if "sdi" in df.columns:
        axes[1].plot(df["date"], df["sdi"], label="SDI", color="#e74c3c", linewidth=1.2)
    axes[1].axhline(-1, color="#e74c3c", linestyle="--", alpha=0.5)
    axes[1].axhline(-2, color="#c0392b", linestyle="--", alpha=0.5)
    axes[1].axhline(0, color="black", linestyle="-", alpha=0.3)
    axes[1].set_title("Standardisierte Dürre-Indizes", fontweight="bold")
    axes[1].legend(loc="upper right")

    axes[2].plot(df["date"], df["smi_percent"], label="SMI", linewidth=1.2)
    axes[2].plot(df["date"], df["recharge_percent"], label="Recharge", linewidth=1.2)
    axes[2].plot(df["date"], df["runoff_percent"], label="Runoff", linewidth=1.2)
    if "discharge_percent" in df.columns:
        axes[2].plot(df["date"], df["discharge_percent"], label="Discharge", linewidth=1.2)
    axes[2].axhline(20, color="#e74c3c", linestyle="--", alpha=0.7)
    axes[2].set_title("Dürre-Percentile", fontweight="bold")
    axes[2].set_ylim(0, 100)
    axes[2].legend(loc="upper right")

    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _plot_heatmap_discrete(df: pd.DataFrame, column: str, title: str, out_file: Path) -> None:
    data = df.copy()
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    pivot = data.pivot(index="year", columns="month", values=column)
    cmap = _create_discrete_colormap()
    bounds = [0, 10, 20, 30, 50, 100]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, norm=norm)
    ax.set_title(title, fontweight="bold")
    ax.set_xticks(np.arange(12))
    ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([str(y) for y in pivot.index])
    cbar = fig.colorbar(im, ax=ax, boundaries=bounds, ticks=[5, 15, 25, 40, 75])
    cbar.set_label("Percentil")
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _plot_discharge_validation(daily_df: pd.DataFrame, out_file: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(daily_df["date"], daily_df["qobs"], label="Qobs (Gemessen)", color="red", linewidth=1.2, alpha=0.8)
    ax.plot(daily_df["date"], daily_df["qsim"], label="Qsim (Modell)", color="blue", linewidth=1.2, alpha=0.8)

    metrics = _calculate_metrics(daily_df["qsim"].to_numpy(), daily_df["qobs"].to_numpy())
    metrics_text = (
        f"KGE: {metrics['KGE']:.3f}\n"
        f"r: {metrics['r']:.3f}\n"
        f"RMSE: {metrics['RMSE']:.2f} m³/s\n"
        f"MAE: {metrics['MAE']:.2f} m³/s\n"
        f"NSE: {metrics['NSE']:.3f}\n"
        f"Bias: {metrics['beta']:.3f}"
    )
    ax.text(
        0.02,
        0.98,
        metrics_text,
        transform=ax.transAxes,
        fontsize=10,
        va="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    ax.set_title("Abfluss: Beobachtet vs. Simuliert", fontweight="bold")
    ax.set_ylabel("Abfluss [m³/s]")
    ax.set_xlabel("Datum")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _plot_correlation_matrix(df: pd.DataFrame, out_file: Path) -> None:
    cols = ["sm", "recharge", "runoff", "aridity_index"]
    if "qsim_monthly_mean" in df.columns:
        cols.append("qsim_monthly_mean")
    corr = df[cols].corr()

    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, square=True, ax=ax)
    ax.set_title("Korrelationsmatrix", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _plot_drought_duration(df: pd.DataFrame, out_file: Path) -> None:
    d = df.copy()
    d["flag"] = d["smi_percent"] < 20
    events = []
    in_ev = False
    start = None
    for _, row in d.iterrows():
        if row["flag"] and not in_ev:
            in_ev = True
            start = row["date"]
        elif not row["flag"] and in_ev:
            in_ev = False
            events.append((row["date"] - start).days)
    if in_ev:
        events.append((d["date"].iloc[-1] - start).days)
    if not events:
        events = [0]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(events, bins=10, color="#e74c3c", edgecolor="white", alpha=0.8)
    ax.set_title("Dürre-Ereignisdauer", fontweight="bold")
    ax.set_xlabel("Tage")
    ax.set_ylabel("Häufigkeit")
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _plot_seasonal_boxplot(df: pd.DataFrame, out_file: Path) -> None:
    d = df.copy()
    d["month"] = d["date"].dt.month
    d["season"] = d["month"].map({12: "Winter", 1: "Winter", 2: "Winter", 3: "Frühling", 4: "Frühling", 5: "Frühling", 6: "Sommer", 7: "Sommer", 8: "Sommer", 9: "Herbst", 10: "Herbst", 11: "Herbst"})

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    pairs = [("smi_percent", "SMI"), ("recharge_percent", "Recharge"), ("runoff_percent", "Runoff"), ("ssi", "SSI")]
    for ax, (col, title) in zip(axes, pairs):
        sns.boxplot(data=d, x="season", y=col, order=["Frühling", "Sommer", "Herbst", "Winter"], ax=ax)
        ax.set_title(title, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _create_summary_report(df: pd.DataFrame, paths: Paths) -> None:
    lines = [
        "# Dürre-Analyse Zusammenfassung",
        "",
        f"**Analyse-Datum:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Zeitraum:** {df['date'].min().strftime('%Y-%m-%d')} bis {df['date'].max().strftime('%Y-%m-%d')}",
        "",
        f"- Mittel Bodenfeuchte (vol.): {df['sm'].mean():.4f} m³/m³",
        f"- SMI < 20: {(df['smi_percent'] < 20).sum()} Monate",
        "",
        f"Plots: {paths.plot_dir}",
    ]
    (paths.results_dir / "analysis_summary.md").write_text("\n".join(lines))


def _clip_period(df: pd.DataFrame, start_year: int | None, end_year: int | None) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if start_year is not None:
        out = out[out["date"] >= pd.Timestamp(f"{start_year}-01-01")]
    if end_year is not None:
        out = out[out["date"] <= pd.Timestamp(f"{end_year}-12-31")]
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Drought pipeline v3.0")
    parser.add_argument("--domain", choices=["test_domain", "catchment_custom"], default="test_domain")
    parser.add_argument("--mhm-output-dir", default=None)
    parser.add_argument("--catchment-name", default=None)
    parser.add_argument("--start-year", type=int, default=None)
    parser.add_argument("--end-year", type=int, default=None)
    args = parser.parse_args()

    if args.domain == "test_domain":
        out = args.mhm_output_dir or "code/mhm/test_domain/output_b1"
        name = args.catchment_name or "test_domain"
    else:
        out = args.mhm_output_dir or "code/mhm/catchment_custom/output_90410700"
        name = args.catchment_name or "catchment_custom"

    paths = _paths(out, name)
    paths.plot_dir.mkdir(parents=True, exist_ok=True)
    paths.results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("DROUGHT PIPELINE v3.0")
    print("=" * 60)

    monthly = _load_monthly(paths)
    daily, monthly_q = _load_daily_discharge(paths)
    monthly = _clip_period(monthly, args.start_year, args.end_year)
    monthly_q = _clip_period(monthly_q, args.start_year, args.end_year)
    daily = _clip_period(daily, args.start_year, args.end_year)

    for c in ["qsim_monthly_mean", "qsim_monthly_min", "qsim_monthly_max", "qsim_monthly_std", "discharge_percent", "sdi"]:
        if c in monthly.columns:
            monthly = monthly.drop(columns=[c])

    merged = monthly.merge(
        monthly_q[["date", "qsim_monthly_mean", "qsim_monthly_min", "qsim_monthly_max", "qsim_monthly_std", "discharge_percent", "sdi"]],
        on="date",
        how="left",
    )

    merged["drought_class"] = np.where(merged["smi_percent"] < 20, "drought", "normal_or_wet")

    _plot_timeseries_modern(merged, paths.plot_dir / "01_drought_timeseries.png")
    _plot_heatmap_discrete(merged, "smi_percent", "SMI Dürre-Klassifikation", paths.plot_dir / "02_heatmap_smi.png")
    _plot_heatmap_discrete(merged, "recharge_percent", "Recharge Dürre-Klassifikation", paths.plot_dir / "03_heatmap_recharge.png")
    _plot_heatmap_discrete(merged, "discharge_percent", "Abfluss Dürre-Klassifikation", paths.plot_dir / "04_heatmap_discharge.png")
    _plot_discharge_validation(daily, paths.plot_dir / "05_discharge_analysis.png")
    _plot_correlation_matrix(merged, paths.plot_dir / "06_correlation_matrix.png")
    _plot_drought_duration(merged, paths.plot_dir / "07_drought_duration.png")
    _plot_seasonal_boxplot(merged, paths.plot_dir / "08_seasonal_boxplots.png")

    merged.to_csv(paths.results_dir / "monthly_drought_indices.csv", index=False)
    daily.to_csv(paths.results_dir / "daily_discharge.csv", index=False)
    (
        merged.assign(year=merged["date"].dt.year)
        .groupby("year", as_index=False)
        .agg(
            min_smi=("smi_percent", "min"),
            min_recharge=("recharge_percent", "min"),
            min_runoff=("runoff_percent", "min"),
            min_discharge=("discharge_percent", "min"),
            drought_months=("drought_class", lambda s: int((s != "normal_or_wet").sum())),
        )
        .to_csv(paths.results_dir / "annual_drought_summary.csv", index=False)
    )
    _create_summary_report(merged, paths)

    print(f"Plots: {paths.plot_dir}")
    print(f"Results: {paths.results_dir}")


if __name__ == "__main__":
    main()
