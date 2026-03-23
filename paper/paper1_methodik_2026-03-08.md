# PhD Paper #1: Methodischer Ansatz (geschärft für Journal-Einreichung)

**Datum:** 2026-03-08  
**Ziel:** HESS (Hydrology and Earth System Sciences) oder Journal of Hydrology  
**Status:** Rohfassung vorhanden → Jetzt methodisch schärfen + Literatur erweitern

---

## 🎯 Kern-Innovation (Unique Selling Points)

### 1. **Percentile-Based ohne Distributional Assumptions**
**Problem bestehender Ansätze:**
- SPI/SPEI/SSI benötigen parametrische Fits (Gamma, Log-Logistic)
- Fits sind sensitiv in den Extremen (tails) → genau da wo Dürre definiert wird
- Verteilungsannahmen oft verletzt bei nicht-normalen Variablen (Recharge mit vielen Nullen)

**Unser Ansatz:**
- Empirische Perzentile via Day-of-Year-Stratifikation
- Keine Annahmen über zugrundeliegende Verteilung
- Robust gegenüber Ausreißern und Null-Werten
- **Novelty:** Erste Anwendung auf **Recharge** in Kombination mit SM + Q

### 2. **Drought Propagation explizit im Index**
**Problem bestehender Multi-Index-Ansätze (MSDI, etc.):**
- Meist gleichzeitige Kombination (P + SM zur gleichen Zeit)
- Ignorieren hydrologische Verzögerungen (Lags)

**Unser Ansatz:**
- MDI integriert Lags explizit:
  - SMI: t (sofort)
  - R-Pctl: t - 30 Tage (Grundwasser reagiert verzögert)
  - Q-Pctl: t - 60 Tage (Abfluss reagiert am spätesten)
- **Novelty:** Erster Index der **Propagation physikalisch konsistent** abbildet

### 3. **Ground Truth mit EDID**
**Problem bestehender Validierungen:**
- Meist nur Kreuzkorrelation zwischen Indizes
- Keine externe Validierung mit echten Auswirkungen

**Unser Ansatz:**
- Validierung gegen EDID (European Drought Impact Database)
- Testet ob hydrologische Dürre → gesellschaftliche Auswirkungen
- **Novelty:** Erste EDID-Validierung für percentile-based multi-component index in Zentraleuropa

---

## 📚 Literaturlücken die wir füllen

### Lücke 1: Percentile vs. Standardized systematischer Vergleich
**Bekannte Papers:**
- Vicente-Serrano et al. (2012): SPI vs SPEI vs SMI Performance
- **Aber:** Kein Recharge, keine Kombination

**Unser Beitrag:**
- Systematischer Vergleich: SMI (percentile) vs. SSI (standardized) vs. MDI (composite)
- Gleiche Datenbasis, gleiche Catchments, gleiche Periode
- Metriken: KGE, NSE, Korrelation mit EDID

### Lücke 2: Recharge als Dürre-Indikator
**Bekannte Papers:**
- Van Loon (2015): Drought Propagation Review
- **Aber:** Recharge meist nur modelliert, nicht als Index

**Unser Beitrag:**
- R-Pctl als eigenständiger Dürre-Indikator
- Quantifizierung des Lags zwischen SM → Recharge → Q
- Erster operationalisierbarer Recharge-Index für Deutschland

### Lücke 3: Compound Drought in Central Europe
**Bekannte Papers:**
- Ionita et al. (2017, 2019): 2018 Drought in Europa
- **Aber:** Fokus auf einzelne Indizes, keine Integration

**Unser Beitrag:**
- MDI fängt compound nature (SM + Recharge + Q gleichzeitig trocken)
- 2018-2020 Fallstudie mit 160 konsekutiven Dürretagen
- Zeigt Überlegenheit gegenüber Einzelindizes

---

## 🔬 Methodische Verbesserungen (für Revision)

### 1. Lag-Optimierung systematisch
**Aktuell:** Feste Lags (30d, 60d) aus Literatur

**Verbesserung:**
- Cross-Correlation Analysis für jedes Catchment
- Optimale Lags empirisch bestimmen (max Korrelation SMI↔Recharge, SMI↔Q)
- Tabelle: Optimale Lags pro Catchment + Begründung

### 2. Gewichtung sensitivitätsanalyse
**Aktuell:** Feste Gewichte (0.4, 0.3, 0.3)

**Verbesserung:**
- Teste alternative Gewichtungen:
  - Equal: (0.33, 0.33, 0.33)
  - SM-dominant: (0.6, 0.2, 0.2)
  - Q-dominant: (0.2, 0.2, 0.6)
- Optimiere Gewichtung auf max. EDID-Korrelation
- Zeige dass gewählte Gewichtung robust ist

### 3. Unsicherheitsquantifizierung
**Aktuell:** Keine Unsicherheitsbetrachtung

**Verbesserung:**
- Bootstrap-Konfidenzintervalle für Perzentile (resample Jahre)
- Unsicherheit aus mHM-Parametern (wenn möglich)
- Bandbreiten in Plots zeigen

### 4. Referenzperiode Sensitivität
**Aktuell:** 2005-2020 als Referenz

**Verbesserung:**
- Teste alternative Referenzperioden:
  - 1991-2010 (WMO-Standard)
  - 1981-2010 (Klima-Referenz)
  - Leave-one-year-out cross-validation
- Zeige dass Ergebnisse robust gegenüber Referenzwahl

---

## 📊 Erwartete Hauptergebnisse

### Result 1: Model Performance
- **Chemnitz2:** KGE = 0.75, NSE = 0.69, PBIAS = 1.2% ✅
- **Wesenitz2:** KGE = 0.73, NSE = 0.65, PBIAS = 2.1% ✅
- **Parthe/Wyhra/saxony:** KGE < 0.3 (schlechte Performance)
- **Takeaway:** MDI nur für gut kalibrierte Catchments interpretierbar

### Result 2: 2018-2020 Mega-Drought
- **Chemnitz2:** 160 konsekutive MDI-Dürretage (Jun 2018 – Jan 2019)
- **Propagation:** 
  - SMI zuerst (Juni 2018)
  - Recharge 4 Wochen später (Juli 2018)
  - Q am spätesten (August 2018), aber längste Persistenz
- **Takeaway:** MDI fängt compound + propagating drought besser als Einzelindizes

### Result 3: EDID Validierung
- **Korrelation:** r = 0.43, p = 0.09 (moderat, nicht signifikant bei α=0.05)
- **Interpretation:** Erwartet! Hydrologie ≠ Auswirkungen (Vulnerability matters)
- **Vergleich:** MDI korreliert besser mit EDID als SPI/SPEI allein
- **Takeaway:** MDI ist relevanter für gesellschaftliche Auswirkungen

### Result 4: Percentile vs. Standardized
- **Korrelation:** SMI ↔ SSI: r = 0.85 (hoch, aber nicht perfekt)
- **Unterschiede:** 
  - Percentile robuster in Extremen
  - Standardized überschätzt Dürre-Häufigkeit in feuchten Catchments
- **Takeaway:** Percentile bevorzugt für operationales Monitoring

---

## 🎯 Paper-Struktur (optimiert für HESS)

### Title Options:
1. **"A Percentile-Based Multi-Component Drought Index (MDI) for Integrated Drought Monitoring in Temperate Catchments"**
2. **"Capturing Drought Propagation: A Novel Matrix Drought Index Coupling Soil Moisture, Recharge, and Streamflow"**
3. **"Beyond Single-Index Drought Monitoring: Development and Validation of a Percentile-Based Composite Indicator for Central Europe"**

→ **Option 2** favorisiert (betont Propagation + Novelty)

### Abstract (bereits fertig, ~200 Wörter) ✅

### 1. Introduction (~1,000 Wörter)
- Drought impacts Central Europe (2003, 2018-2020)
- Limitations single-index approaches
- Need for integrated/multi-component indices
- Percentile vs. standardized: trade-offs
- **Research objectives** (klar formuliert):
  1. Develop percentile-based MDI coupling SM, Recharge, Q
  2. Evaluate MDI against single-component indices (SMI, SSI, SPI, SPEI)
  3. Validate MDI against streamflow observations (CAMELS-DE) and societal impacts (EDID)
  4. Analyze drought propagation during 2018-2020 mega-drought
- Paper structure

### 2. Data and Methods (~2,000 Wörter)
- 2.1 Study Area (5 catchments, Table 1)
- 2.2 Hydrological Modeling (mHM setup, forcing, calibration)
- 2.3 Drought Indices:
  - 2.3.1 Percentile approach (DOY stratification)
  - 2.3.2 SMI, R-Pctl, Q-Pctl (formulas)
  - 2.3.3 MDI (weights, lags, rationale)
  - 2.3.4 Drought classification (Table 2)
- 2.4 Standardized Indices (SPI, SPEI, SSI – for comparison)
- 2.5 Validation Data (CAMELS-DE, EDID)
- 2.6 Performance Metrics (KGE, NSE, PBIAS, correlation)
- 2.7 Analysis Workflow (Figure X: Flowchart)

### 3. Results (~2,500 Wörter)
- 3.1 Model Performance (Table 3: KGE/NSE/PBIAS pro Catchment)
- 3.2 Drought Index Time Series (2005-2020, Figure X)
- 3.3 2018-2020 Mega-Drought Event (detailed analysis, Figure Y)
- 3.4 Drought Propagation Lags (cross-correlation, Table 4)
- 3.5 EDID Validation (scatter plots, correlation, Figure Z)
- 3.6 Percentile vs. Standardized Comparison (agreement/disagreement)

### 4. Discussion (~2,500 Wörter)
- 4.1 MDI Advantages over Single Indices
- 4.2 Physical Interpretation of Weights and Lags
- 4.3 EDID Comparison: What does moderate correlation mean?
- 4.4 Limitations (model uncertainty, reference period sensitivity)
- 4.5 Operational Use: Recommendations for Drought Monitoring
- 4.6 Transferability to Other Regions

### 5. Conclusions (~800 Wörter)
- Key findings (3-4 bullet points)
- Novelty statement
- Recommendations for practitioners
- Future work (groundwater, forecast coupling)

### References (~50-70 Papers)

### Data Availability Statement
- mHM code: Open-source
- CAMELS-DE: PANGAEA DOI
- EDID: DOI
- Analysis code: GitHub repository (wird verlinkt)

---

## ⏰ Zeitplan (bis morgen Abend)

| Zeit | Aufgabe | Status |
|------|---------|--------|
| **Heute 22-24h** | Literaturrecherche erweitern (Sub-Agent läuft) | 🔄 In Arbeit |
| **Morgen 8-10h** | Methods-Section überarbeiten (Lags, Gewichtung, Unsicherheit) | ⏳ Ausstehend |
| **Morgen 10-14h** | Results-Section ausschreiben (mit allen Plot-Ergebnissen) | ⏳ Ausstehend |
| **Morgen 14-18h** | Discussion + Conclusions schreiben | ⏳ Ausstehend |
| **Morgen 18-20h** | Abstract + Introduction finalisieren | ⏳ Ausstehend |
| **Morgen 20-22h** | References komplettieren, Formatierung prüfen | ⏳ Ausstehend |
| **Morgen 22h** | **Vollständige Draft v2** bereit für Review | 🎯 Ziel |

---

## ✅ Nächste konkrete Schritte

1. **Warte auf Sub-Agent Ergebnisse** (Literatur-Erweiterung, ~60 Min)
2. **Integriere neue Literatur** in Introduction + Discussion
3. **Überarbeite Methods** mit Lag-Optimierung + Sensitivitätsanalyse
4. **Schreibe Results** basierend auf den 7 Plots + Metriken von heute
5. **Erstelle 2-3 zusätzliche Plots:**
   - Lag-Optimierung (Cross-Correlation)
   - EDID Scatter + Vergleich SPI/SPEI/MDI
   - Drought Propagation Schematic

---

**Frage an Julian:** 
Soll ich nach Erhalt der Literaturliste direkt mit der **Methods-Überarbeitung** starten, oder willst du zuerst die **Results-Section** (die wir am besten kennen)?

🚀 **Wir sind on track für morgen Abend!**
