#!/usr/bin/env python3
"""Advanced drought analysis: Lag correlations & Matrix Drought Index.

This script extends the basic drought pipeline with:
1. Lag-correlation analysis (Priority 1)
2. Matrix Drought Index heatmap (Priority 2)

Author: Helferchen
Date: 2026-03-02
"""

import argparse
from pathlib import Path
from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import netCDF4 as nc
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

# Modern styling
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['figure.titlesize'] = 14

REPO = Path(__file__).resolve().parents[2]

def load_data(mhm_output_dir: Path, fallback_normal_results_dir: Path | None = None) -> pd.DataFrame:
    """Load monthly mHM data."""
    mhm_nc = mhm_output_dir / "mHM_Fluxes_States.nc"
    q_nc = mhm_output_dir / "discharge.nc"
    if (not mhm_nc.exists() or not q_nc.exists()) and fallback_normal_results_dir is not None:
        cached = fallback_normal_results_dir / "monthly_drought_indices.csv"
        if cached.exists():
            df = pd.read_csv(cached, parse_dates=["date"])
            required = ["date", "precip", "sm", "recharge", "runoff", "pet"]
            for col in required:
                if col not in df.columns:
                    raise KeyError(f"Cached fallback is missing required column: {col}")
            if "qsim_monthly_mean" in df.columns:
                df["discharge"] = df["qsim_monthly_mean"]
            elif "discharge" not in df.columns:
                df["discharge"] = np.nan
            return df[["date", "precip", "sm", "recharge", "runoff", "pet", "discharge"]].sort_values("date")

    ds = nc.Dataset(mhm_nc)
    var_names = set(ds.variables.keys())
    
    time = nc.num2date(ds.variables["time"][:], 
                       units=ds.variables["time"].units)
    time = pd.to_datetime([t.isoformat() for t in time])
    
    # Helper for spatial mean
    def smean(var):
        arr = np.ma.filled(ds.variables[var][:], np.nan)
        return np.nanmean(arr, axis=(1, 2))
    
    def pick_var(candidates):
        for name in candidates:
            if name in var_names:
                return name
        return None

    precip_var = pick_var(["pre", "preEffect"])
    sm_var = pick_var(["SM_Lall", "SM_L01", "SWC_L01"])
    recharge_var = pick_var(["recharge", "L1_percol"])
    runoff_var = pick_var(["Q", "L1_total_runoff"])
    pet_var = pick_var(["PET", "pet", "L1_pet"])

    if precip_var is None or sm_var is None or recharge_var is None or runoff_var is None or pet_var is None:
        missing = {
            "precip": precip_var,
            "sm": sm_var,
            "recharge": recharge_var,
            "runoff": runoff_var,
            "pet": pet_var,
        }
        raise KeyError(f"Missing required variable mapping: {missing}")

    df = pd.DataFrame({
        'date': time,
        'precip': smean(precip_var),
        'sm': smean(sm_var),
        'recharge': smean(recharge_var),
        'runoff': smean(runoff_var),
        'pet': smean(pet_var),
    })
    
    ds.close()
    
    # Add discharge
    ds_q = nc.Dataset(q_nc)
    qsim_var = [n for n in ds_q.variables if n.startswith('Qsim_')][0]
    q_time = nc.num2date(ds_q.variables["time"][:],
                         units=ds_q.variables["time"].units)
    q_time = pd.to_datetime([t.isoformat() for t in q_time])
    qsim = np.array(ds_q.variables[qsim_var][:])
    ds_q.close()
    
    q_df = pd.DataFrame({'date': q_time, 'discharge': qsim})

    # Align all variables to monthly means at month-end timestamps.
    df_monthly = df.resample('ME', on='date').mean().reset_index()
    q_monthly = q_df.resample('ME', on='date').mean().reset_index()
    merged = df_monthly.merge(q_monthly, on='date', how='outer').sort_values('date')

    return merged

def calculate_lag_correlation(x: pd.Series, y: pd.Series, 
                             max_lag: int = 12) -> Tuple[np.ndarray, np.ndarray]:
    """Calculate cross-correlation with lags.
    
    Returns:
        lags: Array of lag values (in months)
        correlations: Correlation coefficients
    """
    lags = np.arange(-max_lag, max_lag + 1)
    correlations = np.zeros(len(lags))
    
    for i, lag in enumerate(lags):
        if lag < 0:
            # x leads y
            x_shifted = x.iloc[:lag].values if lag != 0 else x.values
            y_shifted = y.iloc[-lag:].values if lag != 0 else y.values
        elif lag > 0:
            # y leads x
            x_shifted = x.iloc[lag:].values
            y_shifted = y.iloc[:-lag].values
        else:
            x_shifted = x.values
            y_shifted = y.values
        
        # Remove NaN
        mask = ~(np.isnan(x_shifted) | np.isnan(y_shifted))
        if np.sum(mask) > 3:
            correlations[i] = np.corrcoef(x_shifted[mask], y_shifted[mask])[0, 1]
        else:
            correlations[i] = np.nan
    
    return lags, correlations

def plot_lag_correlation(df: pd.DataFrame, plot_dir: Path):
    """Create lag correlation analysis plot (Priority 1)."""
    print("Creating lag correlation analysis...")
    
    variables = {
        'Niederschlag': 'precip',
        'Bodenfeuchte': 'sm', 
        'Recharge': 'recharge',
        'Runoff': 'runoff',
        'Abfluss': 'discharge'
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    # Plot 1: Precip -> SM (most important)
    lags, corr = calculate_lag_correlation(df['precip'], df['sm'])
    axes[0].plot(lags, corr, 'b-', linewidth=2, marker='o')
    axes[0].axhline(0, color='gray', linestyle='-', alpha=0.3)
    axes[0].axhline(0.5, color='green', linestyle='--', alpha=0.5, label='r=0.5')
    axes[0].axhline(-0.5, color='red', linestyle='--', alpha=0.5, label='r=-0.5')
    axes[0].set_title('Lag-Korrelation: Niederschlag → Bodenfeuchte', fontweight='bold')
    axes[0].set_xlabel('Lag [Monate] (negativ = Niederschlag führt)')
    axes[0].set_ylabel('Korrelationskoeffizient r')
    axes[0].grid(alpha=0.3)
    axes[0].legend()
    
    # Find optimal lag
    valid_corr = corr[~np.isnan(corr)]
    valid_lags = lags[~np.isnan(corr)]
    if len(valid_corr) > 0:
        opt_idx = np.argmax(np.abs(valid_corr))
        opt_lag = valid_lags[opt_idx]
        axes[0].axvline(opt_lag, color='red', linestyle=':', alpha=0.7, 
                       label=f'Max bei {opt_lag} Monaten')
        print(f"  Optimal lag (precip→sm): {opt_lag} months (r={valid_corr[opt_idx]:.2f})")
    
    # Plot 2: SM -> Recharge
    lags, corr = calculate_lag_correlation(df['sm'], df['recharge'])
    axes[1].plot(lags, corr, 'g-', linewidth=2, marker='o')
    axes[1].axhline(0, color='gray', linestyle='-', alpha=0.3)
    axes[1].axhline(0.5, color='green', linestyle='--', alpha=0.5)
    axes[1].axhline(-0.5, color='red', linestyle='--', alpha=0.5)
    axes[1].set_title('Lag-Korrelation: Bodenfeuchte → Recharge', fontweight='bold')
    axes[1].set_xlabel('Lag [Monate]')
    axes[1].set_ylabel('Korrelationskoeffizient r')
    axes[1].grid(alpha=0.3)
    
    valid_corr = corr[~np.isnan(corr)]
    valid_lags = lags[~np.isnan(corr)]
    if len(valid_corr) > 0:
        opt_idx = np.argmax(np.abs(valid_corr))
        opt_lag = valid_lags[opt_idx]
        axes[1].axvline(opt_lag, color='red', linestyle=':', alpha=0.7,
                       label=f'Max bei {opt_lag} Monaten')
        print(f"  Optimal lag (sm→recharge): {opt_lag} months (r={valid_corr[opt_idx]:.2f})")
    
    # Plot 3: Recharge -> Discharge
    lags, corr = calculate_lag_correlation(df['recharge'], df['discharge'])
    axes[2].plot(lags, corr, 'r-', linewidth=2, marker='o')
    axes[2].axhline(0, color='gray', linestyle='-', alpha=0.3)
    axes[2].axhline(0.5, color='green', linestyle='--', alpha=0.5)
    axes[2].axhline(-0.5, color='red', linestyle='--', alpha=0.5)
    axes[2].set_title('Lag-Korrelation: Recharge → Abfluss', fontweight='bold')
    axes[2].set_xlabel('Lag [Monate]')
    axes[2].set_ylabel('Korrelationskoeffizient r')
    axes[2].grid(alpha=0.3)
    
    valid_corr = corr[~np.isnan(corr)]
    valid_lags = lags[~np.isnan(corr)]
    if len(valid_corr) > 0:
        opt_idx = np.argmax(np.abs(valid_corr))
        opt_lag = valid_lags[opt_idx]
        axes[2].axvline(opt_lag, color='red', linestyle=':', alpha=0.7,
                       label=f'Max bei {opt_lag} Monaten')
        print(f"  Optimal lag (recharge→discharge): {opt_lag} months (r={valid_corr[opt_idx]:.2f})")
    
    # Plot 4: Summary matrix (all vs all at lag 0)
    corr_matrix = np.zeros((len(variables), len(variables)))
    var_names = list(variables.keys())
    var_cols = list(variables.values())
    
    for i, col_i in enumerate(var_cols):
        for j, col_j in enumerate(var_cols):
            mask = ~(np.isnan(df[col_i]) | np.isnan(df[col_j]))
            if np.sum(mask) > 3:
                corr_matrix[i, j] = np.corrcoef(df[col_i][mask], df[col_j][mask])[0, 1]
    
    im = axes[3].imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    axes[3].set_xticks(range(len(var_names)))
    axes[3].set_yticks(range(len(var_names)))
    axes[3].set_xticklabels(var_names, rotation=45, ha='right')
    axes[3].set_yticklabels(var_names)
    axes[3].set_title('Korrelationsmatrix (Lag = 0)', fontweight='bold')
    
    # Add correlation values
    for i in range(len(var_names)):
        for j in range(len(var_names)):
            text = axes[3].text(j, i, f'{corr_matrix[i, j]:.2f}',
                            ha="center", va="center", color="black" if abs(corr_matrix[i, j]) < 0.5 else "white",
                            fontsize=8)
    
    plt.colorbar(im, ax=axes[3], shrink=0.8, label='Korrelationskoeffizient r')
    
    fig.tight_layout()
    plot_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_dir / '09_lag_correlation_analysis.png', dpi=200,
                bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: 09_lag_correlation_analysis.png")

def calculate_matrix_drought_index(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate combined Matrix Drought Index.
    
    Based on Research v2.0: SMI × Recharge × Discharge
    With time lags: SMI(t), Recharge(t-1), Discharge(t-2)
    """
    # Calculate percentiles
    for col in ['sm', 'recharge', 'discharge']:
        if col in df.columns:
            df[f'{col}_pct'] = df[col].rank(pct=True) * 100
    
    # Normalize to [0, 1]
    df['sm_norm'] = df['sm_pct'] / 100
    df['recharge_norm'] = df['recharge_pct'].shift(1) / 100  # 1-month lag
    df['discharge_norm'] = df['discharge_pct'].shift(2) / 100  # 2-month lag
    
    # Weights (from Research v2.0)
    w_sm = 0.4
    w_recharge = 0.3
    w_discharge = 0.3
    
    # Matrix Drought Index (0 = severe drought, 1 = wet)
    df['matrix_drought_index'] = (
        w_sm * df['sm_norm'] + 
        w_recharge * df['recharge_norm'] + 
        w_discharge * df['discharge_norm']
    )
    
    # Classification
    def classify(mdi):
        if pd.isna(mdi):
            return 'unknown'
        elif mdi < 0.2:
            return 'extreme_drought'
        elif mdi < 0.4:
            return 'severe_drought'
        elif mdi < 0.6:
            return 'moderate_drought'
        elif mdi < 0.8:
            return 'mild_drought'
        else:
            return 'normal_or_wet'
    
    df['matrix_class'] = df['matrix_drought_index'].apply(classify)
    
    return df

def plot_matrix_drought_index(df: pd.DataFrame, plot_dir: Path, results_dir: Path):
    """Create Matrix Drought Index heatmap (Priority 2)."""
    print("Creating Matrix Drought Index analysis...")
    
    df = calculate_matrix_drought_index(df)
    
    # Create discrete colormap
    colors = ["#8B0000", "#FF4500", "#FFA500", "#FFD700", "#90EE90"]
    cmap = mcolors.ListedColormap(colors)
    bounds = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Prepare data for heatmap
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Plot 1: Matrix Index Heatmap
    pivot = df.pivot(index='year', columns='month', values='matrix_drought_index')
    im1 = axes[0].imshow(pivot.values, aspect='auto', cmap=cmap, norm=norm)
    axes[0].set_title('Matrix Dürre-Index: Kombination SMI × Recharge × Abfluss', 
                     fontweight='bold', pad=20)
    axes[0].set_ylabel('Jahr', fontweight='bold')
    axes[0].set_yticks(range(len(pivot.index)))
    axes[0].set_yticklabels(pivot.index)
    axes[0].set_xticks(range(12))
    axes[0].set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'])
    
    cbar1 = plt.colorbar(im1, ax=axes[0], boundaries=bounds, 
                        ticks=[0.1, 0.3, 0.5, 0.7, 0.9])
    cbar1.ax.set_yticklabels(['Extrem', 'Schwer', 'Mäßig', 'Mild', 'Normal'])
    cbar1.set_label('Dürre-Klasse', fontweight='bold')
    
    # Plot 2: Component breakdown
    axes[1].fill_between(df['date'], 0, df['sm_norm'], alpha=0.3, label='SMI (40%)', color='blue')
    axes[1].fill_between(df['date'], 0, df['recharge_norm'], alpha=0.3, label='Recharge (30%, lag-1)', color='green')
    axes[1].fill_between(df['date'], 0, df['discharge_norm'], alpha=0.3, label='Discharge (30%, lag-2)', color='red')
    axes[1].plot(df['date'], df['matrix_drought_index'], 'k-', linewidth=2, label='Matrix Index')
    axes[1].axhline(0.2, color='darkred', linestyle='--', alpha=0.7, label='Extreme Drought')
    axes[1].axhline(0.4, color='red', linestyle='--', alpha=0.5, label='Severe Drought')
    axes[1].set_title('Matrix-Index Komponenten', fontweight='bold')
    axes[1].set_ylabel('Normalisierter Index [0-1]')
    axes[1].legend(loc='upper right')
    axes[1].grid(alpha=0.3)
    
    # Plot 3: Class frequency by year
    class_counts = df.groupby('year')['matrix_class'].value_counts().unstack(fill_value=0)
    class_order = ['extreme_drought', 'severe_drought', 'moderate_drought', 'mild_drought', 'normal_or_wet']
    colors_map = {'extreme_drought': '#8B0000', 'severe_drought': '#FF4500', 
                  'moderate_drought': '#FFA500', 'mild_drought': '#FFD700', 
                  'normal_or_wet': '#90EE90'}
    
    bottom = np.zeros(len(class_counts))
    for cls in class_order:
        if cls in class_counts.columns:
            axes[2].bar(class_counts.index, class_counts[cls], bottom=bottom, 
                       label=cls.replace('_', ' ').title(),
                       color=colors_map.get(cls, 'gray'))
            bottom += class_counts[cls]
    
    axes[2].set_title('Jährliche Häufigkeit von Dürre-Klassen', fontweight='bold')
    axes[2].set_xlabel('Jahr', fontweight='bold')
    axes[2].set_ylabel('Anzahl Monate')
    axes[2].legend(loc='upper left', bbox_to_anchor=(1.02, 1))
    axes[2].grid(alpha=0.3, axis='y')
    
    fig.tight_layout()
    plot_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_dir / '10_matrix_drought_index.png', dpi=200,
                bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: 10_matrix_drought_index.png")
    
    # Save results
    results_dir.mkdir(parents=True, exist_ok=True)
    df[['date', 'matrix_drought_index', 'matrix_class', 
        'sm_norm', 'recharge_norm', 'discharge_norm']].to_csv(
        results_dir / 'matrix_drought_index.csv', index=False)
    print(f"  Saved: matrix_drought_index.csv")

def main():
    """Run advanced drought analysis."""
    parser = argparse.ArgumentParser(description="Advanced drought analysis")
    parser.add_argument(
        "--domain",
        choices=["test_domain", "catchment_custom"],
        default=None,
        help="Convenience domain selector",
    )
    parser.add_argument(
        "--mhm-output-dir",
        default=str(REPO / "code" / "mhm" / "test_domain" / "output_b1"),
        help="Path to mHM output directory containing mHM_Fluxes_States.nc and discharge.nc",
    )
    parser.add_argument(
        "--analysis-subdir",
        default="test_domain",
        help="Subdirectory name under analysis/advanced for separated outputs",
    )
    args = parser.parse_args()

    # Domain shortcut overrides defaults when selected.
    if args.domain == "test_domain":
        args.mhm_output_dir = str(REPO / "code" / "mhm" / "test_domain" / "output_b1")
        args.analysis_subdir = "test_domain"
    elif args.domain == "catchment_custom":
        args.mhm_output_dir = str(REPO / "code" / "mhm" / "catchment_custom" / "output_90410700")
        args.analysis_subdir = "custom_catchment"

    mhm_output_dir = Path(args.mhm_output_dir)
    plot_dir = REPO / "analysis" / "plots" / args.analysis_subdir / "advanced"
    results_dir = REPO / "analysis" / "results" / args.analysis_subdir / "advanced"

    print("=" * 60)
    print("ADVANCED DROUGHT ANALYSIS")
    print("=" * 60)
    
    # Load data
    print("\nLoading data...")
    fallback_normal_results_dir = REPO / "analysis" / "results" / args.analysis_subdir / "normal"
    df = load_data(mhm_output_dir, fallback_normal_results_dir)
    print(f"  Loaded {len(df)} records")
    
    # Priority 1: Lag correlation
    print("\n" + "-" * 40)
    print("PRIORITY 1: Lag Correlation Analysis")
    print("-" * 40)
    plot_lag_correlation(df, plot_dir)
    
    # Priority 2: Matrix Drought Index
    print("\n" + "-" * 40)
    print("PRIORITY 2: Matrix Drought Index")
    print("-" * 40)
    plot_matrix_drought_index(df, plot_dir, results_dir)
    
    print("\n" + "=" * 60)
    print("Advanced analysis complete!")
    print("=" * 60)
    print(f"Plots: {plot_dir}")
    print(f"Results: {results_dir}")

if __name__ == "__main__":
    main()
