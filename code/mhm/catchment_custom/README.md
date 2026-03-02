# catchment_custom

Template and working example for adding a new basin/catchment dataset to mHM.

## Required structure

- `mhm.nml`
- `mhm_parameter.nml`
- `mhm_outputs.nml`
- `mrm_outputs.nml`
- `input/` with required subfolders/files for your basin
- `output/` (runtime outputs)
- `restart/` (restart states)

## How to provide new data

1. Google Drive:
   - Share folder with "Anyone with the link".
   - Download in container/host with `gdown --folder "<drive_link>" -O /tmp/<catchment_raw>`.
2. Local files:
   - Upload to server (scp/sftp) to `/tmp/<catchment_raw>`.
3. Existing server path:
   - Copy directly with `cp -r <source> <target>`.

## Mapping used in this setup

- `<raw>/mhm_setup/morph/*` -> `input/morph/`
- `<raw>/mhm_setup/luse/*` -> `input/luse/`
- `<raw>/mhm_setup/lai/*` -> `input/lai/`
- `<raw>/mhm_setup/latlon/*` -> `input/latlon/`
- `<raw>/mhm_setup/meteo/pre.nc` -> `input/meteo/pre/pre.nc`
- `<raw>/mhm_setup/meteo/tavg.nc` -> `input/meteo/tavg/tavg.nc`
- `<raw>/mhm_setup/meteo/pet.nc` -> `input/meteo/pet/pet.nc`
- `<raw>/<gauge_id>/<gauge_id>.day` -> `input/gauge/<gauge_id>.day`

## Current status (2026-03-02)

- `mhm.nml` was adapted to:
  - `latlon_0p0625.nc`
  - gauge `90410700.day`
  - 5 land-cover scenes (1990, 2000, 2006, 2012, 2018)
- Smoke run starts and reads all major inputs, but currently stops at:
  - `Class 1700 is missing in input/morph/soil_classdefinition.txt`

This means the catchment import is structurally correct, but needs the correct
soil lookup table for this basin before full simulation.
