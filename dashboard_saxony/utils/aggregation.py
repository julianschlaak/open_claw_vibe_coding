from __future__ import annotations

from typing import Dict, List

import pandas as pd


def nearest_date(df: pd.DataFrame, selected_date: pd.Timestamp) -> pd.Timestamp:
    d = pd.to_datetime(df["date"])
    return d.iloc[(d - pd.Timestamp(selected_date)).abs().argmin()]


def aggregate_by_landkreis(
    data: pd.DataFrame,
    selected_date: pd.Timestamp,
    value_col: str,
    region_col: str = "region",
) -> pd.DataFrame:
    """Aggregate selected value by region for nearest available date."""
    if data.empty:
        return pd.DataFrame(columns=["name", f"{value_col}_mean"])

    t = nearest_date(data, selected_date)
    sub = data.loc[pd.to_datetime(data["date"]) == t].copy()

    agg = (
        sub.groupby(region_col)[value_col]
        .agg(["mean", "median", "min", "max", "std", "count"])
        .reset_index()
        .rename(columns={region_col: "name"})
    )
    agg.columns = ["name"] + [f"{value_col}_{c}" for c in ["mean", "median", "min", "max", "std", "count"]]
    agg["date"] = t
    return agg


def aggregate_timeseries_by_region(
    data: pd.DataFrame,
    value_col: str,
    region: str | None,
    region_col: str = "region",
) -> pd.DataFrame:
    d = data.copy()
    d["date"] = pd.to_datetime(d["date"])

    if region and region != "Sachsen (gesamt)":
        d = d[d[region_col] == region]
        label = region
    else:
        label = "Sachsen (gesamt)"

    ts = d.groupby("date", as_index=False)[value_col].mean()
    ts["selection"] = label
    return ts


def aggregate_polygon(data: pd.DataFrame, polygon_coords: List[List[float]]) -> Dict[str, float]:
    """Placeholder polygon aggregation.

    Current dashboard uses region-level proxy data; polygon support is intentionally
    prepared but not yet bound to gridded point layers.
    """
    if data.empty:
        return {"mean": float("nan"), "median": float("nan"), "min": float("nan"), "max": float("nan"), "count": 0}

    cols = [c for c in ["smi", "mdi", "nfk_pct", "sm_vol_pct"] if c in data.columns]
    col = cols[0] if cols else data.columns[-1]
    s = pd.to_numeric(data[col], errors="coerce")
    return {
        "mean": float(s.mean()),
        "median": float(s.median()),
        "min": float(s.min()),
        "max": float(s.max()),
        "count": int(s.count()),
    }
