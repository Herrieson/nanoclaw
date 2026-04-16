import os
import json
import csv

def build_env():
    base_dir = "assets/data_472"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Master parts list
    master_parts = [f"P{str(i).zfill(3)}" for i in range(1, 21)]
    with open(os.path.join(base_dir, "master_plans.txt"), "w") as f:
        f.write("F-14 Tomcat 1/48 Scale - Master Parts List\n")
        f.write("=========================================\n")
        for part in master_parts:
            f.write(f"- {part}\n")

    # 2. Inventory - Box A (CSV)
    os.makedirs(os.path.join(base_dir, "inventory"), exist_ok=True)
    with open(os.path.join(base_dir, "inventory", "box_A.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["PartID", "Condition", "Location"])
        writer.writerow(["P001", "Good", "Box A"])
        writer.writerow(["P003", "Mint", "Box A"])
        writer.writerow(["P005", "Fair", "Box A"])
        writer.writerow(["P007", "Good", "Box A"])

    # 3. Inventory - Box B (JSON-like text)
    with open(os.path.join(base_dir, "inventory", "box_B.txt"), "w") as f:
        f.write("Stuff in Box B:\n")
        f.write("* Part ID: P010 (looks okay)\n")
        f.write("* Part ID: P015 (still on sprue)\n")

    # 4. Inventory - Desk Drawer (Plain text list)
    with open(os.path.join(base_dir, "inventory", "desk_drawer.log"), "w") as f:
        f.write("P018\nP019\n")

    # Owned: P001, P003, P005, P007, P010, P015, P018, P019
    # Missing: P002, P004, P006, P008, P009, P011, P012, P013, P014, P016, P017, P020

    # 5. Vendor Catalog (JSON)
    catalog = {
        "P001": {"name": "Nose Cone", "price": 4.50},
        "P002": {"name": "Cockpit Tub", "price": 1.50},
        "P003": {"name": "Ejection Seat A", "price": 2.00},
        "P004": {"name": "Ejection Seat B", "price": 2.00},
        "P005": {"name": "Canopy", "price": 3.00},
        "P006": {"name": "Fuselage Top", "price": 0.75},
        "P007": {"name": "Fuselage Bottom", "price": 7.00},
        "P008": {"name": "Left Wing", "price": 3.25},
        "P009": {"name": "Right Wing", "price": 1.00},
        "P010": {"name": "Left Tail", "price": 1.50},
        "P011": {"name": "Right Tail", "price": 4.50},
        "P012": {"name": "Engine Intake L", "price": 2.50},
        "P013": {"name": "Engine Intake R", "price": 1.25},
        "P014": {"name": "Landing Gear Front", "price": 5.00},
        "P015": {"name": "Landing Gear Rear L", "price": 2.50},
        "P016": {"name": "Landing Gear Rear R", "price": 0.50},
        "P017": {"name": "Missile Set A", "price": 2.75},
        "P018": {"name": "Missile Set B", "price": 2.75},
        "P019": {"name": "Decal Sheet", "price": 5.50},
        "P020": {"name": "Display Stand", "price": 8.99}
    }
    
    os.makedirs(os.path.join(base_dir, "vendor"), exist_ok=True)
    with open(os.path.join(base_dir, "vendor", "catalog.json"), "w") as f:
        json.dump(catalog, f, indent=4)

if __name__ == "__main__":
    build_env()
