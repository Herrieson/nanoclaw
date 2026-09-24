import os
import json
import csv

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    
    # 1. Approved rates (Source of Truth)
    approved_rates = {
        "TechNova Solutions": 150.0,
        "ByteSynergy LLC": 200.0,
        "CloudArchitects Inc": 180.0
    }
    with open("raw_data/approved_rates.json", "w", encoding="utf-8") as f:
        json.dump(approved_rates, f, indent=4)
        
    # 2. Timesheet A (CSV) - mixed data, some extra whitespaces
    csv_data = [
        ["Vendor Name", "Logged Hours", "Project Code"],
        [" TechNova Solutions ", "40", "PRJ-992"],
        ["RogueIT Contractors", "25", "PRJ-992"], # Unauthorized
        ["ByteSynergy LLC", "15", "PRJ-881"]
    ]
    with open("raw_data/timesheet_legacy.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
        
    # 3. Timesheet B (JSON)
    json_data = [
        {"vendor_id": "CloudArchitects Inc", "h": 20, "desc": "DB migration"},
        {"vendor_id": "ShadowCoders", "h": 50, "desc": "Frontend hotfix"}, # Unauthorized
        {"vendor_id": "TechNova Solutions", "h": 10, "desc": "Code review"}
    ]
    with open("raw_data/timesheet_api_dump.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

if __name__ == "__main__":
    build_env()
