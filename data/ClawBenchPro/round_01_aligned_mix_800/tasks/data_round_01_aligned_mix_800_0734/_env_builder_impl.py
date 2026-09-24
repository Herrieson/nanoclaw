import os
import json
import csv

def build_env():
    # 1. Create directories
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 2. Approved Volunteers (Whitelist)
    approved = [
        {"name": "Alice Smith", "id": "V001"},
        {"name": "Bob Johnson", "id": "V002"},
        {"name": "Charlie Brown", "id": "V003"},
        {"name": "Diana Prince", "id": "V004"},
        {"name": "Edward Norton", "id": "V005"}
    ]
    with open("approved_volunteers.json", "w") as f:
        json.dump(approved, f, indent=4)

    # 3. Create messy log files
    log1 = [
        ["Volunteer Name", "Hours", "Date", "Note"],
        ["Alice Smith", "4", "2023-10-01", "Early arrival"],
        ["Bob Johnson", "3", "2023-10-01", ""],
        ["Unknown Stranger", "5", "2023-10-01", "Just showed up"], # Unauthorized
        ["Charlie Brown", "2.5", "2023-10-02", "Rainy day"]
    ]
    
    log2 = [
        ["Name", "Duration (Hrs)", "Activity"],
        ["Alice Smith", "2", "Bird counting"],
        ["Diana Prince", "6", "Trail maintenance"],
        ["Intruder Ivan", "4", "No waiver signed"], # Unauthorized
        ["Bob Johnson", "invalid_data", "Mistake"], # Dirty data
        ["Bob Johnson", "2", "Late shift"]
    ]

    with open("raw_data/trip_log_A.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log1)

    with open("raw_data/trip_log_B.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log2)

if __name__ == "__main__":
    build_env()
