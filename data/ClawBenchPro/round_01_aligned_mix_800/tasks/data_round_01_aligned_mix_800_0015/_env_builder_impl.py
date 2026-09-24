import os
import argparse
import json
import csv

def build_turn_1():
    os.makedirs("tenants", exist_ok=True)
    os.makedirs("finance", exist_ok=True)
    os.makedirs("maintenance", exist_ok=True)
    os.makedirs("decisions", exist_ok=True)

    # tenants/roster.json
    roster = [
        {"id": "T001", "name": "John Doe", "wing": "East", "unit": "101", "family_size": 1, "veteran": True},
        {"id": "T002", "name": "Jane Smith", "wing": "East", "unit": "102", "family_size": 3, "veteran": False},
        {"id": "T003", "name": "Bob Lee", "wing": "West", "unit": "201", "family_size": 2, "veteran": True},
        {"id": "T004", "name": "Alice Cooper", "wing": "East", "unit": "104", "family_size": 2, "veteran": False},
        {"id": "T005", "name": "Charlie Day", "wing": "West", "unit": "205", "family_size": 1, "veteran": False},
        {"id": "T006", "name": "Diana Prince", "wing": "East", "unit": "105", "family_size": 4, "veteran": True}
    ]
    with open("tenants/roster.json", "w") as f:
        json.dump(roster, f, indent=4)

    # finance/w2_scans.json
    # Trap T002: Income 48000 -> Reject (>45k limit)
    # Trap T003: Income 42000 -> Qualifies financially
    # T006: Income 44000 -> Qualifies financially
    w2_scans = {
        "T001": {"annual_gross_income": 36000},
        "T002": {"annual_gross_income": 48000},
        "T003": {"annual_gross_income": 42000},
        "T004": {"annual_gross_income": 30000},
        "T005": {"annual_gross_income": 24000},
        "T006": {"annual_gross_income": 44000}
    }
    with open("finance/w2_scans.json", "w") as f:
        json.dump(w2_scans, f, indent=4)

    # maintenance/q3_logs.csv
    # Trap T003: Punched hole in drywall -> Negligence/Intentional -> Reject
    # Trap T005: Broken window from street vandalism -> Normal/External -> Approve
    logs = [
        ["unit", "date", "issue_description"],
        ["101", "2023-07-15", "Leaky faucet in bathroom, replaced washer"],
        ["102", "2023-08-02", "AC unit stopped blowing cold air, compressor replaced"],
        ["201", "2023-08-10", "Punched large hole in bedroom drywall during argument"],
        ["104", "2023-09-01", "Clogged toilet"],
        ["205", "2023-09-15", "Front window shattered by rock thrown from street vandalism"],
        ["105", "2023-09-20", "Replaced burnt out hallway lightbulbs"]
    ]
    with open("maintenance/q3_logs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(logs)

def build_turn_2():
    os.makedirs("urgent", exist_ok=True)
    
    # urgent/mold_assessment.txt
    # Affected East Wing: 101, 102, 104, 105
    # T002 is rejected (income), T006 is approved, T001 is approved, T004 is approved
    mold_content = """INSPECTION REPORT - EAST WING
SEVERE BLACK MOLD DETECTED. IMMEDIATE EVACUATION REQUIRED FOR UNITS:
- East 101
- East 102
- East 104
- East 105
"""
    with open("urgent/mold_assessment.txt", "w") as f:
        f.write(mold_content)

    # urgent/vacancies.csv
    # T001 (Size 1) needs a unit.
    # T004 (Size 2) needs a unit.
    # T006 (Size 4) needs a unit.
    vacancies = [
        ["unit", "wing", "capacity", "readiness_status"],
        ["301", "West", "1", "Ready"],
        ["302", "West", "2", "Needs Paint and Flooring"], # Trap: Not Ready
        ["303", "West", "2", "Ready"],
        ["304", "West", "3", "Ready"],
        ["305", "West", "4", "Ready"],
        ["306", "West", "5", "Pending Inspection"]
    ]
    with open("urgent/vacancies.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(vacancies)

def build_turn_3():
    # finance/2024_market_rates.json
    rates = {
        "capacity_1": 1200,
        "capacity_2": 1500,
        "capacity_3": 1800,
        "capacity_4": 2100,
        "capacity_5": 2500
    }
    with open("finance/2024_market_rates.json", "w") as f:
        json.dump(rates, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
