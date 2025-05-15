
import time
import csv
import os
from datetime import datetime

INFILE = 'FlowShamBo_REALTIME_RESULTS_V2.csv'
OUTFILE = 'flow.csv'

def monitor_and_timestamp():
    # Wait until the input file exists
    while not os.path.exists(INFILE):
        print(f"Waiting for {INFILE} to be created...")
        time.sleep(0.5)

    # Wait until the file has a readable header
    while True:
        with open(INFILE, 'r') as testfile:
            reader = csv.reader(testfile)
            try:
                header = next(reader)
                if header:
                    break
            except StopIteration:
                pass
        print("Waiting for header to appear in CSV...")
        time.sleep(0.5)

    # Begin reading data after header is present
    with open(INFILE, 'r') as infile, open(OUTFILE, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(['external_timestamp'] + header)

        while True:
            line = infile.readline()
            if not line:
                time.sleep(0.1)
                continue

            try:
                row = next(csv.reader([line]))
                timestamp = datetime.now()
                writer.writerow([timestamp] + row)
            except Exception as e:
                print(f"Error processing line: {e}")
                continue

if __name__ == '__main__':
    monitor_and_timestamp()
