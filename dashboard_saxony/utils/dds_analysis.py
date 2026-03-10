"""
Scientific DDS Calibration Analysis for mHM Re-Crit (Multiple Catchments)

Analyzes DDS (Dynamically Dimensioned Search) optimization results:
- Single catchment: Convergence, parameter evolution, parallel coordinates
- Multi-calcation: Comparison between catchments
- Scientific explanations of calibration process
- Parameter sensitivity analysis

Based on:
- dds_results.out: DDS optimization log (200 iterations, 54 parameters)
- FinalParam.nml: Best parameter set (mhm_parameter.nml format)
- FinalParam.out: Model performance with optimized parameters

Author: Helferchen (Research Assistant)
Date: 2026-03-10
"""

from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from pathlib import Path


# =============================================================================
# PARAMETER MAPPING (DDS index → mHM parameter name)
# =============================================================================

DDS_PARAM_MAP = {
    1: ('canopyInterceptionFactor', 'Interception', 'Kronen-Interzeption [-]'),
    2: ('snowTreshholdTemperature', 'Snow', 'Schnee-Regen-Temperatur [°C]'),
    3: ('degreeDayFactor_forest', 'Snow', 'Degree-Day-Faktor Wald [mm/°C/d]'),
    4: ('degreeDayFactor_impervious', 'Snow', 'Degree-Day-Faktor versiegelt [mm/°C/d]'),
    5: ('degreeDayFactor_pervious', 'Snow', 'Degree-Day-Faktor unversiegelt [mm/°C/d]'),
    6: ('increaseDegreeDayFactorByPrecip', 'Snow', 'Niederschlags-Korrektur [-]'),
    7: ('maxDegreeDayFactor_forest', 'Snow', 'Max. DD-Faktor Wald [mm/°C/d]'),
    8: ('maxDegreeDayFactor_impervious', 'Snow', 'Max. DD-Faktor versiegelt [mm/°C/d]'),
    9: ('maxDegreeDayFactor_pervious', 'Snow', 'Max. DD-Faktor unversiegelt [mm/°C/d]'),
    10: ('orgMatterContent_forest', 'Soil', 'Organische Substanz Wald [%]'),
    11: ('orgMatterContent_impervious', 'Soil', 'Organische Substanz versiegelt [%]'),
    12: ('orgMatterContent_pervious', 'Soil', 'Organische Substanz unversiegelt [%]'),
    13: ('PTF_lower66_5_constant', 'Soil', 'PTF Konstante (untere Hälfte) [-]'),
    14: ('PTF_lower66_5_clay', 'Soil', 'PTF Ton-Anteil (untere Hälfte) [-]'),
    15: ('PTF_lower66_5_Db', 'Soil', 'PTF Bulk-Density (untere Hälfte) [-]'),
    16: ('PTF_higher66_5_constant', 'Soil', 'PTF Konstante (obere Hälfte) [-]'),
    17: ('PTF_higher66_5_clay', 'Soil', 'PTF Ton-Anteil (obere Hälfte) [-]'),
    18: ('PTF_higher66_5_Db', 'Soil', 'PTF Bulk-Density (obere Hälfte) [-]'),
    19: ('PTF_Ks_constant', 'Soil', 'PTF Ks Konstante [-]'),
    20: ('PTF_Ks_sand', 'Soil', 'PTF Ks Sand-Anteil [-]'),
    21: ('PTF_Ks_clay', 'Soil', 'PTF Ks Ton-Anteil [-]'),
    22: ('PTF_Ks_curveSlope', 'Soil', 'PTF Ks Kurven-Steigung [-]'),
    23: ('rootFractionCoefficient_forest', 'Soil', 'Wurzel-Fraktion Wald [-]'),
    24: ('rootFractionCoefficient_impervious', 'Soil', 'Wurzel-Fraktion versiegelt [-]'),
    25: ('rootFractionCoefficient_pervious', 'Soil', 'Wurzel-Fraktion unversiegelt [-]'),
    26: ('infiltrationShapeFactor', 'Soil', 'Infiltrations-Formfaktor [-]'),
    27: ('imperviousStorageCapacity', 'Direct Runoff', 'Speicherkapazität versiegelt [mm]'),
    28: ('minCorrectionFactorPET', 'PET', 'Min. PET-Korrektur [-]'),
    29: ('maxCorrectionFactorPET', 'PET', 'Max. PET-Korrektur [-]'),
    30: ('aspectTresholdPET', 'PET', 'Expositions-Schwelle PET [°]'),
    31: ('interflowStorageCapacityFactor', 'Interflow', 'Speicherkapazität Interflow [-]'),
    32: ('interflowRecession_slope', 'Interflow', 'Interflow-Rezession Hang [-]'),
    33: ('fastInterflowRecession_forest', 'Interflow', 'Schneller Interflow Wald [-]'),
    34: ('slowInterflowRecession_Ks', 'Interflow', 'Langsamer Interflow Ks [-]'),
    35: ('exponentSlowInterflow', 'Interflow', 'Exponent langsamer Interflow [-]'),
    36: ('rechargeCoefficient', 'Percolation', 'Grundwasserneubildungs-Koeffizient [-]'),
    37: ('rechargeFactor_karstic', 'Percolation', 'Karst-Grundwasserneubildung [-]'),
    38: ('gain_loss_GWreservoir_karstic', 'Percolation', 'GW-Verlust/ Gewinn karstig [-]'),
    39: ('slope_factor', 'Routing', 'Hangneigungs-Faktor [-]'),
    40: ('GeoParam_1', 'Geology', 'Geologie-Parameter 1 [-]'),
    41: ('GeoParam_2', 'Geology', 'Geologie-Parameter 2 [-]'),
    42: ('GeoParam_3', 'Geology', 'Geologie-Parameter 3 [-]'),
    43: ('GeoParam_4', 'Geology', 'Geologie-Parameter 4 [-]'),
    44: ('GeoParam_5', 'Geology', 'Geologie-Parameter 5 [-]'),
    45: ('GeoParam_6', 'Geology', 'Geologie-Parameter 6 [-]'),
    46: ('GeoParam_7', 'Geology', 'Geologie-Parameter 7 [-]'),
    47: ('GeoParam_8', 'Geology', 'Geologie-Parameter 8 [-]'),
    48: ('GeoParam_9', 'Geology', 'Geologie-Parameter 9 [-]'),
    49: ('GeoParam_10', 'Geology', 'Geologie-Parameter 10 [-]'),
    50: ('GeoParam_11', 'Geology', 'Geologie-Parameter 11 [-]'),
    51: ('GeoParam_12', 'Geology', 'Geologie-Parameter 12 [-]'),
    52: ('GeoParam_13', 'Geology', 'Geologie-Parameter 13 [-]'),
    53: ('GeoParam_14', 'Geology', 'Geologie-Parameter 14 [-]'),
    54: ('GeoParam_15', 'Geology', 'Geologie-Parameter 15 [-]'),
}

PARAM_GROUPS = {
    'Snow (1-9)': list(range(1, 10)),
    'Soil (10-26)': list(range(10, 27)),
    'Direct Runoff (27)': [27],
    'PET (28-30)': list(range(28, 31)),
    'Interflow (31-35)': list(range(31, 36)),
    'Percolation (36-38)': list(range(36, 39)),
    'Routing (39)': [39],
    'Geology (40-54)': list(range(40, 55)),
}


# =============================================================================
# DDS RESULTS PARSING
# =============================================================================

def parse_dds_results(filepath: str, catchment_name: str = None) -> Dict:
    """Parse dds_results.out file."""
    rows = []
    
    with open(filepath, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    data_lines = [l for l in lines if not l.strip().startswith('#')]
    
    for line in data_lines:
        parts = line.split()
        if len(parts) < 3:
            continue
        
        iteration = int(parts[0])
        objective = float(parts[1])
        params = [float(p) for p in parts[2:]]
        
        row = {'iteration': iteration, 'objective': objective}
        for i, p in enumerate(params):
            row[f'param_{i+1:02d}'] = p
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    return {
        'name': catchment_name or Path(filepath).parent.name,
        'df': df,
        'path': filepath,
        'iterations': len(df),
        'n_params': len(df.columns) - 2
    }


def parse_final_param_nml(filepath: str) -> Dict[str, float]:
    """Parse FinalParam.nml with proper mHM parameter names."""
    params = {}
    
    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # Pattern for named parameters: parameter_name = value
    pattern = r'(\w+)\s*=\s*([\d.E+-]+)'
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        try:
            params[name] = float(value)
        except ValueError:
            pass
    
    return params


def parse_dds_to_named_params(dds_df: pd.DataFrame) -> pd.DataFrame:
    """Convert param_01, param_02, ... to named parameters."""
    named_df = dds_df[['iteration', 'objective']].copy()
    
    for idx, (param_name, group, unit) in DDS_PARAM_MAP.items():
        col = f'param_{idx:02d}'
        if col in dds_df.columns:
            named_df[param_name] = dds_df[col]
    
    return named_df


def parse_final_param_out(filepath: str) -> Dict[str, float]:
    """
    Parse FinalParam.out OR calculate metrics from daily_discharge.out.
    
    FinalParam.out (old format): Only contains optimized parameters (no metrics)
    daily_discharge.out: Contains Qobs and Qsim for metric calculation
    
    Returns dict with KGE, NSE, r, PBIAS if available.
    """
    from pathlib import Path
    
    # Try to read daily_discharge.out for metric calculation
    discharge_path = Path(filepath).parent / 'daily_discharge.out'
    
    if discharge_path.exists():
        try:
            return calculate_metrics_from_discharge(discharge_path)
        except Exception:
            pass
    
    # Fallback: Try to parse old format (key = value)
    metrics = {}
    
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            lines = f.readlines()
        
        for line in lines:
            if '=' in line and not line.strip().startswith('!'):
                parts = line.split('=')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    try:
                        metrics[key] = float(value)
                    except ValueError:
                        pass
    except Exception:
        pass
    
    return metrics


def calculate_metrics_from_discharge(filepath: str) -> Dict[str, float]:
    """
    Calculate KGE, NSE, r, PBIAS from daily_discharge.out.
    
    Expected format: Date Qobs Qsim (or similar)
    """
    import numpy as np
    from scipy import stats
    
    qobs = []
    qsim = []
    
    with open(filepath, 'r', encoding='latin-1') as f:
        for line in f:
            if line.strip().startswith('!') or not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                try:
                    # Skip date column, take Qobs and Qsim
                    qobs.append(float(parts[1]))
                    qsim.append(float(parts[2]))
                except (ValueError, IndexError):
                    pass
    
    if len(qobs) < 10 or len(qsim) < 10:
        return {}
    
    qobs = np.array(qobs)
    qsim = np.array(qsim)
    
    # Remove NaN
    valid = ~(np.isnan(qobs) | np.isnan(qsim))
    qobs = qobs[valid]
    qsim = qsim[valid]
    
    if len(qobs) < 10:
        return {}
    
    # Calculate metrics
    # Pearson correlation
    r = np.corrcoef(qobs, qsim)[0, 1]
    
    # NSE (Nash-Sutcliffe Efficiency)
    nse = 1 - (np.sum((qsim - qobs)**2) / np.sum((qobs - np.mean(qobs))**2))
    
    # PBIAS (Percent Bias)
    pbias = 100 * (np.sum(qsim - qobs) / np.sum(qobs))
    
    # KGE (Kling-Gupta Efficiency)
    mu_obs = np.mean(qobs)
    mu_sim = np.mean(qsim)
    std_obs = np.std(qobs, ddof=1)
    std_sim = np.std(qsim, ddof=1)
    
    # Avoid division by zero
    if std_obs == 0 or mu_obs == 0:
        kge = 0.0
    else:
        cc = r  # Correlation
        cv = std_sim / std_obs  # Variability ratio
        beta = mu_sim / mu_obs  # Bias ratio
        kge = 1 - np.sqrt((cc - 1)**2 + (cv - 1)**2 + (beta - 1)**2)
    
    return {
        'KGE': float(kge),
        'NSE': float(nse),
        'r': float(r),
        'PBIAS': float(pbias)
    }


# =============================================================================
# SENSITIVITY ANALYSIS
# =============================================================================

def calculate_parameter_sensitivity(dds_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate parameter sensitivity based on DDS results.
    
    Method: Correlation between parameter values and objective function
    Higher absolute correlation = more sensitive parameter
    """
    sensitivities = []
    
    for idx in range(1, 55):
        col = f'param_{idx:02d}'
        if col in dds_df.columns:
            # Correlation with objective
            corr = dds_df[col].corr(dds_df['objective'])
            if np.isnan(corr):
                corr = 0.0
            
            # Range of parameter values
            param_range = dds_df[col].max() - dds_df[col].min()
            if np.isnan(param_range):
                param_range = 0.0
            
            # Standard deviation
            param_std = dds_df[col].std()
            if np.isnan(param_std):
                param_std = 0.0
            
            # Sensitivity score: |correlation| * range
            sensitivity_score = abs(corr) * param_range
            
            param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
            
            sensitivities.append({
                'index': idx,
                'name': param_name,
                'group': group,
                'unit': unit,
                'correlation': float(corr),
                'range': float(param_range),
                'std': float(param_std),
                'sensitivity_score': float(sensitivity_score)
            })
    
    df = pd.DataFrame(sensitivities)
    if len(df) > 0:
        return df.sort_values('sensitivity_score', ascending=False)
    return df


def create_sensitivity_ranking_plot(sensitivity_df: pd.DataFrame, top_n: int = 15) -> Optional[go.Figure]:
    """Create bar plot of top N most sensitive parameters."""
    if sensitivity_df is None or len(sensitivity_df) == 0:
        return None
    
    top_params = sensitivity_df.head(min(top_n, len(sensitivity_df)))
    
    if len(top_params) == 0:
        return None
    
    # Color by group
    colors = {
        'Snow': '#1f77b4',
        'Soil': '#ff7f0e',
        'Direct Runoff': '#2ca02c',
        'PET': '#d62728',
        'Interflow': '#9467bd',
        'Percolation': '#8c564b',
        'Routing': '#e377c2',
        'Geology': '#7f7f7f',
        'Unknown': '#bcbd22'
    }
    
    bar_colors = [colors.get(g, '#bcbd22') for g in top_params['group']]
    
    y_labels = [f"P{int(idx):02d}: {str(name)[:25]}" for idx, name in zip(top_params['index'], top_params['name'])]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=top_params['sensitivity_score'].tolist(),
        y=y_labels,
        orientation='h',
        marker_color=bar_colors,
        hovertemplate='<b>%{y}</b><br>Sensitivity: %{x:.4f}<extra></extra>',
    ))
    
    fig.update_layout(
        title="🎯 Top 15 sensitivste Parameter (Einfluss auf Zielfunktion)",
        xaxis_title="Sensitivity Score (|Korrelation| × Range)",
        yaxis_title="Parameter",
        height=500,
        showlegend=False,
        template="plotly_dark",
        margin=dict(l=250, r=40, t=60, b=40),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=10)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_group_sensitivity_plot(sensitivity_df: pd.DataFrame) -> Optional[go.Figure]:
    """Aggregate sensitivity by parameter group."""
    if sensitivity_df is None or len(sensitivity_df) == 0:
        return None
    
    try:
        group_stats = sensitivity_df.groupby('group').agg({
            'sensitivity_score': ['sum', 'mean', 'max']
        }).round(4)
        
        if len(group_stats) == 0:
            return None
        
        group_stats.columns = ['total_sensitivity', 'avg_sensitivity', 'max_sensitivity']
        group_stats = group_stats.sort_values('total_sensitivity', ascending=False)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=group_stats['total_sensitivity'].tolist(),
            y=group_stats.index.tolist(),
            orientation='h',
            marker_color='#1f77b4',
            hovertemplate='<b>%{y}</b><br>Total: %{x:.4f}<extra></extra>',
        ))
        
        fig.update_layout(
            title="📊 Sensitivität nach Parameter-Gruppe",
            xaxis_title="Total Sensitivity Score",
            yaxis_title="Parameter-Gruppe",
            height=400,
            showlegend=False,
            template="plotly_dark",
            margin=dict(l=150, r=40, t=60, b=40),
            plot_bgcolor="rgba(30, 30, 30, 1)",
            paper_bgcolor="rgba(30, 30, 30, 1)",
            font=dict(color="#ffffff", size=11)
        )
        
        return fig
    except Exception:
        return None


def create_sensitivity_comparison_plot(sensitivity_results: Dict[str, pd.DataFrame], top_n: int = 10) -> Optional[go.Figure]:
    """
    Compare top N sensitive parameters across multiple catchments.
    
    Args:
        sensitivity_results: Dict mapping catchment name -> sensitivity DataFrame
        top_n: Number of top parameters to show per catchment
    """
    if not sensitivity_results:
        return None
    
    # Get top N params from each catchment
    all_top_params = set()
    for name, df in sensitivity_results.items():
        if df is not None and len(df) > 0:
            top = df.head(top_n)
            for idx in top['index']:
                all_top_params.add(idx)
    
    if not all_top_params:
        return None
    
    # Build comparison data
    rows = []
    for idx in sorted(all_top_params):
        param_name, group, _ = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
        row = {'Param': f'P{idx:02d}', 'Name': param_name, 'Group': group}
        
        for catchment_name, sens_df in sensitivity_results.items():
            if sens_df is not None and len(sens_df) > 0:
                match = sens_df[sens_df['index'] == idx]
                if len(match) > 0:
                    row[f'{catchment_name}_score'] = float(match['sensitivity_score'].iloc[0])
                else:
                    row[f'{catchment_name}_score'] = 0.0
            else:
                row[f'{catchment_name}_score'] = 0.0
        
        rows.append(row)
    
    if not rows:
        return None
    
    comp_df = pd.DataFrame(rows)
    
    # Create grouped bar chart
    fig = go.Figure()
    
    catchment_names = list(sensitivity_results.keys())
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, catchment_name in enumerate(catchment_names):
        score_col = f'{catchment_name}_score'
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Bar(
            name=catchment_name,
            x=[f"P{int(p['Param'][1:]):02d}" for _, p in comp_df.iterrows()],
            y=comp_df[score_col].tolist(),
            marker_color=color,
            hovertemplate='<b>%{x}</b><br>Sensitivity: %{y:.4f}<extra></extra>'
        ))
    
    fig.update_layout(
        title="🎯 Sensitivitäts-Vergleich: Top Parameter über Catchments",
        xaxis_title="Parameter",
        yaxis_title="Sensitivity Score",
        barmode='group',
        height=500,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=80),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=10),
        legend=dict(orientation="h", y=1.02, x=0)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_parameter_statistics_table(results: List[Dict]) -> go.Figure:
    """
    Create statistical summary table for all catchments.
    
    Shows: Mean, Std, CV (Coefficient of Variation), Min, Max for each parameter.
    """
    if not results or len(results) < 2:
        return None
    
    # Get final parameters from each catchment
    all_params = {}
    for r in results:
        df = r['df']
        final_params = df.iloc[-1]  # Last iteration
        all_params[r['name']] = final_params
    
    # Calculate statistics for top 20 parameters
    rows = []
    for idx in range(1, 21):
        col = f'param_{idx:02d}'
        param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
        
        values = [all_params[c][col] for c in all_params.keys() if col in all_params[c]]
        
        if len(values) >= 2:
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / mean_val if mean_val != 0 else 0
            min_val = np.min(values)
            max_val = np.max(values)
            
            consistency = "✓ Konsistent" if cv < 0.1 else ("○ Moderat" if cv < 0.3 else "✗ Variabel")
            
            rows.append({
                'Param': f'P{idx:02d}',
                'Name': param_name[:30],
                'Gruppe': group,
                'Mean': f"{mean_val:.4f}",
                'Std': f"{std_val:.4f}",
                'CV': f"{cv:.3f}",
                'Min': f"{min_val:.4f}",
                'Max': f"{max_val:.4f}",
                'Konsistenz': consistency
            })
    
    if not rows:
        return None
    
    stats_df = pd.DataFrame(rows)
    
    fig = go.Figure(data=go.Table(
        header=dict(
            values=['Param', 'Name', 'Gruppe', 'Mean', 'Std', 'CV', 'Min', 'Max', 'Konsistenz'],
            fill_color="#1f77b4",
            align="left",
            font=dict(color="white", size=9)
        ),
        cells=dict(
            values=[
                stats_df['Param'],
                stats_df['Name'],
                stats_df['Gruppe'],
                stats_df['Mean'],
                stats_df['Std'],
                stats_df['CV'],
                stats_df['Min'],
                stats_df['Max'],
                stats_df['Konsistenz']
            ],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="left",
            font=dict(size=8, color="#ffffff")
        )
    ))
    
    fig.update_layout(
        title="📊 Parameter-Statistik über 6 Catchments (Mean, Std, CV)",
        height=600,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


def create_parameter_recommendation_table(results: List[Dict], cv_threshold: float = 0.1) -> go.Figure:
    """
    Create parameter recommendation table based on CV analysis.
    
    Classifies parameters as:
    - GLOBAL: CV < threshold (consistent across catchments)
    - LOCAL: CV >= threshold (catchment-specific)
    
    Args:
        results: List of DDS result dicts
        cv_threshold: CV threshold for GLOBAL classification (default 0.1)
    """
    if not results or len(results) < 2:
        return None
    
    # Get final parameters from each catchment
    all_params = {}
    for r in results:
        df = r['df']
        final_params = df.iloc[-1]  # Last iteration
        all_params[r['name']] = final_params
    
    # Calculate statistics for all 54 parameters
    rows = []
    for idx in range(1, 55):
        col = f'param_{idx:02d}'
        param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
        
        values = [all_params[c][col] for c in all_params.keys() if col in all_params[c]]
        
        if len(values) >= 2:
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / mean_val if mean_val != 0 else 0
            
            if cv < cv_threshold:
                recommendation = "GLOBAL"
                reason = f"Konsistent (CV={cv:.3f})"
                color = "#2ca02c"  # Green
            elif cv < 0.3:
                recommendation = "GLOBAL ±σ"
                reason = f"Moderat (CV={cv:.3f})"
                color = "#ff7f0e"  # Orange
            else:
                recommendation = "LOKAL"
                reason = f"Variabel (CV={cv:.3f})"
                color = "#d62728"  # Red
            
            rows.append({
                'Param': f'P{idx:02d}',
                'Name': param_name[:25],
                'Gruppe': group,
                'Wert': f"{mean_val:.4f}" if recommendation != "LOKAL" else "-",
                'Unsicherheit': f"±{std_val:.4f}",
                'CV': f"{cv:.3f}",
                'Empfehlung': recommendation,
                'Begruendung': reason,
                'Color': color
            })
    
    if not rows:
        return None
    
    rec_df = pd.DataFrame(rows)
    
    # Color-code recommendation column
    rec_colors = rec_df['Color'].tolist()
    
    fig = go.Figure(data=go.Table(
        header=dict(
            values=['Param', 'Name', 'Gruppe', 'Wert', '±σ', 'CV', 'Empfehlung', 'Begruendung'],
            fill_color="#1f77b4",
            align="left",
            font=dict(color="white", size=9)
        ),
        cells=dict(
            values=[
                rec_df['Param'],
                rec_df['Name'],
                rec_df['Gruppe'],
                rec_df['Wert'],
                rec_df['Unsicherheit'],
                rec_df['CV'],
                go.Table(cells=dict(
                    values=[[r] for r in rec_df['Empfehlung']],
                    fill_color=[[c] for c in rec_colors],
                    align="left",
                    font=dict(size=8, color="#ffffff")
                ))[0],
                rec_df['Begruendung']
            ],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="left",
            font=dict(size=8, color="#ffffff")
        )
    ))
    
    fig.update_layout(
        title="🎯 Empfohlene Parameter-Sets: GLOBAL vs. LOKAL",
        height=800,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


def export_parameter_recommendations(results: List[Dict], output_path: str, cv_threshold: float = 0.1):
    """
    Export parameter recommendations to CSV for mHM use.
    
    Creates a CSV file with recommended parameter values.
    """
    if not results or len(results) < 2:
        return None
    
    # Get final parameters from each catchment
    all_params = {}
    for r in results:
        df = r['df']
        final_params = df.iloc[-1]
        all_params[r['name']] = final_params
    
    rows = []
    for idx in range(1, 55):
        col = f'param_{idx:02d}'
        param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
        
        values = [all_params[c][col] for c in all_params.keys() if col in all_params[c]]
        
        if len(values) >= 2:
            mean_val = np.mean(values)
            std_val = np.std(values)
            cv = std_val / mean_val if mean_val != 0 else 0
            
            if cv < cv_threshold:
                recommendation = "GLOBAL"
                final_value = mean_val
            elif cv < 0.3:
                recommendation = "GLOBAL_WITH_UNCERTAINTY"
                final_value = mean_val
            else:
                recommendation = "CATCHMENT_SPECIFIC"
                final_value = np.nan  # User must specify per catchment
            
            rows.append({
                'param_id': idx,
                'param_name': param_name,
                'group': group,
                'unit': unit,
                'recommended_value': final_value,
                'uncertainty_1sigma': std_val,
                'cv': cv,
                'recommendation': recommendation,
                'note': reason if (reason := f"CV={cv:.3f}") else ""
            })
    
    if not rows:
        return None
    
    rec_df = pd.DataFrame(rows)
    rec_df.to_csv(output_path, index=False)
    
    return output_path


def create_performance_summary_table(results: List[Dict]) -> go.Figure:
    """
    Create performance summary table with KGE, NSE, r, PBIAS for all catchments.
    """
    if not results:
        return None
    
    rows = []
    for r in results:
        out_path = Path(r['path']).parent / 'FinalParam.out'
        metrics = parse_final_param_out(out_path) if out_path.exists() else {}
        
        # Calculate improvement
        df = r['df']
        improvement = ((df['objective'].iloc[0] - df['objective'].iloc[-1]) / df['objective'].iloc[0] * 100)
        
        rows.append({
            'Catchment': r['name'],
            'Iterationen': r['iterations'],
            'Start': f"{df['objective'].iloc[0]:.4f}",
            'Ende': f"{df['objective'].iloc[-1]:.4f}",
            'Verbesserung': f"{improvement:.1f}%",
            'KGE': f"{metrics.get('KGE', float('nan')):.4f}" if not np.isnan(metrics.get('KGE', float('nan'))) else "N/A",
            'NSE': f"{metrics.get('NSE', float('nan')):.4f}" if not np.isnan(metrics.get('NSE', float('nan'))) else "N/A",
            'r': f"{metrics.get('r', float('nan')):.4f}" if not np.isnan(metrics.get('r', float('nan'))) else "N/A",
            'PBIAS': f"{metrics.get('PBIAS', float('nan')):.2f}%" if not np.isnan(metrics.get('PBIAS', float('nan'))) else "N/A"
        })
    
    if not rows:
        return None
    
    perf_df = pd.DataFrame(rows)
    
    fig = go.Figure(data=go.Table(
        header=dict(
            values=['Catchment', 'Iter', 'Start', 'Ende', 'Δ%', 'KGE', 'NSE', 'r', 'PBIAS'],
            fill_color="#1f77b4",
            align="center",
            font=dict(color="white", size=9)
        ),
        cells=dict(
            values=[
                perf_df['Catchment'],
                perf_df['Iterationen'],
                perf_df['Start'],
                perf_df['Ende'],
                perf_df['Verbesserung'],
                perf_df['KGE'],
                perf_df['NSE'],
                perf_df['r'],
                perf_df['PBIAS']
            ],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="center",
            font=dict(size=8, color="#ffffff")
        )
    ))
    
    fig.update_layout(
        title="📊 Performance-Übersicht: Alle 6 Catchments",
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_convergence_comparison(results_list: List[Dict]) -> go.Figure:
    """Compare convergence of multiple catchments."""
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, result in enumerate(results_list):
        df = result['df']
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=df['iteration'],
            y=df['objective'],
            mode='lines',
            name=f"{result['name']} ({result['iterations']} iter)",
            line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{result['name']}</b><br>Iteration: %{{x}}<br>Objective: %{{y:.4f}}<extra></extra>"
        ))
    
    fig.update_layout(
        title="🔬 DDS Konvergenz-Vergleich: Mehrere Einzugsgebiete",
        height=500,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11)
    )
    
    fig.update_xaxes(title_text="Iteration", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(title_text="Objective Function (KGE-basiert) [-]", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_convergence_plot(df: pd.DataFrame, title: str = "DDS Convergence") -> go.Figure:
    """Plot objective function value over iterations."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['iteration'],
        y=df['objective'],
        mode='lines',
        name='Best Objective',
        line=dict(color='#1f77b4', width=2.5),
        hovertemplate='<b>Iteration: %{x}</b><br>Objective: %{y:.4f}<extra></extra>'
    ))
    
    initial_obj = df['objective'].iloc[0]
    final_obj = df['objective'].iloc[-1]
    improvement = ((initial_obj - final_obj) / initial_obj) * 100
    
    fig.add_annotation(
        x=len(df) // 2,
        y=final_obj,
        text=f"Verbesserung: {improvement:.1f}%",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#1f77b4",
        borderwidth=1
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, weight='bold', color='#ffffff')),
        height=400,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11)
    )
    
    fig.update_xaxes(title_text="Iteration", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(title_text="Objective Function [-]", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_parameter_evolution_with_names(df: pd.DataFrame, group_name: str = None, param_indices: List[int] = None) -> go.Figure:
    """Plot evolution of parameters with scientific names."""
    if param_indices is None:
        param_indices = list(range(1, min(11, len(df.columns) - 1)))
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, idx in enumerate(param_indices):
        col = f'param_{idx:02d}'
        if col in df.columns:
            param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
            
            fig.add_trace(go.Scatter(
                x=df['iteration'],
                y=df[col],
                mode='lines',
                name=f"P{idx:02d}: {param_name[:20]}",
                line=dict(color=colors[i % len(colors)], width=1.5),
                opacity=0.8,
                hovertemplate=f"<b>P{idx:02d}: {param_name}</b><br>Iteration: %{{x}}<br>Wert: %{{y:.4f}}<br>Einheit: {unit}<extra></extra>"
            ))
    
    fig.update_layout(
        title=f"📊 {group_name or 'Parameter-Evolution'} — Mit wissenschaftlichen Namen",
        height=450,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(30,30,30,0.9)"),
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=9)
    )
    
    fig.update_xaxes(title_text="Iteration", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(title_text="Parameter Value", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_parameter_change_table(results_list: List[Dict]) -> Optional[go.Figure]:
    """Show parameter changes from initial to final for all catchments."""
    if not results_list or len(results_list) == 0:
        return None
    
    rows = []
    
    for result in results_list:
        df = result['df']
        if len(df) < 2:
            continue
        initial = df.iloc[0]
        final = df.iloc[-1]
        
        for idx in range(1, 11):  # Top 10 parameters only
            col = f'param_{idx:02d}'
            if col not in df.columns:
                continue
            
            param_name, group, unit = DDS_PARAM_MAP.get(idx, (f'param_{idx:02d}', 'Unknown', ''))
            
            init_val = float(initial[col])
            final_val = float(final[col])
            change = ((final_val - init_val) / init_val * 100) if init_val != 0 else 0.0
            
            rows.append({
                'Catchment': result['name'],
                'Param': f'P{idx:02d}',
                'Name': param_name,
                'Group': group,
                'Initial': init_val,
                'Final': final_val,
                'Change_%': change
            })
    
    if not rows:
        return None
    
    df = pd.DataFrame(rows)
    
    try:
        pivot_df = df.pivot_table(
            index=['Param', 'Name', 'Group'],
            columns='Catchment',
            values=['Initial', 'Final', 'Change_%'],
            aggfunc='first'
        ).round(3)
        
        catchment_names = [r['name'] for r in results_list]
        
        header_values = ['Param', 'Name', 'Gruppe']
        for c in catchment_names:
            header_values.append(f'{c}')
        
        cell_values = [
            list(pivot_df.index.get_level_values('Param')),
            [str(x)[:18] for x in pivot_df.index.get_level_values('Name')],
            list(pivot_df.index.get_level_values('Group'))
        ]
        
        for c in catchment_names:
            cell_values.append([
                f"{pivot_df[('Initial', c)].iloc[i]:.3f} / {pivot_df[('Final', c)].iloc[i]:.3f} / {pivot_df[('Change_%', c)].iloc[i]:+.0f}%"
                for i in range(len(pivot_df))
            ])
        
        fig = go.Figure(data=go.Table(
            header=dict(values=header_values, fill_color="#1f77b4", align="left", font=dict(color="white", size=9)),
            cells=dict(values=cell_values, fill_color="rgba(30, 30, 30, 0.8)", align="left", font=dict(size=8, color="#ffffff"))
        ))
        
        fig.update_layout(
            title="📋 Parameter-Änderungen: Initial → Final (Top 10)",
            height=500,
            margin=dict(l=40, r=40, t=60, b=40),
            paper_bgcolor="rgba(30, 30, 30, 1)",
            plot_bgcolor="rgba(30, 30, 30, 1)"
        )
        
        return fig
    except Exception:
        return None


def create_improvement_summary(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate improvement metrics."""
    initial = df['objective'].iloc[0]
    final = df['objective'].iloc[-1]
    best = df['objective'].min()
    
    threshold = initial * 0.5
    iter_50 = df[df['objective'] <= threshold]['iteration'].iloc[0] if len(df[df['objective'] <= threshold]) > 0 else None
    
    return {
        'initial': float(initial),
        'final': float(final),
        'best': float(best),
        'improvement_abs': float(initial - final),
        'improvement_pct': float(((initial - final) / initial) * 100),
        'iterations': len(df),
        'iter_50_pct': int(iter_50) if iter_50 else None
    }


def create_dashboard_summary_card(df: pd.DataFrame, catchment_name: str = None) -> go.Figure:
    """Create a summary card with key metrics."""
    summary = create_improvement_summary(df)
    
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "indicator"}, {"type": "table"}]])
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=summary['improvement_pct'],
        delta={'reference': 0, 'valueformat': '.1f', 'suffix': '%'},
        title={'text': "Objektiv-Verbesserung", 'font': {'size': 14, 'color': '#ffffff'}},
        number={'font': {'size': 36, 'color': '#1f77b4'}}
    ), row=1, col=1)
    
    fig.add_trace(go.Table(
        header=dict(values=["<b>Metrik</b>", "<b>Wert</b>"], fill_color="#1f77b4", align="left", font=dict(color="white", size=11)),
        cells=dict(
            values=[
                ["Start-Objektiv", "End-Objektiv", "Bestes Objektiv", "Verbesserung", "Iterationen"],
                [f"{summary['initial']:.4f}", f"{summary['final']:.4f}", f"{summary['best']:.4f}", f"{summary['improvement_pct']:.1f}%", str(summary['iterations'])]
            ],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="left",
            font=dict(size=10, color="#ffffff")
        )
    ), row=1, col=2)
    
    fig.update_layout(height=320, margin=dict(l=40, r=40, t=40, b=40), paper_bgcolor="rgba(30, 30, 30, 1)", plot_bgcolor="rgba(30, 30, 30, 1)")
    
    return fig


def create_metrics_comparison_table(results_list: List[Dict]) -> Optional[go.Figure]:
    """Compare final model metrics between catchments."""
    if not results_list:
        return None
    
    all_metrics = {}
    
    for result in results_list:
        out_path = Path(result['path']).parent / 'FinalParam.out'
        if out_path.exists():
            metrics = parse_final_param_out(out_path)
            if metrics:
                all_metrics[result['name']] = metrics
    
    if not all_metrics:
        return None
    
    common_metrics = ['KGE', 'NSE', 'r', 'PBIAS']
    
    header_values = ['Metrik'] + list(all_metrics.keys())
    cell_values = [common_metrics]
    
    for catchment_name in all_metrics.keys():
        row = []
        for m in common_metrics:
            val = all_metrics[catchment_name].get(m)
            if val is not None and not np.isnan(val):
                row.append(f"{val:.4f}")
            else:
                row.append("N/A")
        cell_values.append(row)
    
    fig = go.Figure(data=go.Table(
        header=dict(values=header_values, fill_color="#1f77b4", align="left", font=dict(color="white", size=10)),
        cells=dict(values=cell_values, fill_color="rgba(30, 30, 30, 0.8)", align="left", font=dict(size=9, color="#ffffff"))
    ))
    
    fig.update_layout(
        title="📊 Modell-Performance-Vergleich (FinalParam)",
        height=300,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


# =============================================================================
# MAIN ANALYSIS FUNCTIONS
# =============================================================================

def analyze_single_dds(dds_results_path: str, title: str = "DDS Calibration") -> Dict:
    """Analyze single DDS calibration with sensitivity analysis."""
    result = parse_dds_results(dds_results_path)
    df = result['df']
    
    # Sensitivity analysis
    sensitivity_df = calculate_parameter_sensitivity(df)
    
    figures = {
        'convergence': create_convergence_plot(df, f"{title} - Konvergenz"),
        'summary': create_dashboard_summary_card(df, result['name']),
        'sensitivity_ranking': create_sensitivity_ranking_plot(sensitivity_df),
        'group_sensitivity': create_group_sensitivity_plot(sensitivity_df),
        'parameter_evolution': create_parameter_evolution_with_names(df, "Top 10 Parameter", list(range(1, 11))),
    }
    
    # Add FinalParam files if available
    nml_path = Path(dds_results_path).parent / 'FinalParam.nml'
    out_path = Path(dds_results_path).parent / 'FinalParam.out'
    
    if nml_path.exists():
        figures['final_params'] = parse_final_param_nml(nml_path)
    
    if out_path.exists():
        figures['final_metrics'] = parse_final_param_out(out_path)
    
    return {
        'result': result,
        'figures': figures,
        'sensitivity': sensitivity_df
    }


def analyze_multiple_dds(results_paths: List[Tuple[str, str]]) -> Dict:
    """Analyze multiple DDS calibrations."""
    results = [parse_dds_results(path, name) for path, name in results_paths]
    
    figures = {
        'convergence_comparison': create_convergence_comparison(results),
        'parameter_changes': create_parameter_change_table(results),
        'metrics_comparison': create_metrics_comparison_table(results),
    }
    
    # Add individual sensitivity analyses
    for result in results:
        sensitivity_df = calculate_parameter_sensitivity(result['df'])
        figures[f"{result['name']}_sensitivity"] = create_sensitivity_ranking_plot(sensitivity_df)
    
    return {
        'results': results,
        'figures': figures
    }


# =============================================================================
# DASHBOARD INTEGRATION
# =============================================================================

# Translations dictionary
TRANSLATIONS = {
    'de': {
        'header': "🔧 mHM DDS Kalibrierungs-Analyse",
        'subtitle': "**Dynamically Dimensioned Search (DDS) Optimierung für mHM Re-Crit**",
        'mode_label': "📊 Analyse-Modus",
        'mode_single': "Einzel-Catchment",
        'mode_multi': "Mehrere Catchments (Vergleich)",
        'no_dds': "Keine DDS-Ergebnisse gefunden!",
        'found_catchments': "{} Catchments mit DDS-Kalibrierung gefunden",
        'select_catchment': "Catchment auswählen",
        'start_objective': "Start-Objektiv",
        'end_objective': "End-Objektiv",
        'improvement': "Verbesserung",
        'iterations': "Iterationen",
        'sensitivity_title': "🎯 Parameter-Sensitivitätsanalyse",
        'sensitivity_info': """
        **Wie funktioniert die Sensitivitätsanalyse?**
        
        - **Korrelation:** Wie stark ändert sich das Ziel bei Parameter-Änderung?
        - **Range:** Wie groß ist der Wertebereich des Parameters?
        - **Sensitivity Score:** |Korrelation| × Range → Höher = Einflussreicher
        
        **Interpretation:**
        - Top-Parameter haben größten Einfluss auf Modell-Performance
        - Niedrige Sensitivität = Parameter kann kaum kalibriert werden
        - Gruppen-Vergleich zeigt welche Prozesse am wichtigsten sind
        """,
        'sensitivity_not_available': "Sensitivitätsanalyse nicht verfügbar (ungenügende Daten)",
        'group_sensitivity_not_available': "Gruppen-Sensitivität nicht verfügbar",
        'error_analysis': "Fehler bei der Analyse: {}",
        'show_basic': "Zeige nur Basis-Konvergenz...",
        'parameter_evolution': "📈 Parameter-Evolution (mit wissenschaftlichen Namen)",
        'final_params': "📋 Finale Parameter & Metriken",
        'multi_compare': "🔬 Vergleich: Mehrere Einzugsgebiete",
        'convergence_compare': "📈 Konvergenz-Vergleich",
        'sensitivity_compare': "🎯 Sensitivitätsanalyse-Vergleich",
        'sensitivity_compare_info': "Zeigt die Top 10 sensitivsten Parameter für jedes Catchment im direkten Vergleich",
        'top_sensitivity': "📊 {} - Top 10 Sensitivste Parameter",
        'param_changes': "📋 Parameter-Änderungen: Initial → Final",
        'param_changes_not_available': "Parameter-Änderungen nicht verfügbar",
        'performance_compare': "📊 Performance-Vergleich",
        'performance_not_available': "Performance-Metriken nicht verfügbar",
        'perf_summary': "📊 Performance-Übersicht: Alle Catchments",
        'param_stats': "📊 Parameter-Statistik (Mean, Std, CV)",
        'param_stats_info': """
        **Statistische Auswertung über alle Catchments:**
        - **Mean:** Durchschnittlicher Parameterwert
        - **Std:** Standardabweichung (Variabilität)
        - **CV:** Variationskoeffizient (Std/Mean)
        - **Konsistenz:** CV < 0.1 = ✓, 0.1-0.3 = ○, > 0.3 = ✗
        """,
        'indiv_sensitivity': "📊 Individuelle Sensitivitäts-Rankings",
        
        'perf_summary_en': "📊 Performance Summary: All Catchments",
        'param_stats_en': "📊 Parameter Statistics (Mean, Std, CV)",
        'param_stats_info_en': """
        **Statistical analysis across all catchments:**
        - **Mean:** Average parameter value
        - **Std:** Standard deviation (variability)
        - **CV:** Coefficient of variation (Std/Mean)
        - **Consistency:** CV < 0.1 = ✓, 0.1-0.3 = ○, > 0.3 = ✗
        """,
        'indiv_sensitivity_en': "📊 Individual Sensitivity Rankings",
        'methodology': "📖 DDS Methodik & Interpretation",
        'export': "💾 Export",
        'download_csv': "📥 DDS Results CSV",
        'lang_switch': "🌐 Sprache / Language",
        'lang_de': "🇩🇪 Deutsch",
        'lang_en': "🇬🇧 English",
    },
    'en': {
        'header': "🔧 mHM DDS Calibration Analysis",
        'subtitle': "**Dynamically Dimensioned Search (DDS) Optimization for mHM Re-Crit**",
        'mode_label': "📊 Analysis Mode",
        'mode_single': "Single Catchment",
        'mode_multi': "Multiple Catchments (Comparison)",
        'no_dds': "No DDS results found!",
        'found_catchments': "{} catchments with DDS calibration found",
        'select_catchment': "Select catchment",
        'start_objective': "Start Objective",
        'end_objective': "End Objective",
        'improvement': "Improvement",
        'iterations': "Iterations",
        'sensitivity_title': "🎯 Parameter Sensitivity Analysis",
        'sensitivity_info': """
        **How does sensitivity analysis work?**
        
        - **Correlation:** How much does the objective change with parameter variation?
        - **Range:** What is the parameter value range?
        - **Sensitivity Score:** |Correlation| × Range → Higher = More influential
        
        **Interpretation:**
        - Top parameters have greatest influence on model performance
        - Low sensitivity = Parameter hardly identifiable
        - Group comparison shows which processes are most important
        """,
        'sensitivity_not_available': "Sensitivity analysis not available (insufficient data)",
        'group_sensitivity_not_available': "Group sensitivity not available",
        'error_analysis': "Analysis error: {}",
        'show_basic': "Showing basic convergence only...",
        'parameter_evolution': "📈 Parameter Evolution (with scientific names)",
        'final_params': "📋 Final Parameters & Metrics",
        'multi_compare': "🔬 Comparison: Multiple Catchments",
        'convergence_compare': "📈 Convergence Comparison",
        'sensitivity_compare': "🎯 Sensitivity Analysis Comparison",
        'sensitivity_compare_info': "Shows top 10 most sensitive parameters for each catchment in direct comparison",
        'top_sensitivity': "📊 {} - Top 10 Most Sensitive Parameters",
        'param_changes': "📋 Parameter Changes: Initial → Final",
        'param_changes_not_available': "Parameter changes not available",
        'performance_compare': "📊 Performance Comparison",
        'performance_not_available': "Performance metrics not available",
        'methodology': "📖 DDS Methodology & Interpretation",
        'export': "💾 Export",
        'download_csv': "📥 Download DDS Results CSV",
        'lang_switch': "🌐 Sprache / Language",
        'lang_de': "🇩🇪 Deutsch",
        'lang_en': "🇬🇧 English",
    }
}


def render_dds_analysis_tab():
    """Streamlit tab content for DDS analysis."""
    import streamlit as st
    
    # Use global language state from main app
    language = st.session_state.language
    t = TRANSLATIONS[language]
    
    st.header(t['header'])
    st.markdown(t['subtitle'])
    
    catchments = [
        ("Parthe_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"),
        ("Goeltzsch2_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/goeltzsch2_0p0625/dds_results.out"),
        ("Chemnitz2_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/chemnitz2_0p0625/dds_results.out"),
        ("Wesenitz2_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/wesenitz2_0p0625/dds_results.out"),
        ("Wyhra_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/wyhra_0p0625/dds_results.out"),
        ("Zwoenitz1_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/zwoenitz1_0p0625/dds_results.out"),
    ]
    
    existing = [(name, path) for name, path in catchments if Path(path).exists()]
    
    if not existing:
        st.error(t['no_dds'])
        st.stop()
    
    st.success(t['found_catchments'].format(len(existing)))
    
    mode = st.radio(t['mode_label'], [t['mode_single'], t['mode_multi']], horizontal=True)
    
    if mode == t['mode_single']:
        selected = st.selectbox(t['select_catchment'], options=[name for name, _ in existing], index=0)
        path = next(p for n, p in existing if n == selected)
        
        try:
            result = parse_dds_results(path, selected)
            df = result['df']
            if language == 'de':
                st.success(f"DDS-Daten geladen: {len(df)} Iterationen, {result['n_params']} Parameter")
            else:
                st.success(f"DDS data loaded: {len(df)} iterations, {result['n_params']} parameters")
        except Exception as e:
            if language == 'de':
                st.error(f"Fehler: {e}")
            else:
                st.error(f"Error: {e}")
            st.stop()
        
        summary = create_improvement_summary(df)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(t['start_objective'], f"{summary['initial']:.4f}")
        with c2:
            st.metric(t['end_objective'], f"{summary['final']:.4f}")
        with c3:
            st.metric(t['improvement'], f"{summary['improvement_pct']:.1f}%")
        with c4:
            st.metric(t['iterations'], str(summary['iterations']))
        
        st.subheader(t['sensitivity_title'])
        st.markdown(t['sensitivity_info'])
        
        try:
            analysis = analyze_single_dds(path, selected)
            
            if analysis['figures'].get('sensitivity_ranking'):
                st.plotly_chart(analysis['figures']['sensitivity_ranking'], use_container_width=True)
            else:
                st.warning(t['sensitivity_not_available'])
            
            c1, c2 = st.columns(2)
            with c1:
                if analysis['figures'].get('group_sensitivity'):
                    st.plotly_chart(analysis['figures']['group_sensitivity'], use_container_width=True)
                else:
                    st.info(t['group_sensitivity_not_available'])
            with c2:
                st.plotly_chart(analysis['figures']['convergence'], use_container_width=True)
        except Exception as e:
            st.error(t['error_analysis'].format(e))
            st.info(t['show_basic'])
            result = parse_dds_results(path, selected)
            summary = create_improvement_summary(result['df'])
            conv_title = f"{selected} - Konvergenz" if language == 'de' else f"{selected} - Convergence"
            st.plotly_chart(create_convergence_plot(result['df'], conv_title), use_container_width=True)
        
        st.subheader(t['parameter_evolution'])
        st.plotly_chart(analysis['figures']['parameter_evolution'], use_container_width=True)
        
        st.divider()
        st.subheader(t['final_params'])
        
        nml_path = Path(path).parent / 'FinalParam.nml'
        if nml_path.exists():
            final_params = parse_final_param_nml(nml_path)
            param_df = pd.DataFrame(list(final_params.items())[:20], columns=['Parameter', 'Value'])
            st.dataframe(param_df, height=400, use_container_width=True)
        
        out_path = Path(path).parent / 'FinalParam.out'
        if out_path.exists():
            final_metrics = parse_final_param_out(out_path)
            if final_metrics:
                if language == 'de':
                    metrics_df = pd.DataFrame(list(final_metrics.items()), columns=['Metrik', 'Wert'])
                else:
                    metrics_df = pd.DataFrame(list(final_metrics.items()), columns=['Metric', 'Value'])
                st.dataframe(metrics_df, height=300, use_container_width=True)
    
    else:  # mode == t['mode_multi']
        st.subheader(t['multi_compare'])
        
        results = [parse_dds_results(path, name) for name, path in existing]
        
        st.info(f"📊 **{len(results)} Catchments** mit DDS-Kalibrierung analysiert")
        
        # 1. Performance Summary Table
        st.subheader(t['perf_summary'] if language == 'de' else t['perf_summary_en'])
        fig = create_performance_summary_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t['performance_not_available'])
        
        # 2. Convergence Comparison
        st.subheader(t['convergence_compare'])
        fig = create_convergence_comparison(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 3. Parameter Statistics (NEW!)
        st.subheader(t['param_stats'] if language == 'de' else t['param_stats_en'])
        st.info(t['param_stats_info'] if language == 'de' else t['param_stats_info_en'])
        
        fig = create_parameter_statistics_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Parameter statistics not available")
        
        st.divider()
        
        # 4. Sensitivity Comparison
        st.subheader(t['sensitivity_compare'])
        st.info(t['sensitivity_compare_info'])
        
        # Sensitivity comparison for each catchment
        sensitivity_results = {}
        for r in results:
            sens_df = calculate_parameter_sensitivity(r['df'])
            sensitivity_results[r['name']] = sens_df
        
        # Create comparison plot
        fig = create_sensitivity_comparison_plot(sensitivity_results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(t['sensitivity_not_available'])
        
        # Show individual sensitivity rankings
        st.subheader(t['indiv_sensitivity'] if language == 'de' else t['indiv_sensitivity_en'])
        
        cols = st.columns(2 if len(results) <= 4 else 3)
        for i, (name, sens_df) in enumerate(sensitivity_results.items()):
            with cols[i % len(cols)]:
                st.subheader(f"{name}")
                fig = create_sensitivity_ranking_plot(sens_df, top_n=8)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 5. Parameter Recommendations (NEW!)
        st.subheader("🎯 Empfohlene Parameter-Sets: GLOBAL vs. LOKAL")
        st.info("""
        **Automatische Empfehlung basierend auf CV-Analyse:**
        - **GLOBAL:** CV < 0.1 → Parameter über alle Catchments konsistent
        - **GLOBAL ±σ:** CV 0.1-0.3 → Moderat variabel, Unsicherheit beachten
        - **LOKAL:** CV > 0.3 → Catchment-spezifisch kalibrieren
        
        **Download:** `recommended_params.csv` für mHM-Param.nml
        """)
        
        fig = create_parameter_recommendation_table(results, cv_threshold=0.1)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Parameter recommendations not available")
        
        # Export button
        csv_path = "/tmp/recommended_params.csv"
        export_path = export_parameter_recommendations(results, csv_path, cv_threshold=0.1)
        
        if export_path:
            with open(export_path, 'rb') as f:
                st.download_button(
                    label="💾 Download: recommended_params.csv",
                    data=f.read(),
                    file_name="recommended_params.csv",
                    mime="text/csv",
                    key="download_params_csv"
                )
        
        st.divider()
        st.subheader(t['param_changes'])
        fig = create_parameter_change_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t['param_changes_not_available'])
        
        st.subheader(t['performance_compare'])
        fig = create_metrics_comparison_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t['performance_not_available'])
    
    with st.expander(t['methodology']):
        if language == 'de':
            st.markdown("""
### 🔬 Dynamically Dimensioned Search (DDS)

**Algorithmus:** Globale Optimierung für hydrologische Modelle

**Prinzip:**
1. Start mit allen Parametern (volle Dimension)
2. Zufällige Perturbation mit Normalverteilung
3. Dimensionalität reduziert sich über Zeit
4. Nur Verbesserungen werden akzeptiert

**Parameter-Gruppen (mHM 5.13.2):**
- **Snow (1-9):** Schnee-Schmelze, Temperature thresholds
- **Soil (10-26):** Boden-Speicher, PTF, Infiltration
- **Direct Runoff (27):** Versiegelte Flächen
- **PET (28-30):** Potentielle Evapotranspiration
- **Interflow (31-35):** Zwischenabfluss
- **Percolation (36-38):** Grundwasserneubildung
- **Routing (39):** Fluss-Routing
- **Geology (40-54):** Geologie-Parameter

### 🎯 Sensitivitätsanalyse

**Berechnung:**
- Korrelation zwischen Parameter und Zielfunktion
- Multipliziert mit Parameter-Range
- Höherer Score = Größerer Einfluss

**Interpretation:**
- **Top-Parameter:** Sollten priorisiert kalibriert werden
- **Niedrige Sensitivität:** Parameter kaum identifizierbar
- **Gruppen-Vergleich:** Welche Prozesse dominieren?
            """)
        else:
            st.markdown("""
### 🔬 Dynamically Dimensioned Search (DDS)

**Algorithm:** Global optimization for hydrological models

**Principle:**
1. Start with all parameters (full dimension)
2. Random perturbation with normal distribution
3. Dimensionality reduces over time
4. Only improvements are accepted

**Parameter Groups (mHM 5.13.2):**
- **Snow (1-9):** Snow melt, temperature thresholds
- **Soil (10-26):** Soil storage, PTF, infiltration
- **Direct Runoff (27):** Impervious areas
- **PET (28-30):** Potential evapotranspiration
- **Interflow (31-35):** Subsurface flow
- **Percolation (36-38):** Groundwater recharge
- **Routing (39):** River routing
- **Geology (40-54):** Geology parameters

### 🎯 Sensitivity Analysis

**Calculation:**
- Correlation between parameter and objective function
- Multiplied by parameter range
- Higher score = Greater influence

**Interpretation:**
- **Top parameters:** Should be prioritized in calibration
- **Low sensitivity:** Parameter hardly identifiable
- **Group comparison:** Which processes dominate?
            """)
    
    st.divider()
    st.subheader(t['export'])
    
    if mode == t['mode_single']:
        csv_data = df.to_csv(index=False)
        st.download_button(t['download_csv'], data=csv_data.encode("utf-8"), file_name=f"{selected}_dds_results.csv", mime="text/csv")


if __name__ == "__main__":
    parthe_path = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"
    result = analyze_single_dds(parthe_path)
    print(f"✅ Single: Sensitivity top 5:")
    print(result['sensitivity'][['index', 'name', 'sensitivity_score']].head())
