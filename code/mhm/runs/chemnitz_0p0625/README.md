# Parthe Catchment Run Folder

Struktur:
- `input/` - Eingabedaten (hauptsächlich Symlinks auf `output/Parthe_0p0625/mhm_setup`)
- `output/` - Modell-Ausgaben für diesen Run
- `nml/` - Namelists (`mhm.nml`, `mhm_parameter.nml`, `mhm_outputs.nml`)
- `bin/mhm` - Symlink auf die aktive mHM-Executable

Start:
```bash
cd /docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/runs/parthe_0p0625
./bin/mhm ./nml
```

Hinweis:
- Aktuell ist `nGaugesTotal = 0`, weil kein `input/gauge/*.day` für Parthe im Repo gefunden wurde.
- Wenn du eine Gauge-Datei hast, lege sie unter `input/gauge/` ab und setze die Gauge-Einträge in `nml/mhm.nml`.
