# Paper #2 Methods — mHM Implementierungslogik

**Status:** Methods-Kapitel Entwurf (für Implementierungs-Planung)  
**Datum:** 2026-03-13  
**Wortzahl:** ~2,500 (5-6 Seiten)

---

## 3. Methods

### 3.1 Study area and catchment selection

We focus on the Free State of Saxony, Germany, as our regional study domain. Saxony provides an ideal setting for examining LULC effects because it exhibits (1) substantial LULC change over the 1991–2020 period, (2) diverse catchment characteristics (forest cover, agricultural intensity, urbanization, elevation), and (3) high-quality discharge observations through the CAMELS-DE dataset (Kratzert et al., 2023). Renner et al. (2024) previously analyzed 71 Saxon catchments for LULC attribution, providing a methodological precedent for our study.

For this study, we select 3–5 pilot catchments in Phase 1, expanding to 5–20 catchments in Phase 2. Catchment selection criteria prioritize contrast in key characteristics rather than spatial exhaustiveness:

| Criterion | Requirement | Rationale |
|-----------|-------------|-----------|
| **Forest cover** | Contrast: 0–30% (low), 30–60% (medium), 60–90% (high) | Test H3 (forest vs. open-land effects) |
| **Agriculture** | Contrast: cropland-dominant vs. grassland-dominant | Test RQ3 (Acker↔Grünland transitions) |
| **Relief** | Lowland vs. highland (Ore Mountains) | Test H4 (context-dependence) |
| **Discharge data** | CAMELS-DE available (quality-checked) | Mandatory for Q evaluation |
| **Size** | 50–500 km² (mesoscale, mHM-appropriate) | Feasibility, not too large |

Table 1 summarizes catchment characteristics (to be completed after selection).

---

### 3.2 Land use and land cover data

We use CORINE Land Cover (CLC) data as the primary LULC input for mHM. CORINE provides consistent land cover classification across Europe at 6-year intervals: 1991, 2000, 2006, 2012, 2018, and 2024 (EEA, 2024). This temporal resolution captures multi-decadal LULC trends while maintaining classification consistency.

**Data harmonization:**
To ensure consistency across the 1991–2024 period, we apply the following harmonization rules:
1. **Classification consistency:** CORINE nomenclature version 2018 used as reference; earlier versions mapped to 2018 classes where definitions changed.
2. **Spatial resolution:** All CLC rasters resampled to 1 km × 1 km resolution (matching mHM default grid).
3. **Projection:** UTM Zone 33N (ETRS89) enforced for all datasets.
4. **Mapping to mHM classes:** CORINE Level-3 classes aggregated to 4 mHM LULC classes:
   - **Forest:** All forest types (coniferous, deciduous, mixed)
   - **Grassland:** Pastures, natural grasslands, sparsely vegetated areas
   - **Cropland:** Arable land, permanent crops, heterogeneous agricultural areas
   - **Urban:** Urban fabric, industrial/commercial, artificial surfaces

**LAI seasonal variation:**
We derive seasonal Leaf Area Index (LAI) from MODIS MOD15A2H (500m, 8-day) climatology (2000–2020). For 1991–1999 (pre-MODIS), we use the 2000–2020 climatology as a stationary approximation. LAI is aggregated to 4 LULC classes with 3-month seasonal resolution (DJF, MAM, JJA, SON).

**Critical data risk:**
CORINE classification changes between versions may introduce artificial jumps not reflecting real LULC change. We implement quality control through visual inspection and smoothing rules, flagging catchments with suspicious LULC trends for review.

---

### 3.3 Model configurations (M0–M3)

We design four model configurations to isolate input effects from process effects:

| ID | Name | LULC | Interception | Purpose |
|----|------|------|--------------|---------|
| **M0** | Static Reference | Static (single year, e.g., 2018) | Standard mHM | Reference (current practice) |
| **M1** | Dynamic LULC | Dynamic (CORINE 1991, 2000, 2006, 2012, 2018) | Standard mHM | **Input effect** (LULC extent only) |
| **M2** | Dynamic + Interception | Dynamic (same as M1) | **LULC-sensitive interception** | **Process effect** (interception addition) |
| **M3** | Scenarios | Idealized transitions | Same as M2 | Scenario sensitivity |

**Scientific logic:**
- **M1 – M0** = Effect of time-varying LULC (input effect)
- **M2 – M1** = Additional effect of explicit improved interception representation (process effect)
- **M2 – M0** = Combined effect (extent + process)

This design allows us to test whether process representation adds value beyond simply updating LULC inputs—a critical distinction for model development priorities.

---

### 3.4 LULC-sensitive interception scheme

#### 3.4.1 Conceptual basis

The interception scheme extends mHM's existing interception routine by introducing LULC-dependent maximum storage capacity (S_max) and seasonal LAI variation. The conceptual model follows the Rutter-type approach (Rutter et al., 1971; Gash, 1979), adapted for computational efficiency in distributed modeling.

**Key equations:**
```
For each grid cell and timestep:

1. Interception storage update:
   S_int(t) = min(S_max[LULC], S_int(t-1) + P(t) - E_int(t))

2. Interception evaporation:
   E_int(t) = f(LAI_seasonal[LULC], PET(t), S_int(t))
      = (LAI_fraction × PET(t)) × (S_int(t) / S_max[LULC])

3. Throughfall:
   P_through(t) = P(t) - (S_int(t) - S_int(t-1)) - E_int(t)
```

Where:
- S_int = interception storage (mm)
- S_max = maximum storage capacity (LULC-dependent, mm)
- P = precipitation (mm/timestep)
- E_int = interception evaporation (mm/timestep)
- PET = potential evapotranspiration (mm/timestep)
- LAI_fraction = LAI-dependent evaporation efficiency (dimensionless)

#### 3.4.2 Parameter specification

**S_max (maximum storage capacity):**

| LULC class | S_max (mm) | Literature source |
|------------|------------|-------------------|
| **Forest** | 2.0–4.0 | Gash & Morton (1978), Klaassen et al. (1998) |
| **Grassland** | 0.5–1.0 | Literature range |
| **Cropland** | 0.3–0.8 | Literature range |
| **Urban** | 0.1–0.3 | Impervious surface approximation |

**LAI_seasonal (seasonal LAI):**

| LULC class | DJF (winter) | MAM (spring) | JJA (summer) | SON (autumn) |
|------------|--------------|--------------|--------------|--------------|
| **Forest** | 1–3 | 3–5 | 4–6 | 2–4 |
| **Grassland** | 0.5–1.5 | 1–3 | 2–4 | 1–2 |
| **Cropland** | 0.2–0.5 | 1–3 | 3–5 | 0.5–1.5 |
| **Urban** | 0.1–0.5 | 0.1–0.5 | 0.1–0.5 | 0.1–0.5 |

**Implementation notes:**
- S_max values are fixed per LULC class (no calibration)
- LAI_seasonal values derived from MODIS climatology (observation-based)
- Interception evaporation uses existing mHM PET routine (no new energy balance)
- Mass balance enforced: P = Throughfall + Interception_storage_change + Interception_evaporation

#### 3.4.3 mHM code modifications

**Files to modify:**
1. `mhm_parameter.nml` — Add LULC-dependent S_max lookup table
2. `mhm.nml` — Add flag for LULC-sensitive interception toggle
3. `src/interception.f90` (or equivalent) — Modify interception routine to accept S_max[LULC] and LAI_seasonal

**Minimal code change strategy:**
We prioritize minimal invasive changes to mHM source code:
- New namelist entries for S_max per LULC class (4 values)
- New namelist entries for LAI_seasonal per LULC class (4 × 4 = 16 values)
- Interception routine modified to read LULC-dependent parameters
- No changes to energy balance, snow, or root water uptake routines

This strategy reduces implementation risk and maintains compatibility with standard mHM versions.

---

### 3.5 Calibration and evaluation design

#### 3.5.1 Calibration strategy

We calibrate only the M0 configuration using the Differential Dynamic Search (DDS) algorithm (Tolson & Shoemaker, 2007) with Kling-Gupta Efficiency (KGE) as the objective function. M1, M2, and M3 use the same calibrated parameters as M0, differing only in LULC input and interception scheme.

**Rationale:**
Calibrating all configurations separately would introduce confounding effects, making it impossible to attribute differences to LULC or interception changes. By using M0 parameters for all runs, we ensure that performance differences reflect LULC/interception effects rather than parameter equifinality.

**Calibration period:** 1991–2010 (20 years)  
**Validation period:** 2011–2020 (10 years)

#### 3.5.2 Evaluation metrics

We employ multi-variable evaluation to capture effects across the hydrological cycle:

| Variable | Metrics | Data source |
|----------|---------|-------------|
| **Discharge (Q)** | KGE, NSE, logNSE, Bias, high-flow KGE, low-flow KGE | CAMELS-DE observations |
| **Evapotranspiration (ET)** | KGE, RMSE, Bias, seasonal correlation | mHM output (no direct observations) |
| **Soil moisture (SM)** | KGE, RMSE, anomaly correlation | ESA CCI (25km, coarse) or mHM output intercomparison |

**Multi-variable consistency score:**
```
MV_score = (KGE_Q + KGE_ET + KGE_SM) / 3
```

This score prioritizes simultaneous performance across variables rather than optimizing discharge alone—a key lesson from Koycegiz et al. (2024), who found dynamic LULC improved groundwater anomalies even when discharge remained similar.

#### 3.5.3 Comparison design

**Primary comparisons:**
1. **M1 vs. M0:** Tests effect of dynamic LULC extent alone
2. **M2 vs. M1:** Tests effect of LULC-sensitive interception (process effect)
3. **M2 vs. M0:** Tests combined effect (extent + process)

**Secondary comparisons:**
4. **M3 scenarios:** Tests sensitivity to specific LULC transitions (afforestation, deforestation, Acker↔Grünland)
5. **Catchment grouping:** Tests H4 (context-dependence by elevation, forest cover, aridity)

---

### 3.6 Scenario experiments (M3)

M3 configurations test idealized LULC transitions to assess hydrological sensitivity to specific change types:

| Scenario | Transition | Expected effect (based on Bosch & Hewlett, 1982) |
|----------|------------|--------------------------------------------------|
| **S1** | Forest → Grassland (deforestation) | ET↓, Q↑ (~40mm/10% for conifer) |
| **S2** | Grassland → Forest (afforestation) | ET↑, Q↓ (~40mm/10% for conifer) |
| **S3** | Cropland → Grassland | ET↑ (modest), Q↓ (modest) |
| **S4** | Grassland → Cropland | ET↓ (modest), Q↑ (modest) |
| **S5** | Natural → Urban (impervious) | ET↓, Q↑↑ (rapid runoff) |

**Implementation:**
Scenarios applied to 2018 LULC baseline, with transition magnitude scaled to 10%, 20%, 30% cover change. This allows testing of linearity in hydrological response and comparison to Bosch & Hewlett (1982) benchmarks.

---

### 3.7 Limitations and assumptions

**Key assumptions:**
1. **S_max stationarity:** S_max values constant per LULC class (no age/structure dynamics)
2. **LAI climatology:** LAI derived from 2000–2020 climatology (stationary for 1991–1999)
3. **No feedback:** LULC affects hydrology, but hydrology does not affect LULC (one-way coupling)
4. **4-class aggregation:** CORINE Level-3 aggregated to 4 classes (loss of within-class variability)

**Limitations:**
1. **CORINE temporal resolution:** 6-year snapshots (not annual) — interpolation between snapshots introduces uncertainty
2. **ET/SM observations:** Limited direct observations for ET and SM validation in Saxony
3. **Equifinality:** Multiple S_max combinations may produce similar Q/ET — addressed via multi-variable constraint
4. **Scale mismatch:** CORINE (100m) vs. mHM (1km) vs. forcing (varies) — resampling may smooth local variability

---

## References (Methods)

EEA, 2024. CORINE Land Cover. European Environment Agency.

Gash, J.H.C., 1979. An analytical model of rainfall interception by forests. *Journal of Hydrology*, 40(1-2), pp.45-55.

Gash, J.H.C., and Morton, C.J., 1978. An application of the Rutter model to the estimation of the interception loss from Thetford Forest. *Journal of Hydrology*, 38(1-2), pp.49-58.

Klaassen, W., Bosveld, F., and de Water, E., 1998. Water storage and evaporation as constituents of rainfall interception. *Journal of Hydrology*, 212, pp.36-50.

Koycegiz, C., et al., 2024. [Title and details]. *Journal*.

Kratzert, F., et al., 2023. CAMELS-DE: Catchment attributes and MEasurements for Large-scale catchments—DE (Germany). *Hydrology and Earth System Sciences*, 27, pp.1293-1305.

Renner, M., et al., 2024. [Title and details]. *Journal*.

Rutter, A.J., et al., 1971. A predictive model of rainfall interception in forests, 1. Derivation of the model from observations in a plantation of Corsican pine. *Journal of Hydrology*, 14(3), pp.3-28.

Tolson, B.A., and Shoemaker, C.A., 2007. Dynamically dimensioned search algorithm for computationally efficient watershed model calibration. *Water Resources Research*, 43(1).

---

**Next:** Results (Section 4) — after experiments complete

**Word Count:** ~2,500 (5-6 pages)
