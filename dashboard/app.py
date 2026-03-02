#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yaml

st.set_page_config(
    page_title="Dürre-Monitor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE = Path(__file__).resolve().parents[1]
DASH = Path(__file__).resolve().parent
RESULTS_DIR = BASE / "analysis" / "results"

CATCHMENT_FILES: Dict[str, Dict[str, Path]] = {
    "test_domain": {
        "monthly": RESULTS_DIR / "test_domain" / "monthly_drought_indices.csv",
        "discharge": RESULTS_DIR / "test_domain" / "daily_discharge.csv",
    },
    "catchment_custom": {
        "monthly": RESULTS_DIR / "catchment_custom" / "monthly_drought_indices.csv",
        "discharge": RESULTS_DIR / "catchment_custom" / "daily_discharge.csv",
    },
}

MONTHS = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
MONTHS_INV = {v: k for k, v in MONTHS.items()}

DROUGHT_CLASS_MAP = {
    "Alle": None,
    "Extrem": ["extreme_drought"],
    "Schwer": ["severe_drought"],
    "Moderat": ["moderate_drought"],
    "Dürre (gesamt)": ["drought", "moderate_drought", "severe_drought", "extreme_drought"],
    "Normal/Nass": ["normal_or_wet"],
}


def load_config() -> dict:
    cfg_file = DASH / "config.yaml"
    if not cfg_file.exists():
        return {}
    return yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}


def inject_css(theme: str, cfg: dict) -> None:
    base_css = (DASH / "custom.css").read_text(encoding="utf-8") if (DASH / "custom.css").exists() else ""
    color_cfg = cfg.get("colors", {}).get(theme, {})
    ui_cfg = cfg.get("ui", {})
    vars_css = f"""
    <style>
    :root {{
      --bg: {color_cfg.get('bg', '#0E1117')};
      --card: {color_cfg.get('card', '#1E1E1E')};
      --text: {color_cfg.get('text', '#FAFAFA')};
      --text-secondary: {color_cfg.get('text_secondary', '#A0A0A0')};
      --border: {color_cfg.get('border', 'rgba(255,255,255,0.12)')};
      --shadow: {color_cfg.get('shadow', '0 10px 30px rgba(0,0,0,0.30)')};
      --radius: {ui_cfg.get('radius', '12px')};
      --blur: {ui_cfg.get('blur', '10px')};
    }}
    </style>
    <style>{base_css}</style>
    """
    st.markdown(vars_css, unsafe_allow_html=True)


def file_signature(catchment: str) -> tuple:
    items = []
    for k in ("monthly", "discharge"):
        p = CATCHMENT_FILES[catchment][k]
        if p.exists():
            s = p.stat()
            items.append((str(p), int(s.st_mtime), int(s.st_size)))
        else:
            items.append((str(p), 0, 0))
    return tuple(items)


@st.cache_data(show_spinner=False, ttl=5)
def load_data(_sig: tuple, catchment: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    monthly = pd.read_csv(CATCHMENT_FILES[catchment]["monthly"])
    monthly["date"] = pd.to_datetime(monthly["date"])
    monthly["year"] = monthly["date"].dt.year
    monthly["month"] = monthly["date"].dt.month
    monthly["month_name"] = monthly["month"].map(MONTHS)

    discharge = pd.read_csv(CATCHMENT_FILES[catchment]["discharge"])
    discharge["date"] = pd.to_datetime(discharge["date"])
    if "year" not in discharge.columns:
        discharge["year"] = discharge["date"].dt.year
    if "month" not in discharge.columns:
        discharge["month"] = discharge["date"].dt.month
    return monthly, discharge


def calc_metrics(qsim: pd.Series, qobs: pd.Series) -> dict:
    valid = pd.DataFrame({"qsim": qsim, "qobs": qobs}).dropna()
    if valid.empty:
        return {"KGE": np.nan, "RMSE": np.nan, "MAE": np.nan, "r": np.nan}
    sim = valid["qsim"].to_numpy(float)
    obs = valid["qobs"].to_numpy(float)
    r = np.corrcoef(sim, obs)[0, 1] if len(sim) > 1 else np.nan
    std_sim, std_obs = np.std(sim), np.std(obs)
    alpha = std_sim / std_obs if std_obs else np.nan
    mean_sim, mean_obs = np.mean(sim), np.mean(obs)
    beta = mean_sim / mean_obs if mean_obs else np.nan
    kge = 1.0 - np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)
    rmse = np.sqrt(np.mean((sim - obs) ** 2))
    mae = np.mean(np.abs(sim - obs))
    return {"KGE": float(kge), "RMSE": float(rmse), "MAE": float(mae), "r": float(r)}


def status_label(smi: float) -> Tuple[str, str]:
    if smi < 20:
        return "🔴 Schwer", "Kritisch trockene Bedingungen"
    if smi < 40:
        return "🟡 Mäßig", "Erhöhtes Dürresignal"
    return "🟢 Normal", "Kein akutes Dürresignal"


def smart_default_range(df: pd.DataFrame) -> Tuple[int, int]:
    y0, y1 = int(df["year"].min()), int(df["year"].max())
    return y0, y1


def apply_filters(df: pd.DataFrame, years: Tuple[int, int], month_sel: str, drought_sel: str) -> pd.DataFrame:
    out = df[(df["year"] >= years[0]) & (df["year"] <= years[1])].copy()
    if month_sel != "Alle":
        out = out[out["month"] == MONTHS_INV[month_sel]]
    classes = DROUGHT_CLASS_MAP[drought_sel]
    if classes:
        out = out[out["drought_class"].isin(classes)]
    return out


def plot_with_select(fig: go.Figure, key: str, selection_mode: str = "points") -> Optional[dict]:
    try:
        return st.plotly_chart(
            fig,
            use_container_width=True,
            key=key,
            on_select="rerun",
            selection_mode=selection_mode,
            config={"displaylogo": False, "responsive": True},
        )
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, key=key, config={"displaylogo": False, "responsive": True})
        return None


cfg = load_config()
default_theme = cfg.get("default_theme", "dark")
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = default_theme
if "focus_year" not in st.session_state:
    st.session_state.focus_year = None
if "focus_month" not in st.session_state:
    st.session_state.focus_month = None
if "brush_range" not in st.session_state:
    st.session_state.brush_range = None

inject_css(st.session_state.theme_mode, cfg)

# Hero header
left, right = st.columns([0.82, 0.18])
with left:
    st.markdown('<div class="hero"><div class="hero-title">🌍 Dürre-Monitor</div><div class="hero-sub">Hydrological Drought Dashboard · modernisierte UX</div></div>', unsafe_allow_html=True)
with right:
    light = st.toggle("Light Mode", value=(st.session_state.theme_mode == "light"), help="Zwischen Dark- und Light-Theme wechseln")
    st.session_state.theme_mode = "light" if light else "dark"

# Reload css after toggle
inject_css(st.session_state.theme_mode, cfg)

# Progressive disclosure: first basic filter only
f1, f2 = st.columns([0.34, 0.66])
with f1:
    catchment = st.selectbox("Catchment", ["catchment_custom", "test_domain"], index=0, help="Auswahl des Einzugsgebiets")

sig = file_signature(catchment)
monthly, discharge = load_data(sig, catchment)

min_year, max_year = smart_default_range(monthly)
default_years = (min_year, max_year)
with f2:
    years = st.slider("Zeitraum", min_value=min_year, max_value=max_year, value=default_years)

with st.expander("Erweiterte Filter, Rohdaten & Download", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        month_sel = st.selectbox("Monat", ["Alle"] + list(MONTHS.values()), index=0)
    with c2:
        drought_sel = st.selectbox("Dürre-Klasse", list(DROUGHT_CLASS_MAP.keys()), index=0)
    with c3:
        vars_for_ts = st.multiselect(
            "Zeitreihen-Variablen",
            ["SMI", "Recharge", "Runoff", "SSI", "SDI"],
            default=["SMI", "Recharge", "Runoff"],
            help="SMI: Soil Moisture Index (0=trocken, 100=nass)",
        )
    st.download_button(
        "Monatsdaten als CSV herunterladen",
        data=monthly.to_csv(index=False).encode("utf-8"),
        file_name=f"{catchment}_monthly_drought_indices.csv",
        mime="text/csv",
    )

if "month_sel" not in locals():
    month_sel = "Alle"
if "drought_sel" not in locals():
    drought_sel = "Alle"
if "vars_for_ts" not in locals() or not vars_for_ts:
    vars_for_ts = ["SMI", "Recharge", "Runoff"]

flt = apply_filters(monthly, years, month_sel, drought_sel)
if flt.empty:
    st.warning("Keine Daten für diese Filterkombination.")
    st.stop()

latest = flt.sort_values("date").iloc[-1]
label, hint = status_label(float(latest["smi_percent"]))
last_12 = flt.sort_values("date").tail(12)
trend_pct = 0.0
if len(last_12) >= 2 and float(last_12.iloc[0]["smi_percent"]) != 0:
    trend_pct = ((float(last_12.iloc[-1]["smi_percent"]) - float(last_12.iloc[0]["smi_percent"])) / float(last_12.iloc[0]["smi_percent"])) * 100.0

metrics = calc_metrics(discharge.get("qsim", pd.Series(dtype=float)), discharge.get("qobs", pd.Series(dtype=float)))

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Aktueller Status", label, delta=f"SMI: {latest['smi_percent']:.1f}", help="Soil Moisture Index Prozentil")
    st.caption(hint)
    st.markdown('</div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Trend letzte 12M", f"{trend_pct:+.1f}%", help="Prozentuale SMI-Änderung über 12 Monate")
    st.caption("Negativ = trockener")
    st.markdown('</div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("30-Jahre Mittel", f"SMI {flt['smi_percent'].mean():.1f}", help="Mittelwert über gefilterten Zeitraum")
    st.caption(f"Monate: {len(flt)}")
    st.markdown('</div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("Datenqualität", f"KGE {metrics['KGE']:.2f}" if not np.isnan(metrics["KGE"]) else "KGE n/a", help="Modellgüte aus Qsim vs Qobs")
    st.caption(f"r: {metrics['r']:.2f}" if not np.isnan(metrics["r"]) else "r: n/a")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<span class="pulse">{len(flt):,} Monate analysiert · Zeitraum {years[0]}-{years[1]}</span>', unsafe_allow_html=True)

# Main 2x2 grid
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="soft-title">📊 SMI Heatmap</div><div class="soft-sub">Jahre × Monate, klickbar</div>', unsafe_allow_html=True)
    piv = flt.pivot_table(index="year", columns="month", values="smi_percent", aggfunc="mean").reindex(columns=list(range(1, 13)))
    hm = go.Figure(
        data=go.Heatmap(
            z=piv.values,
            x=[MONTHS[m] for m in piv.columns],
            y=piv.index,
            customdata=np.dstack(np.meshgrid(piv.columns, piv.index))[0],
            colorscale=[
                [0.0, "#8b0000"],
                [0.25, "#d7301f"],
                [0.5, "#fdae61"],
                [0.75, "#a6d96a"],
                [1.0, "#1a9850"],
            ],
            zmin=0,
            zmax=100,
            hovertemplate="Jahr %{y}<br>Monat %{x}<br>SMI %{z:.1f}<extra></extra>",
        )
    )
    hm.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    heat_sel = plot_with_select(hm, key="heatmap_v2", selection_mode="points")

    if heat_sel and isinstance(heat_sel, dict):
        points = heat_sel.get("selection", {}).get("points", [])
        if points:
            p = points[0]
            st.session_state.focus_year = int(p.get("y"))
            st.session_state.focus_month = MONTHS_INV.get(str(p.get("x")), None)

    if st.session_state.focus_year and st.session_state.focus_month:
        st.caption(f"Fokus: {st.session_state.focus_year}-{st.session_state.focus_month:02d} (aus Heatmap-Klick)")
    st.markdown('</div>', unsafe_allow_html=True)

with row1_col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="soft-title">📈 Zeitreihe</div><div class="soft-sub">Interaktiv, zoombar, Brush-Selection</div>', unsafe_allow_html=True)
    ts = flt.sort_values("date").copy()

    if st.session_state.focus_year and st.session_state.focus_month:
        center = pd.Timestamp(year=st.session_state.focus_year, month=st.session_state.focus_month, day=1)
        lo, hi = center - pd.DateOffset(months=6), center + pd.DateOffset(months=6)
        ts_zoom = ts[(ts["date"] >= lo) & (ts["date"] <= hi)]
        ts = ts_zoom if not ts_zoom.empty else ts
    elif len(ts) > 72:
        ts = ts.tail(60)

    col_map = {
        "SMI": ("smi_percent", "#FF4B4B"),
        "Recharge": ("recharge_percent", "#00C851"),
        "Runoff": ("runoff_percent", "#5DADE2"),
        "SSI": ("ssi", "#F4D03F"),
        "SDI": ("sdi", "#AF7AC5"),
    }

    ts_fig = go.Figure()
    for v in vars_for_ts:
        c, color = col_map[v]
        ts_fig.add_trace(go.Scatter(x=ts["date"], y=ts[c], mode="lines+markers", marker=dict(size=4), name=v, line=dict(width=2, color=color)))

    ts_fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    ts_fig.update_xaxes(rangeslider_visible=True, showspikes=True)
    ts_fig.update_yaxes(showspikes=True)

    ts_sel = plot_with_select(ts_fig, key="timeseries_v2", selection_mode="box")
    if ts_sel and isinstance(ts_sel, dict):
        pts = ts_sel.get("selection", {}).get("points", [])
        if pts:
            xs = pd.to_datetime([p.get("x") for p in pts])
            st.session_state.brush_range = (xs.min(), xs.max())
            st.caption(f"Brush aktiv: {xs.min().date()} bis {xs.max().date()}")

    st.markdown('</div>', unsafe_allow_html=True)

with row2_col1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="soft-title">📉 Vergleich Test vs Custom</div><div class="soft-sub">Side-by-side, synchroner Zeitraum</div>', unsafe_allow_html=True)
    comp = []
    for c in ["test_domain", "catchment_custom"]:
        ms, _ = load_data(file_signature(c), c)
        sub = ms[(ms["year"] >= years[0]) & (ms["year"] <= years[1])]
        comp.append({"catchment": c, "SMI Mittel": sub["smi_percent"].mean(), "Recharge Mittel": sub["recharge_percent"].mean(), "Runoff Mittel": sub["runoff_percent"].mean()})
    comp_df = pd.DataFrame(comp)
    bar = px.bar(comp_df.melt(id_vars="catchment", var_name="Metrik", value_name="Wert"), x="Metrik", y="Wert", color="catchment", barmode="group", color_discrete_sequence=["#FF4B4B", "#00C851"])
    bar.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(bar, use_container_width=True, config={"displaylogo": False})
    st.markdown('</div>', unsafe_allow_html=True)

with row2_col2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="soft-title">ℹ️ Kontext-Info</div><div class="soft-sub">Was bedeutet die aktuelle Auswahl?</div>', unsafe_allow_html=True)
    st.write(f"**Catchment:** `{catchment}`")
    st.write(f"**Zeitraum:** `{years[0]}-{years[1]}` · **Monat:** `{month_sel}` · **Klasse:** `{drought_sel}`")
    st.write(f"**Aktueller SMI:** `{latest['smi_percent']:.1f}` · **Status:** {label}")

    if st.session_state.focus_year and st.session_state.focus_month:
        focus_rows = flt[(flt["year"] == st.session_state.focus_year) & (flt["month"] == st.session_state.focus_month)]
        if not focus_rows.empty:
            r = focus_rows.iloc[0]
            st.info(
                f"Fokusmonat {st.session_state.focus_year}-{st.session_state.focus_month:02d}: "
                f"SMI {r['smi_percent']:.1f}, Recharge {r['recharge_percent']:.1f}, Runoff {r['runoff_percent']:.1f}"
            )

    st.markdown("---")
    st.write("**Abfluss-Validierung (Qobs vs Qsim)**")
    dsub = discharge[(discharge["year"] >= years[0]) & (discharge["year"] <= years[1])].copy()
    if "qobs" in dsub.columns and dsub["qobs"].notna().any():
        dfig = go.Figure()
        dfig.add_trace(go.Scatter(x=dsub["date"], y=dsub["qobs"], mode="lines", name="Qobs", line=dict(color="#FF4B4B", width=1.7)))
        dfig.add_trace(go.Scatter(x=dsub["date"], y=dsub["qsim"], mode="lines", name="Qsim", line=dict(color="#5DADE2", width=1.7)))
        dfig.update_layout(height=230, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified")
        st.plotly_chart(dfig, use_container_width=True, config={"displaylogo": False})

        m = calc_metrics(dsub["qsim"], dsub["qobs"])
        a, b, c, d = st.columns(4)
        a.metric("KGE", f"{m['KGE']:.3f}")
        b.metric("RMSE", f"{m['RMSE']:.3f}")
        c.metric("MAE", f"{m['MAE']:.3f}")
        d.metric("r", f"{m['r']:.3f}")
    else:
        st.warning("Qobs nicht verfügbar für die aktuelle Auswahl.")

    st.markdown('</div>', unsafe_allow_html=True)

st.caption("Auto-Reload aktiv (Cache TTL 5s bei Datenänderungen).")
