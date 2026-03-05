from __future__ import annotations

from pathlib import Path
from typing import Dict

import geopandas as gpd
import netCDF4 as nc
import numpy as np
import pandas as pd
from shapely.geometry import box
from utils.geo_utils import clip_grid_to_saxony, get_saxony_boundary_gdf


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


def _find_dem_asc() -> Path | None:
    repo = _repo_root()
    p = repo / "code" / "mhm" / "set_up" / "saxony_0p0625" / "mhm_setup" / "morph" / "dem.asc"
    return p if p.exists() else None


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


def _build_regular_saxony_grid(boundary: gpd.GeoDataFrame, resolution: float = 0.0625, edge_buffer_factor: float = 0.55) -> gpd.GeoDataFrame:
    """Build a regular raster over Saxony and clip cells to boundary.

    The small buffer helps retain edge cells that would otherwise create visual gaps.
    """
    sax = boundary.geometry.union_all()
    minx, miny, maxx, maxy = sax.bounds

    cols = int(np.ceil((maxx - minx) / resolution))
    rows = int(np.ceil((maxy - miny) / resolution))

    cells = []
    edge_buffer = resolution * edge_buffer_factor
    sax_for_intersection = sax.buffer(edge_buffer)

    for i in range(cols):
        for j in range(rows):
            x0 = minx + i * resolution
            y0 = miny + j * resolution
            cell = box(x0, y0, x0 + resolution, y0 + resolution)
            if not cell.intersects(sax_for_intersection):
                continue
            clipped = cell.intersection(sax)
            if clipped.is_empty or clipped.area <= 0:
                continue
            cells.append(
                {
                    "lon": x0 + resolution / 2.0,
                    "lat": y0 + resolution / 2.0,
                    "geometry": clipped,
                }
            )

    return gpd.GeoDataFrame(cells, crs="EPSG:4326").reset_index(drop=True)


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


def _load_hillshade_overlay() -> Dict | None:
    """Create subtle RGBA hillshade from DEM ASCII grid."""
    dem_path = _find_dem_asc()
    if dem_path is None:
        return None

    with dem_path.open("r", encoding="utf-8") as f:
        header = {}
        for _ in range(6):
            parts = f.readline().strip().split()
            if len(parts) >= 2:
                header[parts[0].lower()] = float(parts[-1])

    ncols = int(header.get("ncols", 0))
    nrows = int(header.get("nrows", 0))
    xll = float(header.get("xllcorner", 0.0))
    yll = float(header.get("yllcorner", 0.0))
    cell = float(header.get("cellsize", 0.0))
    nodata = float(header.get("nodata_value", -9999.0))
    if ncols <= 0 or nrows <= 0 or cell <= 0:
        return None

    dem = np.loadtxt(dem_path, skiprows=6, dtype=np.float32)
    if dem.shape != (nrows, ncols):
        return None
    dem[dem <= nodata + 1e-6] = np.nan

    # Hillshade (azimuth 315°, altitude 45°)
    dy, dx = np.gradient(dem, cell, cell)
    slope = np.pi / 2.0 - np.arctan(np.sqrt(dx * dx + dy * dy))
    aspect = np.arctan2(-dx, dy)
    az = np.deg2rad(315.0)
    alt = np.deg2rad(45.0)
    hs = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
    hs = np.clip(hs, 0, 1)

    # Normalize visible range, keep subtle transparency
    p2, p98 = np.nanpercentile(hs, [2, 98])
    hs = (hs - p2) / max(1e-6, (p98 - p2))
    hs = np.clip(hs, 0, 1)
    gray = (hs * 255).astype(np.uint8)

    rgba = np.zeros((nrows, ncols, 4), dtype=np.uint8)
    rgba[..., 0] = gray
    rgba[..., 1] = gray
    rgba[..., 2] = gray
    rgba[..., 3] = np.where(np.isfinite(dem), 70, 0).astype(np.uint8)

    minx = xll
    maxx = xll + ncols * cell
    miny = yll
    maxy = yll + nrows * cell
    bounds = [[miny, minx], [maxy, maxx]]
    return {"rgba": rgba, "bounds": bounds}


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

        # Exact polygon clipping for original model cells.
        grid = clip_grid_to_saxony(grid)
        source_indices = grid["__source_index"].to_numpy(dtype=int) if "__source_index" in grid.columns else np.array([], dtype=int)
        if "__source_index" in grid.columns:
            grid = grid.drop(columns=["__source_index"])

        boundary = get_saxony_boundary_gdf()

        # Build complete regular Saxony grid and map each cell to nearest source model cell.
        # This removes uncovered gaps while preserving the model pattern.
        full_grid = _build_regular_saxony_grid(boundary, resolution=0.0625, edge_buffer_factor=0.60)
        src_lon = grid["lon"].to_numpy(dtype=float)
        src_lat = grid["lat"].to_numpy(dtype=float)
        tgt_lon = full_grid["lon"].to_numpy(dtype=float)
        tgt_lat = full_grid["lat"].to_numpy(dtype=float)

        d2 = (tgt_lon[:, None] - src_lon[None, :]) ** 2 + (tgt_lat[:, None] - src_lat[None, :]) ** 2
        nearest_src_idx = np.argmin(d2, axis=1).astype(int)

        source_values_nfk = idx["nfk"][:, source_indices]
        source_values_sm_vol = idx["sm_vol"][:, source_indices]
        source_values_smi = idx["smi"][:, source_indices]

        nfk = source_values_nfk[:, nearest_src_idx]
        sm_vol = source_values_sm_vol[:, nearest_src_idx]
        smi = source_values_smi[:, nearest_src_idx]

        return {
            "dates": dates,
            "grid": full_grid,
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
    hillshade = _load_hillshade_overlay()
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
    raster["hillshade"] = hillshade

    return {
        "raster": raster,
        "timeseries": ts,
        "smi": smi_ts,
        "landkreise": raster["boundary"],
    }
