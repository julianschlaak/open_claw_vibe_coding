#!/usr/bin/env python3
"""
Saxony Raster Drought Indices Pipeline
Extracts SM, Recharge, Runoff from mHM NetCDF and computes MDI (DOY-based percentile)
Output: CSV for dashboards (1991-2020, 30 years)
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Paths
NC_PATH = Path('/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/runs/saxony_0p0625/output/mHM_Fluxes_States.nc')
DISCHARGE_PATH = Path('/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/runs/saxony_0p0625/output/daily_discharge.out')
OUTPUT_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/saxony_0p0625')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"🔍 Loading mHM NetCDF: {NC_PATH}")
print(f"📊 Output directory: {OUTPUT_DIR}")

# Load NetCDF
ds = xr.open_dataset(NC_PATH)
print(f"✅ Dimensions: {dict(ds.dims)}")
print(f"✅ Time range: {ds.time.values[0]} to {ds.time.values[-1]}")

# Extract variables (spatial mean over Saxony)
print("\n📈 Extracting variables (spatial mean)...")
sm_lall = ds['SM_Lall'].mean(dim=['lon', 'lat']).values  # mm
q = ds['Q'].mean(dim=['lon', 'lat']).values  # mm (runoff)
qd = ds['QD'].mean(dim=['lon', 'lat']).values  # mm (drainage/recharge)

# Time coordinate
time = ds['time'].values
dates = pd.to_datetime(time)
print(f"✅ Date range: {dates[0]} to {dates[-1]} ({len(dates)} months)")

# Check if monthly or daily
if len(dates) > 1000:
    freq = 'daily'
else:
    freq = 'monthly'
print(f"✅ Frequency: {freq} ({len(dates)} time steps)")

# Create DataFrame
# Note: SM_Lall is already volumetric (mm/mm), Q and QD are mm/month
df = pd.DataFrame({
    'date': dates,
    'sm_volumetric': sm_lall,  # Already mm/mm
    'runoff_mm': q,  # mm/month
    'recharge_mm': qd,  # mm/month (using QD as proxy)
})

print(f"\n📊 Data shape: {df.shape}")
print(f"   Columns: {list(df.columns)}")
print(f"   SM range: {df['sm_volumetric'].min():.3f} - {df['sm_volumetric'].max():.3f} mm/mm (volumetric)")
print(f"   Runoff range: {df['runoff_mm'].min():.1f} - {df['runoff_mm'].max():.1f} mm/month")
print(f"   Recharge range: {df['recharge_mm'].min():.1f} - {df['recharge_mm'].max():.1f} mm/month")

# Month-based Percentile Calculation (for monthly data)
print("\n🧮 Computing month-based percentiles...")

def month_percentile(series, dates):
    """Compute percentile for each month relative to same month in reference period."""
    df_temp = pd.DataFrame({'value': series.values, 'date': dates})
    df_temp['month'] = df_temp['date'].dt.month
    df_temp['year'] = df_temp['date'].dt.year
    
    percentiles = []
    for i, row in df_temp.iterrows():
        # Get all values for same month (excluding current year for independence)
        same_month = df_temp[
            (df_temp['month'] == row['month']) & 
            (df_temp['year'] != row['year'])
        ]['value']
        
        if len(same_month) < 5:
            percentiles.append(np.nan)
        else:
            # Percentile rank of current value among historical month values
            pct = (same_month < row['value']).sum() / len(same_month) * 100
            percentiles.append(pct)
    
    return percentiles

# Compute percentiles
print("   Computing SM percentile (month-based)...")
df['sm_percent'] = month_percentile(df['sm_volumetric'], df['date'])

print("   Computing Recharge percentile (month-based)...")
df['recharge_percent'] = month_percentile(df['recharge_mm'], df['date'])

print("   Computing Runoff percentile (month-based)...")
df['runoff_percent'] = month_percentile(df['runoff_mm'], df['date'])

# MDI Calculation (weighted average)
print("\n🧮 Computing Matrix Drought Index (MDI)...")
# MDI = 0.4 * SM + 0.3 * Recharge + 0.3 * Runoff
df['mdi_percent'] = (
    0.4 * df['sm_percent'] + 
    0.3 * df['recharge_percent'] + 
    0.3 * df['runoff_percent']
)

# Drought classification
def drought_class(pct):
    if pd.isna(pct):
        return 'unknown'
    if pct < 5:
        return 'extreme_drought'
    elif pct < 10:
        return 'severe_drought'
    elif pct < 20:
        return 'moderate_drought'
    elif pct < 80:
        return 'normal_or_wet'
    else:
        return 'wet'

df['sm_class'] = df['sm_percent'].apply(drought_class)
df['recharge_class'] = df['recharge_percent'].apply(drought_class)
df['runoff_class'] = df['runoff_percent'].apply(drought_class)
df['mdi_class'] = df['mdi_percent'].apply(drought_class)

# Add year, month
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Save to CSV
output_csv = OUTPUT_DIR / 'saxony_drought_indices.csv'
print(f"\n💾 Saving to {output_csv}...")
df.to_csv(output_csv, index=False)

# Summary statistics
print("\n" + "="*60)
print("📊 SUMMARY STATISTICS")
print("="*60)
print(f"Period: {df['date'].min()} to {df['date'].max()} ({len(df)} days)")
print(f"SM percentile: {df['sm_percent'].mean():.1f} ± {df['sm_percent'].std():.1f}")
print(f"Recharge percentile: {df['recharge_percent'].mean():.1f} ± {df['recharge_percent'].std():.1f}")
print(f"Runoff percentile: {df['runoff_percent'].mean():.1f} ± {df['runoff_percent'].std():.1f}")
print(f"MDI: {df['mdi_percent'].mean():.1f} ± {df['mdi_percent'].std():.1f}")

# Drought days summary
drought_days = df[df['mdi_class'].isin(['extreme_drought', 'severe_drought', 'moderate_drought'])]
print(f"\n🌵 Total MDI drought days: {len(drought_days)} ({len(drought_days)/len(df)*100:.1f}%)")
print(f"   Extreme: {(df['mdi_class']=='extreme_drought').sum()}")
print(f"   Severe: {(df['mdi_class']=='severe_drought').sum()}")
print(f"   Moderate: {(df['mdi_class']=='moderate_drought').sum()}")

# 2018-2020 drought
drought_2018_2020 = df[(df['year'] >= 2018) & (df['year'] <= 2020)]
mdi_min = drought_2018_2020['mdi_percent'].min()
drought_days_2018_2020 = (drought_2018_2020['mdi_percent'] < 20).sum()
print(f"\n🔥 2018-2020 Drought:")
print(f"   MDI minimum: {mdi_min:.1f}")
print(f"   Drought days (<20): {drought_days_2018_2020}")

print("\n✅ Pipeline complete!")
print(f"📁 Output: {output_csv}")
