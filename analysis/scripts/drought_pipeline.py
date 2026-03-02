#!/usr/bin/env python3
"""Advanced drought index pipeline for mHM with discrete colormaps & modern styling."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from scipy.stats import norm, gamma

# Modern styling
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 9

@dataclass(frozen=True)
class Paths:
    repo: Path
    output_dir: Path
    results_dir: Path
    plot_dir: Path


def _paths(mhm_output_dir: str, domain_subdir: str) -> Paths:
    repo = Path(__file__).resolve().parents[2]
    output_dir = Path(mhm_output_dir)
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    return Paths(
        repo=repo,
        output_dir=output_dir,
        results_dir=repo / "analysis" / "results" / domain_subdir / "normal",
        plot_dir=repo / "analysis" / "plots" / domain_subdir / "normal",
    )


def _to_datetime(time_var) -> pd.DatetimeIndex:
    t = nc.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def _spatial_mean(ds: nc.Dataset, var_name: str) -> np.ndarray:
    """Calculate spatial mean, handling masked values."""
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(float)
    return np.nanmean(arr, axis=(1, 2))


def _spatial_mean_any(ds: nc.Dataset, candidates: list[str], n_time: int) -> np.ndarray:
    """Return spatial mean of first existing variable in candidates, else NaN array."""
    for name in candidates:
        if name in ds.variables:
            return _spatial_mean(ds, name)
    return np.full(n_time, np.nan, dtype=float)


def _calculate_kge(simulated: np.ndarray, observed: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Calculate Kling-Gupta Efficiency and components.
    Returns: (KGE, r, alpha, beta)
    r: correlation
    alpha: standard deviation ratio
    beta: mean ratio
    """
    mask = ~(np.isnan(simulated) | np.isnan(observed))
    if np.sum(mask) < 2:
        return np.nan, np.nan, np.nan, np.nan
    
    s = simulated[mask]
    o = observed[mask]
    
    r = np.corrcoef(s, o)[0, 1]
    alpha = np.std(s) / np.std(o) if np.std(o) > 0 else np.nan
    beta = np.mean(s) / np.mean(o) if np.mean(o) != 0 else np.nan
    
    kge = 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)
    return kge, r, alpha, beta


def _calculate_metrics(simulated: np.ndarray, observed: np.ndarray) -> dict:
    """Calculate all performance metrics."""
    mask = ~(np.isnan(simulated) | np.isnan(observed))
    s = simulated[mask]
    o = observed[mask]
    
    # RMSE
    rmse = np.sqrt(np.mean((s - o)**2))
    
    # MAE
    mae = np.mean(np.abs(s - o))
    
    # NSE
    nse = 1 - np.sum((s - o)**2) / np.sum((o - np.mean(o))**2)
    
    # KGE
    kge, r, alpha, beta = _calculate_kge(s, o)
    
    return {
        'KGE': kge,
        'r': r,
        'alpha': alpha,
        'beta': beta,
        'RMSE': rmse,
        'MAE': mae,
        'NSE': nse
    }


def _percentile(series: pd.Series) -> pd.Series:
    return series.rank(method="average", pct=True) * 100.0


def _standardized_from_percentile(percentile: pd.Series) -> pd.Series:
    """Convert percentile to standardized value using inverse normal CDF."""
    p = np.clip(percentile / 100.0, 1e-6, 1.0 - 1e-6)
    return pd.Series(norm.ppf(p), index=percentile.index)


def _fit_gamma(series: pd.Series) -> Tuple[float, float]:
    """Fit gamma distribution and return shape (alpha) and scale (beta) parameters."""
    clean = series.dropna()
    clean = clean[clean > 0]  # Gamma requires positive values
    if len(clean) < 10:
        return np.nan, np.nan
    
    shape, loc, scale = stats.gamma.fit(clean, floc=0)
    return shape, scale


def _calculate_sgi(series: pd.Series) -> pd.Series:
    """Calculate Standardized Groundwater Index using gamma distribution."""
    clean = series.dropna()
    clean = clean[clean > 0]
    if len(clean) < 10:
        return pd.Series(np.nan, index=series.index)
    
    shape, scale = _fit_gamma(clean)
    if np.isnan(shape):
        return pd.Series(np.nan, index=series.index)
    
    # Calculate CDF values
    cdf_vals = stats.gamma.cdf(series.replace(0, 1e-10), shape, scale=scale)
    sgi = norm.ppf(np.clip(cdf_vals, 1e-6, 1.0 - 1e-6))
    return pd.Series(sgi, index=series.index)


def _load_monthly(paths: Paths) -> pd.DataFrame:
    """Load monthly mHM outputs and calculate drought indices."""
    nc_file = paths.output_dir / "mHM_Fluxes_States.nc"
    if not nc_file.exists():
        cached = paths.results_dir / "monthly_drought_indices.csv"
        if cached.exists():
            df = pd.read_csv(cached, parse_dates=["date"])
            return df
        raise FileNotFoundError(f"Missing {nc_file} and no cached file at {cached}")

    ds = nc.Dataset(nc_file)
    try:
        time = _to_datetime(ds.variables["time"])
        n_time = len(time)
        df = pd.DataFrame(
            {
                "date": time,
                "sm": _spatial_mean(ds, "SM_Lall"),
                "sm_l1": _spatial_mean_any(ds, ["SM_L1", "SM_L01"], n_time),
                "sm_l2": _spatial_mean_any(ds, ["SM_L2", "SM_L02"], n_time),
                "sm_l3": _spatial_mean_any(ds, ["SM_L3", "SM_L03", "SM_Lall"], n_time),
                "recharge": _spatial_mean(ds, "recharge"),
                "runoff": _spatial_mean(ds, "Q"),
                "pet": _spatial_mean_any(ds, ["PET"], n_time),
                "et": _spatial_mean_any(ds, ["ET", "aET"], n_time),
                "precip": _spatial_mean_any(ds, ["pre", "preEffect"], n_time),
            }
        )
    finally:
        ds.close()

    # Calculate drought indices
    df["smi_percent"] = _percentile(df["sm"])
    df["ssi"] = _standardized_from_percentile(df["smi_percent"])
    df["sgi"] = _calculate_sgi(df["recharge"])
    df["recharge_percent"] = _percentile(df["recharge"])
    df["runoff_percent"] = _percentile(df["runoff"])
    df["pet_percent"] = _percentile(df["pet"])
    df["et_percent"] = _percentile(df["et"])
    df["aridity_index"] = df["pet"] / df["precip"].replace(0, np.nan)
    
    return df


def _load_daily_discharge(paths: Paths) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load daily discharge and aggregate to monthly."""
    nc_file = paths.output_dir / "discharge.nc"
    if not nc_file.exists():
        cached_daily = paths.results_dir / "daily_discharge.csv"
        if cached_daily.exists():
            daily = pd.read_csv(cached_daily, parse_dates=["date"])
            monthly = daily.resample("MS", on="date").agg({
                "qsim": ["mean", "min", "max", "std"]
            }).reset_index()
            monthly.columns = ["date", "qsim_monthly_mean", "qsim_monthly_min", "qsim_monthly_max", "qsim_monthly_std"]
            monthly["discharge_percent"] = _percentile(monthly["qsim_monthly_mean"])
            monthly["sdi"] = _standardized_from_percentile(monthly["discharge_percent"])
            return daily, monthly
        raise FileNotFoundError(f"Missing {nc_file} and no cached file at {cached_daily}")

    ds = nc.Dataset(nc_file)
    try:
        # Find Qsim variable
        qsim_var = next(name for name in ds.variables if name.startswith("Qsim_"))
        time = _to_datetime(ds.variables["time"])
        qsim = np.asarray(ds.variables[qsim_var][:], dtype=float)
    finally:
        ds.close()

    daily = pd.DataFrame({"date": time, "qsim": qsim})
    daily["year"] = daily["date"].dt.year
    daily["month"] = daily["date"].dt.month
    
    # Aggregate to monthly
    monthly = daily.resample("MS", on="date").agg({
        "qsim": ["mean", "min", "max", "std"]
    }).reset_index()
    monthly.columns = ["date", "qsim_monthly_mean", "qsim_monthly_min", "qsim_monthly_max", "qsim_monthly_std"]
    monthly["discharge_percent"] = _percentile(monthly["qsim_monthly_mean"])
    monthly["sdi"] = _standardized_from_percentile(monthly["discharge_percent"])
    
    return daily, monthly


def _classify_drought(row: pd.Series) -> str:
    """Classify drought based on multiple indices."""
    indices = ["smi_percent", "recharge_percent", "runoff_percent", "discharge_percent"]
    values = [row.get(i, 50) for i in indices]
    
    if all(v <= 10 for v in values if not np.isnan(v)):
        return "extreme_drought"
    if all(v <= 20 for v in values if not np.isnan(v)):
        return "severe_drought"
    if all(v <= 30 for v in values if not np.isnan(v)):
        return "moderate_drought"
    if any(v <= 20 for v in values if not np.isnan(v)):
        return "mild_drought"
    return "normal_or_wet"


def _create_discrete_colormap(name: str, n_colors: int = 5) -> mcolors.ListedColormap:
    """Create discrete colormap for drought classification."""
    if name == "drought":
        colors = ["#d73027", "#fc8d59", "#fee08b", "#91bfdb", "#4575b4"]
    elif name == "wet":
        colors = ["#4575b4", "#91bfdb", "#fee08b", "#fc8d59", "#d73027"]
    elif name == "diverging":
        colors = ["#b2182b", "#ef8a62", "#fddbc7", "#d1e5f0", "#67a9cf", "#2166ac"]
    else:
        colors = plt.cm.RdYlBu(np.linspace(0.1, 0.9, n_colors))
    
    return mcolors.ListedColormap(colors)


def _plot_timeseries_modern(df: pd.DataFrame, out_file: Path) -> None:
    """Create modern time series plot with subplots."""
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), constrained_layout=True)
    
    # Panel 1: Soil Moisture
    axes[0].fill_between(df["date"], df["sm"], alpha=0.3, color="#3498db")
    axes[0].plot(df["date"], df["sm"], color="#2980b9", linewidth=1.2, label="SM_Lall")
    axes[0].axhline(df["sm"].quantile(0.2), color="#e74c3c", linestyle="--", alpha=0.7, label="Q20")
    axes[0].set_title("Bodenfeuchte-Verlauf", fontweight='bold')
    axes[0].set_ylabel("m³/m³")
    axes[0].legend(loc="upper right")
    axes[0].grid(alpha=0.3)
    
    # Panel 2: Standardized Indices
    axes[1].plot(df["date"], df["ssi"], label="SSI (Soil)", color="#2ecc71", linewidth=1.2)
    if "sdi" in df.columns:
        axes[1].plot(df["date"], df["sdi"], label="SDI (Discharge)", color="#e74c3c", linewidth=1.2)
    axes[1].axhline(-1, color="#e74c3c", linestyle="--", alpha=0.5, label="Moderate Drought")
    axes[1].axhline(-2, color="#c0392b", linestyle="--", alpha=0.5, label="Severe Drought")
    axes[1].axhline(0, color="black", linestyle="-", alpha=0.3)
    axes[1].set_title("Standardisierte Dürre-Indizes", fontweight='bold')
    axes[1].set_ylabel("Standardabweichungen")
    axes[1].legend(loc="upper right")
    axes[1].grid(alpha=0.3)
    
    # Panel 3: Percentiles
    axes[2].plot(df["date"], df["smi_percent"], label="SMI", linewidth=1.2)
    axes[2].plot(df["date"], df["recharge_percent"], label="Recharge", linewidth=1.2)
    axes[2].plot(df["date"], df["runoff_percent"], label="Runoff", linewidth=1.2)
    if "discharge_percent" in df.columns:
        axes[2].plot(df["date"], df["discharge_percent"], label="Discharge", linewidth=1.2)
    axes[2].axhline(20, color="#e74c3c", linestyle="--", alpha=0.7, label="Dürre-Schwelle (20%)")
    axes[2].set_title("Dürre-Percentile", fontweight='bold')
    axes[2].set_ylabel("Percentil [%]")
    axes[2].set_ylim(0, 100)
    axes[2].legend(loc="upper right")
    axes[2].grid(alpha=0.3)
    
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)


def _plot_heatmap_discrete(df: pd.DataFrame, column: str, title: str, out_file: Path, 
                          cmap_name: str = "drought") -> None:
    """Create heatmap with DISCRETE colormap."""
    data = df.copy()
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    pivot = data.pivot(index="year", columns="month", values=column)
    
    # Discrete colormap
    cmap = _create_discrete_colormap(cmap_name, n_colors=5)
    bounds = [0, 10, 20, 30, 50, 100]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    fig, ax = plt.subplots(figsize=(12, 4))
    im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, norm=norm)
    
    ax.set_title(title, fontweight='bold', pad=20)
    ax.set_xlabel("Monat", fontweight='bold')
    ax.set_ylabel("Jahr", fontweight='bold')
    ax.set_xticks(np.arange(12))
    ax.set_xticklabels(["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels([str(y) for y in pivot.index])
    
    # Colorbar with discrete labels
    cbar = fig.colorbar(im, ax=ax, boundaries=bounds, ticks=[5, 15, 25, 40, 75])
    cbar.ax.set_yticklabels(['Extreme\nDürre (<10)', 'Schwere\nDürre (10-20)', 
                             'Mäßige\nDürre (20-30)', 'Leichte\nDürre (30-50)', 
                             'Normal/Nass\n(>50)'])
    cbar.set_label('Percentil', fontweight='bold')
    
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)


def _plot_discharge_validation(daily_df: pd.DataFrame, out_file: Path) -> None:
    """Plot discharge with performance metrics."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), constrained_layout=True)
    
    # Daily discharge
    axes[0].plot(daily_df["date"], daily_df["qsim"], color="#3498db", linewidth=0.8, alpha=0.7)
    axes[0].set_title("Simulierter Abfluss (täglich)", fontweight='bold')
    axes[0].set_ylabel("Abfluss [m³/s]")
    axes[0].grid(alpha=0.3)
    
    # Monthly statistics
    monthly = daily_df.resample("MS", on="date").agg({
        "qsim": ["mean", "min", "max", "std"]
    }).reset_index()
    monthly.columns = ["date", "mean", "min", "max", "std"]
    
    axes[1].fill_between(monthly["date"], monthly["min"], monthly["max"], 
                          alpha=0.2, color="#3498db", label="Min-Max Spanne")
    axes[1].plot(monthly["date"], monthly["mean"], color="#2980b9", linewidth=1.5, label="Mittelwert")
    axes[1].set_title("Monatliche Abfluss-Statistik", fontweight='bold')
    axes[1].set_ylabel("Abfluss [m³/s]")
    axes[1].set_xlabel("Datum")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)


def _plot_correlation_matrix(df: pd.DataFrame, out_file: Path) -> None:
    """Create correlation heatmap of drought indices."""
    corr_vars = ["sm", "recharge", "runoff", "aridity_index"]
    if "qsim_monthly_mean" in df.columns:
        corr_vars.append("qsim_monthly_mean")
    
    corr_data = df[corr_vars].corr()
    
    fig, ax = plt.subplots(figsize=(8, 7))
    mask = np.triu(np.ones_like(corr_data, dtype=bool), k=1)
    sns.heatmap(corr_data, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, vmin=-1, vmax=1, square=True, ax=ax,
                cbar_kws={"shrink": 0.8})
    ax.set_title("Korrelationsmatrix: Hydrologische Variablen", fontweight='bold', pad=20)
    
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)


def _plot_drought_duration(df: pd.DataFrame, out_file: Path) -> None:
    """Analyze drought event duration distribution."""
    # Identify drought events (SMI < 20)
    df["drought_flag"] = df["smi_percent"] < 20
    
    # Find drought events
    events = []
    in_drought = False
    start = None
    
    for idx, row in df.iterrows():
        if row["drought_flag"] and not in_drought:
            in_drought = True
            start = row["date"]
        elif not row["drought_flag"] and in_drought:
            in_drought = False
            events.append((start, row["date"], (row["date"] - start).days))
    
    # Handle ongoing drought at end
    if in_drought:
        events.append((start, df["date"].iloc[-1], (df["date"].iloc[-1] - start).days))
    
    if len(events) == 0:
        print("No drought events found")
        return
    
    durations = [e[2] for e in events]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(durations, bins=range(0, max(durations)+5, 5), 
                 color="#e74c3c", edgecolor="white", alpha=0.8)
    axes[0].axvline(np.mean(durations), color="#2c3e50", linestyle="--", 
                    linewidth=2, label=f"Mittel: {np.mean(durations):.1f} Tage")
    axes[0].axvline(np.median(durations), color="#8e44ad", linestyle="--", 
                    linewidth=2, label=f"Median: {np.median(durations):.1f} Tage")
    axes[0].set_title("Verteilung der Dürre-Ereignisdauern", fontweight='bold')
    axes[0].set_xlabel("Dauer [Tage]")
    axes[0].set_ylabel("Häufigkeit")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    
    # Cumulative distribution
    sorted_durations = np.sort(durations)
    cdf = np.arange(1, len(sorted_durations) + 1) / len(sorted_durations) * 100
    axes[1].plot(sorted_durations, cdf, linewidth=2, color="#3498db")
    axes[1].fill_between(sorted_durations, cdf, alpha=0.3, color="#3498db")
    axes[1].set_title("Kumulative Verteilung", fontweight='bold')
    axes[1].set_xlabel("Dauer [Tage]")
    axes[1].set_ylabel("Kumulative Häufigkeit [%]")
    axes[1].grid(alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)
    
    print(f"Drought events: {len(events)}")
    print(f"Mean duration: {np.mean(durations):.1f} days")
    print(f"Max duration: {np.max(durations)} days")


def _plot_seasonal_boxplot(df: pd.DataFrame, out_file: Path) -> None:
    """Create seasonal boxplots for drought indices."""
    df["month"] = df["date"].dt.month
    df["season"] = df["month"].map({12: "Winter", 1: "Winter", 2: "Winter",
                                      3: "Frühling", 4: "Frühling", 5: "Frühling",
                                      6: "Sommer", 7: "Sommer", 8: "Sommer",
                                      9: "Herbst", 10: "Herbst", 11: "Herbst"})
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    indices = [
        ("smi_percent", "SMI Percentil"),
        ("recharge_percent", "Recharge Percentil"),
        ("runoff_percent", "Runoff Percentil"),
        ("ssi", "Standardized Soil Index")
    ]
    
    for ax, (col, title) in zip(axes, indices):
        sns.boxplot(data=df, x="season", y=col, ax=ax, 
                   order=["Frühling", "Sommer", "Herbst", "Winter"],
                   palette="Set2")
        ax.set_title(title, fontweight='bold')
        ax.set_xlabel("")
        ax.set_ylabel("Wert")
        ax.axhline(20 if "percent" in col else -1, color="red", 
                  linestyle="--", alpha=0.5, label="Dürre-Schwelle")
    
    fig.tight_layout()
    fig.savefig(out_file, dpi=200, bbox_inches="tight", facecolor='white')
    plt.close(fig)


def _create_summary_report(df: pd.DataFrame, paths: Paths) -> None:
    """Create markdown summary report with key statistics."""
    summary_lines = [
        "# Dürre-Analyse Zusammenfassung",
        "",
        f"**Analyse-Datum:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Zeitraum:** {df['date'].min().strftime('%Y-%m-%d')} bis {df['date'].max().strftime('%Y-%m-%d')}",
        "",
        "## Statistische Kennzahlen",
        "",
        "### Bodenfeuchte",
        f"- Mittelwert: {df['sm'].mean():.4f} m³/m³",
        f"- Standardabweichung: {df['sm'].std():.4f}",
        f"- Minimum: {df['sm'].min():.4f} ({df.loc[df['sm'].idxmin(), 'date'].strftime('%Y-%m-%d')})",
        f"- Maximum: {df['sm'].max():.4f} ({df.loc[df['sm'].idxmax(), 'date'].strftime('%Y-%m-%d')})",
        "",
        "### Recharge",
        f"- Mittelwert: {df['recharge'].mean():.2f} mm/Tag",
        f"- Minimum: {df['recharge'].min():.2f} mm/Tag",
        f"- Maximum: {df['recharge'].max():.2f} mm/Tag",
        "",
        "### Dürre-Indizes",
        f"- SMI < 20 (schwere Dürre): {(df['smi_percent'] < 20).sum()} Monate ({(df['smi_percent'] < 20).mean()*100:.1f}%)",
        f"- SSI < -1 (moderate Dürre): {(df['ssi'] < -1).sum()} Monate",
        f"- SSI < -2 (schwere Dürre): {(df['ssi'] < -2).sum()} Monate",
        "",
        "### Klassifikation",
    ]
    
    class_counts = df["drought_class"].value_counts()
    for cls, count in class_counts.items():
        pct = count / len(df) * 100
        summary_lines.append(f"- {cls}: {count} Monate ({pct:.1f}%)")
    
    summary_lines.extend(["", "## Erstellte Plots", ""])
    summary_lines.append(f"Alle Plots befinden sich im Verzeichnis `{paths.plot_dir}`")
    
    # Write summary
    summary_path = paths.results_dir / "analysis_summary.md"
    with open(summary_path, "w") as f:
        f.write("\n".join(summary_lines))
    
    print(f"Summary report: {summary_path}")


def main() -> None:
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Drought pipeline (normal plots)")
    parser.add_argument(
        "--domain",
        choices=["test_domain", "catchment_custom"],
        default=None,
        help="Convenience domain selector",
    )
    parser.add_argument(
        "--mhm-output-dir",
        default="code/mhm/test_domain/output_b1",
        help="Path to mHM output directory containing mHM_Fluxes_States.nc and discharge.nc",
    )
    parser.add_argument(
        "--domain-subdir",
        default="test_domain",
        help="Domain folder under analysis/plots and analysis/results",
    )
    args = parser.parse_args()

    # Domain shortcut overrides defaults when selected.
    if args.domain == "test_domain":
        args.mhm_output_dir = "code/mhm/test_domain/output_b1"
        args.domain_subdir = "test_domain"
    elif args.domain == "catchment_custom":
        args.mhm_output_dir = "code/mhm/catchment_custom/output_90410700"
        args.domain_subdir = "custom_catchment"

    paths = _paths(args.mhm_output_dir, args.domain_subdir)
    paths.results_dir.mkdir(parents=True, exist_ok=True)
    paths.plot_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DROUGHT PIPELINE v2.0 - Modern & Discrete")
    print("=" * 60)
    
    # Load data
    print("Loading monthly mHM data...")
    monthly = _load_monthly(paths)
    print(f"  Loaded {len(monthly)} monthly records")
    
    print("Loading daily discharge data...")
    daily_discharge, monthly_discharge = _load_daily_discharge(paths)
    print(f"  Loaded {len(daily_discharge)} daily discharge records")
    
    # Merge data
    merged = monthly.merge(
        monthly_discharge[["date", "qsim_monthly_mean", "qsim_monthly_min", 
                           "qsim_monthly_max", "qsim_monthly_std", "discharge_percent", "sdi"]],
        on="date",
        how="left",
    )

    if "discharge_percent" not in merged.columns:
        if "discharge_percent_x" in merged.columns:
            merged["discharge_percent"] = merged["discharge_percent_x"]
        elif "discharge_percent_y" in merged.columns:
            merged["discharge_percent"] = merged["discharge_percent_y"]
    if "sdi" not in merged.columns:
        if "sdi_x" in merged.columns:
            merged["sdi"] = merged["sdi_x"]
        elif "sdi_y" in merged.columns:
            merged["sdi"] = merged["sdi_y"]

    if "discharge_percent" not in merged.columns or merged["discharge_percent"].isna().all():
        if "qsim_monthly_mean" in merged.columns:
            merged["discharge_percent"] = _percentile(merged["qsim_monthly_mean"])
    if "sdi" not in merged.columns or merged["sdi"].isna().all():
        if "discharge_percent" in merged.columns:
            merged["sdi"] = _standardized_from_percentile(merged["discharge_percent"])
    
    # Classify drought
    merged["drought_class"] = merged.apply(_classify_drought, axis=1)
    
    # Create plots
    print("\nCreating plots...")
    
    print("  - Time series (modern style)...")
    _plot_timeseries_modern(merged, paths.plot_dir / "01_drought_timeseries.png")
    
    print("  - SMI heatmap (discrete)...")
    _plot_heatmap_discrete(merged, "smi_percent", "SMI Dürre-Klassifikation", 
                           paths.plot_dir / "02_heatmap_smi_discrete.png")
    
    print("  - Recharge heatmap (discrete)...")
    _plot_heatmap_discrete(merged, "recharge_percent", "Recharge Dürre-Klassifikation",
                           paths.plot_dir / "03_heatmap_recharge_discrete.png")
    
    print("  - Discharge heatmap (discrete)...")
    _plot_heatmap_discrete(merged, "discharge_percent", "Abfluss Dürre-Klassifikation",
                           paths.plot_dir / "04_heatmap_discharge_discrete.png")
    
    print("  - Discharge validation...")
    _plot_discharge_validation(daily_discharge, paths.plot_dir / "05_discharge_analysis.png")
    
    print("  - Correlation matrix...")
    _plot_correlation_matrix(merged, paths.plot_dir / "06_correlation_matrix.png")
    
    print("  - Drought duration analysis...")
    _plot_drought_duration(merged, paths.plot_dir / "07_drought_duration.png")
    
    print("  - Seasonal boxplots...")
    _plot_seasonal_boxplot(merged, paths.plot_dir / "08_seasonal_boxplots.png")
    
    # Save CSVs
    print("\nSaving results...")
    merged.to_csv(paths.results_dir / "monthly_drought_indices.csv", index=False)
    daily_discharge.to_csv(paths.results_dir / "daily_discharge.csv", index=False)
    
    # Create summary report
    _create_summary_report(merged, paths)
    
    # Calculate statistics
    summary = (
        merged.assign(year=merged["date"].dt.year)
        .groupby("year", as_index=False)
        .agg(
            min_smi=("smi_percent", "min"),
            min_recharge=("recharge_percent", "min"),
            min_runoff=("runoff_percent", "min"),
            min_discharge=("discharge_percent", "min"),
            drought_months=("drought_class", lambda s: int((s != "normal_or_wet").sum())),
        )
    )
    summary.to_csv(paths.results_dir / "annual_drought_summary.csv", index=False)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)
    print(f"Plots: {paths.plot_dir}")
    print(f"Results: {paths.results_dir}")


if __name__ == "__main__":
    main()
