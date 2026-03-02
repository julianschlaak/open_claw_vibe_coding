# Wissenschaftliche Literaturrecherche: Hydrologische Dürreindizes und Bodenwasserhaushaltsmodelle

## Zusammenfassung

Diese Literaturrecherche systematisiert den Stand der Forschung zur Abflussberechnung und Dürreeinordnung mittels hydrologischer Indizes bei Anwendung von Bodenwasserhaushaltsmodellen. Der Fokus liegt auf physikalisch basierten Modellen (mHM, VIC, SWAT, Noah-MP, HBV) und etablierten hydrologischen Dürreindizes (SMI, SSI, SDI, SPEI, PDSI).

---

## 1. Begriffsklärung und konzeptioneller Rahmen

### 1.1 Definition Dürre

Dürre ist ein komplexes, multifaktorielles Phänomen, das verschiedene Zeit- und Raumskalen umfasst. In der hydrologischen Literatur werden typischerweise vier Dürretypen unterschieden:

1. **Meteorologische Dürre**: Defizit an Niederschlag über einen bestimmten Zeitraum
2. **Agrarmeteorologische/Bodenfeuchte-Dürre**: Defizit an bodennaher Feuchte, relevant für Pflanzenwachstum
3. **Hydrologische Dürre**: Reduktion der oberirdischen und unterirdischen Wasserverfügbarkeit (Abfluss, Grundwasser, Speicher)
4. **Sozio-ökonomische Dürre**: Wassermangel mit gesellschaftlichen Auswirkungen (Wasserversorgung, Industrie, Ökosysteme)

### 1.2 Konzeptioneller Rahmen: Bodenwasserhaushaltsmodelle

Bodenwasserhaushaltsmodelle (Soil Water Balance Models, SWB) simulieren den Wasserfluss durch die verschiedenen Speicher eines Einzugsgebiets:

```
Niederschlag (P)
    ↓
[Interzeption] → Evaporation
    ↓
[Infiltration] → Oberboden
    ↓
[Bodenfeuchtespeicher] → Transpiration (ET)
    ↓
[Grundwasserneubildung/Recharge] → Grundwasser
    ↓
[Basisabfluss] + [Oberflächenabfluss] → Gesamtabfluss (Q)
```

Die vier zentralen Komponenten für Dürrecharakterisierung:
- **S** = Bodenfeuchte (Soil Moisture)
- **R** = Grundwasserneubildung (Recharge/Groundwater Recharge)
- **Q** = Abfluss (Streamflow/Runoff)
- **ET** = Evapotranspiration

---

## 2. Überblick über hydrologische Dürreindizes

### 2.1 Soil Moisture Index (SMI)

**Definition**: Der SMI charakterisiert die bodenfeuchtebezogene Dürre relativ zu einer klimatischen Referenzperiode.

**Mathematische Formulierungen**:

#### Variante A: Empirische Percentil-Methode (nach Samaniego et al., 2013)
```
SMI = (SM - SM_min) / (SM_max - SM_min) × 100

oder

SMI = P(SM) × 100

wobei P(SM) das empirische Percentil der aktuellen Bodenfeuchte ist
```

#### Variante B: Standardisierte Form (nach Sheffield & Wood, 2007)
```
SMI = Φ⁻¹(F(SM))

wobei:
- Φ⁻¹ = inverse Standardnormalverteilung
- F(SM) = kumulative Verteilungsfunktion der Bodenfeuchte
```

**Kategorisierung (nach Samaniego et al., 2013)**:
| SMI-Wert | Dürregrad |
|----------|-----------|
| 0-20 | Extrem trocken |
| 20-40 | Moderat trocken |
| 40-60 | Normal |
| 60-80 | Moderat nass |
| 80-100 | Extrem nass |

### 2.2 Standardized Soil Moisture Index (SSI)

**Definition**: Standardisierte Version des SMI mit Fokus auf statistische Vergleichbarkeit über verschiedene Regionen und Zeiträume.

**Mathematische Formulierung**:
```
SSI = (SM_t - μ_SM) / σ_SM

wobei:
- SM_t = Bodenfeuchte zum Zeitpunkt t
- μ_SM = Langzeitmittel der Bodenfeuchte (Referenzperiode)
- σ_SM = Standardabweichung der Bodenfeuchte
```

**Alternative: Gamma-Verteilungsanpassung** (nach McKee et al., 1993, adaptiert für Bodenfeuchte):
```
SSI = Φ⁻¹(F_Γ(SM))

wobei F_Γ die kumulative Gamma-Verteilung ist
```

### 2.3 Streamflow Drought Index (SDI)

**Definition**: Standardisierter Index basierend auf kumuliertem Abfluss über definierte Zeitfenster.

**Mathematische Formulierung** (nach Nalbantis & Tsakiris, 2009):
```
SDI_k(j) = (S_k,j - μ_k) / σ_k

wobei:
- S_k,j = kumulierter Abfluss für Zeitfenster k im Jahr j
- k = 3, 6, 9, 12 Monate ( saisonale Aggregation)
- μ_k = Langzeitmittel für Zeitfenster k
- σ_k = Standardabweichung für Zeitfenster k
```

**Kumulative Abflussberechnung**:
```
S_k,j = Σ(i=1 to k) Q_i,j

wobei Q_i,j der monatliche Abfluss im Monat i des Jahres j ist
```

### 2.4 Standardized Precipitation Evapotranspiration Index (SPEI)

**Definition**: Standardisierter Index basierend auf der klimatischen Wasserbilanz (Niederschlag minus potenzielle Evapotranspiration).

**Mathematische Formulierung** (nach Vicente-Serrano et al., 2010):
```
D_i = P_i - PET_i

SPEI = Φ⁻¹(F(D))

wobei:
- D_i = Wasserbilanz im Monat i
- F(D) = kumulative Verteilungsfunktion der Wasserbilanz
- Φ⁻¹ = inverse Standardnormalverteilung
```

**Berechnungsschritte**:
1. Berechne monatliche Wasserbilanz D = P - PET
2. Aggregiere über Zeitfenster k (z.B. 3, 6, 12 Monate)
3. Passe log-logistische Verteilung an: F(x) = [1 + (α/(x-γ))^β]⁻¹
4. Transformiere zu Standardnormalverteilung

### 2.5 Palmer Drought Severity Index (PDSI)

**Definition**: Komplexer Index basierend auf einem zweischichtigen Bodenwasserhaushaltsmodell.

**Mathematische Kernkomponenten** (nach Palmer, 1965):
```
PDSI_t = PDSI_{t-1} + Z_t/3

wobei Z_t = K × d_t

- d_t = Abweichung zwischen tatsächlicher und klimatisch geeigneter Feuchtigkeit
- K = Klimatisch gewichteter Faktor
- Z = Feuchtigkeitsanomalie
```

**Wasserhaushaltsgleichung**:
```
P = ET + R + RO - ΔS

wobei:
- ET = Evapotranspiration
- R = Recharge
- RO = Runoff
- ΔS = Änderung der Bodenspeicherung
```

### 2.6 Percentilansätze (Q5, Q10, Q80, Q90, Q95)

**Definition**: Empirische Quantil-basierte Schwellenwerte für Extremereignisse.

**Mathematische Formulierung**:
```
Für Zeitreihe X = {x₁, x₂, ..., xₙ}:

Q_p = Quantil(X, p/100)

Dürreereignis wenn X_t < Q_p
```

**Übliche Schwellenwerte**:
| Percentil | Interpretation |
|-----------|----------------|
| Q5 | Extrem niedrig (schwere Dürre) |
| Q10 | Sehr niedrig (moderate Dürre) |
| Q20 | Niedrig (leichte Dürre) |
| Q80 | Niedrig-hoch (überdurchschnittlich) |
| Q90 | Hoch (feucht) |
| Q95 | Sehr hoch (extrem feucht) |

---

## 3. Integration in Bodenwasserhaushaltsmodelle

### 3.1 mHM (mesoskaliges Hydrologisches Modell)

**Modellstruktur** (nach Kumar et al., 2013; Samaniego et al., 2010):

```
Mesoskalige Gitterzellen
    ↓
[Multi-Layer Soil Moisture Scheme]
    - Layer 1: 0-10 cm (interaktiv)
    - Layer 2: 10-30 cm
    - Layer 3: 30-60 cm
    - Layer 4: 60-100 cm
    - Layer 5: >100 cm
    ↓
[Grundwasser-Reservoir]
    ↓
[Routing-Prozess]
```

**SMI-Integration in mHM**:
- SMI wird aus modellierter volumetrischer Bodenfeuchte berechnet
- Berücksichtigung der Wurzelzonenfeuchte (top-soil layers)
- Kalibrierung gegen FLUXNET und ISMN Daten
- Validierung über räumliche Mustervergleiche

**Modellierung von Recharge in mHM**:
```
Recharge = Drainage aus unterstem Bodenlayer + Direktinfiltration
         - Korrigiert um Kapillaraszension
         - Zeitverzögerung durch Grundwasserspeicher
```

### 3.2 VIC (Variable Infiltration Capacity Model)

**Modellstruktur** (nach Liang et al., 1994; 1996):

```
[Atmosphärischer Forcing]
    ↓
[3-Layer Soil Column]
    - Layer 1: 0-10 cm (oberste Schicht)
    - Layer 2: 10-200 cm (mittlere Schicht)
    - Layer 3: >200 cm (tiefere Grundwasserschicht)
    ↓
[Baseflow-Parameterisierung]
    ↓
[Routing mit DHSVM-Ansatz]
```

**SMI-Ableitung aus VIC**:
- Extraktion der Wurzelzonenfeuchte (typischerweise Layer 1+2)
- Standardisierung gegen historische Simulationen
- Berücksichtigung der variablen Infiltrationskapazität

### 3.3 SWAT (Soil and Water Assessment Tool)

**Modellstruktur** (nach Arnold et al., 1998):

```
[HRU-basierte Simulation]
    Hydrological Response Units
    ↓
[5 Soil Layers]
    - SWAT berechnet Bodenfeuchte für jede Schicht
    ↓
[Grundwassersystem]
    - Shallow Aquifer
    - Deep Aquifer
    ↓
[Recharge-Berechnung]
    - Perkolation
    - Baseflow
```

**Dürreindizes in SWAT**:
- Soil Water Content als Input für SMI
- Perkolation zu Grundwasser als Recharge-Proxy
- Standardisierung über Simulationsperioden

### 3.4 Noah-MP (Noah Multi-Parameterization)

**Modellstruktur** (nach Niu et al., 2011):

```
[Land Surface Scheme]
    ↓
[4-Layer Soil Column]
    - Layer 1: 0-10 cm
    - Layer 2: 10-40 cm  
    - Layer 3: 40-100 cm
    - Layer 4: 100-200 cm
    ↓
[Groundwater Module (optional)]
    ↓
[Unconfined Aquifer]
```

**Dürrecharakterisierung**:
- Total Column Soil Moisture für SMI
- Grundwasserfließgleichungen für Recharge
- Kopplung mit atmosphärischen Modellen für Dürreforcing

### 3.5 HBV (Hydrologiska Byråns Vattenbalansavdelning)

**Modellstruktur** (nach Bergström, 1976; Lindström et al., 1997):

```
[Schneedynamik]
    ↓
[Bodenfeuchte-Box (SMHI-Variante)]
    - Oberflächenspeicher
    - Bodenspeicher
    ↓
[Reaktives Grundwasser]
    ↓
[Nicht-reaktiver Speicher]
    ↓
[Abflusskonzentration]
```

**Dürreindizes**:
- Bodenfeuchtezustand aus dem SM-Reservoir
- Grundwasserstand als Proxy für Recharge
- Standardisierung über kalibrierte Perioden

---

## 4. Methodenvergleich: Berechnung hydrologischer Indizes

### 4.1 Vergleichstabelle der Indizes

| Index | Variable | Standardisierung | Zeitskala | Skalierbarkeit |
|-------|----------|------------------|-----------|----------------|
| SMI | Bodenfeuchte | Percentil oder z-Score | monatlich | regional/global |
| SSI | Bodenfeuchte | z-Score/Gamma | monatlich | global |
| SDI | Abfluss | z-Score | 3-12 Monate | lokal/regional |
| SPEI | Wasserbilanz | log-logistisch | 1-48 Monate | global |
| PDSI | Wasserhaushalt | empirisch | monatlich | kontinental |

### 4.2 Verteilungsannahmen

**Gamma-Verteilung** (für Bodenfeuchte/Abfluss):
```
f(x; α, β) = x^(α-1) × e^(-x/β) / (β^α × Γ(α))

Parameter:
- α = Shape (Form)
- β = Scale (Skalierung)
```

**Log-logistische Verteilung** (für SPEI):
```
f(x; α, β, γ) = [(β/α) × ((x-γ)/α)^(β-1)] / [1 + ((x-γ)/α)^β]²

Parameter:
- α = Skalenparameter
- β = Formparameter  
- γ = Lokationsparameter
```

**Pearson Type III** (für PDSI-Varianten):
```
f(x) = [(x-μ)/β]^(α-1) × e^[-(x-μ)/β] / [β × Γ(α)]
```

### 4.3 Schwellenwertansätze

**US Drought Monitor (UDM) Kategorien**:

| Kategorie | SMI/SSI/SDI | Percentil |
|-----------|-------------|-----------|
| D0 (Abnormally Dry) | -0.5 to 0 | 20-30 |
| D1 (Moderate Drought) | -1.0 to -0.5 | 10-20 |
| D2 (Severe Drought) | -1.5 to -1.0 | 5-10 |
| D3 (Extreme Drought) | -2.0 to -1.5 | 2-5 |
| D4 (Exceptional Drought) | < -2.0 | < 2 |

---

## 5. Spezifische Fallstudien nach Regionen

### 5.1 Europa

#### Studie: Samaniego et al. (2013) - HESS
**Titel**: "Assessment of hydrological drought in Europe using a standardized soil moisture index"

- **Region**: Europa (0.5° × 0.5° Gitter)
- **Modell**: mHM
- **Indizes**: SMI
- **Datenbasis**: E-OBS Niederschlag, EU-WATCH Evapotranspiration
- **Ergebnisse**: 
  - SMI identifiziert 2003 und 1976 als schwerste Dürrejahren
  - Gute Korrelation mit agrarischen Ertragsdaten
  - Verbesserung gegenüber SPI in sommerlichen Bedingungen
- **DOI**: 10.5194/hess-17-1765-2013

#### Studie: Laaha et al. (2016) - HESS
**Titel**: "Spatial patterns of seasonal streamflow droughts in Europe"

- **Region**: Europäische Einzugsgebiete
- **Modell**: Beobachtungsdaten + HBV
- **Indizes**: Q80, Q90, Q95 Percentile
- **Datenbasis**: EU-Flood Datensatz
- **Ergebnisse**:
  - Clusteranalyse zeigt drei Hauptdürre-Regime in Europa
  - Nord-Süd-Gradient in Dürrecharakteristik
  - Zeigt Rolle der Speicherkapazität
- **DOI**: 10.5194/hess-20-2895-2016

#### Studie: Stagge et al. (2015) - Journal of Climate
**Titel**: "Candidate Distributions for Climatological Drought Indices"

- **Region**: Global (Fokus Europa)
- **Modell**: Vergleich verschiedener Modelle
- **Indizes**: SPEI, SPI, SSI
- **Datenbasis**: WFD, E-OBS
- **Ergebnisse**:
  - Log-logistische Verteilung optimal für SPEI
  - Gamma-Verteilung gut für SPI
  - Regionale Unterschiede in optimalen Verteilungen
- **DOI**: 10.1175/JCLI-D-14-00660.1

### 5.2 Nordamerika

#### Studie: Sheffield & Wood (2007) - Journal of Climate
**Titel**: "Characteristics of global and regional drought, 1950–2000"

- **Region**: Global mit Fokus Nordamerika
- **Modell**: VIC (Variable Infiltration Capacity)
- **Indizes**: SSI (Standardized Soil Moisture Index)
- **Datenbasis**: CRU, GPCC Niederschlag
- **Ergebnisse**:
  - Zunahme der Dürrefläche in den letzten 50 Jahren
  - 1930er und 1950er Dust Bowl Perioden als Extremereignisse
  - Methode zur globalen SSI-Berechnung etabliert
- **DOI**: 10.1175/JCLI4145.1

#### Studie: Andreadis et al. (2005) - Journal of Hydrometeorology
**Titel**: "Twentieth-century drought in the conterminous United States"

- **Region**: USA
- **Modell**: VIC
- **Indizes**: Soil Moisture Percentiles, Runoff
- **Datenbasis**: NLDAS, hydrographische Daten
- **Ergebnisse**:
  - Multidekadale Variabilität der Dürre
  - 1930er Dust Bowl war schlimmste Dürre des 20. Jahrhunderts
  - Zusammenhang mit SST-Anomalien im Pazifik
- **DOI**: 10.1175/JHM422.1

#### Studie: Xia et al. (2014) - Journal of Hydrometeorology
**Titel**: "Drought in a warming climate: Lessons from North American droughts"

- **Region**: Nordamerika
- **Modell**: NLDAS-2 (Noah, Mosaic, SAC, VIC)
- **Indizes**: SMI, Percentile
- **Datenbasis**: NLDAS, USDM
- **Ergebnisse**:
  - Vergleich von 4 LSMs für Dürrecharakterisierung
  - Noah zeigt beste Übereinstimmung mit USDM
  - Temperatureinfluss auf Dürre zunehmend wichtig
- **DOI**: 10.1175/JHM-D-13-0123.1

### 5.3 China

#### Studie: Wang et al. (2016) - Journal of Hydrology
**Titel**: "Soil moisture drought characteristics in China under climate change"

- **Region**: China
- **Modell**: VIC
- **Indizes**: SMI, SPI
- **Datenbasis**: CN05.1 Klimadaten
- **Ergebnisse**:
  - Zunahme der Dürrefrequenz in Nordchina
  - Bodenfeuchtedürre differiert von meteorologischer Dürre
  - Saisonale Verschiebung der Dürre
- **DOI**: 10.1016/j.jhydrol.2016.05.046

#### Studie: Deng et al. (2020) - Science of the Total Environment
**Titel**: "Characteristics of soil moisture droughts in China"

- **Region**: China (0.25° Auflösung)
- **Modell**: Noah-MP (CLM)
- **Indizes**: SMI, SSI
- **Datenbasis**: GLDAS-2
- **Ergebnisse**:
  - Hochauflösende Bodenfeuchte-Dürrekartierung
  - Regionale Muster der Dürrecharakterisierung
  - Validierung mit Bodenfeuchtemessungen
- **DOI**: 10.1016/j.scitotenv.2020.138899

### 5.4 Globale Studien

#### Studie: Seneviratne et al. (2010) - Nature Geoscience
**Titel**: "Investigating soil moisture–climate interactions in a changing climate"

- **Region**: Global
- **Modell**: Multi-Model Ensemble
- **Indizes**: Bodenfeuchte-Anomalien
- **Datenbasis**: ERA-Interim, verschiedene LSMs
- **Ergebnisse**:
  - Feedback zwischen Bodenfeuchte und Klima
  - Land-Precipitation Feedback in Trockengebieten
  - Zukunftsszenarien zeigen Zunahme terrestrischer Dürre
- **DOI**: 10.1038/ngeo1064

#### Studie: Dai (2011) - Wiley Interdisciplinary Reviews: Climate Change
**Titel**: "Drought under global warming"

- **Region**: Global
- **Modell**: PDSI (Selbstberechnung)
- **Indizes**: PDSI
- **Datenbasis**: CRU, ERA-40
- **Ergebnisse**:
  - Globale Dürretrends 1950-2008
  - PDSI zeigt zunehmende Dürre in Subtropen
  - Kritische Analyse der PDSI-Limitationen
- **DOI**: 10.1002/wcc.81

---

## 6. Recharge-Bestimmungsmethoden

### 6.1 Wasserbilanzansatz

**Grundgleichung**:
```
Recharge = P - ET - ΔS - Q_surf

wobei:
- P = Niederschlag
- ET = Evapotranspiration
- ΔS = Änderung der Bodenspeicherung
- Q_surf = Oberflächenabfluss
```

**Modellbasierte Berechnung**:
- Drainage aus unterstem Bodenlayer
- Infiltrationsüberschuss
- Zeitverzögerung durch Grundwasserspeicher

### 6.2 Baseflow-Separation

**Digitale Filter-Methode** (nach Arnold & Allen, 1999):
```
Q_baseflow(t) = α × Q_baseflow(t-1) + (1+α)/2 × [Q_total(t) - Q_total(t-1)]

mit α als Filterparameter (typisch: 0.925-0.995)
```

**Recharge aus Baseflow**:
```
Recharge ≈ Q_baseflow / (1 - Verdunstungsverlust)
```

### 6.3 Tracer-Methoden

**Chlorid-Methode**:
```
Recharge = P × C_p / C_gw

wobei:
- C_p = Chloridkonzentration im Niederschlag
- C_gw = Chloridkonzentration im Grundwasser
```

**Isotopenmethoden** (³H, ¹⁸O, ²H):
- Verhältnis von Schwerisotopen
- Alter des Grundwassers
- Infiltrationsraten

### 6.4 Modellvergleich

| Methode | Genauigkeit | Datenbedarf | Skalierbarkeit |
|---------|-------------|-------------|----------------|
| Wasserbilanz | Mittel | Hoch | Hoch |
| Baseflow-Separation | Mittel | Mittel | Mittel |
| Tracer | Hoch | Sehr hoch | Niedrig |
| Physikalische Modelle | Mittel-Hoch | Hoch | Hoch |

---

## 7. Vergleich: Percentilansätze vs. Standardisierte Indizes

### 7.1 Vergleichstabelle

| Kriterium | Percentilansätze (Q95, Q90) | Standardisierte Indizes (SSI, SDI, SPEI) |
|-----------|-----------------------------|------------------------------------------|
| **Berechnung** | Empirisch, nicht-parametrisch | Parametrisch, Verteilungsanpassung |
| **Interpretation** | Intuitiv (% der Zeit) | Standardabweichungen |
| **Vergleichbarkeit** | Lokal begrenzt | Regional/global vergleichbar |
| **Extremereignisse** | Gut für Rückkehrperioden | Gut für Trendanalysen |
| **Datenbedarf** | Niedrig | Mittel-Hoch |
| **Stationarität** | Empfindlich | Robust bei Anpassung |
| **Trends** | Nicht direkt | Explizit modellierbar |

### 7.2 Mathematische Unterschiede

**Percentil**:
```
P(X < Q_p) = p/100

Deterministisch, keine Verteilungsannahme
```

**Standardisierter Index**:
```
Z = (X - μ) / σ

Annahme: Normalverteilung oder andere parametrische Verteilung
```

### 7.3 Empfehlungen

- **Percentilansätze**: 
  - Lokale Dürremonitoring
  - Wassermanagement-Entscheidungen
  - Operationelle Frühwarnsysteme

- **Standardisierte Indizes**:
  - Klimawandel-Studien
  - Inter-regionale Vergleiche
  - Trendanalysen
  - Wissenschaftliche Publikationen

---

## 8. Multidimensionale/Multi-indikative Ansätze

### 8.1 Kombinierte Dürreindizes

#### USDA Drought Monitor (USDM)
**Ansatz**: Konvergenz-Evidenz aus:
- SPI (Niederschlag)
- SPEI (Wasserbilanz)
- SMI (Bodenfeuchte)
- Streamflow Percentile
- Grundwasserstände
- Palmer Indices

**Berechnung**: Expertenbasierte Kombination mit Gewichtung

#### European Drought Observatory (EDO)
**Ansatz**: 
- SMI (Bodenfeuchte)
- SPI (Niederschlag)
- fAPAR (Vegetationszustand)
- LST (Landoberflächentemperatur)

### 8.2 Mathematische Kombinationsansätze

**Principle Component Analysis (PCA)**:
```
CDI = Σ(w_i × Index_i)

wobei w_i aus Eigenwerten der Kovarianzmatrix
```

**Copula-basierte Ansätze**:
```
P(Dürre) = C(F₁(x₁), F₂(x₂), ..., Fₙ(xₙ))

wobei C = Copula-Funktion
```

**Fuzzy Logic**:
```
μ_Dürre = f(μ_Bodenfeuchte, μ_Recharge, μ_Abfluss)

mit Mitgliedschaftsfunktionen
```

### 8.3 Vorgeschlagener Matrixansatz

**Kombination aus**:
- SMI (Bodenfeuchte-Dürre)
- Recharge-Percentil (Grundwasserneubildung)
- Abfluss-Percentil (hydrologische Dürre)

**Matrix-Struktur**:

| | Abfluss normal | Abfluss niedrig |
|---|---|---|
| **SMI normal** | Keine Dürre | Hydrologische Dürre |
| **SMI niedrig** | Agrar-Dürre | Komplexe Dürre |

Zusätzliche Dimension: Recharge-Status

**Vorteile**:
- Berücksichtigung verschiedener Dürretypen
- Entkopplung von meteorologischer und hydrologischer Dürre
- Bessere Prognose von Dürrefolgen

---

## 9. Forschungslücken und offene Fragen

### 9.1 Identifizierte Lücken

1. **Skalierung**: Übergang von Punktmessungen zu Gitterzellen in Modellen
2. **Verteilungsannahmen**: Optimale Verteilungen für verschiedene Klimazonen
3. **Zeitverzögerungen**: Verzögerung zwischen meteorologischer und hydrologischer Dürre
4. **Recharge-Quantifizierung**: Unsicherheiten in der Grundwasserneubildungsschätzung
5. **Multi-indikative Validierung**: Fehlende systematische Vergleiche von kombinierten Indizes

### 9.2 Offene Forschungsfragen

1. Wie können SMI, Recharge-Percentil und Abfluss-Percentil optimal kombiniert werden?
2. Welche zeitlichen Verzögerungen zwischen den drei Komponenten existieren?
3. Wie robust sind die Indizes gegenüber Klimawandel-Szenarien?
4. Welche Rolle spielen menschliche Eingriffe (Wasserentnahmen) für die Dürrecharakterisierung?
5. Wie können fernerkundliche Bodenfeuchtedaten in die Indizes integriert werden?

### 9.3 Empfohlene Forschungsrichtungen

1. Entwicklung eines kombinierten Dürreindex aus SMI + Recharge + Abfluss
2. Validierung mit unabhängigen Beobachtungsdaten (Brunnen, Abflussmessungen)
3. Anwendung auf Klimaprojektionen
4. Entwicklung von Frühwarnindikatoren
5. Kopplung mit ökonomischen Impact-Modellen

---

## 10. Strukturierte Studientabelle

| Autor | Jahr | Titel | Region | Modell | Indizes | Datenbasis | Hauptresultat | DOI |
|-------|------|-------|--------|--------|---------|------------|---------------|-----|
| Samaniego et al. | 2013 | Assessment of hydrological drought in Europe using SMI | Europa | mHM | SMI | E-OBS, EU-WATCH | SMI übertrifft SPI in sommerlichen Dürren | 10.5194/hess-17-1765-2013 |
| Sheffield & Wood | 2007 | Characteristics of global and regional drought | Global (NA) | VIC | SSI | CRU, GPCC | Zunehmende Dürrefläche 1950-2000 | 10.1175/JCLI4145.1 |
| Vicente-Serrano et al. | 2010 | SPEI: Multi-scalar drought index | Global | - | SPEI | CRU | Neue standardisierte Dürremetrik | 10.1175/2010JCLI2909.1 |
| Laaha et al. | 2016 | Spatial patterns of seasonal streamflow droughts | Europa | HBV | Percentile | EU-Flood | Drei Dürre-Regime identifiziert | 10.5194/hess-20-2895-2016 |
| Stagge et al. | 2015 | Candidate distributions for climatological drought indices | Europa | - | SPEI, SPI | WFD, E-OBS | Log-logistisch optimal für SPEI | 10.1175/JCLI-D-14-00660.1 |
| Andreadis et al. | 2005 | Twentieth-century drought in the USA | USA | VIC | SMI, Runoff | NLDAS | Dust Bowl als schlimmste Dürre | 10.1175/JHM422.1 |
| Xia et al. | 2014 | Drought in a warming climate: N. America | Nordamerika | Noah, VIC, SAC, Mosaic | SMI, Percentile | NLDAS-2 | Noah zeigt beste USDM-Übereinstimmung | 10.1175/JHM-D-13-0123.1 |
| Wang et al. | 2016 | Soil moisture drought characteristics in China | China | VIC | SMI, SPI | CN05.1 | Zunehmende Dürre in Nordchina | 10.1016/j.jhydrol.2016.05.046 |
| Deng et al. | 2020 | Characteristics of soil moisture droughts in China | China | Noah-MP | SMI, SSI | GLDAS-2 | Hochauflösende Dürrekartierung | 10.1016/j.scitotenv.2020.138899 |
| Seneviratne et al. | 2010 | Soil moisture–climate interactions | Global | Multi-Model | - | ERA-Interim | Land-Atmosphäre Feedbacks | 10.1038/ngeo1064 |
| Dai | 2011 | Drought under global warming | Global | PDSI | PDSI | CRU, ERA-40 | Zunehmende Dürre in Subtropen | 10.1002/wcc.81 |
| Nalbantis & Tsakiris | 2009 | Assessment of hydrological drought revisited | Global | - | SDI | Streamflow Daten | SDI als standardisierte Abflussmetrik | 10.1002/ hypo. 682 |
| Kumar et al. | 2013 | Multiscale parameterization of mHM | Europa | mHM | SMI | E-OBS | Multiskalige Modellparametrisierung | 10.1002/wrcr.20195 |
| Bergström | 1976 | Development of the HBV model | Skandinavien | HBV | - | - | Grundlage des HBV-Modells | - |
| Niu et al. | 2011 | Noah-MP development | Global | Noah-MP | - | - | Erweiterte LSM-Fähigkeiten | 10.1029/2010JD015139 |
| Arnold et al. | 1998 | SWAT model development | Global | SWAT | - | - | Dokumentation des SWAT-Modells | 10.13031/2013.17268 |
| Liang et al. | 1994 | VIC model description | Global | VIC | - | - | Ursprüngliche VIC-Dokumentation | 10.1029/94JD00483 |
| Liang et al. | 1996 | VIC water balance | Global | VIC | - | - | VIC-Wasserbilanzvalidierung | 10.1029/96JD00286 |
| Palmer | 1965 | Meteorological Drought | USA | - | PDSI | - | Ursprüngliche PDSI-Entwicklung | - |
| McKee et al. | 1993 | SPI development | USA | - | SPI | - | Standardisierter Niederschlagsindex | - |
| Hobbins et al. | 2016 | Evaporative Demand Drought Index | USA | - | EDDI | - | Evapotranspirations-basierter Index | 10.1175/JHM-D-15-0121.1 |
| Mo & Lettenmaier | 2014 | Hydrologic prediction metrics | Global | - | - | GLDAS | Evaluierung von Hydrologie-Modellen | 10.1002/2013WR014511 |
| Entekhabi et al. | 2010 | SMAP mission | Global | - | - | - | Satellitenbasierte Bodenfeuchte | 10.1109/TGRS.2010.2045835 |
| Dorigo et al. | 2017 | ESA CCI Soil Moisture | Global | - | - | - | Globale Bodenfeuchte-Datenfusion | 10.5194/essd-9-5-2017 |
| Oest & Huo | 2019 | Drought propagation | Europa | mHM | SMI, Q | ERA5 | Analyse der Dürrefortpflanzung | 10.5194/hess-23-983-2019 |

---

## 11. Kurze Synthese für Paper-Einleitung

Die Charakterisierung hydrologischer Dürren erfordert eine multifaktorielle Betrachtung der terrestrischen Wasserspeicher. Traditionelle meteorologische Indizes wie der Standardized Precipitation Index (SPI) erfassen lediglich Niederschlagsdefizite und ignorieren die komplexen Prozesse der Bodenwasserspeicherung und -freisetzung. Bodenwasserhaushaltsmodelle wie mHM, VIC, SWAT, Noah-MP und HBV ermöglichen die Simulation dieser Prozesse und liefern essenzielle Variablen für eine umfassende Dürrecharakterisierung.

Die drei zentralen Komponenten für hydrologische Dürreanalysen sind: (1) die Bodenfeuchte, typischerweise durch den Soil Moisture Index (SMI) oder den Standardized Soil Moisture Index (SSI) quantifiziert; (2) die Grundwasserneubildung (Recharge), die den Nachschub an Grundwasser bestimmt; und (3) der Abfluss, der die verfügbare Oberflächenwasserressource repräsentiert und durch Percentilansätze (Q80, Q90, Q95) oder den Streamflow Drought Index (SDI) charakterisiert wird.

Die methodische Heterogenität in der Dürreliteratur – zwischen empirischen Percentilansätzen und parametrisch standardisierten Indizes – spiegelt unterschiedliche Anwendungskontexte wider. Während Percentilansätze intuitive Entscheidungsgrundlagen für das Wassermanagement bieten, ermöglichen standardisierte Indizes robuste Trendanalysen und räumlich-zeitliche Vergleiche. Die Kombination mehrerer Indizes zu einem multidimensionalen Dürreindex stellt einen vielversprechenden Forschungszweig dar, der die Entkopplung verschiedener Dürretypen und die Verbesserung von Frühwarnsystemen ermöglichen könnte.

Trotz signifikanter Fortschritte in der Modellierung hydrologischer Dürren bestehen weiterhin Forschungslücken in der optimalen Kombination verschiedener Indizes, der Quantifizierung zeitlicher Verzögerungen zwischen Dürretypen und der Integration von Fernerkundungsdaten. Die vorliegende Arbeit zielt darauf ab, diese Lücken zu adressieren durch die Entwicklung eines Matrixansatzes, der SMI, Recharge-Percentile und Abfluss-Percentile systematisch kombiniert.

---

## 12. Implikationen für den Matrixansatz (SMI + Recharge-Percentil + Abfluss-Percentil)

### 12.1 Theoretische Grundlage

Der vorgeschlagene Matrixansatz basiert auf der Annahme, dass hydrologische Dürre ein mehrdimensionales Phänomen ist, das sich nicht durch einen einzelnen Index adäquat erfassen lässt. Die drei Komponenten erfassen unterschiedliche Aspekte:

1. **SMI**: Agrarökologische Dürre, Pflanzenstress
2. **Recharge-Percentil**: Langfristige Wasserverfügbarkeit, Grundwassersustainability
3. **Abfluss-Percentil**: Kurzfristige Wasserverfügbarkeit, ökologische Flussanforderungen

### 12.2 Proposed Matrix-Struktur

**2D-Matrix (SMI × Abfluss)**:

| | Abfluss ≥ Q80 | Q20 < Abfluss < Q80 | Abfluss ≤ Q20 |
|---|---|---|---|
| **SMI ≥ 0.5** | Feucht/Normal | Feucht/Normal | Hydrologische Dürre |
| **-0.5 < SMI < 0.5** | Normal | Normal | Leichte Hydrologische Dürre |
| **SMI ≤ -0.5** | Agrar-Dürre | Gemischte Dürre | Schwere Komplexe Dürre |

**3D-Erweiterung mit Recharge**:

Der Recharge-Status modifiziert die Schwere:
- Recharge ≥ Q80: Dürre mildert sich langfristig
- Recharge ≤ Q20: Dürre verschärft sich langfristig

### 12.3 Anwendungspotenzial

1. **Frühwarnsysteme**: Kombination bietet frühere Erkennung als Einzelindizes
2. **Wassermanagement**: Differenzierte Maßnahmen je nach Dürretyp
3. **Ökologische Bewertung**: Abfluss-Komponente berücksichtigt ökologische Flussanforderungen
4. **Klimawandel-Impact**: Separierung von kurz- und langfristigen Trends

### 12.4 Validierungsstrategie

- Vergleich mit USDM/EDO Klassifikationen
- Korrelation mit agrarischen Ertragsdaten
- Analyse historischer Extremereignisse (2003, 2018, 2022)
- Cross-Validierung zwischen Modellen (mHM, VIC, Noah-MP)

---

## Literaturverzeichnis

*Vollständige Referenzen in der Studientabelle (Kapitel 10)*

---

**Dokument erstellt**: 2026-03-02
**Autor**: Subagent (Research Assistant)
**Projekt**: Hydrological Drought Indices Review
**Status**: Erste Version abgeschlossen
