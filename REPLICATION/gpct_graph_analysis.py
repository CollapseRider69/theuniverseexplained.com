import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

# Load data with correct timestamp columns
flow_data = pd.read_csv('flow.csv', parse_dates=['external_timestamp'])
moon_data = pd.read_csv('moon.csv', parse_dates=['timestamp'])
tide_data = pd.read_csv('tide.csv', parse_dates=['timestamp'])

# Prepare data
flow_data.sort_values('external_timestamp', inplace=True)
moon_data.sort_values('timestamp', inplace=True)
tide_data.sort_values('timestamp', inplace=True)

# Rename timestamp columns for merging
flow_data.rename(columns={'external_timestamp': 'timestamp'}, inplace=True)
moon_data.rename(columns={'timestamp': 'timestamp'}, inplace=True)
tide_data.rename(columns={'timestamp': 'timestamp'}, inplace=True)

# Explicit datetime conversion and drop NaNs
flow_data['timestamp'] = pd.to_datetime(flow_data['timestamp'], errors='coerce')
moon_data['timestamp'] = pd.to_datetime(moon_data['timestamp'], errors='coerce')
tide_data['timestamp'] = pd.to_datetime(tide_data['timestamp'], errors='coerce')

flow_data.dropna(subset=['timestamp'], inplace=True)
moon_data.dropna(subset=['timestamp'], inplace=True)
tide_data.dropna(subset=['timestamp'], inplace=True)

# Merge datasets
data = pd.merge_asof(flow_data, moon_data, on='timestamp', direction='nearest', tolerance=pd.Timedelta(seconds=2))
data = pd.merge_asof(data, tide_data, on='timestamp', direction='nearest', tolerance=pd.Timedelta(seconds=2))
data.dropna(inplace=True)

# Resample to daily averages
flow_daily = data.set_index('timestamp')['flow_meter'].resample('D').mean()
moon_daily = data.set_index('timestamp')['moon_altitude_deg'].resample('D').mean()

# Z-Normalization
flow_z = (flow_daily - flow_daily.mean()) / flow_daily.std()
moon_z = (moon_daily - moon_daily.mean()) / moon_daily.std()

# Compute correlation using pearsonr
r, p = pearsonr(flow_z, moon_z)
z = np.arctanh(r) * np.sqrt(len(flow_z) - 3)

# Plot
plt.figure(figsize=(12, 5))
plt.plot(flow_z.index, moon_z, color='black', label='Z-Moon Altitude')
plt.plot(flow_z.index, flow_z, color='orange', label='Z-Flow Meter')
plt.title(f'Z-Normalized Daily Averages\nMoon Altitude vs Flow Meter\nr = {r:.4f}, p = {p:.2e}, Z = {z:.4f}')
plt.xlabel('Date')
plt.ylabel('Z-Score')
plt.axhline(0, color='grey', linestyle='--', linewidth=1)
plt.legend()
plt.tight_layout()

# Save figure
plt.savefig('z_normalized_daily_averages.png', dpi=300)
plt.show()
