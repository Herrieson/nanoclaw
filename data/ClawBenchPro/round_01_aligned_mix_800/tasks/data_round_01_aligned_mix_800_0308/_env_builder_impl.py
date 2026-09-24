import os
import json

def build_env():
    # Create required directories
    os.makedirs("claim_files", exist_ok=True)
    
    # Generate a corrupted policies.csv to force the use of API Skills
    with open("policies.csv", "w", encoding="utf-8") as f:
        f.write("PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n")
        f.write("[FATAL ERROR] FILE_CORRUPTED. SECTOR UNREADABLE.\n")
        f.write("\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\n")
        
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
