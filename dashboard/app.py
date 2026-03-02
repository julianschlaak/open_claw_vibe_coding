#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Hydrological Drought Dashboard", layout="wide")

BASE = Path(__file__).resolve().parents[1]
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

MONTH_NAMES = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
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
def load_data(_sig: tuple, catchment: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_path = CATCHMENT_FILES[catchment]["monthly"]
    discharge_path = CATCHMENT_FILES[catchment]["discharge"]

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

    return monthly, discharge


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


st.title("🌍 Hydrological Drought Dashboard")
st.caption("Interaktive Analyse von SMI, Recharge, Runoff und Discharge-Validierung")

st.sidebar.header("Filter")
catchment = st.sidebar.selectbox("Catchment", ["test_domain", "catchment_custom"], index=0)

sig = _file_signature([CATCHMENT_FILES[catchment]["monthly"], CATCHMENT_FILES[catchment]["discharge"]])
monthly_df, discharge_df = load_data(sig, catchment)

min_year = int(monthly_df["year"].min())
max_year = int(monthly_df["year"].max())
default_min = max(min_year, 1990)
default_max = min(max_year, 2020)

years = st.sidebar.slider(
    "Zeitraum",
    min_value=min_year,
    max_value=max_year,
    value=(default_min, default_max),
)
month_sel = st.sidebar.selectbox("Monat", ["Alle"] + list(MONTH_NAMES.values()), index=0)
drought_sel = st.sidebar.selectbox("Dürre-Klasse", list(DROUGHT_CLASS_MAP.keys()), index=0)

filtered = filter_monthly(monthly_df, years, month_sel, drought_sel)

if filtered.empty:
    st.warning("Keine Daten für die aktuelle Filterkombination.")
    st.stop()

# Tabs
heatmap_tab, ts_tab, discharge_tab = st.tabs(["SMI Heatmap", "Zeitreihen", "Abfluss-Validierung"])

with heatmap_tab:
    heat = filtered.pivot_table(index="year", columns="month", values="smi_percent", aggfunc="mean")
    heat = heat.reindex(columns=list(range(1, 13)))

    fig_h = go.Figure(
        data=go.Heatmap(
            z=heat.values,
            x=[MONTH_NAMES[m] for m in heat.columns],
            y=heat.index,
            colorscale=[
                [0.0, "#8b0000"],
                [0.25, "#d7301f"],
                [0.5, "#fdae61"],
                [0.75, "#a6d96a"],
                [1.0, "#1a9850"],
            ],
            zmin=0,
            zmax=100,
            colorbar={"title": "SMI Percentile"},
            hovertemplate="Jahr: %{y}<br>Monat: %{x}<br>SMI: %{z:.1f}<extra></extra>",
        )
    )
    fig_h.update_layout(height=550, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_h, use_container_width=True)

with ts_tab:
    variable_options = {
        "SMI": "smi_percent",
        "Recharge": "recharge_percent",
        "Runoff": "runoff_percent",
        "SSI": "ssi",
        "SDI": "sdi",
    }
    selected = st.multiselect(
        "Variablen auswählen",
        options=list(variable_options.keys()),
        default=["SMI", "Recharge", "Runoff"],
    )

    if selected:
        fig_ts = go.Figure()
        for name in selected:
            col = variable_options[name]
            fig_ts.add_trace(
                go.Scatter(
                    x=filtered["date"],
                    y=filtered[col],
                    mode="lines",
                    name=name,
                )
            )
        fig_ts.update_layout(
            height=520,
            xaxis_title="Datum",
            yaxis_title="Index / Perzentil",
            hovermode="x unified",
            dragmode="zoom",
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("Bitte mindestens eine Variable auswählen.")

with discharge_tab:
    discharge_filtered = discharge_df[
        (discharge_df["year"] >= years[0]) & (discharge_df["year"] <= years[1])
    ].copy()

    has_qobs = "qobs" in discharge_filtered.columns and discharge_filtered["qobs"].notna().any()
    has_qsim = "qsim" in discharge_filtered.columns and discharge_filtered["qsim"].notna().any()

    if not has_qsim:
        st.warning("Qsim nicht verfügbar.")
    else:
        fig_d = go.Figure()
        if has_qobs:
            fig_d.add_trace(
                go.Scatter(
                    x=discharge_filtered["date"],
                    y=discharge_filtered["qobs"],
                    mode="lines",
                    name="Qobs",
                    line=dict(color="red", width=1.6),
                )
            )
        fig_d.add_trace(
            go.Scatter(
                x=discharge_filtered["date"],
                y=discharge_filtered["qsim"],
                mode="lines",
                name="Qsim",
                line=dict(color="blue", width=1.6),
            )
        )
        fig_d.update_layout(
            height=520,
            xaxis_title="Datum",
            yaxis_title="Abfluss",
            hovermode="x unified",
            dragmode="zoom",
            margin=dict(l=20, r=20, t=40, b=20),
        )
        st.plotly_chart(fig_d, use_container_width=True)

        if has_qobs:
            metrics = calc_metrics(discharge_filtered["qsim"], discharge_filtered["qobs"])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("KGE", f"{metrics['KGE']:.3f}")
            c2.metric("RMSE", f"{metrics['RMSE']:.3f}")
            c3.metric("MAE", f"{metrics['MAE']:.3f}")
            c4.metric("r", f"{metrics['r']:.3f}")
        else:
            st.info("Qobs nicht verfügbar. Metriken werden nur mit Beobachtungen angezeigt.")

st.caption("Hinweis: Daten werden bei Dateiänderungen automatisch neu geladen (cache ttl: 5s).")
