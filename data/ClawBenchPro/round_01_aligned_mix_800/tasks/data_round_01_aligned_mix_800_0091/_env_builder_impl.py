import os
import json
import csv
import argparse

def build_turn_1():
    os.makedirs("blueprints", exist_ok=True)
    os.makedirs("catalog", exist_ok=True)
    
    # 1. Structural Limits
    limits = {
        "max_weight_lbs": 16000,
        "max_power_kw": 1200,
        "budget_usd": 85000
    }
    with open("blueprints/structural_limits.json", "w") as f:
        json.dump(limits, f, indent=4)
        
    # 2. HVAC Catalog
    # Trap Design:
    # Turn 1 Best (Cheap, Light): C-01 + A-01. (Fails Turn 2 rules)
    # Turn 2 Best (Compliant, exactly hits weight limit): C-02 + A-02. (Fails Turn 3 maintenance overlap on Q1)
    # Turn 3 Best (Compliant, distinct quarters, fits weight): C-02 + A-03.
    hvac_data = [
        ["ID", "Type", "Weight", "Power", "Cost", "Eco_Rating", "Supplier_Region"],
        ["C-01", "Chiller", 4000, 300, 15000, "C", 100],   # Cheap, bad eco
        ["C-02", "Chiller", 5000, 400, 25000, "A", 200],   # Good eco, heavier. Turn 2 choice.
        ["C-03", "Chiller", 6000, 350, 22000, "B", 150],   # Too heavy if paired with A-02
        ["A-01", "AirHandler", 2000, 200, 10000, "B", 400],# Good eco, bad region (>300)
        ["A-02", "AirHandler", 3000, 250, 15000, "A", 150],# Turn 2 choice. Matches weight limit exactly with C-02 (8000).
        ["A-03", "AirHandler", 2500, 300, 18000, "B", 200],# Turn 3 fix.
        ["H-01", "HeatPump", 3000, 250, 12000, "A", 100],  # Constant baseline
        ["H-02", "HeatPump", 3500, 200, 14000, "C", 100]
    ]
    with open("catalog/hvac_components.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(hvac_data)
        
    # 3. Structural Catalog
    struct_data = [
        ["ID", "Type", "Weight", "Power", "Cost", "Eco_Rating", "Supplier_Region"],
        ["B-01", "Beam", 3000, 0, 8000, "A", 100],  # Constant baseline
        ["P-01", "Panel", 2000, 0, 5000, "A", 100], # Constant baseline
        ["P-02", "Panel", 2500, 0, 4000, "C", 500]
    ]
    with open("catalog/structural_components.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(struct_data)

def build_turn_2():
    os.makedirs("compliance", exist_ok=True)
    mandate_text = (
        "MANDATE 2024-B:\n"
        "Effective immediately, all city engineering projects must adhere to strict environmental standards.\n"
        "1. All system components must carry an Eco_Rating of 'A' or 'B'. Any rating of 'C' or below is strictly prohibited.\n"
        "2. To support local supply chains, all components must be sourced from Supplier_Region codes strictly less than 300. "
        "Any region code 300 or higher is banned from deployment.\n"
    )
    with open("compliance/mandate_2024B.txt", "w") as f:
        f.write(mandate_text)

def build_turn_3():
    os.makedirs("operations", exist_ok=True)
    # Turn 2 combo was likely C-02 + A-02. Both are Q1 -> Conflict!
    # Turn 3 forced swap: C-02 (Q1) + A-03 (Q3). Valid.
    schedules = {
        "C-01": "Q1",
        "C-02": "Q1",
        "C-03": "Q2",
        "A-01": "Q3",
        "A-02": "Q1",
        "A-03": "Q3",
        "H-01": "Q2",
        "H-02": "Q4",
        "B-01": "Q4",
        "P-01": "Q3",
        "P-02": "Q2"
    }
    with open("operations/maintenance_schedule.json", "w") as f:
        json.dump(schedules, f, indent=4)

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
