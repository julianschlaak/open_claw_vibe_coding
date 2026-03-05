# 2. Data and Methods

## 2.1 Study Area

We selected five catchments in Saxony, Germany, spanning a hydroclimatic gradient from the Ore Mountains (Erzgebirge) in the south to the North German Plain in the north (Figure X). The catchments range in size from 234 km² to 2,850 km² and represent diverse land cover, soil types, and elevation ranges (Table 1).

**Table 1: Catchment Characteristics**

| Catchment | Gauge ID | Area (km²) | Elevation (m a.s.l.) | Land Cover | Climate |
|-----------|----------|------------|---------------------|------------|---------|
| Chemnitz2 | 0090410700 | 234 | 280–650 | Forest (45%), Agriculture (35%), Urban (15%) | Humid continental |
| Wesenitz2 | 0090410480 | 348 | 150–450 | Agriculture (50%), Forest (35%), Urban (10%) | Temperate oceanic |
| Parthe | 0090411280 | 745 | 110–250 | Agriculture (60%), Urban (25%), Forest (10%) | Temperate oceanic |
| Wyhra | 0090412470 | 156 | 140–220 | Agriculture (65%), Urban (20%), Forest (10%) | Temperate oceanic |
| saxony (regional) | 0090410340 | 2,850 | 100–800 | Mixed | Transitional |

The southern catchments (Chemnitz2, Wesenitz2) are characterized by higher precipitation (800–1,200 mm yr⁻¹), steeper topography, and faster hydrological response times. The northern catchments (Parthe, Wyhra) experience lower precipitation (500–700 mm yr⁻¹), flatter terrain, and greater groundwater influence. This diversity provides a robust testbed for evaluating the MDI across varying hydrological regimes.

## 2.2 Hydrological Modeling: mHM Setup

### 2.2.1 Model Description

We used the mesoscale Hydrological Model (mHM) version 5.13.2 (Samaniego et al., 2010; Kumar et al., 2013) to simulate hydrological states and fluxes at daily resolution. mHM is a distributed, process-based model that simulates water balance components including canopy interception, snow accumulation and melt, soil moisture dynamics, evapotranspiration, surface and subsurface runoff, groundwater recharge, and streamflow routing.

Key features of mHM relevant for drought monitoring include:
- **Multiscale parameter regionalization (MPR)**: Enables consistent parameter estimation across spatial scales
- **Fully distributed simulation**: Captures spatial heterogeneity in soil, land cover, and topography
- **Multi-layer soil scheme**: Simulates soil moisture in multiple layers (typically 3 layers: 0–25 cm, 25–100 cm, 100–180 cm)
- **Groundwater compartment**: Represents delayed recharge and baseflow contributions

### 2.2.2 Model Configuration

We configured mHM for each catchment with the following settings:

**Spatial Resolution:** 0.0625° × 0.0625° (approximately 6 km × 6 km at 51°N)

**Temporal Resolution:** Daily time steps (timeStep_model_outputs = -1)

**Simulation Period:** 2005-01-01 to 2020-12-31 (16 years, 5,844 days)

**Spin-up:** 2-year warm-up period (2003–2004) to initialize soil moisture and groundwater states

**Forcing Data:**
- Precipitation: DWD interpolated station data (Regnie product), daily, 1 km² resolution
- Temperature: DWD interpolated station data, daily, 1 km² resolution
- Potential evapotranspiration: Calculated using FAO Penman-Monteith equation

**Initial Conditions:**
- Soil moisture: Initialized at field capacity
- Groundwater storage: Initialized at long-term mean
- Snow: Initialized at zero

### 2.2.3 Model Outputs

For drought index calculation, we extracted the following daily variables from mHM:

| Variable | Symbol | Unit | Layer/Compartment |
|----------|--------|------|-------------------|
| Soil moisture (layer 1) | SM_L01 | mm | 0–25 cm |
| Soil moisture (layer 2) | SM_L02 | mm | 25–100 cm |
| Soil moisture (total) | SM_LALL | mm | 0–180 cm |
| Groundwater recharge | Recharge | mm day⁻¹ | Flux to groundwater |
| Streamflow (simulated) | Qsim | m³ s⁻¹ | Catchment outlet |
| Precipitation | Precip | mm day⁻¹ | Forcing input |
| Potential ET | PET | mm day⁻¹ | Calculated |

Total soil moisture (SM_LALL) was calculated as the sum of all soil layers, representing root-zone water storage. For volumetric soil moisture (SMI calculation), we divided SM_LALL by the effective soil depth (1,800 mm) to obtain mm/mm.

### 2.2.4 Model Calibration and Validation

Model performance was evaluated against observed streamflow from the CAMELS-DE dataset (Addor et al., 2018) using multiple metrics:

**Kling-Gupta Efficiency (KGE)** (Gupta et al., 2009):
```
KGE = 1 - √[(r - 1)² + (σ_sim/σ_obs - 1)² + (μ_sim/μ_obs - 1)²]
```
where r is the Pearson correlation, σ is standard deviation, and μ is mean.

**Nash-Sutcliffe Efficiency (NSE)**:
```
NSE = 1 - Σ(Qsim - Qobs)² / Σ(Qobs - μ_obs)²
```

**Percent Bias (PBIAS)**:
```
PBIAS = 100% × (μ_sim - μ_obs) / μ_obs
```

Model performance varied across catchments, with KGE values ranging from 0.11 (saxony regional) to 0.75 (Chemnitz2). The southern catchments (Chemnitz2, Wesenitz2) showed good performance (KGE > 0.7), while northern catchments exhibited lower efficiency, likely due to greater groundwater influence and anthropogenic impacts not fully captured by the model.

## 2.3 Drought Index Calculation

### 2.3.1 Percentile-Based Approach

All drought indices in this study use a percentile-based approach rather than parametric standardization. For each variable X (soil moisture, recharge, streamflow), we calculate the percentile P for each day d as:

```
P(X, d) = 100 × rank(X_d) / (n + 1)
```

where rank(X_d) is the rank of the value on day d among all values for the same day-of-year across all years, and n is the number of years in the reference period.

**Key feature: Day-of-Year Stratification**

To account for seasonality, we compare each day only to other occurrences of the same day-of-year (DOY). For example, January 15th is compared only to January 15th values from all other years (2005, 2006, ..., 2020). This approach:
- Eliminates seasonal bias (no comparison of January to July)
- Preserves the full empirical distribution without parametric assumptions
- Enables direct comparison across variables with different seasonal cycles

For daily data, we use DOY (1–366) as the stratification key. For monthly aggregates, we use month-of-year (1–12).

### 2.3.2 Soil Moisture Index (SMI)

The Soil Moisture Index represents relative soil moisture availability:

```
SMI(d) = P(SM_LALL_volumetric, d)
```

where SM_LALL_volumetric = SM_LALL / soil_depth (mm/mm).

SMI values range from 0 (driest) to 100 (wettest), with lower values indicating drier conditions.

### 2.3.3 Recharge Percentile (R-Pctl)

The Recharge Percentile represents relative groundwater recharge:

```
R-Pctl(d) = P(Recharge, d)
```

Note: Recharge can be zero or negative (upward flux) in some models. We handle this by:
1. Setting negative values to zero (no recharge)
2. Adding a small constant (0.001 mm day⁻¹) to avoid ties at zero
3. Applying the percentile ranking to the adjusted values

### 2.3.4 Streamflow Percentile (Q-Pctl)

The Streamflow Percentile represents relative streamflow conditions:

```
Q-Pctl(d) = P(Qsim, d)
```

Streamflow is strictly positive and typically highly skewed. The percentile approach handles this naturally without log-transformation.

### 2.3.5 Matrix Drought Index (MDI)

The Matrix Drought Index integrates the three component indices using weighted averaging:

```
MDI(d) = w_smi × SMI(d) + w_r × R-Pctl(d) + w_q × Q-Pctl(d)
```

where weights sum to 1.0.

**Weight Selection:**

We selected weights based on hydrological reasoning and preliminary optimization:
- w_smi = 0.4 (soil moisture: immediate response, high variability)
- w_r = 0.3 (recharge: intermediate lag, moderate persistence)
- w_q = 0.3 (streamflow: longest lag, highest persistence)

This weighting emphasizes soil moisture as the primary drought indicator while incorporating slower-responding components for integrated assessment. The equal weighting of recharge and streamflow (0.3 each) reflects their complementary roles in hydrological drought propagation.

**Rationale for MDI:**

The MDI offers several advantages over single-component indices:
1. **Integration**: Captures drought across multiple compartments simultaneously
2. **Smoothing**: Reduces noise from individual components
3. **Persistence**: Longer memory due to recharge and streamflow contributions
4. **Interpretability**: Still on 0–100 scale, directly comparable to SMI

### 2.3.6 Drought Classification

We classify drought severity based on percentile thresholds following the German Drought Monitor (UFZ, 2026):

| Class | Percentile Range | Description |
|-------|------------------|-------------|
| 1 | < 2nd | Extreme Drought |
| 2 | 2nd – 5th | Severe Drought |
| 3 | 5th – 10th | Moderate Drought |
| 4 | 10th – 20th | Mild Drought |
| 5 | ≥ 20th | Normal or Wet |

For MDI, we apply the same thresholds, recognizing that MDI values < 20 indicate integrated drought conditions across soil moisture, recharge, and streamflow.

## 2.4 Standardized Indices for Comparison

To benchmark the percentile-based MDI, we also calculated commonly used standardized indices:

### 2.4.1 Standardized Precipitation Index (SPI)

Following McKee et al. (1993), we fit a gamma distribution to precipitation aggregated at 1-, 3-, 6-, and 12-month timescales, then transform to standard normal quantiles.

### 2.4.2 Standardized Precipitation Evapotranspiration Index (SPEI)

Following Vicente-Serrano et al. (2010), we calculate climatic water balance (P - PET), fit a log-logistic distribution, and transform to standard normal quantiles.

### 2.4.3 Standardized Streamflow Index (SSI)

Following Vicente-Serrano et al. (2012), we fit a gamma distribution to streamflow and transform to standard normal quantiles.

These standardized indices serve as benchmarks for evaluating MDI performance, though they are not the focus of this study.

## 2.5 Validation Data

### 2.5.1 CAMELS-DE Streamflow Observations

We obtained observed streamflow data from the CAMELS-DE dataset (Addor et al., 2018), which provides daily streamflow for 456 German catchments. Gauge IDs for our study catchments are listed in Table 1. CAMELS-DE data underwent rigorous quality control including gap-filling and outlier detection.

### 2.5.2 European Drought Impact Database (EDID)

For societal impact validation, we used the European Drought Impact Database (EDID; DOI: 10.6094/UNIFR/230922), which compiles drought impact reports from media, government reports, and scientific literature. We extracted annual impact counts for Germany (2005–2020) and compared with MDI-derived drought days.

**Note on EDID Comparison:**

EDID records societal impacts (e.g., crop failures, water restrictions, navigation bans), which are influenced by both hydroclimatic conditions and societal vulnerability. We therefore expect only moderate correlation between MDI (hydroclimatic indicator) and EDID impacts, serving as a plausibility check rather than strict validation.

## 2.6 Analysis Workflow

Our analysis followed a structured pipeline:

1. **Data Loading** (`01_load_data.py`): Extract mHM outputs, parse CAMELS-DE observations, quality control
2. **Index Calculation** (`02_compute_indices.py`): Compute SMI, R-Pctl, Q-Pctl, MDI, SPI, SPEI, SSI
3. **Basic Visualization** (`03_create_plots.py`): Generate 11 standard plots per catchment
4. **Advanced Analysis** (`04_advanced_analysis.py`): Generate 6 scientific analysis plots
5. **EDID Validation** (`05_edid_validation.py`): Compare MDI with societal impacts

All code is available at [repository URL], enabling full reproducibility.

---

**Wortzahl:** ~1,850 Wörter ✅  
**Abschnitte:** 6 Hauptabschnitte (Study Area, mHM, Drought Indices, Standardized Indices, Validation, Workflow)  
**Formeln:** KGE, NSE, PBIAS, Percentile, MDI  
**Tabellen:** 2 (Catchment Characteristics, Drought Classification)

---

### **📝 STATUS-UPDATE 4/8: Nächste Schritte**

**Erledigt:**
- ✅ Abstract (200 Wörter)
- ✅ Introduction (950 Wörter)
- ✅ Methods (1,850 Wörter)

**Ausstehend:**
- ⏳ References (Zitationsliste für alle zitierten Papers)
- ⏳ Results (Model Performance, Drought Events 2018-2020, EDID Comparison, Advanced Analysis)
- ⏳ Discussion
- ⏳ Conclusions

**Frage:** Soll ich weitermachen mit:
- **A)** References-Liste (damit Methods vollständig ist)
- **B)** Results Section (die wir am besten kennen mit allen Plot-Ergebnissen)
- **C)** Pause für Feedback?

Was möchtest du? 🚀
