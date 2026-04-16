import os
import random
from datetime import datetime, timedelta

def build_env():
    base_dir = "assets/data_461"
    os.makedirs(base_dir, exist_ok=True)
    
    log_file_path = os.path.join(base_dir, "hike_telemetry.log")
    
    start_time = datetime(2023, 10, 27, 8, 0, 0)
    
    # Generate data
    # We want specific targets to be found.
    # Target 1: ELEV > 2500 (2510), TEMP < 5.0 (3.8)
    # Target 2: ELEV > 2500 (2700), TEMP < 5.0 (-1.2)
    # Target 3: ELEV > 2500 (2650), TEMP < 5.0 (4.9)
    
    data_points = [
        {"elev": 2400, "temp": 6.5, "lat": 36.570, "lon": -118.290},
        {"elev": 2450, "temp": 5.5, "lat": 36.572, "lon": -118.291},
        {"elev": 2510, "temp": 3.8, "lat": 36.575, "lon": -118.293}, # MATCH 1
        {"elev": 2550, "temp": 5.2, "lat": 36.577, "lon": -118.294},
        {"elev": 2600, "temp": 6.0, "lat": 36.580, "lon": -118.296},
        {"elev": 2480, "temp": 2.0, "lat": 36.582, "lon": -118.297},
        {"elev": 2700, "temp": -1.2, "lat": 36.585, "lon": -118.300}, # MATCH 2
        {"elev": 2800, "temp": 5.0, "lat": 36.588, "lon": -118.302},
        {"elev": 2650, "temp": 4.9, "lat": 36.590, "lon": -118.305}, # MATCH 3
        {"elev": 2400, "temp": 4.0, "lat": 36.592, "lon": -118.308},
    ]
    
    lines = []
    for i, dp in enumerate(data_points):
        ts = start_time + timedelta(minutes=i*15)
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        loc_line = f"[{ts_str}] LOC: {dp['lat']},{dp['lon']}, ELEV: {dp['elev']}\n"
        sens_line = f"[{ts_str}] SENS: TEMP={dp['temp']}, HUM={random.randint(30, 60)}\n"
        
        # Interleave randomly to make it slightly messy
        if random.choice([True, False]):
            lines.append(loc_line)
            lines.append(sens_line)
        else:
            lines.append(sens_line)
            lines.append(loc_line)
            
        # Add some noise
        if i % 3 == 0:
            lines.append(f"[{ts_str}] SYS: Battery level {random.randint(50, 90)}%\n")

    with open(log_file_path, "w") as f:
        f.writelines(lines)

if __name__ == "__main__":
    build_env()
