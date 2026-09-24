import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("telemetry", exist_ok=True)
    os.makedirs("export", exist_ok=True)

    # Valid data generation
    sensors = [f"TX-{i:03d}" for i in range(1, 11)]
    
    # File 1: Normal data (Raw electrical signals)
    with open("telemetry/run_01.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "transducer_id", "raw_strain_mv", "raw_laser_tof"])
        for i in range(50):
            writer.writerow([
                1600000000 + i,
                random.choice(sensors),
                int(random.uniform(1000, 4500)), # maps to normal load
                int(random.uniform(10, 80))      # maps to normal deflection
            ])

    # File 2: Contains the peak load and some threshold breaches mapped to raw signals
    with open("telemetry/run_02.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "transducer_id", "raw_strain_mv", "raw_laser_tof"])
        for i in range(30):
            writer.writerow([
                1600000100 + i,
                random.choice(sensors),
                int(random.uniform(2000, 6000)),
                int(random.uniform(50, 100))
            ])
        # Inject deterministic peak (Raw signals that the tool will translate to 1250.75 lbf and 4.2 mm)
        writer.writerow([1600000150, "TX-007", 8500, 120])
        
        # Inject deterministic breaches (> 5.0mm) (Raw signals the tool will translate to > 5.0)
        # Tool maps raw_laser_tof 155 -> 5.3mm, 180 -> 6.1mm
        writer.writerow([1600000151, "TX-004", 6200, 155])
        writer.writerow([1600000152, "TX-009", 5900, 180])

    # File 3: Corrupted file (should be ignored)
    with open("telemetry/run_03_err.log", "w") as f:
        f.write("FATAL ERROR: Buffer overflow at address 0x00A3B\n")
        f.write("NULL DATA DUMP\n")
        f.write("?????$$$###\n")

    # File 4: Empty CSV
    with open("telemetry/run_04.csv", "w", newline="") as f:
        pass

    # File 5: Missing columns (Malformed)
    with open("telemetry/run_05.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "data"])
        writer.writerow(["1600000200", "invalid_payload_7A9F"])

if __name__ == "__main__":
    build_env()
