import subprocess
import time
import os
from datetime import datetime
import signal
import sys

print("🚀 FlowShamBo + Logger launching at", datetime.now(), flush=True)

runner = subprocess.Popen(["python3", "FlowShamBo_REALTIME_RUNNER_V2.py"])
logger = subprocess.Popen(["python3", "FlowShamBo_external_realtime_logger.py"])

def shutdown_handler(signum, frame):
    print("\n🛑 Caught interrupt. Terminating subprocesses...", flush=True)
    runner.terminate()
    logger.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

print("🕒 Waiting 15 seconds before monitoring progress...", flush=True)
time.sleep(15)

timestamp_file = "flow.csv"
last_line_count = 0
last_change_time = time.time()

print("📡 Monitoring FlowShamBo progress... (press Ctrl+C to quit)", flush=True)

while True:
    try:
        if os.path.exists(timestamp_file):
            with open(timestamp_file, "r", errors="ignore") as f:
                lines = f.readlines()
            lines = [line for line in lines if "\x00" not in line]
            line_count = len(lines)

            if line_count > last_line_count:
                last_data_line = lines[-1].strip()
                rounds_completed = line_count - 1
                print(f"[{int(time.time() - last_change_time)}s] {rounds_completed:,} rounds complete → {last_data_line}", flush=True)
                last_line_count = line_count
                last_change_time = time.time()

        # Exit if no new lines added in 120 seconds
        if time.time() - last_change_time > 120:
            print("✅ No new data for 120 seconds. Exiting monitor.", flush=True)
            break

    except Exception as e:
        print(f"⚠️ Error during monitoring: {e}", flush=True)

    time.sleep(10)
