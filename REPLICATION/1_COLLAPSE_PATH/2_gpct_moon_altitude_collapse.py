import subprocess
import sys
import tzlocal

required = ["pandas", "requests", "ephem", "tzlocal"]
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


import pandas as pd
import requests
from datetime import datetime
import sys

try:
    df = pd.read_csv("flow.csv", usecols=["external_timestamp"])
    df["external_timestamp"] = pd.to_datetime(df["external_timestamp"], format="mixed")
    start_date = (df["external_timestamp"].min() - pd.Timedelta(days=1)).date()
    end_date   = (df["external_timestamp"].max() + pd.Timedelta(days=1)).date()
except Exception as e:
    print(f"Error reading 'flow.csv': {e}")
    sys.exit(1)
print(f"Date range found in flow.csv: {start_date} to {end_date}")

use_auto = input("Use automatic lat/long? (Y/N): ").strip().upper()
lat, lon = None, None

if use_auto == "Y":
    try:
        res = requests.get("https://ipinfo.io/json", timeout=10)
        data = res.json()
        lat, lon = map(float, data["loc"].split(","))
        print(f"\nApproximate location based on IP:\nLatitude: {lat}\nLongitude: {lon}")
        confirm = input("Is this accurate? (Y/N): ").strip().upper()
        if confirm != "Y":
            lat = input("Enter latitude manually: ").strip()
            lon = input("Enter longitude manually: ").strip()
    except Exception as e:
        print(f"Could not retrieve location from IP: {e}")
        lat = input("Enter latitude manually: ").strip()
        lon = input("Enter longitude manually: ").strip()
else:
    lat = input("Enter latitude: ").strip()
    lon = input("Enter longitude: ").strip()

# Validate lat/lon
if not lat or not lon:
    print("Latitude and longitude must be provided. Exiting.")
    sys.exit(1)

# Convert lat/lon to float
try:
    lat = float(lat)
    lon = float(lon)
except ValueError:
    print("Invalid latitude or longitude format. Exiting.")
    sys.exit(1)

print("\nGenerating moon.csv...")

start_date_str = str(start_date)
end_date_str = str(end_date)
latitude = lat
longitude = lon


import pandas as pd
from tzlocal import get_localzone
import numpy as np
import ephem

observer = ephem.Observer()
observer.lat       = str(latitude)
observer.lon       = str(longitude)
observer.elevation = 0


times = pd.date_range(start=start_date, end=end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1), freq="1s")  # patchedlocal_tz = get_localzone()  # Automatically uses system timezone
from tzlocal import get_localzone
local_tz = get_localzone()
times = times.tz_localize('UTC').tz_convert(local_tz)
times = times.tz_localize(None)
prev_alt = None
moon_altitudes = []
gravity_phases = []
moon_distances = []
macro_phases = []

for time in times:
    observer.date = time
    moon = ephem.Moon(observer)
    alt_deg = float(moon.alt) * 180 / np.pi
    moon_altitudes.append(alt_deg)
    dist = moon.earth_distance * ephem.meters_per_au / 1000  # convert AU to km
    moon_distances.append(dist)
    if len(moon_distances) == 1:
        macro_phases.append("unknown")
    else:
        macro_phases.append("apogean" if dist < moon_distances[-2] else "parigean")
    if prev_alt is None:
        gravity_phases.append('ascending')
    else:
        gravity_phases.append('ascending' if alt_deg > prev_alt else 'descending')
    prev_alt = alt_deg

moon_df = pd.DataFrame({
    "moon_distance_km": moon_distances,
    "macro_phase": macro_phases,
    "timestamp": times,
    "moon_altitude_deg": moon_altitudes,
    "gravity_phase": gravity_phases
})

local_tz = tzlocal.get_localzone()
moon_df["timestamp"] = (
    moon_df["timestamp"]
      .dt.tz_localize("UTC")
      .dt.tz_convert(local_tz)
      .dt.tz_localize(None)
)

moon_df.to_csv("moon.csv", index=False)
print("Moon data saved to moon.csv")


print("moon.csv complete.")
