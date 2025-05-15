
import pandas as pd
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Load merged dataset
merged_df = pd.read_csv("merged_data.csv", parse_dates=["timestamp"])

# Create a copy of the altitude info to re-merge after shifting timestamps
altitude_df = merged_df[["timestamp", "moon_altitude_deg"]].copy()

# Sweep from -12 to +12 hours in 1-hour steps
offsets = np.arange(-12, 13, 1)  # inclusive of +12

results = []

for offset in offsets:
    df = merged_df.copy()

    # Create shifted timestamp
    df["shifted_timestamp"] = df["timestamp"] + pd.Timedelta(hours=offset)

    # Merge in moon altitude based on the shifted timestamp
    df = pd.merge_asof(
        df.sort_values("shifted_timestamp"),
        altitude_df.rename(columns={"timestamp": "shifted_timestamp", "moon_altitude_deg": "shifted_altitude"}).sort_values("shifted_timestamp"),
        on="shifted_timestamp",
        direction="nearest"
    )

    df.dropna(subset=["shifted_altitude", "flow_meter"], inplace=True)

    # Segment and correlate
    rising = df[df["shifted_altitude"] > 0]
    falling = df[df["shifted_altitude"] <= 0]

    if not rising.empty and not falling.empty:
        r_rising, _ = pearsonr(rising["shifted_altitude"], rising["flow_meter"])
        r_falling, _ = pearsonr(falling["shifted_altitude"], falling["flow_meter"])

        z_rising = r_rising * np.sqrt(len(rising))
        z_falling = r_falling * np.sqrt(len(falling))
        z_flip = z_rising - z_falling

        results.append({
            "offset_hr": offset,
            "r_rising": r_rising,
            "r_falling": r_falling,
            "z_flip": z_flip
        })

# Save results
sweep_df = pd.DataFrame(results)
sweep_df.to_csv("phase_sweep_output.csv", index=False)

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(sweep_df["offset_hr"], sweep_df["r_rising"], label="Rising segment")
plt.plot(sweep_df["offset_hr"], sweep_df["r_falling"], label="Falling segment")
plt.plot(sweep_df["offset_hr"], sweep_df["z_flip"] / 1000, label="Z Flip (scaled)", linestyle="--")
plt.axhline(0, color='gray', linestyle=':')
plt.title("Phase Sweep: Collapse Correlation vs Gravitational Offset (24h, Timestamp-based)")
plt.xlabel("Offset from Reference Point (hours)")
plt.ylabel("Correlation (r) / Scaled Z-flip")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("phase_sweep_plot.png")
plt.close()
print("✅ 24-hour timestamp-based phase sweep complete.")
