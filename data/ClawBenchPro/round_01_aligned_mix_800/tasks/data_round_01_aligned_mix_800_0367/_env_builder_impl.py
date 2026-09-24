import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("sensor_dumps", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # File 1: CSV format
    # True expected offsets: XR9-A01 (+2.5), XR9-B02 (-1.0), XR9-C03 (0.0)
    csv_data = [
        ["sample_id", "timestamp", "raw_amplitude", "status", "batch_id"],
        ["SAMP-Alpha", "1620000001", "43.0", "OK", "XR9-A01"],  # True: 45.5
        ["SAMP-Alpha", "1620000002", "-14.5", "OK", "XR9-A01"], # True: -12.0 (Invalid)
        ["SAMP-Beta", "1620000003", "89.0", "OK", "XR9-B02"],   # True: 88.0
        ["SAMP-Alpha", "1620000004", "53.0", "OK", "XR9-A01"],  # True: 55.5
        ["SAMP-Gamma", "1620000005", "10.0", "ERR", "XR9-C03"], # True: 10.0 (ERR, Invalid)
        ["SAMP-Beta", "1620000006", "93.0", "OK", "XR9-B02"]    # True: 92.0
    ]
    with open(os.path.join("sensor_dumps", "log_set_1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: JSON Lines format
    jsonl_data = [
        {"sample_id": "SAMP-Gamma", "timestamp": "1620000007", "raw_amplitude": 120.0, "status": "OK", "batch_id": "XR9-C03"}, # True: 120.0
        {"sample_id": "SAMP-Alpha", "timestamp": "1620000008", "raw_amplitude": 48.0, "status": "OK", "batch_id": "XR9-A01"}, # True: 50.5
        {"sample_id": "SAMP-Beta", "timestamp": "1620000009", "raw_amplitude": -4.0, "status": "ERR", "batch_id": "XR9-B02"}, # True: -5.0 (ERR, Invalid)
        {"sample_id": "SAMP-Gamma", "timestamp": "1620000010", "raw_amplitude": 130.0, "status": "OK", "batch_id": "XR9-C03"} # True: 130.0
    ]
    with open(os.path.join("sensor_dumps", "log_set_2.jsonl"), "w") as f:
        for item in jsonl_data:
            f.write(json.dumps(item) + "\n")

    # Expected Final True Logic:
    # SAMP-Alpha Valid True Amplitudes: 45.5, 55.5, 50.5 -> Avg: 50.5
    # SAMP-Beta Valid True Amplitudes: 88.0, 92.0 -> Avg: 90.0
    # SAMP-Gamma Valid True Amplitudes: 120.0, 130.0 -> Avg: 125.0

if __name__ == "__main__":
    build_env()
