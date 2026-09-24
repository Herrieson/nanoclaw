import os
import json
import random
import csv

def build_env():
    # Base directory
    base_dir = "dump_site_delta"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Create a Fragmented Machine Catalog
    # We'll split the catalog into 3 types of fragments: 
    # - info_{id}.json (ID and Name)
    # - specs_{id}.json (Load and RPM)
    # - price_{id}.json (Price)
    catalog_path = os.path.join(base_dir, "catalog_fragments")
    os.makedirs(catalog_path, exist_ok=True)
    
    machines = [
        {"id": "M-101", "name": "Titan-X", "load": 5000, "rpm": 12000, "price": 150000},
        {"id": "M-102", "name": "Atlas-Pro", "load": 8000, "rpm": 8000, "price": 220000},
        {"id": "M-103", "name": "Hermes-Lite", "load": 2000, "rpm": 20000, "price": 85000},
        {"id": "M-104", "name": "Vulcan-Heavy", "load": 12000, "rpm": 5000, "price": 350000},
        {"id": "M-105", "name": "Zeus-Omni", "load": 15000, "rpm": 25000, "price": 800000},
        {"id": "M-106", "name": "Entry-Level-Trash", "load": 500, "rpm": 1000, "price": 10000}
    ]
    
    # Generate 500 decoy fragment files to hide the real ones
    for i in range(500):
        dummy_id = f"D-{i:03d}"
        with open(os.path.join(catalog_path, f"info_{dummy_id}.json"), "w") as f:
            json.dump({"id": dummy_id, "name": f"Ghost-Unit-{i}"}, f)

    # Write real data
    for m in machines:
        with open(os.path.join(catalog_path, f"info_{m['id']}.json"), "w") as f:
            json.dump({"id": m['id'], "name": m['name']}, f)
        with open(os.path.join(catalog_path, f"specs_{m['id']}.json"), "w") as f:
            json.dump({"load_cap": m['load'], "max_rpm": m['rpm']}, f)
        with open(os.path.join(catalog_path, f"price_{m['id']}.json"), "w") as f:
            json.dump({"cost": m['price']}, f)

    # 2. Create Fragmented and Noisy Client Data
    # Path: dump_site_delta/archives/year_2023/recovered/
    client_path = os.path.join(base_dir, "archives/year_2023/recovered")
    os.makedirs(client_path, exist_ok=True)
    
    # Client A: Stark (Needs 6000kg, 7000 RPM) -> Cheapest: Atlas-Pro (220,000)
    with open(os.path.join(client_path, "session_882.log"), "w") as f:
        f.write("TIMESTAMP 2023-11-01: Incoming transmission from Stark Ind.\n")
        f.write("... interference ...\n")
        f.write("REQUEST_DETAIL: Need minimum load 6000 kg. Spindle must exceed 7000 RPM.\n")
        f.write("Priority: High. Budget: Flexible but don't overcharge.\n")

    # Client B: Wayne (Needs 1500kg, 15000 RPM) -> Cheapest: Hermes-Lite (85,000)
    # This one is hidden in a pseudo-csv log
    with open(os.path.join(client_path, "comm_logs.tmp"), "w") as f:
        f.write("sender,message,meta\n")
        f.write("B.Wayne,Our R&D requires 15000 RPM min speed.,urgent\n")
        f.write("B.Wayne,Also ensure it handles 1500 kg minimum load.,urgent\n")
        for _ in range(100):
            f.write(f"Unknown,System noise {random.random()},low\n")

    # Client C: Acme (Needs 10000kg, 4000 RPM) -> Cheapest: Vulcan-Heavy (350,000)
    # This one is in a deeply nested directory
    acme_path = os.path.join(client_path, "sub_delta_09/trash")
    os.makedirs(acme_path, exist_ok=True)
    with open(os.path.join(acme_path, "memo_final.txt"), "w") as f:
        f.write("Acme Corp demands: Load capacity >= 10000kg. RPM >= 4000. Give us the cheapest option.\n")

    # 3. Add mass noise
    for i in range(10):
        noise_dir = os.path.join(base_dir, f"system_logs_{i}")
        os.makedirs(noise_dir, exist_ok=True)
        for j in range(20):
            with open(os.path.join(noise_dir, f"err_{j}.log"), "w") as f:
                f.write("ERROR: System unstable. Data packet lost.\n" * 100)

if __name__ == "__main__":
    build_env()
