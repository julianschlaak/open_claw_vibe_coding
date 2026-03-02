#!/usr/bin/env python3
import numpy as np
import netCDF4 as nc
import pandas as pd
import matplotlib.pyplot as plt
import os

# Config
output_dir = "/data/.openclaw/workspace/open_claw_vibe_coding/code/mhm/test_domain/output_b1"
results_dir = "/data/.openclaw/workspace/open_claw_vibe_coding/analysis/results"
plot_dir = "/data/.openclaw/workspace/open_claw_vibe_coding/analysis/plots"

os.makedirs(results_dir, exist_ok=True)
os.makedirs(plot_dir, exist_ok=True)

print("Loading mHM data...")
ds = nc.Dataset(os.path.join(output_dir, "mHM_Fluxes_States.nc"))
soil_moisture = ds.variables["L1_soilMoist"][:]
time = nc.num2date(ds.variables["time"][:], ds.variables["time"].units)

print(f"Loaded {len(time)} time steps")
print(f"Soil moisture shape: {soil_moisture.shape}")

# Calculate mean soil moisture
sm_mean = np.nanmean(soil_moisture, axis=(1, 2))

# Save results
df = pd.DataFrame({"time": range(len(time)), "soil_moisture_mean": sm_mean})
df.to_csv(os.path.join(results_dir, "soil_moisture.csv"), index=False)

# Plot
plt.figure(figsize=(12, 6))
plt.plot(sm_mean)
plt.title("Soil Moisture Mean")
plt.xlabel("Time")
plt.ylabel("Soil Moisture [mm]")
plt.savefig(os.path.join(plot_dir, "soil_moisture.png"), dpi=150)
plt.close()

print(f"Results saved to {results_dir}")
print(f"Plot saved to {plot_dir}")
