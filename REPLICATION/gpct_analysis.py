
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def compute_stats(segment):
    # Convert to numeric in case any strings snuck in
    flow = pd.to_numeric(segment['flow_meter'], errors='coerce')
    tide = pd.to_numeric(segment['dTide_dt'], errors='coerce')

    # Drop rows with bad data
    mask = flow.notna() & tide.notna()
    flow = flow[mask]
    tide = tide[mask]

    if len(flow) < 2:
        return pd.Series({'r': None, 'p': None, 'z': None})

    r, p = pearsonr(flow, tide)
    z = np.arctanh(r) * np.sqrt(len(flow) - 3) if abs(r) < 1 else np.inf
    return pd.Series({'r': r, 'p': p, 'z': z})

def run_analysis(flow_csv, moon_csv, tide_csv, output_csv='z_flip_output.csv'):
    # Load data
    flow_df = pd.read_csv(flow_csv, encoding='latin1', on_bad_lines='skip')
    flow_df["flow_meter"] = pd.to_numeric(flow_df["flow_meter"], errors="coerce")
    moon_df = pd.read_csv(moon_csv, encoding='latin1', on_bad_lines='skip')
    tide_df = pd.read_csv(tide_csv, encoding='latin1', on_bad_lines='skip')

    # Parse timestamps
    flow_df['timestamp'] = pd.to_datetime(flow_df['external_timestamp'], errors='coerce')
    flow_df.dropna(subset=['timestamp'], inplace=True)
    moon_df['timestamp'] = pd.to_datetime(moon_df['timestamp'])

    # Restrict flow_df to time range fully covered by tide and moon data
    if 'datetime' in tide_df.columns:
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
    elif 'timestamp' in tide_df.columns:
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
    else:
        raise KeyError("Expected 'datetime' or 'timestamp' column in tide_df")
    start = max(moon_df['timestamp'].min(), tide_df['timestamp'].min())
    end = min(moon_df['timestamp'].max(), tide_df['timestamp'].max())
    flow_df = flow_df[(flow_df['timestamp'] >= start) & (flow_df['timestamp'] <= end)]

    # Allow flexibility between 'datetime' or 'timestamp' columns in tide_df
    if 'datetime' in tide_df.columns:
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
    elif 'timestamp' in tide_df.columns:
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
    else:
        raise KeyError("Expected 'datetime' or 'timestamp' column in tide_df")
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['datetime'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
        tide_df['timestamp'] = pd.to_datetime(tide_df['timestamp'])
    tide_df.rename(columns={'dTide/dt': 'dTide_dt'}, inplace=True)

    # Sort all
    flow_df.sort_values('timestamp', inplace=True)
    moon_df.sort_values('timestamp', inplace=True)
    tide_df.sort_values('timestamp', inplace=True)

    # Merge with 30s tolerance
    merged_df = pd.merge_asof(flow_df, tide_df[['timestamp', 'dTide_dt']],
                               on='timestamp', direction='nearest', tolerance=pd.Timedelta(seconds=30))
    merged_df = pd.merge_asof(merged_df, moon_df[['timestamp', 'moon_altitude_deg','gravity_phase']],
                               on='timestamp', direction='nearest', tolerance=pd.Timedelta(seconds=30))

    # Drop NaNs
    merged_df.dropna(subset=['flow_meter', 'dTide_dt', 'moon_altitude_deg'], inplace=True)

    # Segment by gravitational ascent/descent phase
    merged_df['moon_segment'] = np.where(
    merged_df['gravity_phase'] == 'ascending',
    'lunar_ascent',
    'lunar_decent')

    # --- Diagnostics ---
    print(f"Loaded flow data: {len(flow_df):,} rows")
    print(f"Loaded tide data: {len(tide_df):,} rows")
    print(f"Loaded moon data: {len(moon_df):,} rows")
    print(f"Merged dataset after all joins and NaN drops: {len(merged_df):,} rows")
    print("Rows per moon segment:")
    print(merged_df['moon_segment'].value_counts(dropna=False))
    print("----------------------")
    
# Save merged data for phase sweep
    merged_df.to_csv("merged_data.csv", index=False)

# Compute stats
    grouped = merged_df.groupby('moon_segment').apply(compute_stats)
    total_stats = compute_stats(merged_df)
    z_flip = grouped['z'].iloc[0] - grouped['z'].iloc[1] if len(grouped) > 1 else np.nan

    # Collect results
    results = grouped.copy()
    results.loc['Total'] = total_stats
    results.loc['Z Flip (Total)'] = [np.nan, np.nan, z_flip]

    # Output CSV
    results.to_csv(output_csv)
    print(f"Analysis complete. Results saved to '{output_csv}'.")

# Example usage:
# run_analysis('flow.csv', 'moon.csv', 'tide.csv')


# Run analysis when script is executed
if __name__ == '__main__':
    run_analysis(
        'flow.csv',
        'moon.csv',
        'tide.csv'
    )