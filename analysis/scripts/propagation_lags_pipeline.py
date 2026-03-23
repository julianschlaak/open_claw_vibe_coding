#!/usr/bin/env python3
"""
Drought Propagation Lags Pipeline
Computes cross-correlations between hydrological compartments:
- Precipitation → Soil Moisture (P→SM)
- Soil Moisture → Recharge (SM→R)
- Recharge → Discharge (R→Q)

Output: Lag correlation matrix, optimal lag times per catchment
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr
import json

# Catchment configuration
CATCHMENTS = [
    'chemnitz2', 'wesenitz2', 'parthe', 'wyhra', 
    'goeltzsch2', 'zwoenitz1', 'saxony'
]

RESULTS_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results')
OUTPUT_FILE = RESULTS_DIR / 'propagation_lags.json'

def compute_lag_correlation(series_a, series_b, max_lag_months=24):
    """Compute correlation between two series at different lags."""
    correlations = {}
    
    for lag in range(max_lag_months + 1):
        # Lag series_a by 'lag' months
        if lag == 0:
            corr, _ = pearsonr(series_a, series_b)
        else:
            # Shift series_a forward (a leads b by 'lag' months)
            a_lagged = series_a[:-lag]
            b_trimmed = series_b[lag:]
            
            if len(a_lagged) > 10:
                corr, _ = pearsonr(a_lagged, b_trimmed)
            else:
                corr = np.nan
        
        correlations[lag] = corr
    
    return correlations

def find_optimal_lag(correlations):
    """Find lag with maximum correlation."""
    valid_lags = {k: v for k, v in correlations.items() if pd.notna(v)}
    
    if not valid_lags:
        return None, np.nan
    
    optimal_lag = max(valid_lags, key=valid_lags.get)
    max_corr = valid_lags[optimal_lag]
    
    return optimal_lag, max_corr

def process_catchment(cut_name):
    """Process single catchment for propagation lags."""
    print(f"\n🏞️  Processing: {cut_name.upper()}")
    
    csv_path = RESULTS_DIR / cut_name / 'monthly_drought_indices.csv'
    
    if not csv_path.exists():
        print(f"❌ Not found: {csv_path}")
        return None
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Required columns
    required = ['precip', 'sm_volumetric', 'recharge_mm', 'runoff_mm']
    available = [c for c in required if c in df.columns]
    
    if len(available) < 4:
        print(f"⚠️  Missing columns. Available: {available}")
        # Use proxies
        if 'sm_volumetric' not in df.columns:
            df['sm_volumetric'] = df.get('sm_percent', np.nan)
        if 'recharge_mm' not in df.columns:
            df['recharge_mm'] = df.get('recharge_percent', np.nan)
        if 'runoff_mm' not in df.columns:
            df['runoff_mm'] = df.get('runoff_percent', np.nan)
        if 'precip' not in df.columns:
            # No precip available, skip P→SM
            print(f"   No precipitation data, skipping P→SM")
    
    # Clean data (remove NaN)
    df = df.dropna(subset=['sm_volumetric', 'recharge_mm', 'runoff_mm'])
    
    if len(df) < 50:
        print(f"⚠️  Too few data points: {len(df)}")
        return None
    
    print(f"   ✅ {len(df)} monthly records")
    
    # Compute lag correlations
    results = {
        'catchment': cut_name,
        'n_months': len(df),
        'lags': {},
    }
    
    # P → SM (if precip available)
    if 'precip' in df.columns:
        print("   Computing P → SM lags...")
        p_sm_corr = compute_lag_correlation(df['precip'].values, df['sm_volumetric'].values, max_lag_months=24)
        optimal_lag, max_corr = find_optimal_lag(p_sm_corr)
        results['lags']['P_to_SM'] = {
            'optimal_lag_months': optimal_lag,
            'max_correlation': float(max_corr) if pd.notna(max_corr) else None,
            'correlations': {str(k): float(v) if pd.notna(v) else None for k, v in p_sm_corr.items()}
        }
        print(f"   Optimal lag: {optimal_lag} months, r = {max_corr:.3f}")
    else:
        results['lags']['P_to_SM'] = None
    
    # SM → Recharge
    print("   Computing SM → Recharge lags...")
    sm_r_corr = compute_lag_correlation(df['sm_volumetric'].values, df['recharge_mm'].values, max_lag_months=24)
    optimal_lag, max_corr = find_optimal_lag(sm_r_corr)
    results['lags']['SM_to_Recharge'] = {
        'optimal_lag_months': optimal_lag,
        'max_correlation': float(max_corr) if pd.notna(max_corr) else None,
        'correlations': {str(k): float(v) if pd.notna(v) else None for k, v in sm_r_corr.items()}
    }
    print(f"   Optimal lag: {optimal_lag} months, r = {max_corr:.3f}")
    
    # Recharge → Discharge (using runoff as proxy)
    print("   Computing Recharge → Discharge lags...")
    r_q_corr = compute_lag_correlation(df['recharge_mm'].values, df['runoff_mm'].values, max_lag_months=24)
    optimal_lag, max_corr = find_optimal_lag(r_q_corr)
    results['lags']['Recharge_to_Discharge'] = {
        'optimal_lag_months': optimal_lag,
        'max_correlation': float(max_corr) if pd.notna(max_corr) else None,
        'correlations': {str(k): float(v) if pd.notna(v) else None for k, v in r_q_corr.items()}
    }
    print(f"   Optimal lag: {optimal_lag} months, r = {max_corr:.3f}")
    
    # Full cascade: P → Q (if precip available)
    if 'precip' in df.columns:
        print("   Computing P → Discharge lags...")
        p_q_corr = compute_lag_correlation(df['precip'].values, df['runoff_mm'].values, max_lag_months=24)
        optimal_lag, max_corr = find_optimal_lag(p_q_corr)
        results['lags']['P_to_Discharge'] = {
            'optimal_lag_months': optimal_lag,
            'max_correlation': float(max_corr) if pd.notna(max_corr) else None,
            'correlations': {str(k): float(v) if pd.notna(v) else None for k, v in p_q_corr.items()}
        }
        print(f"   Optimal lag: {optimal_lag} months, r = {max_corr:.3f}")
    
    return results

# Process all catchments
print("🚀 Drought Propagation Lags Pipeline")
print("="*60)

all_results = []
for cut_name in CATCHMENTS:
    result = process_catchment(cut_name)
    if result is not None:
        all_results.append(result)

# Save results
if all_results:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("✅ Propagation Lags complete!")
    print(f"📁 Saved: {OUTPUT_FILE}")
    
    # Summary table
    print("\n📊 Summary:")
    print(f"{'Catchment':<15} {'P→SM':<10} {'SM→R':<10} {'R→Q':<10} {'P→Q':<10}")
    print("-"*60)
    for result in all_results:
        p_sm = result['lags'].get('P_to_SM', {})
        sm_r = result['lags'].get('SM_to_Recharge', {})
        r_q = result['lags'].get('Recharge_to_Discharge', {})
        p_q = result['lags'].get('P_to_Discharge', {})
        
        p_sm_str = f"{p_sm.get('optimal_lag_months', 'N/A')} ({p_sm.get('max_correlation', 0):.2f})" if p_sm else "N/A"
        sm_r_str = f"{sm_r.get('optimal_lag_months', 'N/A')} ({sm_r.get('max_correlation', 0):.2f})"
        r_q_str = f"{r_q.get('optimal_lag_months', 'N/A')} ({r_q.get('max_correlation', 0):.2f})"
        p_q_str = f"{p_q.get('optimal_lag_months', 'N/A')} ({p_q.get('max_correlation', 0):.2f})" if p_q else "N/A"
        
        print(f"{result['catchment']:<15} {p_sm_str:<10} {sm_r_str:<10} {r_q_str:<10} {p_q_str:<10}")
else:
    print("\n❌ No results computed")

print("="*60)
