#!/usr/bin/env python3
"""parse_daily_discharge.py — Parse mHM daily_discharge.out files.

Usage:
    python analysis/scripts/parse_daily_discharge.py --catchment Chemnitz2_0p0625
    python analysis/scripts/parse_daily_discharge.py --catchment all
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]


def load_catchments() -> dict:
    script_path = REPO / "analysis" / "scripts" / "01_load_data.py"
    spec = importlib.util.spec_from_file_location("load_data", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CATCHMENTS


def parse_daily_discharge(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+")
    qobs_col = next((c for c in df.columns if c.startswith("Qobs")), None)
    qsim_col = next((c for c in df.columns if c.startswith("Qsim")), None)
    if qobs_col is None and qsim_col is None:
        raise ValueError(f"No Qobs/Qsim columns found in {path}")

    out = pd.DataFrame({
        "date": pd.to_datetime(dict(year=df["Year"], month=df["Mon"], day=df["Day"]), errors="coerce"),
        "qobs": pd.to_numeric(df[qobs_col], errors="coerce") if qobs_col else pd.NA,
        "qsim": pd.to_numeric(df[qsim_col], errors="coerce") if qsim_col else pd.NA,
    }).dropna(subset=["date"])
    return out.sort_values("date").reset_index(drop=True)


def resolve_daily_discharge(catchment: str, gauge_id: str) -> Path:
    base = REPO / "code" / "mhm"
    candidates = [
        base / "catchments_cloud" / catchment / f"output_{gauge_id}" / "daily_discharge.out",
        base / "output" / catchment / "mhm_sim" / "forward_run" / "daily_discharge.out",
        base / catchment / "output" / "daily_discharge.out",
        base / catchment / "daily_discharge.out",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"daily_discharge.out not found for {catchment}")


def main():
    parser = argparse.ArgumentParser(description="Parse mHM daily_discharge.out")
    parser.add_argument("--catchment", type=str, default="all", help="Catchment name or 'all'")
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
        gid = catchments[c]["gauge_id"]
        print(f"\nProcessing {c} ({gid})")
        try:
            src = resolve_daily_discharge(c, gid)
            df = parse_daily_discharge(src)
            out_dir = REPO / "analysis" / "results" / c
            out_dir.mkdir(parents=True, exist_ok=True)
            pq = out_dir / "daily_discharge.parquet"
            csv = out_dir / "daily_discharge.csv"
            df.to_parquet(pq, index=False)
            df.to_csv(csv, index=False)
            print(f"  ✓ Source: {src}")
            print(f"  ✓ Saved: {pq}")
            print(f"  ✓ Saved: {csv}")
            print(f"  ✓ Rows: {len(df)}")
        except Exception as e:
            print(f"  ❌ {e}")


if __name__ == "__main__":
    main()
