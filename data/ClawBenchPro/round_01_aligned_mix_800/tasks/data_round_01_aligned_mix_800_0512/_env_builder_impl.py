import os
import json
import csv
import random
from datetime import datetime, timedelta

def build_env():
    # Base directory
    base_dir = "work_files"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Fragmented Stock Data (Fragmentation + Scale)
    # Create multiple nested directories with fake stock data
    for i in range(15):
        sub_dir = f"sync_vault_{i:02d}"
        os.makedirs(os.path.join(base_dir, sub_dir), exist_ok=True)
        
        # Add noise files
        with open(os.path.join(base_dir, sub_dir, f"stock_backup_{i}.csv"), "w") as f:
            f.write("Part_ID,Quantity\nEV-101,99999\nEV-999,0") # Misleading old data

    # The REAL stock file (Clue: Highest timestamp in filename)
    real_stock_dir = "sync_vault_07"
    real_stock_filename = "MASTER_STOCK_v2_20231027_FINAL.csv"
    with open(os.path.join(base_dir, real_stock_dir, real_stock_filename), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Part_ID", "Part_Name", "Quantity_On_Hand", "Last_Audit"])
        writer.writerow(["EV-101", "Lithium Cell Pack", "3200", "2023-10-27"])
        writer.writerow(["EV-102", "Stator Coil", "1200", "2023-10-27"])
        writer.writerow(["EV-103", "Rotor Assembly", "150", "2023-10-27"])
        writer.writerow(["EV-104", "Cooling Pump", "45", "2023-10-27"])

    # 2. Multi-hop Requirements (Logic + Fragmentation)
    # Requirements are split across multiple "Production Shift" JSONs
    req_dir = os.path.join(base_dir, "production_pipeline/active_manifests")
    os.makedirs(req_dir, exist_ok=True)
    
    # Shift 1
    with open(os.path.join(req_dir, "shift_alpha_req.json"), "w") as f:
        json.dump({"target_units": 100, "parts_per_unit": {"EV-101": 20, "EV-102": 5, "EV-103": 1}}, f)
    
    # Shift 2 (Deeply nested)
    deep_req_dir = os.path.join(req_dir, "recovery/night_shift")
    os.makedirs(deep_req_dir, exist_ok=True)
    with open(os.path.join(deep_req_dir, "manifest_delta.json"), "w") as f:
        # This one is structured differently
        json.dump([
            {"id": "EV-101", "req": 1500},
            {"id": "EV-102", "req": 800},
            {"id": "EV-104", "req": 60}
        ], f)

    # 3. Messy Carrier Data (Noise & Decoys)
    carrier_dir = os.path.join(base_dir, "logistics/vendors")
    os.makedirs(carrier_dir, exist_ok=True)
    
    # Decoy: Negotiation drafts
    with open(os.path.join(carrier_dir, "negotiation_notes.txt"), "w") as f:
        f.write("Carrier X says they can do $2.00/lb for Same-Day but they are currently SUSPENDED.\n")
        f.write("Carrier Y is cheap ($1.50) but only does Standard.\n")

    # The Registry (Semi-structured)
    registry_path = os.path.join(carrier_dir, "global_registry.log")
    with open(registry_path, "w") as f:
        # Mix of valid and invalid formats
        f.write("[INFO] Initializing vendor registry...\n")
        f.write("ENTRY|ID:771|NAME:Flash-Logistics|TYPE:Same-Day|RATE:5.20|STATUS:ACTIVE\n")
        f.write("ENTRY|ID:882|NAME:Slow-Mo-Freight|TYPE:Standard|RATE:1.10|STATUS:ACTIVE\n")
        f.write("ENTRY|ID:993|NAME:Hyper-Direct|TYPE:Same-Day|RATE:4.85|STATUS:ACTIVE\n")
        f.write("ENTRY|ID:104|NAME:Red-Line-Express|TYPE:Same-Day|RATE:3.95|STATUS:SUSPENDED\n")
        f.write("ENTRY|ID:555|NAME:Titan-Relay|TYPE:Same-Day|RATE:6.00|STATUS:ACTIVE\n")
        f.write("[WARN] Carrier 104 flagged for safety violations.\n")

    # 4. Pure Junk (Scale Simulation)
    junk_dir = os.path.join(base_dir, "temp_trash")
    os.makedirs(junk_dir, exist_ok=True)
    for i in range(100):
        with open(os.path.join(junk_dir, f"error_log_{i}.tmp"), "w") as f:
            f.write("".join([random.choice("abcdefg\n") for _ in range(100)]))

if __name__ == "__main__":
    build_env()
