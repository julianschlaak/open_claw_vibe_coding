# mHM Storage Analysis Guide

## 📋 Overview

This guide provides a complete, reproducible methodology for analyzing water storage dynamics from mHM model outputs. The analysis computes:

1. **Total Catchment Storage** — Sum of all water compartments
2. **Storage Anomalies** — Deviations from climatology (DOY-based)
3. **Storage Percentiles** — Drought indicator (empirical percentile)
4. **Seasonal Boxplots** — Monthly distribution patterns

**Output:** 4 publication-ready plots + CSV data exports

---

## 🎯 What This Analysis Produces

| Plot | Description | Use Case |
|------|-------------|----------|
| `01_storage_timeseries.png` | All storage compartments over time (1991-2020) | Overview, water balance |
| `02_storage_anomaly.png` | Anomalies vs. climatology (filled line plot) | Drought/flood detection |
| `03_storage_percentile.png` | Empirical percentiles with drought thresholds | Drought monitoring (SMI-like) |
| `04_storage_boxplots.png` | Seasonal distribution by month | Climatological patterns |

**Data Exports:**
- `storage_full_timeseries.csv` — All variables (360 months)
- `storage_statistics.csv` — Mean, std, min, max per variable

---

## 📁 File Structure

```
open_claw_vibe_coding/
├── analysis/
│   ├── scripts/
│   │   └── mhm_storage_analysis.py    # Main analysis script
│   └── plots/
│       └── <catchment>/
│           └── storage/                # Output directory
│               ├── 01_storage_timeseries.png
│               ├── 02_storage_anomaly.png
│               ├── 03_storage_percentile.png
│               ├── 04_storage_boxplots.png
│               ├── storage_full_timeseries.csv
│               └── storage_statistics.csv
└── code/
    └── mhm/
        └── runs/
            └── <catchment>/
                └── output/
                    └── mHM_Fluxes_States.nc    # Input file
```

---

## 🔧 Prerequisites

### Python Environment

```bash
# Required packages
numpy>=1.21
pandas>=1.3
xarray>=0.19
matplotlib>=3.4
seaborn>=0.11
```

### Input Data

**Required:** `mHM_Fluxes_States.nc` from mHM model run

**Expected variables:**
| Variable | Description | Unit | Required |
|----------|-------------|------|----------|
| `interception` | Canopy storage | mm | No |
| `snowpack` | Snow water equivalent | mm | No |
| `SWC_L01/L02/L03` | Soil moisture layers | mm | Yes |
| `SWC_LALL` | Total soil moisture | mm | Yes (or SM_Lall) |
| `SM_L01/L02/L03/Lall` | Volumetric soil moisture | mm/mm | Alternative |
| `unsatSTW` | Unsaturated groundwater | mm | No |
| `satSTW` | Saturated groundwater | mm | No |
| `sealedSTW` | Sealed area storage | mm | No |

---

## 🚀 Quick Start

### Step 1: Configure Paths

Edit the **KONFIGURATION** section in `mhm_storage_analysis.py`:

```python
BASE_DIR = Path("/path/to/your/workspace")
RUN_DIR = BASE_DIR / "code/mhm/runs/YOUR_CATCHMENT"
OUTPUT_DIR = RUN_DIR / "output"

# Input file (must exist)
FLUXES_STATES_FILE = OUTPUT_DIR / "mHM_Fluxes_States.nc"

# Output directory for plots
PLOT_DIR = BASE_DIR / "analysis/plots/YOUR_CATCHMENT/storage"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Analysis period
START_DATE = "1991-01-01"
END_DATE = "2020-12-31"

# Soil layer depths [mm] — adjust to your mHM setup
SOIL_L1_DEPTH = 250    # 0-25 cm
SOIL_L2_DEPTH = 750    # 25-100 cm
SOIL_L3_DEPTH = 800    # 100-180 cm
SOIL_TOTAL_DEPTH = 1800  # 0-180 cm
```

### Step 2: Run Analysis

```bash
# Activate conda/mamba environment
conda activate your_env

# Run the script
python mhm_storage_analysis.py
```

### Step 3: Check Outputs

```bash
# List generated files
ls -lh analysis/plots/YOUR_CATCHMENT/storage/

# Expected: 4 PNGs + 2 CSVs
```

---

## 📊 Methodology Details

### 1. Total Storage Calculation

```python
Total Storage = interception + snowpack + SWC_LALL + unsatSTW + satSTW + sealedSTW
```

All available compartments are summed. Missing variables are skipped gracefully.

### 2. Storage Anomalies (DOY-based Climatology)

For each day of year (DOY), compute climatology from reference period:

```python
# For each DOY (1-365/366)
climatology[doy] = mean(storage[all_days_with_same_doy])

# Anomaly = current value - climatology
anomaly[date] = storage[date] - climatology[date.dayofyear]
```

**Reference period:** Configurable (default: 1991-2020)

**Why DOY-based?** Accounts for strong seasonality in storage dynamics.

### 3. Storage Percentiles (Empirical Drought Indicator)

For each DOY, compute empirical percentile rank:

```python
# For each value, compute percentile rank among same-DOY values
rank = (values_same_doy < current_value).sum() + 1
n = count(values_same_doy)
percentile = 100 * rank / (n + 1)
```

**Drought thresholds:**
| Percentile | Drought Class |
|------------|---------------|
| < 2 | Extreme Drought |
| < 5 | Severe Drought |
| < 10 | Moderate Drought |
| < 20 | Mild Drought |
| 20-80 | Normal |
| > 80 | Wet |

**Advantage:** No distributional assumptions (non-parametric).

### 4. Seasonal Boxplots

Monthly boxplots show seasonal patterns:
- Median, IQR, whiskers (1.5×IQR)
- Color-coded by compartment
- 12 boxes per plot (Jan-Dec)

---

## 🎨 Visualization Design

### Plot 1: Storage Timeseries
- **4 panels:** Total, Soil Layers (L1/L2/L3), Groundwater, Surface (Interception+Snow)
- **Style:** Line + fill for total storage
- **X-axis:** Years (1991-2020)
- **Y-axis:** Storage [mm]

### Plot 2: Storage Anomalies
- **3 panels:** Total, Soil Moisture, Groundwater
- **Style:** Line plot with filled areas (red=positive, blue=negative)
- **Zero line:** Black solid line
- **Color scheme:** RdBu (diverging)

### Plot 3: Storage Percentiles
- **3 panels:** Total, Soil Moisture, Groundwater
- **Style:** Line + fill
- **Threshold lines:** 20, 10, 5, 2 percentile (dashed)
- **Y-axis:** 0-100 percentile

### Plot 4: Seasonal Boxplots
- **4 panels:** Total, Soil, Groundwater, Snow
- **Style:** Boxplot with color gradient (Jan→Dec)
- **X-axis:** Month names (Jan-Dez)

---

## 🔍 Quality Control

### Before Running

1. ✅ Check input file exists: `mHM_Fluxes_States.nc`
2. ✅ Verify time period covers at least 10 years (for robust climatology)
3. ✅ Confirm soil layer depths match your mHM setup
4. ✅ Check output directory is writable

### After Running

1. ✅ Verify all 4 PNGs created (>100KB each)
2. ✅ Check CSV exports have correct row count (360 months for 1991-2020)
3. ✅ Inspect plots for artifacts (gaps, spikes, wrong scaling)
4. ✅ Validate anomaly mean ≈ 0 (climatology centered)
5. ✅ Validate percentile distribution (uniform 0-100)

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing variables | mHM output doesn't have variable | Script skips gracefully (check log) |
| Anomaly not centered | Short reference period | Use ≥10 years |
| Percentile clumping | Too few years | Use ≥10 years for smooth distribution |
| Plot colors wrong | Matplotlib version | Update to ≥3.4 |

---

## 📈 Interpretation Guide

### Storage Timeseries

**What to look for:**
- Seasonal amplitude (summer low, winter high)
- Multi-year trends (drought periods, wet periods)
- Compartment coupling (soil vs. groundwater response)

**Example:** Chemnitz2 shows strong seasonality in soil moisture, damped response in groundwater.

### Storage Anomalies

**What to look for:**
- Persistent negative anomalies (drought events)
- Compound events (multiple compartments negative)
- Recovery time (return to normal conditions)

**Example:** 2018-2020 drought shows sustained negative anomalies in all compartments.

### Storage Percentiles

**What to look for:**
- Frequency of drought days (percentile < 20)
- Extreme events (percentile < 5)
- Propagation (soil → groundwater lag)

**Example:** 2018 drought: soil moisture dropped to <2 percentile, groundwater followed with 2-3 month lag.

### Seasonal Boxplots

**What to look for:**
- Seasonal range (IQR)
- Median shift (climate change signal)
- Outliers (extreme events)

**Example:** Soil moisture shows lowest median in September, highest in March.

---

## 🔄 Adapting to Other Systems

### Different Catchment

1. Change `RUN_DIR` to your catchment path
2. Adjust `PLOT_DIR` for output location
3. Verify soil layer depths (may differ by model setup)

### Different Time Period

1. Adjust `START_DATE` and `END_DATE`
2. Ensure reference period is long enough (≥10 years recommended)
3. Update plot titles if needed

### Different Model Output Format

If your NetCDF has different variable names:

1. Edit `extract_storage_variables()` function
2. Map your variable names to expected keys
3. Ensure units are consistent (mm for storage)

**Example for different naming:**
```python
# If your file uses 'SoilMoisture_L1' instead of 'SWC_L01'
if 'SoilMoisture_L1' in ds.data_vars:
    storage['swc_l01'] = ds['SoilMoisture_L1'].mean(dim=['lat', 'lon']).to_series()
```

### Different Output Format (not NetCDF)

If your model outputs CSV or other formats:

1. Replace `load_mhm_states()` function
2. Load data into pandas DataFrame with DateTimeIndex
3. Ensure column names match expected variables
4. Rest of pipeline remains unchanged

---

## 📝 Example: Applying to New Catchment

**Scenario:** You have mHM run for "Elbe" catchment at `/data/mhm/runs/elbe/`

### Step 1: Copy Script

```bash
cp analysis/scripts/mhm_storage_analysis.py analysis/scripts/elbe_storage_analysis.py
```

### Step 2: Edit Configuration

```python
BASE_DIR = Path("/data")
RUN_DIR = BASE_DIR / "mhm/runs/elbe"
OUTPUT_DIR = RUN_DIR / "output"
FLUXES_STATES_FILE = OUTPUT_DIR / "mHM_Fluxes_States.nc"
PLOT_DIR = BASE_DIR / "analysis/plots/elbe/storage"

START_DATE = "1981-01-01"  # Different period
END_DATE = "2010-12-31"
```

### Step 3: Run

```bash
python analysis/scripts/elbe_storage_analysis.py
```

### Step 4: Verify

```bash
ls -lh analysis/plots/elbe/storage/
# Should show: 01-04 PNGs + CSVs
```

---

## 🧪 Testing & Validation

### Unit Test: Climatology Calculation

```python
# Verify DOY-based climatology is correct
test_ts = pd.Series([1,2,3,4,5,6,7,8,9,10], 
                    index=pd.date_range('2000-01-01', periods=10, freq='D'))
# DOY 1: values [1], climatology[1] = 1
# DOY 2: values [2], climatology[2] = 2
# etc.
```

### Integration Test: Known Drought Event

Run on catchment with known drought (e.g., 2018 in Germany):
- Expect percentile < 10 during summer 2018
- Expect negative anomalies during same period
- Compare with independent drought index (e.g., SPI)

---

## 📚 References

### Methodology

- **Percentile-based drought indices:** 
  - Keyantash & Dracup (2002), "The Quantification of Drought"
  - Used in USDM (U.S. Drought Monitor)
  
- **DOY-based climatology:**
  - Standard approach for hydrological variables with strong seasonality
  - Removes seasonal cycle, isolates anomalies

### Related Work

- **Storage-based drought monitoring:**
  - Thomas et al. (2014), "Groundwater storage variability..."
  - Rodell et al. (2009), "Satellite-based groundwater measurements"

---

## 🛠️ Troubleshooting

### Error: "FileNotFoundError: mHM_Fluxes_States.nc"

**Cause:** Input file not found at configured path

**Fix:** 
1. Check `RUN_DIR` and `OUTPUT_DIR` paths
2. Verify file exists: `ls -lh <path>/mHM_Fluxes_States.nc`
3. If filename differs, update `FLUXES_STATES_FILE`

### Error: "No variables found in NetCDF"

**Cause:** NetCDF file is empty or corrupted

**Fix:**
1. Check file size: `ls -lh <file>`
2. Inspect with ncdump: `ncdump -h <file>`
3. Re-run mHM if file is incomplete

### Error: "matplotlib.cm has no attribute 'X'"

**Cause:** Colormap name typo or old matplotlib version

**Fix:**
1. Use standard colormaps: Blues, Greens, Reds, RdBu
2. Update matplotlib: `pip install --upgrade matplotlib`

### Plot looks wrong (flat lines, no variation)

**Cause:** Data not loaded correctly or wrong variable

**Fix:**
1. Check script output for "✓" messages (variables loaded)
2. Inspect CSV export: `head storage_full_timeseries.csv`
3. Verify NetCDF has expected variables: `ncdump -h <file> | grep "float"`

---

## 📞 Support

**Issues:** Open GitHub issue in project repository

**Questions:** Contact project maintainer

**Citation:** If using this methodology in publications, cite:
- This guide (include URL/path)
- Original percentile drought index papers
- mHM model paper (Samaniego et al.)

---

**Version:** 1.0  
**Last Updated:** 2026-03-09  
**Author:** Helferchen (for Julian Schlaak)  
**Tested On:** Chemnitz2 catchment (1991-2020, 30 years)
