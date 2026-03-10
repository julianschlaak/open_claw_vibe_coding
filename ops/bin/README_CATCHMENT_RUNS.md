# 🏃 Catchment Simulation Scripts

## Overview

Scripts for running mHM simulations on all 6 calibrated catchments (1991-2020) using the recommended parameter set from DDS analysis.

## Catchments

1. **Parthe_0p0625**
2. **Goeltzsch2_0p0625**
3. **Chemnitz2_0p0625**
4. **Wesenitz2_0p0625**
5. **Wyhra_0p0625**
6. **Zwoenitz1_0p0625**

## Period

**1991-2020** (30 years, consistent with CAMELS-DE)

---

## 🚀 Quick Start

### Option A: Use Existing FinalParam.nml (Recommended)

After DDS calibration, each catchment has a `FinalParam.nml` file with optimized parameters.

```bash
# Run all 6 catchments
cd /data/.openclaw/workspace/open_claw_vibe_coding
bash ops/bin/run_all_6_catchments_1991_2020.sh
```

**What it does:**
- Copies `FinalParam.nml` → `nml/mhm_parameter.nml` for each catchment
- Runs mHM for 1991-2020
- Outputs: `output/daily_discharge.out`, `output/*.nc`

---

### Option B: Use Recommended Parameter Set (GLOBAL parameters)

If you want to use the **recommended_params.csv** from the dashboard:

```bash
# 1. Generate mhm_parameter.nml from CSV
cd /data/.openclaw/workspace/open_claw_vibe_coding
python ops/bin/generate_param_nml_from_csv.py \
  dashboard_saxony/utils/recommended_params.csv \
  code/mhm_re_crit/runs/parthe_0p0625/nml/mhm_parameter.nml

# 2. Copy to all catchments
for ch in parthe_0p0625 goeltzsch2_0p0625 chemnitz2_0p0625 wesenitz2_0p0625 wyhra_0p0625 zwoenitz1_0p0625; do
  cp code/mhm_re_crit/runs/parthe_0p0625/nml/mhm_parameter.nml \
     code/mhm_re_crit/runs/$ch/nml/mhm_parameter.nml
done

# 3. Run all catchments
bash ops/bin/run_all_6_catchments_1991_2020.sh
```

**Note:** This uses **GLOBAL** parameters (CV < 0.1) for all catchments.
**LOKAL** parameters (CV > 0.3) should be catchment-specific.

---

## 📋 Manual Steps (Before Running)

### 1. Check Time Period in mhm.nml

For each catchment, verify:

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625
grep -i "startDate\|endDate" nml/mhm.nml
```

**Expected:**
```
startDate = "1991-01-01"
endDate   = "2020-12-31"
```

**If wrong:** Edit `nml/mhm.nml` manually.

---

### 2. Check Input Data

Ensure input data exists for 1991-2020:

```bash
ls -la input/metera/
ls -la input/latlon/
ls -la input/lai/
```

---

### 3. Backup Existing Results

```bash
# Backup old output
for ch in parthe_0p0625 goeltzsch2_0p0625 chemnitz2_0p0625 wesenitz2_0p0625 wyhra_0p0625 zwoenitz1_0p0625; do
  mv code/mhm_re_crit/runs/$ch/output \
     code/mhm_re_crit/runs/$ch/output.backup.$(date +%Y%m%d)
done
```

---

## 📊 Output Files

After successful run:

```
runs/<catchment>/output/
├── daily_discharge.out      # Daily discharge (Qobs, Qsim)
├── daily_recharge.out       # Daily recharge
├── daily_soilmoisture.out   # Daily soil moisture
├── *.nc                     # NetCDF outputs (raster data)
└── mhm.log                  # Run log
```

---

## 🔍 Post-Processing

After all runs complete:

```bash
# Run analysis pipeline
bash ops/bin/worker_once.sh

# View dashboard
# http://187.124.13.209:8502
```

---

## 🐛 Troubleshooting

### Error: "File not found"

Check input data paths in `mhm.nml`:
```
&meteo_input
  path_meteo = "input/meteo/"
/
```

### Error: "Segmentation fault"

Check memory limits. mHM for 30 years needs ~2-4 GB RAM.

### Error: "Time period mismatch"

Edit `nml/mhm.nml`:
```fortran
startDate = "1991-01-01"
endDate   = "2020-12-31"
```

---

## 📝 Log Files

Runtime logs are saved in:

```
runs/<catchment>/
├── mhm.log              # Current run
├── output/mhm.log       # Detailed log
└── ConfigFile.log       # Configuration used
```

---

## 🧪 Testing

### Test single catchment (short run)

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm_re_crit/runs/parthe_0p0625
mhm ./parthe_0p0625
```

### Test with 1 year (debug)

Edit `nml/mhm.nml`:
```fortran
startDate = "2018-01-01"
endDate   = "2018-12-31"
```

Then run full script.

---

## 📦 Dependencies

- mHM 5.13.2 (in container)
- Python 3.13 (miniforge)
- pandas, numpy (for CSV script)

---

## 📄 License

Part of open_claw_vibe_coding project.

**Author:** Helferchen (Research Assistant)  
**Date:** 2026-03-10
