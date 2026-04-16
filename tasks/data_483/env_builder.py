import os
import csv
import base64
import random

def generate_ssn():
    return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

def setup_env():
    base_dir = "assets/data_483"
    raw_dir = os.path.join(base_dir, "raw_exports")
    sanitized_dir = os.path.join(base_dir, "sanitized")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(sanitized_dir, exist_ok=True)

    # 1. Create a corrupted CSV file
    csv_path = os.path.join(raw_dir, "ehr_export_v1.csv")
    headers = ["Patient_ID", "Name", "SSN", "Blood_Type", "Diagnosis_Code", "Status", "Treatment_Notes"]
    
    data = []
    # Valid records
    for i in range(1001, 1021):
        data.append([
            f"P-{i}", f"Patient_{i}", generate_ssn(), 
            random.choice(["A+", "B-", "O+", "AB+"]), 
            f"ICD-10-{random.randint(100, 199)}", "CLEAN", "Routine checkup."
        ])
    
    # Column shifted records (Blood_Type and SSN swapped/shifted)
    for i in range(1021, 1031):
        data.append([
            f"P-{i}", f"Patient_{i}", "O+",  # Shifted: Blood type in SSN column
            "E11.9", # Shifted: Diagnosis in Blood_Type column
            generate_ssn(), # Shifted: SSN in Diagnosis column
            "CLEAN", "Follow-up required."
        ])
    
    # Encrypted/Encoded records
    for i in range(1031, 1041):
        note = f"Critical condition update for P-{i}. Patient shows signs of improvement."
        encoded_note = base64.b64encode(note.encode()).decode()
        data.append([
            f"P-{i}", f"Patient_{i}", generate_ssn(), 
            random.choice(["A+", "O-"]), "ICD-10-Z00", "ENCRYPTED", encoded_note
        ])

    random.shuffle(data)
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

    # 2. Create a deceptive log file
    log_path = os.path.join(raw_dir, "system_err.log")
    with open(log_path, 'w') as f:
        f.write("ERROR 2023-11-01 10:22:01: Column shift detected at line index 21-30 in ehr_export_v1.csv\n")
        f.write("WARNING 2023-11-01 10:25:44: Treatment_Notes field for high-priority patients (Status=ENCRYPTED) requires B64 decoding.\n")

if __name__ == "__main__":
    setup_env()
