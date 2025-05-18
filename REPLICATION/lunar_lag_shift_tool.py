
import pandas as pd
import matplotlib.pyplot as plt

# Load your tide and moon files
moon_df = pd.read_csv("moon.csv", parse_dates=["timestamp"])
tide_df = pd.read_csv("tide_dTide_dt.csv", parse_dates=["timestamp"])

# Ensure both are sorted by timestamp
moon_df.sort_values("timestamp", inplace=True)
tide_df.sort_values("timestamp", inplace=True)

# Add a 'date' column to group by day
moon_df['date'] = moon_df['timestamp'].dt.date
tide_df['date'] = tide_df['timestamp'].dt.date

# Create output list
results = []
lag_by_date = {}

for date in sorted(set(moon_df['date'])):
    moon_day = moon_df[moon_df['date'] == date]
    tide_day = tide_df[tide_df['date'] == date]

    if moon_day.empty or tide_day.empty:
        continue

    # Find time of lunar noon (max moon altitude)
    lunar_noon_row = moon_day.loc[moon_day['moon_altitude_deg'].idxmax()]
    lunar_noon_time = lunar_noon_row['timestamp']

    # Include next day tide data if lunar noon is after 18:00
    if lunar_noon_time.hour >= 18:
        next_day = lunar_noon_time.date() + pd.Timedelta(days=1)
        tide_day = pd.concat([tide_day, tide_df[tide_df['date'] == next_day]])

    # Find next high tide slope peak (max dTide/dt after lunar noon), capped at +10 hrs
    tide_after_noon = tide_day[
        (tide_day['timestamp'] > lunar_noon_time) &
        (tide_day['timestamp'] <= lunar_noon_time + pd.Timedelta(hours=10))
    ]

    if tide_after_noon.empty:
        # Inherit previous day's lag if available
        fallback_lag = results[-1]['lag_minutes'] if results else None
        if fallback_lag is not None:
            lag_by_date[date] = pd.Timedelta(minutes=fallback_lag)
            results.append({
                "date": date,
                "lunar_noon": lunar_noon_time,
                "high_tide": None,
                "lag_minutes": fallback_lag
            })
        continue

    high_tide_row = tide_after_noon.loc[tide_after_noon['dTide_dt'].idxmax()]
    high_tide_time = high_tide_row['timestamp']

    lag = (high_tide_time - lunar_noon_time).total_seconds() / 60
    lag_by_date[date] = pd.Timedelta(minutes=lag)

    results.append({
        "date": date,
        "lunar_noon": lunar_noon_time,
        "high_tide": high_tide_time,
        "lag_minutes": lag
    })

# Fill backward with first valid lag if needed
if results:
    first_valid_lag = results[0]["lag_minutes"]
    first_valid_date = results[0]["date"]
    all_dates = sorted(set(tide_df['date']))

    for date in all_dates:
        if date < first_valid_date and date not in lag_by_date:
            lag_by_date[date] = pd.Timedelta(minutes=first_valid_lag)

# Save lag summary
lag_df = pd.DataFrame(results)
lag_df.to_csv("daily_lunar_lag.csv", index=False)

# Plot daily lag
plt.figure(figsize=(10, 4))
plt.plot(lag_df['date'], lag_df['lag_minutes'], marker='o')
plt.title("Daily Lunar Lag")
plt.xlabel("Date")
plt.ylabel("Lag (minutes)")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("lunar_lag_plot.png")
plt.close()

# Apply lag to shift tide timestamps
adjusted_tide = []
for _, row in tide_df.iterrows():
    lag = lag_by_date.get(row['date'], pd.Timedelta(0))
    shifted_time = row['timestamp'] - lag
    adjusted_tide.append({
        "timestamp": shifted_time,
        "dTide_dt": row['dTide_dt'],
        "lag_minutes": lag.total_seconds() / 60
    })

adjusted_tide_df = pd.DataFrame(adjusted_tide)
adjusted_tide_df.to_csv("tide.csv", index=False)

print("✅ Saved: daily_lunar_lag.csv, tide.csv (lag-adjusted), and lunar_lag_plot.png")
