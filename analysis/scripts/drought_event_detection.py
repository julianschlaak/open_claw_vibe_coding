#!/usr/bin/env python3
"""
Drought Event Detection Pipeline
Identifies drought events based on MDI, SPI, and SMI thresholds
Computes event statistics: start, end, duration, severity, peak deficit
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

# Catchment configuration
CATCHMENTS = [
    'chemnitz2', 'wesenitz2', 'parthe', 'wyhra', 
    'goeltzsch2', 'zwoenitz1', 'saxony'
]

RESULTS_DIR = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results')
OUTPUT_FILE = RESULTS_DIR / 'drought_events.json'

# Drought thresholds (percentile-based)
THRESHOLDS = {
    'extreme': 5,
    'severe': 10,
    'moderate': 20,
    'near_normal': 50,
}

def detect_events(series: pd.Series, threshold: float = 20, min_duration: int = 3) -> list:
    """
    Detect drought events from percentile time series.
    
    Args:
        series: Percentile time series (0-100)
        threshold: Drought threshold (default 20 = drought below 20th percentile)
        min_duration: Minimum event duration in months
    
    Returns:
        List of event dictionaries
    """
    drought = (series < threshold).astype(int)
    
    events = []
    in_event = False
    event_start = None
    event_values = []
    
    for i, (date, val) in enumerate(series.items()):
        if drought.iloc[i] and not in_event:
            # Start new event
            in_event = True
            event_start = i
            event_values = [val]
        elif drought.iloc[i] and in_event:
            # Continue event
            event_values.append(val)
        elif not drought.iloc[i] and in_event:
            # End event
            in_event = False
            if len(event_values) >= min_duration:
                events.append({
                    'start_idx': event_start,
                    'end_idx': i - 1,
                    'start_date': str(series.index[event_start]),
                    'end_date': str(series.index[i - 1]),
                    'duration_months': len(event_values),
                    'severity': 'extreme' if all(v < 5 for v in event_values) else \
                              'severe' if all(v < 10 for v in event_values) else \
                              'moderate',
                    'min_value': float(min(event_values)),
                    'mean_value': float(np.mean(event_values)),
                    'max_value': float(max(event_values)),
                    'deficit': float(threshold - np.mean(event_values)),
                    'integrated_deficit': float(sum(threshold - v for v in event_values)),
                })
            event_values = []
    
    # Handle event still ongoing at end of series
    if in_event and len(event_values) >= min_duration:
        events.append({
            'start_idx': event_start,
            'end_idx': len(series) - 1,
            'start_date': str(series.index[event_start]),
            'end_date': str(series.index[-1]),
            'duration_months': len(event_values),
            'severity': 'extreme' if all(v < 5 for v in event_values) else \
                      'severe' if all(v < 10 for v in event_values) else \
                      'moderate',
            'min_value': float(min(event_values)),
            'mean_value': float(np.mean(event_values)),
            'max_value': float(max(event_values)),
            'deficit': float(threshold - np.mean(event_values)),
            'integrated_deficit': float(sum(threshold - v for v in event_values)),
        })
    
    return events

def compute_event_statistics(events: list, series: pd.Series, threshold: float = 20) -> dict:
    """Compute summary statistics for all events."""
    if not events:
        return {
            'n_events': 0,
            'mean_duration': 0,
            'max_duration': 0,
            'total_drought_months': 0,
            'mean_deficit': 0,
            'total_integrated_deficit': 0,
        }
    
    durations = [e['duration_months'] for e in events]
    
    # Handle different event structures (MDI vs compound)
    deficits = []
    integrated = []
    for e in events:
        if 'deficit' in e:
            deficits.append(e['deficit'])
        if 'integrated_deficit' in e:
            integrated.append(e['integrated_deficit'])
        elif 'mean_mdi' in e:
            # Compound events: deficit = (threshold - mean_mdi) * duration
            deficits.append((threshold - e['mean_mdi']) * e['duration_months'])
    
    return {
        'n_events': len(events),
        'mean_duration': float(np.mean(durations)),
        'max_duration': max(durations),
        'min_duration': min(durations),
        'total_drought_months': sum(durations),
        'mean_deficit': float(np.mean(deficits)) if deficits else 0,
        'max_deficit': max(deficits) if deficits else 0,
        'total_integrated_deficit': float(sum(integrated)) if integrated else 0,
        'severity_counts': {
            'extreme': sum(1 for e in events if e.get('severity') == 'extreme'),
            'severe': sum(1 for e in events if e.get('severity') == 'severe'),
            'moderate': sum(1 for e in events if e.get('severity') == 'moderate'),
        },
    }

def process_catchment(cut_name: str) -> dict:
    """Process single catchment for drought events."""
    print(f"\n🏞️  Processing: {cut_name.upper()}")
    
    csv_path = RESULTS_DIR / cut_name / 'monthly_drought_indices.csv'
    
    if not csv_path.exists():
        print(f"❌ Not found: {csv_path}")
        return None
    
    # Load data
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    
    print(f"   ✅ Loaded {len(df)} monthly records ({df.index.min()} to {df.index.max()})")
    
    result = {
        'catchment': cut_name,
        'period': f"{df.index.min()} to {df.index.max()}",
        'n_months': len(df),
        'indices': {},
    }
    
    # Detect events for each index
    indices_to_analyze = [
        ('mdi_percent', 'MDI', 20),
        ('sm_percent', 'SMI', 20),
        ('recharge_percent', 'Recharge', 20),
        ('runoff_percent', 'Runoff', 20),
    ]
    
    for col, name, threshold in indices_to_analyze:
        if col not in df.columns:
            print(f"   ⚠️  {name} column not found: {col}")
            continue
        
        print(f"   📊 Detecting {name} events (threshold < {threshold})...")
        
        series = df[col].dropna()
        events = detect_events(series, threshold=threshold, min_duration=3)
        stats = compute_event_statistics(events, series)
        
        result['indices'][name] = {
            'threshold': threshold,
            'statistics': stats,
            'events': events,
        }
        
        print(f"   ✅ Found {stats['n_events']} events (total {stats['total_drought_months']} drought months)")
    
    # Identify compound events (MDI + SMI + Recharge + Runoff all in drought)
    print(f"   🔗 Identifying compound events...")
    compound_events = detect_compound_events(df, threshold=20, min_duration=3)
    result['compound_events'] = {
        'threshold': 20,
        'statistics': compute_event_statistics(compound_events, df['mdi_percent'], threshold=20),
        'events': compound_events,
    }
    print(f"   ✅ Found {len(compound_events)} compound drought events")
    
    # Identify major events (2018-2020)
    print(f"   🎯 Analyzing 2018-2020 event...")
    major_event = analyze_major_event(df, '2018-01-01', '2020-12-31')
    result['major_event_2018_2020'] = major_event
    
    return result

def detect_compound_events(df: pd.DataFrame, threshold: float = 20, min_duration: int = 3) -> list:
    """Detect compound drought events (all components below threshold)."""
    # Create compound drought indicator
    compound = (
        (df['sm_percent'] < threshold).astype(int) +
        (df['recharge_percent'] < threshold).astype(int) +
        (df['runoff_percent'] < threshold).astype(int)
    )
    
    # All three components must be in drought
    compound_drought = (compound == 3)
    
    events = []
    in_event = False
    event_start = None
    event_values = []
    
    for i, (date, val) in enumerate(compound_drought.items()):
        if val and not in_event:
            in_event = True
            event_start = i
            event_values = [df['mdi_percent'].iloc[i]]
        elif val and in_event:
            event_values.append(df['mdi_percent'].iloc[i])
        elif not val and in_event:
            in_event = False
            if len(event_values) >= min_duration:
                events.append({
                    'start_idx': event_start,
                    'end_idx': i - 1,
                    'start_date': str(compound_drought.index[event_start]),
                    'end_date': str(compound_drought.index[i - 1]),
                    'duration_months': len(event_values),
                    'severity': 'extreme' if all(v < 5 for v in event_values) else \
                              'severe' if all(v < 10 for v in event_values) else \
                              'moderate',
                    'min_mdi': float(min(event_values)),
                    'mean_mdi': float(np.mean(event_values)),
                    'max_mdi': float(max(event_values)),
                    'integrated_deficit': float(sum(20 - v for v in event_values)),
                })
            event_values = []
    
    return events

def analyze_major_event(df: pd.DataFrame, start_date: str, end_date: str) -> dict:
    """Analyze a specific major drought event."""
    mask = (df.index >= start_date) & (df.index <= end_date)
    event_df = df.loc[mask]
    
    if len(event_df) == 0:
        return None
    
    return {
        'period': f"{start_date} to {end_date}",
        'duration_months': len(event_df),
        'mdi': {
            'min': float(event_df['mdi_percent'].min()),
            'mean': float(event_df['mdi_percent'].mean()),
            'months_below_20': int((event_df['mdi_percent'] < 20).sum()),
            'months_below_10': int((event_df['mdi_percent'] < 10).sum()),
            'months_below_5': int((event_df['mdi_percent'] < 5).sum()),
        },
        'sm': {
            'min': float(event_df['sm_percent'].min()),
            'mean': float(event_df['sm_percent'].mean()),
            'months_below_20': int((event_df['sm_percent'] < 20).sum()),
        },
        'recharge': {
            'min': float(event_df['recharge_percent'].min()),
            'mean': float(event_df['recharge_percent'].mean()),
            'months_below_20': int((event_df['recharge_percent'] < 20).sum()),
        },
        'runoff': {
            'min': float(event_df['runoff_percent'].min()),
            'mean': float(event_df['runoff_percent'].mean()),
            'months_below_20': int((event_df['runoff_percent'] < 20).sum()),
        },
    }

# Process all catchments
print("🚀 Drought Event Detection Pipeline")
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
    print("✅ Drought Event Detection complete!")
    print(f"📁 Saved: {OUTPUT_FILE}")
    
    # Summary table
    print("\n📊 Event Summary by Catchment:")
    print(f"{'Catchment':<15} {'MDI Events':<12} {'SMI Events':<12} {'Compound':<12} {'2018-2020 MDI min':<15}")
    print("-"*80)
    for r in all_results:
        mdi_events = r['indices'].get('MDI', {}).get('statistics', {}).get('n_events', 0)
        smi_events = r['indices'].get('SMI', {}).get('statistics', {}).get('n_events', 0)
        compound_events = r['compound_events']['statistics']['n_events']
        major = r.get('major_event_2018_2020', {})
        mdi_min = major.get('mdi', {}).get('min', 'N/A')
        mdi_min_str = f"{mdi_min:.1f}" if isinstance(mdi_min, float) else str(mdi_min)
        print(f"{r['catchment']:<15} {mdi_events:<12} {smi_events:<12} {compound_events:<12} {mdi_min_str:<15}")
else:
    print("\n❌ No results computed")

print("="*60)
