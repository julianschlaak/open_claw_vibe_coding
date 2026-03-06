# Data Availability Statement

**Paper:** "A Percentile-Based Multi-Component Drought Index for Hydrological Drought Monitoring in Central Europe"  
**Date:** 2026-03-06  
**Format:** HESS style

---

## DATA AVAILABILITY

The data and code used in this study are available as follows:

### Model Code

The mesoscale Hydrological Model (mHM) version 5.13.2 is available under the GNU General Public License v3.0 from the official repository: https://www.mhm-model.org/index.php/download/ (last access: March 2026). Model configuration files for this study are available in the supplementary material.

### Analysis Code

All Python scripts for data processing, drought index calculation, and figure generation are publicly available on GitHub: https://github.com/julianschlaak/open_claw_vibe_coding (DOI: pending Zenodo deposition). The code is released under the MIT License to encourage reuse and reproducibility.

### Simulation Outputs

Daily mHM simulation outputs (soil moisture, recharge, streamflow) for the five study catchments are available on Zenodo: https://doi.org/10.5281/zenodo.XXXXXX (placeholder, to be updated upon deposition). The dataset includes:
- Daily soil moisture (0–25 cm, 25–100 cm, 100–180 cm, total) in mm
- Daily groundwater recharge in mm day⁻¹
- Daily simulated streamflow in m³ s⁻¹
- Daily precipitation and potential evapotranspiration forcing data
- Calculated drought indices (SMI, R-Pctl, Q-Pctl, MDI)

Total dataset size: ~2.5 GB (uncompressed CSV format).

### Observational Data

**CAMELS-DE Streamflow:** Observed streamflow data for German catchments are available from the CAMELS-DE repository:
- Loritz, R., Gnann, S. J., Schulz, K., and Fischer, B. M. C.: CAMELS-DE: hydro-meteorological time series and landscape attributes for 1584 German catchments, Earth System Science Data, 16, 5625–5655, https://doi.org/10.5194/essd-16-5625-2024, 2024.
- Data package: https://doi.org/10.5281/zenodo.13837553

**European Drought Impact Database (EDID):** Drought impact records for Europe are available from:
- Stahl, K. and Kohn, I.: European Drought Impacts Database (EDID/EDII), University of Freiburg, https://doi.org/10.6094/UNIFR/230922, 2022.
- Web interface: https://www.edii.org/

**DWD Precipitation and Temperature:** Gridded precipitation (Regnie) and temperature data from the German Weather Service (DWD) are available upon request due to licensing restrictions. Researchers can apply for access via the DWD Climate Data Center: https://www.dwd.de/EN/climate_environment/cdc/cdc.html. Alternatively, similar data are available from the E-OBS dataset: https://www.ecad.eu/download/ensembles/download.php.

### Dashboard

The interactive Drought Monitor Dashboard for Saxony is publicly accessible at: http://187.124.13.209:8502/ (password protected upon request). The dashboard source code is included in the GitHub repository listed above.

---

## AUTHOR CONTRIBUTIONS

**Julian Schlaak:** Conceptualization, methodology, software, formal analysis, investigation, data curation, writing (original draft), visualization.

**[Co-Author 1]:** Validation, writing (review and editing), supervision.

**[Co-Author 2]:** Resources, writing (review and editing), project administration.

**[Co-Author 3]:** Funding acquisition, writing (review and editing).

*Note: Author contributions follow the CRediT taxonomy (Contributor Roles Taxonomy).*

---

## COMPETING INTERESTS

The authors declare that they have no conflict of interest.

---

## ACKNOWLEDGEMENTS

The authors thank the German Weather Service (DWD) for providing precipitation and temperature data, and the Helmholtz Centre for Environmental Research (UFZ) for maintaining the European Drought Impact Database. We acknowledge the CAMELS-DE team for making streamflow observations freely available. Computational resources were provided by [institution/cluster name]. This work was funded by [grant number/agency, if applicable].

Special thanks to [names of colleagues who provided feedback on early drafts] for their constructive comments.

---

## FUNDING

This research was supported by:
- [Grant Agency Name], grant number [XXXXX]
- [University/Institution] PhD Fellowship
- [Additional funding sources, if any]

*Note: Add specific funding information as applicable.*

---

## SUPPLEMENT MATERIAL

The following supplementary materials are available online at [journal URL]:

**S1:** Additional figure captions for all catchments (PDF, 150 KB)  
**S2:** Table of drought event statistics for all catchments (CSV, 50 KB)  
**S3:** Sensitivity analysis of MDI weight combinations (PDF, 200 KB)  
**S4:** mHM model configuration files (ZIP, 10 KB)  
**S5:** Sample code for MDI calculation (Python Jupyter Notebook, 100 KB)

---

**Status:** ✅ Data Availability Statement complete!  
**Format:** HESS compliant  
**DOIs:** Placeholder for Zenodo deposition (to be updated before submission)

---

**Next Steps:**
1. Deposit simulation outputs on Zenodo → Get DOI
2. Finalize GitHub repository → Get permanent link
3. Update placeholder DOIs in this file
4. Add co-author names and affiliations
5. Add funding information
