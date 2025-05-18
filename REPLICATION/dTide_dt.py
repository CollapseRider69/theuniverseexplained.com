
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Load and parse the XML data
tree = ET.parse("id.xml")
root = tree.getroot()

# Extract tide predictions with timestamps
records = []
for item in root.iter("item"):
    date = item.find("date").text
    time = item.find("time").text
    pred = float(item.find("pred").text)
    timestamp = datetime.strptime(f"{date} {time}", "%Y/%m/%d %H:%M")
    records.append({"timestamp": timestamp, "pred": pred})

# Create DataFrame and calculate dTide/dt
df = pd.DataFrame(records)
df["dTide_dt"] = df["pred"].diff()  # per minute

# Drop the first row which has NaN due to diff
df = df.dropna()

# Save as CSV
df.to_csv("tide_dTide_dt.csv", index=False)
print("dTide_dt data saved to tide_dTide_dt.csv")
