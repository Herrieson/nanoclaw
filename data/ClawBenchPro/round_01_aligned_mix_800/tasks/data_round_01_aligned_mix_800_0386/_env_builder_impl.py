import os
import csv
import json

def build_env():
    # 1. Create directories
    os.makedirs("signups", exist_ok=True)
    os.makedirs("planning", exist_ok=True)
    
    # 2. Create group_A.csv (Standard Volunteers)
    # John: 5 hours, Pickup Truck (Valid)
    # Alice: 3 hours, Gloves (Valid, not heavy)
    csv_data = [
        ["name", "hours_committed", "gear"],
        ["John", "5", "pickup truck"],
        ["Alice", "3", "leather gloves"]
    ]
    with open("signups/group_A.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 3. Create group_B.json
    # Dave: 8 hours, ASSET-9902 (Need to look up: Case Backhoe)
    # Bob: 4 hours, heavy truck (BUT Bob is on the blacklist API)
    json_data = [
        {"name": "Dave", "hours": 8, "equipment_id": "ASSET-9902"},
        {"name": "Bob", "hours": 4, "equipment": "heavy truck"}
    ]
    with open("signups/group_B.json", "w") as f:
        json.dump(json_data, f, indent=2)

    # 4. Create notes.txt
    # Sarah: 6 hours, ASSET-7721 (Need to look up: Ford F-150)
    # Carl: 5 hours, no gear (BUT Carl is on the blacklist API)
    notes_content = """Volunteer Notes:
- Sarah called: confirmed 6 hours. Bringing item ASSET-7721 from the warehouse.
- Carl: said he'd help for 5 hours. No equipment.
"""
    with open("signups/notes.txt", "w") as f:
        f.write(notes_content)

    # 5. Create a Mock PDF for Mike (requires specialized skill)
    # Mike: 2 hours in notes, but PDF adds 2 more hours = total 4.
    with open("signups/liability_waiver.pdf", "w") as f:
        f.write("%PDF-1.4 (MOCK)\nThis is a liability waiver for Mike. Note: Mike has updated his commitment from 2 hours to 4 hours total.")

if __name__ == "__main__":
    build_env()
