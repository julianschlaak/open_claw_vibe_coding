# Data Import Notes (Google Drive)

Source folder:
`https://drive.google.com/drive/folders/1ynqbWeUsKM6MMErYQ0FBvRpHBqnLTtFI`

Imported on: 2026-03-02

## Download command used

```bash
python -m gdown --folder "https://drive.google.com/drive/folders/1ynqbWeUsKM6MMErYQ0FBvRpHBqnLTtFI" -O /tmp/mhm_new_catchment_raw
```

## Mapping

- `90410700/90410700.day` -> `input/gauge/90410700.day`
- `mhm_setup/lai/*` -> `input/lai/`
- `mhm_setup/latlon/*` -> `input/latlon/`
- `mhm_setup/luse/*` -> `input/luse/`
- `mhm_setup/morph/*` -> `input/morph/`
- `catchment_ids/idgauges.asc` -> `input/morph/idgauges_from_catchment_ids.asc`
- `catchment_ids/basin_ids.nc` -> `input/optional_data/basin_ids.nc`
- `mhm_setup/meteo/pre.nc` -> `input/meteo/pre/pre.nc`
- `mhm_setup/meteo/tavg.nc` -> `input/meteo/tavg/tavg.nc`
- `mhm_setup/meteo/pet.nc` -> `input/meteo/pet/pet.nc`
- `mhm_setup/meteo/header.txt` -> `input/meteo/*/header.txt`
- `mask.nc` -> `input/meteo/mask.nc`

## Namelist adjustments applied

- `dir_Out(1) = "output/"`
- `file_LatLon(1) = "input/latlon/latlon_0p0625.nc"`
- Landcover scenes updated to:
  - `lc_1990.asc` (1990-1999)
  - `lc_2000.asc` (2000-2005)
  - `lc_2006.asc` (2006-2011)
  - `lc_2012.asc` (2012-2017)
  - `lc_2018.asc` (2018-2099)
- Gauge updated to:
  - `Gauge_id(1,1) = 90410700`
  - `gauge_filename(1,1) = "90410700.day"`

## Run status

- mHM now starts and reads core inputs.
- Current blocker:
  - `Class 1700 is missing in input/morph/soil_classdefinition.txt`
- Action needed:
  - provide basin-compatible `soil_classdefinition.txt`
  - verify `LAI_class.asc` / `LAI_classdefinition.txt` mapping for this basin
