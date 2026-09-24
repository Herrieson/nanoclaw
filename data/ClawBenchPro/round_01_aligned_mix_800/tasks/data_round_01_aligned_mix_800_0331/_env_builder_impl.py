import os
import sqlite3
import json
import csv

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

    # 3. Create Files
    # Building A is now a "PDF" (mock file)
    with open("records/building_a.pdf", "w") as f:
        f.write("%PDF-1.4 [Mock Scanned Ledger Data for T001 and T002]")

    # Building B/C remains CSV
    building_bc = [
        ["Date", "TenantID", "Amount"],
        ["2023-07-01", "T003", "1100"],
        ["2023-08-02", "T003", "1100"],
        ["2023-09-01", "T003", "1100"],
        ["2023-07-01", "T004", "1800"],
        ["2023-08-01", "T004", "1800"],
        # Robert T004 missed September: Total 3600 < 5400
        ["2023-07-15", "T005", "950"],
        ["2023-08-15", "T005", "950"],
        ["2023-09-15", "T005", "950"]
    ]
    with open("records/building_bc.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(building_bc)

    # 4. Create SQLite database with raw metrics
    conn = sqlite3.connect("property_specs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE units (unit_id TEXT, avg_monthly_wattage REAL, insulation_index REAL)")
    # Logic: High-Energy if wattage > 500 and insulation < 0.5
    units_data = [
        ("A1", 300, 0.8),  # Low
        ("A2", 850, 0.3),  # High-Energy (Match)
        ("B1", 450, 0.6),  # Low
        ("B2", 900, 0.2),  # High-Energy (Match)
        ("C1", 700, 0.4)   # High-Energy (Match)
    ]
    cursor.executemany("INSERT INTO units VALUES (?, ?, ?)", units_data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_env()
