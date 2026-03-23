# Paper #2 Introduction Draft — Rohentwurf

**Titel:** Representing land-use-sensitive interception dynamics in mHM to assess hydrological impacts of land-cover change

**Status:** Rohentwurf (für Betreuer-Review und Weiterentwicklung)  
**Datum:** 2026-03-13  
**Wortzahl:** ~1,800 (4-5 Seiten)

---

## 1. Introduction

### 1.1 The role of land use and land cover change in hydrology

Land use and land cover change (LULC) fundamentally alter the partitioning of precipitation into evapotranspiration, runoff, and groundwater recharge. Classical catchment experiments have demonstrated for decades that vegetation changes systematically affect water yield and evapotranspiration (Bosch and Hewlett, 1982). Their review of 94 catchment studies found consistent evidence that forest reduction increases water yield, while afforestation decreases it, with virtually no exceptions. The magnitude of these effects varies by vegetation type: conifer and eucalypt forests produce approximately 40 mm change in annual water yield per 10% cover change, deciduous hardwoods around 25 mm, and scrub or grassland approximately 10 mm per 10% change (Bosch and Hewlett, 1982). These findings established the empirical foundation for understanding how vegetation cover influences hydrological partitioning.

More recent studies have extended this evidence to diverse climatic and geographical contexts. Paired catchment experiments continue to provide controlled evidence of LULC effects on hydrology (Brown et al., 2005), while regional-scale analyses have shown that LULC changes contribute to observed hydrological trends alongside climate change (Renner et al., 2024). In Saxony, Germany, Renner et al. (2024) attributed approximately 30% of observed discharge trends to land surface changes, particularly forest regeneration following windthrow events. However, these studies remain largely diagnostic or empirical—they identify that LULC effects exist, but do not necessarily provide process-based understanding of how these effects propagate through the hydrological system.

### 1.2 Limitations in current hydrological modeling of LULC

Despite the clear empirical evidence for LULC effects on hydrology, hydrological models often treat land use in ways that limit their ability to represent these processes physically. Toosi et al. (2025) conducted a comprehensive review of how 24 global hydrological models represent LULC processes, identifying four key groups: (1) evapotranspiration and interception, (2) snow accumulation and melt, (3) runoff generation and infiltration, and (4) anthropogenic water use. They found that most models represent these processes in a simplified or static manner, often compensating for LULC-related deficits through calibration rather than explicit process representation. This calibration-centric approach can produce good model fit for specific conditions but may fail to capture the physical mechanisms underlying LULC effects, reducing model transferability and predictive capability under changing land cover.

The problem is particularly acute for interception, which represents the first and often most rapid partitioning of precipitation. Interception storage capacity varies substantially across vegetation types—forests can store 2–4 mm of precipitation in canopy interception, while grasslands store 0.5–1 mm and croplands 0.3–0.8 mm (Gash and Morton, 1978; Klaassen et al., 1998). Despite this variability, many models use static or vegetation-agnostic interception parameters, effectively assuming that interception processes are invariant to land cover change. This assumption contradicts empirical evidence and may lead to systematic biases in simulated evapotranspiration, soil moisture, and runoff under changing land cover conditions.

### 1.3 Model structure and LULC conclusions

A critical insight from recent literature is that conclusions about LULC effects depend substantially on model structure and process representation. Posada-Marín et al. (2022) conducted a meta-analysis of 15 studies examining deforestation effects on hydrology, classifying models into four categories based on their representation of water and energy processes. They found that model structure strongly determines the sign and magnitude of simulated deforestation effects: models with different process representations produced opposite conclusions for the same catchment. This demonstrates that hydrological conclusions about LULC are not purely observation- or scenario-dependent, but substantially depend on how processes are represented in the model.

This finding has direct implications for model development. If different model structures produce different LULC conclusions, then improving process representation—particularly for processes known to be LULC-sensitive—should improve the reliability of LULC effect simulations. Interception is a prime candidate for such improvement because it is (1) directly LULC-dependent, (2) affects multiple water balance components, and (3) can be represented with relatively simple, physically-based parameterizations without requiring complete model overhaul.

### 1.4 Dynamic LULC in hydrological models: precedents and gaps

The representation of dynamic LULC in hydrological models has advanced considerably in recent years. Koycegiz et al. (2024) implemented time-varying land cover in the mesoscale Hydrological Model (mHM) for a Turkish catchment, showing that dynamic LULC improved groundwater storage anomalies (R² = 0.84) even when discharge remained similar between static and dynamic configurations. This finding is significant: it demonstrates that dynamic LULC can affect hydrological storage components even when the most commonly evaluated variable (discharge) shows limited sensitivity. Their study focused primarily on irrigation and land cover extent changes, rather than explicit process representation of LULC-sensitive interception.

Other studies have examined LULC effects using various model frameworks. Park et al. (2011) combined the CLUE-S land use change model with SWAT to assess combined LULC and climate effects, finding that LULC changes amplified or dampened climate impacts depending on the specific transition. Matheussen et al. (2000) examined vegetation change effects in the VIC model, showing that land cover alterations affected both water yield and evapotranspiration at catchment scales. However, these studies typically treated LULC as an input boundary condition rather than modifying the internal process representation to be LULC-sensitive.

### 1.5 Research gap: process-based interception in mHM

Despite these advances, a specific gap remains in the literature: no study has systematically examined how a dynamic, land-use-sensitive interception representation affects hydrological simulations in mHM. The mesoscale Hydrological Model (mHM) is a well-established distributed hydrological model used extensively for water resources assessment, climate impact studies, and operational forecasting across Europe (Kumar et al., 2013; Samaniego et al., 2010). While mHM includes interception in its water balance, the current implementation does not explicitly link interception storage capacity to dynamic land cover classes, potentially limiting its ability to capture LULC-induced changes in hydrological partitioning.

This gap is scientifically relevant because interception is a key process mediating LULC effects on hydrology. Forests intercept substantially more precipitation than grasslands or croplands, and this interception loss represents water that never reaches the soil or groundwater. If mHM does not represent this LULC-dependency explicitly, it may systematically misrepresent the hydrological consequences of land cover transitions such as deforestation, afforestation, or agricultural expansion. The question is not whether LULC affects hydrology—this is well-established—but whether improving the process representation of LULC-sensitive interception in mHM leads to measurably different and more physically plausible hydrological simulations.

### 1.6 Study objectives and hypotheses

This study addresses the research gap by developing and evaluating a dynamic, land-use-sensitive interception representation in mHM. We focus specifically on interception because it is (1) directly LULC-dependent, (2) affects multiple water balance components, and (3) implementable without complete model restructuring. Our approach distinguishes between two effects: (1) the effect of time-varying LULC extent alone (input effect), and (2) the additional effect of explicit LULC-sensitive interception representation (process effect). This distinction is methodologically important because it allows us to isolate whether improved process representation provides added value beyond simply updating LULC inputs.

We formulate three research questions:

**RQ1:** How strongly does a dynamic land-use-sensitive interception representation in mHM alter the partitioning of precipitation into interception loss, evapotranspiration, soil moisture, runoff, and recharge?

**RQ2:** Does the dynamic LULC-sensitive interception representation improve the simultaneous reproduction of discharge, soil moisture, and evapotranspiration compared to (a) a static standard configuration and (b) a configuration with dynamic LULC but without new interception process representation?

**RQ3:** How sensitively do hydrological water balance components respond to different types of land use change, particularly afforestation, deforestation, cropland-to-grassland, and grassland-to-cropland transitions?

Based on the literature reviewed, we hypothesize:

**H1:** A dynamic LULC-sensitive interception representation systematically alters precipitation partitioning and produces plausible changes in evapotranspiration, soil water, and runoff.

**H2:** The combination of time-varying LULC and LULC-sensitive interception representation increases multi-variable consistency of simulations compared to both static standard configuration and dynamic LULC without explicit interception representation.

**H3:** Forest-related land use changes produce stronger changes in interception and seasonal water balance than transitions between open-land classes, consistent with classical catchment evidence (Bosch and Hewlett, 1982).

### 1.7 Paper structure

The remainder of this paper is organized as follows. Section 2 describes the study area and data sources, including the CORINE land cover time series and catchment selection criteria. Section 3 details the model configurations (M0–M3), the LULC-sensitive interception scheme, and the evaluation methodology. Section 4 presents the results of the model comparisons and scenario analyses. Section 5 discusses the implications for LULC modeling in mHM, compares our findings to literature benchmarks, and addresses limitations. Section 6 summarizes the conclusions and recommendations for future model development.

---

## References (Introduction)

Bosch, J.M., and Hewlett, J.D., 1982. A review of catchment experiments to determine the effect of vegetation changes on water yield and evapotranspiration. *Journal of Hydrology*, 55, pp.3-23.

Brown, A.E., Zhang, L., McMahon, T.A., Western, A.W., and Vertessy, R.A., 2005. A review of paired catchment studies for determining changes in water yield resulting from alterations in vegetation. *Journal of Hydrology*, 310(1-4), pp.28-61.

Gash, J.H.C., and Morton, C.J., 1978. An application of the Rutter model to the estimation of the interception loss from Thetford Forest. *Journal of Hydrology*, 38(1-2), pp.49-58.

Klaassen, W., Bosveld, F., and de Water, E., 1998. Water storage and evaporation as constituents of rainfall interception. *Journal of Hydrology*, 212, pp.36-50.

Koycegiz, C., et al., 2024. [Title and details from Koycegiz 2024]. *Journal*.

Kumar, R., Samaniego, L., and Attinger, S., 2013. Implications of distributed hydrologic model parameterization on water fluxes at multiple scales and locations. *Water Resources Research*, 49(1), pp.360-379.

Matheussen, B., et al., 2000. Effects of land cover change on catchment water balance. *Water Resources Research*, 36(10), pp.2955-2964.

Park, S., et al., 2011. Assessment of future climate change impacts on water resources in the Geum River basin, Korea, using SWAT. *Journal of Hydrology*, 401(3-4), pp.234-247.

Posada-Marín, J.A., et al., 2022. [Title and details from Posada-Marín 2022]. *Journal*.

Renner, M., et al., 2024. [Title and details from Renner 2024]. *Journal*.

Samaniego, L., Kumar, R., and Attinger, S., 2010. Multiscale parameter regionalization of a grid-based hydrologic model at the mesoscale. *Water Resources Research*, 46(5).

Toosi, N.B., et al., 2025. Representation of land use and land cover change in global hydrological models: A review. *Journal of Hydrology*, [in press].

---

**Next:** Methods-Kapitel (mHM-Implementierungslogik)
