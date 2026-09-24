import os
import csv
import random

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    
    # 1. Create the whitelist (Authorized Codes)
    whitelist_codes = ["92507", "92521", "92522", "92523", "92524", "92610"]
    with open("records/authorized_codes.txt", "w") as f:
        f.write("OFFICIAL AUTHORIZED PROCEDURE CODES - SLP SERVICES\n")
        f.write("--------------------------------------------------\n")
        for code in whitelist_codes:
            f.write(f"CODE: {code}\n")
    
    # 2. Create messy session data
    patients = ["Miller, J.", "Smith, A.", "Wilson, K.", "Brown, L.", "Davis, M."]
    raw_data = [
        # Valid sessions
        ["2023-10-01", "Miller, J.", "92507", "1.0"],
        ["2023-10-02", "Smith, A.", "92521", "1.5"],
        ["2023-10-02", "Smith, A.", "92521", "1.5"], # Duplicate
        ["2023-10-05", "Wilson, K.", "92610", "1.0"],
        # Invalid code
        ["2023-10-06", "Brown, L.", "99999", "0.5"],
        ["2023-10-07", "Davis, M.", "88888", "1.0"],
        # Valid session
        ["2023-10-10", "Miller, J.", "92523", "2.0"],
        # Duplicate with slight variation in whitespace
        ["2023-10-10", "Miller, J. ", "92523", "2.0 "], 
    ]
    
    with open("records/sessions_october_raw.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "PatientName", "ProcCode", "DurationHours"])
        for row in raw_data:
            writer.writerow(row)
            
    # Add a "distractor" file
    with open("records/notes_unrelated.txt", "w") as f:
        f.write("Remember to buy more merino wool for the scarf project.")

if __name__ == "__main__":
    build_env()
