import os
import argparse
import json
import csv
import shutil

def build_turn_1():
    os.makedirs("data/applications", exist_ok=True)
    os.makedirs("data/contractors", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # 1. Properties
    # Prop 1: Rent 1200 -> Ann: 14400. 2.5x = 36000.
    # Prop 2: Rent 1000 -> Ann: 12000. 2.5x = 30000.
    # Prop 3: Rent 1800 -> Ann: 21600. 2.5x = 54000. 
    # Prop 4: Rent 800  -> Ann: 9600.  2.5x = 24000.
    properties = [
        {"id": "P101", "address": "12A Baker St", "rent": 1200, "repair_needed": "Roofing"},
        {"id": "P102", "address": "14B Baker St", "rent": 1000, "repair_needed": "Plumbing"},
        {"id": "P103", "address": "88 Elm St", "rent": 1800, "repair_needed": "HVAC"},
        {"id": "P104", "address": "90 Elm St", "rent": 800, "repair_needed": "Electrical"}
    ]
    with open("data/properties.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "address", "rent", "repair_needed"])
        writer.writeheader()
        writer.writerows(properties)

    # 2. Tenants (Traps included)
    # T1: Veteran, Income 33k. Prop 1: 1200*0.9=1080 -> Ann 12960 -> 2.5x = 32400. PASS. (If no discount, 36000, fails).
    # T2: Income 62k. Fails cap. (Trap: perfect for P103 otherwise).
    # T3: Income 45k. Felony, Violent. Fails.
    # T4: Income 42k. Felony, non-violent. P102 -> 1000 -> 2.5x = 30000. PASS.
    # T5: Income 28k. P104 -> 800 -> 24000. PASS.
    # T6: Income 58k. P103 -> 1800 -> 54000. PASS.
    apps = [
        {"id": "T1", "name": "John Doe", "income": 33000, "is_veteran": True, "background": "Clear"},
        {"id": "T2", "name": "Jane Smith", "income": 62000, "is_veteran": False, "background": "Clear"},
        {"id": "T3", "name": "Mark Ruff", "income": 45000, "is_veteran": False, "background": "Felony - Armed Robbery (Violent)"},
        {"id": "T4", "name": "Lucy Heart", "income": 42000, "is_veteran": False, "background": "Felony - Tax Fraud (non-violent)"},
        {"id": "T5", "name": "Sam Hill", "income": 28000, "is_veteran": False, "background": "Clear"},
        {"id": "T6", "name": "Alan Wake", "income": 58000, "is_veteran": False, "background": "Clear"}
    ]
    for app in apps:
        with open(f"data/applications/{app['id']}.json", "w") as f:
            json.dump(app, f, indent=2)

    # 3. Contractors
    # P101 Roofing: C1 ($3500, Lic), C2 ($3200, Unlic) -> Win: C1
    # P102 Plumbing: C3 ($4200, Lic), C4 ($4800, Lic) -> Win: C3 (Needs Board Approval flag > 4000)
    # P103 HVAC: C5 ($2900, Lic), C6 ($2500, Lic) -> Win: C6
    # P104 Electrical: C7 ($1500, Lic), C8 ($1600, Lic) -> Win: C7
    # Total initial cost = 3500 + 4200 + 2500 + 1500 = 11700.
    bids = [
        {"prop_id": "P101", "contractor_id": "C1", "name": "Roof Masters", "licensed": "Yes", "bid": 3500},
        {"prop_id": "P101", "contractor_id": "C2", "name": "Cheap Roofs", "licensed": "No", "bid": 3200},
        {"prop_id": "P102", "contractor_id": "C3", "name": "Plumb Perfect", "licensed": "Yes", "bid": 4200},
        {"prop_id": "P102", "contractor_id": "C4", "name": "Mario Bros", "licensed": "Yes", "bid": 4800},
        {"prop_id": "P103", "contractor_id": "C5", "name": "Ice Cold HVAC", "licensed": "Yes", "bid": 2900},
        {"prop_id": "P103", "contractor_id": "C6", "name": "Breezy Co", "licensed": "Yes", "bid": 2500},
        {"prop_id": "P104", "contractor_id": "C7", "name": "Sparky", "licensed": "Yes", "bid": 1500},
        {"prop_id": "P104", "contractor_id": "C8", "name": "Shock Value", "licensed": "Yes", "bid": 1600}
    ]
    with open("data/contractors/bids.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["prop_id", "contractor_id", "name", "licensed", "bid"])
        writer.writeheader()
        writer.writerows(bids)

def build_turn_2():
    os.makedirs("data/compliance", exist_ok=True)
    
    # 1. Registry
    # C1 (Roof Masters) gets revoked! C3 (Plumb Perfect) gets suspended!
    registry = [
        {"contractor_id": "C1", "status": "Revoked"},
        {"contractor_id": "C3", "status": "Suspended"},
        {"contractor_id": "C4", "status": "Active"},
        {"contractor_id": "C5", "status": "Active"},
        {"contractor_id": "C6", "status": "Active"},
        {"contractor_id": "C7", "status": "Active"}
    ]
    with open("data/compliance/registry.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["contractor_id", "status"])
        writer.writeheader()
        writer.writerows(registry)

    # 2. Late Bids
    # Need new bids for P101 since C1 is out and C2 is unlicensed.
    # Need to replace C3 for P102. C4 is 4800.
    # Total budget was 11700. 15% cut -> 9945.
    # Wait, if budget is 9945, C6(2500) + C7(1500) = 4000. Leaves 5945 for P101 and P102.
    # If P102 uses C4 (4800), leaves 1145 for P101, which is impossible.
    # So provide new cheaper bids in late_bids to make it solvable under 9945.
    late_bids = [
        {"prop_id": "P101", "contractor_id": "C9", "name": "Late Roofs", "licensed": "Yes", "bid": 2100},
        {"prop_id": "P102", "contractor_id": "C10", "name": "Quick Plumb", "licensed": "Yes", "bid": 3800}
    ]
    # Check: 2500 + 1500 + 2100 + 3800 = 9900 <= 9945. PASS.
    with open("data/contractors/late_bids.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["prop_id", "contractor_id", "name", "licensed", "bid"])
        writer.writeheader()
        writer.writerows(late_bids)

def build_turn_3():
    os.makedirs("data/appeals", exist_ok=True)
    
    # T2 (Jane Smith) Income 62k. Fails cap originally. Appeal: special_medical_need = True. Background: Clear. PASS.
    # T3 (Mark Ruff) Income 45k. Appeal: special_medical_need = True. Background: Violent. FAILS.
    # T7 (New guy) Income 65k. Appeal: special_medical_need = False. Background: Clear. FAILS.
    
    apps = [
        {"id": "T2", "name": "Jane Smith", "income": 62000, "is_veteran": False, "background": "Clear", "special_medical_need": True},
        {"id": "T3", "name": "Mark Ruff", "income": 45000, "is_veteran": False, "background": "Felony - Armed Robbery (Violent)", "special_medical_need": True},
        {"id": "T7", "name": "Bruce Banner", "income": 65000, "is_veteran": False, "background": "Clear", "special_medical_need": False}
    ]
    
    for app in apps:
        with open(f"data/appeals/{app['id']}_appeal.json", "w") as f:
            json.dump(app, f, indent=2)

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
