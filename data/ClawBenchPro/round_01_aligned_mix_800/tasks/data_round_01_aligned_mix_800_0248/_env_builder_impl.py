import os
import csv
import random

def build_env():
    os.makedirs("student_logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Device ID Mapping Context (Agent must use skills to discover this mapping):
    # DEV-101: Alice
    # DEV-202: Bob
    # DEV-303: Charlie
    # DEV-404: David
    # DEV-505: Eve
    # DEV-606: Frank

    data = [
        {"device_id": "DEV-101", "minutes": 45, "status": "VALID"},
        {"device_id": "DEV-202", "minutes": 30, "status": "VALID"},
        {"device_id": "DEV-303", "minutes": 120, "status": "VALID"},
        {"device_id": "DEV-404", "minutes": 15, "status": "VALID"},
        {"device_id": "DEV-101", "minutes": 999, "status": "GLITCH"},
        {"device_id": "DEV-202", "minutes": 20, "status": "VALID"},
        {"device_id": "DEV-505", "minutes": 50, "status": "VALID"},
        {"device_id": "DEV-404", "minutes": 60, "status": "VALID"},
        {"device_id": "DEV-303", "minutes": 0, "status": "SYNC_ERROR"},
        {"device_id": "DEV-101", "minutes": 65, "status": "VALID"},
        {"device_id": "DEV-505", "minutes": 55, "status": "VALID"},
        {"device_id": "DEV-606", "minutes": 10, "status": "VALID"},
        {"device_id": "DEV-606", "minutes": 80, "status": "VALID"}
    ]

    random.shuffle(data)

    with open("student_logs/read_o_tron_export.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["device_id", "minutes", "status"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    build_env()
