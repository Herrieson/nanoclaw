import os
import json
import csv
import argparse

def build_turn_1():
    # Volunteers raw data - includes traps for age and dates
    volunteers = [
        {"name": "Agnes Smith", "age": 55, "bg_check": "2023-06-15", "role": "Lead"},
        {"name": "John Doe", "age": 42, "bg_check": "2023-04-30", "role": "Assistant"}, # Trap: 1 day before cutoff
        {"name": "Mary Jane", "age": 17, "bg_check": "2023-11-20", "role": "Lead"}, # Trap: under 18 requesting lead
        {"name": "Peter Paul", "age": 34, "bg_check": "2024-01-10", "role": "Lead"},
        {"name": "Lucy Vance", "age": 16, "bg_check": "2023-08-05", "role": "Assistant"}
    ]
    
    with open("volunteers_raw.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "bg_check", "role"])
        writer.writeheader()
        writer.writerows(volunteers)

    # Curriculum - priority 1 is highest
    curriculum = [
        {"activity": "Arts and Crafts", "age_group": "5-7", "priority": 1, "needs": {"glitter_pack": 10, "glue_sticks": 15}},
        {"activity": "Coloring Book", "age_group": "8-10", "priority": 2, "needs": {"crayons": 20}},
        {"activity": "Advanced Dioramas", "age_group": "11-13", "priority": 3, "needs": {"glitter_pack": 5, "construction_paper": 50}}
    ]
    
    with open("vbs_curriculum.json", "w") as f:
        json.dump(curriculum, f, indent=4)

    # Inventory
    inventory = {
        "glitter_pack": 5,
        "glue_sticks": 20, # surplus
        "construction_paper": 100, # surplus
        "crayons": 0
    }
    
    with open("supplies_inventory.json", "w") as f:
        json.dump(inventory, f, indent=4)


def build_turn_2():
    # Budget constraint
    with open("budget.txt", "w") as f:
        f.write("Parish Council Directive:\nMaximum allowed expenditure for new VBS supplies this year is strictly capped at $200.00.")

    # Catalog prices
    catalog = {
        "glitter_pack": 25.0, # Trap: extremely expensive
        "glue_sticks": 1.5,
        "construction_paper": 0.5,
        "crayons": 2.0
    }
    with open("catalog.json", "w") as f:
        json.dump(catalog, f, indent=4)

    # Late volunteers
    late_vols = [
        {"name": "Thomas Aquinas", "age": 60, "bg_check": "2023-05-02", "role": "Lead"},
        {"name": "Clare Assisi", "age": 17, "bg_check": "2023-12-01", "role": "Lead"}, # Trap: rule violation
        {"name": "Joan Arc", "age": 22, "bg_check": "2022-10-10", "role": "Assistant"} # Trap: date violation
    ]
    with open("late_volunteers.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age", "bg_check", "role"])
        writer.writeheader()
        writer.writerows(late_vols)


def build_turn_3():
    # Diocese warnings
    warnings = [
        {"name": "Peter Paul", "infraction_code": "Code 3", "description": "Left children unattended near road."},
        {"name": "Clare Assisi", "infraction_code": "Code 1", "description": "Late to training."},
        {"name": "Thomas Aquinas", "infraction_code": "Code 2", "description": "Used unapproved theological texts."}
    ]
    with open("diocese_warnings.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "infraction_code", "description"])
        writer.writeheader()
        writer.writerows(warnings)


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
