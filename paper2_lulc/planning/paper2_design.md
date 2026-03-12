# Paper #2 Design — Realistic Scope (Based on Toosi 2025 Review)

**Created:** 2026-03-12  
**Source:** Toosi et al. (2025) Review + Julian's Strategic Assessment  
**Status:** Conceptual Design Phase

---

## ⚠️ Kern-Einsicht (Toosi 2025 + Julian)

**Nicht versuchen:** Alle 4 LULC-sensitiven Prozessblöcke gleichzeitig mechanistisch in mHM neu entwickeln.
- ❌ Zu groß
- ❌ Zu unsicher
- ❌ Kaum sauber validierbar

**Stattdessen:** **Ein Hauptbeitrag auf Prozessebene** + **1-2 gekoppelte Nebeneffekte** + **starke Mehrgrößen-Evaluation**

---

## 📊 Die 4 LULC-Prozessblöcke (Toosi 2025)

| # | Prozessblock | Toosi-Befund | Paper #2 Eignung |
|---|--------------|--------------|------------------|
| 1 | **Strahlungs-/Energiepartitionierung** | LULC via Albedo, Vegetation, sensible/latent heat, ET, Schnee | ❌ **Zu groß** (datenhungrig, nahe Land-Surface-Model-Umbau) |
| 2 | **Interzeption** | Mehrschichtig (canopy, trunk, understory, litter); LAI als Proxy zu grob | ✅ **BESTE Option** (LULC-nah, implementierbar, relevant, nicht zu expansiv) |
| 3 | **Runoff vs. Infiltration** | Vegetationsschutz, Bodenkrusten, Rauigkeit, Tillage, Urbanisierung, Konnektivität | ⚠️ **Feasible but riskier** (Ereignisdaten nötig, kann unterbestimmt werden) |
| 4 | **Subsurface / Recharge** | LULC = Schlüsselfaktor; Urbanisierung, Bewässerung, Wurzeln, saisonale LULC | ⚠️ **Methodisch heikel** (besser als Folge-Paper mit Recharge-Benchmarks) |

---

## 🏆 Empfohlene Priorisierung

### **Beste Option: Interzeption als Hauptinnovation**

**Paper 2 = Interzeption + gekoppelte Effekte auf ET, SM, Recharge/Q**

**Warum?**
- ✅ Landnutzungsnah (direkter LULC-Einfluss)
- ✅ Prozessrelevant (hydrologisch signifikant)
- ✅ In mHM implementierbar (überschaubare Erweiterung)
- ✅ Nicht zu exotisch (anschlussfähig an Literatur)
- ✅ Mit vorhandenen Datentypen prüfbar (Q, SM, ET)
- ✅ Anschlussfähig an spätere Recharge-/Land-use-Szenarien

---

### **Zweitbeste Option: Runoff/Infiltration-Partitionierung**

**LULC-sensible Parameter für Infiltration, quickflow, surface roughness**

**Gut wenn:** Fokus auf Ereignisse, Hochwasserantwort, schnelle Abflusskomponenten

**Risiko:** Braucht gute Ereignisdaten; mesoskalig kann Prozess unterbestimmt werden

---

### **Dritte Option: Recharge-/Subsurface-Fokus**

**Inhaltlich stark, aber methodisch heikel**

**Besser wenn:** Schon belastbare Recharge-Benchmarks vorhanden

**Risiko:** Wird schnell zum ganzen Projekt statt einem Paper

---

### **Am wenigsten geeignet: Energiepartitionierung**

**Vollständiger Energiebilanz-Ansatz**

**Warum nicht:**
- Zu groß
- Zu datenhungrig (ET-Datasets, LAI, flux towers)
- Zu nahe an Land-Surface-Model-Umbau (nicht mHM-Philosophie)

---

## 📝 Realistisches Paper-Design

### **Titelidee (Prozess-fokussiert)**

> "Incorporating dynamic land-use-sensitive interception and vegetation effects into mHM to assess hydrological impacts of land-cover change"

**Alternativ:**
> "Land use change impacts on catchment hydrology: A process-based approach with dynamic interception in mHM"

---

### **Kernfrage**

> Verbessert eine dynamische, LULC-sensitive Prozessrepräsentation in mHM die Simulation der hydrologischen Auswirkungen von Landnutzungsänderungen gegenüber einer statischen Standardkonfiguration?

---

### **Minimal belastbare Innovation**

| Element | Umsetzung |
|---------|-----------|
| **Dynamic LULC** | CORINE 1991-2020 (annual oder 6-year snapshots) |
| **Interception scheme** | LULC-class specific storage capacities (forest, grassland, cropland, urban) |
| **Optional** | Simple rooting depth / ET partitioning adjustment |
| **Comparison** | Standard mHM (static LULC) vs. Enhanced mHM (dynamic LULC + interception) |

---

### **Zielgrößen (Multi-Variable Evaluation)**

| Variable | Data Source | Purpose |
|----------|-------------|---------|
| **Discharge (Q)** | CAMELS-DE | Primary validation |
| **Soil Moisture (SM)** | mHM output + ESA CCI (optional) | Internal state validation |
| **Evapotranspiration (ET)** | mHM output + FLUXNET (optional) | ET partitioning validation |
| **Recharge** | mHM output + regional estimates (optional) | Subsurface response |

---

### **Szenarien**

**Historische LULC-Dynamik:**
- CORINE 1991, 2000, 2006, 2012, 2018, 2024 (6 snapshots)

**Idealisierte Szenarien:**
- **Afforestation:** Grassland → Forest
- **Deforestation:** Forest → Grassland
- **Urbanization:** Agricultural/Forest → Urban
- **Cropland ↔ Grassland:** Agricultural intensification/extensification
- **Conifer ↔ Deciduous:** Forest type change (via LAI/storage capacity)

---

### **Paper-Anspruch**

| Kriterium | Einschätzung |
|-----------|--------------|
| **Novelty** | ✅ Dynamic LULC + process-sensitive interception in mHM |
| **Rigor** | ✅ Multi-variable evaluation (Q, SM, ET, Recharge) |
| **Feasibility** | ✅ Implementable in mHM without full model overhaul |
| **Validation** | ✅ CAMELS-DE discharge + optional RS/flux data |
| **Publication** | ✅ Strong enough for J. Hydrology / HESS / Water Resources Research |

---

## 🎯 Wissenschaftlicher Mehrwert (Claim)

**Nicht:** "Landnutzungsänderung in mHM insgesamt"

**Sondern:** "Ein klar definierter LULC-sensitiver Prozess in mHM und seine hydrologischen Konsequenzen"

**Konkreter Claim:**
> "Ein verbessertes Interzeptionskonzept verändert nicht nur event-scale runoff, sondern auch saisonale ET-, Bodenfeuchte- und Recharge-Signale unter Landnutzungsänderung."

---

## 📋 Nächste Schritte (Implementation Roadmap)

### Phase 1: Design Finalization (2 weeks)
- [ ] Interception scheme specification (storage capacities per LULC class)
- [ ] Dynamic LULC timeline (CORINE years: 1991, 2000, 2006,12, 2018)
- [ ] mHM code changes scoped (which routines to modify)
- [ ] Validation metrics defined (KGE, NSE, bias for Q, SM, ET)

### Phase 2: Implementation (4-6 weeks)
- [ ] mHM interception module extension (LULC-class specific parameters)
- [ ] Dynamic LULC input handling (time-varying land use maps)
- [ ] Test domain runs (short validation)
- [ ] Catchment_custom runs (1991-2020, 30 years)

### Phase 3: Analysis (4 weeks)
- [ ] Static vs. Dynamic LULC comparison
- [ ] Scenario analysis (afforestation, deforestation, urbanization)
- [ ] Multi-variable evaluation (Q, SM, ET, Recharge)
- [ ] Process attribution (how much change due to interception vs. LULC extent)

### Phase 4: Writing (4 weeks)
- [ ] Introduction (Toosi 2025 + Bosch & Hewlett 1982 + Renner 2024)
- [ ] Methods (mHM modifications, LULC data, validation)
- [ ] Results (static vs. dynamic, scenarios, multi-variable eval)
- [ ] Discussion (process mechanisms, limitations, transferability)
- [ ] Conclusions (recommendations for LULC modeling)

---

## 🔗 Anschlussfähigkeit (Follow-Up Papers)

**Paper 2 (dieses):** Interception + Dynamic LULC

**Paper 3 (optional):**
- Runoff/Infiltration partitioning (LULC-sensitive roughness, infiltration capacity)
- Recharge focus (rooting depth, percolation coefficients)
- Energy partitioning (if ET datasets available)

**Paper 4 (optional):**
- Full LULC + Climate matrix design (like Park 2011, but with mHM)
- Multi-model ensemble (like Posada-Marín 2022)

---

## 📚 Key Literature Support

| Paper | Support For |
|-------|-------------|
| **Toosi et al. (2025)** | Conceptual basis: LULC processes underrepresented in models |
| **Bosch & Hewlett (1982)** | Benchmark: 40mm/10% cover change (validation target) |
| **Park et al. (2011)** | Design: LULC + Climate matrix, non-additive effects |
| **Renner et al. (2024)** | Regional context: Saxony catchments, forest regrowth effect |
| **Brown et al. (2005)** | Methodology: Paired catchment design principles |

---

**Last Updated:** 2026-03-12  
**Next Review:** After implementation scoping (mHM code changes defined)
