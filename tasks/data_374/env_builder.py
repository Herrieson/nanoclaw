import os
import csv
import random

def build_env():
    base_dir = "assets/data_374"
    claims_dir = os.path.join(base_dir, "claims_data")
    
    # Create directories
    os.makedirs(os.path.join(claims_dir, "week_1"), exist_ok=True)
    os.makedirs(os.path.join(claims_dir, "week_2"), exist_ok=True)
    os.makedirs(os.path.join(claims_dir, "archive", "old_format"), exist_ok=True)

    # Predefined targets to ensure deterministic verification
    targets = [
        {"PatientID": "P-1001", "Amount": "1500.00", "folder": "week_1", "file": "log_a.csv"},
        {"PatientID": "P-2034", "Amount": "320.50",  "folder": "week_2", "file": "export.txt"},
        {"PatientID": "P-5521", "Amount": "899.99",  "folder": "archive/old_format", "file": "dump.csv"},
        {"PatientID": "P-1122", "Amount": "100.00",  "folder": "week_1", "file": "log_b.csv"} # Extra target
    ]

    header = ["ClaimID", "PatientID", "Date", "Status", "ErrorCode", "Amount"]

    def generate_random_row():
        claim_id = f"C-{random.randint(10000, 99999)}"
        patient_id = f"P-{random.randint(1000, 9999)}"
        date = f"2023-10-{random.randint(10, 28)}"
        status = random.choice(["APPROVED", "PENDING", "REJECTED"])
        error_code = f"E-{random.randint(700, 750)}" if status == "REJECTED" else ""
        if error_code == "E-729":  # Avoid accidental matches
            error_code = "E-730"
        amount = f"{random.uniform(50.0, 5000.0):.2f}"
        return [claim_id, patient_id, date, status, error_code, amount]

    # Generate files
    files_to_create = {
        "week_1/log_a.csv": [],
        "week_1/log_b.csv": [],
        "week_2/export.txt": [],
        "archive/old_format/dump.csv": [],
        "archive/misc_logs.txt": []
    }

    # Populate with random data
    for file_path in files_to_create.keys():
        for _ in range(random.randint(15, 30)):
            files_to_create[file_path].append(generate_random_row())

    # Inject targets
    for t in targets:
        claim_id = f"C-{random.randint(10000, 99999)}"
        date = f"2023-10-{random.randint(10, 28)}"
        row = [claim_id, t["PatientID"], date, "REJECTED", "E-729", t["Amount"]]
        full_path = f"{t['folder']}/{t['file']}"
        files_to_create[full_path].append(row)

    # Write files
    for file_path, rows in files_to_create.items():
        full_path = os.path.join(claims_dir, file_path)
        random.shuffle(rows) # Shuffle so targets aren't always at the end
        with open(full_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

if __name__ == "__main__":
    build_env()
