import os
import csv

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    
    # 1. Create messy session data (Same as original to maintain objective verification logic)
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
            
    # 2. Add an IT memo replacing the old txt file
    memo_content = """MEMO - IT DEPARTMENT
Date: Oct 28, 2023
Subject: Sunsetting Local Authorization Text Files

Please be advised that 'authorized_codes.txt' has been permanently removed due to compliance audits. 
To verify if a procedure code is covered for SLP services, you must now use our command-line skill tools:

1. `legacy_medicare_portal` (Our old system, might be unstable during migration)
2. `optum_auth_gateway` (The new cloud gateway)

Both tools take a CPT/Procedure code as an argument and return authorization status. Please update your billing workflows accordingly.
"""
    with open("records/IT_memo.txt", "w") as f:
        f.write(memo_content)

    # Add a "distractor" file
    with open("records/notes_unrelated.txt", "w") as f:
        f.write("Remember to buy more merino wool for the scarf project. Also, tell IT their new tools are annoying.")

if __name__ == "__main__":
    build_env()
