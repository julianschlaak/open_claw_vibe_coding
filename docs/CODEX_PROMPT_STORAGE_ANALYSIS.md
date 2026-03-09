# Codex Prompt: mHM Storage Analysis (Portable)

## 📋 Task Overview

Create a complete water storage analysis from hydrological model outputs. The analysis computes total catchment storage, anomalies (vs. climatology), percentiles (drought indicator), and seasonal patterns.

**Deliverables:**
1. Python script (`storage_analysis.py`)
2. 4 publication-ready plots (PNG, 300 dpi)
3. 2 CSV data exports
4. Quality control report

---

## 🎯 Required Input Data

### Mandatory Files

| File | Format | Description | Example Path |
|------|--------|-------------|--------------|
| **Fluxes & States** | NetCDF (.nc) | Daily model outputs with storage variables | `[RUN_DIR]/output/mHM_Fluxes_States.nc` |
| **Model Configuration** | Text/JSON | Soil layer depths, catchment info | `[RUN_DIR]/config.txt` |

### Required NetCDF Variables

The script should check for these variables (gracefully skip if missing):

| Variable | Standard Name | Unit | Description | Required |
|----------|---------------|------|-------------|----------|
| `interception` | canopy_storage | mm | Canopy water storage | No |
| `snowpack` | snow_water_equivalent | mm | Snow water equivalent | No |
| `SWC_L01` | soil_moisture_layer1 | mm | Soil moisture layer 1 | **Yes** |
| `SWC_L02` | soil_moisture_layer2 | mm | Soil moisture layer 2 | **Yes** |
| `SWC_L03` | soil_moisture_layer3 | mm | Soil moisture layer 3 | **Yes** |
| `SWC_LALL` | total_soil_moisture | mm | Total soil moisture (0-180cm) | **Yes** |
| `unsatSTW` | unsaturated_zone_storage | mm | Unsaturated groundwater | No |
| `satSTW` | saturated_zone_storage | mm | Saturated groundwater | No |
| `sealedSTW` | sealed_area_storage | mm | Sealed area storage | No |

**Alternative variables** (if above not available):
- `SM_L01/L02/L03/Lall` — Volumetric soil moisture [mm/mm], convert using soil depth
- `SoilMoisture_*` — Alternative naming conventions

### Required Metadata

Provide these values (edit placeholders below):

```yaml
# Time period
START_DATE: "YYYY-MM-DD"     # e.g., "1991-01-01"
END_DATE: "YYYY-MM-DD"       # e.g., "2020-12-31"

# Soil layer depths [mm] — MUST match your model setup
SOIL_L1_DEPTH: 250           # Layer 1: 0-25 cm
SOIL_L2_DEPTH: 750           # Layer 2: 25-100 cm
SOIL_L3_DEPTH: 800           # Layer 3: 100-180 cm
SOIL_TOTAL_DEPTH: 1800       # Total: 0-180 cm

# Catchment info
CATCHMENT_NAME: "[NAME]"     # e.g., "Chemnitz2", "Elbe", "Rhine"
CATCHMENT_ID: "[ID]"         # Optional identifier
```

---

## 📁 Directory Structure (Target)

Create this structure in your workspace:

```
[YOUR_WORKSPACE]/
├── analysis/
│   ├── scripts/
│   │   └── storage_analysis.py          # Main script (create this)
│   └── plots/
│       └── [CATCHMENT_NAME]/
│           └── storage/                  # Output directory (create)
│               ├── 01_storage_timeseries.png
│               ├── 02_storage_anomaly.png
│               ├── 03_storage_percentile.png
│               ├── 04_storage_boxplots.png
│               ├── storage_full_timeseries.csv
│               └── storage_statistics.csv
└── data/
    └── [CATCHMENT_NAME]/
        └── output/
            └── mHM_Fluxes_States.nc      # Input file (must exist)
```

---

## 🛠️ Implementation Requirements

### Step 1: Create Python Script

Create `analysis/scripts/storage_analysis.py` with:

**Dependencies:**
```python
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
```

**Configuration Section (EDIT THESE):**
```python
# ============================================================================
# USER CONFIGURATION — EDIT THESE PATHS
# ============================================================================

BASE_DIR = Path("[YOUR_WORKSPACE_PATH]")      # e.g., "/home/user/project"
RUN_DIR = BASE_DIR / "data/[CATCHMENT_NAME]"  # e.g., "data/Chemnitz2"
OUTPUT_DIR = RUN_DIR / "output"

# Input file
FLUXES_STATES_FILE = OUTPUT_DIR / "mHM_Fluxes_States.nc"

# Output directory for plots
PLOT_DIR = BASE_DIR / "analysis/plots/[CATCHMENT_NAME]/storage"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Analysis period
START_DATE = "YYYY-MM-DD"    # e.g., "1991-01-01"
END_DATE = "2020-12-31"

# Soil layer depths [mm] — MUST match your model configuration
SOIL_L1_DEPTH = 250          # 0-25 cm
SOIL_L2_DEPTH = 750          # 25-100 cm
SOIL_L3_DEPTH = 800          # 100-180 cm
SOIL_TOTAL_DEPTH = 1800      # 0-180 cm

# ============================================================================
```

### Step 2: Implement Core Functions

**Function 1: Load Data**
```python
def load_model_states():
    """Load NetCDF file and validate variables"""
    # - Check file exists
    # - Open with xarray
    # - List available variables
    # - Validate time dimension
    # - Return dataset
```

**Function 2: Extract Storage Variables**
```python
def extract_storage_variables(ds):
    """Extract all storage variables, catchment-averaged"""
    # - Loop through expected variables
    # - Spatial mean (lat/lon) if gridded
    # - Convert to pandas Series
    # - Handle alternative variable names
    # - Return dict of time series
```

**Function 3: Calculate Total Storage**
```python
def calculate_total_storage(storage):
    """Sum all available storage compartments"""
    # - Initialize with zeros
    # - Add each available component
    # - Store as 'total' key
    # - Return updated dict
```

**Function 4: Calculate Anomalies (DOY-based)**
```python
def calculate_storage_anomaly(storage, ref_start, ref_end):
    """Compute anomalies vs. day-of-year climatology"""
    # - Filter reference period
    # - Group by day-of-year (1-366)
    # - Compute mean for each DOY
    # - Subtract climatology from full series
    # - Return dict of anomaly series
```

**Function 5: Calculate Percentiles (Empirical)**
```python
def calculate_storage_percentile(storage, ref_start, ref_end):
    """Compute empirical percentiles for drought monitoring"""
    # - Filter reference period
    # - For each value, compute rank among same-DOY values
    # - percentile = 100 * rank / (n + 1)
    # - Return dict of percentile series
```

### Step 3: Create Visualization Functions

**Plot 1: Storage Timeseries**
```python
def plot_storage_timeseries(storage):
    """4-panel plot: Total, Soil Layers, Groundwater, Surface"""
    # - Figure: 4 rows, 1 column, shared x-axis
    # - Panel 1: Total storage (line + fill)
    # - Panel 2: Soil layers L1/L2/L3 (colored lines)
    # - Panel 3: Groundwater (unsat + sat)
    # - Panel 4: Surface (interception + snow)
    # - X-axis: Years (formatted)
    # - Y-axis: Storage [mm]
    # - Save: 01_storage_timeseries.png (300 dpi)
```

**Plot 2: Storage Anomalies**
```python
def plot_storage_anomaly(anomalies):
    """3-panel plot: Anomalies with filled areas"""
    # - Figure: 3 rows, 1 column, shared x-axis
    # - Panel 1: Total storage anomaly
    # - Panel 2: Soil moisture anomaly
    # - Panel 3: Groundwater anomaly
    # - Style: Line plot with fill (red=positive, blue=negative)
    # - Zero line: Black solid
    # - Save: 02_storage_anomaly.png (300 dpi)
```

**Plot 3: Storage Percentiles**
```python
def plot_storage_percentile(percentiles):
    """3-panel plot: Percentiles with drought thresholds"""
    # - Figure: 3 rows, 1 column, shared x-axis
    # - Panel 1: Total storage percentile
    # - Panel 2: Soil moisture percentile
    # - Panel 3: Groundwater percentile
    # - Threshold lines: 20, 10, 5, 2 percentile (dashed)
    # - Y-axis: 0-100
    # - Save: 03_storage_percentile.png (300 dpi)
```

**Plot 4: Seasonal Boxplots**
```python
def plot_storage_boxplots(storage):
    """4-panel boxplot: Monthly distributions"""
    # - Figure: 2x2 grid
    # - Panel 1: Total storage by month
    # - Panel 2: Soil moisture by month
    # - Panel 3: Groundwater by month
    # - Panel 4: Snowpack by month
    # - X-axis: Month names (Jan-Dec)
    # - Color gradient: Jan→Dec
    # - Save: 04_storage_boxplots.png (300 dpi)
```

### Step 4: Data Export

```python
def export_storage_summary(storage, anomalies, percentiles):
    """Export time series and statistics to CSV"""
    # - Combine all series into DataFrame
    # - Export full time series: storage_full_timeseries.csv
    # - Compute statistics (mean, std, min, max)
    # - Export statistics: storage_statistics.csv
```

### Step 5: Main Execution

```python
def main():
    # 1. Load data
    # 2. Extract storage variables
    # 3. Calculate total storage
    # 4. Calculate anomalies
    # 5. Calculate percentiles
    # 6. Create all 4 plots
    # 7. Export data
    # 8. Print summary
```

---

## ✅ Quality Control Checklist

### Before Running

- [ ] Input NetCDF file exists at configured path
- [ ] File size > 1 MB (not empty/corrupted)
- [ ] Time period covers ≥10 years (for robust climatology)
- [ ] Soil layer depths match model configuration
- [ ] Output directory is writable
- [ ] Python environment has required packages

### After Running

- [ ] All 4 PNG files created
- [ ] Each PNG > 100 KB (not empty)
- [ ] CSV files have correct row count (matches time period)
- [ ] No NaN values in plots (check for data gaps)
- [ ] Anomaly mean ≈ 0 (climatology centered)
- [ ] Percentile range 0-100 (no clumping at edges)

### Validation Tests

```bash
# Check file sizes
ls -lh analysis/plots/[CATCHMENT]/storage/

# Verify CSV row count
wc -l analysis/plots/[CATCHMENT]/storage/storage_full_timeseries.csv
# Expected: ~360 rows for 1991-2020 (30 years × 12 months)

# Quick plot inspection (if display available)
eog analysis/plots/[CATCHMENT]/storage/01_storage_timeseries.png &
```

---

## 📊 Expected Output Summary

### File Sizes (Reference: Chemnitz2, 30 years)

| File | Expected Size | Notes |
|------|---------------|-------|
| `01_storage_timeseries.png` | 800 KB - 1.5 MB | Depends on data density |
| `02_storage_anomaly.png` | 800 KB - 1.2 MB | Filled areas increase size |
| `03_storage_percentile.png` | 1.0 MB - 1.8 MB | Threshold lines add detail |
| `04_storage_boxplots.png` | 300 KB - 600 KB | Simpler visualization |
| `storage_full_timeseries.csv` | 150 KB - 400 KB | Depends on variable count |
| `storage_statistics.csv` | 400-600 B | Small summary file |

### Console Output (Example)

```
================================================================================
mHM Storage Analysis & Visualization
================================================================================
Start: 2026-03-09T09:28:00
Run-Directory: /data/Chemnitz2
Output-Directory: /data/analysis/plots/Chemnitz2/storage
================================================================================

SCHRITT 1: mHM States laden
📦 Lade mHM States: /data/Chemnitz2/output/mHM_Fluxes_States.nc
   Verfügbare Variablen: ['interception', 'snowpack', 'SWC_L01', ...]

SCHRITT 2: Storage-Variablen extrahieren
   ✓ interception: 360 Werte
   ✓ snowpack: 360 Werte
   ✓ swc_l01: 360 Werte
   ✓ swc_lall: 360 Werte
   ✓ unsatSTW: 360 Werte
   ✓ satSTW: 360 Werte

SCHRITT 3: Anomalien berechnen
   ✓ total_anomaly
   ✓ swc_lall_anomaly
   ✓ ...

SCHRITT 4: Percentile berechnen
   ✓ total_pctl
   ✓ swc_lall_pctl
   ✓ ...

SCHRITT 5: Plots erstellen
   ✓ 01_storage_timeseries.png
   ✓ 02_storage_anomaly.png
   ✓ 03_storage_percentile.png
   ✓ 04_storage_boxplots.png

SCHRITT 6: Daten exportieren
   ✓ storage_full_timeseries.csv
   ✓ storage_statistics.csv

ANALYSE ABGESCHLOSSEN
Alle Outputs gespeichert in: /data/analysis/plots/Chemnitz2/storage
```

---

## 🚨 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Wrong input path | Verify `FLUXES_STATES_FILE` exists |
| `KeyError: 'SWC_LALL'` | Variable not in NetCDF | Check alternative names (SM_Lall) |
| `matplotlib.cm has no attribute` | Colormap typo | Use standard: Blues, Greens, RdBu |
| Flat lines in plots | Data not loaded | Check console for "✓" messages |
| Anomaly not centered | Short reference period | Use ≥10 years |
| Percentile clumping | Too few years | Increase reference period |

---

## 📝 User Instructions

### Step-by-Step

1. **Copy this prompt** to your Codex session

2. **Edit configuration placeholders:**
   - `[YOUR_WORKSPACE_PATH]` → Your actual path
   - `[CATCHMENT_NAME]` → Your catchment name
   - `START_DATE` / `END_DATE` → Your time period
   - `SOIL_L*_DEPTH` → Your model's soil depths

3. **Verify input data:**
   ```bash
   ls -lh [YOUR_WORKSPACE]/data/[CATCHMENT]/output/mHM_Fluxes_States.nc
   ncdump -h [file] | head -50  # Check variables
   ```

4. **Run Codex** with this prompt

5. **Review generated script** before execution

6. **Execute script:**
   ```bash
   python analysis/scripts/storage_analysis.py
   ```

7. **Check outputs:**
   ```bash
   ls -lh analysis/plots/[CATCHMENT]/storage/
   ```

---

## 🔬 Scientific Notes

### Why DOY-based Climatology?

Storage variables have strong seasonality. Using a simple mean would:
- Show positive anomalies in winter (high storage season)
- Show negative anomalies in summer (low storage season)
- Mask real drought/flood signals

**DOY-based approach:**
- Compare each day to same day-of-year across all years
- Removes seasonal cycle
- Isolates interannual variability

### Why Empirical Percentiles?

- **Non-parametric:** No distributional assumptions
- **Robust:** Works with skewed data
- **Interpretable:** Direct drought thresholds (e.g., <20 = drought)
- **Standard:** Used in USDM, EDO, other drought monitors

### Drought Thresholds

| Percentile | Class | Interpretation |
|------------|-------|----------------|
| < 2 | Extreme | 1-in-50 year event |
| < 5 | Severe | 1-in-20 year event |
| < 10 | Moderate | 1-in-10 year event |
| < 20 | Mild | 1-in-5 year event |
| 20-80 | Normal | Typical conditions |
| > 80 | Wet | Above normal |

---

## 📚 References

1. **Keyantash, J., & Dracup, J. A. (2002).** The Quantification of Drought: An Evaluation of Drought Indices. Bulletin of the American Meteorological Society.

2. **Samaniego, L., et al. (2010).** Multiscale high-resolution spatial modeling of hydrological processes. Advances in Water Resources.

3. **U.S. Drought Monitor:** https://droughtmonitor.unl.edu/

4. **European Drought Observatory:** https://edo.jrc.ec.europa.eu/

---

## 🎯 Success Criteria

Analysis is complete when:

- ✅ All 4 plots generated without errors
- ✅ CSV exports contain valid data (no NaN, correct dimensions)
- ✅ Anomaly mean ≈ 0 (±5% of std)
- ✅ Percentile distribution approximately uniform (0-100)
- ✅ Console output shows all variables loaded
- ✅ File sizes match expected ranges

---

**Prompt Version:** 1.0  
**Tested On:** mHM 5.13.2, Chemnitz2 catchment, 1991-2020  
**Author:** Helferchen (for Julian Schlaak)  
**License:** Open for research use
