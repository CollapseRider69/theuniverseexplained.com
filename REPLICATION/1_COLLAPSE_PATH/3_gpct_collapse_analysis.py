
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

def compute_stats(segment):
    flow = pd.to_numeric(segment['flow_meter'], errors='coerce')
    moon = pd.to_numeric(segment['moon_altitude_deg'], errors='coerce')
    mask = flow.notna() & moon.notna()
    flow = flow[mask]
    moon = moon[mask]
    if len(flow) < 2:
        return pd.Series({'r': None, 'p': None, 'z': None})
    r, p = pearsonr(flow, moon)
    z = np.arctanh(r) * np.sqrt(len(flow) - 3) if abs(r) < 1 else np.inf
    return pd.Series({'r': r, 'p': p, 'z': z})

def run_analysis(flow_csv, moon_csv, output_csv='z_bias_output.csv'):
    flow_df = pd.read_csv(flow_csv)
    flow_df['timestamp'] = pd.to_datetime(flow_df['external_timestamp'], errors='coerce')
    n_bad = flow_df['timestamp'].isna().sum()
    if n_bad:
        print(f"Dropping {n_bad} rows from flow_df with unparseable timestamps")
    flow_df = flow_df.dropna(subset=['timestamp'])

    moon_df = pd.read_csv(moon_csv)
    moon_df['timestamp'] = pd.to_datetime(moon_df['timestamp'], errors='coerce')
    moon_df = moon_df.dropna(subset=['timestamp'])

    merged_df = pd.merge_asof(
        left=flow_df.sort_values("timestamp"),
        right=moon_df.sort_values("timestamp"),
        on="timestamp",
        tolerance=pd.Timedelta("500ms")
    )

    merged_df = merged_df.sort_values("timestamp")
    merged_df["G"] = merged_df["moon_altitude_deg"]

    grouped = merged_df.groupby("gravity_phase").apply(compute_stats).reset_index()
    grouped.columns = ['moon_segment', 'r', 'p', 'z']

    total_stats = compute_stats(merged_df)
    total_row = pd.DataFrame([{
        'moon_segment': 'global_correlation',
        'r': total_stats['r'],
        'p': total_stats['p'],
        'z': total_stats['z']
    }])

    if {'ascending', 'descending'}.issubset(set(grouped['moon_segment'])):
        z_asc = grouped.loc[grouped['moon_segment'] == 'ascending', 'z'].values[0]
        z_desc = grouped.loc[grouped['moon_segment'] == 'descending', 'z'].values[0]
        z_flip = abs(z_asc) + abs(z_desc)
        z_flip_row = pd.DataFrame([{'moon_segment': 'z_flip', 'r': None, 'p': None, 'z': z_flip}])
    else:
        z_flip_row = pd.DataFrame([{'moon_segment': 'z_flip', 'r': None, 'p': None, 'z': None}])
    if {'ascending', 'descending'}.issubset(set(grouped['moon_segment'])):
        r_asc  = grouped.loc[grouped['moon_segment']=='ascending',  'r'].values[0]
        r_desc = grouped.loc[grouped['moon_segment']=='descending', 'r'].values[0]
        p_asc  = grouped.loc[grouped['moon_segment']=='ascending',  'p'].values[0]
        p_desc = grouped.loc[grouped['moon_segment']=='descending', 'p'].values[0]
        z_asc  = grouped.loc[grouped['moon_segment']=='ascending',  'z'].values[0]
        z_desc = grouped.loc[grouped['moon_segment']=='descending', 'z'].values[0]

        phase_cancel_row = pd.DataFrame([{
            'moon_segment': 'phase_cancellation',
            'r': r_asc  - r_desc,
            'p': p_asc  - p_desc,
            'z': z_asc  - z_desc
    }])
    else:
        phase_cancel_row = pd.DataFrame([{
            'moon_segment': 'phase_cancellation',
            'r': None, 'p': None, 'z': None
    }])


    final_df = pd.concat([grouped, total_row, phase_cancel_row, z_flip_row], ignore_index=True)
    final_df.to_csv(output_csv, index=False)
    print(f"Analysis complete. Results saved to '{output_csv}'.")

if __name__ == "__main__":
    run_analysis("flow.csv", "moon.csv")
