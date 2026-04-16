import os
import textwrap

def build_env():
    base_dir = "assets/data_349"
    os.makedirs(base_dir, exist_ok=True)

    csv_content = """timestamp,lat,lon,speed
2023-10-27T08:00:00Z,43.0000,-87.0000,90
2023-10-27T08:01:00Z,43.0100,-87.0000,90
CORRUPTED_BLUETOOTH_FRAME_XYZ
2023-10-27T08:02:00Z,43.0200,-87.0000,90
2023-10-27T08:03:00Z,43.0200,-87.0000,0
2023-10-27T08:04:00Z,43.0200,-87.0000,0
2023-10-27T08:10:00Z,43.0200,-87.0000,0
ERROR: SIGNAL LOST
2023-10-27T08:11:00Z,43.0300,-87.0000,90
2023-10-27T08:12:00Z,43.0400,-87.0000,90
2023-10-27T08:15:00Z,43.0400,-87.0000,0
2023-10-27T08:20:00Z,43.0400,-87.0000,0
"""

    with open(os.path.join(base_dir, "tracker_data.csv"), "w") as f:
        f.write(csv_content)

    broken_script = """import csv
import json
from datetime import datetime

# I think this is the earth radius in miles? Or km? Whatever.
R = 3959

def haversine(lat1, lon1, lat2, lon2):
    # Found this on stackoverflow, didn't bother importing math, oops
    return (lat2 - lat1) * R 

def process_logs():
    total_dist = 0
    stops = []
    
    with open('tracker_data.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip header
        
        prev_lat = None
        prev_lon = None
        
        for row in reader:
            # This crashes on the bad lines, too lazy to fix
            ts = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%SZ")
            lat = float(row[1])
            lon = float(row[2])
            speed = float(row[3])
            
            if prev_lat is not None:
                total_dist += haversine(prev_lat, prev_lon, lat, lon)
                
            prev_lat = lat
            prev_lon = lon
            
            # TODO: figure out stops
            
    with open('summary.json', 'w') as f:
        json.dump({"total_distance_km": total_dist, "stops": stops}, f)

if __name__ == "__main__":
    process_logs()
"""
    with open(os.path.join(base_dir, "process_gps.py"), "w") as f:
        f.write(broken_script)

if __name__ == "__main__":
    build_env()
