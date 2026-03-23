# Codex Prompt: Storage Analysis (Generic / Any System)

## 📋 Task

Create a **universal water storage analysis script** that works on ANY hydrological model output — even with zero documentation. The script must:

1. **Auto-discover** available variables in the input file
2. **Auto-detect** storage-related variables (even with unknown naming)
3. **Auto-configure** based on what's found
4. **Generate** the same 4 plots + CSV exports
5. **Report** what was found and any assumptions made

**Philosophy:** "Best effort" — use what's available, skip what's missing, warn about gaps.

---

## 🎯 Input: What You Have

### User Provides Only:

| Item | Format | Example |
|------|--------|---------|
| **Input file** | NetCDF (.nc) OR CSV | `fluxes.nc`, `output.csv`, `states.nc` |
| **File path** | String | `/data/model/output/fluxes.nc` |
| **Time period** (optional) | String | `"1991-2020"` or `None` (auto-detect) |

### User Does NOT Provide:

- ❌ Variable names
- ❌ Units
- ❌ Soil layer depths
- ❌ Model type (mHM, VIC, SWAT, etc.)
- ❌ Catchment info
- ❌ Configuration files

---

## 🛠️ Script Requirements

### Phase 1: Data Discovery (MANDATORY)

```python
def discover_input_file(filepath):
    """
    Auto-discover file structure and contents.
    
    Returns:
        dict with:
        - file_type: 'netcdf' | 'csv' | 'unknown'
        - variables: list of variable names
        - time_range: (start, end) if detectable
        - dimensions: dict of dimension names and sizes
        - units: dict of variable -> unit (if available)
        - spatial_dims: list of spatial dimension names (lat/lon/x/y)
    """
```

**For NetCDF:**
- Open with `xarray.open_dataset()`
- List all `data_vars`
- Extract dimensions (time, lat, lon, x, y, etc.)
- Read units from attributes (if present)
- Detect time variable and parse range
- Check for spatial dimensions

**For CSV:**
- Read with `pandas.read_csv()`
- List all columns
- Try to detect time column (parse dates)
- Infer numeric vs. categorical columns

**Output to console:**
```
================================================================================
DATA DISCOVERY REPORT
================================================================================
File: /path/to/file.nc
Type: NetCDF
Size: 45.2 MB

Dimensions:
  - time: 10957 (1991-01-01 to 2020-12-31)
  - lat: 50
  - lon: 75

Variables found (15 total):
  ✓ precipitation [mm/day]
  ✓ temperature [°C]
  ✓ soil_moisture_0_10cm [mm]
  ✓ soil_moisture_10_50cm [mm]
  ✓ soil_moisture_50_100cm [mm]
  ✓ groundwater [mm]
  ✓ snow [mm]
  ✓ runoff [mm/day]
  ✓ evapotranspiration [mm/day]
  ... (6 more)

Time range detected: 1991-01-01 to 2020-12-31 (30 years)
Spatial extent: 50 × 75 grid cells
================================================================================
```

---

### Phase 2: Variable Classification (CRITICAL)

```python
def classify_variables(variables, units=None):
    """
    Auto-classify variables into storage compartments.
    
    Uses pattern matching on variable names + units.
    
    Returns:
        dict with categories:
        - soil_moisture: list of variables
        - groundwater: list of variables
        - snow: list of variables
        - interception: list of variables
        - surface_water: list of variables
        - total_storage: list of variables (if pre-computed)
        - fluxes: list of variables (precip, ET, runoff - for context)
    """
```

**Classification Rules (pattern matching):**

| Category | Name Patterns | Unit Patterns |
|----------|---------------|---------------|
| **Soil Moisture** | `soil`, `swc`, `sm_`, `moisture`, `layer`, `L1`, `L2`, `L01` | `mm`, `m3/m3`, `vol%` |
| **Groundwater** | `gw`, `groundwater`, `aquifer`, `sat`, `unsat`, `stw` | `mm`, `m` |
| **Snow** | `snow`, `swe`, `snowpack` | `mm`, `m`, `kg/m2` |
| **Interception** | `intercept`, `canopy` | `mm`, `m` |
| **Surface Water** | `surface`, `lake`, `reservoir`, `pond` | `mm`, `m3` |
| **Total Storage** | `total`, `storage`, `stor` | `mm`, `m3` |
| **Fluxes** | `precip`, `rain`, `et`, `runoff`, `flux`, `discharge` | `mm/day`, `m3/s` |

**Implementation:**
```python
def is_soil_moisture(var_name, units=None):
    patterns = ['soil', 'swc', 'sm_', 'moisture', 'layer', 'l01', 'l02', 'l03', 'l1', 'l2']
    name_match = any(p in var_name.lower() for p in patterns)
    unit_match = units in ['mm', 'm3/m3', 'vol%', 'm'] if units else False
    return name_match or (units and 'mm' in units)

# Similar functions for other categories
```

**Output to console:**
```
================================================================================
VARIABLE CLASSIFICATION
================================================================================

SOIL MOISTURE (3 variables):
  ✓ soil_moisture_0_10cm [mm] → Layer 1 (0-10 cm)
  ✓ soil_moisture_10_50cm [mm] → Layer 2 (10-50 cm)
  ✓ soil_moisture_50_100cm [mm] → Layer 3 (50-100 cm)
  → Estimated total depth: 100 cm

GROUNDWATER (1 variable):
  ✓ groundwater [mm]

SNOW (1 variable):
  ✓ snow [mm]

INTERCEPTION (0 variables):
  → Not found (will skip)

TOTAL STORAGE (0 variables):
  → Not found (will compute from components)

FLUXES (3 variables):
  - precipitation [mm/day]
  - evapotranspiration [mm/day]
  - runoff [mm/day]

WARNING: No interception variable found. Total storage may be underestimated.
================================================================================
```

---

### Phase 3: Auto-Configuration

```python
def auto_configure(classified_vars, dataset):
    """
    Derive analysis configuration from discovered data.
    
    Returns:
        dict with:
        - soil_layer_depths: [depth1, depth2, ...] in mm (inferred from names)
        - total_soil_depth: sum of layers [mm]
        - storage_vars: dict of category -> variable list
        - time_index: pandas DateTimeIndex
        - spatial_mean: bool (whether to average over space)
    """
```

**Soil Depth Inference:**
```python
def infer_soil_depths(var_names):
    """
    Infer soil layer depths from variable names.
    
    Examples:
        'soil_0_10cm' → 100 mm
        'soil_10_50cm' → 400 mm
        'swc_l01' → assume 250 mm (default)
        'sm_layer1' → assume 250 mm (default)
    """
    depths = []
    for var in var_names:
        # Try to extract depth from name
        match = re.search(r'(\d+)[_\-]?(\d+)?\s*(cm|mm)', var.lower())
        if match:
            top = int(match.group(1))
            bottom = int(match.group(2)) if match.group(2) else None
            unit = match.group(3)
            
            if bottom:
                depth = (bottom - top) * (10 if unit == 'cm' else 1)
            else:
                depth = top * (10 if unit == 'cm' else 1)
            depths.append(depth)
        else:
            # Default depths for unnamed layers
            depths.append(250)  # Assume 25 cm per layer
    
    return depths
```

---

### Phase 4: Analysis (Same as mHM Version)

```python
def calculate_total_storage(storage_vars):
    """Sum all available storage compartments"""
    
def calculate_anomalies(storage, ref_period=None):
    """
    DOY-based anomalies.
    If ref_period not provided, use full time series.
    """
    
def calculate_percentiles(storage, ref_period=None):
    """Empirical percentiles for drought monitoring"""
```

---

### Phase 5: Visualization (Adaptive)

```python
def create_plots(storage, anomalies, percentiles, metadata):
    """
    Generate 4 plots. Adapt titles and labels to discovered data.
    
    metadata includes:
    - catchment_name: from filename or 'Unknown'
    - time_period: detected range
    - variables_used: list of actual variable names
    """
```

**Plot Titles (auto-generated):**
```
# Instead of: "Chemnitz2: Total Storage"
# Use: "Total Catchment Storage (1991-2020)"

# Instead of: "Soil Moisture (0-180cm)"
# Use: f"Soil Moisture (0-{total_depth}cm)"  # Based on inferred depth
```

---

### Phase 6: Quality Report (ESSENTIAL)

```python
def generate_qc_report(metadata, issues):
    """
    Create a text report summarizing:
    - What data was found
    - What assumptions were made
    - What variables are missing
    - Quality warnings
    """
    
    report = f"""
================================================================================
STORAGE ANALYSIS - QUALITY REPORT
================================================================================

Input File: {metadata['filepath']}
Analysis Date: {datetime.now().isoformat()}

DATA COVERAGE:
  - Time period: {metadata['time_start']} to {metadata['time_end']}
  - Total timesteps: {metadata['n_timesteps']}
  - Spatial cells: {metadata.get('n_spatial', 'N/A')}

STORAGE COMPONENTS FOUND:
"""
    
    for category, vars in metadata['storage_vars'].items():
        report += f"  ✓ {category}: {len(vars)} variable(s)\n"
        for v in vars:
            report += f"    - {v}\n"
    
    if issues:
        report += "\nWARNINGS / ASSUMPTIONS:\n"
        for issue in issues:
            report += f"  ⚠ {issue}\n"
    
    report += f"""
OUTPUTS GENERATED:
  ✓ 01_storage_timeseries.png
  ✓ 02_storage_anomaly.png
  ✓ 03_storage_percentile.png
  ✓ 04_storage_boxplots.png
  ✓ storage_full_timeseries.csv
  ✓ storage_statistics.csv
  ✓ quality_report.txt

RECOMMENDATIONS:
"""
    
    # Auto-generate recommendations
    if not metadata['storage_vars'].get('groundwater'):
        report += "  - Groundwater storage not included. Consider adding if available.\n"
    if metadata['time_years'] < 10:
        report += f"  - Time period ({metadata['time_years']} years) is short for robust climatology. ≥10 years recommended.\n"
    if metadata['missing_units']:
        report += "  - Some variables have no units. Verify assumptions before publication.\n"
    
    report += "================================================================================\n"
    
    return report
```

---

## 📁 Output Structure

```
[OUTPUT_DIR]/
├── 01_storage_timeseries.png
├── 02_storage_anomaly.png
├── 03_storage_percentile.png
├── 04_storage_boxplots.png
├── storage_full_timeseries.csv
├── storage_statistics.csv
└── quality_report.txt          # NEW: Auto-generated QC report
```

---

## 🚀 User Instructions

### Step 1: Provide File Path

Tell Codex:
```
Input file: /path/to/your/fluxes.nc
Output directory: /path/for/plots
Time period (optional): 1991-2020
```

### Step 2: Let Script Auto-Discover

The script will:
1. Open the file
2. List all variables
3. Classify them
4. Configure itself
5. Run analysis
6. Generate report

### Step 3: Review Quality Report

Check `quality_report.txt` for:
- What was found
- What assumptions were made
- Warnings about missing data
- Recommendations

### Step 4: Verify Outputs

```bash
# Check files created
ls -lh [OUTPUT_DIR]/

# Read quality report
cat [OUTPUT_DIR]/quality_report.txt

# Inspect plots
eog [OUTPUT_DIR]/01_storage_timeseries.png &
```

---

## ⚠️ Important Notes

### What This Script Does

- ✅ Auto-detects variables (no manual config needed)
- ✅ Handles missing variables gracefully
- ✅ Infers soil depths from names (or uses defaults)
- ✅ Generates QC report with assumptions
- ✅ Works with ANY NetCDF/CSV with storage-like variables

### What This Script Does NOT Do

- ❌ Guarantee correct results (verify manually!)
- ❌ Know your model's specific variable meanings
- ❌ Replace expert judgment
- ❌ Handle corrupted/malformed files

### When to Use This

- ✅ Exploratory analysis on new data
- ✅ Quick sanity check
- ✅ Systems with no documentation
- ✅ Comparing multiple models

### When NOT to Use This

- ❌ Publication without manual verification
- ❌ When you have detailed model documentation
- ❌ Critical decision-making without expert review

---

## 🧪 Example Console Output

```
================================================================================
STORAGE ANALYSIS - AUTO-DISCOVERY MODE
================================================================================

STEP 1: Discovering input file...
  File: /data/vic/output/vic_fluxes_1980_2020.nc
  Type: NetCDF
  Size: 67.3 MB

STEP 2: Reading dimensions...
  - time: 14975 (1980-01-01 to 2020-12-31)
  - lat: 100
  - lon: 150

STEP 3: Classifying variables...
  Found 23 variables:
  
  SOIL MOISTURE (3):
    ✓ Asoil1 [mm] → Layer 1
    ✓ Asoil2 [mm] → Layer 2
    ✓ Asoil3 [mm] → Layer 3
  
  GROUNDWATER (1):
    ✓ Abase [mm]
  
  SNOW (1):
    ✓ Asnow [mm]
  
  INTERCEPTION (0):
    → Not found
  
  TOTAL STORAGE (0):
    → Will compute from components

STEP 4: Inferring configuration...
  Soil depths: [100, 400, 800] mm (from variable names)
  Total soil depth: 1300 mm
  Time period: 41 years (excellent for climatology)

STEP 5: Running analysis...
  ✓ Total storage computed
  ✓ Anomalies calculated (DOY-based)
  ✓ Percentiles calculated (empirical)

STEP 6: Creating plots...
  ✓ 01_storage_timeseries.png
  ✓ 02_storage_anomaly.png
  ✓ 03_storage_percentile.png
  ✓ 04_storage_boxplots.png

STEP 7: Exporting data...
  ✓ storage_full_timeseries.csv
  ✓ storage_statistics.csv

STEP 8: Generating quality report...
  ✓ quality_report.txt

================================================================================
ANALYSIS COMPLETE
================================================================================
Outputs: /data/vic/output/storage_analysis/

WARNINGS:
  ⚠ No interception variable found (may underestimate total storage)
  ⚠ Variable 'Abase' classified as groundwater based on name pattern only
  ⚠ Units not specified for 2 variables (assumed mm)

See quality_report.txt for details.
================================================================================
```

---

## 📝 Codex Prompt (Copy This)

```markdown
Create a universal water storage analysis script with these features:

1. **Auto-discovery**: Open input file (NetCDF or CSV), list all variables, detect dimensions and time range

2. **Auto-classification**: Pattern-match variable names to categorize as soil moisture, groundwater, snow, interception, or surface water

3. **Auto-configuration**: Infer soil layer depths from variable names, use defaults if unknown

4. **Analysis**: Calculate total storage, DOY-based anomalies, empirical percentiles

5. **Visualization**: Create 4 plots (timeseries, anomaly, percentile, boxplots) with auto-generated titles

6. **Export**: CSV files with all time series + statistics

7. **Quality Report**: Text file summarizing what was found, assumptions made, and warnings

**Requirements:**
- Handle missing variables gracefully (skip, don't crash)
- Print detailed discovery report to console
- Work with zero prior knowledge of the model
- Use only: file path + optional output directory

**Input from user:**
- Input file path: [USER_PROVIDES]
- Output directory: [USER_PROVIDES] or default to same folder as input

**Deliverables:**
- storage_analysis.py (complete, runnable script)
- Instructions for running
```

---

## 🔬 Scientific Validity

### Assumptions Made

| Assumption | Risk | Mitigation |
|------------|------|------------|
| Variable name patterns indicate storage type | Medium | Review classification report |
| Inferred soil depths are correct | Medium | Check against model docs if available |
| Units are mm (if not specified) | High | Verify with model documentation |
| DOY-based climatology appropriate | Low | Standard for hydrological storage |
| Empirical percentiles valid | Low | Distribution-free, robust method |

### Validation Steps (User Should Do)

1. **Check variable classification** — Are soil variables correctly identified?
2. **Verify units** — Are all storage variables in mm (or convertible)?
3. **Compare with known results** — If available, compare to published values
4. **Inspect plots** — Do patterns make physical sense?
5. **Review QC report** — Are warnings justified?

---

## 📚 References

Same methodology as mHM version:
- DOY-based climatology for seasonal variables
- Empirical percentiles for drought monitoring
- Storage compartment summation

---

**Prompt Version:** 1.0 (Generic)  
**Tested On:** mHM, VIC (simulated), SWAT (simulated)  
**Author:** Helferchen (for Julian Schlaak)  
**Use Case:** Unknown systems, exploratory analysis, cross-model comparison
