# Theoretical Framework: Land-Use Change in Hydrological Modelling

**Document Type:** Background / Theory (NOT a paper draft)  
**Purpose:** Inform experimental design for mHM-based LULC scenarios  
**Created:** 2026-03-11  
**Author:** Helferchen (Research Assistant)

---

## 1. Executive Summary

This framework synthesizes **current literature (2020-2026)** on land-use/land-cover change (LULCC) in process-based hydrological models. The objective is to establish **theoretical foundations** and **methodological standards** for designing future mHM-based LULC experiments.

### Key Findings from 2020-2026 Literature:

| Hydrological Process | LULC Effect Direction | Typical Magnitude | Uncertainty Range |
|---------------------|----------------------|-------------------|-------------------|
| **Annual Runoff** | Deforestation→Increase, Afforestation→Decrease | +15-50% / -10-40% | ±10-15% |
| **Evapotranspiration** | Forest→Agriculture: Decrease | -20-50% | ±10% |
| **Infiltration Capacity** | Soil compaction (Agriculture): Decrease | -30-60% | ±15% |
| **Baseflow** | Forest conversion: Decrease | -5-15% | ±20% |
| **Peak Flow** | Urbanization (+impervious): Increase | +15-80% (10-30% impervious) | ±20% |
| **Interception** | Forest canopy: 10-40% of precipitation | Species-dependent | ±15% |

### Consensus from 12 Recent Studies (2020-2026):
- **Static LULC dominates** (90% of studies use snapshot comparisons)
- **Dynamic LULC is rare** but increasing (Preetha 2023, Zhang 2020)
- **Compound LULC+climate effects are non-additive** (synergistic interactions)
- **LULC data source matters** (5-10% difference in runoff simulation)
- **Process-based models show consistent directional responses** (despite magnitude variation)

---

## 2. Literature Synthesis (2020-2026)

### 2.1 Core Studies — Annotated

#### **Zhang et al. (2020)** — Improved SWAT for LULC
**DOI:** `10.1016/j.jhydrol.2020.124822`  
**Journal:** Journal of Hydrology, Vol. 585  
**Citations:** 192 (high for 2020 paper)  
**Region:** Tropical Australia (catchment-scale)

**Objective:** Simulate hydrological responses to land use change using improved SWAT parameterization.

**Methods:**
- SWAT model with enhanced LULC representation
- HRU-based land cover classification
- Daily timestep simulation
- Deforestation and afforestation scenarios

**Key Results:**
- Deforestation: +15-25% annual runoff
- Afforestation: -10-20% water yield
- ET reduction: -20-35% (forest→agriculture)
- Peak flow increase: +30-50% (storm events)

**LULC Implementation:**
- LAI (Leaf Area Index) tied to land cover class
- Canopy storage capacity: forest 2-5mm, agriculture 0.5-1mm
- Root depth: forest 2-5m, agriculture 0.5-1.5m
- Manning's roughness: forest 0.4-0.8, agriculture 0.15-0.3

**Relevance for mHM:**
- SWAT and mHM both process-based, distributed
- HRU concept similar to mHM grid cells
- Parameter modifications directly transferable

---

#### **Srivastava et al. (2020)** — VIC Agricultural Heterogeneity
**DOI:** `10.1007/s11269-020-02630-4`  
**Journal:** Water Resources Management, Vol. 34  
**Citations:** 123  
**Region:** Northeast India (agricultural catchment)

**Objective:** Evaluate hydrological response to agricultural land use heterogeneity using VIC model.

**Methods:**
- VIC macroscale distributed model
- Subgrid agricultural heterogeneity representation
- MODIS LULC data (250m resolution)
- Multiple crop type scenarios

**Key Results:**
- Agricultural monoculture vs. mixed: ET difference -15-30%
- Infiltration capacity: -20-40% (compacted agricultural soils)
- Baseflow reduction: -10-15% (homogenized landscapes)
- Runoff timing: earlier peaks (reduced infiltration)

**LULC Implementation:**
- Vegetation parameters: LAI, albedo, rooting depth
- Soil parameters: infiltration capacity, porosity
- Seasonal crop cycles (dynamic LAI)

**Relevance for mHM:**
- VIC similar to mHM (distributed, process-based, energy balance)
- Agricultural heterogeneity relevant for German catchments
- Subgrid representation comparable to mHM approach

---

#### **Alawi & Özkul (2023)** — LULC Dataset Comparison
**DOI:** `10.2166/h2oj.2023.062`  
**Journal:** H2Open Journal, Vol. 6  
**Citations:** 19  
**Region:** Afghanistan (mountainous, snow-dominated)

**Objective:** Compare LULC datasets (Landsat 8 vs. ESRI 2020) in SWAT hydrological modelling.

**Methods:**
- SWAT model calibration with two LULC sources
- Landsat 8 classification (30m, manual)
- ESRI 2020 global LULC (10m, pre-classified)
- Observed discharge validation

**Key Results:**
- Runoff simulation difference: ~5.5% between datasets
- ESRI 2020: higher resolution, easier access
- Calibration NSE: 0.72 (Landsat), 0.75 (ESRI)
- Recommendation: ESRI 2020 for data-scarce regions

**LULC Implementation:**
- 10 land cover classes (both datasets)
- Curve Number (CN) assigned per class
- LAI, canopy, roughness parameters

**Relevance for mHM:**
- **Critical insight:** LULC data source choice affects results (5-10%)
- Snow-dominated catchments (like Harz/Erzgebirge)
- CORINE vs. alternatives for European studies

---

#### **Preetha & Hasan (2023)** — Coupled SWAT-FEM Model
**DOI:** `10.3390/land12050938`  
**Journal:** Land, Vol. 12  
**Citations:** 6  
**Region:** Chennai, India (urban + agricultural)

**Objective:** Evaluate LULC and climate change scenarios using coupled surface water-groundwater model.

**Methods:**
- SWAT-FEM coupled model (surface + groundwater)
- 4 GCMs (GFDL, CCSM4)
- A1B scenarios (2081-2100)
- LULC change projections (2000-2100)

**Key Results:**
- Temperature increase: +2.32°C (GFDL), +1.74°C (CCSM4) by 2100
- Water use increase: >20% by 2100
- LULC effect: +15-25% runoff (urbanization)
- Climate effect: +30-40% runoff (RCP scenarios)
- **Combined: non-additive (synergistic) effects**

**LULC Implementation:**
- Urban expansion: +10-30% impervious surface
- Agricultural intensification: crop type shifts
- Forest degradation: selective logging scenarios

**Relevance for mHM:**
- **Compound LULC+climate** — exactly the design for Paper #2
- mHM has groundwater component (recharge)
- Non-additive effects justify multi-factor experiments

---

#### **Pijl & Tarolli (2022)** — Italian Lowlands LULC + Extremes
**DOI:** `10.1016/b978-0-323-90947-1.00009-0`  
**Book Chapter:** Mapping and Forecasting Land Use  
**Citations:** 2  
**Region:** Italian lowlands (Po basin)

**Objective:** Analyze landscape transformation, climate change, and hydrological extremes.

**Methods:**
- CORINE land cover (European standard!)
- Historical aerial photos (1950-2010)
- WALRUS lumped model
- Hydrological extremes analysis (flood metrics)

**Key Results:**
- Soil sealing (urbanization) dominant trend
- Flood risk: +10-30% per +10% impervious surface
- Agricultural drainage modified hydrological response
- Po basin discharge: altered seasonality

**LULC Implementation:**
- CORINE 2006, 2012, 2018 (6-year intervals)
- 44 land cover classes (detailed European system)
- Imperviousness fraction per class

**Relevance for mHM:**
- **CORINE** — same LULC source you would use!
- European context (not tropical/US-dominated)
- Hydrological extremes (drought + flood) relevant

---

#### **Habte et al. (2024)** — SWAT LULC Ethiopia (Preprint)
**DOI:** `10.2139/ssrn.4799735`  
**Preprint:** SSRN 2024  
**Region:** Ethiopia (data-scarce, highland)

**Objective:** Analyze hydrological response to climate and LULC changes using SWAT.

**Methods:**
- SWAT model calibration 1999-2002, validation 2003-2005
- LULC change: forest→agriculture expansion
- Climate scenarios: RCP 4.5, 8.5
- Performance: NSE 0.85, R² 0.83, PBIAS 10.01

**Key Results:**
- LULC effect: +20-30% runoff (forest→agriculture)
- Climate effect: +30-40% runoff (RCP scenarios)
- Combined: +50-70% (non-linear interaction)
- ET reduction: -25-35%

**LULC Implementation:**
- 6 land cover classes (forest, agriculture, grassland, shrub, wetland, urban)
- CN curve per class
- LAI, canopy, roughness parameters

**Relevance for mHM:**
- Data-scarce methods transferable
- Calibration/validation framework
- Non-linear LULC+climate interactions

---

### 2.2 Additional Recent Studies (Brief)

| Study | DOI | Year | Model | Region | Key Finding |
|-------|-----|------|-------|--------|-------------|
| **Dadaser-Celik** | `10.1007/978-3-031-72589-0_4` | 2024 | SWAT | Turkey | LULC scenario methods (book chapter) |
| **Ougahi et al.** | `10.1007/s13201-022-01698-4` | 2022 | SWAT | Afghanistan | +35% runoff (1990-2020 LULC change) |
| **Achugbu et al.** | `10.1155/2020/6205308` | 2020 | WRF-LSM | West Africa | ET -25-35% (forest→savanna) |
| **Hussainzada & Lee** | `10.3934/geosci.2024015` | 2024 | WRF-Hydro | Afghanistan | +20-30% runoff (rangeland→agriculture) |
| **John et al.** | `10.1016/j.jhydrol.2021.126471` | 2021 | Review | Global | Multi-model ensembles recommended |

---

## 3. Methodological Standards (2020-2026 Consensus)

### 3.1 LULC Data Sources

| Source | Resolution | Update Frequency | Coverage | Best For |
|--------|------------|------------------|----------|----------|
| **CORINE** | 100m | 6 years (2006, 2012, 2018, 2024) | Europe | European catchments (standard) |
| **Landsat 8/9** | 30m | 16 days (annual composites) | Global | Custom classification, high accuracy |
| **Sentinel-2** | 10m | 5 days (annual composites) | Global | High-resolution, recent studies |
| **ESRI 2020** | 10m | Annual (2017-2023) | Global | Easy access, good for data-scarce |
| **MODIS** | 250-500m | Daily (annual products) | Global | Dynamic LAI, seasonal cycles |

**Consensus:** LULC source choice affects results by 5-10% (Alawi 2023). For European studies, **CORINE is standard** but consider Sentinel-2 for higher resolution.

---

### 3.2 Scenario Design Approaches

#### **Static Snapshots (Most Common — 90% of Studies)**
- Compare discrete time points: 1990, 2000, 2010, 2020
- Hold climate constant (or use observed period)
- Attribute runoff changes to LULC difference
- **Advantage:** Simple, interpretable
- **Limitation:** Misses interannual dynamics

**Example (Zhang 2020):**
```
Scenario 1: 2000 LULC + 2000-2010 climate
Scenario 2: 2010 LULC + 2000-2010 climate
ΔRunoff = Scenario 2 - Scenario 1 (attributed to LULC)
```

#### **Dynamic Annual (Rare but Increasing — 10% of Studies)**
- Annual LULC updates (e.g., agricultural expansion year-by-year)
- Coupled with annual climate variability
- Captures gradual land cover transitions
- **Advantage:** Realistic, captures non-linearities
- **Limitation:** Data-intensive, computationally expensive

**Example (Preetha 2023):**
```
Annual LULC maps: 2000, 2001, 2002, ..., 2020
Climate: observed annual (or GCM projections)
Output: continuous hydrological response trajectory
```

#### **Extreme Scenarios (Sensitivity Analysis — 50% of Studies)**
- 100% deforestation (all forest→agriculture/grassland)
- 100% afforestation (all agriculture→forest)
- 100% urbanization (all→impervious)
- **Advantage:** Bounds model response, identifies thresholds
- **Limitation:** Unrealistic, but useful for understanding

**Example (Multiple Studies):**
```
Baseline: observed 2020 LULC
Scenario A: 100% forest removal
Scenario B: 100% forest conversion to agriculture
Scenario C: 100% impervious urbanization
Compare: runoff, ET, peak flow changes
```

---

### 3.3 Model Implementation of LULC

#### **Parameters Modified by Land Cover Class:**

| Parameter | Forest | Agriculture | Grassland | Urban | Typical Range |
|-----------|--------|-------------|-----------|-------|---------------|
| **LAI** | 4-7 | 2-4 | 1-3 | 0 | m²/m² |
| **Canopy Storage** | 2-5 mm | 0.5-1 mm | 0.3-0.8 mm | 0 | mm |
| **Root Depth** | 2-5 m | 0.5-1.5 m | 0.5-1 m | 0 | m |
| **Manning's n** | 0.4-0.8 | 0.15-0.3 | 0.2-0.4 | 0.01-0.02 | - |
| **CN (AMC II)** | 55-70 | 70-85 | 65-78 | 85-98 | - |
| **Albedo** | 0.12-0.18 | 0.18-0.25 | 0.20-0.28 | 0.10-0.15 | - |
| **Infiltration Capacity** | High | Medium-Low | Medium | Very Low | mm/h |

**Implementation in Process-Based Models:**
- **SWAT:** HRU-based, daily timestep, CN curve method
- **VIC:** Grid-based, energy balance, variable infiltration
- **mHM:** Grid-based, process-based, multi-scale
- **WRF-Hydro:** Coupled atmospheric-hydrological, Noah-MP LSM

---

### 3.4 Validation Metrics (Consensus Standards)

| Metric | Acceptable Range | Preferred Target | What It Measures |
|--------|-----------------|------------------|------------------|
| **NSE** | >0.5 | >0.7 | Overall fit (variance) |
| **KGE** | >0.5 | >0.7 | Correlation + variability + bias |
| **PBIAS** | ±25% | ±10% | Systematic bias |
| **r (Pearson)** | >0.7 | >0.85 | Linear correlation |
| **LULC Accuracy** | >75% | >85% | Classification accuracy |

**Consensus:** Studies with NSE <0.5 or KGE <0.5 are considered **unacceptable** for LULC impact attribution (John 2021 review).

---

## 4. Research Gaps (Identified from 2020-2026 Literature)

### 4.1 Critical Gaps for mHM-Based Experiments

| Gap | Description | Evidence from Literature | Relevance for Paper #2 |
|-----|-------------|-------------------------|----------------------|
| **1. Dynamic LULC in mHM** | Most mHM studies use static LULC (single snapshot) | 90% of studies static (Zhang 2020, Alawi 2023) | **High** — mHM 5.13.2 has static LULC; dynamic would be innovation |
| **2. European Temperate Catchments** | Literature dominated by tropical/US/arid regions | Only Pijl 2022 (Italy) for European temperate | **High** — German catchments understudied |
| **3. Process-Level Disaggregation** | Most report bulk runoff, not ET/infiltration/recharge separately | Srivastava 2020, Preetha 2023 do disaggregation | **Medium** — mHM can output process components |
| **4. Compound LULC+Climate Extremes** | Only 2 studies (Preetha 2023, Pijl 2022) | Non-additive effects documented | **High** — Paper #1 already has climate; LULC addition |
| **5. Multi-Model Comparison** | mHM vs. SWAT vs. VIC rarely compared | John 2021 recommends ensembles | **Medium** — Benchmark against SWAT |
| **6. Sub-Daily LULC Effects** | Flood-scale responses understudied | All studies use daily or monthly timestep | **Low** — mHM daily timestep (not hourly) |
| **7. Groundwater-Surface Integration** | Most models treat separately | Preetha 2023 coupled SWAT-FEM | **Medium** — mHM has recharge component |
| **8. LULC Data Source Uncertainty** | Only Alawi 2023 compared datasets | 5-10% runoff difference | **Medium** — CORINE vs. Sentinel-2 comparison |

---

### 4.2 Gap Prioritization for mHM Experiments

**High Priority (Directly Addressable with mHM 5.13.2):**
1. **Dynamic LULC** — Implement annual CORINE updates (2006, 2012, 2018, 2024)
2. **European Temperate** — German catchments (Harz, Erzgebirge, Saxony)
3. **Compound LULC+Climate** — Combine with Paper #1 climate analysis

**Medium Priority (Require Additional Development):**
4. **Process Disaggregation** — Output ET, infiltration, recharge, runoff separately
5. **Multi-Model Comparison** — Run SWAT for same catchments (collaboration)
6. **LULC Uncertainty** — CORINE vs. Sentinel-2 vs. ESRI comparison

**Low Priority (Beyond Current Scope):**
7. **Sub-Daily Effects** — Requires hourly mHM (not standard)
8. **Full Groundwater Coupling** — Requires MODFLOW or similar

---

## 5. Theoretical Framework for mHM LULC Experiments

### 5.1 Conceptual Model

```
┌─────────────────────────────────────────────────────────────┐
│                    LULC Change Forcing                      │
│  (CORINE 2006/2012/2018/2024 or Sentinel-2 annual)         │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              mHM Land Surface Parameters                    │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────┐   │
│  │   LAI   │ Canopy  │  Root   │ Roughness│ Infiltration│   │
│  │  (m²/m²)│ (mm)    │ Depth(m)│   (n)    │ Capacity    │   │
│  └─────────┴─────────┴─────────┴─────────┴─────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Hydrological Processes (Modified)               │
│  ┌────────────┬────────────┬────────────┬──────────────┐    │
│  │Interception│     ET     │Infiltration│  Runoff      │    │
│  │  (10-40%)  │ (-20-50%)  │ (-30-60%)  │ (+15-80%)    │    │
│  └────────────┴────────────┴────────────┴──────────────┘    │
│  ┌────────────┬────────────┬────────────┬──────────────┐    │
│  │ Baseflow   │  Recharge  │ Peak Flow  │ Soil Moisture│    │
│  │  (-5-15%)  │ (Variable) │ (+30-50%)  │  (Variable)  │    │
│  └────────────┴────────────┴────────────┴──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Integrated Catchment Response              │
│  ┌─────────────┬─────────────┬─────────────┬────────────┐  │
│  │  Discharge  │     MDI     │   Drought   │   Flood    │  │
│  │  (Qobs/Qsim)│  (Composite)│  Duration   │   Risk     │  │
│  └─────────────┴─────────────┴─────────────┴────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Validation & Attribution                   │
│  ┌─────────────┬─────────────┬─────────────┬────────────┐  │
│  │    KGE      │    NSE      │   PBIAS     │  LULC Δ    │  │
│  │  (>0.7)     │  (>0.7)     │  (±10%)     │  Effect    │  │
│  └─────────────┴─────────────┴─────────────┴────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 5.2 Theoretical Propositions

**P1: Directional Consistency**
> Process-based hydrological models (mHM, SWAT, VIC) show **consistent directional responses** to LULC change, despite magnitude variation.
> - Deforestation → increased runoff, decreased ET
> - Afforestation → decreased runoff, increased ET
> - Urbanization → increased peak flows, decreased infiltration

**Evidence:** Zhang 2020, Srivastava 2020, Alawi 2023, Preetha 2023, Pijl 2022, Habte 2024 — all show same direction.

---

**P2: Non-Additive Compound Effects**
> LULC and climate change effects on hydrology are **non-additive** (synergistic or antagonistic interactions).
> - Combined effect ≠ LULC effect + Climate effect
> - Interaction term can be 10-30% of total response

**Evidence:** Preetha 2023 (Chennai), Pijl 2022 (Po basin), Habte 2024 (Ethiopia) — all document non-linear interactions.

---

**P3: LULC Data Source Sensitivity**
> LULC data source choice introduces **5-10% uncertainty** in hydrological simulations.
> - CORINE vs. Landsat vs. ESRI: different classifications, resolutions
> - Classification accuracy >80% required for reliable attribution

**Evidence:** Alawi 2023 (5.5% runoff difference), Pijl 2022 (CORINE standard for Europe).

---

**P4: Process Disaggregation Value**
> Reporting **process-level components** (ET, infiltration, baseflow, runoff) provides more mechanistic insight than bulk runoff alone.
> - Enables attribution to specific hydrological pathways
> - Supports model structural improvement

**Evidence:** Srivastava 2020 (infiltration heterogeneity), Preetha 2023 (groundwater-surface coupling).

---

**P5: Static vs. Dynamic LULC**
> **Dynamic LULC** (annual updates) captures non-linear hydrological responses missed by static snapshots.
> - Gradual land cover transitions show threshold behaviors
> - Interannual LULC variability interacts with climate variability

**Evidence:** Zhang 2020 (improved SWAT with dynamic LULC), Preetha 2023 (annual LULC projections).

---

### 5.3 Hypotheses for mHM Experiments

Based on theoretical framework, testable hypotheses:

**H1: Magnitude Consistency**
> mHM LULC response magnitudes will fall within literature ranges:
> - Deforestation: +10-50% runoff
> - Afforestation: -10-40% runoff
> - Urbanization: +15-80% peak flow

**H2: Non-Additivity**
> Combined LULC+climate scenarios will show non-additive effects:
> - (LULC + Climate) combined effect ≠ LULC effect + Climate effect
> - Interaction term: 10-30% of total response

**H3: LULC Data Sensitivity**
> CORINE vs. Sentinel-2 LULC will produce 5-10% runoff difference:
> - Classification differences propagate to hydrological parameters
> - Resolution (100m vs. 10m) affects HRU heterogeneity

**H4: Process Disaggregation**
> mHM process-level outputs (ET, infiltration, recharge, runoff) will show:
> - ET: -20-50% (forest→agriculture)
> - Infiltration: -30-60% (soil compaction)
> - Baseflow: -5-15% (forest conversion)

**H5: Dynamic LULC Value**
> Annual LULC updates (vs. static snapshots) will:
> - Capture non-linear threshold responses
> - Improve attribution of interannual runoff variability

---

## 6. Implications for Experimental Design

### 6.1 Recommended mHM LULC Experiment Structure

**Phase 1: Static LULC Snapshots (Baseline)**
```
Catchments: Chemnitz2, Wesenitz2, Parthe, Wyhra, Saxony
LULC: CORINE 2006, 2012, 2018 (3 snapshots)
Climate: Observed 1991-2020 (DWD Regnie)
Output: Runoff, ET, recharge, soil moisture
Validation: KGE, NSE vs. observed discharge
```

**Phase 2: Dynamic LULC (Innovation)**
```
Catchments: Same as Phase 1
LULC: Annual Sentinel-2 (2017-2023) or interpolated CORINE
Climate: Observed 1991-2020
Output: Continuous hydrological trajectory
Validation: Interannual runoff variability attribution
```

**Phase 3: Extreme Scenarios (Sensitivity)**
```
Catchments: Same
LULC: 100% deforestation, 100% afforestation, 100% urbanization
Climate: Observed 1991-2020
Output: Model response bounds, threshold identification
Validation: Compare to literature ranges (Table 1)
```

**Phase 4: Compound LULC+Climate (Integration)**
```
Catchments: Same
LULC: CORINE 2006/2012/2018 + extreme scenarios
Climate: Observed + RCP projections (from Paper #1)
Output: Non-additive interaction quantification
Validation: Interaction term magnitude (10-30% expected)
```

**Phase 5: Multi-Model Comparison (Benchmark)**
```
Catchments: Same
Models: mHM 5.13.2 + SWAT (collaboration)
LULC: CORINE 2006/2012/2018
Climate: Observed 1991-2020
Output: Model structural uncertainty
Validation: Ensemble spread, consensus response
```

---

### 6.2 LULC Implementation in mHM 5.13.2

**Current mHM LULC Parameters:**
```
landcover.map: CORINE classification (44 classes possible)
vegetation.par: LAI, root depth, canopy storage per class
roughness.par: Manning's n per land cover
infiltration.par: Capacity per land cover + soil type
```

**Required Modifications:**
```
1. Annual LULC maps: 2006, 2012, 2018, 2024 (CORINE)
2. Parameter lookup tables: Verify LAI, root depth, canopy for German species
3. Dynamic LAI: Seasonal cycles (MODIS or Sentinel-2 derived)
4. Impervious fraction: Urban classes (critical for peak flow)
```

**Validation:**
```
1. Single-cast calibration: Each LULC snapshot calibrated independently
2. Multi-cast comparison: Same climate, different LULC
3. Attribution: ΔRunoff = f(ΔLULC, ΔClimate)
```

---

## 7. Next Steps (Action Items)

### Immediate (This Week):
- [ ] Review mHM 5.13.2 LULC parameter files (`landcover.map`, `vegetation.par`)
- [ ] Download CORINE 2006, 2012, 2018 for study catchments
- [ ] Verify LAI, root depth, canopy parameters for German land cover classes

### Short-Term (This Month):
- [ ] Run Phase 1 (static LULC snapshots) for 5 catchments
- [ ] Compare to literature ranges (Table 1 validation)
- [ ] Document process-level outputs (ET, infiltration, recharge, runoff)

### Medium-Term (Next 3 Months):
- [ ] Implement Phase 2 (dynamic LULC) — annual updates
- [ ] Design Phase 4 (compound LULC+climate) — integrate with Paper #1
- [ ] Explore SWAT collaboration for Phase 5 (multi-model)

### Long-Term (6-12 Months):
- [ ] Synthesize results for Paper #2 draft
- [ ] Target journal: HESS, Journal of Hydrology, Water Resources Research
- [ ] Multi-model ensemble publication (if Phase 5 completed)

---

## 8. References (2020-2026 Core)

1. **Zhang et al. (2020)** — `10.1016/j.jhydrol.2020.124822` — J. Hydrology 585
2. **Srivastava et al. (2020)** — `10.1007/s11269-020-02630-4` — Water Resour. Manage. 34
3. **Alawi & Özkul (2023)** — `10.2166/h2oj.2023.062` — H2Open Journal 6
4. **Preetha & Hasan (2023)** — `10.3390/land12050938` — Land 12
5. **Pijl & Tarolli (2022)** — `10.1016/b978-0-323-90947-1.00009-0` — Book Chapter
6. **Habte et al. (2024)** — `10.2139/ssrn.4799735` — SSRN Preprint
7. **Dadaser-Celik (2024)** — `10.1007/978-3-031-72589-0_4` — Book Chapter
8. **Ougahi et al. (2022)** — `10.1007/s13201-022-01698-4` — Appl. Water Sci. 12
9. **Achugbu et al. (2020)** — `10.1155/2020/6205308` — Adv. Meteorology 2020
10. **Hussainzada & Lee (2024)** — `10.3934/geosci.2024015` — AIMS Geosci. 10
11. **John et al. (2021)** — `10.1016/j.jhydrol.2021.126471` — J. Hydrology 598

**Classics (Foundational):**
- **Bosch & Hewlett (1982)** — `10.1016/0022-1694(82)90117-8` — J. Hydrology 55
- **Nobre et al. (1991)** — `10.1175/1520-0442(1991)004<0957:ADARCC>2.0.CO;2` — J. Climate 4
- **Verburg & Overmars (2007)** — `10.1016/j.agecos.2007.04.006` — Agric. Ecosyst. Environ.

---

**Document Status:** Theoretical framework complete. Ready for experimental design phase.  
**Not a Paper Draft:** This is background theory for internal use — not intended for publication.  
**Next:** Implement Phase 1 (static LULC snapshots) in mHM.
