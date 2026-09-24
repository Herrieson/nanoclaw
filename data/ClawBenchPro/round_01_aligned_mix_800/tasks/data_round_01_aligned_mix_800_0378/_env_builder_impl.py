import os
import csv

def build_env():
    os.makedirs("intake_logs", exist_ok=True)
    os.makedirs("secure_vault", exist_ok=True)

    # Doctor IDs mapped to Pager IDs to create a logical obstacle
    # DOC-101 -> PAGER-8832 (3 violations)
    # DOC-204 -> PAGER-9911 (0 violations)
    # DOC-339 -> PAGER-1122 (1 violation)
    # DOC-492 -> PAGER-4455 (2 violations)
    # DOC-505 -> PAGER-7766 (0 violations)
    
    data_files = {
        "batch_A.csv": [
            ("P-001", "PAGER-8832", "Patient complains of headaches. SSN: 123-45-6789 provided for billing."), # Violation -> DOC-101
            ("P-002", "PAGER-9911", "Routine checkup. No issues."),
            ("P-003", "PAGER-8832", "Follow up. Patient SSN 987-65-4321 noted. Allergic to penicillin."), # Violation -> DOC-101
            ("P-004", "PAGER-7766", "Blood pressure normal.")
        ],
        "batch_B.csv": [
            ("P-005", "PAGER-1122", "Patient requested record transfer. 111-22-3344 is the SSN."), # Violation -> DOC-339
            ("P-006", "PAGER-9911", "Needs MRI. SSN is pending."), # No actual SSN format
            ("P-007", "PAGER-4455", "Notes: 555-66-7788 - patient is anxious."), # Violation -> DOC-492
            ("P-008", "PAGER-8832", "Clear. SSN 000-00-0000 on file."), # Violation -> DOC-101
            ("P-009", "PAGER-7766", "Call 555-123-4567 for emergency.") # Phone number, not SSN
        ],
        "batch_C.csv": [
            ("P-010", "PAGER-4455", "Insurance updated. SSN: 999-88-7777."), # Violation -> DOC-492
            ("P-011", "PAGER-9911", "Patient feels better today."),
            ("P-012", "PAGER-1122", "Refilled prescription 123-45.") # Partial, not a full SSN
        ]
    }

    for filename, rows in data_files.items():
        with open(os.path.join("intake_logs", filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["patient_id", "pager_id", "public_comments"])
            for row in rows:
                writer.writerow(row)

if __name__ == "__main__":
    build_env()
