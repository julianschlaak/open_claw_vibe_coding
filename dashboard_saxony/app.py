from __future__ import annotations

from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.data_loader import load_saxony_data
from utils.plotting import (
    create_corr_heatmap,
    create_multiindex_timeseries,
    create_radar_plot,
    create_timeseries_plot,
    summary_stats,
)

st.set_page_config(page_title="Duerremonitor Sachsen", page_icon="💧", layout="wide", initial_sidebar_state="expanded")

css_path = Path(__file__).resolve().parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

st.title("💧 Duerremonitor Sachsen")
st.markdown("**Interaktives Dashboard fuer Bodenfeuchte und Drought-Monitoring (2005-2020)**")


@st.cache_data(show_spinner=True)
def _load_data():
    return load_saxony_data()


data = _load_data()
raster = data["raster"]
ts_mean = data["timeseries"].copy()
idx_df = data["smi"].copy()
all_dates = pd.to_datetime(raster["dates"])

# Session state
if "clicked_cell_id" not in st.session_state:
    st.session_state.clicked_cell_id = None
if "clicked_lat" not in st.session_state:
    st.session_state.clicked_lat = None
if "clicked_lon" not in st.session_state:
    st.session_state.clicked_lon = None
if "clicked_date" not in st.session_state:
    st.session_state.clicked_date = pd.to_datetime(raster["dates"][0]).date()


# Sidebar
st.sidebar.header("⚙️ Einstellungen")
st.sidebar.selectbox("Region", ["Sachsen (gesamt)"], index=0)
default_date = pd.Timestamp("2018-08-15")
if default_date < all_dates.min() or default_date > all_dates.max():
    default_date = all_dates.min()

min_date = all_dates.min().date()
max_date = all_dates.max().date()
if "selected_date" not in st.session_state:
    st.session_state.selected_date = default_date.date()

st.sidebar.markdown("**Datum**")
dcol1, dcol2, dcol3 = st.sidebar.columns([1, 2.4, 1])
with dcol1:
    if st.button("◀", key="date_prev"):
        d = pd.Timestamp(st.session_state.selected_date) - pd.Timedelta(days=1)
        if d.date() >= min_date:
            st.session_state.selected_date = d.date()
with dcol3:
    if st.button("▶", key="date_next"):
        d = pd.Timestamp(st.session_state.selected_date) + pd.Timedelta(days=1)
        if d.date() <= max_date:
            st.session_state.selected_date = d.date()
with dcol2:
    picked = st.date_input(
        " ",
        value=st.session_state.selected_date,
        min_value=min_date,
        max_value=max_date,
        key="date_picker",
        label_visibility="collapsed",
    )
    st.session_state.selected_date = picked

selected_date = st.session_state.selected_date

view = st.selectbox(
    "Ansicht waehlen",
    ["🌱 nFK", "💧 Vol. Bodenfeuchte", "📊 SMI", "🎯 Multi-Index", "📚 Wissenschaft & Quellen"],
    index=2,
)

max_cell_id = max(0, len(raster["grid"]) - 1)
default_cell = int(st.session_state.clicked_cell_id) if st.session_state.clicked_cell_id is not None else 0
default_cell = min(max(default_cell, 0), max_cell_id)
manual_cell = st.sidebar.number_input("Rasterzelle-ID (Fallback)", min_value=0, max_value=max_cell_id, value=default_cell, step=1)
if st.sidebar.button("Rasterzelle uebernehmen"):
    cid = int(manual_cell)
    st.session_state.clicked_cell_id = str(cid)
    st.session_state.clicked_lat = float(raster["grid"].loc[cid, "lat"])
    st.session_state.clicked_lon = float(raster["grid"].loc[cid, "lon"])
    st.session_state.clicked_date = selected_date


def t_index(d) -> int:
    t = pd.Timestamp(d)
    return int(np.argmin(np.abs(all_dates.values - t.to_datetime64())))


def nearest_cell_id(lat: float, lon: float) -> tuple[int, float, float]:
    grid = raster["grid"]
    dist2 = (grid["lat"] - lat) ** 2 + (grid["lon"] - lon) ** 2
    idx = int(dist2.idxmin())
    return idx, float(grid.loc[idx, "lat"]), float(grid.loc[idx, "lon"])


def nfk_class(v: float) -> tuple[str, str]:
    if v < 30:
        return "<30%", "#d73027"
    if v < 50:
        return "30-50%", "#fc8d59"
    if v < 70:
        return "50-70%", "#fee08b"
    if v < 85:
        return "70-85%", "#91bfdb"
    return ">85%", "#4575b4"


def smi_class(v: float) -> tuple[str, str]:
    if v < 2:
        return "<2", "#74192e"
    if v < 5:
        return "2-5", "#c0392b"
    if v < 10:
        return "5-10", "#e67e22"
    if v < 20:
        return "10-20", "#f1c40f"
    if v < 50:
        return "20-50", "#91cf60"
    return ">50", "#1c9649"


def smvol_class(v: float) -> tuple[str, str]:
    if v < 12:
        return "<12", "#d73027"
    if v < 20:
        return "12-20", "#fc8d59"
    if v < 28:
        return "20-28", "#fee08b"
    if v < 36:
        return "28-36", "#91bfdb"
    return ">=36", "#4575b4"


def mdi_class(v: float) -> tuple[str, str]:
    if v < 2:
        return "<2", "#74192e"
    if v < 5:
        return "2-5", "#c0392b"
    if v < 10:
        return "5-10", "#e67e22"
    if v < 20:
        return "10-20", "#f1c40f"
    if v < 50:
        return "20-50", "#91cf60"
    return ">50", "#1c9649"


def legend_table(title: str, items: list[tuple[str, str]]):
    st.markdown(f"**{title}**")
    html = ["<div style='display:flex; gap:10px; flex-wrap:wrap; margin:6px 0 10px 0;'>"]
    for label, color in items:
        html.append(f"<div style='display:flex; align-items:center; gap:6px;'><span style='display:inline-block;width:14px;height:14px;background:{color};border:1px solid #333'></span><span style='font-size:0.9rem'>{label}</span></div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def show_stats_cards(s: dict, with_percent: bool = False):
    """Render clearly labeled statistics cards."""
    suf = "%" if with_percent else ""
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Mittelwert**")
        st.metric(" ", f"{s['mean']:.1f}{suf}")
    with c2:
        st.markdown("**Standardabweichung**")
        st.metric(" ", f"{s['std']:.1f}{suf}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Minimum**")
        st.metric(" ", f"{s['min']:.1f}{suf}")
    with c2:
        st.markdown("**Maximum**")
        st.metric(" ", f"{s['max']:.1f}{suf}")


def render_raster(metric: str, height: int = 560):
    i = t_index(selected_date)
    grid = raster["grid"].copy()

    if metric == "nfk":
        values = raster["nfk"][i, :]
        cls_fn = nfk_class
    elif metric == "sm_vol":
        values = raster["sm_vol"][i, :]
        cls_fn = smvol_class
    elif metric == "mdi":
        values = raster["mdi"][i, :]
        cls_fn = mdi_class
    else:
        values = raster["smi"][i, :]
        cls_fn = smi_class

    grid["value"] = values
    classes = grid["value"].apply(cls_fn)
    grid["class"] = classes.apply(lambda x: x[0])
    grid["color"] = classes.apply(lambda x: x[1])

    center = raster["boundary"].geometry.iloc[0].centroid
    m = folium.Map(location=[center.y, center.x], zoom_start=7.9, tiles="CartoDB positron")

    folium.GeoJson(
        grid,
        style_function=lambda f: {
            "fillColor": f["properties"]["color"],
            "color": "#1f2937",
            "weight": 0.2,
            "fillOpacity": 0.88,
        },
        highlight_function=lambda f: {"weight": 1.4, "fillOpacity": 0.95},
        tooltip=folium.GeoJsonTooltip(fields=["value", "class", "lat", "lon"], aliases=["Wert", "Klasse", "lat", "lon"]),
    ).add_to(m)

    folium.GeoJson(
        raster["boundary"],
        style_function=lambda _: {"fillColor": "transparent", "color": "#0f172a", "weight": 2.5, "fillOpacity": 0},
    ).add_to(m)

    out = st_folium(m, width=820, height=height, returned_objects=["last_clicked"])
    clicked = out.get("last_clicked") if out else None
    if clicked and "lat" in clicked and "lng" in clicked:
        cell_idx, lat, lon = nearest_cell_id(clicked["lat"], clicked["lng"])
        st.session_state.clicked_cell_id = str(cell_idx)
        st.session_state.clicked_lat = lat
        st.session_state.clicked_lon = lon
        st.session_state.clicked_date = selected_date
        st.info(f"Zelle gewaehlt: id={cell_idx}, lat={lat:.3f}, lon={lon:.3f}")


def metric_series(metric_key: str) -> pd.DataFrame:
    """Return time series for selected cell (if set) else Saxony mean."""
    if st.session_state.clicked_cell_id is not None:
        cid = int(st.session_state.clicked_cell_id)
        arr = raster[metric_key][:, cid]
        out = pd.DataFrame({"date": all_dates, "value": arr, "selection": f"Zelle {cid}"})
        return out

    map_mean_key = {"nfk": "nfk_pct", "sm_vol": "sm_vol_pct", "smi": "smi", "mdi": "mdi"}
    col = map_mean_key[metric_key]
    out = ts_mean[["date", col]].rename(columns={col: "value"}).copy()
    out["selection"] = "Sachsen (Mittel)"
    return out


def radar_data_for_selection() -> dict:
    d = idx_df.copy()
    d["date"] = pd.to_datetime(d["date"])
    target = pd.Timestamp(st.session_state.clicked_date)
    nearest = d.iloc[(d["date"] - target).abs().argsort()[:1]]
    row = nearest.mean(numeric_only=True)

    i = t_index(st.session_state.clicked_date)
    cell_id = int(st.session_state.clicked_cell_id) if st.session_state.clicked_cell_id is not None else 0
    smi_cell = float(raster["smi"][i, cell_id]) if 0 <= cell_id < raster["smi"].shape[1] else float(np.nan)
    nfk_cell = float(raster["nfk"][i, cell_id]) if 0 <= cell_id < raster["nfk"].shape[1] else float(np.nan)
    mdi_cell = float(raster["mdi"][i, cell_id]) if 0 <= cell_id < raster["mdi"].shape[1] else float(np.nan)

    return {
        "SMI": smi_cell,
        "R-Pctl": float(row.get("r_pctl", 50.0)),
        "Q-Pctl": float(row.get("q_pctl", 50.0)),
        "MDI": mdi_cell,
        "SPI-3": float((row.get("spi_3", 0.0) + 3) / 6 * 100),
        "SPEI-3": float((row.get("spei_3", 0.0) + 3) / 6 * 100),
        "%nFK": nfk_cell,
    }


if view == "🌱 nFK":
    st.header("Nutzbare Feldkapazitaet (%nFK) - Raster")
    legend_table("Legende nFK-Klassen (%)", [
        ("<30%", "#d73027"), ("30-50%", "#fc8d59"), ("50-70%", "#fee08b"), ("70-85%", "#91bfdb"), (">85%", "#4575b4")
    ])
    c1, c2 = st.columns([2.2, 1.2])
    with c1:
        render_raster("nfk")
    with c2:
        m = metric_series("nfk")
        fig = create_timeseries_plot(m, "date", "value", f"nFK Zeitreihe - {m['selection'].iloc[0]}", "%nFK")
        fig.add_hline(y=30, line_dash="dash", line_color="#b00020", annotation_text="Trockenstress")
        fig.add_hline(y=50, line_dash="dash", line_color="#f18f01", annotation_text="Beginnender Stress")
        st.plotly_chart(fig, use_container_width=True)
        s = summary_stats(m["value"])
        show_stats_cards(s, with_percent=True)

elif view == "💧 Vol. Bodenfeuchte":
    st.header("Volumetrische Bodenfeuchte (Vol.%) - Raster")
    legend_table("Legende Vol.-SM-Klassen (Vol.%)", [
        ("<12", "#d73027"), ("12-20", "#fc8d59"), ("20-28", "#fee08b"), ("28-36", "#91bfdb"), (">=36", "#4575b4")
    ])
    c1, c2 = st.columns([2.2, 1.2])
    with c1:
        render_raster("sm_vol")
    with c2:
        m = metric_series("sm_vol")
        fig = create_timeseries_plot(m, "date", "value", f"Vol. Bodenfeuchte - {m['selection'].iloc[0]}", "Vol.%")
        st.plotly_chart(fig, use_container_width=True)
        s = summary_stats(m["value"])
        show_stats_cards(s, with_percent=False)

elif view == "📊 SMI":
    st.header("Soil Moisture Index (SMI) - Raster")
    legend_table("Legende SMI-Klassen (UFZ-Schwellen)", [
        ("<2", "#74192e"), ("2-5", "#c0392b"), ("5-10", "#e67e22"), ("10-20", "#f1c40f"), ("20-50", "#91cf60"), (">50", "#1c9649")
    ])
    c1, c2 = st.columns([2.2, 1.2])
    with c1:
        render_raster("smi")
    with c2:
        m = metric_series("smi")
        fig = create_timeseries_plot(m, "date", "value", f"SMI Zeitreihe - {m['selection'].iloc[0]}", "SMI")
        fig.add_hline(y=20, line_dash="dash", line_color="#f18f01", annotation_text="Drought threshold")
        st.plotly_chart(fig, use_container_width=True)
        s = summary_stats(m["value"])
        show_stats_cards(s, with_percent=False)

elif view == "🎯 Multi-Index":
    st.header("Multi-Index Vergleich")
    st.markdown("**Klicke auf die MDI-Karte, um Radar/Stats zu aktualisieren.**")
    legend_table("Legende MDI-Klassen", [
        ("<2", "#74192e"), ("2-5", "#c0392b"), ("5-10", "#e67e22"), ("10-20", "#f1c40f"), ("20-50", "#91cf60"), (">50", "#1c9649")
    ])

    c_map, c_radar = st.columns([2.0, 1.4])
    with c_map:
        render_raster("mdi", height=500)

    if st.session_state.clicked_cell_id is None:
        st.info("Keine Zelle gewaehlt. Nutze MDI-Karte oder Fallback-ID in der Sidebar.")
        radar = {
            "SMI": float(ts_mean["smi"].mean()),
            "R-Pctl": float(idx_df["r_pctl"].mean()),
            "Q-Pctl": float(idx_df["q_pctl"].mean()),
            "MDI": float(ts_mean["mdi"].mean()),
            "SPI-3": float((idx_df["spi_3"].mean() + 3) / 6 * 100),
            "SPEI-3": float((idx_df["spei_3"].mean() + 3) / 6 * 100),
            "%nFK": float(ts_mean["nfk_pct"].mean()),
        }
    else:
        st.success(f"Zelle: {st.session_state.clicked_cell_id} | Datum: {st.session_state.clicked_date}")
        radar = radar_data_for_selection()

    with c_radar:
        st.plotly_chart(create_radar_plot(radar), use_container_width=True, key=f"radar_{st.session_state.clicked_cell_id}_{st.session_state.clicked_date}")

    st.subheader("Zeitreihen-Vergleich")
    st.plotly_chart(create_multiindex_timeseries(idx_df), use_container_width=True)

    with st.expander("Details / Debug"):
        st.json(radar)
        corr_cols = [c for c in ["smi", "r_pctl", "q_pctl", "mdi", "spi_3", "spei_3"] if c in idx_df.columns]
        st.plotly_chart(create_corr_heatmap(idx_df, corr_cols), use_container_width=True)

else:
    st.header("📚 Wissenschaft & Quellen")
    st.markdown(
        "Dieses Dashboard nutzt standardisierte Drought-Methoden und dokumentiert Formeln, Datenquellen und Limitationen transparent."
    )

    st.subheader("🧮 Formeln der Indices")
    with st.expander("🌱 %nFK (Plant Available Water)"):
        st.markdown(
            """
**Formel**
```text
PAW = (SWC - WP) / (FC - WP) * 100
```
- `SWC`: Soil Water Content
- `FC`: Feldkapazität
- `WP`: Welkepunkt

Im Dashboard aktuell als robust skalierter Raster-Proxy aus `SM_Lall` genutzt.
"""
        )

    with st.expander("💧 Volumetrische Bodenfeuchte"):
        st.markdown(
            """
**Formel**
```text
SM_vol = SM / Bodentiefe * 100
```
Im Dashboard als Vol.% Raster mit plausibler Klassierung dargestellt.
"""
        )

    with st.expander("📊 SMI (Soil Moisture Index)"):
        st.markdown(
            """
**Prinzip**
```text
SMI(d, y) = Rank[SM(d, y)] / N * 100
```
Day-of-Year-basierte Perzentile (nicht-parametrisch).

Klassen:
- `<2` extrem
- `2-5` schwer
- `5-10` mäßig
- `10-20` leicht
- `20-50` normal
- `>50` nass
"""
        )

    with st.expander("🎯 MDI (Matrix Drought Index)"):
        st.markdown(
            """
**Kombinationsidee**
```text
MDI = 0.4 * SMI + 0.3 * R-Pctl + 0.3 * Q-Pctl
```
Im Karten-Tab als zellbasierter Proxy mit Lag-Komponenten umgesetzt (`lag30`, `lag60`) für robuste Interaktivität.
"""
        )

    with st.expander("🌧️ SPI / 🌡️ SPEI"):
        st.markdown(
            """
- `SPI`: standardisierter Niederschlagsindex  
- `SPEI`: standardisierte Wasserbilanz `P - PET`  
Zeitskalen typischerweise 1/3/6 Monate.
"""
        )

    st.divider()
    st.subheader("📁 Datenquellen")
    ds1, ds2 = st.columns(2)
    with ds1:
        st.markdown(
            """
| Variable | Quelle | Zeitraum |
|---|---|---|
| Bodenfeuchte / Recharge / Abfluss | mHM 5.13.2 | 2005-2020 |
| Qobs | CAMELS-DE / daily_discharge.out | 2005-2020 |
| Drought-Indizes | Pipeline `01-05` | 2005-2020 |
"""
        )
    with ds2:
        st.markdown(
            """
| Geodaten | Quelle |
|---|---|
| Sachsen-Grenze | `Sachsen.shp` (lokal, BKG-basiert) |
| Raster | mHM Grid (0.0625°) |

EDID/EDII:
- DOI: https://doi.org/10.6094/UNIFR/230922
"""
        )

    st.divider()
    st.subheader("⚠️ Unsicherheiten & Limitationen")
    st.markdown(
        """
- Modellparameter- und Forcing-Unsicherheit (mHM + Inputdaten)
- SMI-Referenzzeitraum 2005-2020 ist relativ kurz für Extremstatistik
- MDI-Gewichte sind fachlich motiviert, nicht global optimiert
- Rasterauflösung 0.0625° glättet lokale Effekte
"""
    )

    st.divider()
    st.subheader("📖 Zitiervorschlag")
    st.code(
        "Schlaak, J. (2026). Duerremonitor Sachsen [Dashboard]. University of Leipzig. URL: http://187.124.13.209:8502/",
        language="text",
    )

    st.subheader("🔗 Weiterführende Links")
    st.markdown(
        """
- mHM: https://www.mhm-model.org/
- CAMELS-DE: https://doi.org/10.1594/PANGAEA.894938
- EDID/EDII: https://doi.org/10.6094/UNIFR/230922
- UFZ Dürremonitor: https://www.ufz.de/index.php?de=39399
"""
    )

# Sidebar selection stats (dynamic, follows active view + cell selection)
st.sidebar.markdown("---")
st.sidebar.subheader("Auswahl-Statistik")
metric_for_view = {
    "🌱 nFK": "nfk",
    "💧 Vol. Bodenfeuchte": "sm_vol",
    "📊 SMI": "smi",
    "🎯 Multi-Index": "mdi",
    "📚 Wissenschaft & Quellen": "smi",
}[view]
series = metric_series(metric_for_view)
ss = summary_stats(series["value"])
st.sidebar.markdown("**Mittelwert**")
st.sidebar.metric(" ", f"{ss['mean']:.1f}")
st.sidebar.markdown("**Median**")
st.sidebar.metric(" ", f"{ss['median']:.1f}")
st.sidebar.markdown("**Standardabweichung**")
st.sidebar.metric(" ", f"{ss['std']:.1f}")
