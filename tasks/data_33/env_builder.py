import os
import json
import sqlite3
import csv

def build_env():
    base_dir = "assets/data_33"
    records_dir = os.path.join(base_dir, "business_records")
    
    # Clean up if exists
    os.makedirs(records_dir, exist_ok=True)
    
    # 1. Create SQLite database for permits
    db_path = os.path.join(records_dir, "permits.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE permits (
            id INTEGER PRIMARY KEY,
            project_name TEXT,
            permit_number TEXT,
            status TEXT,
            issue_date TEXT
        )
    ''')
    
    permits_data = [
        ("Villa Nova", "VN-2022-1102", "Expired", "2022-04-15"),
        ("Villa Nova", "VN-2023-8894", "Active", "2023-09-01"),
        ("River View", "RV-2023-1001", "Active", "2023-01-20"),
        ("Sunset Plaza", "SP-2021-0045", "Expired", "2021-11-10")
    ]
    
    cursor.executemany('''
        INSERT INTO permits (project_name, permit_number, status, issue_date)
        VALUES (?, ?, ?, ?)
    ''', permits_data)
    
    conn.commit()
    conn.close()
    
    # 2. Create invoice files (mix of JSON and CSV to test parsing logic)
    # File 1: JSON
    inv1_path = os.path.join(records_dir, "invoice_Q3_001.json")
    with open(inv1_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "Villa Nova",
            "contractor": "Acme Lumber",
            "items": [
                {"type": "Material", "description": "Oak wood framing", "cost": 1500.50},
                {"type": "Labor", "description": "Delivery and stacking", "cost": 250.00}
            ]
        }, f)
        
    # File 2: JSON (Different project)
    inv2_path = os.path.join(records_dir, "invoice_Q3_002.json")
    with open(inv2_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "River View",
            "items": [
                {"type": "Material", "description": "Concrete", "cost": 800.00}
            ]
        }, f)
        
    # File 3: JSON (Villa Nova, multiple materials)
    inv3_path = os.path.join(records_dir, "invoice_Q3_003.json")
    with open(inv3_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "Villa Nova",
            "contractor": "City Lights Electrical",
            "items": [
                {"type": "Labor", "description": "Wiring installation", "cost": 1200.00},
                {"type": "Material", "description": "Copper wires", "cost": 345.25},
                {"type": "Material", "description": "Junction boxes", "cost": 120.00}
            ]
        }, f)

    # File 4: CSV (Villa Nova)
    inv4_path = os.path.join(records_dir, "hardware_store_receipts.csv")
    with open(inv4_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Project", "ExpenseType", "Amount"])
        writer.writerow(["2023-10-01", "Villa Nova", "Material", "400.25"])
        writer.writerow(["2023-10-02", "Villa Nova", "Labor", "500.00"])
        writer.writerow(["2023-10-03", "Sunset Plaza", "Material", "150.00"])
        writer.writerow(["2023-10-05", "Villa Nova", "Equipment_Rental", "300.00"])

if __name__ == "__main__":
    build_env()
