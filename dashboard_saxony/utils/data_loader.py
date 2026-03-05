from __future__ import annotations

from pathlib import Path
from typing import Dict

import geopandas as gpd
import netCDF4 as nc
import numpy as np
import pandas as pd
from shapely.geometry import box
from utils.geo_utils import clip_points_to_saxony, get_saxony_boundary_gdf


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _find_fluxes_nc() -> Path:
    repo = _repo_root()
    candidates = [
        repo / "code" / "mhm" / "catchments_cloud" / "saxony_0p0625" / "output_0090410340" / "mHM_Fluxes_States.nc",
        repo / "code" / "mhm" / "output" / "saxony_0p0625" / "mhm_sim" / "forward_run" / "mHM_Fluxes_States.nc",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("No mHM_Fluxes_States.nc found for saxony_0p0625")


def _to_datetime(time_var) -> pd.DatetimeIndex:
    t = nc.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def _build_grid(lon: np.ndarray, lat: np.ndarray, valid_mask: np.ndarray) -> gpd.GeoDataFrame:
    dlon = float(np.median(np.diff(lon)))
    dlat = float(np.median(np.diff(lat)))

    rows = []
    for i, y in enumerate(lat):
        for j, x in enumerate(lon):
            if not valid_mask[i, j]:
                continue
            geom = box(x - dlon / 2, y - dlat / 2, x + dlon / 2, y + dlat / 2)
            rows.append({"i": i, "j": j, "lon": float(x), "lat": float(y), "geometry": geom})

    grid = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    return grid


def _compute_indices_from_sm(sm_3d: np.ndarray, dates: pd.DatetimeIndex, valid_mask: np.ndarray) -> Dict[str, np.ndarray]:
    # Flatten valid cells: [time, n_cells]
    vals = sm_3d[:, valid_mask].astype(float)

    # Robust nFK scaling per cell (5-95 percentile)
    q05 = np.nanpercentile(vals, 5, axis=0)
    q95 = np.nanpercentile(vals, 95, axis=0)
    denom = q95 - q05
    denom[denom == 0] = np.nan

    nfk = ((vals - q05) / denom) * 100.0
    nfk = np.clip(nfk, 0, 100)

    sm_vol = 5.0 + np.clip((vals - q05) / denom, 0, 1) * 40.0

    # SMI as DOY percentile per cell (empirical rank, 0..100)
    smi = np.full_like(vals, np.nan, dtype=float)
    doy = dates.dayofyear.values
    for k in np.unique(doy):
        idx = np.where(doy == k)[0]
        sub = vals[idx, :]
        ranks = pd.DataFrame(sub).rank(axis=0, method="average", pct=True).to_numpy() * 100.0
        smi[idx, :] = ranks

    return {"nfk": nfk, "sm_vol": sm_vol, "smi": smi}


def _load_raster_data() -> Dict:
    p = _find_fluxes_nc()
    ds = nc.Dataset(p)
    try:
        lon = np.asarray(ds.variables["lon"][:], dtype=float)
        lat = np.asarray(ds.variables["lat"][:], dtype=float)
        dates = _to_datetime(ds.variables["time"])

        sm_lall = np.ma.filled(ds.variables["SM_Lall"][:], np.nan).astype(float)
        valid_mask = np.isfinite(sm_lall[0])

        grid = _build_grid(lon, lat, valid_mask)
        idx = _compute_indices_from_sm(sm_lall, dates, valid_mask)

        # Hard clip to Saxony polygon (data-level clip, not visual only).
        inside_mask = clip_points_to_saxony(grid, lat_col="lat", lon_col="lon").to_numpy()
        grid = grid.loc[inside_mask].reset_index(drop=True)
        nfk = idx["nfk"][:, inside_mask]
        sm_vol = idx["sm_vol"][:, inside_mask]
        smi = idx["smi"][:, inside_mask]

        boundary = get_saxony_boundary_gdf()

        return {
            "dates": dates,
            "grid": grid,
            "boundary": boundary,
            "valid_mask": valid_mask,
            "nfk": nfk,
            "sm_vol": sm_vol,
            "smi": smi,
        }
    finally:
        ds.close()


def _load_multi_index_timeseries() -> pd.DataFrame:
    repo = _repo_root()
    p = repo / "analysis" / "results" / "Chemnitz2_0p0625" / "drought_indices.parquet"
    if not p.exists():
        raise FileNotFoundError(f"Missing {p}")
    d = pd.read_parquet(p)
    d["date"] = pd.to_datetime(d["date"])
    d["region"] = "Sachsen (gesamt)"
    return d


def load_saxony_data() -> Dict:
    raster = _load_raster_data()
    smi_ts = _load_multi_index_timeseries()

    # Raster-MDI proxy (cell-wise): 0.4*SMI + 0.3*lag30 + 0.3*lag60.
    # This keeps map interactivity consistent until full cell-wise R/Q fields are integrated.
    smi = raster["smi"]
    lag30 = np.roll(smi, 30, axis=0)
    lag60 = np.roll(smi, 60, axis=0)
    lag30[:30, :] = np.nan
    lag60[:60, :] = np.nan
    mdi = 0.4 * smi + 0.3 * lag30 + 0.3 * lag60
    mdi = np.clip(mdi, 0, 100)

    # Raster mean time series for tabs 1-3
    ts = pd.DataFrame({
        "date": raster["dates"],
        "nfk_pct": np.nanmean(raster["nfk"], axis=1),
        "sm_vol_pct": np.nanmean(raster["sm_vol"], axis=1),
        "smi": np.nanmean(raster["smi"], axis=1),
        "mdi": np.nanmean(mdi, axis=1),
        "region": "Sachsen (gesamt)",
    })
    raster["mdi"] = mdi

    return {
        "raster": raster,
        "timeseries": ts,
        "smi": smi_ts,
        "landkreise": raster["boundary"],
    }
