# 🏔️ Saxony Catchment Simulation (1991-2020)

## Overview

Scripts for setting up and running mHM simulations on the **Saxony catchment** (ungauged) using the **recommended parameter set** from DDS analysis of 6 calibrated catchments.

---

## Catchment Details

| Property | Value |
|----------|-------|
| **ID** | `saxony_0p0625` |
| **Name** | Saxony |
| **Resolution** | 0.0625° (~6.25 km) |
| **Period** | 1991-2020 (30 years) |
| **Status** | **Ungauged** (no local calibration) |
| **Parameters** | GLOBAL means from 6 catchments |

---

## 🚀 Quick Start

### Step 1: Setup (Run Once)

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding
bash ops/bin/setup_saxony_0p0625_1991_2020.sh
```

**What it does:**
- Creates run directory: `code/mhm/runs/saxony_0p0625/`
- Copies input data from `catchments_cloud/saxony_0p0625/input/`
- Generates `mhm_parameter.nml` from `recommended_params.csv`
- Creates `mhm.nml` (adjusted from parthe template)

---

### Step 2: Run Simulation

```bash
bash ops/bin/run_saxony_0p0625_1991_2020.sh
```

**What it does:**
- Verifies configuration (time period, input data)
- Runs mHM for 1991-2020 (30 years)
- Outputs: `output/daily_discharge.out`, `output/*.nc`

**Expected runtime:** ~30-60 minutes (depends on hardware)

---

## 📂 Directory Structure

After setup:

```
code/mhm/runs/saxony_0p0625/
├── nml/
│   ├── mhm.nml              # Main config (1991-2020)
│   └── mhm_parameter.nml    # Parameters (GLOBAL means)
├── input/
│   ├── meteo/               # Meteorological forcing
│   ├── morph/               # Morphological data
│   ├── lai/                 # Leaf Area Index
│   └── latlon/              # Lat/Lon coordinates
├── output/                  # Created during run
│   ├── daily_discharge.out  # Daily discharge (Qsim)
│   ├── daily_recharge.out   # Daily recharge
│   ├── daily_soilmoisture.out
│   └── *.nc                 # NetCDF raster outputs
├── restart/                 # Restart files (if enabled)
└── mhm.log                  # Run log
```

---

## 🔧 Parameter Strategy

### For Ungauged Catchments

Since Saxony is **ungauged** (no observed discharge for calibration), we use:

| Parameter Type | Strategy | Source |
|----------------|----------|--------|
| **GLOBAL** (CV < 0.1) | Mean across 6 catchments | `recommended_params.csv` |
| **GLOBAL ±σ** (CV 0.1-0.3) | Mean with uncertainty | `recommended_params.csv` |
| **CATCHMENT_SPECIFIC** (CV > 0.3) | **Use GLOBAL mean** | Not applicable |

**Rationale:**
- No local calibration possible (ungauged)
- GLOBAL parameters are robust across catchments
- Suitable for regionalization studies
- Can be compared with calibrated catchments

---

## 📊 Output Files

### Daily Discharge

**File:** `output/daily_discharge.out`

**Format:**
```
# Date  Qobs  Qsim
1991-01-01  -  1.234
1991-01-02  -  1.456
...
```

**Note:** Qobs is `-` (ungauged, no observations).

---

### NetCDF Outputs

**Files:** `output/*.nc`

**Variables:**
- Soil moisture (0-25cm, 25-50cm, 50-100cm)
- Recharge
- Actual/Potential ET
- Snow water equivalent
- Groundwater storage

---

## 🔍 Post-Processing

### Add to Dashboard

After simulation completes, Saxony data will be available in:

```
Dashboard → "🌊 Discharge (6 Catchments)" → Add "Saxony"
```

**Manual integration:**
1. Copy `daily_discharge.out` to dashboard data folder
2. Update dashboard config to include Saxony
3. Reload dashboard

---

### Run Analysis Pipeline

```bash
bash ops/bin/worker_once.sh
```

**Outputs:**
- Drought indices (SMI, SPI, SPEI)
- Correlation analysis
- Heatmaps, timeseries
- MDI (Matrix Drought Index)

---

## 🐛 Troubleshooting

### Error: "Input data not found"

**Solution:** Check input paths in `mhm.nml`:
```bash
grep "dir_" nml/mhm.nml
```

Ensure symlinks exist:
```bash
ls -la input/
```

---

### Error: "Time period mismatch"

**Solution:** Edit `nml/mhm.nml`:
```fortran
startDate = "1991-01-01"
endDate   = "2020-12-31"
```

---

### Error: "Segmentation fault"

**Cause:** Memory issue (30 years, 0.0625° resolution)

**Solution:**
- Increase container memory limit
- Run shorter period first (test):
  ```fortran
  startDate = "2018-01-01"
  endDate   = "2018-12-31"
  ```

---

### Error: "Invalid parameter value"

**Solution:** Check `mhm_parameter.nml`:
```bash
grep "param_" nml/mhm_parameter.nml | head -20
```

Ensure values are within valid ranges (see mHM documentation).

---

## 📈 Comparison with Calibrated Catchments

| Catchment | Calibration | KGE (expected) | Use Case |
|-----------|-------------|----------------|----------|
| Parthe | DDS (200 iter) | > 0.5 | Reference |
| Goeltzsch2 | DDS (200 iter) | > 0.5 | Urban |
| Chemnitz2 | DDS (100 iter) | > 0.5 | Industrial |
| Wesenitz2 | DDS (100 iter) | > 0.5 | Mixed |
| Wyhra | DDS (100 iter) | > 0.5 | Agricultural |
| Zwoenitz1 | DDS (100 iter) | > 0.5 | Reference |
| **Saxony** | **None (ungauged)** | **?** | **Regionalization** |

---

## 🧪 Testing

### Test Run (1 year)

Edit `nml/mhm.nml`:
```fortran
startDate = "2018-01-01"
endDate   = "2018-12-31"
```

Run:
```bash
bash ops/bin/run_saxony_0p0625_1991_2020.sh
```

Check output, then restore full period.

---

### Compare with Parthe

```bash
# Run both catchments
bash ops/bin/run_all_6_catchments_1991_2020.sh
bash ops/bin/run_saxony_0p0625_1991_2020.sh

# Compare discharge
cat runs/parthe_0p0625/output/daily_discharge.out | head -10
cat runs/saxony_0p0625/output/daily_discharge.out | head -10
```

---

## 📝 Log Files

**Runtime logs:**
- `runs/saxony_0p0625/mhm.log`
- `runs/saxony_0p0625/output/mhm.log`
- `runs/saxony_0p0625/ConfigFile.log`

**Check for errors:**
```bash
grep -i "error\|warning" runs/saxony_0p0625/output/mhm.log
```

---

## 📦 Dependencies

- mHM 5.13.2 (in container)
- Python 3.13 (miniforge)
- pandas, numpy (for setup script)

---

## 📄 Related Scripts

| Script | Purpose |
|--------|---------|
| `setup_saxony_0p0625_1991_2020.sh` | Prepare run directory |
| `run_saxony_0p0625_1991_2020.sh` | Execute simulation |
| `run_all_6_catchments_1991_2020.sh` | Run calibrated catchments |
| `generate_recommended_param_nml.py` | Generate NML from CSV |

---

## 📚 References

- mHM Documentation: https://www.mhm-model.org/
- DDS Calibration: `README_CATCHMENT_RUNS.md`
- Dashboard: `dashboard_saxony/BEDIENUNGSANLEITUNG_dashboard.md`

---

**Author:** Helferchen (Research Assistant)  
**Date:** 2026-03-10  
**Project:** open_claw_vibe_coding (PhD Paper #1)
