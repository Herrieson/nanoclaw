import os
import json
import csv
import random

def setup_environment():
    base_path = "assets/data_48"
    os.makedirs(base_path, exist_ok=True)
    
    # Create a messy directory structure to reflect Low Conscientiousness
    folders = [
        "Downloads", "Documents/Work/Welding", "Desktop/STUFF", 
        "Desktop/New_Folder_2", "Documents/Truck_Project/Old_Manuals",
        ".hidden_configs/temp_backups"
    ]
    for folder in folders:
        os.makedirs(os.path.join(base_path, folder), exist_ok=True)

    # 1. The Diagnostic Log (Hidden and obfuscated)
    # The hex code '0x1A4' represents a 'Mass Air Flow (MAF) Sensor Circuit Intermittent' 
    # in this fictional scenario.
    log_content = [
        "2023-10-27 08:12:01 - System Init",
        "2023-10-27 08:12:05 - CAN Bus Online",
        "2023-10-27 08:12:06 - ERROR: PID 0x1A4 - Voltage Out of Range (0.2V)",
        "2023-10-27 08:12:07 - Warning: Fuel Trim Bank 1 High",
        "2023-10-27 08:12:10 - Critical: Engine Stalled"
    ]
    # Put it in a weird place with a typo
    with open(os.path.join(base_path, ".hidden_configs/temp_backups/scan_reslt_FINAL_final.log"), "w") as f:
        f.write("\n".join(log_content))

    # 2. Part Compatibility Database (JSON)
    # The persona would likely have downloaded a dump of parts
    parts_db = [
        {"part_name": "Oxygen Sensor", "error_code": "0x2B1", "id": "OX-99"},
        {"part_name": "Mass Air Flow Sensor", "error_code": "0x1A4", "id": "MAF-500-X"},
        {"part_name": "Throttle Position Sensor", "error_code": "0x3C2", "id": "TPS-12"},
        {"part_name": "Crankshaft Position Sensor", "error_code": "0x0A1", "id": "CPS-77"}
    ]
    with open(os.path.join(base_path, "Documents/Truck_Project/Old_Manuals/comptbl_parts_ref.json"), "w") as f:
        json.dump(parts_db, f)

    # 3. Local Inventory (CSV)
    # He has some parts, but NOT the MAF-500-X
    inventory = [
        ["part_id", "condition", "bin_location"],
        ["OX-99", "Used", "Shelf A"],
        ["TPS-12", "New", "Shelf B"],
        ["CPS-77", "Used", "Floor Box"]
    ]
    with open(os.path.join(base_path, "Desktop/STUFF/garage_inventory.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerows(inventory)

    # 4. Mock Order Script (The "Local Network Service")
    # We'll create a script that simulates the endpoint
    order_script = """
import sys
import json

if len(sys.argv) < 2:
    print("Usage: python order_tool.py --part_id ID")
    sys.exit(1)

part_id = sys.argv[2]
# Simulate a successful order
with open("order_receipt.json", "w") as f:
    json.dump({"status": "ordered", "part_id": part_id, "pickup_time": "30 mins"}, f)
print(f"Order for {part_id} placed successfully.")
"""
    with open(os.path.join(base_path, "order_tool.py"), "w") as f:
        f.write(order_script)

if __name__ == "__main__":
    setup_environment()
