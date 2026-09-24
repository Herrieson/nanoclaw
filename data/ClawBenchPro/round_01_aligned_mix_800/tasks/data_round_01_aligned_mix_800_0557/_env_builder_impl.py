import os
import json
import csv
import random

def build_env():
    # Set seed for deterministic generation to ensure 100% solvable/evaluable results
    random.seed(1516)
    
    os.makedirs("infrastructure", exist_ok=True)
    os.makedirs("telemetry_dumps", exist_ok=True)
    
    sectors = ["A", "B", "C", "D", "E"]
    crops = ["Corn", "Soy", "Wheat", "Barley", "Tomatoes"]
    
    # 1. Generate Sensor Mapping (Multi-hop requirement)
    sensor_mapping = {}
    # Creating 300 sensors
    for i in range(1, 301):
        s_id = f"SN-{i:04d}"
        sensor_mapping[s_id] = random.choice(sectors)
        
    with open(os.path.join("infrastructure", "sensor_mapping.json"), "w") as f:
        json.dump(sensor_mapping, f, indent=2)
        
    def generate_records(num):
        records = []
        for _ in range(num):
            records.append({
                "sensor_id": f"SN-{random.randint(1, 300):04d}",
                "crop": random.choice(crops),
                "moisture": random.randint(-15, 115), # ~25% chance of invalid moisture
                "nitrogen": random.randint(5, 25),    # ~50% chance of invalid nitrogen (>=15)
                "yield": random.randint(100, 1000)
            })
        return records

    # 2. Generate folders for 12 months + 1 decoy calibration folder
    folders = [f"month_{str(i).zfill(2)}" for i in range(1, 13)]
    folders.append("calibration")
    
    # 3. Populate folders with fragmented, noisy data
    for folder in folders:
        path = os.path.join("telemetry_dumps", folder)
        os.makedirs(path, exist_ok=True)
        
        # Each folder gets a mix of CSV, JSON, TSV, and garbage LOG files
        for i in range(4):
            # CSV Format
            with open(os.path.join(path, f"telemetry_c_{i}.csv"), "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["sensor_id", "crop", "moisture", "nitrogen", "yield"])
                writer.writeheader()
                writer.writerows(generate_records(45))
                
            # JSON Format
            with open(os.path.join(path, f"telemetry_j_{i}.json"), "w") as f:
                json.dump(generate_records(35), f, indent=2)
                
            # TSV Format (Tab separated)
            with open(os.path.join(path, f"telemetry_t_{i}.tsv"), "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["sensor_id", "crop", "moisture", "nitrogen", "yield"], delimiter='\t')
                writer.writeheader()
                writer.writerows(generate_records(40))
                
            # Garbage LOG files (Noise/Decoy)
            with open(os.path.join(path, f"watchdog_{i}.log"), "w") as f:
                f.write(f"[ERROR] Watchdog reset triggered on sensor interface bus {i}\n")
                f.write(f"[WARN] Dropped {random.randint(10, 50)} packets due to buffer overflow.\n")
                f.write("DEBUG: Attempting to recalibrate moisture node...\n")

if __name__ == "__main__":
    build_env()
