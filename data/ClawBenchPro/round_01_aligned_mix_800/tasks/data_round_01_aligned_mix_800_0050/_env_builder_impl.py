import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("orders", exist_ok=True)
    os.makedirs("warehouse", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("inbox", exist_ok=True)

    # Batch 1 tickets
    batch_1 = [
        {"ticket_id": "T-101", "machine_id": "M-A1", "material": "Steel", "est_hours": 10, "req_welding": "MIG"},
        {"ticket_id": "T-102", "machine_id": "M-A2", "material": "Aluminum", "est_hours": 8, "req_welding": "MIG"},
        # Trap: T-103 requests MIG, but Titanium REQUIRES TIG (multiplier 1.8). 
        # Base: $90. Labor: 15 * 90 * 1.8 = $2430. 
        # Part: Titanium_Alloy from Apex ($1900). Total: $4330. Budget is $4500. So it fits!
        {"ticket_id": "T-103", "machine_id": "M-A3", "material": "Titanium", "est_hours": 15, "req_welding": "MIG"},
        {"ticket_id": "T-104", "machine_id": "M-A4", "material": "Copper", "est_hours": 20, "req_welding": "TIG"} # Fails budget
    ]
    with open("orders/batch_1.json", "w") as f:
        json.dump(batch_1, f, indent=4)

    # Inventory
    inventory = [
        {"PartName": "Steel_Pipe", "Price": "150", "Qty": "10"},
        {"PartName": "Aluminum_Sheet", "Price": "300", "Qty": "5"},
        {"PartName": "Titanium_Alloy", "Price": "1800", "Qty": "0"},
        {"PartName": "Copper_Wire", "Price": "800", "Qty": "0"}
    ]
    with open("warehouse/inventory.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["PartName", "Price", "Qty"])
        writer.writeheader()
        writer.writerows(inventory)

    # Suppliers
    suppliers = {
        "Apex Metals": {"Titanium_Alloy": 1900, "Copper_Wire": 900},
        "BetaCorp": {"Titanium_Alloy": 2200, "Copper_Wire": 850},
        "Gamma Forge": {"Titanium_Alloy": 2600, "Copper_Wire": 1200}
    }
    with open("warehouse/suppliers.json", "w") as f:
        json.dump(suppliers, f, indent=4)

    # Materials Matrix
    matrix_content = """Jared's Custom Shop - Materials Matrix
========================================
MATERIAL      REQUIRED_WELDING
Steel         MIG
Aluminum      TIG
Titanium      TIG
Copper        TIG

WELDING MULTIPLIERS:
MIG: 1.2
TIG: 1.8
STICK: 1.0
"""
    with open("docs/materials_matrix.txt", "w") as f:
        f.write(matrix_content)

def build_turn_2():
    # Turn 2 new batch
    batch_2 = [
        {"ticket_id": "T-201", "machine_id": "M-B1", "material": "Steel", "est_hours": 5, "req_welding": "MIG"},
        {"ticket_id": "T-202", "machine_id": "M-B2", "material": "Titanium", "est_hours": 10, "req_welding": "TIG"}
    ]
    with open("orders/batch_2.json", "w") as f:
        json.dump(batch_2, f, indent=4)

    # Recall Notice
    # This will recall Apex Metals' Titanium_Alloy.
    # T-103 must now use BetaCorp's Titanium_Alloy ($2200).
    # New Labor ($2430) + BetaCorp ($2200) = $4630. Budget ($4500) EXCEEDED! T-103 must be rejected now.
    recall_content = """URGENT RECALL NOTICE
Issued by: National Industrial Safety Board
Subject: Apex Metals Part Defect

All "Titanium_Alloy" components sourced from supplier "Apex Metals" have been recalled due to micro-fissures. 
Immediate cessation of use is mandatory. Do not use this supplier for this part under any circumstances.
"""
    with open("inbox/recall.txt", "w") as f:
        f.write(recall_content)

def build_turn_3():
    # Safety Bulletin
    bulletin = """OSHA REGIONAL BULLETIN #994-A
Safety guidelines for high-pressure and combustible environment machinery:

1. No TIG welding may be performed on machinery that contains a "High-Pressure Hydraulic Valve".
2. MIG welding is strictly prohibited on machines manufactured before 2010.
3. Any machine with a "Class 3 Combustible Enclosure" requires a mandatory external vent filter if worked on for more than 6 hours.
"""
    with open("docs/safety_bulletin.txt", "w") as f:
        f.write(bulletin)

    # Machine Specs
    specs = {
        "M-A1": {"manufacture_year": 2015, "features": ["Standard Valve", "Safety Guard"]},
        "M-A2": {"manufacture_year": 2018, "features": ["High-Pressure Hydraulic Valve", "Cooling Fan"]}, # T-102 uses Aluminum -> TIG. TIG + High Pressure = VIOLATION!
        "M-A3": {"manufacture_year": 2020, "features": ["Standard Valve"]},
        "M-B1": {"manufacture_year": 2008, "features": ["Basic Enclosure"]}, # T-201 uses Steel -> MIG. MIG + pre-2010 = VIOLATION!
        "M-B2": {"manufacture_year": 2021, "features": ["High-Pressure Hydraulic Valve"]}
    }
    with open("docs/machine_specs.json", "w") as f:
        json.dump(specs, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
