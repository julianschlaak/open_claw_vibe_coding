"""
Scientific DDS Calibration Analysis for mHM Re-Crit (Parthe_0p0625)

Analyzes DDS (Dynamically Dimensioned Search) optimization results:
- Convergence plots
- Parameter evolution
- Parallel coordinates
- Final parameter set analysis
- Performance metrics

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
# DDS RESULTS PARSING
# =============================================================================

def parse_dds_results(filepath: str) -> pd.DataFrame:
    """
    Parse dds_results.out file.
    
    Format:
    # iter   bestf   (bestx(j),j=1,nopt)
    0   1.2848...   0.3658... 1.3110... ...
    
    Returns
    -------
    pd.DataFrame
        Columns: iteration, objective, param_1, param_2, ..., param_54
    """
    rows = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines (start with #)
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
    
    return pd.DataFrame(rows)


def parse_final_param_nml(filepath: str) -> Dict[str, float]:
    """
    Parse FinalParam.nml (mhm_parameter.nml format).
    
    Extracts parameter names and values.
    """
    params = {}
    
    with open(filepath, 'r', encoding='latin-1') as f:
        content = f.read()
    
    # Pattern: parameter_name = value
    pattern = r'(\w+)\s*=\s*([\d.E+-]+)'
    matches = re.findall(pattern, content)
    
    for name, value in matches:
        try:
            params[name] = float(value)
        except ValueError:
            pass
    
    return params


def parse_final_param_out(filepath: str) -> Dict[str, float]:
    """
    Parse FinalParam.out (model performance metrics).
    
    Expected metrics: KGE, NSE, r, PBIAS, etc.
    """
    metrics = {}
    
    with open(filepath, 'r') as f:
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

def create_convergence_plot(df: pd.DataFrame, title: str = "DDS Convergence") -> go.Figure:
    """
    Plot objective function value over iterations.
    """
    fig = go.Figure()
    
    # Best objective value
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
    
    # Improvement annotations
    initial_obj = df['objective'].iloc[0]
    final_obj = df['objective'].iloc[-1]
    improvement = ((initial_obj - final_obj) / initial_obj) * 100
    
    fig.add_annotation(
        x=len(df) // 2,
        y=final_obj,
        text=f"Improvement: {improvement:.1f}%",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#1f77b4",
        borderwidth=1
    )
    
    # Layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14, weight='bold', color='#ffffff')
        ),
        height=400,
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
        margin=dict(l=60, r=40, t=80, b=50),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11)
    )
    
    fig.update_xaxes(
        title_text="Iteration",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickcolor="rgba(255, 255, 255, 0.3)",
        linecolor="rgba(255, 255, 255, 0.3)"
    )
    
    fig.update_yaxes(
        title_text="Objective Function [-]",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.1)",
        zeroline=True,
        zerolinecolor="rgba(255, 255, 255, 0.2)",
        linecolor="rgba(255, 255, 255, 0.3)"
    )
    
    return fig


def create_parameter_evolution_plot(df: pd.DataFrame, n_params: int = 10) -> go.Figure:
    """
    Plot evolution of top N parameters over iterations.
    """
    # Select first N parameters (or most important ones)
    param_cols = [f'param_{i:02d}' for i in range(1, n_params + 1)]
    
    fig = make_subplots(
        rows=5, cols=2,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=[f"Param {i:02d}" for i in range(1, n_params + 1)]
    )
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, col in enumerate(param_cols):
        row = (i // 2) + 1
        c = (i % 2) + 1
        
        fig.add_trace(
            go.Scatter(
                x=df['iteration'],
                y=df[col],
                mode='lines',
                name=f"Param {i+1:02d}",
                line=dict(color=colors[i], width=1.5),
                showlegend=False
            ),
            row=row, col=c
        )
    
    fig.update_layout(
        height=800,
        showlegend=False,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=60, b=40),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=10)
    )
    
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255, 255, 255, 0.1)")
    
    return fig


def create_parallel_coordinates_plot(df: pd.DataFrame, final_iter: int = -1) -> go.Figure:
    """
    Parallel coordinates plot showing parameter changes from initial to final.
    """
    initial = df.iloc[0]
    final = df.iloc[final_iter]
    
    # Select key parameters (first 20)
    param_cols = [f'param_{i:02d}' for i in range(1, 21)]
    
    dimensions = []
    for col in param_cols:
        dimensions.append(dict(
            range=[float(df[col].min()), float(df[col].max())],
            label=f"P{col[-2:]}",
            values=[float(final[col])]
        ))
    
    fig = go.Figure(data=
        go.Parcoords(
            line=dict(
                color='#1f77b4',
                colorscale='Viridis',
                showscale=False,
                cmin=0,
                cmax=1
            ),
            dimensions=dimensions
        )
    )
    
    fig.update_layout(
        title="Final Parameter Set (Parallel Coordinates)",
        height=400,
        font=dict(color="#ffffff", size=11),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


def create_parameter_distribution_plot(df: pd.DataFrame) -> go.Figure:
    """
    Box plot showing parameter distributions across all iterations.
    """
    param_cols = [c for c in df.columns if c.startswith('param_')]
    
    # Select first 30 parameters for readability
    param_cols = param_cols[:30]
    
    fig = go.Figure()
    
    for col in param_cols:
        fig.add_trace(
            go.Box(
                y=df[col],
                name=col[-2:],
                boxpoints='outliers',
                marker_size=3,
                opacity=0.7
            )
        )
    
    fig.update_layout(
        title="Parameter Distributions (All Iterations)",
        height=500,
        showlegend=False,
        template="plotly_dark",
        margin=dict(l=60, r=40, t=60, b=80),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=10)
    )
    
    fig.update_xaxes(title_text="Parameter")
    fig.update_yaxes(title_text="Value [-]")
    
    return fig


def create_improvement_summary(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate improvement metrics.
    """
    initial = df['objective'].iloc[0]
    final = df['objective'].iloc[-1]
    best = df['objective'].min()
    
    # Find when significant improvement occurred
    threshold = initial * 0.5  # 50% improvement
    iter_50 = df[df['objective'] <= threshold]['iteration'].iloc[0] if len(df[df['objective'] <= threshold]) > 0 else None
    
    return {
        'initial': initial,
        'final': final,
        'best': best,
        'improvement_abs': initial - final,
        'improvement_pct': ((initial - final) / initial) * 100,
        'iterations': len(df),
        'iter_50_pct': iter_50
    }


def create_dashboard_summary_card(df: pd.DataFrame, metrics: Optional[Dict] = None) -> go.Figure:
    """
    Create a summary card with key metrics for dashboard display.
    """
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
            title={'text': "Objective Improvement", 'font': {'size': 14, 'color': '#ffffff'}},
            number={'font': {'size': 40, 'color': '#1f77b4'}}
        ),
        row=1, col=1
    )
    
    # Table: Key metrics
    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Metric</b>", "<b>Value</b>"],
                fill_color="#1f77b4",
                align="left",
                font=dict(color="white", size=12)
            ),
            cells=dict(
                values=[
                    ["Initial Objective", "Final Objective", "Best Objective", "Improvement", "Iterations"],
                    [f"{summary['initial']:.4f}", f"{summary['final']:.4f}", f"{summary['best']:.4f}", f"{summary['improvement_pct']:.1f}%", str(summary['iterations'])]
                ],
                fill_color="rgba(30, 30, 30, 0.8)",
                align="left",
                font=dict(size=11, color="#ffffff")
            )
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor="rgba(30, 30, 30, 1)",
        plot_bgcolor="rgba(30, 30, 30, 1)"
    )
    
    return fig


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_dds_calibration(
    dds_results_path: str,
    final_param_nml_path: Optional[str] = None,
    final_param_out_path: Optional[str] = None,
    title: str = "Parthe_0p0625 DDS Calibration"
) -> Dict[str, go.Figure]:
    """
    Complete DDS calibration analysis.
    
    Parameters
    ----------
    dds_results_path : str
        Path to dds_results.out
    final_param_nml_path : str, optional
        Path to FinalParam.nml
    final_param_out_path : str, optional
        Path to FinalParam.out
    title : str
        Plot title
    
    Returns
    -------
    dict
        Dictionary of plotly figures
    """
    # Parse data
    df = parse_dds_results(dds_results_path)
    
    # Create plots
    figures = {
        'convergence': create_convergence_plot(df, title=f"{title} - Convergence"),
        'summary': create_dashboard_summary_card(df),
        'parameter_evolution': create_parameter_evolution_plot(df, n_params=10),
        'parameter_distribution': create_parameter_distribution_plot(df),
    }
    
    # Parse final parameters if available
    if final_param_nml_path and Path(final_param_nml_path).exists():
        final_params = parse_final_param_nml(final_param_nml_path)
        figures['final_params'] = final_params
    
    if final_param_out_path and Path(final_param_out_path).exists():
        final_metrics = parse_final_param_out(final_param_out_path)
        figures['final_metrics'] = final_metrics
    
    return figures


# =============================================================================
# DASHBOARD INTEGRATION
# =============================================================================

def render_dds_analysis_tab():
    """
    Streamlit tab content for DDS analysis.
    """
    import streamlit as st
    
    st.header("🔧 Parthe_0p0625 — DDS Kalibrierungs-Analyse")
    st.markdown(
        "**Dynamically Dimensioned Search (DDS) Optimierung für mHM Re-Crit**\n\n"
        "Catchment: Parthe_0p0625 | Iterationen: 200 | Parameter: 54"
    )
    
    # File paths
    dds_results = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"
    final_nml = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/FinalParam.nml"
    final_out = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/FinalParam.out"
    
    # Load data
    try:
        df = parse_dds_results(dds_results)
        st.success(f"DDS-Daten geladen: {len(df)} Iterationen, 54 Parameter")
    except Exception as e:
        st.error(f"Fehler beim Laden: {e}")
        st.stop()
    
    # Summary metrics
    summary = create_improvement_summary(df)
    
    # Key metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Initiales Ziel", f"{summary['initial']:.4f}")
    with c2:
        st.metric("Finales Ziel", f"{summary['final']:.4f}")
    with c3:
        st.metric("Verbesserung", f"{summary['improvement_pct']:.1f}%")
    with c4:
        st.metric("Iterationen", str(summary['iterations']))
    
    # Plot selection
    st.subheader("📊 Visualisierung")
    plot_options = {
        "Konvergenz": "Objektive Funktion über Iterationen",
        "Parameter-Evolution": "Entwicklung der ersten 10 Parameter",
        "Parameter-Verteilung": "Box-Plots aller Parameter",
        "Parallel Coordinates": "Finale Parameter-Sets"
    }
    
    selected_plot = st.selectbox(
        "Plot-Typ",
        options=list(plot_options.keys()),
        format_func=lambda x: f"{x}"
    )
    
    # Render plots
    if selected_plot == "Konvergenz":
        fig = create_convergence_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "**Konvergenz-Analyse:**\n"
            f"- Start: {summary['initial']:.4f}\n"
            f"- Ende: {summary['final']:.4f}\n"
            f"- Verbesserung: {summary['improvement_pct']:.1f}%"
        )
    
    elif selected_plot == "Parameter-Evolution":
        fig = create_parameter_evolution_plot(df, n_params=10)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Abb.: Entwicklung der ersten 10 Parameter über 200 Iterationen.")
    
    elif selected_plot == "Parameter-Verteilung":
        fig = create_parameter_distribution_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Abb.: Box-Plots der Parameter-Werte (erste 30 Parameter).")
    
    elif selected_plot == "Parallel Coordinates":
        fig = create_parallel_coordinates_plot(df)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Abb.: Parallel Coordinates für finale Parameter (erste 20).")
    
    # Final parameters table
    if Path(final_nml).exists():
        st.divider()
        st.subheader("📋 Finale Parameter (Top 20)")
        
        final_params = parse_final_param_nml(final_nml)
        param_list = list(final_params.items())[:20]
        
        param_df = pd.DataFrame(param_list, columns=['Parameter', 'Value'])
        st.dataframe(param_df, height=400)
    
    # Final metrics
    if Path(final_out).exists():
        st.divider()
        st.subheader("📊 Modell-Performance (FinalParam)")
        
        final_metrics = parse_final_param_out(final_out)
        
        if final_metrics:
            metrics_df = pd.DataFrame(
                list(final_metrics.items()),
                columns=['Metric', 'Value']
            )
            st.dataframe(metrics_df, height=300)
    
    # Scientific info
    with st.expander("📖 DDS Methodik"):
        st.markdown(
            """
### Dynamically Dimensioned Search (DDS)
**Algorithmus:** Globale Optimierung für hydrologische Modelle

**Prinzip:**
- Startet mit allen Parametern (full dimension)
- Reduziert Dimensionalität über Iterationen
- Perturbation mit Normalverteilung
- Akzeptiert nur Verbesserungen

**Parameter:**
- nIterationen: 200
- nParameter: 54 (mhm_parameter.nml)
- r (DDS): 0.2 (Standard)
- iseed: 1235876 (Reproduzierbarkeit)

**Zielfunktion:**
- KGE-basiert (Kling-Gupta Efficiency)
- Multi-Objective: Qobs vs Qsim
- Lower = Better (Minimierung)

**Konvergenz-Kriterien:**
- < 5% Verbesserung über 20 Iterationen
- Oder: Maximum Iterationen erreicht
        """
        )
    
    # Download
    st.divider()
    st.subheader("💾 Export")
    
    csv_data = df.to_csv(index=False)
    st.download_button(
        "📥 DDS Results CSV",
        data=csv_data.encode("utf-8"),
        file_name="parthe_dds_results.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    # Test
    dds_path = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625/dds_results.out"
    figures = analyze_dds_calibration(dds_path)
    print(f"✅ Created {len(figures)} figures")
    print(f"   - convergence: {len(figures['convergence'].data)} traces")
    print(f"   - summary: {len(figures['summary'].data)} traces")
