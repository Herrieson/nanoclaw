import os
import json
import csv
import random

def build_env():
    base_dir = "assets/data_57"
    os.makedirs(base_dir, exist_ok=True)
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    drivers = {
        "101": "Bubba Smith",
        "102": "Cletus Jones",
        "103": "Mary Lou",
        "104": "Jim Bob",
        "105": "Sally Mae",
        "106": "Billy Ray"
    }

    with open(os.path.join(base_dir, "drivers.json"), "w") as f:
        json.dump(drivers, f, indent=4)

    random.seed(42)
    statuses = ["COMPLETED", "COMPLETED", "COMPLETED", "FAILED"]

    # Monday - CSV
    with open(os.path.join(logs_dir, "monday.csv"), "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["truck_id", "miles", "deliveries", "status"])
        for _ in range(15):
            writer.writerow([
                random.choice(list(drivers.keys())),
                random.randint(50, 400),
                random.randint(1, 5),
                random.choice(statuses)
            ])

    # Tuesday - JSONL
    with open(os.path.join(logs_dir, "tuesday.jsonl"), "w") as f:
        for _ in range(18):
            record = {
                "truck_id": random.choice(list(drivers.keys())),
                "miles": random.randint(50, 400),
                "deliveries": random.randint(1, 5),
                "status": random.choice(statuses)
            }
            f.write(json.dumps(record) + "\n")

    # Wednesday - TXT (Key-Value)
    with open(os.path.join(logs_dir, "wednesday.txt"), "w") as f:
        for _ in range(12):
            tid = random.choice(list(drivers.keys()))
            m = random.randint(50, 400)
            d = random.randint(1, 5)
            s = random.choice(statuses)
            f.write(f"TRUCK:{tid} MILES:{m} DELIVERIES:{d} STATUS:{s}\n")

if __name__ == "__main__":
    build_env()
