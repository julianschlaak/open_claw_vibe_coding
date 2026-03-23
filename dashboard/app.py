#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Drought Dashboard — Paper #1", layout="wide")

BASE = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE / "analysis" / "results"

# =============================================================================
# CATCHMENT CONFIGURATION (6 VALID CATCHMENTS)
# =============================================================================
VALID_CATCHMENTS = ['chemnitz2', 'wesenitz2', 'parthe', 'wyhra', 'goeltzsch2', 'zwoenitz1']

CATCHMENT_FILES: Dict[str, Dict[str, Path]] = {c: {
    "monthly": RESULTS_DIR / c / "monthly_drought_indices.csv",
    "discharge": RESULTS_DIR / c / "monthly_drought_indices.csv",
    "spi_spei": RESULTS_DIR / c / "spi_spei.csv",
} for c in VALID_CATCHMENTS}

CATCHMENT_NAMES = {
    "chemnitz2": "Chemnitz2 — Medium catchment, urban influence",
    "wesenitz2": "Wesenitz2 — Forested, good mHM performance (KGE=0.75)",
    "parthe": "Parthe — North German Plain, groundwater lag (10mo!)",
    "wyhra": "Wyhra — Small agricultural catchment",
    "goeltzsch2": "Goeltzsch2 — Industrial region, regulated flow",
    "zwoenitz1": "Zwoenitz1 — Ore Mountains headwater",
}

MONTH_NAMES = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}

DROUGHT_CLASS_MAP = {
    "Alle": None,
    "Extrem": ["extreme_drought"],
    "Schwer": ["severe_drought"],
    "Moderat": ["moderate_drought"],
    "Dürre (gesamt)": ["drought", "moderate_drought", "severe_drought", "extreme_drought"],
    "Normal/Nass": ["normal_or_wet"],
}

def _file_signature(paths: List[Path]) -> tuple:
    sig = []
    for p in paths:
        if p.exists():
            stt = p.stat()
            sig.append((str(p), int(stt.st_mtime), int(stt.st_size)))
        else:
            sig.append((str(p), 0, 0))
    return tuple(sig)

@st.cache_data(show_spinner=False, ttl=5)
def load_data(_sig: tuple, catchment: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    monthly_path = CATCHMENT_FILES[catchment]["monthly"]
    discharge_path = CATCHMENT_FILES[catchment]["discharge"]
    spi_spei_path = CATCHMENT_FILES[catchment]["spi_spei"]

    monthly = pd.read_csv(monthly_path)
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
    monthly["month_name"] = monthly["month"].map(MONTH_NAMES)

    discharge = pd.read_csv(discharge_path)
    discharge["date"] = pd.to_datetime(discharge["date"])
    if "year" not in discharge.columns:
        discharge["year"] = discharge["date"].dt.year
    if "month" not in discharge.columns:
        discharge["month"] = discharge["date"].dt.month

    # Load SPI/SPEI if available
    spi_spei = None
    if spi_spei_path.exists():
        spi_spei = pd.read_csv(spi_spei_path)
        spi_spei["date"] = pd.to_datetime(spi_spei["date"])
        spi_spei["year"] = spi_spei["date"].dt.year
        spi_spei["month"] = spi_spei["date"].dt.month

    return monthly, discharge, spi_spei

def filter_monthly(df: pd.DataFrame, years: tuple[int, int], month_sel: str, drought_sel: str) -> pd.DataFrame:
    out = df[(df["year"] >= years[0]) & (df["year"] <= years[1])].copy()

    if month_sel != "Alle":
        month_num = [k for k, v in MONTH_NAMES.items() if v == month_sel][0]
        out = out[out["month"] == month_num]

    classes = DROUGHT_CLASS_MAP.get(drought_sel)
    if classes:
        out = out[out["drought_class"].isin(classes)]

    return out

def calc_metrics(qsim: pd.Series, qobs: pd.Series) -> dict:
    valid = pd.DataFrame({"qsim": qsim, "qobs": qobs}).dropna()
    if valid.empty:
        return {"KGE": np.nan, "RMSE": np.nan, "MAE": np.nan, "r": np.nan}

    sim = valid["qsim"].to_numpy(dtype=float)
    obs = valid["qobs"].to_numpy(dtype=float)

    r = np.corrcoef(sim, obs)[0, 1] if len(sim) > 1 else np.nan
    std_sim = np.std(sim)
    std_obs = np.std(obs)
    alpha = (std_sim / std_obs) if std_obs != 0 else np.nan
    mean_sim = np.mean(sim)
    mean_obs = np.mean(obs)
    beta = (mean_sim / mean_obs) if mean_obs != 0 else np.nan
    kge = 1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)

    rmse = float(np.sqrt(np.mean((sim - obs) ** 2)))
    mae = float(np.mean(np.abs(sim - obs)))

    return {"KGE": float(kge), "RMSE": rmse, "MAE": mae, "r": float(r)}

def get_correlation(x: pd.Series, y: pd.Series) -> float:
    valid = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(valid) < 5:
        return np.nan
    return float(valid["x"].corr(valid["y"]))

# =============================================================================
# PAGE START
# =============================================================================
st.title("🌍 Drought Dashboard — Paper #1")
st.caption("Matrix Drought Index (MDI) — 6 German Catchments (1991–2020)")

# Sidebar
st.sidebar.header("Filter")
catchment = st.sidebar.selectbox("Catchment", VALID_CATCHMENTS, index=0)

sig = _file_signature([
    CATCHMENT_FILES[catchment]["monthly"],
    CATCHMENT_FILES[catchment]["discharge"],
    CATCHMENT_FILES[catchment]["spi_spei"],
])
monthly_df, discharge_df, spi_spei_df = load_data(sig, catchment)

min_year = int(monthly_df["year"].min())
max_year = int(monthly_df["year"].max())
default_min = max(min_year, 1990)
default_max = min(max_year, 2020)

years = st.sidebar.slider("Zeitraum", min_value=min_year, max_value=max_year, value=(default_min, default_max))
month_sel = st.sidebar.selectbox("Monat", ["Alle"] + list(MONTH_NAMES.values()), index=0)
drought_sel = st.sidebar.selectbox("Dürre-Klasse", list(DROUGHT_CLASS_MAP.keys()), index=0)

filtered = filter_monthly(monthly_df, years, month_sel, drought_sel)

st.info(f"📍 **{catchment}**: {CATCHMENT_NAMES.get(catchment, 'Unknown')}")

# =============================================================================
# TABS
# =============================================================================
ALL_TABS = ["📊 MDI Overview", "🗺️ Heatmap", "📈 Timeseries", "💧 Discharge", "🔬 Propagation", "📋 Events", "📉 SPI/SPEI", "💾 Export"]
mdi_tab, heatmap_tab, ts_tab, discharge_tab, prop_tab, events_tab, spi_tab, export_tab = st.tabs(ALL_TABS)

# =============================================================================
# TAB 1: MDI OVERVIEW
# =============================================================================
with mdi_tab:
    st.subheader("Matrix Drought Index (MDI)")
    st.markdown("""
    **MDI** integrates three hydrological components:
    - Soil Moisture (SMI, w=0.4)
    - Recharge (R-Pctl, w=0.3)
    - Streamflow (Q-Pctl, w=0.3)
    
    **Advantages over single indices:**
    - Captures drought propagation across compartments
    - Smoother temporal dynamics (recharge + streamflow memory)
    - Percentile-based (no distributional assumptions)
    """)
    
    if "mdi_percent" in filtered.columns:
        mdi_heat = filtered.pivot_table(index="year", columns="month", values="mdi_percent", aggfunc="mean")
        mdi_heat = mdi_heat.reindex(columns=list(range(1, 13)))
        
        fig_mdi = go.Figure(
            data=go.Heatmap(
                z=mdi_heat.values,
                x=[MONTH_NAMES[m] for m in mdi_heat.columns],
                y=mdi_heat.index,
                colorscale=[[0.0, "#8b0000"], [0.25, "#d7301f"], [0.5, "#fdae61"], [0.75, "#a6d96a"], [1.0, "#1a9850"]],
                zmin=0, zmax=100,
                colorbar={"title": "MDI Percentile"},
                hovertemplate="Jahr: %{y}<br>Monat: %{x}<br>MDI: %{z:.1f}<extra></extra>",
            )
        )
        fig_mdi.update_layout(height=550, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_mdi, use_container_width=True)
        
        # 2018-2020 highlight
        mdi_2018_2020 = filtered[(filtered["year"] >= 2018) & (filtered["year"] <= 2020)]
        if not mdi_2018_2020.empty:
            mdi_min = mdi_2018_2020["mdi_percent"].min()
            mdi_days_drought = (mdi_2018_2020["mdi_percent"] < 20).sum()
            c1, c2 = st.columns(2)
            c1.metric("MDI Minimum (2018–2020)", f"{mdi_min:.1f}")
            c2.metric("MDI Drought Months (<20)", f"{mdi_days_drought}")
    else:
        st.warning("MDI column not found in data.")

# =============================================================================
# TAB 2: HEATMAP
# =============================================================================
with heatmap_tab:
    st.subheader("Soil Moisture Index (SMI)")
    sm_col = "sm_percent" if "sm_percent" in filtered.columns else "smi_percent"
    if sm_col in filtered.columns:
        heat = filtered.pivot_table(index="year", columns="month", values=sm_col, aggfunc="mean")
        heat = heat.reindex(columns=list(range(1, 13)))
        
        fig_h = go.Figure(
            data=go.Heatmap(
                z=heat.values,
                x=[MONTH_NAMES[m] for m in heat.columns],
                y=heat.index,
                colorscale=[[0.0, "#8b0000"], [0.25, "#d7301f"], [0.5, "#fdae61"], [0.75, "#a6d96a"], [1.0, "#1a9850"]],
                zmin=0, zmax=100,
                colorbar={"title": "SMI Percentile"},
                hovertemplate="Jahr: %{y}<br>Monat: %{x}<br>SMI: %{z:.1f}<extra></extra>",
            )
        )
        fig_h.update_layout(height=550, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.warning(f"SMI column not found. Available: {list(filtered.columns)}")

# =============================================================================
# TAB 3: TIMESERIES
# =============================================================================
with ts_tab:
    st.subheader("Multi-Component Timeseries")
    variable_options = {
        "SMI": "sm_percent" if "sm_percent" in filtered.columns else "smi_percent",
        "Recharge": "recharge_percent",
        "Runoff": "runoff_percent",
        "MDI": "mdi_percent",
        "Discharge": "qobs_mean" if "qobs_mean" in filtered.columns else None,
    }
    variable_options = {k: v for k, v in variable_options.items() if v is not None and v in filtered.columns}
    
    selected = st.multiselect("Variablen auswählen", options=list(variable_options.keys()),
                               default=["SMI", "Recharge", "Runoff", "MDI"])

    if selected:
        # Define drought class colors (percentiles)
        # 0-5%: Extreme drought (dark red)
        # 5-10%: Severe drought (red)
        # 10-20%: Moderate drought (orange)
        # 20-40%: Below normal (yellow-orange)
        # 40-60%: Normal (green)
        # 60-80%: Above normal (light green)
        # 80-95%: Wet (blue-green)
        # 95-100%: Very wet (blue)
        
        drought_bands = [
            {'threshold': 5, 'color': 'rgba(139, 0, 0, 0.08)', 'name': 'Extreme drought (<5%)'},
            {'threshold': 10, 'color': 'rgba(215, 49, 31, 0.08)', 'name': 'Severe drought (5-10%)'},
            {'threshold': 20, 'color': 'rgba(244, 109, 67, 0.06)', 'name': 'Moderate drought (10-20%)'},
            {'threshold': 40, 'color': 'rgba(253, 174, 97, 0.05)', 'name': 'Below normal (20-40%)'},
            {'threshold': 60, 'color': 'rgba(166, 217, 106, 0.05)', 'name': 'Normal (40-60%)'},
            {'threshold': 80, 'color': 'rgba(102, 189, 99, 0.05)', 'name': 'Above normal (60-80%)'},
            {'threshold': 95, 'color': 'rgba(49, 163, 84, 0.05)', 'name': 'Wet (80-95%)'},
            {'threshold': 100, 'color': 'rgba(26, 152, 80, 0.05)', 'name': 'Very wet (>95%)'},
        ]
        
        # Create shapes for background bands
        shapes = []
        prev_threshold = 0
        for band in drought_bands:
            shapes.append(dict(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=prev_threshold,
                y1=band['threshold'],
                fillcolor=band['color'],
                layer="below",
                line=dict(width=0)
            ))
            prev_threshold = band['threshold']
        
        # Line colors for different components
        line_colors = {
            "SMI": '#d62728',      # Red
            "Recharge": '#1f77b4', # Blue  
            "Runoff": '#9467bd',   # Purple
            "MDI": '#2ca02c',      # Green
            "Discharge": '#ff7f0e' # Orange
        }
        
        fig_ts = go.Figure()
        for name in selected:
            col = variable_options[name]
            if col in filtered.columns:
                fig_ts.add_trace(go.Scatter(
                    x=filtered["date"], 
                    y=filtered[col],
                    mode='lines', 
                    name=name,
                    line=dict(color=line_colors.get(name, '#333'), width=1.8)
                ))
        
        # Add threshold lines for drought classes
        threshold_y = [20, 10, 5]  # Drought thresholds
        for t in threshold_y:
            fig_ts.add_shape(
                type="line",
                x0=filtered["date"].min(),
                x1=filtered["date"].max(),
                y0=t,
                y1=t,
                line=dict(color="rgba(0,0,0,0.2)", width=0.8, dash="dot")
            )
        
        fig_ts.update_layout(
            height=520,
            xaxis_title="Datum",
            yaxis_title="Percentile",
            yaxis_range=[-5, 105],
            hovermode="x unified",
            dragmode="zoom",
            margin=dict(l=20, r=120, t=40, b=20),  # Increased right margin for legend
            shapes=shapes,
            legend=dict(
                orientation="v",
                yanchor="top", 
                y=0.98, 
                xanchor="left", 
                x=1.02,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(size=11)
            )
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("Bitte mindestens eine Variable auswählen.")

# =============================================================================
# TAB 4: DISCHARGE
# =============================================================================
with discharge_tab:
    st.subheader("Discharge Validation (Qobs vs. Qsim)")
    avail_cols = list(discharge_df.columns)
    qobs_col = "qobs_mean" if "qobs_mean" in avail_cols else ("qobs" if "qobs" in avail_cols else None)
    qsim_col = "qsim_mean" if "qsim_mean" in avail_cols else ("qsim" if "qsim" in avail_cols else None)
    
    has_qobs = qobs_col is not None and discharge_df[qobs_col].notna().any() if qobs_col else False
    has_qsim = qsim_col is not None and discharge_df[qsim_col].notna().any() if qsim_col else False
    
    if not has_qsim:
        st.info("Discharge data not available for this catchment.")
    else:
        fig_d = go.Figure()
        if has_qobs:
            fig_d.add_trace(go.Scatter(x=discharge_df["date"], y=discharge_df[qobs_col],
                                       mode="lines", name="Qobs", line=dict(color="red", width=1.6)))
        fig_d.add_trace(go.Scatter(x=discharge_df["date"], y=discharge_df[qsim_col],
                                   mode="lines", name="Qsim", line=dict(color="blue", width=1.6)))
        fig_d.update_layout(height=520, xaxis_title="Datum", yaxis_title="Abfluss (m³/s)",
                            hovermode="x unified", dragmode="zoom", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_d, use_container_width=True)

        if has_qobs:
            metrics = calc_metrics(discharge_df[qsim_col], discharge_df[qobs_col])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("KGE", f"{metrics['KGE']:.3f}")
            c2.metric("RMSE", f"{metrics['RMSE']:.3f}")
            c3.metric("MAE", f"{metrics['MAE']:.3f}")
            c4.metric("r", f"{metrics['r']:.3f}")
        else:
            st.info("Qobs nicht verfügbar. Nur Qsim (simulated) angezeigt.")

# =============================================================================
# TAB 5: PROPAGATION
# =============================================================================
with prop_tab:
    st.subheader("Drought Propagation Analysis")
    st.markdown("""
    **Cross-correlation analysis** between hydrological compartments:
    - **SM → Runoff**: Soil Moisture vs. Runoff (direct surface response)
    - **SM → Recharge**: Soil Moisture vs. Recharge (subsurface response)
    - **Recharge → Runoff**: Recharge vs. Runoff (baseflow contribution)
    
    📊 **Key Finding**: SM ↔ Runoff shows **strong correlation (r=0.77–0.87)** with **0-month lag** — fast hydrological response.
    """)
    
    import json
    # Use corrected lag data
    lag_file = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/propagation_lags_corrected.json')
    if lag_file.exists():
        with open(lag_file) as f:
            prop_data = json.load(f)
        
        # Create summary table
        prop_df = pd.DataFrame(prop_data)
        prop_df.columns = ['Catchment', 'SM→R Lag', 'SM→R r', 'SM→Q Lag', 'SM→Q r', 'R→Q Lag', 'R→Q r', 'N']
        
        # Color-code correlation quality
        def corr_quality(r):
            if pd.isna(r): return "N/A"
            r = abs(r)
            if r >= 0.7: return "🟢 Strong"
            elif r >= 0.5: return "🟡 Moderate"
            else: return "🔴 Weak"
        
        prop_df['SM→R Quality'] = prop_df['SM→R r'].apply(corr_quality)
        prop_df['SM→Q Quality'] = prop_df['SM→Q r'].apply(corr_quality)
        prop_df['R→Q Quality'] = prop_df['R→Q r'].apply(corr_quality)
        
        st.markdown("### 📊 Correlation Quality Summary")
        display_df = prop_df[['Catchment', 'SM→R Lag', 'SM→R r', 'SM→R Quality', 
                             'SM→Q Lag', 'SM→Q r', 'SM→Q Quality']].copy()
        display_df['SM→R r'] = display_df['SM→R r'].round(3)
        display_df['SM→Q r'] = display_df['SM→Q r'].round(3)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Heatmap of correlations
        st.markdown("### 🔥 Correlation Heatmap")
        lag_viz = prop_df[['SM→R r', 'R→Q r', 'SM→Q r']].copy()
        lag_viz.index = prop_df['Catchment']
        lag_viz.columns = ['SM→Recharge', 'Recharge→Runoff', 'SM→Runoff']
        
        fig_lag = go.Figure(data=go.Heatmap(
            z=lag_viz.values, x=lag_viz.columns, y=lag_viz.index,
            colorscale='RdYlGn', zmin=0, zmax=1,
            text=[[f"{v:.2f}" if not pd.isna(v) else "N/A" for v in row] for row in lag_viz.values],
            texttemplate="%{text}", textfont={"size": 14, "color": "black"},
            hovertemplate="Catchment: %{y}<br>Correlation: %{z:.3f}<extra></extra>",
        ))
        fig_lag.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_lag, use_container_width=True)
        
        # Interpretation box
        st.markdown("""
        ### 📝 Interpretation
        
        **SM ↔ Runoff** (r = 0.77–0.87):  
        ✅ **Strong correlation, 0-month lag** — Fast surface/subsurface flow pathways dominate in these catchments.
        
        **SM ↔ Recharge** (r = 0.47–0.54):  
        🔴 **Weak correlation** — mHM simulates rapid SM↔recharge coupling. Other factors (ET, routing) mediate the relationship.
        
        **Recharge ↔ Runoff** (r = 0.57–0.69):  
        🟡 **Moderate correlation** — Recharge contributes to baseflow but other sources also contribute.
        
        **⚠️ Note on Groundwater Lags:**  
        The 0-month lag at monthly resolution suggests **fast hydrological response**. 
        Groundwater memory effects (typically 6–12 months) are **not captured** at monthly aggregation. 
        For groundwater lag analysis, **daily data** would be required.
        """)
    else:
        st.warning("Propagation lags not computed yet.")

# =============================================================================
# TAB 6: EVENTS
# =============================================================================
with events_tab:
    st.subheader("Drought Event Detection")
    st.markdown("""
    **Automatic drought event identification** based on percentile thresholds:
    - **Extreme**: < 5th percentile
    - **Severe**: < 10th percentile  
    - **Moderate**: < 20th percentile
    
    Minimum 3 consecutive months below threshold.
    """)
    
    import json
    events_file = Path('/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results/drought_events.json')
    
    if events_file.exists():
        with open(events_file) as f:
            all_events = json.load(f)
        
        catchment_events = next((e for e in all_events if e['catchment'] == catchment), None)
        
        if catchment_events:
            # 2018-2020 Major Event
            st.markdown("### 🎯 2018–2020 Major Drought Event")
            major = catchment_events.get('major_event_2018_2020', {})
            if major:
                c1, c2, c3, c4 = st.columns(4)
                mdi_data = major.get('mdi', {})
                c1.metric("Duration", f"{major.get('duration_months', 0)} months")
                c2.metric("MDI Min", f"{mdi_data.get('min', 0):.1f}")
                c3.metric("MDI Mean", f"{mdi_data.get('mean', 0):.1f}")
                c4.metric("Months < 20", f"{mdi_data.get('months_below_20', 0)}")
                
                st.markdown("**Component Impact:**")
                cc = st.columns(3)
                for i, comp in enumerate(['sm', 'recharge', 'runoff']):
                    cd = major.get(comp, {})
                    cc[i].metric(f"{comp.upper()} Min", f"{cd.get('min', 0):.1f}", f"{cd.get('months_below_20', 0)} mo < 20")
            
            # Event Statistics
            st.markdown("### 📊 Event Statistics (1991–2020)")
            sc = st.columns(3)
            for i, idx_name in enumerate(['MDI', 'SMI']):
                idx_data = catchment_events.get('indices', {}).get(idx_name, {})
                stats = idx_data.get('statistics', {})
                sc[i].metric(f"{idx_name} Events", f"{stats.get('n_events', 0)}", f"{stats.get('total_drought_months', 0)} months")
            
            compound_stats = catchment_events.get('compound_events', {}).get('statistics', {})
            sc[2].metric("Compound Events", f"{compound_stats.get('n_events', 0)}", f"{compound_stats.get('total_drought_months', 0)} months")
            
            # MDI Events Table
            st.markdown("### 📅 MDI Drought Events")
            mdi_events = catchment_events.get('indices', {}).get('MDI', {}).get('events', [])
            if mdi_events:
                event_df = pd.DataFrame([
                    {
                        'Start': e.get('start_date', '')[:7],
                        'End': e.get('end_date', '')[:7],
                        'Duration': e.get('duration_months', 0),
                        'Severity': e.get('severity', 'N/A'),
                        'Min MDI': f"{e.get('min_value', 0):.1f}",
                        'Mean MDI': f"{e.get('mean_value', 0):.1f}",
                    }
                    for e in mdi_events
                ])
                st.dataframe(event_df, use_container_width=True, hide_index=True)
            else:
                st.info("No MDI drought events detected.")
            
            # Compound Events
            compound_evts = catchment_events.get('compound_events', {}).get('events', [])
            if compound_evts:
                st.markdown("### 🔗 Compound Events (all components < 20)")
                compound_df = pd.DataFrame([
                    {
                        'Start': e.get('start_date', '')[:7],
                        'End': e.get('end_date', '')[:7],
                        'Duration': e.get('duration_months', 0),
                        'Severity': e.get('severity', 'N/A'),
                        'Min MDI': f"{e.get('min_mdi', 0):.1f}",
                    }
                    for e in compound_evts
                ])
                st.dataframe(compound_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No event data for: {catchment}")
    else:
        st.warning("Event detection not computed yet.")

# =============================================================================
# TAB 7: SPI/SPEI
# =============================================================================
with spi_tab:
    st.subheader("SPI/SPEI vs MDI Comparison")
    st.markdown("""
    **Standardized Precipitation Index (SPI)** and **Standardized Precipitation-Evapotranspiration Index (SPEI)**
    are calculated from monthly precipitation and PET data (12-month accumulation).
    
    **Comparison:**
    - **SPI**: Precipitation-based (meteorological drought)
    - **SPEI**: P - PET based (agricultural drought signal)
    - **MDI**: Coupled hydrological drought (SM + Recharge + Discharge)
    """)
    
    if spi_spei_df is not None and not spi_spei_df.empty:
        # Filter SPI/SPEI to selected years
        spi_filtered = spi_spei_df[(spi_spei_df["year"] >= years[0]) & (spi_spei_df["year"] <= years[1])].copy()
        
        # Merge with MDI data
        merged = spi_filtered.merge(
            monthly_df[['date', 'mdi_percent', 'sm_percent']], 
            on='date', 
            how='left',
            suffixes=('_spi', '')
        )
        
        # Create timeseries plot - cleaner design
        fig_spi_ts = go.Figure()
        
        # Drought severity bands (background)
        bands = [
            {'range': (-3, -2), 'color': 'rgba(139, 0, 0, 0.12)', 'name': 'Extreme'},
            {'range': (-2, -1), 'color': 'rgba(215, 48, 31, 0.10)', 'name': 'Severe'},
            {'range': (-1, 0), 'color': 'rgba(253, 174, 97, 0.08)', 'name': 'Moderate'},
        ]
        
        shapes = []
        for band in bands:
            shapes.append(dict(
                type="rect",
                xref="x",
                yref="y",
                x0=merged['date'].min(),
                x1=merged['date'].max(),
                y0=band['range'][0],
                y1=band['range'][1],
                fillcolor=band['color'],
                layer="below",
                line=dict(width=0)
            ))
        
        # Threshold lines
        for y, color in [(-2, 'rgba(139,0,0,0.4)'), (-1, 'rgba(215,48,31,0.4)'), (0, 'rgba(0,0,0,0.2)')]:
            shapes.append(dict(
                type="line", xref="x", yref="y",
                x0=merged['date'].min(), x1=merged['date'].max(),
                y0=y, y1=y,
                line=dict(color=color, width=1, dash="dash")
            ))
        
        # SPI line
        if 'spi12' in merged.columns:
            fig_spi_ts.add_trace(go.Scatter(
                x=merged['date'], y=merged['spi12'],
                mode='lines', name='SPI-12',
                line=dict(color='#1f77b4', width=2)
            ))
        
        # SPEI line
        if 'spei12' in merged.columns:
            fig_spi_ts.add_trace(go.Scatter(
                x=merged['date'], y=merged['spei12'],
                mode='lines', name='SPEI-12',
                line=dict(color='#e377c2', width=2)
            ))
        
        # MDI normalized
        if 'mdi_percent' in merged.columns:
            mdi_norm = ((merged['mdi_percent'] - 50) / 50) * 3
            fig_spi_ts.add_trace(go.Scatter(
                x=merged['date'], y=mdi_norm,
                mode='lines', name='MDI (norm)',
                line=dict(color='#2ca02c', width=2.5)
            ))
        
        fig_spi_ts.update_layout(
            height=500,
            xaxis_title="Datum",
            yaxis_title="Standardized Index",
            hovermode="x unified",
            dragmode="zoom",
            margin=dict(l=20, r=120, t=40, b=20),  # Increased right margin
            shapes=shapes,
            legend=dict(
                orientation="v",
                yanchor="top", y=0.98, xanchor="left", x=1.02,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1,
                font=dict(size=11)
            ),
            yaxis=dict(
                range=[-3.5, 3.5],
                tickvals=[-3, -2, -1, 0, 1, 2, 3],
                ticktext=['-3', '-2', '-1', '0', '+1', '+2', '+3']
            )
        )
        st.plotly_chart(fig_spi_ts, use_container_width=True)
        
        # Correlations
        st.markdown("### 🔗 Correlation Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**MDI vs SPI/SPEI Correlations**")
            if 'mdi_percent' in merged.columns and 'spi12' in merged.columns:
                r_mdi_spi = get_correlation(merged['mdi_percent'], merged['spi12'])
                r_mdi_spei = get_correlation(merged['mdi_percent'], merged['spei12']) if 'spei12' in merged.columns else np.nan
                r_spi_spei = get_correlation(merged['spi12'], merged['spei12']) if 'spei12' in merged.columns else np.nan
                
                corr_df = pd.DataFrame({
                    'Index 1': ['MDI', 'MDI', 'SPI'],
                    'Index 2': ['SPI-12', 'SPEI-12', 'SPEI-12'],
                    'Correlation': [r_mdi_spi, r_mdi_spei, r_spi_spei]
                })
                st.dataframe(corr_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**SMI vs SPI/SPEI Correlations**")
            if 'sm_percent' in merged.columns and 'spi12' in merged.columns:
                r_smi_spi = get_correlation(merged['sm_percent'], merged['spi12'])
                r_smi_spei = get_correlation(merged['sm_percent'], merged['spei12']) if 'spei12' in merged.columns else np.nan
                
                corr_df2 = pd.DataFrame({
                    'Index 1': ['SMI', 'SMI'],
                    'Index 2': ['SPI-12', 'SPEI-12'],
                    'Correlation': [r_smi_spi, r_smi_spei]
                })
                st.dataframe(corr_df2, use_container_width=True, hide_index=True)
        
        # Scatter plots
        st.markdown("### 🎯 Scatter: MDI vs SPI/SPEI")
        sc1, sc2 = st.columns(2)
        
        with sc1:
            if 'mdi_percent' in merged.columns and 'spi12' in merged.columns:
                valid_sc = merged[['mdi_percent', 'spi12']].dropna()
                fig_sc1 = go.Figure()
                fig_sc1.add_trace(go.Scatter(
                    x=valid_sc['spi12'], y=valid_sc['mdi_percent'],
                    mode='markers',
                    marker=dict(color='#1f77b4', opacity=0.6, size=8),
                    text=merged.loc[valid_sc.index, 'date'].dt.strftime('%Y-%m'),
                    hovertemplate="SPI: %{x:.2f}<br>MDI: %{y:.1f}<br>%{text}<extra></extra>",
                ))
                fig_sc1.update_layout(
                    height=400,
                    xaxis_title="SPI-12",
                    yaxis_title="MDI (%)",
                    margin=dict(l=20, r=20, t=40, b=20),
                    title=dict(text=f"MDI vs SPI-12 (r={r_mdi_spi:.2f})" if 'r_mdi_spi' in dir() else "", x=0.5)
                )
                st.plotly_chart(fig_sc1, use_container_width=True)
        
        with sc2:
            if 'mdi_percent' in merged.columns and 'spei12' in merged.columns:
                valid_sc2 = merged[['mdi_percent', 'spei12']].dropna()
                fig_sc2 = go.Figure()
                fig_sc2.add_trace(go.Scatter(
                    x=valid_sc2['spei12'], y=valid_sc2['mdi_percent'],
                    mode='markers',
                    marker=dict(color='#ff7f0e', opacity=0.6, size=8),
                    text=merged.loc[valid_sc2.index, 'date'].dt.strftime('%Y-%m'),
                    hovertemplate="SPEI: %{x:.2f}<br>MDI: %{y:.1f}<br>%{text}<extra></extra>",
                ))
                fig_sc2.update_layout(
                    height=400,
                    xaxis_title="SPEI-12",
                    yaxis_title="MDI (%)",
                    margin=dict(l=20, r=20, t=40, b=20),
                    title=dict(text=f"MDI vs SPEI-12 (r={r_mdi_spei:.2f})" if 'r_mdi_spei' in dir() else "", x=0.5)
                )
                st.plotly_chart(fig_sc2, use_container_width=True)
        
        # 2018-2020 comparison
        st.markdown("### 🎯 2018–2020 Drought Event Comparison")
        evt_data = merged[(merged['year'] >= 2018) & (merged['year'] <= 2020)].copy()
        if not evt_data.empty:
            evt_stats = pd.DataFrame({
                'Index': ['SPI-12', 'SPEI-12', 'MDI', 'SMI'],
                'Min': [
                    evt_data['spi12'].min() if 'spi12' in evt_data.columns else np.nan,
                    evt_data['spei12'].min() if 'spei12' in evt_data.columns else np.nan,
                    evt_data['mdi_percent'].min() if 'mdi_percent' in evt_data.columns else np.nan,
                    evt_data['sm_percent'].min() if 'sm_percent' in evt_data.columns else np.nan,
                ],
                'Mean': [
                    evt_data['spi12'].mean() if 'spi12' in evt_data.columns else np.nan,
                    evt_data['spei12'].mean() if 'spei12' in evt_data.columns else np.nan,
                    evt_data['mdi_percent'].mean() if 'mdi_percent' in evt_data.columns else np.nan,
                    evt_data['sm_percent'].mean() if 'sm_percent' in evt_data.columns else np.nan,
                ],
                'Months < -1': [
                    (evt_data['spi12'] < -1).sum() if 'spi12' in evt_data.columns else 0,
                    (evt_data['spei12'] < -1).sum() if 'spei12' in evt_data.columns else 0,
                    (evt_data['mdi_percent'] < 20).sum() if 'mdi_percent' in evt_data.columns else 0,
                    (evt_data['sm_percent'] < 20).sum() if 'sm_percent' in evt_data.columns else 0,
                ]
            })
            st.dataframe(evt_stats, use_container_width=True, hide_index=True)
    else:
        st.warning("SPI/SPEI data not available for this catchment.")

# =============================================================================
# TAB 8: EXPORT
# =============================================================================
with export_tab:
    st.subheader("Data Export")
    
    csv_data = filtered.to_csv(index=False)
    st.download_button("📊 Download CSV (filtered)", csv_data,
                       f"{catchment}_drought_{years[0]}_{years[1]}.csv", "text/csv")
    
    full_csv = monthly_df.to_csv(index=False)
    st.download_button("📊 Download Full CSV", full_csv,
                       f"{catchment}_full_data.csv", "text/csv")
    
    if spi_spei_df is not None and not spi_spei_df.empty:
        spi_csv = spi_spei_df.to_csv(index=False)
        st.download_button("📉 Download SPI/SPEI CSV", spi_csv,
                           f"{catchment}_spi_spei.csv", "text/csv")
    
    if "mdi_percent" in filtered.columns:
        mdi_heat = filtered.pivot_table(index="year", columns="month", values="mdi_percent", aggfunc="mean")
        fig_png = go.Figure(data=go.Heatmap(z=mdi_heat.values, x=[MONTH_NAMES[m] for m in range(1,13)], y=mdi_heat.index))
        st.plotly_chart(fig_png, use_container_width=True)
        st.download_button("🖼️ Download MDI Heatmap (PNG)",
                           fig_png.to_image(format="png", width=800, height=600, scale=2),
                           f"{catchment}_mdi_heatmap.png", "image/png")

st.caption("Paper #1 Dashboard — 6 German Catchments, 1991–2020 (mHM 5.13.2 + CAMELS-DE)")
