#!/usr/bin/env python3
"""03_create_plots.py — Create Drought Visualizations for PhD Paper #1.

Creates all 10 standard plots:
1.  01_drought_timeseries.png — SMI/R-Pctl/Q-Pctl/MDI time series
2.  02_heatmap_smi.png — Soil moisture interannual heatmap
3.  03_heatmap_recharge.png — Recharge deficits heatmap
4.  04_heatmap_discharge.png — Discharge deficits heatmap
5.  05_discharge_analysis.png — Qobs vs Qsim validation (KGE, NSE)
6.  06_correlation_matrix.png — Compartment coupling
7.  07_drought_duration.png — Event persistence
8.  08_seasonal_boxplots.png — Monthly distributions
9.  09_lag_correlation.png — Cross-correlations with lag
10. 10_matrix_drought_index.png — MDI integrated view
11. 11_discharge_metrics_timeseries.png — Annual discharge metrics over time

QUALITY FEATURES:
- High-resolution (300 DPI)
- Scientific color schemes (colorblind-friendly)
- Clear labels and legends
- Consistent styling across all plots
- Export to PNG + optional PDF

Usage:
    python 03_create_plots.py --catchment Chemnitz2_0p0625
    python 03_create_plots.py --catchment all
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO = Path(__file__).resolve().parents[2]

# Plot settings
DPI = 300
FIG_SIZE_LARGE = (14, 10)
FIG_SIZE_MEDIUM = (12, 8)
FIG_SIZE_SMALL = (10, 6)

# Color schemes (colorblind-friendly)
COLORS = {
    "smi": "#2E86AB",      # Blue
    "recharge": "#A23B72", # Purple
    "discharge": "#F18F01", # Orange
    "mdi": "#C73E1D",      # Red
    "precip": "#6A994E",   # Green
    "pet": "#BC4749",      # Dark red
}

# Drought class colors (per German Drought Monitor style)
DROUGHT_COLORS = {
    "extreme_drought": "#8B0000",  # Dark red
    "severe_drought": "#FF4500",   # Orange-red
    "moderate_drought": "#FFA500", # Orange
    "mild_drought": "#FFD700",     # Yellow
    "normal_or_wet": "#90EE90",    # Light green
    "unknown": "#CCCCCC",          # Gray
}

# Set style
sns.set_style("whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.titlesize"] = 12


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def ensure_dir(path: Path):
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def save_plot(fig, path: Path, dpi: int = DPI):
    """Save figure with proper cleanup."""
    ensure_dir(path.parent)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


def _calendar_month_key(dates: pd.Series) -> pd.Series:
    """Extract month for grouping."""
    return pd.to_datetime(dates).dt.month


def _year_month_series(dates: pd.Series) -> pd.Series:
    """Extract year-month for time series."""
    return pd.to_datetime(dates).dt.to_period("M")


# =============================================================================
# PLOT 01: DROUGHT TIME SERIES
# =============================================================================

def plot_drought_timeseries(df: pd.DataFrame, output_path: Path):
    """Plot 01: Time series of all drought indices."""
    fig, axes = plt.subplots(4, 1, figsize=FIG_SIZE_LARGE, sharex=True)
    
    dates = pd.to_datetime(df["date"])
    
    # SMI
    ax = axes[0]
    ax.plot(dates, df["smi"], color=COLORS["smi"], linewidth=1.5, label="SMI")
    ax.axhline(20, color="gray", linestyle="--", alpha=0.5, label="Drought threshold")
    ax.axhline(10, color="orange", linestyle="--", alpha=0.5)
    ax.axhline(5, color="red", linestyle="--", alpha=0.5)
    ax.axhline(2, color="darkred", linestyle="--", alpha=0.5)
    ax.set_ylabel("Percentile")
    ax.set_title("Soil Moisture Index (SMI)", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    
    # Recharge Percentile
    ax = axes[1]
    ax.plot(dates, df["r_pctl"], color=COLORS["recharge"], linewidth=1.5, label="R-Pctl")
    ax.axhline(20, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("Percentile")
    ax.set_title("Recharge Percentile", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    
    # Discharge Percentile
    ax = axes[2]
    ax.plot(dates, df["q_pctl"], color=COLORS["discharge"], linewidth=1.5, label="Q-Pctl")
    ax.axhline(20, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("Percentile")
    ax.set_title("Discharge Percentile", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    
    # MDI
    ax = axes[3]
    ax.plot(dates, df["mdi"], color=COLORS["mdi"], linewidth=2, label="MDI")
    ax.axhline(20, color="gray", linestyle="--", alpha=0.5, label="Drought threshold")
    ax.set_ylabel("Index (0-100)")
    ax.set_xlabel("Date")
    ax.set_title("Matrix Drought Index (MDI)", fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    
    # Format x-axis
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# PLOT 02-04: HEATMAPS (SMI, RECHARGE, DISCHARGE)
# =============================================================================

def plot_heatmap(df: pd.DataFrame, column: str, title: str, output_path: Path):
    """Plot interannual heatmap (year vs month).
    
    Aggregates daily data to monthly means before pivoting.
    """
    dates = pd.to_datetime(df["date"])
    
    # Aggregate daily to monthly mean first
    df_monthly = df.copy()
    df_monthly["date"] = pd.to_datetime(df_monthly["date"])
    df_monthly["year"] = df_monthly["date"].dt.year
    df_monthly["month"] = df_monthly["date"].dt.month
    
    # Group by year/month and take mean
    df_agg = df_monthly.groupby(["year", "month"])[column].mean().reset_index()
    
    # Create pivot table (year x month)
    pivot = df_agg.pivot(index="year", columns="month", values=column)
    
    # Create figure
    fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
    
    # Color map (blue = wet, red = dry)
    cmap = plt.cm.RdYlBu_r
    vmin, vmax = 0, 100
    
    im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation="nearest")
    
    # Labels
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    
    # Month labels
    month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    ax.set_xticks(range(12))
    ax.set_xticklabels(month_labels)
    
    # Year labels
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Percentile")
    
    # Drought threshold lines
    ax.axhline(y=pivot.index.tolist().index(2018) if 2018 in pivot.index else -1, 
               color="red", linestyle="-", linewidth=2, alpha=0.5, label="2018 drought")
    
    fig.tight_layout()
    save_plot(fig, output_path)


def plot_heatmap_smi(df: pd.DataFrame, output_path: Path):
    """Plot 02: SMI heatmap."""
    plot_heatmap(df, "smi", "Soil Moisture Index (SMI) — Interannual Heatmap", output_path)


def plot_heatmap_recharge(df: pd.DataFrame, output_path: Path):
    """Plot 03: Recharge heatmap."""
    plot_heatmap(df, "r_pctl", "Recharge Percentile — Interannual Heatmap", output_path)


def plot_heatmap_discharge(df: pd.DataFrame, output_path: Path):
    """Plot 04: Discharge heatmap."""
    plot_heatmap(df, "q_pctl", "Discharge Percentile — Interannual Heatmap", output_path)


# =============================================================================
# PLOT 05: DISCHARGE VALIDATION
# =============================================================================

def plot_discharge_analysis(df: pd.DataFrame, output_path: Path):
    """Plot 05: Qobs vs Qsim validation with metrics."""
    if "qobs" not in df.columns:
        print(f"  ⚠ No Qobs available, skipping discharge validation")
        # Create placeholder
        fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
        ax.text(0.5, 0.5, "No Qobs data available", ha="center", va="center", fontsize=14)
        ax.set_title("Discharge Validation", fontweight="bold")
        ax.axis("off")
        save_plot(fig, output_path)
        return
    
    # Remove NaN
    valid = ~(np.isnan(df["qobs"]) | np.isnan(df["qsim"]))
    qobs = df.loc[valid, "qobs"]
    qsim = df.loc[valid, "qsim"]
    
    if len(qobs) < 10:
        print(f"  ⚠ Not enough valid data for discharge validation")
        return
    
    def compute_metrics(obs: pd.Series, sim: pd.Series) -> Dict[str, float]:
        obs = pd.Series(obs, dtype=float)
        sim = pd.Series(sim, dtype=float)
        valid = ~(obs.isna() | sim.isna())
        obs = obs[valid]
        sim = sim[valid]
        if len(obs) < 10:
            return {k: np.nan for k in ["kge", "nse", "rmse", "mae", "r", "bias", "alpha", "beta"]}

        r, _ = pearsonr(obs, sim)
        mean_obs = obs.mean()
        mean_sim = sim.mean()
        rmse = np.sqrt(np.mean((sim - obs) ** 2))
        mae = np.mean(np.abs(sim - obs))
        nse_denom = np.sum((obs - mean_obs) ** 2)
        nse = 1 - np.sum((sim - obs) ** 2) / nse_denom if nse_denom > 0 else np.nan
        std_obs = obs.std()
        std_sim = sim.std()
        alpha = std_sim / std_obs if std_obs > 0 else np.nan
        beta = mean_sim / mean_obs if mean_obs != 0 else np.nan
        kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
        bias = (mean_sim - mean_obs) / mean_obs * 100 if mean_obs != 0 else np.nan
        return {
            "kge": float(kge), "nse": float(nse), "rmse": float(rmse), "mae": float(mae),
            "r": float(r), "bias": float(bias), "alpha": float(alpha), "beta": float(beta),
        }

    m = compute_metrics(qobs, qsim)
    kge, nse, rmse, mae = m["kge"], m["nse"], m["rmse"], m["mae"]
    r, bias, alpha, beta = m["r"], m["bias"], m["alpha"], m["beta"]
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE_LARGE)
    
    # Time series
    ax = axes[0, 0]
    dates = pd.to_datetime(df.loc[valid, "date"])
    ax.plot(dates, qobs, color="blue", linewidth=1, label="Qobs", alpha=0.7)
    ax.plot(dates, qsim, color="red", linewidth=1, label="Qsim", alpha=0.7)
    ax.set_xlabel("Date")
    ax.set_ylabel("Discharge [input units]")
    ax.set_title("Time Series Comparison", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Scatter plot
    ax = axes[0, 1]
    ax.scatter(qobs, qsim, alpha=0.3, s=10, color="gray")
    ax.plot([qobs.min(), qobs.max()], [qobs.min(), qobs.max()], "r--", linewidth=2, label="1:1 line")
    ax.set_xlabel("Qobs [input units]")
    ax.set_ylabel("Qsim [input units]")
    ax.set_title(f"Scatter Plot (r = {r:.3f})", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Flow duration curve
    ax = axes[1, 0]
    qobs_sorted = np.sort(qobs)[::-1]
    qsim_sorted = np.sort(qsim)[::-1]
    exceedance = np.arange(1, len(qobs_sorted) + 1) / len(qobs_sorted) * 100
    ax.semilogy(exceedance, qobs_sorted, "b-", linewidth=2, label="Qobs")
    ax.semilogy(exceedance, qsim_sorted, "r-", linewidth=2, label="Qsim")
    ax.set_xlabel("Exceedance Probability [%]")
    ax.set_ylabel("Discharge [input units] (log scale)")
    ax.set_title("Flow Duration Curve", fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Metrics table
    ax = axes[1, 1]
    ax.axis("off")
    
    metrics_text = (
        f"Discharge Validation Metrics\n"
        f"{'='*35}\n\n"
        f"KGE (Kling-Gupta):    {kge:.3f}\n"
        f"NSE (Nash-Sutcliffe): {nse:.3f}\n"
        f"Pearson r:            {r:.3f}\n"
        f"Bias:                 {bias:+.1f}%\n"
        f"RMSE:                 {rmse:.3f}\n"
        f"MAE:                  {mae:.3f}\n\n"
        f"α (variability):      {alpha:.3f}\n"
        f"β (bias):             {beta:.3f}"
    )
    
    ax.text(0.1, 0.5, metrics_text, fontsize=11, verticalalignment="center",
            family="monospace", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))
    ax.set_title("Validation Metrics", fontweight="bold", pad=20)
    
    fig.tight_layout()
    save_plot(fig, output_path)


def plot_discharge_metrics_timeseries(df: pd.DataFrame, output_path: Path):
    """Plot 11: Yearly discharge skill metrics (KGE/NSE/RMSE/MAE/r/Bias)."""
    if "qobs" not in df.columns:
        fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
        ax.text(0.5, 0.5, "No Qobs data available", ha="center", va="center", fontsize=14)
        ax.set_title("Discharge Metrics Over Time", fontweight="bold")
        ax.axis("off")
        save_plot(fig, output_path)
        return

    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["year"] = d["date"].dt.year
    d = d[["year", "qobs", "qsim"]].dropna()
    if len(d) < 30:
        fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
        ax.text(0.5, 0.5, "Not enough Qobs/Qsim overlap", ha="center", va="center", fontsize=14)
        ax.set_title("Discharge Metrics Over Time", fontweight="bold")
        ax.axis("off")
        save_plot(fig, output_path)
        return

    def metrics(obs: pd.Series, sim: pd.Series) -> Dict[str, float]:
        if len(obs) < 30:
            return {k: np.nan for k in ["kge", "nse", "rmse", "mae", "r", "bias"]}
        r, _ = pearsonr(obs, sim)
        mean_obs = obs.mean()
        mean_sim = sim.mean()
        rmse = np.sqrt(np.mean((sim - obs) ** 2))
        mae = np.mean(np.abs(sim - obs))
        nse_denom = np.sum((obs - mean_obs) ** 2)
        nse = 1 - np.sum((sim - obs) ** 2) / nse_denom if nse_denom > 0 else np.nan
        std_obs = obs.std()
        std_sim = sim.std()
        alpha = std_sim / std_obs if std_obs > 0 else np.nan
        beta = mean_sim / mean_obs if mean_obs != 0 else np.nan
        kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
        bias = (mean_sim - mean_obs) / mean_obs * 100 if mean_obs != 0 else np.nan
        return {"kge": kge, "nse": nse, "rmse": rmse, "mae": mae, "r": r, "bias": bias}

    rows = []
    for year, g in d.groupby("year"):
        m = metrics(g["qobs"], g["qsim"])
        m["year"] = year
        rows.append(m)
    mdf = pd.DataFrame(rows).sort_values("year")

    fig, axes = plt.subplots(3, 2, figsize=FIG_SIZE_LARGE, sharex=True)
    fields = [
        ("kge", "KGE", "tab:blue"),
        ("nse", "NSE", "tab:orange"),
        ("r", "Pearson r", "tab:green"),
        ("bias", "Bias [%]", "tab:red"),
        ("rmse", "RMSE", "tab:purple"),
        ("mae", "MAE", "tab:brown"),
    ]

    for ax, (field, title, color) in zip(axes.flatten(), fields):
        ax.plot(mdf["year"], mdf[field], marker="o", color=color, linewidth=1.8)
        ax.set_title(title, fontweight="bold")
        ax.grid(alpha=0.3)
        if field in {"kge", "nse", "r"}:
            ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
        if field == "bias":
            ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
        ax.set_ylabel(title)

    for ax in axes[-1, :]:
        ax.set_xlabel("Year")

    fig.suptitle("Discharge Validation Metrics by Year", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save_plot(fig, output_path)


# =============================================================================
# PLOT 06: CORRELATION MATRIX
# =============================================================================

def plot_correlation_matrix(df: pd.DataFrame, output_path: Path):
    """Plot 06: Correlation matrix between all compartments."""
    # Select variables
    vars_map = {
        "Precip": "precip",
        "PET": "pet",
        "SMI": "smi",
        "Recharge": "r_pctl",
        "Discharge": "q_pctl",
        "MDI": "mdi",
    }
    
    # Calculate correlation matrix
    corr_matrix = pd.DataFrame(index=vars_map.keys(), columns=vars_map.keys(), dtype=float)
    
    for name1, col1 in vars_map.items():
        for name2, col2 in vars_map.items():
            if col1 in df.columns and col2 in df.columns:
                valid = ~(np.isnan(df[col1]) | np.isnan(df[col2]))
                if valid.sum() > 10:
                    corr, _ = pearsonr(df.loc[valid, col1], df.loc[valid, col2])
                    corr_matrix.loc[name1, name2] = corr
                else:
                    corr_matrix.loc[name1, name2] = np.nan
            else:
                corr_matrix.loc[name1, name2] = np.nan
    
    # Create figure
    fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
    
    # Heatmap
    im = ax.imshow(corr_matrix.values.astype(float), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    
    # Labels
    ax.set_xticks(range(len(vars_map)))
    ax.set_yticks(range(len(vars_map)))
    ax.set_xticklabels(vars_map.keys(), rotation=45, ha="right")
    ax.set_yticklabels(vars_map.keys())
    
    # Title
    ax.set_title("Correlation Matrix (Pearson r)", fontweight="bold")
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Correlation coefficient (r)")
    
    # Annotate with values
    for i in range(len(vars_map)):
        for j in range(len(vars_map)):
            val = corr_matrix.iloc[i, j]
            if not np.isnan(val):
                color = "white" if abs(val) > 0.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# PLOT 07: DROUGHT DURATION
# =============================================================================

def plot_drought_duration(df: pd.DataFrame, output_path: Path):
    """Plot 07: Drought event duration distribution."""
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE_LARGE)
    
    for idx, (col, title) in enumerate(zip(
        ["smi", "r_pctl", "q_pctl", "mdi"],
        ["SMI", "Recharge", "Discharge", "MDI"]
    )):
        ax = axes[idx // 2, idx % 2]
        
        if f"{col}_class" not in df.columns:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            continue
        
        # Identify drought events (consecutive drought months)
        is_drought = df[f"{col}_class"].isin([
            "extreme_drought", "severe_drought", "moderate_drought", "mild_drought"
        ])
        
        # Find event starts and ends
        event_id = (~is_drought).cumsum()
        event_lengths = is_drought.groupby(event_id).sum()
        event_lengths = event_lengths[event_lengths > 0]  # Remove non-drought periods
        
        if len(event_lengths) == 0:
            ax.text(0.5, 0.5, "No drought events", ha="center", va="center")
            continue
        
        # Plot histogram
        ax.hist(event_lengths, bins=range(1, int(event_lengths.max()) + 2), 
                edgecolor="black", alpha=0.7, color=COLORS.get(col, "gray"))
        ax.set_xlabel("Event duration [months]")
        ax.set_ylabel("Frequency")
        ax.set_title(f"{title} — Drought Event Duration", fontweight="bold")
        ax.grid(alpha=0.3)
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# PLOT 08: SEASONAL BOXPLOTS
# =============================================================================

def plot_seasonal_boxplots(df: pd.DataFrame, output_path: Path):
    """Plot 08: Seasonal distributions (boxplots by month)."""
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE_LARGE)
    
    dates = pd.to_datetime(df["date"])
    df_plot = df.copy()
    df_plot["month"] = dates.dt.month
    df_plot["month_name"] = dates.dt.month_name()
    
    month_order = range(1, 13)
    month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    
    for idx, (col, title) in enumerate(zip(
        ["smi", "r_pctl", "q_pctl", "mdi"],
        ["SMI", "Recharge Percentile", "Discharge Percentile", "MDI"]
    )):
        ax = axes[idx // 2, idx % 2]
        
        # Boxplot by month
        data_by_month = [df_plot.loc[df_plot["month"] == m, col].dropna() for m in month_order]
        
        bp = ax.boxplot(data_by_month, positions=range(1, 13), widths=0.6,
                       patch_artist=True, labels=month_labels)
        
        # Color boxes
        for patch in bp["boxes"]:
            patch.set_facecolor(COLORS.get(col, "lightblue"))
            patch.set_alpha(0.7)
        
        ax.set_xlabel("Month")
        ax.set_ylabel("Index value")
        ax.set_title(f"{title} — Seasonal Distribution", fontweight="bold")
        ax.grid(alpha=0.3, axis="y")
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# PLOT 09: LAG CORRELATION
# =============================================================================

def plot_lag_correlation(df: pd.DataFrame, output_path: Path):
    """Plot 09: Cross-correlation with lag analysis."""
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE_LARGE)
    
    # Calculate lag correlations
    def calc_lag_corr(x: pd.Series, y: pd.Series, max_lag: int = 12):
        """Calculate correlation at different lags (in months for daily data)."""
        # Convert to monthly and align both series on identical timestamps first.
        x_monthly = x.resample("ME").mean()
        y_monthly = y.resample("ME").mean()
        aligned = pd.concat([x_monthly.rename("x"), y_monthly.rename("y")], axis=1).dropna()

        if len(aligned) < 20:
            return np.arange(-max_lag, max_lag + 1), np.full(2 * max_lag + 1, np.nan)

        x_clean = aligned["x"]
        y_clean = aligned["y"]

        lags = np.arange(-max_lag, max_lag + 1)
        corr = np.zeros(len(lags))

        for i, lag in enumerate(lags):
            if lag < 0:
                x_shifted = x_clean.iloc[:lag].to_numpy()
                y_shifted = y_clean.iloc[-lag:].to_numpy()
            elif lag > 0:
                x_shifted = x_clean.iloc[lag:].to_numpy()
                y_shifted = y_clean.iloc[:-lag].to_numpy()
            else:
                x_shifted = x_clean.to_numpy()
                y_shifted = y_clean.to_numpy()

            # Ensure both arrays are exactly the same length before pearsonr.
            min_shift_len = min(x_shifted.size, y_shifted.size)
            if min_shift_len < 10:
                corr[i] = np.nan
                continue

            x_shifted = x_shifted[-min_shift_len:]
            y_shifted = y_shifted[-min_shift_len:]

            valid = ~(np.isnan(x_shifted) | np.isnan(y_shifted))
            if valid.sum() > 10 and np.nanstd(x_shifted[valid]) > 0 and np.nanstd(y_shifted[valid]) > 0:
                corr[i], _ = pearsonr(x_shifted[valid], y_shifted[valid])
            else:
                corr[i] = np.nan

        return lags, corr
    
    # Pairs to analyze
    pairs = [
        ("precip", "smi", "Precipitation → SMI", "b"),
        ("smi", "r_pctl", "SMI → Recharge", "g"),
        ("r_pctl", "q_pctl", "Recharge → Discharge", "r"),
    ]
    
    for i, (x_col, y_col, title, color) in enumerate(pairs):
        ax = axes[i // 2, i % 2]
        
        if x_col not in df.columns or y_col not in df.columns:
            ax.text(0.5, 0.5, "No data", ha="center", va="center")
            continue
        
        dates = pd.to_datetime(df["date"])
        x_series = pd.Series(df[x_col].values, index=dates)
        y_series = pd.Series(df[y_col].values, index=dates)
        lags, corr = calc_lag_corr(x_series, y_series, max_lag=12)
        
        ax.plot(lags, corr, color=color, marker="o", linewidth=2, markersize=6)
        ax.axhline(0, color="gray", linestyle="-", alpha=0.3)
        ax.axvline(0, color="gray", linestyle="-", alpha=0.3)
        ax.set_xlabel("Lag [months] (positive = y lags x)")
        ax.set_ylabel("Pearson correlation (r)")
        ax.set_title(title, fontweight="bold")
        ax.grid(alpha=0.3)
    
    # Correlation matrix (lag-0)
    ax = axes[1, 1]
    vars_map = {
        "Precip": "precip",
        "SMI": "smi",
        "Recharge": "r_pctl",
        "Discharge": "q_pctl",
        "MDI": "mdi",
    }
    
    corr_matrix = pd.DataFrame(index=vars_map.keys(), columns=vars_map.keys(), dtype=float)
    for name1, col1 in vars_map.items():
        for name2, col2 in vars_map.items():
            if col1 in df.columns and col2 in df.columns:
                valid = ~(np.isnan(df[col1]) | np.isnan(df[col2]))
                if valid.sum() > 10:
                    corr, _ = pearsonr(df.loc[valid, col1], df.loc[valid, col2])
                    corr_matrix.loc[name1, name2] = corr
    
    im = ax.imshow(corr_matrix.values.astype(float), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(vars_map)))
    ax.set_yticks(range(len(vars_map)))
    ax.set_xticklabels(vars_map.keys(), rotation=45, ha="right")
    ax.set_yticklabels(vars_map.keys())
    ax.set_title("Lag-0 Correlation Matrix", fontweight="bold")
    plt.colorbar(im, ax=ax, shrink=0.8)
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# PLOT 10: MATRIX DROUGHT INDEX (INTEGRATED)
# =============================================================================

def plot_matrix_drought_index(df: pd.DataFrame, output_path: Path):
    """Plot 10: MDI integrated view (heatmap + time series + composition)."""
    dates = pd.to_datetime(df["date"])
    
    # Create figure
    fig = plt.figure(figsize=(14, 14))
    
    # Top: MDI heatmap (year x month)
    ax1 = plt.subplot(3, 1, 1)
    
    # Aggregate daily to monthly mean first
    df_plot = df.copy()
    df_plot["date"] = pd.to_datetime(df_plot["date"])
    df_plot["year"] = df_plot["date"].dt.year
    df_plot["month"] = df_plot["date"].dt.month
    
    # Group by year/month and take mean
    df_agg = df_plot.groupby(["year", "month"])["mdi"].mean().reset_index()
    pivot = df_agg.pivot_table(index="year", columns="month", values="mdi", aggfunc="mean")
    
    # Custom colormap for MDI
    colors = ["#8B0000", "#FF4500", "#FFA500", "#FFD700", "#90EE90"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [0, 20, 40, 60, 80, 100]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    im = ax1.imshow(pivot.values, aspect="auto", cmap=cmap, norm=norm)
    ax1.set_title("Matrix Drought Index (MDI) — Interannual Overview", fontweight="bold", fontsize=14)
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Year")
    
    month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    ax1.set_xticks(range(12))
    ax1.set_xticklabels(month_labels)
    ax1.set_yticks(range(len(pivot.index)))
    ax1.set_yticklabels(pivot.index)
    
    cbar = plt.colorbar(im, ax=ax1, boundaries=bounds, ticks=[10, 30, 50, 70, 90], shrink=0.8)
    cbar.set_label("MDI Value")
    
    # Middle: MDI time series with components
    ax2 = plt.subplot(3, 1, 2)
    
    ax2.plot(dates, df["mdi"] / 100, color="black", linewidth=2.5, label="MDI", zorder=5)
    ax2.plot(dates, df["smi"] / 100, alpha=0.6, linewidth=1.5, label="SMI (40%)", color=COLORS["smi"])
    ax2.plot(dates, df["r_pctl"] / 100, alpha=0.6, linewidth=1.5, label="R-Pctl (30%)", color=COLORS["recharge"])
    ax2.plot(dates, df["q_pctl"] / 100, alpha=0.6, linewidth=1.5, label="Q-Pctl (30%)", color=COLORS["discharge"])
    
    ax2.fill_between(dates, 0, 0.2, color="#8B0000", alpha=0.2, label="Extreme drought")
    ax2.fill_between(dates, 0.2, 0.4, color="#FF4500", alpha=0.2, label="Severe drought")
    
    ax2.set_ylabel("Normalized Index (0-1)")
    ax2.set_title("MDI Time Series with Components", fontweight="bold", fontsize=14)
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(alpha=0.3)
    ax2.set_ylim(0, 1)
    
    # Bottom: Drought class composition by year
    ax3 = plt.subplot(3, 1, 3)
    
    if "mdi_class" in df.columns:
        df_plot["mdi_class"] = df["mdi_class"]
        class_counts = df_plot.groupby("year")["mdi_class"].value_counts().unstack(fill_value=0)
        
        # Order classes
        class_order = ["extreme_drought", "severe_drought", "moderate_drought", "mild_drought", "normal_or_wet"]
        class_colors = [DROUGHT_COLORS[c] for c in class_order if c in class_counts.columns]
        
        bottom = np.zeros(len(class_counts))
        for i, cls in enumerate(class_order):
            if cls in class_counts.columns:
                ax3.bar(class_counts.index, class_counts[cls], bottom=bottom,
                       color=DROUGHT_COLORS[cls], label=cls.replace("_", " ").title())
                bottom += class_counts[cls]
        
        ax3.set_xlabel("Year")
        ax3.set_ylabel("Months")
        ax3.set_title("MDI Drought Class Composition by Year", fontweight="bold", fontsize=14)
        ax3.legend(loc="upper right", fontsize=9)
        ax3.grid(alpha=0.3, axis="y")
    
    fig.tight_layout()
    save_plot(fig, output_path)


# =============================================================================
# MAIN PLOTTER
# =============================================================================

def create_all_plots(df: pd.DataFrame, plot_dir: Path, catchment_name: str):
    """Create standard drought analysis plots."""
    print(f"Creating plots for {catchment_name}...")
    
    plots = [
        ("01_drought_timeseries.png", plot_drought_timeseries),
        ("02_heatmap_smi.png", plot_heatmap_smi),
        ("03_heatmap_recharge.png", plot_heatmap_recharge),
        ("04_heatmap_discharge.png", plot_heatmap_discharge),
        ("05_discharge_analysis.png", plot_discharge_analysis),
        ("06_correlation_matrix.png", plot_correlation_matrix),
        ("07_drought_duration.png", plot_drought_duration),
        ("08_seasonal_boxplots.png", plot_seasonal_boxplots),
        ("09_lag_correlation.png", plot_lag_correlation),
        ("10_matrix_drought_index.png", plot_matrix_drought_index),
        ("11_discharge_metrics_timeseries.png", plot_discharge_metrics_timeseries),
    ]
    
    for filename, plot_func in plots:
        try:
            output_path = plot_dir / filename
            plot_func(df, output_path)
        except Exception as e:
            print(f"  ❌ Error creating {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ All plots created: {plot_dir}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="03_create_plots.py — Create drought visualizations")
    parser.add_argument("--catchment", type=str, default="Chemnitz2_0p0625",
                        help="Catchment name or 'all' for all")
    parser.add_argument("--input-dir", type=Path, default=None,
                        help="Input directory (default: analysis/results/<catchment>)")
    parser.add_argument("--plot-dir", type=Path, default=None,
                        help="Plot output directory (default: analysis/plots/<catchment>)")
    args = parser.parse_args()
    
    # Import catchment list
    import sys
    import importlib.util
    script_path = REPO / "analysis" / "scripts" / "01_load_data.py"
    spec = importlib.util.spec_from_file_location("load_data", script_path)
    load_data_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(load_data_module)
    CATCHMENTS = load_data_module.CATCHMENTS
    
    # Determine catchments
    if args.catchment == "all":
        catchments_to_process = list(CATCHMENTS.keys())
    else:
        catchments_to_process = [args.catchment]
    
    for catchment_name in catchments_to_process:
        print(f"\n{'='*60}")
        print(f"Processing: {catchment_name}")
        print(f"{'='*60}")
        
        try:
            # Input directory
            if args.input_dir:
                input_dir = args.input_dir / catchment_name
            else:
                input_dir = REPO / "analysis" / "results" / catchment_name
            
            # Load indices
            indices_path = input_dir / "drought_indices.parquet"
            if not indices_path.exists():
                indices_path = input_dir / "drought_indices.csv"
            
            if not indices_path.exists():
                raise FileNotFoundError(
                    f"No indices found in {input_dir}. Run 02_compute_indices.py first!"
                )
            
            print(f"  → Loading indices from {indices_path}")
            if indices_path.suffix == ".parquet":
                df = pd.read_parquet(indices_path)
            else:
                df = pd.read_csv(indices_path, parse_dates=["date"])
            
            # Plot directory
            if args.plot_dir:
                plot_dir = args.plot_dir / catchment_name
            else:
                plot_dir = REPO / "analysis" / "plots" / catchment_name
            
            # Create all plots
            create_all_plots(df, plot_dir, catchment_name)
            
        except Exception as e:
            print(f"\n❌ Error processing {catchment_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("All catchments processed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
