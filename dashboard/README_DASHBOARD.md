# Dashboard Anleitung

## Installation

```bash
cd /data/.openclaw/workspace/open_claw_vibe_coding/dashboard
pip install -r requirements.txt
```

## Starten

```bash
streamlit run app.py
```

## Zugriff

- Lokal: http://localhost:8501

## Features

- Catchment-Filter (`test_domain`, `catchment_custom`)
- Zeitraum-Slider
- Monatsfilter (Alle / Jan-Dez)
- Dürreklassen-Filter
- Tab 1: SMI-Heatmap (Jahre x Monate)
- Tab 2: Interaktive Zeitreihen (SMI, Recharge, Runoff, optional SSI/SDI)
- Tab 3: Abfluss-Validierung (Qsim vs Qobs + KGE, RMSE, MAE, r)
- Automatisches Reload bei Datenänderungen (cache ttl)

## Datenquellen

- `analysis/results/test_domain/monthly_drought_indices.csv`
- `analysis/results/catchment_custom/monthly_drought_indices.csv`
- `analysis/results/test_domain/daily_discharge.csv`
- `analysis/results/catchment_custom/daily_discharge.csv`

## Screenshot

- Platzhalter: `dashboard/screenshots/dashboard_overview.png`
