import os
import json
import csv

def build_env():
    base_dir = "assets/data_73"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "audits"), exist_ok=True)

    # employees.json
    employees = {
        "E01": "Alice",
        "E02": "Bob",
        "E03": "Charlie",
        "E04": "David"
    }
    with open(os.path.join(base_dir, "employees.json"), "w") as f:
        json.dump(employees, f)

    # system_inventory.csv
    inventory = [
        {"ID": "RX-101", "Medication": "Lisinopril", "Expected": 100},
        {"ID": "RX-102", "Medication": "Metformin", "Expected": 250},
        {"ID": "RX-103", "Medication": "Amlodipine", "Expected": 150},
        {"ID": "RX-104", "Medication": "Albuterol", "Expected": 80},
        {"ID": "RX-105", "Medication": "Omeprazole", "Expected": 300},
        {"ID": "RX-106", "Medication": "Gabapentin", "Expected": 500}
    ]
    with open(os.path.join(base_dir, "system_inventory.csv"), "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["ID", "Medication", "Expected"])
        writer.writeheader()
        writer.writerows(inventory)

    # audits
    audit_data = [
        "Audit Log - Week 40",
        "===================",
        "[2023-10-01] Emp: E02 checked RX-101. Actual count: 98.",
        "[2023-10-01] Emp: E01 checked RX-102. Actual count: 250.",
        "[2023-10-02] Emp: E03 checked RX-101. Actual count: 95.", 
        "[2023-10-02] Emp: E04 checked RX-103. Actual count: 145.",
        "Note: Spill on aisle 3 cleaned.",
        "[2023-10-03] Emp: E02 checked RX-103. Actual count: 140.", 
        "[2023-10-03] Emp: E01 checked RX-104. Actual count: 80.",
        "[2023-10-04] Emp: E01 checked RX-105. Actual count: 290.",
        "[2023-10-04] Emp: E04 checked RX-106. Actual count: 495." 
    ]
    with open(os.path.join(base_dir, "audits", "audit_log_2023.txt"), "w") as f:
        f.write("\n".join(audit_data))

if __name__ == "__main__":
    build_env()
