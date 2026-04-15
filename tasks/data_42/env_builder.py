import os
import sqlite3
import csv

def build_environment():
    base_dir = "assets/data_42/trail_finances"
    os.makedirs(base_dir, exist_ok=True)
    
    csv_path = os.path.join(base_dir, "pledges.csv")
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["transaction_id", "donor_name", "pledged_amount", "date"])
        writer.writerow(["TX-9001", "Alice Smith", "1000.00", "2025-09-01"])
        writer.writerow(["TX-9002", "Robert Jones", "500.00", "2025-09-02"]) # Discrepancy: Cleared as 50.00
        writer.writerow(["TX-9003", "Charlie Brown", "250.00", "2025-09-03"]) 
        writer.writerow(["TX-9004", "Diana Prince", "1500.00", "2025-09-04"]) # Discrepancy: Missing in DB
        writer.writerow(["TX-9005", "Evan Wright", "100.00", "2025-09-05"])
        
    db_path = os.path.join(base_dir, "bank_records.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE cleared_transactions (
            id TEXT PRIMARY KEY,
            amount REAL,
            status TEXT
        )
    ''')
    
    # Inserting mock data (Notice TX-9002 has a typo in amount, and TX-9004 is completely absent)
    transactions = [
        ("TX-9001", 1000.00, "CLEARED"),
        ("TX-9002", 50.00, "CLEARED"), 
        ("TX-9003", 250.00, "CLEARED"),
        ("TX-9005", 100.00, "CLEARED")
    ]
    
    cursor.executemany('INSERT INTO cleared_transactions VALUES (?, ?, ?)', transactions)
    conn.commit()
    conn.close()
    
    print(f"Environment successfully built at {base_dir}")

if __name__ == "__main__":
    build_environment()
