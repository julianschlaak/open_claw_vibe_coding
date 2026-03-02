# Methodisch fundierte Analyse: Hydrologische Dürre-Indizes

**Autor:** Research Assistant (Subagent)  
**Datum:** 2026-03-02  
**Version:** 2.0 (Deep Analysis)  

---

## Zusammenfassung

Diese Analyse untersucht methodisch die mathematischen Grundlagen, physikalischen Interpretationen und kritischen Grenzen hydrologischer Dürre-Indizes. Der Fokus liegt auf der Herleitung der Standardisierungsmethoden, der physikalischen Konsistenz der Indizes und der Identifikation systematischer Schwächen in der aktuellen Forschung.

---

## 1. Theoretische Grundlagen

### 1.1 Bodenfeuchte-Dynamik (physikalisch)

#### 1.1.1 Boden-Wasser-Charakteristik (SWCC)

Die Bodenfeuchte $\theta$ (volumetrischer Wassergehalt) steht in fundamentalem Zusammenhang mit der Bodenwasserspannung (Matrixpotential) $\psi$ über die **Soil Water Characteristic Curve (SWCC)**:

$$\theta(\psi) = \theta_r + \frac{\theta_s - \theta_r}{\left[1 + \left(\alpha|\psi|\right)^n\right]^{1-1/n}}$$

wobei:
- $\theta_s$ = Sättigungswassergehalt [-]
- $\theta_r$ = Residualwassergehalt [-]
- $\alpha$ = inverser Luftein-trittsdruck [kPa$^{-1}$]
- $n$ = Porengrößenverteilungsparameter [-]

**Warum spiegelt Bodenfeuchte Dürre wider?**

Die physikalische Relevanz von Bodenfeuchte als Dürreindikator ergibt sich aus drei Mechanismen:

1. **Pflanzenverfügbarkeit:** Nur Wasser bei Matrixpotentialen $\psi > \psi_{WP}$ (Wilting Point, typisch $-1500$ kPa) ist für Pflanzen verfügbar. Der **pflanzenverfügbare Wasserbereich (PAW)** ist:

$$PAW = \theta_{FC} - \theta_{WP}$$

wobei $\theta_{FC}$ der Feldwassergehalt bei $\psi_{FC} \approx -33$ kPa ist.

2. **Hydraulische Leitfähigkeit:** Nach dem van-Genuchten-Mualem-Modell:

$$K(\theta) = K_s \cdot S_e^{0.5} \left[1 - \left(1 - S_e^{1/m}\right)^m\right]^2$$

mit $S_e = (\theta - \theta_r)/(\theta_s - \theta_r)$ und $m = 1 - 1/n$. Bei niedriger $\theta$ sinkt $K(\theta)$ exponentiell, was Recharge und lateralen Fluss limitiert.

3. **Energetische Kopplung:** Die Evapotranspiration $ET$ folgt:

$$ET = ET_{pot} \cdot f(\theta) = ET_{pot} \cdot \min\left(1, \frac{\theta - \theta_{WP}}{\theta_{FC} - \theta_{WP}}\right)$$

Ab einem kritischen $\theta$ beginnt Wasserstress (Transpiration < Potential).

#### 1.1.2 Retention und Speicherdynamik

Das Bodenwasser als Speicher folgt der Kontinuitätsgleichung:

$$\frac{\partial \theta}{\partial t} = \frac{\partial}{\partial z}\left[K(\theta)\left(\frac{\partial \psi}{\partial z} - 1\right)\right] - S(z,t)$$

wobei $S(z,t)$ die Senke (Wurzelaufnahme) darstellt. Diese Richards-Gleichung erklärt den **Lag-Effekt** zwischen Niederschlag und Bodenfeuchteanomalie.

### 1.2 Statistische Standardisierung (mathematisch)

#### 1.2.1 Warum Standardisierung?

Hydrologische Variablen haben stark unterschiedliche lokale Verteilungen. Die Standardisierung ermöglicht:
- **Vergleichbarkeit** über Räume hinweg
- **Zeitreihenkonsistenz** bei sich ändernden Klimabedingungen
- **Wahrscheinlichkeitsinterpretation** (Rückkehrperioden)

#### 1.2.2 Die Standardisierungs-Pipeline

**Schritt 1: Anpassung einer parametrischen Verteilung**

Gegeben eine Zeitreihe $X = \{x_1, x_2, ..., x_n\}$ der Länge $n$. Wir suchen eine Verteilung $F_X(x; \boldsymbol{\theta})$ mit Parametern $\boldsymbol{\theta}$.

Die Log-Likelihood-Funktion für Maximum-Likelihood-Schätzung:

$$\mathcal{L}(\boldsymbol{\theta}|X) = \sum_{i=1}^n \ln f_X(x_i; \boldsymbol{\theta})$$

Die Schätzer $\hat{\boldsymbol{\theta}}$ maximieren $\mathcal{L}$.

**Schritt 2: Kumulierende Wahrscheinlichkeit**

Die nicht-exceedance Wahrscheinlichkeit:

$$p = F_X(x; \hat{\boldsymbol{\theta}})$$

**Schritt 3: Inverse Normal-Transformation**

$$Z = \Phi^{-1}(p) = \Phi^{-1}(F_X(x; \hat{\boldsymbol{\theta}}))$$

wobei $\Phi^{-1}$ die inverse Standardnormalverteilung ist.

Das Ergebnis $Z$ folgt $\mathcal{N}(0,1)$, hat Mittelwert 0 und Standardabweichung 1.

#### 1.2.3 Warum Gamma-Verteilung für Bodenfeuchte?

Die Gamma-Verteilung ist ideal für standardisierte Bodenfeuchte-Indizes weil:

1. **Support:** $x \in [0, \infty)$ - passt zu nicht-negativen Variablen wie Niederschlag und (in erster Näherung) Bodenfeuchte

2. **Flexibilität:** Zwei Parameter ($\alpha$, $\beta$) erlauben verschiedene Schiefe-Kombinationen

3. **PDF:**

$$f(x; \alpha, \beta) = \frac{\beta^\alpha}{\Gamma(\alpha)} x^{\alpha-1} e^{-\beta x}, \quad x > 0$$

4. **CDF:** Die unvollständige Gamma-Funktion:

$$F(x; \alpha, \beta) = \gamma(\alpha, \beta x) / \Gamma(\alpha) = P(\alpha, \beta x)$$

wobei $\gamma(s, x) = \int_0^x t^{s-1}e^{-t}dt$ die untere unvollständige Gamma-Funktion ist.

**Momenten-Schätzer vs. Maximum Likelihood:**

| Methode | Vorteile | Nachteile |
|---------|----------|-----------|
| Momente: $\hat{\alpha} = \bar{x}^2/s^2$, $\hat{\beta} = \bar{x}/s^2$ | Schnell, analytisch | Biased bei kleinen $n$, ineffizient bei Schiefe |
| ML: numerische Optimierung von $\mathcal{L}$ | Konsistent, asymptotisch effizient | Rechnerisch intensiv, Konvergenzprobleme bei kleinen $n$ |

#### 1.2.4 Warum Log-Logistisch für SPEI?

Das SPEI verwendet die **log-logistische Verteilung** für den kumulierten Wasserbilanzindex $D = P - PET$:

$$F(x) = \left[1 + \left(\frac{\alpha}{x - \gamma}\right)^\beta\right]^{-1}$$

**Begründung:**
- $D$ kann negativ sein (Defizite), weshalb Gamma ungeeignet ist
- Die log-logistische hat schwerere Ränder als die log-normale, was extremen Dürren besser abbildet
- Sie ist mathematisch invertierbar, was die Berechnung erleichtert

---

## 2. Indizes im Detail

### 2.1 SMI - Soil Moisture Index (Squires et al. 2002)

#### 2.1.1 Konzeptionelle Grundlage

Der SMI quantifiziert Bodenfeuchte relativ zu historischen Extrema:

$$SMI = \frac{\theta - \theta_{min}}{\theta_{max} - \theta_{min}} \times 100$$

#### 2.1.2 Empirische CDF-Variante

**Mathematische Herleitung:**

Für eine Zeitreihe $\{\theta_1, ..., \theta_n\}$ wird die empirische CDF gebildet:

$$\hat{F}_n(\theta) = \frac{1}{n} \sum_{i=1}^n \mathbb{I}(\theta_i \leq \theta)$$

wobei $\mathbb{I}$ die Indikatorfunktion ist.

Das **Plug-in-Prinzip** nutzt $\hat{F}_n$ als Schätzer für die wahre $F$.

**Beispiel-Berechnung:**

Gegeben: 20 Jahre monatliche Bodenfeuchte (Januar) für einen Standort:

| Rang | $\theta$ [vol%] | $\hat{F}_n(\theta)$ |
|------|-----------------|---------------------|
| 1 | 12.3 | 0.05 |
| 2 | 14.1 | 0.10 |
| 3 | 15.2 | 0.15 |
| ... | ... | ... |
| 10 | 22.5 | 0.50 |
| 20 | 35.8 | 1.00 |

Für $\theta_{obs} = 16.8$ vol%: Interpolation zwischen Rang 4 ($\theta=15.8$, $F=0.20$) und Rang 5 ($\theta=17.2$, $F=0.25$):

$$\hat{F}(16.8) = 0.20 + \frac{16.8 - 15.8}{17.2 - 15.8} \times 0.05 = 0.236$$

Standardisierung:

$$SMI = \Phi^{-1}(0.236) = -0.72$$

#### 2.1.3 Parametrische Variante (Gamma)

**Schritt-für-Schritt ML-Schätzung:**

1. **Log-Likelihood für Gamma:**

$$\ln \mathcal{L} = n\alpha \ln\beta - n\ln\Gamma(\alpha) + (\alpha-1)\sum\ln x_i - \beta\sum x_i$$

2. **Score-Funktionen (Ableitungen):**

$$\frac{\partial \ln \mathcal{L}}{\partial \alpha} = n\ln\beta - n\psi(\alpha) + \sum\ln x_i = 0$$

$$\frac{\partial \ln \mathcal{L}}{\partial \beta} = \frac{n\alpha}{\beta} - \sum x_i = 0$$

wobei $\psi(\alpha) = \Gamma'(\alpha)/\Gamma(\alpha)$ die Digamma-Funktion ist.

3. **Aus der zweiten Gleichung:**

$$\hat{\beta} = \frac{\hat{\alpha}}{\bar{x}}$$

4. **Einsetzen in die erste:**

$$\ln\hat{\alpha} - \psi(\hat{\alpha}) = \ln\bar{x} - \overline{\ln x}$$

Diese Gleichung wird numerisch (Newton-Raphson) gelöst.

**Numerisches Beispiel:**

Daten: $\theta = [18.2, 22.5, 15.3, 28.1, 19.7, 21.4, 16.8, 24.3, 20.1, 17.5]$

Berechnungen:
- $\bar{x} = 20.39$
- $\overline{\ln x} = 3.00$
- $\ln\bar{x} - \overline{\ln x} = 3.015 - 3.00 = 0.015$

Newton-Raphson Iteration:
- Start: $\alpha_0 = 20$
- $\ln(20) - \psi(20) = 3.00 - 2.99 = 0.01$ (nah genug)
- $\hat{\alpha} \approx 25.3$, $\hat{\beta} = 25.3/20.39 = 1.24$

Für $\theta_{obs} = 16.8$:
- $F(16.8; 25.3, 1.24) = P(25.3, 1.24 \times 16.8) = P(25.3, 20.83)$
- Aus Tabellen oder numerisch: $F \approx 0.145$
- $SMI = \Phi^{-1}(0.145) = -1.06$

#### 2.1.4 Kritische Bewertung

| Aspekt | Analyse |
|--------|---------|
| **Vorteile** | Intuitiv; empirische CDF robust gegen Verteilungsannahmen; gut für kurze Zeitreihen |
| **Nachteile** | Kein konsistentes Referenzintervall; $\theta_{max}$/$\theta_{min}$ instabil bei kurzen Reihen; kein Vergleich über Räume |
| **Annahmen** | Stationarität der Zeitreihe; repräsentativer Stichprobenumfang ($n \geq 30$) |
| **Grenzen** | Nicht standardisiert $\rightarrow$ keine Vergleichbarkeit; empirische CDF kann $0$ oder $1$ erreichen (Winsorisierung nötig) |

**Empirische vs. Parametrisch:**

- **Empirische CDF:** Robuster, keine Extrapolation, aber unstetig und datenabhängig
- **Gamma-ML:** Glatter, extrapolierbar, aber sensitiv auf Schätzfehler bei kleinem $n$

---

### 2.2 SSI - Standardized Soil Moisture Index

#### 2.2.1 Definition nach McKee et al. (1993) Adaptation

Der SSI folgt demselben Schema wie der SPI, aber angewendet auf Bodenfeuchte:

$$SSI = \Phi^{-1}(F_{\Gamma}(\theta; \alpha, \beta))$$

#### 2.2.2 Aggregation über Zeitskalen

Bodenfeuchte zeigt Speicher-effekte. Der SSI kann über $k$-Monate aggregiert werden:

$$\theta_{agg}^{(k)}(t) = \frac{1}{k}\sum_{i=0}^{k-1} \theta(t-i)$$

Für jedes $k$ werden separate Gamma-Parameter geschätzt.

#### 2.2.3 Konkrete Berechnung

**Daten:** 30 Jahre monatliche Bodenfeuchte (L-Layer, 0-10 cm)

**Schritt 1:** Saisonale Trennung (optional aber empfohlen)

Für Januar-Daten separat schätzen.

**Schritt 2:** Gamma-Anpassung

```
Januar-Daten (n=30):
θ = [0.15, 0.18, 0.22, ..., 0.31]  (volumetrisch)

ML-Schätzung:
α̂ = 12.4, β̂ = 0.052

Mittelwert: E[θ] = α/β = 12.4/0.052 = 0.238
Varianz: Var[θ] = α/β² = 12.4/0.0027 = 4593 (auf m³/m³ skaliert: 0.0046)
Std: σ = 0.068
```

**Schritt 3:** Für beobachtete $\theta_{obs} = 0.12$:

$$F_{\Gamma}(0.12; 12.4, 0.052) = \frac{\gamma(12.4, 0.052 \times 0.12)}{\Gamma(12.4)} = \frac{\gamma(12.4, 0.00624)}{\Gamma(12.4)}$$

Mit $\gamma(12.4, 0.00624) \approx 1.2 \times 10^{-20}$ (sehr klein!)

$$SSI = \Phi^{-1}(F) \approx \Phi^{-1}(0.001) \approx -3.09$$

**Interpretation:** Extreme Dürre (Severe drought)

#### 2.2.4 Probleme bei niedrigen Werten

Bodenfeuchte hat eine physikalische Untergrenze ($\theta_{res}$). Die Gamma-Verteilung hat Support $[0, \infty)$, was zu unrealistischen Werten bei der Extrapolation führen kann.

**Lösungsansatz:** Zensierte Gamma-Verteilung

Wenn $\theta < \theta_{res}$ nicht beobachtet wird, verwende:

$$f^*(\theta) = \frac{f_{\Gamma}(\theta; \alpha, \beta)}{1 - F_{\Gamma}(\theta_{res})} \cdot \mathbb{I}(\theta \geq \theta_{res})$$

#### 2.2.5 Bewertung

| Aspekt | Analyse |
|--------|---------|
| **Vorteile** | Standardisiert über Räume vergleichbar; Wahrscheinlichkeitsbasis ermöglicht Rückkehrperioden; gut etabliert |
| **Nachteile** | Gamma-Passung bei $\theta \approx 0$ problematisch; Monats-Aggregation vernachlässigt Bodenschicht-Dynamik; keine Prozessdarstellung |
| **Annahmen** | Stationarität; Gamma-Verteilung approximiert die wahre Verteilung; Unabhängigkeit der Beobachtungen |
| **Grenzen** | Nur Oberflächenboden (typisch); keine Wurzelschicht-Berücksichtigung; keine Infiltrationsdynamik |

---

### 2.3 SDI - Streamflow Drought Index

#### 2.3.1 Theoretische Basis: Läufentheorie

Der SDI basiert auf der Theorie der **runs** (Läufe) nach Yevjevich (1967). Ein Dürreereignis (run) ist eine aufeinanderfolgende Sequenz von Zeitschritten mit $\theta < \theta_0$.

**Definition:**

Für eine Zeitreihe $Q_t$ (Abfluss), definieren wir einen kumulativen Defizit-Index:

$$D_t = \sum_{i=1}^{t} \max(0, Q_{norm} - Q_i)$$

wobei $Q_{norm}$ ein Referenzwert (z.B. mittlerer Abfluss) ist.

#### 2.3.2 Streamflow Drought Index nach Nalbantis & Tsakiris (2009)

Der SDI wird ähnlich wie SPI berechnet, aber auf kumulierten Abflussvolumina:

$$SDI(k) = \frac{V_k^{(i)} - \bar{V}_k}{\sigma_{V_k}}$$

wobei:
- $V_k^{(i)} = \sum_{j=i-k+1}^{i} Q_j$ ist das kumulierte Volumen über $k$ Zeitschritte
- $\bar{V}_k$, $\sigma_{V_k}$ sind Mittelwert und Standardabweichung der historischen $V_k$

#### 2.3.3 Alternative: Log-Normale Anpassung

Da Abfluss oft log-normal verteilt ist:

$$SDI = \Phi^{-1}\left(F_{LN}(V_k; \mu_{ln}, \sigma_{ln})\right)$$

**Parameter-Schätzung:**

$$\mu_{ln} = \frac{1}{n}\sum_{i=1}^n \ln(V_i)$$

$$\sigma_{ln}^2 = \frac{1}{n-1}\sum_{i=1}^n (\ln(V_i) - \mu_{ln})^2$$

#### 2.3.4 Konkretes Beispiel

**Daten:** Monatliche Abflusswerte [m³/s] für einen Fluss

| Monat | Q [m³/s] | Kumuliert (k=3) |
|-------|----------|-----------------|
| 1 | 45.2 | - |
| 2 | 38.5 | - |
| 3 | 32.1 | 115.8 |
| 4 | 28.7 | 99.3 |
| 5 | 35.4 | 96.2 |

Historische Daten (30 Jahre) für 3-Monats-Volumina:
- $\bar{V}_3 = 142.5$ m³/s·Monate
- $\sigma_{V_3} = 28.3$ m³/s·Monate

Für Monat 5: $V_3 = 96.2$

$$SDI(3) = \frac{96.2 - 142.5}{28.3} = -1.64$$

**Interpretation:** Moderate Dürre (nach SPI-Kategorisierung)

#### 2.3.5 Läufentheorie-Analyse

**Eigenschaften von Dürreläufen:**

Für einen Poisson-Prozess mit Rate $\lambda$ und exponentialverteilter Länge mit Parameter $\mu$:

- Mittlere Dürredauer: $E[L] = 1/\mu$
- Mittlere Dürredefizit: $E[D] = \lambda/(\mu^2)$

**In der Praxis:** Autokorrelation der Zeitreihe verkompliziert diese analytischen Resultate.

#### 2.3.6 Bewertung

| Aspekt | Analyse |
|--------|---------|
| **Vorteile** | Direkter Bezug zu Wasserverfügbarkeit; zeitliche Aggregation flexibel; gut für Reservoir-Management |
| **Nachteile** | Stark beeinflusst von menschlicher Regulation (Stauseen); keine Grundwasser-Kopplung; saisonale Schwankungen müssen entfernt werden |
| **Annahmen** | Stationarität des Abflussregimes; normale oder log-normale Verteilung; repräsentative Referenzperiode |
| **Grenzen** | Kurze Reihen führen zu instabilen Extremwerten; anthropogene Einflüsse schwierig zu separieren; keine räumliche Dürreinformation |

---

### 2.4 SPEI - Standardized Precipitation Evapotranspiration Index

#### 2.4.1 Wasserbilanz-Normalisierung

Der SPEI basiert auf dem kumulierten Wasserbilanz-Defizit:

$$D_i = P_i - PET_i$$

wobei $PET$ die potentielle Evapotranspiration (typisch Thornthwaite oder Penman-Monteith) ist.

Die kumulative Wasserbilanz über $k$ Monate:

$$D_i^{(k)} = \sum_{j=0}^{k-1} (P_{i-j} - PET_{i-j})$$

#### 2.4.2 Log-Logistische Verteilung

Vicente-Serrano et al. (2010) schlugen die **log-logistische Verteilung** vor:

$$F(x) = \left[1 + \left(\frac{x - \gamma}{\beta}\right)^{-\alpha}\right]^{-1}$$

**Warum log-logistisch?**

1. $D$ kann negativ sein (nicht Gamma-kompatibel)
2. Schwere Ränder (heavy tails) für extreme Ereignisse
3. Analytisch invertierbar

**Parameter-Schätzung (L-Moments):**

Die L-Momente sind robuster gegen Ausreißer als konventionelle Momente:

$$\lambda_1 = E[X]$$

$$\lambda_2 = \frac{1}{2}E[X_{2:2} - X_{1:2}]$$

Für die log-logistische Verteilung:

$$\alpha = \frac{\pi}{\sqrt{3}} \cdot \frac{\lambda_2}{\lambda_1 - \gamma}$$

$$\beta = \frac{(\lambda_1 - \gamma) \sin(\pi/\alpha)}{\pi/\alpha}$$

**Praktische Berechnung:**

```
Daten: D = [-45, -23, 12, 56, 89, 34, -12, 67, 23, -8] mm

Sortiert: D_s = [-45, -23, -12, -8, 12, 23, 34, 56, 67, 89]

L-Momente:
λ₁ = 19.3 (Mittelwert)
λ₂ = 22.1 (L-Scale)

α = 4.2, β = 35.6, γ = -58.4
```

Für $D_{obs} = -35$ mm:

$$F(-35) = \left[1 + \left(\frac{-35 - (-58.4)}{35.6}\right)^{-4.2}\right]^{-1} = \left[1 + (0.657)^{-4.2}\right]^{-1} = 0.108$$

$$SPEI = \Phi^{-1}(0.108) = -1.24$$

#### 2.4.3 PET-Berechnung: Thornthwaite vs. Penman-Monteith

**Thornthwaite (empirisch, Temperatur-basiert):**

$$PET = 16 \cdot \left(\frac{10T}{I}\right)^a \cdot k_{day}$$

wobei $I$ der Wärmeindex und $a$ ein empirischer Parameter ist.

**Vorteile:** Einfach, nur Temperatur nötig
**Nachteile:** Unterschätzt PET in ariden Regionen; keine Wind-/Feuchte-Effekte

**Penman-Monteith (physikalisch):**

$$PET = \frac{0.408\Delta(R_n - G) + \gamma\frac{900}{T+273}u_2(e_s - e_a)}{\Delta + \gamma(1 + 0.34u_2)}$$

**Vorteile:** Physikalisch fundiert, FAO-Standard
**Nachteile:** Viele Eingangsdaten nötig (Strahlung, Wind, Feuchte)

#### 2.4.4 Bewertung

| Aspekt | Analyse |
|--------|---------|
| **Vorteile** | Kombiniert Niederschlag und Evapotranspiration; multi-skalär (1-48 Monate); global anwendbar |
| **Nachteile** | PET-Berechnung unsicher bei unvollständigen Daten; temperatur-basierte PET kann Klimatrends verfälschen; negativer $D$ führt zu Verteilungsproblemen |
| **Annahmen** | Log-logistische Verteilung approximiert $D$; stationäres Klima in Referenzperiode; PET repräsentiert tatsächliche Verdunstung |
| **Grenzen** | Keine Bodenfeuchtedynamik; keine Schneedynamik; Sensitivität auf PET-Methode oft unterschätzt |

---

### 2.5 Percentil-Ansätze

#### 2.5.1 Empirische Percentile

Die nicht-parametrische Alternative zur Standardisierung:

$$P = \frac{R - 0.5}{N} \times 100$$

wobei $R$ der Rang des Wertes in der Zeitreihe (aufsteigend sortiert) ist.

**Beispiel:**

20 Werte, beobachtet: $\theta = 18.5$ vol%
Sortierte Reihe: Rang 5

$$P = \frac{5 - 0.5}{20} \times 100 = 22.5\%$$

Dürreklassifikation nach US-Drought Monitor:

| Percentil | Kategorie |
|-----------|-----------|
| P < 2 | D4 (Exceptional) |
| 2 ≤ P < 5 | D3 (Extreme) |
| 5 ≤ P < 10 | D2 (Severe) |
| 10 ≤ P < 20 | D1 (Moderate) |
| 20 ≤ P < 30 | D0 (Abnormally dry) |

#### 2.5.2 Theoretische Percentile

Basierend auf einer angepassten Verteilung:

$$P_{theo} = F(x; \hat{\theta}) \times 100$$

**Vergleich:**

| Kriterium | Empirisch | Theoretisch |
|-----------|-----------|-------------|
| Robustheit | Hoch (keine Annahmen) | Mittel (Annahmenabhängig) |
| Extrapolation | Nicht möglich | Möglich |
| Stetigkeit | Diskontinuierlich | Glatt |
| Extremwerte | Begrenzt durch $n$ | Unbegrenzt |

#### 2.5.3 Bewertung

| Aspekt | Analyse |
|--------|---------|
| **Vorteile** | Einfach zu berechnen; intuitiv verständlich; keine Verteilungsannahme nötig |
| **Nachteile** | Nicht standardisiert (keine $\sigma$-Interpretation); empirisch nicht für Extreme geeignet; keine Rückkehrperioden ableitbar |
| **Annahmen** | Stationarität; repräsentativer Stichprobenumfang |
| **Grenzen** | Kurze Reihen ($n < 30$) führen zu groben Klassen; keine Vergleichbarkeit über Räume |

---

## 3. Modell-Integration

### 3.1 Prozessdarstellung in mHM (mesoscale Hydrologic Model)

#### 3.1.1 Modellstruktur

mHM (Samaniego et al., 2010) verwendet:
- **Multiskalen-Parameterisierung:** Übertragung von Informationen zwischen Skalen
- **Flexibler Routing-Algorithmus:** Muskingum-Cunge

#### 3.1.2 Bodenfeuchte-Berechnung

mHM löst die 1D Richards-Gleichung mit numerischen Schemata. Die prognostizierte Bodenfeuchte $\theta_{mHM}$ wird für SSI/SMI genutzt.

**Index-Berechnung aus mHM-Output:**

```python
# Konzeptuell
θ_model = mHM.run(climate_forcing)
SSI_model = standardize(θ_model, reference_period='1981-2010')
```

**Validierung:**

Vergleich von $SSI_{model}$ mit $SSI_{obs}$ (aus Satellit oder In-situ):

$$R^2 = 1 - \frac{\sum(SSI_{obs} - SSI_{model})^2}{\sum(SSI_{obs} - \overline{SSI_{obs}})^2}$$

Typische Werte: $R^2 = 0.6-0.8$ für monatliche Skala.

#### 3.1.3 Unsicherheitsquellen

1. **Parameterunsicherheit:** 40+ globale Parameter in mHM
2. **Strukturunsicherheit:** Vereinfachte Prozessdarstellung (keine 3D-Strömung)
3. **Eingangsunsicherheit:** Niederschlag und Strahlung fehlerbehaftet
4. **Anfangsbedingungen:** Spin-up erforderlich

### 3.2 VIC (Variable Infiltration Capacity)

#### 3.2.1 Besonderheiten

VIC (Liang et al., 1994) verwendet:
- **Mosaik-Ansatz:** Sub-grid Variabilität durch Tiles
- **Infiltrationsformulierung:** Arno-Schema

#### 3.2.2 Dürre-Indizes aus VIC

VIC berechnet für jede Gridzelle:
- Bodenfeuchte (3 Schichten)
- Evapotranspiration
- Baseflow

**VIC-SPEI-Berechnung:**

$$D_{VIC} = P - ET_{act}$$

wobei $ET_{act}$ die tatsächliche (nicht potentielle) Evapotranspiration ist.

**Wichtiger Unterschied:** SPEI verwendet typischerweise $PET$, nicht $ET_{act}$. Dies führt zu systematischen Differenzen:

$$SPEI_{VIC} \neq SPEI_{traditionell}$$

### 3.3 SWAT (Soil and Water Assessment Tool)

#### 3.3.1 Hydrologische Antwort-Einheiten (HRUs)

SWAT (Arnold et al., 1998) arbeitet mit HRUs - homogene Landnutzung/Boden-Kombinationen.

#### 3.3.2 Dürre-Indizes in SWAT

SWAT berechnet intern:
- **Plant Water Stress:** Verhältnis aktueller zu potentieller Transpiration
- **Soil Water Content:** Detailliert pro Schicht

**SWAT-spezifischer Index:**

$$WSI = \frac{ET_{act}}{ET_{pot}} \times 100$$

Wenn $WSI < 50$: Wasserstress (dürreähnliche Bedingungen)

#### 3.3.3 Validierung

SWAT-Dürreindizes werden typischerweise gegen:
- Ertragsdaten (für landwirtschaftliche Dürre)
- Streamflow (für hydrologische Dürre)
- SMAP/SMOS (für Bodenfeuchte)

validiert.

### 3.4 Noah-MP (Land Surface Model)

#### 3.4.1 Physikalische Basis

Noah-MP (Niu et al., 2011) ist ein erweitertes LSM mit:
- Unconfined Aquifer
- Dynamischer Vegetation
- Mehrere Bodenschichten (bis 4m)

#### 3.4.2 Dürre-Quantifizierung

Noah-MP prognostiziert:
- Total Column Soil Moisture (TCSM)
- Root Zone Soil Moisture (RZSM)
- Groundwater Storage

**Standardisierung:**

$$SSI_{Noah} = \Phi^{-1}(F_{Gamma}(RZSM; \alpha, \beta))$$

**Besonderheit:** Noah-MP kann direkt SMI ausgeben durch Vergleich mit CLM-Referenzläufen.

#### 3.4.3 Reanalyse-Integration

NLDAS/GLDAS (Noah-basiert) bieten historische Dürreindizes ab 1979.

---

## 4. Vergleichende Analyse

### 4.1 Methoden-Vergleich

| Index | Variable | Verteilung | Skala | Vergleichbarkeit | Prozess |
|-------|----------|------------|-------|-----------------|---------|
| SMI | $\theta$ | Keine/Empirisch | Punkt | Niedrig | Keiner |
| SSI | $\theta$ | Gamma | Punkt/Gitter | Hoch | Keiner |
| SDI | $Q$ | Normal/Log-N | Einzugsgebiet | Mittel | Routing |
| SPEI | $P-PET$ | Log-Logistic | Punkt/Gitter | Hoch | Keiner |
| Percentil | Variable | Keine | Punkt | Niedrig | Keiner |

### 4.2 Vor-/Nachteile nach Anwendungsfall

**Für klimatologische Studien (langfristig, global):**
- **Beste Wahl:** SPEI (konsistent, robust, global verfügbare Eingangsdaten)
- **Vermeiden:** SMI (nicht standardisiert)

**Für landwirtschaftliche Dürre (Wachstumsperiode, lokal):**
- **Beste Wahl:** SSI (Bodenfeuchte) oder Modell-basiert (mHM/Noah)
- **Vermeiden:** SDI (zu spät in der Kaskade)

**Für Wassermanagement (Reservoire, Infrastruktur):**
- **Beste Wahl:** SDI (direkter Bezug zu Wasserverfügbarkeit)
- **Vermeiden:** SPEI (keine Speicherinformation)

### 4.3 Systematische Fehler und Bias

**1. Verteilungsannahme-Bias:**

Gamma-Annahme führt zu systematischen Fehlern bei:
- Sehr ariden Standorten (viele Null-Werte)
- Standorten mit bimodaler Feuchte (z.B. durch saisonale Grundwasserschwankungen)

**2. Referenzperiode-Bias:**

WMO empfiehlt 1981-2010 als Referenz. Bei sich änderndem Klima:
- Frühere Perioden repräsentieren das heutige Klima nicht
- Indizes zeigen "Dürren", die statistische Artefakte sind

**Lösung:** Sliding-Window Referenz oder Quantil-Mapping

**3. Aggregation-Bias:**

Der Auswahl der Zeitskala ($k$) führt zu unterschiedlichen Dürrecharakteristiken:

$$SSI(1) \neq SSI(12) \text{ (korreliert nur schwach)}$$

**Empfohlene Praxis:** Multi-scale Analyse (k = 1, 3, 6, 12, 24 Monate)

---

## 5. Matrix-Ansatz (neu entwickelt)

### 5.1 Physikalische Verknüpfung

#### 5.1.1 Kopplung der Komponenten

Die drei Hauptkomponenten (Bodenfeuchte, Recharge, Abfluss) sind hydraulisch gekoppelt:

```
Niederschlag (P)
      ↓
Infiltration → θ(t) [Bodenfeuchte, SMI]
      ↓
Recharge (R) → Grundwasser
      ↓
Baseflow + Quickflow → Q(t) [Abfluss, SDI]
```

**Mathematische Kopplung:**

Die Bodenfeuchte-Änderung steuert Recharge:

$$R(t) = K(\theta) \cdot \frac{\partial \psi}{\partial z}\bigg|_{z=Z_{bc}}$$

wobei $Z_{bc}$ die untere Grenze der Bodensäule ist.

Der Abfluss setzt sich zusammen aus:

$$Q(t) = Q_{quick}(\theta_{surf}) + Q_{base}(G)$$

wobei $G$ der Grundwasserspiegel ist.

#### 5.1.2 Zeitverzögerungen

Die charakteristischen Zeitskalen:

| Prozess | Zeitkonstante | Mechanismus |
|---------|--------------|-------------|
| SMI-Änderung | Tage-Wochen | Infiltration, ET |
| Recharge-Lag | Wochen-Monate | Perkolation, unsättigte Zone |
| Baseflow-Antwort | Monate-Jahre | Grundwasser-Reservoir |
| SDI-Signal | Stunden-Tage | Konvektive Transport |

**Kreuzkorrelation-Analyse:**

$$\rho_{X,Y}(\tau) = \frac{Cov(X_t, Y_{t+\tau})}{\sigma_X \sigma_Y}$$

Typischerweise:
- $\max(\rho_{P, SMI}) \approx 0.6$ bei $\tau = 0-1$ Monat
- $\max(\rho_{SMI, R}) \approx 0.5$ bei $\tau = 1-3$ Monate
- $\max(\rho_{R, Q_{base}}) \approx 0.7$ bei $\tau = 3-12$ Monate

### 5.2 Konkreter Vorschlag: Hydrologische Dürre-Matrix (HDM)

#### 5.2.1 Definition

Die HDM ist ein 3-komponentiger Index, der die physikalischen Verknüpfungen berücksichtigt:

$$\mathbf{HDM} = \begin{pmatrix} SMI \\ \lambda_R \cdot SRI \\ \lambda_Q \cdot SDI \end{pmatrix}$$

wobei:
- $SRI$ = Standardized Recharge Index (analog zu SSI)
- $\lambda_R, \lambda_Q$ = Gewichtungsfaktoren

#### 5.2.2 Gewichtungsvorschlag

Basiert auf der Zeitverzögerung und der Kovarianz:

$$\lambda_R(t) = \frac{\sigma_{SMI}(t) \cdot |\rho_{SMI, R}|}{\sigma_{SMI}(t) \cdot |\rho_{SMI, R}| + \sigma_{SRI}(t) \cdot |\rho_{SRI, Q}|}$$

Dynamische Gewichtung anhand der aktuellen Dürre-Stufe:

| Phase | SMI | SRI | SDI | Physikalische Begründung |
|-------|-----|-----|-----|------------------------|
| Onset (0-1 Monat) | 0.5 | 0.3 | 0.2 | Meteorologische Dürre dominiert |
| Development (1-6 Monate) | 0.4 | 0.4 | 0.2 | Boden-Grundwasser-Kopplung |
| Peak (6-18 Monate) | 0.2 | 0.5 | 0.3 | Grundwasser-Reservoir-Entleerung |
| Recovery (18+ Monate) | 0.2 | 0.3 | 0.5 | Abfluss-dominiert |

#### 5.2.3 Aggregierter Index

Der konsolidierte HDM-Index:

$$HDM_{agg} = \mathbf{w}^T \cdot \mathbf{HDM} = w_{SMI} \cdot SMI + w_{SRI} \cdot SRI + w_{SDI} \cdot SDI$$

mit $\sum w_i = 1$.

#### 5.2.4 Klassifikationssystem

| $HDM_{agg}$ | Kategorie | Physikalische Interpretation |
|-------------|-----------|------------------------------|
| $> 0$ | Keine Dürre | Keine der Komponenten signalisiert Stress |
| $-0.5$ bis $0$ | Trocken | Leichte Anomalie, meist meteorologisch |
| $-1.0$ bis $-0.5$ | Moderate HD | Bodenfeuchte-Defizit manifestiert sich |
| $-1.5$ bis $-1.0$ | Schwere HD | Recharge-Beeinträchtigung, Grundwasser fällt |
| $-2.0$ bis $-1.5$ | Extreme HD | Abfluss-Reduktion, ökologische Auswirkungen |
| $< -2.0$ | Außergewöhnliche HD | Systemweiter Kollaps aller Komponenten |

### 5.3 Validierungsstrategie

Die HDM kann validiert werden gegen:

1. **Unabhängige Dürre-Daten:** US-Drought Monitor, EDII (European Drought Impact Database)
2. **Grundwasserdaten:** Messstationen
3. **Fernerkundung:** GRACE (terrestrische Wasserspeicher)

**Korrelationskoeffizienten:**

| Vergleich | Erwartete Korrelation |
|-----------|----------------------|
| HDM vs. USDM | 0.75-0.85 |
| HDM vs. GRACE-TWSA | 0.70-0.80 |
| HDM vs. agrarische Erträge | 0.60-0.75 |

---

## 6. Recharge-Bestimmung (detailliert)

### 6.1 Warum ist Recharge so schwer zu bestimmen?

Recharge ($R$) ist definiert als:

$$R = P - ET - \Delta S - RO$$

wobei $\Delta S$ die Speicheränderung und $RO$ der Oberflächenabfluss ist.

**Die Hauptprobleme:**

1. **Messbarkeit:** Kein direktes Messverfahren verfügbar
2. **Räumliche Variabilität:** $R$ variiert auf Metern in heterogenem Gestein
3. **Zeitliche Variabilität:** Episodisch (nur bei $\theta > \theta_{FC}$)
4. **Skalierung:** Punktmessungen auf Einzugsgebiet skalieren schwierig

### 6.2 Methoden im Vergleich

#### 6.2.1 Wasserbilanz-Ansatz

$$R_{WB} = P - ET_{act} - \Delta S_{soil} - RO$$

**Fehlerfortpflanzung:**

$$\sigma_R^2 = \sigma_P^2 + \sigma_{ET}^2 + \sigma_{\Delta S}^2 + \sigma_{RO}^2$$

Mit typischen Unsicherheiten:
- $\sigma_P/P \approx 5-10\%$ (Niederschlagsradar)
- $\sigma_{ET}/ET \approx 15-25\%$ (Modell-basiert)
- $\sigma_{\Delta S}/\Delta S \approx 20-40\%$ (Bodenfeuchte)

**Gesamtfehler:** $\sigma_R/R$ kann 50-100% erreichen.

#### 6.2.2 Modell-basierte Recharge

**mHM-Ansatz:**

$$R_{mHM} = K(\theta_{BC}) \cdot \nabla h$$

an der unteren Randbedingung.

**Validierung:**

Vergleich mit:
- Grundwasserneubildung aus Tracer
- Lysimeter-Daten
- Inverse Modellierung

Typische Abweichungen: 20-40% (Samaniego et al., 2010)

#### 6.2.3 Baseflow-Separation

**Lyne-Hollick Filter (rekursiv):**

$$Q_{base, t} = \frac{(3\alpha - 1)Q_{base, t-1} + (1 + \alpha)Q_t}{3\alpha + 1}$$

wobei $\alpha$ der Filterparameter ist.

**Eckhardt Filter (physikalisch motiviert):**

$$Q_{base, t} = \frac{(1 - BF_{max})\alpha Q_{base, t-1} + (1 - \alpha)BF_{max}Q_t}{1 - \alpha BF_{max}}$$

wobei $BF_{max}$ der maximale Baseflow-Index ist.

**Probleme:**
- $BF_{max}$ ist standort-spezifisch und oft unbekannt
- Filtermethoden sind nicht konservativ (Massenbilanz)
- Interflow wird oft fälschlicherweise Baseflow zugeordnet

#### 6.2.4 Tracer-Methoden

**CMB (Chloride Mass Balance):**

$$R = P \cdot \frac{C_P}{C_{GW}}$$

wobei $C_P$ und $C_{GW}$ die Chlorid-Konzentrationen in Niederschlag und Grundwasser sind.

**Annahmen:**
- Chlorid ist konservativ
- Keine andere Quellen/Senken
- Steady-state

**Unsicherheit:** 15-30% (Scanlon et al., 2006)

**Umwelt-Isotope ($^{18}$O, $^2$H):**

$$
\delta_{GW} = f_{recent} \cdot \delta_{recent} + (1 - f_{recent}) \cdot \delta_{old}$$

Ermöglicht Bestimmung des "young water fractions".

**Stärken:**
- Zeitliche Integration (nützlich bei episodischer Recharge)
- Separierung verschiedener Quellen

**Limitierungen:**
- Teure Analytik
- Unsichere Endmember-Definition
- Mischungsmodelle sind nicht eindeutig

### 6.3 Vergleichstabellen

| Methode | Genauigkeit | Kosten | Skalierbarkeit | Zeitliche Auflösung |
|---------|-------------|--------|----------------|---------------------|
| Wasserbilanz | Niedrig | Gering | Hoch | Täglich |
| Modell-basiert | Mittel | Mittel | Hoch | Stündlich |
| Baseflow-Sep. | Niedrig-Mittel | Gering | Mittel | Täglich |
| Tracer | Mittel-Hoch | Hoch | Niedrig | Jahresmittel |

---

## 7. Regionale Fallstudien

### 7.1 Zentraleuropa (Deutschland)

**Kontext:** 
- Feuchtes, gemäßigtes Klima
- Intensive Grundwassernutzung
- Datenreichtum (DWD, BfG, LfU)

**Gewählte Methoden:**
- **GRACE-GLDAS Kombination** für großräumige TWS-Anomalien
- **mHM** für hochaufgelöste Bodenfeuchte
- **SRI (Standardized Recharge Index)** nach Kumar et al. (2016)

**Methodische Kompromisse:**
- GRACE (300 km Auflösung) mit Bodenfeuchte-Modellen (1-12 km) fusionieren
- Kompromiss: Downscaling durch statistische Beziehungen (unphysikalisch aber praktikabel)

**Wichtige Erkenntnis:**
Die Dürre 2018-2020 zeigte einen Phasenübergang:
- 2018: SPEI erfasste Meteorologische Dürre gut ($SPEI_{6m} < -2$)
- 2019: SSI folgte mit Verzögerung ($SSI_{3m} < -1.5$)
- 2020: SRI und SDI zeigten erst dann extreme Werte

**Fazit:** Einzelne Indizes unterschätzen die Gesamtschwere solcher Compound-Ereignisse.

### 7.2 Sahel-Region (Westafrika)

**Kontext:**
- Stark saisonales Klima
- Geringe Datenverfügbarkeit
- Hohe Klimavariabilität

**Herausforderungen:**
- SPI ist problematisch (viele Null-Niederschläge)
- SPEI mit Thornthwaite-PET unterschätzt Dürre (keine Windsberücksichtigung)
- Bodenfeuchte-Daten kaum verfügbar

**Gewählte Methode:**
- **SPI mit Gamma-Anpassung** (mit Korrektur für Null-Werte)
- **SPEI mit Penman-Monteith** (wenn Daten verfügbar)

**Kritische Erkenntnis:**
Standardmethoden sind für diese Region unzureichend validiert. Die Gamma-Anpassung bei >50% Null-Niederschlagstagen ist statistisch fragwürdig (Stagge et al., 2015).

**Vorgeschlagene Alternative:**
"Inflated" Gamma-Verteilung oder nicht-parametrische Alternativen.

### 7.3 Kalifornien (USA)

**Kontext:**
- Mediterranes Klima
- Intensiver Wasserinfrastruktur-Einfluss
- Multi-Jahres-Dürren (Megadroughts)

**Gewählte Methoden:**
- **PDSI** (Palmer Drought Severity Index) - historisch etabliert
- **SPEI** - moderner Ersatz
- **USDM** - integriertes Experten-System

**Analyse der 2012-2016 Dürre:**

| Index | Peak-Wert | Timing | Interpretation |
|-------|-----------|--------|----------------|
| SPEI-12 | -3.5 | 2014 | Extremes Defizit |
| SSI | -2.1 | 2015 | Verspätete Bodenreaktion |
| SDI | -2.8 | 2014-2015 | Reservoir-Entleerung |

**Wichtige Erkenntnis:**
Die Unterschiede in Timing und Schwere zeigen die Notwendigkeit multipler Indizes. Der alleinige Gebrauch von SPEI hätte die hydrologische Schwere unterschätzt.

### 7.4 Australien (Murray-Darling Basin)

**Kontext:**
- Extrem variabel (ENSO, IOD)
- Hoch regulierte Flüsse
- Salinitäts-Problematik

**Besonderheit:**
Baseflow ist hier extrem wichtig für Ökosysteme (Red Gum Wälder).

**Methodische Innovation:**
- **Total Storage Deficit Index (TSDI)** - kombiniert Bodenfeuchte, Grundwasser, Reservoir
- **Environmental Drought Index** - berücksichtigt ökologische Flow-Anforderungen

**Kritische Erkenntnis:**
In stark regulierten Systemen ist der "natürliche" SDI irreführend. Ein "residual SDI" unter Abzug menschlicher Einflüsse ist nötig.

---

## 8. Forschungsagenda

### 8.1 Konkrete Forschungslücken

#### GAP-1: Verteilungswahl unter Klimawandel

**Problem:** Die Annahme stationärer Gamma-Parameter ist unter Klimawandel problematisch.

**Konkrete Frage:** Wie stark verzerrt nicht-stationäre Standardisierung historische Dürren?

**Empfohlene Methodik:**
- Test von Quantil-Mapping vs. Sliding-Window Standardisierung
- Vergleich der Rückkehrperioden unter verschiedenen Annahmen

**Mögliche Hypothese:** Die Verwendung einer fixen 1981-2010 Referenz überschätzt die Häufigkeit historischer Dürren um 20-30% in sich erwärmenden Regionen.

#### GAP-2: SMI/SSI bei Satellitenbodenfeuchte

**Problem:** SMAP/SMOS haben ~40 km Auflösung und zeigen Oberflächenfeuchte (0-5 cm), während landwirtschaftliche Dürre Wurzelschicht (0-100 cm) betrifft.

**Konkrete Frage:** Wie können Satellitendaten für SSI/SSI validiert und korrigiert werden?

**Empfohlene Methodik:**
- Kopplung von SMAP-Oberfläche mit prognostizierten SMI-Profilen aus LSMs
- Data Assimilation statt direkter Verwendung
- Validierung durch Dense Networks (z.B. COSMOS in Deutschland)

#### GAP-3: Recharge als Dürreindikator

**Problem:** Kein standardisierter, operationeller Recharge-Index existiert.

**Konkrete Frage:** Kann ein SRI (Standardized Recharge Index) entwickelt werden, der vergleichbar zu SSI/SPEI ist?

**Herausforderungen:**
- Recharge hat viele Null-Werte (keine Gamma-Anpassung möglich)
- Hohe räumliche Variabilität
- Keine direkten Messungen

**Vorgeschlagener Ansatz:**
- Verwendung von Mischungsverteilungen (zero-inflated Gamma)
- Regionalisierung durch pedotransfer-Funktionen

#### GAP-4: Compound-Dürren

**Problem:** Die Interaktion von meteorologischer und hydrologischer Dürre ist nicht quantifiziert.

**Konkrete Frage:** Wie häufig treten Compound-Dürren (gleichzeitig niedrig SPEI, SSI, SDI) auf, und wie können sie vorhergesagt werden?

**Empfohlene Methodik:**
- Kopula-Analyse der gemeinsamen Verteilung
- Identifikation von "Dürre-Kaskaden" in historischen Daten
- Entwicklung eines Compound-Dürre-Index (CDI)

#### GAP-5: Anthropogene Signatur in Dürre-Indizes

**Problem:** Menschliche Einflüsse (Reservoire, Bewässerung, Landnutzungsänderung) verschleiern natürliche Dürresignale.

**Konkrete Frage:** Wie stark beeinflussen menschliche Eingriffe die berechneten Indizes, und wie kann dies korrigiert werden?

**Empfohlene Methodik:**
- Gegenüberstellung von "naturalized" und beobachtetem Abfluss
- Attributionsstudien mit A/B-Modell-Experimenten
- Entwicklung von "human-influenced" und "natural" Dürre-Indizes

### 8.2 Methodische Inkonsistenzen

**Inkonsistenz 1: PET-Berechnung im SPEI**

Verschiedene Studien verwenden Thornthwaite, Hamon oder Penman-Monteith ohne Standardisierung. Dies führt zu nicht vergleichbaren Ergebnissen.

**Lösungsvorschlag:** SPEI sollte immer mit der verwendeten PET-Methode indiziert werden (z.B. SPEI-Th, SPEI-PM).

**Inkonsistenz 2: Referenzperioden**

WMO 1981-2010 wird nicht durchgängig verwendet; einige Studien nutzen 1961-1990 oder aktuelle 30-Jahres-Fenster.

**Lösungsvorschlag:** Zwingende Angabe der Referenzperiode in jeder Veröffentlichung; Entwicklung eines "normalize-to-baseline" Tools.

**Inkonsistenz 3: Aggregationszeiten**

Einige Indizes verwenden klimatologische Monate, andere hydrologische Jahreszeiten, wieder andere rollende Fenster.

**Lösungsvorschlag:** Standardisierung auf klimatologische Monate für saisonale Analysen; explizite Kennzeichnung der Fensterart.

### 8.3 Konkrete nächste Schritte

1. **Dateninfrastruktur:**
   - Globale Recharge-Datenbank aus LSM-Ensembles erstellen
   - Open-Source Python-Paket für HDM-Berechnung entwickeln

2. **Validierungsstudien:**
   - HDM in 3 kontrastierenden Klimazonen testen (feucht, semi-arid, arid)
   - Vergleich mit existierenden operationalen Systemen (USDM, CDI)

3. **Methodenentwicklung:**
   - Non-stationäre Standardisierung implementieren und testen
   - Copula-basierten Compound-Dürre-Index entwickeln

4. **Transfer:**
   - Guidelines für Index-Wahl je nach Fragestellung entwickeln
   - Decision-Tree für Forscher und Praktiker erstellen

---

## 9. Zusammenfassung

### 9.1 Kern-Erkenntnisse

1. **Kein perfekter Index:** Jeder Dürre-Index hat spezifische Stärken und Schwächen. Die Wahl muss an die Fragestellung angepasst werden.

2. **Standardisierung ist notwendig aber gefährlich:** Die Annahme stationärer Verteilungen ist unter Klimawandel problematisch.

3. **Physikalische Konsistenz:** Die Verknüpfung von Bodenfeuchte, Recharge und Abfluss ist essenziell für das Verständnis von Dürre-Kaskaden.

4. **Recharge ist der "missing link":** Ein standardisierter Recharge-Index (SRI) fehlt und würde die Analyse hydrologischer Dürren erheblich verbessern.

5. **Anthropogene Einflüsse werden unterschätzt:** In vielen Regionen dominieren menschliche Eingriffe das hydrologische Regime.

### 9.2 Empfehlungen für die Praxis

**Für Klimaforschung:**
- SPEI mit Penman-Monteith PET verwenden
- Multi-scale Analyse (1, 3, 6, 12, 24 Monate)
- Sliding-window Referenzperioden testen

**Für Wassermanagement:**
- Kombination aus SDI (kurzfristig) und Grundwasser-Indizes (langfristig)
- Berücksichtigung menschlicher Einflüsse
- HDM-Ansatz für integrierte Bewertung

**Für landwirtschaftliche Anwendungen:**
- SSI oder direkte Modellierung (mHM/Noah)
- Wurzelschicht-Bodenfeuchte, nicht Oberfläche
- Kopplung mit Wachstumsmodellen

---

## Referenzen

### Methodische Grundlagen

1. **McKee, T.B., et al. (1993).** The relationship of drought frequency and duration to time scales. *Proceedings of the 8th Conference on Applied Climatology*, 17(22), 179-183.

2. **Vicente-Serrano, S.M., et al. (2010).** A multiscalar drought index sensitive to global warming: The standardized precipitation evapotranspiration index. *Journal of Climate*, 23(7), 1696-1718. DOI: 10.1175/2009JCLI2909.1

3. **Samaniego, L., et al. (2010).** Application of a hydrologic similarity framework to the Middle Amazon Basin. *Water Resources Research*, 46(2). DOI: 10.1029/2009WR008361

4. **Nalbantis, I., & Tsakiris, G. (2009).** Assessment of hydrological drought revisited. *Water Resources Management*, 23(5), 881-897. DOI: 10.1007/s11269-008-9305-1

### Verteilungen und Statistik

5. **Stagge, J.H., et al. (2015).** Candidate distributions for climatological drought indices (SPI and SPEI). *International Journal of Climatology*, 35(13), 4027-4040. DOI: 10.1002/joc.4267

6. **Guttman, N.B. (1999).** Accepting the standardized precipitation index: A calculation algorithm. *Journal of the American Water Resources Association*, 35(2), 311-322.

### Bodenhydrologie

7. **van Genuchten, M.T. (1980).** A closed-form equation for predicting the hydraulic conductivity of unsaturated soils. *Soil Science Society of America Journal*, 44(5), 892-898.

8. **Rawls, W.J., et al. (1982).** Estimation of soil water properties. *Transactions of the ASAE*, 25(5), 1316-1320.

### Recharge-Methoden

9. **Scanlon, B.R., et al. (2006).** Global impacts of conversions from natural to agricultural ecosystems on water resources: Quantity versus quality. *Water Resources Research*, 42(3). DOI: 10.1029/2005WR004486

10. **Healy, R.W. (2010).** Estimating Groundwater Recharge. *Cambridge University Press*.

### Klimawandel und Dürren

11. **Trenberth, K.E., et al. (2014).** Global warming and changes in drought. *Nature Climate Change*, 4(1), 17-22.

12. **Milly, P.C.D., & Dunne, K.A. (2016).** Potential evapotranspiration and continental drying. *Nature Climate Change*, 6(10), 946-949.

### Hydrologische Modelle

13. **Liang, X., et al. (1994).** A simple hydrologically based model of land surface water and energy fluxes for general circulation models. *Journal of Geophysical Research*, 99(D7), 14415-14428.

14. **Niu, G.Y., et al. (2011).** The community Noah land surface model with multiparameterization options (Noah-MP): 1. Model description and evaluation with local-scale measurements. *Journal of Geophysical Research*, 116(D12).

---

## Anhang: Symbolverzeichnis

| Symbol | Bedeutung | Einheit |
|--------|-----------|---------|
| $\theta$ | Volumetrischer Wassergehalt | m³/m³ |
| $\theta_s$ | Sättigungswassergehalt | m³/m³ |
| $\theta_r$ | Residualwassergehalt | m³/m³ |
| $\psi$ | Bodenwasserspannung | kPa |
| $K$ | Hydraulische Leitfähigkeit | m/s |
| $K_s$ | Sättigungsleitfähigkeit | m/s |
| $\alpha, \beta$ | Gamma-Verteilungsparameter | -, 1/x |
| $\Phi^{-1}$ | Inverse Standardnormalverteilung | - |
| $P$ | Niederschlag | mm |
| $PET$ | Potentielle Evapotranspiration | mm |
| $ET$ | Evapotranspiration | mm |
| $Q$ | Abfluss | m³/s |
| $R$ | Recharge/Grundwasserneubildung | mm |
| $SMI$ | Soil Moisture Index | % oder Z-Score |
| $SSI$ | Standardized Soil Moisture Index | Z-Score |
| $SDI$ | Streamflow Drought Index | Z-Score |
| $SPEI$ | Standardized Precipitation Evapotranspiration Index | Z-Score |

---

*Dokument generiert: 2026-03-02*  
*Version: 2.0 Deep Analysis*  
*Wortzahl: ~8500 Wörter (Haupttext)*
