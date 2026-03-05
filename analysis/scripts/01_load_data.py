#!/usr/bin/env python3
"""01_load_data.py — Data Loader for PhD Paper #1.

Loads mHM output and CAMELS-DE discharge data.
Interpolates monthly → daily.
Calculates volumetric soil moisture.
Saves as Parquet + CSV + Metadata JSON.

Usage:
    python 01_load_data.py --catchment Chemnitz2_0p0625
    python 01_load_data.py --catchment all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO = Path(__file__).resolve().parents[2]
CATCHMENTS = {
    "Chemnitz2_0p0625": {"gauge_id": "0090410700", "kge": 0.745, "priority": "high"},
    "GrosseRoeder3_0p0625": {"gauge_id": "0090411050", "kge": 0.654, "priority": "high"},
    "Parthe_0p0625": {"gauge_id": "0090411280", "kge": 0.220, "priority": "low"},
    "Wesenitz2_0p0625": {"gauge_id": "0090410480", "kge": 0.729, "priority": "high"},
    "Wyhra_0p0625": {"gauge_id": "0090412470", "kge": 0.239, "priority": "low"},
    "saxony_0p0625": {"gauge_id": "0090410340", "kge": 0.114, "priority": "low"},
}

# Soil layer depths (mm) - adjust based on mhm.nml
SOIL_L01_DEPTH_MM = 250.0  # Top layer
SOIL_L02_DEPTH_MM = 350.0  # Second layer
SOIL_LALL_DEPTH_MM = 600.0  # Total


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _to_datetime(time_var) -> pd.DatetimeIndex:
    """Convert netCDF time variable to pandas DatetimeIndex."""
    t = nc.num2date(time_var[:], units=time_var.units, calendar=getattr(time_var, "calendar", "standard"))
    return pd.to_datetime([x.isoformat() for x in t])


def _spatial_mean(ds: nc.Dataset, var_name: str) -> np.ndarray:
    """Calculate spatial mean over all grid cells."""
    arr = np.ma.filled(ds.variables[var_name][:], np.nan).astype(float)
    return np.nanmean(arr, axis=(1, 2))


def _spatial_mean_any(ds: nc.Dataset, candidates: list[str], n_time: int) -> np.ndarray:
    """Try multiple variable names, return first found."""
    for c in candidates:
        if c in ds.variables:
            return _spatial_mean(ds, c)
    return np.full(n_time, np.nan)


def _interpolate_monthly_to_daily(monthly_dates: np.ndarray, monthly_values: np.ndarray, 
                                   daily_dates: np.ndarray) -> np.ndarray:
    """Interpolate monthly values to daily resolution using cubic spline."""
    # Convert to pandas DatetimeIndex, then to ordinal (days since 0001-01-01)
    monthly_idx = pd.to_datetime(monthly_dates)
    daily_idx = pd.to_datetime(daily_dates)
    
    # Convert to ordinal using pandas' internal representation
    monthly_ord = monthly_idx.map(pd.Timestamp.toordinal).astype(float)
    daily_ord = daily_idx.map(pd.Timestamp.toordinal).astype(float)
    
    # Remove NaN for interpolation
    valid = ~np.isnan(monthly_values)
    if valid.sum() < 3:
        return np.full(len(daily_dates), np.nan)
    
    # Cubic interpolation
    f = interp1d(monthly_ord[valid], monthly_values[valid], kind='cubic', 
                 bounds_error=False, fill_value=np.nan)
    return f(daily_ord)


def _load_mhm_fluxes(mhm_nc_path: Path) -> Dict[str, Any]:
    """Load mHM Fluxes_States.nc and extract key variables."""
    ds = nc.Dataset(mhm_nc_path)
    try:
        time = _to_datetime(ds.variables["time"])
        n_time = len(time)
        
        # Soil moisture:
        # Prefer direct volumetric mHM outputs (SM_*). Fall back to SWC_* / depth.
        sm_l01 = _spatial_mean_any(ds, ["SM_L01", "SM_L1"], n_time)
        if np.isnan(sm_l01).all():
            swc_l01 = _spatial_mean_any(ds, ["SWC_L01", "SWC_L1"], n_time)
            sm_l01 = swc_l01 / SOIL_L01_DEPTH_MM

        sm_l02 = _spatial_mean_any(ds, ["SM_L02", "SM_L2"], n_time)
        if np.isnan(sm_l02).all():
            swc_l02 = _spatial_mean_any(ds, ["SWC_L02", "SWC_L2"], n_time)
            sm_l02 = swc_l02 / SOIL_L02_DEPTH_MM

        sm_lall = _spatial_mean_any(ds, ["SM_Lall", "SM_LALL", "SM_LAll"], n_time)
        if np.isnan(sm_lall).all():
            swc_lall = _spatial_mean_any(ds, ["SWC_Lall", "SWC_LALL"], n_time)
            sm_lall = swc_lall / SOIL_LALL_DEPTH_MM
        
        # Recharge (mm/day or mm/month)
        recharge = _spatial_mean_any(ds, ["recharge", "L1_percol", "perc"], n_time)
        
        # Runoff (mm/day or mm/month)
        runoff = _spatial_mean_any(ds, ["Q", "L1_total_runoff", "runoff"], n_time)
        
        # Precipitation (mm/day or mm/month)
        precip = _spatial_mean_any(ds, ["pre", "preEffect", "precip"], n_time)
        
        # PET (mm/day or mm/month)
        pet = _spatial_mean_any(ds, ["pet", "PET", "potet"], n_time)
        
        return {
            "time": time,
            "sm_l01": sm_l01,
            "sm_l02": sm_l02,
            "sm_lall": sm_lall,
            "recharge": recharge,
            "runoff": runoff,
            "precip": precip,
            "pet": pet,
        }
    finally:
        ds.close()


def _load_discharge(discharge_nc_path: Path) -> Dict[str, Any]:
    """Load mHM discharge.nc and extract Qsim.
    
    Keeps daily resolution - do NOT aggregate to monthly!
    """
    ds = nc.Dataset(discharge_nc_path)
    try:
        time = _to_datetime(ds.variables["time"])
        
        # Find Qsim variable (may have different names)
        qsim_var = next((v for v in ds.variables if v.startswith("Qsim_")), None)
        if qsim_var is None:
            qsim_var = "Qsim"
        
        qsim = np.asarray(ds.variables[qsim_var][:], dtype=float)

        # Optional Qobs variable from discharge.nc
        qobs_var = next((v for v in ds.variables if v.startswith("Qobs_")), None)
        if qobs_var is None and "Qobs" in ds.variables:
            qobs_var = "Qobs"
        qobs = np.asarray(ds.variables[qobs_var][:], dtype=float) if qobs_var else np.full(len(time), np.nan)
        
        # Always keep original resolution (daily or monthly)
        return {
            "time": time,
            "qsim": qsim,
            "qobs": qobs,
        }
    finally:
        ds.close()


def _load_camels_de(gauge_id: str, camels_dir: Path) -> pd.DataFrame | None:
    """Load CAMELS-DE observed discharge for a gauge."""
    camels_file = camels_dir / f"{gauge_id}.csv"
    if not camels_file.exists():
        return None
    
    df = pd.read_csv(camels_file, parse_dates=["date"])
    if "discharge" not in df.columns and "Qobs" in df.columns:
        df["discharge"] = df["Qobs"]
    
    return df[["date", "discharge"]].sort_values("date")


def _load_daily_discharge_out(path: Path) -> pd.DataFrame | None:
    """Load mHM daily_discharge.out with columns like: No Day Mon Year Qobs_* Qsim_*."""
    if not path.exists():
        return None

    try:
        df = pd.read_csv(path, sep=r"\s+")
        required = {"Day", "Mon", "Year"}
        if not required.issubset(df.columns):
            return None

        qobs_col = next((c for c in df.columns if c.startswith("Qobs")), None)
        qsim_col = next((c for c in df.columns if c.startswith("Qsim")), None)
        if qobs_col is None and qsim_col is None:
            return None

        out = pd.DataFrame({
            "date": pd.to_datetime(dict(year=df["Year"], month=df["Mon"], day=df["Day"]), errors="coerce"),
            "qobs_out": pd.to_numeric(df[qobs_col], errors="coerce") if qobs_col else np.nan,
            "qsim_out": pd.to_numeric(df[qsim_col], errors="coerce") if qsim_col else np.nan,
        }).dropna(subset=["date"])
        return out.sort_values("date").reset_index(drop=True)
    except Exception:
        return None


def _resolve_camels_dir(camels_dir: Path | None) -> Path | None:
    """Resolve CAMELS-DE directory from explicit arg or common project locations."""
    if camels_dir and camels_dir.exists():
        return camels_dir

    candidates = [
        REPO / "data" / "camels_de",
        REPO / "data" / "camels-de",
        REPO / "data" / "CAMELS_DE",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# =============================================================================
# MAIN LOADER
# =============================================================================

def load_catchment(catchment_name: str, camels_dir: Path | None = None) -> pd.DataFrame:
    """Load all data for a single catchment."""
    if catchment_name not in CATCHMENTS:
        raise ValueError(f"Unknown catchment: {catchment_name}. Available: {list(CATCHMENTS.keys())}")
    
    catchment_info = CATCHMENTS[catchment_name]
    gauge_id = catchment_info["gauge_id"]
    
    # Paths - try multiple locations
    mhm_base = REPO / "code" / "mhm"
    
    # Priority 1: catchments_cloud/<name>/output_<gauge>/
    mhm_fluxes = mhm_base / "catchments_cloud" / catchment_name / f"output_{gauge_id}" / "mHM_Fluxes_States.nc"
    mhm_discharge = mhm_base / "catchments_cloud" / catchment_name / f"output_{gauge_id}" / "discharge.nc"
    mhm_daily_discharge = mhm_base / "catchments_cloud" / catchment_name / f"output_{gauge_id}" / "daily_discharge.out"
    
    # Priority 2: output/<name>/mhm_sim/forward_run/
    if not mhm_fluxes.exists():
        mhm_fluxes = mhm_base / "output" / catchment_name / "mhm_sim" / "forward_run" / "mHM_Fluxes_States.nc"
        mhm_discharge = mhm_base / "output" / catchment_name / "mhm_sim" / "forward_run" / "discharge.nc"
        mhm_daily_discharge = mhm_base / "output" / catchment_name / "mhm_sim" / "forward_run" / "daily_discharge.out"
    
    # Priority 3: <name>/output/
    if not mhm_fluxes.exists():
        mhm_dir = mhm_base / catchment_name
        mhm_fluxes = mhm_dir / "output" / "mHM_Fluxes_States.nc"
        mhm_discharge = mhm_dir / "output" / "discharge.nc"
        mhm_daily_discharge = mhm_dir / "output" / "daily_discharge.out"
    
    # Fallback: direct in catchment folder
    if not mhm_fluxes.exists():
        mhm_fluxes = mhm_base / catchment_name / "mHM_Fluxes_States.nc"
        mhm_discharge = mhm_base / catchment_name / "discharge.nc"
        mhm_daily_discharge = mhm_base / catchment_name / "daily_discharge.out"
    
    print(f"Loading catchment: {catchment_name} (Gauge: {gauge_id})")
    
    # Load mHM data
    if not mhm_fluxes.exists():
        raise FileNotFoundError(f"mHM Fluxes not found: {mhm_fluxes}")
    
    mhm_data = _load_mhm_fluxes(mhm_fluxes)
    print(f"  ✓ Loaded mHM Fluxes: {len(mhm_data['time'])} time steps")
    
    # Load discharge (Qsim)
    if mhm_discharge.exists():
        q_data = _load_discharge(mhm_discharge)
        print(f"  ✓ Loaded mHM Discharge: {len(q_data['time'])} time steps")
    else:
        print(f"  ⚠ No discharge.nc found, Qsim will be NaN")
        q_data = {
            "time": mhm_data["time"],
            "qsim": np.full(len(mhm_data["time"]), np.nan),
            "qobs": np.full(len(mhm_data["time"]), np.nan),
        }

    # Load CAMELS-DE (Qobs), or fallback to daily_discharge.out
    qobs_df = None
    camels_dir_resolved = _resolve_camels_dir(camels_dir)
    if camels_dir_resolved and (camels_dir_resolved / f"{gauge_id}.csv").exists():
        qobs_df = _load_camels_de(gauge_id, camels_dir_resolved)
        print(f"  ✓ Loaded CAMELS-DE Qobs: {len(qobs_df)} time steps")
    elif mhm_daily_discharge.exists():
        daily_q = _load_daily_discharge_out(mhm_daily_discharge)
        if daily_q is not None:
            qobs_df = daily_q[["date", "qobs_out"]].rename(columns={"qobs_out": "discharge"})
            qsim_from_out = daily_q[["date", "qsim_out"]]
            print(f"  ✓ Loaded daily_discharge.out fallback: {len(daily_q)} time steps")
        else:
            qsim_from_out = None
    else:
        qsim_from_out = None
    
    # Determine temporal resolution
    mhm_time = pd.to_datetime(mhm_data["time"])
    mhm_diff = pd.Series(mhm_time).diff().dt.days.median()
    q_time = pd.to_datetime(q_data["time"])
    q_diff = pd.Series(q_time).diff().dt.days.median()
    
    if q_diff <= 2 and mhm_diff <= 2:  # both daily -> use direct values, no interpolation
        if len(mhm_time) == len(q_time) and np.array_equal(mhm_time.values, q_time.values):
            print(f"  → Fluxes and discharge are daily ({len(q_time)} steps), using direct daily values")
            df = pd.DataFrame({
                "date": mhm_data["time"],
                "precip": mhm_data["precip"],
                "pet": mhm_data["pet"],
                "sm_l01": mhm_data["sm_l01"],
                "sm_l02": mhm_data["sm_l02"],
                "sm_lall": mhm_data["sm_lall"],
                "recharge": mhm_data["recharge"],
                "runoff": mhm_data["runoff"],
                "qsim": q_data["qsim"],
            })
        else:
            print(f"  → Fluxes/discharge are daily but dates differ, aligning by date")
            df_flux = pd.DataFrame({
                "date": mhm_data["time"],
                "precip": mhm_data["precip"],
                "pet": mhm_data["pet"],
                "sm_l01": mhm_data["sm_l01"],
                "sm_l02": mhm_data["sm_l02"],
                "sm_lall": mhm_data["sm_lall"],
                "recharge": mhm_data["recharge"],
                "runoff": mhm_data["runoff"],
            })
            df_q = pd.DataFrame({"date": q_data["time"], "qsim": q_data["qsim"]})
            df = df_flux.merge(df_q, on="date", how="outer").sort_values("date").reset_index(drop=True)

    elif q_diff <= 2:  # discharge daily, fluxes monthly -> interpolate fluxes to daily
        print(f"  → Discharge is daily ({len(q_data['time'])} steps), interpolating Fluxes to match...")
        daily_data = {"date": q_time}
        fluxes_vars = ["precip", "pet", "sm_l01", "sm_l02", "sm_lall", "recharge", "runoff"]
        for var in fluxes_vars:
            daily_data[var] = _interpolate_monthly_to_daily(
                mhm_time.values,
                mhm_data[var],
                q_time.values
            )

        daily_data["qsim"] = q_data["qsim"]
        df = pd.DataFrame(daily_data)
        print(f"  ✓ Interpolated Fluxes to {len(df)} daily time steps")
        
    else:  # Both are monthly or coarser
        # Create DataFrame with monthly data
        df = pd.DataFrame({
            "date": mhm_data["time"],
            "precip": mhm_data["precip"],
            "pet": mhm_data["pet"],
            "sm_l01": mhm_data["sm_l01"],
            "sm_l02": mhm_data["sm_l02"],
            "sm_lall": mhm_data["sm_lall"],
            "recharge": mhm_data["recharge"],
            "runoff": mhm_data["runoff"],
            "qsim": q_data["qsim"],
        })

    # If available, merge qsim from daily_discharge.out as fallback for missing qsim.
    if "qsim_from_out" in locals() and qsim_from_out is not None:
        df = df.merge(qsim_from_out, on="date", how="left")
        if "qsim_out" in df.columns:
            df["qsim"] = df["qsim"].fillna(df["qsim_out"])
            df = df.drop(columns=["qsim_out"])

    # Add qobs from CAMELS-DE / daily_discharge.out / discharge.nc (in this priority)
    qobs_nc = pd.DataFrame({"date": q_data["time"], "qobs": q_data["qobs"]})
    df = df.merge(qobs_nc, on="date", how="left")
    if qobs_df is not None and len(qobs_df) > 0:
        qobs_clean = qobs_df.rename(columns={"discharge": "qobs_camels"})
        df = df.merge(qobs_clean[["date", "qobs_camels"]], on="date", how="left")
        df["qobs"] = df["qobs_camels"].combine_first(df["qobs"])
        df = df.drop(columns=["qobs_camels"])
    
    # Add metadata
    df.attrs["catchment"] = catchment_name
    df.attrs["gauge_id"] = gauge_id
    df.attrs["kge"] = catchment_info["kge"]
    df.attrs["priority"] = catchment_info["priority"]
    df.attrs["temporal_resolution"] = "daily"
    
    return df


def save_data(df: pd.DataFrame, output_dir: Path):
    """Save DataFrame as Parquet + CSV + Metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parquet (preserves metadata)
    parquet_path = output_dir / "drought_data.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"  ✓ Saved Parquet: {parquet_path}")
    
    # CSV (universal)
    csv_path = output_dir / "drought_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"  ✓ Saved CSV: {csv_path}")
    
    # Metadata JSON
    metadata = {
        "catchment": df.attrs.get("catchment", "unknown"),
        "gauge_id": df.attrs.get("gauge_id", "unknown"),
        "kge": df.attrs.get("kge", None),
        "priority": df.attrs.get("priority", "unknown"),
        "temporal_resolution": df.attrs.get("temporal_resolution", "daily"),
        "date_range": {
            "start": str(df["date"].min()),
            "end": str(df["date"].max()),
            "days": len(df),
        },
        "columns": list(df.columns),
        "soil_depths_mm": {
            "L01": SOIL_L01_DEPTH_MM,
            "L02": SOIL_L02_DEPTH_MM,
            "LALL": SOIL_LALL_DEPTH_MM,
        },
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Saved Metadata: {metadata_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="01_load_data.py — Load mHM + CAMELS-DE data")
    parser.add_argument("--catchment", type=str, default="Chemnitz2_0p0625",
                        help=f"Catchment name or 'all' for all. Available: {list(CATCHMENTS.keys())}")
    parser.add_argument("--camels-dir", type=Path, default=None,
                        help="Path to CAMELS-DE data directory")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: analysis/results/<catchment>)")
    args = parser.parse_args()
    
    # Determine catchments to process
    if args.catchment == "all":
        catchments_to_process = list(CATCHMENTS.keys())
    else:
        catchments_to_process = [args.catchment]
    
    # Process each catchment
    for catchment_name in catchments_to_process:
        print(f"\n{'='*60}")
        print(f"Processing: {catchment_name}")
        print(f"{'='*60}")
        
        try:
            # Load data
            df = load_catchment(catchment_name, camels_dir=args.camels_dir)
            
            # Determine output directory
            if args.output_dir:
                output_dir = args.output_dir / catchment_name
            else:
                output_dir = REPO / "analysis" / "results" / catchment_name
            
            # Save data
            save_data(df, output_dir)
            
            print(f"\n✅ Complete: {catchment_name}")
            
        except Exception as e:
            print(f"\n❌ Error processing {catchment_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("All catchments processed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
