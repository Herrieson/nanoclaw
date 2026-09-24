import os
import sqlite3
import json
import csv
import random

def build_env():
    # 1. Create directory structure
    os.makedirs("records", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 2. Create contract_master.json
    contracts = {
        "T001": {"name": "James Wilson", "monthly_rent": 1200, "unit": "A1"},
        "T002": {"name": "Linda Chen", "monthly_rent": 1500, "unit": "A2"},
        "T003": {"name": "Sarah Miller", "monthly_rent": 1100, "unit": "B1"},
        "T004": {"name": "Robert Taylor", "monthly_rent": 1800, "unit": "B2"},
        "T005": {"name": "Gina Smith", "monthly_rent": 950, "unit": "C1"}
    }
    with open("contract_master.json", "w") as f:
        json.dump(contracts, f, indent=4)

    # 3. Create messy CSV records (Building A and Building B/C)
    # James (T001) - Full pay: 3600
    # Linda (T002) - Underpay: 1500 + 1500 + 1000 = 4000 (Short 500)
    # Sarah (T003) - Full pay: 3300
    # Robert (T004) - Underpay: 1800 + 1800 + 0 = 3600 (Short 1800)
    # Gina (T005) - Full pay: 2850
    
    building_a = [
        ["Date", "TenantID", "Amount", "Note"],
        ["2023-07-01", "T001", "1200", "Paid"],
        ["2023-08-01", "T001", "1200", "Paid"],
        ["2023-09-01", "T001", "1200", "Late"],
        ["2023-07-05", "T002", "1500", "Check"],
        ["2023-08-05", "T002", "1500", "Check"],
        ["2023-09-10", "T002", "1000", "Partial - will pay rest later"]
    ]
    
    building_bc = [
        ["Date", "TenantID", "Amount"],
        ["2023-07-01", "T003", "1100"],
        ["2023-08-02", "T003", "1100"],
        ["2023-09-01", "T003", "1100"],
        ["2023-07-01", "T004", "1800"],
        ["2023-08-01", "T004", "1800"],
        # Robert T004 missed September
        ["2023-07-15", "T005", "950"],
        ["2023-08-15", "T005", "950"],
        ["2023-09-15", "T005", "950"]
    ]

    with open("records/building_a.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(building_a)
    
    with open("records/building_bc.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(building_bc)

    # 4. Create SQLite database for property specs
    conn = sqlite3.connect("property_specs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE units (unit_id TEXT, energy_rating TEXT)")
    units_data = [
        ("A1", "Low-Energy"),
        ("A2", "High-Energy"), # Match
        ("B1", "Low-Energy"),
        ("B2", "High-Energy"), # Match
        ("C1", "High-Energy")  # Match
    ]
    cursor.executemany("INSERT INTO units VALUES (?, ?)", units_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
