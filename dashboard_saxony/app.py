from __future__ import annotations

from pathlib import Path

import folium
import numpy as np
import pandas as pd
import streamlit as st
from folium.plugins import Draw
from shapely.geometry import shape
from streamlit_folium import st_folium

from utils.data_loader import load_saxony_data
from utils.plotting import (
    create_corr_heatmap,
    create_multiindex_timeseries,
    create_radar_plot,
    create_timeseries_plot,
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
if "selected_cell_ids" not in st.session_state:
    st.session_state.selected_cell_ids = []


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
if "date_picker" not in st.session_state:
    st.session_state.date_picker = st.session_state.selected_date

st.sidebar.markdown("**Datum**")
dcol1, dcol2, dcol3 = st.sidebar.columns([1, 2.4, 1])
with dcol1:
    if st.button("◀", key="date_prev"):
        d = pd.Timestamp(st.session_state.selected_date) - pd.Timedelta(days=1)
        if d.date() >= min_date:
            st.session_state.selected_date = d.date()
            st.session_state.date_picker = d.date()
with dcol3:
    if st.button("▶", key="date_next"):
        d = pd.Timestamp(st.session_state.selected_date) + pd.Timedelta(days=1)
        if d.date() <= max_date:
            st.session_state.selected_date = d.date()
            st.session_state.date_picker = d.date()
with dcol2:
    st.date_input(
        " ",
        min_value=min_date,
        max_value=max_date,
        key="date_picker",
        label_visibility="collapsed",
    )
    st.session_state.selected_date = st.session_state.date_picker

selected_date = st.session_state.selected_date

VIEW_OPTIONS = ["🌱 nFK", "💧 Vol. Bodenfeuchte", "📊 SMI", "🎯 Multi-Index", "📚 Wissenschaft & Quellen"]
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "📊 SMI"

st.markdown("**Ansicht waehlen**")
bar = st.container()
with bar:
    bcols = st.columns(len(VIEW_OPTIONS))
    for i, opt in enumerate(VIEW_OPTIONS):
        with bcols[i]:
            selected = st.session_state.view_mode == opt
            if st.button(opt, key=f"view_btn_{i}", use_container_width=True, type="primary" if selected else "secondary"):
                st.session_state.view_mode = opt

view = st.session_state.view_mode

NFK_CLASSES = [
    {"range": "< 30%", "label": "Trockenstress", "description": "Pflanzen leiden unter Wassermangel", "color": "#d73027"},
    {"range": "30-50%", "label": "Warnung", "description": "Beginnender Trockenstress", "color": "#fc8d59"},
    {"range": "50-70%", "label": "Optimal", "description": "Ideale Wasserversorgung", "color": "#fee08b"},
    {"range": "70-85%", "label": "Feucht", "description": "Ausreichend Wasser verfuegbar", "color": "#91bfdb"},
    {"range": "> 85%", "label": "Gesaettigt", "description": "Nahe Feldkapazitaet", "color": "#4575b4"},
]

SMI_CLASSES = [
    {"range": "< 2", "label": "Extreme Duerre", "description": "Seltener als 1-in-50-Jahre Ereignis", "color": "#74192e"},
    {"range": "2-5", "label": "Schwere Duerre", "description": "1-in-20-Jahre Ereignis", "color": "#c0392b"},
    {"range": "5-10", "label": "Maessige Duerre", "description": "1-in-10-Jahre Ereignis", "color": "#e67e22"},
    {"range": "10-20", "label": "Leichte Duerre", "description": "Trocken, aber nicht aussergewoehnlich", "color": "#f1c40f"},
    {"range": "20-50", "label": "Normal", "description": "Durchschnittliche Bedingungen", "color": "#91cf60"},
    {"range": "> 50", "label": "Feucht", "description": "Feuchter als Durchschnitt", "color": "#1c9649"},
]

MDI_CLASSES = [
    {"range": "< 20", "label": "Extreme Duerre", "description": "Alle Kompartimente stark betroffen", "color": "#74192e"},
    {"range": "20-40", "label": "Schwere Duerre", "description": "Mehrere Kompartimente defizitaer", "color": "#c0392b"},
    {"range": "40-60", "label": "Moderate Duerre", "description": "Einzelne Kompartimente defizitaer", "color": "#e67e22"},
    {"range": "60-80", "label": "Unauffaellig", "description": "Keine ausgepraegten Defizite", "color": "#91cf60"},
    {"range": "> 80", "label": "Feucht", "description": "Ueberdurchschnittliche Wasserverfuegbarkeit", "color": "#1c9649"},
]

SMVOL_CLASSES = [
    {"range": "<12", "label": "Sehr trocken", "description": "Niedriger Wassergehalt", "color": "#d73027"},
    {"range": "12-20", "label": "Trocken", "description": "Defizit in der Wurzelzone", "color": "#fc8d59"},
    {"range": "20-28", "label": "Mittel", "description": "Uebergangsbereich", "color": "#fee08b"},
    {"range": "28-36", "label": "Feucht", "description": "Gute Wasserversorgung", "color": "#91bfdb"},
    {"range": ">=36", "label": "Sehr feucht", "description": "Nahe Saettigung", "color": "#4575b4"},
]

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
        return "Trockenstress (<30%)", "#d73027"
    if v < 50:
        return "Warnung (30-50%)", "#fc8d59"
    if v < 70:
        return "Optimal (50-70%)", "#fee08b"
    if v < 85:
        return "Feucht (70-85%)", "#91bfdb"
    return "Gesaettigt (>85%)", "#4575b4"


def smi_class(v: float) -> tuple[str, str]:
    if v < 2:
        return "Extreme Duerre (<2)", "#74192e"
    if v < 5:
        return "Schwere Duerre (2-5)", "#c0392b"
    if v < 10:
        return "Maessige Duerre (5-10)", "#e67e22"
    if v < 20:
        return "Leichte Duerre (10-20)", "#f1c40f"
    if v < 50:
        return "Normal (20-50)", "#91cf60"
    return "Feucht (>50)", "#1c9649"


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
    if v < 20:
        return "Extreme Duerre (<20)", "#74192e"
    if v < 40:
        return "Schwere Duerre (20-40)", "#c0392b"
    if v < 60:
        return "Moderate Duerre (40-60)", "#e67e22"
    if v < 80:
        return "Unauffaellig (60-80)", "#91cf60"
    return "Feucht (>80)", "#1c9649"


def legend_table(title: str, items: list[tuple[str, str]]):
    st.markdown(f"**{title}**")
    html = ["<div style='display:flex; gap:10px; flex-wrap:wrap; margin:6px 0 10px 0;'>"]
    for label, color in items:
        html.append(f"<div style='display:flex; align-items:center; gap:6px;'><span style='display:inline-block;width:14px;height:14px;background:{color};border:1px solid #333'></span><span style='font-size:0.9rem'>{label}</span></div>")
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def class_table(title: str, classes: list[dict]):
    st.markdown(f"**{title}**")
    cdf = pd.DataFrame([{"Bereich": c["range"], "Klasse": c["label"], "Beschreibung": c["description"]} for c in classes])
    st.dataframe(cdf, use_container_width=True, hide_index=True)


def current_value(metric_key: str) -> float:
    i = t_index(selected_date)
    if st.session_state.clicked_cell_id is not None:
        cid = int(st.session_state.clicked_cell_id)
        return float(raster[metric_key][i, cid])
    series = metric_series(metric_key)
    idx = int(np.argmin(np.abs(pd.to_datetime(series["date"]).values - pd.Timestamp(selected_date).to_datetime64())))
    return float(series.iloc[idx]["value"])


def show_current_value_card(label: str, value: float, unit: str, cls_text: str):
    st.markdown(
        f"""
<div class="current-value-card">
  <div class="cv-label">{label}</div>
  <div class="cv-value">{value:.1f}{unit}</div>
  <div class="cv-sub">{cls_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def build_selection_timeseries(metric_key: str, ids: list[int]) -> pd.DataFrame:
    arr = raster[metric_key][:, ids]
    out = pd.DataFrame({"date": pd.to_datetime(all_dates)})
    for j, cid in enumerate(ids):
        out[f"cell_{cid}"] = arr[:, j]
    out["area_mean"] = np.nanmean(arr, axis=1)
    return out


def render_selection_tool(metric_key: str, unit: str, cls_fn):
    sb = st.sidebar
    sb.markdown("---")
    sb.markdown("**Raster-Auswahl & Export**")
    ids = [int(x) for x in st.session_state.selected_cell_ids] if st.session_state.selected_cell_ids else []

    c1, c2 = sb.columns(2)
    with c1:
        if sb.button("Auswahl leeren", key=f"clear_sel_{metric_key}"):
            st.session_state.selected_cell_ids = []
            ids = []
    with c2:
        if sb.button("Klickzelle +", key=f"add_click_{metric_key}") and st.session_state.clicked_cell_id is not None:
            merged = sorted(set(ids + [int(st.session_state.clicked_cell_id)]))
            st.session_state.selected_cell_ids = merged
            ids = merged

    sb.caption("Mehrfachauswahl: Auf der Karte ein Rechteck zeichnen, um mehrere Rasterzellen zu markieren.")
    sb.write(f"Ausgewaehlte Zellen: **{len(ids)}**")

    if len(ids) > 0:
        i = t_index(selected_date)
        day_vals = raster[metric_key][i, ids]
        area_mean_now = float(np.nanmean(day_vals))
        area_class = cls_fn(area_mean_now)[0]
        sb.metric("Aktuelles Flaechenmittel", f"{area_mean_now:.1f}{unit}")
        sb.caption(f"Klasse (Flaechenmittel): {area_class}")

        ts = build_selection_timeseries(metric_key, ids)
        sb.download_button(
            "CSV Download (alle ausgewaehlten Pixel)",
            data=ts.to_csv(index=False).encode("utf-8"),
            file_name=f"{metric_key}_selected_cells_timeseries.csv",
            mime="text/csv",
            key=f"dl_sel_{metric_key}",
        )
    else:
        sb.info("Keine Rasterzellen ausgewaehlt.")


def describe_current_condition(metric_key: str, value: float, cls_text: str) -> str:
    if metric_key == "smi":
        if value < 2:
            return "Die Zelle zeigt eine extreme Duerresituation. Sehr niedrige Bodenfeuchtewerte treten nur selten auf und gehen oft mit erhoehtem Vegetationsstress einher."
        if value < 5:
            return "Es liegt eine schwere Duerre vor. Der Boden ist fuer die Jahreszeit deutlich trockener als ueblich, was die Pflanzenwasserversorgung klar einschraenkt."
        if value < 10:
            return "Maessige Duerre: Die Feuchte ist klar unter dem saisonalen Normalzustand, aber noch nicht im Extrembereich."
        if value < 20:
            return "Leichte Duerre: Erste Trockenheitssignale sind sichtbar; empfindliche Standorte reagieren oft bereits."
        if value < 50:
            return "Die Bedingungen sind im normalen Bereich. Fuer den Standort ist aktuell keine ausgepraegte Duerre erkennbar."
        return "Die Zelle ist feuchter als der historische Mittelbereich. Kurzfristig ist die Duerregefahr gering."
    if metric_key == "nfk":
        if value < 30:
            return "Die pflanzenverfuegbare Bodenwasserreserve ist niedrig. In der Praxis entspricht das oft Trockenstress fuer flachwurzelnde Kulturen."
        if value < 50:
            return "Der Speicher fuellt den Bedarf nur teilweise. Ohne Niederschlagsnachschub kann sich Trockenstress rasch verstaerken."
        if value < 70:
            return "Der Bereich ist agronomisch guenstig: meist ausreichende Wasserversorgung bei noch guter Durchlueftung."
        if value < 85:
            return "Die Bodenwasserversorgung ist gut bis hoch. Kurzfristiger Trockenstress ist unwahrscheinlich."
        return "Nahe Saettigung: viel Wasser verfuegbar, lokal kann aber die Belueftung des Wurzelraums abnehmen."
    if metric_key == "sm_vol":
        if value < 12:
            return "Sehr niedriger volumetrischer Wassergehalt. Der Boden ist trocken, und nutzbares Wasser ist stark begrenzt."
        if value < 20:
            return "Trockener Bereich mit reduziertem Wasserangebot. Pflanzen koennen bereits eingeschraenkt reagieren."
        if value < 28:
            return "Mittlerer Feuchtebereich. Die Wasserversorgung ist vorhanden, aber nicht komfortabel."
        if value < 36:
            return "Feuchter Bereich mit guter Verfuegbarkeit im Wurzelraum."
        return "Sehr feucht bis nahe Saettigung. Duerre ist unwahrscheinlich, lokal sind Staunaesseffekte moeglich."
    if metric_key == "mdi":
        if value < 20:
            return "Der kombinierte Index zeigt eine starke Gesamtdürre in mehreren Kompartimenten (Boden, Neubildung, Abfluss)."
        if value < 40:
            return "Deutliches Mehrkomponenten-Defizit: die Duerresignale sind hydrologisch breit abgestuetzt."
        if value < 60:
            return "Moderates Defizit: einzelne Komponenten sind trocken, die Gesamtlage bleibt gemischt."
        if value < 80:
            return "Unauffaelliger Gesamtzustand ohne starke Mehrkomponenten-Duerre."
        return "Ueberdurchschnittlich feuchte Gesamtlage im Mehrkomponentenvergleich."
    return f"Aktueller Zustand: {cls_text}."


def show_condition_text(metric_key: str, value: float, cls_text: str):
    text = describe_current_condition(metric_key, value, cls_text)
    st.markdown(
        f"""
<div class="condition-note">
  <div class="condition-title">Kurzbewertung der aktuellen Rasterzelle</div>
  <div class="condition-main">Aktueller Wert: <b>{value:.1f}</b> | Klasse: <b>{cls_text}</b></div>
  <div class="condition-body">{text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


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
    m = folium.Map(location=[center.y, center.x], zoom_start=7.9, tiles="CartoDB dark_matter", control_scale=True)

    cities = {
        "Dresden": (51.05, 13.74),
        "Leipzig": (51.34, 12.38),
        "Chemnitz": (50.83, 12.92),
        "Goerlitz": (51.15, 14.99),
        "Zwickau": (50.72, 12.50),
    }
    for city, (clat, clon) in cities.items():
        folium.map.Marker(
            [clat, clon],
            icon=folium.DivIcon(
                html=f"<div style='font-size:11px;color:#f8fafc;font-weight:700;text-shadow:0 0 4px #000;'>{city}</div>"
            ),
        ).add_to(m)

    folium.GeoJson(
        grid,
        style_function=lambda f: {
            "fillColor": f["properties"]["color"],
            "color": "#2c3e50",
            "weight": 0.8,
            "fillOpacity": 0.68,
        },
        highlight_function=lambda f: {"weight": 1.4, "fillOpacity": 0.82},
        tooltip=folium.GeoJsonTooltip(fields=["value", "class", "lat", "lon"], aliases=["Wert", "Klasse", "lat", "lon"]),
    ).add_to(m)

    folium.GeoJson(
        raster["boundary"],
        style_function=lambda _: {"fillColor": "transparent", "color": "#0f172a", "weight": 2.5, "fillOpacity": 0},
    ).add_to(m)

    Draw(
        export=False,
        draw_options={
            "polyline": False,
            "polygon": False,
            "circle": False,
            "circlemarker": False,
            "marker": False,
            "rectangle": True,
        },
        edit_options={"edit": True, "remove": True},
    ).add_to(m)

    out = st_folium(m, width=None, height=height, returned_objects=["last_clicked", "all_drawings"])
    clicked = out.get("last_clicked") if out else None
    if clicked and "lat" in clicked and "lng" in clicked:
        cell_idx, lat, lon = nearest_cell_id(clicked["lat"], clicked["lng"])
        st.session_state.clicked_cell_id = str(cell_idx)
        st.session_state.clicked_lat = lat
        st.session_state.clicked_lon = lon
        st.session_state.clicked_date = selected_date
        st.info(f"Zelle gewaehlt: id={cell_idx}, lat={lat:.3f}, lon={lon:.3f}")

    drawings = out.get("all_drawings") if out else None
    if drawings:
        draw_geoms = []
        for d in drawings:
            geom = d.get("geometry")
            if geom:
                try:
                    draw_geoms.append(shape(geom))
                except Exception:
                    pass
        if draw_geoms:
            selected = []
            for idx, g in enumerate(raster["grid"].geometry):
                for dg in draw_geoms:
                    if g.intersects(dg):
                        selected.append(idx)
                        break
            st.session_state.selected_cell_ids = sorted(set(selected))
            st.success(f"Auswahl aktualisiert: {len(st.session_state.selected_cell_ids)} Zellen")


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


selection_cfg = {
    "🌱 nFK": ("nfk", "%", nfk_class),
    "💧 Vol. Bodenfeuchte": ("sm_vol", " Vol.%", smvol_class),
    "📊 SMI": ("smi", "", smi_class),
    "🎯 Multi-Index": ("mdi", "", mdi_class),
}
if view in selection_cfg:
    mk, unit, cls_fn = selection_cfg[view]
    render_selection_tool(mk, unit, cls_fn)


if view == "🌱 nFK":
    st.header("Nutzbare Feldkapazitaet (%nFK) - Raster")
    st.info(
        "%nFK beschreibt den Anteil des fuer Pflanzen verfuegbaren Bodenwassers. "
        "Berechnet wird relativ zur Speicherkapazitaet zwischen Feldkapazitaet und Welkepunkt. "
        "Werte unter 30% deuten auf Trockenstress, Werte ueber 70% auf gute Versorgung. "
        "Quelle: KA5 (2005), Allen et al. (1998, FAO-56)."
    )
    c1, c2 = st.columns([2.5, 1.5])
    with c1:
        render_raster("nfk")
        legend_table("Farblegende nFK (%)", [(f"{c['range']}", c["color"]) for c in NFK_CLASSES])
        class_table("Klassengrenzen nFK", NFK_CLASSES)
    with c2:
        m = metric_series("nfk")
        cv = current_value("nfk")
        cv_class = nfk_class(cv)[0]
        show_current_value_card("Aktueller nFK-Wert", cv, "%", cv_class)
        fig = create_timeseries_plot(m, "date", "value", f"nFK Zeitreihe - {m['selection'].iloc[0]}", "%nFK")
        fig.add_hline(y=30, line_dash="dash", line_color="#b00020", annotation_text="Trockenstress")
        fig.add_hline(y=50, line_dash="dash", line_color="#f18f01", annotation_text="Beginnender Stress")
        st.markdown('<div class="plot-frame">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        legend_table("2. Legende nFK", [(f"{c['range']}", c["color"]) for c in NFK_CLASSES])
        show_condition_text("nfk", cv, cv_class)

elif view == "💧 Vol. Bodenfeuchte":
    st.header("Volumetrische Bodenfeuchte (Vol.%) - Raster")
    st.info(
        "Die volumetrische Bodenfeuchte zeigt den absoluten Wassergehalt im Boden in Volumenprozent. "
        "Typische Werte reichen von sehr trocken (~5%) bis nahe Saettigung (~45%). "
        "Im Dashboard wird der gesamte Wurzelraum abgebildet und taeglich aktualisiert. "
        "Quelle: Samaniego et al. (2013), mHM Dokumentation."
    )
    legend_table("Legende Vol.-SM-Klassen (Vol.%)", [
        ("<12", "#d73027"), ("12-20", "#fc8d59"), ("20-28", "#fee08b"), ("28-36", "#91bfdb"), (">=36", "#4575b4")
    ])
    c1, c2 = st.columns([2.5, 1.5])
    with c1:
        render_raster("sm_vol")
        class_table("Klassengrenzen Vol.-SM", SMVOL_CLASSES)
    with c2:
        m = metric_series("sm_vol")
        cv = current_value("sm_vol")
        cv_class = smvol_class(cv)[0]
        show_current_value_card("Aktuelle Bodenfeuchte", cv, " Vol.%", cv_class)
        fig = create_timeseries_plot(m, "date", "value", f"Vol. Bodenfeuchte - {m['selection'].iloc[0]}", "Vol.%")
        st.markdown('<div class="plot-frame">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        legend_table("2. Legende Vol.-SM", [(f"{c['range']}", c["color"]) for c in SMVOL_CLASSES])
        show_condition_text("sm_vol", cv, cv_class)

elif view == "📊 SMI":
    st.header("Soil Moisture Index (SMI) - Raster")
    st.info(
        "Der SMI vergleicht die aktuelle Bodenfeuchte mit historischen Werten desselben Kalendertages. "
        "Ein SMI von 5 bedeutet: trockener als 95% der Referenzwerte. "
        "Die Perzentil-Methode ist robust, weil sie keine feste Verteilungsannahme benoetigt. "
        "Quelle: Van Loon & Van Lanen (2012), Samaniego et al. (2013)."
    )
    c1, c2 = st.columns([2.5, 1.5])
    with c1:
        render_raster("smi")
        legend_table("Farblegende SMI", [(f"{c['range']}", c["color"]) for c in SMI_CLASSES])
        class_table("Klassengrenzen SMI", SMI_CLASSES)
    with c2:
        m = metric_series("smi")
        cv = current_value("smi")
        cv_class = smi_class(cv)[0]
        show_current_value_card("Aktueller SMI-Wert", cv, "", cv_class)
        fig = create_timeseries_plot(m, "date", "value", f"SMI Zeitreihe - {m['selection'].iloc[0]}", "SMI")
        fig.add_hline(y=20, line_dash="dash", line_color="#f18f01", annotation_text="Drought threshold")
        st.markdown('<div class="plot-frame">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        legend_table("2. Legende SMI", [(f"{c['range']}", c["color"]) for c in SMI_CLASSES])
        show_condition_text("smi", cv, cv_class)

elif view == "🎯 Multi-Index":
    st.header("Multi-Index Vergleich")
    st.info(
        "Der MDI kombiniert Bodenfeuchte, Grundwasserneubildung und Abfluss zu einem Gesamtindex. "
        "Die Gewichtung 0.4/0.3/0.3 bildet die Weitergabe von Duerresignalen durch den Wasserkreislauf ab. "
        "So werden kurzfristige und verzoegerte Effekte gemeinsam sichtbar. "
        "Quelle: Schlaak (2026, in prep.), inspiriert durch Hao & AghaKouchak (2013)."
    )
    st.markdown("**Klicke auf die MDI-Karte, um Radar und Statistiken zu aktualisieren.**")
    legend_table("Farblegende MDI", [(f"{c['range']}", c["color"]) for c in MDI_CLASSES])

    c_map, c_radar = st.columns([2.5, 1.5])
    with c_map:
        render_raster("mdi", height=500)
        class_table("Klassengrenzen MDI", MDI_CLASSES)

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
        cv = current_value("mdi")
        cv_class = mdi_class(cv)[0]
        show_current_value_card("Aktueller MDI-Wert", cv, "", cv_class)
        st.plotly_chart(create_radar_plot(radar), use_container_width=True, key=f"radar_{st.session_state.clicked_cell_id}_{st.session_state.clicked_date}")
        legend_table("2. Legende MDI", [(f"{c['range']}", c["color"]) for c in MDI_CLASSES])
        show_condition_text("mdi", cv, cv_class)

    st.subheader("Zeitreihen-Vergleich")
    st.plotly_chart(create_multiindex_timeseries(idx_df), use_container_width=True)

    with st.expander("Details / Debug"):
        st.json(radar)
        corr_cols = [c for c in ["smi", "r_pctl", "q_pctl", "mdi", "spi_3", "spei_3"] if c in idx_df.columns]
        st.plotly_chart(create_corr_heatmap(idx_df, corr_cols), use_container_width=True)

else:
    st.header("📚 Wissenschaft & Quellen")
    st.markdown("Dieser Bereich zeigt **nur Kernquellen** (Primärliteratur, Standards, Datensatz-Paper).")
    st.info(
        "SPI quantifiziert Niederschlagsdefizite auf standardisierter Skala, SPEI erweitert dies um Verdunstung "
        "und reagiert daher staerker auf Temperaturanstiege. Beide Indizes sind zeitskalenabhaengig "
        "(z. B. 1/3/6/12 Monate) und regional vergleichbar. "
        "Quelle: McKee et al. (1993), WMO (2012), Vicente-Serrano et al. (2010)."
    )

    st.subheader("🧮 Methodik mit belastbaren Kernquellen")
    with st.expander("🌱 %nFK / PAW"):
        st.markdown(
            """
**Formel**
```text
PAW = (SWC - WP) / (FC - WP) * 100
```
**Kernquellen**
- Allen et al. (1998), FAO-56 (Crop evapotranspiration; FC/WP/PAW Standardkonzepte)
- KA5 (2005), Bodenkundliche Kartieranleitung (Standardwerk Deutschland)
- Saxton & Rawls (2006), Schätzung bodenhydraulischer Eigenschaften. DOI: https://doi.org/10.2136/sssaj2005.0117
"""
        )
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("FAO-56 (offiziell)", "https://www.fao.org/3/X0490E/X0490E00.htm")
        with b2:
            st.link_button("KA5 (BGR)", "https://www.bgr.bund.de/DE/Themen/Boden/Informationsgrundlagen/Kartenwerke/Bodenkundliche_Kartieranleitung/kartieranleitung_node.html")

    with st.expander("📊 SMI (Perzentilbasiert)"):
        st.markdown(
            """
**Prinzip**
```text
SMI(d, y) = Rank[SM(d, y)] / N * 100
```
**Kernquellen**
- Samaniego, Kumar & Zink (2013), *J. Hydrometeorology*. DOI: https://doi.org/10.1175/JHM-D-12-075.1
- Van Loon & Van Lanen (2012), *HESS*. DOI: https://doi.org/10.5194/hess-16-1915-2012
- UFZ Dürremonitor Methodenhinweise (offizielle Produktdokumentation): https://www.ufz.de/droughtmonitor/
"""
        )
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("SMI JHM 2013", "https://doi.org/10.1175/JHM-D-12-075.1")
        with b2:
            st.link_button("UFZ Dürremonitor", "https://www.ufz.de/droughtmonitor/")

    with st.expander("🎯 MDI / Multivariate Dürreindizes"):
        st.markdown(
            """
**Konzept**
```text
MDI = w1*SMI + w2*R-Pctl + w3*Q-Pctl
```
**Kernquellen zur multivariaten Indexbildung**
- Hao & AghaKouchak (2013), *Adv. Water Res.* DOI: https://doi.org/10.1016/j.advwatres.2013.03.009
- Hao et al. (2017), *Journal of Hydrology*. DOI: https://doi.org/10.1016/j.jhydrol.2017.07.026
- Van Loon (2015), *WIREs Water*. DOI: https://doi.org/10.1002/wat2.1085
"""
        )
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("MSDI Original", "https://doi.org/10.1016/j.advwatres.2013.03.009")
        with b2:
            st.link_button("Drought Propagation", "https://doi.org/10.1002/wat2.1085")

    with st.expander("🌧️ SPI / 🌡️ SPEI"):
        st.markdown(
            """
**Kernquellen**
- McKee et al. (1993), SPI Originalbeschreibung (Konferenzband)
- WMO (2012), *Standardized Precipitation Index User Guide (WMO-No. 1090)*
- Vicente-Serrano et al. (2010), SPEI. DOI: https://doi.org/10.1175/2009JCLI2909.1
"""
        )
        b1, b2 = st.columns(2)
        with b1:
            st.link_button("WMO SPI Guide", "https://www.droughtmanagement.info/literature/WMO_standardized_precipitation_index_user_guide_en_2012.pdf")
        with b2:
            st.link_button("SPEI Original", "https://doi.org/10.1175/2009JCLI2909.1")

    st.divider()
    st.subheader("📁 Datenquellen")
    ds1, ds2 = st.columns(2)
    with ds1:
        st.markdown(
            """
| Variable | Quelle | Zeitraum |
|---|---|---|
| Bodenfeuchte / Recharge / Abfluss | mHM-Simulationen | 2005-2020 |
| Qobs | CAMELS-DE + lokale Gauge-Dateien | 2005-2020 |
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
- Nicht alle Literaturquellen liefern identische Schwellenwerte; Schwellen sind methodenabhängig
"""
    )

    st.divider()
    st.subheader("📖 Zitiervorschlag")
    st.code(
        "Schlaak, J. (2026). Duerremonitor Sachsen [Dashboard]. University of Leipzig. URL: http://187.124.13.209:8502/",
        language="text",
    )
    st.code(
        "Schlaak, J. (2026). A Percentile-Based Multi-Component Drought Index for Hydrological Drought Monitoring in Central Europe. (PhD Paper #1, in preparation).",
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

    st.divider()
    st.subheader("📚 Referenzen Export")
    bib_path = Path(__file__).resolve().parent / "data" / "references.bib"
    if bib_path.exists():
        st.download_button(
            "📥 Alle Referenzen als BibTeX herunterladen",
            data=bib_path.read_text(encoding="utf-8").encode("utf-8"),
            file_name="drought_monitor_references.bib",
            mime="text/plain",
        )
    else:
        st.info("references.bib nicht gefunden.")
