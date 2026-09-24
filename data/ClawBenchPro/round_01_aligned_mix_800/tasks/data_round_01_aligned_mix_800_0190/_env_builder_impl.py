import os
import argparse
import json
import csv

def build_turn_1():
    # Directories
    os.makedirs("inventory", exist_ok=True)
    os.makedirs("manuals", exist_ok=True)
    os.makedirs("orders", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # 1. Initial Inventory
    inventory = {
        "Pyrethrin": 500.0,   # Toxic, cheap
        "Bifenthrin": 400.0,  # Safe for pets/kids
        "Fipronil": 200.0     # Termite only
    }
    with open("inventory/truck_stock.json", "w") as f:
        json.dump(inventory, f, indent=4)

    # 2. Chemical Rules
    rules = {
        "Pyrethrin": {"usage_multiplier": 0.05, "target": ["Roach", "Ant", "Bedbug"]},
        "Bifenthrin": {"usage_multiplier": 0.08, "target": ["Roach", "Ant", "Bedbug", "Spider"]},
        "Fipronil": {"usage_multiplier": 0.12, "target": ["Termite"]}
    }
    with open("manuals/chemicals_rules.json", "w") as f:
        json.dump(rules, f, indent=4)

    # 3. Restrictions
    restrictions = """STRICT PROTOCOLS - READ CAREFULLY!
1. If the household has Pets (Yes) OR Children (Yes), you MUST NEVER use Pyrethrin. Use Bifenthrin instead.
2. Fipronil is strictly reserved for Termite infestations. Do not use for anything else.
3. If multiple chemicals are valid, ALWAYS prioritize Pyrethrin if allowed, because it's cheaper.
Note: Usage calculation is (House Area in sqft * usage_multiplier) in ounces.
"""
    with open("manuals/restrictions.txt", "w") as f:
        f.write(restrictions)

    # 4. Orders (Mix of Monday and Tuesday, complex data)
    orders = [
        {"order_id": "O-101", "day": "Monday", "area_sqft": 1500, "pest": "Roach", "pets": "No", "children": "No"},
        {"order_id": "O-102", "day": "Monday", "area_sqft": 2500, "pest": "Termite", "pets": "Yes", "children": "No"},
        {"order_id": "O-103", "day": "Monday", "area_sqft": 1800, "pest": "Ant", "pets": "Yes", "children": "Yes"},
        {"order_id": "O-104", "day": "Monday", "area_sqft": 3000, "pest": "Roach", "pets": "No", "children": "No"}, # Trap: 3000 sqft uses 150oz Pyrethrin. Will be affected by Turn 2 law if it was Tuesday.
        {"order_id": "O-201", "day": "Tuesday", "area_sqft": 2200, "pest": "Bedbug", "pets": "No", "children": "No"}, # Turn 2 trap
        {"order_id": "O-202", "day": "Tuesday", "area_sqft": 1200, "pest": "Ant", "pets": "No", "children": "Yes"},
        {"order_id": "O-203", "day": "Tuesday", "area_sqft": 1900, "pest": "Roach", "pets": "No", "children": "No"}
    ]
    with open("orders/this_week_orders.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "day", "area_sqft", "pest", "pets", "children"])
        writer.writeheader()
        writer.writerows(orders)

def build_turn_2():
    os.makedirs("hq_memos", exist_ok=True)
    
    # 1. New Law
    memo = """URGENT HQ MEMO - EPA REGULATION UPDATE
Effective IMMEDIATELY (This Tuesday):
Due to new groundwater protection laws, the use of Pyrethrin is strictly PROHIBITED in any property with an area strictly greater than 2000 sqft. 
If an order requires treatment for such a property and Pyrethrin was planned, you MUST switch to an alternative chemical regardless of pet/child status.
"""
    with open("hq_memos/new_environmental_law.txt", "w") as f:
        f.write(memo)

    # 2. Urgent Tuesday Orders
    urgent_orders = [
        {"order_id": "U-901", "day": "Tuesday", "area_sqft": 2600, "pest": "Ant", "pets": "No", "children": "No"}, # Trap: >2000, no pets, previously would use Pyrethrin, now MUST use Bifenthrin. Area 2600 * 0.08 = 208 oz.
        {"order_id": "U-902", "day": "Tuesday", "area_sqft": 900, "pest": "Termite", "pets": "No", "children": "No"}
    ]
    with open("orders/urgent_tuesday.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "day", "area_sqft", "pest", "pets", "children"])
        writer.writeheader()
        writer.writerows(urgent_orders)

def build_turn_3():
    os.makedirs("logs", exist_ok=True)
    
    # 1. Leak Log
    log_content = """[CRITICAL ALERT] 03:14 AM - PRESSURE DROP DETECTED IN TANK B (Bifenthrin).
[SENSOR 1] Liquid level anomaly.
[CALCULATION] Loss estimated at exactly 35.5% of the CURRENT remaining volume in the tank prior to the leak.
[STATUS] Valve manually shut off at 06:00 AM. Awaiting maintenance.
"""
    with open("logs/leak_report.log", "w") as f:
        f.write(log_content)

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
