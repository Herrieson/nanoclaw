import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("telemetry", exist_ok=True)
    os.makedirs("export", exist_ok=True)

    # Valid data generation
    sensors = [f"TX-{i:03d}" for i in range(1, 11)]
    
    # File 1: Normal data
    with open("telemetry/run_01.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "transducer_id", "load_lbf", "deflection_mm"])
        for i in range(50):
            writer.writerow([
                1600000000 + i,
                random.choice(sensors),
                round(random.uniform(100.0, 500.0), 2),
                round(random.uniform(0.5, 3.5), 2)
            ])

    # File 2: Contains the peak load and some threshold breaches
    with open("telemetry/run_02.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "transducer_id", "load_lbf", "deflection_mm"])
        for i in range(30):
            writer.writerow([
                1600000100 + i,
                random.choice(sensors),
                round(random.uniform(200.0, 800.0), 2),
                round(random.uniform(2.0, 4.9), 2)
            ])
        # Inject deterministic peak
        writer.writerow([1600000150, "TX-007", 1250.75, 4.2])
        # Inject deterministic breaches (> 5.0)
        writer.writerow([1600000151, "TX-004", 800.00, 5.3])
        writer.writerow([1600000152, "TX-009", 750.50, 6.1])

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
        writer.writerow(["1600000200", "invalid_payload"])

if __name__ == "__main__":
    build_env()
