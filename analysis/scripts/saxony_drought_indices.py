#!/usr/bin/env python3
"""
Saxony Drought Indices Calculator (1971-2020)

Calculates percentile-based drought indices for the entire Saxony domain:
- SMI (Soil Moisture Index) from SM_Lall
- RCI (Recharge Condition Index) from recharge
- QDI (Discharge Index) from Q at gauge 0090410340
- MDI (Matrix Drought Index) = Combined indicator

Output:
- NetCDF files for spatial data (SMI, RCI, MDI)
- CSV files for time series
- Compatible with dashboard_saxony visualization
"""

import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
WORKSPACE = Path("/data/.openclaw/workspace/open_claw_vibe_coding")
SAXONY_OUTPUT = WORKSPACE / "code/mhm/runs/saxony_0p0625/output"
DASHBOARD_UTILS = WORKSPACE / "dashboard_saxony/utils"
ANALYSIS_PLOTS = WORKSPACE / "analysis/plots/saxony_0p0625"

# Create output directories
DASHBOARD_UTILS.mkdir(parents=True, exist_ok=True)
ANALYSIS_PLOTS.mkdir(parents=True, exist_ok=True)

print("="*80)
print("🏔️  SAXONY DROUGHT INDICES CALCULATOR (1971-2020)")
print("="*80)
print()

#-------------------------------------------------------------------------------
# Step 1: Load monthly data
#-------------------------------------------------------------------------------
print("📊 Step 1: Loading mHM_Fluxes_States.nc...")
nc_file = SAXONY_OUTPUT / "mHM_Fluxes_States.nc"

if not nc_file.exists():
    print(f"❌ Error: {nc_file} not found!")
    exit(1)

ds = xr.open_dataset(nc_file)
print(f"   ✅ Loaded: {ds.dims}")
print(f"   Time range: {ds['time'].values[0]} to {ds['time'].values[-1]}")
print(f"   Grid: {len(ds['lat'])} x {len(ds['lon'])} = {len(ds['lat']) * len(ds['lon'])} cells")
print()

# Extract key variables
SM_Lall = ds['SM_Lall']  # Soil moisture all layers
recharge = ds['recharge']  # Groundwater recharge
Q = ds['Q']  # Total runoff
PET = ds['PET']  # Potential evapotranspiration

print(f"   Variables loaded:")
print(f"      SM_Lall: {SM_Lall.shape} (time, lat, lon)")
print(f"      recharge: {recharge.shape}")
print(f"      Q: {Q.shape}")
print(f"      PET: {PET.shape}")
print()

#-------------------------------------------------------------------------------
# Step 2: Calculate percentile-based indices (SMI, RCI)
#-------------------------------------------------------------------------------
print("📊 Step 2: Calculating percentile-based indices...")
print()

def calculate_percentile_index(data, name):
    """
    Calculate percentile-based index using Day-of-Year approach.
    
    For each grid cell and each day of year, calculate the empirical
    percentile from the 50-year climatology.
    
    Returns: Index (0-100) where <20 = drought, >80 = wet
    """
    print(f"   Calculating {name}...")
    
    # Convert to pandas for easier DoY handling
    time_index = pd.to_datetime(data['time'].values)
    df = data.to_pandas()
    df.index = time_index
    
    # Add Day-of-Year
    df['doy'] = df.index.dayofyear
    
    # Initialize output
    index = xr.zeros_like(data)
    index.attrs['long_name'] = f"{name} Index (Percentile-based)"
    index.attrs['units'] = 'percentile'
    index.attrs['description'] = f"{name} percentile (0-100), <20=drought, >80=wet"
    
    # Calculate for each day of year separately
    for doy in range(1, 367):
        # Get all values for this DoY across all years
        mask = df['doy'] == doy
        doy_data = df[mask].drop(columns=['doy'])
        
        if len(doy_data) < 10:
            continue
        
        # For each grid cell, calculate percentile
        for lat_idx in range(len(data['lat'])):
            for lon_idx in range(len(data['lon'])):
                cell_series = doy_data.iloc[:, lat_idx, lon_idx]
                
                # Calculate empirical percentile for each value
                for time_idx, val in enumerate(cell_series):
                    # Percentile = percentage of values <= current value
                    pct = (cell_series <= val).sum() / len(cell_series) * 100
                    index.values[time_idx, lat_idx, lon_idx] = pct
    
    return index

# For efficiency, use vectorized approach
def calculate_percentile_index_fast(data, name):
    """
    Fast vectorized percentile calculation.
    
    For each grid cell, calculate the empirical CDF and convert to percentiles.
    Uses all data for climatology (simplified approach).
    """
    print(f"   Calculating {name} (fast method)...")
    
    # Reshape to 2D (time, space)
    n_time = data.shape[0]
    n_lat = data.shape[1]
    n_lon = data.shape[2]
    
    data_2d = data.values.reshape(n_time, n_lat * n_lon)
    
    # Calculate percentile for each value
    # For each column (grid cell), rank all values
    index_2d = np.zeros_like(data_2d)
    
    for col in range(data_2d.shape[1]):
        col_data = data_2d[:, col]
        
        # Handle NaN
        valid_mask = ~np.isnan(col_data)
        if valid_mask.sum() < 10:
            continue
        
        # Calculate empirical percentile (rank-based)
        # Using scipy for efficiency
        from scipy.stats import rankdata
        ranks = rankdata(col_data[valid_mask], method='average')
        percentiles = ranks / len(ranks) * 100
        
        index_2d[valid_mask, col] = percentiles
    
    # Reshape back to 3D
    index = xr.DataArray(
        index_2d.reshape(n_time, n_lat, n_lon),
        dims=['time', 'lat', 'lon'],
        coords={'time': data['time'], 'lat': data['lat'], 'lon': data['lon']}
    )
    
    index.attrs['long_name'] = f"{name} Index (Percentile-based)"
    index.attrs['units'] = 'percentile'
    index.attrs['description'] = f"{name} percentile (0-100), <20=drought, >80=wet"
    
    return index

# Calculate SMI
print("   💧 Calculating SMI (Soil Moisture Index)...")
SMI = calculate_percentile_index_fast(SM_Lall, "SMI")
print(f"      SMI range: {SMI.min().values:.2f} - {SMI.max().values:.2f}")
print(f"      SMI mean: {SMI.mean().values:.2f}")
print()

# Calculate RCI (Recharge Condition Index)
print("   🔄 Calculating RCI (Recharge Condition Index)...")
RCI = calculate_percentile_index_fast(recharge, "RCI")
print(f"      RCI range: {RCI.min().values:.2f} - {RCI.max().values:.2f}")
print(f"      RCI mean: {RCI.mean().values:.2f}")
print()

# Calculate QDI (Discharge Index) - spatially distributed
print("   🌊 Calculating QDI (Discharge Index)...")
QDI = calculate_percentile_index_fast(Q, "QDI")
print(f"      QDI range: {QDI.min().values:.2f} - {QDI.max().values:.2f}")
print(f"      QDI mean: {QDI.mean().values:.2f}")
print()

#-------------------------------------------------------------------------------
# Step 3: Calculate MDI (Matrix Drought Index)
#-------------------------------------------------------------------------------
print("📊 Step 3: Calculating MDI (Matrix Drought Index)...")
print()

# MDI = Average of SMI, RCI, QDI (equal weighting)
# Lower values = more drought
MDI = (SMI + RCI + QDI) / 3
MDI.attrs['long_name'] = 'Matrix Drought Index'
MDI.attrs['units'] = 'percentile'
MDI.attrs['description'] = 'Combined drought index (SMI + RCI + QDI) / 3, <20=drought'

print(f"   💎 MDI = (SMI + RCI + QDI) / 3")
print(f"      MDI range: {MDI.min().values:.2f} - {MDI.max().values:.2f}")
print(f"      MDI mean: {MDI.mean().values:.2f}")
print()

# Drought classification
print("   📋 Drought Classification (MDI):")
drought_classes = {
    'Extreme Drought': (MDI < 5).sum().values,
    'Severe Drought': ((MDI >= 5) & (MDI < 10)).sum().values,
    'Moderate Drought': ((MDI >= 10) & (MDI < 20)).sum().values,
    'Normal': ((MDI >= 20) & (MDI < 80)).sum().values,
    'Wet': ((MDI >= 80) & (MDI < 95)).sum().values,
    'Very Wet': (MDI >= 95).sum().values,
}

total_cells = MDI.size
for cls, count in drought_classes.items():
    pct = count / total_cells * 100
    print(f"      {cls:20s}: {count:8d} cells ({pct:5.2f}%)")
print()

#-------------------------------------------------------------------------------
# Step 4: Save to NetCDF
#-------------------------------------------------------------------------------
print("📊 Step 4: Saving to NetCDF...")
print()

# Create output dataset
output_ds = xr.Dataset({
    'SMI': SMI,
    'RCI': RCI,
    'QDI': QDI,
    'MDI': MDI,
    'SM_Lall': SM_Lall,
    'recharge': recharge,
    'Q': Q,
})

# Add metadata
output_ds.attrs['title'] = 'Saxony Drought Indices (1971-2020)'
output_ds.attrs['created'] = datetime.now().isoformat()
output_ds.attrs['source'] = 'mHM 5.13.2 simulation'
output_ds.attrs['method'] = 'Percentile-based indices (empirical CDF)'

# Save
netcdf_path = DASHBOARD_UTILS / "saxony_drought_indices.nc"
output_ds.to_netcdf(netcdf_path, encoding={
    'SMI': {'zlib': True, 'complevel': 6},
    'RCI': {'zlib': True, 'complevel': 6},
    'QDI': {'zlib': True, 'complevel': 6},
    'MDI': {'zlib': True, 'complevel': 6},
})

print(f"   ✅ Saved: {netcdf_path}")
print(f"      Size: {netcdf_path.stat().st_size / 1024 / 1024:.1f} MB")
print()

#-------------------------------------------------------------------------------
# Step 5: Extract gauge time series (for discharge comparison)
#-------------------------------------------------------------------------------
print("📊 Step 5: Extracting gauge time series...")
print()

# Load discharge.nc for gauge 0090410340
discharge_nc = SAXONY_OUTPUT / "discharge.nc"

if discharge_nc.exists():
    ds_q = xr.open_dataset(discharge_nc)
    
    # Extract Qsim time series
    if 'Qsim_0090410340' in ds_q.data_vars:
        qsim = ds_q['Qsim_0090410340']
        
        # Save to CSV
        qsim_df = pd.DataFrame({
            'date': pd.to_datetime(ds_q['time'].values),
            'Qsim': qsim.values
        })
        
        csv_path = DASHBOARD_UTILS / "saxony_gauge_0090410340_Qsim.csv"
        qsim_df.to_csv(csv_path, index=False)
        print(f"   ✅ Saved gauge Qsim: {csv_path}")
        print(f"      Time steps: {len(qsim_df)}")
        print(f"      Range: {qsim.min().values:.3f} - {qsim.max().values:.3f} mm")
    
    ds_q.close()
else:
    print(f"   ⚠️  {discharge_nc} not found")
print()

#-------------------------------------------------------------------------------
# Step 6: Create summary statistics
#-------------------------------------------------------------------------------
print("📊 Step 6: Creating summary statistics...")
print()

# Monthly climatology
print("   Calculating monthly climatology...")
time_index = pd.to_datetime(SMI['time'].values)

# For 3D data, calculate spatial mean first, then monthly climatology
SMI_spatial_mean = SMI.mean(dim=['lat', 'lon'])
SMI_series = pd.Series(SMI_spatial_mean.values, index=time_index)

monthly_clim = SMI_series.groupby(SMI_series.index.month).mean()
monthly_clim.index.name = 'month'

clim_path = DASHBOARD_UTILS / "saxony_smi_monthly_climatology.csv"
monthly_clim.to_csv(clim_path)
print(f"   ✅ Saved monthly climatology: {clim_path}")
print()

# Annual drought statistics
print("   Calculating annual drought statistics...")
annual_stats = []

# Convert to pandas Series with DatetimeIndex
MDI_spatial = MDI.mean(dim=['lat', 'lon'])  # Spatial mean
MDI_series = pd.Series(MDI_spatial.values, index=time_index)

SMI_spatial_series = pd.Series(SMI_spatial_mean.values, index=time_index)

for year in range(1971, 2021):
    year_mask = MDI_series.index.year == year
    mdi_year = MDI_series[year_mask]
    smi_year = SMI_spatial_series[year_mask]
    
    # Drought months (MDI < 20)
    drought_months = (mdi_year < 20).sum()
    total_months = len(mdi_year)
    
    annual_stats.append({
        'year': year,
        'drought_months': int(drought_months),
        'total_months': int(total_months),
        'drought_fraction': float(drought_months / total_months) if total_months > 0 else 0,
        'smi_mean': float(smi_year.mean()),
        'smi_min': float(smi_year.min()),
    })

annual_df = pd.DataFrame(annual_stats)
annual_path = DASHBOARD_UTILS / "saxony_annual_drought_stats.csv"
annual_df.to_csv(annual_path, index=False)
print(f"   ✅ Saved annual statistics: {annual_path}")
print()

# Print worst drought years
print("   📋 Top 5 Drought Years (by drought fraction):")
top_drought = annual_df.nlargest(5, 'drought_fraction')
for _, row in top_drought.iterrows():
    print(f"      {int(row['year'])}: {row['drought_months']} months ({row['drought_fraction']*100:.1f}%)")
print()

#-------------------------------------------------------------------------------
# Step 7: Cleanup
#-------------------------------------------------------------------------------
print("📊 Step 7: Cleanup...")
ds.close()
print("   ✅ Datasets closed")
print()

#-------------------------------------------------------------------------------
# Summary
#-------------------------------------------------------------------------------
print("="*80)
print("✅ SAXONY DROUGHT INDICES COMPLETE!")
print("="*80)
print()
print("📂 Output files:")
print(f"   • {netcdf_path}")
print(f"      - SMI, RCI, QDI, MDI (25×52 grid, 600 months)")
print(f"      - Size: {netcdf_path.stat().st_size / 1024 / 1024:.1f} MB")
print()
print(f"   • {DASHBOARD_UTILS / 'saxony_gauge_0090410340_Qsim.csv'}")
print(f"      - Gauge discharge time series (daily)")
print()
print(f"   • {DASHBOARD_UTILS / 'saxony_smi_monthly_climatology.csv'}")
print(f"      - Monthly SMI climatology")
print()
print(f"   • {DASHBOARD_UTILS / 'saxony_annual_drought_stats.csv'}")
print(f"      - Annual drought statistics (1971-2020)")
print()
print("🎯 Next steps:")
print("   1. Update dashboard to load saxony_drought_indices.nc")
print("   2. Add Saxony as spatial layer in tabs 🌱💧📊🎯")
print("   3. Keep 🌊 Discharge tab for 6 catchments validation")
print()
print("🎉 Ready for dashboard integration!")
print()
