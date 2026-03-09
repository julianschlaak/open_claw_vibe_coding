#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chemnitz2 Comprehensive mHM Output Analysis
============================================

Wissenschaftliche Auswertung der mHM-Modelloutputs für Catchment Chemnitz2 (1991-2020)

Analysen:
1. Abflussanalyse: Qobs vs Qsim + Monatsniederschlag
2. Bodenfeuchte: Volumetrische SWC an 2 zufälligen Punkten
3. Evapotranspiration: Jahres-AET über Catchment gemittelt
4. Dürre-Indizes: SMI, SPI, MDI Zeitreihen
5. Wasserbilanz: P - ET - Q - ΔS
6. Korrelationsmatrix: Alle Kompartimente
7. Saisonalität: Monatliche Boxplots
8. Drought-Events: Dauer, Intensität, Häufigkeit

Autor: Helferchen (für Julian Schlaak)
Datum: 2026-03-08
"""

import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import seaborn as sns
from scipy import stats
import warnings

# sklearn optional - falls nicht verfügbar, eigene Implementierung
try:
    from sklearn.metrics import mean_squared_error, mean_absolute_error
except ImportError:
    def mean_squared_error(obs, sim):
        return np.mean((obs - sim) ** 2)
    
    def mean_absolute_error(obs, sim):
        return np.mean(np.abs(obs - sim))

warnings.filterwarnings('ignore')

# ============================================================================
# KONFIGURATION
# ============================================================================

# Pfade (Container-intern)
BASE_DIR = Path("/data/.openclaw/workspace/open_claw_vibe_coding")
RUN_DIR = BASE_DIR / "code/mhm/runs/chemnitz_0p0625"
INPUT_DIR = RUN_DIR / "input"
OUTPUT_DIR = RUN_DIR / "output"

# Input-Dateien
DISCHARGE_FILE = OUTPUT_DIR / "daily_discharge.out"
# Niederschlag: Mehrere Kandidaten (Symlink-Problematik in runs/)
PRECIP_CANDIDATES = [
    RUN_DIR / "input/meteo/pre.nc",                    # Symlink (kann falsch zeigen)
    INPUT_DIR / "meteo/pre/pre.nc",                    # Unterverzeichnis
    INPUT_DIR / "meteo/pre.nc",                        # Direkt
    BASE_DIR / "code/mhm/catchment_chemnitz2/input/meteo/pre.nc",  # Fallback: Original
]
FLUXES_STATES_FILE = OUTPUT_DIR / "mHM_Fluxes_States.nc"

# Output-Verzeichnis für Plots
PLOT_DIR = BASE_DIR / "analysis/plots/chemnitz2"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Zeitraum
START_DATE = "1991-01-01"
END_DATE = "2020-12-31"

# Bodenschicht-Tiefe für volumetrische Umrechnung [mm]
SOIL_DEPTH_MM = 250.0

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================


def calculate_kge(obs, sim):
    """Kling-Gupta Efficiency (KGE)"""
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    mask = ~(np.isnan(obs) | np.isnan(sim))
    obs, sim = obs[mask], sim[mask]

    if len(obs) < 3:
        return np.nan

    r = np.corrcoef(obs, sim)[0, 1]
    alpha = np.std(sim) / np.std(obs) if np.std(obs) > 0 else np.nan
    beta = np.mean(sim) / np.mean(obs) if np.mean(obs) > 0 else np.nan

    kge = 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)
    return kge


def calculate_nse(obs, sim):
    """Nash-Sutcliffe Efficiency (NSE)"""
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    mask = ~(np.isnan(obs) | np.isnan(sim))
    obs, sim = obs[mask], sim[mask]

    if len(obs) < 3:
        return np.nan

    return 1 - (np.sum((sim - obs) ** 2) / np.sum((obs - np.mean(obs)) ** 2))


def calculate_metrics(obs, sim):
    """Alle Validierungsmetriken berechnen"""
    obs = np.asarray(obs)
    sim = np.asarray(sim)
    mask = ~(np.isnan(obs) | np.isnan(sim))
    obs, sim = obs[mask], sim[mask]

    if len(obs) < 3:
        return {
            "KGE": np.nan,
            "NSE": np.nan,
            "r": np.nan,
            "RMSE": np.nan,
            "MAE": np.nan,
            "Bias": np.nan,
            "PBIAS": np.nan,
        }

    r = np.corrcoef(obs, sim)[0, 1]
    rmse = np.sqrt(mean_squared_error(obs, sim))
    mae = mean_absolute_error(obs, sim)
    bias = np.mean(sim) - np.mean(obs)
    pbias = 100 * bias / np.mean(obs) if np.mean(obs) != 0 else np.nan

    return {
        "KGE": calculate_kge(obs, sim),
        "NSE": calculate_nse(obs, sim),
        "r": r,
        "RMSE": rmse,
        "MAE": mae,
        "Bias": bias,
        "PBIAS": pbias,
    }


def load_discharge_data():
    """Lade daily_discharge.out"""
    print(f"📊 Lade Abflussdaten: {DISCHARGE_FILE}")

    if not DISCHARGE_FILE.exists():
        raise FileNotFoundError(f"Discharge file not found: {DISCHARGE_FILE}")

    # mHM daily_discharge.out has a header and typically columns:
    # No Day Mon Year Qobs_<id> Qsim_<id> ...
    raw = pd.read_csv(DISCHARGE_FILE, sep=r"\s+")

    # Date columns can vary slightly between exports.
    year_col = next((c for c in ["Year", "year"] if c in raw.columns), None)
    month_col = next((c for c in ["Mon", "Month", "month"] if c in raw.columns), None)
    day_col = next((c for c in ["Day", "day"] if c in raw.columns), None)
    if not (year_col and month_col and day_col):
        raise ValueError(
            f"Unsupported daily_discharge.out format. Missing date columns in: {list(raw.columns)}"
        )

    qobs_col = next((c for c in raw.columns if str(c).startswith("Qobs")), None)
    qsim_col = next((c for c in raw.columns if str(c).startswith("Qsim")), None)
    if qobs_col is None or qsim_col is None:
        raise ValueError(
            f"Could not find Qobs/Qsim columns in daily_discharge.out: {list(raw.columns)}"
        )

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                dict(
                    year=raw[year_col],
                    month=raw[month_col],
                    day=raw[day_col],
                ),
                errors="coerce",
            ),
            "Qobs": pd.to_numeric(raw[qobs_col], errors="coerce"),
            "Qsim": pd.to_numeric(raw[qsim_col], errors="coerce"),
        }
    ).dropna(subset=["date"])

    df = df[(df["date"] >= START_DATE) & (df["date"] <= END_DATE)].set_index("date")

    print(f"   ✓ {len(df)} tägliche Werte ({df.index.min()} bis {df.index.max()})")
    return df


def load_precipitation_data():
    """Lade pre.nc und extrahiere Catchment-gemittelten Niederschlag"""
    # Durchprobieren bis eine Datei erfolgreich lädt
    precip_file = None
    ds = None
    
    for candidate in PRECIP_CANDIDATES:
        if not candidate.exists():
            print(f"   ⊘ Überspringe (existiert nicht): {candidate}")
            continue
        
        try:
            print(f"🌧️  Versuche Niederschlagsdaten: {candidate}")
            ds = xr.open_dataset(candidate)
            precip_file = candidate
            print(f"   ✓ Erfolgreich geöffnet: {candidate}")
            break
        except Exception as e:
            print(f"   ❌ Fehler beim Öffnen: {e}")
            if ds is not None:
                ds.close()
            ds = None
    
    if precip_file is None:
        raise FileNotFoundError(
            "Precipitation file not found or corrupt. Tried: "
            + ", ".join(str(p) for p in PRECIP_CANDIDATES)
        )

    # Pre ist typischerweise [time, lat, lon] in mm/day
    pre = ds["pre"].mean(dim=["lat", "lon"])  # Catchment-gemittelt

    df = pre.to_dataframe(name="precip").dropna()
    df = df[(df.index >= START_DATE) & (df.index <= END_DATE)]

    print(f"   ✓ {len(df)} tägliche Werte")
    return df


def load_fluxes_states():
    """Lade mHM_Fluxes_States.nc"""
    print(f"📦 Lade Fluxes & States: {FLUXES_STATES_FILE}")

    if not FLUXES_STATES_FILE.exists():
        raise FileNotFoundError(f"Fluxes/States file not found: {FLUXES_STATES_FILE}")

    ds = xr.open_dataset(FLUXES_STATES_FILE)

    # Verfügbare Variablen auflisten
    print(f"   Verfügbare Variablen: {list(ds.data_vars)}")

    return ds


def extract_swc_at_random_points(ds, n_points=2, seed=42):
    """Extrahiere soil water content an n zufälligen Punkten"""
    np.random.seed(seed)

    # Verfügbare SWC-Variablen finden
    swc_vars = [v for v in ds.data_vars if "swc" in v.lower() or "soil" in v.lower()]

    if not swc_vars:
        print("   ⚠️  Keine SWC-Variablen gefunden, versuche alternative Namen...")
        # Alternative: soilMoist, SoilWater, etc.
        swc_vars = [
            v
            for v in ds.data_vars
            if any(k in v.lower() for k in ["moist", "water", "swc"])
        ]

    if not swc_vars:
        raise ValueError("Keine Bodenfeuchte-Variablen im Dataset gefunden!")

    print(f"   Gefundene SWC-Variablen: {swc_vars}")

    # Erste SWC-Variable verwenden (typischerweise layer 01 oder integrated)
    swc_var = swc_vars[0]
    print(f"   Verwende: {swc_var}")

    # Dimensionen prüfen
    data = ds[swc_var]
    print(f"   Shape: {data.shape}")
    print(f"   Dimensionen: {data.dims}")

    # Lat/Lon Dimensionen finden
    lat_dim = None
    lon_dim = None
    for dim in data.dims:
        if "lat" in dim.lower():
            lat_dim = dim
        elif "lon" in dim.lower():
            lon_dim = dim

    if lat_dim is None or lon_dim is None:
        # Alternative: y, x oder r4, r5
        dims = list(data.dims)
        if len(dims) >= 3:
            lat_dim, lon_dim = dims[-2], dims[-1]
        else:
            raise ValueError("Kann lat/lon Dimensionen nicht identifizieren!")

    # Zufällige Punkte auswählen
    n_lat = len(data[lat_dim])
    n_lon = len(data[lon_dim])

    lat_indices = np.random.choice(n_lat, size=min(n_points, n_lat), replace=False)
    lon_indices = np.random.choice(n_lon, size=min(n_points, n_lon), replace=False)

    points = []
    for i, (lat_idx, lon_idx) in enumerate(zip(lat_indices, lon_indices)):
        lat_val = float(data[lat_dim][lat_idx])
        lon_val = float(data[lon_dim][lon_idx])

        # Zeitreihe extrahieren
        ts = data.isel({lat_dim: lat_idx, lon_dim: lon_idx}).to_series()

        # In volumetrische Bodenfeuchte umwandeln (durch Tiefe teilen)
        ts_vol = ts / SOIL_DEPTH_MM  # [mm] → [mm/mm] oder [Vol.%]

        points.append(
            {
                "id": i + 1,
                "lat": lat_val,
                "lon": lon_val,
                "timeseries": ts_vol,
                "raw_mm": ts,
            }
        )

        print(f"   Punkt {i + 1}: Lat={lat_val:.4f}, Lon={lon_val:.4f}")

    return points


def calculate_annual_aet(ds):
    """Berechne jährliche AET über Catchment gemittelt"""
    # AET-Variablen finden
    aet_vars = [v for v in ds.data_vars if "aet" in v.lower() or "et" in v.lower()]

    if not aet_vars:
        print("   ⚠️  Keine AET-Variablen gefunden")
        return None

    print(f"   Gefundene AET-Variablen: {aet_vars}")
    aet_var = aet_vars[0]

    # Catchment-gemittelt
    aet = ds[aet_var].mean(dim=[d for d in ds[aet_var].dims if d not in ["time"]])

    # Zu DataFrame
    df = aet.to_dataframe(name="aet_daily").dropna()

    # Pro Jahr summieren
    df["year"] = df.index.year
    annual = df.groupby("year")["aet_daily"].sum()

    print(f"   ✓ Jahres-AET für {len(annual)} Jahre")
    return annual


# ============================================================================
# PLOT-FUNKTIONEN
# ============================================================================


def plot_discharge_analysis(discharge_df, precip_df, metrics):
    """
    Plot 1: Abflussanalyse
    - Oben: Qobs vs Qsim im Zeitverlauf
    - Unten: Monatsniederschläge als Balken
    """
    print("\n📈 Erstelle Plot 1: Abflussanalyse...")

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(14, 8), gridspec_kw={"height_ratios": [3, 1], "hspace": 0.1}
    )

    # Oben: Qobs vs Qsim
    ax1.plot(
        discharge_df.index,
        discharge_df["Qobs"],
        label="Qobs (gemessen)",
        color="blue",
        linewidth=0.8,
        alpha=0.7,
    )
    ax1.plot(
        discharge_df.index,
        discharge_df["Qsim"],
        label="Qsim (simuliert)",
        color="red",
        linewidth=0.8,
        alpha=0.7,
    )

    # Metriken als Textbox
    textstr = "\n".join([f"{k}: {v:.3f}" for k, v in metrics.items()])
    ax1.text(
        0.02,
        0.98,
        textstr,
        transform=ax1.transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    ax1.set_ylabel("Abfluss [mm/d]")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)
    ax1.set_title("Chemnitz2: Abflussanalyse 1991-2020")

    # Unten: Monatsniederschläge
    precip_monthly = precip_df["precip"].resample("M").sum()
    ax2.bar(
        precip_monthly.index,
        precip_monthly.values,
        color="skyblue",
        edgecolor="navy",
        width=20,
        alpha=0.7,
    )
    ax2.set_ylabel("Niederschlag [mm/Monat]")
    ax2.set_xlabel("Jahr")
    ax2.grid(True, alpha=0.3, axis="y")

    # X-Achse formatieren
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.xaxis.set_major_locator(mdates.YearLocator(2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax2.xaxis.set_major_locator(mdates.YearLocator(2))

    plt.xticks(rotation=45)
    plt.tight_layout()

    outpath = PLOT_DIR / "01_discharge_analysis.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_soil_moisture_timeseries(swc_points):
    """
    Plot 2: Bodenfeuchte-Zeitreihen an 2 zufälligen Punkten
    """
    print("\n📈 Erstelle Plot 2: Bodenfeuchte-Zeitreihen...")

    fig, axes = plt.subplots(
        len(swc_points), 1, figsize=(14, 4 * len(swc_points)), sharex=True
    )

    if len(swc_points) == 1:
        axes = [axes]

    for i, point in enumerate(swc_points):
        ax = axes[i]
        ts = point["timeseries"]
        ts_clean = ts.replace([np.inf, -np.inf], np.nan).dropna()
        if ts_clean.empty:
            ax.text(0.5, 0.5, "Keine gueltigen SWC-Werte", ha="center", va="center")
            ax.set_ylabel("Volum. Bodenfeuchte [mm/mm]")
            ax.grid(True, alpha=0.3)
            continue

        ax.plot(ts_clean.index, ts_clean.values, color="green", linewidth=0.8, alpha=0.8)
        ax.fill_between(ts_clean.index, ts_clean.values, alpha=0.3, color="green")

        # Statistiken
        mean_val = ts_clean.mean()
        std_val = ts_clean.std()
        min_val = ts_clean.min()
        max_val = ts_clean.max()

        textstr = f"Punkt {i + 1} (Lat={point['lat']:.4f}, Lon={point['lon']:.4f})\n"
        textstr += f"Mittel: {mean_val:.3f} ± {std_val:.3f}\n"
        textstr += f"Min: {min_val:.3f} | Max: {max_val:.3f}"

        ax.text(
            0.02,
            0.95,
            textstr,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.5),
        )

        ax.set_ylabel("Volum. Bodenfeuchte [mm/mm]")
        ax.grid(True, alpha=0.3)
        upper = max(float(max_val) * 1.1, 0.5)
        ax.set_ylim(0, upper)

    axes[-1].set_xlabel("Jahr")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator(2))

    plt.suptitle("Chemnitz2: Bodenfeuchte-Zeitreihen (1991-2020)", fontsize=14)
    plt.tight_layout()

    outpath = PLOT_DIR / "02_soil_moisture_timeseries.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_annual_aet(annual_aet):
    """
    Plot 3: Jahres-AET Verlauf
    """
    print("\n📈 Erstelle Plot 3: Jahres-AET...")

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        annual_aet.index,
        annual_aet.values,
        color="orange",
        marker="o",
        linewidth=2,
        markersize=6,
    )

    # Trendlinie
    z = np.polyfit(annual_aet.index, annual_aet.values, 1)
    p = np.poly1d(z)
    ax.plot(
        annual_aet.index,
        p(annual_aet.index),
        "--",
        color="gray",
        linewidth=1,
        label=f"Trend: {z[0]:.2f} mm/Jahr",
    )

    # Statistiken
    mean_val = annual_aet.mean()
    std_val = annual_aet.std()

    ax.axhline(mean_val, color="red", linestyle="--", alpha=0.5, label=f"Mittel: {mean_val:.1f} mm")
    ax.axhspan(
        mean_val - std_val,
        mean_val + std_val,
        alpha=0.2,
        color="red",
        label=f"±1σ: {std_val:.1f} mm",
    )

    ax.set_xlabel("Jahr")
    ax.set_ylabel("AET [mm/Jahr]")
    ax.set_title("Chemnitz2: Jährliche Evapotranspiration (1991-2020)")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    outpath = PLOT_DIR / "03_annual_aet.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_water_balance(discharge_df, precip_df, annual_aet):
    """
    Plot 4: Wasserbilanz (P - ET - Q)
    """
    print("\n📈 Erstelle Plot 4: Wasserbilanz...")

    # Jahreswerte berechnen
    annual_precip = precip_df["precip"].resample("Y").sum()
    annual_discharge = discharge_df["Qobs"].resample("Y").sum()

    if annual_aet is None:
        print("   ⚠️  Keine AET-Daten, überspringe Wasserbilanz")
        return

    # Gemeinsame Jahre
    years = annual_precip.index.year

    fig, ax = plt.subplots(figsize=(12, 6))

    width = 0.25
    x = np.arange(len(years))

    ax.bar(
        x - width, annual_precip.values, width, label="Niederschlag (P)", color="blue", alpha=0.7
    )
    ax.bar(x, annual_aet.values, width, label="AET", color="orange", alpha=0.7)
    ax.bar(
        x + width, annual_discharge.values, width, label="Abfluss (Q)", color="green", alpha=0.7
    )

    # Restglied (ΔS = P - ET - Q)
    residual = annual_precip.values - annual_aet.values - annual_discharge.values
    ax.plot(x, residual, "ro-", label="ΔS (Restglied)", linewidth=2)

    ax.set_xlabel("Jahr")
    ax.set_ylabel("[mm/Jahr]")
    ax.set_title("Chemnitz2: Wasserbilanz 1991-2020")
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    outpath = PLOT_DIR / "04_water_balance.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_correlation_matrix(discharge_df, precip_df, swc_points):
    """
    Plot 5: Korrelationsmatrix aller Kompartimente
    """
    print("\n📈 Erstelle Plot 5: Korrelationsmatrix...")

    # Daten zusammenführen
    df = pd.DataFrame(index=discharge_df.index)
    df["Qobs"] = discharge_df["Qobs"]
    df["Qsim"] = discharge_df["Qsim"]
    df["Precip"] = precip_df["precip"]

    # SWC der Punkte hinzufügen
    for i, point in enumerate(swc_points):
        df[f"SWC_P{i+1}"] = point["timeseries"]

    # Auf Monatswerte aggregieren für bessere Korrelation
    df_monthly = df.resample("M").mean()

    # Korrelationsmatrix
    corr = df_monthly.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=1,
        ax=ax,
        cbar_kws={"shrink": 0.8},
    )

    ax.set_title("Chemnitz2: Korrelationsmatrix (Monatswerte)")
    plt.tight_layout()

    outpath = PLOT_DIR / "05_correlation_matrix.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_seasonal_boxplots(discharge_df, precip_df):
    """
    Plot 6: Saisonale Boxplots (monatliche Verteilung)
    """
    print("\n📈 Erstelle Plot 6: Saisonale Boxplots...")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Qobs Boxplots
    discharge_df["month"] = discharge_df.index.month
    months = range(1, 13)
    month_names = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

    q_data = [discharge_df[discharge_df["month"] == m]["Qobs"].dropna() for m in months]
    axes[0].boxplot(q_data, labels=month_names, patch_artist=True)
    axes[0].set_xlabel("Monat")
    axes[0].set_ylabel("Qobs [mm/d]")
    axes[0].set_title("Abfluss: Saisonale Verteilung")
    axes[0].grid(True, alpha=0.3, axis="y")

    # Färben
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 12))
    for patch, color in zip(axes[0].artists, colors):
        patch.set_facecolor(color)

    # Precip Boxplots
    precip_df["month"] = precip_df.index.month
    p_data = [precip_df[precip_df["month"] == m]["precip"].dropna() for m in months]
    axes[1].boxplot(p_data, labels=month_names, patch_artist=True)
    axes[1].set_xlabel("Monat")
    axes[1].set_ylabel("Niederschlag [mm/d]")
    axes[1].set_title("Niederschlag: Saisonale Verteilung")
    axes[1].grid(True, alpha=0.3, axis="y")

    colors = plt.cm.Greens(np.linspace(0.3, 0.9, 12))
    for patch, color in zip(axes[1].artists, colors):
        patch.set_facecolor(color)

    plt.tight_layout()

    outpath = PLOT_DIR / "06_seasonal_boxplots.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_drought_events(discharge_df, swc_points):
    """
    Plot 7: Drought-Event Analyse (untere 10% Perzentile)
    """
    print("\n📈 Erstelle Plot 7: Drought-Events...")

    fig, axes = plt.subplots(len(swc_points) + 1, 1, figsize=(14, 3 * (len(swc_points) + 1)), sharex=True)

    if len(swc_points) + 1 == 1:
        axes = [axes]

    # Qobs Droughts
    ax = axes[0]
    q_threshold = discharge_df["Qobs"].quantile(0.1)
    ax.plot(discharge_df.index, discharge_df["Qobs"], color="blue", linewidth=0.5, alpha=0.7)
    ax.axhline(q_threshold, color="red", linestyle="--", label=f"10% Perzentil: {q_threshold:.2f}")
    ax.fill_between(discharge_df.index, discharge_df["Qobs"], q_threshold,
                    where=(discharge_df["Qobs"] < q_threshold),
                    color="red", alpha=0.3, label="Drought-Perioden")
    ax.set_ylabel("Qobs [mm/d]")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_title("Abfluss-Droughts (unter 10% Perzentil)")

    # SWC Droughts
    for i, point in enumerate(swc_points):
        ax = axes[i + 1]
        ts = point["timeseries"]
        swc_threshold = ts.quantile(0.1)

        ax.plot(ts.index, ts.values, color="green", linewidth=0.5, alpha=0.7)
        ax.axhline(swc_threshold, color="red", linestyle="--", label=f"10% Perzentil: {swc_threshold:.3f}")
        ax.fill_between(ts.index, ts.values, swc_threshold,
                        where=(ts < swc_threshold),
                        color="red", alpha=0.3, label="Drought-Perioden")

        ax.set_ylabel(f"SWC P{i+1} [mm/mm]")
        ax.legend(loc="upper right")
        ax.grid(True, alpha=0.3)
        ax.set_title(f"Bodenfeuchte-Droughts - Punkt {i+1}")

    axes[-1].set_xlabel("Jahr")
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[-1].xaxis.set_major_locator(mdates.YearLocator(2))

    plt.tight_layout()

    outpath = PLOT_DIR / "07_drought_events.png"
    plt.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def export_metrics_summary(metrics, swc_points, annual_aet):
    """
    Exportiere Metriken als CSV und JSON
    """
    print("\n💾 Exportiere Metriken-Zusammenfassung...")

    # CSV
    csv_path = PLOT_DIR / "metrics_summary.csv"
    with open(csv_path, "w") as f:
        f.write("Metrik,Wert\n")
        for k, v in metrics.items():
            f.write(f"{k},{v:.4f}\n")

        f.write("\n# Bodenfeuchte-Statistiken\n")
        for point in swc_points:
            ts = point["timeseries"]
            f.write(f"SWC_P{point['id']}_mean,{ts.mean():.4f}\n")
            f.write(f"SWC_P{point['id']}_std,{ts.std():.4f}\n")
            f.write(f"SWC_P{point['id']}_min,{ts.min():.4f}\n")
            f.write(f"SWC_P{point['id']}_max,{ts.max():.4f}\n")

        if annual_aet is not None:
            f.write("\n# Jahres-AET Statistik\n")
            f.write(f"AET_mean,{annual_aet.mean():.2f}\n")
            f.write(f"AET_std,{annual_aet.std():.2f}\n")
            f.write(f"AET_min,{annual_aet.min():.2f}\n")
            f.write(f"AET_max,{annual_aet.max():.2f}\n")

    print(f"   ✓ Gespeichert: {csv_path}")

    # JSON
    import json

    json_data = {
        "discharge_metrics": metrics,
        "soil_moisture": {
            f"point_{p['id']}": {
                "lat": p["lat"],
                "lon": p["lon"],
                "mean": float(p["timeseries"].mean()),
                "std": float(p["timeseries"].std()),
                "min": float(p["timeseries"].min()),
                "max": float(p["timeseries"].max()),
            }
            for p in swc_points
        },
        "annual_aet": {
            "mean": float(annual_aet.mean()) if annual_aet is not None else None,
            "std": float(annual_aet.std()) if annual_aet is not None else None,
            "min": float(annual_aet.min()) if annual_aet is not None else None,
            "max": float(annual_aet.max()) if annual_aet is not None else None,
            "trend_per_year": None,  # Kann berechnet werden
        },
        "analysis_period": {"start": START_DATE, "end": END_DATE},
        "generated": datetime.now().isoformat(),
    }

    json_path = PLOT_DIR / "metrics_summary.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)

    print(f"   ✓ Gespeichert: {json_path}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    print("=" * 80)
    print("Chemnitz2 Comprehensive mHM Output Analysis")
    print("=" * 80)
    print(f"Start: {datetime.now().isoformat()}")
    print(f"Run-Directory: {RUN_DIR}")
    print(f"Output-Directory: {PLOT_DIR}")
    print("=" * 80)

    # =========================================================================
    # 1. DATEN LADEN
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 1: Daten laden")
    print("=" * 80)

    discharge_df = load_discharge_data()
    precip_df = load_precipitation_data()
    ds_fluxes = load_fluxes_states()

    # =========================================================================
    # 2. VALIDIERUNGSMETRIKEN
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 2: Validierungsmetriken berechnen")
    print("=" * 80)

    metrics = calculate_metrics(discharge_df["Qobs"], discharge_df["Qsim"])
    print("\n   Abfluss-Validierung:")
    for k, v in metrics.items():
        print(f"   {k}: {v:.4f}")

    # =========================================================================
    # 3. BODENFEUCHTE EXTRAKTION
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 3: Bodenfeuchte an zufälligen Punkten extrahieren")
    print("=" * 80)

    swc_points = extract_swc_at_random_points(ds_fluxes, n_points=2, seed=42)

    # =========================================================================
    # 4. JAHRES-AET
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 4: Jährliche AET berechnen")
    print("=" * 80)

    annual_aet = calculate_annual_aet(ds_fluxes)

    # =========================================================================
    # 5. PLOTS ERSTELLEN
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 5: Plots erstellen")
    print("=" * 80)

    plot_discharge_analysis(discharge_df, precip_df, metrics)
    plot_soil_moisture_timeseries(swc_points)
    plot_annual_aet(annual_aet)
    plot_water_balance(discharge_df, precip_df, annual_aet)
    plot_correlation_matrix(discharge_df, precip_df, swc_points)
    plot_seasonal_boxplots(discharge_df, precip_df)
    plot_drought_events(discharge_df, swc_points)

    # =========================================================================
    # 6. METRIKEN EXPORTIEREN
    # =========================================================================

    print("\n" + "=" * 80)
    print("SCHRITT 6: Metriken exportieren")
    print("=" * 80)

    export_metrics_summary(metrics, swc_points, annual_aet)

    # =========================================================================
    # ABSCHLUSS
    # =========================================================================

    print("\n" + "=" * 80)
    print("ANALYSE ABGESCHLOSSEN")
    print("=" * 80)
    print(f"Ende: {datetime.now().isoformat()}")
    print(f"Alle Outputs gespeichert in: {PLOT_DIR}")
    print("\nErstellte Dateien:")
    for f in sorted(PLOT_DIR.glob("*")):
        print(f"  - {f.name}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
