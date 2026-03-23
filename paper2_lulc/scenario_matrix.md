# Paper #2 LULC: mHM Szenario-Matrix

**Document Type:** Experimental Design for mHM LULC Scenarios  
**Purpose:** Structured scenario matrix for LULC impact analysis  
**Created:** 2026-03-11  
**Region Focus:** Harz (primary),可扩展 (CAMELS-DE catchments)

---

## 1. Motivation: Harz 2018-2020 Drought as Natural Experiment

**Historical Context:**
- **2018-2020 Drought:** Most severe 3-year drought in Central Europe since 1901
- **Harz Impact:** ~30-50% Norway Spruce mortality (Picea abies)
- **Cause:** Compound drought + bark beetle outbreak (Ips typographus)
- **Result:** Large-scale forest conversion (monoculture → mixed forest / clearcut)

**Research Question:**
> "What would have happened to soil water balance if the forest had NOT died?"
> - Counterfactual: Spruce monoculture (pre-2018 state)
> - Alternative: Mixed forest (Beech + Spruce)
> - Reality: Clearcut / salvage logging (post-2018)

**Scientific Value:**
- **Natural experiment:** Real drought event (not hypothetical)
- **Policy relevance:** Forest management decisions (monoculture vs. mixed)
- **Climate adaptation:** Resilience of forest types to compound drought

---

## 2. Scenario Matrix (3×3 Design)

### 2.1 Primary Scenarios (Harz Catchment)

| Scenario ID | LULC State | Forest Type | LAI | Interception | Root Depth | Description |
|-------------|------------|-------------|-----|--------------|------------|-------------|
| **S0: Baseline** | Pre-2018 | 100% Spruce monoculture | 8.0 (evergreen) | 30-35% annual | 0.5-1.5m | Historical state (healthy forest) |
| **S1: Counterfactual** | Post-2018 (no mortality) | 100% Spruce monoculture | 8.0 (evergreen) | 30-35% annual | 0.5-1.5m | "What if forest survived?" |
| **S2: Alternative** | Post-2018 (converted) | 50% Spruce + 50% Beech (mixed) | 7.0 (summer) / 4.0 (winter) | 18-28% annual | 2.0-3.0m (weighted) | "What if converted to mixed forest?" |
| **S3: Reality** | Post-2018 (observed) | Clearcut / salvage logging | 0.2 (bare) / 3.0 (regrowth) | 5-10% (bare) / 15-20% (regrowth) | 0.5-1.0m | Actual post-2018 state |

**Time Periods:**
- **Pre-2018:** 1991-2017 (baseline climate, healthy forest)
- **Post-2018:** 2018-2020 (drought period, forest mortality)
- **Recovery:** 2021-2026 (regrowth, conversion)

---

### 2.2 Extended Scenarios (Expandable to Other Catchments)

| Scenario ID | LULC Change | Forest Type Transition | Expected Hydrological Effect | Source |
|-------------|-------------|------------------------|------------------------------|--------|
| **S4: Afforestation** | Agriculture → Forest | Grassland → Spruce monoculture | -20-30% annual runoff, +20-30% ET | Bosch & Hewlett 1982 |
| **S5: Deforestation** | Forest → Agriculture | Spruce → Grassland/Crops | +40-60% annual runoff, -30-50% ET | Bosch & Hewlett 1982 |
| **S6: Urbanization** | Forest → Urban | Spruce → Impervious surface | +50-100% peak flow, +10-30% annual runoff | Booth 2005, Pijl 2022 |
| **S7: Forest Age** | Mature → Young | Old Spruce (LAI 8) → Young Spruce (LAI 3) | +10-20% runoff, -10-20% ET | Calder 1978 |
| **S8: Climate × LULC** | LULC + Climate Change | Spruce + RCP 4.5 (2050) | Non-additive: +10-30% interaction | Preetha 2023, Dixit 2022 |

**Expandable Regions:**
- **Harz:** Primary (2018-2020 drought, spruce mortality)
- **Erzgebirge:** Similar climate, spruce-dominated
- **Sächsische Schweiz:** Mixed forest (beech component)
- **CAMELS-DE catchments:** 456 German catchments (available data)

---

## 3. mHM Implementation Parameters

### 3.1 Forest Type Parameters (from forest_type_parameters.md)

| Parameter | Spruce | Beech (summer) | Beech (winter) | Mixed (50/50) | Clearcut |
|-----------|--------|----------------|----------------|---------------|----------|
| **LAI (m²/m²)** | 8.0 | 6.0 | 0.2 | 7.0 / 4.0 | 0.2 / 3.0 |
| **Canopy Storage (mm)** | 3.5 | 2.0 | 0.5 | 2.8 / 1.5 | 0.5 / 1.0 |
| **Root Depth (m)** | 1.0 | 3.0 | 3.0 | 2.0 | 0.5 |
| **Manning's n** | 0.7 | 0.6 | 0.6 | 0.65 | 0.3 |
| **CN (HSG B)** | 50 | 55 | 55 | 52 | 71 |
| **Albedo** | 0.10 | 0.18 | 0.30 | 0.14 / 0.22 | 0.22 |
| **Ksat (mm/h)** | 120 | 150 | 150 | 135 | 50 |
| **Transpiration (mm/day, peak)** | 3.0 | 4.0 | 0.0 | 3.5 / 1.5 | 2.0 |

**Seasonal Dynamics:**
- **Spruce:** Evergreen (constant parameters year-round)
- **Beech:** Deciduous (dynamic LAI: 0.2 → 6.0 → 0.2 annual cycle)
- **Mixed:** Weighted average (seasonal variation from beech component)
- **Clearcut:** Bare soil (low LAI) → regrowth (increasing LAI)

---

### 3.2 Multi-Year LULC Implementation (Busari et al. 2021)

**Critical: Use Multi-Year LULC, NOT Static!**

```python
# Multi-year LULC for Harz scenarios
corine_years = [2006, 2012, 2018]  # 6-year intervals
for year in corine_years:
    lulc = load_corine(year, region='harz')  # 100m resolution
    lai = load_modis_lai(year, region='harz')  # Monthly LAI, 500m
    mhm_setup(lulc, lai, pet_method='LAI-based')
```

**LULC Datasets:**
- **CORINE:** 100m, 6-year (2006, 2012, 2018, 2024)
- **MODIS:** Yearly, 500m (MOD15A2H, 8-day LAI)
- **Hybrid:** CORINE + MODIS (recommended by Busari 2021)

**PET Method:**
- **Default mHM:** Aspect-based (static) — ❌ Suboptimal
- **Recommended:** LAI-based (monthly) — ✅ +20-30% performance

---

## 4. Expected Hydrological Responses

### 4.1 Harz Scenarios (S0-S3)

| Scenario | ΔRunoff (Annual) | ΔET (Annual) | ΔPeak Flow | ΔBaseflow | ΔSoil Moisture |
|----------|-----------------|--------------|------------|-----------|----------------|
| **S0: Baseline** | 0% (reference) | 0% (reference) | 0% (reference) | 0% (reference) | 0% (reference) |
| **S1: Counterfactual** | 0% (same as S0) | 0% (same as S0) | 0% (same as S0) | 0% (same as S0) | 0% (same as S0) |
| **S2: Alternative (Mixed)** | +10-15% | -5-10% | +10-15% | +5-10% | +5-10% (deeper roots) |
| **S3: Reality (Clearcut)** | +40-60% | -30-50% | +50-100% | -10-20% | -20-30% (loss of buffering) |

**Sources:** Bosch & Hewlett (1982), Zhang et al. (2020), Preetha & Hasan (2023), Pijl & Tarolli (2022).

**Mechanisms:**
- **Mixed forest (S2):** Lower winter interception (beech leaf-off) → +10-15% runoff
- **Clearcut (S3):** Loss of interception + ET → +40-60% runoff, +50-100% peak flow
- **Soil moisture (S3):** Reduced root water uptake → -20-30% soil moisture (drought amplification)

---

### 4.2 Extended Scenarios (S4-S8)

| Scenario | ΔRunoff (Annual) | ΔET (Annual) | ΔPeak Flow | ΔBaseflow | Source |
|----------|-----------------|--------------|------------|-----------|--------|
| **S4: Afforestation** | -20-30% | +20-30% | -30-50% | +10-20% | Bosch & Hewlett 1982 |
| **S5: Deforestation** | +40-60% | -30-50% | +50-100% | -10-20% | Bosch & Hewlett 1982 |
| **S6: Urbanization** | +10-30% | -10-20% | +50-100% | -20-40% | Booth 2005, Pijl 2022 |
| **S7: Forest Age** | +10-20% | -10-20% | +15-25% | 0 to -5% | Calder 1978 |
| **S8: Climate × LULC** | +30-50% (combined) | -20-40% (combined) | +40-70% (combined) | -10-30% | Preetha 2023, Dixit 2022 |

**Non-Additive Effects (S8: Climate × LULC):**
- **LULC effect:** +10-15% runoff (mixed vs. spruce)
- **Climate effect:** +20-30% runoff (RCP 4.5, 2050)
- **Interaction:** +10-30% (non-linear, > additive)
- **Combined:** +40-75% (not +30-45% additive)

**Source:** Preetha & Hasan (2023) — Compound LULC+climate, interaction term 10-30%.

---

## 5. Validation Metrics

### 5.1 Performance Metrics (mHM Calibration)

| Metric | Target Range | Interpretation | Source |
|--------|--------------|----------------|--------|
| **KGE** | 0.70-0.85 | Good (correlation + variability + bias) | Kling-Gupta 2009 |
| **NSE** | 0.60-0.80 | Good (variance explained) | Nash-Sutcliffe 1970 |
| **r** | 0.75-0.90 | Strong correlation | Pearson |
| **Bias** | -10% to +10% | Acceptable systematic deviation | — |
| **RMSE** | Context-dependent | Error magnitude (catchment-specific) | — |

**Busari et al. (2021) — mHM Multi-Year LULC:**
- **Multi-year LULC:** NSE 0.23-0.42 (calibration), 0.13-0.39 (validation)
- **LAI-based PET:** +20-30% improvement (vs. aspect-based)
- **Recommendation:** Use multi-year LULC + LAI-based PET for Harz scenarios

---

### 5.2 Drought Indices (for Harz 2018-2020 Analysis)

| Index | Component | Timescale | Interpretation |
|-------|-----------|-----------|----------------|
| **SPI** | Precipitation | 1, 3, 6, 12 months | Meteorological drought |
| **SPEI** | Precipitation + PET | 1, 3, 6, 12 months | Climatic drought |
| **SMI** | Soil Moisture | 1, 3, 6, 12 months | Agricultural drought |
| **SDI** | Streamflow | 1, 3, 6, 12 months | Hydrological drought |
| **MDI** | Composite (SM + Recharge + Q) | 1, 3, 6, 12 months | Integrated drought (Paper #1) |

**Drought Propagation (from MEMORY.md, Paper #1):**
- **P → SMI:** 4 weeks (1 month)
- **SMI → Recharge:** 12 weeks (3 months)
- **Recharge → Q:** 20 weeks (5 months)
- **Total:** ~9 months (36 weeks)

---

## 6. Analysis Workflow (8-Phase Approach)

### 6.1 Phase 1: Literature Review ✅ (COMPLETE)
- **Status:** 15 papers synthesized (forest_type_parameters.md)
- **Key findings:** Forest type parameters, LULC effect magnitudes

### 6.2 Phase 2: Scenario Design ✅ (THIS DOCUMENT)
- **Status:** Scenario matrix defined (S0-S8)
- **Key decisions:** Harz primary, multi-year LULC, LAI-based PET

### 6.3 Phase 3: Data Preparation ⏳ (NEXT)
- **Tasks:**
  - CORINE 2006/2012/2018 for Harz region
  - MODIS LAI (monthly, 2006-2020)
  - Meteorological forcing (DWD, 1991-2020)
  - Soil parameters (BGR, 100m resolution)

### 6.4 Phase 4: mHM Setup ⏳
- **Tasks:**
  - Create Harz catchment domain (mHM `catchments_cloud`)
  - Configure `vegetation.par` for S0-S3 scenarios
  - Setup multi-year LULC (CORINE 2006/2012/2018)
  - Enable LAI-based PET (MODIS monthly)

### 6.5 Phase 5: Calibration ⏳
- **Tasks:**
  - Calibrate mHM for S0 (baseline, 1991-2017)
  - Target: KGE 0.70-0.85, NSE 0.60-0.80
  - Multi-constraint: Streamflow + GLEAM + ESA CCI (Dembélé 2020)

### 6.6 Phase 6: Scenario Runs ⏳
- **Tasks:**
  - Run S1 (counterfactual, 2018-2020)
  - Run S2 (alternative, 2018-2020)
  - Run S3 (reality, 2018-2020)
  - Compare hydrological responses

### 6.7 Phase 7: Analysis ⏳
- **Tasks:**
  - ΔRunoff, ΔET, ΔPeak Flow, ΔBaseflow, ΔSoil Moisture
  - Drought indices (SPI, SPEI, SMI, SDI, MDI)
  - Drought propagation (P → SM → Q lags)

### 6.8 Phase 8: Visualization & Writing ⏳
- **Tasks:**
  - Timeseries plots (S0-S3 comparison)
  - Heatmaps (interannual variability)
  - Correlation matrices (compartment coupling)
  - Paper #2 writing (methods, results, discussion)

---

## 7. Harz Catchment Selection

### 7.1 Candidate Catchments (CAMELS-DE / mHM Domains)

| Catchment ID | Name | Area (km²) | Elevation (m) | Forest Cover | Gauge ID |
|--------------|------|------------|---------------|--------------|----------|
| **Harz_01** | Bode (Ermsleben) | ~300 | 200-500 | Mixed (beech + spruce) | 4024170 |
| **Harz_02** | Holtemme (Derenburg) | ~150 | 150-400 | Spruce-dominated | 4024175 |
| **Harz_03** | Ilse (Ilsenburg) | ~100 | 250-600 | Spruce (high elevation) | 4024180 |
| **Harz_04** | Selke (Meisdorf) | ~400 | 100-450 | Mixed (agriculture + forest) | 4024190 |

**Recommended:** **Harz_01 (Bode)** or **Harz_03 (Ilse)**
- **Bode:** Larger catchment, mixed forest (representative)
- **Ilse:** Smaller, spruce-dominated (high mortality 2018-2020)

---

### 7.2 mHM Domain Setup (Harz)

```bash
# Create Harz domain (example: Ilsenburg catchment)
cd /data/.openclaw/workspace/open_claw_vibe_coding/code/mhm
mkdir -p catchments_cloud/harz_ilse_0p0625
cd catchments_cloud/harz_ilse_0p0625

# Domain structure (from catchment_custom template)
mkdir -p input/{morph,meteo,lai,latlon,soil,vegetation}
mkdir -p runs/harz_ilse_0p0625/nml

# Copy CORINE LULC (2006, 2012, 2018)
cp /data/Corine/{2006,2012,2018}/harz_region.asc input/morph/

# Copy MODIS LAI (monthly, 2006-2020)
cp /data/MODIS/MOD15A2H/harz_monthly_*.asc input/lai/

# Configure mhm.nml (LAI-based PET, multi-year LULC)
# Edit: mhm_parameter.nml (vegetation.par for S0-S3 scenarios)
```

---

## 8. Extended Scenarios (Future Work)

### 8.1 Other Drought-Affected Regions

| Region | Drought Event | Forest Type | LULC Change | Status |
|--------|---------------|-------------|-------------|--------|
| **Erzgebirge** | 2018-2020 | Spruce monoculture | Similar to Harz | ⏳ Pending |
| **Sächsische Schweiz** | 2018-2020 | Mixed (beech + spruce) | Lower mortality | ⏳ Pending |
| **Schwarzwald** | 2018-2020 | Spruce + fir | Moderate mortality | ⏳ Pending |
| **Bayerischer Wald** | 2018-2020 | Spruce + beech | Bark beetle outbreak | ⏳ Pending |

### 8.2 Climate Change Scenarios (RCP Projections)

| Scenario | RCP | Time Period | Temperature Δ | Precipitation Δ | Source |
|----------|-----|-------------|---------------|-----------------|--------|
| **RCP 2.6** | Low emissions | 2040-2060 | +1.5°C | -5% to +5% | IPCC AR6 |
| **RCP 4.5** | Moderate | 2040-2060 | +2.0°C | -10% to 0% | IPCC AR6 |
| **RCP 8.5** | High | 2040-2060 | +3.0°C | -15% to -5% | IPCC AR6 |

**Compound LULC × Climate (S8):**
- **LULC:** Spruce → Mixed forest
- **Climate:** RCP 4.5 (2040-2060)
- **Interaction:** Non-additive (+10-30% effect)
- **Source:** Preetha & Hasan (2023), Dixit et al. (2022)

---

## 9. Next Steps (Immediate Actions)

### 9.1 Priority 1: Harz Catchment Setup
- [ ] Select Harz catchment (Bode vs. Ilse)
- [ ] Download CORINE 2006/2012/2018 for Harz region
- [ ] Download MODIS LAI (monthly, 2006-2020)
- [ ] Create mHM domain (catchments_cloud/harz_*)

### 9.2 Priority 2: mHM Parameter Files
- [ ] Create `vegetation.par` for S0-S3 scenarios
- [ ] Configure LAI-based PET (MODIS monthly)
- [ ] Setup multi-year LULC (CORINE 2006/2012/2018)

### 9.3 Priority 3: Calibration & Validation
- [ ] Calibrate mHM for S0 (baseline, 1991-2017)
- [ ] Validate with CAMELS-DE gauge data
- [ ] Multi-constraint: GLEAM + ESA CCI (Dembélé 2020)

### 9.4 Priority 4: Scenario Runs
- [ ] Run S1 (counterfactual, 2018-2020)
- [ ] Run S2 (alternative, 2018-2020)
- [ ] Run S3 (reality, 2018-2020)
- [ ] Compare hydrological responses

---

## 10. Key References (Scenario Design)

**Forest Type Parameters:**
- **Calder (1978)** — Spruce transpiration. DOI: `10.1016/0022-1694(78)90130-0`
- **Bosch & Hewlett (1982)** — Catchment experiments. DOI: `10.1016/0022-1694(82)90117-8`
- **Granier et al. (2000)** — Beech water balance. DOI: `10.1016/S0168-1923(99)00151-3`
- **Lagergren & Lindroth (2002)** — Pine vs. Spruce. DOI: `10.1016/S0168-1923(02)00060-6`

**LULC Impact Studies:**
- **Zhang et al. (2020)** — SWAT LULC. DOI: `10.1016/j.jhydrol.2020.124822`
- **Pijl & Tarolli (2022)** — Italian LULC + extremes. DOI: `10.1016/b978-0-323-90947-1.00009-0`
- **Dixit et al. (2022)** — WRF-Hydro LULC Kerala. DOI: `10.3354/cr01701`
- **Preetha & Hasan (2023)** — Coupled SWAT-FEM. DOI: `10.3390/land12050938`

**mHM-Specific:**
- **Busari et al. (2021)** — mHM Multi-Year LULC + LAI. DOI: `10.3390/w13111538`
- **Dembélé et al. (2020)** — Distributed model + satellite. DOI: `10.1029/2019WR026085`

**Drought Propagation:**
- **Vorobevskii et al. (2022)** — Wernersbach (Saxony). DOI: `10.1016/j.hydroa.2022.100122`

---

**Document Status:** Complete scenario matrix for Paper #2 LULC.  
**Next:** Harz catchment setup (Priority 1).
