import os
import csv
import json
import random
import math

def build_env():
    random.seed(42) # Ensure determinism

    # 1. Create directory structure
    os.makedirs("workspace", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    os.makedirs("sys_logs", exist_ok=True)
    
    # 2. Setup Device to Sample mapping
    samples = ["SAMP-Alpha", "SAMP-Beta", "SAMP-Gamma", "SAMP-Delta", "SAMP-Omega"]
    devices = {f"XR900-{str(i).zfill(3)}": random.choice(samples) for i in range(1, 16)}
    
    # Write registry (with some decoy noise in the config folder)
    with open(os.path.join("config", "device_registry.json"), "w") as f:
        json.dump(devices, f, indent=4)
        
    # Decoy registry
    with open(os.path.join("config", "device_registry.json.bak"), "w") as f:
        json.dump({"XR900-001": "SAMP-OLD", "XR900-999": "SAMP-INVALID"}, f)

    # 3. Setup Power Spikes (Blackouts)
    # Define 3 blackout windows
    blackouts = [
        (1696005000, 1696010000),
        (1696050000, 1696060000),
        (1696100000, 1696105000)
    ]
    
    with open(os.path.join("sys_logs", "power_events.txt"), "w") as f:
        f.write("FACILITY INCIDENT REPORT\n")
        f.write("========================\n\n")
        f.write("The following times represent critical grid failures.\n")
        for i, (start, end) in enumerate(blackouts, 1):
            f.write(f"Event #{i}: Major grid failure between {start} and {end}. Impact: Severe. All telemetry invalid.\n")
            f.write("Maintenance crew dispatched.\n\n")

    # 4. Generate Sensor Dumps (Scale & Fragmentation)
    # We will generate data across 10 different "day" folders
    base_time = 1696000000
    
    expected_sums = {s: 0.0 for s in samples}
    expected_counts = {s: 0 for s in samples}

    for day in range(1, 11):
        day_dir = os.path.join("sensor_dumps", f"day_{str(day).zfill(2)}")
        os.makedirs(day_dir, exist_ok=True)
        
        # Determine time range for the day
        day_start = base_time + (day - 1) * 86400
        
        # Generate 1 CSV file and 1 JSONL file per day, plus 1 junk file
        csv_data = [["device_id", "timestamp", "amplitude", "status"]]
        jsonl_data = []
        
        # Generate 500 records per day
        for _ in range(500):
            dev_id = random.choice(list(devices.keys()))
            ts = random.randint(day_start, day_start + 86400)
            
            # Determine validity
            is_blackout = any(start <= ts <= end for start, end in blackouts)
            
            # 70% chance of valid amplitude, 30% negative
            is_amp_valid = random.random() < 0.7
            amplitude = round(random.uniform(10.0, 150.0), 2) if is_amp_valid else round(random.uniform(-50.0, -1.0), 2)
            
            # 80% chance of OK status
            status_choices = ["OK", "ERR", "WARN", "OOM", "TIMEOUT"]
            status = "OK" if random.random() < 0.8 else random.choice(status_choices[1:])
            
            record = {
                "device_id": dev_id,
                "timestamp": ts,
                "amplitude": amplitude,
                "status": status
            }
            
            # Add to ground truth if fully valid
            if not is_blackout and amplitude >= 0 and status == "OK":
                sample_id = devices[dev_id]
                expected_sums[sample_id] += amplitude
                expected_counts[sample_id] += 1
                
            if random.choice([True, False]):
                csv_data.append([dev_id, str(ts), str(amplitude), status])
            else:
                jsonl_data.append(record)
                
        # Write files
        with open(os.path.join(day_dir, f"telemetry_{day}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
            
        with open(os.path.join(day_dir, f"telemetry_{day}.jsonl"), "w") as f:
            for item in jsonl_data:
                f.write(json.dumps(item) + "\n")
                
        # Write decoy/junk file
        with open(os.path.join(day_dir, f"cache_{day}.tmp"), "wb") as f:
            f.write(os.urandom(1024)) # Unparseable binary noise
            
        # Add a file with missing headers or wrong schema just to test robust parsing
        if day % 3 == 0:
            with open(os.path.join(day_dir, f"broken_{day}.csv"), "w") as f:
                f.write("just,some,random,garbage,data\n")
                f.write("1,2,3,4,5\n")

    # Ground truth validation (for reference)
    # expected_averages = {s: round(expected_sums[s] / expected_counts[s], 2) for s in samples if expected_counts[s] > 0}
    # print("DEBUG GROUND TRUTH:", expected_averages)

if __name__ == "__main__":
    build_env()
