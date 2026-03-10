"""
Scientific DDS Calibration Analysis for mHM Re-Crit (Multiple Catchments)

Analyzes DDS (Dynamically Dimensioned Search) optimization results:
- Single catchment: Convergence, parameter evolution, parallel coordinates
- Multi-calculation: Comparison between catchments
- Scientific explanations of calibration process

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
# PARAMETER GROUPS (mHM 5.13.2)
# =============================================================================

PARAM_GROUPS = {
    'Soil (1-12)': list(range(1, 13)),      # Soil storage capacities
    'Routing (13-20)': list(range(13, 21)),  # mRM routing parameters
    'Groundwater (21-30)': list(range(21, 31)), # Groundwater storage
    'Surface (31-40)': list(range(31, 41)),   # Surface runoff
    'Evapotranspiration (41-50)': list(range(41, 51)), # ET parameters
    'Precipitation/Snow (51-54)': list(range(51, 55)), # Snow/Precip correction
}

PARAM_DESCRIPTIONS = {
    'param_01': 'FC1: Field capacity, layer 1 [mm]',
    'param_02': 'WP1: Wilting point, layer 1 [mm]',
    'param_03': 'FC2: Field capacity, layer 2 [mm]',
    'param_04': 'WP2: Wilting point, layer 2 [mm]',
    'param_05': 'FC3: Field capacity, layer 3 [mm]',
    'param_06': 'WP3: Wilting point, layer 3 [mm]',
    'param_13': 'c_z: Manning coefficient overland flow',
    'param_14': 'c_l: Manning coefficient channel flow',
    'param_21': 'K_GW1: Groundwater recession constant, shallow',
    'param_22': 'K_GW2: Groundwater recession constant, deep',
    'param_31': 'C_R: Surface runoff coefficient',
    'param_41': 'C_T: Temperature correction for ET',
    'param_51': 'P_corr: Precipitation correction factor',
    'param_52': 'T_snow: Snow-rain threshold [°C]',
}


# =============================================================================
# DDS RESULTS PARSING
# =============================================================================

def parse_dds_results(filepath: str, catchment_name: str = None) -> Dict:
    """
    Parse dds_results.out file.
    
    Returns
    -------
    dict
        {'name': catchment_name, 'df': DataFrame, 'path': filepath}
    """
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
    """Parse FinalParam.nml (mhm_parameter.nml format)."""
    params = {}
    
    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()
    
    pattern = r'(\w+)\s*=\s*([\d.E+-]+)'
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        try:
            params[name] = float(value)
        except ValueError:
            pass
    
    return params


def parse_final_param_out(filepath: str) -> Dict[str, float]:
    """Parse FinalParam.out (model performance metrics)."""
    metrics = {}
    
    with open(filepath, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    for line in lines:
        if '=' in line:
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
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_convergence_comparison(results_list: List[Dict]) -> go.Figure:
    """
    Compare convergence of multiple catchments.
    """
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    for i, result in enumerate(results_list):
        df = result['df']
        color = colors[i % len(colors)]
        
        fig.add_trace(
            go.Scatter(
                x=df['iteration'],
                y=df['objective'],
                mode='lines',
                name=f"{result['name']} ({result['iterations']} iter)",
                line=dict(color=color, width=2.5),
                hovertemplate=f"<b>{result['name']}</b><br>Iteration: %{{x}}<br>Objective: %{{y:.4f}}<extra></extra>"
            )
        )
    
    fig.update_layout(
        title=dict(
            text="🔬 DDS Konvergenz-Vergleich: Mehrere Einzugsgebiete",
            font=dict(size=14, weight='bold', color='#ffffff')
        ),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(30, 30, 30, 0.9)",
            font=dict(color="#ffffff", size=11)
        ),
        hovermode="x unified",
        template="plotly_dark",
        margin=dict(l=60, r=40, t=100, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11)
    )
    
    fig.update_xaxes(
        title_text="Iteration",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.3)"
    )
    
    fig.update_yaxes(
        title_text="Objective Function (KGE-basiert) [-]",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.1)",
        linecolor="rgba(255, 255, 255, 0.3)"
    )
    
    return fig


def create_convergence_plot(df: pd.DataFrame, title: str = "DDS Convergence") -> go.Figure:
    """Plot objective function value over iterations."""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['iteration'],
            y=df['objective'],
            mode='lines',
            name='Best Objective',
            line=dict(color='#1f77b4', width=2.5),
            hovertemplate='<b>Iteration: %{x}</b><br>Objective: %{y:.4f}<extra></extra>'
        )
    )
    
    # Improvement annotation
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
        showlegend=True,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11)
    )
    
    fig.update_xaxes(title_text="Iteration", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(title_text="Objective Function [-]", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_parameter_group_evolution(df: pd.DataFrame, group_name: str, param_indices: List[int]) -> go.Figure:
    """
    Plot evolution of a parameter group (e.g., soil parameters 1-12).
    """
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
              '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5']
    
    for i, param_idx in enumerate(param_indices):
        col = f'param_{param_idx:02d}'
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['iteration'],
                    y=df[col],
                    mode='lines',
                    name=f"P{param_idx:02d}",
                    line=dict(color=colors[i % len(colors)], width=1.5),
                    opacity=0.8
                )
            )
    
    fig.update_layout(
        title=f"📊 {group_name} — Parameter-Evolution",
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=10)
    )
    
    fig.update_xaxes(title_text="Iteration", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(title_text="Parameter Value [-]", showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_faceted_parameter_groups(df: pd.DataFrame) -> go.Figure:
    """
    Create faceted plot showing all parameter groups.
    """
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=list(PARAM_GROUPS.keys()),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for idx, (group_name, param_indices) in enumerate(PARAM_GROUPS.items()):
        row = (idx // 2) + 1
        col = (idx % 2) + 1
        
        for i, param_idx in enumerate(param_indices[:8]):  # Show first 8 per group
            col_name = f'param_{param_idx:02d}'
            if col_name in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['iteration'],
                        y=df[col_name],
                        mode='lines',
                        name=f"P{param_idx:02d}",
                        line=dict(color=colors[i % len(colors)], width=1.2),
                        opacity=0.7,
                        showlegend=False
                    ),
                    row=row, col=col
                )
    
    fig.update_layout(
        height=900,
        showlegend=False,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=60, b=40),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=9)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_improvement_summary(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate improvement metrics."""
    initial = df['objective'].iloc[0]
    final = df['objective'].iloc[-1]
    best = df['objective'].min()
    
    # Find when 50% improvement occurred
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
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "table"}]]
    )
    
    # Indicator: Improvement
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=summary['improvement_pct'],
            delta={'reference': 0, 'valueformat': '.1f', 'suffix': '%'},
            title={'text': "Objektiv-Verbesserung", 'font': {'size': 14, 'color': '#ffffff'}},
            number={'font': {'size': 40, 'color': '#1f77b4'}}
        ),
        row=1, col=1
    )
    
    # Table: Key metrics
    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Metrik</b>", "<b>Wert</b>"],
                fill_color="#1f77b4",
                align="left",
                font=dict(color="white", size=12)
            ),
            cells=dict(
                values=[
                    ["Start-Objektiv", "End-Objektiv", "Bestes Objektiv", "Verbesserung", "Iterationen"],
                    [f"{summary['initial']:.4f}", f"{summary['final']:.4f}",
                     f"{summary['best']:.4f}", f"{summary['improvement_pct']:.1f}%",
                     str(summary['iterations'])]
                ],
                fill_color="rgba(30, 30, 30, 0.8)",
                align="left",
                font=dict(size=11, color="#ffffff")
            )
        ),
        row=1, col=2
    )
    
    if catchment_name:
        fig.add_annotation(
            x=0.5, y=1.15, xref="paper", yref="paper",
            text=f"Catchment: {catchment_name}",
            showarrow=False,
            font=dict(size=14, color="#ffffff")
        )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


def create_parameter_comparison_table(results_list: List[Dict]) -> go.Figure:
    """
    Compare final parameters between catchments.
    """
    # Get final parameters for each catchment
    all_params = {}
    
    for result in results_list:
        nml_path = Path(result['path']).parent / 'FinalParam.nml'
        if nml_path.exists():
            params = parse_final_param_nml(nml_path)
            all_params[result['name']] = params
    
    # Select key parameters (first 20)
    key_params = [f'param_{i:02d}' for i in range(1, 21)]
    
    # Build table
    headers = ['Parameter'] + [r['name'] for r in results_list]
    rows = [key_params]
    
    for param in key_params:
        row = [param]
        for result in results_list:
            if result['name'] in all_params and param in all_params[result['name']]:
                row.append(f"{all_params[result['name']][param]:.4f}")
            else:
                row.append('N/A')
        rows.append(row)
    
    fig = go.Figure(data=go.Table(
        header=dict(
            values=headers,
            fill_color="#1f77b4",
            align="left",
            font=dict(color="white", size=11)
        ),
        cells=dict(
            values=[list(row) for row in zip(*rows)],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="left",
            font=dict(size=10, color="#ffffff")
        )
    ))
    
    fig.update_layout(
        title="📋 Finale Parameter-Vergleich (Top 20)",
        height=600,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


def create_metrics_comparison_table(results_list: List[Dict]) -> go.Figure:
    """
    Compare final model metrics between catchments.
    """
    all_metrics = {}
    
    for result in results_list:
        out_path = Path(result['path']).parent / 'FinalParam.out'
        if out_path.exists():
            metrics = parse_final_param_out(out_path)
            all_metrics[result['name']] = metrics
    
    # Common metrics
    common_metrics = ['KGE', 'NSE', 'r', 'PBIAS', 'RMSE', 'MAE']
    
    # Build table
    headers = ['Metrik'] + [r['name'] for r in results_list]
    rows = [common_metrics]
    
    for metric in common_metrics:
        row = [metric]
        for result in results_list:
            if result['name'] in all_metrics and metric in all_metrics[result['name']]:
                row.append(f"{all_metrics[result['name']][metric]:.4f}")
            else:
                row.append('N/A')
        rows.append(row)
    
    fig = go.Figure(data=go.Table(
        header=dict(
            values=headers,
            fill_color="#1f77b4",
            align="left",
            font=dict(color="white", size=11)
        ),
        cells=dict(
            values=[list(row) for row in zip(*rows)],
            fill_color="rgba(30, 30, 30, 0.8)",
            align="left",
            font=dict(size=10, color="#ffffff")
        )
    ))
    
    fig.update_layout(
        title="📊 Modell-Performance-Vergleich (FinalParam)",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_multiple_dds(results_paths: List[Tuple[str, str]]) -> Dict:
    """
    Analyze multiple DDS calibrations.
    
    Parameters
    ----------
    results_paths : List[Tuple[str, str]]
        List of (filepath, catchment_name) tuples
    
    Returns
    -------
    dict
        Analysis results with figures and data
    """
    results = [parse_dds_results(path, name) for path, name in results_paths]
    
    figures = {
        'convergence_comparison': create_convergence_comparison(results),
        'parameter_comparison': create_parameter_comparison_table(results),
        'metrics_comparison': create_metrics_comparison_table(results),
    }
    
    # Add individual analyses
    for result in results:
        figures[f"{result['name']}_convergence"] = create_convergence_plot(
            result['df'], f"{result['name']} - Konvergenz"
        )
        figures[f"{result['name']}_summary"] = create_dashboard_summary_card(
            result['df'], result['name']
        )
        figures[f"{result['name']}_groups"] = create_faceted_parameter_groups(result['df'])
    
    return {
        'results': results,
        'figures': figures
    }


def analyze_single_dds(dds_results_path: str, title: str = "DDS Calibration") -> Dict:
    """Analyze single DDS calibration."""
    result = parse_dds_results(dds_results_path)
    df = result['df']
    
    figures = {
        'convergence': create_convergence_plot(df, f"{title} - Konvergenz"),
        'summary': create_dashboard_summary_card(df, result['name']),
        'parameter_groups': create_faceted_parameter_groups(df),
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
        'figures': figures
    }


# =============================================================================
# DASHBOARD INTEGRATION
# =============================================================================

def render_dds_analysis_tab():
    """Streamlit tab content for DDS analysis."""
    import streamlit as st
    
    st.header("🔧 mHM DDS Kalibrierungs-Analyse")
    st.markdown(
        "**Dynamically Dimensioned Search (DDS) Optimierung für mHM Re-Crit**\n\n"
        "Automatische Parameter-Kalibrierung mit globalem Optimierungsalgorithmus"
    )
    
    # Define catchments with DDS results
    catchments = [
        ("Parthe_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"),
        ("Goeltzsch2_0p0625", "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/goeltzsch2_0p0625/dds_results.out"),
    ]
    
    # Filter existing files
    existing = [(name, path) for name, path in catchments if Path(path).exists()]
    
    if not existing:
        st.error("Keine DDS-Ergebnisse gefunden!")
        st.stop()
    
    st.success(f"{len(existing)} Catchments mit DDS-Kalibrierung gefunden")
    
    # Mode selection
    mode = st.radio(
        "📊 Analyse-Modus",
        ["Einzel-Catchment", "Mehrere Catchments (Vergleich)"],
        horizontal=True
    )
    
    if mode == "Einzel-Catchment":
        # Select catchment
        selected = st.selectbox(
            "Catchment auswählen",
            options=[name for name, _ in existing],
            index=0
        )
        
        path = next(p for n, p in existing if n == selected)
        
        # Load and analyze
        try:
            result = parse_dds_results(path, selected)
            df = result['df']
            st.success(f"DDS-Daten geladen: {len(df)} Iterationen, {result['n_params']} Parameter")
        except Exception as e:
            st.error(f"Fehler: {e}")
            st.stop()
        
        # Summary metrics
        summary = create_improvement_summary(df)
        
        # Key metrics row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Start-Objektiv", f"{summary['initial']:.4f}")
        with c2:
            st.metric("End-Objektiv", f"{summary['final']:.4f}")
        with c3:
            st.metric("Verbesserung", f"{summary['improvement_pct']:.1f}%")
        with c4:
            st.metric("Iterationen", str(summary['iterations']))
        
        # Plot selection
        st.subheader("📊 Visualisierung")
        plot_options = {
            "Konvergenz": "Objektive Funktion über Iterationen",
            "Parameter-Gruppen": "Alle 6 Parameter-Gruppen (faceted)",
            "Soil (1-12)": "Boden-Parameter (Field Capacity, Wilting Point)",
            "Routing (13-20)": "mRM Routing-Parameter (Manning, etc.)",
            "Groundwater (21-30)": "Grundwasser-Parameter",
            "Surface (31-40)": "Oberflächenabfluss-Parameter",
            "ET (41-50)": "Evapotranspiration-Parameter",
            "Snow (51-54)": "Schnee/Niederschlag-Parameter"
        }
        
        selected_plot = st.selectbox("Plot-Typ", options=list(plot_options.keys()))
        
        # Render plots
        if selected_plot == "Konvergenz":
            fig = create_convergence_plot(df, f"{selected} - Konvergenz")
            st.plotly_chart(fig, use_container_width=True)
            
            st.info(
                f"**Konvergenz-Analyse ({selected}):**\n"
                f"- Start: {summary['initial']:.4f}\n"
                f"- Ende: {summary['final']:.4f}\n"
                f"- Verbesserung: {summary['improvement_pct']:.1f}%\n"
                f"- Iterationen: {summary['iterations']}"
            )
        
        elif selected_plot == "Parameter-Gruppen":
            fig = create_faceted_parameter_groups(df)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Abb.: Evolution aller 6 Parameter-Gruppen über 200 Iterationen.")
        
        else:
            # Get group indices
            for group_name, param_indices in PARAM_GROUPS.items():
                if selected_plot.startswith(group_name.split()[0]):
                    fig = create_parameter_group_evolution(df, group_name, param_indices)
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption(f"Abb.: {group_name} — Parameter-Evolution.")
                    break
        
        # Final parameters table
        nml_path = Path(path).parent / 'FinalParam.nml'
        if nml_path.exists():
            st.divider()
            st.subheader("📋 Finale Parameter (Top 20)")
            
            final_params = parse_final_param_nml(nml_path)
            param_list = list(final_params.items())[:20]
            
            param_df = pd.DataFrame(param_list, columns=['Parameter', 'Value'])
            st.dataframe(param_df, height=400, use_container_width=True)
        
        # Final metrics
        out_path = Path(path).parent / 'FinalParam.out'
        if out_path.exists():
            st.divider()
            st.subheader("📊 Modell-Performance (FinalParam)")
            
            final_metrics = parse_final_param_out(out_path)
            
            if final_metrics:
                metrics_df = pd.DataFrame(
                    list(final_metrics.items()),
                    columns=['Metrik', 'Wert']
                )
                st.dataframe(metrics_df, height=300, use_container_width=True)
    
    else:
        # Multi-calcation comparison
        st.subheader("🔬 Vergleich: Mehrere Einzugsgebiete")
        
        results = [parse_dds_results(path, name) for name, path in existing]
        
        # Comparison metrics
        st.markdown("### Zusammenfassung")
        
        comp_df = pd.DataFrame([
            {
                'Catchment': r['name'],
                'Iterationen': r['iterations'],
                'Parameter': r['n_params'],
                'Start': f"{r['df']['objective'].iloc[0]:.4f}",
                'Ende': f"{r['df']['objective'].iloc[-1]:.4f}",
                'Verbesserung': f"{((r['df']['objective'].iloc[0] - r['df']['objective'].iloc[-1]) / r['df']['objective'].iloc[0] * 100):.1f}%"
            }
            for r in results
        ])
        
        st.dataframe(comp_df, use_container_width=True)
        
        # Convergence comparison plot
        st.subheader("📈 Konvergenz-Vergleich")
        fig = create_convergence_comparison(results)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "**Interpretation:**\n"
            "- Unterschiedliche Start-Ziele: Reflektiert initiale Parameter-Unsicherheit\n"
            "- Konvergenz-Rate: Zeigt Komplexität des Catchments\n"
            "- Finale Ziele: Vergleichbare Modell-Performance?"
        )
        
        # Parameter comparison
        st.subheader("📋 Parameter-Vergleich")
        fig = create_parameter_comparison_table(results)
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics comparison
        st.subheader("📊 Performance-Vergleich")
        fig = create_metrics_comparison_table(results)
        st.plotly_chart(fig, use_container_width=True)
    
    # Scientific info
    st.divider()
    with st.expander("📖 DDS Methodik & Erklärung"):
        st.markdown(
            """
### 🔬 Dynamically Dimensioned Search (DDS)

**Algorithmus:** Globale Optimierung für hydrologische Modelle

**Prinzip:**
1. **Start:** Alle Parameter aktiv (volle Dimension)
2. **Iteration:** Zufällige Perturbation mit Normalverteilung N(0, σ²)
3. **Reduktion:** Dimensionalität reduziert sich über Zeit
4. **Akzeptanz:** Nur Verbesserungen werden übernommen

**Parameter:**
- `nIterationen`: 200 (Standard für mHM)
- `nParameter`: 54 (mhm_parameter.nml)
- `r` (DDS neighborhood size): 0.2 (Standard)
- `iseed`: 1235876 (Reproduzierbarkeit)

**Zielfunktion:**
- **KGE-basiert** (Kling-Gupta Efficiency)
- **Multi-Objective:** Qobs vs Qsim
- **Minimierung:** Lower = Better

**Konvergenz:**
- < 5% Verbesserung über 20 Iterationen
- ODER: Maximum Iterationen erreicht

---

### 📊 Parameter-Gruppen (mHM 5.13.2)

| Gruppe | Parameter | Beschreibung |
|--------|-----------|--------------|
| **Soil** | 1-12 | Boden-Speicher (FC, WP für 3 Schichten) |
| **Routing** | 13-20 | mRM Routing (Manning, Fließgeschwindigkeit) |
| **Groundwater** | 21-30 | Grundwasser (Recession constants) |
| **Surface** | 31-40 | Oberflächenabfluss (Runoff coefficients) |
| **ET** | 41-50 | Evapotranspiration (Temp-Korrektur, etc.) |
| **Snow** | 51-54 | Schnee/Niederschlag (Korrektur, Thresholds) |

---

### 🎯 Interpretation der Kalibrierung

**Gute Konvergenz:**
- > 50% Verbesserung über 200 Iterationen
- Stabile Parameter nach Iteration 150
- KGE > 0.5 (akzeptabel), > 0.7 (gut)

**Schlechte Konvergenz:**
- < 20% Verbesserung
- Oszillierende Parameter
- KGE < 0.3 (Problem mit Modell/Data)

**Catchment-Vergleich:**
- Ähnliche finale Ziele → Konsistente Kalibrierung
- Unterschiedliche Parameter → Catchment-spezifische Prozesse
            """
        )
    
    # Download
    st.divider()
    st.subheader("💾 Export")
    
    if mode == "Einzel-Catchment":
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📥 DDS Results CSV",
            data=csv_data.encode("utf-8"),
            file_name=f"{selected}_dds_results.csv",
            mime="text/csv"
        )
    else:
        # Export comparison
        comp_csv = comp_df.to_csv(index=False)
        st.download_button(
            "📥 Vergleich CSV",
            data=comp_csv.encode("utf-8"),
            file_name="dds_catchment_comparison.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    # Test single
    parthe_path = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"
    result = analyze_single_dds(parthe_path)
    print(f"✅ Single: {len(result['figures'])} figures")
    
    # Test multi
    paths = [
        (parthe_path, "Parthe_0p0625"),
        ("/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/goeltzsch2_0p0625/dds_results.out", "Goeltzsch2_0p0625")
    ]
    result = analyze_multiple_dds(paths)
    print(f"✅ Multi: {len(result['figures'])} figures")
