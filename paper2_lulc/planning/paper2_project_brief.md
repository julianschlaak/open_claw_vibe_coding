# Paper #2 Project Brief — mHM Landnutzungsänderungen

**Arbeitstitel:** Dynamische landnutzungssensitive Interzeption in mHM zur Analyse hydrologischer Auswirkungen von Landnutzungsänderungen

**Status:** Project Foundation Document  
**Created:** 2026-03-13  
**Author:** OpenClaw Research Agent (Helferchen)  
**Review:** Julian Schlaak

---

## EXECUTIVE SUMMARY

**Projekt:** Fokussiertes zweites PhD-Paper zu Landnutzungsänderungen in mHM

**Kernprozess:** Interzeption als landnutzungssensitiver Prozess

**Innovation:** Dynamische, LULC-sensitive Interzeptionsrepräsentation (nicht vollständige LULC-Modellierung)

**Forschungslücke:** Es fehlt eine systematische Untersuchung, wie eine dynamische, landnutzungssensitive Interzeptionsrepräsentation in mHM die Simulation hydrologischer Prozesse unter Landnutzungsänderung beeinflusst.

**Design:** 4 Modellkonfigurationen (M0: statisch, M1: dynamische LULC, M2: dynamisch + Interzeption, M3: Szenarien)

**Evaluation:** Mehrgrößen (Q, ET, SM, Recharge) — nicht nur Abfluss

**Raum:** Sachsen / 3-20 Catchments (nicht ganz Deutschland)

**Zeitrahmen:** 6-12 Monate

**Originalität:** Prozessbasierte Interzeption in mHM mit dynamischer LULC — nicht diagnostisch (Renner 2024), nicht irrigation-fokussiert (Koycegiz 2024)

**Realisierbarkeit:** ✅ Machbar innerhalb 6-12 Monaten bei Fokus auf Interzeption als Hauptprozess

---

## TEIL A – Projektfokus und wissenschaftliche Zuspitzung

### A.1 Arbeitstitel (3 Optionen)

| Option | Titel | Fokus |
|--------|-------|-------|
| **A** (empfohlen) | "Representing land-use-sensitive interception dynamics in mHM to assess hydrological impacts of land-cover change" | Prozess-fokussiert, stärkste Option |
| **B** | "Towards dynamic land-use representation in mHM: improving interception and vegetation controls under land-cover change" | Breiter (LULC + vegetation) |
| **C** | "Hydrological consequences of dynamic land-cover change in mHM: the role of interception, evapotranspiration, and recharge" | Wirkungskette betont |

---

### A.2 Zielsetzung (präzise formuliert)

**Übergeordnetes Ziel:**
> Entwicklung und Bewertung einer dynamischen, LULC-sensitiven Interzeptionsrepräsentation in mHM zur Verbesserung der hydrologischen Simulation unter Landnutzungsänderung.

**Explizite Eingrenzung:**

| Was ist KERN des Papers | Was ist bewusst AUSGESCHLOSSEN |
|-------------------------|-------------------------------|
| Interzeption als Hauptprozess | Vollständige Energiebilanz-Neuentwicklung |
| Dynamische LULC (CORINE 1991-2020) | Explizites Strahlungsmodell |
| LULC-spezifische Speicherkapazität | Komplexe Schnee-Canopy-Physik |
| Saisonale Variation (LAI-basiert) | Umfassende Wurzelphysik |
| Evaluation: Q, ET, SM, Recharge | Vollständige Infiltration/Grundwasser-Neuentwicklung |
| 3-20 sächsische Catchments | Bewässerung, Urbanhydrologie, Erosion |
| 6-12 Monate Entwicklung | Ganz Deutschland-Anwendung |

---

### A.3 Forschungslücke (präzise herausgearbeitet)

**Allgemeine Lücke (Toosi 2025):**
> LULC in hydrologischen Modellen wird zu stark vereinfacht (nicht nur Eingabedaten, vor allem Prozessrepräsentation). Kalibrierungs-Praxis: Parameter-Anpassung prioritär → guter Modell-Fit, aber LULC-Prozesse nicht physikalisch abgebildet.

**Spezifische Lücke (mHM-bezogen):**

| Aspekt | Status in aktueller Literatur | Paper #2 Beitrag |
|--------|-------------------------------|------------------|
| **Dynamische LULC in mHM** | Koycegiz 2024 zeigt Machbarkeit (Türkei, Irrigation) | ✅ Transfer auf Sachsen, Interzeption |
| **Diagnostische Attribution** | Renner 2024 (Sachsen, diagnostisch, nicht modellbasiert) | ✅ Prozessbasierte Simulation (nicht ex-post) |
| **Modellstruktur-Einfluss** | Posada-Marín 2022 (Meta-Analyse, Südamerika) | ✅ mHM-spezifisch, regional (Sachsen) |
| **Interzeption-spezifisch** | ❌ Keine mHM-Implementierung | ✅ LULC-sensitive Interzeption in mHM |

**Präzise Formulierung der Lücke:**
> Es fehlt eine systematische Untersuchung dazu, wie eine **dynamische, landnutzungssensitive Interzeptionsrepräsentation in mHM** die Simulation hydrologischer Prozesse unter Landnutzungsänderung beeinflusst. Insbesondere offen ist:
> 1. Ob dynamische LULC-Informationen allein schon einen messbaren Unterschied machen
> 2. Ob eine explizite Prozessverbesserung über Interzeption zusätzlichen Mehrwert bringt
> 3. Wie sich Änderungen auf mehrere Zielgrößen gleichzeitig auswirken
> 4. Welche Landnutzungsübergänge hydrologisch besonders relevant sind

---

### A.4 Forschungsfragen (geschärft)

| RQ | Frage | Literatur-Support |
|----|-------|-------------------|
| **RQ1** | Wie stark verändert eine dynamische landnutzungssensitive Interzeptionsrepräsentation in mHM die Partitionierung von Niederschlag in Interzeptionsverlust, Evapotranspiration, Bodenfeuchte, Abfluss und Recharge? | Toosi 2025 (4 Prozessgruppen), Bosch & Hewlett 1982 (water yield partitioning) |
| **RQ2** | Verbessert die dynamische LULC-sensitive Interzeptionsrepräsentation die gleichzeitige Reproduktion von Abfluss, Bodenfeuchte und Evapotranspiration im Vergleich zu (a) einer statischen Standardkonfiguration und (b) einer Konfiguration mit nur dynamischer LULC, aber ohne neue Interzeptionsprozessdarstellung? | Koycegiz 2024 (static vs. dynamic, Q similar but GW different), Posada-Marín 2022 (model structure matters) |
| **RQ3** | Wie sensitiv reagieren hydrologische Wasserhaushaltskomponenten auf unterschiedliche Typen von Landnutzungsänderung (Aufforstung, Entwaldung, Acker→Grünland, Grünland→Acker, Urbanisierung)? | Bosch & Hewlett 1982 (forest vs. open-land differences), Brown 2005 (paired catchment methodology) |

---

### A.5 Hypothesen (geschärft, literaturgestützt)

| H | Hypothese | Literatur-Support | Testbarkeit |
|---|-----------|-------------------|-------------|
| **H1** | Eine dynamische LULC-sensitive Interzeptionsdarstellung verändert die Niederschlagspartitionierung systematisch und führt zu plausiblen Änderungen in ET, Bodenwasser, Abfluss und Recharge. | Toosi 2025 (LULC affects all water balance components), Bosch & Hewlett 1982 (vegetation change → water yield change) | ✅ Testbar via M1 vs. M2 comparison (ET, SM, Q, Recharge) |
| **H2** | Die Kombination aus zeitvariabler LULC und LULC-sensitiver Interzeptionsdarstellung erhöht die Mehrgrößen-Konsistenz der Simulationen gegenüber einer statischen Standardkonfiguration und gegenüber einer Konfiguration mit nur dynamischer LULC. | Koycegiz 2024 (dynamic LULC improved GW anomalies, Q similar), Posada-Marín 2022 (model structure determines conclusions) | ✅ Testbar via M0 vs. M1 vs. M2 (multi-variable KGE/NSE) |
| **H3** | Waldbezogene Landnutzungsänderungen verursachen stärkere Änderungen in Interzeption und saisonaler Wasserbilanz als Übergänge zwischen Offenlandklassen. | Bosch & Hewlett 1982 (conifer 40mm/10% > hardwood 25mm > scrub 10mm), Renner 2024 (forest headwaters show stronger decline) | ✅ Testbar via M3 scenarios (forest→nonforest vs. cropland→grassland) |
| **H4** | Die hydrologischen Auswirkungen der Interzeptionsänderung sind standortabhängig und variieren in Abhängigkeit von Klima, Boden, Relief und Ausgangslandnutzung. | Renner 2024 (catchment-specific responses), Posada-Marín 2022 (context-dependent effects) | ✅ Testbar via catchment grouping (elevation, forest cover, aridity) |

---

### A.6 Wissenschaftliche Originalität und Realisierbarkeit

| Kriterium | Einschätzung | Begründung |
|-----------|--------------|------------|
| **Originalität** | ✅ Moderat bis hoch | Keine mHM-spezifische Interzeption-LULC-Implementierung publiziert (Koycegiz 2024: Irrigation, nicht Interception) |
| **Novelty** | ✅ Klar abgegrenzt | Prozessbasiert (nicht diagnostisch wie Renner 2024), mHM-spezifisch (nicht allgemein wie Toosi 2025) |
| **Realisierbarkeit** | ✅ Hoch (6-12 Monate) | Fokus auf einen Hauptprozess (Interzeption), nicht Total-Modellumbau |
| **Risiko** | ⚠️ Moderat (LULC-Datenkonsistenz, Parameter-Identifizierbarkeit) | Siehe TEIL F (Risiken) |
| **Publikations-Potenzial** | ✅ J. Hydrology / HESS / Water Resources Research | Strong enough for Q1 hydrology journal |

---

## TEIL B – Literaturbasierte Einordnung

### B.1 Literaturmatrix (strukturiert nach Funktion)

| Paper | Typ | Prozessfokus | LULC-Repräsentation | mHM-Relevanz | Paper #2 Funktion |
|-------|-----|--------------|---------------------|--------------|-------------------|
| **Toosi 2025** | Review | Alle 4 LULC-Prozessgruppen | Statisch (Kritikpunkt) | Allgemein | **Konzeptionelle Basis** (Introduction) |
| **Koycegiz 2024** | Modellstudie | Irrigation (anthropogen) | Dynamisch (MODIS annual) | ✅ mHM | **Methodischer Vorläufer** (Methods) |
| **Renner 2024** | Diagnostisch | ET, Q (Attribution) | Proxy (CORINE, forest damage) | ❌ Kein Modell | **Regionaler Kontext** (Study Area, Discussion) |
| **Posada-Marín 2022** | Meta-Analyse | ΔQ = ΔP - ΔE | Klassifikation (W-F, W+F, WO+F, O+F) | Allgemein | **Argumentation** (Introduction, Discussion) |
| **Bosch & Hewlett 1982** | Review (94 Catchments) | Water Yield, ET | Vegetation cover change | ❌ Pre-modelling | **Klassisches Fundament** (Introduction, Hypotheses) |
| **Brown 2005** | Review (paired catchments) | Water Yield | Vegetation alteration | ❌ Pre-modelling | **Methodik** (paired catchment design) |
| **Park 2011** | Modellstudie (SWAT) | Q, ET, Sediment | Dynamisch (CLUE-S) | ❌ SWAT | **Design-Blueprint** (LULC + Climate matrix) |
| **Matheussen 2000** | Modellstudie (VIC) | Q, ET | Vegetation change | ❌ VIC (≈ mHM) | **Modell-Präzedenz** (distributed LULC effects) |
| **Oudin 2018** | Modellstudie | Q, ET | Urbanization | ❌ GR4J | **Complement** (urban LULC effects) |
| **Babaremu 2024** | Review | LULC + Hydrology | Unklar | ❌ Unklar | ⏳ PDF nötig (TBD) |
| **Hou 2023** | Synthesis | Forestation/Deforestation | Global | ❌ Allgemein | ⏳ PDF nötig (TBD) |
| **Teuling 2019** | Europa-scale | Drought + Vegetation | LULC + Climate | ❌ Allgemein | ⏳ PDF nötig (TBD) |
| **Cai 2019** | Modellstudie | Deforestation effects | LULC + Climate feedback | ❌ Allgemein | ⏳ PDF nötig (TBD) |

---

### B.2 Literatur nach Funktion geordnet

#### **Review / Überblick:**
- Toosi 2025 (LULC processes underrepresented)
- Brown 2005 (paired catchment methodology)
- Bosch & Hewlett 1982 (classical catchment evidence)

#### **Empirische Evidenz:**
- Bosch & Hewlett 1982 (94 catchments, 40mm/10% benchmark)
- Renner 2024 (Saxony, 71 catchments, forest regrowth effect)

#### **Hydrologische Modellierung:**
- Koycegiz 2024 (mHM, dynamic LULC, irrigation)
- Park 2011 (SWAT, LULC + Climate matrix)
- Matheussen 2000 (VIC, distributed LULC effects)
- Oudin 2018 (GR4J, urbanization)

#### **mHM-spezifische Relevanz:**
- **Koycegiz 2024** ✅ (direct mHM precedent)
- Alle anderen: ❌ (nicht mHM)

#### **Direkt übertragbare Ideen:**

| Paper | Idee | Paper #2 Transfer |
|-------|------|-------------------|
| Koycegiz 2024 | Static vs. Dynamic LULC comparison | M0 vs. M1 vs. M2 design |
| Koycegiz 2024 | Multi-variable evaluation (Q + GW) | Q + ET + SM + Recharge |
| Renner 2024 | 71 Saxony catchments | Same region, subset selection |
| Posada-Marín 2022 | Model structure determines conclusions | Justifies M0/M1/M2 comparison |
| Bosch & Hewlett 1982 | 40mm/10% forest benchmark | H3 justification, validation target |

---

### B.3 Literatur nach Paper #2 Section geordnet

| Section | Papers (priorisiert) |
|---------|---------------------|
| **Introduction** | Toosi 2025, Posada-Marín 2022, Bosch & Hewlett 1982, Renner 2024 |
| **Study Area** | Renner 2024 (Saxony catchments), Koycegiz 2024 (LULC data approach) |
| **Methods** | Koycegiz 2024 (mHM dynamic LULC), Brown 2005 (paired design), Park 2011 (matrix) |
| **Hypotheses** | Bosch & Hewlett 1982 (H3 benchmark), Toosi 2025 (H1, H2) |
| **Results** | Koycegiz 2024 (multi-variable logic), Renner 2024 (catchment contrast) |
| **Discussion** | Posada-Marín 2022 (model structure), Toosi 2025 (process representation), Renner 2024 (regional context) |

---

### B.4 Was Literatur wirklich zeigt vs. was abgeleitet wird

| Paper | Was wirklich gezeigt | Was für Paper #2 abgeleitet |
|-------|---------------------|----------------------------|
| **Koycegiz 2024** | Dynamic LULC in mHM improves GW anomalies (R²=0.84), Q similar | ✅ Transfer: Dynamic LULC + Interception may improve ET/SM/Recharge |
| **Renner 2024** | LULC effects detectable diagnostically in Saxony (forest regrowth → ET↑) | ✅ Transfer: Process-based simulation should capture this effect |
| **Posada-Marín 2022** | Model structure determines ΔQ sign (W-F vs. WO+F opposite conclusions) | ✅ Transfer: M0 vs. M2 may show different multi-variable consistency |
| **Bosch & Hewlett 1982** | Forest reduction → water yield ↑ (40mm/10% conifer) | ✅ Transfer: H3 (forest changes > open-land changes) |
| **Toosi 2025** | LULC processes underrepresented in models | ✅ Transfer: Justifies interception module addition |

---

## TEIL C – Paperdesign

### C.1 Paperstruktur (IMRaD)

| Abschnitt | Länge (ca.) | Zentrale Botschaft | Literatur | Figuren / Tabellen |
|-----------|-------------|-------------------|-----------|-------------------|
| **1. Introduction** | 4-5 Seiten | LULC affects hydrology, but model structure matters (Toosi, Posada-Marín). Regional evidence from Saxony (Renner). Gap: no process-based mHM implementation. | Toosi 2025, Posada-Marín 2022, Renner 2024, Bosch & Hewlett 1982 | - |
| **2. Study Area & Data** | 3-4 Seiten | Saxony catchments (3-20), CORINE 1991-2024, CAMELS-DE discharge, forcing data. | Renner 2024 (catchment selection), Koycegiz 2024 (LULC approach) | Table 1: Catchment characteristics, Fig. 1: Study area map, LULC timeline |
| **3. Methods** | 5-6 Seiten | mHM configurations (M0-M3), interception scheme, LULC handling, metrics, evaluation design. | Koycegiz 2024 (mHM dynamic LULC), Brown 2005 (comparison design) | Table 2: M0-M3 specifications, Fig. 2: Interception scheme diagram, Table 3: Metrics |
| **4. Results** | 6-8 Seiten | M0 vs. M1 vs. M2 comparison, scenario results (M3), multi-variable evaluation, catchment contrast. | - | Fig. 3-7: Results panels (Q, ET, SM, Recharge), Table 4: Performance metrics |
| **5. Discussion** | 4-5 Seiten | Process mechanisms, comparison to literature (Bosch benchmark, Renner attribution), limitations, transferability. | Bosch & Hewlett 1982, Renner 2024, Posada-Marín 2022, Koycegiz 2024 | Fig. 8: Benchmark comparison, Table 5: Literature synthesis |
| **6. Conclusions** | 2-3 Seiten | Key findings, recommendations for LULC modeling in mHM, future work. | - | - |
| **Supplement** | Variable | Additional figures, catchment tables, parameter values. | - | Tables S1-S5, Figures S1-S10 |

---

### C.2 Storyline (rote Faden)

**Narrative:**
1. **Problem:** LULC affects hydrology (Bosch & Hewlett 1982, Toosi 2025), but models treat LULC statically or implicitly (Posada-Marín 2022)
2. **Regional evidence:** Saxony shows LULC effects diagnostically (Renner 2024), but no process-based simulation
3. **mHM precedent:** Dynamic LULC feasible in mHM (Koycegiz 2024), but irrigation-focused, not interception
4. **Gap:** No systematic investigation of LULC-sensitive interception in mHM
5. **Our approach:** M0 (static) vs. M1 (dynamic LULC) vs. M2 (dynamic + interception) vs. M3 (scenarios)
6. **Evaluation:** Multi-variable (Q, ET, SM, Recharge) — not just Q (Koycegiz lesson)
7. **Results:** M2 improves multi-variable consistency, especially ET/SM/Recharge (not necessarily Q)
8. **Implications:** Process-based interception matters for LULC change simulation in mHM

---

### C.3 Wichtigste Reviewer-Fragen (vorab identifiziert)

| Frage | Antwort-Strategie | Literatur-Support |
|-------|-------------------|-------------------|
| **"Warum Interzeption und nicht anderer Prozess?"** | Interception is one of 4 LULC-sensitive process groups (Toosi 2025), directly LULC-dependent, implementable without full model overhaul | Toosi 2025, Koycegiz 2024 (pragmatic addition) |
| **"Q bleibt ähnlich — warum dann neue Komplexität?"** | Koycegiz 2024 showed Q similar but GW improved. Multi-variable evaluation essential (ET, SM, Recharge show effect) | Koycegiz 2024, Posada-Marín 2022 |
| **"Sind 3-20 Catchments genug?"** | Renner 2024 used 71, but we focus on process mechanism, not spatial exhaustiveness. 3-5 pilot + 5-20 expansion is feasible | Renner 2024, Brown 2005 (paired design) |
| **"LULC-Datenkonsistenz über 1991-2024?"** | CORINE harmonization critical (acknowledged limitation). Same classification, projection, resolution enforced | Koycegiz 2024 (MODIS harmonization) |
| **"Equifinalität / Überparametrisierung?"** | Minimal parameter set (storage capacity per LULC, seasonal LAI variation). Not full canopy physics | Koycegiz 2024 (pragmatic approach) |
| **"Vergleich zu Bosch & Hewlett benchmark (40mm/10%)?"** | Our process-based approach enables forward simulation, not just observation. Benchmark used for discussion validation | Bosch & Hewlett 1982 |
| **"Warum nicht ganz Deutschland?"** | Feasibility (6-12 months), process focus over spatial exhaustiveness. Transferability discussed | Renner 2024 (regional focus) |

---

## TEIL D – Modell- und Experimentdesign

### D.1 Modellkonfigurationen (M0-M3)

| ID | Name | LULC | Interception | Zweck |
|----|------|------|--------------|-------|
| **M0** | Static Reference | Static (single year, e.g., 2018) | Standard mHM | Referenz (current practice) |
| **M1** | Dynamic LULC | Dynamic (CORINE 1991, 2000, 2006, 2012, 2018, 2024) | Standard mHM | Effekt der bloßen LULC-Aktualisierung |
| **M2** | Dynamic + Interception | Dynamic (same as M1) | **LULC-sensitive interception** | **Hauptmodell** (Prozessverbesserung) |
| **M3** | Scenarios | Idealized transitions | Same as M2 | Sensitivität (Aufforstung, Entwaldung, Acker↔Grünland, Urbanisierung) |

---

### D.2 Was sich zwischen M0, M1, M2 genau ändert

| Aspekt | M0 → M1 | M1 → M2 | M0 → M2 |
|--------|---------|---------|---------|
| **LULC input** | Static → Dynamic | Unchanged (both dynamic) | Static → Dynamic |
| **Interception scheme** | Unchanged (standard) | Standard → LULC-sensitive | Standard → LULC-sensitive |
| **Parameters** | Unchanged | New: S_max per LULC, LAI seasonal | New: S_max per LULC, LAI seasonal + dynamic LULC |
| **Expected effect** | Small (LULC extent only) | Moderate (process addition) | Largest (combined) |
| **Primary signal** | LULC extent change | Interception-mediated ET/SM/Recharge | Combined extent + process |

---

### D.3 Minimalversion des Interzeptionsschemas

**Parameter (minimal, identifizierbar):**

| Parameter | Beschreibung | Werte (Beispiel) | Quelle |
|-----------|--------------|------------------|--------|
| **S_max (mm)** | Maximaler Interzeptionsspeicher pro LULC-Klasse | Forest: 2-4 mm, Grassland: 0.5-1 mm, Cropland: 0.3-0.8 mm, Urban: 0.1-0.3 mm | Literatur (Bosch & Hewlett, interception literature) |
| **LAI_seasonal** | Monatliche LAI-Variation pro LULC-Klasse | Forest: 3-6 (summer), 1-3 (winter); Grassland: 1-4; Cropland: 0.5-5 (growing season) | CORINE + MODIS LAI |
| **Evaporation rate** | Interzeptionsverdunstungsrate | Forest: higher (canopy exposure), Open-land: lower | Standard mHM ET routine |

**Prozess-Logik:**
```
For each timestep:
  P_throughfall = P - (Interception_storage_change + Interception_evaporation)
  Interception_storage = min(S_max[LULC], cumulative_P)
  Interception_evaporation = f(LAI_seasonal, PET, S_current)
```

---

### D.4 Risiken (Equifinalität, Überparametrisierung)

| Risiko | Beschreibung | Gegenmaßnahme |
|--------|--------------|---------------|
| **Equifinalität** | Verschiedene S_max-Kombinationen produzieren ähnliche Q/ET | Multi-variable constraint (Q + ET + SM), nicht nur Q |
| **Überparametrisierung** | Zu viele LULC-Klassen (10+) mit je eigenen Parametern | Aggregation (Forest, Grassland, Cropland, Urban — 4 Klassen) |
| **LULC-Dateninkonsistenz** | CORINE class jumps (classification artifacts, not real change) | Harmonization rules, smoothing, quality flags |
| **Q nicht sensitiv** | Interception effect not visible in Q (Koycegiz lesson) | Primary evaluation: ET, SM, Recharge; Q secondary |
| **Skalen-Mismatch** | LULC resolution vs. mHM resolution vs. forcing resolution | Consistent resolution enforced (e.g., 1km × 1km) |

---

## TEIL E – Daten- und Untersuchungsraumstrategie

### E.1 Untersuchungsraum (Sachsen / Pilot-Catchments)

**Kriterien für Catchment-Auswahl:**

| Kriterium | Anforderung | Begründung |
|-----------|-------------|------------|
| **Waldanteil** | Kontrast: 0-30% (low), 30-60% (medium), 60-90% (high) | H3 test (forest vs. open-land) |
| **Landwirtschaft** | Kontrast: Acker-dominant vs. Grünland-dominant | RQ3 test (Acker↔Grünland) |
| **Urbanisierung** | Gradient: rural → suburban → urban | RQ3 test (Urbanization effect) |
| **Relief** | Niedrigland vs. Mittelgebirge (Erzgebirge) | H4 test (context-dependence) |
| **Abflussdaten** | CAMELS-DE verfügbar (quality-checked) | Q evaluation mandatory |
| **Größe** | 50-500 km² (mesoscale, mHM-appropriate) | Feasibility, not too large |

**Vorschlag:**
- **Phase 1:** 3-5 Pilot-Catchments (high contrast: forest, agricultural, urban, lowland, highland)
- **Phase 2:** 5-20 Catchments (expansion, regional coverage)

---

### E.2 LULC-Daten (CORINE 1991-2024)

**Anforderungen:**

| Anforderung | Risiko bei Verletzung | Gegenmaßnahme |
|-------------|----------------------|---------------|
| **Gleiche Klassenlogik** | Künstliche Sprünge (class redefinition) | CORINE version harmonization (1991, 2000, 2006, 2012, 2018, 2024) |
| **Gleiche räumliche Auflösung** | Skaleneffekte, Artefakte | Resampling to consistent resolution (e.g., 1km) |
| **Gleiche Projektion** | Georegistration errors | UTM Zone 33N (Saxony standard) |
| **Robustes Mapping auf mHM-Parameter** | Fehlklassifikation → falsche Parameter | Lookup table (CORINE class → mHM LULC class → S_max, LAI) |
| **Keine Datensatzartefakte** | False trends (classification change, not real LULC change) | Quality control, visual inspection, smoothing rules |

**Empfehlung:**
- CORINE Land Cover (1991, 2000, 2006, 2012, 2018, 2024) — 6 snapshots
- Optional: Annual interpolation (between snapshots) — but higher uncertainty
- LAI: MODIS MOD15A2H (monthly, 500m) — downscaled/averaged to mHM resolution

---

### E.3 Datenlücken und kritische Unsicherheiten

| Datenquelle | Lücke / Unsicherheit | Auswirkung | Umgang |
|-------------|---------------------|------------|--------|
| **CORINE** | 6-year snapshots (not annual) | Interpolation uncertainty between snapshots | Linear interpolation or step-function (documented) |
| **LAI (MODIS)** | 2000+ only (not 1991-1999) | Early period LAI uncertain | Climatology (2000-2020 average) for 1991-1999 |
| **CAMELS-DE** | 456 catchments, but not all Saxony | Some catchments may lack Q data | Subset selection (Saxony + quality) |
| **ET (FLUXNET)** | Sparse in Saxony | ET validation limited | mHM output intercomparison, optional FLUXNET sites |
| **Recharge** | No direct observations | Recharge evaluation uncertain | mHM output, regional estimates (literature) |
| **Soil Moisture (ESA CCI)** | 1978+, but coarse resolution (25km) | SM validation at catchment scale limited | mHM output intercomparison, optional in-situ |

---

## TEIL F – Arbeitsplan (6-12 Monate)

### F.1 Arbeitspakete (AP)

| AP | Titel | Dauer | Ziel | Zwischenschritte | Erwartete Ergebnisse | Größte Risiken |
|----|-------|-------|------|------------------|---------------------|----------------|
| **AP1** | Literatur + Konzeptfinalisierung | 4-6 Wochen | 2-3 Seiten internes Konzept + Parameter-Mapping | - LULC-Prozess-Review (Toosi, Bosch, Koycegiz)<br>- Interception scheme spec<br>- mHM code scope | Concept paper, parameter table, M0-M3 spec | Scope creep (adding too many processes) |
| **AP2** | Datenaufbereitung | 4-8 Wochen | Reproduzierbarer Preprocessing-Workflow | - CORINE download + harmonization<br>- Catchment selection (3-5 pilot)<br>- LULC→mHM mapping table | LULC time series (1991-2024), catchment masks, mapping table | CORINE inconsistencies, classification artifacts |
| **AP3** | mHM-Implementierung | 6-10 Wochen | Stabile Modellversion + Testläufe | - Interception module coding (Fortran/Python)<br>- nml file extensions<br>- Test domain runs | mHM code (interception extension), test output | Code bugs, mass balance errors, performance issues |
| **AP4** | Kalibrierung + Experimente | 6-10 Wochen | Vollständiges Experiment-Set (M0-M3) | - M0 calibration (DDS, KGE)<br>- M1 runs (dynamic LULC)<br>- M2 runs (dynamic + interception)<br>- M3 scenarios | Simulation output (M0-M3, all catchments, 1991-2020) | Computational time, calibration non-convergence |
| **AP5** | Auswertung | 4-8 Wochen | Figure package + Ergebnisstruktur | - Multi-variable evaluation (Q, ET, SM, Recharge)<br>- M0 vs. M1 vs. M2 comparison<br>- Scenario analysis (M3) | Performance metrics, comparison figures, scenario results | Q shows no difference (need ET/SM/Recharge focus) |
| **AP6** | Schreiben | 4-6 Wochen | Erste vollständige Paper-Version | - IMRaD draft<br>- Supplement<br>- Co-author review | Full paper draft (8000-10000 words) | Writer's block, co-author delays |

**Summe:** 6-12 Monate (abhängig von Catchment-Anzahl, Datenverfügbarkeit, Code-Komplexität)

---

### F.2 Kritische Meilensteine

| Meilenstein | Zeitpunkt | Deliverable | Go/No-Go Kriterium |
|-------------|-----------|-------------|-------------------|
| **M1: Konzept final** | Ende AP1 | Concept paper (2-3 pages) | ✅ Clear scope (interception only, not full LULC overhaul) |
| **M2: LULC-Daten ready** | Ende AP2 | CORINE time series (1991-2024), catchment masks | ✅ Consistent (no major artifacts, harmonized) |
| **M3: mHM code stable** | Ende AP3 | mHM with interception module, test runs pass | ✅ Mass balance closed, no crashes |
| **M4: Experiments complete** | Ende AP4 | M0-M3 output (all catchments, 1991-2020) | ✅ All runs finished, output files valid |
| **M5: Results clear** | Ende AP5 | Performance metrics, comparison figures | ✅ M2 shows improvement in ET/SM/Recharge (not necessarily Q) |
| **M6: Paper draft** | Ende AP6 | Full paper draft | ✅ IMRaD complete, supplement ready |

---

## TEIL G – Konkrete nächste Entscheidungen

### G.1 Unmittelbare Entscheidungen (5-10)

| # | Entscheidung | Optionen | Empfehlung | Begründung |
|---|--------------|----------|------------|------------|
| **1** | **LULC-Datenbasis** | CORINE (6-year) vs. MODIS (annual) vs.混合 | ✅ **CORINE 1991-2024 (6 snapshots)** | Consistent classification, Saxony-appropriate, Koycegiz used MODIS but CORINE better for Europe |
| **2** | **Catchments** | 3-5 pilot vs. 5-20 full vs. 71 (Renner) | ✅ **3-5 pilot (Phase 1), then 5-20 (Phase 2)** | Feasibility (6-12 months), process focus over spatial exhaustiveness |
| **3** | **Zielgrößen** | Q only vs. Q+ET vs. Q+ET+SM+Recharge | ✅ **Q+ET+SM+Recharge** | Koycegiz lesson: Q alone insufficient, multi-variable essential |
| **4** | **Interzeptionsschema** | Minimal (4 classes) vs. Extended (Laub/Nadel split) | ✅ **Minimal (4 classes: Forest, Grassland, Cropland, Urban)** | Identifiability, not over-parameterized; Laub/Nadel optional Phase 2 |
| **5** | **LAI-Variation** | Monthly MODIS vs. Seasonal climatology | ✅ **Seasonal climatology (3-month: DJF, MAM, JJA, SON)** | Simpler, fewer parameters; MODIS only 2000+ (gap 1991-1999) |
| **6** | **mHM Code** | Fortran extension vs. Python wrapper vs. nml-only | ✅ **nml + parameter table extension** (minimal code change) | Koycegiz showed nml changes feasible; avoid full Fortran rewrite |
| **7** | **Kalibrierung** | M0 only vs. M0+M1 vs. M0+M1+M2 | ✅ **M0 only** (M1, M2 use M0 parameters, only LULC/interception differ) | Identifiability; calibrating all separately introduces confounding |
| **8** | **Periode** | 1991-2020 (30y) vs. 2000-2020 (20y, LAI available) | ✅ **1991-2020 (30y)** | Consistent with CAMELS-DE, Renner 2024; LAI climatology for 1991-1999 |
| **9** | **Journal** | HESS vs. J. Hydrology vs. WRR | ✅ **HESS** (Hydrology and Earth System Sciences) | Open access, fast review, process-focused, Renner 2024 published here |
| **10** | **Sub-Agent** | Research assistant for literature vs. manual | ✅ **Manual** (literature complete) | 6 papers fully analyzed (Toosi, Koycegiz, Renner, Posada-Marín, Bosch, Park); remaining 4 optional |

---

### G.2 Priorisierte nächste Schritte (sofort)

| Priorität | Schritt | Dauer | Deliverable |
|-----------|---------|-------|-------------|
| **1** | **Interception parameter table** (S_max per LULC, LAI seasonal) | 1 week | Parameter table (Forest, Grassland, Cropland, Urban) |
| **2** | **CORINE download + harmonization** (1991, 2000, 2006, 2012, 2018, 2024) | 2 weeks | LULC time series (GeoTIFF/ASC, consistent projection) |
| **3** | **Catchment selection** (3-5 pilot from CAMELS-DE, Saxony) | 1 week | Catchment list (IDs, characteristics, forest cover, elevation) |
| **4** | **mHM nml review** (which files to extend for LULC/interception) | 1 week | nml change spec (mhm.nml, mhm_parameter.nml) |
| **5** | **Exposé draft** (Introduction, Methods, RQs, Hypotheses) | 2 weeks | 4-6 pages (for supervisor review) |

---

## ANHANG: Tabellen

### Tabelle 1: M0-M3 Spezifikation

| Aspekt | M0 (Static) | M1 (Dynamic LULC) | M2 (Dynamic + Interception) | M3 (Scenarios) |
|--------|-------------|-------------------|----------------------------|----------------|
| **LULC input** | Single year (e.g., 2018) | CORINE 1991, 2000, 2006, 2012, 2018, 2024 | Same as M1 | Idealized transitions |
| **Interception** | Standard mHM | Standard mHM | LULC-sensitive (S_max per class) | Same as M2 |
| **LAI** | Static (climatology) | Static (climatology) | Seasonal (per LULC class) | Same as M2 |
| **Parameters** | Standard mHM | Standard mHM | + S_max (4 values), LAI_seasonal (4×4) | Same as M2 |
| **Purpose** | Reference | LULC extent effect | Process effect | Scenario sensitivity |
| **Comparison** | Baseline | vs. M0 | vs. M0, M1 | vs. M2 (baseline) |

---

### Tabelle 2: Projektrisiken

| Risiko | Wahrscheinlichkeit | Auswirkung | Gegenmaßnahme |
|--------|-------------------|------------|---------------|
| **LULC-Dateninkonsistenz** | Moderat | Hoch (false trends) | Harmonization rules, quality control, visual inspection |
| **Q zeigt keinen Unterschied** | Hoch | Moderat (expected per Koycegiz) | Multi-variable focus (ET, SM, Recharge primary) |
| **Equifinalität** | Moderat | Hoch (unidentifiable parameters) | Multi-variable constraint, minimal parameter set (4 classes) |
| **Code-Bugs / Mass balance** | Moderat | Hoch (simulation failure) | Test domain runs, mass balance check, incremental testing |
| **Scope creep** | Hoch | Hoch (project becomes too large) | Strict focus on interception (not energy, snow, roots, infiltration) |
| **Computational time** | Moderat | Moderat (delays) | Parallel runs, test domain first, 3-5 catchments before 5-20 |
| **Co-author delays** | Moderat | Moderat (writing delays) | Early draft (AP6), buffer time |

---

### Tabelle 3: Literatur-Support pro Paper Section

| Section | Primary Papers | Secondary Papers | Support Type |
|---------|---------------|------------------|--------------|
| **Introduction** | Toosi 2025, Posada-Marín 2022, Renner 2024 | Bosch & Hewlett 1982, Brown 2005 | Conceptual, Argumentation, Regional |
| **Study Area** | Renner 2024 | Koycegiz 2024 | Catchment selection, LULC approach |
| **Methods** | Koycegiz 2024 | Brown 2005, Park 2011 | mHM precedent, Comparison design |
| **Hypotheses** | Bosch & Hewlett 1982 | Toosi 2025, Renner 2024 | Benchmark, Process rationale |
| **Results** | Koycegiz 2024 | Renner 2024 | Multi-variable logic, Catchment contrast |
| **Discussion** | Posada-Marín 2022, Toosi 2025 | Bosch & Hewlett 1982, Kida 2024 | Model structure, Process representation, Benchmark |

---

**Last Updated:** 2026-03-13  
**Next:** Commit + Push, then use as foundation for Exposé draft (AP1/AP6)
