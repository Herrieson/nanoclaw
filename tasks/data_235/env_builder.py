import os
import json
import gzip
import random

def build_env():
    base_dir = "assets/data_235"
    os.makedirs(base_dir, exist_ok=True)
    gps_dir = os.path.join(base_dir, "gps_data")
    os.makedirs(gps_dir, exist_ok=True)

    # 1. Generate locations.json
    locations = [
        {"name": "Des Moines Truck Stop", "lat": 41.6312, "lon": -93.5821},
        {"name": "Iowa State Capitol", "lat": 41.5911, "lon": -93.6037},
        {"name": "Retro Threads", "lat": 41.5868, "lon": -93.6250},
        {"name": "Omaha Warehouse", "lat": 41.2565, "lon": -95.9345}
    ]
    with open(os.path.join(base_dir, "locations.json"), "w") as f:
        json.dump(locations, f, indent=4)

    # 2. Generate GPS logs (gzipped)
    # Format: TIMESTAMP, LAT, LON, SPEED
    
    # Truck 1: Normal route to Omaha
    t1_data = []
    for i in range(10):
        t1_data.append(f"2023-10-25T10:0{i}:00Z, {41.6 + i*0.01:.4f}, {-93.5 - i*0.02:.4f}, 65")
    
    # Truck 2: Normal route somewhere else
    t2_data = []
    for i in range(10):
        t2_data.append(f"2023-10-25T11:0{i}:00Z, {41.0 - i*0.01:.4f}, {-94.0 - i*0.01:.4f}, 60")
        
    # Truck 3: The Culprit. Stops near Retro Threads (41.5868, -93.6250)
    t3_data = []
    for i in range(5):
        t3_data.append(f"2023-10-25T13:0{i}:00Z, {41.6500 - i*0.01:.4f}, {-93.6000 - i*0.005:.4f}, 45")
    # Parked at Retro Threads (slightly offset to require distance/nearness logic, not string matching)
    t3_data.append(f"2023-10-25T13:05:00Z, 41.5865, -93.6248, 0")
    t3_data.append(f"2023-10-25T13:06:00Z, 41.5865, -93.6248, 0")
    for i in range(7, 10):
        t3_data.append(f"2023-10-25T13:0{i}:00Z, {41.5865 - (i-6)*0.01:.4f}, {-93.6248 - (i-6)*0.01:.4f}, 55")

    # Truck 4: Normal route
    t4_data = []
    for i in range(10):
        t4_data.append(f"2023-10-25T14:0{i}:00Z, {42.0 + i*0.01:.4f}, {-93.0 + i*0.01:.4f}, 70")

    trucks = {
        "truck_1": t1_data,
        "truck_2": t2_data,
        "truck_3": t3_data,
        "truck_4": t4_data
    }

    for t_id, data in trucks.items():
        file_path = os.path.join(gps_dir, f"{t_id}.log.gz")
        with gzip.open(file_path, "wt") as f:
            f.write("TIMESTAMP, LAT, LON, SPEED\n")
            f.write("\n".join(data) + "\n")

if __name__ == "__main__":
    build_env()
