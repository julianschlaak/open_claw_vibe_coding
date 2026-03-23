# Paper #2 LULC: Conceptual Diagrams & Graphical Abstracts

**Document Type:** Visual Framework Specifications  
**Purpose:** Diagram descriptions for Paper #2 figures (theoretical, no data)  
**Created:** 2026-03-11  
**Status:** Theoretical only (no data/model prep)

---

## 1. Graphical Abstract (One-Panel Summary)

### 1.1 Concept

**Title:** "Forest Type Effects on Water Balance During Compound Drought"

**Layout:** 3-column comparison (Spruce vs. Mixed vs. Clearcut)

**Visual Elements:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    HARZ 2018-2020 DROUGHT                       │
│              Compound Event: SPI -2.8, +2.1°C                   │
└─────────────────────────────────────────────────────────────────┘

┌───────────────┬───────────────┬───────────────┐
│   SPRUCE      │   MIXED       │   CLEARCUT    │
│   (Baseline)  │   (50/50)     │   (Mortality) │
├───────────────┼───────────────┼───────────────┤
│   🌲🌲🌲      │   🌲🌳🌲🌳    │   🪵🪵🪵       │
│   LAI 8.0     │   LAI 7.0/4.0 │   LAI 0.2     │
│   Root 1.0m   │   Root 2.0m   │   Root 0.5m   │
│   Int 30-35%  │   Int 18-28%  │   Int 5-10%   │
├───────────────┼───────────────┼───────────────┤
│   ET: 100%    │   ET: 85-92%  │   ET: 50-70%  │
│   Q: 100%     │   Q: 110-115% │   Q: 140-160% │
│   Lag: 100%   │   Lag: 80-85% │   Lag: 30-40% │
└───────────────┴───────────────┴───────────────┘

Arrow: "Forest Conversion → +10-15% Runoff (Mixed), +40-60% Runoff (Clearcut)"
```

**Color Scheme:**
- **Spruce:** Dark green (#2D5016)
- **Beech:** Light green (#6B8E23)
- **Clearcut:** Brown (#8B4513)
- **Water:** Blue (#4682B4)
- **Drought:** Red/orange gradient (#FF6347 → #FFA500)

**Text:** Minimal (key parameters only: LAI, Root Depth, Interception, ΔQ, ΔET)

---

### 1.2 Specifications for Illustrator

| Element | Size | Position | Notes |
|---------|------|----------|-------|
| **Title Box** | 100% width | Top | Bold, sans-serif |
| **Forest Icons** | 3× equal | Middle row | Stylized trees (not photorealistic) |
| **Parameter Boxes** | 3× equal | Below icons | White background, black text |
| **Effect Arrows** | Horizontal | Bottom | Green (Mixed), Red (Clearcut) |
| **Scale Bar** | Bottom right | — | "100% = Spruce Baseline" |

**File Format:** SVG (scalable), PNG (300 dpi minimum)

**Target Journal:** HESS (Hydrology and Earth System Sciences) — 2-column format

---

## 2. Conceptual Framework Diagram (Multi-Panel)

### 2.1 Panel A: Water Balance Pathways

**Title:** "Forest Type Modulates Water Balance Partitioning"

**Layout:** Flow diagram (precipitation → partitioning → outputs)

```
                    PRECIPITATION (P)
                         │
                         │ 800 mm/yr (Harz)
                         ▼
              ┌──────────────────────┐
              │   FOREST CANOPY      │
              │                      │
              │  Spruce: LAI 8.0     │
              │  Mixed:  LAI 7.0/4.0 │
              │  Clearcut: LAI 0.2   │
              └──────────────────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
      INTERCEPTION   THROUGHFALL   STEMFLOW
      (30-35% S)     (65-70% S)     (2-3% S)
      (18-28% M)     (72-82% M)     (2-3% M)
      (5-10% C)      (90-95% C)     (1-2% C)
            │            │
            │            ▼
      EVAPORATION   INFILTRATION
      (Canopy)      (Soil Surface)
            │            │
            │            ▼
            │      TRANSPORTATION
            │      (Root Uptake)
            │            │
            │      ┌─────┴─────┐
            │      │           │
            │   SOIL STORAGE  RECHARGE
            │   (0.5-1.5m S)  (Deep)
            │   (2.0-4.0m M)      │
            │   (0.5-1.0m C)      │
            │                     │
            │                     ▼
            │               BASEFLOW
            │               (Delayed)
            │                     │
            └─────────────────────┘
                      │
                      ▼
                  RUNOFF (Q)
                  (Quick Flow)
```

**Color Coding:**
- **Interception:** Light blue (evaporation loss)
- **Transpiration:** Green (vegetation flux)
- **Runoff:** Dark blue (streamflow)
- **Recharge:** Light blue (groundwater)

**Arrow Thickness:** Proportional to flux magnitude (Spruce baseline = 100%)

---

### 2.2 Panel B: Drought Propagation Pathway

**Title:** "Forest Type Modulates Drought Propagation Lags"

**Layout:** Timeline with lag arrows (different forest types)

```
METEORDROUGHT (P) ──────┬──────────────────────────────────────> SPI
                        │  (SPI -2.8, 2018-2020)
                        │
                        │ Lag: 4-6 weeks (Spruce)
                        │      3-5 weeks (Mixed)
                        │      1-2 weeks (Clearcut)
                        ▼
AGRIC. DROUGHT (SM) ────┼──────────────────────────────────────> SMI
                        │  (SMI -2.5, 2018-2020)
                        │
                        │ Lag: 12-20 weeks (Spruce)
                        │      10-16 weeks (Mixed)
                        │       4-8 weeks (Clearcut)
                        ▼
HYDRO. DROUGHT (Q) ─────┴──────────────────────────────────────> SDI
                           (SDI -2.2, 2018-2020)

Total Lag (P → Q):
  Spruce:    16-26 weeks (████████████████████)
  Mixed:     13-21 weeks (████████████████)
  Clearcut:   5-10 weeks (████████)
```

**Visual Style:**
- **Boxes:** Rounded rectangles (meteorological, agricultural, hydrological)
- **Arrows:** Curved (showing lag time)
- **Timeline:** Horizontal axis (weeks 0-30)
- **Color:** Gradient (blue → orange → red for drought severity)

---

### 2.3 Panel C: Counterfactual Analysis Framework

**Title:** "Attribution: LULC vs. Climate Effects"

**Layout:** 2×2 matrix (time × scenario)

```
                    TIME PERIOD
              ┌───────────┬───────────┐
              │ 1991-2017 │ 2018-2020 │
              │ (Baseline)│ (Drought) │
┌─────────────┼───────────┼───────────┤
│  SPRUCE     │           │           │
│  (Healthy)  │    S0     │    S1     │
│             │  Baseline │  Counter- │
│             │           │  factual  │
├─────────────┼───────────┼───────────┤
│  MIXED      │           │           │
│  (50/50)    │    —      │    S2     │
│             │           │  Alternative│
├─────────────┼───────────┼───────────┤
│  CLEARCUT   │           │           │
│  (Mortality)│    —      │    S3     │
│             │           │  Reality  │
└─────────────┴───────────┴───────────┘

Attribution:
  Climate Effect = S1 - S0
  LULC Effect    = S3 - S1
  Interaction    = (S3 - S0) - (Climate + LULC)
```

**Color Coding:**
- **S0:** Green (baseline, healthy forest)
- **S1:** Yellow (counterfactual, drought but no mortality)
- **S2:** Blue-green (alternative, mixed forest)
- **S3:** Brown (reality, clearcut)

**Arrows:** Show comparison pathways (S1-S0, S3-S1, etc.)

---

## 3. Hypothesis Diagrams (H1-H6)

### 3.1 H1: Forest Type → Interception

**Visual:** Box plot (3 boxes: Spruce, Mixed, Beech)

```
Interception (% of P)
  │
40│         ┌───┐
  │         │   │
35│    ┌────┤   ├────┐
  │    │    │   │    │
30│    ├────┤   │    │
  │    │    │   │    │
25│    │    └───┘    │
  │    │             │
20│    │             │
  │    │             └───┐
15│    │                 │
  │    │                 ├───┐
10│    │                 │   │
  │    │                 │   │
 5│    │                 │   │
  │    │                 │   │
 0│────┴─────────────────┴───┴────>
      Spruce    Mixed    Beech
      (S)       (M)      (B)

  ┌─┐ = 95% CI
  │ │ = Mean
  └─┘ = Range
```

**Expected Pattern:** Spruce > Mixed > Beech (annual), Beech winter << Spruce winter

---

### 3.2 H2: Seasonal Interception (Beech)

**Visual:** Line plot (seasonal trajectory, Spruce flat vs. Beech sinusoidal)

```
Interception (%)
  │
35│    Spruce (evergreen)
  │    ────────────────────
30│
  │
25│
  │                    Beech (deciduous)
20│                 ╱──────╲
  │               ╱          ╲
15│             ╱              ╲
  │           ╱                  ╲
10│         ╱                      ╲
  │       ╱                          ╲
 5│     ╱                              ╲
  │   ╱                                  ╲
 0│──┴────┬────┬────┬────┬────┬────┬────┴──>
      Spr  Sum  Aut  Win  Spr  Sum  Aut  Win
      (Seasonal Cycle)
```

**Key Feature:** Beech winter minimum (5-10%) vs. Spruce constant (30-35%)

---

### 3.3 H3: Root Depth → Drought Resilience

**Visual:** Soil profile cross-section (root depth comparison)

```
Depth (m)
  │
0 │─────────────────────────────────  Soil Surface
  │
  │    Spruce (shallow)
1 │    ═══════════════════
  │    ███████████████████
  │
2 │                    Beech (deep)
  │                    ═══════════════════
  │                    ███████████████████
3 │                                    ═══
  │                                    ███
4 │
  │
  │    ████████ = Root biomass
  │    ════════ = Water table (drought)
```

**Annotation:** "Beech accesses deep water during drought (ψ < -1.5 MPa)"

---

### 3.4 H4: Drought Propagation Lags

**Visual:** Cross-correlation function (ACF plot, forest type comparison)

```
Correlation (r)
  │
1.0│  ┌─────────────────────────────────────┐
   │  │                                     │
0.8│  │  Spruce                             │
   │  │  ═══════════════                    │
0.6│  │                  Mixed               │
   │  │                  ═══════             │
0.4│  │                          Clearcut    │
   │  │                          ═══         │
0.2│  │                                      │
   │  │                                      │
0.0│──┴──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──>
      0  4  8 12 16 20 24 28 32 36 40 44 48  (weeks)
         ↑     ↑     ↑
        P→SM  SM→Q  Total
```

**Peak Lag:** Spruce (16-26 wks), Mixed (13-21 wks), Clearcut (5-10 wks)

---

### 3.5 H5: Clearcut → Runoff Effect

**Visual:** Before/after bar chart (Spruce vs. Clearcut)

```
Runoff (mm/yr)
  │
600│                              ┌─────┐
   │                              │     │
500│                              │     │
   │                              │     │
400│                              │     │
   │              ┌─────┐         │     │
300│              │     │         │     │
   │              │     │         │     │
200│              │     │         │     │
   │              │     │         │     │
100│              │     │         │     │
   │              │     │         │     │
  0│──────────────┴─────┴─────────┴─────┴────>
         Spruce         Clearcut
         (Baseline)     (Mortality)

         200-350        320-520
         mm/yr          mm/yr
         (+40-60%)
```

**Error Bars:** 95% CI (Spruce: [180, 380], Clearcut: [290, 580])

---

### 3.6 H6: LULC × Climate Interaction

**Visual:** Interaction plot (additive vs. non-additive)

```
Runoff (mm/yr)
  │
600│                                    ┌─────┐
   │                                    │     │
500│                                    │Obs  │
   │                                    │  ●  │
400│                          ┌─────┐   │     │
   │                          │Add  │   │     │
300│                ┌─────┐   │  ●  │   │     │
   │                │Base │   │     │   │     │
200│                │  ●  │   │     │   │     │
   │                │     │   │     │   │     │
100│                │     │   │     │   │     │
   │                │     │   │     │   │     │
  0│────────────────┴─────┴───┴─────┴───┴─────┴────>
              Baseline  LULC  Climate  Combined
              (S0)      only  only     (Observed)

  ● = Expected (additive model)
  ┌─┐ = Observed (non-additive, interaction +10-30%)
```

**Key Feature:** Observed > Additive (synergistic interaction)

---

## 4. Scenario Comparison Diagram (S0-S3)

### 4.1 Multi-Panel Layout

**Title:** "Scenario Matrix: Harz 2018-2020"

**Layout:** 4-column (S0, S1, S2, S3) × 3-row (Parameters, Fluxes, Drought Response)

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│     S0      │     S1      │     S2      │     S3      │
│  Baseline   │  Counter-   │  Alternative│   Reality   │
│  (1991-2017)│  factual    │  (Mixed)    │  (Clearcut) │
│             │  (2018-2020)│  (2018-2020)│  (2018-2020)│
├─────────────┼─────────────┼─────────────┼─────────────┤
│  🌲🌲🌲     │  🌲🌲🌲     │  🌲🌳🌲🌳   │  🪵🪵🪵      │
│  100% Spruce│  100% Spruce│  50/50      │  0% Forest  │
│  LAI 8.0    │  LAI 8.0    │  LAI 7.0/4.0│  LAI 0.2    │
│  Root 1.0m  │  Root 1.0m  │  Root 2.0m  │  Root 0.5m  │
├─────────────┼─────────────┼─────────────┼─────────────┤
│  ET: 100%   │  ET: 85-95% │  ET: 80-90% │  ET: 50-70% │
│  Q: 100%    │  Q: 90-95%  │  Q: 110-115%│  Q: 140-160%│
│  Lag: 100%  │  Lag: 95%   │  Lag: 80-85%│  Lag: 30-40%│
├─────────────┼─────────────┼─────────────┼─────────────┤
│  SMI: -1.0  │  SMI: -2.5  │  SMI: -2.0  │  SMI: -3.0  │
│  SDI: -0.8  │  SDI: -2.2  │  SDI: -1.8  │  SDI: -2.5  │
│  (Normal)   │  (Drought)  │  (Drought)  │  (Drought)  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

**Color Gradient:**
- **S0:** Green (baseline, healthy)
- **S1:** Yellow (drought, but forest intact)
- **S2:** Blue-green (mixed, intermediate)
- **S3:** Brown (clearcut, degraded)

---

### 4.2 Timeseries Overlay (All Scenarios)

**Visual:** Multi-line plot (1991-2020, S0-S3 comparison)

```
Runoff (mm/yr)
  │
600│                                    S3 (Clearcut)
   │                                   ╱
500│                                  ╱
   │                                 ╱
400│                        S2 (Mixed)
   │                       ╱────────
300│              S0, S1   ╱
   │              ════════
200│             ╱
   │            ╱
100│           ╱
   │          ╱
  0│─────────┴────┬────┬────┬────┬────┬────┬────┬────>
     1991   1995  2000 2005 2010 2015 2018 2020
                          │     │
                          │     └─ Drought Period (S1, S2, S3 diverge)
                          └─ Baseline Period (S0, S1 overlap)
```

**Key Feature:** Scenarios overlap 1991-2017 (S0=S1), diverge 2018-2020 (LULC effect).

---

## 5. Mechanism Diagrams

### 5.1 Interception Mechanism

**Visual:** Canopy water flux (droplets on leaves, evaporation arrows)

```
    Precipitation
         │
         ▼
    ┌─────────┐
    │  Canopy │
    │  (LAI)  │
    └─────────┘
         │
    ┌────┴────┐
    │         │
Throughfall  Interception
    │         │
    ▼         ▼
  Soil     Evaporation
            (LAI-dependent)
            Spruce: 30-35%
            Mixed:  18-28%
            Clearcut: 5-10%
```

**Detail:** Leaf-level inset (spruce needle vs. beech leaf, water droplets)

---

### 5.2 Transpiration Mechanism

**Visual:** Soil profile with root water uptake (depth-dependent)

```
Depth (m)     Spruce        Mixed         Clearcut
  │
0 │─────────────────────────────────────────────────
  │           ║║║           ║║║║║         ║
  │           ║║║           ║║║║║         ║║
1 │═══════════╝║           ║║║║║         ║║
  │           Root          ║║║║║         ║║
  │           (0.5-1.5m)    ║║║║║         ║║
2 │                         ║║║║║         ║║
  │                         ║║║║║         ║║
  │                         ║║║║║         ║║
3 │                         ║║║║║         ║║
  │                         ║║║║║         ║║
  │                         ║║║║║         ║║
4 │                         ║║║║║         ║║
  │                         Beech         Regrowth
  │                         (2-4m)        (0.5-1m)
  │
  │   ║ = Root biomass
  │   ═ = Water table
```

**Annotation:** "Beech deep roots access water during drought (ψ < -1.5 MPa)"

---

### 5.3 Runoff Generation Mechanism

**Visual:** Hillslope cross-section (overland flow, subsurface flow, baseflow)

```
Elevation (m)
  │
600│  🌲🌲🌲 (Spruce)
   │   ╲
500│    ╲  Overland Flow (quick)
   │     ╲
400│      ╲  Subsurface Flow (intermediate)
   │       ╲
300│        ╲  Baseflow (delayed)
   │         ╲
200│          ╲
   │           ╲
100│            ╲
   │             ╲
  0│──────────────╲────────────────────> Stream
      0  1  2  3  4  5  6  7  8  9  10 (km)

Flow Components:
  Overland:   20% (Spruce), 30% (Mixed), 60% (Clearcut)
  Subsurface: 40% (Spruce), 45% (Mixed), 30% (Clearcut)
  Baseflow:   40% (Spruce), 25% (Mixed), 10% (Clearcut)
```

**Key Feature:** Clearcut → more overland flow (flashier), less baseflow (reduced groundwater recharge).

---

## 6. Specifications for Figure Creation

### 6.1 Software Recommendations

| Figure Type | Recommended Tool | Format | Notes |
|-------------|------------------|--------|-------|
| **Graphical Abstract** | Adobe Illustrator / Inkscape | SVG | Vector, scalable |
| **Conceptual Framework** | PowerPoint / Keynote + Illustrator | PNG (300 dpi) | Multi-panel |
| **Hypothesis Diagrams** | R (ggplot2) / Python (matplotlib) | PDF | Statistical plots |
| **Scenario Comparison** | R (ggplot2) / Python (seaborn) | PDF | Timeseries overlay |
| **Mechanism Diagrams** | Illustrator / BioRender | SVG | Process flows |

**Open-Source Alternative:** Inkscape (SVG), R/ggplot2 (PDF), Python/matplotlib (PNG)

---

### 6.2 Journal Requirements (HESS)

| Requirement | Specification |
|-------------|---------------|
| **Figure Width** | Single column: 8.3 cm, Double column: 16.6 cm |
| **Resolution** | 300 dpi (minimum), 600 dpi (preferred) |
| **Format** | PDF/EPS (vector), PNG/TIFF (raster) |
| **Font** | Arial/Helvetica (sans-serif), 8-10 pt |
| **Color Mode** | RGB (online), CMYK (print) |
| **File Size** | <10 MB per figure |

**Color Blindness:** Use ColorBrewer palettes (viridis, plasma, cividis)

---

### 6.3 Figure Captions (Draft)

**Graphical Abstract:**
> "Forest type effects on water balance during the 2018-2020 compound drought in the Harz region. Spruce monoculture (baseline) is compared to mixed forest (50% spruce + 50% beech) and clearcut (post-mortality). Key parameters (LAI, root depth, interception) drive differences in evapotranspiration (ET), runoff (Q), and drought propagation lags. Clearcut shows +40-60% runoff increase, while mixed forest shows +10-15% increase relative to spruce baseline."

**Conceptual Framework (Panel A-C):**
> "Conceptual framework for forest type effects on water balance. (A) Water balance partitioning: precipitation is divided into interception, throughfall, and stemflow, with forest type modulating flux magnitudes. (B) Drought propagation pathway: meteorological drought (SPI) propagates to agricultural (SMI) and hydrological (SDI) drought with forest type-dependent lags. (C) Counterfactual analysis framework: four scenarios (S0-S3) enable attribution of LULC vs. climate effects."

---

## 7. Summary: Diagram Specifications

| Diagram | Purpose | Complexity | Priority |
|---------|---------|------------|----------|
| **Graphical Abstract** | One-panel summary | Medium | High (TOC) |
| **Conceptual Framework** | Multi-panel theory | High | High (Introduction) |
| **H1-H6 Diagrams** | Hypothesis visualization | Medium | Medium (Methods) |
| **Scenario Comparison** | S0-S3 overview | Medium | High (Results) |
| **Mechanism Diagrams** | Process explanation | High | Medium (Discussion) |

**Total:** 5 diagram types, 10-15 individual panels

**Estimated Effort:** 20-30 hours (professional illustrator), 40-60 hours (DIY with R/Python)

---

**Document Status:** Complete conceptual diagram specifications (theoretical, no data).  
**Next:** Implement diagrams when empirical results available.
