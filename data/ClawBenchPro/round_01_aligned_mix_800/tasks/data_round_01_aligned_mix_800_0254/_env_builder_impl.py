import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs("messy_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Create the messy volunteer shifts (JSON)
    # Note: Use slightly messy names to test Agent's matching/skill usage
    shifts = [
        {"name": "Hector Ramirez", "hours": 3.5, "task": "Brakes"},
        {"name": "Sketchy Bob", "hours": 6.0, "task": "Wandering around"},
        {"name": "Luis P.", "hours": 2.0, "task": "Oil changes"}, # Shortened name
        {"name": "Hector Ramirez", "hours": 4.5, "task": "Transmission"},
        {"name": "Maria Gonzalez", "hours": 5.0, "task": "Intake manifold"},
        {"name": "Random Joe", "hours": 2.0, "task": "Eating donuts"},
        {"name": "Fr. Thomas", "hours": 1.5, "task": "Blessing the tools"}, # Abbreviation
        {"name": "Luis Perez", "hours": 3.0, "task": "Tire rotation"}
    ]
    with open("messy_logs/volunteer_shifts.json", "w", encoding="utf-8") as f:
        json.dump({"weekend_shifts": shifts}, f, indent=2)

    # 2. Create the parts inventory (CSV) using Internal IDs
    # CH-101: Oil Filter (3) - NEED
    # CH-202: Brake Pads (15) - OK
    # CH-303: Alternator (1) - NEED
    # CH-404: Wiper Blades (8) - OK
    # CH-505: Spark Plugs (4) - NEED
    # CH-606: Battery (5) - OK
    parts_data = [
        ["Internal_ID", "Quantity", "Location"],
        ["CH-101", "3", "Shelf A"],
        ["CH-202", "15", "Shelf B"],
        ["CH-303", "1", "Floor"],
        ["CH-404", "8", "Shelf A"],
        ["CH-505", "4", "Shelf C"],
        ["CH-606", "5", "Floor"]
    ]
    with open("messy_logs/inventory.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(parts_data)

if __name__ == "__main__":
    build_env()
