import os
import json
import csv

def build_env():
    # Create the data directory
    os.makedirs("pharmacy_data", exist_ok=True)
    
    # 1. Start of month counts (JSON)
    start_counts = {
        "Amoxicillin": 1500,
        "Oxycodone": 200,
        "Lisinopril": 800,
        "Adderall": 300,
        "Diazepam": 150,
        "Ibuprofen": 2000
    }
    with open("pharmacy_data/start_of_month.json", "w") as f:
        json.dump(start_counts, f, indent=4)
        
    # 2. System Dispensed logs (CSV)
    dispensed_data = [
        ["drug_name", "quantity_dispensed"],
        ["Amoxicillin", 450],
        ["Oxycodone", 80],
        ["Lisinopril", 200],
        ["Adderall", 110],
        ["Diazepam", 40],
        ["Ibuprofen", 800]
    ]
    with open("pharmacy_data/system_dispensed.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(dispensed_data)
        
    # 3. Actual Physical Counts (CSV)
    # Expected calculations:
    # Amoxicillin: 1500 - 450 = 1050. Actual = 1050 (Bal)
    # Oxycodone: 200 - 80 = 120. Actual = 115 (Deficit of 5)
    # Lisinopril: 800 - 200 = 600. Actual = 600 (Bal)
    # Adderall: 300 - 110 = 190. Actual = 180 (Deficit of 10)
    # Diazepam: 150 - 40 = 110. Actual = 110 (Bal)
    # Ibuprofen: 2000 - 800 = 1200. Actual = 1200 (Bal)
    
    physical_data = [
        ["drug_name", "physical_count"],
        ["Amoxicillin", 1050],
        ["Oxycodone", 115],
        ["Lisinopril", 600],
        ["Adderall", 180],
        ["Diazepam", 110],
        ["Ibuprofen", 1200]
    ]
    with open("pharmacy_data/physical_counts.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(physical_data)

if __name__ == "__main__":
    build_env()
