#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import datetime as dt
import netCDF4 as nc

ROOT = Path('/docker/openclaw-1lxa/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm')
SRC_OUTPUT = ROOT / 'output'
SRC_SETUP = ROOT / 'set_up'
DST_ROOT = ROOT / 'catchments_cloud'
TEMPLATE_NML = ROOT / 'catchment_custom' / 'mhm.nml'
TEMPLATE_PARAM = ROOT / 'catchment_custom' / 'mhm_parameter.nml'
TEMPLATE_OUTPUTS = ROOT / 'catchment_custom' / 'mhm_outputs.nml'
TEMPLATE_MRM_OUT = ROOT / 'catchment_custom' / 'mrm_outputs.nml'
CLASSDEF_SRC = ROOT / 'catchment_custom' / 'input' / 'morph'

CATCHMENTS = sorted([p.name for p in SRC_SETUP.iterdir() if p.is_dir() and (p / 'mhm_setup').exists()])


def parse_daily_discharge(daily_file: Path):
    with daily_file.open('r', encoding='utf-8') as f:
        header = f.readline().split()
        # No Day Mon Year Qobs_x Qsim_x
        if len(header) < 6:
            raise RuntimeError(f'Unexpected header in {daily_file}: {header}')
        qobs_col = header[4]
        gauge = qobs_col.split('Qobs_')[-1]
        rows = []
        for line in f:
            cols = line.split()
            if len(cols) < 6:
                continue
            day = int(cols[1]); mon = int(cols[2]); year = int(cols[3]); qobs = float(cols[4])
            rows.append((dt.date(year, mon, day), qobs))
    if not rows:
        raise RuntimeError(f'No rows in {daily_file}')
    return gauge, rows


def write_camels_day(out_file: Path, rows):
    start = rows[0][0]
    end = rows[-1][0]
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with out_file.open('w', encoding='utf-8') as f:
        f.write('CAMELS-DATA-Set\n')
        f.write('nodata   -9999.000\n')
        f.write('n       1 measurement per day [1, 1440]\n')
        f.write(f'start   {start.year:04d} {start.month:02d} {start.day:02d} 00 00 (YYYY MM DD HH MM)\n')
        f.write(f'end     {end.year:04d} {end.month:02d} {end.day:02d} 00 00 (YYYY MM DD HH MM)\n')
        for d, qobs in rows:
            f.write(f'{d.year:04d} {d.month:02d} {d.day:02d} 00 00   {qobs:10.3f}\n')


def meteo_period(pre_nc: Path):
    ds = nc.Dataset(pre_nc)
    t = ds.variables['time']
    dates = nc.num2date(t[:], t.units, getattr(t, 'calendar', 'standard'))
    ds.close()
    d0 = dates[0].date() if hasattr(dates[0], 'date') else dt.date(dates[0].year, dates[0].month, dates[0].day)
    d1 = dates[-1].date() if hasattr(dates[-1], 'date') else dt.date(dates[-1].year, dates[-1].month, dates[-1].day)
    return d0, d1


def patch_mhm_nml(text: str, gauge: str, y0: int, m0: int, d0: int, y1: int, m1: int, d1: int):
    replacements = [
        (r'dir_Out\(1\)\s*=\s*"[^"]*"', f'dir_Out(1)           = "output_{gauge}/"'),
        (r'dir_Total_Runoff\(1\)\s*=\s*[\'\"][^\'\"]*[\'\"]', f"dir_Total_Runoff(1) = 'output_{gauge}/'"),
        (r'dir_Precipitation\(1\)\s*=\s*"[^"]*"', 'dir_Precipitation(1) = "input/meteo/"'),
        (r'dir_Temperature\(1\)\s*=\s*"[^"]*"', 'dir_Temperature(1)   = "input/meteo/"'),
        (r'dir_ReferenceET\(1\)\s*=\s*"[^"]*"', 'dir_ReferenceET(1)     = "input/meteo/"'),
        (r'Gauge_id\(1,1\)\s*=\s*\d+', f'Gauge_id(1,1)       = {int(gauge)}'),
        (r'gauge_filename\(1,1\)\s*=\s*"[^"]*"', f'gauge_filename(1,1) = "{gauge}.day"'),
        (r'timeStep_LAI_input\s*=\s*\d+', 'timeStep_LAI_input = 1'),
        (r'warming_Days\(1\)\s*=\s*\d+', 'warming_Days(1)    = 720'),
        (r'eval_Per\(1\)%yStart\s*=\s*\d+', f'eval_Per(1)%yStart = {y0}'),
        (r'eval_Per\(1\)%mStart\s*=\s*\d+', f'eval_Per(1)%mStart = {m0:02d}'),
        (r'eval_Per\(1\)%dStart\s*=\s*\d+', f'eval_Per(1)%dStart = {d0:02d}'),
        (r'eval_Per\(1\)%yEnd\s*=\s*\d+', f'eval_Per(1)%yEnd   = {y1}'),
        (r'eval_Per\(1\)%mEnd\s*=\s*\d+', f'eval_Per(1)%mEnd   = {m1:02d}'),
        (r'eval_Per\(1\)%dEnd\s*=\s*\d+', f'eval_Per(1)%dEnd   = {d1:02d}'),
    ]
    out = text
    for pat, repl in replacements:
        out = re.sub(pat, repl, out)
    if '&directories_mpr' not in out.lower():
        block = (
            '\n!> LAI gridded time series folder definition (optional, MPR-related)\n'
            '&directories_MPR\n'
            'dir_gridded_LAI(1)   = "input/lai/"\n'
            '/\n'
        )
        out = out.replace('\n!> PROCESSES (mandatory)\n', block + '\n!> PROCESSES (mandatory)\n')
    return out


def copy_tree(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main():
    DST_ROOT.mkdir(parents=True, exist_ok=True)
    nml_template = TEMPLATE_NML.read_text(encoding='utf-8')
    for c in CATCHMENTS:
        setup = SRC_SETUP / c / 'mhm_setup'
        daily = SRC_OUTPUT / c / 'mhm_sim' / 'forward_run' / 'daily_discharge.out'
        pre_nc = setup / 'meteo' / 'pre.nc'
        if not daily.exists() or not pre_nc.exists():
            print(f'[SKIP] {c}: missing daily_discharge.out or pre.nc')
            continue

        gauge, rows = parse_daily_discharge(daily)
        start_meteo, end_meteo = meteo_period(pre_nc)
        start_obs, end_obs = rows[0][0], rows[-1][0]

        # safe overlap between forcing and observed discharge series
        start = max(start_meteo, start_obs)
        end = min(end_meteo, end_obs)

        dst = DST_ROOT / c
        inp = dst / 'input'
        out_dir = dst / f'output_{gauge}'
        (dst / 'restart').mkdir(parents=True, exist_ok=True)

        # copy mhm_setup -> input
        copy_tree(setup, inp)

        # enforce classdefinition files from catchment_custom/input/morph
        for fn in ['soil_classdefinition.txt', 'geology_classdefinition.txt', 'LAI_classdefinition.txt']:
            s = CLASSDEF_SRC / fn
            if s.exists():
                shutil.copy2(s, inp / 'morph' / fn)

        # create gauge file in CAMELS format
        rows_filtered = [(d, q) for d, q in rows if start <= d <= end]
        gauge_file = inp / 'gauge' / f'{gauge}.day'
        write_camels_day(gauge_file, rows_filtered)

        # nmls
        patched = patch_mhm_nml(nml_template, gauge, start.year, start.month, start.day, end.year, end.month, end.day)
        (dst / 'mhm.nml').write_text(patched, encoding='utf-8')
        shutil.copy2(TEMPLATE_PARAM, dst / 'mhm_parameter.nml')
        shutil.copy2(TEMPLATE_OUTPUTS, dst / 'mhm_outputs.nml')
        shutil.copy2(TEMPLATE_MRM_OUT, dst / 'mrm_outputs.nml')

        # output dir
        out_dir.mkdir(parents=True, exist_ok=True)

        # quick summary file
        (dst / 'RUN_INFO.txt').write_text(
            f'catchment={c}\n'
            f'gauge_id={gauge}\n'
            f'forcing_period={start_meteo}..{end_meteo}\n'
            f'obs_period={start_obs}..{end_obs}\n'
            f'run_period={start}..{end}\n'
            f'warming_days=720\n',
            encoding='utf-8'
        )

        print(f'[OK] {c}: gauge={gauge}, run={start}..{end}')

if __name__ == '__main__':
    main()
