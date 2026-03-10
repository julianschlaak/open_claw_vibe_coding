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
    """Parse FinalParam.out (model performance metrics)."""
    metrics = {}
    
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
    
    return metrics


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

def render_dds_analysis_tab():
    """Streamlit tab content for DDS analysis."""
    import streamlit as st
    
    st.header("🔧 mHM DDS Kalibrierungs-Analyse")
    st.markdown("**Dynamically Dimensioned Search (DDS) Optimierung für mHM Re-Crit**")
    
    catchments = [
        ("Parthe_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"),
        ("Goeltzsch2_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/goeltzsch2_0p0625/dds_results.out"),
    ]
    
    existing = [(name, path) for name, path in catchments if Path(path).exists()]
    
    if not existing:
        st.error("Keine DDS-Ergebnisse gefunden!")
        st.stop()
    
    st.success(f"{len(existing)} Catchments mit DDS-Kalibrierung gefunden")
    
    mode = st.radio("📊 Analyse-Modus", ["Einzel-Catchment", "Mehrere Catchments (Vergleich)"], horizontal=True)
    
    if mode == "Einzel-Catchment":
        selected = st.selectbox("Catchment auswählen", options=[name for name, _ in existing], index=0)
        path = next(p for n, p in existing if n == selected)
        
        try:
            result = parse_dds_results(path, selected)
            df = result['df']
            st.success(f"DDS-Daten geladen: {len(df)} Iterationen, {result['n_params']} Parameter")
        except Exception as e:
            st.error(f"Fehler: {e}")
            st.stop()
        
        summary = create_improvement_summary(df)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Start-Objektiv", f"{summary['initial']:.4f}")
        with c2:
            st.metric("End-Objektiv", f"{summary['final']:.4f}")
        with c3:
            st.metric("Verbesserung", f"{summary['improvement_pct']:.1f}%")
        with c4:
            st.metric("Iterationen", str(summary['iterations']))
        
        st.subheader("🎯 Parameter-Sensitivitätsanalyse")
        st.markdown("""
        **Wie funktioniert die Sensitivitätsanalyse?**
        
        - **Korrelation:** Wie stark ändert sich das Ziel bei Parameter-Änderung?
        - **Range:** Wie groß ist der Wertebereich des Parameters?
        - **Sensitivity Score:** |Korrelation| × Range → Höher = Einflussreicher
        
        **Interpretation:**
        - Top-Parameter haben größten Einfluss auf Modell-Performance
        - Niedrige Sensitivität = Parameter kann kaum kalibriert werden
        - Gruppen-Vergleich zeigt welche Prozesse am wichtigsten sind
        """)
        
        try:
            analysis = analyze_single_dds(path, selected)
            
            if analysis['figures'].get('sensitivity_ranking'):
                st.plotly_chart(analysis['figures']['sensitivity_ranking'], use_container_width=True)
            else:
                st.warning("Sensitivitätsanalyse nicht verfügbar (ungenügende Daten)")
            
            c1, c2 = st.columns(2)
            with c1:
                if analysis['figures'].get('group_sensitivity'):
                    st.plotly_chart(analysis['figures']['group_sensitivity'], use_container_width=True)
                else:
                    st.info("Gruppen-Sensitivität nicht verfügbar")
            with c2:
                st.plotly_chart(analysis['figures']['convergence'], use_container_width=True)
        except Exception as e:
            st.error(f"Fehler bei der Analyse: {e}")
            st.info("Zeige nur Basis-Konvergenz...")
            result = parse_dds_results(path, selected)
            summary = create_improvement_summary(result['df'])
            st.plotly_chart(create_convergence_plot(result['df'], f"{selected} - Konvergenz"), use_container_width=True)
        
        st.subheader("📈 Parameter-Evolution (mit wissenschaftlichen Namen)")
        st.plotly_chart(analysis['figures']['parameter_evolution'], use_container_width=True)
        
        st.divider()
        st.subheader("📋 Finale Parameter & Metriken")
        
        nml_path = Path(path).parent / 'FinalParam.nml'
        if nml_path.exists():
            final_params = parse_final_param_nml(nml_path)
            param_df = pd.DataFrame(list(final_params.items())[:20], columns=['Parameter', 'Value'])
            st.dataframe(param_df, height=400, use_container_width=True)
        
        out_path = Path(path).parent / 'FinalParam.out'
        if out_path.exists():
            final_metrics = parse_final_param_out(out_path)
            if final_metrics:
                metrics_df = pd.DataFrame(list(final_metrics.items()), columns=['Metrik', 'Wert'])
                st.dataframe(metrics_df, height=300, use_container_width=True)
    
    else:
        st.subheader("🔬 Vergleich: Mehrere Einzugsgebiete")
        
        results = [parse_dds_results(path, name) for name, path in existing]
        
        comp_df = pd.DataFrame([{
            'Catchment': r['name'],
            'Iterationen': r['iterations'],
            'Parameter': r['n_params'],
            'Start': f"{r['df']['objective'].iloc[0]:.4f}",
            'Ende': f"{r['df']['objective'].iloc[-1]:.4f}",
            'Verbesserung': f"{((r['df']['objective'].iloc[0] - r['df']['objective'].iloc[-1]) / r['df']['objective'].iloc[0] * 100):.1f}%"
        } for r in results])
        
        st.dataframe(comp_df, use_container_width=True)
        
        st.subheader("📈 Konvergenz-Vergleich")
        fig = create_convergence_comparison(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("📋 Parameter-Änderungen: Initial → Final")
        fig = create_parameter_change_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Parameter-Änderungen nicht verfügbar")
        
        st.subheader("📊 Performance-Vergleich")
        fig = create_metrics_comparison_table(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Performance-Metriken nicht verfügbar")
    
    with st.expander("📖 DDS Methodik & Interpretation"):
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
    
    st.divider()
    st.subheader("💾 Export")
    
    if mode == "Einzel-Catchment":
        csv_data = df.to_csv(index=False)
        st.download_button("📥 DDS Results CSV", data=csv_data.encode("utf-8"), file_name=f"{selected}_dds_results.csv", mime="text/csv")


if __name__ == "__main__":
    parthe_path = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"
    result = analyze_single_dds(parthe_path)
    print(f"✅ Single: Sensitivity top 5:")
    print(result['sensitivity'][['index', 'name', 'sensitivity_score']].head())
