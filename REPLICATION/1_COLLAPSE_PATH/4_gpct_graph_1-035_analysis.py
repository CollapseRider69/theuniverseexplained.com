import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

flow = pd.read_csv(
    'flow.csv',
    parse_dates=['external_timestamp'],
    infer_datetime_format=True
).rename(columns={'external_timestamp': 'timestamp'})
moon = pd.read_csv(
    'moon.csv',
    parse_dates=['timestamp'],
    infer_datetime_format=True
)

flow['timestamp'] = pd.to_datetime(flow['timestamp'], errors='coerce')
moon ['timestamp'] = pd.to_datetime(moon ['timestamp'], errors='coerce')
flow.dropna(subset=['timestamp','flow_meter'], inplace=True)
moon .dropna(subset=['timestamp'], inplace=True)

flow.sort_values('timestamp', inplace=True)
moon .sort_values('timestamp', inplace=True)

data = pd.merge_asof(
    flow, moon,
    on='timestamp',
    direction='nearest',
    tolerance=pd.Timedelta(seconds=2)
).dropna(subset=['flow_meter','moon_altitude_deg']).reset_index(drop=True)

bin_size = pd.Timedelta(hours=1.035)

start_time = data['timestamp'].min()
end_time   = data['timestamp'].max()
search_start = start_time - bin_size
search_end   = end_time   + bin_size

alt_series = (
    data.set_index('timestamp')['moon_altitude_deg']
        .resample('5min')
        .mean()
        .interpolate()
        .loc[search_start:search_end]
)

is_min = (alt_series.shift(1) > alt_series) & (alt_series.shift(-1) > alt_series)
lunar_midnights = alt_series[is_min].index

try:
    first_lm = next(t for t in lunar_midnights if t >= start_time)
except StopIteration:
    first_lm = lunar_midnights.min()

offset = first_lm - start_time
data['aligned_ts'] = data['timestamp'] + offset
data['bin_id']     = (
    (data['aligned_ts'] - data['aligned_ts'].min()) // bin_size
).astype(int)

agg = data.groupby('bin_id').agg(
    flow_avg = ('flow_meter',          'mean'),
    moon_avg = ('moon_altitude_deg',   'mean')
).reset_index()

agg['bin_center'] = (
    data['aligned_ts'].min()
    + (agg['bin_id'] + 0.5) * bin_size
    - offset
)

agg['flow_z'] = (agg['flow_avg'] - agg['flow_avg'].mean()) / agg['flow_avg'].std(ddof=0)
agg['moon_z'] = (agg['moon_avg'] - agg['moon_avg'].mean()) / agg['moon_avg'].std(ddof=0)

r, p = pearsonr(agg['flow_z'], agg['moon_z'])
z_stat = np.arctanh(r) * np.sqrt(len(agg) - 3)

plt.figure(figsize=(12, 5))
plt.plot(agg['bin_center'], agg['moon_z'], label='Z-Moon Altitude')
plt.plot(agg['bin_center'], agg['flow_z'], label='Z-Flow Meter')
plt.title(f'Anchored 1.035 h Averages: r={r:.4f}, p={p:.2e}, Z={z_stat:.4f}')
plt.xlabel('Timestamp')
plt.ylabel('Z-Score')
plt.axhline(0, linestyle='--', linewidth=1)
plt.legend()
plt.tight_layout()
plt.savefig('z_normalized_1.035h_anchored.png', dpi=300)
plt.show()
