#!/usr/bin/env python3
"""
Daily Discharge Integration Pipeline
Parses daily_discharge.out files and merges with monthly drought indices
Output: Updated monthly_drought_indices.csv with discharge stats
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

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
RESULTS_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results')

def parse_daily_discharge(cut_name, run_folder):
    """Parse daily_discharge.out file."""
    print(f"\n📊 Parsing daily discharge: {cut_name}")
    
    discharge_path = BASE_DIR / run_folder / 'output' / 'daily_discharge.out'
    
    if not discharge_path.exists():
        print(f"❌ Not found: {discharge_path}")
        return None
    
    # Read file (skip header line, whitespace delimited)
    df = pd.read_csv(discharge_path, skiprows=1, delim_whitespace=True)
    
    # Clean column names
    df.columns = ['no', 'day', 'mon', 'year', 'qobs', 'qsim']
    
    # Create date column
    df['date'] = pd.to_datetime({'year': df['year'], 'month': df['mon'], 'day': df['day']})
    
    print(f"✅ Loaded {len(df)} daily records ({df['date'].min()} to {df['date'].max()})")
    print(f"   Qobs range: {df['qobs'].min():.2f} - {df['qobs'].max():.2f}")
    print(f"   Qsim range: {df['qsim'].min():.2f} - {df['qsim'].max():.2f}")
    
    return df

def aggregate_to_monthly(daily_df):
    """Aggregate daily discharge to monthly statistics."""
    print("   Aggregating to monthly...")
    
    monthly = daily_df.groupby(['year', 'mon']).agg({
        'qobs': ['mean', 'min', 'max', 'std'],
        'qsim': ['mean', 'min', 'max', 'std'],
    }).reset_index()
    
    # Flatten column names
    monthly.columns = ['year', 'mon', 'qobs_mean', 'qobs_min', 'qobs_max', 'qobs_std',
                       'qsim_mean', 'qsim_min', 'qsim_max', 'qsim_std']
    
    # Create date column
    monthly['date'] = pd.to_datetime({'year': monthly['year'], 'month': monthly['mon'], 'day': 1})
    
    print(f"   ✅ Created {len(monthly)} monthly records")
    
    return monthly

def merge_with_drought_indices(cut_name, monthly_discharge):
    """Merge discharge data with existing drought indices."""
    csv_path = RESULTS_DIR / cut_name / 'monthly_drought_indices.csv'
    
    if not csv_path.exists():
        print(f"❌ Drought indices not found: {csv_path}")
        return None
    
    # Load existing data
    drought_df = pd.read_csv(csv_path)
    drought_df['date'] = pd.to_datetime(drought_df['date'])
    
    # Merge
    merged = drought_df.merge(
        monthly_discharge[['date', 'qobs_mean', 'qobs_min', 'qobs_max', 'qobs_std',
                           'qsim_mean', 'qsim_min', 'qsim_max', 'qsim_std']],
        on='date',
        how='left'
    )
    
    # Compute discharge percentile (month-based, like other percentiles)
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
    
    print("   Computing discharge percentiles...")
    merged['qobs_percent'] = month_percentile(merged['qobs_mean'], merged['date'])
    merged['qsim_percent'] = month_percentile(merged['qsim_mean'], merged['date'])
    
    # Save updated file
    merged.to_csv(csv_path, index=False)
    
    print(f"   ✅ Updated {csv_path}")
    print(f"   New columns: qobs_mean/min/max/std, qsim_mean/min/max/std, qobs_percent, qsim_percent")
    
    return merged

# Process all catchments
print("🚀 Daily Discharge Integration Pipeline")
print("="*60)

for cut_name, run_folder in CATCHMENTS.items():
    print(f"\n{'='*60}")
    print(f"🏞️  Processing: {cut_name.upper()}")
    print('='*60)
    
    daily_df = parse_daily_discharge(cut_name, run_folder)
    if daily_df is None:
        continue
    
    monthly_discharge = aggregate_to_monthly(daily_df)
    merged = merge_with_drought_indices(cut_name, monthly_discharge)
    
    if merged is not None:
        # Summary
        print(f"\n📊 {cut_name} Summary:")
        print(f"   Period: {merged['date'].min()} to {merged['date'].max()}")
        print(f"   Qobs mean: {merged['qobs_mean'].mean():.2f} ± {merged['qobs_mean'].std():.2f}")
        print(f"   Qsim mean: {merged['qsim_mean'].mean():.2f} ± {merged['qsim_mean'].std():.2f}")
        
        # KGE computation (simple version)
        valid = merged.dropna(subset=['qobs_mean', 'qsim_mean'])
        if len(valid) > 10:
            from scipy.stats import pearsonr
            r = pearsonr(valid['qobs_mean'], valid['qsim_mean'])[0]
            print(f"   Qobs-Qsim correlation: r = {r:.3f}")

print(f"\n{'='*60}")
print("✅ Daily Discharge Integration complete!")
print('='*60)
