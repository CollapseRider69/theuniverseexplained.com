
import pandas as pd

# Load your original dataset
df = pd.read_csv("merged_data.csv", parse_dates=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# --- Detect lunar midnights (lowest altitude every 24.84h) ---
def find_lunar_midnights(df):
    lunar_midnights = []
    window_hours = 24.84
    start_time = df["timestamp"].iloc[0]
    end_time = df["timestamp"].iloc[-1]
    current_start = start_time

    while current_start < end_time:
        current_end = current_start + pd.Timedelta(hours=window_hours)
        window_df = df[(df["timestamp"] >= current_start) & (df["timestamp"] < current_end)]

        if not window_df.empty:
            min_row = window_df.loc[window_df["moon_altitude_deg"].idxmin()]
            lunar_midnights.append(min_row["timestamp"])

        current_start = current_end

    return lunar_midnights

# Assign lunar midnight to each row
def annotate_with_midnight(df, midnights):
    all_rows = []
    for lm in midnights:
        temp_df = df.copy()
        temp_df["hours_since_lunar_midnight"] = (temp_df["timestamp"] - lm).dt.total_seconds() / 3600.0
        temp_df["lunar_midnight"] = lm
        # Keep only rows within 0–24.84h of that midnight
        temp_df = temp_df[(temp_df["hours_since_lunar_midnight"] >= 0) & (temp_df["hours_since_lunar_midnight"] < 24.84)]
        all_rows.append(temp_df)
    return pd.concat(all_rows).sort_values("timestamp").reset_index(drop=True)

# Run it
lunar_midnights = find_lunar_midnights(df)
annotated_df = annotate_with_midnight(df, lunar_midnights)

# Save it
annotated_df.to_csv("lunar_aligned.csv", index=False)
print("✅ Created lunar_aligned.csv with timestamp, altitude, flow, and alignment.")
