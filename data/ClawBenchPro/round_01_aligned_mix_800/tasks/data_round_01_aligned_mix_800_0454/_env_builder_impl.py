import os
import json
import random
import csv
from datetime import datetime

def build_env():
    # Base directories
    base_dir = "garage_dump"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create a deep, confusing directory tree
    subdirs = [f"sector_{i}" for i in range(5)]
    for sd in subdirs:
        for j in range(3):
            os.makedirs(os.path.join(base_dir, sd, f"node_{j}"), exist_ok=True)

    all_nodes = []
    for root, dirs, files in os.walk(base_dir):
        if not dirs:
            all_nodes.append(root)

    # 2. Generate the "Truth" - Official Crew
    # We use a mix of names and UUIDs to make it harder
    crew = [
        {"id": "V-9901", "name": "Hector Ramirez"},
        {"id": "V-9902", "name": "Luis Perez"},
        {"id": "V-9903", "name": "Father Thomas"},
        {"id": "V-9904", "name": "Maria Gonzalez"}
    ]
    
    # Hide the roster in a non-obvious place with a misleading name
    roster_path = os.path.join(random.choice(all_nodes), "system_config_v2.cfg")
    with open(roster_path, "w") as f:
        f.write("# CHURCH AUTO MINISTRY - ENROLLED VOLUNTEERS\n")
        f.write("meta_version: 4.0\n")
        for member in crew:
            f.write(f"ENTRY:{member['id']}|{member['name']}\n")

    # 3. Generate Voluminous Noisy Shift Logs
    # Only some shifts belong to the crew.
    fake_names = ["Sketchy Bob", "Random Joe", "Intruder Mike", "Wandering Soul"]
    
    for i in range(150):
        node = random.choice(all_nodes)
        is_real = random.random() > 0.6
        person = random.choice(crew) if is_real else {"id": f"X-{i}", "name": random.choice(fake_names)}
        
        shift_data = {
            "session_id": f"SESS_{i:04d}",
            "worker": person["name"],
            "worker_id": person["id"],
            "hours_logged": round(random.uniform(1.0, 5.0), 1),
            "timestamp": "2023-10-15T10:00:00Z"
        }
        
        # Mix formats: some JSON, some TXT
        if i % 2 == 0:
            with open(os.path.join(node, f"log_delta_{i}.json"), "w") as f:
                json.dump(shift_data, f)
        else:
            with open(os.path.join(node, f"fragment_{i}.tmp"), "w") as f:
                f.write(f"WORKER_ID: {person['id']}\nHOURS: {shift_data['hours_logged']}\nSTATUS: SIGNED")

    # 4. Generate Inventory (The Trap)
    # 4.1 Old/Fake Inventory Files (Noise)
    for i in range(10):
        node = random.choice(all_nodes)
        with open(os.path.join(node, f"inv_backup_2019_{i}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["part", "current_stock", "status"])
            writer.writerow(["Spark Plugs", "50", "archived"])

    # 4.2 The Real Inventory (Fragmented)
    parts_truth = [
        {"part": "Oil Filter", "stock": 3, "status": "verified", "date": "2023-10-01"},
        {"part": "Brake Pads", "stock": 15, "status": "verified", "date": "2023-10-02"},
        {"part": "Alternator", "stock": 1, "status": "verified", "date": "2023-10-05"},
        {"part": "Wiper Blades", "stock": 8, "status": "verified", "date": "2023-10-10"},
        {"part": "Spark Plugs", "stock": 4, "status": "unverified", "date": "2023-09-20"}, # Should ignore (wrong date/status)
        {"part": "Transmission Fluid", "stock": 2, "status": "verified", "date": "2023-10-12"},
        {"part": "Battery", "stock": 5, "status": "verified", "date": "2023-10-14"}
    ]

    for p in parts_truth:
        node = random.choice(all_nodes)
        # Naming parts files with confusing prefixes
        fname = f"data_blob_{random.randint(1000,9999)}.csv"
        with open(os.path.join(node, fname), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["part_name", "current_stock", "status", "last_updated"])
            writer.writerow([p["part"], p["stock"], p["status"], p["date"]])

if __name__ == "__main__":
    build_env()
