import os
import csv
import json
import random

def build_env():
    # Setup directories
    base_dir = "raw_recovery"
    export_dir = "export"
    os.makedirs(f"{base_dir}/telemetry/nodes", exist_ok=True)
    os.makedirs(f"{base_dir}/metadata/manifests", exist_ok=True)
    os.makedirs(f"{base_dir}/logs", exist_ok=True)
    os.makedirs(export_dir, exist_ok=True)

    # 1. Manifest: Defining which sensors are valid
    valid_sensors = [f"SNS-{i:04d}" for i in range(100, 115)]
    ghost_sensors = [f"GHOST-{i:04d}" for i in range(50)]
    manifest = {
        "active_rig_id": "APEX-01",
        "valid_transducers": valid_sensors,
        "environment": "high_stress_chamber"
    }
    with open(f"{base_dir}/metadata/manifests/cluster_manifest.json", "w") as f:
        json.dump(manifest, f)

    # 2. System Logs: One sensor is a liar
    malfunctioning_sensor = "SNS-0105"
    with open(f"{base_dir}/logs/system_status.log", "w") as f:
        f.write("2023-10-27 10:00:01 INFO: System Boot\n")
        f.write(f"2023-10-27 10:15:22 WARNING: Sensor {malfunctioning_sensor} reporting erratic voltage.\n")
        f.write(f"2023-10-27 10:15:45 CRITICAL: {malfunctioning_sensor} marked as MALFUNCTION. DISCARD ALL DATA.\n")

    # 3. Fragmented Data Generation
    # Sub-folder A: CSV data (Bulk)
    for i in range(5):
        with open(f"{base_dir}/telemetry/nodes/batch_{i}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "id", "val_lbf", "defl_mm"])
            for _ in range(50):
                s_id = random.choice(valid_sensors + ghost_sensors)
                writer.writerow([1698390000 + random.randint(0, 1000), s_id, round(random.uniform(50, 400), 2), round(random.uniform(0.1, 4.5), 2)])

    # Sub-folder B: JSON Snippets (The "Scattered" data)
    # Injecting the peak load here
    peak_data = {"ts": 1698391000, "id": "SNS-0112", "val_lbf": 2450.85, "defl_mm": 4.8}
    with open(f"{base_dir}/telemetry/nodes/fragment_peak.json", "w") as f:
        json.dump(peak_data, f)
        
    # Injecting deflection breaches
    breach_1 = {"ts": 1698391005, "id": "SNS-0102", "val_lbf": 1200.0, "defl_mm": 5.8}
    breach_2 = {"ts": 1698391010, "id": "SNS-0109", "val_lbf": 900.0, "defl_mm": 6.2}
    # This one should be ignored because it's the malfunctioning sensor
    fake_breach = {"ts": 1698391015, "id": malfunctioning_sensor, "val_lbf": 9999.9, "defl_mm": 9.9}
    
    for idx, data in enumerate([breach_1, breach_2, fake_breach]):
        with open(f"{base_dir}/telemetry/nodes/frag_{idx}.json", "w") as f:
            json.dump(data, f)

    # 4. Noise/Decoys
    # Empty CSVs
    with open(f"{base_dir}/telemetry/nodes/empty.csv", "w") as f:
        f.write("ts,id,val_lbf,defl_mm\n")
    
    # Legacy format files (should be ignored based on manifest)
    for i in range(10):
        with open(f"{base_dir}/telemetry/nodes/legacy_{i}.dat", "w") as f:
            f.write(f"LEGACY_DATA|{random.choice(ghost_sensors)}|{random.random()}")

    # Nested deceptive directories
    os.makedirs(f"{base_dir}/telemetry/nodes/backup/temp", exist_ok=True)
    with open(f"{base_dir}/telemetry/nodes/backup/temp/old_run.csv", "w") as f:
        f.write("ts,id,val_lbf,defl_mm\n100,GHOST-999,9999,9999")

if __name__ == "__main__":
    build_env()
