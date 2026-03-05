#!/usr/bin/env python3
"""04_advanced_analysis.py — Advanced scientific drought analysis plots.

Creates six additional plots (A-F):
A. Drought propagation analysis (precip -> SMI -> recharge -> discharge)
B. Drought event duration survival curves
C. Interannual variability (yearly boxplots)
D. Spatial comparison across catchments (SMI/MDI)
E. Index comparison Taylor diagram (vs SPI-3 reference)
F. Drought onset analysis (component response lags)
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, norm

REPO = Path(__file__).resolve().parents[2]

DPI = 300
FIG_SIZE_LARGE = (14, 10)
FIG_SIZE_MEDIUM = (12, 8)

COLORS = {
    "precip": "#3A86FF",
    "smi": "#2E86AB",
    "r_pctl": "#A23B72",
    "q_pctl": "#F18F01",
    "mdi": "#C73E1D",
}


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def save_plot(fig, path: Path):
    ensure_dir(path.parent)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Saved: {path.name}")


def load_catchments() -> Dict[str, Dict]:
    script_path = REPO / "analysis" / "scripts" / "01_load_data.py"
    spec = importlib.util.spec_from_file_location("load_data", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CATCHMENTS


def load_inputs(catchment: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    res = REPO / "analysis" / "results" / catchment
    idx_path = res / "drought_indices.parquet"
    dat_path = res / "drought_data.parquet"
    if not idx_path.exists():
        raise FileNotFoundError(f"Missing: {idx_path}")
    if not dat_path.exists():
        raise FileNotFoundError(f"Missing: {dat_path}")

    idx = pd.read_parquet(idx_path).copy()
    dat = pd.read_parquet(dat_path).copy()
    idx["date"] = pd.to_datetime(idx["date"])
    dat["date"] = pd.to_datetime(dat["date"])
    return idx, dat


def zscore(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    std = x.std()
    if pd.isna(std) or std == 0:
        return pd.Series(np.nan, index=x.index)
    return (x - x.mean()) / std


def percentile_to_z(s: pd.Series) -> pd.Series:
    p = np.clip(pd.to_numeric(s, errors="coerce") / 100.0, 1e-6, 1 - 1e-6)
    return pd.Series(norm.ppf(p), index=s.index)


def event_lengths(series: pd.Series, threshold: float = 20.0) -> List[int]:
    x = pd.to_numeric(series, errors="coerce").to_numpy()
    dry = np.isfinite(x) & (x < threshold)
    lengths: List[int] = []
    run = 0
    for v in dry:
        if v:
            run += 1
        elif run > 0:
            lengths.append(run)
            run = 0
    if run > 0:
        lengths.append(run)
    return lengths


def onset_dates(series: pd.Series, dates: pd.Series, threshold: float = 20.0) -> pd.DatetimeIndex:
    x = pd.to_numeric(series, errors="coerce")
    d = pd.to_datetime(dates)
    below = x < threshold
    onset = below & (~below.shift(1, fill_value=False))
    return d[onset.fillna(False)]


def plot_a_propagation(idx: pd.DataFrame, dat: pd.DataFrame, out: Path):
    df = idx.merge(dat[["date", "precip"]], on="date", how="left")
    plot_df = pd.DataFrame({
        "date": df["date"],
        "Precip": zscore(df["precip"]),
        "SMI": zscore(percentile_to_z(df["smi"])),
        "Recharge": zscore(percentile_to_z(df["r_pctl"])),
        "Discharge": zscore(percentile_to_z(df["q_pctl"])),
    }).dropna()

    fig, ax = plt.subplots(figsize=FIG_SIZE_LARGE)
    ax.plot(plot_df["date"], plot_df["Precip"], color=COLORS["precip"], lw=1.0, alpha=0.8, label="Precip (z)")
    ax.plot(plot_df["date"], plot_df["SMI"], color=COLORS["smi"], lw=1.2, label="SMI (z)")
    ax.plot(plot_df["date"], plot_df["Recharge"], color=COLORS["r_pctl"], lw=1.2, label="Recharge Pctl (z)")
    ax.plot(plot_df["date"], plot_df["Discharge"], color=COLORS["q_pctl"], lw=1.2, label="Discharge Pctl (z)")
    ax.axvspan(pd.Timestamp("2018-01-01"), pd.Timestamp("2020-12-31"), color="gray", alpha=0.12, label="2018-2020")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title("A) Drought Propagation: Precip -> SMI -> Recharge -> Discharge", fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel("Standardized anomaly [z]")
    ax.grid(alpha=0.3)
    ax.legend(ncol=3, fontsize=9)
    fig.tight_layout()
    save_plot(fig, out)


def plot_b_survival(idx: pd.DataFrame, out: Path):
    variables = {
        "SMI": idx["smi"],
        "R-Pctl": idx["r_pctl"],
        "Q-Pctl": idx["q_pctl"],
        "MDI": idx["mdi"],
    }
    fig, ax = plt.subplots(figsize=FIG_SIZE_MEDIUM)
    for name, s in variables.items():
        lengths = sorted(event_lengths(s))
        if not lengths:
            continue
        u = np.array(sorted(set(lengths)))
        surv = np.array([(np.array(lengths) >= k).mean() for k in u])
        ax.step(u, surv, where="post", lw=2, label=name)
    ax.set_title("B) Drought Event Duration Survival Curves", fontweight="bold")
    ax.set_xlabel("Event duration [days]")
    ax.set_ylabel("P(Duration >= d)")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    save_plot(fig, out)


def plot_c_interannual(idx: pd.DataFrame, out: Path):
    df = idx.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE_LARGE, sharex=True)
    fields = [("smi", "SMI"), ("r_pctl", "Recharge Pctl"), ("q_pctl", "Discharge Pctl"), ("mdi", "MDI")]
    years = sorted(df["year"].dropna().unique())

    for ax, (col, title) in zip(axes.flatten(), fields):
        data = [df.loc[df["year"] == y, col].dropna() for y in years]
        ax.boxplot(data, tick_labels=[str(y) for y in years], patch_artist=True,
                   boxprops=dict(facecolor="#A8DADC", alpha=0.8))
        for y in [2018, 2019, 2020, 2003]:
            if y in years:
                pos = years.index(y) + 1
                ax.axvspan(pos - 0.5, pos + 0.5, color="#FFB703", alpha=0.15)
        ax.set_title(title, fontweight="bold")
        ax.grid(alpha=0.3, axis="y")
        ax.tick_params(axis="x", rotation=45)
    fig.suptitle("C) Interannual Variability (Yearly Boxplots)", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    save_plot(fig, out)


def plot_d_spatial(catchments: Dict[str, Dict], out: Path):
    rows = []
    for c in catchments.keys():
        p = REPO / "analysis" / "results" / c / "drought_indices.parquet"
        if not p.exists():
            continue
        df = pd.read_parquet(p)[["date", "smi", "mdi"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["catchment"] = c
        rows.append(df)
    if not rows:
        return
    all_df = pd.concat(rows, ignore_index=True)

    fig, axes = plt.subplots(2, 1, figsize=FIG_SIZE_LARGE, sharex=True)
    for c, g in all_df.groupby("catchment"):
        gm = g.set_index("date")[["smi", "mdi"]].resample("ME").mean().reset_index()
        axes[0].plot(gm["date"], gm["smi"], lw=1.2, label=c)
        axes[1].plot(gm["date"], gm["mdi"], lw=1.2, label=c)
    axes[0].set_title("D) Spatial Comparison: SMI", fontweight="bold")
    axes[1].set_title("D) Spatial Comparison: MDI", fontweight="bold")
    axes[0].set_ylabel("SMI")
    axes[1].set_ylabel("MDI")
    axes[1].set_xlabel("Date")
    for ax in axes:
        ax.grid(alpha=0.3)
        ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    save_plot(fig, out)


def plot_e_taylor(idx: pd.DataFrame, out: Path):
    if "spi_3" not in idx.columns:
        return
    ref = pd.to_numeric(idx["spi_3"], errors="coerce")
    comps = {
        "SMI": percentile_to_z(idx["smi"]),
        "R-Pctl": percentile_to_z(idx["r_pctl"]),
        "Q-Pctl": percentile_to_z(idx["q_pctl"]),
        "MDI": percentile_to_z(idx["mdi"]),
    }
    ref_std = ref.std()
    if pd.isna(ref_std) or ref_std == 0:
        return

    fig = plt.figure(figsize=FIG_SIZE_MEDIUM)
    ax = plt.subplot(111, projection="polar")
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_title("E) Taylor Diagram (Reference: SPI-3)", fontweight="bold")

    for name, s in comps.items():
        v = ~(ref.isna() | s.isna())
        if v.sum() < 30:
            continue
        r, _ = pearsonr(ref[v], s[v])
        r = float(np.clip(r, -1, 1))
        theta = np.arccos(r)
        radius = s[v].std()
        ax.plot(theta, radius, "o", ms=8, label=f"{name} (r={r:.2f})")

    ax.plot(0, ref_std, marker="*", ms=12, color="black", label="SPI-3 ref")
    ax.set_rlim(0, max(ref_std * 1.8, 2.0))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", bbox_to_anchor=(1.28, 1.1), fontsize=9)
    fig.tight_layout()
    save_plot(fig, out)


def plot_f_onset(idx: pd.DataFrame, out: Path):
    d = pd.to_datetime(idx["date"])
    smi_onsets = onset_dates(idx["smi"], d, threshold=20.0)
    if len(smi_onsets) == 0:
        return

    series_map = {"R-Pctl": idx["r_pctl"], "Q-Pctl": idx["q_pctl"], "MDI": idx["mdi"]}
    lags: Dict[str, List[float]] = {k: [] for k in series_map}

    for name, s in series_map.items():
        ons = onset_dates(s, d, threshold=20.0)
        for t in ons:
            prev = smi_onsets[smi_onsets <= t]
            if len(prev) > 0:
                lags[name].append((t - prev.max()).days)

    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_MEDIUM)
    names = list(lags.keys())
    vals = [lags[n] if len(lags[n]) > 0 else [np.nan] for n in names]

    axes[0].boxplot(vals, tick_labels=names, patch_artist=True,
                    boxprops=dict(facecolor="#90BE6D", alpha=0.8))
    axes[0].set_title("Lag to SMI onset", fontweight="bold")
    axes[0].set_ylabel("Lag [days]")
    axes[0].grid(alpha=0.3, axis="y")

    medians = [np.nanmedian(v) if len(v) > 0 else np.nan for v in vals]
    axes[1].bar(names, medians, color=["#577590", "#F3722C", "#F94144"])
    axes[1].set_title("Median onset lag", fontweight="bold")
    axes[1].set_ylabel("Lag [days]")
    axes[1].grid(alpha=0.3, axis="y")

    fig.suptitle("F) Drought Onset Analysis", fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save_plot(fig, out)


def run_catchment(catchment: str, catchments: Dict[str, Dict], plot_dir: Path):
    print(f"Processing advanced analysis: {catchment}")
    idx, dat = load_inputs(catchment)
    ensure_dir(plot_dir)

    plot_a_propagation(idx, dat, plot_dir / "A_drought_propagation.png")
    plot_b_survival(idx, plot_dir / "B_event_duration_survival.png")
    plot_c_interannual(idx, plot_dir / "C_interannual_variability.png")
    plot_d_spatial(catchments, plot_dir / "D_spatial_comparison.png")
    plot_e_taylor(idx, plot_dir / "E_index_comparison_taylor.png")
    plot_f_onset(idx, plot_dir / "F_drought_onset_analysis.png")
    print(f"✅ Advanced analysis complete: {plot_dir}")


def main():
    parser = argparse.ArgumentParser(description="04_advanced_analysis.py — Advanced drought analysis plots")
    parser.add_argument("--catchment", type=str, default="Chemnitz2_0p0625",
                        help="Catchment name or 'all'")
    parser.add_argument("--plot-dir", type=Path, default=None,
                        help="Output plot directory (default: analysis/plots/<catchment>/advanced)")
    args = parser.parse_args()

    catchments = load_catchments()
    if args.catchment == "all":
        targets = list(catchments.keys())
    else:
        targets = [args.catchment]

    for c in targets:
        if c not in catchments:
            print(f"❌ Unknown catchment: {c}")
            continue
        out = args.plot_dir / c if args.plot_dir else REPO / "analysis" / "plots" / c / "advanced"
        run_catchment(c, catchments, out)


if __name__ == "__main__":
    main()
