
import pandas as pd
from tzlocal import get_localzone
import numpy as np
import ephem

# Observer location:
lat, lon = '47.601558', '-122.364796'
observer = ephem.Observer()
observer.lat = lat
observer.lon = lon
observer.elevation = 0

# Generate minute-by-minute timestamps
times = pd.date_range(start="2025-04-27 00:00:00", end="2025-05-20 23:59:59", freq="1min")
local_tz = get_localzone()  # Automatically uses system timezone
times = times.tz_localize('UTC').tz_convert(local_tz)
times = times.tz_localize(None)
prev_alt = None
moon_altitudes = []
gravity_phases = []

# Calculate moon altitude and gravitational phase (near/far side)
for time in times:
    observer.date = time
    moon = ephem.Moon(observer)
    alt_deg = float(moon.alt) * 180 / np.pi
    moon_altitudes.append(alt_deg)
    if prev_alt is None:
        gravity_phases.append('ascending')  # Arbitrary for first point
    else:
        gravity_phases.append('ascending' if alt_deg > prev_alt else 'descending')
    prev_alt = alt_deg

# Create DataFrame
moon_df = pd.DataFrame({
    "timestamp": times,
    "moon_altitude_deg": moon_altitudes,
    "gravity_phase": gravity_phases
})

# Save to CSV
moon_df.to_csv("moon.csv", index=False)
print("Moon data saved to moon.csv")
