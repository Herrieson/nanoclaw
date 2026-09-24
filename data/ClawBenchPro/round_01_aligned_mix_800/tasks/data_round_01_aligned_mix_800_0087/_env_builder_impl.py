import os
import argparse
import csv
import json

def build_turn_1():
    os.makedirs("vendors", exist_ok=True)
    os.makedirs("financials", exist_ok=True)

    food_vendors = [
        {"vendor_id": "F01", "name": "GreenBites", "sugar_pct": 4.0, "carbon_footprint": 2.0},  # Pass
        {"vendor_id": "F02", "name": "SugarRush Inc", "sugar_pct": 6.0, "carbon_footprint": 1.0}, # Fail T1 (Sugar), Trap for T2
        {"vendor_id": "F03", "name": "HeavyEats", "sugar_pct": 3.0, "carbon_footprint": 3.0},   # Fail T1 (Carbon)
        {"vendor_id": "F04", "name": "BalancedDiet", "sugar_pct": 2.0, "carbon_footprint": 2.1},  # Pass
        {"vendor_id": "F05", "name": "LuxFoods", "sugar_pct": 4.5, "carbon_footprint": 1.5},    # Fail T1 (Bid > 50k)
        {"vendor_id": "F06", "name": "LeanPrep", "sugar_pct": 1.0, "carbon_footprint": 1.0},    # Pass
        {"vendor_id": "F07", "name": "EcoSnack", "sugar_pct": 2.0, "carbon_footprint": 1.5},    # Pass
    ]

    with open("vendors/food.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["vendor_id", "name", "sugar_pct", "carbon_footprint"])
        writer.writeheader()
        writer.writerows(food_vendors)

    fitness_vendors = [
        {"vendor_id": "G01", "name": "IronWorks Local", "equipment_source": "Local", "ghg_emissions": 15.0}, # Pass T1 (Local)
        {"vendor_id": "G02", "name": "GlobalFit", "equipment_source": "Imported", "ghg_emissions": 8.0},    # Pass T1 (GHG < 10)
        {"vendor_id": "G03", "name": "CheapLift", "equipment_source": "Imported", "ghg_emissions": 12.0},   # Fail T1, Trap for T2
        {"vendor_id": "G04", "name": "CaliGym", "equipment_source": "Local", "ghg_emissions": 5.0},         # Pass T1
        {"vendor_id": "G05", "name": "TitanImports", "equipment_source": "Imported", "ghg_emissions": 9.0}, # Fail T1 (Bid > 50k)
        {"vendor_id": "G06", "name": "StateAthletics", "equipment_source": "Local", "ghg_emissions": 6.0},  # Pass T1
    ]

    with open("vendors/fitness.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["vendor_id", "name", "equipment_source", "ghg_emissions"])
        writer.writeheader()
        writer.writerows(fitness_vendors)

    bids = {
        "F01": 45000,
        "F02": 25000, # Cheap trap
        "F03": 40000,
        "F04": 48000,
        "F05": 52000,
        "F06": 35000,
        "F07": 40000,
        "G01": 40000,
        "G02": 49000,
        "G03": 20000, # Cheap trap
        "G04": 42000,
        "G05": 60000,
        "G06": 45000
    }

    with open("financials/bids.json", "w") as f:
        json.dump(bids, f, indent=4)

def build_turn_2():
    os.makedirs("hr_data", exist_ok=True)
    os.makedirs("facilities", exist_ok=True)

    labor_audits = {
        "F01": {"equity_score": 85, "labor_violations": 0},
        "F02": {"equity_score": 99, "labor_violations": 0}, # Trap: Perfect union score, but failed T1
        "F03": {"equity_score": 80, "labor_violations": 0},
        "F04": {"equity_score": 75, "labor_violations": 0}, # Fails T2 (Equity < 80)
        "F05": {"equity_score": 90, "labor_violations": 0},
        "F06": {"equity_score": 91, "labor_violations": 0},
        "F07": {"equity_score": 80, "labor_violations": 0},
        "G01": {"equity_score": 82, "labor_violations": 1}, # Fails T2 (Violation)
        "G02": {"equity_score": 88, "labor_violations": 0},
        "G03": {"equity_score": 98, "labor_violations": 0}, # Trap: Perfect union score, but failed T1
        "G04": {"equity_score": 95, "labor_violations": 0},
        "G05": {"equity_score": 85, "labor_violations": 0},
        "G06": {"equity_score": 81, "labor_violations": 0}
    }

    with open("hr_data/labor_audits.json", "w") as f:
        json.dump(labor_audits, f, indent=4)

    campus_zones = {
        "North Campus": {"max_budget": 78000},
        "South Campus": {"max_budget": 72000}
    }

    with open("facilities/campus_zones.json", "w") as f:
        json.dump(campus_zones, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
