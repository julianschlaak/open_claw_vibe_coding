#!/usr/bin/env python3
"""Extended drought analysis plots and statistics for mHM outputs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import netCDF4 as nc
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Paths:
    repo: Path
    output: Path
    plots: Path
    results: Path


def resolve_paths() -> Paths:
    repo = Path(__file__).resolve().parents[2]
    output = repo / "code" / "mhm" / "test_domain" / "output_b1"
    return Paths(repo=repo, output=output, plots=repo / "analysis" / "plots", results=repo / "analysis" / "results")


def to_datetime(var) -> pd.DatetimeIndex:
    t = nc.num2date(var[:], units=var.units, calendar=getattr(var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def spatial_mean(ds: nc.Dataset, var_name: str) -> np.ndarray:
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(float)
    return np.nanmean(arr, axis=(1, 2))


def percentile_rank(series: pd.Series) -> pd.Series:
    return series.rank(method="average", pct=True) * 100.0


def drought_event_lengths(mask: np.ndarray) -> list[int]:
    lengths: list[int] = []
    current = 0
    for v in mask:
        if bool(v):
            current += 1
        elif current > 0:
            lengths.append(current)
            current = 0
    if current > 0:
        lengths.append(current)
    return lengths


def main() -> None:
    p = resolve_paths()
    p.plots.mkdir(parents=True, exist_ok=True)
    p.results.mkdir(parents=True, exist_ok=True)

    ds_mhm = nc.Dataset(p.output / "mHM_Fluxes_States.nc")
    try:
        t_month = to_datetime(ds_mhm.variables["time"])
        sm_l01 = spatial_mean(ds_mhm, "SM_L01")
        sm_l02 = spatial_mean(ds_mhm, "SM_L02")
        sm_all = spatial_mean(ds_mhm, "SM_Lall")
        recharge = spatial_mean(ds_mhm, "recharge")
        runoff = spatial_mean(ds_mhm, "Q")
    finally:
        ds_mhm.close()

    monthly = pd.DataFrame(
        {
            "date": t_month,
            "SM_L01": sm_l01,
            "SM_L02": sm_l02,
            "SM_Lall": sm_all,
            "recharge": recharge,
            "runoff": runoff,
        }
    )
    monthly["smi_percent"] = percentile_rank(monthly["SM_Lall"])
    monthly["month"] = monthly["date"].dt.month

    ds_q = nc.Dataset(p.output / "discharge.nc")
    try:
        q_name = next(n for n in ds_q.variables if n.startswith("Qsim_"))
        t_day = to_datetime(ds_q.variables["time"])
        qsim = np.ma.filled(ds_q.variables[q_name][:], np.nan).astype(float)
    finally:
        ds_q.close()

    daily = pd.DataFrame({"date": t_day, "qsim": qsim}).dropna()
    q5 = float(np.nanpercentile(daily["qsim"], 5))
    q95 = float(np.nanpercentile(daily["qsim"], 95))
    daily["below_q5"] = daily["qsim"] < q5
    daily["above_q95"] = daily["qsim"] > q95

    # Daily SMI proxy from monthly SMI percentile (forward fill to daily timeline).
    smi_daily = monthly[["date", "smi_percent"]].set_index("date").resample("D").ffill().reset_index()
    smi_daily = smi_daily.merge(daily[["date"]], on="date", how="right").sort_values("date")
    smi_daily["smi_percent"] = smi_daily["smi_percent"].ffill().bfill()
    smi_daily["drought"] = smi_daily["smi_percent"] < 20.0
    durations = drought_event_lengths(smi_daily["drought"].to_numpy())

    # Plot 1: seasonal drought analysis (boxplot by month)
    fig, ax = plt.subplots(figsize=(12, 6))
    data = [monthly.loc[monthly["month"] == m, "smi_percent"].to_numpy() for m in range(1, 13)]
    ax.boxplot(data, patch_artist=True, medianprops={"color": "black"})
    ax.set_xticks(range(1, 13), labels=[str(i) for i in range(1, 13)])
    ax.set_xlabel("Monat")
    ax.set_ylabel("SMI-Percentil")
    ax.set_title("Saisonale Dürre-Analyse: Monatsverteilung des SMI")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(p.plots / "01_saisonale_dürre.png", dpi=170)
    plt.close(fig)

    # Plot 2: extreme events with Q5/Q95 thresholds
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(daily["date"], daily["qsim"], color="0.2", linewidth=1.0, label="Qsim")
    ax.axhline(q5, color="red", linestyle="--", label=f"Q5 = {q5:.2f}")
    ax.axhline(q95, color="blue", linestyle="--", label=f"Q95 = {q95:.2f}")
    ax.fill_between(daily["date"], daily["qsim"], q5, where=daily["below_q5"], color="red", alpha=0.25, interpolate=True)
    ax.fill_between(daily["date"], q95, daily["qsim"], where=daily["above_q95"], color="blue", alpha=0.2, interpolate=True)
    ax.set_title("Extrem-Ereignisse: Zeitreihe mit Q5/Q95")
    ax.set_ylabel("Abfluss Qsim [m3 s-1]")
    ax.grid(alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(p.plots / "02_extremereignisse.png", dpi=170)
    plt.close(fig)

    # Plot 3: correlation matrix scatter plots
    corr_df = monthly[["smi_percent", "recharge", "runoff"]].copy()
    corr = corr_df.corr(method="pearson")

    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    pairs = [
        ("smi_percent", "recharge", "SMI vs Recharge"),
        ("smi_percent", "runoff", "SMI vs Abfluss"),
        ("recharge", "runoff", "Recharge vs Abfluss"),
    ]
    for ax, (x, y, title) in zip(axes, pairs):
        ax.scatter(corr_df[x], corr_df[y], alpha=0.75, s=35)
        r = np.corrcoef(corr_df[x], corr_df[y])[0, 1]
        ax.set_title(f"{title}\nr = {r:.2f}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.grid(alpha=0.25)
    fig.savefig(p.plots / "03_korrelationsmatrix.png", dpi=170)
    plt.close(fig)

    # Plot 4: spatio-temporal heatmap (time x layers)
    hm_data = np.vstack([monthly["SM_L01"].to_numpy(), monthly["SM_L02"].to_numpy(), monthly["SM_Lall"].to_numpy()])
    fig, ax = plt.subplots(figsize=(14, 5))
    im = ax.imshow(hm_data, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_yticks([0, 1, 2], labels=["Layer 1 (SM_L01)", "Layer 2 (SM_L02)", "Layer 3 (SM_Lall)"])
    xt = np.arange(0, len(monthly), max(1, len(monthly) // 8))
    ax.set_xticks(xt, labels=[monthly["date"].dt.strftime("%Y-%m").iloc[i] for i in xt], rotation=30, ha="right")
    ax.set_title("Räumlich-zeitliche Heatmap: SMI-Dynamik über Bodenschichten")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Soil Moisture Index proxy")
    fig.tight_layout()
    fig.savefig(p.plots / "04_raeumliche_heatmap.png", dpi=170)
    plt.close(fig)

    # Plot 5: drought duration distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    if durations:
        bins = np.arange(1, max(durations) + 2)
        ax.hist(durations, bins=bins, edgecolor="black", alpha=0.8)
    ax.set_xlabel("Dauer (Tage)")
    ax.set_ylabel("Häufigkeit")
    ax.set_title("Dürre-Dauer-Verteilung (SMI < 20)")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(p.plots / "05_dürredauer_histogramm.png", dpi=170)
    plt.close(fig)

    stats = {
        "q5": q5,
        "q95": q95,
        "extreme_days": {
            "below_q5": int(daily["below_q5"].sum()),
            "above_q95": int(daily["above_q95"].sum()),
            "total_days": int(len(daily)),
        },
        "drought_events": {
            "count": int(len(durations)),
            "durations_days": durations,
            "mean_duration_days": float(np.mean(durations)) if durations else 0.0,
            "median_duration_days": float(np.median(durations)) if durations else 0.0,
            "max_duration_days": int(max(durations)) if durations else 0,
        },
        "correlations_pearson": corr.to_dict(),
        "notes": {
            "daily_smi_method": "Monthly SMI percentiles were forward-filled to daily resolution for duration analysis.",
            "layers_used_for_heatmap": ["SM_L01", "SM_L02", "SM_Lall"],
        },
    }

    (p.results / "drought_statistics.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    log_lines = [
        "# EXTENDED_ANALYSIS_LOG",
        "",
        "## Schritte",
        "1. mHM monatliche Variablen geladen (SM_L01, SM_L02, SM_Lall, recharge, Q).",
        "2. Discharge-Tagesdaten geladen und Q5/Q95 berechnet.",
        "3. Fünf fachliche Plots erzeugt.",
        "4. Dürre-Events über SMI<20 (daily proxy) identifiziert.",
        "5. Statistiken nach JSON geschrieben.",
        "",
        "## Wichtige Kennzahlen",
        f"- Q5: {q5:.3f}",
        f"- Q95: {q95:.3f}",
        f"- Dürre-Events: {len(durations)}",
        f"- Mittlere Dürre-Dauer (Tage): {float(np.mean(durations)) if durations else 0.0:.2f}",
    ]
    (p.results / "EXTENDED_ANALYSIS_LOG.md").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
