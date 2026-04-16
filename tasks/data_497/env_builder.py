import os
import json
import csv
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def build_env():
    base_dir = "assets/data_497"
    logs_dir = os.path.join(base_dir, "truck_logs")
    
    os.makedirs(os.path.join(logs_dir, "monday"), exist_ok=True)
    os.makedirs(os.path.join(logs_dir, "tuesday"), exist_ok=True)
    os.makedirs(os.path.join(logs_dir, "misc"), exist_ok=True)
    os.makedirs(os.path.join(logs_dir, "friday"), exist_ok=True)

    # Ground truth points chronologically
    points = [
        {"ts": "2023-10-01T10:00:00Z", "lat": 43.00, "lon": -89.00, "speed": 55},
        {"ts": "2023-10-01T10:05:00Z", "lat": 43.05, "lon": -89.02, "speed": 62},
        {"ts": "2023-10-01T10:10:00Z", "lat": 43.10, "lon": -89.05, "speed": 68},
        {"ts": "2023-10-01T10:15:00Z", "lat": 43.15, "lon": -89.00, "speed": 74}, # Max speed
        {"ts": "2023-10-01T10:20:00Z", "lat": 43.20, "lon": -88.95, "speed": 60},
    ]

    # Calculate ground truth miles
    total_miles = 0.0
    for i in range(1, len(points)):
        total_miles += haversine(
            points[i-1]["lat"], points[i-1]["lon"],
            points[i]["lat"], points[i]["lon"]
        )

    # Save Ground truth secretly
    with open(os.path.join(base_dir, ".ground_truth.json"), "w") as f:
        json.dump({"top_speed": 74, "total_miles": total_miles}, f)

    # Distribute points into messy formats
    
    # File 1: CSV (monday/trip_1.csv) -> Points 0 and 3
    csv_file = os.path.join(logs_dir, "monday", "trip_1.csv")
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "lat", "lon", "speed"])
        writer.writerow([points[0]["ts"], points[0]["lat"], points[0]["lon"], points[0]["speed"]])
        writer.writerow([points[3]["ts"], points[3]["lat"], points[3]["lon"], points[3]["speed"]])

    # File 2: JSON (tuesday/data.json) -> Points 1 and 4
    json_file = os.path.join(logs_dir, "tuesday", "data.json")
    with open(json_file, "w") as f:
        data = [
            {"time": points[1]["ts"], "latitude": points[1]["lat"], "longitude": points[1]["lon"], "speed_mph": points[1]["speed"]},
            {"time": points[4]["ts"], "latitude": points[4]["lat"], "longitude": points[4]["lon"], "speed_mph": points[4]["speed"]}
        ]
        json.dump(data, f, indent=2)

    # File 3: JSON Lines (friday/gps.jsonl) -> Point 2
    jsonl_file = os.path.join(logs_dir, "friday", "gps.jsonl")
    with open(jsonl_file, "w") as f:
        f.write(json.dumps({"ts": points[2]["ts"], "lat": points[2]["lat"], "lng": points[2]["lon"], "spd": points[2]["speed"]}) + "\n")

    # File 4: Corrupted log (misc/corrupted.log) -> Garbage data
    bad_file = os.path.join(logs_dir, "misc", "corrupted.log")
    with open(bad_file, "w") as f:
        f.write("ERROR 502: OBD SENSOR DISCONNECTED\n")
        f.write("2023-10-01T10:12:00Z NULL NULL NaN\n")
        f.write("Just some random text because the truck hit a bump.\n")

if __name__ == "__main__":
    build_env()
