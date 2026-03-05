# Dashboard Sachsen – Quellen-Handover für OpenClaw

Datum: 2026-03-05
Scope: Wissenschafts-Tab (`dashboard_saxony/app.py`) und Bibliographie (`dashboard_saxony/data/references.bib`)

## Ziel
Bitte die unten gelisteten Quellen in das OpenClaw-Research-Gedächtnis übernehmen und als "verified references" markieren.

## Bereits im Dashboard/Bib eingebaut
1. Van Loon, A. F., & Van Lanen, H. A. J. (2012). A process-based typology of hydrological drought. Hydrology and Earth System Sciences, 16, 1915-1946. DOI: 10.5194/hess-16-1915-2012
2. Samaniego, L., Kumar, R., & Zink, M. (2013). Implications of parameter uncertainty on soil moisture drought analysis in Germany. Journal of Hydrometeorology, 14(1), 47-68. DOI: 10.1175/JHM-D-12-075.1
3. Hao, Z., & AghaKouchak, A. (2013). Multivariate Standardized Drought Index: A parametric multi-index model. Advances in Water Resources, 57, 12-18. DOI: 10.1016/j.advwatres.2013.03.009
4. Hao, Z., Singh, V. P., & Xia, Y. (2017). Integration of multivariate drought indices using Bayesian methods. Journal of Hydrology, 552, 638-647. DOI: 10.1016/j.jhydrol.2017.07.026
5. Van Loon, A. F. (2015). Hydrological drought explained. WIREs Water, 2(4), 359-392. DOI: 10.1002/wat2.1085
6. Vicente-Serrano, S. M., Begueria, S., & Lopez-Moreno, J. I. (2010). A Multiscalar Drought Index Sensitive to Global Warming: The SPEI. Journal of Climate, 23(7), 1696-1718. DOI: 10.1175/2009JCLI2909.1
7. Lloyd-Hughes, B., & Saunders, M. A. (2002). A drought climatology for Europe. International Journal of Climatology, 22(13), 1571-1592. DOI: 10.1002/joc.846
8. Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements. FAO Irrigation and Drainage Paper 56.
9. Saxton, K. E., & Rawls, W. J. (2006). Soil water characteristic estimates by texture and organic matter for hydrologic solutions. SSSAJ, 70(5), 1569-1578. DOI: 10.2136/sssaj2005.0117
10. BGR (2005). Bodenkundliche Kartieranleitung (KA5), 5. Auflage. ISBN: 978-3-510-95920-4
11. Loritz, R., Gnann, S. J., Schulz, K., et al. (2024). CAMELS-DE: hydro-meteorological time series and landscape attributes for 1584 German catchments. ESSD, 16, 5625-5655. DOI: 10.5194/essd-16-5625-2024
12. CAMELS-DE data package (2024). Zenodo. DOI: 10.5281/zenodo.13837553
13. WMO (2012). Standardized Precipitation Index User Guide. WMO-No. 1090.
14. Stahl, K., & Kohn, I. (2022). European Drought Impacts Database (EDID/EDII). DOI: 10.6094/UNIFR/230922

## Quellen mit Zugriffshinweis
- Einige historische DOI-Ziele (z. B. sehr alte Journals) liefern je nach Umgebung 403/404 beim Direktaufruf.
- Für Nutzerführung im Dashboard wurden deshalb stabile Landing-Pages (FAO/BGR/UFZ/WMO) zusätzlich verlinkt.

## To-do für OpenClaw
1. Diese Referenzen in `memory/research/` als kanonische Quellenliste ablegen.
2. `memory/research/drought_indices_methodology.md` um DOI/ISBN/Standards ergänzen.
3. Pro Index (nFK, SMI, MDI, SPI/SPEI) jeweils 2-3 Primärquellen + 1 Standardquelle markieren.
4. Optional: Verfügbarkeitscheck je Link (HTTP status + Datum) protokollieren.

