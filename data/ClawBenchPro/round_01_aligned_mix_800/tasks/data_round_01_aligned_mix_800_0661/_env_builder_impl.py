import os
import csv
import json

def build_env():
    # Create the dirty manifests directory
    os.makedirs("manifests", exist_ok=True)

    # Batch A: CSV format
    csv_data = [
        ["tracking_number", "destination", "zone_code", "is_vip"],
        ["TRK-7771", "101 Financial Blvd", "7", "TRUE"],
        ["TRK-7001", "202 Market St", "7", "FALSE"],
        ["TRK-3001", "99 Suburbia Ln", "3", "FALSE"]
    ]
    with open("manifests/batch_A.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # Batch B: JSON format
    json_data = [
        {"trk": "TRK-7002", "addr": "303 Industry Park", "zone": 7, "priority": "standard"},
        {"trk": "TRK-9001", "addr": "88 Faraway Rd", "zone": 9, "priority": "standard"},
        {"trk": "TRK-7772", "addr": "404 Executive Tower", "zone": 7, "priority": "VIP"}
    ]
    with open("manifests/batch_B.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    # Batch C: Messy text format
    txt_data = """--- ROUTE LOG ---
Package: TRK-3002 | Dest: 12 Residential Ct | Area: Zone 3 | Status: Normal
Package: TRK-7003 | Dest: 505 Startup Ave | Area: Zone 7 | Status: Normal
-----------------
"""
    with open("manifests/batch_C.txt", "w", encoding="utf-8") as f:
        f.write(txt_data)

if __name__ == "__main__":
    build_env()
