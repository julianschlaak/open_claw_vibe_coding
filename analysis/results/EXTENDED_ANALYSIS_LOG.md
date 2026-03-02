# EXTENDED_ANALYSIS_LOG

## Schritte
1. mHM monatliche Variablen geladen (SM_L01, SM_L02, SM_Lall, recharge, Q).
2. Discharge-Tagesdaten geladen und Q5/Q95 berechnet.
3. Fünf fachliche Plots erzeugt.
4. Dürre-Events über SMI<20 (daily proxy) identifiziert.
5. Statistiken nach JSON geschrieben.

## Wichtige Kennzahlen
- Q5: 37.151
- Q95: 380.821
- Dürre-Events: 5
- Mittlere Dürre-Dauer (Tage): 54.60

## Tool-Stabilisierung (OpenClaw)
- Instabile Tools analysiert: `write`, `exec`, `sessions_spawn`.
- In der Host-Bridge `/usr/local/bin/openclaw-mcp-bridge` implementiert:
  - Retry-Logik: 3 Versuche
  - Exponential Backoff: 0.5s, 1.0s, 2.0s
  - Fehlerbehandlung + Logging nach `/tmp/openclaw_mcp_bridge.log`
- 10 Wiederholungen pro Tool durchgeführt (via `analysis/scripts/tool_stability_harness.py`).
- Ergebnis siehe `analysis/results/tool_stability_report.json`.
