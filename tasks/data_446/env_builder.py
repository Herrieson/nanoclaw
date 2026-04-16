import os
import csv
import json
import random

def build_env():
    base_dir = "assets/data_446"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Generate Hot Sheet (JSON)
    # The primary stolen vehicle (10-99) is 5KTE342
    # Secondary stolen vehicle is 8YYY999 (fewer hits)
    hot_sheet = {
        "department": "State Police - Sector 4",
        "date": "2023-10-24",
        "plates": [
            {"plate": "1ABC123", "status": "10-39", "notes": "Clear"},
            {"plate": "5KTE342", "status": "10-99", "notes": "Felony GTA - Armed and Dangerous"},
            {"plate": "9ZZZ111", "status": "10-39", "notes": "Clear"},
            {"plate": "8YYY999", "status": "10-99", "notes": "Misdemeanor Warrant"},
            {"plate": "2DEF456", "status": "10-39", "notes": "Clear"}
        ]
    }

    with open(os.path.join(base_dir, "hot_sheet.json"), "w", encoding="utf-8") as f:
        json.dump(hot_sheet, f, indent=4)

    # 2. Generate ALPR Logs (CSV)
    # 5KTE342 should have the most hits among the 10-99s.
    alpr_data = [
        # Random noise
        ("07:15:22", "1ABC123", "Main St & 1st Ave"),
        ("07:18:10", "2DEF456", "Highway 101 Northbound"),
        # Target plate sequence
        ("08:00:45", "5KTE342", "Main St & 1st Ave"),
        ("08:45:12", "5KTE342", "Highway 101 Northbound"),
        ("09:12:33", "8YYY999", "Elm Street Suburbs"), # Other 10-99 hit (only 1)
        ("09:30:05", "5KTE342", "Industrial Parkway"),
        ("10:05:50", "9ZZZ111", "Downtown Crossing"),
        ("11:15:20", "5KTE342", "Abandoned Lot, 5th Sector"),
        ("12:22:15", "1ABC123", "Downtown Crossing"),
        ("14:20:00", "5KTE342", "Warehouse 42, Port District") # Last location
    ]

    # Add a lot of noise so it's not trivial to just eyeball
    for i in range(150):
        hh = str(random.randint(0, 23)).zfill(2)
        mm = str(random.randint(0, 59)).zfill(2)
        ss = str(random.randint(0, 59)).zfill(2)
        plate = f"{random.randint(1,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100,999)}"
        loc = random.choice(["Main St & 1st Ave", "Highway 101 Northbound", "Industrial Parkway", "Downtown Crossing", "Elm Street Suburbs"])
        alpr_data.append((f"{hh}:{mm}:{ss}", plate, loc))

    # Sort chronologically just in case, though they are written out of order mostly, wait, let's mix them up to test sorting
    random.shuffle(alpr_data)

    with open(os.path.join(base_dir, "alpr_logs.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "plate", "location"])
        writer.writerows(alpr_data)

if __name__ == "__main__":
    build_env()
