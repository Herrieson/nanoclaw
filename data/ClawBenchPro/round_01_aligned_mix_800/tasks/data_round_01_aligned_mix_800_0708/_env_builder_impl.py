import os
import csv
import json

def build_env():
    # Create required directories
    os.makedirs("claim_files", exist_ok=True)
    
    # Generate the policy master list
    policies = [
        ["policy_id", "coverage_limit", "active_date"],
        ["POL-001", "5000.00", "2023-01-01"],
        ["POL-002", "10000.00", "2023-05-01"],
        ["POL-003", "2500.00", "2022-11-15"],
        ["POL-004", "150000.00", "2021-06-01"]
    ]
    
    with open("policies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(policies)
        
    # Generate claims files (mix of valid and invalid)
    claims = [
        # Valid claim
        {
            "claim_id": "CLM-8810",
            "policy_id": "POL-001",
            "requested_amount": 4500.00,
            "incident_date": "2023-02-15",
            "adjuster_notes": "Minor fender bender. All documentation provided."
        },
        # Invalid: Exceeds limit ($12,000 > $10,000)
        {
            "claim_id": "CLM-8811",
            "policy_id": "POL-002",
            "requested_amount": 12000.00,
            "incident_date": "2023-06-10",
            "adjuster_notes": "Hail damage to roof and siding."
        },
        # Invalid: Predates policy (2022-10-25 < 2022-11-15)
        {
            "claim_id": "CLM-8812",
            "policy_id": "POL-003",
            "requested_amount": 1500.00,
            "incident_date": "2022-10-25",
            "adjuster_notes": "Stolen electronics from vehicle."
        },
        # Invalid: Slightly exceeds limit ($5001 > $5000)
        {
            "claim_id": "CLM-8813",
            "policy_id": "POL-001",
            "requested_amount": 5001.00,
            "incident_date": "2023-01-05",
            "adjuster_notes": "Medical expenses related to slip and fall."
        },
        # Valid claim
        {
            "claim_id": "CLM-8814",
            "policy_id": "POL-004",
            "requested_amount": 145000.00,
            "incident_date": "2022-01-10",
            "adjuster_notes": "Major commercial property fire damage."
        }
    ]
    
    # Write each claim to a separate file to mimic a messy dump
    for claim in claims:
        file_path = os.path.join("claim_files", f"{claim['claim_id']}_report.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(claim, f, indent=4)
            
    # Add some noise to the folder to distract
    with open(os.path.join("claim_files", "adjuster_scratchpad.txt"), "w", encoding="utf-8") as f:
        f.write("Call John back about CLM-8810.\nNote to self: The coffee machine is broken again.\nNeed to verify POL-004 coverage limits soon.")

if __name__ == "__main__":
    build_env()
