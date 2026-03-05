from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_timeseries_plot(df: pd.DataFrame, x: str, y: str, title: str, y_label: str, height: int = 330):
    fig = px.line(df, x=x, y=y, title=title, labels={x: "Date", y: y_label})
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=16, r=12, t=42, b=18),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.45)",
        title=dict(font=dict(size=18)),
    )
    fig.update_traces(line=dict(width=2.2))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.25)")
    return fig


def create_multiindex_timeseries(df: pd.DataFrame, date_col: str = "date"):
    cols = [c for c in ["smi", "r_pctl", "q_pctl", "mdi"] if c in df.columns]
    x = df[[date_col] + cols].copy()
    x[date_col] = pd.to_datetime(x[date_col])
    x = x.groupby(date_col, as_index=False).mean()
    fig = px.line(x, x=date_col, y=cols, title="Multi-Index Time Series", labels={"value": "Index (0-100)", date_col: "Date"})
    fig.update_layout(template="plotly_white", height=430)
    return fig


def create_radar_plot(values: dict):
    theta = list(values.keys())
    r = list(values.values())
    theta.append(theta[0])
    r.append(r[0])

    fig = go.Figure(
        data=[go.Scatterpolar(r=r, theta=theta, fill="toself", line=dict(color="#1f6f8b", width=2))]
    )
    fig.update_layout(
        title="Radar: Multi-Index Comparison",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template="plotly_white",
        height=430,
    )
    return fig


def create_corr_heatmap(df: pd.DataFrame, cols: list[str]):
    corr = df[cols].corr()
    fig = px.imshow(corr, labels=dict(x="Index", y="Index", color="Correlation"), color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    fig.update_layout(template="plotly_white", title="Correlation Matrix", height=430)
    return fig


def classify_smi(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    out = pd.Series("normal", index=x.index)
    out[x < 20] = "mild_drought"
    out[x < 10] = "moderate_drought"
    out[x < 5] = "severe_drought"
    out[x < 2] = "extreme_drought"
    return out


def summary_stats(s: pd.Series) -> dict:
    v = pd.to_numeric(s, errors="coerce")
    return {
        "mean": float(v.mean()),
        "std": float(v.std()),
        "min": float(v.min()),
        "max": float(v.max()),
        "median": float(v.median()),
        "count": int(v.count()),
    }
