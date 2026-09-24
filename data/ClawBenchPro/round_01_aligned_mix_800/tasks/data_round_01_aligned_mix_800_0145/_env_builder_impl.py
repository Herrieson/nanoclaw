import os
import json
import argparse
import csv

def build_turn_1():
    os.makedirs("venues", exist_ok=True)
    
    venues_data = [
        {"id": "v1", "name": "Southside Hall", "cost": 300, "capacity": 60, "zone": "South", "dates_available": ["2024-07-05"], "has_kitchen": False, "ada_rating": "A"},
        {"id": "v2", "name": "Northside Comm Center", "cost": 800, "capacity": 150, "zone": "Northside", "dates_available": ["2024-07-10"], "has_kitchen": False, "ada_rating": "A"},
        {"id": "v3", "name": "Eastside Kitchen", "cost": 500, "capacity": 100, "zone": "East", "dates_available": ["2024-07-15"], "has_kitchen": True, "ada_rating": "B"},
        {"id": "v4", "name": "Westside Gym", "cost": 900, "capacity": 120, "zone": "West", "dates_available": ["2024-07-10"], "has_kitchen": False, "ada_rating": "B"},
        {"id": "v5", "name": "Downtown Loft", "cost": 700, "capacity": 200, "zone": "Downtown", "dates_available": ["2024-07-15"], "has_kitchen": False, "ada_rating": "A"},
        {"id": "v6", "name": "Luxury Hall", "cost": 1500, "capacity": 200, "zone": "West", "dates_available": ["2024-07-12"], "has_kitchen": False, "ada_rating": "A"},
        {"id": "v7", "name": "Cheap North", "cost": 200, "capacity": 70, "zone": "Northside", "dates_available": ["2024-07-05"], "has_kitchen": False, "ada_rating": "C"},
        {"id": "v8", "name": "Big South", "cost": 750, "capacity": 120, "zone": "South", "dates_available": ["2024-07-05"], "has_kitchen": False, "ada_rating": "B"},
        {"id": "v9", "name": "Alt South", "cost": 600, "capacity": 60, "zone": "South", "dates_available": ["2024-07-12"], "has_kitchen": False, "ada_rating": "A"},
        {"id": "v10", "name": "Far East Kitchen", "cost": 850, "capacity": 90, "zone": "East", "dates_available": ["2024-07-20"], "has_kitchen": True, "ada_rating": "B"}
    ]
    
    for v in venues_data:
        with open(os.path.join("venues", f"{v['id']}.json"), "w") as f:
            json.dump(v, f, indent=2)

    rules_content = """Campaign Requirements for Summer of Solidarity:

1. TR (Tenant Rights): 
   - We need an intimate but accessible space.
   - Capacity must be >= 50.
   - ADA rating MUST be strictly 'A'.

2. YA (Youth Art): 
   - Needs room for installations.
   - Capacity must be >= 100.
   - ADA rating can be 'A' or 'B'.

3. FD (Food Drive): 
   - Heavy logistics.
   - Capacity must be >= 80.
   - A dedicated kitchen facility is absolutely REQUIRED (has_kitchen must be true).
"""
    with open("campaign_rules.txt", "w") as f:
        f.write(rules_content)


def build_turn_2():
    volunteers = [
        ["Name", "Zone", "Available_Dates"],
        ["Alice", "South", "2024-07-05"],
        ["Bob", "South", "2024-07-05"],
        ["Charlie", "South", "2024-07-10"],
        ["Dave", "West", "2024-07-10"],
        ["Eve", "West", "2024-07-10"],
        ["Frank", "West", "2024-07-05"],
        ["Grace", "East", "2024-07-15"],
        ["Heidi", "East", "2024-07-15"],
        ["Ivan", "Northside", "2024-07-10"],
        ["Judy", "Downtown", "2024-07-15"],
        ["Kevin", "East", "2024-07-20"]
    ]
    
    with open("volunteers.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(volunteers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
