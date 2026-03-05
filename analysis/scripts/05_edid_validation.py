#!/usr/bin/env python3
"""05_edid_validation.py — Compare MDI drought signal with EDID/EDII impacts.

Workflow:
1. Download EDII V2.0 archive (if missing)
2. Parse impact records
3. Aggregate Germany yearly impact counts
4. Compare against yearly MDI drought days from selected catchments
5. Save CSV + plot
"""

from __future__ import annotations

import argparse
import importlib.util
import io
from pathlib import Path
import zipfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy.stats import pearsonr

REPO = Path(__file__).resolve().parents[2]
EDII_URL = "https://freidok.uni-freiburg.de/dnb/download/230922"
EDII_ZIP = REPO / "analysis" / "data_external" / "edii" / "EDII_V2_0.zip"
EDII_TXT = REPO / "analysis" / "data_external" / "edii" / "EDII_V2.0" / "EDII_DataV2.0.txt"


def load_catchments() -> dict:
    script_path = REPO / "analysis" / "scripts" / "01_load_data.py"
    spec = importlib.util.spec_from_file_location("load_data", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CATCHMENTS


def ensure_edii_data(force_download: bool = False):
    EDII_ZIP.parent.mkdir(parents=True, exist_ok=True)
    if force_download or not EDII_ZIP.exists():
        print(f"  → Downloading EDII archive from {EDII_URL}")
        r = requests.get(EDII_URL, timeout=120)
        r.raise_for_status()
        EDII_ZIP.write_bytes(r.content)
        print(f"  ✓ Saved: {EDII_ZIP}")
    if force_download or not EDII_TXT.exists():
        print("  → Extracting EDII archive")
        with zipfile.ZipFile(EDII_ZIP, "r") as zf:
            zf.extractall(EDII_ZIP.parent)
        print(f"  ✓ Extracted: {EDII_TXT}")


def load_edii(country: str, year_from: int, year_to: int) -> pd.DataFrame:
    df = pd.read_csv(EDII_TXT, sep="\t", encoding="latin-1", low_memory=False)
    df["Year_start"] = pd.to_numeric(df["Year_start"], errors="coerce")
    c = df[df["Country"] == country].copy()
    c = c[(c["Year_start"] >= year_from) & (c["Year_start"] <= year_to)].copy()
    c["year"] = c["Year_start"].astype(int)
    yearly = c.groupby("year").agg(
        edid_impacts=("ID", "count"),
        edid_unique_events=("Related_drought_event", lambda x: x.fillna("NA").nunique()),
    ).reset_index()
    return yearly


def load_mdi_yearly(catchments: list[str], year_from: int, year_to: int) -> pd.DataFrame:
    rows = []
    for c in catchments:
        p = REPO / "analysis" / "results" / c / "drought_indices.parquet"
        if not p.exists():
            print(f"  ⚠ Missing indices for {c}, skipping")
            continue
        df = pd.read_parquet(p)[["date", "mdi"]].copy()
        df["date"] = pd.to_datetime(df["date"])
        df["year"] = df["date"].dt.year
        y = df[(df["year"] >= year_from) & (df["year"] <= year_to)].groupby("year").agg(
            mdi_mean=("mdi", "mean"),
            mdi_drought_days=("mdi", lambda s: int((pd.to_numeric(s, errors="coerce") < 20).sum())),
        ).reset_index()
        y["catchment"] = c
        rows.append(y)
    if not rows:
        return pd.DataFrame(columns=["year", "mdi_mean_mean", "mdi_drought_days_total", "mdi_drought_days_mean"])

    all_y = pd.concat(rows, ignore_index=True)
    out = all_y.groupby("year").agg(
        mdi_mean_mean=("mdi_mean", "mean"),
        mdi_drought_days_total=("mdi_drought_days", "sum"),
        mdi_drought_days_mean=("mdi_drought_days", "mean"),
    ).reset_index()
    return out


def create_plot(df: pd.DataFrame, out_path: Path, title_suffix: str):
    fig, axes = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    ax = axes[0]
    ax.plot(df["year"], df["edid_impacts"], marker="o", linewidth=2, label="EDID impacts (DE)")
    ax.set_ylabel("Impact reports per year")
    ax.grid(alpha=0.3)
    ax.legend()
    ax.set_title(f"EDID vs MDI (Germany, yearly) {title_suffix}", fontweight="bold")

    ax2 = axes[1]
    ax2.plot(df["year"], df["mdi_drought_days_mean"], marker="o", linewidth=2, color="#C73E1D",
             label="Mean MDI drought days (5 catchments)")
    ax2.set_ylabel("MDI drought days/year")
    ax2.set_xlabel("Year")
    ax2.grid(alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  ✓ Saved plot: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="EDID/EDII validation against MDI")
    parser.add_argument("--country", default="DE", help="Country code in EDII dataset")
    parser.add_argument("--year-from", type=int, default=2005)
    parser.add_argument("--year-to", type=int, default=2020)
    parser.add_argument("--catchments", type=str,
                        default="Chemnitz2_0p0625,Wesenitz2_0p0625,Parthe_0p0625,Wyhra_0p0625,saxony_0p0625")
    parser.add_argument("--force-download", action="store_true")
    args = parser.parse_args()

    print("EDID/EDII validation")
    ensure_edii_data(force_download=args.force_download)

    catchments_available = load_catchments()
    catchments = [c.strip() for c in args.catchments.split(",") if c.strip()]
    catchments = [c for c in catchments if c in catchments_available]
    print(f"  → Catchments: {catchments}")

    edid = load_edii(args.country, args.year_from, args.year_to)
    mdi = load_mdi_yearly(catchments, args.year_from, args.year_to)
    comp = pd.merge(edid, mdi, on="year", how="outer").sort_values("year")
    comp["edid_impacts"] = comp["edid_impacts"].fillna(0)

    valid = comp[["edid_impacts", "mdi_drought_days_mean"]].dropna()
    if len(valid) >= 3:
        r, p = pearsonr(valid["edid_impacts"], valid["mdi_drought_days_mean"])
    else:
        r, p = np.nan, np.nan

    out_dir = REPO / "analysis" / "results" / "edid_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"edid_vs_mdi_{args.country}_{args.year_from}_{args.year_to}.csv"
    comp.to_csv(out_csv, index=False)
    print(f"  ✓ Saved table: {out_csv}")

    out_md = out_dir / f"edid_vs_mdi_{args.country}_{args.year_from}_{args.year_to}.md"
    with open(out_md, "w") as f:
        f.write(f"# EDID vs MDI validation ({args.country}, {args.year_from}-{args.year_to})\n\n")
        f.write(f"- Pearson r (EDID impacts vs mean MDI drought days): {r:.3f}\n")
        f.write(f"- p-value: {p:.3g}\n")
        f.write(f"- Catchments: {', '.join(catchments)}\n\n")
        f.write("## Notes\n")
        f.write("- EDII source: DOI 10.6094/UNIFR/230922\n")
        f.write("- EDID impacts are societal reports, MDI is hydroclimatic signal; relation is indicative, not causal.\n")
    print(f"  ✓ Saved summary: {out_md}")

    plot_path = REPO / "analysis" / "plots" / "edid" / f"edid_vs_mdi_{args.country}_{args.year_from}_{args.year_to}.png"
    create_plot(comp, plot_path, f"({args.country}, {args.year_from}-{args.year_to})")

    print(f"  → Correlation r={r:.3f}, p={p:.3g}")


if __name__ == "__main__":
    main()
