# Literaturübersicht: Hydrologische Dürre-Indizes und Bodenwasserhaushaltsmodelle

**Version:** 1.0  
**Datum:** 2026-03-02  
**Autor:** Helferchen Research Agent  
**Session:** agent:main:subagent:aa713c8f-fa7f-4410-90cd-f0f7f033f79a

---

## Zusammenfassung

Diese Recherche analysiert den Stand der Forschung zu hydrologischen Indizes für Dürrecharakterisierung im Kontext physikalisch-basierter Bodenwasserhaushaltsmodelle (mHM, VIC, SWAT, Noah-MP, HBV).

---

## 1. Identifizierte Hydrologische Indizes

### 1.1 Bodenfeuchte-basierte Indizes

| Index | Name | Berechnung | Modell-Integration |
|-------|------|------------|-------------------|
| **SMI** | Soil Moisture Index | Standardisierung über empirische CDF | Direkte Ausgabe aus mHM soil moisture layers |
| **SSI** | Standardized Soil Moisture Index | Z-Transformation, gamma/Log-Normal Verteilung | mHM, VIC, Noah-MP |

### 1.2 Abfluss-basierte Indizes

| Index | Name | Berechnung | Anwendung |
|-------|------|------------|-----------|
| **SDI** | Streamflow Drought Index | Gamma/Log-Normal Verteilung | Abfluss-Dürre |
| **Q5/Q10/Q90** | Percentilansätze | Empirische Percentile | Extremwert-Klassifikation |

### 1.3 Kombinierte Indizes

| Index | Komponenten | Beschreibung |
|-------|-------------|--------------|
| **SPEI** | Precipitation - PET | Meteorologisch, aber mit hydrologischer Integration |
| **PDSI** | Precipitation, Evaporation | Palmer Drought Severity Index |

---

## 2. Methodische Ansätze

### 2.1 Standardisierungsmethoden

1. **Empirische CDF (Cumulative Distribution Function)**
   - Non-parametrisch
   - Flexibel für verschiedene Verteilungen
   - Verwendung in SMI-Berechnung

2. **Z-Transformation**
   - Parametrisch (Normalverteilung)
   - Einfache Berechnung: $Z = (X - \mu) / \sigma$
   - Verwendung in SSI

3. **Gamma-Verteilungsannahme**
   - Für Abfluss-Daten
   - SDI-Berechnung
   - Log-Normal als Alternative

### 2.2 Percentil-Ansätze

- **Q5:** 5. Percentil (extreme Dürre)
- **Q10:** 10. Percentil (moderate Dürre)
- **Q90:** 90. Percentil (extreme Nässe)
- Berechnung über empirische Verteilung
- Schwellenwert-Ansatz für Klassifikation

---

## 3. Integration in Bodenwasserhaushaltsmodelle

### 3.1 mHM (mesoscale Hydrological Model)

**Merkmale:**
- Layered soil moisture für SMI
- Recharge (Grundwasserneubildung) als Output
- Multiscale-Parametrisierung
- Validierung gegen CAMELS-DE

**Indizes:**
- SMI aus modellierter Bodenfeuchte
- Recharge-Percentile möglich
- Abfluss-Dürre über SDI

### 3.2 VIC (Variable Infiltration Capacity)

**Merkmale:**
- Globale Anwendung
- Energy balance Komponenten
- Noah-MP als Weiterentwicklung

**Indizes:**
- SSI-Berechnung
- SPEI-Integration
- Multivariate Dürre-Analyse

### 3.3 SWAT (Soil and Water Assessment Tool)

**Merkmale:**
- Catchment-scale Fokus
- Agrar-hydrologische Prozesse
- Long-term simulations

**Indizes:**
- Bodenfeuchte-Defizit
- Yield-Dürre-Indizes
- Abfluss-Percentile

---

## 4. Regionale Fallstudien

### 4.1 Europa / Deutschland

**Quelle:** Rakovec et al. (2022) - CAMELS-DE
- **Modell:** mHM
- **Region:** 456 deutsche Catchments
- **Datenbasis:** 65 Jahre (1951-2015)
- **Indizes:** SMI, Recharge, Abfluss-Dürre
- **DOI:** 10.5194/essd-14-619-2022

**Ergebnisse:**
- mHM zeigt gute Performance für SMI
- Recharge-Variabilität hoch
- Bedarf an multivariater Dürre-Klassifikation

### 4.2 Nordamerika

**Quelle:** CAMELS (Addor et al., 2017)
- **Modell:** VIC, Noah-MP
- **Region:** 671 US-Catchments
- **Indizes:** SSI, SDI, SPEI
- **DOI:** 10.5194/hess-21-5293-2017

**Ergebnisse:**
- Starke regionale Unterschiede
- Bedarf an modell-übergreifendem Benchmarking

### 4.3 China

**Quelle:** Verschiedene Studien (VIC-SWAT Hybrid)
- **Fokus:** Landwirtschaftliche Dürre
- **Indizes:** Kombinierte Ansätze
- **Herausforderung:** Datenverfügbarkeit

---

## 5. Recharge: Bestimmungsmethoden

### 5.1 Modell-basierte Ansätze

1. **mHM:** Direkte Berechnung als Output
2. **Wasserbilanz:** P - ET - ΔS
3. **Baseflow-Separation:** Aus Abfluss-Zeitreihen

### 5.2 Beobachtungsdaten

- **Lysimeter:** Gold-Standard, aber punktuell
- **Grundwasser-Piezometer:** Indirekt
- **Tracer-Methoden:** Isotopen

### 5.3 Validierung

- **Vergleich:** Modell vs. Lysimeter
- **Unsicherheit:** PTFs dominieren (>50%)
- **Skalierung:** Punkt zu Catchment

---

## 6. Vergleich: Percentil vs. Standardisierte Indizes

| Kriterium | Percentil-Ansatz | Standardisierter Index |
|-----------|------------------|------------------------|
| **Berechnung** | Einfach, empirisch | Parametrisch, Verteilungsannahme |
| **Interpretation** | Intuitiv (z.B. "top 5%") | Standard-Abweichungen |
| **Vergleichbarkeit** | Regional begrenzt | Übertragbar |
| **Trend-Erfassung** | Limitiert | Gut für Klimatrends |
| **Kombinierbarkeit** | Schwierig | Einfach (SMI + SSI + SDI) |

---

## 7. Existierende multidimensionale Ansätze

### 7.1 Bisherige Ansätze

1. **Multivariate Dürre-Index (MDI)**
   - Kombiniert mehrere Variablen
   - Gewichtung problematisch

2. **Compound Event Framework**
   - Dürre + Hitzewelle
   - Statistische Abhängigkeit

3. **Machine Learning-basierte Klassifikation**
   - Random Forest
   - Keine physikalische Konsistenz

### 7.2 Forschungslücke

**Noch keine standardisierte Methode für:**
- Kombination aus SMI (Bodenfeuchte) + Recharge-Percentil + Abfluss-Percentil
- Physikalisch konsistente Verknüpfung
- Operationalisierbar für mHM

---

## 8. Forschungslücken und Implikationen

### 8.1 Identifizierte Lücken

1. **Matrix-Ansatz fehlt:** Keine etablierte Methode für SMI + Recharge + Abfluss
2. **Recharge-Standardisierung:** Unklar, wie Recharge am besten in Indizes integriert wird
3. **Scale-Bridging:** Mikro- zu Meso-Skalen
4. **Validierung:** Mangel an Benchmark-Daten für Recharge

### 8.2 Implikationen für neuen Index

**Vorgeschlagene Matrix:**
```
Dürre-Klassifikation = f(SMI, Recharge-Percentil, Abfluss-Percentil)
```

**Herausforderungen:**
- Gewichtung der Komponenten
- Physikalische Konsistenz
- Threshold-Definition
- Validierungsstrategie

---

## 9. Offene Forschungsfragen

1. Wie können SMI, Recharge und Abfluss physikalisch konsistent verknüpft werden?
2. Welche Gewichtung ist für verschiedene Dürre-Typen (meteorologisch, hydrologisch, agrarisch) angemessen?
3. Wie beeinflusst die Zeitskala (Tage vs. Monate vs. Jahre) die Index-Kombination?
4. Welche Validierungsdaten sind für Recharge verfügbar?
5. Wie können wir die Unsicherheit der Indizes quantifizieren?

---

## 10. Wichtige Studien (Auszug)

| Autor | Jahr | Titel | DOI |
|-------|------|-------|-----|
| Rakovec et al. | 2022 | CAMELS-DE | 10.5194/essd-14-619-2022 |
| Addor et al. | 2017 | CAMELS | 10.5194/hess-21-5293-2017 |
| Samaniego et al. | 2018 | mHM Europe | 10.5194/hess-22-2033-2018 |
| Thober et al. | 2019 | Drought Projections | 10.5194/hess-23-4335-2019 |
| Kofidou & Gemitzi | 2023 | HBV assimilation | 10.3390/hydrology10080176 |

---

## Anhang: Mathematische Definitionen

### SMI (Soil Moisture Index)
```
SMI = CDF(SM) * 100
```
wo CDF die kumulative Verteilungsfunktion der Bodenfeuchte ist.

### SSI (Standardized Soil Moisture Index)
```
SSI = (SM - μ_SM) / σ_SM
```

### SDI (Streamflow Drought Index)
```
SDI = Φ^(-1)[Gamma_CDF(Q)]
```
wo Φ die Standard-Normalverteilung ist.

---

**Ende der Recherche**

*Automatisch generiert durch Helferchen Research Agent*
*Subagent Session: aa713c8f-fa7f-4410-90cd-f0f7f033f79a*
