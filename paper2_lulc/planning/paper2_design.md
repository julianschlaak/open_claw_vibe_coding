# Paper #2 Design — Realistic Scope (Based on Toosi 2025 Review)

**Created:** 2026-03-12  
**Updated:** 2026-03-12 (21:35 CET) — Full Paper Sketch Added  
**Source:** Toosi et al. (2025) Review + Julian's Strategic Assessment + Detailed Paper Concept  
**Status:** Ready for Implementation Scoping

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

## 📝 Vollständige Paper-Skizze (6-12 Monate Plan)

### 🏷️ Titel-Optionen

| Option | Titel | Fokus |
|--------|-------|-------|
| **A** (empfohlen) | "Representing land-use-sensitive interception dynamics in mHM to assess hydrological impacts of land-cover change" | Prozess-fokussiert, stärkste Option |
| **B** | "Towards dynamic land-use representation in mHM: improving interception and vegetation controls under land-cover change" | Breiter (LULC + vegetation) |
| **C** | "Hydrological consequences of dynamic land-cover change in mHM: the role of interception, evapotranspiration, and recharge" | Wirkungskette betont |

---

### 💡 Kernidee

**Nicht:** Vollständige neue Landoberflächenphysik in mHM

**Sondern:** Klar abgegrenzter, LULC-sensitiver Prozessbaustein — **Interzeption** — und Prüfung der Auswirkungen auf ET, Bodenfeuchte, Abfluss, Recharge unter Landnutzungsänderung.

**Anschluss an Toosi 2025 Review:**
- LULC beeinflusst hydrologische Prozesse stark
- Viele Modelle stellen Prozesse nur vereinfacht dar
- Kalibrierung verdeckt oft Prozessdefizite
- Interzeption = eine der 4 zentralen LULC-sensitiven Prozessgruppen

---

### 🔍 Forschungslücke

**Allgemein:**
- Hydrologische Modelle behandeln Landnutzung oft: **statisch** oder **indirekt über pauschale Parameter**
- Prozessänderungen unter Landnutzungswechsel unzureichend repräsentiert
- Toosi 2025 Kritik: Statt Prozessrepräsentation zu verbessern, wird oft nur nachkalibriert

**Spezifisch (Interzeption):**
- Laut Review häufig als **einfacher Speicher** dargestellt
- Stark über **LAI vereinfacht**
- Struktur vegetierter Systeme (canopy, trunk, understory, litter) unberücksichtigt
- Besonders für **Wälder, saisonale Unterschiede, veränderte Vegetationsbedeckung** unzureichend

**In mHM-Sprache:**
> Es fehlt eine systematische Untersuchung, wie eine dynamische, landnutzungssensitive Interzeptionsrepräsentation in mHM die Simulation von Wasserhaushaltskomponenten unter Landnutzungsänderung beeinflusst.

---

### ❓ Forschungsfragen (max. 3)

| RQ | Frage |
|----|-------|
| **RQ1** | Wie stark verändert eine dynamische, LULC-sensitive Interzeptionsrepräsentation in mHM die simulierte Partitionierung von Niederschlag in Interzeptionsverlust, Transpiration, Bodenfeuchte, Abfluss und Recharge? |
| **RQ2** | Verbessert eine solche Prozessrepräsentation die Konsistenz zwischen mehreren Beobachtungsgrößen gegenüber einer Standardkonfiguration mit statischer oder vereinfachter Landnutzungsdarstellung? |
| **RQ3** | Wie sensitiv sind hydrologische Wirkungen gegenüber unterschiedlichen Typen von Landnutzungsänderung (Aufforstung, Entwaldung, Acker-Grünland-Umwandlung, Urbanisierung)? |

---

### 🎯 Hypothesen

| H | Hypothese | Toosi 2025 Anschluss |
|---|-----------|---------------------|
| **H1** | Eine dynamische LULC-sensitive Interzeptionsdarstellung erhöht die realistische Verdunstung aus Niederschlagsrückhalt und verändert dadurch systematisch die Aufteilung zwischen aET, Bodenwasser, Abfluss und Recharge. | - |
| **H2** | Die Berücksichtigung zeitlich veränderlicher Landnutzung reduziert Kompensationsfehler in der Kalibrierung und verbessert die Mehrgrößen-Konsistenz gegenüber einer statischen Standardkonfiguration. | ✅ Direkt an Review-Kritik (Parameteranpassung ≠ Prozessverbesserung) |
| **H3** | Waldbezogene Landnutzungsänderungen erzeugen stärkere Änderungen in Interzeption und saisonaler Wasserbilanz als reine Verschiebungen zwischen Offenlandklassen. | - |
| **H4** | Die Auswirkungen auf Recharge und Abfluss sind nicht überall gleich, sondern hängen von Klima, Boden, Relief und bestehender Vegetationsstruktur ab. | ✅ Review: LULC-Wirkungen sind kontext- und skalenabhängig |

---

### 🔧 mHM-Änderungen (Minimal Innovation)

**Empfohlene Minimalinnovation:**
- Zeitvariable LULC-Klassen
- LULC-spezifische Interzeptionsspeicherkapazität
- Saisonale Variation der Speicherkapazität
- Getrennte Behandlung für: **Wald, Grünland, Acker, versiegelte/urbane Flächen**

**Gute, aber realistische Erweiterung:**
- Zweiter Speicher für **litter / forest floor** (bei Waldklassen)
- Unterscheidung **Laubwald / Nadelwald**
- Einfacher **Winter-/Sommer-Modus**

**❌ Nicht in Paper 2:**
- Explizites Strahlungsmodell
- Volles Canopy-Physik-Modell
- Eigener Schneekronenspeicher mit kompletter Energiebilanz
- Komplexe Wurzelphysik
- Gleichzeitige komplette Infiltrations- und Groundwater-Neuentwicklung

---

### 🧪 Methodisches Studiendesign

**4 Modellkonfigurationen:**

| ID | Konfiguration | Zweck |
|----|---------------|-------|
| **M0** | Standard-mHM (bisherige/statische LULC) | Referenz |
| **M1** | Dynamische LULC ohne Prozessänderung | Effekt der bloßen LULC-Aktualisierung |
| **M2** | Dynamische LULC + neues Interzeptionsschema | **Hauptmodell** (Prozessverbesserung) |
| **M3** | Sensitivitäts-/Szenarioversion | Idealisierte Szenarien (Aufforstung, Entwaldung, Acker→Grünland, Urbanisierung) |

**Unterscheidung ermöglicht:**
- Effekt der bloßen Aktualisierung von LULC-Daten
- Effekt der wirklichen Prozessverbesserung

---

### 📊 Beobachtungs- und Bewertungsgrößen

**Minimum:**
- Discharge (Q)
- Soil Moisture (SM)
- Evapotranspiration (ET)

**Optional (belastbar):**
- Recharge product / groundwater recharge estimate
- TWS / GRACE (nur großräumig)
- Schnee (nur wenn Untersuchungsraum passt)

**Kennzahlen:**

| Variable | Metriken |
|----------|----------|
| **Q** | KGE, NSE, logNSE, FHV/FLV (high-/low-flow-spezifisch) |
| **SM / ET** | KGE, RMSE, Bias, saisonale Anomalien, event/saisonale Dynamik |
| **Water Balance** | P, aET, Q, Recharge, dS |

---

### 🗺️ Untersuchungsraum

**Empfehlung:** Sachsen oder ausgewählte sächsische / ostdeutsche Catchments

**Kriterien:**
- Brauchbare Abflussdaten
- Bodenfeuchtebezug
- ET-Datensätze
- Landnutzungsdaten über mehrere Zeitpunkte

**Größe:** 5–20 gut charakterisierte Catchments oder regionaler Verbund mit Kontrast in Wald, Landwirtschaft, Urbanisierung

**Nicht zu groß:** Nicht sofort ganz Deutschland bei gleichzeitiger mHM-Code-Entwicklung

---

### 📁 Datenseite (Pflicht + Hilfreich)

| Kategorie | Pflicht | Sehr hilfreich |
|-----------|---------|----------------|
| **Meteorologie** | Forcing-Datensatz | - |
| **Boden** | Statische Bodendaten / Topographie | - |
| **LULC** | LULC-Zeitstände oder jährliche LULC-Daten | LULC-Transitionskarten |
| **Q** | Abflussdaten | - |
| **ET** | ET-Datensatz | FLUXNET |
| **SM** | SM-Datensatz oder Referenzprodukte | ESA CCI |
| **Vegetation** | - | Waldtyp-Informationen, Fraktion Laub/Nadel, LAI-Produkte |

**Kritischer Punkt:**
> Die größte praktische Schwierigkeit wird wahrscheinlich nicht mHM-Code, sondern eine konsistente zeitlich variable LULC-Datenbasis: gleiche Klassendefinitionen, gleiche Projektion/Auflösung, keine chaotischen Klassensprünge, klare Regel wie Klassen in mHM-Parameter übersetzt werden.

---

### ⏱️ Realistischer Ablauf (6-12 Monate)

| Phase | Dauer | Deliverable |
|-------|-------|-------------|
| **1. Literatur + Konzept** | 4-6 Wochen | 2-3 Seiten internes Konzept + Parameter-Mapping |
| **2. Datenaufbereitung** | 4-8 Wochen | Reproduzierbarer Preprocessing-Workflow (LULC harmonisieren, Klassenmapping) |
| **3. mHM-Implementierung** | 6-10 Wochen | Stabile Modellversion + Testläufe (neue Interzeptionsroutine) |
| **4. Kalibrierung + Experimente** | 6-10 Wochen | Vollständiges Experiment-Set (M0-M3, Sensitivitätsanalyse) |
| **5. Auswertung** | 4-8 Wochen | Figure package + Ergebnisstruktur (Mehrgrößenvergleich, saisonale Analyse) |
| **6. Schreiben** | 4-6 Wochen | Erste vollständige Paper-Version (IMRaD + Supplement) |

**Summe:** 6-12 Monate (abhängig von Catchment-Anzahl, Datenverfügbarkeit, Code-Komplexität)

---

### 📈 Realistisch publizierbare Ergebnisse

**Erwartungshaltung:**
- M2 verbessert **nicht zwingend jede Einzelmetrik**
- Aber: Verbessert **saisonale ET-Konsistenz**
- Verändert **Wasserbilanz plausibel**
- Reduziert **bestimmte systematische Fehler**
- Zeigt **robuste Unterschiede** zwischen statischer und dynamischer LULC

**Wissenschaftlicher Wert:**
> Ein gutes hydrologisches Methodenpaper muss nicht in jeder Kennzahl spektakulär besser sein. Es reicht oft, wenn du sauber zeigst, dass: der Prozess besser repräsentiert wird, die Wirkungskette nachvollziehbar ist, und die Standardkonfiguration relevante LULC-Effekte verschleift.

---

### ⚠️ Risiken (Wo das Paper scheitern kann)

| Risiko | Beschreibung | Gegenmaßnahme |
|--------|--------------|---------------|
| **1. Projekt wird zu groß** | Zusätzliche Wurzeldynamik, Infiltrationsschema, Schnee, Urbanhydrologie, Bewässerung | **Fokus auf einen Hauptprozess** (Interzeption) |
| **2. LULC-Daten inkonsistent** | Klassifikationsrauschen statt Landnutzungsänderung | **Harmonisierung** (gleiche Klassendefinitionen, Projektion, Auflösung) |
| **3. Zu viele Freiheitsgrade** | Jede LULC-Klasse bekommt 10 neue Parameter → kaum identifizierbar | **Minimalparameter** (storage capacity, seasonal variation) |
| **4. Nur Q evaluiert** | Kann nicht zeigen, ob Prozessbeitrag real oder kompensatorisch ist | **Mehrgrößen-Evaluation** (Q, SM, ET, Recharge) |

---

### 🎯 Klarer Zuschnitt (Empfehlung)

| Element | Festlegung |
|---------|------------|
| **Ziel** | Einführung eines dynamischen, LULC-sensitiven Interzeptionsmoduls in mHM |
| **Hauptvergleich** | Statische Standardkonfiguration vs. dynamische LULC ohne Prozessänderung vs. dynamische LULC mit neuer Interzeption |
| **Evaluation** | Q, SM, ET, optional Recharge |
| **Raum** | Sachsen / regionale Catchments mit Kontrast in Wald-Acker-Urban |
| **Beitrag** | Nicht "wir lösen Landnutzungsänderung vollständig in mHM", sondern: "Wir zeigen, dass eine explizite, dynamische Interzeptionsrepräsentation ein zentraler Hebel ist, um LULC-Effekte in mHM hydrologisch plausibler abzubilden." |

---

### 📑 Paper-Gliederung

| Abschnitt | Inhalt |
|-----------|--------|
| **1. Introduction** | Relevanz von LULC für Hydrologie; Modelle behandeln LULC oft zu statisch/vereinfacht; Interzeption als zentraler, aber vereinfachter Prozess; Forschungslücke in mHM; Ziel und Hypothesen |
| **2. Study Area and Data** | Catchments, Forcing, LULC, Q/SM/ET/Recharge |
| **3. Methods** | Standard-mHM; neue Interzeptionskonzeption; dynamische LULC-Implementierung; Experimente M0-M3; Metriken |
| **4. Results** | Wirkung auf Interzeptionsverlust; Wirkung auf ET/SM/Q/Recharge; Vergleich der Modellversionen; Sensitivität je LULC-Übergang |
| **5. Discussion** | Bedeutung für prozessbasierte LULC-Modellierung; Grenzen der Vereinfachung; Identifizierbarkeit/Unsicherheit; Übertragbarkeit auf größere Räume |
| **6. Conclusions** | Prägnant, keine Übertreibung |

---

### ✅ Ehrliches Urteil zur Machbarkeit

| Zeitrahmen | Einschätzung |
|------------|--------------|
| **6 Monate** | Machbar, wenn: Raum begrenzt, nur ein Hauptprozess, dynamische LULC-Daten verfügbar |
| **12 Monate** | Sehr gut machbar, inkl. sauberer Sensitivitätsanalyse, mehreren Catchments, starkem Supplement |
| **Nicht realistisch** | Kompletter LULC-Prozessbaukasten, deutschlandweite Vollanwendung plus neue Physik, umfassende Grundwasser- und Energiebilanz-Neuentwicklung |

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
