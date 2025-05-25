
import time
import ntplib
from datetime import datetime, timedelta

LOG_FILE = "gpct_time.csv"
SAMPLE_INTERVAL = 1
STATUS_INTERVAL = 30

try:
    days = int(input("How many days should the tracker run? "))
except ValueError:
    print("Invalid input. Exiting.")
    exit()

end_time = datetime.now() + timedelta(days=days)

c = ntplib.NTPClient()

try:
    with open(LOG_FILE, "x") as f:
        f.write("external_timestamp,flow_meter\n")
except FileExistsError:
    pass

sample_count = 0
print("Tracking time drift. Press Ctrl+C to quit at any time.")

try:
    while datetime.now() < end_time:
        try:
            response = c.request('pool.ntp.org', version=3)
            gps_time = response.tx_time
            system_time = time.time()
            drift_ns = (system_time - gps_time) * 1e9
            timestamp = datetime.now().isoformat()
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp},{drift_ns:.3f}\n")

            sample_count += 1

            if sample_count % STATUS_INTERVAL == 0:
                print(f"[{timestamp}] flow_meter: {drift_ns:.3f} ns — Logged {sample_count} samples")

        except Exception as e:
            print("NTP error:", e)
            time.sleep(5)
            continue

        time.sleep(SAMPLE_INTERVAL)

    print("Time tracking complete. Log saved to gpct_time.csv.")

except KeyboardInterrupt:
    print("\nTracking stopped by user. Log saved to gpct_time.csv.")
