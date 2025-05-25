
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def compute_stats(segment):
    flow = pd.to_numeric(segment['flow_meter'], errors='coerce')
    bias = pd.to_numeric(segment['phase_bias_index'], errors='coerce')
    mask = flow.notna() & bias.notna()
    flow = flow[mask]
    bias = bias[mask]
    if len(flow) < 2:
        return pd.Series({'r': None, 'p': None, 'z': None})
    r, p = pearsonr(flow, bias)
    z = np.arctanh(r) * np.sqrt(len(flow) - 3) if abs(r) < 1 else np.inf
    return pd.Series({'r': r, 'p': p, 'z': z})

def run_analysis(flow_csv, moon_csv, output_csv='z_bias_output.csv'):
    flow_df = pd.read_csv(flow_csv, encoding='latin1', on_bad_lines='skip')
    flow_df["flow_meter"] = pd.to_numeric(flow_df["flow_meter"], errors="coerce")
    moon_df = pd.read_csv(moon_csv, encoding='latin1', on_bad_lines='skip')

    flow_df['timestamp'] = pd.to_datetime(flow_df['external_timestamp'], errors='coerce')
    flow_df.dropna(subset=['timestamp'], inplace=True)
    moon_df['timestamp'] = pd.to_datetime(moon_df['timestamp'])

    moon_df = moon_df.sort_values('timestamp').reset_index(drop=True)
    moon_df['dG_dt'] = moon_df['moon_altitude_deg'].diff() / moon_df['timestamp'].diff().dt.total_seconds()
    moon_df['dG_dt'] = moon_df['dG_dt'].rolling(window=5, center=True).mean()


    # === PHASE-BIAS INDEX (PBI) CONSTRUCTION ===
    # Z-score the moon altitude
    moon_df['z_altitude'] = (moon_df['moon_altitude_deg'] - moon_df['moon_altitude_deg'].mean()) / moon_df['moon_altitude_deg'].std()
    # Z-score the rate-of-change (dG/dt)
    moon_df['z_dG_dt'] = (moon_df['dG_dt'] - moon_df['dG_dt'].mean()) / moon_df['dG_dt'].std()


    # === PHASE-BIAS INDEX (PBI) CONSTRUCTION ===
    # Z-score the moon altitude
    moon_df['phase_bias_index'] = moon_df['z_altitude'] * moon_df['z_dG_dt']

    start = moon_df['timestamp'].min()
    end = moon_df['timestamp'].max()
    flow_df = flow_df[(flow_df['timestamp'] >= start) & (flow_df['timestamp'] <= end)]

    flow_df.sort_values('timestamp', inplace=True)
    moon_df.sort_values('timestamp', inplace=True)

    merged_df = pd.merge_asof(
        flow_df,
        moon_df[['timestamp', 'phase_bias_index', 'gravity_phase']],
        on='timestamp', direction='nearest', tolerance=pd.Timedelta(milliseconds=500)
    )

    print("After merge:")
    print(merged_df[["timestamp", "flow_meter", "phase_bias_index", "gravity_phase"]].head())
    print(f"Merged rows before dropna: {len(merged_df)}")

    merged_df.dropna(subset=['flow_meter', 'phase_bias_index'], inplace=True)
    print(f"Merged rows after dropna: {len(merged_df)}")

    merged_df['moon_segment'] = np.where(
        merged_df['gravity_phase'] == 'ascending',
        'lunar_ascent',
        'lunar_decent'
    )

    grouped = merged_df.groupby("moon_segment").apply(compute_stats).reset_index()

    grouped.columns = ['moon_segment', 'r', 'p', 'z']

    total_stats = compute_stats(merged_df)
    total_row = pd.DataFrame([{'moon_segment': 'total', 'r': total_stats['r'], 'p': total_stats['p'], 'z': total_stats['z']}])

    if {'lunar_ascent', 'lunar_decent'}.issubset(set(grouped['moon_segment'])):
        z_ascent = grouped.loc[grouped['moon_segment'] == 'lunar_ascent', 'z'].values[0]
        z_decent = grouped.loc[grouped['moon_segment'] == 'lunar_decent', 'z'].values[0]
        z_flip = abs(z_ascent) + abs(z_decent)
        z_flip_row = pd.DataFrame([{'moon_segment': 'z_flip', 'r': None, 'p': None, 'z': z_flip}])
    else:
        z_flip_row = pd.DataFrame([{'moon_segment': 'z_flip', 'r': None, 'p': None, 'z': None}])

    final_df = pd.concat([grouped, total_row, z_flip_row], ignore_index=True)

    final_df.to_csv(output_csv, index=False)
    print(f"Analysis complete. Results saved to '{output_csv}'.")

if __name__ == "__main__":
    run_analysis("flow.csv", "moon.csv")
