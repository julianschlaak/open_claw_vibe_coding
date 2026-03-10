"""
Scientific discharge visualization for Chemnitz2 catchment.
Hydrograph, flow duration, residuals, metrics timeseries.

Modern Design (2025):
- Colorblind-safe palette (Okabe-Ito)
- Multi-panel layout with context (precip, SMI)
- Enhanced hover tooltips
- Threshold annotations (Q10, Q90)
- Model metrics in title
"""

from typing import Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# COLOR PALETTES (Colorblind-Safe, Okabe-Ito)
# =============================================================================
COLORS = {
    'blue': '#1f77b4',      # Primary (Qobs)
    'orange': '#ff7f0e',    # Secondary (Qsim)
    'green': '#2ca02c',     # Precipitation, positive
    'red': '#d62728',       # Drought, negative
    'purple': '#9467bd',    # SMI
    'brown': '#8c564b',     # Additional
    'pink': '#e377c2',      # Additional
    'gray': '#7f7f7f',      # Neutral
    'cyan': '#17becf',      # Additional
}

# Drought/Flood shading
DROUGHT_COLOR = 'rgba(214, 39, 40, 0.12)'
FLOOD_COLOR = 'rgba(44, 160, 44, 0.12)'


def load_chemnitz2_discharge() -> pd.DataFrame:
    """Load Chemnitz2 discharge data (Qobs, Qsim, indices)."""
    df = pd.read_csv(
        "/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/Chemnitz2_0p0625/drought_indices.csv",
        parse_dates=["date"]
    )
    return df


def create_hydrograph(df: pd.DataFrame, start_date: str = "2018-01-01", end_date: str = "2020-12-31", 
                      include_precip: bool = True) -> go.Figure:
    """
    Modern hydrograph with multi-panel layout:
    - Panel 1: Qobs vs Qsim with drought/flood shading
    - Panel 2: Precipitation (optional)
    - Panel 3: Soil Moisture Index (SMI)
    
    Features:
    - Colorblind-safe palette (Okabe-Ito)
    - Enhanced hover tooltips with difference
    - Threshold annotations (Q10, Q90)
    - Model metrics in title (KGE, NSE)
    - Drought/flood period shading
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with date, qobs, qsim, smi, precip (optional) columns
    start_date : str
        Start date for visualization
    end_date : str
        End date for visualization
    include_precip : bool
        Whether to include precipitation panel
    """
    df = df.copy()
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].reset_index(drop=True)
    
    # Calculate metrics for title
    metrics = calculate_metrics(df)
    kge_str = f"{metrics.get('KGE', 0):.2f}"
    nse_str = f"{metrics.get('NSE', 0):.2f}"
    
    # Calculate thresholds (Q10, Q90)
    q10 = df["qobs"].quantile(0.10)
    q90 = df["qobs"].quantile(0.90)
    
    # Determine number of rows
    if include_precip and "precip" in df.columns:
        n_rows = 3
        row_heights = [0.50, 0.25, 0.25]
        subplot_titles = [
            f"Discharge [m³/s] — KGE: {kge_str} | NSE: {nse_str}",
            "Precipitation [mm/day]",
            "Soil Moisture Index (SMI) [-]"
        ]
    else:
        n_rows = 2
        row_heights = [0.65, 0.35]
        subplot_titles = [
            f"Discharge [m³/s] — KGE: {kge_str} | NSE: {nse_str}",
            "Soil Moisture Index (SMI) [-]"
        ]
    
    # Create subplots
    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights,
        subplot_titles=subplot_titles
    )
    
    # ==========================================================================
    # ROW 1: HYDROGRAPH
    # ==========================================================================
    
    # Calculate difference for tooltip
    df["diff"] = df["qobs"] - df["qsim"]
    
    # Qobs (Observed)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["qobs"],
            name="Qobs (CAMELS-DE)",
            line=dict(color=COLORS['blue'], width=2.5),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Qobs: %{y:.2f} m³/s<br>"
                "Qsim: %{customdata:.2f} m³/s<br>"
                "Diff: %{text:.2f} m³/s<extra></extra>"
            ),
            customdata=df["qsim"],
            text=df["diff"]
        ),
        row=1, col=1
    )
    
    # Qsim (Simulated)
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["qsim"],
            name="Qsim (mHM 5.13.2)",
            line=dict(color=COLORS['orange'], width=2, dash='dash'),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Qsim: %{y:.2f} m³/s<br>"
                "Qobs: %{customdata:.2f} m³/s<br>"
                "Diff: %{text:.2f} m³/s<extra></extra>"
            ),
            customdata=df["qobs"],
            text=df["diff"]
        ),
        row=1, col=1
    )
    
    # Q10 threshold (low-flow)
    fig.add_hline(
        y=q10,
        line_dash="dash",
        line_color=COLORS['red'],
        line_width=1.5,
        annotation_text=f"Q10 (Low-flow: {q10:.2f} m³/s)",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['red'],
        row=1, col=1
    )
    
    # Q90 threshold (high-flow)
    fig.add_hline(
        y=q90,
        line_dash="dash",
        line_color=COLORS['green'],
        line_width=1.5,
        annotation_text=f"Q90 (High-flow: {q90:.2f} m³/s)",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['green'],
        row=1, col=1
    )
    
    # Drought shading (SMI < 20)
    drought_mask = df["smi"] < 20
    drought_periods = _find_contiguous_periods(df["date"], drought_mask)
    
    for start_d, end_d in drought_periods:
        fig.add_vrect(
            x0=start_d, x1=end_d,
            fillcolor=DROUGHT_COLOR,
            opacity=1,
            layer="below",
            line_width=0,
            row=1, col=1
        )
    
    # Flood shading (SMI > 80) - optional
    flood_mask = df["smi"] > 80
    flood_periods = _find_contiguous_periods(df["date"], flood_mask)
    
    for start_d, end_d in flood_periods:
        fig.add_vrect(
            x0=start_d, x1=end_d,
            fillcolor=FLOOD_COLOR,
            opacity=1,
            layer="below",
            line_width=0,
            row=1, col=1
        )
    
    # Add drought annotation as a separate trace (legend only)
    fig.add_trace(
        go.Scatter(
            x=[None], y=[None],
            mode='markers',
            name='Drought period (SMI < 20)',
            marker=dict(color=COLORS['red'], size=10, opacity=0.3),
            showlegend=True
        )
    )
    
    # ==========================================================================
    # ROW 2: PRECIPITATION (if available)
    # ==========================================================================
    if include_precip and "precip" in df.columns:
        fig.add_trace(
            go.Bar(
                x=df["date"],
                y=df["precip"],
                name="Precipitation",
                marker_color=COLORS['green'],
                opacity=0.7,
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Precip: %{y:.1f} mm<extra></extra>"
            ),
            row=2, col=1
        )
        fig.update_yaxes(title_text="Precip [mm/day]", row=2, col=1)
        smi_row = 3
    else:
        smi_row = 2
    
    # ==========================================================================
    # ROW (2 or 3): SMI
    # ==========================================================================
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["smi"],
            name="SMI",
            line=dict(color=COLORS['purple'], width=2),
            fill="tozeroy",
            fillcolor="rgba(148, 103, 189, 0.2)",
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>SMI: %{y:.1f}<extra></extra>"
        ),
        row=smi_row, col=1
    )
    
    # SMI drought threshold
    fig.add_hline(
        y=20,
        line_dash="dash",
        line_color=COLORS['red'],
        line_width=1.5,
        annotation_text="Drought threshold (20)",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['red'],
        row=smi_row, col=1
    )
    
    # SMI wet threshold
    fig.add_hline(
        y=80,
        line_dash="dash",
        line_color=COLORS['green'],
        line_width=1.5,
        annotation_text="Wet threshold (80)",
        annotation_position="right",
        annotation_font_size=10,
        annotation_font_color=COLORS['green'],
        row=smi_row, col=1
    )
    
    # ==========================================================================
    # LAYOUT (DARK THEME for better readability)
    # ==========================================================================
    fig.update_layout(
        height=700 if include_precip else 600,
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
        margin=dict(l=60, r=80, t=80, b=40),
        plot_bgcolor="rgba(30, 30, 30, 1)",
        paper_bgcolor="rgba(30, 30, 30, 1)",
        font=dict(color="#ffffff", size=11),
        title=dict(
            font=dict(color="#ffffff", size=14, weight="bold")
        )
    )
    
    # Update title color
    fig.update_layout(
        title_font_color="#ffffff",
        title_font_size=14
    )
    
    # X-axis (dark theme)
    fig.update_xaxes(
        tickformat="%Y-%m",
        ticklabelmode="period",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.1)",
        tickcolor="rgba(255, 255, 255, 0.3)",
        linecolor="rgba(255, 255, 255, 0.3)",
        title_font_color="#ffffff",
        tickfont_color="#ffffff",
        row=n_rows, col=1
    )
    
    # Y-axes (dark theme)
    for row in range(1, n_rows + 1):
        fig.update_yaxes(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.1)",
            zeroline=True,
            zerolinecolor="rgba(255, 255, 255, 0.2)",
            linecolor="rgba(255, 255, 255, 0.3)",
            title_font_color="#ffffff",
            tickfont_color="#ffffff",
            row=row, col=1
        )
    
    return fig


def _find_contiguous_periods(dates: pd.Series, mask: pd.Series) -> list:
    """
    Find contiguous periods where mask is True.
    
    Returns
    -------
    list of tuples: [(start_date_str, end_date_str), ...]
    """
    periods = []
    in_period = False
    start = None
    
    for i, (date, is_active) in enumerate(zip(dates, mask)):
        if is_active and not in_period:
            start = date
            in_period = True
        elif not is_active and in_period:
            # Convert to string for Plotly compatibility
            periods.append((
                start.strftime("%Y-%m-%d"),
                dates.iloc[i-1].strftime("%Y-%m-%d")
            ))
            in_period = False
    
    if in_period:
        periods.append((
            start.strftime("%Y-%m-%d"),
            dates.iloc[-1].strftime("%Y-%m-%d")
        ))
    
    return periods


def create_flow_duration_curve(df: pd.DataFrame) -> go.Figure:
    """
    Flow duration curve: Exceedance probability vs discharge.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with qobs, qsim columns
    """
    df = df.copy()
    
    # Sort by discharge (descending)
    qobs_sorted = np.sort(df["qobs"].dropna())[::-1]
    qsim_sorted = np.sort(df["qsim"].dropna())[::-1]
    
    # Exceedance probability (Weibull plotting position)
    n_obs = len(qobs_sorted)
    n_sim = len(qsim_sorted)
    
    prob_obs = (np.arange(1, n_obs + 1) - 0.3) / (n_obs + 0.4) * 100
    prob_sim = (np.arange(1, n_sim + 1) - 0.3) / (n_sim + 0.4) * 100
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=prob_obs,
            y=qobs_sorted,
            mode="lines",
            name="Qobs (CAMELS-DE)",
            line=dict(color="#1f77b4", width=2)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=prob_sim,
            y=qsim_sorted,
            mode="lines",
            name="Qsim (mHM 5.13.2)",
            line=dict(color="#ff7f0e", width=2, dash="dash")
        )
    )
    
    # Layout: log-scale y-axis
    fig.update_layout(
        title="Flow Duration Curve - Chemnitz2 (2005-2020)",
        xaxis_title="Exceedance Probability [%]",
        yaxis_title="Discharge [m³/s]",
        yaxis_type="log",
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"),
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="lightgray")
    
    return fig


def create_residual_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Residual analysis: Qobs - Qsim distribution and timeseries.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with date, qobs, qsim columns
    """
    df = df.copy()
    df["residual"] = df["qobs"] - df["qsim"]
    
    # Create subplots: 2 rows (timeseries + histogram)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.08,
        row_heights=[0.5, 0.5],
        subplot_titles=("Residual Timeseries (Qobs - Qsim)", "Residual Distribution")
    )
    
    # Row 1: Residual timeseries
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["residual"],
            mode="lines",
            name="Residual",
            line=dict(color="#2ca02c", width=1),
            fill="tozeroy"
        ),
        row=1, col=1
    )
    
    # Zero line
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=1, col=1)
    
    # Row 2: Histogram
    fig.add_trace(
        go.Histogram(
            x=df["residual"],
            name="Residuals",
            nbinsx=50,
            marker_color="#2ca02c",
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Mean residual line
    mean_res = df["residual"].mean()
    fig.add_vline(
        x=mean_res,
        line_dash="dash",
        line_color="#d62728",
        annotation_text=f"Mean: {mean_res:.2f} m³/s",
        row=2, col=1
    )
    
    # Layout
    fig.update_layout(
        height=600,
        showlegend=False,
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    fig.update_xaxes(title_text="Date", row=1, col=1)
    fig.update_yaxes(title_text="Residual [m³/s]", row=1, col=1)
    fig.update_xaxes(title_text="Residual [m³/s]", row=2, col=1)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    
    return fig


def calculate_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate hydrological performance metrics.
    
    Returns
    -------
    dict
        KGE, NSE, r, PBIAS, RMSE, MAE
    """
    qobs = df["qobs"].values
    qsim = df["qsim"].values
    
    # Remove NaN
    mask = ~(np.isnan(qobs) | np.isnan(qsim))
    qobs = qobs[mask]
    qsim = qsim[mask]
    
    if len(qobs) == 0:
        return {}
    
    # Basic statistics
    mu_obs = np.mean(qobs)
    mu_sim = np.mean(qsim)
    sigma_obs = np.std(qobs, ddof=1)
    sigma_sim = np.std(qsim, ddof=1)
    
    # Pearson correlation
    r = np.corrcoef(qobs, qsim)[0, 1]
    
    # NSE
    nse = 1 - np.sum((qsim - qobs) ** 2) / np.sum((qobs - mu_obs) ** 2)
    
    # KGE (Gupta et al., 2009)
    cc = r
    alpha = sigma_sim / sigma_obs if sigma_obs > 0 else 0
    beta = mu_sim / mu_obs if mu_obs > 0 else 0
    kge = 1 - np.sqrt((cc - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    
    # PBIAS
    pbias = 100 * (np.sum(qsim) - np.sum(qobs)) / np.sum(qobs)
    
    # RMSE, MAE
    rmse = np.sqrt(np.mean((qsim - qobs) ** 2))
    mae = np.mean(np.abs(qsim - qobs))
    
    return {
        "KGE": kge,
        "NSE": nse,
        "r": r,
        "PBIAS": pbias,
        "RMSE": rmse,
        "MAE": mae,
        "alpha": alpha,
        "beta": beta
    }


def create_metrics_panel(df: pd.DataFrame) -> go.Figure:
    """
    Create a panel showing KGE decomposition and metrics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with qobs, qsim columns
    """
    metrics = calculate_metrics(df)
    
    if not metrics:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    # Create bar chart for KGE components
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("KGE Decomposition", "Performance Metrics"),
        specs=[[{"type": "bar"}, {"type": "table"}]]
    )
    
    # KGE components (cc, alpha, beta)
    kge_components = {
        "Correlation (r)": metrics.get("r", 0),
        "Variability (α)": metrics.get("alpha", 0),
        "Bias (β)": metrics.get("beta", 0)
    }
    
    fig.add_trace(
        go.Bar(
            x=list(kge_components.values()),
            y=list(kge_components.keys()),
            orientation="h",
            name="Component",
            marker_color=["#1f77b4", "#ff7f0e", "#2ca02c"],
            text=[f"{v:.3f}" for v in kge_components.values()],
            textposition="auto"
        ),
        row=1, col=1
    )
    
    # Perfect value line (1.0)
    fig.add_vline(x=1.0, line_dash="dash", line_color="gray", row=1, col=1)
    
    # Metrics table
    metrics_table = {
        "Metric": ["KGE", "NSE", "r (Pearson)", "PBIAS [%]", "RMSE [m³/s]", "MAE [m³/s]"],
        "Value": [
            f"{metrics.get('KGE', 0):.3f}",
            f"{metrics.get('NSE', 0):.3f}",
            f"{metrics.get('r', 0):.3f}",
            f"{metrics.get('PBIAS', 0):.2f}",
            f"{metrics.get('RMSE', 0):.3f}",
            f"{metrics.get('MAE', 0):.3f}"
        ],
        "Rating": [
            "Good" if metrics.get("KGE", 0) > 0.5 else "Poor",
            "Good" if metrics.get("NSE", 0) > 0.5 else "Poor",
            "Strong" if metrics.get("r", 0) > 0.7 else "Moderate",
            "Low" if abs(metrics.get("PBIAS", 0)) < 10 else "High",
            "-",
            "-"
        ]
    }
    
    fig.add_trace(
        go.Table(
            header=dict(
                values=["<b>Metric</b>", "<b>Value</b>", "<b>Rating</b>"],
                fill_color="#1f77b4",
                align="left",
                font=dict(color="white", size=12)
            ),
            cells=dict(
                values=[metrics_table["Metric"], metrics_table["Value"], metrics_table["Rating"]],
                fill_color="white",
                align="left",
                font=dict(size=11)
            )
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_xaxes(title_text="Value [-]", row=1, col=1)
    fig.update_xaxes(range=[0, 1.5], row=1, col=1)
    
    return fig


def create_low_flow_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Low-flow analysis: Q7Q10, drought events.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with date, qobs, qsim columns
    """
    df = df.copy()
    
    # 7-day moving average
    df["qobs_7d"] = df["qobs"].rolling(window=7, min_periods=1).mean()
    df["qsim_7d"] = df["qsim"].rolling(window=7, min_periods=1).mean()
    
    # Find low-flow events (Q < Q10, where Q10 = 10th percentile)
    q10_obs = df["qobs"].quantile(0.10)
    q10_sim = df["qsim"].quantile(0.10)
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.4],
        subplot_titles=("7-day Moving Average Discharge", "Low-Flow Events Identification")
    )
    
    # Row 1: 7-day MA
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["qobs_7d"],
            mode="lines",
            name="Qobs 7d-MA",
            line=dict(color="#1f77b4", width=1.5)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["qsim_7d"],
            mode="lines",
            name="Qsim 7d-MA",
            line=dict(color="#ff7f0e", width=1.2, dash="dash")
        ),
        row=1, col=1
    )
    
    # Q10 threshold
    fig.add_hline(
        y=q10_obs,
        line_dash="dash",
        line_color="#d62728",
        annotation_text=f"Q10 (obs): {q10_obs:.2f} m³/s",
        row=1, col=1
    )
    
    # Row 2: Low-flow indicator
    low_flow_obs = (df["qobs_7d"] < q10_obs).astype(int)
    
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=low_flow_obs * 100,
            mode="lines",
            name="Low-flow (Q < Q10)",
            line=dict(color="#d62728", width=1),
            fill="tozeroy"
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top"),
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Discharge [m³/s]", row=1, col=1)
    fig.update_yaxes(title_text="Low-flow indicator [%]", range=[-10, 110], row=2, col=1)
    
    return fig


def create_seasonal_discharge_plot(df: pd.DataFrame) -> go.Figure:
    """
    Seasonal discharge patterns: monthly boxplots.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with date, qobs, qsim columns
    """
    df = df.copy()
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    # Prepare data for boxplots
    qobs_by_month = [df[df["month"] == i+1]["qobs"].dropna().values for i in range(12)]
    qsim_by_month = [df[df["month"] == i+1]["qsim"].dropna().values for i in range(12)]
    
    fig = go.Figure()
    
    # Observed boxplots
    for i, month in enumerate(months):
        fig.add_trace(
            go.Box(
                y=qobs_by_month[i],
                name=month,
                marker_color="#1f77b4",
                opacity=0.7,
                showlegend=False
            )
        )
    
    # Simulated boxplots (offset)
    for i, month in enumerate(months):
        fig.add_trace(
            go.Box(
                y=qsim_by_month[i],
                name=f"{month} (sim)",
                marker_color="#ff7f0e",
                opacity=0.5,
                showlegend=False
            )
        )
    
    fig.update_layout(
        title="Seasonal Discharge Patterns - Chemnitz2 (2005-2020)",
        xaxis_title="Month",
        yaxis_title="Discharge [m³/s]",
        height=500,
        margin=dict(l=60, r=40, t=60, b=50)
    )
    
    fig.update_xaxes(ticktext=months, tickvals=list(range(1, 25, 2)))
    
    return fig
