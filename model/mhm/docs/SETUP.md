# mHM Setup Guide

## mHM - mesoscale Hydrological Model v5.13.2

**Installationsdatum:** 2026-03-02  
**Installationspfad:** `/data/.openclaw/workspace/miniforge/bin/mhm`

---

## Übersicht

mHM ist ein physikalisch basiertes, mesoskaliges Hydrologisches Modell zur Simulation von Wasserflüssen in Einzugsgebieten. Es wurde am Helmholtz-Zentrum für Umweltforschung (UFZ) entwickelt.

**Webseite:** https://mhm-ufz.org/  
**GitHub:** https://github.com/mhm-ufz/mHM

---

## Installation

### 1. Miniforge installieren

```bash
# Download Miniforge
curl -L -o /tmp/Miniforge3.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

# Installieren
bash /tmp/Miniforge3.sh -b -p /data/.openclaw/workspace/miniforge
```

### 2. Conda initialisieren

```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
```

### 3. mHM installieren

```bash
conda install -c conda-forge mhm -y
```

---

## Aktivierung

### Automatisch via Script

```bash
source model/mhm/setup/activate_mhm.sh
```

### Manuell

```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
mhm --version  # Zeigt Version 5.13.2
```

---

## Verzeichnisstruktur

```
model/mhm/
├── setup/
│   └── activate_mhm.sh      # Environment-Aktivierung
├── config/
│   ├── mhm.nml              # Hauptkonfiguration
│   ├── mhm_parameter.nml    # Parameter
│   └── mhm_outputs.nml      # Output-Einstellungen
├── tests/
│   └── test_domain/         # Test-Daten
└── docs/
    └── SETUP.md             # Diese Datei
```

---

## Test-Run

### Standard-Test

```bash
cd model/mhm
mhm ./test_domain
```

### Was passiert?

1. mHM liest die Konfiguration aus `test_domain/`
2. Führt die Simulation durch
3. Schreibt Ergebnisse nach `test_domain/output_b1/`

### Output-Dateien

- `output_b1/` - Simulationsergebnisse (NetCDF)
- `restart/` - Restart-Dateien
- `mHM.out` - Log-Output

---

## Konfiguration

### Hauptkonfiguration (mhm.nml)

Wichtige Parameter:
- `time_step` - Zeitschritt (Stunden)
- `sim_time` - Simulationszeitraum
- `dir_Input` - Input-Verzeichnis
- `dir_Out` - Output-Verzeichnis

### Parameter (mhm_parameter.nml)

- Horizontspezifische Parameter
- Routing-Parameter
- Evapotranspirations-Parameter

---

## Verwendung

### Basis-Befehl

```bash
mhm [options] [path_to_config]
```

### Optionen

- `-h, --help` - Hilfe anzeigen
- `-V, --version` - Version anzeigen
- `-q, --quiet` - Silent mode

### Beispiele

```bash
# Mit Standard-Konfiguration
mhm ./test_domain

# Mit spezifischer Konfiguration
mhm /pfad/zur/konfiguration
```

---

## Integration in Dürre-Indizes

mHM liefert folgende Outputs für Dürre-Analysen:

- **Bodenfeuchte** (Soil Moisture) → SMI, SSI
- **Grundwasserneubildung** (Recharge) → Recharge-Percentile
- **Abfluss** (Runoff) → SDI, Q5/Q10/Q90

Diese werden für den Matrix-Ansatz (SMI + Recharge + Abfluss) verwendet.

---

## Troubleshooting

### "mhm: command not found"

**Lösung:** PATH setzen
```bash
export PATH="/data/.openclaw/workspace/miniforge/bin:$PATH"
```

### "conda: command not found"

**Lösung:** Miniforge initialisieren
```bash
source /data/.openclaw/workspace/miniforge/etc/profile.d/conda.sh
```

### Fehlende Bibliotheken

**Lösung:** Conda-Environment prüfen
```bash
conda list | grep mhm
```

---

## Weiterführende Links

- **Dokumentation:** https://mhm.pages.ufz.de/mhm
- **GitHub:** https://github.com/mhm-ufz/mHM
- **CAMELS-DE:** https://doi.org/10.5194/essd-14-619-2022

---

**Setup durchgeführt von:** Helferchen  
**Datum:** 2026-03-02
