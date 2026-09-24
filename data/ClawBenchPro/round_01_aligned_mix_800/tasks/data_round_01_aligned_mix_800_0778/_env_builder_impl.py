import os
import csv
import random

def build_env():
    os.makedirs("intake_logs", exist_ok=True)
    os.makedirs("secure_vault", exist_ok=True)

    # Doctor IDs
    docs = ["DOC-101", "DOC-204", "DOC-339", "DOC-492", "DOC-505"]
    
    # Pre-determined violations to ensure deterministic testing
    # DOC-101: 3 violations
    # DOC-339: 1 violation
    # DOC-492: 2 violations
    
    data_files = {
        "batch_A.csv": [
            ("P-001", "DOC-101", "Patient complains of headaches. SSN: 123-45-6789 provided for billing."), # Violation
            ("P-002", "DOC-204", "Routine checkup. No issues."),
            ("P-003", "DOC-101", "Follow up. Patient SSN 987-65-4321 noted. Allergic to penicillin."), # Violation
            ("P-004", "DOC-505", "Blood pressure normal.")
        ],
        "batch_B.csv": [
            ("P-005", "DOC-339", "Patient requested record transfer. 111-22-3344 is the SSN."), # Violation
            ("P-006", "DOC-204", "Needs MRI. SSN is pending."), # No actual SSN format
            ("P-007", "DOC-492", "Notes: 555-66-7788 - patient is anxious."), # Violation
            ("P-008", "DOC-101", "Clear. SSN 000-00-0000 on file."), # Violation
            ("P-009", "DOC-505", "Call 555-123-4567 for emergency.") # Phone number, not SSN
        ],
        "batch_C.csv": [
            ("P-010", "DOC-492", "Insurance updated. SSN: 999-88-7777."), # Violation
            ("P-011", "DOC-204", "Patient feels better today."),
            ("P-012", "DOC-339", "Refilled prescription 123-45.") # Partial, not a full SSN
        ]
    }

    for filename, rows in data_files.items():
        with open(os.path.join("intake_logs", filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["patient_id", "doctor_id", "public_comments"])
            for row in rows:
                writer.writerow(row)

if __name__ == "__main__":
    build_env()
