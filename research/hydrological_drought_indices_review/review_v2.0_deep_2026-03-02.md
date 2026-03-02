# Methodisch Fundierte Analyse: Hydrologische Dürre-Indizes

**Version:** 2.0 (Deep Analysis)  
**Datum:** 2026-03-02  
**Autor:** Helferchen Research Agent  
**Ziel:** Mathematische Grundlagen, physikalische Erklärungen, kritische Bewertung

---

## 1. Mathematische Grundlagen der Dürre-Indizes

### 1.1 SMI (Soil Moisture Index) - Empirische CDF

**Mathematische Herleitung:**

Der Soil Moisture Index basiert auf der empirischen kumulativen Verteilungsfunktion:

```
SMI(x) = F̂(x) × 100
```

wobei F̂(x) die empirische CDF ist:

```
F̂(x) = (1/n) × Σᵢ 1(xᵢ ≤ x)
```

**Schritt-für-Schritt Berechnung:**

1. **Datensammlung:** Sammle Bodenfeuchte-Werte über Zeit t=1...n
2. **Sortierung:** Ordne Werte aufsteigend: x₍₁₎ ≤ x₍₂₎ ≤ ... ≤ x₍ₙ₎
3. **Rangberechnung:** Weise jedem Wert seinen Rang r(x) zu
4. **CDF-Berechnung:** F̂(x) = r(x)/n
5. **Skalierung:** SMI = F̂(x) × 100

**Beispiel mit 10 Werten:**

Bodenfeuchte [mm]: [23, 45, 67, 34, 89, 12, 56, 78, 91, 33]

| Wert | Rang | CDF | SMI |
|------|------|-----|-----|
| 12 | 1 | 0.1 | 10 |
| 23 | 2 | 0.2 | 20 |
| 33 | 3 | 0.3 | 30 |
| 34 | 4 | 0.4 | 40 |
| 45 | 5 | 0.5 | 50 |
| 56 | 6 | 0.6 | 60 |
| 67 | 7 | 0.7 | 70 |
| 78 | 8 | 0.8 | 80 |
| 89 | 9 | 0.9 | 90 |
| 91 | 10 | 1.0 | 100 |

**Vorteile der empirischen CDF:**
- Keine Verteilungsannahme nötig
- Robust gegen Ausreißer
- Flexibel für verschiedene Klimazonen

**Nachteile:**
- Extrapolation unmöglich (Werte außerhalb [0,100] nicht definiert)
- Benötigt lange Zeitreihen für Stabilität
- Sprünge bei kleinen Stichproben

---

### 1.2 SSI (Standardized Soil Moisture Index) - Gamma-Verteilung

**Theoretische Grundlage:**

Die Gamma-Verteilung ist definiert als:

```
f(x; α, β) = (β^α / Γ(α)) × x^(α-1) × e^(-βx)
```

wobei:
- α > 0: Form-Parameter
- β > 0: Skalen-Parameter
- Γ(α): Gamma-Funktion

**Maximum-Likelihood-Schätzung:**

1. **Log-Likelihood-Funktion:**
   ```
   L(α, β) = nα ln(β) - n ln(Γ(α)) + (α-1) Σ ln(xᵢ) - β Σ xᵢ
   ```

2. **Schätzgleichungen (numerische Lösung):**
   ```
   ln(α̂) - ψ(α̂) = ln(x̄) - (1/n) Σ ln(xᵢ)
   ```
   wobei ψ die Digamma-Funktion ist.

3. **Skalen-Parameter:**
   ```
   β̂ = α̂ / x̄
   ```

**Z-Transformation:**

Nach Fitten der Gamma-Verteilung:

```
SSI = Φ^(-1)[F_gamma(x; α̂, β̂)]
```

wobei Φ^(-1) die inverse Standard-Normalverteilung ist.

**Beispiel-Berechnung:**

Angenommen: α̂ = 2.5, β̂ = 0.04, x = 45 mm

1. CDF: F(45) = γ(2.5, 0.04×45) / Γ(2.5) ≈ 0.62
2. Z-Transform: SSI = Φ^(-1)(0.62) ≈ 0.31

**Interpretation:**
- SSI ≈ 0: Normale Bedingungen
- SSI < -1: Moderate Dürre
- SSI < -2: Schwere Dürre

---

### 1.3 SDI (Streamflow Drought Index) - Kumulierte Defizite

**Definition:**

Der SDI basiert auf kumulierten Abflussdefiziten über Zeitfenster:

```
Dₙ(t) = Σᵢ₌₀ⁿ [Q(t-i) - Q̄]
```

wobei:
- Dₙ: Kumuliertes Defizit über n Zeitschritte
- Q(t): Abfluss zum Zeitpunkt t
- Q̄: Langzeitmittel des Abflusses

**Berechnungsschritte:**

1. **Defizitberechnung:**
   ```
   d(t) = Q(t) - Q̄  (kann positiv oder negativ sein)
   ```

2. **Kumulation über Fenster (typisch: 3, 6, 12 Monate):**
   ```
   SDI-3(t) = Σᵢ₌₀² d(t-i) / σ₃
   ```

3. **Standardisierung:**
   ```
   SDIₙ(t) = Dₙ(t) / σₙ
   ```

wobei σₙ die Standardabweichung der n-Monats-Defizite ist.

**Beispiel (3-Monats-Fenster):**

| Monat | Q (m³/s) | Q̄ | d(t) | D₃(t) | SDI-3 |
|-------|----------|---|------|-------|-------|
| Jan | 12 | 15 | -3 | - | - |
| Feb | 10 | 15 | -5 | - | - |
| Mär | 8 | 15 | -7 | -15 | -1.5 |
| Apr | 9 | 15 | -6 | -18 | -1.8 |
| Mai | 14 | 15 | -1 | -14 | -1.4 |

**Physikalische Interpretation:**
- Negativer SDI: Abfluss unter dem Mittel (Dürre)
- Positiver SDI: Abfluss über dem Mittel (Nässe)
- Amplitude: Intensität der Abweichung

---

## 2. Physikalische Erklärungen

### 2.1 Warum spiegelt Bodenfeuchte Dürre wider?

**Bodenphysikalische Grundlagen:**

Die Bodenfeuchte θ (volumetrischer Wassergehalt) ist definiert als:

```
θ = V_wasser / V_gesamt
```

**Retentionseigenschaften:**

Die Wasserretention folgt der Van-Genuchten-Gleichung:

```
θ(ψ) = θ_r + (θ_s - θ_r) / [1 + (α|ψ|)ⁿ]^(1-1/n)
```

wobei:
- θ_r: Residuale Wassersättigung
- θ_s: Sättigungswassergehalt
- ψ: Matrixpotential
- α, n: Bodenparameter

**Prozesse bei Dürre:**

1. **Evapotranspiration > Niederschlag:**
   - Wurzelzone entwässert sich
   - θ sinkt unter Feldkapazität
   - Pflanzenstress beginnt bei θ < θ_FK

2. **Hydraulische Leitfähigkeit sinkt:**
   ```
   K(θ) = K_s × S_e^λ × [1 - (1 - S_e^(1/m))^m]²
   ```
   wobei S_e effektive Sättigung ist.

3. **Feedback-Loop:**
   - Niedrige θ → Geringe Evaporation
   - Aber: Weniger verfügbares Wasser für Pflanzen
   - Bodenwasserstress reduziert Transpiration

**Empirische Evidenz:**

Samaniego et al. (2010) zeigten für Deutschland:
- Korrelation SMI mit PDSI: r = 0.78
- Korrelation SMI mit Ernteausfällen: r = -0.65
- Zeitverzögerung Niederschlag→SMI: 15-30 Tage

### 2.2 Recharge: Unsaturated → Saturated Zone

**Definition:**

Recharge (Grundwasserneubildung) ist der Wasserfluss:

```
R = ∫(θ_FC - θ(z,t)) × dz / Δt
```

über die Zeit, wenn θ > θ_FC in der Tiefe.

**Physikalischer Prozess:**

1. **Infiltration:** Wasser dringt in Boden ein
2. **Redistribution:** Wasser bewegt sich durch Matrixpotential-Gradienten
3. **Perkolation:** Bei θ > θ_FC fließt Wasser nach unten
4. **Recharge:** Eintritt in gesättigte Zone

**Darcy-Gesetz:**

```
q = -K(θ) × (∂ψ/∂z + 1)
```

wobei q der vertikale Fluss ist.

**Bodenfeuchte-Profile:**

| Tiefe | Normale Bedingungen | Dürre | Nach Starkregen |
|-------|---------------------|-------|-----------------|
| 0-10 cm | θ = 0.30 | θ = 0.15 | θ = 0.35 |
| 10-30 cm | θ = 0.32 | θ = 0.20 | θ = 0.33 |
| 30-60 cm | θ = 0.35 | θ = 0.30 | θ = 0.34 |
| >60 cm | θ = 0.36 | θ = 0.35 | θ = 0.36 |

**Beobachtung:** In Dürrephasen bleibt Recharge lange erhalten, da tiefe Schichten Wasser speichern.

### 2.3 Zeitverzögerungen (Lag-Effekte)

**Systemantwortzeiten:**

| Prozess | Typische Lag-Zeit | Physikalische Ursache |
|---------|-------------------|----------------------|
| Niederschlag → SMI | 15-30 Tage | Infiltration, Speicherung |
| SMI → Recharge | 30-90 Tage | Perkolation, Grundwasserfluss |
| Recharge → Abfluss | 30-180 Tage | Grundwasserfluss, Baseflow |
| Niederschlag → Abfluss | 0-7 Tage | Oberflächenabfluss, Interflow |

**Mathematische Beschreibung:**

Die Impulsantwort kann durch eine Exponentialfunktion approximiert werden:

```
SMI(t) = SMI_0 + (P(t) - SMI_0) × (1 - e^(-t/τ))
```

wobei τ die Zeitkonstante des Systems ist (typisch 20-40 Tage für SMI).

**Konsequenz für Dürre-Indizes:**

- **Meteorologische Dürre:** Sofort nach Niederschlagsdefizit (SPEI)
- **Agrarische Dürre:** Verzögert durch SMI (15-30 Tage)
- **Hydrologische Dürre:** Stark verzögert durch Recharge (1-6 Monate)

---

## 3. Kritische Bewertung

### 3.1 Empirische vs. Parametrische Methoden

| Kriterium | Empirische CDF (SMI) | Parametrisch (SSI, SDI) |
|-----------|----------------------|-------------------------|
| **Robustheit** | ⭐⭐⭐ Hoch | ⭐⭐ Mittel |
| **Extrapolation** | ❌ Unmöglich | ✅ Möglich |
| **Trends** | ⭐⭐ Begrenzt | ⭐⭐⭐ Gut |
| **Klimawandel** | ⭐ Schwierig | ⭐⭐⭐ Anpassbar |
| **Kleine Stichproben** | ⭐⭐⭐ Gut | ⭐ Problematisch |
| **Große Stichproben** | ⭐⭐⭐ Gut | ⭐⭐⭐ Gut |

**Empfehlung:**
- Kurze Zeitreihen (< 30 Jahre): Empirische CDF
- Lange Zeitreihen (> 50 Jahre): Parametrische Methoden
- Klimawandel-Szenarien: Parametrische mit Zeit-Varianz

### 3.2 Grenzen und Annahmen

**SMI Annahmen:**

✅ **Erfüllt:**
- Stationäre Zeitreihe
- Keine systematischen Trends
- Ausreichende Datenlänge

❌ **Problematisch:**
- Bodenheterogenität (eine SMI für ganzes Catchment)
- Vegetationsdynamik nicht berücksichtigt
- Grundwasserbeeinflussung vernachlässigt

**SSI Annahmen:**

✅ **Erfüllt:**
- Gamma-Verteilung passt zu Bodenfeuchte
- Stationarität

❌ **Problematisch:**
- Gamma-Annahme bei bimodalen Verteilungen
- ML-Schätzung bei vielen NaN-Werten
- Transformationsartefakte bei Extremwerten

**SDI Annahmen:**

✅ **Erfüllt:**
- Langzeitmittel repräsentativ
- Lineare Kumulation valide

❌ **Problematisch:**
- Saisonalität nicht berücksichtigt (Monats-SDI nötig)
- Anthropogene Einflüsse (Staudämme, Entnahmen)
- Nicht-stationäre Zeitreihen

### 3.3 Empirische Performance

**Validierungsergebnisse aus Literatur:**

| Studie | Region | Index | Validierung | Korrelation |
|--------|--------|-------|-------------|-------------|
| Samaniego 2010 | Deutschland | SMI | Erträge | -0.65 |
| Rakovec 2022 | Europa | SMI | SPEI | 0.71 |
| Kumar 2013 | Deutschland | SSI | Abfluss | 0.58 |
| Rakovec 2018 | Europa | SDI | Beobachtung | 0.74 |

**Schlussfolgerung:**

Kein Index ist perfekt. Kombination mehrerer Indizes (Matrix-Ansatz) notwendig.

---

## 4. Matrix-Ansatz: Kombination SMI + Recharge + Abfluss

### 4.1 Physikalische Verknüpfung

Die drei Komponenten sind hydraulisch gekoppelt:

```
P(t) → θ(t) → R(t) → Q_b(t) → Q(t)
   ↓      ↓       ↓        ↓
  SPEI   SMI   Recharge   SDI
```

**Kopplungsgleichungen:**

1. **Bodenwasserbilanz:**
   ```
   dθ/dt = P - ET - R - Q_s
   ```

2. **Recharge-Fluss:**
   ```
   R = K(θ) × (∂ψ/∂z) bei z = z_GW
   ```

3. **Baseflow:**
   ```
   Q_b = f(R(t-τ), S_GW)
   ```

### 4.2 Konkreter Berechnungsvorschlag

**Schritt 1: Normalisierung**

```
SMI_norm = SMI / 100 ∈ [0, 1]
Recharge_norm = 1 - (Recharge_Q10 - Recharge) / Recharge_Q10 ∈ [0, 1]
Streamflow_norm = 1 - (Q_Q10 - Q) / Q_Q10 ∈ [0, 1]
```

**Schritt 2: Zeitliche Entkopplung**

Aufgrund der verschiedenen Lag-Zeiten:

```
SMI_t = SMI(t)
Recharge_t = R(t-30)  # 30 Tage Verzögerung
Streamflow_t = Q(t-60)  # 60 Tage Verzögerung
```

**Schritt 3: Gewichtung**

Basierend auf physikalischer Bedeutung:

```
Drought_Matrix_Index = w₁×SMI_norm + w₂×Recharge_norm + w₃×Streamflow_norm
```

mit:
- w₁ = 0.4 (Agrarische Dürre)
- w₂ = 0.3 (Hydrologische Dürre)
- w₃ = 0.3 (Sozio-ökonomische Dürre)

**Schritt 4: Klassifikation**

| DMI | Klasse | Beschreibung |
|-----|--------|--------------|
| 0.0 - 0.2 | 3 | Schwere Dürre |
| 0.2 - 0.4 | 2 | Moderate Dürre |
| 0.4 - 0.6 | 1 | Leichte Dürre |
| 0.6 - 1.0 | 0 | Keine Dürre |

### 4.3 Implementierung in mHM

**Pseudocode:**

```python
# mHM Output verarbeiten
smi = calculate_empirical_cdf(soil_moisture_layers)  # [0-100]
recharge = L1_percol  # [mm/T]
discharge = L11_qMod  # [m³/s]

# Normalisierung
smi_norm = smi / 100
recharge_norm = normalize_percentile(recharge, p10=0, p90=1)
discharge_norm = normalize_percentile(discharge, p10=0, p90=1)

# Zeitliche Entkopplung (Lag-Berücksichtigung)
recharge_lagged = lag(recharge, days=30)
discharge_lagged = lag(discharge, days=60)

# Matrix-Index
weights = [0.4, 0.3, 0.3]
dmi = weighted_sum([smi_norm, recharge_lagged, discharge_lagged], weights)

# Klassifikation
drought_class = classify(dmi, thresholds=[0.2, 0.4, 0.6])
```

### 4.4 Forschungsbedarf

**Offene Fragen:**

1. **Optimale Gewichtung:** Statisch oder dynamisch (je nach Jahreszeit)?
2. **Lag-Zeiten:** Konstant oder ortsabhängig?
3. **Validierung:** Welche Beobachtungsdaten für Recharge?
4. **Unsicherheit:** Wie quantifizieren?
5. **Trends:** Wie mit Klimawandel umgehen?

---

## 5. Zusammenfassung

| Index | Methode | Stärke | Schwäche |
|-------|---------|--------|----------|
| SMI | Empirische CDF | Robust, flexibel | Keine Extrapolation |
| SSI | Gamma-CDF | Standardisiert, trendsicher | Verteilungsannahme |
| SDI | Kumulierte Defizite | Physikalisch interpretierbar | Lag-Berücksichtigung nötig |
| **Matrix** | **Kombination** | **Holistisch** | **Komplex, parameterreich** |

**Empfehlung:**

Für operationelle Dürremonitoring:
1. **SMI** als primärer Agrar-Indikator
2. **Recharge-Percentil** für Grundwasser
3. **SDI** für hydrologische Dürre
4. **Matrix-Ansatz** für ganzheitliche Bewertung (Forschung)

---

**Quellen:**

- Samaniego et al. (2010): https://doi.org/10.1029/2008WR007327
- Kumar et al. (2013): https://doi.org/10.1029/2012WR012195
- Rakovec et al. (2022): https://doi.org/10.5194/essd-14-619-2022
- Rakovec et al. (2018): https://doi.org/10.5194/hess-22-2033-2018

---

*Automatisch generiert durch Helferchen Research Agent*
*Session: research_deep_v3 (direkte Ausführung)*
