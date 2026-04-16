import os
import csv

def build_env():
    base_dir = "assets/data_419"
    claim_dir = os.path.join(base_dir, "claim_data")
    
    os.makedirs(claim_dir, exist_ok=True)
    
    # Write notepad scrawls
    notepad_content = """Claim #88-A9 Notes:
- Accident officially occurred on 2023-10-15.
- RULE 1: Any medical bills dated PRIOR to 2023-10-15 are strictly unrelated and must be denied.
- RULE 2: Fraud department just confirmed Dr. Smith is under federal indictment. Deny ALL claims from 'Dr. Smith Clinic', regardless of the date.
- Calculate the total amount claimed across all invoices.
- Calculate the total amount approved (only invoices that pass both rules above).
- I need the output as a JSON file named `verdict.json` in the current directory.
- Schema requirement:
{
  "total_claimed": float,
  "total_approved": float,
  "denied_invoices": [list of integer IDs that were denied]
}
Make sure the lists are sorted. Double check the math.
"""
    with open(os.path.join(claim_dir, "notepad_scrawls.txt"), "w") as f:
        f.write(notepad_content)
        
    # Write invoices CSV
    invoices = [
        {"id": 1, "date": "2023-10-16", "provider": "City General Hospital", "amount": "2500.00"},
        {"id": 2, "date": "2023-10-14", "provider": "Dr. Smith Clinic", "amount": "850.50"},
        {"id": 3, "date": "2023-10-18", "provider": "PharmaCorp Rx", "amount": "120.25"},
        {"id": 4, "date": "2023-10-19", "provider": "Dr. Smith Clinic", "amount": "400.00"},
        {"id": 5, "date": "2023-10-12", "provider": "Downtown ER", "amount": "1500.00"},
        {"id": 6, "date": "2023-10-22", "provider": "Physical Therapy Partners", "amount": "600.75"}
    ]
    
    with open(os.path.join(claim_dir, "invoices.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "provider", "amount"])
        writer.writeheader()
        writer.writerows(invoices)

if __name__ == "__main__":
    build_env()
