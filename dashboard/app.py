#!/usr/bin/env python3
from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Dürre-Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / "analysis" / "results"

DOMAINS = {
    "catchment_custom": "Einzugsgebiet 90410700 · 30 Jahre Daten",
    "test_domain": "Test Domain · Kurzserie",
}


@st.cache_data(ttl=600, show_spinner=False)
def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return pd.read_csv(p)


@st.cache_data(ttl=600, show_spinner=False)
def load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))
    return json.loads(p.read_text(encoding="utf-8"))


def status_color(smi: float) -> tuple[str, str]:
    if smi < 20:
        return "#FF4B4B", "🔴 AKTIVE DÜRRE"
    if smi < 40:
        return "#F5A623", "🟡 ERHÖHTE TROCKENHEIT"
    return "#00C851", "🟢 NORMAL"


def kpi_card_html(color: str, title: str, body: str) -> str:
    return f"""
    <div style="
      border:1px solid rgba(255,255,255,0.12);
      border-left:6px solid {color};
      background:#1E1E1E;
      border-radius:12px;
      padding:12px 14px;
      margin:8px 0 12px 0;
      color:#FAFAFA;">
      <div style="font-weight:700;font-size:1.05rem;">{title}</div>
      <div style="margin-top:6px;color:#D0D0D0;">{body}</div>
    </div>
    """


def plot_timeline(monthly: pd.DataFrame, selected_year: Optional[int]) -> Optional[int]:
    annual = monthly.groupby("year", as_index=False)["smi_percent"].mean().rename(columns={"smi_percent": "avg_smi"})
    annual["color"] = np.where(annual["avg_smi"] < 20, "#FF4B4B", np.where(annual["avg_smi"] < 40, "#F5A623", "#00C851"))

    fig = go.Figure(
        data=[
            go.Scatter(
                x=annual["year"],
                y=annual["avg_smi"],
                mode="lines+markers",
                marker=dict(size=11, color=annual["color"], line=dict(width=1, color="#D9D9D9")),
                line=dict(color="#8A8A8A", width=2),
                customdata=annual[["year", "avg_smi"]],
                hovertemplate="Jahr: %{customdata[0]}<br>Ø SMI: %{customdata[1]:.1f}<extra></extra>",
                name="Jahresmittel SMI",
            )
        ]
    )
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=30, b=20),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#FAFAFA"),
        xaxis_title="Jahr",
        yaxis_title="Ø SMI",
        yaxis_range=[0, 100],
    )
    if selected_year:
        fig.add_vline(x=selected_year, line_dash="dash", line_color="#FAFAFA", opacity=0.6)

    try:
        sel = st.plotly_chart(
            fig,
            use_container_width=True,
            key="timeline_v3",
            on_select="rerun",
            selection_mode="points",
            config={"displayModeBar": False, "scrollZoom": False, "responsive": True},
        )
        pts = sel.get("selection", {}).get("points", []) if isinstance(sel, dict) else []
        if pts:
            return int(pts[0].get("x"))
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "scrollZoom": False, "responsive": True})

    return selected_year


def plot_detail_timeseries(monthly: pd.DataFrame, selected_year: Optional[int]) -> go.Figure:
    data = monthly.copy()
    if selected_year is not None:
        data = data[data["year"] == selected_year]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["date"], y=data["smi_percent"], mode="lines+markers", name="SMI", line=dict(color="#FF4B4B", width=2)))
    fig.add_trace(go.Scatter(x=data["date"], y=data["recharge_percent"], mode="lines", name="Recharge", line=dict(color="#00C851", width=2)))
    fig.add_trace(go.Scatter(x=data["date"], y=data["runoff_percent"], mode="lines", name="Runoff", line=dict(color="#5DADE2", width=2)))
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#FAFAFA"),
        hovermode="x unified",
    )
    fig.update_xaxes(rangeslider_visible=True)
    return fig


st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background: #0E1117 !important;
  color: #FAFAFA !important;
}
[data-testid="stHeader"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# Top
col_a, col_b = st.columns([0.68, 0.32])
with col_a:
    st.title("🌍 DÜRRE-MONITOR")
with col_b:
    domain = st.selectbox("Catchment", list(DOMAINS.keys()), index=0)

st.caption(DOMAINS[domain])

# Load data with robust fallback
try:
    monthly = load_csv(str(RESULTS / domain / "monthly_drought_indices.csv"))
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly = monthly.sort_values("date").reset_index(drop=True)
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
except Exception as e:
    st.warning("Daten werden geladen... monthly_drought_indices.csv fehlt oder ist fehlerhaft.")
    st.code(str(e))
    st.stop()

try:
    events = load_csv(str(RESULTS / domain / "drought_events.csv"))
except Exception:
    events = pd.DataFrame(columns=["event_id", "start_date", "end_date", "duration_months", "min_smi", "avg_smi", "severity_score", "max_intensity", "recovery_months"])

try:
    seasonal = load_csv(str(RESULTS / domain / "seasonal_stats.csv"))
except Exception:
    seasonal = pd.DataFrame(columns=["month", "avg_smi", "drought_frequency", "avg_duration", "early_start_pct", "late_end_pct"])

try:
    trend = load_csv(str(RESULTS / domain / "trend_analysis.csv"))
except Exception:
    trend = pd.DataFrame(columns=["metric", "mann_kendall_tau", "p_value", "sens_slope", "trend_per_decade", "significance"])

try:
    ranking = load_json(str(RESULTS / domain / "current_ranking.json"))
except Exception:
    ranking = {}

try:
    warning = load_json(str(RESULTS / domain / "forecast_warning.json"))
except Exception:
    warning = {}

if "selected_year" not in st.session_state:
    st.session_state.selected_year = int(monthly["year"].iloc[-1])

latest = monthly.iloc[-1]
current_smi = float(latest["smi_percent"])
color, status = status_color(current_smi)
rank_driest = ranking.get("rank_driest", "n/a")
rp = ranking.get("return_period", "n/a")

st.markdown(
    kpi_card_html(
        color,
        f"{status} · Seit laufender Beobachtung · SMI: {current_smi:.1f}%",
        f"Rang {rank_driest}. trockenster Monat seit {int(monthly['year'].min())} · Rückkehrperiode: {rp}",
    ),
    unsafe_allow_html=True,
)

# Timeline
st.subheader("📍 30-JAHRES ZEITSTRAHL (Klickbar)")
st.session_state.selected_year = plot_timeline(monthly, st.session_state.selected_year)
selected_year = st.session_state.selected_year
st.caption(f"Ausgewählt: {selected_year}")

# Event table
st.subheader("📊 DÜRRE-EREIGNISSE IN DIESER PERIODE")
events_view = events.copy()
if not events_view.empty:
    events_view["start_year"] = pd.to_datetime(events_view["start_date"]).dt.year
    events_view = events_view[events_view["start_year"] <= selected_year]
    events_view = events_view.sort_values("severity_score", ascending=False)
    show_cols = ["start_date", "end_date", "duration_months", "min_smi", "severity_score", "recovery_months"]
    st.dataframe(events_view[show_cols], use_container_width=True, hide_index=True)
else:
    st.info("Keine Dürre-Ereignisse nach aktueller Regel erkannt.")

with st.expander("▼ MEHR DETAILS ANZEIGEN", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Saisonale Statistik (gefährliche Monate)**")
        if not seasonal.empty:
            season_fig = go.Figure(
                data=[
                    go.Bar(
                        x=seasonal["month"],
                        y=seasonal["drought_frequency"],
                        marker_color="#FF4B4B",
                        name="Drought frequency %",
                    )
                ]
            )
            season_fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                font=dict(color="#FAFAFA"),
                xaxis_title="Monat",
                yaxis_title="Dürre-Häufigkeit [%]",
            )
            st.plotly_chart(season_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        else:
            st.info("Keine saisonalen Statistiken verfügbar.")

    with c2:
        st.markdown("**Trend-Indikator (Mann-Kendall + Sen's Slope)**")
        if not trend.empty:
            tr = trend[trend["metric"].str.lower().eq("drought_frequency")]
            if tr.empty:
                tr = trend.iloc[[0]]
            tr = tr.iloc[0]
            val = float(tr.get("trend_per_decade", np.nan))
            arrow = "↑" if np.isfinite(val) and val > 0 else "↓"
            st.metric("Trend pro Dekade", f"{val:+.2f}", delta=f"{arrow} {tr.get('significance', 'n/a')}")
            st.dataframe(trend, use_container_width=True, hide_index=True)
        else:
            st.info("Keine Trenddaten verfügbar.")

    st.markdown("**Zeitreihe Detail (interaktiv)**")
    fig_detail = plot_detail_timeseries(monthly, selected_year)
    st.plotly_chart(fig_detail, use_container_width=True, config={"displayModeBar": False, "responsive": True})

    st.markdown("**Download**")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button(
            "CSV: drought_events",
            data=events.to_csv(index=False).encode("utf-8"),
            file_name=f"{domain}_drought_events.csv",
            mime="text/csv",
        )
    with d2:
        png_bytes = None
        try:
            png_bytes = fig_detail.to_image(format="png", width=1200, height=500)
        except Exception:
            pass
        if png_bytes:
            st.download_button(
                "Chart PNG",
                data=png_bytes,
                file_name=f"{domain}_timeseries.png",
                mime="image/png",
            )
        else:
            st.caption("Chart PNG nicht verfügbar (kaleido fehlt).")
    with d3:
        report_txt = io.StringIO()
        report_txt.write("Drought Monitor Quick Report\n")
        report_txt.write(f"Domain: {domain}\n")
        report_txt.write(f"Selected year: {selected_year}\n")
        report_txt.write(f"Current SMI: {current_smi:.2f}\n")
        report_txt.write(f"Status: {status}\n")
        report_txt.write(f"Ranking: {rank_driest}\n")
        report_txt.write(f"Return period: {rp}\n")
        st.download_button(
            "Report (txt)",
            data=report_txt.getvalue().encode("utf-8"),
            file_name=f"{domain}_report.txt",
            mime="text/plain",
        )

st.caption("Stabiler Modus: Cache TTL 600s · Port 8501 empfohlen · Mobile-freundliches Single-Page Layout")
