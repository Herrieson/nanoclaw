import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs("messy_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create the whitelist of approved volunteers
    whitelist = ["Hector Ramirez", "Luis Perez", "Father Thomas", "Maria Gonzalez"]
    with open("messy_logs/approved_crew.txt", "w", encoding="utf-8") as f:
        f.write("--- OFFICIAL CHURCH AUTO MINISTRY CREW ---\n")
        for name in whitelist:
            f.write(f"{name}\n")

    # 2. Create the messy volunteer shifts (JSON)
    # Includes unapproved people (Sketchy Bob, Random Joe) and messy nested data
    shifts = [
        {"name": "Hector Ramirez", "hours": 3.5, "task": "Brakes"},
        {"name": "Sketchy Bob", "hours": 6.0, "task": "Wandering around"},
        {"name": "Luis Perez", "hours": 2.0, "task": "Oil changes"},
        {"name": "Hector Ramirez", "hours": 4.5, "task": "Transmission"},
        {"name": "Maria Gonzalez", "hours": 5.0, "task": "Intake manifold"},
        {"name": "Random Joe", "hours": 2.0, "task": "Eating donuts"},
        {"name": "Father Thomas", "hours": 1.5, "task": "Blessing the tools"},
        {"name": "Luis Perez", "hours": 3.0, "task": "Tire rotation"}
    ]
    with open("messy_logs/volunteer_shifts.json", "w", encoding="utf-8") as f:
        json.dump({"weekend_shifts": shifts}, f, indent=2)

    # 3. Create the parts inventory (CSV)
    # Needs restocking: Oil Filter (3), Alternator (1), Spark Plugs (4)
    # Good: Brake Pads (15), Wiper Blades (8), Battery (5)
    parts_data = [
        ["Part_Name", "Quantity", "Location"],
        ["Oil Filter", "3", "Shelf A"],
        ["Brake Pads", "15", "Shelf B"],
        ["Alternator", "1", "Floor"],
        ["Wiper Blades", "8", "Shelf A"],
        ["Spark Plugs", "4", "Shelf C"],
        ["Battery", "5", "Floor"]
    ]
    with open("messy_logs/inventory.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(parts_data)

if __name__ == "__main__":
    build_env()
