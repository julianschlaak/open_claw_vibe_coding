#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mHM Storage Analysis & Visualization
=====================================

Berechnet und visualisiert Wasserspeicher aus mHM-Outputs:
- Total Storage (alle Kompartimente)
- Soil Moisture Storage (L1, L2, L3, Total)
- Storage Anomalien (gegenüber Klimatologie)
- Storage Percentile (Dürre-Indikator)
- Groundwater Storage (unsat + sat)

Autor: Helferchen
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
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# KONFIGURATION
# ============================================================================

BASE_DIR = Path("/data/.openclaw/workspace/open_claw_vibe_coding")
RUN_DIR = BASE_DIR / "code/mhm/runs/chemnitz_0p0625"
OUTPUT_DIR = RUN_DIR / "output"

# Input-Dateien
FLUXES_STATES_FILE = OUTPUT_DIR / "mHM_Fluxes_States.nc"

# Output-Verzeichnis für Plots
PLOT_DIR = BASE_DIR / "analysis/plots/chemnitz2/storage"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Zeitraum
START_DATE = "1991-01-01"
END_DATE = "2020-12-31"

# Bodenschicht-Tiefen [mm]
SOIL_L1_DEPTH = 250    # 0-25 cm
SOIL_L2_DEPTH = 750    # 25-100 cm
SOIL_L3_DEPTH = 800    # 100-180 cm
SOIL_TOTAL_DEPTH = 1800  # 0-180 cm

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================


def load_mhm_states():
    """Lade mHM Fluxes & States NetCDF"""
    print(f"📦 Lade mHM States: {FLUXES_STATES_FILE}")
    
    if not FLUXES_STATES_FILE.exists():
        raise FileNotFoundError(f"States file not found: {FLUXES_STATES_FILE}")
    
    ds = xr.open_dataset(FLUXES_STATES_FILE)
    print(f"   Verfügbare Variablen: {list(ds.data_vars)}")
    
    return ds


def extract_storage_variables(ds):
    """Extrahiere alle Storage-Variablen catchment-gemittelt"""
    print("\n📊 Extrahiere Storage-Variablen...")
    
    storage = {}
    
    # Interception
    if 'interception' in ds.data_vars:
        storage['interception'] = ds['interception'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ interception: {len(storage['interception'])} Werte")
    
    # Snowpack
    if 'snowpack' in ds.data_vars:
        storage['snowpack'] = ds['snowpack'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ snowpack: {len(storage['snowpack'])} Werte")
    
    # Soil Moisture Layers
    for layer in ['L01', 'L02', 'L03']:
        var_name = f'SWC_{layer}'
        if var_name in ds.data_vars:
            storage[f'swc_{layer.lower()}'] = ds[var_name].mean(dim=['lat', 'lon']).to_series()
            print(f"   ✓ {var_name}: {len(storage[f'swc_{layer.lower()}'])} Werte")
    
    # Total Soil Moisture (SWC_LALL oder SM_Lall * soil_depth)
    if 'SWC_LALL' in ds.data_vars:
        storage['swc_lall'] = ds['SWC_LALL'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ SWC_LALL: {len(storage['swc_lall'])} Werte")
    elif 'SM_Lall' in ds.data_vars:
        # SM_Lall ist volumetrisch [mm/mm], umrechnen zu mm
        storage['swc_lall'] = ds['SM_Lall'].mean(dim=['lat', 'lon']).to_series() * SOIL_TOTAL_DEPTH
        print(f"   ✓ SM_Lall (umgerechnet zu SWC_LALL): {len(storage['swc_lall'])} Werte")
    
    # Groundwater Storage
    if 'unsatSTW' in ds.data_vars:
        storage['unsatSTW'] = ds['unsatSTW'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ unsatSTW: {len(storage['unsatSTW'])} Werte")
    
    if 'satSTW' in ds.data_vars:
        storage['satSTW'] = ds['satSTW'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ satSTW: {len(storage['satSTW'])} Werte")
    
    if 'sealedSTW' in ds.data_vars:
        storage['sealedSTW'] = ds['sealedSTW'].mean(dim=['lat', 'lon']).to_series()
        print(f"   ✓ sealedSTW: {len(storage['sealedSTW'])} Werte")
    
    # SM (volumetric) falls verfügbar
    for layer in ['L01', 'L02', 'L03', 'Lall']:
        var_name = f'SM_{layer}'
        if var_name in ds.data_vars:
            storage[f'sm_{layer.lower()}'] = ds[var_name].mean(dim=['lat', 'lon']).to_series()
            print(f"   ✓ {var_name}: {len(storage[f'sm_{layer.lower()}'])} Werte")
    
    return storage


def calculate_total_storage(storage):
    """Berechne Total Catchment Storage"""
    print("\n💧 Berechne Total Storage...")
    
    total = pd.Series(0.0, index=storage['swc_lall'].index)
    
    # Addiere alle verfügbaren Komponenten
    components = ['interception', 'snowpack', 'swc_lall', 'unsatSTW', 'satSTW', 'sealedSTW']
    
    for comp in components:
        if comp in storage:
            total += storage[comp]
            print(f"   + {comp}")
    
    storage['total'] = total
    print(f"   ✓ Total Storage: {len(total)} Werte")
    
    return storage


def calculate_storage_anomaly(storage, period='1991-01-01', end_period='2020-12-31'):
    """Berechne Storage-Anomalien gegenüber Klimatologie"""
    print("\n📈 Berechne Storage-Anomalien...")
    
    anomalies = {}
    
    for key, ts in storage.items():
        if key.startswith('sm_'):
            continue  # Volumetric nicht doppelt berechnen
        
        # Filtere Referenzperiode
        ts_ref = ts[(ts.index >= period) & (ts.index <= end_period)]
        
        # Klimatologie für jeden DOY
        ts_ref_df = pd.DataFrame({'value': ts_ref, 'doy': ts_ref.index.dayofyear})
        climatology = ts_ref_df.groupby('doy')['value'].mean()
        
        # Anomalie = Aktuell - Klimatologie
        anomaly = ts.copy()
        for i, val in anomaly.items():
            doy = i.dayofyear
            if doy in climatology.index:
                anomaly[i] = val - climatology[doy]
            else:
                anomaly[i] = np.nan
        
        anomalies[f'{key}_anomaly'] = anomaly
        print(f"   ✓ {key}_anomaly")
    
    return anomalies


def calculate_storage_percentile(storage, period='1991-01-01', end_period='2020-12-31'):
    """Berechne Storage-Percentile (Dürre-Indikator)"""
    print("\n📊 Berechne Storage-Percentile...")
    
    percentiles = {}
    
    for key, ts in storage.items():
        if key.startswith('sm_'):
            continue  # Volumetric nicht doppelt berechnen
        
        # Filtere Referenzperiode
        ts_ref = ts[(ts.index >= period) & (ts.index <= end_period)]
        
        # Percentile für jeden DOY
        percentile_ts = ts.copy()
        for i, val in percentile_ts.items():
            doy = i.dayofyear
            ts_same_doy = ts_ref[ts_ref.index.dayofyear == doy]
            
            if len(ts_same_doy) > 0:
                # Empirisches Percentil
                rank = (ts_same_doy < val).sum() + 1
                n = len(ts_same_doy)
                percentile_ts[i] = 100 * rank / (n + 1)
            else:
                percentile_ts[i] = np.nan
        
        percentiles[f'{key}_pctl'] = percentile_ts
        print(f"   ✓ {key}_pctl")
    
    return percentiles


# ============================================================================
# PLOT-FUNKTIONEN
# ============================================================================


def plot_storage_timeseries(storage):
    """Plot 1: Storage-Zeitreihen aller Kompartimente"""
    print("\n📈 Erstelle Plot 1: Storage-Zeitreihen...")
    
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    
    # Oben: Total Storage
    ax = axes[0]
    if 'total' in storage:
        ax.plot(storage['total'].index, storage['total'].values, 
                color='black', linewidth=1.5, label='Total Storage')
        ax.fill_between(storage['total'].index, storage['total'].values, 
                       alpha=0.3, color='blue')
        ax.set_ylabel('Total Storage [mm]')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_title('Chemnitz2: Total Catchment Storage (1991-2020)')
    
    # Bodenfeuchte-Schichten
    ax = axes[1]
    colors = ['green', 'orange', 'brown']
    layers = ['swc_l01', 'swc_l02', 'swc_l03']
    layer_names = ['L1 (0-25cm)', 'L2 (25-100cm)', 'L3 (100-180cm)']
    
    for i, (layer, name) in enumerate(zip(layers, layer_names)):
        if layer in storage:
            ax.plot(storage[layer].index, storage[layer].values, 
                   color=colors[i], linewidth=1, alpha=0.8, label=name)
    
    ax.set_ylabel('Soil Storage [mm]')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title('Bodenfeuchte nach Schichten')
    
    # Groundwater
    ax = axes[2]
    if 'unsatSTW' in storage:
        ax.plot(storage['unsatSTW'].index, storage['unsatSTW'].values, 
               color='cyan', linewidth=1, label='Ungesättigte Zone')
    if 'satSTW' in storage:
        ax.plot(storage['satSTW'].index, storage['satSTW'].values, 
               color='blue', linewidth=1, label='Gesättigte Zone')
    
    ax.set_ylabel('Groundwater Storage [mm]')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title('Groundwater Storage')
    
    # Interception + Snow
    ax = axes[3]
    if 'interception' in storage:
        ax.plot(storage['interception'].index, storage['interception'].values, 
               color='lightgreen', linewidth=0.8, label='Interception')
    if 'snowpack' in storage:
        ax.plot(storage['snowpack'].index, storage['snowpack'].values, 
               color='lightblue', linewidth=0.8, label='Snowpack')
    
    ax.set_ylabel('Surface Storage [mm]')
    ax.set_xlabel('Jahr')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title('Oberflächen-Speicher')
    
    # X-Achse formatieren
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    outpath = PLOT_DIR / '01_storage_timeseries.png'
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_storage_anomaly(anomalies):
    """Plot 2: Storage-Anomalien als Linienplots (Zeitreihen)"""
    print("\n📈 Erstelle Plot 2: Storage-Anomalien...")
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Total Storage Anomaly
    ax = axes[0]
    if 'total_anomaly' in anomalies:
        ax.plot(anomalies['total_anomaly'].index, 
               anomalies['total_anomaly'].values,
               color='black', linewidth=1, label='Total Storage')
        ax.fill_between(anomalies['total_anomaly'].index, 
                       anomalies['total_anomaly'].values,
                       where=(anomalies['total_anomaly'].values > 0),
                       alpha=0.4, color='red', label='Über Normal')
        ax.fill_between(anomalies['total_anomaly'].index, 
                       anomalies['total_anomaly'].values,
                       where=(anomalies['total_anomaly'].values < 0),
                       alpha=0.4, color='blue', label='Unter Normal')
        ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
        ax.set_ylabel('Anomalie [mm]')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('Total Storage Anomalie (gegenüber 1991-2020 Klimatologie)')
    
    # Soil Moisture Anomaly
    ax = axes[1]
    if 'swc_lall_anomaly' in anomalies:
        ax.plot(anomalies['swc_lall_anomaly'].index, 
               anomalies['swc_lall_anomaly'].values,
               color='green', linewidth=1, label='Soil Moisture')
        ax.fill_between(anomalies['swc_lall_anomaly'].index, 
                       anomalies['swc_lall_anomaly'].values,
                       where=(anomalies['swc_lall_anomaly'].values > 0),
                       alpha=0.3, color='red')
        ax.fill_between(anomalies['swc_lall_anomaly'].index, 
                       anomalies['swc_lall_anomaly'].values,
                       where=(anomalies['swc_lall_anomaly'].values < 0),
                       alpha=0.3, color='blue')
        ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
        ax.set_ylabel('Anomalie [mm]')
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('Soil Moisture Anomalie (0-180cm)')
    
    # Groundwater Anomaly
    ax = axes[2]
    if 'unsatSTW_anomaly' in anomalies:
        ax.plot(anomalies['unsatSTW_anomaly'].index, 
               anomalies['unsatSTW_anomaly'].values,
               color='cyan', linewidth=0.8, label='Ungesättigt')
    if 'satSTW_anomaly' in anomalies:
        ax.plot(anomalies['satSTW_anomaly'].index, 
               anomalies['satSTW_anomaly'].values,
               color='blue', linewidth=0.8, label='Gesättigt')
    
    ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
    ax.set_ylabel('Anomalie [mm]')
    ax.set_xlabel('Jahr')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_title('Groundwater Storage Anomalie')
    
    # X-Achse formatieren
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    outpath = PLOT_DIR / '02_storage_anomaly.png'
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_storage_percentile(percentiles):
    """Plot 3: Storage-Percentile (Dürre-Indikator)"""
    print("\n📈 Erstelle Plot 3: Storage-Percentile...")
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Total Storage Percentile
    ax = axes[0]
    if 'total_pctl' in percentiles:
        ax.plot(percentiles['total_pctl'].index, percentiles['total_pctl'].values,
               color='black', linewidth=0.8)
        ax.fill_between(percentiles['total_pctl'].index, 
                       percentiles['total_pctl'].values,
                       alpha=0.3, color='blue')
        
        # Dürre-Schwellenwerte
        ax.axhline(20, color='orange', linestyle='--', linewidth=1, label='Mild Drought (<20)')
        ax.axhline(10, color='red', linestyle='--', linewidth=1, label='Moderate Drought (<10)')
        ax.axhline(5, color='darkred', linestyle='--', linewidth=1, label='Severe Drought (<5)')
        ax.axhline(2, color='purple', linestyle='--', linewidth=1, label='Extreme Drought (<2)')
        
        ax.set_ylabel('Percentile [-]')
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.set_title('Total Storage Percentile (Dürre-Indikator)')
    
    # Soil Moisture Percentile
    ax = axes[1]
    if 'swc_lall_pctl' in percentiles:
        ax.plot(percentiles['swc_lall_pctl'].index, percentiles['swc_lall_pctl'].values,
               color='green', linewidth=0.8)
        ax.fill_between(percentiles['swc_lall_pctl'].index, 
                       percentiles['swc_lall_pctl'].values,
                       alpha=0.3, color='green')
        
        ax.axhline(20, color='orange', linestyle='--', linewidth=1)
        ax.axhline(10, color='red', linestyle='--', linewidth=1)
        
        ax.set_ylabel('Percentile [-]')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        ax.set_title('Soil Moisture Percentile (SMI-ähnlich)')
    
    # Groundwater Percentile
    ax = axes[2]
    if 'unsatSTW_pctl' in percentiles:
        ax.plot(percentiles['unsatSTW_pctl'].index, percentiles['unsatSTW_pctl'].values,
               color='cyan', linewidth=0.8, label='Ungesättigt')
    if 'satSTW_pctl' in percentiles:
        ax.plot(percentiles['satSTW_pctl'].index, percentiles['satSTW_pctl'].values,
               color='blue', linewidth=0.8, label='Gesättigt')
    
    ax.axhline(20, color='orange', linestyle='--', linewidth=1)
    ax.axhline(10, color='red', linestyle='--', linewidth=1)
    
    ax.set_ylabel('Percentile [-]')
    ax.set_xlabel('Jahr')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_title('Groundwater Storage Percentile')
    
    # X-Achse formatieren
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    outpath = PLOT_DIR / '03_storage_percentile.png'
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def plot_storage_boxplots(storage):
    """Plot 4: Saisonale Storage-Verteilung (Boxplots)"""
    print("\n📈 Erstelle Plot 4: Saisonale Boxplots...")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    months = range(1, 13)
    month_names = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    
    # Total Storage
    ax = axes[0, 0]
    if 'total' in storage:
        df = pd.DataFrame({'total': storage['total'], 'month': storage['total'].index.month})
        data = [df[df['month'] == m]['total'].dropna() for m in months]
        ax.boxplot(data, labels=month_names, patch_artist=True)
        ax.set_xlabel('Monat')
        ax.set_ylabel('Total Storage [mm]')
        ax.set_title('Total Storage: Saisonale Verteilung')
        ax.grid(True, alpha=0.3, axis='y')
        
        colors = plt.cm.Blues(np.linspace(0.3, 0.9, 12))
        for patch, color in zip(ax.artists, colors):
            patch.set_facecolor(color)
    
    # Soil Moisture
    ax = axes[0, 1]
    if 'swc_lall' in storage:
        df = pd.DataFrame({'swc': storage['swc_lall'], 'month': storage['swc_lall'].index.month})
        data = [df[df['month'] == m]['swc'].dropna() for m in months]
        ax.boxplot(data, labels=month_names, patch_artist=True)
        ax.set_xlabel('Monat')
        ax.set_ylabel('Soil Storage [mm]')
        ax.set_title('Soil Moisture: Saisonale Verteilung')
        ax.grid(True, alpha=0.3, axis='y')
        
        colors = plt.cm.Greens(np.linspace(0.3, 0.9, 12))
        for patch, color in zip(ax.artists, colors):
            patch.set_facecolor(color)
    
    # Groundwater
    ax = axes[1, 0]
    if 'unsatSTW' in storage:
        df = pd.DataFrame({'gw': storage['unsatSTW'], 'month': storage['unsatSTW'].index.month})
        data = [df[df['month'] == m]['gw'].dropna() for m in months]
        ax.boxplot(data, labels=month_names, patch_artist=True)
        ax.set_xlabel('Monat')
        ax.set_ylabel('Groundwater Storage [mm]')
        ax.set_title('Groundwater (ungesättigt): Saisonale Verteilung')
        ax.grid(True, alpha=0.3, axis='y')
        
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, 12))
        for patch, color in zip(ax.artists, colors):
            patch.set_facecolor(color)
    
    # Snowpack
    ax = axes[1, 1]
    if 'snowpack' in storage:
        df = pd.DataFrame({'snow': storage['snowpack'], 'month': storage['snowpack'].index.month})
        data = [df[df['month'] == m]['snow'].dropna() for m in months]
        ax.boxplot(data, labels=month_names, patch_artist=True)
        ax.set_xlabel('Monat')
        ax.set_ylabel('Snowpack [mm]')
        ax.set_title('Snowpack: Saisonale Verteilung')
        ax.grid(True, alpha=0.3, axis='y')
        
        colors = plt.cm.Greys(np.linspace(0.3, 0.9, 12))
        for patch, color in zip(ax.artists, colors):
            patch.set_facecolor(color)
    
    plt.tight_layout()
    
    outpath = PLOT_DIR / '04_storage_boxplots.png'
    plt.savefig(outpath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✓ Gespeichert: {outpath}")


def export_storage_summary(storage, anomalies, percentiles):
    """Exportiere Storage-Zusammenfassung als CSV"""
    print("\n💾 Exportiere Storage-Zusammenfassung...")
    
    # DataFrame erstellen
    df = pd.DataFrame(index=storage['swc_lall'].index)
    
    for key, ts in storage.items():
        df[f'{key}'] = ts
    
    for key, ts in anomalies.items():
        df[f'{key}'] = ts
    
    for key, ts in percentiles.items():
        df[f'{key}'] = ts
    
    # CSV exportieren
    csv_path = PLOT_DIR / 'storage_full_timeseries.csv'
    df.to_csv(csv_path)
    print(f"   ✓ Gespeichert: {csv_path}")
    
    # Statistiken
    stats_path = PLOT_DIR / 'storage_statistics.csv'
    with open(stats_path, 'w') as f:
        f.write("Variable,Mean,Std,Min,Max,Unit\n")
        for key, ts in storage.items():
            f.write(f"{key},{ts.mean():.2f},{ts.std():.2f},{ts.min():.2f},{ts.max():.2f},mm\n")
    
    print(f"   ✓ Gespeichert: {stats_path}")


# ============================================================================
# MAIN
# ============================================================================


def main():
    print("=" * 80)
    print("mHM Storage Analysis & Visualization")
    print("=" * 80)
    print(f"Start: {datetime.now().isoformat()}")
    print(f"Run-Directory: {RUN_DIR}")
    print(f"Output-Directory: {PLOT_DIR}")
    print("=" * 80)
    
    # =========================================================================
    # 1. DATEN LADEN
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 1: mHM States laden")
    print("=" * 80)
    
    ds = load_mhm_states()
    
    # =========================================================================
    # 2. STORAGE EXTRAKTIEREN
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 2: Storage-Variablen extrahieren")
    print("=" * 80)
    
    storage = extract_storage_variables(ds)
    storage = calculate_total_storage(storage)
    
    # =========================================================================
    # 3. ANOMALIEN BERECHNEN
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 3: Anomalien berechnen")
    print("=" * 80)
    
    anomalies = calculate_storage_anomaly(storage)
    
    # =========================================================================
    # 4. PERCENTILE BERECHNEN
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 4: Percentile berechnen")
    print("=" * 80)
    
    percentiles = calculate_storage_percentile(storage)
    
    # =========================================================================
    # 5. PLOTS ERSTELLEN
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 5: Plots erstellen")
    print("=" * 80)
    
    plot_storage_timeseries(storage)
    plot_storage_anomaly(anomalies)
    plot_storage_percentile(percentiles)
    plot_storage_boxplots(storage)
    
    # =========================================================================
    # 6. EXPORT
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCHRITT 6: Daten exportieren")
    print("=" * 80)
    
    export_storage_summary(storage, anomalies, percentiles)
    
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
