import os
import csv
import json

def build_env():
    # Create directories
    os.makedirs("sensor_dumps", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # File 1: CSV format
    csv_data = [
        ["sample_id", "timestamp", "amplitude", "status"],
        ["SAMP-Alpha", "1620000001", "45.5", "OK"],
        ["SAMP-Alpha", "1620000002", "-12.0", "OK"], # Invalid (negative)
        ["SAMP-Beta", "1620000003", "88.0", "OK"],
        ["SAMP-Alpha", "1620000004", "55.5", "OK"],
        ["SAMP-Gamma", "1620000005", "10.0", "ERR"], # Invalid (ERR)
        ["SAMP-Beta", "1620000006", "92.0", "OK"]
    ]
    with open(os.path.join("sensor_dumps", "log_set_1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # File 2: JSON Lines format (to test agent's ability to handle multiple formats)
    jsonl_data = [
        {"sample_id": "SAMP-Gamma", "timestamp": "1620000007", "amplitude": 120.0, "status": "OK"},
        {"sample_id": "SAMP-Alpha", "timestamp": "1620000008", "amplitude": 50.5, "status": "OK"},
        {"sample_id": "SAMP-Beta", "timestamp": "1620000009", "amplitude": -5.0, "status": "ERR"}, # Invalid
        {"sample_id": "SAMP-Gamma", "timestamp": "1620000010", "amplitude": 130.0, "status": "OK"}
    ]
    with open(os.path.join("sensor_dumps", "log_set_2.jsonl"), "w") as f:
        for item in jsonl_data:
            f.write(json.dumps(item) + "\n")

    # Expected Logic:
    # SAMP-Alpha: 45.5, 55.5, 50.5 -> Avg: 50.5
    # SAMP-Beta: 88.0, 92.0 -> Avg: 90.0
    # SAMP-Gamma: 120.0, 130.0 -> Avg: 125.0

if __name__ == "__main__":
    build_env()
