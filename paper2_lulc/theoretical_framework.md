# Paper #2 LULC: Theoretischer Rahmen

**Document Type:** Theoretical Framework for LULC Impact Analysis  
**Purpose:** Scientific foundation, hypotheses, expected relationships  
**Created:** 2026-03-11  
**Status:** Theoretical only (no data/model prep)

---

## 1. Research Questions & Hypotheses

### 1.1 Primary Research Question

> **"How does forest type composition affect soil water balance during compound drought events?"**

**Sub-Questions:**
1. What is the hydrological effect of spruce monoculture vs. mixed forest (spruce + beech)?
2. How does forest mortality (2018-2020 drought) alter catchment water balance?
3. What is the counterfactual: "What if the forest had not died?"
4. What is the alternative: "What if converted to mixed forest instead of clearcut?"

---

### 1.2 Hypotheses (H1-H6)

| Hypothesis | Statement | Expected Direction | Source |
|------------|-----------|-------------------|--------|
| **H1: Forest Type Effect** | Mixed forest (50% spruce + 50% beech) has lower annual interception than spruce monoculture | Mixed < Spruce by 10-15% | Calder 1978, Rowe 1983 |
| **H2: Seasonal Interception** | Beech shows strong seasonal interception variation (summer 15-25%, winter 5-10%); spruce is evergreen (30-35% year-round) | Beech winter < Spruce winter by 20-25% | Granier 2000 |
| **H3: Root Water Uptake** | Beech (deep roots, 2-4m) accesses deeper soil water during drought than spruce (shallow, 0.5-1.5m) | Beech drought resilience > Spruce | Martinetti 2025 |
| **H4: Drought Propagation** | Forest type affects drought propagation speed (P → SM → Q lags) | Mixed forest: faster drainage, shorter lags | Vorobevskii 2022 |
| **H5: Mortality Effect** | Forest mortality (clearcut) increases annual runoff by 40-60% and peak flow by 50-100% | Clearcut >> Spruce | Bosch & Hewlett 1982 |
| **H6: Non-Additive Interaction** | LULC × Climate interaction is non-additive (combined effect > sum of individual effects) | Interaction term: +10-30% | Preetha 2023, Dixit 2022 |

---

## 2. Conceptual Framework

### 2.1 Water Balance Equation (Catchment Scale)

```
P = Q + ET + ΔS + R

Where:
- P: Precipitation (mm/yr)
- Q: Discharge (mm/yr)
- ET: Evapotranspiration (mm/yr) = Interception + Transpiration + Soil Evaporation
- ΔS: Change in Storage (soil moisture + groundwater) (mm/yr)
- R: Deep Recharge (mm/yr)
```

**Forest Type Effects:**
- **Interception:** Spruce (30-35%) > Mixed (18-28%) > Beech summer (15-25%) > Beech winter (5-10%)
- **Transpiration:** Beech (500-700 mm/yr) > Spruce (400-550 mm/yr) > Pine (450-600 mm/yr)
- **Root Depth:** Beech (2-4m) > Pine (1-3m) > Spruce (0.5-1.5m)
- **Net Effect on Q:** Clearcut >> Spruce > Mixed > Beech

---

### 2.2 Drought Propagation Pathway

```
Meteorological Drought (SPI/SPEI)
    ↓  (1-3 months lag)
Agricultural Drought (SMI - Soil Moisture)
    ↓  (3-6 months lag)
Hydrological Drought (SDI - Streamflow)
    ↓
Integrated Drought (MDI - Matrix Index, Paper #1)
```

**Forest Type Modulation:**
- **Spruce:** Conservative water use → earlier stomatal closure → slower propagation
- **Beech:** Aggressive water use → deeper roots → faster drainage → shorter lags
- **Clearcut:** No interception/transpiration → immediate runoff response → shortest lags

**Expected Lags (Harz):**
- **Spruce:** P → SM (4-6 weeks), SM → Q (12-20 weeks), Total: 16-26 weeks
- **Mixed:** P → SM (3-5 weeks), SM → Q (10-16 weeks), Total: 13-21 weeks
- **Clearcut:** P → SM (1-2 weeks), SM → Q (4-8 weeks), Total: 5-10 weeks

**Source:** Vorobevskii 2022 (Wernersbach, Saxony: 4-9 months total = 16-36 weeks)

---

### 2.3 LULC Impact Mechanisms

| Mechanism | Spruce → Mixed | Spruce → Clearcut | Source |
|-----------|----------------|-------------------|--------|
| **Interception Loss** | -10-15% (annual) | -20-30% (annual) | Calder 1978, Rowe 1983 |
| **Transpiration** | -5-10% (beech lower than spruce in winter) | -30-50% (no canopy) | Granier 2000 |
| **Root Water Uptake** | Deeper (beech 2-4m vs. spruce 0.5-1.5m) | Lost (shallow regrowth 0.5-1m) | Martinetti 2025 |
| **Infiltration (Ksat)** | Similar (135 vs. 120 mm/h) | -50-75% (compaction) | Bonell 1998 |
| **Manning's n** | Similar (0.65 vs. 0.7) | -50-60% (0.3 vs. 0.7) | Chow 1959 |
| **Albedo** | +10-20% (mixed higher) | +50-100% (bare soil) | Bonan 2008 |
| **Net Effect on Q** | +10-15% annual runoff | +40-60% annual runoff | Bosch & Hewlett 1982 |

---

## 3. Theoretical Expectations (Quantitative)

### 3.1 Annual Water Balance (Harz, ~800mm P/yr)

| Component | Spruce (Baseline) | Mixed Forest | Clearcut | Beech (Pure) |
|-----------|-------------------|--------------|----------|--------------|
| **P (Precipitation)** | 800 mm/yr | 800 mm/yr | 800 mm/yr | 800 mm/yr |
| **Interception** | 240-280 mm/yr (30-35%) | 144-224 mm/yr (18-28%) | 40-80 mm/yr (5-10%) | 120-200 mm/yr (15-25%) |
| **Transpiration** | 400-550 mm/yr | 380-520 mm/yr | 200-300 mm/yr | 500-700 mm/yr |
| **Soil Evaporation** | 50-80 mm/yr | 60-90 mm/yr | 100-150 mm/yr | 50-80 mm/yr |
| **Total ET** | 690-910 mm/yr | 588-834 mm/yr | 340-530 mm/yr | 670-980 mm/yr |
| **Q (Runoff)** | 200-350 mm/yr | 220-400 mm/yr | 320-520 mm/yr | 180-300 mm/yr |
| **ΔS + R** | Balance | Balance | Balance | Balance |

**Sources:** Calder 1978, Granier 2000, Bosch & Hewlett 1982, Zhang 2020.

**Key Insight:** Clearcut has **lowest ET** (no canopy) → **highest Q** (more runoff). Mixed forest has **intermediate Q** (between spruce and clearcut).

---

### 3.2 Seasonal Dynamics (Beech vs. Spruce)

| Season | Spruce Interception | Beech Interception | Difference |
|--------|---------------------|--------------------|------------|
| **Spring (Mar-May)** | 30-35% | 10-20% (leaf-out) | Beech -10-15% |
| **Summer (Jun-Aug)** | 30-35% | 15-25% (full canopy) | Beech -5-10% |
| **Autumn (Sep-Nov)** | 30-35% | 15-20% (senescence) | Beech -10-15% |
| **Winter (Dec-Feb)** | 30-35% | 5-10% (leaf-off) | **Beech -20-25%** |

**Implication:** Winter runoff is **20-25% higher** under beech than spruce (less interception loss).

---

### 3.3 Drought Response (2018-2020 Compound Event)

| Metric | Spruce (Healthy) | Spruce (Drought-Stressed) | Mixed Forest | Clearcut |
|--------|------------------|---------------------------|--------------|----------|
| **Interception** | 30-35% | 25-30% (reduced LAI) | 18-28% | 5-10% |
| **Transpiration** | 400-550 mm/yr | 300-400 mm/yr (stomatal closure) | 380-520 mm/yr | 200-300 mm/yr |
| **Soil Moisture** | Baseline | -30-50% (drought) | -20-40% (deeper roots) | -50-70% (no buffering) |
| **Runoff** | Baseline | -20-40% (less Q from drought) | -15-35% | -10-25% (but higher absolute Q) |
| **Peak Flow** | Baseline | Variable (flashier) | +10-15% (faster response) | +50-100% (immediate) |
| **Baseflow** | Baseline | -30-50% | -20-40% | -40-60% |

**Source:** Dixit 2022 (Kerala megafloods: LULC attribution 20-30% of flood enhancement).

---

## 4. Analytical Framework

### 4.1 Drought Indices (Multi-Timescale)

| Index | Component | Timescales | Interpretation |
|-------|-----------|------------|----------------|
| **SPI** | Precipitation only | 1, 3, 6, 12 months | Meteorological drought |
| **SPEI** | P - PET (climatic water balance) | 1, 3, 6, 12 months | Climatic drought (temperature-sensitive) |
| **SMI** | Soil Moisture (percentile-based) | 1, 3, 6, 12 months | Agricultural drought |
| **SDI** | Streamflow (percentile-based) | 1, 3, 6, 12 months | Hydrological drought |
| **MDI** | Composite (SM + Recharge + Q) | 1, 3, 6, 12 months | Integrated drought (Paper #1) |

**Forest Type Signal:**
- **SPI:** No forest signal (precipitation only)
- **SPEI:** Forest type affects PET (LAI-based, not aspect-based)
- **SMI:** Strong forest signal (interception + transpiration + root uptake)
- **SDI:** Strong forest signal (runoff generation, peak flow timing)
- **MDI:** Integrated forest signal (all compartments)

---

### 4.2 Attribution Approach (LULC vs. Climate)

**Problem:** 2018-2020 drought had both:
- **Climate driver:** Low precipitation, high temperature (SPI/SPEI signal)
- **LULC driver:** Forest mortality, salvage logging (LULC change)

**Solution:** Counterfactual Analysis

```
Observed (2018-2020): Climate + LULC (mortality)
Counterfactual S1 (2018-2020): Climate only (no mortality)
Alternative S2 (2018-2020): Climate + LULC (mixed forest)
Reality S3 (2018-2020): Climate + LULC (clearcut)

LULC Effect = Observed - Counterfactual S1
Climate Effect = Counterfactual S1 - Baseline S0 (1991-2017)
Interaction = (Observed - S0) - (Climate Effect + LULC Effect)
```

**Source:** Preetha & Hasan (2023) — Compound LULC+climate, interaction term 10-30%.

---

### 4.3 Expected Effect Sizes (Cohen's d)

| Comparison | Effect Size (d) | Interpretation | Source |
|------------|-----------------|----------------|--------|
| **Spruce → Mixed (Interception)** | d = 0.8-1.2 | Large | Calder 1978, Rowe 1983 |
| **Spruce → Clearcut (Runoff)** | d = 1.5-2.5 | Very Large | Bosch & Hewlett 1982 |
| **Spruce → Mixed (Runoff)** | d = 0.5-0.8 | Medium | Zhang 2020 |
| **Drought → Non-Drought (SMI)** | d = 1.0-1.5 | Large | Vorobevskii 2022 |
| **LULC × Climate (Interaction)** | d = 0.6-1.0 | Medium-Large | Preetha 2023, Dixit 2022 |

**Statistical Power:**
- **n = 30 years** (1991-2020) → High power (1-β > 0.80) for large effects
- **n = 3 years** (2018-2020 drought) → Moderate power for very large effects

---

## 5. Literature Synthesis (15 Papers)

### 5.1 Forest Hydrology (Pre-2000)

| Paper | Key Finding | Effect Size | Relevance |
|-------|-------------|-------------|-----------|
| **Calder (1978)** | Spruce interception 30-35%, transpiration 400-550 mm/yr | Baseline | H1, H2 |
| **Bosch & Hewlett (1982)** | Forest removal → +40-60% runoff | d = 1.5-2.5 | H5 |
| **Rutter et al. (1975)** | Coniferous > Deciduous interception | d = 0.8-1.2 | H1, H2 |
| **Rowe (1983)** | Beech winter interception 5-10% (leaf-off) | d = 1.0-1.5 | H2 |
| **Neary & Gizyn (1994)** | Throughfall: Coniferous 74%, Deciduous 84% | d = 0.6-0.8 | H1 |

---

### 5.2 Modern Forest Hydrology (2000-2026)

| Paper | Key Finding | Effect Size | Relevance |
|-------|-------------|-------------|-----------|
| **Granier et al. (2000)** | Beech transpiration 500-700 mm/yr, LAI 5-7 | Baseline | H1, H2, H3 |
| **Lagergren & Lindroth (2002)** | Pine maintains transpiration at lower ψ than spruce | d = 0.5-0.8 | H3 |
| **Martinetti et al. (2025)** | Beech deeper roots (2-4m) vs. spruce (0.5-1.5m) | d = 1.0-1.5 | H3 |
| **Zhang et al. (2020)** | LULC change → +15-25% runoff (agriculture → forest: -20-30%) | d = 0.8-1.2 | H5 |
| **Pijl & Tarolli (2022)** | Urbanization → +10-30% runoff, +50-100% peak flow | d = 1.0-1.5 | H5 |

---

### 5.3 LULC Impact Studies (2020-2026)

| Paper | Key Finding | Effect Size | Relevance |
|-------|-------------|-------------|-----------|
| **Dixit et al. (2022)** | LULC attribution: 20-30% of flood enhancement (WRF-Hydro) | d = 0.6-1.0 | H6 |
| **Preetha & Hasan (2023)** | LULC × Climate interaction: +10-30% (non-additive) | d = 0.6-1.0 | H6 |
| **Busari et al. (2021)** | Multi-year LULC + LAI-based PET: +20-30% performance | d = 0.5-0.8 | Method |
| **Dembélé et al. (2020)** | Multi-satellite calibration: +20-40% skill | d = 0.5-0.8 | Method |
| **Vorobevskii et al. (2022)** | Drought propagation: P→SM (1-3 mo), SM→Q (3-6 mo) | Baseline | H4 |
| **Alewell et al. (2019)** | CORINE LULC (EU standard, 100m, 6-year) | N/A | Method |

---

## 6. Conceptual Diagrams

### 6.1 Forest Type Water Balance (Annual)

```
                    PRECIPITATION (800 mm/yr)
                           │
              ┌────────────┼────────────┐
              │            │            │
        INTERCEPTION   THROUGHFALL    STEMFLOW
        (Spruce: 30%)   (Spruce: 65%)  (Spruce: 3%)
              │            │            │
              │       ┌────┴────┐       │
              │       │         │       │
         EVAPORATION  INFILTRATION RUNOFF
         (Canopy)     (Soil)     (Quick flow)
                          │
                    TRANSPORTATION
                    (Spruce: 400-550 mm/yr)
                          │
                    ┌─────┴─────┐
                    │           │
              SOIL STORAGE   RECHARGE
              (0.5-1.5m)     (Deep)
              Spruce         │
              shallow        │
                             │
                      BASEFLOW
                      (Delayed)
```

**Mixed Forest Modifications:**
- Interception: -10-15% (beech component)
- Transpiration: -5-10% (winter dormancy)
- Root Depth: +100-200% (beech 2-4m vs. spruce 0.5-1.5m)
- Baseflow: +5-10% (deeper recharge)

---

### 6.2 Drought Propagation (Forest Type Modulation)

```
METEORDROUGHP) ──────┬──────> SPI (-30 to -50% 2018-2020)
                     │
              (1-3 months lag)
                     │
                     ▼
AGRIC. DROUGHT (SM) ─┼──────> SMI (Spruce: -30 to -50%)
                     │         (Mixed: -20 to -40%)
                     │         (Clearcut: -50 to -70%)
              (3-6 months lag)
                     │
                     ▼
HYDRO. DROUGHT (Q) ──┴──────> SDI (Spruce: -20 to -40%)
                              (Mixed: -15 to -35%)
                              (Clearcut: -10 to -25%)
                              BUT: Higher absolute Q (less ET)
```

**Forest Type Effect on Lags:**
- **Spruce:** 16-26 weeks total (conservative, shallow)
- **Mixed:** 13-21 weeks total (faster drainage)
- **Clearcut:** 5-10 weeks total (immediate response)

---

## 7. Knowledge Gaps & Contributions

### 7.1 What We Know (from Literature)

| Topic | Consensus | Uncertainty |
|-------|-----------|-------------|
| **Interception (Spruce)** | 30-35% annual | ±5% (climate-dependent) |
| **Interception (Beech)** | 15-25% summer, 5-10% winter | ±3% (phenology variable) |
| **Transpiration (Spruce)** | 400-550 mm/yr | ±50 mm/yr (drought-sensitive) |
| **Transpiration (Beech)** | 500-700 mm/yr | ±80 mm/yr (V PD-dependent) |
| **Runoff Effect (Clearcut)** | +40-60% annual | ±10% (soil type, slope) |
| **Runoff Effect (Mixed)** | +10-15% annual | ±5% (composition ratio) |
| **Drought Lags** | 16-36 weeks total | ±4 weeks (catchment-specific) |

---

### 7.2 What We Don't Know (Research Gap)

| Gap | Why It Matters | How Paper #2 Addresses |
|-----|----------------|------------------------|
| **Central European forest type effects** | Most studies are North American (Plynlimon) or Mediterranean | Harz focus (German catchments, spruce/beech) |
| **Compound drought × LULC interaction** | Single-factor studies dominate | Counterfactual analysis (climate vs. LULC separation) |
| **Multi-year LULC dynamics** | Static LULC common | Busari 2021 approach (CORINE 2006/2012/2018) |
| **mHM-specific LULC implementation** | SWAT, VIC more common | mHM explicit (Busari 2021, Dembélé 2020) |
| **Drought propagation by forest type** | General lags known, not species-specific | Harz 2018-2020 (spruce mortality event) |

---

### 7.3 Expected Contribution

**Theoretical:**
- Forest type-specific water balance parameters (Central Europe)
- Drought propagation lags by forest type (spruce vs. mixed vs. clearcut)
- LULC × Climate interaction quantification (non-additive effect)

**Methodological:**
- Multi-year LULC implementation (CORINE 2006/2012/2018)
- LAI-based PET (not aspect-based default)
- Counterfactual analysis framework (climate vs. LULC attribution)

**Practical:**
- Forest management guidance (monoculture vs. mixed resilience)
- Drought early warning (forest type vulnerability)
- Climate adaptation strategy (species selection)

---

## 8. Summary: Theoretical Framework

### 8.1 Core Model

```
Forest Type → Interception + Transpiration + Root Depth → Water Balance
     │              │              │              │
     │              │              │              └─→ Q (Runoff)
     │              │              └─→ Drought Resilience
     │              └─→ ET (Annual, Seasonal)
     └─→ LULC Scenario (S0-S3)

Moderators:
- Climate (SPI/SPEI, 2018-2020 drought)
- Soil Type (Ksat, storage capacity)
- Topography (slope, aspect, elevation)
- Forest Age (LAI, root development)
```

---

### 8.2 Expected Outcomes

| Outcome | Direction | Magnitude | Confidence |
|---------|-----------|-----------|------------|
| **Mixed forest vs. Spruce (Q)** | +10-15% annual | Medium | High (Calder, Granier) |
| **Clearcut vs. Spruce (Q)** | +40-60% annual | Large | Very High (Bosch & Hewlett) |
| **Mixed forest vs. Spruce (Drought Resilience)** | +10-20% | Medium | Medium (Martinetti 2025) |
| **LULC × Climate Interaction** | +10-30% non-additive | Medium-Large | Medium (Preetha 2023) |
| **Drought Lags (Mixed vs. Spruce)** | -3 to -5 weeks | Small-Medium | Medium (Vorobevskii 2022) |

---

**Document Status:** Complete theoretical framework (no data/model prep).  
**Next:** Empirical test (when data available).
