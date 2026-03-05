#!/usr/bin/env python3
"""02_compute_indices.py — Calculate Drought Indices for PhD Paper #1.

QUALITY-FIRST IMPLEMENTATION:
- Calendar-based percentiles (DOY for daily, month for monthly) — NO seasonal bias
- Empirical ranking (not distributional assumptions) — robust for extremes
- Proper handling of NaN and missing data
- Drought classes per German Drought Monitor (<2%, <5%, <10%, <20%)

Calculates:
CORE (Paper #1):
  - SMI (Soil Moisture Index) — Percentile per DOY from SM_Lall
  - SMI_L01, SMI_L02 — Individual soil layers
  - R-Pctl (Recharge Percentile) — Percentile per DOY
  - Q-Pctl (Discharge Percentile) — Percentile per DOY
  - MDI (Matrix Drought Index) — Weighted: 0.4×SMI + 0.3×R-Pctl(lag-1) + 0.3×Q-Pctl(lag-2)

COMPARISON (Standardized):
  - SPI-1, SPI-3, SPI-6 — Standardized Precipitation Index
  - SPEI-1, SPEI-3, SPEI-6 — Standardized Precipitation Evapotranspiration Index
  - SDI-3, SDI-6 — Streamflow Drought Index

Usage:
    python 02_compute_indices.py --catchment Chemnitz2_0p0625
    python 02_compute_indices.py --catchment all
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd
from scipy.stats import norm, gamma, fisk

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO = Path(__file__).resolve().parents[2]

# Drought class thresholds (percentile-based, per German Drought Monitor)
DROUGHT_THRESHOLDS = {
    "extreme_drought": 2.0,    # < 2nd percentile
    "severe_drought": 5.0,     # < 5th percentile
    "moderate_drought": 10.0,  # < 10th percentile
    "mild_drought": 20.0,      # < 20th percentile
}

# MDI weights (optimized for hydrological drought)
MDI_WEIGHTS = {
    "smi": 0.4,      # Soil moisture (immediate)
    "recharge": 0.3, # Groundwater recharge (lag-1 month)
    "discharge": 0.3,# Streamflow (lag-2 months)
}


# =============================================================================
# QUALITY-CRITICAL: CALENDAR-BASED PERCENTILE
# =============================================================================

def calendar_percentile(dates: pd.Series, values: pd.Series) -> pd.Series:
    """Calculate percentile for each day based on calendar day-of-year.
    
    THIS IS THE KEY METHOD FOR SCIENTIFIC RIGOR:
    - Daily data: Compare each day only to the same day-of-year across all years
    - Monthly data: Compare each month only to the same month across all years
    - Removes seasonal bias (no comparing January to July!)
    - Empirical ranking (no distributional assumptions)
    
    Args:
        dates: Datetime series
        values: Numeric series of the same length
    
    Returns:
        Percentile series (0-100), where 100 = wettest, 0 = driest
    """
    d = pd.to_datetime(dates)
    v = pd.to_numeric(values, errors="coerce")
    
    # Determine temporal resolution
    dd = d.sort_values().diff().dt.days.dropna()
    if len(dd) > 0 and float(dd.median()) <= 2.0:
        # Daily data: use day-of-year (1-366)
        key = d.dt.dayofyear
    else:
        # Monthly or coarser: use month-of-year (1-12)
        key = d.dt.month
    
    out = pd.Series(np.nan, index=v.index, dtype=float)
    
    for k in key.dropna().unique():
        idx = key == k
        subset = v.loc[idx].dropna()
        
        if len(subset) < 3:
            # Not enough data for robust percentile
            out.loc[idx] = np.nan
            continue
        
        # Empirical percentile ranking (method='average' handles ties)
        ranks = subset.rank(method="average", pct=True)
        out.loc[idx] = ranks * 100.0
    
    return out


def classify_drought(percentile: pd.Series) -> pd.Series:
    """Classify drought severity based on percentile thresholds.
    
    Thresholds per German Drought Monitor (UFZ):
    - extreme_drought: < 2nd percentile
    - severe_drought: < 5th percentile
    - moderate_drought: < 10th percentile
    - mild_drought: < 20th percentile
    - normal_or_wet: >= 20th percentile
    """
    def _classify(p):
        if pd.isna(p):
            return "unknown"
        if p < DROUGHT_THRESHOLDS["extreme_drought"]:
            return "extreme_drought"
        if p < DROUGHT_THRESHOLDS["severe_drought"]:
            return "severe_drought"
        if p < DROUGHT_THRESHOLDS["moderate_drought"]:
            return "moderate_drought"
        if p < DROUGHT_THRESHOLDS["mild_drought"]:
            return "mild_drought"
        return "normal_or_wet"
    
    return percentile.apply(_classify)


def percentile_to_standardized(p: pd.Series) -> pd.Series:
    """Convert percentile (0-100) to standardized index (mean=0, std=1).
    
    Uses inverse normal CDF (probit transformation).
    Clips to avoid infinity at extremes.
    """
    x = np.clip(p / 100.0, 1e-6, 1 - 1e-6)
    return pd.Series(norm.ppf(x), index=p.index)


# =============================================================================
# STANDARDIZED INDICES (SPI, SPEI, SDI)
# =============================================================================

def calculate_spi(precip: pd.Series, timescale: int = 1) -> pd.Series:
    """Calculate Standardized Precipitation Index (SPI).
    
    Method:
    1. Accumulate precipitation over timescale months
    2. Fit gamma distribution to accumulated values
    3. Transform to cumulative probability
    4. Convert to standard normal (mean=0, std=1)
    
    Args:
        precip: Precipitation series (daily or monthly)
        timescale: Accumulation period in months (1, 3, 6, 12)
    
    Returns:
        SPI series (standardized, mean=0, std=1)
        Negative = dry, Positive = wet
    """
    # Convert to monthly if daily
    if len(precip) > 366:
        # Daily data: aggregate to monthly first
        dates = pd.to_datetime(precip.index) if hasattr(precip.index, 'to_datetime') else pd.Series(precip.index)
        # For simplicity, use rolling window approximation
        window_days = timescale * 30
        precip_accum = precip.rolling(window=window_days, min_periods=window_days//2).sum()
    else:
        # Already monthly
        precip_accum = precip if timescale == 1 else precip.rolling(window=timescale, min_periods=timescale).sum()
    
    # Handle zeros and negatives (add small constant)
    precip_pos = precip_accum.clip(lower=0.001)
    
    # Fit gamma distribution
    valid = precip_pos.dropna()
    if len(valid) < 10:
        return pd.Series(np.nan, index=precip_accum.index)
    
    try:
        # Gamma fit (shape, loc, scale)
        shape, loc, scale = gamma.fit(valid, floc=0)  # Fix location to 0
        
        # Cumulative probability
        prob = gamma.cdf(precip_pos, shape, loc=loc, scale=scale)
        
        # Transform to standard normal
        spi = norm.ppf(prob)
        
        return pd.Series(spi, index=precip_accum.index)
    
    except Exception as e:
        print(f"  ⚠ SPI-{timescale} calculation failed: {e}")
        return pd.Series(np.nan, index=precip_accum.index)


def calculate_spei(precip: pd.Series, pet: pd.Series, timescale: int = 1) -> pd.Series:
    """Calculate Standardized Precipitation Evapotranspiration Index (SPEI).
    
    Method:
    1. Calculate water balance: D = P - PET
    2. Accumulate over timescale months
    3. Fit log-logistic distribution
    4. Transform to standard normal
    
    Args:
        precip: Precipitation series
        pet: Potential evapotranspiration series
        timescale: Accumulation period in months
    
    Returns:
        SPEI series (standardized)
    """
    # Water balance
    wb = precip - pet
    
    # Accumulate
    if len(wb) > 366:
        window_days = timescale * 30
        wb_accum = wb.rolling(window=window_days, min_periods=window_days//2).sum()
    else:
        wb_accum = wb if timescale == 1 else wb.rolling(window=timescale, min_periods=timescale).sum()
    
    # Fit log-logistic (Fisk) distribution
    valid = wb_accum.dropna()
    if len(valid) < 10:
        return pd.Series(np.nan, index=wb_accum.index)
    
    try:
        # Log-logistic fit
        shape, loc, scale = fisk.fit(valid)
        
        # Cumulative probability
        prob = fisk.cdf(wb_accum, shape, loc=loc, scale=scale)
        
        # Transform to standard normal
        spei = norm.ppf(prob)
        
        return pd.Series(spei, index=wb_accum.index)
    
    except Exception as e:
        print(f"  ⚠ SPEI-{timescale} calculation failed: {e}")
        return pd.Series(np.nan, index=wb_accum.index)


def calculate_sdi(discharge: pd.Series, timescale: int = 3) -> pd.Series:
    """Calculate Streamflow Drought Index (SDI).
    
    Method:
    1. Accumulate discharge over timescale months
    2. Standardize (subtract mean, divide by std)
    
    Simpler than SPI/SPEI because discharge is already positive and continuous.
    
    Args:
        discharge: Discharge series (Qsim or Qobs)
        timescale: Accumulation period in months
    
    Returns:
        SDI series (standardized)
    """
    # Accumulate
    if len(discharge) > 366:
        window_days = timescale * 30
        q_accum = discharge.rolling(window=window_days, min_periods=window_days//2).sum()
    else:
        q_accum = discharge if timescale == 1 else discharge.rolling(window=timescale, min_periods=timescale).sum()
    
    # Standardize
    mean_q = q_accum.mean()
    std_q = q_accum.std()
    
    if pd.isna(std_q) or std_q == 0:
        return pd.Series(np.nan, index=q_accum.index)
    
    sdi = (q_accum - mean_q) / std_q
    
    return sdi


# =============================================================================
# MATRIX DROUGHT INDEX (MDI) — CORE INNOVATION
# =============================================================================

def calculate_mdi(smi: pd.Series, r_pctl: pd.Series, q_pctl: pd.Series,
                  weights: Dict[str, float] = MDI_WEIGHTS) -> pd.Series:
    """Calculate Matrix Drought Index (MDI).
    
    Weighted composite of three hydrological compartments:
    - SMI (soil moisture): immediate response
    - R-Pctl (recharge): lag-1 month (water percolates slowly)
    - Q-Pctl (discharge): lag-2 months (streamflow responds slowest)
    
    This captures drought propagation through the hydrological cycle!
    
    Args:
        smi: Soil Moisture Index (percentile, 0-100)
        r_pctl: Recharge Percentile (0-100)
        q_pctl: Discharge Percentile (0-100)
        weights: Dict with keys 'smi', 'recharge', 'discharge'
    
    Returns:
        MDI series (0-100, higher = wetter)
    """
    # Normalize to 0-1
    smi_norm = smi / 100.0
    r_norm = r_pctl / 100.0
    q_norm = q_pctl / 100.0
    
    # Apply lags (hydrological memory)
    # Recharge responds with ~1 month delay to soil moisture changes
    r_lagged = r_norm.shift(30)  # 30 days
    # Discharge responds with ~2 months delay
    q_lagged = q_norm.shift(60)  # 60 days
    
    # Weighted composite
    mdi = (weights["smi"] * smi_norm + 
           weights["recharge"] * r_lagged + 
           weights["discharge"] * q_lagged)
    
    # Convert back to 0-100 scale
    mdi = mdi * 100.0
    
    return mdi


# =============================================================================
# MAIN CALCULATION
# =============================================================================

def compute_all_indices(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all drought indices for a catchment.
    
    Input DataFrame must have columns:
    - date
    - precip, pet
    - sm_l01, sm_l02, sm_lall
    - recharge
    - qsim (and optionally qobs)
    
    Returns:
    DataFrame with all indices and drought classes.
    """
    print(f"Computing drought indices...")
    
    result = pd.DataFrame({"date": pd.to_datetime(df["date"])})
    # Preserve discharge series for downstream validation plots.
    if "qsim" in df.columns:
        result["qsim"] = pd.to_numeric(df["qsim"], errors="coerce")
    if "qobs" in df.columns:
        result["qobs"] = pd.to_numeric(df["qobs"], errors="coerce")
    
    # -------------------------------------------------------------------------
    # CORE INDICES (Paper #1) — Percentile-based
    # -------------------------------------------------------------------------
    print("  → Core percentile-based indices...")
    
    # SMI (Soil Moisture Index) — main layer (Lall)
    result["smi"] = calendar_percentile(df["date"], df["sm_lall"])
    result["smi_class"] = classify_drought(result["smi"])
    
    # SMI for individual layers (diagnostic)
    result["smi_l01"] = calendar_percentile(df["date"], df["sm_l01"])
    result["smi_l02"] = calendar_percentile(df["date"], df["sm_l02"])
    
    # R-Pctl (Recharge Percentile)
    result["r_pctl"] = calendar_percentile(df["date"], df["recharge"])
    result["r_pctl_class"] = classify_drought(result["r_pctl"])
    
    # Q-Pctl (Discharge Percentile) — prefer Qobs if available
    q_col = "qobs" if "qobs" in df.columns else "qsim"
    if q_col not in df.columns:
        print(f"  ⚠ No discharge column found ({q_col}), Q-Pctl will be NaN")
        result["q_pctl"] = np.nan
    else:
        result["q_pctl"] = calendar_percentile(df["date"], df[q_col])
    result["q_pctl_class"] = classify_drought(result["q_pctl"])
    
    # MDI (Matrix Drought Index) — THE INNOVATION
    print("  → Computing MDI (Matrix Drought Index)...")
    result["mdi"] = calculate_mdi(result["smi"], result["r_pctl"], result["q_pctl"])
    result["mdi_class"] = classify_drought(result["mdi"])
    
    # -------------------------------------------------------------------------
    # COMPARISON INDICES — Standardized
    # -------------------------------------------------------------------------
    print("  → Standardized indices (SPI, SPEI, SDI)...")
    
    # SPI (1, 3, 6 months)
    result["spi_1"] = calculate_spi(df["precip"], timescale=1)
    result["spi_3"] = calculate_spi(df["precip"], timescale=3)
    result["spi_6"] = calculate_spi(df["precip"], timescale=6)
    
    # SPEI (1, 3, 6 months)
    result["spei_1"] = calculate_spei(df["precip"], df["pet"], timescale=1)
    result["spei_3"] = calculate_spei(df["precip"], df["pet"], timescale=3)
    result["spei_6"] = calculate_spei(df["precip"], df["pet"], timescale=6)
    
    # SDI (3, 6 months)
    if q_col in df.columns:
        result["sdi_3"] = calculate_sdi(df[q_col], timescale=3)
        result["sdi_6"] = calculate_sdi(df[q_col], timescale=6)
    else:
        result["sdi_3"] = np.nan
        result["sdi_6"] = np.nan
    
    # -------------------------------------------------------------------------
    # DROUGHT STATISTICS
    # -------------------------------------------------------------------------
    print("  → Computing drought statistics...")
    
    drought_summary = {}
    for idx_col in ["smi", "r_pctl", "q_pctl", "mdi"]:
        class_col = f"{idx_col}_class"
        if class_col in result.columns:
            counts = result[class_col].value_counts().to_dict()
            # Convert numpy int to Python int for JSON serialization
            counts = {k: int(v) for k, v in counts.items()}
            drought_summary[idx_col] = counts
    
    result.attrs["drought_summary"] = drought_summary
    result.attrs["catchment"] = df.attrs.get("catchment", "unknown")
    result.attrs["gauge_id"] = df.attrs.get("gauge_id", "unknown")
    
    return result


def save_indices(result: pd.DataFrame, output_dir: Path, catchment_name: str):
    """Save indices to files with metadata."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Full indices (Parquet preserves metadata)
    parquet_path = output_dir / "drought_indices.parquet"
    result.to_parquet(parquet_path, index=False)
    print(f"  ✓ Saved indices (Parquet): {parquet_path}")
    
    # CSV (universal, no metadata)
    csv_path = output_dir / "drought_indices.csv"
    result.to_csv(csv_path, index=False)
    print(f"  ✓ Saved indices (CSV): {csv_path}")
    
    # Summary JSON
    summary = {
        "catchment": catchment_name,
        "gauge_id": result.attrs.get("gauge_id", "unknown"),
        "date_range": {
            "start": str(result["date"].min()),
            "end": str(result["date"].max()),
            "days": len(result),
        },
        "indices_calculated": [
            "smi", "smi_l01", "smi_l02",
            "r_pctl", "q_pctl",
            "mdi",
            "spi_1", "spi_3", "spi_6",
            "spei_1", "spei_3", "spei_6",
            "sdi_3", "sdi_6",
        ],
        "drought_summary": result.attrs.get("drought_summary", {}),
        "thresholds": DROUGHT_THRESHOLDS,
        "mdi_weights": MDI_WEIGHTS,
        "methodology": {
            "percentile_method": "empirical_ranking",
            "calendar_basis": "day_of_year_for_daily_data",
            "seasonal_bias": "removed",
        },
    }
    
    summary_path = output_dir / "indices_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  ✓ Saved summary: {summary_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="02_compute_indices.py — Calculate drought indices (QUALITY-FIRST)"
    )
    parser.add_argument("--catchment", type=str, default="Chemnitz2_0p0625",
                        help="Catchment name or 'all' for all")
    parser.add_argument("--input-dir", type=Path, default=None,
                        help="Input directory (default: analysis/results/<catchment>)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: same as input)")
    args = parser.parse_args()
    
    # Import catchment list from 01_load_data
    import sys
    import importlib.util
    script_path = REPO / "analysis" / "scripts" / "01_load_data.py"
    spec = importlib.util.spec_from_file_location("load_data", script_path)
    load_data_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(load_data_module)
    CATCHMENTS = load_data_module.CATCHMENTS
    
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
            # Determine input directory
            if args.input_dir:
                input_dir = args.input_dir / catchment_name
            else:
                input_dir = REPO / "analysis" / "results" / catchment_name
            
            # Load data
            data_path = input_dir / "drought_data.parquet"
            if not data_path.exists():
                data_path = input_dir / "drought_data.csv"
            
            if not data_path.exists():
                raise FileNotFoundError(
                    f"No data found in {input_dir}. Run 01_load_data.py first!"
                )
            
            print(f"  → Loading data from {data_path}")
            if data_path.suffix == ".parquet":
                df = pd.read_parquet(data_path)
            else:
                df = pd.read_csv(data_path, parse_dates=["date"])
            
            # Compute indices
            result = compute_all_indices(df)
            
            # Determine output directory
            output_dir = args.output_dir / catchment_name if args.output_dir else input_dir
            
            # Save indices
            save_indices(result, output_dir, catchment_name)
            
            # Print summary
            print(f"\n  📊 Drought Summary:")
            summary = result.attrs.get("drought_summary", {})
            for idx, counts in summary.items():
                total = sum(counts.values())
                drought_days = sum(v for k, v in counts.items() if "drought" in k)
                pct = (drought_days / total * 100) if total > 0 else 0
                print(f"    {idx}: {drought_days}/{total} days ({pct:.1f}%) in drought")
            
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
