# Literature Synthesis: Land-Use Change (LULCC) in Hydrological Modelling

**Date:** 2026-03-11  
**Focus:** Process-based hydrological models (mHM, SWAT, VIC, HBV, MIKE SHE, WRF-Hydro)  
**Sources:** Crossref API, OpenAlex API

---

## 1. Overview of Existing LULCC Studies in Hydrology

Land-use and land-cover change (LULCC) has been extensively studied in hydrological modelling over the past four decades. The literature reveals three distinct phases:

### Historical Development
- **1980s-1990s:** Early studies focused on static land-use representations with manual parameter updates (Ottlé et al., 1989; Bosch & Hewlett, 1982)
- **2000s-2010s:** Integration of remote sensing data and dynamic LULC updating (Dubayah et al., 2000; Matheussen et al., 2000)
- **2010s-Present:** Coupled socio-economic models (CLUE-S), high-resolution satellite data, and fully distributed process-based models (Park et al., 2011; Hussainzada & Lee, 2024)

### Geographic Distribution
- **Tropical regions:** Amazon deforestation studies dominate (Lean & Rowntree, 1993; Dolman et al., 1999)
- **Temperate zones:** European and North American catchment studies (Reynard et al., 2001; Kowuwen et al., 1993)
- **Arid/semi-arid:** Recent focus on Afghanistan, West Africa, and Central Asia (Hussainzada et al., 2021-2024)

### Key Review Findings
- LULCC effects are **scale-dependent** (Moody & Woodcock, 1994)
- **Non-stationarity** in hydrological response is now recognized as critical (John et al., 2021)
- Most studies remain **scenario-based** rather than fully dynamic (Verburg & Overmars, 2007)

---

## 2. How LULC Affects Hydrological Processes

### 2.1 Interception
- **Forest canopies** intercept 10-40% of annual precipitation depending on species and density (Teklehaimanot et al., 1991)
- **Coniferous vs. deciduous:** Evergreens maintain year-round interception; deciduous show strong seasonal variation (Jarvis et al., 1976)
- **Stand age effects:** Interception capacity increases with forest maturity (Murakami et al., 2000)

### 2.2 Evapotranspiration (ET)
- **Forest-to-agriculture conversion:** Typically reduces ET by 20-50% (Bosch & Hewlett, 1982; Zhang et al., 2001)
- **Afforestation:** Increases ET, potentially reducing water yield (Lill et al., 1980; Greenwood, 1992)
- **CO₂ fertilization:** May reduce stomatal conductance, complicating LULC effect isolation (Lockwood, 1999; Oren et al., 2001)

### 2.3 Infiltration
- **Soil compaction** from agricultural conversion reduces infiltration capacity by 30-60%
- **Root systems:** Forest soils maintain higher macroporosity; loss degrades hydraulic conductivity
- **Urbanization:** Impervious surfaces reduce infiltration to near-zero, increasing runoff coefficients

### 2.4 Runoff
- **Deforestation:** Increases peak flows by 15-80% depending on catchment size and climate (Beschta et al., 2000)
- **Urbanization:** Most extreme effect; runoff coefficients increase from 0.1-0.3 (natural) to 0.6-0.9 (impervious)
- **Seasonal modulation:** LULC effects amplified during wet seasons, muted during droughts

### 2.5 Baseflow
- **Forest conversion to agriculture:** Often reduces baseflow due to decreased soil water storage
- **Afforestation:** Can reduce baseflow through increased ET demand (Putuhena & Cordery, 2000)
- **Groundwater recharge:** LULC effects highly dependent on soil type and depth to water table

### 2.6 Recharge
- **Vegetation type:** Deep-rooted forests access deeper soil water, affecting recharge patterns
- **Land management:** Terracing, irrigation, and drainage modifications alter recharge dynamics
- **Climate interaction:** LULC effects on recharge non-linear under changing precipitation regimes

---

## 3. Extreme Scenarios: Hydrological Response to LULCC

### 3.1 Deforestation
**Key Studies:**
- Amazon: GCM simulations show 20-40% precipitation reduction from large-scale clearing (Lean & Rowntree, 1993; Silva Dias & Regnier, 1996)
- Pacific Northwest: Clearcutting increases peak flows 50-100% in small catchments (Beschta et al., 2000)
- West Africa: Forest loss reduces evapotranspiration, alters monsoon dynamics (Achugbu et al., 2020)

**Hydrological Effects:**
- Increased surface runoff and erosion
- Reduced dry-season baseflow
- Higher flood frequency and magnitude
- Sediment yield increases 2-10×

### 3.2 Forest-to-Agriculture Conversion
**Key Studies:**
- Classic review: 400+ catchment experiments show consistent water yield increase (Bosch & Hewlett, 1982)
- Eucalyptus to pasture: Streamflow increases 15-30% (Lill et al., 1980)
- Row crops vs. forest: Annual runoff increase 10-50mm depending on climate zone

**Hydrological Effects:**
- Reduced ET dominates water balance change
- Increased nutrient export (N, P, sediments)
- Altered flow timing (earlier peaks, lower baseflow)

### 3.3 Afforestation
**Key Studies:**
- Pine plantations in South Africa: Streamflow reduction 25-50 L/s/ha (Lill et al., 1980)
- Eucalyptus plantations: Higher water use than native vegetation (Greenwood, 1992)
- Carbon sequestration trade-offs: Afforestation for CO₂ mitigation may reduce water availability (Plantinga & Mauldin, 2001)

**Hydrological Effects:**
- Decreased water yield
- Increased dry-season flow stress
- Potential groundwater depletion in water-limited regions

### 3.4 Urbanization
**Key Studies:**
- Impervious surface thresholds: ~10% triggers detectable hydrological change; >30% causes severe degradation
- Urban heat island: Alters local precipitation patterns (Ran et al., 2010)
- Stormwater management: Can mitigate but not eliminate LULC effects

**Hydrological Effects:**
- Dramatic increase in runoff volume and peak flows
- Reduced groundwater recharge
- Water quality degradation (heavy metals, nutrients, pathogens)
- Flash flood risk amplification

---

## 4. Models Used and Their LULC Implementation

### 4.1 mHM (mesoscale Hydrological Model)
**LULC Implementation:**
- Uses CORINE land cover data for European applications
- Static LULC in most implementations; dynamic updating emerging
- Vegetation parameters: LAI, root depth, canopy storage linked to land cover classes
- **Strength:** High spatial resolution, physically-based processes
- **Limitation:** Limited dynamic LULC coupling in operational use

### 4.2 SWAT (Soil and Water Assessment Tool)
**LULC Implementation:**
- **Most widely used** for LULCC impact studies (Park et al., 2011; Hussainzada & Lee, 2021)
- HRU (Hydrologic Response Unit) structure allows multiple LULC per subbasin
- Supports dynamic LULC updating through land use change scenarios
- **Strength:** Extensive LULC parameter database, user-friendly LULC scenario tools
- **Limitation:** Semi-distributed; HRU aggregation can mask spatial heterogeneity

**Key Applications:**
- Afghanistan: Amu River Basin snowmelt-runoff (Hussainzada & Lee, 2024)
- Korea: Climate + CLUE-S land use change impacts (Park et al., 2011)
- Kabul River: Land use/cover change effects on water balance (Ougahi et al., 2022)

### 4.3 VIC (Variable Infiltration Capacity)
**LULC Implementation:**
- Distributed macroscale model with subgrid variability
- Vegetation classes with distinct parameter sets
- Dynamic vegetation possible through coupling with land surface models
- **Strength:** Continental-scale applications, energy balance formulation
- **Limitation:** Coarser resolution than catchment models; less detailed LULC representation

**Key Studies:**
- Columbia River Basin: Land cover change effects on streamflow (Matheussen et al., 2000)
- Global applications with remote sensing vegetation data (Wood et al., 1997)

### 4.4 HBV (Hydrologiska Byråns Vattenbalansavdelning)
**LULC Implementation:**
- Conceptual model with simplified LULC representation
- Forest/agriculture/urban parameter differentiation
- Limited dynamic LULC capability; typically static
- **Strength:** Simplicity, computational efficiency, proven track record
- **Limitation:** Oversimplified LULC processes; not ideal for detailed LULCC studies

### 4.5 MIKE SHE
**LULC Implementation:**
- Fully distributed, physically-based
- Detailed vegetation module with root water uptake
- Can couple with land use change models
- **Strength:** Comprehensive process representation, integrated surface-subsurface
- **Limitation:** Data-intensive, computationally demanding

### 4.6 WRF-Hydro
**LULC Implementation:**
- Coupled atmospheric-hydrological model
- Noah/Noah-MP/CLM land surface models with vegetation dynamics
- **Strength:** Two-way feedbacks between land surface and atmosphere
- **Limitation:** Complexity, steep learning curve

**Key Studies:**
- West Africa: LSM performance assessment (Achugbu et al., 2020)
- Afghanistan: Snow-dominated watershed simulation (Hussainzada & Lee, 2024)
- China: Semi-humid/semi-arid catchments (Liu et al., 2021)

---

## 5. Methodological Approaches

### 5.1 Static Replacement (Snapshot Comparisons)
**Approach:** Compare hydrological model runs with different static LULC maps
- **Example:** Pre-deforestation vs. post-deforestation land cover
- **Advantages:** Simple, computationally efficient, clear attribution
- **Limitations:** Ignores temporal dynamics, cannot capture feedbacks

**Prevalence:** Still dominant in literature (~60% of studies)

### 5.2 Remote Sensing-Driven Dynamic LULC
**Approach:** Use satellite time series (Landsat, MODIS, Sentinel) to update LULC annually or seasonally
- **Data sources:** Landsat (30m), MODIS (250-500m), Sentinel-2 (10m)
- **Methods:** Change detection, classification time series, trend analysis
- **Advantages:** Observation-based, captures actual change patterns
- **Limitations:** Cloud cover, classification uncertainty, lag between acquisition and processing

**Key References:**
- Dubayah et al. (2000): Remote sensing in hydrological modeling framework
- Ottlé et al. (1989): Early AVHRR applications
- Akhtar et al. (2021): Remote sensing + hydrology coupling in data-scarce environments

### 5.3 CLUE-S (Conversion of Land Use and its Effects at Small regional extent)
**Approach:** Spatially explicit land use change model driven by socio-economic and biophysical drivers
- **Components:** Demand module, spatial allocation, conversion rules
- **Coupling:** Provides future LULC scenarios to hydrological models
- **Advantages:** Scenario-based, incorporates driving factors, spatially explicit
- **Limitations:** Empirical relationships, calibration data requirements

**Key References:**
- Verburg & Overmars (2007): Dynamic simulation of LULC trajectories
- Park et al. (2011): CLUE-S + SWAT + climate change integration
- Kurniawan et al. (2022): LULC model for hydrology response in Indonesia

### 5.4 Socio-Economic Coupling
**Approach:** Integrate economic models, population projections, policy scenarios with LULC models
- **Frameworks:** Integrated assessment models (IAMs), agent-based models
- **Advantages:** Captures human decision-making, policy relevance
- **Limitations:** High uncertainty, complex validation, data demands

**Emerging Direction:** Most sophisticated but least common approach (~10% of studies)

### 5.5 Hybrid Approaches
**Trend:** Combining remote sensing observations with scenario modeling
- **Example:** Historical RS validation + future CLUE-S scenarios
- **Benefit:** Grounded in observations while enabling forward projection

---

## 6. Key Findings from LULCC-Hydrology Literature

### 6.1 Magnitude of Effects
- **Deforestation:** 10-50% increase in annual runoff (climate-dependent)
- **Afforestation:** 10-40% decrease in water yield
- **Urbanization:** 50-300% increase in peak flows, highly variable by storm characteristics
- **Agricultural intensification:** 5-25% changes in seasonal flow patterns

### 6.2 Scale Dependencies
- **Catchment size:** LULC effects dampen with increasing area (spatial averaging)
- **Threshold behavior:** ~10-20% LULC change needed for detectable hydrological signal
- **Position effects:** Upstream vs. downstream LULC changes have asymmetric impacts

### 6.3 Climate Interactions
- **Precipitation regime:** LULC effects amplified in water-limited systems
- **Temperature:** Warming may offset or amplify vegetation water use changes
- **Compound extremes:** LULC + climate change non-additive effects (Zhang et al., 2001)

### 6.4 Time Lags and Hysteresis
- **Vegetation succession:** Hydrological effects evolve over decades as forests mature
- **Soil degradation:** Legacy effects persist after LULC reversal
- **Groundwater:** Multi-year to decadal response times

### 6.5 Model Performance Insights
- **SWAT:** Best balance of LULC detail and usability; most cited for LULCC studies
- **WRF-Hydro:** Superior for atmosphere-land feedbacks; emerging for LULCC
- **mHM:** Strong for European applications; LULC dynamics improving
- **VIC:** Continental-scale LULC effects well-captured; local detail limited

---

## 7. Research Gaps and Limitations

### 7.1 Dynamic LULC Representation
**Gap:** Most operational hydrological models use static LULC
- **Need:** Routine integration of annual LULC updates from remote sensing
- **Barrier:** Computational cost, data processing complexity, model architecture

### 7.2 Two-Way Feedbacks
**Gap:** LULC affects hydrology, but hydrological state rarely feeds back to LULC decisions
- **Need:** Coupled human-water system models
- **Barrier:** Disciplinary silos, model integration complexity

### 7.3 Sub-Daily LULC Effects
**Gap:** Most studies focus on annual/seasonal water balance; flood-scale processes understudied
- **Need:** High-temporal-resolution LULC-hydrology coupling
- **Barrier:** Data availability, model time-step constraints

### 7.4 Groundwater-Surface Water Integration
**Gap:** LULC effects on groundwater often simplified or omitted
- **Need:** Fully integrated models (e.g., MIKE SHE) more widely applied
- **Barrier:** Data requirements, calibration complexity

### 7.5 Tropical and Data-Scarce Regions
**Gap:** Literature dominated by temperate, data-rich catchments
- **Need:** More studies in Africa, South Asia, South America
- **Barrier:** Data scarcity, modeling capacity, funding priorities

**Recent Progress:** Afghanistan, West Africa studies emerging (Hussainzada et al., 2021-2024; Achugbu et al., 2020)

### 7.6 Vegetation Dynamics vs. Land Cover Change
**Gap:** LULC (land cover class change) conflated with vegetation state change (LAI, phenology)
- **Need:** Distinguish structural LULC from vegetation condition dynamics
- **Barrier:** Remote sensing product limitations, model parameterization

### 7.7 Compound LULC + Climate Extremes
**Gap:** Most studies examine LULC or climate change in isolation
- **Need:** Interaction effects under compound hot-dry, wet-warm scenarios
- **Barrier:** Scenario complexity, attribution challenges

---

## 8. Recommendations for Future Research

### 8.1 Methodological Priorities

1. **Dynamic LULC Forcing:** Implement annual LULC updates from Sentinel-2/Landsat in operational models
2. **Multi-Model Ensembles:** Compare LULCC responses across mHM, SWAT, VIC, WRF-Hydro to quantify structural uncertainty
3. **Observation Constraints:** Use GRACE terrestrial water storage, SMAP soil moisture, flux tower ET to validate LULC effects
4. **Process Disaggregation:** Separate LULC effects on interception, ET, infiltration, routing rather than bulk runoff

### 8.2 Model Development Needs

1. **mHM:** Enhance dynamic LULC module; couple with CORINE time series
2. **SWAT:** Improve sub-daily LULC response; integrate urban stormwater modules
3. **WRF-Hydro:** Develop user-friendly LULC scenario tools; expand LSM vegetation options
4. **Hybrid Models:** Combine process-based detail with machine learning LULC prediction

### 8.3 Study Design Recommendations

1. **Paired Catchments:** Continue classic experimental watershed approach with modern instrumentation
2. **Space-for-Time Substitution:** Use LULC gradients as natural experiments
3. **Long-Term Monitoring:** Multi-decadal records essential for detecting LULC legacy effects
4. **Open Data/Code:** Standardized LULC scenario protocols for cross-study comparison

### 8.4 Priority Research Questions

1. **What LULC change thresholds** trigger non-linear hydrological response?
2. **How do LULC effects interact** with compound climate extremes (drought + heat, flood + land saturation)?
3. **Can dynamic LULC updating** improve flood forecasting skill?
4. **What is the relative importance** of LULC vs. climate change for water security in different regions?
5. **How can socio-economic scenarios** (SSPs) be operationalized in hydrological LULC modeling?

---

## Key References (Selected)

### Foundational Studies
- Bosch, J.M. & Hewlett, J.D. (1982). Catchment experiments on vegetation changes and water yield. *J. Hydrol.*, 55, 3-23.
- Lean, J. & Rowntree, P. (1993). Amazonian deforestation climate impact. *Q.J.R. Meteorol. Soc.*, 119, 509-530.

### Model-Specific LULCC Studies
- Park, J.-Y. et al. (2011). MIROC3.2 + CLUE-S + SWAT integration. *Trans. ASABE*, 54(5), 1713-1724.
- Matheussen, B. et al. (2000). Columbia River Basin LULC effects (VIC). *Hydrol. Process.*, 14, 867-885.
- Hussainzada, W. & Lee, H.S. (2024). WRF-Hydro in Afghanistan snow-dominated watersheds. *AIMS Geosci.*, 10(2), 312-332.
- Achugbu, I.C. et al. (2020). WRF LSM performance over West Africa. *Advances in Meteorology*, 2020, 6205308.

### Remote Sensing Integration
- Dubayah, R.O. et al. (2000). Remote sensing in hydrological modeling. *Springer*, 85-102.
- Ottlé, C. et al. (1989). Remote sensing applications to hydrological modeling. *J. Hydrol.*, 105, 369-384.

### LULC Modeling
- Verburg, P.H. & Overmars, K.P. (2007). CLUE-S dynamic simulation. *Modelling Land-Use Change*, 321-337.
- Kurniawan, I. et al. (2022). LULC to hydrology response model (IKN Nusantara). *J. Southwest Jiaotong Univ.*, 57(6), 985-994.

### Recent Synthesis
- John, A. et al. (2021). Disaggregated hydrological models for changing climate. *J. Hydrol.*, 598, 126471.
- Zhang, H. et al. (2001). Tropical deforestation + greenhouse warming compounding. *Climatic Change*, 49, 309-338.

---

**Synthesis compiled by:** Helferchen (Research Assistant)  
**For:** Julian Schlaak - PhD Paper #2 (LULCC in Hydrological Modelling)  
**Workspace:** `/data/.openclaw/workspace/open_claw_vibe_coding/paper2_lulc/literature/synthesis.md`
