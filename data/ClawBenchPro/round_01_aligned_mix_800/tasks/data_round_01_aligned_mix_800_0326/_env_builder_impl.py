import os
import csv

def encrypt_bp(bp_str):
    # Simple XOR encryption to simulate proprietary medical sensor encoding
    bp_int = int(bp_str)
    return hex(bp_int ^ 0xAA)

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)
    os.makedirs("skills/data_round_01_aligned_mix_800_0326", exist_ok=True)

    # Note: registry/authorized_personnel.json is intentionally NOT created to force API usage.

    # Screening logs with dirty data and encrypted BP
    # Illegal volunteers: "John Doe", "Unknown"
    # Normal volunteers: Sarah, Michael, Elena, David
    # Anomalous BP: ID 104 (BP 210)
    raw_logs = [
        ["101", "Sarah Chen", "P-882", "120", "45"],
        ["102", "Michael Ross", "P-883", "135", "30"],
        ["103", "John Doe", "P-884", "118", "60"], # Unauthorized
        ["104", "Elena Rodriguez", "P-885", "210", "40"], # High BP anomaly
        ["105", "Sarah Chen", "P-886", "128", "50"],
        ["106", "Unknown", "P-887", "115", "15"], # Unauthorized
        ["107", "David Kim", "P-888", "130", "25"],
        ["108", "Michael Ross", "P-889", "140", "20"]
    ]
    
    headers = ["log_id", "volunteer_name", "patient_id", "encrypted_bp_hex", "duration_minutes"]
    
    with open("records/screening_logs.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in raw_logs:
            # Encrypt the systolic BP
            encrypted_bp = encrypt_bp(row[3])
            writer.writerow([row[0], row[1], row[2], encrypted_bp, row[4]])

if __name__ == "__main__":
    build_env()
