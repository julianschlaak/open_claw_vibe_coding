#!/usr/bin/env python3
"""
Six Catchments Drought Indices Pipeline
Processes mHM output for 6 Saxonian catchments and computes MDI
Output: CSV files for dashboards
"""

import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

# Catchment configuration
CATCHMENTS = {
    'chemnitz2': 'chemnitz2_0p0625',
    'wesenitz2': 'wesenitz2_0p0625',
    'parthe': 'parthe_0p0625',
    'wyhra': 'wyhra_0p0625',
    'goeltzsch2': 'goeltzsch2_0p0625',
    'zwoenitz1': 'zwoenitz1_0p0625',
}

BASE_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs')
OUTPUT_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results')

def process_catchment(name, run_folder):
    """Process single catchment from mHM NetCDF output."""
    print(f"\n{'='*60}")
    print(f"🏞️  Processing: {name.upper()} ({run_folder})")
    print('='*60)
    
    # Paths
    nc_path = BASE_DIR / run_folder / 'output' / 'mHM_Fluxes_States.nc'
    discharge_path = BASE_DIR / run_folder / 'output' / 'daily_discharge.out'
    out_folder = OUTPUT_DIR / name
    out_folder.mkdir(parents=True, exist_ok=True)
    
    # Check files exist
    if not nc_path.exists():
        print(f"❌ NetCDF not found: {nc_path}")
        return None
    
    # Load NetCDF
    ds = xr.open_dataset(nc_path)
    
    # Spatial mean (catchment is already masked in NetCDF)
    sm_lall = ds['SM_Lall'].mean(dim=['lon', 'lat']).values  # mm/mm (volumetric)
    q = ds['Q'].mean(dim=['lon', 'lat']).values  # mm/month (runoff)
    qd = ds['QD'].mean(dim=['lon', 'lat']).values  # mm/month (recharge/drainage)
    
    # Time coordinate
    time = ds['time'].values
    dates = pd.to_datetime(time)
    
    print(f"✅ Time range: {dates[0]} to {dates[-1]} ({len(dates)} months)")
    print(f"✅ SM range: {sm_lall.min():.3f} - {sm_lall.max():.3f} mm/mm")
    print(f"✅ Runoff range: {q.min():.1f} - {q.max():.1f} mm/month")
    print(f"✅ Recharge range: {qd.min():.1f} - {qd.max():.1f} mm/month")
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'sm_volumetric': sm_lall,
        'runoff_mm': q,
        'recharge_mm': qd,
    })
    
    # Month-based percentile calculation
    def month_percentile(series, dates):
        df_temp = pd.DataFrame({'value': series.values, 'date': dates})
        df_temp['month'] = df_temp['date'].dt.month
        df_temp['year'] = df_temp['date'].dt.year
        
        percentiles = []
        for i, row in df_temp.iterrows():
            same_month = df_temp[
                (df_temp['month'] == row['month']) & 
                (df_temp['year'] != row['year'])
            ]['value']
            
            if len(same_month) < 5:
                percentiles.append(np.nan)
            else:
                pct = (same_month < row['value']).sum() / len(same_month) * 100
                percentiles.append(pct)
        
        return percentiles
    
    print("🧮 Computing percentiles...")
    df['sm_percent'] = month_percentile(df['sm_volumetric'], df['date'])
    df['recharge_percent'] = month_percentile(df['recharge_mm'], df['date'])
    df['runoff_percent'] = month_percentile(df['runoff_mm'], df['date'])
    
    # MDI Calculation
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
    output_csv = out_folder / 'monthly_drought_indices.csv'
    df.to_csv(output_csv, index=False)
    
    # Summary
    drought_days = df[df['mdi_class'].isin(['extreme_drought', 'severe_drought', 'moderate_drought'])]
    print(f"\n📊 Summary:")
    print(f"   Period: {df['date'].min()} to {df['date'].max()}")
    print(f"   MDI drought days: {len(drought_days)} ({len(drought_days)/len(df)*100:.1f}%)")
    
    # 2018-2020 drought
    drought_2018_2020 = df[(df['year'] >= 2018) & (df['year'] <= 2020)]
    if len(drought_2018_2020) > 0:
        mdi_min = drought_2018_2020['mdi_percent'].min()
        drought_days_2018_2020 = (drought_2018_2020['mdi_percent'] < 20).sum()
        print(f"   2018-2020 MDI min: {mdi_min:.1f}")
        print(f"   2018-2020 drought days: {drought_days_2018_2020}")
    
    print(f"✅ Saved: {output_csv}")
    
    return df

# Process all catchments
print("🚀 Six Catchments Drought Indices Pipeline")
print("="*60)

results = {}
for name, run_folder in CATCHMENTS.items():
    df = process_catchment(name, run_folder)
    if df is not None:
        results[name] = df

# Create aggregated "saxony" summary (mean of 6 catchments)
print(f"\n{'='*60}")
print("🗺️  Creating Saxony Aggregation (6 catchments mean)")
print('='*60)

# Merge all catchments on date
merged = None
for name, df in results.items():
    df_copy = df[['date', 'sm_volumetric', 'runoff_mm', 'recharge_mm']].copy()
    df_copy.columns = ['date', f'sm_{name}', f'runoff_{name}', f'recharge_{name}']
    
    if merged is None:
        merged = df_copy
    else:
        merged = merged.merge(df_copy, on='date', how='inner')

# Compute mean across catchments
saxony_agg = pd.DataFrame({
    'date': merged['date'],
    'sm_volumetric': merged[[c for c in merged.columns if c.startswith('sm_')]].mean(axis=1),
    'runoff_mm': merged[[c for c in merged.columns if c.startswith('runoff_')]].mean(axis=1),
    'recharge_mm': merged[[c for c in merged.columns if c.startswith('recharge_')]].mean(axis=1),
})

# Compute percentiles for aggregated Saxony
def month_percentile(series, dates):
    df_temp = pd.DataFrame({'value': series.values, 'date': dates})
    df_temp['month'] = df_temp['date'].dt.month
    df_temp['year'] = df_temp['date'].dt.year
    
    percentiles = []
    for i, row in df_temp.iterrows():
        same_month = df_temp[
            (df_temp['month'] == row['month']) & 
            (df_temp['year'] != row['year'])
        ]['value']
        
        if len(same_month) < 5:
            percentiles.append(np.nan)
        else:
            pct = (same_month < row['value']).sum() / len(same_month) * 100
            percentiles.append(pct)
    
    return percentiles

saxony_agg['sm_percent'] = month_percentile(saxony_agg['sm_volumetric'], saxony_agg['date'])
saxony_agg['recharge_percent'] = month_percentile(saxony_agg['recharge_mm'], saxony_agg['date'])
saxony_agg['runoff_percent'] = month_percentile(saxony_agg['runoff_mm'], saxony_agg['date'])
saxony_agg['mdi_percent'] = (
    0.4 * saxony_agg['sm_percent'] + 
    0.3 * saxony_agg['recharge_percent'] + 
    0.3 * saxony_agg['runoff_percent']
)

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

saxony_agg['sm_class'] = saxony_agg['sm_percent'].apply(drought_class)
saxony_agg['recharge_class'] = saxony_agg['recharge_percent'].apply(drought_class)
saxony_agg['runoff_class'] = saxony_agg['runoff_percent'].apply(drought_class)
saxony_agg['mdi_class'] = saxony_agg['mdi_percent'].apply(drought_class)
saxony_agg['year'] = saxony_agg['date'].dt.year
saxony_agg['month'] = saxony_agg['date'].dt.month

# Save aggregated Saxony
saxony_out = OUTPUT_DIR / 'saxony' / 'monthly_drought_indices.csv'
saxony_out.parent.mkdir(parents=True, exist_ok=True)
saxony_agg.to_csv(saxony_out, index=False)

print(f"\n📊 Saxony Aggregation Summary:")
print(f"   Period: {saxony_agg['date'].min()} to {saxony_agg['date'].max()}")
drought_days_sax = saxony_agg[saxony_agg['mdi_class'].isin(['extreme_drought', 'severe_drought', 'moderate_drought'])]
print(f"   MDI drought days: {len(drought_days_sax)} ({len(drought_days_sax)/len(saxony_agg)*100:.1f}%)")
drought_2018_2020_sax = saxony_agg[(saxony_agg['year'] >= 2018) & (saxony_agg['year'] <= 2020)]
if len(drought_2018_2020_sax) > 0:
    mdi_min_sax = drought_2018_2020_sax['mdi_percent'].min()
    drought_days_2018_2020_sax = (drought_2018_2020_sax['mdi_percent'] < 20).sum()
    print(f"   2018-2020 MDI min: {mdi_min_sax:.1f}")
    print(f"   2018-2020 drought days: {drought_days_2018_2020_sax}")
print(f"✅ Saved: {saxony_out}")

print(f"\n{'='*60}")
print("✅ Pipeline complete!")
print(f"📁 Output folders: {list(OUTPUT_DIR.iterdir())}")
print('='*60)
