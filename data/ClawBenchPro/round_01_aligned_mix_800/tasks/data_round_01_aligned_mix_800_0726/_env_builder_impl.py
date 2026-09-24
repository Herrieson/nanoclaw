import os
import json
import csv

def build_env():
    # Create directories
    os.makedirs("records", exist_ok=True)
    os.makedirs("registry", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Authorized personnel list
    authorized = [
        {"id": "V001", "name": "Sarah Chen"},
        {"id": "V002", "name": "Michael Ross"},
        {"id": "V003", "name": "Elena Rodriguez"},
        {"id": "V005", "name": "David Kim"}
    ]
    with open("registry/authorized_personnel.json", "w") as f:
        json.dump(authorized, f, indent=4)

    # Screening logs with dirty data
    # Illegal volunteers: "John Doe", "Unknown"
    # Normal volunteers: Sarah, Michael, Elena
    # Anomalous BP: ID 104 (BP 210)
    logs = [
        ["log_id", "volunteer_name", "patient_id", "systolic_bp", "duration_minutes"],
        ["101", "Sarah Chen", "P-882", "120", "45"],
        ["102", "Michael Ross", "P-883", "135", "30"],
        ["103", "John Doe", "P-884", "118", "60"], # Unauthorized
        ["104", "Elena Rodriguez", "P-885", "210", "40"], # High BP anomaly
        ["105", "Sarah Chen", "P-886", "128", "50"],
        ["106", "Unknown", "P-887", "115", "15"], # Unauthorized
        ["107", "David Kim", "P-888", "130", "25"],
        ["108", "Michael Ross", "P-889", "140", "20"]
    ]
    
    with open("records/screening_logs.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(logs)

if __name__ == "__main__":
    build_env()
