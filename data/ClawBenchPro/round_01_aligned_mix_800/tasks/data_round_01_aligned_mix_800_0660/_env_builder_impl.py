import os
import json
import csv

def build_env():
    # Create the dirty notes directory
    os.makedirs("patient_notes", exist_ok=True)

    # 1. Messy CSV file
    csv_data = [
        ["PatientID", "Category", "TimeSpent"],
        ["P-001", "Private", "2.5"],
        ["P-002", "Charity", "1.5"],
        ["P-003", "Charity", "3.0"]
    ]
    with open(os.path.join("patient_notes", "week1_logs.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. Unstructured text file (The "scribbles")
    text_data = """Notes for Tuesday:
- Patient ID: P-004
- Name: Mary Jenkins
- Program: Charity
- Duration: 2.0 hrs

Notes for Wednesday:
- Patient ID: P-005
- Name: Bob S.
- Program: Private Insurance
- Duration: 1.5 hrs
"""
    with open(os.path.join("patient_notes", "scribbles.txt"), "w") as f:
        f.write(text_data)

    # 3. JSON file with slightly different keys
    json_data = [
        {"uid": "P-006", "billing": "Charity", "time": 4.5},
        {"uid": "P-007", "billing": "Medicaid", "time": 1.0}
    ]
    with open(os.path.join("patient_notes", "week2_logs.json"), "w") as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    build_env()
