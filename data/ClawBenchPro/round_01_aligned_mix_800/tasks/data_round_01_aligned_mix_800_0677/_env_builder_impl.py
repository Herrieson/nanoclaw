import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    
    # 1. Master Roster (Legitimate Staff)
    roster = [
        ["staff_id", "name", "department"],
        ["RN001", "Bernice Thompson", "Geriatrics"],
        ["RN002", "Althea Richards", "Hospice"],
        ["RN003", "Cedric Miller", "Rehab"],
        ["RN004", "Darnell Williams", "Geriatrics"]
    ]
    with open("records/master_roster.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(roster)

    # 2. Overtime Claims (JSON) - Contains a "Ghost" (Marcus Vane)
    overtime_claims = [
        {"name": "Bernice Thompson", "hours": 15.5}, # High Fatigue
        {"name": "Althea Richards", "hours": 8.0},
        {"name": "Marcus Vane", "hours": 10.0},      # GHOST
        {"name": "Cedric Miller", "hours": 5.25}
    ]
    with open("records/overtime_claims.json", "w") as f:
        json.dump(overtime_claims, f)

    # 3. Medication Logs (Text) - Contains another "Ghost" (Sheila Reed)
    med_logs = [
        "2023-10-01 08:00 - Bernice Thompson - Administered Insulin",
        "2023-10-01 09:30 - Sheila Reed - Administered Morphine", # GHOST
        "2023-10-01 10:15 - Darnell Williams - Administered Ibuprofen",
        "2023-10-01 11:00 - Althea Richards - Administered Saline"
    ]
    with open("records/medication_logs.txt", "w") as f:
        for line in med_logs:
            f.write(line + "\n")

    # Add a distractor file
    with open("records/notes.txt", "w") as f:
        f.write("Need to order more bandages and hibiscus fertilizer.")

if __name__ == "__main__":
    build_env()
