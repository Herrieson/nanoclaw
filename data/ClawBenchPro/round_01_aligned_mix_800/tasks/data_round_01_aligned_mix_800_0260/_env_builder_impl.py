import os
import json
import csv

def build_env():
    # Create the dirty notes directory
    os.makedirs("patient_notes", exist_ok=True)

    # 1. Messy CSV file (Now uses Insurance Codes instead of explicitly saying "Charity")
    csv_data = [
        ["PatientID", "InsuranceCode", "TimeSpent"],
        ["P-001", "INS-PRI", "2.5"],
        ["P-002", "INS-CHRY", "1.5"],
        ["P-003", "INS-CHRY", "3.0"]
    ]
    with open(os.path.join("patient_notes", "week1_logs.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

    # 2. Voice memo binary file (Replacing the text scribbles)
    # This represents encrypted/proprietary dictaphone data.
    dummy_binary_content = b"\x89VMEMO\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00...audio bytes encrypted..."
    with open(os.path.join("patient_notes", "tuesday_ward_rounds.vmemo"), "wb") as f:
        f.write(dummy_binary_content)

    # 3. JSON file with slightly different keys and financial tiers
    json_data = [
        {"uid": "P-006", "finance_tier": "TIER-C", "time": 4.5},
        {"uid": "P-007", "finance_tier": "MEDICAID-STD", "time": 1.0}
    ]
    with open(os.path.join("patient_notes", "week2_logs.json"), "w") as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    build_env()
