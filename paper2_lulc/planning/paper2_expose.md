# Paper #2 Exposé — Dynamische landnutzungssensitive Interzeption in mHM

**Titel:** Representing land-use-sensitive interception dynamics in mHM to assess hydrological impacts of land-cover change

**Autor:** Julian Schlaak  
**Datum:** 2026-03-13  
**Status:** Exposé für Betreuer-Review  
**Geplanter Journal:** Hydrology and Earth System Sciences (HESS)

---

## 1. Motivation und Forschungslücke

Landnutzungsänderungen beeinflussen hydrologische Prozesse systematisch — klassische Catchment-Experimente zeigen seit Jahrzehnten konsistente Zusammenhänge zwischen Vegetationsänderung und Wasserertrag (Bosch & Hewlett, 1982). Dennoch behandeln hydrologische Modelle Landnutzung oft zu statisch, zu grob oder nur implizit, wodurch hydrologische Auswirkungen von Landnutzungsänderungen unzureichend repräsentiert werden (Toosi et al., 2025).

**Spezifische Lücke für mHM:**
Es fehlt eine systematische Untersuchung dazu, wie eine **dynamische, landnutzungssensitive Interzeptionsrepräsentation in mHM** die Simulation hydrologischer Prozesse unter Landnutzungsänderung beeinflusst. Insbesondere offen ist:
1. Ob dynamische LULC-Informationen allein schon einen messbaren Unterschied machen
2. Ob eine explizite Prozessverbesserung über Interzeption zusätzlichen Mehrwert bringt
3. Wie sich Änderungen auf mehrere Zielgrößen gleichzeitig auswirken

**Regionale Evidenz (Sachsen):**
Renner et al. (2024) zeigten diagnostisch für 71 sächsische Catchments, dass Landoberflächen-Effekte (insbesondere Waldregeneration) hydrologische Trends mitprägen — jedoch ohne prozessbasierte Modellierung. Koycegiz et al. (2024) demonstrierten die Machbarkeit dynamischer LULC in mHM (Türkei, Irrigation), jedoch nicht für Interzeption.

---

## 2. Zielsetzung

**Übergeordnetes Ziel:**
> Entwicklung und Bewertung einer dynamischen, LULC-sensitiven Interzeptionsrepräsentation in mHM zur Verbesserung der hydrologischen Simulation unter Landnutzungsänderung.

**Explizite Eingrenzung:**

| Was ist KERN | Was ist bewusst AUSGESCHLOSSEN |
|--------------|-------------------------------|
| Interzeption als Hauptprozess | Vollständige Energiebilanz-Neuentwicklung |
| Dynamische LULC (CORINE 1991-2020) | Komplexe Schnee-Canopy-Physik |
| LULC-spezifische Speicherkapazität | Umfassende Wurzelphysik |
| Saisonale Variation (LAI-basiert) | Vollständige Infiltration/Grundwasser-Neuentwicklung |
| Evaluation: Q, ET, SM | Bewässerung, Urbanhydrologie, Erosion |
| 3-5 sächsische Pilot-Catchments | Ganz Deutschland-Anwendung |

---

## 3. Forschungsfragen

| RQ | Frage |
|----|-------|
| **RQ1** | Wie stark verändert eine dynamische landnutzungssensitive Interzeptionsrepräsentation in mHM die Partitionierung von Niederschlag in Interzeptionsverlust, Evapotranspiration, Bodenfeuchte und Abfluss? |
| **RQ2** | Verbessert die dynamische LULC-sensitive Interzeptionsrepräsentation die gleichzeitige Reproduktion von Abfluss, Bodenfeuchte und Evapotranspiration im Vergleich zu (a) einer statischen Standardkonfiguration und (b) einer Konfiguration mit nur dynamischer LULC, aber ohne neue Interzeptionsprozessdarstellung? |
| **RQ3** | Wie sensitiv reagieren hydrologische Wasserhaushaltskomponenten auf unterschiedliche Typen von Landnutzungsänderung (Aufforstung, Entwaldung, Acker→Grünland, Grünland→Acker)? |

---

## 4. Hypothesen

| H | Hypothese | Literatur-Support |
|---|-----------|-------------------|
| **H1** | Eine dynamische LULC-sensitive Interzeptionsdarstellung verändert die Niederschlagspartitionierung systematisch und führt zu plausiblen Änderungen in ET, Bodenwasser und Abfluss. | Toosi 2025 (LULC affects all water balance components), Bosch & Hewlett 1982 (vegetation change → water yield change) |
| **H2** | Die Kombination aus zeitvariabler LULC und LULC-sensitiver Interzeptionsdarstellung erhöht die Mehrgrößen-Konsistenz der Simulationen gegenüber einer statischen Standardkonfiguration und gegenüber einer Konfiguration mit nur dynamischer LULC. | Koycegiz 2024 (dynamic LULC improved GW anomalies, Q similar), Posada-Marín 2022 (model structure determines conclusions) |
| **H3** | Waldbezogene Landnutzungsänderungen verursachen stärkere Änderungen in Interzeption und saisonaler Wasserbilanz als Übergänge zwischen Offenlandklassen. | Bosch & Hewlett 1982 (conifer 40mm/10% > hardwood 25mm > scrub 10mm), Renner 2024 (forest headwaters show stronger decline) |

---

## 5. Methodisches Design

### 5.1 Modellkonfigurationen (M0-M3)

| ID | Name | LULC | Interception | Zweck |
|----|------|------|--------------|-------|
| **M0** | Static Reference | Static (single year, e.g., 2018) | Standard mHM | Referenz (current practice) |
| **M1** | Dynamic LULC | Dynamic (CORINE 1991, 2000, 2006, 2012, 2018) | Standard mHM | **Input-Effekt** (LULC extent only) |
| **M2** | Dynamic + Interception | Dynamic (same as M1) | **LULC-sensitive interception** | **Prozess-Effekt** (interception addition) |
| **M3** | Scenarios | Idealized transitions | Same as M2 | Sensitivität (Aufforstung, Entwaldung, Acker↔Grünland) |

**Wissenschaftliche Kern-Logik:**
- **M1 - M0** = Effekt zeitvariabler LULC (Input-Effekt)
- **M2 - M1** = zusätzlicher Effekt explizit verbesserter Interzeptionsrepräsentation (Prozess-Effekt)

**Diese Trennung macht das Paper wissenschaftlich sauber und publizierbar!**

---

### 5.2 Minimal-Interzeptionsschema

**Parameter (4 LULC-Oberklassen):**

| Klasse | S_max (mm) | LAI (sommer) | LAI (winter) |
|--------|------------|--------------|--------------|
| **Forest** | 2.0-4.0 | 4-6 | 1-3 |
| **Grassland** | 0.5-1.0 | 2-4 | 0.5-1.5 |
| **Cropland** | 0.3-0.8 | 3-5 (growing) | 0.2-0.5 |
| **Urban** | 0.1-0.3 | 0.1-0.5 | 0.1-0.5 |

**Prozess-Logik:**
```
For each timestep:
  P_throughfall = P - (Interception_storage_change + Interception_evaporation)
  Interception_storage = min(S_max[LULC], cumulative_P)
  Interception_evaporation = f(LAI_seasonal, PET, S_current)
```

---

### 5.3 Untersuchungsraum

**Sachsen / 3-5 Pilot-Catchments:**

| Kriterium | Anforderung |
|-----------|-------------|
| **Waldanteil** | Kontrast: 0-30% (low), 30-60% (medium), 60-90% (high) |
| **Landwirtschaft** | Kontrast: Acker-dominant vs. Grünland-dominant |
| **Relief** | Niedrigland vs. Mittelgebirge (Erzgebirge) |
| **Abflussdaten** | CAMELS-DE verfügbar (quality-checked) |
| **Größe** | 50-500 km² (mesoscale, mHM-appropriate) |

---

### 5.4 Evaluation

**Mehrgrößen (nicht nur Q):**

| Größe | Metriken |
|-------|----------|
| **Abfluss (Q)** | KGE, NSE, logNSE, Bias, high-flow / low-flow |
| **Evapotranspiration (ET)** | KGE, RMSE, Bias, saisonale Dynamik |
| **Bodenfeuchte (SM)** | KGE, RMSE, Anomalien-Korrelation |

**Kern-Kennzahl:** Multi-variable consistency score (KGE_Q + KGE_ET + KGE_SM) / 3

---

## 6. Erwartete Ergebnisse

| Vergleich | Erwartetes Signal | Interpretation |
|-----------|-------------------|----------------|
| **M1 - M0** | Small (LULC extent only) | Input-Effekt begrenzt |
| **M2 - M1** | Moderate (ET↑, SM↓, Q↓) | **Prozess-Effekt signifikant** |
| **M2 - M0** | Largest (combined) | Combined extent + process |
| **M3 (forest→nonforest)** | ET↓, Q↑ (Bosch benchmark ~40mm/10%) | Validation against classical evidence |

---

## 7. Zeitplan (6-12 Monate)

| Arbeitspaket | Dauer | Deliverable |
|--------------|-------|-------------|
| **AP1:** Literatur + Konzeptfinalisierung | 4-6 Wochen | Concept paper, parameter table |
| **AP2:** Datenaufbereitung | 4-8 Wochen | CORINE time series, catchment masks |
| **AP3:** mHM-Implementierung | 6-10 Wochen | mHM code (interception extension) |
| **AP4:** Kalibrierung + Experimente | 6-10 Wochen | M0-M3 output (all catchments) |
| **AP5:** Auswertung | 4-8 Wochen | Performance metrics, comparison figures |
| **AP6:** Schreiben | 4-6 Wochen | Full paper draft (8000-10000 words) |

---

## 8. Kritische Risiken und Gegenmaßnahmen

| Risiko | Wahrscheinlichkeit | Gegenmaßnahme |
|--------|-------------------|---------------|
| **LULC-Dateninkonsistenz** | Moderat | Harmonization rules, quality control |
| **Q zeigt keinen Unterschied** | Hoch (expected per Koycegiz) | Multi-variable focus (ET, SM primary) |
| **Equifinalität** | Moderat | Minimal parameter set (4 classes) |
| **Scope drift** | Hoch | Strict focus on interception only |

---

## 9. Wissenschaftliche Originalität

| Kriterium | Einschätzung |
|-----------|--------------|
| **Originalität** | Moderat bis hoch (keine mHM-spezifische Interzeption-LULC-Implementierung publiziert) |
| **Novelty** | Klar abgegrenzt (prozessbasiert, nicht diagnostisch wie Renner 2024) |
| **Realisierbarkeit** | Hoch (6-12 Monate, Fokus auf einen Hauptprozess) |
| **Publikations-Potenzial** | HESS / J. Hydrology / Water Resources Research (Q1 hydrology) |

---

## 10. Literatur (Schlüsselpapiere)

1. **Toosi et al. (2025):** Review — LULC processes underrepresented in hydrological models
2. **Koycegiz et al. (2024):** mHM study — dynamic LULC (Turkey, irrigation focus)
3. **Renner et al. (2024):** Diagnostic attribution — Saxony, 71 catchments, LULC effects detected
4. **Posada-Marín et al. (2022):** Meta-analysis — model structure determines deforestation conclusions
5. **Bosch & Hewlett (1982):** Review (94 catchments) — classical foundation, 40mm/10% benchmark

---

**Next:** Betreuer-Feedback einholen, dann AP2 (Datenaufbereitung) starten

**Word Count:** ~1,200 (2 pages)
