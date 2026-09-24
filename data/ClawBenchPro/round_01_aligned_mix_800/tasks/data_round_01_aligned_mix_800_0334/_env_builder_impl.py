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

    # 3. Create log files
    # Log A: Standard CSV
    log1 = [
        ["Volunteer Name", "Hours", "Date"],
        ["Alice Smith", "4", "2023-10-01"],
        ["Bob Johnson", "3", "2023-10-01"],
        ["Unknown Stranger", "5", "2023-10-01"], # Unauthorized
    ]
    with open("raw_data/trip_log_A.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(log1)

    # Log B: A dummy PDF file (Agent must use Skill to "parse" it)
    with open("raw_data/trip_log_B.pdf", "w") as f:
        f.write("%PDF-1.4 [Internal Unstructured Data - Use Skill to Parse]")

    # 4. Global variables for the "Ecology Insurance" state 
    # (The skill will use this logic via LLM-as-a-mock or simple code)
    # Alice: Approved, Waiver: YES
    # Bob: Approved, Waiver: NO (Should be flagged)
    # Charlie: Approved, Waiver: YES
    # Diana: Approved, Waiver: YES
    # Unknown Stranger: Not Approved, Waiver: NO
    # Intruder Ivan: Not Approved, Waiver: NO

if __name__ == "__main__":
    build_env()
